"""Every reader of a recorded kill cooldown follows it; the census checks the writes.

The reader gate records one fake-provider game at ``kill_cooldown_ticks = 6``
under the regroup reset and reads it four ways: a re-simulation this module owns
(the live game's recording against the recorded value), the shared replay walk,
``ReplayLoader`` and the prompt-byte golden's directory walk. Cooldowns are part
of the hashed state, so a site that forgets the value fails a hash: the seeding
at tick 0, an advance at the first kill, a meeting at the first regroup. The
planted cases replace the helper's value with ``None`` at exactly one of the
thirteen seeding, advance and meeting calls and require the gate to name that
call.

The rest of the module holds the readers that name their settings, the census's
grace window and its cooldown cell, the validity gate's homogeneity check and the
tactical lab's dial. Every recording here is a fake-provider game recorded into a
temporary directory from a declared config, except one count-only census case
over the committed candidate round 1, the one committed set recorded under the
regroup reset. No prompt is printed: the one prompt check is a regex count.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any, Final, NoReturn, TypedDict

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import TypeAdapter

import api.replay_loader as replay_loader_module
import eval.gameplay_census as census
import eval.recorded_settings as recorded_settings_module
import eval.replay_walk as replay_walk_module
import experiments.tactical_gameplay as lab_module
import orchestrator.game as game_module
import tests.meetings.test_prompt_byte_golden as golden
from api.replay_loader import ReplayLoader, ReplayStateMismatchError
from engine import meeting_reset as meeting_reset_module
from engine import tick as tick_module
from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import KilledEvent, MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map, resolve_kill_cooldown
from eval import evidence_honesty, funnel, kill_craft, solvability
from eval import win_condition_selfcheck
from eval.balance_eval import run_tournament_eval
from eval.evidence_honesty import compute_evidence_honesty
from eval.funnel import compute_information_funnel, compute_pooling_funnel
from eval.gameplay_census import (
    CensusInputs,
    CooldownWrite,
    EraKey,
    FieldUse,
    GameFacts,
    GameplayCensusConformanceError,
    GameplayCensusEraError,
    KillFact,
    MeetingFact,
    canonical_settings,
    census_from_inputs,
    fold_set,
    load_census_inputs,
    section_from_tally,
)
from eval.kill_craft import compute_kill_craft_report
from eval.replay_walk import (
    MeetingApplied,
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    WalkViolation,
    walk_replay,
)
from eval.solvability import compute_solvability_report
from eval.validity import run_validity_gate
from eval.win_condition_selfcheck import check_replay_win_condition
from experiments.tactical_gameplay import (
    MECHANISMS_WALK_CONFIG,
    Roster,
    candidate_configs,
    run_candidate,
)
from meetings.schemas import MeetingResult
from orchestrator.experiment_config import (
    EngineArguments,
    RecordedExperimentConfig,
    engine_arguments,
)
from orchestrator.game import (
    HeadlessGame,
    apply_meeting_result,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
    recorded_experiment_config,
)
from orchestrator.seeder import seed_initial_state
from tests._helpers.committed import census_inputs
from tests._helpers.scripted_meeting import (
    PROMPT_SET,
    Ejection,
    ScriptedMeetingClient,
    record_game,
)

_SCRIPTS: Final[Path] = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import _manifest_writer  # noqa: E402
import publish_gameplay_census  # noqa: E402
import validity_gate  # noqa: E402

MAP: Final[Map] = load_canonical_map()
SIX: Final[int] = 6
#: The reader-gate fixture: fake provider, the 9p2i sample roster, this seed.
SEED: Final[int] = 0
GAME_ID: Final[str] = f"headless-seed-{SEED}"


class _Roster(TypedDict):
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


ROSTER: Final[_Roster] = {"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}
COOLDOWN_SIX: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    kill_cooldown_ticks=SIX, meeting_reset="hub_with_grace"
)
_ACTIONS: Final[TypeAdapter[list[Action]]] = TypeAdapter(list[Action])
#: The impostor's own cooldown line in rendered memory (a count, never printed).
_COOLDOWN_LINE: Final[re.Pattern[str]] = re.compile(
    r"Your kill cooldown is (\d+) ticks\."
)


def _record(directory: Path, config: RecordedExperimentConfig | None) -> Path:
    record_game(directory, seed=SEED, config=config, **ROSTER)
    return directory


@pytest.fixture(scope="module")
def cooldown_game(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The reader-gate fixture's set directory."""

    return _record(tmp_path_factory.mktemp("cooldown") / "9p2i", COOLDOWN_SIX)


def _path(set_dir: Path) -> Path:
    return set_dir / f"replay-seed-{SEED}.jsonl"


def _impostor_cooldowns(state: WorldState) -> tuple[int | None, ...]:
    return tuple(
        state.cooldowns.get(pid)
        for pid, player in sorted(state.players.items())
        if player.alive and player.role == "IMPOSTOR"
    )


# --------------------------------------------------------------------------- #
# The four readings                                                           #
# --------------------------------------------------------------------------- #


class _Violation(AssertionError):
    def __init__(self, violation: WalkViolation) -> None:
        super().__init__(f"{violation.kind} at tick {violation.tick}")
        self.violation = violation


def _raise_violation(violation: WalkViolation) -> NoReturn:
    raise _Violation(violation)


#: A walk that verifies every tick hash and both meeting hashes.
READERS_PROFILE: Final[ReplayWalkConfig] = ReplayWalkConfig(
    profile="kill-cooldown-readers",
    on_violation=_raise_violation,
    verify_tick_hashes=True,
    verify_meeting_pre_hashes=True,
    verify_meeting_post_hashes=True,
    missing_meeting_row="violation",
    supports_experiments=True,
)


@dataclass(frozen=True)
class WalkReading:
    """The cooldowns the walk read after each write, and what the game held."""

    round_start: tuple[int | None, ...]
    after_kill: tuple[int | None, ...]
    regroup: tuple[int | None, ...]
    #: Kills whose killer stood alive on a later tick row.
    kills_with_a_next_row: int
    #: Regroups that resumed play with a living impostor.
    regroups_with_an_impostor: int
    completed: bool


def walk_reading(path: Path) -> WalkReading:
    round_start: tuple[int | None, ...] = ()
    after_kill: list[int | None] = []
    regroup: list[int | None] = []
    killers: list[tuple[int, PlayerId]] = []
    alive_rows: list[tuple[int, frozenset[PlayerId]]] = []
    regroups = 0
    completed = False
    for step in walk_replay(
        path, seed=SEED, game_map=MAP, config=READERS_PROFILE, **ROSTER
    ):
        if isinstance(step, TickOpened):
            if not alive_rows:
                round_start = _impostor_cooldowns(step.state)
            alive_rows.append(
                (
                    step.entry.tick,
                    frozenset(
                        pid
                        for pid, player in step.state.players.items()
                        if player.alive
                    ),
                )
            )
        elif isinstance(step, TickAdvanced):
            for event in step.events:
                if isinstance(event, KilledEvent):
                    after_kill.append(step.state.cooldowns.get(event.actor))
                    killers.append((event.tick, event.actor))
        elif isinstance(step, MeetingApplied) and step.state.phase == "PLAY":
            cooldowns = _impostor_cooldowns(step.state)
            regroup.extend(cooldowns)
            regroups += bool(cooldowns)
        elif isinstance(step, WalkComplete):
            completed = True
    return WalkReading(
        round_start=round_start,
        after_kill=tuple(after_kill),
        regroup=tuple(regroup),
        kills_with_a_next_row=sum(
            any(row > tick and killer in alive for row, alive in alive_rows)
            for tick, killer in killers
        ),
        regroups_with_an_impostor=regroups,
        completed=completed,
    )


def _walk_phase(violation: WalkViolation) -> str:
    if violation.kind == "meeting_post_hash_mismatch":
        return "meeting"
    if violation.kind == "tick_hash_mismatch":
        return "seeding" if violation.tick == 0 else "advance"
    return violation.kind


def reference_divergence(
    path: Path, *, override: Mapping[str, object] | None = None
) -> str | None:
    """Re-simulate the recording here, at its recorded settings; name a mismatch.

    This re-simulation calls the engine entry points this module imported, so a
    plant at any of the four sites does not reach it: a mismatch here means the
    recording itself was made at another cooldown. ``override`` replaces helper
    arguments, for the default re-simulation the non-vacuity check runs.
    """

    entries = read_all_entries(path)
    recorded = recorded_experiment_config(entries)
    settings_ = recorded if recorded is not None else RecordedExperimentConfig()
    engine: dict[str, Any] = {**engine_arguments(recorded), **(override or {})}
    meetings = {e.tick: e for e in entries if isinstance(e, MeetingReplayEntry)}
    state = seed_initial_state(
        seed=SEED,
        game_map=MAP,
        kill_cooldown_ticks=engine["kill_cooldown_ticks"],
        **ROSTER,
    )
    first = True
    for entry in (e for e in entries if isinstance(e, ReplayEntry)):
        if state.phase != "PLAY":
            break
        state, events = advance_tick(
            state, _ACTIONS.validate_python(list(entry.actions)), game_map=MAP, **engine
        )
        if _state_hash(state) != entry.state_hash:
            return f"{'seeding' if first else 'advance'} hash at tick {entry.tick}"
        first = False
        if state.phase != "MEETING":
            continue
        meeting = meetings[entry.tick]
        trigger = next(e for e in events if isinstance(e, MeetingTriggeredEvent))
        state, _post = apply_meeting_result(
            state,
            MeetingResult(
                meeting_id=meeting.meeting_id,
                triggered_by=meeting.triggered_by,
                trigger_tick=meeting.tick,
                outcome=meeting.outcome,
                ejected_player_id=meeting.ejected_player_id,
                ballots=meeting.ballots,
                contradictions=meeting.contradictions,
                transcript=meeting.transcript,
            ),
            game_map=MAP,
            triggering_body_id=trigger.body_id,
            redistribution_policy=settings_.redistribution_policy,
            meeting_reset=settings_.meeting_reset,
            kill_cooldown_ticks=engine["kill_cooldown_ticks"],
        )
        if _state_hash(state) != meeting.state_hash_after:
            return f"meeting hash at tick {entry.tick}"
    return None


def _loader_phase(error: ReplayStateMismatchError, path: Path) -> str:
    after = {
        e.state_hash_after
        for e in read_all_entries(path)
        if isinstance(e, MeetingReplayEntry)
    }
    if error.expected in after:
        return "meeting"
    return "seeding" if error.tick == 0 else "advance"


def _golden_phase(message: str) -> str:
    if "state_hash_after" in message:
        return "meeting"
    return "seeding" if f"{GAME_ID} tick 0:" in message else "advance"


def _unrecorded_round_start(config: RecordedExperimentConfig) -> tuple[int | None, ...]:
    """The live game's seeded cooldowns on its no-replay path."""

    game = HeadlessGame(
        seed=SEED,
        game_map=MAP,
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=None,
        meeting_runner=build_default_meeting_runner(
            llm_client=golden_fake_provider(),
            env={"AILIBI_PROMPT_SET": PROMPT_SET},
        ),
        experiment_config=config,
        **ROSTER,
    )
    return _impostor_cooldowns(game.run_unrecorded().initial_state)


def golden_fake_provider() -> Any:
    from llm.fake_provider import FakeProvider

    return FakeProvider()


def reader_gate(set_dir: Path) -> list[str]:
    """Every way the four readings, and the live no-replay seeding, miss the value.

    Each problem reads ``<reader>: <phase> ...``, the phase being where the
    first divergence fell: the seeding, an advance or an applied meeting.
    """

    path = _path(set_dir)
    problems: list[str] = []
    live = reference_divergence(path)
    if live is not None:
        problems.append(f"live: {live}")
    if set(_unrecorded_round_start(COOLDOWN_SIX)) != {SIX}:
        problems.append("live unrecorded: seeding at another cooldown")
    try:
        reading = walk_reading(path)
    except _Violation as violation:
        problems.append(f"walk: {_walk_phase(violation.violation)} {violation}")
    else:
        for writer, values in (
            ("seeding", reading.round_start),
            ("advance", reading.after_kill),
            ("meeting", reading.regroup),
        ):
            if not values or set(values) != {SIX}:
                problems.append(f"walk: {writer} read {sorted(set(values), key=str)}")
    try:
        view = ReplayLoader(set_dir).load_replay(GAME_ID)
    except ReplayStateMismatchError as error:
        problems.append(
            f"loader: {_loader_phase(error, path)} hash at tick {error.tick}"
        )
    else:
        if not view.metadata.outcome_verified:
            problems.append("loader: outcome not verified")
    try:
        walked = golden.walk_directory(set_dir)
    except AssertionError as error:
        problems.append(f"golden: {_golden_phase(str(error))} hash")
    else:
        if not walked.prompts or not all(p.reproduced for p in walked.prompts):
            problems.append("golden: a recorded prompt did not re-render")
        if walked.miscounted_meetings:
            problems.append("golden: a recorded call was not consumed once")
    return problems


# --------------------------------------------------------------------------- #
# The fixture is not vacuous                                                   #
# --------------------------------------------------------------------------- #


def test_the_fixture_is_a_cooldown_six_regroup_recording_on_every_row(
    cooldown_game: Path,
) -> None:
    rows = [
        json.loads(line)
        for line in _path(cooldown_game).read_text(encoding="utf-8").splitlines()
    ]
    stamped = [row for row in rows if row["kind"] in ("tick", "game_over")]
    assert stamped and stamped[-1]["kind"] == "game_over"
    for row in stamped:
        assert row["experiment_config"] == {
            "format_version": 1,
            "meeting_reset": "hub_with_grace",
            "kill_cooldown_ticks": SIX,
            **{
                key: value
                for key, value in RecordedExperimentConfig().model_dump().items()
                if key not in ("format_version", "meeting_reset")
            },
        }


def test_the_fixture_kills_regroups_and_diverges_at_the_default(
    cooldown_game: Path,
) -> None:
    reading = walk_reading(_path(cooldown_game))
    assert reading.completed
    assert reading.kills_with_a_next_row >= 1
    assert reading.regroups_with_an_impostor >= 1
    # The default re-simulation fails the hash of the first tick row: the
    # seeded cooldowns differ, so the state after tick 0 differs.
    assert reference_divergence(
        _path(cooldown_game), override={"kill_cooldown_ticks": None}
    ) == ("seeding hash at tick 0")


# --------------------------------------------------------------------------- #
# Every reader reads the recorded value                                        #
# --------------------------------------------------------------------------- #


def test_every_reader_reads_six_at_each_write(cooldown_game: Path) -> None:
    assert reader_gate(cooldown_game) == []
    reading = walk_reading(_path(cooldown_game))
    assert set(reading.round_start) == {SIX} and len(reading.round_start) == 2
    assert reading.after_kill and set(reading.after_kill) == {SIX}
    assert reading.regroup and set(reading.regroup) == {SIX}


def test_the_golden_re_renders_an_impostor_cooldown_above_the_maps(
    cooldown_game: Path,
) -> None:
    walked = golden.walk_directory(cooldown_game)
    assert walked.prompts and all(prompt.reproduced for prompt in walked.prompts)
    state = seed_initial_state(seed=SEED, game_map=MAP, **ROSTER)
    impostors = {pid for pid, p in state.players.items() if p.role == "IMPOSTOR"}
    above = sum(
        int(match.group(1)) > MAP.kill_cooldown_ticks
        for prompt in walked.prompts
        if prompt.agent_id in impostors
        for match in _COOLDOWN_LINE.finditer(prompt.recorded_prompt)
    )
    assert above >= 1


#: Each of the thirteen calls that seed, advance or apply a meeting, by the
#: module whose binding it calls, the bound name, and the calling function.
SITES: Final[Mapping[tuple[str, str], tuple[ModuleType, str, str]]] = {
    ("live", "seeding"): (game_module, "seed_initial_state", "run"),
    ("live unrecorded", "seeding"): (
        game_module,
        "seed_initial_state",
        "run_unrecorded",
    ),
    ("live", "advance"): (game_module, "advance_tick", "_run_loop"),
    ("live", "meeting"): (
        game_module,
        "apply_meeting_result",
        "_run_and_apply_meeting",
    ),
    ("loader", "seeding"): (replay_loader_module, "seed_initial_state", "_walk"),
    ("loader", "advance"): (replay_loader_module, "advance_tick", "_walk"),
    ("loader", "meeting"): (replay_loader_module, "apply_meeting_result", "_walk"),
    ("walk", "seeding"): (replay_walk_module, "seed_initial_state", "_walk_replay"),
    ("walk", "advance"): (replay_walk_module, "advance_tick", "_walk_replay"),
    ("walk", "meeting"): (replay_walk_module, "apply_meeting_result", "_walk_replay"),
    ("golden", "seeding"): (golden, "seed_initial_state", "walk_replay_meetings"),
    ("golden", "advance"): (golden, "advance_tick", "walk_replay_meetings"),
    ("golden", "meeting"): (golden, "apply_meeting_result", "walk_replay_meetings"),
}


@contextmanager
def _forgotten_at(site: tuple[str, str]) -> Iterator[list[int]]:
    """The helper's value replaced by ``None`` at exactly one call."""

    module, name, caller = SITES[site]
    real = getattr(module, name)
    hits: list[int] = []

    def forgetting(*args: Any, **kwargs: Any) -> Any:
        if sys._getframe(1).f_code.co_name == caller:
            assert "kill_cooldown_ticks" in kwargs, site
            kwargs = {**kwargs, "kill_cooldown_ticks": None}
            hits.append(1)
        return real(*args, **kwargs)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(module, name, forgetting)
        yield hits


@pytest.mark.parametrize("site", sorted(SITES), ids=" ".join)
def test_a_site_that_forgets_the_value_fails_the_gate_naming_it(
    site: tuple[str, str], cooldown_game: Path, tmp_path: Path
) -> None:
    reader, phase = site
    with _forgotten_at(site) as hits:
        if reader == "live":
            set_dir = _record(tmp_path / "planted" / "9p2i", COOLDOWN_SIX)
            problems = reader_gate(set_dir)
        else:
            problems = reader_gate(cooldown_game)
    assert hits, f"the plant at {site} never ran"
    assert any(problem.startswith(f"{reader}: {phase}") for problem in problems), (
        problems
    )


def test_every_site_calls_the_binding_it_is_planted_at() -> None:
    for site, (module, name, _caller) in SITES.items():
        assert (
            getattr(module, name)
            is {
                "seed_initial_state": seed_initial_state,
                "advance_tick": advance_tick,
                "apply_meeting_result": apply_meeting_result,
            }[name]
        ), site


# --------------------------------------------------------------------------- #
# The readers that name their settings                                         #
# --------------------------------------------------------------------------- #


def _win_condition(directory: Path) -> object:
    return [check_replay_win_condition(_path(directory), seed=SEED, **ROSTER)]


#: The five instruments that read the readable settings whole, one entry point
#: per walk, and the module holding each one's field list.
INSTRUMENTS: Final[Mapping[str, tuple[ModuleType, str, Callable[[Path], object]]]] = {
    "kill-craft": (kill_craft, "KILL_CRAFT_READS", compute_kill_craft_report),
    "funnel": (funnel, "FUNNEL_READS", compute_information_funnel),
    "pooling-funnel": (funnel, "FUNNEL_READS", compute_pooling_funnel),
    "solvability": (solvability, "SOLVABILITY_READS", compute_solvability_report),
    "win-condition": (win_condition_selfcheck, "WIN_CONDITION_READS", _win_condition),
    "evidence-honesty": (evidence_honesty, "HONESTY_READS", compute_evidence_honesty),
}


def test_the_readable_settings_name_the_cooldown() -> None:
    assert "kill_cooldown_ticks" in recorded_settings_module.READABLE_SETTINGS
    for module, reads, _run in INSTRUMENTS.values():
        assert "kill_cooldown_ticks" in getattr(module, reads)


@pytest.mark.parametrize("instrument", sorted(INSTRUMENTS))
def test_each_instrument_walks_the_cooldown_game_with_its_hashes(
    instrument: str, cooldown_game: Path
) -> None:
    _module, _reads, run = INSTRUMENTS[instrument]
    assert run(cooldown_game) is not None


@pytest.mark.parametrize("instrument", sorted(INSTRUMENTS))
def test_without_the_cooldown_in_the_readable_settings_each_instrument_refuses(
    instrument: str, cooldown_game: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Perturbed: the field removed from the readable settings, and so from every
    field list that reads them whole."""

    narrowed = recorded_settings_module.READABLE_SETTINGS - {"kill_cooldown_ticks"}
    monkeypatch.setattr(recorded_settings_module, "READABLE_SETTINGS", narrowed)
    for module, reads, _run in INSTRUMENTS.values():
        monkeypatch.setattr(module, reads, narrowed)
    _module, _reads, run = INSTRUMENTS[instrument]
    with pytest.raises(ValueError, match="kill_cooldown_ticks=6"):
        run(cooldown_game)


# --------------------------------------------------------------------------- #
# The census: the grace window and the cooldown cell                           #
# --------------------------------------------------------------------------- #


def _set_dir_section(
    set_dir: Path, capsys: pytest.CaptureFixture[str]
) -> tuple[int, dict[str, Any] | None, str]:
    code = publish_gameplay_census.main(["--set-dir", str(set_dir), "--json-stdout"])
    captured = capsys.readouterr()
    return code, (json.loads(captured.out) if captured.out else None), captured.err


def test_the_census_reads_the_recorded_window_and_every_write_at_six(
    cooldown_game: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The publication pools the nine-player sets by source, so the set stands in
    # for one of them.
    loaded = load_census_inputs(cooldown_game)
    published = census_from_inputs([replace(loaded, source="replays/samples/9p2i")])
    assert published.constants["grace_window_ticks"] == SIX
    code, section, err = _set_dir_section(cooldown_game, capsys)
    assert (code, err) == (0, "") and section is not None
    grace = section["cells"]["kills_in_grace_window_after_regroup"]
    assert (grace["numerator"], grace["by_construction"]) == (
        0,
        "meeting_reset = hub_with_grace",
    )
    assert grace["denominator"] >= 1
    cell = section["cells"]["kill_cooldowns_differing_from_recorded"]
    writes = section["tables"]["kill_cooldown_writes_by_writer"]["counts"]
    assert (cell["numerator"], cell["by_construction"]) == (0, "always")
    assert set(writes) == {"round_start", "after_kill", "regroup"}
    assert all(count > 0 for count in writes.values())
    assert cell["denominator"] == sum(writes.values())


@pytest.mark.parametrize(
    ("writer", "module"),
    [
        ("round_start", "orchestrator.seeder"),
        ("after_kill", "engine.tick"),
        ("regroup", "engine.meeting_reset"),
    ],
)
def test_a_write_left_at_the_maps_value_breaches_the_cell_naming_its_writer(
    writer: str,
    module: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: one engine write restored to the map's value, in the live game and
    in the census walk alike, so every hash passes and only the cell can tell."""

    def map_value(game_map: Map, kill_cooldown_ticks: int | None) -> int:
        return game_map.kill_cooldown_ticks

    monkeypatch.setattr(sys.modules[module], "resolve_kill_cooldown", map_value)
    set_dir = _record(tmp_path / "planted" / "9p2i", COOLDOWN_SIX)
    player, tick = _first_write(_path(set_dir), writer)
    code, section, err = _set_dir_section(set_dir, capsys)
    assert (code, section) == (1, None)
    assert err.startswith("conformance breach: Kill cooldowns that differ")
    assert (
        f"set planted/9p2i, seed {SEED}, the {writer} write of {player}'s cooldown "
        f"at tick {tick} (4 against 6) breaches it"
    ) in err, err


def _first_write(path: Path, writer: str) -> tuple[PlayerId, int]:
    """The impostor and tick of ``writer``'s first write, read from a full walk."""

    for step in walk_replay(
        path, seed=SEED, game_map=MAP, config=READERS_PROFILE, **ROSTER
    ):
        if writer == "round_start" and isinstance(step, TickOpened):
            return _living_impostors(step.state)[0], step.state.tick
        if writer == "after_kill" and isinstance(step, TickAdvanced):
            for event in step.events:
                if isinstance(event, KilledEvent):
                    return event.actor, event.tick
        if (
            writer == "regroup"
            and isinstance(step, MeetingApplied)
            and step.state.phase == "PLAY"
        ):
            return _living_impostors(step.state)[0], step.entry.tick
    raise AssertionError(f"no {writer} write in {path.name}")


def _living_impostors(state: WorldState) -> tuple[PlayerId, ...]:
    return tuple(
        pid
        for pid, player in sorted(state.players.items())
        if player.alive and player.role == "IMPOSTOR"
    )


def test_the_writer_modules_are_the_ones_planted() -> None:
    assert sys.modules["engine.tick"] is tick_module
    assert sys.modules["engine.meeting_reset"] is meeting_reset_module


#: A fake 9p2i game at cooldown 6 under the regroup reset whose first meeting
#: resumes play and whose second, every voter but turn 0's speaker ejecting that
#: crewmate, ends the game with both impostors alive below the window.
ENDING_SEED: Final[int] = 4
ENDING_EJECTION: Final[Ejection] = Ejection(meeting=1, target_turn=0)


def test_a_meeting_that_ends_the_game_writes_no_regroup_cooldown(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Planted: a meeting that ends the game is not a regroup. Its living
    impostors keep the cooldown they held, below the window, so a regroup write
    counted there breaches the cell."""

    set_dir = tmp_path / "ending" / "9p2i"
    path = record_game(
        set_dir,
        seed=ENDING_SEED,
        config=COOLDOWN_SIX,
        client=ScriptedMeetingClient(script=(), ejections=(ENDING_EJECTION,)),
        **ROSTER,
    )
    applied = [
        step
        for step in walk_replay(
            path, seed=ENDING_SEED, game_map=MAP, config=READERS_PROFILE, **ROSTER
        )
        if isinstance(step, MeetingApplied)
    ]
    resumed = [step for step in applied if step.state.phase == "PLAY"]
    ending = applied[-1]
    # Not vacuous: a regroup resumes play, and the game ends at a meeting with
    # living impostors whose cooldowns are below the window.
    assert resumed and ending.state.phase == "GAME_OVER"
    ejected = ending.entry.ejected_player_id
    assert ending.entry.outcome == "EJECTED" and ejected is not None
    assert ending.state.players[ejected].role == "CREWMATE"
    left = [ending.state.cooldowns.get(pid) for pid in _living_impostors(ending.state)]
    assert left and all(ticks is not None and ticks < SIX for ticks in left)
    regroup_writes = [
        (write.tick, write.player, write.ticks)
        for write in load_census_inputs(set_dir).games[0].cooldown_writes
        if write.writer == "regroup"
    ]
    assert regroup_writes == [
        (step.entry.tick, pid, SIX)
        for step in resumed
        for pid in _living_impostors(step.state)
    ]
    code, section, err = _set_dir_section(set_dir, capsys)
    assert (code, err) == (0, "") and section is not None
    cell = section["cells"]["kill_cooldowns_differing_from_recorded"]
    writes = section["tables"]["kill_cooldown_writes_by_writer"]["counts"]
    assert cell["numerator"] == 0
    assert writes["regroup"] == len(regroup_writes)


#: Candidate round 1, the one committed set recorded under the regroup reset.
ROUND_ONE: Final[Path] = (
    Path(__file__).resolve().parents[2]
    / "replays"
    / "candidates"
    / "stage-b-r1"
    / "9p2i"
)


def test_round_one_reads_every_cooldown_write_at_the_maps_value() -> None:
    """Count-only, on the committed round 1: 0 of 487 writes differ from 4 (100 at
    round start, 227 after a kill, 160 at a regroup) and 0 of 139 kills fall in a
    grace window. Some of its meetings end the game with a living impostor below
    the window, so counting those meetings as regroups breaches the cell.

    The set is walked once, through the shared committed-walk cache, and folded
    and serialized by the ``--set-dir`` path's own function.
    """

    loaded = census_inputs(ROUND_ONE)
    ending = sum(
        1
        for game in loaded.games
        for meeting in game.meetings
        if meeting.phase_after == "GAME_OVER"
        and any(
            pid != meeting.ejected and ticks != MAP.kill_cooldown_ticks
            for pid, ticks in meeting.impostor_cooldowns_at_open
        )
    )
    assert ending >= 1
    section = json.loads(
        publish_gameplay_census.set_dir_json(ROUND_ONE, load=census_inputs)
    )
    cell = section["cells"]["kill_cooldowns_differing_from_recorded"]
    assert (cell["numerator"], cell["denominator"], cell["by_construction"]) == (
        0,
        487,
        "always",
    )
    assert section["tables"]["kill_cooldown_writes_by_writer"]["counts"] == {
        "round_start": 100,
        "after_kill": 227,
        "regroup": 160,
    }
    grace = section["cells"]["kills_in_grace_window_after_regroup"]
    assert (grace["numerator"], grace["denominator"]) == (0, 139)


def _cooldown_era(**settings_: Any) -> EraKey:
    return EraKey(
        settings=canonical_settings(settings_),
        temporal_observation_version=None,
        substrate_flags=None,
        prompt_stamps=None,
    )


def _carrier(era: EraKey, *, kill_tick: int, meeting_tick: int = 10) -> CensusInputs:
    """A census carrier: one regroup meeting at ``meeting_tick`` and one later kill.

    Its window is the census's own reading of the era,
    :func:`eval.gameplay_census.recorded_kill_cooldown`.
    """

    roles: Mapping[PlayerId, Role] = MappingProxyType(
        {"p-1": "IMPOSTOR", "p-2": "CREWMATE", "p-3": "CREWMATE"}
    )
    meeting = MeetingFact(
        meeting_id="meeting-0",
        tick=meeting_tick,
        trigger_kind="emergency",
        opener="p-2",
        trigger_body=None,
        bodies_at_open=(),
        in_vent_at_open=frozenset(),
        impostor_cooldowns_at_open=(),
        living=frozenset(roles),
        sabotage_active=False,
        outcome="SKIPPED",
        ejected=None,
        vent_flag_subjects=(),
        turns=(),
        ballots=(),
        ballot_floor=0.6,
        selector_pick=None,
        opener_prompt_has_kill_tick_handle=None,
        own_kill_rows=(),
        trigger_tick_dropped_events=(),
        phase_after="PLAY",
        in_vent_after=frozenset(),
        bodies_after=frozenset(),
        regrouped=True,
    )
    game = GameFacts(
        seed=SEED,
        roles=roles,
        era=era,
        kills=(
            KillFact(
                tick=kill_tick, killer="p-1", room="STORAGE", witnesses=frozenset()
            ),
        ),
        vents=(),
        bodies=(),
        frames=MappingProxyType({}),
        meetings=(meeting,),
        discarded=(),
        rows_without_dispositions=0,
        winner="IMPOSTORS",
        terminal_tick=60,
    )
    return CensusInputs(
        label="planted/9p2i",
        source="replays/planted/9p2i",
        era=era,
        kill_cooldown_ticks=census.recorded_kill_cooldown(era, MAP),
        neighbours=MappingProxyType({}),
        games=(game,),
    )


_SIX_ERA: Final[dict[str, Any]] = {
    "meeting_reset": "hub_with_grace",
    "kill_cooldown_ticks": SIX,
}


def test_a_kill_at_meeting_plus_five_breaches_the_grace_window_at_six() -> None:
    carrier = _carrier(_cooldown_era(**_SIX_ERA), kill_tick=15)
    assert carrier.kill_cooldown_ticks == SIX
    with pytest.raises(
        GameplayCensusConformanceError,
        match=(
            r"^Kills in the grace window after a regroup must be 0 by construction "
            r"while meeting_reset = hub_with_grace, but set planted/9p2i, seed 0, "
            r"tick 15 after meeting meeting-0 breaches it$"
        ),
    ):
        fold_set(carrier)
    # The tick after the window is an ordinary kill.
    after = section_from_tally(
        fold_set(_carrier(_cooldown_era(**_SIX_ERA), kill_tick=17))
    )
    grace = after.cells["kills_in_grace_window_after_regroup"]
    assert (grace.numerator, grace.denominator) == (0, 1)


def test_the_same_kill_in_the_default_cooldown_era_raises_nothing() -> None:
    default = _carrier(_cooldown_era(meeting_reset="hub_with_grace"), kill_tick=15)
    assert default.kill_cooldown_ticks == MAP.kill_cooldown_ticks
    grace = section_from_tally(fold_set(default)).cells[
        "kills_in_grace_window_after_regroup"
    ]
    assert (grace.numerator, grace.denominator) == (0, 1)


def test_the_window_read_from_the_map_again_misses_the_plus_five_kill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Perturbed: the census reads its window from the map, not the recording."""

    def map_value(game_map: Map, kill_cooldown_ticks: int | None) -> int:
        return game_map.kill_cooldown_ticks

    monkeypatch.setattr(census, "resolve_kill_cooldown", map_value)
    carrier = _carrier(_cooldown_era(**_SIX_ERA), kill_tick=15)
    assert carrier.kill_cooldown_ticks == MAP.kill_cooldown_ticks
    fold_set(carrier)  # no breach: the T+5 kill reads as ordinary


def test_the_loader_reads_the_window_from_the_recorded_era(
    cooldown_game: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert load_census_inputs(cooldown_game).kill_cooldown_ticks == SIX
    seen: list[object] = []
    real = resolve_kill_cooldown

    def spy(game_map: Map, kill_cooldown_ticks: int | None) -> int:
        seen.append(kill_cooldown_ticks)
        return real(game_map, kill_cooldown_ticks)

    monkeypatch.setattr(census, "resolve_kill_cooldown", spy)
    assert load_census_inputs(cooldown_game).kill_cooldown_ticks == SIX
    assert seen == [SIX]


def _write(
    writer: str, ticks: int | None, tick: int = 0, player: PlayerId = "p-1"
) -> CooldownWrite:
    return CooldownWrite(writer=writer, tick=tick, player=player, ticks=ticks)  # type: ignore[arg-type]


def _writes_carrier(*writes: CooldownWrite, window: int = SIX) -> CensusInputs:
    base = _carrier(_cooldown_era(**_SIX_ERA), kill_tick=40)
    return replace(
        base,
        kill_cooldown_ticks=window,
        games=(replace(base.games[0], cooldown_writes=writes),),
    )


@settings(deadline=None, max_examples=60)
@given(
    values=st.lists(
        st.tuples(
            st.sampled_from(("round_start", "after_kill", "regroup")),
            st.one_of(st.none(), st.integers(min_value=1, max_value=12)),
            st.sampled_from(("p-1", "p-2")),
        ),
        max_size=8,
    ),
    window=st.integers(min_value=1, max_value=12),
)
def test_the_cell_breaches_exactly_when_a_write_differs_from_the_window(
    values: list[tuple[str, int | None, PlayerId]], window: int
) -> None:
    carrier = _writes_carrier(
        *(
            _write(writer, ticks, tick, player)
            for tick, (writer, ticks, player) in enumerate(values)
        ),
        window=window,
    )
    differing = [
        (tick, writer, ticks, player)
        for tick, (writer, ticks, player) in enumerate(values)
        if ticks != window
    ]
    if differing:
        tick, writer, ticks, player = differing[0]
        with pytest.raises(
            GameplayCensusConformanceError,
            match=re.escape(
                f"the {writer} write of {player}'s cooldown at tick {tick} "
                f"({ticks} against {window})"
            ),
        ):
            fold_set(carrier)
        return
    section = section_from_tally(fold_set(carrier))
    cell = section.cells["kill_cooldowns_differing_from_recorded"]
    assert (cell.numerator, cell.denominator) == (0, len(values))
    table = section.tables["kill_cooldown_writes_by_writer"].counts
    assert sum(table.values()) == len(values)
    for writer in ("round_start", "after_kill", "regroup"):
        assert table.get(writer, 0) == sum(w == writer for w, _, _ in values)


def test_the_writes_read_living_impostors_only() -> None:
    state = seed_initial_state(seed=SEED, game_map=MAP, **ROSTER)
    impostors = _living_impostors(state)
    crewmate = min(
        p for p, player in state.players.items() if player.role == "CREWMATE"
    )
    players = dict(state.players)
    players[impostors[1]] = replace(players[impostors[1]], alive=False)
    cooldowns = {impostors[0]: 3, impostors[1]: 2, crewmate: 1}
    planted = replace(state, players=players, cooldowns=cooldowns)
    assert census._impostor_cooldowns(planted, "regroup", 9) == (
        CooldownWrite(writer="regroup", tick=9, player=impostors[0], ticks=3),
    )
    missing = replace(planted, cooldowns={})
    assert census._impostor_cooldowns(missing, "round_start", 0) == (
        CooldownWrite(writer="round_start", tick=0, player=impostors[0], ticks=None),
    )


@pytest.mark.parametrize("value", [True, "6", 6.5])
def test_a_recorded_cooldown_that_is_not_a_tick_count_is_refused(value: Any) -> None:
    era = _cooldown_era(kill_cooldown_ticks=value)
    with pytest.raises(census.GameplayCensusFieldError, match="not a tick count"):
        census.recorded_kill_cooldown(era, MAP)


def test_the_census_refuses_sets_at_different_windows() -> None:
    six = _carrier(_cooldown_era(**_SIX_ERA), kill_tick=40)
    four = replace(six, kill_cooldown_ticks=MAP.kill_cooldown_ticks)
    with pytest.raises(ValueError, match="the sets ran at different kill cooldowns"):
        census_from_inputs([six, four])


def test_the_cell_and_table_carry_the_names_the_record_card_reads() -> None:
    cell = census.CELLS["kill_cooldowns_differing_from_recorded"]
    assert cell.title == "Kill cooldowns that differ from the recorded value"
    assert cell.guard is census.ALWAYS and cell.scope is None
    table = census.TABLES["kill_cooldown_writes_by_writer"]
    assert table.scope is None and table.heading == cell.heading


def test_a_field_use_takes_exactly_one_kind() -> None:
    assert FieldUse(value_read_by="the window").value_read_by == "the window"
    assert FieldUse(predicates=("always",)).predicates == ("always",)
    assert FieldUse(reason="a reason").reason == "a reason"
    for planted in (
        {},
        {"predicates": ("always",), "value_read_by": "the window"},
        {"value_read_by": "the window", "reason": "a reason"},
        {"predicates": ("always",), "reason": "a reason"},
    ):
        with pytest.raises(ValueError, match="exactly one"):
            FieldUse(**planted)


def test_the_cooldown_field_is_published_as_read_as_a_value() -> None:
    use = census.FIELD_CLASSIFICATION["kill_cooldown_ticks"]
    assert use.value_read_by and not use.predicates and not use.reason
    row = census._field_classification_view()["kill_cooldown_ticks"]
    assert row.startswith("read as a value by: ") and "not read" not in row


# --------------------------------------------------------------------------- #
# Homogeneity: the validity gate and the census era                            #
# --------------------------------------------------------------------------- #

_FAKE_SHA: Final[str] = "abc1234"


def _fake_set(directory: Path, config: RecordedExperimentConfig | None) -> Path:
    """Two fake 4p/1i games recorded as the recorder does, with roster and MANIFEST."""

    run_tournament_eval(
        seeds=(0, 1),
        output_dir=directory,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        experiment_config=config,
    )
    for audit in directory.glob("*.audit.jsonl"):
        audit.unlink()
    _manifest_writer.ensure_roster_descriptor(
        directory, num_players=4, num_impostors=1, tasks_per_crewmate=1
    )
    _manifest_writer.update_manifest(
        directory / "MANIFEST.md",
        directory,
        (0, 1),
        git_sha=_FAKE_SHA,
        refreshed_at="2026-10-01",
        model_override="fake-meeting",
    )
    return directory


@pytest.fixture(scope="module")
def homogeneity_sets(tmp_path_factory: pytest.TempPathFactory) -> Mapping[str, Path]:
    root = tmp_path_factory.mktemp("homogeneity")
    six = _fake_set(root / "six", RecordedExperimentConfig(kill_cooldown_ticks=SIX))
    bare = _fake_set(root / "bare", None)
    mixed = Path(shutil.copytree(six, root / "mixed"))
    shutil.copy(bare / "replay-seed-1.jsonl", mixed / "replay-seed-1.jsonl")
    _manifest_writer.update_manifest(
        mixed / "MANIFEST.md",
        mixed,
        (1,),
        git_sha=_FAKE_SHA,
        refreshed_at="2026-10-01",
        model_override="fake-meeting",
    )
    return {"six": six, "mixed": mixed}


def _gate(
    directory: Path, declared: Path | None, capsys: pytest.CaptureFixture[str]
) -> tuple[int, dict[str, list[str]]]:
    arguments = [str(directory), "--json"]
    if declared is not None:
        arguments += ["--expected-experiment-config", str(declared)]
    code = validity_gate.main(arguments)
    report = json.loads(capsys.readouterr().out)
    return code, {
        check["name"]: check["violations"]
        for check in report["checks"]
        if not check["passed"]
    }


def test_the_validity_gate_fails_a_set_mixing_cooldowns_naming_the_odd_game(
    homogeneity_sets: Mapping[str, Path],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    declared = tmp_path / "config.json"
    declared.write_text('{"format_version": 1, "kill_cooldown_ticks": 6}\n')
    code, failing = _gate(homogeneity_sets["mixed"], declared, capsys)
    assert code == 1 and list(failing) == ["cost_and_provenance_exact"]
    (line,) = failing["cost_and_provenance_exact"]
    assert line.startswith(
        "headless-seed-1: recorded experiment config (none: historical defaults)"
    )
    code, failing = _gate(homogeneity_sets["mixed"], None, capsys)
    assert code == 1 and list(failing) == ["cost_and_provenance_exact"]
    (line,) = failing["cost_and_provenance_exact"]
    assert line.startswith("headless-seed-0: ") and "kill_cooldown_ticks=6" in line
    code, failing = _gate(homogeneity_sets["six"], declared, capsys)
    assert (code, failing) == (0, {})
    assert run_validity_gate(
        homogeneity_sets["six"],
        expected_experiment_config=RecordedExperimentConfig(kill_cooldown_ticks=SIX),
    ).passed


def test_the_census_refuses_a_set_mixing_cooldowns(
    homogeneity_sets: Mapping[str, Path],
) -> None:
    assert load_census_inputs(homogeneity_sets["six"]).kill_cooldown_ticks == SIX
    with pytest.raises(GameplayCensusEraError, match="settings"):
        load_census_inputs(homogeneity_sets["mixed"])


# --------------------------------------------------------------------------- #
# The tactical lab's dial                                                      #
# --------------------------------------------------------------------------- #

#: A development seed and roster whose ``stage_b_full`` game kills before tick 6.
LAB_SEED: Final[int] = 1000
LAB_ROSTER: Final[Roster] = Roster(num_players=4, num_impostors=1, tasks_per_crewmate=1)


def _first_kill(arm: str, directory: Path) -> int | None:
    """The tick of the arm's first ``Killed`` event, read from its replay."""

    directory.mkdir(parents=True)
    path = directory / f"replay-seed-{LAB_SEED}.jsonl"
    row = run_candidate(
        seed=LAB_SEED,
        roster=LAB_ROSTER,
        config=candidate_configs()[arm],
        replay_path=path,
    )
    assert row.error is None and row.completion_status == "completed"
    kills = [
        event.tick
        for step in walk_replay(
            path,
            seed=LAB_SEED,
            game_map=MAP,
            config=MECHANISMS_WALK_CONFIG,
            **LAB_ROSTER.model_dump(),
        )
        if isinstance(step, TickAdvanced)
        for event in step.events
        if isinstance(event, KilledEvent)
    ]
    return min(kills) if kills else None


def test_the_dial_holds_the_first_kill_back(tmp_path: Path) -> None:
    first_at_four = _first_kill("stage_b_full", tmp_path / "four")
    assert first_at_four is not None and first_at_four < SIX
    first_at_six = _first_kill("stage_b_full_kill_cooldown_6", tmp_path / "six")
    first_at_eight = _first_kill("stage_b_full_kill_cooldown_8", tmp_path / "eight")
    assert first_at_six is not None and first_at_six >= SIX
    assert first_at_eight is not None and first_at_eight >= 8


def _withheld(config: RecordedExperimentConfig | None) -> EngineArguments:
    arguments = engine_arguments(config)
    arguments["kill_cooldown_ticks"] = None
    return arguments


def test_the_six_arm_with_the_field_withheld_kills_before_six(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Perturbed: every engine-arguments binding the lab's run and its walk call
    drops the field, so the hashes agree and only the first kill tells."""

    for module in (game_module, replay_walk_module, replay_loader_module, lab_module):
        monkeypatch.setattr(module, "engine_arguments", _withheld)
    first = _first_kill("stage_b_full_kill_cooldown_6", tmp_path / "withheld")
    assert first is not None and first < SIX


def test_the_dial_arms_are_the_full_arm_plus_the_cooldown() -> None:
    configs = candidate_configs()
    full = configs["stage_b_full"].model_dump()
    assert "kill_cooldown_ticks" not in full
    for arm, ticks in (
        ("stage_b_full_kill_cooldown_6", 6),
        ("stage_b_full_kill_cooldown_8", 8),
    ):
        assert configs[arm].model_dump() == {**full, "kill_cooldown_ticks": ticks}


def test_the_comparison_publishes_ticks_to_parity_over_its_own_arms(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The output's one new key is the summary of the rows it carries.

    The games are stubbed (a parity win at a tick count that grows with the
    seed), so the test reads the summary's wiring, not the lab's games.
    """

    def stub_game(
        *,
        seed: int,
        roster: Roster,
        config: RecordedExperimentConfig,
        replay_path: Path,
    ) -> lab_module.GameMetrics:
        return lab_module.GameMetrics(
            seed=seed,
            roster=roster,
            counts={"tick_rows": seed - 990, "event:Killed": 1},
            maximum_finished_wait_ticks=0,
            completion_status="completed",
            winner="IMPOSTORS",
            reason="IMPOSTOR_PARITY",
            replay_sha256="",
            trajectory_sha256="",
            reported_cost_usd=0.0,
        )

    monkeypatch.setattr(lab_module, "run_candidate", stub_game)
    monkeypatch.setattr(lab_module, "measure_world_copy_control", lambda **kwargs: {})
    output = lab_module.build_comparison(
        split="development", arms=("stage_b_full_kill_cooldown_6",)
    )
    assert output["ticks_to_parity"] == lab_module.ticks_to_parity(output["arms"])
    assert output["ticks_to_parity"]["stage_b_full_kill_cooldown_6"]["9p2i"] == {
        "games": 8,
        "parity_games": 8,
        "parity_tick_rows_minimum": 10,
        "parity_tick_rows_median": 13.5,
        "parity_tick_rows_maximum": 17,
        "kills": 8,
    }


def test_ticks_to_parity_counts_only_parity_games() -> None:
    def row(reason: str | None, tick_rows: int, kills: int) -> dict[str, Any]:
        return {
            "reason": reason,
            "counts": {"tick_rows": tick_rows, "event:Killed": kills},
        }

    arms = {
        "arm": {
            "sets": {
                "9p2i": [
                    row("IMPOSTOR_PARITY", 30, 7),
                    row("CREWMATE_TASKS", 50, 2),
                    row("IMPOSTOR_PARITY", 20, 7),
                    row("IMPOSTOR_PARITY", 41, 7),
                ],
                "4p1i": [row("CREWMATE_TASKS", 60, 1), row(None, 96, 0)],
            }
        }
    }
    assert lab_module.ticks_to_parity(arms) == {
        "arm": {
            "9p2i": {
                "games": 4,
                "parity_games": 3,
                "parity_tick_rows_minimum": 20,
                "parity_tick_rows_median": 30,
                "parity_tick_rows_maximum": 41,
                "kills": 23,
            },
            "4p1i": {
                "games": 2,
                "parity_games": 0,
                "parity_tick_rows_minimum": None,
                "parity_tick_rows_median": None,
                "parity_tick_rows_maximum": None,
                "kills": 1,
            },
        }
    }
