"""FROZEN (Phase 19 tier map, training/README.md): the torch probe, a clean negative.
Bug fixes and evidence readers only; no new search.

The torch-probe entrant adapter — the TORCH-FREE comparability plumbing (15.17).

This module is the seam between the experiment-tier torch code
(``ppo_gru.py``, imported only by the operator scripts) and the production
training stack, consumed strictly read-only:

* rollouts run through ``training.env.TacticalRolloutEnv`` (the 15.8 seam
  every trainer rides) with the probe policy at the ``IntentSelector`` seam;
* features come from the encoder-v2 ``agents.tactical.features
  .TacticalFeatureEncoder`` (same features as the 15.15 entrants);
* the frozen champion adapts into the 15.15 ``BakeoffPolicy`` /
  ``BakeoffEntrant`` seam, so ``training.bakeoff.harness.evaluate_candidate``
  — the committed eval protocol — scores it unchanged, through its
  experiment-tier (determinism-FAIL-tolerant) row path.

Nothing here imports torch: the committed test
(``tests/experiments/test_torch_probe_excluded.py``) drives this adapter with
a tiny CPU stub, so ``uv run pytest`` exercises the comparability plumbing
without torch installed. The learner/scorer seams are duck-typed protocols
(``ProbeLearner`` / ``RecurrentScorer``) the torch PPO learner and the test
stub both implement.

THE ONE DOCUMENTED FEATURE DEVIATION (report §"Comparability"): the 15.8
``IntentSelector`` seam is deliberately memory-blind — it sees the packet,
the map, the FSM proposal, and the mask, but NOT the inner agent's live
``AgentMemory`` (``training/determinism.py`` docstring names this contrast).
The memory-carrying encoder therefore reads a SHADOW ``AgentMemory`` this
module maintains per agent through the production ``agents.perception
.ingest_packet`` — the exact fold ``orchestrator.game.TacticalAgent.decide``
performs — so the shadow tracks the live memory tick-for-tick during play and
diverges only where meetings fold beliefs through the agent's absorb hooks.
The frozen policy uses the SAME shadow at eval time (ignoring the live memory
the harness passes) so train-time and eval-time features are one
distribution. Carrying that meeting-fold residue latently is exactly what the
GRU is being probed for.
"""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import math  # noqa: E402
import time  # noqa: E402
from collections.abc import Mapping, Sequence  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from typing import Protocol, runtime_checkable  # noqa: E402

from agents.memory.store import AgentMemory  # noqa: E402
from agents.perception import ingest_packet  # noqa: E402
from agents.tactical.features import TacticalFeatureEncoder  # noqa: E402
from engine.rng import RngStateHashPolicy  # noqa: E402
from engine.world import Map, load_canonical_map  # noqa: E402
from observation.action_intent import (  # noqa: E402
    ActionIntent,
    VentIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket  # noqa: E402
from observation.public_map import PublicMapView  # noqa: E402
from orchestrator.boundary import public_map_from_engine_map  # noqa: E402
from training.bakeoff.harness import (  # noqa: E402
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    TRUNCATED_EPISODE_FITNESS,
    TrainedCandidate,
    intent_key,
)
from training.bakeoff.policy_es import head_size, head_slot_for_intent  # noqa: E402
from training.determinism import PolicyFrame  # noqa: E402
from training.env import (  # noqa: E402
    MaskedDecision,
    TacticalRolloutEnv,
    build_action_mask,
)
from training.rewards import PotentialShaper, compute_shaped_reward  # noqa: E402
from training.rollout import EpisodeRollout  # noqa: E402

ENTRANT_NAME = "torch-ppo-gru"


# --------------------------------------------------------------------------- #
# Shadow memory: encoder-v2 features at the memory-blind selector seam.        #
# --------------------------------------------------------------------------- #


class ShadowMemoryFeaturizer:
    """Per-agent shadow ``AgentMemory`` + encoder-v2 features.

    ``features`` folds the packet through the production ``ingest_packet``
    (the same call ``TacticalAgent.decide`` makes) into a shadow memory owned
    here, then encodes with the production encoder. One call per (agent,
    tick) — the caller owns that discipline, because a double fold would
    duplicate episodic rows. ``new_episode=True`` drops the agent's shadow so
    a fresh game starts from the empty-memory zero encoding, exactly like a
    freshly built production agent.
    """

    def __init__(self, encoder: TacticalFeatureEncoder | None = None) -> None:
        self.encoder = encoder if encoder is not None else TacticalFeatureEncoder()
        self._memories: dict[str, AgentMemory] = {}

    def reset(self) -> None:
        self._memories.clear()

    def features(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        *,
        new_episode: bool,
    ) -> tuple[float, ...]:
        agent_id = packet.agent_id
        if new_episode:
            self._memories.pop(agent_id, None)
        memory = self._memories.setdefault(agent_id, AgentMemory())
        ingest_packet(packet=packet, memory=memory.episodic, beliefs=memory.beliefs)
        return self.encoder.encode(packet, public_map, memory)


# --------------------------------------------------------------------------- #
# Candidate enumeration: the shared 15.15 head-slot vocabulary.                 #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ScoredCandidate:
    """One submission-legal intent with its head slots (the scoring recipe).

    ``slots`` is the tuple of head-logit indices whose SUM scores the intent —
    ``(kind_or_room_slot,)`` for everything except a vent, which adds its
    vent-room's room slot (the 15.15 vent-exit lever,
    ``training/bakeoff/policy_es.py::MaskedMlpPolicy._scored_candidates``).
    The learner and the frozen policy both score through this recipe, so the
    torch head speaks exactly the ``MaskedMlpPolicy`` head vocabulary.
    """

    intent: ActionIntent
    key: str
    slots: tuple[int, ...]


def enumerate_candidates(
    submission_legal: Sequence[ActionIntent],
    public_map: PublicMapView,
    *,
    room_index: Mapping[str, int],
) -> list[ScoredCandidate]:
    """Map submission-legal intents to head-slot recipes (emergency excluded).

    Mirrors ``MaskedMlpPolicy._scored_candidates``: ``head_slot_for_intent``
    returns ``None`` for the emergency intent (and any off-vocabulary shape),
    which is skipped — the learned impostor vocabulary excludes emergencies
    exactly as every 15.15 entrant does.
    """

    candidates: list[ScoredCandidate] = []
    for intent in submission_legal:
        slot = head_slot_for_intent(intent, room_index=room_index)
        if slot is None:
            continue
        slots = (slot,)
        if isinstance(intent, VentIntent):
            vent_room = public_map.vent_rooms.get(intent.payload.vent_id)
            room_slot = room_index.get(vent_room) if vent_room is not None else None
            if room_slot is not None:
                slots = (slot, room_slot)
        candidates.append(
            ScoredCandidate(intent=intent, key=intent_key(intent), slots=slots)
        )
    return candidates


def candidate_scores(
    candidates: Sequence[ScoredCandidate], logits: Sequence[float]
) -> list[float]:
    """Score every candidate as the sum of its head-slot logits."""

    return [math.fsum(logits[slot] for slot in item.slots) for item in candidates]


def select_greedy(
    candidates: Sequence[ScoredCandidate], scores: Sequence[float]
) -> ActionIntent:
    """Argmax with the repo tie-break: score desc, canonical intent key asc."""

    paired = list(zip(candidates, scores, strict=True))
    best, _ = min(paired, key=lambda item: (-item[1], item[0].key))
    return best.intent


def _softmax(scores: Sequence[float]) -> list[float]:
    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = math.fsum(exps)
    return [value / total for value in exps]


# --------------------------------------------------------------------------- #
# The learner / scorer seams (duck-typed; torch and the CPU stub both fit).    #
# --------------------------------------------------------------------------- #


@runtime_checkable
class RecurrentScorer(Protocol):
    """A frozen recurrent head: features in, head logits out, hidden inside.

    ``score`` advances the scorer's per-agent hidden state by one decision and
    returns one logit per head slot (``head_size(public_map)`` of them).
    ``new_episode=True`` means the agent's recurrent state must reset first.
    """

    def score(
        self, agent_id: str, features: Sequence[float], *, new_episode: bool
    ) -> Sequence[float]: ...


@runtime_checkable
class ProbeLearner(Protocol):
    """The training-side seam the entrant drives (torch PPO or the test stub).

    ``act`` is called at every impostor decision with the encoder features,
    the candidate recipes, and the index of the FSM's proposal within them
    (``None`` when the FSM proposal is off-vocabulary) — it returns the chosen
    candidate index and owns its own trajectory buffers. ``episode_result``
    closes the episode with per-agent per-decision rewards (aligned with the
    ``act`` call order); ``update`` runs one optimization step over the
    buffered episodes and returns loggable stats.
    """

    def act(
        self,
        agent_id: str,
        features: Sequence[float],
        candidates: Sequence[ScoredCandidate],
        *,
        fsm_index: int | None,
        new_episode: bool,
    ) -> int: ...

    def episode_result(
        self, rewards_by_agent: Mapping[str, Sequence[float]], *, truncated: bool
    ) -> None: ...

    def update(self) -> Mapping[str, float]: ...

    def frozen_scorer(self) -> RecurrentScorer: ...

    def flat_weights(self) -> tuple[float, ...]: ...

    def config(self) -> Mapping[str, object]: ...


# --------------------------------------------------------------------------- #
# The frozen champion: a BakeoffPolicy around a RecurrentScorer.               #
# --------------------------------------------------------------------------- #


class TorchProbePolicy:
    """The frozen probe champion behind the 15.15 ``BakeoffPolicy`` seam.

    Statefulness is the honest deviation from the seam's purity doctrine: a
    recurrent policy carries per-agent hidden state and a shadow memory across
    ticks, so this adapter is exactly the shape the harness's experiment-tier
    (determinism-FAIL-tolerant) row path exists for. Two mechanics keep it
    coherent inside the harness's calling pattern:

    * ``evaluate`` and ``choice_distribution`` are called back-to-back with
      the same inputs at one decision (``harness._CandidateAgent``); the
      forward pass runs ONCE per (agent, tick) and is cached, so the GRU
      advances one step per decision, never two.
    * an agent's tick stream is strictly increasing within one game; a tick
      that does not increase signals a new game (the eval protocol, the
      determinism double-run, and the leak scan all replay seeds), which
      resets that agent's hidden state and shadow memory.
    """

    def __init__(
        self,
        *,
        scorer: RecurrentScorer,
        public_map: PublicMapView,
        sabotage_kinds: Sequence[str],
        encoder: TacticalFeatureEncoder | None = None,
    ) -> None:
        self._scorer = scorer
        self._public_map = public_map
        self._featurizer = ShadowMemoryFeaturizer(encoder=encoder)
        self._rooms = tuple(sorted(public_map.room_ids))
        self._room_index = {room: i for i, room in enumerate(self._rooms)}
        self._sabotage_kinds = tuple(sabotage_kinds)
        self._head = head_size(public_map)
        self._last_tick: dict[str, int] = {}
        self._cache: dict[
            str, tuple[ObservationPacket, tuple[float, ...], tuple[float, ...]]
        ] = {}

    @property
    def encoder_version(self) -> str:
        return self._featurizer.encoder.version

    @property
    def featurizer(self) -> ShadowMemoryFeaturizer:
        return self._featurizer

    def _forward(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> tuple[tuple[float, ...], tuple[float, ...]]:
        agent_id = packet.agent_id
        # Same-DECISION dedupe by packet identity: ``evaluate`` and
        # ``choice_distribution`` receive the same packet object within one
        # ``_CandidateAgent.decide`` call (and the cache holds a reference, so
        # the id cannot be recycled). Keying on the tick VALUE instead would
        # falsely hit when a new game's first decision lands on the same tick
        # the prior game ended on, skipping the episode reset below.
        cached = self._cache.get(agent_id)
        if cached is not None and cached[0] is packet:
            return cached[1], cached[2]
        last = self._last_tick.get(agent_id)
        new_episode = last is None or packet.tick <= last
        features = self._featurizer.features(
            packet, public_map, new_episode=new_episode
        )
        raw = self._scorer.score(agent_id, features, new_episode=new_episode)
        logits = tuple(float(value) for value in raw)
        if len(logits) != self._head:
            raise ValueError(
                f"scorer returned {len(logits)} logits; head expects {self._head}"
            )
        self._last_tick[agent_id] = packet.tick
        self._cache[agent_id] = (packet, features, logits)
        return features, logits

    def _candidates(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> list[ScoredCandidate]:
        # The emergency-free mask every 15.15 candidate validates against
        # (harness._CandidateAgent re-validates with the same arguments).
        mask = build_action_mask(
            packet,
            public_map,
            sabotage_kinds=self._sabotage_kinds,
            emergency_uses_remaining=0,
        )
        candidates = enumerate_candidates(
            mask.submission_legal, public_map, room_index=self._room_index
        )
        if not candidates:
            raise ValueError(
                f"no head-scorable submission-legal intent for "
                f"{packet.agent_id!r} at tick {packet.tick}"
            )
        return candidates

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        # ``memory`` (the inner agent's live memory) is deliberately unused:
        # features come from the shadow so train and eval see one distribution
        # (module docstring — the documented deviation).
        features, logits = self._forward(packet, public_map)
        if packet.self_state.role != "IMPOSTOR":
            intent = fsm_intent
        else:
            candidates = self._candidates(packet, public_map)
            intent = select_greedy(candidates, candidate_scores(candidates, logits))
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=features,
            logits=logits,
            intent=intent,
        )

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> Mapping[str, float]:
        if packet.self_state.role != "IMPOSTOR":
            return {intent_key(fsm_intent): 1.0}
        _, logits = self._forward(packet, public_map)
        candidates = self._candidates(packet, public_map)
        probabilities = _softmax(candidate_scores(candidates, logits))
        distribution: dict[str, float] = {}
        for item, probability in zip(candidates, probabilities, strict=True):
            distribution[item.key] = distribution.get(item.key, 0.0) + probability
        return distribution


# --------------------------------------------------------------------------- #
# Per-decision rewards from the typed episode record.                          #
# --------------------------------------------------------------------------- #


def per_decision_rewards(
    rollout: EpisodeRollout,
    decision_ticks: Mapping[str, Sequence[int]],
    *,
    shaper: PotentialShaper,
) -> dict[str, list[float]]:
    """Split the episode's impostor shaped reward across decision steps.

    The potential-shaping delta of every frame transition is attributed to the
    latest decision at-or-before the transition's arrival tick (pre-first-
    decision deltas fold into the first decision), and the episode-level dense
    terms + terminal reward land on the agent's LAST decision — so each
    impostor trajectory's reward sum equals
    ``compute_shaped_reward(rollout, "IMPOSTOR").total()`` exactly (γ=1
    telescoping), the same scalar the 15.15 inner fitness starts from. A
    truncated episode mirrors the harness's documented
    ``TRUNCATED_EPISODE_FITNESS`` as a single terminal penalty instead —
    never a silent skip.
    """

    if shaper.gamma != 1.0:
        # The split below telescopes the shaping series against a γ=1 total;
        # a discounted shaper would silently break both the sum identity and
        # shaping policy-invariance. Fail loud (AGENTS.md: no silent
        # fallbacks) — the probe trains undiscounted by design.
        raise ValueError(f"per_decision_rewards requires gamma=1.0, got {shaper.gamma}")
    rewards = {
        agent_id: [0.0] * len(ticks)
        for agent_id, ticks in decision_ticks.items()
        if ticks
    }
    if not rewards:
        return rewards
    if not rollout.complete:
        for agent_id in rewards:
            rewards[agent_id][-1] = TRUNCATED_EPISODE_FITNESS
        return rewards

    shaping = [float(value) for value in shaper.shaping_series(rollout)]
    arrival_ticks = [frame.tick for frame in rollout.frames[1:]]
    shaped = compute_shaped_reward(rollout, "IMPOSTOR")
    episode_terms = (
        shaped.terminal_weight * shaped.terminal_reward
        + shaped.dense_weight * math.fsum(shaped.dense_terms.values())
    )

    for agent_id, ticks in decision_ticks.items():
        if not ticks:
            continue
        series = rewards[agent_id]
        cursor = 0
        for delta, arrival in zip(shaping, arrival_ticks, strict=True):
            while cursor + 1 < len(ticks) and ticks[cursor + 1] <= arrival:
                cursor += 1
            series[cursor] += shaped.shaping_weight * delta
        series[-1] += episode_terms
    return rewards


# --------------------------------------------------------------------------- #
# The entrant: BakeoffEntrant around TacticalRolloutEnv + the learner.         #
# --------------------------------------------------------------------------- #


@dataclass
class TorchProbeConfig:
    """The probe's training budget (recorded verbatim in the report row)."""

    train_seeds: tuple[int, ...]
    updates: int
    episodes_per_update: int
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE
    extra: Mapping[str, object] = field(default_factory=dict)


class TorchProbeEntrant:
    """The 15.17 entrant: PPO+recurrent training behind the 15.15 seam.

    Training rollouts run through ``training.env.TacticalRolloutEnv`` on the
    fast no-replay path (the 15.8.1 training-only knobs — trajectories are
    identical to the recording path, so training transfers exactly), with the
    learner acting at the ``IntentSelector`` seam through the shadow-memory
    encoder-v2 features. ``train()`` returns a 15.15 ``TrainedCandidate``
    whose policy is the frozen :class:`TorchProbePolicy`; every reported
    metric is computed by ``training.bakeoff.harness.evaluate_candidate``,
    never here.
    """

    def __init__(
        self,
        *,
        learner: ProbeLearner,
        config: TorchProbeConfig,
        game_map: Map | None = None,
        name: str = ENTRANT_NAME,
    ) -> None:
        self._learner = learner
        self._config = config
        self._name = name
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._public_map = public_map_from_engine_map(self._game_map)
        self._room_index = {
            room: i for i, room in enumerate(sorted(self._public_map.room_ids))
        }
        self.featurizer = ShadowMemoryFeaturizer()
        # Exposed for the committed wiring test: the env the training loop
        # drives and the encoder the features come from are the production
        # classes, constructed here.
        self.rollout_env: TacticalRolloutEnv | None = None
        self.fitness_trace: list[float] = []

    @property
    def name(self) -> str:
        return self._name

    def _build_selector(
        self, decision_ticks: dict[str, list[int]]
    ) -> "_LearnerSelector":
        return _LearnerSelector(
            learner=self._learner,
            featurizer=self.featurizer,
            room_index=self._room_index,
            decision_ticks=decision_ticks,
        )

    def train(self) -> TrainedCandidate:
        started = time.perf_counter()
        decision_ticks: dict[str, list[int]] = {}
        selector = self._build_selector(decision_ticks)
        self.rollout_env = TacticalRolloutEnv(
            game_map=self._game_map,
            num_players=self._config.num_players,
            num_impostors=self._config.num_impostors,
            tasks_per_crewmate=self._config.tasks_per_crewmate,
            intent_selector=selector,
            no_replay=True,
            rng_hash_policy=RngStateHashPolicy.TRAINING_FAST,
        )
        shaper = PotentialShaper(side="IMPOSTOR")
        seeds = self._config.train_seeds
        cursor = 0
        episodes = 0
        update_stats: list[Mapping[str, float]] = []
        for _ in range(self._config.updates):
            shaped_totals: list[float] = []
            for _ in range(self._config.episodes_per_update):
                seed = seeds[cursor % len(seeds)]
                cursor += 1
                decision_ticks.clear()
                selector.begin_episode()
                rollout = self.rollout_env.rollout(seed)
                rewards = per_decision_rewards(rollout, decision_ticks, shaper=shaper)
                self._learner.episode_result(rewards, truncated=not rollout.complete)
                episodes += 1
                if rollout.complete:
                    shaped_totals.append(
                        compute_shaped_reward(rollout, "IMPOSTOR").total()
                    )
                else:
                    shaped_totals.append(TRUNCATED_EPISODE_FITNESS)
            update_stats.append(dict(self._learner.update()))
            self.fitness_trace.append(math.fsum(shaped_totals) / len(shaped_totals))
        scorer = self._learner.frozen_scorer()
        policy = TorchProbePolicy(
            scorer=scorer,
            public_map=self._public_map,
            sabotage_kinds=tuple(sorted(self._game_map.sabotages)),
        )
        weights = self._learner.flat_weights()
        return TrainedCandidate(
            entrant=self._name,
            policy=policy,
            weights=weights,
            config={
                "entrant": self._name,
                "env": "training.env.TacticalRolloutEnv",
                "encoder_version": policy.encoder_version,
                "train_seeds": list(self._config.train_seeds),
                "updates": self._config.updates,
                "episodes_per_update": self._config.episodes_per_update,
                "learner": dict(self._learner.config()),
                **dict(self._config.extra),
            },
            train_wall_clock_s=time.perf_counter() - started,
            train_metadata={
                "episodes": episodes,
                "shaped_reward_trace": [
                    round(value, 4) for value in self.fitness_trace
                ],
                "final_update_stats": update_stats[-1] if update_stats else {},
            },
        )


def _canonical_crew_delegate(decision: MaskedDecision) -> ActionIntent:
    """Delegate a crew decision to the FSM, canonicalized against the mask.

    Exactly two crew-FSM emissions are KNOWN to fail ``is_submission_legal``
    verbatim, both emergencies, and only those are canonicalized:

    * The 15.8 exact-equality gap documented at ``eval/leak_test.py:608-616``
      (the fix is Task 15.16's ``training/env.py`` region, out of scope
      here): the FSM's emergency stamps ``payload.reason`` while the mask's
      entry carries the default payload. The reason changes no engine
      DECISION (``resolve_emergency_meeting`` ignores it; it survives only in
      ``player.last_action`` telemetry, which the no-replay training path
      never hashes), so remapping to the mask's SAME-``intent_key`` object
      keeps the trajectory equivalent.
    * A spent-budget KILL-WITNESS emergency: the FSM emits it without
      consulting the budget, and the engine no-ops it via
      ``ActionRejectedError``. There is no same-key legal intent then, so
      mirror the engine's rejection no-op with the always-legal WAIT.

    Any OTHER off-mask crew intent is an undocumented FSM/mask mismatch and
    raises (AGENTS.md: no silent fallbacks) — a crew-policy regression must
    surface, not silently diverge the training substrate from production.
    (``intent_key`` folds every non-emergency intent's full payload, so the
    same-key remap is structurally emergency-only regardless.)
    """

    fsm_intent = decision.fsm_intent
    if decision.mask.is_submission_legal(fsm_intent):
        return fsm_intent
    if fsm_intent.type != "emergency":
        raise ValueError(
            f"crew FSM intent {fsm_intent!r} for "
            f"{decision.packet.agent_id!r} at tick {decision.packet.tick} is "
            "not submission-legal and is not a documented emergency "
            "canonicalization case"
        )
    fsm_key = intent_key(fsm_intent)
    for candidate in decision.mask.submission_legal:
        if intent_key(candidate) == fsm_key:
            return candidate
    return WaitIntent(actor=decision.packet.agent_id, type="wait")


class _LearnerSelector:
    """The ``IntentSelector`` driving the learner at every impostor decision.

    Crew decisions delegate to the FSM proposal untouched (the crew side stays
    the frozen scripted FSM this wave, exactly as in the 15.15 bake-off). The
    env's mask arrives already built — including a live emergency tracker —
    but ``enumerate_candidates`` drops the emergency intent from the learnable
    vocabulary, so the training-time and eval-time vocabularies agree.
    """

    def __init__(
        self,
        *,
        learner: ProbeLearner,
        featurizer: ShadowMemoryFeaturizer,
        room_index: Mapping[str, int],
        decision_ticks: dict[str, list[int]],
    ) -> None:
        self._learner = learner
        self._featurizer = featurizer
        self._room_index = room_index
        self._decision_ticks = decision_ticks
        self._last_tick: dict[str, int] = {}

    def begin_episode(self) -> None:
        self._last_tick.clear()

    def __call__(self, decision: MaskedDecision) -> ActionIntent:
        packet = decision.packet
        if packet.self_state.role != "IMPOSTOR":
            return _canonical_crew_delegate(decision)
        agent_id = packet.agent_id
        last = self._last_tick.get(agent_id)
        new_episode = last is None or packet.tick <= last
        self._last_tick[agent_id] = packet.tick
        features = self._featurizer.features(
            packet, decision.public_map, new_episode=new_episode
        )
        candidates = enumerate_candidates(
            decision.mask.submission_legal,
            decision.public_map,
            room_index=self._room_index,
        )
        if not candidates:
            raise ValueError(
                f"no head-scorable submission-legal intent for "
                f"{agent_id!r} at tick {packet.tick}"
            )
        fsm_key = intent_key(decision.fsm_intent)
        fsm_index: int | None = None
        for index, item in enumerate(candidates):
            if item.key == fsm_key:
                fsm_index = index
                break
        chosen = self._learner.act(
            agent_id,
            features,
            candidates,
            fsm_index=fsm_index,
            new_episode=new_episode,
        )
        self._decision_ticks.setdefault(agent_id, []).append(packet.tick)
        return candidates[chosen].intent
