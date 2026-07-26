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
from collections.abc import Callable
from dataclasses import replace

import pytest

from engine.events import KilledEvent, VentEnteredEvent, VentExitedEvent
from engine.rng import EngineRng, RngStateHashPolicy
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from observation.action_intent import ActionIntent, VentIntent, WaitIntent
from orchestrator.replay import _state_hash
from training.bakeoff.es import ESConfig, evolve
from training.coevo.driver import CoevoScenarioProvider
from training.env import IntentSelector, MaskedDecision, TacticalRolloutEnv
from training.rewards import TruncatedEpisodeError, compute_shaped_reward
from training.rollout import EpisodeRollout
from training.scenarios import (
    BODY_DISCOVERY_LATENCY,
    FORCE_PARITY_ENDGAME,
    KILL_WITH_WITNESS_NEARBY,
    SCENARIO_LIBRARY,
    VENT_UNSEEN_UNDER_PATROL,
    ScenarioProvider,
    ScenarioSpec,
    build_scenario_state,
    scenario_by_name,
)

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


def test_build_rejects_a_forked_task_key() -> None:
    def fork_a_key(state: WorldState) -> WorldState:
        tasks = dict(state.tasks)
        task = tasks.pop("p-1:empty_trash")
        tasks["empty_trash"] = task
        return replace(state, tasks=tasks)

    spec = _broken(KILL_WITH_WITNESS_NEARBY, fork_a_key)
    with pytest.raises(ValueError, match="tasks key"):
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


def test_kill_with_witness_fsm_lands_the_kill_and_survives() -> None:
    rollout = _run(KILL_WITH_WITNESS_NEARBY, 7)
    kills = [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert kills, "the staged window must be takeable (victim co-located, cd 0)"
    concluded = [m for m in rollout.meetings if m.outcome is not None]
    assert concluded, "the nearby witness must turn the kill into a meeting"
    assert all(
        m.ejected_player_id is None
        or rollout.roles.get(m.ejected_player_id) != "IMPOSTOR"
        for m in concluded
    )
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 2.0


def test_kill_with_witness_rewards_nothing_without_the_kill() -> None:
    # A holding impostor earns zero — including zero survival credit, even if
    # the crew were to meet anyway: the drill is kill-then-survive, not hide.
    rollout = _run(KILL_WITH_WITNESS_NEARBY, 7, intent_selector=_impostor_wait_selector)
    assert not [e for e in rollout.events if isinstance(e, KilledEvent)]
    assert KILL_WITH_WITNESS_NEARBY.fitness(rollout) == 0.0


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
    assert any(isinstance(e, VentEnteredEvent) for e in vent_events)
    assert any(isinstance(e, VentExitedEvent) for e in vent_events)
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


def test_body_discovery_fsm_routes_the_report() -> None:
    rollout = _run(BODY_DISCOVERY_LATENCY, 7)
    first_meeting = rollout.meetings[0]
    assert first_meeting.trigger == "report"
    assert rollout.roles.get(first_meeting.triggered_by) == "CREWMATE"
    fitness = BODY_DISCOVERY_LATENCY.fitness(rollout)
    assert 0.0 < fitness <= 1.0
    # The definition is exactly 1 - latency/horizon for that first report.
    latency = first_meeting.tick - BODY_DISCOVERY_LATENCY.staged_tick
    assert fitness == 1.0 - latency / BODY_DISCOVERY_LATENCY.horizon_ticks


def _emergency_never_report_selector(decision: MaskedDecision) -> ActionIntent:
    """Crew spam the button when legal and never file a body report."""

    from observation.action_intent import EmergencyMeetingIntent, ReportBodyIntent

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
    """genome[0] > 0 delegates the impostor to the FSM; else it holds still."""

    def selector(decision: MaskedDecision) -> ActionIntent:
        if decision.packet.self_state.role != "IMPOSTOR" or genome[0] > 0.0:
            return decision.fsm_intent
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


def test_provider_terms_are_pure_and_genome_sensitive() -> None:
    provider = _kill_witness_provider()
    term = provider(0, "impostor")[0]
    # Pure and deterministic in the genome (the ES/double-run-digest contract):
    # repeated calls agree, across separately-provided terms too.
    engaged = term.fitness((1.0,))
    held = term.fitness((-1.0,))
    assert term.fitness((1.0,)) == engaged
    assert provider(1, "impostor")[0].fitness((1.0,)) == engaged
    # ...and the scenario carries real pressure: engaging beats holding still.
    assert engaged == 2.0
    assert held == 0.0


def test_miniature_es_leg_runs_end_to_end_on_one_scenario() -> None:
    """The DoD leg: a tiny (1+2) ES over the kill-witness scenario term.

    Seeded at a holding genome (fitness 0), one mutation crosses the gate and
    the champion climbs to the full 2.0 — scenario skill pressure flowing
    through the exact fitness callable the driver's seam would consume — and
    the double run is digest-identical (the purity obligation).
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
