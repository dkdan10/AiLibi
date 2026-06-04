"""Tests for the transcript helpers (Task 8.7).

Exercises the pure chain logic that backs the reactive accusation chain
(DESIGN.md §5.2) -- :func:`accusation_target`, :func:`next_chain_step`,
:func:`walk_chain` -- plus the chain-turn ordering predicates. The chain
helpers are the single source of truth shared by
:class:`meetings.manager.MeetingManager` (recording) and the replay-walk
(reconstruction), so these tests pin the determinism the replay invariant
relies on. Contradiction detection over ``transcript.turns`` lives in
``test_contradictions.py``.
"""

from __future__ import annotations

import pytest

from meetings.schemas import AccusationClaim, MeetingTranscript, MeetingTurn
from meetings.transcript import (
    accusation_target,
    is_canonically_ordered,
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
