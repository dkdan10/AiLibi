from __future__ import annotations

import json
import shutil
from collections.abc import Iterator, Sequence
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal

import eval.leak_scan as leak_scan
import eval.replay_walk as replay_walk
from engine.world import load_canonical_map
from eval.leak_scan import PacketRecord, assert_no_factory_packet_leaks
from eval.replay_walk import walk_replay
from eval.temporal_entitlement import assert_temporal_batch_entitled

import pytest

from _verify_samples import verify_samples
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    ConfigLayer,
    RecordedExperimentConfig,
    wave_settings,
)
from orchestrator.replay import read_all_entries, recorded_experiment_config
from scan_recording_packets import scan_recording_set
from tests.eval.test_vent_witness_readers import ROSTER, SEED, record_fake_set


@pytest.mark.parametrize("set_name", ["4p1i", "9p2i"])
def test_ml_corpus_exercises_real_observation_channels(set_name: str) -> None:
    result = scan_recording_set(Path("replays/ml_corpus") / set_name)
    assert result.games > 0 and result.packets > result.games
    assert (
        result.vent_views > 0 and result.body_views > 0 and result.moved_player_rows > 0
    )
    if set_name == "9p2i":
        assert result.kill_views > 0 and result.alarm_rows > 0
    assert result.source_fingerprint.startswith("sha256:")


def test_corpus_scan_fails_on_a_missing_witness_producer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("engine.rules._witnesses_in_room", lambda *args, **kwargs: ())
    with pytest.raises(AssertionError, match="witness entitlement"):
        scan_recording_set(Path("replays/ml_corpus/9p2i"))


def test_corpus_scan_rejects_inputs_changed_during_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import scan_recording_packets as scanner

    source = Path("replays/ml_corpus/4p1i")
    destination = tmp_path / "corpus"
    shutil.copytree(source, destination)
    original = assert_no_factory_packet_leaks
    changed = False

    def scan_then_change_roster(records: Sequence[PacketRecord]) -> None:
        nonlocal changed
        original(records)
        if not changed:
            roster = destination / "roster.json"
            roster.write_bytes(roster.read_bytes() + b"\n")
            changed = True

    monkeypatch.setattr(
        scanner, "assert_no_factory_packet_leaks", scan_then_change_roster
    )
    with pytest.raises(ValueError, match="inputs changed during packet census"):
        scanner.scan_recording_set(destination)


def test_corpus_scan_requires_explicit_roster(tmp_path: Path) -> None:
    (tmp_path / "replay-seed-0.jsonl").write_text("{}\n")
    with pytest.raises(ValueError, match="explicit roster"):
        scan_recording_set(tmp_path)


# --------------------------------------------------------------------------- #
# Physical-rule recordings: the scan hands the recorded rule to both oracles   #
# --------------------------------------------------------------------------- #

_FULL_CONFIG_SETTINGS: dict[str, object] = {
    "vent_witness_rule": "physical",
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}
#: The arms that exist today, recorded for real under the full-config copy.
_TODAYS_ARMS = RecordedExperimentConfig(
    meeting_reset="hub_with_grace", bounded_rebuttal_version=1
)


@pytest.fixture(scope="module")
def physical_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return record_fake_set(tmp_path_factory.mktemp("physical") / "9p2i").set_dir


@pytest.fixture(scope="module")
def temporal_physical_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return record_fake_set(
        tmp_path_factory.mktemp("temporal") / "9p2i", temporal=True
    ).set_dir


def _withhold_the_rule(monkeypatch: pytest.MonkeyPatch) -> None:
    """Planted: the one reader returns the default rule for every recording."""

    monkeypatch.setattr(
        leak_scan, "_recorded_vent_witness_rule", lambda _entries: "both_rooms"
    )


def test_a_physical_set_passes_the_scan_with_vent_views(physical_set: Path) -> None:
    result = scan_recording_set(physical_set)
    assert result.games == 1 and result.packets > 0
    assert result.vent_views > 0
    assert result.event_batches == 0


def test_a_physical_set_fails_the_scan_with_the_rule_withheld(
    physical_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _withhold_the_rule(monkeypatch)
    with pytest.raises(AssertionError, match="vent source witness entitlement"):
        scan_recording_set(physical_set)


def test_a_temporal_physical_set_passes_the_scan_with_event_batches(
    temporal_physical_set: Path,
) -> None:
    result = scan_recording_set(temporal_physical_set)
    assert result.games == 1 and result.event_batches > 0
    assert result.vent_views > 0


def test_a_temporal_physical_set_fails_with_the_rule_withheld_from_the_v2_oracle(
    temporal_physical_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: only the temporal oracle is handed the default rule."""

    original = assert_temporal_batch_entitled

    def unthreaded(*args: Any, **kwargs: Any) -> None:
        original(*args, **{**kwargs, "vent_witness_rule": "both_rooms"})

    monkeypatch.setattr(leak_scan, "assert_temporal_batch_entitled", unthreaded)
    with pytest.raises(
        AssertionError, match="v2 missing, extra or incorrectly ordered"
    ):
        scan_recording_set(temporal_physical_set)


# --------------------------------------------------------------------------- #
# The leak-scan-factory profile declares the layers it reads                  #
# --------------------------------------------------------------------------- #


def _open_pending_arms(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}))


@pytest.fixture(scope="module")
def todays_arms_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return record_fake_set(
        tmp_path_factory.mktemp("todays-arms") / "9p2i", config=_TODAYS_ARMS
    ).set_dir


def _replay(set_dir: Path) -> Path:
    (path,) = set_dir.glob(f"replay-seed-{SEED}.jsonl")
    return path


def _full_config_copy(source: Path, destination: Path) -> Path:
    """``source``'s set with every tick row and footer carrying every wave field ON."""

    shutil.copytree(source, destination)
    path = _replay(destination)
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    stamped = 0
    for row in rows:
        if row["kind"] in ("tick", "game_over"):
            row["experiment_config"] = {
                **row["experiment_config"],
                **_FULL_CONFIG_SETTINGS,
            }
            stamped += 1
    assert stamped > 1
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return destination


def test_the_factory_profile_scans_a_full_config_copy_with_every_hash_verified(
    todays_arms_set: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _open_pending_arms(monkeypatch)
    copy = _full_config_copy(todays_arms_set, tmp_path / "full" / "9p2i")
    config = recorded_experiment_config(read_all_entries(_replay(copy)))
    assert config is not None
    assert {
        field: getattr(config, field) for field in _FULL_CONFIG_SETTINGS
    } == _FULL_CONFIG_SETTINGS
    assert (config.meeting_reset, config.bounded_rebuttal_version) == (
        "hub_with_grace",
        1,
    )
    # Every wave setting outside the engine sits in a layer the profile declares.
    assert {
        experiment_config.FIELD_LAYER[field] for field, _value in wave_settings(config)
    } - {"engine"} == leak_scan._FACTORY_WALK_CONFIG.threaded_layers
    # Every recorded hash verifies, and the scan verifies them again first.
    assert verify_samples(copy) == []
    result = scan_recording_set(copy)
    assert result.games == 1 and result.packets > 0


def _spied_walk(monkeypatch: pytest.MonkeyPatch) -> list[object]:
    yielded: list[object] = []
    real = walk_replay

    def spy(*args: Any, **kwargs: Any) -> Iterator[Any]:
        for event in real(*args, **kwargs):
            yielded.append(event)
            yield event

    monkeypatch.setattr(leak_scan, "walk_replay", spy)
    return yielded


def test_the_factory_profile_without_its_layers_refuses_the_full_config_copy(
    todays_arms_set: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Perturbed: the profile's layer declaration removed."""

    _open_pending_arms(monkeypatch)
    copy = _full_config_copy(todays_arms_set, tmp_path / "full" / "9p2i")
    monkeypatch.setattr(
        leak_scan,
        "_FACTORY_WALK_CONFIG",
        replace(leak_scan._FACTORY_WALK_CONFIG, threaded_layers=frozenset()),
    )
    yielded = _spied_walk(monkeypatch)
    with pytest.raises(
        ValueError, match="'leak-scan-factory' does not read the recorded"
    ):
        scan_recording_set(copy)
    assert yielded == []


@pytest.mark.parametrize("layer", ["engine", "format"])
def test_the_factory_profile_refuses_a_stand_in_in_a_layer_it_does_not_declare(
    physical_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    layer: ConfigLayer,
) -> None:
    """Planted: a stand-in field on the config model, in ``layer``.

    The profile declares every layer a profile may declare, so an undeclared
    layer is the engine layer, whose fields the helper threads or refuses, or
    the format layer, which no profile declares.
    """

    assert layer not in leak_scan._FACTORY_WALK_CONFIG.threaded_layers

    class _StandIn(RecordedExperimentConfig):
        stand_in_rule: Literal["old", "new"] = "old"

    def stand_in_config(entries: Any) -> _StandIn:
        recorded = recorded_experiment_config(entries)
        assert recorded is not None
        return _StandIn.model_validate(
            {**recorded.model_dump(), "stand_in_rule": "new"}
        )

    layers = MappingProxyType({**experiment_config.FIELD_LAYER, "stand_in_rule": layer})
    monkeypatch.setattr(experiment_config, "FIELD_LAYER", layers)
    monkeypatch.setattr(replay_walk, "FIELD_LAYER", layers)
    monkeypatch.setattr(replay_walk, "recorded_experiment_config", stand_in_config)
    monkeypatch.setattr(leak_scan, "recorded_experiment_config", stand_in_config)
    yielded = _spied_walk(monkeypatch)
    with pytest.raises(ValueError, match="stand_in_rule='new'"):
        leak_scan._reconstruct_factory_records(
            _replay(physical_set),
            game_map=load_canonical_map(),
            seed=SEED,
            audit_dir=tmp_path,
            **ROSTER,
        )
    assert yielded == []
