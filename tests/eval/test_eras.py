"""The era registry (``eval/eras.py``), held to the recorded bytes.

Each committed set's games must fold to one census era key, the sets of one era
id must share it and sets of different ids must not, and every game of an era
with a declared config must have recorded exactly that config. The planted cases
file ``samples/9p2i`` under the wrong era and edit one game's recorded config in
a scratch copy; both are refused.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from eval import eras
from eval.gameplay_census import (
    GameplayCensusEraError,
    recorded_game_eras,
    verify_era_registry,
)
from scripts._manifest_writer import parse_manifest

_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The sha256 of candidate round 2's declared config (its record, section 1.4).
_ROUND_2_CONFIG_SHA256 = (
    "0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b"
)


def test_the_registry_names_each_committed_set_once_and_two_eras() -> None:
    paths = [entry.path for entry in eras.COMMITTED_SETS]
    assert paths == [
        "replays/ml_corpus/9p2i",
        "replays/samples/9p2i",
        "replays/ml_corpus/4p1i",
        "replays/samples/4p1i",
    ]
    assert {entry.era.id for entry in eras.COMMITTED_SETS} == {
        "baseline-9",
        "stage-b-r2",
    }
    assert eras.era_of("replays/samples/9p2i") == eras.STAGE_B_R2
    assert eras.sets_in(eras.BASELINE_9) == (
        "replays/ml_corpus/9p2i",
        "replays/ml_corpus/4p1i",
        "replays/samples/4p1i",
    )
    assert eras.LADDER_TIP_ERA == eras.BASELINE_9
    with pytest.raises(ValueError, match="not a committed set"):
        eras.era_of("replays/candidates/stage-b-r1/9p2i")


def test_the_registry_holds_on_the_committed_bytes() -> None:
    keys = verify_era_registry(_REPO_ROOT)
    assert set(keys) == {entry.path for entry in eras.COMMITTED_SETS}
    baseline_9 = {keys[path] for path in eras.sets_in(eras.BASELINE_9)}
    assert len(baseline_9) == 1
    assert keys["replays/samples/9p2i"] not in baseline_9
    assert next(iter(baseline_9)).settings == ()
    assert dict(keys["replays/samples/9p2i"].settings)["kill_cooldown_ticks"] == 6


def test_the_declared_config_is_round_2s_bytes() -> None:
    declared = eras.STAGE_B_R2.declared_config
    assert declared == "replays/samples/9p2i/experiment-config.json"
    data = (_REPO_ROOT / declared).read_bytes()
    assert hashlib.sha256(data).hexdigest() == _ROUND_2_CONFIG_SHA256
    assert eras.BASELINE_9.declared_config is None


@pytest.mark.parametrize("entry", eras.COMMITTED_SETS, ids=lambda entry: entry.path)
def test_each_eras_recording_date_is_its_manifests(entry: eras.CommittedSet) -> None:
    rows = parse_manifest(
        (_REPO_ROOT / entry.path / "MANIFEST.md").read_text(encoding="utf-8")
    ).values()
    assert max(row.refreshed_at.strip() for row in rows) == entry.era.recorded_on


def test_each_eras_record_exists() -> None:
    for era in eras.ERAS:
        assert (_REPO_ROOT / era.record).is_file(), era.record


def test_a_registry_filing_samples_9p2i_under_baseline_9_is_refused() -> None:
    """Planted: the promoted set named baseline-9 folds to a different key."""

    misfiled = tuple(
        eras.CommittedSet(entry.path, eras.BASELINE_9) for entry in eras.COMMITTED_SETS
    )
    with pytest.raises(GameplayCensusEraError, match="replays/samples/9p2i"):
        verify_era_registry(_REPO_ROOT, registry=misfiled)


def _scratch_set(tmp_path: Path, seeds: tuple[int, ...]) -> Path:
    """A scratch root holding a few of the promoted set's games and its files."""

    source = _REPO_ROOT / "replays" / "samples" / "9p2i"
    target = tmp_path / "replays" / "samples" / "9p2i"
    target.mkdir(parents=True)
    for name in ("MANIFEST.md", "roster.json", "experiment-config.json"):
        shutil.copy(source / name, target / name)
    for seed in seeds:
        shutil.copy(
            source / f"replay-seed-{seed}.jsonl", target / f"replay-seed-{seed}.jsonl"
        )
    return target


_SCRATCH_REGISTRY = (eras.CommittedSet("replays/samples/9p2i", eras.STAGE_B_R2),)


def test_a_scratch_copy_of_the_promoted_games_passes(tmp_path: Path) -> None:
    _scratch_set(tmp_path, (0, 1))
    keys = verify_era_registry(tmp_path, registry=_SCRATCH_REGISTRY)
    assert len(keys) == 1


def test_one_games_edited_config_is_refused(tmp_path: Path) -> None:
    """Planted: one game's recorded cooldown edited on every row it carries."""

    target = _scratch_set(tmp_path, (0, 1))
    replay = target / "replay-seed-1.jsonl"
    rows = [json.loads(line) for line in replay.read_text().splitlines() if line]
    edited = 0
    for row in rows:
        config = row.get("experiment_config")
        if isinstance(config, dict) and config.get("kill_cooldown_ticks") == 6:
            config["kill_cooldown_ticks"] = 5
            edited += 1
    assert edited > 0
    replay.write_text("".join(json.dumps(row) + "\n" for row in rows))
    assert recorded_game_eras(target)[1] != recorded_game_eras(target)[0]
    with pytest.raises(GameplayCensusEraError, match="replays/samples/9p2i"):
        verify_era_registry(tmp_path, registry=_SCRATCH_REGISTRY)


def test_a_declared_config_no_game_recorded_is_refused(tmp_path: Path) -> None:
    """Planted: the era's declared file edited away from what every game recorded."""

    target = _scratch_set(tmp_path, (0,))
    declared = json.loads((target / "experiment-config.json").read_text())
    declared["kill_cooldown_ticks"] = 5
    (target / "experiment-config.json").write_text(json.dumps(declared) + "\n")
    with pytest.raises(GameplayCensusEraError, match="seed 0 recorded settings"):
        verify_era_registry(tmp_path, registry=_SCRATCH_REGISTRY)
