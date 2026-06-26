"""Tests for :func:`meetings.transcript.detect_contradictions` (Task 8.7).

The contract mirrors DESIGN.md §5.4 + §6.4, now indexing over the single
ordered ``transcript.turns`` list (every alibi claim and ``saw_player``
observation appears on a :class:`MeetingTurn`, regardless of turn-kind):

* The detector flags pairs of events that cannot both be true:
  ``alibi_conflict`` for two alibis that place the same agent in
  different rooms over overlapping ticks, and ``alibi_vs_sighting`` for
  an alibi contradicted by a ``saw_player`` observation elsewhere within
  the alibi range.
* Flags are *information*, not verdicts -- the detector reports only what
  cannot both be true.
* The detector is deterministic: re-running on the same transcript
  produces byte-identical flags with a canonical ``contradiction_id``.
* Event ids reference the contributing turn
  (``turn:{turn_id}:claim:{i}`` / ``turn:{turn_id}:obs:{i}``).
"""

from __future__ import annotations

from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
)
from meetings.transcript import (
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_ADVERSARIAL,
    WEAK_REASON_BOUNDARY_OVERLAP,
    WEAK_REASON_KILL_SCENE,
    WEAK_REASON_NARROW_WINDOW,
    WEAK_REASON_SELF_PAIR,
    detect_contradictions,
    is_weak_contradiction,
)

_FLAG_ON = {"AILIBI_WITNESSED_KILL_EVIDENCE": "1"}


# --- Builders --------------------------------------------------------------


def _alibi(*, subject: str, from_tick: int, to_tick: int, room: str) -> AlibiClaim:
    return AlibiClaim(
        type="alibi",
        subject=subject,
        from_tick=from_tick,
        to_tick=to_tick,
        room=room,
    )


def _saw(
    *, tick: int, subject: str, room: str, co_present: tuple[str, ...] = ()
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player",
        tick=tick,
        subject=subject,
        room=room,
        co_present=co_present,
    )


def _turn(
    *,
    turn_index: int,
    speaker: str,
    turn_kind: str = "opening",
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text=f"turn {turn_index} from {speaker}",
    )


# --- Empty / non-contradictory transcripts ---------------------------------


class TestNoContradictions:
    def test_empty_transcript_returns_empty_tuple(self) -> None:
        assert detect_contradictions(MeetingTranscript()) == ()

    def test_single_alibi_cannot_self_conflict(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            claims=(_alibi(subject="p-1", from_tick=100, to_tick=200, room="STORAGE"),),
        )
        assert detect_contradictions(MeetingTranscript(turns=(turn,))) == ()

    def test_same_room_alibis_do_not_conflict(self) -> None:
        # Two agents corroborating that p-3 was in Storage at the same time
        # is *consistent* evidence, not a contradiction.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=120, to_tick=180, room="STORAGE"),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_non_overlapping_ranges_do_not_conflict(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            claims=(
                _alibi(subject="p-1", from_tick=100, to_tick=150, room="STORAGE"),
                _alibi(subject="p-1", from_tick=160, to_tick=200, room="ADMIN"),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=(turn,))) == ()

    def test_alibis_about_different_subjects_do_not_conflict(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-4", from_tick=100, to_tick=200, room="ADMIN"),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_sighting_outside_alibi_range_is_not_flagged(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=250, subject="p-3", room="CAFETERIA"),),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_sighting_matching_alibi_is_corroboration_not_conflict(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=150, subject="p-3", room="STORAGE"),),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_non_alibi_claims_are_ignored(self) -> None:
        # Accusations and corroborations carry no location data; pairing
        # them with a saw_player observation must not raise or emit a flag.
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-5",
                    confidence=0.7,
                    reason="suspicious behaviour near MedBay",
                ),
                CorroborationClaim(
                    type="corroboration",
                    supports="p-3",
                    on_tick=150,
                    reason="saw them in Storage",
                ),
            ),
            observations=(_saw(tick=150, subject="p-3", room="STORAGE"),),
        )
        assert detect_contradictions(MeetingTranscript(turns=(turn,))) == ()

    def test_non_sighting_observations_are_ignored(self) -> None:
        # Only ``saw_player`` is cross-referenced against alibis;
        # ``completed_task`` / ``found_body`` carry the reporter's location,
        # not the alibi subject's.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
                observations=(_saw(tick=150, subject="p-5", room="STORAGE"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                observations=(
                    CompletedTaskObservation(
                        type="completed_task",
                        tick=150,
                        task_id="wiring",
                        room="ELECTRICAL",
                    ),
                    FoundBodyObservation(
                        type="found_body",
                        tick=200,
                        body_of="p-4",
                        room="MEDBAY",
                    ),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()


# --- alibi_conflict --------------------------------------------------------


class TestAlibiConflict:
    def test_two_alibis_same_subject_different_rooms_overlapping_ticks(
        self,
    ) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        flag = flags[0]
        assert isinstance(flag, ContradictionRef)
        assert flag.kind == "alibi_conflict"
        assert flag.subjects == ("p-3",)
        # Source ids reference the contributing turns in canonical (sorted)
        # order so replays remain byte-stable.
        assert flag.event_a_id <= flag.event_b_id
        assert flag.event_a_id == "turn:m-1:turn-0:claim:0"
        assert flag.event_b_id == "turn:m-1:turn-1:claim:0"
        assert "STORAGE" in flag.description
        assert "CAFETERIA" in flag.description
        assert "p-3" in flag.description

    def test_self_contradicting_turn_is_flagged(self) -> None:
        # A single speaker listing two overlapping alibis with different
        # rooms is a self-contradiction the detector must catch.
        turn = _turn(
            turn_index=0,
            speaker="p-3",
            claims=(
                _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                _alibi(subject="p-3", from_tick=180, to_tick=220, room="ADMIN"),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=(turn,)))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert flags[0].subjects == ("p-3",)
        assert flags[0].event_a_id == "turn:m-1:turn-0:claim:0"
        assert flags[0].event_b_id == "turn:m-1:turn-0:claim:1"

    def test_boundary_overlap_is_a_conflict(self) -> None:
        # AlibiClaim ranges are inclusive, so alibis sharing a boundary tick
        # are mutually exclusive.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=150, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=200, room="ADMIN"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"

    def test_alibi_in_later_turn_conflicts_with_alibi_in_opening(self) -> None:
        # Alibis can be raised on any turn (opening, reply, opt_in); the
        # detector sees every turn surface.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-2",
                    turn_kind="reply",
                    claims=(
                        _alibi(subject="p-3", from_tick=150, to_tick=180, room="ADMIN"),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert {flags[0].event_a_id, flags[0].event_b_id} == {
            "turn:m-1:turn-0:claim:0",
            "turn:m-1:turn-1:claim:0",
        }


# --- alibi_vs_sighting -----------------------------------------------------


class TestAlibiVsSighting:
    def test_sighting_inside_alibi_range_different_room_is_flagged(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=150, subject="p-3", room="CAFETERIA"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        flag = flags[0]
        assert flag.kind == "alibi_vs_sighting"
        assert flag.subjects == ("p-3",)
        assert flag.event_a_id <= flag.event_b_id
        assert {flag.event_a_id, flag.event_b_id} == {
            "turn:m-1:turn-0:claim:0",
            "turn:m-1:turn-1:obs:0",
        }
        assert "STORAGE" in flag.description
        assert "CAFETERIA" in flag.description
        assert "p-3" in flag.description

    def test_sighting_at_alibi_boundary_is_flagged(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=200, subject="p-3", room="CAFETERIA"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))
        assert len(flags) == 1
        assert flags[0].kind == "alibi_vs_sighting"

    def test_multiple_sightings_each_emit_a_flag(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=120, subject="p-3", room="CAFETERIA"),),
            ),
            _turn(
                turn_index=2,
                speaker="p-7",
                observations=(_saw(tick=180, subject="p-3", room="ADMIN"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))
        assert len(flags) == 2
        assert all(flag.kind == "alibi_vs_sighting" for flag in flags)


# --- alibi_vs_physical (Task 13.4, report-phase-b-plan B3/B4) ---------------


def _saw_player_obs_ids(transcript: MeetingTranscript) -> set[str]:
    """Every ``saw_player`` observation id in the transcript (id-format mirror).

    Mirrors ``meetings.transcript._turn_observation_id`` so the firewall
    assertion below checks an ``alibi_vs_physical`` flag's placement event id
    against the public ``saw_player`` observations it must trace to -- with no
    reach into the belief layer (a leak test does not scan beliefs, so this is
    the guard that every placement is transcript-derived).
    """

    return {
        f"turn:{turn.turn_id}:obs:{index}"
        for turn in transcript.turns
        for index, obs in enumerate(turn.observations)
        if isinstance(obs, SawPlayerObservation)
    }


def _alibi_claim_ids(transcript: MeetingTranscript) -> set[str]:
    """Every ``alibi`` claim id in the transcript (id-format mirror)."""

    return {
        f"turn:{turn.turn_id}:claim:{index}"
        for turn in transcript.turns
        for index, claim in enumerate(turn.claims)
        if isinstance(claim, AlibiClaim)
    }


class TestAlibiVsPhysical:
    """The inferential ``alibi_vs_physical`` kind (Task 13.4).

    A subject's OWN stated alibi physically contradicted by independent
    CO-PRESENCE placements (the subject named in another player's ``saw_player``
    co-presence list) reconstructed from public testimony. STRONG only under the
    two-source conjunction: the alibi is uncorroborated AND
    ``PHYSICAL_CONTRADICTION_MIN_VOICES`` (2) distinct non-adversarial voices
    place the subject elsewhere at strictly interior ticks; a LONE contradicting
    voice emits WEAK (informs, cannot eject alone). Direct sightings of the
    subject stay the 9.7 weak ``alibi_vs_sighting`` band.
    """

    def _two_voice_conjunction(self) -> MeetingTranscript:
        # p-3's OWN alibi (STORAGE) physically contradicted by two independent
        # co-presence placements in EAST_HALL: p-5 sights p-1 (co-present p-3)
        # and p-7 sights p-2 (co-present p-3). Nobody places p-3 in STORAGE
        # after spawn -> uncorroborated; both co-presence ticks are interior.
        return MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )

    def test_two_source_co_presence_conjunction_is_strong(self) -> None:
        flags = detect_contradictions(self._two_voice_conjunction())
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        # One flag per contradicting co-presence placement (two voices).
        assert len(physical) == 2
        for flag in physical:
            assert flag.subjects == ("p-3",)
            # STRONG by construction: the physical detector mints no weak marker.
            assert is_weak_contradiction(flag) is False
            assert "p-3" in flag.description
            assert "EAST_HALL" in flag.description
            assert "STORAGE" in flag.description

    def test_every_physical_flag_traces_to_a_saw_player(self) -> None:
        # The firewall assertion (DoD): no alibi_vs_physical flag references a
        # placement that is not a public transcript saw_player, and its alibi
        # side is a real alibi claim -- so the flag is transcript-derived end to
        # end (never a belief-layer artifact).
        transcript = self._two_voice_conjunction()
        flags = detect_contradictions(transcript)
        obs_ids = _saw_player_obs_ids(transcript)
        claim_ids = _alibi_claim_ids(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        assert physical  # the scenario does emit flags to check
        for flag in physical:
            # event_a is the subject's alibi claim; event_b the co-presence
            # sighting (canonicalised order may swap them, so check membership).
            assert flag.event_a_id in claim_ids or flag.event_a_id in obs_ids
            assert flag.event_b_id in claim_ids or flag.event_b_id in obs_ids
            placement_ids = {flag.event_a_id, flag.event_b_id} - claim_ids
            assert placement_ids, "a physical flag must reference a saw_player"
            assert placement_ids <= obs_ids

    def test_lone_co_presence_voice_is_weak_not_strong(self) -> None:
        # A single contradicting voice is below the two-source bar: it emits a
        # WEAK alibi_vs_physical (informs) that cannot cross the gate alone.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        assert len(physical) == 1
        assert is_weak_contradiction(physical[0]) is True
        assert physical[0].subjects == ("p-3",)

    def test_corroborated_alibi_suppresses_physical(self) -> None:
        # An independent voice places p-3 INSIDE the STORAGE alibi (co-placement
        # agreement, the crewmate shape) -> the alibi is corroborated, so even
        # two contradicting voices mint no physical flag (the role-gate).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=3,
                    speaker="p-8",
                    observations=(
                        _saw(
                            tick=140,
                            subject="p-9",
                            room="STORAGE",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert not [f for f in flags if f.kind == "alibi_vs_physical"]

    def test_adversarial_voice_does_not_count_toward_the_conjunction(self) -> None:
        # p-7 places p-3 elsewhere but also ACCUSES p-3 (across the accusation
        # chain) -> the 13.3 adversarial guard drops p-7's voice, leaving one
        # non-adversarial voice: below the two-source bar, so no STRONG flag (the
        # lone p-5 voice stays weak).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    turn_kind="reply",
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-3",
                            confidence=0.8,
                            reason="placed p-3 away from their alibi",
                        ),
                    ),
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        # No STRONG flag: p-7's adversarial voice did not promote the conjunction.
        assert all(is_weak_contradiction(f) is True for f in physical)

    def test_endpoint_tick_co_presence_excluded(self) -> None:
        # A co-presence exactly on the alibi window edge (tick 100) is transit
        # fuzz and excluded, leaving one interior voice -> below the STRONG bar.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=100,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        # Only the interior p-7 voice survives -> weak, never STRONG.
        assert all(is_weak_contradiction(f) is True for f in physical)

    def test_direct_sightings_mint_no_physical_flag(self) -> None:
        # Two DIRECT sightings of the subject contradict the self-alibi, but the
        # physical detector reads co-presence ONLY: those stay the 9.7 weak
        # alibi_vs_sighting band (preserving the audited seed-3 design).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=150, subject="p-3", room="EAST_HALL"),),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(_saw(tick=160, subject="p-3", room="ADMIN"),),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert not [f for f in flags if f.kind == "alibi_vs_physical"]
        assert all(f.kind == "alibi_vs_sighting" for f in flags)

    def test_proxy_alibi_mints_no_physical_flag(self) -> None:
        # The alibi must be the subject's OWN (speaker == subject); a proxy alibi
        # (p-1 vouching for p-3) is the Task 10.6 retargeted-proxy domain, never
        # an alibi_vs_physical.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-4",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert not [f for f in flags if f.kind == "alibi_vs_physical"]

    def test_self_alibi_not_hidden_by_earlier_proxy_echo(self) -> None:
        # A proxy (p-1) states p-3's alibi FIRST, then p-3 restates it. The
        # global echo-dedup keeps the proxy claim and would drop p-3's own; the
        # physical detector de-echoes SELF-statements separately, so it still
        # sees p-3's OWN alibi and the two-voice conjunction fires STRONG against
        # p-3's own claim (not the proxy's).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",  # proxy states it first
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-3",  # subject restates own alibi (an echo)
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=3,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-4",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        assert physical
        assert all(is_weak_contradiction(f) is False for f in physical)
        assert all(f.subjects == ("p-3",) for f in physical)
        # The contradicted alibi is p-3's OWN claim (turn 1), never the proxy's.
        referenced = {f.event_a_id for f in physical} | {f.event_b_id for f in physical}
        assert "turn:m-1:turn-1:claim:0" in referenced
        assert "turn:m-1:turn-0:claim:0" not in referenced

    def test_co_presence_anchored_on_hallucinated_subject_is_ignored(self) -> None:
        # Each co-presence of p-3 is anchored on a sighting whose OWN subject is
        # a hallucinated id (p-98 / p-99). Under a roster those sightings are
        # dropped, so their co-presence cannot back a physical flag against p-3.
        roster = frozenset({"p-1", "p-2", "p-3", "p-4", "p-5", "p-6", "p-7"})

        def _scenario(anchor_a: str, anchor_b: str) -> MeetingTranscript:
            return MeetingTranscript(
                turns=(
                    _turn(
                        turn_index=0,
                        speaker="p-3",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=100,
                                to_tick=200,
                                room="STORAGE",
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=1,
                        speaker="p-5",
                        observations=(
                            _saw(
                                tick=150,
                                subject=anchor_a,
                                room="EAST_HALL",
                                co_present=("p-3",),
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=2,
                        speaker="p-7",
                        observations=(
                            _saw(
                                tick=160,
                                subject=anchor_b,
                                room="EAST_HALL",
                                co_present=("p-3",),
                            ),
                        ),
                    ),
                )
            )

        hallucinated = detect_contradictions(_scenario("p-98", "p-99"), roster=roster)
        assert not [f for f in hallucinated if f.kind == "alibi_vs_physical"]
        # Sanity: with roster-valid anchors the SAME shape DOES emit, so it is the
        # roster gate that suppressed above, not the co-presence path itself.
        valid = detect_contradictions(_scenario("p-1", "p-2"), roster=roster)
        assert [f for f in valid if f.kind == "alibi_vs_physical"]

    def test_emergency_trigger_kind_drops_kill_scene_exclusion(self) -> None:
        # An emergency opening carries a (fabricated) found_body in EAST_HALL.
        # With trigger_kind="emergency" the reconstruction does NOT treat that
        # room as a kill scene, so the co-presence placements there still count
        # and the conjunction fires; trigger_kind="report" (default) would gate
        # them out as kill-scene sightings.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    observations=(
                        FoundBodyObservation(
                            type="found_body",
                            tick=40,
                            body_of="p-9",
                            room="EAST_HALL",
                        ),
                    ),
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        report = detect_contradictions(transcript, trigger_kind="report")
        assert not [f for f in report if f.kind == "alibi_vs_physical"]
        emergency = detect_contradictions(transcript, trigger_kind="emergency")
        assert [f for f in emergency if f.kind == "alibi_vs_physical"]

    def test_physical_detection_is_deterministic(self) -> None:
        transcript = self._two_voice_conjunction()
        assert detect_contradictions(transcript) == detect_contradictions(transcript)


# --- alibi_vs_physical kill-scene intensification (Task 13.5.3 (b)) ---------


class TestKillSceneStrongFlag:
    """Task 13.5.3 (b) -- the kill-scene intensification of alibi_vs_physical.

    A co-presence placing the accused at the BODY's room within the kill window
    (normally DROPPED by the relevance gate -- presence at the scene must never
    exonerate) is RECOVERED behind ``AILIBI_WITNESSED_KILL_EVIDENCE`` and made to
    CONTRADICT an alibi placed elsewhere. STRICT (owner-LOCKED): a lone
    kill-scene placement is sub-gate; STRONG needs a second independent source.
    """

    def _body(self, *, room: str = "REACTOR") -> FoundBodyObservation:
        return FoundBodyObservation(
            type="found_body", tick=40, body_of="p-9", room=room
        )

    def _scene(
        self,
        *,
        placements: tuple[tuple[str, str, int, str], ...],
        alibi_room: str = "STORAGE",
    ) -> MeetingTranscript:
        # turn 0 reports the body (the kill scene); turn 1 is p-3's OWN alibi;
        # each placement is (speaker, sighting_subject, tick, room) naming p-3 as
        # co_present.
        turns = [
            _turn(turn_index=0, speaker="p-1", observations=(self._body(),)),
            _turn(
                turn_index=1,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room=alibi_room),
                ),
            ),
        ]
        for index, (speaker, subject, tick, room) in enumerate(placements, start=2):
            turns.append(
                _turn(
                    turn_index=index,
                    speaker=speaker,
                    observations=(
                        _saw(
                            tick=tick, subject=subject, room=room, co_present=("p-3",)
                        ),
                    ),
                )
            )
        return MeetingTranscript(turns=tuple(turns))

    def test_two_kill_scene_voices_strong_only_when_flag_on(self) -> None:
        # Two independent co-presence placements of p-3 at the REACTOR kill scene
        # contradict p-3's STORAGE alibi.
        transcript = self._scene(
            placements=(
                ("p-5", "p-8", 150, "REACTOR"),
                ("p-7", "p-2", 160, "REACTOR"),
            )
        )
        # Flag OFF (default): the kill-scene placements are dropped -> no flag,
        # byte-identical to HEAD.
        off = [
            f
            for f in detect_contradictions(transcript)
            if f.kind == "alibi_vs_physical"
        ]
        assert off == []
        # Flag ON: both placements recovered -> two-source conjunction STRONG.
        on = [
            f
            for f in detect_contradictions(transcript, env=_FLAG_ON)
            if f.kind == "alibi_vs_physical"
        ]
        assert len(on) == 2
        for flag in on:
            assert flag.subjects == ("p-3",)
            assert is_weak_contradiction(flag) is False  # STRONG
            assert "kill scene" in flag.description
            assert "REACTOR" in flag.description
            assert "STORAGE" in flag.description

    def test_lone_kill_scene_placement_is_sub_gate(self) -> None:
        # A SINGLE kill-scene placement INFORMS but cannot eject alone: WEAK with
        # the kill-scene marker (read by is_weak_contradiction), the STRICT rule.
        transcript = self._scene(placements=(("p-5", "p-8", 150, "REACTOR"),))
        on = [
            f
            for f in detect_contradictions(transcript, env=_FLAG_ON)
            if f.kind == "alibi_vs_physical"
        ]
        assert len(on) == 1
        flag = on[0]
        assert is_weak_contradiction(flag) is True
        assert WEAK_REASON_KILL_SCENE in flag.description
        assert flag.subjects == ("p-3",)
        # And OFF it is not even emitted.
        assert not [
            f
            for f in detect_contradictions(transcript)
            if f.kind == "alibi_vs_physical"
        ]

    def test_body_placement_two_source_conjunction_is_strong(self) -> None:
        # The second independent source can be a REGULAR (non-kill-scene)
        # placement: one REACTOR kill-scene voice + one EAST_HALL voice = two
        # sources -> STRONG (the "body+placement two-source conjunction").
        transcript = self._scene(
            placements=(
                ("p-5", "p-8", 150, "REACTOR"),  # kill scene
                ("p-7", "p-2", 160, "EAST_HALL"),  # regular physical placement
            )
        )
        on = [
            f
            for f in detect_contradictions(transcript, env=_FLAG_ON)
            if f.kind == "alibi_vs_physical"
        ]
        assert len(on) == 2
        assert all(is_weak_contradiction(f) is False for f in on)
        # Exactly one of the two STRONG flags names the kill scene.
        assert sum("kill scene" in f.description for f in on) == 1

    def test_accused_admitting_the_scene_is_not_contradicted(self) -> None:
        # If the accused's OWN alibi places them at the body's room (REACTOR), a
        # kill-scene placement there AGREES -> corroboration suppresses, no flag.
        # Presence-at-scene never exonerates, but a self-consistent account is no
        # contradiction.
        transcript = self._scene(
            placements=(
                ("p-5", "p-8", 150, "REACTOR"),
                ("p-7", "p-2", 160, "REACTOR"),
            ),
            alibi_room="REACTOR",
        )
        assert not [
            f
            for f in detect_contradictions(transcript, env=_FLAG_ON)
            if f.kind == "alibi_vs_physical"
        ]

    def test_flag_on_without_a_body_is_unchanged(self) -> None:
        # Flag ON but the meeting has NO kill scene (no opening found_body): the
        # kill-scene path is inert and the detector is byte-identical to flag OFF
        # (the regular 13.4 two-voice conjunction still fires STRONG).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-8",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        assert detect_contradictions(transcript) == detect_contradictions(
            transcript, env=_FLAG_ON
        )


# --- Mixed cases / determinism / surface contract --------------------------


class TestMixedAndDeterministic:
    def _mixed_transcript(self) -> MeetingTranscript:
        return MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-2",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    observations=(_saw(tick=160, subject="p-3", room="ADMIN"),),
                ),
            )
        )

    def test_alibi_conflict_and_alibi_vs_sighting_coexist(self) -> None:
        flags = detect_contradictions(self._mixed_transcript())

        kinds = sorted(flag.kind for flag in flags)
        # One alibi_conflict between the two alibis; one alibi_vs_sighting
        # per alibi whose room differs from ADMIN (both differ).
        assert kinds == [
            "alibi_conflict",
            "alibi_vs_sighting",
            "alibi_vs_sighting",
        ]

    def test_result_is_sorted_by_contradiction_id(self) -> None:
        flags = detect_contradictions(self._mixed_transcript())
        ids = [flag.contradiction_id for flag in flags]
        assert ids == sorted(ids)

    def test_pure_function_is_idempotent(self) -> None:
        transcript = self._mixed_transcript()
        first = detect_contradictions(transcript)
        second = detect_contradictions(transcript)
        assert first == second

    def test_canonical_event_pair_ordering(self) -> None:
        # The same logical contradiction produces a canonical
        # (sorted) event-id pair regardless of which claim the detector
        # visits first, so the §6.6 memory view never double-counts.
        flags = detect_contradictions(
            MeetingTranscript(
                turns=(
                    _turn(
                        turn_index=0,
                        speaker="p-1",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=100,
                                to_tick=200,
                                room="STORAGE",
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=1,
                        speaker="p-2",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=150,
                                to_tick=180,
                                room="CAFETERIA",
                            ),
                        ),
                    ),
                )
            )
        )
        assert len(flags) == 1
        assert flags[0].event_a_id <= flags[0].event_b_id
        assert flags[0].contradiction_id == (
            f"contra:alibi_conflict:{flags[0].event_a_id}|{flags[0].event_b_id}"
        )

    def test_flags_are_shared_schema_objects(self) -> None:
        flags = detect_contradictions(
            MeetingTranscript(
                turns=(
                    _turn(
                        turn_index=0,
                        speaker="p-1",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=100,
                                to_tick=200,
                                room="STORAGE",
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=1,
                        speaker="p-2",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=150,
                                to_tick=180,
                                room="CAFETERIA",
                            ),
                        ),
                    ),
                )
            )
        )

        assert isinstance(flags, tuple)
        for flag in flags:
            assert isinstance(flag, ContradictionRef)
            dumped = flag.model_dump(mode="json")
            assert ContradictionRef.model_validate(dumped) == flag


# --- Cross-speaker alibi_conflict strength (Task 13.3, B2) ------------------


class TestCrossSpeakerConflictStrength:
    """A genuinely-independent cross-speaker ``alibi_conflict`` is STRONG.

    Task 13.3 (DESIGN.md §5.4; report-phase-b-plan B2; grounding-audit P1):
    two DISTINCT non-subject speakers placing the same subject in two rooms
    over overlapping ticks, with NONE of the four weak-guard conditions
    (self-pair / adversarial / narrow / boundary), is a real inferential
    contradiction and carries NO weak marker -- so ``is_weak_contradiction``
    returns ``False`` and a re-extraction stamps ``strong=True``. The four
    weak guards stay byte-identical: each still down-weights its own
    false-positive shape. These tests lock both halves in so a future detector
    edit cannot silently re-mark the independent case weak (Goodharting R7) or
    drop a guard (re-opening the wrong-ejection path the weak delta closed).
    """

    def test_independent_cross_speaker_conflict_is_strong(self) -> None:
        # Two distinct non-subject speakers (p-1, p-2) place subject p-3 in
        # disjoint rooms over a real (non-boundary) overlap; wide windows; no
        # accusation relation. None of the four guards fire -> STRONG.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=120, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        flag = flags[0]
        assert flag.kind == "alibi_conflict"
        assert flag.subjects == ("p-3",)
        assert is_weak_contradiction(flag) is False
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flag.description

    def test_self_pair_conflict_stays_weak(self) -> None:
        # Both conflicting alibis are the subject's OWN statements: the subject's
        # coarse self-recollection disagreeing with itself, not cross-speaker
        # evidence. The self-pair guard keeps it weak.
        turn = _turn(
            turn_index=0,
            speaker="p-3",
            claims=(
                _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                _alibi(subject="p-3", from_tick=120, to_tick=180, room="CAFETERIA"),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=(turn,)))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_SELF_PAIR in flags[0].description

    def test_adversarial_conflict_stays_weak(self) -> None:
        # One speaker (p-1) is across the accusation chain from the subject
        # (p-1 accused p-3), so p-1's alibi about p-3 is a weaponised
        # counter-alibi (the seed-13 m2 impostor deflection). The adversarial
        # guard keeps the conflict weak even though the speakers are distinct.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-3",
                        confidence=0.7,
                        reason="near MedBay before the kill",
                    ),
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=120, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_ADVERSARIAL in flags[0].description

    def test_narrow_window_conflict_stays_weak(self) -> None:
        # Distinct non-subject speakers, but one alibi spans a sub-
        # NARROW_ALIBI_WINDOW_TICKS window (a single transit observation), so
        # the conflict inherits the tick-boundary fuzz: weak.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=151, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_NARROW_WINDOW in flags[0].description

    def test_boundary_overlap_conflict_stays_weak(self) -> None:
        # Distinct non-subject speakers whose windows overlap ONLY on the
        # junction tick where one ends and the other begins -- a movement pair
        # ("STORAGE t100-150" then "CAFETERIA t150-200"), not two incompatible
        # accounts: weak.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=150, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=200, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_BOUNDARY_OVERLAP in flags[0].description
