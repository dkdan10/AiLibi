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

The second mode: the development calibration
--------------------------------------------

:func:`run_calibration` measures what the provider CHARGES, on the first
:data:`CALIBRATION_PAIRED_SEEDS` accepted seeds of a band a stopped run already
converted to development data. It exists because this evaluation was sized in
charged tokens, enforced in reserved ones, and only ever met the real provider
on the held-out run itself (``tasks/diagnosis-2026-09-13-live-run-stops.md``).
It shares the run's path — :func:`run_unit`, the same wrapper, the same budgets,
the same arms — and shares none of its authorization: its own limits
(:data:`CALIBRATION_LIMITS`), its own clause in the manifest
(:data:`CALIBRATION_CLAUSE`), its own gate
(:func:`assert_calibration_is_authorized`) and its own inputs
(:func:`verify_calibration_set`, which refuses the held-out record by name). It
grades nothing: no grader runs, no paired statistic is computed and no meeting
outcome is reported, so nothing it measures can reach the frozen analysis.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter
from collections.abc import Awaitable, Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from types import MappingProxyType
from typing import Any, Final, Literal, Self, TypeVar, get_args

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.perception import ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from experiments.held_out_prefixes import (
    CONVERTED_BANDS,
    MANIFEST_PATH,
    MAX_TICKS,
    PREREGISTERED_BAND,
    TEMPORAL_OBSERVATION_VERSION,
    ConvertedBand,
    GeneratedSet,
    HeldOutPrefix,
    PrefixRoster,
    SeedBand,
    assert_no_legacy_body_handles,
    build_prefix,
    canonical_prefix_json,
    generate,
    legacy_body_handles,
    prefix_sha256,
)
from experiments.held_out_prefixes import AUTHORIZED_ROSTER as FROZEN_PREFIX_ROSTER
from llm.budget import BudgetExceededError, GameBudget
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.fake_provider import FAKE_FINISH_REASON, FakeProvider
from llm.provider import extract_parse_failure
from meetings.citation_relevance import citations_bear_on
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    DEFAULT_TURN_FREE_TEXT,
    DEFAULT_TURN_MAX_TOKENS,
    DEFAULT_VOTE_MAX_TOKENS,
    DEFAULT_VOTE_RATIONALE,
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    OFF_TARGET_CITATION_EJECT_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    MeetingConfig,
)
from meetings.schemas import (
    AccusationClaim,
    BallotTargetRewriteReason,
    Claim,
    CorroborationClaim,
    MeetingTurn,
    ModelAuthoredVoteBallot,
    TurnAnnotationKind,
    VoteBallot,
)
from meetings.voting import SKIP_TARGET
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

from paired_stats import exact_mcnemar_p, one_sided_binomial_p  # noqa: E402


# ---------------------------------------------------------------------------
# The authorized limits (tasks/work/fresh-deduction-authorization.md)
# ---------------------------------------------------------------------------
#
# Every constant below is a value the owner authorized by merging #437 on
# 2026-09-07 (merge commit 0f49d8e6; ruling B.12 in
# tasks/owner-decisions-2026-09-07.md), except the six the later authorization
# cards moved and name: the two wall windows, from
# tasks/work/fresh-deduction-authorization-3.md (2026-09-13), and the turn cap
# and the four token ceilings, from tasks/work/fresh-deduction-authorization-4.md
# (2026-09-14), which sized them on that day's live development calibration.
# They are copied here so the instrument ENFORCES the manifest rather than
# describing it, and tests/experiments/test_fresh_deduction_instrument.py
# asserts the manifest quotes each of them. Changing one here without a new
# authorization is a spending decision, not a refactor.

#: The provider name the manifest binds. Anything else needs its own manifest.
AUTHORIZED_PROVIDER: Final[str] = "featherless"

#: The served model id, locked 2026-07-12 (Task 16.2).
AUTHORIZED_MODEL: Final[str] = "Qwen/Qwen3.6-27B"

#: The prompt set the model lock carries.
AUTHORIZED_PROMPT_SET: Final[str] = "qwen3_6_27b"

#: The per-call output caps. The vote cap is the shipped default, unchanged and
#: written as such. The TURN cap is not: the fourth authorization
#: (``tasks/work/fresh-deduction-authorization-4.md``, 2026-09-14) raised it from
#: the shipped 2,048 to 4,096 because the development calibration of that day
#: charged 2,036 output tokens on its largest candidate turn — 1 of 15 — and a
#: truncation is a stop with no retry, while the committed lab rows for this
#: model ran at ``max_tokens=4096``. It is therefore written here as a number
#: rather than read from ``meetings.manager``, and the run serves it through
#: :data:`AUTHORIZED_SAMPLING`'s own :class:`~meetings.manager.MeetingConfig`,
#: so no default-path byte moves and no other campaign draws differently. The
#: instrument still refuses a call asking for more than the turn cap and refuses
#: a ``max_tokens`` that is neither authorized value, so "the caps this manifest
#: binds" is a check rather than a claim.
AUTHORIZED_TURN_MAX_TOKENS: Final[int] = 4_096
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

#: The run-level hard stop, both token dimensions. Re-sized by the FIFTH
#: authorization (``tasks/work/fresh-deduction-authorization-5.md``, 2026-09-15)
#: from the second live development calibration of that day
#: (``audits/deduction-candidate/calibration-2-2026-09-15/calibration.json``)
#: rather than from a projection: :data:`CEILING_PROPOSAL_RULE`, computed by
#: :func:`ceiling_proposal` over that sitting's 120 units — the larger of a
#: hundred units at the measured mean x 1.5 and a hundred units at the largest
#: measured unit on each dimension, with ONE further turn cap on the output side
#: for the run's last in-flight reservation (100 x 4,176 + 4,096 = 421,696,
#: rounded up). The fourth authorization's figures were 3,710,000 / 459,000;
#: the INPUT ceiling RISES because v4's largest unit charged 38,440 against the
#: 37,100 a hundred of them were allowed, and the OUTPUT ceiling FALLS because
#: the rule is followed and v4 made units smaller on output. The figures merged
#: on 2026-09-07 were 2,400,000 / 200,000.
AUTHORIZED_RUN_MAX_INPUT_TOKENS: Final[int] = 3_844_000
AUTHORIZED_RUN_MAX_OUTPUT_TOKENS: Final[int] = 422_000

#: The per-unit hard stop, charged upward into the run-level parent. Also the
#: fifth authorization's, from the same sitting: three times the largest
#: measured unit (38,440 input; 4,176 output gives 12,528), with the OUTPUT
#: figure held to the reservation schedule the raised turn cap makes —
#: :func:`unit_output_reservation` is 15,360 — and rounded up to 16,000, which
#: is why the output ceiling does not move while the input one rises from the
#: fourth authorization's 106,000. The figures merged on 2026-09-07 were
#: 45,000 / 4,000, and :func:`assert_limits_are_feasible` refuses that output
#: ceiling under either turn cap.
AUTHORIZED_UNIT_MAX_INPUT_TOKENS: Final[int] = 116_000
AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS: Final[int] = 16_000

#: 6 h of model work inside an 8 h elapsed window: two limits and therefore two
#: clocks, the elapsed one :class:`~orchestrator.run_limits.RunDeadline` and the
#: work one the summed provider-call wall :class:`_InstrumentClient`
#: accumulates. The work window fits a sequential six hundred calls at the
#: slowest pace this evaluation has measured — 26.6 s each, about 4 h 26 m —
#: and the elapsed margin covers one recorded provider-side stall on top of it.
#: Source: ``tasks/work/fresh-deduction-authorization-3.md`` (2026-09-13).
AUTHORIZED_MODEL_WORK_SECONDS: Final[float] = 6 * 60 * 60
AUTHORIZED_ELAPSED_SECONDS: Final[float] = 8 * 60 * 60

#: How many times the instrument's own client wrapper sends ONE call whose
#: attempt came back with no completion: four attempts, so one send and three
#: retries. The bound is small on purpose. A retry buys no new draw — an attempt
#: that produced nothing is not a sample of anything — so the only thing more
#: attempts buy is a longer wait before the same stop, and a sequential run of
#: one hundred units needs about six hundred consecutive successes, which is the
#: reason the run needs any retry at all.
MAX_TRANSPORT_ATTEMPTS: Final[int] = 4

#: The wall one attempt may hold before this wrapper cuts it off and counts it
#: as an attempt that produced nothing. Sized off the measured per-call band:
#: the first attempt of this evaluation ran at 11.7 s/call and the second at
#: 26.6 s/call, so 180 s is about seven times the slowest call anyone has
#: measured here and a healthy call cannot reach it. The provider client's own
#: budget is the thing being bounded: ``llm/featherless_client.py`` sends six
#: times at a 600 s timeout with backoff, so without this one stalled call can
#: hold the run for the better part of an hour, while four attempts at this
#: bound cost at most 12 minutes of a 6 h window.
PER_ATTEMPT_TIMEOUT_SECONDS: Final[float] = 180.0

#: The first retry waits this long, the second twice that, the third four times.
#: Short on purpose: the failures it backs off from are a stalled or empty
#: endpoint rather than a rate limit the run could wait out, and the run's own
#: wall is the budget being spent.
TRANSPORT_BACKOFF_BASE_SECONDS: Final[float] = 1.0

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


# ---------------------------------------------------------------------------
# The development calibration (tasks/work/fresh-deduction-calibration.md)
# ---------------------------------------------------------------------------
#
# A second, much smaller authorization, approved by the owner on 2026-09-14 and
# recorded in that card: five paired seeds of a CONVERTED band — development
# data, already rendered once — measured for what the provider charges, so the
# ceilings a fourth held-out authorization is sized from come off this endpoint
# rather than off a projection. Everything below is the size of that spend. The
# per-call caps, the temperatures and the transport bound were NOT re-sized for
# it: the calibration measures the run it is sizing, so it had to draw the way
# that run drew.
#
# That calibration has since been spent — once, on 2026-09-14 — and the fourth
# authorization it sized raised the RUN's turn cap from the 2,048 it drew at to
# 4,096. Its own ceilings were authorized against the 9,216-token schedule the
# caps it drew at reserve, so they are frozen here together with those caps
# (CALIBRATION_SAMPLING): the mode reproduces the draw it measured, and the
# committed output remains the arithmetic this tree can re-derive. A calibration
# that sized a run drawing at 4,096 would have to draw at 4,096 and would need
# its own ceilings, which are the owner's on a card and are not written here.

#: Paired seeds the calibration renders: five prefixes, both arms, thirty calls
#: an arm. Small on purpose — the quantity being measured is what one call and
#: one unit cost, and thirty calls of each arm measure that.
CALIBRATION_PAIRED_SEEDS: Final[int] = 5

#: The per-unit ceilings of a calibration unit. The output figure clears the
#: 9,216-token reservation schedule of :data:`CALIBRATION_SAMPLING` with room
#: for a unit that runs long; the input figure is about 2.5x the largest unit
#: the live archives charged.
CALIBRATION_UNIT_MAX_INPUT_TOKENS: Final[int] = 60_000
CALIBRATION_UNIT_MAX_OUTPUT_TOKENS: Final[int] = 12_000

#: The run-level ceilings, ten units at those per-unit figures.
CALIBRATION_RUN_MAX_INPUT_TOKENS: Final[int] = 600_000
CALIBRATION_RUN_MAX_OUTPUT_TOKENS: Final[int] = 120_000

#: One hour of model work inside a ninety-minute elapsed window. Thirty units of
#: six calls is sixty calls; at the slowest pace this evaluation has measured
#: (26.6 s/call) sixty calls are about 27 minutes, so the work window is twice
#: the slowest projection and the elapsed margin covers one stalled attempt.
CALIBRATION_MODEL_WORK_SECONDS: Final[float] = 60 * 60
CALIBRATION_ELAPSED_SECONDS: Final[float] = 1.5 * 60 * 60

CALIBRATION_LIMITS: Final[RunLimits] = RunLimits(
    run_max_input_tokens=CALIBRATION_RUN_MAX_INPUT_TOKENS,
    run_max_output_tokens=CALIBRATION_RUN_MAX_OUTPUT_TOKENS,
    unit_max_input_tokens=CALIBRATION_UNIT_MAX_INPUT_TOKENS,
    unit_max_output_tokens=CALIBRATION_UNIT_MAX_OUTPUT_TOKENS,
    max_cost_usd=AUTHORIZED_MAX_COST_USD,
    elapsed_seconds=CALIBRATION_ELAPSED_SECONDS,
    model_work_seconds=CALIBRATION_MODEL_WORK_SECONDS,
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

#: The draw the development calibration of 2026-09-14 made, frozen at what it
#: made rather than tracking :data:`AUTHORIZED_SAMPLING`. Until the fourth
#: authorization the two were the same object, and the calibration's ceilings
#: were approved on that basis: :data:`CALIBRATION_UNIT_MAX_OUTPUT_TOKENS` of
#: 12,000 pays for the 9,216-token schedule these caps reserve and not for the
#: 15,360 the raised turn cap reserves. Letting the calibration mode follow the
#: run's cap would authorize six calls its own ceilings cannot pay for — the
#: defect :func:`assert_limits_are_feasible` exists to refuse — so the mode
#: keeps the draw it measured, the committed calibration output stays
#: re-derivable from this tree, and a calibration of the raised draw needs its
#: own ceilings on its own card.
CALIBRATION_SAMPLING: Final[SamplingConfig] = SamplingConfig(
    turn_max_tokens=DEFAULT_TURN_MAX_TOKENS,
    turn_temperature=AUTHORIZED_TURN_TEMPERATURE,
    vote_max_tokens=AUTHORIZED_VOTE_MAX_TOKENS,
    vote_temperature=AUTHORIZED_VOTE_TEMPERATURE,
)


# ---------------------------------------------------------------------------
# The SECOND development calibration
# (tasks/work/fresh-deduction-calibration-2.md)
# ---------------------------------------------------------------------------
#
# A third authorization, approved by the owner on 2026-09-15 as decision 7 of
# ``tasks/diagnosis-2026-09-15-truncation-stop.md``, and a SECOND set beside the
# one above rather than a replacement of it. The first mode keeps its own
# sampling, seeds and ceilings, because the output it measured is still the
# arithmetic this tree re-derives; this one is the draw the FIFTH run would
# make.
#
# What makes it a different authorization rather than a bigger version of the
# first: it draws at :data:`AUTHORIZED_SAMPLING` (turn 4,096, not 2,048), so it
# needs ceilings that pay for the 15,360-token schedule that cap reserves; it
# draws sixty paired seeds rather than five, which no single converted record
# holds; and in it a per-call truncation is a MEASUREMENT rather than a stop,
# because a calibration that stops at the first runaway cannot measure the rate
# it was sent to measure. The live run's stop rule is untouched by all three.

#: Paired seeds the second calibration renders: sixty prefixes, both arms, 120
#: units, about 720 model calls. The bar is the owner's decision 7 — at least
#: sixty impostor-authored candidate ballots, a 99.2% chance of seeing a
#: 1-in-13 event — and exposure is about one impostor ballot draw per unit, so
#: sixty candidate units is sixty draws.
CALIBRATION_2_PAIRED_SEEDS: Final[int] = 60

#: The per-unit ceilings of a second-calibration unit. The output figure clears
#: the 15,360-token reservation schedule of :data:`CALIBRATION_2_SAMPLING`; the
#: input figure is about 1.6x the largest unit the fourth run charged (36,743).
CALIBRATION_2_UNIT_MAX_INPUT_TOKENS: Final[int] = 60_000
CALIBRATION_2_UNIT_MAX_OUTPUT_TOKENS: Final[int] = 16_000

#: The run-level ceilings. The fourth run's per-unit means project about 2.87 M
#: input and 276 k output over 120 units, so these are anomaly detectors at
#: roughly 1.6x rather than a budget.
CALIBRATION_2_RUN_MAX_INPUT_TOKENS: Final[int] = 4_500_000
CALIBRATION_2_RUN_MAX_OUTPUT_TOKENS: Final[int] = 450_000

#: Five hours of model work inside a six-hour elapsed window, one sitting. The
#: wall is the binding limit and is stated rather than absorbed: 720 calls in
#: 5 h allows 25.0 s per call, against 17.23 s per attempt pooled and 21.85 s on
#: the candidate arm on 2026-09-14 — a margin of 1.45x pooled and 1.14x at the
#: slowest arm pace this evaluation has measured.
CALIBRATION_2_MODEL_WORK_SECONDS: Final[float] = 5 * 60 * 60
CALIBRATION_2_ELAPSED_SECONDS: Final[float] = 6 * 60 * 60

CALIBRATION_2_LIMITS: Final[RunLimits] = RunLimits(
    run_max_input_tokens=CALIBRATION_2_RUN_MAX_INPUT_TOKENS,
    run_max_output_tokens=CALIBRATION_2_RUN_MAX_OUTPUT_TOKENS,
    unit_max_input_tokens=CALIBRATION_2_UNIT_MAX_INPUT_TOKENS,
    unit_max_output_tokens=CALIBRATION_2_UNIT_MAX_OUTPUT_TOKENS,
    max_cost_usd=AUTHORIZED_MAX_COST_USD,
    elapsed_seconds=CALIBRATION_2_ELAPSED_SECONDS,
    model_work_seconds=CALIBRATION_2_MODEL_WORK_SECONDS,
)

#: The draw the second calibration makes: the RUN's own, to the token and to
#: the temperature. Written as the same object rather than as a copy of its
#: four numbers, because the property being asserted is identity of the draw —
#: what is measured is what the fifth run would do — and a copy is a place for
#: the two to part without anything going red.
CALIBRATION_2_SAMPLING: Final[SamplingConfig] = AUTHORIZED_SAMPLING


# ---------------------------------------------------------------------------
# The THIRD development calibration
# (tasks/work/fresh-deduction-calibration-3.md)
# ---------------------------------------------------------------------------
#
# A fourth authorization, approved by the owner on 2026-09-18 as decision 1 of
# ``tasks/diagnosis-2026-09-18-fifth-run.md``, and a THIRD set beside the two
# above rather than a replacement of either. Both of those record spends that
# have been MADE — the 2026-09-14 sitting and the 2026-09-15 one — so their
# seeds, ceilings, sampling and clauses are history and nothing here edits them.
#
# What makes it a different authorization rather than a re-run of the second:
# the wave of 2026-09-18 moved the prompt bytes on both arms (the v5 accounts
# revision on the candidate, the relevance-aware citation guard on both), so the
# second calibration's token profile is a measurement of a surface this tree no
# longer renders. This mode draws the SAME sixty seeds at the SAME caps, which
# is what makes the two comparable on identical inputs, and it reports the
# authored-ballot DIAGNOSTICS block beside the token profile because the
# question this sitting is sent to answer is whether the three wave cards moved
# the mechanisms the diagnosis names.
#
# What it is NOT: an evaluation. It computes no paired statistic, evaluates no
# decision rule and reports no primary outcome, and the frozen analysis below is
# untouched by it.

#: Paired seeds the third calibration renders: the second calibration's draw to
#: the seed — all fifty accepted seeds of the 3000-3999 record then the first
#: ten of the 5000-5999 one — so the only thing that moved between the two
#: sittings is the wave's prompt bytes.
CALIBRATION_3_PAIRED_SEEDS: Final[int] = 60

#: The per-unit ceilings of a third-calibration unit. The output figure clears
#: the 15,360-token reservation schedule of :data:`CALIBRATION_3_SAMPLING`; the
#: input figure is about 3x the largest unit the second calibration charged
#: (38,440), the headroom being for prompt bytes the wave adds that no
#: calibration has measured.
CALIBRATION_3_UNIT_MAX_INPUT_TOKENS: Final[int] = 116_000
CALIBRATION_3_UNIT_MAX_OUTPUT_TOKENS: Final[int] = 16_000

#: The run-level ceilings. 120 units of the second calibration's largest unit is
#: 4,612,800 input and 505,216 output including the in-flight headroom term, so
#: these carry 1.9% and 2.9% of margin over the floors the gate enforces. A
#: ceiling pinned AT the floor is a stop rule that fires on the first unit larger
#: than any of calibration 2's, which is exactly what the wave is expected to
#: produce.
CALIBRATION_3_RUN_MAX_INPUT_TOKENS: Final[int] = 4_700_000
CALIBRATION_3_RUN_MAX_OUTPUT_TOKENS: Final[int] = 520_000

#: Five hours of model work inside a six-hour elapsed window, one sitting. 720
#: calls in 5 h allows 25.0 s per call, against about 12.9 s on the fifth run's
#: candidate arm (3,897.6 s over 301 calls) and 11.65 s per attempt on
#: calibration 2's candidate arm — a margin of 1.9x at the slowest pace measured
#: on these inputs.
CALIBRATION_3_MODEL_WORK_SECONDS: Final[float] = 5 * 60 * 60
CALIBRATION_3_ELAPSED_SECONDS: Final[float] = 6 * 60 * 60

CALIBRATION_3_LIMITS: Final[RunLimits] = RunLimits(
    run_max_input_tokens=CALIBRATION_3_RUN_MAX_INPUT_TOKENS,
    run_max_output_tokens=CALIBRATION_3_RUN_MAX_OUTPUT_TOKENS,
    unit_max_input_tokens=CALIBRATION_3_UNIT_MAX_INPUT_TOKENS,
    unit_max_output_tokens=CALIBRATION_3_UNIT_MAX_OUTPUT_TOKENS,
    max_cost_usd=AUTHORIZED_MAX_COST_USD,
    elapsed_seconds=CALIBRATION_3_ELAPSED_SECONDS,
    model_work_seconds=CALIBRATION_3_MODEL_WORK_SECONDS,
)

#: The draw the third calibration makes: the RUN's own, as the second's is.
#: Written as the same object for the same reason — what is measured has to be
#: what a run would do, and a copy is a place for the two to part silently.
CALIBRATION_3_SAMPLING: Final[SamplingConfig] = AUTHORIZED_SAMPLING


# ---------------------------------------------------------------------------
# What a unit RESERVES, and what a unit has actually COST
# ---------------------------------------------------------------------------
#
# The two units of account the run of 2026-09-13 was sized in and enforced in
# (``tasks/diagnosis-2026-09-13-live-run-stops.md``). Everything below is
# arithmetic over the constants above and over seven archived live units; none
# of it reads a file, so it can refuse a run before a credential exists.

#: The calls one unit makes, by kind: one opening turn per living speaker and
#: one ballot per living voter. Both are the roster's living count, and
#: :func:`run_unit` refuses a unit that resolved a different number of ballots,
#: so this is the schedule the run follows rather than an estimate of it.
UNIT_TURN_CALLS: Final[int] = AUTHORIZED_LIVING_VOTERS
UNIT_BALLOT_CALLS: Final[int] = AUTHORIZED_LIVING_VOTERS

#: The largest input and output a single unit has been CHARGED, over the 120
#: units the second live development calibration of 2026-09-15 measured (their
#: per-call rows are in ``tests/experiments/deduction_usage_profile.json``,
#: whose ``units`` block a test holds these two numbers to). Both figures are
#: complete six-call units this time, measured at accounts revision v4 on a
#: converted band: the profile the fourth authorization was sized against held
#: the seven units of the three stopped live runs — 24,282 input and 3,116
#: output, the latter a unit that stopped after four of its six calls — and
#: those rows now live beside it in
#: ``tests/experiments/deduction_stopped_runs_usage_profile.json``, where the
#: rehearsals of the archived FAULTS read them. They are what the run-level
#: ceilings are checked against, because a ceiling is an anomaly detector and
#: the largest thing this evaluation has measured is the anomaly's lower edge.
CALIBRATED_UNIT_INPUT_TOKENS: Final[int] = 38_440
CALIBRATED_UNIT_OUTPUT_TOKENS: Final[int] = 4_176

#: The same two figures as the profile committed when the two SPENT CALIBRATION
#: modes were authorized — the three stopped live runs' seven units, now
#: committed as ``tests/experiments/deduction_stopped_runs_usage_profile.json``
#: — and what :func:`assert_calibration_is_authorized` and
#: :func:`assert_ready_for_a_calibration` check THOSE two modes' ceilings
#: against. Carried as each mode's own ``sizing_unit_input_tokens`` field, so a
#: later mode sized on a later profile cannot be checked against this one.
#:
#: A calibration mode's limits are the record of a spend the manifest authorizes
#: ONCE, and both have been spent: the 2026-09-14 mode on that day and the
#: 2026-09-15 mode on the sitting that produced the profile above. Checking
#: their ceilings against a profile measured BY one of them asks whether a
#: sitting that already happened could be authorized under numbers that did not
#: exist when it was authorized, which is not a question this gate exists to
#: answer — and answering it would force a re-sizing of ``CALIBRATION_2_LIMITS``,
#: which is to say a second sitting nobody authorized. The live EVALUATION's
#: ceilings keep reading the constants above, which is where a refreshed
#: measurement belongs. A test holds these two to the committed stopped-runs
#: fixture's own maxima, so they are read off evidence rather than typed.
CALIBRATION_SIZING_UNIT_INPUT_TOKENS: Final[int] = 24_282
CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS: Final[int] = 3_116

#: The profile the 2026-09-18 mode's ceilings were sized against: the largest of
#: the 120 units the second calibration measured on these same sixty seeds, as
#: its committed output publishes them
#: (``audits/deduction-candidate/calibration-2-2026-09-15/calibration.json``,
#: ``proposal.measured_max_unit_*_tokens``; a test reads both off that archive).
#:
#: A FROZEN LITERAL rather than a read of :data:`CALIBRATED_UNIT_INPUT_TOKENS`,
#: which today holds the same two numbers. The refresh
#: ``tasks/work/fresh-deduction-limits-6.md`` makes FROM this sitting moves
#: those two constants to this sitting's own maxima, and a mode whose gate read
#: them would then be checked against the measurement it produced — the
#: circularity :data:`CALIBRATION_SIZING_UNIT_INPUT_TOKENS` above exists to
#: refuse, one authorization later. Against 24,282 this mode's run-level input
#: ceiling passes anything (120 units is 2,913,840); against 38,440 it bites at
#: 4,612,800, which is the margin the Constraints table states.
CALIBRATION_3_SIZING_UNIT_INPUT_TOKENS: Final[int] = 38_440
CALIBRATION_3_SIZING_UNIT_OUTPUT_TOKENS: Final[int] = 4_176


def planned_units() -> int:
    """How many units a whole run is: one per frozen prefix per arm."""

    return PREREGISTERED_BAND.size * len(instrument_arms())


def calibration_units(paired_seeds: int = CALIBRATION_PAIRED_SEEDS) -> int:
    """How many units a calibration is: one per drawn seed per arm.

    Separate from :func:`planned_units` because the two are different runs:
    the feasibility gate checks a run-level ceiling against the units that run
    will make, and a calibration's ten units against the held-out run's hundred
    is the difference between a ceiling that pays for its own run and one that
    does not.
    """

    if paired_seeds < 1:
        raise ValueError(f"a calibration draws at least one seed, got {paired_seeds}")
    return paired_seeds * len(instrument_arms())


def unit_output_reservation(
    *,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
    living_voters: int = AUTHORIZED_LIVING_VOTERS,
) -> int:
    """The output tokens ONE unit reserves before it is billed for anything.

    ``llm/budgeted_client.py`` pre-flights every call against the full per-call
    output cap (``llm/budgeted_client.py:259``), so a unit's six calls reserve
    the whole of both caps whatever the model then writes. This is that
    schedule, and :func:`assert_limits_are_feasible` is what holds a ceiling to
    it.
    """

    if living_voters < 1:
        raise ValueError(f"a unit has at least one living voter, got {living_voters}")
    return living_voters * (sampling.turn_max_tokens + sampling.vote_max_tokens)


RESERVATION_POLICY: Final[str] = (
    "The token ceilings are enforced on RESERVED spend and were sized on "
    "CHARGED spend. Every call is pre-flighted against its full per-call output "
    "cap before it is sent, so one unit reserves "
    f"{UNIT_TURN_CALLS} x {AUTHORIZED_TURN_MAX_TOKENS:,} for its turns and "
    f"{UNIT_BALLOT_CALLS} x {AUTHORIZED_VOTE_MAX_TOKENS:,} for its ballots — "
    f"{unit_output_reservation():,} output tokens — whatever it is then billed. "
    "A per-unit output ceiling below that schedule authorizes six legal calls "
    "it cannot pay for, and refuses one of them by arithmetic rather than by "
    "spend; the instrument therefore refuses such a ceiling before a live run "
    "starts, rather than discovering it partway through one. The run-level "
    "ceilings are the same question one level up, because the pre-flight "
    "recurses into the parent budget, and are checked against the "
    "largest per-unit spend the committed usage profile carries — "
    f"{CALIBRATED_UNIT_INPUT_TOKENS:,} input and "
    f"{CALIBRATED_UNIT_OUTPUT_TOKENS:,} output, the largest of the 120 units "
    "the second live development calibration of 2026-09-15 measured at "
    "accounts revision v4 — rather than against a mean "
    "projection: a hundred units at the largest unit this evaluation has "
    "measured is what a run ceiling has to be able to pay for, because a "
    "ceiling that cannot is a stop rule that fires on arithmetic near the end "
    "of a run it has already paid for. The run-level OUTPUT ceiling carries "
    f"one further {AUTHORIZED_TURN_MAX_TOKENS:,}-token turn cap on top of that "
    "product, because the last call of the run is reserved against the run "
    "budget after the run has charged everything before it; the input "
    "dimension carries no such term, its pre-flight being the prompt's own "
    "estimated length rather than a cap."
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
    "A call that came back with no completion at all — an empty body, a "
    "transport failure, a retryable status, or an attempt that outran the "
    "per-attempt wall each send is bounded by — is retried up to three times, "
    "then a stop carrying the same partial accounting, with every attempt "
    "counted per arm and per unit. Retrying one of those buys no new draw: an "
    "attempt that produced nothing is not a sample. A body that reached its "
    "output cap and a returned payload that failed schema validation ARE "
    "samples and are never retried, and neither is an exhausted budget or "
    "deadline. "
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

TRANSPORT_RETRY: Final[str] = (
    "A call whose attempt came back with no completion at all is sent again by "
    "this instrument's own client wrapper rather than by the provider client, "
    "so no recorded campaign changes behaviour: at most "
    f"{MAX_TRANSPORT_ATTEMPTS} attempts, one send and "
    f"{MAX_TRANSPORT_ATTEMPTS - 1} retries, on any body the authorized client "
    "refuses to record a completion from — no choices, empty assistant "
    "content, or a usage block it cannot read token counts out of — as well as "
    "a transport failure, a retryable HTTP status, or an attempt that outran "
    f"the {PER_ATTEMPT_TIMEOUT_SECONDS:.0f} s per-attempt wall this wrapper "
    "bounds each send by — each retry after a short exponential backoff, and "
    "each attempt still bounded by what is left of the model-work window, "
    "which no retry may outlive. The last failure stops the run with the same "
    "partial accounting every other unit failure reports. Nothing that "
    "produced a completion is retried: a response that reached its output cap, "
    "a returned payload that failed schema validation, an exhausted budget or "
    "deadline and a refused live run are all left exactly as they were. Every "
    "retried attempt is recorded as an unaccounted attempt carrying zero "
    "tokens, which may have been billed for tokens this side cannot see: the "
    "provider client raises instead of returning a completion, and its refusal "
    "carries no usage onto the exception, so no usage rides any of these four "
    "classes and this wrapper has none to charge. A body it refused for the "
    "state of its usage block is no different here: what the adapter read, it "
    "did not pass on. The attempts are counted per arm and per "
    "unit — retried calls, unaccounted attempts and the trigger class of each "
    "— beside the meeting-internal defaults."
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


class CalibrationInputsRejected(InstrumentError):
    """The calibration was pointed at inputs it may not draw, or they moved.

    One class for both because they are one rule: a calibration draws a
    CONVERTED band's record and nothing else, and it draws exactly the prefixes
    that record froze. A held-out record, a band no freeze has converted, a
    record whose status still says ``held_out``, and a seed that rebuilds to a
    different digest are all "these are not the development inputs the owner
    authorized", and each of them is a refusal before any call.
    """


class LiveRunNotAuthorized(InstrumentError):
    """A non-fake provider was reached without an explicit live invocation."""


class LimitsInfeasible(InstrumentError):
    """The authorized limits cannot pay for the run they authorize.

    Not a stop: a refusal BEFORE a run, raised by :func:`assert_limits_are_feasible`
    from arithmetic over module constants alone. A ceiling below the reservation
    schedule the same run will make is a mismatch between the unit the limit was
    sized in and the unit it is enforced in, and it is static — the run of
    2026-09-13 discovered it live, and nothing about discovering it needed a
    provider.
    """


class ResumeNotAuthorized(InstrumentError):
    """A resumed run was asked for where no authorization or state allows one.

    Three different refusals share this class because they are one rule: a
    resume continues a run under the manifest and the sources the stopped one
    ran under. A checkpoint whose digests are not this tree's is a different
    run; a live resume without the owner's resumption clause in the committed
    manifest is an unauthorized one.
    """


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


class TransportAttemptsExhausted(InstrumentError):
    """Every authorized attempt at one call came back with no completion.

    The stop a bounded retry ends in, and the one thing this instrument's
    wrapper retries towards: an empty body, a transport failure, a retryable
    status and an attempt cut off at :data:`PER_ATTEMPT_TIMEOUT_SECONDS` are all
    attempts that produced nothing, and :data:`MAX_TRANSPORT_ATTEMPTS` of them
    in a row is a provider that is not answering rather than a transient. A
    subclass of :class:`InstrumentError` so the run stops with the partial
    accounting every other unit failure reports, and so no outer layer can
    mistake it for another retryable failure and send the call again.
    """


class ProvenanceMismatch(InstrumentError):
    """A unit's recorded identity is not the arm it was run under."""


class PrefixBytesLeaked(InstrumentError):
    """A report payload carries held-out prefix bytes."""


class CalibrationReportsAnOutcome(InstrumentError):
    """A calibration payload carries a paired statistic or a graded outcome."""


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
    #: What the wrapper's bounded retry did, per arm. Defaulted rather than
    #: required so a caller that builds a partial state without one still
    #: reports the same counts it always did; the run path always supplies it.
    attempts_by_arm: Mapping[str, TransportAttempts] = field(default_factory=dict)

    def describe(self) -> str:
        spent = ", ".join(
            f"{arm}: {usage.calls} calls, {usage.input_tokens} in, "
            f"{usage.output_tokens} out"
            for arm, usage in sorted(self.usage_by_arm.items())
        )
        # Only when there were any: a stop that retried nothing should not read
        # as one that retried and got nowhere.
        retried = ", ".join(
            f"{arm}: {attempts.describe()}"
            for arm, attempts in sorted(self.attempts_by_arm.items())
            if attempts.unaccounted_attempts
        )
        return (
            f"{self.reason}; {self.completed_units}/{self.planned_units} units "
            f"completed, {self.elapsed_seconds:.1f}s elapsed, "
            f"{self.model_work_seconds:.1f}s model work; {spent or 'no spend'}"
            + (f"; {retried}" if retried else "")
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

    The relevance rule used to ride ``citation_relevance_version=1``, set on
    BOTH arms so it was never a second treatment. That lever is retired: the
    rule is unconditional and decides a ``grounding_label`` rather than a
    coercion (ruling D6 of 2026-09-19), so neither arm carries the keyword and
    the pair still differs in the accounts channels alone
    (``test_the_arms_differ_only_in_the_account_channels`` is the assertion).
    The fifth run's re-baselining stands as recorded: its reference figures
    were taken on the coercing surface and are not comparable with a later
    run's, and the manifest's dated section of 2026-09-18 says so in full.
    """

    return (
        InstrumentArm(
            name="repaired_clock",
            experiment_config=RecordedExperimentConfig(
                format_version=2,
                evidence_reasoning_version=2,
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


#: The Inputs table's "Seed band" row of the execution manifest, whose first two
#: numbers are the band that document binds. Anchored on the row label rather
#: than on a bare pair of numbers: the same document names the CONVERTED band in
#: prose beside it, and a looser reader would take whichever came first.
_MANIFEST_SEED_BAND_ROW: Final = re.compile(
    r"^\|\s*Seed band\s*\|\s*(\d+)[–-](\d+)\b", re.MULTILINE
)


def manifest_bound_band(manifest_text: str) -> tuple[int, int]:
    """The seed band the execution manifest's Inputs table binds.

    Exactly one "Seed band" row may state one, because the band is what the
    authorization is written against: no row, or two of them, is a document that
    does not say which inputs it authorizes, and that is refused rather than
    resolved by picking one.
    """

    rows = _MANIFEST_SEED_BAND_ROW.findall(manifest_text)
    if len(rows) != 1:
        raise LiveRunNotAuthorized(
            f"{EXECUTION_MANIFEST_PATH} carries {len(rows)} 'Seed band' rows "
            "naming a band; exactly one says which inputs this run is "
            "authorized to spend"
        )
    first, last = rows[0]
    return int(first), int(last)


def assert_manifest_binds_the_live_band(repo_root: Path = _REPO_ROOT) -> None:
    """Refuse a live run whose authorization names a band the runner would not draw.

    :func:`verify_frozen_set` regenerates whatever record sits at
    :data:`~experiments.held_out_prefixes.MANIFEST_PATH` and holds it to the
    generator's own :data:`~experiments.held_out_prefixes.PREREGISTERED_BAND`.
    Neither of those reads this document, so a band that moves — 3000-3999
    became development data on 2026-09-10, 5000-5999 on 2026-09-13, 6000-6999
    on 2026-09-13 as well and 7000-7999 on 2026-09-15, each replaced by a fresh
    freeze — leaves the manifest authorizing one band while the run draws
    another, with every other gate green. That gap is closed here, by comparing
    the band the Inputs row states with the band the live record holds.

    It is part of the authorization, not of the frozen-set check: it runs inside
    :func:`assert_live_run_is_authorized`, which is the first thing
    :func:`assert_ready_for_a_live_run` calls, so a stale binding stops the run
    before a provider, a credential or a connection exists.
    """

    manifest = (repo_root / EXECUTION_MANIFEST_PATH).resolve()
    if not manifest.is_file():
        raise LiveRunNotAuthorized(f"execution manifest is missing: {manifest}")
    bound = manifest_bound_band(manifest.read_text(encoding="utf-8"))
    record_file = repo_root / MANIFEST_PATH
    if not record_file.is_file():
        raise LiveRunNotAuthorized(f"the freeze manifest is missing: {MANIFEST_PATH}")
    record = json.loads(record_file.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or not isinstance(record.get("band"), Mapping):
        raise LiveRunNotAuthorized(
            f"{MANIFEST_PATH} carries no band block; it does not describe the "
            "set this run would draw"
        )
    band = record["band"]
    live = (band.get("first_seed"), band.get("last_seed"))
    if bound != live:
        raise LiveRunNotAuthorized(
            f"{EXECUTION_MANIFEST_PATH} binds seed band {bound[0]}-{bound[1]}, "
            f"but the held-out record at {MANIFEST_PATH} holds "
            f"{live[0]}-{live[1]}: the authorization was written for one band "
            "and this run would spend another"
        )


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

    The last two checks are on the document rather than on the run. The band
    the manifest's Inputs table binds has to be the band the live freeze record
    holds (:func:`assert_manifest_binds_the_live_band`), so an authorization
    written for one band cannot spend another; and the manifest may not carry
    the closing clause of 2026-09-19
    (:func:`assert_the_evaluation_is_not_closed`), which it does since the
    owner closed this evaluation — so on this tree an otherwise perfect
    invocation is refused here, by construction.
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
    # The digest above says WHICH document authorized this run; this says the
    # document authorized THESE inputs. A held-out band that moves under a
    # manifest nobody re-bound passes every check above it.
    assert_manifest_binds_the_live_band(repo_root)
    # And this says the document still authorizes ANY run. Last of the document
    # checks on purpose: only a run that is otherwise authorized — right
    # manifest, right model, right band — reaches the closing refusal, so a
    # misconfigured run is told what is wrong with it instead.
    assert_the_evaluation_is_not_closed(manifest.read_text(encoding="utf-8"))
    # Last here, first in :func:`assert_ready_for_a_live_run`. The checks above
    # say WHICH run this is, and a run whose manifest, model or band is wrong
    # should be told that rather than told its arithmetic; on the CLI's own path
    # the arithmetic is checked before any of this, because it reads nothing.
    assert_limits_are_feasible(limits=limits, sampling=sampling, units=units)


def assert_limits_are_feasible(
    *,
    limits: RunLimits = AUTHORIZED_LIMITS,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
    units: int | None = None,
    calibrated_unit_input_tokens: int | None = None,
    calibrated_unit_output_tokens: int | None = None,
) -> None:
    """Refuse limits a run cannot honour, from arithmetic alone.

    :data:`RESERVATION_POLICY` states the rule; this enforces it. Four
    comparisons, no file and no client:

    * the per-unit OUTPUT ceiling against :func:`unit_output_reservation` — the
      schedule one unit's six pre-flights reserve. The run of 2026-09-13 was
      stopped by this one: 4,000 against 9,216, six legal calls authorized and
      the fifth refused by the reservation arithmetic;
    * the per-unit INPUT ceiling against the largest unit the live archives
      charged, because a ceiling below a unit this evaluation has already run
      refuses a unit it has already seen;
    * both RUN ceilings against that same per-unit figure times the unit count,
      and the OUTPUT one against one further per-call turn cap on top of that
      product. ``GameBudget.preflight`` recurses into its parent
      (``llm/budget.py``), so the RUN budget sees a call's full output cap added
      to everything the run has already charged, exactly as the unit budget
      does; a run ceiling sized at exactly what its units charge therefore
      cannot pay for its own last call. A run ceiling below what its own units
      are authorized to spend stops the run near its end on arithmetic rather
      than on a real overrun, which is the same two-units-of-account defect one
      level up. The INPUT dimension takes no such term: a call's input side is
      pre-flighted at the prompt's own estimated length
      (``llm/budgeted_client.py``'s ``estimate``), not at a cap.

    It runs first in :func:`assert_ready_for_a_live_run` and again inside
    :func:`assert_live_run_is_authorized`, so neither the CLI's path nor a
    direct :func:`run_instrument` call can reach a provider without it. It
    ACCEPTS :data:`AUTHORIZED_LIMITS` since the fifth authorization of
    2026-09-15 re-sized them on the refreshed profile — the fourth
    authorization's 3,710,000 run-level input ceiling is REFUSED on it, a
    hundred units of 38,440 needing 3,844,000 — and it still refuses the
    ceilings merged on 2026-09-07 — 4,000 per-unit output against a schedule of
    :func:`unit_output_reservation`, under either turn cap — which is what
    ``test_the_ceilings_merged_on_2026_09_07_are_still_refused`` plants.

    The two calibrated figures default to the module's constants — the largest
    unit the committed usage profile holds — and are parameters so that a
    caller can run this same gate against a DIFFERENT measurement. Two do:

    * :func:`ceiling_proposal` runs it against the sitting's OWN measured
      maxima, because a proposal sized on what a sitting measured is feasible
      or not against that sitting's numbers, and checking it against a profile
      built from some earlier run's archives answers a question nobody asked;
    * the two calibration gates run it against the matched mode's own
      ``sizing_unit_input_tokens`` and its output twin, the profile THAT mode
      was sized on, because a mode's ceilings record a spend the manifest
      authorizes once. The two spent modes carry
      :data:`CALIBRATION_SIZING_UNIT_INPUT_TOKENS`; the 2026-09-18 mode carries
      :data:`CALIBRATION_3_SIZING_UNIT_INPUT_TOKENS`, the measurement the
      2026-09-15 sitting made on the same sixty seeds.

    Read from module scope at call time rather than bound as parameter
    defaults, so a test that moves either constant moves this gate with it.
    """

    planned = planned_units() if units is None else units
    if planned < 1:
        raise ValueError(f"a run has at least one unit, got {planned}")
    calibrated_input = (
        CALIBRATED_UNIT_INPUT_TOKENS
        if calibrated_unit_input_tokens is None
        else calibrated_unit_input_tokens
    )
    calibrated_output = (
        CALIBRATED_UNIT_OUTPUT_TOKENS
        if calibrated_unit_output_tokens is None
        else calibrated_unit_output_tokens
    )
    reserved = unit_output_reservation(sampling=sampling)
    if limits.unit_max_output_tokens < reserved:
        raise LimitsInfeasible(
            f"the per-unit output ceiling is {limits.unit_max_output_tokens:,} "
            f"tokens and one unit reserves {reserved:,} "
            f"({UNIT_TURN_CALLS} x {sampling.turn_max_tokens:,} + "
            f"{UNIT_BALLOT_CALLS} x {sampling.vote_max_tokens:,}): this run "
            "authorizes calls it cannot pay for, and the budget would refuse "
            "one of them on the reservation rather than on the spend"
        )
    if limits.unit_max_input_tokens < calibrated_input:
        raise LimitsInfeasible(
            f"the per-unit input ceiling is {limits.unit_max_input_tokens:,} "
            "tokens and the largest unit the live archives charged is "
            f"{calibrated_input:,}: this ceiling refuses a unit "
            "this evaluation has already run"
        )
    for dimension, ceiling, calibrated, in_flight in (
        (
            "output",
            limits.run_max_output_tokens,
            calibrated_output,
            sampling.turn_max_tokens,
        ),
        ("input", limits.run_max_input_tokens, calibrated_input, 0),
    ):
        needed = calibrated * planned + in_flight
        if ceiling < needed:
            reserved_here = (
                f", plus the {in_flight:,} its last call reserves against the "
                "run budget on top of them,"
                if in_flight
                else ""
            )
            raise LimitsInfeasible(
                f"the run-level {dimension} ceiling is {ceiling:,} tokens and "
                f"{planned} units at the largest unit the live archives "
                f"charged ({calibrated:,}){reserved_here} need {needed:,}: a "
                "run this long would stop on the run ceiling rather than on "
                "its own evidence"
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


#: The owner's resumption clause, approved on 2026-09-14
#: (``tasks/work/fresh-deduction-calibration.md``) and quoted verbatim by the
#: execution manifest's dated "Resumption clause (2026-09-14)" section. Held
#: here as the thing the gate looks for rather than as a paraphrase, and held to
#: the manifest byte for byte by a test, so the code's account of what the owner
#: authorized and the document's cannot drift apart.
#:
#: What the code enforces of it, and where: the checkpoint a stop leaves behind
#: carries the interrupted unit's spend and model-work seconds
#: (:class:`AbandonedSpend`, written on the stop path) and the next sitting
#: charges them before its first call, so "with the interrupted unit's spend and
#: model-work time carried" is arithmetic rather than a promise. That write is
#: reached by every stop that unwinds this process, interrupts included
#: (``run_instrument`` catches ``BaseException`` for the accounting and re-raises
#: an interrupt unchanged). It is NOT reached by a stop that runs no code at
#: all — a SIGKILL, an OOM kill, a power loss — which leaves the last checkpoint
#: at the previous pair boundary and carries that pair's spend nowhere; the
#: runner reads the abandoned sitting's output directory before resuming from a
#: stop of that class, and the manifest's dated section says so. The once-per-
#: stop bound and the final-stop list are the runner's too, not this module's: a
#: checkpoint records no stop class, so a resume cannot be refused on one, and
#: the run's record states which stop each sitting followed.
RESUMPTION_CLAUSE: Final[str] = (
    "A run stopped by transport exhaustion, a credential failure or a process "
    "crash may be resumed once per stop, from its last checkpoint and under "
    "this manifest, with the interrupted unit's spend and model-work time "
    "carried into the next sitting; a stop by a limit, a truncation, a digest "
    "or provenance mismatch, or the legacy body handle is final."
)

#: The owner's calibration clause, approved in the same session and quoted
#: verbatim by the manifest's dated "Development calibration (2026-09-14)"
#: section. The same shape as the clause above and for the same reason: the
#: manifest authorizes the spend, so the gate reads the manifest rather than a
#: flag, and a document that merely describes a calibration does not authorize
#: one.
CALIBRATION_CLAUSE: Final[str] = (
    "A development calibration may spend on the first five accepted seeds of a "
    "converted band, both arms, once and under the calibration limits; it "
    "grades nothing, reads no held-out prefix, and writes aggregates only."
)

#: The owner's SECOND calibration clause, approved on 2026-09-15 with the rest
#: of the diagnosis's section-6 decisions and quoted verbatim by the manifest's
#: dated "Development calibration 2 (2026-09-15)" section. A second clause
#: rather than an edited first one: the first calibration has been spent, its
#: clause is what authorized that spend, and a document that rewrote it would
#: describe a spend nobody made.
CALIBRATION_2_CLAUSE: Final[str] = (
    "A second development calibration may spend on the first sixty accepted "
    "seeds of the converted bands, taken in the order those bands were "
    "converted, both arms, once and under the calibration-2 limits; it grades "
    "nothing, reads no held-out prefix, counts a per-call truncation as a "
    "measurement rather than a stop, and writes aggregates only."
)

#: The owner's THIRD calibration clause, approved on 2026-09-18 with the rest of
#: that diagnosis's section-11 rulings and quoted verbatim by the manifest's
#: dated "Development calibration 3 (2026-09-18)" section. A third clause rather
#: than an edited second one, for the reason the second gives about the first:
#: both earlier sittings have been spent, and their clauses are what authorized
#: those spends.
CALIBRATION_3_CLAUSE: Final[str] = (
    "A third development calibration may spend on the first sixty accepted "
    "seeds of the converted bands, taken in the order those bands were "
    "converted, both arms, once and under the calibration-3 limits, with the "
    "revision of 2026-09-18 enabled on both arms; it grades nothing, reads no "
    "held-out prefix, counts a per-call truncation as a measurement rather than "
    "a stop, reports the authored-ballot diagnostics beside the token profile, "
    "and computes no paired statistic, evaluates no decision rule and reports "
    "no primary outcome."
)

#: The owner's CLOSING clause, accepted on 2026-09-19 with decisions D1, D2 and
#: D8 of ``tasks/direction-2026-09-19-process-over-outcome.md`` and quoted
#: verbatim by the execution manifest's dated closing section. The same shape as
#: the four clauses above, and the same idiom for the opposite reason: those
#: sentences are what a gate looks for before it lets a spend through, and this
#: one is what both gates look for before they REFUSE. A closed evaluation whose
#: closure lived in a variable could be reopened by an edit nobody reads; living
#: in the committed document, reopening it means deleting the owner's sentence
#: from the record that carries it, which is a visible act.
#:
#: What it does NOT do: withdraw, re-score or restate a result. The five runs
#: and three calibrations keep every figure they recorded and every meaning
#: those figures had; what stops is the gating, not the record.
CLOSURE_CLAUSE: Final[str] = (
    "The accuracy-gated fresh-model deduction evaluation is closed as of "
    "2026-09-19: its preregistered primary outcome, decision rule and "
    "wrongful-ejection bound stay the record of what was measured and are no "
    "longer the project's gate, no further live run or calibration under this "
    "manifest is authorized, and the held-out records this evaluation drew are "
    "an archive rather than inputs."
)


def assert_the_evaluation_is_not_closed(manifest_text: str) -> None:
    """Refuse any live spend while the execution manifest carries the closure.

    The document is the authorization, so the document is also the closure: a
    run or a calibration reaching this point has satisfied every other check,
    and what stops it is the owner's own sentence in the record it is
    authorized against. Reopening the evaluation therefore means deleting that
    sentence from the manifest under a card that says why, not passing a flag.

    Placed LAST among the document checks on both paths, so a run whose
    manifest, model, band or mode is wrong is told that instead: "this
    evaluation is closed" is the answer for an otherwise authorized run, and a
    misconfigured one deserves the misconfiguration's message.
    """

    if CLOSURE_CLAUSE in manifest_text:
        raise LiveRunNotAuthorized(
            f"{EXECUTION_MANIFEST_PATH} carries the closing clause of "
            "2026-09-19: the owner closed this evaluation that day (decisions "
            "D1, D2 and D8 of "
            "tasks/direction-2026-09-19-process-over-outcome.md), so no live "
            "run and no calibration under this manifest is authorized. The "
            "results it recorded stand; the gate does not. Reopening it means "
            "removing that clause from the manifest under a card that says why."
        )


@dataclass(frozen=True)
class CalibrationPrediction:
    """One directional reading the 2026-09-18 sitting is read against.

    Held here so the card's table, the manifest's dated section and this module
    cannot drift: a test holds all three to these six rows. They are fixed
    BEFORE the sitting for the only reason a prediction is worth writing down —
    a reading chosen after the numbers are in is a description of them.
    """

    #: ``P1`` to ``P6``, as the card and the manifest number them.
    id: str
    #: The mechanism the wave was supposed to move, with its memo section.
    mechanism: str
    #: What the fifth run measured, on DIFFERENT prefixes.
    fifth_run: str
    #: The direction this sitting is read for. Never a threshold.
    prediction: str


#: The six predictions, verbatim from the card's Evidence table and copied
#: verbatim into the manifest's dated section. Read from memo section 7 against
#: the fifth run's own figures, which were measured on the 8000-8999 prefixes
#: rather than on this draw's — so every one of them is a DIRECTION and none of
#: them is a threshold this sitting can pass or fail.
CALIBRATION_3_PREDICTIONS: Final[tuple[CalibrationPrediction, ...]] = (
    CalibrationPrediction(
        id="P1",
        mechanism="F6 costs the impostor its free pass (§3)",
        fifth_run="impostor EJECTs survive 86.8%, crew 51.9%",
        prediction="the gap narrows",
    ),
    CalibrationPrediction(
        id="P2",
        mechanism="F6 attacks stage 2 (§2)",
        fifth_run="wrongful coalitions convert 36.4%, correct 18.2%",
        prediction="wrongful falls to or below correct",
    ),
    CalibrationPrediction(
        id="P3",
        mechanism="F7 equalises the register (§4)",
        fifth_run="candidate authors 119 EJECT / 31 SKIP of 150",
        prediction="authored EJECTs fall toward 14",
    ),
    CalibrationPrediction(
        id="P4",
        mechanism="F4 revives the turn channel (§3)",
        fifth_run="0 of 150 keep a `primary_reason_id`; 27 nulled; 44 coerced",
        prediction="surviving ids rise, coercions fall",
    ),
    CalibrationPrediction(
        id="P5",
        mechanism="The deduction signal is real (§5)",
        fifth_run="crew authored EJECTs name the impostor 51 of 81",
        prediction="holds near 63% once volume falls",
    ),
    CalibrationPrediction(
        id="P6",
        mechanism="The vocabulary un-collapses (§4)",
        fifth_run="1 contradiction flag against 14",
        prediction="flags rise above 1",
    ),
)

#: What the six rows above are and are not. Quoted by the manifest's dated
#: section beside the table, because a table of predictions published without
#: this sentence reads as a table of bars.
CALIBRATION_3_PREDICTIONS_NOTE: Final[str] = (
    "These six are PREDICTIONS and none of them is a gate. They are read "
    "against the fifth run's figures, which were measured on different "
    "prefixes, so each is a direction rather than a threshold: a miss is "
    "neither a stop nor a verdict, and no decision rule reads any of them."
)


@dataclass(frozen=True)
class CalibrationMode:
    """One authorized calibration, as the whole set of values it was approved as.

    The reason this is a value object and not nine module constants read
    independently: the three modes differ on every axis at once — seeds, limits,
    sampling, clause, the profile their ceilings were sized against and what a
    truncation means — and each set was approved as a set. Constants read
    independently authorize the crossings nobody approved, which is exactly how
    a sixty-seed draw could end up running under ceilings sized for ten units.
    """

    #: The dated name, which is also the manifest heading and the CLI value.
    name: str
    paired_seeds: int
    limits: RunLimits
    sampling: SamplingConfig
    clause: str
    #: Whether a per-call truncation is a measurement in this mode. False on the
    #: first, and on every live evaluation: see :data:`STOP_RULE`, which this
    #: flag does not edit and does not reach.
    truncation_is_a_measurement: bool
    #: The largest unit this mode's ceilings were SIZED against, which is what
    #: :func:`assert_limits_are_feasible` checks them by. A field of the mode
    #: rather than one module constant for all of them, because a mode's
    #: ceilings record a spend the manifest authorizes once and the profile that
    #: spend was approved under is a property of that approval: the two spent
    #: modes were sized on the three stopped runs' archives
    #: (:data:`CALIBRATION_SIZING_UNIT_INPUT_TOKENS`) and the 2026-09-18 mode on
    #: what the 2026-09-15 sitting then measured.
    sizing_unit_input_tokens: int
    sizing_unit_output_tokens: int
    #: Whether the report carries the per-role call schedules and the leak
    #: column. Stated rather than inferred from
    #: ``truncation_is_a_measurement``: the two happen to agree on all three
    #: modes, and a report SHAPE decided by a stop-discipline flag is a coupling
    #: that survives only until a mode disagrees with it.
    reports_the_role_split: bool
    #: Whether the report carries the authored-ballot DIAGNOSTICS block. False
    #: on both spent modes, whose committed outputs were written without it and
    #: have to keep re-deriving the same bytes.
    reports_authored_diagnostics: bool

    def describe(self) -> str:
        return (
            f"{self.name}: {self.paired_seeds} paired seeds, that mode's "
            f"calibration limits, turn {self.sampling.turn_max_tokens:,} / vote "
            f"{self.sampling.vote_max_tokens:,}"
        )


#: Every calibration the owner has authorized, oldest first. A closed table, so
#: "exactly one of these, whole" is a lookup rather than a chain of ifs.
CALIBRATION_MODES: Final[tuple[CalibrationMode, ...]] = (
    CalibrationMode(
        name="2026-09-14",
        paired_seeds=CALIBRATION_PAIRED_SEEDS,
        limits=CALIBRATION_LIMITS,
        sampling=CALIBRATION_SAMPLING,
        clause=CALIBRATION_CLAUSE,
        truncation_is_a_measurement=False,
        sizing_unit_input_tokens=CALIBRATION_SIZING_UNIT_INPUT_TOKENS,
        sizing_unit_output_tokens=CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS,
        reports_the_role_split=False,
        reports_authored_diagnostics=False,
    ),
    CalibrationMode(
        name="2026-09-15",
        paired_seeds=CALIBRATION_2_PAIRED_SEEDS,
        limits=CALIBRATION_2_LIMITS,
        sampling=CALIBRATION_2_SAMPLING,
        clause=CALIBRATION_2_CLAUSE,
        truncation_is_a_measurement=True,
        sizing_unit_input_tokens=CALIBRATION_SIZING_UNIT_INPUT_TOKENS,
        sizing_unit_output_tokens=CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS,
        reports_the_role_split=True,
        reports_authored_diagnostics=False,
    ),
    CalibrationMode(
        name="2026-09-18",
        paired_seeds=CALIBRATION_3_PAIRED_SEEDS,
        limits=CALIBRATION_3_LIMITS,
        sampling=CALIBRATION_3_SAMPLING,
        clause=CALIBRATION_3_CLAUSE,
        truncation_is_a_measurement=True,
        sizing_unit_input_tokens=CALIBRATION_3_SIZING_UNIT_INPUT_TOKENS,
        sizing_unit_output_tokens=CALIBRATION_3_SIZING_UNIT_OUTPUT_TOKENS,
        reports_the_role_split=True,
        reports_authored_diagnostics=True,
    ),
)


def _names_the_modes_with(field: str, value: object) -> str:
    """Which authorized modes carry ``value`` in ``field``, in words."""

    owners = [mode.name for mode in CALIBRATION_MODES if getattr(mode, field) == value]
    if not owners:
        return "no authorized calibration mode's"
    return " and ".join(f"the {name} mode's" for name in owners)


def calibration_mode_for(
    *,
    limits: RunLimits,
    sampling: SamplingConfig,
    paired_seeds: int,
) -> CalibrationMode:
    """The ONE authorized mode these three values are, or a refusal naming the cross.

    Arithmetic over :data:`CALIBRATION_MODES`: no file is read and no provider
    exists, so it runs first in :func:`assert_calibration_is_authorized` and on
    the rehearsal path too. A set that matches no mode on all three fields is
    refused with the fields named one by one, because "these limits are not the
    ones the owner authorized" says nothing about WHICH of the two the caller
    half-reached.
    """

    for mode in CALIBRATION_MODES:
        if (mode.limits, mode.sampling, mode.paired_seeds) == (
            limits,
            sampling,
            paired_seeds,
        ):
            return mode
    raise LiveRunNotAuthorized(
        "a calibration runs exactly one authorized mode whole, and these "
        "values cross them: the limits are "
        f"{_names_the_modes_with('limits', limits)}, the sampling is "
        f"{_names_the_modes_with('sampling', sampling)}, and {paired_seeds} "
        f"paired seeds is {_names_the_modes_with('paired_seeds', paired_seeds)}. "
        "The authorized modes are "
        + "; ".join(mode.describe() for mode in CALIBRATION_MODES)
        + ". Each mode's calibration limits, sampling and paired seeds were "
        "approved as one set, so a value taken from the other mode is not a "
        "smaller spend but a different one."
    )


def arm_lever_profile(arm: InstrumentArm) -> Mapping[str, str]:
    """The SUBSTRATE levers one arm resolves, without the transport key.

    One reader, for the calibration report that publishes what each arm
    actually resolved. It had a second caller, the pre-flight that refused a
    sitting of the 2026-09-18 mode while either arm resolved the relevance
    revision OFF; ruling D6 of 2026-09-19 retired that lever into the default,
    so the question has no answer any more and the gate went with it -- a check
    whose plant cannot be constructed is not a check. The provider is dropped
    because it is transport rather than substrate and the report names it once
    at the top level; the value passed in is therefore immaterial.
    """

    resolved = dict(arm.environment(provider=AUTHORIZED_PROVIDER))
    resolved.pop("AILIBI_LLM_PROVIDER", None)
    return MappingProxyType(dict(sorted(resolved.items())))


def assert_resume_is_authorized(*, provider: str, repo_root: Path = _REPO_ROOT) -> None:
    """Refuse a LIVE resume until the manifest carries the owner's clause.

    The mechanism exists and the fake-provider rehearsal uses it; spending a
    held-out band on a second sitting is a different question, and it is the
    owner's. ``fake`` passes untouched, because a rehearsal that could not
    resume could not prove the resume.
    """

    if provider == "fake":
        return
    manifest = (repo_root / EXECUTION_MANIFEST_PATH).resolve()
    if not manifest.is_file():
        raise ResumeNotAuthorized(f"execution manifest is missing: {manifest}")
    if RESUMPTION_CLAUSE not in manifest.read_text(encoding="utf-8"):
        raise ResumeNotAuthorized(
            f"{EXECUTION_MANIFEST_PATH} carries no resumption clause, so a live "
            "run may not be continued from a checkpoint: the mechanism is "
            "built and rehearsed offline, and authorizing a second sitting on "
            "the held-out set is the owner's decision, not this runner's"
        )


def assert_calibration_is_authorized(
    *,
    provider: str,
    invocation: LiveRunInvocation | None,
    limits: RunLimits = CALIBRATION_LIMITS,
    sampling: SamplingConfig = CALIBRATION_SAMPLING,
    paired_seeds: int = CALIBRATION_PAIRED_SEEDS,
    repo_root: Path = _REPO_ROOT,
) -> CalibrationMode:
    """Refuse a calibration that is not one the owner authorized, or name it.

    The live-run gate's sibling, not a relaxation of it: the two authorize
    different spends, so they check different limits, different inputs and a
    different clause, and neither passes the other's run.

    * the three values that size the spend — the limits, the sampling
      configuration and the seed count — have to be ONE authorized mode of
      :data:`CALIBRATION_MODES`, whole. Three modes are authorized: the
      five-seed calibration of 2026-09-14 at :data:`CALIBRATION_SAMPLING`, the
      sixty-seed calibration of 2026-09-15 at :data:`CALIBRATION_2_SAMPLING`,
      and the sixty-seed calibration of 2026-09-18 at
      :data:`CALIBRATION_3_SAMPLING` under its own, larger ceilings. Every
      crossing of them is refused by :func:`calibration_mode_for` — sixty seeds
      under the first mode's ceilings is a run its per-unit output figure
      cannot pay for, five seeds under the second's is a spend nobody approved,
      the 2026-09-15 draw under the 2026-09-18 ceilings is a bigger spend than
      the one that was authorized for it, and any mode drawing at another's
      caps measures a distribution the run it sizes does not draw from. That
      last refusal is the one the fourth authorization created: it raised the
      RUN's turn cap to 4,096, so a calibration sizing that run has to draw at
      4,096 under ceilings that clear its 15,360-token schedule, which is what
      the second and third modes are;
    * ``fake`` passes without an invocation, and refuses one, exactly as
      :func:`assert_live_run_is_authorized` does — a rehearsal is not a run.
      The mode lookup above still runs for it, so a rehearsal of a crossing is
      refused where a runner would be refused rather than quietly rehearsing a
      shape no live sitting could take;
    * the manifest has to carry the matched mode's own clause. That is the
      authorization itself, the way the resumption clause is: this gate reads
      the committed document rather than a flag, and each mode's clause
      authorizes only that mode's spend;
    * and it must NOT carry the closing clause of 2026-09-19
      (:func:`assert_the_evaluation_is_not_closed`). It does since the owner
      closed this evaluation, so every mode above is refused here on this tree
      however well-formed the invocation is.

    :func:`assert_manifest_binds_the_live_band` is deliberately NOT applied. It
    binds the Inputs table's band to the held-out record, and a calibration
    draws neither — its inputs are a converted band's record, checked by
    :func:`verify_calibration_draw` against :data:`CONVERTED_BANDS`.

    Returns the matched mode, because the caller needs it: it is what says
    whether a truncation is a measurement in this sitting and whether the
    report carries the role split. Returning it rather than having
    :func:`run_calibration` look it up a second time keeps one answer to
    "which spend is this".
    """

    mode = calibration_mode_for(
        limits=limits, sampling=sampling, paired_seeds=paired_seeds
    )
    if provider == "fake":
        if invocation is not None:
            raise LiveRunNotAuthorized(
                "a fake-provider calibration takes no live invocation; the "
                "rehearsal is the mechanics check and never the authorized run"
            )
        return mode
    if invocation is None:
        raise LiveRunNotAuthorized(
            f"provider {provider!r} is a live provider and this calibration "
            f"carries no LiveRunInvocation naming {EXECUTION_MANIFEST_PATH}. "
            "The manifest authorizes limits; only an explicit runner invocation "
            "authorizes a call."
        )
    if invocation.provider != provider:
        raise LiveRunNotAuthorized(
            f"the live invocation names provider {invocation.provider!r} but the "
            f"calibration asks for {provider!r}"
        )
    if provider != AUTHORIZED_PROVIDER:
        raise LiveRunNotAuthorized(
            f"provider {provider!r} is not the authorized provider "
            f"{AUTHORIZED_PROVIDER!r}; a different provider needs its own "
            "authorization and its own manifest"
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
    text = manifest.read_text(encoding="utf-8")
    committed = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if invocation.manifest_sha256 != committed:
        raise LiveRunNotAuthorized(
            "the live invocation's manifest digest is not the committed "
            f"manifest's: invocation {invocation.manifest_sha256}, file "
            f"{committed}"
        )
    if mode.clause not in text:
        raise LiveRunNotAuthorized(
            f"{EXECUTION_MANIFEST_PATH} carries no calibration clause for the "
            f"{mode.name} mode, so no live calibration is authorized: the mode "
            "is built and rehearsed offline, and spending on development "
            "inputs is recorded in the manifest or it is not authorized"
        )
    # A mode's clause authorizes that spend; the closing clause withdraws the
    # authorization from all of them at once. Checked after the mode's own, so
    # a sitting asking for a mode this document never carried is told that
    # rather than told the evaluation is closed.
    assert_the_evaluation_is_not_closed(text)
    assert_limits_are_feasible(
        limits=limits,
        sampling=sampling,
        units=calibration_units(paired_seeds),
        # A mode's ceilings are checked against the profile THAT MODE was SIZED
        # on, not against whatever a later sitting refreshed the committed one
        # to: see :data:`CALIBRATION_SIZING_UNIT_INPUT_TOKENS`.
        calibrated_unit_input_tokens=mode.sizing_unit_input_tokens,
        calibrated_unit_output_tokens=mode.sizing_unit_output_tokens,
    )
    return mode


def assert_ready_for_a_live_run(
    *,
    provider: str,
    invocation: LiveRunInvocation,
    units: int | None = None,
    limits: RunLimits = AUTHORIZED_LIMITS,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
    repo_root: Path = _REPO_ROOT,
    resuming: bool = False,
) -> FrozenSet:
    """Everything that must hold BEFORE a live client exists, in order.

    Feasibility first — it is arithmetic over module constants, reads nothing
    and needs nothing, so limits that cannot pay for their own run are refused
    before a path is resolved. Then the authorization gate, then the frozen
    held-out set, and only then may a caller build a client — which is why this
    returns the verified :class:`FrozenSet` and :func:`build_authorized_client`
    takes one. A client is a credential and a connection; a run that must stop
    should stop before one is made, and a moved held-out set is exactly such a
    stop.

    ``FrozenSet`` and :func:`verify_frozen_set` are defined further down this
    module; the annotations are lazy (``from __future__ import annotations``) and
    the call happens at run time, so the ordering of the definitions is a reading
    convenience rather than a constraint.
    """

    assert_limits_are_feasible(limits=limits, sampling=sampling, units=units)
    if resuming:
        assert_resume_is_authorized(provider=provider, repo_root=repo_root)
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
    frozen: FrozenSet | CalibrationSet | CalibrationDraw,
    env: Mapping[str, str] | None = None,
) -> LLMClient:
    """Construct the ONE client a live run may use, from the pinned environment.

    ``env`` defaults to the process environment, from which
    :func:`authorized_client_environment` keeps only the credential.

    ``frozen`` is evidence rather than an input: it is unused below, and it is
    required so that no client can be constructed before the inputs have been
    verified. The only producer of a :class:`FrozenSet` is
    :func:`verify_frozen_set`, the only producer of a :class:`CalibrationSet`
    is :func:`verify_calibration_set` and the only producer of a
    :class:`CalibrationDraw` is :func:`verify_calibration_draw`, so "the inputs
    are checked before a provider exists" is a property of this signature
    instead of an ordering a later edit to :func:`main` could quietly reverse.
    All three types are accepted and none can stand in for another anywhere
    else: which one a caller holds is what decides which records it verified.

    :func:`verify_archived_set` is not a fourth producer. It returns an
    :class:`ArchivedSet` — a sibling of :class:`FrozenSet`, not a subclass — so
    the archive of a band that has already been rendered to a model is not
    evidence here, and a caller holding one has verified nothing a live run may
    spend. The annotation refuses it under mypy and the check below refuses it
    at run time, because a type alone would be enforced only where the type
    checker runs.
    """

    if not isinstance(frozen, FrozenSet | CalibrationSet | CalibrationDraw):
        raise LiveRunNotAuthorized(
            "a live client is built only from inputs a live reader verified, "
            f"and {type(frozen).__name__} is not one of those records: the "
            "FrozenSet verify_frozen_set returns, the CalibrationSet "
            "verify_calibration_set returns and the CalibrationDraw "
            "verify_calibration_draw returns are the three. An ArchivedSet is "
            "the record of a band a run has already spent: the offline "
            "rehearsal draws it, and nothing that reaches a provider may."
        )
    del frozen  # see the docstring: proof of ordering, not an input

    from llm.provider import build_default_client

    ambient = dict(os.environ) if env is None else dict(env)
    return build_default_client(env=authorized_client_environment(ambient))


# ---------------------------------------------------------------------------
# The client wrapper: per-call caps, prompt capture, model-work clock
# ---------------------------------------------------------------------------


#: What one attempt in the client's ledger DID, as the ledger's own row says.
#: Four values because :meth:`_InstrumentClient._record` has four callers and
#: they mean four different things: a completion that came back, one the
#: provider billed for and then refused on its own schema validation, an attempt
#: that produced nothing at all, and an attempt the model-work window cut off.
#: Only the first two are samples of what a call costs — the other two carry
#: zero tokens because zero is what is KNOWN, not what was spent — so a summary
#: that averaged all four would report a cheaper call than the provider serves.
CallDisposition = Literal["resolved", "billed_and_refused", "unaccounted", "aborted"]


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
    #: Defaulted so a row built without one reads as an ordinary completion,
    #: which is what every caller that predates this field recorded.
    disposition: CallDisposition = "resolved"
    #: The provider's own word for why generation stopped, as the response or
    #: the parse-failure metadata reported it. ``None`` on the two dispositions
    #: that carry no completion, and ``None`` from any adapter that maps no
    #: such reading: a missing reading is recorded as missing rather than
    #: guessed. Defaulted for the same reason ``disposition`` is.
    finish_reason: str | None = None


#: The provider's own word for a completion cut off at its output cap, as the
#: OpenAI-compatible endpoints this run is authorized against report it
#: (``choices[0].finish_reason``). Every other value — and an absent reading —
#: is not a truncation.
TRUNCATION_FINISH_REASON: Final[str] = "length"


def _truncation_signals(
    *, finish_reason: str | None, output_tokens: int, max_tokens: int
) -> tuple[bool, bool]:
    """The two independent readings of "this completion was cut off".

    ``observed`` is the provider's own ``finish_reason``; ``inferred`` is the
    counter comparison this instrument has made since it was written. Returned
    as a pair rather than as one verdict because both callers need both: the
    stop fires on EITHER, and a call whose two signals disagree is counted
    whichever way it fell, because preferring one of them silently is how the
    fourth run stopped on a truncation nobody observed.
    """

    observed = finish_reason == TRUNCATION_FINISH_REASON
    inferred = output_tokens >= max_tokens
    return observed, inferred


def _cap_signals_disagree(call: CapturedCall) -> bool:
    """Whether one ledger row's two truncation signals contradict each other.

    A null observation is NOT a disagreement: an absent reading contradicts
    nothing, so a row from an adapter that maps no ``finish_reason`` — and the
    two dispositions that carry no completion at all — never counts.

    Read off the recorded row rather than tallied at the stop, so the count is
    a property of the ledger the report summarises and one definition serves
    the stop and the count alike. A row that stopped the run for another reason
    (an identity mismatch, say) still counts here if its two signals disagreed,
    which is the honest reading: the disagreement happened.
    """

    if call.finish_reason is None:
        return False
    observed, inferred = _truncation_signals(
        finish_reason=call.finish_reason,
        output_tokens=call.output_tokens,
        max_tokens=call.max_tokens,
    )
    return observed != inferred


#: The key an ABSENT ``finish_reason`` is counted under, so "the provider
#: reported nothing" is a row of the distribution rather than a hole in it. The
#: same word :func:`_role_split_rows` already keys a null reading under.
NULL_FINISH_REASON: Final[str] = "null"


def _finish_reason_key(call: CapturedCall) -> str:
    """The distribution key one ledger row's ``finish_reason`` counts under."""

    return NULL_FINISH_REASON if call.finish_reason is None else call.finish_reason


def _summed_finish_reasons(
    left: Mapping[str, int], right: Mapping[str, int]
) -> Mapping[str, int]:
    """Two distributions of the same arm, summed and sorted.

    Sorted and rebuilt as a plain ``dict`` so two tallies that saw the same
    readings in a different order compare equal — which ``abandoned_spend``
    depends on, testing a summed row against a default-constructed one.
    """

    counts: Counter[str] = Counter(left)
    counts.update(right)
    return dict(sorted(counts.items()))


@dataclass(frozen=True)
class ArmUsage:
    """One arm's spend, kept separate so the arms' asymmetry stays visible.

    ``cap_signal_disagreements`` is not spend; it rides here because this is
    the tally that walks the captured rows, and the count is derived from them
    (:func:`_cap_signals_disagree`) rather than accumulated separately.
    ``finish_reasons`` rides here for the same reason and answers what that one
    aggregate cannot: what the provider actually said, per call.

    The default distribution is EMPTY and must stay comparable across
    instances: :func:`abandoned_spend` decides whether an arm spent anything at
    all by testing ``spend == ArmUsage()``, so a default that did not compare
    equal — or a :meth:`plus` over no calls that seeded a key — would write an
    abandoned row for an arm that made no call.
    """

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    model_work_seconds: float = 0.0
    cap_signal_disagreements: int = 0
    finish_reasons: Mapping[str, int] = field(default_factory=dict)

    def plus(self, calls: Sequence[CapturedCall]) -> ArmUsage:
        return ArmUsage(
            calls=self.calls + len(calls),
            input_tokens=self.input_tokens + sum(c.input_tokens for c in calls),
            output_tokens=self.output_tokens + sum(c.output_tokens for c in calls),
            cost_usd=self.cost_usd + sum(c.cost_usd for c in calls),
            model_work_seconds=self.model_work_seconds + sum(c.seconds for c in calls),
            cap_signal_disagreements=(
                self.cap_signal_disagreements
                + sum(1 for c in calls if _cap_signals_disagree(c))
            ),
            finish_reasons=_summed_finish_reasons(
                self.finish_reasons, Counter(_finish_reason_key(c) for c in calls)
            ),
        )

    def merged(self, other: ArmUsage) -> ArmUsage:
        """Two tallies of the SAME arm, summed.

        What a resumed run needs and :meth:`plus` cannot give it: a sitting
        carries totals forward, not the calls they came from, because the calls
        themselves are gone with the process that made them.
        """

        return ArmUsage(
            calls=self.calls + other.calls,
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
            model_work_seconds=self.model_work_seconds + other.model_work_seconds,
            cap_signal_disagreements=(
                self.cap_signal_disagreements + other.cap_signal_disagreements
            ),
            finish_reasons=_summed_finish_reasons(
                self.finish_reasons, other.finish_reasons
            ),
        )


#: The four failure classes this wrapper retries, all of them ways for an
#: attempt to produce no completion at all. Written as a closed set so the
#: report's counts name what was retried rather than "something failed".
TransportTrigger = Literal[
    "empty_completion", "transport_error", "retryable_status", "attempt_timeout"
]


@dataclass(frozen=True)
class TransportAttempts:
    """One unit's bounded-retry counts: what was sent again, and why.

    Three numbers, because they answer three different questions. How many
    CALLS needed more than one send is the provider's reliability over this
    unit; how many ATTEMPTS bought nothing is what the run spent on them, and
    the wall of each is on the model-work clock and in the call ledger with a
    marker for a model; and the TRIGGER of each says whether the endpoint
    returned an empty body, dropped the connection, answered with a retryable
    status or simply stopped answering.

    Counts, not a stop, up to :data:`MAX_TRANSPORT_ATTEMPTS`: see
    :data:`TRANSPORT_RETRY` and :data:`STOP_RULE`. Fields are per unit and
    summed per arm onto :class:`ArmSummary`, beside the meeting-internal
    defaults :class:`DefaultedAttempts` carries.
    """

    retried_calls: int = 0
    unaccounted_attempts: int = 0
    by_trigger: Mapping[str, int] = field(default_factory=lambda: MappingProxyType({}))

    def plus(self, other: TransportAttempts) -> TransportAttempts:
        merged: Counter[str] = Counter(dict(self.by_trigger))
        merged.update(dict(other.by_trigger))
        return TransportAttempts(
            retried_calls=self.retried_calls + other.retried_calls,
            unaccounted_attempts=(
                self.unaccounted_attempts + other.unaccounted_attempts
            ),
            by_trigger=MappingProxyType(dict(sorted(merged.items()))),
        )

    def describe(self) -> str:
        triggers = ", ".join(
            f"{trigger} {count}" for trigger, count in sorted(self.by_trigger.items())
        )
        return (
            f"{self.retried_calls} retried calls, "
            f"{self.unaccounted_attempts} unaccounted attempts"
            + (f" ({triggers})" if triggers else "")
        )


#: The HTTP statuses a retry is worth making, mirroring the authorized client's
#: own ``_RETRYABLE_STATUS`` (``llm/featherless_client.py:529``). Held here
#: rather than imported because the wrapper classifies a FAILURE the client
#: already exhausted its own attempts on, and because importing a private name
#: out of a provider module would couple this instrument to one provider's
#: internals; a test parses that module's source and holds the two sets equal.
_RETRYABLE_STATUS_CODES: Final[frozenset[int]] = frozenset({429, 500, 502, 503, 504})

#: The status a failed send reports, as the authorized client words it
#: (``_format_send_error``, ``llm/featherless_client.py:671-681``).
_HTTP_STATUS_IN_MESSAGE: Final[re.Pattern[str]] = re.compile(r"\bHTTP (\d{3})\b")

#: What the authorized client says when a 2xx body gave it no completion it
#: would record (``_raw_from_response_body``, ``llm/featherless_client.py:803-858``).
#: It raises a bare ``RuntimeError`` for every one of them, so the message is the
#: only handle there is. Two tests hold this tuple to that function: one asserts
#: each fragment is still in its source, so a rewording turns the classifier red
#: instead of turning it into a stop mid-run, and one ENUMERATES every message
#: that function raises and requires this tuple to classify all of them, so a
#: fifth refusal shape added there is red here rather than silently unretried.
#: The last two arrive after the body's ``usage`` block has been read and
#: rejected rather than before, which changes nothing this side: a refusal the
#: adapter raises carries no usage onto the exception either way.
_EMPTY_COMPLETION_MARKERS: Final[tuple[str, ...]] = (
    "refusing to record an empty completion",
    "returned empty assistant content",
    "carried no usage block",
    "usage block omitted prompt_tokens / completion_tokens",
)

#: And what it says when its own sends exhausted on a dropped connection or an
#: unparseable body (``_send_with_retry``, ``llm/featherless_client.py:741-747``).
_TRANSPORT_FAILURE_MARKER: Final[str] = "on a transport/parse error"


def transport_trigger(exc: BaseException) -> TransportTrigger | None:
    """Which no-completion class this failure is, or ``None`` to leave it alone.

    ``None`` is the important half. A failure that carries parse-failure
    metadata is a completion the provider BILLED for and then refused on its own
    schema validation — a sample, which the meeting layer's default path and the
    per-unit reconciliation already handle, and re-drawing it would be a second
    draw on one unit. Every refusal this instrument raises itself is ``None``
    too: a truncation, a foreign checkpoint, an exhausted budget, a deadline and
    a live-gate refusal are limits that were reached, not calls that failed to
    happen, and retrying one would be the "no retry and no widening" the stop
    rule forbids.

    What is left is an attempt that produced nothing, and the four classes are
    the four shapes that takes. ``TimeoutError`` is one of them rather than a
    limit: the wrapper's own per-attempt cut-off never reaches here (its caller
    knows which of the two walls expired), so a ``TimeoutError`` arriving here
    was raised by the inner client and a read timeout is a transport failure.

    Among the wordings, a status the adapter itself wrote decides before any
    body text does. ``_format_send_error`` puts the status first and quotes the
    response body after it, so a permanent 4xx whose body happens to contain an
    empty-completion phrase would otherwise be read off that body and re-sent up
    to :data:`MAX_TRANSPORT_ATTEMPTS` times against an endpoint that has already
    refused it — and only :data:`_RETRYABLE_STATUS_CODES` are retryable at all.
    """

    if extract_parse_failure(exc) is not None:
        return None
    if isinstance(
        exc,
        (InstrumentError, RunDeadlineExceeded, BudgetExceededError, ValidationError),
    ):
        return None
    if isinstance(exc, (httpx.TransportError, TimeoutError)):
        return "transport_error"
    message = str(exc)
    status = _HTTP_STATUS_IN_MESSAGE.search(message)
    if status is not None:
        # The status the adapter reported outranks the body it quotes after it.
        code = int(status.group(1))
        return "retryable_status" if code in _RETRYABLE_STATUS_CODES else None
    if any(marker in message for marker in _EMPTY_COMPLETION_MARKERS):
        return "empty_completion"
    if _TRANSPORT_FAILURE_MARKER in message:
        return "transport_error"
    return None


class _NoCompletion(Exception):
    """Internal: one attempt produced nothing. Never leaves :class:`_InstrumentClient`.

    Carries the trigger class so the retry loop counts what it retried without
    classifying the same exception twice. The original failure is always chained
    onto it, and the loop re-raises that chain on the attempt that exhausts the
    bound.
    """

    def __init__(self, trigger: TransportTrigger) -> None:
        super().__init__(trigger)
        self.trigger = trigger


class _ModelWorkClock:
    """The summed provider-call wall, against the authorized work window.

    Separate from :class:`~orchestrator.run_limits.RunDeadline`, which measures
    ELAPSED time: the authorization allows 6 h of model work inside an 8 h
    elapsed window, which is two limits and therefore two clocks.

    The window bounds each call IN FLIGHT as well as the total after it. A clock
    charged only on return can be overrun by one whole call, and one whole call
    on the authorized provider is not small: ``llm/featherless_client.py`` retries
    a send six times at a 600 s timeout with exponential backoff, so a single
    ``complete`` can stay in flight for the better part of an hour. Charging on
    return alone would let a run at 5 h 59 m of model work spend a seventh hour
    against an authorization of six, with only the separate 8 h elapsed clock
    behind it. :meth:`remaining` is what
    :meth:`_InstrumentClient._attempt` bounds each await by, and
    ``test_the_work_clock_docstring_states_the_authorized_window`` holds the
    figures above to the two constants so a widened authorization cannot leave
    the enforcing class describing the old one.
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

#: The ``model`` a :class:`CapturedCall` carries for an attempt that came back
#: with no completion at all — the class :data:`TRANSPORT_RETRY` sends again.
#: No usage reaches this side for it — the provider client raises before it
#: reads the body's usage block — so its row carries zero tokens and this
#: marker rather than a served model id, and may have been billed for tokens
#: this side cannot see. The report's ``model_ids`` names it beside the real
#: ones: a run that had to send calls twice says so.
UNACCOUNTED_ATTEMPT_MODEL: Final[str] = "no-completion-returned"


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

    Six jobs, none of which the budget layer does:

    1. refuse a ``max_tokens`` that is not one of the two shipped caps, so
       "the shipped defaults unchanged" is checked rather than asserted;
    2. treat a response that reached its cap as a STOP — a truncation is a cap
       artifact, and the authorization says a truncation in either arm is a
       stop, not a datum. The ONE exception is the second calibration's mode
       (``truncation_is_a_measurement``), where the truncated body is returned
       to the meeting layer's shipped fail-soft and counted, because a
       calibration sent to measure a truncation rate cannot stop at the first
       one. It is off by default and the evaluation never turns it on;
    3. refuse a response from a model other than ``expected_model`` on the call
       that returns it, so a hosted endpoint serving a different checkpoint
       stops the run instead of being noticed in the report afterwards;
    4. bound each provider await by the model-work window's remaining seconds,
       so the authorized window stops the run DURING the call that exhausts it
       rather than one whole call later;
    5. send a call that came back with no completion again, up to
       :data:`MAX_TRANSPORT_ATTEMPTS` attempts, counting every one
       (:data:`TRANSPORT_RETRY`);
    6. hold the prompts the supported grader reads, in memory, for one unit.

    Job 5 lives HERE and not in the provider client. ``llm/featherless_client.py``
    retries its own transport families already, and every recorded campaign runs
    through it, so widening its retry classes to cover an empty completion would
    change behaviour for recordings this evaluation has nothing to do with. This
    wrapper is the run's own, and a retry it makes moves nothing else.

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
        # OFF everywhere but the second calibration's own mode. See
        # :meth:`_unusable_response`: it turns the cap branch into a counted
        # measurement and reaches nothing else — not the identity branch, not
        # the live evaluation, and not :data:`STOP_RULE`, which is unedited.
        truncation_is_a_measurement: bool = False,
        max_transport_attempts: int = MAX_TRANSPORT_ATTEMPTS,
        per_attempt_timeout_seconds: float = PER_ATTEMPT_TIMEOUT_SECONDS,
        # Read from the module at CONSTRUCTION rather than captured as a default
        # when this class is defined, so a test of a stop that exhausts the
        # bound does not have to sit out the seven seconds of real backoff the
        # authorized value would spend inside ``run_instrument``.
        backoff_base_seconds: float | None = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        backoff = (
            TRANSPORT_BACKOFF_BASE_SECONDS
            if backoff_base_seconds is None
            else backoff_base_seconds
        )
        if max_transport_attempts < 1:
            raise ValueError("a call is sent at least once")
        if per_attempt_timeout_seconds <= 0:
            raise ValueError("the per-attempt wall must be positive")
        if backoff < 0:
            raise ValueError("a backoff cannot be negative")
        self._inner = inner
        self._work_clock = work_clock
        self._allowed_max_tokens = frozenset({turn_max_tokens, vote_max_tokens})
        self._ceiling = max(turn_max_tokens, vote_max_tokens)
        # ``None`` on the dry run, where the served model is the fixture's own
        # marker; the authorized model id on a live run, where the served model
        # is a thing the manifest binds.
        self._expected_model = expected_model
        self._truncation_is_a_measurement = truncation_is_a_measurement
        self._max_attempts = max_transport_attempts
        self._per_attempt_seconds = per_attempt_timeout_seconds
        self._backoff_base = backoff
        # Injected for the same reason ``llm/featherless_client.py`` injects its
        # own: a test of the bound must not wait out the backoff it is testing.
        self._sleep = sleep
        self._calls: list[CapturedCall] = []
        self._retried_calls = 0
        self._unaccounted_attempts = 0
        self._triggers: Counter[str] = Counter()
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

    def attempts(self) -> TransportAttempts:
        """This unit's retry counts so far, without clearing them."""

        return TransportAttempts(
            retried_calls=self._retried_calls,
            unaccounted_attempts=self._unaccounted_attempts,
            by_trigger=MappingProxyType(dict(sorted(self._triggers.items()))),
        )

    def take_attempts(self) -> TransportAttempts:
        """Return this unit's retry counts and reset them for the next unit."""

        counted = self.attempts()
        self._retried_calls = 0
        self._unaccounted_attempts = 0
        self._triggers.clear()
        return counted

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
        """One call, sent up to :data:`MAX_TRANSPORT_ATTEMPTS` times.

        The caps are checked once, because they describe the REQUEST and no
        retry changes it. Everything after that is one attempt at a time:
        :meth:`_attempt` either returns a response, raises the stop that attempt
        earned, or raises :class:`_NoCompletion` when it produced nothing at
        all. Only the last of those is sent again, and only
        :data:`TRANSPORT_RETRY`'s classes reach it.
        """

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
        for attempt in range(1, self._max_attempts + 1):
            try:
                return await self._attempt(
                    prompt=prompt,
                    schema=schema,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    call_kind=call_kind,
                    model=model,
                    agent_id=agent_id,
                )
            except _NoCompletion as nothing:
                cause = nothing.__cause__ or nothing
                self._triggers[nothing.trigger] += 1
                self._unaccounted_attempts += 1
                if attempt == self._max_attempts:
                    raise TransportAttemptsExhausted(
                        f"{self._max_attempts} attempts at one call came back "
                        f"with no completion (last: {nothing.trigger}, "
                        f"{type(cause).__name__}: {cause})"
                    ) from cause
                # Exponential, like the provider client's own loop, and short:
                # the run's wall is what a wait is spent out of.
                await self._sleep(self._backoff_base * 2 ** (attempt - 1))
                # Counted after the wait, not before it: the counter says a call
                # was SENT again, and a run the elapsed deadline cancels during
                # the backoff never sends it. Nothing is awaited between here and
                # the next send, so the count and the send cannot come apart.
                if attempt == 1:
                    self._retried_calls += 1
        raise AssertionError(  # pragma: no cover - the loop returns or raises
            "the attempt loop neither returned a response nor raised a stop"
        )

    async def _attempt(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind,
        model: str | None,
        agent_id: str | None,
    ) -> LLMResponse:
        """One send, recorded whatever it does.

        Two walls bound the await and only the tighter one applies: what is LEFT
        of the model-work window, the way
        ``orchestrator.run_limits.RunDeadline.run`` bounds meeting work by what
        is left of the elapsed one, and :data:`PER_ATTEMPT_TIMEOUT_SECONDS` for
        this attempt alone. Which of the two expired decides what the cut-off
        means: the window is a limit the run reached and a stop, the per-attempt
        wall is an attempt that stopped answering and a retry. Without the
        window bound the limit is checked only once a call returns, so a run
        near its ceiling can spend one further whole call — up to the provider
        client's own retry-and-timeout budget — beyond the authorization.
        ``timeout.expired()`` separates OUR cut-off from a timeout the inner
        client raised itself, which stays a provider failure.
        """

        started = time.monotonic()
        remaining = self._work_clock.remaining()
        window_binds = remaining <= self._per_attempt_seconds
        window = asyncio.timeout(min(remaining, self._per_attempt_seconds))
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
                # The inner client's own read timeout: an attempt that produced
                # nothing, recorded and retried like the other three classes
                # rather than re-labelled as a limit this run reached.
                raise self._nothing_came_back(
                    trigger="transport_error",
                    started=started,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    agent_id=agent_id,
                ) from exc
            if window_binds:
                aborted = time.monotonic() - started
                # Recorded like every other stop in this client: the attempt
                # bought no response, but it held the provider for ``aborted``
                # seconds and may have been billed for tokens this side cannot
                # see, so it enters the partial accounting as a call with
                # unknown (zero) usage rather than vanishing. Its own marker,
                # because the limit that cut it off is the run's window.
                self._record(
                    agent_id=agent_id,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=0.0,
                    model=ABORTED_ATTEMPT_MODEL,
                    seconds=aborted,
                    disposition="aborted",
                )
                raise self._work_clock.charge_aborted(aborted) from exc
            # The per-attempt wall was the tighter of the two: an endpoint that
            # stopped answering, recorded and retried like the other classes.
            raise self._nothing_came_back(
                trigger="attempt_timeout",
                started=started,
                prompt=prompt,
                max_tokens=max_tokens,
                agent_id=agent_id,
            ) from exc
        except BaseException as exc:
            # A call the provider BILLED and then refused. A real provider
            # validates the completion itself and raises before anything
            # downstream can log it, so this attempt reaches no ``llm_calls``
            # row and would otherwise be missing from the partial accounting a
            # stop reports — the same understatement the truncation stop used to
            # make, and the gap the run of 2026-09-10 stopped on. The
            # parse-failure metadata riding the exception carries the real spend
            # (``llm.provider.extract_parse_failure``).
            failure = extract_parse_failure(exc)
            if failure is None:
                # Nothing was billed, so nothing is charged for tokens; whether
                # the attempt is sent again is :func:`transport_trigger`'s to
                # say, and an exception it does not recognise is re-raised
                # untouched.
                trigger = transport_trigger(exc)
                if trigger is None:
                    raise
                raise self._nothing_came_back(
                    trigger=trigger,
                    started=started,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    agent_id=agent_id,
                ) from exc
            burned = time.monotonic() - started
            self._record(
                agent_id=agent_id,
                prompt=prompt,
                max_tokens=max_tokens,
                input_tokens=failure.input_tokens,
                output_tokens=failure.output_tokens,
                cost_usd=failure.cost_usd,
                model=failure.model,
                seconds=burned,
                disposition="billed_and_refused",
                finish_reason=failure.finish_reason,
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
                finish_reason=failure.finish_reason,
            )
            if stop is not None:
                raise stop from exc
            raise
        seconds = time.monotonic() - started
        # Recorded before either of the stops below, because the response
        # exists: its tokens were spent and its provider time elapsed, and a
        # stop that dropped them would understate its own partial accounting.
        self._record(
            agent_id=agent_id,
            prompt=prompt,
            max_tokens=max_tokens,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost_usd=response.cost_usd,
            model=response.model,
            seconds=seconds,
            finish_reason=response.finish_reason,
        )
        self._work_clock.charge(seconds)
        stop = self._unusable_response(
            model=response.model,
            output_tokens=response.usage.output_tokens,
            max_tokens=max_tokens,
            finish_reason=response.finish_reason,
        )
        if stop is not None:
            raise stop
        return response

    def _record(
        self,
        *,
        agent_id: str | None,
        prompt: str,
        max_tokens: int,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        model: str,
        seconds: float,
        disposition: CallDisposition = "resolved",
        finish_reason: str | None = None,
    ) -> None:
        """Put one attempt in the ledger, with whatever it actually cost.

        One recorder for all four outcomes — a response, a billed-and-refused
        completion, an attempt the window cut off and an attempt that produced
        nothing — so an attempt the provider reported usage for is charged with
        that usage and an attempt it reported none for still occupies a row. A
        row that vanished would understate the partial accounting a stop
        reports, which is the defect the run of 2026-09-10 stopped on.

        ``disposition`` is which of the four this row is. Recorded rather than
        re-derived downstream from the model marker: two of the four carry a
        marker for a model and the other two carry the served one, so a
        summary would have to guess which of THOSE two it was looking at.

        ``finish_reason`` is the provider's own word for why generation
        stopped, on the two dispositions that carry a completion: a response
        reports it and a parse failure's metadata carries it. The other two
        record null and the parameter is defaulted for them, because nothing
        came back to report one — an absent reading is recorded as absent and
        never back-filled.
        """

        self._calls.append(
            CapturedCall(
                agent_id=agent_id,
                prompt=prompt,
                max_tokens=max_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd,
                model=model,
                seconds=seconds,
                disposition=disposition,
                finish_reason=finish_reason,
            )
        )

    def _nothing_came_back(
        self,
        *,
        trigger: TransportTrigger,
        started: float,
        prompt: str,
        max_tokens: int,
        agent_id: str | None,
    ) -> _NoCompletion:
        """Record an attempt that produced no completion, and ask for a retry.

        No usage reaches this side for it — that is what makes it this class
        rather than a billed refusal — so it enters the ledger as an unaccounted
        attempt with a marker for a model and zero tokens, and its wall is
        charged to the work clock, which held it whether or not anything came
        back. Zero is what is KNOWN, not what was spent:
        ``llm/featherless_client.py::_raw_from_response_body`` raises rather than
        returning a completion, and its refusal carries no usage onto the
        exception — whether it refused before reading the body's ``usage`` block
        (no choices, empty content) or because of what that block said (absent,
        or missing its two counts) — so an attempt of this class may have been
        billed for tokens neither this wrapper nor the budget can see.
        Charging a guess instead would put an invented number in the accounting;
        moving the read is a change to the provider client, which this
        instrument deliberately leaves where every recorded campaign has it.
        Returned rather than raised so the caller chains the original failure
        onto it.
        """

        elapsed = time.monotonic() - started
        self._record(
            agent_id=agent_id,
            prompt=prompt,
            max_tokens=max_tokens,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            model=UNACCOUNTED_ATTEMPT_MODEL,
            seconds=elapsed,
            disposition="unaccounted",
        )
        self._work_clock.charge(elapsed)
        return _NoCompletion(trigger)

    def _unusable_response(
        self,
        *,
        model: str,
        output_tokens: int,
        max_tokens: int,
        finish_reason: str | None,
    ) -> InstrumentError | None:
        """The stop a completed call earns, or ``None`` if it earns none.

        Returned rather than raised so the two callers can chain it: a call the
        provider refused on its own schema validation raises this ``from`` the
        provider's exception, and a call that returned raises it bare. One
        function so the two paths cannot enforce different lists — the run of
        2026-09-10's lesson was a check that reached one surface and not the
        other.

        The truncation stop reads TWO signals and prefers neither: the
        provider's own ``finish_reason`` and the ``output_tokens >= max_tokens``
        inference this instrument has always made. Either one stops the run —
        the union can only stop it EARLIER than the inference alone, never
        later, and can never turn a stop into a datum — and the message names
        which of them fired. A call whose two signals disagree is counted per
        arm off its ledger row (:func:`_cap_signals_disagree`); a null reading
        is not a disagreement, because an absent reading contradicts nothing.
        """

        if self._expected_model is not None and model != self._expected_model:
            return ProviderIdentityMismatch(
                f"a response came back from model {model!r}; this run "
                f"is authorized for {self._expected_model!r} only"
            )
        observed, inferred = _truncation_signals(
            finish_reason=finish_reason,
            output_tokens=output_tokens,
            max_tokens=max_tokens,
        )
        if (observed or inferred) and self._truncation_is_a_measurement:
            # The second calibration's mode, and nothing else. A calibration
            # sent to measure the rate at which a ballot runs past its cap
            # cannot stop at the first one: the rate would be unmeasurable and
            # the sitting would report one event and no denominator. So the
            # truncated body is returned, the meeting layer's shipped fail-soft
            # substitutes a marked SKIP or a placeholder turn for it exactly as
            # it does for any other payload that fails schema validation, and
            # the call is counted off this ledger row — per arm, per call type,
            # per voter role and with its ``finish_reason``. The ROW is what
            # carries it (:func:`_truncation_signals` reads the same two
            # signals back out), so nothing is accumulated here.
            #
            # The identity branch above is untouched and still returns its stop:
            # a foreign checkpoint is not a datum in any mode. The live
            # evaluation never constructs this client with the flag set, and
            # :data:`STOP_RULE` still says a truncation is a stop, because on
            # the run it is.
            return None
        if observed or inferred:
            fired: list[str] = []
            if inferred:
                fired.append(
                    f"a response reached its {max_tokens}-token output cap "
                    f"({output_tokens} tokens)"
                )
            if observed:
                fired.append(
                    "the provider reported finish_reason "
                    f"{TRUNCATION_FINISH_REASON!r}"
                    + (
                        ""
                        if inferred
                        else f" on {output_tokens} of {max_tokens} output tokens"
                    )
                )
            message = " and ".join(fired) + "; a truncation is a stop, not a datum"
            if finish_reason is not None and observed != inferred:
                message += (
                    " (the two signals disagree: finish_reason "
                    f"{finish_reason!r} against {output_tokens} of "
                    f"{max_tokens} output tokens)"
                )
            return PerCallCapExceeded(message)
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
            # A DOUBLE's reading, like everything else this provider reports.
            # It writes its own payload and is never cut off, so ``"stop"`` is
            # the honest word; it is supplied so the dry run exercises the
            # recorded field rather than leaving it null on every offline path.
            # It is not an archive's silence — a real adapter that maps no
            # reading still records ``None``.
            finish_reason=FAKE_FINISH_REASON,
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
class VerifiedPrefixRecord:
    """Prefixes regenerated and checked against a committed freeze record.

    Holds the prefixes because the caller needs them; holds no rendered text and
    is never serialized. :func:`assert_report_holds_no_prefix_bytes` is the
    guard on the other side.

    The two subclasses below are what the readers return, and WHICH record was
    verified is the whole of the difference between them. They are siblings on
    purpose — neither is an instance of the other, so a reader's return value
    cannot be passed where the other reader's is required, in mypy or at run
    time. :func:`build_authorized_client` is the caller that rests on that.
    """

    generated: GeneratedSet
    manifest_sha256: str
    accepted_seeds: tuple[int, ...]
    skipped_seeds: tuple[int, ...]

    @property
    def prefixes(self) -> tuple[HeldOutPrefix, ...]:
        return self.generated.prefixes


@dataclass(frozen=True)
class FrozenSet(VerifiedPrefixRecord):
    """A HELD-OUT set, verified by :func:`verify_frozen_set` and unspent.

    The only thing a live run may draw, and the only prefix record
    :func:`build_authorized_client` accepts as proof that the inputs were
    checked before a provider existed.
    """


@dataclass(frozen=True)
class ArchivedSet(VerifiedPrefixRecord):
    """An ARCHIVED set, verified by :func:`verify_archived_set` and spent.

    The record of a band a run already rendered to a model. The offline
    mechanics rehearsal draws it; nothing that reaches a provider may, which is
    why this is a type of its own rather than a :class:`FrozenSet` read from a
    different file.
    """


#: Which of the two records a reader verified. Bound to the shared base so the
#: one body below constructs the class its caller asked for and returns that
#: class, rather than a common type both callers would have to narrow.
_Verified = TypeVar("_Verified", bound=VerifiedPrefixRecord)


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
    test_the_archived_band_keeps_the_blocks_it_was_frozen_with`` is what holds
    it; duplicating the check here would make an un-restamped source edit stop
    the run for a reason the archive check states better.

    Two things are refused here, and the second is not the first said twice: a
    record that does not say ``held_out``, and a record carrying a ``converted``
    block — whatever its ``status`` says. The block names the run that rendered
    those prefixes to a model, so it is a FACT about the bytes, while the status
    is a label one field-edit can flip back; a record that carries both reads as
    a set already spent and is refused as one.

    On this tree it refuses, and that is the settled state: the record at
    :data:`MANIFEST_PATH` is the ARCHIVE of the band the run of 2026-09-16
    spent, marked ``development`` on 2026-09-19, so there is no held-out set to
    verify and no live run can be built from this checkout. The offline
    mechanics path reads that archive through :func:`verify_archived_set`
    instead, which cannot stand in for this one.
    """

    return _verified_prefix_record(repo_root, into=FrozenSet)


def verify_archived_set(repo_root: Path = _REPO_ROOT) -> ArchivedSet:
    """The ARCHIVED record's inputs, for the offline mechanics path only.

    Identical to :func:`verify_frozen_set` in everything it compares, and the
    opposite of it in the one thing it accepts: the record has to be marked
    ``development`` AND carry a ``converted`` block — the archive the closing
    card of 2026-09-19 left at :data:`MANIFEST_PATH` — and a ``held_out``
    record is refused here by name. Neither function can be used in the other's
    place, which is the point of there being two: a set still to be spent is
    not something a rehearsal may draw, and an archive is not something a live
    run may spend. The live paths — :func:`assert_ready_for_a_live_run` and
    :func:`run_instrument` on any provider but ``fake`` — call
    :func:`verify_frozen_set` and reach this function never.

    What it returns says so as well. An :class:`ArchivedSet` is not a
    :class:`FrozenSet` and is not a subclass of one, so it cannot be handed to
    :func:`build_authorized_client` by an edit that merely reaches for the
    nearer reader: that call does not type-check, and it is refused at run time
    too. Before 2026-09-19 both readers returned the same class, which made
    "the inputs were verified" indistinguishable from "an archive was read".

    It exists because the fake-provider run is the instrument's published
    mechanics check (the execution manifest's "Verification of this manifest"
    quotes its command) and it spends nothing, reaches no provider and renders
    to no model. Closing the evaluation stops the spending, not the arithmetic
    that documents it.
    """

    return _verified_prefix_record(repo_root, into=ArchivedSet)


def _verified_prefix_record(repo_root: Path, *, into: type[_Verified]) -> _Verified:
    """The body of both readers above. ``into`` picks which record is legal.

    The type asked for and the record accepted are one choice rather than two
    that could drift apart: ``into`` is both the class returned and the answer
    to "is this the archive path?".
    """

    archived = into is ArchivedSet
    manifest_file = repo_root / MANIFEST_PATH
    if not manifest_file.is_file():
        raise FrozenSetMismatch(f"the freeze manifest is missing: {MANIFEST_PATH}")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise FrozenSetMismatch(f"{MANIFEST_PATH} does not hold a JSON object")
    if archived:
        if manifest.get("status") != "development" or "converted" not in manifest:
            raise FrozenSetMismatch(
                f"the record at {MANIFEST_PATH} is marked "
                f"{manifest.get('status')!r} and carries "
                f"{'a' if 'converted' in manifest else 'no'} 'converted' block; "
                "the offline mechanics path draws the ARCHIVED record and never "
                "a set that is still to be spent"
            )
    elif "converted" in manifest:
        # Before the status, and independent of it: the block is the record of
        # a run that rendered these prefixes to a model, so the inputs are
        # development data whatever the file calls itself. Trusting the status
        # alone left one field-edit between a spent archive and a live spend.
        block = manifest["converted"]
        spent_on = block.get("date") if isinstance(block, Mapping) else None
        raise FrozenSetMismatch(
            f"the record at {MANIFEST_PATH} carries a 'converted' block, dated "
            f"{spent_on!r}, naming the run that already rendered these "
            "prefixes to a model; a spent set is development data whatever its "
            "'status' says, and this run may not draw it"
        )
    elif manifest.get("status") != "held_out":
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
    return into(
        generated=generated,
        manifest_sha256=hashlib.sha256(manifest_file.read_bytes()).hexdigest(),
        accepted_seeds=tuple(seed for seed, _ in expected_accepted),
        skipped_seeds=tuple(seed for seed, _ in expected_skipped),
    )


# ---------------------------------------------------------------------------
# The calibration's inputs: a CONVERTED band's record, never the held-out one
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CalibrationSet:
    """The rebuilt development prefixes a calibration draws, and their record.

    A different type from :class:`FrozenSet` on purpose. The two are produced by
    different functions from different records and authorize different spends,
    so a value of one cannot be passed where the other is required: the
    calibration path cannot be handed the held-out set by a later edit, and the
    held-out run cannot be handed development inputs.

    Holds the prefixes because the calibration renders them, and nothing else
    that a report could carry: the digests are the record's own published ones.
    """

    record_path: Path
    record_sha256: str
    band: SeedBand
    roster: PrefixRoster
    prefixes: tuple[HeldOutPrefix, ...]
    digests: tuple[str, ...]
    accepted_in_record: int
    skipped_in_record: int

    @property
    def seeds(self) -> tuple[int, ...]:
        return tuple(prefix.seed for prefix in self.prefixes)


def _converted_band_for(record: Path, repo_root: Path) -> ConvertedBand:
    """The converted band whose record this path is, or a refusal naming it.

    Matched on the PATH rather than on what the file says its band is: a record
    is the freeze it was written as, and a document that names a converted band
    from somewhere else on disk is not that freeze. The held-out record is
    refused first and by name, because pointing the calibration at it is the one
    mistake that would convert a held-out prefix.
    """

    resolved = record.resolve()
    held_out = (repo_root / MANIFEST_PATH).resolve()
    if resolved == held_out:
        raise CalibrationInputsRejected(
            f"{MANIFEST_PATH} is the HELD-OUT record; a calibration draws "
            "development data only, and rendering a held-out prefix to the "
            "model would convert the set this evaluation has still to spend"
        )
    for converted in CONVERTED_BANDS:
        if (repo_root / converted.manifest_path).resolve() == resolved:
            return converted
    raise CalibrationInputsRejected(
        f"{record} is not a converted band's freeze record; the calibration "
        "draws one of "
        + ", ".join(converted.manifest_path for converted in CONVERTED_BANDS)
        + " and nothing else"
    )


def verify_calibration_set(
    record: Path,
    *,
    repo_root: Path = _REPO_ROOT,
    paired_seeds: int = CALIBRATION_PAIRED_SEEDS,
    draw_at_most: bool = False,
) -> CalibrationSet:
    """Rebuild the calibration's prefixes from a converted record, or refuse.

    The development-data counterpart of :func:`verify_frozen_set`, and it
    differs from it in exactly two ways, both of them because a converted band
    is not the band the generator's own constants describe:

    * the band comes from :data:`CONVERTED_BANDS` rather than from
      :data:`~experiments.held_out_prefixes.PREREGISTERED_BAND`, so a record the
      generator would no longer draw is still checkable;
    * only the first ``paired_seeds`` accepted seeds are rebuilt, with
      :func:`~experiments.held_out_prefixes.build_prefix` seed by seed, because
      re-running the whole filter over a thousand seeds to reach five prefixes
      is a minute of replay for no evidence. Everything the filter decided is
      already in the record, and what the calibration needs from it is that the
      five prefixes it renders are the five that record froze — which their
      digests say.

    The generator is unchanged and is not asked to change: ``build_prefix``
    already takes its seed, roster and map, so drawing a converted band needs
    nothing of it but the arguments this function passes.

    ``draw_at_most`` is :func:`verify_calibration_draw`'s: it draws
    ``min(paired_seeds, what the record accepts)`` instead of refusing a record
    that holds fewer, because a draw that spans records fills a short record
    from the NEXT band rather than stopping on it. Off by default, so the
    single-record path keeps refusing a record it cannot fill — the second
    calibration's own "ran out of seeds" refusal lives one level up, over the
    whole draw, where the question is actually answerable.
    """

    if paired_seeds < 1:
        raise ValueError(f"a calibration draws at least one seed, got {paired_seeds}")
    converted = _converted_band_for(record, repo_root)
    resolved = record.resolve()
    if not resolved.is_file():
        raise CalibrationInputsRejected(f"the calibration record is missing: {record}")
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CalibrationInputsRejected(f"{record} does not hold a JSON object")
    status = payload.get("status")
    if status != "development":
        raise CalibrationInputsRejected(
            f"{converted.manifest_path} is marked {status!r}, not 'development'; "
            "a calibration spends on data a stopped run already rendered, and "
            "on nothing else"
        )
    if payload.get("temporal_observation_version") != TEMPORAL_OBSERVATION_VERSION:
        raise CalibrationInputsRejected(
            "the calibration record was screened under observation clock "
            f"{payload.get('temporal_observation_version')!r}, but both arms "
            f"run clock {TEMPORAL_OBSERVATION_VERSION}"
        )
    if payload.get("max_ticks") != MAX_TICKS:
        raise CalibrationInputsRejected(
            f"the calibration record names a {payload.get('max_ticks')!r}-tick "
            f"budget; the generator builds every prefix inside {MAX_TICKS}"
        )
    raw_roster = payload.get("roster")
    if not isinstance(raw_roster, Mapping):
        raise CalibrationInputsRejected(
            f"{converted.manifest_path} carries no roster block; it does not "
            "describe the set this calibration would draw"
        )
    # The three parsers below are the freeze record's, shared with the held-out
    # check so one reader decides what a record field means. Their refusal class
    # is re-raised as this path's, because what a runner needs told here is that
    # the CALIBRATION's inputs were rejected, not that a frozen set was.
    try:
        roster = _parsed_roster(raw_roster)
        band = _parsed_band(payload.get("band"))
        rows = _manifest_rows(payload, "accepted")
        accepted = [(_as_int(row, "seed"), _as_str(row, "sha256")) for row in rows]
        skipped_in_record = len(_manifest_rows(payload, "skipped"))
    except FrozenSetMismatch as mismatch:
        raise CalibrationInputsRejected(
            f"{converted.manifest_path} is not a readable freeze record: {mismatch}"
        ) from mismatch
    if roster != FROZEN_PREFIX_ROSTER:
        raise CalibrationInputsRejected(
            f"the calibration record's roster is {roster!r}; the generator draws "
            f"{FROZEN_PREFIX_ROSTER!r} and a change of roster invalidates both "
            "the screening and the token budget this calibration measures"
        )
    if band != converted.band:
        raise CalibrationInputsRejected(
            f"{converted.manifest_path} names band {band.first_seed}-"
            f"{band.last_seed} size {band.size}; the converted band it is the "
            f"record of is {converted.band.first_seed}-{converted.band.last_seed} "
            f"size {converted.band.size}"
        )
    seeds = [seed for seed, _ in accepted]
    if seeds != sorted(seeds):
        raise CalibrationInputsRejected(
            "the calibration record's accepted seeds are not ascending; the "
            "first five of a different order are a different five prefixes"
        )
    if len(accepted) < paired_seeds and not draw_at_most:
        raise CalibrationInputsRejected(
            f"{converted.manifest_path} accepts {len(accepted)} seeds and this "
            f"calibration draws {paired_seeds}"
        )
    drawn = min(paired_seeds, len(accepted))
    game_map = load_canonical_map()
    prefixes: list[HeldOutPrefix] = []
    for seed, digest in accepted[:drawn]:
        prefix = build_prefix(seed=seed, roster=roster, game_map=game_map)
        rebuilt = prefix_sha256(prefix)
        if rebuilt != digest:
            raise CalibrationInputsRejected(
                f"seed {seed} rebuilds to {rebuilt}, and "
                f"{converted.manifest_path} froze {digest}: the generator no "
                "longer produces the prefix this record describes, so the "
                "calibration would measure inputs nobody froze"
            )
        assert_no_legacy_body_handles([canonical_prefix_json(prefix)])
        prefixes.append(prefix)
    return CalibrationSet(
        record_path=resolved,
        record_sha256=hashlib.sha256(resolved.read_bytes()).hexdigest(),
        band=band,
        roster=roster,
        prefixes=tuple(prefixes),
        digests=tuple(digest for _, digest in accepted[:drawn]),
        accepted_in_record=len(accepted),
        skipped_in_record=skipped_in_record,
    )


@dataclass(frozen=True)
class CalibrationDraw:
    """The records ONE calibration draws across, in order, and their prefixes.

    The first calibration drew five seeds and one converted record held them.
    The second draws sixty, and no record holds sixty: the 3000-3999 and
    5000-5999 freezes accept fifty each. So the draw is a sequence of
    :class:`CalibrationSet` rather than one of them, taken from
    :data:`~experiments.held_out_prefixes.CONVERTED_BANDS` in list order until
    the seed count is bound — all fifty of the first record, then the first ten
    of the second.

    A separate type for the same reason :class:`CalibrationSet` is separate
    from :class:`FrozenSet`: it is what :func:`verify_calibration_draw`
    produces and nothing else, so a caller holding one has been through the
    per-record checks for every record in it. Each set in ``sets`` carries its
    own record path, its own sha256 and the seeds drawn from it, which is what
    the report's inputs block publishes.
    """

    sets: tuple[CalibrationSet, ...]

    @property
    def prefixes(self) -> tuple[HeldOutPrefix, ...]:
        """Every drawn prefix, in draw order across the records."""

        return tuple(prefix for drawn in self.sets for prefix in drawn.prefixes)

    @property
    def seeds(self) -> tuple[int, ...]:
        return tuple(prefix.seed for prefix in self.prefixes)

    @property
    def paired_seeds(self) -> int:
        return len(self.prefixes)


def _converted_record_paths(repo_root: Path) -> tuple[Path, ...]:
    """Every converted band's record, in the order those bands were converted."""

    return tuple(repo_root / band.manifest_path for band in CONVERTED_BANDS)


def _draw_in_converted_order(
    paths: Sequence[Path], *, repo_root: Path
) -> tuple[Path, ...]:
    """Hold a supplied record list to a PREFIX of the converted records, or refuse.

    The card's decision 2 and the manifest's dated section both say the draw is
    :data:`CONVERTED_BANDS` in the order those bands were converted, with
    nothing left to the runner — so a list is a PREFIX of that order: it starts
    at the first converted record and skips none, which with the greedy fill in
    :func:`verify_calibration_draw` makes the drawn seeds a function of the seed
    count alone. An ordered non-repeating SUBSEQUENCE is not enough, and the
    round-2 review of 2026-09-15 is why: :data:`CONVERTED_BANDS` held three
    development records at that review, so ``[band-5000, band-6000]`` and
    ``[band-3000, band-6000]`` are each ascending and name no record twice, yet
    each verified clean at sixty seeds and ended at seed 6010 where the
    authorized draw ends at 5009 — a different sixty seeds under the same
    authorization. Round 1 had reproduced the two shapes this rule already
    refused, ``[band-5000, band-3000]`` (re-ordered) and
    ``[band-3000, band-3000]`` (sixty prefixes over fifty distinct seeds).

    Checked here rather than trusted, and before a prefix is rebuilt, because
    the caller that may pass a list is the live-capable pre-flight
    (:func:`assert_ready_for_a_calibration`, :func:`run_calibration`): each of
    those shapes would have spent an authorized live sitting on a draw nobody
    approved.

    Membership itself is :func:`_converted_band_for`'s, which refuses the
    held-out record BY NAME before anything else and refuses a path that is no
    converted band's record at all; this adds the two facts that are about the
    list rather than about one path.

    One consequence, stated rather than absorbed: the first calibration's
    ``--calibration-record`` can now name only the first converted record, the
    one it drew from. Its clause reads "a converted band", so this is narrower
    than that authorization — and narrowing one can refuse a spend that was
    approved but can never permit one that was not, which is the direction a
    pre-flight should err in.
    """

    order = [band.manifest_path for band in CONVERTED_BANDS]
    seen: dict[str, int] = {}
    for position, path in enumerate(paths):
        converted = _converted_band_for(path, repo_root)
        if converted.manifest_path in seen:
            raise CalibrationInputsRejected(
                f"the calibration draw names {converted.manifest_path} twice "
                f"(at positions {seen[converted.manifest_path] + 1} and "
                f"{position + 1}); a record drawn twice renders the same seeds "
                "twice and reports them as distinct paired seeds, so the draw "
                "is the converted records without repetition"
            )
        if position >= len(order) or order[position] != converted.manifest_path:
            raise CalibrationInputsRejected(
                f"the calibration draw names {converted.manifest_path} at "
                f"position {position + 1}; the draw is the converted records "
                "in the order those bands were converted, from the first "
                "onwards with none skipped ("
                + ", ".join(order)
                + "), and any other list draws a different set of seeds under "
                "the same authorization"
            )
        seen[converted.manifest_path] = position
    return tuple(paths)


def verify_calibration_draw(
    *,
    records: Sequence[Path] | None = None,
    repo_root: Path = _REPO_ROOT,
    paired_seeds: int = CALIBRATION_2_PAIRED_SEEDS,
) -> CalibrationDraw:
    """Bind ``paired_seeds`` accepted seeds across the converted records, or refuse.

    Ascending within each record and in :data:`CONVERTED_BANDS`' own order
    across them, which is the order the bands were converted: a draw is
    reproducible from the list and the count alone, with no choice left to the
    runner. Every record goes through :func:`verify_calibration_set` unchanged
    — status, observation clock, tick budget, roster, band, ascending seeds and
    every drawn prefix rebuilt and held to the digest that record froze — and
    the held-out record is refused by name inside it
    (:func:`_converted_band_for`), so pointing this at the live band is refused
    at the first path rather than after fifty prefixes have been rebuilt.

    ``records`` names a PREFIX of that order and nothing else:
    :func:`_draw_in_converted_order` refuses a re-ordered, repeated or
    band-skipping list before a prefix is rebuilt. With the greedy fill below,
    that makes the drawn seeds a function of ``paired_seeds`` alone — an
    accepted ``records`` list draws exactly what the default draws — so the
    override cannot turn the canonical draw into one the card does not
    authorize, only shorten the list of records the same draw may spill into.

    A draw that cannot be filled is a stop, not a smaller calibration: sixty
    paired seeds is the owner's decision 7 and fifty of them measures a
    different thing. That refusal is here rather than in
    :func:`verify_calibration_set`, because whether a short record matters is a
    question about the whole draw.
    """

    if paired_seeds < 1:
        raise ValueError(f"a calibration draws at least one seed, got {paired_seeds}")
    paths = _converted_record_paths(repo_root) if records is None else tuple(records)
    if not paths:
        raise CalibrationInputsRejected(
            "a calibration draw names at least one converted record"
        )
    paths = _draw_in_converted_order(paths, repo_root=repo_root)
    sets: list[CalibrationSet] = []
    drawn = 0
    for path in paths:
        if drawn >= paired_seeds:
            break
        chunk = verify_calibration_set(
            path,
            repo_root=repo_root,
            paired_seeds=paired_seeds - drawn,
            draw_at_most=True,
        )
        if not chunk.prefixes:
            continue
        sets.append(chunk)
        drawn += len(chunk.prefixes)
    if drawn < paired_seeds:
        named = ", ".join(str(path) for path in paths)
        raise CalibrationInputsRejected(
            f"the converted records this draw may use ({named}) accept "
            f"{drawn} seeds in all and this calibration draws {paired_seeds}: "
            "a draw that runs out of accepted seeds is a stop, not a smaller "
            "calibration"
        )
    return CalibrationDraw(sets=tuple(sets))


def assert_ready_for_a_calibration(
    record: Path | None = None,
    *,
    provider: str,
    invocation: LiveRunInvocation | None,
    records: Sequence[Path] | None = None,
    limits: RunLimits = CALIBRATION_LIMITS,
    sampling: SamplingConfig = CALIBRATION_SAMPLING,
    paired_seeds: int = CALIBRATION_PAIRED_SEEDS,
    repo_root: Path = _REPO_ROOT,
) -> CalibrationDraw:
    """Everything a calibration must satisfy BEFORE a client exists, in order.

    The same ordering rule as :func:`assert_ready_for_a_live_run`: arithmetic
    and the authorization first, the inputs next, and the verified inputs are
    what :func:`build_authorized_client` requires as its first argument, so a
    credential is never made for a calibration that may not run.

    ``record`` names ONE converted record, as the first calibration's CLI does;
    ``records`` names the draw's records in order; neither names the default,
    which is every converted record in :data:`CONVERTED_BANDS`' own order. The
    two are mutually exclusive, because a caller that passed both would have
    said two different things about the same draw. Either way the list reaches
    :func:`_draw_in_converted_order`, which holds it to a PREFIX of
    :data:`CONVERTED_BANDS` before a prefix is rebuilt, so neither override can
    name a draw the mode's clause does not authorize.

    The mode is resolved FIRST, before the feasibility arithmetic rather than
    after it, because the profile a mode's ceilings are checked against is a
    field of the mode (:class:`CalibrationMode`) and the three modes do not
    share one. :func:`calibration_mode_for` reads no file and needs no
    credential, so nothing about the ordering rule — arithmetic and the
    authorization before the inputs, the inputs before a client — changes.
    """

    mode = calibration_mode_for(
        limits=limits, sampling=sampling, paired_seeds=paired_seeds
    )
    assert_limits_are_feasible(
        limits=limits,
        sampling=sampling,
        units=calibration_units(paired_seeds),
        # As above: the profile THIS mode was sized on.
        calibrated_unit_input_tokens=mode.sizing_unit_input_tokens,
        calibrated_unit_output_tokens=mode.sizing_unit_output_tokens,
    )
    assert_calibration_is_authorized(
        provider=provider,
        invocation=invocation,
        limits=limits,
        sampling=sampling,
        paired_seeds=paired_seeds,
        repo_root=repo_root,
    )
    return verify_calibration_draw(
        records=_draw_records(record=record, records=records),
        repo_root=repo_root,
        paired_seeds=paired_seeds,
    )


def _draw_records(
    *, record: Path | None, records: Sequence[Path] | None
) -> Sequence[Path] | None:
    """The record list a caller asked for, or ``None`` for every converted band."""

    if record is not None and records is not None:
        raise ValueError(
            "a calibration draws from one record or from a named list of "
            "them, not from both"
        )
    if record is not None:
        return [record]
    return records


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
    transport_attempts: TransportAttempts


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

    replay_path = unit_replay_path(output_dir, arm=arm.name, seed=prefix.seed)
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
    # Drained with the calls and for the same reason: the attempts belong to the
    # unit that made them, and the next unit starts at zero.
    attempts = client.take_attempts()
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
        transport_attempts=attempts,
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

# The aboutness rule itself lives in the MEETING layer
# (:mod:`meetings.citation_relevance`) and is imported at the top of this
# module. It used to live here, which is why the recording-time gate could not
# ask it: ``meetings/`` may not import ``experiments/``, while this module
# imports ``meetings`` freely. One definition, two callers -- this grader and
# :func:`meetings.manager.label_ballot_grounding`, which asks it unconditionally
# to decide ``supported`` versus ``off_target`` -- and
# ``tests/meetings/test_citation_relevance.py`` asserts the two cannot reach
# different verdicts about the same ballot.


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
            # The grader's surface is EVERY prompt this voter received during
            # the unit, split into lines here: the recording-time guard holds
            # only the ballot prompt, and the shared rule takes lines so
            # neither caller has to fake the other's surface.
            verdict = (
                "relevant"
                if citations_bear_on(
                    cited_turn_id=cited_turn,
                    cited_observation_id=cited_observation,
                    subject=subject,
                    turns_by_id=by_id,
                    lines=[
                        line
                        for prompt in prompts_by_agent.get(ballot.voter, ())
                        for line in prompt.splitlines()
                    ],
                )
                else "off_target"
            )
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
# The authored-ballot diagnostics (the diagnosis of 2026-09-18, decision 2)
# ---------------------------------------------------------------------------
#
# What the crew AUTHORED, before the guards rewrote it. The meeting layer
# already records the authored target on every rewritten ballot
# (``VoteBallot.guard_redirected_from`` beside ``guard_rewrite_reason``), so the
# layer BELOW the recorded tally is recoverable from the ballots alone and no
# new recording is needed for it. Every count here is a labelled diagnostic:
# nothing in the run path reads one, no stop condition mentions one, and none of
# them is on :class:`PairedResult`.

#: What the block says about itself, in the report and in the manifest alike.
#: Held as a constant so the two cannot drift, and stated in full because a
#: reader meeting a 63% precision figure beside a 2-of-12 outcome will otherwise
#: supply the wrong reading of it.
AUTHORED_DIAGNOSTICS_NOTE: Final[str] = (
    "AUTHORING-CONDITIONED DIAGNOSTICS. Every count below is conditioned on a "
    "ballot having been AUTHORED as an ejection, so it flatters whichever arm "
    "authors more ejections and says nothing about how often an arm decides "
    "correctly. They are reported beside the primary outcome and are NEVER a "
    "decision input: no stop condition reads one, the decision rule does not "
    "mention one, none of them is a field of the paired result, and they were "
    "never preregistered — they were approved on 2026-09-18 as a labelled "
    "diagnostic only (decision 2 of the diagnosis of that day). The crew "
    "per-ballot precision is therefore reported ONLY beside its harm counter, "
    "the crew-on-crew authored ejections and the units carrying one, because "
    "an arm can raise both together. An authored ejection the meeting could "
    "not act on — an id naming no living candidate — is reported in its own "
    "illegal-target column and counted in no other, naming as it does neither "
    "the impostor nor a crewmate. The arms also differ in the ballot "
    "REGISTER as well as in the accounts surface, so a cross-arm reading of "
    "these counts is confounded until the v5 prompt set equalises the register."
)

#: The same block as published by the 2026-09-18 CALIBRATION, which reports no
#: primary outcome for it to sit beside and runs the v5 prompt set on both arms.
#: A second string rather than an edit of the one above, for the reason
#: :data:`CALIBRATION_3_CAVEAT` is a second caveat: the live run's note is what
#: that run's block is published under and it stays byte-identical, while a
#: reader of THIS payload would be told two things it contradicts — that the
#: counts sit beside a primary outcome, and that the register confound waits on
#: a prompt set this sitting already renders. The half that does not change is
#: the half that matters: authoring-conditioned, paired precision and harm,
#: never preregistered, never a decision input.
CALIBRATION_3_AUTHORED_DIAGNOSTICS_NOTE: Final[str] = (
    "AUTHORING-CONDITIONED DIAGNOSTICS. Every count below is conditioned on a "
    "ballot having been AUTHORED as an ejection, so it flatters whichever arm "
    "authors more ejections and says nothing about how often an arm decides "
    "correctly. This is a DEVELOPMENT calibration: no primary outcome is "
    "reported beside them, no paired statistic was computed and no decision "
    "rule was evaluated. They are NEVER a decision input: no stop condition "
    "reads one, the decision rule does not mention one, none of them is a "
    "field of the paired result, and they were never preregistered — they were "
    "approved on 2026-09-18 as a labelled diagnostic only (decision 2 of the "
    "diagnosis of that day). The crew per-ballot precision is therefore "
    "reported ONLY beside its harm counter, the crew-on-crew authored "
    "ejections and the units carrying one, because an arm can raise both "
    "together. An authored ejection the meeting could not act on — an id "
    "naming no living candidate — is reported in its own illegal-target "
    "column and counted in no other, naming as it does neither the impostor "
    "nor a crewmate. Both arms of this sitting render the revision of "
    "2026-09-18, so whether the ballot REGISTER is now equal across them is "
    "one of the things these counts are read FOR rather than something a "
    "reader may assume; they are read against the predictions the manifest "
    "fixed BEFORE the sitting, and none of those is a gate."
)

#: The rewrite reasons the tally reports, read off the schema's own alias rather
#: than listed here: a reason ADDED to
#: :data:`~meetings.schemas.BallotTargetRewriteReason` has to appear in this
#: block with a zero count without another edit to this module.
BALLOT_REWRITE_REASONS: Final[tuple[str, ...]] = tuple(
    sorted(get_args(BallotTargetRewriteReason))
)

#: The audit marker each target-rewriting reason writes onto ``rationale_text``,
#: from the production literals so a rename breaks loudly here. The block counts
#: over THIS rather than over ``VoteBallot.guard_rewrite_reason``, because the
#: typed field records the FIRST rewrite only: ``ballot_target_rewrite_provenance``
#: (``meetings/voting.py``) returns ``{}`` once a reason is set, so a ballot
#: re-aimed by ``under_gate_redirect`` and THEN coerced by the citation gate
#: keeps ``under_gate_redirect`` in the field while both markers stack on the
#: rationale. The fifth run's seed 8006 is exactly that ballot, and reading the
#: single field would report zero coercions on a run full of them. Both guards
#: were retired by ruling D6 of 2026-09-19, so this table reads RECORDED bytes:
#: no run after that mints either marker, and no new ballot stacks. The typed
#: field keeps its own jobs -- the AUTHORED target and whether the ballot reached
#: the tally -- which are properties of the first rewrite and are read from it.
#:
#: ``parse_default`` is the one that is not a prefix: it is the WHOLE rationale
#: of a ballot that authored nothing, so it is matched the same way (its head is
#: still at position zero) and cannot stack with anything.
_TARGET_REWRITE_MARKERS: Mapping[str, str] = MappingProxyType(
    {
        "invalid_target": INVALID_VOTE_TARGET_MARKER,
        "teammate_coerced": TEAMMATE_VOTE_TARGET_MARKER,
        "under_gate_redirect": BALLOT_TARGET_REDIRECT_MARKER,
        "uncited_coerced": UNCITED_ZERO_FLAG_EJECT_MARKER,
        "off_target_coerced": OFF_TARGET_CITATION_EJECT_MARKER,
        "parse_default": VOTE_PARSE_DEFAULT_MARKER,
    }
)

if set(_TARGET_REWRITE_MARKERS) != set(BALLOT_REWRITE_REASONS):  # pragma: no cover
    raise InstrumentError(
        "every ballot target-rewrite reason needs its marker here: a reason "
        "without one is a rewrite this diagnostic cannot see"
    )

#: The static head of each marker -- everything before its ``{...!r}`` payload.
#: Matching the head is enough to say the marker fired and is what keeps this
#: independent of the payload's repr quoting.
_TARGET_REWRITE_MARKER_HEADS: Mapping[str, str] = MappingProxyType(
    {
        reason: marker.split("{", 1)[0]
        for reason, marker in _TARGET_REWRITE_MARKERS.items()
    }
)

#: The OTHER markers the ballot chain prepends: the two citation-id validators,
#: which run before the target rewrites and so sit deeper in the same stack
#: (``meetings/manager.py`` ``_normalize_ballot_reason_id`` and
#: ``_normalize_ballot_observation_id``). They rewrite no target and are counted
#: nowhere here; they are listed so the walk below can step OVER one instead of
#: stopping at it and missing a rewrite behind it.
_OTHER_BALLOT_MARKER_HEADS: Final[tuple[str, ...]] = (
    INVALID_REASON_ID_MARKER.split("{", 1)[0],
    INVALID_OBSERVATION_ID_MARKER.split("{", 1)[0],
)

#: What ends every marker in the chain: the closing bracket and its space.
_BALLOT_MARKER_TERMINATOR: Final[str] = "] "


def ballot_rewrites_that_fired(ballot: VoteBallot) -> tuple[str, ...]:
    """Every target rewrite this ballot's marker stack records, sorted by reason.

    One RECORDED ballot can carry two (the redirect-then-coerce class, which
    ruling D6 of 2026-09-19 left as history — no live chain stacks it now); the
    typed ``guard_rewrite_reason`` names only the first, which is why this reads
    the stack. A ballot no guard touched returns ``()``.

    ANCHORED to the stack rather than searched for anywhere in the rationale.
    Every guard in the ballot chain PREPENDS its marker and none of them edits
    the body -- ``meetings/manager.py``'s ``_preserved_ballot_markers`` raises
    if that is ever untrue -- so the markers are a contiguous block at position
    zero and the model's own text is the suffix. A substring search over the
    whole rationale therefore counts a model that ECHOES a marker phrase as a
    guard that fired: on the recorded runs this grades the vote prompt rendered
    coerced ballots back to later voters, so "[off-target citation for eject
    target 'p-2' coerced to SKIP]"
    is a phrase the model has seen and can reproduce, and one echo would move
    the rewrite tally of a sitting the guard never touched. This walks the
    block from position zero, consuming one recognised marker at a time and
    stopping at the first thing that is not one, which is where this codebase's
    text ends and the model's begins.
    """

    text = ballot.rationale_text
    fired: set[str] = set()
    offset = 0
    while offset < len(text):
        matched = next(
            (
                reason
                for reason, head in _TARGET_REWRITE_MARKER_HEADS.items()
                if text.startswith(head, offset)
            ),
            None,
        )
        if matched is None and not any(
            text.startswith(head, offset) for head in _OTHER_BALLOT_MARKER_HEADS
        ):
            break
        end = text.find(_BALLOT_MARKER_TERMINATOR, offset)
        if end < 0:
            # A marker head with no terminator is a truncated record rather
            # than a fired guard; stop here rather than guess where it ended.
            break
        if matched is not None:
            fired.add(matched)
        offset = end + len(_BALLOT_MARKER_TERMINATOR)
    return tuple(reason for reason in BALLOT_REWRITE_REASONS if reason in fired)


#: The null a crew ballot's target is read against: two legal targets. The crew
#: pair's common candidate set on this prefix is the impostor and the other
#: crewmate (``meetings/manager.py`` ``_candidate_targets``, living-minus-voter,
#: on a four-player roster with one dead), so a crewmate authoring an ejection
#: at random names the impostor half the time. The denominator it is read
#: against therefore holds LEGAL authored targets only
#: (:func:`_authored_a_legal_target`): a trial with no legal target is not a
#: trial of this null.
CREW_PRECISION_NULL: Final[float] = 0.5

#: The null an EJECTION is read against: one of the three living players.
EJECTION_CHANCE_NULL: Final[float] = 1.0 / 3.0


def authored_ballot_target(ballot: VoteBallot) -> str | None:
    """The target the VOTER wrote, or ``None`` when the voter wrote none.

    The guard pair is the meeting layer's own typed testimony about its rewrite
    (``meetings/schemas.py``), written by ``ballot_target_rewrite_provenance``
    at every rewrite site and serialized only when a guard fired. So the
    authored target is ``guard_redirected_from`` where one did and ``target``
    where none did — and ``None`` under ``parse_default``, where nothing parsed
    and therefore nothing was authored.
    """

    if ballot.guard_rewrite_reason is None:
        return ballot.target
    return ballot.guard_redirected_from


def _authored_an_ejection(ballot: VoteBallot) -> bool:
    """Whether this voter authored an EJECTION rather than a SKIP or nothing."""

    authored = authored_ballot_target(ballot)
    return authored is not None and authored != SKIP_TARGET


#: The recorded reason under which the AUTHORED target is not one the meeting
#: could have acted on: the layer normalized it because it named no living
#: candidate — a hallucinated id, a player already dead, or the voter itself
#: (``meetings/voting.py`` ``normalize_ballot_target`` and the manager's own
#: ``_normalize_ballot_target``, both of which preserve the id verbatim).
ILLEGAL_TARGET_REASON: Final[str] = "invalid_target"


def _authored_a_legal_target(
    ballot: VoteBallot, roles: Mapping[PlayerId, Role]
) -> bool:
    """Whether the voter's authored target was one the meeting could act on.

    The meeting layer decides this and not the instrument: ``invalid_target``
    is its own typed verdict that the id the voter wrote named no living
    candidate other than the voter, so what ``guard_redirected_from`` preserved
    under that reason is a hallucination, a dead player or the voter itself.
    Such a ballot named neither the impostor nor a crewmate, and the null the
    crew row is read against is the null of the crew pair's TWO LEGAL TARGETS —
    a trial that had none is in neither half of it and in neither denominator.
    The roster test is the belt to that brace: an id nobody on this unit's
    roster carries is illegal whatever reason the layer recorded.
    """

    if ballot.guard_rewrite_reason == ILLEGAL_TARGET_REASON:
        return False
    authored = authored_ballot_target(ballot)
    return authored is not None and authored in roles and authored != ballot.voter


def _reached_the_tally(ballot: VoteBallot) -> bool:
    """Whether the recorded ballot still names a player rather than SKIP.

    "Cleared the citation gate" in the block's terms, which are the RECORDED
    run's: that gate was retired by ruling D6 of 2026-09-19 and coerces nothing
    now. Read off the RECORDED target rather than off the rewrite reason,
    because more than one guard could coerce a ballot to SKIP on those bytes and
    the question asked is what the tally saw.
    """

    return ballot.target != SKIP_TARGET


def _converted(ballot: VoteBallot) -> bool:
    """Whether the recorded ballot reached the tally on its AUTHORED target.

    Strictly stronger than :func:`_reached_the_tally`: a ballot the under-gate
    redirect re-aimed cleared the gate and voted for somebody its voter did not
    name.
    """

    return ballot.target == authored_ballot_target(ballot)


class AuthoredBallotCounts(BaseModel):
    """One unit's authored-ballot counts, additive across units.

    Counts only, so a unit's row carries no ballot, no target and no role — the
    same rule :class:`UnitTelemetry` follows, and the reason this projection
    happens at unit close rather than at report time: a resumed run summarises
    units it did not run, and the only thing it has of them is the checkpoint.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    crew_authored_ejects: int = 0
    crew_authored_naming_impostor: int = 0
    crew_authored_ejects_cleared: int = 0
    crew_on_crew_authored_ejects: int = 0
    #: 0 or 1 per unit, so the arm's sum is the number of units carrying one.
    units_with_crew_on_crew: int = 0
    #: Authored ejections at a target the meeting could not act on, counted in
    #: their own column and in NO other: neither naming the impostor nor naming
    #: a crewmate, and so in neither precision denominator.
    crew_authored_illegal_targets: int = 0
    impostor_authored_ejects: int = 0
    impostor_authored_ejects_cleared: int = 0
    impostor_authored_illegal_targets: int = 0
    correct_coalitions: int = 0
    correct_coalitions_cleared: int = 0
    correct_coalitions_converted: int = 0
    wrongful_coalitions: int = 0
    wrongful_coalitions_cleared: int = 0
    wrongful_coalitions_converted: int = 0
    ejections: int = 0
    role_correct_ejections: int = 0
    crew_authored_role_correct_ejections: int = 0
    guard_rewrites_by_reason: Mapping[str, int] = {}

    def plus(self, other: AuthoredBallotCounts) -> AuthoredBallotCounts:
        """Two units' counts, summed. The arm's block is this folded over units."""

        reasons: Counter[str] = Counter(self.guard_rewrites_by_reason)
        reasons.update(other.guard_rewrites_by_reason)
        return AuthoredBallotCounts(
            crew_authored_ejects=self.crew_authored_ejects + other.crew_authored_ejects,
            crew_authored_naming_impostor=(
                self.crew_authored_naming_impostor + other.crew_authored_naming_impostor
            ),
            crew_authored_ejects_cleared=(
                self.crew_authored_ejects_cleared + other.crew_authored_ejects_cleared
            ),
            crew_on_crew_authored_ejects=(
                self.crew_on_crew_authored_ejects + other.crew_on_crew_authored_ejects
            ),
            units_with_crew_on_crew=(
                self.units_with_crew_on_crew + other.units_with_crew_on_crew
            ),
            crew_authored_illegal_targets=(
                self.crew_authored_illegal_targets + other.crew_authored_illegal_targets
            ),
            impostor_authored_ejects=(
                self.impostor_authored_ejects + other.impostor_authored_ejects
            ),
            impostor_authored_ejects_cleared=(
                self.impostor_authored_ejects_cleared
                + other.impostor_authored_ejects_cleared
            ),
            impostor_authored_illegal_targets=(
                self.impostor_authored_illegal_targets
                + other.impostor_authored_illegal_targets
            ),
            correct_coalitions=self.correct_coalitions + other.correct_coalitions,
            correct_coalitions_cleared=(
                self.correct_coalitions_cleared + other.correct_coalitions_cleared
            ),
            correct_coalitions_converted=(
                self.correct_coalitions_converted + other.correct_coalitions_converted
            ),
            wrongful_coalitions=self.wrongful_coalitions + other.wrongful_coalitions,
            wrongful_coalitions_cleared=(
                self.wrongful_coalitions_cleared + other.wrongful_coalitions_cleared
            ),
            wrongful_coalitions_converted=(
                self.wrongful_coalitions_converted + other.wrongful_coalitions_converted
            ),
            ejections=self.ejections + other.ejections,
            role_correct_ejections=(
                self.role_correct_ejections + other.role_correct_ejections
            ),
            crew_authored_role_correct_ejections=(
                self.crew_authored_role_correct_ejections
                + other.crew_authored_role_correct_ejections
            ),
            guard_rewrites_by_reason=dict(sorted(reasons.items())),
        )


def authored_ballot_diagnostics(
    *,
    ballots: Sequence[VoteBallot],
    roles: Mapping[PlayerId, Role],
    ejected_player_id: PlayerId | None,
) -> AuthoredBallotCounts:
    """One unit's authored layer, counted. Pure; never called mid-run.

    Three readings, all off the ballots the meeting recorded and the ground
    truth the run record holds in memory:

    * **Per voter role** — how many ejections that role AUTHORED, how many of
      them reached the tally, and (for the crew) how many named the impostor
      and how many named a crewmate. An authored ejection the meeting layer
      normalized as an ``invalid_target`` named neither — the id preserved
      there is a hallucination, a dead player or the voter — so it is counted
      in its own column and left out of every other one
      (:func:`_authored_a_legal_target`).
    * **The coalition funnel** — an authored coalition is two or more ballots
      authored at the SAME target in one unit. It is CORRECT when that target
      is the impostor and WRONGFUL otherwise. ``cleared`` and ``converted`` are
      different counts: a coalition clears when every one of its ballots
      reached the tally, and converts when every one of them reached it ON THE
      AUTHORED TARGET, which an under-gate redirect broke on the recorded bytes
      this instrument grades (ruling D6 of 2026-09-19 retired that redirect).
    * **The ejection** — whether it was role-correct, and whether every
      recorded ballot naming the ejected player was its voter's own rather than
      a guard's rewrite (the ``voter_authored`` condition the primary outcome
      already applies, read here on the ejection rather than on the ballot).

    ``roles`` is the unit's own ground truth, the same mapping
    :func:`count_leaking_turns` reads; nothing downstream of the run sees it.
    """

    reasons: Counter[str] = Counter(dict.fromkeys(BALLOT_REWRITE_REASONS, 0))
    impostors = {player for player, role in roles.items() if role == "IMPOSTOR"}
    crew_authored = 0
    crew_naming_impostor = 0
    crew_cleared = 0
    crew_on_crew = 0
    crew_illegal = 0
    impostor_authored = 0
    impostor_cleared = 0
    impostor_illegal = 0
    for ballot in ballots:
        # The marker STACK, not the typed field: see _TARGET_REWRITE_MARKERS.
        for reason in ballot_rewrites_that_fired(ballot):
            reasons[reason] += 1
        if not _authored_an_ejection(ballot):
            continue
        authored = authored_ballot_target(ballot)
        voter_is_impostor = roles[ballot.voter] == "IMPOSTOR"
        if not _authored_a_legal_target(ballot, roles):
            if voter_is_impostor:
                impostor_illegal += 1
            else:
                crew_illegal += 1
            continue
        if voter_is_impostor:
            impostor_authored += 1
            impostor_cleared += int(_reached_the_tally(ballot))
            continue
        crew_authored += 1
        crew_cleared += int(_reached_the_tally(ballot))
        if authored in impostors:
            crew_naming_impostor += 1
        else:
            crew_on_crew += 1

    by_target: dict[str, list[VoteBallot]] = {}
    for ballot in ballots:
        if not _authored_an_ejection(ballot):
            continue
        # A coalition is a bloc the meeting could have ejected somebody on, so
        # an illegal authored target forms none: two voters naming one
        # hallucinated id agreed about nobody.
        if not _authored_a_legal_target(ballot, roles):
            continue
        target = authored_ballot_target(ballot)
        assert target is not None  # _authored_an_ejection said so
        by_target.setdefault(target, []).append(ballot)
    correct = [0, 0, 0]
    wrongful = [0, 0, 0]
    for target, bloc in by_target.items():
        if len(bloc) < 2:
            continue
        row = correct if target in impostors else wrongful
        row[0] += 1
        row[1] += int(all(_reached_the_tally(ballot) for ballot in bloc))
        row[2] += int(all(_converted(ballot) for ballot in bloc))

    ejections = 0
    role_correct = 0
    crew_authored_role_correct = 0
    if ejected_player_id is not None:
        ejections = 1
        if ejected_player_id in impostors:
            role_correct = 1
            naming = [
                ballot for ballot in ballots if ballot.target == ejected_player_id
            ]
            crew_authored_role_correct = int(
                bool(naming)
                and all(ballot.guard_rewrite_reason is None for ballot in naming)
            )

    return AuthoredBallotCounts(
        crew_authored_ejects=crew_authored,
        crew_authored_naming_impostor=crew_naming_impostor,
        crew_authored_ejects_cleared=crew_cleared,
        crew_on_crew_authored_ejects=crew_on_crew,
        units_with_crew_on_crew=int(crew_on_crew > 0),
        crew_authored_illegal_targets=crew_illegal,
        impostor_authored_ejects=impostor_authored,
        impostor_authored_ejects_cleared=impostor_cleared,
        impostor_authored_illegal_targets=impostor_illegal,
        correct_coalitions=correct[0],
        correct_coalitions_cleared=correct[1],
        correct_coalitions_converted=correct[2],
        wrongful_coalitions=wrongful[0],
        wrongful_coalitions_cleared=wrongful[1],
        wrongful_coalitions_converted=wrongful[2],
        ejections=ejections,
        role_correct_ejections=role_correct,
        crew_authored_role_correct_ejections=crew_authored_role_correct,
        guard_rewrites_by_reason=dict(sorted(reasons.items())),
    )


class AuthoredEjectRow(BaseModel):
    """One voter role's authored ejections, and what the gate did with them."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Role
    authored: int
    cleared: int
    coerced: int
    #: Authored ejections at a target the meeting could not act on, reported
    #: here and counted nowhere else — not in ``authored``, and so not in the
    #: precision denominator either. Defaulted, so a row written before this
    #: column existed parses and reads zero.
    illegal_targets: int = 0


#: The precision half of the block, and the harm half it may never be reported
#: without. Two named sets so the rule is a lookup rather than a sentence in a
#: docstring, and so the refusal can say which key is missing.
_PRECISION_KEYS: Final[tuple[str, ...]] = (
    "crew_authored_ejects",
    "crew_authored_naming_impostor",
    "crew_authored_precision_p",
)
_HARM_KEYS: Final[tuple[str, ...]] = (
    "crew_on_crew_authored_ejects",
    "units_with_crew_on_crew",
)


class AuthoredBallotDiagnostics(BaseModel):
    """One arm's labelled DIAGNOSTICS block: the authored layer, summed.

    Defaulted throughout, so an ``ArmSummary`` written before this block existed
    still parses and reads an empty one rather than a fabricated reading. What
    is NOT optional is the pairing: a payload carrying the crew per-ballot
    precision and dropping the harm counter beside it is refused, because the
    precision alone is the figure that reads as an achievement and the harm
    counter is the one that says what the same authoring bought.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    note: str = AUTHORED_DIAGNOSTICS_NOTE
    # The precision pair and its harm counter, which travel together.
    crew_authored_ejects: int = 0
    crew_authored_naming_impostor: int = 0
    crew_authored_precision_p: float = 1.0
    crew_on_crew_authored_ejects: int = 0
    units_with_crew_on_crew: int = 0
    # The gate's survival rate, by the voter's hidden role.
    by_voter_role: tuple[AuthoredEjectRow, ...] = ()
    # The funnel. ``cleared`` and ``converted`` are different counts.
    correct_coalitions: int = 0
    correct_coalitions_cleared: int = 0
    correct_coalitions_converted: int = 0
    wrongful_coalitions: int = 0
    wrongful_coalitions_cleared: int = 0
    wrongful_coalitions_converted: int = 0
    # The ejections, against the 1/3 chance rate of a three-player table.
    ejections: int = 0
    role_correct_ejections: int = 0
    role_correct_p: float = 1.0
    crew_authored_role_correct_ejections: int = 0
    crew_authored_role_correct_p: float = 1.0
    guard_rewrites_by_reason: Mapping[str, int] = {}

    @model_validator(mode="before")
    @classmethod
    def _harm_counter_travels_with_the_precision(cls, data: Any) -> Any:
        """Refuse a block that reports the precision and drops the harm counter.

        Checked on the PAYLOAD rather than after construction, so it catches a
        caller that assembled the block by hand and a report re-read from a file
        alike; an empty block carries neither half and is not a claim about
        anything.
        """

        if not isinstance(data, Mapping):
            return data
        if not any(key in data for key in _PRECISION_KEYS):
            return data
        missing = [key for key in _HARM_KEYS if key not in data]
        if missing:
            raise ValueError(
                "the crew per-ballot precision is never reported without its "
                "harm counter; this block is missing " + ", ".join(missing)
            )
        return data


def authored_ballot_block(
    counts: AuthoredBallotCounts, *, note: str = AUTHORED_DIAGNOSTICS_NOTE
) -> AuthoredBallotDiagnostics:
    """One arm's summed counts, with the three chance-rate tails computed on them.

    The tails are computed HERE rather than per unit because a p value is not
    additive: the question is asked of the arm's whole count.

    ``note`` is what the block says about itself, and it defaults to the live
    evaluation's: that path publishes the block beside the primary outcome and
    its note says so. A calibration passes its own mode's
    (:data:`CALIBRATION_DIAGNOSTICS_NOTES`), because a payload that reports no
    outcome may not carry a paragraph telling a reader the counts sit beside
    one.
    """

    # CREWMATE first, the order the calibration's role split already reports.
    by_role: tuple[tuple[Role, int, int, int], ...] = (
        (
            "CREWMATE",
            counts.crew_authored_ejects,
            counts.crew_authored_ejects_cleared,
            counts.crew_authored_illegal_targets,
        ),
        (
            "IMPOSTOR",
            counts.impostor_authored_ejects,
            counts.impostor_authored_ejects_cleared,
            counts.impostor_authored_illegal_targets,
        ),
    )
    return AuthoredBallotDiagnostics(
        note=note,
        crew_authored_ejects=counts.crew_authored_ejects,
        crew_authored_naming_impostor=counts.crew_authored_naming_impostor,
        crew_authored_precision_p=one_sided_binomial_p(
            counts.crew_authored_naming_impostor,
            counts.crew_authored_ejects,
            CREW_PRECISION_NULL,
        ),
        crew_on_crew_authored_ejects=counts.crew_on_crew_authored_ejects,
        units_with_crew_on_crew=counts.units_with_crew_on_crew,
        by_voter_role=tuple(
            AuthoredEjectRow(
                role=role,
                authored=authored,
                cleared=cleared,
                coerced=authored - cleared,
                illegal_targets=illegal,
            )
            for role, authored, cleared, illegal in by_role
        ),
        correct_coalitions=counts.correct_coalitions,
        correct_coalitions_cleared=counts.correct_coalitions_cleared,
        correct_coalitions_converted=counts.correct_coalitions_converted,
        wrongful_coalitions=counts.wrongful_coalitions,
        wrongful_coalitions_cleared=counts.wrongful_coalitions_cleared,
        wrongful_coalitions_converted=counts.wrongful_coalitions_converted,
        ejections=counts.ejections,
        role_correct_ejections=counts.role_correct_ejections,
        role_correct_p=one_sided_binomial_p(
            counts.role_correct_ejections, counts.ejections, EJECTION_CHANCE_NULL
        ),
        crew_authored_role_correct_ejections=(
            counts.crew_authored_role_correct_ejections
        ),
        crew_authored_role_correct_p=one_sided_binomial_p(
            counts.crew_authored_role_correct_ejections,
            counts.ejections,
            EJECTION_CHANCE_NULL,
        ),
        guard_rewrites_by_reason=dict(counts.guard_rewrites_by_reason),
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
    # The bounded retry's counts, reported beside the meeting-internal defaults
    # and for the same reason: a call this arm had to send twice is spend and a
    # provider fault, and without these counts a retried run is indistinguishable
    # from a clean one. ``calls`` above includes the unaccounted attempts, whose
    # rows carry zero tokens and the ``UNACCOUNTED_ATTEMPT_MODEL`` marker, so
    # subtracting ``unaccounted_attempts`` from it gives the completions.
    retried_calls: int
    unaccounted_attempts: int
    attempts_by_trigger: Mapping[str, int]
    units_with_retries: int
    # Calls on which the provider's own ``finish_reason`` and this instrument's
    # ``output_tokens >= max_tokens`` inference contradicted each other. A
    # counted anomaly beside the two above, and reported for the same reason:
    # the truncation stop fires on either signal, so without this count a run
    # whose two readings disagree is indistinguishable from one whose readings
    # agree. Zero on an arm whose provider reported no reading at all, because
    # an absent reading contradicts nothing.
    cap_signal_disagreements: int
    # The per-call distribution the count above collapses: how many of this
    # arm's ledger rows carried each ``finish_reason`` the provider reported,
    # with an absent reading keyed ``"null"`` the way the role split already
    # keys it. Reported beside the disagreement count because that count is one
    # aggregate and this is the reading it was derived from — a run whose
    # provider maps no reading at all and one whose completions all stopped
    # cleanly are indistinguishable without it. Defaulted, so a report written
    # before this field parses and reads an EMPTY distribution rather than a
    # fabricated ``"stop"`` on every call.
    finish_reasons: Mapping[str, int] = {}
    # The labelled authored-ballot block. Defaulted for the same reason, and
    # never a decision input: :data:`AUTHORED_DIAGNOSTICS_NOTE`, which the block
    # itself carries, says so in the report.
    authored_diagnostics: AuthoredBallotDiagnostics = AuthoredBallotDiagnostics()
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
    records: Sequence[UnitTelemetry], *, arm: ArmName
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
    report: BaseModel, prefixes: Iterable[HeldOutPrefix]
) -> None:
    """Refuse a report that carries any held-out prefix content.

    Checks every string in the dumped report for each prefix's canonical JSON
    and for each of its steps' canonical JSON — the step is the smaller unit and
    the one a careless summary would reach for. This is the guard behind "the
    runner opens no prefix, prints none".

    Takes any report model rather than the evaluation's, so the calibration's
    goes through the same check. One guard, because a second payload shape with
    its own guard is how the first one's rule stops applying.
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


def _every_key_in(value: object) -> list[str]:
    """Every mapping KEY in a dumped payload, at any depth.

    Keys and not values, deliberately: :data:`CALIBRATION_3_CAVEAT` and
    :data:`CALIBRATION_3_AUTHORED_DIAGNOSTICS_NOTE` both SAY that no primary
    outcome is reported, and a guard that searched values would refuse the
    sentence that makes the promise.
    """

    if isinstance(value, Mapping):
        found: list[str] = []
        for key, item in value.items():
            if isinstance(key, str):
                found.append(key)
            found.extend(_every_key_in(item))
        return found
    if isinstance(value, (list, tuple)):
        return [key for item in value for key in _every_key_in(item)]
    return []


#: Fields no calibration payload may carry, whatever its mode. The first three
#: are the frozen analysis's own vocabulary (:data:`PRIMARY_OUTCOME`,
#: :data:`DECISION_RULE`, :class:`PairedResult`), and a calibration that carried
#: any of them would be an evaluation wearing a calibration's schema.
CALIBRATION_FORBIDDEN_FIELDS: Final[tuple[str, ...]] = (
    "paired",
    "primary_outcome",
    "supported_correct_ejections",
    PRIMARY_OUTCOME,
    "decision",
    "decision_rule",
    "p_exact",
)


def assert_calibration_reports_no_outcome(payload: Mapping[str, object]) -> None:
    """Refuse a calibration payload carrying a paired statistic or an outcome.

    ``extra="forbid"`` on :class:`CalibrationReport` already refuses a field
    that arrived unnoticed at CONSTRUCTION. This is the same rule over the
    PAYLOAD, which is what a reader — or the refresh path, or a later card
    re-reading a committed archive — actually holds, and it is the rule the
    2026-09-18 mode's clause states in words: this sitting computes no paired
    statistic, evaluates no decision rule and reports no primary outcome.

    Run on every mode rather than on the third alone. A guard applied on one
    path only is a guard that has already started to drift, and no calibration
    has ever been allowed to publish an outcome.
    """

    present = sorted(
        {key for key in _every_key_in(payload) if key in CALIBRATION_FORBIDDEN_FIELDS}
    )
    if present:
        raise CalibrationReportsAnOutcome(
            "a calibration reports no outcome and computes no paired "
            "statistic, and this payload carries " + ", ".join(present)
        )


def _summarize_arm(
    arm: ArmName,
    *,
    grades: Sequence[UnitGrade],
    usage: ArmUsage,
    telemetry: Sequence[UnitTelemetry],
) -> ArmSummary:
    own = [grade for grade in grades if grade.arm == arm]
    verdicts: Counter[str] = Counter()
    for grade in own:
        verdicts.update(grade.verdict_counts())
    own_records = [unit for unit in telemetry if unit.arm == arm]
    defaults = DefaultedAttempts()
    attempts = TransportAttempts()
    diagnostics = AuthoredBallotCounts()
    for record in own_records:
        defaults = defaults.plus(record.defaults())
        attempts = attempts.plus(record.attempts())
        diagnostics = diagnostics.plus(record.diagnostics)
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
            1 for record in own_records if record.defaults().total > 0
        ),
        retried_calls=attempts.retried_calls,
        unaccounted_attempts=attempts.unaccounted_attempts,
        attempts_by_trigger=dict(attempts.by_trigger),
        units_with_retries=sum(
            1 for record in own_records if record.attempts().unaccounted_attempts > 0
        ),
        cap_signal_disagreements=usage.cap_signal_disagreements,
        finish_reasons=dict(usage.finish_reasons),
        authored_diagnostics=authored_ballot_block(diagnostics),
        prompt_versions=dict(_one_prompt_version_set(telemetry, arm=arm)),
        calls=usage.calls,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_usd=usage.cost_usd,
        model_work_seconds=usage.model_work_seconds,
    )


# ---------------------------------------------------------------------------
# The per-unit checkpoint and the outcome-blind resume
# ---------------------------------------------------------------------------

#: The payload version. A checkpoint written by another shape of this file is
#: refused rather than migrated: a resumed run has to be the same run.
CHECKPOINT_SCHEMA: Final[str] = "fresh-deduction-checkpoint/1"

#: The files this module NAMES as deciding what an arm shows a model and what a
#: payload may say: this instrument, the meeting layer that drives the turns and
#: the ballots, the memory store the prompts render from, the loader that builds
#: the Jinja environment and selects the renderers, and the game module the
#: instrument drives a prefix and its meeting through. A resume across a change
#: to any of them would pair units drawn from two different instruments, so the
#: checkpoint records their digests and :func:`assert_checkpoint_matches`
#: refuses a mismatch.
#:
#: A NAMED set, not a transitive import closure, and the rest of the run path is
#: covered elsewhere rather than here: the frozen INPUTS by the held-out
#: manifest's own digest, the 22 generator sources by that manifest's
#: ``source_sha256`` block and the freeze test that regenerates it
#: (``verify_frozen_set`` deliberately does not re-compare it), and a rendering
#: change that bumped a prompt version by :func:`_one_prompt_version_set` when
#: the report is built. ``orchestrator/game.py`` is in both sets, because the
#: freeze covers it only for changes that move a generated prefix.
ARM_SURFACE_SOURCES: Final[tuple[str, ...]] = (
    "agents/memory/store.py",
    "agents/strategic/prompts/loader.py",
    "experiments/fresh_deduction_instrument.py",
    "meetings/manager.py",
    "meetings/public_accounts.py",
    "meetings/schemas.py",
    "orchestrator/game.py",
)

#: The prompt directory both arms render from; every file in it is hashed.
ARM_SURFACE_PROMPT_DIR: Final[str] = "agents/strategic/prompts/qwen3_6_27b"


def arm_surface_digests(repo_root: Path = _REPO_ROOT) -> Mapping[str, str]:
    """``{repository path: sha256}`` over the NAMED arm surface.

    The named surface is :data:`ARM_SURFACE_SOURCES` plus every file of the
    prompt directory both arms render from — the constant says what it covers
    and where the rest of the run path is covered instead. Sorted and complete
    over that set: a template ADDED to the prompt directory changes this mapping
    as surely as one edited, because a family that gained a file is a family
    that renders differently.
    """

    digests: dict[str, str] = {}
    paths = [repo_root / name for name in ARM_SURFACE_SOURCES]
    prompts = repo_root / ARM_SURFACE_PROMPT_DIR
    if not prompts.is_dir():
        raise InstrumentError(
            f"the prompt set both arms render from is missing: {prompts}; this "
            "run cannot say what it would render"
        )
    paths.extend(sorted(path for path in prompts.iterdir() if path.is_file()))
    for path in paths:
        if not path.is_file():
            raise InstrumentError(
                f"an arm-surface source is missing: {path}; this run cannot say "
                "what it would render"
            )
        relative = path.resolve().relative_to(repo_root.resolve()).as_posix()
        digests[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return MappingProxyType(dict(sorted(digests.items())))


class CarriedUsage(BaseModel):
    """One unit's spend, as the checkpoint carries it into the next sitting."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    model_work_seconds: float = 0.0
    #: Carried for the same reason the counts are: the calls themselves are
    #: gone with the sitting that made them, so a resumed run that dropped this
    #: would report an arm's disagreements as the tail's alone. Defaulted, so a
    #: checkpoint written before this field parses and reads zero.
    cap_signal_disagreements: int = 0
    #: And the distribution that count collapses, carried for the same reason:
    #: a resumed run whose earlier sitting saw a reading the tail never sees
    #: would otherwise report the tail's readings as the run's. Defaulted, so a
    #: checkpoint written before this field parses and reads an empty one.
    finish_reasons: Mapping[str, int] = {}

    @model_validator(mode="after")
    def _a_populated_distribution_is_one_row_per_call(self) -> CarriedUsage:
        """Refuse a carried distribution that is not what it claims to be.

        A checkpoint is a FILE, and a resumed run merges what it reads here
        straight into the arm summary the report is built from, so a malformed
        row would be reported as a reading nobody saw. The EMPTY mapping stays
        legal — that is what a record written before the field reads — but a
        populated one has to be a count of calls: no negative reading, and one
        row per call of this same row's ``calls``.
        """

        if not self.finish_reasons:
            return self
        negative = sorted(
            reason for reason, count in self.finish_reasons.items() if count < 0
        )
        if negative:
            raise ValueError(
                "a finish-reason distribution counts calls, so no reading is "
                "negative; this one carries " + ", ".join(negative)
            )
        total = sum(self.finish_reasons.values())
        if total != self.calls:
            raise ValueError(
                "a populated finish-reason distribution is one row per call: "
                f"this one sums to {total} over {self.calls} calls"
            )
        return self

    def arm_usage(self) -> ArmUsage:
        return ArmUsage(
            calls=self.calls,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            cost_usd=self.cost_usd,
            model_work_seconds=self.model_work_seconds,
            cap_signal_disagreements=self.cap_signal_disagreements,
            finish_reasons=dict(self.finish_reasons),
        )


class UnitTelemetry(BaseModel):
    """Everything the REPORT needs from one unit that is not a grade.

    Counts and version markers: what the meeting layer substituted, what the
    wrapper had to send again, what the unit spent, which models answered and
    which template versions rendered it. No prompt, no prefix, no ballot and no
    role — those live on :class:`UnitRecord`, which is never serialized.

    It exists because a resumed run has to summarise units it did not run. The
    report was previously built by walking the in-memory records; it is now
    built by walking these, and one is projected from each record as it
    finishes (:func:`unit_telemetry`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    arm: ArmName
    defaulted_turns: int = 0
    defaulted_votes: int = 0
    defaults_by_validation: int = 0
    defaults_by_deadline: int = 0
    degraded_openings: int = 0
    retried_calls: int = 0
    unaccounted_attempts: int = 0
    attempts_by_trigger: Mapping[str, int] = {}
    prompt_versions: Mapping[str, str] = {}
    model_ids: tuple[str, ...] = ()
    usage: CarriedUsage = CarriedUsage()
    #: The authored layer of this unit's ballots, projected here at unit close
    #: for the same reason everything else on this model is: the report is built
    #: by walking these rows, and a resumed run restores the earlier ones from
    #: the checkpoint alone. Defaulted, so a checkpoint written before this
    #: field parses and reads zeros rather than a fabricated reading.
    diagnostics: AuthoredBallotCounts = AuthoredBallotCounts()

    def defaults(self) -> DefaultedAttempts:
        return DefaultedAttempts(
            defaulted_turns=self.defaulted_turns,
            defaulted_votes=self.defaulted_votes,
            by_validation=self.defaults_by_validation,
            by_deadline=self.defaults_by_deadline,
            degraded_openings=self.degraded_openings,
        )

    def attempts(self) -> TransportAttempts:
        return TransportAttempts(
            retried_calls=self.retried_calls,
            unaccounted_attempts=self.unaccounted_attempts,
            by_trigger=MappingProxyType(dict(sorted(self.attempts_by_trigger.items()))),
        )


def unit_telemetry(record: UnitRecord) -> UnitTelemetry:
    """Project one finished unit onto the counts a report and a resume need."""

    usage = ArmUsage().plus(record.calls)
    return UnitTelemetry(
        seed=record.seed,
        arm=record.arm,
        defaulted_turns=record.defaults.defaulted_turns,
        defaulted_votes=record.defaults.defaulted_votes,
        defaults_by_validation=record.defaults.by_validation,
        defaults_by_deadline=record.defaults.by_deadline,
        degraded_openings=record.defaults.degraded_openings,
        retried_calls=record.transport_attempts.retried_calls,
        unaccounted_attempts=record.transport_attempts.unaccounted_attempts,
        attempts_by_trigger=dict(record.transport_attempts.by_trigger),
        prompt_versions=dict(record.prompt_versions),
        model_ids=tuple(sorted({call.model for call in record.calls})),
        diagnostics=authored_ballot_diagnostics(
            ballots=record.ballots,
            roles=record.roles,
            ejected_player_id=record.ejected_player_id,
        ),
        usage=CarriedUsage(
            calls=usage.calls,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cost_usd=usage.cost_usd,
            model_work_seconds=usage.model_work_seconds,
            cap_signal_disagreements=usage.cap_signal_disagreements,
            finish_reasons=dict(usage.finish_reasons),
        ),
    )


class CheckpointBallot(BaseModel):
    """One ballot's support verdict, as the checkpoint carries it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    voter: str
    target: str
    cited_turn_id: str | None
    cited_observation_id: str | None
    verdict: SupportVerdict
    guard_rewrite_reason: str | None


class CheckpointUnit(BaseModel):
    """One graded unit, flattened for the file and restorable from it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    arm: ArmName
    outcome: str
    stop: Literal["terminal", "partial"]
    ejected_player_id: str | None
    ejected_role: Role | None
    role_correct: bool
    supported_correct_ejection: bool
    naming_ballots: int
    off_target_citations: int
    supported: tuple[CheckpointBallot, ...]
    telemetry: UnitTelemetry

    def grade(self) -> UnitGrade:
        """The grade this row was written from, rebuilt exactly."""

        return UnitGrade(
            seed=self.seed,
            arm=self.arm,
            outcome=self.outcome,
            stop=self.stop,
            supported=tuple(
                SupportedGrade(
                    voter=ballot.voter,
                    target=ballot.target,
                    cited_turn_id=ballot.cited_turn_id,
                    cited_observation_id=ballot.cited_observation_id,
                    verdict=ballot.verdict,
                    guard_rewrite_reason=ballot.guard_rewrite_reason,
                )
                for ballot in self.supported
            ),
            privileged=PrivilegedGrade(
                ejected_player_id=self.ejected_player_id,
                ejected_role=self.ejected_role,
                role_correct=self.role_correct,
                supported_correct_ejection=self.supported_correct_ejection,
                naming_ballots=self.naming_ballots,
                off_target_citations=self.off_target_citations,
            ),
        )


def checkpoint_unit(grade: UnitGrade, telemetry: UnitTelemetry) -> CheckpointUnit:
    """Flatten one graded unit and its telemetry into one checkpoint row."""

    if (grade.seed, grade.arm) != (telemetry.seed, telemetry.arm):
        raise InstrumentError(
            f"a checkpoint row would pair the grade of seed {grade.seed} on "
            f"{grade.arm} with the telemetry of seed {telemetry.seed} on "
            f"{telemetry.arm}"
        )
    return CheckpointUnit(
        seed=grade.seed,
        arm=grade.arm,
        outcome=grade.outcome,
        stop=grade.stop,
        ejected_player_id=grade.privileged.ejected_player_id,
        ejected_role=grade.privileged.ejected_role,
        role_correct=grade.privileged.role_correct,
        supported_correct_ejection=grade.privileged.supported_correct_ejection,
        naming_ballots=grade.privileged.naming_ballots,
        off_target_citations=grade.privileged.off_target_citations,
        supported=tuple(
            CheckpointBallot(
                voter=ballot.voter,
                target=ballot.target,
                cited_turn_id=ballot.cited_turn_id,
                cited_observation_id=ballot.cited_observation_id,
                verdict=ballot.verdict,
                guard_rewrite_reason=ballot.guard_rewrite_reason,
            )
            for ballot in grade.supported
        ),
        telemetry=telemetry,
    )


class AbandonedArm(BaseModel):
    """One arm's charged-but-ungraded spend, as the checkpoint carries it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    arm: ArmName
    usage: CarriedUsage = CarriedUsage()
    retried_calls: int = 0
    unaccounted_attempts: int = 0
    attempts_by_trigger: Mapping[str, int] = {}

    def attempts(self) -> TransportAttempts:
        return TransportAttempts(
            retried_calls=self.retried_calls,
            unaccounted_attempts=self.unaccounted_attempts,
            by_trigger=MappingProxyType(dict(sorted(self.attempts_by_trigger.items()))),
        )


class AbandonedSpend(BaseModel):
    """The calls a stop charged inside the pair it interrupted.

    A checkpoint is written at PAIR boundaries, so calls made after the last
    boundary belong to no graded unit: the arm the stop landed in, and the arm
    of the same prefix that finished beside it without its partner. They bought
    nothing and they were still billed, which is exactly the case a resume
    exists for — the stops the diagnosis of 2026-09-13 records were transport
    exhaustion and a budget refusal, and both land mid-pair.

    So a resumed run charges them again against the run ceilings: the ceilings
    bound what the RUN spends, the stopped sitting spent these, and a resume
    that dropped them would run its tail under a budget larger than the
    authorization by up to one pair per stop — unboundedly, because nothing
    bounds how often a provider may drop.

    It accumulates. A checkpoint written by a resumed sitting carries the
    earlier sittings' abandoned calls beside its own, so the third sitting of a
    run charges what the first two abandoned as well as what they graded.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    arms: tuple[AbandonedArm, ...] = ()
    #: The model-work seconds those calls burned. Not the sum of the rows above:
    #: the clock is charged per ATTEMPT, and an attempt that returned nothing is
    #: on no captured call.
    model_work_seconds: float = 0.0

    def usage_by_arm(self) -> Mapping[str, ArmUsage]:
        return MappingProxyType({row.arm: row.usage.arm_usage() for row in self.arms})

    def attempts_by_arm(self) -> Mapping[str, TransportAttempts]:
        return MappingProxyType({row.arm: row.attempts() for row in self.arms})


def abandoned_spend(
    carried: AbandonedSpend,
    *,
    arms: Sequence[ArmName],
    usage_by_arm: Mapping[str, ArmUsage],
    attempts_by_arm: Mapping[str, TransportAttempts],
    model_work_seconds: float,
) -> AbandonedSpend:
    """``carried`` plus one more stop's ungraded calls, summed per arm.

    ``arms`` supplies the names, so a row is only ever built for an arm this run
    knows; an arm carried in but not run here keeps its row.
    """

    names: list[ArmName] = list(arms)
    names.extend(row.arm for row in carried.arms if row.arm not in names)
    usage = dict(carried.usage_by_arm())
    attempts = dict(carried.attempts_by_arm())
    rows: list[AbandonedArm] = []
    for name in names:
        spend = usage.get(name, ArmUsage()).merged(
            usage_by_arm.get(name, ArmUsage()),
        )
        tally = attempts.get(name, TransportAttempts()).plus(
            attempts_by_arm.get(name, TransportAttempts()),
        )
        if spend == ArmUsage() and tally == TransportAttempts():
            continue
        rows.append(
            AbandonedArm(
                arm=name,
                usage=CarriedUsage(
                    calls=spend.calls,
                    input_tokens=spend.input_tokens,
                    output_tokens=spend.output_tokens,
                    cost_usd=spend.cost_usd,
                    model_work_seconds=spend.model_work_seconds,
                    cap_signal_disagreements=spend.cap_signal_disagreements,
                    finish_reasons=dict(spend.finish_reasons),
                ),
                retried_calls=tally.retried_calls,
                unaccounted_attempts=tally.unaccounted_attempts,
                attempts_by_trigger=dict(tally.by_trigger),
            )
        )
    return AbandonedSpend(
        arms=tuple(rows),
        model_work_seconds=carried.model_work_seconds + model_work_seconds,
    )


class RunCheckpoint(BaseModel):
    """What a stopped run may be continued from, and nothing more.

    Written after every completed PAIRED seed — both arms of one prefix — so a
    resume never begins mid-pair and the design's pairing cannot be broken by a
    stop. It carries the identity of everything a resumed run must still be
    (the execution manifest, the frozen set, the arm surface), the budgets the
    first sitting spent, and the graded results of the units it finished.

    The budgets are the whole of what was spent, not the graded part of it. A
    stop lands mid-pair, and the calls it made there are on
    :attr:`abandoned` rather than on any unit row; one final checkpoint is
    written on the stop path to record them. :meth:`usage_by_arm` is the graded
    half alone, and :func:`run_instrument` charges both.

    It is not an interim analysis. Nothing in the run path reads a grade off it:
    :func:`next_seeds_after` takes the SEEDS it lists and nothing else, and no
    stop condition anywhere in this module consults one. The grades are in the
    file because a resumed run has to be able to report the units it did not
    run, not because anything decides on them.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = CHECKPOINT_SCHEMA
    provider: str
    manifest_sha256: str
    held_out_manifest_sha256: str
    arm_surface_sha256: Mapping[str, str]
    limits: RunLimits
    sampling: SamplingConfig
    completed_seeds: tuple[int, ...]
    units: tuple[CheckpointUnit, ...]
    elapsed_seconds: float
    model_work_seconds: float
    #: What the stops charged inside the pairs they interrupted. Defaulted
    #: empty, because a checkpoint written at a pair boundary has abandoned
    #: nothing yet.
    abandoned: AbandonedSpend = AbandonedSpend()

    def usage_by_arm(self) -> Mapping[str, ArmUsage]:
        """The GRADED spend, per arm.

        The units this file carries, and only those. What a stop abandoned
        mid-pair is on :attr:`abandoned`, which a resume charges beside this:
        the two are kept apart because one of them bought units and the other
        bought nothing, and a report that summed them silently could not say
        which.
        """

        totals: dict[str, ArmUsage] = {}
        for unit in self.units:
            totals[unit.arm] = totals.get(unit.arm, ArmUsage()).merged(
                unit.telemetry.usage.arm_usage()
            )
        return MappingProxyType(totals)

    def charged_usage_by_arm(self) -> Mapping[str, ArmUsage]:
        """Everything the earlier sittings spent: graded plus abandoned."""

        totals = dict(self.usage_by_arm())
        for arm, spend in self.abandoned.usage_by_arm().items():
            totals[arm] = totals.get(arm, ArmUsage()).merged(spend)
        return MappingProxyType(totals)

    def charged_model_work_seconds(self) -> float:
        """The clock the earlier sittings burned, graded attempts and abandoned."""

        return self.model_work_seconds + self.abandoned.model_work_seconds


def write_checkpoint(path: Path, checkpoint: RunCheckpoint) -> None:
    """Write the checkpoint atomically, refusing one that carries input bytes.

    Atomic because the file is rewritten after every paired seed and a run
    killed mid-write would otherwise leave the only record of a sitting
    truncated. The leak check is the same rule the report is held to: a
    checkpoint is an artifact of the run, so the legacy body handle may not
    ride it any more than it may ride a report.
    """

    payload = checkpoint.model_dump(mode="json")
    leaked = legacy_body_handles(_every_string_in(payload))
    if leaked:
        raise PrefixBytesLeaked(
            "the checkpoint carries a legacy body handle: "
            + ", ".join(sorted(set(leaked)))
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")
    temporary.replace(path)


def read_checkpoint(path: Path) -> RunCheckpoint:
    """Load a checkpoint, or refuse the file for saying what it is not."""

    if not path.is_file():
        raise ResumeNotAuthorized(f"there is no checkpoint at {path}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ResumeNotAuthorized(f"{path} is not a checkpoint: {exc}") from exc
    # Bound before the refusal, not inside it: a file holding a JSON list or a
    # bare string is exactly the shape this guard exists for, and reading
    # ``.get`` off it while wording the refusal would raise AttributeError
    # instead — an incidental failure where AGENTS.md requires a named one.
    schema = loaded.get("schema_version") if isinstance(loaded, dict) else None
    if schema != CHECKPOINT_SCHEMA:
        raise ResumeNotAuthorized(
            f"{path} carries schema {schema!r}, not "
            f"{CHECKPOINT_SCHEMA!r}; a resumed run is the same run"
        )
    try:
        return RunCheckpoint.model_validate(loaded)
    except ValidationError as exc:
        raise ResumeNotAuthorized(f"{path} is not a usable checkpoint: {exc}") from exc


def assert_checkpoint_matches(
    checkpoint: RunCheckpoint,
    *,
    provider: str,
    limits: RunLimits,
    sampling: SamplingConfig,
    # Either verified record, because the fake-provider rehearsal is what proves
    # the resume works and it draws the ARCHIVE. What is compared is the record
    # this sitting verified against the one the first sitting did, and that
    # question is the same for both readers; which record a run is allowed to
    # draw at all is settled one level up, by the reader it calls.
    frozen: VerifiedPrefixRecord,
    repo_root: Path = _REPO_ROOT,
) -> None:
    """Refuse to continue a run that would not be the same run.

    Every comparison is an identity, not a preference: the manifest that
    authorized the first sitting, the freeze that supplied its inputs, the bytes
    that rendered its arms, the limits and the sampling configuration it drew
    under, and the provider it ran against. A difference in any of them makes
    the two sittings two runs, and pairing their units would be a comparison
    across instruments rather than across arms.
    """

    manifest = (repo_root / EXECUTION_MANIFEST_PATH).resolve()
    if not manifest.is_file():
        raise ResumeNotAuthorized(f"execution manifest is missing: {manifest}")
    committed = hashlib.sha256(manifest.read_bytes()).hexdigest()
    if checkpoint.manifest_sha256 != committed:
        raise ResumeNotAuthorized(
            "the checkpoint was written under execution manifest "
            f"{checkpoint.manifest_sha256}, and the committed one is "
            f"{committed}: the document that authorized that sitting is not "
            "this one"
        )
    if checkpoint.held_out_manifest_sha256 != frozen.manifest_sha256:
        raise ResumeNotAuthorized(
            "the checkpoint was written over held-out freeze "
            f"{checkpoint.held_out_manifest_sha256}, and this run verified "
            f"{frozen.manifest_sha256}: the inputs moved between the sittings"
        )
    surface = arm_surface_digests(repo_root)
    if dict(checkpoint.arm_surface_sha256) != dict(surface):
        moved = sorted(
            name
            for name in set(surface) | set(checkpoint.arm_surface_sha256)
            if checkpoint.arm_surface_sha256.get(name) != surface.get(name)
        )
        raise ResumeNotAuthorized(
            "the arm surface moved between the sittings, so the resumed units "
            "would not be drawn from the instrument the finished ones were: "
            + ", ".join(moved)
        )
    if checkpoint.provider != provider:
        raise ResumeNotAuthorized(
            f"the checkpoint ran against provider {checkpoint.provider!r} and "
            f"this run asks for {provider!r}"
        )
    if checkpoint.limits != limits:
        raise ResumeNotAuthorized(
            "the checkpoint ran under different limits; a resumed run carries "
            "the first sitting's budgets, so it runs under its ceilings too"
        )
    if checkpoint.sampling != sampling:
        raise ResumeNotAuthorized(
            "the checkpoint drew at a different sampling configuration; the "
            "two sittings would not be one sample"
        )
    known = set(frozen.accepted_seeds)
    unknown = sorted(seed for seed in checkpoint.completed_seeds if seed not in known)
    if unknown:
        raise ResumeNotAuthorized(
            "the checkpoint reports seeds this freeze does not accept: "
            + ", ".join(str(seed) for seed in unknown)
        )


def next_seeds_after(
    checkpoint: RunCheckpoint, prefixes: Sequence[HeldOutPrefix]
) -> tuple[HeldOutPrefix, ...]:
    """The unrendered tail of the ascending list, and only the tail.

    Outcome-blind by construction: it reads the SEEDS the checkpoint lists — the
    completed ones and the ones its unit rows name — and the order the run draws
    in, and nothing else on it. A completed seed that is not a PREFIX of the
    ascending list is refused rather than skipped: the run order is part of the
    design, and a hole in it is a checkpoint this module did not write.

    A seed the checkpoint carries but this run would not draw is refused too,
    rather than ignored. ``prefixes`` is truncated by ``--units``, so a resume
    asked for fewer units than the checkpoint finished would otherwise return an
    empty tail and report every carried unit anyway — a report naming more units
    than were requested, with no run behind the difference.
    """

    done = set(checkpoint.completed_seeds)
    carried = done | {unit.seed for unit in checkpoint.units}
    seeds = [prefix.seed for prefix in prefixes]
    outside = sorted(seed for seed in carried if seed not in set(seeds))
    if outside:
        raise ResumeNotAuthorized(
            "the checkpoint carries seeds this run would not draw: "
            + ", ".join(str(seed) for seed in outside)
            + "; a resumed run reports the units the stopped one finished, so "
            "it cannot be narrower than the checkpoint it continues"
        )
    finished = [seed for seed in seeds if seed in done]
    if finished != seeds[: len(finished)]:
        raise ResumeNotAuthorized(
            "the checkpoint's completed seeds are not a prefix of the run "
            "order; this run draws seeds ascending and a resume continues at "
            "the next unrendered one"
        )
    return tuple(prefixes[len(finished) :])


def unit_replay_path(output_dir: Path, *, arm: ArmName, seed: int) -> Path:
    """Where one unit's replay is recorded.

    Named once: :func:`run_unit` writes it and
    :func:`assert_the_tail_can_be_recorded` looks for it, and a gate that
    guessed the other's spelling would pass a directory it should refuse.
    """

    return output_dir / f"{arm}-seed-{seed}.jsonl"


def assert_the_tail_can_be_recorded(
    *,
    output_dir: Path,
    prefixes: Sequence[HeldOutPrefix],
    arms: Sequence[ArmName],
) -> None:
    """Refuse a resume whose directory already holds a replay of a seed to come.

    A stop inside a unit leaves that unit's partial recording behind, so a
    second sitting pointed at the first one's ``--output-dir`` reaches the
    recorder's own refusal (``orchestrator/recording.py``:
    :class:`~orchestrator.replay.ReplayLog.AlreadyExistsError`) — but only after
    the resume gates have passed and, on a metered provider, after the tail has
    begun to spend. This says so first, names the file, and costs one ``stat``
    per unit. A resumed sitting writes into a fresh directory; ``force`` is not
    offered, because replacing a held-out unit's replay is a decision, not a
    default.
    """

    occupied: list[str] = []
    for prefix in prefixes:
        for arm in arms:
            path = unit_replay_path(output_dir, arm=arm, seed=prefix.seed)
            if path.exists():
                occupied.append(path.name)
    if occupied:
        raise ResumeNotAuthorized(
            "the output directory already holds a recording for a seed this "
            "sitting has still to run: "
            + ", ".join(sorted(occupied))
            + f" under {output_dir}. A resumed sitting writes into a fresh "
            "directory: the stop left the unit it was inside half-recorded, and "
            "that file is evidence of the stop rather than something to "
            "overwrite"
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
    attempts_by_arm: dict[str, TransportAttempts] = field(default_factory=dict)
    completed: int = 0
    #: The same two tallies restricted to the calls made SINCE the last
    #: checkpoint was written. A stop writes these into the checkpoint as
    #: abandoned spend: the pair they belong to was never graded, so no unit row
    #: carries them, and a resumed run that did not charge them would run its
    #: tail under a budget the stopped sitting had already eaten into.
    pending_usage_by_arm: dict[str, ArmUsage] = field(default_factory=dict)
    pending_attempts_by_arm: dict[str, TransportAttempts] = field(default_factory=dict)

    def charge(
        self,
        arm: ArmName,
        calls: Sequence[CapturedCall],
        attempts: TransportAttempts = TransportAttempts(),
    ) -> None:
        self.usage_by_arm[arm] = self.usage_by_arm.get(arm, ArmUsage()).plus(calls)
        self.attempts_by_arm[arm] = self.attempts_by_arm.get(
            arm, TransportAttempts()
        ).plus(attempts)
        self.pending_usage_by_arm[arm] = self.pending_usage_by_arm.get(
            arm, ArmUsage()
        ).plus(calls)
        self.pending_attempts_by_arm[arm] = self.pending_attempts_by_arm.get(
            arm, TransportAttempts()
        ).plus(attempts)

    def pair_completed(self) -> None:
        """The pair boundary has passed, so nothing is ungraded any more."""

        self.pending_usage_by_arm.clear()
        self.pending_attempts_by_arm.clear()


@dataclass(frozen=True)
class _RunHarness:
    """The four objects that bound a sitting: one wiring, two callers.

    :func:`run_instrument` and :func:`run_calibration` spend under different
    ceilings on different inputs, and they must spend them the same WAY — one
    wrapper enforcing the per-call caps and the model-work window, one run-level
    budget, one elapsed deadline. Built here so the calibration cannot measure a
    run wired differently from the one it is sizing.
    """

    client: _InstrumentClient
    run_budget: GameBudget
    deadline: RunDeadline
    work_clock: _ModelWorkClock


def _build_harness(
    *,
    client: LLMClient | None,
    limits: RunLimits,
    sampling: SamplingConfig,
    invocation: LiveRunInvocation | None,
    truncation_is_a_measurement: bool = False,
) -> _RunHarness:
    """Wire one sitting's client, budget and two clocks from its limits.

    ``truncation_is_a_measurement`` is the second calibration's mode and is
    defaulted OFF, so the evaluation's two entry points — :func:`run_instrument`
    and :func:`run_dry` — cannot reach it without naming it, and neither does.
    """

    work_clock = _ModelWorkClock(max_seconds=limits.model_work_seconds)
    return _RunHarness(
        client=_InstrumentClient(
            client if client is not None else DryRunProvider(),
            work_clock=work_clock,
            turn_max_tokens=sampling.turn_max_tokens,
            vote_max_tokens=sampling.vote_max_tokens,
            truncation_is_a_measurement=truncation_is_a_measurement,
            # A live run is bound to the model the invocation names; a dry run
            # has no served model to bind, and its fixture says so in the
            # report's ``model_ids`` and its caveat.
            expected_model=None if invocation is None else invocation.model,
        ),
        run_budget=GameBudget(
            max_cost_usd=limits.max_cost_usd,
            max_input_tokens=limits.run_max_input_tokens,
            max_output_tokens=limits.run_max_output_tokens,
        ),
        deadline=RunDeadline(seconds=limits.elapsed_seconds),
        work_clock=work_clock,
    )


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
    checkpoint_path: Path | None = None,
    resume: RunCheckpoint | None = None,
) -> InstrumentReport:
    """Run both arms over the frozen set, sequentially, and grade the result.

    Order of operations is load-bearing. The authorization gate and the
    client-type check run before anything else, the frozen set is verified before
    a unit runs, the arms run paired seed by seed, and every grader runs only
    after the unit it grades has FINISHED — after the last one, or, when a
    checkpoint is being written, after both arms of a completed pair.

    ``checkpoint_path`` writes the per-unit checkpoint a stopped run may be
    continued from — after every completed pair, and once more on the stop path
    so the pair a stop interrupted leaves its spend behind. ``resume`` is one,
    already read and already matched against this tree
    (:func:`assert_checkpoint_matches`). A resumed run continues at the next
    unrendered seed, carries the earlier sittings' whole spend — graded units
    and abandoned pairs alike — into both the run budget and the model-work
    clock, and reports the finished units beside the fresh ones. It writes into
    a directory of its own: a replay already on disk for a seed still to run is
    refused rather than overwritten.

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
    # The inputs, read by the reader that matches what this run is. A live run
    # draws a held-out set and refuses an archive; the offline rehearsal draws
    # the archive and refuses a set still to be spent. Since 2026-09-19 this
    # tree holds only the archive, so `fake` is the only provider that gets
    # past this line at all — the closing gate above having already refused
    # every other one.
    frozen = (
        verify_archived_set(repo_root)
        if provider == "fake"
        else verify_frozen_set(repo_root)
    )
    prefixes = frozen.prefixes if units is None else frozen.prefixes[:units]
    arms = instrument_arms()
    planned = len(prefixes) * len(arms)
    carried_grades: list[UnitGrade] = []
    carried_telemetry: list[UnitTelemetry] = []
    completed_seeds: list[int] = []
    remaining = prefixes
    if resume is not None:
        assert_resume_is_authorized(provider=provider, repo_root=repo_root)
        assert_checkpoint_matches(
            resume,
            provider=provider,
            limits=limits,
            sampling=sampling,
            frozen=frozen,
            repo_root=repo_root,
        )
        remaining = next_seeds_after(resume, prefixes)
        assert_the_tail_can_be_recorded(
            output_dir=output_dir,
            prefixes=remaining,
            arms=[arm.name for arm in arms],
        )
        completed_seeds = list(resume.completed_seeds)
        carried_grades = [unit.grade() for unit in resume.units]
        carried_telemetry = [unit.telemetry for unit in resume.units]

    harness = _build_harness(
        client=client, limits=limits, sampling=sampling, invocation=live_invocation
    )
    work_clock = harness.work_clock
    instrument_client = harness.client
    run_budget = harness.run_budget
    deadline = harness.deadline
    output_dir.mkdir(parents=True, exist_ok=True)

    state = _RunState()
    records: list[UnitRecord] = []
    grades: list[UnitGrade] = list(carried_grades)
    telemetry: list[UnitTelemetry] = list(carried_telemetry)
    started = time.monotonic()
    # The elapsed wall of the sittings BEFORE this one. The deadline itself is
    # per sitting — it bounds a process, and a resumed run is a new one — but
    # what the record reports is the run's total, so the two are kept apart
    # here rather than conflated.
    carried_elapsed = 0.0 if resume is None else resume.elapsed_seconds
    # What the earlier sittings spent on pairs they never finished. Carried
    # forward through every checkpoint this sitting writes, so a run stopped
    # twice charges both stops rather than only the last.
    carried_abandoned = AbandonedSpend() if resume is None else resume.abandoned
    if resume is not None:
        # The earlier sittings' spend, charged before this one's first call: a
        # resumed run continues under the same ceilings, so what the stopped run
        # charged is charged again here rather than forgotten. BOTH halves —
        # the units it graded and the pair its stop abandoned — because the
        # ceilings bound what the run spent and it spent both. A carried total
        # already past a cap raises out of ``charge``: a run that exhausted its
        # budget is not resumable, which is the correct answer.
        for arm_name, carried in resume.charged_usage_by_arm().items():
            state.usage_by_arm[arm_name] = carried
            run_budget.charge(
                usage=TokenUsage(
                    input_tokens=carried.input_tokens,
                    output_tokens=carried.output_tokens,
                ),
                cost_usd=carried.cost_usd,
            )
        for unit in carried_telemetry:
            state.attempts_by_arm[unit.arm] = state.attempts_by_arm.get(
                unit.arm, TransportAttempts()
            ).plus(unit.attempts())
        for arm_name, tally in resume.abandoned.attempts_by_arm().items():
            state.attempts_by_arm[arm_name] = state.attempts_by_arm.get(
                arm_name, TransportAttempts()
            ).plus(tally)
        state.completed = len(carried_telemetry)
        work_clock.charge(resume.charged_model_work_seconds())
    # The clock reading at the last checkpoint — or at the start of this sitting,
    # which is the same thing for a resume. What the clock has run past it is
    # what a stop would abandon.
    work_at_boundary = work_clock.seconds

    def _checkpoint_now(abandoned: AbandonedSpend, *, graded_seconds: float) -> None:
        if checkpoint_path is None:
            return
        write_checkpoint(
            checkpoint_path,
            RunCheckpoint(
                provider=provider,
                manifest_sha256=hashlib.sha256(
                    (repo_root / EXECUTION_MANIFEST_PATH).read_bytes()
                ).hexdigest(),
                held_out_manifest_sha256=frozen.manifest_sha256,
                arm_surface_sha256=dict(arm_surface_digests(repo_root)),
                limits=limits,
                sampling=sampling,
                completed_seeds=tuple(completed_seeds),
                units=tuple(
                    checkpoint_unit(grade, unit)
                    for grade, unit in zip(grades, telemetry, strict=True)
                ),
                elapsed_seconds=carried_elapsed + time.monotonic() - started,
                model_work_seconds=graded_seconds,
                abandoned=abandoned,
            ),
        )

    for prefix in remaining:
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
            # quieter. ``BaseException`` IS caught, but only far enough to
            # account for what the interrupted pair had already bought: see the
            # re-raise below.
            except BaseException as exc:
                # The stopped unit's calls are still in the client. They were
                # spent, so they are charged into the partial accounting before
                # it is reported — "retains partial evidence and unresolved
                # accounting" means the spend that bought nothing, too.
                state.charge(
                    arm.name,
                    instrument_client.take(),
                    instrument_client.take_attempts(),
                )
                # And into the checkpoint, as the spend of a pair no unit row
                # will ever carry. Without this final write the next sitting
                # would rebuild its run budget from the last PAIR boundary and
                # silently forgive everything the stop had already charged
                # against the ceilings — up to one whole pair per stop, and a
                # transport that drops can stop a run again and again.
                _checkpoint_now(
                    abandoned_spend(
                        carried_abandoned,
                        arms=[each.name for each in arms],
                        usage_by_arm=state.pending_usage_by_arm,
                        attempts_by_arm=state.pending_attempts_by_arm,
                        model_work_seconds=work_clock.seconds - work_at_boundary,
                    ),
                    graded_seconds=work_at_boundary
                    - carried_abandoned.model_work_seconds,
                )
                if not isinstance(exc, Exception):
                    # An interrupt is still NOT a run stop: it is not reported
                    # as a PartialRun, it is not given a ``reason``, and it
                    # leaves this function as itself. What it now also does is
                    # leave the two lines above behind it. The owner's
                    # resumption clause names "a process crash" as resumable
                    # "with the interrupted unit's spend and model-work time
                    # carried", and a Ctrl-C, a SIGTERM or a SystemExit that
                    # unwinds this frame spent exactly as much as a transport
                    # failure did; forgiving it would be the same silent
                    # forgiveness the final write exists to prevent. The stop
                    # classes that run no code at all — SIGKILL, an OOM kill, a
                    # power loss — write nothing and carry nothing, which is the
                    # limitation the manifest's dated clause section states in
                    # the runner's own terms.
                    raise
                raise InstrumentAborted(
                    PartialRun(
                        reason=f"{type(exc).__name__}: {exc}",
                        completed_units=state.completed,
                        planned_units=planned,
                        usage_by_arm=dict(state.usage_by_arm),
                        elapsed_seconds=(carried_elapsed + time.monotonic() - started),
                        model_work_seconds=work_clock.seconds,
                        attempts_by_arm=dict(state.attempts_by_arm),
                    )
                ) from exc
            state.charge(arm.name, record.calls, record.transport_attempts)
            state.completed += 1
            records.append(record)
        # The pair is complete, so the seed is: both arms of one prefix ran, and
        # a checkpoint written here can never be resumed from inside a pair.
        # Grading happens at this boundary rather than mid-unit — the graders
        # are pure functions over finished records and no stop condition reads
        # one — because a resumed run has to be able to report units it did not
        # itself run.
        completed_seeds.append(prefix.seed)
        for record in records[-len(arms) :]:
            grades.append(grade_unit(record))
            telemetry.append(unit_telemetry(record))
        # Nothing is abandoned at a pair boundary, so the file carries only what
        # the earlier sittings abandoned, and the clock it records is the graded
        # one: total minus what those stops burned.
        _checkpoint_now(
            carried_abandoned,
            graded_seconds=work_clock.seconds - carried_abandoned.model_work_seconds,
        )
        work_at_boundary = work_clock.seconds
        state.pair_completed()

    report = InstrumentReport(
        provider=provider,
        model_ids=tuple(
            sorted({model for unit in telemetry for model in unit.model_ids})
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
                telemetry=telemetry,
            )
            for arm in arms
        ),
        paired=paired_result(grades),
        elapsed_seconds=carried_elapsed + time.monotonic() - started,
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
    client: LLMClient | None = None,
    checkpoint_path: Path | None = None,
    resume: RunCheckpoint | None = None,
) -> InstrumentReport:
    """The fake-provider mechanics check. Refuses a live invocation outright.

    Writes every replay into a temporary directory when none is given, so a dry
    run leaves no prefix bytes behind at all.

    ``client`` is how a rehearsal hands in an offline double — the replay double
    that reproduces the archived usage profile, say. It is still held to
    :func:`assert_client_matches_provider`, so only a
    :class:`~llm.fake_provider.FakeProvider` can be passed here and the fake
    label cannot be worn by a metered client.
    """

    if live_invocation is not None:
        raise LiveRunNotAuthorized(
            "the dry run is the mechanics check and never the authorized run; "
            "it takes no LiveRunInvocation"
        )
    if output_dir is not None:
        return run_instrument(
            output_dir=output_dir,
            client=client,
            provider="fake",
            repo_root=repo_root,
            units=units,
            limits=limits,
            sampling=sampling,
            checkpoint_path=checkpoint_path,
            resume=resume,
        )
    with TemporaryDirectory() as directory:
        return run_instrument(
            output_dir=Path(directory),
            client=client,
            provider="fake",
            repo_root=repo_root,
            units=units,
            limits=limits,
            sampling=sampling,
            checkpoint_path=checkpoint_path,
            resume=resume,
        )


# ---------------------------------------------------------------------------
# The development calibration: what the provider actually charges
# ---------------------------------------------------------------------------
#
# Everything below measures SPEND and nothing else. No grader runs, no paired
# test is computed and no meeting outcome is reported: the five seeds are a
# converted band's, already rendered once by a stopped run, and what they are
# asked is what a call and a unit cost on this endpoint.

#: The payload version of a calibration output, so a reader — the profile
#: refresh below, or a later card — knows what it is holding.
CALIBRATION_SCHEMA: Final[str] = "fresh-deduction-calibration/1"

#: What a call of a unit is. Spelled here rather than imported from the
#: rehearsal double, which is a test module this one may not depend on.
CallType = Literal["turn", "ballot"]

#: The two schedules, in the order a summary reports them.
CALL_TYPES: Final[tuple[CallType, ...]] = ("turn", "ballot")

#: The dispositions that are SAMPLES of what a call costs: a completion that
#: came back, and one the provider billed for and then refused. The other two
#: carry zero tokens because nothing was reported, so averaging them in would
#: describe a cheaper endpoint than the one being measured.
COMPLETED_DISPOSITIONS: Final[frozenset[str]] = frozenset(
    {"resolved", "billed_and_refused"}
)

PERCENTILE_RULE: Final[str] = (
    "p95 is the nearest-rank percentile of the sample sorted ascending: the "
    "value at index ceil(0.95 x n) - 1. No interpolation, because every value "
    "in the sample is a token count some call was actually charged and a "
    "number between two of them is not one of those."
)

#: The multiple of the largest measured unit a proposed per-unit ceiling leaves.
CEILING_PROPOSAL_UNIT_MULTIPLE: Final[int] = 3

#: The margin a proposed run-level ceiling leaves over the measured mean.
CEILING_PROPOSAL_RUN_MARGIN: Final[float] = 1.5

#: Proposed ceilings are rounded UP to this granularity, so the numbers an
#: authorization card would carry read as decisions rather than as residues.
CEILING_PROPOSAL_ROUNDING: Final[int] = 1_000

CEILING_PROPOSAL_RULE: Final[str] = (
    "The per-unit OUTPUT ceiling is max(the reservation schedule, "
    f"{CEILING_PROPOSAL_UNIT_MULTIPLE} x the largest unit measured): it is "
    "enforced on what a unit RESERVES, so it has to clear that schedule before "
    "anything else. The per-unit INPUT ceiling is "
    f"{CEILING_PROPOSAL_UNIT_MULTIPLE} x the largest unit measured — the same "
    "multiple with no reservation floor to clear, because no pre-flight "
    "reserves an input cap. Each run-level ceiling is the whole design's unit "
    f"count x the measured MEAN unit x {CEILING_PROPOSAL_RUN_MARGIN}, raised to "
    "that unit count x the largest unit measured where the mean rule falls "
    "below it: that product is the floor `assert_limits_are_feasible` enforces, "
    "and a proposed ceiling the instrument would refuse is not a proposal. The "
    "run-level OUTPUT floor carries ONE further per-call turn cap on top of "
    "that product — the in-flight headroom the gate itself adds, because the "
    "run's last call is reserved against the run budget after the run has "
    "charged everything before it. Without that term a proposal reproduces the "
    "defect of 2026-09-14, whose 459,000 for a hundred units is exactly a "
    "hundred times its own largest unit and 4,096 short of what those hundred "
    "units reserve. The INPUT dimension takes no such term, its pre-flight "
    "being the prompt's own estimated length rather than a cap. "
    f"Every figure is rounded up to the next {CEILING_PROPOSAL_ROUNDING:,} "
    "tokens. The feasibility check the proposal reports is run against the "
    "CALIBRATION's own measured maxima rather than against whatever the tree's "
    "committed usage profile happens to hold, because the question a proposal "
    "answers is whether these ceilings can pay for the run THIS sitting "
    "measured; the same check against the committed profile is reported beside "
    "it, so a sitting whose units are larger than the profile's says so. This "
    "is a proposal and authorizes nothing: the ceilings a run "
    "spends under are the owner's, on a card, and this instrument keeps "
    "refusing any limits but the ones it is handed."
)

CALIBRATION_CAVEAT: Final[str] = (
    "A spend measurement on development inputs, not an evaluation. No grader "
    "ran, no paired statistic was computed and no meeting outcome is reported: "
    "the primary outcome, the decision rule and the minimum actionable effect "
    "are untouched, and no unit of this calibration counts towards them."
)

#: The 2026-09-18 mode's own caveat, beside the one above rather than an edit of
#: it: that string is what the two spent sittings were published under and it
#: stays byte-identical. This mode needs its own because it reports MORE than a
#: spend measurement — the authored-ballot diagnostics — and a reader meeting
#: those counts under a caveat that says "no meeting outcome is reported" would
#: be told something the payload contradicts. What has not changed is the half
#: that matters: no grader, no paired statistic, no decision rule and no primary
#: outcome.
CALIBRATION_3_CAVEAT: Final[str] = (
    "A spend and diagnostics measurement on development inputs, not an "
    "evaluation. What is reported: the token profile per arm, call type and "
    "hidden role; truncations as measurements carrying their finish reason; the "
    "role-leak column; and the aggregate authored-ballot and ejection "
    "diagnostics, as counts over the sitting and never per seed. What is NOT: "
    "no grader ran, no paired statistic was computed, no decision rule was "
    "evaluated and no primary outcome is reported. The primary outcome, the "
    "decision rule, the minimum actionable effect, the acceptable-tradeoff "
    "bound and the stop rule are untouched, and no unit of this calibration "
    "counts towards them. The diagnostics are read against predictions the "
    "manifest fixed BEFORE this sitting; none of them is a gate, and a missed "
    "prediction is neither a stop nor a verdict."
)

#: Which caveat each authorized mode publishes. A closed table beside the modes
#: for the same reason :data:`CALIBRATION_MODES` is one: a caveat chosen by an
#: ``if`` is a caveat a fourth mode can silently inherit.
CALIBRATION_CAVEATS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "2026-09-14": CALIBRATION_CAVEAT,
        "2026-09-15": CALIBRATION_CAVEAT,
        "2026-09-18": CALIBRATION_3_CAVEAT,
    }
)

if set(CALIBRATION_CAVEATS) != {
    mode.name for mode in CALIBRATION_MODES
}:  # pragma: no cover
    raise InstrumentError(
        "every authorized calibration mode needs its caveat here: a mode "
        "without one would publish somebody else's statement of what it "
        "measured"
    )

#: Which note the authored-ballot block carries in each mode that REPORTS one.
#: A closed table for the same reason the caveats are one, and keyed on the mode
#: rather than defaulted, because the default is the live evaluation's note: a
#: calibration that fell through to it would publish "they are reported beside
#: the primary outcome" on a payload whose own caveat says no primary outcome is
#: reported. A mode that reports no block is absent here, not mapped to a note.
CALIBRATION_DIAGNOSTICS_NOTES: Final[Mapping[str, str]] = MappingProxyType(
    {"2026-09-18": CALIBRATION_3_AUTHORED_DIAGNOSTICS_NOTE}
)


def assert_every_reporting_mode_has_its_note(
    notes: Mapping[str, str],
    modes: Sequence[CalibrationMode] = CALIBRATION_MODES,
) -> None:
    """Refuse a table that does not name exactly the modes reporting a block.

    A function rather than a bare ``if`` so the invariant can be planted: the
    failure it guards is a fourth mode switching ``reports_authored_diagnostics``
    on and silently inheriting the live evaluation's note.
    """

    reporting = {mode.name for mode in modes if mode.reports_authored_diagnostics}
    if set(notes) != reporting:
        raise InstrumentError(
            "every calibration mode that reports the authored-ballot block "
            "needs its OWN note here, and a mode that reports none needs no "
            f"entry: this table names {sorted(notes)} against "
            f"{sorted(reporting)}"
        )
    if AUTHORED_DIAGNOSTICS_NOTE in notes.values():
        raise InstrumentError(
            "a calibration may not publish the live evaluation's note: that "
            "string says the counts are reported beside the primary outcome, "
            "and a calibration reports none"
        )


assert_every_reporting_mode_has_its_note(CALIBRATION_DIAGNOSTICS_NOTES)


def _percentile(values: Sequence[int], fraction: float) -> int:
    """The nearest-rank percentile of ``values``. See :data:`PERCENTILE_RULE`."""

    if not values:
        raise ValueError("a percentile of no samples is not a number")
    if not 0.0 < fraction <= 1.0:
        raise ValueError(f"a percentile fraction is in (0, 1], got {fraction}")
    ordered = sorted(values)
    return ordered[math.ceil(fraction * len(ordered)) - 1]


def _rounded_up(value: float, granularity: int = CEILING_PROPOSAL_ROUNDING) -> int:
    """``value`` rounded up to the next whole ``granularity``."""

    if granularity < 1:
        raise ValueError(f"a rounding granularity is at least 1, got {granularity}")
    return math.ceil(value / granularity) * granularity


def calibration_call_type(call: CapturedCall, sampling: SamplingConfig) -> CallType:
    """Which kind of call one ledger row is, from the cap it asked for.

    The two caps differ and :class:`_InstrumentClient` refuses any other, so the
    request's own cap says which schedule a call belongs to without the ledger
    carrying a second copy of what the meeting layer already decided. Anything
    else raises rather than defaulting to a kind: a row filed under the wrong
    schedule moves both of that schedule's statistics.
    """

    if call.max_tokens == sampling.turn_max_tokens:
        return "turn"
    if call.max_tokens == sampling.vote_max_tokens:
        return "ballot"
    raise InstrumentError(
        f"a captured call asked for {call.max_tokens} output tokens, which is "
        f"neither the turn cap {sampling.turn_max_tokens} nor the ballot cap "
        f"{sampling.vote_max_tokens}; this calibration cannot say which "
        "schedule it belongs to"
    )


# ---------------------------------------------------------------------------
# What the SECOND calibration reports: role, prose length, truncation, leak
# ---------------------------------------------------------------------------
#
# The first calibration measured tokens. The fourth run's stop was not a token
# fact: one ballot in thirteen IMPOSTOR-authored candidate draws ran past its
# 1,024-token cap, and the mechanism the diagnosis of 2026-09-15 found is
# role-conditioned — an impostor that opens by naming its own role or its own
# kill writes a longer rationale than a crewmate does. So everything below
# splits by the author's hidden role, and measures the character lengths of the
# fields that carry prose beside the token counts, because a cap is spent on
# characters.
#
# Counts and lengths only. No prose, no prompt, no prefix and no outcome
# reaches any of these models, and
# :func:`assert_report_holds_no_prefix_bytes` runs over the payload either way.

#: The prose fields a completion can spend its cap on, named once. One of them
#: lives on a ballot and two on a turn.
ProseField = Literal["rationale_text", "claims_reason", "free_text"]

#: The fields a ballot's author can write prose into, and a turn's.
BALLOT_PROSE_FIELDS: Final[tuple[ProseField, ...]] = ("rationale_text",)
TURN_PROSE_FIELDS: Final[tuple[ProseField, ...]] = ("free_text", "claims_reason")

#: The order the role split reports its two roles in, so two runs of the same
#: measurement produce the same rows in the same order.
ROLE_SPLIT_ORDER: Final[tuple[Role, ...]] = ("CREWMATE", "IMPOSTOR")


def _claim_reason(claim: Claim) -> str | None:
    """A claim's free-text reason, or ``None`` for a kind that carries none.

    Matched on the claim type rather than read with a default, because an
    alibi genuinely has no ``reason`` field and a missing attribute is a fact
    about the schema rather than an empty string to average in.
    """

    if isinstance(claim, (AccusationClaim, CorroborationClaim)):
        return claim.reason
    return None


def _ballot_was_authored(ballot: VoteBallot) -> bool:
    """Whether a recorded ballot's rationale is the VOTER's, not the layer's.

    The meeting layer's shipped fail-soft substitutes a marked SKIP for a
    payload that failed schema validation and a deadline default for a ballot
    that never arrived, and both carry a rationale this layer wrote. Averaging
    those two in would measure the substitution rather than the draw — and in
    the second calibration's mode a TRUNCATED ballot is exactly one of them, so
    the field that must not be polluted is the one the mode exists to measure.

    The draw still counts: the truncation rate's denominator is impostor DRAWS,
    off the call ledger, and a fail-softed ballot is a draw that produced no
    rationale.
    """

    return (
        ballot.guard_rewrite_reason != "parse_default"
        and ballot.rationale_text != DEFAULT_VOTE_RATIONALE
    )


def _turn_was_authored(turn: MeetingTurn) -> bool:
    """Whether a recorded turn's text is the SPEAKER's, not the placeholder."""

    return turn.free_text not in frozenset(DEFAULT_TURN_FREE_TEXT.values())


# ---------------------------------------------------------------------------
# The pre-declared leak diagnostic (the diagnosis of 2026-09-15, decision 9)
# ---------------------------------------------------------------------------

ROLE_LEAK_RULE: Final[str] = (
    "A leaking turn is a COMMITTED public turn whose speaker is an IMPOSTOR "
    "and whose text states, in the first person and without attributing the "
    "statement to someone else, either that role or a kill that speaker "
    "committed. The roles are the unit's own ground truth, which the run "
    "record holds in memory and no listener sees. Three shapes decide it: a "
    "first-person role statement, a first-person kill statement, and the "
    "negative the diagnosis of 2026-09-15 counted out — an impostor REBUTTING "
    "an accusation against itself, which quotes the words without asserting "
    "them and is not counted. A statement that is SUPPOSED or ASKED rather "
    "than asserted — a conditional, a hypothetical or a question governing the "
    "words — is not counted either, for the same reason: the words are there "
    "and the assertion is not. A CREWMATE naming its own role is not counted "
    "either: every crewmate says so, and counting it would report the roster "
    "rather than a leak. A turn the meeting layer substituted is not counted, "
    "because its text is the layer's. The count is a REPORTED diagnostic and "
    "not a gate: the owner's reading of decision 9 on 2026-09-15 is that the "
    "leak does not block the next run on its own, which is what makes a "
    "reported column beside the primary outcome the right instrument for it. "
    "What the rule cannot do is read intent, and its guards see one sentence "
    "at a time: an impostor that confesses in words the two shapes do not "
    "match is missed, and an attribution, denial or supposition spread across "
    "two sentences is counted. So the figure is an ESTIMATE carrying error in "
    "BOTH directions and is not a floor, which is a further reason to read it "
    "beside the outcome rather than to gate on it."
)

#: The sentence this rule works in. A leak is decided inside one sentence,
#: because the attribution that makes a statement someone else's — a report of
#: another player's claim — sits in the same sentence as the words it quotes.
_SENTENCE_SPLIT: Final[re.Pattern[str]] = re.compile(r"[.!?\n]+")

#: A first-person statement of the IMPOSTOR role.
_SELF_ROLE_STATEMENT: Final[re.Pattern[str]] = re.compile(
    r"\bi(?:\s+am|'m|\s+was)\s+(?:the\s+|an?\s+)?(?:impostor|imposter|killer)\b",
    re.IGNORECASE,
)

#: A first-person statement of a kill. ``did it`` is in the set because the
#: fourth run's reference arm produced it verbatim as an admission; the others
#: are the words this game has for the act.
_SELF_KILL_STATEMENT: Final[re.Pattern[str]] = re.compile(
    r"\bi\s+(?:killed|stabbed|vented|did\s+it|was\s+the\s+one\s+who\s+killed)\b",
    re.IGNORECASE,
)

#: What stops the words that follow from being this speaker's own ASSERTION.
#: Searched in the part of the sentence BEFORE the match, which is where a
#: governor has to sit to govern it. Three families, and the third is the one
#: the review of 2026-09-15 found missing: a conditional, a hypothetical or a
#: question puts the words in play without asserting them ("if I am the
#: impostor, why would I report the body?"), and counting that as a confession
#: inflates the column in the direction the rule claims it cannot move. The
#: three question words are CROSSED with their four auxiliaries rather than
#: listed, so the interrogative family is complete by construction — a question
#: in the present or the past asserts as little as a modal one, and a fifth
#: auxiliary is one word here rather than three entries.
#: Crossed on 2026-09-18; :data:`ROLE_LEAK_RULE`'s own text is unchanged.
_NOT_AN_ASSERTION: Final[re.Pattern[str]] = re.compile(
    # Attributed to somebody else.
    r"\b(?:claim|claims|claimed|claiming|accuse\w*|accusation\w*|allege\w*|"
    r"say|says|said|suggest\w*|think|thinks|insist\w*|argue\w*|argument\w*|"
    # Denied.
    r"not|never|deny|denies|denied|nobody|"
    # Supposed, imagined or asked rather than said.
    r"if|unless|whether|suppose|supposes|supposed|supposing|assume|assumes|"
    r"assumed|assuming|imagine|imagines|imagining|pretend\w*|hypothetical\w*|"
    r"were\s+i|(?:why|how|what)\s+(?:would|do|does|did))\b",
    re.IGNORECASE,
)


def states_own_role_or_kill(text: str, *, role: Role) -> bool:
    """Whether ``text`` leaks the speaker's own hidden role or a kill it made.

    :data:`ROLE_LEAK_RULE` states the rule; this is it. Pure, deterministic and
    role-conditioned: a CREWMATE never matches, because the statement being
    counted is the one that costs the evaluation its validity.

    The words alone are not the leak — the ASSERTION is. So a match is counted
    only when nothing in front of it in the same sentence attributes it to
    somebody else, denies it, or merely supposes or asks it
    (:data:`_NOT_AN_ASSERTION`).
    """

    if role != "IMPOSTOR":
        return False
    for sentence in _SENTENCE_SPLIT.split(text):
        for pattern in (_SELF_ROLE_STATEMENT, _SELF_KILL_STATEMENT):
            found = pattern.search(sentence)
            if found is None:
                continue
            if _NOT_AN_ASSERTION.search(sentence[: found.start()]):
                # Someone else's words, a denial of them, or a supposition or
                # question that puts them in play without asserting them. The
                # fourth run's seed 7015 is the first case and the diagnosis
                # counted it out; the third is the review of 2026-09-15's.
                continue
            return True
    return False


def count_leaking_turns(record: UnitRecord) -> int:
    """How many of one unit's COMMITTED public turns leak their speaker's role.

    Over ``record.turns`` — what the transcript actually carries, which is what
    a later speaker and a later voter read — and off ``record.roles``, the
    ground truth the run record holds in memory and nothing downstream of it
    sees.
    """

    return sum(
        1
        for turn in record.turns
        if _turn_was_authored(turn)
        and states_own_role_or_kill(turn.free_text, role=record.roles[turn.speaker])
    )


#: A bracketed marker the meeting layer prepends to a rationale for display.
#: Stripped before the OPENING of a rationale is read, so a ballot the guard
#: annotated is judged on what its author wrote rather than on the annotation.
_LEADING_MARKER: Final[re.Pattern[str]] = re.compile(r"^\s*\[[^\]]*\]\s*")


def opens_with_a_self_tell(ballot: VoteBallot, *, role: Role) -> bool:
    """Whether an impostor's ballot OPENS by naming its own role or kill.

    The opening is the rationale's first sentence, after any bracketed marker
    the meeting layer prepended. "Opens" rather than "contains" because that is
    the shape the diagnosis measured — eleven of twelve impostor candidate
    ballots on the fourth run began with the confession — and because a
    rationale that reaches the same words after arguing for four hundred
    characters is a different behaviour.
    """

    if not _ballot_was_authored(ballot):
        return False
    opening = _SENTENCE_SPLIT.split(
        _LEADING_MARKER.sub("", ballot.rationale_text), maxsplit=1
    )[0]
    return states_own_role_or_kill(opening, role=role)


def count_self_telling_ballots(record: UnitRecord) -> int:
    """This unit's impostor-authored ballots that open with a self-tell."""

    return sum(
        1
        for ballot in record.ballots
        if record.roles[ballot.voter] == "IMPOSTOR"
        and opens_with_a_self_tell(ballot, role="IMPOSTOR")
    )


class LengthStats(BaseModel):
    """One prose field's character lengths, over the payloads that carried it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    field: ProseField
    #: Payloads the AUTHOR wrote, not draws: a fail-softed ballot is a draw
    #: that produced no rationale and contributes no sample here.
    samples: int
    mean: float
    p95: int
    max: int


class RoleSplitUsage(BaseModel):
    """One arm's one call kind as authored by one hidden role.

    The unit of account the fourth run's stop needed and the first calibration
    did not have: it measured tokens, not role. Counts and lengths only.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    arm: str
    call_type: CallType
    #: The AUTHOR's hidden role, off the unit's own ground truth.
    role: Role
    #: Completed ledger rows this role drew on this schedule. The truncation
    #: rate's denominator: a fail-softed ballot is still a draw.
    draws: int
    output_mean: float
    output_p95: int
    output_max: int
    #: Draws whose completion reached its cap on either signal
    #: (:func:`_truncation_signals`), and the provider's own word for each —
    #: ``null`` where it reported none.
    truncations: int
    truncations_by_finish_reason: Mapping[str, int]
    lengths: tuple[LengthStats, ...]


def _length_stats(field: ProseField, values: Sequence[int]) -> LengthStats | None:
    """One prose field's statistics, or ``None`` when nothing carried it."""

    if not values:
        return None
    return LengthStats(
        field=field,
        samples=len(values),
        mean=sum(values) / len(values),
        p95=_percentile(values, 0.95),
        max=max(values),
    )


def _role_of_call(call: CapturedCall, record: UnitRecord) -> Role:
    """The hidden role of the player one ledger row was drawn for, or a stop.

    Invalid input raises. A captured call the unit cannot attribute to a player
    it holds a role for cannot be split by role, and filing it under a default
    would move one of the two distributions this calibration exists to
    separate.
    """

    agent_id = call.agent_id
    if agent_id is None or PlayerId(agent_id) not in record.roles:
        raise InstrumentError(
            f"seed {record.seed}: a captured call names speaker {agent_id!r}, "
            "which this unit holds no hidden role for; the role split cannot "
            "say who drew it"
        )
    return record.roles[PlayerId(agent_id)]


def _prose_lengths_by_role(
    records: Sequence[UnitRecord],
) -> Mapping[tuple[Role, ProseField], list[int]]:
    """Every authored prose field's length, keyed by author role and field."""

    lengths: dict[tuple[Role, ProseField], list[int]] = {}

    def add(role: Role, field: ProseField, value: int) -> None:
        lengths.setdefault((role, field), []).append(value)

    for record in records:
        for ballot in record.ballots:
            if not _ballot_was_authored(ballot):
                continue
            add(
                record.roles[ballot.voter],
                "rationale_text",
                len(ballot.rationale_text),
            )
        for turn in record.turns:
            if not _turn_was_authored(turn):
                continue
            role = record.roles[turn.speaker]
            add(role, "free_text", len(turn.free_text))
            for claim in turn.claims:
                reason = _claim_reason(claim)
                if reason is not None:
                    add(role, "claims_reason", len(reason))
    return lengths


def _role_split_rows(
    arm: ArmName,
    *,
    records: Sequence[UnitRecord],
    sampling: SamplingConfig,
) -> tuple[RoleSplitUsage, ...]:
    """One arm's call schedules split by the author's hidden role."""

    own = [record for record in records if record.arm == arm]
    lengths = _prose_lengths_by_role(own)
    rows: list[RoleSplitUsage] = []
    for call_type in CALL_TYPES:
        fields = BALLOT_PROSE_FIELDS if call_type == "ballot" else TURN_PROSE_FIELDS
        for role in ROLE_SPLIT_ORDER:
            sample = [
                call
                for record in own
                for call in record.calls
                if call.disposition in COMPLETED_DISPOSITIONS
                and calibration_call_type(call, sampling) == call_type
                and _role_of_call(call, record) == role
            ]
            if not sample:
                # A role that drew nothing on this schedule is a fact, not a
                # bucket to average over.
                continue
            outputs = [call.output_tokens for call in sample]
            truncated = [
                call
                for call in sample
                if any(
                    _truncation_signals(
                        finish_reason=call.finish_reason,
                        output_tokens=call.output_tokens,
                        max_tokens=call.max_tokens,
                    )
                )
            ]
            by_reason: Counter[str] = Counter(
                "null" if call.finish_reason is None else call.finish_reason
                for call in truncated
            )
            rows.append(
                RoleSplitUsage(
                    arm=arm,
                    call_type=call_type,
                    role=role,
                    draws=len(sample),
                    output_mean=sum(outputs) / len(outputs),
                    output_p95=_percentile(outputs, 0.95),
                    output_max=max(outputs),
                    truncations=len(truncated),
                    truncations_by_finish_reason=dict(sorted(by_reason.items())),
                    lengths=tuple(
                        stats
                        for stats in (
                            _length_stats(field, lengths.get((role, field), []))
                            for field in fields
                        )
                        if stats is not None
                    ),
                )
            )
    return tuple(rows)


class CallTypeUsage(BaseModel):
    """One arm's one call kind: how many completions, and how big they ran."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    arm: str
    call_type: CallType
    #: Completions only (:data:`COMPLETED_DISPOSITIONS`); the attempts that
    #: reported nothing are counted on the arm rather than averaged in here.
    completions: int
    input_mean: float
    input_p95: int
    input_max: int
    output_mean: float
    output_p95: int
    output_max: int
    #: The cap these calls were drawn under, so a maximum can be read against
    #: the ceiling it was approaching.
    max_tokens: int


class CalibrationCall(BaseModel):
    """One completion, as the four counts a rehearsal needs to replay it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    arm: str
    #: The two boundary fields are the module's own Literals rather than plain
    #: strings, because this model is a PARSE boundary: ``--refresh-usage-profile``
    #: validates a calibration JSON through it and the rehearsal double keys a
    #: refusal off ``disposition == "billed_and_refused"`` exactly. A misspelled
    #: or later value typed as ``str`` would parse clean and replay a billed
    #: refusal as a resolved call, into the committed profile the feasibility
    #: gate's two calibrated constants are held to. Invalid input raises here.
    call_type: CallType
    input_tokens: int
    output_tokens: int
    disposition: CallDisposition
    #: The provider's own word for why this completion stopped, or null when it
    #: reported none — which is what every call in a calibration recorded
    #: before this field existed reads, because the reading was not captured
    #: then. Defaulted, and typed ``str | None`` rather than a Literal: it is
    #: the PROVIDER's vocabulary, not this module's, and a value this module
    #: does not know is a fact to record rather than a parse error.
    finish_reason: str | None = None


class CalibrationUnitUsage(BaseModel):
    """One unit's spend. Counts and identifiers only, and no outcome.

    The seed is here because the converted band's own committed record already
    publishes it. What is deliberately absent is what the meeting DID: this
    calibration measures cost, and publishing outcomes on inputs nothing may be
    tuned to is how a development set becomes a training set.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    arm: str
    attempts: int
    completions: int
    input_tokens: int
    output_tokens: int
    model_work_seconds: float
    defaulted_turns: int
    defaulted_votes: int
    charged_failed_attempts: int
    retried_calls: int
    unaccounted_attempts: int


class CalibrationArmUsage(BaseModel):
    """One arm's totals over the calibration, with its two call schedules."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    arm: str
    units: int
    attempts: int
    completions: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model_work_seconds: float
    #: Model-work seconds per ATTEMPT, retries and cut-off attempts included:
    #: a wall-clock limit is spent on the attempts the provider is held for,
    #: not only on the ones that answered.
    seconds_per_attempt: float
    by_call_type: tuple[CallTypeUsage, ...]
    mean_unit_input_tokens: float
    mean_unit_output_tokens: float
    max_unit_input_tokens: int
    max_unit_output_tokens: int
    # The meeting-internal fail-soft substitutions, off the replay rows the
    # runner wrote (:func:`count_defaulted_attempts`).
    defaulted_turns: int
    defaulted_votes: int
    defaults_by_validation: int
    defaults_by_deadline: int
    degraded_openings: int
    units_with_defaults: int
    #: Attempts the provider BILLED and then refused on its own schema
    #: validation, off this instrument's own call ledger. The same event also
    #: raises ``defaults_by_validation`` when the meeting layer substituted for
    #: it: the two count it at two layers rather than counting two things.
    charged_failed_attempts: int
    charged_failed_input_tokens: int
    charged_failed_output_tokens: int
    # The bounded retry's counts, and the attempts that bought nothing.
    retried_calls: int
    unaccounted_attempts: int
    aborted_attempts: int
    attempts_by_trigger: Mapping[str, int]
    #: The second calibration's own unit of account: this arm's two call
    #: schedules split by the AUTHOR's hidden role, with the prose-field
    #: lengths and the truncation counts. Empty on a mode that measures no
    #: role split, so the first calibration's committed shape still parses.
    by_role: tuple[RoleSplitUsage, ...] = ()
    #: Impostor-authored ballots whose rationale OPENS by naming that role or a
    #: kill (:func:`opens_with_a_self_tell`).
    self_telling_impostor_ballots: int = 0
    #: The pre-declared leak diagnostic (:data:`ROLE_LEAK_RULE`): committed
    #: public turns whose speaker stated its own hidden role or its own kill,
    #: and the units carrying any.
    leaking_turns: int = 0
    units_with_a_leaking_turn: int = 0
    #: The substrate levers this arm RESOLVED, as
    #: :func:`arm_lever_profile` reads them. Published because the 2026-09-18
    #: mode exists to measure a revision that lives behind a default-OFF lever,
    #: and a token profile whose reader cannot tell which surface produced it is
    #: a number without a subject. Empty on the two spent modes, whose committed
    #: outputs predate the field.
    resolved_levers: Mapping[str, str] = {}
    #: The authored-ballot DIAGNOSTICS block summed over this arm's units,
    #: carrying the note of the MODE that reported it
    #: (:data:`CALIBRATION_DIAGNOSTICS_NOTES`, and never the live evaluation's
    #: :data:`AUTHORED_DIAGNOSTICS_NOTE`). Counts only, never per seed.
    #:
    #: ``None`` — not an empty block — on a mode that reports none, which is
    #: both spent modes. An empty :class:`AuthoredBallotDiagnostics` is not
    #: empty in the payload: it carries a note, which is a paragraph about
    #: authored ejections, and publishing that beside the 2026-09-14 output's
    #: zeros would have the first calibration explaining a block it never
    #: measured. Absent means absent.
    authored_diagnostics: AuthoredBallotDiagnostics | None = None


class CeilingProposal(BaseModel):
    """Re-sized ceilings, computed from what was measured by a stated rule."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule: str
    #: The run the proposal is FOR: the whole held-out design's unit count, not
    #: the calibration's own ten.
    units: int
    reservation_schedule: int
    measured_max_unit_input_tokens: int
    measured_max_unit_output_tokens: int
    measured_mean_unit_input_tokens: float
    measured_mean_unit_output_tokens: float
    unit_max_input_tokens: int
    unit_max_output_tokens: int
    run_max_input_tokens: int
    run_max_output_tokens: int
    #: Whether :func:`assert_limits_are_feasible` accepts these four figures
    #: for the whole run, checked against the maxima THIS calibration measured.
    #: That is the proposal's own claim: these ceilings pay for a run of the
    #: units this sitting saw.
    clears_the_feasibility_gate: bool
    feasibility_refusal: str | None
    #: The same four figures against the CALIBRATED constants this tree carries
    #: — the largest unit the committed usage profile holds. False on a
    #: fixture-driven rehearsal, whose 66-token calls are a serialisation
    #: length rather than a measurement, and false on any sitting whose units
    #: ran smaller than the profile's; the refusal below says which in the
    #: gate's own words rather than leaving a reader to infer it. Defaulted, so
    #: an output written before this field existed still parses.
    clears_the_committed_profiles_gate: bool = False
    committed_profile_refusal: str | None = None


class CalibrationInputs(BaseModel):
    """Which development record the calibration drew, and how much of it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    record: str
    record_sha256: str
    status: str
    band_first_seed: int
    band_last_seed: int
    seeds: tuple[int, ...]
    accepted_in_record: int
    skipped_in_record: int


class CalibrationReport(BaseModel):
    """Aggregate spend only. No prompt, no prefix, no step, no outcome.

    ``extra="forbid"`` for the same reason :class:`InstrumentReport` carries it:
    a field that arrived unnoticed is a field nobody decided was publishable.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    report_schema: str
    provider: str
    model_ids: tuple[str, ...]
    execution_mode: str
    instrument_sha256: str
    prompt_set: str
    inputs: CalibrationInputs
    #: Every record the draw spanned, in draw order, each with its own sha256
    #: and the seeds taken from it. ``inputs`` is the first of them, kept as
    #: its own field because the first calibration drew exactly one record and
    #: its committed output — and the refresh path that reads it — names it
    #: there. Empty on a payload written before the draw could span records.
    input_records: tuple[CalibrationInputs, ...] = ()
    #: Which authorized mode of :data:`CALIBRATION_MODES` this sitting ran.
    #: Defaulted for the same reason: the first calibration's output predates
    #: the table that named it.
    mode: str = CALIBRATION_MODES[0].name
    limits: RunLimits
    sampling: SamplingConfig
    paired_seeds: int
    units: int
    arms: tuple[CalibrationArmUsage, ...]
    #: Every completion, as four counts each: the distribution rather than its
    #: summary, because the rehearsal double replays individual calls and a
    #: bucket collapsed to its mean would hand a 1,024-capped ballot a turn's
    #: length. Four counts are not a prompt and not a prefix.
    calls: tuple[CalibrationCall, ...]
    unit_usage: tuple[CalibrationUnitUsage, ...]
    proposal: CeilingProposal
    percentile_rule: str
    #: The leak diagnostic's rule, quoted in the output for the same reason
    #: :data:`PERCENTILE_RULE` is: a count whose rule lives only in a module is
    #: a count a reader cannot check. Empty on a mode that reports no leak.
    role_leak_rule: str = ""
    elapsed_seconds: float
    model_work_seconds: float
    seconds_per_attempt: float
    total_cost_usd: float
    dry_run: bool
    caveat: str


def _call_rows(
    records: Sequence[UnitRecord], sampling: SamplingConfig
) -> tuple[CalibrationCall, ...]:
    """Every completion of every unit, in the order the units made them."""

    return tuple(
        CalibrationCall(
            arm=record.arm,
            call_type=calibration_call_type(call, sampling),
            input_tokens=call.input_tokens,
            output_tokens=call.output_tokens,
            disposition=call.disposition,
            finish_reason=call.finish_reason,
        )
        for record in records
        for call in record.calls
        if call.disposition in COMPLETED_DISPOSITIONS
    )


def _unit_rows(
    records: Sequence[UnitRecord],
) -> tuple[CalibrationUnitUsage, ...]:
    """One row per unit, in run order."""

    return tuple(
        CalibrationUnitUsage(
            seed=record.seed,
            arm=record.arm,
            attempts=len(record.calls),
            completions=sum(
                1 for call in record.calls if call.disposition in COMPLETED_DISPOSITIONS
            ),
            input_tokens=sum(call.input_tokens for call in record.calls),
            output_tokens=sum(call.output_tokens for call in record.calls),
            model_work_seconds=sum(call.seconds for call in record.calls),
            defaulted_turns=record.defaults.defaulted_turns,
            defaulted_votes=record.defaults.defaulted_votes,
            charged_failed_attempts=sum(
                1 for call in record.calls if call.disposition == "billed_and_refused"
            ),
            retried_calls=record.transport_attempts.retried_calls,
            unaccounted_attempts=record.transport_attempts.unaccounted_attempts,
        )
        for record in records
    )


def _summarize_calibration_arm(
    arm: ArmName,
    *,
    records: Sequence[UnitRecord],
    usage: ArmUsage,
    attempts: TransportAttempts,
    sampling: SamplingConfig,
    by_role: bool = False,
    diagnostics_note: str | None = None,
    levers: Mapping[str, str] | None = None,
) -> CalibrationArmUsage:
    """One arm's totals and its two call schedules, over the units it ran.

    ``by_role`` adds the second calibration's role split and its two
    diagnostics; ``diagnostics_note`` adds the third calibration's
    authored-ballot block, carrying that note, and ``levers`` the surface it was
    measured on. All three are off by default, because the earlier
    calibrations' committed outputs were written without them and re-deriving
    those has to keep producing the same bytes.

    The block is requested BY its note rather than by a boolean beside one,
    because those two could disagree: a caller that asked for the block and
    supplied no note would publish the live evaluation's paragraph on a payload
    that reports no outcome.
    """

    own = [record for record in records if record.arm == arm]
    if not own:
        raise InstrumentError(
            f"arm {arm} ran no unit; a calibration measures both arms or it "
            "measures neither"
        )
    rows = _unit_rows(own)
    by_call_type: list[CallTypeUsage] = []
    for call_type in CALL_TYPES:
        sample = [
            call
            for record in own
            for call in record.calls
            if call.disposition in COMPLETED_DISPOSITIONS
            and calibration_call_type(call, sampling) == call_type
        ]
        if not sample:
            # Every unit schedules three of each, so an empty bucket means every
            # one of them produced nothing at all — a fact, and not one to
            # average over.
            continue
        inputs = [call.input_tokens for call in sample]
        outputs = [call.output_tokens for call in sample]
        by_call_type.append(
            CallTypeUsage(
                arm=arm,
                call_type=call_type,
                completions=len(sample),
                input_mean=sum(inputs) / len(inputs),
                input_p95=_percentile(inputs, 0.95),
                input_max=max(inputs),
                output_mean=sum(outputs) / len(outputs),
                output_p95=_percentile(outputs, 0.95),
                output_max=max(outputs),
                max_tokens=(
                    sampling.turn_max_tokens
                    if call_type == "turn"
                    else sampling.vote_max_tokens
                ),
            )
        )
    defaults = DefaultedAttempts()
    for record in own:
        defaults = defaults.plus(record.defaults)
    refused = [
        call
        for record in own
        for call in record.calls
        if call.disposition == "billed_and_refused"
    ]
    return CalibrationArmUsage(
        arm=arm,
        units=len(own),
        attempts=usage.calls,
        completions=sum(row.completions for row in rows),
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_usd=usage.cost_usd,
        model_work_seconds=usage.model_work_seconds,
        seconds_per_attempt=(
            usage.model_work_seconds / usage.calls if usage.calls else 0.0
        ),
        by_call_type=tuple(by_call_type),
        mean_unit_input_tokens=sum(row.input_tokens for row in rows) / len(rows),
        mean_unit_output_tokens=sum(row.output_tokens for row in rows) / len(rows),
        max_unit_input_tokens=max(row.input_tokens for row in rows),
        max_unit_output_tokens=max(row.output_tokens for row in rows),
        defaulted_turns=defaults.defaulted_turns,
        defaulted_votes=defaults.defaulted_votes,
        defaults_by_validation=defaults.by_validation,
        defaults_by_deadline=defaults.by_deadline,
        degraded_openings=defaults.degraded_openings,
        units_with_defaults=sum(1 for record in own if record.defaults.total > 0),
        charged_failed_attempts=len(refused),
        charged_failed_input_tokens=sum(call.input_tokens for call in refused),
        charged_failed_output_tokens=sum(call.output_tokens for call in refused),
        retried_calls=attempts.retried_calls,
        unaccounted_attempts=attempts.unaccounted_attempts,
        aborted_attempts=sum(
            1
            for record in own
            for call in record.calls
            if call.disposition == "aborted"
        ),
        attempts_by_trigger=dict(attempts.by_trigger),
        by_role=(
            _role_split_rows(arm, records=own, sampling=sampling) if by_role else ()
        ),
        self_telling_impostor_ballots=(
            sum(count_self_telling_ballots(record) for record in own) if by_role else 0
        ),
        leaking_turns=(
            sum(count_leaking_turns(record) for record in own) if by_role else 0
        ),
        units_with_a_leaking_turn=(
            sum(1 for record in own if count_leaking_turns(record) > 0)
            if by_role
            else 0
        ),
        resolved_levers=dict(levers) if levers is not None else {},
        authored_diagnostics=(
            authored_ballot_block(_authored_counts_over(own), note=diagnostics_note)
            if diagnostics_note is not None
            else None
        ),
    )


def _authored_counts_over(records: Sequence[UnitRecord]) -> AuthoredBallotCounts:
    """One arm's authored-ballot counts, summed over the units it ran.

    The calibration path has the :class:`UnitRecord` objects in hand and never
    builds the evaluation's :class:`UnitTelemetry`, so it sums the same
    per-unit function (:func:`authored_ballot_diagnostics`) the evaluation's
    telemetry projection sums. One counter, two callers.
    """

    counts = AuthoredBallotCounts()
    for record in records:
        counts = counts.plus(
            authored_ballot_diagnostics(
                ballots=record.ballots,
                roles=record.roles,
                ejected_player_id=record.ejected_player_id,
            )
        )
    return counts


def ceiling_proposal(
    arms: Sequence[CalibrationArmUsage],
    *,
    sampling: SamplingConfig = AUTHORIZED_SAMPLING,
    units: int | None = None,
) -> CeilingProposal:
    """The re-sized ceilings :data:`CEILING_PROPOSAL_RULE` states, as numbers.

    Computed over BOTH arms together, on the worst arm's maximum and on the
    mean across every unit: one run spends one pair of ceilings, so a proposal
    sized on the cheaper arm would authorize a run the dearer one cannot pay
    for.
    """

    if not arms:
        raise ValueError("a proposal needs at least one measured arm")
    planned = planned_units() if units is None else units
    if planned < 1:
        raise ValueError(f"a run has at least one unit, got {planned}")
    measured_units = sum(arm.units for arm in arms)
    max_input = max(arm.max_unit_input_tokens for arm in arms)
    max_output = max(arm.max_unit_output_tokens for arm in arms)
    mean_input = (
        sum(arm.mean_unit_input_tokens * arm.units for arm in arms) / measured_units
    )
    mean_output = (
        sum(arm.mean_unit_output_tokens * arm.units for arm in arms) / measured_units
    )
    reserved = unit_output_reservation(sampling=sampling)
    proposed = RunLimits(
        run_max_input_tokens=_rounded_up(
            max(planned * mean_input * CEILING_PROPOSAL_RUN_MARGIN, planned * max_input)
        ),
        run_max_output_tokens=_rounded_up(
            max(
                planned * mean_output * CEILING_PROPOSAL_RUN_MARGIN,
                # The in-flight headroom term the gate enforces
                # (:func:`assert_limits_are_feasible`): the run's last call is
                # pre-flighted against the run budget after everything before
                # it has been charged, so a ceiling sized at exactly what its
                # units charge cannot pay for its own last call.
                planned * max_output + sampling.turn_max_tokens,
            )
        ),
        unit_max_input_tokens=_rounded_up(max_input * CEILING_PROPOSAL_UNIT_MULTIPLE),
        unit_max_output_tokens=_rounded_up(
            max(reserved, max_output * CEILING_PROPOSAL_UNIT_MULTIPLE)
        ),
        max_cost_usd=AUTHORIZED_MAX_COST_USD,
        elapsed_seconds=AUTHORIZED_ELAPSED_SECONDS,
        model_work_seconds=AUTHORIZED_MODEL_WORK_SECONDS,
    )
    # Run the gate on the proposal rather than describing it, twice and
    # against two different calibrations of it.
    #
    # The proposal's OWN claim is checked against the maxima this sitting
    # measured: these ceilings pay for a run of the units it saw. Checking that
    # claim against the tree's committed constants — which is what this did
    # before the second calibration's card — answers a different question, and
    # answers it with a profile built from some earlier run's archives.
    refusal: str | None = None
    try:
        assert_limits_are_feasible(
            limits=proposed,
            sampling=sampling,
            units=planned,
            calibrated_unit_input_tokens=max_input,
            calibrated_unit_output_tokens=max_output,
        )
    except LimitsInfeasible as infeasible:
        refusal = str(infeasible)
    # And the committed profile's, reported beside it: a rehearsal whose
    # fixture reports a tenth of a real call's tokens is told it proposes
    # ceilings this tree would refuse, instead of publishing them as if they
    # were sized on a measurement.
    committed_refusal: str | None = None
    try:
        assert_limits_are_feasible(limits=proposed, sampling=sampling, units=planned)
    except LimitsInfeasible as infeasible:
        committed_refusal = str(infeasible)
    return CeilingProposal(
        rule=CEILING_PROPOSAL_RULE,
        units=planned,
        reservation_schedule=reserved,
        measured_max_unit_input_tokens=max_input,
        measured_max_unit_output_tokens=max_output,
        measured_mean_unit_input_tokens=mean_input,
        measured_mean_unit_output_tokens=mean_output,
        unit_max_input_tokens=proposed.unit_max_input_tokens,
        unit_max_output_tokens=proposed.unit_max_output_tokens,
        run_max_input_tokens=proposed.run_max_input_tokens,
        run_max_output_tokens=proposed.run_max_output_tokens,
        clears_the_feasibility_gate=refusal is None,
        feasibility_refusal=refusal,
        clears_the_committed_profiles_gate=committed_refusal is None,
        committed_profile_refusal=committed_refusal,
    )


def proposed_limits(proposal: CeilingProposal) -> RunLimits:
    """The proposal's four ceilings as a :class:`RunLimits`, walls unchanged.

    The proposal re-sizes TOKENS. The elapsed and model-work windows are a
    separate decision the owner took on 2026-09-13 and this rule says nothing
    about them, so they come through as the authorized ones rather than being
    quietly re-sized by a function nobody asked to touch them.
    """

    return RunLimits(
        run_max_input_tokens=proposal.run_max_input_tokens,
        run_max_output_tokens=proposal.run_max_output_tokens,
        unit_max_input_tokens=proposal.unit_max_input_tokens,
        unit_max_output_tokens=proposal.unit_max_output_tokens,
        max_cost_usd=AUTHORIZED_MAX_COST_USD,
        elapsed_seconds=AUTHORIZED_ELAPSED_SECONDS,
        model_work_seconds=AUTHORIZED_MODEL_WORK_SECONDS,
    )


def run_calibration(
    record: Path | None = None,
    *,
    output_dir: Path,
    records: Sequence[Path] | None = None,
    client: LLMClient | None = None,
    provider: str = "fake",
    live_invocation: LiveRunInvocation | None = None,
    repo_root: Path = _REPO_ROOT,
    limits: RunLimits = CALIBRATION_LIMITS,
    sampling: SamplingConfig = CALIBRATION_SAMPLING,
    paired_seeds: int = CALIBRATION_PAIRED_SEEDS,
) -> CalibrationReport:
    """Measure what the provider charges, on a converted band's first seeds.

    The same public-API path as the evaluation — :func:`run_unit`, the same
    wrapper, the same budgets, the same arms in the same order — because the
    number being measured is what THAT path costs. What it does not do is grade:
    no grader is called, no paired statistic is computed and no outcome is
    reported, so nothing here can inform the frozen analysis.

    The held-out record is never read. :func:`verify_frozen_set` is not called
    on this path at all, and :func:`verify_calibration_set` refuses
    :data:`~experiments.held_out_prefixes.MANIFEST_PATH` by name.

    No checkpoint and no resume. A calibration is one sitting inside its own
    elapsed window; a stop is reported with its partial accounting and the
    calibration is re-run, which spends development data the evaluation is not
    holding in reserve.

    Which of the three authorized modes this is comes from the three values
    that size the spend, through :func:`calibration_mode_for`, and the mode
    decides what nothing else does: whether a per-call truncation is a
    measurement, whether the report carries the role split and the leak
    diagnostic, whether it carries the authored-ballot diagnostics and the
    resolved levers, and which caveat it is published under. ``record`` names
    one converted record and ``records`` the
    draw's records in order; neither names the default, which is every
    converted band in :data:`CONVERTED_BANDS`' own order, and both are held to
    a PREFIX of that order by :func:`_draw_in_converted_order`.
    """

    mode = assert_calibration_is_authorized(
        provider=provider,
        invocation=live_invocation,
        limits=limits,
        sampling=sampling,
        paired_seeds=paired_seeds,
        repo_root=repo_root,
    )
    assert_client_matches_provider(provider=provider, client=client)
    draw = verify_calibration_draw(
        records=_draw_records(record=record, records=records),
        repo_root=repo_root,
        paired_seeds=paired_seeds,
    )
    arms = instrument_arms()
    harness = _build_harness(
        client=client,
        limits=limits,
        sampling=sampling,
        invocation=live_invocation,
        truncation_is_a_measurement=mode.truncation_is_a_measurement,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    state = _RunState()
    unit_records: list[UnitRecord] = []
    planned = draw.paired_seeds * len(arms)
    started = time.monotonic()
    for prefix in draw.prefixes:
        for arm in arms:
            try:
                harness.deadline.check()
                unit = run_unit(
                    prefix,
                    arm=arm,
                    client=harness.client,
                    run_budget=harness.run_budget,
                    deadline=harness.deadline,
                    work_clock=harness.work_clock,
                    output_dir=output_dir,
                    provider=provider,
                    limits=limits,
                    sampling=sampling,
                )
            # The run path's stop discipline, unchanged: the stopped unit's
            # calls are still in the client, they were spent, and they are
            # charged into the partial accounting before it is reported.
            except Exception as exc:
                state.charge(
                    arm.name, harness.client.take(), harness.client.take_attempts()
                )
                raise InstrumentAborted(
                    PartialRun(
                        reason=f"{type(exc).__name__}: {exc}",
                        completed_units=state.completed,
                        planned_units=planned,
                        usage_by_arm=dict(state.usage_by_arm),
                        elapsed_seconds=time.monotonic() - started,
                        model_work_seconds=harness.work_clock.seconds,
                        attempts_by_arm=dict(state.attempts_by_arm),
                    )
                ) from exc
            state.charge(arm.name, unit.calls, unit.transport_attempts)
            state.completed += 1
            unit_records.append(unit)
    summaries = tuple(
        _summarize_calibration_arm(
            arm.name,
            records=unit_records,
            usage=state.usage_by_arm.get(arm.name, ArmUsage()),
            attempts=state.attempts_by_arm.get(arm.name, TransportAttempts()),
            sampling=sampling,
            by_role=mode.reports_the_role_split,
            diagnostics_note=(
                CALIBRATION_DIAGNOSTICS_NOTES[mode.name]
                if mode.reports_authored_diagnostics
                else None
            ),
            levers=(
                arm_lever_profile(arm) if mode.reports_authored_diagnostics else None
            ),
        )
        for arm in arms
    )
    attempts = sum(summary.attempts for summary in summaries)
    report = CalibrationReport(
        report_schema=CALIBRATION_SCHEMA,
        provider=provider,
        model_ids=tuple(
            sorted({call.model for unit in unit_records for call in unit.calls})
        ),
        execution_mode=AUTHORIZED_EXECUTION_MODE,
        instrument_sha256=instrument_sha256(),
        prompt_set=AUTHORIZED_PROMPT_SET,
        inputs=_calibration_inputs(draw.sets[0], repo_root),
        input_records=tuple(
            _calibration_inputs(drawn, repo_root) for drawn in draw.sets
        ),
        mode=mode.name,
        limits=limits,
        sampling=sampling,
        paired_seeds=paired_seeds,
        units=len(unit_records),
        arms=summaries,
        calls=_call_rows(unit_records, sampling),
        unit_usage=_unit_rows(unit_records),
        proposal=ceiling_proposal(summaries, sampling=sampling),
        percentile_rule=PERCENTILE_RULE,
        role_leak_rule=ROLE_LEAK_RULE if mode.reports_the_role_split else "",
        elapsed_seconds=time.monotonic() - started,
        model_work_seconds=harness.work_clock.seconds,
        seconds_per_attempt=(
            harness.work_clock.seconds / attempts if attempts else 0.0
        ),
        total_cost_usd=sum(summary.cost_usd for summary in summaries),
        dry_run=provider == "fake",
        caveat=CALIBRATION_CAVEATS[mode.name],
    )
    # The same guard the evaluation's report passes. A calibration's inputs are
    # development data and leaking them would convert nothing, but the rule
    # this instrument is built on is that a REPORT carries counts, and one rule
    # applied on one path only is a rule that has already started to drift.
    assert_report_holds_no_prefix_bytes(report, draw.prefixes)
    # And the rule the 2026-09-18 clause states in words, over the payload a
    # reader holds rather than over the object this function built.
    assert_calibration_reports_no_outcome(report.model_dump(mode="json"))
    return report


def _calibration_inputs(drawn: CalibrationSet, repo_root: Path) -> CalibrationInputs:
    """One drawn record as the report's inputs row: path, digest, seeds."""

    return CalibrationInputs(
        record=str(drawn.record_path.relative_to(repo_root.resolve())),
        record_sha256=drawn.record_sha256,
        status="development",
        band_first_seed=drawn.band.first_seed,
        band_last_seed=drawn.band.last_seed,
        seeds=drawn.seeds,
        accepted_in_record=drawn.accepted_in_record,
        skipped_in_record=drawn.skipped_in_record,
    )


def usage_profile_from_calibration(report: CalibrationReport) -> dict[str, object]:
    """A rehearsal usage profile built from one calibration's measurements.

    The double replays individual calls keyed by (arm, call type), so the rows
    here are the calibration's own completions in the order they were made,
    carrying the four counts and nothing else. The unit rows are what
    :meth:`UsageProfile.largest_unit` reads, which is what the feasibility
    gate's two calibrated constants are held to — so refreshing the profile
    moves those constants, and the test that compares them is where that shows
    up.
    """

    if report.report_schema != CALIBRATION_SCHEMA:
        raise ValueError(
            f"{report.report_schema!r} is not a calibration this refresh reads"
        )
    complete = UNIT_TURN_CALLS + UNIT_BALLOT_CALLS
    calls = [
        {
            "arm": call.arm,
            "call_type": call.call_type,
            "input_tokens": call.input_tokens,
            "output_tokens": call.output_tokens,
            "disposition": call.disposition,
            # Null on a row measured before the reading was captured, which is
            # what the committed profile carries today: the rehearsal double
            # reads it with ``entry.get`` and replays a double's ``"stop"``
            # where the archive is silent, and says so.
            "finish_reason": call.finish_reason,
        }
        for call in report.calls
    ]
    units = [
        {
            "arm": unit.arm,
            "complete": unit.completions >= complete,
            "charged_input_tokens": unit.input_tokens,
            "charged_output_tokens": unit.output_tokens,
            "resolved_calls": unit.completions - unit.charged_failed_attempts,
            "refused_calls": unit.charged_failed_attempts,
        }
        for unit in report.unit_usage
    ]
    refused = sum(1 for call in calls if call["disposition"] == "billed_and_refused")
    return {
        "schema": "fresh-deduction-usage-profile/1",
        "built_from": {
            "calibration": CALIBRATION_SCHEMA,
            "mode": report.mode,
            "provider": report.provider,
            "record": report.inputs.record,
            "band": f"{report.inputs.band_first_seed}-{report.inputs.band_last_seed}",
            # Every record the draw spanned, because the second calibration's
            # sixty seeds do not fit in one: the two keys above name the first
            # of them, which is what a profile built from the five-seed mode
            # has always carried, and this names all of them.
            "records": [
                {
                    "record": row.record,
                    "band": f"{row.band_first_seed}-{row.band_last_seed}",
                    "seeds": len(row.seeds),
                }
                for row in report.input_records
            ],
            "instrument_sha256": report.instrument_sha256,
            "note": (
                "Token counts only, measured by the development calibration on "
                "a converted band. No prompt, no prefix, no response text."
            ),
        },
        "calls": calls,
        "units": units,
        "totals": {
            "units": len(units),
            "resolved_calls": len(calls) - refused,
            "refused_calls_with_usage": refused,
            "largest_charged_unit_input_tokens": max(
                (int(str(unit["charged_input_tokens"])) for unit in units), default=0
            ),
            "largest_charged_unit_output_tokens": max(
                (int(str(unit["charged_output_tokens"])) for unit in units), default=0
            ),
        },
    }


def write_usage_profile(report: CalibrationReport, path: Path) -> None:
    """Write :func:`usage_profile_from_calibration`'s payload to ``path``."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(usage_profile_from_calibration(report), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _preflight_json_destination(
    path: Path | None, parser: argparse.ArgumentParser
) -> None:
    """Make the ``--json`` destination's directory BEFORE the first call.

    The manifest's documented live command writes into a dated archive
    directory — ``audits/deduction-candidate/calibration-<date>/`` — that
    nothing has created yet, and :meth:`Path.write_text` does not create it.
    Discovering that after the run is the one ordering that loses the
    measurement: the calibration this manifest authorizes is a once-only spend,
    and its whole record is the payload written at the end. So the directory is
    made, or the path refused, before a provider is reached rather than after
    it is paid.
    """

    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        parser.error(
            f"--json {path} cannot be written: {exc}. A run whose output has "
            "nowhere to land is refused before it spends, not after"
        )


def _emit_report(payload: str, path: Path | None) -> None:
    """stdout first, then the file: a failed write must not eat the payload.

    The pair with :func:`_preflight_json_destination`. The preflight makes the
    write overwhelmingly likely to succeed; this ordering makes the failure it
    cannot rule out (a full disk, a revoked permission) cost the operator a
    copy-paste rather than the measurement.
    """

    print(payload)
    if path is not None:
        path.write_text(payload + "\n", encoding="utf-8")


def _run_calibration_from_args(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> int:
    """The ``--calibrate`` path of :func:`main`, live or rehearsed.

    Split out because it is a second run mode rather than a second branch: it
    has its own gate, its own limits and its own inputs, and reading them beside
    the evaluation's flags was what made the CLI hard to hold in the head.
    """

    mode = _calibration_mode_named(args.calibration_mode, parser)
    single_record_mode = mode is CALIBRATION_MODES[0]
    if not single_record_mode and args.calibration_record is not None:
        parser.error(
            f"the {mode.name} calibration draws across the converted bands in "
            "their own order and takes no single --calibration-record; the "
            "draw is that list and the seed count, with nothing left to choose"
        )
    record = (
        (
            _REPO_ROOT / DEFAULT_CALIBRATION_RECORD
            if args.calibration_record is None
            else args.calibration_record
        )
        if single_record_mode
        else None
    )
    if args.dry_run or args.provider == "fake":
        with TemporaryDirectory() as directory:
            report = run_calibration(
                record,
                # A rehearsal renders development prompts too, and they belong
                # nowhere on disk once it is over.
                output_dir=Path(directory)
                if args.output_dir is None
                else args.output_dir,
                provider="fake",
                limits=mode.limits,
                sampling=mode.sampling,
                paired_seeds=mode.paired_seeds,
            )
    else:
        if args.execution_manifest is None or not args.i_am_the_runner:
            parser.error(
                "a live calibration needs --execution-manifest and the runner "
                "flag; the manifest authorizes the spend, the invocation "
                "authorizes the call"
            )
        if args.output_dir is None:
            parser.error("a live calibration writes its replays; pass --output-dir")
        invocation = LiveRunInvocation.naming(
            args.execution_manifest,
            provider=args.provider,
            model=AUTHORIZED_MODEL,
        )
        # Authorized and verified before a client exists, exactly as the live
        # run's path is: the verified inputs are what build_authorized_client
        # requires, so the order cannot be reversed by editing these lines.
        inputs = assert_ready_for_a_calibration(
            record,
            provider=args.provider,
            invocation=invocation,
            limits=mode.limits,
            sampling=mode.sampling,
            paired_seeds=mode.paired_seeds,
        )
        report = run_calibration(
            record,
            output_dir=args.output_dir,
            client=build_authorized_client(inputs),
            provider=args.provider,
            live_invocation=invocation,
            limits=mode.limits,
            sampling=mode.sampling,
            paired_seeds=mode.paired_seeds,
        )
    _emit_report(report.model_dump_json(indent=2), args.json)
    return 0


def _calibration_mode_named(
    name: str, parser: argparse.ArgumentParser
) -> CalibrationMode:
    """The authorized mode this CLI value names, or exit 2.

    ``argparse``'s own ``choices`` already holds the value to the table; this
    turns it into the object, and refuses an unknown one rather than falling
    back to the first mode — which would run a five-seed spend under a name
    nobody recognised.
    """

    for mode in CALIBRATION_MODES:
        if mode.name == name:
            return mode
    parser.error(
        f"{name!r} is not an authorized calibration mode; the authorized modes "
        + ", ".join(mode.name for mode in CALIBRATION_MODES)
        + " are the only spends the manifest carries a clause for"
    )
    raise AssertionError("unreachable: parser.error exits")


#: The calibration's default input: the first band a stopped run converted. A
#: default rather than a required argument because the record is part of the
#: authorized shape — the owner approved a calibration on the converted
#: 3000-3999 band — and :func:`verify_calibration_set` refuses anything that is
#: not a converted band's record anyway.
DEFAULT_CALIBRATION_RECORD: Final[str] = CONVERTED_BANDS[0].manifest_path


def main(argv: Sequence[str] | None = None) -> int:
    """``--dry-run`` is the only mode any gate uses; a live run needs three flags.

    Three modes, in the order they are dispatched: ``--refresh-usage-profile``
    rewrites the rehearsal double's profile from a calibration output and makes
    no call; ``--calibrate`` measures spend on a converted band; the default is
    the evaluation, dry by default and live only with the manifest, the runner
    flag and an output directory.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help=(
            "measure what the provider charges on the accepted seeds of the "
            "CONVERTED bands, both arms, under one authorized mode's limits "
            "(see --calibration-mode). Grades nothing and reads no held-out "
            "prefix"
        ),
    )
    parser.add_argument(
        "--calibration-record",
        type=Path,
        default=None,
        help=(
            "the converted band's freeze record the calibration draws from "
            f"(default: {DEFAULT_CALIBRATION_RECORD}). A draw is a PREFIX of "
            "the converted bands in the order they were converted, so that "
            "record is also the only one a draw may start at. The "
            + " and ".join(mode.name for mode in CALIBRATION_MODES[1:])
            + " modes draw across the converted bands in order and refuse "
            "this flag"
        ),
    )
    parser.add_argument(
        "--calibration-mode",
        default=CALIBRATION_MODES[0].name,
        choices=[mode.name for mode in CALIBRATION_MODES],
        help=(
            "which authorized calibration to run: "
            + "; ".join(mode.describe() for mode in CALIBRATION_MODES)
        ),
    )
    parser.add_argument(
        "--refresh-usage-profile",
        type=Path,
        default=None,
        help=(
            "read a calibration output written by --calibrate and write the "
            "rehearsal double's usage profile from it to --profile-out. Makes "
            "no call and reads no input record"
        ),
    )
    parser.add_argument(
        "--profile-out",
        type=Path,
        default=None,
        help="where --refresh-usage-profile writes the profile",
    )
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
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help=(
            "write the per-unit checkpoint here after every completed paired "
            "seed, and once more where a stop lands; a run stopped by an "
            "environmental cause can be continued from it with --resume. "
            "Defaults to the --resume path, so a resumed sitting keeps "
            "advancing the checkpoint it continues"
        ),
    )
    parser.add_argument(
        "--resume",
        type=Path,
        default=None,
        help=(
            "continue the run this checkpoint stopped, at the next unrendered "
            "seed, into an output directory of its own. Refused unless the "
            "manifest, the frozen set, the arm surface, the limits and the "
            "sampling configuration are still the ones it was written under — "
            "and, on a live provider, unless the execution manifest carries "
            "the owner's resumption clause"
        ),
    )
    args = parser.parse_args(argv)
    # Before the dispatch, so both modes that write one get the same guarantee:
    # a destination that cannot be written is a refusal now, at exit 2, and not
    # a traceback after the spend.
    _preflight_json_destination(args.json, parser)

    if args.refresh_usage_profile is not None:
        if args.profile_out is None:
            parser.error("--refresh-usage-profile writes somewhere; pass --profile-out")
        calibration = CalibrationReport.model_validate_json(
            args.refresh_usage_profile.read_text(encoding="utf-8")
        )
        write_usage_profile(calibration, args.profile_out)
        print(f"wrote {args.profile_out} from {args.refresh_usage_profile}")
        return 0

    if args.calibrate:
        return _run_calibration_from_args(args, parser)

    resume = None if args.resume is None else read_checkpoint(args.resume)
    # A resumed sitting that wrote no checkpoint would lose its own progress to
    # the next stop and re-spend held-out calls a third sitting had already
    # bought, so --resume implies --checkpoint at the same path unless one is
    # named. Continuing a run is what the file is for; advancing it is the same
    # act.
    checkpoint_path = args.checkpoint if args.checkpoint is not None else args.resume
    if args.dry_run or args.provider == "fake":
        report = run_dry(
            output_dir=args.output_dir,
            units=args.units,
            checkpoint_path=checkpoint_path,
            resume=resume,
        )
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
            provider=args.provider,
            invocation=invocation,
            units=args.units,
            resuming=resume is not None,
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
            checkpoint_path=checkpoint_path,
            resume=resume,
        )
    _emit_report(report.model_dump_json(indent=2), args.json)
    return 0


if __name__ == "__main__":  # pragma: no cover - the operator entry point
    raise SystemExit(main())
