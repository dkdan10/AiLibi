"""Per-episode rollout records + behavioral descriptors.

The training env (:mod:`training.env`) drives the REAL production loop
(:class:`orchestrator.game.HeadlessGame`) and writes a replay. This module turns
one such replay back into a TYPED :class:`EpisodeRollout`: a re-seeded,
state-hash-verified walk over the recorded actions through
:func:`engine.tick.advance_tick` (and, on a meeting tick,
:func:`orchestrator.game.apply_meeting_result`) that recovers the typed engine
event log, per-tick engine-state scalars, and the behavioral descriptors the QD
entrant and the pause audit need.

Why reconstruct rather than parse the replay bytes: the recorded actions are the
ground truth of what happened, but the reward-source events
(``KilledEvent.witnesses``, ``TaskProgressed``, vent events, meeting triggers,
the terminal ``GameOverEvent``) are NOT in the replay rows — only the submitted
actions and the per-tick ``state_hash`` are (``orchestrator/replay.py``). Feeding
the recorded actions back through the pure engine re-derives the exact typed
events (the engine is a deterministic function of state + actions, DESIGN.md §0),
so :class:`training.rewards.ShapedReward` scores from the TYPED log and a trainer
never re-derives rewards from replay bytes. Roles come from the re-seeded state
(replays are role-free by firewall design), never from the replay.

Episode horizon: a meeting runner is ALWAYS installed by the env, so
``meeting_runner=None`` truncation (``MEETING_PHASE_REACHED``) is structurally
unreachable. ``full_game`` is the one episode boundary: such an episode is
``truncated`` only when the game never reached ``GAME_OVER`` — the tick budget
capped it, and a capped game writes no ``game_over`` row. Truncation is never
SILENT, and the mechanism that enforces that is named: a replay recording a
``game_over`` winner the reconstruction never reaches raises
:class:`RolloutReconstructionError` rather than returning a ``TICK_BUDGET``
episode, and :func:`EpisodeRollout.complete` (``winner is not None and not
truncated``) is the single gate the reward channel reads, so no fitness term
ever scores a truncated episode as a full game.

Provenance: introduced by Task 15.8; Task 19.19 retired the ``first_meeting``
boundary, leaving ``full_game`` alone.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeAlias, get_args

import numpy as np
from numpy.typing import NDArray
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import (
    EngineEvent,
    GameOverEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import advance_tick
from engine.world import Map, WorldState
from meetings.schemas import MeetingOutcome, MeetingResult
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    WinnerSide,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

# The full-game boundary (Task 15.8); the ``first_meeting`` opt-in retired at
# Task 19.19 with no production caller. Kept as a named alias — every caller
# passes it explicitly, and ``_validate_episode_boundary`` still fails loud.
EpisodeBoundary: TypeAlias = Literal["full_game"]

# The runtime-valid boundary set, derived from the Literal so it never drifts.
_VALID_EPISODE_BOUNDARIES: frozenset[str] = frozenset(get_args(EpisodeBoundary))


def _validate_episode_boundary(boundary: str) -> None:
    """Fail loud on an unknown ``episode_boundary`` (AGENTS.md no silent fallbacks).

    ``episode_boundary`` gates whether an episode is scoreable as a full game, so
    a typo arriving from config/CLI (``"fullgame"``) must NOT fall through to the
    full-game path and silently mark an unintended episode complete."""

    if boundary not in _VALID_EPISODE_BOUNDARIES:
        raise ValueError(
            f"unknown episode_boundary {boundary!r}; expected one of "
            f"{sorted(_VALID_EPISODE_BOUNDARIES)}"
        )


# Terminal shape of one episode. ``TICK_BUDGET`` marks an episode the scheduler
# capped before ``GAME_OVER``; it is non-terminal for fitness.
EpisodeOutcome: TypeAlias = Literal["CREWMATES", "IMPOSTORS", "TICK_BUDGET"]

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# The behavioral-descriptor vector's fixed column order (the QD map's feature
# axes). Stable so a downstream reader indexes by position, not by dict order;
# :meth:`BehavioralDescriptors.vector` builds the vector in this order.
DESCRIPTOR_VECTOR_FIELDS: tuple[str, ...] = (
    "kill_count",
    "witness_exposure_rate",
    "vent_usage",
    "meeting_count",
    "meeting_trigger_rate",
    "do_task_emissions",
    "do_task_cadence",
    "median_kill_tick",
)


class RolloutReconstructionError(RuntimeError):
    """Raised when a replay fails to reconstruct byte-identically.

    A per-tick ``state_hash`` (or a meeting row's ``state_hash_before`` /
    ``state_hash_after``) disagreeing with the engine reconstruction means the
    replay is corrupted, drifted, or was recorded under a different roster /
    engine — a fitness number computed off it would be silently wrong, so the
    walk fails loud (AGENTS.md "no silent fallbacks") instead of measuring a
    drifted stream.
    """


@dataclass(frozen=True)
class EpisodeFrame:
    """Engine-state scalars at one reconstructed step (Task 15.8).

    The frame chain opens with ONE ``kind="initial"`` frame for the seeded
    pre-action state s0 (so the potential series starts at Φ(s0) and the shaping
    telescopes over the ACTUAL episode from the real start), then one frame per
    ``advance_tick`` (``kind="tick"``) plus one per applied meeting
    (``kind="meeting"``, carrying the post-``apply_meeting_result`` state, stamped
    with the RESUMED tick ``trigger_tick + 1``). The scalars are exactly what the
    potential-based reward channel's side-specific potential Φ reads
    (:mod:`training.rewards`) — no float belief state, so the potential is a pure
    integer/ratio function and the telescoping identity is exact.

    ``state_hash`` is the recorded, verified hash for this step; the ordered
    tuple of frame hashes is the byte-determinism chain the env's frozen-policy
    test pins. Only ``kind="tick"`` frames correspond to recorded replay tick
    rows (the ``initial`` / ``meeting`` frames have no tick row).
    """

    tick: int
    kind: Literal["initial", "tick", "meeting"]
    phase: Literal["PLAY", "MEETING", "GAME_OVER"]
    state_hash: str
    tasks_completed: int
    tasks_total: int
    alive_crew: int
    alive_impostors: int
    cumulative_kills: int
    # Whether a living, non-vented crewmate shared a room with a living,
    # non-vented impostor this step — the engine-truth basis of the crew's
    # buddy/patrol-coverage reward (:mod:`training.rewards`). Trivially True at
    # spawn / meeting-room resumption, so the reward reads it only on genuine
    # ``kind="tick"`` PLAY frames.
    crew_shadowing_impostor: bool = False


@dataclass(frozen=True)
class MeetingRecord:
    """One resolved (or truncated-at) meeting in an episode (Task 15.8)."""

    tick: int
    meeting_id: str
    trigger: Literal["report", "emergency"]
    triggered_by: PlayerId
    outcome: MeetingOutcome | None
    ejected_player_id: PlayerId | None


@dataclass(frozen=True)
class BehavioralDescriptors:
    """The named behavioral descriptors the QD entrant + pause audit need (15.8).

    Every field named in the task contract: ``kill_ticks`` (kill-timing
    distribution), ``witness_exposure_rate`` (fraction of impostor kills the crew
    witnessed, via ``KilledEvent.witnesses``), ``vent_usage``, ``meeting_count`` /
    ``meeting_trigger_rate``, ``do_task_emissions`` / ``do_task_cadence`` (the
    ``do_task`` submission cadence — includes the impostor's engine-rejected
    pretend ``do_task`` camouflage, counted from submitted actions), and
    ``win_shape``. :meth:`vector` projects the numeric descriptors into a fixed-
    order numpy feature vector for the QD map.
    """

    kill_ticks: tuple[int, ...]
    witness_exposure_rate: float
    vent_usage: int
    meeting_count: int
    meeting_trigger_rate: float
    do_task_emissions: int
    do_task_cadence: float
    win_shape: str

    @property
    def kill_count(self) -> int:
        return len(self.kill_ticks)

    @property
    def median_kill_tick(self) -> float:
        """Median resolved-kill tick (0.0 when no kills landed).

        The kill-timing distribution's central tendency, computed with numpy so
        the QD descriptor axis matches the rest of the training-side math (numpy
        is training-confined, DESIGN.md locked dependency posture)."""

        if not self.kill_ticks:
            return 0.0
        return float(np.median(np.asarray(self.kill_ticks, dtype=np.float64)))

    def vector(self) -> NDArray[np.float64]:
        """Fixed-order numeric feature vector for the QD map (numpy lands here).

        Built in :data:`DESCRIPTOR_VECTOR_FIELDS` order, so the constant is the
        single source of truth for the axis layout downstream QD code indexes by.
        """

        return np.asarray(
            [float(getattr(self, name)) for name in DESCRIPTOR_VECTOR_FIELDS],
            dtype=np.float64,
        )


@dataclass(frozen=True)
class EpisodeRollout:
    """One reconstructed, typed episode record (Task 15.8 public type).

    Carries the typed engine event log, per-step engine-state frames, meeting
    records, the roster's roles (from the re-seeded state), the terminal shape,
    and the behavioral descriptors. Downstream trainers import THIS — never the
    replay bytes. Signature is stable per the task contract.

    A frozen dataclass (not a Pydantic model) for the same reason the
    orchestrator's own in-memory result bundles
    (:class:`orchestrator.game.MeetingArtifacts` /
    :class:`~orchestrator.game.HeadlessGameResult`) are: it is a computation
    result held in-process and it CARRIES engine ``EngineEvent`` frozen
    dataclasses (AGENTS.md reserves Pydantic for serialized/boundary DTOs like
    the replay entries, and frozen dataclasses for engine state — a Pydantic
    model wrapping a tuple of engine dataclasses would re-validate already-valid
    engine truth). :meth:`__post_init__` enforces the terminal-shape invariant so
    an inconsistent record still fails loud at construction.
    """

    seed: int
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    episode_boundary: EpisodeBoundary
    truncated: bool
    outcome: EpisodeOutcome
    winner: WinnerSide | None
    win_reason: str | None
    final_tick: int
    roles: Mapping[PlayerId, Role]
    frames: tuple[EpisodeFrame, ...]
    events: tuple[EngineEvent, ...]
    meetings: tuple[MeetingRecord, ...]
    descriptors: BehavioralDescriptors

    def __post_init__(self) -> None:
        # Fail loud on an inconsistent terminal shape (AGENTS.md no silent
        # fallbacks): a truncated / non-terminal episode must carry no winner, a
        # completed one must carry a winner matching its outcome. This makes an
        # invalid rollout record unconstructable, so it can never be scored.
        if self.truncated and (self.winner is not None or self.win_reason is not None):
            raise ValueError(
                "truncated EpisodeRollout must have winner=None and "
                f"win_reason=None (got winner={self.winner!r})"
            )
        if self.outcome in ("CREWMATES", "IMPOSTORS"):
            if self.truncated or self.winner != self.outcome:
                raise ValueError(
                    f"terminal outcome {self.outcome!r} requires winner=={self.outcome!r}"
                    f" and truncated=False (got winner={self.winner!r}, "
                    f"truncated={self.truncated})"
                )
        elif self.winner is not None or not self.truncated:
            # TICK_BUDGET is non-terminal: no winner, truncated.
            raise ValueError(
                f"non-terminal outcome {self.outcome!r} requires winner=None and "
                f"truncated=True (got winner={self.winner!r}, "
                f"truncated={self.truncated})"
            )

    @property
    def state_hashes(self) -> tuple[str, ...]:
        """The ordered per-step state-hash chain (byte-determinism pin)."""

        return tuple(frame.state_hash for frame in self.frames)

    @property
    def complete(self) -> bool:
        """Whether this episode is a scoreable FULL game (Task 15.8).

        The single gate the reward channel reads: a terminal winner AND not
        truncated. A tick-budget-capped episode is NOT complete — so no fitness
        term ever scores a truncated episode as a full game.
        """

        return self.winner is not None and not self.truncated

    def impostor_ids(self) -> tuple[PlayerId, ...]:
        return tuple(
            sorted(pid for pid, role in self.roles.items() if role == "IMPOSTOR")
        )

    def crew_ids(self) -> tuple[PlayerId, ...]:
        return tuple(
            sorted(pid for pid, role in self.roles.items() if role == "CREWMATE")
        )


def _deserialize_actions(raw_actions: Sequence[Mapping[str, object]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _count_do_task_submissions(raw_actions: Sequence[Mapping[str, object]]) -> int:
    """Count submitted ``do_task`` actions this tick (the camouflage cadence).

    Reads the SUBMITTED actions, so an impostor's engine-rejected pretend
    ``do_task`` (it owns no instance) is counted exactly like a crew task — the
    ``action="task"`` camouflage the observation service renders to witnesses
    (Task 15.8; ``observation/service.py``). Counting resolved task events would
    silently drop the 396 pretend submissions in the committed baseline-2 stream.
    """

    return sum(1 for raw in raw_actions if raw.get("type") == "do_task")


def _crew_shadows_impostor(state: WorldState, roles: Mapping[PlayerId, Role]) -> bool:
    """Whether a living, non-vented crewmate shares a room with an impostor.

    The engine-truth basis of the crew's buddy/patrol-coverage reward: a crew
    member co-located with a suspect's ACTUAL position (the impostor) is covering
    it, deterring the kill — the intended shadowing behavior, rewardable without
    reconstructing agent belief state. Vented players are excluded (a vented
    impostor is hidden; a vented crew is not patrolling)."""

    impostor_rooms = {
        player.room
        for pid, player in state.players.items()
        if player.alive and not player.in_vent and roles.get(pid) == "IMPOSTOR"
    }
    if not impostor_rooms:
        return False
    return any(
        player.alive
        and not player.in_vent
        and roles.get(pid) == "CREWMATE"
        and player.room in impostor_rooms
        for pid, player in state.players.items()
    )


def _frame(
    state: WorldState,
    *,
    tick: int,
    kind: Literal["initial", "tick", "meeting"],
    state_hash: str,
    roles: Mapping[PlayerId, Role],
    cumulative_kills: int,
) -> EpisodeFrame:
    tasks_completed = sum(1 for task in state.tasks.values() if task.completed)
    alive_crew = sum(
        1
        for pid, player in state.players.items()
        if player.alive and roles.get(pid) == "CREWMATE"
    )
    alive_impostors = sum(
        1
        for pid, player in state.players.items()
        if player.alive and roles.get(pid) == "IMPOSTOR"
    )
    return EpisodeFrame(
        tick=tick,
        kind=kind,
        phase=state.phase,
        state_hash=state_hash,
        tasks_completed=tasks_completed,
        tasks_total=len(state.tasks),
        alive_crew=alive_crew,
        alive_impostors=alive_impostors,
        cumulative_kills=cumulative_kills,
        crew_shadowing_impostor=_crew_shadows_impostor(state, roles),
    )


def crew_witnesses(
    event: KilledEvent, roles: Mapping[PlayerId, Role]
) -> tuple[PlayerId, ...]:
    """The CREWMATE witnesses of a kill (Task 15.8).

    ``KilledEvent.witnesses`` (``engine/rules.py`` ``_witnesses_in_room``) excludes
    only the killer and the victim, so in a multi-impostor game it can include a
    co-located FELLOW impostor — who generates NO crew testimony (a teammate never
    reports its own team). "Witnessed-ness" in the training-signal doctrine is
    about crew EVIDENCE, so both the ``witness_exposure_rate`` descriptor and the
    reward channel's un-witnessed-ness term count only crew witnesses; a kill seen
    solely by a teammate is un-witnessed from the crew's (deduction) perspective.
    """

    return tuple(
        witness for witness in event.witnesses if roles.get(witness) == "CREWMATE"
    )


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


def _build_descriptors(
    *,
    events: Sequence[EngineEvent],
    meetings: Sequence[MeetingRecord],
    do_task_emissions: int,
    final_tick: int,
    roles: Mapping[PlayerId, Role],
    outcome: EpisodeOutcome,
    winner: WinnerSide | None,
    win_reason: str | None,
) -> BehavioralDescriptors:
    kill_ticks = tuple(event.tick for event in events if isinstance(event, KilledEvent))
    kills = [event for event in events if isinstance(event, KilledEvent)]
    # CREW-witnessed only: a kill seen solely by a fellow impostor generated no
    # crew evidence and is not "exposure" (see :func:`crew_witnesses`).
    witnessed = sum(1 for event in kills if crew_witnesses(event, roles))
    witness_exposure_rate = witnessed / len(kills) if kills else 0.0
    vent_usage = sum(
        1
        for event in events
        if isinstance(event, (VentEnteredEvent, VentExitedEvent))
        and roles.get(event.actor) == "IMPOSTOR"
    )
    denominator = max(1, final_tick)
    meeting_count = len(meetings)
    if winner is not None:
        win_shape = f"{winner}:{win_reason}" if win_reason else winner
    else:
        win_shape = outcome
    return BehavioralDescriptors(
        kill_ticks=kill_ticks,
        witness_exposure_rate=witness_exposure_rate,
        vent_usage=vent_usage,
        meeting_count=meeting_count,
        meeting_trigger_rate=meeting_count / denominator,
        do_task_emissions=do_task_emissions,
        do_task_cadence=do_task_emissions / denominator,
        win_shape=win_shape,
    )


def reconstruct_episode(
    replay_path: Path,
    *,
    game_map: Map,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    episode_boundary: EpisodeBoundary = "full_game",
) -> EpisodeRollout:
    """Re-seed + replay one recorded game into a typed :class:`EpisodeRollout`.

    Mirrors the ``api/replay_loader.py::_walk`` / ``eval.funnel._walk_game``
    reconstruction recipe (never importing the API-tier loader): re-seed, feed
    the recorded actions through :func:`engine.tick.advance_tick`, verify every
    ``state_hash``, and on a MEETING tick rebuild the
    :class:`~meetings.schemas.MeetingResult` from the recorded meeting row and
    apply it via :func:`orchestrator.game.apply_meeting_result` (verifying
    ``state_hash_after``). The typed events, per-step frames, and descriptors are
    collected along the way.

    ``episode_boundary`` is ``"full_game"`` — the only boundary since Task 19.19
    retired the unused ``first_meeting`` opt-in. It is still an explicit
    parameter (every caller passes it) and still validated, so an unknown value
    fails loud rather than falling back.
    """

    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }
    game_end = next(
        (entry for entry in entries if isinstance(entry, GameEndReplayEntry)), None
    )

    _validate_episode_boundary(episode_boundary)

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    roles: dict[PlayerId, Role] = {
        pid: player.role for pid, player in state.players.items()
    }

    events: list[EngineEvent] = []
    meetings: list[MeetingRecord] = []
    cumulative_kills = 0
    do_task_emissions = 0
    winner: WinnerSide | None = None
    win_reason: str | None = None
    truncated = False
    outcome: EpisodeOutcome
    final_tick = 0

    # The seeded pre-action state s0 opens the frame chain so the potential
    # series starts at Φ(s0): the shaping then telescopes over the ACTUAL episode
    # from the real start, and a first-tick change to the potential (an immediate
    # kill / task progress) is scored identically to the same change later. It is
    # kind="initial" (not "tick"): the seeded state has no recorded replay tick
    # row, so it is excluded from the tick-hash chain that maps to the replay.
    frames: list[EpisodeFrame] = [
        _frame(
            state,
            tick=state.tick,
            kind="initial",
            state_hash=_state_hash(state),
            roles=roles,
            cumulative_kills=cumulative_kills,
        )
    ]

    for entry in tick_entries:
        do_task_emissions += _count_do_task_submissions(entry.actions)
        actions = _deserialize_actions(entry.actions)
        state, tick_events = advance_tick(state, actions, game_map=game_map)
        actual = _state_hash(state)
        if actual != entry.state_hash:
            raise RolloutReconstructionError(
                f"seed {seed}: tick {entry.tick} reconstructed {actual!r} != "
                f"recorded {entry.state_hash!r} (roster mismatch or drift)"
            )
        final_tick = state.tick
        for event in tick_events:
            events.append(event)
            if isinstance(event, KilledEvent):
                cumulative_kills += 1
            elif isinstance(event, GameOverEvent):
                winner = event.winner
                win_reason = event.reason
        frames.append(
            _frame(
                state,
                tick=entry.tick,
                kind="tick",
                state_hash=actual,
                roles=roles,
                cumulative_kills=cumulative_kills,
            )
        )

        if state.phase == "GAME_OVER":
            break
        if state.phase != "MEETING":
            continue

        trigger_event = next(
            (e for e in tick_events if isinstance(e, MeetingTriggeredEvent)), None
        )
        if trigger_event is None:
            raise RolloutReconstructionError(
                f"seed {seed}: tick {entry.tick} entered MEETING with no "
                "MeetingTriggeredEvent in the reconstructed events"
            )
        meeting_entry = meeting_by_tick.get(entry.tick)

        if meeting_entry is None:
            raise RolloutReconstructionError(
                f"seed {seed}: tick {entry.tick} entered MEETING but the replay "
                "carries no meeting row for that tick (partial recording)"
            )
        if meeting_entry.state_hash_before != actual:
            raise RolloutReconstructionError(
                f"seed {seed}: meeting at tick {entry.tick} recorded "
                f"state_hash_before {meeting_entry.state_hash_before!r} != "
                f"reconstructed pre-meeting state {actual!r}"
            )
        result = _meeting_result_from_entry(meeting_entry)
        state, post_events = apply_meeting_result(
            state,
            result,
            game_map=game_map,
            triggering_body_id=trigger_event.body_id,
        )
        after = _state_hash(state)
        if after != meeting_entry.state_hash_after:
            raise RolloutReconstructionError(
                f"seed {seed}: meeting at tick {entry.tick} reconstructed "
                f"{after!r} != recorded {meeting_entry.state_hash_after!r}"
            )
        for event in post_events:
            events.append(event)
            if isinstance(event, GameOverEvent):
                winner = event.winner
                win_reason = event.reason
        meetings.append(
            MeetingRecord(
                tick=entry.tick,
                meeting_id=meeting_entry.meeting_id,
                trigger=trigger_event.trigger,
                triggered_by=meeting_entry.triggered_by,
                outcome=meeting_entry.outcome,
                ejected_player_id=meeting_entry.ejected_player_id,
            )
        )
        final_tick = state.tick
        frames.append(
            _frame(
                state,
                # apply_meeting_result resumes gameplay at trigger_tick + 1, so
                # the post-meeting frame is stamped with the RESUMED state.tick,
                # not the trigger tick — otherwise two frames share the trigger
                # tick and the resumed tick has none (an off-by-one in any
                # time-based feature around meetings).
                tick=state.tick,
                kind="meeting",
                state_hash=after,
                roles=roles,
                cumulative_kills=cumulative_kills,
            )
        )
        if state.phase == "GAME_OVER":
            break

    if winner is not None:
        outcome = winner
    else:
        # No GameOverEvent: the scheduler capped the game. An episode that never
        # terminated is not complete.
        outcome = "TICK_BUDGET"
        truncated = True

    # The recorded game_over row is the producer's claim; the reconstruction is
    # authoritative. A recorded terminal the walk never reaches means trailing
    # tick rows are missing — dropping them shortens the walk without breaking
    # the state-hash chain, so nothing upstream catches it. A legitimate
    # tick-budget cap writes no game_over row at all
    # (orchestrator.game.HeadlessGame), so neither clause can fire on one.
    if game_end is not None and game_end.winner is not None:
        if truncated:
            raise RolloutReconstructionError(
                f"seed {seed}: replay records game_over winner "
                f"{game_end.winner!r} but the reconstructed walk never reached "
                "GAME_OVER (truncated tick stream)"
            )
        if game_end.winner != winner:
            raise RolloutReconstructionError(
                f"seed {seed}: reconstructed winner {winner!r} != recorded "
                f"game_over winner {game_end.winner!r}"
            )

    descriptors = _build_descriptors(
        events=events,
        meetings=meetings,
        do_task_emissions=do_task_emissions,
        final_tick=final_tick,
        roles=roles,
        outcome=outcome,
        winner=winner,
        win_reason=win_reason,
    )

    return EpisodeRollout(
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        episode_boundary=episode_boundary,
        truncated=truncated,
        outcome=outcome,
        winner=None if truncated else winner,
        win_reason=None if truncated else win_reason,
        final_tick=final_tick,
        roles=roles,
        frames=tuple(frames),
        events=tuple(events),
        meetings=tuple(meetings),
        descriptors=descriptors,
    )


__all__ = [
    "DESCRIPTOR_VECTOR_FIELDS",
    "BehavioralDescriptors",
    "EpisodeBoundary",
    "EpisodeFrame",
    "EpisodeOutcome",
    "EpisodeRollout",
    "MeetingRecord",
    "RolloutReconstructionError",
    "reconstruct_episode",
]
