"""The real-path re-rank recorder (Task 18.17).

Productizes the two real-path selection loops the training-signal decision
adopted: (B) per-generation top-K re-rank — given K candidate genomes and a seed
list, record each candidate on the real provider path and score it through the
committed CLIs — and (C) champion-trace re-rank — the same over an
:attr:`training.bakeoff.es.ESResult.champion_trace`.

Mechanism. For each candidate this records one game per seed through
:func:`eval.balance_eval.run_tournament_eval` (the ``meeting_runner_factory``
seam) into a throwaway per-candidate directory under ``work_dir``, with two
guards the headless recorder lacks: a per-meeting wall-clock timeout proxy around
the runner (headless meetings are deadline-free — ``orchestrator/game.py``
:data:`~orchestrator.game.HEADLESS_MEETING_DEADLINES`, so a hung provider would
otherwise stall the loop forever) and a per-seed crash-retry budget that
re-records a timed-out / crashed / degraded seed with ``force=True``. Each game's
``game_over`` record is stamped with the candidate's
:class:`~orchestrator.replay.TacticalPolicyStamp`; the stamp written into the row
is READ BACK from the recorded bytes (:func:`~orchestrator.replay.read_tactical_policy_stamp`),
never echoed from the launch config — the Task 17.14 discipline. Each recording
directory is then scored through the committed library entry points
(:func:`eval.validity.run_validity_gate`, :func:`eval.watchability.compute_watchability`,
and the core ``scripts/measure_baseline.py`` fold), and one machine-readable
ranking row per candidate is emitted to ``ranking_path`` as JSONL — the committed
truth. The recordings under ``work_dir`` are throwaway working artifacts.

Honesty note (provider nondeterminism). Real-path ranks are a SELECTION signal,
NOT a fitness. Two runs of the same genome on the real provider may score
differently, which selection tolerates but the ES fitness-purity contract
(``training/bakeoff/es.py:51-55`` — a fitness MUST be a pure, deterministic
function of the genome) does not. These scores MUST NEVER be written back into an
ES fitness channel; routing them into :func:`~training.bakeoff.es.evolve` would
break the double-run determinism digest. The committed output is the ranking
JSONL; nothing here feeds :func:`~training.bakeoff.es.evolve`.

Public surface (stable — downstream tasks import these):
:class:`RealPathCandidate`, :class:`RealPathRerankConfig`,
:class:`RealPathSeedTelemetry`, :class:`RealPathRerankRow`,
:class:`RealPathRerankResult`, :func:`candidates_from_champion_trace`,
:func:`run_realpath_rerank`, the :class:`RealPathRerankError` family, and the
``SCHEMA_VERSION`` / ``MODE_*`` / ``DEFAULT_*`` constants.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from agents.base import AgentInterface
from agents.tactical.features import weights_to_hex_json
from engine.entities import PlayerId
from engine.world import Map, WorldState, load_canonical_map
from eval.balance_eval import _resolve_game_budget, run_tournament_eval
from eval.validity import ValidityGateReport, run_validity_gate
from eval.watchability import WatchabilityReport, compute_watchability
from meetings.manager import MeetingTrigger
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    AgentFactory,
    MeetingArtifacts,
    MeetingRunner,
    build_default_meeting_runner,
)
from orchestrator.replay import TacticalPolicyStamp, read_tactical_policy_stamp
from training.bakeoff.es import ESResult
from training.bakeoff.harness import BakeoffPolicy, build_candidate_factory
from training.bakeoff.policy_es import build_masked_mlp_policy
from training.bakeoff.utility_es import ENCODER_VERSION as _UTILITY_ENCODER_VERSION
from training.bakeoff.utility_es import build_utility_scorer_policy

# ``scripts/`` is a bare-module namespace (no ``__init__.py``): the committed core
# CLI (``scripts/measure_baseline.py``) is importable only with ``scripts/`` on
# ``sys.path`` (mypy resolves it via ``mypy_path = "scripts"``). Mirror the
# established bootstraps: tests/scripts/conftest.py and
# scripts/measure_baseline.py:76-78.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import measure_baseline  # noqa: E402

# --------------------------------------------------------------------------- #
# Constants.                                                                   #
# --------------------------------------------------------------------------- #

SCHEMA_VERSION: Final[str] = "realpath-rerank-v1"

# The re-rank imposes its OWN per-meeting wall-clock deadline because headless
# meetings run deadline-free (orchestrator/game.py:397-399).
DEFAULT_MEETING_TIMEOUT_SECONDS: Final[float] = 300.0

# Continuity with the operator runbook's AILIBI_SEED_MAX_ATTEMPTS >= 8 (the
# real-provider record used a staggered per-seed retry budget of at least 8).
DEFAULT_MAX_ATTEMPTS: Final[int] = 8

# The committed watchability floor block every training consumer pins.
DEFAULT_BASELINE_ID: Final[str] = "baseline-5"

# The 9p2i SELECTION roster (the canonical eval roster the referee floors are
# pinned for), NOT the engine's 4p1i defaults (orchestrator/game.py:120-121):
# the re-rank scores champions on the roster the bake-off selects on.
DEFAULT_NUM_PLAYERS: Final[int] = 9
DEFAULT_NUM_IMPOSTORS: Final[int] = 2
DEFAULT_TASKS_PER_CREWMATE: Final[int] = 2

MODE_TOP_K: Final[str] = "top-k"
MODE_CHAMPION_TRACE: Final[str] = "champion-trace"

# The selection composition mirrors training/bakeoff/goodhart.py:257/269/272-290:
# a validity-failing set scores below any real geomean, and a referee pass
# (supply floors AND integrity) dominates the geomean tie-break.
_INVALID_SELECTION_SCORE: Final[float] = -1.0
_REFEREE_PASS_BONUS: Final[float] = 1000.0

_ROSTER_FILENAME: Final[str] = "roster.json"
_SLUG_EXTRA: Final[str] = "-_"


# --------------------------------------------------------------------------- #
# Exceptions.                                                                  #
# --------------------------------------------------------------------------- #


class RealPathRerankError(RuntimeError):
    """Base error for the real-path re-rank recorder (fail-loud, no fallbacks)."""


class RealPathMeetingTimeoutError(RealPathRerankError):
    """A meeting exceeded the configured per-meeting wall-clock deadline.

    Raised by :class:`_TimeoutMeetingRunner`. ``run_tournament_eval`` re-raises it
    unchanged (its parse-failure fold only recovers ``LLMCallFailure``-carrying
    errors), which is exactly what the re-rank loop needs — the distinct type lets
    :func:`_record_seed` count wall-clock timeouts separately from generic crashes
    in the telemetry, and can never be confused with the meeting manager's
    fail-soft per-turn deadline ``TimeoutError`` (which degrades a turn internally
    and never propagates) or a provider-internal timeout.
    """


class RealPathSeedExhaustedError(RealPathRerankError):
    """A seed failed to record cleanly within the per-seed retry budget.

    Aborts the whole re-rank BEFORE the ranking JSONL is written, so no partial
    committed artifact is ever produced.
    """


class RealPathStampError(RealPathRerankError):
    """A candidate's provenance stamp is missing, non-uniform, or mismatched.

    Covers a genome that does not rebuild the declared encoder, a recording whose
    ``game_over`` bytes carry no stamp, and a read-back ``weights_sha256`` that
    disagrees with the computed genome digest (the Task 17.14 conflation guard).
    """


# --------------------------------------------------------------------------- #
# The per-meeting wall-clock timeout proxy.                                    #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _TimeoutMeetingRunner:
    """A :class:`~orchestrator.game.MeetingRunner` that bounds one meeting's clock.

    Wraps an inner runner's async ``run_meeting`` in :func:`asyncio.wait_for`. The
    proxy runs INSIDE the ``asyncio.run`` loop the orchestrator opens for the
    meeting (``orchestrator/game.py`` ``_drive_async``), so no edit to the game is
    needed. It forwards every keyword verbatim and never mutates ``state``.
    """

    _inner: MeetingRunner
    _timeout_seconds: float

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        try:
            return await asyncio.wait_for(
                self._inner.run_meeting(
                    meeting_id=meeting_id,
                    trigger=trigger,
                    state=state,
                    agents=agents,
                ),
                timeout=self._timeout_seconds,
            )
        except TimeoutError as exc:
            # Python 3.11: asyncio.TimeoutError IS the builtin TimeoutError.
            raise RealPathMeetingTimeoutError(
                f"meeting {meeting_id!r} exceeded {self._timeout_seconds}s wall "
                "clock (headless meetings are deadline-free; "
                "orchestrator/game.py:397-399)"
            ) from exc


# --------------------------------------------------------------------------- #
# Public data models (JSONL row types — frozen, extra='forbid').              #
# --------------------------------------------------------------------------- #


class RealPathCandidate(BaseModel):
    """One genome to re-rank, with the provenance the stamp needs.

    ``label`` is the unique candidate id and the source of the work-subdir slug.
    ``method`` is REQUIRED (no bland default): provenance must be caller-named.
    The utility family (``encoder_version == 'impostor-option-features-v1'``) takes
    no ``hidden`` width; every other family requires ``hidden >= 1`` (never
    defaulted). The five stamp-bound strings are pre-validated against the
    :class:`~orchestrator.replay.TacticalPolicyStamp` field rules (non-blank, no
    ``|`` / newline / CR; replay.py:211-254) so a bad candidate fails HERE.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str
    genome: tuple[float, ...]
    encoder_version: str
    hidden: int | None = None
    policy_id: str
    method: str
    anchor_policy: str = "fsm-default"
    generation_indices: tuple[int, ...] = ()

    @model_validator(mode="after")
    def _validate(self) -> RealPathCandidate:
        if not self.genome:
            raise ValueError(f"candidate {self.label!r}: genome must be non-empty")
        if self.encoder_version == _UTILITY_ENCODER_VERSION:
            if self.hidden is not None:
                raise ValueError(
                    f"candidate {self.label!r}: the utility family "
                    f"({_UTILITY_ENCODER_VERSION!r}) takes no hidden width; got "
                    f"hidden={self.hidden!r}"
                )
        elif self.hidden is None or self.hidden < 1:
            raise ValueError(
                f"candidate {self.label!r}: family {self.encoder_version!r} "
                f"requires hidden >= 1; got hidden={self.hidden!r}"
            )
        for name, value in (
            ("label", self.label),
            ("policy_id", self.policy_id),
            ("method", self.method),
            ("encoder_version", self.encoder_version),
            ("anchor_policy", self.anchor_policy),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be a non-blank token; got {value!r}")
            for forbidden, human in (("|", "pipe"), ("\n", "newline"), ("\r", "CR")):
                if forbidden in value:
                    raise ValueError(
                        f"{name} must be MANIFEST-safe (no {human}); got {value!r}"
                    )
        return self


class RealPathRerankConfig(BaseModel):
    """The roster / budget knobs a re-rank runs under (frozen, extra='forbid').

    Defaults to the 9p2i selection roster. There is deliberately NO ``seeds``
    field: the seed list is a :func:`run_realpath_rerank` parameter (the task
    contract's "given K candidate genomes and a seed list").
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    num_players: int = DEFAULT_NUM_PLAYERS
    num_impostors: int = DEFAULT_NUM_IMPOSTORS
    tasks_per_crewmate: int = DEFAULT_TASKS_PER_CREWMATE
    max_ticks: int = DEFAULT_MAX_TICKS
    baseline_id: str = DEFAULT_BASELINE_ID
    meeting_timeout_seconds: float = DEFAULT_MEETING_TIMEOUT_SECONDS
    max_attempts: int = DEFAULT_MAX_ATTEMPTS

    @model_validator(mode="after")
    def _validate(self) -> RealPathRerankConfig:
        if not self.meeting_timeout_seconds > 0:
            raise ValueError(
                "meeting_timeout_seconds must be > 0; got "
                f"{self.meeting_timeout_seconds!r}"
            )
        if self.max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1; got {self.max_attempts!r}")
        if not 1 <= self.num_impostors < self.num_players:
            raise ValueError(
                "require 1 <= num_impostors < num_players; got "
                f"num_impostors={self.num_impostors!r}, "
                f"num_players={self.num_players!r}"
            )
        if self.tasks_per_crewmate < 1:
            raise ValueError(
                f"tasks_per_crewmate must be >= 1; got {self.tasks_per_crewmate!r}"
            )
        if self.max_ticks < 1:
            raise ValueError(f"max_ticks must be >= 1; got {self.max_ticks!r}")
        if not self.baseline_id.strip():
            raise ValueError(f"baseline_id must be non-blank; got {self.baseline_id!r}")
        return self


class RealPathSeedTelemetry(BaseModel):
    """Per-seed recording telemetry (frozen, extra='forbid').

    ``attempts`` is the total attempts (>= 1) including the successful one;
    ``error_types`` is the failed-attempt exception class names in order, so
    ``len(error_types) == attempts - 1``. ``degraded_recordings`` counts normal
    returns whose replay carried NO ``game_over`` stamp (the real-provider
    parse-fold abort case). ``wall_seconds`` is cumulative monotonic time across
    all attempts, rounded to 3 places.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    attempts: int
    timed_out_attempts: int
    degraded_recordings: int
    error_types: tuple[str, ...]
    wall_seconds: float

    @model_validator(mode="after")
    def _validate(self) -> RealPathSeedTelemetry:
        if self.attempts < 1:
            raise ValueError(f"attempts must be >= 1; got {self.attempts!r}")
        if len(self.error_types) != self.attempts - 1:
            raise ValueError(
                "error_types must record one entry per failed attempt "
                f"(len == attempts - 1); got {len(self.error_types)} entries for "
                f"attempts={self.attempts!r}"
            )
        for count in (self.timed_out_attempts, self.degraded_recordings):
            if count < 0:
                raise ValueError("attempt counters must be >= 0")
        if self.wall_seconds < 0:
            raise ValueError(f"wall_seconds must be >= 0; got {self.wall_seconds!r}")
        return self


class RealPathRerankRow(BaseModel):
    """One candidate's committed ranking row (frozen, extra='forbid').

    ``stamp`` is the READ-BACK stamp (recovered from the recorded bytes), never
    the in-memory launch stamp. Core metrics are flattened scalars (no ``scripts/``
    type in the row schema); a ``float | None`` core field stays ``None`` when its
    denominator is empty and is never coerced to ``0.0``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = SCHEMA_VERSION
    label: str
    mode: str
    generation_indices: tuple[int, ...]
    stamp: TacticalPolicyStamp
    weights_sha256: str
    stamp_verified_games: int
    stamp_uniform: bool
    stamp_equals_computed_digest: bool
    seeds: tuple[int, ...]
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    max_ticks: int
    baseline_id: str
    meeting_timeout_seconds: float
    max_attempts: int
    seed_telemetry: tuple[RealPathSeedTelemetry, ...]
    validity: ValidityGateReport
    watchability: WatchabilityReport
    core_games_total: int
    core_impostor_win_rate: float
    core_ejection_accuracy: float | None
    core_genuine_class_conversion: float | None
    core_meeting_rate: float | None
    validity_passed: bool
    referee_passed: bool
    selection_score: float
    rank: int

    def to_json_line(self) -> str:
        """Serialize to a single, key-sorted JSONL line (the committed row form)."""

        return json.dumps(self.model_dump(mode="json"), sort_keys=True)


class RealPathRerankResult(BaseModel):
    """The full re-rank verdict (frozen, extra='forbid').

    ``rows`` are rank-ascending and never empty (candidates are validated
    non-empty). ``ranking_path`` / ``work_dir`` are the emitted JSONL path and the
    throwaway recording root.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: str
    ranking_path: str
    work_dir: str
    seeds: tuple[int, ...]
    config: RealPathRerankConfig
    rows: tuple[RealPathRerankRow, ...]

    def top(self) -> RealPathRerankRow:
        """The rank-1 row (rows are never empty)."""

        return self.rows[0]


# --------------------------------------------------------------------------- #
# Private helpers.                                                             #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _CandidatePayload:
    """Per-candidate results collected before the final ranking pass."""

    candidate: RealPathCandidate
    stamp: TacticalPolicyStamp
    digest: str
    verified: int
    telemetry: tuple[RealPathSeedTelemetry, ...]
    validity: ValidityGateReport
    watchability: WatchabilityReport
    core: measure_baseline.BaselineMeasurementReport


def _genome_digest(genome: Sequence[float]) -> str:
    """The byte-addressable genome id — identical to write_candidate_artifact.

    ``sha256`` over ``weights_to_hex_json(genome) + "\\n"`` (harness.py:858-861),
    so an in-memory genome's digest matches a committed artifact's sidecar without
    needing a committed directory.
    """

    payload = (weights_to_hex_json(genome) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _candidate_stamp(candidate: RealPathCandidate) -> TacticalPolicyStamp:
    """Build the launch stamp, computing ``weights_sha256`` over the genome bytes."""

    return TacticalPolicyStamp(
        policy_id=candidate.policy_id,
        method=candidate.method,
        encoder_version=candidate.encoder_version,
        weights_sha256=_genome_digest(candidate.genome),
        anchor_policy=candidate.anchor_policy,
    )


def _build_agent_factory(
    candidate: RealPathCandidate, *, game_map: Map
) -> AgentFactory:
    """Rebuild the candidate's agent factory, dispatching on ``encoder_version``.

    Built ONCE per candidate before the seed loop, so a bad genome fails
    immediately (and is never retried).
    """

    policy: BakeoffPolicy
    if candidate.encoder_version == _UTILITY_ENCODER_VERSION:
        policy = build_utility_scorer_policy(candidate.genome, game_map=game_map)
    else:
        hidden = candidate.hidden
        if hidden is None:  # unreachable: the model validator requires it
            raise RealPathStampError(
                f"candidate {candidate.label!r}: family "
                f"{candidate.encoder_version!r} requires a hidden width"
            )
        policy = build_masked_mlp_policy(
            candidate.genome, game_map=game_map, hidden=hidden
        )
    if policy.encoder_version != candidate.encoder_version:
        raise RealPathStampError(
            f"candidate {candidate.label!r}: rebuilt policy encoder_version "
            f"{policy.encoder_version!r} != declared {candidate.encoder_version!r}"
        )
    return build_candidate_factory(policy, game_map=game_map)


def _timeout_runner_factory(
    base_factory: Callable[[], MeetingRunner] | None,
    *,
    timeout_seconds: float,
    num_players: int,
) -> Callable[[], MeetingRunner]:
    """A zero-arg factory yielding a FRESH timeout-wrapped runner per game.

    The inner runner is ``base_factory()`` when supplied, else the default
    roster-scaled runner (identical to ``run_tournament_eval``'s ``None`` path).
    """

    def factory() -> MeetingRunner:
        inner: MeetingRunner
        if base_factory is not None:
            inner = base_factory()
        else:
            inner = build_default_meeting_runner(
                budget=_resolve_game_budget(num_players=num_players)
            )
        return _TimeoutMeetingRunner(inner, timeout_seconds)

    return factory


def _write_roster_json(directory: Path, config: RealPathRerankConfig) -> None:
    """Write ``roster.json`` the scoring CLIs read (mirrors harness.py:979-990)."""

    (directory / _ROSTER_FILENAME).write_text(
        json.dumps(
            {
                "num_players": config.num_players,
                "num_impostors": config.num_impostors,
                "tasks_per_crewmate": config.tasks_per_crewmate,
            }
        )
    )


def _drop_audit_sidecars(directory: Path) -> None:
    """Drop the per-game ``*.audit.jsonl`` sidecars (mirrors harness.py:993-998).

    The referee / validity / core seed glob (``replay-seed-*.jsonl``) trips on
    them, so they must go before scoring.
    """

    for sidecar in directory.glob("*.audit.jsonl"):
        sidecar.unlink()


def _record_seed(
    *,
    seed: int,
    label: str,
    candidate_dir: Path,
    game_map: Map,
    agent_factory: AgentFactory,
    stamp: TacticalPolicyStamp,
    config: RealPathRerankConfig,
    base_meeting_runner_factory: Callable[[], MeetingRunner] | None,
) -> RealPathSeedTelemetry:
    """Record one seed with the per-seed crash-retry budget (fail-loud on exhaust).

    A retry (``attempt > 1``) records with ``force=True`` so a crashed / partial
    replay is truncated and cleanly overwritten. A timeout is a distinct,
    retryable outcome; any other ``Exception`` (provider / transport / engine
    crash) is presumed transient on the real path and retried; a normal return
    whose replay carries NO ``game_over`` stamp (the parse-fold abort) is a
    degraded recording and retried. ``KeyboardInterrupt`` / ``SystemExit`` are not
    ``Exception`` and propagate.
    """

    timed_out = 0
    degraded = 0
    error_types: list[str] = []
    last_exc: BaseException | None = None
    start = time.monotonic()
    replay_path = candidate_dir / f"replay-seed-{seed}.jsonl"
    for attempt in range(1, config.max_attempts + 1):
        runner_factory = _timeout_runner_factory(
            base_meeting_runner_factory,
            timeout_seconds=config.meeting_timeout_seconds,
            num_players=config.num_players,
        )
        try:
            run_tournament_eval(
                seeds=[seed],
                output_dir=candidate_dir,
                game_map=game_map,
                agent_factory=agent_factory,
                num_players=config.num_players,
                num_impostors=config.num_impostors,
                tasks_per_crewmate=config.tasks_per_crewmate,
                max_ticks=config.max_ticks,
                force=attempt > 1,
                tactical_policy_stamp=stamp,
                meeting_runner_factory=runner_factory,
            )
        except RealPathMeetingTimeoutError as exc:
            timed_out += 1
            error_types.append(type(exc).__name__)
            last_exc = exc
            continue
        except Exception as exc:  # noqa: BLE001 - retried; exhaustion is fail-loud
            error_types.append(type(exc).__name__)
            last_exc = exc
            continue
        if read_tactical_policy_stamp(replay_path) is None:
            degraded += 1
            error_types.append("DegradedRecording")
            last_exc = RealPathRerankError(
                f"seed {seed} recording aborted before game_over (parse-fold): "
                "no stamp on bytes"
            )
            continue
        return RealPathSeedTelemetry(
            seed=seed,
            attempts=attempt,
            timed_out_attempts=timed_out,
            degraded_recordings=degraded,
            error_types=tuple(error_types),
            wall_seconds=round(time.monotonic() - start, 3),
        )
    raise RealPathSeedExhaustedError(
        f"candidate {label!r} seed {seed} exhausted {config.max_attempts} "
        f"attempts ({timed_out} timeouts, {degraded} degraded recordings); "
        f"last error {type(last_exc).__name__}: {last_exc}"
    ) from last_exc


def _verify_stamps(
    candidate_dir: Path,
    *,
    seeds: Sequence[int],
    expected_digest: str,
    label: str,
) -> tuple[TacticalPolicyStamp, int]:
    """Read every seed's stamp back from bytes and enforce the 17.14 invariants.

    Fails loud (RealPathStampError) on a missing stamp, a read-back
    ``weights_sha256`` that disagrees with the computed genome digest, or a
    non-uniform stamp across seeds. Returns the uniform stamp and the verified
    game count.
    """

    stamps: list[TacticalPolicyStamp] = []
    for seed in seeds:
        replay_path = candidate_dir / f"replay-seed-{seed}.jsonl"
        stamp = read_tactical_policy_stamp(replay_path)
        if stamp is None:
            raise RealPathStampError(
                f"candidate {label!r} seed {seed}: replay carries no tactical "
                f"policy stamp on its game_over record ({replay_path})"
            )
        if stamp.weights_sha256 != expected_digest:
            raise RealPathStampError(
                f"candidate {label!r} seed {seed}: read-back weights_sha256 "
                f"{stamp.weights_sha256!r} != computed genome digest "
                f"{expected_digest!r} (17.14 conflation guard)"
            )
        stamps.append(stamp)
    first = stamps[0]
    if any(stamp.model_dump() != first.model_dump() for stamp in stamps[1:]):
        raise RealPathStampError(
            f"candidate {label!r}: read-back stamps are not uniform across seeds"
        )
    return first, len(stamps)


def _selection_score(
    validity: ValidityGateReport, watchability: WatchabilityReport
) -> float:
    """The composed selection scalar (mirrors goodhart._composed_referee_fitness).

    Invalid sentinel when the HARD validity gate fails; otherwise ``mean_score``
    plus a dominating bonus iff the whole referee passes (supply floors AND
    integrity). The bare geomean is Goodhart-able and is only the tie-break among
    referee-failing candidates.
    """

    if not validity.passed:
        return _INVALID_SELECTION_SCORE
    bonus = _REFEREE_PASS_BONUS if watchability.referee_passed else 0.0
    return watchability.mean_score + bonus


def _safe_slug(label: str) -> str:
    """A filesystem-safe slug: keep ``[-a-zA-Z0-9_]``, replace anything else."""

    return "".join(
        ch if (ch.isascii() and ch.isalnum()) or ch in _SLUG_EXTRA else "-"
        for ch in label
    )


def _build_row(
    payload: _CandidatePayload,
    *,
    mode: str,
    seeds: tuple[int, ...],
    config: RealPathRerankConfig,
    selection_score: float,
    rank: int,
) -> RealPathRerankRow:
    core = payload.core
    return RealPathRerankRow(
        label=payload.candidate.label,
        mode=mode,
        generation_indices=payload.candidate.generation_indices,
        stamp=payload.stamp,
        weights_sha256=payload.digest,
        stamp_verified_games=payload.verified,
        stamp_uniform=True,
        stamp_equals_computed_digest=True,
        seeds=seeds,
        num_players=config.num_players,
        num_impostors=config.num_impostors,
        tasks_per_crewmate=config.tasks_per_crewmate,
        max_ticks=config.max_ticks,
        baseline_id=config.baseline_id,
        meeting_timeout_seconds=config.meeting_timeout_seconds,
        max_attempts=config.max_attempts,
        seed_telemetry=payload.telemetry,
        validity=payload.validity,
        watchability=payload.watchability,
        core_games_total=core.games_total,
        core_impostor_win_rate=core.impostor_win_rate,
        core_ejection_accuracy=core.ejection_accuracy,
        core_genuine_class_conversion=core.genuine_class_conversion,
        core_meeting_rate=core.meeting_rate,
        validity_passed=payload.validity.passed,
        referee_passed=payload.watchability.referee_passed,
        selection_score=selection_score,
        rank=rank,
    )


# --------------------------------------------------------------------------- #
# Public functions.                                                           #
# --------------------------------------------------------------------------- #


def candidates_from_champion_trace(
    result: ESResult,
    *,
    encoder_version: str,
    policy_id: str,
    method: str,
    hidden: int | None = None,
    anchor_policy: str = "fsm-default",
    label_prefix: str = "gen",
) -> tuple[RealPathCandidate, ...]:
    """Turn an ``ESResult.champion_trace`` into de-duplicated candidates (design C).

    ``champion_trace`` (index 0 = the seeded initial genome; consecutive repeats
    when a generation makes no strict improvement — es.py) is de-duplicated by
    :func:`_genome_digest`; the first occurrence wins and every generation index
    that produced the genome accumulates into ``generation_indices``. The label is
    ``f"{label_prefix}{first_index:03d}"``. You supply the stamp fields yourself
    (there is no per-generation ``stamp.json``); ``weights_sha256`` is computed
    from the exact genome bytes recorded, so the read-back invariant still holds.
    """

    order: list[str] = []
    first_index: dict[str, int] = {}
    indices: dict[str, list[int]] = {}
    genome_by_digest: dict[str, tuple[float, ...]] = {}
    for index, raw in enumerate(result.champion_trace):
        genome = tuple(raw)
        digest = _genome_digest(genome)
        if digest not in indices:
            order.append(digest)
            first_index[digest] = index
            indices[digest] = [index]
            genome_by_digest[digest] = genome
        else:
            indices[digest].append(index)
    return tuple(
        RealPathCandidate(
            label=f"{label_prefix}{first_index[digest]:03d}",
            genome=genome_by_digest[digest],
            encoder_version=encoder_version,
            hidden=hidden,
            policy_id=policy_id,
            method=method,
            anchor_policy=anchor_policy,
            generation_indices=tuple(indices[digest]),
        )
        for digest in order
    )


def run_realpath_rerank(
    candidates: Sequence[RealPathCandidate],
    *,
    seeds: Sequence[int],
    work_dir: Path,
    ranking_path: Path,
    config: RealPathRerankConfig | None = None,
    game_map: Map | None = None,
    meeting_runner_factory: Callable[[], MeetingRunner] | None = None,
    mode: str = MODE_TOP_K,
) -> RealPathRerankResult:
    """Record and re-rank K candidates over a seed list on the real path.

    For each candidate: rebuild its agent factory (fail-loud on a bad genome),
    record one game per seed into ``work_dir / f"{i:03d}-{slug}"`` with the
    per-meeting timeout proxy and per-seed retry budget, drop the audit sidecars,
    write ``roster.json``, verify every recording's stamp read back from bytes,
    and score the directory through the committed validity / core / watchability
    library entry points. After ALL candidates are scored, sort stably by
    descending selection score (ties keep input order), assign ranks ``1..K``, and
    write one JSONL row per candidate to ``ranking_path`` (write-once, only after
    ranking — an exhausted seed aborts BEFORE any committed artifact exists).

    ``meeting_runner_factory`` is the BASE per-game runner factory (the
    ``eval/balance_eval.py:241`` seam); the re-rank always wraps each produced
    runner in the timeout proxy. ``None`` uses the default roster-scaled runner,
    identical to ``run_tournament_eval``'s ``None`` path.
    """

    resolved_config = config if config is not None else RealPathRerankConfig()
    if not candidates:
        raise ValueError("candidates must be non-empty")
    labels = [candidate.label for candidate in candidates]
    if len(set(labels)) != len(labels):
        raise ValueError(f"candidate labels must be unique; got {labels!r}")
    seeds_tuple = tuple(seeds)
    if not seeds_tuple:
        raise ValueError("seeds must be non-empty")
    if len(set(seeds_tuple)) != len(seeds_tuple):
        raise ValueError(f"seeds must be unique; got {seeds_tuple!r}")
    if mode not in (MODE_TOP_K, MODE_CHAMPION_TRACE):
        raise ValueError(
            f"mode must be one of {(MODE_TOP_K, MODE_CHAMPION_TRACE)!r}; got {mode!r}"
        )

    resolved_map = game_map if game_map is not None else load_canonical_map()

    payloads: list[_CandidatePayload] = []
    for index, candidate in enumerate(candidates):
        stamp = _candidate_stamp(candidate)
        digest = stamp.weights_sha256
        agent_factory = _build_agent_factory(candidate, game_map=resolved_map)
        candidate_dir = work_dir / f"{index:03d}-{_safe_slug(candidate.label)}"
        candidate_dir.mkdir(parents=True, exist_ok=False)
        telemetry = tuple(
            _record_seed(
                seed=seed,
                label=candidate.label,
                candidate_dir=candidate_dir,
                game_map=resolved_map,
                agent_factory=agent_factory,
                stamp=stamp,
                config=resolved_config,
                base_meeting_runner_factory=meeting_runner_factory,
            )
            for seed in seeds_tuple
        )
        _drop_audit_sidecars(candidate_dir)
        _write_roster_json(candidate_dir, resolved_config)
        read_stamp, verified = _verify_stamps(
            candidate_dir,
            seeds=seeds_tuple,
            expected_digest=digest,
            label=candidate.label,
        )
        validity = run_validity_gate(candidate_dir)
        watchability = compute_watchability(
            candidate_dir, baseline_id=resolved_config.baseline_id
        )
        core = measure_baseline.measure_baseline(candidate_dir)
        payloads.append(
            _CandidatePayload(
                candidate=candidate,
                stamp=read_stamp,
                digest=digest,
                verified=verified,
                telemetry=telemetry,
                validity=validity,
                watchability=watchability,
                core=core,
            )
        )

    scores = [
        _selection_score(payload.validity, payload.watchability) for payload in payloads
    ]
    order = sorted(range(len(payloads)), key=lambda i: (-scores[i], i))
    rows = tuple(
        _build_row(
            payloads[i],
            mode=mode,
            seeds=seeds_tuple,
            config=resolved_config,
            selection_score=scores[i],
            rank=rank,
        )
        for rank, i in enumerate(order, start=1)
    )
    ranking_path.parent.mkdir(parents=True, exist_ok=True)
    ranking_path.write_text("".join(row.to_json_line() + "\n" for row in rows))
    return RealPathRerankResult(
        mode=mode,
        ranking_path=str(ranking_path),
        work_dir=str(work_dir),
        seeds=seeds_tuple,
        config=resolved_config,
        rows=rows,
    )


__all__ = [
    "DEFAULT_BASELINE_ID",
    "DEFAULT_MAX_ATTEMPTS",
    "DEFAULT_MEETING_TIMEOUT_SECONDS",
    "DEFAULT_NUM_IMPOSTORS",
    "DEFAULT_NUM_PLAYERS",
    "DEFAULT_TASKS_PER_CREWMATE",
    "MODE_CHAMPION_TRACE",
    "MODE_TOP_K",
    "SCHEMA_VERSION",
    "RealPathCandidate",
    "RealPathMeetingTimeoutError",
    "RealPathRerankConfig",
    "RealPathRerankError",
    "RealPathRerankResult",
    "RealPathRerankRow",
    "RealPathSeedExhaustedError",
    "RealPathSeedTelemetry",
    "RealPathStampError",
    "candidates_from_champion_trace",
    "run_realpath_rerank",
]
