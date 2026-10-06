"""Exercise the comparison through genuine recorded games and adversarial inputs."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from itertools import combinations
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, get_args

import pytest
from hypothesis import Phase, example, given, settings
from hypothesis import strategies as st

import engine.rules as engine_rules
import experiments.tactical_gameplay as lab
from api.replay_loader import ReplayLoader
from engine.actions import Action, KillAction, MoveAction
from engine.entities import PlayerState, TaskState
from engine.events import EngineEvent, KilledEvent
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from eval.replay_walk import TickAdvanced
from experiments.tactical_gameplay import (
    Roster,
    candidate_configs,
    measure_replay,
    permute_state_and_actions,
    run_candidate,
)
from orchestrator.experiment_config import RecordedExperimentConfig, engine_arguments
from orchestrator.game import HeadlessGame, build_default_agent_factory
from orchestrator.replay import GameEndReplayEntry, ReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state


#: The arms whose seed-1000 game holds no meeting on this roster, with a seed
#: whose game does, so every arm's reconstruction includes a meeting.
_SEED_WITH_A_MEETING: dict[str, int] = {
    "stage_b_full_kill_cooldown_6": 1001,
    "stage_b_full_kill_cooldown_6_patrol": 1001,
    "stage_b_full_kill_cooldown_6_accompany": 1001,
}


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
        "vent_physical",
        "vent_look_and_wait",
        "vent_own_fresh_kill",
        "stage_b_full",
        "stage_b_full_minus_look_and_wait",
        "stage_b_full_minus_own_fresh_kill",
        "stage_b_full_minus_physical",
        "stage_b_full_minus_hub_with_grace",
        "stage_b_full_kill_cooldown_6",
        "stage_b_full_kill_cooldown_8",
        "stage_b_full_kill_cooldown_6_patrol",
        "stage_b_full_kill_cooldown_6_accompany",
    ],
)
def test_genuine_candidate_reconstructs_in_api_and_repeats(
    tmp_path: Path, arm: str
) -> None:
    roster = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)
    seed = _SEED_WITH_A_MEETING.get(arm, 1000)
    metrics = []
    for name in ("first", "repeat"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "roster.json").write_text(
            roster.model_dump_json(), encoding="utf-8"
        )
        path = directory / f"replay-seed-{seed}.jsonl"
        row = run_candidate(
            seed=seed, roster=roster, config=candidate_configs()[arm], replay_path=path
        )
        metrics.append(row)
        assert row.error is None and row.completion_status == "completed"
        assert row.model_calls > 0 and row.input_tokens > 0
        assert row.reported_cost_usd == 0
        replay = ReplayLoader(directory).load_replay(f"headless-seed-{seed}")
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


# --- The idle-policy cross ---------------------------------------------------


def _cross_problems(configs: Mapping[str, RecordedExperimentConfig]) -> list[str]:
    """Each cross arm must be the reference arm's payload plus its one policy."""

    reference = configs[lab.STAGE_B_IDLE_REFERENCE].model_dump()
    problems: list[str] = []
    for name, policy in lab.STAGE_B_IDLE_POLICIES.items():
        dumped = configs[name].model_dump()
        differing = sorted(
            key
            for key in set(dumped) | set(reference)
            if dumped.get(key) != reference.get(key)
        )
        if differing != ["crew_idle_policy"] or dumped["crew_idle_policy"] != policy:
            problems.append(
                f"{name}: differs in {differing} with "
                f"crew_idle_policy={dumped['crew_idle_policy']!r}"
            )
    return problems


def test_the_cross_arms_are_the_reference_arm_plus_one_idle_policy() -> None:
    configs = candidate_configs()
    field = RecordedExperimentConfig.model_fields["crew_idle_policy"]
    # The cross covers every idle policy the field declares but its default,
    # which the reference arm holds.
    assert set(lab.STAGE_B_IDLE_POLICIES.values()) == set(
        get_args(field.annotation)
    ) - {field.default}
    assert configs[lab.STAGE_B_IDLE_REFERENCE].crew_idle_policy == field.default
    assert lab.STAGE_B_IDLE_REFERENCE in lab.STAGE_B_KILL_COOLDOWNS
    for name, policy in lab.STAGE_B_IDLE_POLICIES.items():
        assert name == f"{lab.STAGE_B_IDLE_REFERENCE}_{policy}"
        assert configs[name].model_dump() == {
            **configs[lab.STAGE_B_IDLE_REFERENCE].model_dump(),
            "crew_idle_policy": policy,
        }
    assert _cross_problems(configs) == []


def test_a_cross_arm_without_the_cooldown_or_at_hub_wait_fails() -> None:
    """Planted: one arm built from ``stage_b_full``; another at ``hub_wait``."""

    configs = candidate_configs()
    dropped = dict(configs)
    dropped["stage_b_full_kill_cooldown_6_patrol"] = (
        RecordedExperimentConfig.model_validate(
            {**configs["stage_b_full"].model_dump(), "crew_idle_policy": "patrol"}
        )
    )
    assert _cross_problems(dropped) == [
        "stage_b_full_kill_cooldown_6_patrol: differs in "
        "['crew_idle_policy', 'kill_cooldown_ticks'] with crew_idle_policy='patrol'"
    ]
    hub = dict(configs)
    hub["stage_b_full_kill_cooldown_6_accompany"] = (
        RecordedExperimentConfig.model_validate(
            {
                **configs[lab.STAGE_B_IDLE_REFERENCE].model_dump(),
                "crew_idle_policy": "hub_wait",
            }
        )
    )
    assert _cross_problems(hub) == [
        "stage_b_full_kill_cooldown_6_accompany: differs in [] with "
        "crew_idle_policy='hub_wait'"
    ]


def test_the_cross_arms_follow_the_cooldown_dial(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Source change: the reference arm's cooldown moves and the cross follows."""

    monkeypatch.setattr(
        lab,
        "STAGE_B_KILL_COOLDOWNS",
        MappingProxyType(
            {"stage_b_full_kill_cooldown_6": 7, "stage_b_full_kill_cooldown_8": 8}
        ),
    )
    configs = candidate_configs()
    assert configs[lab.STAGE_B_IDLE_REFERENCE].kill_cooldown_ticks == 7
    for name in lab.STAGE_B_IDLE_POLICIES:
        assert configs[name].kill_cooldown_ticks == 7
    assert _cross_problems(configs) == []


# --- The split table ---------------------------------------------------------


def _split_problems(splits: Mapping[str, tuple[int, ...]]) -> list[str]:
    problems: list[str] = []
    held_out = set(splits["held_out"])
    for name, seeds in splits.items():
        if len(set(seeds)) != len(seeds):
            problems.append(f"{name} repeats a seed")
        if name.startswith("development") and held_out & set(seeds):
            problems.append(f"{name} reaches the held-out seeds")
    development = splits["development"]
    if splits["development_wide"][: len(development)] != development:
        problems.append("development_wide does not begin with development")
    return problems


def test_the_split_table_keeps_development_apart_from_held_out() -> None:
    assert dict(lab.SPLIT_SEEDS) == {
        "development": tuple(range(1000, 1008)),
        "held_out": tuple(range(2000, 2016)),
        "development_wide": tuple(range(1000, 1100)),
    }
    assert _split_problems(lab.SPLIT_SEEDS) == []


def test_a_wide_split_reaching_the_held_out_seeds_fails() -> None:
    planted = {**lab.SPLIT_SEEDS, "development_wide": tuple(range(1000, 2001))}
    assert _split_problems(planted) == ["development_wide reaches the held-out seeds"]
    shifted = {**lab.SPLIT_SEEDS, "development_wide": tuple(range(1001, 1100))}
    assert _split_problems(shifted) == [
        "development_wide does not begin with development"
    ]


@pytest.mark.parametrize("split", ["held-out", "Development", "", "development "])
def test_an_unknown_split_is_refused_before_any_game(
    monkeypatch: pytest.MonkeyPatch, split: str
) -> None:
    def no_work(*args: object, **kwargs: object) -> None:
        pytest.fail("an unknown split must be refused before any work")

    monkeypatch.setattr(lab, "run_candidate", no_work)
    monkeypatch.setattr(lab, "runtime_fingerprint", no_work)
    with pytest.raises(ValueError, match=re.escape(f"unknown split {split!r}")):
        lab.build_comparison(split=split, arms=("baseline",))


def test_the_command_line_offers_exactly_the_declared_splits(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: list[str] = []

    def record(*, split: str, **kwargs: object) -> dict[str, Any]:
        seen.append(split)
        return {}

    monkeypatch.setattr(lab, "build_comparison", record)
    for split in lab.SPLIT_SEEDS:
        output = tmp_path / f"{split}.json"
        monkeypatch.setattr(
            sys, "argv", ["lab", "--output", str(output), "--split", split]
        )
        lab.main()
    assert seen == list(lab.SPLIT_SEEDS)
    monkeypatch.setattr(
        sys,
        "argv",
        ["lab", "--output", str(tmp_path / "x.json"), "--split", "held-out"],
    )
    with pytest.raises(SystemExit):
        lab.main()
    assert seen == list(lab.SPLIT_SEEDS)


# --- The whereabouts-coverage cell -------------------------------------------


def _player(
    player_id: str,
    room: str,
    *,
    role: Literal["CREWMATE", "IMPOSTOR"] = "CREWMATE",
    alive: bool = True,
    in_vent: bool = False,
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role=role,
        alive=alive,
        room=room,
        position=(0.0, 0.0),
        last_action=None,
        in_vent=in_vent,
    )


def _world(*players: PlayerState) -> WorldState:
    """The players on the canonical map; every impostor may kill at once."""

    owner = next(player.id for player in players if player.role == "CREWMATE")
    return WorldState(
        tick=10,
        phase="PLAY",
        map=load_canonical_map().id,
        players={player.id: player for player in players},
        bodies={},
        tasks={
            f"{owner}:swipe_card": TaskState(
                id=f"{owner}:swipe_card",
                owner=owner,
                map_task_id="swipe_card",
                room="ADMIN",
                progress=0,
                required_ticks=3,
                completed=False,
            )
        },
        sabotage=None,
        cooldowns={player.id: 0 for player in players if player.role == "IMPOSTOR"},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def _step(
    pre: WorldState,
    post: WorldState,
    events: Sequence[EngineEvent],
    actions: Sequence[Action] = (),
) -> TickAdvanced:
    return TickAdvanced(
        entry=ReplayEntry(game_id="g", tick=pre.tick, actions=(), state_hash="0"),
        pre_state=pre,
        state=post,
        events=tuple(events),
        actions=tuple(actions),
    )


def _move(actor: str, room: str) -> Action:
    return MoveAction.model_validate(
        {"type": "move", "actor": actor, "payload": {"to_room": room}}
    )


def _kill(actor: str, target: str) -> Action:
    return KillAction.model_validate(
        {"type": "kill", "actor": actor, "payload": {"target": target}}
    )


def _killed(actor: str, target: str, room: str) -> KilledEvent:
    return KilledEvent(
        type="Killed", tick=10, actor=actor, target=target, room=room, witnesses=()
    )


def test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered() -> (
    None
):
    state = _world(
        _player("p-1", "ADMIN"), _player("p-2", "ADMIN"), _player("p-3", "LABS")
    )
    assert lab.whereabouts_coverage(state) == (3, 2)
    alone = _world(_player("p-1", "ADMIN"), _player("p-2", "LABS"))
    assert lab.whereabouts_coverage(alone) == (2, 0)


def test_a_vented_player_covers_nothing_and_is_not_covered() -> None:
    state = _world(
        _player("p-1", "ADMIN", role="IMPOSTOR", in_vent=True),
        _player("p-2", "ADMIN"),
    )
    assert lab.whereabouts_coverage(state) == (2, 0)


def test_a_dead_player_covers_nothing_and_is_not_a_subject() -> None:
    state = _world(_player("p-1", "ADMIN", alive=False), _player("p-2", "ADMIN"))
    assert lab.whereabouts_coverage(state) == (1, 0)


def test_a_tick_without_a_kill_adds_only_to_the_play_tick_pair() -> None:
    state = _world(
        _player("p-1", "ADMIN", role="IMPOSTOR"),
        _player("p-2", "ADMIN"),
        _player("p-3", "LABS"),
    )
    counts: Counter[str] = Counter()
    lab.fold_whereabouts(_step(state, state, ()), counts)
    assert dict(counts) == {
        "whereabouts_subjects_at_play_ticks": 3,
        "whereabouts_covered_at_play_ticks": 2,
    }


def test_a_tick_with_two_kills_counts_its_players_once() -> None:
    state = _world(
        _player("p-1", "ADMIN", role="IMPOSTOR"),
        _player("p-2", "LABS", role="IMPOSTOR"),
        _player("p-3", "ADMIN"),
        _player("p-4", "LABS"),
        _player("p-5", "ADMIN", alive=False),
        _player("p-6", "LABS", alive=False),
    )
    kills = (_killed("p-1", "p-5", "ADMIN"), _killed("p-2", "p-6", "LABS"))
    counts: Counter[str] = Counter()
    lab.fold_whereabouts(_step(state, state, kills), counts)
    assert dict(counts) == {
        "whereabouts_subjects_at_play_ticks": 4,
        "whereabouts_covered_at_play_ticks": 4,
        "whereabouts_subjects_at_kill_ticks": 4,
        "whereabouts_covered_at_kill_ticks": 4,
    }


def test_the_state_the_tick_leaves_is_read() -> None:
    """A move joins two players: the post-tick state covers both, the pre none."""

    game_map = load_canonical_map()
    pre = _world(
        _player("p-1", "ADMIN"), _player("p-2", "WEST_HALL"), _player("p-3", "LABS")
    )
    post, events = advance_tick(
        pre, [_move("p-2", "ADMIN")], game_map=game_map, **engine_arguments(None)
    )
    assert lab.whereabouts_coverage(pre) == (3, 0)
    counts: Counter[str] = Counter()
    lab.fold_whereabouts(_step(pre, post, events), counts)
    assert counts["whereabouts_covered_at_play_ticks"] == 2


def test_every_row_carries_the_seven_counts_even_without_a_kill(
    tmp_path: Path,
) -> None:
    roster = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)
    row = run_candidate(
        seed=1000,
        roster=roster,
        config=candidate_configs()["baseline"],
        replay_path=tmp_path / "replay-seed-1000.jsonl",
        max_ticks=2,
    )
    assert row.counts.get("event:Killed", 0) == 0
    assert {
        key: row.counts[key] for key in lab.WHEREABOUTS_COUNTS + lab.KILL_WITNESS_COUNTS
    } == {
        "whereabouts_subjects_at_kill_ticks": 0,
        "whereabouts_covered_at_kill_ticks": 0,
        "whereabouts_subjects_at_play_ticks": 8,
        "whereabouts_covered_at_play_ticks": 6,
        "crew_kill_witnesses": 0,
        "crew_kill_witnesses_walked_in": 0,
        "kills_with_walk_in_crew_witness": 0,
    }


_ROLES: tuple[Literal["CREWMATE", "IMPOSTOR"], ...] = ("CREWMATE", "IMPOSTOR")


@st.composite
def _coverage_states(draw: st.DrawFn) -> WorldState:
    """A seeded canonical-map state with random rooms, life, vents and roles."""

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=draw(st.integers(min_value=0, max_value=10_000)),
        game_map=game_map,
        num_players=draw(st.integers(min_value=2, max_value=9)),
    )
    rooms = sorted(game_map.rooms)
    room = st.one_of(st.sampled_from(rooms[:2]), st.sampled_from(rooms))
    players = {
        pid: replace(
            player,
            room=draw(room),
            alive=draw(st.booleans()),
            in_vent=draw(st.booleans()),
            role=draw(st.sampled_from(_ROLES)),
        )
        for pid, player in sorted(state.players.items())
    }
    return replace(state, players=players)


def _property_settings(*, perturbed: bool) -> dict[str, Any]:
    """The cell properties' settings; a perturbed run is reproducible and unshrunk.

    A perturbed run only has to fail, so it draws a fixed sequence of examples
    and stops at the first failure instead of shrinking it.
    """

    return {
        "deadline": None,
        "max_examples": 200,
        "database": None,
        "derandomize": perturbed,
        "phases": (Phase.generate,) if perturbed else tuple(Phase),
    }


def _with_impostors(state: WorldState, impostors: Sequence[str]) -> WorldState:
    return replace(
        state,
        players={
            pid: replace(player, role="IMPOSTOR" if pid in impostors else "CREWMATE")
            for pid, player in state.players.items()
        },
    )


def _role_blind_failures(
    helper: Callable[[WorldState], tuple[int, int]], state: WorldState
) -> list[tuple[str, ...]]:
    """Every assignment of the state's roles among its players that moves the result."""

    impostors = sum(player.role == "IMPOSTOR" for player in state.players.values())
    expected = helper(state)
    return [
        chosen
        for chosen in combinations(sorted(state.players), impostors)
        if helper(_with_impostors(state, chosen)) != expected
    ]


def _role_blind_property(
    helper: Callable[[WorldState], tuple[int, int]], *, perturbed: bool = False
) -> Callable[[], None]:
    @settings(**_property_settings(perturbed=perturbed))
    @given(_coverage_states())
    def check(state: WorldState) -> None:
        assert _role_blind_failures(helper, state) == []

    return check


def test_the_cell_is_unchanged_under_every_permutation_of_roles() -> None:
    _role_blind_property(lab.whereabouts_coverage)()


def _crew_observers_only(state: WorldState) -> tuple[int, int]:
    """Perturbed: a subject counts as covered only beside a living crewmate."""

    players = state.players
    covered = sum(
        1
        for pid, player in players.items()
        if player.alive
        and not player.in_vent
        and any(
            other_id != pid
            and other.alive
            and not other.in_vent
            and other.room == player.room
            and other.role == "CREWMATE"
            for other_id, other in players.items()
        )
    )
    return sum(player.alive for player in players.values()), covered


def test_a_cell_counting_only_crewmate_observers_fails_the_property() -> None:
    with pytest.raises(AssertionError):
        _role_blind_property(_crew_observers_only, perturbed=True)()


def _engine_rule_coverage(state: WorldState) -> tuple[int, int]:
    """The cell restated from the engine's kill-witness rule, subject by subject."""

    covered = sum(
        1
        for pid, player in state.players.items()
        if player.alive
        and not player.in_vent
        and engine_rules._witnesses_in_room(state, room=player.room, exclude={pid})
    )
    return sum(player.alive for player in state.players.values()), covered


def _pin_property(*, perturbed: bool = False) -> Callable[[], None]:
    @settings(**_property_settings(perturbed=perturbed))
    @given(_coverage_states())
    def check(state: WorldState) -> None:
        assert lab.whereabouts_coverage(state) == _engine_rule_coverage(state)
        # Room by room as well, so no two subjects' errors can cancel.
        for room in {player.room for player in state.players.values()}:
            alone = replace(
                state,
                players={
                    pid: player
                    for pid, player in state.players.items()
                    if player.room == room
                },
            )
            assert lab.whereabouts_coverage(alone) == _engine_rule_coverage(alone)

    return check


def test_the_cell_is_the_engines_kill_witness_rule() -> None:
    _pin_property()()


def test_a_witness_rule_that_admits_vented_players_breaks_the_pin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Source change: the engine's rule moves and the pin turns red."""

    def admitting_vented(
        state: WorldState, *, room: str, exclude: set[str]
    ) -> tuple[str, ...]:
        return tuple(
            sorted(
                pid
                for pid, player in state.players.items()
                if pid not in exclude and player.alive and player.room == room
            )
        )

    monkeypatch.setattr(engine_rules, "_witnesses_in_room", admitting_vented)
    with pytest.raises(AssertionError):
        _pin_property(perturbed=True)()


# --- The kill-witness rows ---------------------------------------------------


def _witness_counts(state: WorldState, actions: Sequence[Action]) -> dict[str, int]:
    """One planted tick through the engine, folded by the lab."""

    game_map = load_canonical_map()
    engine = engine_arguments(candidate_configs()[lab.STAGE_B_IDLE_REFERENCE])
    post, events = advance_tick(state, actions, game_map=game_map, **engine)
    assert any(isinstance(event, KilledEvent) for event in events)
    counts: Counter[str] = Counter()
    lab.fold_kill_witnesses(_step(state, post, events, actions), counts)
    return {key: counts[key] for key in lab.KILL_WITNESS_COUNTS}


def _kill_scene(*bystanders: PlayerState) -> WorldState:
    """``p-1`` kills ``p-2`` in ADMIN; ``p-8`` and ``p-9`` keep the crew ahead."""

    return _world(
        _player("p-1", "ADMIN", role="IMPOSTOR"),
        _player("p-2", "ADMIN"),
        *bystanders,
        _player("p-8", "LABS"),
        _player("p-9", "LABS"),
    )


@pytest.mark.parametrize(
    ("bystander", "actions", "expected"),
    [
        pytest.param(
            _player("p-3", "ADMIN"),
            (_kill("p-1", "p-2"),),
            (1, 0, 0),
            id="already-in-the-room",
        ),
        pytest.param(
            _player("p-3", "WEST_HALL"),
            (_kill("p-1", "p-2"), _move("p-3", "ADMIN")),
            (0, 0, 0),
            id="moves-in-after-the-kill",
        ),
        pytest.param(
            _player("p-3", "ADMIN"),
            (_move("p-3", "WEST_HALL"), _kill("p-1", "p-2")),
            (0, 0, 0),
            id="leaves-before-the-kill",
        ),
        pytest.param(
            _player("p-3", "ADMIN"),
            (_move("p-3", "ADMIN"), _kill("p-1", "p-2")),
            (1, 0, 0),
            id="moves-to-its-own-room",
        ),
        pytest.param(
            _player("p-3", "WEST_HALL"),
            (_move("p-3", "ADMIN"), _kill("p-1", "p-2")),
            (1, 1, 1),
            id="walks-in-before-the-kill",
        ),
        pytest.param(
            _player("p-3", "WEST_HALL", role="IMPOSTOR"),
            (_move("p-3", "ADMIN"), _kill("p-1", "p-2")),
            (0, 0, 0),
            id="an-impostor-walks-in",
        ),
    ],
)
def test_a_kill_witness_walked_in_only_from_another_room_before_the_kill(
    bystander: PlayerState,
    actions: tuple[Action, ...],
    expected: tuple[int, int, int],
) -> None:
    counts = _witness_counts(_kill_scene(bystander), actions)
    assert tuple(counts[key] for key in lab.KILL_WITNESS_COUNTS) == expected


def test_walk_ins_count_per_witness_and_once_per_kill() -> None:
    state = _kill_scene(
        _player("p-3", "WEST_HALL"),
        _player("p-4", "EAST_HALL"),
        _player("p-5", "ADMIN"),
    )
    actions = (_move("p-3", "ADMIN"), _move("p-4", "ADMIN"), _kill("p-1", "p-2"))
    assert _witness_counts(state, actions) == {
        "crew_kill_witnesses": 3,
        "crew_kill_witnesses_walked_in": 2,
        "kills_with_walk_in_crew_witness": 1,
    }


def test_a_walk_in_is_read_against_the_kills_own_room() -> None:
    """A kill in MEDBAY: a walk into MEDBAY counts, a walk into ADMIN does not."""

    state = _world(
        _player("p-1", "MEDBAY", role="IMPOSTOR"),
        _player("p-2", "MEDBAY"),
        _player("p-3", "LABS"),
        _player("p-4", "WEST_HALL"),
        _player("p-8", "REACTOR"),
        _player("p-9", "REACTOR"),
    )
    actions = (_move("p-3", "MEDBAY"), _move("p-4", "ADMIN"), _kill("p-1", "p-2"))
    assert _witness_counts(state, actions) == {
        "crew_kill_witnesses": 1,
        "crew_kill_witnesses_walked_in": 1,
        "kills_with_walk_in_crew_witness": 1,
    }


@st.composite
def _kill_ticks(draw: st.DrawFn) -> tuple[WorldState, tuple[Action, ...]]:
    """A kill room, killers and victims in it, and bystanders moving about it."""

    game_map = load_canonical_map()
    rooms = sorted(game_map.rooms)
    kill_room = draw(st.sampled_from(rooms))
    near = (kill_room, *game_map.room_neighbors(kill_room))
    killers = draw(st.integers(min_value=1, max_value=2))
    players = [_player(f"p-{i}", kill_room, role="IMPOSTOR") for i in range(killers)]
    players += [_player(f"p-{i}", kill_room) for i in range(killers, 2 * killers)]
    actions: list[Action] = [
        _kill(f"p-{i}", f"p-{i + killers}") for i in range(killers)
    ]
    for index in range(2 * killers, 2 * killers + draw(st.integers(0, 6))):
        pid = f"p-{index}"
        room = draw(st.sampled_from(near))
        players.append(_player(pid, room, role=draw(st.sampled_from(_ROLES))))
        here = (room, *game_map.room_neighbors(room))
        if draw(st.booleans()):
            actions.append(_move(pid, draw(st.sampled_from(here))))
    players += [_player("p-90", "REACTOR"), _player("p-91", "REACTOR")]
    order = draw(st.permutations(actions))
    return _world(*players), tuple(order)


@settings(deadline=None, max_examples=200)
@given(_kill_ticks())
def test_walk_ins_never_exceed_the_crew_witnesses(
    scene: tuple[WorldState, tuple[Action, ...]],
) -> None:
    state, actions = scene
    game_map = load_canonical_map()
    post, events = advance_tick(
        state, actions, game_map=game_map, **engine_arguments(None)
    )
    counts: Counter[str] = Counter()
    lab.fold_kill_witnesses(_step(state, post, events, actions), counts)
    kills = [event for event in events if isinstance(event, KilledEvent)]
    crew_witnessed = sum(
        any(state.players[pid].role == "CREWMATE" for pid in kill.witnesses)
        for kill in kills
    )
    assert counts["kills_with_walk_in_crew_witness"] <= crew_witnessed
    assert counts["crew_kill_witnesses_walked_in"] <= counts["crew_kill_witnesses"]
    assert counts["crew_kill_witnesses"] <= sum(len(kill.witnesses) for kill in kills)


@settings(deadline=None, max_examples=6, database=None)
@given(
    seed=st.integers(min_value=1000, max_value=1099),
    arm=st.sampled_from(
        (lab.STAGE_B_IDLE_REFERENCE, *lab.STAGE_B_IDLE_POLICIES, "stage_b_full")
    ),
)
# A game with a crew-witnessed kill a crewmate walked in on, so every bound
# below is read on counts the folds actually moved.
@example(seed=1000, arm=lab.STAGE_B_IDLE_REFERENCE)
def test_on_lab_games_walk_ins_stay_within_crew_witnessed_kills(
    seed: int, arm: str
) -> None:
    roster = Roster(num_players=9, num_impostors=2, tasks_per_crewmate=2)
    with tempfile.TemporaryDirectory(prefix="ailibi-walk-in-") as directory:
        counts = run_candidate(
            seed=seed,
            roster=roster,
            config=candidate_configs()[arm],
            replay_path=Path(directory) / f"replay-seed-{seed}.jsonl",
        ).counts
    assert counts["kills_with_walk_in_crew_witness"] <= counts["kills_crew_witnessed"]
    # A kill a crewmate witnessed has at least one crew witness.
    assert counts["kills_crew_witnessed"] <= counts["crew_kill_witnesses"]
    assert counts["crew_kill_witnesses_walked_in"] <= counts["crew_kill_witnesses"]
    assert counts["kills_crew_witnessed"] <= counts.get("event:Killed", 0)
    # A kill tick has a subject, its killer, and every play tick has one.
    assert (counts["whereabouts_subjects_at_kill_ticks"] > 0) == (
        counts.get("event:Killed", 0) > 0
    )
    assert counts["whereabouts_subjects_at_play_ticks"] >= counts["tick_rows"]
    assert (
        counts["whereabouts_covered_at_kill_ticks"]
        <= (counts["whereabouts_subjects_at_kill_ticks"])
    )


# --- The summaries -----------------------------------------------------------

_REFERENCE = "stage_b_full_kill_cooldown_6"
_PATROL = "stage_b_full_kill_cooldown_6_patrol"
_ACCOMPANY = "stage_b_full_kill_cooldown_6_accompany"
_SUMMARY_ARMS = ("stage_b_full", _REFERENCE, _PATROL, _ACCOMPANY)

#: Per arm, per seed offset: (covered at play ticks, (subjects, covered) at
#: kill ticks); every game has 100 subjects at play ticks.
_STUB: dict[str, list[tuple[int, tuple[int, int]]]] = {
    "stage_b_full": [(50, (5, 5))] * 8,
    _REFERENCE: [
        (covered, (10, offset) if offset < 6 else (0, 0))
        for offset, covered in enumerate((40, 50, 60, 40, 50, 60, 40, 50))
    ],
    _PATROL: [
        (50, (5, 1) if offset in (0, 1, 2, 3, 6) else (0, 0)) for offset in range(8)
    ],
    _ACCOMPANY: [(70, (0, 0))] * 8,
}


def _stub_counts(arm: str, seed: int) -> dict[str, int]:
    play, (subjects, covered) = _STUB[arm][seed - 1000]
    counts = {
        "tick_rows": 20,
        "whereabouts_subjects_at_play_ticks": 100,
        "whereabouts_covered_at_play_ticks": play,
        "whereabouts_subjects_at_kill_ticks": subjects,
        "whereabouts_covered_at_kill_ticks": covered,
    }
    if subjects:
        counts["event:Killed"] = 2 if arm == "stage_b_full" else 1
    return counts


def _stubbed_comparison(
    monkeypatch: pytest.MonkeyPatch, arms: tuple[str, ...]
) -> dict[str, Any]:
    configs = candidate_configs()

    def stub_game(
        *,
        seed: int,
        roster: Roster,
        config: RecordedExperimentConfig,
        replay_path: Path,
    ) -> lab.GameMetrics:
        (arm,) = [name for name in arms if configs[name] == config]
        return lab.GameMetrics(
            seed=seed,
            roster=roster,
            counts=_stub_counts(arm, seed),
            maximum_finished_wait_ticks=0,
            completion_status="completed",
            winner="CREWMATES",
            reason="CREWMATE_TASKS",
            replay_sha256="",
            trajectory_sha256="",
            reported_cost_usd=0.0,
        )

    monkeypatch.setattr(lab, "run_candidate", stub_game)
    monkeypatch.setattr(lab, "measure_world_copy_control", lambda **kwargs: {})
    return lab.build_comparison(split="development", arms=arms)


_EXPECTED_COVERAGE: dict[str, dict[str, Any]] = {
    "stage_b_full": {
        "games": 8,
        "kills": 16,
        "whereabouts_subjects_at_kill_ticks": 40,
        "whereabouts_covered_at_kill_ticks": 40,
        "whereabouts_subjects_at_play_ticks": 800,
        "whereabouts_covered_at_play_ticks": 400,
        "games_without_a_kill_tick": 0,
        "kill_tick_share_minimum": 1.0,
        "kill_tick_share_median": 1.0,
        "kill_tick_share_maximum": 1.0,
    },
    _REFERENCE: {
        "games": 8,
        "kills": 6,
        "whereabouts_subjects_at_kill_ticks": 60,
        "whereabouts_covered_at_kill_ticks": 15,
        "whereabouts_subjects_at_play_ticks": 800,
        "whereabouts_covered_at_play_ticks": 390,
        "games_without_a_kill_tick": 2,
        "kill_tick_share_minimum": 0.0,
        "kill_tick_share_median": 0.25,
        "kill_tick_share_maximum": 0.5,
    },
    _PATROL: {
        "games": 8,
        "kills": 5,
        "whereabouts_subjects_at_kill_ticks": 25,
        "whereabouts_covered_at_kill_ticks": 5,
        "whereabouts_subjects_at_play_ticks": 800,
        "whereabouts_covered_at_play_ticks": 400,
        "games_without_a_kill_tick": 3,
        "kill_tick_share_minimum": 0.2,
        "kill_tick_share_median": 0.2,
        "kill_tick_share_maximum": 0.2,
    },
    _ACCOMPANY: {
        "games": 8,
        "kills": 0,
        "whereabouts_subjects_at_kill_ticks": 0,
        "whereabouts_covered_at_kill_ticks": 0,
        "whereabouts_subjects_at_play_ticks": 800,
        "whereabouts_covered_at_play_ticks": 560,
        "games_without_a_kill_tick": 8,
        "kill_tick_share_minimum": None,
        "kill_tick_share_median": None,
        "kill_tick_share_maximum": None,
    },
}

_EXPECTED_PAIRS: dict[str, dict[str, Any]] = {
    _PATROL: {
        "reference": _REFERENCE,
        "seeds": 8,
        "seeds_with_a_kill_tick_in_both": 4,
        "kill_tick_share_higher": 2,
        "kill_tick_share_equal": 1,
        "kill_tick_share_lower": 1,
        "play_tick_share_higher": 3,
        "play_tick_share_equal": 3,
        "play_tick_share_lower": 2,
    },
    _ACCOMPANY: {
        "reference": _REFERENCE,
        "seeds": 8,
        "seeds_with_a_kill_tick_in_both": 0,
        "kill_tick_share_higher": 0,
        "kill_tick_share_equal": 0,
        "kill_tick_share_lower": 0,
        "play_tick_share_higher": 8,
        "play_tick_share_equal": 0,
        "play_tick_share_lower": 0,
    },
}


def test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The games are stubbed, so the test reads the summaries' wiring."""

    output = _stubbed_comparison(monkeypatch, _SUMMARY_ARMS)
    assert output["whereabouts_coverage"] == lab.whereabouts_coverage_summary(
        output["arms"]
    )
    assert output["idle_policy_pairs"] == lab.idle_policy_pairs(output["arms"])
    for roster in ("4p1i", "9p2i"):
        assert {
            arm: output["whereabouts_coverage"][arm][roster] for arm in _SUMMARY_ARMS
        } == _EXPECTED_COVERAGE
        assert {
            arm: output["idle_policy_pairs"][arm][roster]
            for arm in (_PATROL, _ACCOMPANY)
        } == _EXPECTED_PAIRS
    assert set(output["idle_policy_pairs"]) == {_PATROL, _ACCOMPANY}


def test_a_summary_over_another_arms_rows_or_a_pair_against_stage_b_full_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: the patrol summary fed the reference's rows; the pair re-keyed."""

    output = _stubbed_comparison(monkeypatch, _SUMMARY_ARMS)
    arms = output["arms"]
    swapped = {**arms, _PATROL: arms[_REFERENCE]}
    assert (
        lab.whereabouts_coverage_summary(swapped)[_PATROL]["9p2i"]
        != _EXPECTED_COVERAGE[_PATROL]
    )
    monkeypatch.setattr(lab, "STAGE_B_IDLE_REFERENCE", "stage_b_full")
    against_full = lab.idle_policy_pairs(arms)[_PATROL]["9p2i"]
    assert against_full["seeds_with_a_kill_tick_in_both"] == 5
    assert against_full["kill_tick_share_lower"] == 5
    assert against_full["play_tick_share_equal"] == 8
    assert against_full != _EXPECTED_PAIRS[_PATROL]


def test_pairs_need_the_reference_in_the_same_comparison(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = _stubbed_comparison(monkeypatch, ("stage_b_full", _PATROL))
    assert output["idle_policy_pairs"] == {}
    only_reference = _stubbed_comparison(monkeypatch, (_REFERENCE, _ACCOMPANY))
    assert set(only_reference["idle_policy_pairs"]) == {_ACCOMPANY}


def test_pairs_refuse_arms_that_ran_different_seeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arms = _stubbed_comparison(monkeypatch, (_REFERENCE, _PATROL))["arms"]
    shorter = {
        **arms,
        _PATROL: {
            **arms[_PATROL],
            "sets": {
                roster: rows[:-1] for roster, rows in arms[_PATROL]["sets"].items()
            },
        },
    }
    with pytest.raises(ValueError, match="ran different seeds"):
        lab.idle_policy_pairs(shorter)


def test_a_game_without_a_subject_has_no_share() -> None:
    empty = dict.fromkeys(lab.WHEREABOUTS_COUNTS, 0)
    full = {**empty, "whereabouts_subjects_at_play_ticks": 5}
    with pytest.raises(ValueError, match="no share"):
        lab._compare_shares(empty, full, "play_ticks")
    with pytest.raises(ValueError, match="no share"):
        lab._compare_shares(full, empty, "play_ticks")


def test_the_wide_split_runs_its_hundred_seeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configs = candidate_configs()
    calls: list[tuple[str, int]] = []

    def stub_game(
        *,
        seed: int,
        roster: Roster,
        config: RecordedExperimentConfig,
        replay_path: Path,
    ) -> lab.GameMetrics:
        assert config == configs["baseline"]
        calls.append((f"{roster.num_players}p", seed))
        return lab.GameMetrics(
            seed=seed,
            roster=roster,
            counts={
                **dict.fromkeys(lab.WHEREABOUTS_COUNTS, 0),
                "whereabouts_subjects_at_play_ticks": 1,
            },
            maximum_finished_wait_ticks=0,
            completion_status="completed",
            winner=None,
            reason=None,
            replay_sha256="",
            trajectory_sha256="",
            reported_cost_usd=0.0,
        )

    monkeypatch.setattr(lab, "run_candidate", stub_game)
    monkeypatch.setattr(lab, "measure_world_copy_control", lambda **kwargs: {})
    output = lab.build_comparison(split="development_wide", arms=("baseline",))
    assert output["split"] == "development_wide"
    assert output["seeds"] == tuple(range(1000, 1100))
    assert calls == [
        (name, seed) for name in ("4p", "9p") for seed in range(1000, 1100)
    ]
    assert [row["seed"] for row in output["arms"]["baseline"]["sets"]["9p2i"]] == list(
        range(1000, 1100)
    )
