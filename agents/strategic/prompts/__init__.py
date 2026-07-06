"""Strategic prompt templates (DESIGN.md §5.2, §5.3, §5.5, §6.6).

The four Jinja2 templates next to this module are loaded by
:mod:`agents.strategic.prompts.loader` and exposed as named callables —
one per template — that ``MeetingManager`` imports from here.
"""

from __future__ import annotations

from agents.strategic.prompts.loader import (
    ACCUSATION_ROUND_TEMPLATE,
    CREWMATE_REPORT_TEMPLATE,
    DEFAULT_PROMPT_SET,
    ENV_PROMPT_SET,
    IMPOSTOR_REPORT_TEMPLATE,
    VOTE_BALLOT_TEMPLATE,
    PromptRenderers,
    accusation_round_prompt,
    build_environment,
    build_prompt_renderers,
    crewmate_report_prompt,
    impostor_report_prompt,
    resolve_prompt_set,
    vote_ballot_prompt,
)

__all__ = [
    "ACCUSATION_ROUND_TEMPLATE",
    "CREWMATE_REPORT_TEMPLATE",
    "DEFAULT_PROMPT_SET",
    "ENV_PROMPT_SET",
    "IMPOSTOR_REPORT_TEMPLATE",
    "VOTE_BALLOT_TEMPLATE",
    "PromptRenderers",
    "accusation_round_prompt",
    "build_environment",
    "build_prompt_renderers",
    "crewmate_report_prompt",
    "impostor_report_prompt",
    "resolve_prompt_set",
    "vote_ballot_prompt",
]
