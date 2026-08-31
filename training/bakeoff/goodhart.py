"""Adversarial Goodhart probe — red-team the Task 15.2 selection referee (Task 15.14).

Before the mid-phase pause is allowed to use the committed referee
(:func:`eval.watchability.compute_watchability`, with the pinned selection
baseline's floors — baseline-5 since Task 17.11; the original 15.14 attack ran
on the baseline-3 floors from 15.7) as a champion-selection GATE, this probe
attacks it: it runs the shared ES
core (:mod:`training.bakeoff.es`) DIRECTLY on the referee score — the
deliberately-forbidden objective (``eval/watchability.py`` SELECTION-ONLY DOCTRINE)
— and reports what a tactical genome can extract.

WHAT IS OPTIMIZED. The fitness is the full COMPOSED referee over a fixed replay
SET generated on the training env (:class:`training.env.TacticalRolloutEnv`) with
fake-provider meetings (:func:`_composed_referee_fitness`): when the HARD validity
gate (:func:`eval.validity.run_validity_gate`) — the ONLY constraint — passes,
``mean_score`` (the D1-D4 floor-gated geomean, averaged over the K fitness seeds)
PLUS a dominating bonus iff the whole referee passes (``referee_passed`` = the
set-level evidence-supply floors AND integrity). So the ES targets the full
champion-selection referee, not the Layer-2 geomean alone — a genome that CLEARS
the gate outranks any geomean-only candidate — with the geomean as the tie-break
among the genomes that fail the gate. Under fake meetings the supply floors never
clear, so the bonus is 0 for every genome and the fitness equals ``mean_score``;
the composition is what makes the surrogate-path re-run (Task 15.15, where the
floors CAN clear) hunt for a genome that actually launders past the gate.
Averaging over the K seeds is the ES core's K-seed averaging done set-level by the
referee's own per-game mean (equivalent to
:func:`training.bakeoff.es.k_seed_mean` over the per-game scores).

THE ATTACK SURFACE (the implementation hint). FO-3
(``experiments/lab/ml_spike/fo3_rubric_goodhart.py``) already showed tactical play
cannot move the meeting-CONTROLLED rubric terms under fake meetings (D2
separation/conversion, D3 deflection are decided inside the meeting). So the
genome drives the IMPOSTOR side only (crew stays the scripted FSM — the 15.15
threat model the referee will actually gate) over a small, legality-validated
tactic menu whose reachable levers are: **meeting-farming** (impostor-called
emergency / body-report meetings inflate the D4 contest term
``min(1, (n-1)/2)``), **stall-to-clock** (WAIT to bend the D1 resolution term),
and raw kill/sabotage aggression (which moves the witnessed-kill supply gauge).
Every selected intent is validated against the env's legal-action mask, so the
genome is structurally unable to emit an illegal or off-menu action. A null result
on the meeting-DEPENDENT terms is EXPECTED and is reported WITH the surrogate-path
caveat, never as "referee safe".

THE VERDICT. Every improvement in the ES fitness trace is decomposed to the
moving D-term / floor — or to the referee-gate flip itself when the gain is the
composed-referee pass bonus — with its behavioral cause named (no undecomposed
gains). The
report ends HELD (no exploit clears the stated materiality bar) or EXPLOITS-FOUND
(each with trajectory evidence + a recommended floor routed to the PAUSE — this
task NEVER edits the referee it attacks), and always states the 15.15
surrogate-path re-run obligation.

THE 18.18 CONVICTION-PATH ARMS. The training-signal role grew at Task 18.16
(the GO-shipped conviction fitness term + the referee pre-screen), so the probe
re-runs BEFORE any campaign selection leans on the new signal — the standing
rule. :func:`run_conviction_path_probe` wraps the UNCHANGED standing probe and
asks the narrow new question: does the conviction TERM — a PREDICTION of
evidence supply — diverge from the recorded REALITY (flags in bytes) under the
adversarial levers, and by how much. Per forced lever (plus the scripted-FSM
baseline and the ES champion corner) the arms re-roll the same K seeds (the env
is a pure function of the seed, so the bytes are identical to the set the
standing bars scored), read predicted-vs-actual side by side off the conviction
table's mirrored labels, price the term's fitness contribution exactly as
``inner_episode_fitness`` composes it, and run the COMMITTED 18.16 pre-screen
(``training.bakeoff.harness.conviction_prescreen`` — the real instrument, never
a mirror) beside the recorded supply floors: the composed-gate laundering
check. Every prediction is metered through the ONE shared sha-keyed
:class:`~training.conviction.model.ConvictionUseCounter` (the 18.16 threading
discipline) and the report quotes the consumption. The carried 4p1i
``d4-contest-farming`` exploit (audits/audit-phase-17-close.md §6: +61.8% on
the reference roster — re-probe before any 4p1i-scored selection) is re-read at
the current substrate by :func:`reread_carried_4p1i_exploit`. The probed
modules (``training/conviction/``, ``training/bakeoff/harness.py``) are
consumed through their public seams, never edited; every above-bar finding is a
NAMED blocker for the 18.24 protocol, never a silent caveat.
"""

from __future__ import annotations

import json
import math
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict

from agents.tactical.features import mlp_forward, mlp_genome_length
from eval.validity import run_validity_gate
from eval.watchability import (
    WatchabilityGameScore,
    WatchabilityReport,
    compute_watchability,
)
from observation.action_intent import (
    ActionIntent,
    EmergencyMeetingIntent,
    KillIntent,
    ReportBodyIntent,
    SabotageIntent,
    WaitIntent,
)
from orchestrator.game import MeetingRunner
from training.bakeoff.es import ESConfig, ESResult, evolve
from training.conviction.dataset import build_conviction_table
from training.conviction.fidelity import CONVICTION_CONVERSION_DECISION_THRESHOLD
from training.conviction.model import ConvictionUseCounter
from training.env import IntentSelector, MaskedDecision, TacticalRolloutEnv

if TYPE_CHECKING:
    # Type-only: at runtime the harness imports THIS module at module scope, so
    # the committed 18.16 integration is consumed through function-local
    # imports (see run_conviction_path_probe) — the _build_entrants
    # acyclic-graph precedent.
    from training.bakeoff.harness import ConvictionFitnessTerm

# A factory for the meeting runner the probe scores under. ``None`` (the default)
# is the env's fake-provider runner (this task's scoping). Task 15.15 threads the
# 15.13 learned surrogate factory through here to discharge the re-run obligation
# via THIS probe path — no duplicate evaluator.
MeetingRunnerFactory: TypeAlias = Callable[[], MeetingRunner]

# --------------------------------------------------------------------------- #
# The packet-only genome policy: features -> tactic MLP -> a legal intent.      #
# --------------------------------------------------------------------------- #

# The reachable tactic menu the genome ranks. "fsm" delegates to the scripted
# proposal; the rest are the physically-reachable Goodhart levers (meeting-farming
# via emergency/report, stall via wait, aggression via kill/sabotage). The order
# is fixed so a logit-tie breaks on this index deterministically.
_TACTICS: Final[tuple[str, ...]] = (
    "fsm",
    "emergency",
    "report",
    "wait",
    "kill",
    "sabotage",
)
_TACTIC_TYPES: Final[dict[str, type[ActionIntent]]] = {
    "emergency": EmergencyMeetingIntent,
    "report": ReportBodyIntent,
    "wait": WaitIntent,
    "kill": KillIntent,
    "sabotage": SabotageIntent,
}
# One hidden layer; small on purpose — the probe is cheap insurance, not an
# exhaustive search, and a small head keeps the genome (and the ES budget) honest.
_HIDDEN: Final[int] = 4
_FEATURE_DIM: Final[int] = 8


def probe_genome_length() -> int:
    """The flat genome length for the probe's packet-only tactic MLP."""

    return mlp_genome_length(
        input_dim=_FEATURE_DIM, hidden=_HIDDEN, output=len(_TACTICS)
    )


def _packet_features(decision: MaskedDecision) -> tuple[float, ...]:
    """A compact, deterministic packet-only feature vector (no memory).

    The ``training.env`` IntentSelector seam is packet-only (it cannot reach the
    inner agent's memory — that is the 15.10 determinism-harness seam), so the
    probe reads scalars straight off the observation packet. Bounded / normalized
    so the ``tanh`` MLP sees inputs in a stable range.
    """

    packet = decision.packet
    self_state = packet.self_state
    cooldown = packet.cooldown if packet.cooldown is not None else 0
    return (
        1.0,
        min(cooldown, 10) / 10.0,
        1.0 if self_state.in_vent else 0.0,
        len(packet.visible_players) / 8.0,
        len(packet.visible_bodies) / 2.0,
        min(packet.tick, 200) / 200.0,
        1.0 if packet.global_state.sabotage_active else 0.0,
        1.0 if self_state.pending_task_id is not None else 0.0,
    )


def _first_legal_of_type(
    decision: MaskedDecision, intent_type: type[ActionIntent]
) -> ActionIntent | None:
    """The first submission-legal intent of ``intent_type`` (mask menu order)."""

    for intent in decision.mask.submission_legal:
        if isinstance(intent, intent_type):
            return intent
    return None


def _legal_wait(decision: MaskedDecision) -> ActionIntent:
    """A guaranteed-legal WAIT (always in the engine-legal set for a live actor)."""

    wait = _first_legal_of_type(decision, WaitIntent)
    if wait is not None:
        return wait
    return WaitIntent(actor=decision.packet.agent_id, type="wait")


def _fsm_or_legal(decision: MaskedDecision) -> ActionIntent:
    """Return the FSM's proposal, repaired to a mask-legal intent.

    The env validates every returned intent against the mask, but the mask
    reconstructs an :class:`EmergencyMeetingIntent` with ``reason=None`` while the
    scripted FSM proposes one with a ``reason`` payload — so the FSM's own
    emergency is not ``is_submission_legal``. Rather than DROP the FSM's meeting
    intent (which would understate the scripted baseline's meeting cadence), we
    substitute the mask's legal reason-less emergency; anything else illegal
    (never expected from the scripted FSM) falls back to WAIT.
    """

    fsm_intent = decision.fsm_intent
    if decision.mask.is_submission_legal(fsm_intent):
        return fsm_intent
    if isinstance(fsm_intent, EmergencyMeetingIntent):
        emergency = _first_legal_of_type(decision, EmergencyMeetingIntent)
        if emergency is not None:
            return emergency
    return _legal_wait(decision)


def build_probe_selector(genome: Sequence[float]) -> IntentSelector:
    """Build the IntentSelector for one genome (impostor-side tactic policy).

    Crew delegates to the scripted FSM (the 15.15 threat model: the referee gates
    an impostor champion against frozen crew). For the impostor, the genome's MLP
    ranks the tactic menu; the highest-ranked tactic whose concrete intent is
    submission-legal at this tick wins, falling back down the ranking and finally
    to WAIT — so the returned intent is ALWAYS legal.
    """

    genome_tuple = tuple(float(gene) for gene in genome)

    def select(decision: MaskedDecision) -> ActionIntent:
        if decision.packet.self_state.role != "IMPOSTOR":
            return _fsm_or_legal(decision)
        logits = mlp_forward(
            genome_tuple,
            _packet_features(decision),
            input_dim=_FEATURE_DIM,
            hidden=_HIDDEN,
            output=len(_TACTICS),
        )
        order = sorted(range(len(_TACTICS)), key=lambda k: (-logits[k], k))
        for k in order:
            tactic = _TACTICS[k]
            if tactic == "fsm":
                return _fsm_or_legal(decision)
            intent = _first_legal_of_type(decision, _TACTIC_TYPES[tactic])
            if intent is not None:
                return intent
        return _legal_wait(decision)

    return select


# The single-tactic levers the reachability sweep forces (every menu entry except
# the FSM delegate — those are the physically-reachable degenerate corners a
# random-init ES may not stumble into within a bounded budget).
_SWEEP_TACTICS: Final[tuple[str, ...]] = tuple(t for t in _TACTICS if t != "fsm")
# The output bias magnitude that makes one tactic dominate the MLP ranking (so the
# forced genome always plays that tactic when it is legal). A flat genome with one
# large output bias — the corner of genome space that single lever occupies.
_FORCE_BIAS: Final[float] = 100.0


def _forced_genome(tactic: str) -> tuple[float, ...]:
    """A genome that ranks ``tactic`` first whenever it is legal (a lever corner)."""

    length = probe_genome_length()
    output = len(_TACTICS)
    genome = [0.0] * length
    genome[length - output + _TACTICS.index(tactic)] = _FORCE_BIAS
    return tuple(genome)


# --------------------------------------------------------------------------- #
# The referee+validity set evaluation (the fitness under attack).              #
# --------------------------------------------------------------------------- #

# The fitness a validity-failing set is scored at — below any real geomean so the
# ES abandons invalid sets (the validity gate is the only constraint). A genome
# that scored HIGH here would itself be an exploit (laundering an invalid set);
# the referee's own integrity floor already zeroes non-reconstructing sets.
_INVALID_FITNESS: Final[float] = -1.0

# The bonus added when a set clears the COMPOSED referee (referee_passed = the
# supply-floor gate AND integrity). Larger than any attainable geomean (score is
# capped at 100), so the ES optimizes the FULL champion-selection referee, not the
# Layer-2 geomean alone: a genome that PASSES the gate is preferred over ANY
# geomean-only candidate, and the geomean is only the tie-break among the
# (many) genomes that fail the gate. Under fake meetings the meeting-driven supply
# floors are un-clearable, so this bonus is 0 for every genome and the fitness
# degrades to mean_score — but the objective is now faithfully the composed
# referee, so a surrogate-path re-run (where the floors CAN clear) will prefer a
# lower-geomean champion that actually launders past the gate.
_REFEREE_PASS_BONUS: Final[float] = 1000.0


def _composed_referee_fitness(
    watchability: WatchabilityReport, validity_passed: bool
) -> float:
    """The fitness under attack — the COMPOSED referee, validity-gated.

    ``_INVALID_FITNESS`` when the only constraint (the HARD validity gate) fails;
    otherwise ``mean_score`` PLUS ``_REFEREE_PASS_BONUS`` iff the whole referee
    passes (supply-floor gate AND integrity). So the ES targets the full
    champion-selection referee — a genome that CLEARS the gate outranks any
    geomean-only candidate — with the geomean as the tie-break among the genomes
    that fail the gate. Under fake meetings the gate never clears, so this equals
    ``mean_score`` for every genome (today's report is unchanged); the composition
    matters once the surrogate opens the meeting-driven floors at Task 15.15.
    """

    if not validity_passed:
        return _INVALID_FITNESS
    bonus = _REFEREE_PASS_BONUS if watchability.referee_passed else 0.0
    return watchability.mean_score + bonus


@dataclass(frozen=True)
class _SetEvaluation:
    """The full referee + validity verdict over one genome's replay set."""

    fitness: float
    watchability: WatchabilityReport
    validity_passed: bool


@dataclass(frozen=True)
class _SetAggregates:
    """Set-level means of the referee's per-game terms (decomposition inputs)."""

    mean_score: float
    mean_d1: float
    mean_d2: float
    mean_d3: float
    mean_d4: float
    mean_d2_separation: float
    mean_d2_conversion: float
    mean_d4_arc: float
    mean_d4_swing: float
    mean_d4_contest: float
    mean_meetings: float
    floor_trip_rate: float


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values) if values else 0.0


def _aggregate(games: Sequence[WatchabilityGameScore]) -> _SetAggregates:
    if not games:
        return _SetAggregates(*([0.0] * 12))
    return _SetAggregates(
        mean_score=_mean([g.score for g in games]),
        mean_d1=_mean([g.d1_resolution for g in games]),
        mean_d2=_mean([g.d2_deduction for g in games]),
        mean_d3=_mean([g.d3_craft for g in games]),
        mean_d4=_mean([g.d4_arc for g in games]),
        mean_d2_separation=_mean([g.d2_separation_norm for g in games]),
        mean_d2_conversion=_mean([g.d2_conversion for g in games]),
        mean_d4_arc=_mean([g.d4_arc_term for g in games]),
        mean_d4_swing=_mean([g.d4_swing_term for g in games]),
        mean_d4_contest=_mean([g.d4_contest_term for g in games]),
        mean_meetings=_mean([float(g.n_meetings) for g in games]),
        floor_trip_rate=_mean(
            [1.0 if g.floor_multiplier == 0.0 else 0.0 for g in games]
        ),
    )


class _RefereeAttackEvaluator:
    """Rolls out a genome's replay set and scores it through referee + validity.

    Caches by genome so the ES core's champion trace can be re-decomposed after
    the run without regenerating games. The env writes a ``.audit.jsonl`` sidecar
    and needs a ``roster.json`` descriptor for the referee's re-seed — both handled
    here so the scoring dir is exactly what the committed-bytes referee consumes.
    """

    def __init__(
        self,
        *,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        fitness_seeds: Sequence[int],
        baseline_id: str,
        meeting_runner_factory: MeetingRunnerFactory | None = None,
    ) -> None:
        self._num_players = num_players
        self._num_impostors = num_impostors
        self._tasks_per_crewmate = tasks_per_crewmate
        self._seeds = tuple(fitness_seeds)
        # The env writes one replay-seed-{seed}.jsonl per rollout, so a duplicate
        # seed would OVERWRITE its earlier replay and the referee would score fewer
        # games than the stated K-seed budget. ESConfig already rejects duplicates;
        # this guards direct construction too (no silent budget shrink).
        if len(set(self._seeds)) != len(self._seeds):
            raise ValueError(
                f"fitness_seeds must be unique, got {self._seeds!r}: duplicate "
                "seeds overwrite each other's replays and silently shrink the "
                "scored set below the stated budget"
            )
        self._baseline_id = baseline_id
        # None => the env's fake-provider runner (this task). Task 15.15 passes the
        # 15.13 surrogate factory so the re-run opens the meeting-controlled terms.
        self._meeting_runner_factory = meeting_runner_factory
        self._cache: dict[tuple[float, ...], _SetEvaluation] = {}

    def _roster_json(self, directory: Path) -> None:
        (directory / "roster.json").write_text(
            json.dumps(
                {
                    "num_players": self._num_players,
                    "num_impostors": self._num_impostors,
                    "tasks_per_crewmate": self._tasks_per_crewmate,
                }
            )
        )

    def evaluate_set(self, genome: tuple[float, ...] | None) -> _SetEvaluation:
        """Score one genome's (or the scripted FSM's) replay set. ``None`` = FSM."""

        if genome is not None and genome in self._cache:
            return self._cache[genome]
        selector = None if genome is None else build_probe_selector(genome)
        with tempfile.TemporaryDirectory(prefix="ailibi-goodhart-") as tmp:
            directory = Path(tmp)
            self._roster_json(directory)
            env = TacticalRolloutEnv(
                num_players=self._num_players,
                num_impostors=self._num_impostors,
                tasks_per_crewmate=self._tasks_per_crewmate,
                intent_selector=selector,
                output_dir=directory,
                meeting_runner_factory=self._meeting_runner_factory,
            )
            for seed in self._seeds:
                env.rollout(seed)
            # The env writes a per-game audit sidecar; the referee's seed glob
            # would trip on it, so drop them before scoring.
            for sidecar in directory.glob("*.audit.jsonl"):
                sidecar.unlink()
            watchability = compute_watchability(
                directory, baseline_id=self._baseline_id
            )
            validity = run_validity_gate(directory)
        evaluation = _SetEvaluation(
            fitness=_composed_referee_fitness(watchability, validity.passed),
            watchability=watchability,
            validity_passed=validity.passed,
        )
        if genome is not None:
            self._cache[genome] = evaluation
        return evaluation

    def fitness(self, genome: tuple[float, ...]) -> float:
        return self.evaluate_set(genome).fitness


# --------------------------------------------------------------------------- #
# Decomposition — attribute every trace improvement to a moving term/floor.     #
# --------------------------------------------------------------------------- #

# The geomean weights (mirrors eval.watchability._GEOMEAN_WEIGHTS) — used ONLY to
# rank which dimension contributed most to a geomean improvement, never to
# recompute the referee (that lives in eval/, consumed read-only).
_DIM_WEIGHTS: Final[dict[str, float]] = {"d1": 0.40, "d2": 0.25, "d3": 0.15, "d4": 0.20}
_GEOMEAN_EPSILON: Final[float] = 1e-3


class TraceImprovement(BaseModel):
    """One decomposed fitness gain in the ES trace (Task 15.14).

    ``moving_term`` is the D-dimension / floor that moved most (weighted log-gain
    of the geomean, or the floor-trip rate) — or ``referee_gate`` when the
    composed-referee gate FLIPPED to passing between the two champions, in which
    case the fitness jump is the referee-pass bonus, not a geomean move;
    ``behavioral_cause`` names WHY (e.g. meeting-farming D4-contest,
    stall-to-clock D1) from the behavioral deltas. ``validity_passed_before`` /
    ``validity_passed_after`` and ``referee_passed_before`` /
    ``referee_passed_after`` carry both gate states through the trace: a jump out
    of ``_INVALID_FITNESS`` decomposes to ``validity_gate`` (constraint
    satisfaction, not a D-term move) and a referee-pass-bonus jump to
    ``referee_gate`` — neither is ever laundered as a D-term. Every trace
    improvement produces one of these — the "no undecomposed gains" contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    generation: int
    fitness_before: float
    fitness_after: float
    delta: float
    moving_term: str
    behavioral_cause: str
    validity_passed_before: bool
    validity_passed_after: bool
    referee_passed_before: bool
    referee_passed_after: bool
    mean_meetings_before: float
    mean_meetings_after: float
    floor_trip_rate_before: float
    floor_trip_rate_after: float


def _dominant_dimension(before: _SetAggregates, after: _SetAggregates) -> str:
    """The D-dimension whose weighted log-gain most raised the geomean."""

    dims = {
        "d1": (before.mean_d1, after.mean_d1),
        "d2": (before.mean_d2, after.mean_d2),
        "d3": (before.mean_d3, after.mean_d3),
        "d4": (before.mean_d4, after.mean_d4),
    }
    contributions = {
        dim: _DIM_WEIGHTS[dim]
        * (
            math.log(max(after_val, _GEOMEAN_EPSILON))
            - math.log(max(before_val, _GEOMEAN_EPSILON))
        )
        for dim, (before_val, after_val) in dims.items()
    }
    return max(contributions, key=lambda dim: contributions[dim])


def _mechanism(before: _SetAggregates, after: _SetAggregates, moving_term: str) -> str:
    """The distinct exploit MECHANISM behind a moving term (the dedupe key).

    Two exploits that move the same top-level D dimension through DIFFERENT
    mechanisms (D2 separation theater vs D2 conversion; D4 contest-farming vs
    D4 arc/swing) are distinct findings, each owed its own trajectory evidence
    and recommended floor — so exploit dedupe keys on the mechanism, never on
    the dimension alone.
    """

    if moving_term == "d4":
        contest_delta = after.mean_d4_contest - before.mean_d4_contest
        meetings_delta = after.mean_meetings - before.mean_meetings
        if contest_delta > 1e-6 and meetings_delta > 1e-6:
            return "d4-contest-farming"
        return "d4-arc-swing"
    if moving_term == "d2":
        sep_delta = after.mean_d2_separation - before.mean_d2_separation
        conv_delta = after.mean_d2_conversion - before.mean_d2_conversion
        if sep_delta > 1e-6 and conv_delta <= 1e-6:
            return "d2-separation-theater"
        return "d2-conversion"
    # d1 / d3 / floor / referee_gate have one mechanism each.
    return moving_term


def _behavioral_cause(
    before: _SetAggregates, after: _SetAggregates, moving_term: str
) -> str:
    """Name the behavior behind a moving term from the set-level deltas."""

    mechanism = _mechanism(before, after, moving_term)
    if mechanism == "floor":
        return (
            "fewer per-game integrity floors tripped "
            f"({before.floor_trip_rate:.2f} -> {after.floor_trip_rate:.2f} trip "
            "rate): a railroad / friendly-fire / drift floor stopped zeroing games"
        )
    if mechanism == "d4-contest-farming":
        return (
            "meeting-farming: mean meetings/game "
            f"{before.mean_meetings:.2f} -> {after.mean_meetings:.2f} lifts the "
            "D4 contest term min(1,(n-1)/2) with no added deduction"
        )
    if mechanism == "d4-arc-swing":
        return (
            "D4 arc/swing moved (a cross-meeting suspicion rise/knife-edge eject) "
            "— meeting-decided, not tactically reachable under fake meetings"
        )
    if mechanism == "d1":
        return (
            "resolution shift: the D1 term moved with the win-reason / meeting mix "
            f"(mean meetings {before.mean_meetings:.2f} -> {after.mean_meetings:.2f})"
        )
    if mechanism == "d2-separation-theater":
        return (
            "D2 SEPARATION inflated "
            f"({before.mean_d2_separation:.2f} -> {after.mean_d2_separation:.2f}) "
            "while conversion stayed pinned "
            f"({before.mean_d2_conversion:.2f} -> {after.mean_d2_conversion:.2f}): "
            "the FAKE provider's rendered suspicion tracks the impostor's "
            "kill/exposure count, so aggressive play lifts the 'crew-deduction' "
            "term WITHOUT any ejection — suspicion theater, a REACHABLE artifact "
            "of scoring separation on fake-provider suspicion, not real deduction"
        )
    if mechanism == "d2-conversion":
        return (
            "D2 conversion moved (a real ejection of an observation-backed impostor) "
            "— meeting-decided; unexpected under fake meetings, so treat as "
            "chaotic-fitness noise until the surrogate re-run confirms it (FO-3)"
        )
    if mechanism == "d3":
        return (
            "D3 (impostor deflection) is decided inside the meeting; a move under "
            "fake meetings is chaotic-fitness noise, not reachable (FO-3) — surrogate"
        )
    return "unattributed"


def _moving_term(before: _SetAggregates, after: _SetAggregates) -> str:
    """The term a gain attributes to: an un-tripped floor, else the top dimension.

    A geomean gain vs a floor gain: if the floor-trip rate fell, the un-zeroing
    dominates; else the geomean dimension with the largest weighted log-gain.
    """

    if after.floor_trip_rate < before.floor_trip_rate - 1e-9:
        return "floor"
    return _dominant_dimension(before, after)


def _validity_flip_cause(after_eval: _SetEvaluation) -> str:
    """The cause string for a validity-gate flip in the trace (out of invalid)."""

    return (
        "the HARD validity gate FLIPPED to passing (validity_passed False -> "
        "True): the fitness jump is constraint satisfaction — the previous "
        "champion's set was scored _INVALID_FITNESS (e.g. a stall-to-clock set "
        "tripping the meeting-rate floor), so the gain is the whole referee score "
        f"of the first ADMISSIBLE set (referee_passed="
        f"{after_eval.watchability.referee_passed}), not a D-term move"
    )


def _gate_flip_cause(after_report: WatchabilityReport) -> str:
    """The cause string for a referee-gate flip in the trace (the bonus jump)."""

    gauges = ", ".join(
        f"{g.name}={'PASS' if g.passed else 'FAIL'}" for g in after_report.supply_gauges
    )
    return (
        "the COMPOSED referee gate FLIPPED to passing (referee_passed False -> "
        "True): the fitness jump is the referee-pass bonus, not a geomean move — "
        f"the evidence-supply floors / integrity now clear ({gauges}), so the "
        "SELECTION gate would accept this directly-referee-optimized champion "
        "(the gate-laundering mechanism the 15.15 surrogate re-run hunts)"
    )


def _decompose_improvement(
    generation: int,
    fitness_before: float,
    fitness_after: float,
    before_eval: _SetEvaluation,
    after_eval: _SetEvaluation,
) -> TraceImprovement:
    before = _aggregate(before_eval.watchability.per_game)
    after = _aggregate(after_eval.watchability.per_game)
    valid_before = before_eval.validity_passed
    valid_after = after_eval.validity_passed
    gate_before = before_eval.watchability.referee_passed
    gate_after = after_eval.watchability.referee_passed
    # Gate flips get their own terms — attributing either jump to whichever
    # D-term drifted alongside would hide the mechanism. A validity flip is
    # checked FIRST: the previous fitness was pinned at _INVALID_FITNESS, so the
    # whole gain is constraint satisfaction regardless of the D-term deltas. Then
    # a referee flip (the dominating pass bonus). Neither reverse flip can be an
    # improvement — dropping to _INVALID_FITNESS or losing the bonus always
    # dwarfs any geomean gain.
    if valid_after and not valid_before:
        moving_term = "validity_gate"
        behavioral_cause = _validity_flip_cause(after_eval)
    elif gate_after and not gate_before:
        moving_term = "referee_gate"
        behavioral_cause = _gate_flip_cause(after_eval.watchability)
    else:
        moving_term = _moving_term(before, after)
        behavioral_cause = _behavioral_cause(before, after, moving_term)
    return TraceImprovement(
        generation=generation,
        fitness_before=round(fitness_before, 4),
        fitness_after=round(fitness_after, 4),
        delta=round(fitness_after - fitness_before, 4),
        moving_term=moving_term,
        behavioral_cause=behavioral_cause,
        validity_passed_before=valid_before,
        validity_passed_after=valid_after,
        referee_passed_before=gate_before,
        referee_passed_after=gate_after,
        mean_meetings_before=round(before.mean_meetings, 3),
        mean_meetings_after=round(after.mean_meetings, 3),
        floor_trip_rate_before=round(before.floor_trip_rate, 3),
        floor_trip_rate_after=round(after.floor_trip_rate, 3),
    )


# --------------------------------------------------------------------------- #
# The probe report (public type) + the driver.                                 #
# --------------------------------------------------------------------------- #


class ProbeExploit(BaseModel):
    """One material exploit surfaced by the probe (routed to the PAUSE).

    ``mechanism`` is the distinct exploit mechanism (e.g. ``d2-separation-theater``
    vs ``d2-conversion``) — the dedupe key, finer than ``moving_term`` so two
    different attacks on the same D dimension are both reported.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    moving_term: str
    mechanism: str
    behavioral_cause: str
    score_baseline: float
    score_champion: float
    delta: float
    trajectory_evidence: str
    recommended_floor: str


class LeverResult(BaseModel):
    """One single-tactic reachability-sweep result (Task 15.14).

    The sweep forces each menu lever (kill / emergency / report / wait /
    sabotage) to the top of the ranking and scores the resulting degenerate
    policy — the physically-reachable corners of genome space a bounded random-init
    ES may not stumble into. ``relative_gain`` is vs the scripted-FSM baseline.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    tactic: str
    mean_score: float
    referee_passed: bool
    validity_passed: bool
    relative_gain: float
    mean_meetings: float
    moving_term: str
    behavioral_cause: str


class ProbeBudget(BaseModel):
    """The stated ES budget (generations x population x seeds)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    generations: int
    population: int
    num_seeds: int
    fitness_seeds: tuple[int, ...]
    total_evaluations: int
    lever_sweep_evaluations: int


class GoodhartProbeReport(BaseModel):
    """The trust verdict + exploit decompositions for one probe run (Task 15.14).

    Downstream (15.15) imports this symbol to append the surrogate-path re-run
    delta; keep the signature stable. ``champion_genome`` is ADDITIVE at Task
    18.18 (default ``()`` so pre-18.18 report JSON still validates): the exact
    ES champion genome, exposed so the conviction-path arms re-roll the
    champion corner through the committed 18.16 instrument without re-running
    the ES — the floats travel exactly (JSON floats round-trip), the same
    genome :meth:`~training.bakeoff.es.ESResult.digest` hashes.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    roster_key: str
    baseline_id: str
    genome_length: int
    es_digest: str
    budget: ProbeBudget
    materiality_bar: float
    baseline_mean_score: float
    baseline_referee_passed: bool
    baseline_validity_passed: bool
    champion_mean_score: float
    champion_referee_passed: bool
    champion_validity_passed: bool
    relative_gain: float
    fitness_trace: tuple[float, ...]
    improvements: tuple[TraceImprovement, ...]
    lever_sweep: tuple[LeverResult, ...]
    strongest_reachable_score: float
    verdict: Literal["HELD", "EXPLOITS_FOUND"]
    exploits: tuple[ProbeExploit, ...]
    supply_floor_note: str
    surrogate_rerun_obligation: str
    champion_genome: tuple[float, ...] = ()

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2)


_SURROGATE_OBLIGATION: Final[str] = (
    "OBLIGATION (Task 15.15): re-run this probe under the 15.13 learned meeting "
    "surrogate on the fixed eval seed set. Under fake meetings the meeting-decided "
    "terms (D2 separation/conversion, D3 deflection) and the meeting-driven supply "
    "floors (flags_per_meeting, testimony_backed_conversion) are structurally "
    "unreachable, so a null result on them is NOT evidence the referee is safe — it "
    "only means the fake provider supplies no evidence to move. The surrogate opens "
    "those terms to tactical pressure; the 15.15 report appends the delta verdict."
)


def _supply_floor_note(report: WatchabilityReport, fake_meetings: bool) -> str:
    provider = "fake meetings" if fake_meetings else "the surrogate meeting path"
    gauges = ", ".join(
        f"{g.name}={'PASS' if g.passed else 'FAIL'}"
        f"(measured={g.measured}, floor={g.floor})"
        for g in report.supply_gauges
    )
    prefix = f"Evidence-supply floors on the champion set ({provider}): {gauges}. "
    if fake_meetings and not report.referee_passed:
        return (
            prefix + "The meeting-driven floors cannot clear under the fake provider "
            "(no contradiction flags, no observation-backed accusations), so "
            "referee_passed stays False — the champion-SELECTION GATE holds under "
            "probe by the two-layer design, independent of the geomean."
        )
    if report.referee_passed:
        return (
            prefix + "The champion CLEARS the composed referee (referee_passed=True) "
            "— the selection gate would ACCEPT this candidate, so the supply floors "
            "did NOT hold here; see the gate-laundering exploit."
        )
    return (
        prefix + "The champion does not clear the supply-floor gate "
        "(referee_passed=False); the gate holds for this candidate, independent of "
        "the geomean."
    )


def run_goodhart_probe(
    *,
    config: ESConfig,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    baseline_id: str = "baseline-8",
    materiality_bar: float = 0.25,
    meeting_runner_factory: MeetingRunnerFactory | None = None,
) -> GoodhartProbeReport:
    """Run the probe: ES on the referee score, then the trust verdict (Task 15.14).

    ``materiality_bar`` is the RELATIVE geomean gain (champion vs scripted-FSM
    baseline ``mean_score``) above which a decomposed gain is reported as an
    exploit rather than chaotic-fitness noise. ``meeting_runner_factory`` defaults
    to the env's fake-provider runner (this task's scoping); Task 15.15 passes the
    15.13 learned surrogate factory to discharge the surrogate-path re-run
    obligation through this SAME probe path. Deterministic under ``config.seed``
    (the env + referee are pure functions of the seed).
    """

    evaluator = _RefereeAttackEvaluator(
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        fitness_seeds=config.fitness_seeds,
        baseline_id=baseline_id,
        meeting_runner_factory=meeting_runner_factory,
    )

    baseline = evaluator.evaluate_set(None)
    baseline_score = baseline.watchability.mean_score
    baseline_aggs = _aggregate(baseline.watchability.per_game)
    # The referee's report-level mean_score is display-rounded (2 decimals), so
    # every gain / materiality-bar comparison below uses the UNROUNDED per-game
    # set mean instead — the same fsum mean before the report rounding. Display
    # fields keep the referee's own rounded values.
    baseline_exact = baseline_aggs.mean_score

    # The required attack: run evolution DIRECTLY on the referee score.
    result: ESResult = evolve(
        evaluator.fitness,
        genome_length=probe_genome_length(),
        config=config,
    )

    # Decompose EVERY improvement in the champion trace (no undecomposed gains).
    # The FULL evaluations (not just the D-term aggregates) flow through so a
    # referee-gate flip — the dominating pass bonus — decomposes to referee_gate
    # rather than being laundered as whichever D-term drifted alongside it.
    champion_evals = [
        evaluator.evaluate_set(genome) for genome in result.champion_trace
    ]
    improvements: list[TraceImprovement] = []
    for gen in range(1, len(result.fitness_trace)):
        before_f = result.fitness_trace[gen - 1]
        after_f = result.fitness_trace[gen]
        if after_f > before_f + 1e-9:
            improvements.append(
                _decompose_improvement(
                    gen,
                    before_f,
                    after_f,
                    champion_evals[gen - 1],
                    champion_evals[gen],
                )
            )

    # The reachability sweep: force each single-tactic lever and score its
    # degenerate policy. A bounded random-init ES can MISS a reachable exploit; the
    # sweep is the systematic net so a null ES trace never launders a false HELD.
    levers, lever_candidates = _sweep_levers(evaluator, baseline_exact, baseline_aggs)

    champion_eval = evaluator.evaluate_set(result.champion)
    champion_report = champion_eval.watchability
    champion_score = champion_report.mean_score
    champion_exact = _aggregate(champion_report.per_game).mean_score
    relative_gain = _relative_gain(baseline_exact, champion_exact)

    # None => the fake-provider runner (this task); a factory => the 15.15 surrogate
    # path, under which the meeting-driven supply floors CAN clear and a candidate
    # may launder past the gate. The verdict + evidence text branch on this.
    fake_meetings = meeting_runner_factory is None
    exploits, strongest_score = _build_exploits(
        baseline_score=baseline_exact,
        baseline_aggs=baseline_aggs,
        baseline_referee_passed=baseline.watchability.referee_passed,
        champion_eval=champion_eval,
        champion_score=champion_exact,
        champion_gain=relative_gain,
        lever_candidates=lever_candidates,
        materiality_bar=materiality_bar,
        fake_meetings=fake_meetings,
    )
    verdict: Literal["HELD", "EXPLOITS_FOUND"] = (
        "EXPLOITS_FOUND" if exploits else "HELD"
    )

    return GoodhartProbeReport(
        roster_key=champion_report.roster_key,
        baseline_id=baseline_id,
        genome_length=probe_genome_length(),
        es_digest=result.digest(),
        budget=ProbeBudget(
            generations=config.generations,
            population=config.population,
            num_seeds=len(config.fitness_seeds),
            fitness_seeds=config.fitness_seeds,
            total_evaluations=result.num_evaluations,
            lever_sweep_evaluations=len(_SWEEP_TACTICS),
        ),
        materiality_bar=materiality_bar,
        baseline_mean_score=baseline_score,
        baseline_referee_passed=baseline.watchability.referee_passed,
        baseline_validity_passed=baseline.validity_passed,
        champion_mean_score=champion_score,
        champion_referee_passed=champion_report.referee_passed,
        champion_validity_passed=champion_eval.validity_passed,
        relative_gain=round(relative_gain, 4) if math.isfinite(relative_gain) else -1.0,
        fitness_trace=tuple(round(v, 4) for v in result.fitness_trace),
        improvements=tuple(improvements),
        lever_sweep=levers,
        strongest_reachable_score=round(strongest_score, 2),
        verdict=verdict,
        exploits=exploits,
        supply_floor_note=_supply_floor_note(champion_report, fake_meetings),
        surrogate_rerun_obligation=_SURROGATE_OBLIGATION,
        champion_genome=result.champion,
    )


def _relative_gain(baseline_score: float, score: float) -> float:
    """Relative geomean gain of ``score`` over the baseline (inf if baseline 0)."""

    if baseline_score > 0:
        return (score - baseline_score) / baseline_score
    return math.inf if score > 0 else 0.0


def _sweep_levers(
    evaluator: _RefereeAttackEvaluator,
    baseline_score: float,
    baseline_aggs: _SetAggregates,
) -> tuple[tuple[LeverResult, ...], tuple[_ExploitCandidate, ...]]:
    """Score every single-tactic lever, decomposed vs the scripted-FSM baseline.

    ``baseline_score`` is the UNROUNDED per-game set mean. Returns the display
    rows AND the exploit candidates: the candidate carries the unrounded
    score/gain (from the per-game aggregates, NOT the display-rounded
    ``WatchabilityReport.mean_score``) so ``_build_exploits`` thresholds and
    dedupes on exact values, while ``LeverResult`` stays rounded for the report.
    """

    results: list[LeverResult] = []
    candidates: list[_ExploitCandidate] = []
    for tactic in _SWEEP_TACTICS:
        evaluation = evaluator.evaluate_set(_forced_genome(tactic))
        aggs = _aggregate(evaluation.watchability.per_game)
        exact_score = aggs.mean_score
        moving = _moving_term(baseline_aggs, aggs)
        results.append(
            LeverResult(
                tactic=tactic,
                mean_score=round(evaluation.watchability.mean_score, 2),
                referee_passed=evaluation.watchability.referee_passed,
                validity_passed=evaluation.validity_passed,
                relative_gain=round(_relative_gain(baseline_score, exact_score), 4),
                mean_meetings=round(aggs.mean_meetings, 3),
                moving_term=moving,
                behavioral_cause=_behavioral_cause(baseline_aggs, aggs, moving),
            )
        )
        candidates.append(
            _ExploitCandidate(
                label=f"forced-{tactic} lever",
                score=exact_score,
                gain=_relative_gain(baseline_score, exact_score),
                referee_passed=evaluation.watchability.referee_passed,
                validity_passed=evaluation.validity_passed,
                aggs=aggs,
            )
        )
    return tuple(results), tuple(candidates)


def _recommended_floor(mechanism: str) -> str:
    """The floor/patch recommended to the PAUSE for one MECHANISM (never applied).

    Keyed on the exploit mechanism (``_mechanism``), not the top-level D
    dimension: two exploits on the same dimension (D2 separation theater vs D2
    conversion, D4 contest-farming vs D4 arc/swing) need DIFFERENT patches, and
    each reported exploit must carry the one that fits its mechanism.
    """

    if mechanism == "referee_gate":
        return (
            "A referee-optimized genome CLEARS the composed selection gate "
            "(referee_passed) that the honest scripted baseline does NOT — the "
            "referee would SELECT this candidate as a champion. Scrutinize whether "
            "its play is genuinely watchable or a laundered degenerate before "
            "trusting the gate; harden the supply floors / add a behavioral-diversity "
            "check against the anchor — routed to the PAUSE (eval/watchability.py is "
            "the subject under attack, out of scope here)"
        )
    if mechanism == "d4-contest-farming":
        return (
            "cap the D4 contest term's reward for raw meeting COUNT (it already "
            "saturates at n>=3); gate contest on a per-meeting evidence floor so "
            "impostor-farmed empty meetings cannot inflate it — routed to the PAUSE, "
            "not self-served (eval/watchability.py is out of scope here)"
        )
    if mechanism == "d4-arc-swing":
        return (
            "audit how the D4 arc/swing sub-terms were manufactured: a cross-meeting "
            "suspicion arc or knife-edge eject produced by a policy optimizing the "
            "referee (rather than by real deliberation) is drama theater — gate "
            "arc/swing on evidence-backed suspicion movement and re-confirm under "
            "the surrogate — routed to the PAUSE"
        )
    if mechanism == "floor":
        return (
            "audit which integrity floor stopped tripping; a genome that avoids the "
            "railroad/friendly-fire floors is legitimate, but confirm no drift floor "
            "was bypassed — routed to the PAUSE"
        )
    if mechanism == "d1":
        return (
            "confirm the D1 resolution tiers cannot be farmed by stall/clock or "
            "self-ejection; consider a play-decided evidence requirement — PAUSE"
        )
    if mechanism == "d2-separation-theater":
        return (
            "GATE the D2 separation sub-term on conversion/evidence: separation "
            "without an ejection or a contradiction flag is suspicion theater, not "
            "deduction, and the fake provider lets kill-aggression inflate it. Cap or "
            "condition separation on backed conversion, and NEVER read mean_score "
            "without the supply-floor gate — routed to the PAUSE (eval/watchability.py "
            "is the subject under attack, out of scope here)"
        )
    if mechanism == "d2-conversion":
        return (
            "audit HOW the D2 conversions were produced: ejections farmed by a "
            "referee-optimized policy (e.g. baiting cheap ejects or self-exposure "
            "theater) are not deduction — verify each conversion is observation-"
            "backed (the testimony_backed_conversion floor) and not railroaded, and "
            "re-confirm under the surrogate — routed to the PAUSE"
        )
    return (
        f"{mechanism.upper()} moved under fake meetings; re-confirm under the "
        "surrogate before trusting the delta — routed to the PAUSE"
    )


@dataclass(frozen=True)
class _ExploitCandidate:
    """One evaluated policy considered as a potential exploit (ES champ / lever)."""

    label: str
    score: float
    gain: float
    referee_passed: bool
    validity_passed: bool
    aggs: _SetAggregates


def _build_exploits(
    *,
    baseline_score: float,
    baseline_aggs: _SetAggregates,
    baseline_referee_passed: bool,
    champion_eval: _SetEvaluation,
    champion_score: float,
    champion_gain: float,
    lever_candidates: Sequence[_ExploitCandidate],
    materiality_bar: float,
    fake_meetings: bool,
) -> tuple[tuple[ProbeExploit, ...], float]:
    """Promote every material policy (ES champion / lever) to an exploit.

    Returns ``(exploits, strongest_reachable_score)``. A candidate is material when
    the validity gate passes AND EITHER of:

    * it CLEARS the composed referee gate (``referee_passed``) that the honest
      scripted baseline does NOT — a laundered champion the SELECTION gate would
      accept (the strongest possible exploit; flagged regardless of geomean gain,
      the primary case the 15.15 surrogate path opens); or
    * its relative geomean gain clears the materiality bar — the ``mean_score``
      sub-metric pushed materially above the honest FSM (today's fake-meeting
      finding, where the gate still rejects it).

    Gains are compared UNROUNDED — candidate/baseline scores are the per-game set
    means, not the display-rounded ``WatchabilityReport.mean_score``, and rounding
    only happens at display time — so a candidate at 24.99% is not promoted past a
    25% bar (nor a below-bar one promoted by 2-decimal report rounding). Deduped
    by the exploit
    MECHANISM (``_mechanism`` — finer than the top-level D dimension), so two
    distinct attacks that move the same dimension (D2 separation theater vs D2
    conversion, D4 contest-farming vs D4 arc/swing) are BOTH reported, each with
    its own trajectory evidence and recommended floor, while repeats of one
    mechanism keep only the worst-case (highest-scoring) evidence.
    """

    candidates: list[_ExploitCandidate] = [
        _ExploitCandidate(
            label="ES champion",
            score=champion_score,
            gain=champion_gain,
            referee_passed=champion_eval.watchability.referee_passed,
            validity_passed=champion_eval.validity_passed,
            aggs=_aggregate(champion_eval.watchability.per_game),
        ),
        *lever_candidates,
    ]

    # The strongest ADMISSIBLE reachable score: the probe is validity-gated, so a
    # validity-failing candidate (e.g. a stall-to-clock set that trips the meeting-
    # rate floor) is not a reachable attack and must not be reported as the
    # strongest — even if its raw geomean is high. Ranks the baseline + the
    # validity-passing candidates only.
    strongest_score = max(
        [baseline_score]
        + [candidate.score for candidate in candidates if candidate.validity_passed]
    )

    def _gate_laundered(candidate: _ExploitCandidate) -> bool:
        # A referee-optimized genome that clears the gate the honest baseline does
        # not = the referee would SELECT a directly-optimized champion.
        return candidate.referee_passed and not baseline_referee_passed

    material = [
        candidate
        for candidate in candidates
        if candidate.validity_passed
        and (candidate.gain >= materiality_bar or _gate_laundered(candidate))
    ]
    # Gate-laundering first (the strongest exploit), then by score; dedupe by the
    # exploit MECHANISM so each distinct mechanism is reported once with its
    # worst-case evidence.
    material.sort(
        key=lambda candidate: (_gate_laundered(candidate), candidate.score),
        reverse=True,
    )
    exploits: list[ProbeExploit] = []
    seen_mechanisms: set[str] = set()
    for candidate in material:
        laundered = _gate_laundered(candidate)
        if laundered:
            moving = "referee_gate"
            mechanism = "referee_gate"
        else:
            moving = _moving_term(baseline_aggs, candidate.aggs)
            mechanism = _mechanism(baseline_aggs, candidate.aggs, moving)
        if mechanism in seen_mechanisms:
            continue
        seen_mechanisms.add(mechanism)
        exploits.append(
            ProbeExploit(
                moving_term=moving,
                mechanism=mechanism,
                behavioral_cause=(
                    _gate_laundered_cause(candidate)
                    if laundered
                    else _behavioral_cause(baseline_aggs, candidate.aggs, moving)
                ),
                score_baseline=round(baseline_score, 2),
                score_champion=round(candidate.score, 2),
                delta=round(candidate.score - baseline_score, 2),
                trajectory_evidence=_exploit_trajectory(
                    candidate, baseline_score, baseline_aggs, fake_meetings, laundered
                ),
                recommended_floor=_recommended_floor(mechanism),
            )
        )
    return tuple(exploits), strongest_score


def _gate_laundered_cause(candidate: _ExploitCandidate) -> str:
    return (
        f"{candidate.label} CLEARS the composed referee (referee_passed=True) that "
        "the honest scripted baseline does not: a directly-referee-optimized genome "
        f"the SELECTION gate would accept as a champion at mean_score "
        f"{candidate.score:.2f}. This is laundering the forbidden objective past the "
        "gate — the exact failure the two-layer referee exists to prevent."
    )


def _exploit_trajectory(
    candidate: _ExploitCandidate,
    baseline_score: float,
    baseline_aggs: _SetAggregates,
    fake_meetings: bool,
    laundered: bool,
) -> str:
    head = (
        f"{candidate.label}: scripted-FSM baseline mean_score={baseline_score:.2f} "
        f"(mean meetings {baseline_aggs.mean_meetings:.2f}) -> mean_score="
        f"{candidate.score:.2f} (mean meetings {candidate.aggs.mean_meetings:.2f}); "
        f"relative geomean gain {candidate.gain:.0%}. "
        f"referee_passed={candidate.referee_passed}"
    )
    if laundered:
        return (
            head + " — the candidate CLEARS the composed selection gate and would be "
            "SELECTED as a champion (LAUNDERED); the supply floors did NOT hold here."
        )
    if fake_meetings:
        return (
            head + " — the supply-floor GATE still rejects it under fake meetings, so "
            "no champion is laundered TODAY, but the geomean sub-metric is inflated "
            "(re-check under the surrogate)."
        )
    return (
        head + " — the supply-floor gate rejects it on the surrogate meeting path, so "
        "no champion is laundered, but the geomean sub-metric is inflated."
    )


# --------------------------------------------------------------------------- #
# The 18.18 conviction-path arms — predicted supply vs recorded reality.        #
# --------------------------------------------------------------------------- #

# The carried finding this re-probe re-reads (audits/audit-phase-17-close.md §6,
# recorded by Task 17.15 on the baseline-5 floors): forced-`emergency`
# meeting-farming on the 4p1i reference roster, +61.8% over the scripted-FSM
# baseline via the D4 contest term — above the bar, routed to the PAUSE and
# carried with the instruction "re-probe before any 4p1i-scored selection".
# Consumed as committed NUMBERS (the pin-as-committed-ratio precedent), never
# re-measured; the re-read states the CURRENT substrate beside them.
_CARRIED_MECHANISM: Final[str] = "d4-contest-farming"
_CARRIED_TACTIC: Final[str] = "emergency"
_CARRIED_ROSTER: Final[str] = "4p1i"
_CARRIED_BASELINE_MEAN_SCORE: Final[float] = 0.85
_CARRIED_LEVER_MEAN_SCORE: Final[float] = 1.38
_CARRIED_RELATIVE_GAIN: Final[float] = 0.618

# The tactic tokens of the two non-lever reads (the deltas' anchor and the ES
# corner). Levers keep their menu names, so a read is findable by tactic.
_BASELINE_TACTIC: Final[str] = "fsm-baseline"
_CHAMPION_TACTIC: Final[str] = "es-champion"

# The roster the committed pre-screen's floors are pinned for (the harness's
# PRESCREEN_* constants are the baseline-6 9p2i pins; there is no other
# committed pre-screen). A gate read on any other roster is diagnostic and the
# gate verdict says so.
_PRESCREEN_PINS_ROSTER: Final[str] = "9p2i"


class ConvictionLeverRead(BaseModel):
    """One policy's predicted-supply vs recorded-reality read (Task 18.18).

    The narrow 18.18 question, per probed policy (the scripted-FSM baseline,
    each forced lever, the ES champion corner): does the conviction TERM — a
    prediction — diverge from the recorded REALITY (flags in bytes) under this
    play, and by how much. Two channel conventions, deliberately both:

    * the FITNESS channel (``mean_episode_predicted_supply`` /
      ``mean_episode_actual_flags``): per-episode means, K-seed averaged —
      EXACTLY the quantity ``inner_episode_fitness`` pays
      (``DecisionTrace.mean_predicted_supply``'s convention: a no-meeting
      episode contributes 0.0), so ``conviction_term`` is the term's real
      inner-fitness contribution and ``conviction_term_delta`` its move vs the
      scripted-FSM baseline;
    * the SIDE-BY-SIDE channel (``*_per_meeting`` / the shares): set-level
      per-meeting means — the report's predicted-vs-actual display, the
      ``flags_minted`` labels being the referee's own quantities mirrored from
      the recorded bytes.

    ``launders_supply`` is the verdict on the fitness channel — the probe's
    UNCHANGED delta convention applied to the new term: a lever launders when
    (validity-gated) its predicted-supply gain clears the materiality bar while
    the recorded-flags gain does NOT — predicted supply bought fitness the
    play's bytes never minted. Gains follow :func:`_signed_relative_gain` (the
    flags head is unclipped, so the channel is signed: the denominator is
    ``abs(baseline)``; a zero baseline reads ``inf`` when the lever is
    positive, else 0.0), are compared UNROUNDED, and are DISPLAYED via the
    standing convention
    (4 decimals; non-finite stored as -1.0 — ``materiality_arithmetic``
    carries the honest wording either way). The pre-screen booleans are the
    COMMITTED 18.16 instrument's own verdict over this set's meetings — its
    floors are the baseline-6 9p2i pins as shipped, on every roster (there is
    no other committed pre-screen; a non-9p2i gate read is diagnostic and the
    report says so).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str
    tactic: str
    games: int
    meetings: int
    validity_passed: bool
    referee_passed: bool
    supply_floors_passed: bool
    mean_score: float
    mean_episode_predicted_supply: float
    mean_episode_actual_flags: float
    conviction_term: float
    conviction_term_delta: float
    predicted_supply_gain: float
    actual_supply_gain: float
    predicted_flags_per_meeting: float
    actual_flags_per_meeting: float
    predicted_converting_share: float
    predicted_mean_conversion_prob: float
    actual_converting_share: float
    prescreen_flags_pass: bool
    prescreen_conversion_pass: bool
    prescreen_floors_pass: bool
    prescreen_advisory_only: bool
    launders_supply: bool
    materiality_arithmetic: str


class ConvictionGateCheck(BaseModel):
    """The composed-gate laundering verdict over every probed policy (18.18).

    The 18.16 pre-screen is a PREDICTED-floors gate the campaign driver
    consults before spending real-path evals; the recorded referee floors are
    the reality it predicts. A predicted-PASS / recorded-FAIL divergence
    splits on the standing BASELINE-RELATIVE gate convention (the probe's
    gate-flip doctrine — a flip is measured against the honest scripted
    baseline, never in isolation):

    * ``laundered`` — validity-passing policies whose predicted floors PASS
      while their recorded supply floors FAIL and the honest baseline does
      NOT share the divergence: adversarial play FLIPPED the predicted gate —
      the true laundering seam, flagged REGARDLESS of magnitude;
    * ``substrate_divergent`` — the same predicted-PASS / recorded-FAIL read
      when the HONEST BASELINE shows it too: no lever flipped anything — the
      model predicts the real-path supply economy it was fit on while this
      substrate's meetings mint no flags in bytes. A consumption hazard
      (named, never silent), not lever laundering.

    ``false_blocked`` is the reverse divergence (predicted FAIL, recorded
    PASS): an efficiency loss, reported, never a blocker. All three are
    validity-gated — an inadmissible set is not a reachable attack (the
    standing doctrine); the per-read booleans stay raw.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    prescreen_is_gating: bool
    laundered: tuple[str, ...]
    substrate_divergent: tuple[str, ...]
    false_blocked: tuple[str, ...]
    verdict: str


class ConvictionPathFinding(BaseModel):
    """One material conviction-path seam (named, never a silent caveat).

    ``mechanism`` is ``conviction-supply-laundering`` (the term pays fitness
    for predicted evidence the play never mints) or
    ``prescreen-gate-laundering`` (the predicted floors pass where the recorded
    floors fail). ``blocker`` is the NAMED blocker string the 18.24 protocol
    consumes — the task contract's "never a silent caveat".
    ``recommended_guard`` is routed, never applied: the probed modules
    (``training/conviction/``, ``training/bakeoff/harness.py``) are out of
    scope here by contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    mechanism: str
    tactic: str
    label: str
    behavioral_cause: str
    materiality_arithmetic: str
    recommended_guard: str
    blocker: str


class CarriedExploitReread(BaseModel):
    """The carried 4p1i ``d4-contest-farming`` exploit, re-read (Task 18.18).

    The carried numbers are the audit-committed pins (17.15, baseline-5
    floors); the re-read numbers are the CURRENT substrate's (baseline-6, the
    conviction path live). ``still_above_bar`` keeps or releases the carried
    blocker; ``conviction_term_delta`` / ``conviction_launders_supply`` add the
    NEW question — does meeting-farming also pay the conviction term without
    minting evidence.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    mechanism: str
    tactic: str
    roster_key: str
    carried_baseline_mean_score: float
    carried_lever_mean_score: float
    carried_relative_gain: float
    reread_baseline_mean_score: float
    reread_lever_mean_score: float
    reread_relative_gain: float
    reread_moving_term: str
    still_above_bar: bool
    conviction_term_delta: float
    conviction_launders_supply: bool
    materiality_arithmetic: str
    verdict: str


class ConvictionPathProbeReport(BaseModel):
    """The 18.18 re-probe: the standing probe + the conviction-path arms.

    ``probe`` is the UNCHANGED standing report (the standing bars); the arms
    ride beside it, never inside its fitness. ``reads`` is the scripted-FSM
    baseline first, then the forced levers in menu order, then the ES champion
    corner. ``blockers`` names every above-bar finding — the conviction-path
    findings AND the standing probe's exploits — so the 18.24 protocol
    consumes a LIST, never a prose caveat; ``verdict`` composes over both.
    Consumption discipline: ``conviction_uses`` is this probe's metered spend
    on the ONE shared sha-keyed counter (every recorded meeting is predicted
    once per committed consumption path — the fitness-term read and the
    pre-screen read), quoted against the committed cap.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    roster_key: str
    baseline_id: str
    conviction_weights_sha256: str
    conviction_model_verdict: Literal["GO", "NO-GO"]
    prescreen_role: Literal["gating", "advisory"]
    conviction_weight: float
    conversion_threshold: float
    materiality_bar: float
    probe: GoodhartProbeReport
    reads: tuple[ConvictionLeverRead, ...]
    gate_check: ConvictionGateCheck
    findings: tuple[ConvictionPathFinding, ...]
    blockers: tuple[str, ...]
    verdict: Literal["HELD", "EXPLOITS_FOUND"]
    conviction_uses: int
    conviction_uses_total: int
    conviction_max_uses: int
    consumption_note: str

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True, indent=2)


@dataclass(frozen=True)
class _ConvictionSetRead:
    """One policy set's raw conviction-arm numbers (pre-delta plumbing)."""

    label: str
    tactic: str
    games: int
    meetings: int
    validity_passed: bool
    referee_passed: bool
    supply_floors_passed: bool
    mean_score: float
    episode_predicted_supply: float
    episode_actual_flags: float
    predicted_flags_per_meeting: float
    actual_flags_per_meeting: float
    predicted_converting_share: float
    predicted_mean_conversion_prob: float
    actual_converting_share: float
    prescreen_flags_pass: bool
    prescreen_conversion_pass: bool
    prescreen_floors_pass: bool
    prescreen_advisory_only: bool


class _ConvictionArmReader:
    """Re-rolls a policy's replay set and reads the conviction arms off it.

    The env is a pure function of the seed, so the re-rolled bytes are
    byte-identical to the set the standing probe scored — the conviction
    table's features and mirrored labels ("flags in bytes") and the referee
    re-read here describe EXACTLY the play the standing bars scored. Every
    model prediction goes through the committed 18.16 consumption paths —
    ``ConvictionFitnessTerm.predict_meeting`` for the term read and
    ``conviction_prescreen`` for the composed-gate read — so both are metered
    on the ONE shared sha-keyed counter. Seed uniqueness is already enforced
    upstream (``ESConfig`` and the standing evaluator both reject duplicates
    before any reader exists).
    """

    def __init__(
        self,
        *,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        fitness_seeds: Sequence[int],
        baseline_id: str,
        term: "ConvictionFitnessTerm",
        conviction_artifact_dir: Path,
        meeting_runner_factory: MeetingRunnerFactory | None = None,
    ) -> None:
        self._num_players = num_players
        self._num_impostors = num_impostors
        self._tasks_per_crewmate = tasks_per_crewmate
        self._seeds = tuple(fitness_seeds)
        self._baseline_id = baseline_id
        self._term = term
        self._artifact_dir = conviction_artifact_dir
        self._meeting_runner_factory = meeting_runner_factory

    def read(
        self, genome: tuple[float, ...] | None, *, label: str, tactic: str
    ) -> _ConvictionSetRead:
        """Read one policy's set (``None`` = the scripted FSM), metered."""

        # Local import: the harness imports this module at module scope (see
        # run_conviction_path_probe's note) — the pre-screen consumed here is
        # the COMMITTED instrument, never a mirror.
        from training.bakeoff.harness import conviction_prescreen

        selector = None if genome is None else build_probe_selector(genome)
        with tempfile.TemporaryDirectory(prefix="ailibi-goodhart-conviction-") as tmp:
            directory = Path(tmp)
            (directory / "roster.json").write_text(
                json.dumps(
                    {
                        "num_players": self._num_players,
                        "num_impostors": self._num_impostors,
                        "tasks_per_crewmate": self._tasks_per_crewmate,
                    }
                )
            )
            env = TacticalRolloutEnv(
                num_players=self._num_players,
                num_impostors=self._num_impostors,
                tasks_per_crewmate=self._tasks_per_crewmate,
                intent_selector=selector,
                output_dir=directory,
                meeting_runner_factory=self._meeting_runner_factory,
            )
            for seed in self._seeds:
                env.rollout(seed)
            # The env's audit sidecars trip the referee's / walk's seed globs,
            # exactly as in the standing evaluator.
            for sidecar in directory.glob("*.audit.jsonl"):
                sidecar.unlink()
            watchability = compute_watchability(
                directory, baseline_id=self._baseline_id
            )
            validity = run_validity_gate(directory)
            table = build_conviction_table(directory)
            rows = table.rows
            # The term read: one metered prediction per recorded meeting, in
            # the table's deterministic (seed, meeting_index) order.
            predictions = [self._term.predict_meeting(row.features) for row in rows]
            # The composed-gate read: the COMMITTED pre-screen over the same
            # meetings, metered on the SAME shared counter.
            prescreen = conviction_prescreen(
                [row.features for row in rows],
                artifact_dir=self._artifact_dir,
                use_counter=self._term.use_counter,
            )

        # The fitness channel: per-episode means, K-seed averaged — exactly
        # the quantity inner_episode_fitness pays (a no-meeting episode
        # contributes 0.0, the DecisionTrace.mean_predicted_supply doctrine).
        predicted_by_seed: dict[int, list[float]] = {seed: [] for seed in self._seeds}
        actual_by_seed: dict[int, list[float]] = {seed: [] for seed in self._seeds}
        for row, prediction in zip(rows, predictions, strict=True):
            predicted_by_seed[row.seed].append(prediction.expected_flags)
            actual_by_seed[row.seed].append(float(row.flags_minted))
        episode_predicted = _mean(
            [_mean(values) for values in predicted_by_seed.values()]
        )
        episode_actual = _mean([_mean(values) for values in actual_by_seed.values()])

        # The side-by-side channel: set-level per-meeting means (0.0 on an
        # evidence-starved no-meeting set — documented, never a NaN).
        n = len(rows)
        predicted_per_meeting = (
            math.fsum(p.expected_flags for p in predictions) / n if n else 0.0
        )
        actual_per_meeting = (
            math.fsum(float(row.flags_minted) for row in rows) / n if n else 0.0
        )
        converting = sum(
            1
            for p in predictions
            if p.conversion_prob >= CONVICTION_CONVERSION_DECISION_THRESHOLD
        )
        mean_prob = math.fsum(p.conversion_prob for p in predictions) / n if n else 0.0
        actual_converting = sum(1 for row in rows if row.testimony_backed_conversion)

        return _ConvictionSetRead(
            label=label,
            tactic=tactic,
            games=len(self._seeds),
            meetings=n,
            validity_passed=validity.passed,
            referee_passed=watchability.referee_passed,
            supply_floors_passed=watchability.supply_floors_passed,
            mean_score=watchability.mean_score,
            episode_predicted_supply=episode_predicted,
            episode_actual_flags=episode_actual,
            predicted_flags_per_meeting=predicted_per_meeting,
            actual_flags_per_meeting=actual_per_meeting,
            predicted_converting_share=converting / n if n else 0.0,
            predicted_mean_conversion_prob=mean_prob,
            actual_converting_share=actual_converting / n if n else 0.0,
            prescreen_flags_pass=prescreen.predicted_flags_pass,
            prescreen_conversion_pass=prescreen.predicted_conversion_pass,
            prescreen_floors_pass=prescreen.predicted_floors_pass,
            prescreen_advisory_only=prescreen.advisory_only,
        )


def _display_gain(gain: float) -> float:
    """The standing display convention: 4 decimals; non-finite stored as -1.0."""

    return round(gain, 4) if math.isfinite(gain) else -1.0


def _format_gain(gain: float) -> str:
    """The honest wording for a gain, including the inf-on-zero-baseline branch."""

    if math.isinf(gain):
        return "+inf% (baseline 0)"
    return f"{gain:+.1%}"


def _signed_relative_gain(baseline: float, value: float) -> float:
    """The delta convention generalized to a SIGNED channel (Task 18.18).

    :func:`_relative_gain` was written for the geomean SCORE channel, which is
    never negative; the conviction flags head is DELIBERATELY UNCLIPPED (a
    negative supply score is a legitimate bottom rank — ``ConvictionPrediction``),
    so a non-positive baseline episode mean is reachable and the score-channel
    convention would silently collapse a real supply rise (e.g. -0.5 -> -0.1,
    a genuine +0.4 x weight term advantage) to a 0.0 gain — a false HELD in
    the dangerous direction (the 18.18 review's confirmed finding). The signed
    generalization divides by ``abs(baseline)`` — identical to the standing
    convention wherever the baseline is positive, honest on the negative
    branch, and keeping the documented zero-baseline branches (``inf`` on a
    rise from 0, 0.0 otherwise).
    """

    if baseline != 0.0:
        return (value - baseline) / abs(baseline)
    return math.inf if value > 0 else 0.0


def _build_conviction_read(
    baseline: _ConvictionSetRead,
    read: _ConvictionSetRead,
    *,
    weight: float,
    materiality_bar: float,
) -> ConvictionLeverRead:
    """Delta one raw read against the scripted-FSM baseline (fitness channel).

    The laundering verdict is the probe's UNCHANGED delta convention applied to
    the term: validity-gated, the predicted-supply gain clears the bar while
    the recorded-flags gain does not. Compared UNROUNDED; displayed via the
    standing convention. Gains ride :func:`_signed_relative_gain` — the flags
    head is unclipped, so the supply channel is signed.
    """

    term_value = weight * read.episode_predicted_supply
    term_delta = term_value - weight * baseline.episode_predicted_supply
    if read.tactic == _BASELINE_TACTIC:
        predicted_gain = 0.0
        actual_gain = 0.0
        launders = False
        arithmetic = (
            "the scripted-FSM baseline anchors every delta (gain 0.0 by "
            f"definition); conviction term {weight} x supply = {term_value:.4f}"
        )
    else:
        predicted_gain = _signed_relative_gain(
            baseline.episode_predicted_supply, read.episode_predicted_supply
        )
        actual_gain = _signed_relative_gain(
            baseline.episode_actual_flags, read.episode_actual_flags
        )
        launders = (
            read.validity_passed
            and predicted_gain >= materiality_bar
            and not (actual_gain >= materiality_bar)
        )
        arithmetic = (
            f"predicted supply (episode mean) "
            f"{baseline.episode_predicted_supply:.4f} -> "
            f"{read.episode_predicted_supply:.4f} ({_format_gain(predicted_gain)} "
            f"vs the {materiality_bar:.0%} bar); recorded flags (episode mean) "
            f"{baseline.episode_actual_flags:.4f} -> "
            f"{read.episode_actual_flags:.4f} ({_format_gain(actual_gain)}); "
            f"conviction term {weight} x supply = {term_value:.4f} "
            f"(delta {term_delta:+.4f} vs the scripted-FSM baseline)"
        )
    return ConvictionLeverRead(
        label=read.label,
        tactic=read.tactic,
        games=read.games,
        meetings=read.meetings,
        validity_passed=read.validity_passed,
        referee_passed=read.referee_passed,
        supply_floors_passed=read.supply_floors_passed,
        mean_score=round(read.mean_score, 2),
        mean_episode_predicted_supply=round(read.episode_predicted_supply, 4),
        mean_episode_actual_flags=round(read.episode_actual_flags, 4),
        conviction_term=round(term_value, 4),
        conviction_term_delta=round(term_delta, 4),
        predicted_supply_gain=_display_gain(predicted_gain),
        actual_supply_gain=_display_gain(actual_gain),
        predicted_flags_per_meeting=round(read.predicted_flags_per_meeting, 4),
        actual_flags_per_meeting=round(read.actual_flags_per_meeting, 4),
        predicted_converting_share=round(read.predicted_converting_share, 4),
        predicted_mean_conversion_prob=round(read.predicted_mean_conversion_prob, 4),
        actual_converting_share=round(read.actual_converting_share, 4),
        prescreen_flags_pass=read.prescreen_flags_pass,
        prescreen_conversion_pass=read.prescreen_conversion_pass,
        prescreen_floors_pass=read.prescreen_floors_pass,
        prescreen_advisory_only=read.prescreen_advisory_only,
        launders_supply=launders,
        materiality_arithmetic=arithmetic,
    )


def _build_gate_check(
    reads: Sequence[ConvictionLeverRead],
    *,
    prescreen_is_gating: bool,
    roster_key: str,
) -> ConvictionGateCheck:
    """The composed-gate laundering check over every probed policy.

    The standing BASELINE-RELATIVE gate convention: a predicted-PASS /
    recorded-FAIL divergence is LAUNDERING only when the honest scripted
    baseline does not share it — a divergence the baseline shows too is the
    substrate speaking (the model predicts real-path supply; this substrate
    mints none), named as ``substrate_divergent``, never dressed up as a
    lever flip. On a non-9p2i ``roster_key`` the verdict carries the
    diagnostic caveat the read docstring promises: the committed pre-screen's
    pins are the baseline-6 9p2i floors as shipped (there is no other
    committed pre-screen), so its side of the comparison is a 9p2i-pinned
    prediction against this roster's recorded floors.
    """

    baseline = next((read for read in reads if read.tactic == _BASELINE_TACTIC), None)
    if baseline is None:
        raise ValueError(
            "the gate check needs the scripted-FSM baseline read — no "
            f"{_BASELINE_TACTIC!r} entry in the reads"
        )
    baseline_diverges = (
        baseline.validity_passed
        and baseline.prescreen_floors_pass
        and not baseline.supply_floors_passed
    )
    divergent = tuple(
        read.tactic
        for read in reads
        if read.validity_passed
        and read.prescreen_floors_pass
        and not read.supply_floors_passed
    )
    laundered = () if baseline_diverges else divergent
    substrate_divergent = divergent if baseline_diverges else ()
    false_blocked = tuple(
        read.tactic
        for read in reads
        if read.validity_passed
        and not read.prescreen_floors_pass
        and read.supply_floors_passed
    )
    if laundered:
        verdict = (
            "PREDICTION-LAUNDERED: the committed pre-screen's predicted floors "
            f"PASS for {', '.join(laundered)} while the recorded supply floors "
            "FAIL and the honest baseline shows no such divergence — "
            "adversarial play flipped the predicted gate; the 18.24 protocol "
            "must not spend (or be mis-read to select) on the pre-screen "
            "verdict for these families without a recorded-bytes confirm"
        )
    elif substrate_divergent:
        verdict = (
            "SUBSTRATE-DIVERGENT: the committed pre-screen's predicted floors "
            f"PASS for {', '.join(substrate_divergent)} while the recorded "
            "floors FAIL — the HONEST baseline shares the divergence, so no "
            "lever flipped the predicted gate; the model predicts the "
            "real-path supply economy it was fit on while this substrate's "
            "meetings mint no flags in bytes. A pre-screen PASS is real-path "
            "spend advice ONLY on such a substrate — never a recorded-floor "
            "read"
        )
    else:
        verdict = (
            "no laundering: no validity-passing policy's predicted floors pass "
            "where the recorded floors fail — the committed pre-screen cannot "
            "spend a real eval the recorded referee would refuse, on this "
            "substrate at this scale"
        )
    if roster_key != _PRESCREEN_PINS_ROSTER:
        verdict += (
            f" [diagnostic on {roster_key}: the committed pre-screen's pins "
            f"are the baseline-6 {_PRESCREEN_PINS_ROSTER} floors as shipped — "
            "there is no other committed pre-screen — so this gate read "
            f"compares a {_PRESCREEN_PINS_ROSTER}-pinned prediction against "
            f"{roster_key}-recorded floors]"
        )
    return ConvictionGateCheck(
        prescreen_is_gating=prescreen_is_gating,
        laundered=laundered,
        substrate_divergent=substrate_divergent,
        false_blocked=false_blocked,
        verdict=verdict,
    )


def _build_conviction_findings(
    reads: Sequence[ConvictionLeverRead],
    *,
    gate_check: ConvictionGateCheck,
    roster_key: str,
) -> tuple[ConvictionPathFinding, ...]:
    """Promote every material conviction-path seam to a NAMED finding."""

    findings: list[ConvictionPathFinding] = []
    for read in reads:
        if read.tactic == _BASELINE_TACTIC:
            continue
        if read.launders_supply:
            findings.append(
                ConvictionPathFinding(
                    mechanism="conviction-supply-laundering",
                    tactic=read.tactic,
                    label=read.label,
                    behavioral_cause=(
                        f"{read.label}: the conviction term pays fitness for "
                        "PREDICTED evidence supply this play never mints — "
                        f"predicted flags/meeting "
                        f"{read.predicted_flags_per_meeting:.3f} vs recorded "
                        f"{read.actual_flags_per_meeting:.3f} in bytes; the "
                        f"term's inner-fitness delta is "
                        f"{read.conviction_term_delta:+.4f}"
                    ),
                    materiality_arithmetic=read.materiality_arithmetic,
                    recommended_guard=(
                        "condition (or cap) the conviction term on "
                        "recorded-bytes confirmation for this lever family "
                        "before any conviction-weighted fitness selects — "
                        "routed to the 18.24 protocol, never self-served "
                        "(training/conviction/ + harness.py are probed, not "
                        "edited)"
                    ),
                    blocker=(
                        f"conviction-supply-laundering[{read.tactic},"
                        f"{roster_key}]: {read.materiality_arithmetic}"
                    ),
                )
            )
        if read.tactic in gate_check.laundered:
            findings.append(
                ConvictionPathFinding(
                    mechanism="prescreen-gate-laundering",
                    tactic=read.tactic,
                    label=read.label,
                    behavioral_cause=(
                        f"{read.label}: the committed pre-screen's predicted "
                        "floors PASS while the recorded supply floors FAIL "
                        "and the honest baseline shows no such divergence — "
                        "adversarial play flipped the predicted gate (flagged "
                        "regardless of magnitude, the standing gate-flip "
                        "convention)"
                    ),
                    materiality_arithmetic=read.materiality_arithmetic,
                    recommended_guard=(
                        "the 18.24 protocol must pair every pre-screen PASS "
                        "for this family with a recorded-bytes floor read "
                        "before spending — routed, never self-served"
                    ),
                    blocker=(
                        f"prescreen-gate-laundering[{read.tactic},{roster_key}]: "
                        "predicted floors PASS / recorded floors FAIL, not "
                        "shared by the honest baseline"
                    ),
                )
            )
    if gate_check.substrate_divergent:
        baseline = next(read for read in reads if read.tactic == _BASELINE_TACTIC)
        affected = "+".join(gate_check.substrate_divergent)
        findings.append(
            ConvictionPathFinding(
                mechanism="prescreen-substrate-divergence",
                tactic=affected,
                label="composed-gate substrate divergence",
                behavioral_cause=(
                    "the committed pre-screen's predicted floors PASS while "
                    f"the recorded floors FAIL for {affected} — the HONEST "
                    "scripted baseline shares the divergence, so no lever "
                    "flipped the predicted gate; the model predicts the "
                    "real-path supply economy it was fit on while this "
                    "substrate's meetings mint no flags in bytes "
                    "(prediction-vs-substrate, not lever laundering)"
                ),
                materiality_arithmetic=(
                    "honest baseline: predicted flags/meeting "
                    f"{baseline.predicted_flags_per_meeting:.3f} + predicted "
                    f"converting share {baseline.predicted_converting_share:.3f} "
                    "clear the committed pins while recorded flags/meeting = "
                    f"{baseline.actual_flags_per_meeting:.3f} (a gate "
                    "divergence is flagged regardless of magnitude — the "
                    "standing gate-flip convention)"
                ),
                recommended_guard=(
                    "the 18.24 protocol must consume a pre-screen PASS as "
                    "real-path spend advice ONLY — never as a recorded-floor "
                    "read on a substrate whose meetings cannot mint flags; "
                    "pair every gating use with a recorded-bytes floor read — "
                    "routed, never self-served"
                ),
                blocker=(
                    f"prescreen-substrate-divergence[{affected},{roster_key}]: "
                    "predicted floors PASS / recorded floors FAIL, shared by "
                    "the honest baseline — a pre-screen PASS is real-path "
                    "spend advice only on this substrate"
                ),
            )
        )
    return tuple(findings)


def _standing_blockers(probe: GoodhartProbeReport) -> tuple[str, ...]:
    """Name the standing probe's above-bar exploits as 18.24 blockers."""

    return tuple(
        f"{exploit.mechanism}[{probe.roster_key}] (standing probe): mean_score "
        f"{exploit.score_baseline:.2f} -> {exploit.score_champion:.2f} "
        f"(delta {exploit.delta:+.2f}, above the {probe.materiality_bar:.0%} "
        "bar) — no selection reads this roster's score until the recommended "
        "floor lands"
        for exploit in probe.exploits
    )


def run_conviction_path_probe(
    *,
    config: ESConfig,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    baseline_id: str = "baseline-8",
    materiality_bar: float = 0.25,
    conviction_artifact_dir: Path | None = None,
    conviction_weight: float | None = None,
    use_counter: ConvictionUseCounter | None = None,
    meeting_runner_factory: MeetingRunnerFactory | None = None,
) -> ConvictionPathProbeReport:
    """Run the 18.18 re-probe: the standing probe + the conviction-path arms.

    Runs :func:`run_goodhart_probe` UNCHANGED (the standing bars; the anchors
    reproduce), then re-rolls the scripted-FSM baseline, every forced lever,
    and the ES champion corner through the conviction arms: the term read
    (predicted supply priced exactly as ``inner_episode_fitness`` pays it),
    the predicted-vs-actual side-by-side off the recorded bytes, and the
    COMMITTED pre-screen beside the recorded supply floors (the composed-gate
    laundering check). ``conviction_weight`` / ``conviction_artifact_dir``
    default to the committed 18.16 integration's own
    (``DEFAULT_CONVICTION_WEIGHT`` / ``CONVICTION_ARTIFACT_DIR``); a committed
    NO-GO verdict fails loud — the arms attack the LIVE term, and under NO-GO
    there is nothing to probe. ONE :class:`ConvictionUseCounter` threads
    through the term read and the pre-screen (pass ``use_counter`` to share a
    run-wide counter; the committed cap is cumulative). Deterministic under
    ``config.seed`` (env + referee + conviction model are pure functions of
    the seed and the frozen weights).
    """

    # Local import: training/bakeoff/harness.py imports THIS module at module
    # scope (the probe entry points it drives), so the committed 18.16
    # integration is consumed through a function-local import — the
    # _build_entrants acyclic-graph precedent. The arms attack the EXACT
    # committed instrument (term + pre-screen), never a mirrored constant
    # that could drift.
    from training.bakeoff.harness import (
        CONVICTION_ARTIFACT_DIR,
        DEFAULT_CONVICTION_WEIGHT,
        load_conviction_fitness_term,
    )

    artifact_dir = (
        conviction_artifact_dir
        if conviction_artifact_dir is not None
        else CONVICTION_ARTIFACT_DIR
    )
    weight = (
        DEFAULT_CONVICTION_WEIGHT if conviction_weight is None else conviction_weight
    )
    term = load_conviction_fitness_term(
        artifact_dir, use_counter=use_counter, weight=weight
    )
    if term is None:
        raise ValueError(
            f"the committed conviction verdict under {artifact_dir} ships no "
            "fitness term (NO-GO: fitness_term='absent') — the conviction-path "
            "arms attack the LIVE 18.16 term, so there is nothing to probe; "
            "run run_goodhart_probe for the standing bars instead (no silent "
            "fallbacks)"
        )
    uses_before = term.use_counter.uses

    probe = run_goodhart_probe(
        config=config,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        baseline_id=baseline_id,
        materiality_bar=materiality_bar,
        meeting_runner_factory=meeting_runner_factory,
    )
    if not probe.champion_genome:
        raise ValueError(
            "run_goodhart_probe returned no champion genome — the ES champion "
            "corner cannot be re-read through the conviction arms"
        )

    reader = _ConvictionArmReader(
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        fitness_seeds=config.fitness_seeds,
        baseline_id=baseline_id,
        term=term,
        conviction_artifact_dir=artifact_dir,
        meeting_runner_factory=meeting_runner_factory,
    )
    raws = [reader.read(None, label="scripted-FSM baseline", tactic=_BASELINE_TACTIC)]
    for tactic in _SWEEP_TACTICS:
        raws.append(
            reader.read(
                _forced_genome(tactic), label=f"forced-{tactic} lever", tactic=tactic
            )
        )
    raws.append(
        reader.read(probe.champion_genome, label="ES champion", tactic=_CHAMPION_TACTIC)
    )

    baseline_raw = raws[0]
    reads = tuple(
        _build_conviction_read(
            baseline_raw, raw, weight=weight, materiality_bar=materiality_bar
        )
        for raw in raws
    )
    gate_check = _build_gate_check(
        reads,
        prescreen_is_gating=term.verdict.prescreen_role == "gating",
        roster_key=probe.roster_key,
    )
    findings = _build_conviction_findings(
        reads, gate_check=gate_check, roster_key=probe.roster_key
    )
    blockers = tuple(finding.blocker for finding in findings) + _standing_blockers(
        probe
    )
    verdict: Literal["HELD", "EXPLOITS_FOUND"] = (
        "EXPLOITS_FOUND" if blockers else "HELD"
    )

    uses = term.use_counter.uses - uses_before
    meetings_read = sum(raw.meetings for raw in raws)
    consumption_note = (
        "Conviction-model consumption, metered on the ONE shared sha-keyed "
        f"counter ({term.weights_sha256[:12]}…): {uses} predicted meetings "
        f"this probe over {meetings_read} recorded meetings (each predicted "
        "once per committed consumption path — the fitness-term read via "
        "ConvictionFitnessTerm.predict_meeting and the composed-gate read via "
        f"conviction_prescreen); counter total {term.use_counter.uses} of the "
        f"committed cap {term.use_counter.cap.max_uses} "
        f"({term.use_counter.uses / term.use_counter.cap.max_uses:.2%})."
    )
    return ConvictionPathProbeReport(
        roster_key=probe.roster_key,
        baseline_id=baseline_id,
        conviction_weights_sha256=term.weights_sha256,
        conviction_model_verdict=term.verdict.verdict,
        prescreen_role=term.verdict.prescreen_role,
        conviction_weight=weight,
        conversion_threshold=CONVICTION_CONVERSION_DECISION_THRESHOLD,
        materiality_bar=materiality_bar,
        probe=probe,
        reads=reads,
        gate_check=gate_check,
        findings=findings,
        blockers=blockers,
        verdict=verdict,
        conviction_uses=uses,
        conviction_uses_total=term.use_counter.uses,
        conviction_max_uses=term.use_counter.cap.max_uses,
        consumption_note=consumption_note,
    )


def reread_carried_4p1i_exploit(
    report: ConvictionPathProbeReport,
) -> CarriedExploitReread:
    """Re-read the carried 4p1i ``d4-contest-farming`` exploit (Task 18.18).

    The audit-carried finding (audits/audit-phase-17-close.md §6) binds a
    re-probe BEFORE any 4p1i-scored selection: this reads the
    forced-``emergency`` lever out of a 4p1i conviction-path report and states
    the carried numbers beside the fresh ones with the materiality arithmetic.
    ``still_above_bar`` DEFERS to the standing probe's own exploit list (the
    authoritative UNROUNDED materiality gate — ``_build_exploits`` thresholds
    on exact per-game set means): the carried mechanism is above the bar iff
    the standing report still names it, never re-decided off the
    display-rounded ``LeverResult`` fields (a 4-decimal boundary could
    disagree with the unrounded gate). Raises on a non-4p1i report (the
    finding is roster-specific) and on a sweep missing the lever (the net
    must never silently shrink).
    """

    if report.roster_key != _CARRIED_ROSTER:
        raise ValueError(
            f"the carried {_CARRIED_MECHANISM} exploit is a {_CARRIED_ROSTER} "
            f"finding; got a {report.roster_key!r} report — re-read it on the "
            "reference roster"
        )
    lever = next(
        (
            entry
            for entry in report.probe.lever_sweep
            if entry.tactic == _CARRIED_TACTIC
        ),
        None,
    )
    if lever is None:
        raise ValueError(
            f"the standing sweep carries no forced-{_CARRIED_TACTIC} lever — "
            "the reachability net silently shrank"
        )
    read = next(
        (entry for entry in report.reads if entry.tactic == _CARRIED_TACTIC), None
    )
    if read is None:
        raise ValueError(
            f"the conviction arms carry no forced-{_CARRIED_TACTIC} read — "
            "the re-probe did not cover the carried lever"
        )
    # The authoritative call: the standing probe already ran the UNROUNDED
    # materiality gate and named the mechanism iff it cleared (validity-gated,
    # deduped by mechanism) — defer to it rather than re-deciding off the
    # display-rounded lever row.
    still_above = any(
        exploit.mechanism == _CARRIED_MECHANISM for exploit in report.probe.exploits
    )
    arithmetic = (
        f"carried (17.15, baseline-5 floors): mean_score "
        f"{_CARRIED_BASELINE_MEAN_SCORE:.2f} -> {_CARRIED_LEVER_MEAN_SCORE:.2f} "
        f"({_CARRIED_RELATIVE_GAIN:+.1%}); re-read ({report.baseline_id} "
        f"substrate, conviction path live): {report.probe.baseline_mean_score:.2f} "
        f"-> {lever.mean_score:.2f} ({lever.relative_gain:+.1%} vs the "
        f"{report.materiality_bar:.0%} bar)"
    )
    if still_above:
        verdict = (
            "the carried exploit REPRODUCES above the bar at the current "
            "substrate — the blocker stands: no 4p1i-scored selection before "
            "the routed D4 contest floor lands"
        )
    else:
        verdict = (
            "the carried exploit no longer clears the bar at the current "
            "substrate — record the closure with this arithmetic before any "
            "4p1i-scored selection"
        )
    return CarriedExploitReread(
        mechanism=_CARRIED_MECHANISM,
        tactic=_CARRIED_TACTIC,
        roster_key=_CARRIED_ROSTER,
        carried_baseline_mean_score=_CARRIED_BASELINE_MEAN_SCORE,
        carried_lever_mean_score=_CARRIED_LEVER_MEAN_SCORE,
        carried_relative_gain=_CARRIED_RELATIVE_GAIN,
        reread_baseline_mean_score=report.probe.baseline_mean_score,
        reread_lever_mean_score=lever.mean_score,
        reread_relative_gain=lever.relative_gain,
        reread_moving_term=lever.moving_term,
        still_above_bar=still_above,
        conviction_term_delta=read.conviction_term_delta,
        conviction_launders_supply=read.launders_supply,
        materiality_arithmetic=arithmetic,
        verdict=verdict,
    )


__all__ = [
    "CarriedExploitReread",
    "ConvictionGateCheck",
    "ConvictionLeverRead",
    "ConvictionPathFinding",
    "ConvictionPathProbeReport",
    "GoodhartProbeReport",
    "LeverResult",
    "ProbeBudget",
    "ProbeExploit",
    "TraceImprovement",
    "build_probe_selector",
    "probe_genome_length",
    "reread_carried_4p1i_exploit",
    "run_conviction_path_probe",
    "run_goodhart_probe",
]
