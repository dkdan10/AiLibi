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
  requires an explicit :class:`LiveRunInvocation` naming the execution manifest
  (:func:`resolve_live_client`). No test, CI job or dry run constructs one, and
  :func:`run_dry` refuses one outright.

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
    TEMPORAL_OBSERVATION_VERSION,
    GeneratedSet,
    HeldOutPrefix,
    assert_no_legacy_body_handles,
    canonical_prefix_json,
    generate,
    legacy_body_handles,
    prefix_sha256,
)
from llm.budget import BudgetExceededError, GameBudget
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from meetings.manager import DEFAULT_TURN_MAX_TOKENS, DEFAULT_VOTE_MAX_TOKENS
from meetings.schemas import MeetingTurn, ModelAuthoredVoteBallot, VoteBallot
from observation.action_intent import ActionIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import (
    HeadlessGame,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.replay import (
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


# ---------------------------------------------------------------------------
# The preregistered analysis, frozen before any outcome is inspected
# ---------------------------------------------------------------------------

#: The one binary the paired test is computed on. Named here so the manifest and
#: the code cannot drift, and so no second outcome can be promoted to primary
#: after the fact.
PRIMARY_OUTCOME: Final[str] = "supported_correct_ejection"

PRIMARY_OUTCOME_RUBRIC: Final[str] = (
    "A unit scores 1 when its meeting ejected the player whose hidden role is "
    "IMPOSTOR and every ballot naming that player carried a citation the "
    "supported grader graded 'supported'; otherwise 0. Role-correctness alone "
    "and support alone are reported beside it and neither is the primary "
    "outcome."
)

#: The net paired difference (b - c over 50 paired units) below which a
#: difference is not acted on, whatever its p value.
MINIMUM_ACTIONABLE_EFFECT_UNITS: Final[int] = 10

#: Two-sided alpha for the exact paired McNemar test.
DECISION_ALPHA: Final[float] = 0.05

DECISION_RULE: Final[str] = (
    "combined_accounts advances to an explicitly scoped adopting review only if "
    "BOTH hold on the 50 paired units: the two-sided exact McNemar p over the "
    "discordant pairs (scripts/paired_stats.py::exact_mcnemar_p) is below "
    "0.05, AND the net paired difference b - c is at least 10 units. Any other "
    "result is inconclusive, and inconclusive is not success. A result in "
    "either direction is a measurement, never an adoption: adoption stays a "
    "separate owner decision on a separate card."
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
    "deadline or the model-work window; a per-call response that reached its "
    "output cap (a truncation is a stop, not a datum); a held-out digest or "
    "skip that differs from the frozen manifest; a rendered prompt or "
    "regenerated prefix matching the legacy body handle; or a unit whose "
    "recorded observation clock or experiment config is not the arm's. No stop "
    "condition reads an outcome: the 50 paired units are a fixed sample with no "
    "interim analysis and no optional stopping, so nothing here can be tripped "
    "by a result the run has produced."
)

_ANALYSIS_FREEZE_NOTE: Final[str] = (
    "PRIMARY_OUTCOME, DECISION_RULE, MINIMUM_ACTIONABLE_EFFECT_UNITS and "
    "STOP_RULE are module constants and the execution manifest quotes them "
    "verbatim, so the analysis is frozen in code and in the record before any "
    "held-out outcome exists."
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
    def naming(cls, manifest_path: Path, *, provider: str, model: str) -> Self:
        """Build an invocation from the manifest on disk, or refuse.

        Refuses a manifest that is not the authorized path, is absent, or does
        not carry the authorized provider and model — an invocation that names
        a manifest saying something else authorizes nothing.
        """

        resolved = manifest_path.resolve()
        if resolved.as_posix().split("/")[-3:] != EXECUTION_MANIFEST_PATH.split("/"):
            raise LiveRunNotAuthorized(
                "a live run names the authorized execution manifest "
                f"{EXECUTION_MANIFEST_PATH}, got {manifest_path}"
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
) -> None:
    """Refuse any non-fake provider without an explicit live invocation.

    ``fake`` is the only provider that passes without one, and it is the default
    everywhere in this module. Every other value — including one the owner has
    authorized in the manifest — needs the runner to say so at the call, because
    the manifest authorizes LIMITS and the invocation is the run.
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
    if limits != AUTHORIZED_LIMITS:
        raise LiveRunNotAuthorized(
            "a live run runs under the authorized limits exactly; the limits "
            "this run carries are not the ones the owner authorized"
        )


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
    """

    def __init__(self, *, max_seconds: float) -> None:
        if max_seconds <= 0:
            raise ValueError("the model-work window must be positive")
        self._max_seconds = max_seconds
        self._seconds = 0.0

    @property
    def seconds(self) -> float:
        return self._seconds

    def charge(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError(f"a call cannot take {seconds} seconds")
        self._seconds += seconds
        if self._seconds > self._max_seconds:
            raise RunDeadlineExceeded(
                f"model-work window exhausted: {self._seconds:.1f}s of "
                f"{self._max_seconds:.1f}s"
            )


class _InstrumentClient:
    """Wrap the provider to enforce the per-call caps and capture the prompts.

    Three jobs, none of which the budget layer does:

    1. refuse a ``max_tokens`` that is not one of the two shipped caps, so
       "the shipped defaults unchanged" is checked rather than asserted;
    2. treat a response that reached its cap as a STOP — a truncation is a cap
       artifact, and the authorization says a truncation in either arm is a
       stop, not a datum;
    3. hold the prompts the supported grader reads, in memory, for one unit.

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
    ) -> None:
        self._inner = inner
        self._work_clock = work_clock
        self._allowed_max_tokens = frozenset({turn_max_tokens, vote_max_tokens})
        self._ceiling = max(turn_max_tokens, vote_max_tokens)
        self._calls: list[CapturedCall] = []
        # A zero pre-flight rate is the honest statement for a client whose
        # completions are free: it disables ``BudgetedLLMClient``'s USD
        # dimension exactly as the live provider's own zero rate does, so the
        # authorized $0.00 cap means the same thing on both paths.
        self.preflight_cost_per_input_token_usd = 0.0
        self.preflight_cost_per_output_token_usd = 0.0

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
        response = await self._inner.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        seconds = time.monotonic() - started
        if response.usage.output_tokens >= max_tokens:
            raise PerCallCapExceeded(
                f"a response reached its {max_tokens}-token output cap "
                f"({response.usage.output_tokens} tokens); a truncation is a "
                "stop, not a datum"
            )
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
        return response


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


def verify_frozen_set(repo_root: Path = _REPO_ROOT) -> FrozenSet:
    """Regenerate the held-out set and refuse to proceed on any difference.

    Runs BEFORE any arm and before any provider exists. What it compares:
    the band, the roster, the tick budget, the observation clock, every accepted
    seed and digest in order, and the skip list with its reason codes. A
    mismatch names seeds and digests only — both are already published in the
    committed manifest — and never a step.

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

    generated = generate()
    expected_accepted = [
        (int(row["seed"]), str(row["sha256"])) for row in manifest["accepted"]
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
        (int(row["seed"]), str(row["reason"])) for row in manifest["skipped"]
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
    turn_ids: tuple[str, ...]
    roles: Mapping[PlayerId, Role]
    prompts_by_agent: Mapping[str, tuple[str, ...]]
    calls: tuple[CapturedCall, ...]
    game_outcome: str
    recorded_temporal_version: int | None
    recorded_experiment_config: RecordedExperimentConfig | None
    prompt_versions: Mapping[str, str]


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
) -> UnitRecord:
    """Run one frozen prefix's meeting under one arm through the public API.

    The tick budget stops the game one tick after the report, so the unit is
    exactly "one frozen legal prefix followed by one fresh meeting" and nothing
    downstream of the decision is claimed (the preregistration's "Apply that
    meeting's outcome and stop").
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
    _reconcile_recorded_spend(meeting, budget=unit_budget, seed=prefix.seed, arm=arm)

    calls = client.take()
    prompts: dict[str, list[str]] = {}
    for call in calls:
        if call.agent_id is not None:
            prompts.setdefault(call.agent_id, []).append(call.prompt)
    assert_no_legacy_body_handles([call.prompt for call in calls])
    _assert_live_prompts_were_recorded(meeting, calls=calls, seed=prefix.seed)
    del work_clock  # charged inside the client; named here so the caller sees it

    return UnitRecord(
        seed=prefix.seed,
        arm=arm.name,
        meeting_id=meeting.meeting_id,
        outcome=meeting.outcome,
        ejected_player_id=meeting.ejected_player_id,
        ballots=meeting.ballots,
        turn_ids=tuple(turn.turn_id for turn in meeting.transcript.turns),
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


def _reconcile_recorded_spend(
    meeting: MeetingReplayEntry, *, budget: GameBudget, seed: int, arm: InstrumentArm
) -> None:
    """Compare the RECORDED per-call spend against the enforced budget snapshot."""

    snapshot = budget.snapshot()
    recorded_input = sum(call.input_tokens for call in meeting.llm_calls)
    recorded_output = sum(call.output_tokens for call in meeting.llm_calls)
    recorded_cost = sum(call.cost_usd for call in meeting.llm_calls)
    if (
        recorded_input != snapshot.input_tokens
        or recorded_output != snapshot.output_tokens
        or abs(recorded_cost - snapshot.cost_usd) > 1e-9
    ):
        raise InstrumentError(
            f"seed {seed} on arm {arm.name}: the recorded spend "
            f"({recorded_input} in / {recorded_output} out / {recorded_cost} USD) "
            f"differs from the enforced budget ({snapshot.input_tokens} in / "
            f"{snapshot.output_tokens} out / {snapshot.cost_usd} USD)"
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
    "The privileged pass reads the hidden roles and grades two things the "
    "supported pass cannot: whether the meeting ejected the IMPOSTOR "
    "(role-correct) and, separately, whether it did so on ballots the supported "
    "pass had already graded 'supported' (right for that reason). The support "
    "labels are computed FIRST and are inputs here; no support label is revised "
    "after the role is known. Judge information never selects a tactical action, "
    "fabricates an observation, chooses a reply or supplies an accusation "
    "target: grading is a pure function over a finished UnitRecord and the run "
    "path calls no grader at all."
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


@dataclass(frozen=True)
class PrivilegedGrade:
    """The privileged pass: role truth, and the conjunction with support."""

    ejected_player_id: PlayerId | None
    ejected_role: Role | None
    role_correct: bool
    supported_correct_ejection: bool


def grade_privileged(
    record: UnitRecord, *, supported: Sequence[SupportedGrade]
) -> PrivilegedGrade:
    """Score role truth from the hidden roles, after support is already fixed.

    Takes the support grades as an argument rather than recomputing them, so the
    ordering the preregistration requires — support first, from entitled inputs
    only; truth second, from privileged state — is a property of the signature.
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
    return PrivilegedGrade(
        ejected_player_id=ejected,
        ejected_role=role,
        role_correct=role_correct,
        supported_correct_ejection=role_correct and every_naming_ballot_supported,
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
    """

    by_arm: dict[ArmName, dict[int, bool]] = {reference: {}, candidate: {}}
    for grade in grades:
        if grade.arm not in by_arm:
            raise InstrumentError(f"unit for unknown arm {grade.arm!r}")
        if grade.seed in by_arm[grade.arm]:
            raise InstrumentError(f"seed {grade.seed} appears twice on {grade.arm}")
        by_arm[grade.arm][grade.seed] = grade.primary
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
        meets_decision_rule=(
            p_exact < DECISION_ALPHA and net >= MINIMUM_ACTIONABLE_EFFECT_UNITS
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
    supported_correct_ejections: int
    terminal_units: int
    partial_units: int
    ballot_verdicts: Mapping[str, int]
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
    primary_outcome: str
    decision_rule: str
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
    return ArmSummary(
        arm=arm,
        units=len(own),
        ejections=sum(1 for grade in own if grade.outcome == "EJECTED"),
        role_correct=sum(1 for grade in own if grade.privileged.role_correct),
        supported_correct_ejections=sum(1 for grade in own if grade.primary),
        terminal_units=sum(1 for grade in own if grade.stop == "terminal"),
        partial_units=sum(1 for grade in own if grade.stop == "partial"),
        ballot_verdicts=dict(sorted(verdicts.items())),
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
) -> InstrumentReport:
    """Run both arms over the frozen set, sequentially, and grade the result.

    Order of operations is load-bearing. The frozen set is verified BEFORE a
    provider is constructed, so a run against a moved set cannot spend anything;
    the arms run paired seed by seed; and every grader runs only after the last
    unit, over finished records.
    """

    assert_live_run_is_authorized(
        provider=provider, invocation=live_invocation, limits=limits
    )
    frozen = verify_frozen_set(repo_root)
    prefixes = frozen.prefixes if units is None else frozen.prefixes[:units]
    arms = instrument_arms()
    planned = len(prefixes) * len(arms)

    inner = client if client is not None else DryRunProvider()
    work_clock = _ModelWorkClock(max_seconds=limits.model_work_seconds)
    instrument_client = _InstrumentClient(inner, work_clock=work_clock)
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
                )
            except (
                BudgetExceededError,
                RunDeadlineExceeded,
                PerCallCapExceeded,
                ProvenanceMismatch,
            ) as exc:
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
        held_out_manifest_sha256=frozen.manifest_sha256,
        held_out_accepted_seeds=len(frozen.accepted_seeds),
        held_out_skipped_seeds=len(frozen.skipped_seeds),
        primary_outcome=PRIMARY_OUTCOME,
        decision_rule=DECISION_RULE,
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
        )
    with TemporaryDirectory() as directory:
        return run_instrument(
            output_dir=Path(directory),
            provider="fake",
            repo_root=repo_root,
            units=units,
            limits=limits,
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
        "--i-am-the-runner",
        action="store_true",
        help=(
            "the runner's explicit statement that this invocation is the "
            "authorized live run named in the execution manifest"
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--units", type=int, default=None)
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
        from llm.provider import build_default_client

        report = run_instrument(
            output_dir=args.output_dir,
            client=build_default_client(),
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
