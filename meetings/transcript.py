"""Meeting transcript helpers (DESIGN.md §5.2, §5.4).

This module currently hosts the statement-ordering helpers that
:class:`meetings.manager.MeetingManager` produces under the
producer-guaranteed canonical order contract (Task 3.8 C-3 resolution,
audit ``audits/audit-2026-05-16-0611-claude.md``).

Task 3.11 will add :func:`detect_contradictions` here per DESIGN.md
§5.4; that work is intentionally out of scope for Task 3.8.

Canonical statement order
=========================

A meeting transcript stores ``statements`` as a tuple. The canonical
order is:

* ascending :attr:`meetings.schemas.Statement.round_index`, then
* ascending insertion order within a round (i.e. the order in which
  participants submitted their statements, or were recorded with a
  default no-statement entry on deadline).

:class:`meetings.manager.MeetingManager` emits statements directly in
this order, so consumers may read ``transcript.statements`` in tuple
order without re-sorting. :func:`sort_statements_canonically` is
exposed for external producers (e.g. a future replay reconstructor)
that need to normalise a transcript they assembled out of order; it
uses a stable sort so insertion order within a round is preserved.
"""

from __future__ import annotations

from collections.abc import Iterable

from meetings.schemas import Statement


def sort_statements_canonically(
    statements: Iterable[Statement],
) -> tuple[Statement, ...]:
    """Return ``statements`` sorted by canonical ``(round_index, insertion_order)``.

    The sort is stable: within a round the input order is preserved.
    Manager-produced transcripts are already canonically ordered; this
    helper exists for external producers that need to normalise a
    transcript assembled out of order.
    """

    return tuple(sorted(statements, key=lambda statement: statement.round_index))


def is_canonically_ordered(statements: Iterable[Statement]) -> bool:
    """Return ``True`` if ``statements`` is sorted by ``round_index``.

    "Insertion order within a round" is, by definition, the tuple's
    own order, so this predicate cannot check it -- it only verifies
    the cross-round invariant. ``MeetingManager`` is the contract
    holder for the insertion-order half; downstream consumers may use
    this predicate as a cheap pre-condition check before processing
    a transcript.
    """

    last_round = -1
    for statement in statements:
        if statement.round_index < last_round:
            return False
        last_round = statement.round_index
    return True


__all__ = [
    "is_canonically_ordered",
    "sort_statements_canonically",
]
