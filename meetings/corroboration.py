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
record and earns no account. What is tested is the PLACEMENT
(:func:`~meetings.transcript.sighting_placement`), not the shape it was spoken
in: a sighting and a transition that put the subject in one room at one tick are
one placement, so either of the speaker's own record channels can bear it out.

A spoken :class:`~meetings.schemas.SawKillObservation` is therefore excluded: the
three channels are GROUNDED ones and the kill shape has none here to be tested
against. What would have to land before it could join is in
:func:`_speaker_grounding_places`. Excluded from the COUNT, it is still named on
the row -- a voice who watched the kill is not a voice who said nothing.

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
    SawKillObservation,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    TurnId,
)
from meetings.transcript import (
    MOVE_GROUNDING_TICK_TOLERANCE,
    MeetingTriggerKind,
    StatedPlacement,
    canonical_rooms,
    move_observation_matches_record,
    reconstruct_stated_paths,
    room_hops,
    sighting_observation_matches_record,
    sighting_placement,
    turn_observation_id,
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
    * ``first_hand_places`` -- per first-hand speaker, sorted by speaker, the
      ``(kind, room, tick)`` coordinates of the observations of ``subject`` their
      OWN record bore out, earliest first. A speaker counts ONCE however many
      records they hold or observations they spoke; the coordinates say WHICH of
      their statements earned the credit, so a speaker whose other sighting of
      the same subject is the one a contradiction above quotes is not thereby
      credited for that one. All three, because one speaker can place a subject
      in two rooms at one tick, or speak a sighting and a vent at one room and
      tick, with only one of them borne out. The triple is exactly what the
      transcript above distinguishes a row by, so a statement this cannot tell
      apart is one the transcript did not distinguish either.
    * ``adopted_silent`` -- accusing speakers who described nothing they saw of
      ``subject`` at all.
    * ``adopted_spoke_ungrounded`` -- accusing speakers who described seeing
      ``subject`` in a shape this ledger grounds, whose own record did not bear
      it out.
    * ``adopted_spoke_kill`` -- accusing speakers who said they watched
      ``subject`` kill. The shape has no grounding channel here, so it earns no
      account; it is a different thing from having said nothing, and the row
      says which. Precedence over the two above, because it is the strongest
      claim the speaker made.
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
    first_hand_places: tuple[tuple[PlayerId, tuple[tuple[str, str, int], ...]], ...]
    adopted_silent: tuple[PlayerId, ...]
    adopted_spoke_ungrounded: tuple[PlayerId, ...]
    adopted_spoke_kill: tuple[PlayerId, ...]
    flagged: bool
    opener_charge_turn_id: TurnId | None
    walkable_transits: tuple[tuple[str, str], ...]

    @property
    def first_hand(self) -> tuple[PlayerId, ...]:
        """The distinct speakers whose account of ``subject`` was borne out."""

        return tuple(speaker for speaker, _ in self.first_hand_places)

    @property
    def adopted(self) -> tuple[PlayerId, ...]:
        """Every other accusing speaker, sorted.

        The three adopted fields partition this set, so the split describes the
        voices without changing how many there are.
        """

        return tuple(
            sorted(
                (
                    *self.adopted_silent,
                    *self.adopted_spoke_ungrounded,
                    *self.adopted_spoke_kill,
                )
            )
        )

    @property
    def voices(self) -> int:
        """Distinct speakers carrying the charge."""

        return len(self.first_hand) + len(self.adopted)

    @property
    def rendered_first_hand_places(
        self,
    ) -> tuple[tuple[PlayerId, tuple[tuple[str, str, int], ...]], ...]:
        """``first_hand_places`` with each (room, tick) named once per speaker.

        One speaker can earn credit for one coordinate under two shapes -- a
        transition and the sighting standing behind it, or a sighting and a vent
        -- and the account line would then say the same room and tick twice
        ("arriving in EAST_HALL at tick 19, EAST_HALL at tick 19"). The FIRST
        entry of a repeated coordinate is the one printed, which is the movement
        shape wherever there is one: the coordinates are sorted by
        ``(tick, room, kind)`` and ``saw_move`` sorts ahead of ``saw_player``
        and ``saw_vent``. Where a sighting and a vent collide the plain sighting
        survives -- the weaker of the two wordings, the direction this block
        always moves in.

        Membership is untouched. This drops no speaker, no account and no
        statement from the ledger; the triple is still what says WHICH statement
        earned the credit, and only the second printing of one coordinate goes.
        """

        return tuple(
            (speaker, _distinct_coordinates(places))
            for speaker, places in self.first_hand_places
        )


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


def _distinct_coordinates(
    places: tuple[tuple[str, str, int], ...],
) -> tuple[tuple[str, str, int], ...]:
    """One ``(kind, room, tick)`` per (room, tick), the first of each kept."""

    seen: set[tuple[str, int]] = set()
    kept: list[tuple[str, str, int]] = []
    for kind, room, tick in places:
        if (room, tick) in seen:
            continue
        seen.add((room, tick))
        kept.append((kind, room, tick))
    return tuple(kept)


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


def _speaker_grounding_places(
    transcript: MeetingTranscript,
    *,
    speaker: PlayerId,
    subject: PlayerId,
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]],
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]],
    grounded_vent_ids: frozenset[str],
) -> tuple[tuple[str, str, int], ...]:
    """``(kind, room, tick)`` per FIRST-HAND observation of ``subject`` here.

    Empty means they grounded nothing, so this is the ledger's one definition of
    "first-hand" and the row's coordinates in a single pass: the ballot names
    the coordinates so a voter can tell the credited statement apart from the
    speaker's OTHER sighting of the same subject, which a contradiction above
    may be quoting. A ``saw_move`` is labelled by its destination, the room it
    places the subject in.

    Two grounded channels test a PLACEMENT and one tests a flag. A
    ``saw_player`` and a ``saw_move`` are one shape here --
    :func:`~meetings.transcript.sighting_placement` reads both as "the subject
    was in this room at this tick", a ``saw_move`` at its DESTINATION -- so
    either the speaker's own :class:`~meetings.schemas.SightingRecord` rows or
    their own :class:`~meetings.schemas.MoveWitnessRecord` rows may bear that
    placement out (:func:`_placement_grounded`). A spoken vent is the third
    channel and grounds only through the OWN observation id the detector minted
    a flag from (:func:`_grounded_vent_observation_ids`). A fabricated
    observation matches nothing in either channel and grounds nothing, which is
    the whole point of testing the record rather than the turn.

    Every channel is tested per STATEMENT, not per speaker: a witness who spoke
    two vents of one subject and had one of them grounded is one account, and
    the row names only the tick that held up.

    The sighting mapping arrives §4.7-firewalled from the manager, so an
    impostor's row naming a teammate cannot ground a case against that teammate.

    A spoken :class:`~meetings.schemas.SawKillObservation` is NOT a further
    channel. Each of the three above tests an account against a typed record or a
    minted flag, and the kill shape has neither: ``KillWitnessRecord`` is an
    ``orchestrator.game`` tactical-agent surface that never reaches the meeting
    layer, no such mapping is threaded into :func:`build_testimony_ledger`, and
    this module may not import one (the module docstring's import rule). Counting
    it would credit an UNGROUNDED claim as a first-hand source -- the one thing
    "first-hand" is defined here to exclude -- and would put on the ballot the
    same suspicion delta
    :func:`meetings.transcript._carries_relevant_observation` refuses on the
    accusation side. Admitting it needs a grounding channel FIRST; until one
    exists the shape is testimony a voter reads and no ledger row counts --
    which is why :func:`_spoke_of_subject` sorts such a speaker into
    ``adopted_spoke_kill`` and the ballot names what they said rather than
    reporting them silent. Ruled at #416 Q4.
    """

    sightings = sighting_records.get(speaker, ())
    moves = move_witness_records.get(speaker, ())
    places: set[tuple[str, str, int]] = set()
    for turn in transcript.turns:
        if turn.speaker != speaker:
            continue
        for index, observation in enumerate(turn.observations):
            if isinstance(observation, SawVentObservation):
                if (
                    observation.subject == subject
                    and turn_observation_id(turn=turn, index=index) in grounded_vent_ids
                ):
                    places.add((observation.type, observation.room, observation.tick))
                continue
            if not isinstance(observation, SawPlayerObservation | SawMoveObservation):
                continue
            # The two shapes ``sighting_placement`` places; every other one
            # locates nobody and returns ``None``.
            placement = sighting_placement(observation)
            if placement is None or placement.subject != subject:
                continue
            if _placement_grounded(
                observation, placement, sightings=sightings, moves=moves
            ):
                places.add((observation.type, placement.room, placement.tick))
    return tuple(sorted(places, key=lambda place: (place[2], place[1], place[0])))


def _placement_grounded(
    observation: SawPlayerObservation | SawMoveObservation,
    placement: SawPlayerObservation,
    *,
    sightings: tuple[SightingRecord, ...],
    moves: tuple[MoveWitnessRecord, ...],
) -> bool:
    """Whether either of the speaker's OWN record channels bears this placement out.

    ``placement`` is what :func:`~meetings.transcript.sighting_placement` reads
    off ``observation`` -- the sighting itself, or a transition's arrival. Both
    channels are consulted for both shapes, because the two shapes assert the
    same thing and a witness records whichever one their own perception minted:
    someone who watched a subject walk into a room holds a
    :class:`~meetings.schemas.MoveWitnessRecord` and may say "I saw them there",
    and someone who saw them standing there holds a
    :class:`~meetings.schemas.SightingRecord` and may say "I saw them arrive".

    Each channel keeps its own predicate and its own tick tolerance, so nothing
    is loosened by crossing them: the sighting channel is
    :func:`~meetings.transcript.sighting_observation_matches_record` at
    :data:`~meetings.transcript.SIGHTING_GROUNDING_TICK_TOLERANCE`, and the
    movement channel is exact
    (:data:`~meetings.transcript.MOVE_GROUNDING_TICK_TOLERANCE`) -- both halves
    of the transition for a spoken ``saw_move``
    (:func:`~meetings.transcript.move_observation_matches_record`), and the
    ARRIVAL half alone for a spoken ``saw_player``
    (:func:`_move_record_places_sighting`). The origin half stays unplaced in
    both directions, exactly as :func:`~meetings.transcript.sighting_placement`
    defines it.

    The movement channel is ADJUDICATED before it is matched, the discipline
    :func:`meetings.transcript._apply_movement_claim_shape` applies to both of
    its own arms: engine truth forbids two transitions of one subject landing on
    one tick, so a channel saying otherwise is wrong about something and no arm
    may take a placement from it (:func:`_movement_channel_conflicts`). Without
    that, this function could credit an account off the record that happens to
    fit the spoken room while the transit clause's own reconstruction, reading
    the same rows through the chokepoint, refused them all.
    """

    if any(
        sighting_observation_matches_record(placement, record) for record in sightings
    ):
        return True
    if _movement_channel_conflicts(
        moves, subject=placement.subject, tick=placement.tick
    ):
        return False
    if isinstance(observation, SawMoveObservation):
        return any(
            move_observation_matches_record(observation, record) for record in moves
        )
    return any(_move_record_places_sighting(observation, record) for record in moves)


def _movement_channel_conflicts(
    records: tuple[MoveWitnessRecord, ...], *, subject: PlayerId, tick: int
) -> bool:
    """Whether the speaker's own transitions disagree about where ``subject`` landed.

    :func:`meetings.transcript._destinations_conflict`'s reading of one speaker's
    channel, over the records naming this subject at this tick. Engine truth
    forbids two transitions of one subject landing on one tick, so a channel that
    says otherwise is describing something other than the transition the speaker
    meant, and neither the ledger nor the movement chokepoint may take a
    destination from it. Both agree on the same rows by construction: the tick
    window is :data:`~meetings.transcript.MOVE_GROUNDING_TICK_TOLERANCE`, the
    chokepoint's own, and the destinations are compared as
    :func:`~meetings.transcript.canonical_rooms` sets, the meeting layer's one
    room normalisation.
    """

    at_tick = [
        record
        for record in records
        if record.subject == subject
        and abs(record.tick - tick) <= MOVE_GROUNDING_TICK_TOLERANCE
    ]
    return len({canonical_rooms(record.to_room) for record in at_tick}) > 1


def _move_record_places_sighting(
    observation: SawPlayerObservation, record: MoveWitnessRecord
) -> bool:
    """Whether one own transition record puts the subject where the speaker said.

    The arrival half only: a :class:`~meetings.schemas.MoveWitnessRecord` places
    its subject in ``to_room`` at ``tick`` and nowhere else, which is the
    placement :func:`~meetings.transcript.sighting_placement` reads off the
    spoken twin of this record. A sighting naming the ORIGIN room grounds
    nothing here, since the record does not place the subject there at ``tick``.
    The tick must be EXACT: the channel under test sets the tolerance, and this
    is the movement channel
    (:data:`~meetings.transcript.MOVE_GROUNDING_TICK_TOLERANCE`).
    """

    if observation.subject != record.subject:
        return False
    if abs(observation.tick - record.tick) > MOVE_GROUNDING_TICK_TOLERANCE:
        return False
    spoken_rooms = canonical_rooms(observation.room)
    return bool(spoken_rooms and canonical_rooms(record.to_room) & spoken_rooms)


def _spoke_of_subject(
    transcript: MeetingTranscript, *, speaker: PlayerId, subject: PlayerId
) -> tuple[bool, bool]:
    """What ``speaker`` said they saw of ``subject``, as ``(kill, anything)``.

    The sibling of :func:`_speaker_grounding_places` for the voices it turned
    away: a speaker the record did not bear out still said something or said
    nothing, and a watched kill is neither of those -- it is the one shape this
    ledger has no channel to test, so the row names it as testimony instead of
    reporting silence. Only the four subject-naming shapes count; a roll-call
    ``whereabouts``, a task or a body report names no one.
    """

    kill = False
    anything = False
    for turn in transcript.turns:
        if turn.speaker != speaker:
            continue
        for observation in turn.observations:
            if not isinstance(
                observation,
                SawPlayerObservation
                | SawMoveObservation
                | SawVentObservation
                | SawKillObservation,
            ):
                continue
            if observation.subject != subject:
                continue
            anything = True
            if isinstance(observation, SawKillObservation):
                kill = True
    return kill, anything


def _grounded_vent_observation_ids(
    contradictions: Sequence[ContradictionRef],
) -> frozenset[str]:
    """The spoken vent observations the detector minted a flag from.

    A ``vent_sighting`` flag is minted from one speaker's own matched
    :class:`~meetings.schemas.VentWitnessRecord` and carries that exact spoken
    observation in both event ids, so the flag names WHICH account it grounds --
    not merely whom it accuses, and not merely that its speaker said something
    true once. Matching the id is what stops a second speaker riding someone
    else's grounded vent AND stops one witness's grounded vent vouching for
    their own second, ungrounded one; it is exact whatever the cardinality, since
    a witness with two grounded vents mints two flags on two of their own
    observations and a fabricator standing beside them matches none.

    The id format comes from :func:`~meetings.transcript.turn_observation_id`,
    the one home for it and the same writer the detector stamped the flag with,
    so this never re-derives an id shape of its own.
    """

    return frozenset(
        flag.event_a_id for flag in contradictions if flag.kind == "vent_sighting"
    )


def _room_label(rooms: frozenset[str]) -> str:
    """One spoken placement's canonical rooms as one readable label."""

    return "/".join(sorted(rooms))


def _walkable_transits(
    placements: Sequence[StatedPlacement],
) -> tuple[tuple[str, str], ...]:
    """The placement pairs about one subject that one tick of walking reconciles.

    A pair qualifies when the elapsed ticks between the two spoken placements
    COVER the doorway hops between the two rooms and stay inside
    :data:`~meetings.constants.MAP_ARBITRATION_MAX_TICK_GAP` -- the arbitration
    bounds the detector itself uses, read from :mod:`meetings.constants` rather
    than re-derived here. One hop costs one tick on the canonical map, so the
    walk must have had time to happen: two placements in adjacent rooms at the
    SAME tick are a physical impossibility, not a legal walk, and saying
    otherwise would clear the very charge the map refutes. Zero hops is dropped
    too: two statements naming one room agree, and there is no walk to explain.
    ``placements`` arrives tick-sorted from
    :func:`~meetings.transcript.reconstruct_stated_paths`, so the pairs come out
    earliest first, dedupe by room-label pair, and the inner scan can stop at the
    first placement past the tick bound rather than walk the rest.
    """

    seen: set[tuple[str, str]] = set()
    pairs: list[tuple[str, str]] = []
    for index, earlier in enumerate(placements):
        for later in placements[index + 1 :]:
            elapsed = later.tick - earlier.tick
            if elapsed > MAP_ARBITRATION_MAX_TICK_GAP:
                break
            hops = room_hops(
                earlier.rooms, later.rooms, max_hops=MAP_ARBITRATION_MAX_HOPS
            )
            if hops is None or hops == 0 or hops > elapsed:
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
    passed straight to :func:`~meetings.transcript.reconstruct_stated_paths`,
    together with ``move_witness_records``, so the placements the
    walkable-transit clause reads are the movement-shaped ones the rest of the
    meeting layer reads -- a transition the speaker's own record confirms places
    its subject at the destination instead of placing nobody.

    That set is NOT a superset of the detector's own unshaped reconstruction. It
    mostly adds, and it also takes away: a re-read replaces the room a witness
    spoke, so a transit line resting on the spoken room goes, and a row already
    at :data:`MAX_WALKABLE_TRANSITS_PER_SUBJECT` can have an earlier pair push a
    later one off the page. Over the four committed sets the shaping GAINS 256
    lines across 196 rows and LOSES 11 lines across 11 rows -- 8 to that cap
    displacement and 3 to a replaced room -- for 287 lines -> 532 and 241 rows
    carrying one -> 412 (172 rows go from none to at least one, and 1 goes the
    other way). Both directions are safe here only because this block weakens
    charges and mints nothing, and because the shaped placements reach
    ``walkable_transits`` alone, while ``first_hand``, ``adopted`` and
    ``flagged`` keep the inputs they had.
    """

    accusations = _accused_by_turn(transcript)
    if not accusations:
        return MeetingTestimonyLedger(rows=(), opener=opener)

    grounded_vent_ids = _grounded_vent_observation_ids(contradictions)
    flagged_subjects = frozenset(
        subject
        for contradiction in contradictions
        for subject in contradiction.subjects
    )
    paths = reconstruct_stated_paths(
        transcript,
        roster=roster,
        trigger_kind=trigger_kind,
        movement_witness_records=move_witness_records,
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
        first_hand_places: list[tuple[PlayerId, tuple[tuple[str, str, int], ...]]] = []
        silent: list[PlayerId] = []
        ungrounded: list[PlayerId] = []
        spoke_kill: list[PlayerId] = []
        for speaker in sorted(accusers[subject]):
            places = _speaker_grounding_places(
                transcript,
                speaker=speaker,
                subject=subject,
                sighting_records=sighting_records,
                move_witness_records=move_witness_records,
                grounded_vent_ids=grounded_vent_ids,
            )
            if places:
                first_hand_places.append((speaker, places))
                continue
            kill, anything = _spoke_of_subject(
                transcript, speaker=speaker, subject=subject
            )
            if kill:
                spoke_kill.append(speaker)
            elif anything:
                ungrounded.append(speaker)
            else:
                silent.append(speaker)
        opener_charge_turn_id: TurnId | None = None
        if subject == opener:
            charge = opener_charges.get(origin_speaker)
            if charge is not None and charge[0] < origin_index:
                opener_charge_turn_id = charge[1]
        rows.append(
            TestimonySupport(
                subject=subject,
                originating_turn_id=origin_turn_id,
                first_hand_places=tuple(first_hand_places),
                adopted_silent=tuple(silent),
                adopted_spoke_ungrounded=tuple(ungrounded),
                adopted_spoke_kill=tuple(spoke_kill),
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
