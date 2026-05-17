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
    PlayerId,
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
) -> str:
    """Render the Phase-1 crewmate report prompt (DESIGN.md §5.3)."""

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
) -> str:
    """Render the Phase-1 impostor report prompt (DESIGN.md §4.5, §5.3).

    Conforms to the same :class:`~meetings.manager.ReportPromptRenderer`
    Protocol as :func:`crewmate_report_prompt` so the meeting manager
    can dispatch by role without an extra adapter. The impostor
    template itself does not reference ``agent_id``, ``current_tick``,
    or ``meeting_trigger`` — they are accepted and passed through so
    a future template revision can opt in without breaking call sites.
    """

    return _ENV.get_template(IMPOSTOR_REPORT_TEMPLATE).render(
        agent_id=agent_id,
        current_tick=current_tick,
        meeting_trigger=meeting_trigger,
        rendered_memory=rendered_memory,
        public_transcript=public_transcript,
    )


def accusation_round_prompt(
    *,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
) -> str:
    """Render an accusation-round speech-turn prompt (DESIGN.md §5.2)."""

    return _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
        rendered_memory=rendered_memory,
        transcript=transcript,
        contradictions=contradictions,
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
) -> str:
    """Render a vote-ballot prompt (DESIGN.md §5.5).

    Conforms to the :class:`~meetings.manager.VotePromptRenderer`
    Protocol; the meeting manager invokes this callable verbatim per
    voter to produce the ballot-phase prompt.
    """

    return _ENV.get_template(VOTE_BALLOT_TEMPLATE).render(
        voter_id=voter_id,
        rendered_memory=rendered_memory,
        transcript=transcript,
        contradiction_flags=contradiction_flags,
        suspicion_graph=suspicion_graph,
        candidate_targets=candidate_targets,
        skip_confidence_threshold=skip_confidence_threshold,
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
