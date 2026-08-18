"""Tests for scenario staging: the skill-scenario library (Task 18.23).

Pins the definition-of-done contract: all four scenarios construct valid states
(engine-accepted, hash-coherent, canonical rng snapshot); an injected-state
episode is deterministic (same scenario + seed => identical digest twice, and
seed-sensitive); scenario episodes score through the dense channel while the
terminal gate refuses them; each fitness definition's Goodhart guard (what it
deliberately does NOT reward — the FO-2 lesson) actually withholds credit; the
provider conforms to the driver's ``CoevoScenarioProvider`` seam with pure
deterministic terms and a stated game budget; and a miniature ES leg on one
scenario runs end-to-end (double-run digest equal, fitness pressure visible).
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import replace

import pytest

from agents.memory.store import AgentMemory
from engine.entities import PlayerId
from engine.events import (
    KilledEvent,
    MeetingTriggeredEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.rng import EngineRng, RngStateHashPolicy
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from observation.action_intent import (
    ActionIntent,
    EmergencyMeetingIntent,
    KillIntent,
    MoveIntent,
    ReportBodyIntent,
    VentIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import AgentFactory
from orchestrator.replay import _state_hash
from training.bakeoff.es import ESConfig, evolve
from training.coevo.driver import CoevoScenarioProvider
from training.coevo.factory import build_coevo_factory
from training.determinism import PolicyFrame
from training.env import IntentSelector, MaskedDecision, TacticalRolloutEnv
from training.rewards import TruncatedEpisodeError, compute_shaped_reward
from training.rollout import EpisodeRollout
from training.scenarios import (
    BODY_DISCOVERY_LATENCY,
    FORCE_PARITY_ENDGAME,
    KILL_WITH_WITNESS_NEARBY,
    SCENARIO_LIBRARY,
    VENT_UNSEEN_UNDER_PATROL,
    AgentFactoryBuilder,
    ScenarioProvider,
    ScenarioSpec,
    SelectorBuilder,
    build_scenario_state,
    scenario_by_name,
)

# Task 19.27: campaign tier (training/README.md §2 FREEZE — co-evolution / campaign machinery).
# Excluded from the default gate; runs weekly in CI's campaign-tier job and
# at phase close via `-m campaign`.
pytestmark = pytest.mark.campaign

_GAME_MAP = load_canonical_map()


def _episode_digest(rollout: EpisodeRollout) -> str:
    """SHA-256 over the per-frame state-hash chain — the determinism pin."""

    hasher = hashlib.sha256()
    for state_hash in rollout.state_hashes:
        hasher.update(state_hash.encode("utf-8"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def _run(
    spec: ScenarioSpec,
    seed: int,
    *,
    intent_selector: IntentSelector | None = None,
    rng_hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
) -> EpisodeRollout:
    env = TacticalRolloutEnv(
        game_map=_GAME_MAP,
        intent_selector=intent_selector,
        max_ticks=spec.max_ticks,
        no_replay=True,
        rng_hash_policy=rng_hash_policy,
    )
    return env.rollout_injected(build_scenario_state(spec, seed=seed))


def _wait(decision: MaskedDecision) -> ActionIntent:
    return WaitIntent(actor=decision.packet.agent_id, type="wait")


def _impostor_wait_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor holds still forever; every crew decision stays the FSM's."""

    if decision.packet.self_state.role == "IMPOSTOR":
        return _wait(decision)
    return decision.fsm_intent


def _all_wait_selector(decision: MaskedDecision) -> ActionIntent:
    return _wait(decision)


# --------------------------------------------------------------------------- #
# All four scenarios construct valid states                                    #
# --------------------------------------------------------------------------- #


def test_library_carries_the_four_contract_scenarios() -> None:
    assert tuple(spec.name for spec in SCENARIO_LIBRARY) == (
        "kill-with-witness-nearby-then-survive-the-meeting",
        "vent-unseen-under-patrol",
        "force-parity-endgame",
        "body-discovery-latency",
    )
    assert tuple(spec.side for spec in SCENARIO_LIBRARY) == (
        "impostor",
        "impostor",
        "impostor",
        "crew",
    )
    # Every fitness definition documents both halves of its contract: what it
    # rewards AND what it deliberately does not (the FO-2 Goodhart guard).
    for spec in SCENARIO_LIBRARY:
        assert spec.rewards
        assert spec.does_not_reward
    for spec in SCENARIO_LIBRARY:
        assert scenario_by_name(spec.name) is spec
    with pytest.raises(ValueError, match="unknown scenario"):
        scenario_by_name("no-such-drill")


@pytest.mark.parametrize("spec", SCENARIO_LIBRARY, ids=lambda s: s.name)
def test_scenario_states_are_valid_and_hash_coherent(spec: ScenarioSpec) -> None:
    state = build_scenario_state(spec, seed=7)
    # The staged shape: a runnable mid-game PLAY state on the canonical map.
    assert state.phase == "PLAY"
    assert state.map == _GAME_MAP.id
    assert state.tick == spec.staged_tick
    assert state.seed == 7
    # The rng-snapshot discipline: byte-exact canonical from_seed snapshot.
    assert state.rng_state == EngineRng.from_seed(7).snapshot()
    # Hash-coherent: the committed state serialization accepts it, and the
    # construction is byte-stable (two builds hash identically).
    assert _state_hash(state) == _state_hash(build_scenario_state(spec, seed=7))
    # Engine-accepted: advance_tick takes the staged state as-is without
    # ending the game on the spot (parity/eject/task/sabotage traps absent).
    next_state, _ = advance_tick(state, [], game_map=_GAME_MAP)
    assert next_state.phase == "PLAY"
    assert next_state.tick == spec.staged_tick + 1


@pytest.mark.parametrize("spec", SCENARIO_LIBRARY, ids=lambda s: s.name)
def test_injected_episode_is_deterministic_twice(spec: ScenarioSpec) -> None:
    first = _run(spec, 7)
    second = _run(spec, 7)
    assert _episode_digest(first) == _episode_digest(second)
    assert first.events == second.events
    assert first.meetings == second.meetings
    # The digest is seed-sensitive: a different seed re-stamps the rng chain.
    assert _episode_digest(first) != _episode_digest(_run(spec, 8))


def test_injected_episode_carries_the_state_derived_roster() -> None:
    rollout = _run(FORCE_PARITY_ENDGAME, 3)
    assert rollout.seed == 3
    assert rollout.num_players == 5
    assert rollout.num_impostors == 1
    assert rollout.tasks_per_crewmate == 1
    assert rollout.frames[0].kind == "initial"
    assert rollout.frames[0].tick == FORCE_PARITY_ENDGAME.staged_tick
    assert rollout.roles == {
        "p-1": "CREWMATE",
        "p-2": "IMPOSTOR",
        "p-3": "CREWMATE",
        "p-4": "CREWMATE",
        "p-5": "CREWMATE",
    }


def test_injected_descriptor_rates_normalize_over_the_captured_horizon() -> None:
    # Rate descriptors divide by the CAPTURED horizon, not the absolute staged
    # clock — otherwise equivalent traces would score different rates purely
    # because of staged_tick. final_tick itself stays absolute.
    rollout = _run(BODY_DISCOVERY_LATENCY, 7)
    elapsed = rollout.final_tick - BODY_DISCOVERY_LATENCY.staged_tick
    assert rollout.final_tick > BODY_DISCOVERY_LATENCY.staged_tick
    assert rollout.descriptors.meeting_trigger_rate == len(rollout.meetings) / elapsed
    assert (
        rollout.descriptors.do_task_cadence
        == rollout.descriptors.do_task_emissions / elapsed
    )


def test_scenario_episode_runs_on_the_training_fast_path() -> None:
    """The provider's fast-path opt-in changes bytes, never the trajectory."""

    full = _run(VENT_UNSEEN_UNDER_PATROL, 7)
    fast = _run(
        VENT_UNSEEN_UNDER_PATROL,
        7,
        rng_hash_policy=RngStateHashPolicy.TRAINING_FAST,
    )
    assert fast.events == full.events
    assert fast.meetings == full.meetings
    assert all(frame.state_hash == "" for frame in fast.frames)
    assert VENT_UNSEEN_UNDER_PATROL.fitness(fast) == VENT_UNSEEN_UNDER_PATROL.fitness(
        full
    )


# --------------------------------------------------------------------------- #
# Staged-state validation fails loud on construction bugs                      #
# --------------------------------------------------------------------------- #


def _broken(
    base: ScenarioSpec, mutate: Callable[[WorldState], WorldState]
) -> ScenarioSpec:
    """A spec whose builder post-mutates the good staged state."""

    def build(game_map: Map, seed: int) -> WorldState:
        return mutate(base.build_state(game_map, seed))

    return replace(base, build_state=build)


def test_build_rejects_a_parity_trap() -> None:
    def kill_one_crew(state: WorldState) -> WorldState:
        players = dict(state.players)
        players["p-1"] = replace(players["p-1"], alive=False)
        return replace(state, players=players)

    spec = _broken(FORCE_PARITY_ENDGAME, kill_one_crew)
    with pytest.raises(ValueError, match="IMPOSTOR_PARITY"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_a_non_canonical_rng_snapshot() -> None:
    spec = _broken(
        KILL_WITH_WITNESS_NEARBY,
        lambda state: replace(state, rng_state=EngineRng.from_seed(99).snapshot()),
    )
    with pytest.raises(ValueError, match="canonical EngineRng"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_a_staged_tick_drift() -> None:
    spec = _broken(
        KILL_WITH_WITNESS_NEARBY, lambda state: replace(state, tick=state.tick + 1)
    )
    with pytest.raises(ValueError, match="staged_tick"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_dead_players_owning_incomplete_work() -> None:
    def kill_the_victim(state: WorldState) -> WorldState:
        players = dict(state.players)
        players["p-5"] = replace(players["p-5"], alive=False)
        return replace(state, players=players)

    spec = _broken(KILL_WITH_WITNESS_NEARBY, kill_the_victim)
    with pytest.raises(ValueError, match="dead-task invariant"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_an_instant_task_win() -> None:
    def complete_everything(state: WorldState) -> WorldState:
        tasks = {
            instance_id: replace(task, progress=task.required_ticks, completed=True)
            for instance_id, task in state.tasks.items()
        }
        return replace(state, tasks=tasks)

    spec = _broken(KILL_WITH_WITNESS_NEARBY, complete_everything)
    with pytest.raises(ValueError, match="CREWMATE_TASKS"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_an_empty_task_map() -> None:
    # The seeder refuses tasks_per_crewmate < 1 and completed instances stay
    # in the mapping, so no reachable game state carries zero task instances —
    # and the engine's total-tasks > 0 guard would make CREWMATE_TASKS
    # structurally unreachable, quietly deleting a crew win pressure from
    # every episode staged on such a state.
    spec = _broken(KILL_WITH_WITNESS_NEARBY, lambda state: replace(state, tasks={}))
    with pytest.raises(ValueError, match="task map is empty"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_a_forked_task_key() -> None:
    def fork_a_key(state: WorldState) -> WorldState:
        tasks = dict(state.tasks)
        task = tasks.pop("p-1:empty_trash")
        tasks["empty_trash"] = task
        return replace(state, tasks=tasks)

    spec = _broken(KILL_WITH_WITNESS_NEARBY, fork_a_key)
    with pytest.raises(ValueError, match="tasks key"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_an_impossible_cooldown() -> None:
    # The engine only ever sets a cooldown to the map maximum and decrements
    # it; a larger staged value is a state no game can produce.
    def overclock(state: WorldState) -> WorldState:
        return replace(state, cooldowns={"p-4": _GAME_MAP.kill_cooldown_ticks + 1})

    spec = _broken(KILL_WITH_WITNESS_NEARBY, overclock)
    with pytest.raises(ValueError, match="outside"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_impostor_owned_task_instances() -> None:
    # The seeder deals instances to crew only and impostors get pretend task
    # ids; an impostor-owned incomplete instance would permanently block
    # CREWMATE_TASKS.
    def deal_to_the_impostor(state: WorldState) -> WorldState:
        tasks = dict(state.tasks)
        definition = _GAME_MAP.tasks["log_findings"]
        tasks["p-4:log_findings"] = replace(
            tasks["p-1:empty_trash"],
            id="p-4:log_findings",
            owner="p-4",
            map_task_id="log_findings",
            room=definition.room,
            required_ticks=definition.duration_ticks,
        )
        return replace(state, tasks=tasks)

    spec = _broken(KILL_WITH_WITNESS_NEARBY, deal_to_the_impostor)
    with pytest.raises(ValueError, match="impostor"):
        build_scenario_state(spec, seed=7)


def test_scenario_spec_rejects_an_unknown_side() -> None:
    # A side arriving as a plain string from config/CLI (e.g. the Role-cased
    # "IMPOSTOR") must fail loud at spec construction, not silently make the
    # scenario unservable by every provider lookup.
    with pytest.raises(ValueError, match="unknown scenario side"):
        replace(KILL_WITH_WITNESS_NEARBY, side="IMPOSTOR")  # type: ignore[arg-type]


def test_build_rejects_a_missing_impostor_cooldown_entry() -> None:
    # The seeder mints a cooldown entry for every impostor and resolve_kill
    # reads a missing key as kill-ready — an accidental free kill no real
    # game grants.
    spec = _broken(KILL_WITH_WITNESS_NEARBY, lambda state: replace(state, cooldowns={}))
    with pytest.raises(ValueError, match="no cooldown entry"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_fabricated_killer_provenance() -> None:
    # resolve_kill only ever attributes a body to a roster impostor.
    def crew_killer(state: WorldState) -> WorldState:
        bodies = {
            body_id: replace(body, killed_by="p-1")
            for body_id, body in state.bodies.items()
        }
        return replace(state, bodies=bodies)

    spec = _broken(BODY_DISCOVERY_LATENCY, crew_killer)
    with pytest.raises(ValueError, match="not a roster impostor"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_a_discovered_body() -> None:
    # The engine removes a reported body when its meeting applies, so a
    # PLAY-state body with discovered_by set has no game provenance — and
    # visibility hides it, silently flooring a discovery drill.
    def discover_the_body(state: WorldState) -> WorldState:
        bodies = {
            body_id: replace(body, discovered_by="p-1")
            for body_id, body in state.bodies.items()
        }
        return replace(state, bodies=bodies)

    spec = _broken(BODY_DISCOVERY_LATENCY, discover_the_body)
    with pytest.raises(ValueError, match="already discovered"):
        build_scenario_state(spec, seed=7)


def test_build_rejects_out_of_range_emergency_uses() -> None:
    # The engine counts button presses up from 0 to the map cap; a negative
    # staged count would mint extra presses (and corrupt the mask tracker).
    spec = _broken(
        KILL_WITH_WITNESS_NEARBY,
        lambda state: replace(state, emergency_uses={"p-1": -1}),
    )
    with pytest.raises(ValueError, match="outside"):
        build_scenario_state(spec, seed=7)
    spec = _broken(
        KILL_WITH_WITNESS_NEARBY,
        lambda state: replace(state, emergency_uses={"p-99": 1}),
    )
    with pytest.raises(ValueError, match="not a roster player"):
        build_scenario_state(spec, seed=7)


# --------------------------------------------------------------------------- #
# Per-scenario fitness: dense tactical facts, and the named non-rewards hold   #
# --------------------------------------------------------------------------- #


def test_scenario_episodes_score_dense_while_the_terminal_gate_refuses() -> None:
    """The doctrine pin: truncated scenario episodes score through the dense
    channel; ``compute_shaped_reward``'s terminal gate refuses them."""

    rollout = _run(BODY_DISCOVERY_LATENCY, 7, intent_selector=_all_wait_selector)
    assert rollout.truncated
    assert rollout.outcome == "TICK_BUDGET"
    # Dense scoring is well-defined on the truncated episode...
    assert BODY_DISCOVERY_LATENCY.fitness(rollout) == 0.0
    # ...while the full-game terminal gate refuses it, structurally.
    with pytest.raises(TruncatedEpisodeError):
        compute_shaped_reward(rollout, "CREWMATE")


def test_kill_with_witness_fsm_hunts_elsewhere_and_earns_nothing() -> None:
    # The scripted FSM impostor never takes the staged LABS window at all — it
    # walks next door and kills through MEDBAY instead. Under an any-kill
    # reading that unstaged rampage COLLECTED the kill credit (the exploit the
    # staged-kill qualifier closes); keyed on the staged victim in the staged
    # room, the scripted anchor earns 0.0 and only actually running the drill
    # scores.
    rollout = _run(KILL_WITH_WITNESS_NEARBY, 7)
    kills = [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert len(kills) >= 2
    assert all(k.target != "p-5" for k in kills)
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 0.0


def _kill_once_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor takes the staged window at tick 40 and then holds still."""

    packet = decision.packet
    if packet.self_state.role != "IMPOSTOR":
        return decision.fsm_intent
    if packet.tick == KILL_WITH_WITNESS_NEARBY.staged_tick:
        for intent in decision.mask.engine_legal:
            if isinstance(intent, KillIntent):
                return intent
    return _wait(decision)


def test_kill_with_witness_single_kill_then_survive_earns_full_credit() -> None:
    # The drill's ideal: exactly one kill, the corpse crew-reported, the
    # meeting concluded without ejecting an impostor — the full 2.0.
    rollout = _run(KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_kill_once_selector)
    kills = [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert len(kills) == 1
    first = kills[0]
    assert any(
        isinstance(e, MeetingTriggeredEvent)
        and e.trigger == "report"
        and e.body_id == f"body-{first.target}-{first.tick}"
        and rollout.roles.get(e.actor) == "CREWMATE"
        for e in rollout.events
    )
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 2.0


def test_kill_with_witness_rewards_nothing_without_the_kill() -> None:
    # A holding impostor earns zero — including zero survival credit, even if
    # the crew were to meet anyway: the drill is kill-then-survive, not hide.
    rollout = _run(KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_impostor_wait_selector)
    assert not [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 0.0


def _snub_the_staged_victim_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor refuses the staged LABS window, walks next door, kills there.

    The unstaged-kill exploit (Codex review on PR #313): under an any-kill
    reading, killing some OTHER crewmate in another room — none of the staged
    witness pressure — earned the kill credit (and, once that corpse was
    crew-reported, the survival credit too) in a scenario named for killing
    with a witness nearby.
    """

    packet = decision.packet
    if packet.self_state.role != "IMPOSTOR":
        return decision.fsm_intent
    for intent in decision.mask.engine_legal:
        if isinstance(intent, KillIntent) and intent.payload.target != "p-5":
            return intent
    if packet.self_state.room == "LABS":
        return MoveIntent.model_validate(
            {
                "type": "move",
                "actor": packet.agent_id,
                "payload": {"to_room": "MEDBAY"},
            }
        )
    return _wait(decision)


def test_kill_with_witness_pays_nothing_for_an_unstaged_kill() -> None:
    # Both credits key on the staged opportunity (the staged victim, in the
    # staged room), so routing around the witness pressure — a kill of anyone
    # else, anywhere else — scores 0.0, reported corpse or not.
    rollout = _run(
        KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_snub_the_staged_victim_selector
    )
    kills = [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert kills, "the impostor found a victim away from the staged window"
    assert all(k.target != "p-5" for k in kills)
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 0.0


def _self_report_farm_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor kills whenever legal and reports its own corpse; crew hold.

    The farm the crew-routed requirement exists to defeat: under the default
    fake meeting layer no meeting can ever eject, so an any-meeting-concluded
    reading of "survived" would hand this maximally blatant strategy the full
    survival credit for free.
    """

    if decision.packet.self_state.role != "IMPOSTOR":
        return _wait(decision)
    for intent in decision.mask.engine_legal:
        if isinstance(intent, KillIntent):
            return intent
    for intent in decision.mask.engine_legal:
        if isinstance(intent, ReportBodyIntent):
            return intent
    return _wait(decision)


def test_kill_with_witness_self_report_farm_earns_only_the_kill() -> None:
    rollout = _run(
        KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_self_report_farm_selector
    )
    concluded = [m for m in rollout.meetings if m.outcome is not None]
    # Meetings DID conclude — but every one was impostor-routed, so the
    # survival credit stays off: self-report spam cannot farm it.
    assert concluded
    assert all(rollout.roles.get(m.triggered_by) == "IMPOSTOR" for m in concluded)
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 1.0


def _pre_kill_button_selector(decision: MaskedDecision) -> ActionIntent:
    """p-1 presses the button; the impostor lands the staged kill just after.

    The ordering exploit (Codex review on PR #313): a crew-routed meeting that
    concluded BEFORE the kill satisfied an order-blind crew-routed check, so
    killing right after the meeting collected the full survival credit with no
    post-kill scrutiny at all. The impostor holds through the staged tick (the
    button meeting resolves first) and then takes the staged victim — still
    co-located in the staged room — while the crew never file a report.
    """

    packet = decision.packet
    if packet.self_state.role == "IMPOSTOR":
        if packet.tick > KILL_WITH_WITNESS_NEARBY.staged_tick:
            for intent in decision.mask.engine_legal:
                if isinstance(intent, KillIntent) and intent.payload.target == "p-5":
                    return intent
        return _wait(decision)
    if packet.agent_id == "p-1":
        emergency = EmergencyMeetingIntent(actor=packet.agent_id, type="emergency")
        if decision.mask.is_engine_legal(emergency):
            return emergency
    if isinstance(decision.fsm_intent, ReportBodyIntent):
        return _wait(decision)
    return decision.fsm_intent


def test_kill_with_witness_pre_kill_meeting_carries_no_survival_credit() -> None:
    rollout = _run(
        KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_pre_kill_button_selector
    )
    kills = [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert kills, "the impostor still lands the staged kill after the meeting"
    assert all(k.target == "p-5" and k.room == "LABS" for k in kills)
    kill_ticks = [k.tick for k in kills]
    concluded = [m for m in rollout.meetings if m.outcome is not None]
    # Every crew-routed meeting concluded strictly BEFORE the first kill...
    crew_routed = [
        m for m in concluded if rollout.roles.get(m.triggered_by) == "CREWMATE"
    ]
    assert crew_routed
    assert all(m.tick < min(kill_ticks) for m in crew_routed)
    # ...so the staged kill lands but the survival credit does not: pre-kill
    # meetings are not scrutiny of the kill.
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 1.0


def _same_batch_selector(decision: MaskedDecision) -> ActionIntent:
    """Kill and button press land in the SAME action batch at tick 42.

    The Codex round-2 exploit shape: intents are collected from pre-tick
    packets, so p-6's button decision cannot have seen p-4's kill even though
    the kill resolves first in the sorted batch — both stamp tick 42. The
    impostor waits until tick 42 then kills; p-6 walks to CAFETERIA and
    presses; every other crew decision suppresses reports/emergencies so no
    later (legitimately qualifying) meeting muddies the pin.
    """

    packet = decision.packet
    if packet.self_state.role == "IMPOSTOR":
        if packet.tick >= 42:
            for intent in decision.mask.engine_legal:
                if isinstance(intent, KillIntent):
                    return intent
        return _wait(decision)
    if packet.agent_id == "p-6":
        emergency = EmergencyMeetingIntent(actor=packet.agent_id, type="emergency")
        if decision.mask.is_engine_legal(emergency):
            return emergency
        if packet.self_state.room == "ENGINEERING":
            return MoveIntent.model_validate(
                {
                    "type": "move",
                    "actor": packet.agent_id,
                    "payload": {"to_room": "EAST_HALL"},
                }
            )
        if packet.self_state.room == "EAST_HALL":
            return MoveIntent.model_validate(
                {
                    "type": "move",
                    "actor": packet.agent_id,
                    "payload": {"to_room": "CAFETERIA"},
                }
            )
        return _wait(decision)
    if isinstance(decision.fsm_intent, (EmergencyMeetingIntent, ReportBodyIntent)):
        return _wait(decision)
    return decision.fsm_intent


def test_kill_with_witness_same_batch_meeting_carries_no_survival_credit() -> None:
    rollout = _run(KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_same_batch_selector)
    kill_ticks = [e.tick for e in rollout.events if isinstance(e, KilledEvent)]
    assert kill_ticks
    concluded = [m for m in rollout.meetings if m.outcome is not None]
    crew_routed = [
        m for m in concluded if rollout.roles.get(m.triggered_by) == "CREWMATE"
    ]
    # The crew-routed meeting shares the first kill's tick — the same action
    # batch, decided from pre-kill packets — so it is not post-kill scrutiny.
    assert crew_routed
    assert min(kill_ticks) == min(m.tick for m in crew_routed)
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 1.0


def _unrelated_post_kill_meeting_selector(decision: MaskedDecision) -> ActionIntent:
    """Crew press the button AFTER the staged kill but never report the body.

    The Codex round-4 exploit shape: an order-only check accepted ANY
    crew-routed post-kill meeting — a stray emergency included — so the
    survival credit was collectable without the staged victim's body ever
    being discovered. The impostor takes the staged window and holds.
    """

    packet = decision.packet
    if packet.self_state.role == "IMPOSTOR":
        if packet.tick == KILL_WITH_WITNESS_NEARBY.staged_tick:
            for intent in decision.mask.engine_legal:
                if isinstance(intent, KillIntent):
                    return intent
        return _wait(decision)
    if packet.agent_id == "p-6":
        if packet.tick >= 44:
            emergency = EmergencyMeetingIntent(actor=packet.agent_id, type="emergency")
            if decision.mask.is_engine_legal(emergency):
                return emergency
        if packet.self_state.room == "ENGINEERING":
            return MoveIntent.model_validate(
                {
                    "type": "move",
                    "actor": packet.agent_id,
                    "payload": {"to_room": "EAST_HALL"},
                }
            )
        if packet.self_state.room == "EAST_HALL":
            return MoveIntent.model_validate(
                {
                    "type": "move",
                    "actor": packet.agent_id,
                    "payload": {"to_room": "CAFETERIA"},
                }
            )
        return _wait(decision)
    if isinstance(decision.fsm_intent, (EmergencyMeetingIntent, ReportBodyIntent)):
        return _wait(decision)
    return decision.fsm_intent


def _serial_killer_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor kills whenever legal; crew stay pure FSM (they DO report).

    The Codex round-5 exploit shape: with an at-least-one-kill gate, the
    impostor could kill the staged victim, keep killing (silencing would-be
    discoverers), and still collect the survival credit when some crew
    reported the FIRST corpse around the massacre.
    """

    if decision.packet.self_state.role != "IMPOSTOR":
        return decision.fsm_intent
    for intent in decision.mask.engine_legal:
        if isinstance(intent, KillIntent):
            return intent
    return _wait(decision)


def test_kill_with_witness_second_kill_forfeits_the_survival_credit() -> None:
    rollout = _run(KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_serial_killer_selector)
    kills = [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert len(kills) >= 2, "the serial killer lands more than the staged kill"
    # The FIRST corpse's crew report DID happen — the survival credit's other
    # conditions hold — but the extra kills forfeit it.
    first = kills[0]
    assert any(
        isinstance(e, MeetingTriggeredEvent)
        and e.trigger == "report"
        and e.body_id == f"body-{first.target}-{first.tick}"
        and rollout.roles.get(e.actor) == "CREWMATE"
        for e in rollout.events
    )
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 1.0


def test_kill_with_witness_unrelated_post_kill_meeting_earns_nothing() -> None:
    rollout = _run(
        KILL_WITH_WITNESS_NEARBY,
        7,
        intent_selector=_unrelated_post_kill_meeting_selector,
    )
    kill_ticks = [e.tick for e in rollout.events if isinstance(e, KilledEvent)]
    assert kill_ticks
    concluded = [m for m in rollout.meetings if m.outcome is not None]
    # A crew-routed meeting concluded strictly AFTER the kill — but it is an
    # emergency, not the staged kill's body report, so it is not scrutiny of
    # THIS kill and the survival credit stays off.
    assert any(
        m.trigger == "emergency"
        and rollout.roles.get(m.triggered_by) == "CREWMATE"
        and m.tick > min(kill_ticks)
        for m in concluded
    )
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 1.0


def _scripted_vent_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor: always take the lexically-last engine-legal vent action.

    From the staged REACTOR start this enters REACTOR_VENT, then exits at
    STORAGE_VENT (the unwatched connection), then cycles enter/exit in empty
    STORAGE — every vent event witness-free. Crew decisions stay the FSM's.
    """

    if decision.packet.self_state.role != "IMPOSTOR":
        return decision.fsm_intent
    vents = [
        intent
        for intent in decision.mask.engine_legal
        if isinstance(intent, VentIntent)
    ]
    if not vents:
        return _wait(decision)
    return max(vents, key=lambda intent: intent.payload.vent_id)


def test_vent_unseen_scripted_transit_earns_both_credits() -> None:
    rollout = _run(VENT_UNSEEN_UNDER_PATROL, 7, intent_selector=_scripted_vent_selector)
    vent_events = [
        e for e in rollout.events if isinstance(e, (VentEnteredEvent, VentExitedEvent))
    ]
    # A REAL network transit: an exit whose source and destination vents differ.
    assert any(
        isinstance(e, VentExitedEvent) and e.source_vent_id != e.destination_vent_id
        for e in vent_events
    )
    assert all(
        rollout.roles.get(witness) != "CREWMATE"
        for event in vent_events
        for witness in event.witnesses
    )
    assert VENT_UNSEEN_UNDER_PATROL.fitness(rollout) == 2.0


def test_vent_unseen_rewards_nothing_for_holding_still() -> None:
    # Never venting is the safest way to stay unseen — and worth exactly zero:
    # the unseen credit is conditional on an actual transit.
    rollout = _run(VENT_UNSEEN_UNDER_PATROL, 7, intent_selector=_impostor_wait_selector)
    assert not [
        e for e in rollout.events if isinstance(e, (VentEnteredEvent, VentExitedEvent))
    ]
    assert VENT_UNSEEN_UNDER_PATROL.fitness(rollout) == 0.0


def _in_place_bob_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor endlessly enters/exits REACTOR_VENT without ever moving."""

    if decision.packet.self_state.role != "IMPOSTOR":
        return decision.fsm_intent
    for intent in decision.mask.engine_legal:
        if isinstance(intent, VentIntent) and intent.payload.vent_id == "REACTOR_VENT":
            return intent
    return _wait(decision)


def _kill_then_vent_selector(decision: MaskedDecision) -> ActionIntent:
    """Impostor clears the patrol at tick 34, then vents through empty rooms.

    The Codex round-4 exploit shape: the staged full cooldown only delays the
    first kill window, so within the 12-tick horizon the impostor can walk to
    ENGINEERING, kill the patrol when the cooldown expires, and transit the
    now-empty vent network unseen — which must FORFEIT the drill, not max it.
    """

    packet = decision.packet
    if packet.self_state.role != "IMPOSTOR":
        return decision.fsm_intent
    for intent in decision.mask.engine_legal:
        if isinstance(intent, KillIntent):
            return intent
    if packet.tick < 34:
        if packet.self_state.room == "REACTOR":
            return MoveIntent.model_validate(
                {
                    "type": "move",
                    "actor": packet.agent_id,
                    "payload": {"to_room": "ENGINEERING"},
                }
            )
        return _wait(decision)
    vents = [
        intent
        for intent in decision.mask.engine_legal
        if isinstance(intent, VentIntent)
    ]
    if vents:
        return max(vents, key=lambda intent: intent.payload.vent_id)
    return _wait(decision)


def test_vent_unseen_any_kill_forfeits_the_drill() -> None:
    rollout = _run(
        VENT_UNSEEN_UNDER_PATROL, 7, intent_selector=_kill_then_vent_selector
    )
    kills = [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert kills, "the horizon outlasts the staged cooldown, so the kill lands"
    # A real network transit happened after the murder — the transit credit
    # WOULD be satisfiable — but the kill forfeits the whole score before any
    # witness accounting: clearing the patrol can never solve the stealth
    # drill.
    assert any(
        isinstance(e, VentExitedEvent) and e.source_vent_id != e.destination_vent_id
        for e in rollout.events
    )
    assert VENT_UNSEEN_UNDER_PATROL.fitness(rollout) == 0.0


def test_vent_unseen_in_place_bob_is_not_a_transit() -> None:
    # The engine accepts exiting at the CURRENT vent, so an enter/exit bob in
    # the staged empty room emits VentEntered AND VentExited events with zero
    # witnesses — the cheapest would-be maximizer. The transit definition
    # (source vent != destination vent) pays it nothing.
    rollout = _run(VENT_UNSEEN_UNDER_PATROL, 7, intent_selector=_in_place_bob_selector)
    vent_events = [
        e for e in rollout.events if isinstance(e, (VentEnteredEvent, VentExitedEvent))
    ]
    assert vent_events, "the bob really does emit vent events"
    assert all(e.source_vent_id == e.destination_vent_id for e in vent_events)
    assert VENT_UNSEEN_UNDER_PATROL.fitness(rollout) == 0.0


def test_force_parity_fsm_converts_the_won_position() -> None:
    rollout = _run(FORCE_PARITY_ENDGAME, 7)
    last = rollout.frames[-1]
    assert last.alive_impostors >= last.alive_crew
    assert FORCE_PARITY_ENDGAME.fitness(rollout) == 2.0


def test_force_parity_reads_frames_never_the_winner_literal() -> None:
    # A holding impostor forces nothing — and the two live crew finish their
    # tasks inside the horizon, so the episode terminates with a WINNER
    # (CREWMATES via the task race). The fitness still scores 0.0 from the
    # unchanged alive counts: the terminal literal is never consulted, in
    # either direction.
    rollout = _run(FORCE_PARITY_ENDGAME, 7, intent_selector=_impostor_wait_selector)
    assert rollout.winner == "CREWMATES"
    assert FORCE_PARITY_ENDGAME.fitness(rollout) == 0.0
    # And on a fully-passive TRUNCATED episode (no winner exists at all) the
    # same definition is still well-defined: frame alive counts always are.
    truncated = _run(FORCE_PARITY_ENDGAME, 7, intent_selector=_all_wait_selector)
    assert truncated.truncated
    assert truncated.winner is None
    assert FORCE_PARITY_ENDGAME.fitness(truncated) == 0.0


def _staged_body_id() -> str:
    state = build_scenario_state(BODY_DISCOVERY_LATENCY, seed=7)
    return next(iter(state.bodies))


def test_body_discovery_fsm_routes_the_report() -> None:
    rollout = _run(BODY_DISCOVERY_LATENCY, 7)
    staged_report = next(
        e
        for e in rollout.events
        if isinstance(e, MeetingTriggeredEvent)
        and e.trigger == "report"
        and e.body_id == _staged_body_id()
    )
    assert rollout.roles.get(staged_report.actor) == "CREWMATE"
    fitness = BODY_DISCOVERY_LATENCY.fitness(rollout)
    assert 0.0 < fitness <= 1.0
    # The definition is exactly 1 - latency/horizon for THE STAGED BODY's
    # crew-routed report.
    latency = staged_report.tick - BODY_DISCOVERY_LATENCY.staged_tick
    assert fitness == 1.0 - latency / BODY_DISCOVERY_LATENCY.horizon_ticks


def _avoid_staged_body_selector(decision: MaskedDecision) -> ActionIntent:
    """Crew report any corpse EXCEPT the staged one; everything else is FSM."""

    if decision.packet.self_state.role == "IMPOSTOR":
        return decision.fsm_intent
    if (
        isinstance(decision.fsm_intent, ReportBodyIntent)
        and decision.fsm_intent.payload.body_id == _staged_body_id()
    ):
        return _wait(decision)
    return decision.fsm_intent


def test_body_discovery_gives_no_credit_for_other_bodies() -> None:
    # A fresh in-episode kill mints a new corpse; reporting IT is not the
    # staged discovery problem — without the body-id filter an easier-to-find
    # fresh body would substitute for the drill.
    rollout = _run(
        BODY_DISCOVERY_LATENCY, 7, intent_selector=_avoid_staged_body_selector
    )
    reports = [
        e
        for e in rollout.events
        if isinstance(e, MeetingTriggeredEvent) and e.trigger == "report"
    ]
    assert reports, "a fresh-body report meeting does happen"
    assert all(e.body_id != _staged_body_id() for e in reports)
    assert BODY_DISCOVERY_LATENCY.fitness(rollout) == 0.0


def _emergency_never_report_selector(decision: MaskedDecision) -> ActionIntent:
    """Crew spam the button when legal and never file a body report."""

    if decision.packet.self_state.role == "IMPOSTOR":
        return decision.fsm_intent
    emergency = EmergencyMeetingIntent(actor=decision.packet.agent_id, type="emergency")
    if decision.mask.is_engine_legal(emergency):
        return emergency
    if isinstance(decision.fsm_intent, ReportBodyIntent):
        return _wait(decision)
    return decision.fsm_intent


def test_body_discovery_gives_no_credit_for_button_meetings() -> None:
    # The FO-2 guard, sharpened: meetings HAPPEN (emergency), but no
    # crew-routed report ever does — the latency term still pays zero, so
    # neither suppression nor button spam can substitute for discovery.
    rollout = _run(
        BODY_DISCOVERY_LATENCY, 7, intent_selector=_emergency_never_report_selector
    )
    assert any(m.trigger == "emergency" for m in rollout.meetings)
    assert all(m.trigger != "report" for m in rollout.meetings)
    assert BODY_DISCOVERY_LATENCY.fitness(rollout) == 0.0


# --------------------------------------------------------------------------- #
# The provider conforms to the driver's scenario seam                          #
# --------------------------------------------------------------------------- #


def _impostor_gate_builder(genome: tuple[float, ...]) -> IntentSelector:
    """genome[0] > 0 takes the staged window then holds; else holds throughout.

    (The scripted FSM is no baseline here: it hunts through MEDBAY instead of
    taking the staged LABS kill, which the staged-kill qualifier scores 0.0.)
    """

    def selector(decision: MaskedDecision) -> ActionIntent:
        packet = decision.packet
        if packet.self_state.role != "IMPOSTOR":
            return decision.fsm_intent
        if genome[0] > 0.0 and packet.tick == KILL_WITH_WITNESS_NEARBY.staged_tick:
            for intent in decision.mask.engine_legal:
                if isinstance(intent, KillIntent):
                    return intent
        return _wait(decision)

    return selector


def _kill_witness_provider() -> ScenarioProvider:
    return ScenarioProvider(
        selector_builders={"impostor": _impostor_gate_builder},
        fitness_seeds=(0, 1),
        scenarios={"impostor": (KILL_WITH_WITNESS_NEARBY,)},
    )


def test_provider_conforms_to_the_driver_seam() -> None:
    provider = _kill_witness_provider()
    # Static conformance: the provider IS a CoevoScenarioProvider.
    seam: CoevoScenarioProvider = provider
    terms = seam(0, "impostor")
    assert [term.label for term in terms] == [
        "kill-with-witness-nearby-then-survive-the-meeting"
    ]
    # A side with no selector builder (or no scenarios) is inert.
    assert seam(0, "crew") == ()
    # The stated budget: episodes per ES evaluation, outside the driver's
    # projected_game_bound ceiling.
    assert provider.games_per_evaluation("impostor") == 2
    assert provider.games_per_evaluation("crew") == 0


def test_provider_default_library_splits_by_side() -> None:
    provider = ScenarioProvider(
        selector_builders={
            "impostor": _impostor_gate_builder,
            "crew": _impostor_gate_builder,
        },
        fitness_seeds=(0,),
    )
    assert [t.label for t in provider(0, "impostor")] == [
        spec.name for spec in SCENARIO_LIBRARY if spec.side == "impostor"
    ]
    assert [t.label for t in provider(3, "crew")] == [
        spec.name for spec in SCENARIO_LIBRARY if spec.side == "crew"
    ]
    assert provider.games_per_evaluation("impostor") == 3
    assert provider.games_per_evaluation("crew") == 1


def test_provider_rejects_bad_configurations() -> None:
    with pytest.raises(ValueError, match="at least one fitness seed"):
        ScenarioProvider(
            selector_builders={"impostor": _impostor_gate_builder},
            fitness_seeds=(),
        )
    with pytest.raises(ValueError, match="unique"):
        ScenarioProvider(
            selector_builders={"impostor": _impostor_gate_builder},
            fitness_seeds=(0, 0),
        )
    with pytest.raises(ValueError, match="configured under side"):
        ScenarioProvider(
            selector_builders={"crew": _impostor_gate_builder},
            fitness_seeds=(0,),
            scenarios={"crew": (KILL_WITH_WITNESS_NEARBY,)},
        )
    with pytest.raises(ValueError, match="duplicate scenario names"):
        ScenarioProvider(
            selector_builders={"impostor": _impostor_gate_builder},
            fitness_seeds=(0,),
            scenarios={
                "impostor": (KILL_WITH_WITNESS_NEARBY, KILL_WITH_WITNESS_NEARBY)
            },
        )
    # A mistyped / role-cased side key would never be looked up by the driver,
    # silently disabling every scenario term for the real side.
    with pytest.raises(ValueError, match="unknown selector-builder side"):
        ScenarioProvider(
            selector_builders={"IMPOSTOR": _impostor_gate_builder},  # type: ignore[dict-item]
            fitness_seeds=(0,),
        )
    with pytest.raises(ValueError, match="unknown scenarios side"):
        ScenarioProvider(
            selector_builders={"impostor": _impostor_gate_builder},
            fitness_seeds=(0,),
            scenarios={"IMPOSTOR": ()},  # type: ignore[dict-item]
        )
    with pytest.raises(ValueError, match="unknown agent-factory-builder side"):
        ScenarioProvider(
            agent_factory_builders={
                "IMPOSTOR": _tap_gate_factory_builder(  # type: ignore[dict-item]
                    _MemoryTapPolicy()
                )
            },
            fitness_seeds=(0,),
        )
    # A side under BOTH seams has two competing drivers for the same episodes.
    with pytest.raises(
        ValueError, match="both selector_builders and agent_factory_builders"
    ):
        ScenarioProvider(
            selector_builders={"impostor": _impostor_gate_builder},
            agent_factory_builders={
                "impostor": _tap_gate_factory_builder(_MemoryTapPolicy())
            },
            fitness_seeds=(0,),
        )
    # ...and a provider with NEITHER seam could only ever be silently inert.
    with pytest.raises(ValueError, match="at least one side"):
        ScenarioProvider(fitness_seeds=(0,))


def test_provider_terms_are_pure_and_genome_sensitive() -> None:
    provider = _kill_witness_provider()
    term = provider(0, "impostor")[0]
    # Pure and deterministic in the genome (the ES/double-run-digest contract):
    # repeated calls agree, across separately-provided terms too.
    engaged = term.fitness((1.0,))
    held = term.fitness((-1.0,))
    assert term.fitness((1.0,)) == engaged
    assert provider(1, "impostor")[0].fitness((1.0,)) == engaged
    # ...and the scenario carries real pressure: taking the staged window
    # (then holding through the corpse's report meeting) runs the whole
    # drill, while holding still earns nothing.
    assert engaged == 2.0
    assert held == 0.0


class _MemoryTapPolicy:
    """A minimal ``BakeoffPolicy``: run the drill (or hold) and tap the memory.

    Records every ``AgentMemory`` object handed to :meth:`evaluate` (strong
    references, so object identities can never be recycled) — the pin that the
    factory seam feeds policies the inner agent's LIVE memory, not a fresh
    per-call construction. The default behavior takes the staged kill-witness
    window and then holds (the whole drill); ``hold=True`` freezes the
    impostor throughout, the behavioral lever the genome-sensitivity pin
    flips.
    """

    def __init__(self, *, hold: bool = False) -> None:
        self._hold = hold
        self.taps: list[tuple[PlayerId, AgentMemory]] = []

    @property
    def encoder_version(self) -> str:
        return "impostor-memory-tap-test-v1"

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        del public_map, fsm_intent
        self.taps.append((packet.agent_id, memory))
        intent: ActionIntent = WaitIntent(actor=packet.agent_id, type="wait")
        if not self._hold and packet.tick == KILL_WITH_WITNESS_NEARBY.staged_tick:
            intent = KillIntent.model_validate(
                {
                    "type": "kill",
                    "actor": packet.agent_id,
                    "payload": {"target": "p-5"},
                }
            )
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(),
            logits=(),
            intent=intent,
        )

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> Mapping[str, float]:
        del packet, public_map, memory, fsm_intent
        return {"delegate": 1.0}


def _tap_gate_factory_builder(tap: _MemoryTapPolicy) -> AgentFactoryBuilder:
    """genome[0] > 0 runs the drill-running tap; else a fresh holding policy."""

    def build(genome: tuple[float, ...]) -> AgentFactory:
        policy = tap if genome[0] > 0.0 else _MemoryTapPolicy(hold=True)
        return build_coevo_factory(policy, None, game_map=_GAME_MAP)

    return build


def test_provider_agent_factory_builders_run_the_campaign_agents() -> None:
    """The campaign-faithful path: factory-driven episodes feed LIVE memory.

    An ``IntentSelector`` sees a ``MaskedDecision`` (packet + mask) only, so a
    campaign policy whose features read the agent's own ``AgentMemory`` (the
    v3 meeting-history / last-seen channels) cannot run through the selector
    seam. ``agent_factory_builders`` routes scenario episodes through the
    campaign's own wrappers instead (``build_coevo_factory``, the exact
    factory the coevo rollouts build): the pin below shows every policy
    decision received the inner agent's live memory — ONE object per agent
    per episode, reused across that episode's decisions — while the genome
    still gates behavior and the term stays pure.
    """

    tap = _MemoryTapPolicy()
    provider = ScenarioProvider(
        agent_factory_builders={"impostor": _tap_gate_factory_builder(tap)},
        fitness_seeds=(0, 1),
        scenarios={"impostor": (KILL_WITH_WITNESS_NEARBY,)},
    )
    seam: CoevoScenarioProvider = provider
    terms = seam(0, "impostor")
    assert [term.label for term in terms] == [
        "kill-with-witness-nearby-then-survive-the-meeting"
    ]
    # The factory seam serves the side's budget exactly like the selector seam.
    assert provider.games_per_evaluation("impostor") == 2
    assert provider.games_per_evaluation("crew") == 0

    engaged = terms[0].fitness((1.0,))
    held = terms[0].fitness((-1.0,))
    # The tap runs the whole drill (staged kill, then holds through the
    # corpse's report meeting) — landing exactly on the selector path's
    # pinned 2.0; holding scores nothing; repeat calls agree (the purity
    # contract).
    assert engaged == 2.0
    assert held == 0.0
    assert terms[0].fitness((1.0,)) == engaged

    # The live-memory pin: the delegating tap drove 2 fitness calls x 2 seeds
    # = 4 episodes, and every decision saw its agent's own live AgentMemory —
    # one distinct object per episode (fresh agents per game), reused across
    # all of that episode's decisions (never rebuilt per call).
    assert tap.taps
    by_agent: dict[PlayerId, list[AgentMemory]] = {}
    for agent_id, memory in tap.taps:
        assert isinstance(memory, AgentMemory)
        by_agent.setdefault(agent_id, []).append(memory)
    for memories in by_agent.values():
        distinct = {id(memory) for memory in memories}
        assert len(distinct) == 4
        assert len(memories) > len(distinct)


def _one_shot_builder_with_ledger(builds: list[int]) -> SelectorBuilder:
    """A deliberately STATEFUL product: each built selector fires only once.

    An engaged selector takes the staged window once in its LIFETIME (the
    ``fired`` closure flag), so a single instance reused across seed episodes
    would hold still in every episode after the first. The ledger records one
    entry per build call.
    """

    def build(genome: tuple[float, ...]) -> IntentSelector:
        builds.append(1)
        fired = [False]

        def selector(decision: MaskedDecision) -> ActionIntent:
            packet = decision.packet
            if packet.self_state.role != "IMPOSTOR":
                return decision.fsm_intent
            if (
                genome[0] > 0.0
                and not fired[0]
                and packet.tick == KILL_WITH_WITNESS_NEARBY.staged_tick
            ):
                for intent in decision.mask.engine_legal:
                    if isinstance(intent, KillIntent):
                        fired[0] = True
                        return intent
            return _wait(decision)

        return selector

    return build


def test_provider_rebuilds_the_policy_for_every_seed_episode() -> None:
    """A stateful builder product cannot leak state across seed episodes.

    The builder types cannot enforce stateless products (Codex round-8), so
    the provider rebuilds the selector/factory from the genome per seed
    episode: were one one-shot instance shared across both seeds, the second
    episode would hold still and the mean would drop to 1.0 — instead every
    episode runs the full drill and the ledger shows one build per seed.
    """

    builds: list[int] = []
    provider = ScenarioProvider(
        selector_builders={"impostor": _one_shot_builder_with_ledger(builds)},
        fitness_seeds=(0, 1),
        scenarios={"impostor": (KILL_WITH_WITNESS_NEARBY,)},
    )
    term = provider(0, "impostor")[0]
    assert term.fitness((1.0,)) == 2.0
    assert len(builds) == 2


def test_miniature_es_leg_runs_end_to_end_on_one_scenario() -> None:
    """The DoD leg: a tiny (1+2) ES over the kill-witness scenario term.

    Seeded at a holding genome (fitness 0), one mutation crosses the gate and
    the champion climbs to 2.0 (takes the staged window, then survives the
    corpse's crew report meeting) — scenario skill pressure flowing through
    the exact fitness callable the driver's seam would consume — and the
    double run is digest-identical (the purity obligation).
    """

    provider = _kill_witness_provider()
    term = provider(0, "impostor")[0]
    config = ESConfig(
        generations=1, population=2, sigma=1.0, seed=1, fitness_seeds=(0, 1)
    )
    first = evolve(term.fitness, genome_length=1, config=config, initial_genome=(-0.5,))
    second = evolve(
        term.fitness, genome_length=1, config=config, initial_genome=(-0.5,)
    )
    assert first.digest() == second.digest()
    assert first.num_evaluations == 3
    assert first.fitness_trace == (0.0, 2.0)
    assert first.champion_fitness == 2.0
    assert first.champion[0] > 0.0
