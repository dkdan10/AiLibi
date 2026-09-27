"""B1 in recorded fake games: wiring, reconstruction, the census and the lab.

Every recording here is a fake-provider game made in a temporary directory; no
committed recording is read. The B1 recording plays the 9p2i roster on
development seed 1003 with both vent values and the physical witness rule ON,
and it holds an entry, a wait, a surfacing before the cap and one at the cap.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any, Final, Literal, TypedDict, cast

import pytest
from pydantic import TypeAdapter

import eval.balance_eval as balance_eval
import eval.replay_walk as replay_walk
import experiments.tactical_gameplay as lab
import orchestrator.replay as replay_module
from agents.base import AgentInterface
from agents.tactical.experimental import (
    FRESH_KILL_WINDOW_TICKS,
    IN_VENT_CAP_TICKS,
    UNBUILT_OPTION_VALUES,
    ExperimentalCrewmatePolicy,
    ExperimentalImpostorPolicy,
    TacticalExperimentOptions,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from api.replay_loader import ReplayLoader
from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import KilledEvent, VentEnteredEvent
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval.evidence_honesty import (
    RECORDED_ARM_POLICY_FOLD,
    compute_evidence_honesty,
    live_impostor_policy,
)
import eval.gameplay_census as census
from eval.gameplay_census import (
    CensusInputs,
    GameFacts,
    GameplayCensusConformanceError,
    KillFact,
    VentFact,
    fold_set,
    load_census_inputs,
)
from eval.replay_walk import TickAdvanced, WalkComplete, walk_replay
from experiments.tactical_gameplay import (
    LAB_THREADED_LAYERS,
    MECHANISMS_WALK_CONFIG,
    STAGE_B_FULL_SETTINGS,
    STAGE_B_MINUS_ONE,
    Roster,
    candidate_configs,
    measure_replay,
    run_candidate,
)
from llm.fake_provider import FakeProvider
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    ConfigLayer,
    RecordedExperimentConfig,
    normalize_experiment_config,
)
from orchestrator.game import (
    HeadlessGame,
    TacticalAgent,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state
from tests._helpers.scripted_meeting import record_game

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _manifest_writer import update_manifest  # noqa: E402

MAP = load_canonical_map()
SEED: Final[int] = 1003
B1_ON: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    vent_exit_policy="look_and_wait",
    vent_entry_policy="own_fresh_kill",
    vent_witness_rule="physical",
)
NINE: Final[Roster] = Roster(num_players=9, num_impostors=2, tasks_per_crewmate=2)
FOUR: Final[Roster] = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)


class _RosterKwargs(TypedDict):
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


def _kwargs(roster: Roster) -> _RosterKwargs:
    return {
        "num_players": roster.num_players,
        "num_impostors": roster.num_impostors,
        "tasks_per_crewmate": roster.tasks_per_crewmate,
    }


@pytest.fixture(scope="module")
def b1_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The B1 recording, as a set directory with roster and MANIFEST."""

    directory = tmp_path_factory.mktemp("b1") / "9p2i"
    record_game(directory, seed=SEED, config=B1_ON)
    return directory


def _rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


# --------------------------------------------------------------------------- #
# Reconstructible from memory                                                  #
# --------------------------------------------------------------------------- #


def test_honesty_reconstructs_the_recorded_policy_with_no_mismatch(
    b1_set: Path,
) -> None:
    recorded = compute_evidence_honesty(b1_set).impostor_targeting
    assert recorded.policy_mode == RECORDED_ARM_POLICY_FOLD
    assert recorded.reconstruction_mismatches == 0
    assert recorded.decisions_reconstructed > 0
    assert recorded.in_vent_decisions > 0
    default = compute_evidence_honesty(
        b1_set, impostor_policy=live_impostor_policy
    ).impostor_targeting
    assert default.decisions_reconstructed == recorded.decisions_reconstructed
    assert default.reconstruction_mismatches > 0


# --------------------------------------------------------------------------- #
# Wiring and determinism                                                       #
# --------------------------------------------------------------------------- #


def _built_policies(
    config: RecordedExperimentConfig, tmp_path: Path
) -> dict[PlayerId, object]:
    """Each agent's policy as a short ``HeadlessGame`` on ``config`` builds it."""

    built: dict[PlayerId, AgentInterface] = {}
    factory = build_default_agent_factory(experiment_config=config)

    def keeping(agent_id: PlayerId, role: Role) -> AgentInterface:
        built[agent_id] = factory(agent_id, role)
        return built[agent_id]

    HeadlessGame(
        seed=1000,
        game_map=MAP,
        agent_factory=keeping,
        replay_path=tmp_path / "replay-seed-1000.jsonl",
        scheduler=TickScheduler(max_ticks=3),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider(), env={}),
        experiment_config=config,
        **_kwargs(FOUR),
    ).run()
    policies: dict[PlayerId, object] = {}
    for agent_id, agent in built.items():
        assert isinstance(agent, TacticalAgent)
        policies[agent_id] = agent._policy
    return policies


def _check_wiring(
    field: Literal["vent_exit_policy", "vent_entry_policy"],
    value: str,
    tmp_path: Path,
) -> None:
    config = RecordedExperimentConfig.model_validate({field: value})
    assert config.has_tactical_changes
    policies = _built_policies(config, tmp_path)
    impostors = [p for p in policies.values() if isinstance(p, ImpostorPolicy)]
    assert impostors
    for policy in impostors:
        assert type(policy) is ExperimentalImpostorPolicy
        assert getattr(policy.options, field) == value
    for other in policies.values():
        if not isinstance(other, ImpostorPolicy):
            assert type(other) is ExperimentalCrewmatePolicy


@pytest.mark.parametrize(
    ("field", "value"),
    [("vent_exit_policy", "look_and_wait"), ("vent_entry_policy", "own_fresh_kill")],
)
def test_either_value_alone_builds_the_experimental_impostor(
    field: Literal["vent_exit_policy", "vent_entry_policy"],
    value: str,
    tmp_path: Path,
) -> None:
    _check_wiring(field, value, tmp_path)


def test_a_config_whose_entry_value_builds_the_default_policy_fails_the_wiring(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the tactical layer blind to ``vent_entry_policy``.

    The factory then builds the default ``ImpostorPolicy`` for an
    ``own_fresh_kill`` config, and the game runs it without complaint.
    """

    monkeypatch.setattr(
        experiment_config,
        "FIELD_LAYER",
        MappingProxyType({**FIELD_LAYER, "vent_entry_policy": "orchestrator"}),
    )
    with pytest.raises(AssertionError):
        _check_wiring("vent_entry_policy", "own_fresh_kill", tmp_path)


def test_both_values_build_and_validate_with_no_refusal() -> None:
    assert UNBUILT_OPTION_VALUES == {}
    assert not any(
        field in experiment_config.WAVE_ARMS_PENDING
        for field in ("vent_exit_policy", "vent_entry_policy")
    )
    assert RecordedExperimentConfig.model_validate(B1_ON.model_dump()) == B1_ON
    for options in (
        TacticalExperimentOptions(vent_exit_policy="look_and_wait"),
        TacticalExperimentOptions(vent_entry_policy="own_fresh_kill"),
    ):
        assert ExperimentalImpostorPolicy(agent_id="p-1", options=options)


def test_the_b1_recording_repeats_byte_for_byte_and_loads_verified(
    b1_set: Path, tmp_path: Path
) -> None:
    again = tmp_path / "again" / "9p2i"
    record_game(again, seed=SEED, config=B1_ON)
    name = f"replay-seed-{SEED}.jsonl"
    first = (b1_set / name).read_bytes()
    assert (again / name).read_bytes() == first
    # Planted: one tick row's state hash edited breaks the byte comparison.
    rows = _rows(again / name)
    tick = next(row for row in rows if row["kind"] == "tick")
    tick["state_hash"] = "0" * len(tick["state_hash"])
    edited = "".join(json.dumps(row) + "\n" for row in rows).encode()
    assert edited != first
    replay = ReplayLoader(b1_set).load_replay(f"headless-seed-{SEED}")
    assert replay.metadata.outcome_verified
    stamped = [row for row in _rows(b1_set / name) if row["kind"] == "tick"]
    assert stamped
    for row in stamped:
        assert row["experiment_config"]["vent_exit_policy"] == "look_and_wait"
        assert row["experiment_config"]["vent_entry_policy"] == "own_fresh_kill"
        assert row["experiment_config"]["vent_witness_rule"] == "physical"


def test_a_default_config_serializes_without_the_new_key() -> None:
    assert "vent_entry_policy" not in RecordedExperimentConfig().model_dump()
    exit_only = RecordedExperimentConfig(vent_exit_policy="look_and_wait")
    assert "vent_entry_policy" not in exit_only.model_dump()
    assert exit_only.model_dump()["vent_exit_policy"] == "look_and_wait"
    assert normalize_experiment_config(RecordedExperimentConfig()) is None


# --------------------------------------------------------------------------- #
# The census reads 0 on a game built with the arms                             #
# --------------------------------------------------------------------------- #

_B1_CELLS: Final[tuple[str, ...]] = (
    "vent_entries_not_after_own_fresh_kill",
    "surfacings_before_cap_in_view",
    "trips_longer_than_cap",
)


def _game(inputs: CensusInputs) -> GameFacts:
    (game,) = inputs.games
    return game


def _with_game(inputs: CensusInputs, game: GameFacts) -> CensusInputs:
    return replace(inputs, games=(game,))


def _visible(room: str, sabotage: bool) -> frozenset[str]:
    if sabotage:
        return frozenset({room})
    return frozenset({room, *MAP.room_neighbors(room)})


def _watched(game: GameFacts, actor: str, room: str, tick: int) -> bool:
    frame = game.frames[tick]
    teammates = {
        pid for pid, role in game.roles.items() if role == "IMPOSTOR" and pid != actor
    }
    sight = _visible(room, frame.sabotage_active)
    return any(
        where in sight
        for pid, where in frame.rooms.items()
        if pid != actor and pid not in teammates
    )


def test_the_census_reads_zero_on_the_b1_cells(b1_set: Path) -> None:
    folded = fold_set(load_census_inputs(b1_set))
    for key in _B1_CELLS:
        assert folded.cells[key].numerator == 0, key
        assert folded.cells[key].denominator > 0, key
    assert folded.cells["forced_surfacings"].numerator > 0


def test_a_surfacing_moved_to_a_watched_tick_breaches(b1_set: Path) -> None:
    inputs = load_census_inputs(b1_set)
    game = _game(inputs)
    # A tick the impostor waited through inside: someone stood in its sight.
    moves = [
        (vent, tick)
        for vent in game.vents
        if vent.kind == "exit"
        for entry in game.vents
        if entry.kind == "entry"
        and entry.actor == vent.actor
        and entry.tick < vent.tick
        and not any(
            other.actor == vent.actor and entry.tick < other.tick < vent.tick
            for other in game.vents
        )
        for tick in range(entry.tick + 1, vent.tick)
        if _watched(game, vent.actor, vent.source_room, tick)
    ]
    assert moves
    surfacing, watched_tick = moves[0]
    vents = tuple(
        replace(vent, tick=watched_tick) if vent == surfacing else vent
        for vent in game.vents
    )
    with pytest.raises(GameplayCensusConformanceError, match="in view"):
        fold_set(_with_game(inputs, replace(game, vents=vents)))


def test_a_stay_extended_past_the_cap_breaches(b1_set: Path) -> None:
    inputs = load_census_inputs(b1_set)
    game = _game(inputs)

    def inside(exit_fact: VentFact) -> int:
        # Ticks inside as the census counts them: from the entry, or from the
        # last meeting opened since.
        entry_tick = max(
            vent.tick
            for vent in game.vents
            if vent.kind == "entry"
            and vent.actor == exit_fact.actor
            and vent.tick < exit_fact.tick
        )
        meetings = [m.tick for m in game.meetings if m.tick < exit_fact.tick]
        return exit_fact.tick - max([entry_tick, *meetings])

    capped = next(
        vent
        for vent in game.vents
        if vent.kind == "exit"
        and inside(vent) == IN_VENT_CAP_TICKS
        and not any(
            other.actor == vent.actor and other.tick == vent.tick + 1
            for other in game.vents
        )
    )
    later = replace(capped, tick=capped.tick + 1)
    vents = tuple(later if vent == capped else vent for vent in game.vents)
    with pytest.raises(GameplayCensusConformanceError, match="longer than the cap"):
        fold_set(_with_game(inputs, replace(game, vents=vents)))


def test_an_entry_rekeyed_to_a_teammates_victim_breaches(b1_set: Path) -> None:
    inputs = load_census_inputs(b1_set)
    game = _game(inputs)
    entry = next(vent for vent in game.vents if vent.kind == "entry")
    teammate = next(
        pid
        for pid, role in sorted(game.roles.items())
        if role == "IMPOSTOR" and pid != entry.actor
    )
    kills: tuple[KillFact, ...] = tuple(
        replace(kill, killer=teammate)
        if kill.killer == entry.actor
        and kill.room == entry.source_room
        and entry.tick - FRESH_KILL_WINDOW_TICKS <= kill.tick < entry.tick
        else kill
        for kill in game.kills
    )
    assert kills != game.kills
    with pytest.raises(GameplayCensusConformanceError, match="own fresh kill"):
        fold_set(_with_game(inputs, replace(game, kills=kills)))


# --------------------------------------------------------------------------- #
# The lab: arms, counters and walk profiles                                    #
# --------------------------------------------------------------------------- #

#: The round-1 config the decision memo declares (section 1, "Arms").
_ROUND_ONE: Final[dict[str, object]] = {
    "format_version": 1,
    "meeting_reset": "hub_with_grace",
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
    "vent_witness_rule": "physical",
    "bounded_rebuttal_version": 1,
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}


def _changed(config: RecordedExperimentConfig) -> dict[str, object]:
    return {
        field: getattr(config, field)
        for field, info in RecordedExperimentConfig.model_fields.items()
        if getattr(config, field) != info.default
    }


def test_the_eight_arms_set_what_their_names_say() -> None:
    configs = candidate_configs()
    assert _changed(configs["vent_physical"]) == {"vent_witness_rule": "physical"}
    assert _changed(configs["vent_look_and_wait"]) == {
        "vent_exit_policy": "look_and_wait"
    }
    assert _changed(configs["vent_own_fresh_kill"]) == {
        "vent_entry_policy": "own_fresh_kill"
    }
    full = _changed(configs["stage_b_full"])
    assert full == dict(STAGE_B_FULL_SETTINGS)
    # The round-1 fields left out are the rebuttal, the body handle and both
    # ballot versions: none acts on a fake game's play.
    left_out = {
        field for field in _ROUND_ONE if field not in full and field != "format_version"
    }
    assert left_out == {
        "bounded_rebuttal_version",
        "report_body_handle_version",
        "ballot_kill_row_version",
        "impostor_ballot_version",
    }
    assert all(_ROUND_ONE[field] == value for field, value in full.items())


def _minus_one_problems(configs: Mapping[str, RecordedExperimentConfig]) -> list[str]:
    """Each minus-one arm must equal stage_b_full but for the field it names.

    The field is found from the arm's name alone: the one field whose value in
    stage_b_full is the name's suffix. It must be back at its default.
    """

    full = configs["stage_b_full"]
    problems: list[str] = []
    for name in sorted(configs):
        if not name.startswith("stage_b_full_minus_"):
            continue
        dropped = name.removeprefix("stage_b_full_minus_")
        named = [
            field
            for field in RecordedExperimentConfig.model_fields
            if getattr(full, field) == dropped
        ]
        if len(named) != 1:
            problems.append(f"{name}: stage_b_full holds {dropped!r} in {named}")
            continue
        differing = [
            field
            for field in RecordedExperimentConfig.model_fields
            if getattr(configs[name], field) != getattr(full, field)
        ]
        if differing != named:
            problems.append(f"{name}: differs in {differing}, not only {named}")
            continue
        if (
            getattr(configs[name], named[0])
            != RecordedExperimentConfig.model_fields[named[0]].default
        ):
            problems.append(f"{name}: {named[0]} is not back at its default")
    return problems


def test_each_minus_one_arm_drops_exactly_the_field_it_names() -> None:
    configs = candidate_configs()
    minus = sorted(name for name in configs if name.startswith("stage_b_full_minus_"))
    assert minus == sorted(
        (
            "stage_b_full_minus_look_and_wait",
            "stage_b_full_minus_own_fresh_kill",
            "stage_b_full_minus_physical",
            "stage_b_full_minus_hub_with_grace",
        )
    )
    assert set(STAGE_B_MINUS_ONE) == set(minus)
    assert set(STAGE_B_MINUS_ONE.values()) == set(STAGE_B_FULL_SETTINGS)
    assert _minus_one_problems(configs) == []


def test_a_minus_one_arm_that_drops_another_field_or_nothing_fails() -> None:
    """Perturbed: one arm drops the wrong field; another equals stage_b_full."""

    configs = candidate_configs()
    wrong = dict(configs)
    wrong["stage_b_full_minus_physical"] = configs["stage_b_full_minus_look_and_wait"]
    assert _minus_one_problems(wrong) == [
        "stage_b_full_minus_physical: differs in ['vent_exit_policy'], not only "
        "['vent_witness_rule']"
    ]
    same = dict(configs)
    same["stage_b_full_minus_hub_with_grace"] = configs["stage_b_full"]
    assert _minus_one_problems(same) == [
        "stage_b_full_minus_hub_with_grace: differs in [], not only ['meeting_reset']"
    ]


def _lab_recording(
    directory: Path, *, arm: str, seed: int, roster: Roster
) -> tuple[Path, dict[str, int]]:
    """One lab game recorded by the lab itself, made walkable as a set."""

    directory.mkdir(parents=True)
    path = directory / f"replay-seed-{seed}.jsonl"
    row = run_candidate(
        seed=seed, roster=roster, config=candidate_configs()[arm], replay_path=path
    )
    assert row.error is None
    (directory / "roster.json").write_text(roster.model_dump_json(), encoding="utf-8")
    update_manifest(
        directory / "MANIFEST.md",
        directory,
        [seed],
        git_sha="lab",
        refreshed_at="2026-09-26",
    )
    return path, row.counts


def _applied_in_vent_impostor_waits(path: Path, *, seed: int, roster: Roster) -> int:
    """Waits an impostor inside a vent made, read from the walked dispositions."""

    adapter: TypeAdapter[Action] = TypeAdapter(Action)
    waits = 0
    for step in walk_replay(
        path,
        seed=seed,
        game_map=MAP,
        config=MECHANISMS_WALK_CONFIG,
        **_kwargs(roster),
    ):
        if not isinstance(step, TickAdvanced):
            continue
        dispositions = step.entry.action_dispositions
        assert dispositions is not None
        for raw, disposition in zip(step.entry.actions, dispositions, strict=True):
            action = adapter.validate_python(raw)
            player = step.pre_state.players[action.actor]
            waits += (
                disposition == "applied"
                and action.type == "wait"
                and player.role == "IMPOSTOR"
                and player.in_vent
            )
    return waits


@pytest.mark.parametrize(
    ("arm", "seed"), [("vent_look_and_wait", 1000), ("stage_b_full", 1005)]
)
def test_the_lab_counters_agree_with_the_census(
    tmp_path: Path, arm: str, seed: int
) -> None:
    path, counts = _lab_recording(
        tmp_path / arm / "9p2i", arm=arm, seed=seed, roster=NINE
    )
    folded = fold_set(load_census_inputs(path.parent))
    cell = folded.cells
    assert counts["vent_exits_crew_destination_witnessed"] == (
        cell["vent_exits_seen_from_exit_room"].numerator
    )
    assert counts["vent_exits_crew_source_only_witnessed"] == (
        cell["vent_exits_seen_only_from_room_left"].numerator
    )
    assert counts["vent_exits_in_place"] == (
        cell["in_place_surfacings_near_crew"].denominator
    )
    assert counts["vent_trips_reaching_cap"] == cell["forced_surfacings"].numerator
    assert counts["vent_entries_not_after_own_fresh_kill"] == (
        cell["vent_entries_not_after_own_fresh_kill"].numerator
    )
    assert counts["meetings_opening_with_impostor_in_vent"] == (
        cell["meetings_opening_with_impostor_in_vent"].numerator
    )
    ticks = {
        key.removeprefix("vent_trip_ticks_inside:"): value
        for key, value in counts.items()
        if key.startswith("vent_trip_ticks_inside:")
    }
    assert ticks == dict(folded.tables["ticks_inside_per_trip"])
    assert counts["impostor_in_vent_waits"] == _applied_in_vent_impostor_waits(
        path, seed=seed, roster=NINE
    )
    # Each counter the comparison reads is live on at least one of the two games.
    assert counts["impostor_in_vent_waits"] > 0
    assert counts["vent_trips_reaching_cap"] > 0
    assert counts["vent_exits_in_place"] > 0
    assert counts["meetings_opening_with_impostor_in_vent"] > 0
    if arm == "vent_look_and_wait":
        assert counts["vent_exits_crew_source_only_witnessed"] > 0
        assert counts["vent_entries_not_after_own_fresh_kill"] > 0


def _entered(tick: int, actor: str = "p-1", room: str = "STORAGE") -> VentEnteredEvent:
    return VentEnteredEvent(
        type="VentEntered",
        tick=tick,
        actor=actor,
        vent_id=f"{room}_VENT",
        room=room,
        source_vent_id=f"{room}_VENT",
        destination_vent_id=f"{room}_VENT",
        source_room=room,
        destination_room=room,
        traversal_ticks=1,
        witnesses=(),
        source_witnesses=(),
        destination_witnesses=(),
    )


def _killed(tick: int, actor: str = "p-1", room: str = "STORAGE") -> KilledEvent:
    return KilledEvent(
        type="Killed", tick=tick, actor=actor, target="p-7", room=room, witnesses=()
    )


@pytest.mark.parametrize(
    ("kill", "meetings", "fresh"),
    [
        (_killed(9), (), True),
        (_killed(7), (), True),
        (_killed(6), (), False),
        (_killed(10), (), False),
        (_killed(9, actor="p-2"), (), False),
        (_killed(9, room="ENGINEERING"), (), False),
        (_killed(8), (8,), False),
        (_killed(8), (9,), False),
        (_killed(8), (7,), True),
        (_killed(8), (10,), True),
    ],
)
def test_an_entry_follows_its_own_fresh_kill_by_the_census_definition(
    kill: KilledEvent, meetings: tuple[int, ...], fresh: bool
) -> None:
    # The entry resolves at tick 10 in STORAGE; the window is three ticks.
    assert (
        lab.entry_after_own_fresh_kill(
            _entered(10), kills=(kill,), meeting_ticks=meetings
        )
        is fresh
    )
    game = cast(
        GameFacts,
        SimpleNamespace(
            kills=(KillFact(kill.tick, kill.actor, kill.room, frozenset()),),
            meetings=tuple(SimpleNamespace(tick=tick) for tick in meetings),
        ),
    )
    entry = VentFact(10, "p-1", "entry", "STORAGE", "STORAGE", frozenset(), frozenset())
    assert census._own_fresh_kill_before(game, entry) is fresh


def test_a_living_player_in_a_vent_is_one_the_census_reads() -> None:
    state = seed_initial_state(seed=0, game_map=MAP, num_players=4)
    assert not lab.living_player_in_vent(state)
    inside = {
        pid: replace(player, in_vent=pid == "p-1")
        for pid, player in state.players.items()
    }
    assert lab.living_player_in_vent(replace(state, players=inside))
    dead_inside = {
        pid: replace(player, in_vent=pid == "p-1", alive=pid != "p-1")
        for pid, player in state.players.items()
    }
    assert not lab.living_player_in_vent(replace(state, players=dead_inside))


def test_measure_replay_hands_the_entry_check_the_kills_and_meetings_so_far(
    b1_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[tuple[int, tuple[int, ...], tuple[int, ...]]] = []
    real = lab.entry_after_own_fresh_kill

    def spying(
        entry: VentEnteredEvent,
        *,
        kills: Sequence[KilledEvent],
        meeting_ticks: Sequence[int],
    ) -> bool:
        seen.append(
            (entry.tick, tuple(kill.tick for kill in kills), tuple(meeting_ticks))
        )
        return real(entry, kills=kills, meeting_ticks=meeting_ticks)

    monkeypatch.setattr(lab, "entry_after_own_fresh_kill", spying)
    measure_replay(b1_set / f"replay-seed-{SEED}.jsonl", seed=SEED, roster=NINE)
    rows = _rows(b1_set / f"replay-seed-{SEED}.jsonl")
    meetings = [row["tick"] for row in rows if row["kind"] == "meeting"]
    game = _game(load_census_inputs(b1_set))
    assert seen
    for tick, kill_ticks, meeting_ticks in seen:
        assert meeting_ticks == tuple(m for m in meetings if m < tick)
        assert kill_ticks == tuple(
            kill.tick for kill in game.kills if kill.tick <= tick
        )
    assert any(meeting_ticks for _tick, _kills, meeting_ticks in seen)


# The two lab walk profiles ---------------------------------------------------

_PROFILES: Final[dict[str, str]] = {
    "tactical-mechanisms": "MECHANISMS_WALK_CONFIG",
    "tactical-seat-effects": "SEAT_EFFECTS_WALK_CONFIG",
}

#: Every other wave setting at its ON value, stamped onto a recording that ran
#: the physical rule, the regroup and the rebuttal, which exist today.
_FULL_CONFIG_SETTINGS: Final[dict[str, object]] = {
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}
_TODAY: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    vent_witness_rule="physical",
    meeting_reset="hub_with_grace",
    bounded_rebuttal_version=1,
)
#: The fake 4p/1i game the profile proofs copy.
_PROFILE_SEED: Final[int] = 1


@pytest.fixture(scope="module")
def today_game(tmp_path_factory: pytest.TempPathFactory) -> Path:
    directory = tmp_path_factory.mktemp("today") / "4p1i"
    return record_game(directory, seed=_PROFILE_SEED, config=_TODAY, **_kwargs(FOUR))


def _copy(source: Path, tmp_path: Path, name: str) -> Path:
    directory = tmp_path / name
    directory.mkdir()
    return Path(shutil.copy(source, directory))


def _full_config_copy(source: Path, tmp_path: Path) -> Path:
    path = _copy(source, tmp_path, "full")
    rows = _rows(path)
    stamped = 0
    for row in rows:
        if row["kind"] in ("tick", "game_over"):
            row["experiment_config"].update(_FULL_CONFIG_SETTINGS)
            stamped += 1
    assert stamped > 1
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return path


def _open_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}))


def _walk_with(profile: str, path: Path) -> object:
    """``path`` read through ``profile`` as the lab reads it."""

    if profile == "tactical-mechanisms":
        return measure_replay(path, seed=_PROFILE_SEED, roster=FOUR).counts
    steps = list(
        walk_replay(
            path,
            seed=_PROFILE_SEED,
            game_map=MAP,
            config=lab.SEAT_EFFECTS_WALK_CONFIG,
            **_kwargs(FOUR),
        )
    )
    terminal = next(step for step in steps if isinstance(step, WalkComplete))
    return (
        sum(isinstance(step, TickAdvanced) for step in steps),
        terminal.terminal_tick,
        terminal.state,
    )


def _counted_advances(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []

    def counting(*args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        return advance_tick(*args, **kwargs)

    monkeypatch.setattr(replay_walk, "advance_tick", counting)
    return calls


@pytest.mark.parametrize("profile", sorted(_PROFILES))
def test_each_lab_profile_is_current_report_plus_its_own_layers(profile: str) -> None:
    config = getattr(lab, _PROFILES[profile])
    assert LAB_THREADED_LAYERS == {"orchestrator", "tactical", "meeting"}
    assert config == replace(
        balance_eval._CURRENT_REPORT_WALK_CONFIG,
        profile=profile,
        threaded_layers=LAB_THREADED_LAYERS,
    )


def test_the_lab_profiles_never_inherit_the_current_report_layers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Re-executed with the current-report profile declaring no layer."""

    monkeypatch.setattr(
        balance_eval,
        "_CURRENT_REPORT_WALK_CONFIG",
        replace(balance_eval._CURRENT_REPORT_WALK_CONFIG, threaded_layers=frozenset()),
    )
    spec = importlib.util.spec_from_file_location("lab_reexecuted", lab.__file__)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "lab_reexecuted", module)
    spec.loader.exec_module(module)
    assert module.MECHANISMS_WALK_CONFIG.threaded_layers == LAB_THREADED_LAYERS
    assert module.SEAT_EFFECTS_WALK_CONFIG.threaded_layers == LAB_THREADED_LAYERS


def test_each_lab_consumer_walks_with_its_profile(
    today_game: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    seen: list[str] = []
    real = walk_replay

    def spying(*args: Any, config: replay_walk.ReplayWalkConfig, **kwargs: Any) -> Any:
        seen.append(config.profile)
        assert config is getattr(lab, _PROFILES[config.profile])
        return real(*args, config=config, **kwargs)

    monkeypatch.setattr(lab, "walk_replay", spying)
    measure_replay(today_game, seed=_PROFILE_SEED, roster=FOUR)
    baseline = tmp_path / "baseline" / "replay-seed-1000.jsonl"
    baseline.parent.mkdir()
    run_candidate(
        seed=1000,
        roster=FOUR,
        config=candidate_configs()["baseline"],
        replay_path=baseline,
    )
    lab.measure_identity_effects(baseline, seed=1000, roster=FOUR)
    assert seen == [
        "tactical-mechanisms",
        "tactical-mechanisms",
        "tactical-seat-effects",
    ]


@pytest.mark.parametrize("profile", sorted(_PROFILES))
def test_each_lab_profile_reads_the_full_config_copy_with_every_hash_verified(
    profile: str,
    today_game: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _open_pending(monkeypatch)
    plain = _copy(today_game, tmp_path, "plain")
    full = _full_config_copy(today_game, tmp_path)
    advances = _counted_advances(monkeypatch)
    assert _walk_with(profile, full) == _walk_with(profile, plain)
    assert advances


@pytest.mark.parametrize("profile", sorted(_PROFILES))
def test_without_its_declaration_a_lab_profile_refuses_the_full_config_copy(
    profile: str,
    today_game: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Perturbed: the profile's layer declaration removed."""

    _open_pending(monkeypatch)
    full = _full_config_copy(today_game, tmp_path)
    name = _PROFILES[profile]
    monkeypatch.setattr(
        lab, name, replace(getattr(lab, name), threaded_layers=frozenset())
    )
    advances = _counted_advances(monkeypatch)
    with pytest.raises(ValueError, match=f"replay profile '{profile}' does not read"):
        _walk_with(profile, full)
    assert advances == []


class _StandIn(RecordedExperimentConfig):
    """The config model with one field no reader has reviewed."""

    stand_in_rule: Literal["old", "new"] = "old"


@pytest.mark.parametrize("profile", sorted(_PROFILES))
@pytest.mark.parametrize("layer", ["engine", "orchestrator", "tactical", "meeting"])
def test_a_stand_in_field_in_an_undeclared_layer_is_refused_before_advancing(
    profile: str,
    layer: ConfigLayer,
    today_game: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: a field added to the config model and to the layer table.

    An engine-layer stand-in is refused by the engine-arguments helper, which no
    profile can declare past. A stand-in in a declarable layer is read by the
    profile as declared, and refused by the same profile with that one layer
    removed, so the refusal comes from the declaration.
    """

    path = _copy(today_game, tmp_path, "game")
    stand_in = _StandIn.model_validate({**_TODAY.model_dump(), "stand_in_rule": "new"})
    layers = MappingProxyType({**FIELD_LAYER, "stand_in_rule": layer})
    monkeypatch.setattr(experiment_config, "FIELD_LAYER", layers)
    monkeypatch.setattr(replay_walk, "FIELD_LAYER", layers)
    # The walk and the lab's own per-action apply both read the recorded config.
    monkeypatch.setattr(
        replay_walk, "recorded_experiment_config", lambda _entries: stand_in
    )
    monkeypatch.setattr(lab, "recorded_experiment_config", lambda _entries: stand_in)
    monkeypatch.setattr(
        replay_module, "recorded_experiment_config", lambda _entries: stand_in
    )
    name = _PROFILES[profile]
    declared = getattr(lab, name)
    advances = _counted_advances(monkeypatch)
    if layer != "engine":
        _walk_with(profile, path)
        assert advances
        advances.clear()
        monkeypatch.setattr(
            lab,
            name,
            replace(declared, threaded_layers=declared.threaded_layers - {layer}),
        )
    with pytest.raises(ValueError, match="stand_in_rule='new'"):
        _walk_with(profile, path)
    assert advances == []


def test_the_full_config_copy_sets_a_later_value_in_every_declared_layer() -> None:
    assert {FIELD_LAYER[field] for field in _FULL_CONFIG_SETTINGS} == (
        LAB_THREADED_LAYERS
    )
