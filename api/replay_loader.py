"""Engine-playback replay loader for the spectator API (DESIGN.md §7, §11.4, §1.3).

The replay log persists ``state_hash`` per tick plus the recorded action
stream, not per-tick player positions (``orchestrator/replay.py``). To produce
the per-tick :class:`~api.schemas.AgentTickStateView` DTOs the frontend needs,
this loader re-seeds the engine from the game's seed and re-applies the
recorded actions through :func:`engine.tick.advance_tick`, mirroring the
orchestrator's own tick loop. Meeting outcomes are re-applied via the
orchestrator's :func:`~orchestrator.game.apply_meeting_result`. Every
reconstructed ``state_hash`` is checked against the recorded one; a divergence
is a determinism break and raises :class:`ReplayStateMismatchError` (surfaced
as HTTP 500 by the routes).

This is a *read-only* engine touch: the loader IMPORTS from ``engine/`` and
``orchestrator/`` but modifies nothing. ``api/`` is a privileged spectator
surface and is intentionally outside the observation firewall (DESIGN.md §1.3),
which forbids ``agents/``, ``llm/``, ``meetings/`` from importing ``engine/`` —
not ``api/``.

Per-game results are memoized in a per-process LRU cache keyed by ``game_id``;
replays are immutable once written, so process-restart is the only
invalidation. No cross-process cache (Redis) — that lands in Phase 5.
"""

from __future__ import annotations

import hashlib
import re
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, Literal

from fastapi import Request
from pydantic import TypeAdapter

from agents.memory.store import DEFAULT_TOKEN_BUDGET, AgentMemory, render_for_prompt
from agents.perception import EVENT_SAW_BODY, EVENT_SAW_PLAYER, ingest_packet
from api.schemas import (
    AccusationClaimView,
    AgentMemoryView,
    AgentTickStateView,
    AlibiClaimView,
    BallotView,
    BeliefEntryView,
    CompletedTaskObsView,
    ContradictionView,
    CorroborationClaimView,
    EdgeView,
    EvalCostSummaryView,
    FailedCallView,
    FoundBodyObsView,
    KillEventView,
    LLMCallView,
    MapLayoutView,
    MeetingTriggeredEventView,
    MeetingView,
    PlayerView,
    PositionView,
    ReplayMetadataView,
    ReplayView,
    ReportBodyEventView,
    ReportView,
    RoomView,
    SabotageEventView,
    SawPlayerView,
    SizeView,
    StatementView,
    TaskCompletedEventView,
    TickEventView,
    TickView,
    VentView,
)
from engine.actions import Action
from engine.events import (
    EngineEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    SabotageStartedEvent,
    TaskCompletedEvent,
)
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingResult,
    ObservationClaim,
    ReportDocument,
    SawPlayerObservation,
    Statement,
    VoteBallot,
)
from observation.service import ObservationService
from orchestrator.game import (
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    apply_meeting_result,
)
from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    compute_cost_usd,
    read_all_entries,
    read_game_outcome,
)
from orchestrator.seeder import seed_initial_state

_DEFAULT_CACHE_SIZE: Final[int] = 16

_GAME_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"headless-seed-(-?\d+)")
_FILENAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"replay-seed-(-?\d+)\.jsonl")
_PLAYER_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"p-(\d+)")

# Deterministic render palette assigned to players by their ``p-N`` index so
# the spectator UI gets stable, visually distinct colors without persisting a
# color in the engine. Index past the palette wraps; non-``p-N`` ids fall back
# to a hash-derived color.
_COLOR_PALETTE: Final[tuple[str, ...]] = (
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#bcf60c",
    "#fabebe",
    "#008080",
    "#9a6324",
)

_ACTION_ADAPTER: Final[TypeAdapter[Action]] = TypeAdapter(Action)

_TriggerKind = Literal["body", "emergency"]


class ReplayStateMismatchError(RuntimeError):
    """Reconstructed ``state_hash`` diverged from the recorded one.

    Indicates a replay-determinism break (DESIGN.md §0, §11.4): either
    non-determinism in :func:`engine.tick.advance_tick`, wrong action
    deserialization, or wrong meeting-result application. Surfaced as HTTP 500
    with the offending tick + game id in the response body.
    """

    def __init__(self, *, game_id: str, tick: int, expected: str, actual: str) -> None:
        self.game_id = game_id
        self.tick = tick
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"replay state-hash mismatch for {game_id!r} at tick {tick}: "
            f"recorded {expected!r}, reconstructed {actual!r}"
        )


@dataclass(frozen=True)
class _WalkResult:
    """Internal result of one engine-playback pass over a replay file."""

    initial_state: WorldState
    ticks: tuple[TickView, ...]
    meeting_entries: tuple[MeetingReplayEntry, ...]
    failed_calls: tuple[FailedCallReplayEntry, ...]
    trigger_kind_by_meeting_id: Mapping[str, _TriggerKind]
    memories: Mapping[tuple[str, str], AgentMemoryView]


class ReplayLoader:
    """Loads + engine-replays JSONL replays into sanitized spectator DTOs.

    The loader is the single source of truth for engine-playback: routes import
    it and never compose engine APIs directly. ``load_replay`` and the
    meeting-memory reconstruction are memoized per ``game_id`` in per-process
    LRU caches (default ``maxsize=16``); :meth:`clear_cache` resets them (used
    by tests to stay hermetic).
    """

    def __init__(
        self,
        replay_dir: Path,
        *,
        game_map: Map | None = None,
        cache_size: int = _DEFAULT_CACHE_SIZE,
    ) -> None:
        self._replay_dir = replay_dir
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._map_view = self._build_map_view()
        self._cached_load = lru_cache(maxsize=cache_size)(self._load_replay)
        self._cached_memories = lru_cache(maxsize=cache_size)(
            self._reconstruct_meeting_memories
        )

    # -- public API -------------------------------------------------------

    def list_replays(self) -> list[ReplayMetadataView]:
        """Scan the replay dir and return metadata for every replay, by seed."""

        return [self._metadata_view(path, seed) for seed, path in self._replay_paths()]

    def load_replay(self, game_id: str) -> ReplayView:
        """Return the full reconstructed :class:`ReplayView` (LRU-cached).

        Raises :class:`FileNotFoundError` if no replay matches ``game_id`` and
        :class:`ReplayStateMismatchError` if engine playback diverges from the
        recorded state hashes.
        """

        return self._cached_load(game_id)

    def cost_summary(self) -> EvalCostSummaryView:
        """Aggregate LLM cost + decisive-outcome split across every replay."""

        paths = [path for _, path in self._replay_paths()]
        total_replays = len(paths)
        costs = [compute_cost_usd(path) for path in paths]
        total_cost = sum(costs)
        winners = [read_game_outcome(path) for path in paths]
        decisive = [winner for winner in winners if winner is not None]

        decisive_split: dict[str, float] = {}
        if decisive:
            for side in ("CREWMATES", "IMPOSTORS"):
                decisive_split[side] = sum(1 for w in decisive if w == side) / len(
                    decisive
                )

        return EvalCostSummaryView(
            total_replays=total_replays,
            total_cost_usd=total_cost,
            mean_cost_per_replay=(total_cost / total_replays if total_replays else 0.0),
            max_cost_per_replay=(max(costs) if costs else 0.0),
            decisive_split=decisive_split,
        )

    def get_meeting_memory(
        self, game_id: str, meeting_id: str, agent_id: str
    ) -> AgentMemoryView:
        """Return one agent's memory snapshot at one meeting boundary.

        Raises :class:`FileNotFoundError` for an unknown ``game_id`` and
        :class:`KeyError` for an unknown meeting or agent (routes map both to
        404). Memory is only exposed at meeting boundaries per the 4.1 decision.
        """

        memories = self._cached_memories(game_id)
        known_meetings = {meeting for meeting, _ in memories}
        if meeting_id not in known_meetings:
            raise KeyError(f"meeting not found: {meeting_id}")
        key = (meeting_id, agent_id)
        if key not in memories:
            raise KeyError(f"agent not found at meeting {meeting_id}: {agent_id}")
        return memories[key]

    def clear_cache(self) -> None:
        """Drop both per-process caches (engine playback + memory walk)."""

        self._cached_load.cache_clear()
        self._cached_memories.cache_clear()

    # -- cached implementations ------------------------------------------

    def _load_replay(self, game_id: str) -> ReplayView:
        path = self._resolve_path(game_id)
        if path is None:
            raise FileNotFoundError(game_id)
        seed = _parse_seed_from_game_id(game_id)
        if seed is None:
            raise FileNotFoundError(game_id)

        walk = self._walk(path, seed, collect_memory=False)
        return ReplayView(
            metadata=self._metadata_view(path, seed),
            map=self._map_view,
            players=self._players_view(walk.initial_state),
            ticks=walk.ticks,
            meetings=tuple(
                self._meeting_view(entry, walk.trigger_kind_by_meeting_id)
                for entry in walk.meeting_entries
            ),
            failed_calls=tuple(_failed_call_view(entry) for entry in walk.failed_calls),
        )

    def _reconstruct_meeting_memories(
        self, game_id: str
    ) -> Mapping[tuple[str, str], AgentMemoryView]:
        path = self._resolve_path(game_id)
        if path is None:
            raise FileNotFoundError(game_id)
        seed = _parse_seed_from_game_id(game_id)
        if seed is None:
            raise FileNotFoundError(game_id)
        return self._walk(path, seed, collect_memory=True).memories

    # -- engine playback --------------------------------------------------

    def _walk(self, path: Path, seed: int, *, collect_memory: bool) -> _WalkResult:
        """Re-seed and re-apply the recorded action stream through the engine.

        Mirrors :meth:`orchestrator.game.HeadlessGame.run`'s tick loop. When
        ``collect_memory`` is set, the agent observation+perception pipeline is
        re-run in lockstep so per-agent memory can be re-rendered at meeting
        boundaries (the observation audit log is routed to a throwaway temp
        file). Verifies every reconstructed ``state_hash`` against the record.
        """

        game_id = _game_id_for_seed(seed)
        entries = read_all_entries(path)
        replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
        meeting_entries = tuple(e for e in entries if isinstance(e, MeetingReplayEntry))
        failed_calls = tuple(e for e in entries if isinstance(e, FailedCallReplayEntry))
        meeting_by_tick = {entry.tick: entry for entry in meeting_entries}

        initial_state = seed_initial_state(
            seed=seed,
            game_map=self._game_map,
            num_players=_infer_num_players(replay_entries),
            num_impostors=DEFAULT_NUM_IMPOSTORS,
        )
        state = initial_state

        memories: dict[str, AgentMemory] = {}
        service: ObservationService | None = None
        audit_dir: tempfile.TemporaryDirectory[str] | None = None
        if collect_memory:
            audit_dir = tempfile.TemporaryDirectory(prefix="ailibi-replay-audit-")
            service = ObservationService(
                game_map=self._game_map,
                audit_log_path=Path(audit_dir.name) / "audit.jsonl",
            )
            memories = {pid: AgentMemory() for pid in initial_state.players}

        ticks: list[TickView] = []
        trigger_kind_by_meeting_id: dict[str, _TriggerKind] = {}
        memory_views: dict[tuple[str, str], AgentMemoryView] = {}
        last_events: tuple[EngineEvent, ...] = ()
        meeting_index = 0

        try:
            for entry in replay_entries:
                if service is not None:
                    self._ingest_tick(service, memories, state, last_events)

                actions = _deserialize_actions(entry.actions)
                state, events = advance_tick(state, actions, game_map=self._game_map)
                actual = _state_hash(state)
                if actual != entry.state_hash:
                    raise ReplayStateMismatchError(
                        game_id=game_id,
                        tick=entry.tick,
                        expected=entry.state_hash,
                        actual=actual,
                    )

                meeting_entry: MeetingReplayEntry | None = None
                meeting_id: str | None = None
                trigger_kind: _TriggerKind | None = None
                body_id: str | None = None
                if state.phase == "MEETING":
                    meeting_entry = meeting_by_tick.get(entry.tick)
                    trigger_kind, body_id = _meeting_trigger_from_events(events)
                    meeting_id = (
                        meeting_entry.meeting_id
                        if meeting_entry is not None
                        else _meeting_id_for(game_id, meeting_index)
                    )
                    trigger_kind_by_meeting_id[meeting_id] = trigger_kind

                ticks.append(self._tick_view(entry.tick, state, events, meeting_id))

                if state.phase != "MEETING":
                    if state.phase == "GAME_OVER":
                        break
                    last_events = tuple(events)
                    continue

                assert meeting_id is not None  # set above when phase == MEETING

                if meeting_entry is None:
                    # Partial replay: the meeting opened but never resolved
                    # (the run crashed mid-meeting per Task 3.19). It is not
                    # exposed via /meetings/{meeting_id}, so do NOT snapshot
                    # memory for it either — keep the two endpoints consistent.
                    # The tick timeline is intact up to here; stop the walk.
                    break

                if collect_memory:
                    # Snapshot every known player, alive or dead. The endpoint
                    # contract is agent-based (ThoughtStream selects by agent),
                    # so a player who died before this meeting must still be
                    # retrievable; their memory is frozen at death (perception
                    # stops ingesting once they are dead).
                    for pid in sorted(state.players):
                        memory_views[(meeting_id, pid)] = self._agent_memory_view(
                            agent_id=pid,
                            tick=entry.tick,
                            meeting_state=state,
                            memory=memories[pid],
                            meeting_entry=meeting_entry,
                        )

                pre_meeting_events = tuple(events)
                result = _meeting_result_from_entry(meeting_entry)
                state, post_events = apply_meeting_result(
                    state,
                    result,
                    game_map=self._game_map,
                    triggering_body_id=body_id,
                )
                after = _state_hash(state)
                if after != meeting_entry.state_hash_after:
                    raise ReplayStateMismatchError(
                        game_id=game_id,
                        tick=entry.tick,
                        expected=meeting_entry.state_hash_after,
                        actual=after,
                    )
                meeting_index += 1
                if state.phase == "GAME_OVER":
                    break
                last_events = pre_meeting_events + tuple(post_events)
        finally:
            if audit_dir is not None:
                audit_dir.cleanup()

        return _WalkResult(
            initial_state=initial_state,
            ticks=tuple(ticks),
            meeting_entries=meeting_entries,
            failed_calls=failed_calls,
            trigger_kind_by_meeting_id=trigger_kind_by_meeting_id,
            memories=memory_views,
        )

    def _ingest_tick(
        self,
        service: ObservationService,
        memories: Mapping[str, AgentMemory],
        state: WorldState,
        last_events: Sequence[EngineEvent],
    ) -> None:
        """Re-run perception for every alive agent (mirrors the game loop).

        Matches :meth:`orchestrator.game.TacticalAgent.decide`: a packet is
        built from the pre-tick world state and the previous tick's events, then
        ingested into the agent's episodic store. Tactical/strategic output is
        irrelevant for replay (we have the recorded actions); only the memory
        side effect matters.
        """

        for pid in sorted(state.players):
            if not state.players[pid].alive:
                continue
            packet = service.build_packet(
                world_state=state, agent_id=pid, engine_events=last_events
            )
            ingest_packet(
                packet=packet,
                memory=memories[pid].episodic,
                beliefs=memories[pid].beliefs,
            )

    # -- DTO builders -----------------------------------------------------

    def _tick_view(
        self,
        tick: int,
        state: WorldState,
        events: Sequence[EngineEvent],
        meeting_id: str | None,
    ) -> TickView:
        agent_states = tuple(
            self._agent_tick_state(state, pid) for pid in sorted(state.players)
        )
        sabotage = state.sabotage
        sabotage_active = (
            (sabotage.kind,) if sabotage is not None and sabotage.active else ()
        )
        return TickView(
            tick=tick,
            agent_states=agent_states,
            events=self._tick_events(state, events, meeting_id),
            sabotage_active=sabotage_active,
            tasks_completed_total=sum(1 for t in state.tasks.values() if t.completed),
            tasks_required_total=len(state.tasks),
        )

    def _agent_tick_state(self, state: WorldState, pid: str) -> AgentTickStateView:
        player = state.players[pid]
        return AgentTickStateView(
            agent_id=pid,
            room_id=player.room if player.alive else None,
            is_alive=player.alive,
            is_venting=player.in_vent,
            task_progress=self._task_progress(state, pid, player.role),
            current_action=_current_action(player.last_action),
        )

    def _task_progress(self, state: WorldState, pid: str, role: str) -> float | None:
        if role == "IMPOSTOR":
            return None
        owned = [task for task in state.tasks.values() if task.owner == pid]
        if not owned:
            return 0.0
        required = sum(task.required_ticks for task in owned)
        if required <= 0:
            return 0.0
        progress = sum(task.progress for task in owned)
        return progress / required

    def _tick_events(
        self,
        state: WorldState,
        events: Sequence[EngineEvent],
        meeting_id: str | None,
    ) -> tuple[TickEventView, ...]:
        views: list[TickEventView] = []
        for event in events:
            if isinstance(event, KilledEvent):
                views.append(
                    KillEventView(
                        type="kill",
                        tick=event.tick,
                        killer_id=event.actor,
                        victim_id=event.target,
                        room_id=event.room,
                    )
                )
            elif isinstance(event, TaskCompletedEvent):
                views.append(
                    TaskCompletedEventView(
                        type="task_completed",
                        tick=event.tick,
                        agent_id=event.actor,
                        task_id=event.task_id,
                        room_id=self._game_map.tasks[event.task_id].room,
                    )
                )
            elif isinstance(event, SabotageStartedEvent):
                if event.kind == "lights":
                    views.append(
                        SabotageEventView(
                            type="sabotage",
                            tick=event.tick,
                            kind="lights",
                            room_id=None,
                            actor_id=event.actor,
                        )
                    )
            elif isinstance(event, MeetingTriggeredEvent):
                if meeting_id is None:
                    raise RuntimeError(
                        "MeetingTriggered event without a resolved meeting id"
                    )
                kind: _TriggerKind = (
                    "body" if event.trigger == "report" else "emergency"
                )
                views.append(
                    MeetingTriggeredEventView(
                        type="meeting_triggered",
                        tick=event.tick,
                        meeting_id=meeting_id,
                        triggered_by=event.actor,
                        trigger_kind=kind,
                    )
                )
                if event.trigger == "report" and event.body_id is not None:
                    body = state.bodies.get(event.body_id)
                    if body is not None:
                        views.append(
                            ReportBodyEventView(
                                type="report_body",
                                tick=event.tick,
                                reporter_id=event.actor,
                                body_of=body.player_id,
                                room_id=body.room,
                            )
                        )
        return tuple(views)

    def _meeting_view(
        self,
        entry: MeetingReplayEntry,
        trigger_kind_by_meeting_id: Mapping[str, _TriggerKind],
    ) -> MeetingView:
        return MeetingView(
            meeting_id=entry.meeting_id,
            tick=entry.tick,
            triggered_by=entry.triggered_by,
            trigger_kind=trigger_kind_by_meeting_id[entry.meeting_id],
            outcome=entry.outcome,
            ejected_player_id=entry.ejected_player_id,
            reports=tuple(_report_view(r) for r in entry.transcript.reports),
            statements=tuple(_statement_view(s) for s in entry.transcript.statements),
            ballots=tuple(_ballot_view(b) for b in entry.ballots),
            contradictions=tuple(_contradiction_view(c) for c in entry.contradictions),
            llm_calls=tuple(
                _llm_call_view(call, entry.prompt_versions) for call in entry.llm_calls
            ),
            prompt_versions=dict(entry.prompt_versions),
            total_cost_usd=sum((call.cost_usd for call in entry.llm_calls), 0.0),
        )

    def _agent_memory_view(
        self,
        *,
        agent_id: str,
        tick: int,
        meeting_state: WorldState,
        memory: AgentMemory,
        meeting_entry: MeetingReplayEntry | None,
    ) -> AgentMemoryView:
        role = meeting_state.players[agent_id].role
        owned = [
            task for task in meeting_state.tasks.values() if task.owner == agent_id
        ]

        # Observations are projected from the agent's own reconstructed episodic
        # memory (the same store ``rendered_memory_text`` renders), NOT from the
        # agent's submitted report — the report is a selective output and would
        # leave ``observations`` empty/inconsistent with the rendered view (and
        # empty for dead non-participants). Only the structured-claim event
        # types map: ``saw_body`` -> found_body and ``saw_player``. Heard cues
        # and completed-task inferences surface only in ``rendered_memory_text``.
        observations = _observations_from_memory(memory)

        open_contradictions: tuple[ContradictionView, ...] = ()
        if meeting_entry is not None:
            open_contradictions = tuple(
                _contradiction_view(c)
                for c in meeting_entry.contradictions
                if agent_id in c.subjects
            )

        beliefs = tuple(
            _belief_entry_view(memory, subject, tick)
            for subject in sorted(memory.beliefs.known_players())
        )
        return AgentMemoryView(
            agent_id=agent_id,
            tick=tick,
            role=role,
            tasks_completed=sum(1 for task in owned if task.completed),
            tasks_assigned=len(owned),
            observations=observations,
            beliefs=beliefs,
            open_contradictions=open_contradictions,
            rendered_memory_text=render_for_prompt(
                memory, token_budget=DEFAULT_TOKEN_BUDGET
            ),
        )

    def _metadata_view(self, path: Path, seed: int) -> ReplayMetadataView:
        entries = read_all_entries(path)
        tick_count = sum(1 for e in entries if isinstance(e, ReplayEntry))
        meeting_entries = [e for e in entries if isinstance(e, MeetingReplayEntry)]
        game_end: GameEndReplayEntry | None = None
        for entry in entries:
            if isinstance(entry, GameEndReplayEntry):
                game_end = entry

        prompt_versions: dict[str, str] = {}
        for meeting in meeting_entries:
            prompt_versions.update(meeting.prompt_versions)

        return ReplayMetadataView(
            game_id=_game_id_for_seed(seed),
            seed=seed,
            total_ticks=tick_count,
            winner=game_end.winner if game_end is not None else None,
            winner_reason=game_end.reason if game_end is not None else None,
            meeting_count=len(meeting_entries),
            total_cost_usd=compute_cost_usd(path),
            prompt_versions=prompt_versions,
            created_at=_iso_mtime(path),
        )

    def _players_view(self, initial_state: WorldState) -> tuple[PlayerView, ...]:
        return tuple(
            PlayerView(
                agent_id=pid,
                display_name=_display_name(pid),
                role=initial_state.players[pid].role,
                color=_color_for(pid),
            )
            for pid in sorted(initial_state.players)
        )

    def _build_map_view(self) -> MapLayoutView:
        rooms = tuple(
            RoomView(
                id=room.id,
                name=room.name,
                position=PositionView(
                    x=float(room.position.x), y=float(room.position.y)
                ),
                size=SizeView(
                    width=float(room.size.width), height=float(room.size.height)
                ),
            )
            for room in sorted(self._game_map.rooms.values(), key=lambda r: r.id)
        )
        vents = tuple(
            VentView(
                id=vent.id,
                room_id=vent.room,
                connected_room_ids=tuple(
                    self._game_map.vents[connected].room
                    for connected in vent.connects_to
                ),
            )
            for vent in sorted(self._game_map.vents.values(), key=lambda v: v.id)
        )
        edges = tuple(
            EdgeView(
                from_room_id=edge.from_room,
                to_room_id=edge.to_room,
                is_door=edge.kind == "doorway",
            )
            for edge in self._game_map.edges
        )
        return MapLayoutView(rooms=rooms, vents=vents, edges=edges)

    # -- path / seed helpers ----------------------------------------------

    def _replay_paths(self) -> list[tuple[int, Path]]:
        if not self._replay_dir.exists():
            return []
        pairs: list[tuple[int, Path]] = []
        for path in self._replay_dir.glob("replay-seed-*.jsonl"):
            if not path.is_file():
                continue
            seed = _parse_seed_from_filename(path.name)
            if seed is None:
                continue
            pairs.append((seed, path))
        # Sort by (seed, filename) and keep one canonical file per seed. Two
        # filenames can map to the same seed (e.g. ``replay-seed-1`` vs
        # ``replay-seed-01``); deduplicating with a deterministic tie-break (the
        # lexicographically-first filename) keeps ``game_id`` unique in
        # ``list_replays`` and makes ``_resolve_path`` pick the same file across
        # runs despite ``Path.glob`` having unspecified order.
        pairs.sort(key=lambda pair: (pair[0], pair[1].name))
        deduped: list[tuple[int, Path]] = []
        seen: set[int] = set()
        for seed, path in pairs:
            if seed in seen:
                continue
            seen.add(seed)
            deduped.append((seed, path))
        return deduped

    def _resolve_path(self, game_id: str) -> Path | None:
        # Resolve by matching the discovered seed rather than reconstructing the
        # canonical filename, so a file `list_replays` advertised (e.g. a
        # zero-padded `replay-seed-01.jsonl` surfaced as `headless-seed-1`) is
        # always fetchable by the game_id it was advertised under.
        seed = _parse_seed_from_game_id(game_id)
        if seed is None:
            return None
        for found_seed, path in self._replay_paths():
            if found_seed == seed:
                return path
        return None


# ---------------------------------------------------------------------------
# Module-level helpers (pure; no loader state)
# ---------------------------------------------------------------------------


def _game_id_for_seed(seed: int) -> str:
    return f"headless-seed-{seed}"


def _meeting_id_for(game_id: str, index: int) -> str:
    return f"{game_id}:meeting-{index}"


def _parse_seed_from_game_id(game_id: str) -> int | None:
    match = _GAME_ID_PATTERN.fullmatch(game_id)
    return int(match.group(1)) if match is not None else None


def _parse_seed_from_filename(name: str) -> int | None:
    match = _FILENAME_PATTERN.fullmatch(name)
    return int(match.group(1)) if match is not None else None


def _display_name(agent_id: str) -> str:
    match = _PLAYER_ID_PATTERN.fullmatch(agent_id)
    return f"Player {match.group(1)}" if match is not None else agent_id


def _color_for(agent_id: str) -> str:
    match = _PLAYER_ID_PATTERN.fullmatch(agent_id)
    if match is not None:
        return _COLOR_PALETTE[(int(match.group(1)) - 1) % len(_COLOR_PALETTE)]
    return "#" + hashlib.sha256(agent_id.encode("utf-8")).hexdigest()[:6]


def _iso_mtime(path: Path) -> str | None:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()


def _deserialize_actions(raw_actions: Sequence[Mapping[str, Any]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _infer_num_players(replay_entries: Sequence[ReplayEntry]) -> int:
    """Recover the player count from the recorded action stream.

    The replay format does not persist the roster (only the seed, via
    ``game_id``), and producers accept non-default ``--num-players``. The seeder
    names players ``p-1 .. p-{num_players}`` and the orchestrator solicits one
    action per alive agent every tick, so a real game's actions name every
    player; the max ``p-N`` index across all recorded actions therefore recovers
    ``num_players``. Falls back to :data:`DEFAULT_NUM_PLAYERS` when no actions
    were recorded (e.g. a synthetic no-op replay). ``num_impostors`` is not
    inferable and stays pinned to the MVP-invariant default (DESIGN.md §8.1/§8.2:
    one impostor). A wrong inference cannot corrupt output: the per-tick
    state-hash check fails loud instead.
    """

    max_index = 0
    for entry in replay_entries:
        for raw_action in entry.actions:
            actor = raw_action.get("actor")
            if not isinstance(actor, str):
                continue
            match = _PLAYER_ID_PATTERN.fullmatch(actor)
            if match is not None:
                max_index = max(max_index, int(match.group(1)))
    return max_index if max_index > 0 else DEFAULT_NUM_PLAYERS


def _meeting_trigger_from_events(
    events: Sequence[EngineEvent],
) -> tuple[_TriggerKind, str | None]:
    trigger_event: MeetingTriggeredEvent | None = None
    for event in events:
        if isinstance(event, MeetingTriggeredEvent):
            trigger_event = event
    if trigger_event is None:
        raise RuntimeError(
            "engine entered MEETING phase without a MeetingTriggered event"
        )
    if trigger_event.trigger == "report":
        return "body", trigger_event.body_id
    return "emergency", None


def _meeting_result_from_entry(entry: MeetingReplayEntry) -> MeetingResult:
    return MeetingResult(
        meeting_id=entry.meeting_id,
        triggered_by=entry.triggered_by,
        trigger_tick=entry.tick,
        outcome=entry.outcome,
        ejected_player_id=entry.ejected_player_id,
        ballots=entry.ballots,
        contradictions=entry.contradictions,
        transcript=entry.transcript,
    )


def _current_action(
    last_action: Action | None,
) -> Literal["IDLE", "MOVING", "TASK", "KILL", "VENT", "REPORT", "SABOTAGE"]:
    if last_action is None:
        return "IDLE"
    kind = last_action.type
    if kind == "move":
        return "MOVING"
    if kind == "do_task":
        return "TASK"
    if kind == "kill":
        return "KILL"
    if kind == "vent":
        return "VENT"
    if kind in ("report", "emergency"):
        return "REPORT"
    if kind == "sabotage":
        return "SABOTAGE"
    if kind == "repair_sabotage":
        return "TASK"
    return "IDLE"


def _observations_from_memory(
    memory: AgentMemory,
) -> tuple[SawPlayerView | CompletedTaskObsView | FoundBodyObsView, ...]:
    """Project an agent's reconstructed episodic memory into observation DTOs.

    Only the two episodic event types that map onto the structured-claim union
    are surfaced: ``saw_body`` -> :class:`FoundBodyObsView` (deduplicated by
    body id, as the renderer does) and ``saw_player`` -> :class:`SawPlayerView`.
    Salience order matches DESIGN.md §6.2: body discoveries first, then
    sightings; within each group, most-recent tick first. ``co_present`` is not
    captured per-sighting in the episodic store, so it is left empty.
    """

    found: list[FoundBodyObsView] = []
    seen_bodies: set[str] = set()
    sightings: list[SawPlayerView] = []
    for event in memory.episodic.recent(since_tick=0):
        if event.type == EVENT_SAW_BODY:
            body_id = event.payload.get("body_id")
            victim = event.payload.get("victim_id")
            room = event.payload.get("room")
            if not (
                isinstance(body_id, str)
                and isinstance(victim, str)
                and isinstance(room, str)
            ):
                continue
            if body_id in seen_bodies:
                continue
            seen_bodies.add(body_id)
            found.append(
                FoundBodyObsView(
                    type="found_body", tick=event.tick, body_of=victim, room=room
                )
            )
        elif event.type == EVENT_SAW_PLAYER:
            subject = event.payload.get("player_id")
            room = event.payload.get("room")
            if not (isinstance(subject, str) and isinstance(room, str)):
                continue
            sightings.append(
                SawPlayerView(
                    type="saw_player",
                    tick=event.tick,
                    subject=subject,
                    room=room,
                    co_present=(),
                )
            )
    found.sort(key=lambda obs: obs.tick, reverse=True)
    sightings.sort(key=lambda obs: obs.tick, reverse=True)
    return (*found, *sightings)


def _observation_claim_view(
    claim: ObservationClaim,
) -> SawPlayerView | CompletedTaskObsView | FoundBodyObsView:
    if isinstance(claim, SawPlayerObservation):
        return SawPlayerView(
            type="saw_player",
            tick=claim.tick,
            subject=claim.subject,
            room=claim.room,
            co_present=tuple(claim.co_present),
        )
    if isinstance(claim, CompletedTaskObservation):
        return CompletedTaskObsView(
            type="completed_task",
            tick=claim.tick,
            task_id=claim.task_id,
            room=claim.room,
        )
    if isinstance(claim, FoundBodyObservation):
        return FoundBodyObsView(
            type="found_body",
            tick=claim.tick,
            body_of=claim.body_of,
            room=claim.room,
        )
    raise TypeError(f"unsupported observation claim: {type(claim).__name__}")


def _statement_claim_view(
    claim: Claim,
) -> AlibiClaimView | AccusationClaimView | CorroborationClaimView:
    if isinstance(claim, AlibiClaim):
        return AlibiClaimView(
            type="alibi",
            subject=claim.subject,
            from_tick=claim.from_tick,
            to_tick=claim.to_tick,
            room=claim.room,
            evidence=tuple(claim.evidence),
        )
    if isinstance(claim, AccusationClaim):
        return AccusationClaimView(
            type="accusation",
            against=claim.against,
            confidence=claim.confidence,
            reason=claim.reason,
        )
    if isinstance(claim, CorroborationClaim):
        return CorroborationClaimView(
            type="corroboration",
            supports=claim.supports,
            on_tick=claim.on_tick,
            reason=claim.reason,
        )
    raise TypeError(f"unsupported statement claim: {type(claim).__name__}")


def _report_view(report: ReportDocument) -> ReportView:
    return ReportView(
        agent_id=report.agent_id,
        tick=report.tick,
        observations=tuple(_observation_claim_view(o) for o in report.observations),
        claims=tuple(_statement_claim_view(c) for c in report.claims),
        free_text=report.free_text,
    )


def _statement_view(statement: Statement) -> StatementView:
    return StatementView(
        statement_id=statement.statement_id,
        speaker=statement.speaker,
        tick=statement.tick,
        round_index=statement.round_index,
        target=statement.target,
        claims=tuple(_statement_claim_view(c) for c in statement.claims),
        free_text=statement.free_text,
    )


def _contradiction_view(contradiction: ContradictionRef) -> ContradictionView:
    return ContradictionView(
        contradiction_id=contradiction.contradiction_id,
        kind=contradiction.kind,
        event_a_id=contradiction.event_a_id,
        event_b_id=contradiction.event_b_id,
        subjects=tuple(contradiction.subjects),
        description=contradiction.description,
    )


def _ballot_view(ballot: VoteBallot) -> BallotView:
    return BallotView(
        voter=ballot.voter,
        target=ballot.target,
        confidence=ballot.confidence,
        primary_reason_id=ballot.primary_reason_id,
        considered_alternatives=tuple(ballot.considered_alternatives),
        rationale_text=ballot.rationale_text,
    )


def _failed_call_view(entry: FailedCallReplayEntry) -> FailedCallView:
    return FailedCallView(
        meeting_id=entry.meeting_id,
        tick=entry.tick,
        model=entry.model,
        cost_usd=entry.cost_usd,
        error_type=entry.error_type,
        error_message=entry.error_message[:200],
    )


def _llm_call_view(
    call: LLMCallRecord, prompt_versions: Mapping[str, str]
) -> LLMCallView:
    return LLMCallView(
        call_kind=call.call_kind,
        model=call.model,
        prompt_template_id=_classify_template_id(call, prompt_versions),
        prompt_text=call.prompt,
        response_text=call.response_text,
        input_tokens=call.input_tokens,
        output_tokens=call.output_tokens,
        cost_usd=call.cost_usd,
        agent_id=call.agent_id,
    )


def _classify_template_id(
    call: LLMCallRecord, prompt_versions: Mapping[str, str]
) -> str:
    """Best-effort template id for one captured LLM call.

    ``LLMCallRecord`` does not persist which prompt template produced a call, so
    the template is inferred from stable markers in the (frozen) rendered prompt
    bodies and mapped to the recorded ``prompt_versions``. Falls back to the
    ``call_kind`` tier when the marker set does not match.
    """

    if call.call_kind == "trigger":
        return "trigger"
    prompt = call.prompt
    if "ReportDocument" in prompt:
        key = (
            "impostor_report"
            if "role for this match is IMPOSTOR" in prompt
            else "crewmate_report"
        )
    elif "casting a vote" in prompt:
        key = "vote_ballot"
    elif "accusation round" in prompt:
        key = "accusation_round"
    else:
        return call.call_kind
    return prompt_versions.get(key, key)


def _belief_entry_view(memory: AgentMemory, subject: str, tick: int) -> BeliefEntryView:
    belief = memory.beliefs.view(subject)
    return BeliefEntryView(
        subject=subject,
        suspicion=belief.suspicion,
        confidence=min(1.0, abs(belief.suspicion - 0.5) * 2.0),
        snapshot_tick=tick,
    )


def get_replay_loader(request: Request) -> ReplayLoader:
    """FastAPI dependency: the process-wide loader stored on ``app.state``."""

    loader = request.app.state.replay_loader
    if not isinstance(loader, ReplayLoader):
        raise RuntimeError("ReplayLoader is not configured on app.state")
    return loader


__all__ = ["ReplayLoader", "ReplayStateMismatchError", "get_replay_loader"]
