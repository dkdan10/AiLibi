"""Headless game orchestrator (DESIGN.md §1.4, §3.1, §11.4).

:class:`HeadlessGame` wires the engine, observation service, agents,
action-intent translation, meeting dispatch, and replay log into a
single deterministic tick loop. It is the Phase-3 convergence point:
when the engine transitions to ``MEETING`` phase, the orchestrator
dispatches to :class:`~meetings.manager.MeetingManager` (via a
:class:`MeetingRunner`), applies the returned :class:`MeetingResult`
to engine-owned world state through :func:`apply_meeting_result`, and
resumes the tick loop at tick ``t+1`` per DESIGN.md §3.1.

The orchestrator is the only non-``engine/`` module that imports from
``engine/`` and the only module that mutates engine-owned state.
``MeetingManager`` is engine-pure: it receives agent-side inputs
(rendered memory, suspicion graphs) and returns a
:class:`MeetingResult` DTO. Applying that result to the world is the
orchestrator's job (DESIGN.md §1.3).
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final, Literal, Protocol, TypeAlias, TypeVar, runtime_checkable

from agents.base import AgentInterface
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    render_for_prompt,
)
from agents.perception import ingest_packet
from agents.strategic.prompts import (
    accusation_round_prompt,
    crewmate_report_prompt,
    impostor_report_prompt,
    vote_ballot_prompt,
)
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import BodyId, PlayerId, PlayerState, Role
from engine.events import (
    EngineEvent,
    GameOverEvent,
    MeetingTriggeredEvent,
)
from engine.rng import EngineRng
from engine.rules import resolve_win_conditions
from engine.tick import advance_tick
from engine.world import Map, WorldState
from llm.budget import GameBudget
from llm.budgeted_client import BudgetedLLMClient
from llm.client import LLMClient, LLMResponse
from llm.client import CallKind as _LLMCallKind
from llm.provider import build_default_client, extract_parse_failure
from meetings.manager import (
    DefaultedCall,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    ReportPromptRenderer,
    StatementPromptRenderer,
    SuspicionEntry,
    VotePromptRenderer,
)
from meetings.schemas import (
    MeetingResult,
)
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.boundary import (
    public_map_from_engine_map,
    translate_action_intents_for_tick,
)
from orchestrator.replay import LLMCallRecord, ReplayLog, _state_hash
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state
from pydantic import BaseModel

AgentFactory: TypeAlias = Callable[[PlayerId, Role], AgentInterface]

Outcome: TypeAlias = Literal[
    "CREWMATES",
    "IMPOSTORS",
    "MEETING_PHASE_REACHED",
    "TICK_BUDGET_REACHED",
]

DEFAULT_MAX_TICKS: Final[int] = 1000
DEFAULT_NUM_PLAYERS: Final[int] = 4
DEFAULT_NUM_IMPOSTORS: Final[int] = 1
# Locked Phase 7 Wave 0 default (diagnosis audit 2026-05-30-1952 §1, §3): one
# task per crewmate ends 4p/1i games by median tick 9, before any
# kill->body->report chain can complete (4/50 meetings). Two tasks per crewmate
# lengthens games so bodies can outlive the win condition. The seeder parameter
# itself stays 1 (see ``orchestrator.seeder.seed_initial_state``); this
# default-of-2 is applied only at the harness/CLI layer, so the committed-replay
# loader keeps re-seeding the 4p/1i baseline byte-identically.
DEFAULT_TASKS_PER_CREWMATE: Final[int] = 2


@dataclass(frozen=True)
class RosterPreset:
    """A named, data-only roster configuration (DESIGN.md §1.4, §3.1).

    Bundles the three roster knobs — ``num_players``, ``num_impostors``, and
    ``tasks_per_crewmate`` — under one name so the eval harness (and, in a later
    frontend task, the replay picker) can refer to a config by name instead of
    restating all three values. Frozen and behaviour-free by design: a future
    frontend task can surface the same names without a code change.
    """

    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


# The two canonical roster presets (DESIGN.md §3.5, §8.1). ``4p1i`` is the flat
# descriptor-less determinism/leak reference, pinned at ``tasks_per_crewmate=1``
# — NOT the new default of 2 — so it reproduces the byte-identical committed
# 4p/1i baseline. ``9p2i`` is the canonical eval roster: parity reaches at 5 crew
# deaths (7 crew), so games run longer and surface more meetings, at 2 tasks per
# crewmate. Per-player task instances (DESIGN.md §3.2; the Phase 8 seed-cap
# removal) let its 7×2=14 task instances overlap the 12 map tasks, which the old
# ``num_crewmates × tasks_per_crewmate ≤ len(map.tasks)`` cap forbade.
ROSTER_PRESETS: Final[Mapping[str, RosterPreset]] = {
    "4p1i": RosterPreset(num_players=4, num_impostors=1, tasks_per_crewmate=1),
    "9p2i": RosterPreset(num_players=9, num_impostors=2, tasks_per_crewmate=2),
}

# Static map of prompt-template id → version string. The versions are
# embedded as comments + a visible "Prompt: <id>" marker line in the .j2
# files (see ``agents/strategic/prompts/*.j2``); maintaining the mapping
# here keeps the replay record's :attr:`MeetingReplayEntry.prompt_versions`
# in sync without a runtime regex over the loaded templates. Bump the
# string here whenever the matching template header is bumped.
#
# Task 8.8 bumped ALL FOUR templates in lockstep because the reactive
# accusation-chain reshape (DESIGN.md §5.2) is a behavior-shifting change
# to every meeting prompt: the four ``.j2`` templates now emit the
# chain shapes (opening / reactive reply / opt-in / vote) against the
# ``MeetingTurn`` schema. The four versions must move together — a partial
# bump fails the manifest/replay provenance cross-check. The reshape is one
# of the Phase-8 byte-breakers, so both committed sets are re-recorded in
# Task 8.12 under these revisions (there is no byte-identity left to
# preserve, which is why the old vote_ballot v1-body / v2-record split is
# also retired here). This map is metadata only (never rendered into a
# prompt); the recorded value is the AUTHORITATIVE revision read by
# replay/eval and the sample MANIFESTs.
DEFAULT_PROMPT_VERSIONS: Final[Mapping[str, str]] = {
    "crewmate_report": "crewmate_report.v2",
    "impostor_report": "impostor_report_v3",
    "accusation_round": "accusation_round.v4",
    "vote_ballot": "vote_ballot/v3",
}

# Headless recording runs meetings deadline-free (DESIGN.md §1.4, §5.2, §8.3:
# "Meeting deadlines off in headless mode; on with generous defaults in live
# mode"). The choice is made explicit HERE, at the production headless
# construction site (:func:`build_default_meeting_runner`), rather than left to
# the interactive ``MeetingDeadlines`` 30 s default: audit gp-2 found the
# headless recorder silently ran the interactive 30 s per-turn/per-vote
# deadlines, so slow local-Ollama calls lost 11 turns (9 of 91 openings) to a
# wall-clock race with no record of any kind. ``None`` disables the deadline
# (passed straight to ``asyncio.wait_for``); a provider-level transport timeout
# remains the fail-loud guard via ``meetings.manager._isolate_provider_timeout``.
HEADLESS_MEETING_DEADLINES: Final[MeetingDeadlines] = MeetingDeadlines(
    turn_seconds=None, vote_seconds=None
)

# Sentinel ``model`` for a ``deadline_default`` failed-call marker. Such a
# marker carries ZERO spend (a wall-clock miss completed nothing; a validation
# default's real spend is already captured in the meeting's ``llm_calls``), so
# it must never be mistaken for a model call -- this clearly-labelled phantom
# keeps it a distinct, non-spend bucket in any per-model cost roll-up.
_DEADLINE_DEFAULT_MODEL: Final[str] = "(deadline_default)"

_T = TypeVar("_T")


# ---------------------------------------------------------------------------
# Meeting wiring — protocols, artifacts, and the default runner.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MeetingArtifacts:
    """Bundle returned by a :class:`MeetingRunner` (DESIGN.md §11.4).

    Carries the :class:`MeetingResult` plus the per-call LLM telemetry
    and the prompt-version metadata the replay log needs to persist a
    full audit trail per the R-9 acceptance gate.

    ``defaulted_calls`` carries any turn / ballot that fell back to its
    placeholder during the meeting (audit gp-2). The orchestrator writes one
    visible ``deadline_default`` :class:`~orchestrator.replay.FailedCallReplayEntry`
    per entry so a defaulted turn is never lost from the replay. It defaults to
    ``()`` so a runner that produces no defaults -- the common case -- need not
    set it.
    """

    result: MeetingResult
    llm_calls: tuple[LLMCallRecord, ...]
    prompt_versions: Mapping[str, str]
    defaulted_calls: tuple[DefaultedCall, ...] = ()


@runtime_checkable
class MeetingRunner(Protocol):
    """Drive one meeting end-to-end from inside the tick loop.

    The orchestrator dispatches here when ``state.phase == "MEETING"``.
    Implementations own the wiring (LLM client, prompt callables,
    participant construction); the orchestrator only consumes the
    returned :class:`MeetingArtifacts`. The runner MUST NOT mutate
    ``state``; engine-state application happens through
    :func:`apply_meeting_result` after the runner returns
    (DESIGN.md §1.3, §5.1).
    """

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts: ...


@runtime_checkable
class MeetingAwareAgent(Protocol):
    """Agent that exposes the inputs a meeting needs (DESIGN.md §5.1, §6.6).

    The default :class:`MeetingRunner` (:class:`DefaultMeetingRunner`)
    consumes this protocol to build :class:`MeetingParticipant`s from
    each living agent. Tactical agents instantiated by
    :func:`build_default_agent_factory` satisfy this protocol; tests
    that do not exercise meetings can use any
    :class:`AgentInterface` implementer.
    """

    @property
    def agent_id(self) -> PlayerId: ...

    @property
    def role(self) -> Role: ...

    def render_memory_for_meeting(
        self, *, token_budget: int = DEFAULT_TOKEN_BUDGET
    ) -> str: ...

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]: ...


class _RecordingLLMClient:
    """LLM client adapter that captures every call for replay.

    Wraps an inner :class:`LLMClient` and appends one
    :class:`LLMCallRecord` per :meth:`complete` call. The records are
    drained by :class:`DefaultMeetingRunner` after each meeting and
    written into the replay log so LLM-layer determinism can be
    achieved by replaying the recorded outputs rather than re-calling
    the provider (DESIGN.md §11.4).
    """

    def __init__(self, inner: LLMClient) -> None:
        self._inner = inner
        self._calls: list[LLMCallRecord] = []

    @property
    def calls(self) -> tuple[LLMCallRecord, ...]:
        return tuple(self._calls)

    def drain(self) -> tuple[LLMCallRecord, ...]:
        drained = tuple(self._calls)
        self._calls.clear()
        return drained

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: _LLMCallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        response = await self._inner.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        self._calls.append(
            LLMCallRecord(
                call_kind=call_kind,
                model=response.model,
                prompt=prompt,
                response_text=response.text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cost_usd=response.cost_usd,
                agent_id=agent_id,
            )
        )
        return response


class DefaultMeetingRunner:
    """Default :class:`MeetingRunner` wiring (DESIGN.md §5.1, §11.4).

    Builds one :class:`MeetingParticipant` per living
    :class:`MeetingAwareAgent`, runs the underlying
    :class:`MeetingManager`, and returns the artifacts plus the
    recorded LLM-call telemetry. The :class:`_RecordingLLMClient`
    wrapper is the integration point: it sits between the manager
    and the user-supplied :class:`LLMClient` so every call lands in
    the replay record without each prompt callable having to know
    about replay.
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
        prompt_versions: Mapping[str, str] = DEFAULT_PROMPT_VERSIONS,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
    ) -> None:
        self._recording_client = _RecordingLLMClient(llm_client)
        self._manager = MeetingManager(
            llm_client=self._recording_client,
            crewmate_report_prompt=crewmate_report_prompt,
            impostor_report_prompt=impostor_report_prompt,
            statement_prompt=statement_prompt,
            vote_prompt=vote_prompt,
            config=config,
        )
        self._prompt_versions = dict(prompt_versions)
        self._token_budget = token_budget

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        # Drop any stale captures left over from a prior run that
        # raised mid-meeting. Without this the leftover records would
        # silently attach to this meeting's replay payload and
        # contaminate llm_calls counts + cost metadata.
        self._recording_client.drain()
        participants = _build_participants(
            state=state,
            agents=agents,
            token_budget=self._token_budget,
        )
        try:
            result = await self._manager.run(
                meeting_id=meeting_id,
                trigger=trigger,
                participants=participants,
            )
        except BaseException:
            # On failure, drop the partial captures so a retry against
            # the same runner does not double-count completed prefixes.
            self._recording_client.drain()
            raise
        return MeetingArtifacts(
            result=result,
            llm_calls=self._recording_client.drain(),
            prompt_versions=dict(self._prompt_versions),
            # Surface any fired turn / ballot defaults so the orchestrator
            # records them visibly in the replay (audit gp-2). Read straight
            # off the manager, which reset its ledger at the start of this run.
            defaulted_calls=self._manager.defaulted_calls,
        )


def build_default_meeting_runner(
    *,
    llm_client: LLMClient | None = None,
    budget: GameBudget | None = None,
    config: MeetingConfig | None = None,
    prompt_versions: Mapping[str, str] = DEFAULT_PROMPT_VERSIONS,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> DefaultMeetingRunner:
    """Construct the production default meeting runner (DESIGN.md §5.1, §11.4).

    This is the single wire-up surface the public entry-points
    (:mod:`scripts.run_game`, and :mod:`scripts.run_tournament` via
    :func:`eval.balance_eval.run_balance_eval`) use to turn the meeting
    machinery Tasks 3.8-3.12 built into a runnable production default.
    It binds the four canonical ``agents/strategic/prompts`` Jinja
    callables to a :class:`DefaultMeetingRunner`.

    ``llm_client`` defaults to :func:`llm.provider.build_default_client`,
    which selects the adapter from ``AILIBI_LLM_PROVIDER`` (defaulting to
    :class:`llm.fake_provider.FakeProvider` when the env var is unset, so
    CI / headless runs still never touch the network). Setting
    ``AILIBI_LLM_PROVIDER=anthropic`` routes the public entry-points
    through :class:`llm.provider.AnthropicClient`; callers may still pass
    an explicit ``llm_client`` to bypass env selection. When ``budget`` is
    provided the client is wrapped in
    :class:`llm.budgeted_client.BudgetedLLMClient` *before* the runner's
    :class:`_RecordingLLMClient` layer, so the per-game cost cap is
    enforced at call time (pre-flight) rather than measured post-hoc
    from the replay log.

    When ``config`` is omitted the runner is wired deadline-free
    (:data:`HEADLESS_MEETING_DEADLINES`, i.e. ``turn_seconds=None`` /
    ``vote_seconds=None``): this is the production HEADLESS recording surface
    and recording must never lose a turn to a wall-clock race (audit gp-2;
    DESIGN.md §1.4, §8.3). An interactive/live caller passes an explicit
    ``MeetingConfig`` to opt back into the 30 s ``MeetingDeadlines`` default.

    Production callers construct a fresh runner + a fresh
    :class:`llm.budget.GameBudget` per game: the budget must reset
    between games and the recording client carries per-game state. Do
    not share one runner (or one budget) across a tournament.
    """

    inner: LLMClient = llm_client if llm_client is not None else build_default_client()
    client: LLMClient = (
        BudgetedLLMClient(inner=inner, budget=budget) if budget is not None else inner
    )
    # This is the production HEADLESS recording surface, so an unspecified
    # config runs deadline-free (audit gp-2): recording must never lose a turn
    # to a wall-clock race. An explicit ``config`` is honoured unchanged, so an
    # interactive/live caller opts back into the 30 s ``MeetingDeadlines``
    # default by passing its own ``MeetingConfig``.
    resolved_config = (
        config
        if config is not None
        else MeetingConfig(deadlines=HEADLESS_MEETING_DEADLINES)
    )
    return DefaultMeetingRunner(
        llm_client=client,
        crewmate_report_prompt=crewmate_report_prompt,
        impostor_report_prompt=impostor_report_prompt,
        statement_prompt=accusation_round_prompt,
        vote_prompt=vote_ballot_prompt,
        config=resolved_config,
        prompt_versions=prompt_versions,
        token_budget=token_budget,
    )


def _build_participants(
    *,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    token_budget: int,
) -> tuple[MeetingParticipant, ...]:
    """Build one :class:`MeetingParticipant` per living agent.

    Every living agent referenced in ``state.players`` must be a
    :class:`MeetingAwareAgent`; the firewall (DESIGN.md §1.3) keeps
    rendered memory and suspicion graph on the agent side, so the
    orchestrator can't synthesize them without the agent's
    cooperation. Fail-loud at the boundary rather than silently
    feeding the meeting an empty rendered memory.

    ``fellow_impostor_ids`` (Task 7.12, audit gp-imp-1) is derived here
    from world-state roles — the same firewall-safe self-channel data
    :class:`observation.service.ObservationService` puts on
    ``SelfView`` (Task 7.2) and the kill policy already consumes (Task
    7.9). For an impostor participant it is the sorted ids of the OTHER
    impostors (by role, independent of alive state, so an impostor
    still knows a teammate ejected earlier in the game); it is ``()``
    for every crewmate and for a sole impostor, and never contains the
    participant's own id. The orchestrator is the right place to read
    roles: the meeting layer is engine-pure and must not re-derive them.
    """

    impostor_ids = tuple(
        sorted(
            player_id
            for player_id, player in state.players.items()
            if player.role == "IMPOSTOR"
        )
    )

    participants: list[MeetingParticipant] = []
    for player_id in sorted(state.players):
        player = state.players[player_id]
        if not player.alive:
            continue
        agent = agents.get(player_id)
        if agent is None:
            raise ValueError(
                f"orchestrator missing agent for living player {player_id!r}; "
                "every alive player in a meeting-enabled game must have a "
                "constructed agent"
            )
        if not isinstance(agent, MeetingAwareAgent):
            raise TypeError(
                f"agent for {player_id!r} does not implement MeetingAwareAgent; "
                "meeting-enabled HeadlessGame requires agents that expose "
                "render_memory_for_meeting() and suspicion_graph_for_meeting()"
            )
        # Crewmates (and a sole impostor) get ``()``; an impostor gets the
        # other impostors' ids, never its own. This is the meeting-side
        # mirror of the SelfView firewall invariant: teammate identity
        # enters only an impostor's own meeting inputs, never a crewmate's.
        fellow_impostor_ids = (
            tuple(pid for pid in impostor_ids if pid != player_id)
            if player.role == "IMPOSTOR"
            else ()
        )
        participants.append(
            MeetingParticipant(
                agent_id=player_id,
                role=player.role,
                rendered_memory=agent.render_memory_for_meeting(
                    token_budget=token_budget
                ),
                suspicion_graph=agent.suspicion_graph_for_meeting(),
                fellow_impostor_ids=fellow_impostor_ids,
            )
        )
    return tuple(participants)


# ---------------------------------------------------------------------------
# Meeting outcome → engine-owned state application.
# ---------------------------------------------------------------------------


def _validate_runner_result(
    *,
    result: MeetingResult,
    expected_meeting_id: str,
    expected_trigger: MeetingTrigger,
) -> None:
    """Reject a :class:`MeetingResult` whose trigger fields drift from the engine.

    The orchestrator builds the canonical :class:`MeetingTrigger` from
    the :class:`MeetingTriggeredEvent` the engine emitted; the runner
    receives it verbatim. The returned :class:`MeetingResult` echoes
    back ``meeting_id`` / ``triggered_by`` / ``trigger_tick`` and the
    orchestrator persists those into the replay record. A buggy or
    custom runner could swap any of those fields, causing the replay
    log to contradict the engine event that actually opened the
    meeting — which silently breaks downstream provenance for
    eval / replay tooling. Fail loud here instead.
    """

    if result.meeting_id != expected_meeting_id:
        raise ValueError(
            "MeetingRunner returned a MeetingResult whose meeting_id "
            f"{result.meeting_id!r} does not match the dispatched "
            f"meeting_id {expected_meeting_id!r}; this is an "
            "orchestrator-runner wiring bug"
        )
    if result.triggered_by != expected_trigger.triggered_by:
        raise ValueError(
            "MeetingRunner returned a MeetingResult whose triggered_by "
            f"{result.triggered_by!r} does not match the engine-emitted "
            f"trigger {expected_trigger.triggered_by!r}"
        )
    if result.trigger_tick != expected_trigger.trigger_tick:
        raise ValueError(
            "MeetingRunner returned a MeetingResult whose trigger_tick "
            f"{result.trigger_tick} does not match the engine-emitted "
            f"trigger_tick {expected_trigger.trigger_tick}"
        )


def apply_meeting_result(
    state: WorldState,
    result: MeetingResult,
    *,
    game_map: Map,
    triggering_body_id: BodyId | None = None,
) -> tuple[WorldState, list[EngineEvent]]:
    """Apply a :class:`MeetingResult` to engine-owned state (DESIGN.md §3.1, §5.1).

    Lives in the orchestrator (not ``engine/``) because applying a
    meeting outcome is an orchestration concern: the engine remains a
    pure ``(state, actions) -> (state', events)`` function and the
    meeting manager remains engine-pure. The orchestrator is the only
    module allowed to mutate engine-owned state outside an
    ``advance_tick`` call.

    The returned state is ready to be fed back into the next
    :func:`advance_tick`: phase is ``PLAY`` (unless the ejection
    triggered a win), tick is incremented by one (per DESIGN.md §3.1
    "returns control to tick t+1"), and the rng is advanced one step
    so the rng cursor remains in lockstep with the tick counter (a
    successful normal tick advances both, so the meeting tick must do
    the same).

    For an ``EJECTED`` outcome the ejected player's ``alive`` flag is
    cleared, their ``last_action`` is reset to ``None`` so the next
    tick's task-progress pass does not try to continue their task,
    their cooldown entry is removed, and their incomplete tasks are
    dropped per the dead-crewmate-task rule (DESIGN.md §3.5; same
    semantics as a kill).

    Win conditions are re-evaluated after the ejection. An ejection
    that reaches impostor parity, sabotage timeout, or completes the
    crew task pool emits a :class:`GameOverEvent` and the returned
    state has ``phase == "GAME_OVER"``.

    The cooldown / sabotage / emergency-uses counters are unchanged
    during the meeting tick because DESIGN.md §5.1 freezes engine
    state during a meeting ("kill cooldown paused"). The next normal
    tick will decrement them via the standard step-2 of
    :func:`advance_tick`.
    """

    if state.phase != "MEETING":
        raise ValueError(
            f"apply_meeting_result requires state.phase=='MEETING', got {state.phase!r}"
        )

    events: list[EngineEvent] = []
    working = state

    if result.outcome == "EJECTED":
        ejected_id = result.ejected_player_id
        if ejected_id is None:
            raise ValueError(
                "MeetingResult outcome=='EJECTED' must carry a non-None "
                "ejected_player_id (enforced by MeetingResult validator; this "
                "branch is defense-in-depth)"
            )
        if ejected_id not in working.players:
            raise ValueError(
                f"MeetingResult.ejected_player_id={ejected_id!r} not in state.players"
            )
        if not working.players[ejected_id].alive:
            raise ValueError(
                f"cannot eject already-dead player {ejected_id!r}; the meeting "
                "should never have nominated a dead participant"
            )
        players = dict(working.players)
        ejected = players[ejected_id]
        players[ejected_id] = replace(ejected, alive=False, last_action=None)
        # Dead-crewmate task rule: DESIGN.md §3.5 dropped. Mirror
        # ``engine/tick.py::_apply_kill``: drop the ejected player's
        # incomplete tasks so the crew win check counts only alive-
        # owned tasks; completed tasks remain so they still count
        # toward ``crew_tasks_done``.
        tasks = {
            task_id: task
            for task_id, task in working.tasks.items()
            if not (task.owner == ejected_id and not task.completed)
        }
        cooldowns = dict(working.cooldowns)
        cooldowns.pop(ejected_id, None)
        working = replace(working, players=players, tasks=tasks, cooldowns=cooldowns)

    # Consume the corpse that triggered a body-report meeting. The
    # engine's visibility layer already hides bodies whose
    # ``discovered_by`` is set, so default tactical agents cannot
    # re-report the body via observation. But ``engine.rules.resolve_report``
    # does not reject already-discovered bodies, so a hardcoded /
    # adversarial intent with the same body_id would otherwise
    # repeatedly re-trigger meetings after gameplay resumes. Drop
    # the body here so the trigger surface is the same as the
    # observation surface.
    if triggering_body_id is not None and triggering_body_id in working.bodies:
        bodies = dict(working.bodies)
        del bodies[triggering_body_id]
        working = replace(working, bodies=bodies)

    # Re-evaluate win conditions on the post-ejection (or
    # post-skip) world. A skipped meeting cannot newly satisfy a win
    # condition by itself, but the check is unconditional so a future
    # mid-meeting state mutation cannot silently bypass the gate.
    win_result = resolve_win_conditions(working)
    if win_result is not None:
        game_over_state = replace(working, phase="GAME_OVER")
        events.append(
            GameOverEvent(
                type="GameOver",
                tick=state.tick,
                winner=win_result.winner,
                reason=win_result.reason,
            )
        )
        return game_over_state, events

    # Advance the rng cursor one step so the per-tick rng-state
    # transition mirrors the end-of-tick advance in
    # :func:`advance_tick`. Without this step the rng cursor would
    # stall across the meeting boundary and a replay that ran with a
    # different meeting outcome could re-sync rng state by accident.
    rng = EngineRng.from_state(working.rng_state)
    _, next_rng_state = rng.randint(0, 2**31 - 1)
    next_state = replace(
        working,
        phase="PLAY",
        tick=working.tick + 1,
        rng_state=next_rng_state,
    )
    return next_state, events


# ---------------------------------------------------------------------------
# Headless game loop.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HeadlessGameResult:
    """Outcome bundle returned by :meth:`HeadlessGame.run`.

    ``outcome`` is one of:

    - ``CREWMATES`` / ``IMPOSTORS``: an engine ``GameOverEvent`` fired
      and named the winner. ``final_state.phase`` is ``GAME_OVER``.
    - ``MEETING_PHASE_REACHED``: a ``ReportBody`` or ``EmergencyMeeting``
      intent transitioned the engine to ``MEETING`` and no
      :class:`MeetingRunner` was configured to resume the game. The
      orchestrator pauses here without mutating state. ``final_state``
      has ``phase == "MEETING"``. This is the engine-only opt-out for
      Phase 2 byte-identity tests; production paths always pass a
      runner (see :func:`build_default_meeting_runner`) and never reach
      this outcome.
    - ``TICK_BUDGET_REACHED``: :class:`TickScheduler` capped the game
      before it ended naturally. ``final_state.phase`` is ``PLAY``.
      The partial replay is still written to ``replay_path``.
    """

    final_state: WorldState
    outcome: Outcome
    replay_path: Path


class HeadlessGame:
    """Run one deterministic headless game from a seed."""

    def __init__(
        self,
        *,
        seed: int,
        game_map: Map,
        agent_factory: AgentFactory,
        replay_path: Path,
        audit_log_path: Path | None = None,
        num_players: int = DEFAULT_NUM_PLAYERS,
        num_impostors: int = DEFAULT_NUM_IMPOSTORS,
        tasks_per_crewmate: int = DEFAULT_TASKS_PER_CREWMATE,
        scheduler: TickScheduler | None = None,
        meeting_runner: MeetingRunner | None = None,
        force: bool = False,
    ) -> None:
        self._seed = seed
        self._game_map = game_map
        self._agent_factory = agent_factory
        self._replay_path = replay_path
        # Passed through to ReplayLog: force=True truncates a pre-existing
        # replay file at construction (just before this game writes it),
        # force=False (default) makes a re-run against an existing path fail
        # loud (DESIGN.md §11.4; Task 4.16). run() keeps its existing
        # signature; the flag rides the constructor.
        self._force = force
        self._audit_log_path = (
            audit_log_path
            if audit_log_path is not None
            else replay_path.parent / f"{replay_path.stem}.audit.jsonl"
        )
        self._num_players = num_players
        self._num_impostors = num_impostors
        self._tasks_per_crewmate = tasks_per_crewmate
        self._scheduler = (
            scheduler
            if scheduler is not None
            else TickScheduler(max_ticks=DEFAULT_MAX_TICKS)
        )
        self._public_map = public_map_from_engine_map(game_map)
        self._meeting_runner = meeting_runner

    @property
    def public_map(self) -> PublicMapView:
        return self._public_map

    @property
    def replay_path(self) -> Path:
        return self._replay_path

    def run(self) -> HeadlessGameResult:
        """Run the headless tick loop until terminate, meeting, or tick budget.

        Each iteration: build observations for every alive agent,
        dispatch them, collect :class:`ActionIntent`s, translate to
        engine actions, advance the engine one tick, and append to
        the replay log. When the engine transitions to ``MEETING``
        and a :class:`MeetingRunner` is configured, dispatch to the
        runner, persist the meeting artifacts in the replay log,
        apply the outcome to engine-owned state through
        :func:`apply_meeting_result`, and continue. When no runner
        is configured the loop returns ``MEETING_PHASE_REACHED`` as
        in Phase 2.
        """

        state = seed_initial_state(
            seed=self._seed,
            game_map=self._game_map,
            num_players=self._num_players,
            num_impostors=self._num_impostors,
            tasks_per_crewmate=self._tasks_per_crewmate,
        )
        observation_service = ObservationService(
            game_map=self._game_map,
            audit_log_path=self._audit_log_path,
        )
        replay = ReplayLog(
            self._replay_path, game_id=self._game_id(), force=self._force
        )
        agents = self._build_agents(state.players)

        # Close the per-game replay + audit handles deterministically at every
        # loop exit (game over, tick budget, meeting pause, or exception). Both
        # logs flush each row as it is written, so this only releases the file
        # descriptors (Task 5.9 write-cadence pass); the recorded bytes — and
        # therefore the determinism contract — are unchanged.
        try:
            return self._run_loop(
                state=state,
                observation_service=observation_service,
                replay=replay,
                agents=agents,
            )
        finally:
            replay.close()
            observation_service.close()

    def _run_loop(
        self,
        *,
        state: WorldState,
        observation_service: ObservationService,
        replay: ReplayLog,
        agents: dict[PlayerId, AgentInterface],
    ) -> HeadlessGameResult:
        """Drive the tick loop until terminate, meeting, or tick budget.

        Extracted from :meth:`run` so the handle close lives in a single
        ``finally`` around every loop exit (Task 5.9). The replay log and
        observation service are owned by :meth:`run`, which closes them.
        """

        last_events: tuple[EngineEvent, ...] = ()
        meeting_counter = 0
        while state.phase != "GAME_OVER":
            if not self._scheduler.should_continue(state.tick):
                return HeadlessGameResult(
                    final_state=state,
                    outcome="TICK_BUDGET_REACHED",
                    replay_path=self._replay_path,
                )

            packets = self._build_packets(
                state=state,
                observation_service=observation_service,
                last_events=last_events,
            )
            intents = self._collect_intents(packets=packets, agents=agents)
            actions = list(translate_action_intents_for_tick(intents))
            input_tick = state.tick
            state, events = advance_tick(state, actions, game_map=self._game_map)
            last_events = tuple(events)
            replay.record_tick(input_tick, actions, state)

            if state.phase == "MEETING":
                if self._meeting_runner is None:
                    # Engine-only opt-out for Phase 2 byte-identity tests;
                    # production paths always pass a runner. The public
                    # entry-points (scripts/run_*.py, eval/balance_eval.py)
                    # build a DefaultMeetingRunner via
                    # build_default_meeting_runner and never reach this
                    # branch; only callers that explicitly pass
                    # meeting_runner=None (engine-only replay) land here.
                    return HeadlessGameResult(
                        final_state=state,
                        outcome="MEETING_PHASE_REACHED",
                        replay_path=self._replay_path,
                    )
                pre_meeting_events = last_events
                state, post_events = self._run_and_apply_meeting(
                    state=state,
                    events=pre_meeting_events,
                    agents=agents,
                    replay=replay,
                    meeting_index=meeting_counter,
                )
                meeting_counter += 1
                # Preserve the events the engine emitted on the
                # meeting-trigger tick (e.g. a ``KilledEvent`` that
                # landed in the same action queue as the report).
                # ``ObservationService._observed_actions_for_agent``
                # reads ``engine_events`` to surface kills and vent
                # uses as observed actions; dropping the pre-meeting
                # events here would silently regress agent perception
                # on the resume tick.
                last_events = pre_meeting_events + tuple(post_events)

        # The engine fired a GameOverEvent (the while loop only exits
        # GAME_OVER via that event). Persist the decisive outcome as the
        # final replay row so win-rate is recoverable from any replay log,
        # including a partial tournament that crashed mid-run (Task 3.19
        # finding 3).
        game_over_event = self._game_over_event(last_events)
        replay.record_game_end(
            winner=game_over_event.winner,
            reason=game_over_event.reason,
            tick=game_over_event.tick,
        )
        return HeadlessGameResult(
            final_state=state,
            outcome=game_over_event.winner,
            replay_path=self._replay_path,
        )

    def _run_and_apply_meeting(
        self,
        *,
        state: WorldState,
        events: Sequence[EngineEvent],
        agents: Mapping[PlayerId, AgentInterface],
        replay: ReplayLog,
        meeting_index: int,
    ) -> tuple[WorldState, list[EngineEvent]]:
        if self._meeting_runner is None:
            raise RuntimeError(
                "_run_and_apply_meeting called without a configured meeting runner"
            )
        trigger, triggering_body_id = _build_meeting_trigger(state=state, events=events)
        meeting_id = f"{self._game_id()}:meeting-{meeting_index}"
        try:
            artifacts = _drive_async(
                self._meeting_runner.run_meeting(
                    meeting_id=meeting_id,
                    trigger=trigger,
                    state=state,
                    agents=agents,
                )
            )
        except BaseException as exc:
            # A meeting that aborts because a structured-output response
            # failed schema validation carries the rejected call's cost +
            # partial response on the propagating ValidationError (see
            # llm.provider.extract_parse_failure). Persist it before the
            # crash propagates so per-meeting cost is auditable for the
            # meeting that broke the run (Task 3.19 finding 2). The meeting
            # still aborts — the caller cannot proceed without a valid
            # response — so the exception is re-raised unchanged.
            failure = extract_parse_failure(exc)
            if failure is not None:
                replay.record_failed_call(
                    meeting_id=meeting_id,
                    tick=trigger.trigger_tick,
                    model=failure.model,
                    prompt_length=failure.prompt_length,
                    raw_response=failure.raw_response,
                    input_tokens=failure.input_tokens,
                    output_tokens=failure.output_tokens,
                    cost_usd=failure.cost_usd,
                    error_type=failure.error_type,
                    error_message=failure.error_message,
                )
            raise
        _validate_runner_result(
            result=artifacts.result,
            expected_meeting_id=meeting_id,
            expected_trigger=trigger,
        )
        state_hash_before = _state_hash(state)
        next_state, post_events = apply_meeting_result(
            state,
            artifacts.result,
            game_map=self._game_map,
            triggering_body_id=triggering_body_id,
        )
        state_hash_after = _state_hash(next_state)
        replay.record_meeting(
            meeting_id=meeting_id,
            result=artifacts.result,
            llm_calls=artifacts.llm_calls,
            prompt_versions=artifacts.prompt_versions,
            state_hash_before=state_hash_before,
            state_hash_after=state_hash_after,
        )
        # Make any fired turn / ballot default visible in the replay (audit
        # gp-2): one ``deadline_default`` failed-call marker per default, so a
        # husk turn is never silently dropped from the record.
        _record_deadline_defaults(
            replay=replay,
            meeting_id=meeting_id,
            tick=trigger.trigger_tick,
            defaulted_calls=artifacts.defaulted_calls,
        )
        return next_state, post_events

    def _build_agents(
        self,
        players: Mapping[PlayerId, PlayerState],
    ) -> dict[PlayerId, AgentInterface]:
        agents: dict[PlayerId, AgentInterface] = {}
        for player_id in sorted(players):
            agents[player_id] = self._agent_factory(player_id, players[player_id].role)
        return agents

    def _build_packets(
        self,
        *,
        state: WorldState,
        observation_service: ObservationService,
        last_events: tuple[EngineEvent, ...],
    ) -> dict[PlayerId, ObservationPacket]:
        packets: dict[PlayerId, ObservationPacket] = {}
        for player_id in sorted(state.players):
            if not state.players[player_id].alive:
                continue
            packets[player_id] = observation_service.build_packet(
                world_state=state,
                agent_id=player_id,
                engine_events=last_events,
            )
        return packets

    def _collect_intents(
        self,
        *,
        packets: Mapping[PlayerId, ObservationPacket],
        agents: Mapping[PlayerId, AgentInterface],
    ) -> list[ActionIntent]:
        return [
            agents[player_id].decide(packets[player_id], self._public_map)
            for player_id in sorted(packets)
        ]

    def _game_over_event(self, last_events: tuple[EngineEvent, ...]) -> GameOverEvent:
        for event in last_events:
            if isinstance(event, GameOverEvent):
                return event
        raise RuntimeError("game loop exited PLAY without emitting a GameOverEvent")

    def _game_id(self) -> str:
        return f"headless-seed-{self._seed}"


def _record_deadline_defaults(
    *,
    replay: ReplayLog,
    meeting_id: str,
    tick: int,
    defaulted_calls: Sequence[DefaultedCall],
) -> None:
    """Record each fired meeting default as a visible replay entry (audit gp-2).

    A turn / ballot that fell back to its placeholder is written into the
    EXISTING failed-call channel as a
    :class:`~orchestrator.replay.FailedCallReplayEntry` with
    ``error_type="deadline_default"`` -- no new replay record kind, since
    ``FailedCallReplayEntry.error_type`` is a free string. The marker carries
    ZERO spend: a deadline miss completed nothing, and a validation default's
    real spend is already captured in the meeting's ``llm_calls`` (the recording
    client logged the returned-but-invalid call), so charging it here too would
    double-count. The defaulted phase and the trigger kind (deadline vs
    validation) are named in ``error_message`` so the husk is auditable -- the
    headless recorder previously lost such turns with no record of any kind
    while telemetry reported ``failed_calls=0`` (true of the records, false of
    the run).
    """

    for default in defaulted_calls:
        replay.record_failed_call(
            meeting_id=meeting_id,
            tick=tick,
            model=_DEADLINE_DEFAULT_MODEL,
            prompt_length=0,
            raw_response="",
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            error_type="deadline_default",
            error_message=_deadline_default_message(default),
        )


def _deadline_default_message(default: DefaultedCall) -> str:
    """Human-readable ``error_message`` for a ``deadline_default`` record.

    Names the defaulted phase and the trigger kind (``deadline`` vs
    ``validation``) plus the participant who submitted nothing; the meeting id
    and tick ride the entry's own fields.
    """

    if default.phase == "vote":
        return (
            f"vote defaulted ({default.trigger}); "
            f"{default.agent_id} submitted no ballot"
        )
    index = "" if default.turn_index is None else f" (turn {default.turn_index})"
    return (
        f"{default.phase} turn{index} defaulted ({default.trigger}); "
        f"{default.agent_id} submitted no turn"
    )


def _build_meeting_trigger(
    *,
    state: WorldState,
    events: Sequence[EngineEvent],
) -> tuple[MeetingTrigger, BodyId | None]:
    """Construct a :class:`MeetingTrigger` from the engine's transition events.

    The engine emits a :class:`MeetingTriggeredEvent` from
    :mod:`engine.tick._apply_report` / ``_apply_emergency`` whenever a
    valid ``ReportBody`` / ``EmergencyMeeting`` action drives the
    world into ``MEETING`` phase. The orchestrator pulls the most
    recent such event off the engine's emitted event list and renders
    it into the human-readable description the report prompt
    surfaces.

    The second element of the returned tuple is the ``body_id`` of
    the corpse that triggered a ``report`` meeting (``None`` for an
    ``emergency`` meeting). :func:`apply_meeting_result` consumes
    that body so a hardcoded second report cannot re-trigger a meeting
    on the same corpse after gameplay resumes (defense in depth — the
    visibility layer already hides discovered bodies from default
    tactical agents, but the engine's ``resolve_report`` does not
    reject already-discovered bodies, so an adversarial / scripted
    intent could otherwise replay the trigger).
    """

    trigger_event: MeetingTriggeredEvent | None = None
    for event in events:
        if isinstance(event, MeetingTriggeredEvent):
            trigger_event = event
    if trigger_event is None:
        raise RuntimeError(
            "engine transitioned to MEETING phase without emitting a "
            "MeetingTriggeredEvent; this is an engine invariant violation"
        )
    body_id: BodyId | None
    if trigger_event.trigger == "report":
        body_id = trigger_event.body_id
        description = (
            f"{trigger_event.actor} reported "
            + (f"body {body_id} " if body_id is not None else "a body ")
            + f"at tick {trigger_event.tick}"
        )
    else:
        body_id = None
        description = (
            f"{trigger_event.actor} called an emergency meeting at tick "
            f"{trigger_event.tick}"
        )
    trigger = MeetingTrigger(
        triggered_by=trigger_event.actor,
        trigger_tick=trigger_event.tick,
        description=description,
    )
    return trigger, body_id


def _drive_async(coro: Coroutine[object, object, _T]) -> _T:
    """Run an async coroutine to completion from a synchronous context.

    Refuses to run when the caller is already inside an event loop —
    that would deadlock or silently spawn a nested loop. The
    orchestrator's :meth:`HeadlessGame.run` is synchronous by
    contract; the only sanctioned path into the meeting subsystem
    runs through this helper.
    """

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError(
        "HeadlessGame.run() must not be called from a running event loop; "
        "the orchestrator drives async meeting code via asyncio.run()"
    )


# ---------------------------------------------------------------------------
# Tactical agent — composite memory + tactical policy.
# ---------------------------------------------------------------------------


class TacticalAgent:
    """Default tactical agent that bridges perception, memory, and policy.

    The orchestrator's default :data:`AgentFactory`
    (:func:`build_default_agent_factory`) returns one of these per
    player. Each agent owns a private :class:`AgentMemory`;
    :func:`agents.perception.ingest_packet` writes packets into the
    composite memory's episodic store, then the tactical policy reads
    the same episodic store and returns an :class:`ActionIntent`.

    The class lives in the orchestrator because it composes pieces
    from ``agents/`` (perception + memory + tactical) without leaking
    that wiring back into ``agents/runtime.py``; that file's stubs are
    owned by future tasks.

    For Phase 3.12, :class:`TacticalAgent` implements the
    :class:`MeetingAwareAgent` protocol: it exposes
    :meth:`render_memory_for_meeting` (token-budgeted Markdown view of
    its composite memory via :func:`render_for_prompt`) and
    :meth:`suspicion_graph_for_meeting` (a tuple of
    :class:`SuspicionEntry` rows pulled from the agent's belief
    state). The default-game integration test exercises these methods
    end-to-end through the meeting protocol.
    """

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        policy: CrewmatePolicy | ImpostorPolicy,
        role: Role | None = None,
        memory: AgentMemory | None = None,
    ) -> None:
        self._agent_id = agent_id
        self._policy = policy
        # ``role`` is optional because the legacy Phase-2 tests
        # construct a :class:`TacticalAgent` without specifying it.
        # Phase 3.12 meetings need a concrete role for participant
        # construction; the orchestrator's default agent factory
        # always passes one. Tests that bypass the factory get
        # ``"CREWMATE"`` / ``"IMPOSTOR"`` inferred from the policy
        # type so the meeting wiring still works without an extra
        # kwarg at every call site.
        self._role: Role = role if role is not None else _infer_role_from_policy(policy)
        self._memory = memory if memory is not None else AgentMemory()

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return self._role

    @property
    def memory(self) -> AgentMemory:
        return self._memory

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        if packet.agent_id != self._agent_id:
            raise ValueError(
                f"observation packet for agent {packet.agent_id!r} given to "
                f"tactical agent bound to {self._agent_id!r}"
            )
        ingest_packet(
            packet=packet,
            memory=self._memory.episodic,
            beliefs=self._memory.beliefs,
        )
        return self._policy.decide(self._memory.episodic, public_map)

    def render_memory_for_meeting(
        self, *, token_budget: int = DEFAULT_TOKEN_BUDGET
    ) -> str:
        """Token-budgeted rendered memory view (DESIGN.md §6.6)."""

        return render_for_prompt(self._memory, token_budget=token_budget)

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        """Snapshot of the agent's belief state as a suspicion graph.

        DESIGN.md §5.5 feeds the suspicion graph straight into the
        vote-ballot prompt. The entries are sorted by ``player_id``
        for deterministic prompt-input ordering.
        """

        entries: list[SuspicionEntry] = []
        for player_id in sorted(self._memory.beliefs.known_players()):
            belief = self._memory.beliefs.view(player_id)
            entries.append(
                SuspicionEntry(
                    player_id=player_id,
                    suspicion=belief.suspicion,
                    trust=belief.trust,
                )
            )
        return tuple(entries)


def _infer_role_from_policy(policy: CrewmatePolicy | ImpostorPolicy) -> Role:
    if isinstance(policy, ImpostorPolicy):
        return "IMPOSTOR"
    return "CREWMATE"


def build_default_agent_factory() -> AgentFactory:
    """Return the orchestrator's default :data:`AgentFactory`.

    Each constructed agent is a :class:`TacticalAgent` with the role-
    appropriate policy. Useful for ``scripts/run_game.py`` and for
    tests that just want a real, deterministic agent without
    scripting one.
    """

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        policy: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy = ImpostorPolicy(agent_id=agent_id)
        else:
            policy = CrewmatePolicy(agent_id=agent_id)
        return TacticalAgent(agent_id=agent_id, policy=policy, role=role)

    return factory


__all__ = [
    "AgentFactory",
    "DEFAULT_MAX_TICKS",
    "DEFAULT_NUM_IMPOSTORS",
    "DEFAULT_NUM_PLAYERS",
    "DEFAULT_PROMPT_VERSIONS",
    "DEFAULT_TASKS_PER_CREWMATE",
    "DefaultMeetingRunner",
    "HEADLESS_MEETING_DEADLINES",
    "HeadlessGame",
    "HeadlessGameResult",
    "MeetingArtifacts",
    "MeetingAwareAgent",
    "MeetingRunner",
    "Outcome",
    "ROSTER_PRESETS",
    "RosterPreset",
    "TacticalAgent",
    "apply_meeting_result",
    "build_default_agent_factory",
    "build_default_meeting_runner",
]
