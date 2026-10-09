"""Rubric version 2: the role-blind game-shape profile of one replay set.

The profile describes each game; it scores, ranks and zeroes none. For every
game it gives a timeline of physical moments (the facets), the named shelves it
sits on, the meeting chips it carries, and two tripwires. Shelves come in one
fixed order and list their games in seed order, so nothing here orders a game
by anything but its seed. ``docs/game-profile.md`` is the generated page;
``scripts/publish_game_profile.py`` writes it and the served file
``results-game-profile.json`` beside the recordings.

**Two projections.** Everything a spectator may see before the reveal is
computed from :class:`BlindGame`, which :func:`blind_projection` builds from the
census carrier (:func:`eval.gameplay_census.load_census_inputs`) and scorecard
row 3's set inputs (:func:`eval.process_scorecard.load_set_inputs`). It holds
ids, ticks, rooms, grounding labels, cited ids, accusations, vent-flag subjects,
kill victims and witnesses, bodies, regroups, the set-level kill cooldown and
each meeting's manufactured-flag subjects, and no role, winner, ending, task
count, killer, vent actor or game report: a pre-reveal predicate that reads a
role fails strict mypy. :class:`RevealGame` adds the roles, the recorded ending,
the final task count and the sabotage starts; only the reveal shelves, the
reveal facets and the leak rule read it.

**The tripwires.** A game that trips one sits on no shelf and keeps a plain
label under All games. T1, decided by a vote that held nothing: with the
ejecting ballots labelled ``off_target``, ``uncited`` or ``invalid_citation``
removed, :func:`eval.gameplay_census.tally_outcome` at the meeting's recorded
confidence floor ejects no one or someone else. ``supported`` and ``flag_only``
are held, and ``not_assessed`` stays as recorded. An ejecting ballot labelled
``none_held`` is a case the ruled tripwire does not classify, so it raises
:class:`GameProfileConformanceError` naming the set, seed, meeting and voter
until the owner says how T1 reads one. The every and any readings, and the two
other decisive readings (read as SKIP; every ungrounded ballot removed), are
published beside the governing one. T2, decided on a manufactured
contradiction: the ejected player is named by an alibi-class flag that row 3
classes as manufactured over the engine route. Row 3 can evaluate few flags, so
T2 is nearly blind, and the page says so.

**The leak and saturation rules.** Each candidate pre-reveal shelf is tested
by a two-sided Fisher exact test of its membership against each recorded
ending, against some meeting having ejected someone and against a crewmate
having been ejected, over every game of the era, a tripped game counted as a
non-member. Any p below :data:`LEAK_P_LEVEL` puts the shelf behind the reveal
for that era. A candidate holding more than :data:`SATURATION_SHARE` of the
era's games is a facet, never a shelf, and saturation is applied first. The
classes are recomputed per era and recorded in the served file.

Role-correctness is reported here and gates nothing. No module under
``agents``, ``meetings``, ``orchestrator``, ``engine`` or ``training`` may import
this one (``.importlinter``), and no pre-registration, step rule, gate or
objective reads it.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from fractions import Fraction
from types import MappingProxyType
from typing import Final, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import PlayerId, Role, RoomId
from eval.gameplay_census import (
    BallotFact,
    CensusInputs,
    GameFacts,
    TriggerKind,
    game_endings,
    grounding_labels,
    tally_outcome,
)
from eval.process_scorecard import (
    ALIBI_FLAG_KINDS,
    SetInputs,
    _flag_is_manufactured,
    _self_alibi_truths,
)
from eval.report_schema import GameReport, MeetingReport
from meetings.schemas import BallotGroundingLabel
from meetings.voting import SKIP_TARGET

# ---------------------------------------------------------------------------
# The design constants, frozen for this profile version
# ---------------------------------------------------------------------------

#: The profile's version, stamped as ``rubric_version`` in the served file.
#: Version 1 was the interestingness score; a change to any constant below needs
#: version 3.
RUBRIC_VERSION: Final[int] = 2

#: A slow burn is a stretch of at least this many ticks with no kill.
SLOW_BURN_TICKS: Final[int] = 20

#: A kill is in a regroup's wave when it lands more than the kill cooldown, and
#: at most this many ticks past it, after the regroup.
WAVE_SLACK_TICKS: Final[int] = 4

#: A close call is a meeting whose leading choice beat the runner-up by at most
#: this many ballots.
CLOSE_CALL_MARGIN: Final[int] = 1

#: A third round is a game with at least this many meetings.
THIRD_ROUND_MEETINGS: Final[int] = 3

#: Down to the wire needs the losing side to have started at least this many
#: steps from its own ending.
DOWN_TO_THE_WIRE_START: Final[int] = 3

#: A runaway leaves the losing side at least this share of its starting
#: distance from its ending.
RUNAWAY_SHARE: Final[Fraction] = Fraction(1, 2)

#: A candidate shelf with any leak-rule p below this is reveal-only for the era.
LEAK_P_LEVEL: Final[Fraction] = Fraction(1, 20)

#: A candidate holding more than this share of an era's games is a facet.
SATURATION_SHARE: Final[Fraction] = Fraction(3, 4)


class GameProfileConformanceError(RuntimeError):
    """A recording the profile cannot read as ruled, named by set, seed and meeting."""


# ---------------------------------------------------------------------------
# The grounding-label partition the tripwire reads
# ---------------------------------------------------------------------------

LabelClass: TypeAlias = Literal["held", "ungrounded", "as_recorded", "unclassified"]

#: How T1 reads an ejecting ballot by its grounding label. ``held`` ballots
#: stay, ``ungrounded`` ones are removed, ``as_recorded`` ones stay as the
#: meeting layer recorded them, and an ``unclassified`` one raises.
LABEL_CLASSES: Final[Mapping[str, LabelClass]] = MappingProxyType(
    {
        "supported": "held",
        "flag_only": "held",
        "off_target": "ungrounded",
        "uncited": "ungrounded",
        "invalid_citation": "ungrounded",
        "not_assessed": "as_recorded",
        "none_held": "unclassified",
    }
)

#: The labels whose ballots "one line, two readings" groups by the turn cited.
READING_LABELS: Final[tuple[str, ...]] = ("supported", "none_held", "off_target")


def label_classes() -> Mapping[str, LabelClass]:
    """Every grounding label the meeting layer writes, with its tripwire class.

    The labels are read at call time from
    :data:`meetings.schemas.BallotGroundingLabel`
    (:func:`eval.gameplay_census.grounding_labels`). A label the partition does
    not class, or a class for a label the type no longer has, raises: the
    tripwire never guesses how to read a new label.
    """

    labels = grounding_labels()
    unclassed = [label for label in labels if label not in LABEL_CLASSES]
    if unclassed:
        raise GameProfileConformanceError(
            f"the grounding label {unclassed[0]!r} has no class in the tripwire's "
            "label partition; the owner decides how a new label reads"
        )
    stale = [label for label in LABEL_CLASSES if label not in labels]
    if stale:
        raise GameProfileConformanceError(
            f"the tripwire's label partition classes {stale[0]!r}, a label the "
            "meeting layer no longer writes"
        )
    unknown = [label for label in READING_LABELS if label not in labels]
    if unknown:
        raise GameProfileConformanceError(
            f"one line, two readings groups ballots labelled {unknown[0]!r}, a "
            "label the meeting layer no longer writes"
        )
    return MappingProxyType({label: LABEL_CLASSES[label] for label in labels})


# ---------------------------------------------------------------------------
# The role-blind projection
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BlindBallot:
    """One ballot: voter, target, confidence, label and the ids it cites."""

    voter: PlayerId
    target: str
    confidence: float
    grounding_label: BallotGroundingLabel
    cited_observation_id: str | None
    primary_reason_id: str | None


@dataclass(frozen=True)
class BlindTurn:
    """One spoken turn, as far as the profile reads it: who it accused."""

    speaker: PlayerId
    accusations: tuple[PlayerId, ...]


@dataclass(frozen=True)
class BlindOwnKillRow:
    """A served own-kill row: who held it and the observation id it cites."""

    holder: PlayerId
    citation_id: str | None


@dataclass(frozen=True)
class BlindKill:
    """One kill: when, where, who died and who the engine says saw it."""

    tick: int
    room: RoomId
    victim: PlayerId
    witnesses: frozenset[PlayerId]


@dataclass(frozen=True)
class BlindBody:
    """One corpse, joined to its kill by victim."""

    body_id: str
    victim: PlayerId
    kill_tick: int


@dataclass(frozen=True)
class BlindMeeting:
    """One meeting, without any read of a role or the ending.

    ``manufactured_subjects`` are the players named by this meeting's
    alibi-class flags that row 3 classes as manufactured; ``alibi_flags`` and
    ``alibi_flags_evaluable`` count the meeting's alibi-class flags and those
    row 3 can answer.
    """

    index: int
    meeting_id: str
    tick: int
    trigger_kind: TriggerKind
    opener: PlayerId
    trigger_body: str | None
    living: frozenset[PlayerId]
    ejected: PlayerId | None
    ballot_floor: float
    ballots: tuple[BlindBallot, ...]
    turns: tuple[BlindTurn, ...]
    vent_flag_subjects: tuple[frozenset[PlayerId], ...]
    own_kill_rows: tuple[BlindOwnKillRow, ...]
    regrouped: bool
    manufactured_subjects: frozenset[PlayerId]
    alibi_flags: int
    alibi_flags_evaluable: int


@dataclass(frozen=True)
class BlindGame:
    """One game, role-blind: the sole input of every pre-reveal reading."""

    seed: int
    terminal_tick: int
    kills: tuple[BlindKill, ...]
    bodies: tuple[BlindBody, ...]
    meetings: tuple[BlindMeeting, ...]
    kill_cooldown_ticks: int


@dataclass(frozen=True)
class BlindSet:
    """The role-blind projection of one replay set, games in seed order."""

    label: str
    games: tuple[BlindGame, ...]


def _manufactured(
    meeting: MeetingReport, route: Mapping[int, Mapping[PlayerId, RoomId]]
) -> tuple[frozenset[PlayerId], int, int]:
    """Row 3's manufactured subjects, alibi-class flags and evaluable flags."""

    truths = _self_alibi_truths(meeting, route)
    subjects: set[PlayerId] = set()
    flags = 0
    evaluable = 0
    for flag in meeting.contradictions:
        if flag.kind not in ALIBI_FLAG_KINDS:
            continue
        flags += 1
        verdict = _flag_is_manufactured(flag, truths)
        if verdict is None:
            continue
        evaluable += 1
        if verdict[0]:
            subjects.update(flag.subjects)
    return frozenset(subjects), flags, evaluable


def _blind_ballot(ballot: BallotFact, *, where: str) -> BlindBallot:
    if ballot.grounding_label is None:
        raise GameProfileConformanceError(
            f"{where}, voter {ballot.voter}: the ballot carries no grounding label"
        )
    return BlindBallot(
        voter=ballot.voter,
        target=ballot.target,
        confidence=ballot.confidence,
        grounding_label=ballot.grounding_label,
        cited_observation_id=ballot.cited_observation_id,
        primary_reason_id=ballot.primary_reason_id,
    )


def _blind_game(
    game: GameFacts,
    *,
    label: str,
    report: GameReport,
    route: Mapping[int, Mapping[PlayerId, RoomId]],
    kill_cooldown_ticks: int,
) -> BlindGame:
    where = f"set {label}, seed {game.seed}"
    if len(report.meetings) != len(game.meetings):
        raise GameProfileConformanceError(
            f"{where}: the scorecard holds {len(report.meetings)} meetings and the "
            f"carrier {len(game.meetings)}"
        )
    meetings: list[BlindMeeting] = []
    for index, (fact, scored) in enumerate(
        zip(game.meetings, report.meetings, strict=True)
    ):
        meeting_where = f"{where}, meeting index {index}"
        if scored.meeting_id != fact.meeting_id:
            raise GameProfileConformanceError(
                f"{meeting_where}: the scorecard's meeting {scored.meeting_id} is "
                f"not the carrier's {fact.meeting_id}"
            )
        subjects, flags, evaluable = _manufactured(scored, route)
        meetings.append(
            BlindMeeting(
                index=index,
                meeting_id=fact.meeting_id,
                tick=fact.tick,
                trigger_kind=fact.trigger_kind,
                opener=fact.opener,
                trigger_body=fact.trigger_body,
                living=fact.living,
                ejected=fact.ejected,
                ballot_floor=fact.ballot_floor,
                ballots=tuple(
                    _blind_ballot(ballot, where=meeting_where)
                    for ballot in fact.ballots
                ),
                turns=tuple(
                    BlindTurn(speaker=turn.speaker, accusations=turn.accusations)
                    for turn in fact.turns
                ),
                vent_flag_subjects=fact.vent_flag_subjects,
                own_kill_rows=tuple(
                    BlindOwnKillRow(holder=row.holder, citation_id=row.citation_id)
                    for row in fact.own_kill_rows
                ),
                regrouped=fact.regrouped,
                manufactured_subjects=subjects,
                alibi_flags=flags,
                alibi_flags_evaluable=evaluable,
            )
        )
    kills: list[BlindKill] = []
    for kill in game.kills:
        if kill.victim is None:
            raise GameProfileConformanceError(
                f"{where}: the kill at tick {kill.tick} names no victim"
            )
        kills.append(
            BlindKill(
                tick=kill.tick,
                room=kill.room,
                victim=kill.victim,
                witnesses=kill.witnesses,
            )
        )
    bodies: list[BlindBody] = []
    for body in game.bodies:
        if body.victim is None:
            raise GameProfileConformanceError(
                f"{where}: the body {body.body_id} names no victim"
            )
        bodies.append(
            BlindBody(
                body_id=body.body_id, victim=body.victim, kill_tick=body.kill_tick
            )
        )
    return BlindGame(
        seed=game.seed,
        terminal_tick=game.terminal_tick,
        kills=tuple(kills),
        bodies=tuple(bodies),
        meetings=tuple(meetings),
        kill_cooldown_ticks=kill_cooldown_ticks,
    )


def blind_projection(inputs: CensusInputs, scorecard: SetInputs) -> BlindSet:
    """The role-blind projection of one set's carrier and row-3 inputs.

    Row 3's manufactured subjects are computed here, from each scorecard
    meeting's transcript and the engine route, and joined to the carrier's
    meetings by meeting id; a mismatch raises, naming set, seed and meeting
    index. A ballot with no grounding label, a kill or a body with no victim
    raises too. The scorecard's game reports are read for their meetings only
    and are not kept.
    """

    where = f"set {inputs.label}"
    reports: dict[int, GameReport] = {}
    for report in scorecard.games:
        if report.seed in reports:
            raise GameProfileConformanceError(
                f"{where}: the scorecard inputs hold seed {report.seed} twice"
            )
        reports[report.seed] = report
    facts: dict[int, GameFacts] = {}
    for fact in inputs.games:
        if fact.seed in facts:
            raise GameProfileConformanceError(
                f"{where}: the carrier holds seed {fact.seed} twice"
            )
        facts[fact.seed] = fact
    if sorted(facts) != sorted(reports):
        raise GameProfileConformanceError(
            f"{where}: the carrier holds seeds {sorted(facts)} and the scorecard "
            f"inputs {sorted(reports)}"
        )
    missing = [seed for seed in sorted(facts) if seed not in scorecard.routes]
    if missing:
        raise GameProfileConformanceError(
            f"{where}, seed {missing[0]}: the scorecard holds no route"
        )
    games = tuple(
        _blind_game(
            facts[seed],
            label=inputs.label,
            report=reports[seed],
            route=scorecard.routes[seed],
            kill_cooldown_ticks=inputs.kill_cooldown_ticks,
        )
        for seed in sorted(facts)
    )
    return BlindSet(label=inputs.label, games=games)


# ---------------------------------------------------------------------------
# The reveal projection
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RevealGame:
    """One game with the reads that sit behind the reveal.

    ``roles`` are the seeded roles, ``end_reason`` the recorded ending (one of
    :func:`eval.gameplay_census.game_endings`), ``tasks_done`` and
    ``tasks_assigned`` the final task count, and ``sabotage_starts`` the ticks
    a sabotage became active.
    """

    blind: BlindGame
    roles: Mapping[PlayerId, Role]
    end_reason: str
    tasks_done: int
    tasks_assigned: int
    sabotage_starts: tuple[int, ...]


def _sabotage_starts(game: GameFacts) -> tuple[int, ...]:
    starts: list[int] = []
    previous = False
    for tick in sorted(game.frames):
        active = game.frames[tick].sabotage_active
        if active and not previous:
            starts.append(tick)
        previous = active
    return tuple(starts)


def reveal_projection(inputs: CensusInputs, blind: BlindSet) -> tuple[RevealGame, ...]:
    """Each blind game with its roles, recorded ending and final task count.

    An ending outside :func:`eval.gameplay_census.game_endings`, a game with no
    recorded ending or no final task count, and a blind game the carrier does
    not hold each raise.
    """

    endings = game_endings()
    facts = {game.seed: game for game in inputs.games}
    revealed: list[RevealGame] = []
    for game in blind.games:
        where = f"set {blind.label}, seed {game.seed}"
        if game.seed not in facts:
            raise GameProfileConformanceError(f"{where}: the carrier holds no game")
        fact = facts[game.seed]
        if fact.end_reason is None:
            raise GameProfileConformanceError(f"{where}: no recorded ending")
        if fact.end_reason not in endings:
            raise GameProfileConformanceError(
                f"{where}: the recorded ending {fact.end_reason!r} is not one the "
                "engine or the runner records"
            )
        if fact.final_tasks_completed is None or fact.final_tasks_total is None:
            raise GameProfileConformanceError(f"{where}: no final task count")
        revealed.append(
            RevealGame(
                blind=game,
                roles=fact.roles,
                end_reason=fact.end_reason,
                tasks_done=fact.final_tasks_completed,
                tasks_assigned=fact.final_tasks_total,
                sabotage_starts=_sabotage_starts(fact),
            )
        )
    return tuple(revealed)


# ---------------------------------------------------------------------------
# Names, in their one fixed order
# ---------------------------------------------------------------------------

#: What the catalogue records of each name: a candidate's class for the era
#: (``shelf``, ``leaks`` or ``saturated``), what a reveal-only shelf reads, or
#: the name's kind.
Classification: TypeAlias = Literal[
    "shelf",
    "leaks",
    "saturated",
    "reads_an_ejection",
    "reads_the_ending",
    "reads_a_role",
    "chip",
    "facet",
    "tripwire",
]

REPORTER_SAW_IT: Final[str] = "the_reporter_saw_it_happen"
DOUBLE_KILL: Final[str] = "double_kill"
SLOW_BURN: Final[str] = "slow_burn"
TWO_KILLS_AFTER_ONE_REGROUP: Final[str] = "two_kills_after_one_regroup"
CLOSE_CALL: Final[str] = "a_close_call"
SUSPICION_MOVED: Final[str] = "suspicion_moved"
THIRD_ROUND: Final[str] = "a_third_round"
CAUGHT_VENTING: Final[str] = "caught_venting"
ONE_LINE_TWO_READINGS: Final[str] = "one_line_two_readings"
STRUCK_AFTER_THE_REGROUP: Final[str] = "struck_after_the_regroup"

#: Every candidate pre-reveal shelf, in the order shelves are served.
CANDIDATES: Final[tuple[str, ...]] = (
    REPORTER_SAW_IT,
    DOUBLE_KILL,
    SLOW_BURN,
    TWO_KILLS_AFTER_ONE_REGROUP,
    CLOSE_CALL,
    SUSPICION_MOVED,
    THIRD_ROUND,
    CAUGHT_VENTING,
    ONE_LINE_TWO_READINGS,
    STRUCK_AFTER_THE_REGROUP,
)

ONE_VOTE_EJECTION: Final[str] = "one_vote_ejection"
NOBODY_VOTED_OUT: Final[str] = "nobody_voted_out"
DOWN_TO_THE_WIRE: Final[str] = "down_to_the_wire"
RUNAWAY: Final[str] = "runaway"
DECIDED_AT_A_MEETING: Final[str] = "decided_at_a_meeting"
RIGHT_WITHOUT_PROOF: Final[str] = "decided_without_proof_right"
WRONG_ON_WHAT_IT_HELD: Final[str] = "decided_without_proof_wrong"

#: The shelves that sit behind the reveal by design, in serving order, with
#: what each reads.
REVEAL_SHELVES: Final[tuple[tuple[str, Classification], ...]] = (
    (ONE_VOTE_EJECTION, "reads_an_ejection"),
    (NOBODY_VOTED_OUT, "reads_an_ejection"),
    (DOWN_TO_THE_WIRE, "reads_the_ending"),
    (RUNAWAY, "reads_the_ending"),
    (DECIDED_AT_A_MEETING, "reads_the_ending"),
)

EYEWITNESS_CHIP: Final[str] = "an_eyewitness_voted_on_it"

HELD_NOTHING: Final[str] = "decided_by_a_vote_that_held_nothing"
MANUFACTURED: Final[str] = "decided_on_a_manufactured_contradiction"

#: The tripwire readings, in publication order: (reading, tripwire, governs).
#: A governing reading trips its game; the others are published beside it.
TRIPWIRE_READINGS: Final[tuple[tuple[str, str, bool], ...]] = (
    ("decisive", HELD_NOTHING, True),
    ("decisive_read_as_skip", HELD_NOTHING, False),
    ("decisive_all_ungrounded_removed", HELD_NOTHING, False),
    ("every", HELD_NOTHING, False),
    ("any", HELD_NOTHING, False),
    ("manufactured", MANUFACTURED, True),
)

#: The facets, by half, in order.
PRE_REVEAL_FACETS: Final[tuple[str, ...]] = (
    "length_in_ticks",
    "meetings_by_trigger",
    "kill_timeline",
    "reports_with_corpse_age",
    "bodies_never_found",
)
REVEAL_FACETS: Final[tuple[str, ...]] = (
    "ending",
    "distance_from_the_other_ending",
    "sabotage_starts",
    "ejection_annotations",
)

#: The facts the leak rule tests each candidate against, beside each recorded
#: ending.
ANY_EJECTION: Final[str] = "some_meeting_ejected_someone"
CREWMATE_EJECTED: Final[str] = "a_crewmate_was_ejected"


# ---------------------------------------------------------------------------
# Pointers and the role-blind readings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Pointer:
    """Where a shelf finds its moment: meeting indexes and kill ticks."""

    meetings: tuple[int, ...] = ()
    kill_ticks: tuple[int, ...] = ()


def _as_fact(ballot: BlindBallot) -> BallotFact:
    return BallotFact(
        voter=ballot.voter,
        target=ballot.target,
        authored_target=ballot.target,
        confidence=ballot.confidence,
        grounding_label=ballot.grounding_label,
        cited_observation_id=ballot.cited_observation_id,
    )


def _tallied(ballots: Sequence[BlindBallot], floor: float) -> PlayerId | None:
    """Who the game's own tally ejects from ``ballots`` at ``floor``."""

    return tally_outcome(tuple(_as_fact(ballot) for ballot in ballots), floor)[1]


def meeting_readings(
    meeting: BlindMeeting,
    *,
    where: str,
    classes: Mapping[str, LabelClass],
) -> frozenset[str]:
    """The tripwire readings one meeting's ejection trips; none at a skip."""

    ejected = meeting.ejected
    ejecting = [ballot for ballot in meeting.ballots if ballot.target == ejected]
    for ballot in ejecting:
        if classes[ballot.grounding_label] == "unclassified":
            raise GameProfileConformanceError(
                f"{where}, meeting index {meeting.index}, voter {ballot.voter}: an "
                f"ejecting ballot labelled {ballot.grounding_label!r} is a case the "
                "tripwire does not classify; the owner decides how it reads"
            )
    readings: set[str] = set()

    def ungrounded(ballot: BlindBallot) -> bool:
        return classes[ballot.grounding_label] == "ungrounded"

    removed_from_ejection = [ballot for ballot in ejecting if ungrounded(ballot)]
    if ejecting and len(removed_from_ejection) == len(ejecting):
        readings.add("every")
    if removed_from_ejection:
        readings.add("any")
        kept = tuple(
            ballot
            for ballot in meeting.ballots
            if not (ballot.target == ejected and ungrounded(ballot))
        )
        if _tallied(kept, meeting.ballot_floor) != ejected:
            readings.add("decisive")
        as_skip = tuple(
            replace(ballot, target=SKIP_TARGET)
            if ballot.target == ejected and ungrounded(ballot)
            else ballot
            for ballot in meeting.ballots
        )
        if _tallied(as_skip, meeting.ballot_floor) != ejected:
            readings.add("decisive_read_as_skip")
        grounded = tuple(ballot for ballot in meeting.ballots if not ungrounded(ballot))
        if _tallied(grounded, meeting.ballot_floor) != ejected:
            readings.add("decisive_all_ungrounded_removed")
    if ejected in meeting.manufactured_subjects:
        readings.add("manufactured")
    return frozenset(readings)


def game_readings(
    game: BlindGame, *, label: str, classes: Mapping[str, LabelClass]
) -> Mapping[str, tuple[int, ...]]:
    """Each tripwire reading's meeting indexes in one game, in reading order."""

    where = f"set {label}, seed {game.seed}"
    per_meeting = [
        meeting_readings(meeting, where=where, classes=classes)
        for meeting in game.meetings
    ]
    return MappingProxyType(
        {
            reading: tuple(
                meeting.index
                for meeting, hits in zip(game.meetings, per_meeting, strict=True)
                if reading in hits
            )
            for reading, _, _ in TRIPWIRE_READINGS
        }
    )


def tripped(readings: Mapping[str, tuple[int, ...]]) -> bool:
    """Whether a governing reading trips the game."""

    return any(
        readings[reading] for reading, _, governs in TRIPWIRE_READINGS if governs
    )


def _last_regroup_before(regroups: Sequence[int], tick: int) -> int | None:
    earlier = [regroup for regroup in regroups if regroup < tick]
    return max(earlier) if earlier else None


def wave_kills(game: BlindGame) -> tuple[tuple[int, int], ...]:
    """Every kill in a regroup's wave, as (regroup tick, kill tick).

    A kill is in the wave of the last regroup before it when it lands more than
    the set's kill cooldown, and at most :data:`WAVE_SLACK_TICKS` past it, after
    that regroup.
    """

    regroups = [meeting.tick for meeting in game.meetings if meeting.regrouped]
    cooldown = game.kill_cooldown_ticks
    wave: list[tuple[int, int]] = []
    for kill in game.kills:
        regroup = _last_regroup_before(regroups, kill.tick)
        if regroup is None:
            continue
        if cooldown < kill.tick - regroup <= cooldown + WAVE_SLACK_TICKS:
            wave.append((regroup, kill.tick))
    return tuple(wave)


def _kill_of(game: BlindGame, body_id: str, *, where: str) -> BlindKill:
    """The kill whose victim the body ``body_id`` is; anything else raises."""

    bodies = [body for body in game.bodies if body.body_id == body_id]
    if len(bodies) != 1:
        raise GameProfileConformanceError(
            f"{where}: the reported body {body_id} joins {len(bodies)} corpses"
        )
    kills = [kill for kill in game.kills if kill.victim == bodies[0].victim]
    if len(kills) != 1:
        raise GameProfileConformanceError(
            f"{where}: the reported body {body_id} joins {len(kills)} kills"
        )
    return kills[0]


def _lead_margin(meeting: BlindMeeting) -> int | None:
    """The leading choice's ballots minus the runner-up's, SKIP a choice."""

    ranked = Counter(ballot.target for ballot in meeting.ballots).most_common()
    if not ranked:
        return None
    return ranked[0][1] - (ranked[1][1] if len(ranked) > 1 else 0)


def _eject_votes(meeting: BlindMeeting) -> Counter[str]:
    return Counter(
        ballot.target for ballot in meeting.ballots if ballot.target != SKIP_TARGET
    )


def _suspicion_moved(game: BlindGame, index: int) -> bool:
    """Across meetings ``index - 1`` and ``index``, read from ballots and charges.

    Any of: the ejected player drew EJECT ballots at an earlier meeting; a
    player who drew EJECT ballots draws none, and no accusation, while alive;
    the leading EJECT target changes while the old lead lives.
    """

    meeting = game.meetings[index]
    votes = [_eject_votes(earlier) for earlier in game.meetings[: index + 1]]
    previous, now = votes[index - 1], votes[index]
    charged = {
        accused
        for turn in meeting.turns
        for accused in turn.accusations
        if accused != turn.speaker
    }
    if meeting.ejected is not None and any(
        meeting.ejected in votes[earlier] for earlier in range(index)
    ):
        return True
    if any(
        player in meeting.living and now.get(player, 0) == 0 and player not in charged
        for player in previous
    ):
        return True
    old_lead = previous.most_common(1)[0][0] if previous else None
    new_lead = now.most_common(1)[0][0] if now else None
    return (
        old_lead is not None
        and new_lead is not None
        and old_lead != new_lead
        and old_lead in meeting.living
    )


def candidate_pointers(game: BlindGame, *, label: str) -> Mapping[str, Pointer]:
    """Every candidate pre-reveal shelf the game sits on, with its pointer."""

    where = f"set {label}, seed {game.seed}"
    hits: dict[str, Pointer] = {}

    reporter = tuple(
        meeting.index
        for meeting in game.meetings
        if meeting.trigger_kind == "report"
        and meeting.trigger_body is not None
        and meeting.opener
        in _kill_of(
            game,
            meeting.trigger_body,
            where=f"{where}, meeting index {meeting.index}",
        ).witnesses
    )
    if reporter:
        hits[REPORTER_SAW_IT] = Pointer(meetings=reporter)

    ticks = sorted(kill.tick for kill in game.kills)
    doubled = tuple(
        sorted({later for earlier, later in zip(ticks, ticks[1:]) if earlier == later})
    )
    if doubled:
        hits[DOUBLE_KILL] = Pointer(kill_ticks=doubled)

    marks = [0, *ticks, game.terminal_tick]
    stretches = [
        (start, end)
        for start, end in zip(marks, marks[1:])
        if end - start >= SLOW_BURN_TICKS
    ]
    if stretches:
        bounding = sorted(
            {tick for stretch in stretches for tick in stretch if tick in ticks}
        )
        hits[SLOW_BURN] = Pointer(kill_ticks=tuple(bounding))

    wave = wave_kills(game)
    per_regroup = Counter(regroup for regroup, _ in wave)
    crowded = sorted(regroup for regroup, count in per_regroup.items() if count >= 2)
    if crowded:
        hits[TWO_KILLS_AFTER_ONE_REGROUP] = Pointer(
            meetings=tuple(
                meeting.index for meeting in game.meetings if meeting.tick in crowded
            ),
            kill_ticks=tuple(tick for regroup, tick in wave if regroup in crowded),
        )
    if wave:
        hits[STRUCK_AFTER_THE_REGROUP] = Pointer(
            kill_ticks=tuple(tick for _, tick in wave)
        )

    close = tuple(
        meeting.index
        for meeting in game.meetings
        if (margin := _lead_margin(meeting)) is not None and margin <= CLOSE_CALL_MARGIN
    )
    if close:
        hits[CLOSE_CALL] = Pointer(meetings=close)

    moved = tuple(
        index for index in range(1, len(game.meetings)) if _suspicion_moved(game, index)
    )
    if moved:
        hits[SUSPICION_MOVED] = Pointer(meetings=moved)

    if len(game.meetings) >= THIRD_ROUND_MEETINGS:
        hits[THIRD_ROUND] = Pointer(meetings=(THIRD_ROUND_MEETINGS - 1,))

    venting = tuple(
        meeting.index
        for meeting in game.meetings
        if any(subjects for subjects in meeting.vent_flag_subjects)
    )
    if venting:
        hits[CAUGHT_VENTING] = Pointer(meetings=venting)

    def two_readings(meeting: BlindMeeting) -> bool:
        readings: dict[str, set[str]] = {}
        for ballot in meeting.ballots:
            if (
                ballot.primary_reason_id is not None
                and ballot.grounding_label in READING_LABELS
            ):
                readings.setdefault(ballot.primary_reason_id, set()).add(ballot.target)
        return any(len(targets) >= 2 for targets in readings.values())

    lines = tuple(meeting.index for meeting in game.meetings if two_readings(meeting))
    if lines:
        hits[ONE_LINE_TWO_READINGS] = Pointer(meetings=lines)

    return MappingProxyType({name: hits[name] for name in CANDIDATES if name in hits})


def eyewitness_meetings(game: BlindGame) -> tuple[int, ...]:
    """The meetings where a kill witness's ballot cites its own kill row."""

    marked: list[int] = []
    for meeting in game.meetings:
        cited = {
            ballot.voter: ballot.cited_observation_id for ballot in meeting.ballots
        }
        if any(
            row.citation_id is not None
            and row.holder in cited
            and cited[row.holder] == row.citation_id
            for row in meeting.own_kill_rows
        ):
            marked.append(meeting.index)
    return tuple(marked)


# ---------------------------------------------------------------------------
# The reveal readings
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Distance:
    """How far the losing side was from its own ending, and where it started.

    ``counts`` names the unit: tasks left for the crew, kills short of parity
    for the impostors.
    """

    counts: Literal["tasks_left", "kills_short_of_parity"]
    steps: int
    start: int


def _living_split(roles: Mapping[PlayerId, Role], living: frozenset[PlayerId]) -> int:
    """Living crewmates minus living impostors: kills short of parity."""

    crew = sum(1 for player in living if roles[player] == "CREWMATE")
    impostors = sum(1 for player in living if roles[player] == "IMPOSTOR")
    return crew - impostors


def distance(game: RevealGame) -> Distance | None:
    """The losing side's distance from its own ending, measured alike for both.

    An impostor win counts the tasks left; a task win counts kills short of
    parity at game over; an ejection win counts kills short of parity at the
    deciding meeting. A game stopped without a winner has no losing side.
    """

    roles = game.roles
    impostors = sum(1 for role in roles.values() if role == "IMPOSTOR")
    parity_start = len(roles) - 2 * impostors
    reason = game.end_reason
    if reason.startswith("IMPOSTOR_"):
        return Distance(
            counts="tasks_left",
            steps=game.tasks_assigned - game.tasks_done,
            start=game.tasks_assigned,
        )
    if reason == "CREWMATE_TASKS":
        removed = {kill.victim for kill in game.blind.kills} | {
            meeting.ejected
            for meeting in game.blind.meetings
            if meeting.ejected is not None
        }
        living = frozenset(player for player in roles if player not in removed)
        return Distance(
            counts="kills_short_of_parity",
            steps=_living_split(roles, living),
            start=parity_start,
        )
    if reason == "CREWMATE_EJECT":
        if not game.blind.meetings:
            raise GameProfileConformanceError(
                f"seed {game.blind.seed}: an ejection win with no meeting"
            )
        return Distance(
            counts="kills_short_of_parity",
            steps=_living_split(roles, game.blind.meetings[-1].living),
            start=parity_start,
        )
    return None


def reveal_pointers(game: RevealGame) -> Mapping[str, Pointer]:
    """Every reveal-only shelf the game sits on, the pair's halves included."""

    blind = game.blind
    hits: dict[str, Pointer] = {}
    one_vote: list[int] = []
    for meeting in blind.meetings:
        if meeting.ejected is None:
            continue
        counts = Counter(ballot.target for ballot in meeting.ballots)
        others = [
            count for target, count in counts.items() if target != meeting.ejected
        ]
        if counts[meeting.ejected] - (max(others) if others else 0) == 1:
            one_vote.append(meeting.index)
    if one_vote:
        hits[ONE_VOTE_EJECTION] = Pointer(meetings=tuple(one_vote))
    if blind.meetings and all(meeting.ejected is None for meeting in blind.meetings):
        hits[NOBODY_VOTED_OUT] = Pointer(
            meetings=tuple(meeting.index for meeting in blind.meetings)
        )
    measured = distance(game)
    if measured is not None:
        if measured.steps == 1 and measured.start >= DOWN_TO_THE_WIRE_START:
            hits[DOWN_TO_THE_WIRE] = Pointer()
        if measured.steps >= measured.start * RUNAWAY_SHARE:
            hits[RUNAWAY] = Pointer()
    if blind.meetings and blind.meetings[-1].tick == blind.terminal_tick:
        hits[DECIDED_AT_A_MEETING] = Pointer(meetings=(blind.meetings[-1].index,))
    right: list[int] = []
    wrong: list[int] = []
    for meeting in blind.meetings:
        ejected = meeting.ejected
        if ejected is None:
            continue
        ejecting = [ballot for ballot in meeting.ballots if ballot.target == ejected]
        vented = any(ejected in subjects for subjects in meeting.vent_flag_subjects)
        if (
            ejecting
            and all(
                LABEL_CLASSES[ballot.grounding_label] == "held" for ballot in ejecting
            )
            and not vented
            and ejected not in meeting.manufactured_subjects
        ):
            (right if game.roles[ejected] == "IMPOSTOR" else wrong).append(
                meeting.index
            )
    if right:
        hits[RIGHT_WITHOUT_PROOF] = Pointer(meetings=tuple(right))
    if wrong:
        hits[WRONG_ON_WHAT_IT_HELD] = Pointer(meetings=tuple(wrong))
    return MappingProxyType(hits)


# ---------------------------------------------------------------------------
# The leak rule and the saturation rule
# ---------------------------------------------------------------------------


def fisher_two_sided(a: int, b: int, c: int, d: int) -> Fraction:
    """The two-sided Fisher exact p of the table ``[[a, b], [c, d]]``, exactly.

    The sum of the hypergeometric probabilities of every table with the same
    margins that is no likelier than the observed one.
    """

    if min(a, b, c, d) < 0:
        raise ValueError(f"a 2x2 table cannot hold a negative count: {(a, b, c, d)}")
    row = a + b
    column = a + c
    total = a + b + c + d
    whole = math.comb(total, row)

    def probability(x: int) -> Fraction:
        return Fraction(
            math.comb(column, x) * math.comb(total - column, row - x), whole
        )

    observed = probability(a)
    low, high = max(0, row + column - total), min(row, column)
    return sum(
        (probability(x) for x in range(low, high + 1) if probability(x) <= observed),
        Fraction(0),
    )


@dataclass(frozen=True)
class LeakRow:
    """One 2x2 table: members with and without the fact, then non-members."""

    fact: str
    a: int
    b: int
    c: int
    d: int
    p: Fraction


@dataclass(frozen=True)
class CandidateClass:
    """One candidate's class for the era and the tables that decided it."""

    name: str
    games: int
    members: int
    rows: tuple[LeakRow, ...]
    classification: Classification


def era_facts(games: Sequence[RevealGame]) -> tuple[tuple[str, frozenset[int]], ...]:
    """Each fact the leak rule tests against, with the seeds that hold it.

    Each recorded ending present in the era, in the order the engine and the
    runner define them, then some meeting having ejected someone, then a
    crewmate having been ejected.
    """

    endings = game_endings()
    recorded = {game.end_reason for game in games}
    facts: list[tuple[str, frozenset[int]]] = [
        (
            ending,
            frozenset(game.blind.seed for game in games if game.end_reason == ending),
        )
        for ending in endings
        if ending in recorded
    ]
    facts.append(
        (
            ANY_EJECTION,
            frozenset(
                game.blind.seed
                for game in games
                if any(meeting.ejected is not None for meeting in game.blind.meetings)
            ),
        )
    )
    facts.append(
        (
            CREWMATE_EJECTED,
            frozenset(
                game.blind.seed
                for game in games
                if any(
                    meeting.ejected is not None
                    and game.roles[meeting.ejected] == "CREWMATE"
                    for meeting in game.blind.meetings
                )
            ),
        )
    )
    return tuple(facts)


def is_saturated(members: int, games: int) -> bool:
    """Whether ``members`` of an era's ``games`` is more than the saturation share."""

    return members * SATURATION_SHARE.denominator > games * SATURATION_SHARE.numerator


def classify_candidate(
    name: str,
    members: frozenset[int],
    *,
    seeds: frozenset[int],
    facts: Sequence[tuple[str, frozenset[int]]],
) -> CandidateClass:
    """One candidate's class: saturated first, then the leak rule.

    ``members`` are the games on the candidate, a tripped game excluded;
    ``seeds`` are every game of the era, a tripped one included, so each table
    spans the era with a tripped game a non-member.
    """

    if not members <= seeds:
        raise ValueError(f"{name}: members outside the era: {sorted(members - seeds)}")
    rows: list[LeakRow] = []
    for fact, holders in facts:
        a = len(members & holders)
        b = len(members - holders)
        c = len(holders - members)
        d = len(seeds) - a - b - c
        rows.append(
            LeakRow(fact=fact, a=a, b=b, c=c, d=d, p=fisher_two_sided(a, b, c, d))
        )
    classification: Classification
    if is_saturated(len(members), len(seeds)):
        classification = "saturated"
    elif any(row.p < LEAK_P_LEVEL for row in rows):
        classification = "leaks"
    else:
        classification = "shelf"
    return CandidateClass(
        name=name,
        games=len(seeds),
        members=len(members),
        rows=tuple(rows),
        classification=classification,
    )


# ---------------------------------------------------------------------------
# The served file
# ---------------------------------------------------------------------------


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


def _in_seed_order(seeds: Sequence[int], where: str) -> None:
    if list(seeds) != sorted(set(seeds)) or len(set(seeds)) != len(seeds):
        raise ValueError(f"{where}: members out of seed order: {list(seeds)}")


class ProfileConstants(_FrozenModel):
    """The design constants this profile version froze."""

    slow_burn_ticks: int
    wave_slack_ticks: int
    close_call_margin: int
    third_round_meetings: int
    down_to_the_wire_start: int
    runaway_share: str
    leak_p_level: str
    saturation_share: str


class CatalogueEntry(_FrozenModel):
    """One shelf, chip, facet or tripwire: its half and its class."""

    name: str
    half: Literal["pre_reveal", "reveal"]
    kind: Literal["shelf", "chip", "facet", "tripwire"]
    classification: Classification


class ShelfMember(_FrozenModel):
    seed: int
    meetings: tuple[int, ...]
    kill_ticks: tuple[int, ...]


class Shelf(_FrozenModel):
    name: str
    members: tuple[ShelfMember, ...]

    @model_validator(mode="after")
    def _seed_order(self) -> Shelf:
        _in_seed_order([member.seed for member in self.members], self.name)
        return self


class ChipMember(_FrozenModel):
    seed: int
    meetings: tuple[int, ...]


class Chip(_FrozenModel):
    name: str
    members: tuple[ChipMember, ...]

    @model_validator(mode="after")
    def _seed_order(self) -> Chip:
        _in_seed_order([member.seed for member in self.members], self.name)
        return self


class TripwireEntry(_FrozenModel):
    seed: int
    meeting: int


class TripwireReading(_FrozenModel):
    name: str
    tripwire: str
    governs: bool
    entries: tuple[TripwireEntry, ...]


class Tripwires(_FrozenModel):
    """Every reading's entries, and how many alibi-class flags T2 could read."""

    readings: tuple[TripwireReading, ...]
    alibi_flags: int
    alibi_flags_evaluable: int


class MeetingFacet(_FrozenModel):
    index: int
    tick: int
    trigger: TriggerKind
    regrouped: bool


class KillFacet(_FrozenModel):
    tick: int
    in_wave: bool


class ReportFacet(_FrozenModel):
    meeting: int
    corpse_age: int


class TripLabel(_FrozenModel):
    tripwire: str
    meeting: int


class GameFacets(_FrozenModel):
    """One game's pre-reveal facets, under All games."""

    seed: int
    ticks: int
    meetings: tuple[MeetingFacet, ...]
    kills: tuple[KillFacet, ...]
    reports: tuple[ReportFacet, ...]
    bodies_never_found: int
    moments: tuple[str, ...]
    tripped: tuple[TripLabel, ...]


class PreRevealHalf(_FrozenModel):
    shelves: tuple[Shelf, ...]
    chips: tuple[Chip, ...]
    games: tuple[GameFacets, ...]
    tripwires: Tripwires

    @model_validator(mode="after")
    def _seed_order(self) -> PreRevealHalf:
        _in_seed_order([game.seed for game in self.games], "all games")
        return self


class DistanceFacet(_FrozenModel):
    counts: Literal["tasks_left", "kills_short_of_parity"]
    steps: int
    start: int


class EjectionFacet(_FrozenModel):
    meeting: int
    right: bool


class RevealFacets(_FrozenModel):
    """One game's reveal facets."""

    seed: int
    ending: str
    distance: DistanceFacet | None
    sabotage_starts: tuple[int, ...]
    tasks_done: int
    tasks_assigned: int
    ejections: tuple[EjectionFacet, ...]


class Pair(_FrozenModel):
    """Decided without proof: the table right, and wrong on what it held."""

    right: Shelf
    wrong: Shelf


class ClassRow(_FrozenModel):
    fact: str
    a: int
    b: int
    c: int
    d: int
    p: float


class ClassTable(_FrozenModel):
    name: str
    games: int
    members: int
    rows: tuple[ClassRow, ...]
    classification: Classification


class RevealHalf(_FrozenModel):
    shelves: tuple[Shelf, ...]
    decided_without_proof: Pair
    games: tuple[RevealFacets, ...]
    class_tables: tuple[ClassTable, ...]

    @model_validator(mode="after")
    def _seed_order(self) -> RevealHalf:
        _in_seed_order([game.seed for game in self.games], "reveal facets")
        return self


class GameProfile(_FrozenModel):
    """The served profile of one set: provenance, catalogue and both halves."""

    rubric_version: int
    era: str | None
    manifest_key: str | None
    source_fingerprint: str
    seedset: str
    constants: ProfileConstants
    catalogue: tuple[CatalogueEntry, ...]
    pre_reveal: PreRevealHalf
    reveal: RevealHalf


@dataclass(frozen=True)
class ProfileStamp:
    """Where the profile came from: the bytes it was computed over."""

    era: str | None
    manifest_key: str | None
    source_fingerprint: str
    seedset: str


def profile_constants() -> ProfileConstants:
    """The design constants as the served file and the page render them."""

    return ProfileConstants(
        slow_burn_ticks=SLOW_BURN_TICKS,
        wave_slack_ticks=WAVE_SLACK_TICKS,
        close_call_margin=CLOSE_CALL_MARGIN,
        third_round_meetings=THIRD_ROUND_MEETINGS,
        down_to_the_wire_start=DOWN_TO_THE_WIRE_START,
        runaway_share=str(RUNAWAY_SHARE),
        leak_p_level=_decimal(LEAK_P_LEVEL),
        saturation_share=str(SATURATION_SHARE),
    )


def _decimal(value: Fraction) -> str:
    """A fraction whose denominator divides a power of ten, as a decimal."""

    for places in range(1, 7):
        scaled = value * 10**places
        if scaled.denominator == 1:
            return f"{float(value):.{places}f}"
    raise ValueError(f"{value} has no short decimal form")


def _shelf(name: str, hits: Mapping[int, Pointer]) -> Shelf:
    return Shelf(
        name=name,
        members=tuple(
            ShelfMember(
                seed=seed,
                meetings=hits[seed].meetings,
                kill_ticks=hits[seed].kill_ticks,
            )
            for seed in sorted(hits)
        ),
    )


def _game_facets(
    game: BlindGame,
    *,
    moments: tuple[str, ...],
    readings: Mapping[str, tuple[int, ...]],
    label: str,
) -> GameFacets:
    wave = {tick for _, tick in wave_kills(game)}
    reports: list[ReportFacet] = []
    found: set[PlayerId] = set()
    for meeting in game.meetings:
        if meeting.trigger_kind != "report" or meeting.trigger_body is None:
            continue
        kill = _kill_of(
            game,
            meeting.trigger_body,
            where=f"set {label}, seed {game.seed}, meeting index {meeting.index}",
        )
        found.add(kill.victim)
        reports.append(
            ReportFacet(meeting=meeting.index, corpse_age=meeting.tick - kill.tick)
        )
    labels = sorted(
        (meeting, tripwire)
        for reading, tripwire, governs in TRIPWIRE_READINGS
        if governs
        for meeting in readings[reading]
    )
    return GameFacets(
        seed=game.seed,
        ticks=game.terminal_tick,
        meetings=tuple(
            MeetingFacet(
                index=meeting.index,
                tick=meeting.tick,
                trigger=meeting.trigger_kind,
                regrouped=meeting.regrouped,
            )
            for meeting in game.meetings
        ),
        kills=tuple(
            KillFacet(tick=kill.tick, in_wave=kill.tick in wave)
            for kill in sorted(game.kills, key=lambda kill: kill.tick)
        ),
        reports=tuple(reports),
        bodies_never_found=sum(1 for kill in game.kills if kill.victim not in found),
        moments=moments,
        tripped=tuple(
            TripLabel(tripwire=tripwire, meeting=meeting)
            for meeting, tripwire in labels
        ),
    )


def _reveal_facets(game: RevealGame) -> RevealFacets:
    measured = distance(game)
    return RevealFacets(
        seed=game.blind.seed,
        ending=game.end_reason,
        distance=(
            None
            if measured is None
            else DistanceFacet(
                counts=measured.counts, steps=measured.steps, start=measured.start
            )
        ),
        sabotage_starts=game.sabotage_starts,
        tasks_done=game.tasks_done,
        tasks_assigned=game.tasks_assigned,
        ejections=tuple(
            EjectionFacet(
                meeting=meeting.index,
                right=game.roles[meeting.ejected] == "IMPOSTOR",
            )
            for meeting in game.blind.meetings
            if meeting.ejected is not None
        ),
    )


@dataclass(frozen=True)
class PreRevealReading:
    """Every pre-reveal reading of a set, from its blind projection alone.

    ``readings`` are each game's tripwire readings, ``candidates`` the
    candidate shelves each game sits on with their pointers, ``eyewitness`` the
    meetings the chip marks, ``tripped`` the games a governing reading trips,
    ``saturated`` the candidates the saturation rule makes facets, and
    ``facets`` every game's facets under All games, in seed order.
    """

    readings: Mapping[int, Mapping[str, tuple[int, ...]]]
    candidates: Mapping[int, Mapping[str, Pointer]]
    eyewitness: Mapping[int, tuple[int, ...]]
    tripped: frozenset[int]
    saturated: tuple[str, ...]
    facets: tuple[GameFacets, ...]


def read_pre_reveal(blind: BlindSet) -> PreRevealReading:
    """Everything the profile shows before the reveal, read from ``blind`` alone."""

    classes = label_classes()
    readings = {
        game.seed: game_readings(game, label=blind.label, classes=classes)
        for game in blind.games
    }
    candidates = {
        game.seed: candidate_pointers(game, label=blind.label) for game in blind.games
    }
    trips = frozenset(seed for seed, found in readings.items() if tripped(found))
    saturated = tuple(
        name
        for name in CANDIDATES
        if is_saturated(
            sum(
                1
                for seed, held in candidates.items()
                if seed not in trips and name in held
            ),
            len(blind.games),
        )
    )
    return PreRevealReading(
        readings=MappingProxyType(readings),
        candidates=MappingProxyType(candidates),
        eyewitness=MappingProxyType(
            {game.seed: eyewitness_meetings(game) for game in blind.games}
        ),
        tripped=trips,
        saturated=saturated,
        facets=tuple(
            _game_facets(
                game,
                moments=(
                    ()
                    if game.seed in trips
                    else tuple(
                        name for name in saturated if name in candidates[game.seed]
                    )
                ),
                readings=readings[game.seed],
                label=blind.label,
            )
            for game in blind.games
        ),
    )


def _catalogue(classes: Mapping[str, CandidateClass]) -> tuple[CatalogueEntry, ...]:
    entries: list[CatalogueEntry] = []
    for name in CANDIDATES:
        classification = classes[name].classification
        entries.append(
            CatalogueEntry(
                name=name,
                half="reveal" if classification == "leaks" else "pre_reveal",
                kind="facet" if classification == "saturated" else "shelf",
                classification=classification,
            )
        )
    entries.extend(
        CatalogueEntry(name=name, half="reveal", kind="shelf", classification=reads)
        for name, reads in REVEAL_SHELVES
    )
    entries.extend(
        CatalogueEntry(
            name=name, half="reveal", kind="shelf", classification="reads_a_role"
        )
        for name in (RIGHT_WITHOUT_PROOF, WRONG_ON_WHAT_IT_HELD)
    )
    entries.append(
        CatalogueEntry(
            name=EYEWITNESS_CHIP, half="pre_reveal", kind="chip", classification="chip"
        )
    )
    entries.extend(
        CatalogueEntry(
            name=name, half="pre_reveal", kind="facet", classification="facet"
        )
        for name in PRE_REVEAL_FACETS
    )
    entries.extend(
        CatalogueEntry(name=name, half="reveal", kind="facet", classification="facet")
        for name in REVEAL_FACETS
    )
    entries.extend(
        CatalogueEntry(
            name=name, half="pre_reveal", kind="tripwire", classification="tripwire"
        )
        for name in (HELD_NOTHING, MANUFACTURED)
    )
    return tuple(entries)


def build_profile(
    inputs: CensusInputs, scorecard: SetInputs, *, stamp: ProfileStamp
) -> GameProfile:
    """The profile of one set, every game of which is one era's universe."""

    blind = blind_projection(inputs, scorecard)
    pre = read_pre_reveal(blind)
    revealed = reveal_projection(inputs, blind)
    seeds = frozenset(game.seed for game in blind.games)
    facts = era_facts(revealed)
    classes = {
        name: classify_candidate(
            name,
            frozenset(
                seed
                for seed in seeds
                if seed not in pre.tripped and name in pre.candidates[seed]
            ),
            seeds=seeds,
            facts=facts,
        )
        for name in CANDIDATES
    }
    eligible = sorted(seeds - pre.tripped)

    def candidate_shelf(name: str) -> Shelf:
        return _shelf(
            name,
            {
                seed: pre.candidates[seed][name]
                for seed in eligible
                if name in pre.candidates[seed]
            },
        )

    reveal_hits = {game.blind.seed: reveal_pointers(game) for game in revealed}

    def reveal_shelf(name: str) -> Shelf:
        return _shelf(
            name,
            {
                seed: reveal_hits[seed][name]
                for seed in eligible
                if name in reveal_hits[seed]
            },
        )

    readings = tuple(
        TripwireReading(
            name=reading,
            tripwire=tripwire,
            governs=governs,
            entries=tuple(
                TripwireEntry(seed=game.seed, meeting=meeting)
                for game in blind.games
                for meeting in pre.readings[game.seed][reading]
            ),
        )
        for reading, tripwire, governs in TRIPWIRE_READINGS
    )
    return GameProfile(
        rubric_version=RUBRIC_VERSION,
        era=stamp.era,
        manifest_key=stamp.manifest_key,
        source_fingerprint=stamp.source_fingerprint,
        seedset=stamp.seedset,
        constants=profile_constants(),
        catalogue=_catalogue(classes),
        pre_reveal=PreRevealHalf(
            shelves=tuple(
                candidate_shelf(name)
                for name in CANDIDATES
                if classes[name].classification == "shelf"
            ),
            chips=(
                Chip(
                    name=EYEWITNESS_CHIP,
                    members=tuple(
                        ChipMember(seed=game.seed, meetings=pre.eyewitness[game.seed])
                        for game in blind.games
                        if pre.eyewitness[game.seed]
                    ),
                ),
            ),
            games=pre.facets,
            tripwires=Tripwires(
                readings=readings,
                alibi_flags=sum(
                    meeting.alibi_flags
                    for game in blind.games
                    for meeting in game.meetings
                ),
                alibi_flags_evaluable=sum(
                    meeting.alibi_flags_evaluable
                    for game in blind.games
                    for meeting in game.meetings
                ),
            ),
        ),
        reveal=RevealHalf(
            shelves=(
                *(
                    candidate_shelf(name)
                    for name in CANDIDATES
                    if classes[name].classification == "leaks"
                ),
                *(reveal_shelf(name) for name, _ in REVEAL_SHELVES),
            ),
            decided_without_proof=Pair(
                right=reveal_shelf(RIGHT_WITHOUT_PROOF),
                wrong=reveal_shelf(WRONG_ON_WHAT_IT_HELD),
            ),
            games=tuple(_reveal_facets(game) for game in revealed),
            class_tables=tuple(
                ClassTable(
                    name=name,
                    games=classes[name].games,
                    members=classes[name].members,
                    rows=tuple(
                        ClassRow(
                            fact=row.fact,
                            a=row.a,
                            b=row.b,
                            c=row.c,
                            d=row.d,
                            p=float(row.p),
                        )
                        for row in classes[name].rows
                    ),
                    classification=classes[name].classification,
                )
                for name in CANDIDATES
            ),
        ),
    )


def serialize_profile(profile: GameProfile) -> str:
    """The served file's bytes: indented JSON with a trailing newline."""

    return profile.model_dump_json(indent=2) + "\n"


__all__ = [
    "CANDIDATES",
    "CLOSE_CALL_MARGIN",
    "DOWN_TO_THE_WIRE_START",
    "LABEL_CLASSES",
    "LEAK_P_LEVEL",
    "RUBRIC_VERSION",
    "RUNAWAY_SHARE",
    "SATURATION_SHARE",
    "SLOW_BURN_TICKS",
    "THIRD_ROUND_MEETINGS",
    "WAVE_SLACK_TICKS",
    "BlindGame",
    "BlindMeeting",
    "BlindSet",
    "GameProfile",
    "GameProfileConformanceError",
    "ProfileStamp",
    "RevealGame",
    "blind_projection",
    "build_profile",
    "classify_candidate",
    "fisher_two_sided",
    "label_classes",
    "reveal_projection",
    "serialize_profile",
]
