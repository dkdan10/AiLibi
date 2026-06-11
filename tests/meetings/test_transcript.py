"""Tests for the transcript helpers (Task 8.7).

Exercises the pure chain logic that backs the reactive accusation chain
(DESIGN.md §5.2) -- :func:`accusation_target`, :func:`next_chain_step`,
:func:`walk_chain` -- plus the chain-turn ordering predicates. The chain
helpers are the single source of truth shared by
:class:`meetings.manager.MeetingManager` (recording) and the replay-walk
(reconstruction), so these tests pin the determinism the replay invariant
relies on. General contradiction detection over ``transcript.turns``
lives in ``test_contradictions.py``; the Task 9.7 weak-signal
classification (DESIGN.md §5.4; audit gp-1 precision) is pinned here.
"""

from __future__ import annotations

import pytest

from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
)
from meetings.transcript import (
    NARROW_ALIBI_WINDOW_TICKS,
    PLACEHOLDER_ROOM_LABELS,
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_ADVERSARIAL,
    WEAK_REASON_BOUNDARY_OVERLAP,
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_NARROW_WINDOW,
    WEAK_REASON_SELF_PAIR,
    WEAK_REASON_SELF_STATED,
    DetectedCorroboration,
    accusation_target,
    canonical_rooms,
    contradiction_lift_key,
    detect_contradictions,
    detect_corroborations,
    is_canonically_ordered,
    is_weak_contradiction,
    next_chain_step,
    sort_turns_canonically,
    walk_chain,
)


def _turn(
    *,
    turn_index: int,
    speaker: str,
    turn_kind: str = "reply",
    reply_to: str | None = None,
    accuses: str | None = None,
) -> MeetingTurn:
    claims = (
        (
            AccusationClaim(
                type="accusation", against=accuses, confidence=0.5, reason="r"
            ),
        )
        if accuses is not None
        else ()
    )
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to=reply_to,
        claims=claims,
        free_text=f"turn {turn_index}",
    )


class TestAccusationTarget:
    def test_first_accusation_claim_is_the_target(self) -> None:
        turn = MeetingTurn(
            turn_id="m-1:turn-0",
            turn_index=0,
            speaker="p-1",
            turn_kind="opening",
            reply_to=None,
            claims=(
                AccusationClaim(
                    type="accusation", against="p-5", confidence=0.7, reason="r"
                ),
                AccusationClaim(
                    type="accusation", against="p-9", confidence=0.9, reason="r"
                ),
            ),
            free_text="",
        )

        # The chain passes on the FIRST accusation in claim order, not the
        # most confident -- a deterministic, replay-stable tie-break.
        assert accusation_target(turn) == "p-5"

    def test_no_accusation_returns_none(self) -> None:
        turn = _turn(turn_index=0, speaker="p-1", turn_kind="opening")

        assert accusation_target(turn) is None


_LIVING_4 = frozenset({"p-1", "p-3", "p-5", "p-7"})


class TestNextChainStep:
    def test_accusation_passes_floor_to_the_accused(self) -> None:
        prev = _turn(turn_index=0, speaker="p-1", turn_kind="opening", accuses="p-3")

        step = next_chain_step(
            prev_turn=prev,
            spoken=frozenset({"p-1"}),
            living_ids=_LIVING_4,
            turns_recorded=1,
        )

        assert step.next_speaker == "p-3"
        assert step.termination is None

    def test_no_new_accusation_terminates(self) -> None:
        prev = _turn(turn_index=1, speaker="p-3", turn_kind="reply")

        step = next_chain_step(
            prev_turn=prev,
            spoken=frozenset({"p-1", "p-3"}),
            living_ids=_LIVING_4,
            turns_recorded=2,
        )

        assert step.next_speaker is None
        assert step.termination == "no_new_accusation"

    def test_accusation_of_non_living_player_terminates(self) -> None:
        # The floor cannot pass to a dead / hallucinated id -- terminate
        # rather than dangling on a player who is not at the table.
        prev = _turn(turn_index=1, speaker="p-3", turn_kind="reply", accuses="p-99")

        step = next_chain_step(
            prev_turn=prev,
            spoken=frozenset({"p-1", "p-3"}),
            living_ids=_LIVING_4,
            turns_recorded=2,
        )

        assert step.next_speaker is None
        assert step.termination == "target_not_living"

    def test_re_accusation_cycle_terminates(self) -> None:
        # p-3 re-accuses p-1, who already opened -> cycle.
        prev = _turn(turn_index=1, speaker="p-3", turn_kind="reply", accuses="p-1")

        step = next_chain_step(
            prev_turn=prev,
            spoken=frozenset({"p-1", "p-3"}),
            living_ids=_LIVING_4,
            turns_recorded=2,
        )

        assert step.next_speaker is None
        assert step.termination == "re_accusation_cycle"

    def test_turn_count_cap_terminates(self) -> None:
        # Defensive cap: a living, not-yet-spoken accused is still refused
        # once the recorded turn count reaches the living-player count. (In
        # consistent operation this coincides with the cycle check, since
        # every reply is a fresh living speaker; the cap is the explicit
        # bound.) Here a 2-living table has already recorded 2 turns.
        prev = _turn(turn_index=1, speaker="p-1", turn_kind="reply", accuses="p-3")

        step = next_chain_step(
            prev_turn=prev,
            spoken=frozenset({"p-1"}),
            living_ids=frozenset({"p-1", "p-3"}),
            turns_recorded=2,
        )

        assert step.next_speaker is None
        assert step.termination == "turn_count_cap"


class TestWalkChain:
    def test_walks_a_well_formed_chain_without_the_llm(self) -> None:
        # opening(p-1 accuses p-3) -> reply(p-3 accuses p-5) -> reply(p-5,
        # defensive) terminates; then one opt_in turn.
        turns = (
            _turn(turn_index=0, speaker="p-1", turn_kind="opening", accuses="p-3"),
            _turn(
                turn_index=1,
                speaker="p-3",
                turn_kind="reply",
                reply_to="m-1:turn-0",
                accuses="p-5",
            ),
            _turn(
                turn_index=2,
                speaker="p-5",
                turn_kind="reply",
                reply_to="m-1:turn-1",
            ),
            _turn(turn_index=3, speaker="p-7", turn_kind="opt_in"),
        )

        walk = walk_chain(MeetingTranscript(turns=turns), living_ids=_LIVING_4)

        assert walk.chain_speakers == ("p-1", "p-3", "p-5")
        assert walk.termination == "no_new_accusation"
        assert walk.opt_in_speakers == ("p-7",)

    def test_empty_transcript_is_an_empty_walk(self) -> None:
        walk = walk_chain(MeetingTranscript(), living_ids=_LIVING_4)

        assert walk.chain_speakers == ()
        assert walk.opt_in_speakers == ()

    def test_reply_by_unexpected_speaker_raises(self) -> None:
        # p-1 accused p-3, but the recorded reply is by p-9 -- a chain that
        # could not have been produced deterministically.
        turns = (
            _turn(turn_index=0, speaker="p-1", turn_kind="opening", accuses="p-3"),
            _turn(
                turn_index=1,
                speaker="p-9",
                turn_kind="reply",
                reply_to="m-1:turn-0",
            ),
        )

        with pytest.raises(ValueError, match="predicts"):
            walk_chain(MeetingTranscript(turns=turns), living_ids=_LIVING_4)

    def test_broken_reply_to_link_raises(self) -> None:
        turns = (
            _turn(turn_index=0, speaker="p-1", turn_kind="opening", accuses="p-3"),
            _turn(
                turn_index=1,
                speaker="p-3",
                turn_kind="reply",
                reply_to="m-1:turn-99",
            ),
        )

        with pytest.raises(ValueError, match="links to"):
            walk_chain(MeetingTranscript(turns=turns), living_ids=_LIVING_4)

    def test_non_opening_head_raises(self) -> None:
        turns = (_turn(turn_index=0, speaker="p-1", turn_kind="reply"),)

        with pytest.raises(ValueError, match="opening"):
            walk_chain(MeetingTranscript(turns=turns), living_ids=_LIVING_4)

    def test_non_opt_in_tail_after_chain_raises(self) -> None:
        # The opening names no accusation, so the chain ends immediately; a
        # following ``reply`` turn is structurally impossible.
        turns = (
            _turn(turn_index=0, speaker="p-1", turn_kind="opening"),
            _turn(turn_index=1, speaker="p-3", turn_kind="reply"),
        )

        with pytest.raises(ValueError, match="opt_in"):
            walk_chain(MeetingTranscript(turns=turns), living_ids=_LIVING_4)


class TestSortTurnsCanonically:
    def test_empty_returns_empty_tuple(self) -> None:
        assert sort_turns_canonically([]) == ()

    def test_sorts_by_turn_index(self) -> None:
        t0 = _turn(turn_index=0, speaker="p-1", turn_kind="opening")
        t1 = _turn(turn_index=1, speaker="p-3")
        t2 = _turn(turn_index=2, speaker="p-5")

        result = sort_turns_canonically([t2, t0, t1])

        assert result == (t0, t1, t2)


class TestIsCanonicallyOrdered:
    def test_empty_is_canonically_ordered(self) -> None:
        assert is_canonically_ordered([]) is True

    def test_contiguous_ascending_turn_indices_are_canonical(self) -> None:
        turns = (
            _turn(turn_index=0, speaker="p-1", turn_kind="opening"),
            _turn(turn_index=1, speaker="p-3"),
            _turn(turn_index=2, speaker="p-5"),
        )

        assert is_canonically_ordered(turns) is True

    def test_index_not_matching_position_is_not_canonical(self) -> None:
        turns = (
            _turn(turn_index=0, speaker="p-1", turn_kind="opening"),
            _turn(turn_index=2, speaker="p-3"),
        )

        assert is_canonically_ordered(turns) is False


# --- Weak-signal classification (Task 9.7; DESIGN.md §5.4, audit gp-1) ------


def _alibi_turn(
    *,
    turn_index: int,
    speaker: str,
    subject: str,
    from_tick: int,
    to_tick: int,
    room: str,
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening" if turn_index == 0 else "reply",
        reply_to=None,
        claims=(
            AlibiClaim(
                type="alibi",
                subject=subject,
                from_tick=from_tick,
                to_tick=to_tick,
                room=room,
            ),
        ),
        free_text=f"turn {turn_index}",
    )


def _sighting_turn(
    *, turn_index: int, speaker: str, subject: str, tick: int, room: str
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening" if turn_index == 0 else "reply",
        reply_to=None,
        observations=(
            SawPlayerObservation(
                type="saw_player", tick=tick, subject=subject, room=room
            ),
        ),
        free_text=f"turn {turn_index}",
    )


class TestWeakContradictionClassification:
    """Task 9.7: the detector marks the audited false-positive patterns.

    A lone ``alibi_vs_sighting`` railroaded 13/13 wrong ejections in the
    9.5 baseline; 8/13 were the reporter's own self-stated alibi against
    a third party's sighting. The detector still emits every flag (the
    recorded set stays honest) but appends the weak audit marker for the
    two patterns, and :func:`is_weak_contradiction` is the predicate
    belief Rule 2 keys its graduated delta on.
    """

    def test_self_stated_alibi_vs_third_party_sighting_is_weak(self) -> None:
        # The seed-3 audited shape: the reporter's own alibi (CAFETERIA)
        # against a third party's sighting of them (EAST_HALL).
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-5",
                    subject="p-5",
                    from_tick=100,
                    to_tick=200,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-5",
                    tick=150,
                    room="EAST_HALL",
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        flag = flags[0]
        assert flag.kind == "alibi_vs_sighting"
        assert WEAK_CONTRADICTION_MARKER_PREFIX in flag.description
        assert WEAK_REASON_SELF_STATED in flag.description
        assert WEAK_REASON_NARROW_WINDOW not in flag.description
        assert is_weak_contradiction(flag) is True

    def test_third_party_alibi_wide_window_stays_strong(self) -> None:
        # Two third parties disagreeing about the subject's location is
        # the strong pattern: no marker, full Rule-2 weight downstream.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-5",
                    from_tick=100,
                    to_tick=200,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-5",
                    tick=150,
                    room="EAST_HALL",
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flags[0].description
        assert is_weak_contradiction(flags[0]) is False

    def test_narrow_window_third_party_alibi_is_weak(self) -> None:
        # A 2-tick claim and an in-range sighting elsewhere can both be
        # honest accounts of one transit (movement is one room per tick).
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-5",
                    from_tick=3,
                    to_tick=4,
                    room="STORAGE",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-2", subject="p-5", tick=3, room="MEDBAY"
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        assert WEAK_REASON_NARROW_WINDOW in flags[0].description
        assert WEAK_REASON_SELF_STATED not in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_window_at_threshold_is_not_narrow(self) -> None:
        # Boundary pin: width == NARROW_ALIBI_WINDOW_TICKS is NOT narrow
        # ("below a small constant"), so a third-party claim spanning it
        # keeps full weight.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-5",
                    from_tick=100,
                    to_tick=100 + NARROW_ALIBI_WINDOW_TICKS,
                    room="STORAGE",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-2", subject="p-5", tick=101, room="MEDBAY"
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        assert is_weak_contradiction(flags[0]) is False

    def test_self_stated_and_narrow_reasons_render_in_fixed_order(self) -> None:
        # A single-tick self-alibi with the sighting on that tick matches
        # all three vs-sighting patterns; the reasons render in the fixed
        # order self-stated -> narrow -> endpoint (Task 10.1 adds the
        # endpoint reason) so the marker is byte-stable across runs.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-5",
                    subject="p-5",
                    from_tick=7,
                    to_tick=7,
                    room="ADMIN",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-2", subject="p-5", tick=7, room="MEDBAY"
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        marker = (
            f"{WEAK_CONTRADICTION_MARKER_PREFIX}"
            f"{WEAK_REASON_SELF_STATED}; {WEAK_REASON_NARROW_WINDOW}; "
            f"{WEAK_REASON_ENDPOINT_TICK}]"
        )
        assert flags[0].description.endswith(marker)
        assert is_weak_contradiction(flags[0]) is True

    def test_narrow_alibi_conflict_is_weak_classified(self) -> None:
        # Task 10.1 (audit gp-2 C-C-2): the conflict path now receives the
        # 9.7 classification it previously skipped. A conflict built on a
        # single-tick claim is transit fuzz, weak-banded -- the pre-10.1
        # behaviour (always strong) is exactly what let one such pair
        # carry the full Rule-2 delta.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-5",
                    subject="p-5",
                    from_tick=7,
                    to_tick=7,
                    room="ADMIN",
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-5",
                    from_tick=7,
                    to_tick=7,
                    room="MEDBAY",
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert WEAK_REASON_NARROW_WINDOW in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_weak_classification_is_deterministic(self) -> None:
        # Re-running the pure detector yields byte-identical flags,
        # marker included -- the replay-determinism contract.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-5",
                    subject="p-5",
                    from_tick=100,
                    to_tick=200,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-5",
                    tick=150,
                    room="EAST_HALL",
                ),
            )
        )
        first = detect_contradictions(transcript)
        second = detect_contradictions(transcript)

        assert first == second
        assert [f.model_dump_json() for f in first] == [
            f.model_dump_json() for f in second
        ]

    def test_predicate_is_marker_gated_for_both_kinds(self) -> None:
        # Task 10.1: is_weak_contradiction is marker-gated only -- the
        # conflict path now writes the marker too (the 9.7 kind gate is
        # gone), so a marked alibi_conflict IS weak and a marker-free
        # flag of either kind stays strong.
        marked_conflict = ContradictionRef(
            contradiction_id="contra:alibi_conflict:a|b",
            kind="alibi_conflict",
            event_a_id="a",
            event_b_id="b",
            subjects=("p-5",),
            description=f"x {WEAK_CONTRADICTION_MARKER_PREFIX}{WEAK_REASON_SELF_PAIR}]",
        )
        unmarked_sighting = ContradictionRef(
            contradiction_id="contra:alibi_vs_sighting:a|b",
            kind="alibi_vs_sighting",
            event_a_id="a",
            event_b_id="b",
            subjects=("p-5",),
            description="no marker here",
        )
        unmarked_conflict = ContradictionRef(
            contradiction_id="contra:alibi_conflict:c|d",
            kind="alibi_conflict",
            event_a_id="c",
            event_b_id="d",
            subjects=("p-5",),
            description="no marker here either",
        )

        assert is_weak_contradiction(marked_conflict) is True
        assert is_weak_contradiction(unmarked_sighting) is False
        assert is_weak_contradiction(unmarked_conflict) is False


# --- Task 10.1: room canonicalization (audit gp-2 C-C-1) --------------------


class TestCanonicalRooms:
    """`canonical_rooms` is the single normalisation point for room labels.

    Every variant below is from the committed replay sets' observed
    inventory -- the canonicaliser is grounded in what qwen3.5:9b
    actually emits, not a guessed grammar.
    """

    def test_plain_label_is_a_singleton_set(self) -> None:
        assert canonical_rooms("CAFETERIA") == frozenset({"CAFETERIA"})

    def test_case_variants_fold_to_upper(self) -> None:
        # Observed: 'CAFEteria' and 'cafeteria' string-mismatched
        # 'CAFETERIA' and minted artifact flags.
        assert canonical_rooms("CAFEteria") == frozenset({"CAFETERIA"})
        assert canonical_rooms("cafeteria") == frozenset({"CAFETERIA"})

    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("LABS/MEDBAY", {"LABS", "MEDBAY"}),
            ("STORAGE/ENGINEERING/EAST_HALL", {"STORAGE", "ENGINEERING", "EAST_HALL"}),
            ("WEST_HALL|LABS", {"WEST_HALL", "LABS"}),
            ("ENGINEERING-EAST_HALL_TRANSITION", {"ENGINEERING", "EAST_HALL"}),
            ("EAST_HALL_AND_ADMIN_TRANSITION", {"EAST_HALL", "ADMIN"}),
            ("ADMIN/WEST_HALL_TRANSITION", {"ADMIN", "WEST_HALL"}),
        ],
    )
    def test_compound_labels_split_into_member_rooms(
        self, label: str, expected: set[str]
    ) -> None:
        # The committed sets' compound inventory: "/", "|", "-", "_AND_"
        # joiners and the trailing "_TRANSITION" transit token. "_" alone
        # never splits (canonical ids are UPPERCASE_SNAKE: EAST_HALL).
        assert canonical_rooms(label) == frozenset(expected)

    @pytest.mark.parametrize("label", sorted(PLACEHOLDER_ROOM_LABELS))
    def test_placeholders_canonicalise_to_no_room(self, label: str) -> None:
        assert canonical_rooms(label) == frozenset()
        assert canonical_rooms(label.lower()) == frozenset()

    def test_placeholder_member_is_dropped_from_a_compound(self) -> None:
        assert canonical_rooms("CAFETERIA/UNKNOWN") == frozenset({"CAFETERIA"})

    def test_underscore_rooms_never_split(self) -> None:
        assert canonical_rooms("EAST_HALL") == frozenset({"EAST_HALL"})


class TestCanonicalRoomComparison:
    """The detector compares canonical room sets, not raw strings."""

    def test_containment_sighting_is_consistent_not_a_flag(self) -> None:
        # The seed-9 m1 archetype: a truthful compound alibi
        # ("LABS/MEDBAY") paired against sightings inside its member
        # rooms minted 19 artifact flags; under canonical comparison the
        # sighting room is a MEMBER of the alibi set -- a confirmation.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="LABS/MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-5", subject="p-8", tick=4, room="MEDBAY"
                ),
                _sighting_turn(
                    turn_index=2, speaker="p-9", subject="p-8", tick=5, room="LABS"
                ),
            )
        )
        assert detect_contradictions(transcript) == ()

    def test_case_variant_same_room_is_consistent(self) -> None:
        # Observed seed-26 m0 shape: 'CAFETERIA' alibi vs 'CAFEteria'
        # sighting string-mismatched into an artifact flag.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=0,
                    to_tick=5,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-2", subject="p-9", tick=5, room="CAFEteria"
                ),
            )
        )
        assert detect_contradictions(transcript) == ()

    def test_placeholder_alibi_mints_no_sighting_flag(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-6",
                    subject="p-6",
                    from_tick=0,
                    to_tick=18,
                    room="VARIABLE",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-6",
                    tick=9,
                    room="ENGINEERING",
                ),
            )
        )
        assert detect_contradictions(transcript) == ()

    def test_placeholder_alibi_mints_no_conflict_flag(self) -> None:
        # The seed-13 m2 shape: a counter-alibi overlapping a "VARIOUS"
        # self-alibi minted the strong conflict that ejected the accuser.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=0,
                    to_tick=14,
                    room="VARIOUS",
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-1",
                    subject="p-9",
                    from_tick=13,
                    to_tick=14,
                    room="ENGINEERING",
                ),
            )
        )
        assert detect_contradictions(transcript) == ()

    def test_intersecting_compound_alibis_do_not_conflict(self) -> None:
        # Two multi-room accounts sharing a member room can both be true
        # (the subject was in the shared room over the overlap).
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-3",
                    subject="p-3",
                    from_tick=0,
                    to_tick=10,
                    room="LABS/MEDBAY",
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-3",
                    from_tick=5,
                    to_tick=8,
                    room="MEDBAY",
                ),
            )
        )
        assert detect_contradictions(transcript) == ()

    def test_disjoint_compound_labels_still_flag(self) -> None:
        # Canonicalization is not a blanket mute: disjoint sets over an
        # in-window tick remain a real mismatch.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-3",
                    from_tick=0,
                    to_tick=10,
                    room="LABS/MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-3",
                    tick=5,
                    room="STORAGE/ENGINEERING",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].kind == "alibi_vs_sighting"
        assert is_weak_contradiction(flags[0]) is False


# --- Task 10.1: endpoint-tick weak band (audit gp-2 C-C-1) ------------------


class TestEndpointTickWeakBand:
    """An endpoint-tick-only mismatch is weak-banded, never excluded.

    Preference per the task contract: an endpoint mismatch can still be
    a real signal under corroboration, so the flag stays in the recorded
    set and belief Rule 2 applies the graduated delta.
    """

    def test_sighting_on_window_end_tick_is_weak(self) -> None:
        # Other-stated + wide window: pre-10.1 this was a STRONG flag;
        # the only weak reason is the endpoint tick.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-3",
                    from_tick=100,
                    to_tick=200,
                    room="STORAGE",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-3",
                    tick=200,
                    room="CAFETERIA",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert WEAK_REASON_ENDPOINT_TICK in flags[0].description
        assert WEAK_REASON_SELF_STATED not in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_sighting_on_window_start_tick_is_weak(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-3",
                    from_tick=100,
                    to_tick=200,
                    room="STORAGE",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-3",
                    tick=100,
                    room="CAFETERIA",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert is_weak_contradiction(flags[0]) is True

    def test_interior_sighting_stays_strong(self) -> None:
        # The genuine CANON_INTERIOR channel: an in-window, non-edge
        # sighting against a third-party alibi keeps full weight.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-3",
                    from_tick=100,
                    to_tick=200,
                    room="STORAGE",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-3",
                    tick=150,
                    room="CAFETERIA",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flags[0].description
        assert is_weak_contradiction(flags[0]) is False


# --- Task 10.1: alibi_conflict weak classification (audit gp-2 C-C-2) -------


class TestAlibiConflictWeakClassification:
    """`_detect_alibi_conflicts` now applies the 9.7 weak classification.

    Pre-10.1 the conflict path never called the weak helpers: a
    self-stated movement pair carried the full +0.3 while a single
    self-stated alibi carried 0.08 -- the rationale applies a fortiori.
    """

    def _conflict_turns(
        self,
        *,
        left_speaker: str,
        right_speaker: str,
        subject: str,
        left_range: tuple[int, int] = (0, 6),
        right_range: tuple[int, int] = (4, 9),
        accusations: tuple[tuple[int, str, str], ...] = (),
    ) -> MeetingTranscript:
        """Two conflicting alibis plus optional accusation claims.

        ``accusations`` entries are ``(turn_index, speaker, against)``
        appended as extra turns so the adversarial relation can be staged.
        """

        turns = [
            _alibi_turn(
                turn_index=0,
                speaker=left_speaker,
                subject=subject,
                from_tick=left_range[0],
                to_tick=left_range[1],
                room="CAFETERIA",
            ),
            _alibi_turn(
                turn_index=1,
                speaker=right_speaker,
                subject=subject,
                from_tick=right_range[0],
                to_tick=right_range[1],
                room="STORAGE",
            ),
        ]
        for turn_index, speaker, against in accusations:
            turns.append(
                _turn(
                    turn_index=turn_index,
                    speaker=speaker,
                    turn_kind="opt_in",
                    accuses=against,
                )
            )
        return MeetingTranscript(turns=tuple(turns))

    def test_self_pair_is_weak(self) -> None:
        # The seed-11 m2 / seed-17 m0 shape: both claims are the
        # subject's own statements.
        flags = detect_contradictions(
            self._conflict_turns(left_speaker="p-1", right_speaker="p-1", subject="p-1")
        )
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert WEAK_REASON_SELF_PAIR in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_accuser_stated_counter_alibi_is_capped_weak(self) -> None:
        # The seed-13 m2 deflection: the accused (p-1) states a
        # counter-alibi about their accuser (p-9); adversarial testimony
        # caps at weak in BOTH directions of the accusation edge.
        flags = detect_contradictions(
            self._conflict_turns(
                left_speaker="p-9",
                right_speaker="p-1",
                subject="p-9",
                accusations=((2, "p-9", "p-1"),),
            )
        )
        assert len(flags) == 1
        assert WEAK_REASON_ADVERSARIAL in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_accusers_own_alibi_about_their_target_is_capped_weak(self) -> None:
        # The other direction: the accuser states the conflicting alibi
        # about the player they accused.
        flags = detect_contradictions(
            self._conflict_turns(
                left_speaker="p-9",
                right_speaker="p-1",
                subject="p-9",
                accusations=((2, "p-1", "p-9"),),
            )
        )
        assert len(flags) == 1
        assert WEAK_REASON_ADVERSARIAL in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_boundary_tick_only_overlap_is_weak(self) -> None:
        # "CAFETERIA t0-6" + "STORAGE t6-9": the windows share only the
        # junction tick where one ends and the other begins -- a movement
        # pair, weak-banded like the vs-sighting endpoint fuzz.
        flags = detect_contradictions(
            self._conflict_turns(
                left_speaker="p-1",
                right_speaker="p-2",
                subject="p-3",
                left_range=(0, 6),
                right_range=(6, 9),
            )
        )
        assert len(flags) == 1
        assert WEAK_REASON_BOUNDARY_OVERLAP in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_independent_third_party_conflict_stays_strong(self) -> None:
        # The genuine CONFLICT_REAL shape: two independent non-subject
        # speakers, wide windows, multi-tick interior overlap -- killing
        # artifacts must not kill detection.
        flags = detect_contradictions(
            self._conflict_turns(left_speaker="p-1", right_speaker="p-2", subject="p-3")
        )
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flags[0].description
        assert is_weak_contradiction(flags[0]) is False

    def test_subject_vs_independent_witness_conflict_stays_strong(self) -> None:
        # One side self-stated is NOT a self-pair: the subject's claim
        # against an independent witness's account keeps full weight.
        flags = detect_contradictions(
            self._conflict_turns(left_speaker="p-3", right_speaker="p-2", subject="p-3")
        )
        assert len(flags) == 1
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flags[0].description
        assert is_weak_contradiction(flags[0]) is False


# --- Task 10.1: defense-echo dedup (audit gp-2 C-C-2) -----------------------


class TestDefenseEchoDedup:
    """An exact alibi restatement dedupes to the original claim."""

    def test_defender_echo_mints_no_extra_flags(self) -> None:
        # The seed-26 m1 / seed-28 m1 shape: a defender restates the
        # accused's own alibi verbatim. Pre-10.1 the echo was other-stated
        # and its sighting pairings minted STRONG flags against the player
        # being defended; now the echo dedupes to the original (self-stated)
        # claim and only the original's weak flag remains.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=2,
                    to_tick=18,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-1",
                    subject="p-9",
                    tick=10,
                    room="WEST_HALL",
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-7",
                    subject="p-9",
                    from_tick=2,
                    to_tick=18,
                    room="MEDBAY",
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        assert flags[0].event_a_id == "turn:m-1:turn-0:claim:0"
        assert WEAK_REASON_SELF_STATED in flags[0].description
        assert is_weak_contradiction(flags[0]) is True

    def test_echo_matches_on_canonical_rooms(self) -> None:
        # The echo predicate uses the canonical parse, so a case-variant
        # restatement still dedupes.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=2,
                    to_tick=18,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-1",
                    subject="p-9",
                    tick=10,
                    room="WEST_HALL",
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-7",
                    subject="p-9",
                    from_tick=2,
                    to_tick=18,
                    room="medbay",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].event_a_id == "turn:m-1:turn-0:claim:0"

    def test_changed_window_is_not_an_echo(self) -> None:
        # A restatement that changes the window asserts new information
        # and pairs normally (two flags: one per claim).
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=2,
                    to_tick=18,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-1",
                    subject="p-9",
                    tick=10,
                    room="WEST_HALL",
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-7",
                    subject="p-9",
                    from_tick=5,
                    to_tick=18,
                    room="MEDBAY",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 2

    def test_self_restatement_after_accusation_dedupes(self) -> None:
        # The subject re-asserting their own alibi (a defensive reply)
        # is the same account, not a second claim to pair against.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=2,
                    to_tick=18,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-1",
                    subject="p-9",
                    tick=10,
                    room="WEST_HALL",
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=2,
                    to_tick=18,
                    room="MEDBAY",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1


# --- Task 10.1: detector-derived corroboration (audit gp-2 C-C-1) -----------


class TestDetectCorroborations:
    """Containment-consistent (alibi, sighting) pairs feed Rule 3."""

    def _containment_transcript(self) -> MeetingTranscript:
        return MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="LABS/MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-5", subject="p-8", tick=4, room="MEDBAY"
                ),
            )
        )

    def test_third_party_sighting_inside_alibi_corroborates(self) -> None:
        corroborations = detect_corroborations(self._containment_transcript())

        assert corroborations == (
            DetectedCorroboration(
                subject="p-8",
                alibi_event_id="turn:m-1:turn-0:claim:0",
                sighting_event_id="turn:m-1:turn-1:obs:0",
            ),
        )

    def test_corroborated_pair_is_not_also_a_contradiction(self) -> None:
        # The same pair feeds exactly one path: consistency feeds Rule 3,
        # never a flag.
        transcript = self._containment_transcript()
        assert detect_contradictions(transcript) == ()
        assert len(detect_corroborations(transcript)) == 1

    def test_alibi_speakers_own_sighting_is_not_independent(self) -> None:
        # One witness restating their account in two formats (an alibi
        # claim + a saw_player observation) is one voice, not a vouch.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-5",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-5", subject="p-8", tick=4, room="MEDBAY"
                ),
            )
        )
        assert detect_corroborations(transcript) == ()

    def test_subjects_own_sighting_does_not_corroborate_their_alibi(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-8", subject="p-8", tick=4, room="MEDBAY"
                ),
            )
        )
        assert detect_corroborations(transcript) == ()

    def test_placeholder_alibi_corroborates_nothing(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="VARIOUS",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-5", subject="p-8", tick=4, room="MEDBAY"
                ),
            )
        )
        assert detect_corroborations(transcript) == ()

    def test_out_of_window_sighting_does_not_corroborate(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-5", subject="p-8", tick=9, room="MEDBAY"
                ),
            )
        )
        assert detect_corroborations(transcript) == ()

    def test_subject_echo_of_witness_vouch_still_corroborates(self) -> None:
        # The witness-vouches-first shape: p-5 states p-8's alibi AND the
        # matching sighting; p-8 restates the same alibi later. The echo
        # dedup is contradiction-side only -- here p-8's self-stated
        # version is exactly the account p-5's sighting independently
        # confirms (sighting speaker != subject != claim speaker), while
        # p-5's sighting against p-5's OWN claim stays gated as one
        # voice. Deduping the echo to p-5's first statement would orphan
        # the sighting and silently drop a genuine Rule-3 signal.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-5",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-5", subject="p-8", tick=4, room="MEDBAY"
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="MEDBAY",
                ),
            )
        )
        corroborations = detect_corroborations(transcript)

        # Exactly one pair: the subject's own (echoed) claim x the
        # witness's sighting; the witness's claim x their own sighting
        # is still rejected by the independence gate.
        assert corroborations == (
            DetectedCorroboration(
                subject="p-8",
                alibi_event_id="turn:m-1:turn-2:claim:0",
                sighting_event_id="turn:m-1:turn-1:obs:0",
            ),
        )
        # And the same echo still mints no contradiction flag.
        assert detect_contradictions(transcript) == ()

    def test_roster_filters_subjects(self) -> None:
        corroborations = detect_corroborations(
            self._containment_transcript(), roster=frozenset({"p-1", "p-5"})
        )
        assert corroborations == ()

    def test_deterministic_and_sorted(self) -> None:
        transcript = self._containment_transcript()
        first = detect_corroborations(transcript)
        second = detect_corroborations(transcript)
        assert first == second
        assert list(first) == sorted(
            first, key=lambda c: (c.subject, c.alibi_event_id, c.sighting_event_id)
        )


# --- Task 10.1: the belief-lift dedup key -----------------------------------


class TestContradictionLiftKey:
    def test_vs_sighting_key_is_the_alibi_claim_id(self) -> None:
        # Every sighting paired against one alibi claim shares the key --
        # the seed-9 fountain collapses to one lift group.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-3",
                    from_tick=100,
                    to_tick=200,
                    room="STORAGE",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-3",
                    tick=150,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=2, speaker="p-5", subject="p-3", tick=160, room="ADMIN"
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 2
        keys = {contradiction_lift_key(flag) for flag in flags}
        assert keys == {"turn:m-1:turn-0:claim:0"}

    def test_conflict_key_is_the_claim_pair(self) -> None:
        flags = detect_contradictions(
            MeetingTranscript(
                turns=(
                    _alibi_turn(
                        turn_index=0,
                        speaker="p-1",
                        subject="p-3",
                        from_tick=0,
                        to_tick=9,
                        room="STORAGE",
                    ),
                    _alibi_turn(
                        turn_index=1,
                        speaker="p-2",
                        subject="p-3",
                        from_tick=4,
                        to_tick=9,
                        room="CAFETERIA",
                    ),
                )
            )
        )
        assert len(flags) == 1
        assert contradiction_lift_key(flags[0]) == (
            "turn:m-1:turn-0:claim:0|turn:m-1:turn-1:claim:0"
        )

    def test_foreign_event_ids_fall_back_to_the_pair(self) -> None:
        # A flag built outside the detector (no ":claim:" segment) keys
        # on its own event pair -- one key per flag, the pre-10.1 shape.
        flag = ContradictionRef(
            contradiction_id="contra:alibi_vs_sighting:a|b",
            kind="alibi_vs_sighting",
            event_a_id="a",
            event_b_id="b",
            subjects=("p-5",),
            description="hand-built",
        )
        assert contradiction_lift_key(flag) == "a|b"


# --- Task 10.1 acceptance pins against the committed replay bytes -----------
#
# Offline reconstructions per the task contract: the committed
# replays/samples/9p2i set does NOT change until the 10.5 re-record, so every
# pin below re-derives the repaired detector's output from the RECORDED
# transcripts (the audit-extractor walk: read the meeting rows, re-run the
# pure detector) and compares against the RECORDED flag set the old detector
# wrote. Audit anchor: audit-2026-06-10-1820-gameplay-data.md gp-2
# (C-C-1, C-C-2, C-C-3, D-D-3).

from pathlib import Path  # noqa: E402

from meetings.transcript import (  # noqa: E402
    _dedupe_echo_alibis,  # noqa: PLC2701
    _iter_alibis,  # noqa: PLC2701
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries  # noqa: E402

_COMMITTED_9P2I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)


def _committed_meetings(seed: int) -> list[MeetingReplayEntry]:
    path = _COMMITTED_9P2I_DIR / f"replay-seed-{seed}.jsonl"
    return [
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, MeetingReplayEntry)
    ]


def _living_roster(entry: MeetingReplayEntry) -> frozenset[str]:
    # Every recorded ballot was cast by a living participant (audit
    # self-check), so the ballot voters ARE the roster the meeting ran
    # with -- the same roster the recording-time detector received.
    return frozenset(ballot.voter for ballot in entry.ballots)


def _rederive(entry: MeetingReplayEntry) -> tuple[ContradictionRef, ...]:
    return detect_contradictions(entry.transcript, roster=_living_roster(entry))


def _alibi_rooms_by_event_id(entry: MeetingReplayEntry) -> dict[str, frozenset[str]]:
    """Canonical room set per alibi-claim event id, detector-id format."""

    return {
        f"turn:{turn.turn_id}:claim:{index}": canonical_rooms(claim.room)
        for turn in entry.transcript.turns
        for index, claim in enumerate(turn.claims)
        if isinstance(claim, AlibiClaim)
    }


def _sighting_rooms_by_event_id(
    entry: MeetingReplayEntry,
) -> dict[str, frozenset[str]]:
    return {
        f"turn:{turn.turn_id}:obs:{index}": canonical_rooms(observation.room)
        for turn in entry.transcript.turns
        for index, observation in enumerate(turn.observations)
        if isinstance(observation, SawPlayerObservation)
    }


def _classify_removed_flag(
    entry: MeetingReplayEntry, flag: ContradictionRef
) -> set[str]:
    """Which Task 10.1 artifact classes explain a no-longer-emitted flag.

    Resolves the flag's event ids back into the recorded claims and
    classifies with the production ``canonical_rooms`` -- the audited
    artifact taxonomy (gp-2): ``placeholder`` (a side canonicalises to no
    room), ``containment`` (the canonical sets intersect -- a
    confirmation, not a contradiction), ``echo`` (the flag rode an alibi
    restatement now deduped to the original claim).
    """

    alibi_rooms = _alibi_rooms_by_event_id(entry)
    sighting_rooms = _sighting_rooms_by_event_id(entry)
    sides = [
        alibi_rooms.get(event_id, sighting_rooms.get(event_id))
        for event_id in (flag.event_a_id, flag.event_b_id)
    ]
    assert sides[0] is not None and sides[1] is not None

    classes: set[str] = set()
    if not sides[0] or not sides[1]:
        classes.add("placeholder")
    elif sides[0] & sides[1]:
        classes.add("containment")
    surviving_claim_ids = {
        alibi.event_id
        for alibi in _dedupe_echo_alibis(tuple(_iter_alibis(entry.transcript)))
    }
    flag_claim_ids = {
        event_id
        for event_id in (flag.event_a_id, flag.event_b_id)
        if event_id in alibi_rooms
    }
    if flag_claim_ids - surviving_claim_ids:
        classes.add("echo")
    return classes


class TestCommittedBytesArtifactCollapse:
    """The audited artifact classes no longer reproduce (gp-2 C-C-1/C-C-2).

    The audit classified 77/83 recorded flags as artifacts; the dominant
    removable classes -- 34 compound-label containments, 11 placeholders
    (plus the echo duplicates behind the defense-echo shape) -- must not
    re-derive under the repaired detector, while everything the new
    detector still emits must be a flag the old detector also emitted
    (the repair only removes and reclassifies; it invents no pairing).
    """

    def test_rederived_flags_are_a_subset_and_removals_are_all_artifacts(
        self,
    ) -> None:
        recorded_total = 0
        removed_by_class = {"placeholder": 0, "containment": 0, "echo": 0}
        removed_total = 0
        for seed in range(50):
            for entry in _committed_meetings(seed):
                recorded_by_id = {
                    flag.contradiction_id: flag for flag in entry.contradictions
                }
                recorded_total += len(recorded_by_id)
                rederived_ids = {flag.contradiction_id for flag in _rederive(entry)}
                # No new pairings on the committed bytes: every re-derived
                # flag is one the old detector also emitted.
                assert rederived_ids <= set(recorded_by_id)
                for flag_id, flag in recorded_by_id.items():
                    classes = _classify_removed_flag(entry, flag)
                    if "placeholder" in classes or "containment" in classes:
                        # The DoD pin: a containment- or placeholder-class
                        # recorded flag cannot reproduce under the new
                        # detector.
                        assert flag_id not in rederived_ids
                    if flag_id in rederived_ids:
                        continue
                    # Nothing genuine was removed: every removal is
                    # explained by an audited artifact class.
                    assert classes, (
                        f"non-artifact flag removed: {flag.contradiction_id}"
                    )
                    removed_total += 1
                    for cls in classes:
                        removed_by_class[cls] += 1

        # The committed set carries 83 flags (audit C-1) and the repaired
        # detector removes 53 of them, every one artifact-classified. The
        # audit's facts (34 compound-label containments + 11 placeholders
        # = 45) sit INSIDE these removals: the production canonicaliser
        # also case-folds ('CAFEteria') and splits the richer joiners
        # ("|", "-", "_AND_", "_TRANSITION"), so flags the audit binned
        # as boundary/non-canonical mismatches resolve to containment
        # here too, and the 9 defense-echo rides (audit C-2's seed 26/28
        # shapes) dedup away -- 4 of them doubly classified as
        # placeholder+echo, hence 36 + 12 + 9 > 53.
        assert recorded_total == 83
        assert removed_total == 53
        assert removed_by_class["containment"] == 36
        assert removed_by_class["placeholder"] == 12
        assert removed_by_class["echo"] == 9

    def test_surviving_endpoint_flags_are_weak_banded(self) -> None:
        # The audit's 31 endpoint-fuzz flags (29 CANON_BOUNDARY + 2
        # CONFLICT_BOUNDARY_TICK_ONLY) collapse: the compound/case-variant
        # members resolve as containment and disappear, and every
        # SURVIVING edge-tick flag -- 24 across the set -- now carries
        # the weak marker (weak-banded by preference over exclusion: an
        # endpoint mismatch can still convert under corroboration).
        endpoint_weak = 0
        for seed in range(50):
            for entry in _committed_meetings(seed):
                for flag in _rederive(entry):
                    if (
                        WEAK_REASON_ENDPOINT_TICK in flag.description
                        or WEAK_REASON_BOUNDARY_OVERLAP in flag.description
                    ):
                        assert is_weak_contradiction(flag)
                        endpoint_weak += 1
        assert endpoint_weak == 24

    def test_every_surviving_flag_remains_deterministic(self) -> None:
        # Byte-identical re-derivation: running the pure detector twice
        # over every committed transcript yields identical flag tuples
        # (the §0 rule-1 precondition for the 10.5 re-record).
        for seed in range(50):
            for entry in _committed_meetings(seed):
                first = _rederive(entry)
                second = _rederive(entry)
                assert [flag.model_dump_json() for flag in first] == [
                    flag.model_dump_json() for flag in second
                ]


class TestCommittedBytesSeedPins:
    """The task contract's named acceptance seeds, pinned individually."""

    def test_seed9_m1_fountain_no_longer_reproduces(self) -> None:
        # 19 recorded flags from ONE truthful compound alibi
        # ("LABS/MEDBAY" t2-7) x repeated containment-consistent
        # sightings; the repaired detector emits none of them, and the
        # third-party sightings now corroborate p-8 instead.
        entry = _committed_meetings(9)[1]
        assert len(entry.contradictions) == 19

        assert _rederive(entry) == ()
        corroborated = {
            corroboration.subject
            for corroboration in detect_corroborations(
                entry.transcript, roster=_living_roster(entry)
            )
        }
        assert "p-8" in corroborated

    def test_seed26_m1_placeholder_and_echo_flags_no_longer_reproduce(self) -> None:
        # 8 recorded flags on innocent p-6: 4 weak off p-6's own
        # placeholder alibi ("VARIABLE") + 4 STRONG off p-2's defense
        # echo of that same alibi. Placeholder canonicalisation removes
        # the pairing entirely (the echo dedup would otherwise fold the
        # strong four into the original's weak classification).
        entry = _committed_meetings(26)[1]
        assert len(entry.contradictions) == 8
        assert all("p-6" in flag.subjects for flag in entry.contradictions)

        assert _rederive(entry) == ()

    def test_seed13_m2_adversarial_counter_alibi_no_longer_reproduces(self) -> None:
        # The accused impostor's counter-alibi about their accuser
        # overlapped the accuser's "VARIOUS" self-alibi: the placeholder
        # side mints no conflict under the repaired detector.
        entry = _committed_meetings(13)[2]
        assert len(entry.contradictions) == 1
        assert entry.contradictions[0].kind == "alibi_conflict"

        assert _rederive(entry) == ()

    @pytest.mark.parametrize("seed", [11, 17])
    def test_self_pair_conflicts_land_in_the_weak_band(self, seed: int) -> None:
        # Seeds 11 m2 / 17 m0 (audit C-2): the self-stated movement-pair
        # conflicts that ejected their own speakers re-derive as WEAK --
        # every conflict flag in these meetings carries the marker, and
        # the self-pair itself names the reason.
        meeting_index = {11: 2, 17: 0}[seed]
        entry = _committed_meetings(seed)[meeting_index]
        rederived = _rederive(entry)

        conflicts = [flag for flag in rederived if flag.kind == "alibi_conflict"]
        assert conflicts
        assert all(is_weak_contradiction(flag) for flag in conflicts)
        assert any(WEAK_REASON_SELF_PAIR in flag.description for flag in conflicts)

    @pytest.mark.parametrize(
        ("seed", "subject", "interior_tick"),
        [(3, "p-6", 10), (30, "p-3", 7), (42, "p-7", 9), (45, "p-9", 4)],
    )
    def test_genuine_canon_interior_impostor_flag_survives(
        self, seed: int, subject: str, interior_tick: int
    ) -> None:
        # THE survival pin (gp-2 acceptance: "the 4 genuine
        # CANON_INTERIOR impostor flags survive untouched"): the only
        # genuinely diagnostic flags the audited set produced -- an
        # impostor's own alibi contradicted by an interior-tick sighting
        # in a different canonical room -- re-derive BYTE-IDENTICALLY
        # (same id, same description, same weak self-stated
        # classification; recall past weak is the explicit D-D-3
        # follow-on, not this task). Killing artifacts must not kill
        # detection. ``interior_tick`` selects the audited interior
        # sighting -- seed 30 also carries an edge-tick flag on the same
        # subject, which is endpoint-banded, not this pin.
        entry = _committed_meetings(seed)[0]
        recorded = [
            flag
            for flag in entry.contradictions
            if subject in flag.subjects
            and f"at tick {interior_tick}." in flag.description
        ]
        assert len(recorded) == 1
        rederived = _rederive(entry)

        assert recorded[0] in rederived
        assert is_weak_contradiction(recorded[0])
