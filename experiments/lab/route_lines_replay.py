"""Offline replay of the route lines on the committed recordings, count only.

The decision this informs is round 3's spend on the route lines
(``meetings.route_lines``, recorded as ``route_lines_version``): before any live
seed, how much of what the reference reading (c) of the route-check replay
reaches would the field as rendered reach, and what would it add to a ballot. It
walks the route-check replay's columns (s9, r1, r2 and, once recorded, r3), each
read alone and never pooled, through that replay's own faithful walk and its own
per-meeting reading, and on every recorded ballot renders the field ON beside the
ballot as recorded.

* **Parity.** For each column the committed route-check replay JSON records, the
  harness's per-meeting records recomputed here (``route_check_replay.
  read_meeting``) must equal the committed ones meeting by meeting, and the
  column's commit, path and tree must be the ones that JSON pins; a mismatch
  raises. So M (ejections resting on a charge the map or the regroup
  reconciles), W (those at kill-witness meetings) and (c)'s reach are the
  committed figures, recomputed.
* **The field's reach.** A renderer wrapper captures each ballot render's inputs
  and renders the same ballot with ``route_lines_version = 1`` and the lines
  :func:`meetings.route_lines.build_route_lines` builds from those inputs and the
  meeting's public regroup ticks. The ON render minus its block must equal the
  render as recorded, and its block must parse back to the lines; either failure
  raises. A case is reached when some EJECT voter's parsed block holds a line
  about the ejected player. The charge-touching reach asks that a step end on a
  charged placement; an unreached misjudged case is set out by reason.
* **The every-pair leg** is informational: it asks whether any pair of the
  ejected player's stated places, not only a consecutive one, would reconcile, so
  what the consecutive rule gives up is reproducible.
* **Size.** The consecutive changes of room left out because they neither walk
  nor cross; steps per reading; block characters per ballot; and the projected
  added input tokens, each recorded ballot call's input tokens times its block's
  characters over its prompt's characters, beside the column's recorded input
  tokens, the 17,500,000 token ceiling and its 15,750,000 hard stop.
* **r3.** A column recorded with the field ON is read from its served blocks:
  each recorded ballot's block must equal the lines built again from its inputs,
  and the reach is reported both served and rebuilt.

Roles are read only to set the cases out by ejection class, as description. The
reach is reported as measured and gates nothing. Offline: no provider client,
no environment write, no recorded byte edited. The outputs carry ids, ticks,
counts and the instrument's fixed wording; before writing, the run scans both
for every recorded turn text, ballot rationale, travel line and rendered route
line of 16 or more characters it read (the route-check replay's own scan) and
refuses to write one that holds any.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Final, Literal, TypeAlias, cast, get_args

import experiments.lab.route_check_replay as rcr
from agents.strategic.prompts.loader import PromptRenderers
from engine.entities import Role
from eval.gameplay_census import CensusInputs, GameFacts, load_census_inputs
from eval.validity import seeds_on_disk
from meetings.render_contract import VotePromptRenderer
from meetings.route_lines import (
    ROUTE_PLACEMENT_KINDS,
    Placement,
    RouteLine,
    RouteReading,
    _route_spots,
    build_route_lines,
    parse_route_lines,
    placements_of,
    reconcilable,
    route_block_span,
    spoken_placements,
    without_route_block,
)
from meetings.schemas import PlayerId
from orchestrator.replay import (
    MeetingReplayEntry,
    derive_regroup_ticks,
    read_all_entries,
    recorded_experiment_config,
)
from tests.meetings.test_prompt_byte_golden import (
    ReconstructedMeeting,
    _canonical_renderers,
)

SCHEMA_VERSION: Final[int] = 1

DEFAULT_JSON: Final[Path] = Path("experiments/lab/results-route-lines-replay.json")
DEFAULT_REPORT: Final[Path] = Path("experiments/lab/report-route-lines-replay.md")
#: The committed route-check replay JSON the parity check reads.
DEFAULT_ROUTE_CHECK_JSON: Final[Path] = rcr.DEFAULT_JSON

#: The round's input-token ceiling and its stop at 90 percent (decision memo
#: section 4, the standing ceilings round 3 keeps).
INPUT_TOKEN_CEILING: Final[int] = 17_500_000
INPUT_TOKEN_HARD_STOP: Final[int] = 15_750_000

FieldReason: TypeAlias = Literal["kind", "consecutive", "residual"]
#: The fixed order an unreached case's reason is chosen in.
FIELD_REASONS: Final[tuple[FieldReason, ...]] = get_args(FieldReason)
READINGS: Final[tuple[RouteReading, ...]] = get_args(RouteReading)
ColumnMode: TypeAlias = Literal["rendered", "served"]

_REASON_NAMES: Final[Mapping[FieldReason, str]] = {
    "kind": "every reconcilable pair has an end the field does not read (a vent sighting)",
    "consecutive": "the reconcilable pair is not a consecutive change of room",
    "residual": "none of the listed reasons",
}


class RouteLinesReplayError(RuntimeError):
    """The instrument refused an input or found the walk or a render unfaithful."""


# ---------------------------------------------------------------------------
# The renderer wrapper
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BallotRender:
    """One ballot render as the walk asked for it: its inputs and its prompt."""

    kwargs: Mapping[str, Any]
    prompt: str


@dataclass
class CapturingVote:
    """A vote renderer that records each render's inputs and prompt, unchanged."""

    inner: VotePromptRenderer
    renders: list[BallotRender] = field(default_factory=list)

    def __call__(self, **kwargs: Any) -> str:
        prompt = self.inner(**kwargs)
        self.renders.append(BallotRender(kwargs=dict(kwargs), prompt=prompt))
        return prompt

    def take(self) -> tuple[BallotRender, ...]:
        """The renders since the last take, in render order."""

        taken = tuple(self.renders)
        self.renders.clear()
        return taken


def capturing_renderers(
    renderers: Mapping[str, PromptRenderers],
) -> tuple[dict[str, PromptRenderers], dict[str, CapturingVote]]:
    """Each set's renderers with its vote renderer wrapped, and the wrappers."""

    wrapped: dict[str, PromptRenderers] = {}
    votes: dict[str, CapturingVote] = {}
    for name, bound in renderers.items():
        votes[name] = CapturingVote(inner=bound.vote)
        wrapped[name] = replace(bound, vote=votes[name])
    return wrapped, votes


# ---------------------------------------------------------------------------
# One ballot, rendered ON
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BallotReading:
    """One voter's ballot under the field: its lines and what the block adds."""

    voter: PlayerId
    lines: tuple[RouteLine, ...]
    block_chars: int
    block_rows: tuple[str, ...]
    recorded_prompt: str
    served_lines: tuple[RouteLine, ...] | None


def read_ballot(
    render: BallotRender,
    *,
    inner: VotePromptRenderer,
    regroup_ticks: frozenset[int],
    served: bool,
) -> BallotReading:
    """Build one ballot's lines, render it ON (or read its served block), check both.

    Rendered mode: the ballot recorded the field OFF, so the lines are built from
    the render's own transcript and candidates and this meeting's regroup ticks,
    the ballot is rendered again with them ON, and the ON render minus its block
    must equal the render as recorded and its block must parse back to the
    lines. Served mode: the ballot recorded the field ON, so its block is parsed
    as served and must equal the lines built again.
    """

    kwargs = render.kwargs
    voter = cast(PlayerId, kwargs["voter_id"])
    lines = build_route_lines(
        transcript=kwargs["transcript"],
        candidate_targets=tuple(kwargs["candidate_targets"]),
        regroup_ticks=regroup_ticks,
    )
    if served:
        on_prompt = render.prompt
        served_lines = parse_route_lines(on_prompt)
        if served_lines != lines:
            raise RouteLinesReplayError(
                f"{voter}: the served route block is not the lines its inputs build"
            )
        off_prompt = without_route_block(on_prompt)
    else:
        if kwargs.get("route_lines") or kwargs.get("route_lines_version") is not None:
            raise RouteLinesReplayError(
                f"{voter}: a ballot recorded OFF was rendered with route lines"
            )
        off_prompt = render.prompt
        on_prompt = (
            inner(**{**kwargs, "route_lines": lines, "route_lines_version": 1})
            if lines
            else off_prompt
        )
        if without_route_block(on_prompt) != off_prompt:
            raise RouteLinesReplayError(
                f"{voter}: the ON render minus its block is not the recorded render"
            )
        if parse_route_lines(on_prompt) != lines:
            raise RouteLinesReplayError(
                f"{voter}: the ON render's block does not parse back to its lines"
            )
        served_lines = None
    span = route_block_span(on_prompt)
    rows = () if span is None else tuple(on_prompt.split("\n")[span[0] : span[1] + 1])
    return BallotReading(
        voter=voter,
        lines=lines,
        block_chars=len(on_prompt) - len(off_prompt),
        block_rows=rows,
        recorded_prompt=render.prompt,
        served_lines=served_lines,
    )


# ---------------------------------------------------------------------------
# One meeting
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldCase:
    """What the field did for one ejection."""

    ejected: PlayerId
    eject_voters: int
    misjudged: bool
    witness_meeting: bool
    c_reaches: bool
    reaches: bool
    reaches_served: bool | None
    reaches_charge: bool
    every_pair_reaches: bool
    reason: FieldReason | None


@dataclass(frozen=True)
class FieldMeeting:
    """One meeting's field counts, keyed by (seed, meeting)."""

    seed: int
    meeting: int
    ballots: int
    ballots_with_block: int
    lines_served: int
    block_chars: int
    lines: int
    steps: tuple[tuple[RouteReading, int], ...]
    left_out: int
    every_pair_lines: int
    harness: rcr.MeetingRecord
    case: FieldCase | None


def _spot_key(
    tick: int, rooms: Sequence[str] | frozenset[str]
) -> tuple[int, frozenset[str]]:
    return tick, frozenset(rooms)


def changes_left_out(
    placements: Sequence[Placement],
    subjects: Sequence[PlayerId],
    *,
    regroup_ticks: frozenset[int],
) -> int:
    """Consecutive changes of room among the subjects' places that neither walk nor cross."""

    left = 0
    for subject in subjects:
        spots = _route_spots(placements_of(placements, subject))
        for earlier, later in zip(spots, spots[1:], strict=False):
            if earlier.rooms & later.rooms:
                continue
            if reconcilable(earlier, later, regroup_ticks=regroup_ticks) is None:
                left += 1
    return left


def every_pair_reconciles(
    placements: Sequence[Placement], subject: PlayerId, *, regroup_ticks: frozenset[int]
) -> bool:
    """Whether any pair of the subject's stated places of the field's kinds reconciles."""

    spots = _route_spots(placements_of(placements, subject))
    return any(
        reconcilable(earlier, later, regroup_ticks=regroup_ticks) is not None
        for index, earlier in enumerate(spots)
        for later in spots[index + 1 :]
    )


def _field_reason(
    pairs: Sequence[tuple[Placement, Placement]], *, every_pair: bool
) -> FieldReason:
    in_kinds = [
        pair for pair in pairs if all(end.kind in ROUTE_PLACEMENT_KINDS for end in pair)
    ]
    if not in_kinds:
        return "kind"
    if every_pair:
        return "consecutive"
    return "residual"


def read_field_meeting(
    inputs: rcr.MeetingInputs,
    *,
    record: rcr.MeetingRecord,
    readings: Sequence[BallotReading],
    served: bool,
) -> FieldMeeting:
    """Count one meeting under the field, beside the harness's record of it."""

    universe = spoken_placements(inputs.transcript)
    roster = sorted(inputs.roster)
    by_voter = {reading.voter: reading for reading in readings}
    if set(by_voter) != set(roster) or len(by_voter) != len(readings):
        raise RouteLinesReplayError(
            f"seed {record.seed} meeting {record.meeting}: one ballot render per "
            "participant is expected"
        )
    distinct: dict[PlayerId, RouteLine] = {}
    for reading in readings:
        for line in reading.lines:
            if distinct.setdefault(line.subject, line) != line:
                raise RouteLinesReplayError(
                    f"seed {record.seed} meeting {record.meeting}: two voters hold "
                    f"different lines about {line.subject}"
                )
    steps = Counter(step.reading for line in distinct.values() for step in line.steps)
    case = None
    harness_case = record.case
    if inputs.ejected is not None and harness_case is not None:
        ejected = inputs.ejected
        eject_voters = sorted(
            {ballot.voter for ballot in inputs.ballots if ballot.target == ejected}
        )
        about = [
            line
            for voter in eject_voters
            for line in by_voter[voter].lines
            if line.subject == ejected
        ]
        served_about = (
            [
                line
                for voter in eject_voters
                for line in (by_voter[voter].served_lines or ())
                if line.subject == ejected
            ]
            if served
            else None
        )
        charges = rcr.charges_against(
            ejected,
            ballots=inputs.ballots,
            contradictions=inputs.contradictions,
            universe=universe,
        )
        charged = {
            _spot_key(spot.tick, spot.rooms)
            for charge in charges
            for spot in charge.placements
        }
        reaches = bool(about)
        every_pair = bool(eject_voters) and every_pair_reconciles(
            universe, ejected, regroup_ticks=inputs.regroup_ticks
        )
        pairs = rcr.misjudging_pairs(
            placements_of(universe, ejected),
            frozenset().union(*(charge.placements for charge in charges)),
            regroup_ticks=inputs.regroup_ticks,
        )
        case = FieldCase(
            ejected=ejected,
            eject_voters=len(eject_voters),
            misjudged=harness_case.misjudged,
            witness_meeting=record.witness_meeting,
            c_reaches=harness_case.check("c").reaches,
            reaches=reaches,
            reaches_served=bool(served_about) if served_about is not None else None,
            reaches_charge=any(
                _spot_key(step.from_tick, step.from_rooms) in charged
                or _spot_key(step.to_tick, step.to_rooms) in charged
                for line in about
                for step in line.steps
            ),
            every_pair_reaches=every_pair,
            reason=(
                _field_reason(pairs, every_pair=every_pair)
                if harness_case.misjudged and not reaches
                else None
            ),
        )
    return FieldMeeting(
        seed=record.seed,
        meeting=record.meeting,
        ballots=len(readings),
        ballots_with_block=sum(1 for reading in readings if reading.lines),
        lines_served=sum(len(reading.lines) for reading in readings),
        block_chars=sum(reading.block_chars for reading in readings),
        lines=len(distinct),
        steps=tuple((reading, steps[reading]) for reading in READINGS),
        left_out=changes_left_out(universe, roster, regroup_ticks=inputs.regroup_ticks),
        every_pair_lines=sum(
            1
            for subject in roster
            if every_pair_reconciles(
                universe, subject, regroup_ticks=inputs.regroup_ticks
            )
        ),
        harness=record,
        case=case,
    )


def added_input_tokens(
    entry: MeetingReplayEntry, readings: Sequence[BallotReading]
) -> Fraction:
    """Each recorded ballot call's input tokens times its block's share of its prompt.

    A ballot call is a recorded call by a voter whose prompt begins with that
    voter's render as recorded (a retry appends feedback to it).
    """

    added = Fraction(0)
    for reading in readings:
        for call in entry.llm_calls:
            if call.agent_id == reading.voter and call.prompt.startswith(
                reading.recorded_prompt
            ):
                added += Fraction(
                    call.input_tokens * reading.block_chars, len(call.prompt)
                )
    return added


# ---------------------------------------------------------------------------
# One game, one column
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GameReading:
    """Every meeting of one game, the texts the scan seeks, and its token counts."""

    meetings: tuple[FieldMeeting, ...]
    texts: frozenset[str]
    recorded_input_tokens: int
    recorded_ballot_input_tokens: int
    added_input_tokens: Fraction


def walk_with_captures(
    path: Path,
    *,
    label: str,
    seed: int,
) -> Iterator[
    tuple[ReconstructedMeeting, tuple[BallotRender, ...], VotePromptRenderer]
]:
    """The route-check replay's faithful walk, each meeting with its ballot renders."""

    renderers, votes = capturing_renderers(_canonical_renderers())
    for meeting in rcr.walk_game(path, label=label, seed=seed, renderers=renderers):
        vote = votes[meeting.set_name]
        captured = vote.take()
        for other in votes.values():
            if other.take():
                raise RouteLinesReplayError(
                    f"{label} seed {seed}: a ballot rendered through another set"
                )
        yield meeting, captured, vote.inner


def read_game(path: Path, *, label: str, game: GameFacts) -> GameReading:
    """Every meeting of one game: the harness's record and the field's, side by side."""

    seed = game.seed
    entries = read_all_entries(path)
    recorded = recorded_experiment_config(entries)
    served = _column_mode(path) == "served"
    earlier: list[int] = []
    meetings: list[FieldMeeting] = []
    texts: set[str] = set()
    added = Fraction(0)
    ballot_tokens = 0
    for index, (meeting, captured, inner) in enumerate(
        walk_with_captures(path, label=label, seed=seed)
    ):
        if index >= len(game.meetings):
            raise RouteLinesReplayError(
                f"{label} seed {seed} meeting {index}: the census holds no such meeting"
            )
        fact = game.meetings[index]
        if fact.meeting_id != meeting.meeting_id or fact.tick != meeting.entry.tick:
            raise RouteLinesReplayError(
                f"{label} seed {seed} meeting {index}: the census and the walk read "
                "different meetings"
            )
        regroup = derive_regroup_ticks(recorded, earlier)
        inputs = rcr.meeting_inputs(meeting, regroup_ticks=regroup)
        record, read = rcr.read_meeting(
            inputs,
            seed=seed,
            index=index,
            tick=fact.tick,
            kind=rcr.meeting_kind(fact),
            witness_meeting=rcr.is_witness_meeting(
                fact,
                kills=game.kills,
                previous_tick=game.meetings[index - 1].tick if index else None,
            ),
        )
        readings = [
            read_ballot(render, inner=inner, regroup_ticks=regroup, served=served)
            for render in captured
        ]
        meetings.append(
            read_field_meeting(inputs, record=record, readings=readings, served=served)
        )
        texts.update(read)
        texts.update(row for reading in readings for row in reading.block_rows)
        added += added_input_tokens(meeting.entry, readings)
        ballot_tokens += sum(
            call.input_tokens
            for call in meeting.entry.llm_calls
            for reading in readings
            if call.agent_id == reading.voter
            and call.prompt.startswith(reading.recorded_prompt)
        )
        earlier.append(meeting.entry.tick)
    if len(meetings) != len(game.meetings):
        raise RouteLinesReplayError(
            f"{label} seed {seed}: the census holds {len(game.meetings)} meetings and "
            f"the walk read {len(meetings)}"
        )
    return GameReading(
        meetings=tuple(meetings),
        texts=frozenset(texts),
        recorded_input_tokens=sum(
            call.input_tokens
            for entry in entries
            if isinstance(entry, MeetingReplayEntry)
            for call in entry.llm_calls
        ),
        recorded_ballot_input_tokens=ballot_tokens,
        added_input_tokens=added,
    )


@dataclass(frozen=True)
class SetReading:
    """One column's meetings, scan texts, token counts and mode."""

    meetings: tuple[FieldMeeting, ...]
    texts: frozenset[str]
    recorded_input_tokens: int
    recorded_ballot_input_tokens: int
    added_input_tokens: Fraction
    mode: ColumnMode


def _column_mode(path: Path) -> ColumnMode:
    """Served when the game recorded the field ON, rendered otherwise."""

    config = recorded_experiment_config(read_all_entries(path))
    if config is not None and config.route_lines_version is not None:
        return "served"
    return "rendered"


def read_set(set_dir: Path, *, label: str, census: CensusInputs) -> SetReading:
    """Every game of one column's set, against that set's census."""

    games = {game.seed: game for game in census.games}
    seeds = seeds_on_disk(set_dir)
    if sorted(games) != seeds:
        raise RouteLinesReplayError(
            f"{label}: the census and the set hold different seeds"
        )
    readings = [
        read_game(set_dir / f"replay-seed-{seed}.jsonl", label=label, game=games[seed])
        for seed in seeds
    ]
    modes = {_column_mode(set_dir / f"replay-seed-{seed}.jsonl") for seed in seeds}
    if len(modes) != 1:
        raise RouteLinesReplayError(f"{label}: its games record the field both ways")
    return SetReading(
        meetings=tuple(m for reading in readings for m in reading.meetings),
        texts=frozenset().union(*(reading.texts for reading in readings)),
        recorded_input_tokens=sum(r.recorded_input_tokens for r in readings),
        recorded_ballot_input_tokens=sum(
            r.recorded_ballot_input_tokens for r in readings
        ),
        added_input_tokens=sum((r.added_input_tokens for r in readings), Fraction(0)),
        mode=modes.pop(),
    )


# ---------------------------------------------------------------------------
# Parity with the committed route-check replay
# ---------------------------------------------------------------------------


def committed_column(
    route_check: Mapping[str, object], label: str
) -> Mapping[str, object] | None:
    """The committed route-check column ``label``, or ``None`` when it records none."""

    for column in cast(Sequence[Mapping[str, object]], route_check["columns"]):
        if column["label"] == label:
            return column
    return None


def require_parity(
    source: rcr.ColumnSource,
    meetings: Sequence[FieldMeeting],
    *,
    route_check: Mapping[str, object],
) -> bool:
    """Hold the harness's recomputed records equal to the committed column's.

    Returns whether the committed route-check JSON records this column. When it
    does, the column's sha, path and tree must be the ones it pins, and every
    recomputed meeting record must equal the committed one; otherwise this raises.
    """

    committed = committed_column(route_check, source.label)
    if committed is None:
        return False
    pinned = (committed["sha"], committed["path"], committed["tree"])
    if pinned != (source.sha, source.path, source.tree):
        raise RouteLinesReplayError(
            f"column {source.label}: the route-check replay pins other bytes for it"
        )
    recomputed = [rcr._record_payload(meeting.harness) for meeting in meetings]
    recorded = cast(Sequence[Mapping[str, object]], committed["meetings"])
    if len(recomputed) != len(recorded):
        raise RouteLinesReplayError(
            f"column {source.label}: the route-check replay records "
            f"{len(recorded)} meetings and the walk read {len(recomputed)}"
        )
    for found, expected in zip(recomputed, recorded, strict=True):
        if found != expected:
            raise RouteLinesReplayError(
                f"column {source.label} seed {found['seed']} meeting "
                f"{found['meeting']}: the recomputed route-check record differs from "
                "the committed one"
            )
    return True


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _case_counts(cases: Sequence[FieldCase], *, served: bool) -> dict[str, object]:
    misjudged = [case for case in cases if case.misjudged]
    witness = [case for case in misjudged if case.witness_meeting]
    counts: dict[str, object] = {
        "ejections": len(cases),
        "M": len(misjudged),
        "W": len(witness),
        "c_reaches_M": sum(1 for case in misjudged if case.c_reaches),
        "c_reaches_W": sum(1 for case in witness if case.c_reaches),
        "field_reaches_all": sum(1 for case in cases if case.reaches),
        "field_reaches_M": sum(1 for case in misjudged if case.reaches),
        "field_reaches_W": sum(1 for case in witness if case.reaches),
        "field_reaches_charge_M": sum(1 for case in misjudged if case.reaches_charge),
        "field_only_M": sum(
            1 for case in misjudged if case.reaches and not case.c_reaches
        ),
        "c_only_M": sum(1 for case in misjudged if case.c_reaches and not case.reaches),
        "every_pair_reaches_M": sum(1 for case in misjudged if case.every_pair_reaches),
        "every_pair_reaches_W": sum(1 for case in witness if case.every_pair_reaches),
        "unreached_reasons": {
            reason: sum(1 for case in misjudged if case.reason == reason)
            for reason in FIELD_REASONS
        },
    }
    if served:
        counts["field_reaches_M_served"] = sum(
            1 for case in misjudged if case.reaches_served
        )
        counts["field_reaches_W_served"] = sum(
            1 for case in witness if case.reaches_served
        )
    return counts


def _ejection_classes(
    meeting: FieldMeeting, roles: Mapping[PlayerId, Role]
) -> tuple[rcr.EjectionClass, ...]:
    harness_case = meeting.harness.case
    if harness_case is None:
        raise ValueError("a class is an ejection's")
    return rcr.ejection_class(meeting.harness, harness_case, roles)


def column_counts(
    reading: SetReading, roles: Mapping[int, Mapping[PlayerId, Role]]
) -> dict[str, object]:
    """One column's whole-set counts, and the cases set out by ejection class."""

    meetings = reading.meetings
    served = reading.mode == "served"
    cases = [meeting.case for meeting in meetings if meeting.case is not None]
    ballots = sum(meeting.ballots for meeting in meetings)
    block_chars = sum(meeting.block_chars for meeting in meetings)
    with_block = sum(meeting.ballots_with_block for meeting in meetings)
    added = round(reading.added_input_tokens)
    projected = reading.recorded_input_tokens + (0 if served else added)
    counts: dict[str, object] = {
        "meetings": len(meetings),
        "ballots": ballots,
        "ballots_with_block": with_block,
        "lines": sum(meeting.lines for meeting in meetings),
        "lines_served": sum(meeting.lines_served for meeting in meetings),
        "steps": {
            reading_name: sum(dict(meeting.steps)[reading_name] for meeting in meetings)
            for reading_name in READINGS
        },
        "left_out_changes": sum(meeting.left_out for meeting in meetings),
        "every_pair_lines": sum(meeting.every_pair_lines for meeting in meetings),
        "block_chars": block_chars,
        "block_chars_per_ballot": round(block_chars / ballots, 1) if ballots else 0.0,
        "block_chars_per_ballot_with_block": round(block_chars / with_block, 1)
        if with_block
        else 0.0,
        "tokens": {
            "recorded_input": reading.recorded_input_tokens,
            "recorded_ballot_input": reading.recorded_ballot_input_tokens,
            "added_input": added,
            "projected_input": projected,
            "ceiling": INPUT_TOKEN_CEILING,
            "hard_stop": INPUT_TOKEN_HARD_STOP,
            "within_hard_stop": projected <= INPUT_TOKEN_HARD_STOP,
        },
    }
    counts.update(_case_counts(cases, served=served))
    by_class: dict[str, object] = {}
    for name in rcr.EJECTION_CLASSES:
        members = [
            meeting.case
            for meeting in meetings
            if meeting.case is not None
            and name in _ejection_classes(meeting, roles[meeting.seed])
        ]
        by_class[name] = _case_counts(members, served=served)
    counts["classes"] = by_class
    return counts


def _meeting_payload(meeting: FieldMeeting) -> dict[str, object]:
    payload: dict[str, object] = {
        "seed": meeting.seed,
        "meeting": meeting.meeting,
        "ballots": meeting.ballots,
        "ballots_with_block": meeting.ballots_with_block,
        "lines": meeting.lines,
        "lines_served": meeting.lines_served,
        "steps": dict(meeting.steps),
        "left_out_changes": meeting.left_out,
        "every_pair_lines": meeting.every_pair_lines,
        "block_chars": meeting.block_chars,
    }
    case = meeting.case
    if case is not None:
        payload["case"] = {
            "ejected": case.ejected,
            "eject_voters": case.eject_voters,
            "misjudged": case.misjudged,
            "witness_meeting": case.witness_meeting,
            "c_reaches": case.c_reaches,
            "reaches": case.reaches,
            "reaches_served": case.reaches_served,
            "reaches_charge": case.reaches_charge,
            "every_pair_reaches": case.every_pair_reaches,
            "reason": case.reason,
        }
    return payload


def column_payload(
    source: rcr.ColumnSource,
    *,
    reading: SetReading,
    roles: Mapping[int, Mapping[PlayerId, Role]],
    parity: bool,
) -> dict[str, object]:
    """One column's JSON: provenance, mode, parity, counts and meetings."""

    return {
        "label": source.label,
        "commit": source.commit,
        "sha": source.sha,
        "path": source.path,
        "tree": source.tree,
        "declared_config": rcr.declared_config_path(source.label),
        "mode": reading.mode,
        "route_check_parity": parity,
        "games": len(roles),
        "seeds": rcr.seed_ranges(roles),
        "roster": rcr.column_roster(source.label, roles),
        "all": column_counts(reading, roles),
        "meetings": [_meeting_payload(meeting) for meeting in reading.meetings],
    }


def build_payload(columns: Sequence[dict[str, object]]) -> dict[str, object]:
    labels = [cast(str, column["label"]) for column in columns]
    return {
        "schema_version": SCHEMA_VERSION,
        "instrument": "experiments/lab/route_lines_replay.py",
        "route_check_instrument": "experiments/lab/route_check_replay.py",
        "governing_column": "r2" if "r2" in labels else None,
        "columns": columns,
    }


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------


def _of(numerator: object, denominator: object) -> str:
    return f"{numerator} of {denominator}"


def _column_section(column: Mapping[str, object]) -> list[str]:
    whole = cast(Mapping[str, object], column["all"])
    tokens = cast(Mapping[str, object], whole["tokens"])
    steps = cast(Mapping[str, int], whole["steps"])
    reasons = cast(Mapping[str, int], whole["unreached_reasons"])
    classes = cast(Mapping[str, Mapping[str, object]], whole["classes"])
    served = column["mode"] == "served"
    out = [
        f"## Column {column['label']}",
        "",
        f"`{column['path']}` at `{column['sha']}` (tree `{column['tree']}`); declared "
        f"config: {column['declared_config'] or 'none'}; {column['games']} games, seeds "
        f"{column['seeds']}. "
        + (
            "The ballots recorded the route lines, so the block is read as served "
            "and held equal to the lines its inputs build."
            if served
            else "The ballots recorded no route lines, so each is rendered again with "
            "them and held equal to the recorded render once the block is removed."
        )
        + (
            " The route-check replay's per-meeting records for this column were "
            "recomputed and equal its committed ones."
            if column["route_check_parity"]
            else " The route-check replay records no such column, so nothing is held "
            "against it."
        ),
        "",
    ]
    reach_rows: list[tuple[object, ...]] = [
        ("(c) reference", whole["c_reaches_M"], whole["c_reaches_W"]),
        ("route lines", whole["field_reaches_M"], whole["field_reaches_W"]),
        (
            "route lines, every pair (informational)",
            whole["every_pair_reaches_M"],
            whole["every_pair_reaches_W"],
        ),
    ]
    if served:
        reach_rows.append(
            (
                "route lines, as served",
                whole["field_reaches_M_served"],
                whole["field_reaches_W_served"],
            )
        )
    out.extend(
        rcr._table(
            (
                "reading",
                f"reaches misjudged (M = {whole['M']})",
                f"reaches misjudged at witness meetings (W = {whole['W']})",
            ),
            [
                (name, _of(m, whole["M"]), _of(w, whole["W"]))
                for name, m, w in reach_rows
            ],
        )
    )
    out.append("")
    out.append(
        f"Of {whole['ejections']} ejections, the route lines reach "
        f"{whole['field_reaches_all']}. Over the misjudged cases they reach "
        f"{whole['field_only_M']} that (c) does not and miss {whole['c_only_M']} that "
        f"(c) reaches; {whole['field_reaches_charge_M']} of their misjudged reaches put "
        "a step on a charged place. Reaching is showing a line, not changing a vote."
    )
    out.append("")
    out.append("Unreached misjudged cases by reason:")
    out.append("")
    out.extend(
        rcr._table(
            ("reason", "cases"),
            [(_REASON_NAMES[reason], reasons[reason]) for reason in FIELD_REASONS],
        )
    )
    out.append("")
    out.append(
        "By ejection class, as description only (an ejected witness is innocent too):"
    )
    out.append("")
    out.extend(
        rcr._table(
            ("class", "ejections", "misjudged", "(c) reaches", "route lines reach"),
            [
                (
                    name.replace("_", " "),
                    classes[name]["ejections"],
                    classes[name]["M"],
                    classes[name]["c_reaches_M"],
                    classes[name]["field_reaches_M"],
                )
                for name in rcr.EJECTION_CLASSES
            ],
        )
    )
    out.append("")
    out.append("What the block holds and costs:")
    out.append("")
    out.extend(
        rcr._table(
            ("count", "value"),
            [
                ("meetings", whole["meetings"]),
                ("ballots", whole["ballots"]),
                ("ballots carrying the block", whole["ballots_with_block"]),
                ("lines, one per player and meeting", whole["lines"]),
                ("lines served over all ballots", whole["lines_served"]),
                ("steps reading walking fits", steps["walking_fits"]),
                ("steps reading the regroup between", steps["regroup_between"]),
                (
                    "consecutive changes of room left out (neither walk nor regroup)",
                    whole["left_out_changes"],
                ),
                (
                    "players with a reconcilable pair under every pair (informational)",
                    whole["every_pair_lines"],
                ),
                ("block characters, all ballots", whole["block_chars"]),
                ("block characters per ballot", whole["block_chars_per_ballot"]),
                (
                    "block characters per ballot carrying the block",
                    whole["block_chars_per_ballot_with_block"],
                ),
            ],
        )
    )
    out.append("")
    out.extend(
        rcr._table(
            ("input tokens", "count"),
            [
                ("recorded, every meeting call", tokens["recorded_input"]),
                ("recorded, ballot calls", tokens["recorded_ballot_input"]),
                (
                    "already served in the recorded ballots"
                    if served
                    else "projected added by the block",
                    tokens["added_input"],
                ),
                ("projected total", tokens["projected_input"]),
                ("ceiling", tokens["ceiling"]),
                ("hard stop (90 percent of the ceiling)", tokens["hard_stop"]),
                ("projected total within the hard stop", tokens["within_hard_stop"]),
            ],
        )
    )
    out.append("")
    return out


def render_report(payload: Mapping[str, object]) -> str:
    """The lab report, a pure function of the JSON payload."""

    columns = cast(Sequence[Mapping[str, object]], payload["columns"])
    out = [
        "# Route-lines replay",
        "",
        "Offline and count-only (`experiments/lab/route_lines_replay.py`). Each column "
        "is walked through the route-check replay's faithful walk, and each recorded "
        "ballot is read with the route lines on. M counts ejections resting on a charge "
        "the map or the public regroup reconciles, W those at meetings a kill witness "
        "opened, and the (c) reference is the route-check replay's reading. A case is "
        "reached when some voter who cast an eject ballot for the ejected player holds "
        "a line about them. The projected added input tokens are each recorded ballot "
        "call's input tokens times its block's share of the prompt's characters: a "
        "planning figure on recorded bytes, not a prediction of a model. Columns are "
        "read alone and never pooled"
        + (
            f"; {payload['governing_column']} governs the pre-spend reading."
            if payload["governing_column"]
            else "."
        ),
        "",
    ]
    for column in columns:
        out.extend(_column_section(column))
    return "\n".join(out).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# Running and checking
# ---------------------------------------------------------------------------


def run_columns(
    repo: Path,
    sources: Sequence[rcr.ColumnSource],
    *,
    route_check: Mapping[str, object],
) -> tuple[dict[str, object], frozenset[str]]:
    """Read every column from its exact bytes; return the payload and the scan set."""

    labels = [source.label for source in sources]
    if len(set(labels)) != len(labels):
        raise RouteLinesReplayError(
            "a label was given twice: columns are read alone and never pooled"
        )
    order = list(rcr.COLUMN_LABELS)
    columns: list[dict[str, object]] = []
    forbidden: set[str] = set()
    for source in sorted(sources, key=lambda s: order.index(s.label)):
        config = rcr.declared_config(repo, source)
        with tempfile.TemporaryDirectory(prefix="route-lines-replay-") as scratch:
            set_dir = rcr.materialize(repo, source, Path(scratch))
            rcr.require_declared_settings(set_dir, label=source.label, config=config)
            census = load_census_inputs(set_dir)
            reading = read_set(set_dir, label=source.label, census=census)
            parity = require_parity(source, reading.meetings, route_check=route_check)
            forbidden.update(rcr.forbidden_strings(set_dir))
            forbidden.update(reading.texts)
            roles = {game.seed: game.roles for game in census.games}
            columns.append(
                column_payload(source, reading=reading, roles=roles, parity=parity)
            )
    return build_payload(columns), frozenset(forbidden)


def outputs_for(
    repo: Path,
    sources: Sequence[rcr.ColumnSource],
    *,
    route_check: Mapping[str, object],
) -> tuple[str, str]:
    """The JSON and the report for ``sources``, scanned before anyone writes them."""

    payload, forbidden = run_columns(repo, sources, route_check=route_check)
    json_text = rcr.serialize(payload)
    report = render_report(payload)
    try:
        rcr.scan_outputs((json_text, report), forbidden)
    except rcr.RouteCheckReplayError as error:
        raise RouteLinesReplayError(str(error)) from error
    return json_text, report


def _load_route_check(path: Path) -> Mapping[str, object]:
    return cast(Mapping[str, object], json.loads(path.read_text(encoding="utf-8")))


def check(
    repo: Path, json_path: Path, report_path: Path, *, route_check_path: Path
) -> list[str]:
    """Recompute both outputs from the recorded shas; return what differs."""

    committed_json = json_path.read_text(encoding="utf-8")
    try:
        sources = rcr.recorded_sources(json.loads(committed_json), repo)
    except rcr.RouteCheckReplayError as error:
        raise RouteLinesReplayError(str(error)) from error
    json_text, report = outputs_for(
        repo, sources, route_check=_load_route_check(route_check_path)
    )
    problems = []
    if json_text != committed_json:
        problems.append(f"{json_path}: the recomputed JSON differs")
    if report != report_path.read_text(encoding="utf-8"):
        problems.append(f"{report_path}: the recomputed report differs")
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="LABEL=COMMIT:PATH",
        help="one column: s9, r1, r2 or r3, a commit, and a set path (repeatable)",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-report", type=Path, default=None)
    parser.add_argument(
        "--check",
        action="store_true",
        help="recompute the JSON and report from the commits the JSON records",
    )
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--route-check-json",
        type=Path,
        default=DEFAULT_ROUTE_CHECK_JSON,
        help="the committed route-check replay JSON the parity check reads",
    )
    parser.add_argument("--repo", type=Path, default=rcr._REPO_ROOT)
    args = parser.parse_args(argv)
    started = time.monotonic()
    try:
        if args.check:
            if args.set:
                raise RouteLinesReplayError(
                    "--check takes its columns from the JSON, never from --set"
                )
            problems = check(
                args.repo,
                args.json,
                args.report,
                route_check_path=args.route_check_json,
            )
            for problem in problems:
                print(problem, file=sys.stderr)
            if problems:
                return 1
            print(
                f"route-lines replay: reproduced ({time.monotonic() - started:.1f} s)"
            )
            return 0
        if not args.set or args.out_json is None or args.out_report is None:
            raise RouteLinesReplayError(
                "a run needs at least one --set, --out-json and --out-report"
            )
        try:
            requests = [rcr.parse_column_request(text) for text in args.set]
            sources = [rcr.resolve_column(args.repo, request) for request in requests]
        except rcr.RouteCheckReplayError as error:
            raise RouteLinesReplayError(str(error)) from error
        json_text, report = outputs_for(
            args.repo, sources, route_check=_load_route_check(args.route_check_json)
        )
    except (RouteLinesReplayError, rcr.RouteCheckReplayError) as error:
        print(f"route-lines replay: {error}", file=sys.stderr)
        return 1
    args.out_json.write_text(json_text, encoding="utf-8")
    args.out_report.write_text(report, encoding="utf-8")
    print(
        f"route-lines replay: wrote {args.out_json} and {args.out_report} "
        f"({time.monotonic() - started:.1f} s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
