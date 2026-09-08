"""Version-3 walks reproduce real policies and own temporary audit lifetime."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import NoReturn, cast

import pytest

import eval.replay_walk as replay_walk
from engine.world import load_canonical_map
from eval.replay_walk import ReplayWalkConfig, ReplayWalkEvent, WalkViolation
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import HeadlessGame, build_default_agent_factory
from orchestrator.replay import substrate_flag_snapshot
from orchestrator.scheduler import TickScheduler


def _reject(violation: WalkViolation) -> NoReturn:
    raise ValueError(violation.kind)


def _walk(path: Path) -> Generator[ReplayWalkEvent, None, None]:
    return cast(
        Generator[ReplayWalkEvent, None, None],
        replay_walk.walk_replay(
            path,
            seed=1,
            num_players=7,
            num_impostors=1,
            tasks_per_crewmate=1,
            game_map=load_canonical_map(),
            config=ReplayWalkConfig(
                profile="v3-policy-test",
                on_violation=_reject,
                supports_temporal_observations=True,
                supports_experiments=True,
                reconstruct_v3_policies=True,
            ),
        ),
    )


def _record(path: Path) -> Path:
    experiment = RecordedExperimentConfig(
        format_version=3, evidence_reasoning_version=2, investigation_version=1
    )
    path.mkdir()
    flags = {**substrate_flag_snapshot(), "temporal_observations": True}
    HeadlessGame(
        seed=1,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=experiment),
        experiment_config=experiment,
        replay_path=path / "replay-seed-1.jsonl",
        scheduler=TickScheduler(max_ticks=3),
        substrate_flags=flags,
        temporal_observation_version=2,
    ).run()
    return path / "replay-seed-1.jsonl"


def test_genuine_partial_v3_policy_reconstructs_and_action_drift_is_refused(
    tmp_path: Path,
) -> None:
    path = _record(tmp_path / "genuine")
    assert isinstance(list(_walk(path))[-1], replay_walk.WalkComplete)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    first = next(row for row in rows if row["kind"] == "tick")
    first["actions"][0] = {
        "type": "wait",
        "actor": first["actions"][0]["actor"],
        "payload": {},
    }
    changed = tmp_path / "changed.jsonl"
    changed.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    # This profile deliberately has no state-hash check. The refusal must come
    # from actual policy intent reproduction, including on a partial recording,
    # and it arrives through the profile's own hook as a coded violation.
    with pytest.raises(ValueError, match="v3_policy_mismatch"):
        list(_walk(changed))


def test_the_v3_reconstruction_is_a_profile_option_not_a_core_check(
    tmp_path: Path,
) -> None:
    """A profile that declares no checks must not acquire this one (NC3-1).

    ``eval/replay_walk``'s contract is that every check the walker performs is a
    profile-declared option; ``leak-scan-factory`` declares none and its only
    policy is ``KeyError(tick)``. The re-decision ran for it anyway, raising a
    bare ``ValueError`` its ``on_violation`` never saw — so the profile silently
    lost its declared refusal and paid for a per-agent per-tick policy replay it
    never asked for.
    """

    clean = _record(tmp_path / "genuine")
    rows = [json.loads(line) for line in clean.read_text().splitlines()]
    first = next(row for row in rows if row["kind"] == "tick")
    first["actions"][0] = {
        "type": "wait",
        "actor": first["actions"][0]["actor"],
        "payload": {},
    }
    changed = tmp_path / "changed.jsonl"
    changed.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    calls: list[str] = []

    def record_then_raise(violation: WalkViolation) -> NoReturn:
        calls.append(violation.kind)
        raise KeyError(violation.tick)

    def walk(path: Path, *, reconstruct: bool) -> None:
        # Byte-equal to eval/leak_scan.py's declared no-check profile apart from
        # the option under test.
        list(
            replay_walk.walk_replay(
                path,
                seed=1,
                num_players=7,
                num_impostors=1,
                tasks_per_crewmate=1,
                game_map=load_canonical_map(),
                config=ReplayWalkConfig(
                    profile="leak-scan-factory",
                    on_violation=record_then_raise,
                    missing_meeting_row="violation",
                    supports_temporal_observations=True,
                    supports_experiments=True,
                    reconstruct_v3_policies=reconstruct,
                ),
            )
        )

    # Default OFF: the tampered actions are simply not re-decided.
    walk(changed, reconstruct=False)
    assert calls == []

    # Opted in: the profile's OWN policy decides, on a coded violation kind.
    with pytest.raises(KeyError):
        walk(changed, reconstruct=True)
    assert calls == ["v3_policy_mismatch"]


@pytest.mark.parametrize("exit_mode", ["close", "throw", "complete"])
def test_temporary_audit_is_cleaned_on_every_generator_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exit_mode: str
) -> None:
    path = _record(tmp_path / "genuine")
    directories: list[Path] = []

    def tracked_directory(*, prefix: str) -> TemporaryDirectory[str]:
        directory = TemporaryDirectory(prefix=prefix, dir=tmp_path)
        directories.append(Path(directory.name))
        return directory

    monkeypatch.setattr(replay_walk, "TemporaryDirectory", tracked_directory)
    iterator = _walk(path)
    next(iterator)
    assert len(directories) == 1 and directories[0].exists()
    if exit_mode == "close":
        iterator.close()
    elif exit_mode == "throw":
        with pytest.raises(RuntimeError, match="consumer stopped"):
            iterator.throw(RuntimeError("consumer stopped"))
    else:
        list(iterator)
    assert not directories[0].exists()
