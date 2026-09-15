"""A provider double that reports the usage the real endpoint reported.

The three stopped live runs of the fresh-model deduction instrument left 36
resolved calls and two billed-and-refused ones in their archives. This module
replays their TOKEN COUNTS — never their bytes — keyed by the arm that made the
call and by whether it was a turn or a ballot, so an offline rehearsal exercises
the dimension the run of 2026-09-13 actually stopped on.

Why keyed, and why counts
-------------------------

`DryRunProvider` derives its usage from the length of the payload it serialises:
66 output tokens per call, identical on both arms, 396 per unit against a 4,000
ceiling. Every offline check therefore ran at 10% of the limit the live run hit
in four units. Replaying the measured counts closes that gap, and keying them by
(arm, call type) is what keeps the replay honest: the candidate arm's turns ran
to 1,045 output tokens and its ballots to 223, so a sampler that pooled them
would hand a 1,024-capped ballot a turn's length and manufacture a truncation
the provider never produced. `CallTypeBlindReplayProvider` is that mistake, kept
as the regression the keying prevents.

The payload each call returns is still `DryRunProvider`'s own mechanics answer.
A real response's bytes render a held-out prefix and are not committed anywhere;
what is committed is `deduction_usage_profile.json`, which carries arm, call
type and two token counts per call and nothing else.

The draw is a rotation, not a random sample: each bucket is consumed in its
committed order from an offset the seed fixes, so a run of N units exercises the
whole measured distribution rather than a subsample of it, and two runs of the
same rehearsal draw the same calls.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel

import experiments.fresh_deduction_instrument as instrument
from experiments.fresh_deduction_instrument import DryRunProvider
from llm.client import CallKind, LLMResponse, TokenUsage
from llm.fake_provider import FAKE_FINISH_REASON
from meetings.schemas import MeetingTurn, ModelAuthoredVoteBallot
from tests.experiments.burned_call_double import (
    EMPTY_BODY_ERROR,
    NO_USAGE_BODY_ERROR,
    TRANSPORT_ERROR,
    charged_parse_failure,
)

#: The committed profile: aggregate rows only. Since the fifth authorization of
#: 2026-09-15 it is the second live development calibration's 720 calls over 120
#: units, refreshed by ``--refresh-usage-profile`` from
#: ``audits/deduction-candidate/calibration-2-2026-09-15/calibration.json``, and
#: it is what :data:`experiments.fresh_deduction_instrument.CALIBRATED_UNIT_INPUT_TOKENS`
#: and its output twin are read off.
PROFILE_PATH: Final[Path] = Path(__file__).with_name("deduction_usage_profile.json")

#: The profile that stood there until that refresh: the three stopped live runs'
#: 38 rows, 36 resolved and two the provider billed and then refused. It is kept
#: because the FAULTS are only in it. The sitting of 2026-09-15 archived no
#: refusal, no default and no truncation — the corrected prompts worked — so a
#: rehearsal of the stop of 2026-09-13, of the archived refusal, of a
#: manufactured truncation or of a mid-unit transport drop has nothing to replay
#: in the current profile and everything to replay in this one. Splitting them
#: is what keeps both true at once: the gate is calibrated on the largest unit
#: this evaluation has measured, and the fault rehearsals still run on the calls
#: that actually faulted.
STOPPED_RUNS_PROFILE_PATH: Final[Path] = Path(__file__).with_name(
    "deduction_stopped_runs_usage_profile.json"
)


CallType = Literal["turn", "ballot"]

#: What the candidate arm's two prompt families say and the reference arm's do
#: not, one marker per call type. Both arms render the same facts through
#: different templates, so the family IS the arm here; the markers are structural
#: headings rather than content, and an unrecognised prompt raises rather than
#: defaulting to an arm (AGENTS.md: no silent fallbacks).
_ACCOUNTS_TURN_MARKER: Final[str] = "Public accounts are statements made by a player."
_REFERENCE_TURN_MARKER: Final[str] = "Living players you may accuse"
_ACCOUNTS_BALLOT_MARKER: Final[str] = "Living candidates:"
_REFERENCE_BALLOT_MARKER: Final[str] = "## Valid ejection targets"


#: What this double reports as the reason generation stopped when the archived
#: row carries no reading of its own — which is every row of the profile
#: committed on 2026-09-14, measured before the field existed. A DOUBLE's word
#: and not an archive's: the replay re-serves a payload the dry-run provider
#: writes, so `"stop"` describes THIS call honestly, while the archive's own
#: silence stays visible on `UsageRow.finish_reason`. Where the archive DOES
#: carry a reading, that reading is replayed instead.
REPLAYED_FINISH_REASON: Final[str] = FAKE_FINISH_REASON


@dataclass(frozen=True)
class UsageRow:
    """One archived call, as the profile carries it.

    ``refused`` is the row the provider BILLED for and then refused on its own
    schema validation. It is in the same bucket as the resolved calls and in the
    position the provider produced it — a unit's third turn, both times — so a
    replay of the bucket replays the mixture rather than an idealised version of
    it: the candidate arm refused two of its nine archived turns, and the run of
    2026-09-13 stopped on a unit that carried one.
    """

    arm: str
    call_type: CallType
    input_tokens: int
    output_tokens: int
    refused: bool = False
    #: The provider's own word for why this archived call stopped, when the
    #: calibration that measured it recorded one. ``None`` for every row of the
    #: profile committed on 2026-09-14, which was measured before the reading
    #: was captured: an archive's silence is carried as silence, and what the
    #: double substitutes for it on the wire is a DOUBLE's ``"stop"``, said so
    #: at :data:`REPLAYED_FINISH_REASON`.
    finish_reason: str | None = None


@dataclass(frozen=True)
class ArchivedUnit:
    """One archived unit's charged totals, for the calibration check."""

    arm: str
    complete: bool
    charged_input_tokens: int
    charged_output_tokens: int


class UsageProfile:
    """The committed profile, bucketed by (arm, call type)."""

    def __init__(
        self,
        *,
        calls: tuple[UsageRow, ...],
        units: tuple[ArchivedUnit, ...],
    ) -> None:
        if not calls:
            raise ValueError("a usage profile with no calls replays nothing")
        self.calls = calls
        self.units = units

    @property
    def refusals(self) -> tuple[UsageRow, ...]:
        return tuple(row for row in self.calls if row.refused)

    @property
    def resolved(self) -> tuple[UsageRow, ...]:
        return tuple(row for row in self.calls if not row.refused)

    @classmethod
    def load(cls, path: Path = PROFILE_PATH) -> UsageProfile:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != "fresh-deduction-usage-profile/1":
            raise ValueError(f"{path} is not a usage profile this double reads")
        return cls(
            calls=tuple(_row(entry) for entry in payload["calls"]),
            units=tuple(
                ArchivedUnit(
                    arm=str(entry["arm"]),
                    complete=bool(entry["complete"]),
                    charged_input_tokens=int(str(entry["charged_input_tokens"])),
                    charged_output_tokens=int(str(entry["charged_output_tokens"])),
                )
                for entry in payload["units"]
            ),
        )

    def bucket(self, arm: str, call_type: CallType) -> tuple[UsageRow, ...]:
        rows = tuple(
            row for row in self.calls if row.arm == arm and row.call_type == call_type
        )
        if not rows:
            raise KeyError(f"the profile carries no {call_type} of arm {arm!r}")
        return rows

    def pooled(self, arm: str) -> tuple[UsageRow, ...]:
        """Every call of one arm, call type discarded. The blind sampler's view."""

        rows = tuple(row for row in self.calls if row.arm == arm)
        if not rows:
            raise KeyError(f"the profile carries no call of arm {arm!r}")
        return rows

    def refusal(self, arm: str) -> UsageRow:
        """The archived billed-and-refused call of one arm."""

        for row in self.refusals:
            if row.arm == arm:
                return row
        raise KeyError(f"the profile carries no refusal of arm {arm!r}")

    def largest_unit(self) -> tuple[int, int]:
        """``(input, output)``: the largest charged totals any archived unit has.

        What
        :data:`experiments.fresh_deduction_instrument.CALIBRATED_UNIT_INPUT_TOKENS`
        and its output twin are held to, so the feasibility gate's calibration
        is read off committed evidence rather than typed into the module.
        """

        return (
            max(unit.charged_input_tokens for unit in self.units),
            max(unit.charged_output_tokens for unit in self.units),
        )


def stopped_runs_profile() -> UsageProfile:
    """The three stopped live runs' rows, as a profile.

    Named rather than spelled out at each call site, because "which profile is
    this rehearsal replaying" is the question the split of 2026-09-15 makes
    worth asking out loud: the eight cases that call this one are the eight
    whose subject is a FAULT.
    """

    return UsageProfile.load(STOPPED_RUNS_PROFILE_PATH)


def _row(entry: Mapping[str, object]) -> UsageRow:
    call_type = str(entry["call_type"])
    if call_type not in ("turn", "ballot"):
        raise ValueError(f"a profile row carries call type {call_type!r}")
    kind: CallType = "turn" if call_type == "turn" else "ballot"
    return UsageRow(
        arm=str(entry["arm"]),
        call_type=kind,
        input_tokens=int(str(entry["input_tokens"])),
        output_tokens=int(str(entry["output_tokens"])),
        refused=entry.get("disposition") == "billed_and_refused",
        # Read with ``entry.get`` exactly as ``refused`` is, so the profile
        # committed before this field existed loads and reads null rather than
        # raising.
        finish_reason=_finish_reason(entry.get("finish_reason")),
    )


def _finish_reason(value: object) -> str | None:
    """One archived row's reading, or ``None`` when the archive is silent."""

    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"a profile row carries finish reason {value!r}")
    return value


def _replayed_finish_reason(row: UsageRow) -> str:
    """What the replayed call reports: the archive's reading, or this double's.

    :data:`REPLAYED_FINISH_REASON` where the archive is silent, so every
    offline path exercises the field — and it is this double's own word, not a
    measurement the calibration made.
    """

    return (
        row.finish_reason if row.finish_reason is not None else REPLAYED_FINISH_REASON
    )


def call_type_of(schema: type[BaseModel] | None) -> CallType:
    """Which call this is, from the schema the meeting layer asked for."""

    if schema is MeetingTurn:
        return "turn"
    if schema is ModelAuthoredVoteBallot:
        return "ballot"
    raise ValueError(f"neither a turn nor a ballot: {schema!r}")


def arm_of(prompt: str, call_type: CallType) -> str:
    """Which arm rendered this prompt, from its family's own structure."""

    accounts, reference = (
        (_ACCOUNTS_TURN_MARKER, _REFERENCE_TURN_MARKER)
        if call_type == "turn"
        else (_ACCOUNTS_BALLOT_MARKER, _REFERENCE_BALLOT_MARKER)
    )
    if accounts in prompt:
        return "combined_accounts"
    if reference in prompt:
        return "repaired_clock"
    raise ValueError(
        f"a {call_type} prompt carries neither arm's marker; this double cannot "
        "say whose usage to replay, and guessing would replay the wrong arm"
    )


#: What a spoiled call does. The first three produce no completion and are the
#: instrument wrapper's retry classes; `billed_refusal` produces one the provider
#: billed for and refused, which is a sample and is never retried.
ReplayMode = Literal["billed_refusal", "empty_body", "no_usage_body", "transport_error"]


class UsageReplayProvider(DryRunProvider):
    """A dry-run provider that reports the archived usage of a real call.

    The default behaviour replays the bucket: each call reports the tokens the
    next archived call of its (arm, call type) reported, and a call whose
    archived row is a refusal is refused here the way the provider refused it.

    `spoil_call` and `mode` plant one PROVIDER FAULT on the nth call this double
    receives, 1-based — a 2xx body with no completion, one whose usage block the
    adapter would not read, a dropped connection, or an extra billed refusal.
    Those are faults rather than behaviours of the prompt, so they are planted
    rather than replayed. `seed` rotates each bucket's starting offset.
    """

    def __init__(
        self,
        *,
        profile: UsageProfile | None = None,
        seed: int = 0,
        spoil_call: int | None = None,
        spoil_repeats: int = 1,
        mode: ReplayMode = "billed_refusal",
    ) -> None:
        super().__init__()
        if spoil_repeats < 1:
            raise ValueError("a planted fault spoils at least one attempt")
        self.profile = UsageProfile.load() if profile is None else profile
        self.seed = seed
        self.spoil_call = spoil_call
        self.spoil_repeats = spoil_repeats
        self.mode: ReplayMode = mode
        self.attempts = 0
        self.spoiled = 0
        self.refused = 0
        self.replayed: list[UsageRow] = []
        self._cursor: dict[tuple[str, str], int] = {}

    def draw(self, arm: str, call_type: CallType) -> UsageRow:
        """The next archived call of this (arm, call type), in rotation."""

        rows = self.profile.bucket(arm, call_type)
        return self._next(rows, key=(arm, call_type))

    def _next(self, rows: tuple[UsageRow, ...], *, key: tuple[str, str]) -> UsageRow:
        index = self._cursor.get(key, self.seed)
        self._cursor[key] = index + 1
        return rows[index % len(rows)]

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
        if schema is None:
            return await super().complete(
                prompt=prompt,
                schema=schema,
                max_tokens=max_tokens,
                temperature=temperature,
                call_kind=call_kind,
                model=model,
                agent_id=agent_id,
            )
        self.attempts += 1
        call_type = call_type_of(schema)
        arm = arm_of(prompt, call_type)
        if (
            self.spoil_call is not None
            and self.spoil_call <= self.attempts < self.spoil_call + self.spoil_repeats
        ):
            # Before the draw, so a spoiled attempt consumes no archived row:
            # the call it spoils never reached the provider, and a resumed run
            # picks the rotation up where the completed units left it.
            self.spoiled += 1
            self._spoil(arm=arm, schema=schema, prompt=prompt)
        row = self.draw(arm, call_type)
        self.replayed.append(row)
        if row.refused:
            # The archived refusal, replayed where it happened: a completion the
            # provider billed for and then refused on its own schema validation.
            # It rides the exception with its usage attached, exactly as the
            # adapter raises it, so the budget charges it after the fact and the
            # meeting layer fail-softs the turn.
            self.refused += 1
            raise charged_parse_failure(
                schema,
                prompt=prompt,
                input_tokens=row.input_tokens,
                output_tokens=row.output_tokens,
                finish_reason=_replayed_finish_reason(row),
            )
        response = await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        return LLMResponse(
            text=response.text,
            usage=TokenUsage(
                input_tokens=row.input_tokens, output_tokens=row.output_tokens
            ),
            cost_usd=response.cost_usd,
            model=response.model,
            finish_reason=_replayed_finish_reason(row),
        )

    def _spoil(self, *, arm: str, schema: type[BaseModel], prompt: str) -> None:
        if self.mode == "billed_refusal":
            burned = self.profile.refusal(arm)
            raise charged_parse_failure(
                schema,
                prompt=prompt,
                input_tokens=burned.input_tokens,
                output_tokens=burned.output_tokens,
                finish_reason=_replayed_finish_reason(burned),
            )
        if self.mode == "empty_body":
            raise RuntimeError(EMPTY_BODY_ERROR)
        if self.mode == "no_usage_body":
            raise RuntimeError(NO_USAGE_BODY_ERROR)
        raise RuntimeError(TRANSPORT_ERROR)


class CallTypeBlindReplayProvider(UsageReplayProvider):
    """The same replay with the call type discarded: the regression, kept.

    It draws a ballot's usage out of the arm's whole pool, so a candidate ballot
    capped at 1,024 output tokens eventually reports a turn's 1,045 and the
    instrument stops the run on a truncation the provider never produced. That
    stop is an artifact of the sampler, and it is what keying by call type
    prevents.
    """

    def draw(self, arm: str, call_type: CallType) -> UsageRow:
        del call_type  # the defect under test: the key is thrown away
        return self._next(self.profile.pooled(arm), key=(arm, "pooled"))


def feasible_limits() -> instrument.RunLimits:
    """Limits the feasibility gate accepts that are NOT the authorized ones.

    The numbers decision 3 of `tasks/diagnosis-2026-09-13-live-run-stops.md`
    puts to the owner, used here as the rehearsal's "what a re-sized
    authorization would look like", with three figures moved since. The
    per-unit output ceiling, 12,000 in that proposal, would not clear the
    15,360-token schedule the fourth authorization's turn cap reserves, so it
    is 16,000. The two RUN ceilings, 3,600,000 and 350,000 there, no longer
    clear what a hundred units of the profile committed on 2026-09-15 charge —
    3,844,000 input and 421,696 output including the last call's in-flight
    reservation — so they are raised past both, to figures that are still
    nobody's authorization. They remain unauthorized for a live run: they
    differ from `AUTHORIZED_LIMITS` on all three, and
    `assert_live_run_is_authorized` refuses them there for exactly that reason.
    What the double CHARGES does not depend on any of them, so the rehearsals
    that quote their own totals into the manifest are unmoved by this.
    """

    return instrument.RunLimits(
        run_max_input_tokens=3_900_000,
        run_max_output_tokens=430_000,
        unit_max_input_tokens=60_000,
        unit_max_output_tokens=16_000,
        max_cost_usd=instrument.AUTHORIZED_MAX_COST_USD,
        elapsed_seconds=instrument.AUTHORIZED_ELAPSED_SECONDS,
        model_work_seconds=instrument.AUTHORIZED_MODEL_WORK_SECONDS,
    )
