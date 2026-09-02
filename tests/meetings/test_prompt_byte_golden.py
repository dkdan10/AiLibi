"""The prompt-byte golden (Task 16.3 (c); the C9 catch of the V&J audit).

This is the phase's OFF-path proof instrument. ``scripts/verify_samples.sh``
re-checks engine ``state_hash`` bytes only — it is belief- and prompt-BLIND, so
it cannot prove that Task 16.3's inert render-contract widening (persona +
suspicion_provenance kwargs, ``SuspicionEntry`` provenance fields,
``MeetingParticipant.persona``) left the rendered prompts unchanged. This golden
closes that gap: for every committed meeting of every committed replay in
``replays/samples/{9p2i,4p1i}`` it re-renders each recorded prompt from the
recorded inputs through the REAL production render path and asserts byte-equality
against ``llm_calls[].prompt``. Every later render lever in Phase 16 (16.5's
id-rendering, 16.15's provenance surface, 16.16's persona text) re-parametrizes
this same instrument, so its helpers are named for reuse, not for this task.

Architecture (the orchestrator's binding decision, GOLDEN-ARCH.md): the golden
re-runs each recorded meeting THROUGH THE REAL :class:`meetings.manager.
MeetingManager` rather than re-implementing the manager's per-turn prompt-input
assembly (transcript-so-far, contradictions-so-far, chain order, the 13.5.5
ballot memory re-render). Re-implementing that would be a second source of truth
and a dishonest golden; driving the real ``run()`` with a stub LLM client that
replays the recorded ``response_text`` strings exercises 100% of the production
render path and turns the recorded prompts into per-call byte assertions.

Reconstruction mirrors :meth:`api.replay_loader.ReplayLoader._walk` with
``collect_memory=True`` (the 15.3 walk): re-seed the engine from the game's
seed, re-apply the recorded action stream through
:func:`engine.tick.advance_tick`, verify every ``state_hash``, and maintain each
agent's :class:`agents.memory.store.AgentMemory` in lockstep through the SAME
observation → perception pipeline (:func:`agents.perception.ingest_packet`) plus
the post-meeting belief fold (:func:`orchestrator.game._absorb_meeting_beliefs`)
and the meeting-history fold
(:func:`orchestrator.replay.fold_meeting_outcome_into_memories`, the helper the
replay loader and the evidence-honesty walk share).
Real :class:`orchestrator.game.TacticalAgent` instances are carried so
participants are built VERBATIM by :func:`orchestrator.game._build_participants`
(rendered_memory via ``render_memory_for_meeting`` at
``token_budget=DEFAULT_TOKEN_BUDGET``, ``suspicion_graph_for_meeting``, the
``_memory_rerender_hook``, ``vent_witness_records_for_meeting``) and the meeting
trigger description — which is NOT recorded — is rebuilt by
:func:`orchestrator.game._build_meeting_trigger` and cross-checked against the
recorded ``triggered_by``.

The recorded-response stub (:class:`_RecordedResponseStub`) is keyed by the
EXACT prompt the manager passes to ``complete()`` — which is precisely the string
``orchestrator.game._RecordingLLMClient`` logged into ``llm_calls[].prompt`` — so
a lookup HIT is itself the per-call byte-equality proof. A lookup MISS
(``deadline_default`` turn/vote: every provider attempt failed schema validation
at record time, so no successful call was logged, verified below across all 100
committed files) returns an unparseable placeholder, forcing the manager down the
identical fail-soft default path it took at record time; because
:func:`meetings.manager._default_turn` is a fixed placeholder, a defaulted turn
reconstructs byte-identically and later prompts that embed it stay aligned. A
provider parse-failure that RECOVERED on a retry (its unparseable attempt raised
inside ``complete()`` before the recording client logged it, so it is absent from
``llm_calls`` — only the successful attempt, under the unchanged base prompt, was
logged) is transparently reproduced: the stub returns the successful response on
the manager's first attempt. A manager-side content retry (emergency-body strip /
positionless-opening feedback) logged BOTH the parsed-but-invalid attempt and the
feedback-augmented retry as successful calls, so both are in the stub's dict and
the feedback path replays exactly.

Coverage (GOLDEN-ARCH.md §3): the four template kinds are ``crewmate_report`` /
``impostor_report`` (the opening, split by opener role) and ``accusation_round``
(reply + opt_in) / ``vote_ballot``. In the committed sets EVERY meeting opener is
a CREWMATE (0 of 199 openers is an impostor — the FSM impostor presses no button;
DESIGN.md §12, AGENTS.md), so ``impostor_report`` has NO committed coverage. The
per-set counters therefore assert every kind that OCCURS in the recorded data was
reproduced (a kind silently skipped fails the gate), and
:func:`test_impostor_report_opening_kind_is_exercised` drives an
impostor-opener meeting through the same manager seam so the fourth kind is not a
blind spot. The one-byte template perturbation leg
(:func:`test_one_byte_template_perturbation_breaks_the_golden`) proves the gate
can fail — a golden that cannot fail is not a gate.

The archive seam (Task 16.15, the bump-in-flight instrument): when a committed
set stamps a prompt-set the live :data:`PROMPT_VERSION_SETS` has advanced past,
its recorded stamps resolve instead through
:data:`ARCHIVED_PROMPT_VERSION_SETS` — byte-copies of the recorded template
bodies under ``tests/fixtures/prompt_archive/`` — so the walk renders each
recorded meeting through the templates its own stamps name and every byte
assertion keeps its meaning across the window.

The window is CLOSED: the baseline-8 record wrote all 300 committed games at
``*.qwen3_6_27b.v5``, which is what the live registry serves, so every recorded
meeting resolves through the LIVE bodies and the archive is EMPTY. That is the
healthy state — an archive holds bytes only while a committed set names a
prompt-set the registry has moved past. The seam itself stays for the next bump,
and an archived set is pinned on BOTH halves of what it rendered: the template
bytes (``root=_ARCHIVE_ROOT``) and the render inputs that moved with it
(:data:`ARCHIVED_MAP_CARDS` — the v4→v5 bump rewrote the map card's row format,
which archived ``.j2`` bytes alone would not have reproduced).
"""

from __future__ import annotations

import asyncio
import difflib
import shutil
from collections.abc import Iterator, Mapping, Sequence
from itertools import combinations
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
from pydantic import BaseModel

from agents.memory.beliefs import (
    SUSPICION_PROVENANCE_ATOL,
    SuspicionProvenance,
    hard_evidence_gated_suspicion,
)
from agents.memory.store import DEFAULT_TOKEN_BUDGET
from agents.perception import ingest_packet
from agents.strategic.prompts.loader import (
    _PROMPTS_ROOT,
    PromptRenderers,
    build_prompt_renderers,
)
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from api.replay_loader import (
    _deserialize_actions,
    _game_id_for_seed,
    _infer_num_players,
    _load_roster_config,
)
from engine.entities import PlayerId, Role
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.manager import (
    EMERGENCY_TRIGGER_PHRASE,
    MeetingConfig,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    SuspicionEntry,
)
from meetings.render_contract import ReporterContext
from meetings.schemas import MeetingResult, MeetingTranscript
from meetings.transcript import MeetingTriggerKind
from observation.service import ObservationService
from orchestrator.game import (
    DEFAULT_NUM_IMPOSTORS,
    HEADLESS_MEETING_DEADLINES,
    PROMPT_VERSION_SETS,
    TacticalAgent,
    _absorb_meeting_beliefs,
    _build_meeting_trigger,
    _build_participants,
    _PROMPT_VERSION_OVERLAYS,
    apply_meeting_result,
    prompt_versions_for_set,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    env_var_for_lever,
    fold_meeting_outcome_into_memories,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

# --------------------------------------------------------------------------- #
# Committed-sample paths + the four template kinds                            #
# --------------------------------------------------------------------------- #

_REPO_ROOT: Path = Path(__file__).resolve().parents[2]
_SAMPLE_SETS: tuple[Path, ...] = (
    _REPO_ROOT / "replays" / "samples" / "9p2i",
    _REPO_ROOT / "replays" / "samples" / "4p1i",
)

# Task 16.15: recorded-stamp registry for committed sets that predate a
# prompt-set bump. Keyed like PROMPT_VERSION_SETS, but each key names a
# directory of ARCHIVED template bytes under tests/fixtures/prompt_archive/ —
# the exact bodies the committed recordings rendered through. The walk
# resolves a recorded ``prompt_versions`` mapping against the live registry
# first and this archive second, so the byte golden stays a real gate across
# a bump-in-flight window. Retire an entry when no committed set stamps it any
# longer (the adopting re-record).
#
# EMPTY at this HEAD, and that is the healthy state: the baseline-8 record wrote
# every committed set at ``*.qwen3_6_27b.v5``, which the live registry serves, so
# all 672 recorded meetings resolve through the LIVE bodies alone and the archive
# has nothing to hold. The v4 entry and its six fixture bodies retired with that
# record. The mechanism stays for the next bump-in-flight window.
_ARCHIVE_ROOT: Path = _REPO_ROOT / "tests" / "fixtures" / "prompt_archive"
ARCHIVED_PROMPT_VERSION_SETS: Mapping[str, Mapping[str, str]] = {}

# The ``<map>`` card an archived set rendered through. A card is a RENDER INPUT,
# not a template, so archived ``.j2`` bytes alone do not reproduce a prompt once
# the card's own format moves — which is why an archive entry pairs each recorded
# stamp with BOTH halves. Empty alongside the registry above.
ARCHIVED_MAP_CARDS: Mapping[str, str] = {}

# The four render kinds, labelled by the manager seam that emits each. The
# opening is split crewmate/impostor (both are ``ReportPromptRenderer``s); the
# reply + opt_in turns share the one ``accusation_round`` statement renderer.
_KIND_CREWMATE_REPORT = "crewmate_report"
_KIND_IMPOSTOR_REPORT = "impostor_report"
_KIND_ACCUSATION_ROUND = "accusation_round"
_KIND_VOTE_BALLOT = "vote_ballot"
_ALL_KINDS: tuple[str, ...] = (
    _KIND_CREWMATE_REPORT,
    _KIND_IMPOSTOR_REPORT,
    _KIND_ACCUSATION_ROUND,
    _KIND_VOTE_BALLOT,
)

# The unparseable placeholder the stub returns on a lookup miss. It fails both
# ``MeetingTurn`` and ``VoteBallot`` JSON validation, forcing the manager's
# fail-soft default exactly as a record-time ``deadline_default`` did (the miss
# is a turn/vote whose every provider attempt failed validation, so no
# successful call was ever logged into ``llm_calls`` — see the module-level
# no-successful-call-for-a-default invariant, pinned by
# ``test_defaults_are_the_only_lookup_misses``).
_FORCE_DEFAULT_RESPONSE = "<<golden: force manager-side default (not JSON)>>"


# --------------------------------------------------------------------------- #
# Reusable reconstruction DTOs (16.5 / 16.15 / 16.16 re-parametrize these)     #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _Render:
    """One renderer invocation captured off the real manager seam.

    ``prompt`` is the base template render the renderer returned; the string the
    manager finally passes to ``complete()`` may append manager-side retry
    feedback (Task 10.6) to it, so ``prompt`` is the base for kind attribution,
    not necessarily the recorded ``llm_calls[].prompt`` byte-for-byte.
    """

    kind: str
    agent_id: PlayerId | None
    prompt: str
    # Task 16.3 (c): the ``suspicion_provenance`` rows the manager threaded into
    # this render. On the ballot seam these are the post-fold rows (the same
    # object as ``suspicion_graph``), so the live-population provenance assertions
    # can read the folded ballot-time decomposition straight off the render sink.
    suspicion_provenance: tuple[SuspicionEntry, ...] = ()


@dataclass(frozen=True)
class _CompleteCall:
    """One ``complete()`` call the manager made, as the stub observed it.

    ``hit`` is ``True`` when ``prompt`` matched a recorded ``llm_calls[].prompt``
    exactly — i.e. this call is a per-call byte-equality proof for that recorded
    call. A miss is a manager-side default (verified to be the only miss cause).
    """

    prompt: str
    agent_id: PlayerId | None
    hit: bool


@dataclass(frozen=True)
class ReconstructedMeeting:
    """One committed meeting re-run through the real manager (reuse surface).

    Carries everything a byte assertion or a downstream render-lever test needs:
    the recorded ``entry``, the manager's reconstructed ``result`` (its
    transcript / ballots / outcome cross-check the recording), every renderer
    ``render`` in order (for kind attribution + drift diffs), and the set of
    recorded prompts the manager reproduced byte-for-byte (``hit_prompts``).
    """

    seed: int
    set_name: str
    meeting_index: int
    meeting_id: str
    entry: MeetingReplayEntry
    result: MeetingResult
    renders: tuple[_Render, ...]
    complete_calls: tuple[_CompleteCall, ...]
    hit_prompts: frozenset[str]
    # Task 16.3 (c): the participants built VERBATIM by ``_build_participants``.
    # Each carries the live suspicion_graph (with the game builder's provenance
    # fields) the live-population assertions decompose.
    participants: tuple[MeetingParticipant, ...] = ()
    # Task 16.8: the reconstructed trigger's kind ("report" / "emergency"), from
    # the same ``_build_meeting_trigger`` rebuild the walk drives the manager
    # with. A downstream re-derivation needs it to mirror the manager's
    # emergency-reporter predicate (``reporter=None`` for an emergency meeting
    # -- the recorded ``MeetingReplayEntry`` carries no trigger description, so
    # this is the only faithful channel). ``None`` = a direct construction that
    # never threaded it.
    trigger_kind: MeetingTriggerKind | None = None


@dataclass(frozen=True)
class RerenderedPrompt:
    """One recorded LLM call paired with its production re-render.

    ``reproduced`` is the byte-equality verdict for this recorded call:
    ``rerendered_prompt == recorded_prompt`` when the manager passed the exact
    recorded bytes to ``complete()``. On a drift ``rerendered_prompt`` is the
    manager's nearest actual complete-prompt (same speaker) so a caller can emit
    a readable unified diff. Downstream Phase-16 render-lever tests iterate these
    and assert ``reproduced`` under their widened templates.
    """

    seed: int
    set_name: str
    meeting_index: int
    meeting_id: str
    kind: str
    agent_id: PlayerId | None
    recorded_prompt: str
    rerendered_prompt: str
    reproduced: bool


# --------------------------------------------------------------------------- #
# The recorded-response stub + the kind-tagging renderer wrapper              #
# --------------------------------------------------------------------------- #


@dataclass
class _RecordedResponseStub:
    """Stub :class:`llm.client.LLMClient` replaying recorded meeting responses.

    Keyed by the EXACT prompt the manager passes to ``complete()`` — the same
    bytes ``_RecordingLLMClient`` logged as ``llm_calls[].prompt`` — so a HIT is
    the per-call byte-equality proof and a MISS (a record-time
    ``deadline_default`` whose every attempt failed validation, so nothing was
    logged) returns the unparseable placeholder that drives the manager's
    identical fail-soft default. Records every call so the walk can assert every
    recorded prompt was consumed and diff a drift against the nearest miss.
    """

    responses: Mapping[str, LLMResponse]
    calls: list[_CompleteCall] = field(default_factory=list)

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        recorded = self.responses.get(prompt)
        self.calls.append(
            _CompleteCall(prompt=prompt, agent_id=agent_id, hit=recorded is not None)
        )
        if recorded is not None:
            return recorded
        return LLMResponse(
            text=_FORCE_DEFAULT_RESPONSE,
            usage=TokenUsage(input_tokens=0, output_tokens=0),
            cost_usd=0.0,
            model="golden-force-default",
        )


class _KindTaggingRenderer:
    """Wrap a real prompt renderer, tagging each render with its template kind.

    The manager holds four renderer callables; this wrapper records the kind +
    speaker + returned prompt of every invocation, then delegates to the real
    renderer so the manager sees byte-identical output. ``**kwargs`` (not the
    frozen current signature) keeps the wrapper valid as Task 16.3 (b)/(c) and
    the later render levers widen the renderer Protocols with new defaulted
    kwargs — the manager must be able to thread ``persona`` /
    ``suspicion_provenance`` through this wrapper unchanged.
    """

    def __init__(self, kind: str, inner: Any, renders: list[_Render]) -> None:
        self._kind = kind
        self._inner = inner
        self._renders = renders

    def __call__(self, **kwargs: Any) -> str:
        prompt: str = self._inner(**kwargs)
        agent_id = kwargs.get("agent_id")
        if agent_id is None:
            agent_id = kwargs.get("voter_id")
        self._renders.append(
            _Render(
                kind=self._kind,
                agent_id=agent_id,
                prompt=prompt,
                # Task 16.3 (c): capture the inert provenance rows the manager
                # threaded (post-fold rows on the ballot seam; the frozen graph
                # on the turn seams). Default ``()`` before the widening lands.
                suspicion_provenance=tuple(kwargs.get("suspicion_provenance", ())),
            )
        )
        return prompt


def _tagging_manager(
    *,
    stub: _RecordedResponseStub,
    renderers: PromptRenderers,
    renders: list[_Render],
) -> MeetingManager:
    """Build a real :class:`MeetingManager` wired exactly as the recording did.

    The recording path (:func:`orchestrator.game.build_default_meeting_runner`)
    runs deadline-free (:data:`orchestrator.game.HEADLESS_MEETING_DEADLINES`)
    with an otherwise-default :class:`meetings.manager.MeetingConfig`, so the
    ``skip_confidence_threshold`` and token budgets that reach the vote prompt
    match the recorded run. The four renderers are the kind-tagging wrappers
    around the set's real Jinja callables.
    """

    return MeetingManager(
        llm_client=stub,
        crewmate_report_prompt=_KindTaggingRenderer(
            _KIND_CREWMATE_REPORT, renderers.crewmate_report, renders
        ),
        impostor_report_prompt=_KindTaggingRenderer(
            _KIND_IMPOSTOR_REPORT, renderers.impostor_report, renders
        ),
        statement_prompt=_KindTaggingRenderer(
            _KIND_ACCUSATION_ROUND, renderers.statement, renders
        ),
        vote_prompt=_KindTaggingRenderer(_KIND_VOTE_BALLOT, renderers.vote, renders),
        config=MeetingConfig(deadlines=HEADLESS_MEETING_DEADLINES),
    )


# --------------------------------------------------------------------------- #
# Set resolution + the reconstruction walk                                    #
# --------------------------------------------------------------------------- #


def resolve_prompt_set(prompt_versions: Mapping[str, str]) -> str:
    """Reverse-look the recorded ``prompt_versions`` up in the set registries.

    :data:`orchestrator.game.PROMPT_VERSION_SETS` maps each prompt-set name to
    its ``prompt_versions`` mapping; the recording stamped the mapping, not the
    name, so the golden recovers the name by an exact reverse lookup (no
    hardcoded set name) and pairs :func:`build_prompt_renderers` with the SAME
    resolved set — the recording-provenance invariant
    ``build_default_meeting_runner`` guarantees (DESIGN.md §11.4). A recorded
    stamp a later bump moved the live registry past resolves through
    :data:`ARCHIVED_PROMPT_VERSION_SETS` instead (Task 16.15 — the archived
    bodies are what those recordings rendered). A recording made with substrate
    levers ON stamps those arms' version strings instead, so it resolves through
    the ON-ARM index (:func:`_overlay_stamp_index`). Fail loud unless exactly one
    set matches across all three.
    """

    wanted = dict(prompt_versions)
    matches = [
        name
        for registry in (PROMPT_VERSION_SETS, ARCHIVED_PROMPT_VERSION_SETS)
        for name, versions in registry.items()
        if dict(versions) == wanted
    ]
    # The ON-arm index is consulted only when the registries above hold nothing.
    # An arm stamp can never equal a default one (the invariant below pins it),
    # so this cannot hide an ambiguity -- and it keeps the enumeration off the
    # path every lever-OFF recording takes.
    if not matches:
        matches = list(_overlay_stamp_owners(wanted))
    if len(matches) != 1:
        raise AssertionError(
            f"recorded prompt_versions {wanted} matched {len(matches)} registered "
            f"sets ({matches}); expected exactly one"
        )
    return matches[0]


def _stamp_key(versions: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    """A recorded ``prompt_versions`` mapping as an order-free lookup key."""

    return tuple(sorted(versions.items()))


def _overlay_stamp_owners(wanted: Mapping[str, str]) -> tuple[str, ...]:
    """The sets whose ON-ARM stamp for some lever slate equals ``wanted``.

    A lever with a version overlay moves provenance with the bytes it re-bodies,
    so a recording made under one stamps that arm's version strings and a
    multi-lever slate stamps a per-template composite of them
    (:func:`orchestrator.game.prompt_versions_for_set`). None of those mappings
    is a value in the default registry -- that separation is the point, and
    ``test_a_lever_on_recording_can_never_wear_a_default_stamp`` pins it -- so
    without this lookup a lever-ON recording reverse-looks up to NO set and
    cannot be reconstructed at all, which is the state the Wave-2 record's own
    bytes would otherwise be in.

    Enumerated over every SUBSET of the live overlay keys rather than the all-ON
    slate alone, so a half-exported or single-lever recording resolves and is
    named rather than silently unmatched. A set with no body for an arm raises
    from the resolver and is skipped for that subset only: it cannot have
    stamped an arm it cannot render, and its no-arm stamp is already covered by
    the default registry.

    Recomputed per call rather than cached: the registries it reads are this
    build's, and a memoised copy would answer from an earlier process state
    after a test replaced one. It costs a fraction of a millisecond and only
    runs for a stamp the default registries could not place.
    """

    wanted_key = _stamp_key(wanted)
    owners: list[str] = []
    for name in PROMPT_VERSION_SETS:
        for size in range(1, len(_OVERLAY_KEYS) + 1):
            if name in owners:
                break
            for subset in combinations(_OVERLAY_KEYS, size):
                env = {env_var_for_lever(key): "1" for key in subset}
                try:
                    versions = prompt_versions_for_set(name, env=env)
                except ValueError:
                    continue
                if _stamp_key(versions) == wanted_key:
                    owners.append(name)
                    break
    return tuple(owners)


def _roster_for(
    replay_dir: Path, replay_entries: Sequence[ReplayEntry]
) -> tuple[int, int, int]:
    """Resolve ``(num_players, num_impostors, tasks_per_crewmate)`` per ``_walk``.

    A set with a ``roster.json`` (the 9p2i preset) re-seeds from it; the flat
    4p1i baseline has none, so it defaults exactly as
    :meth:`api.replay_loader.ReplayLoader._walk` does — infer ``num_players``
    from the action stream, pin ``num_impostors`` to the MVP invariant, and
    default one task per crewmate. A wrong resolution cannot corrupt the golden:
    the per-tick ``state_hash`` check fails loud.
    """

    roster = _load_roster_config(replay_dir)
    if roster is None:
        return _infer_num_players(replay_entries), DEFAULT_NUM_IMPOSTORS, 1
    return roster.num_players, roster.num_impostors, roster.tasks_per_crewmate


def _build_agents(state: WorldState) -> dict[PlayerId, TacticalAgent]:
    """One real :class:`TacticalAgent` per seeded player.

    The default agent factory's construction (:func:`orchestrator.game.
    build_default_agent_factory`) — a role-appropriate policy plus a fresh
    :class:`agents.memory.store.AgentMemory`. The tactical policy is never
    exercised here (the walk applies the RECORDED actions, not policy output);
    memory is reconstructed by feeding the observation pipeline directly, the
    same episodic/belief writes ``TacticalAgent.decide`` makes. Real agents let
    ``_build_participants`` and ``_absorb_meeting_beliefs`` run VERBATIM.
    """

    agents: dict[PlayerId, TacticalAgent] = {}
    for player_id in sorted(state.players):
        role: Role = state.players[player_id].role
        policy: CrewmatePolicy | ImpostorPolicy = (
            ImpostorPolicy(agent_id=player_id)
            if role == "IMPOSTOR"
            else CrewmatePolicy(agent_id=player_id)
        )
        agents[player_id] = TacticalAgent(
            agent_id=player_id, policy=policy, role=role, memory=None
        )
    return agents


def _ingest_tick(
    service: ObservationService,
    agents: Mapping[PlayerId, TacticalAgent],
    state: WorldState,
    last_events: Sequence[Any],
) -> None:
    """Re-run perception for every alive agent (mirrors ``_walk._ingest_tick``).

    A packet built from the pre-tick world state and the previous tick's events
    is ingested into each living agent's episodic + belief stores — the exact
    memory side effect :meth:`orchestrator.game.TacticalAgent.decide` produces,
    so the reconstructed memory the meeting renders from is identical to the
    live run's.
    """

    for player_id in sorted(state.players):
        if not state.players[player_id].alive:
            continue
        packet = service.build_packet(
            world_state=state, agent_id=player_id, engine_events=last_events
        )
        ingest_packet(
            packet=packet,
            memory=agents[player_id].memory.episodic,
            beliefs=agents[player_id].memory.beliefs,
        )


def walk_replay_meetings(
    replay_path: Path,
    *,
    game_map: Map,
    renderers_for_set: Mapping[str, PromptRenderers],
) -> Iterator[ReconstructedMeeting]:
    """Re-seed, re-walk, and re-run every committed meeting of one replay.

    Mirrors :meth:`api.replay_loader.ReplayLoader._walk` (``collect_memory``)
    plus the recorded render inputs: re-apply the recorded actions through
    :func:`advance_tick` verifying every ``state_hash``, maintain each agent's
    memory in lockstep, and at each :class:`MeetingReplayEntry` drive the REAL
    :class:`MeetingManager` with a recorded-response stub, yielding a
    :class:`ReconstructedMeeting`. After each meeting the recorded result is
    applied (:func:`apply_meeting_result`, its ``state_hash_after`` verified) and
    folded into living agents' beliefs (:func:`_absorb_meeting_beliefs`) and
    their meeting history (:func:`fold_meeting_outcome_into_memories`) so the
    NEXT meeting renders from the same accumulated/decayed suspicion and the same
    announced outcomes the live agents held. ``renderers_for_set`` lets a caller
    inject a perturbed template
    root (the perturbation leg).
    """

    seed = _seed_from_path(replay_path)
    game_id = _game_id_for_seed(seed)
    entries = read_all_entries(replay_path)
    replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
    meeting_by_tick = {e.tick: e for e in entries if isinstance(e, MeetingReplayEntry)}
    num_players, num_impostors, tasks_per_crewmate = _roster_for(
        replay_path.parent, replay_entries
    )
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    agents = _build_agents(state)

    with TemporaryDirectory(prefix="ailibi-golden-audit-") as audit_dir:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit_dir) / "audit.jsonl"
        )
        last_events: tuple[Any, ...] = ()
        meeting_index = 0
        for entry in replay_entries:
            _ingest_tick(service, agents, state, last_events)
            actions = _deserialize_actions(entry.actions)
            state, events = advance_tick(state, actions, game_map=game_map)
            actual = _state_hash(state)
            if actual != entry.state_hash:
                raise AssertionError(
                    f"{game_id} tick {entry.tick}: reconstructed state_hash "
                    f"{actual!r} != recorded {entry.state_hash!r}"
                )
            if state.phase != "MEETING":
                if state.phase == "GAME_OVER":
                    break
                last_events = tuple(events)
                continue

            meeting_entry = meeting_by_tick.get(entry.tick)
            if meeting_entry is None:
                # Partial replay: a meeting opened but never resolved. Stop the
                # walk exactly as ``_walk`` does (the two must stay consistent).
                break

            reconstructed, result, body_id, trigger_kind = _run_recorded_meeting(
                meeting_entry=meeting_entry,
                seed=seed,
                meeting_index=meeting_index,
                state=state,
                events=events,
                agents=agents,
                renderers_for_set=renderers_for_set,
            )
            yield reconstructed

            next_state, post_events = apply_meeting_result(
                state, result, game_map=game_map, triggering_body_id=body_id
            )
            after = _state_hash(next_state)
            if after != meeting_entry.state_hash_after:
                raise AssertionError(
                    f"{meeting_entry.meeting_id}: reconstructed state_hash_after "
                    f"{after!r} != recorded {meeting_entry.state_hash_after!r}"
                )
            _absorb_meeting_beliefs(
                result=result,
                state=next_state,
                agents=agents,
                trigger_kind=trigger_kind,
            )
            # Then the meeting-history fold, in the live loop's order
            # (``_notify_meeting_concluded`` runs after the belief fold), through
            # the same shared helper the replay loader and the evidence-honesty
            # walk call — so the mirrors cannot drift. Inert to every rendered
            # byte while the ``meeting_outcome_memory`` lever is OFF, which is
            # the state every committed recording was made in.
            fold_meeting_outcome_into_memories(
                result,
                state=next_state,
                memories={pid: agent.memory for pid, agent in agents.items()},
            )
            state = next_state
            meeting_index += 1
            if state.phase == "GAME_OVER":
                break
            last_events = tuple(events) + tuple(post_events)


def _run_recorded_meeting(
    *,
    meeting_entry: MeetingReplayEntry,
    seed: int,
    meeting_index: int,
    state: WorldState,
    events: Sequence[Any],
    agents: Mapping[PlayerId, TacticalAgent],
    renderers_for_set: Mapping[str, PromptRenderers],
) -> tuple[ReconstructedMeeting, MeetingResult, str | None, Any]:
    """Drive one recorded meeting through the real manager + stub client."""

    set_name = resolve_prompt_set(meeting_entry.prompt_versions)
    renderers = renderers_for_set[set_name]
    responses = {
        call.prompt: LLMResponse(
            text=call.response_text,
            usage=TokenUsage(
                input_tokens=call.input_tokens, output_tokens=call.output_tokens
            ),
            cost_usd=call.cost_usd,
            model=call.model,
        )
        for call in meeting_entry.llm_calls
    }
    trigger, body_id, trigger_kind = _build_meeting_trigger(state=state, events=events)
    if trigger.triggered_by != meeting_entry.triggered_by:
        raise AssertionError(
            f"{meeting_entry.meeting_id}: rebuilt trigger opener "
            f"{trigger.triggered_by!r} != recorded {meeting_entry.triggered_by!r}"
        )
    participants = _build_participants(
        state=state, agents=agents, token_budget=DEFAULT_TOKEN_BUDGET
    )
    dead_ids = tuple(
        sorted(pid for pid, player in state.players.items() if not player.alive)
    )
    renders: list[_Render] = []
    stub = _RecordedResponseStub(responses=responses)
    manager = _tagging_manager(stub=stub, renderers=renderers, renders=renders)
    result = asyncio.run(
        manager.run(
            meeting_id=meeting_entry.meeting_id,
            trigger=trigger,
            participants=participants,
            dead_ids=dead_ids,
            # The SEEDED impostor count, derived exactly as the live loop derives
            # it (orchestrator.game._run_meeting): render-only, and the persona
            # sentence's number agreement rides on it, so omitting it renders a
            # 9p2i meeting in 4p1i wording and every prompt lookup misses.
            impostor_count=sum(
                1 for player in state.players.values() if player.role == "IMPOSTOR"
            ),
        )
    )
    hit_prompts = frozenset(call.prompt for call in stub.calls if call.hit)
    reconstructed = ReconstructedMeeting(
        seed=seed,
        set_name=set_name,
        meeting_index=meeting_index,
        meeting_id=meeting_entry.meeting_id,
        entry=meeting_entry,
        result=result,
        renders=tuple(renders),
        complete_calls=tuple(stub.calls),
        hit_prompts=hit_prompts,
        participants=tuple(participants),
        trigger_kind=trigger_kind,
    )
    return reconstructed, result, body_id, trigger_kind


# --------------------------------------------------------------------------- #
# Kind attribution + per-call re-render pairing                               #
# --------------------------------------------------------------------------- #


def _classify_recorded_prompt(
    recorded_prompt: str, renders: Sequence[_Render]
) -> _Render | None:
    """Attribute a recorded prompt to the render that produced it.

    An exact match is the common case; a manager-side retry appends feedback to
    the base render (Task 10.6), so a recorded prompt that is a base render plus
    a suffix is attributed to the longest such base. Returns ``None`` only when
    the manager never rendered a matching base — a drift the caller reports.
    """

    exact = {render.prompt: render for render in renders}
    hit = exact.get(recorded_prompt)
    if hit is not None:
        return hit
    prefixed = [r for r in renders if recorded_prompt.startswith(r.prompt)]
    if prefixed:
        return max(prefixed, key=lambda r: len(r.prompt))
    return None


def rerendered_prompts(
    meeting: ReconstructedMeeting,
) -> Iterator[RerenderedPrompt]:
    """Yield one :class:`RerenderedPrompt` per recorded LLM call (reuse surface).

    Pairs each recorded ``llm_calls[i].prompt`` with the manager's reproduction:
    ``reproduced`` is ``True`` iff the manager passed those exact bytes to
    ``complete()``. On a drift the nearest same-speaker complete-prompt is
    attached so the caller can emit a unified diff.
    """

    for call in meeting.entry.llm_calls:
        reproduced = call.prompt in meeting.hit_prompts
        render = _classify_recorded_prompt(call.prompt, meeting.renders)
        kind = render.kind if render is not None else _kind_from_response(call)
        if reproduced:
            rerendered = call.prompt
        else:
            rerendered = _nearest_miss(meeting, call.agent_id)
        yield RerenderedPrompt(
            seed=meeting.seed,
            set_name=meeting.set_name,
            meeting_index=meeting.meeting_index,
            meeting_id=meeting.meeting_id,
            kind=kind,
            agent_id=call.agent_id,
            recorded_prompt=call.prompt,
            rerendered_prompt=rerendered,
            reproduced=reproduced,
        )


def _kind_from_response(call: Any) -> str:
    """Fallback kind attribution from the recorded response payload (drift only).

    Reached only when the manager rendered nothing matching a recorded prompt (a
    perturbed template), so the render sink is useless; the recorded response's
    schema still classifies the call for the diff header.
    """

    from meetings.schemas import VoteBallot

    try:
        VoteBallot.model_validate_json(call.response_text)
    except Exception:
        return _KIND_ACCUSATION_ROUND
    return _KIND_VOTE_BALLOT


def _nearest_miss(meeting: ReconstructedMeeting, agent_id: PlayerId | None) -> str:
    """The manager's nearest same-speaker complete-prompt that was NOT recorded.

    Used only to diff a drift: the manager's actual bytes for this speaker that
    failed to match any recorded prompt. Empty when the manager made no such
    call (the whole meeting cascaded off an earlier drift).
    """

    for call in meeting.complete_calls:
        if not call.hit and call.agent_id == agent_id:
            return call.prompt
    for call in meeting.complete_calls:
        if not call.hit:
            return call.prompt
    return ""


def _byte_diff(recorded: str, rerendered: str) -> str:
    """A bounded unified diff of the first divergent region (readable failure)."""

    diff = difflib.unified_diff(
        recorded.splitlines(keepends=True),
        rerendered.splitlines(keepends=True),
        fromfile="recorded_prompt",
        tofile="rerendered_prompt",
        n=2,
    )
    body = "".join(diff)
    return body[:2000] if body else "(no line-level diff; whitespace-only drift)"


# --------------------------------------------------------------------------- #
# Per-set aggregate walk (one walk per set, shared by the assertions)         #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _SetWalk:
    """The full re-render of one committed sample set, aggregated once."""

    set_dir: Path
    prompts: tuple[RerenderedPrompt, ...]
    meetings: int
    seeds: int
    kinds_in_data: frozenset[str]
    # Task 16.3 (c): the live provenance decompositions collected on the same
    # walk. ``participant_rows`` are the open-tick graph rows the game builder
    # populated (``suspicion_graph_for_meeting``); ``ballot_prov_rows`` are the
    # post-fold rows the manager threaded into the ballot's ``suspicion_provenance``
    # kwarg (Seam C). Both must satisfy ``0.5 + sum(components) == suspicion``.
    participant_rows: tuple[SuspicionEntry, ...] = ()
    ballot_prov_rows: tuple[SuspicionEntry, ...] = ()


def _seed_from_path(path: Path) -> int:
    return int(path.stem.rsplit("-", 1)[-1])


def _seed_paths(set_dir: Path) -> list[Path]:
    return sorted(set_dir.glob("replay-seed-*.jsonl"), key=_seed_from_path)


def _canonical_renderers() -> dict[str, PromptRenderers]:
    """Renderers for every registered set, bound to the committed template root.

    Archived sets (Task 16.15) bind to their byte-copied template directory
    under :data:`_ARCHIVE_ROOT` AND to the map card those bytes rendered
    (:data:`ARCHIVED_MAP_CARDS`) — so a recorded meeting always re-renders via
    the templates its own stamps name and the render inputs they were given.
    """

    renderers = {name: build_prompt_renderers(name) for name in PROMPT_VERSION_SETS}
    renderers.update(
        {
            name: build_prompt_renderers(
                name, root=_ARCHIVE_ROOT, map_card=ARCHIVED_MAP_CARDS[name]
            )
            for name in ARCHIVED_PROMPT_VERSION_SETS
        }
    )
    return renderers


def _walk_set(set_dir: Path) -> _SetWalk:
    game_map = load_canonical_map()
    renderers_for_set = _canonical_renderers()
    prompts: list[RerenderedPrompt] = []
    kinds_in_data: set[str] = set()
    participant_rows: list[SuspicionEntry] = []
    ballot_prov_rows: list[SuspicionEntry] = []
    meetings = 0
    seed_paths = _seed_paths(set_dir)
    for path in seed_paths:
        for meeting in walk_replay_meetings(
            path, game_map=game_map, renderers_for_set=renderers_for_set
        ):
            meetings += 1
            for rendered in rerendered_prompts(meeting):
                prompts.append(rendered)
                kinds_in_data.add(rendered.kind)
            # Task 16.3 (c): the live open-tick graph rows the game builder
            # populated (provenance read straight off ``belief.provenance``).
            for participant in meeting.participants:
                participant_rows.extend(participant.suspicion_graph)
            # The post-fold rows threaded into every ballot render's inert
            # ``suspicion_provenance`` kwarg (Seam C).
            for render in meeting.renders:
                if render.kind == _KIND_VOTE_BALLOT:
                    ballot_prov_rows.extend(render.suspicion_provenance)
    return _SetWalk(
        set_dir=set_dir,
        prompts=tuple(prompts),
        meetings=meetings,
        seeds=len(seed_paths),
        kinds_in_data=frozenset(kinds_in_data),
        participant_rows=tuple(participant_rows),
        ballot_prov_rows=tuple(ballot_prov_rows),
    )


@pytest.fixture(scope="module", params=_SAMPLE_SETS, ids=lambda p: p.name)
def set_walk(request: pytest.FixtureRequest) -> _SetWalk:
    """Re-render one committed set once; every assertion below reads the result."""

    set_dir = request.param
    assert set_dir.is_dir(), f"missing committed sample set: {set_dir}"
    return _walk_set(set_dir)


# --------------------------------------------------------------------------- #
# The byte golden                                                             #
# --------------------------------------------------------------------------- #


def test_every_recorded_prompt_re_renders_byte_identically(
    set_walk: _SetWalk,
) -> None:
    """Byte-equality: every recorded prompt is reproduced by production code.

    The DoD's central claim — Task 16.3's inert widening changed no rendered
    byte. Each recorded ``llm_calls[].prompt`` must equal the bytes the real
    manager passed to ``complete()`` when re-run over the reconstructed inputs.
    Fails with a unified diff of the FIRST divergent call (seed, meeting, kind,
    speaker) — never a weakened assertion.
    """

    assert set_walk.prompts, f"{set_walk.set_dir.name}: walked zero recorded calls"
    failures = [rp for rp in set_walk.prompts if not rp.reproduced]
    if failures:
        first = failures[0]
        raise AssertionError(
            f"{set_walk.set_dir.name}: {len(failures)} of {len(set_walk.prompts)} "
            f"recorded prompts did not re-render byte-identically.\n"
            f"first divergence: seed={first.seed} meeting={first.meeting_id} "
            f"kind={first.kind} speaker={first.agent_id}\n"
            f"{_byte_diff(first.recorded_prompt, first.rerendered_prompt)}"
        )


def test_every_recorded_llm_call_is_consumed_exactly_once(
    set_walk: _SetWalk,
) -> None:
    """Coverage floor: the walk consumed every recorded meeting call, no more.

    Count the ``call_kind == "meeting"`` calls independently off disk and assert
    the walk emitted exactly one :class:`RerenderedPrompt` per recorded call, so
    the golden cannot silently walk a subset of the recorded prompts. All
    committed calls are ``"meeting"`` (0 ``"trigger"`` calls across the 100
    files); a ``"trigger"`` call would not flow through a meeting render seam and
    is asserted absent.
    """

    recorded_meeting_calls = 0
    for path in _seed_paths(set_walk.set_dir):
        for entry in read_all_entries(path):
            if isinstance(entry, MeetingReplayEntry):
                for call in entry.llm_calls:
                    assert call.call_kind == "meeting", (
                        f"{entry.meeting_id}: unexpected call_kind {call.call_kind!r}"
                    )
                    recorded_meeting_calls += 1
    assert recorded_meeting_calls == len(set_walk.prompts)
    assert set_walk.meetings > 0, f"{set_walk.set_dir.name}: walked zero meetings"


def test_present_template_kinds_are_each_reproduced(set_walk: _SetWalk) -> None:
    """No template kind that OCCURS in the recorded data is silently skipped.

    ``crewmate_report`` / ``accusation_round`` / ``vote_ballot`` all occur in
    both committed sets and must each be reproduced. ``impostor_report`` does
    NOT occur — every one of the 199 committed meeting openers is a crewmate
    (the FSM impostor presses no button; DESIGN.md §12) — so it is covered by
    :func:`test_impostor_report_opening_kind_is_exercised` instead, not asserted
    per-set here (asserting it would make the golden RED on unmodified code,
    which the DoD forbids). Each present kind's counter must be > 0.
    """

    counts = {kind: 0 for kind in _ALL_KINDS}
    for rp in set_walk.prompts:
        counts[rp.kind] = counts.get(rp.kind, 0) + 1
    for kind in (_KIND_CREWMATE_REPORT, _KIND_ACCUSATION_ROUND, _KIND_VOTE_BALLOT):
        assert counts[kind] > 0, (
            f"{set_walk.set_dir.name}: template kind {kind!r} occurs in the "
            f"recorded data but was never reproduced (counts={counts})"
        )
    # Every reproduced kind must be one of the four contract kinds.
    assert set_walk.kinds_in_data <= set(_ALL_KINDS)


def test_reconstructed_transcript_matches_the_recording(
    set_walk: _SetWalk,
) -> None:
    """Free cross-check: the reproduction is faithful, not merely prompt-shaped.

    Because the byte golden is only honest if the manager reached each prompt in
    the RIGHT context, assert the reconstructed transcript equals the recorded
    one turn-for-turn (speaker, index, kind, free_text). Ballots' targets and
    the ejected outcome are already pinned by the ``state_hash_after`` check
    inside the walk; the transcript pin catches a mid-meeting divergence that a
    later default would otherwise mask.
    """

    # One transcript comparison per meeting: re-walk lazily and compare. The
    # walk is cheap enough to repeat, and reading it here keeps the assertion
    # self-contained.
    game_map = load_canonical_map()
    renderers_for_set = _canonical_renderers()
    for path in _seed_paths(set_walk.set_dir):
        for meeting in walk_replay_meetings(
            path, game_map=game_map, renderers_for_set=renderers_for_set
        ):
            reconstructed = tuple(
                (t.speaker, t.turn_index, t.turn_kind, t.free_text)
                for t in meeting.result.transcript.turns
            )
            recorded = tuple(
                (t.speaker, t.turn_index, t.turn_kind, t.free_text)
                for t in meeting.entry.transcript.turns
            )
            assert reconstructed == recorded, (
                f"{meeting.meeting_id}: reconstructed transcript diverged from "
                f"the recording ({len(reconstructed)} vs {len(recorded)} turns)"
            )


# --------------------------------------------------------------------------- #
# The fourth kind: impostor_report exercised through the same manager seam    #
# --------------------------------------------------------------------------- #


def _first_meeting_state(
    set_dir: Path,
) -> tuple[WorldState, dict[PlayerId, TacticalAgent], Sequence[Any], Map]:
    """Reconstruct the world + agents at the first meeting of the set's seed-0.

    Reuses the production walk up to the first ``MeetingReplayEntry`` so the
    agents carry real reconstructed memory, then returns the pre-meeting state,
    the agents, and the trigger events — the inputs
    :func:`_build_participants` / :func:`_build_meeting_trigger` consume.
    """

    game_map = load_canonical_map()
    path = _seed_paths(set_dir)[0]
    seed = _seed_from_path(path)
    entries = read_all_entries(path)
    replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
    meeting_by_tick = {e.tick: e for e in entries if isinstance(e, MeetingReplayEntry)}
    num_players, num_impostors, tasks_per_crewmate = _roster_for(
        path.parent, replay_entries
    )
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    agents = _build_agents(state)
    with TemporaryDirectory(prefix="ailibi-golden-imp-") as audit_dir:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit_dir) / "audit.jsonl"
        )
        last_events: tuple[Any, ...] = ()
        for entry in replay_entries:
            _ingest_tick(service, agents, state, last_events)
            state, events = advance_tick(
                state, _deserialize_actions(entry.actions), game_map=game_map
            )
            if state.phase == "MEETING" and meeting_by_tick.get(entry.tick) is not None:
                return state, agents, tuple(events), game_map
            last_events = tuple(events)
    raise AssertionError(f"{set_dir.name}: seed-0 has no resolved meeting to reuse")


# The ON-arm overlay seam, read from the registry rather than listed, so a
# sibling arm registered later joins the subset enumeration below with no edit.
_OVERLAY_SET: str = "qwen3_6_27b"
_OVERLAY_KEYS: tuple[str, ...] = tuple(_PROMPT_VERSION_OVERLAYS)

# The ALL-ON composite, materialised by name: the arm the Wave-2 smoke and the
# adopting record spend a run on, so it is pinned rather than derived at the
# record. Grows when a sibling registers, which is the point -- the change shows
# up here as a diff instead of inside a fold nobody reads. Each cell carries the
# LINEAGE of every body that shaped it: ``accusation_round`` joins the roll-call
# variant's own v1 with the reporter arm's v5 line, so a bump to EITHER moves the
# stamp; a template no enabled arm re-bodies keeps its default value, because
# those are the default bytes.
_ALL_ON_STAMPS: Mapping[str, str] = {
    "crewmate_report": (
        "crewmate_report.qwen3_6_27b.v5.reporter_reasoning"
        "+crewmate_report.qwen3_6_27b.v5.testimony_shapes"
    ),
    "impostor_report": "impostor_report_roll_call.qwen3_6_27b.v1",
    "accusation_round": (
        "accusation_round_roll_call.qwen3_6_27b.v1"
        "+accusation_round.qwen3_6_27b.v5.reporter_reasoning"
        "+accusation_round.qwen3_6_27b.v5.testimony_shapes"
    ),
    "vote_ballot": (
        "vote_ballot.qwen3_6_27b.v5.corroboration_discipline"
        "+vote_ballot.qwen3_6_27b.v5.testimony_shapes"
    ),
}


def _contributors(template: str, keys: frozenset[str]) -> tuple[str, ...]:
    """The arms in ``keys`` that re-body ``template``, in registration order.

    The stamp is a statement about BODIES, so two slates share a template's stamp
    exactly when the same arms shaped it -- which is when the rendered bytes are
    the same. This is the predicate the invariant below is written against.
    """

    default = PROMPT_VERSION_SETS[_OVERLAY_SET]
    return tuple(
        key
        for key in _OVERLAY_KEYS
        if key in keys
        and _PROMPT_VERSION_OVERLAYS[key][_OVERLAY_SET][template] != default[template]
    )


def _templates_touched_by(keys: frozenset[str]) -> set[str]:
    """Templates at least one of ``keys`` re-bodies, against the default entry."""

    return {
        template
        for template in PROMPT_VERSION_SETS[_OVERLAY_SET]
        if _contributors(template, keys)
    }


def _resolve_every_subset() -> dict[frozenset[str], Mapping[str, str]]:
    """``prompt_versions_for_set`` over EVERY subset of the live overlay keys."""

    resolved: dict[frozenset[str], Mapping[str, str]] = {}
    for size in range(len(_OVERLAY_KEYS) + 1):
        for subset in combinations(_OVERLAY_KEYS, size):
            env = {env_var_for_lever(key): "1" for key in subset}
            resolved[frozenset(subset)] = prompt_versions_for_set(_OVERLAY_SET, env=env)
    return resolved


def overlay_stamp_violations(
    resolved: Mapping[frozenset[str], Mapping[str, str]],
) -> list[str]:
    """Every way a resolution table breaks the overlay-stamp invariant.

    Named, and returning data rather than asserting inline, so the planted cases
    can run through THIS function: a gate whose perturbation only compares two
    literals to each other stays green when the gate itself is deleted.

    Three rules, all forms of one claim -- the stamp is a statement about BODIES:

    * no template an arm re-bodies may wear a value any default registry entry
      carries (arm-shaped bytes must never resolve as default ones);
    * two slates share a template's stamp EXACTLY WHEN the same arms shaped it,
      which forbids a collision between different bodies AND a spurious split
      between identical ones;
    * a composite carries the LINEAGE of every body that shaped it, so a bump to
      any participating body moves it.
    """

    default_values = {
        value
        for versions in PROMPT_VERSION_SETS.values()
        for value in versions.values()
    }
    violations: list[str] = []
    for keys, versions in resolved.items():
        for template in _templates_touched_by(keys):
            if versions[template] in default_values:
                violations.append(
                    f"{sorted(keys)}/{template}: arm-shaped bytes wear the "
                    f"default value {versions[template]!r}"
                )
            for key in _contributors(template, keys):
                arm_value = _PROMPT_VERSION_OVERLAYS[key][_OVERLAY_SET][template]
                if arm_value not in versions[template]:
                    violations.append(
                        f"{sorted(keys)}/{template}: lost the lineage of {key} "
                        f"({arm_value!r} absent from {versions[template]!r})"
                    )
    for left, left_versions in resolved.items():
        for right, right_versions in resolved.items():
            for template in PROMPT_VERSION_SETS[_OVERLAY_SET]:
                same_bodies = _contributors(template, left) == _contributors(
                    template, right
                )
                same_stamp = left_versions[template] == right_versions[template]
                if same_stamp != same_bodies:
                    violations.append(
                        f"{sorted(left)} vs {sorted(right)}/{template}: same "
                        f"bodies={same_bodies} but same stamp={same_stamp}"
                    )
    return violations


def _first_meeting_prompt_set() -> Mapping[str, str]:
    """The ``prompt_versions`` stamp the 9p2i set's first meeting recorded."""

    path = _seed_paths(_SAMPLE_SETS[0])[0]
    for entry in read_all_entries(path):
        if isinstance(entry, MeetingReplayEntry):
            return entry.prompt_versions
    raise AssertionError(f"{path.name}: no recorded meeting to read a stamp from")


def test_no_archive_is_needed_because_the_default_registry_did_not_move() -> None:
    # An arm that re-bodies a template behind a default-OFF gate creates no
    # bump-in-flight window: the DEFAULT entry is untouched, so every committed
    # stamp still resolves through the live registry and every committed meeting
    # still re-renders through the live bodies -- which is exactly what the walk
    # above proves. Stated here so a future arm cannot quietly skip the archive
    # while ALSO moving the default entry.
    assert ARCHIVED_PROMPT_VERSION_SETS == {}
    assert not _ARCHIVE_ROOT.exists()
    for path in _SAMPLE_SETS:
        for replay in _seed_paths(path):
            for entry in read_all_entries(replay):
                if not isinstance(entry, MeetingReplayEntry):
                    continue
                assert dict(entry.prompt_versions) == dict(
                    PROMPT_VERSION_SETS[resolve_prompt_set(entry.prompt_versions)]
                )


def test_a_lever_on_recording_can_never_wear_a_default_stamp() -> None:
    """The provenance half of the OFF-path proof (Ruling 3(d)).

    The walk above is a real gate only while every committed stamp resolves
    through the LIVE registry -- which it does because the default entry does not
    move. That is what lets an arm merge with no archive. The other side of the
    same coin is that an arm-shaped recording must never resolve HERE: with a
    live overlay ON, every template that arm re-bodies stamps a value no default
    registry entry carries, so ``resolve_prompt_set`` could never mistake those
    bytes for these.

    Enumerated over EVERY subset of the live overlay keys, not spot-checked, so a
    sibling arm registered later cannot quietly collide.
    """

    resolved = _resolve_every_subset()
    assert dict(resolved[frozenset()]) == dict(PROMPT_VERSION_SETS[_OVERLAY_SET])

    violations = overlay_stamp_violations(resolved)
    assert violations == [], violations

    # And the ALL-ON arm -- the one 21.23 smokes and 21.24 records -- is
    # materialised by name rather than left to be derived at the record.
    assert dict(resolved[frozenset(_OVERLAY_KEYS)]) == _ALL_ON_STAMPS


def test_a_lever_on_stamp_resolves_to_the_set_that_wrote_it() -> None:
    """The other half: an arm-shaped stamp must resolve to ITS OWN set.

    The test above proves an arm stamp can never be mistaken for a default one.
    That separation is what makes a lever-ON recording unresolvable unless the
    arms are indexed, and an unresolvable recording cannot be reconstructed at
    all -- which is the state the Wave-2 record's own bytes would be in. Every
    subset resolves, including the all-ON slate 21.24 records.

    The planted case is the one that matters: a stamp carrying a version string
    NO arm of this build writes must still refuse. The index widens which stamps
    resolve, never how loosely they are matched.
    """

    for keys, versions in _resolve_every_subset().items():
        assert resolve_prompt_set(versions) == _OVERLAY_SET, sorted(keys)

    fabricated = {
        **_ALL_ON_STAMPS,
        "vote_ballot": "vote_ballot.qwen3_6_27b.v5.no_such_arm",
    }
    with pytest.raises(AssertionError, match="matched 0 registered sets"):
        resolve_prompt_set(fabricated)


def test_a_file_swapping_arm_serves_a_body_its_siblings_do_not_reach() -> None:
    """A KNOWN GAP, pinned so it cannot be rediscovered by a recording.

    An arm that swaps in a variant FILE serves a body authored independently of
    every sibling. A sibling whose block lives in the DEFAULT body therefore does
    not reach the render while that swap is on: the two compose in the stamp and
    not in the bytes. ``impostor_roll_call`` swaps ``accusation_round.j2`` for
    ``accusation_round_roll_call.j2``, which carries no ``<who_reported>`` block,
    so with both arms ON every statement turn silently loses the reporter-voice
    effects.

    Neither arm's slate is recorded (18.10's was not shipped by the CREW-ONLY
    ruling, and the Wave-2 record runs its own three arms with this one OFF), and
    the variant file belongs to the other arm's frozen v1 lineage, so this is
    pinned rather than patched here. The rule for the next arm author is in
    ``orchestrator.game.prompt_versions_for_set``: an arm that swaps a file must
    author its siblings' blocks into the variant. When one does, THIS test fails
    -- which is the point.
    """

    on_both = {"AILIBI_IMPOSTOR_ROLL_CALL": "1", "AILIBI_REPORTER_REASONING": "1"}
    renderers = build_prompt_renderers(_OVERLAY_SET, env=on_both)
    rendered = renderers.statement(
        agent_id="p-3",
        rendered_memory="(memory)",
        transcript=MeetingTranscript(turns=()),
        contradictions=(),
        prior_turn=None,
        turn_kind="reply",
        reporter_context=ReporterContext(reporter_id="p-1", tick=5),
        at_body=True,
    )
    assert "<who_reported>" not in rendered
    # With the swap OFF the SAME threaded context does render, so the assertion
    # above is about the variant body and not about a context that never landed.
    default_render = build_prompt_renderers(_OVERLAY_SET, env={}).statement(
        agent_id="p-3",
        rendered_memory="(memory)",
        transcript=MeetingTranscript(turns=()),
        contradictions=(),
        prior_turn=None,
        turn_kind="reply",
        reporter_context=ReporterContext(reporter_id="p-1", tick=5),
        at_body=True,
    )
    assert "<who_reported>" in default_render


def test_the_subset_invariant_bites_on_planted_stamp_tables() -> None:
    """The perturbation craft rule 2 asks for, run through the REAL checker.

    Three doctored resolution tables are fed to :func:`overlay_stamp_violations`
    -- the same function the gate above calls -- and each must be REPORTED. A
    planted case that only compared two literal dicts to each other would stay
    green if the checker were deleted, bypassed or inverted, which is what this
    replaces.
    """

    resolved = _resolve_every_subset()
    assert overlay_stamp_violations(resolved) == []

    # (a) COLLISION: an arm-shaped template wears a default value, so a recording
    #     made under the arm would resolve as a default one.
    collided = dict(resolved)
    arm = frozenset({"reporter_reasoning"})
    collided[arm] = {
        **resolved[arm],
        "crewmate_report": PROMPT_VERSION_SETS[_OVERLAY_SET]["crewmate_report"],
    }
    assert any("default value" in line for line in overlay_stamp_violations(collided))

    # (b) SPURIOUS SPLIT: two slates that shaped a template identically are given
    #     different stamps, which would send a recording to an archive it does
    #     not need.
    split = dict(resolved)
    split[frozenset()] = {
        **resolved[frozenset()],
        "vote_ballot": "vote_ballot.qwen3_6_27b.v5.invented",
    }
    assert any("same bodies" in line for line in overlay_stamp_violations(split))

    # (c) LOST LINEAGE: a composite rebuilt off the default value, dropping the
    #     variant body's own version -- the failure the per-template fold exists
    #     to stop, and the one a stamp cannot recover from.
    lossy = dict(resolved)
    all_on = frozenset(_OVERLAY_KEYS)
    lossy[all_on] = {
        **resolved[all_on],
        "accusation_round": (
            "accusation_round.qwen3_6_27b.v5.impostor_roll_call+reporter_reasoning"
        ),
    }
    assert any("lineage" in line for line in overlay_stamp_violations(lossy))


def test_impostor_report_opening_kind_is_exercised() -> None:
    """The fourth kind: drive an impostor opener through the real manager seam.

    Every committed opener is a crewmate, so ``impostor_report`` has no replay
    coverage; this exercises it directly. Reuse the reconstructed agents at the
    first committed meeting, retarget the trigger's opener to a LIVING impostor,
    and run the real :class:`MeetingManager` opening seam. The kind-tagging
    wrapper records that ``impostor_report`` was invoked for that impostor, and
    the render carries the impostor template's role marker — so the fourth kind
    is not a blind spot in the instrument. The stub returns the force-default
    placeholder (the opening still RENDERS before it defaults, which is all this
    coverage pin needs).
    """

    state, agents, events, game_map = _first_meeting_state(_SAMPLE_SETS[0])
    impostor = next(
        (
            pid
            for pid in sorted(state.players)
            if state.players[pid].alive and state.players[pid].role == "IMPOSTOR"
        ),
        None,
    )
    assert impostor is not None, "seed-0 first meeting has no living impostor"

    trigger = MeetingTrigger(
        triggered_by=impostor,
        trigger_tick=state.tick,
        description=f"{impostor} {EMERGENCY_TRIGGER_PHRASE} at tick {state.tick}",
    )
    participants = _build_participants(
        state=state, agents=agents, token_budget=DEFAULT_TOKEN_BUDGET
    )
    # Resolve the set's OWN recorded stamps — read off the replay rather than
    # written out here, so a prompt-set bump cannot leave this test pointing at a
    # version no committed meeting stamps — and take that set's renderers from
    # the same table the walk uses, so an archived stamp binds to its archived
    # template dir rather than a directory that does not exist.
    renderers = _canonical_renderers()[resolve_prompt_set(_first_meeting_prompt_set())]
    renders: list[_Render] = []
    stub = _RecordedResponseStub(responses={})
    manager = _tagging_manager(stub=stub, renderers=renderers, renders=renders)
    dead_ids = tuple(
        sorted(pid for pid, player in state.players.items() if not player.alive)
    )
    asyncio.run(
        manager.run(
            meeting_id="golden-impostor-opening",
            trigger=trigger,
            participants=participants,
            dead_ids=dead_ids,
        )
    )
    impostor_openings = [
        render
        for render in renders
        if render.kind == _KIND_IMPOSTOR_REPORT and render.agent_id == impostor
    ]
    assert impostor_openings, (
        "impostor opener did not dispatch to the impostor_report renderer; "
        f"kinds rendered: {sorted({r.kind for r in renders})}"
    )
    # The locked-set impostor template (impostor_report.qwen3_6_27b.v3) frames the
    # role as the saboteur — it carries NO "**IMPOSTOR**" literal (the qwen3_32b.v5
    # marker); its role marker is this unconditional persona line, absent from the
    # crewmate template, so its presence proves the impostor kind rendered.
    assert "for this match YOU are the saboteur" in impostor_openings[0].prompt


# --------------------------------------------------------------------------- #
# The perturbation leg: a golden that cannot fail is not a gate               #
# --------------------------------------------------------------------------- #


def test_one_byte_template_perturbation_breaks_the_golden(
    tmp_path: Path,
) -> None:
    """Flip one committed template byte; the byte golden must then FAIL.

    The victim is the LIVE ``qwen3_6_27b/crewmate_report.j2``. It was the
    ARCHIVED v4 body while the committed sets stamped ``*.qwen3_6_27b.v4`` and
    the live registry had already moved to v5 — then, perturbing the live body
    would have been a no-op and the leg would have asserted nothing. The
    baseline-8 record wrote every set at v5, so the live body IS what every
    recorded meeting re-renders through, and the archive is empty.

    Copy the template dirs under a scratch root, append one byte to that victim,
    build renderers against the perturbed root, and re-run ONE recorded meeting.
    At least one recorded prompt must no longer reproduce byte-for-byte —
    proving the gate can fail. Kept cheap: the first meeting-bearing seed of
    9p2i, one meeting.
    """

    set_dir = _SAMPLE_SETS[0]
    perturbed_root = tmp_path / "prompts"
    for name in PROMPT_VERSION_SETS:
        shutil.copytree(_PROMPTS_ROOT / name, perturbed_root / name)
    victim = perturbed_root / "qwen3_6_27b" / "crewmate_report.j2"
    victim.write_bytes(victim.read_bytes() + b"\n")  # one-byte perturbation

    perturbed_renderers = {
        name: build_prompt_renderers(name, root=perturbed_root)
        for name in PROMPT_VERSION_SETS
    }
    game_map = load_canonical_map()
    reproduced_all = True
    walked_a_meeting = False
    for path in _seed_paths(set_dir):
        for meeting in walk_replay_meetings(
            path, game_map=game_map, renderers_for_set=perturbed_renderers
        ):
            walked_a_meeting = True
            for rendered in rerendered_prompts(meeting):
                reproduced_all = reproduced_all and rendered.reproduced
            break
        if walked_a_meeting:
            break

    assert walked_a_meeting, "perturbation leg walked no meeting"
    assert not reproduced_all, (
        "a one-byte crewmate_report.j2 perturbation left every prompt "
        "byte-identical — the golden cannot detect a template change and is "
        "therefore not a gate"
    )


def test_defaults_are_the_only_lookup_misses(set_walk: _SetWalk) -> None:
    """Invariant behind the stub: a lookup miss is always a manager default.

    Every recorded response parses cleanly (a failed provider attempt raised
    before the recording client logged it, so it is absent from ``llm_calls``),
    which is why keying the stub on the recorded prompt is exact: a miss is a
    ``deadline_default`` turn/vote, never a mis-key. If any recorded prompt did
    NOT reproduce, this set's byte golden already failed; here assert the dual —
    every reproduced call round-tripped, so the reproduced count equals the
    recorded count.
    """

    reproduced = sum(1 for rp in set_walk.prompts if rp.reproduced)
    assert reproduced == len(set_walk.prompts), (
        f"{set_walk.set_dir.name}: {len(set_walk.prompts) - reproduced} recorded "
        "prompts were lookup misses — see the byte-equality failure above"
    )


# --------------------------------------------------------------------------- #
# Live provenance population (Task 16.3 parts (a)+(b), over both committed sets) #
# --------------------------------------------------------------------------- #

# The eight provenance channels on ``SuspicionEntry`` (mirror
# ``agents.memory.beliefs.SuspicionProvenance`` field-by-name).
_PROVENANCE_COMPONENTS: tuple[str, ...] = (
    "flag_lift",
    "body_proximity",
    "kill_or_vent_pin",
    "testimony_spread",
    "accusation_carry",
    "carried_hard",
    "carried_soft",
    "unattributed",
)

# Non-vacuous "populated, not defaults" floors (DoD bullets 1 + 5), measured on
# the baseline-4 committed sets 2026-07-13: 9p2i had 1393/1615 open-tick graph rows
# and 1973/2372 folded ballot rows carrying a nonzero hard/soft split; 4p1i had
# 13/13 and 73/91. These per-set-safe floors sit well below the smaller set's counts,
# so a regression that stopped populating provenance (defaults everywhere) trips
# them while the healthy committed data clears them.
_MIN_POPULATED_PARTICIPANT_ROWS = 10
_MIN_POPULATED_BALLOT_ROWS = 50


def _entry_sum_error(entry: SuspicionEntry) -> float:
    """Error in the sum invariant, accounting for the J1 render clamp (Task 16.4).

    The eight provenance fields decompose the PRE-clamp suspicion
    (``0.5 + sum == raw_suspicion``, the belief store's own invariant). A row's
    rendered scalar is then EITHER that raw sum (a post-fold ballot row the fold
    lifted above the sub-gate, or a row the manager's ``seed_player`` reconciled)
    OR its J1 clamp: the graph builder
    (``orchestrator.game.TacticalAgent.suspicion_graph_for_meeting``) folds an
    entirely-soft conviction-grade row down to
    :func:`~agents.memory.beliefs.hard_evidence_gated_suspicion` while leaving the
    raw decomposition as the true evidence record, and the manager's ballot seam
    passes such a row through verbatim when nothing reconciles it. So the faithful
    invariant is that the scalar matches the raw sum OR its clamp (``min`` of the
    two errors). For an unclamped row the clamp is a no-op and this is exactly the
    original ``0.5 + sum == suspicion`` check; a clamped row's deliberate shortfall
    (raw sum >= 0.60 rendered at the 0.59 sub-gate ceiling) is accounted for without
    masking a row inconsistent with BOTH (the game builder's ``suspicion_graph``
    docstring qualifies the raw invariant to the lever-OFF case)."""

    total = sum(float(getattr(entry, name)) for name in _PROVENANCE_COMPONENTS)
    provenance = SuspicionProvenance(
        flag_lift=entry.flag_lift,
        body_proximity=entry.body_proximity,
        kill_or_vent_pin=entry.kill_or_vent_pin,
        testimony_spread=entry.testimony_spread,
        accusation_carry=entry.accusation_carry,
        carried_hard=entry.carried_hard,
        carried_soft=entry.carried_soft,
        unattributed=entry.unattributed,
    )
    raw_error = abs((0.5 + total) - entry.suspicion)
    clamp_error = abs(
        hard_evidence_gated_suspicion(0.5 + total, provenance) - entry.suspicion
    )
    return min(raw_error, clamp_error)


def _has_hard_or_soft(entry: SuspicionEntry) -> bool:
    """A row carries a real decomposition (some hard or soft channel is nonzero).

    ``unattributed`` alone does NOT count as populated -- it is the residual
    bucket every seed writes, so a row with only unattributed movement carries no
    source-tagged evidence. A nonzero hard or soft channel is the "populated, not
    defaults" signal the DoD requires.
    """

    hard = (
        entry.flag_lift
        + entry.body_proximity
        + entry.kill_or_vent_pin
        + entry.carried_hard
    )
    soft = entry.testimony_spread + entry.accusation_carry + entry.carried_soft
    return hard != 0.0 or soft != 0.0


def test_live_suspicion_graph_rows_decompose_to_the_scalar(
    set_walk: _SetWalk,
) -> None:
    """Every live open-tick graph row satisfies the sum invariant and is populated.

    DoD bullets 1 + 5, over both committed sets: the participants
    ``_build_participants`` produced VERBATIM carry the game builder's
    ``suspicion_graph_for_meeting`` rows, whose eight provenance fields are read
    straight off ``belief.provenance``. Every row must satisfy the sum invariant
    ``0.5 + sum(components) == suspicion`` -- or, for an entirely-soft
    conviction-grade row the now-unconditional J1 render clamp (Task 16.4) folds to
    the 0.59 sub-gate ceiling, that clamped scalar (see :func:`_entry_sum_error`) --
    within :data:`~agents.memory.beliefs.SUSPICION_PROVENANCE_ATOL`, and a
    non-vacuous floor of rows must carry a real hard/soft decomposition (not
    all-default) -- proving 16.15's future surface has genuine data, not zeros.
    """

    assert set_walk.participant_rows, (
        f"{set_walk.set_dir.name}: walked zero participant graph rows"
    )
    for entry in set_walk.participant_rows:
        err = _entry_sum_error(entry)
        assert err <= SUSPICION_PROVENANCE_ATOL, (
            f"{set_walk.set_dir.name}: live graph row {entry.player_id!r} violates "
            f"the sum invariant (raw or J1-clamped) (error {err}, suspicion "
            f"{entry.suspicion})"
        )
    populated = sum(1 for e in set_walk.participant_rows if _has_hard_or_soft(e))
    assert populated >= _MIN_POPULATED_PARTICIPANT_ROWS, (
        f"{set_walk.set_dir.name}: only {populated} of "
        f"{len(set_walk.participant_rows)} live graph rows carry a nonzero "
        f"hard/soft split (floor {_MIN_POPULATED_PARTICIPANT_ROWS}) — provenance "
        "population regressed to defaults"
    )


def test_folded_ballot_provenance_rows_decompose_to_the_scalar(
    set_walk: _SetWalk,
) -> None:
    """Every post-fold ballot provenance row satisfies the sum invariant.

    The ballot seam (Seam C) threads the SAME post-fold rows into
    ``suspicion_provenance`` as into ``suspicion_graph`` -- the rows
    ``_suspicion_graph_with_contradictions`` emits after the Rule-2 lift, the
    pre-vote fold, and the Task 13.14 joint cap. The joint cap's provenance
    scaling must keep the sum invariant ``0.5 + sum(components) == suspicion`` on
    every emitted row (the render-after-fold consistency pin) -- a fold can lift a
    subject above the J1 sub-gate ceiling (the raw sum stands), while a row the
    seam passes through verbatim carries the graph builder's clamp
    (:func:`_entry_sum_error` admits either), over both committed sets. A
    non-vacuous floor must again carry a real hard/soft split.
    """

    assert set_walk.ballot_prov_rows, (
        f"{set_walk.set_dir.name}: walked zero folded ballot provenance rows"
    )
    for entry in set_walk.ballot_prov_rows:
        err = _entry_sum_error(entry)
        assert err <= SUSPICION_PROVENANCE_ATOL, (
            f"{set_walk.set_dir.name}: folded ballot row {entry.player_id!r} "
            f"violates the sum invariant (raw or J1-clamped) (error {err}, suspicion "
            f"{entry.suspicion})"
        )
    populated = sum(1 for e in set_walk.ballot_prov_rows if _has_hard_or_soft(e))
    assert populated >= _MIN_POPULATED_BALLOT_ROWS, (
        f"{set_walk.set_dir.name}: only {populated} of "
        f"{len(set_walk.ballot_prov_rows)} folded ballot rows carry a nonzero "
        f"hard/soft split (floor {_MIN_POPULATED_BALLOT_ROWS})"
    )


# --------------------------------------------------------------------------- #
# The meeting-history fold: the mirror must fold what the live loop folded      #
# --------------------------------------------------------------------------- #

_MEETINGS_HEADER = "## Meetings so far:"
# One committed 9p2i seed resolving three meetings, so the SECOND meeting renders
# from a memory that must already carry the FIRST meeting's announced outcome.
_MULTI_MEETING_REPLAY = _SAMPLE_SETS[0] / "replay-seed-0.jsonl"


def _second_meeting_renders() -> tuple[str, ...]:
    """Every prompt the walk renders for the SECOND meeting of one replay."""

    renderers_for_set = _canonical_renderers()
    game_map = load_canonical_map()
    for meeting in walk_replay_meetings(
        _MULTI_MEETING_REPLAY,
        game_map=game_map,
        renderers_for_set=renderers_for_set,
    ):
        if meeting.meeting_index == 1:
            return tuple(render.prompt for render in meeting.renders)
    raise AssertionError(f"{_MULTI_MEETING_REPLAY.name}: no second meeting")


def test_the_walk_folds_meeting_outcomes_into_the_memory_it_renders() -> None:
    # The mirror's half of the reconstruction parity: the memory this walk
    # renders the SECOND meeting from carries the FIRST meeting's announced
    # outcome — the same rows the live loop wrote via
    # ``_notify_meeting_concluded`` while recording. A walk that skipped the fold
    # would render a memory no live agent ever held, and every prompt-byte
    # assertion built on it would be measuring the wrong thing.
    prompts = _second_meeting_renders()
    assert prompts
    assert any(_MEETINGS_HEADER in prompt for prompt in prompts)


def test_removing_the_fold_empties_the_block_the_previous_test_asserts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The planted divergence that proves the gate above can fail: neutralise the
    # shared fold and the block disappears from every render, so the assertion
    # that it is present is a real check rather than prose.
    import sys

    monkeypatch.setattr(
        sys.modules[__name__],
        "fold_meeting_outcome_into_memories",
        lambda *args, **kwargs: None,
    )
    prompts = _second_meeting_renders()
    assert prompts
    assert not any(_MEETINGS_HEADER in prompt for prompt in prompts)
