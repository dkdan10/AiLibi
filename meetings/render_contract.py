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

Observation shapes a turn may answer with
========================================

The renderers above show the transcript and take the model's structured turn
back, so the shapes a turn may carry are part of this contract:
:class:`~meetings.schemas.SawPlayerObservation` (a player at a room and tick),
:class:`~meetings.schemas.SawMoveObservation` (a witnessed transition -- that
player moved from one room to another, arriving at the tick),
:class:`~meetings.schemas.CompletedTaskObservation`,
:class:`~meetings.schemas.FoundBodyObservation`,
:class:`~meetings.schemas.SawVentObservation` and
:class:`~meetings.schemas.WhereaboutsClaim` (the speaker's own placement).

The turn schema accepts a transition unconditionally. The ``qwen3_6_27b`` v4
turn templates list the shape, so a model served that set can answer with one;
every other set is silent about it and its speakers cannot. The meeting layer
reads a spoken transition through
:func:`meetings.transcript.movement_claim_shape_enabled`, which graduated at the
baseline-7 record: a stated transition now grounds a placement on every path.
Before that graduation it recorded as ordinary testimony and grounded nothing,
which is what the pre-baseline-7 committed bytes hold.

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

    Surfaced verbatim into the vote-ballot prompt. The ``player_id`` /
    ``suspicion`` / ``trust`` fields mirror
    :class:`agents.memory.beliefs.PlayerBelief` so a belief snapshot maps
    into this DTO without re-shaping it.

    Provenance decomposition (Task 16.3). The eight trailing float fields
    mirror :class:`agents.memory.beliefs.SuspicionProvenance` FIELD-BY-NAME --
    NOT by import: this module is the leaf that breaks the ``agents ↛
    meetings.manager`` cycle (see the module docstring), so it must never
    import ``agents.*``. They decompose ``suspicion`` into its source channels
    (``_DEFAULT_SUSPICION + sum(the eight) == suspicion`` within the belief
    module's :data:`~agents.memory.beliefs.SUSPICION_PROVENANCE_ATOL`),
    populated by :meth:`orchestrator.game.TacticalAgent.suspicion_graph_for_meeting`
    from ``belief.provenance`` and re-seeded through the manager's pre-vote fold
    (:func:`meetings.manager._suspicion_graph_with_contradictions`). All default
    to ``0.0`` and are additive/trailing, so every existing construction stays
    valid and a row built without them decomposes as "wholly unattributed"
    (0.0 in every channel). No template renders them yet -- Task 16.15 is the
    provenance surface; until then they ride inert (the widen-the-contract-inert
    pattern, the 15.5 reporter-lever precedent).
    """

    player_id: PlayerId
    suspicion: float
    trust: float
    flag_lift: float = 0.0
    body_proximity: float = 0.0
    kill_or_vent_pin: float = 0.0
    testimony_spread: float = 0.0
    accusation_carry: float = 0.0
    carried_hard: float = 0.0
    carried_soft: float = 0.0
    unattributed: float = 0.0


@dataclass(frozen=True)
class PromptRenderInputs:
    """The two facts about THIS game and THIS map the v4 templates state.

    Both are public knowledge, so neither leaks anything into a crewmate's
    prompt:

    * ``impostor_count`` is the roster preset's own impostor count (the "2i" of
      ``9p2i``) — stated in the design, in every set name, and on the spectator
      surface. It is the count the game was SEEDED with, not the count still
      alive, so it never moves mid-game and an ejection reveals nothing through
      it. The templates use it to say how many hidden impostors there are and to
      state the win condition (impostors win once they equal the crew) with the
      right arithmetic; ``None`` means the caller did not thread it and the
      templates keep their singular wording.
    * ``map_card`` is the pre-rendered room-and-doorway card
      (:func:`agents.strategic.prompts.loader.render_map_card`). It is a
      constant of the canonical map and carries WALKABLE adjacency only — vent
      topology is impostor-only knowledge and must never appear here. ``""``
      renders no card.

    Threaded as one additive, defaulted keyword on the three renderer Protocols
    below, so every existing call site stays valid and every render that omits
    it is byte-identical.
    """

    impostor_count: int | None = None
    map_card: str = ""


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

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the two inert
    trailing widenings the foundation lands once so the later render levers
    edit ONLY templates (the widen-the-contract-inert pattern; the 15.5
    ``reporter_id`` lever is the precedent). The default ``""`` / ``()`` keep
    every current render byte-identical (jinja ignores a kwarg no template
    references), which the prompt-byte golden pins.

    ``render_inputs`` (Task 20.31) carries the game's impostor count and the
    map card the v4 ``qwen3_6_27b`` templates state. ``None`` -- every caller
    that does not thread it -- renders exactly as before.
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
        persona: str = "",
        suspicion_provenance: tuple[SuspicionEntry, ...] = (),
        render_inputs: PromptRenderInputs | None = None,
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

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the two inert
    trailing widenings the foundation lands once (the widen-the-contract-inert
    pattern; the 15.5 ``reporter_id`` lever precedent). The default ``""`` /
    ``()`` keep every current render byte-identical, pinned by the prompt-byte
    golden.

    ``render_inputs`` (Task 20.31) carries the game's impostor count and the
    map card the v4 ``qwen3_6_27b`` templates state. ``None`` -- every caller
    that does not thread it -- renders exactly as before.
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
        persona: str = "",
        suspicion_provenance: tuple[SuspicionEntry, ...] = (),
        render_inputs: PromptRenderInputs | None = None,
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

    ``reporter_id`` (Task 15.5, the reporter-exculpation lever) is the
    body-report meeting's own reporter -- the manager threads
    :attr:`meetings.manager.MeetingTrigger.triggered_by`, but ONLY when the
    default-OFF ``reporter_exculpation`` lever is ON and the meeting is a body
    report. The template renders the base-rate annotation ("p-N reported the
    body; self-report is weakly exculpatory in this game") only when it is
    non-``None``. The default ``None`` -- lever OFF, an emergency call, or any
    ad-hoc render -- omits the block, so a lever-OFF ballot prompt is
    byte-identical (the Voice-doc 15.0 widen-the-contract-inert pattern). This is
    the render mirror of the belief-side damp in
    :func:`agents.memory.beliefs.apply_meeting_evidence_rules`; both read the one
    :func:`agents.memory.beliefs.reporter_exculpation_enabled` resolver so the
    damped suspicion graph and the annotation cannot disagree.

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the two inert
    trailing widenings the foundation lands once (the widen-the-contract-inert
    pattern; the 15.5 ``reporter_id`` lever precedent). On the ballot the manager
    threads the SAME post-fold rows into ``suspicion_provenance`` as into
    ``suspicion_graph`` -- the render-after-fold consistency pin -- so 16.15's
    surface decomposes exactly the scalars this prompt already shows. The default
    ``""`` / ``()`` keep every current render byte-identical, pinned by the
    prompt-byte golden.

    ``render_inputs`` (Task 20.31) carries the game's impostor count and the
    map card the v4 ``qwen3_6_27b`` templates state. ``None`` -- every caller
    that does not thread it -- renders exactly as before.
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
        reporter_id: PlayerId | None = None,
        persona: str = "",
        suspicion_provenance: tuple[SuspicionEntry, ...] = (),
        render_inputs: PromptRenderInputs | None = None,
    ) -> str: ...


__all__ = [
    "PromptRenderInputs",
    "ReportPromptRenderer",
    "StatementPromptRenderer",
    "SuspicionEntry",
    "VotePromptRenderer",
]
