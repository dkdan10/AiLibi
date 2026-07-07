"""Leaf home for the meeting prompt-render contract (Task 15.6).

The three prompt-render :class:`~typing.Protocol` types
(:class:`ReportPromptRenderer`, :class:`StatementPromptRenderer`,
:class:`VotePromptRenderer`) and the :class:`SuspicionEntry` DTO they
surface are the SHARED surface between :mod:`meetings.manager` (which
consumes a renderer per prompt) and ``agents/strategic/prompts`` (which
builds the loader callables that conform to these Protocols). They lived
inside 3-KLoC :mod:`meetings.manager` and were imported UPWARD by
``agents/strategic/prompts/loader.py`` -- the last ``agents ↛
meetings.manager`` import edge besides the gate constant. Homing them here,
in a leaf that imports only :mod:`meetings.schemas` (pure typing / pydantic
surface, no manager import), is what makes the ``agents ↛ meetings.manager``
contract satisfiable (audit post-phase-14-pause §3, import contracts):
``agents/`` imports the leaf, not the manager. :mod:`meetings.manager`
imports these back and re-exports them, so every existing
``from meetings.manager import ...`` call site keeps working.

Keep this module a leaf: import only from :mod:`meetings.schemas` and the
stdlib. It must never import :mod:`meetings.manager` (that would re-create
the cycle the split exists to break).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    TurnKind,
)


@dataclass(frozen=True)
class SuspicionEntry:
    """One row of the agent's suspicion graph (DESIGN.md §5.5).

    Surfaced verbatim into the vote-ballot prompt. The fields mirror
    :class:`agents.memory.beliefs.PlayerBelief` so a belief snapshot maps
    into this DTO without re-shaping it.
    """

    player_id: PlayerId
    suspicion: float
    trust: float


@runtime_checkable
class ReportPromptRenderer(Protocol):
    """Render the opening-turn prompt (DESIGN.md §5.2 PHASE 1, §5.3).

    The manager dispatches to the crewmate or impostor renderer based on
    the opener's :attr:`MeetingParticipant.role`. The opening turn IS the
    body report: the reporter states findings (observations) and accuses
    one player or declares "unsure". ``public_transcript`` is the empty
    string at the opening since no turn precedes it.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate list
    surfaced into the impostor opening prompt so the model never accuses /
    incriminates a teammate. It is ``()`` for a crewmate and a sole
    impostor; the crewmate template ignores it.

    ``living_ids`` (Task 9.9, audit gp-3) is the living-roster accusation
    list -- living participants minus the speaker, the turn-side mirror of
    the vote ballot's ``candidate_targets`` -- rendered so the model never
    wastes its opening accusing a dead / ejected player. ``()`` (ad-hoc
    renders) omits the roster block.

    ``dead_ids`` (Task 10.3, audit gp-9 H-H-3/D-D-8) is the negative
    list: the dead / ejected players, rendered as an explicit
    do-not-accuse line under the living roster. The living-roster block
    alone left "who is dead" implicit and 17/18 hallucinated accusation
    targets named a dead real player. ``()`` (ad-hoc renders) omits the
    line.
    """

    def __call__(
        self,
        *,
        agent_id: PlayerId,
        current_tick: int,
        meeting_trigger: str,
        rendered_memory: str,
        public_transcript: str,
        fellow_impostor_ids: tuple[PlayerId, ...] = (),
        living_ids: tuple[PlayerId, ...] = (),
        dead_ids: tuple[PlayerId, ...] = (),
    ) -> str: ...


@runtime_checkable
class StatementPromptRenderer(Protocol):
    """Render a reactive ``reply`` / ``opt_in`` turn prompt (DESIGN.md §5.2).

    Grows two inputs over the old fixed-round statement renderer (Task
    8.7): ``prior_turn`` is the accusing turn this speaker answers (the
    "who accused me" context; ``None`` for an opt-in info-share turn), and
    ``turn_kind`` is ``"reply"`` or ``"opt_in"`` so the template can frame
    the turn correctly. ``transcript`` is the transcript-so-far in chain
    order; ``contradictions`` are the §5.4 flags warranted by the claims
    made up to this turn.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate list;
    the shared template renders a teammate block only when it is non-empty,
    so a crewmate / sole-impostor prompt is byte-unchanged.

    ``living_ids`` (Task 9.9, audit gp-3) is the living-roster accusation
    list -- living participants minus the speaker, the turn-side mirror of
    the vote ballot's ``candidate_targets`` -- rendered so a reply / opt-in
    accusation stays on the living roster. ``()`` (ad-hoc renders) omits
    the roster block.

    ``dead_ids`` (Task 10.3, audit gp-9 H-H-3/D-D-8) is the dead /
    ejected negative list rendered as an explicit do-not-accuse line
    under the living roster (17/18 hallucinated targets were dead real
    players). ``()`` (ad-hoc renders) omits the line.

    ``is_impostor`` (Task 11.2) gates the cover-consistency directive on
    the reply branch (commit to ONE sheltered room + tick-window away from
    the body and reuse it every turn). It is an explicit bool rather than a
    reuse of ``fellow_impostor_ids`` because a SOLE impostor has empty
    fellows but must still get the directive. The default ``False`` keeps
    the crewmate (and ad-hoc) render byte-unchanged.

    ``is_body_report`` (Task 11.2; PR #159 review) is the second gate on the
    cover directive: it speaks of "the body's room and the tick it happened",
    so -- mirroring ``impostor_report.j2``'s ``body_report_opening`` gate -- it
    must fire only when a body is on the table, never on a body-less emergency
    reply. The default ``False`` keeps the block off unless the caller marks the
    meeting a body report.
    """

    def __call__(
        self,
        *,
        agent_id: PlayerId,
        rendered_memory: str,
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
        prior_turn: MeetingTurn | None,
        turn_kind: TurnKind,
        fellow_impostor_ids: tuple[PlayerId, ...] = (),
        living_ids: tuple[PlayerId, ...] = (),
        dead_ids: tuple[PlayerId, ...] = (),
        is_impostor: bool = False,
        is_body_report: bool = False,
    ) -> str: ...


@runtime_checkable
class VotePromptRenderer(Protocol):
    """Render a vote-ballot prompt (DESIGN.md §5.5).

    ``candidate_targets`` is the explicit set of living eject targets
    (every living participant except the voter); ``skip_confidence_threshold``
    matches :attr:`MeetingConfig.skip_confidence_threshold`. ``transcript``
    is the full chain transcript.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate list;
    the shared ballot template renders a teammate block only when it is
    non-empty (instructing the impostor to SKIP rather than vote a
    teammate), so a crewmate / sole-impostor prompt is byte-unchanged.
    """

    def __call__(
        self,
        *,
        voter_id: PlayerId,
        rendered_memory: str,
        transcript: MeetingTranscript,
        contradiction_flags: tuple[ContradictionRef, ...],
        suspicion_graph: tuple[SuspicionEntry, ...],
        candidate_targets: tuple[PlayerId, ...],
        skip_confidence_threshold: float,
        fellow_impostor_ids: tuple[PlayerId, ...] = (),
    ) -> str: ...


__all__ = [
    "ReportPromptRenderer",
    "StatementPromptRenderer",
    "SuspicionEntry",
    "VotePromptRenderer",
]
