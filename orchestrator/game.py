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
import os
from collections.abc import Callable, Coroutine, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Final, Literal, Protocol, TypeAlias, TypeVar, runtime_checkable

from agents.base import AgentInterface
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    absorb_meeting_evidence,
    absorb_reported_testimony,
    render_for_prompt,
    testimony_as_content_enabled,
)
from agents.perception import ingest_packet
from agents.strategic.prompts import (
    DEFAULT_PROMPT_SET,
    build_prompt_renderers,
    resolve_prompt_set,
)
from agents.tactical.crewmate_policy import CrewmatePolicy, EmergencyPacingTracker
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import BodyId, PlayerId, PlayerState, Role
from engine.events import (
    EngineEvent,
    GameOverEvent,
    MeetingTriggeredEvent,
)
from engine.rng import EngineRng
from engine.rules import resolve_win_conditions
from engine.tick import advance_tick, redistribute_dead_tasks
from engine.world import Map, WorldState
from llm.budget import GameBudget
from llm.budgeted_client import BudgetedLLMClient
from llm.client import LLMClient, LLMResponse
from llm.client import CallKind as _LLMCallKind
from llm.provider import LLMCallFailure, build_default_client, extract_parse_failure
from meetings.manager import (
    EMERGENCY_TRIGGER_PHRASE,
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
    derive_reported_testimony,
    extract_belief_evidence,
)
from meetings.schemas import (
    FoundBodyObservation,
    MeetingResult,
    ReportedStatement,
)
from meetings.transcript import MeetingTriggerKind
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
#
# Task 8.16 (DESIGN.md §5.5; audit gp-3) bumps ``vote_ballot`` alone to
# vote_ballot/v4: only the vote prompt's `primary_reason_id` example text
# changed (a real transcript turn id, never a hardcoded one), so this is a
# single-template prompt-text revision, not the four-template lockstep of
# 8.8. The committed sample / prompt-regression bytes still record v3 and
# are regenerated in Task 8.18, not here.
#
# Task 9.9 (DESIGN.md §5.1, §5.2, §5.5; audit gp-3) bumps the two TURN
# templates -- crewmate_report v3 -> v4 and accusation_round v5 -> v6: both
# gain the free_text length discipline (the 9B relocates its deliberation
# into free_text and overruns the frozen 2048 turn cap) and the gated
# living-roster accusation block (living players minus the speaker, threaded
# like the vote ballot's candidate_targets). Prompt-text revisions to the two
# turn templates only, not a lockstep bump; the committed sample bytes still
# record v3/v5 and are re-recorded in Task 9.11, not here.
#
# Task 10.3 (DESIGN.md §5.1, §5.2; audit gp-9) bumps the THREE turn templates
# -- crewmate_report v4 -> v5, impostor_report v3 -> v4, accusation_round
# v6 -> v7: the openings make the §5.2 accuse-or-declare-unsure choice a hard
# requirement (backed by the manager's opening retry), all three carry the
# list-each-sighting-once anti-repetition line, and the roster block renders
# the DEAD / ejected players as an explicit do-not-accuse line (the impostor
# template gains the roster block itself). vote_ballot is FROZEN (the §4.6
# render). The committed sample bytes still record v4/v3/v6 and are
# re-recorded in Task 10.5, not here.
#
# Task 10.8 (DESIGN.md §3.2, §5.2; audit gp-3) bumps crewmate_report alone
# v5 -> v6: the template gains an emergency-opening branch (keyed off the
# orchestrator's "called an emergency meeting" trigger description) that
# frames a body-less, called-on-suspicion meeting -- state who you suspect
# and the first-hand basis, or unsure -- now that the suspicion-accumulation
# trigger makes the emergency channel reachable for crew. The body-report
# branch is byte-identical to v5 apart from this version marker (golden-
# pinned). Lineage confirmed at branch time: builds on the v5 merged in
# Wave 0 and recorded by 10.5; no Wave-1 task touches the template in
# parallel (10.7 is prompts-frozen). The committed sample bytes still record
# v5 and are re-recorded in Task 10.9, not here.
#
# Task 10.11 (DESIGN.md §3.2, §5.2, §5.4; audit-2026-06-13-1816 B-B-1) bumps
# crewmate_report alone v6 -> v7: the emergency-opening branch must NOT present
# a `found_body` observation. On the close baseline every emergency opening
# re-narrated a real-but-stale corpse as a fresh discovery and voters anchored
# ejections on the fabrication; v7's emergency job paragraph leads with the
# suspicion that crossed the line and forbids a `found_body`. The body-report
# branch is byte-identical to v6 apart from this version marker (golden-pinned);
# only the emergency job paragraph changed. The engine half is the
# trigger-kind-gated relevance zone (:func:`meetings.transcript.triggering_body_rooms`)
# plus the emergency-opening self-check below. The committed sample bytes still
# record their as-recorded versions and are NOT re-recorded here (recording-side
# only; replays/samples out of scope).
#
# Task 10.14 (DESIGN.md §3.4, §4.5, §5.3; audit-2026-06-13-1816 D-D-1/D-D-2/D-D-7;
# experiments/lab/report-deception-battery-2.md) bumps impostor_report alone
# v4 -> v5: the impostor opening gains an ANTICIPATORY-COVER branch on a
# body-report trigger (the perform-from-a-goal directive that makes the 9B build
# its own sheltered alibi away from the kill scene and PIN the cover room/window
# so the justification does not drift). The emergency branch keeps the v4 frame
# (impostors gain no button this wave). It is the prompt half of the impostor
# toolkit (blending + kill discipline land in agents/tactical + observation). The
# committed sample bytes still record impostor_report_v4 and are re-recorded at
# 10.17, not here (recording-side only; replays/samples out of scope).
#
# Task 11.2 (2026-06-15; DESIGN.md §5.2; experiments/lab/report-vent-escape-lab.md)
# bumps accusation_round alone v7 -> v8: the impostor cover-consistency directive
# (commit to ONE sheltered room + tick-window away from the body and reuse it
# every turn) was stranded on the impostor_report body-report OPENING that
# impostors never take, so on the REPLY turn -- the only turn an impostor ever
# speaks -- its account drifted across turns (the residual self-pair alibi_conflict
# flags the vent fix cannot remove). The directive is ported verbatim into the
# accusation_round reply branch, gated on the new `is_impostor` bool; crewmate
# replies and opt-in turns are byte-unchanged. The committed sample bytes still
# record accusation_round.v7 and are re-recorded at 11.4, not here (recording-side
# only; replays/samples + the prompt-regression baseline out of scope).
#
# Task 13.6 (2026-06-21; report-phase-b-plan "Prompts"; the GATE FINDING in
# tasks/phase-13.md) bumps ALL FOUR together: the meeting templates were reworked so
# the crew STATE richer who/where/when sightings (the two-source material the
# inferential detector starved for -- R7 0/50 on the committed set). crewmate_report
# v7 -> v8 and accusation_round v8 -> v9 are REBUILT from a clean base (a focused
# sighting-elicitation section + the belief-mover framing, every load-bearing guard
# carried forward); impostor_report v5 -> v6 and vote_ballot/v5 -> v6 take the lighter
# trim + the belief-mover framing. The store.py directional movement breadcrumb feeds
# the same who/where/when material into the rendered memory. NO re-record here -- the
# committed sample bytes still record the v7/v5/v8/v5 set and are re-recorded at the
# Wave-B smoke re-record (13.10), not here (recording-side only; replays/samples + the
# prompt-regression baseline out of scope). think=False is preserved (13.9).
#
# Task 13.13 (DESIGN.md §4.6 + §5.5 reconciled; Probe 1) bumps vote_ballot ALONE,
# vote_ballot/v6 -> v7: the §4.6 decision-rule gate is DE-IMPERATIVED -- the
# pre-computed MUST-vote-to-eject / MUST-set-SKIP command becomes a non-directive
# evidence line (max suspicion + the 0.60 reference threshold as ONE input), and the
# emitted confidence is pinned IN PROSE (no code clamp) so a sub-threshold target
# cannot carry a >= threshold confidence. The deterministic tally floor
# (meetings.voting.tally_ballots) and the manager's guard_ballot_target_graph §4.6
# verdict are UNCHANGED -- the anti-cascade backstop is the tally, not the prompt. NO
# re-record here: the committed sample bytes still record vote_ballot/v5 (the 13.6 v6
# bump was never re-recorded either; the manifest pin reads v5 as-recorded) and are
# re-recorded at the held 13.12 combined re-record (recording-side only). The other
# three templates are byte-unchanged at this task.
DEFAULT_PROMPT_VERSIONS: Final[Mapping[str, str]] = {
    "crewmate_report": "crewmate_report.v8",
    "impostor_report": "impostor_report_v6",
    "accusation_round": "accusation_round.v9",
    "vote_ballot": "vote_ballot/v7",
}

# Per-model prompt-set version registry (Task 14.2; owner decision 2026-06-25 —
# per-model prompt sets; DESIGN.md §11.4 replay provenance). The frozen
# ``qwen3.5:9b`` reference set keeps the EXACT ``DEFAULT_PROMPT_VERSIONS``
# mapping above (same symbol, byte-identical keys/values) so the committed
# replays and the ``prompt_versions`` assertions in ``tests/orchestrator/`` and
# ``tests/scripts/`` stay green with ZERO re-record. A new-model set is
# distinguished by its OWN version strings plus the recorded model id -- NOT by
# prefixing or reformatting the 9B set's keys/values. New sets register
# themselves here (Task 14.5) keyed by the same ``AILIBI_PROMPT_SET`` selector
# the loader (:mod:`agents.strategic.prompts.loader`) resolves.
PROMPT_VERSION_SETS: Final[Mapping[str, Mapping[str, str]]] = {
    DEFAULT_PROMPT_SET: DEFAULT_PROMPT_VERSIONS,
}


def prompt_versions_for_set(
    prompt_set: str | None = None,
    *,
    env: Mapping[str, str] | None = None,
) -> Mapping[str, str]:
    """Return the recorded ``prompt_versions`` mapping for a prompt set.

    Resolves the active set via :func:`resolve_prompt_set` (the same
    ``AILIBI_PROMPT_SET`` selector the loader uses) and looks it up in
    :data:`PROMPT_VERSION_SETS`. An unregistered set raises :class:`ValueError`
    -- no silent fallback (AGENTS.md §"No silent fallbacks"). With the default
    (9B) set this returns :data:`DEFAULT_PROMPT_VERSIONS` byte-identically.
    """

    name = resolve_prompt_set(prompt_set, env=env)
    try:
        return PROMPT_VERSION_SETS[name]
    except KeyError as exc:
        known = ", ".join(sorted(PROMPT_VERSION_SETS))
        raise ValueError(
            f"Unknown prompt set {name!r}: no version registry entry "
            f"(known sets: {known})"
        ) from exc


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
    per entry so a defaulted turn is never lost from the replay.

    ``recovered_call_failures`` carries provider parse-failures the manager
    recovered on a SUCCEEDING turn (an earlier retry attempt raised before the
    recording client could log the call, then a later attempt parsed). The
    orchestrator records each so the burned spend stays visible even though the
    turn ultimately succeeded and carries no ``DefaultedCall``.

    Both default to ``()`` so a runner that produces neither -- the common
    case -- need not set them.
    """

    result: MeetingResult
    llm_calls: tuple[LLMCallRecord, ...]
    prompt_versions: Mapping[str, str]
    defaulted_calls: tuple[DefaultedCall, ...] = ()
    recovered_call_failures: tuple[LLMCallFailure, ...] = ()


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
        self,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str: ...

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]: ...


@runtime_checkable
class BeliefPersistingAgent(Protocol):
    """Agent that folds a meeting's evidence into persistent beliefs (Task 9.8).

    The post-meeting half of DESIGN.md §4.4 step 4 (rule-based, no LLM):
    after :func:`apply_meeting_result` the orchestrator calls this on every
    living agent so the meeting's accusation bump, Rule 3 corroboration,
    and Rule 5 decay land in the SAME stored :class:`BeliefState` the next
    meeting's :meth:`MeetingAwareAgent.suspicion_graph_for_meeting` reads --
    the persistence that lets suspicion accumulate across rounds instead of
    being rebuilt and discarded at vote time (audit gp-1 recall).

    Deliberately a separate, OPTIONAL capability rather than an extension
    of :class:`MeetingAwareAgent`: an agent without a persistent belief
    store (a scripted / packet-recording test agent whose suspicion graph
    is canned) has nothing to fold, exactly as ``ingest_packet(beliefs=None)``
    skips the belief rules for store-less runtimes. The production
    :class:`TacticalAgent` implements it; the across-meeting persistence of
    that path is pinned by integration test so a silent regression (the
    "inert accumulator" failure mode) cannot pass CI.
    """

    def absorb_meeting_evidence(
        self,
        *,
        accused: tuple[PlayerId, ...],
        corroborated: tuple[PlayerId, ...],
        contradicted: tuple[PlayerId, ...],
    ) -> None: ...


@runtime_checkable
class ReportedTestimonyAgent(Protocol):
    """Agent that folds a meeting's public testimony into memory as CONTENT (Task 13.5.2).

    The content twin of :class:`BeliefPersistingAgent`: where that capability
    folds a meeting into a scalar suspicion Δ, this one preserves the WHAT of
    public speech as ``provenance="reported"`` episodic rows and populates the
    alibi map (the 2026-06-25 memory diagnosis, workflow ``wg54kfoxy``: "social
    info is a scalar, not content"). A SEPARATE, OPTIONAL capability for the same
    reason :class:`BeliefPersistingAgent` is one -- a scripted / packet-recording
    test agent without a memory store has nothing to ingest -- and additive, so
    no existing agent must implement it. :func:`_absorb_meeting_beliefs` calls it
    per living agent only when :func:`testimony_as_content_enabled` is ON, so the
    flag-OFF path is byte-identical to today.
    """

    def absorb_reported_testimony(
        self,
        *,
        statements: tuple[ReportedStatement, ...],
    ) -> None: ...


@runtime_checkable
class MeetingPacingAgent(Protocol):
    """Agent that bookkeeps meeting-end pacing facts (Task 10.8).

    After every resolved meeting the orchestrator notifies each living
    agent of three PUBLIC facts -- when gameplay resumes (``end_tick``),
    the announced post-meeting dead roster (deaths and ejections are
    public at meetings, the same knowledge the Task 10.3 DEAD prompt line
    renders), and which player's emergency action opened the meeting
    (``None`` for a body report). The crewmate emergency trigger's
    :class:`~agents.tactical.crewmate_policy.EmergencyPacingTracker`
    consumes these for the global
    :data:`~agents.tactical.crewmate_policy.EMERGENCY_COOLDOWN_TICKS`
    cooldown, the one-call-per-game accounting (a call is spent only when
    a meeting actually OPENS from it -- engine truth, so a pre-empted
    intent does not burn the call), and the crossed-since-meeting reset.

    Optional capability like :class:`BeliefPersistingAgent`: a scripted /
    packet-recording test agent without pacing bookkeeping is skipped, and
    an impostor :class:`TacticalAgent` implements it as a no-op (impostors
    gain no button behavior until Wave 2 decides it).
    """

    def note_meeting_concluded(
        self,
        *,
        end_tick: int,
        dead_ids: tuple[PlayerId, ...],
        emergency_caller_id: PlayerId | None,
    ) -> None: ...


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
            unfreeze_memory=unfreeze_memory_enabled(),
        )
        # Dead / ejected roster (Task 10.3, audit gp-9): the orchestrator is
        # the only meeting-adjacent layer that may read world state, so it
        # derives the negative list here and the manager threads it into the
        # turn prompts as the explicit do-not-accuse line. "Who is dead" is
        # public knowledge (deaths and ejections are announced), so this
        # stays firewall-safe. Sorted for a deterministic render.
        dead_ids = tuple(
            sorted(
                player_id
                for player_id, player in state.players.items()
                if not player.alive
            )
        )
        try:
            result = await self._manager.run(
                meeting_id=meeting_id,
                trigger=trigger,
                participants=participants,
                dead_ids=dead_ids,
            )
        except BaseException as exc:
            # On failure, drop the partial captures so a retry against
            # the same runner does not double-count completed prefixes.
            self._recording_client.drain()
            # Carry the side-records that fired BEFORE the abort onto the
            # exception so the orchestrator can still persist them (audit gp-2:
            # a default must be visible -- and a recovered provider parse-failure
            # accounted -- even when a LATER call aborts the meeting, where
            # record_meeting and this success-path return never run).
            _attach_meeting_side_records(
                exc,
                _MeetingSideRecords(
                    defaulted_calls=self._manager.defaulted_calls,
                    recovered_call_failures=self._manager.recovered_call_failures,
                ),
            )
            raise
        return MeetingArtifacts(
            result=result,
            llm_calls=self._recording_client.drain(),
            prompt_versions=dict(self._prompt_versions),
            # Surface the manager's side-records (reset at the start of this
            # run): fired turn / ballot defaults (audit gp-2) and provider
            # parse-failures recovered on a succeeding turn, so both reach the
            # replay accurately.
            defaulted_calls=self._manager.defaulted_calls,
            recovered_call_failures=self._manager.recovered_call_failures,
        )


def build_default_meeting_runner(
    *,
    llm_client: LLMClient | None = None,
    budget: GameBudget | None = None,
    config: MeetingConfig | None = None,
    prompt_versions: Mapping[str, str] | None = None,
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

    # Provenance must match the rendered set (DESIGN.md §11.4). Resolve the
    # active set ONCE and bind both the renderers and the recorded
    # ``prompt_versions`` to it, so a runner never records one set's versions
    # while rendering another's templates -- the failure mode when the module's
    # import-time ``_ENV`` lags an in-process ``AILIBI_PROMPT_SET`` change (Task
    # 14.2; PR #203 review). With the default 9B set the renderers and versions
    # are byte-identical to pre-task HEAD, so committed replays + the version
    # assertions stay green with no re-record. An explicit ``prompt_versions``
    # mapping still wins (the caller pins its own provenance).
    active_prompt_set = resolve_prompt_set()
    renderers = build_prompt_renderers(active_prompt_set)
    resolved_versions = (
        prompt_versions
        if prompt_versions is not None
        else prompt_versions_for_set(active_prompt_set)
    )
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
        crewmate_report_prompt=renderers.crewmate_report,
        impostor_report_prompt=renderers.impostor_report,
        statement_prompt=renderers.statement,
        vote_prompt=renderers.vote,
        config=resolved_config,
        prompt_versions=resolved_versions,
        token_budget=token_budget,
    )


# Task 13.5.5 unfreeze-rendered-memory lever. Default OFF: every
# ``MeetingParticipant`` carries the one-time open-tick render (the frozen
# snapshot), byte-identical to pre-task HEAD, so the existing meeting suite and
# the committed replays are untouched. ON: the orchestrator attaches a ballot
# re-render hook so a voter's ballot renders its belief-line suspicion from the
# SAME pre-vote-folded suspicion the ``suspicion_graph`` kwarg carries --
# resolving the belief-line-vs-graph divergence (the PR #198 review
# inconsistency). Turn prompts keep the frozen render (they carry no
# ``suspicion_graph``). Mirrors
# ``meetings.transcript.witnessed_kill_evidence_enabled`` and
# ``agents.memory.store.testimony_as_content_enabled``.
ENV_UNFREEZE_MEMORY: Final[str] = "AILIBI_UNFREEZE_MEMORY"
_UNFREEZE_MEMORY_FLAG_TRUE: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)


def unfreeze_memory_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the Task 13.5.5 unfreeze-rendered-memory lever is ON.

    Reads :data:`ENV_UNFREEZE_MEMORY` from ``env`` (defaulting to the real
    process environment). Default OFF: an unset / empty / unrecognised value
    is ``False`` so the merge is the frozen open-tick render, byte-identical
    to pre-task HEAD. Accepts ``1/true/yes/on`` (case-insensitive). The
    ``env`` argument lets tests toggle the flag deterministically without
    mutating ``os.environ``.
    """

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_UNFREEZE_MEMORY, "").strip().lower()
        in _UNFREEZE_MEMORY_FLAG_TRUE
    )


def _memory_rerender_hook(
    agent: MeetingAwareAgent, *, token_budget: int
) -> Callable[[Mapping[PlayerId, float]], str]:
    """Build a participant's ballot re-render hook (Task 13.5.5).

    Returns a callable taking the per-voter ``suspicion_override`` (the
    pre-vote-folded suspicion the ballot's ``suspicion_graph`` carries) and
    re-rendering the agent's standing memory with that suspicion substituted
    into the belief lines, via ``render_memory_for_meeting`` ->
    :func:`agents.memory.store.render_for_prompt`. So the ballot's belief
    lines and its ``suspicion_graph`` kwarg read ONE folded suspicion source
    (the PR #198 review inconsistency, resolved by construction).

    Replay-deterministic: the override is a pure function of the recorded
    transcript + the agent's belief snapshot, and the renderer is itself
    deterministic (no wall-clock / RNG / set-order), so a replay rebuilds an
    identical ballot prompt. The renderer is CALLED, not edited beyond the
    additive ``suspicion_override`` parameter.
    """

    def _rerender(suspicion_override: Mapping[PlayerId, float]) -> str:
        return agent.render_memory_for_meeting(
            token_budget=token_budget, suspicion_override=suspicion_override
        )

    return _rerender


def _build_participants(
    *,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    token_budget: int,
    unfreeze_memory: bool = False,
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
        # Task 13.5.5: the open-tick render is ALWAYS produced (it is the
        # frozen value every TURN prompt reads, and the flag-OFF default for
        # the ballot too -- byte-identical to HEAD). With the flag ON we also
        # attach a re-render hook the manager calls ONLY for the ballot, with
        # the per-voter pre-vote-folded suspicion, so the ballot's belief lines
        # match the ``suspicion_graph`` it consumes.
        rerender_memory = (
            _memory_rerender_hook(agent, token_budget=token_budget)
            if unfreeze_memory
            else None
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
                rerender_memory=rerender_memory,
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
    resolved per the map's dead-crewmate-task rule (DESIGN.md §3.5;
    same semantics as a kill): dropped under the default ``drop`` and
    re-keyed to living crewmates under ``redistribute``.

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
        # Dead-crewmate task rule: DESIGN.md §3.5. Mirror
        # ``engine/tick.py::_apply_kill``: drop the ejected player's
        # incomplete tasks so the crew win check counts only alive-
        # owned tasks; completed tasks remain so they still count
        # toward ``crew_tasks_done``.
        surviving_tasks = {
            task_id: task
            for task_id, task in working.tasks.items()
            if not (task.owner == ejected_id and not task.completed)
        }
        # Under ``redistribute`` the dropped incomplete instances are re-keyed to
        # living crewmates instead of vanishing (DESIGN.md §3.5; map-flag-gated).
        # The default ``drop`` leaves ``surviving_tasks`` byte-identical.
        if game_map.dead_task_rule == "redistribute":
            tasks = redistribute_dead_tasks(
                surviving_tasks=surviving_tasks,
                pre_death_tasks=working.tasks,
                players=players,
                victim=ejected_id,
            )
        else:
            tasks = surviving_tasks
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
        trigger, triggering_body_id, trigger_kind = _build_meeting_trigger(
            state=state, events=events
        )
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
            # Persist the side-records that fired BEFORE this abort (audit
            # gp-2): record_meeting never runs for an aborted meeting, so
            # without this the earlier default / recovered failure would vanish.
            # The DefaultMeetingRunner attached them to the propagating exception.
            side_records = _extract_meeting_side_records(exc)
            _record_deadline_defaults(
                replay=replay,
                meeting_id=meeting_id,
                tick=trigger.trigger_tick,
                defaulted_calls=side_records.defaulted_calls,
            )
            _record_recovered_failures(
                replay=replay,
                meeting_id=meeting_id,
                tick=trigger.trigger_tick,
                failures=side_records.recovered_call_failures,
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
        # Task 10.11 self-check (audit-2026-06-13-1816 B-B-1): an EMERGENCY
        # meeting has NO kill scene by design (§5.2 PHASE 1) -- the caller
        # pressed the button on suspicion, no body was reported. The 10.8
        # check ("engine body_id is None") was TRUE yet MASKED a transcript
        # fabrication: every emergency opening re-narrated a stale corpse as a
        # fresh `found_body`. Fail loud on any emergency opening that still
        # carries one, so a model that ignores the v7 prompt is caught at the
        # source rather than silently anchoring votes on a non-existent body.
        _assert_no_emergency_opening_body(
            trigger_kind=trigger_kind, result=artifacts.result
        )
        replay.record_meeting(
            meeting_id=meeting_id,
            result=artifacts.result,
            llm_calls=artifacts.llm_calls,
            prompt_versions=artifacts.prompt_versions,
            state_hash_before=state_hash_before,
            state_hash_after=state_hash_after,
        )
        # Persist the meeting's side-records: a visible ``deadline_default``
        # marker per fired default (audit gp-2), and the recovered provider
        # parse-failures whose burned spend is absent from llm_calls.
        _record_deadline_defaults(
            replay=replay,
            meeting_id=meeting_id,
            tick=trigger.trigger_tick,
            defaulted_calls=artifacts.defaulted_calls,
        )
        _record_recovered_failures(
            replay=replay,
            meeting_id=meeting_id,
            tick=trigger.trigger_tick,
            failures=artifacts.recovered_call_failures,
        )
        # Post-meeting belief fold (Task 9.8, DESIGN.md §4.4 step 4; audit
        # gp-1 recall): write the meeting's public evidence into each living
        # agent's PERSISTENT belief state so suspicion accumulates across
        # meetings and decays between them. Runs AFTER apply_meeting_result
        # (the ejected player's beliefs are never read again) and OUTSIDE it
        # (the replay re-walk re-applies recorded results through that pure
        # function with no agents in hand -- engine bytes stay untouched).
        _absorb_meeting_beliefs(
            result=artifacts.result,
            state=next_state,
            agents=agents,
            trigger_kind=trigger_kind,
        )
        # Meeting-end pacing notification (Task 10.8). Runs AFTER the belief
        # fold so the emergency tracker's post-meeting over-gate baseline
        # samples the folded beliefs -- only a fresh below-to-above crossing
        # after this point re-arms the suspicion trigger.
        _notify_meeting_concluded(
            state=next_state,
            agents=agents,
            emergency_caller_id=(
                trigger.triggered_by if trigger_kind == "emergency" else None
            ),
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


@dataclass(frozen=True)
class _MeetingSideRecords:
    """Meeting side-records that must survive a meeting abort (audit gp-2).

    Bundles the two non-result outputs the orchestrator persists -- fired
    ``deadline_default`` markers and recovered provider parse-failures -- so a
    LATER aborting call (after which ``record_meeting`` never runs) does not
    lose them. Rides the propagating exception like ``llm.provider``'s
    parse-failure-on-exception pattern, which keeps the ``MeetingRunner``
    Protocol unchanged (a custom runner that does not attach simply yields an
    empty bundle here) and avoids module-level mutable state.
    """

    defaulted_calls: tuple[DefaultedCall, ...] = ()
    recovered_call_failures: tuple[LLMCallFailure, ...] = ()


_MEETING_SIDE_RECORDS_ATTR: Final[str] = "_ailibi_meeting_side_records"


def _attach_meeting_side_records(
    exc: BaseException, records: _MeetingSideRecords
) -> None:
    setattr(exc, _MEETING_SIDE_RECORDS_ATTR, records)


def _extract_meeting_side_records(exc: BaseException) -> _MeetingSideRecords:
    """Return the :class:`_MeetingSideRecords` carried by ``exc`` (empty if none)."""

    value = getattr(exc, _MEETING_SIDE_RECORDS_ATTR, None)
    return value if isinstance(value, _MeetingSideRecords) else _MeetingSideRecords()


def _record_recovered_failures(
    *,
    replay: ReplayLog,
    meeting_id: str,
    tick: int,
    failures: Sequence[LLMCallFailure],
) -> None:
    """Record provider parse-failures recovered on a succeeding turn (gp-2).

    A real provider validates internally and raises before the recording client
    can log the call, so a retry that fails once then parses would otherwise
    lose the failed attempt's spend (absent from ``llm_calls``, and a success
    carries no ``DefaultedCall``). Each is written into the existing failed-call
    channel with its REAL model / response / tokens / cost -- the same fields
    the meeting-abort path records for the aborting call, since both are genuine
    provider parse-failures -- so call count and cost stay accurate.
    """

    for failure in failures:
        replay.record_failed_call(
            meeting_id=meeting_id,
            tick=tick,
            model=failure.model,
            prompt_length=failure.prompt_length,
            raw_response=failure.raw_response,
            input_tokens=failure.input_tokens,
            output_tokens=failure.output_tokens,
            cost_usd=failure.cost_usd,
            error_type=failure.error_type,
            error_message=failure.error_message,
        )


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
    ``FailedCallReplayEntry.error_type`` is a free string. The defaulted phase
    and the trigger kind (deadline vs validation) are named in ``error_message``
    so the husk is auditable -- the headless recorder previously lost such turns
    with no record of any kind while telemetry reported ``failed_calls=0`` (true
    of the records, false of the run).

    Spend is preserved accurately. When a default carries ``parse_failures`` --
    a REAL provider validated internally and raised *before* the recording
    client could log the call, so that spend is absent from ``llm_calls`` -- one
    row is written per burned call with its real model / response / tokens /
    cost (the same per-call granularity ``llm_calls`` uses). Otherwise the row
    is a ZERO-spend visibility marker: a deadline miss completed nothing, and a
    manager-side validation of a returned-but-invalid payload already has its
    spend in ``llm_calls``, so charging it here too would double-count.

    De-dup (Task 9.10, audit gp-4): a deterministic provider regenerates the
    SAME failing response on the in-turn retry, so a single default can carry
    the same burned generation twice; :meth:`ReplayLog.record_failed_call`
    drops the byte-identical second row at the write chokepoint, so each
    distinct burned generation -- and each distinct zero-spend marker, whose
    ``error_message`` names its participant -- records exactly once.
    """

    for default in defaulted_calls:
        # The rendered §4.6 verdict max rides ONLY a defaulted vote (Task 10.12,
        # audit H-H-2): it is the sole telemetry that recovers a defaulted
        # ballot's MUST-vote / MUST-skip verdict, lost when the vote call failed
        # before the recording client logged its prompt. ``None`` for turns.
        if default.parse_failures:
            for failure in default.parse_failures:
                replay.record_failed_call(
                    meeting_id=meeting_id,
                    tick=tick,
                    model=failure.model,
                    prompt_length=failure.prompt_length,
                    raw_response=failure.raw_response,
                    input_tokens=failure.input_tokens,
                    output_tokens=failure.output_tokens,
                    cost_usd=failure.cost_usd,
                    error_type="deadline_default",
                    error_message=_deadline_default_message(default, failure),
                    rendered_vote_max=default.rendered_vote_max,
                )
            continue
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
            rendered_vote_max=default.rendered_vote_max,
        )


def _deadline_default_message(
    default: DefaultedCall, failure: LLMCallFailure | None = None
) -> str:
    """Human-readable ``error_message`` for a ``deadline_default`` record.

    Names the defaulted phase and the trigger kind (``deadline`` vs
    ``validation``) plus the participant who submitted nothing; the meeting id
    and tick ride the entry's own fields. When a provider ``failure`` is
    supplied its underlying error is appended so the husk's original cause is
    auditable alongside the preserved spend.
    """

    if default.phase == "vote":
        base = (
            f"vote defaulted ({default.trigger}); "
            f"{default.agent_id} submitted no ballot"
        )
    else:
        index = "" if default.turn_index is None else f" (turn {default.turn_index})"
        base = (
            f"{default.phase} turn{index} defaulted ({default.trigger}); "
            f"{default.agent_id} submitted no turn"
        )
    if failure is None:
        return base
    return f"{base} [{failure.error_type}: {failure.error_message}]"


def _absorb_meeting_beliefs(
    *,
    result: MeetingResult,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    trigger_kind: MeetingTriggerKind,
) -> None:
    """Fold a resolved meeting's evidence into living agents' beliefs (Task 9.8).

    The orchestrator-owned fan-out of the persistent post-meeting belief
    path: one :func:`meetings.manager.extract_belief_evidence` reduction,
    then one :meth:`BeliefPersistingAgent.absorb_meeting_evidence` per
    player still alive in the post-meeting ``state`` (a player alive after
    the meeting was necessarily a participant -- meetings only remove
    players). Iteration is sorted for determinism. The fold itself fires
    even when the meeting produced no evidence at all: an evidence-free
    round is exactly when §6.3 Rule 5 decays every unreinforced suspicion
    toward 0.5.

    Agents that do not implement the optional
    :class:`BeliefPersistingAgent` capability (scripted test agents with
    no belief store) are skipped -- see the protocol docstring for why
    that is a capability gate, not a silent fallback.

    Task 10.11 (audit-2026-06-13-1816 B-B-1): the engine-authoritative
    ``trigger_kind`` is threaded into the evidence reduction so the §6.3
    Rule-3 relevance gate treats an EMERGENCY meeting as having no kill
    scene -- a (fabricated) opening ``found_body`` can never widen the
    exclusion zone that the persisted corroborations / voices fold through.
    """

    evidence = extract_belief_evidence(result, trigger_kind=trigger_kind)
    # Task 13.5.2: the reported-testimony content fold rides the SAME
    # per-living-agent loop as the scalar belief fold, gated on the
    # ``AILIBI_TESTIMONY_AS_CONTENT`` flag (resolved once here, like
    # ``llm.provider`` resolves the provider). Flag OFF (the default) -> the
    # derivation never runs and no reported row is ingested, so the live game is
    # byte-identical to pre-task HEAD. The derivation is a pure function of the
    # recorded ``result``, identical to the replay loader's, so reconstruction
    # stays byte-identical.
    testimony_enabled = testimony_as_content_enabled()
    statements: tuple[ReportedStatement, ...] = (
        derive_reported_testimony(result) if testimony_enabled else ()
    )
    for player_id in sorted(state.players):
        if not state.players[player_id].alive:
            continue
        agent = agents.get(player_id)
        if isinstance(agent, BeliefPersistingAgent):
            agent.absorb_meeting_evidence(
                accused=evidence.accused,
                corroborated=evidence.corroborated,
                contradicted=evidence.contradicted,
            )
        # Reported content is ADDITIVE narrative, never a suspicion Δ -- it runs
        # AFTER the scalar fold (so the meeting-boundary marker is already
        # appended) and is wholly separate from it. NOT teammate-firewalled: the
        # capability ingests public speech faithfully (the scalar firewall above
        # is unchanged).
        if testimony_enabled and isinstance(agent, ReportedTestimonyAgent):
            agent.absorb_reported_testimony(statements=statements)


def _assert_no_emergency_opening_body(
    *,
    trigger_kind: MeetingTriggerKind,
    result: MeetingResult,
) -> None:
    """Fail loud if an emergency opening fabricates a body (Task 10.11).

    DESIGN.md §5.2 PHASE 1: an EMERGENCY meeting has no body -- the caller
    pressed the button on suspicion, no corpse was reported. The 10.8
    self-check ("engine ``body_id is None``") was true yet MASKED a
    transcript-level fabrication: on the close baseline every emergency
    opening re-narrated a real-but-stale corpse as a fresh ``found_body``
    (audit-2026-06-13-1816 B-B-1), and voters anchored ejections on it.
    This check looks at the OPENING TURN's observations, not the engine
    field, so a model that ignores the v7 prompt and still emits a
    ``found_body`` on an emergency opening is caught at the source instead
    of silently widening the §6.3 Rule-3 exclusion zone. Non-emergency
    meetings and empty transcripts are no-ops.
    """

    if trigger_kind != "emergency":
        return
    turns = result.transcript.turns
    if not turns:
        return
    fabricated = [
        observation
        for observation in turns[0].observations
        if isinstance(observation, FoundBodyObservation)
    ]
    if fabricated:
        bodies = ", ".join(
            f"{observation.body_of} in {observation.room}@t{observation.tick}"
            for observation in fabricated
        )
        raise RuntimeError(
            "Task 10.11 invariant violated: emergency meeting "
            f"{result.meeting_id!r} opening turn carries a fabricated "
            f"found_body observation ({bodies}). An emergency meeting reports "
            "no body (DESIGN.md §5.2 PHASE 1); the crewmate_report v7 emergency "
            "branch forbids a found_body observation."
        )


def _notify_meeting_concluded(
    *,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    emergency_caller_id: PlayerId | None,
) -> None:
    """Fan one concluded meeting's pacing facts out to living agents (10.8).

    The orchestrator-owned mirror of :func:`_absorb_meeting_beliefs` for the
    :class:`MeetingPacingAgent` capability: every player still alive in the
    post-meeting ``state`` learns the tick gameplay resumes at
    (``state.tick`` -- :func:`apply_meeting_result` already advanced it),
    the announced dead roster (sorted, post-ejection -- everyone at the
    table saw who is gone), and the meeting's emergency caller (``None``
    for a body report). All three are public knowledge at a meeting, so no
    engine-private state crosses the firewall. Iteration is sorted for
    determinism; agents without the capability are skipped (capability
    gate, not a silent fallback -- see :class:`MeetingPacingAgent`).
    """

    dead_ids = tuple(
        sorted(
            player_id for player_id, player in state.players.items() if not player.alive
        )
    )
    for player_id in sorted(state.players):
        if not state.players[player_id].alive:
            continue
        agent = agents.get(player_id)
        if isinstance(agent, MeetingPacingAgent):
            agent.note_meeting_concluded(
                end_tick=state.tick,
                dead_ids=dead_ids,
                emergency_caller_id=emergency_caller_id,
            )


def _build_meeting_trigger(
    *,
    state: WorldState,
    events: Sequence[EngineEvent],
) -> tuple[MeetingTrigger, BodyId | None, Literal["report", "emergency"]]:
    """Construct a :class:`MeetingTrigger` from the engine's transition events.

    The engine emits a :class:`MeetingTriggeredEvent` from
    :mod:`engine.tick._apply_report` / ``_apply_emergency`` whenever a
    valid ``ReportBody`` / ``EmergencyMeeting`` action drives the
    world into ``MEETING`` phase. The orchestrator pulls the most
    recent such event off the engine's emitted event list and renders
    it into the human-readable description the report prompt
    surfaces.

    The emergency description's "called an emergency meeting" phrase is
    load-bearing (Task 10.8): ``crewmate_report.j2`` v6 branches its
    emergency-opening frame on exactly that substring of the rendered
    ``meeting_trigger`` (the meeting layer threads no structured trigger
    kind to the prompt renderers, by design — the description IS the
    trigger surface). A wording change here must move in lockstep with
    the template branch; the strategic-prompt tests pin both ends.

    The second element of the returned tuple is the ``body_id`` of
    the corpse that triggered a ``report`` meeting (``None`` for an
    ``emergency`` meeting). :func:`apply_meeting_result` consumes
    that body so a hardcoded second report cannot re-trigger a meeting
    on the same corpse after gameplay resumes (defense in depth — the
    visibility layer already hides discovered bodies from default
    tactical agents, but the engine's ``resolve_report`` does not
    reject already-discovered bodies, so an adversarial / scripted
    intent could otherwise replay the trigger).

    The third element is the engine's trigger kind, consumed by the
    Task 10.8 post-meeting pacing notification (an ``emergency``
    meeting spends its caller's one emergency call per game).
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
            f"{trigger_event.actor} {EMERGENCY_TRIGGER_PHRASE} at tick "
            f"{trigger_event.tick}"
        )
    trigger = MeetingTrigger(
        triggered_by=trigger_event.actor,
        trigger_tick=trigger_event.tick,
        description=description,
    )
    return trigger, body_id, trigger_event.trigger


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
        # Emergency pacing bookkeeping (Task 10.8) exists only for a
        # crewmate running the crewmate FSM: the suspicion-accumulation
        # trigger is crew-only, and an impostor agent must carry NO button
        # bookkeeping at all (impostors gain no button behavior until
        # Wave 2 decides it -- this gate is what the no-impostor-emergency
        # pin asserts against).
        self._emergency_tracker: EmergencyPacingTracker | None = (
            EmergencyPacingTracker()
            if self._role == "CREWMATE" and isinstance(policy, CrewmatePolicy)
            else None
        )

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
        # Crewmate path (Task 10.8): sample the emergency tracker AFTER
        # perception (so this tick's §6.3 belief updates are visible) and
        # hand the policy the immutable eligibility snapshot. The sample is
        # idempotent for a given state, so repeated decide() calls stay
        # equal (the policy-determinism contract).
        if self._emergency_tracker is not None and isinstance(
            self._policy, CrewmatePolicy
        ):
            view = self._emergency_tracker.observe_tick(
                tick=packet.tick,
                memory=self._memory.episodic,
                beliefs=self._memory.beliefs,
                own_id=self._agent_id,
            )
            return self._policy.decide(
                self._memory.episodic, public_map, emergency=view
            )
        return self._policy.decide(self._memory.episodic, public_map)

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str:
        """Token-budgeted rendered memory view (DESIGN.md §6.6).

        ``suspicion_override`` (Task 13.5.5) is forwarded to
        :func:`render_for_prompt` so the meeting can render a ballot's
        belief-line suspicion from the pre-vote-folded numbers; ``None``
        (every non-ballot render) is byte-identical to pre-task HEAD.
        """

        return render_for_prompt(
            self._memory,
            token_budget=token_budget,
            suspicion_override=suspicion_override,
        )

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

    def absorb_meeting_evidence(
        self,
        *,
        accused: tuple[PlayerId, ...],
        corroborated: tuple[PlayerId, ...],
        contradicted: tuple[PlayerId, ...],
    ) -> None:
        """Fold one meeting's public evidence into stored beliefs (Task 9.8).

        Implements :class:`BeliefPersistingAgent` by delegating to the
        composite store (``agents.memory.store.absorb_meeting_evidence``),
        which mutates the SAME :class:`AgentMemory` belief state
        :meth:`suspicion_graph_for_meeting` snapshots -- so the bump a
        meeting writes here is what the next meeting's vote prompt sees.
        """

        absorb_meeting_evidence(
            self._memory,
            accused=accused,
            corroborated=corroborated,
            contradicted=contradicted,
        )

    def absorb_reported_testimony(
        self,
        *,
        statements: tuple[ReportedStatement, ...],
    ) -> None:
        """Fold one meeting's public testimony into memory as content (Task 13.5.2).

        Implements :class:`ReportedTestimonyAgent` by delegating to the composite
        store (``agents.memory.store.absorb_reported_testimony``), which appends
        ``provenance="reported"`` rows for OTHER speakers' structured claims and
        populates the alibi map on the SAME :class:`AgentMemory` the scalar fold
        and the meeting renderer read. Only invoked when the
        ``AILIBI_TESTIMONY_AS_CONTENT`` flag is ON.
        """

        absorb_reported_testimony(self._memory, statements=statements)

    def note_meeting_concluded(
        self,
        *,
        end_tick: int,
        dead_ids: tuple[PlayerId, ...],
        emergency_caller_id: PlayerId | None,
    ) -> None:
        """Fold one meeting's pacing facts into the emergency tracker (10.8).

        Implements :class:`MeetingPacingAgent`. A no-op for an impostor
        agent (no tracker -- impostors gain no button behavior). The
        orchestrator calls this AFTER :meth:`absorb_meeting_evidence`, so
        the tracker's post-meeting over-gate baseline reads the folded
        beliefs and only a fresh below-to-above crossing re-arms the
        suspicion trigger.
        """

        if self._emergency_tracker is None:
            return
        self._emergency_tracker.observe_meeting_end(
            end_tick=end_tick,
            announced_dead=dead_ids,
            was_own_emergency_call=emergency_caller_id == self._agent_id,
            memory=self._memory.episodic,
            beliefs=self._memory.beliefs,
            own_id=self._agent_id,
        )


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
    "BeliefPersistingAgent",
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
    "MeetingPacingAgent",
    "MeetingRunner",
    "Outcome",
    "PROMPT_VERSION_SETS",
    "ROSTER_PRESETS",
    "ReportedTestimonyAgent",
    "RosterPreset",
    "TacticalAgent",
    "apply_meeting_result",
    "build_default_agent_factory",
    "build_default_meeting_runner",
    "prompt_versions_for_set",
]
