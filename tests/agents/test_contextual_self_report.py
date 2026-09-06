"""The preregistered reporting table uses current own observations only."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agents.memory.episodic import MemoryStore
from agents.tactical.experimental import (
    ExperimentalImpostorPolicy,
    TacticalExperimentOptions,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from observation.action_intent import ActionIntent
from tests.agents.test_tactical_experiments import _event, _map, _snapshot


def _decision(
    *,
    present: bool = True,
    body: bool = True,
    cooldown: int = 2,
    teammate: bool = False,
    room: str = "H",
    provenance: str = "observed",
    phase: str = "snapshot",
    source_tick: int = 5,
    vented: bool = False,
    isolated: bool = False,
) -> tuple[ActionIntent, ActionIntent]:
    memory = MemoryStore()
    _snapshot(
        memory,
        tick=5,
        cooldown=cooldown,
        teammates=("other",) if teammate else (),
        vented=vented,
    )
    if body:
        _event(
            memory, 5, "saw_body", body_id="public-victim", victim_id="victim", room="H"
        )
    if present:
        _event(
            memory,
            5,
            "saw_player",
            player_id="other",
            room=room,
            action="wait",
            provenance=provenance,
            source_tick=source_tick,
            observation_phase=phase,
        )
    game_map = _map()
    if isolated:
        game_map = game_map.model_copy(
            update={
                "room_neighbors": {**game_map.room_neighbors, "H": ()},
                "vent_rooms": {},
                "vent_graph": {},
            }
        )
    candidate = ExperimentalImpostorPolicy(
        agent_id="imp",
        options=TacticalExperimentOptions(contextual_self_report_version=1),
    ).decide(memory, game_map)
    return candidate, ImpostorPolicy(agent_id="imp").decide(memory, game_map)


def test_current_non_teammate_and_active_cooldown_changes_escape_to_report() -> None:
    candidate, anchor = _decision()
    assert anchor.type == "move"
    assert candidate.type == "report"
    assert candidate.payload.body_id == "public-victim"


@pytest.mark.parametrize(
    "change",
    [
        {"present": False},
        {"cooldown": 0},
        {"teammate": True},
        {"room": "A"},
        {"provenance": "reported"},
        {"phase": "event"},
        {"source_tick": 4},
        {"source_tick": 6},
        {"body": False},
        {"vented": True},
    ],
)
def test_table_escape_controls_keep_the_ordinary_action(
    change: dict[str, object],
) -> None:
    # The dynamic fixture deliberately varies one epistemic condition at a time.
    candidate, anchor = _decision(**change)  # type: ignore[arg-type]
    assert candidate == anchor
    assert candidate.type != "report"


def test_no_available_escape_reports_without_inventing_a_nearby_observer() -> None:
    candidate, anchor = _decision(present=False, isolated=True, cooldown=0)
    assert anchor.type == "wait"
    assert candidate.type == "report"


@pytest.mark.parametrize(
    "field", ["investigation_version", "contextual_self_report_version"]
)
@pytest.mark.parametrize("invalid", [True, False, "1", 1.0, 2])
def test_tactical_versions_do_not_coerce(field: str, invalid: object) -> None:
    with pytest.raises(ValidationError):
        TacticalExperimentOptions.model_validate({field: invalid})


@pytest.mark.parametrize(
    "options",
    [
        {"investigation_version": 1, "crew_idle_policy": "patrol"},
        {"investigation_version": 1, "crew_idle_policy": "accompany"},
        {"contextual_self_report_version": 1, "self_report": True},
    ],
)
def test_old_and_new_choices_cannot_claim_independent_arms(
    options: dict[str, object],
) -> None:
    with pytest.raises(ValidationError, match="conflicts"):
        TacticalExperimentOptions.model_validate(options)


def test_search_and_contextual_reporting_are_independent() -> None:
    both = TacticalExperimentOptions(
        investigation_version=1, contextual_self_report_version=1
    )
    assert both.investigation_version == both.contextual_self_report_version == 1
