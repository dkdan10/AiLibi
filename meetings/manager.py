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
matches the manager's speaker order: the meeting opener
(``trigger.triggered_by``) speaks first, then every other living
participant in ascending ``agent_id`` order. Default no-statement
entries from deadline timeouts share their speaker's insertion slot.

Consumers may read ``transcript.statements`` in tuple order and trust
that statements are sorted by ``(round_index, insertion_order)``
without re-sorting. The pin test
``tests/meetings/test_manager.py::TestStatementOrderingContract``
fails against any implementation that violates this contract.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Final, Literal, Protocol, runtime_checkable

from llm.client import LLMClient
from meetings.schemas import (
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
DEFAULT_REPORT_MAX_TOKENS: Final[int] = 1024
DEFAULT_REPORT_TEMPERATURE: Final[float] = 0.4
DEFAULT_STATEMENT_MAX_TOKENS: Final[int] = 512
DEFAULT_STATEMENT_TEMPERATURE: Final[float] = 0.4
DEFAULT_VOTE_MAX_TOKENS: Final[int] = 384
DEFAULT_VOTE_TEMPERATURE: Final[float] = 0.2

# Free-text recorded on the transcript when a participant misses a
# deadline. The audit-trail requirement in DESIGN.md §5.2 means we
# always record *something* on timeout; these strings are the canonical
# audit markers downstream code (replay, eval) can pattern-match on.
DEFAULT_REPORT_FREE_TEXT: Final[str] = "(missed deadline; no report submitted)"
DEFAULT_STATEMENT_FREE_TEXT: Final[str] = "(missed deadline; no statement)"
DEFAULT_VOTE_RATIONALE: Final[str] = "(missed deadline; default skip)"

_SKIP_TARGET: Final[str] = "SKIP"


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
    ``transcript`` is the transcript-so-far including all prior
    rounds' statements in canonical order; ``contradictions`` is the
    :class:`ContradictionRef` flags that Task 3.11 will populate
    (empty for now).
    """

    def __call__(
        self,
        *,
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
       rounds (default 2). Within each round, participants speak
       round-robin starting from ``trigger.triggered_by`` and then
       ascending ``agent_id``.
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
        round is the speaker order:
        ``trigger.triggered_by`` first (if alive), then every other
        living participant in ascending ``agent_id`` order. Default
        no-statement entries from missed deadlines share their
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
        self._validate_unique_participants(participants)

        # Phase 1: report intake (parallel).
        reports = await self._collect_reports(
            trigger=trigger, participants=participants
        )

        # Phase 2: accusation rounds (sequential rounds, ordered speakers).
        contradictions: tuple[ContradictionRef, ...] = ()
        speaker_order = _speaker_order(participants=participants, trigger=trigger)
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
            participants=participants,
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
        # gather() preserves input order in its return, so report order
        # is deterministically participant-input order. The transcript
        # ordering test pins this.
        coroutines = [
            self._collect_one_report(trigger=trigger, participant=participant)
            for participant in participants
        ]
        return tuple(await asyncio.gather(*coroutines))

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
                self._llm_client.complete(
                    prompt=prompt,
                    schema=ReportDocument,
                    max_tokens=self._config.report_max_tokens,
                    temperature=self._config.report_temperature,
                    call_kind="meeting",
                ),
                timeout=self._config.deadlines.report_seconds,
            )
        except asyncio.TimeoutError:
            return _default_report(
                agent_id=participant.agent_id, tick=trigger.trigger_tick
            )
        parsed = ReportDocument.model_validate_json(response.text)
        # Override identity fields with the canonical values; the LLM
        # is told to emit any non-empty string and the manager is
        # authoritative for who said what (see crewmate_report.j2 line
        # 64 and impostor_report.j2 "the reasoner will override").
        return parsed.model_copy(
            update={
                "agent_id": participant.agent_id,
                "tick": trigger.trigger_tick,
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
                self._llm_client.complete(
                    prompt=prompt,
                    schema=Statement,
                    max_tokens=self._config.statement_max_tokens,
                    temperature=self._config.statement_temperature,
                    call_kind="meeting",
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
        # Override identity fields. The accusation_round.j2 contract
        # is "the orchestrator fills the deterministic identity
        # fields (statement_id, speaker, tick, round_index)".
        return parsed.model_copy(
            update={
                "statement_id": statement_id,
                "speaker": participant.agent_id,
                "tick": trigger.trigger_tick,
                "round_index": round_index,
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
        coroutines = [
            self._collect_one_ballot(
                trigger=trigger,
                participant=participant,
                participants=participants,
                transcript=transcript,
                contradictions=contradictions,
            )
            for participant in participants
        ]
        return tuple(await asyncio.gather(*coroutines))

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
                self._llm_client.complete(
                    prompt=prompt,
                    schema=VoteBallot,
                    max_tokens=self._config.vote_max_tokens,
                    temperature=self._config.vote_temperature,
                    call_kind="meeting",
                ),
                timeout=self._config.deadlines.vote_seconds,
            )
        except asyncio.TimeoutError:
            return _default_vote(voter=participant.agent_id)
        parsed = VoteBallot.model_validate_json(response.text)
        return parsed.model_copy(update={"voter": participant.agent_id})

    # -- Phase 4: resolution ----------------------------------------------

    def _tally(
        self,
        ballots: Sequence[VoteBallot],
    ) -> tuple[MeetingOutcome, PlayerId | None]:
        """Plurality tally (DESIGN.md §5.2 PHASE 4).

        Task 3.10 will refactor this into ``meetings/voting.py`` with
        the proper uncertainty-aware skip behavior from DESIGN.md
        §4.6 + §5.5. For Task 3.8 we implement plurality with
        SKIP-as-abstention and tie -> ``TIE``:

        * count votes per non-SKIP target;
        * if the top target's count is strictly greater than every
          other target's count and there is at least one non-SKIP
          vote, the outcome is ``EJECTED``;
        * if two or more targets tie at the top, the outcome is
          ``TIE``;
        * otherwise (no non-SKIP votes), the outcome is ``SKIPPED``.

        SKIP votes never tie with non-SKIP votes -- a vote of SKIP is
        an abstention from the eject decision.
        """

        tallies: dict[PlayerId, int] = {}
        for ballot in ballots:
            if ballot.target == _SKIP_TARGET:
                continue
            tallies[ballot.target] = tallies.get(ballot.target, 0) + 1
        if not tallies:
            return "SKIPPED", None
        max_votes = max(tallies.values())
        leaders = sorted(
            target for target, count in tallies.items() if count == max_votes
        )
        if len(leaders) > 1:
            return "TIE", None
        return "EJECTED", leaders[0]

    @staticmethod
    def _validate_unique_participants(
        participants: Sequence[MeetingParticipant],
    ) -> None:
        seen: set[PlayerId] = set()
        for participant in participants:
            if participant.agent_id in seen:
                raise ValueError(
                    "MeetingManager.run participants must have unique agent_ids; "
                    f"duplicate: {participant.agent_id!r}"
                )
            seen.add(participant.agent_id)


def _speaker_order(
    *,
    participants: Sequence[MeetingParticipant],
    trigger: MeetingTrigger,
) -> tuple[MeetingParticipant, ...]:
    """Round-robin order starting from the reporter (DESIGN.md §5.2).

    The reporter (``trigger.triggered_by``) speaks first if they are
    among the living participants; the remaining participants speak
    in ascending ``agent_id`` order. If the reporter is not in the
    participant set (e.g. they were ejected before the round started,
    or the trigger came from a non-participant), all participants
    speak in ascending ``agent_id`` order.
    """

    by_id = {p.agent_id: p for p in participants}
    sorted_ids = sorted(by_id)
    reporter = by_id.get(trigger.triggered_by)
    if reporter is None:
        return tuple(by_id[agent_id] for agent_id in sorted_ids)
    others = [agent_id for agent_id in sorted_ids if agent_id != reporter.agent_id]
    return (reporter,) + tuple(by_id[agent_id] for agent_id in others)


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
