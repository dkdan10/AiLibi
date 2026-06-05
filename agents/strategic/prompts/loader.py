"""Jinja loader for the four strategic prompt templates (Task 3.9 C-4).

The four ``.j2`` templates under ``agents/strategic/prompts/`` are the
canonical phase-1 report, accusation-round, and vote-ballot prompts
consumed by :class:`agents.strategic.reasoner.StrategicReasoner` and
:class:`meetings.manager.MeetingManager`. This module wraps them in a
single strict-undefined :class:`jinja2.Environment` and exposes one named
Python callable per template so the wider codebase never touches the
filesystem directly.

Strict-undefined behavior
=========================

The :class:`jinja2.StrictUndefined` policy means a missing or typo'd
template kwarg raises :class:`jinja2.UndefinedError` at render time
instead of silently rendering an empty string. ``trim_blocks=True`` /
``lstrip_blocks=True`` keep the rendered Markdown free of stray
whitespace that the templates' own ``{%- ... -%}`` markers already
intend. ``autoescape=False`` is correct here because the prompts are
plain-text LLM input, not HTML.

Templates remain frozen
=======================

The four ``.j2`` files are out of scope for Task 3.9 — the loader reads
them as-is. If a template needs a new kwarg, the wrapper callable's
signature is updated here; the template itself is not edited from this
module.

Per-template wrapper signatures
===============================

Each wrapper conforms to the :class:`~meetings.manager.ReportPromptRenderer`,
:class:`~meetings.manager.StatementPromptRenderer`, or
:class:`~meetings.manager.VotePromptRenderer` Protocol from
:mod:`meetings.manager` so the loader-built callables can be passed
straight into :class:`~meetings.manager.MeetingManager` without an
intermediate adapter layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from meetings.manager import SuspicionEntry
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    TurnKind,
)

_TEMPLATE_DIR: Final[Path] = Path(__file__).resolve().parent

_ENV: Final[Environment] = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)

CREWMATE_REPORT_TEMPLATE: Final[str] = "crewmate_report.j2"
IMPOSTOR_REPORT_TEMPLATE: Final[str] = "impostor_report.j2"
ACCUSATION_ROUND_TEMPLATE: Final[str] = "accusation_round.j2"
VOTE_BALLOT_TEMPLATE: Final[str] = "vote_ballot.j2"


def crewmate_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    """Render the Phase-1 crewmate report prompt (DESIGN.md §5.3).

    ``fellow_impostor_ids`` (Task 7.12) is accepted so this wrapper
    conforms to the same :class:`~meetings.manager.ReportPromptRenderer`
    Protocol as :func:`impostor_report_prompt` and the meeting manager
    can dispatch by role without an adapter. A crewmate has no teammate
    list (the value is always ``()``) and the crewmate template never
    references it, so the rendered prompt is byte-unchanged.
    """

    return _ENV.get_template(CREWMATE_REPORT_TEMPLATE).render(
        agent_id=agent_id,
        current_tick=current_tick,
        meeting_trigger=meeting_trigger,
        rendered_memory=rendered_memory,
        public_transcript=public_transcript,
    )


def impostor_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    """Render the Phase-1 impostor report prompt (DESIGN.md §4.5, §5.3).

    Conforms to the same :class:`~meetings.manager.ReportPromptRenderer`
    Protocol as :func:`crewmate_report_prompt` so the meeting manager
    can dispatch by role without an extra adapter. The impostor
    template itself does not reference ``agent_id``, ``current_tick``,
    or ``meeting_trigger`` — they are accepted and passed through so
    a future template revision can opt in without breaking call sites.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor's teammate list;
    the template renders the "never accuse / incriminate a teammate"
    block only when it is non-empty, so a sole impostor (``()``) gets a
    byte-unchanged prompt.
    """

    return _ENV.get_template(IMPOSTOR_REPORT_TEMPLATE).render(
        agent_id=agent_id,
        current_tick=current_tick,
        meeting_trigger=meeting_trigger,
        rendered_memory=rendered_memory,
        public_transcript=public_transcript,
        fellow_impostor_ids=fellow_impostor_ids,
    )


def accusation_round_prompt(
    *,
    agent_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
    prior_turn: MeetingTurn | None,
    turn_kind: TurnKind,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    """Render a reactive ``reply`` / ``opt_in`` turn prompt (DESIGN.md §5.2).

    Conforms to the :class:`~meetings.manager.StatementPromptRenderer`
    Protocol so the meeting manager and strategic reasoner can invoke it
    for every reactive-chain and opt-in turn without an adapter.

    Task 8.8 grew two inputs over the old fixed-round statement renderer:

    * ``prior_turn`` is the accusing turn this speaker answers -- the
      "who accused me" context. It is the prior chain turn on a
      ``reply`` and ``None`` on an opt-in info-share turn.
    * ``turn_kind`` is ``"reply"`` or ``"opt_in"`` so the template frames
      the turn correctly (the opt-in turn is terminal and never extends
      the chain).

    ``transcript`` is the transcript-so-far in chain order (its ``turns``
    tuple); ``contradictions`` are the §5.4 flags warranted up to this
    turn. ``agent_id`` is threaded into the template so the self-alibi
    example renders the speaker's own canonical player id (e.g.
    ``"subject": "p-3"``) rather than a placeholder the model might
    mis-substitute, keeping DESIGN.md §5.4 contradiction detection able to
    match self-alibis across speakers.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate
    list; the template renders the "never target a teammate" block only
    when it is non-empty, so a crewmate / sole-impostor turn (``()``) is
    byte-unchanged.
    """

    return _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
        agent_id=agent_id,
        rendered_memory=rendered_memory,
        transcript=transcript,
        contradictions=contradictions,
        prior_turn=prior_turn,
        turn_kind=turn_kind,
        fellow_impostor_ids=fellow_impostor_ids,
    )


def vote_ballot_prompt(
    *,
    voter_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradiction_flags: tuple[ContradictionRef, ...],
    suspicion_graph: tuple[SuspicionEntry, ...],
    candidate_targets: tuple[PlayerId, ...],
    skip_confidence_threshold: float,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    """Render a vote-ballot prompt (DESIGN.md §5.5).

    Conforms to the :class:`~meetings.manager.VotePromptRenderer`
    Protocol; the meeting manager invokes this callable verbatim per
    voter to produce the ballot-phase prompt.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate
    list; the template renders the "never vote a teammate — SKIP
    instead" block only when it is non-empty, so a crewmate /
    sole-impostor ballot (``()``) is byte-unchanged.
    """

    return _ENV.get_template(VOTE_BALLOT_TEMPLATE).render(
        voter_id=voter_id,
        rendered_memory=rendered_memory,
        transcript=transcript,
        contradiction_flags=contradiction_flags,
        suspicion_graph=suspicion_graph,
        candidate_targets=candidate_targets,
        skip_confidence_threshold=skip_confidence_threshold,
        fellow_impostor_ids=fellow_impostor_ids,
    )


__all__ = [
    "ACCUSATION_ROUND_TEMPLATE",
    "CREWMATE_REPORT_TEMPLATE",
    "IMPOSTOR_REPORT_TEMPLATE",
    "VOTE_BALLOT_TEMPLATE",
    "accusation_round_prompt",
    "crewmate_report_prompt",
    "impostor_report_prompt",
    "vote_ballot_prompt",
]
