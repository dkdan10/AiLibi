"""Tests for the transcript helpers (Task 3.8).

Task 3.11 will add ``detect_contradictions`` and its tests here. For
Task 3.8 we only exercise the statement-ordering helpers
(:func:`meetings.transcript.sort_statements_canonically` and
:func:`meetings.transcript.is_canonically_ordered`) that back the C-3
ordering contract documented on :class:`meetings.manager.MeetingManager`.
"""

from __future__ import annotations

from meetings.schemas import Statement
from meetings.transcript import (
    is_canonically_ordered,
    sort_statements_canonically,
)


def _statement(
    *,
    statement_id: str,
    round_index: int,
    speaker: str = "p-1",
) -> Statement:
    return Statement(
        statement_id=statement_id,
        speaker=speaker,
        tick=100,
        round_index=round_index,
        target=None,
        claims=(),
        free_text=f"stub statement {statement_id}",
    )


class TestSortStatementsCanonically:
    def test_empty_returns_empty_tuple(self) -> None:
        assert sort_statements_canonically([]) == ()

    def test_already_sorted_input_is_passthrough(self) -> None:
        statements = (
            _statement(statement_id="s0", round_index=0),
            _statement(statement_id="s1", round_index=0),
            _statement(statement_id="s2", round_index=1),
        )

        result = sort_statements_canonically(statements)

        # Stable sort over an already-sorted input preserves order
        # byte-for-byte.
        assert result == statements

    def test_groups_statements_by_round_in_ascending_order(self) -> None:
        # Round 1's two entries are deliberately placed before round 0's
        # two entries so that a non-stable or wrongly-keyed sort would
        # scramble them.
        round_one_a = _statement(statement_id="r1-a", round_index=1)
        round_one_b = _statement(statement_id="r1-b", round_index=1)
        round_zero_a = _statement(statement_id="r0-a", round_index=0)
        round_zero_b = _statement(statement_id="r0-b", round_index=0)

        result = sort_statements_canonically(
            [round_one_a, round_one_b, round_zero_a, round_zero_b]
        )

        assert result == (round_zero_a, round_zero_b, round_one_a, round_one_b)

    def test_within_round_order_is_stable(self) -> None:
        # Within a round, the original insertion order must be
        # preserved -- this is the "insertion_order" half of the C-3
        # contract.
        first = _statement(statement_id="alpha", round_index=0, speaker="p-9")
        second = _statement(statement_id="bravo", round_index=0, speaker="p-1")
        third = _statement(statement_id="charlie", round_index=0, speaker="p-5")

        result = sort_statements_canonically([first, second, third])

        # Sorting must NOT reorder within a round by speaker, statement
        # id, or anything else -- insertion order is the contract.
        assert result == (first, second, third)


class TestIsCanonicallyOrdered:
    def test_empty_is_canonically_ordered(self) -> None:
        assert is_canonically_ordered([]) is True

    def test_ascending_rounds_are_canonical(self) -> None:
        statements = (
            _statement(statement_id="s0", round_index=0),
            _statement(statement_id="s1", round_index=0),
            _statement(statement_id="s2", round_index=1),
            _statement(statement_id="s3", round_index=2),
        )

        assert is_canonically_ordered(statements) is True

    def test_round_regression_is_not_canonical(self) -> None:
        # A round-1 statement followed by a round-0 statement breaks
        # the contract; the predicate must catch it so consumers can
        # treat it as a tripwire.
        statements = (
            _statement(statement_id="s0", round_index=1),
            _statement(statement_id="s1", round_index=0),
        )

        assert is_canonically_ordered(statements) is False
