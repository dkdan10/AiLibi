"""Tests for the tactical rollout env + legal-action mask (Task 15.8).

Pins the definition-of-done contract: the env runs full fake-provider games
through the injected factory; the always-installed meeting runner makes
``MEETING_PHASE_REACHED`` truncation structurally unreachable; ``full_game`` is
the one boundary mode (Task 19.19 retired the unused ``first_meeting`` opt-in),
so only a tick-budget cap marks an episode truncated;
the mask is property-tested against the REAL engine (every masked-legal action
resolves, every unmasked action is engine-rejected, and the impostor's pretend
``do_task`` camouflage is carried in the SUBMISSION set but excluded from the
engine-legal set), with the in-vent ruling — ``vent`` and ``wait`` are the only
actions legal from inside a vent — pinned on a hand-built state rather than left
to a sampled rollout; a frozen-policy episode is byte-deterministic; and the
interposition wrapper satisfies the full ``MeetingAwareAgent`` protocol.
"""

from __future__ import annotations

import tempfile
from collections.abc import Iterator, Mapping
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyState, PlayerId, SabotageState
from engine.events import ActionRejectedEvent, MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from meetings.schemas import MeetingResult
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    EmergencyMeetingIntent,
    KillIntent,
    RepairSabotageIntent,
    ReportBodyIntent,
    SabotageIntent,
    VentIntent,
)
from observation.packet import ObservationPacket
from observation.service import ObservationService
from orchestrator.boundary import (
    public_map_from_engine_map,
    translate_action_intent,
)
from orchestrator.game import (
    HeadlessGame,
    MeetingAwareAgent,
    apply_meeting_result,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state
from training.env import (
    ActionMask,
    MaskedDecision,
    TacticalRolloutEnv,
    build_action_mask,
    build_interposition_factory,
)

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

_NUM_PLAYERS = 9
_NUM_IMPOSTORS = 2
_TASKS = 2


def _env(**overrides: object) -> TacticalRolloutEnv:
    kwargs: dict[str, object] = {
        "num_players": _NUM_PLAYERS,
        "num_impostors": _NUM_IMPOSTORS,
        "tasks_per_crewmate": _TASKS,
    }
    kwargs.update(overrides)
    return TacticalRolloutEnv(**kwargs)  # type: ignore[arg-type]


def _engine_rejects(state: WorldState, intent: ActionIntent, game_map: Map) -> bool:
    """Check a public intent through production translation and engine legality."""

    action = translate_action_intent(intent, world_state=state)
    _, events = advance_tick(state, [action], game_map=game_map)
    return any(
        isinstance(event, ActionRejectedEvent) and event.actor == action.actor
        for event in events
    )


def _play_states_with_packets(
    replay_path: Path,
    *,
    game_map: Map,
    seed: int,
) -> Iterator[tuple[WorldState, Mapping[PlayerId, ObservationPacket]]]:
    """Re-walk a recorded game, yielding each PLAY state + its per-agent packets.

    Mirrors the reconstruction walk (advance recorded actions, apply meetings)
    but rebuilds the observation packets the agents actually saw, so the mask can
    be checked against the REAL engine at realistic mid-game states (kills,
    cooldowns, bodies, post-meeting resets).
    """

    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS,
    )
    with tempfile.TemporaryDirectory(prefix="ailibi-mask-test-") as tmp:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(tmp) / "audit.jsonl"
        )
        last_events: tuple[object, ...] = ()
        for entry in tick_entries:
            if state.phase == "PLAY":
                packets = {
                    pid: service.build_packet(
                        world_state=state,
                        agent_id=pid,
                        engine_events=last_events,  # type: ignore[arg-type]
                    )
                    for pid, player in state.players.items()
                    if player.alive
                }
                yield state, packets
            actions = [
                _ACTION_ADAPTER.validate_python(dict(raw)) for raw in entry.actions
            ]
            state, events = advance_tick(state, actions, game_map=game_map)
            if state.phase == "GAME_OVER":
                break
            if state.phase != "MEETING":
                last_events = tuple(events)
                continue
            meeting_entry = meeting_by_tick[entry.tick]
            body_id = next(
                (
                    event.body_id
                    for event in events
                    if isinstance(event, MeetingTriggeredEvent)
                ),
                None,
            )
            result = MeetingResult(
                meeting_id=meeting_entry.meeting_id,
                triggered_by=meeting_entry.triggered_by,
                trigger_tick=meeting_entry.tick,
                outcome=meeting_entry.outcome,
                ejected_player_id=meeting_entry.ejected_player_id,
                ballots=meeting_entry.ballots,
                contradictions=meeting_entry.contradictions,
                transcript=meeting_entry.transcript,
            )
            pre = tuple(events)
            state, post = apply_meeting_result(
                state, result, game_map=game_map, triggering_body_id=body_id
            )
            last_events = pre + tuple(post)
            if state.phase == "GAME_OVER":
                break
        service.close()


# --------------------------------------------------------------------------- #
# Env drives full production games through the injected factory                #
# --------------------------------------------------------------------------- #


def test_env_runs_full_games_through_injected_factory() -> None:
    env = _env()
    rollout = env.rollout(0)
    assert rollout.outcome in ("CREWMATES", "IMPOSTORS")
    assert rollout.complete
    assert rollout.state_hashes  # a non-empty per-tick chain


def test_meeting_runner_always_installed_meeting_phase_unreachable() -> None:
    env = _env()
    # A runner is ALWAYS installed, so the game never returns
    # MEETING_PHASE_REACHED (rollout raises RuntimeError if it ever does).
    assert env._build_meeting_runner() is not None  # noqa: SLF001
    for seed in range(4):
        rollout = env.rollout(seed)
        # full_game is the only boundary, so a terminal (or tick-budget)
        # outcome — never MEETING_PHASE_REACHED.
        assert rollout.outcome in ("CREWMATES", "IMPOSTORS", "TICK_BUDGET")


def test_default_meeting_runner_forces_fake_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Phase-15 self-play stays $0 / offline even in a real-provider shell.

    The default meeting runner forces the deterministic fake client regardless of
    the ambient ``AILIBI_LLM_PROVIDER``, so a rollout never routes a training
    meeting to a paid/network provider unless a caller opts in via
    ``meeting_runner_factory``. Set a real provider (and clear its key): if the
    env leaked to that provider the rollout would fail; forcing fake keeps it
    offline and deterministic.
    """

    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rollout = _env().rollout(0)
    assert rollout.complete
    assert rollout.meetings  # meetings resolved through the forced fake path


def test_env_rejects_unknown_episode_boundary() -> None:
    # A typo from config/CLI must fail loud at construction, not silently run as
    # a full-game episode (which would then be scoreable).
    with pytest.raises(ValueError, match="unknown episode_boundary"):
        TacticalRolloutEnv(episode_boundary="first-meeting")  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Frozen-policy byte determinism                                              #
# --------------------------------------------------------------------------- #


def test_frozen_policy_episode_is_byte_deterministic() -> None:
    env = _env()
    first = env.rollout(5)
    second = env.rollout(5)
    assert first.state_hashes == second.state_hashes
    assert len(first.state_hashes) > 0


def test_identity_selector_is_byte_identical_to_fsm() -> None:
    def identity(decision: MaskedDecision) -> ActionIntent:
        return decision.fsm_intent

    fsm_env = _env()
    selector_env = _env(intent_selector=identity)
    # An identity selector exercises the mask + selector path every tick, yet the
    # recorded stream is byte-identical to pure FSM delegation.
    assert fsm_env.rollout(3).state_hashes == selector_env.rollout(3).state_hashes


# --------------------------------------------------------------------------- #
# The interposition wrapper satisfies the FULL MeetingAwareAgent protocol      #
# --------------------------------------------------------------------------- #


def test_interposed_agent_satisfies_meeting_protocol_and_delegates() -> None:
    env = _env()
    factory = build_interposition_factory(game_map=env.game_map)
    impostor = factory("p2", "IMPOSTOR")
    crewmate = factory("p5", "CREWMATE")
    assert isinstance(impostor, MeetingAwareAgent)
    assert isinstance(crewmate, MeetingAwareAgent)
    # Properties + self-channel accessor delegate to the inner TacticalAgent
    # (isinstance above narrows the wrapper to MeetingAwareAgent).
    assert impostor.agent_id == "p2"
    assert impostor.role == "IMPOSTOR"
    assert impostor.vent_witness_records_for_meeting() == ()
    # A full game with meetings runs end-to-end THROUGH the wrapper (the whole
    # meeting protocol delegates), so the episode carries resolved meetings.
    assert env.rollout(0).meetings


def test_wrapped_fsm_is_byte_identical_to_production_factory() -> None:
    """No drift from the production loop (Task 15.8 integration risk #1).

    With no selector the interposition wrapper is a transparent FSM delegate, so
    the env's recorded stream must be byte-identical to a game run with the
    production ``build_default_agent_factory`` — proving the ONLY interposition is
    at the factory and it never perturbs the real ``HeadlessGame`` loop.
    """

    game_map = load_canonical_map()
    seed = 7
    with tempfile.TemporaryDirectory(prefix="ailibi-prod-") as tmp:
        replay_path = Path(tmp) / "prod.jsonl"
        HeadlessGame(
            seed=seed,
            game_map=game_map,
            agent_factory=build_default_agent_factory(),
            replay_path=replay_path,
            num_players=_NUM_PLAYERS,
            num_impostors=_NUM_IMPOSTORS,
            tasks_per_crewmate=_TASKS,
            scheduler=TickScheduler(max_ticks=1000),
            meeting_runner=build_default_meeting_runner(),
            force=True,
        ).run()
        production_hashes = [
            entry.state_hash
            for entry in read_all_entries(replay_path)
            if isinstance(entry, ReplayEntry)
        ]
    env_tick_hashes = [
        frame.state_hash
        for frame in _env().rollout(seed).frames
        if frame.kind == "tick"
    ]
    assert env_tick_hashes == production_hashes


def test_selector_returning_illegal_intent_raises() -> None:
    def bad_selector(decision: MaskedDecision) -> ActionIntent:
        if decision.mask.illegal:
            return decision.mask.illegal[0]
        return decision.fsm_intent

    env = _env(intent_selector=bad_selector)
    with pytest.raises(ValueError, match="non-submission-legal"):
        env.rollout(0)


def test_masked_legal_selector_produces_a_valid_game() -> None:
    def wait_when_possible(decision: MaskedDecision) -> ActionIntent:
        # Always the FSM choice, but re-validated through the mask — a trivial
        # learned-policy stand-in that only ever emits submission-legal intents.
        assert decision.mask.is_submission_legal(decision.fsm_intent)
        return decision.fsm_intent

    env = _env(intent_selector=wait_when_possible)
    rollout = env.rollout(1)
    assert rollout.outcome in ("CREWMATES", "IMPOSTORS", "TICK_BUDGET")


# --------------------------------------------------------------------------- #
# The mask is property-tested against the REAL engine                          #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("seed", range(8))
def test_mask_legality_against_engine(seed: int) -> None:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    sabotage_kinds = tuple(sorted(game_map.sabotages))
    cap = game_map.emergency.uses_per_player

    checked_legal = 0
    checked_illegal = 0
    submission_only_seen = 0

    with tempfile.TemporaryDirectory(prefix="ailibi-mask-replay-") as tmp:
        env = _env(output_dir=Path(tmp))
        env.rollout(seed)
        replay_path = Path(tmp) / f"replay-seed-{seed}.jsonl"
        for state, packets in _play_states_with_packets(
            replay_path, game_map=game_map, seed=seed
        ):
            for pid, packet in packets.items():
                remaining = cap - state.emergency_uses.get(pid, 0)
                mask = build_action_mask(
                    packet,
                    public_map,
                    sabotage_kinds=sabotage_kinds,
                    emergency_uses_remaining=remaining,
                )
                for intent in mask.engine_legal:
                    assert not _engine_rejects(state, intent, game_map), (
                        f"masked-legal but engine-rejected: {pid} {intent!r}"
                    )
                    checked_legal += 1
                for intent in mask.illegal:
                    assert _engine_rejects(state, intent, game_map), (
                        f"masked-illegal but engine-accepted: {pid} {intent!r}"
                    )
                    checked_illegal += 1
                for intent in mask.submission_only:
                    # Observation-meaningful but engine-rejected (the impostor's
                    # pretend do_task camouflage).
                    assert _engine_rejects(state, intent, game_map)
                    assert mask.is_submission_legal(intent)
                    assert not mask.is_engine_legal(intent)
                    submission_only_seen += 1

    assert checked_legal > 0
    assert checked_illegal > 0
    # Impostors carry a pretend do_task on their self channel from tick 0, so the
    # split vocabulary is exercised.
    assert submission_only_seen > 0


def test_impostor_pretend_do_task_is_submission_only_in_the_task_room() -> None:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    base = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS,
    )
    impostor = next(
        pid for pid, player in base.players.items() if player.role == "IMPOSTOR"
    )
    pending = _packet_for(base, impostor, game_map).self_state.pending_task_id
    assert pending is not None  # an impostor's pretend map task
    task_room = public_map.task_locations[pending]
    pretend = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": impostor, "payload": {"task_id": pending}}
    )

    def _mask_with_impostor_in(room: str, *, in_vent: bool = False) -> ActionMask:
        players = dict(base.players)
        players[impostor] = replace(players[impostor], room=room, in_vent=in_vent)
        state = replace(base, players=players)
        return build_action_mask(
            _packet_for(state, impostor, game_map),
            public_map,
            sabotage_kinds=tuple(sorted(game_map.sabotages)),
            emergency_uses_remaining=game_map.emergency.uses_per_player,
        )

    # In the pretend task's room: the observation-meaningful camouflage submission
    # (engine-rejected, not engine-legal).
    in_room = _mask_with_impostor_in(task_room)
    assert pretend in in_room.submission_only
    assert in_room.is_submission_legal(pretend)
    assert not in_room.is_engine_legal(pretend)
    assert _engine_rejects(base, pretend, game_map)  # no owned instance, any room

    # Elsewhere (a different room, or hidden in a vent): a plain illegal
    # submission, so a selector cannot spam a stationary fake task.
    other_room = next(room for room in public_map.room_ids if room != task_room)
    elsewhere = _mask_with_impostor_in(other_room)
    assert pretend in elsewhere.illegal
    assert not elsewhere.is_submission_legal(pretend)
    vented = _mask_with_impostor_in(task_room, in_vent=True)
    assert pretend in vented.illegal
    assert not vented.is_submission_legal(pretend)


def test_in_vent_impostor_cannot_kill_report_or_sabotage() -> None:
    # The in-vent ruling, pinned on a hand-built state instead of hoping a
    # sampled rollout vents beside a victim: kill, report and sabotage are masked
    # ILLEGAL and the engine agrees on the same state; step the impostor out of
    # the vent with nothing else changed and all three flip to masked LEGAL and
    # engine-accepted, so the pairing is the vent and nothing else.
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    sabotage_kinds = tuple(sorted(game_map.sabotages))
    base = _base_state(game_map)
    impostor = next(
        pid for pid, player in base.players.items() if player.role == "IMPOSTOR"
    )
    victim, corpse = sorted(
        pid for pid, player in base.players.items() if player.role == "CREWMATE"
    )[:2]
    vent_id, room = sorted(public_map.vent_rooms.items())[0]

    players = dict(base.players)
    players[impostor] = replace(players[impostor], room=room, in_vent=True)
    players[victim] = replace(players[victim], room=room, in_vent=False)
    players[corpse] = replace(players[corpse], room=room, alive=False, in_vent=False)
    body = BodyState(
        id=f"body-{corpse}-0",
        player_id=corpse,
        room=room,
        position=(0.0, 0.0),
        killed_by=impostor,
        discovered_by=None,
    )
    vented = replace(
        base,
        players=players,
        bodies={body.id: body},
        cooldowns={**dict(base.cooldowns), impostor: 0},
    )
    standing = replace(
        vented,
        players={**players, impostor: replace(players[impostor], in_vent=False)},
    )

    def _mask(state: WorldState) -> ActionMask:
        return build_action_mask(
            _packet_for(state, impostor, game_map),
            public_map,
            sabotage_kinds=sabotage_kinds,
            emergency_uses_remaining=game_map.emergency.uses_per_player,
        )

    kill = KillIntent.model_validate(
        {"type": "kill", "actor": impostor, "payload": {"target": victim}}
    )
    report = ReportBodyIntent.model_validate(
        {
            "type": "report",
            "actor": impostor,
            "payload": {"body_id": f"body-{corpse}"},
        }
    )
    # The mask consumes public handles; engine legality still uses the actual
    # corpse identity in both states. Translation must not grant permission.
    for state in (vented, standing):
        action = translate_action_intent(report, world_state=state)
        assert action.type == "report"
        assert action.payload.body_id == body.id
    sabotage = SabotageIntent.model_validate(
        {"type": "sabotage", "actor": impostor, "payload": {"kind": sabotage_kinds[0]}}
    )

    vented_mask = _mask(vented)
    for intent in (kill, report, sabotage):
        assert intent in vented_mask.illegal
        assert not vented_mask.is_submission_legal(intent)
        assert _engine_rejects(vented, intent, game_map)

    standing_mask = _mask(standing)
    for intent in (kill, report, sabotage):
        assert intent in standing_mask.engine_legal
        assert not _engine_rejects(standing, intent, game_map)

    # And the ruling is TOTAL on this state: `vent` and `wait` are the only
    # engine-legal intents left, with both mask directions still pinned against
    # the engine.
    assert {intent.type for intent in vented_mask.engine_legal} == {"vent", "wait"}
    assert vent_id in {
        intent.payload.vent_id
        for intent in vented_mask.engine_legal
        if isinstance(intent, VentIntent)
    }
    for legal_intent in vented_mask.engine_legal:
        assert not _engine_rejects(vented, legal_intent, game_map)
    for illegal_intent in vented_mask.illegal:
        assert _engine_rejects(vented, illegal_intent, game_map)


# --------------------------------------------------------------------------- #
# Targeted mask caveats: emergency-uses tracker + sabotage-kind vocabulary     #
# --------------------------------------------------------------------------- #


def _packet_for(
    state: WorldState, agent_id: PlayerId, game_map: Map
) -> ObservationPacket:
    with tempfile.TemporaryDirectory(prefix="ailibi-caveat-") as tmp:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(tmp) / "a.jsonl"
        )
        packet = service.build_packet(
            world_state=state, agent_id=agent_id, engine_events=()
        )
        service.close()
    return packet


def _base_state(game_map: Map) -> WorldState:
    return seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS,
    )


def test_emergency_uses_tracker_is_the_mask_caveat() -> None:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    button_room = game_map.emergency.button_room
    cap = game_map.emergency.uses_per_player
    base = _base_state(game_map)
    actor = min(base.players)

    def _place_in_button_room(uses: int) -> WorldState:
        players = dict(base.players)
        players[actor] = replace(players[actor], room=button_room, in_vent=False)
        return replace(base, players=players, emergency_uses={actor: uses})

    available = _place_in_button_room(0)
    exhausted = _place_in_button_room(cap)
    emergency = EmergencyMeetingIntent(actor=actor, type="emergency")

    mask_available = build_action_mask(
        _packet_for(available, actor, game_map),
        public_map,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_remaining=cap - 0,
    )
    assert emergency in mask_available.engine_legal
    assert not _engine_rejects(available, emergency, game_map)

    mask_exhausted = build_action_mask(
        _packet_for(exhausted, actor, game_map),
        public_map,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_remaining=cap - cap,
    )
    assert emergency in mask_exhausted.illegal
    assert _engine_rejects(exhausted, emergency, game_map)


def test_sabotage_kind_vocabulary_is_the_mask_caveat() -> None:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    sabotage_kinds = tuple(sorted(game_map.sabotages))
    base = _base_state(game_map)
    impostor = next(
        pid for pid, player in base.players.items() if player.role == "IMPOSTOR"
    )
    reactor = game_map.sabotages["reactor"]
    repair_room = reactor.repair_rooms[0]

    # An active reactor sabotage, with the impostor standing in its repair room.
    players = dict(base.players)
    players[impostor] = replace(players[impostor], room=repair_room, in_vent=False)
    active = replace(
        base,
        players=players,
        sabotage=SabotageState(
            kind="reactor",
            remaining_ticks=reactor.duration_ticks,
            affected_rooms=reactor.repair_rooms,
            active=True,
        ),
    )
    mask = build_action_mask(
        _packet_for(active, impostor, game_map),
        public_map,
        sabotage_kinds=sabotage_kinds,
        emergency_uses_remaining=game_map.emergency.uses_per_player,
    )

    # Starting any sabotage is illegal while one is active (both kinds).
    for kind in sabotage_kinds:
        start = SabotageIntent.model_validate(
            {"type": "sabotage", "actor": impostor, "payload": {"kind": kind}}
        )
        assert start in mask.illegal
        assert _engine_rejects(active, start, game_map)

    # Repairing the ACTIVE kind in its repair room is legal; the other kind is not.
    repair_reactor = RepairSabotageIntent.model_validate(
        {"type": "repair_sabotage", "actor": impostor, "payload": {"kind": "reactor"}}
    )
    repair_lights = RepairSabotageIntent.model_validate(
        {"type": "repair_sabotage", "actor": impostor, "payload": {"kind": "lights"}}
    )
    assert repair_reactor in mask.engine_legal
    assert not _engine_rejects(active, repair_reactor, game_map)
    assert repair_lights in mask.illegal
    assert _engine_rejects(active, repair_lights, game_map)


def test_action_mask_split_vocabulary_is_disjoint() -> None:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    state = _base_state(game_map)
    impostor = next(
        pid for pid, player in state.players.items() if player.role == "IMPOSTOR"
    )
    mask = build_action_mask(
        _packet_for(state, impostor, game_map),
        public_map,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_remaining=game_map.emergency.uses_per_player,
    )
    assert isinstance(mask, ActionMask)
    legal = set(map(id, mask.engine_legal))
    # submission_legal is exactly engine_legal + submission_only.
    assert len(mask.submission_legal) == len(mask.engine_legal) + len(
        mask.submission_only
    )
    # An engine-legal action is not simultaneously in the illegal partition.
    for intent in mask.engine_legal:
        assert intent not in mask.illegal
    assert legal  # non-empty (WAIT is always legal)


# --------------------------------------------------------------------------- #
# The initial_state injection seam (Task 18.23)                                #
# --------------------------------------------------------------------------- #


def test_injecting_the_seeded_state_matches_the_seeded_path_exactly() -> None:
    """The seam changes nothing but the SOURCE of s0.

    Injecting exactly the state ``seed_initial_state`` would have produced must
    yield an episode identical to the default seeded no-replay path — frames,
    hash chain, events, meetings, and the derived roster fields alike — so the
    injection path provably shares the whole live-assembly machinery instead of
    forking it.
    """

    env = _env(no_replay=True)
    seeded_state = _base_state(load_canonical_map())
    injected = env.rollout_injected(seeded_state)
    seeded = env.rollout(0)
    assert injected.state_hashes == seeded.state_hashes
    assert injected.frames == seeded.frames
    assert injected.events == seeded.events
    assert injected.meetings == seeded.meetings
    assert injected.descriptors == seeded.descriptors
    assert injected.num_players == seeded.num_players
    assert injected.num_impostors == seeded.num_impostors
    assert injected.tasks_per_crewmate == seeded.tasks_per_crewmate


def test_injected_mid_game_state_opens_the_frame_chain_at_its_tick() -> None:
    state = replace(_base_state(load_canonical_map()), tick=17)
    rollout = _env(no_replay=True).rollout_injected(state)
    assert rollout.seed == 0
    assert rollout.frames[0].kind == "initial"
    assert rollout.frames[0].tick == 17
    assert rollout.num_players == _NUM_PLAYERS
    assert rollout.num_impostors == _NUM_IMPOSTORS
    assert rollout.tasks_per_crewmate == _TASKS


def test_rollout_injected_requires_no_replay() -> None:
    env = _env()  # default: the recording path
    state = _base_state(load_canonical_map())
    with pytest.raises(ValueError, match="no_replay=True"):
        env.rollout_injected(state)


def test_rollout_injected_requires_tick_headroom() -> None:
    state = replace(_base_state(load_canonical_map()), tick=40)
    env = _env(no_replay=True, max_ticks=40)
    with pytest.raises(ValueError, match="max_ticks"):
        env.rollout_injected(state)


def test_headless_game_refuses_initial_state_on_the_recording_path() -> None:
    game_map = load_canonical_map()
    state = _base_state(game_map)
    with tempfile.TemporaryDirectory(prefix="ailibi-inject-") as tmp:
        with pytest.raises(ValueError, match="no-replay training path"):
            HeadlessGame(
                seed=0,
                game_map=game_map,
                agent_factory=build_default_agent_factory(),
                replay_path=Path(tmp) / "refused.jsonl",
                num_players=_NUM_PLAYERS,
                num_impostors=_NUM_IMPOSTORS,
                tasks_per_crewmate=_TASKS,
                initial_state=state,
            )


def test_headless_game_validates_injected_state_consistency() -> None:
    """Every seed/roster/phase/map disagreement is a loud constructor error."""

    game_map = load_canonical_map()
    state = _base_state(game_map)

    def _game(**overrides: object) -> HeadlessGame:
        kwargs: dict[str, object] = {
            "seed": 0,
            "game_map": game_map,
            "agent_factory": build_default_agent_factory(),
            "replay_path": None,
            "num_players": _NUM_PLAYERS,
            "num_impostors": _NUM_IMPOSTORS,
            "tasks_per_crewmate": _TASKS,
            "initial_state": state,
        }
        kwargs.update(overrides)
        return HeadlessGame(**kwargs)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="seed"):
        _game(seed=1)
    with pytest.raises(ValueError, match="num_players"):
        _game(num_players=_NUM_PLAYERS - 1)
    with pytest.raises(ValueError, match="impostors"):
        _game(num_impostors=_NUM_IMPOSTORS + 1)
    with pytest.raises(ValueError, match="PLAY"):
        _game(initial_state=replace(state, phase="MEETING"))
    with pytest.raises(ValueError, match="map"):
        _game(initial_state=replace(state, map="some_other_map"))


def test_injected_state_seeds_the_emergency_mask_tracker() -> None:
    """An injected state's spent button uses reach the mask (Task 18.23).

    The mask's emergency tracker is policy-side (uses-remaining is not on the
    observation surface), so a mid-game injected state with spent
    ``emergency_uses`` must seed it — a tracker at the map-wide full allowance
    would advertise an engine-rejected emergency as engine-legal and corrupt
    the legal-action signal.
    """

    game_map = load_canonical_map()
    cap = game_map.emergency.uses_per_player
    base = replace(_base_state(game_map), tick=10)
    crew_id = next(
        pid for pid, player in base.players.items() if player.role == "CREWMATE"
    )
    emergency = EmergencyMeetingIntent(actor=crew_id, type="emergency")

    def _first_mask_for(state: WorldState) -> ActionMask:
        captured: dict[PlayerId, ActionMask] = {}

        def capture(decision: MaskedDecision) -> ActionIntent:
            if decision.packet.agent_id == crew_id and crew_id not in captured:
                captured[crew_id] = decision.mask
            return decision.fsm_intent

        env = _env(no_replay=True, intent_selector=capture, max_ticks=12)
        env.rollout_injected(state)
        return captured[crew_id]

    # All uses spent in the staged state: the mask must mark the emergency
    # illegal, in agreement with the engine.
    spent_state = replace(base, emergency_uses={crew_id: cap})
    assert not _first_mask_for(spent_state).is_engine_legal(emergency)
    assert _engine_rejects(spent_state, emergency, game_map)

    # The unspent control: same staged shape, full allowance, mask legal.
    assert _first_mask_for(base).is_engine_legal(emergency)
    assert not _engine_rejects(base, emergency, game_map)


def test_rollout_injected_rejects_invalid_emergency_counters() -> None:
    """Out-of-range / roster-foreign staged counters fail loud at the seam.

    The mask trackers are seeded by subtracting the staged spent-use counts
    from the map allowance, and the engine counts presses up from 0 — a
    negative count would mint extra button presses, so it has no game
    provenance and must never reach the factory.
    """

    game_map = load_canonical_map()
    base = replace(_base_state(game_map), tick=10)
    crew_id = next(
        pid for pid, player in base.players.items() if player.role == "CREWMATE"
    )
    env = _env(no_replay=True)
    with pytest.raises(ValueError, match="outside"):
        env.rollout_injected(replace(base, emergency_uses={crew_id: -1}))
    with pytest.raises(ValueError, match="outside"):
        env.rollout_injected(
            replace(
                base,
                emergency_uses={crew_id: game_map.emergency.uses_per_player + 1},
            )
        )
    with pytest.raises(ValueError, match="not on its roster"):
        env.rollout_injected(replace(base, emergency_uses={"p-99": 1}))


def test_rollout_injected_accepts_an_explicit_agent_factory() -> None:
    """The campaign-agent seam: an explicit factory replaces the default one.

    ``agent_factory`` swaps WHO builds the agents (e.g. the coevo factory's
    memory-aware wrappers), never the machinery around them — so handing the
    seam the exact factory the default path would have built must reproduce
    the default injected episode byte-for-byte.
    """

    game_map = load_canonical_map()
    state = replace(_base_state(game_map), tick=10)
    default_episode = _env(no_replay=True).rollout_injected(state)
    factory = build_interposition_factory(
        game_map=game_map,
        intent_selector=None,
        emergency_uses_spent=state.emergency_uses,
    )
    explicit = _env(no_replay=True).rollout_injected(state, agent_factory=factory)
    assert explicit.state_hashes == default_episode.state_hashes
    assert explicit.frames == default_episode.frames
    assert explicit.events == default_episode.events
    assert explicit.meetings == default_episode.meetings


def test_build_interposition_factory_rejects_out_of_range_spent_counts() -> None:
    """The exported factory validates spent-use counts itself (fail loud).

    ``rollout_injected`` validates its own staged state, but the factory is a
    public seam that accepts the mapping independently — and its tracker
    seeding subtracts from the map allowance, so a too-large count would
    silently clamp to zero remaining and a negative one would mint extra
    presses, corrupting every mask instead of failing at construction.
    """

    game_map = load_canonical_map()
    cap = game_map.emergency.uses_per_player
    with pytest.raises(ValueError, match="outside"):
        build_interposition_factory(game_map=game_map, emergency_uses_spent={"p-1": -1})
    with pytest.raises(ValueError, match="outside"):
        build_interposition_factory(
            game_map=game_map, emergency_uses_spent={"p-1": cap + 1}
        )


def test_rollout_injected_refuses_a_supplied_factory_with_spent_emergencies() -> None:
    """Staged spent button uses + an explicit factory fail loud (Task 18.23).

    Only the interposition factory takes ``emergency_uses_spent``; a supplied
    factory's wrappers seed every agent's tracker at the map-wide full
    allowance, so its policies would be told an engine-rejected emergency
    press is legal — a silently distorted episode rather than an error.
    """

    game_map = load_canonical_map()
    base = replace(_base_state(game_map), tick=10)
    crew_id = next(
        pid for pid, player in base.players.items() if player.role == "CREWMATE"
    )
    state = replace(base, emergency_uses={**base.emergency_uses, crew_id: 1})
    env = _env(no_replay=True)
    factory = build_interposition_factory(game_map=game_map)
    with pytest.raises(ValueError, match="spent emergency_uses"):
        env.rollout_injected(state, agent_factory=factory)
    # The all-zero staged shape stays fine through the same factory seam
    # (pinned end-to-end by the explicit-factory equality test above).


def test_rollout_injected_rejects_competing_agent_seams() -> None:
    """An explicit factory plus a constructor selector is refused, fail loud.

    Both claim the whole agent seam; silently ignoring either would run a
    different episode than the caller configured (AGENTS.md no silent
    fallbacks).
    """

    game_map = load_canonical_map()
    state = _base_state(game_map)

    def delegate(decision: MaskedDecision) -> ActionIntent:
        return decision.fsm_intent

    env = _env(no_replay=True, intent_selector=delegate)
    factory = build_interposition_factory(game_map=game_map)
    with pytest.raises(ValueError, match="competing agent seams"):
        env.rollout_injected(state, agent_factory=factory)
