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

The default is byte-identity, not a recommendation (Task 19.6). Every
operational surface runs :data:`OPERATIONAL_BASELINE_PROMPT_SET`
(``qwen3_6_27b``, the bespoke set for the canonical Featherless model), so a
bare environment taking the 9B default is running a prompt family two
generations behind the reports. The default VALUE stays — moving it would
move committed prompt bytes — but the fallback is no longer quiet:
:func:`resolve_prompt_set` emits a one-line stderr notice naming
``AILIBI_PROMPT_SET`` and the baseline set whenever it falls back with no
override present.

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

The impostor-answer template arm (Task 18.10)
=============================================

The gate's highest-variance arm, built inert: behind the default-OFF
:func:`impostor_roll_call_enabled` lever (``AILIBI_IMPOSTOR_ROLL_CALL``),
the two impostor-facing templates are swapped for their ``*_roll_call.j2``
VARIANT siblings — the impostor opening and reply ANSWER the whereabouts
ask with a structured self-placement instead of the hard-coded
``"observations": []`` (audits/audit-phase-18-planning.md §3.4, the
structural refusal). Routing is by template FILENAME: the wrapper
callables take an explicit ``template_name`` and
:func:`build_prompt_renderers` resolves the lever ONCE at construction and
binds the variant filenames into the returned bundle, so a runner renders
and stamps one consistent decision (the PR #203 binding discipline applied
to the lever). The variant templates exist only in the ``qwen3_6_27b``
set; lever ON with any other set fails loud at
:func:`build_prompt_renderers` — no silent fallback. Lever OFF (the
default) binds the exact default filenames, so the rendered prompt set is
byte-identical to the committed registry. The matching provenance side
lives in :data:`orchestrator.game.IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`
(recorded ``prompt_versions`` come from that registry, never from this
loader).
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Final

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

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

# The set every operational surface actually runs (Task 19.6): the bespoke
# 27B set recorded against the canonical Featherless model ``Qwen/Qwen3.6-27B``
# (AGENTS.md §"Environment setup"; the baseline-6 recording env in
# training/reports/report-finalist-eval.md is literally
# ``AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b``). It is NOT
# the default — :data:`DEFAULT_PROMPT_SET` stays the frozen 9B set so every
# committed render stays byte-identical (owner decision 2026-06-25) — but it is
# named in the bare-environment notice below so a bare shell cannot quietly run
# a prompt family two generations behind what the reports describe.
OPERATIONAL_BASELINE_PROMPT_SET: Final[str] = "qwen3_6_27b"


def _notify_bare_prompt_set_fallback() -> None:
    """Emit the one-line bare-environment notice on stderr (Task 19.6).

    Called from :func:`resolve_prompt_set` on the fallback path only. It is
    deliberately unconditional — no "warn once" flag, because that would be
    module-level mutable state (AGENTS.md §"No global state") — and stderr, not
    stdout, so it never contaminates the machine-readable stdout the CLI
    surfaces emit. The resolution points it rides are per-process or per-runner
    (the import-time :data:`_ENV`, ``build_prompt_renderers``,
    ``orchestrator.game.build_default_meeting_runner``,
    ``training.realpath``'s manifest stamp), not per-turn.
    """

    print(
        f"agents.strategic.prompts.loader: {ENV_PROMPT_SET} is unset — falling "
        f"back to the frozen reference set {DEFAULT_PROMPT_SET!r}, two "
        f"generations behind the operational baseline "
        f"{OPERATIONAL_BASELINE_PROMPT_SET!r}; export "
        f"{ENV_PROMPT_SET}={OPERATIONAL_BASELINE_PROMPT_SET} to run the "
        f"baseline set.",
        file=sys.stderr,
    )


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

    The bare-environment path is LOUD (Task 19.6). The default value itself is
    unchanged — it must stay :data:`DEFAULT_PROMPT_SET` for byte-identity with
    every committed render — but taking it *without* an ``AILIBI_PROMPT_SET``
    override now emits a one-line stderr notice naming the variable and
    :data:`OPERATIONAL_BASELINE_PROMPT_SET`, because a bare shell otherwise
    runs a prompt family two generations behind the operational baseline with
    no signal at all. The notice fires on exactly one path: no explicit
    ``prompt_set`` argument AND no non-empty ``AILIBI_PROMPT_SET``. An explicit
    argument (a caller pinning its own set) and a set env var are both silent —
    they are choices, not fallbacks.
    """

    if prompt_set is not None:
        return prompt_set
    environment = env if env is not None else os.environ
    selected = environment.get(ENV_PROMPT_SET, "").strip()
    if selected:
        return selected
    _notify_bare_prompt_set_fallback()
    return DEFAULT_PROMPT_SET


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

# Task 18.10 impostor-answer VARIANT filenames (qwen3_6_27b only): the impostor
# opening and reply answer the whereabouts ask with a structured self-placement
# instead of the hard-coded ``"observations": []``. Selected ONLY through the
# default-OFF :func:`impostor_roll_call_enabled` lever; the default filename
# constants above stay the served path everywhere else.
IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE: Final[str] = "impostor_report_roll_call.j2"
ACCUSATION_ROUND_ROLL_CALL_TEMPLATE: Final[str] = "accusation_round_roll_call.j2"

# Task 18.10 impostor-answer lever — DEFAULT-OFF (the 16.8 ``absence_prior_enabled``
# pattern: env-gated, NOT retired). Deliberately NOT registered in
# ``orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS`` yet — Task 18.11 wires the
# substrate stamp (with the other three Phase-18 lever flags) before any probe
# seed records; Task 18.12 is the graduation flip if the gate rules SHIP.
ENV_IMPOSTOR_ROLL_CALL: Final[str] = "AILIBI_IMPOSTOR_ROLL_CALL"
_IMPOSTOR_ROLL_CALL_FLAG_TRUE: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)


def impostor_roll_call_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the Task 18.10 impostor-answer lever is ON. DEFAULT OFF.

    Reads :data:`ENV_IMPOSTOR_ROLL_CALL` from ``env`` (defaulting to the real
    process environment), mirroring the 16.8
    :func:`agents.memory.beliefs.absence_prior_enabled` resolver it clones
    (itself the 16.4 ``hard_evidence_gate`` live-toggle pattern; the 18.8
    :func:`meetings.manager.roll_call_round_enabled` sibling). Default OFF: an
    unset / empty / unrecognised value is ``False`` so the loader keeps serving
    the exact default template filenames and the rendered prompt set stays
    byte-identical to the committed registry (the committed recordings and the
    ``tests/meetings/test_prompt_byte_golden.py`` reconstruction stay clean).
    Accepts ``1/true/yes/on`` (case-insensitive). The ``env`` argument lets
    tests toggle the lever deterministically without mutating ``os.environ``.

    ON swaps the two impostor-facing templates for their ``*_roll_call.j2``
    variant siblings (:data:`IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE` /
    :data:`ACCUSATION_ROUND_ROLL_CALL_TEMPLATE`, authored only in the
    ``qwen3_6_27b`` set): the impostor opening and reply ANSWER the
    whereabouts ask with one structured ``whereabouts`` self-placement — the
    two-tier design lets the claim be a lie, manufacturing exactly the
    contradiction material the alibi rules prosecute
    (audits/audit-phase-18-planning.md §3.4) — at the measured risk of the
    >=44% self-flag class the prompt ladder closed. The 18.11 probe measures
    both (pre-registered bar (c): probe impostor win >= 0.20 AND STRONG
    self-flag rate <= 0.25 of answered impostor roll-calls); the graduation
    flip, if ruled, is Task 18.12. Recorded provenance moves WITH the lever
    through :func:`orchestrator.game.prompt_versions_for_set`
    (:data:`~orchestrator.game.IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`), so
    variant bytes and default bytes never share a version stamp
    (audits/audit-phase-17-absence-gate.md Ruling 3(d)).
    """

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_IMPOSTOR_ROLL_CALL, "").strip().lower()
        in _IMPOSTOR_ROLL_CALL_FLAG_TRUE
    )


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
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
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

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are accepted so this
    wrapper conforms to the widened
    :class:`~meetings.render_contract.ReportPromptRenderer` Protocol and are
    passed straight through to ``.render(...)``. The current template references
    neither, so jinja ignores them and the prompt is byte-unchanged (the
    widen-the-contract-inert pattern; the 15.5 ``reporter_id`` precedent). The
    seam is landed once here so 16.15/16.16 edit ONLY the template.
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
            persona=persona,
            suspicion_provenance=suspicion_provenance,
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
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
    environment: Environment | None = None,
    template_name: str | None = None,
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

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the inert
    render-contract widenings, passed straight through; the current template
    references neither, so the prompt is byte-unchanged (the
    widen-the-contract-inert pattern, landed once so 16.15/16.16 edit only the
    template).

    ``template_name`` (Task 18.10) selects the template FILE this wrapper
    renders: the default ``None`` resolves it live from the
    :func:`impostor_roll_call_enabled` lever (OFF — the default — is the
    exact pre-task :data:`IMPOSTOR_REPORT_TEMPLATE` path, byte-identical),
    while :func:`build_prompt_renderers` passes an explicit name so a
    recording runner's routing decision is pinned at construction time (the
    PR #203 binding discipline). Lever ON outside the ``qwen3_6_27b`` set
    fails loud with :class:`jinja2.TemplateNotFound` — the variant file
    exists only there, and there is no silent fallback.
    """

    resolved_template = (
        template_name
        if template_name is not None
        else (
            IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE
            if impostor_roll_call_enabled()
            else IMPOSTOR_REPORT_TEMPLATE
        )
    )
    return (
        (environment or _ENV)
        .get_template(resolved_template)
        .render(
            agent_id=agent_id,
            current_tick=current_tick,
            meeting_trigger=meeting_trigger,
            rendered_memory=rendered_memory,
            public_transcript=public_transcript,
            fellow_impostor_ids=fellow_impostor_ids,
            living_ids=living_ids,
            dead_ids=dead_ids,
            persona=persona,
            suspicion_provenance=suspicion_provenance,
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
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
    environment: Environment | None = None,
    template_name: str | None = None,
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

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the inert
    render-contract widenings, passed straight through; the current template
    references neither, so the prompt is byte-unchanged (the
    widen-the-contract-inert pattern, landed once so 16.15/16.16 edit only the
    template).

    ``template_name`` (Task 18.10) selects the template FILE this wrapper
    renders: the default ``None`` resolves it live from the
    :func:`impostor_roll_call_enabled` lever (OFF — the default — is the
    exact pre-task :data:`ACCUSATION_ROUND_TEMPLATE` path, byte-identical),
    while :func:`build_prompt_renderers` passes an explicit name so a
    recording runner's routing decision is pinned at construction time (the
    PR #203 binding discipline). The variant file swaps ONLY the impostor
    reply surfaces; the crew reply and the role-blind info-share render
    byte-identically through it (fixture-pinned), which is why the swap is
    per-FILE rather than per-role — one meeting's ``accusation_round``
    prompts all carry one provenance stamp. Lever ON outside the
    ``qwen3_6_27b`` set fails loud with :class:`jinja2.TemplateNotFound`.
    """

    resolved_template = (
        template_name
        if template_name is not None
        else (
            ACCUSATION_ROUND_ROLL_CALL_TEMPLATE
            if impostor_roll_call_enabled()
            else ACCUSATION_ROUND_TEMPLATE
        )
    )
    return (
        (environment or _ENV)
        .get_template(resolved_template)
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
            persona=persona,
            suspicion_provenance=suspicion_provenance,
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
    persona: str = "",
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),
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

    ``persona`` (Task 16.3, populated 16.9, rendered 16.16) and
    ``suspicion_provenance`` (Task 16.3, rendered 16.15) are the inert
    render-contract widenings, passed straight through; the current template
    references neither, so the prompt is byte-unchanged. On the ballot the
    manager threads the same post-fold rows into ``suspicion_provenance`` as into
    ``suspicion_graph`` (the render-after-fold consistency pin), so 16.15's
    surface will decompose exactly the scalars already shown -- landed once here
    so 16.15 edits only the template.
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
            persona=persona,
            suspicion_provenance=suspicion_provenance,
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

    The Task 18.10 impostor-answer lever is resolved HERE, once, from the same
    ``env`` mapping (the PR #203 binding discipline extended to the lever):
    lever OFF — the default — binds the exact default template filenames, so
    the bundle is byte-identical to the pre-task path; lever ON binds the two
    ``*_roll_call.j2`` variant filenames into the impostor-report and
    statement renderers. ON with a set that does not carry the variant files
    (only ``qwen3_6_27b`` does) raises :class:`ValueError` at construction —
    no silent fallback, and no half-routed bundle can reach a runner.
    ``prompt_versions_for_set`` reads the same lever from the same ``env``,
    which is what keeps a recording's rendered bytes and recorded stamps on
    one routing decision.
    """

    environment = build_environment(prompt_set, root=root, env=env)
    variant = impostor_roll_call_enabled(env)
    impostor_report_template = (
        IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE if variant else IMPOSTOR_REPORT_TEMPLATE
    )
    statement_template = (
        ACCUSATION_ROUND_ROLL_CALL_TEMPLATE if variant else ACCUSATION_ROUND_TEMPLATE
    )
    if variant:
        for name in (impostor_report_template, statement_template):
            try:
                environment.get_template(name)
            except TemplateNotFound as exc:
                raise ValueError(
                    f"Prompt set {resolve_prompt_set(prompt_set, env=env)!r} has "
                    f"no impostor-answer variant template {name!r}; the Task "
                    "18.10 lever (AILIBI_IMPOSTOR_ROLL_CALL) is only authored "
                    "for the 'qwen3_6_27b' set — unset the lever or select a "
                    "variant-capable set"
                ) from exc
    return PromptRenderers(
        crewmate_report=partial(crewmate_report_prompt, environment=environment),
        impostor_report=partial(
            impostor_report_prompt,
            environment=environment,
            template_name=impostor_report_template,
        ),
        statement=partial(
            accusation_round_prompt,
            environment=environment,
            template_name=statement_template,
        ),
        vote=partial(vote_ballot_prompt, environment=environment),
    )


__all__ = [
    "ACCUSATION_ROUND_ROLL_CALL_TEMPLATE",
    "ACCUSATION_ROUND_TEMPLATE",
    "CREWMATE_REPORT_TEMPLATE",
    "DEFAULT_PROMPT_SET",
    "ENV_IMPOSTOR_ROLL_CALL",
    "ENV_PROMPT_SET",
    "IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE",
    "IMPOSTOR_REPORT_TEMPLATE",
    "OPERATIONAL_BASELINE_PROMPT_SET",
    "VOTE_BALLOT_TEMPLATE",
    "PromptRenderers",
    "accusation_round_prompt",
    "build_environment",
    "build_prompt_renderers",
    "crewmate_report_prompt",
    "impostor_report_prompt",
    "impostor_roll_call_enabled",
    "resolve_prompt_set",
    "vote_ballot_prompt",
]
