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
    SawVentObservation,
)
from meetings.transcript import (
    CANONICAL_ROOMS,
    NARROW_ALIBI_WINDOW_TICKS,
    SPAWN_WINDOW_LAST_TICK,
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_ADVERSARIAL,
    WEAK_REASON_BOUNDARY_OVERLAP,
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_NARROW_WINDOW,
    WEAK_REASON_PROXY_INTRA_TURN,
    WEAK_REASON_RETARGETED_PROXY,
    WEAK_REASON_SELF_PAIR,
    WEAK_REASON_SELF_STATED,
    DetectedCorroboration,
    accusation_target,
    canonical_rooms,
    contradiction_lift_key,
    detect_contradictions,
    detect_corroborations,
    is_canonically_ordered,
    is_relevant_sighting,
    is_weak_contradiction,
    next_chain_step,
    sort_turns_canonically,
    triggering_body_rooms,
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

    Task 13.14 (owner LONE-STRONG decision, 2026-06-22) REVERSES the
    self-stated down-weight for the ``alibi_vs_sighting`` band only: a
    self-stated-only sighting contradiction now classifies STRONG (see
    ``test_self_stated_alibi_vs_third_party_sighting_is_strong``). The
    genuine shaky guards -- narrow window, endpoint-tick, and the
    ``alibi_conflict`` self-pair / adversarial / boundary patterns -- STAY
    weak (real precision guards, not the self-stated down-weight).
    """

    def test_self_stated_alibi_vs_third_party_sighting_is_strong(self) -> None:
        # The seed-3 audited shape: the reporter's own alibi (CAFETERIA)
        # against a third party's sighting of them (EAST_HALL). Task 13.14
        # (owner LONE-STRONG decision, 2026-06-22; DESIGN.md §5.4 + §6.4)
        # REVERSES the audit-9.7 self-stated down-weight for the
        # alibi_vs_sighting band: a self-stated-only alibi contradicted by a
        # third party's sighting now classifies STRONG (no weak marker) and
        # drives Rule 2's full gate-crossing delta. The window is wide (100-200)
        # and the sighting interior (150), so neither the narrow nor the
        # endpoint guard fires -- the flag carries no weak marker at all.
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
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flag.description
        assert WEAK_REASON_SELF_STATED not in flag.description
        assert WEAK_REASON_NARROW_WINDOW not in flag.description
        assert is_weak_contradiction(flag) is False

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

    def test_narrow_and_endpoint_reasons_render_in_fixed_order(self) -> None:
        # A MULTI-tick narrow self-alibi (from != to, window 1 < 2) with the
        # sighting on its endpoint tick matches the narrow + endpoint vs-sighting
        # patterns; the reasons render in the fixed order narrow -> endpoint so the
        # marker is byte-stable across runs. Task 13.14 drops the self-stated reason
        # from the sighting path (the owner LONE-STRONG reversal), so the marker no
        # longer leads with self-stated; the flag STAYS weak on the surviving
        # narrow/endpoint guards. Re-anchored at baseline 6: the SINGLE-tick
        # (from == to) degenerate class now graduates to STRONG under the
        # unconditional whereabouts-interior exemption, so the marker-ordering
        # coverage moves to this multi-tick narrow case, which the exemption (scoped
        # to from == to) leaves untouched.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-5",
                    subject="p-5",
                    from_tick=7,
                    to_tick=8,
                    room="ADMIN",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-2", subject="p-5", tick=8, room="MEDBAY"
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        marker = (
            f"{WEAK_CONTRADICTION_MARKER_PREFIX}"
            f"{WEAK_REASON_NARROW_WINDOW}; {WEAK_REASON_ENDPOINT_TICK}]"
        )
        assert flags[0].description.endswith(marker)
        assert WEAK_REASON_SELF_STATED not in flags[0].description
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

    Every variant below is from the recorded replay sets' observed
    compound-label inventory -- the canonicaliser is grounded in what the
    models actually emitted, not a guessed grammar.
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

    @pytest.mark.parametrize(
        "label",
        [
            # The 10.1 denylist inventory...
            "VARIOUS",
            "VARIABLE",
            "VARYING",
            "UNKNOWN",
            "UNKNOWN_ROOM",
            # ...plus the variants that LEAKED past it (audit C-C-5): the
            # allowlist kills the class, not the observed instances.
            "VARYING_ROOMS",
            "HALLS",
            "SOMEWHERE",
        ],
    )
    def test_non_map_labels_canonicalise_to_no_room(self, label: str) -> None:
        # Task 10.6 (audit gp-1 C-C-5): membership in the frozen
        # CANONICAL_ROOMS allowlist replaces the placeholder denylist --
        # "VARYING_ROOMS" escaped the denylist and minted 25% of the
        # Wave-0 set's flag volume against one innocent. A non-map label
        # is non-spatial: no flag, no corroboration.
        assert canonical_rooms(label) == frozenset()
        assert canonical_rooms(label.lower()) == frozenset()

    def test_placeholder_member_is_dropped_from_a_compound(self) -> None:
        assert canonical_rooms("CAFETERIA/UNKNOWN") == frozenset({"CAFETERIA"})

    def test_underscore_rooms_never_split(self) -> None:
        assert canonical_rooms("EAST_HALL") == frozenset({"EAST_HALL"})

    def test_every_canonical_room_is_its_own_canonical_form(self) -> None:
        for room in CANONICAL_ROOMS:
            assert canonical_rooms(room) == frozenset({room})

    def test_allowlist_equals_the_engine_map_room_set(self) -> None:
        # The Task 10.6 review tripwire: CANONICAL_ROOMS is deliberately
        # DATA inside meetings/ (agents/ imports this module, so an
        # engine import here would breach the §1.3 firewall
        # transitively). This test is the one place the duplication is
        # reconciled -- a future map change MUST fail here and
        # re-trigger detector review, otherwise the new rooms would
        # silently canonicalise to "no room" and re-open the
        # placeholder-leak class. Tests sit outside the firewall, so the
        # engine import is legal exactly here.
        from engine.world import load_canonical_map

        assert CANONICAL_ROOMS == frozenset(load_canonical_map().rooms)


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
        # and its sighting pairings minted extra flags against the player
        # being defended; now the echo dedupes to the original (self-stated)
        # claim and only the original's flag remains. Task 13.14 promotes that
        # surviving self-stated alibi_vs_sighting to STRONG (the down-weight
        # reversal); the echo-DEDUP property this test guards -- one flag,
        # anchored to the original claim event -- is unchanged.
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
        assert WEAK_REASON_SELF_STATED not in flags[0].description
        assert is_weak_contradiction(flags[0]) is False

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


# The committed replays/samples sets were re-recorded for Task 16.14 baseline 4
# on the Qwen/Qwen3.6-27B substrate (qwen3_6_27b.v1 prompts — all four
# templates: accusation_round, crewmate_report, impostor_report, vote_ballot)
# with all SIX substrate levers ON (evidence_quality_lift, movement_perception,
# reporter_exculpation, testimony_as_content, unfreeze_memory, witnessed_kill_evidence)
# — the substrate stamped into every replay game_over. detect_contradictions is a
# pure function with no env dependency, so a bare re-derivation over the recorded
# transcripts reproduces the recorded NON-VENT census byte-for-byte. The Task 15.4
# ``vent_sighting`` kind is the one exception: it is GROUNDED against each speaker's
# typed vent-witness channel (``vent_witness_records``), which is NOT in the
# transcript, so a bare re-derivation without that channel mints no vent flag and
# the recorded vent flags are recorded-only (mirrors eval.watchability's
# vent-aware merge). Re-derivation and the recorded vent census are therefore
# disjoint; the pins below exclude ``vent_sighting`` when comparing recorded vs
# re-derived. (These tests read raw replay bytes via read_all_entries, not the
# flag-gated ReplayLoader, so they need no AILIBI_EVIDENCE_QUALITY_LIFT env.)
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


def _vent_observation_event_ids(entry: MeetingReplayEntry) -> frozenset[str]:
    """Detector-id set for every spoken :class:`SawVentObservation`.

    The Task 18.9 lever-2 (grounded vent-placement) variant of
    ``alibi_vs_physical`` pairs one of these vent observations with the subject's
    own placement, GROUNDED against the speaker's typed vent-witness channel --
    which is not in the transcript. A bare re-derivation (no vent channel) never
    mints it, exactly like the Task 15.4 ``vent_sighting`` kind, so those recorded
    flags are recorded-only and excluded from the re-derivation-exactness pin.
    """

    return frozenset(
        f"turn:{turn.turn_id}:obs:{index}"
        for turn in entry.transcript.turns
        for index, observation in enumerate(turn.observations)
        if isinstance(observation, SawVentObservation)
    )


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


def _is_promoted_self_stated_divergence(
    recorded: ContradictionRef | None, rederived: ContradictionRef | None
) -> bool:
    """Whether ``recorded`` -> ``rederived`` is the Task 13.14 self-stated drop.

    The 13.14 reversal removes ``WEAK_REASON_SELF_STATED`` from the
    ``alibi_vs_sighting`` marker writer, so a committed (pre-13.14) weak
    self-stated flag re-derives as the SAME flag -- identical contradiction id,
    kind, subjects, and event-id pair -- with only the self-stated reason gone
    (the interior/wide subset thereby crossing into the STRONG band). This
    recogniser lets the artifact-collapse pin treat that reclassification as
    the EXPECTED $0-re-extraction divergence, distinct from the placeholder /
    proxy-retarget repairs.
    """

    return (
        recorded is not None
        and rederived is not None
        and recorded.kind == "alibi_vs_sighting"
        and WEAK_REASON_SELF_STATED in recorded.description
        and WEAK_REASON_SELF_STATED not in rederived.description
        and recorded.subjects == rederived.subjects
        and recorded.event_a_id == rederived.event_a_id
        and recorded.event_b_id == rederived.event_b_id
    )


class TestCommittedBytesArtifactCollapse:
    """Re-derivation reproduces the recorded bytes EXACTLY (no offline divergence).

    At 10.1 merge time this class proved the artifact collapse against the
    e750b40 era bytes; at 10.5 it pinned exactness; at W1 the only surviving
    divergence was the Task 10.10 guard the W1 bytes predated. The Task 10.17
    W2 re-record was recorded with the FULL repaired detector — the 10.6
    allowlist/proxy rules AND the 10.10 same-speaker guard all ran at record
    time — so the committed bytes already carry every repair and the pin is
    once again pure exactness: re-derivation reproduces every recorded
    transcript-derivable flag byte-for-byte, with no removed and no added sites.

    Task 16.14 baseline 4: the recorded set carries the grounded Task 15.4
    ``vent_sighting`` kind, which is GROUNDED against each speaker's typed
    vent-witness channel rather than the transcript, so a bare re-derivation never
    mints it. Task 18.12 baseline 6: the graduated lever-2 adds the GROUNDED
    vent-placement variant of ``alibi_vs_physical`` (9 flags), grounded the same
    way. Both grounded kinds are excluded from the recorded side of the exactness
    comparison below (re-derivation and the recorded vent census are disjoint);
    the transcript-derivable flags -- including the 6 INFERENTIAL co-presence
    ``alibi_vs_physical`` flags -- still re-derive byte-for-byte.

    The structural guards stay armed: any removal must still be explained by a
    repair (placeholder kill or a proxy re-target) and any addition must still
    be a weak proxy re-target — so a future detector drift away from the
    committed bytes fails here exactly as before, even though on baseline 4 both
    lists are empty.
    """

    # (seed, meeting_index) -> recorded flags that no longer re-derive.
    # At W0/W1 this class proved detector repairs (10.6, then 10.10) as an
    # OFFLINE divergence from pre-repair recorded flags. The Task 10.17 W2
    # re-record runs every repair at RECORD time (10.6 allowlist/proxy + the
    # 10.10 same-speaker guard), so there is NO offline divergence left: every
    # recorded flag re-derives byte-identically and removed_sites is empty.
    _REPAIRED_SITES: dict[tuple[int, int], int] = {}

    def test_rederivation_diverges_only_at_the_repaired_sites(self) -> None:
        recorded_total = 0
        rederived_total = 0
        removed_sites: dict[tuple[int, int], int] = {}
        # Task 13.14: the self-stated down-weight is removed for the
        # alibi_vs_sighting band. On the Task 16.14 baseline-4 re-record
        # the bytes are RECORDED under 13.14, so the recorded flags already carry
        # the post-13.14 classification and re-derivation no longer drops a marker
        # -- 0 promoted divergences (vs 110 when the pre-13.14 bytes re-derived).
        # These are counted + pinned separately from the placeholder /
        # proxy-retarget repairs the original guard tracks.
        promoted_divergences = 0
        promoted_to_strong = 0
        for seed in range(50):
            for index, entry in enumerate(_committed_meetings(seed)):
                # ``vent_sighting`` (Task 15.4) AND the Task 18.9 lever-2 GROUNDED
                # vent-placement variant of ``alibi_vs_physical`` are both grounded
                # against each speaker's typed vent-witness channel, which is not in
                # the transcript, so a bare re-derivation never mints them -- the
                # recorded vent flags are recorded-only and disjoint from the
                # re-derived set (mirrors eval.watchability's vent-aware merge).
                # The re-derivation-exactness pin is over the transcript-derivable
                # kinds, so both are excluded from the recorded side here. A
                # grounded vent-placement flag is one referencing a spoken
                # SawVentObservation (the INFERENTIAL alibi_vs_physical -- a plain
                # co-presence contradiction -- has no vent-observation side and
                # re-derives normally).
                vent_obs_ids = _vent_observation_event_ids(entry)
                recorded_by_id = {
                    flag.contradiction_id: flag
                    for flag in entry.contradictions
                    if flag.kind != "vent_sighting"
                    and not (
                        flag.kind == "alibi_vs_physical"
                        and (
                            flag.event_a_id in vent_obs_ids
                            or flag.event_b_id in vent_obs_ids
                        )
                    )
                }
                rederived_by_id = {
                    flag.contradiction_id: flag for flag in _rederive(entry)
                }
                recorded_total += len(recorded_by_id)
                rederived_total += len(rederived_by_id)
                removed = []
                for flag_id, flag in recorded_by_id.items():
                    rederived = rederived_by_id.get(flag_id)
                    if rederived == flag:
                        continue
                    if rederived is not None and _is_promoted_self_stated_divergence(
                        flag, rederived
                    ):
                        promoted_divergences += 1
                        if not is_weak_contradiction(rederived):
                            promoted_to_strong += 1
                        continue
                    removed.append(flag)
                added = [
                    flag
                    for flag_id, flag in rederived_by_id.items()
                    if recorded_by_id.get(flag_id) != flag
                    and not _is_promoted_self_stated_divergence(
                        recorded_by_id.get(flag_id), flag
                    )
                ]
                if removed:
                    removed_sites[(seed, index)] = len(removed)
                for flag in removed:
                    # Each non-13.14 removal must be explained by a repair: a
                    # 10.6 placeholder-variant side (the allowlist kill) or a
                    # flag whose re-target now exists in the re-derived set under
                    # the same event-id pair -- the 10.6 cross-speaker proxy
                    # alibi or the 10.10 same-speaker proxy-intra-turn guard.
                    classes = _classify_removed_flag(entry, flag)
                    retargeted = flag.contradiction_id in rederived_by_id and any(
                        reason in rederived_by_id[flag.contradiction_id].description
                        for reason in (
                            WEAK_REASON_RETARGETED_PROXY,
                            WEAK_REASON_PROXY_INTRA_TURN,
                        )
                    )
                    assert "placeholder" in classes or retargeted, flag.contradiction_id
                for flag in added:
                    # The only NEW pairings a repair may mint are the weak
                    # re-targets at the proxy speaker (10.6 cross-speaker, 10.10
                    # same-speaker).
                    assert (
                        WEAK_REASON_RETARGETED_PROXY in flag.description
                        or WEAK_REASON_PROXY_INTRA_TURN in flag.description
                    ), flag.contradiction_id
                    assert is_weak_contradiction(flag)

        # The placeholder / proxy-retarget repair divergence stays empty (the
        # committed bytes already carry those repairs).
        assert removed_sites == self._REPAIRED_SITES
        # Re-derivation preserves the transcript-derivable flag COUNT (none added
        # or removed) on the Task 18.12 baseline-6 bytes -- the recorded grounded
        # ``vent_sighting`` and grounded vent-placement ``alibi_vs_physical`` flags
        # are excluded above, as re-derivation without the vent channel cannot mint
        # them; every remaining transcript-derivable flag re-derives byte-for-byte.
        assert recorded_total == rederived_total
        # Task 16.14 baseline-4: the bytes are RECORDED under 13.14, so
        # the self-stated down-weight is already baked into every recorded
        # alibi_vs_sighting flag. Re-derivation is BYTE-IDENTICAL (0 promoted
        # divergences, vs 110 when the pre-13.14 bytes re-derived with the marker
        # dropped) — the post-substrate determinism property; the strong promotions
        # now live in the recorded bytes, not minted at re-extraction.
        assert promoted_divergences == 0
        assert promoted_to_strong == 0

    def test_surviving_endpoint_flags_are_weak_banded(self) -> None:
        # The endpoint class survives ONLY weak-banded (the 10.1 decision:
        # weak-banded by preference over exclusion — an endpoint mismatch
        # can still convert under corroboration). The invariant is that every
        # endpoint-reason flag carries the weak marker (asserted in-loop); the
        # count is 26 on the Task 18.12 baseline-6 re-record (the CREW-ONLY
        # graduation slate) — the re-derived alibi_vs_sighting surface is 76 flags
        # total on this substrate, of which 26 sit in the endpoint/boundary weak
        # band; the remainder are interior (strong, or narrow/self-banded), not
        # endpoint-banded.
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
        assert endpoint_weak == 26

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
    """Named acceptance pins, re-pointed at the Task 10.5 honest baseline.

    The 10.1-era pins named the e750b40 defect coordinates (the seed-9
    fountain, the seed-26 placeholder/echo stack, the seed-13 adversarial
    counter-alibi, the seed-11/17 self-pairs); those inputs no longer exist
    in the tree — the proofs live in git history at the 10.1 merge. The
    live successors pin (a) the artifact INPUT classes still occurring in
    the new bytes minting nothing, (b) every recorded conflict flag sitting
    in the weak band, and (c) the genuine-class supply at its recorded
    coordinates.
    """

    def test_artifact_input_classes_still_occur_and_mint_nothing(self) -> None:
        # The W0-era artifact INPUT classes (non-spatial "placeholder" rooms and
        # multi-room "compound" labels) that the placeholder/artifact flags rode.
        # On the Task 18.12 baseline-6 re-record (the CREW-ONLY graduation slate)
        # BOTH classes stay at ZERO: the substrate emits no split-room compound
        # claim label and no non-spatial placeholder claim room. The census guards
        # that neither artifact input class re-appears; the "mints nothing"
        # in-loop assert (no recorded or re-derived contradiction references a
        # placeholder turn) holds vacuously on this record, the placeholder set
        # being empty.
        compound_claim_rooms = 0
        placeholder_claim_rooms = 0
        placeholder_turn_ids: set[str] = set()
        for seed in range(50):
            for entry in _committed_meetings(seed):
                for turn in entry.transcript.turns:
                    for claim in turn.claims:
                        room = getattr(claim, "room", None)
                        if not room:
                            continue
                        canon = canonical_rooms(room)
                        if len(canon) > 1:
                            compound_claim_rooms += 1
                        elif not canon:
                            placeholder_claim_rooms += 1
                            placeholder_turn_ids.add(turn.turn_id)
                # A placeholder side mints nothing: no flag (recorded or re-derived)
                # references the turn that carried the non-spatial claim.
                for flag in (*entry.contradictions, *_rederive(entry)):
                    assert not any(
                        tid in flag.contradiction_id for tid in placeholder_turn_ids
                    )
        assert compound_claim_rooms == 0
        assert placeholder_claim_rooms == 0

    def test_recorded_conflict_flag_census(self) -> None:
        # On the Task 18.12 baseline-6 re-record (the CREW-ONLY graduation slate)
        # the alibi_conflict surface carries exactly EIGHT recorded flags, ALL
        # WEAK — so the band is non-empty but carries ZERO strong. The baseline-1
        # lone-STRONG cross-speaker deception conflict remains GONE. The
        # STRONG-conflict tripwire stays armed (rule 3): if a future re-record
        # surfaces a STRONG conflict here, that is a new deception-surface signal
        # to review.
        conflict_sites: list[tuple[int, int, tuple[str, ...]]] = []
        strong_sites: list[tuple[int, int, tuple[str, ...]]] = []
        for seed in range(50):
            for index, entry in enumerate(_committed_meetings(seed)):
                for flag in entry.contradictions:
                    if flag.kind != "alibi_conflict":
                        continue
                    conflict_sites.append((seed, index, flag.subjects))
                    if not is_weak_contradiction(flag):
                        strong_sites.append((seed, index, flag.subjects))
        assert len(conflict_sites) == 8
        assert sorted(strong_sites) == []

    @pytest.mark.parametrize(
        ("meeting_index", "seed", "subject", "interior_tick"),
        [
            (0, 42, "p-4", 10),
        ],
    )
    def test_genuine_canon_interior_impostor_flag_survives(
        self, meeting_index: int, seed: int, subject: str, interior_tick: int
    ) -> None:
        # THE survival pin (10.4's definition: alibi_vs_sighting WITHOUT the
        # endpoint band, an in-window interior-tick contradiction). The
        # interior_tick sits strictly INSIDE the alibi window (never a
        # from_tick/to_tick boundary), so the flag carries neither the
        # endpoint-tick nor the boundary-overlap weak reason — the test asserts
        # that explicitly, so it cannot drift onto an endpoint-band flag (a
        # different class, covered by test_surviving_endpoint_flags_are_weak_banded)
        # while the real interior genuine supply disappears.
        #
        # INTENT-PRESERVATION (doctrine rule 3): on the Task 18.12 baseline-6
        # re-record (the CREW-ONLY graduation slate) the interior STRONG
        # alibi_vs_sighting supply this pin anchors on is the two flags at seed-42
        # m0 p-4 (an IMPOSTOR) — alibi places p-4 in EAST_HALL (ticks 9-11) vs two
        # LABS sightings that both land on interior tick 10 (strictly inside the
        # multi-tick window, 9 < 10 < 11), so each carries neither the endpoint-tick
        # nor the boundary-overlap weak reason. This pin RE-ANCHORS to that
        # coordinate (the prior baseline-6 seed-38 m3 p-7 anchor has no successor --
        # seed 38 now holds only two meetings). The test guards
        # the checkable half — the interior STRONG detection CHANNEL is alive,
        # lights R7 (no weak marker), and re-derives byte-identically. The bytes are
        # recorded with the 13.14 self-stated down-weight already dropped, so the
        # interior flags are recorded STRONG directly and re-derivation is
        # byte-identical.
        entry = _committed_meetings(seed)[meeting_index]
        recorded = [
            flag
            for flag in entry.contradictions
            if subject in flag.subjects
            and flag.kind == "alibi_vs_sighting"
            and f"at tick {interior_tick}." in flag.description
        ]
        assert len(recorded) == 2
        rederived_by_id = {f.contradiction_id: f for f in _rederive(entry)}
        for flag in recorded:
            # The pin is an INTERIOR genuine flag, not an endpoint-band one: the
            # sighting tick sits strictly inside the alibi window, so the genuine
            # class the gate counts (which EXCLUDES the endpoint band) actually
            # carries it. Without this guard a re-anchor could silently land on an
            # endpoint-tick flag and pass while the interior supply drifted away.
            assert WEAK_REASON_ENDPOINT_TICK not in flag.description
            assert WEAK_REASON_BOUNDARY_OVERLAP not in flag.description
            # Recorded under 13.14: the self-stated marker is dropped, so the
            # genuine interior flag is STRONG already in the committed bytes (R7
            # lit).
            assert WEAK_REASON_SELF_STATED not in flag.description
            assert is_weak_contradiction(flag) is False
            # Re-derivation is byte-identical: the same contradiction id stays
            # STRONG.
            promoted = rederived_by_id[flag.contradiction_id]
            assert promoted.subjects == flag.subjects
            assert WEAK_REASON_SELF_STATED not in promoted.description
            assert is_weak_contradiction(promoted) is False


# ---------------------------------------------------------------------------
# Task 10.6: allowlist, proxy subject-account consistency, Rule-3 relevance.
#
# Audit anchors: audit-2026-06-11-2218-gameplay-data.md gp-1 (C-C-5, C-C-4),
# C-C-3. Synthetic shapes first; the committed-bytes acceptance pins (the
# DoD coordinates) close the section, walked offline against the Task 10.5
# bytes exactly like the 10.1/10.5 pin classes above.
# ---------------------------------------------------------------------------

from meetings.schemas import FoundBodyObservation  # noqa: E402


def _body_report_turn(
    *, turn_index: int, speaker: str, body_of: str, tick: int, room: str
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening" if turn_index == 0 else "reply",
        reply_to=None,
        observations=(
            FoundBodyObservation(
                type="found_body", tick=tick, body_of=body_of, room=room
            ),
        ),
        free_text=f"turn {turn_index}",
    )


class TestProxyAlibiSubjectAccountConsistency:
    """Audit C-C-4, owner option (b): suppress + re-target proxy alibis.

    The Wave-0 strong band was 3/3 proxy-shaped (alibi speaker != subject
    always escapes the self-stated weak band) at 1 TP / 2 FP. When the
    subject's OWN account agrees with the conflicting sighting, the proxy
    claim is the odd account out: the flag re-targets WEAK at the proxy
    speaker. When the subject echoed the proxy's (false) alibi -- the
    seed-24 true-positive shape -- nothing suppresses.
    """

    def _seed28_shape(self) -> MeetingTranscript:
        # Miniature of seed 28 m1: p-7's over-broad proxy alibi for p-9
        # vs sightings of p-9 in WEST_HALL -- which p-9's OWN
        # self-sighting agrees with.
        subject_turn = MeetingTurn(
            turn_id="m-1:turn-1",
            turn_index=1,
            speaker="p-9",
            turn_kind="reply",
            reply_to=None,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=17, subject="p-9", room="WEST_HALL"
                ),
            ),
            free_text="turn 1",
        )
        return MeetingTranscript(
            turns=(
                _sighting_turn(
                    turn_index=0,
                    speaker="p-3",
                    subject="p-9",
                    tick=17,
                    room="WEST_HALL",
                ),
                subject_turn,
                _alibi_turn(
                    turn_index=2,
                    speaker="p-7",
                    subject="p-9",
                    from_tick=0,
                    to_tick=18,
                    room="CAFETERIA",
                ),
            )
        )

    def test_consistent_subject_account_suppresses_and_retargets(self) -> None:
        flags = detect_contradictions(self._seed28_shape())

        # Both sightings (p-3's and p-9's own) conflicted with p-7's
        # proxy alibi; both flags re-target at p-7, none lands on p-9.
        assert flags
        assert all(flag.subjects == ("p-7",) for flag in flags)
        for flag in flags:
            assert flag.kind == "alibi_vs_sighting"
            assert is_weak_contradiction(flag)
            assert WEAK_REASON_RETARGETED_PROXY in flag.description

    def test_retargets_share_the_proxy_claim_lift_key(self) -> None:
        # Belief Rule 2 dedups its lift per (subject, alibi-claim) key, so
        # however many sightings the proxy claim conflicts with, the
        # re-targets sum to ONE weak delta on the proxy speaker -- a
        # re-target can never eject alone (the gp-1 over-suppression
        # tripwire's flip side).
        flags = detect_contradictions(self._seed28_shape())
        assert len({contradiction_lift_key(flag) for flag in flags}) == 1

    def test_subject_echo_of_the_proxy_alibi_keeps_the_strong_flag(self) -> None:
        # The seed-24 TP shape: the proxy (fellow impostor) states the
        # false alibi FIRST, the subject ECHOES it, and the subject's own
        # per-tick accounts agree with the ALIBI, not the sighting. No
        # self-account matches the sighting room, so no suppression -- the
        # strong flag on the subject survives.
        transcript = MeetingTranscript(
            turns=(
                _sighting_turn(
                    turn_index=0, speaker="p-7", subject="p-4", tick=8, room="WEST_HALL"
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-1",
                    subject="p-4",
                    from_tick=0,
                    to_tick=9,
                    room="CAFETERIA",
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-4",
                    subject="p-4",
                    from_tick=0,
                    to_tick=9,
                    room="CAFETERIA",
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert len(flags) == 1
        assert flags[0].subjects == ("p-4",)
        assert not is_weak_contradiction(flags[0])

    def test_subject_account_is_read_before_echo_dedup(self) -> None:
        # The ordering subtlety the contract names: the agreeing
        # self-account is itself an alibi the PROXY stated first, so
        # echo-dedup keeps the proxy's copy and discards the subject's --
        # the subject's own account would be invisible to a post-dedup
        # lookup exactly when the proxy spoke first. The pre-dedup lookup
        # still sees it: the conflicting blanket alibi suppresses and
        # re-targets.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-5",
                    from_tick=0,
                    to_tick=10,
                    room="CAFETERIA",
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-5",
                    from_tick=4,
                    to_tick=6,
                    room="WEST_HALL",
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-5",
                    subject="p-5",
                    from_tick=4,
                    to_tick=6,
                    room="WEST_HALL",
                ),
                _sighting_turn(
                    turn_index=3, speaker="p-8", subject="p-5", tick=5, room="WEST_HALL"
                ),
            )
        )
        flags = detect_contradictions(transcript)

        retargets = [
            flag for flag in flags if WEAK_REASON_RETARGETED_PROXY in flag.description
        ]
        assert len(retargets) == 1
        assert retargets[0].subjects == ("p-1",)
        # The proxy rule owns the alibi_vs_sighting path: no SIGHTING flag
        # lands on the subject. (The p-1 vs p-2 alibi_conflict pair still
        # names p-5 -- the conflict path is outside the rule's contract
        # scope, and that flag is weak-banded.)
        assert not any(
            "p-5" in flag.subjects and flag.kind == "alibi_vs_sighting"
            for flag in flags
        )

    def test_account_outside_the_proxy_window_does_not_suppress(self) -> None:
        # The subject admits the sighting's room only OUTSIDE the proxy
        # claim's window: the proxy claim and the sighting still cannot
        # both be true, and the subject's account does not arbitrate --
        # the flag stays on the subject.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=12,
                    to_tick=14,
                    room="WEST_HALL",
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-7",
                    subject="p-9",
                    from_tick=2,
                    to_tick=8,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=2, speaker="p-3", subject="p-9", tick=5, room="WEST_HALL"
                ),
            )
        )
        flags = detect_contradictions(transcript)

        assert any(
            flag.subjects == ("p-9",) and flag.kind == "alibi_vs_sighting"
            for flag in flags
        )
        assert not any(
            WEAK_REASON_RETARGETED_PROXY in flag.description for flag in flags
        )

    def test_self_stated_alibi_never_retargets(self) -> None:
        # The proxy rule keys on speaker != subject, so a self-stated alibi is
        # never re-targeted to a proxy speaker -- the flag stays on the subject
        # (p-9), the self-pair/self-stated band's business, not the proxy
        # rule's. Task 13.14 promotes this self-stated alibi_vs_sighting to
        # STRONG (the down-weight reversal); the no-retarget property this test
        # guards (subject stays p-9) is unchanged.
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-9",
                    subject="p-9",
                    from_tick=0,
                    to_tick=9,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-3", subject="p-9", tick=5, room="WEST_HALL"
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].subjects == ("p-9",)
        assert WEAK_REASON_SELF_STATED not in flags[0].description
        assert is_weak_contradiction(flags[0]) is False


class TestProxyIntraTurnGuard:
    """Task 10.10 (audit-2026-06-13-1816 C-C-2, C-C-3): the same-speaker guard.

    When BOTH events of a contradiction resolve to ONE speaker who is NOT
    the subject, the flag is one narrator's two proxy-claims about a third
    party in mutual conflict -- a flag-stacking artifact, re-targeted WEAK
    at the speaker. Cross-speaker pairings (two-witness disagreements, the
    impostor-frames-innocent deception frame) and self-contradictions
    (speaker IS the subject) are untouched.
    """

    def _proxy_pair_turn(
        self,
        *,
        speaker: str,
        subject: str,
        alibi_room: str,
        other_room: str,
        sighting_tick: int,
    ) -> MeetingTurn:
        # One speaker, one turn: a proxy alibi about ``subject`` plus a
        # contradicting proxy sighting of the same subject. Both events
        # resolve to ``speaker`` (the guard's single-author condition).
        return MeetingTurn(
            turn_id="m-1:turn-1",
            turn_index=1,
            speaker=speaker,
            turn_kind="reply",
            reply_to=None,
            claims=(
                AlibiClaim(
                    type="alibi",
                    subject=subject,
                    from_tick=2,
                    to_tick=8,
                    room=alibi_room,
                ),
            ),
            observations=(
                SawPlayerObservation(
                    type="saw_player",
                    tick=sighting_tick,
                    subject=subject,
                    room=other_room,
                ),
            ),
            free_text="turn 1",
        )

    def test_same_speaker_alibi_vs_sighting_retargets_weak(self) -> None:
        # The seed-2/seed-40 alibi_vs_sighting shape: p-5's proxy alibi
        # for p-4 conflicts with p-5's own sighting of p-4 -- a would-be
        # STRONG flag (speaker != subject), capped WEAK at the speaker.
        transcript = MeetingTranscript(
            turns=(
                self._proxy_pair_turn(
                    speaker="p-5",
                    subject="p-4",
                    alibi_room="ENGINEERING",
                    other_room="EAST_HALL",
                    sighting_tick=5,
                ),
            )
        )
        flags = detect_contradictions(transcript)
        sightings = [f for f in flags if f.kind == "alibi_vs_sighting"]
        assert len(sightings) == 1
        flag = sightings[0]
        assert flag.subjects == ("p-5",)
        assert is_weak_contradiction(flag)
        assert WEAK_REASON_PROXY_INTRA_TURN in flag.description
        # p-4 -- the third party the claims were ABOUT -- carries no flag.
        assert not any("p-4" in f.subjects for f in flags)

    def test_same_speaker_alibi_conflict_retargets_weak(self) -> None:
        # The seed-40 alibi_conflict shape: p-5's two p-4-alibis name p-4
        # in disjoint rooms over the same window -- a would-be STRONG
        # conflict, re-targeted WEAK at p-5.
        conflict_turn = MeetingTurn(
            turn_id="m-1:turn-1",
            turn_index=1,
            speaker="p-5",
            turn_kind="reply",
            reply_to=None,
            claims=(
                AlibiClaim(
                    type="alibi",
                    subject="p-4",
                    from_tick=1,
                    to_tick=6,
                    room="EAST_HALL",
                ),
                AlibiClaim(
                    type="alibi",
                    subject="p-4",
                    from_tick=1,
                    to_tick=6,
                    room="ENGINEERING",
                ),
            ),
            free_text="turn 1",
        )
        flags = detect_contradictions(MeetingTranscript(turns=(conflict_turn,)))
        conflicts = [f for f in flags if f.kind == "alibi_conflict"]
        assert len(conflicts) == 1
        flag = conflicts[0]
        assert flag.subjects == ("p-5",)
        assert is_weak_contradiction(flag)
        assert WEAK_REASON_PROXY_INTRA_TURN in flag.description

    def test_cross_speaker_conflict_is_untouched(self) -> None:
        # The legitimate two-witness disagreement: two DIFFERENT speakers
        # place p-4 in incompatible rooms. Different authors, so the guard
        # never fires -- the flag stays on the subject (the seed-14 shape,
        # the seed-12 deception frame's structural sibling).
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-4",
                    from_tick=1,
                    to_tick=6,
                    room="EAST_HALL",
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-2",
                    subject="p-4",
                    from_tick=1,
                    to_tick=6,
                    room="ENGINEERING",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].subjects == ("p-4",)
        assert WEAK_REASON_PROXY_INTRA_TURN not in flags[0].description

    def test_cross_speaker_alibi_vs_sighting_is_untouched(self) -> None:
        # A proxy alibi (p-1 about p-4) vs a THIRD party's sighting (p-2 of
        # p-4): two authors, so the same-speaker guard never fires. (The
        # subject's own account does not agree, so the 10.6 rule stays out
        # too -- this is the cross-speaker frame the guard must not blunt.)
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-1",
                    subject="p-4",
                    from_tick=2,
                    to_tick=8,
                    room="ENGINEERING",
                ),
                _sighting_turn(
                    turn_index=1, speaker="p-2", subject="p-4", tick=5, room="EAST_HALL"
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].subjects == ("p-4",)
        assert WEAK_REASON_PROXY_INTRA_TURN not in flags[0].description

    def test_self_contradiction_is_not_retargeted(self) -> None:
        # The subject contradicting THEMSELVES (speaker IS subject): the
        # self-pair weak band's business, not the proxy guard's. The flag
        # stays on the subject and keeps its self-pair reason.
        self_turn = MeetingTurn(
            turn_id="m-1:turn-0",
            turn_index=0,
            speaker="p-4",
            turn_kind="opening",
            reply_to=None,
            claims=(
                AlibiClaim(
                    type="alibi",
                    subject="p-4",
                    from_tick=1,
                    to_tick=6,
                    room="EAST_HALL",
                ),
                AlibiClaim(
                    type="alibi",
                    subject="p-4",
                    from_tick=1,
                    to_tick=6,
                    room="ENGINEERING",
                ),
            ),
            free_text="turn 0",
        )
        flags = detect_contradictions(MeetingTranscript(turns=(self_turn,)))
        conflicts = [f for f in flags if f.kind == "alibi_conflict"]
        assert len(conflicts) == 1
        assert conflicts[0].subjects == ("p-4",)
        assert WEAK_REASON_SELF_PAIR in conflicts[0].description
        assert WEAK_REASON_PROXY_INTRA_TURN not in conflicts[0].description

    def test_retarget_is_deterministic(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                self._proxy_pair_turn(
                    speaker="p-5",
                    subject="p-4",
                    alibi_room="ENGINEERING",
                    other_room="EAST_HALL",
                    sighting_tick=5,
                ),
            )
        )
        first = detect_contradictions(transcript)
        second = detect_contradictions(transcript)
        assert [f.model_dump_json() for f in first] == [
            f.model_dump_json() for f in second
        ]

    def test_same_author_10_6_retarget_folds_under_one_lift_key(self) -> None:
        # Codex PR #152 review, P1 #2: one turn where p-5 gives two
        # conflicting p-4 alibis PLUS a p-4 sighting (also by p-5) that p-4's
        # OWN account confirms. The conflict re-targets via 10.10; the two
        # alibi_vs_sighting flags re-target via the 10.6 subject-account rule
        # (WEAK_REASON_RETARGETED_PROXY). All three are one narrator's single
        # turn, so they must fold to ONE weak lift key on p-5 -- otherwise the
        # per-claim 10.6 keys stack with the 10.10 key (0.5 + 0.08*3 = 0.74)
        # and the single-turn artifact crosses the gate on the proxy speaker.
        from agents.memory.beliefs import BeliefState, apply_contradiction_rule

        transcript = MeetingTranscript(
            turns=(
                MeetingTurn(
                    turn_id="m-1:turn-1",
                    turn_index=1,
                    speaker="p-5",
                    turn_kind="reply",
                    reply_to=None,
                    claims=(
                        AlibiClaim(
                            type="alibi",
                            subject="p-4",
                            from_tick=1,
                            to_tick=6,
                            room="EAST_HALL",
                        ),
                        AlibiClaim(
                            type="alibi",
                            subject="p-4",
                            from_tick=1,
                            to_tick=6,
                            room="ENGINEERING",
                        ),
                    ),
                    observations=(
                        SawPlayerObservation(
                            type="saw_player", tick=3, subject="p-4", room="STORAGE"
                        ),
                    ),
                    free_text="turn 1",
                ),
                _alibi_turn(
                    turn_index=2,
                    speaker="p-4",
                    subject="p-4",
                    from_tick=2,
                    to_tick=4,
                    room="STORAGE",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        p5_flags = [flag for flag in flags if flag.subjects == ("p-5",)]
        # The 10.6 + 10.10 re-targets all land on p-5 under ONE fold key.
        assert len(p5_flags) >= 2
        assert {contradiction_lift_key(flag) for flag in p5_flags} == {
            "proxy-intra-turn"
        }
        assert all(
            WEAK_REASON_PROXY_INTRA_TURN in flag.description for flag in p5_flags
        )

        beliefs = BeliefState()
        beliefs.seed_player("p-5", suspicion=0.5, trust=0.5)
        lifted = apply_contradiction_rule(beliefs, p5_flags)
        assert lifted.view("p-5").suspicion == pytest.approx(0.58)
        assert lifted.view("p-5").suspicion < 0.60


class TestIsRelevantSighting:
    """The named pure Rule-3 relevance predicate (audit C-C-3; 10.7 reuses it)."""

    def test_spawn_window_ticks_are_never_relevant(self) -> None:
        for tick in range(SPAWN_WINDOW_LAST_TICK + 1):
            assert not is_relevant_sighting(
                tick=tick,
                rooms=frozenset({"MEDBAY"}),
                triggering_body_rooms=frozenset(),
            )

    def test_tick_two_or_later_is_outside_the_spawn_window(self) -> None:
        assert is_relevant_sighting(
            tick=SPAWN_WINDOW_LAST_TICK + 1,
            rooms=frozenset({"MEDBAY"}),
            triggering_body_rooms=frozenset(),
        )

    def test_kill_scene_sighting_is_not_relevant(self) -> None:
        assert not is_relevant_sighting(
            tick=16,
            rooms=frozenset({"ADMIN"}),
            triggering_body_rooms=frozenset({"ADMIN"}),
        )

    def test_non_scene_room_is_relevant(self) -> None:
        assert is_relevant_sighting(
            tick=16,
            rooms=frozenset({"MEDBAY"}),
            triggering_body_rooms=frozenset({"ADMIN"}),
        )

    def test_roomless_account_gates_only_on_the_spawn_window(self) -> None:
        # The claim-stated corroboration shape: no room, so the kill-scene
        # prong can never bind -- only the tick prong gates.
        assert is_relevant_sighting(
            tick=2, rooms=frozenset(), triggering_body_rooms=frozenset({"ADMIN"})
        )
        assert not is_relevant_sighting(
            tick=0, rooms=frozenset(), triggering_body_rooms=frozenset({"ADMIN"})
        )


class TestTriggeringBodyRooms:
    """The kill-scene set is the OPENING turn's found_body rooms only."""

    def test_opening_body_room_is_canonicalised(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _body_report_turn(
                    turn_index=0, speaker="p-3", body_of="p-4", tick=17, room="admin"
                ),
            )
        )
        assert triggering_body_rooms(transcript) == frozenset({"ADMIN"})

    def test_empty_transcript_has_no_scene(self) -> None:
        assert triggering_body_rooms(MeetingTranscript()) == frozenset()

    def test_later_turn_bodies_do_not_widen_the_scene(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _sighting_turn(
                    turn_index=0, speaker="p-3", subject="p-6", tick=5, room="MEDBAY"
                ),
                _body_report_turn(
                    turn_index=1, speaker="p-8", body_of="p-4", tick=17, room="ADMIN"
                ),
            )
        )
        assert triggering_body_rooms(transcript) == frozenset()

    def test_emergency_trigger_ignores_a_fabricated_opening_body(self) -> None:
        # Task 10.11 (audit-2026-06-13-1816 B-B-1): an emergency meeting has
        # no kill scene by design (§5.2 PHASE 1). Even when the opening turn
        # carries a (model-fabricated) found_body -- the exact close-baseline
        # shape -- gating on trigger_kind="emergency" yields the empty set, so
        # the fabrication cannot widen the §6.3 Rule-3 exclusion zone.
        transcript = MeetingTranscript(
            turns=(
                _body_report_turn(
                    turn_index=0, speaker="p-3", body_of="p-2", tick=8, room="REACTOR"
                ),
            )
        )
        # The default / report path still trusts the opening body...
        assert triggering_body_rooms(transcript) == frozenset({"REACTOR"})
        assert triggering_body_rooms(transcript, trigger_kind="report") == frozenset(
            {"REACTOR"}
        )
        # ...but an emergency meeting never does.
        assert (
            triggering_body_rooms(transcript, trigger_kind="emergency") == frozenset()
        )

    def test_emergency_trigger_on_a_bodyless_opening_is_still_empty(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _sighting_turn(
                    turn_index=0, speaker="p-3", subject="p-6", tick=5, room="MEDBAY"
                ),
            )
        )
        assert (
            triggering_body_rooms(transcript, trigger_kind="emergency") == frozenset()
        )


class TestDetectCorroborationsRelevanceGate:
    """Audit C-C-3: evidentially-empty vouches no longer corroborate."""

    def test_spawn_window_sighting_does_not_corroborate(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _alibi_turn(
                    turn_index=0,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=0,
                    to_tick=7,
                    room="CAFETERIA",
                ),
                _sighting_turn(
                    turn_index=1,
                    speaker="p-5",
                    subject="p-8",
                    tick=SPAWN_WINDOW_LAST_TICK,
                    room="CAFETERIA",
                ),
            )
        )
        assert detect_corroborations(transcript) == ()

    def test_kill_scene_sighting_does_not_corroborate(self) -> None:
        # The seed-6 m1 byte shape in miniature: the reporter found the
        # body in ADMIN and ALSO saw the subject in ADMIN inside the
        # subject's alibi window -- presence at the scene must never
        # exonerate.
        opening = MeetingTurn(
            turn_id="m-1:turn-0",
            turn_index=0,
            speaker="p-3",
            turn_kind="opening",
            reply_to=None,
            observations=(
                FoundBodyObservation(
                    type="found_body", tick=17, body_of="p-4", room="ADMIN"
                ),
                SawPlayerObservation(
                    type="saw_player", tick=16, subject="p-6", room="ADMIN"
                ),
            ),
            free_text="turn 0",
        )
        transcript = MeetingTranscript(
            turns=(
                opening,
                _alibi_turn(
                    turn_index=1,
                    speaker="p-6",
                    subject="p-6",
                    from_tick=15,
                    to_tick=17,
                    room="ADMIN",
                ),
            )
        )
        assert detect_corroborations(transcript) == ()

    def test_interior_non_scene_sighting_still_corroborates(self) -> None:
        # The gate prunes, never kills: an interior-tick sighting away
        # from the scene is exactly the Rule-3 evidence that should count.
        transcript = MeetingTranscript(
            turns=(
                _body_report_turn(
                    turn_index=0, speaker="p-3", body_of="p-4", tick=17, room="ADMIN"
                ),
                _alibi_turn(
                    turn_index=1,
                    speaker="p-8",
                    subject="p-8",
                    from_tick=2,
                    to_tick=7,
                    room="MEDBAY",
                ),
                _sighting_turn(
                    turn_index=2, speaker="p-5", subject="p-8", tick=4, room="MEDBAY"
                ),
            )
        )
        corroborations = detect_corroborations(transcript)
        assert len(corroborations) == 1
        assert corroborations[0].subject == "p-8"


class TestCommittedBytes106Pins:
    """The Task 10.6 DoD acceptance pins, walked offline (no re-record)."""

    def test_varying_rooms_mints_nothing_set_wide(self) -> None:
        # Audit C-C-5: at W0 the "p-9 in VARYING_ROOMS" phantom-room alibi
        # minted a 22-flag storm on seed 13 m1 (25% of set volume), which the
        # 10.6 allowlist collapsed OFFLINE. The 10.9 re-record runs the allowlist
        # at RECORD time, so the non-spatial label never pairs: zero recorded
        # contradictions reference it anywhere on the set.
        flagged = [
            flag
            for seed in range(50)
            for entry in _committed_meetings(seed)
            for flag in entry.contradictions
            if "VARYING_ROOMS" in flag.description
        ]
        assert flagged == []

    def test_placeholder_labels_classify_non_spatial(self) -> None:
        # The allowlist's classification of the two W0-leaked placeholder
        # labels (seed-13's ``VARYING_ROOMS`` storm, seed-6's ``HALLS``): both
        # canonicalize to the empty set, so a non-spatial side mints no flag.
        # Pinned as pure logic (the W0 seed-6 m1 HALLS claim is not present in
        # the re-record); the set-wide absence is pinned above.
        assert canonical_rooms("HALLS") == frozenset()
        assert canonical_rooms("VARYING_ROOMS") == frozenset()

    def test_seed28_m1_proxy_fp_does_not_recur(self) -> None:
        # Audit C-C-4 FP: at W0 innocent p-9 was ejected 4-3 off 2 over-broad
        # proxy strong flags on seed 28 m1, which 10.6 suppressed+re-targeted
        # OFFLINE. On the Task 16.14 baseline-4 re-record (proxy gate at record
        # time) the FP does not recur — p-9 (the FP victim) carries NO strong flag.
        # (The meeting's only strong flag on baseline 4 is a legitimate Task-15.4
        # vent_sighting on p-8, a different genuine class; the proxy suppress+
        # re-target LOGIC is covered by the synthetic proxy tests.)
        entry = _committed_meetings(28)[1]
        p9_strong = [
            flag
            for flag in entry.contradictions
            if "p-9" in flag.subjects and not is_weak_contradiction(flag)
        ]
        assert p9_strong == []

    def test_seed28_m1_p9_rederived_max_below_the_gate(self) -> None:
        # The audit C-C-4 proxy repair guarantees the over-broad proxy alibi
        # cannot eject innocent p-9 alone: p-9 carries no re-derived flag, so
        # its §4.6 verdict from the 0.5 prior stays BELOW the 0.60 gate.
        #
        # Task 16.14 baseline-4 re-record: at this re-recorded coordinate p-7
        # carries no flag either, so it stays at the 0.5 prior (the pre-13.14
        # crew-FP promotion demo no longer occurs at seed-28 m1; the new bytes are
        # recorded under 13.14, so promotions live in the bytes elsewhere, not
        # minted here at re-extraction). The C-C-4 repair — suppressing the
        # PROXY band, a different class — is unaffected, and p-9 stays below gate.
        from agents.memory.beliefs import BeliefState, apply_contradiction_rule

        entry = _committed_meetings(28)[1]
        rederived = _rederive(entry)

        def _rederived_suspicion(player: str) -> float:
            beliefs = BeliefState()
            beliefs.seed_player(player, suspicion=0.5, trust=0.5)
            lifted = apply_contradiction_rule(
                beliefs, [flag for flag in rederived if player in flag.subjects]
            )
            return lifted.view(player).suspicion

        assert _rederived_suspicion("p-9") < 0.60
        assert _rederived_suspicion("p-7") == pytest.approx(0.50)

    def test_strong_flags_surface_under_the_wave_e_substrate(self) -> None:
        # The Task 18.12 baseline-6 re-record (the CREW-ONLY graduation slate, with
        # the whereabouts-interior and vent-placement levers now UNCONDITIONAL)
        # lights a RICHER R7 detector surface: 160 strong flags across the committed
        # meetings. Composition is all legitimate detector kinds (vent_sighting 96,
        # alibi_vs_sighting 58, alibi_vs_physical 6) — no forbidden leak shape, and
        # NO strong alibi_conflict (the lone-STRONG cross-speaker conflict of
        # baseline 1 stays gone with the railroad elimination). The graduated
        # whereabouts-interior exemption promotes single-tick self-alibi-vs-sighting
        # flags into the strong band, and Task 15.4's vent observability plus the
        # grounded vent-placement variant carry the rest; the weak band holds 26
        # flags — ALIVE (gated, not killed).
        weak = strong = 0
        for seed in range(50):
            for entry in _committed_meetings(seed):
                for flag in entry.contradictions:
                    if is_weak_contradiction(flag):
                        weak += 1
                    else:
                        strong += 1
        assert strong == 160  # the R7 detector surface (vent + graduated levers)
        assert weak == 26  # the weak band stays alive (gated, not killed)

    def test_seed2_m0_surviving_corroborations_are_interior_tick(self) -> None:
        # Audit C-C-3: at W0 a kill-scene sighting at seed 6 m1 was relevance-
        # gated to ZERO corroborations. Re-pointed to the Task 16.14 baseline-4
        # re-record (Qwen/Qwen3.6-27B, qwen3_6_27b.v1 prompts, all six substrate
        # levers ON): seed 2 m0 is a meeting whose corroborations DO survive the
        # gate (5 pairs). Assert every one is backed by an interior-tick sighting,
        # so no kill-scene / spawn-window evidence-free pair leaks through (the same
        # property the set-wide pin below enforces across all 50 seeds).
        entry = _committed_meetings(2)[0]
        sightings_by_id = {
            f"turn:{turn.turn_id}:obs:{index}": observation
            for turn in entry.transcript.turns
            for index, observation in enumerate(turn.observations)
            if isinstance(observation, SawPlayerObservation)
        }
        pairs = detect_corroborations(entry.transcript, roster=_living_roster(entry))
        assert pairs  # the re-record meeting does produce backed corroborations
        for pair in pairs:
            assert sightings_by_id[pair.sighting_event_id].tick > SPAWN_WINDOW_LAST_TICK

    def test_no_spawn_window_corroboration_survives_set_wide(self) -> None:
        # DoD pin: spawn-window-sourced corroborations count 0 set-wide,
        # and the channel survives the gate (re-derived Rule-3 pairs stay
        # well above zero -- gated, not killed).
        surviving = 0
        for seed in range(50):
            for entry in _committed_meetings(seed):
                sightings_by_id = {
                    f"turn:{turn.turn_id}:obs:{index}": observation
                    for turn in entry.transcript.turns
                    for index, observation in enumerate(turn.observations)
                    if isinstance(observation, SawPlayerObservation)
                }
                for pair in detect_corroborations(
                    entry.transcript, roster=_living_roster(entry)
                ):
                    surviving += 1
                    sighting = sightings_by_id[pair.sighting_event_id]
                    assert sighting.tick > SPAWN_WINDOW_LAST_TICK, (
                        f"spawn-window corroboration survived: seed {seed}, "
                        f"{pair.sighting_event_id}"
                    )
        # 245 pairs survive the gate on the Task 18.12 baseline-6 re-record (the
        # CREW-ONLY graduation slate). EVERY surviving pair still passes the
        # per-pair spawn-window leak assert above (tick > SPAWN_WINDOW_LAST_TICK), so
        # the no-spawn-window-leak firewall holds; the count moved with the
        # substrate's saw_player supply. The over-suppression tripwire: a future
        # change driving this to 0 means the channel died, which the audit ranks as
        # bad as the artifacts. Well above zero: gated, not killed.
        assert surviving == 245


class TestCommittedBytes1010Pins:
    """Task 10.10 DoD pins, re-pointed at the Task 18.12 baseline-6 re-record.

    audit-2026-06-13-1816 C-C-2/C-C-3. On the baseline-6 re-record (the CREW-ONLY
    graduation slate, after the vent-widening cascade) the same-speaker guard is
    DORMANT: it fires at ZERO committed sites -- no single narrator authors both
    events of a contradiction about a third party anywhere in the re-recorded set.
    The guard LOGIC is fully pinned by the synthetic ``TestProxyIntraTurnGuard``
    shapes; these committed-bytes pins now pin the honest absence (no firing) and
    guard that no future drift silently re-targets a two-author disagreement onto
    the speaker (the alibi_conflict tripwire below).
    """

    def test_seed5_m0_flag_retargets_weak_at_p9(self) -> None:
        # C-C-2/C-C-3, INTENT-PRESERVED (doctrine rule 3) on the Task 16.14
        # baseline-4 re-record (Qwen/Qwen3.6-27B, qwen3_6_27b.v1 prompts). The
        # baseline-2/3 representative proxy-intra-turn firing site (p-9's proxy
        # alibi for p-1 conflicting with p-9's own sighting of p-1, re-targeted WEAK
        # at speaker p-9) DISSOLVED with the alibi-surface collapse: seed-5 m0 now
        # re-derives to ZERO contradiction flags, and no same-speaker proxy pair
        # fires the guard anywhere on the set. This pins the honest absence at the
        # former representative coordinate: seed-5 m0 mints no proxy-intra-turn
        # retarget on the speaker AND none leaks onto the third party. The guard
        # LOGIC (that such a pair WOULD re-target weak) is pinned by the synthetic
        # ``TestProxyIntraTurnGuard.test_same_speaker_alibi_vs_sighting_retargets_weak``.
        entry = _committed_meetings(5)[0]
        rederived = _rederive(entry)
        on_p1_proxy = [
            flag
            for flag in rederived
            if "p-1" in flag.subjects
            and WEAK_REASON_PROXY_INTRA_TURN in flag.description
        ]
        retargeted = [
            flag
            for flag in rederived
            if flag.subjects == ("p-9",)
            and WEAK_REASON_PROXY_INTRA_TURN in flag.description
        ]
        # Guard dormant on baseline-4: no proxy-intra-turn retarget on the speaker,
        # and none leaked onto the third party p-1.
        assert on_p1_proxy == []
        assert retargeted == []
        assert all(is_weak_contradiction(flag) for flag in retargeted)

    def test_seed38_m1_p6_below_gate_and_not_redirect_argmax(self) -> None:
        # C-C-2 (re-pointed to the Task 16.14 baseline-4 re-record):
        # p-6's re-derived max stays at the 0.5 prior (it carries no flag), below
        # the §4.6 gate, so the 10.9.2 redirect -- which only ever targets an
        # over-gate candidate -- can never launder an ungrounded ballot onto p-6.
        # On the re-recorded bytes the seed-38 m1 proxy-intra-turn re-target no
        # longer occurs (it moved off this coordinate), so p-2 too carries no flag
        # and stays at the 0.5 prior -- the single turn's artifact crosses the gate
        # on NO ONE. Walked from the 0.5 prior, the seed-28 pin's convention.
        from agents.memory.beliefs import BeliefState, apply_contradiction_rule

        entry = _committed_meetings(38)[1]
        rederived = _rederive(entry)

        def lifted_max(player: str) -> float:
            beliefs = BeliefState()
            beliefs.seed_player(player, suspicion=0.5, trust=0.5)
            return (
                apply_contradiction_rule(
                    beliefs, [flag for flag in rederived if player in flag.subjects]
                )
                .view(player)
                .suspicion
            )

        assert lifted_max("p-6") < 0.60
        # p-2 carries no flag at this re-recorded coordinate, so it stays at the
        # 0.5 prior, still below the gate (the P1-review tripwire).
        assert lifted_max("p-2") == pytest.approx(0.50)
        assert lifted_max("p-2") < 0.60
        # The redirect argmax is the highest over-gate candidate (ties to
        # the lowest id); no proxy artifact row is over-gate, so p-6 (and
        # p-2) can never be that argmax.
        graph = {player: lifted_max(player) for player in sorted(_living_roster(entry))}
        over_gate = {p: s for p, s in graph.items() if s >= 0.60}
        assert "p-6" not in over_gate
        assert "p-2" not in over_gate
        if over_gate:
            argmax = min(over_gate, key=lambda p: (-over_gate[p], p))
            assert argmax != "p-6"

    def test_proxy_intra_turn_retargets_weak_set_wide(self) -> None:
        # INTENT-PRESERVED (doctrine rule 3) on the Task 18.12 baseline-6 re-record
        # (the CREW-ONLY graduation slate, after the vent-widening cascade). The
        # same-speaker guard is DORMANT on this re-record: NO single narrator authors
        # both events of a contradiction about a third party, so the guard re-targets
        # nothing -- the census collapses to the empty set (the prior baseline-6
        # sites seed-2 m0 / seed-40 m0 dissolved with the alibi-surface shift). The
        # invariant the C-C-3 guard protects -- every proxy-intra-turn retarget stays
        # weak-banded -- is still asserted in-loop (vacuous here) and the honest
        # absence is pinned. A future re-record firing the guard at a NON-weak band
        # re-triggers scrutiny.
        retargets: list[tuple[int, int, tuple[str, ...]]] = []
        for seed in range(50):
            for index, entry in enumerate(_committed_meetings(seed)):
                for flag in _rederive(entry):
                    if WEAK_REASON_PROXY_INTRA_TURN in flag.description:
                        assert is_weak_contradiction(flag)
                        retargets.append((seed, index, flag.subjects))
        assert sorted(set(retargets)) == []

    def test_seed25_m0_weak_cross_speaker_conflict_not_retargeted(self) -> None:
        # THE TRIPWIRE, INTENT-PRESERVED (doctrine rule 3) on the Task 18.12
        # baseline-6 re-record (the CREW-ONLY graduation slate). The
        # alibi_conflict band carries EIGHT flags set-wide, each a WEAK two-author
        # same-subject disagreement the same-speaker
        # guard must NOT re-target. The tripwire's spirit -- the guard must NEVER
        # re-target a two-author disagreement -- is pinned directly on real bytes:
        # the conflicts exist, re-derive with the same count, and NONE carries the
        # proxy-intra-turn marker. The LOGIC is pinned by the synthetic
        # TestProxyIntraTurnGuard.test_cross_speaker_conflict_is_untouched. If a
        # future re-record makes the guard FIRE on one of these (a proxy-intra-turn
        # marker appears), STOP: the guard would be over-reaching onto a two-author
        # disagreement.
        recorded_conflicts: list[ContradictionRef] = []
        rederived_conflicts: list[ContradictionRef] = []
        for seed in range(50):
            for entry in _committed_meetings(seed):
                recorded_conflicts.extend(
                    flag
                    for flag in entry.contradictions
                    if flag.kind == "alibi_conflict"
                )
                rederived_conflicts.extend(
                    flag for flag in _rederive(entry) if flag.kind == "alibi_conflict"
                )
        assert len(recorded_conflicts) == 8
        assert len(rederived_conflicts) == 8
        # The same-speaker guard re-targets NONE of the two-author conflicts.
        assert not any(
            WEAK_REASON_PROXY_INTRA_TURN in flag.description
            for flag in recorded_conflicts + rederived_conflicts
        )

    def test_seed14_m0_two_witness_disagreement_unaffected(self) -> None:
        # A genuine same-subject contradiction from TWO different speakers
        # (the seed-14 m0 two-witness fold on p-3) classifies exactly as
        # today: no retarget, re-derivation byte-identical to the record.
        entry = _committed_meetings(14)[0]
        rederived = _rederive(entry)
        recorded_by_id = {flag.contradiction_id: flag for flag in entry.contradictions}
        rederived_by_id = {flag.contradiction_id: flag for flag in rederived}
        assert rederived_by_id == recorded_by_id
        assert not any(
            WEAK_REASON_PROXY_INTRA_TURN in flag.description for flag in rederived
        )


# ---------------------------------------------------------------------------
# Task 10.7: independent voices -- the pre-vote two-witness fold's pure
# transcript half (audit gp-2 C-C-1/C-C-2; the corroborate-within-round
# owner principle). Synthetic shapes first; the committed-bytes pins (the
# DoD coordinates: the seed-30 pile-on STOP pin and the seed-2/5 yield
# voices) close the section, walked offline against the Task 10.5 bytes.
# ---------------------------------------------------------------------------

from meetings.schemas import (  # noqa: E402
    Claim,
    CompletedTaskObservation,
    CorroborationClaim,
    ObservationClaim,
    TurnKind,
)
from meetings.transcript import independent_voices  # noqa: E402


def _voice_turn(
    *,
    turn_index: int,
    speaker: str,
    turn_kind: TurnKind,
    accuses: tuple[str, ...] = (),
    supports: tuple[str, ...] = (),
    sightings: tuple[tuple[str, str, int], ...] = (),
    body: tuple[str, str, int] | None = None,
    free_text: str | None = None,
) -> MeetingTurn:
    """One turn for the voices tests: ``sightings`` are (subject, room, tick),
    ``body`` is (body_of, room, tick)."""

    observations: list[ObservationClaim] = []
    if body is not None:
        body_of, body_room, body_tick = body
        observations.append(
            FoundBodyObservation(
                type="found_body", tick=body_tick, body_of=body_of, room=body_room
            )
        )
    for subject, room, tick in sightings:
        observations.append(
            SawPlayerObservation(
                type="saw_player", tick=tick, subject=subject, room=room
            )
        )
    claims: list[Claim] = []
    for target in accuses:
        claims.append(
            AccusationClaim(
                type="accusation",
                against=target,
                confidence=0.6,
                reason=f"{speaker} accuses {target}",
            )
        )
    for supported in supports:
        claims.append(
            CorroborationClaim(
                type="corroboration",
                supports=supported,
                on_tick=5,
                reason=f"{speaker} vouches for {supported}",
            )
        )
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,
        reply_to=None,
        observations=tuple(observations),
        claims=tuple(claims),
        free_text=f"turn {turn_index}" if free_text is None else free_text,
    )


class TestIndependentVoices:
    """The Task 10.7 voice definition, prong by prong.

    A voice is a chain/opening accusation with relevance-grade
    observation backing, or an opt-in corroboration aligned with an
    existing accuser that carries the same backing. Bare verbal
    accusations carry no voice; opt-in DIRECT accusations carry no
    voice (the seed-30 anti-pile-on property).
    """

    _BODY = ("p-9", "MEDBAY", 10)

    def _two_voice_transcript(self) -> MeetingTranscript:
        return MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                ),
                _voice_turn(turn_index=1, speaker="p-2", turn_kind="reply"),
                _voice_turn(
                    turn_index=2,
                    speaker="p-3",
                    turn_kind="opt_in",
                    supports=("p-1",),
                    sightings=(("p-2", "ADMIN", 8),),
                ),
            )
        )

    def test_observation_backed_accuser_plus_aligned_opt_in_are_two_voices(
        self,
    ) -> None:
        voices = independent_voices(self._two_voice_transcript())

        assert voices == {"p-2": ("p-1", "p-3")}

    def test_bare_verbal_accusation_carries_no_voice(self) -> None:
        # The opening accuses with NO observations at all: no voice, and
        # the opt-in corroboration still aligns with the accuser and
        # carries backing, so the subject sits at one voice.
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    body=self._BODY,
                ),
                _voice_turn(
                    turn_index=1,
                    speaker="p-3",
                    turn_kind="opt_in",
                    supports=("p-1",),
                    sightings=(("p-2", "ADMIN", 8),),
                ),
            )
        )

        assert independent_voices(transcript) == {"p-2": ("p-3",)}

    def test_kill_scene_only_backing_carries_no_voice(self) -> None:
        # The seed-30 deflection shape: every located observation on the
        # accusing turn sits at the kill scene, which the §6.3 relevance
        # predicate prices as evidentially empty -- anyone at the scene
        # can say it (one home with the Task 10.6 corroboration gate).
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "MEDBAY", 9), ("p-4", "MEDBAY", 9)),
                    body=self._BODY,
                ),
            )
        )

        assert independent_voices(transcript) == {}

    def test_spawn_window_only_backing_carries_no_voice(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "CAFETERIA", SPAWN_WINDOW_LAST_TICK),),
                    body=self._BODY,
                ),
            )
        )

        assert independent_voices(transcript) == {}

    def test_placeholder_room_backing_carries_no_voice(self) -> None:
        # A non-spatial label locates nothing (the 10.6 allowlist), so it
        # cannot back a voice -- "I saw them somewhere" is bare testimony.
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "VARYING_ROOMS", 8),),
                    body=self._BODY,
                ),
            )
        )

        assert independent_voices(transcript) == {}

    def test_opt_in_direct_accusation_is_never_a_voice(self) -> None:
        # THE anti-pile-on property: an opt-in turn may accuse (§5.2
        # PHASE 3) and may even carry relevant backing, but its direct
        # accusation adds no voice -- only its corroboration can, and
        # only when aligned with an existing accuser of the subject.
        # Witness COUNT cannot filter the seed-30 pile-on; independence
        # can.
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                ),
                _voice_turn(turn_index=1, speaker="p-2", turn_kind="reply"),
                _voice_turn(
                    turn_index=2,
                    speaker="p-3",
                    turn_kind="opt_in",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                ),
                _voice_turn(
                    turn_index=3,
                    speaker="p-4",
                    turn_kind="opt_in",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                ),
            )
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}

    def test_opt_in_corroboration_of_a_non_accuser_adds_no_voice(self) -> None:
        # The exact seed-30 m1 mechanics: the opt-in accuses subject B
        # directly while its corroboration supports an accuser of
        # subject A -- it is a voice for A, never for B.
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                ),
                _voice_turn(
                    turn_index=1,
                    speaker="p-2",
                    turn_kind="reply",
                    accuses=("p-3",),
                ),
                _voice_turn(turn_index=2, speaker="p-3", turn_kind="reply"),
                _voice_turn(
                    turn_index=3,
                    speaker="p-4",
                    turn_kind="opt_in",
                    accuses=("p-3",),
                    supports=("p-1",),
                    sightings=(("p-3", "ADMIN", 8),),
                ),
            )
        )

        voices = independent_voices(transcript)

        assert voices == {"p-2": ("p-1", "p-4")}
        assert "p-3" not in voices

    def test_opt_in_corroboration_without_backing_adds_no_voice(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                ),
                _voice_turn(
                    turn_index=1,
                    speaker="p-3",
                    turn_kind="opt_in",
                    supports=("p-1",),
                ),
            )
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}

    def test_task_completion_backing_counts(self) -> None:
        # "Observation backing" is turn-level first-hand located content:
        # a completed task in a non-scene room outside the spawn window
        # stakes the speaker's whereabouts exactly like a self-sighting
        # (the seed-2 m1 witness shape).
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    body=self._BODY,
                ).model_copy(
                    update={
                        "observations": (
                            FoundBodyObservation(
                                type="found_body",
                                tick=10,
                                body_of="p-9",
                                room="MEDBAY",
                            ),
                            CompletedTaskObservation(
                                type="completed_task",
                                tick=8,
                                task_id="wires",
                                room="ADMIN",
                            ),
                        )
                    }
                ),
            )
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}

    def test_subject_is_never_a_voice(self) -> None:
        # A self-accusation mints no voice, and the subject vouching for
        # their own accuser (the seed-30 m1 turn-2 shape, were it an
        # opt-in) can never voice against themselves.
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-2",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                ),
                _voice_turn(
                    turn_index=1,
                    speaker="p-1",
                    turn_kind="reply",
                    accuses=("p-3",),
                    sightings=(("p-3", "ADMIN", 8),),
                ),
                _voice_turn(
                    turn_index=2,
                    speaker="p-3",
                    turn_kind="opt_in",
                    supports=("p-1",),
                    sightings=(("p-3", "ADMIN", 8),),
                ),
            )
        )

        voices = independent_voices(transcript)

        assert "p-2" not in voices
        assert voices == {"p-3": ("p-1",)}

    def test_one_speaker_is_one_voice_however_many_claims(self) -> None:
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2", "p-2"),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                ),
            )
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}

    def test_roster_filters_subjects(self) -> None:
        transcript = self._two_voice_transcript()

        assert independent_voices(transcript, roster=frozenset({"p-1", "p-3"})) == {}
        assert independent_voices(transcript, roster=frozenset()) == {}

    def test_deterministic_and_sorted(self) -> None:
        transcript = self._two_voice_transcript()

        first = independent_voices(transcript)
        second = independent_voices(transcript)

        assert first == second
        assert all(speakers == tuple(sorted(speakers)) for speakers in first.values())
        assert list(first) == sorted(first)


class TestVoiceEchoDedup:
    """Echo-dedup: copied rationales cannot manufacture independence.

    Task 10.15 (audit 2026-06-13 H-4): distinct speakers whose voice-minting
    turns carry the SAME rationale (after :func:`_normalize_rationale`'s
    case/punctuation/whitespace normalisation) collapse to ONE voice --
    the model's verbatim rationale copying (many within-meeting echo pairs)
    is copied reasoning, not independent corroboration.
    """

    _BODY = ("p-9", "MEDBAY", 10)

    def _two_accusers(self, *, free_text_a: str, free_text_b: str) -> MeetingTranscript:
        # Two distinct observation-backed accusers of p-2 (an opening and a
        # chain reply). Their voice count is two UNLESS their rationales echo.
        return MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                    free_text=free_text_a,
                ),
                _voice_turn(
                    turn_index=1,
                    speaker="p-3",
                    turn_kind="reply",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    free_text=free_text_b,
                ),
            )
        )

    def test_verbatim_echo_collapses_a_would_be_fold_to_one_voice(self) -> None:
        # Two backed accusers would be a two-witness FOLD; verbatim-copied
        # rationales drop them to ONE voice (the inform band), so copied echoes
        # cannot manufacture the fold's independence.
        transcript = self._two_accusers(
            free_text_a="p-2 left the body without helping.",
            free_text_b="p-2 left the body without helping.",
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}

    def test_case_and_punctuation_variant_is_an_echo(self) -> None:
        # "near-identical" is normalisation-identical: case, punctuation, and
        # whitespace differences are erased, so a trivially reworded copy
        # still collapses.
        transcript = self._two_accusers(
            free_text_a="p-2 left the body without helping.",
            free_text_b="  P-2  LEFT the BODY, without helping!!  ",
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}

    def test_distinct_rationales_stay_two_independent_voices(self) -> None:
        # The over-collapse guard: genuinely distinct reasoning is two voices
        # (the fold survives) -- echo-dedup only collapses copies.
        transcript = self._two_accusers(
            free_text_a="p-2 was in ADMIN when the kill happened.",
            free_text_b="p-2's timeline does not add up against mine.",
        )

        assert independent_voices(transcript) == {"p-2": ("p-1", "p-3")}

    def test_empty_rationales_never_echo_collapse(self) -> None:
        # An empty / punctuation-only rationale stakes no reasoning to copy,
        # so two backed witnesses who wrote nothing in free-text stay TWO
        # voices -- emptiness is not an echo.
        transcript = self._two_accusers(free_text_a="", free_text_b="...")

        assert independent_voices(transcript) == {"p-2": ("p-1", "p-3")}

    def test_first_speaker_in_canonical_order_keeps_the_voice(self) -> None:
        # Deterministic tie-break: the FIRST speaker (lowest turn index) to
        # stake a rationale keeps the voice; later copies drop, regardless of
        # transcript ordering.
        forward = self._two_accusers(free_text_a="same words", free_text_b="same words")
        reversed_turns = MeetingTranscript(turns=tuple(reversed(forward.turns)))

        assert independent_voices(forward) == {"p-2": ("p-1",)}
        assert independent_voices(reversed_turns) == {"p-2": ("p-1",)}

    def test_opt_in_corroboration_echo_collapses(self) -> None:
        # The second-voice channel echoes too: an opt-in corroboration whose
        # rationale copies the accuser's opening is not an independent voice.
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                    free_text="p-2 fled the scene.",
                ),
                _voice_turn(turn_index=1, speaker="p-2", turn_kind="reply"),
                _voice_turn(
                    turn_index=2,
                    speaker="p-3",
                    turn_kind="opt_in",
                    supports=("p-1",),
                    sightings=(("p-2", "ADMIN", 8),),
                    free_text="p-2 fled the scene.",
                ),
            )
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}

    def test_three_echoing_voters_collapse_to_one(self) -> None:
        # The audit's homogeneity at scale: three distinct backed accusers
        # all copying one rationale are ONE voice, not a deep fold.
        transcript = MeetingTranscript(
            turns=(
                _voice_turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    body=self._BODY,
                    free_text="vote p-2 they are the impostor",
                ),
                _voice_turn(
                    turn_index=1,
                    speaker="p-3",
                    turn_kind="reply",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    free_text="vote p-2 they are the impostor",
                ),
                _voice_turn(
                    turn_index=2,
                    speaker="p-4",
                    turn_kind="reply",
                    accuses=("p-2",),
                    sightings=(("p-2", "ADMIN", 8),),
                    free_text="vote p-2 they are the impostor",
                ),
            )
        )

        assert independent_voices(transcript) == {"p-2": ("p-1",)}


class TestCommittedBytes107VoicePins:
    """The Task 10.7 DoD voice coordinates, walked offline (no re-record)."""

    def test_seed12_m0_derives_no_voice_for_bare_pile_on_p4(self) -> None:
        # THE owner-principle tripwire, pinned SET-WIDE on the Task 18.12 baseline-6
        # re-record (the CREW-ONLY graduation slate). The anti-railroad
        # safety property: a BARE pile-on (a subject with >= 2 distinct accusers,
        # NONE observation-backed) must derive NO independent voice, so the
        # two-witness fold never sees it and a bare pile-on cannot convert. On
        # baseline-3 no bare pile-on existed (every multi-accuser subject was
        # voiced); the leaner Qwen3.6-27B substrate emits fewer observation-backed
        # accusations, so bare pile-ons RE-APPEAR (29 of them on the Task 18.12
        # baseline-6 re-record, pinned below). The mechanism
        # correctly denies EVERY ONE a voice -- that is the whole list of unvoiced
        # multi-accuser subjects, and each is safe (no voice => no conversion). The
        # census is the tripwire: if a future re-record makes one of these bare
        # pile-ons acquire a voice (dropping it from the list, or the rule
        # converting it), STOP and escalate, per the contract. (The positive
        # controls -- where independent_voices DOES derive voices from backed
        # accusers -- are the two-voice and multi-voice yield pins below.)
        multi_accuser_unvoiced: list[tuple[int, int, str]] = []
        multi_accuser_total = 0
        for seed in range(50):
            for meeting_index, entry in enumerate(_committed_meetings(seed)):
                roster = _living_roster(entry)
                if not roster:
                    continue
                voices = independent_voices(entry.transcript, roster=roster)
                accusers: dict[str, set[str]] = {}
                for turn in entry.transcript.turns:
                    for claim in turn.claims:
                        if (
                            isinstance(claim, AccusationClaim)
                            and turn.speaker != claim.against
                        ):
                            accusers.setdefault(claim.against, set()).add(turn.speaker)
                for subject, accs in accusers.items():
                    if len(accs) >= 2:
                        multi_accuser_total += 1
                        if not voices.get(subject):
                            multi_accuser_unvoiced.append(
                                (seed, meeting_index, subject)
                            )
        # The STOP tripwire: these are EXACTLY the bare pile-ons (multi-accuser,
        # no observation-backed accuser), and the mechanism denies every one a
        # voice -- so none can convert via the two-witness fold.
        assert multi_accuser_unvoiced == [
            (1, 0, "p-8"),
            (2, 1, "p-3"),
            (4, 2, "p-9"),
            (6, 1, "p-1"),
            (6, 3, "p-4"),
            (7, 0, "p-2"),
            (7, 0, "p-4"),
            (8, 2, "p-7"),
            (8, 3, "p-4"),
            (12, 1, "p-9"),
            (13, 1, "p-2"),
            (17, 2, "p-5"),
            (18, 1, "p-1"),
            (18, 3, "p-7"),
            (20, 1, "p-8"),
            (21, 2, "p-4"),
            (21, 3, "p-6"),
            (27, 0, "p-3"),
            (33, 1, "p-9"),
            (33, 2, "p-2"),
            (35, 1, "p-2"),
            (36, 0, "p-7"),
            (40, 0, "p-4"),
            (40, 2, "p-1"),
            (42, 1, "p-1"),
            (47, 1, "p-6"),
            (48, 0, "p-6"),
            (48, 1, "p-1"),
            (48, 4, "p-6"),
        ]
        # Non-vacuous: multi-accuser subjects DO occur across the committed set.
        assert multi_accuser_total > 20

    def test_seed16_m2_derives_two_voices_for_p4(self) -> None:
        # Yield-pin (re-anchored to the Task 18.12 baseline-6 re-record -- the
        # CREW-ONLY graduation slate): seed-16 m2 p-9 takes a multi-voice pre-vote
        # fold -- four observation-backed voices under echo-dedup.
        entry = _committed_meetings(16)[2]
        voices = independent_voices(entry.transcript, roster=_living_roster(entry))

        assert voices.get("p-9") == ("p-4", "p-5", "p-6", "p-8")

    def test_seed8_m0_derives_multiple_voices_for_p1(self) -> None:
        # The richer yield shape (re-anchored to the Task 18.12 baseline-6 re-record
        # -- the CREW-ONLY graduation slate): seed-0 m0 p-6 takes a deep pre-vote
        # fold (voices p-1/p-3/p-4/p-5/p-7/p-8/p-9) -- an observation-backed
        # accuser plus aligned corroborations, the richest multi-voice fold in the
        # set on this substrate. (The property is "the mechanism derives a
        # multi-voice fold", not the exact width.)
        entry = _committed_meetings(0)[0]
        voices = independent_voices(entry.transcript, roster=_living_roster(entry))

        assert voices.get("p-6") == ("p-1", "p-3", "p-4", "p-5", "p-7", "p-8", "p-9")
