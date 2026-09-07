"""Exercise the comparison through genuine recorded games and adversarial inputs."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from api.replay_loader import ReplayLoader
from engine.actions import KillAction, MoveAction
from engine.tick import advance_tick
from engine.world import load_canonical_map
from experiments.tactical_gameplay import (
    Roster,
    candidate_configs,
    measure_replay,
    permute_state_and_actions,
    run_candidate,
)
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import HeadlessGame, build_default_agent_factory
from orchestrator.replay import GameEndReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state


@pytest.mark.parametrize(
    "arm",
    [
        "baseline",
        "workload",
        "meeting_reset",
        "patrol",
        "vent_risk",
        "self_report",
        "earlier_sabotage",
        "post_meeting",
    ],
)
def test_genuine_candidate_reconstructs_in_api_and_repeats(
    tmp_path: Path, arm: str
) -> None:
    roster = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)
    metrics = []
    for name in ("first", "repeat"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "roster.json").write_text(
            roster.model_dump_json(), encoding="utf-8"
        )
        path = directory / "replay-seed-1000.jsonl"
        row = run_candidate(
            seed=1000, roster=roster, config=candidate_configs()[arm], replay_path=path
        )
        metrics.append(row)
        assert row.error is None and row.completion_status == "completed"
        assert row.model_calls > 0 and row.input_tokens > 0
        assert row.reported_cost_usd == 0
        replay = ReplayLoader(directory).load_replay("headless-seed-1000")
        assert replay.metadata.outcome_verified
        assert replay.metadata.winner == row.winner
        raw = [json.loads(line) for line in path.read_text().splitlines()]
        ticks = [entry for entry in raw if entry["kind"] == "tick"]
        assert all(
            ("experiment_config" in entry) == (arm != "baseline") for entry in ticks
        )
    assert metrics[0] == metrics[1]


def test_a_call_limit_retains_partial_meeting_usage_without_a_fake_outcome(
    tmp_path: Path,
) -> None:
    roster = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)
    path = tmp_path / "replay-seed-1000.jsonl"
    row = run_candidate(
        seed=1000,
        roster=roster,
        config=candidate_configs()["baseline"],
        replay_path=path,
        max_calls=1,
    )
    assert row.completion_status == "aborted"
    assert row.winner is None and row.reason is None
    assert row.model_calls == 1 and row.input_tokens > 0 and row.output_tokens > 0
    assert row.error is not None and "model-call limit" in row.error
    assert not any(
        isinstance(entry, GameEndReplayEntry) for entry in read_all_entries(path)
    )


def test_harness_refuses_a_forged_winner(tmp_path: Path) -> None:
    roster = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)
    path = tmp_path / "replay-seed-1000.jsonl"
    run_candidate(
        seed=1000,
        roster=roster,
        config=candidate_configs()["baseline"],
        replay_path=path,
    )
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[-1]["winner"] = "CREWMATES"
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="outcome"):
        measure_replay(path, seed=1000, roster=roster)


def test_a_tactical_claim_cannot_use_an_unchanged_factory(tmp_path: Path) -> None:
    game = HeadlessGame(
        seed=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=tmp_path / "replay-seed-1.jsonl",
        experiment_config=RecordedExperimentConfig(crew_idle_policy="patrol"),
    )
    with pytest.raises(ValueError, match="factory does not implement"):
        game.run()
    assert list(tmp_path.iterdir()) == []


def test_identity_intervention_keeps_roles_and_intentions_attached() -> None:
    game_map = load_canonical_map()
    state = seed_initial_state(seed=2, game_map=game_map, num_players=5)
    players = {
        pid: replace(player, role="IMPOSTOR" if pid == "p-2" else "CREWMATE")
        for pid, player in state.players.items()
    }
    state = replace(state, players=players, cooldowns={"p-2": 0})
    move = MoveAction.model_validate(
        {
            "type": "move",
            "actor": "p-1",
            "payload": {"to_room": game_map.room_neighbors(game_map.spawn.room)[0]},
        }
    )
    kill = KillAction.model_validate(
        {"type": "kill", "actor": "p-2", "payload": {"target": "p-1"}}
    )
    baseline, _ = advance_tick(state, (move, kill), game_map=game_map)
    assert baseline.players["p-1"].alive
    permutation = {pid: pid for pid in players}
    permutation.update({"p-1": "p-2", "p-2": "p-1"})
    renamed, actions = permute_state_and_actions(state, (move, kill), permutation)
    assert renamed.players["p-1"].role == "IMPOSTOR"
    assert renamed.players["p-2"].role == "CREWMATE"
    assert renamed.rng_state == state.rng_state
    assert actions[0].actor == "p-1" and actions[0].type == "kill"
    assert actions[0].payload.target == "p-2"
    alternate, _ = advance_tick(renamed, actions, game_map=game_map)
    assert not alternate.players["p-2"].alive
    restored, restored_actions = permute_state_and_actions(
        renamed, actions, permutation
    )
    assert restored == state and restored_actions == (move, kill)
    with pytest.raises(ValueError, match="bijection"):
        permute_state_and_actions(state, (move, kill), {"p-1": "p-2"})


def test_identity_instrument_refuses_an_experimental_engine(tmp_path: Path) -> None:
    from experiments.tactical_gameplay import measure_identity_effects

    roster = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)
    path = tmp_path / "replay-seed-1000.jsonl"
    run_candidate(
        seed=1000,
        roster=roster,
        config=candidate_configs()["workload"],
        replay_path=path,
    )
    with pytest.raises(ValueError, match="experiment"):
        measure_identity_effects(path, seed=1000, roster=roster)


def test_runtime_fingerprint_includes_rendered_templates_and_dependencies(
    tmp_path: Path,
) -> None:
    from experiments.tactical_gameplay import runtime_fingerprint

    # The helper fingerprints its own absolute file as well; keep the real
    # repository root and temporarily substitute bytes only at the read seam.
    from unittest.mock import patch

    root = Path(__file__).resolve().parents[2]
    initial = runtime_fingerprint(root)
    actual_read = Path.read_bytes
    for suffix in (".j2", "uv.lock"):

        def changed_read(path: Path) -> bytes:
            raw = actual_read(path)
            return raw + b"\nchanged" if str(path).endswith(suffix) else raw

        with patch.object(Path, "read_bytes", changed_read):
            assert runtime_fingerprint(root) != initial


def test_source_identity_binds_the_exact_consumed_roster_before_running(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import experiments.tactical_gameplay as instrument

    root = Path(__file__).resolve().parents[2]
    roster_path = root / "replays/samples/9p2i/roster.json"
    actual_read = Path.read_bytes
    reads = 0

    def transient_roster(path: Path) -> bytes:
        nonlocal reads
        raw = actual_read(path)
        if path == roster_path:
            reads += 1
            if reads == 2:
                # The first fingerprint saw the actual two-task roster. The
                # consuming read sees a transient three-task replacement, then
                # the source returns to its original bytes. Hashes alone would
                # miss this A -> B -> A replacement; exact consumed bytes matter.
                altered = json.loads(raw)
                altered["tasks_per_crewmate"] = 3
                return json.dumps(altered).encode()
        return raw

    def no_game_work(**kwargs: object) -> None:
        pytest.fail("input mismatch must be refused before any candidate runs")

    monkeypatch.setattr(Path, "read_bytes", transient_roster)
    monkeypatch.setattr(instrument, "run_candidate", no_game_work)
    with pytest.raises(RuntimeError, match="inputs changed"):
        instrument.build_comparison(split="development", arms=("baseline",))
    assert reads >= 3
