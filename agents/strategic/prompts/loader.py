"""Jinja loader for the four strategic prompt templates (Task 3.9 C-4).

The four ``.j2`` templates under ``agents/strategic/prompts/`` are the
canonical phase-1 report, accusation-round, and vote-ballot prompts
consumed by :class:`meetings.manager.MeetingManager`. This module wraps
them in a single strict-undefined :class:`jinja2.Environment` and exposes
one named Python callable per template so the wider codebase never touches
the filesystem directly.

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

Per-model prompt sets (Task 14.2)
=================================

The four templates live under a per-model *set* subdirectory rather than
flat next to this module (owner decision 2026-06-25 — per-model prompt
sets). The frozen ``qwen3.5:9b`` reference set is :data:`DEFAULT_PROMPT_SET`
(directory ``qwen3_5_9b/``); :func:`build_environment` resolves a set name
to its subdirectory and builds the strict-undefined
:class:`jinja2.Environment` against it. The active set is selected by the
:data:`ENV_PROMPT_SET` environment variable (``AILIBI_PROMPT_SET``),
defaulting to :data:`DEFAULT_PROMPT_SET` so existing renders are
byte-identical. An unknown set name (no matching subdirectory) raises
:class:`ValueError` — there is no silent fallback (AGENTS.md §"No silent
fallbacks"). The ``*_TEMPLATE`` filename constants are shared across sets;
only the directory varies.

The module-level wrapper callables render through the import-time process
default :data:`_ENV` (selected by ``AILIBI_PROMPT_SET`` at import). Each also
accepts an explicit ``environment`` so a caller can pin a specific set's
:class:`jinja2.Environment` per call — :func:`build_prompt_renderers` uses this
to bind the four renderers to ONE resolved set at construction time, so a runner
renders and records the SAME set even when ``AILIBI_PROMPT_SET`` is changed
in-process after this module is imported (PR #203 review).

Per-template wrapper signatures
===============================

Each wrapper conforms to the :class:`~meetings.render_contract.ReportPromptRenderer`,
:class:`~meetings.render_contract.StatementPromptRenderer`, or
:class:`~meetings.render_contract.VotePromptRenderer` Protocol from
:mod:`meetings.render_contract` so the loader-built callables can be passed
straight into :class:`~meetings.manager.MeetingManager` without an
intermediate adapter layer.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Final

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from meetings.render_contract import (
    ReportPromptRenderer,
    StatementPromptRenderer,
    SuspicionEntry,
    VotePromptRenderer,
)
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    TurnKind,
)

# Root holding the per-model prompt-set subdirectories (Task 14.2). The four
# ``.j2`` templates no longer live flat next to this module; each set is a
# subdirectory (``qwen3_5_9b/`` is the frozen 9B reference set).
_PROMPTS_ROOT: Final[Path] = Path(__file__).resolve().parent

# The frozen ``qwen3.5:9b`` reference set — the default so existing renders are
# byte-identical (owner decision 2026-06-25). Selected by ``AILIBI_PROMPT_SET``.
DEFAULT_PROMPT_SET: Final[str] = "qwen3_5_9b"
ENV_PROMPT_SET: Final[str] = "AILIBI_PROMPT_SET"


def resolve_prompt_set(
    prompt_set: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> str:
    """Resolve the active prompt-set name (Task 14.2).

    An explicit ``prompt_set`` wins; otherwise the :data:`ENV_PROMPT_SET`
    environment variable is consulted, defaulting to :data:`DEFAULT_PROMPT_SET`
    (the frozen 9B set) when unset or empty. The ``env`` argument lets tests
    select a set deterministically without mutating ``os.environ``.
    """

    if prompt_set is not None:
        return prompt_set
    environment = env if env is not None else os.environ
    return environment.get(ENV_PROMPT_SET, "").strip() or DEFAULT_PROMPT_SET


def build_environment(
    prompt_set: str | None = None,
    *,
    root: Path = _PROMPTS_ROOT,
    env: Mapping[str, str] | None = None,
) -> Environment:
    """Build a strict-undefined :class:`jinja2.Environment` for a prompt set.

    Resolves ``prompt_set`` (via :func:`resolve_prompt_set`) to a subdirectory
    of ``root`` and builds the loader against it. An unknown set — no matching
    subdirectory — raises :class:`ValueError`; there is no silent fallback
    (AGENTS.md §"No silent fallbacks"). The strict-undefined / trim / lstrip /
    no-autoescape policy is identical across sets, so a content-preserving move
    of the 9B templates renders byte-identically.
    """

    name = resolve_prompt_set(prompt_set, env=env)
    directory = root / name
    if not directory.is_dir():
        raise ValueError(
            f"Unknown prompt set {name!r}: no template directory at {directory}"
        )
    return Environment(
        loader=FileSystemLoader(directory),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


# The process-default environment, bound to the active set at import time. The
# wrapper callables below render through it so call sites stay unchanged; the
# set is selected by ``AILIBI_PROMPT_SET`` (default: the frozen 9B set).
_ENV: Final[Environment] = build_environment()

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
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    environment: Environment | None = None,
) -> str:
    """Render the Phase-1 crewmate report prompt (DESIGN.md §5.3).

    ``fellow_impostor_ids`` (Task 7.12) is accepted so this wrapper
    conforms to the same :class:`~meetings.render_contract.ReportPromptRenderer`
    Protocol as :func:`impostor_report_prompt` and the meeting manager
    can dispatch by role without an adapter. A crewmate has no teammate
    list (the value is always ``()``) and the crewmate template never
    references it, so the rendered prompt is byte-unchanged.

    ``living_ids`` (Task 9.9, audit gp-3) is the living-roster accusation
    list -- living participants minus this speaker, the turn-side mirror of
    the vote ballot's ``candidate_targets`` -- rendered as the only valid
    accusation targets. The template guards the block on a non-empty value,
    so the default ``()`` (ad-hoc renders) keeps the prompt byte-unchanged.

    ``dead_ids`` (Task 10.3, audit gp-9) is the dead / ejected negative
    list, rendered as an explicit do-not-accuse line under the living
    roster. Guarded the same way: the default ``()`` omits the line.
    """

    return (
        (environment or _ENV)
        .get_template(CREWMATE_REPORT_TEMPLATE)
        .render(
            agent_id=agent_id,
            current_tick=current_tick,
            meeting_trigger=meeting_trigger,
            rendered_memory=rendered_memory,
            public_transcript=public_transcript,
            living_ids=living_ids,
            dead_ids=dead_ids,
        )
    )


def impostor_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    environment: Environment | None = None,
) -> str:
    """Render the Phase-1 impostor report prompt (DESIGN.md §4.5, §5.3).

    Conforms to the same :class:`~meetings.render_contract.ReportPromptRenderer`
    Protocol as :func:`crewmate_report_prompt` so the meeting manager
    can dispatch by role without an extra adapter. The impostor
    template itself does not reference ``agent_id``, ``current_tick``,
    or ``meeting_trigger`` — they are accepted and passed through so
    a future template revision can opt in without breaking call sites.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor's teammate list;
    the template renders the "never accuse / incriminate a teammate"
    block only when it is non-empty, so a sole impostor (``()``) gets a
    byte-unchanged prompt.

    ``living_ids`` (Task 9.9) is the living-roster accusation list,
    rendered since impostor_report_v4 (Task 10.3): the dead-id
    accusation hallucination was disproportionately impostor-spoken
    (12/18, audit gp-9 D-D-8), so the impostor opening now carries the
    same roster block as the crewmate one. ``dead_ids`` (Task 10.3) is
    the matching dead / ejected do-not-accuse line. Both are guarded on
    a non-empty value, so the defaults (``()``) omit the blocks.
    """

    return (
        (environment or _ENV)
        .get_template(IMPOSTOR_REPORT_TEMPLATE)
        .render(
            agent_id=agent_id,
            current_tick=current_tick,
            meeting_trigger=meeting_trigger,
            rendered_memory=rendered_memory,
            public_transcript=public_transcript,
            fellow_impostor_ids=fellow_impostor_ids,
            living_ids=living_ids,
            dead_ids=dead_ids,
        )
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
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    is_impostor: bool = False,
    is_body_report: bool = False,
    environment: Environment | None = None,
) -> str:
    """Render a reactive ``reply`` / ``opt_in`` turn prompt (DESIGN.md §5.2).

    Conforms to the :class:`~meetings.render_contract.StatementPromptRenderer`
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

    ``living_ids`` (Task 9.9, audit gp-3) is the living-roster accusation
    list -- living participants minus this speaker, the turn-side mirror of
    the vote ballot's ``candidate_targets`` -- rendered as the only valid
    accusation targets. The template guards the block on a non-empty value,
    so the default ``()`` (ad-hoc renders) keeps the prompt byte-unchanged.

    ``dead_ids`` (Task 10.3, audit gp-9) is the dead / ejected negative
    list, rendered as an explicit do-not-accuse line under the living
    roster. Guarded the same way: the default ``()`` omits the line.

    ``is_impostor`` (Task 11.2) gates the cover-consistency directive on
    the reply branch -- the impostor commits to ONE sheltered room +
    tick-window away from the body and reuses it every turn (DESIGN.md
    §5.2; experiments/lab/report-vent-escape-lab.md, the residual
    self-pair alibi_conflict drift). It is an explicit bool rather than a
    reuse of ``fellow_impostor_ids`` because a SOLE impostor has empty
    fellows but must still get the directive. The default ``False`` keeps
    the crewmate (and ad-hoc) render byte-unchanged.

    ``is_body_report`` (Task 11.2; PR #159 review) is the second gate on the
    cover directive: the wording speaks of "the body's room and the tick it
    happened", so -- mirroring ``impostor_report.j2``'s ``body_report_opening``
    gate -- the block must fire only when a body is on the table, never on a
    body-less emergency reply. The default ``False`` keeps the block off unless
    the caller explicitly marks the meeting a body report.
    """

    return (
        (environment or _ENV)
        .get_template(ACCUSATION_ROUND_TEMPLATE)
        .render(
            agent_id=agent_id,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradictions=contradictions,
            prior_turn=prior_turn,
            turn_kind=turn_kind,
            fellow_impostor_ids=fellow_impostor_ids,
            living_ids=living_ids,
            dead_ids=dead_ids,
            is_impostor=is_impostor,
            is_body_report=is_body_report,
        )
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
    reporter_id: PlayerId | None = None,
    environment: Environment | None = None,
) -> str:
    """Render a vote-ballot prompt (DESIGN.md §5.5).

    Conforms to the :class:`~meetings.render_contract.VotePromptRenderer`
    Protocol; the meeting manager invokes this callable verbatim per
    voter to produce the ballot-phase prompt.

    ``fellow_impostor_ids`` (Task 7.12) is the impostor-only teammate
    list; the template renders the "never vote a teammate — SKIP
    instead" block only when it is non-empty, so a crewmate /
    sole-impostor ballot (``()``) is byte-unchanged.

    ``reporter_id`` (Task 15.5, reporter-exculpation lever) is the
    body-report meeting's own reporter, threaded by the manager ONLY when the
    default-OFF ``reporter_exculpation`` lever is ON. The v6 template renders
    the self-report base-rate annotation only when it is non-``None``; the
    default ``None`` (lever OFF, emergency call, or ad-hoc render) omits the
    block, so a lever-OFF ballot prompt is byte-identical.
    """

    return (
        (environment or _ENV)
        .get_template(VOTE_BALLOT_TEMPLATE)
        .render(
            voter_id=voter_id,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradiction_flags=contradiction_flags,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=skip_confidence_threshold,
            fellow_impostor_ids=fellow_impostor_ids,
            reporter_id=reporter_id,
        )
    )


@dataclass(frozen=True)
class PromptRenderers:
    """The four strategic prompt renderers bound to ONE prompt set (Task 14.2).

    Each field is a wrapper callable pre-bound (via :func:`functools.partial`)
    to a single set's :class:`jinja2.Environment`, so a meeting runner renders
    its turns and records its ``prompt_versions`` from the SAME set -- even if
    ``AILIBI_PROMPT_SET`` is changed in-process after this module's import-time
    :data:`_ENV` was built (PR #203 review). The field names mirror the
    :class:`~meetings.manager.MeetingManager` prompt-callable parameters.
    """

    crewmate_report: ReportPromptRenderer
    impostor_report: ReportPromptRenderer
    statement: StatementPromptRenderer
    vote: VotePromptRenderer


def build_prompt_renderers(
    prompt_set: str | None = None,
    *,
    root: Path = _PROMPTS_ROOT,
    env: Mapping[str, str] | None = None,
) -> PromptRenderers:
    """Build the four renderers bound to a single resolved prompt set.

    Resolves ``prompt_set`` once (via :func:`build_environment`) and binds every
    renderer to that set's :class:`jinja2.Environment`. Pairing the returned
    bundle with :func:`orchestrator.game.prompt_versions_for_set` for the SAME
    resolved set keeps a recording's rendered templates and recorded
    ``prompt_versions`` on one set, which is the replay-provenance invariant
    (DESIGN.md §11.4). An unknown set raises via :func:`build_environment`.
    """

    environment = build_environment(prompt_set, root=root, env=env)
    return PromptRenderers(
        crewmate_report=partial(crewmate_report_prompt, environment=environment),
        impostor_report=partial(impostor_report_prompt, environment=environment),
        statement=partial(accusation_round_prompt, environment=environment),
        vote=partial(vote_ballot_prompt, environment=environment),
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
