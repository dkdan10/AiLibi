"""A real built-in actor preserves source-time danger across the next snapshot."""

from __future__ import annotations

import pytest

from agents.memory.episodic import EpisodicEvent
from agents.tactical.investigation import has_recent_witnessed_danger
from observation.packet import EventObservationBatch, ObservationPacket, PlayerView
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import TacticalAgent, build_default_agent_factory
from tests.agents.test_investigation_planner import _packet
from tests.agents.test_tactical_experiments import _map


def _witness(*, enabled: bool = True) -> tuple[TacticalAgent, ObservationPacket]:
    config = RecordedExperimentConfig(
        format_version=3,
        evidence_reasoning_version=2,
        investigation_version=1 if enabled else None,
    )
    agent = build_default_agent_factory(experiment_config=config)("crew", "CREWMATE")
    assert type(agent) is TacticalAgent
    agent.bind_experiment(config, _map())
    agent.decide(
        _packet(1, visible=(PlayerView(id="missing", room="A", action=None),)), _map()
    )
    # An already-spent emergency cannot mask the direct-witness interrupt via
    # suspicion pacing. Witnessed danger still takes the ordinary flee route.
    agent.note_meeting_concluded(
        end_tick=2,
        dead_ids=(),
        emergency_caller_id="crew",
        ejected_id=None,
        ejected_role=None,
        votes_for_ejected=0,
        skip_votes=3,
        roster_impostor_count=1,
    )
    agent.decide(_packet(5), _map())
    agent.observe_events(
        EventObservationBatch.model_validate(
            {
                "tick": 5,
                "agent_id": "crew",
                "temporal_observation_version": 2,
                "ordered_events": [
                    {
                        "observation_order": 0,
                        "observer_before_event": {"room": "H", "in_vent": False},
                        "event": {
                            "kind": "witnessed_action",
                            "player": {"id": "killer", "room": "H", "action": "kill"},
                        },
                    },
                    {
                        "observation_order": 1,
                        "observer_before_event": {"room": "H", "in_vent": False},
                        "event": {
                            "kind": "own_transition",
                            "from_room": "H",
                            "to_room": "A",
                            "was_in_vent": False,
                            "in_vent": False,
                        },
                    },
                ],
            }
        )
    )
    # With lights active the observer cannot see the corpse in the room left
    # after the witnessed kill; the new snapshot need not repeat the action.
    packet = _packet(6, "A").model_copy(
        update={
            "global_state": _packet().global_state.model_copy(
                update={"sabotage_active": True, "sabotage_kind": "lights"}
            )
        }
    )
    return agent, packet


def test_previous_tick_kill_overrides_search_despite_spent_emergency() -> None:
    agent, packet = _witness()
    assert has_recent_witnessed_danger(agent.memory.episodic, packet=packet)
    intent = agent.decide(packet, _map())
    assert intent.type == "move" and intent.payload.to_room == "H"
    state = agent.memory.working.investigation
    assert state is not None and state.active_plan is not None
    assert state.active_plan.expires_tick == 11
    # No repeated source delivery or decision extends the clock.
    assert agent.decide(packet, _map()) == intent
    assert not has_recent_witnessed_danger(
        agent.memory.episodic, packet=packet.model_copy(update={"tick": 7})
    )


def test_investigation_off_keeps_the_previous_tactical_choice() -> None:
    agent, packet = _witness(enabled=False)
    intent = agent.decide(packet, _map())
    assert intent.type == "move" and intent.payload.to_room == "C"


def test_meeting_after_source_discussion_ends_the_immediate_danger_interrupt() -> None:
    agent, packet = _witness()
    agent.memory.episodic.append(
        EpisodicEvent(tick=6, type="meeting_boundary", provenance="public", payload={})
    )
    assert not has_recent_witnessed_danger(agent.memory.episodic, packet=packet)


@pytest.mark.parametrize("provenance", ["reported", "inferred"])
def test_another_speakers_claim_cannot_start_direct_witness_flight(
    provenance: str,
) -> None:
    agent, packet = _witness()
    # Isolate the claim after the real event has aged out.
    packet = packet.model_copy(update={"tick": 8})
    agent.memory.episodic.append(
        EpisodicEvent(
            tick=7,
            type="saw_player",
            provenance=provenance,
            observation_id="claimed-clock",
            payload={
                "player_id": "killer",
                "room": "A",
                "action": "kill",
                "source_tick": 7,
                "observation_phase": "event",
            },
        )
    )
    assert not has_recent_witnessed_danger(agent.memory.episodic, packet=packet)
