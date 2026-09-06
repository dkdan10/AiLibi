"""Public-account privacy and attribution through real games and their reader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import pytest
from pydantic import BaseModel

from api.replay_loader import ReplayLoader
from eval.balance_eval import load_tournament_report
from eval.meeting_quality import build_tournament_eval_report
from eval.report_schema import build_provenance_groups
from experiments.deduction_scenarios import (
    ScenarioCapture,
    ScriptedDeductionProvider,
    run_case,
    scenario_definition,
)
from llm.client import CallKind, LLMResponse
from meetings.manager import MeetingManager
from meetings.schemas import (
    MeetingTranscript,
    MeetingTurn,
    SawVentObservation,
    TaskActivityAccount,
    VentWitnessRecord,
)
from meetings.transcript import detect_contradictions
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import TacticalAgent
from orchestrator.replay import MeetingReplayEntry, read_all_entries


def _config(
    *,
    common: Literal[1] | None = 1,
    attributed: Literal[1] | None = 1,
    reply: Literal[1] | None = None,
) -> RecordedExperimentConfig:
    return RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        public_account_version=common,
        attributed_testimony_version=attributed,
        bounded_rebuttal_version=reply,
    )


def _loader(directory: Path) -> ReplayLoader:
    (directory / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1})
    )
    return ReplayLoader(directory)


def _meetings(capture: ScenarioCapture) -> list[MeetingReplayEntry]:
    return [
        row
        for row in read_all_entries(capture.replay_path)
        if isinstance(row, MeetingReplayEntry)
    ]


class _AttributedProvider(ScriptedDeductionProvider):
    """Fix public speech independently of the perturbed private grounding."""

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
        response = await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        if schema is not MeetingTurn:
            return response
        turn = MeetingTurn.model_validate_json(response.text)
        observations = turn.observations
        if agent_id == "p-3":
            # This is deliberate, possibly false speech. The listener must not
            # receive a truth certificate from p-3's private witness accessor.
            observations += (
                SawVentObservation(
                    type="saw_vent",
                    subject="p-4",
                    room="LABS",
                    tick=2,
                ),
            )
        if agent_id == "p-4":
            observations += (
                TaskActivityAccount(
                    type="task_activity",
                    task_id="upload_logs",
                    room="ADMIN",
                    from_tick=2,
                    to_tick=2,
                ),
            )
        return response.model_copy(
            update={
                "text": turn.model_copy(
                    update={"observations": observations}
                ).model_dump_json()
            }
        )


def _assert_real_noninterference(
    directory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = TacticalAgent.vent_witness_records_for_meeting
    captures: list[ScenarioCapture] = []
    for grounded in (False, True):

        def records(agent: TacticalAgent) -> tuple[VentWitnessRecord, ...]:
            if grounded and agent.agent_id == "p-3":
                return (VentWitnessRecord(subject="p-4", room="LABS", tick=2),)
            return original(agent)

        monkeypatch.setattr(TacticalAgent, "vent_witness_records_for_meeting", records)
        definition = scenario_definition("already_known_dead")
        captures.append(
            run_case(
                directory / str(grounded),
                case=definition.case,
                experiment_config=_config(),
                llm_client=_AttributedProvider(definition),
            )
        )
    before, after = captures
    first, second = _meetings(before)
    assert [row.tick for row in _meetings(before)] == [5, 8]
    assert before.result.final_state == after.result.final_state
    assert _meetings(before) == _meetings(after), (
        "private grounding changed public meeting artifacts"
    )
    for capture in captures:
        assert isinstance(capture.provider, _AttributedProvider)
    assert isinstance(before.provider, _AttributedProvider)
    assert isinstance(after.provider, _AttributedProvider)
    assert [p for actor, p in before.provider.prompts if actor == "p-2"] == [
        p for actor, p in after.provider.prompts if actor == "p-2"
    ]
    # The second public reader snapshot includes the actual first meeting fold.
    snapshots = [
        _loader(capture.replay_path.parent).get_meeting_memory(
            "headless-seed-1", second.meeting_id, "p-2"
        )
        for capture in captures
    ]
    assert snapshots[0] == snapshots[1]
    assert "p-3" in snapshots[0].rendered_memory_text
    assert (
        "attempted task activity for upload_logs" in snapshots[0].rendered_memory_text
    )
    assert "this does not certify task progress" in snapshots[0].rendered_memory_text
    assert first.contradictions  # Publicly incompatible accounts are retained.
    assert all(flag.evidence_band == "weak" for flag in first.contradictions)
    for capture in captures:
        memory = capture.agents["p-2"].memory
        reference = before.agents["p-2"].memory.beliefs
        assert memory.beliefs.known_players() == reference.known_players()
        assert [
            memory.beliefs.view(player) for player in reference.known_players()
        ] == [reference.view(player) for player in reference.known_players()]
        events = memory.episodic.recent(since_tick=0)
        for kind, speaker in (("saw_vent", "p-3"), ("task_activity", "p-4")):
            assert any(
                event.provenance == "reported"
                and event.type == "reported_testimony"
                and event.payload.get("kind") == kind
                and event.payload.get("speaker") == speaker
                and isinstance(event.payload.get("source_event_id"), str)
                for event in events
            )
        assert not any(
            event.provenance == "observed"
            and event.type == "saw_player"
            and event.payload.get("action") == "vent"
            for event in events
        )
        assert not any(
            event.provenance == "observed"
            and event.type == "completed_task"
            and event.payload.get("player_id") == "p-4"
            for event in events
        )


def test_real_game_and_reader_do_not_certify_other_speakers_private_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _assert_real_noninterference(tmp_path, monkeypatch)


def test_real_noninterference_gate_rejects_a_planted_private_grounding_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def planted(
        self: MeetingManager,
        transcript: MeetingTranscript,
        **kwargs: Any,
    ) -> Any:
        return tuple(
            flag.model_copy(update={"kind": "alibi_conflict", "evidence_band": "weak"})
            for flag in detect_contradictions(transcript, **kwargs)
        )

    monkeypatch.setattr(MeetingManager, "_detect_contradictions", planted)
    with pytest.raises(
        AssertionError, match="private grounding changed public meeting artifacts"
    ):
        _assert_real_noninterference(tmp_path, monkeypatch)


@pytest.mark.parametrize("case", ["witnessed_kill", "witnessed_vent"])
def test_genuine_own_direct_evidence_remains_reliable_in_attributed_mode(
    tmp_path: Path,
    case: Literal["witnessed_kill", "witnessed_vent"],
) -> None:
    capture = run_case(tmp_path, case=case, experiment_config=_config())
    assert capture.agents["p-2"].memory.beliefs.view("p-4").suspicion == 1.0
    (meeting,) = _meetings(capture)
    own = _loader(tmp_path).get_meeting_memory(
        "headless-seed-1", meeting.meeting_id, "p-2"
    )
    assert next(row for row in own.beliefs if row.subject == "p-4").suspicion == 1.0
    assert "You witnessed p-4" in own.rendered_memory_text
    assert not any(flag.kind == "vent_sighting" for flag in meeting.contradictions)


@pytest.mark.parametrize("common,attributed", [(1, None), (None, 1), (1, 1)])
def test_independent_account_profiles_reconstruct_real_completed_games(
    tmp_path: Path,
    common: Literal[1] | None,
    attributed: Literal[1] | None,
) -> None:
    capture = run_case(
        tmp_path,
        case="honest",
        experiment_config=_config(common=common, attributed=attributed),
    )
    replay = _loader(tmp_path).load_replay("headless-seed-1")
    assert replay.metadata.outcome_verified
    assert replay.metadata.completion_status == "completed"
    assert all(
        ballot.target == "SKIP" for row in _meetings(capture) for ballot in row.ballots
    )
    assert len(_meetings(capture)) == 1


def test_real_late_reporter_charge_gets_one_reply_before_voting(tmp_path: Path) -> None:
    off = run_case(
        tmp_path / "off", case="late_accusation", experiment_config=_config()
    )
    on = run_case(
        tmp_path / "on", case="late_accusation", experiment_config=_config(reply=1)
    )
    (before,), (after,) = _meetings(off), _meetings(on)
    assert [turn.speaker for turn in before.transcript.turns] == ["p-2", "p-4", "p-3"]
    assert [turn.speaker for turn in after.transcript.turns] == [
        "p-2",
        "p-4",
        "p-3",
        "p-2",
    ]
    assert after.transcript.turns[-1].reply_to == after.transcript.turns[-2].turn_id
    assert len(after.llm_calls) == len(before.llm_calls) + 1
    assert after.ballots == before.ballots
    assert (
        _loader(on.replay_path.parent)
        .load_replay("headless-seed-1")
        .metadata.outcome_verified
    )


@pytest.mark.parametrize("source", ["valid", "missing", "invalid"])
def test_served_report_identity_is_bound_to_actual_recording(
    tmp_path: Path, source: Literal["valid", "missing", "invalid"]
) -> None:
    capture = run_case(tmp_path, case="honest", experiment_config=_config())
    report = build_tournament_eval_report(
        load_tournament_report(
            tmp_path,
            roles_by_seed={
                1: {
                    pid: player.role
                    for pid, player in capture.result.final_state.players.items()
                }
            },
            tasks_per_crewmate=1,
        )
    ).model_dump(mode="json")
    # A self-consistent serialized group is still not evidence of runtime identity.
    for row in (*report["report"]["games"], *report["report"]["provenance_groups"]):
        row["agent_factory_kind"] = "scripted"
        row["experiment_config"] = None
    (tmp_path / "tournament-eval-report.json").write_text(json.dumps(report))
    if source == "missing":
        capture.replay_path.unlink()
    elif source == "invalid":
        rows = [
            json.loads(line) for line in capture.replay_path.read_text().splitlines()
        ]
        rows[0]["state_hash"] = "forged-state"
        capture.replay_path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    rebound = _loader(tmp_path).tournament_report()
    (game,) = rebound.report.games
    assert game.agent_factory_kind == ("custom" if source == "valid" else None)
    assert game.experiment_config == (_config() if source == "valid" else None)
    assert game.outcome_verified is (source == "valid")
    assert rebound.report.provenance_groups == build_provenance_groups(
        rebound.report.games
    )
    # Old metric cells remain descriptive; the source identity correction is narrow.
    assert rebound.deduction.model_dump(mode="json") == report["deduction"]
