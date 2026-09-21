"""Aboutness: whether a ballot's citation bears on the player that ballot names.

ONE definition, in the meeting layer, because two callers ask the same question
of the same ballot and a run is unreadable if they can answer it differently:

* :func:`meetings.manager.label_ballot_grounding` asks it at recording time, to
  decide whether a ballot's surviving citation reads ``supported`` or
  ``off_target``. Unconditional since ruling D6 of 2026-09-19 retired the
  ``citation_relevance_version`` lever: the rule is the default, and the LABEL
  is all it decides -- no target moves either way;
* ``experiments.fresh_deduction_instrument.grade_citation_relevance`` asks it
  afterwards, as the third conjunct of the deduction instrument's primary
  outcome.

The rule used to live in the instrument alone, which is why the recording-time
gate could describe the gap as a scope choice: it enforced citation VALIDITY
(the id resolves) and never relevance (the thing it resolves to is about the
accused). Moving it here is what lets the meeting layer ask, because
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

#: A CITATION is a whole token for the same reason, and the reason bites harder:
#: an observation id is ``{agent}:{tick}:{seq}``
#: (:func:`agents.memory.episodic.derive_observation_id`), so ``p-1:4:1`` is a
#: string prefix of ``p-1:4:10`` the moment a voter's tenth observation of that
#: tick renders. A substring test would let the LONGER id's line answer for the
#: SHORTER id's citation -- and the gate would fail OPEN on exactly the class it
#: exists to close, because that other line is the one naming somebody else. The
#: class is the player alphabet plus ``:``, the only characters that can extend
#: an id on either side.
CITATION_TOKEN: Final[str] = r"(?<![0-9A-Za-z_:-]){citation}(?![0-9A-Za-z_:-])"


def names_player(text: str, player: str) -> bool:
    """Whether ``text`` names ``player`` as a whole id rather than as a prefix."""

    return re.search(PLAYER_TOKEN.format(player=re.escape(player)), text) is not None


def carries_citation(text: str, citation: str) -> bool:
    """Whether ``text`` carries ``citation`` as a whole id rather than as a prefix.

    The citation twin of :func:`names_player`, and deliberately a boundary rule
    rather than a match on the rendered ``[obs {id}] `` wrapper
    (:func:`agents.memory.store.render_for_prompt`): the wrapper is render
    dressing that a caller's surface may or may not carry, while the id is what
    a ballot actually cites.
    """

    return (
        re.search(CITATION_TOKEN.format(citation=re.escape(citation)), text) is not None
    )


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

    BOTH halves are whole-token matches (:func:`carries_citation`,
    :func:`names_player`). A substring test on either half reads a record the
    line does not hold: ``p-1`` inside ``p-10`` on the name half, and the line
    of ``p-1:4:10`` answering for a citation of ``p-1:4:1`` on the id half.
    """

    return any(
        carries_citation(line, citation) and names_player(line, player)
        for line in lines
    )


def citations_bear_on_any(
    *,
    cited_turn_id: str | None,
    cited_observation_id: str | None,
    subjects: Sequence[PlayerId],
    turns_by_id: Mapping[str, MeetingTurn],
    lines: Sequence[str],
) -> bool:
    """Whether the citations a ballot DOES carry bear on ANY of ``subjects``.

    The composition every caller uses, so none can compose it differently. The
    multi-subject shape is what lets a SKIP be assessed at all: an EJECT names
    one player, but a SKIP names none, so its subject is the pool it weighed
    (:func:`meetings.manager._ballot_grounding_subjects`). A citation that bears
    on ONE member of that pool is a basis for the decision -- the voter
    considered those players and cited something about one of them.

    Vacuously true when neither channel is cited, exactly as the one-subject
    case has always been: aboutness is a test of what a citation SAYS, and an
    uncited ballot is the labeller's other business
    (:func:`meetings.manager.label_ballot_grounding`) and the grader's own
    ``uncited`` verdict. That branch is taken BEFORE ``subjects`` is read, so an
    uncited ballot answers ``True`` even against an empty pool.

    With a citation present and ``subjects`` empty there is no subject for it to
    bear on, so the answer is ``False``. The production call site cannot reach
    that: a vote is only collected while at least one candidate is living, so a
    SKIP that weighed nothing still carries the living pool.

    A cited turn id that resolves to no turn is NOT relevant, for every subject.
    At the labeller's call site the upstream validator has already nulled every
    unresolvable id, so that branch is the grader's -- it grades recorded bytes,
    where a caller may hold a partial turn set.
    """

    if cited_turn_id is None and cited_observation_id is None:
        return True
    return any(
        _citations_bear_on_one(
            cited_turn_id=cited_turn_id,
            cited_observation_id=cited_observation_id,
            subject=subject,
            turns_by_id=turns_by_id,
            lines=lines,
        )
        for subject in subjects
    )


def _citations_bear_on_one(
    *,
    cited_turn_id: str | None,
    cited_observation_id: str | None,
    subject: PlayerId,
    turns_by_id: Mapping[str, MeetingTurn],
    lines: Sequence[str],
) -> bool:
    """One subject's half of :func:`citations_bear_on_any`.

    BOTH cited channels must bear on the SAME subject when both are present:
    the ballot offers them as one basis, so a turn about ``p-1`` paired with an
    observation about ``p-2`` bears on neither.
    """

    if cited_turn_id is not None:
        turn = turns_by_id.get(cited_turn_id)
        if turn is None or not turn_bears_on(turn, subject):
            return False
    if cited_observation_id is not None:
        return cited_line_names(lines, citation=cited_observation_id, player=subject)
    return True


def citations_bear_on(
    *,
    cited_turn_id: str | None,
    cited_observation_id: str | None,
    subject: PlayerId,
    turns_by_id: Mapping[str, MeetingTurn],
    lines: Sequence[str],
) -> bool:
    """Whether the citations a ballot DOES carry bear on ``subject``.

    The ONE-SUBJECT case of :func:`citations_bear_on_any`, and literally that
    call: the rule has one definition, so the grader's single-subject question
    and the labeller's pooled one can never be answered differently.
    """

    return citations_bear_on_any(
        cited_turn_id=cited_turn_id,
        cited_observation_id=cited_observation_id,
        subjects=(subject,),
        turns_by_id=turns_by_id,
        lines=lines,
    )
