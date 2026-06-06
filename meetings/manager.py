"""Meeting state machine (DESIGN.md §5.1, §5.2).

:class:`MeetingManager` runs one meeting end-to-end as the reactive
accusation chain (DESIGN.md §5.2). It is constructed with the LLM
client, the prompt callables (Task 8.8 jinja templates wrapped as Python
callables), and a deadline configuration. :meth:`MeetingManager.run` is a
no-op until the orchestrator invokes it with a :class:`MeetingTrigger`;
from there the manager sequences a single ordered list of **turns** ->
voting -> resolution and returns a :class:`MeetingResult`.

The manager NEVER mutates engine state. It only reads agent-side inputs
(rendered memory, role, suspicion graph) supplied by the orchestrator
and emits a :class:`MeetingResult` DTO. The orchestrator applies the
outcome to engine-owned state per DESIGN.md §5.1.

Reactive accusation chain (DESIGN.md §5.2)
==========================================

A meeting is one ordered ``transcript.turns`` list followed by a vote:

1. **Opening** (turn 0) -- the body-reporter / emergency caller states
   findings and accuses one player or declares "unsure".
2. **Reactive chain** -- the accused responds; the next speaker is
   deterministically the player just accused. The chain terminates when
   the current turn names no new accusation, re-accuses someone who has
   already spoken (cycle), or the turn count reaches the living-player
   count (hard cap). The chain's next speaker and its termination are
   pure functions of the recorded turns (:mod:`meetings.transcript`), so
   a replay reconstructs the chain from ``transcript.turns`` without
   re-calling the model.
3. **Opt-in info-share** -- living non-speakers with a relevant
   observation (a deterministic co-presence gate with the body / the
   accused) each take one terminal turn; an opt-in turn may accuse but
   never extends the chain.
4. **Voting** -- contradictions (§5.4) recompute once over the full
   transcript, then every living agent submits a :class:`VoteBallot`.
5. **Resolution** -- plurality tally with the confidence threshold.

Single per-turn chokepoint
===========================

Every turn -- opening, reply, or opt-in -- is collected through
:meth:`MeetingManager._collect_turn`, so every turn-kind inherits the
same guards: self-alibi subject normalization, the Task 7.12 teammate
firewall (an impostor never accuses / incriminates a fellow impostor),
the strict :class:`~meetings.schemas.AlibiClaim` chronology, and the
Task 7.10 fail-soft (a malformed turn degrades to a default turn rather
than aborting the meeting). The vote inherits the third 7.12 guard,
:func:`coerce_teammate_ballot_to_skip`.
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine, Sequence
from dataclasses import dataclass, field
from typing import Any, Final, Literal, Protocol, TypeVar, runtime_checkable

from pydantic import ValidationError

from agents.memory.beliefs import BeliefState, apply_contradiction_rule
from llm.client import LLMClient
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    ContradictionRef,
    FoundBodyObservation,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
    TurnKind,
    VoteBallot,
)
from meetings.transcript import (
    accusation_target,
    detect_contradictions,
    next_chain_step,
)

Role = Literal["CREWMATE", "IMPOSTOR"]

# Protocol-default deadline values (DESIGN.md §5.2: T_turn = 30 s per turn,
# T2 = 30 s for the vote). The reactive chain replaces the old fixed
# ``round_count`` loop: the meeting's *total* turn cap is the living-player
# count (DESIGN.md §5.2 PHASE 2 condition (c), enforced by
# :func:`meetings.transcript.next_chain_step`), so the deterministic
# "total meeting cap" is structural -- the per-turn deadline below bounds
# each turn's wall-clock, the chain bounds their number.
DEFAULT_TURN_DEADLINE_SECONDS: Final[float] = 30.0
DEFAULT_VOTE_DEADLINE_SECONDS: Final[float] = 30.0
DEFAULT_SKIP_CONFIDENCE_THRESHOLD: Final[float] = 0.6

# LLM-call settings. A :class:`MeetingTurn` (observations + claims +
# free-text prose in one object) is the most verbose meeting artifact, so
# the per-turn budget is the largest; too tight a cap truncates the model
# mid-JSON into an unterminated string that fails to parse. Vote ballots
# are smaller but get the same defense-in-depth headroom. Public defaults
# so the orchestrator can override per call without monkey-patching.
DEFAULT_TURN_MAX_TOKENS: Final[int] = 2048
DEFAULT_TURN_TEMPERATURE: Final[float] = 0.4
DEFAULT_VOTE_MAX_TOKENS: Final[int] = 1024
DEFAULT_VOTE_TEMPERATURE: Final[float] = 0.2

# Free-text recorded on a turn / ballot when a participant misses a
# deadline or emits an unparseable payload. The audit-trail requirement in
# DESIGN.md §5.2 means we always record *something*; these strings are the
# canonical audit markers downstream code (replay, eval) can match on.
DEFAULT_TURN_FREE_TEXT: Final[str] = "(missed deadline; no turn submitted)"
DEFAULT_VOTE_RATIONALE: Final[str] = "(missed deadline; default skip)"

# Audit-trail marker prefix prepended to ``rationale_text`` when the LLM
# returns a ``target`` that is neither ``"SKIP"`` nor a valid candidate.
# Such a ballot is defensively normalized to ``SKIP`` so the tally cannot
# be corrupted by a hallucinated player id; the marker preserves the
# original (invalid) target for replay analysis.
INVALID_VOTE_TARGET_MARKER: Final[str] = (
    "[invalid target {target!r} normalized to SKIP] "
)

# Audit-trail marker prepended to ``rationale_text`` when the teammate
# firewall guard (Task 7.12) coerces a ballot that targets a fellow
# impostor into ``SKIP``. A teammate is a *valid* living candidate, so the
# invalid-target normalization above never catches it; this is the
# belt-and-suspenders deterministic guard that backstops the prompt
# instruction (the 7B model may still emit a teammate target). The marker
# preserves the original (teammate) target for replay / audit analysis.
TEAMMATE_VOTE_TARGET_MARKER: Final[str] = (
    "[teammate target {target!r} coerced to SKIP] "
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
# * ``"self"``         -- reference token (prompt-fix covered; kept here
#                          for defense-in-depth).
# * ``"p-self"``       -- the ``p-`` sibling-example prefix concatenated
#                          with the ``self`` token.
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

    Distinct from :class:`asyncio.TimeoutError` raised by the manager's
    per-turn deadlines (:class:`MeetingDeadlines`). In Python 3.11+
    :class:`asyncio.TimeoutError` is an alias of built-in
    :class:`TimeoutError`, so without an explicit conversion the manager's
    deadline handler would silently coerce provider timeouts into default
    turns / default-skip ballots. This class is the canonical
    infrastructure-failure signal; meeting callers can catch it explicitly
    (e.g. for retry or for a kill-meeting decision in the orchestrator).
    """


async def _isolate_provider_timeout(
    coro: Coroutine[Any, Any, _T],
) -> _T:
    """Re-tag any inner :class:`TimeoutError` as :class:`LLMProviderError`.

    Used to wrap LLM client calls before they are passed to
    :func:`asyncio.wait_for`. Without this, the manager's
    ``except asyncio.TimeoutError`` handler cannot distinguish a
    deadline-driven cancellation from an infrastructure timeout surfaced
    by the provider's own transport / SDK, and would default the
    participant's response when it should fail loud (AGENTS.md "no silent
    fallbacks").
    """

    try:
        return await coro
    except TimeoutError as e:
        raise LLMProviderError("LLM provider timeout") from e


@dataclass(frozen=True)
class SuspicionEntry:
    """One row of the agent's suspicion graph (DESIGN.md §5.5).

    Surfaced verbatim into the vote-ballot prompt. The fields mirror
    :class:`agents.memory.beliefs.PlayerBelief` so the strategic reasoner
    (Task 8.8) can map a belief snapshot into this DTO without re-shaping
    it.
    """

    player_id: PlayerId
    suspicion: float
    trust: float


@dataclass(frozen=True)
class MeetingParticipant:
    """One living agent's contribution to the meeting (DESIGN.md §5.1).

    The manager treats this as a static snapshot for the duration of the
    meeting: ``rendered_memory`` is what the §6.6 renderer produced when
    the meeting opened, ``role`` selects which opening prompt is used, and
    ``suspicion_graph`` populates the vote-ballot prompt input.

    ``fellow_impostor_ids`` carries the impostor-only teammate list
    (Task 7.12) onto the meeting layer: the sorted ids of the OTHER
    impostors when ``role == "IMPOSTOR"`` and ``()`` for every crewmate
    and for a sole impostor, never the participant's own id. The
    orchestrator populates it from world-state roles; the default of
    ``()`` keeps every existing construction site valid and is the
    firewall-correct value for a crewmate.
    """

    agent_id: PlayerId
    role: Role
    rendered_memory: str
    suspicion_graph: tuple[SuspicionEntry, ...] = ()
    fellow_impostor_ids: tuple[PlayerId, ...] = ()


@dataclass(frozen=True)
class MeetingTrigger:
    """Why the meeting was opened (DESIGN.md §5.1).

    The orchestrator constructs this from the engine event that
    transitioned the world into ``MEETING`` phase. ``triggered_by`` is the
    opener (turn 0); ``description`` is a short free-text summary (e.g.
    ``"p3 reported p2's body in MedBay at tick 410"``) that the opening
    prompt surfaces to the LLM.
    """

    triggered_by: PlayerId
    trigger_tick: int
    description: str


@dataclass(frozen=True)
class MeetingDeadlines:
    """Per-turn + vote deadlines (DESIGN.md §1.4, §5.2).

    ``None`` disables the deadline for that phase (headless mode); the
    value is passed straight to :func:`asyncio.wait_for`. ``turn_seconds``
    bounds each opening / reply / opt-in turn; ``vote_seconds`` bounds each
    ballot. The meeting's *total* turn count is hard-capped at the
    living-player count by the chain protocol itself (DESIGN.md §5.2
    PHASE 2), so the deterministic total-meeting bound is structural, not a
    wall-clock budget.
    """

    turn_seconds: float | None = DEFAULT_TURN_DEADLINE_SECONDS
    vote_seconds: float | None = DEFAULT_VOTE_DEADLINE_SECONDS


@dataclass(frozen=True)
class MeetingConfig:
    """Meeting protocol configuration (DESIGN.md §5.2)."""

    deadlines: MeetingDeadlines = field(default_factory=MeetingDeadlines)
    skip_confidence_threshold: float = DEFAULT_SKIP_CONFIDENCE_THRESHOLD
    turn_max_tokens: int = DEFAULT_TURN_MAX_TOKENS
    turn_temperature: float = DEFAULT_TURN_TEMPERATURE
    vote_max_tokens: int = DEFAULT_VOTE_MAX_TOKENS
    vote_temperature: float = DEFAULT_VOTE_TEMPERATURE


# Phase the default fell back on; a turn kind (:data:`TurnKind`) or the vote.
DefaultedPhase = Literal["opening", "reply", "opt_in", "vote"]
# Why a default fired. ``deadline`` is a wall-clock miss (only reachable with a
# configured deadline -- interactive mode); ``validation`` is a payload that
# failed schema validation even after the provider's parse-tolerance (reachable
# even in deadline-free headless recording).
DefaultTrigger = Literal["deadline", "validation"]


@dataclass(frozen=True)
class DefaultedCall:
    """A meeting turn / ballot that fell back to its default (audit gp-2).

    Surfaced by :meth:`MeetingManager.run` through
    :attr:`MeetingManager.defaulted_calls` so the orchestrator can write a
    visible ``deadline_default`` record into the replay. Audit gp-2: a turn
    that defaults must never vanish from the replay -- the headless recorder
    previously lost 11 turns (9 of 91 openings) to the interactive 30 s
    deadline with no record of any kind, so the report's ``failed_calls=0`` was
    true of the records and false of the run.

    The manager only carries the facts the orchestrator needs to name the
    default in its replay record; the orchestrator owns the
    :class:`~orchestrator.replay.FailedCallReplayEntry` write itself
    (``error_type="deadline_default"``).

    * ``phase`` -- the defaulted slot: a turn kind (``opening`` / ``reply`` /
      ``opt_in``) or ``vote``.
    * ``agent_id`` -- the participant who submitted nothing.
    * ``trigger`` -- ``deadline`` (wall-clock miss, interactive only) or
      ``validation`` (a schema-invalid payload, reachable in headless mode).
    * ``turn_index`` -- the turn ordinal for a defaulted turn; ``None`` for a
      defaulted vote.
    """

    phase: DefaultedPhase
    agent_id: PlayerId
    trigger: DefaultTrigger
    turn_index: int | None = None


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
    ) -> str: ...


class MeetingManager:
    """State machine that runs one meeting end-to-end (DESIGN.md §5.1, §5.2).

    Construction is cheap and side-effect free: it stores references to
    the LLM client, the prompt callables, and the config. Nothing runs
    until :meth:`run` is invoked, which is the trigger lifecycle in
    DESIGN.md §5.1.

    :meth:`run` sequences the reactive accusation chain (opening ->
    reactive chain -> opt-in) then voting and resolution. The manager
    returns the result without mutating engine state; the orchestrator
    applies the outcome to engine-owned state.
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
        if not 0.0 <= config.skip_confidence_threshold <= 1.0:
            raise ValueError(
                "MeetingConfig.skip_confidence_threshold must be in [0, 1], "
                f"got {config.skip_confidence_threshold}"
            )
        # Reject misconfigured deadlines fail-loud. A negative or zero
        # deadline reaches ``asyncio.wait_for`` and trips ``TimeoutError``
        # before the LLM call can complete, silently routing every turn
        # into the default-turn / default-skip path. That would change
        # meeting outcomes without any explicit configuration error
        # (AGENTS.md "no silent fallbacks"). ``None`` is the explicit
        # opt-out (headless mode, §1.4).
        for name, value in (
            ("turn_seconds", config.deadlines.turn_seconds),
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
        # Per-run scratch: the defaults that fired during the most recent
        # :meth:`run`. Reset at the top of every ``run`` (the manager is reused
        # across a game's meetings) and read by the orchestrator immediately
        # after ``run`` returns (audit gp-2). Not engine state and not a DTO --
        # a turn/ballot that defaulted is recorded into the replay through the
        # existing failed-call channel, never lost silently.
        self._defaulted_calls: list[DefaultedCall] = []

    @property
    def defaulted_calls(self) -> tuple[DefaultedCall, ...]:
        """Defaults that fired during the most recent :meth:`run` (audit gp-2).

        Reset at the start of every :meth:`run`. The orchestrator reads this
        right after ``run`` returns and writes one visible ``deadline_default``
        replay record per entry, so a turn / ballot that fell back to its
        placeholder is never lost from the replay (the headless recorder
        previously dropped 11 such turns with no record of any kind). Empty for
        a meeting in which every turn and ballot was produced normally.
        """

        return tuple(self._defaulted_calls)

    async def run(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        participants: Sequence[MeetingParticipant],
    ) -> MeetingResult:
        """Run opening -> reactive chain -> opt-in -> voting -> resolution.

        The returned ``MeetingResult.transcript.turns`` is the single
        ordered turn list (DESIGN.md §5.2): turn 0 is the opening (the
        opener is ``trigger.triggered_by``, which MUST be a living
        participant), followed by the reactive ``reply`` chain and any
        terminal ``opt_in`` turns. Turn ids are ``"{meeting_id}:turn-{N}"``.
        The chain's next speaker and its termination are pure functions of
        the recorded turns, so a replay reconstructs the discussion from
        ``transcript.turns`` without re-calling the LLM.
        """

        if not meeting_id:
            raise ValueError("meeting_id must be a non-empty string")
        if not participants:
            raise ValueError(
                "MeetingManager.run requires at least one living participant"
            )
        self._validate_participants(participants, trigger=trigger)

        # Fresh per-run default ledger (the manager is reused across a game's
        # meetings); the orchestrator reads :attr:`defaulted_calls` after this
        # ``run`` returns (audit gp-2).
        self._defaulted_calls = []

        # Canonicalise participant order at entry. Real callers may iterate
        # over a set/dict whose order is hash-seeded and not
        # determinism-preserving; sorting by ``agent_id`` is deterministic
        # and matches the lexical ``p-N`` convention used everywhere else.
        ordered_participants = tuple(sorted(participants, key=lambda p: p.agent_id))
        by_id = {p.agent_id: p for p in ordered_participants}
        roster = frozenset(by_id)

        # Phase 1: opening turn (turn 0, role-dispatched). The opening is a
        # single point of failure for the whole meeting -- an empty opening
        # names no accusation, so the chain is dead and every ballot votes on a
        # husk -- so it is retried once before defaulting (audit gp-2).
        opener = by_id[trigger.triggered_by]
        opening_turn = await self._collect_turn(
            meeting_id=meeting_id,
            trigger=trigger,
            participant=opener,
            turn_index=0,
            turn_kind="opening",
            reply_to=None,
            prior_turn=None,
            transcript_so_far=MeetingTranscript(),
            contradictions=(),
            retries=1,
        )
        turns: list[MeetingTurn] = [opening_turn]
        spoken: set[PlayerId] = {opener.agent_id}

        # Phase 2: reactive chain (next speaker = the accused; deterministic
        # 3-condition termination -- DESIGN.md §5.2 PHASE 2).
        while True:
            prev = turns[-1]
            step = next_chain_step(
                prev_turn=prev,
                spoken=frozenset(spoken),
                living_ids=roster,
                turns_recorded=len(turns),
            )
            if step.next_speaker is None:
                break
            # 7.12 defense-in-depth at the chain-passing chokepoint: never
            # pass the floor to a fellow impostor of the accuser. The per-turn
            # claim guard already strips a teammate accusation before the turn
            # is recorded, so ``accusation_target`` (and therefore
            # ``next_chain_step``) never names a teammate here -- this is a
            # provable no-op that keeps the guard on the chain path and never
            # diverges the replay-walk (which re-derives via ``next_chain_step``).
            guarded_next = drop_teammate_statement_target(
                step.next_speaker,
                fellow_impostor_ids=by_id[prev.speaker].fellow_impostor_ids,
            )
            if guarded_next is None:
                break
            transcript_so_far = MeetingTranscript(turns=tuple(turns))
            contradictions_so_far = detect_contradictions(
                transcript_so_far, roster=roster
            )
            reply_turn = await self._collect_turn(
                meeting_id=meeting_id,
                trigger=trigger,
                participant=by_id[guarded_next],
                turn_index=len(turns),
                turn_kind="reply",
                reply_to=prev.turn_id,
                prior_turn=prev,
                transcript_so_far=transcript_so_far,
                contradictions=contradictions_so_far,
            )
            turns.append(reply_turn)
            spoken.add(guarded_next)

        # Phase 3: opt-in info-share. Eligibility is computed ONCE from the
        # post-chain transcript (a co-presence gate with the body / accused),
        # so an opt-in turn's own accusation never makes a new player eligible
        # and never extends the chain (DESIGN.md §5.2 PHASE 3).
        transcript_after_chain = MeetingTranscript(turns=tuple(turns))
        for opt_in_id in _opt_in_eligible_ids(
            transcript=transcript_after_chain,
            spoken=frozenset(spoken),
            living_ids=roster,
        ):
            transcript_so_far = MeetingTranscript(turns=tuple(turns))
            contradictions_so_far = detect_contradictions(
                transcript_so_far, roster=roster
            )
            opt_in_turn = await self._collect_turn(
                meeting_id=meeting_id,
                trigger=trigger,
                participant=by_id[opt_in_id],
                turn_index=len(turns),
                turn_kind="opt_in",
                reply_to=None,
                prior_turn=None,
                transcript_so_far=transcript_so_far,
                contradictions=contradictions_so_far,
            )
            turns.append(opt_in_turn)
            spoken.add(opt_in_id)

        transcript = MeetingTranscript(turns=tuple(turns))

        # Phase 4: contradictions recompute ONCE over the full transcript
        # before voting (DESIGN.md §5.4), then collect ballots.
        contradictions = detect_contradictions(transcript, roster=roster)
        ballots = await self._collect_ballots(
            trigger=trigger,
            participants=ordered_participants,
            transcript=transcript,
            contradictions=contradictions,
        )

        # Phase 5: resolution.
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

    # -- Turn collection (the single per-turn chokepoint) -----------------

    async def _collect_turn(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        participant: MeetingParticipant,
        turn_index: int,
        turn_kind: TurnKind,
        reply_to: str | None,
        prior_turn: MeetingTurn | None,
        transcript_so_far: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
        retries: int = 0,
    ) -> MeetingTurn:
        """Collect one turn through the shared guard chokepoint.

        Every turn-kind (opening / reply / opt-in) flows through here, so
        every turn inherits the same guards: self-alibi normalization, the
        Task 7.12 teammate firewall, and the Task 7.10 fail-soft. The
        manager is authoritative for the identity fields (``turn_id``,
        ``turn_index``, ``speaker``, ``turn_kind``, ``reply_to``); the LLM
        supplies only ``observations`` / ``claims`` / ``free_text``.

        ``retries`` is the number of EXTRA attempts on top of the first before
        the turn defaults (the opening passes ``retries=1`` -- audit gp-2). A
        fired default is appended to :attr:`defaulted_calls` so the orchestrator
        can record it in the replay; the prompt is rendered once and reused
        across attempts (its inputs do not change between retries).
        """

        prompt = self._render_turn_prompt(
            participant=participant,
            turn_kind=turn_kind,
            trigger=trigger,
            transcript_so_far=transcript_so_far,
            contradictions=contradictions,
            prior_turn=prior_turn,
        )
        turn_id = _turn_id(meeting_id=meeting_id, turn_index=turn_index)
        # The trigger kind of the LAST failed attempt, recorded with the
        # default so the orchestrator can name it (deadline vs validation).
        trigger_kind: DefaultTrigger = "deadline"
        for _attempt in range(retries + 1):
            try:
                response = await asyncio.wait_for(
                    _isolate_provider_timeout(
                        self._llm_client.complete(
                            prompt=prompt,
                            schema=MeetingTurn,
                            max_tokens=self._config.turn_max_tokens,
                            temperature=self._config.turn_temperature,
                            call_kind="meeting",
                            agent_id=participant.agent_id,
                        )
                    ),
                    timeout=self._config.deadlines.turn_seconds,
                )
                parsed = MeetingTurn.model_validate_json(response.text)
            except (asyncio.TimeoutError, ValidationError) as exc:
                # Fail-soft on a single turn (Task 7.10): a missed deadline
                # (``TimeoutError``) and a malformed turn that still fails
                # schema validation after the provider's parse-tolerance
                # normalization (``ValidationError`` -- e.g. an ``AlibiClaim``
                # so broken the chronological-range swap cannot salvage it)
                # BOTH degrade to the same placeholder so the meeting continues
                # to its vote and the game reaches ``game_over``. A
                # provider/transport timeout is still re-tagged
                # ``LLMProviderError`` (by ``_isolate_provider_timeout``) and
                # propagates -- only the deadline + parse failures fail soft.
                # Note which fired so the surfaced ``deadline_default`` record
                # names it (audit gp-2); ``asyncio.TimeoutError`` is built-in
                # ``TimeoutError`` in 3.11+, distinct from ``ValidationError``.
                trigger_kind = (
                    "deadline"
                    if isinstance(exc, asyncio.TimeoutError)
                    else "validation"
                )
                continue
            # Defense-in-depth: rewrite self-alibi placeholder subjects (e.g.
            # "p-self") to the speaker's canonical id before the identity
            # override, so DESIGN.md §5.4 contradiction detection can match
            # this turn's self-alibi against other speakers (Task 3.20).
            normalized_claims = _normalize_self_alibi_subjects(
                parsed.claims, speaker_id=participant.agent_id
            )
            # Teammate firewall guard (Task 7.12) on EVERY turn-kind: drop any
            # accusation an impostor makes against a fellow impostor. Because
            # the chain reads its next speaker off these recorded claims,
            # guarding here is what keeps an impostor from passing the chain to
            # (or publicly incriminating) a teammate on any turn. Deterministic
            # and a no-op for a crewmate / sole impostor, so replay is
            # unaffected.
            guarded_claims = _guard_teammate_turn_claims(
                normalized_claims, fellow_impostor_ids=participant.fellow_impostor_ids
            )
            # Override the identity fields with the canonical values; the LLM
            # is told to emit any non-empty string and the manager is
            # authoritative for who said what and where it sits in the chain.
            return parsed.model_copy(
                update={
                    "turn_id": turn_id,
                    "turn_index": turn_index,
                    "speaker": participant.agent_id,
                    "turn_kind": turn_kind,
                    "reply_to": reply_to,
                    "claims": guarded_claims,
                }
            )
        # Every attempt (1 + ``retries``) failed: surface the fired default so
        # the orchestrator records it in the replay (audit gp-2 -- a defaulted
        # turn must never be invisible), then return the placeholder.
        self._defaulted_calls.append(
            DefaultedCall(
                phase=turn_kind,
                agent_id=participant.agent_id,
                trigger=trigger_kind,
                turn_index=turn_index,
            )
        )
        return _default_turn(
            turn_id=turn_id,
            turn_index=turn_index,
            speaker=participant.agent_id,
            turn_kind=turn_kind,
            reply_to=reply_to,
        )

    def _render_turn_prompt(
        self,
        *,
        participant: MeetingParticipant,
        turn_kind: TurnKind,
        trigger: MeetingTrigger,
        transcript_so_far: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
        prior_turn: MeetingTurn | None,
    ) -> str:
        if turn_kind == "opening":
            renderer = (
                self._impostor_report_prompt
                if participant.role == "IMPOSTOR"
                else self._crewmate_report_prompt
            )
            return renderer(
                agent_id=participant.agent_id,
                current_tick=trigger.trigger_tick,
                meeting_trigger=trigger.description,
                rendered_memory=participant.rendered_memory,
                public_transcript="",
                fellow_impostor_ids=participant.fellow_impostor_ids,
            )
        return self._statement_prompt(
            agent_id=participant.agent_id,
            rendered_memory=participant.rendered_memory,
            transcript=transcript_so_far,
            contradictions=contradictions,
            prior_turn=prior_turn,
            turn_kind=turn_kind,
            fellow_impostor_ids=participant.fellow_impostor_ids,
        )

    # -- Voting -----------------------------------------------------------

    async def _collect_ballots(
        self,
        *,
        trigger: MeetingTrigger,
        participants: Sequence[MeetingParticipant],
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
    ) -> tuple[VoteBallot, ...]:
        # Sequential collection: concurrent ballots on a single local GPU
        # inflate each call's wall-clock past vote_seconds (measured 0.71x
        # concurrency), so votes time out into default SKIP and nothing is
        # ever ejected. One-by-one keeps each call inside its deadline. Each
        # _collect_one_ballot retains its own deadline + default; a genuine
        # parse error still propagates and fails the meeting.
        ballots: list[VoteBallot] = []
        for participant in participants:
            ballots.append(
                await self._collect_one_ballot(
                    trigger=trigger,
                    participant=participant,
                    participants=participants,
                    transcript=transcript,
                    contradictions=contradictions,
                )
            )
        return tuple(ballots)

    async def _collect_one_ballot(
        self,
        *,
        trigger: MeetingTrigger,
        participant: MeetingParticipant,
        participants: Sequence[MeetingParticipant],
        transcript: MeetingTranscript,
        contradictions: tuple[ContradictionRef, ...],
    ) -> VoteBallot:
        # Confirm the candidate set over the FINAL transcript: every living
        # participant except the voter is an eligible eject target.
        candidate_targets = tuple(
            sorted(
                other.agent_id
                for other in participants
                if other.agent_id != participant.agent_id
            )
        )
        # Belief Rule 2 (DESIGN.md §6.3): a detected contradiction lifts the
        # contradicted subject's suspicion in this voter's graph before the
        # ballot prompt renders, so the vote sees the detected lie reflected
        # in its suspicion prior -- not just in the raw flag list. Engine
        # state is never touched.
        suspicion_graph = _suspicion_graph_with_contradictions(
            voter_id=participant.agent_id,
            suspicion_graph=participant.suspicion_graph,
            contradictions=contradictions,
        )
        prompt = self._vote_prompt(
            voter_id=participant.agent_id,
            rendered_memory=participant.rendered_memory,
            transcript=transcript,
            contradiction_flags=contradictions,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=self._config.skip_confidence_threshold,
            fellow_impostor_ids=participant.fellow_impostor_ids,
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
            # The vote catches only the deadline (a malformed ballot still
            # propagates and aborts the meeting, unchanged); surface the fired
            # default so the orchestrator records it (audit gp-2). Deadline-free
            # headless recording never reaches here -- a vote default is an
            # interactive-mode wall-clock miss.
            self._defaulted_calls.append(
                DefaultedCall(
                    phase="vote",
                    agent_id=participant.agent_id,
                    trigger="deadline",
                )
            )
            return _default_vote(voter=participant.agent_id)
        parsed = VoteBallot.model_validate_json(response.text)
        # Defensive normalization: if the LLM hallucinates a target id that
        # is not in ``candidate_targets`` (and not ``"SKIP"``), ``_tally``
        # would otherwise count it as a real eject and could resolve to
        # ``EJECTED`` with a non-participant id. Replace the target with
        # ``"SKIP"`` and mark the rationale so the original (bad) target is
        # preserved for audit / replay.
        normalized = _normalize_ballot_target(
            ballot=parsed, candidate_targets=candidate_targets
        )
        # Teammate firewall guard (Task 7.12): a teammate is a *valid* living
        # candidate, so the invalid-target normalization above never catches
        # it. Coerce a ballot that targets a fellow impostor to SKIP so an
        # impostor can never supply the betrayal vote that ejects a teammate.
        # Deterministic, no RNG, and a no-op for a crewmate / sole impostor.
        normalized = coerce_teammate_ballot_to_skip(
            ballot=normalized, fellow_impostor_ids=participant.fellow_impostor_ids
        )
        return normalized.model_copy(update={"voter": participant.agent_id})

    # -- Resolution -------------------------------------------------------

    def _tally(
        self,
        ballots: Sequence[VoteBallot],
    ) -> tuple[MeetingOutcome, PlayerId | None]:
        """Plurality tally with confidence threshold (DESIGN.md §5.2 + §4.6 + §5.5).

        ``SKIP`` is a real tally target -- a vote of ``SKIP`` competes with
        non-``SKIP`` votes for plurality (DESIGN.md §5.5 schemas
        ``VoteBallot.target`` as ``PlayerId | Literal["SKIP"]``; §5.2:
        "tie or below threshold -> skip").

        Resolution rules:

        * Empty ballots -> ``SKIPPED`` (no votes to tally).
        * ``SKIP`` has plurality (alone or tied at the top) -> ``SKIPPED``.
        * Two or more non-``SKIP`` targets tied at the top -> ``SKIPPED``.
        * Single non-``SKIP`` target with strict plurality AND at least one
          ballot for that target with ``confidence >=
          skip_confidence_threshold`` -> ``EJECTED``.
        * Otherwise (strict plurality but no confident ballot) ->
          ``SKIPPED`` (the mechanical "meets threshold" check; the "max
          confidence across the target's ballots" reading matches DESIGN.md
          §4.6 -- the eject requires at least one confident voter).

        The threshold check is inclusive at the cutoff: a confidence of
        exactly ``skip_confidence_threshold`` ejects.
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
            # ``MeetingParticipant`` is a runtime dataclass; the ``Role``
            # ``Literal`` is enforced by mypy --strict at the call site but
            # not at runtime. A typo like ``"impostor"`` would otherwise fall
            # through the ``role == "IMPOSTOR"`` check in
            # ``_render_turn_prompt`` and silently route the agent to the
            # crewmate prompt. Fail-loud at entry.
            if participant.role not in _VALID_ROLES:
                raise ValueError(
                    "MeetingParticipant.role must be one of "
                    f"{sorted(_VALID_ROLES)}; got {participant.role!r} "
                    f"for agent {participant.agent_id!r}"
                )
            # Task 7.12 firewall (mirrors the 7.2 crew-empty invariant):
            # ``fellow_impostor_ids`` is impostor-only self-channel data, and
            # the manager runs no leak scanner of its own before threading it
            # into the shared turn / vote prompts. A non-impostor carrying a
            # non-empty teammate list would render the teammate block into a
            # crewmate's prompt, leaking impostor identities outside the self
            # channel. Fail loud rather than leak (AGENTS.md "no silent
            # fallbacks").
            if participant.role != "IMPOSTOR" and participant.fellow_impostor_ids:
                raise ValueError(
                    "MeetingParticipant.fellow_impostor_ids must be empty for a "
                    f"non-impostor; got {participant.fellow_impostor_ids!r} for "
                    f"{participant.role!r} agent {participant.agent_id!r} "
                    "(teammate identity is impostor-only self-channel data)"
                )
        # The protocol opens with the reporter (DESIGN.md §5.2 PHASE 1). A
        # trigger whose ``triggered_by`` is not in the participant set is an
        # upstream orchestrator bug -- not something to silently demote.
        # Failing loud here surfaces the wiring error at meeting entry,
        # before any LLM traffic is spent (AGENTS.md "no silent fallbacks").
        if trigger.triggered_by not in seen:
            raise ValueError(
                f"MeetingTrigger.triggered_by={trigger.triggered_by!r} is not in "
                f"the participant set ({sorted(seen)}); the protocol requires "
                "the opener to be a living participant"
            )


def _opt_in_eligible_ids(
    *,
    transcript: MeetingTranscript,
    spoken: frozenset[PlayerId],
    living_ids: frozenset[PlayerId],
) -> tuple[PlayerId, ...]:
    """Living non-speakers with a relevant observation (DESIGN.md §5.2 PHASE 3).

    The "relevant observation" gate is a deterministic co-presence check
    against the body and the accused, computed purely from the recorded
    turns (so it is replay-stable and needs no extra LLM call): a living
    non-speaker is eligible iff the public ``saw_player`` observations
    place them co-present with the body's room or with a player who was
    accused during the meeting. Co-presence is symmetric -- "p was seen
    near the body / with the accused" means p holds a relevant
    first-hand observation -- so the transcript is a sufficient, leak-safe
    source for the gate. Returned in ascending player-id order (DESIGN.md
    §5.2 PHASE 3 "in player-id order").
    """

    body_rooms = {
        observation.room
        for turn in transcript.turns
        for observation in turn.observations
        if isinstance(observation, FoundBodyObservation)
    }
    accused: set[PlayerId] = set()
    for turn in transcript.turns:
        target = accusation_target(turn)
        if target is not None:
            accused.add(target)

    relevant: set[PlayerId] = set()
    for turn in transcript.turns:
        for observation in turn.observations:
            if not isinstance(observation, SawPlayerObservation):
                continue
            group = {observation.subject, *observation.co_present}
            if (
                observation.room in body_rooms
                or observation.subject in accused
                or (group & accused)
            ):
                relevant |= group

    return tuple(
        player_id
        for player_id in sorted(living_ids)
        if player_id not in spoken and player_id in relevant
    )


def _suspicion_graph_with_contradictions(
    *,
    voter_id: PlayerId,
    suspicion_graph: tuple[SuspicionEntry, ...],
    contradictions: tuple[ContradictionRef, ...],
) -> tuple[SuspicionEntry, ...]:
    """Apply belief Rule 2 to a voter's suspicion graph (DESIGN.md §6.3).

    Reconstructs an agents-side :class:`BeliefState` from the voter's
    incoming suspicion-graph snapshot, runs
    :func:`agents.memory.beliefs.apply_contradiction_rule` over the
    detected ``contradictions``, and projects the result back into a
    sorted :class:`SuspicionEntry` tuple for the vote-ballot prompt.

    A contradicted subject the voter had no prior row for is added (the
    belief store materialises a default 0.5 prior before the +0.3 bump).
    The voter never accrues suspicion about themselves. With no
    contradictions the graph is returned unchanged so the no-flag path is
    byte-identical (a precondition for replay stability).
    """

    if not contradictions:
        return suspicion_graph

    beliefs = BeliefState()
    for entry in suspicion_graph:
        beliefs.seed_player(
            entry.player_id, suspicion=entry.suspicion, trust=entry.trust
        )
    updated = apply_contradiction_rule(beliefs, contradictions)

    entries: list[SuspicionEntry] = []
    for player_id in sorted(updated.known_players()):
        if player_id == voter_id:
            continue
        belief = updated.view(player_id)
        entries.append(
            SuspicionEntry(
                player_id=player_id,
                suspicion=belief.suspicion,
                trust=belief.trust,
            )
        )
    return tuple(entries)


def _turn_id(*, meeting_id: str, turn_index: int) -> str:
    """The canonical turn id ``"{meeting_id}:turn-{turn_index}"`` (DESIGN.md §5.2).

    Keyed on the turn ordinal, not the speaker, so it is unique even when
    a player speaks twice; :attr:`VoteBallot.primary_reason_id` references
    it.
    """

    return f"{meeting_id}:turn-{turn_index}"


def _default_turn(
    *,
    turn_id: str,
    turn_index: int,
    speaker: PlayerId,
    turn_kind: TurnKind,
    reply_to: str | None,
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=turn_id,
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,
        reply_to=reply_to,
        observations=(),
        claims=(),
        free_text=DEFAULT_TURN_FREE_TEXT,
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

    The model occasionally emits ``subject: "self"`` or ``"p-self"`` in an
    :class:`~meetings.schemas.AlibiClaim`, leaking a prompt-template /
    few-shot placeholder into the structured ``subject`` field (Task 3.20).
    Those claims are unambiguously the speaker's own self-alibi; this
    rewrites their ``subject`` to the speaker's canonical player id so
    DESIGN.md §5.4 contradiction detection -- which indexes alibis by
    ``(subject, tick_range, location)`` -- can match them against other
    speakers' claims. The full placeholder set is
    :data:`_SELF_ALIBI_PLACEHOLDERS`.

    A ``subject`` that is NOT in the placeholder set is passed through
    unchanged; this helper deliberately does not validate ``subject``
    against the meeting's roster (an unknown subject simply fails to match
    in contradiction detection, no worse than today). Only
    :class:`~meetings.schemas.AlibiClaim`s are inspected; accusation /
    corroboration claims are returned as-is.
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
    ``rationale_text`` preserving the original (invalid) target. The tally
    cannot then resolve to ``EJECTED`` against a non-participant id; the
    audit trail records what the LLM actually emitted.
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


# ---------------------------------------------------------------------------
# Teammate firewall guard (Task 7.12).
#
# Meeting output is LLM-driven, so the fix is two layers: a prompt layer that
# tells an impostor who its teammates are (the ``.j2`` templates) and these
# deterministic guards that hard-exclude a teammate from the produced
# accusation / ballot regardless of what the model emits. Each helper is a
# pure function of ``fellow_impostor_ids`` with no RNG and no new LLM call,
# and is an exact no-op when ``fellow_impostor_ids`` is empty (every crewmate
# and a sole impostor), so replay reconstruction of the committed sets is
# unaffected. Shared by :class:`MeetingManager` (the production meeting path)
# and the strategic reasoner. In the reactive chain the accusation lives in a
# turn's ``claims`` (there is no separate ``Statement.target`` field), so
# :func:`exclude_teammate_accusation_claims` is the operative chain-safety
# guard and :func:`drop_teammate_statement_target` backstops the derived
# next-speaker target (:func:`_guard_teammate_turn_claims`).
# ---------------------------------------------------------------------------


def exclude_teammate_accusation_claims(
    claims: tuple[Claim, ...],
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> tuple[Claim, ...]:
    """Drop every :class:`AccusationClaim` aimed at a fellow impostor.

    Returns ``claims`` unchanged when ``fellow_impostor_ids`` is empty
    (crewmate / sole impostor) so the no-coordination path is
    byte-identical. Only :class:`AccusationClaim`s are filtered: an
    :class:`AlibiClaim` for a teammate or a :class:`CorroborationClaim`
    supporting a teammate *helps* the team and is retained.
    """

    if not fellow_impostor_ids:
        return claims
    teammates = frozenset(fellow_impostor_ids)
    return tuple(
        claim
        for claim in claims
        if not (isinstance(claim, AccusationClaim) and claim.against in teammates)
    )


def drop_teammate_statement_target(
    target: PlayerId | None,
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> PlayerId | None:
    """Null an accusation target that names a fellow impostor.

    Returns ``target`` unchanged when ``fellow_impostor_ids`` is empty or
    when ``target`` is not a teammate; a teammate-naming target degrades to
    ``None``. In the reactive chain this guards the derived next-speaker
    target (the floor never passes to a fellow impostor) -- a defensive
    backstop to :func:`exclude_teammate_accusation_claims`, which has
    already stripped the teammate accusation from the recorded claims.
    """

    if not fellow_impostor_ids or target is None:
        return target
    if target in fellow_impostor_ids:
        return None
    return target


def coerce_teammate_ballot_to_skip(
    *,
    ballot: VoteBallot,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> VoteBallot:
    """Coerce a ballot that targets a fellow impostor to ``SKIP``.

    A teammate is a *valid* living candidate, so the hallucinated-target
    normalization (:func:`_normalize_ballot_target`) never catches it. This
    guard is what stops an impostor from supplying the betrayal vote that
    ejects a teammate. Returns ``ballot`` unchanged when
    ``fellow_impostor_ids`` is empty or the target is not a teammate;
    otherwise rewrites ``target`` to ``SKIP`` and prepends
    :data:`TEAMMATE_VOTE_TARGET_MARKER` to ``rationale_text`` so the
    original (teammate) target stays auditable in the replay record.
    """

    if not fellow_impostor_ids or ballot.target not in fellow_impostor_ids:
        return ballot
    marker = TEAMMATE_VOTE_TARGET_MARKER.format(target=ballot.target)
    return ballot.model_copy(
        update={
            "target": _SKIP_TARGET,
            "rationale_text": marker + ballot.rationale_text,
        }
    )


def _guard_teammate_turn_claims(
    claims: tuple[Claim, ...],
    *,
    fellow_impostor_ids: tuple[PlayerId, ...],
) -> tuple[Claim, ...]:
    """Apply the Task 7.12 claim-level teammate guards to one turn's claims.

    Runs the primary guard (:func:`exclude_teammate_accusation_claims`,
    which drops accusation claims naming a teammate) and then a
    :func:`drop_teammate_statement_target` backstop on the derived
    accusation target: the reactive chain passes the floor to the player a
    turn accuses, so the recorded claims must never leave a teammate as
    that target. The backstop is a no-op once the primary guard has run
    (the teammate accusation is already gone); it is retained so all three
    7.12 guards wrap every turn-kind. A no-op for a crewmate / sole
    impostor (empty ``fellow_impostor_ids``).
    """

    guarded = exclude_teammate_accusation_claims(
        claims, fellow_impostor_ids=fellow_impostor_ids
    )
    target = next(
        (claim.against for claim in guarded if isinstance(claim, AccusationClaim)),
        None,
    )
    if (
        target is not None
        and drop_teammate_statement_target(
            target, fellow_impostor_ids=fellow_impostor_ids
        )
        is None
    ):
        guarded = tuple(
            claim
            for claim in guarded
            if not (isinstance(claim, AccusationClaim) and claim.against == target)
        )
    return guarded


__all__ = [
    "DEFAULT_SKIP_CONFIDENCE_THRESHOLD",
    "DEFAULT_TURN_DEADLINE_SECONDS",
    "DEFAULT_TURN_FREE_TEXT",
    "DEFAULT_TURN_MAX_TOKENS",
    "DEFAULT_TURN_TEMPERATURE",
    "DEFAULT_VOTE_DEADLINE_SECONDS",
    "DEFAULT_VOTE_MAX_TOKENS",
    "DEFAULT_VOTE_RATIONALE",
    "DEFAULT_VOTE_TEMPERATURE",
    "INVALID_VOTE_TARGET_MARKER",
    "TEAMMATE_VOTE_TARGET_MARKER",
    "DefaultTrigger",
    "DefaultedCall",
    "DefaultedPhase",
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
    "coerce_teammate_ballot_to_skip",
    "drop_teammate_statement_target",
    "exclude_teammate_accusation_claims",
]
