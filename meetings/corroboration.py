"""How many people actually SAW it: the per-subject testimony ledger.

A meeting knows two different things about a name: how many voices carry it,
and how many of those voices are accounts of something the speaker personally
witnessed. The ballot renders only the first. This module derives the second
from bytes the meeting already holds -- the transcript, the flags the detector
raised, and the per-speaker typed record channels -- so a voter reads a charge's
provenance beside the flags it is weighed against.

Nothing here suppresses, caps or re-scores anything. Agreement with the opener
is the corpus's strongest soft signal, so the ledger COUNTS and NAMES; pricing
the difference is the voter's call and the tally is untouched.

The grounding predicates are the detector's own
(:func:`meetings.transcript.sighting_observation_matches_record`,
:func:`~meetings.transcript.move_observation_matches_record`, and the
``vent_sighting`` flag channel), so "first-hand" means here exactly what it
means everywhere else in the meeting layer -- an invented sighting matches no
record and earns no account.

Keep this module import-light: :mod:`meetings.schemas`, :mod:`meetings.constants`
and :mod:`meetings.transcript` only, never :mod:`meetings.manager` -- the prompt
loader imports it for the ledger type and ``agents`` may not reach the manager
(.importlinter).
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

from meetings.constants import MAP_ARBITRATION_MAX_HOPS, MAP_ARBITRATION_MAX_TICK_GAP
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MoveWitnessRecord,
    PlayerId,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    TurnId,
)
from meetings.transcript import (
    MeetingTriggerKind,
    StatedPlacement,
    grounded_vent_subjects_from_flags,
    move_observation_matches_record,
    reconstruct_stated_paths,
    room_hops,
    sighting_observation_matches_record,
)

# The corroboration lever, DEFAULT OFF. ON, the vote ballot gains one guarded
# block per accused candidate: how many voices carry the charge, how many of
# them are first-hand accounts their own record confirms, which turn it started
# in, whether that turn was an answer to the opener's own charge, and any pair
# of spoken placements the map says one tick of walking reconciles. It changes
# only what a voter READS -- no flag is minted or re-banded, no threshold moves,
# no ballot is rewritten.
#
# Homed here beside the builder rather than in the loader: the loader builds its
# Jinja environment at import time and stays env-free for render INPUTS, while
# the threading decision belongs to the meeting layer. Registered in
# ``orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS`` by identity, so the
# recorded substrate stamp and this read-site are one function.
ENV_CORROBORATION_DISCIPLINE: Final[str] = "AILIBI_CORROBORATION_DISCIPLINE"
_CORROBORATION_DISCIPLINE_FLAG_TRUE: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)

# How many walkable-transit pairs one subject's row may carry. The ballot is a
# decision surface, not a map dump: the pair a voter is being asked to convict
# on is the point, and a long list of legal walks buries it.
MAX_WALKABLE_TRANSITS_PER_SUBJECT: Final[int] = 2


def corroboration_discipline_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the corroboration lever is ON. DEFAULT OFF.

    Reads :data:`ENV_CORROBORATION_DISCIPLINE` from ``env`` (defaulting to the
    real process environment). Default OFF: an unset / empty / unrecognised
    value is ``False``, so the manager threads no ledger and every rendered byte
    matches the committed registry. Accepts ``1/true/yes/on``
    (case-insensitive). The ``env`` argument lets tests toggle the lever
    deterministically without mutating ``os.environ``.

    Recorded provenance moves WITH the lever through
    :func:`orchestrator.game.prompt_versions_for_set`
    (:data:`~orchestrator.game.CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS`),
    so lever-shaped ballot bytes and default ballot bytes never share a version
    stamp (audits/audit-phase-17-absence-gate.md Ruling 3(d)).
    """

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_CORROBORATION_DISCIPLINE, "").strip().lower()
        in _CORROBORATION_DISCIPLINE_FLAG_TRUE
    )


@dataclass(frozen=True)
class TestimonySupport:
    """What stands behind the charge against one subject at one table.

    * ``subject`` -- the accused.
    * ``originating_turn_id`` -- the turn the charge started in (the first turn
      of this meeting whose accusation names ``subject``).
    * ``first_hand`` -- the distinct speakers who accused ``subject`` AND spoke
      an observation of them their OWN typed record confirms, sorted. A speaker
      counts ONCE however many records they hold or observations they spoke.
    * ``adopted`` -- every other distinct accusing speaker, sorted: they named
      ``subject`` and added nothing they saw. Disjoint from ``first_hand`` by
      construction, so ``len(first_hand) + len(adopted)`` is the honest count of
      voices carrying the charge.
    * ``flagged`` -- whether any contradiction detected at this table names
      ``subject``. Read off the flags, exactly as
      :func:`meetings.manager.guard_ballot_citation` reads them, never off a
      suspicion value.
    * ``opener_charge_turn_id`` -- set only when ``subject`` is the meeting's
      opener AND the originating accusation came from a speaker the opener had
      already accused; it is the opener's own accusing turn, the charge this one
      answers. An answer to a charge is not a second witness. Provenance only:
      no turn is reordered and the reply's counter-accusation stays legal.
    * ``walkable_transits`` -- pairs of spoken room labels about ``subject`` the
      map reconciles with one tick of walking
      (:data:`~meetings.constants.MAP_ARBITRATION_MAX_HOPS` doorway hops within
      :data:`~meetings.constants.MAP_ARBITRATION_MAX_TICK_GAP` ticks), earliest
      first, capped at :data:`MAX_WALKABLE_TRANSITS_PER_SUBJECT`.
    """

    subject: PlayerId
    originating_turn_id: TurnId
    first_hand: tuple[PlayerId, ...]
    adopted: tuple[PlayerId, ...]
    flagged: bool
    opener_charge_turn_id: TurnId | None
    walkable_transits: tuple[tuple[str, str], ...]

    @property
    def voices(self) -> int:
        """Distinct speakers carrying the charge."""

        return len(self.first_hand) + len(self.adopted)


@dataclass(frozen=True)
class MeetingTestimonyLedger:
    """Every accused subject's row for one meeting, plus who opened it.

    ``rows`` is ordered by the turn index the charge started in, then by subject
    id, so the render is deterministic. ``opener`` is the meeting's opener --
    the trigger's ``triggered_by``, the same derivation the ballot's reporter
    annotation uses -- and is what ``opener_charge_turn_id`` is measured against.
    """

    rows: tuple[TestimonySupport, ...]
    opener: PlayerId

    def __bool__(self) -> bool:
        """Truthy only with rows, so an empty ledger renders nothing."""

        return bool(self.rows)


def _accused_by_turn(
    transcript: MeetingTranscript,
) -> tuple[tuple[int, TurnId, PlayerId, PlayerId], ...]:
    """Every accusation at this table as ``(turn_index, turn_id, speaker, subject)``.

    Transcript order, self-accusations dropped: a speaker is not a voice against
    themselves, and counting one would inflate the very number this ledger
    exists to state honestly.
    """

    return tuple(
        (turn.turn_index, turn.turn_id, turn.speaker, claim.against)
        for turn in transcript.turns
        for claim in turn.claims
        if isinstance(claim, AccusationClaim) and claim.against != turn.speaker
    )


def _speaker_grounds_subject(
    transcript: MeetingTranscript,
    *,
    speaker: PlayerId,
    subject: PlayerId,
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]],
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]],
    vent_placed: frozenset[PlayerId],
) -> bool:
    """Whether ``speaker`` spoke a FIRST-HAND observation of ``subject`` here.

    The three grounded channels, each through the detector's own predicate: a
    ``saw_player`` matched by the speaker's own
    :class:`~meetings.schemas.SightingRecord` rows, a ``saw_move`` matched by
    their own :class:`~meetings.schemas.MoveWitnessRecord` rows, or a spoken
    vent whose subject the meeting's ``vent_sighting`` flags already carry. A
    fabricated observation matches nothing and grounds nothing, which is the
    whole point of testing the record rather than the turn.

    The sighting mapping arrives §4.7-firewalled from the manager, so an
    impostor's row naming a teammate cannot ground a case against that teammate.
    """

    sightings = sighting_records.get(speaker, ())
    moves = move_witness_records.get(speaker, ())
    for turn in transcript.turns:
        if turn.speaker != speaker:
            continue
        for observation in turn.observations:
            if isinstance(observation, SawPlayerObservation):
                if observation.subject == subject and any(
                    sighting_observation_matches_record(observation, record)
                    for record in sightings
                ):
                    return True
            elif isinstance(observation, SawMoveObservation):
                if observation.subject == subject and any(
                    move_observation_matches_record(observation, record)
                    for record in moves
                ):
                    return True
            elif isinstance(observation, SawVentObservation):
                if observation.subject == subject and subject in vent_placed:
                    return True
    return False


def _room_label(rooms: frozenset[str]) -> str:
    """One spoken placement's canonical rooms as one readable label."""

    return "/".join(sorted(rooms))


def _walkable_transits(
    placements: Sequence[StatedPlacement],
) -> tuple[tuple[str, str], ...]:
    """The placement pairs about one subject that one tick of walking reconciles.

    A pair qualifies when the two spoken ticks sit within
    :data:`~meetings.constants.MAP_ARBITRATION_MAX_TICK_GAP` of each other and
    the two canonical room sets sit within
    :data:`~meetings.constants.MAP_ARBITRATION_MAX_HOPS` doorway hops -- the
    arbitration bounds the detector itself uses, read from
    :mod:`meetings.constants` rather than re-derived here. Zero hops is dropped:
    two accounts naming the same room agree, and there is no walk to explain.
    ``placements`` arrives tick-sorted from
    :func:`~meetings.transcript.reconstruct_stated_paths`, so the pairs come out
    earliest first and dedupe by room-label pair.
    """

    seen: set[tuple[str, str]] = set()
    pairs: list[tuple[str, str]] = []
    for index, earlier in enumerate(placements):
        for later in placements[index + 1 :]:
            if later.tick - earlier.tick > MAP_ARBITRATION_MAX_TICK_GAP:
                continue
            hops = room_hops(
                earlier.rooms, later.rooms, max_hops=MAP_ARBITRATION_MAX_HOPS
            )
            if hops is None or hops == 0:
                continue
            pair = (_room_label(earlier.rooms), _room_label(later.rooms))
            if pair in seen:
                continue
            seen.add(pair)
            pairs.append(pair)
            if len(pairs) == MAX_WALKABLE_TRANSITS_PER_SUBJECT:
                return tuple(pairs)
    return tuple(pairs)


def build_testimony_ledger(
    transcript: MeetingTranscript,
    *,
    contradictions: Sequence[ContradictionRef],
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]],
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]],
    opener: PlayerId,
    roster: frozenset[PlayerId] | None = None,
    trigger_kind: MeetingTriggerKind | None = None,
) -> MeetingTestimonyLedger:
    """Derive one meeting's per-subject testimony ledger.

    A pure function of the transcript, the meeting's detected contradictions,
    the two per-speaker record mappings and the opener: no RNG, no clock, no
    environment read, no free-text parsing. Identical inputs return an identical
    ledger.

    ``sighting_records`` must be the §4.7-firewalled mapping the detector
    receives, not the raw accessor output. ``roster`` and ``trigger_kind`` are
    passed straight to :func:`~meetings.transcript.reconstruct_stated_paths`, so
    the placements this reads are the ones the detector reconstructed.
    """

    accusations = _accused_by_turn(transcript)
    if not accusations:
        return MeetingTestimonyLedger(rows=(), opener=opener)

    vent_placed = grounded_vent_subjects_from_flags(contradictions)
    flagged_subjects = frozenset(
        subject
        for contradiction in contradictions
        for subject in contradiction.subjects
    )
    paths = reconstruct_stated_paths(
        transcript, roster=roster, trigger_kind=trigger_kind
    )
    # Every turn in which the opener accused someone, so a charge answering one
    # of them can be recognised as an answer rather than a second witness.
    opener_charges: dict[PlayerId, tuple[int, TurnId]] = {}
    for turn_index, turn_id, speaker, subject in accusations:
        if speaker == opener and subject not in opener_charges:
            opener_charges[subject] = (turn_index, turn_id)

    origins: dict[PlayerId, tuple[int, TurnId, PlayerId]] = {}
    accusers: dict[PlayerId, list[PlayerId]] = {}
    for turn_index, turn_id, speaker, subject in accusations:
        if subject not in origins:
            origins[subject] = (turn_index, turn_id, speaker)
            accusers[subject] = []
        if speaker not in accusers[subject]:
            accusers[subject].append(speaker)

    rows: list[TestimonySupport] = []
    for subject, (origin_index, origin_turn_id, origin_speaker) in origins.items():
        first_hand = tuple(
            sorted(
                speaker
                for speaker in accusers[subject]
                if _speaker_grounds_subject(
                    transcript,
                    speaker=speaker,
                    subject=subject,
                    sighting_records=sighting_records,
                    move_witness_records=move_witness_records,
                    vent_placed=vent_placed,
                )
            )
        )
        adopted = tuple(
            sorted(
                speaker for speaker in accusers[subject] if speaker not in first_hand
            )
        )
        opener_charge_turn_id: TurnId | None = None
        if subject == opener:
            charge = opener_charges.get(origin_speaker)
            if charge is not None and charge[0] < origin_index:
                opener_charge_turn_id = charge[1]
        rows.append(
            TestimonySupport(
                subject=subject,
                originating_turn_id=origin_turn_id,
                first_hand=first_hand,
                adopted=adopted,
                flagged=subject in flagged_subjects,
                opener_charge_turn_id=opener_charge_turn_id,
                walkable_transits=_walkable_transits(paths.get(subject, ())),
            )
        )
    rows.sort(key=lambda row: (origins[row.subject][0], row.subject))
    return MeetingTestimonyLedger(rows=tuple(rows), opener=opener)


__all__ = [
    "ENV_CORROBORATION_DISCIPLINE",
    "MAX_WALKABLE_TRANSITS_PER_SUBJECT",
    "MeetingTestimonyLedger",
    "TestimonySupport",
    "build_testimony_ledger",
    "corroboration_discipline_enabled",
]
