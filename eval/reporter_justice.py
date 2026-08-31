"""How a committed replay set treats the player who reported the body.

The reporter is the one seat the meeting hands a structural disadvantage: they
speak first, they are the only speaker whose turn is spent before anyone can
answer them, and until the reporter-voice lever the base rate that says
"reporting is weakly exculpatory" reached only the ballot. This module measures
what that costs, from recorded bytes alone, so the class has cells rather than
an impression:

* how many meetings a body opened and how many a button did;
* what role the reporter held (an impostor that reports its own kill would make
  the exculpation a laundering channel, so the census is the premise check);
* how often the reporter was ejected, against the same rate for an innocent
  non-reporter and for an impostor, with the relative risk;
* how much of the set's innocent-ejection total the reporter accounts for (a
  guilty reporter's conviction is counted as exposure and NOT as a wrongful
  ejection, so the two never blur);
* how often crew and impostors aim at the reporter, in SPEECH and in BALLOTS
  (the two follow through at different rates, and the ballot half is the one
  that convicts);
* how often the exculpation is INVOKED rather than merely rendered;
* how many meetings carry a non-reporter who found the same body, split by role.

Reading discipline
==================

Everything comes from the committed JSONL: the meeting kind from the recorded
tick action stream (an applied ``report`` / ``emergency`` by the meeting's own
opener), roles from :func:`eval.validity.roles_by_seed` (re-seeding the engine,
never a prompt-string marker), and speech / ballots / rendered memory from the
recorded transcript, ballots and prompts. No eval report is consulted and no
model is called, so two runs over the same bytes return identical cells.

The invocation cells are an UPPER BOUND, and deliberately so. A rationale
"invokes" the exculpation when it mentions a report AND carries one of the
hinges in :data:`EXCULPATORY_HINGE_TERMS` -- a stated list, not an implicit one,
because a filing that leaves the hinge list implicit cannot be reproduced and
the first attempt at this cell missed by about fourfold for exactly that reason.
A hand read of the Wave-0 hits found roughly two thirds to three quarters of
them to be genuine invocations rather than incidental phrasing, so read the
hinge count as a ceiling on real use.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from engine.entities import PlayerId, Role
from eval.validity import resolve_roster_knobs, roles_by_seed, seeds_on_disk
from meetings.schemas import AccusationClaim
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    read_all_entries,
)

#: Engine action types that open a meeting, mapped to the kind they open.
_TRIGGER_ACTION_KINDS: Final[Mapping[str, str]] = {
    "report": "body_report",
    "emergency": "emergency",
}

#: An applied action is the only one that opened anything: on the committed
#: meeting-trigger ticks 6.13% of recorded actions were submitted and rejected,
#: reports and emergency calls among them, so reading the submission would
#: mis-classify meetings the engine never opened that way.
_APPLIED: Final[str] = "applied"

#: The §6.6 memory line a first-hand body discovery renders as. Parsed rather
#: than re-derived so the census counts what the speaker was actually shown.
_DISCOVERY_LINE: Final[re.Pattern[str]] = re.compile(
    r"\[tick (?P<tick>\d+)\] You discovered (?P<victim>[^']+)'s body in (?P<room>\w+)\."
)

#: A discovery counts as "at the body when the meeting opened" if its tick is the
#: trigger tick or the one before it. Perception stamps the row on the packet's
#: tick, which is one early for a player who saw the corpse on the approach: 18
#: of 625 reporter discovery lines in the Wave-0 census sat at trigger tick - 1,
#: so a strict equality test silently drops them.
DISCOVERY_WINDOW_TICKS: Final[int] = 1

#: The body id ``engine/rules.py`` mints for a corpse. Parsed to recover WHICH
#: corpse a report was made on, checked against the roster at every call so a
#: format change fails loud instead of emptying the co-discovery cell.
_BODY_ID: Final[re.Pattern[str]] = re.compile(r"^body-(?P<victim>.+)-(?P<tick>\d+)$")

#: A rationale or a spoken turn "mentions a report" when it contains this stem,
#: which covers report / reported / reporting / reporter in one test.
REPORT_MENTION_TERM: Final[str] = "report"

#: The hinges that mark the self-report base rate being REASONED FROM rather
#: than the word "report" merely appearing. Stated as data so the cell is
#: reproducible and so a later reader can widen it deliberately instead of
#: guessing what an earlier one meant.
EXCULPATORY_HINGE_TERMS: Final[tuple[str, ...]] = (
    "exculpat",
    "not by itself",
    "first to the scene",
    "own kill",
    "self-report",
    "would not report",
    "wouldn't report",
    "unlikely to report",
    "no reason to report",
    "just because",
    "expected for the reporter",
    "didn't just",
    "did not just",
    "weak evidence",
    "not proof",
    "isn't proof",
)


class ReporterJusticeError(RuntimeError):
    """A committed replay set does not support a reporter-justice reading."""


@dataclass(frozen=True)
class ReporterJusticeCells:
    """The reporter-justice cells for ONE committed replay set.

    Counts only -- every rate is derived by the properties below, so a caller
    reading the raw cells and a caller reading a rate can never disagree about
    the denominator.
    """

    set_name: str
    games: int
    meetings: int
    body_report_meetings: int
    emergency_meetings: int

    reporter_crewmate_meetings: int
    reporter_impostor_meetings: int

    # The set's whole ejection ledger, over EVERY meeting: the denominator a
    # published innocent-ejection count is quoted against.
    ejections: int
    innocent_ejections: int
    impostor_ejections: int

    # Per-slot exposure, over BODY-REPORT meetings only -- there is no reporter
    # anywhere else, so a rate pooled over emergency meetings would compare a
    # seat that exists against one that does not. One slot per living
    # participant per meeting; the slot classes partition that roster.
    reporter_slots: int
    reporter_ejections: int
    reporter_innocent_ejections: int
    innocent_non_reporter_slots: int
    innocent_non_reporter_ejections: int
    impostor_slots: int
    impostor_slot_ejections: int

    # Aim at the reporter, in speech and in ballots, split by the speaker's role.
    crew_accusations: int
    crew_accusations_at_reporter: int
    impostor_accusations: int
    impostor_accusations_at_reporter: int
    crew_ballots: int
    crew_ballots_at_reporter: int
    impostor_ballots: int
    impostor_ballots_at_reporter: int

    # Invocation: the exculpation reasoned from, not merely rendered.
    ballot_rationales: int
    ballot_rationales_mentioning_report: int
    ballot_rationales_with_hinge: int
    speech_turns: int
    speech_turns_mentioning_report: int
    speech_turns_with_hinge: int
    speech_turns_with_hinge_by_reporter: int

    # Co-discovery: a NON-reporter holding the same discovery row at the trigger.
    meetings_with_co_discoverer: int
    co_discoverer_slots_crewmate: int
    co_discoverer_slots_impostor: int

    @property
    def reporter_ejection_rate(self) -> float:
        """Ejections per reporter slot; 0.0 when the set opened no body report."""

        return _rate(self.reporter_ejections, self.reporter_slots)

    @property
    def innocent_non_reporter_ejection_rate(self) -> float:
        return _rate(
            self.innocent_non_reporter_ejections, self.innocent_non_reporter_slots
        )

    @property
    def impostor_ejection_rate(self) -> float:
        return _rate(self.impostor_slot_ejections, self.impostor_slots)

    @property
    def reporter_relative_risk(self) -> float:
        """Reporter ejection rate over the innocent non-reporter's.

        A zero baseline is NOT zero risk, and reporting it as ``0.0`` would
        reverse the reading of the one shape the class cares about -- a set where
        reporters are ejected and no other innocent seat ever is. So a zero
        baseline with reporter ejections returns :data:`math.inf` (unbounded), and
        a zero baseline with no reporter ejection returns :data:`math.nan` (no
        evidence either way). :func:`render_reporter_justice` prints both in
        words; a caller comparing numbers should test ``math.isfinite`` first.
        """

        baseline = self.innocent_non_reporter_ejection_rate
        if baseline > 0.0:
            return self.reporter_ejection_rate / baseline
        return math.inf if self.reporter_ejections else math.nan

    @property
    def reporter_share_of_innocent_ejections(self) -> float:
        """How much of the set's WRONGFUL-ejection total the reporter accounts for.

        Numerator is :attr:`reporter_innocent_ejections`, not every reporter
        ejection: a guilty reporter convicted is a correct verdict and belongs to
        neither side of this ratio. ``0.0`` when the set ejected no innocent at
        all -- a zero over zero, which :func:`render_reporter_justice` prints as
        "n/a" rather than as a share.
        """

        return _rate(self.reporter_innocent_ejections, self.innocent_ejections)

    @property
    def crew_accusation_at_reporter_share(self) -> float:
        return _rate(self.crew_accusations_at_reporter, self.crew_accusations)

    @property
    def impostor_accusation_at_reporter_share(self) -> float:
        return _rate(self.impostor_accusations_at_reporter, self.impostor_accusations)

    @property
    def crew_ballot_at_reporter_share(self) -> float:
        return _rate(self.crew_ballots_at_reporter, self.crew_ballots)

    @property
    def impostor_ballot_at_reporter_share(self) -> float:
        return _rate(self.impostor_ballots_at_reporter, self.impostor_ballots)

    @property
    def ballot_report_mention_rate(self) -> float:
        return _rate(self.ballot_rationales_mentioning_report, self.ballot_rationales)

    @property
    def ballot_hinge_rate(self) -> float:
        return _rate(self.ballot_rationales_with_hinge, self.ballot_rationales)

    @property
    def speech_hinge_rate(self) -> float:
        return _rate(self.speech_turns_with_hinge, self.speech_turns)

    @property
    def co_discoverer_slots(self) -> int:
        return self.co_discoverer_slots_crewmate + self.co_discoverer_slots_impostor

    @property
    def co_discoverer_impostor_share(self) -> float:
        return _rate(self.co_discoverer_slots_impostor, self.co_discoverer_slots)


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _innocent_share_text(cells: ReporterJusticeCells) -> str:
    """The reporter's share of the innocent ejections, or "n/a" over an empty set."""

    if cells.innocent_ejections == 0:
        return "n/a"
    return f"{cells.reporter_share_of_innocent_ejections:.1%}"


def _relative_risk_text(cells: ReporterJusticeCells) -> str:
    """The relative risk in words, so an undefined ratio never reads as zero."""

    risk = cells.reporter_relative_risk
    if math.isnan(risk):
        return "undefined (no innocent ejection of either kind)"
    if math.isinf(risk):
        return "unbounded (no innocent non-reporter was ever ejected)"
    return f"{risk:.2f}x"


@dataclass(frozen=True)
class _Meeting:
    """One recorded meeting, resolved to the facts the cells read."""

    kind: str
    reporter: PlayerId
    trigger_tick: int
    victim_id: PlayerId | None
    entry: MeetingReplayEntry


def _meeting_trigger(
    entries: Sequence[ReplayEntry], *, entry: MeetingReplayEntry, roster: Iterable[str]
) -> tuple[str, PlayerId | None]:
    """``(kind, reported victim)`` off the recorded action stream at this tick.

    The meeting layer keeps no structured trigger kind (the description IS the
    trigger surface, and descriptions are not recorded), so the honest recorded
    source is the tick's action list: the meeting's own opener's APPLIED
    ``report`` or ``emergency``. Fails loud when the tick carries neither --
    a meeting the recorded actions cannot explain is a corrupt reading, not a
    meeting to bin as "other".

    A report's ``body_id`` names the corpse (``engine/rules.py`` mints
    ``body-{victim}-{tick}``), and the victim is what lets the co-discovery cell
    say "found THIS body" rather than "found A body near this tick". The parse is
    checked against the roster and raises on a miss, so a changed id format is a
    loud failure rather than a quietly emptied cell.
    """

    players = set(roster)
    for tick_entry in entries:
        if tick_entry.tick != entry.tick:
            continue
        dispositions = tick_entry.action_dispositions
        for index, action in enumerate(tick_entry.actions):
            kind = _TRIGGER_ACTION_KINDS.get(str(action.get("type")))
            if kind is None or action.get("actor") != entry.triggered_by:
                continue
            if dispositions is not None and dispositions[index] != _APPLIED:
                continue
            if kind != "body_report":
                return kind, None
            payload = action.get("payload")
            body_id = payload.get("body_id") if isinstance(payload, dict) else None
            match = _BODY_ID.match(body_id) if isinstance(body_id, str) else None
            if match is None or match.group("victim") not in players:
                # A body report with no readable corpse is refused, not accepted
                # with an unknown victim: an unknown victim would re-open the
                # match-any-corpse behaviour the victim filter exists to close,
                # and silently inflate the co-discovery cells again.
                raise ReporterJusticeError(
                    f"{entry.game_id}/{entry.meeting_id}: report action carries "
                    f"body id {body_id!r}, which does not name a roster player; "
                    "the reported corpse cannot be read from the recorded bytes"
                )
            return kind, match.group("victim")
    raise ReporterJusticeError(
        f"{entry.game_id}/{entry.meeting_id}: tick {entry.tick} carries no applied "
        f"report or emergency action by {entry.triggered_by!r}; the meeting kind "
        "cannot be read from the recorded bytes"
    )


def _accusations(entry: MeetingReplayEntry) -> Iterable[tuple[PlayerId, PlayerId]]:
    """``(speaker, accused)`` for every accusation claim in the transcript."""

    for turn in entry.transcript.turns:
        for claim in turn.claims:
            if isinstance(claim, AccusationClaim):
                yield turn.speaker, claim.against


def _mentions_report(text: str) -> bool:
    return REPORT_MENTION_TERM in text.lower()


def _carries_hinge(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in EXCULPATORY_HINGE_TERMS)


def _discoveries_by_agent(
    entry: MeetingReplayEntry,
) -> dict[PlayerId, set[tuple[int, str]]]:
    """``(tick, victim)`` pairs each speaker's OWN rendered memory showed them.

    Read off the recorded prompt bytes, which is what the speaker was actually
    given; a participant whose every call defaulted logged no prompt and
    contributes nothing rather than a guessed row. The victim rides along because
    "found a body near this tick" and "found THIS body" are different claims.
    """

    rows: dict[PlayerId, set[tuple[int, str]]] = {}
    for call in entry.llm_calls:
        agent_id = call.agent_id
        if agent_id is None:
            continue
        for match in _DISCOVERY_LINE.finditer(call.prompt):
            rows.setdefault(agent_id, set()).add(
                (int(match.group("tick")), match.group("victim"))
            )
    return rows


@dataclass
class _Tallies:
    """Mutable accumulators; folded into the frozen cells at the end."""

    games: int = 0
    meetings: int = 0
    body_report_meetings: int = 0
    emergency_meetings: int = 0
    reporter_crewmate_meetings: int = 0
    reporter_impostor_meetings: int = 0
    ejections: int = 0
    innocent_ejections: int = 0
    impostor_ejections: int = 0
    reporter_slots: int = 0
    reporter_ejections: int = 0
    reporter_innocent_ejections: int = 0
    innocent_non_reporter_slots: int = 0
    innocent_non_reporter_ejections: int = 0
    impostor_slots: int = 0
    impostor_slot_ejections: int = 0
    crew_accusations: int = 0
    crew_accusations_at_reporter: int = 0
    impostor_accusations: int = 0
    impostor_accusations_at_reporter: int = 0
    crew_ballots: int = 0
    crew_ballots_at_reporter: int = 0
    impostor_ballots: int = 0
    impostor_ballots_at_reporter: int = 0
    ballot_rationales: int = 0
    ballot_rationales_mentioning_report: int = 0
    ballot_rationales_with_hinge: int = 0
    speech_turns: int = 0
    speech_turns_mentioning_report: int = 0
    speech_turns_with_hinge: int = 0
    speech_turns_with_hinge_by_reporter: int = 0
    meetings_with_co_discoverer: int = 0
    co_discoverer_slots_crewmate: int = 0
    co_discoverer_slots_impostor: int = 0


def _fold_meeting(
    meeting: _Meeting,
    *,
    roles: Mapping[PlayerId, Role],
    tallies: _Tallies,
) -> None:
    """Fold ONE body-report meeting into the running cells."""

    entry = meeting.entry
    reporter = meeting.reporter
    if roles[reporter] == "IMPOSTOR":
        tallies.reporter_impostor_meetings += 1
    else:
        tallies.reporter_crewmate_meetings += 1

    # Living participants: every one casts a ballot, so the ballot set IS the
    # meeting's living roster as recorded. The classes are REPORTER-FIRST, so
    # they partition that roster even if a reporter is ever an impostor -- which
    # is exactly the laundering case the role census exists to catch, and which
    # a role-first split would hide by counting that seat twice and then
    # attributing its ejection to the impostor class instead of the reporter one.
    living = sorted({ballot.voter for ballot in entry.ballots})
    for player_id in living:
        if player_id == reporter:
            tallies.reporter_slots += 1
        elif roles[player_id] == "IMPOSTOR":
            tallies.impostor_slots += 1
        else:
            tallies.innocent_non_reporter_slots += 1

    ejected = entry.ejected_player_id
    if ejected is not None:
        if ejected == reporter:
            # Every reporter ejection, whatever the role: this is the numerator
            # of a per-SLOT exposure rate, and exposure is role-blind. The
            # innocent half is counted separately because a guilty reporter's
            # conviction is not a wrongful one and must never inflate a share of
            # the innocent total.
            tallies.reporter_ejections += 1
            if roles[ejected] != "IMPOSTOR":
                tallies.reporter_innocent_ejections += 1
        elif roles[ejected] == "IMPOSTOR":
            tallies.impostor_slot_ejections += 1
        else:
            tallies.innocent_non_reporter_ejections += 1

    for speaker, accused in _accusations(entry):
        if roles[speaker] == "IMPOSTOR":
            tallies.impostor_accusations += 1
            tallies.impostor_accusations_at_reporter += 1 if accused == reporter else 0
        else:
            tallies.crew_accusations += 1
            tallies.crew_accusations_at_reporter += 1 if accused == reporter else 0

    for ballot in entry.ballots:
        if roles[ballot.voter] == "IMPOSTOR":
            tallies.impostor_ballots += 1
            tallies.impostor_ballots_at_reporter += (
                1 if ballot.target == reporter else 0
            )
        else:
            tallies.crew_ballots += 1
            tallies.crew_ballots_at_reporter += 1 if ballot.target == reporter else 0
        tallies.ballot_rationales += 1
        if _mentions_report(ballot.rationale_text):
            tallies.ballot_rationales_mentioning_report += 1
            if _carries_hinge(ballot.rationale_text):
                tallies.ballot_rationales_with_hinge += 1

    for turn in entry.transcript.turns:
        tallies.speech_turns += 1
        if not _mentions_report(turn.free_text):
            continue
        tallies.speech_turns_mentioning_report += 1
        if not _carries_hinge(turn.free_text):
            continue
        tallies.speech_turns_with_hinge += 1
        if turn.speaker == reporter:
            tallies.speech_turns_with_hinge_by_reporter += 1

    discoveries = _discoveries_by_agent(entry)
    co_discoverers = [
        player_id
        for player_id, rows in sorted(discoveries.items())
        if player_id != reporter
        and any(
            0 <= meeting.trigger_tick - tick <= DISCOVERY_WINDOW_TICKS
            # THIS meeting's corpse, not any corpse near this tick: a speaker
            # who found a different body a tick earlier was not at the body that
            # opened the meeting. A recording whose body id could not be read
            # leaves ``victim_id`` None and falls back to the tick window.
            and (meeting.victim_id is None or victim == meeting.victim_id)
            for tick, victim in rows
        )
    ]
    if co_discoverers:
        tallies.meetings_with_co_discoverer += 1
    for player_id in co_discoverers:
        if roles[player_id] == "IMPOSTOR":
            tallies.co_discoverer_slots_impostor += 1
        else:
            tallies.co_discoverer_slots_crewmate += 1


def compute_reporter_justice(sample_dir: Path) -> ReporterJusticeCells:
    """Fold one committed replay set into its reporter-justice cells.

    Pure and offline: resolve the roster, recover per-seed roles by re-seeding,
    then read every committed game's recorded ticks, meetings, transcripts,
    ballots and prompts once. Raises :class:`ReporterJusticeError` on a set with
    no replays and on a meeting whose kind the recorded actions cannot explain --
    a zero-game or half-read measurement is worse than none.
    """

    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)
    seeds = seeds_on_disk(sample_dir)
    if not seeds:
        raise ReporterJusticeError(
            f"{sample_dir}: no replay-seed-*.jsonl files found — not a replay set "
            "(wrong path?); refusing to report a zero-game measurement"
        )
    per_seed_roles = roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )

    tallies = _Tallies()
    for seed in seeds:
        tallies.games += 1
        roles = per_seed_roles[seed]
        entries = read_all_entries(sample_dir / f"replay-seed-{seed}.jsonl")
        ticks = [e for e in entries if isinstance(e, ReplayEntry)]
        for entry in entries:
            if not isinstance(entry, MeetingReplayEntry):
                continue
            tallies.meetings += 1
            # The whole-set ledger counts every meeting: an innocent ejection
            # from an emergency call is still one of the set's innocent
            # ejections, and the reporter's SHARE is quoted against that total.
            ejected = entry.ejected_player_id
            if ejected is not None:
                tallies.ejections += 1
                if roles[ejected] == "IMPOSTOR":
                    tallies.impostor_ejections += 1
                else:
                    tallies.innocent_ejections += 1
            kind, victim_id = _meeting_trigger(ticks, entry=entry, roster=roles)
            if kind != "body_report":
                tallies.emergency_meetings += 1
                continue
            tallies.body_report_meetings += 1
            _fold_meeting(
                _Meeting(
                    kind=kind,
                    reporter=entry.triggered_by,
                    trigger_tick=entry.tick,
                    victim_id=victim_id,
                    entry=entry,
                ),
                roles=roles,
                tallies=tallies,
            )

    return ReporterJusticeCells(set_name=sample_dir.name, **vars(tallies))


def pool_reporter_justice(
    cells: Iterable[ReporterJusticeCells], *, set_name: str = "pooled"
) -> ReporterJusticeCells:
    """Sum per-set cells into one pooled reading.

    Every cell is a count over disjoint games, so pooling is addition and the
    derived rates recompute from the pooled numerator and denominator rather
    than being averaged -- a small set cannot drag a rate the way a mean of
    rates would. Raises on an empty input: there is nothing to pool, and a
    zeroed row would read as a measurement.
    """

    rows = list(cells)
    if not rows:
        raise ReporterJusticeError("pool_reporter_justice: no sets to pool")
    fields = [
        name for name in ReporterJusticeCells.__dataclass_fields__ if name != "set_name"
    ]
    totals: dict[str, Any] = {
        name: sum(getattr(row, name) for row in rows) for name in fields
    }
    return ReporterJusticeCells(set_name=set_name, **totals)


def render_reporter_justice(cells: ReporterJusticeCells) -> str:
    """A short human-readable block, for a PR body or an audit appendix."""

    lines = [
        f"reporter justice — {cells.set_name} "
        f"({cells.games} games, {cells.meetings} meetings)",
        f"  meetings: body report {cells.body_report_meetings}, "
        f"emergency {cells.emergency_meetings}",
        f"  reporter role: CREWMATE {cells.reporter_crewmate_meetings}, "
        f"IMPOSTOR {cells.reporter_impostor_meetings}",
        f"  ejections (all meetings): {cells.ejections} total, "
        f"{cells.innocent_ejections} innocent, {cells.impostor_ejections} impostor; "
        f"{cells.reporter_ejections} reporter "
        f"({cells.reporter_innocent_ejections} of them innocent, "
        f"{_innocent_share_text(cells)} of the innocent total)",
        f"  per-slot ejection: reporter {cells.reporter_ejections}/"
        f"{cells.reporter_slots} = {cells.reporter_ejection_rate:.2%}, "
        f"innocent non-reporter {cells.innocent_non_reporter_ejections}/"
        f"{cells.innocent_non_reporter_slots} = "
        f"{cells.innocent_non_reporter_ejection_rate:.2%}, "
        f"impostor {cells.impostor_slot_ejections}/{cells.impostor_slots} = "
        f"{cells.impostor_ejection_rate:.2%} "
        f"(relative risk {_relative_risk_text(cells)})",
        f"  speech at reporter: crew {cells.crew_accusations_at_reporter}/"
        f"{cells.crew_accusations} = {cells.crew_accusation_at_reporter_share:.1%}, "
        f"impostor {cells.impostor_accusations_at_reporter}/"
        f"{cells.impostor_accusations} = "
        f"{cells.impostor_accusation_at_reporter_share:.1%}",
        f"  ballots at reporter: crew {cells.crew_ballots_at_reporter}/"
        f"{cells.crew_ballots} = {cells.crew_ballot_at_reporter_share:.1%}, "
        f"impostor {cells.impostor_ballots_at_reporter}/{cells.impostor_ballots} = "
        f"{cells.impostor_ballot_at_reporter_share:.1%}",
        f"  invocation (upper bound): ballots "
        f"{cells.ballot_rationales_mentioning_report}/{cells.ballot_rationales} "
        f"mention a report = {cells.ballot_report_mention_rate:.2%}, "
        f"{cells.ballot_rationales_with_hinge} also carry a hinge = "
        f"{cells.ballot_hinge_rate:.2%}; speech "
        f"{cells.speech_turns_with_hinge}/{cells.speech_turns} = "
        f"{cells.speech_hinge_rate:.2%} "
        f"({cells.speech_turns_with_hinge_by_reporter} by the reporter)",
        f"  co-discovery: {cells.meetings_with_co_discoverer}/"
        f"{cells.body_report_meetings} meetings carry one; slots "
        f"{cells.co_discoverer_slots_crewmate} CREWMATE / "
        f"{cells.co_discoverer_slots_impostor} IMPOSTOR = "
        f"{cells.co_discoverer_impostor_share:.1%} impostor",
    ]
    return "\n".join(lines)


def _cli(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("sample_dir", nargs="+", type=Path)
    parser.add_argument(
        "--pooled", action="store_true", help="also print the pooled reading"
    )
    args = parser.parse_args(argv)
    rows = [compute_reporter_justice(sample_dir) for sample_dir in args.sample_dir]
    for cells in rows:
        print(render_reporter_justice(cells))
    if args.pooled:
        print(render_reporter_justice(pool_reporter_justice(rows)))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(_cli())


__all__ = [
    "DISCOVERY_WINDOW_TICKS",
    "EXCULPATORY_HINGE_TERMS",
    "REPORT_MENTION_TERM",
    "ReporterJusticeCells",
    "ReporterJusticeError",
    "compute_reporter_justice",
    "pool_reporter_justice",
    "render_reporter_justice",
]
