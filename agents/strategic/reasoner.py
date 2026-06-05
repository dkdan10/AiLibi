"""Strategic reasoner (Task 3.9 / 8.8, DESIGN.md §4.4, §5.2, §6.6).

The reasoner is the convergence point for the strategic policy: composite
agent memory (Task 3.3), the four ``.j2`` prompt templates (reshaped in
Task 8.8 to the reactive accusation chain), the structured-output schemas
(Task 8.7), and the budget-wrapped LLM client (Task 3.9 C-5) compose into a
single class that produces meeting artifacts at meetings or specified
trigger points (kill-witnessed, body-found) — never inside
``agents/tactical/``.

Reactive accusation chain producers (DESIGN.md §4.4, §5.2)
=========================================================

The chain (DESIGN.md §5.2) records one ordered ``transcript.turns`` list,
so the reasoner produces :class:`~meetings.schemas.MeetingTurn` instances
rather than the old parallel ``ReportDocument`` / ``Statement`` pair:

* :meth:`StrategicReasoner.produce_report` -- the **opening** turn
  (``turn_kind = "opening"``, turn 0): the reporter / emergency caller
  states findings and accuses one player or stays unsure. Role selects the
  crewmate vs impostor template.
* :meth:`StrategicReasoner.produce_statement` -- a **reactive chain or
  opt-in** turn (``turn_kind ∈ {"reply", "opt_in"}``). It gains a
  ``prior_turn`` input (the accusing turn this speaker answers -- the "who
  accused me" context) and sets ``reply_to`` from it.
* :meth:`StrategicReasoner.produce_vote` -- the :class:`VoteBallot`.

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
5. The response text is parsed as the schema; the identity fields owned
   by the reasoner (``turn_id``, ``turn_index``, ``speaker``,
   ``turn_kind``, ``reply_to`` for a turn; ``voter`` for a ballot) are
   overwritten with the canonical values supplied by the caller. The LLM
   is never authoritative for identity bookkeeping (matches the
   meeting-manager precedent in :mod:`meetings.manager`).

The Task 7.12 teammate firewall guard and the leak scan run on **every**
turn-kind (opening, reply, opt-in) and on the vote, so an impostor never
produces an accusation / ballot that incriminates a fellow impostor and
no hidden field reaches the LLM, regardless of what the model emits.

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
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    DEFAULT_TURN_MAX_TOKENS,
    DEFAULT_TURN_TEMPERATURE,
    DEFAULT_VOTE_MAX_TOKENS,
    DEFAULT_VOTE_TEMPERATURE,
    ReportPromptRenderer,
    StatementPromptRenderer,
    SuspicionEntry,
    VotePromptRenderer,
    coerce_teammate_ballot_to_skip,
    exclude_teammate_accusation_claims,
)
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    PlayerId,
    SawPlayerObservation,
    TurnKind,
    VoteBallot,
)

Role = Literal["CREWMATE", "IMPOSTOR"]

# Turn kinds the reactive chain / opt-in producer may emit. The opening
# turn (turn 0) is produced by :meth:`StrategicReasoner.produce_report`;
# ``produce_statement`` owns the reactive ``reply`` and terminal ``opt_in``
# turns, so it rejects ``"opening"`` fail-loud.
_STATEMENT_TURN_KINDS: Final[frozenset[TurnKind]] = frozenset({"reply", "opt_in"})

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
# trigger points that produce an opening-shaped LLM output; the
# reactive-turn and vote phases only happen inside a meeting and
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
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
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

    Teammate self-channel allow-list (Task 7.12)
    --------------------------------------------

    ``fellow_impostor_ids`` is impostor-only self-channel data, exactly
    like the role line: an impostor is entitled to know its own team
    (Task 7.2). It rides the allow-listed ``self_state`` sub-object so
    an impostor's own teammate ids are not flagged (they are also
    role-neutral ``p-N`` ids that never match the value scanner). The
    firewall teeth are the explicit assertion below: a NON-impostor
    prompt carrying any teammate id is a leak (it would tell a crewmate
    who the impostors are), so it fails loud — mirroring the 7.2
    crew-empty invariant. A crewmate's list is always empty, so the
    scan for a crewmate prompt is unchanged (not loosened).

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
    # Task 7.12 firewall: teammate ids may only ride an impostor's own
    # prompt. A non-impostor prompt carrying any fellow_impostor_id is a
    # crew-misroute leak (mirrors the 7.2 crew-empty invariant); fail
    # loud. The crew path keeps an empty list, so this never fires for a
    # crewmate and the scan is unchanged for crewmate prompts.
    if fellow_impostor_ids and role.strip().upper() != "IMPOSTOR":
        raise AssertionError(
            "fellow_impostor_ids leaked into a non-impostor prompt: "
            f"role={role!r}, fellow_impostor_ids={fellow_impostor_ids!r}"
        )
    payload: dict[str, JsonValue] = {
        # ``fellow_impostor_ids`` sits beside ``role`` in the allow-listed
        # self-channel: legitimate impostor-only data, role-neutral ids.
        "self_state": {"role": role, "fellow_impostor_ids": list(fellow_impostor_ids)},
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


def _exclude_teammate_incriminating_observations(
    observations: tuple[ObservationClaim, ...],
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> tuple[ObservationClaim, ...]:
    """Strip ``saw_player`` observations that publicly place a fellow impostor.

    The Task 8.7 :class:`~meetings.schemas.MeetingTurn` schema adds an
    ``observations`` channel to every turn-kind (the old ``Statement`` carried
    none). A ``saw_player`` observation naming a teammate would let an impostor
    publicly place a fellow impostor near the body / a crewmate -- incriminating
    them through the observation channel and bypassing
    :func:`~meetings.manager.exclude_teammate_accusation_claims`, which only
    guards accusation *claims*. This deterministic backstop extends the Task
    7.12 firewall (DESIGN.md §5.2: "an impostor never accuses / incriminates /
    votes a fellow impostor") to the observation surface, mirroring the
    belt-and-suspenders precedent of the claim/ballot guards.

    A ``saw_player`` whose ``subject`` is a teammate is dropped entirely (it is
    a public sighting of the teammate); a retained sighting of a non-teammate
    has any teammate ids filtered out of its ``co_present`` list (so a teammate
    is never publicly co-located with the body / accused). ``found_body`` and
    ``completed_task`` name the victim / the speaker's own task -- not a living
    teammate -- so they pass through unchanged.

    A pure function of ``fellow_impostor_ids`` with no RNG and no LLM call, and
    an exact no-op when ``fellow_impostor_ids`` is empty (every crewmate and a
    sole impostor), so replay reconstruction of the committed sets is
    unaffected.
    """

    if not fellow_impostor_ids:
        return observations
    teammates = frozenset(fellow_impostor_ids)
    kept: list[ObservationClaim] = []
    for observation in observations:
        if isinstance(observation, SawPlayerObservation):
            if observation.subject in teammates:
                # Public sighting of a teammate: drop it entirely.
                continue
            if any(player_id in teammates for player_id in observation.co_present):
                observation = observation.model_copy(
                    update={
                        "co_present": tuple(
                            player_id
                            for player_id in observation.co_present
                            if player_id not in teammates
                        )
                    }
                )
        kept.append(observation)
    return tuple(kept)


class StrategicReasoner:
    """Composite memory + prompt + LLM pipeline (DESIGN.md §4.4, §5.2).

    Construction is cheap and side-effect free: it stores references
    to the LLM client, the four prompt callables, and per-call default
    knobs. The reasoner does NOT own any meeting state — every call
    takes the participating agent's memory, identity, and the relevant
    meeting context as explicit kwargs.

    The four prompt callables default to the loader-built wrappers in
    :mod:`agents.strategic.prompts`; tests and the orchestrator may
    inject scripted stubs by passing alternates to the constructor.

    The reasoner is the public surface downstream tasks consume; its
    public type signature is therefore stable. Mirroring the meeting
    manager (DESIGN.md §5.2), every turn — opening, reply, opt-in — and
    the vote pass through the leak scan and the Task 7.12 teammate
    firewall guard.
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
        turn_max_tokens: int = DEFAULT_TURN_MAX_TOKENS,
        turn_temperature: float = DEFAULT_TURN_TEMPERATURE,
        vote_max_tokens: int = DEFAULT_VOTE_MAX_TOKENS,
        vote_temperature: float = DEFAULT_VOTE_TEMPERATURE,
        skip_confidence_threshold: float = DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    ) -> None:
        if token_budget <= 0:
            raise ValueError(f"token_budget must be positive, got {token_budget}")
        if turn_max_tokens <= 0:
            raise ValueError(f"turn_max_tokens must be positive, got {turn_max_tokens}")
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
        self._turn_max_tokens = turn_max_tokens
        self._turn_temperature = turn_temperature
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
        meeting_id: str,
        agent_id: PlayerId,
        role: Role,
        current_tick: int,
        meeting_trigger: str,
        public_transcript: str = "",
        fellow_impostor_ids: tuple[PlayerId, ...] = (),
        trigger: StrategicTrigger = "meeting_report",
    ) -> MeetingTurn:
        """Opening :class:`MeetingTurn` (turn 0) from rendered memory.

        The opening turn (DESIGN.md §5.2 PHASE 1) IS the body report: the
        reporter / emergency caller states findings and accuses one player
        or stays unsure. Routes to the crewmate or impostor template based
        on ``role``. The reasoner is authoritative for the identity fields
        (``turn_id`` = ``"{meeting_id}:turn-0"``, ``turn_index`` = 0,
        ``speaker`` = ``agent_id``, ``turn_kind`` = ``"opening"``,
        ``reply_to`` = ``None``); the LLM-supplied values are discarded
        (the prompt templates explicitly say the manager/reasoner will
        override them).

        ``fellow_impostor_ids`` (Task 7.12) is the impostor's teammate
        list. It is surfaced into the impostor opening prompt and used by
        the deterministic guard below to drop any accusation claim the
        model makes against a teammate. It is ``()`` for a crewmate and a
        sole impostor, where both the prompt block and the guard are
        no-ops, so those turns are byte-unchanged.
        """

        if role not in ("CREWMATE", "IMPOSTOR"):
            raise ValueError(f"role must be 'CREWMATE' or 'IMPOSTOR', got {role!r}")
        if not meeting_id:
            raise ValueError("meeting_id must be a non-empty string")
        _validate_trigger_for_method(
            trigger,
            method="produce_report",
            allowed=_REPORT_ALLOWED_TRIGGERS,
        )
        rendered_memory = render_for_prompt(memory, token_budget=self._token_budget)
        _scan_prompt_inputs(
            rendered_memory=rendered_memory,
            fellow_impostor_ids=fellow_impostor_ids,
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
            fellow_impostor_ids=fellow_impostor_ids,
        )
        response = await self._llm_client.complete(
            prompt=prompt,
            schema=MeetingTurn,
            max_tokens=self._turn_max_tokens,
            temperature=self._turn_temperature,
            call_kind=_TRIGGER_CALL_KIND[trigger],
            agent_id=agent_id,
        )
        parsed = MeetingTurn.model_validate_json(response.text)
        # Teammate firewall guard (Task 7.12): drop accusation claims against a
        # fellow impostor AND strip observations that publicly place a teammate
        # (the MeetingTurn observation channel is a second incrimination
        # surface). No-op when ``fellow_impostor_ids`` is empty, so replay is
        # unaffected.
        guarded_claims = exclude_teammate_accusation_claims(
            parsed.claims, fellow_impostor_ids=fellow_impostor_ids
        )
        guarded_observations = _exclude_teammate_incriminating_observations(
            parsed.observations, fellow_impostor_ids=fellow_impostor_ids
        )
        return parsed.model_copy(
            update={
                "turn_id": _turn_id(meeting_id=meeting_id, turn_index=0),
                "turn_index": 0,
                "speaker": agent_id,
                "turn_kind": "opening",
                "reply_to": None,
                "observations": guarded_observations,
                "claims": guarded_claims,
            }
        )

    async def produce_statement(
        self,
        *,
        memory: AgentMemory,
        meeting_id: str,
        speaker: PlayerId,
        turn_index: int,
        turn_kind: TurnKind,
        transcript: MeetingTranscript,
        prior_turn: MeetingTurn | None = None,
        contradictions: tuple[ContradictionRef, ...] = (),
        fellow_impostor_ids: tuple[PlayerId, ...] = (),
        trigger: StrategicTrigger = "meeting_statement",
    ) -> MeetingTurn:
        """A reactive ``reply`` / ``opt_in`` :class:`MeetingTurn` (DESIGN.md §5.2).

        ``turn_id`` is composed deterministically as
        ``"{meeting_id}:turn-{turn_index}"`` so replay logs can map a turn
        back to its slot without trusting the LLM with the identity. The
        reasoner is authoritative for ``turn_id``, ``turn_index``,
        ``speaker``, ``turn_kind`` and ``reply_to`` (derived from
        ``prior_turn``).

        ``prior_turn`` is the accusing turn this speaker answers — the
        "who accused me" context surfaced into the reactive-turn template.
        It is the prior chain turn on a ``reply`` and ``None`` on a
        terminal ``opt_in`` info-share turn; ``reply_to`` is its
        ``turn_id`` (``None`` when ``prior_turn`` is ``None``).

        ``fellow_impostor_ids`` (Task 7.12) surfaces the teammate block
        into the shared reactive-turn prompt and drives the deterministic
        guard: an accusation claim against a teammate is dropped from the
        recorded claims (which is what the chain reads its next speaker
        off, so the floor never passes to a teammate). No-op for a
        crewmate / sole impostor (empty list).
        """

        if not meeting_id:
            raise ValueError("meeting_id must be a non-empty string")
        if turn_index < 0:
            raise ValueError(f"turn_index must be non-negative, got {turn_index}")
        if turn_kind not in _STATEMENT_TURN_KINDS:
            raise ValueError(
                "produce_statement turn_kind must be one of "
                f"{sorted(_STATEMENT_TURN_KINDS)} (the opening turn is "
                f"produce_report's job); got {turn_kind!r}"
            )
        _validate_trigger_for_method(
            trigger,
            method="produce_statement",
            allowed=_STATEMENT_ALLOWED_TRIGGERS,
        )
        rendered_memory = render_for_prompt(memory, token_budget=self._token_budget)
        _scan_prompt_inputs(
            rendered_memory=rendered_memory,
            fellow_impostor_ids=fellow_impostor_ids,
        )
        # Fail loud on a prior_turn / turn_kind mismatch -- after the leak scan
        # (always run on LLM-bound inputs) but BEFORE spending the LLM call. A
        # ``reply`` answers the accusing turn it follows, so it MUST carry that
        # ``prior_turn``; without it the recorded turn would have
        # ``reply_to=None`` and the transcript could not reconstruct the
        # accusation edge (DESIGN.md §5.2: a reply references the turn it
        # answers). An ``opt_in`` is a terminal info-share turn that answers no
        # specific turn, so it must NOT carry a prior_turn. (AGENTS.md "no
        # silent fallbacks".)
        if turn_kind == "reply" and prior_turn is None:
            raise ValueError(
                "produce_statement(turn_kind='reply') requires a prior_turn (the "
                "accusing turn being answered); a reply must reference the turn it "
                "answers so the transcript can reconstruct the accusation edge"
            )
        if turn_kind == "opt_in" and prior_turn is not None:
            raise ValueError(
                "produce_statement(turn_kind='opt_in') must not take a prior_turn; an "
                "opt-in info-share turn is terminal and answers no specific turn"
            )
        prompt = self._statement_prompt(
            agent_id=speaker,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradictions=contradictions,
            prior_turn=prior_turn,
            turn_kind=turn_kind,
            fellow_impostor_ids=fellow_impostor_ids,
        )
        response = await self._llm_client.complete(
            prompt=prompt,
            schema=MeetingTurn,
            max_tokens=self._turn_max_tokens,
            temperature=self._turn_temperature,
            call_kind=_TRIGGER_CALL_KIND[trigger],
            agent_id=speaker,
        )
        parsed = MeetingTurn.model_validate_json(response.text)
        # Teammate firewall guard (Task 7.12): drop accusation claims against a
        # fellow impostor AND strip observations that publicly place a teammate.
        # Because the chain passes the floor to the player a turn accuses,
        # stripping the teammate accusation keeps an impostor from handing the
        # chain to a teammate; stripping a teammate-naming ``saw_player`` closes
        # the observation channel the MeetingTurn schema added. No-op when empty.
        guarded_claims = exclude_teammate_accusation_claims(
            parsed.claims, fellow_impostor_ids=fellow_impostor_ids
        )
        guarded_observations = _exclude_teammate_incriminating_observations(
            parsed.observations, fellow_impostor_ids=fellow_impostor_ids
        )
        reply_to = prior_turn.turn_id if prior_turn is not None else None
        return parsed.model_copy(
            update={
                "turn_id": _turn_id(meeting_id=meeting_id, turn_index=turn_index),
                "turn_index": turn_index,
                "speaker": speaker,
                "turn_kind": turn_kind,
                "reply_to": reply_to,
                "observations": guarded_observations,
                "claims": guarded_claims,
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
        fellow_impostor_ids: tuple[PlayerId, ...] = (),
        trigger: StrategicTrigger = "meeting_vote",
    ) -> VoteBallot:
        """Phase-4 :class:`VoteBallot` from rendered memory + transcript.

        The reasoner is authoritative for the ``voter`` field; the LLM
        is told to emit it but any value it returns is overwritten with
        the canonical caller-supplied id. Defensive normalization of an
        invalid ``target`` value is the meeting manager's responsibility
        (DESIGN.md §5.5 + meeting-manager contract), not the reasoner's.

        ``fellow_impostor_ids`` (Task 7.12) surfaces the teammate block
        into the ballot prompt and drives the deterministic guard: a
        ballot whose ``target`` is a fellow impostor is coerced to
        ``SKIP`` so an impostor can never cast the betrayal vote that
        ejects a teammate. No-op for a crewmate / sole impostor.
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
        _scan_prompt_inputs(
            rendered_memory=rendered_memory,
            fellow_impostor_ids=fellow_impostor_ids,
        )
        prompt = self._vote_prompt(
            voter_id=voter,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradiction_flags=contradiction_flags,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=threshold,
            fellow_impostor_ids=fellow_impostor_ids,
        )
        response = await self._llm_client.complete(
            prompt=prompt,
            schema=VoteBallot,
            max_tokens=self._vote_max_tokens,
            temperature=self._vote_temperature,
            call_kind=_TRIGGER_CALL_KIND[trigger],
            agent_id=voter,
        )
        parsed = VoteBallot.model_validate_json(response.text)
        # Teammate firewall guard (Task 7.12): a teammate is a valid
        # living candidate, so coerce a teammate-targeted ballot to SKIP
        # here. No-op when ``fellow_impostor_ids`` is empty.
        guarded = coerce_teammate_ballot_to_skip(
            ballot=parsed.model_copy(update={"voter": voter}),
            fellow_impostor_ids=fellow_impostor_ids,
        )
        return guarded


def _turn_id(*, meeting_id: str, turn_index: int) -> str:
    """The canonical turn id ``"{meeting_id}:turn-{turn_index}"`` (DESIGN.md §5.2).

    Mirrors :func:`meetings.manager._turn_id`: keyed on the turn ordinal,
    not the speaker, so it is unique even when a player speaks twice and a
    :attr:`VoteBallot.primary_reason_id` can reference it.
    """

    return f"{meeting_id}:turn-{turn_index}"


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
