"""Genuine evidence → attributed exchange → opaque citation, with fixed SKIPs."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Literal

import pytest

from api.replay_loader import ReplayLoader
from experiments.deduction_scenarios import (
    ScenarioCapture,
    ScenarioCase,
    ScriptedDeductionProvider,
    run_case,
    scenario_definition,
)
from meetings.schemas import (
    MeetingTurn,
    ModelAuthoredVoteBallot,
    SawMoveObservation,
    WhereaboutsClaim,
)
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import MeetingReplayEntry, read_all_entries


def _config(
    arm: str,
) -> tuple[Literal[2] | None, RecordedExperimentConfig]:
    if arm == "legacy_reference":
        return None, RecordedExperimentConfig()
    return 2, RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        public_account_version=1
        if arm in ("common_accounts", "combined_accounts", "combined_with_reply")
        else None,
        attributed_testimony_version=1
        if arm in ("attributed_testimony", "combined_accounts", "combined_with_reply")
        else None,
        bounded_rebuttal_version=1 if arm == "combined_with_reply" else None,
    )


def _meetings(capture: ScenarioCapture) -> list[MeetingReplayEntry]:
    return [
        row
        for row in read_all_entries(capture.replay_path)
        if isinstance(row, MeetingReplayEntry)
    ]


def _loader(directory: Path) -> ReplayLoader:
    (directory / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1})
    )
    return ReplayLoader(directory)


@pytest.mark.parametrize(
    "arm",
    [
        "legacy_reference",
        "repaired_clock",
        "common_accounts",
        "attributed_testimony",
        "combined_accounts",
        "combined_with_reply",
    ],
)
@pytest.mark.parametrize("case", ["honest", "impossible_account", "late_accusation"])
def test_real_movement_is_shared_and_cited_from_its_own_supplied_memory(
    tmp_path: Path, arm: str, case: ScenarioCase
) -> None:
    temporal, config = _config(arm)
    capture = run_case(
        tmp_path, case=case, experiment_config=config, temporal_version=temporal
    )
    assert capture.definition.version == 2
    (meeting,) = _meetings(capture)
    (spoken,) = [
        row
        for row in meeting.transcript.turns[0].observations
        if isinstance(row, SawMoveObservation)
    ]
    displayed_tick = 6 if temporal is None else 5
    assert (spoken.subject, spoken.from_room, spoken.to_room, spoken.tick) == (
        "p-4",
        "ADMIN",
        "WEST_HALL",
        displayed_tick,
    )
    assert all(ballot.target == "SKIP" for ballot in meeting.ballots)
    reporter_ballot = next(b for b in meeting.ballots if b.voter == "p-2")
    identifier = reporter_ballot.primary_reason_observation_id
    assert identifier is not None
    assert all(
        b.primary_reason_observation_id is None
        for b in meeting.ballots
        if b.voter != "p-2"
    )
    supplied_vote = next(
        call.prompt
        for call in meeting.llm_calls
        if call.agent_id == "p-2"
        and json.loads(call.response_text).get("voter") == "p-2"
    )
    assert any(
        f"[obs {identifier}]" in line and "move from ADMIN to WEST_HALL." in line
        for line in supplied_vote.splitlines()
    )
    (event,) = [
        event
        for event in capture.agents["p-2"].memory.episodic.recent(since_tick=0)
        if event.observation_id == identifier
    ]
    assert event.type == "saw_player_move"
    assert event.tick == displayed_tick
    assert event.provenance == "observed"
    assert event.payload["player_id"] == "p-4"
    assert (event.payload["from_room"], event.payload["to_room"]) == (
        "ADMIN",
        "WEST_HALL",
    )
    loader = _loader(tmp_path)
    own = loader.get_meeting_memory("headless-seed-1", meeting.meeting_id, "p-2")
    (reference,) = own.observation_references
    assert reference.observation_id == identifier
    assert reference.observer_id == "p-2"
    assert reference.resolved and reference.provenance == "observed"
    assert reference.kind == "saw_player_move"
    assert reference.subject_id == "p-4"
    assert reference.observation_tick == displayed_tick
    assert reference.scene_tick == 5
    assert (reference.from_room, reference.to_room) == ("ADMIN", "WEST_HALL")
    if temporal == 2:
        assert reference.source_tick == 5
        assert reference.observation_phase == "event"
        assert reference.observer_room == "ADMIN"
    assert any(
        frame.tick == reference.scene_tick
        for frame in loader.load_replay("headless-seed-1").ticks
    )
    listener_vote = next(
        call.prompt
        for call in meeting.llm_calls
        if call.agent_id == "p-3"
        and json.loads(call.response_text).get("voter") == "p-3"
    )
    assert "ADMIN" in listener_vote and "WEST_HALL" in listener_vote
    assert "I saw p-4 move from ADMIN to WEST_HALL" in listener_vote
    assert f"[obs {identifier}]" not in listener_vote
    assert not any(
        row.type == "saw_player_move" and row.payload.get("player_id") == "p-4"
        for row in capture.agents["p-3"].memory.episodic.recent(since_tick=0)
    )
    if config.public_account_version or config.attributed_testimony_version:
        if case == "impossible_account":
            assert any(
                flag.kind
                == (
                    "alibi_conflict"
                    if config.attributed_testimony_version
                    else "alibi_vs_sighting"
                )
                and "WEST_HALL" in flag.description
                and "REACTOR" in flag.description
                for flag in meeting.contradictions
            )
            if config.attributed_testimony_version:
                assert "attributed accounts" in meeting.contradictions[0].description
        else:
            assert not meeting.contradictions


@pytest.mark.parametrize("case", ["insufficient_evidence", "already_known_dead"])
def test_unobserved_departure_and_future_discovery_are_not_spoken_or_cited(
    tmp_path: Path, case: ScenarioCase
) -> None:
    temporal, config = _config("combined_with_reply")
    capture = run_case(
        tmp_path, case=case, experiment_config=config, temporal_version=temporal
    )
    meetings = _meetings(capture)
    assert not any(
        isinstance(obs, SawMoveObservation)
        for meeting in meetings
        for turn in meeting.transcript.turns
        for obs in turn.observations
    )
    assert all(
        ballot.primary_reason_observation_id is None
        for meeting in meetings
        for ballot in meeting.ballots
    )
    if case == "already_known_dead":
        assert meetings[0].tick == 5
        assert all(
            obs.type != "found_body"
            for turn in meetings[0].transcript.turns
            for obs in turn.observations
        )
        reporter_turn = next(
            t for t in meetings[0].transcript.turns if t.speaker == "p-2"
        )
        assert not reporter_turn.observations and not reporter_turn.claims


def test_late_reply_answers_the_charge_with_actual_pre_action_placements(
    tmp_path: Path,
) -> None:
    temporal, config = _config("combined_with_reply")
    capture = run_case(
        tmp_path,
        case="late_accusation",
        experiment_config=config,
        temporal_version=temporal,
    )
    (meeting,) = _meetings(capture)
    opening, _, charge, reply = meeting.transcript.turns
    assert reply.speaker == "p-2"
    assert reply.reply_to == charge.turn_id
    assert reply.free_text != opening.free_text
    assert "returning to ADMIN" in reply.free_text
    assert "working on upload logs" in reply.free_text
    assert "did not witness the kill" in reply.free_text
    assert not reply.claims
    assert len(reply.observations) == 2
    assert [
        (obs.type, obs.tick, obs.room)
        for obs in reply.observations
        if isinstance(obs, WhereaboutsClaim)
    ] == [
        ("whereabouts", 5, "UPPER_HALL"),
        ("whereabouts", 6, "ADMIN"),
    ]
    events = capture.agents["p-2"].memory.episodic.recent(since_tick=0)
    for tick, room in ((5, "UPPER_HALL"), (6, "ADMIN")):
        assert any(
            event.type == "self_state"
            and event.tick == tick
            and event.payload.get("room") == room
            and event.payload.get("observation_phase") == "snapshot"
            for event in events
        )
    assert any(
        event.type == "own_task_attempt"
        and event.tick == 2
        and event.payload.get("task_id") == "upload_logs"
        and event.payload.get("outcome") == "progressed"
        for event in events
    )
    assert all(ballot.target == "SKIP" for ballot in meeting.ballots)


@pytest.mark.parametrize("format", ["xml", "accounts"])
def test_citation_uses_opaque_supplied_id_and_cannot_borrow_public_prose(
    format: str,
) -> None:
    provider = ScriptedDeductionProvider(scenario_definition("honest"))
    line = (
        "- [obs opaque:999:handle] [during tick 5, your observation 1] "
        "You witnessed p-4 move from ADMIN to WEST_HALL. "
        "You were in ADMIN immediately before this event."
    )

    def ballot(own: str, public: str = "") -> ModelAuthoredVoteBallot:
        prompt = (
            f"<memory>\n{own}\n</memory>\n{public}"
            if format == "xml"
            else f"## Your private memory\n{own}\n## What players said\n{public}"
        )
        response = asyncio.run(
            provider.complete(
                prompt=prompt,
                schema=ModelAuthoredVoteBallot,
                max_tokens=1000,
                temperature=0,
                agent_id="p-2",
            )
        )
        return ModelAuthoredVoteBallot.model_validate_json(response.text)

    assert ballot(line).primary_reason_observation_id == "opaque:999:handle"
    # Removing the observer's line cannot be repaired by an identical public
    # statement, by the previous provider call, or by the fixture's world truth.
    assert ballot("", line).primary_reason_observation_id is None
    assert (
        ballot(
            "", line.replace("opaque:999:handle", "another-player-id")
        ).primary_reason_observation_id
        is None
    )
    response = asyncio.run(
        provider.complete(
            prompt=f"<memory>\n{line}\n</memory>",
            schema=MeetingTurn,
            max_tokens=1000,
            temperature=0,
            agent_id="p-2",
        )
    )
    turn = MeetingTurn.model_validate_json(response.text)
    (movement,) = [
        row for row in turn.observations if isinstance(row, SawMoveObservation)
    ]
    assert movement.tick == 5


def test_historical_definition_remains_readable_but_is_not_silently_reexecuted() -> (
    None
):
    current = scenario_definition("honest")
    historical = current.model_copy(update={"version": 1})
    assert current.model_validate_json(historical.model_dump_json()).version == 1
    with pytest.raises(ValueError, match="definition version 2"):
        ScriptedDeductionProvider(historical)
