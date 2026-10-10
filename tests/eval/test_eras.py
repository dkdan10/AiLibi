"""The era registry (``eval/eras.py``), held to the recorded bytes.

Each committed set's games must fold to one census era key, the sets of one era
id must share it and sets of different ids must not, and every game of an era
with a declared config must have recorded exactly that config. The planted cases
file ``samples/9p2i`` under the wrong era, edit one game's recorded config in a
scratch copy, file two scratch copies that fold to different keys under one era
id, and file two that fold to one key under two ids; each is refused.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

from eval import eras
from eval.gameplay_census import (
    GameplayCensusEraError,
    recorded_game_eras,
    verify_era_registry,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _manifest_writer import parse_manifest  # noqa: E402

#: The sha256 of candidate round 2's declared config (its record, section 1.4).
_ROUND_2_CONFIG_SHA256 = (
    "0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b"
)
#: The sha256 of candidate round 3's declared config (its record, section 1.3).
_ROUND_3_CONFIG_SHA256 = (
    "a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d"
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
        "stage-b-r3",  # was stage-b-r2
    }
    assert eras.era_of("replays/samples/9p2i") == eras.STAGE_B_R3  # was STAGE_B_R2
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
    shown = dict(keys["replays/samples/9p2i"].settings)
    assert shown["kill_cooldown_ticks"] == 6
    assert shown["route_lines_version"] == 1


def test_the_declared_configs_are_round_3s_and_round_2s_bytes() -> None:
    """The shown era reads round 3's file in the set; round 2's moved with its bytes."""

    declared = eras.STAGE_B_R3.declared_config
    assert declared == "replays/samples/9p2i/experiment-config.json"
    data = (_REPO_ROOT / declared).read_bytes()
    assert hashlib.sha256(data).hexdigest() == _ROUND_3_CONFIG_SHA256
    kept = eras.STAGE_B_R2.declared_config
    # was replays/samples/9p2i/experiment-config.json, before round 2's bytes moved
    assert kept == "replays/candidates/stage-b-r2/experiment-config.json"
    data = (_REPO_ROOT / kept).read_bytes()
    assert hashlib.sha256(data).hexdigest() == _ROUND_2_CONFIG_SHA256
    assert eras.BASELINE_9.declared_config is None
    assert eras.STAGE_B_R2 not in eras.ERAS


@pytest.mark.parametrize("entry", eras.COMMITTED_SETS, ids=lambda entry: entry.path)
def test_each_eras_recording_date_is_its_manifests(entry: eras.CommittedSet) -> None:
    rows = parse_manifest(
        (_REPO_ROOT / entry.path / "MANIFEST.md").read_text(encoding="utf-8")
    ).values()
    assert max(row.refreshed_at.strip() for row in rows) == entry.era.recorded_on


def test_each_eras_record_exists() -> None:
    for era in eras.ERAS:
        assert (_REPO_ROOT / era.record).is_file(), era.record


def test_the_module_exports_every_public_name_it_defines() -> None:
    names: set[str] = set()
    for node in ast.parse(Path(eras.__file__).read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    assert set(eras.__all__) == {name for name in names if not name.startswith("_")}


def test_eras_is_the_registrys_eras_oldest_first() -> None:
    assert eras.ERAS == eras.registered_eras()
    # was (BASELINE_9, STAGE_B_R2), before round 3's promotion
    assert eras.registered_eras() == (eras.BASELINE_9, eras.STAGE_B_R3)


#: An era no committed set belongs to, recorded after both committed eras.
_THIRD_ERA = eras.Era(
    id="planted-third",
    record="audits/planted.md",
    recorded_on="2026-10-12",  # was 2026-10-05, before the shown era's 2026-10-09
    declared_config=None,
)


def test_eras_held_to_the_registry_turns_red_on_either_side() -> None:
    """Planted: ERAS without the promoted era, ERAS still naming the era it
    replaced, and a registry naming a third.

    Each way the registry's eras and ERAS differ, so the pin above is red.
    """

    assert (eras.BASELINE_9,) != eras.registered_eras()
    assert (eras.BASELINE_9, eras.STAGE_B_R2) != eras.registered_eras()
    widened = (*eras.COMMITTED_SETS, eras.CommittedSet("replays/x/9p2i", _THIRD_ERA))
    assert eras.ERAS != eras.registered_eras(widened)
    assert eras.registered_eras(widened) == (*eras.ERAS, _THIRD_ERA)


def test_registered_eras_sort_by_date_then_first_appearance() -> None:
    """Planted: a registry listing the newest era first still reads oldest first.

    Two eras of one date keep the order the registry first names them in.
    """

    newest_first = (
        eras.CommittedSet("replays/x/9p2i", _THIRD_ERA),
        *reversed(eras.COMMITTED_SETS),
    )
    assert eras.registered_eras(newest_first) == (*eras.ERAS, _THIRD_ERA)
    same_day = eras.Era("same-day", "audits/planted.md", "2026-09-22", None)
    paired = (
        eras.CommittedSet("replays/y/9p2i", same_day),
        *eras.COMMITTED_SETS,
    )
    assert eras.registered_eras(paired) == (same_day, *eras.ERAS)


def test_two_eras_filed_under_one_id_are_refused() -> None:
    """Planted: a second era spelled with the baseline-9 id but another date."""

    impostor = eras.Era(
        id=eras.BASELINE_9.id,
        record=eras.BASELINE_9.record,
        recorded_on="2026-09-23",
        declared_config=None,
    )
    doubled = (*eras.COMMITTED_SETS, eras.CommittedSet("replays/x/9p2i", impostor))
    with pytest.raises(
        ValueError,
        match="^the era registry files two different eras under the id baseline-9$",
    ):
        eras.registered_eras(doubled)


def test_a_registry_filing_samples_9p2i_under_baseline_9_is_refused() -> None:
    """Planted: the promoted set named baseline-9 folds to a different key."""

    misfiled = tuple(
        eras.CommittedSet(entry.path, eras.BASELINE_9) for entry in eras.COMMITTED_SETS
    )
    with pytest.raises(GameplayCensusEraError, match="replays/samples/9p2i"):
        verify_era_registry(_REPO_ROOT, registry=misfiled)


def test_a_registry_filing_samples_9p2i_under_stage_b_r2_is_refused() -> None:
    """Planted: the promoted set left under the era its bytes replaced.

    Round 2's declared config, read at its candidate copy, is not what round 3's
    games recorded (it lacks the route lines), so the registry is refused naming
    the set and the era.
    """

    stale = tuple(
        eras.CommittedSet(entry.path, eras.STAGE_B_R2)
        if entry.path == "replays/samples/9p2i"
        else entry
        for entry in eras.COMMITTED_SETS
    )
    message = (
        "replays/samples/9p2i: seed 0 recorded settings that differ from the "
        "stage-b-r2 era's declared config"
    )
    with pytest.raises(GameplayCensusEraError, match=re.escape(message)):
        verify_era_registry(_REPO_ROOT, registry=stale)


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


_SCRATCH_REGISTRY = (eras.CommittedSet("replays/samples/9p2i", eras.STAGE_B_R3),)


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


#: Two committed 4p1i games whose recordings hold a meeting, so their MANIFEST
#: rows' prompt stamps are part of each game's key.
_MEETING_SEEDS_4P1I = (1, 2)

#: A second era id for the planted cases, recorded with every switch off.
_TWIN_OF_BASELINE_9 = eras.Era(
    id="baseline-9-twin",
    record=eras.BASELINE_9.record,
    recorded_on=eras.BASELINE_9.recorded_on,
    declared_config=None,
)


def _scratch_4p1i(root: Path, relative: str, *, restamp: bool = False) -> Path:
    """A scratch copy of two 4p1i sample games that held meetings, at ``relative``.

    With ``restamp`` every MANIFEST row's first prompt stamp gains a suffix, so
    the copy's games fold to a different recorded key from the committed set's
    while still agreeing with one another.
    """

    source = _REPO_ROOT / "replays" / "samples" / "4p1i"
    target = root / relative
    target.mkdir(parents=True)
    shutil.copy(source / "MANIFEST.md", target / "MANIFEST.md")
    for seed in _MEETING_SEEDS_4P1I:
        shutil.copy(
            source / f"replay-seed-{seed}.jsonl", target / f"replay-seed-{seed}.jsonl"
        )
    stamps = recorded_game_eras(target)[_MEETING_SEEDS_4P1I[0]].prompt_stamps
    assert stamps is not None
    if restamp:
        manifest = (target / "MANIFEST.md").read_text(encoding="utf-8")
        assert manifest.count(stamps[0]) >= len(_MEETING_SEEDS_4P1I)
        (target / "MANIFEST.md").write_text(
            manifest.replace(stamps[0], f"{stamps[0]}_planted"), encoding="utf-8"
        )
    return target


@pytest.mark.parametrize(
    "era", (eras.BASELINE_9, _TWIN_OF_BASELINE_9), ids=lambda era: era.id
)
def test_two_sets_of_one_era_folding_to_different_keys_are_refused(
    tmp_path: Path, era: eras.Era
) -> None:
    """Planted: one of two switch-off copies restamped, so it folds elsewhere."""

    first = _scratch_4p1i(tmp_path, "replays/scratch/first")
    _scratch_4p1i(tmp_path, "replays/scratch/same")
    moved = _scratch_4p1i(tmp_path, "replays/scratch/moved", restamp=True)
    assert set(recorded_game_eras(moved).values()).isdisjoint(
        recorded_game_eras(first).values()
    )
    same_key = (
        eras.CommittedSet("replays/scratch/first", era),
        eras.CommittedSet("replays/scratch/same", era),
    )
    assert len(set(verify_era_registry(tmp_path, registry=same_key).values())) == 1
    two_keys = (
        eras.CommittedSet("replays/scratch/first", era),
        eras.CommittedSet("replays/scratch/moved", era),
    )
    message = (
        "replays/scratch/moved: its recordings fold to a different era from the "
        f"other {era.id} sets"
    )
    with pytest.raises(GameplayCensusEraError, match=re.escape(message)):
        verify_era_registry(tmp_path, registry=two_keys)


@pytest.mark.parametrize(
    ("kept", "second"),
    (
        (eras.BASELINE_9, _TWIN_OF_BASELINE_9),
        (_TWIN_OF_BASELINE_9, eras.BASELINE_9),
    ),
    ids=("tip-first", "twin-first"),
)
def test_two_era_ids_folding_to_one_key_are_refused(
    tmp_path: Path, kept: eras.Era, second: eras.Era
) -> None:
    """Planted: one recorded key filed under two era ids, in either order."""

    _scratch_4p1i(tmp_path, "replays/scratch/first")
    _scratch_4p1i(tmp_path, "replays/scratch/same")
    _scratch_4p1i(tmp_path, "replays/scratch/moved", restamp=True)
    two_ids_two_keys = (
        eras.CommittedSet("replays/scratch/first", kept),
        eras.CommittedSet("replays/scratch/moved", second),
    )
    keys = verify_era_registry(tmp_path, registry=two_ids_two_keys)
    assert len(set(keys.values())) == 2
    two_ids_one_key = (
        eras.CommittedSet("replays/scratch/first", kept),
        eras.CommittedSet("replays/scratch/same", second),
    )
    message = (
        f"the {kept.id} and {second.id} eras fold to one recorded key; one "
        "recorded era carries one id"
    )
    with pytest.raises(GameplayCensusEraError, match=re.escape(message)):
        verify_era_registry(tmp_path, registry=two_ids_one_key)


def test_a_switch_off_set_filed_under_a_declared_config_is_refused(
    tmp_path: Path,
) -> None:
    """Planted: two switch-off 4p1i games filed under the stage-b-r3 era."""

    _scratch_4p1i(tmp_path, "replays/scratch/first")
    declared = eras.STAGE_B_R3.declared_config  # was STAGE_B_R2's
    assert declared is not None
    (tmp_path / declared).parent.mkdir(parents=True)
    shutil.copy(_REPO_ROOT / declared, tmp_path / declared)
    message = (
        f"replays/scratch/first: seed {_MEETING_SEEDS_4P1I[0]} recorded settings "
        "that differ from the stage-b-r3 era's declared config"
    )
    with pytest.raises(GameplayCensusEraError, match=re.escape(message)):
        verify_era_registry(
            tmp_path,
            registry=(eras.CommittedSet("replays/scratch/first", eras.STAGE_B_R3),),
        )


def test_a_set_whose_games_fold_to_two_keys_is_refused_by_its_path(
    tmp_path: Path,
) -> None:
    """Planted: one game's MANIFEST row restamped inside a switch-off copy."""

    target = _scratch_4p1i(tmp_path, "replays/scratch/first")
    seed = _MEETING_SEEDS_4P1I[-1]
    stamps = recorded_game_eras(target)[seed].prompt_stamps
    assert stamps is not None
    lines = (target / "MANIFEST.md").read_text(encoding="utf-8").splitlines()
    rows = [index for index, line in enumerate(lines) if line.startswith(f"| {seed} |")]
    assert len(rows) == 1
    lines[rows[0]] = lines[rows[0]].replace(stamps[0], f"{stamps[0]}_planted")
    (target / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    games = recorded_game_eras(target)
    assert games[seed] != games[_MEETING_SEEDS_4P1I[0]]
    message = "replays/scratch/first: two eras differ in prompt stamps"
    with pytest.raises(GameplayCensusEraError, match=re.escape(message)):
        verify_era_registry(
            tmp_path,
            registry=(eras.CommittedSet("replays/scratch/first", eras.BASELINE_9),),
        )
