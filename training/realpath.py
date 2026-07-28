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

Two recording outcomes are terminal, never retried: a ``TICK_BUDGET_REACHED``
game is an accepted non-decisive outcome (the engine writes no ``game_over``
row for it, so that seed contributes no stamp bytes — provenance is proven over
the decisive seeds, and a candidate with NO decisive seed fails loud), and a
:class:`~llm.budget.BudgetExceededError` is a metering stop that propagates
unretried (re-recording would re-spend the per-game cap on a paid provider).

Honesty note (provider nondeterminism). Real-path ranks are a SELECTION signal,
NOT a fitness. Two runs of the same genome on the real provider may score
differently, which selection tolerates but the ES fitness-purity contract
(``training/bakeoff/es.py:51-55`` — a fitness MUST be a pure, deterministic
function of the genome) does not. These scores MUST NEVER be written back into an
ES fitness channel; routing them into :func:`~training.bakeoff.es.evolve` would
break the double-run determinism digest. The committed output is the ranking
JSONL; nothing here feeds :func:`~training.bakeoff.es.evolve`.

Campaign ergonomics (Task 18.31, from the 18.24 campaign's operational cost
evidence — training/reports/report-impostor-campaign.md §11):

* **RESUME** (``resume=True``; §11 defect 1 — a provider 503 at hour 40
  destroyed 25 recorded games because a re-run re-records everything). A
  ``(candidate, seed)`` element is SKIPPED only when all three of these hold —
  the predicate is CONJUNCTIVE and any miss RE-RECORDS: the replay exists; its
  stamp read BACK from bytes carries a ``weights_sha256`` equal to the
  candidate's computed genome digest; and the recording passes the dir-scoped
  byte-completeness fence (:func:`eval.kill_craft.compute_kill_craft_report`,
  reached per element through a per-seed staging copy). The cost asymmetry is
  the whole design: re-recording one seed costs minutes, while skipping one
  unverified element poisons an evidence table. Two dispositions follow from
  the rule and are stated so nobody re-derives them: a ``TICK_BUDGET_REACHED``
  replay writes NO ``game_over`` row by design, so it carries no stamp and is
  NEVER skippable (it re-records, deliberately), and a replay recorded by a
  DIFFERENT genome fails the digest check no matter how complete it is.
* **Native pre-screen records + a native leg log** (§11 defect 3 / F9, and §12
  Errata item 10 — the session-5 provenance gap: 36 games whose
  pre-screen-before-spend ordering rests on operator testimony because the only
  leg logs were shell redirections). :func:`write_prescreen_record` writes the
  blocker-4 quotes keyed by TRANCHE and INVOCATION (never in place), and every
  leg opens an invocation-stamped manifest plus an APPEND-ONLY
  :class:`RealPathLegLog` that the library itself writes — pre-screen quotes
  before any recording, one event per recorded/resumed seed, the ranked rows,
  and a terminal event on success or failure.

Public surface (stable — downstream tasks import these):
:class:`RealPathCandidate`, :class:`RealPathRerankConfig`,
:class:`RealPathSeedTelemetry`, :class:`RealPathRerankRow`,
:class:`RealPathRerankResult`, :class:`PreScreenQuote`,
:class:`PreScreenRecord`, :class:`RealPathLegLog`,
:func:`candidates_from_champion_trace`, :func:`write_prescreen_record`,
:func:`run_realpath_rerank`, the :class:`RealPathRerankError` family, and the
``SCHEMA_VERSION`` / ``MODE_*`` / ``DEFAULT_*`` constants.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from agents.base import AgentInterface
from agents.tactical.features import weights_to_hex_json
from engine.entities import PlayerId
from engine.world import Map, WorldState, load_canonical_map
from eval.balance_eval import _resolve_game_budget, run_tournament_eval

# The dir-scoped byte-completeness fence the resume predicate's third check
# reaches per (candidate, seed) through a staging copy (Task 18.31). It is
# consumed EXACTLY as committed — eval/kill_craft.py is not edited.
from eval.kill_craft import compute_kill_craft_report
from eval.validity import ValidityGateReport, run_validity_gate

# _BASELINE_SUPPLY_FLOORS is a deliberate private import (same posture as
# _resolve_game_budget above): the floor-block preflight must fail BEFORE any
# real-provider seed is recorded, and compute_watchability can only raise its
# KeyError after a directory of recordings exists.
from eval.watchability import (
    _BASELINE_SUPPLY_FLOORS,
    WatchabilityReport,
    compute_watchability,
)
from llm.budget import BudgetExceededError
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

# The committed watchability floor block every training consumer pins — the
# adopted phase-18 substrate (baseline-6, Task 18.12's record), tracking the
# bake-off selection bar (training.bakeoff.harness.BAKEOFF_BASELINE_ID) so a
# default-config real-path re-rank scores on the same floors the bake-off selects
# on. Re-pinned baseline-5 -> baseline-6 at Task 18.14 (the selection-bar flip).
DEFAULT_BASELINE_ID: Final[str] = "baseline-6"

# The 9p2i SELECTION roster (the canonical eval roster the referee floors are
# pinned for), NOT the engine's 4p1i defaults (orchestrator/game.py:120-121):
# the re-rank scores champions on the roster the bake-off selects on.
DEFAULT_NUM_PLAYERS: Final[int] = 9
DEFAULT_NUM_IMPOSTORS: Final[int] = 2
DEFAULT_TASKS_PER_CREWMATE: Final[int] = 2

MODE_TOP_K: Final[str] = "top-k"
MODE_CHAMPION_TRACE: Final[str] = "champion-trace"

# The masked-MLP family's encoder identities. Both rebuild through
# ``build_masked_mlp_policy``'s ``encoder_version`` seam (Task 18.22): the
# committed policy-es champion stamps "v2"; the 18.22 encoder-v3 + per-target
# head family stamps "v3" (wider input AND head, so the seam — not a hard-coded
# builder — is what keeps the genome shape honest). A new family is supported by
# extending the dispatch in _build_agent_factory and this whitelist — never by
# silently building the wrong encoder for an unknown version.
_MASKED_MLP_ENCODER_VERSION: Final[str] = "v2"
_MASKED_MLP_ENCODER_VERSION_V3: Final[str] = "v3"
_SUPPORTED_ENCODER_VERSIONS: Final[tuple[str, ...]] = (
    _UTILITY_ENCODER_VERSION,
    _MASKED_MLP_ENCODER_VERSION,
    _MASKED_MLP_ENCODER_VERSION_V3,
)

# The non-decisive outcome run_tournament_eval folds with
# ``fallback_reason=result.outcome`` (eval/balance_eval.py): such a game is
# complete but capped, writes NO game_over row, and must not be retried.
_TICK_BUDGET_REASON: Final[str] = "TICK_BUDGET_REACHED"

# The selection composition mirrors training/bakeoff/goodhart.py:257/269/272-290:
# a validity-failing set scores below any real geomean, and a referee pass
# (supply floors AND integrity) dominates the geomean tie-break.
_INVALID_SELECTION_SCORE: Final[float] = -1.0
_REFEREE_PASS_BONUS: Final[float] = 1000.0

_ROSTER_FILENAME: Final[str] = "roster.json"
_SLUG_EXTRA: Final[str] = "-_"

# A 64-lowercase-hex sha256 digest (the genome identity every quote names).
_SHA256_HEX_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")

# --------------------------------------------------------------------------- #
# Task 18.31: pre-screen records + the native leg log.                         #
# --------------------------------------------------------------------------- #

#: The pre-screen quote record schema identity.
PRESCREEN_SCHEMA_VERSION: Final[str] = "realpath-prescreen-v1"

#: The append-only leg-log event schema identity.
LEG_LOG_SCHEMA_VERSION: Final[str] = "realpath-leg-log-v1"

#: The per-invocation leg-manifest schema identity (a distinct artifact from
#: the log's event stream — one stamp per invocation, not one per event).
LEG_MANIFEST_SCHEMA_VERSION: Final[str] = "realpath-leg-manifest-v1"

#: The verbatim blocker-4 disclaimer every committed pre-screen quote carries:
#: a pre-screen is SPEND ADVICE, never a gating read.
PRESCREEN_ADVICE_NOTE: Final[str] = "spend advice ONLY (blocker 4)"

#: ``<work_dir>/prescreen-quotes-<tranche>-<invocation>.json`` — the committed
#: 18.24 stem, now keyed by invocation as well as tranche so a second tranche
#: (or a re-run of the same one) can never overwrite the first's record.
PRESCREEN_FILENAME_STEM: Final[str] = "prescreen-quotes"

#: ``<work_dir>/leg-<tranche>-<invocation>.json`` — the invocation stamp whose
#: exclusive creation ALLOCATES the invocation id (race-free, no directory
#: scan-then-write window).
LEG_MANIFEST_FILENAME_STEM: Final[str] = "leg"

#: ``<work_dir>/leg-log.jsonl`` — one append-only log per work dir, every event
#: keyed by ``(tranche, invocation)``.
LEG_LOG_FILENAME: Final[str] = "leg-log.jsonl"

#: The invocation-ordinal ceiling. 1000 invocations of ONE tranche into ONE
#: work dir is a runaway, not a campaign: refuse rather than spin.
_MAX_INVOCATIONS: Final[int] = 1000

#: Event-record keys the leg log owns; a caller field colliding with one of
#: them is a fail-loud contradiction, never a silent override.
_LEG_LOG_RESERVED_KEYS: Final[tuple[str, ...]] = (
    "event",
    "invocation",
    "recorded_at",
    "schema_version",
    "seq",
    "tranche",
)


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
        if self.encoder_version not in _SUPPORTED_ENCODER_VERSIONS:
            raise ValueError(
                f"candidate {self.label!r}: unsupported encoder_version "
                f"{self.encoder_version!r}; supported families: "
                f"{_SUPPORTED_ENCODER_VERSIONS!r}. A new family extends "
                "_build_agent_factory's dispatch and this whitelist — never a "
                "silent fallback to the wrong builder"
            )
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
    parse-fold abort case). ``tick_budget_reached`` marks the accepted
    non-decisive outcome: the game hit the scheduler cap, so its replay has no
    ``game_over`` row (and no stamp bytes) BY DESIGN — never retried, and
    excluded from stamp verification. ``wall_seconds`` is cumulative monotonic
    time across all attempts, rounded to 3 places.

    ``resumed`` (Task 18.31) marks an element this invocation did NOT record:
    a pre-existing replay that satisfied the whole conjunctive resume
    predicate. Such an entry carries ``attempts=0`` (honest — no recording was
    attempted), empty counters, and ``tick_budget_reached=False``: a capped
    replay has no ``game_over`` row, so it can never satisfy the predicate.
    ``wall_seconds`` is then the verification cost.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    attempts: int
    timed_out_attempts: int
    degraded_recordings: int
    tick_budget_reached: bool
    error_types: tuple[str, ...]
    wall_seconds: float
    resumed: bool = False

    @model_validator(mode="after")
    def _validate(self) -> RealPathSeedTelemetry:
        if self.resumed:
            if self.attempts != 0:
                raise ValueError(
                    f"a resumed element attempts no recording; got "
                    f"attempts={self.attempts!r}"
                )
            if self.error_types:
                raise ValueError(
                    "a resumed element records no failed attempt; got "
                    f"error_types={self.error_types!r}"
                )
            if self.tick_budget_reached:
                raise ValueError(
                    "a tick-budget replay carries no game_over stamp and is "
                    "therefore never resumable; got tick_budget_reached=True"
                )
        elif self.attempts < 1:
            raise ValueError(f"attempts must be >= 1; got {self.attempts!r}")
        if len(self.error_types) != max(self.attempts - 1, 0):
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
    the in-memory launch stamp; ``stamp_verified_games`` counts the DECISIVE
    games whose bytes proved it (a tick-budget game has no ``game_over`` row and
    is excluded — see ``seed_telemetry``'s ``tick_budget_reached``). Core
    metrics are flattened scalars (no ``scripts/`` type in the row schema); a
    ``float | None`` core field stays ``None`` when its denominator is empty and
    is never coerced to ``0.0``.
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
# Pre-screen records + the native leg log (Task 18.31).                        #
# --------------------------------------------------------------------------- #


class PreScreenQuote(BaseModel):
    """One candidate's blocker-4 pre-screen quote (frozen, extra='forbid').

    SPEND ADVICE ONLY: a pre-screen predicts whether a candidate is worth real
    seeds, and no gating read ever stands on it (``note`` carries the committed
    disclaimer verbatim). The optional fields mirror the 18.24 records —
    ``None`` means the quantity was not measured, never a zero-ghost.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str
    weights_sha256: str
    predicted_flags_per_meeting: float
    predicted_floors_pass: bool
    generation: int | None = None
    meetings_scored: int | None = None
    conviction_uses: int | None = None
    recorded_flags_fake_substrate: float | None = None
    note: str = PRESCREEN_ADVICE_NOTE

    @model_validator(mode="after")
    def _validate(self) -> PreScreenQuote:
        if not self.label.strip():
            raise ValueError(f"label must be non-blank; got {self.label!r}")
        if _SHA256_HEX_RE.fullmatch(self.weights_sha256) is None:
            raise ValueError(
                "weights_sha256 must be exactly 64 lowercase hex chars; got "
                f"{self.weights_sha256!r}"
            )
        for name, value in (
            ("predicted_flags_per_meeting", self.predicted_flags_per_meeting),
            ("recorded_flags_fake_substrate", self.recorded_flags_fake_substrate),
        ):
            if value is not None and not math.isfinite(value):
                raise ValueError(f"{name} must be finite; got {value!r}")
        for name, count in (
            ("meetings_scored", self.meetings_scored),
            ("conviction_uses", self.conviction_uses),
        ):
            if count is not None and count < 0:
                raise ValueError(f"{name} must be >= 0; got {count!r}")
        if self.note != PRESCREEN_ADVICE_NOTE:
            # The disclaimer is the record's provenance guarantee, not a caption:
            # a quote whose note called the prediction gating evidence would
            # invert blocker 4 in the committed artifact (Codex review on
            # PR #314). It is a constant the field carries, never caller text.
            raise ValueError(
                f"note must be exactly {PRESCREEN_ADVICE_NOTE!r} (a pre-screen is "
                f"spend advice by contract); got {self.note!r}"
            )
        return self


class PreScreenRecord(BaseModel):
    """A tranche/invocation-keyed pre-screen record (frozen, extra='forbid').

    The committed 18.24 records were written IN PLACE per leg, so a second
    tranche overwrote the first's quotes (report §11 defect 3 / F9) and the
    session-5 records carried no invocation stamp at all (§12 Errata item 10).
    Both keys are structural here: the record names its tranche AND its
    invocation, and :func:`write_prescreen_record` only ever creates a NEW file.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = PRESCREEN_SCHEMA_VERSION
    tranche: str
    invocation: str
    seeds: tuple[int, ...]
    recorded_at: str
    quotes: tuple[PreScreenQuote, ...]

    @model_validator(mode="after")
    def _validate(self) -> PreScreenRecord:
        if not self.quotes:
            raise ValueError("a pre-screen record must carry at least one quote")
        labels = [quote.label for quote in self.quotes]
        if len(set(labels)) != len(labels):
            raise ValueError(f"pre-screen quote labels must be unique; got {labels!r}")
        if not self.seeds:
            raise ValueError("seeds must be non-empty")
        return self

    def to_json(self) -> str:
        """The committed byte form: key-sorted, 2-space indent, trailing newline."""

        return json.dumps(self.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"


class RealPathLegLog:
    """The leg library's OWN append-only run log (Task 18.31 fix 3).

    An explicit, invocation-scoped object (never module state — AGENTS.md): the
    leg constructs one and writes every ordering-relevant event through it, so
    the blocker-4 "pre-screen quoted BEFORE any spend" evidence is a library
    artifact rather than an operator shell redirection. §12 Errata item 10 is
    the demonstration of the gap: session 5's 36 real games have no chain log,
    so their ordering rests on testimony alone.

    Every event is one key-sorted JSON object on its own line, carrying the
    ``(tranche, invocation)`` key, a monotone per-invocation ``seq``, and a UTC
    ``recorded_at``. The file is opened in APPEND mode per event and closed
    again, so a leg killed mid-recording (the hour-40 provider 503) still leaves
    every event it had already emitted on disk.
    """

    def __init__(self, path: Path, *, tranche: str, invocation: str) -> None:
        self._path = path
        self._tranche = tranche
        self._invocation = invocation
        self._seq = 0

    @property
    def path(self) -> Path:
        return self._path

    @property
    def invocation(self) -> str:
        return self._invocation

    def emit(self, event: str, **fields: object) -> None:
        """Append one event; fail loud on a field that shadows a reserved key."""

        clashing = sorted(key for key in _LEG_LOG_RESERVED_KEYS if key in fields)
        if clashing:
            raise ValueError(
                f"leg-log event {event!r} carries reserved keys {clashing}; the "
                "log owns them (they are its ordering evidence)"
            )
        self._seq += 1
        record: dict[str, object] = {
            "event": event,
            "invocation": self._invocation,
            "recorded_at": _utc_now(),
            "schema_version": LEG_LOG_SCHEMA_VERSION,
            "seq": self._seq,
            "tranche": self._tranche,
            **fields,
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def _utc_now() -> str:
    """The wall-clock stamp the ordering evidence needs (UTC, ISO-8601)."""

    return datetime.now(UTC).isoformat()


def tranche_key(seeds: Sequence[int]) -> str:
    """The committed tranche key for a seed list (``4000-4002``; ``4000`` if one).

    Mirrors the 18.24 artifact names (``ranking-4000-4002.jsonl``). The key is
    the FIRST and LAST seed in the caller's order, so a non-contiguous tranche
    keys on its endpoints; the exact seed list is recorded in the leg manifest
    and the pre-screen record, so nothing is lost by the abbreviation.
    """

    if not seeds:
        raise ValueError("cannot key a tranche with no seeds")
    if len(seeds) == 1:
        return str(seeds[0])
    return f"{seeds[0]}-{seeds[-1]}"


def _invocation_path(directory: Path, stem: str, tranche: str, ordinal: int) -> Path:
    return directory / f"{stem}-{tranche}-{ordinal:03d}.json"


def write_prescreen_record(
    directory: Path,
    *,
    seeds: Sequence[int],
    quotes: Sequence[PreScreenQuote],
    invocation: str | None = None,
) -> Path:
    """Write one tranche/invocation-keyed pre-screen record; NEVER in place.

    ``invocation=None`` allocates the next free ordinal for this tranche by
    EXCLUSIVE creation (``open("x")``), so two concurrent legs cannot be handed
    the same id; an explicit ``invocation`` writes exactly that file and raises
    :class:`FileExistsError` if it already exists. Returns the written path.
    """

    tranche = tranche_key(tuple(seeds))
    record_seeds = tuple(seeds)
    directory.mkdir(parents=True, exist_ok=True)
    if invocation is not None:
        path = directory / f"{PRESCREEN_FILENAME_STEM}-{tranche}-{invocation}.json"
        _write_prescreen_json(
            path,
            tranche=tranche,
            invocation=invocation,
            seeds=record_seeds,
            quotes=quotes,
        )
        return path
    for ordinal in range(_MAX_INVOCATIONS):
        path = _invocation_path(directory, PRESCREEN_FILENAME_STEM, tranche, ordinal)
        try:
            _write_prescreen_json(
                path,
                tranche=tranche,
                invocation=f"{ordinal:03d}",
                seeds=record_seeds,
                quotes=quotes,
            )
        except FileExistsError:
            continue
        return path
    raise RealPathRerankError(
        f"no free pre-screen invocation ordinal for tranche {tranche!r} under "
        f"{directory} after {_MAX_INVOCATIONS} attempts; that is a runaway, "
        "not a campaign"
    )


def _validate_prescreen_coverage(
    quotes: Sequence[PreScreenQuote], candidates: Sequence[RealPathCandidate]
) -> None:
    """Refuse pre-screen quotes that do not name THIS leg's candidates (18.31).

    The ordering evidence is only worth what it names: a stale or partial quote
    set proves that SOME advice preceded the spend, not that the candidates
    consuming real-provider games were the ones pre-screened (Codex review on
    PR #314). Coverage is therefore the full ``label -> digest`` MAPPING, not a
    digest set: a leg may legitimately carry two labels over one genome (the
    same policy re-entered under two names), and comparing sets would let one
    quote cover both — leaving a candidate that consumed real games unnamed.
    """

    expected = {
        candidate.label: _genome_digest(candidate.genome) for candidate in candidates
    }
    quoted: dict[str, str] = {}
    for quote in quotes:
        if quote.label in quoted:  # pragma: no cover - PreScreenRecord re-checks
            raise ValueError(
                f"pre-screen quotes must name each candidate once; {quote.label!r} "
                "is quoted twice"
            )
        quoted[quote.label] = quote.weights_sha256
    if quoted != expected:
        missing = sorted(set(expected) - set(quoted))
        extra = sorted(set(quoted) - set(expected))
        mispaired = sorted(
            f"{label} quoted {quoted[label]} != candidate {expected[label]}"
            for label in set(expected) & set(quoted)
            if quoted[label] != expected[label]
        )
        raise ValueError(
            "pre-screen quotes must cover exactly this leg's candidates "
            f"(label -> digest); missing {missing}, extra {extra}, "
            f"mispaired {mispaired} (the blocker-4 evidence names the candidates "
            "the spend recorded)"
        )


def _write_prescreen_json(
    path: Path,
    *,
    tranche: str,
    invocation: str,
    seeds: tuple[int, ...],
    quotes: Sequence[PreScreenQuote],
) -> None:
    """Build + exclusively write one pre-screen record (validation before I/O)."""

    record = PreScreenRecord(
        tranche=tranche,
        invocation=invocation,
        seeds=seeds,
        recorded_at=_utc_now(),
        quotes=tuple(quotes),
    )
    with path.open("x", encoding="utf-8") as handle:
        handle.write(record.to_json())


def _open_leg_manifest(
    work_dir: Path,
    *,
    tranche: str,
    seeds: tuple[int, ...],
    mode: str,
    resume: bool,
    candidates: Sequence[RealPathCandidate],
    config: RealPathRerankConfig,
    ranking_path: Path,
) -> tuple[str, Path]:
    """Allocate this leg's invocation id by exclusively creating its manifest.

    The invocation stamp §12 Errata item 10 records the absence of: which
    candidates, which seeds, which knobs, and WHEN — written before any
    recording, and the file's exclusive creation is what makes the id unique.
    """

    work_dir.mkdir(parents=True, exist_ok=True)
    for ordinal in range(_MAX_INVOCATIONS):
        path = _invocation_path(work_dir, LEG_MANIFEST_FILENAME_STEM, tranche, ordinal)
        manifest = {
            "candidates": [
                {
                    "encoder_version": candidate.encoder_version,
                    "hidden": candidate.hidden,
                    "label": candidate.label,
                    "weights_sha256": _genome_digest(candidate.genome),
                }
                for candidate in candidates
            ],
            "config": config.model_dump(mode="json"),
            "invocation": f"{ordinal:03d}",
            "mode": mode,
            "ranking_path": str(ranking_path),
            "resume": resume,
            "schema_version": LEG_MANIFEST_SCHEMA_VERSION,
            "seeds": list(seeds),
            "started_at": _utc_now(),
            "tranche": tranche,
        }
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        except FileExistsError:
            continue
        return f"{ordinal:03d}", path
    raise RealPathRerankError(
        f"no free leg invocation ordinal for tranche {tranche!r} under {work_dir} "
        f"after {_MAX_INVOCATIONS} attempts; that is a runaway, not a campaign"
    )


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
        # The encoder_version seam (Task 18.22) selects the v2 or v3 family —
        # the whitelist above already vetted it, and the post-check below pins
        # the rebuilt identity against the declared one.
        policy = build_masked_mlp_policy(
            candidate.genome,
            game_map=game_map,
            hidden=hidden,
            encoder_version=candidate.encoder_version,
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


def _completeness_fence_failure(
    replay_path: Path, *, config: RealPathRerankConfig
) -> str | None:
    """``None`` iff the single recording passes the byte-completeness fence.

    The committed fence (:func:`eval.kill_craft.compute_kill_craft_report`) is
    DIR-scoped: it walks every ``replay-seed-*.jsonl`` beside the roster
    descriptor. Per-(candidate, seed) verification is therefore reached by
    STAGING one replay into a throwaway directory with its ``roster.json`` —
    the sanctioned route (Task 18.31), never an edit to ``eval/kill_craft.py``.
    Any failure at all (a truncated replay, a missing ``game_over`` row,
    trailing rows after the terminal tick, an unreadable file, a roster the
    walk cannot reconstruct) returns a reason string, and every reason means
    RE-RECORD: the resume predicate is conjunctive and biased toward spending
    minutes rather than certifying bytes nobody verified.
    """

    with tempfile.TemporaryDirectory(prefix="realpath-resume-") as raw_staging:
        staging = Path(raw_staging)
        try:
            (staging / replay_path.name).write_bytes(replay_path.read_bytes())
        except OSError as exc:
            return f"{type(exc).__name__}: {exc}"
        _write_roster_json(staging, config)
        try:
            compute_kill_craft_report(staging)
        except Exception as exc:  # noqa: BLE001 - ANY failure re-records
            return f"{type(exc).__name__}: {exc}"
    return None


def _resume_skip_reason(
    replay_path: Path, *, expected_digest: str, config: RealPathRerankConfig
) -> str | None:
    """``None`` iff this (candidate, seed) element may be SKIPPED (Task 18.31).

    The predicate is CONJUNCTIVE — all three checks must pass, and any miss
    returns the reason and re-records:

    1. **the replay exists** on disk at all;
    2. **its stamp reads back from the bytes** (never echoed from the launch
       config — the 17.14 discipline) and its ``weights_sha256`` equals the
       candidate's COMPUTED genome digest, so a foreign or superseded genome's
       recording can never be adopted as this candidate's;
    3. **the byte-completeness fence is green** for that recording.

    Check 2 is also what makes a ``TICK_BUDGET_REACHED`` replay unskippable:
    the engine writes no ``game_over`` row for a capped game, so there are no
    stamp bytes to read and the element re-records — deliberately, since a
    capped replay is an accepted OUTCOME of a recording, not proof that this
    invocation's recording happened.
    """

    if not replay_path.exists():
        return "no replay on disk"
    try:
        stamp = read_tactical_policy_stamp(replay_path)
    except Exception as exc:  # noqa: BLE001 - ANY unreadable replay re-records
        # An interrupted process can leave a half-written line, and the reader
        # raises on it (``ValueError: invalid replay JSON at line N``) or on the
        # doubled-file pattern (``CorruptedFileError``). Those are the very
        # states a resume exists to meet: an unreadable replay is a verification
        # MISS, never a leg-killing exception (Codex review on PR #314).
        return f"replay bytes are unreadable ({type(exc).__name__}: {exc})"
    if stamp is None:
        return (
            "no tactical policy stamp on the recorded bytes (no game_over row — "
            "a TICK_BUDGET_REACHED, truncated, or parse-folded recording)"
        )
    if stamp.weights_sha256 != expected_digest:
        return (
            f"read-back weights_sha256 {stamp.weights_sha256!r} != computed "
            f"genome digest {expected_digest!r}"
        )
    fence = _completeness_fence_failure(replay_path, config=config)
    if fence is not None:
        return f"byte-completeness fence failed ({fence})"
    return None


def _replay_seed(path: Path) -> int | None:
    """The seed a ``replay-seed-<n>.jsonl`` filename names (``None`` if unparsable)."""

    token = path.name.removeprefix("replay-seed-").removesuffix(".jsonl")
    try:
        return int(token)
    except ValueError:
        return None


def _refuse_foreign_replays(
    candidate_dir: Path, *, seeds: tuple[int, ...], label: str
) -> None:
    """Refuse a resume into a dir holding replays outside THIS tranche (18.31).

    The scoring entry points (``run_validity_gate`` /
    ``compute_watchability`` / ``measure_baseline``) fold the whole DIRECTORY,
    so a leftover replay from a different tranche would silently enter this
    invocation's committed row. An unparsable ``replay-seed-*.jsonl`` name
    counts as foreign — the ambiguity is resolved toward refusing, never
    toward folding bytes nobody can attribute to a seed.
    """

    requested = set(seeds)
    foreign = sorted(
        path.name
        for path in candidate_dir.glob("replay-seed-*.jsonl")
        if _replay_seed(path) not in requested
    )
    if foreign:
        raise RealPathRerankError(
            f"candidate {label!r}: resume refuses {candidate_dir} — it holds "
            f"replays outside this tranche {foreign}; the scoring gates fold the "
            f"whole directory, so those bytes would silently enter the row for "
            f"seeds {list(seeds)}"
        )


def _publish_ranking(ranking_path: Path, payload: str) -> None:
    """Publish the ranking bytes ATOMICALLY and write-once (18.31).

    A bare ``open("x")`` creates the file and only then writes it, so an
    interrupt (or a failing write) between the two leaves an empty or partial
    ranking on disk. That file is indistinguishable from a committed one to
    everything downstream: the resume preflight rejects the leg as already
    recorded — refusing a resume whose verified replays are still there — and a
    reader folds truncated rows as though they were the whole leg (Codex review
    on PR #314). Round 3's preflight is what made that half-written file
    reachable, so the fix belongs here rather than in the preflight.

    The complete bytes are staged in the DESTINATION directory (same
    filesystem, so the link below cannot cross devices), flushed through to
    disk, and then published with :func:`os.link` — one syscall that is both
    atomic and exclusive, failing with ``FileExistsError`` if the ranking
    already exists. ``os.replace`` would be atomic but would silently CLOBBER a
    committed ranking, which is the defect round 2 caught. The stage file is
    removed on every path, so a crash leaves at most a ``.tmp`` nobody reads.
    """

    stage: Path | None = None
    try:
        handle_fd, stage_name = tempfile.mkstemp(
            dir=ranking_path.parent, prefix=f".{ranking_path.name}.", suffix=".tmp"
        )
        stage = Path(stage_name)
        with os.fdopen(handle_fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(stage, ranking_path)
        except FileExistsError as exc:
            raise RealPathRerankError(
                f"a committed ranking already exists at {ranking_path}; this leg "
                "is already recorded and its rows are never rewritten (point "
                "--ranking-path at a fresh file, or delete the stale one "
                "deliberately)"
            ) from exc
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)


def _record_or_resume_seed(
    *,
    seed: int,
    candidate: RealPathCandidate,
    candidate_dir: Path,
    game_map: Map,
    agent_factory: AgentFactory,
    stamp: TacticalPolicyStamp,
    digest: str,
    config: RealPathRerankConfig,
    base_meeting_runner_factory: Callable[[], MeetingRunner] | None,
    resume: bool,
    leg_log: RealPathLegLog,
) -> RealPathSeedTelemetry:
    """Skip a verified-complete element, else record it (Task 18.31 fix 1).

    Non-resume runs go straight to :func:`_record_seed`, byte-for-byte the
    pre-18.31 path. Under ``resume`` the conjunctive predicate decides, and its
    verdict — skip, or the exact reason for re-recording — is logged either way.
    """

    replay_path = candidate_dir / f"replay-seed-{seed}.jsonl"
    force_first_attempt = False
    if resume:
        start = time.monotonic()
        reason = _resume_skip_reason(replay_path, expected_digest=digest, config=config)
        if reason is None:
            resumed = RealPathSeedTelemetry(
                seed=seed,
                attempts=0,
                timed_out_attempts=0,
                degraded_recordings=0,
                tick_budget_reached=False,
                error_types=(),
                wall_seconds=round(time.monotonic() - start, 3),
                resumed=True,
            )
            leg_log.emit(
                "seed-resumed",
                label=candidate.label,
                replay=str(replay_path),
                seed=seed,
                wall_seconds=resumed.wall_seconds,
            )
            return resumed
        # Any miss re-records, over whatever bytes are there.
        force_first_attempt = replay_path.exists()
        leg_log.emit(
            "seed-rerecord",
            label=candidate.label,
            reason=reason,
            seed=seed,
        )
    telemetry = _record_seed(
        seed=seed,
        label=candidate.label,
        candidate_dir=candidate_dir,
        game_map=game_map,
        agent_factory=agent_factory,
        stamp=stamp,
        config=config,
        base_meeting_runner_factory=base_meeting_runner_factory,
        force_first_attempt=force_first_attempt,
    )
    leg_log.emit(
        "seed-recorded",
        attempts=telemetry.attempts,
        label=candidate.label,
        seed=seed,
        tick_budget_reached=telemetry.tick_budget_reached,
        wall_seconds=telemetry.wall_seconds,
    )
    return telemetry


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
    force_first_attempt: bool = False,
) -> RealPathSeedTelemetry:
    """Record one seed with the per-seed crash-retry budget (fail-loud on exhaust).

    A retry (``attempt > 1``) records with ``force=True`` so a crashed / partial
    replay is truncated and cleanly overwritten. A timeout is a distinct,
    retryable outcome; any other ``Exception`` (provider / transport / engine
    crash) is presumed transient on the real path and retried; a normal return
    whose replay carries NO ``game_over`` stamp (the parse-fold abort) is a
    degraded recording and retried. Two outcomes are terminal, never retried: a
    ``TICK_BUDGET_REACHED`` game (deterministic non-decisive outcome — the
    replay has no ``game_over`` row by design; accepted with
    ``tick_budget_reached=True``) and :class:`~llm.budget.BudgetExceededError`
    (a metering stop — re-recording would re-spend the per-game cap; it
    propagates unretried). ``KeyboardInterrupt`` / ``SystemExit`` are not
    ``Exception`` and propagate.

    ``force_first_attempt`` (Task 18.31) truncates a pre-existing replay on the
    FIRST attempt too: a resume that refused to skip an element is by
    definition re-recording over bytes it declined to certify.
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
            report = run_tournament_eval(
                seeds=[seed],
                output_dir=candidate_dir,
                game_map=game_map,
                agent_factory=agent_factory,
                num_players=config.num_players,
                num_impostors=config.num_impostors,
                tasks_per_crewmate=config.tasks_per_crewmate,
                max_ticks=config.max_ticks,
                force=force_first_attempt or attempt > 1,
                tactical_policy_stamp=stamp,
                meeting_runner_factory=runner_factory,
            )
        except RealPathMeetingTimeoutError as exc:
            timed_out += 1
            error_types.append(type(exc).__name__)
            last_exc = exc
            continue
        except BudgetExceededError:
            # A metering stop, not a transient crash: a fresh GameBudget is
            # built per attempt, so retrying would re-spend the per-game cap
            # up to max_attempts times on a paid provider. Propagate unretried.
            raise
        except Exception as exc:  # noqa: BLE001 - retried; exhaustion is fail-loud
            error_types.append(type(exc).__name__)
            last_exc = exc
            continue
        tick_budget = report.games[0].reason == _TICK_BUDGET_REASON
        if not tick_budget and read_tactical_policy_stamp(replay_path) is None:
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
            tick_budget_reached=tick_budget,
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
    """Read every decisive seed's stamp back from bytes (the 17.14 invariants).

    ``seeds`` are the DECISIVE seeds only — a tick-budget game writes no
    ``game_over`` row, so it carries no stamp bytes by design and is excluded by
    the caller. Fails loud (RealPathStampError) when no decisive seed exists
    (nothing on disk can prove which policy produced the bytes), on a missing
    stamp, on a read-back ``weights_sha256`` that disagrees with the computed
    genome digest, or on a non-uniform stamp across seeds. Returns the uniform
    stamp and the verified game count.
    """

    if not seeds:
        raise RealPathStampError(
            f"candidate {label!r}: every seed hit the tick budget, so no "
            "game_over bytes exist to prove provenance (stamp read-back "
            "requires at least one decisive game)"
        )
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
    resume: bool = False,
    prescreen: Sequence[PreScreenQuote] | None = None,
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

    ``resume=True`` (Task 18.31) makes an interrupted leg re-enterable: the
    candidate dirs may already exist, and each (candidate, seed) element whose
    recording satisfies the whole CONJUNCTIVE predicate in
    :func:`_resume_skip_reason` is skipped; every other element re-records with
    ``force=True``. The default (``False``) keeps the write-once discipline
    exactly as before — a pre-existing candidate dir fails loud. A resume also
    refuses a candidate dir holding replays for seeds OUTSIDE this tranche:
    the scoring entry points fold the whole DIRECTORY, so an unrequested replay
    would silently enter the committed row.

    ``prescreen`` records the blocker-4 spend advice NATIVELY: its quotes are
    written to a tranche/invocation-keyed record and logged into this leg's
    append-only log BEFORE any seed is recorded, which is the
    pre-screen-before-spend ordering evidence §12 Errata item 10 found missing.

    Every invocation stamps a manifest (``leg-<tranche>-<invocation>.json``) and
    appends its events to ``leg-log.jsonl`` under ``work_dir``, including a
    terminal ``leg-failed`` event when the leg raises.
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

    # Preflight the watchability floor block BEFORE any recording: an unknown
    # baseline_id / roster would otherwise only surface at scoring time, after
    # every real-provider seed for the candidate has already been recorded.
    # Mirrors compute_watchability's own lookup (baseline id, then the
    # "{num_players}p{num_impostors}i" roster key).
    roster_key = f"{resolved_config.num_players}p{resolved_config.num_impostors}i"
    baseline_floors = _BASELINE_SUPPLY_FLOORS.get(resolved_config.baseline_id)
    if baseline_floors is None:
        raise ValueError(
            "no supply-floor block pinned for baseline_id "
            f"{resolved_config.baseline_id!r} "
            f"(known: {sorted(_BASELINE_SUPPLY_FLOORS)}); refusing to record"
        )
    if roster_key not in baseline_floors:
        raise ValueError(
            f"baseline {resolved_config.baseline_id!r} has no supply-floor "
            f"block for roster {roster_key!r} (known: {sorted(baseline_floors)}); "
            "refusing to record"
        )

    # The ranking path is preflighted HERE, before the first game: the
    # exclusive open at the end is race protection, but on its own it would let
    # an operator's path typo burn a whole 30–40 h leg before failing (Codex
    # review on PR #314). Both checks stand — this one saves the budget, that
    # one closes the window between them.
    if ranking_path.exists():
        raise RealPathRerankError(
            f"a committed ranking already exists at {ranking_path}; this leg is "
            "already recorded and its rows are never rewritten — refusing before "
            "any game is spent (point --ranking-path at a fresh file)"
        )

    # The leg's own invocation stamp + append-only log, opened AFTER every
    # preflight (so a refused configuration still leaves work_dir untouched)
    # and BEFORE any recording (so the pre-screen quotes are provably logged
    # before the first game's spend — the blocker-4 ordering evidence).
    tranche = tranche_key(seeds_tuple)
    invocation, manifest_path = _open_leg_manifest(
        work_dir,
        tranche=tranche,
        seeds=seeds_tuple,
        mode=mode,
        resume=resume,
        candidates=candidates,
        config=resolved_config,
        ranking_path=ranking_path,
    )
    leg_log = RealPathLegLog(
        work_dir / LEG_LOG_FILENAME, tranche=tranche, invocation=invocation
    )
    leg_log.emit(
        "leg-start",
        candidates=list(labels),
        manifest=str(manifest_path),
        mode=mode,
        resume=resume,
        seeds=list(seeds_tuple),
    )
    try:
        if prescreen is not None:
            # Coverage BEFORE the record and the log: evidence that names the
            # wrong candidates is worse than no evidence, because it reads as
            # proof (Codex review on PR #314).
            _validate_prescreen_coverage(prescreen, candidates)
            for quote in prescreen:
                leg_log.emit(
                    "prescreen-quote",
                    label=quote.label,
                    note=quote.note,
                    predicted_flags_per_meeting=quote.predicted_flags_per_meeting,
                    predicted_floors_pass=quote.predicted_floors_pass,
                    weights_sha256=quote.weights_sha256,
                )
            prescreen_path = write_prescreen_record(
                work_dir,
                seeds=seeds_tuple,
                quotes=prescreen,
                invocation=invocation,
            )
            leg_log.emit(
                "prescreen-record",
                path=str(prescreen_path),
                quotes=len(prescreen),
            )

        payloads: list[_CandidatePayload] = []
        for index, candidate in enumerate(candidates):
            stamp = _candidate_stamp(candidate)
            digest = stamp.weights_sha256
            agent_factory = _build_agent_factory(candidate, game_map=resolved_map)
            candidate_dir = work_dir / f"{index:03d}-{_safe_slug(candidate.label)}"
            candidate_dir.mkdir(parents=True, exist_ok=resume)
            if resume:
                _refuse_foreign_replays(
                    candidate_dir, seeds=seeds_tuple, label=candidate.label
                )
            leg_log.emit(
                "candidate-start",
                dir=str(candidate_dir),
                index=index,
                label=candidate.label,
                weights_sha256=digest,
            )
            telemetry = tuple(
                _record_or_resume_seed(
                    seed=seed,
                    candidate=candidate,
                    candidate_dir=candidate_dir,
                    game_map=resolved_map,
                    agent_factory=agent_factory,
                    stamp=stamp,
                    digest=digest,
                    config=resolved_config,
                    base_meeting_runner_factory=meeting_runner_factory,
                    resume=resume,
                    leg_log=leg_log,
                )
                for seed in seeds_tuple
            )
            _drop_audit_sidecars(candidate_dir)
            _write_roster_json(candidate_dir, resolved_config)
            decisive_seeds = tuple(
                entry.seed for entry in telemetry if not entry.tick_budget_reached
            )
            read_stamp, verified = _verify_stamps(
                candidate_dir,
                seeds=decisive_seeds,
                expected_digest=digest,
                label=candidate.label,
            )
            validity = run_validity_gate(candidate_dir)
            watchability = compute_watchability(
                candidate_dir, baseline_id=resolved_config.baseline_id
            )
            core = measure_baseline.measure_baseline(candidate_dir)
            leg_log.emit(
                "candidate-scored",
                label=candidate.label,
                mean_score=watchability.mean_score,
                referee_passed=watchability.referee_passed,
                resumed_seeds=[entry.seed for entry in telemetry if entry.resumed],
                stamp_verified_games=verified,
                validity_passed=validity.passed,
            )
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
            _selection_score(payload.validity, payload.watchability)
            for payload in payloads
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
        _publish_ranking(
            ranking_path, "".join(row.to_json_line() + "\n" for row in rows)
        )
        for row in rows:
            leg_log.emit(
                "rank",
                label=row.label,
                rank=row.rank,
                referee_passed=row.referee_passed,
                selection_score=row.selection_score,
                validity_passed=row.validity_passed,
            )
        leg_log.emit("leg-done", ranking_path=str(ranking_path), rows=len(rows))
    except BaseException as exc:
        # The hour-40 provider 503 leaves its own record: the leg log states
        # exactly where the leg stopped, which is what a resume reads next.
        leg_log.emit("leg-failed", error=type(exc).__name__, message=str(exc))
        raise
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
    "LEG_LOG_FILENAME",
    "LEG_LOG_SCHEMA_VERSION",
    "LEG_MANIFEST_FILENAME_STEM",
    "LEG_MANIFEST_SCHEMA_VERSION",
    "MODE_CHAMPION_TRACE",
    "MODE_TOP_K",
    "PRESCREEN_ADVICE_NOTE",
    "PRESCREEN_FILENAME_STEM",
    "PRESCREEN_SCHEMA_VERSION",
    "SCHEMA_VERSION",
    "PreScreenQuote",
    "PreScreenRecord",
    "RealPathCandidate",
    "RealPathLegLog",
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
    "tranche_key",
    "write_prescreen_record",
]
