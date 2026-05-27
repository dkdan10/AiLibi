"""Meeting state machine (DESIGN.md §5.1, §5.2).

:class:`MeetingManager` runs one meeting end-to-end. It is constructed
with the LLM client, the four prompt callables (Tasks 3.4-3.7 jinja
templates wrapped as Python callables), and a deadline configuration.
:meth:`MeetingManager.run` is a no-op until the orchestrator (Task
3.12) invokes it with a :class:`MeetingTrigger`; from there the manager
sequences report intake -> accusation rounds -> voting -> resolution
per DESIGN.md §5.2 and returns a :class:`MeetingResult`.

The manager NEVER mutates engine state. It only reads agent-side
inputs (rendered memory, role, suspicion graph) supplied by the
orchestrator and emits a :class:`MeetingResult` DTO. The orchestrator
applies the outcome to engine-owned state per DESIGN.md §5.1.

Statement-ordering contract (C-3, audit
``audits/audit-2026-05-16-0611-claude.md``)
============================================================

This module implements **option (a)** of the C-3 directive:
producer-guaranteed canonical order. The
``MeetingResult.transcript.statements`` tuple is sorted by
``(round_index, insertion_order)``. Insertion order within a round
is the speaker order returned by :func:`_speaker_order`: a true
round-robin cyclic rotation of the canonical sorted ``agent_id``
sequence so that ``trigger.triggered_by`` is at index 0. With
sorted ids ``[p-1, p-2, p-3, p-4]`` and reporter ``p-2`` the order
is ``[p-2, p-3, p-4, p-1]`` (DESIGN.md §5.2 "round-robin starting
from reporter"). Default no-statement entries from deadline
timeouts share their speaker's insertion slot.

Consumers may read ``transcript.statements`` in tuple order and trust
that statements are sorted by ``(round_index, insertion_order)``
without re-sorting. The pin test
``tests/meetings/test_manager.py::TestStatementOrderingContract``
fails against any implementation that violates this contract.
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine, Sequence
from dataclasses import dataclass, field
from typing import Any, Final, Literal, Protocol, TypeVar, runtime_checkable

from llm.client import LLMClient
from meetings.schemas import (
    AlibiClaim,
    Claim,
    ContradictionRef,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    PlayerId,
    ReportDocument,
    Statement,
    VoteBallot,
)

Role = Literal["CREWMATE", "IMPOSTOR"]

# Protocol-default deadline values (DESIGN.md §5.2 default: T1 = 30 s,
# T2 = 30 s, R = 2 rounds; statement deadline matches the report
# deadline since both gate one LLM call per agent).
DEFAULT_ROUND_COUNT: Final[int] = 2
DEFAULT_REPORT_DEADLINE_SECONDS: Final[float] = 30.0
DEFAULT_STATEMENT_DEADLINE_SECONDS: Final[float] = 30.0
DEFAULT_VOTE_DEADLINE_SECONDS: Final[float] = 30.0
DEFAULT_SKIP_CONFIDENCE_THRESHOLD: Final[float] = 0.6

# LLM-call settings. Kept conservative for the meeting protocol; Task
# 3.9 (strategic reasoner) may want to expose these through the
# orchestrator. Public defaults so the orchestrator can override per
# call without monkey-patching constants.
#
# The report and statement budgets are the largest: a ReportDocument
# and a multi-claim Statement are the most verbose meeting artifacts
# (observations, claims, and free-text prose in one object), and too
# tight a cap truncates the model mid-JSON into an unterminated string
# that fails to parse. Vote ballots are smaller but get the same
# defense-in-depth headroom.
DEFAULT_REPORT_MAX_TOKENS: Final[int] = 2048
DEFAULT_REPORT_TEMPERATURE: Final[float] = 0.4
DEFAULT_STATEMENT_MAX_TOKENS: Final[int] = 2048
DEFAULT_STATEMENT_TEMPERATURE: Final[float] = 0.4
DEFAULT_VOTE_MAX_TOKENS: Final[int] = 1024
DEFAULT_VOTE_TEMPERATURE: Final[float] = 0.2

# Free-text recorded on the transcript when a participant misses a
# deadline. The audit-trail requirement in DESIGN.md §5.2 means we
# always record *something* on timeout; these strings are the canonical
# audit markers downstream code (replay, eval) can pattern-match on.
DEFAULT_REPORT_FREE_TEXT: Final[str] = "(missed deadline; no report submitted)"
DEFAULT_STATEMENT_FREE_TEXT: Final[str] = "(missed deadline; no statement)"
DEFAULT_VOTE_RATIONALE: Final[str] = "(missed deadline; default skip)"

# Audit-trail marker prefix prepended to ``rationale_text`` when the LLM
# returns a ``target`` that is neither ``"SKIP"`` nor a valid candidate.
# Such a ballot is defensively normalized to ``SKIP`` so the tally cannot
# be corrupted by a hallucinated player id; the marker preserves the
# original (invalid) target for replay analysis.
INVALID_VOTE_TARGET_MARKER: Final[str] = (
    "[invalid target {target!r} normalized to SKIP] "
)

_SKIP_TARGET: Final[str] = "SKIP"
_VALID_ROLES: Final[frozenset[str]] = frozenset({"CREWMATE", "IMPOSTOR"})

# Self-alibi placeholder subjects the model occasionally emits in an
# ``AlibiClaim`` instead of its own canonical player id. Each leaks a
# prompt-template / few-shot artifact into the structured ``subject``
# field; :func:`_normalize_self_alibi_subjects` rewrites them to the
# speaker's id so DESIGN.md §5.4 contradiction detection can match the
# claim across speakers (Task 3.20):
#
# * ``"self"``         -- Task 3.18 reference token (prompt-fix covered;
#                          kept here for defense-in-depth).
# * ``"p-self"``       -- the ``p-`` sibling-example prefix concatenated
#                          with the ``self`` token; the post-3.18
#                          prompt-only fix did not catch this variant.
# * ``"{{ agent_id }}"`` -- an unrendered Jinja placeholder; only
#                          reachable via a template rendering bug, but
#                          rewriting it costs nothing and fails safe.
_SELF_ALIBI_PLACEHOLDERS: Final[frozenset[str]] = frozenset(
    {
        "self",
        "p-self",
        "{{ agent_id }}",
    }
)


_T = TypeVar("_T")


class LLMProviderError(RuntimeError):
    """LLM provider / transport failure (e.g. SDK or network timeout).

    Distinct from :class:`asyncio.TimeoutError` raised by the
    manager's per-phase deadlines (:class:`MeetingDeadlines`). In
    Python 3.11+ :class:`asyncio.TimeoutError` is an alias of
    built-in :class:`TimeoutError`, so without an explicit conversion
    the manager's deadline handler would silently coerce provider
    timeouts into default no-report / no-statement / default-skip
    entries. This class is the canonical infrastructure-failure
    signal; meeting callers can catch it explicitly (e.g. for retry
    or for a kill-meeting decision in the orchestrator).
    """


async def _isolate_provider_timeout(
    coro: Coroutine[Any, Any, _T],
) -> _T:
    """Re-tag any inner :class:`TimeoutError` as :class:`LLMProviderError`.

    Used to wrap LLM client calls before they are passed to
    :func:`asyncio.wait_for`. Without this, the manager's
    ``except asyncio.TimeoutError`` handler cannot distinguish a
    deadline-driven cancellation from an infrastructure timeout
    surfaced by the provider's own transport / SDK, and would default
    the participant's response when it should fail loud (AGENTS.md
    "no silent fallbacks").
    """

    try:
        return await coro
    except TimeoutError as e:
        raise LLMProviderError("LLM provider timeout") from e


async def _gather_all_or_cancel(
    coros: list[Coroutine[Any, Any, _T]],
) -> tuple[_T, ...]:
    """Run coroutines concurrently, cancelling siblings on failure.

    Replaces :func:`asyncio.gather` which propagates the first
    exception but lets sibling coroutines keep running -- leaking
    LLM token spend and side effects after the caller has already
    decided to fail. :class:`asyncio.TaskGroup` (Python 3.11+) gives
    the all-or-nothing semantics we want: any task failure cancels
    every sibling.

    Successful runs return results in input order (matching the
    previous ``gather()`` shape). On failure the resulting
    :class:`BaseExceptionGroup` is unwrapped to the first underlying
    exception so callers see a regular single exception (matching
    the previous ``gather()`` semantics) instead of an exception
    group. Cancellation already prevents follow-on side effects;
    surfacing every concurrent failure to the caller would force
    every call site to learn the exception-group API for no
    additional debugging value.
    """

    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(coro) for coro in coros]
    except BaseExceptionGroup as eg:
        raise eg.exceptions[0] from None
    return tuple(task.result() for task in tasks)


@dataclass(frozen=True)
class SuspicionEntry:
    """One row of the agent's suspicion graph (DESIGN.md §5.5).

    Surfaced verbatim into the vote-ballot prompt. The fields mirror
    :class:`agents.memory.beliefs.PlayerBelief` so the strategic
    reasoner (Task 3.9) can map a belief snapshot into this DTO
    without re-shaping it.
    """

    player_id: PlayerId
    suspicion: float
    trust: float


@dataclass(frozen=True)
class MeetingParticipant:
    """One living agent's contribution to the meeting (DESIGN.md §5.1).

    The manager treats this as a static snapshot for the duration of
    the meeting: ``rendered_memory`` is what the §6.6 renderer
    produced when the meeting opened, ``role`` selects which report
    prompt is used, and ``suspicion_graph`` populates the vote-ballot
    prompt input.
    """

    agent_id: PlayerId
    role: Role
    rendered_memory: str
    suspicion_graph: tuple[SuspicionEntry, ...] = ()


@dataclass(frozen=True)
class MeetingTrigger:
    """Why the meeting was opened (DESIGN.md §5.1).

    The orchestrator constructs this from the engine event that
    transitioned the world into ``MEETING`` phase. ``description`` is
    a short free-text summary (e.g. ``"p3 reported p2's body in
    MedBay at tick 410"``) that the report prompt surfaces to the
    LLM.
    """

    triggered_by: PlayerId
    trigger_tick: int
    description: str


@dataclass(frozen=True)
class MeetingDeadlines:
    """Per-phase deadlines (DESIGN.md §1.4, §5.2).

    ``None`` disables the deadline for that phase (headless mode).
    The manager passes the value straight to :func:`asyncio.wait_for`.
    """

    report_seconds: float | None = DEFAULT_REPORT_DEADLINE_SECONDS
    statement_seconds: float | None = DEFAULT_STATEMENT_DEADLINE_SECONDS
    vote_seconds: float | None = DEFAULT_VOTE_DEADLINE_SECONDS


@dataclass(frozen=True)
class MeetingConfig:
    """Meeting protocol configuration (DESIGN.md §5.2)."""

    round_count: int = DEFAULT_ROUND_COUNT
    deadlines: MeetingDeadlines = field(default_factory=MeetingDeadlines)
    skip_confidence_threshold: float = DEFAULT_SKIP_CONFIDENCE_THRESHOLD
    report_max_tokens: int = DEFAULT_REPORT_MAX_TOKENS
    report_temperature: float = DEFAULT_REPORT_TEMPERATURE
    statement_max_tokens: int = DEFAULT_STATEMENT_MAX_TOKENS
    statement_temperature: float = DEFAULT_STATEMENT_TEMPERATURE
    vote_max_tokens: int = DEFAULT_VOTE_MAX_TOKENS
    vote_temperature: float = DEFAULT_VOTE_TEMPERATURE


@runtime_checkable
class ReportPromptRenderer(Protocol):
    """Render a Phase-1 report prompt (DESIGN.md §5.2, §5.3).

    The manager dispatches to the crewmate or impostor renderer based
    on :attr:`MeetingParticipant.role`. Template inputs match the
    Jinja2 surface in ``agents/strategic/prompts/{crewmate,impostor}_report.j2``
    (Tasks 3.4 + 3.5). ``public_transcript`` is the empty string at
    Phase-1 since no statements have been made yet.
    """

    def __call__(
        self,
        *,
        agent_id: PlayerId,
        current_tick: int,
        meeting_trigger: str,
        rendered_memory: str,
        public_transcript: str,
    ) -> str: ...


@runtime_checkable
class StatementPromptRenderer(Protocol):
    """Render an accusation-round prompt (DESIGN.md §5.2, §5.3).

    Template inputs match
    ``agents/strategic/prompts/accusation_round.j2`` (Task 3.6).
    ``agent_id`` is the speaker's own player id; it anchors the
    self-alibi example in the template to a concrete id so the model
    does not mis-substitute a placeholder (Task 3.20, matching the
    ``ReportPromptRenderer`` ``agent_id`` thread from Task 3.18).
    ``transcript`` is the transcript-so-far including all prior
    rounds' statements in canonical order; ``contradictions`` is the
    :class:`ContradictionRef` flags that Task 3.11 will populate
    (empty for now).
    """

    def __call__(
        self,
        *,
        agent_id: PlayerId,
        rendered_memory: str,
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
    ) -> str: ...


@runtime_checkable
class VotePromptRenderer(Protocol):
    """Render a vote-ballot prompt (DESIGN.md §5.5).

    Template inputs match ``agents/strategic/prompts/vote_ballot.j2``
    (Task 3.7). ``candidate_targets`` is the explicit set of living
    eject targets (every living participant except the voter);
    ``skip_confidence_threshold`` matches
    :attr:`MeetingConfig.skip_confidence_threshold`.
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
    ) -> str: ...


class MeetingManager:
    """State machine that runs one meeting end-to-end (DESIGN.md §5.1, §5.2).

    Construction is cheap and side-effect free: it stores references
    to the LLM client, the four prompt callables, and the config.
    Nothing runs until :meth:`run` is invoked, which is the trigger
    lifecycle in DESIGN.md §5.1.

    :meth:`run` sequences the four phases:

    1. **Report intake** -- parallel ``ReportDocument`` collection from
       every living participant. Crewmates use the crewmate prompt;
       impostors use the impostor prompt.
    2. **Accusation rounds** -- ``config.round_count`` sequential
       rounds (default 2). Within each round, participants speak in
       true round-robin order: the canonical sorted ``agent_id``
       sequence rotated so ``trigger.triggered_by`` is at index 0
       (see :func:`_speaker_order`).
    3. **Voting** -- parallel ``VoteBallot`` collection from every
       living participant.
    4. **Resolution** -- plurality tally produces the
       :class:`MeetingOutcome` and the :class:`MeetingResult`.

    The manager returns the result without mutating engine state. The
    orchestrator (Task 3.12) applies the outcome to engine-owned
    state.

    Statement-ordering contract: see module docstring. Statements are
    emitted into the transcript in canonical
    ``(round_index, insertion_order)`` order; consumers may rely on
    that order without re-sorting.
    """

    def __init__(
        self,
        *,
        llm_client: LLMClient,
        crewmate_report_prompt: ReportPromptRenderer,
        impostor_report_prompt: ReportPromptRenderer,
        statement_prompt: StatementPromptRenderer,
        vote_prompt: VotePromptRenderer,
        config: MeetingConfig | None = None,
    ) -> None:
        if config is None:
            config = MeetingConfig()
        if config.round_count < 1:
            raise ValueError(
                f"MeetingConfig.round_count must be >= 1, got {config.round_count}"
            )
        if not 0.0 <= config.skip_confidence_threshold <= 1.0:
            raise ValueError(
                "MeetingConfig.skip_confidence_threshold must be in [0, 1], "
                f"got {config.skip_confidence_threshold}"
            )
        # Reject misconfigured deadlines fail-loud. A negative or zero
        # deadline reaches ``asyncio.wait_for`` and trips ``TimeoutError``
        # before the LLM call can complete, silently routing every
        # participant into the default no-report/no-statement/skip path.
        # That would change meeting outcomes without any explicit
        # configuration error (AGENTS.md "no silent fallbacks").
        # ``None`` is the explicit opt-out (headless mode, §1.4).
        for name, value in (
            ("report_seconds", config.deadlines.report_seconds),
            ("statement_seconds", config.deadlines.statement_seconds),
            ("vote_seconds", config.deadlines.vote_seconds),
        ):
            if value is None:
                continue
            if value <= 0:
                raise ValueError(
                    f"MeetingDeadlines.{name} must be None or > 0, got {value}"
                )
        self._llm_client = llm_client
        self._crewmate_report_prompt = crewmate_report_prompt
        self._impostor_report_prompt = impostor_report_prompt
        self._statement_prompt = statement_prompt
        self._vote_prompt = vote_prompt
        self._config = config

    async def run(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        participants: Sequence[MeetingParticipant],
    ) -> MeetingResult:
        """Run report intake -> accusation rounds -> voting -> resolution.

        Statement-ordering contract: the returned
        ``MeetingResult.transcript.statements`` is sorted by
        ``(round_index, insertion_order)`` per option (a) of the C-3
        directive (see module docstring). Insertion order within a
        round is the true round-robin speaker order returned by
        :func:`_speaker_order`: the canonical sorted ``agent_id``
        sequence cyclically rotated so ``trigger.triggered_by`` is at
        index 0. ``trigger.triggered_by`` MUST be present in
        ``participants`` -- a non-participant reporter is rejected at
        entry rather than silently demoted to sorted-only order.
        Default no-statement entries from missed deadlines share their
        speaker's insertion slot. Consumers may read
        ``transcript.statements`` in tuple order and trust the order
        without re-sorting.
        """

        if not meeting_id:
            raise ValueError("meeting_id must be a non-empty string")
        if not participants:
            raise ValueError(
                "MeetingManager.run requires at least one living participant"
            )
        self._validate_participants(participants, trigger=trigger)

        # Canonicalise participant order at entry. Real callers may
        # iterate over a set/dict whose order is hash-seeded and not
        # determinism-preserving; without this normalisation, the
        # transcript ordering, the report order embedded into every
        # statement prompt, and the gather()'d ballot order would all
        # drift between runs with the same seed. Sorting by ``agent_id``
        # is deterministic and matches the lexical ``p-N`` convention
        # used everywhere else in the project.
        ordered_participants = tuple(sorted(participants, key=lambda p: p.agent_id))

        # Phase 1: report intake (parallel).
        reports = await self._collect_reports(
            trigger=trigger, participants=ordered_participants
        )

        # Phase 2: accusation rounds (sequential rounds, ordered speakers).
        contradictions: tuple[ContradictionRef, ...] = ()
        speaker_order = _speaker_order(
            participants=ordered_participants, trigger=trigger
        )
        statements: list[Statement] = []
        for round_index in range(self._config.round_count):
            for participant in speaker_order:
                statement = await self._collect_statement(
                    meeting_id=meeting_id,
                    trigger=trigger,
                    participant=participant,
                    round_index=round_index,
                    transcript_so_far=MeetingTranscript(
                        reports=reports, statements=tuple(statements)
                    ),
                    contradictions=contradictions,
                )
                statements.append(statement)
        transcript = MeetingTranscript(reports=reports, statements=tuple(statements))

        # Phase 3: voting (parallel).
        ballots = await self._collect_ballots(
            trigger=trigger,
            participants=ordered_participants,
            transcript=transcript,
            contradictions=contradictions,
        )

        # Phase 4: resolution.
        outcome, ejected = self._tally(ballots)
        return MeetingResult(
            meeting_id=meeting_id,
            triggered_by=trigger.triggered_by,
            trigger_tick=trigger.trigger_tick,
            outcome=outcome,
            ejected_player_id=ejected,
            ballots=ballots,
            contradictions=contradictions,
            transcript=transcript,
        )

    # -- Phase 1: report intake -------------------------------------------

    async def _collect_reports(
        self,
        *,
        trigger: MeetingTrigger,
        participants: Sequence[MeetingParticipant],
    ) -> tuple[ReportDocument, ...]:
        # All-or-nothing parallel collection: if any single report
        # fails (provider error, parse error, etc.) the sibling LLM
        # calls are cancelled before they incur additional token
        # spend. Successful results preserve input order so the
        # transcript ordering test still holds.
        coroutines: list[Coroutine[Any, Any, ReportDocument]] = [
            self._collect_one_report(trigger=trigger, participant=participant)
            for participant in participants
        ]
        return await _gather_all_or_cancel(coroutines)

    async def _collect_one_report(
        self,
        *,
        trigger: MeetingTrigger,
        participant: MeetingParticipant,
    ) -> ReportDocument:
        renderer = (
            self._impostor_report_prompt
            if participant.role == "IMPOSTOR"
            else self._crewmate_report_prompt
        )
        prompt = renderer(
            agent_id=participant.agent_id,
            current_tick=trigger.trigger_tick,
            meeting_trigger=trigger.description,
            rendered_memory=participant.rendered_memory,
            public_transcript="",
        )
        try:
            response = await asyncio.wait_for(
                _isolate_provider_timeout(
                    self._llm_client.complete(
                        prompt=prompt,
                        schema=ReportDocument,
                        max_tokens=self._config.report_max_tokens,
                        temperature=self._config.report_temperature,
                        call_kind="meeting",
                        agent_id=participant.agent_id,
                    )
                ),
                timeout=self._config.deadlines.report_seconds,
            )
        except asyncio.TimeoutError:
            return _default_report(
                agent_id=participant.agent_id, tick=trigger.trigger_tick
            )
        parsed = ReportDocument.model_validate_json(response.text)
        # Defense-in-depth: rewrite self-alibi placeholder subjects
        # (e.g. "p-self") to the speaker's canonical id before the
        # identity override, so DESIGN.md §5.4 contradiction detection
        # can match this report's self-alibi against other speakers
        # (Task 3.20).
        normalized_claims = _normalize_self_alibi_subjects(
            parsed.claims, speaker_id=participant.agent_id
        )
        # Override identity fields with the canonical values; the LLM
        # is told to emit any non-empty string and the manager is
        # authoritative for who said what (see crewmate_report.j2 line
        # 64 and impostor_report.j2 "the reasoner will override").
        return parsed.model_copy(
            update={
                "agent_id": participant.agent_id,
                "tick": trigger.trigger_tick,
                "claims": normalized_claims,
            }
        )

    # -- Phase 2: accusation rounds ---------------------------------------

    async def _collect_statement(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        participant: MeetingParticipant,
        round_index: int,
        transcript_so_far: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
    ) -> Statement:
        prompt = self._statement_prompt(
            agent_id=participant.agent_id,
            rendered_memory=participant.rendered_memory,
            transcript=transcript_so_far,
            contradictions=contradictions,
        )
        statement_id = _statement_id(
            meeting_id=meeting_id,
            round_index=round_index,
            speaker=participant.agent_id,
        )
        try:
            response = await asyncio.wait_for(
                _isolate_provider_timeout(
                    self._llm_client.complete(
                        prompt=prompt,
                        schema=Statement,
                        max_tokens=self._config.statement_max_tokens,
                        temperature=self._config.statement_temperature,
                        call_kind="meeting",
                        agent_id=participant.agent_id,
                    )
                ),
                timeout=self._config.deadlines.statement_seconds,
            )
        except asyncio.TimeoutError:
            return _default_statement(
                statement_id=statement_id,
                speaker=participant.agent_id,
                tick=trigger.trigger_tick,
                round_index=round_index,
            )
        parsed = Statement.model_validate_json(response.text)
        # Defense-in-depth: rewrite self-alibi placeholder subjects
        # (e.g. "p-self") to the speaker's canonical id before the
        # identity override, so DESIGN.md §5.4 contradiction detection
        # can match this turn's self-alibi against other speakers
        # (Task 3.20).
        normalized_claims = _normalize_self_alibi_subjects(
            parsed.claims, speaker_id=participant.agent_id
        )
        # Override identity fields. The accusation_round.j2 contract
        # is "the orchestrator fills the deterministic identity
        # fields (statement_id, speaker, tick, round_index)".
        return parsed.model_copy(
            update={
                "statement_id": statement_id,
                "speaker": participant.agent_id,
                "tick": trigger.trigger_tick,
                "round_index": round_index,
                "claims": normalized_claims,
            }
        )

    # -- Phase 3: voting --------------------------------------------------

    async def _collect_ballots(
        self,
        *,
        trigger: MeetingTrigger,
        participants: Sequence[MeetingParticipant],
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
    ) -> tuple[VoteBallot, ...]:
        # All-or-nothing parallel collection: see _collect_reports
        # docstring. A failing ballot cancels siblings so the tally
        # is not corrupted by partially-collected votes.
        coroutines: list[Coroutine[Any, Any, VoteBallot]] = [
            self._collect_one_ballot(
                trigger=trigger,
                participant=participant,
                participants=participants,
                transcript=transcript,
                contradictions=contradictions,
            )
            for participant in participants
        ]
        return await _gather_all_or_cancel(coroutines)

    async def _collect_one_ballot(
        self,
        *,
        trigger: MeetingTrigger,
        participant: MeetingParticipant,
        participants: Sequence[MeetingParticipant],
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
    ) -> VoteBallot:
        candidate_targets = tuple(
            sorted(
                other.agent_id
                for other in participants
                if other.agent_id != participant.agent_id
            )
        )
        prompt = self._vote_prompt(
            voter_id=participant.agent_id,
            rendered_memory=participant.rendered_memory,
            transcript=transcript,
            contradiction_flags=contradictions,
            suspicion_graph=participant.suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=self._config.skip_confidence_threshold,
        )
        try:
            response = await asyncio.wait_for(
                _isolate_provider_timeout(
                    self._llm_client.complete(
                        prompt=prompt,
                        schema=VoteBallot,
                        max_tokens=self._config.vote_max_tokens,
                        temperature=self._config.vote_temperature,
                        call_kind="meeting",
                        agent_id=participant.agent_id,
                    )
                ),
                timeout=self._config.deadlines.vote_seconds,
            )
        except asyncio.TimeoutError:
            return _default_vote(voter=participant.agent_id)
        parsed = VoteBallot.model_validate_json(response.text)
        # Defensive normalization: if the LLM hallucinates a target id
        # that is not in ``candidate_targets`` (and not ``"SKIP"``),
        # ``_tally`` would otherwise count it as a real eject and could
        # resolve to ``EJECTED`` with a non-participant id, corrupting
        # outcome application and replay integrity. Replace the target
        # with ``"SKIP"`` and mark the rationale so the original (bad)
        # target is preserved for audit / replay.
        normalized = _normalize_ballot_target(
            ballot=parsed, candidate_targets=candidate_targets
        )
        return normalized.model_copy(update={"voter": participant.agent_id})

    # -- Phase 4: resolution ----------------------------------------------

    def _tally(
        self,
        ballots: Sequence[VoteBallot],
    ) -> tuple[MeetingOutcome, PlayerId | None]:
        """Plurality tally with confidence threshold (DESIGN.md §5.2 + §4.6 + §5.5).

        ``SKIP`` is a real tally target -- a vote of ``SKIP`` competes
        with non-``SKIP`` votes for plurality. Two reads from the
        protocol motivate this:

        * DESIGN.md §5.5 schemas ``VoteBallot.target`` as
          ``PlayerId | Literal["SKIP"]`` -- ``SKIP`` is a first-class
          target, not an abstention.
        * DESIGN.md §5.2 PHASE 4 says "If tie or below threshold,
          skip" -- if ``SKIP`` were dropped, a single non-``SKIP``
          vote among many ``SKIP`` s would still eject, which
          contradicts the "below threshold, skip" intent.

        Resolution rules:

        * Empty ballots -> ``SKIPPED`` (no votes to tally).
        * ``SKIP`` has plurality (alone or tied at the top) ->
          ``SKIPPED``. Tied with one or more players is treated as
          skip because the table did not converge on an eject.
        * Two or more non-``SKIP`` targets tied at the top ->
          ``SKIPPED`` (DESIGN.md §5.2: "if tie ... skip"). The
          schema-level ``TIE`` outcome was deliberately removed in
          this task because DESIGN.md only defines ejection-or-skip.
        * Single non-``SKIP`` target with strict plurality AND at
          least one ballot for that target has ``confidence >=
          skip_confidence_threshold`` -> ``EJECTED``.
        * Otherwise (strict plurality but no confident ballot) ->
          ``SKIPPED``. This is the mechanical "meets threshold"
          check from DESIGN.md §5.2 PHASE 4: the tally enforces it
          independent of LLM compliance with the vote prompt's
          ``skip_confidence_threshold`` instruction. The "max
          confidence across the target's ballots" reading matches
          DESIGN.md §4.6 "max suspicion confidence < 0.6 ... skip" --
          the eject requires at least one voter to be confident, not
          all of them.

        Task 3.10 (``meetings/voting.py``) may refactor this body
        into a dedicated module; the threshold semantics above are
        the protocol contract and should be preserved across the
        refactor.
        """

        tallies: dict[str, int] = {}
        for ballot in ballots:
            tallies[ballot.target] = tallies.get(ballot.target, 0) + 1
        if not tallies:
            return "SKIPPED", None
        max_votes = max(tallies.values())
        leaders = sorted(
            target for target, count in tallies.items() if count == max_votes
        )
        if _SKIP_TARGET in leaders:
            return "SKIPPED", None
        if len(leaders) > 1:
            return "SKIPPED", None
        leader = leaders[0]
        threshold = self._config.skip_confidence_threshold
        leader_max_confidence = max(
            ballot.confidence for ballot in ballots if ballot.target == leader
        )
        if leader_max_confidence < threshold:
            return "SKIPPED", None
        return "EJECTED", leader

    @staticmethod
    def _validate_participants(
        participants: Sequence[MeetingParticipant],
        *,
        trigger: MeetingTrigger,
    ) -> None:
        seen: set[PlayerId] = set()
        for participant in participants:
            if participant.agent_id in seen:
                raise ValueError(
                    "MeetingManager.run participants must have unique agent_ids; "
                    f"duplicate: {participant.agent_id!r}"
                )
            seen.add(participant.agent_id)
            # ``MeetingParticipant`` is a runtime dataclass; the
            # ``Role`` ``Literal`` is enforced by mypy --strict at the
            # call site but not at runtime. A typo like ``"impostor"``
            # or ``"UNKNOWN"`` would otherwise fall through the
            # ``role == "IMPOSTOR"`` check in ``_collect_one_report``
            # and silently route the agent to the crewmate prompt,
            # which would be hard to diagnose. Fail-loud at entry.
            if participant.role not in _VALID_ROLES:
                raise ValueError(
                    "MeetingParticipant.role must be one of "
                    f"{sorted(_VALID_ROLES)}; got {participant.role!r} "
                    f"for agent {participant.agent_id!r}"
                )
        # The protocol requires round-robin starting from the reporter
        # (DESIGN.md §5.2). A trigger whose ``triggered_by`` is not in
        # the participant set is an upstream orchestrator bug -- not
        # something to silently demote to sorted-only order. Failing
        # loud here surfaces the wiring error at meeting entry, before
        # any LLM traffic is spent on a transcript whose speaker order
        # is no longer tied to the reporter (AGENTS.md "no silent
        # fallbacks").
        if trigger.triggered_by not in seen:
            raise ValueError(
                f"MeetingTrigger.triggered_by={trigger.triggered_by!r} is not in "
                f"the participant set ({sorted(seen)}); the protocol requires "
                "the reporter to be a living participant"
            )


def _speaker_order(
    *,
    participants: Sequence[MeetingParticipant],
    trigger: MeetingTrigger,
) -> tuple[MeetingParticipant, ...]:
    """True round-robin order starting from the reporter (DESIGN.md §5.2).

    The canonical sequence is sorted by ``agent_id`` ascending; the
    returned tuple is that sequence rotated so the reporter
    (``trigger.triggered_by``) is at index 0. With sorted ids
    ``[p-1, p-2, p-3, p-4]`` and reporter ``p-2`` the result is
    ``[p-2, p-3, p-4, p-1]`` -- a cyclic rotation, not "reporter then
    ascending others". This preserves the round-robin semantics from
    DESIGN.md §5.2 where each speaker sees the prior speaker's
    statement in the transcript-so-far and can react to it.

    ``trigger.triggered_by`` MUST be present in ``participants``;
    :meth:`MeetingManager._validate_participants` rejects the meeting
    at entry otherwise. This helper assumes the invariant and raises
    ``ValueError`` if it is violated (defense-in-depth).
    """

    by_id = {p.agent_id: p for p in participants}
    if trigger.triggered_by not in by_id:
        raise ValueError(
            f"_speaker_order: reporter {trigger.triggered_by!r} is not in "
            f"the participant set ({sorted(by_id)}); this is a wiring bug, "
            "MeetingManager._validate_participants should have rejected it"
        )
    sorted_ids = sorted(by_id)
    reporter_index = sorted_ids.index(trigger.triggered_by)
    rotated = sorted_ids[reporter_index:] + sorted_ids[:reporter_index]
    return tuple(by_id[agent_id] for agent_id in rotated)


def _statement_id(*, meeting_id: str, round_index: int, speaker: PlayerId) -> str:
    return f"{meeting_id}:r{round_index}:{speaker}"


def _default_report(*, agent_id: PlayerId, tick: int) -> ReportDocument:
    return ReportDocument(
        agent_id=agent_id,
        tick=tick,
        observations=(),
        claims=(),
        free_text=DEFAULT_REPORT_FREE_TEXT,
    )


def _default_statement(
    *,
    statement_id: str,
    speaker: PlayerId,
    tick: int,
    round_index: int,
) -> Statement:
    return Statement(
        statement_id=statement_id,
        speaker=speaker,
        tick=tick,
        round_index=round_index,
        target=None,
        claims=(),
        free_text=DEFAULT_STATEMENT_FREE_TEXT,
    )


def _default_vote(*, voter: PlayerId) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=_SKIP_TARGET,
        confidence=0.0,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=DEFAULT_VOTE_RATIONALE,
    )


def _normalize_self_alibi_subjects(
    claims: tuple[Claim, ...],
    *,
    speaker_id: PlayerId,
) -> tuple[Claim, ...]:
    """Rewrite known self-alibi placeholder subjects to ``speaker_id``.

    The model occasionally emits ``subject: "self"`` or
    ``subject: "p-self"`` in an :class:`~meetings.schemas.AlibiClaim`,
    leaking a prompt-template / few-shot placeholder into the
    structured ``subject`` field (Task 3.20 Findings 1 & 2). Those
    claims are unambiguously the speaker's own self-alibi; this helper
    rewrites their ``subject`` to the speaker's canonical player id so
    DESIGN.md §5.4 contradiction detection -- which indexes alibis by
    ``(subject, tick_range, location)`` -- can match them against
    other speakers' claims. The full placeholder set is
    :data:`_SELF_ALIBI_PLACEHOLDERS`.

    Out-of-roster pass-through: a ``subject`` that is NOT in the
    self-alibi placeholder set is passed through unchanged. This helper
    deliberately does NOT validate ``subject`` against the meeting's
    player roster; that broader ``PlayerId``-validation refactor is
    explicitly deferred. Rationale: an unknown subject (e.g. a
    hallucinated ``"p-99"`` or an other-player id the speaker invented)
    simply fails to match in contradiction detection, which is no worse
    than today -- the goal of THIS normalizer is to fix only the
    deterministic self-alibi placeholder leaks, not to mechanically
    validate every subject. The contract is "fix the speaker's
    self-alibi only"; non-self alibis MUST pass through untouched.

    Only :class:`~meetings.schemas.AlibiClaim`s are inspected;
    accusation / corroboration claims are returned as-is. The rewrite
    is via ``model_copy`` so frozen-model immutability is preserved.
    """

    normalized: list[Claim] = []
    for claim in claims:
        if isinstance(claim, AlibiClaim) and claim.subject in _SELF_ALIBI_PLACEHOLDERS:
            normalized.append(claim.model_copy(update={"subject": speaker_id}))
        else:
            normalized.append(claim)
    return tuple(normalized)


def _normalize_ballot_target(
    *,
    ballot: VoteBallot,
    candidate_targets: tuple[PlayerId, ...],
) -> VoteBallot:
    """Defensively normalize an LLM-produced ballot target.

    Returns the ballot unchanged when ``target`` is ``"SKIP"`` or in
    ``candidate_targets``. When the LLM hallucinates an unknown id, the
    ballot is rewritten to ``"SKIP"`` with a marker prefix on
    ``rationale_text`` preserving the original (invalid) target. The
    tally cannot then resolve to ``EJECTED`` against a non-participant
    id; the audit trail records what the LLM actually emitted.
    """

    if ballot.target == _SKIP_TARGET or ballot.target in candidate_targets:
        return ballot
    marker = INVALID_VOTE_TARGET_MARKER.format(target=ballot.target)
    return ballot.model_copy(
        update={
            "target": _SKIP_TARGET,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


__all__ = [
    "DEFAULT_REPORT_DEADLINE_SECONDS",
    "DEFAULT_REPORT_FREE_TEXT",
    "DEFAULT_REPORT_MAX_TOKENS",
    "DEFAULT_REPORT_TEMPERATURE",
    "DEFAULT_ROUND_COUNT",
    "DEFAULT_SKIP_CONFIDENCE_THRESHOLD",
    "DEFAULT_STATEMENT_DEADLINE_SECONDS",
    "DEFAULT_STATEMENT_FREE_TEXT",
    "DEFAULT_STATEMENT_MAX_TOKENS",
    "DEFAULT_STATEMENT_TEMPERATURE",
    "DEFAULT_VOTE_DEADLINE_SECONDS",
    "DEFAULT_VOTE_MAX_TOKENS",
    "DEFAULT_VOTE_RATIONALE",
    "DEFAULT_VOTE_TEMPERATURE",
    "INVALID_VOTE_TARGET_MARKER",
    "LLMProviderError",
    "MeetingConfig",
    "MeetingDeadlines",
    "MeetingManager",
    "MeetingParticipant",
    "MeetingTrigger",
    "ReportPromptRenderer",
    "Role",
    "StatementPromptRenderer",
    "SuspicionEntry",
    "VotePromptRenderer",
]
