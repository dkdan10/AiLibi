"""Every reader of a physical-rule recording serves the physical witness sets.

A witness list lives only in the engine's events, never in ``WorldState``, so a
reader that re-simulates a ``vent_witness_rule="physical"`` recording under the
default rule reproduces every state hash while serving the old witness sets.
The reader gate below records one fake-provider physical game and reads it
three ways: the live game's own agent memory, ``ReplayLoader``'s memory walk
and ``walk_replay``. For every vent exit with a crewmate in the room left and
none in the room surfaced into, none of the three gives that crewmate the vent,
and the three agree on every vent observation of every agent. Replacing the
engine-arguments helper's result at any one of the three sites with the
``both_rooms`` arguments turns the gate red while every hash still verifies.

The same file holds the config line's round trip and the census end to end: a
physical game folded by ``publish_gameplay_census.py --set-dir`` reads zero on
the room-left-only exit cell, and the same recording walked with the rule
withheld raises that cell's conformance breach.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import NoReturn, TypedDict

import pytest

import api.replay_loader as replay_loader_module
import eval.replay_walk as replay_walk_module
import orchestrator.game as game_module
from agents.base import AgentInterface
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import AgentMemory
from api.replay_loader import ReplayLoader
from api.schemas import ExperimentConfigView
from engine.actions import Action
from engine.entities import PlayerId, Role, RoomId
from engine.events import EngineEvent, VentExitedEvent
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from eval.replay_walk import (
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    WalkViolation,
    walk_replay,
)
from llm.fake_provider import FakeProvider
from meetings.evidence_profile import profile_from_config
from observation.service import ObservationService
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    WAVE_ARMS_PENDING,
    EngineArguments,
    RecordedExperimentConfig,
    engine_arguments,
    meeting_values,
    normalize_experiment_config,
)
from orchestrator.game import (
    HeadlessGame,
    TacticalAgent,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import publish_gameplay_census  # noqa: E402

MAP = load_canonical_map()
PHYSICAL = RecordedExperimentConfig(vent_witness_rule="physical")
#: The reader-gate fixture: fake provider, the 9p2i roster, this seed.
SEED = 0


class Roster(TypedDict):
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


ROSTER: Roster = {"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}
#: The three re-simulation sites the gate reads, by the module whose
#: ``engine_arguments`` binding each one calls.
SITES: Mapping[str, ModuleType] = {
    "live": game_module,
    "loader": replay_loader_module,
    "walk": replay_walk_module,
}


@dataclass(frozen=True)
class FakeSet:
    """One recorded fake-provider set and each live agent's episodic log."""

    set_dir: Path
    path: Path
    live: Mapping[PlayerId, tuple[EpisodicEvent, ...]]


def record_fake_set(
    set_dir: Path,
    *,
    config: RecordedExperimentConfig | None = PHYSICAL,
    seed: int = SEED,
    temporal: bool = False,
) -> FakeSet:
    """Record one fake-provider 9p2i game into ``set_dir`` as a verifiable set.

    The set carries the ``roster.json`` the loader reads and a ``MANIFEST.md``
    row naming the prompt stamps its meetings recorded, which the census reads.
    ``temporal`` selects temporal observations version 2 through the runner's
    explicit environment mapping, never the process environment; the runner's
    meeting profile is built from ``config``.
    """

    set_dir.mkdir(parents=True, exist_ok=True)
    (set_dir / "roster.json").write_text(json.dumps(dict(ROSTER)), encoding="utf-8")
    built: dict[PlayerId, AgentInterface] = {}
    factory = build_default_agent_factory(experiment_config=config)

    def keeping(agent_id: PlayerId, role: Role) -> AgentInterface:
        built[agent_id] = factory(agent_id, role)
        return built[agent_id]

    path = set_dir / f"replay-seed-{seed}.jsonl"
    env = {"AILIBI_TEMPORAL_OBSERVATIONS": "2"} if temporal else {}
    HeadlessGame(
        seed=seed,
        game_map=MAP,
        agent_factory=keeping,
        replay_path=path,
        meeting_runner=build_default_meeting_runner(
            llm_client=FakeProvider(),
            env=env,
            profile=profile_from_config(
                meeting_values(config or RecordedExperimentConfig())
            ),
        ),
        experiment_config=config,
        **ROSTER,
    ).run()
    stamps = sorted(
        {
            stamp
            for entry in read_all_entries(path)
            if isinstance(entry, MeetingReplayEntry)
            for stamp in entry.prompt_versions.values()
        }
    )
    with (set_dir / "MANIFEST.md").open("a", encoding="utf-8") as manifest:
        manifest.write(f"| {seed} | fake | {', '.join(stamps)} |\n")
    live: dict[PlayerId, tuple[EpisodicEvent, ...]] = {}
    for agent_id, agent in built.items():
        assert isinstance(agent, TacticalAgent)
        live[agent_id] = agent.memory.episodic.recent(since_tick=0)
    return FakeSet(set_dir=set_dir, path=path, live=live)


# --------------------------------------------------------------------------- #
# The three readings                                                          #
# --------------------------------------------------------------------------- #

#: One vent observation: (holder, packet tick, actor, room).
VentRow = tuple[PlayerId, int, PlayerId, RoomId]


@dataclass(frozen=True)
class RoomLeftExit:
    """A vent exit with a crewmate in the room left and none in the destination.

    ``crewmates`` are the living, non-vented crewmates in the room left, read
    from a ``both_rooms`` re-simulation of the same tick, so the set does not
    depend on the rule under test.
    """

    tick: int
    actor: PlayerId
    source_room: RoomId
    crewmates: tuple[PlayerId, ...]


def _raise_violation(violation: WalkViolation) -> NoReturn:
    raise AssertionError(f"walk violation: {violation}")


#: A walk that verifies every tick hash and both meeting hashes.
READERS_PROFILE = ReplayWalkConfig(
    profile="vent-witness-readers",
    on_violation=_raise_violation,
    verify_tick_hashes=True,
    verify_meeting_pre_hashes=True,
    verify_meeting_post_hashes=True,
    missing_meeting_row="violation",
    supports_experiments=True,
)


def _vent_rows(logs: Mapping[PlayerId, Sequence[EpisodicEvent]]) -> list[VentRow]:
    return sorted(
        (holder, event.tick, event.payload["player_id"], event.payload["room"])
        for holder, events in logs.items()
        for event in events
        if event.type == "saw_player"
        and event.provenance == "observed"
        and event.payload.get("action") == "vent"
    )


@dataclass(frozen=True)
class WalkReading:
    exits: tuple[RoomLeftExit, ...]
    rows: list[VentRow]
    #: (exit, crewmate, packet tick) for each room-left crewmate alive at the
    #: next packet built after the exit.
    checks: tuple[tuple[RoomLeftExit, PlayerId, int], ...]
    witnessed: tuple[tuple[RoomLeftExit, PlayerId], ...]
    completed: bool


def _walk_reading(fake: FakeSet, tmp: Path) -> WalkReading:
    exits: list[RoomLeftExit] = []
    witnessed: list[tuple[RoomLeftExit, PlayerId]] = []
    pending: list[RoomLeftExit] = []
    checks: list[tuple[RoomLeftExit, PlayerId, int]] = []
    rows: list[VentRow] = []
    completed = False
    service = ObservationService(game_map=MAP, audit_log_path=tmp / "walk-audit.jsonl")
    try:
        for step in walk_replay(
            fake.path, seed=SEED, game_map=MAP, config=READERS_PROFILE, **ROSTER
        ):
            if isinstance(step, TickOpened):
                for agent_id, player in sorted(step.state.players.items()):
                    if not player.alive:
                        continue
                    packet = service.build_packet(
                        world_state=step.state,
                        agent_id=agent_id,
                        engine_events=step.last_events,
                    )
                    rows.extend(
                        (agent_id, packet.tick, view.id, view.room)
                        for view in packet.visible_players
                        if view.action == "vent"
                    )
                    checks.extend(
                        (exit_fact, agent_id, packet.tick)
                        for exit_fact in pending
                        if agent_id in exit_fact.crewmates
                    )
                pending = []
            elif isinstance(step, TickAdvanced):
                found = _room_left_exits(step.pre_state, step.actions, step.events)
                for exit_fact, event in found:
                    exits.append(exit_fact)
                    pending.append(exit_fact)
                    witnessed.extend(
                        (exit_fact, crewmate)
                        for crewmate in exit_fact.crewmates
                        if crewmate in event.witnesses
                        or crewmate in event.source_witnesses
                    )
            elif isinstance(step, WalkComplete):
                completed = True
    finally:
        service.close()
    return WalkReading(
        exits=tuple(exits),
        rows=sorted(rows),
        checks=tuple(checks),
        witnessed=tuple(witnessed),
        completed=completed,
    )


def _room_left_exits(
    pre_state: WorldState,
    actions: Sequence[Action],
    events: Sequence[EngineEvent],
) -> list[tuple[RoomLeftExit, VentExitedEvent]]:
    """This tick's room-left-only exits, paired with the walk's own event."""

    _state, reference = advance_tick(
        pre_state,
        list(actions),
        game_map=MAP,
        vent_witness_rule="both_rooms",
    )
    assert [type(event) for event in reference] == [type(event) for event in events]
    roles = {pid: player.role for pid, player in pre_state.players.items()}
    found: list[tuple[RoomLeftExit, VentExitedEvent]] = []
    for both, walked in zip(reference, events, strict=True):
        if (
            not isinstance(both, VentExitedEvent)
            or both.source_room == both.destination_room
        ):
            continue
        assert isinstance(walked, VentExitedEvent)
        crew_left = tuple(p for p in both.source_witnesses if roles[p] == "CREWMATE")
        crew_there = [p for p in both.destination_witnesses if roles[p] == "CREWMATE"]
        if crew_left and not crew_there:
            found.append(
                (
                    RoomLeftExit(
                        tick=both.tick,
                        actor=both.actor,
                        source_room=both.source_room,
                        crewmates=crew_left,
                    ),
                    walked,
                )
            )
    return found


def _loader_rows(fake: FakeSet) -> list[VentRow]:
    """``ReplayLoader``'s memory walk, reading every agent's whole episodic log."""

    captured: list[Mapping[str, AgentMemory]] = []
    original = ReplayLoader._ingest_tick

    def keeping(
        loader: ReplayLoader,
        service: ObservationService,
        memories: Mapping[str, AgentMemory],
        state: WorldState,
        last_events: Sequence[EngineEvent],
    ) -> dict[str, tuple[EpisodicEvent, ...]]:
        if not captured or captured[-1] is not memories:
            captured.append(memories)
        return original(loader, service, memories, state, last_events)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(ReplayLoader, "_ingest_tick", keeping)
        ReplayLoader(fake.set_dir)._walk(fake.path, SEED, collect_memory=True)
    assert len(captured) == 1
    return _vent_rows(
        {
            agent_id: memory.episodic.recent(since_tick=0)
            for agent_id, memory in captured[0].items()
        }
    )


@dataclass(frozen=True)
class GateResult:
    problems: list[str]
    exits: tuple[RoomLeftExit, ...]
    checks: int


def reader_gate(fake: FakeSet, tmp: Path) -> GateResult:
    """The three readings, and every way they fail the physical rule."""

    walk = _walk_reading(fake, tmp)
    assert walk.completed, "the verified walk did not reach the end of the game"
    live = _vent_rows(fake.live)
    loader = _loader_rows(fake)
    problems: list[str] = []
    if live != walk.rows:
        problems.append("live: the game's own memory disagrees with the walk's packets")
    if loader != walk.rows:
        problems.append("loader: the memory walk disagrees with the walk's packets")
    for exit_fact, crewmate in walk.witnessed:
        problems.append(
            f"walk: tick {exit_fact.tick} lists {crewmate} in the room left as a "
            f"witness to {exit_fact.actor}'s exit"
        )
    for exit_fact, crewmate, packet_tick in walk.checks:
        for site, rows in (("live", live), ("loader", loader), ("walk", walk.rows)):
            if any(
                row[0] == crewmate
                and row[1] == packet_tick
                and row[2] == exit_fact.actor
                for row in rows
            ):
                problems.append(
                    f"{site}: {crewmate} holds a vent observation of "
                    f"{exit_fact.actor}'s exit at tick {exit_fact.tick}"
                )
    return GateResult(problems=problems, exits=walk.exits, checks=len(walk.checks))


def _both_rooms_arguments(config: RecordedExperimentConfig | None) -> EngineArguments:
    """The helper's result with the rule replaced by the default."""

    arguments = engine_arguments(config)
    arguments["vent_witness_rule"] = "both_rooms"
    return arguments


@contextmanager
def _withheld_at(site: str) -> Iterator[None]:
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(SITES[site], "engine_arguments", _both_rooms_arguments)
        yield


@pytest.fixture(scope="module")
def physical_game(tmp_path_factory: pytest.TempPathFactory) -> FakeSet:
    return record_fake_set(tmp_path_factory.mktemp("physical") / "9p2i")


def test_the_fixture_is_a_physical_recording_on_every_row(
    physical_game: FakeSet,
) -> None:
    rows = [
        json.loads(line)
        for line in physical_game.path.read_text(encoding="utf-8").splitlines()
    ]
    stamped = [row for row in rows if row["kind"] in ("tick", "game_over")]
    assert stamped and any(row["kind"] == "game_over" for row in stamped)
    for row in stamped:
        assert row["experiment_config"] == {
            "format_version": 1,
            **{
                key: value
                for key, value in RecordedExperimentConfig().model_dump().items()
                if key != "format_version"
            },
            "vent_witness_rule": "physical",
        }


def test_no_reader_gives_a_room_left_crewmate_the_physical_exit(
    physical_game: FakeSet, tmp_path: Path
) -> None:
    result = reader_gate(physical_game, tmp_path)
    # Not vacuous: seed 0 has room-left-only exits whose crewmate lives to the
    # next packet, where the default rule would hand it the vent.
    assert len(result.exits) >= 1 and result.checks >= 1
    assert result.problems == []


@pytest.mark.parametrize("site", sorted(SITES))
def test_a_site_that_forgets_the_rule_fails_the_gate_with_every_hash_equal(
    site: str, tmp_path: Path, physical_game: FakeSet
) -> None:
    """Planted: the helper's result replaced at exactly one site.

    The walk verifies every tick and meeting hash and the loader raises on any
    hash it cannot reproduce, so the gate goes red on witness sets alone.
    """

    if site == "live":
        with _withheld_at(site):
            fake = record_fake_set(tmp_path / "planted" / "9p2i")
        result = reader_gate(fake, tmp_path)
    else:
        with _withheld_at(site):
            result = reader_gate(physical_game, tmp_path)
    assert result.exits
    assert any(problem.startswith(f"{site}:") for problem in result.problems), (
        result.problems
    )


def test_a_helper_without_the_rule_refuses_the_physical_game(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, physical_game: FakeSet
) -> None:
    """Planted: the helper's threaded fields without this card's line."""

    monkeypatch.setattr(
        experiment_config, "_THREADED_ENGINE_FIELDS", ("redistribution_policy",)
    )
    with pytest.raises(ValueError, match="vent_witness_rule='physical'"):
        record_fake_set(tmp_path / "unthreaded" / "9p2i")
    with pytest.raises(ValueError, match="vent_witness_rule='physical'"):
        reader_gate(physical_game, tmp_path)


# --------------------------------------------------------------------------- #
# The config line                                                             #
# --------------------------------------------------------------------------- #


def test_the_helper_threads_the_recorded_rule() -> None:
    assert engine_arguments(PHYSICAL)["vent_witness_rule"] == "physical"
    assert engine_arguments(None)["vent_witness_rule"] == "both_rooms"
    assert engine_arguments(RecordedExperimentConfig())["vent_witness_rule"] == (
        "both_rooms"
    )
    assert "vent_witness_rule" in experiment_config._THREADED_ENGINE_FIELDS
    assert "vent_witness_rule" not in WAVE_ARMS_PENDING


def test_a_physical_config_round_trips_through_the_config_and_the_view() -> None:
    payload = PHYSICAL.model_dump(mode="json")
    assert payload["vent_witness_rule"] == "physical"
    assert RecordedExperimentConfig.model_validate(payload) == PHYSICAL
    assert (
        RecordedExperimentConfig.model_validate_json(PHYSICAL.model_dump_json())
        == PHYSICAL
    )
    view = ExperimentConfigView.model_validate(payload)
    assert view.vent_witness_rule == "physical"
    assert not PHYSICAL.is_default
    assert normalize_experiment_config(PHYSICAL) == PHYSICAL


def test_the_rule_at_its_default_serializes_without_the_key() -> None:
    for config in (
        RecordedExperimentConfig(),
        RecordedExperimentConfig(vent_witness_rule="both_rooms"),
        RecordedExperimentConfig(
            vent_witness_rule="both_rooms", crew_idle_policy="patrol"
        ),
    ):
        assert "vent_witness_rule" not in config.model_dump()
        assert "vent_witness_rule" not in json.loads(config.model_dump_json())
    assert RecordedExperimentConfig.model_validate({}).vent_witness_rule == "both_rooms"


def test_the_rule_is_an_engine_arm_not_a_tactical_change() -> None:
    assert experiment_config.FIELD_LAYER["vent_witness_rule"] == "engine"
    assert not PHYSICAL.has_tactical_changes
    assert RecordedExperimentConfig(crew_idle_policy="patrol").has_tactical_changes


# --------------------------------------------------------------------------- #
# The census, end to end through --set-dir                                    #
# --------------------------------------------------------------------------- #

_CELL = "vent_exits_seen_only_from_room_left"


def _set_dir_section(
    set_dir: Path, capsys: pytest.CaptureFixture[str]
) -> tuple[int, str, str]:
    code = publish_gameplay_census.main(["--set-dir", str(set_dir), "--json-stdout"])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_the_census_reads_zero_room_left_exits_on_a_physical_game(
    physical_game: FakeSet, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    exits = reader_gate(physical_game, tmp_path).exits
    assert exits
    code, out, err = _set_dir_section(physical_game.set_dir, capsys)
    assert (code, err) == (0, "")
    cell = json.loads(out)["cells"][_CELL]
    assert cell["numerator"] == 0
    assert cell["by_construction"] == "vent_witness_rule = physical"
    assert isinstance(cell["denominator"], int) and cell["denominator"] >= len(exits)


def test_the_census_walk_without_the_rule_raises_the_cells_breach(
    physical_game: FakeSet, capsys: pytest.CaptureFixture[str]
) -> None:
    """Planted: the rule withheld at the census walk's advance."""

    with _withheld_at("walk"):
        code, out, err = _set_dir_section(physical_game.set_dir, capsys)
    assert (code, out) == (1, "")
    assert err.startswith("conformance breach: ")
    assert "vent_witness_rule = physical" in err
    assert f"seed {SEED}" in err


def _callable_sites() -> Mapping[str, Callable[..., object]]:
    return {site: module.engine_arguments for site, module in SITES.items()}


def test_every_site_reads_the_helper_it_is_planted_at() -> None:
    """The plant patches the helper each site actually calls."""

    for site, helper in _callable_sites().items():
        assert helper is engine_arguments, site
