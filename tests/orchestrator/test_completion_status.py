"""Normal runner stops carry evidence that interrupted historical prefixes lack."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest

from api.replay_loader import ReplayLoader
from agents.base import AgentInterface
from engine.entities import PlayerId, Role
from engine.world import WorldState, load_canonical_map
from eval.balance_eval import load_tournament_report
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from observation.action_intent import ActionIntent, EmergencyMeetingIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    HeadlessGame,
    MeetingArtifacts,
    build_default_agent_factory,
)
from orchestrator.replay import GameStopReplayEntry, read_all_entries
from orchestrator.replay_integrity import ReplayIntegrityError
from orchestrator.scheduler import TickScheduler
from tests.orchestrator.test_replay_integrity import (
    _game,
    completed_recording as completed_recording,
)


@pytest.mark.parametrize("ticks", [1, 5])
def test_real_tick_limit_has_explicit_nonterminal_stop(
    tmp_path: Path, ticks: int
) -> None:
    path = tmp_path / "replay-seed-1.jsonl"
    result = _game(path, max_ticks=ticks).run()
    stop = read_all_entries(path)[-1]
    assert isinstance(stop, GameStopReplayEntry)
    assert stop.tick == result.final_state.tick == ticks
    assert stop.reason == result.outcome == "TICK_BUDGET_REACHED"
    replay = ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert replay.metadata.completion_status == "tick_limited"
    assert replay.metadata.winner is None
    assert replay.metadata.outcome_verified is False


def test_meeting_phase_stop_matches_actual_unresolved_meeting(tmp_path: Path) -> None:
    path = tmp_path / "replay-seed-1.jsonl"
    result = HeadlessGame(
        seed=1,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=200),
    ).run()
    stop = read_all_entries(path)[-1]
    assert isinstance(stop, GameStopReplayEntry)
    assert stop.reason == "MEETING_PHASE_REACHED"
    assert stop.tick == result.final_state.tick
    assert (
        ReplayLoader(tmp_path).load_replay("headless-seed-1").metadata.completion_status
        == "unfinished"
    )


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ("tick", "stop_tick_mismatch"),
        ("reason", "stop_reason_mismatch"),
        ("duplicate", "row_order"),
        ("continuation", "row_order"),
        ("conflict", "row_order"),
        ("winner", None),
    ],
)
def test_stop_claims_cannot_rewrite_chronology(
    tmp_path: Path,
    mutation: str,
    code: str | None,
) -> None:
    path = tmp_path / "replay-seed-1.jsonl"
    _game(path, max_ticks=5).run()
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if mutation == "tick":
        rows[-1]["tick"] += 1
    elif mutation == "reason":
        rows[-1]["reason"] = "MEETING_PHASE_REACHED"
    elif mutation == "duplicate":
        rows.append(dict(rows[-1]))
    elif mutation == "continuation":
        continuation = dict(rows[0])
        continuation["tick"] = 5
        rows.append(continuation)
    elif mutation == "conflict":
        rows.append(
            {
                "kind": "game_over",
                "game_id": "headless-seed-1",
                "tick": 5,
                "winner": "CREWMATES",
                "reason": "CREWMATE_TASKS",
            }
        )
    else:
        rows[-1]["winner"] = "CREWMATES"
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    with pytest.raises(ValueError) as exc:
        ReplayLoader(tmp_path).load_replay("headless-seed-1")
    if code is not None:
        assert isinstance(exc.value, ReplayIntegrityError)
        assert exc.value.code == code


def test_stop_cannot_replace_real_terminal_outcome(
    completed_recording: Path, tmp_path: Path
) -> None:
    rows = [json.loads(line) for line in completed_recording.read_text().splitlines()]
    rows[-1] = {
        "kind": "game_stopped",
        "game_id": "headless-seed-1",
        "tick": rows[-1]["tick"] + 1,
        "reason": "TICK_BUDGET_REACHED",
    }
    path = tmp_path / completed_recording.name
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    with pytest.raises(ReplayIntegrityError) as exc:
        ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert exc.value.code == "recorded_outcome_mismatch"


def test_old_prefix_without_stop_is_unfinished(tmp_path: Path) -> None:
    path = tmp_path / "replay-seed-1.jsonl"
    _game(path, max_ticks=5).run()
    lines = path.read_text().splitlines()
    path.write_text("\n".join(lines[:-1]) + "\n")
    metadata = ReplayLoader(tmp_path).load_replay("headless-seed-1").metadata
    assert metadata.completion_status == "unfinished"
    assert metadata.outcome_verified is False


@dataclass(frozen=True)
class _BoundaryAgent:
    agent_id: str

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        if self.agent_id == "p-1" and packet.tick == 0:
            return EmergencyMeetingIntent(type="emergency", actor=self.agent_id)
        return WaitIntent(type="wait", actor=self.agent_id)


def _boundary_factory(agent_id: PlayerId, role: Role) -> AgentInterface:
    return _BoundaryAgent(agent_id)


@dataclass(frozen=True)
class _BoundaryMeeting:
    eject: bool

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        target = (
            next(
                pid
                for pid, player in state.players.items()
                if player.role == "CREWMATE"
            )
            if self.eject
            else None
        )
        return MeetingArtifacts(
            result=MeetingResult(
                meeting_id=meeting_id,
                triggered_by=trigger.triggered_by,
                trigger_tick=trigger.trigger_tick,
                outcome="EJECTED" if self.eject else "SKIPPED",
                ejected_player_id=target,
                ballots=tuple(
                    VoteBallot(
                        voter=pid,
                        target=target
                        if target is not None and pid != target
                        else "SKIP",
                        confidence=1.0,
                        primary_reason_id=None,
                        considered_alternatives=(),
                        rationale_text="scripted boundary vote",
                    )
                    for pid in state.players
                ),
                transcript=MeetingTranscript(),
            ),
            llm_calls=(),
            prompt_versions={},
        )


@pytest.mark.parametrize("eject", [False, True])
@pytest.mark.parametrize("reader", ["api", "eval"])
@pytest.mark.parametrize("forged_tick", [False, True])
def test_stop_after_resolved_meeting_uses_actual_post_application_state(
    tmp_path: Path,
    eject: bool,
    reader: str,
    forged_tick: bool,
) -> None:
    path = tmp_path / "replay-seed-2026.jsonl"
    result = HeadlessGame(
        seed=2026,
        num_players=4,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=_boundary_factory,
        replay_path=path,
        scheduler=TickScheduler(max_ticks=1),
        meeting_runner=_BoundaryMeeting(eject=eject),
    ).run()
    assert result.outcome == "TICK_BUDGET_REACHED"
    assert result.final_state.phase == "PLAY"
    assert result.final_state.tick == 1
    assert read_all_entries(path)[-1].tick == 1
    if forged_tick:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[-1]["tick"] = 0  # the trigger state before applying the meeting
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    def load_status() -> str:
        if reader == "api":
            return (
                ReplayLoader(tmp_path)
                .load_replay("headless-seed-2026")
                .metadata.completion_status
            )
        report = load_tournament_report(
            tmp_path,
            roles_by_seed={
                2026: {
                    pid: player.role
                    for pid, player in result.final_state.players.items()
                }
            },
            tasks_per_crewmate=1,
        )
        return report.games[0].completion_status

    if forged_tick:
        with pytest.raises(ReplayIntegrityError) as exc:
            load_status()
        assert exc.value.code == "stop_tick_mismatch"
    else:
        assert load_status() == "tick_limited"
