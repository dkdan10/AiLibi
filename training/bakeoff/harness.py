"""The impostor bake-off harness — one eval protocol for every entrant (Task 15.15).

Four training methods (BC/DAgger, utility-scorer+ES, direct policy-net+ES,
MAP-Elites) enter ONE harness so the mid-phase pause compares METHODS, not
evaluation protocols (audits/post-phase-14-ML-planning.md §5.2/§9;
post-phase-14-ML-training-signal.md §4). The harness owns three things and the
entrant modules own nothing that is reported:

1. **The entrant protocol.** :class:`BakeoffEntrant` — an entrant trains against
   the baseline-5 substrate and returns a :class:`TrainedCandidate` whose policy
   implements :class:`BakeoffPolicy` (a structural superset of the 15.10
   :class:`training.determinism.FramePolicy`, plus the choice DISTRIBUTION the
   anchor cross-entropy reads). The 15.17 torch probe adapts into this same seam.
2. **The fixed eval protocol.** :func:`evaluate_candidate` scores every candidate
   on the SAME fixed eval seed set — the frozen corpus test split
   (``replays/ml_corpus/9p2i/splits.json``, ``seed % 5 == 4``,
   :func:`load_eval_seeds`) — through the SAME metric tuple: the 15.1 validity
   gate + the 15.2 referee (SELECTION filters, never fitness terms —
   training-signal audit §4), the inner fitness re-scored on the real
   (fake-provider) meeting path AND the 15.13 surrogate path (divergence is
   data), the anchor cross-entropy toward the frozen FSM (the piKL-style
   penalty: log-loss of the candidate's choice distribution at the FSM's
   deterministic choice — a literal KL against a deterministic anchor's delta
   distribution is degenerate), win rate + take-rate (reported, never gated),
   the 15.10 determinism harness and the leak-test factory mode THROUGH THE
   CANDIDATE'S OWN policy factory, surrogate-staleness usage, and wall-clock.
3. **The report emitter.** :class:`BakeoffResult` rows serialize to
   ``training/reports/results-impostor-bakeoff.jsonl`` (the machine-readable
   rows 15.18 consumes); candidate weights freeze under
   ``training/artifacts/impostor/`` as float-hex JSON + sha256 sidecars.

A determinism-harness FAIL never drops a row: the row is marked
``tier="experiment"`` and carries the full
:class:`~training.determinism.PolicyDeterminismReport` plus an N-repeat metric
spread — the seam the 15.17 torch entrant reports through.

The module also discharges the 15.14 obligation
(:func:`run_goodhart_surrogate_rerun`): the Goodhart probe re-runs through its
OWN entry point (``run_goodhart_probe(meeting_runner_factory=…)``) under the
15.13 surrogate — including the forced single-tactic reachability sweep, the
net that found the 15.14 exploit — alongside the surrogate's measured
ejection/SKIP rate (an under-ejecting surrogate can hold the meeting-driven
floors for the wrong reason).

Import posture: this harness is the ONLY bake-off module that imports
``eval.validity`` / ``eval.watchability`` / ``eval.leak_test`` — a committed
test AST-scans the entrant modules for those imports (the firewall-test
pattern), so no entrant can grow a private eval loop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal, Protocol, TypeAlias, runtime_checkable

from pydantic import BaseModel, ConfigDict

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.features import weights_from_hex_json, weights_to_hex_json
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import Map, load_canonical_map
from eval.leak_test import scan_factory_packets
from eval.validity import run_validity_gate
from eval.watchability import WatchabilityReport, compute_watchability
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from observation.action_intent import ActionIntent, KillIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    AgentFactory,
    HeadlessGame,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import (
    GoodhartProbeReport,
    MeetingRunnerFactory,
    run_goodhart_probe,
)
from training.determinism import (
    PolicyDeterminismReport,
    PolicyFrame,
    run_policy_determinism,
)
from training.env import build_action_mask
from training.rewards import compute_shaped_reward
from training.rollout import (
    DESCRIPTOR_VECTOR_FIELDS,
    EpisodeRollout,
    reconstruct_episode,
)
from training.surrogate.ballots import load_staleness_cap
from training.surrogate.runner import SurrogateUseCounter, load_surrogate_runner_factory

# --------------------------------------------------------------------------- #
# The fixed eval protocol constants (stated BEFORE any training run).          #
# --------------------------------------------------------------------------- #

# The frozen corpus + split the fixed eval seed set is read from (Task 15.12).
CORPUS_SPLITS_PATH: Final[Path] = Path("replays/ml_corpus/9p2i/splits.json")
# The committed split rule the test split must satisfy (MANIFEST.md): the eval
# seeds are exactly the ``seed % 5 == 4`` bucket.
EVAL_SPLIT_MODULUS: Final[int] = 5
EVAL_SPLIT_REMAINDER: Final[int] = 4

# The bake-off roster — the canonical 9p2i eval roster the corpus was recorded
# on and the referee floors the bake-off selects on are pinned for: the
# baseline-6 (adopted Phase-18) floors since the Task-18.13 corpus re-record
# (Task 18.14 flips the id; the floors themselves are pinned at Task 18.12).
BAKEOFF_NUM_PLAYERS: Final[int] = 9
BAKEOFF_NUM_IMPOSTORS: Final[int] = 2
BAKEOFF_TASKS_PER_CREWMATE: Final[int] = 2
BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"

# The pre-stated BC bar (task contract): held-out top-1 intent agreement with
# the FSM oracle. Stated here, before training, per the definition of done.
BC_INTENT_AGREEMENT_BAR: Final[float] = 0.90

# The documented anchor-KL ceiling (mean anchor cross-entropy, nats). No audit
# commits a numeric ceiling (post-phase-14-ML-training-signal.md §4 is
# qualitative), so the bake-off documents one BEFORE running: a candidate whose
# mean -log P(anchor action) exceeds 2.0 nats assigns the FSM's choice under
# e^-2 ≈ 13.5% average probability — below uniform over a typical ~15-intent
# menu, i.e. it has drifted off the legible anchor. Rows above the ceiling are
# FLAGGED (``anchor_ce_flagged``), never dropped (definition of done).
ANCHOR_CE_CEILING: Final[float] = 2.0
# The probability floor for the anchor log-loss: when a candidate's choice
# distribution assigns (numerically) zero mass to the FSM's choice, the CE term
# is clamped at -log(eps) rather than inf, and the decision is counted in
# ``anchor_offmenu_decisions`` — an explicit tally, not a silent clamp.
ANCHOR_CE_EPSILON: Final[float] = 1e-6

# The default anchor-penalty weight in the SHARED inner fitness every ES/QD
# entrant optimizes: shaped impostor reward (side-specific tactically-reachable
# terms + potential shaping, training.rewards) MINUS this weight times the mean
# per-decision anchor cross-entropy.
DEFAULT_ANCHOR_PENALTY_WEIGHT: Final[float] = 1.0

# The explicit fitness assigned to a truncated (tick-budget-capped) episode.
# ``training.rewards`` refuses to score a truncated episode as a full game; a
# candidate that stalls the scheduler has no terminal outcome, so its episode
# scores this documented constant — well below any reachable full-game fitness
# — rather than raising out of the optimizer or being silently skipped.
TRUNCATED_EPISODE_FITNESS: Final[float] = -10.0

# The committed 15.13 surrogate artifact (weights + sha256 sidecar + staleness
# cap) the surrogate-path columns and the Goodhart re-run load.
SURROGATE_ARTIFACT_DIR: Final[Path] = Path("training/artifacts/surrogate")

# The fake-provider probe baseline the surrogate re-run's delta is stated
# against, RE-CONFIRMED at the baseline-6 tree (Task 18.14) under the baseline-6
# floors through the probe's own entry point —
# ``run_goodhart_probe(config=ESConfig(generations=6, population=6, sigma=0.5,
# seed=0, fitness_seeds=tuple(range(8))), num_players=9, num_impostors=2,
# tasks_per_crewmate=2, materiality_bar=0.25)`` with the fake provider ($0,
# offline) — never hand-copied. The fake-provider probe is SUBSTRATE-INDEPENDENT:
# under fake meetings the referee gate is always False (no contradiction flags,
# no observation-backed accusations), so the ES fitness is ``mean_score`` for
# both baselines and all six values below reproduce unchanged from baseline 5 —
# ``baseline_id`` selects only the supply floors, which don't feed ``mean_score``
# and are False either way. ES-core digest of the origin-platform run:
# a7c5ea590233f0735571cf6960fbdf1567bdbb2575e0d27bfba995f08d235c14 (the six
# rounded values are platform-stable; the digest is the exact-float genome hash
# and is origin-platform-specific — the same ES trajectory ULP-sensitivity the
# map-elites/anchor byte-identity pins carry). The ES champion and the
# forced-report lever tie at the strongest reachable score (the ES converged to
# the same corner), so the tactic names the lever.
GOODHART_9P2I_BASELINE: Final[Mapping[str, float | str]] = {
    "baseline_mean_score": 3.28,
    "champion_mean_score": 3.7,
    "relative_gain": 0.1298,
    "strongest_reachable_score": 3.7,
    "strongest_reachable_tactic": "report",
    "verdict": "HELD",
}

_ROSTER_FILENAME: Final[str] = "roster.json"
_WEIGHTS_FILENAME: Final[str] = "weights.json"
_CONFIG_FILENAME: Final[str] = "config.json"

_RESULTS_JSONL_PATH: Final[Path] = Path(
    "training/reports/results-impostor-bakeoff.jsonl"
)
_ARTIFACT_ROOT: Final[Path] = Path("training/artifacts/impostor")


def load_eval_seeds(splits_path: Path = CORPUS_SPLITS_PATH) -> tuple[int, ...]:
    """The fixed eval seed set: the frozen corpus TEST split (Task 15.15).

    Reads the committed ``splits.json`` and returns its ``test`` bucket,
    verifying every seed satisfies the committed split rule
    (``seed % 5 == 4``) and that NO test-rule seed leaked into another bucket —
    a drifted split file fails loud rather than silently re-ranking the
    bake-off on different games.
    """

    raw = json.loads(splits_path.read_text())
    test_seeds = tuple(int(seed) for seed in raw["test"])
    if not test_seeds:
        raise ValueError(f"{splits_path} carries an empty test split")
    offenders = [
        seed for seed in test_seeds if seed % EVAL_SPLIT_MODULUS != EVAL_SPLIT_REMAINDER
    ]
    if offenders:
        raise ValueError(
            f"{splits_path} test split violates the committed rule "
            f"seed % {EVAL_SPLIT_MODULUS} == {EVAL_SPLIT_REMAINDER}: {offenders!r}"
        )
    for bucket in ("train", "val"):
        leaked = [
            seed
            for seed in (int(s) for s in raw[bucket])
            if seed % EVAL_SPLIT_MODULUS == EVAL_SPLIT_REMAINDER
        ]
        if leaked:
            raise ValueError(
                f"{splits_path} {bucket} split contains test-rule seeds {leaked!r}"
            )
    return test_seeds


def load_train_seeds(splits_path: Path = CORPUS_SPLITS_PATH) -> tuple[int, ...]:
    """The corpus TRAIN split (``seed % 5`` in ``{0, 1, 2}``) for entrant training."""

    raw = json.loads(splits_path.read_text())
    return tuple(int(seed) for seed in raw["train"])


def load_val_seeds(splits_path: Path = CORPUS_SPLITS_PATH) -> tuple[int, ...]:
    """The corpus VAL split (``seed % 5 == 3``) — the BC held-out agreement set."""

    raw = json.loads(splits_path.read_text())
    return tuple(int(seed) for seed in raw["val"])


# --------------------------------------------------------------------------- #
# The canonical intent key — the shared metric language.                       #
# --------------------------------------------------------------------------- #


def intent_key(intent: ActionIntent) -> str:
    """Canonical string key for one intent (the anchor-CE / agreement alphabet).

    ``type`` plus the salient payload field, so two intents compare equal iff
    they would drive the engine identically: ``move:STORAGE``, ``kill:p-3``,
    ``vent:v-1``, ``do_task:t-5``, ``report:b-1``, ``sabotage:reactor``,
    ``repair:reactor``, ``emergency``, ``wait``.
    """

    payload = intent.model_dump(mode="json").get("payload") or {}
    kind = intent.type
    if kind == "move":
        return f"move:{payload['to_room']}"
    if kind == "kill":
        return f"kill:{payload['target']}"
    if kind == "vent":
        return f"vent:{payload['vent_id']}"
    if kind == "do_task":
        return f"do_task:{payload['task_id']}"
    if kind == "report":
        return f"report:{payload['body_id']}"
    if kind == "sabotage":
        return f"sabotage:{payload['kind']}"
    if kind == "repair_sabotage":
        return f"repair:{payload['kind']}"
    return kind  # wait / emergency carry no distinguishing payload


# --------------------------------------------------------------------------- #
# The entrant-facing policy protocol + rollout runner.                         #
# --------------------------------------------------------------------------- #


@runtime_checkable
class BakeoffPolicy(Protocol):
    """The frozen-candidate interface every entrant produces (Task 15.15).

    A structural SUPERSET of the 15.10 :class:`training.determinism.FramePolicy`
    — any ``BakeoffPolicy`` runs through ``run_policy_determinism`` unchanged —
    plus :meth:`choice_distribution`, the per-decision probability the anchor
    cross-entropy is the log-loss of. Both methods must be pure functions of
    their inputs (no RNG, no mutable state): the determinism digest and the
    double-scored eval both depend on it.
    """

    @property
    def encoder_version(self) -> str: ...

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame: ...

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> Mapping[str, float]: ...


# A per-decision observer for dataset builders (the BC/DAgger harvest): called
# at every IMPOSTOR decision with the packet, map, the inner agent's OWN live
# memory, the FSM's proposal (the free oracle label), and the intent that
# actually drove the game.
DecisionCallback: TypeAlias = Callable[
    [ObservationPacket, PublicMapView, AgentMemory, ActionIntent, ActionIntent], None
]


@dataclass
class DecisionTrace:
    """Accumulators over one (or many) rollouts' impostor decisions.

    ``anchor_ce_sum`` accumulates ``-log P(candidate emits the FSM's choice)``
    per decision (clamped at ``-log ANCHOR_CE_EPSILON``; clamped decisions are
    tallied in ``offmenu_decisions``). ``opportunities`` / ``kills_taken``
    implement the take-rate the planning audit §4.3 measured: a CLEAN
    opportunity is an impostor decision with ``cooldown == 0`` and exactly one
    visible non-teammate co-located (no crew witness), and a take is a kill
    emitted against that target.
    """

    impostor_decisions: int = 0
    scored_decisions: int = 0
    anchor_ce_sum: float = 0.0
    offmenu_decisions: int = 0
    agreement_hits: int = 0
    opportunities: int = 0
    kills_taken: int = 0

    def record(
        self,
        packet: ObservationPacket,
        *,
        fsm_intent: ActionIntent,
        chosen: ActionIntent,
        distribution: Mapping[str, float] | None,
    ) -> None:
        self.impostor_decisions += 1
        anchor_key = intent_key(fsm_intent)
        if distribution is not None:
            self.scored_decisions += 1
            probability = distribution.get(anchor_key, 0.0)
            if probability < ANCHOR_CE_EPSILON:
                probability = ANCHOR_CE_EPSILON
                self.offmenu_decisions += 1
            self.anchor_ce_sum += -math.log(probability)
        if intent_key(chosen) == anchor_key:
            self.agreement_hits += 1

        own_room = packet.self_state.room
        fellows = set(packet.self_state.fellow_impostor_ids)
        colocated = [
            view.id
            for view in packet.visible_players
            if view.room == own_room and view.id not in fellows
        ]
        if packet.cooldown == 0 and len(colocated) == 1:
            self.opportunities += 1
            if isinstance(chosen, KillIntent) and (
                chosen.payload.target == colocated[0]
            ):
                self.kills_taken += 1

    def mean_anchor_ce(self) -> float:
        """Mean per-decision anchor cross-entropy (0.0 when nothing was scored)."""

        if self.scored_decisions == 0:
            return 0.0
        return self.anchor_ce_sum / self.scored_decisions

    def take_rate(self) -> float | None:
        """Kills taken per clean opportunity (``None`` when none arose)."""

        if self.opportunities == 0:
            return None
        return self.kills_taken / self.opportunities


class _CandidateAgent:
    """Interposition wrapper driving a candidate through the production loop.

    Mirrors the 15.10 ``_FrameRecordingAgent``: drives the inner FSM first (so
    perception + the agent's OWN memory populate exactly as in production),
    then — for IMPOSTOR decisions only, the crew side stays the frozen scripted
    FSM throughout (no co-evolution this wave) — evaluates the candidate off
    the inner agent's live :class:`~agents.memory.store.AgentMemory` and lets
    its intent drive the game, validated against the legal-action mask so an
    off-vocabulary candidate fails loud. With ``policy=None`` the wrapper is a
    transparent FSM delegate that still feeds the trace / decision callback —
    the BC harvest and the scripted-baseline measurements ride that mode.
    """

    def __init__(
        self,
        inner: TacticalAgent,
        *,
        policy: BakeoffPolicy | None,
        sabotage_kinds: tuple[str, ...],
        trace: DecisionTrace | None,
        on_decision: DecisionCallback | None,
    ) -> None:
        self._inner = inner
        self._policy = policy
        self._sabotage_kinds = sabotage_kinds
        self._trace = trace
        self._on_decision = on_decision

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        fsm_intent = self._inner.decide(packet, public_map)
        if packet.self_state.role != "IMPOSTOR":
            return fsm_intent
        memory = self._inner.memory
        chosen = fsm_intent
        distribution: Mapping[str, float] | None = None
        if self._policy is not None:
            frame = self._policy.evaluate(
                packet, public_map, memory, fsm_intent=fsm_intent
            )
            chosen = frame.intent
            # The candidate's mask is emergency-free (see the entrant modules);
            # the wrapper re-validates with the same emergency-free mask, so a
            # candidate that somehow realized an off-vocabulary intent fails
            # loud here rather than silently wasting engine-rejected ticks.
            mask = build_action_mask(
                packet,
                public_map,
                sabotage_kinds=self._sabotage_kinds,
                emergency_uses_remaining=0,
            )
            if not mask.is_submission_legal(chosen):
                raise ValueError(
                    f"candidate policy returned a non-submission-legal intent "
                    f"{chosen!r} for {packet.agent_id!r} at tick {packet.tick}"
                )
            if self._trace is not None:
                distribution = self._policy.choice_distribution(
                    packet, public_map, memory, fsm_intent=fsm_intent
                )
        if self._trace is not None:
            self._trace.record(
                packet,
                fsm_intent=fsm_intent,
                chosen=chosen,
                distribution=distribution,
            )
        if self._on_decision is not None:
            self._on_decision(packet, public_map, memory, fsm_intent, chosen)
        return chosen

    def __getattr__(self, name: str) -> object:
        # Delegate the MeetingAwareAgent protocol + belief-fold hooks to the
        # inner TacticalAgent (the 15.8/15.10 wrapper idiom).
        return getattr(self._inner, name)


def build_candidate_factory(
    policy: BakeoffPolicy | None,
    *,
    game_map: Map,
    trace: DecisionTrace | None = None,
    on_decision: DecisionCallback | None = None,
) -> AgentFactory:
    """The candidate's OWN policy factory (Task 15.15).

    The factory the leak-test factory mode and the eval rollouts run through:
    every agent is a real role-appropriate :class:`TacticalAgent`, impostors
    wrapped so the candidate's encoder + head actually run on every impostor
    decision (the 15.10 ``_IdleExploreAgent`` reference wrapper runs no encoder
    and does not count).
    """

    sabotage_kinds = tuple(sorted(game_map.sabotages))

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        policy_impl: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy_impl = ImpostorPolicy(agent_id=agent_id)
        else:
            policy_impl = CrewmatePolicy(agent_id=agent_id)
        inner = TacticalAgent(agent_id=agent_id, policy=policy_impl, role=role)
        return _CandidateAgent(
            inner,
            policy=policy,
            sabotage_kinds=sabotage_kinds,
            trace=trace,
            on_decision=on_decision,
        )

    return factory


def rollout_candidate(
    policy: BakeoffPolicy | None,
    seed: int,
    *,
    output_dir: Path,
    game_map: Map | None = None,
    num_players: int = BAKEOFF_NUM_PLAYERS,
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS,
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE,
    meeting_runner_factory: MeetingRunnerFactory | None = None,
    max_ticks: int = DEFAULT_MAX_TICKS,
    trace: DecisionTrace | None = None,
    on_decision: DecisionCallback | None = None,
) -> EpisodeRollout:
    """Run ONE full production game with the candidate and reconstruct it.

    The single rollout path every entrant trains through and the eval protocol
    scores through (integration-risk guard (a): one runner, no protocol drift).
    Drives :class:`orchestrator.game.HeadlessGame` through the candidate's own
    factory, writes ``replay-seed-{seed}.jsonl`` under ``output_dir``, and
    returns the state-hash-verified typed episode.
    ``meeting_runner_factory=None`` is the real (deterministic fake-provider)
    meeting path; pass the 15.13 surrogate factory for the surrogate path.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    output_dir.mkdir(parents=True, exist_ok=True)
    replay_path = output_dir / f"replay-seed-{seed}.jsonl"
    factory = build_candidate_factory(
        policy, game_map=resolved_map, trace=trace, on_decision=on_decision
    )
    if meeting_runner_factory is not None:
        meeting_runner = meeting_runner_factory()
    else:
        meeting_runner = build_default_meeting_runner(
            llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
        )
    game = HeadlessGame(
        seed=seed,
        game_map=resolved_map,
        agent_factory=factory,
        replay_path=replay_path,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        scheduler=TickScheduler(max_ticks=max_ticks),
        meeting_runner=meeting_runner,
        force=True,
    )
    game.run()
    return reconstruct_episode(
        replay_path,
        game_map=resolved_map,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        episode_boundary="full_game",
    )


def inner_episode_fitness(
    rollout: EpisodeRollout,
    trace: DecisionTrace,
    *,
    anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT,
) -> float:
    """The SHARED per-episode inner fitness every ES/QD entrant optimizes.

    The tactically-reachable side-specific impostor terms + potential shaping
    (:func:`training.rewards.compute_shaped_reward`), MINUS the anchor-KL
    penalty toward the frozen FSM (``anchor_weight`` × the episode's mean
    anchor cross-entropy). The validity gate and the 15.2 referee are NEVER
    terms here — they are selection filters :func:`evaluate_candidate` applies
    after training. A truncated (tick-budget-capped) episode scores the
    documented :data:`TRUNCATED_EPISODE_FITNESS` — never a silent skip, never a
    full-game read of a truncated record.
    """

    if not rollout.complete:
        return TRUNCATED_EPISODE_FITNESS
    shaped = compute_shaped_reward(rollout, "IMPOSTOR").total()
    return shaped - anchor_weight * trace.mean_anchor_ce()


# --------------------------------------------------------------------------- #
# The entrant protocol + public result types.                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TrainedCandidate:
    """One entrant's frozen champion, ready for the fixed eval protocol.

    ``weights`` + ``config`` are the reloadable artifact
    (:func:`write_candidate_artifact` freezes them as float-hex JSON + sha256);
    ``train_metadata`` carries entrant-specific findings (the BC agreement +
    bar verdict, the MAP-Elites archive coverage, fitness traces) verbatim into
    the report row.
    """

    entrant: str
    policy: BakeoffPolicy
    weights: tuple[float, ...]
    config: Mapping[str, object]
    surrogate_uses_training: int = 0
    train_wall_clock_s: float = 0.0
    train_metadata: Mapping[str, object] = field(default_factory=dict)


@runtime_checkable
class BakeoffEntrant(Protocol):
    """The entrant seam (Task 15.15 public type — 15.16/15.17 ride it).

    An entrant owns its training loop and budget; it must train against the
    baseline-5 substrate through :func:`rollout_candidate` and return a
    :class:`TrainedCandidate`. It computes NO reported metrics — the harness's
    :func:`evaluate_candidate` is the only module that does.
    """

    @property
    def name(self) -> str: ...

    def train(self) -> TrainedCandidate: ...


class SupplyGaugeRow(BaseModel):
    """One referee evidence-supply gauge in a result row (name/measured/floor)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    measured: float | None
    floor: float | None
    passed: bool


class MetricSpread(BaseModel):
    """Min/mean/max of one metric over the N-repeat runs (experiment tier)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    values: tuple[float, ...]
    min: float
    mean: float
    max: float

    @classmethod
    def from_values(cls, values: Sequence[float]) -> "MetricSpread":
        rounded = tuple(float(value) for value in values)
        return cls(
            values=rounded,
            min=min(rounded),
            mean=math.fsum(rounded) / len(rounded),
            max=max(rounded),
        )


class DeterminismRow(BaseModel):
    """The full 15.10 ``PolicyDeterminismReport`` embedded in a result row."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    encoder_version: str
    seeds: tuple[int, ...]
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    num_frames: int
    num_state_hashes: int
    frame_stream_sha256: str
    state_hash_sha256: str
    deterministic: bool

    @classmethod
    def from_report(cls, report: PolicyDeterminismReport) -> "DeterminismRow":
        return cls(
            encoder_version=report.encoder_version,
            seeds=report.seeds,
            num_players=report.num_players,
            num_impostors=report.num_impostors,
            tasks_per_crewmate=report.tasks_per_crewmate,
            num_frames=report.num_frames,
            num_state_hashes=report.num_state_hashes,
            frame_stream_sha256=report.frame_stream_sha256,
            state_hash_sha256=report.state_hash_sha256,
            deterministic=report.deterministic,
        )


class RepeatSpread(BaseModel):
    """The N-repeat metric spread an experiment-tier row carries (15.17 seam)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    repeats: int
    inner_fitness_real: MetricSpread
    impostor_win_rate: MetricSpread
    anchor_cross_entropy: MetricSpread


class BakeoffResult(BaseModel):
    """One entrant's full metric tuple (Task 15.15 public type; 15.18 consumes).

    One row per entrant in ``results-impostor-bakeoff.jsonl``. Every field the
    definition of done names is here: the validity-gate verdict, the referee
    result (per-game score distribution + floor-trip rate + supply floors), the
    inner fitness on BOTH meeting paths (divergence is data, never collapsed),
    the anchor cross-entropy against the documented ceiling (flagged, never
    dropped), win rate + take-rate (reported, never gated), the determinism
    verdict (or the experiment-tier FAIL carrying the full report + N-repeat
    spread), the leak-test verdict through the candidate's own factory, the
    surrogate-staleness usage, and wall-clock. Signature is stable per the task
    contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    entrant: str
    tier: Literal["candidate", "experiment"]
    encoder_version: str
    genome_length: int
    weights_sha256: str
    artifact_path: str
    eval_seeds: tuple[int, ...]
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    baseline_id: str

    validity_passed: bool
    validity_failing_checks: tuple[str, ...]

    referee_passed: bool
    supply_floors_passed: bool
    referee_mean_score: float
    referee_median_score: float
    referee_scores: tuple[float, ...]
    floor_trip_rate: float
    supply_gauges: tuple[SupplyGaugeRow, ...]

    inner_fitness_real: float
    mean_shaped_reward_real: float | None
    truncated_episodes_real: int
    inner_fitness_surrogate: float | None
    truncated_episodes_surrogate: int | None
    surrogate_real_divergence: float | None

    anchor_cross_entropy: float
    anchor_ce_ceiling: float
    anchor_ce_flagged: bool
    anchor_offmenu_decisions: int
    fsm_intent_agreement: float | None

    impostor_win_rate: float
    take_rate: float | None
    take_opportunities: int

    determinism: DeterminismRow
    repeat_spread: RepeatSpread | None

    leak_test_passed: bool
    leak_packets_scanned: int | None
    leak_failure: str | None

    surrogate_uses_training: int
    surrogate_uses_eval: int
    wall_clock_train_s: float
    wall_clock_eval_s: float

    descriptor_footprint: Mapping[str, float]
    train_metadata: Mapping[str, object]

    def to_json_line(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True)


@dataclass(frozen=True)
class BakeoffProtocolConfig:
    """The FIXED eval protocol every entrant is scored under (Task 15.15).

    One instance per bake-off run; the committed defaults are the contract.
    ``surrogate_artifact_dir=None`` disables the surrogate-path column (the
    row records ``inner_fitness_surrogate=None`` — used only by tiny CI
    configurations that must not meter the committed staleness cap).
    """

    eval_seeds: tuple[int, ...]
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE
    baseline_id: str = BAKEOFF_BASELINE_ID
    anchor_ce_ceiling: float = ANCHOR_CE_CEILING
    anchor_penalty_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
    determinism_seeds: tuple[int, ...] = (1004, 1009)
    leak_seeds: tuple[int, ...] = (0, 1)
    repeat_n: int = 3
    surrogate_artifact_dir: Path | None = SURROGATE_ARTIFACT_DIR
    surrogate_use_counter: SurrogateUseCounter | None = None
    max_ticks: int = DEFAULT_MAX_TICKS

    def resolved_surrogate_counter(self) -> SurrogateUseCounter | None:
        """The SHARED cumulative use counter for this run (built lazily once).

        The staleness-cap doctrine: ONE counter outlives every runner the run
        constructs, so the committed cap is cumulative across entrants, eval
        passes, and the Goodhart re-run.
        """

        if self.surrogate_artifact_dir is None:
            return None
        if self.surrogate_use_counter is not None:
            return self.surrogate_use_counter
        counter = SurrogateUseCounter(load_staleness_cap(self.surrogate_artifact_dir))
        # A frozen dataclass: stash via object.__setattr__ so every subsequent
        # call shares the SAME counter (never a silent per-call reset).
        object.__setattr__(self, "surrogate_use_counter", counter)
        return counter


def default_protocol_config() -> BakeoffProtocolConfig:
    """The committed fixed eval protocol (the full-run defaults)."""

    return BakeoffProtocolConfig(eval_seeds=load_eval_seeds())


# --------------------------------------------------------------------------- #
# Artifact freeze/reload (float-hex JSON + sha256 sidecar).                    #
# --------------------------------------------------------------------------- #


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_candidate_artifact(
    candidate: TrainedCandidate, artifact_root: Path
) -> tuple[Path, str]:
    """Freeze one candidate under ``training/artifacts/impostor/<entrant>/``.

    ``weights.json`` is the float-hex genome
    (:func:`agents.tactical.features.weights_to_hex_json` — the Wave-1 lossless
    format), ``weights.json.sha256`` the standard sidecar
    (``<digest>  <basename>``), and ``config.json`` the entrant config needed
    to reconstruct the exact policy around the weights. Returns
    ``(entrant_dir, weights_sha256)``.
    """

    entrant_dir = artifact_root / candidate.entrant
    entrant_dir.mkdir(parents=True, exist_ok=True)
    weights_json = weights_to_hex_json(candidate.weights) + "\n"
    weights_path = entrant_dir / _WEIGHTS_FILENAME
    weights_path.write_text(weights_json)
    digest = _sha256_hex(weights_json.encode("utf-8"))
    (entrant_dir / f"{_WEIGHTS_FILENAME}.sha256").write_text(
        f"{digest}  {_WEIGHTS_FILENAME}\n"
    )
    (entrant_dir / _CONFIG_FILENAME).write_text(
        json.dumps(dict(candidate.config), indent=2, sort_keys=True) + "\n"
    )
    return entrant_dir, digest


def load_candidate_weights(entrant_dir: Path) -> tuple[float, ...]:
    """Reload a frozen genome, verifying the sha256 sidecar (fail loud on drift)."""

    weights_path = entrant_dir / _WEIGHTS_FILENAME
    raw = weights_path.read_text()
    recorded = (entrant_dir / f"{_WEIGHTS_FILENAME}.sha256").read_text().split()[0]
    actual = _sha256_hex(raw.encode("utf-8"))
    if actual != recorded:
        raise ValueError(
            f"{weights_path} hashes to {actual} but the sidecar records {recorded}"
        )
    return weights_from_hex_json(raw)


# --------------------------------------------------------------------------- #
# The fixed eval protocol.                                                     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _EvalPass:
    """One scoring pass of a candidate over the eval seed set."""

    inner_fitness: float
    mean_shaped_reward: float | None
    truncated_episodes: int
    win_rate: float
    trace: DecisionTrace
    descriptor_mean: dict[str, float]
    meetings_total: int
    meetings_ejected: int


def _score_eval_pass(
    policy: BakeoffPolicy,
    *,
    protocol: BakeoffProtocolConfig,
    game_map: Map,
    output_dir: Path,
    meeting_runner_factory: MeetingRunnerFactory | None,
) -> _EvalPass:
    trace = DecisionTrace()
    fitnesses: list[float] = []
    shaped_totals: list[float] = []
    truncated = 0
    wins = 0
    descriptor_sums = [0.0] * len(DESCRIPTOR_VECTOR_FIELDS)
    meetings_total = 0
    meetings_ejected = 0
    for seed in protocol.eval_seeds:
        episode_trace = DecisionTrace()
        rollout = rollout_candidate(
            policy,
            seed,
            output_dir=output_dir,
            game_map=game_map,
            num_players=protocol.num_players,
            num_impostors=protocol.num_impostors,
            tasks_per_crewmate=protocol.tasks_per_crewmate,
            meeting_runner_factory=meeting_runner_factory,
            max_ticks=protocol.max_ticks,
            trace=episode_trace,
        )
        fitnesses.append(
            inner_episode_fitness(
                rollout, episode_trace, anchor_weight=protocol.anchor_penalty_weight
            )
        )
        if rollout.complete:
            shaped_totals.append(compute_shaped_reward(rollout, "IMPOSTOR").total())
        else:
            truncated += 1
        if rollout.winner == "IMPOSTORS":
            wins += 1
        vector = rollout.descriptors.vector()
        for index in range(len(DESCRIPTOR_VECTOR_FIELDS)):
            descriptor_sums[index] += float(vector[index])
        meetings_total += len(rollout.meetings)
        meetings_ejected += sum(
            1 for meeting in rollout.meetings if meeting.ejected_player_id is not None
        )
        # Fold the per-episode trace into the set-level accumulators.
        trace.impostor_decisions += episode_trace.impostor_decisions
        trace.scored_decisions += episode_trace.scored_decisions
        trace.anchor_ce_sum += episode_trace.anchor_ce_sum
        trace.offmenu_decisions += episode_trace.offmenu_decisions
        trace.agreement_hits += episode_trace.agreement_hits
        trace.opportunities += episode_trace.opportunities
        trace.kills_taken += episode_trace.kills_taken
    games = len(protocol.eval_seeds)
    descriptor_mean = {
        name: descriptor_sums[index] / games
        for index, name in enumerate(DESCRIPTOR_VECTOR_FIELDS)
    }
    return _EvalPass(
        inner_fitness=math.fsum(fitnesses) / games,
        mean_shaped_reward=(
            math.fsum(shaped_totals) / len(shaped_totals) if shaped_totals else None
        ),
        truncated_episodes=truncated,
        win_rate=wins / games,
        trace=trace,
        descriptor_mean=descriptor_mean,
        meetings_total=meetings_total,
        meetings_ejected=meetings_ejected,
    )


def _write_roster_json(
    directory: Path, *, num_players: int, num_impostors: int, tasks_per_crewmate: int
) -> None:
    (directory / _ROSTER_FILENAME).write_text(
        json.dumps(
            {
                "num_players": num_players,
                "num_impostors": num_impostors,
                "tasks_per_crewmate": tasks_per_crewmate,
            }
        )
    )


def _drop_audit_sidecars(directory: Path) -> None:
    # The game writes a per-game ``*.audit.jsonl`` sidecar; the referee's
    # ``replay-seed-*`` glob would trip on it, so drop them before scoring
    # (the 15.14 evaluator precedent).
    for sidecar in directory.glob("*.audit.jsonl"):
        sidecar.unlink()


def evaluate_candidate(
    candidate: TrainedCandidate,
    protocol: BakeoffProtocolConfig,
    *,
    artifact_root: Path = _ARTIFACT_ROOT,
    game_map: Map | None = None,
) -> BakeoffResult:
    """Score one candidate through the FULL fixed eval protocol (Task 15.15).

    Every reported number is computed here and only here. The real-path pass
    (fake-provider meetings on the fixed eval seed set) is the ground truth
    every entrant re-scores on; the surrogate-path pass is the divergence
    column; the determinism harness and the leak-test factory mode run through
    the candidate's OWN policy factory. A determinism FAIL demotes the row to
    ``tier="experiment"`` and attaches the N-repeat metric spread — the row is
    never dropped.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    started = time.perf_counter()
    entrant_dir, weights_sha256 = write_candidate_artifact(candidate, artifact_root)

    with tempfile.TemporaryDirectory(prefix="ailibi-bakeoff-eval-") as tmp:
        real_dir = Path(tmp) / "real"
        real_dir.mkdir()
        _write_roster_json(
            real_dir,
            num_players=protocol.num_players,
            num_impostors=protocol.num_impostors,
            tasks_per_crewmate=protocol.tasks_per_crewmate,
        )
        real_pass = _score_eval_pass(
            candidate.policy,
            protocol=protocol,
            game_map=resolved_map,
            output_dir=real_dir,
            meeting_runner_factory=None,
        )
        _drop_audit_sidecars(real_dir)
        watchability: WatchabilityReport = compute_watchability(
            real_dir, baseline_id=protocol.baseline_id
        )
        validity = run_validity_gate(real_dir)

    surrogate_fitness: float | None = None
    surrogate_truncated: int | None = None
    surrogate_uses_eval = 0
    counter = protocol.resolved_surrogate_counter()
    if counter is not None and protocol.surrogate_artifact_dir is not None:
        uses_before = counter.uses
        surrogate_factory = load_surrogate_runner_factory(
            protocol.surrogate_artifact_dir, use_counter=counter
        )
        with tempfile.TemporaryDirectory(prefix="ailibi-bakeoff-surr-") as tmp:
            surrogate_pass = _score_eval_pass(
                candidate.policy,
                protocol=protocol,
                game_map=resolved_map,
                output_dir=Path(tmp),
                meeting_runner_factory=surrogate_factory,
            )
        surrogate_fitness = surrogate_pass.inner_fitness
        surrogate_truncated = surrogate_pass.truncated_episodes
        surrogate_uses_eval = counter.uses - uses_before

    determinism_report = run_policy_determinism(
        candidate.policy,
        seeds=protocol.determinism_seeds,
        game_map=resolved_map,
        num_players=protocol.num_players,
        num_impostors=protocol.num_impostors,
        tasks_per_crewmate=protocol.tasks_per_crewmate,
        max_ticks=protocol.max_ticks,
    )

    repeat_spread: RepeatSpread | None = None
    tier: Literal["candidate", "experiment"] = "candidate"
    if not determinism_report.deterministic:
        # Experiment tier: the row survives, carrying the full determinism
        # report plus the N-repeat spread of the headline metrics (the seam the
        # 15.17 torch entrant reports through).
        tier = "experiment"
        fitness_values = [real_pass.inner_fitness]
        win_values = [real_pass.win_rate]
        ce_values = [real_pass.trace.mean_anchor_ce()]
        for _ in range(max(0, protocol.repeat_n - 1)):
            with tempfile.TemporaryDirectory(prefix="ailibi-bakeoff-rep-") as tmp:
                repeat_pass = _score_eval_pass(
                    candidate.policy,
                    protocol=protocol,
                    game_map=resolved_map,
                    output_dir=Path(tmp),
                    meeting_runner_factory=None,
                )
            fitness_values.append(repeat_pass.inner_fitness)
            win_values.append(repeat_pass.win_rate)
            ce_values.append(repeat_pass.trace.mean_anchor_ce())
        repeat_spread = RepeatSpread(
            repeats=len(fitness_values),
            inner_fitness_real=MetricSpread.from_values(fitness_values),
            impostor_win_rate=MetricSpread.from_values(win_values),
            anchor_cross_entropy=MetricSpread.from_values(ce_values),
        )

    leak_passed = True
    leak_packets: int | None = None
    leak_failure: str | None = None
    leak_factory = build_candidate_factory(candidate.policy, game_map=resolved_map)
    try:
        leak_packets = scan_factory_packets(
            leak_factory,
            seeds=protocol.leak_seeds,
            num_players=protocol.num_players,
            num_impostors=protocol.num_impostors,
            tasks_per_crewmate=protocol.tasks_per_crewmate,
        )
    except AssertionError as error:
        leak_passed = False
        leak_failure = str(error)

    anchor_ce = real_pass.trace.mean_anchor_ce()
    agreement = (
        real_pass.trace.agreement_hits / real_pass.trace.impostor_decisions
        if real_pass.trace.impostor_decisions
        else None
    )
    floor_trips = sum(
        1 for game in watchability.per_game if game.floor_multiplier == 0.0
    )
    games_total = len(watchability.per_game)

    return BakeoffResult(
        entrant=candidate.entrant,
        tier=tier,
        encoder_version=candidate.policy.encoder_version,
        genome_length=len(candidate.weights),
        weights_sha256=weights_sha256,
        artifact_path=str(entrant_dir),
        eval_seeds=protocol.eval_seeds,
        num_players=protocol.num_players,
        num_impostors=protocol.num_impostors,
        tasks_per_crewmate=protocol.tasks_per_crewmate,
        baseline_id=protocol.baseline_id,
        validity_passed=validity.passed,
        validity_failing_checks=validity.failing_checks(),
        referee_passed=watchability.referee_passed,
        supply_floors_passed=watchability.supply_floors_passed,
        referee_mean_score=watchability.mean_score,
        referee_median_score=watchability.median_score,
        referee_scores=tuple(game.score for game in watchability.per_game),
        floor_trip_rate=(floor_trips / games_total if games_total else 0.0),
        supply_gauges=tuple(
            SupplyGaugeRow(
                name=gauge.name,
                measured=gauge.measured,
                floor=gauge.floor,
                passed=gauge.passed,
            )
            for gauge in watchability.supply_gauges
        ),
        inner_fitness_real=real_pass.inner_fitness,
        mean_shaped_reward_real=real_pass.mean_shaped_reward,
        truncated_episodes_real=real_pass.truncated_episodes,
        inner_fitness_surrogate=surrogate_fitness,
        truncated_episodes_surrogate=surrogate_truncated,
        surrogate_real_divergence=(
            surrogate_fitness - real_pass.inner_fitness
            if surrogate_fitness is not None
            else None
        ),
        anchor_cross_entropy=anchor_ce,
        anchor_ce_ceiling=protocol.anchor_ce_ceiling,
        anchor_ce_flagged=anchor_ce > protocol.anchor_ce_ceiling,
        anchor_offmenu_decisions=real_pass.trace.offmenu_decisions,
        fsm_intent_agreement=agreement,
        impostor_win_rate=real_pass.win_rate,
        take_rate=real_pass.trace.take_rate(),
        take_opportunities=real_pass.trace.opportunities,
        determinism=DeterminismRow.from_report(determinism_report),
        repeat_spread=repeat_spread,
        leak_test_passed=leak_passed,
        leak_packets_scanned=leak_packets,
        leak_failure=leak_failure,
        surrogate_uses_training=candidate.surrogate_uses_training,
        surrogate_uses_eval=surrogate_uses_eval,
        wall_clock_train_s=candidate.train_wall_clock_s,
        wall_clock_eval_s=time.perf_counter() - started,
        descriptor_footprint=real_pass.descriptor_mean,
        train_metadata=candidate.train_metadata,
    )


def run_entrant(
    entrant: BakeoffEntrant,
    protocol: BakeoffProtocolConfig,
    *,
    artifact_root: Path = _ARTIFACT_ROOT,
    game_map: Map | None = None,
) -> BakeoffResult:
    """Train one entrant, then score its champion through the fixed protocol."""

    candidate = entrant.train()
    if candidate.entrant != entrant.name:
        raise ValueError(
            f"entrant {entrant.name!r} returned a candidate labeled "
            f"{candidate.entrant!r}; the row label must match the entrant"
        )
    return evaluate_candidate(
        candidate, protocol, artifact_root=artifact_root, game_map=game_map
    )


def write_results_jsonl(results: Sequence[BakeoffResult], path: Path) -> None:
    """Emit the machine-readable per-entrant rows 15.18 consumes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(result.to_json_line() + "\n" for result in results))


# --------------------------------------------------------------------------- #
# The 15.14 obligation: the Goodhart probe under the surrogate meeting path.   #
# --------------------------------------------------------------------------- #


class SurrogateMeetingStats(BaseModel):
    """Ejection/SKIP shape of surrogate-resolved vs real-path meetings.

    An under-ejecting surrogate can hold the meeting-driven floors for the
    wrong reason, so a HELD verdict must be read next to this: how often the
    surrogate ejects at all, against the real fake-provider path on the SAME
    seeds and the SAME scripted-FSM baseline.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seeds: tuple[int, ...]
    surrogate_meetings: int
    surrogate_ejections: int
    surrogate_ejection_rate: float | None
    surrogate_skip_rate: float | None
    real_meetings: int
    real_ejections: int
    real_ejection_rate: float | None


class GoodhartSurrogateRerun(BaseModel):
    """The surrogate-path Goodhart re-run + the delta vs the 15.14 baseline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    probe: GoodhartProbeReport
    meeting_stats: SurrogateMeetingStats
    surrogate_uses: int
    committed_baseline: Mapping[str, object]
    delta_verdict: str
    wall_clock_s: float

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2)


def _baseline_meeting_stats(
    seeds: Sequence[int],
    *,
    surrogate_factory: MeetingRunnerFactory,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    game_map: Map,
) -> SurrogateMeetingStats:
    def outcome_counts(
        meeting_runner_factory: MeetingRunnerFactory | None,
    ) -> tuple[int, int]:
        meetings = 0
        ejections = 0
        with tempfile.TemporaryDirectory(prefix="ailibi-goodhart-stats-") as tmp:
            for seed in seeds:
                rollout = rollout_candidate(
                    None,
                    seed,
                    output_dir=Path(tmp),
                    game_map=game_map,
                    num_players=num_players,
                    num_impostors=num_impostors,
                    tasks_per_crewmate=tasks_per_crewmate,
                    meeting_runner_factory=meeting_runner_factory,
                )
                meetings += len(rollout.meetings)
                ejections += sum(
                    1
                    for meeting in rollout.meetings
                    if meeting.ejected_player_id is not None
                )
        return meetings, ejections

    surrogate_meetings, surrogate_ejections = outcome_counts(surrogate_factory)
    real_meetings, real_ejections = outcome_counts(None)
    return SurrogateMeetingStats(
        seeds=tuple(seeds),
        surrogate_meetings=surrogate_meetings,
        surrogate_ejections=surrogate_ejections,
        surrogate_ejection_rate=(
            surrogate_ejections / surrogate_meetings if surrogate_meetings else None
        ),
        surrogate_skip_rate=(
            1.0 - surrogate_ejections / surrogate_meetings
            if surrogate_meetings
            else None
        ),
        real_meetings=real_meetings,
        real_ejections=real_ejections,
        real_ejection_rate=(real_ejections / real_meetings if real_meetings else None),
    )


def run_goodhart_surrogate_rerun(
    *,
    config: ESConfig,
    surrogate_artifact_dir: Path = SURROGATE_ARTIFACT_DIR,
    use_counter: SurrogateUseCounter | None = None,
    num_players: int = BAKEOFF_NUM_PLAYERS,
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS,
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE,
    baseline_id: str = BAKEOFF_BASELINE_ID,
    game_map: Map | None = None,
) -> GoodhartSurrogateRerun:
    """Discharge the 15.14 obligation through the probe's OWN entry point.

    Calls ``run_goodhart_probe(meeting_runner_factory=<surrogate>)`` — which
    ALWAYS includes the forced single-tactic reachability sweep, the net that
    found the 15.14 exploit (the committed ES budget alone only recovered to
    baseline, +1.7%) — and pairs the verdict with the surrogate's measured
    ejection/SKIP rate on the scripted-FSM baseline plus the delta against the
    committed 15.14 fake-provider numbers.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    started = time.perf_counter()
    counter = (
        use_counter
        if use_counter is not None
        else SurrogateUseCounter(load_staleness_cap(surrogate_artifact_dir))
    )
    uses_before = counter.uses
    surrogate_factory = load_surrogate_runner_factory(
        surrogate_artifact_dir, use_counter=counter
    )
    probe = run_goodhart_probe(
        config=config,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        baseline_id=baseline_id,
        meeting_runner_factory=surrogate_factory,
    )
    meeting_stats = _baseline_meeting_stats(
        config.fitness_seeds,
        surrogate_factory=surrogate_factory,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=resolved_map,
    )
    committed = dict(GOODHART_9P2I_BASELINE)
    delta_verdict = (
        f"15.14 fake-provider verdict {committed['verdict']} "
        f"(strongest reachable {committed['strongest_reachable_score']} via "
        f"{committed['strongest_reachable_tactic']}) -> surrogate-path verdict "
        f"{probe.verdict} (champion {probe.champion_mean_score}, strongest "
        f"reachable {probe.strongest_reachable_score}, referee_passed="
        f"{probe.champion_referee_passed})"
    )
    return GoodhartSurrogateRerun(
        probe=probe,
        meeting_stats=meeting_stats,
        surrogate_uses=counter.uses - uses_before,
        committed_baseline=committed,
        delta_verdict=delta_verdict,
        wall_clock_s=time.perf_counter() - started,
    )


# --------------------------------------------------------------------------- #
# CLI — the committed entry point every reported number regenerates from.      #
# --------------------------------------------------------------------------- #


def _build_entrants(
    budget: str, protocol: BakeoffProtocolConfig
) -> list[BakeoffEntrant]:
    """Construct the four entrants at the requested budget (lazy imports).

    Local imports keep the module graph acyclic: entrant modules import THIS
    module for the protocol types and the shared rollout runner.
    """

    from training.bakeoff.bc import BcDaggerEntrant, bc_budget
    from training.bakeoff.map_elites import MapElitesEntrant, map_elites_budget
    from training.bakeoff.policy_es import PolicyEsEntrant, policy_es_budget
    from training.bakeoff.utility_es import UtilityEsEntrant, utility_es_budget

    anchor_weight = protocol.anchor_penalty_weight
    bc = BcDaggerEntrant(config=bc_budget(budget))
    bc_candidate_holder: list[TrainedCandidate] = []

    def bc_candidate() -> TrainedCandidate:
        # Train the BC clone AT MOST ONCE per _build_entrants call, no matter
        # who asks first — the BC entrant's own train() or an ES/QD warm
        # start. BC training is deterministic under its seeds, so on-demand
        # training inside a `--entrant policy-es` / `--entrant map-elites`
        # rerun reproduces the exact genome the full run warm-started from —
        # a filtered rerun never silently drops the committed warm start
        # (Codex review on PR #242).
        if not bc_candidate_holder:
            bc_candidate_holder.append(bc.train())
        return bc_candidate_holder[0]

    class _WarmStartingBc:
        """Train BC once (shared with the warm-start closure); emit its row."""

        name = bc.name

        def train(self) -> TrainedCandidate:
            return bc_candidate()

    def bc_genome() -> tuple[float, ...] | None:
        return bc_candidate().weights

    return [
        _WarmStartingBc(),
        UtilityEsEntrant(config=utility_es_budget(budget, anchor_weight=anchor_weight)),
        PolicyEsEntrant(
            config=policy_es_budget(budget, anchor_weight=anchor_weight),
            warm_start=bc_genome,
        ),
        MapElitesEntrant(
            config=map_elites_budget(budget, anchor_weight=anchor_weight),
            warm_start=bc_genome,
        ),
    ]


def _committed_goodhart_config(eval_seeds: tuple[int, ...]) -> ESConfig:
    """The committed 15.14 ES budget re-anchored on the fixed eval seed set."""

    return ESConfig(
        generations=6,
        population=6,
        sigma=0.5,
        seed=0,
        fitness_seeds=eval_seeds,
        init_scale=0.5,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m training.bakeoff.harness",
        description="The Task 15.15 impostor bake-off harness.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run", help="Train + evaluate the four entrants; write jsonl + artifacts."
    )
    run_parser.add_argument("--budget", choices=("ci", "full"), default="full")
    run_parser.add_argument(
        "--results", type=Path, default=_RESULTS_JSONL_PATH, help="Output jsonl path."
    )
    run_parser.add_argument(
        "--artifacts", type=Path, default=_ARTIFACT_ROOT, help="Artifact root dir."
    )
    run_parser.add_argument(
        "--entrant",
        choices=("bc-dagger", "utility-es", "policy-es", "map-elites", "all"),
        default="all",
    )

    goodhart_parser = subparsers.add_parser(
        "goodhart-surrogate",
        help="Re-run the 15.14 Goodhart probe under the surrogate meeting path.",
    )
    goodhart_parser.add_argument(
        "--budget", choices=("ci", "committed"), default="committed"
    )

    args = parser.parse_args(argv)
    if args.command == "run":
        protocol = default_protocol_config()
        entrants = _build_entrants(args.budget, protocol)
        if args.entrant != "all":
            entrants = [entrant for entrant in entrants if entrant.name == args.entrant]
            if not entrants:
                raise SystemExit(f"unknown entrant {args.entrant!r}")
        results = [
            run_entrant(entrant, protocol, artifact_root=args.artifacts)
            for entrant in entrants
        ]
        write_results_jsonl(results, args.results)
        for result in results:
            print(result.to_json_line())
        return 0

    eval_seeds = load_eval_seeds()
    if args.budget == "ci":
        config = ESConfig(
            generations=1,
            population=1,
            sigma=0.5,
            seed=0,
            fitness_seeds=eval_seeds[:1],
        )
    else:
        config = _committed_goodhart_config(eval_seeds)
    rerun = run_goodhart_surrogate_rerun(config=config)
    print(rerun.to_json())
    return 0


__all__ = [
    "ANCHOR_CE_CEILING",
    "ANCHOR_CE_EPSILON",
    "BAKEOFF_BASELINE_ID",
    "BAKEOFF_NUM_IMPOSTORS",
    "BAKEOFF_NUM_PLAYERS",
    "BAKEOFF_TASKS_PER_CREWMATE",
    "BC_INTENT_AGREEMENT_BAR",
    "BakeoffEntrant",
    "BakeoffPolicy",
    "BakeoffProtocolConfig",
    "BakeoffResult",
    "DEFAULT_ANCHOR_PENALTY_WEIGHT",
    "DecisionCallback",
    "DecisionTrace",
    "DeterminismRow",
    "GoodhartSurrogateRerun",
    "MetricSpread",
    "RepeatSpread",
    "SupplyGaugeRow",
    "SurrogateMeetingStats",
    "TRUNCATED_EPISODE_FITNESS",
    "TrainedCandidate",
    "build_candidate_factory",
    "default_protocol_config",
    "evaluate_candidate",
    "inner_episode_fitness",
    "intent_key",
    "load_candidate_weights",
    "load_eval_seeds",
    "load_train_seeds",
    "load_val_seeds",
    "main",
    "rollout_candidate",
    "run_entrant",
    "run_goodhart_surrogate_rerun",
    "write_candidate_artifact",
    "write_results_jsonl",
]


if __name__ == "__main__":
    raise SystemExit(main())
