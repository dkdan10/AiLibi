"""Aboutness: whether a ballot's citation bears on the player that ballot names.

ONE definition, in the meeting layer, because two callers ask the same question
of the same ballot and a run is unreadable if they can answer it differently:

* :func:`meetings.manager.guard_ballot_citation` asks it at recording time, to
  decide whether an EJECT may stand on the citation it carries (only while the
  ``citation_relevance_version`` lever is ON);
* ``experiments.fresh_deduction_instrument.grade_citation_relevance`` asks it
  afterwards, as the third conjunct of the deduction instrument's primary
  outcome.

The rule used to live in the instrument alone, which is why the guard's own
docstring could describe the gap as a scope choice: the gate enforced citation
VALIDITY (the id resolves) and never relevance (the thing it resolves to is
about the accused). Moving it here is what lets the guard ask, because
``meetings/`` may not import ``experiments/`` -- the firewall interior is
``{agents, llm, meetings, observation}`` and ``experiments`` is ungraphed, so
``tests/test_firewall.py``'s closure scan forbids that direction outright while
the instrument may import ``meetings`` freely.

Surfaces are the CALLER'S business. The cited-line rule takes already-split
LINES rather than prompts, because the two callers hold different surfaces: the
guard holds the voter's rendered ballot prompt at the moment it runs, the
grader holds every prompt that voter received during the unit. Splitting here
would force one of them to fake the other's surface.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Final

from meetings.schemas import MeetingTurn, PlayerId

#: A player id is a whole token: ``p-1`` must not match inside ``p-10``. The
#: class is the id alphabet plus ``-``, so neither a longer id nor a trailing
#: ``-2`` suffix can satisfy a shorter one.
PLAYER_TOKEN: Final[str] = r"(?<![0-9A-Za-z_-]){player}(?![0-9A-Za-z_-])"


def names_player(text: str, player: str) -> bool:
    """Whether ``text`` names ``player`` as a whole id rather than as a prefix."""

    return re.search(PLAYER_TOKEN.format(player=re.escape(player)), text) is not None


def every_string_in(value: object) -> list[str]:
    """Every string anywhere in a dumped structure, keys included.

    Walking the DUMPED STRUCTURE rather than the JSON text is what makes the
    match honest: a name inside a string field survives ``model_dump_json`` as
    an ESCAPED substring, so a search over the encoded text can read a name the
    field does not carry, and miss one it does.

    Deliberately a second copy of the instrument's ``_every_string_in``, which
    stays where it is because it also serves the held-out leak scan: this one
    is inside the firewall interior and that one is not, and importing across
    that line is exactly what this module exists to avoid. A test asserts the
    two walkers agree on a dumped :class:`~meetings.schemas.MeetingTurn`.
    """

    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        found: list[str] = []
        for key, item in value.items():
            if isinstance(key, str):
                found.append(key)
            found.extend(every_string_in(item))
        return found
    if isinstance(value, (list, tuple)):
        return [text for item in value for text in every_string_in(item)]
    return []


def turn_bears_on(turn: MeetingTurn, player: PlayerId) -> bool:
    """Whether a recorded turn is the player's own or names them in its content.

    The content is walked as the DUMPED STRUCTURE (:func:`every_string_in`)
    rather than field by field: a turn carries a dozen observation and claim
    shapes, each naming players under a different key (``subject``, ``against``,
    ``supports``, ``body_of``, ``co_present``), and a rule enumerating them
    would silently stop covering the ones a later schema adds.
    """

    if turn.speaker == player:
        return True
    return any(
        names_player(text, player)
        for text in every_string_in(turn.model_dump(mode="json"))
    )


def cited_line_names(lines: Sequence[str], *, citation: str, player: PlayerId) -> bool:
    """Whether a LINE carrying ``citation`` also names ``player``.

    The line is the unit because the rendered memory prints one observation per
    line: an id and a name in the same line are the same record, an id and a
    name in the same prompt are not.
    """

    return any(citation in line and names_player(line, player) for line in lines)


def citations_bear_on(
    *,
    cited_turn_id: str | None,
    cited_observation_id: str | None,
    subject: PlayerId,
    turns_by_id: Mapping[str, MeetingTurn],
    lines: Sequence[str],
) -> bool:
    """Whether the citations a ballot DOES carry bear on ``subject``.

    The composition both callers use, so neither can compose it differently.
    Vacuously true when neither channel is cited: aboutness is a test of what a
    citation says, and an uncited ballot is the citation gate's other business
    (:func:`meetings.manager.guard_ballot_citation`) and the grader's own
    ``uncited`` verdict.

    A cited turn id that resolves to no turn is NOT relevant. At the guard's
    call site the upstream validator has already nulled every unresolvable id,
    so that branch is the grader's -- it grades recorded bytes, where a caller
    may hold a partial turn set.
    """

    if cited_turn_id is not None:
        turn = turns_by_id.get(cited_turn_id)
        if turn is None or not turn_bears_on(turn, subject):
            return False
    if cited_observation_id is not None:
        return cited_line_names(lines, citation=cited_observation_id, player=subject)
    return True
