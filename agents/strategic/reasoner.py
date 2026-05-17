"""Strategic reasoner (Task 3.9, DESIGN.md §4.4, §6.6).

The reasoner is the convergence point for sub-phase C: composite agent
memory (Task 3.3), the four ``.j2`` prompt templates (Tasks 3.4-3.7),
the structured-output schemas (Task 3.2), and the budget-wrapped LLM
client (Task 3.9 C-5) compose into a single class that produces
:class:`~meetings.schemas.ReportDocument`,
:class:`~meetings.schemas.Statement`, or
:class:`~meetings.schemas.VoteBallot` instances at meetings or specified
trigger points (kill-witnessed, body-found) — never inside
``agents/tactical/``.

Pipeline
========

For every strategic call the pipeline is:

1. :func:`~agents.memory.store.render_for_prompt` produces the
   Markdown view of the agent's composite memory under the
   configured token budget.
2. The rendered view is scanned for leaks via the canonical
   :func:`eval.leak_test._assert_no_recursive_hidden_fields` /
   :func:`eval.leak_test._assert_no_role_bearing_values` helpers
   (R-10 acceptance gate, ``audits/audit-2026-05-15-0225-reconciled.md``
   §R-10; closes C-1 from
   ``audits/audit-2026-05-16-2239-claude.md``). The scanners are
   imported directly; no Phase-3 successor is introduced.
3. The matching prompt callable (one of the four from
   :mod:`agents.strategic.prompts`) renders the final prompt string.
4. :meth:`~llm.client.LLMClient.complete` is invoked with the
   appropriate Pydantic schema. The budget-wrapped client enforces
   :meth:`~llm.budget.GameBudget.preflight` /
   :meth:`~llm.budget.GameBudget.charge` around the call.
5. The response text is parsed as the schema; identity fields owned
   by the reasoner (``agent_id``, ``tick``, ``statement_id``,
   ``round_index``, ``voter``) are overwritten with the canonical
   values supplied by the caller. The LLM is never authoritative for
   identity bookkeeping (matches the meeting-manager precedent in
   :mod:`meetings.manager`).

Non-elastic token-budget carve-out (DESIGN.md §6.6)
====================================================

DESIGN.md §6.6 documents that the role line, tasks-completed line,
beliefs, and contradictions are always retained (non-elastic) when the
rendered view runs over budget; only observations are elastic and
drop salience-sorted. The reasoner respects this contract: it calls
:func:`~agents.memory.store.render_for_prompt` with the configured
token budget and trusts the renderer's elasticity policy. When a meeting
prompt would push past the model's context window, that is an
orchestrator-level concern (DESIGN.md §6.6); the reasoner does not
re-implement budget elasticity for beliefs/contradictions.
"""

from __future__ import annotations

import re
from typing import Final, Literal, cast

from agents.memory.store import DEFAULT_TOKEN_BUDGET, AgentMemory, render_for_prompt
from agents.strategic.prompts import (
    accusation_round_prompt as _default_accusation_round_prompt,
)
from agents.strategic.prompts import (
    crewmate_report_prompt as _default_crewmate_report_prompt,
)
from agents.strategic.prompts import (
    impostor_report_prompt as _default_impostor_report_prompt,
)
from agents.strategic.prompts import (
    vote_ballot_prompt as _default_vote_ballot_prompt,
)
from llm.client import CallKind, LLMClient
from meetings.manager import (
    DEFAULT_REPORT_MAX_TOKENS,
    DEFAULT_REPORT_TEMPERATURE,
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    DEFAULT_STATEMENT_MAX_TOKENS,
    DEFAULT_STATEMENT_TEMPERATURE,
    DEFAULT_VOTE_MAX_TOKENS,
    DEFAULT_VOTE_TEMPERATURE,
    ReportPromptRenderer,
    StatementPromptRenderer,
    SuspicionEntry,
    VotePromptRenderer,
)
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    PlayerId,
    ReportDocument,
    Statement,
    VoteBallot,
)

Role = Literal["CREWMATE", "IMPOSTOR"]

# Trigger points at which the reasoner may be invoked (DESIGN.md §4.4).
# The tag is recorded on each invocation for downstream replay / cost
# attribution and to route the LLM call to the right model tier (meeting
# vs trigger; see :data:`_TRIGGER_CALL_KIND`).
StrategicTrigger = Literal[
    "meeting_report",
    "meeting_statement",
    "meeting_vote",
    "kill_witnessed",
    "body_found",
]

# Map each :class:`StrategicTrigger` label to the :class:`CallKind` the
# wrapped :class:`LLMClient` consumes. Meeting-protocol calls use the
# meeting-strength tier (Sonnet in production); the
# out-of-meeting trigger points (kill-witnessed, body-found) per
# DESIGN.md §4.4 are short reactive checks that route to the cheaper
# triggered-check tier (Haiku in production). Without this mapping the
# reasoner would always invoke the meeting tier even for triggered
# checks, mis-attributing cost and selecting the wrong model.
_TRIGGER_CALL_KIND: Final[dict[StrategicTrigger, CallKind]] = {
    "meeting_report": "meeting",
    "meeting_statement": "meeting",
    "meeting_vote": "meeting",
    "kill_witnessed": "trigger",
    "body_found": "trigger",
}

# Per-method allowed-trigger subsets. Each ``produce_*`` method
# validates against its own subset so cross-method mismatches (e.g.
# ``produce_statement(trigger="kill_witnessed")``) are rejected
# fail-loud instead of silently mis-routing the call to the trigger
# tier. ``produce_report`` admits the kill/body reactive labels
# because DESIGN.md §4.4 names them as out-of-meeting strategic
# trigger points that produce a report-shaped LLM output; the
# accusation-round and vote phases only happen inside a meeting and
# therefore admit only their corresponding meeting label.
_REPORT_ALLOWED_TRIGGERS: Final[frozenset[StrategicTrigger]] = frozenset(
    {"meeting_report", "kill_witnessed", "body_found"}
)
_STATEMENT_ALLOWED_TRIGGERS: Final[frozenset[StrategicTrigger]] = frozenset(
    {"meeting_statement"}
)
_VOTE_ALLOWED_TRIGGERS: Final[frozenset[StrategicTrigger]] = frozenset({"meeting_vote"})

# Defense-in-depth: hidden field NAMES from the engine packet
# vocabulary that could leak as TEXT substrings inside the rendered
# memory or auxiliary inputs. The canonical
# :func:`eval.leak_test._assert_no_recursive_hidden_fields` scanner
# walks JSON keys, not string values, so a contradiction summary or
# free-text input containing ``killed_by p-5`` slips past it. The
# substring check below catches that text-surface case. ``player_id``
# is intentionally excluded because the literal substring appears in
# benign contexts (every player belief line mentions ``p-X`` ids; the
# string ``player_id`` itself is not a leak surface in rendered text).
_FORBIDDEN_TEXT_SUBSTRINGS: Final[tuple[str, ...]] = (
    "killed_by",
    "kill_attribution",
)

# Mirror the patterns the memory-rendering tests use to map the
# legitimate ``## Your role: X`` line onto the canonical
# ``self_state.role`` path so the leak scanner does not trip on it.
# The renderer guarantees this header is the first line of the rendered
# view; only the first match is stripped so injected lines later in the
# body (e.g. inside a contradiction summary) still reach the scanner.
_ROLE_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^## Your role: .+$\n?", re.MULTILINE
)
_ROLE_VALUE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^## Your role: (.+)$", re.MULTILINE
)


def _scan_prompt_inputs(
    *,
    rendered_memory: str,
    auxiliary_text_inputs: dict[str, str] | None = None,
) -> None:
    """Run the canonical packet leak scanners on strategic prompt inputs.

    Reuses :func:`eval.leak_test._assert_no_recursive_hidden_fields` and
    :func:`eval.leak_test._assert_no_role_bearing_values` directly — no
    re-implementation — per the R-10 acceptance gate
    (``audits/audit-2026-05-15-0225-reconciled.md`` §R-10) and the
    C-1 hedge closure (``audits/audit-2026-05-16-2239-claude.md``).

    The scanner imports are function-local so that importing
    :mod:`agents.strategic.reasoner` does not pull
    :mod:`eval.leak_test` (and its transitive engine + test-helper
    dependencies) into the importing process at module-load time.
    Engine is loaded only when a scan actually runs.

    The single allowed appearance of a role-bearing string is the
    agent's own ``## Your role: X`` header line — the
    :func:`~agents.memory.store.render_for_prompt` renderer guarantees
    this is the first line of the rendered view. We strip only that
    first match (``count=1``) and map its captured role onto the
    canonical ``self_state.role`` path the scanner already
    allow-lists. Any further occurrence of the same prefix later in
    the body (e.g. inside a contradiction summary or other free text)
    is left in place so the scanner sees and rejects it.

    Defense-in-depth substring check
    --------------------------------

    :func:`~eval.leak_test._assert_no_recursive_hidden_fields` checks
    JSON KEY names, not string VALUES. Hidden-field NAMES like
    ``killed_by`` / ``kill_attribution`` could still appear inside the
    rendered text (e.g. a contradiction summary that says
    ``"killed_by p-5"``) and slip past the canonical scanner — the
    rendered body lives in a single ``rendered_body`` JSON value, so
    the recursive scanner only sees the wrapper key. The substring
    check below catches the text-surface case explicitly, as a
    supplement to (not a replacement for) the canonical scanners.

    Raises :class:`AssertionError` if any scanner trips. The reasoner
    treats this as fail-loud — a leak in a strategic prompt input is
    a wiring bug, not a recoverable condition (AGENTS.md "no silent
    fallbacks").
    """

    # Function-local import: defers loading eval.leak_test (which
    # transitively imports engine/* and tests/_helpers/*) until a scan
    # actually runs. Importing StrategicReasoner alone does not trigger
    # the chain.
    from eval.leak_test import (  # noqa: PLC0415
        JsonValue,
        _assert_no_recursive_hidden_fields,
        _assert_no_role_bearing_values,
    )

    role_match = _ROLE_VALUE_PATTERN.search(rendered_memory)
    role = role_match.group(1) if role_match else ""
    body = _ROLE_LINE_PATTERN.sub("", rendered_memory, count=1)
    payload: dict[str, JsonValue] = {
        "self_state": {"role": role},
        "rendered_body": body,
    }
    if auxiliary_text_inputs is not None:
        for name, text in auxiliary_text_inputs.items():
            payload[name] = text
    payload_value = cast(JsonValue, payload)
    _assert_no_recursive_hidden_fields(payload_value)
    _assert_no_role_bearing_values(payload_value)
    # Supplementary substring scan for hidden-field NAMES that may
    # appear as TEXT inside rendered_body / auxiliary inputs.
    _assert_no_forbidden_field_substrings(
        rendered_memory=body,
        auxiliary_text_inputs=auxiliary_text_inputs,
    )


def _assert_no_forbidden_field_substrings(
    *,
    rendered_memory: str,
    auxiliary_text_inputs: dict[str, str] | None,
) -> None:
    """Defense-in-depth scan for forbidden hidden-field NAMES in text.

    Complements the canonical
    :func:`eval.leak_test._assert_no_recursive_hidden_fields` (which
    walks JSON keys) by catching the same forbidden field names when
    they appear as TEXT substrings inside the rendered memory body or
    free-text auxiliary inputs. Raises :class:`AssertionError` on a
    hit with the offending substring and surface name in the message
    so the wiring bug is easy to trace.
    """

    surfaces: list[tuple[str, str]] = [("rendered_body", rendered_memory)]
    if auxiliary_text_inputs is not None:
        surfaces.extend(auxiliary_text_inputs.items())
    for name, text in surfaces:
        for forbidden in _FORBIDDEN_TEXT_SUBSTRINGS:
            if forbidden in text:
                raise AssertionError(
                    f"forbidden field-name substring {forbidden!r} leaked "
                    f"into strategic prompt input {name!r}"
                )


class StrategicReasoner:
    """Composite memory + prompt + LLM pipeline (DESIGN.md §4.4).

    Construction is cheap and side-effect free: it stores references
    to the LLM client, the four prompt callables, and per-call default
    knobs. The reasoner does NOT own any meeting state — every call
    takes the participating agent's memory, identity, and the relevant
    meeting context as explicit kwargs.

    The four prompt callables default to the loader-built wrappers in
    :mod:`agents.strategic.prompts`; tests and the orchestrator may
    inject scripted stubs by passing alternates to the constructor.

    The reasoner is the public surface downstream tasks (3.10 voting,
    3.11 contradictions, 3.12 orchestrator) consume; its public type
    signature is therefore stable.
    """

    def __init__(
        self,
        *,
        llm_client: LLMClient,
        crewmate_report_prompt: ReportPromptRenderer = (
            _default_crewmate_report_prompt
        ),
        impostor_report_prompt: ReportPromptRenderer = (
            _default_impostor_report_prompt
        ),
        statement_prompt: StatementPromptRenderer = (_default_accusation_round_prompt),
        vote_prompt: VotePromptRenderer = _default_vote_ballot_prompt,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        report_max_tokens: int = DEFAULT_REPORT_MAX_TOKENS,
        report_temperature: float = DEFAULT_REPORT_TEMPERATURE,
        statement_max_tokens: int = DEFAULT_STATEMENT_MAX_TOKENS,
        statement_temperature: float = DEFAULT_STATEMENT_TEMPERATURE,
        vote_max_tokens: int = DEFAULT_VOTE_MAX_TOKENS,
        vote_temperature: float = DEFAULT_VOTE_TEMPERATURE,
        skip_confidence_threshold: float = DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    ) -> None:
        if token_budget <= 0:
            raise ValueError(f"token_budget must be positive, got {token_budget}")
        if report_max_tokens <= 0:
            raise ValueError(
                f"report_max_tokens must be positive, got {report_max_tokens}"
            )
        if statement_max_tokens <= 0:
            raise ValueError(
                f"statement_max_tokens must be positive, got {statement_max_tokens}"
            )
        if vote_max_tokens <= 0:
            raise ValueError(f"vote_max_tokens must be positive, got {vote_max_tokens}")
        if not 0.0 <= skip_confidence_threshold <= 1.0:
            raise ValueError(
                "skip_confidence_threshold must be in [0, 1], "
                f"got {skip_confidence_threshold}"
            )
        self._llm_client = llm_client
        self._crewmate_report_prompt = crewmate_report_prompt
        self._impostor_report_prompt = impostor_report_prompt
        self._statement_prompt = statement_prompt
        self._vote_prompt = vote_prompt
        self._token_budget = token_budget
        self._report_max_tokens = report_max_tokens
        self._report_temperature = report_temperature
        self._statement_max_tokens = statement_max_tokens
        self._statement_temperature = statement_temperature
        self._vote_max_tokens = vote_max_tokens
        self._vote_temperature = vote_temperature
        self._skip_confidence_threshold = skip_confidence_threshold

    @property
    def llm_client(self) -> LLMClient:
        """The wrapped :class:`LLMClient` (typically a budgeted client)."""

        return self._llm_client

    async def produce_report(
        self,
        *,
        memory: AgentMemory,
        agent_id: PlayerId,
        role: Role,
        current_tick: int,
        meeting_trigger: str,
        public_transcript: str = "",
        trigger: StrategicTrigger = "meeting_report",
    ) -> ReportDocument:
        """Phase-1 :class:`ReportDocument` from rendered memory.

        Routes to the crewmate or impostor template based on ``role``.
        The LLM-provided ``agent_id`` and ``tick`` are discarded; the
        reasoner is authoritative for identity bookkeeping (matches the
        meeting-manager precedent in :mod:`meetings.manager` -- the
        prompt templates explicitly say the reasoner will override
        those fields).
        """

        if role not in ("CREWMATE", "IMPOSTOR"):
            raise ValueError(f"role must be 'CREWMATE' or 'IMPOSTOR', got {role!r}")
        _validate_trigger_for_method(
            trigger,
            method="produce_report",
            allowed=_REPORT_ALLOWED_TRIGGERS,
        )
        rendered_memory = render_for_prompt(memory, token_budget=self._token_budget)
        _scan_prompt_inputs(
            rendered_memory=rendered_memory,
            auxiliary_text_inputs={"meeting_trigger": meeting_trigger},
        )
        renderer = (
            self._impostor_report_prompt
            if role == "IMPOSTOR"
            else self._crewmate_report_prompt
        )
        prompt = renderer(
            agent_id=agent_id,
            current_tick=current_tick,
            meeting_trigger=meeting_trigger,
            rendered_memory=rendered_memory,
            public_transcript=public_transcript,
        )
        response = await self._llm_client.complete(
            prompt=prompt,
            schema=ReportDocument,
            max_tokens=self._report_max_tokens,
            temperature=self._report_temperature,
            call_kind=_TRIGGER_CALL_KIND[trigger],
        )
        parsed = ReportDocument.model_validate_json(response.text)
        return parsed.model_copy(update={"agent_id": agent_id, "tick": current_tick})

    async def produce_statement(
        self,
        *,
        memory: AgentMemory,
        meeting_id: str,
        speaker: PlayerId,
        tick: int,
        round_index: int,
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...] = (),
        trigger: StrategicTrigger = "meeting_statement",
    ) -> Statement:
        """Phase-2 :class:`Statement` from rendered memory + transcript.

        ``statement_id`` is composed deterministically from
        ``(meeting_id, round_index, speaker)`` so replay logs can map a
        statement back to its slot without trusting the LLM with the
        identity.
        """

        if not meeting_id:
            raise ValueError("meeting_id must be a non-empty string")
        if round_index < 0:
            raise ValueError(f"round_index must be non-negative, got {round_index}")
        _validate_trigger_for_method(
            trigger,
            method="produce_statement",
            allowed=_STATEMENT_ALLOWED_TRIGGERS,
        )
        rendered_memory = render_for_prompt(memory, token_budget=self._token_budget)
        _scan_prompt_inputs(rendered_memory=rendered_memory)
        prompt = self._statement_prompt(
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradictions=contradictions,
        )
        response = await self._llm_client.complete(
            prompt=prompt,
            schema=Statement,
            max_tokens=self._statement_max_tokens,
            temperature=self._statement_temperature,
            call_kind=_TRIGGER_CALL_KIND[trigger],
        )
        parsed = Statement.model_validate_json(response.text)
        statement_id = f"{meeting_id}:r{round_index}:{speaker}"
        return parsed.model_copy(
            update={
                "statement_id": statement_id,
                "speaker": speaker,
                "tick": tick,
                "round_index": round_index,
            }
        )

    async def produce_vote(
        self,
        *,
        memory: AgentMemory,
        voter: PlayerId,
        transcript: MeetingTranscript,
        candidate_targets: tuple[PlayerId, ...],
        contradiction_flags: tuple[ContradictionRef, ...] = (),
        suspicion_graph: tuple[SuspicionEntry, ...] = (),
        skip_confidence_threshold: float | None = None,
        trigger: StrategicTrigger = "meeting_vote",
    ) -> VoteBallot:
        """Phase-3 :class:`VoteBallot` from rendered memory + transcript.

        The reasoner is authoritative for the ``voter`` field; the LLM
        is told to emit it but any value it returns is overwritten with
        the canonical caller-supplied id. Defensive normalization of an
        invalid ``target`` value is the meeting manager's responsibility
        (DESIGN.md §5.5 + meeting-manager contract), not the reasoner's.
        """

        _validate_trigger_for_method(
            trigger,
            method="produce_vote",
            allowed=_VOTE_ALLOWED_TRIGGERS,
        )
        threshold = (
            self._skip_confidence_threshold
            if skip_confidence_threshold is None
            else skip_confidence_threshold
        )
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                f"skip_confidence_threshold must be in [0, 1], got {threshold}"
            )
        rendered_memory = render_for_prompt(memory, token_budget=self._token_budget)
        _scan_prompt_inputs(rendered_memory=rendered_memory)
        prompt = self._vote_prompt(
            voter_id=voter,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradiction_flags=contradiction_flags,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=threshold,
        )
        response = await self._llm_client.complete(
            prompt=prompt,
            schema=VoteBallot,
            max_tokens=self._vote_max_tokens,
            temperature=self._vote_temperature,
            call_kind=_TRIGGER_CALL_KIND[trigger],
        )
        parsed = VoteBallot.model_validate_json(response.text)
        return parsed.model_copy(update={"voter": voter})


def _validate_trigger_for_method(
    trigger: StrategicTrigger,
    *,
    method: str,
    allowed: frozenset[StrategicTrigger],
) -> None:
    """Reject a trigger label that does not match this entrypoint.

    Each ``produce_*`` method calls this with its own ``allowed``
    subset so cross-method mismatches (e.g.
    ``produce_statement(trigger="kill_witnessed")``) are rejected
    fail-loud rather than silently routing the call to the wrong
    model tier. The :class:`StrategicTrigger` ``Literal`` is enforced
    by mypy at compile-time call sites, but runtime dispatch code can
    still pass a stringly-typed label that slips past static checks;
    this guard surfaces the wiring error at the call instead of
    mis-attributing the call in replay logs.
    """

    if trigger not in allowed:
        raise ValueError(
            f"StrategicReasoner.{method} does not accept trigger {trigger!r}; "
            f"allowed triggers: {sorted(allowed)}"
        )


__all__ = [
    "Role",
    "StrategicReasoner",
    "StrategicTrigger",
]
