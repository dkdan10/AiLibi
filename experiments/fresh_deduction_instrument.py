"""The fresh-model deduction instrument: paired arms over the frozen held-out set.

This module is the RUNNER side of the design
``audits/deduction-candidate/preregistration.md`` describes and
``audits/deduction-candidate/execution-manifest.md`` binds. It runs one meeting
per frozen held-out prefix under two arms and scores the ballots, and it does so
through the shipped public entry points only:
:class:`~orchestrator.game.HeadlessGame`,
:func:`~orchestrator.game.build_default_meeting_runner` and the public
:class:`~orchestrator.game.TacticalAgent`.

What this module is NOT
-----------------------

* It is not the held-out generator. :mod:`experiments.held_out_prefixes` is,
  it was frozen by a different session's pull request, and this module only
  regenerates the set from that frozen band and checks it against
  ``audits/deduction-candidate/held-out/manifest.json``
  (:func:`verify_frozen_set`).
* It is not one of the two committed MECHANICS_ONLY harnesses
  (:mod:`experiments.deduction_evaluation`,
  :mod:`experiments.investigation_evaluation`). Their refusal of real providers
  is their own acceptance criterion; nothing here reuses, subclasses or relaxes
  it, and neither file is imported.
* It is not an authorization to spend. Running it against a real provider
  requires an explicit :class:`LiveRunInvocation` naming the committed execution
  manifest, re-verified by path and digest in
  :func:`assert_live_run_is_authorized`, AND :data:`LIVE_RUN_FLAG` on the command
  line. Tests do construct invocations — proving each refusal is what they are
  for — but none of them reaches a provider: no committed file outside this
  module and the manifest's documented command carries :data:`LIVE_RUN_FLAG` (a
  tree scan holds that), :func:`run_dry` refuses an invocation outright, and the
  gate reads the CLIENT's real type rather than the provider label it was given.
  The client a live run uses is built from the authorized provider and model
  (:func:`build_authorized_client`), never from the ambient environment, and
  cannot be constructed before the frozen set is verified — the verified
  :class:`FrozenSet` is that function's first argument.

Two things this module deliberately never does with a held-out prefix: print it
and serialize it. Inspecting a held-out input converts it to development data
(the preregistration's "Use the known seven cases only for
development/operational checks"), so a prefix is consumed only as a
:class:`~experiments.held_out_prefixes.HeldOutPrefix` object driving the engine,
and :func:`assert_report_holds_no_prefix_bytes` refuses to emit a report that
carries one.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from types import MappingProxyType
from typing import Final, Literal, Self

from pydantic import BaseModel, ConfigDict

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.perception import ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from experiments.held_out_prefixes import (
    MANIFEST_PATH,
    MAX_TICKS,
    PREREGISTERED_BAND,
    TEMPORAL_OBSERVATION_VERSION,
    GeneratedSet,
    HeldOutPrefix,
    PrefixRoster,
    SeedBand,
    assert_no_legacy_body_handles,
    canonical_prefix_json,
    generate,
    legacy_body_handles,
    prefix_sha256,
)
from experiments.held_out_prefixes import AUTHORIZED_ROSTER as FROZEN_PREFIX_ROSTER
from llm.budget import GameBudget
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from llm.provider import extract_parse_failure
from meetings.manager import (
    DEFAULT_TURN_MAX_TOKENS,
    DEFAULT_VOTE_MAX_TOKENS,
    MeetingConfig,
)
from meetings.schemas import (
    MeetingTurn,
    ModelAuthoredVoteBallot,
    TurnAnnotationKind,
    VoteBallot,
)
from observation.action_intent import ActionIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import (
    HEADLESS_MEETING_DEADLINES,
    HeadlessGame,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    FailedCallReplayEntry,
    MeetingReplayEntry,
    ReplayLogEntry,
    read_all_entries,
    recorded_experiment_config,
    recorded_temporal_observation_version,
)
from orchestrator.run_limits import RunDeadline, RunDeadlineExceeded
from orchestrator.scheduler import TickScheduler

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR: Final[Path] = _REPO_ROOT / "scripts"
# ``scripts/`` has no ``__init__.py`` and ``mypy_path = "scripts"`` resolves its
# modules as top-level names, so importing ``scripts.paired_stats`` would make
# mypy see one file under two module names. Mirrors the bootstrap in
# scripts/check_doc_facts.py and scripts/verify_ml_evidence.py.
for _bootstrap_path in (_REPO_ROOT, _SCRIPTS_DIR):
    if str(_bootstrap_path) not in sys.path:
        sys.path.insert(0, str(_bootstrap_path))

from paired_stats import exact_mcnemar_p  # noqa: E402


# ---------------------------------------------------------------------------
# The authorized limits (tasks/work/fresh-deduction-authorization.md)
# ---------------------------------------------------------------------------
#
# Every constant below is a value the owner authorized by merging #437 on
# 2026-09-07 (merge commit 0f49d8e6; ruling B.12 in
# tasks/owner-decisions-2026-09-07.md). They are copied here so the instrument
# ENFORCES the manifest rather than describing it, and
# tests/experiments/test_fresh_deduction_instrument.py asserts the manifest
# quotes each of them. Changing one here without a new authorization is a
# spending decision, not a refactor.

#: The provider name the manifest binds. Anything else needs its own manifest.
AUTHORIZED_PROVIDER: Final[str] = "featherless"

#: The served model id, locked 2026-07-12 (Task 16.2).
AUTHORIZED_MODEL: Final[str] = "Qwen/Qwen3.6-27B"

#: The prompt set the model lock carries.
AUTHORIZED_PROMPT_SET: Final[str] = "qwen3_6_27b"

#: The shipped per-call output caps, unchanged. The instrument refuses a call
#: asking for more than the turn cap and refuses a ``max_tokens`` that is
#: neither shipped value, so "the shipped defaults unchanged" is a check rather
#: than a claim.
AUTHORIZED_TURN_MAX_TOKENS: Final[int] = DEFAULT_TURN_MAX_TOKENS
AUTHORIZED_VOTE_MAX_TOKENS: Final[int] = DEFAULT_VOTE_MAX_TOKENS

#: The sampling temperatures the run draws at. The preregistration asks the
#: manifest to bind the SAMPLING CONFIGURATION, and a temperature the run
#: inherits from a module default is not bound: a later edit to
#: ``meetings.manager`` would move the hosted sampling distribution of a frozen
#: design without moving this manifest. So they are written here as numbers, the
#: instrument passes them in an explicit :class:`~meetings.manager.MeetingConfig`
#: rather than letting the manager default them, and
#: ``tests/experiments/test_fresh_deduction_instrument.py`` asserts they are
#: still the shipped values — a default change then breaks a test rather than
#: the run.
AUTHORIZED_TURN_TEMPERATURE: Final[float] = 0.4
AUTHORIZED_VOTE_TEMPERATURE: Final[float] = 0.2

#: The run-level hard stop, both token dimensions.
AUTHORIZED_RUN_MAX_INPUT_TOKENS: Final[int] = 2_400_000
AUTHORIZED_RUN_MAX_OUTPUT_TOKENS: Final[int] = 200_000

#: The per-unit hard stop, charged upward into the run-level parent.
AUTHORIZED_UNIT_MAX_INPUT_TOKENS: Final[int] = 45_000
AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS: Final[int] = 4_000

#: 4 h of model work inside a 6 h elapsed window. Two different clocks: the
#: elapsed one is :class:`~orchestrator.run_limits.RunDeadline`; the work one is
#: the summed provider-call wall :class:`_InstrumentClient` accumulates.
AUTHORIZED_MODEL_WORK_SECONDS: Final[float] = 4 * 60 * 60
AUTHORIZED_ELAPSED_SECONDS: Final[float] = 6 * 60 * 60

#: Bookkeeping, not an enforcement mechanism: the provider's zero pre-flight rate
#: disables ``BudgetedLLMClient``'s USD dimension entirely.
AUTHORIZED_MAX_COST_USD: Final[float] = 0.0

#: The roster the token budget is sized on. A different roster invalidates it.
AUTHORIZED_ROSTER_PLAYERS: Final[int] = 4
AUTHORIZED_ROSTER_IMPOSTORS: Final[int] = 1
AUTHORIZED_LIVING_VOTERS: Final[int] = 3

#: One unit at a time. Concurrency would change both the wall projection and the
#: provider's concurrency accounting the cost statement rests on.
AUTHORIZED_EXECUTION_MODE: Final[Literal["sequential"]] = "sequential"

#: The execution manifest this instrument is bound to. A live run names this
#: exact path (:class:`LiveRunInvocation`).
EXECUTION_MANIFEST_PATH: Final[str] = "audits/deduction-candidate/execution-manifest.md"

#: The runner's explicit live-run flag, defined once. :func:`main` registers it
#: from here and the tree-scan test searches for THIS value, so the scan needs no
#: second copy of the string to look for — and therefore no exemption for the
#: file that does the looking.
LIVE_RUN_FLAG: Final[str] = "--i-am-the-runner"


class RunLimits(BaseModel):
    """The six numbers that bound a run, as one frozen value object.

    A parameter rather than six constants read from module scope, because a
    planted overrun has to be reachable from a test without rewriting the
    module — and because a limits object can then be COMPARED to the authorized
    one. :func:`assert_live_run_is_authorized` does exactly that, so the only
    limits a live provider ever runs under are :data:`AUTHORIZED_LIMITS`, while
    the offline gate can plant an exhaustion freely.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    run_max_input_tokens: int
    run_max_output_tokens: int
    unit_max_input_tokens: int
    unit_max_output_tokens: int
    max_cost_usd: float
    elapsed_seconds: float
    model_work_seconds: float


AUTHORIZED_LIMITS: Final[RunLimits] = RunLimits(
    run_max_input_tokens=AUTHORIZED_RUN_MAX_INPUT_TOKENS,
    run_max_output_tokens=AUTHORIZED_RUN_MAX_OUTPUT_TOKENS,
    unit_max_input_tokens=AUTHORIZED_UNIT_MAX_INPUT_TOKENS,
    unit_max_output_tokens=AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS,
    max_cost_usd=AUTHORIZED_MAX_COST_USD,
    elapsed_seconds=AUTHORIZED_ELAPSED_SECONDS,
    model_work_seconds=AUTHORIZED_MODEL_WORK_SECONDS,
)


class SamplingConfig(BaseModel):
    """The draw itself: the two caps and the two temperatures, as one value.

    Separate from :class:`RunLimits` because it is not a limit — it is the
    sampling distribution the manifest binds. Held as a value object for the
    same two reasons: a live run is refused unless it equals
    :data:`AUTHORIZED_SAMPLING`, and the report carries it, so a result names
    the distribution it was drawn from rather than whatever the meeting layer's
    defaults were on the day.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    turn_max_tokens: int
    turn_temperature: float
    vote_max_tokens: int
    vote_temperature: float

    def meeting_config(self) -> MeetingConfig:
        """The meeting configuration these values are served through.

        The deadlines are the HEADLESS ones on purpose: passing any explicit
        :class:`~meetings.manager.MeetingConfig` opts back into the interactive
        30 s per-turn wall (``orchestrator/game.py:1425-1435``), and a recording
        that loses a turn to a wall-clock race is exactly the audit-gp-2 failure
        the headless default exists to prevent. The run's own wall limits are
        the two clocks the authorization names, not this one.
        """

        return MeetingConfig(
            deadlines=HEADLESS_MEETING_DEADLINES,
            turn_max_tokens=self.turn_max_tokens,
            turn_temperature=self.turn_temperature,
            vote_max_tokens=self.vote_max_tokens,
            vote_temperature=self.vote_temperature,
        )


AUTHORIZED_SAMPLING: Final[SamplingConfig] = SamplingConfig(
    turn_max_tokens=AUTHORIZED_TURN_MAX_TOKENS,
    turn_temperature=AUTHORIZED_TURN_TEMPERATURE,
    vote_max_tokens=AUTHORIZED_VOTE_MAX_TOKENS,
    vote_temperature=AUTHORIZED_VOTE_TEMPERATURE,
)


# ---------------------------------------------------------------------------
# The preregistered analysis, frozen before any outcome is inspected
# ---------------------------------------------------------------------------

#: The one binary the paired test is computed on. Named here so the manifest and
#: the code cannot drift, and so no second outcome can be promoted to primary
#: after the fact.
PRIMARY_OUTCOME: Final[str] = "supported_correct_ejection"

PRIMARY_OUTCOME_RUBRIC: Final[str] = (
    "A unit scores 1 when its meeting ejected the player whose hidden role is "
    "IMPOSTOR and every ballot naming that player carried a citation that is "
    "both PRESENT in that voter's own prompts (the supported grader) and "
    "RELEVANT to the ejected player (the citation-relevance rule); otherwise 0. "
    "Role-correctness alone, support alone and relevance alone are reported "
    "beside it and none of them is the primary outcome."
)

#: The net paired difference (b - c over 50 paired units) below which a
#: difference is not acted on, whatever its p value.
MINIMUM_ACTIONABLE_EFFECT_UNITS: Final[int] = 10

#: Two-sided alpha for the exact paired McNemar test.
DECISION_ALPHA: Final[float] = 0.05

DECISION_RULE: Final[str] = (
    "combined_accounts advances to an explicitly scoped adopting review only if "
    "ALL THREE hold on the 50 paired units: the two-sided exact McNemar p over "
    "the discordant pairs (scripts/paired_stats.py::exact_mcnemar_p) is below "
    "0.05; the net paired difference b - c is at least 10 units; and the "
    "candidate's net increase in wrongful crew ejections over the reference arm "
    "is no larger than that net paired difference. Any other result is "
    "inconclusive, and inconclusive is not success. A result in either "
    "direction is a measurement, never an adoption: adoption stays a separate "
    "owner decision on a separate card."
)

#: The preregistration (`audits/deduction-candidate/preregistration.md:116-118`,
#: `:236-239`) requires the manifest to bind the ACCEPTABLE TRADEOFFS, and names
#: the wrongful decision as one of them. This is that bound, frozen with the rest
#: of the analysis and before any held-out outcome exists.
WRONGFUL_EJECTION_TRADEOFF: Final[str] = (
    "A wrongful ejection is a unit whose meeting ejected a player whose hidden "
    "role is CREWMATE. The candidate may not buy its supported-correct "
    "ejections by ejecting more innocents: its net increase in wrongful "
    "ejections over the reference arm, on the same 50 paired units, must be no "
    "larger than its net paired gain b - c on the primary outcome. One extra "
    "wrongful ejection has to be paid for by at least one extra "
    "supported-correct ejection. The bound is one-for-one because the failure it "
    "guards against is a candidate that merely raises the ejection RATE: "
    "converting reference-arm skips into ejections lifts both counts together, "
    "and a candidate whose wrongful count rises at least as fast as its "
    "supported-correct count has moved the meeting's willingness to eject rather "
    "than its deduction. No ratio below one is asserted, because this design "
    "resolves 50 paired units and a finer bound would be a number the sample "
    "cannot carry."
)

MINIMUM_ACTIONABLE_EFFECT_RATIONALE: Final[str] = (
    "10 of 50 is chosen for the resolution of this design, not for a headline. "
    "The smallest net difference the exact test can call at all on 50 paired "
    "units is 6 with no discordant pairs the other way (b=6, c=0 gives "
    "p=0.03125; b=5, c=0 gives p=0.0625), so a bar of 6 would be the "
    "significance boundary restated. A net of 10 stays below 0.05 for every "
    "discordant total up to 20 (b=15, c=5 gives p=0.0414) and fails at 22 "
    "(b=16, c=6 gives p=0.0525), so it is a difference that survives the noise "
    "this design can actually carry. Every figure in this paragraph is "
    "reproducible with scripts/paired_stats.py::exact_mcnemar_p."
)

STOP_RULE: Final[str] = (
    "The run stops, retains its partial evidence and unresolved accounting, and "
    "authorizes no retry and no widening of any limit, on any of: a token "
    "budget exhausted at either the per-unit or the run level; the elapsed wall "
    "deadline or the model-work window, the latter cutting off the attempt in "
    "flight rather than one call later; a per-call response that reached its "
    "output cap (a truncation is a stop, not a datum); a held-out digest or "
    "skip that differs from the frozen manifest; a rendered prompt or "
    "regenerated prefix matching the legacy body handle; a unit whose recorded "
    "observation clock or experiment config is not the arm's; or a recorded "
    "meeting default whose phase and trigger this instrument cannot classify. "
    "A meeting-internal default is NOT itself a stop. The meeting layer's "
    "shipped fail-soft substitutes a placeholder turn or a marked SKIP ballot "
    "for a payload that failed schema validation, at an accepted rate of about "
    "1 in 50 calls, and a fixed 50-unit paired sample cannot be abandoned for a "
    "substitution the engine is designed to make. Every such substitution is "
    "instead counted per arm and per unit — turns and votes separately, by "
    "trigger, with the units carrying any — and reported beside decision "
    "coverage, so it is visible rather than silently replaced. No stop "
    "condition reads an outcome: the 50 paired units are a fixed sample with no "
    "interim analysis and no optional stopping, so nothing here can be tripped "
    "by a result the run has produced."
)

SPEND_RECONCILIATION: Final[str] = (
    "After each unit the recorded spend is reconciled against the enforced "
    "budget snapshot over every call the provider charged: the meeting row's "
    "resolved calls plus every failed attempt the replay records with usage — a "
    "payload a real provider validated and refused before the recording client "
    "could log it, whose tokens the budget charged off the parse-failure "
    "metadata. A zero-spend default marker is not a charged call, so a "
    "manager-side validation of a returned payload, whose spend the meeting row "
    "already carries, is counted once and not twice. This is the token budget's "
    "accounting check rather than a limit of its own: what it can find is a "
    "unit whose recorded calls do not add up to what the budget charged, and "
    "that unit stops the run the way every other unit failure does."
)

BUDGET_CAP_READBACK: Final[str] = (
    "After each unit both budgets are also read back against the caps they were "
    "built with, because one kind of charge never meets a pre-flight: a call the "
    "provider billed and then refused on its own schema validation is charged "
    "after the fact, off the parse-failure metadata, and the resulting overrun is "
    "downgraded to a note on the exception the meeting layer then fail-softs. On "
    "a unit's last call the per-unit ceiling would otherwise be crossed with the "
    "budget then discarded, and on a run's last call the run ceiling with nothing "
    "further to pre-flight. A budget found past its cap stops the run on the unit "
    "that crossed it: the tokens are already spent, and the stop is what keeps "
    "the next unit from spending more."
)

_ANALYSIS_FREEZE_NOTE: Final[str] = (
    "PRIMARY_OUTCOME, DECISION_RULE, MINIMUM_ACTIONABLE_EFFECT_UNITS, "
    "WRONGFUL_EJECTION_TRADEOFF and STOP_RULE are module constants and the "
    "execution manifest quotes them verbatim, so the analysis is frozen in code "
    "and in the record before any held-out outcome exists."
)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class InstrumentError(RuntimeError):
    """Base class for every refusal this instrument raises."""


class FrozenSetMismatch(InstrumentError):
    """The regenerated held-out set differs from the frozen manifest."""


class LiveRunNotAuthorized(InstrumentError):
    """A non-fake provider was reached without an explicit live invocation."""


class PerCallCapExceeded(InstrumentError):
    """A call asked for, or a response reached, more than the authorized cap."""


class ProviderIdentityMismatch(InstrumentError):
    """A response came back from a model this manifest does not authorize.

    Checked on the response rather than on the request, because the request only
    says what was ASKED for: a hosted endpoint that silently serves a different
    checkpoint would otherwise be discovered in the report's ``model_ids`` after
    the whole run had been spent.
    """


class BudgetExhausted(InstrumentError):
    """A charge already applied left a token budget past its authorized cap.

    Distinct from :class:`~llm.budget.BudgetExceededError`, which the budget
    raises on the PRE-FLIGHT that would cross a cap and which stops the call
    before it is made. This one is raised on a charge that was applied without a
    pre-flight to refuse it — a call the provider billed and then refused on its
    own schema validation, whose overrun ``llm/budgeted_client.py`` downgrades to
    a note — so the tokens are already spent when it fires. Both are the same
    stop condition in ``STOP_RULE``; only the moment differs.
    """


class ProvenanceMismatch(InstrumentError):
    """A unit's recorded identity is not the arm it was run under."""


class PrefixBytesLeaked(InstrumentError):
    """A report payload carries held-out prefix bytes."""


@dataclass(frozen=True)
class PartialRun:
    """Everything a stopped run can honestly say about itself.

    Deliberately counts and identifiers only: the units that completed, what
    each arm spent, and the limit that stopped the run. No prefix, step, room or
    tick appears here, because a stop is not a licence to publish an input.
    """

    reason: str
    completed_units: int
    planned_units: int
    usage_by_arm: Mapping[str, ArmUsage]
    elapsed_seconds: float
    model_work_seconds: float

    def describe(self) -> str:
        spent = ", ".join(
            f"{arm}: {usage.calls} calls, {usage.input_tokens} in, "
            f"{usage.output_tokens} out"
            for arm, usage in sorted(self.usage_by_arm.items())
        )
        return (
            f"{self.reason}; {self.completed_units}/{self.planned_units} units "
            f"completed, {self.elapsed_seconds:.1f}s elapsed, "
            f"{self.model_work_seconds:.1f}s model work; {spent or 'no spend'}"
        )


class InstrumentAborted(InstrumentError):
    """A limit stopped the run. Carries the partial state, never a retry.

    Raised instead of returning a short report so a caller cannot mistake a
    stopped run for a completed one. ``partial`` is what the run may report;
    the preregistration's "Reaching an authorized time, token or cost limit
    stops new calls, retains partial evidence and unresolved accounting, and
    does not trigger unbudgeted retries or silent expansion" is the rule this
    class implements.
    """

    def __init__(self, partial: PartialRun) -> None:
        super().__init__(partial.describe())
        self.partial = partial


# ---------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------

ArmName = Literal["repaired_clock", "combined_accounts"]


class InstrumentArm(BaseModel):
    """One arm: an experiment config plus the environment that renders it.

    Both arms run the SAME temporal clock (version 2) and the same evidence
    reasoning (version 2). ``combined_accounts`` adds public accounts and
    attributed testimony and nothing else, so a difference between the two is a
    difference in those two channels rather than in the clock they share.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: ArmName
    experiment_config: RecordedExperimentConfig
    temporal_version: Literal[2] = TEMPORAL_OBSERVATION_VERSION

    def environment(self, *, provider: str) -> Mapping[str, str]:
        """The substrate environment this arm renders under, stated not inherited.

        Built per call and returned read-only for the same reason
        :func:`experiments.held_out_prefixes.filter_environment` does it: a
        developer's shell must not be able to move which channel an arm renders.
        """

        config = self.experiment_config
        return MappingProxyType(
            {
                "AILIBI_LLM_PROVIDER": provider,
                "AILIBI_PROMPT_SET": AUTHORIZED_PROMPT_SET,
                "AILIBI_TEMPORAL_OBSERVATIONS": str(self.temporal_version),
                "AILIBI_EVIDENCE_REASONING": str(
                    config.evidence_reasoning_version or 0
                ),
                "AILIBI_PUBLIC_ACCOUNTS": str(config.public_account_version or 0),
                "AILIBI_ATTRIBUTED_TESTIMONY": str(
                    config.attributed_testimony_version or 0
                ),
                "AILIBI_BOUNDED_REBUTTAL": str(config.bounded_rebuttal_version or 0),
            }
        )


def instrument_arms() -> tuple[InstrumentArm, InstrumentArm]:
    """The two paired arms, reference first.

    Investigation is deliberately absent: it changes the world the prefix
    froze, so it cannot be paired on an identical prefix and the card puts it
    out of scope.
    """

    return (
        InstrumentArm(
            name="repaired_clock",
            experiment_config=RecordedExperimentConfig(
                format_version=2, evidence_reasoning_version=2
            ),
        ),
        InstrumentArm(
            name="combined_accounts",
            experiment_config=RecordedExperimentConfig(
                format_version=2,
                evidence_reasoning_version=2,
                public_account_version=1,
                attributed_testimony_version=1,
            ),
        ),
    )


#: The arm the per-unit budget is sized on. Both arms get the SAME per-unit cap
#: so a cap cannot advantage one of them; the reference arm renders the larger
#: prompt (no accounts block to compress the memory render), so it is the one
#: the cap is sized on.
BUDGET_SIZING_ARM: Final[ArmName] = "repaired_clock"


# ---------------------------------------------------------------------------
# The live-run gate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LiveRunInvocation:
    """The explicit, per-run statement that a live provider may be reached.

    There is no default value, no environment variable and no flag combination
    that produces one implicitly: :func:`main` builds one only from
    ``--provider`` together with ``--execution-manifest`` and
    ``--i-am-the-runner``, and :func:`run_dry` refuses one. That is what makes
    "no test, CI job or dry run performs the live invocation" a property of the
    code rather than a promise.
    """

    manifest_path: Path
    manifest_sha256: str
    provider: str
    model: str

    @classmethod
    def naming(
        cls,
        manifest_path: Path,
        *,
        provider: str,
        model: str,
        repo_root: Path = _REPO_ROOT,
    ) -> Self:
        """Build an invocation from the manifest on disk, or refuse.

        Refuses a manifest that is not THE committed manifest — the path is
        compared against ``repo_root / EXECUTION_MANIFEST_PATH`` in full, not by
        its last components, because a same-named file anywhere on disk would
        otherwise authorize a run while carrying none of the owner's limits.
        Refuses one that is absent, or that does not carry the authorized
        provider, model and prompt set.

        The digest this records is re-checked against the same file at the
        authorization boundary (:func:`assert_live_run_is_authorized`), so a
        directly constructed dataclass does not skip the check.
        """

        expected = (repo_root / EXECUTION_MANIFEST_PATH).resolve()
        resolved = manifest_path.resolve()
        if resolved != expected:
            raise LiveRunNotAuthorized(
                "a live run names the authorized execution manifest "
                f"{expected}, got {resolved}"
            )
        if not resolved.is_file():
            raise LiveRunNotAuthorized(
                f"execution manifest is missing: {manifest_path}"
            )
        text = resolved.read_text(encoding="utf-8")
        for required in (provider, model, AUTHORIZED_PROMPT_SET):
            if required not in text:
                raise LiveRunNotAuthorized(
                    f"the execution manifest does not name {required!r}; it "
                    "authorizes no run of this shape"
                )
        return cls(
            manifest_path=resolved,
            manifest_sha256=hashlib.sha256(resolved.read_bytes()).hexdigest(),
            provider=provider,
            model=model,
        )


def assert_live_run_is_authorized(
    *,
    provider: str,
    invocation: LiveRunInvocation | None,
    limits: RunLimits = AUTHORIZED_LIMITS,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
    units: int | None = None,
    repo_root: Path = _REPO_ROOT,
) -> None:
    """Refuse any non-fake provider without an explicit live invocation.

    ``fake`` is the only provider that passes without one, and it is the default
    everywhere in this module. Every other value — including one the owner has
    authorized in the manifest — needs the runner to say so at the call, because
    the manifest authorizes LIMITS and the invocation is the run.

    Nothing here is taken on the invocation's word. The manifest it names is
    re-read from ``repo_root`` and re-hashed, so a hand-built
    :class:`LiveRunInvocation` carrying a path, a digest or a model of its own
    does not pass; and ``units`` must be ``None``, because a live run is the
    whole frozen set. A subset is the pilot the authorization card, this card
    and the manifest all refuse — and it would spend part of the held-out set
    outside the 50-pair design while leaving the rest held out.
    """

    if provider == "fake":
        if invocation is not None:
            raise LiveRunNotAuthorized(
                "a fake-provider run takes no live invocation; the dry run is "
                "the mechanics check and never the authorized run"
            )
        return
    if invocation is None:
        raise LiveRunNotAuthorized(
            f"provider {provider!r} is a live provider and this run carries no "
            f"LiveRunInvocation naming {EXECUTION_MANIFEST_PATH}. The manifest "
            "authorizes limits; only an explicit runner invocation authorizes a "
            "call, and no test, CI job or dry run performs one."
        )
    if invocation.provider != provider:
        raise LiveRunNotAuthorized(
            f"the live invocation names provider {invocation.provider!r} but the "
            f"run asks for {provider!r}"
        )
    if provider != AUTHORIZED_PROVIDER:
        raise LiveRunNotAuthorized(
            f"provider {provider!r} is not the authorized provider "
            f"{AUTHORIZED_PROVIDER!r}; a different provider needs its own "
            "authorization and its own manifest"
        )
    if units is not None:
        raise LiveRunNotAuthorized(
            f"a live run is the whole frozen set; this one asks for {units} "
            "prefixes. No pilot, smoke run or retry is authorized, including on "
            "flat-rate service, and a subset would spend part of a held-out set "
            "the rest of which is still held out. --units is a dry-run knob."
        )
    if limits != AUTHORIZED_LIMITS:
        raise LiveRunNotAuthorized(
            "a live run runs under the authorized limits exactly; the limits "
            "this run carries are not the ones the owner authorized"
        )
    if sampling != AUTHORIZED_SAMPLING:
        raise LiveRunNotAuthorized(
            "a live run draws at the authorized sampling configuration exactly; "
            "the caps or temperatures this run carries are not the ones the "
            "manifest binds"
        )
    if invocation.model != AUTHORIZED_MODEL:
        raise LiveRunNotAuthorized(
            f"the live invocation names model {invocation.model!r}, not the "
            f"authorized {AUTHORIZED_MODEL!r}"
        )
    manifest = (repo_root / EXECUTION_MANIFEST_PATH).resolve()
    if invocation.manifest_path.resolve() != manifest:
        raise LiveRunNotAuthorized(
            f"the live invocation names {invocation.manifest_path}, not the "
            f"committed execution manifest {manifest}"
        )
    if not manifest.is_file():
        raise LiveRunNotAuthorized(f"execution manifest is missing: {manifest}")
    committed = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if invocation.manifest_sha256 != committed:
        raise LiveRunNotAuthorized(
            "the live invocation's manifest digest is not the committed "
            f"manifest's: invocation {invocation.manifest_sha256}, file "
            f"{committed}"
        )


def assert_client_matches_provider(*, provider: str, client: object | None) -> None:
    """Refuse a run whose CLIENT is not what its provider label says it is.

    The rest of the gate reads the ``provider`` string a caller passed. That
    string is a label, and a label is not a client: ``provider="fake"`` with a
    metered client handed in reaches the metered provider with every refusal in
    this module satisfied, and ``provider="featherless"`` with an offline client
    writes a report labelled live that no model authored. Both are refused here,
    on the object's real type:

    * the fake path accepts only a :class:`~llm.fake_provider.FakeProvider` — or
      ``None``, which is :func:`run_instrument`'s own
      :class:`DryRunProvider` fallback, itself one;
    * the live path accepts neither a ``FakeProvider`` nor ``None``, because the
      fallback IS a ``FakeProvider``.

    This is a type check, not a name check: subclassing ``FakeProvider`` keeps a
    client offline, and calling a class ``FeatherlessClient`` does not make it
    one.
    """

    is_fake = client is None or isinstance(client, FakeProvider)
    if provider == "fake" and not is_fake:
        raise LiveRunNotAuthorized(
            "a run labelled 'fake' was handed a "
            f"{type(client).__name__}, which is not the offline fake provider; "
            "the label authorizes nothing and this client would reach whatever "
            "it wraps"
        )
    if provider != "fake" and is_fake:
        raise LiveRunNotAuthorized(
            f"a run labelled {provider!r} was handed "
            f"{'no client' if client is None else type(client).__name__}, which "
            "is the offline fake provider; a live-labelled report must be the "
            "authorized provider's own output, not a fixture's"
        )


def assert_ready_for_a_live_run(
    *,
    provider: str,
    invocation: LiveRunInvocation,
    units: int | None = None,
    limits: RunLimits = AUTHORIZED_LIMITS,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
    repo_root: Path = _REPO_ROOT,
) -> FrozenSet:
    """Everything that must hold BEFORE a live client exists, in order.

    The authorization gate first, then the frozen held-out set, and only then may
    a caller build a client — which is why this returns the verified
    :class:`FrozenSet` and :func:`build_authorized_client` takes one. A client is
    a credential and a connection; a run that must stop should stop before one is
    made, and a moved held-out set is exactly such a stop.

    ``FrozenSet`` and :func:`verify_frozen_set` are defined further down this
    module; the annotations are lazy (``from __future__ import annotations``) and
    the call happens at run time, so the ordering of the definitions is a reading
    convenience rather than a constraint.
    """

    assert_live_run_is_authorized(
        provider=provider,
        invocation=invocation,
        limits=limits,
        sampling=sampling,
        units=units,
        repo_root=repo_root,
    )
    return verify_frozen_set(repo_root)


def authorized_client_environment(env: Mapping[str, str]) -> dict[str, str]:
    """The environment the live client is built from: pinned, not inherited.

    :func:`llm.provider.build_default_client` selects BOTH the provider and the
    model from the environment, so calling it bare would let the ambient shell
    decide what an invocation labelled ``featherless`` actually reaches — a fake
    provider recorded as a live run, or a metered provider this manifest does
    not authorize and whose cost statement explicitly excludes it. Everything
    the factory reads is therefore written here from the authorized constants,
    and exactly one value crosses over from the ambient environment: the API
    key, which is a credential rather than a choice.
    """

    from llm.provider import (
        ENV_FEATHERLESS_API_KEY,
        ENV_MEETING_MODEL,
        ENV_PROVIDER,
        ENV_TRIGGER_MODEL,
    )

    api_key = env.get(ENV_FEATHERLESS_API_KEY, "").strip()
    if not api_key:
        raise LiveRunNotAuthorized(
            f"{ENV_FEATHERLESS_API_KEY} is not set; the authorized provider "
            f"{AUTHORIZED_PROVIDER!r} cannot be reached and no other provider "
            "may stand in for it"
        )
    return {
        ENV_PROVIDER: AUTHORIZED_PROVIDER,
        ENV_MEETING_MODEL: AUTHORIZED_MODEL,
        ENV_TRIGGER_MODEL: AUTHORIZED_MODEL,
        ENV_FEATHERLESS_API_KEY: api_key,
    }


def build_authorized_client(
    frozen: FrozenSet, env: Mapping[str, str] | None = None
) -> LLMClient:
    """Construct the ONE client a live run may use, from the pinned environment.

    ``env`` defaults to the process environment, from which
    :func:`authorized_client_environment` keeps only the credential.

    ``frozen`` is evidence rather than an input: it is unused below, and it is
    required so that no client can be constructed before the held-out set has
    been verified. The only producer of a :class:`FrozenSet` is
    :func:`verify_frozen_set`, so "the frozen set is checked before a provider
    exists" is a property of this signature instead of an ordering a later edit
    to :func:`main` could quietly reverse.
    """

    del frozen  # see the docstring: proof of ordering, not an input

    from llm.provider import build_default_client

    ambient = dict(os.environ) if env is None else dict(env)
    return build_default_client(env=authorized_client_environment(ambient))


# ---------------------------------------------------------------------------
# The client wrapper: per-call caps, prompt capture, model-work clock
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CapturedCall:
    """One provider call as the instrument saw it: never written to a report.

    ``prompt`` is the listener-visible input the supported grader reads. It stays
    in memory for the duration of a unit and is summarised into counts; the
    report carries no prompt text, because a prompt renders the prefix.
    """

    agent_id: str | None
    prompt: str
    max_tokens: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str
    seconds: float


@dataclass(frozen=True)
class ArmUsage:
    """One arm's spend, kept separate so the arms' asymmetry stays visible."""

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    model_work_seconds: float = 0.0

    def plus(self, calls: Sequence[CapturedCall]) -> ArmUsage:
        return ArmUsage(
            calls=self.calls + len(calls),
            input_tokens=self.input_tokens + sum(c.input_tokens for c in calls),
            output_tokens=self.output_tokens + sum(c.output_tokens for c in calls),
            cost_usd=self.cost_usd + sum(c.cost_usd for c in calls),
            model_work_seconds=self.model_work_seconds + sum(c.seconds for c in calls),
        )


class _ModelWorkClock:
    """The summed provider-call wall, against the authorized work window.

    Separate from :class:`~orchestrator.run_limits.RunDeadline`, which measures
    ELAPSED time: the authorization allows 4 h of model work inside a 6 h
    elapsed window, which is two limits and therefore two clocks.

    The window bounds each call IN FLIGHT as well as the total after it. A clock
    charged only on return can be overrun by one whole call, and one whole call
    on the authorized provider is not small: ``llm/featherless_client.py`` retries
    a send six times at a 600 s timeout with exponential backoff, so a single
    ``complete`` can stay in flight for the better part of an hour. Charging on
    return alone would let a run at 3 h 59 m of model work spend a fifth hour
    against an authorization of four, with only the separate 6 h elapsed clock
    behind it. :meth:`remaining` is what
    :meth:`_InstrumentClient.complete` bounds each await by.
    """

    def __init__(self, *, max_seconds: float) -> None:
        if max_seconds <= 0:
            raise ValueError("the model-work window must be positive")
        self._max_seconds = max_seconds
        self._seconds = 0.0

    @property
    def seconds(self) -> float:
        return self._seconds

    def remaining(self) -> float:
        """Work seconds left in the window; never negative."""

        return max(0.0, self._max_seconds - self._seconds)

    def charge(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError(f"a call cannot take {seconds} seconds")
        self._seconds += seconds
        if self._seconds > self._max_seconds:
            raise RunDeadlineExceeded(
                f"model-work window exhausted: {self._seconds:.1f}s of "
                f"{self._max_seconds:.1f}s"
            )

    def charge_aborted(self, seconds: float) -> RunDeadlineExceeded:
        """Charge an attempt the window cut off, and RETURN the stop to raise.

        Returned rather than raised so the caller can chain the underlying
        timeout onto it. The attempt bought no response, but its provider wall
        elapsed, so the clock carries it: the partial accounting a stop reports
        would otherwise understate the very limit that fired.
        """

        self._seconds += max(seconds, 0.0)
        return RunDeadlineExceeded(
            f"model-work window exhausted mid-call: {self._seconds:.1f}s of "
            f"{self._max_seconds:.1f}s, the attempt in flight was cut off"
        )


#: The ``model`` a :class:`CapturedCall` carries for an attempt the model-work
#: window cut off in flight. No response came back, so no served model is known;
#: the marker keeps the aborted attempt distinguishable in the partial
#: accounting from a response that actually arrived.
ABORTED_ATTEMPT_MODEL: Final[str] = "aborted-in-flight"


def _preflight_rates(inner: LLMClient) -> tuple[float, float] | None:
    """The USD pre-flight rates :class:`_InstrumentClient` should expose, if any.

    ``None`` means "expose none", which leaves ``BudgetedLLMClient`` free to
    apply its own frontier-calibrated defaults exactly as it would to the
    unwrapped client (``llm/budgeted_client.py:115-129``). A client that states
    its own rates has them passed through unchanged; a
    :class:`~llm.fake_provider.FakeProvider` states none but bills nothing, and
    zero is the honest rate for a client whose ``cost_usd`` is 0.0 by
    construction — the same statement the free providers make about themselves.
    """

    input_rate = getattr(inner, "preflight_cost_per_input_token_usd", None)
    output_rate = getattr(inner, "preflight_cost_per_output_token_usd", None)
    if isinstance(input_rate, float) and isinstance(output_rate, float):
        return (input_rate, output_rate)
    if isinstance(inner, FakeProvider):
        return (0.0, 0.0)
    return None


class _InstrumentClient:
    """Wrap the provider to enforce the per-call caps and capture the prompts.

    Five jobs, none of which the budget layer does:

    1. refuse a ``max_tokens`` that is not one of the two shipped caps, so
       "the shipped defaults unchanged" is checked rather than asserted;
    2. treat a response that reached its cap as a STOP — a truncation is a cap
       artifact, and the authorization says a truncation in either arm is a
       stop, not a datum;
    3. refuse a response from a model other than ``expected_model`` on the call
       that returns it, so a hosted endpoint serving a different checkpoint
       stops the run instead of being noticed in the report afterwards;
    4. bound each provider await by the model-work window's remaining seconds,
       so the authorized window stops the run DURING the call that exhausts it
       rather than one whole call later;
    5. hold the prompts the supported grader reads, in memory, for one unit.

    Every stop above records the call FIRST. The response came back, so the
    tokens were spent whether or not they are usable, and the partial accounting
    the stop rule promises has to carry them. The same rule reaches a call that
    never returned a usable response at all: an attempt the provider billed and
    then refused on its own schema validation is captured with the spend its
    parse-failure metadata carries, because the meeting layer fail-softs past it
    and no ``llm_calls`` row will ever hold it. Jobs 2 and 3 reach that attempt
    too, off the parse-failure metadata's own ``output_tokens`` and ``model``
    (:meth:`_unusable_response`): the completion the provider billed for is the
    thing they judge, and whether its body then parsed is not what makes a
    truncation or a foreign checkpoint a stop.

    Not a subclass of anything in ``experiments/``: the committed MECHANICS_ONLY
    harnesses keep their own refusal, and this wrapper composes an arbitrary
    :class:`~llm.client.LLMClient` instead.
    """

    def __init__(
        self,
        inner: LLMClient,
        *,
        work_clock: _ModelWorkClock,
        turn_max_tokens: int = AUTHORIZED_TURN_MAX_TOKENS,
        vote_max_tokens: int = AUTHORIZED_VOTE_MAX_TOKENS,
        expected_model: str | None = None,
    ) -> None:
        self._inner = inner
        self._work_clock = work_clock
        self._allowed_max_tokens = frozenset({turn_max_tokens, vote_max_tokens})
        self._ceiling = max(turn_max_tokens, vote_max_tokens)
        # ``None`` on the dry run, where the served model is the fixture's own
        # marker; the authorized model id on a live run, where the served model
        # is a thing the manifest binds.
        self._expected_model = expected_model
        self._calls: list[CapturedCall] = []
        # The USD pre-flight rates are the WRAPPED client's, never this
        # wrapper's own. ``BudgetedLLMClient`` reads them off whatever it is
        # handed (``llm/budgeted_client.py:115-129``), so hardcoding zero here
        # would disable the USD dimension for every client this wrapper ever
        # composed — including a metered one, whose $0.00 cap would then stop
        # nothing. On the authorized provider the pass-through IS zero
        # (``llm/featherless_client.py:244-245``), which is what the
        # authorization card's cost statement says: the token budget and the
        # wall deadline are the only limits that can stop this run.
        rates = _preflight_rates(inner)
        if rates is not None:
            self.preflight_cost_per_input_token_usd = rates[0]
            self.preflight_cost_per_output_token_usd = rates[1]

    @property
    def calls(self) -> tuple[CapturedCall, ...]:
        return tuple(self._calls)

    def prompts_for(self, agent_id: str) -> tuple[str, ...]:
        return tuple(call.prompt for call in self._calls if call.agent_id == agent_id)

    def take(self) -> tuple[CapturedCall, ...]:
        """Return this unit's calls and clear them for the next unit."""

        calls = tuple(self._calls)
        self._calls.clear()
        return calls

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if max_tokens > self._ceiling:
            raise PerCallCapExceeded(
                f"a call asked for {max_tokens} output tokens; the authorized "
                f"per-call ceiling is {self._ceiling}"
            )
        if max_tokens not in self._allowed_max_tokens:
            raise PerCallCapExceeded(
                f"a call asked for {max_tokens} output tokens; the authorized "
                f"caps are the shipped {sorted(self._allowed_max_tokens)} and "
                "this run may not move them"
            )
        started = time.monotonic()
        # The await is bounded by what is LEFT of the model-work window, the
        # way orchestrator.run_limits.RunDeadline.run bounds meeting work by
        # what is left of the elapsed one. Without it the window is checked only
        # once a call returns, so a run near its limit can spend one further
        # whole call — up to the provider client's own retry-and-timeout budget
        # — beyond an authorized ceiling. ``timeout.expired()`` separates OUR
        # stop from a timeout the inner client raised itself, which stays a
        # provider failure and is not re-labelled as a limit.
        window = asyncio.timeout(self._work_clock.remaining())
        try:
            async with window:
                response = await self._inner.complete(
                    prompt=prompt,
                    schema=schema,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    call_kind=call_kind,
                    model=model,
                    agent_id=agent_id,
                )
        except TimeoutError as exc:
            if not window.expired():
                raise
            aborted = time.monotonic() - started
            # Recorded like every other stop in this client: the attempt bought
            # no response, but it held the provider for ``aborted`` seconds and
            # may have been billed for tokens this side cannot see, so it enters
            # the partial accounting as a call with unknown (zero) usage rather
            # than vanishing.
            self._calls.append(
                CapturedCall(
                    agent_id=agent_id,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    model=ABORTED_ATTEMPT_MODEL,
                    seconds=aborted,
                )
            )
            raise self._work_clock.charge_aborted(aborted) from exc
        except BaseException as exc:
            # A call the provider BILLED and then refused. A real provider
            # validates the completion itself and raises before anything
            # downstream can log it, so this attempt reaches no ``llm_calls``
            # row and would otherwise be missing from the partial accounting a
            # stop reports — the same understatement the truncation stop used to
            # make, and the gap the run of 2026-09-10 stopped on. The
            # parse-failure metadata riding the exception carries the real spend
            # (``llm.provider.extract_parse_failure``); an exception without it
            # bought nothing and is re-raised untouched.
            failure = extract_parse_failure(exc)
            if failure is None:
                raise
            burned = time.monotonic() - started
            self._calls.append(
                CapturedCall(
                    agent_id=agent_id,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    input_tokens=failure.input_tokens,
                    output_tokens=failure.output_tokens,
                    cost_usd=failure.cost_usd,
                    model=failure.model,
                    seconds=burned,
                )
            )
            # Charged like a call that returned: the provider held the wall for
            # it either way, so the work clock and the per-arm
            # ``model_work_seconds`` keep describing the same seconds.
            self._work_clock.charge(burned)
            # The identity and truncation stops read the SAME two facts off the
            # parse-failure metadata that they read off a response, because both
            # describe the completion the provider produced and billed for.
            # Skipping them here would make a refused payload the one way past
            # them: a body truncated at the output cap is exactly the body that
            # then fails schema validation, and an endpoint serving a different
            # checkpoint would be recorded and reported rather than stopping the
            # run. Raising here also replaces the ``ValidationError`` the meeting
            # layer fail-softs with a stop it does not, which is the point — the
            # call is already in this client's ledger, so the partial accounting
            # a stop reports carries its spend even though the budget layer's own
            # charge (keyed on the parse-failure metadata) no longer fires.
            stop = self._unusable_response(
                model=failure.model,
                output_tokens=failure.output_tokens,
                max_tokens=max_tokens,
            )
            if stop is not None:
                raise stop from exc
            raise
        seconds = time.monotonic() - started
        # Recorded before either of the stops below, because the response
        # exists: its tokens were spent and its provider time elapsed, and a
        # stop that dropped them would understate its own partial accounting.
        self._calls.append(
            CapturedCall(
                agent_id=agent_id,
                prompt=prompt,
                max_tokens=max_tokens,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cost_usd=response.cost_usd,
                model=response.model,
                seconds=seconds,
            )
        )
        self._work_clock.charge(seconds)
        stop = self._unusable_response(
            model=response.model,
            output_tokens=response.usage.output_tokens,
            max_tokens=max_tokens,
        )
        if stop is not None:
            raise stop
        return response

    def _unusable_response(
        self, *, model: str, output_tokens: int, max_tokens: int
    ) -> InstrumentError | None:
        """The stop a completed call earns, or ``None`` if it earns none.

        Returned rather than raised so the two callers can chain it: a call the
        provider refused on its own schema validation raises this ``from`` the
        provider's exception, and a call that returned raises it bare. One
        function so the two paths cannot enforce different lists — the run of
        2026-09-10's lesson was a check that reached one surface and not the
        other.
        """

        if self._expected_model is not None and model != self._expected_model:
            return ProviderIdentityMismatch(
                f"a response came back from model {model!r}; this run "
                f"is authorized for {self._expected_model!r} only"
            )
        if output_tokens >= max_tokens:
            return PerCallCapExceeded(
                f"a response reached its {max_tokens}-token output cap "
                f"({output_tokens} tokens); a truncation is a "
                "stop, not a datum"
            )
        return None


# ---------------------------------------------------------------------------
# The dry-run provider: mechanics only, never model judgment
# ---------------------------------------------------------------------------

# The two arms render the same facts in two different prompt families, so every
# pattern here matches both. A turn id is ``{meeting_id}:turn-{index}``; the
# closing bracket is what separates it from the accounts family's derived
# ``[turn:<turn id>:claim:0]`` handles, which are not turn ids and are not
# citable in ``primary_reason_id``.
_TRANSCRIPT_TURN_ID: Final[re.Pattern[str]] = re.compile(r"\[([\w.:-]+:turn-\d+)\]")
#: The reference family's candidate block.
_VALID_TARGETS_BLOCK: Final[re.Pattern[str]] = re.compile(
    r"## Valid ejection targets\n([^\n]+)"
)
#: The accounts family's candidate line.
_LIVING_CANDIDATES: Final[re.Pattern[str]] = re.compile(r"Living candidates: ([^\n.]+)")
_LIVING_LINE: Final[re.Pattern[str]] = re.compile(
    r"(?:Living players you may accuse|Other living players): ([^\n.]+)"
)
_BACKTICKED_ID: Final[re.Pattern[str]] = re.compile(r"`(p-\d+)`")
_BARE_ID: Final[re.Pattern[str]] = re.compile(r"\bp-\d+\b")

DRY_RUN_MODEL: Final[str] = "dry-run-mechanics"

DRY_RUN_CAVEAT: Final[str] = (
    "A green dry run says nothing about model judgment. This provider reads the "
    "prompt for a valid target and a real turn id and returns them; it "
    "establishes that the pipeline carries a non-SKIP decision through to a "
    "graded outcome, not that any model would produce one."
)


class DryRunProvider(FakeProvider):
    """A deterministic $0 provider that carries a decision through the pipeline.

    Reads ONLY the prompt it is handed — the same bytes a model gets — and
    returns the first valid ejection target citing the last transcript turn.
    It has no access to roles, to the prefix, or to any grader.

    It exists because the bare :class:`~llm.fake_provider.FakeProvider` builds a
    minimal schema instance whose ``target`` is not a living player, so every
    ballot is struck to SKIP by the invalid-target guard and the pipeline is
    never exercised past the tally.
    """

    def __init__(self) -> None:
        self.preflight_cost_per_input_token_usd = 0.0
        self.preflight_cost_per_output_token_usd = 0.0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        payload: BaseModel
        if schema is MeetingTurn:
            payload = self._turn(prompt=prompt, agent_id=agent_id)
        elif schema is ModelAuthoredVoteBallot:
            payload = self._ballot(prompt=prompt, agent_id=agent_id)
        else:
            return await super().complete(
                prompt=prompt,
                schema=schema,
                max_tokens=max_tokens,
                temperature=temperature,
                call_kind=call_kind,
                model=model,
                agent_id=agent_id,
            )
        text = payload.model_dump_json()
        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=max(1, len(prompt) // 4),
                output_tokens=max(1, len(text) // 4),
            ),
            cost_usd=0.0,
            model=DRY_RUN_MODEL,
        )

    def _turn(self, *, prompt: str, agent_id: str | None) -> MeetingTurn:
        speaker = agent_id if agent_id is not None else "p-1"
        accused = self._first_other_living(prompt, speaker=speaker)
        claims: list[dict[str, object]] = []
        if accused is not None:
            claims.append(
                {
                    "type": "accusation",
                    "against": accused,
                    "confidence": 0.6,
                    "reason": "mechanics check; this names no evidence",
                }
            )
        return MeetingTurn.model_validate(
            {
                "turn_id": "dry-run",
                "turn_index": 0,
                "speaker": speaker,
                "turn_kind": "opening",
                "reply_to": None,
                "observations": [],
                "claims": claims,
                "free_text": (
                    "This is a mechanics check, not a judgment about anyone."
                ),
            }
        )

    def _ballot(self, *, prompt: str, agent_id: str | None) -> ModelAuthoredVoteBallot:
        voter = agent_id if agent_id is not None else "p-1"
        target = self._first_valid_target(prompt, voter=voter)
        turn_ids = list(dict.fromkeys(_TRANSCRIPT_TURN_ID.findall(prompt)))
        cited = turn_ids[-1] if turn_ids else None
        if target is None or cited is None:
            return ModelAuthoredVoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.5,
                primary_reason_id=None,
                primary_reason_observation_id=None,
                considered_alternatives=(),
                rationale_text="Nothing in this prompt to cite; abstaining.",
            )
        return ModelAuthoredVoteBallot(
            voter=voter,
            target=target,
            confidence=0.7,
            primary_reason_id=cited,
            primary_reason_observation_id=None,
            considered_alternatives=(),
            rationale_text="Mechanics check: the first valid target, cited.",
        )

    @staticmethod
    def _first_valid_target(prompt: str, *, voter: str) -> str | None:
        block = _VALID_TARGETS_BLOCK.search(prompt)
        if block is not None:
            for candidate in _BACKTICKED_ID.findall(block.group(1)):
                if candidate != voter:
                    return str(candidate)
            return None
        line = _LIVING_CANDIDATES.search(prompt)
        if line is None:
            return None
        for candidate in _BARE_ID.findall(line.group(1)):
            if candidate != voter:
                return str(candidate)
        return None

    @staticmethod
    def _first_other_living(prompt: str, *, speaker: str) -> str | None:
        match = _LIVING_LINE.search(prompt)
        if match is None:
            return None
        for candidate in _BARE_ID.findall(match.group(1)):
            if candidate != speaker:
                return str(candidate)
        return None


# ---------------------------------------------------------------------------
# The frozen held-out set
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FrozenSet:
    """The regenerated set, verified against the committed freeze manifest.

    Holds the prefixes because the run needs them; holds no rendered text and is
    never serialized. :func:`assert_report_holds_no_prefix_bytes` is the guard
    on the other side.
    """

    generated: GeneratedSet
    manifest_sha256: str
    accepted_seeds: tuple[int, ...]
    skipped_seeds: tuple[int, ...]

    @property
    def prefixes(self) -> tuple[HeldOutPrefix, ...]:
        return self.generated.prefixes


def _as_int(raw: Mapping[str, object], key: str) -> int:
    """One manifest field as an ``int``, or a stop naming the field."""

    value = raw.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise FrozenSetMismatch(
            f"the frozen manifest's {key!r} is {value!r}, not a whole number"
        )
    return value


def _as_str(raw: Mapping[str, object], key: str) -> str:
    """One manifest field as a ``str``, or a stop naming the field."""

    value = raw.get(key)
    if not isinstance(value, str):
        raise FrozenSetMismatch(
            f"the frozen manifest's {key!r} is {value!r}, not a string"
        )
    return value


def _manifest_rows(
    manifest: Mapping[str, object], key: str
) -> list[Mapping[str, object]]:
    """One of the freeze manifest's row blocks, or a stop naming what is missing.

    A manifest with no ``accepted`` or no ``skipped`` block used to reach a bare
    ``KeyError`` here — an unnamed crash where the stop rule promises a refusal
    that says what differed. AGENTS.md: invalid input raises explicitly.
    """

    rows = manifest.get(key)
    if not isinstance(rows, list) or not all(isinstance(row, Mapping) for row in rows):
        raise FrozenSetMismatch(
            f"the frozen manifest carries no {key!r} block of rows (found "
            f"{type(rows).__name__}); it does not describe a frozen set and this "
            "run may not proceed on it"
        )
    return [row for row in rows if isinstance(row, Mapping)]


def _parsed_band(raw: object) -> SeedBand:
    """The manifest's band as a :class:`SeedBand`, or a stop.

    The manifest's band block carries a ``draw_order`` the model does not model,
    so the three band fields are lifted by name rather than splatted; a band that
    is not drawn ascending is a different draw and is refused here rather than
    silently accepted by dropping the key.
    """

    if not isinstance(raw, Mapping):
        raise FrozenSetMismatch(f"the frozen set's band is {raw!r}, not a block")
    if raw.get("draw_order") != "ascending":
        raise FrozenSetMismatch(
            f"the frozen set was drawn {raw.get('draw_order')!r}; the generator "
            "draws ascending and a different order is a different set"
        )
    return SeedBand(
        first_seed=_as_int(raw, "first_seed"),
        last_seed=_as_int(raw, "last_seed"),
        size=_as_int(raw, "size"),
    )


def _parsed_roster(raw: Mapping[str, object]) -> PrefixRoster:
    """The manifest's roster as a :class:`PrefixRoster`, or a stop."""

    return PrefixRoster(
        num_players=_as_int(raw, "num_players"),
        num_impostors=_as_int(raw, "num_impostors"),
        tasks_per_crewmate=_as_int(raw, "tasks_per_crewmate"),
    )


def verify_frozen_set(repo_root: Path = _REPO_ROOT) -> FrozenSet:
    """Regenerate the held-out set and refuse to proceed on any difference.

    Runs BEFORE any arm and before any provider exists. What it compares:
    the band, the roster, the tick budget, the observation clock, every accepted
    seed and digest in order, and the skip list with its reason codes. The
    first three are compared against the generator's own frozen values and the
    parsed band and roster are then what :func:`generate` is called with, so the
    set that is regenerated is the one this manifest describes rather than one
    the manifest merely sits beside. A mismatch names seeds and digests only —
    both are already published in the committed manifest — and never a step.

    Not compared here: ``source_sha256``. That is the freeze's own restamp
    record, and ``tests/experiments/test_held_out_prefixes.py::
    test_the_committed_manifest_regenerates_from_its_own_band`` is what holds
    it; duplicating the check here would make an un-restamped source edit stop
    the run for a reason the freeze test states better.
    """

    manifest_file = repo_root / MANIFEST_PATH
    if not manifest_file.is_file():
        raise FrozenSetMismatch(f"the freeze manifest is missing: {MANIFEST_PATH}")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise FrozenSetMismatch(f"{MANIFEST_PATH} does not hold a JSON object")
    if manifest.get("status") != "held_out":
        raise FrozenSetMismatch(
            f"the frozen set is marked {manifest.get('status')!r}, not "
            "'held_out'; a set converted to development data is not a held-out "
            "input and this run may not use it"
        )
    if manifest.get("temporal_observation_version") != TEMPORAL_OBSERVATION_VERSION:
        raise FrozenSetMismatch(
            "the frozen set was screened under observation clock "
            f"{manifest.get('temporal_observation_version')!r}, but both arms "
            f"run clock {TEMPORAL_OBSERVATION_VERSION}"
        )
    roster = manifest.get("roster")
    if not isinstance(roster, dict) or (
        roster.get("num_players"),
        roster.get("num_impostors"),
    ) != (AUTHORIZED_ROSTER_PLAYERS, AUTHORIZED_ROSTER_IMPOSTORS):
        raise FrozenSetMismatch(
            f"the frozen set's roster is {roster!r}; the authorized token "
            f"budget is sized on {AUTHORIZED_ROSTER_PLAYERS}p"
            f"{AUTHORIZED_ROSTER_IMPOSTORS}i and a change of roster "
            "invalidates it"
        )
    # The band, the tick budget and the rest of the roster are compared too, and
    # the parsed band and roster are what generate() is then driven with. Read
    # but unchecked, they would let the manifest DESCRIBE a draw that is not the
    # one the run regenerates — a different band, a different tick budget or a
    # different task count — while every digest still matched, because the
    # digests would have come from the module defaults either way.
    band = _parsed_band(manifest.get("band"))
    if band != PREREGISTERED_BAND:
        raise FrozenSetMismatch(
            f"the frozen set names band {band.first_seed}-{band.last_seed} "
            f"size {band.size}; the preregistered band is "
            f"{PREREGISTERED_BAND.first_seed}-{PREREGISTERED_BAND.last_seed} "
            f"size {PREREGISTERED_BAND.size}"
        )
    parsed_roster = _parsed_roster(roster)
    if parsed_roster != FROZEN_PREFIX_ROSTER:
        raise FrozenSetMismatch(
            f"the frozen set's roster is {parsed_roster!r}; the generator draws "
            f"{FROZEN_PREFIX_ROSTER!r} and a change of roster invalidates the "
            "screening"
        )
    if manifest.get("max_ticks") != MAX_TICKS:
        raise FrozenSetMismatch(
            f"the frozen set names a {manifest.get('max_ticks')!r}-tick budget; "
            f"the generator builds every prefix inside {MAX_TICKS}"
        )

    generated = generate(band=band, roster=parsed_roster)
    expected_accepted = [
        (_as_int(row, "seed"), _as_str(row, "sha256"))
        for row in _manifest_rows(manifest, "accepted")
    ]
    actual_accepted = [
        (prefix.seed, digest)
        for prefix, digest in zip(generated.prefixes, generated.digests)
    ]
    if actual_accepted != expected_accepted:
        raise FrozenSetMismatch(
            _first_difference(
                "accepted prefixes",
                expected=[f"{seed}:{digest}" for seed, digest in expected_accepted],
                actual=[f"{seed}:{digest}" for seed, digest in actual_accepted],
            )
        )
    expected_skipped = [
        (_as_int(row, "seed"), _as_str(row, "reason"))
        for row in _manifest_rows(manifest, "skipped")
    ]
    actual_skipped = [(skip.seed, skip.reason) for skip in generated.skipped]
    if actual_skipped != expected_skipped:
        raise FrozenSetMismatch(
            _first_difference(
                "skipped seeds",
                expected=[f"{seed}:{reason}" for seed, reason in expected_skipped],
                actual=[f"{seed}:{reason}" for seed, reason in actual_skipped],
            )
        )
    for prefix in generated.prefixes:
        assert_no_legacy_body_handles([canonical_prefix_json(prefix)])
        if prefix_sha256(prefix) != dict(expected_accepted)[prefix.seed]:
            raise FrozenSetMismatch(f"seed {prefix.seed} re-hashes differently")
    return FrozenSet(
        generated=generated,
        manifest_sha256=hashlib.sha256(manifest_file.read_bytes()).hexdigest(),
        accepted_seeds=tuple(seed for seed, _ in expected_accepted),
        skipped_seeds=tuple(seed for seed, _ in expected_skipped),
    )


def _first_difference(
    what: str, *, expected: Sequence[str], actual: Sequence[str]
) -> str:
    """Name the first row that differs, by seed and digest, and nothing else."""

    if len(expected) != len(actual):
        return (
            f"the regenerated {what} has {len(actual)} rows, the frozen manifest "
            f"has {len(expected)}; this is a stop"
        )
    for index, (want, got) in enumerate(zip(expected, actual)):
        if want != got:
            return (
                f"the regenerated {what} differ at row {index}: frozen {want}, "
                f"regenerated {got}; this is a stop"
            )
    return f"the regenerated {what} differ"


# ---------------------------------------------------------------------------
# Running one unit
# ---------------------------------------------------------------------------


class _ScriptedPrefixAgent(TacticalAgent):
    """A public :class:`TacticalAgent` driving one frozen prefix's schedule.

    :func:`orchestrator.game.build_default_agent_factory` cannot run a scripted
    prefix — its agents choose their own actions, and its
    :class:`~agents.memory.store.AgentMemory` carries none of the arm's channel
    versions — so the instrument builds the same public ``TacticalAgent`` with
    the same public policies and hands it the prefix and the arm's memory. The
    decide path mirrors the filter's: ingest the real typed packet, then return
    the predetermined legal action or an explicit wait.
    """

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        role: Role,
        prefix: HeldOutPrefix,
        memory: AgentMemory,
    ) -> None:
        policy = (
            ImpostorPolicy(agent_id=agent_id)
            if role == "IMPOSTOR"
            else CrewmatePolicy(agent_id=agent_id)
        )
        super().__init__(agent_id=agent_id, policy=policy, role=role, memory=memory)
        self._scripted = {
            step.tick: step.action
            for step in prefix.steps
            if step.action.actor == agent_id
        }

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        del public_map
        ingest_packet(
            packet=packet, memory=self.memory.episodic, beliefs=self.memory.beliefs
        )
        scripted = self._scripted.get(packet.tick)
        if scripted is None:
            return WaitIntent(type="wait", actor=self.agent_id)
        return scripted


# ---------------------------------------------------------------------------
# Meeting-internal defaults: counted, never dropped
# ---------------------------------------------------------------------------

#: The error type ``orchestrator/game.py`` stamps on every fired meeting default.
_DEFAULT_MARKER_ERROR_TYPE: Final[str] = "deadline_default"
#: The two message shapes ``orchestrator.game._deadline_default_message`` writes.
#: Parsed rather than trusted: an unrecognised message means the producer's
#: wording moved and this classification is no longer evidence of anything, so
#: :func:`count_defaulted_attempts` stops the run instead of miscounting.
_DEFAULTED_VOTE_MESSAGE: Final[re.Pattern[str]] = re.compile(
    r"^vote defaulted \((deadline|validation)\); "
)
_DEFAULTED_TURN_MESSAGE: Final[re.Pattern[str]] = re.compile(
    r"^\w+ turn(?: \(turn \d+\))? defaulted \((deadline|validation)\); "
)
#: The typed note the manager puts on a Task 10.6 validation-DEGRADE: an opening
#: rebuilt as unsure from the model's last parsed-but-position-less attempt. The
#: replay carries no ``degraded`` field, so this annotation is the only recorded
#: seam between a degrade and a full placeholder default.
_DEGRADED_OPENING_ANNOTATION: Final[TurnAnnotationKind] = "opening_degraded_unsure"


@dataclass(frozen=True)
class DefaultedAttempts:
    """One unit's meeting-internal fail-soft substitutions, as counts.

    The meeting layer does not abort on a payload that fails schema validation:
    a turn becomes a placeholder (``meetings/manager.py::_default_turn``) and a
    ballot becomes a marked SKIP (``_vote_parse_default``, the runaway class
    accepted at about 1 in 50). Both are recorded as ``deadline_default``
    :class:`~orchestrator.replay.FailedCallReplayEntry` rows, and the
    preregistration requires missing attempts to REMAIN VISIBLE
    (``audits/deduction-candidate/preregistration.md:112``) and failed attempts
    to be retained (``:136``).

    Reading those rows is what makes that true of this instrument. Without it a
    defaulted ballot reaches the report as one more ``uncited`` or
    ``guard_rewritten`` verdict, indistinguishable from a voter who chose to
    abstain, and a defaulted TURN reaches it as nothing at all — a meeting in
    which no model-authored turn existed would score as a complete unit.

    Counts, not a stop: see :data:`STOP_RULE`. Fields are per unit and summed
    per arm onto :class:`ArmSummary`.
    """

    defaulted_turns: int = 0
    defaulted_votes: int = 0
    by_validation: int = 0
    by_deadline: int = 0
    degraded_openings: int = 0

    @property
    def total(self) -> int:
        return self.defaulted_turns + self.defaulted_votes

    def plus(self, other: DefaultedAttempts) -> DefaultedAttempts:
        return DefaultedAttempts(
            defaulted_turns=self.defaulted_turns + other.defaulted_turns,
            defaulted_votes=self.defaulted_votes + other.defaulted_votes,
            by_validation=self.by_validation + other.by_validation,
            by_deadline=self.by_deadline + other.by_deadline,
            degraded_openings=self.degraded_openings + other.degraded_openings,
        )


def count_defaulted_attempts(
    entries: Sequence[ReplayLogEntry], *, meeting: MeetingReplayEntry, seed: int
) -> DefaultedAttempts:
    """Count this unit's recorded meeting defaults, by phase and by trigger.

    ``seed`` names the unit in the stop message only; nothing about the prefix
    itself is read, and no message text reaches a report.
    """

    turns = 0
    votes = 0
    validation = 0
    deadline = 0
    for entry in entries:
        if not isinstance(entry, FailedCallReplayEntry):
            continue
        if entry.error_type != _DEFAULT_MARKER_ERROR_TYPE:
            continue
        vote = _DEFAULTED_VOTE_MESSAGE.match(entry.error_message)
        turn = _DEFAULTED_TURN_MESSAGE.match(entry.error_message)
        matched = vote or turn
        if matched is None:
            raise InstrumentError(
                f"seed {seed}: a recorded meeting default carries a message "
                "this instrument cannot classify by phase and trigger; the "
                "producer's wording moved and the defaulted-attempt counts "
                "would be wrong"
            )
        if vote is not None:
            votes += 1
        else:
            turns += 1
        if matched.group(1) == "validation":
            validation += 1
        else:
            deadline += 1
    return DefaultedAttempts(
        defaulted_turns=turns,
        defaulted_votes=votes,
        by_validation=validation,
        by_deadline=deadline,
        degraded_openings=sum(
            1
            for turn_record in meeting.transcript.turns
            if any(
                note.kind == _DEGRADED_OPENING_ANNOTATION
                for note in turn_record.annotations
            )
        ),
    )


@dataclass(frozen=True)
class UnitRecord:
    """One unit's raw capture, before any grading. Privileged and in-memory only.

    Holds the ground-truth roles and the live prompts, so it never leaves the
    process and is never serialized. :func:`grade_unit` is a pure function OVER
    this record; nothing in the run path reads a grade, which is what keeps
    judge information out of every listener and every tactic.
    """

    seed: int
    arm: ArmName
    meeting_id: str
    outcome: str
    ejected_player_id: PlayerId | None
    ballots: tuple[VoteBallot, ...]
    # The turns themselves, not their ids: the citation-relevance rule asks what
    # a cited turn SAYS and who spoke it, which an id cannot answer.
    turns: tuple[MeetingTurn, ...]
    roles: Mapping[PlayerId, Role]
    prompts_by_agent: Mapping[str, tuple[str, ...]]
    calls: tuple[CapturedCall, ...]
    game_outcome: str
    recorded_temporal_version: int | None
    recorded_experiment_config: RecordedExperimentConfig | None
    prompt_versions: Mapping[str, str]
    defaults: DefaultedAttempts


def run_unit(
    prefix: HeldOutPrefix,
    *,
    arm: InstrumentArm,
    client: _InstrumentClient,
    run_budget: GameBudget,
    deadline: RunDeadline,
    work_clock: _ModelWorkClock,
    output_dir: Path,
    provider: str = "fake",
    limits: RunLimits = AUTHORIZED_LIMITS,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
) -> UnitRecord:
    """Run one frozen prefix's meeting under one arm through the public API.

    The tick budget stops the game one tick after the report, so the unit is
    exactly "one frozen legal prefix followed by one fresh meeting" and nothing
    downstream of the decision is claimed (the preregistration's "Apply that
    meeting's outcome and stop").

    The sampling configuration is PASSED rather than inherited: the manifest
    binds the two temperatures and the two caps, so the meeting runs on a
    :class:`~meetings.manager.MeetingConfig` this module states.
    """

    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    config = arm.experiment_config
    unit_budget = GameBudget(
        max_cost_usd=limits.max_cost_usd,
        max_input_tokens=limits.unit_max_input_tokens,
        max_output_tokens=limits.unit_max_output_tokens,
        parent=run_budget,
    )
    runner = build_default_meeting_runner(
        llm_client=client,
        budget=unit_budget,
        config=sampling.meeting_config(),
        deadline=deadline,
        env=arm.environment(provider=provider),
        public_map=public_map,
    )
    agents: dict[PlayerId, _ScriptedPrefixAgent] = {}

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        agent = _ScriptedPrefixAgent(
            agent_id=agent_id,
            role=role,
            prefix=prefix,
            memory=AgentMemory(
                evidence_reasoning_version=config.evidence_reasoning_version,
                public_account_version=config.public_account_version,
                attributed_testimony_version=config.attributed_testimony_version,
                public_map=public_map,
            ),
        )
        agents[agent_id] = agent
        return agent

    replay_path = output_dir / f"{arm.name}-seed-{prefix.seed}.jsonl"
    result = HeadlessGame(
        seed=prefix.seed,
        num_players=prefix.roster.num_players,
        num_impostors=prefix.roster.num_impostors,
        tasks_per_crewmate=prefix.roster.tasks_per_crewmate,
        game_map=game_map,
        agent_factory=factory,
        replay_path=replay_path,
        # The observation audit re-states the prefix packet by packet and this
        # instrument reads none of it, so it goes to the null device rather than
        # into the results directory — a held-out input is not published by
        # accident (the precedent is experiments/tactical_gameplay.py).
        audit_log_path=Path(os.devnull),
        scheduler=TickScheduler(max_ticks=prefix.report_tick + 1),
        meeting_runner=runner,
        experiment_config=config,
        temporal_observation_version=arm.temporal_version,
        substrate_flags=runner.substrate_flags,
        deadline=deadline,
    ).run()

    entries = read_all_entries(replay_path)
    meetings = [entry for entry in entries if isinstance(entry, MeetingReplayEntry)]
    if len(meetings) != 1:
        raise InstrumentError(
            f"seed {prefix.seed} on arm {arm.name} resolved {len(meetings)} "
            "meetings; a controlled unit is exactly one"
        )
    meeting = meetings[0]
    if len(meeting.ballots) != AUTHORIZED_LIVING_VOTERS:
        raise InstrumentError(
            f"seed {prefix.seed} on arm {arm.name} resolved with "
            f"{len(meeting.ballots)} ballots; the authorized roster puts "
            f"{AUTHORIZED_LIVING_VOTERS} living voters at meeting open and the "
            "token budget is sized on that"
        )
    _assert_arm_provenance(entries, arm=arm, seed=prefix.seed)
    _reconcile_recorded_spend(
        meeting, entries=entries, budget=unit_budget, seed=prefix.seed, arm=arm
    )
    _assert_charged_spend_is_within_caps(
        unit_budget, level="per-unit", seed=prefix.seed, arm=arm
    )
    _assert_charged_spend_is_within_caps(
        run_budget, level="run", seed=prefix.seed, arm=arm
    )

    # Read, not drained. Every check below can stop the run, and a stop after
    # the buffer was emptied would hand the abort handler an empty client and
    # report a unit that spent nothing — the same understatement the truncation
    # stop used to make. The unit is drained only once it has been accepted.
    prompts: dict[str, list[str]] = {}
    for call in client.calls:
        if call.agent_id is not None:
            prompts.setdefault(call.agent_id, []).append(call.prompt)
    assert_no_legacy_body_handles([call.prompt for call in client.calls])
    _assert_live_prompts_were_recorded(meeting, calls=client.calls, seed=prefix.seed)
    calls = client.take()
    del work_clock  # charged inside the client; named here so the caller sees it

    return UnitRecord(
        seed=prefix.seed,
        arm=arm.name,
        meeting_id=meeting.meeting_id,
        outcome=meeting.outcome,
        ejected_player_id=meeting.ejected_player_id,
        ballots=meeting.ballots,
        turns=tuple(meeting.transcript.turns),
        roles=MappingProxyType(
            {pid: player.role for pid, player in result.final_state.players.items()}
        ),
        prompts_by_agent=MappingProxyType(
            {agent: tuple(texts) for agent, texts in prompts.items()}
        ),
        calls=calls,
        game_outcome=result.outcome,
        recorded_temporal_version=recorded_temporal_observation_version(entries),
        recorded_experiment_config=recorded_experiment_config(entries),
        prompt_versions=MappingProxyType(dict(meeting.prompt_versions)),
        defaults=count_defaulted_attempts(entries, meeting=meeting, seed=prefix.seed),
    )


def _assert_arm_provenance(
    entries: Sequence[ReplayLogEntry], *, arm: InstrumentArm, seed: int
) -> None:
    """Refuse a unit whose recorded identity is not the arm it claims to be.

    The recorded observation clock is what makes the two arms distinguishable at
    all — without it a v1 and a v2 recording carry byte-identical provenance —
    so a unit that does not carry its arm's clock and config is a provenance
    failure, which the preregistration's decision rules make a stop.
    """

    clock = recorded_temporal_observation_version(entries)
    if clock != arm.temporal_version:
        raise ProvenanceMismatch(
            f"seed {seed} on arm {arm.name} recorded observation clock "
            f"{clock!r}, not {arm.temporal_version}"
        )
    config = recorded_experiment_config(entries)
    if config != arm.experiment_config:
        raise ProvenanceMismatch(
            f"seed {seed} on arm {arm.name} recorded an experiment config that "
            "is not the arm's"
        )


def _charged_failed_attempts(
    entries: Sequence[ReplayLogEntry], *, meeting_id: str
) -> tuple[FailedCallReplayEntry, ...]:
    """This meeting's failed provider attempts that the provider still charged.

    A real provider validates the completion itself and raises BEFORE the
    recording client can log the call, so the tokens a schema-failed attempt
    burned never reach :attr:`MeetingReplayEntry.llm_calls` — while the budget
    layer charges them off the parse-failure metadata riding the exception
    (``llm/budgeted_client.py``, ``llm.provider.extract_parse_failure``). They
    reach the replay through the failed-call channel instead: from the
    recorder's identified ledger (``orchestrator/game.py::_record_captured_failures``)
    or, for a runner that supplies none, off the surfaced default's
    ``parse_failures`` (``_record_deadline_defaults``).

    Usage is the discriminator, and the producer is the one that set it. The two
    attempts whose spend is not the provider's to charge again are both written
    as ZERO-spend visibility markers: a deadline miss completed nothing, and a
    manager-side validation of a returned-but-invalid payload has its spend in
    ``llm_calls`` already (``meetings/manager.py:1712-1720`` states that
    property). Summing only the rows carrying usage therefore counts every
    charged call exactly once.
    """

    return tuple(
        entry
        for entry in entries
        if isinstance(entry, FailedCallReplayEntry)
        and entry.meeting_id == meeting_id
        and (
            entry.input_tokens != 0 or entry.output_tokens != 0 or entry.cost_usd != 0.0
        )
    )


@dataclass(frozen=True)
class _RecordedSpend:
    """One unit's recorded spend over every call the provider charged."""

    input_tokens: int
    output_tokens: int
    cost_usd: float
    resolved_calls: int
    charged_failures: int


def _recorded_spend(
    meeting: MeetingReplayEntry, entries: Sequence[ReplayLogEntry]
) -> _RecordedSpend:
    """Sum the meeting's resolved calls AND its charged failed attempts."""

    failed = _charged_failed_attempts(entries, meeting_id=meeting.meeting_id)
    return _RecordedSpend(
        input_tokens=(
            sum(call.input_tokens for call in meeting.llm_calls)
            + sum(entry.input_tokens for entry in failed)
        ),
        output_tokens=(
            sum(call.output_tokens for call in meeting.llm_calls)
            + sum(entry.output_tokens for entry in failed)
        ),
        cost_usd=(
            sum(call.cost_usd for call in meeting.llm_calls)
            + sum(entry.cost_usd for entry in failed)
        ),
        resolved_calls=len(meeting.llm_calls),
        charged_failures=len(failed),
    )


def _reconcile_recorded_spend(
    meeting: MeetingReplayEntry,
    *,
    entries: Sequence[ReplayLogEntry],
    budget: GameBudget,
    seed: int,
    arm: InstrumentArm,
) -> None:
    """Check that every call the budget charged is one the replay accounts for.

    The token budget is the limit; this is its accounting check. It reads the
    RECORDED spend — the meeting row's resolved calls plus the failed attempts
    the replay records with usage (:func:`_charged_failed_attempts`) — against
    the enforced budget snapshot, so a charged call that reached neither surface
    is caught on the unit that burned it rather than at the end of a run.

    Summing ``llm_calls`` alone did not do that, and the run of 2026-09-10 is
    the case: a payload the provider validated and refused burned 2,228 input
    and 861 output tokens that the budget charged and the meeting row could not
    carry, so the first of one hundred units stopped on an accounting gap rather
    than on a limit.
    """

    snapshot = budget.snapshot()
    recorded = _recorded_spend(meeting, entries)
    if (
        recorded.input_tokens != snapshot.input_tokens
        or recorded.output_tokens != snapshot.output_tokens
        or abs(recorded.cost_usd - snapshot.cost_usd) > 1e-9
    ):
        raise InstrumentError(
            f"seed {seed} on arm {arm.name}: the recorded spend over "
            f"{recorded.resolved_calls} resolved calls and "
            f"{recorded.charged_failures} charged failed attempts "
            f"({recorded.input_tokens} in / {recorded.output_tokens} out / "
            f"{recorded.cost_usd} USD) differs from the enforced budget "
            f"({snapshot.input_tokens} in / {snapshot.output_tokens} out / "
            f"{snapshot.cost_usd} USD)"
        )


#: Mirrors ``llm/budget.py``'s ``_COST_USD_CAP_SLACK``. The budget tolerates a
#: millionth of a dollar of binary-rounding noise before it calls a USD total an
#: overrun, and a check that re-reads its totals has to tolerate the same or it
#: would stop a run the budget itself considers inside its cap.
_COST_CAP_SLACK_USD: Final[float] = 1e-6


def _assert_charged_spend_is_within_caps(
    budget: GameBudget, *, level: str, seed: int, arm: InstrumentArm
) -> None:
    """Stop the run when a charge already applied left a budget past its cap.

    ``STOP_RULE`` makes "a token budget exhausted at either the per-unit or the
    run level" a stop, and the budget's PRE-FLIGHT is what normally delivers it,
    on the call that would cross the cap. One class of charge never reaches a
    pre-flight, though: a call the provider billed and then refused on its own
    schema validation is charged from its parse-failure metadata AFTER the fact
    (``llm/budgeted_client.py``), and the resulting
    :class:`~llm.budget.BudgetExceededError` is downgraded there to a note on
    the propagating exception, which the meeting layer then fail-softs. On the
    unit's last call the budget object is discarded with the overrun still on it
    and no later pre-flight exists to find it, so the ceiling would be crossed
    and the run would carry on.

    This is that missing arrival, and :data:`BUDGET_CAP_READBACK` is the
    statement of it the execution manifest quotes: after each unit both budgets
    are read back against the caps they were built with. It is a check on
    RECORDED spend and reports it as such — the tokens are gone either way, and
    the stop is what keeps the next unit from spending more.
    """

    snapshot = budget.snapshot()
    over = [
        f"{name} ({charged} charged against a {cap} cap)"
        for name, charged, cap in (
            ("input tokens", snapshot.input_tokens, snapshot.max_input_tokens),
            ("output tokens", snapshot.output_tokens, snapshot.max_output_tokens),
        )
        if charged > cap
    ]
    if snapshot.cost_usd > snapshot.max_cost_usd + _COST_CAP_SLACK_USD:
        over.append(
            f"cost ({snapshot.cost_usd} USD charged against a "
            f"{snapshot.max_cost_usd} USD cap)"
        )
    if over:
        raise BudgetExhausted(
            f"seed {seed} on arm {arm.name}: the {level} token budget is "
            f"exhausted on {', and '.join(over)}; the charge that crossed it is "
            "already spent, so the run stops here"
        )


def _assert_live_prompts_were_recorded(
    meeting: MeetingReplayEntry, *, calls: Sequence[CapturedCall], seed: int
) -> None:
    """Every recorded meeting call must be one the live client was handed.

    The supported grader reads the LIVE prompts, so a recording that does not
    mirror them would let the grader score inputs the model never saw. Extra
    live calls are fine — a failed call reaches no meeting row — so the check is
    one-directional.
    """

    available: Counter[tuple[str | None, str]] = Counter(
        (call.agent_id, call.prompt) for call in calls
    )
    for recorded in meeting.llm_calls:
        key = (recorded.agent_id, recorded.prompt)
        if available[key] <= 0:
            raise InstrumentError(
                f"seed {seed}: a recorded meeting call is not one of the live "
                "provider inputs the grader reads"
            )
        available[key] -= 1


# ---------------------------------------------------------------------------
# The graders
# ---------------------------------------------------------------------------

SupportVerdict = Literal["supported", "unsupported", "uncited"]

SUPPORTED_RUBRIC: Final[str] = (
    "A ballot is SUPPORTED when every citation it carries — the transcript turn "
    "in primary_reason_id, the episodic observation in "
    "primary_reason_observation_id, or both — appears verbatim in a prompt THAT "
    "VOTER was handed. It is UNSUPPORTED when a citation is present and no "
    "prompt of that voter's carries it, and UNCITED when it carries neither. "
    "The grader reads exactly the deciding agent's entitled inputs: the prompts, "
    "and nothing else. It never sees a role, a trajectory or the privileged "
    "grade, and the rubric is frozen here before any held-out outcome exists."
)

PRIVILEGED_RUBRIC: Final[str] = (
    "The privileged pass reads the hidden roles and grades what the supported "
    "pass cannot: whether the meeting ejected the IMPOSTOR (role-correct) and, "
    "separately, whether it did so on ballots that were both 'supported' by the "
    "presence pass and RELEVANT to the ejected player under the "
    "citation-relevance rule (right for that reason). The support labels are "
    "computed FIRST and are inputs here; no support label is revised after the "
    "role is known, and relevance reads only the recorded meeting and the "
    "voter's own prompts — never a role. Judge information never selects a "
    "tactical action, fabricates an observation, chooses a reply or supplies an "
    "accusation target: grading is a pure function over a finished UnitRecord "
    "and the run path calls no grader at all."
)

#: Frozen with the rest of the analysis and before any held-out outcome exists.
#: Presence is not aboutness: a ballot that guesses the impostor while citing a
#: turn about somebody else, or an alibi that has nothing to do with the player
#: it names, is a lucky guess with a citation stapled to it, and the primary
#: outcome is supposed to separate those from a supported inference.
CITATION_RELEVANCE_RUBRIC: Final[str] = (
    "A citation is RELEVANT to a named player when the evidence it identifies "
    "bears on that player. For a transcript turn (primary_reason_id): the "
    "recorded turn is the named player's own — they are its speaker, the case "
    "the ballot template itself asks a voter to cite when a contradiction broke "
    "their account — or it names that player anywhere in its recorded content, "
    "its structured observations, its claims and its free text included. For an "
    "episodic observation (primary_reason_observation_id): at least one line of "
    "that voter's OWN prompts carrying the cited id also names that player, "
    "which is the rendered '[obs ...]' memory line the id was copied from. A "
    "player id is matched as a whole token, so p-1 does not match p-10. A "
    "citation naming a turn this meeting did not record is not relevant to "
    "anyone. A ballot is RELEVANT when every citation it carries is relevant, "
    "OFF_TARGET when it carries one that is not, and UNCITED when it carries "
    "none. Relevance reads the recorded meeting and the voter's own prompts "
    "only: no role, no trajectory and no support label is an input to it."
)


@dataclass(frozen=True)
class SupportedGrade:
    """One ballot's support verdict from the voter's own entitled inputs."""

    voter: PlayerId
    target: str
    cited_turn_id: str | None
    cited_observation_id: str | None
    verdict: SupportVerdict
    guard_rewrite_reason: str | None

    @property
    def voter_authored(self) -> bool:
        """Whether this ballot is the voter's own call rather than a rewrite."""

        return self.guard_rewrite_reason is None


def grade_supported(
    ballots: Sequence[VoteBallot], *, prompts_by_agent: Mapping[str, Sequence[str]]
) -> tuple[SupportedGrade, ...]:
    """Grade every ballot's citation against that voter's OWN prompts.

    Entitled inputs only: the prompts the voter received. A citation that
    appears in somebody else's prompt is not support, which is why the lookup is
    keyed by voter rather than searched across the meeting.
    """

    grades: list[SupportedGrade] = []
    for ballot in ballots:
        own = tuple(prompts_by_agent.get(ballot.voter, ()))
        citations = [
            citation
            for citation in (
                ballot.primary_reason_id,
                ballot.primary_reason_observation_id,
            )
            if citation is not None
        ]
        if not citations:
            verdict: SupportVerdict = "uncited"
        elif all(any(citation in prompt for prompt in own) for citation in citations):
            verdict = "supported"
        else:
            verdict = "unsupported"
        grades.append(
            SupportedGrade(
                voter=ballot.voter,
                target=ballot.target,
                cited_turn_id=ballot.primary_reason_id,
                cited_observation_id=ballot.primary_reason_observation_id,
                verdict=verdict,
                guard_rewrite_reason=ballot.guard_rewrite_reason,
            )
        )
    return tuple(grades)


RelevanceVerdict = Literal["relevant", "off_target", "uncited"]

#: A player id is a whole token: ``p-1`` must not match inside ``p-10``.
_PLAYER_TOKEN: Final[str] = r"(?<![0-9A-Za-z_-]){player}(?![0-9A-Za-z_-])"


def _names_player(text: str, player: str) -> bool:
    """Whether ``text`` names ``player`` as a whole id rather than as a prefix."""

    return re.search(_PLAYER_TOKEN.format(player=re.escape(player)), text) is not None


def _turn_bears_on(turn: MeetingTurn, player: PlayerId) -> bool:
    """Whether a recorded turn is the player's own or names them in its content.

    The content is walked as the DUMPED STRUCTURE (:func:`_every_string_in`)
    rather than field by field: a turn carries a dozen observation and claim
    shapes, each naming players under a different key (``subject``, ``against``,
    ``supports``, ``body_of``, ``co_present``), and a rule enumerating them would
    silently stop covering the ones a later schema adds.
    """

    if turn.speaker == player:
        return True
    return any(
        _names_player(text, player)
        for text in _every_string_in(turn.model_dump(mode="json"))
    )


def _cited_line_names(
    prompts: Sequence[str], *, citation: str, player: PlayerId
) -> bool:
    """Whether a line of these prompts carrying ``citation`` also names ``player``."""

    return any(
        citation in line and _names_player(line, player)
        for prompt in prompts
        for line in prompt.splitlines()
    )


@dataclass(frozen=True)
class RelevanceGrade:
    """One ballot's citation relevance to the player under test."""

    voter: PlayerId
    target: str
    verdict: RelevanceVerdict


def grade_citation_relevance(
    ballots: Sequence[VoteBallot],
    *,
    subject: PlayerId,
    turns: Sequence[MeetingTurn],
    prompts_by_agent: Mapping[str, Sequence[str]],
) -> tuple[RelevanceGrade, ...]:
    """Grade each ballot's citations against :data:`CITATION_RELEVANCE_RUBRIC`.

    ``subject`` is the player the relevance is judged against — the ejected one,
    when :func:`grade_privileged` calls this. Separate from
    :func:`grade_supported` because they answer different questions: presence
    ("did this voter see the thing it cited") and aboutness ("does the thing it
    cited bear on the player it named"). A run is not graded on either alone.
    """

    by_id = {turn.turn_id: turn for turn in turns}
    grades: list[RelevanceGrade] = []
    for ballot in ballots:
        cited_turn = ballot.primary_reason_id
        cited_observation = ballot.primary_reason_observation_id
        if cited_turn is None and cited_observation is None:
            verdict: RelevanceVerdict = "uncited"
        else:
            relevant = True
            if cited_turn is not None:
                turn = by_id.get(cited_turn)
                relevant = turn is not None and _turn_bears_on(turn, subject)
            if relevant and cited_observation is not None:
                relevant = _cited_line_names(
                    tuple(prompts_by_agent.get(ballot.voter, ())),
                    citation=cited_observation,
                    player=subject,
                )
            verdict = "relevant" if relevant else "off_target"
        grades.append(
            RelevanceGrade(voter=ballot.voter, target=ballot.target, verdict=verdict)
        )
    return tuple(grades)


@dataclass(frozen=True)
class PrivilegedGrade:
    """The privileged pass: role truth, and the conjunction with support."""

    ejected_player_id: PlayerId | None
    ejected_role: Role | None
    role_correct: bool
    supported_correct_ejection: bool
    #: Ballots naming the ejected player, and how many of them cited something
    #: that does not bear on that player. Reported so a reader can see how often
    #: relevance, rather than presence, is what the primary outcome turned on.
    naming_ballots: int = 0
    off_target_citations: int = 0

    @property
    def wrongful_ejection(self) -> bool:
        """An innocent was ejected: the unit the acceptable-tradeoff bound counts.

        A skipped meeting is not wrongful — it decided nothing — so this is an
        ejection that landed on a crewmate, not the complement of
        ``role_correct``.
        """

        return self.ejected_player_id is not None and not self.role_correct


def grade_privileged(
    record: UnitRecord, *, supported: Sequence[SupportedGrade]
) -> PrivilegedGrade:
    """Score role truth and citation relevance, after support is already fixed.

    Takes the support grades as an argument rather than recomputing them, so the
    ordering the preregistration requires — support first, from entitled inputs
    only; truth second, from privileged state — is a property of the signature.

    Relevance is graded HERE, beside role truth, and it is the half of the
    primary outcome that presence cannot supply: a ballot naming the impostor
    while citing a turn about somebody else was right, but not for that reason.
    It reads no role of its own (:data:`CITATION_RELEVANCE_RUBRIC`); it is in
    this pass because the player it judges aboutness against — the one the
    meeting ejected — is only fixed once the unit is finished.
    """

    ejected = record.ejected_player_id
    if ejected is None:
        return PrivilegedGrade(
            ejected_player_id=None,
            ejected_role=None,
            role_correct=False,
            supported_correct_ejection=False,
        )
    role = record.roles.get(ejected)
    role_correct = role == "IMPOSTOR"
    naming = [grade for grade in supported if grade.target == ejected]
    every_naming_ballot_supported = bool(naming) and all(
        grade.verdict == "supported" and grade.voter_authored for grade in naming
    )
    relevance = grade_citation_relevance(
        [ballot for ballot in record.ballots if ballot.target == ejected],
        subject=ejected,
        turns=record.turns,
        prompts_by_agent=record.prompts_by_agent,
    )
    every_citation_relevant = bool(relevance) and all(
        grade.verdict == "relevant" for grade in relevance
    )
    return PrivilegedGrade(
        ejected_player_id=ejected,
        ejected_role=role,
        role_correct=role_correct,
        supported_correct_ejection=(
            role_correct and every_naming_ballot_supported and every_citation_relevant
        ),
        naming_ballots=len(relevance),
        off_target_citations=sum(
            1 for grade in relevance if grade.verdict == "off_target"
        ),
    )


@dataclass(frozen=True)
class UnitGrade:
    """One graded unit: the primary binary plus the counts behind it."""

    seed: int
    arm: ArmName
    outcome: str
    stop: Literal["terminal", "partial"]
    supported: tuple[SupportedGrade, ...]
    privileged: PrivilegedGrade

    @property
    def primary(self) -> bool:
        return self.privileged.supported_correct_ejection

    def verdict_counts(self) -> Mapping[str, int]:
        counts = Counter(grade.verdict for grade in self.supported)
        return {
            "supported": counts["supported"],
            "unsupported": counts["unsupported"],
            "uncited": counts["uncited"],
            "guard_rewritten": sum(
                1 for grade in self.supported if not grade.voter_authored
            ),
        }


def grade_unit(record: UnitRecord) -> UnitGrade:
    """The whole grading pass over one finished unit. Pure; never called mid-run."""

    supported = grade_supported(
        record.ballots, prompts_by_agent=record.prompts_by_agent
    )
    return UnitGrade(
        seed=record.seed,
        arm=record.arm,
        outcome=record.outcome,
        stop="terminal"
        if record.game_outcome in ("CREWMATES", "IMPOSTORS")
        else "partial",
        supported=supported,
        privileged=grade_privileged(record, supported=supported),
    )


# ---------------------------------------------------------------------------
# The paired comparison
# ---------------------------------------------------------------------------


class PairedResult(BaseModel):
    """The paired exact McNemar over the discordant units, and the decision."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    primary_outcome: str
    paired_units: int
    reference_arm: str
    candidate_arm: str
    reference_successes: int
    candidate_successes: int
    b: int
    c: int
    net: int
    p_exact: float
    alpha: float
    minimum_actionable_effect_units: int
    reference_wrongful_ejections: int
    candidate_wrongful_ejections: int
    wrongful_net: int
    meets_wrongful_ejection_tradeoff: bool
    meets_decision_rule: bool


def paired_result(
    grades: Sequence[UnitGrade],
    *,
    reference: ArmName = "repaired_clock",
    candidate: ArmName = "combined_accounts",
) -> PairedResult:
    """Pair the units by seed and compute the exact McNemar over the discordants.

    Refuses an unpaired seed rather than dropping it: a unit missing from one arm
    is a hole in the pairing, and silently analysing the rest would change the
    design after the fact.

    The wrongful-ejection tradeoff is computed here beside the test, not left to
    a reader: ``meets_decision_rule`` is the conjunction of all three frozen
    conditions, so a candidate that buys its supported-correct ejections by
    ejecting more innocents cannot satisfy the rule by satisfying two of them.
    """

    by_arm: dict[ArmName, dict[int, bool]] = {reference: {}, candidate: {}}
    wrongful_by_arm: dict[ArmName, dict[int, bool]] = {reference: {}, candidate: {}}
    for grade in grades:
        if grade.arm not in by_arm:
            raise InstrumentError(f"unit for unknown arm {grade.arm!r}")
        if grade.seed in by_arm[grade.arm]:
            raise InstrumentError(f"seed {grade.seed} appears twice on {grade.arm}")
        by_arm[grade.arm][grade.seed] = grade.primary
        wrongful_by_arm[grade.arm][grade.seed] = grade.privileged.wrongful_ejection
    seeds = sorted(by_arm[reference])
    if sorted(by_arm[candidate]) != seeds:
        raise InstrumentError(
            "the two arms did not run the same seeds; a paired test needs "
            "identical prefixes on both sides"
        )
    b = sum(
        1 for seed in seeds if by_arm[candidate][seed] and not by_arm[reference][seed]
    )
    c = sum(
        1 for seed in seeds if by_arm[reference][seed] and not by_arm[candidate][seed]
    )
    p_exact = exact_mcnemar_p(b, c)
    net = b - c
    reference_wrongful = sum(wrongful_by_arm[reference].values())
    candidate_wrongful = sum(wrongful_by_arm[candidate].values())
    wrongful_net = candidate_wrongful - reference_wrongful
    meets_tradeoff = wrongful_net <= net
    return PairedResult(
        primary_outcome=PRIMARY_OUTCOME,
        paired_units=len(seeds),
        reference_arm=reference,
        candidate_arm=candidate,
        reference_successes=sum(by_arm[reference].values()),
        candidate_successes=sum(by_arm[candidate].values()),
        b=b,
        c=c,
        net=net,
        p_exact=p_exact,
        alpha=DECISION_ALPHA,
        minimum_actionable_effect_units=MINIMUM_ACTIONABLE_EFFECT_UNITS,
        reference_wrongful_ejections=reference_wrongful,
        candidate_wrongful_ejections=candidate_wrongful,
        wrongful_net=wrongful_net,
        meets_wrongful_ejection_tradeoff=meets_tradeoff,
        meets_decision_rule=(
            p_exact < DECISION_ALPHA
            and net >= MINIMUM_ACTIONABLE_EFFECT_UNITS
            and meets_tradeoff
        ),
    )


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------


class ArmSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    arm: str
    units: int
    ejections: int
    role_correct: int
    wrongful_ejections: int
    supported_correct_ejections: int
    # Ballots naming the ejected player, and how many of those cited evidence
    # that does not bear on that player. The pair is what makes the primary
    # outcome readable: it says how often relevance rather than presence is what
    # a unit turned on, which a single conjunction cannot.
    naming_ballots: int
    off_target_citations: int
    terminal_units: int
    partial_units: int
    ballot_verdicts: Mapping[str, int]
    # The meeting-internal fail-soft substitutions this arm's units recorded.
    # Reported beside decision coverage rather than folded into the verdicts,
    # because a defaulted ballot is a SKIP the model did not choose and a
    # defaulted turn is a placeholder it did not write: without these counts
    # both are invisible, and ``units_with_defaults`` is what bounds how many of
    # this arm's decisions rest on a partly unauthored meeting.
    defaulted_turns: int
    defaulted_votes: int
    defaults_by_validation: int
    defaults_by_deadline: int
    degraded_openings: int
    units_with_defaults: int
    prompt_versions: Mapping[str, str]
    calls: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model_work_seconds: float


class InstrumentReport(BaseModel):
    """Aggregate counts only. No prompt, no prefix, no step, ever.

    :func:`assert_report_holds_no_prefix_bytes` checks that on the way out; the
    model's ``extra="forbid"`` keeps a future field from arriving unnoticed.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    provider: str
    model_ids: tuple[str, ...]
    execution_mode: str
    # The source identity the preregistration asks the manifest to bind: this
    # module's own bytes, the prompt set and the version markers the runner
    # recorded on every meeting row, and the digest of the freeze that supplied
    # the inputs. Together they say WHICH instrument, WHICH templates and WHICH
    # inputs produced the counts below.
    instrument_sha256: str
    prompt_set: str
    held_out_manifest_sha256: str
    held_out_accepted_seeds: int
    held_out_skipped_seeds: int
    limits: RunLimits
    sampling: SamplingConfig
    primary_outcome: str
    primary_outcome_rubric: str
    citation_relevance_rubric: str
    decision_rule: str
    wrongful_ejection_tradeoff: str
    stop_rule: str
    arms: tuple[ArmSummary, ...]
    paired: PairedResult
    elapsed_seconds: float
    model_work_seconds: float
    total_cost_usd: float
    dry_run: bool
    caveat: str


def instrument_sha256() -> str:
    """This module's own bytes, so a report names the instrument that made it."""

    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _one_prompt_version_set(
    records: Sequence[UnitRecord], *, arm: ArmName
) -> Mapping[str, str]:
    """The prompt versions every unit of ONE arm recorded, or a stop.

    Per arm, not per run: the two arms render different template families —
    ``combined_accounts`` renders the account templates — so their version
    markers differ by design and only a difference WITHIN an arm is a source
    change mid-run, which the preregistration's decision rules make a stop.
    """

    seen = {
        json.dumps(dict(record.prompt_versions), sort_keys=True)
        for record in records
        if record.arm == arm
    }
    if len(seen) > 1:
        raise InstrumentError(
            f"arm {arm} recorded {len(seen)} different prompt-version sets; a "
            "source change mid-run stops the comparison"
        )
    if not seen:
        return MappingProxyType({})
    versions: dict[str, str] = json.loads(next(iter(seen)))
    return MappingProxyType(versions)


def _every_string_in(value: object) -> list[str]:
    """Every string anywhere in a dumped report, keys included.

    Walking the DUMPED STRUCTURE rather than the JSON text is what makes the
    check honest: a prefix smuggled into a string field survives
    ``model_dump_json`` as an ESCAPED substring, so a search over the encoded
    text would look clean while the field still carried the input.
    """

    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        found: list[str] = []
        for key, item in value.items():
            if isinstance(key, str):
                found.append(key)
            found.extend(_every_string_in(item))
        return found
    if isinstance(value, (list, tuple)):
        return [text for item in value for text in _every_string_in(item)]
    return []


def assert_report_holds_no_prefix_bytes(
    report: InstrumentReport, prefixes: Iterable[HeldOutPrefix]
) -> None:
    """Refuse a report that carries any held-out prefix content.

    Checks every string in the dumped report for each prefix's canonical JSON
    and for each of its steps' canonical JSON — the step is the smaller unit and
    the one a careless summary would reach for. This is the guard behind "the
    runner opens no prefix, prints none".
    """

    strings = _every_string_in(report.model_dump(mode="json"))
    for prefix in prefixes:
        whole = canonical_prefix_json(prefix)
        if any(whole in text for text in strings):
            raise PrefixBytesLeaked(
                f"the report carries the canonical JSON of seed {prefix.seed}"
            )
        for step in prefix.steps:
            fragment = json.dumps(
                step.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
            )
            if any(fragment in text for text in strings):
                raise PrefixBytesLeaked(
                    f"the report carries a scripted step of seed {prefix.seed}"
                )
    leaked = legacy_body_handles(strings)
    if leaked:
        raise PrefixBytesLeaked(
            "the report carries a legacy body handle: " + ", ".join(sorted(set(leaked)))
        )


def _summarize_arm(
    arm: ArmName,
    *,
    grades: Sequence[UnitGrade],
    usage: ArmUsage,
    records: Sequence[UnitRecord],
) -> ArmSummary:
    own = [grade for grade in grades if grade.arm == arm]
    verdicts: Counter[str] = Counter()
    for grade in own:
        verdicts.update(grade.verdict_counts())
    own_records = [record for record in records if record.arm == arm]
    defaults = DefaultedAttempts()
    for record in own_records:
        defaults = defaults.plus(record.defaults)
    return ArmSummary(
        arm=arm,
        units=len(own),
        ejections=sum(1 for grade in own if grade.outcome == "EJECTED"),
        role_correct=sum(1 for grade in own if grade.privileged.role_correct),
        wrongful_ejections=sum(
            1 for grade in own if grade.privileged.wrongful_ejection
        ),
        supported_correct_ejections=sum(1 for grade in own if grade.primary),
        naming_ballots=sum(grade.privileged.naming_ballots for grade in own),
        off_target_citations=sum(
            grade.privileged.off_target_citations for grade in own
        ),
        terminal_units=sum(1 for grade in own if grade.stop == "terminal"),
        partial_units=sum(1 for grade in own if grade.stop == "partial"),
        ballot_verdicts=dict(sorted(verdicts.items())),
        defaulted_turns=defaults.defaulted_turns,
        defaulted_votes=defaults.defaulted_votes,
        defaults_by_validation=defaults.by_validation,
        defaults_by_deadline=defaults.by_deadline,
        degraded_openings=defaults.degraded_openings,
        units_with_defaults=sum(
            1 for record in own_records if record.defaults.total > 0
        ),
        prompt_versions=dict(_one_prompt_version_set(records, arm=arm)),
        calls=usage.calls,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_usd=usage.cost_usd,
        model_work_seconds=usage.model_work_seconds,
    )


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------


@dataclass
class _RunState:
    """Mutable bookkeeping owned by one :func:`run_instrument` call.

    A local object rather than module state: AGENTS.md forbids module-level
    mutable state, and two concurrent callers must not share a tally.
    """

    usage_by_arm: dict[str, ArmUsage] = field(default_factory=dict)
    completed: int = 0

    def charge(self, arm: ArmName, calls: Sequence[CapturedCall]) -> None:
        self.usage_by_arm[arm] = self.usage_by_arm.get(arm, ArmUsage()).plus(calls)


def run_instrument(
    *,
    output_dir: Path,
    client: LLMClient | None = None,
    provider: str = "fake",
    live_invocation: LiveRunInvocation | None = None,
    repo_root: Path = _REPO_ROOT,
    units: int | None = None,
    limits: RunLimits = AUTHORIZED_LIMITS,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
) -> InstrumentReport:
    """Run both arms over the frozen set, sequentially, and grade the result.

    Order of operations is load-bearing. The authorization gate and the
    client-type check run before anything else, the frozen set is verified before
    a unit runs, the arms run paired seed by seed, and every grader runs only
    after the last unit, over finished records.

    On the CLI's live path the frozen set is verified one level up, before the
    client this function is handed even exists
    (:func:`assert_ready_for_a_live_run`); the check here is the same one again,
    and it is cheap and offline.
    """

    assert_live_run_is_authorized(
        provider=provider,
        invocation=live_invocation,
        limits=limits,
        sampling=sampling,
        units=units,
        repo_root=repo_root,
    )
    # The label said what this run is; this says what it actually holds. Both
    # directions are refused, and both before anything is spent.
    assert_client_matches_provider(provider=provider, client=client)
    frozen = verify_frozen_set(repo_root)
    prefixes = frozen.prefixes if units is None else frozen.prefixes[:units]
    arms = instrument_arms()
    planned = len(prefixes) * len(arms)

    inner = client if client is not None else DryRunProvider()
    work_clock = _ModelWorkClock(max_seconds=limits.model_work_seconds)
    instrument_client = _InstrumentClient(
        inner,
        work_clock=work_clock,
        turn_max_tokens=sampling.turn_max_tokens,
        vote_max_tokens=sampling.vote_max_tokens,
        # A live run is bound to the model the invocation names; a dry run has
        # no served model to bind, and its fixture says so in the report's
        # ``model_ids`` and its caveat.
        expected_model=None if live_invocation is None else live_invocation.model,
    )
    run_budget = GameBudget(
        max_cost_usd=limits.max_cost_usd,
        max_input_tokens=limits.run_max_input_tokens,
        max_output_tokens=limits.run_max_output_tokens,
    )
    deadline = RunDeadline(seconds=limits.elapsed_seconds)
    output_dir.mkdir(parents=True, exist_ok=True)

    state = _RunState()
    records: list[UnitRecord] = []
    started = time.monotonic()
    for prefix in prefixes:
        for arm in arms:
            try:
                deadline.check()
                record = run_unit(
                    prefix,
                    arm=arm,
                    client=instrument_client,
                    run_budget=run_budget,
                    deadline=deadline,
                    work_clock=work_clock,
                    output_dir=output_dir,
                    provider=provider,
                    limits=limits,
                    sampling=sampling,
                )
            # Every way a unit can fail is a stop that reports its partial
            # state, which is why this catches Exception rather than the four
            # limit classes it started with. An attempt that never resolved is
            # a stop with partial accounting — a provider transport failure, a
            # mid-run legacy body handle
            # (:class:`~experiments.held_out_prefixes.HeldOutPrefixError`), a
            # spend that does not reconcile or a meeting that resolved the wrong
            # number of ballots all land here. A meeting-internal default does
            # NOT: the engine substituted for it and the unit resolved, so it is
            # counted onto :class:`DefaultedAttempts` instead. Nothing is
            # swallowed either way:
            # the class and message are copied into ``reason`` and the original
            # is chained, so a stop is louder than the raw exception, not
            # quieter. ``BaseException`` is deliberately not caught — an
            # interrupt is not a run stop.
            except Exception as exc:
                # The stopped unit's calls are still in the client. They were
                # spent, so they are charged into the partial accounting before
                # it is reported — "retains partial evidence and unresolved
                # accounting" means the spend that bought nothing, too.
                state.charge(arm.name, instrument_client.take())
                raise InstrumentAborted(
                    PartialRun(
                        reason=f"{type(exc).__name__}: {exc}",
                        completed_units=state.completed,
                        planned_units=planned,
                        usage_by_arm=dict(state.usage_by_arm),
                        elapsed_seconds=time.monotonic() - started,
                        model_work_seconds=work_clock.seconds,
                    )
                ) from exc
            state.charge(arm.name, record.calls)
            state.completed += 1
            records.append(record)

    grades = [grade_unit(record) for record in records]
    report = InstrumentReport(
        provider=provider,
        model_ids=tuple(
            sorted({call.model for record in records for call in record.calls})
        ),
        execution_mode=AUTHORIZED_EXECUTION_MODE,
        instrument_sha256=instrument_sha256(),
        prompt_set=AUTHORIZED_PROMPT_SET,
        limits=limits,
        sampling=sampling,
        held_out_manifest_sha256=frozen.manifest_sha256,
        held_out_accepted_seeds=len(frozen.accepted_seeds),
        held_out_skipped_seeds=len(frozen.skipped_seeds),
        primary_outcome=PRIMARY_OUTCOME,
        primary_outcome_rubric=PRIMARY_OUTCOME_RUBRIC,
        citation_relevance_rubric=CITATION_RELEVANCE_RUBRIC,
        decision_rule=DECISION_RULE,
        wrongful_ejection_tradeoff=WRONGFUL_EJECTION_TRADEOFF,
        stop_rule=STOP_RULE,
        arms=tuple(
            _summarize_arm(
                arm.name,
                grades=grades,
                usage=state.usage_by_arm.get(arm.name, ArmUsage()),
                records=records,
            )
            for arm in arms
        ),
        paired=paired_result(grades),
        elapsed_seconds=time.monotonic() - started,
        model_work_seconds=work_clock.seconds,
        total_cost_usd=sum(usage.cost_usd for usage in state.usage_by_arm.values()),
        dry_run=provider == "fake",
        caveat=DRY_RUN_CAVEAT if provider == "fake" else PRIMARY_OUTCOME_RUBRIC,
    )
    assert_report_holds_no_prefix_bytes(report, prefixes)
    return report


def run_dry(
    *,
    output_dir: Path | None = None,
    repo_root: Path = _REPO_ROOT,
    units: int | None = None,
    limits: RunLimits = AUTHORIZED_LIMITS,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
    live_invocation: LiveRunInvocation | None = None,
) -> InstrumentReport:
    """The fake-provider mechanics check. Refuses a live invocation outright.

    Writes every replay into a temporary directory when none is given, so a dry
    run leaves no prefix bytes behind at all.
    """

    if live_invocation is not None:
        raise LiveRunNotAuthorized(
            "the dry run is the mechanics check and never the authorized run; "
            "it takes no LiveRunInvocation"
        )
    if output_dir is not None:
        return run_instrument(
            output_dir=output_dir,
            provider="fake",
            repo_root=repo_root,
            units=units,
            limits=limits,
            sampling=sampling,
        )
    with TemporaryDirectory() as directory:
        return run_instrument(
            output_dir=Path(directory),
            provider="fake",
            repo_root=repo_root,
            units=units,
            limits=limits,
            sampling=sampling,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    """``--dry-run`` is the only mode any gate uses; a live run needs three flags."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--provider", default="fake")
    parser.add_argument("--execution-manifest", type=Path, default=None)
    parser.add_argument(
        LIVE_RUN_FLAG,
        dest="i_am_the_runner",
        action="store_true",
        help=(
            "the runner's explicit statement that this invocation is the "
            "authorized live run named in the execution manifest"
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--units",
        type=int,
        default=None,
        help=(
            "run only the first N frozen prefixes. A DRY-RUN knob: a live "
            "invocation carrying it is refused, because a live run is the whole "
            "frozen set and a subset is a pilot"
        ),
    )
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.dry_run or args.provider == "fake":
        report = run_dry(output_dir=args.output_dir, units=args.units)
    else:
        if args.execution_manifest is None or not args.i_am_the_runner:
            parser.error(
                "a live provider needs --execution-manifest and --i-am-the-runner; "
                "the manifest authorizes limits, the invocation authorizes the run"
            )
        if args.output_dir is None:
            parser.error("a live run writes its results; pass --output-dir")
        invocation = LiveRunInvocation.naming(
            args.execution_manifest,
            provider=args.provider,
            model=AUTHORIZED_MODEL,
        )
        # Authorized AND verified before a client exists: an unauthorized shape
        # — a unit override, moved limits — must not construct a provider it may
        # not use, and neither must a run whose held-out set has moved. The
        # verified set is what ``build_authorized_client`` requires, so that
        # order cannot be reversed by editing these two lines.
        frozen = assert_ready_for_a_live_run(
            provider=args.provider, invocation=invocation, units=args.units
        )
        report = run_instrument(
            output_dir=args.output_dir,
            # NOT ``build_default_client()``: that reads the ambient environment
            # for both provider and model, so an invocation labelled
            # ``featherless`` would reach whatever the shell happened to name.
            client=build_authorized_client(frozen),
            provider=args.provider,
            live_invocation=invocation,
            units=args.units,
        )
    payload = report.model_dump_json(indent=2)
    if args.json is not None:
        args.json.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover - the operator entry point
    raise SystemExit(main())
