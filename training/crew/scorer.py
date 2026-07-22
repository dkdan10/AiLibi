"""The learned crew option scorer + training entry + the crew eval twin (15.16).

Three responsibilities, mirroring the 15.15 split without editing it:

1. **The frozen candidate.** :class:`CrewOptionScorer` — a linear utility over
   the observable-only crew option menu (:mod:`training.crew.options`). A pure
   function of ``(packet, public_map, memory, fsm_intent)``: impostor decisions
   delegate to the scripted FSM (the impostor stays FROZEN this track — the
   exact inverse of the 15.15 bake-off, whose crew stayed frozen), crew
   decisions enumerate the menu, score each option with a linear head, and
   realize the argmax (score DESC, canonical intent-key ASC — the repo's
   lexical tie-break idiom). Implements the 15.15
   :class:`training.bakeoff.harness.BakeoffPolicy` /
   :class:`training.determinism.FramePolicy` shape, so the 15.10 determinism
   harness runs it unchanged.
2. **The training entry.** :class:`CrewEsEntrant` — the 15.14 ``(1 + λ)`` ES
   core (:mod:`training.bakeoff.es`, consumed read-only) climbing the crew
   inner fitness: the tactically-reachable crew terms + potential shaping
   (:func:`training.rewards.compute_shaped_reward` with side ``"CREWMATE"`` —
   task progress, survival, correctly-routed reports, the owner-ratified
   engine-truth ``patrol_coverage`` proxy, plus the terminal win) MINUS the
   anchor cross-entropy toward the frozen
   :class:`~agents.tactical.crewmate_policy.CrewmatePolicy` (log-loss at the
   FSM's deterministic choice, exactly as 15.15 defines it).
3. **The crew eval twin.** :func:`evaluate_crew_candidate` — the fixed 15.15
   protocol SHAPE (gate / referee / fitness / determinism / leak) on the same
   frozen eval seed set (``load_eval_seeds``), emitted as
   :class:`CrewTrackResult` rows into ``training/reports/results-crew-track.jsonl``
   with artifacts frozen under ``training/artifacts/crew/``. The 15.15 harness
   cannot drive a learned CREW side (its ``_CandidateAgent`` interposes
   impostor decisions only and its trace/fitness are impostor-specific), so
   this module carries the crew-side twin — the documented generalization ask
   lives in the crew report, and ``training/bakeoff/harness.py`` /
   ``training/bakeoff/es.py`` stay read-only per the task contract.

Emergency semantics: the wrapper (:class:`_CrewCandidateAgent`) always drives
the inner FSM first, so the agent's perception, memory, and
``EmergencyPacingTracker`` pacing/announce bookkeeping run exactly as in
production; the menu's emergency option exists only when that tracker-gated FSM
took the button course (see :mod:`training.crew.options`), and the emitted
press carries the FSM's ``reason`` payload — submission-legal under
``build_action_mask`` via the 15.16 canonicalization region this task closes.

The coverage-cue diagnostic (:class:`CoverageCueDiagnostic`) implements the Q6
obligation (owner, 2026-07-09, mid-wave review): it correlates earned
``patrol_coverage``-style credit (the deciding crew agent co-located with a
living impostor) with the agent's OWN contemporaneous suspicion toward the
shadowed player. Engine-truth roles feed ONLY this diagnostic — never a policy
input, never a reward re-definition.

Task 15.22 (audits/audit-phase-15-pause.md decision 5) adds the OPTIONAL widened
basis: an :class:`~training.crew.options.OwnedTaskOptionBasis` passed to
:class:`CrewOptionScorer` / :func:`build_crew_scorer` / :class:`CrewEsEntrant`
routes scoring through the widened option menu (the ``nearest_task`` addition +
the four owned-task scalars over ``SelfView.owned_task_ids``) and bumps the
reported encoder string to :data:`OWNED_TASK_ENCODER_VERSION` — the four-item
review's item 4: the version bump lives on the TRAINING-side basis; the
production encoder (``agents/tactical/features.py``) is untouched. ``basis=None``
is the 15.16 behavior byte-identical. The wrapper's override validation gains a
legality mirror (:func:`_owned_task_do_task_is_submission_legal`): the action
mask (``training/env.py``, read-only this task) enumerates ``do_task`` only for
the engine-fed ``pending_task_id`` — pre-15.22 the packet carried no owned set —
while the engine accepts a ``do_task`` for ANY owned unfinished task in the
actor's room, so the wrapper carries the mask-invisible mirror (the
emergency-uses tracker precedent for wrapper-carried legality inputs).

Task 18.16 wires the GO-gated conviction term into the crew inner fitness. The
seam exists HERE because crew fitness does NOT route through
``training/bakeoff/harness.py`` — without :func:`crew_inner_episode_fitness`
carrying its own optional ``conviction`` term the crew campaign would train
without that gradient. The term is the SAME frozen 18.15 artifact and the SAME
shared :class:`~training.bakeoff.harness.ConvictionFitnessTerm` object the
impostor side takes (one :class:`~training.conviction.model.ConvictionUseCounter`
per run threaded through both); :class:`CrewDecisionTrace` grows the
predicted-supply accumulators the impostor trace already carries. Under NO-GO
the term is structurally absent (``conviction=None``), never zero-weighted, and
:func:`evaluate_crew_candidate` stamps the same provenance triple onto the row.
"""

from __future__ import annotations

import argparse
import json
import math
import tempfile
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Final, Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.features import beliefs_suspicion, quantize_unit_interval
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import Map, load_canonical_map
from eval.leak_test import scan_factory_packets
from eval.validity import run_validity_gate
from eval.watchability import WatchabilityReport, compute_watchability
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from observation.action_intent import ActionIntent, DoTaskIntent
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
from training.bakeoff.es import ESConfig, evolve, k_seed_mean
from training.bakeoff.goodhart import MeetingRunnerFactory
from training.bakeoff.harness import (
    ANCHOR_CE_CEILING,
    ANCHOR_CE_EPSILON,
    BAKEOFF_BASELINE_ID,
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    CONVICTION_ARTIFACT_DIR,
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    DEFAULT_CONVICTION_WEIGHT,
    TRUNCATED_EPISODE_FITNESS,
    ConvictionFitnessTerm,
    DeterminismRow,
    MetricSpread,
    SupplyGaugeRow,
    TrainedCandidate,
    intent_key,
    load_conviction_row_provenance,
    load_eval_seeds,
    load_train_seeds,
    write_candidate_artifact,
)
from training.conviction.model import ConvictionPrediction
from training.crew.options import (
    _NEUTRAL_SUSPICION_QUANTUM,
    _SUSPICION_GATE_QUANTUM,
    CREW_OPTION_FEATURE_NAMES,
    CrewOption,
    OwnedTaskOptionBasis,
    crew_genome_length,
    enumerate_crew_options,
)
from training.determinism import PolicyFrame, run_policy_determinism
from training.env import build_action_mask
from training.rewards import compute_shaped_reward
from training.rollout import (
    DESCRIPTOR_VECTOR_FIELDS,
    EpisodeRollout,
    reconstruct_episode,
)

# The policy encoder tag reported in the row and hashed by the 15.10
# determinism harness. This candidate's feature basis is the per-option crew
# featurizer — NOT the shared encoder-v2 memory vector — so it carries its own
# version string (the 15.15 utility-es precedent).
ENCODER_VERSION: Final[str] = "crew-option-features-v1"

# The Task 15.22 widened-basis encoder tag (the four-item review's item 4 — the
# version bump lives on the training-side basis; the production encoder
# ``agents/tactical/features.py`` is NOT touched). Reported when a
# :class:`~training.crew.options.OwnedTaskOptionBasis` is set.
OWNED_TASK_ENCODER_VERSION: Final[str] = "crew-option-features-v2"

# The FSM-delegate baseline's tag: it runs no encoder at all.
FSM_BASELINE_ENCODER_VERSION: Final[str] = "crew-fsm-delegate-v1"

# The entrant / baseline row labels.
CREW_ENTRANT_NAME: Final[str] = "crew-utility-es"
# The Task 15.22 widened-basis entrant label (its own artifact subdir + jsonl).
CREW_OWNED_TASKS_ENTRANT_NAME: Final[str] = "crew-owned-tasks-es"
CREW_FSM_BASELINE_NAME: Final[str] = "crew-fsm-baseline"

# The FO-8 small-gain prior the report states the measured delta against
# (experiments/lab/ml_spike/fo8_crew_buddy.py; audits/post-phase-14-ML-planning.md
# §8.2): learned buddy/task gate 11/12 crew wins vs the FSM crew's 10/12 —
# +1 game on the spike's 12-seed set.
FO8_PRIOR_FSM_WINS: Final[int] = 10
FO8_PRIOR_LEARNED_WINS: Final[int] = 11
FO8_PRIOR_SEEDS: Final[int] = 12

# The committed TRAINING episode budget (see CrewEsConfig): ~6-12× the
# scripted crew's typical game length (16-49 ticks on the train seeds), and
# generous against the FO-8 spike's own ``max_ticks=80`` training budget. Only
# training rides it; the eval protocol keeps the production 1000-tick budget.
TRAIN_MAX_TICKS: Final[int] = 300

_RESULTS_JSONL_PATH: Final[Path] = Path("training/reports/results-crew-track.jsonl")
# The Task 15.22 widened-basis rows land in their own jsonl (the CLI default
# when ``--basis owned-tasks`` is selected); the 15.16 track file is untouched.
_OWNED_TASK_RESULTS_JSONL_PATH: Final[Path] = Path(
    "training/reports/results-crew-owned-tasks.jsonl"
)
_ARTIFACT_ROOT: Final[Path] = Path("training/artifacts/crew")
_ROSTER_FILENAME: Final[str] = "roster.json"


def _softmax(scores: Sequence[float]) -> list[float]:
    """Numerically-stable softmax (peak-shifted), pure stdlib math."""

    peak = max(scores)
    exps = [math.exp(score - peak) for score in scores]
    total = math.fsum(exps)
    return [value / total for value in exps]


def _owned_task_do_task_is_submission_legal(
    intent: ActionIntent, *, packet: ObservationPacket, public_map: PublicMapView
) -> bool:
    """The Task 15.22 wrapper legality mirror for an owned-task ``do_task``.

    The action mask (``training/env.py``, read-only this task) enumerates
    ``do_task`` ONLY for the engine-fed ``pending_task_id`` — pre-15.22 the
    packet carried no owned set, so the mask has no owned-task vocabulary — while
    the engine (``engine/tick.py::_apply_do_task``) accepts a ``do_task`` for ANY
    of the actor's owned unfinished tasks when it stands in the task room, is not
    vented, and no gating sabotage is active. The widened basis's ``nearest_task``
    override submits exactly such a task, so the wrapper carries this mirror over
    the widened self channel (the emergency-uses tracker precedent for a
    wrapper-carried legality input the mask cannot see). Mirrors the engine
    predicate over the OBSERVABLE surface: a crewmate actor, the task in its own
    :attr:`observation.packet.SelfView.owned_task_ids`, not vented, no gating
    sabotage, and the task's room equal to the actor's room. Returns ``False``
    for any non-``do_task`` intent, so a genuinely off-vocabulary override still
    fails the mask and raises.
    """

    if not isinstance(intent, DoTaskIntent):
        return False
    self_state = packet.self_state
    global_state = packet.global_state
    task_id = intent.payload.task_id
    return (
        intent.actor == packet.agent_id
        and self_state.role == "CREWMATE"
        and task_id in self_state.owned_task_ids
        and not self_state.in_vent
        and not (global_state.sabotage_active and global_state.sabotage_is_gating)
        and public_map.task_locations.get(task_id) == self_state.room
    )


@runtime_checkable
class CrewTrackPolicy(Protocol):
    """The crew-track policy seam — the 15.15 ``BakeoffPolicy`` shape plus the
    optional emergency-uses tracker input.

    ``emergency_uses_remaining`` is the one mask caveat the pure decision
    surface cannot derive (the actor's spent-use count is not on the
    observation packet — the ``EmergencyPacingTracker`` precedent): the eval
    wrapper passes its tracked count so the menu's emergency PRESS mirrors the
    mask's legality exactly, while fixed-signature callers (the 15.10
    determinism harness's ``FramePolicy`` surface) omit it and the press keys
    on the FSM's own tracker-gated proposal alone. Both concrete policies in
    this module satisfy :class:`training.bakeoff.harness.BakeoffPolicy` and
    :class:`training.determinism.FramePolicy` structurally.
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
        emergency_uses_remaining: int | None = None,
    ) -> PolicyFrame: ...

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> Mapping[str, float]: ...


class CrewOptionScorer:
    """The frozen learned-utility candidate over the crew option menu (15.16).

    A pure function of ``(packet, public_map, memory, fsm_intent)`` plus the
    optional wrapper-tracked ``emergency_uses_remaining``: impostor decisions
    delegate to the scripted FSM (the frozen opponent), crew decisions
    enumerate :func:`training.crew.options.enumerate_crew_options`, score each
    option with a linear head (``dot(weights[:-1], features) + weights[-1]``),
    and realize the argmax (score DESC, canonical intent-key ASC). Every tie is
    lexical and the arithmetic is stdlib ``math`` only, so the 15.10 double-run
    digests agree. Signature is stable per the task contract.
    """

    def __init__(
        self,
        *,
        weights: Sequence[float],
        game_map: Map | None = None,
        basis: OwnedTaskOptionBasis | None = None,
    ) -> None:
        # ``basis`` (Task 15.22) selects the widened option menu; ``None`` is the
        # 15.16 behavior byte-identical (the pinned 22-weight genome + v1 tag).
        self._basis = basis
        expected = basis.genome_length() if basis is not None else crew_genome_length()
        if len(weights) != expected:
            raise ValueError(f"weights length {len(weights)} != expected {expected}")
        self._weights = tuple(float(weight) for weight in weights)
        resolved_map = game_map if game_map is not None else load_canonical_map()
        # Kept for API symmetry with the mask / the 15.15 policies (sorted for
        # replay stability); the crew menu itself needs no sabotage vocabulary.
        self._sabotage_kinds = tuple(sorted(resolved_map.sabotages))

    @property
    def encoder_version(self) -> str:
        return (
            OWNED_TASK_ENCODER_VERSION if self._basis is not None else ENCODER_VERSION
        )

    def _enumerate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None,
    ) -> tuple[CrewOption, ...]:
        # Route through the widened basis when set (Task 15.22), otherwise the
        # pinned 15.16 menu — one seam so evaluate/choice_distribution stay in
        # lockstep on the option set they score.
        if self._basis is not None:
            return self._basis.enumerate(
                packet,
                public_map,
                memory,
                fsm_intent=fsm_intent,
                emergency_uses_remaining=emergency_uses_remaining,
            )
        return enumerate_crew_options(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=emergency_uses_remaining,
        )

    @property
    def weights(self) -> tuple[float, ...]:
        return self._weights

    def _score(self, option: CrewOption) -> float:
        head = self._weights[:-1]
        bias = self._weights[-1]
        return (
            math.fsum(
                weight * feature
                for weight, feature in zip(head, option.features, strict=True)
            )
            + bias
        )

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> PolicyFrame:
        if packet.self_state.role != "CREWMATE":
            return PolicyFrame(
                agent_id=packet.agent_id,
                tick=packet.tick,
                features=(),
                logits=(),
                intent=fsm_intent,
            )
        options = self._enumerate(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=emergency_uses_remaining,
        )
        scores = [self._score(option) for option in options]
        best_option, _ = min(
            zip(options, scores, strict=True),
            key=lambda pair: (-pair[1], intent_key(pair[0].intent)),
        )
        features = tuple(chain.from_iterable(option.features for option in options))
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=features,
            logits=tuple(scores),
            intent=best_option.intent,
        )

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> Mapping[str, float]:
        if packet.self_state.role != "CREWMATE":
            return {intent_key(fsm_intent): 1.0}
        options = self._enumerate(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=emergency_uses_remaining,
        )
        scores = [self._score(option) for option in options]
        probabilities = _softmax(scores)
        distribution: dict[str, float] = {}
        for option, probability in zip(options, probabilities, strict=True):
            key = intent_key(option.intent)
            distribution[key] = distribution.get(key, 0.0) + probability
        return distribution


def build_crew_scorer(
    weights: Sequence[float],
    *,
    game_map: Map | None = None,
    basis: OwnedTaskOptionBasis | None = None,
) -> CrewOptionScorer:
    """Construct the frozen scorer around a flat genome (the artifact-reload seam).

    ``basis`` (Task 15.22) selects the widened option menu + the 27-weight
    genome; ``None`` reloads a pinned 15.16 22-weight champion byte-identically.
    """

    return CrewOptionScorer(weights=weights, game_map=game_map, basis=basis)


class FsmCrewBaseline:
    """The scripted-FSM crew baseline as a candidate policy (Task 15.16).

    A transparent delegate — every decision returns the FSM's own intent with
    an empty feature/logit frame and a delta choice distribution (so its anchor
    cross-entropy is exactly 0 and its intent agreement exactly 1). It exists
    so the FSM crew gets a full protocol row (gate / referee / determinism /
    leak) through the SAME eval path the trained scorer rides — the
    scorer-vs-FSM deltas the definition of done names are read row-to-row.
    """

    @property
    def encoder_version(self) -> str:
        return FSM_BASELINE_ENCODER_VERSION

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> PolicyFrame:
        del public_map, memory, emergency_uses_remaining
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(),
            logits=(),
            intent=fsm_intent,
        )

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> Mapping[str, float]:
        del packet, public_map, memory, emergency_uses_remaining
        return {intent_key(fsm_intent): 1.0}


@dataclass
class CrewDecisionTrace:
    """Accumulators over one (or many) rollouts' CREW decisions (Task 15.16).

    The crew twin of the 15.15 ``DecisionTrace``: ``anchor_ce_sum`` accumulates
    ``-log P(candidate emits the FSM's choice)`` per crew decision (clamped at
    ``-log ANCHOR_CE_EPSILON``; clamped decisions are tallied in
    ``offmenu_decisions`` — an explicit tally, not a silent clamp), and
    ``agreement_hits`` counts canonical-key agreement with the FSM anchor. The
    impostor-specific take-rate accumulators have no crew analogue and are
    deliberately absent; the crew-side outcome metrics (meeting-trigger
    quality, correct-report rate, survival, task pace) are episode-level facts
    read from the typed rollout record, not per-decision tallies.

    ``conviction_supply_sum`` / ``conviction_meetings`` (Task 18.16) accumulate
    the conviction term's predicted-supply signal exactly as the impostor
    :class:`~training.bakeoff.harness.DecisionTrace` does, so
    :func:`crew_inner_episode_fitness` can add the GO-gated term on the crew
    side too.
    """

    crew_decisions: int = 0
    scored_decisions: int = 0
    anchor_ce_sum: float = 0.0
    offmenu_decisions: int = 0
    agreement_hits: int = 0
    conviction_supply_sum: float = 0.0
    conviction_meetings: int = 0

    def record(
        self,
        *,
        fsm_intent: ActionIntent,
        chosen: ActionIntent,
        distribution: Mapping[str, float] | None,
    ) -> None:
        self.crew_decisions += 1
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

    def fold(self, other: CrewDecisionTrace) -> None:
        """Fold a per-episode trace into this set-level accumulator."""

        self.crew_decisions += other.crew_decisions
        self.scored_decisions += other.scored_decisions
        self.anchor_ce_sum += other.anchor_ce_sum
        self.offmenu_decisions += other.offmenu_decisions
        self.agreement_hits += other.agreement_hits
        self.conviction_supply_sum += other.conviction_supply_sum
        self.conviction_meetings += other.conviction_meetings

    def mean_anchor_ce(self) -> float:
        """Mean per-decision anchor cross-entropy (0.0 when nothing was scored)."""

        if self.scored_decisions == 0:
            return 0.0
        return self.anchor_ce_sum / self.scored_decisions

    def record_conviction_prediction(self, prediction: ConvictionPrediction) -> None:
        """Accumulate one predicted meeting's supply score (Task 18.16).

        Same semantics as the impostor
        :meth:`~training.bakeoff.harness.DecisionTrace.record_conviction_prediction`:
        ``expected_flags`` is the flags head's real-valued SUPPLY score. One
        call per model-predicted meeting; the metering is the caller's (via the
        shared :class:`~training.bakeoff.harness.ConvictionFitnessTerm`).
        """

        self.conviction_supply_sum += prediction.expected_flags
        self.conviction_meetings += 1

    def mean_predicted_supply(self) -> float:
        """Mean predicted supply over recorded meetings (0.0 when none).

        A no-meeting episode carries no supply signal, so the term contributes
        exactly 0.0 — documented, never a silent NaN from a zero divide.
        """

        if self.conviction_meetings == 0:
            return 0.0
        return self.conviction_supply_sum / self.conviction_meetings


@dataclass
class CoverageCueDiagnostic:
    """The Q6 coverage-cue diagnostic (owner 2026-07-09, mid-wave review).

    ``training/rewards.py``'s ``patrol_coverage`` credits engine-truth
    co-location with an impostor's ACTUAL room (the ratified doctrine). This
    diagnostic measures whether that credit is CUED: at every crew decision, a
    decision is *credited* when a living impostor is co-located in the deciding
    agent's own room (visible players are alive by construction — the
    per-decision attribution of the frame-level ``crew_shadowing_impostor``
    flag), and the agent's OWN contemporaneous quantized suspicion toward the
    shadowed impostor(s) is sampled. Mostly UN-CUED coverage (shadowing players
    the agent holds no suspicion about) means the term is training crowding
    rather than patrol — the pause revisits with exactly this data.

    Engine-truth roles feed ONLY this diagnostic (the eval factory records the
    roster it constructed); they never reach a policy input or a reward
    re-definition. The co-located-innocent aggregate is the contrast column:
    cue separation is the mean suspicion toward shadowed impostors minus the
    mean suspicion toward co-located innocents at the same decision points.
    """

    crew_decisions: int = 0
    credited_decisions: int = 0
    suspicion_quantum_sum: int = 0
    cued_decisions: int = 0
    strongly_cued_decisions: int = 0
    innocent_colocated_decisions: int = 0
    innocent_suspicion_quantum_sum: int = 0

    def record(
        self,
        packet: ObservationPacket,
        memory: AgentMemory,
        roles: Mapping[PlayerId, Role],
    ) -> None:
        own_room = packet.self_state.room
        colocated = [
            view.id for view in packet.visible_players if view.room == own_room
        ]
        shadowed = [pid for pid in colocated if roles.get(pid) == "IMPOSTOR"]
        innocents = [pid for pid in colocated if roles.get(pid) == "CREWMATE"]
        self.crew_decisions += 1
        if shadowed:
            quantum = max(
                quantize_unit_interval(beliefs_suspicion(memory, pid))
                for pid in shadowed
            )
            self.credited_decisions += 1
            self.suspicion_quantum_sum += quantum
            if quantum > _NEUTRAL_SUSPICION_QUANTUM:
                self.cued_decisions += 1
            if quantum >= _SUSPICION_GATE_QUANTUM:
                self.strongly_cued_decisions += 1
        if innocents:
            self.innocent_colocated_decisions += 1
            self.innocent_suspicion_quantum_sum += max(
                quantize_unit_interval(beliefs_suspicion(memory, pid))
                for pid in innocents
            )

    def to_row(self) -> CoverageCueRow:
        credited = self.credited_decisions
        mean_shadowed = (
            self.suspicion_quantum_sum / credited / 1000.0 if credited else None
        )
        mean_innocent = (
            self.innocent_suspicion_quantum_sum
            / self.innocent_colocated_decisions
            / 1000.0
            if self.innocent_colocated_decisions
            else None
        )
        return CoverageCueRow(
            crew_decisions=self.crew_decisions,
            credited_decisions=credited,
            credited_rate=(
                credited / self.crew_decisions if self.crew_decisions else 0.0
            ),
            mean_suspicion_toward_shadowed=mean_shadowed,
            cued_rate=(self.cued_decisions / credited if credited else None),
            strongly_cued_rate=(
                self.strongly_cued_decisions / credited if credited else None
            ),
            mean_suspicion_toward_colocated_innocents=mean_innocent,
            cue_separation=(
                mean_shadowed - mean_innocent
                if mean_shadowed is not None and mean_innocent is not None
                else None
            ),
        )


class CoverageCueRow(BaseModel):
    """The Q6 diagnostic column of a crew result row (see the diagnostic class)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    crew_decisions: int
    credited_decisions: int
    credited_rate: float
    mean_suspicion_toward_shadowed: float | None
    cued_rate: float | None
    strongly_cued_rate: float | None
    mean_suspicion_toward_colocated_innocents: float | None
    cue_separation: float | None


class _CrewCandidateAgent:
    """Interposition wrapper driving a crew candidate through the production loop.

    The crew twin of the 15.15 ``_CandidateAgent``: drives the inner FSM first
    (so perception, the agent's OWN memory, and the ``EmergencyPacingTracker``
    pacing/announce bookkeeping run exactly as in production — the wrapper
    never touches the tracker), then — for CREW decisions only, the impostor
    side stays the frozen scripted FSM throughout — evaluates the candidate
    off the inner agent's live :class:`~agents.memory.store.AgentMemory` and
    lets its intent drive the game. An OVERRIDING intent (one that differs
    from the FSM's own proposal) is validated against the legal-action mask
    with the wrapper's tracked emergency-uses count, so an off-vocabulary
    candidate fails loud; a DELEGATED intent is the production FSM's own
    behavior and is returned unvalidated, exactly as an uninterposed game
    would submit it. With ``policy=None`` the wrapper is a transparent FSM
    delegate that still feeds the trace/diagnostic.
    """

    def __init__(
        self,
        inner: TacticalAgent,
        *,
        policy: CrewTrackPolicy | None,
        sabotage_kinds: tuple[str, ...],
        emergency_uses_per_player: int,
        trace: CrewDecisionTrace | None,
        diagnostic: CoverageCueDiagnostic | None,
        roles: Mapping[PlayerId, Role],
    ) -> None:
        self._inner = inner
        self._agent_id = inner.agent_id
        self._policy = policy
        self._sabotage_kinds = sabotage_kinds
        self._trace = trace
        self._diagnostic = diagnostic
        self._roles = roles
        # The mask's emergency-uses tracker (the _InterposedAgent precedent):
        # the actor's spent-use count is not on the observation surface, so the
        # wrapper carries it, decremented when THIS agent's own emergency opens
        # a meeting (engine truth via note_meeting_concluded).
        self._emergency_uses_remaining = emergency_uses_per_player

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        fsm_intent = self._inner.decide(packet, public_map)
        if packet.self_state.role != "CREWMATE":
            return fsm_intent
        memory = self._inner.memory
        chosen = fsm_intent
        distribution: Mapping[str, float] | None = None
        if self._policy is not None:
            frame = self._policy.evaluate(
                packet,
                public_map,
                memory,
                fsm_intent=fsm_intent,
                emergency_uses_remaining=self._emergency_uses_remaining,
            )
            chosen = frame.intent
            if chosen != fsm_intent:
                # Validate OVERRIDES only: the FSM's own proposal is production
                # behavior (an uninterposed game submits it with no mask), and
                # the menu is submission-legal by construction — this is the
                # fail-loud backstop for a drifted menu, riding the 15.16
                # emergency canonicalization for the reason-stamped press.
                mask = build_action_mask(
                    packet,
                    public_map,
                    sabotage_kinds=self._sabotage_kinds,
                    emergency_uses_remaining=self._emergency_uses_remaining,
                )
                # The widened basis's ``nearest_task`` override submits a
                # ``do_task`` for an owned task the mask never enumerates (it
                # only knows ``pending_task_id``); the engine accepts it, so the
                # wrapper accepts it through the Task 15.22 legality mirror. A
                # genuinely off-vocabulary override fails both and raises.
                if not mask.is_submission_legal(
                    chosen
                ) and not _owned_task_do_task_is_submission_legal(
                    chosen, packet=packet, public_map=public_map
                ):
                    raise ValueError(
                        f"crew candidate returned a non-submission-legal intent "
                        f"{chosen!r} for {packet.agent_id!r} at tick {packet.tick}"
                    )
            if self._trace is not None:
                distribution = self._policy.choice_distribution(
                    packet,
                    public_map,
                    memory,
                    fsm_intent=fsm_intent,
                    emergency_uses_remaining=self._emergency_uses_remaining,
                )
        if self._trace is not None:
            self._trace.record(
                fsm_intent=fsm_intent, chosen=chosen, distribution=distribution
            )
        if self._diagnostic is not None:
            self._diagnostic.record(packet, memory, self._roles)
        return chosen

    def note_meeting_concluded(
        self,
        *,
        end_tick: int,
        dead_ids: tuple[PlayerId, ...],
        emergency_caller_id: PlayerId | None,
    ) -> None:
        """Track this agent's own spent emergency use, then delegate verbatim.

        Explicitly overridden (rather than delegated via ``__getattr__``) so
        the mask's ``emergency_uses_remaining`` tracker stays in lockstep with
        the engine's per-player counter — the ``_InterposedAgent`` precedent.
        The inner agent's own bookkeeping (its ``EmergencyPacingTracker`` +
        memory) still runs; this forwards verbatim.
        """

        if emergency_caller_id == self._agent_id:
            self._emergency_uses_remaining = max(0, self._emergency_uses_remaining - 1)
        self._inner.note_meeting_concluded(
            end_tick=end_tick,
            dead_ids=dead_ids,
            emergency_caller_id=emergency_caller_id,
        )

    def __getattr__(self, name: str) -> object:
        # Delegate the MeetingAwareAgent protocol + belief-fold hooks to the
        # inner TacticalAgent (the 15.8/15.10/15.15 wrapper idiom).
        return getattr(self._inner, name)


def build_crew_candidate_factory(
    policy: CrewTrackPolicy | None,
    *,
    game_map: Map,
    trace: CrewDecisionTrace | None = None,
    diagnostic: CoverageCueDiagnostic | None = None,
) -> AgentFactory:
    """The crew candidate's OWN policy factory (Task 15.16).

    The factory the leak-test factory mode and the crew eval rollouts run
    through: every agent is a real role-appropriate
    :class:`~orchestrator.game.TacticalAgent`, ALL of them wrapped in
    :class:`_CrewCandidateAgent` so the candidate's featurizer + head actually
    run on every crew decision while impostors stay the frozen scripted FSM.
    The factory records the roster it constructs (engine-truth roles) for the
    Q6 diagnostic ONLY — the mapping never reaches a policy input.
    """

    sabotage_kinds = tuple(sorted(game_map.sabotages))
    emergency_uses = game_map.emergency.uses_per_player
    roles: dict[PlayerId, Role] = {}

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        roles[agent_id] = role
        policy_impl: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy_impl = ImpostorPolicy(agent_id=agent_id)
        else:
            policy_impl = CrewmatePolicy(agent_id=agent_id)
        inner = TacticalAgent(agent_id=agent_id, policy=policy_impl, role=role)
        return _CrewCandidateAgent(
            inner,
            policy=policy,
            sabotage_kinds=sabotage_kinds,
            emergency_uses_per_player=emergency_uses,
            trace=trace,
            diagnostic=diagnostic,
            roles=roles,
        )

    return factory


def rollout_crew_candidate(
    policy: CrewTrackPolicy | None,
    seed: int,
    *,
    output_dir: Path,
    game_map: Map | None = None,
    num_players: int = BAKEOFF_NUM_PLAYERS,
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS,
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE,
    meeting_runner_factory: MeetingRunnerFactory | None = None,
    max_ticks: int = DEFAULT_MAX_TICKS,
    trace: CrewDecisionTrace | None = None,
    diagnostic: CoverageCueDiagnostic | None = None,
) -> EpisodeRollout:
    """Run ONE full production game with the crew candidate and reconstruct it.

    The crew twin of ``training.bakeoff.harness.rollout_candidate`` (which is
    consumed read-only and interposes impostor decisions only): the single
    rollout path the crew entrant trains through and the crew eval protocol
    scores through. Drives :class:`orchestrator.game.HeadlessGame` through the
    candidate's own factory, writes ``replay-seed-{seed}.jsonl`` under
    ``output_dir``, and returns the state-hash-verified typed episode.
    ``meeting_runner_factory=None`` is the real (deterministic fake-provider)
    meeting path.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    output_dir.mkdir(parents=True, exist_ok=True)
    replay_path = output_dir / f"replay-seed-{seed}.jsonl"
    factory = build_crew_candidate_factory(
        policy, game_map=resolved_map, trace=trace, diagnostic=diagnostic
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


def crew_inner_episode_fitness(
    rollout: EpisodeRollout,
    trace: CrewDecisionTrace,
    *,
    anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT,
    conviction: ConvictionFitnessTerm | None = None,
) -> float:
    """The per-episode crew inner fitness the ES entrant optimizes (15.16).

    The tactically-reachable crew terms + potential shaping
    (:func:`training.rewards.compute_shaped_reward` with side ``"CREWMATE"`` —
    task progress, survival, correctly-routed reports, the engine-truth
    ``patrol_coverage`` proxy, the terminal win), MINUS the anchor penalty
    toward the frozen crew FSM (``anchor_weight`` × the episode's mean anchor
    cross-entropy) — the same shape as 15.15's ``inner_episode_fitness`` with
    the side flipped — PLUS, under a GO verdict only, the 18.16 conviction term
    (``conviction.weight`` × the episode's mean predicted supply).

    The validity gate and the referee are NEVER terms here — they are selection
    filters :func:`evaluate_crew_candidate` applies after training. The
    conviction term IS a term, and a legitimate one: it is a REWARD-side
    prediction from FENCED pre-meeting tactical facts (the frozen Task-18.15
    artifact, sha-keyed, metered by its own
    :class:`~training.conviction.model.ConvictionUseCounter`, shipped ONLY under
    the committed GO verdict); it never reads, wraps, or re-derives
    ``eval/watchability.py`` scores (the designer ruling in
    tasks/phase-18.md:81-84), and under NO-GO it is STRUCTURALLY ABSENT
    (``conviction=None``; no zero-weighted ghost). It is the SAME frozen artifact
    and the SAME shared
    :class:`~training.bakeoff.harness.ConvictionFitnessTerm` object used on the
    impostor side — pass the SAME object to both sides. A truncated episode
    scores the documented
    :data:`~training.bakeoff.harness.TRUNCATED_EPISODE_FITNESS`.
    """

    if not rollout.complete:
        return TRUNCATED_EPISODE_FITNESS
    shaped = compute_shaped_reward(rollout, "CREWMATE").total()
    fitness = shaped - anchor_weight * trace.mean_anchor_ce()
    if conviction is not None:
        fitness += conviction.weight * trace.mean_predicted_supply()
    return fitness


@dataclass(frozen=True)
class CrewEsConfig:
    """The crew-scorer+ES entrant budget (recorded verbatim in the report).

    ``max_ticks`` is the TRAINING episode budget: a training episode that has
    not terminated by then is truncated and scores the documented
    :data:`~training.bakeoff.harness.TRUNCATED_EPISODE_FITNESS` sentinel. The
    committed budgets cap it at :data:`TRAIN_MAX_TICKS` (the FO-8 spike
    precedent — the prior this track measures against trained under
    ``max_ticks=80``): without a cap the optimizer drifts into marathon
    survive-and-grind genomes whose games run to the 1000-tick production
    budget, 20-30× the scripted crew's game length — a wall-clock sink and a
    degenerate play shape. The EVAL protocol (:class:`CrewProtocolConfig`)
    keeps the production ``DEFAULT_MAX_TICKS``, so every reported metric is
    measured under the uncapped budget.
    """

    es: ESConfig
    anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE
    max_ticks: int = DEFAULT_MAX_TICKS


def crew_es_budget(
    budget: str, *, anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
) -> CrewEsConfig:
    """The two committed budgets: ``ci`` (seconds-scale) and ``full``.

    Mirrors the 15.15 utility-es budgets (the closest analog entrant): the
    full budget is 20 generations × 12 offspring, K-seed-averaged over the
    first 6 corpus TRAIN-split seeds. Both budgets cap TRAINING episodes at
    :data:`TRAIN_MAX_TICKS` (see :class:`CrewEsConfig` — the eval protocol
    keeps the production tick budget).
    """

    train_seeds = load_train_seeds()
    if budget == "ci":
        return CrewEsConfig(
            es=ESConfig(
                generations=1,
                population=2,
                sigma=0.3,
                seed=0,
                fitness_seeds=train_seeds[:1],
            ),
            anchor_weight=anchor_weight,
            max_ticks=TRAIN_MAX_TICKS,
        )
    if budget == "full":
        return CrewEsConfig(
            es=ESConfig(
                generations=20,
                population=12,
                sigma=0.3,
                seed=0,
                fitness_seeds=train_seeds[:6],
            ),
            anchor_weight=anchor_weight,
            max_ticks=TRAIN_MAX_TICKS,
        )
    raise ValueError(f"unknown budget {budget!r}; expected 'ci' or 'full'")


class CrewEsEntrant:
    """The crew track's single entrant: the option scorer + the shared ES core.

    Mirrors the 15.15 ``UtilityEsEntrant`` with the side flipped: no warm
    start (the crew option-feature genome shares no shape with any committed
    family), the ES core draws its own deterministic Gaussian init, and every
    generation's fitness is :func:`crew_inner_episode_fitness` K-seed-averaged
    through :func:`rollout_crew_candidate` — one runner, one fitness, no
    protocol drift. Satisfies the 15.15 ``BakeoffEntrant`` seam structurally
    (``name`` + ``train()``).

    The 18.16 conviction term stays ``conviction=None`` in this training loop:
    the campaign wires the live per-meeting serving path later — this task lands
    the SEAM (:func:`crew_inner_episode_fitness`'s optional term), not the live
    feature production.
    """

    def __init__(
        self,
        *,
        config: CrewEsConfig,
        game_map: Map | None = None,
        basis: OwnedTaskOptionBasis | None = None,
    ) -> None:
        self._config = config
        self._game_map = game_map if game_map is not None else load_canonical_map()
        # ``basis`` (Task 15.22) selects the widened option menu; the entrant
        # name, genome length, and reported encoder/feature-names all follow it.
        self._basis = basis

    @property
    def name(self) -> str:
        return (
            CREW_OWNED_TASKS_ENTRANT_NAME
            if self._basis is not None
            else CREW_ENTRANT_NAME
        )

    def _seed_fitness(self, genome: tuple[float, ...], seed: int) -> float:
        policy = CrewOptionScorer(
            weights=genome, game_map=self._game_map, basis=self._basis
        )
        trace = CrewDecisionTrace()
        with tempfile.TemporaryDirectory(prefix="ailibi-crew-es-") as tmp:
            rollout = rollout_crew_candidate(
                policy,
                seed,
                output_dir=Path(tmp),
                game_map=self._game_map,
                num_players=self._config.num_players,
                num_impostors=self._config.num_impostors,
                tasks_per_crewmate=self._config.tasks_per_crewmate,
                max_ticks=self._config.max_ticks,
                trace=trace,
            )
        return crew_inner_episode_fitness(
            rollout, trace, anchor_weight=self._config.anchor_weight
        )

    def train(self) -> TrainedCandidate:
        started = time.perf_counter()
        genome_length = (
            self._basis.genome_length()
            if self._basis is not None
            else crew_genome_length()
        )
        feature_names = list(
            self._basis.feature_names
            if self._basis is not None
            else CREW_OPTION_FEATURE_NAMES
        )
        fitness = k_seed_mean(self._seed_fitness, self._config.es.fitness_seeds)
        result = evolve(fitness, genome_length=genome_length, config=self._config.es)
        policy = CrewOptionScorer(
            weights=result.champion, game_map=self._game_map, basis=self._basis
        )
        return TrainedCandidate(
            entrant=self.name,
            policy=policy,
            weights=result.champion,
            config={
                "entrant": self.name,
                "anchor_weight": self._config.anchor_weight,
                "es": self._config.es.model_dump(mode="json"),
                "train_max_ticks": self._config.max_ticks,
                "feature_names": feature_names,
                "genome_length": genome_length,
                "encoder_version": policy.encoder_version,
            },
            train_wall_clock_s=time.perf_counter() - started,
            train_metadata={
                "warm_start_used": False,
                "es_digest": result.digest(),
                "num_evaluations": result.num_evaluations,
                "fitness_trace": [round(value, 4) for value in result.fitness_trace],
                "champion_fitness": round(result.champion_fitness, 4),
            },
        )


def fsm_baseline_candidate() -> TrainedCandidate:
    """The scripted-FSM crew baseline packaged for the fixed eval protocol.

    Zero weights (an empty genome — there is nothing learned to freeze), the
    delegate policy, zero train wall-clock. Its row is the FSM side of every
    scorer-vs-FSM delta the definition of done names.
    """

    return TrainedCandidate(
        entrant=CREW_FSM_BASELINE_NAME,
        policy=FsmCrewBaseline(),
        weights=(),
        config={
            "entrant": CREW_FSM_BASELINE_NAME,
            "encoder_version": FSM_BASELINE_ENCODER_VERSION,
            "note": "scripted CrewmatePolicy delegate — the anchor baseline row",
        },
        train_wall_clock_s=0.0,
        train_metadata={"warm_start_used": False},
    )


# --------------------------------------------------------------------------- #
# The fixed crew eval protocol (the 15.15 shape, surrogate column excluded).   #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CrewProtocolConfig:
    """The FIXED crew eval protocol (Task 15.16) — the 15.15 shape.

    Same frozen eval seed set (the corpus test split), same roster, same
    referee baseline, same determinism/leak seeds and repeat-N as the 15.15
    defaults. The 15.13 surrogate meeting path is deliberately NOT metered by
    this track (the committed staleness cap budgets the impostor bake-off +
    the Goodhart re-run); the row's surrogate columns are ``None`` for shape
    parity, never a silently-zero measurement.

    The 18.16 ``conviction_artifact_dir`` / ``conviction_weight`` fields stamp
    each row's conviction provenance metadata (mirroring the impostor
    ``BakeoffProtocolConfig``); the crew fitness COLUMNS stay anchor-composed
    until the live serving seam lands.
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
    max_ticks: int = DEFAULT_MAX_TICKS
    conviction_artifact_dir: Path = CONVICTION_ARTIFACT_DIR
    conviction_weight: float = DEFAULT_CONVICTION_WEIGHT


def default_crew_protocol_config() -> CrewProtocolConfig:
    """The committed fixed crew eval protocol (the full-run defaults)."""

    return CrewProtocolConfig(eval_seeds=load_eval_seeds())


class CrewRepeatSpread(BaseModel):
    """The N-repeat metric spread an experiment-tier crew row carries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    repeats: int
    inner_fitness_real: MetricSpread
    crew_win_rate: MetricSpread
    anchor_cross_entropy: MetricSpread


class CrewTrackResult(BaseModel):
    """One crew candidate's full metric tuple (Task 15.16 public row shape).

    One row per candidate in ``training/reports/results-crew-track.jsonl`` —
    the same tuple shape as 15.15's ``BakeoffResult`` (gate / referee /
    fitness-with-surrogate-columns / anchor-CE / determinism / leak /
    wall-clock / descriptor footprint), with the impostor metric block
    replaced by the crew block the definition of done names: win rate,
    survival, task-completion pace, and the mis-eject-relevant meeting
    metrics (meeting-trigger quality, correct-report rate, mis-eject rate),
    plus the Q6 coverage-cue diagnostic column. Surrogate columns are ``None``
    (this track does not meter the 15.13 staleness cap). Task 18.16 appends the
    conviction provenance triple: the weight is named under
    ``fitness_term == "ships"``; under ``"absent"`` the weight is None — the row
    says the term is structurally absent, never zero-weighted.
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

    crew_win_rate: float
    crew_survival_rate: float
    task_completion_final: float
    tasks_per_100_ticks: float
    meetings_total: int
    meetings_crew_triggered: int
    meeting_trigger_quality: float | None
    crew_report_meetings: int
    correct_report_meetings: int
    correct_report_rate: float | None
    crew_ejections: int
    impostor_ejections: int
    mis_eject_rate: float | None

    coverage_cue: CoverageCueRow

    determinism: DeterminismRow
    repeat_spread: CrewRepeatSpread | None

    leak_test_passed: bool
    leak_packets_scanned: int | None
    leak_failure: str | None

    surrogate_uses_training: int
    surrogate_uses_eval: int
    wall_clock_train_s: float
    wall_clock_eval_s: float

    descriptor_footprint: Mapping[str, float]
    train_metadata: Mapping[str, object]

    # Task 18.16 conviction provenance (OPTIONAL, None-default — pre-18.16
    # serialized rows must still validate). ``conviction_weight`` is named only
    # under "ships"; under "absent" it is None — the row says the term is
    # structurally absent, never zero-weighted.
    conviction_fitness_term: Literal["ships", "absent"] | None = None
    conviction_weight: float | None = None
    conviction_weights_sha256: str | None = None

    def to_json_line(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True)


@dataclass(frozen=True)
class _CrewEvalPass:
    """One scoring pass of a crew candidate over the eval seed set."""

    inner_fitness: float
    mean_shaped_reward: float | None
    truncated_episodes: int
    win_rate: float
    survival_rate: float
    task_completion_final: float
    tasks_per_100_ticks: float
    meetings_total: int
    meetings_crew_triggered: int
    meetings_crew_triggered_impostor_ejected: int
    crew_report_meetings: int
    correct_report_meetings: int
    crew_ejections: int
    impostor_ejections: int
    trace: CrewDecisionTrace
    diagnostic: CoverageCueDiagnostic
    descriptor_mean: dict[str, float]


def _score_crew_eval_pass(
    policy: CrewTrackPolicy,
    *,
    protocol: CrewProtocolConfig,
    game_map: Map,
    output_dir: Path,
) -> _CrewEvalPass:
    trace = CrewDecisionTrace()
    diagnostic = CoverageCueDiagnostic()
    fitnesses: list[float] = []
    shaped_totals: list[float] = []
    truncated = 0
    wins = 0
    survival_sum = 0.0
    completion_sum = 0.0
    pace_sum = 0.0
    meetings_total = 0
    crew_triggered = 0
    crew_triggered_impostor_ejected = 0
    crew_report_meetings = 0
    correct_report_meetings = 0
    crew_ejections = 0
    impostor_ejections = 0
    descriptor_sums = [0.0] * len(DESCRIPTOR_VECTOR_FIELDS)
    initial_crew = max(1, protocol.num_players - protocol.num_impostors)
    for seed in protocol.eval_seeds:
        episode_trace = CrewDecisionTrace()
        rollout = rollout_crew_candidate(
            policy,
            seed,
            output_dir=output_dir,
            game_map=game_map,
            num_players=protocol.num_players,
            num_impostors=protocol.num_impostors,
            tasks_per_crewmate=protocol.tasks_per_crewmate,
            max_ticks=protocol.max_ticks,
            trace=episode_trace,
            diagnostic=diagnostic,
        )
        fitnesses.append(
            crew_inner_episode_fitness(
                rollout, episode_trace, anchor_weight=protocol.anchor_penalty_weight
            )
        )
        if rollout.complete:
            shaped_totals.append(compute_shaped_reward(rollout, "CREWMATE").total())
        else:
            truncated += 1
        if rollout.winner == "CREWMATES":
            wins += 1
        last = rollout.frames[-1]
        survival_sum += last.alive_crew / initial_crew
        completion_sum += last.tasks_completed / max(1, last.tasks_total)
        pace_sum += 100.0 * last.tasks_completed / max(1, rollout.final_tick)
        for meeting in rollout.meetings:
            meetings_total += 1
            ejected = meeting.ejected_player_id
            ejected_role = rollout.roles.get(ejected) if ejected is not None else None
            if ejected_role == "CREWMATE":
                crew_ejections += 1
            elif ejected_role == "IMPOSTOR":
                impostor_ejections += 1
            if rollout.roles.get(meeting.triggered_by) != "CREWMATE":
                continue
            crew_triggered += 1
            if ejected_role == "IMPOSTOR":
                crew_triggered_impostor_ejected += 1
            if meeting.trigger == "report":
                crew_report_meetings += 1
                if ejected_role == "IMPOSTOR":
                    correct_report_meetings += 1
        vector = rollout.descriptors.vector()
        for index in range(len(DESCRIPTOR_VECTOR_FIELDS)):
            descriptor_sums[index] += float(vector[index])
        trace.fold(episode_trace)
    games = len(protocol.eval_seeds)
    descriptor_mean = {
        name: descriptor_sums[index] / games
        for index, name in enumerate(DESCRIPTOR_VECTOR_FIELDS)
    }
    return _CrewEvalPass(
        inner_fitness=math.fsum(fitnesses) / games,
        mean_shaped_reward=(
            math.fsum(shaped_totals) / len(shaped_totals) if shaped_totals else None
        ),
        truncated_episodes=truncated,
        win_rate=wins / games,
        survival_rate=survival_sum / games,
        task_completion_final=completion_sum / games,
        tasks_per_100_ticks=pace_sum / games,
        meetings_total=meetings_total,
        meetings_crew_triggered=crew_triggered,
        meetings_crew_triggered_impostor_ejected=crew_triggered_impostor_ejected,
        crew_report_meetings=crew_report_meetings,
        correct_report_meetings=correct_report_meetings,
        crew_ejections=crew_ejections,
        impostor_ejections=impostor_ejections,
        trace=trace,
        diagnostic=diagnostic,
        descriptor_mean=descriptor_mean,
    )


def _write_roster_json(
    directory: Path, *, num_players: int, num_impostors: int, tasks_per_crewmate: int
) -> None:
    # The referee/gate readers expect the recorded roster next to the replays
    # (the 15.15 harness writes the same three fields; mirrored here because
    # the harness helper is private and the harness is read-only for 15.16).
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
    # ``replay-seed-*`` glob would trip on it (the 15.14/15.15 precedent).
    for sidecar in directory.glob("*.audit.jsonl"):
        sidecar.unlink()


def evaluate_crew_candidate(
    candidate: TrainedCandidate,
    protocol: CrewProtocolConfig,
    *,
    artifact_root: Path = _ARTIFACT_ROOT,
    game_map: Map | None = None,
) -> CrewTrackResult:
    """Score one crew candidate through the full fixed protocol (Task 15.16).

    The 15.15 ``evaluate_candidate`` shape with the crew metric block: the
    real (fake-provider) pass on the fixed eval seed set, the 15.1 validity
    gate + the 15.2 referee as SELECTION columns (never fitness terms), the
    anchor cross-entropy against the documented ceiling (flagged, never
    dropped), the 15.10 determinism harness and the leak-test factory mode
    THROUGH THE CANDIDATE'S OWN crew factory, and wall-clock. A determinism
    FAIL demotes the row to ``tier="experiment"`` with the N-repeat spread —
    the row is never dropped. Every reported number is computed here and only
    here.
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    started = time.perf_counter()
    # The committed conviction verdict stamps the row's provenance metadata —
    # the crew-side twin of the impostor row's stamp (the crew fitness columns
    # stay anchor-composed until the live serving seam lands). Drift-checked
    # via the harness's bundle loader BEFORE any eval side effects: a stale or
    # partially-updated bundle fails the run loud, never lands in a row.
    conviction_verdict = load_conviction_row_provenance(
        protocol.conviction_artifact_dir
    )
    entrant_dir, weights_sha256 = write_candidate_artifact(candidate, artifact_root)

    policy = candidate.policy
    if not isinstance(policy, (CrewOptionScorer, FsmCrewBaseline)):
        raise ValueError(
            f"crew eval expects a crew-track policy, got {type(policy).__name__}"
        )

    with tempfile.TemporaryDirectory(prefix="ailibi-crew-eval-") as tmp:
        real_dir = Path(tmp) / "real"
        real_dir.mkdir()
        _write_roster_json(
            real_dir,
            num_players=protocol.num_players,
            num_impostors=protocol.num_impostors,
            tasks_per_crewmate=protocol.tasks_per_crewmate,
        )
        real_pass = _score_crew_eval_pass(
            policy,
            protocol=protocol,
            game_map=resolved_map,
            output_dir=real_dir,
        )
        _drop_audit_sidecars(real_dir)
        watchability: WatchabilityReport = compute_watchability(
            real_dir, baseline_id=protocol.baseline_id
        )
        validity = run_validity_gate(real_dir)

    determinism_report = run_policy_determinism(
        policy,
        seeds=protocol.determinism_seeds,
        game_map=resolved_map,
        num_players=protocol.num_players,
        num_impostors=protocol.num_impostors,
        tasks_per_crewmate=protocol.tasks_per_crewmate,
        max_ticks=protocol.max_ticks,
    )

    repeat_spread: CrewRepeatSpread | None = None
    tier: Literal["candidate", "experiment"] = "candidate"
    if not determinism_report.deterministic:
        tier = "experiment"
        fitness_values = [real_pass.inner_fitness]
        win_values = [real_pass.win_rate]
        ce_values = [real_pass.trace.mean_anchor_ce()]
        for _ in range(max(0, protocol.repeat_n - 1)):
            with tempfile.TemporaryDirectory(prefix="ailibi-crew-rep-") as tmp:
                repeat_pass = _score_crew_eval_pass(
                    policy,
                    protocol=protocol,
                    game_map=resolved_map,
                    output_dir=Path(tmp),
                )
            fitness_values.append(repeat_pass.inner_fitness)
            win_values.append(repeat_pass.win_rate)
            ce_values.append(repeat_pass.trace.mean_anchor_ce())
        repeat_spread = CrewRepeatSpread(
            repeats=len(fitness_values),
            inner_fitness_real=MetricSpread.from_values(fitness_values),
            crew_win_rate=MetricSpread.from_values(win_values),
            anchor_cross_entropy=MetricSpread.from_values(ce_values),
        )

    leak_passed = True
    leak_packets: int | None = None
    leak_failure: str | None = None
    leak_factory = build_crew_candidate_factory(policy, game_map=resolved_map)
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
        real_pass.trace.agreement_hits / real_pass.trace.crew_decisions
        if real_pass.trace.crew_decisions
        else None
    )
    floor_trips = sum(
        1 for game in watchability.per_game if game.floor_multiplier == 0.0
    )
    games_total = len(watchability.per_game)

    return CrewTrackResult(
        entrant=candidate.entrant,
        tier=tier,
        encoder_version=policy.encoder_version,
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
        inner_fitness_surrogate=None,
        truncated_episodes_surrogate=None,
        surrogate_real_divergence=None,
        anchor_cross_entropy=anchor_ce,
        anchor_ce_ceiling=protocol.anchor_ce_ceiling,
        anchor_ce_flagged=anchor_ce > protocol.anchor_ce_ceiling,
        anchor_offmenu_decisions=real_pass.trace.offmenu_decisions,
        fsm_intent_agreement=agreement,
        crew_win_rate=real_pass.win_rate,
        crew_survival_rate=real_pass.survival_rate,
        task_completion_final=real_pass.task_completion_final,
        tasks_per_100_ticks=real_pass.tasks_per_100_ticks,
        meetings_total=real_pass.meetings_total,
        meetings_crew_triggered=real_pass.meetings_crew_triggered,
        meeting_trigger_quality=(
            real_pass.meetings_crew_triggered_impostor_ejected
            / real_pass.meetings_crew_triggered
            if real_pass.meetings_crew_triggered
            else None
        ),
        crew_report_meetings=real_pass.crew_report_meetings,
        correct_report_meetings=real_pass.correct_report_meetings,
        correct_report_rate=(
            real_pass.correct_report_meetings / real_pass.crew_report_meetings
            if real_pass.crew_report_meetings
            else None
        ),
        crew_ejections=real_pass.crew_ejections,
        impostor_ejections=real_pass.impostor_ejections,
        mis_eject_rate=(
            real_pass.crew_ejections / real_pass.meetings_total
            if real_pass.meetings_total
            else None
        ),
        coverage_cue=real_pass.diagnostic.to_row(),
        determinism=DeterminismRow.from_report(determinism_report),
        repeat_spread=repeat_spread,
        leak_test_passed=leak_passed,
        leak_packets_scanned=leak_packets,
        leak_failure=leak_failure,
        surrogate_uses_training=candidate.surrogate_uses_training,
        surrogate_uses_eval=0,
        wall_clock_train_s=candidate.train_wall_clock_s,
        wall_clock_eval_s=time.perf_counter() - started,
        descriptor_footprint=real_pass.descriptor_mean,
        train_metadata=candidate.train_metadata,
        conviction_fitness_term=conviction_verdict.fitness_term,
        conviction_weight=(
            protocol.conviction_weight
            if conviction_verdict.fitness_term == "ships"
            else None
        ),
        conviction_weights_sha256=conviction_verdict.weights_sha256,
    )


def write_crew_results_jsonl(results: Sequence[CrewTrackResult], path: Path) -> None:
    """Emit the machine-readable per-candidate rows the pause consumes."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(result.to_json_line() + "\n" for result in results))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m training.crew.scorer",
        description="The Task 15.16 crew track: train + evaluate the crew scorer.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser(
        "run",
        help="Train the crew scorer, evaluate it + the FSM baseline, write jsonl.",
    )
    run_parser.add_argument("--budget", choices=("ci", "full"), default="full")
    run_parser.add_argument(
        "--basis",
        choices=("pending", "owned-tasks"),
        default="pending",
        help=(
            "Option basis: 'pending' is the 15.16 menu; 'owned-tasks' is the "
            "Task 15.22 widened basis over SelfView.owned_task_ids."
        ),
    )
    run_parser.add_argument(
        "--results",
        type=Path,
        default=None,
        help="Output jsonl path (defaults per --basis).",
    )
    run_parser.add_argument(
        "--artifacts", type=Path, default=_ARTIFACT_ROOT, help="Artifact root dir."
    )
    args = parser.parse_args(argv)

    # The widened basis (Task 15.22) selects the owned-task menu, the
    # crew-owned-tasks entrant name, and — unless overridden — its own jsonl.
    basis = OwnedTaskOptionBasis() if args.basis == "owned-tasks" else None
    results_path: Path = args.results
    if results_path is None:
        results_path = (
            _OWNED_TASK_RESULTS_JSONL_PATH if basis is not None else _RESULTS_JSONL_PATH
        )

    protocol = default_crew_protocol_config()
    entrant = CrewEsEntrant(config=crew_es_budget(args.budget), basis=basis)
    candidates = [fsm_baseline_candidate(), entrant.train()]
    results = [
        evaluate_crew_candidate(candidate, protocol, artifact_root=args.artifacts)
        for candidate in candidates
    ]
    write_crew_results_jsonl(results, results_path)
    for result in results:
        print(result.to_json_line())
    return 0


__all__ = [
    "CREW_ENTRANT_NAME",
    "CREW_OWNED_TASKS_ENTRANT_NAME",
    "OWNED_TASK_ENCODER_VERSION",
    "TRAIN_MAX_TICKS",
    "CREW_FSM_BASELINE_NAME",
    "ENCODER_VERSION",
    "FO8_PRIOR_FSM_WINS",
    "FO8_PRIOR_LEARNED_WINS",
    "FO8_PRIOR_SEEDS",
    "FSM_BASELINE_ENCODER_VERSION",
    "CoverageCueDiagnostic",
    "CoverageCueRow",
    "CrewDecisionTrace",
    "CrewEsConfig",
    "CrewEsEntrant",
    "CrewOptionScorer",
    "CrewProtocolConfig",
    "CrewRepeatSpread",
    "CrewTrackPolicy",
    "CrewTrackResult",
    "FsmCrewBaseline",
    "build_crew_candidate_factory",
    "build_crew_scorer",
    "crew_es_budget",
    "crew_inner_episode_fitness",
    "default_crew_protocol_config",
    "evaluate_crew_candidate",
    "fsm_baseline_candidate",
    "main",
    "rollout_crew_candidate",
    "write_crew_results_jsonl",
]


if __name__ == "__main__":
    raise SystemExit(main())
