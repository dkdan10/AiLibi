"""Unit tests for scripts/run_tournament.py roster + tasks-per-crewmate wiring.

Drives ``main()`` (bare-module import via ``tests/scripts/conftest.py``) on a
tiny seed range and a low tick budget so the fake-provider run is fast, and
asserts the roster config threaded into ``run_tournament_eval``: the locked
default of 2 tasks/crewmate, a named ``--roster-preset``, explicit roster flags,
and the fail-loud conflict when a preset is combined with explicit flags.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Final

import pytest

import run_tournament as rt
from api.replay_loader import ReplayLoader
from eval import balance_eval
from eval.balance_eval import run_tournament_eval as _real_run_tournament_eval
from eval.report_schema import TournamentReport
from meetings.evidence_profile import EXPERIMENT_ENV_NAMES, profile_from_config
from orchestrator.experiment_config import RecordedExperimentConfig, meeting_values
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    TacticalPolicyStamp,
    fsm_default_tactical_policy_stamp,
    read_all_entries,
    read_tactical_policy_stamp,
)


def test_force_rerun_preserves_fresh_replay_and_audit_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    args = ["--num-games", "2", "--output-dir", str(tmp_path), "--max-ticks", "2"]
    assert rt.main(args) == 0
    paths = [
        tmp_path / f"replay-seed-{seed}{suffix}.jsonl"
        for seed in range(2)
        for suffix in ("", ".audit")
    ]
    original = {path: path.read_bytes() for path in paths}
    with pytest.raises(FileExistsError):
        rt.main(args)
    assert {path: path.read_bytes() for path in paths} == original
    assert rt.main([*args, "--force"]) == 0
    assert {path: path.read_bytes() for path in paths} == original


def _install_capturing_spy(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, int]
) -> None:
    """Patch ``run_tournament.run_tournament_eval`` to record the threaded config.

    The spy records the roster knobs ``main`` passes through, then delegates to
    the real harness (imported directly, same function object ``main`` calls) so
    ``main`` still produces a valid report end-to-end.
    """

    def spy(
        *,
        seeds: Sequence[int],
        output_dir: Path,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        max_ticks: int,
        force: bool,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
    ) -> TournamentReport:
        captured["num_players"] = num_players
        captured["num_impostors"] = num_impostors
        captured["tasks_per_crewmate"] = tasks_per_crewmate
        return _real_run_tournament_eval(
            seeds=seeds,
            output_dir=output_dir,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=max_ticks,
            force=force,
            tactical_policy_stamp=tactical_policy_stamp,
        )

    monkeypatch.setattr(rt, "run_tournament_eval", spy)


def test_main_defaults_to_four_one_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No roster flags: 4 players / 1 impostor / locked default of 2 tasks."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        ["--num-games", "1", "--output-dir", str(tmp_path), "--max-ticks", "2"]
    )

    assert rc == 0
    assert captured == {"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 2}


def test_main_roster_preset_supplies_all_three_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--roster-preset 9p2i`` threads 9 players / 2 impostors / 2 tasks."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--roster-preset",
            "9p2i",
            "--max-ticks",
            "2",
        ]
    )

    assert rc == 0
    assert captured == {"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}


def test_main_roster_preset_4p1i_pins_committed_baseline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--roster-preset 4p1i`` pins 1 task/crewmate (the committed baseline)."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--roster-preset",
            "4p1i",
            "--max-ticks",
            "2",
        ]
    )

    assert rc == 0
    assert captured == {"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1}


def test_main_explicit_flags_thread_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit roster flags stay usable for ad-hoc configs."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--num-players",
            "5",
            "--num-impostors",
            "2",
            "--tasks-per-crewmate",
            "1",
            "--max-ticks",
            "2",
        ]
    )

    assert rc == 0
    assert captured == {"num_players": 5, "num_impostors": 2, "tasks_per_crewmate": 1}


def test_main_rejects_preset_combined_with_explicit_roster_flag(
    tmp_path: Path,
) -> None:
    """A preset is mutually exclusive with explicit roster flags (fail loud)."""

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--roster-preset",
                "9p2i",
                "--num-players",
                "5",
            ]
        )


def test_main_rejects_preset_combined_with_tasks_flag(tmp_path: Path) -> None:
    """The conflict also fires for --tasks-per-crewmate, not just player count."""

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--roster-preset",
                "4p1i",
                "--tasks-per-crewmate",
                "3",
            ]
        )


# -- tactical-policy stamp flag (Task 15.9) -----------------------------------


def test_resolve_tactical_policy_stamp_none_is_absent() -> None:
    assert rt._resolve_tactical_policy_stamp(None) is None


def test_resolve_tactical_policy_stamp_fsm_default_literal() -> None:
    assert (
        rt._resolve_tactical_policy_stamp("fsm-default")
        == fsm_default_tactical_policy_stamp()
    )


def test_resolve_tactical_policy_stamp_json_file(tmp_path: Path) -> None:
    stamp = TacticalPolicyStamp(
        policy_id="wave2-champion-7",
        method="neuroevolution",
        encoder_version="encoder.v3",
        weights_sha256="a" * 64,
        anchor_policy="fsm-default",
    )
    path = tmp_path / "champion.json"
    path.write_text(stamp.model_dump_json(), encoding="utf-8")
    assert rt._resolve_tactical_policy_stamp(str(path)) == stamp


def test_resolve_tactical_policy_stamp_missing_file_is_fail_loud(
    tmp_path: Path,
) -> None:
    with pytest.raises(SystemExit, match="cannot read stamp file"):
        rt._resolve_tactical_policy_stamp(str(tmp_path / "nope.json"))


def test_resolve_tactical_policy_stamp_malformed_json_is_fail_loud(
    tmp_path: Path,
) -> None:
    # A JSON file missing required fields must fail loud, never silently record an
    # FSM default (AGENTS.md "no silent fallbacks").
    path = tmp_path / "bad.json"
    path.write_text('{"policy_id": "x"}', encoding="utf-8")
    with pytest.raises(SystemExit, match="not a valid TacticalPolicyStamp"):
        rt._resolve_tactical_policy_stamp(str(path))


def test_main_stamps_replay_on_disk_via_cli(tmp_path: Path) -> None:
    # The production seam the Task-15.12 corpus wrapper drives: a real end-to-end
    # CLI run with --tactical-policy-stamp fsm-default lands the stamp ON DISK.
    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "200",
            "--tactical-policy-stamp",
            "fsm-default",
        ]
    )
    assert rc == 0
    stamp = read_tactical_policy_stamp(tmp_path / "replay-seed-0.jsonl")
    assert stamp == fsm_default_tactical_policy_stamp()


def test_main_without_stamp_records_absent_via_cli(tmp_path: Path) -> None:
    # Omitting the flag records the absent = FSM default (no stamp on disk),
    # byte-identical to today's path.
    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "200",
        ]
    )
    assert rc == 0
    assert read_tactical_policy_stamp(tmp_path / "replay-seed-0.jsonl") is None


# -- the declared experiment config (--experiment-config) ---------------------

#: The declared test config: three arms that exist today, since the pending
#: guard refuses the wave's new values.
_TEST_CONFIG_JSON: Final[str] = (
    '{"format_version": 1, "meeting_reset": "hub_with_grace", '
    '"vent_exit_policy": "observed_risk", "bounded_rebuttal_version": 1}\n'
)
_TEST_CONFIG: Final[RecordedExperimentConfig] = (
    RecordedExperimentConfig.model_validate_json(_TEST_CONFIG_JSON)
)
#: Seed 1 of the 4p/1i/1-task roster holds a meeting under the fake provider.
_MEETING_SEED: Final[int] = 1


def _config_file(tmp_path: Path, text: str = _TEST_CONFIG_JSON) -> Path:
    path = tmp_path / "experiment-config.json"
    path.write_text(text, encoding="utf-8")
    return path


def _config_args(output_dir: Path, config: Path, *extra: str) -> list[str]:
    return [
        "--start-seed",
        str(_MEETING_SEED),
        "--num-games",
        "1",
        "--output-dir",
        str(output_dir),
        "--num-players",
        "4",
        "--num-impostors",
        "1",
        "--tasks-per-crewmate",
        "1",
        "--experiment-config",
        str(config),
        *extra,
    ]


def test_the_flag_records_exactly_the_file_on_every_row(tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert rt.main(_config_args(out, _config_file(tmp_path))) == 0
    replay = out / f"replay-seed-{_MEETING_SEED}.jsonl"
    entries = read_all_entries(replay)
    stamped = [
        entry.experiment_config
        for entry in entries
        if isinstance(entry, (ReplayEntry, GameEndReplayEntry))
    ]
    assert len(stamped) > 1
    assert all(config == _TEST_CONFIG for config in stamped)
    assert any(isinstance(entry, MeetingReplayEntry) for entry in entries)
    (out / "roster.json").write_text(
        '{"num_impostors": 1, "num_players": 4, "tasks_per_crewmate": 1}\n'
    )
    loaded = ReplayLoader(out).load_replay(f"headless-seed-{_MEETING_SEED}")
    assert loaded.metadata.outcome_verified
    view = loaded.metadata.experiment_config
    assert view is not None
    assert (
        view.meeting_reset,
        view.vent_exit_policy,
        view.bounded_rebuttal_version,
    ) == (
        "hub_with_grace",
        "observed_risk",
        1,
    )


def test_an_unknown_field_exits_before_any_file_is_written(tmp_path: Path) -> None:
    out = tmp_path / "out"
    config = _config_file(tmp_path, '{"format_version": 1, "hidden_travel": "on"}\n')
    with pytest.raises(SystemExit, match="hidden_travel"):
        rt.main(_config_args(out, config))
    assert not out.exists()


def test_a_repeated_key_is_refused_rather_than_resolved(tmp_path: Path) -> None:
    out = tmp_path / "out"
    config = _config_file(
        tmp_path,
        '{"meeting_reset": "hub_with_grace", "meeting_reset": "preserve"}\n',
    )
    with pytest.raises(SystemExit, match="'meeting_reset' appears more than once"):
        rt.main(_config_args(out, config))
    assert not out.exists()


def test_resume_with_an_edited_config_is_refused_by_the_fingerprint(
    tmp_path: Path,
) -> None:
    out = tmp_path / "out"
    config = _config_file(tmp_path)
    assert rt.main(_config_args(out, config)) == 0
    # Unedited, the saved run resumes (its one seed is already finished).
    assert rt.main(_config_args(out, config, "--resume")) == 0
    config.write_text(
        '{"format_version": 1, "meeting_reset": "hub_with_grace", '
        '"vent_exit_policy": "observed_risk"}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Continuation configuration differs"):
        rt.main(_config_args(out, config, "--resume"))


def test_the_saved_configuration_carries_the_normalized_config(tmp_path: Path) -> None:
    out = tmp_path / "out"
    assert rt.main(_config_args(out, _config_file(tmp_path))) == 0
    saved = json.loads((out / "tournament-progress.json").read_text())
    assert saved["configuration"]["experiment_config"] == _TEST_CONFIG.model_dump(
        mode="json"
    )
    # A config of historical defaults normalizes to none, and records none.
    defaults = tmp_path / "defaults"
    config = tmp_path / "defaults-config.json"
    config.write_text('{"format_version": 1, "meeting_reset": "preserve"}\n')
    assert rt.main(_config_args(defaults, config)) == 0
    saved = json.loads((defaults / "tournament-progress.json").read_text())
    assert saved["configuration"]["experiment_config"] is None
    rows = (defaults / f"replay-seed-{_MEETING_SEED}.jsonl").read_text()
    assert '"experiment_config"' not in rows


@pytest.mark.parametrize("name", sorted(EXPERIMENT_ENV_NAMES))
@pytest.mark.parametrize("value", ["1", "0"])
def test_a_meeting_experiment_export_beside_the_flag_is_refused(
    name: str, value: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(name, value)
    out = tmp_path / "out"
    with pytest.raises(SystemExit, match=f"environment also exports {name}"):
        rt.main(_config_args(out, _config_file(tmp_path)))
    assert not out.exists()


@pytest.mark.parametrize(
    ("flags", "named"),
    [
        (["--agent-factory", "learned-champion"], "--agent-factory learned-champion"),
        (["--agent-factory", "learned-crew"], "--agent-factory learned-crew"),
        (
            ["--candidate-artifact", "training/artifacts/impostor"],
            "--candidate-artifact",
        ),
        (["--crew-artifact", "training/artifacts/crew"], "--crew-artifact"),
    ],
)
def test_an_agent_factory_flag_beside_the_flag_is_refused(
    flags: list[str], named: str, tmp_path: Path
) -> None:
    out = tmp_path / "out"
    with pytest.raises(SystemExit, match=f"cannot run beside {named}"):
        rt.main(_config_args(out, _config_file(tmp_path), *flags))
    assert not out.exists()


def test_the_default_agent_factory_flag_is_not_a_factory_flag(tmp_path: Path) -> None:
    out = tmp_path / "out"
    config = _config_file(tmp_path)
    assert rt.main(_config_args(out, config, "--agent-factory", "fsm-default")) == 0


def _capture_eval_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> list[dict[str, object]]:
    captured: list[dict[str, object]] = []

    def spy(**kwargs: Any) -> TournamentReport:
        captured.append(kwargs)
        return _real_run_tournament_eval(**kwargs)

    monkeypatch.setattr(rt, "run_tournament_eval", spy)
    return captured


def test_the_flag_reaches_the_harness_and_its_absence_leaves_every_call_as_before(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _capture_eval_kwargs(monkeypatch)
    assert rt.main(_config_args(tmp_path / "flagged", _config_file(tmp_path))) == 0
    assert (
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path / "bare"),
                "--max-ticks",
                "2",
            ]
        )
        == 0
    )
    flagged, bare = captured
    assert flagged["experiment_config"] == _TEST_CONFIG
    assert "experiment_config" not in bare


# -- the harness: run_tournament_eval(experiment_config=...) -------------------


def test_the_harness_refuses_a_switched_on_config_beside_a_custom_runner(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="custom meeting_runner_factory"):
        _real_run_tournament_eval(
            seeds=[0],
            output_dir=tmp_path,
            meeting_runner_factory=build_default_meeting_runner,
            experiment_config=_TEST_CONFIG,
        )
    assert not any(tmp_path.iterdir())
    # A config of historical defaults records nothing new beside it.
    _real_run_tournament_eval(
        seeds=[0],
        output_dir=tmp_path,
        max_ticks=2,
        meeting_runner_factory=build_default_meeting_runner,
        experiment_config=RecordedExperimentConfig(),
    )


def test_the_harness_threads_the_config_to_the_factory_runner_and_game(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each construction the harness makes receives the declared config."""

    calls: dict[str, list[dict[str, object]]] = {
        "factory": [],
        "runner": [],
        "game": [],
    }
    real_factory = build_default_agent_factory
    real_runner = build_default_meeting_runner
    real_game = HeadlessGame

    def factory(**kwargs: Any) -> Any:
        calls["factory"].append(kwargs)
        return real_factory(**kwargs)

    def runner(**kwargs: Any) -> Any:
        calls["runner"].append(kwargs)
        return real_runner(**kwargs)

    def game(**kwargs: Any) -> Any:
        calls["game"].append(kwargs)
        return real_game(**kwargs)

    monkeypatch.setattr(balance_eval, "build_default_agent_factory", factory)
    monkeypatch.setattr(balance_eval, "build_default_meeting_runner", runner)
    monkeypatch.setattr(balance_eval, "HeadlessGame", game)
    _real_run_tournament_eval(
        seeds=[_MEETING_SEED],
        output_dir=tmp_path / "flagged",
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        experiment_config=_TEST_CONFIG,
    )
    assert calls["factory"] == [{"experiment_config": _TEST_CONFIG}]
    (runner_call,) = calls["runner"]
    assert runner_call["profile"] == profile_from_config(meeting_values(_TEST_CONFIG))
    (game_call,) = calls["game"]
    assert game_call["experiment_config"] == _TEST_CONFIG

    for recorded in calls.values():
        recorded.clear()
    _real_run_tournament_eval(
        seeds=[_MEETING_SEED],
        output_dir=tmp_path / "bare",
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
    )
    assert calls["factory"] == [{}]
    assert set(calls["runner"][0]) == {"budget"}
    assert "experiment_config" not in calls["game"][0]


def test_the_harness_runner_refuses_an_export_beside_the_declared_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The runner is built from the config's profile, not from the shell."""

    monkeypatch.setenv("AILIBI_BOUNDED_REBUTTAL", "1")
    with pytest.raises(ValueError, match="declared meeting profile"):
        _real_run_tournament_eval(
            seeds=[0],
            output_dir=tmp_path,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            experiment_config=RecordedExperimentConfig(meeting_reset="hub_with_grace"),
        )
