"""The committed game-shape profile must match a recomputation from the recordings.

``--check`` runs through ``check_report`` with the two walks served from the
shared cache, as the census's test does. Everything else runs the real
``publish`` / ``check_report`` / ``main`` against a planted copy of the shown
set or a planted page, so the writer's refusals, the stamp and the
write-nothing mode are exercised end to end.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from typing import Any, get_args

import pytest

import publish_game_profile as command
from eval import game_profile as gp
from eval.eras import COMMITTED_SETS, CommittedSet, Era, era_of
from eval.gameplay_census import CensusInputs
from eval.process_scorecard import SetInputs, load_set_inputs
from tests._helpers.committed import (
    SAMPLES_4P1I,
    SAMPLES_9P2I,
    census_inputs,
    repo_root,
)

ROOT = repo_root
SERVED = SAMPLES_9P2I / command.PROFILE_FILENAME


@cache
def _scorecard(set_dir: Path) -> SetInputs:
    return load_set_inputs(set_dir)


def _committed_census(_: Path) -> CensusInputs:
    return census_inputs(SAMPLES_9P2I)


def _committed_scorecard(_: Path) -> SetInputs:
    return _scorecard(SAMPLES_9P2I)


#: The shown set's two walks, whatever directory holds a copy of its bytes.
COMMITTED = command.Loaders(census=_committed_census, scorecard=_committed_scorecard)


def _committed() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(SERVED.read_text(encoding="utf-8"))
    return payload


@pytest.fixture
def planted_root(tmp_path: Path) -> Iterator[Path]:
    """A checkout-shaped copy holding the shown set and the published page."""

    root = tmp_path / "checkout"
    shutil.copytree(SAMPLES_9P2I, root / "replays" / "samples" / "9p2i")
    (root / "docs").mkdir()
    shutil.copyfile(ROOT / command.MARKDOWN_PATH, root / command.MARKDOWN_PATH)
    yield root


def test_the_committed_profile_matches_a_recomputation() -> None:
    assert command.check_report(ROOT, loaders=COMMITTED) == 0, (
        f"the committed profile drifted; re-run `{command.REGENERATE_COMMAND}`"
    )


def test_one_edited_membership_turns_check_red(
    planted_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert command.check_report(planted_root, loaders=COMMITTED) == 0
    served = planted_root / "replays" / "samples" / "9p2i" / command.PROFILE_FILENAME
    payload = json.loads(served.read_text(encoding="utf-8"))
    members = payload["pre_reveal"]["shelves"][0]["members"]
    payload["pre_reveal"]["shelves"][0]["members"] = members[1:]
    served.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    capsys.readouterr()
    assert command.check_report(planted_root, loaders=COMMITTED) == 1
    printed = capsys.readouterr().out
    assert "replays/samples/9p2i/results-game-profile.json is STALE" in printed
    assert command.REGENERATE_COMMAND in printed


def test_an_edited_page_turns_check_red(
    planted_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    page = planted_root / command.MARKDOWN_PATH
    page.write_text(page.read_text(encoding="utf-8") + "\nAn edit.\n", encoding="utf-8")
    assert command.check_report(planted_root, loaders=COMMITTED) == 1
    assert "docs/game-profile.md is STALE" in capsys.readouterr().out


def _never(_: Path) -> Any:
    raise AssertionError("an absent file must be reported before any walk")


@pytest.mark.parametrize("missing", ["served", "page"])
def test_check_reports_an_absent_file_before_computing(
    planted_root: Path, missing: str, capsys: pytest.CaptureFixture[str]
) -> None:
    target = (
        planted_root / "replays" / "samples" / "9p2i" / command.PROFILE_FILENAME
        if missing == "served"
        else planted_root / command.MARKDOWN_PATH
    )
    target.unlink()
    loaders = command.Loaders(census=_never, scorecard=_never)
    assert command.check_report(planted_root, loaders=loaders) == 1
    assert f"no committed profile file at {target}" in capsys.readouterr().out


def test_publish_writes_both_files_and_check_reads_them_green(
    planted_root: Path,
) -> None:
    served = planted_root / "replays" / "samples" / "9p2i" / command.PROFILE_FILENAME
    page = planted_root / command.MARKDOWN_PATH
    served.unlink()
    page.unlink()
    profiles = command.publish(planted_root, loaders=COMMITTED)
    assert [set_path for set_path, _ in profiles] == list(command.PROFILE_SETS)
    assert served.read_text(encoding="utf-8") == SERVED.read_text(encoding="utf-8")
    assert page.read_text(encoding="utf-8") == (ROOT / command.MARKDOWN_PATH).read_text(
        encoding="utf-8"
    )
    assert command.check_report(planted_root, loaders=COMMITTED) == 0


def test_the_served_file_may_alias_no_recording(planted_root: Path) -> None:
    """Planted: the served file is a hard link to a replay."""

    set_dir = planted_root / "replays" / "samples" / "9p2i"
    served = set_dir / command.PROFILE_FILENAME
    served.unlink()
    os.link(set_dir / "replay-seed-0.jsonl", served)
    before = (set_dir / "replay-seed-0.jsonl").read_bytes()
    with pytest.raises(ValueError, match="overlaps a recording output"):
        command.publish(planted_root, loaders=COMMITTED)
    assert (set_dir / "replay-seed-0.jsonl").read_bytes() == before


def test_the_page_may_not_land_under_the_recordings(
    planted_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(command, "MARKDOWN_PATH", Path("replays/game-profile.md"))
    with pytest.raises(ValueError, match="overlaps a recording output"):
        command.publish(planted_root, loaders=COMMITTED)


def test_the_recording_inputs_are_every_set_file_but_the_served_one() -> None:
    inputs = command.recording_inputs(SAMPLES_9P2I)
    names = {path.name for path in inputs}
    assert command.PROFILE_FILENAME not in names
    assert {"MANIFEST.md", "roster.json", "replay-seed-0.jsonl"} <= names
    assert len(inputs) == sum(1 for _ in SAMPLES_9P2I.iterdir()) - 1


def test_set_dir_prints_a_profile_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A copy outside the registry carries no era; every other byte is the set's."""

    copy = tmp_path / "round" / "9p2i"
    shutil.copytree(SAMPLES_9P2I, copy)
    (copy / command.PROFILE_FILENAME).unlink()
    listing = sorted((path.name, path.stat().st_size) for path in copy.iterdir())
    assert command.main(["--set-dir", str(copy), "--json-stdout"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == {**_committed(), "era": None}
    assert (
        sorted((path.name, path.stat().st_size) for path in copy.iterdir()) == listing
    )


def test_a_four_player_set_is_refused_by_name(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert command.main(["--set-dir", str(SAMPLES_4P1I), "--json-stdout"]) == 1
    error = capsys.readouterr().err
    assert (
        f"refused: {SAMPLES_4P1I} holds a 4-player, 1-impostor roster; the game-shape "
        "profile reads 9-player, 2-impostor sets only" in error
    )
    assert not (SAMPLES_4P1I / command.PROFILE_FILENAME).exists()


@pytest.mark.parametrize("impostors", [1, 3])
def test_a_nine_player_set_of_another_impostor_count_is_refused(
    tmp_path: Path, impostors: int
) -> None:
    """Planted: nine players is not enough; the impostor count is read too."""

    (tmp_path / "roster.json").write_text(
        json.dumps(
            {"num_impostors": impostors, "num_players": 9, "tasks_per_crewmate": 2}
        ),
        encoding="utf-8",
    )
    with pytest.raises(
        command.ProfileRefused,
        match=rf"^{re.escape(str(tmp_path))} holds a 9-player, {impostors}-impostor "
        r"roster; the game-shape profile reads 9-player, 2-impostor sets only$",
    ):
        command.require_profile_roster(tmp_path)


def test_set_dir_and_json_stdout_go_together() -> None:
    for argv in (
        ["--set-dir", str(SAMPLES_9P2I)],
        ["--json-stdout"],
        ["--set-dir", str(SAMPLES_9P2I), "--json-stdout", "--check"],
    ):
        with pytest.raises(SystemExit) as refused:
            command.main(argv)
        assert refused.value.code == 2, argv


def test_a_conformance_breach_exits_one_and_names_it(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def breach(*_: Any, **__: Any) -> Any:
        raise gp.GameProfileConformanceError(
            "set samples/9p2i, seed 3, meeting index 1, voter p-4: planted"
        )

    monkeypatch.setattr(command, "compute_profile", breach)
    assert command.main(["--set-dir", str(SAMPLES_9P2I), "--json-stdout"]) == 1
    assert (
        "conformance breach: set samples/9p2i, seed 3, meeting index 1, voter p-4"
        in (capsys.readouterr().err)
    )
    monkeypatch.setattr(command, "check_report", breach)
    assert command.main(["--check"]) == 1
    monkeypatch.setattr(command, "publish", breach)
    assert command.main([]) == 1


def test_main_checks_and_publishes_the_scripts_own_checkout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: list[tuple[str, Path]] = []

    def check(root: Path, **_: Any) -> int:
        seen.append(("check", root))
        return 7

    def publish(root: Path, **_: Any) -> tuple[tuple[str, gp.GameProfile], ...]:
        seen.append(("publish", root))
        return (("replays/samples/9p2i", gp.GameProfile.model_validate(_committed())),)

    monkeypatch.setattr(command, "check_report", check)
    monkeypatch.setattr(command, "publish", publish)
    assert command.main(["--check"]) == 7
    assert command.main([]) == 0
    assert seen == [("check", command._REPO_ROOT), ("publish", command._REPO_ROOT)]
    printed = capsys.readouterr().out
    # was "era stage-b-r2", before round 3's promotion
    assert (
        "Wrote replays/samples/9p2i/results-game-profile.json: 50 games, era "
        f"{era_of('replays/samples/9p2i').id}; role-correctness is reported and "
        "gates nothing." in printed
    )
    assert era_of("replays/samples/9p2i").id == "stage-b-r3"
    assert "Wrote docs/game-profile.md." in printed


def test_the_script_runs_from_any_directory(tmp_path: Path) -> None:
    environment = {
        key: value for key, value in os.environ.items() if key != "PYTHONPATH"
    }
    finished = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "publish_game_profile.py"),
            "--set-dir",
            str(SAMPLES_4P1I),
            "--json-stdout",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert finished.returncode == 1, finished.stderr[-2000:]
    assert "4-player, 1-impostor roster" in finished.stderr
    assert finished.stdout == ""


def test_the_stamp_is_read_before_and_after_the_walk(tmp_path: Path) -> None:
    """Planted: a recording moves while the profile walks the set."""

    copy = tmp_path / "round" / "9p2i"
    shutil.copytree(SAMPLES_9P2I, copy)

    def moving(set_dir: Path) -> CensusInputs:
        manifest = set_dir / "MANIFEST.md"
        manifest.write_text(
            manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8"
        )
        return census_inputs(SAMPLES_9P2I)

    loaders = command.Loaders(census=moving, scorecard=_committed_scorecard)
    with pytest.raises(
        RuntimeError,
        match=rf"^{re.escape(str(copy))}: the recordings changed while the profile "
        r"walked them$",
    ):
        command.compute_profile(copy, loaders=loaders)


def test_the_stamp_reads_the_loaders_manifest_key_and_the_fingerprint() -> None:
    from api.replay_loader import _manifest_git_sha
    from orchestrator.recording_fingerprint import recording_fingerprint

    stamp = command.read_stamp(SAMPLES_9P2I, ROOT)
    assert stamp == gp.ProfileStamp(
        era="stage-b-r3",  # was stage-b-r2
        manifest_key=_manifest_git_sha(SAMPLES_9P2I),
        source_fingerprint=recording_fingerprint(SAMPLES_9P2I),
        seedset="9p2i",
    )
    served = _committed()
    assert (served["era"], served["manifest_key"], served["source_fingerprint"]) == (
        stamp.era,
        stamp.manifest_key,
        stamp.source_fingerprint,
    )
    assert served["rubric_version"] == gp.RUBRIC_VERSION


def test_a_set_with_no_roster_names_no_seedset(tmp_path: Path) -> None:
    shutil.copyfile(
        SAMPLES_9P2I / "replay-seed-0.jsonl", tmp_path / "replay-seed-0.jsonl"
    )
    with pytest.raises(
        command.ProfileRefused,
        match=rf"^{re.escape(str(tmp_path))} has no roster.json to name its seedset$",
    ):
        command.read_stamp(tmp_path, ROOT)


def test_the_era_is_the_registrys(tmp_path: Path) -> None:
    """Sourced: a registry naming another id changes the stamp."""

    assert command.era_id(SAMPLES_9P2I, ROOT) == era_of("replays/samples/9p2i").id
    renamed = tuple(
        CommittedSet(
            entry.path,
            Era(
                "planted-era",
                entry.era.record,
                entry.era.recorded_on,
                entry.era.declared_config,
            ),
        )
        if entry.path == "replays/samples/9p2i"
        else entry
        for entry in COMMITTED_SETS
    )
    assert command.era_id(SAMPLES_9P2I, ROOT, registry=renamed) == "planted-era"
    assert command.era_id(tmp_path, ROOT) is None
    assert command.era_id(ROOT / "replays" / "candidates", ROOT) is None
    # Planted: a registry that no longer files the shown set gives it no era.
    without = tuple(
        entry for entry in COMMITTED_SETS if entry.path != "replays/samples/9p2i"
    )
    assert len(without) == len(COMMITTED_SETS) - 1
    assert command.era_id(SAMPLES_9P2I, ROOT, registry=without) is None


def test_the_profiled_sets_and_their_roster() -> None:
    assert command.PROFILE_SETS == ("replays/samples/9p2i",)
    assert command.PROFILE_ROSTER == (9, 2)
    assert not (SAMPLES_4P1I / command.PROFILE_FILENAME).exists()


def test_an_era_holding_two_sets_is_refused(
    monkeypatch: pytest.MonkeyPatch, planted_root: Path
) -> None:
    monkeypatch.setattr(
        command,
        "sets_in",
        lambda era: ("replays/samples/9p2i", "replays/elsewhere/9p2i"),
    )
    era = era_of("replays/samples/9p2i").id
    with pytest.raises(
        command.ProfileRefused,
        match=rf"^the {re.escape(era)} era holds replays/samples/9p2i, "
        r"replays/elsewhere/9p2i; the leak rule would span them, and the profile "
        r"is computed per set$",
    ):
        command.compute_profiles(planted_root, loaders=COMMITTED)


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------

_PAGE = ROOT / command.MARKDOWN_PATH


def _page() -> str:
    return " ".join(_PAGE.read_text(encoding="utf-8").split())


def test_the_page_states_what_the_profile_is_not() -> None:
    page = _page()
    for sentence in (
        "This is a description of each game, not a score.",
        "It has no score, no rank, no total and no zeroing floor.",
        "Role-correctness is reported here and gates nothing.",
        "no pre-registration, step rule, gate or objective reads it",
        "The four-player set ships no profile",
        "The rule can only hide more; it never selects or orders a game.",
        "carry some information about the ending",
        "so this tripwire is nearly blind",
        "A wrong call on lines the voters held and believed is part of the game",
    ):
        assert sentence in page, sentence
    # Read off the served file (was the literal "1 of this set's 15", round 2's).
    tripwires = _committed()["pre_reveal"]["tripwires"]
    answered = (
        f"Row 3 can answer {tripwires['alibi_flags_evaluable']} of this set's "
        f"{tripwires['alibi_flags']} alibi-class flags"
    )
    assert answered in page


def _seeds(members: list[dict[str, Any]]) -> str:
    return ", ".join(str(member["seed"]) for member in members) or "none"


def _served_lines(served: dict[str, Any]) -> list[str]:
    """The page lines the served file's shelves, classes, tripwires and lean imply.

    Each is built from the served file's own values and the page's words for
    them, so the page is held to the file it ships beside; the values themselves
    are held to the recordings by ``--check``. (On round 2's bytes these read the
    reporter shelf at 14 games, the wrong shelf at 20 with 21 ejections, the
    regroup-kills shelf before the reveal at 6 of 50, the governing reading
    tripping (26, 2), and the task-win lean at 13 games, 1.46 shelves.)
    """

    pre, reveal = served["pre_reveal"], served["reveal"]
    shelves = {shelf["name"]: shelf for shelf in pre["shelves"]}
    reporter = shelves[gp.REPORTER_SAW_IT]
    wrong = reveal["decided_without_proof"]["wrong"]
    tables = {table["name"]: table for table in reveal["class_tables"]}
    lines = [
        f"| {command.NAMES[gp.REPORTER_SAW_IT]} | {len(reporter['members'])} | "
        f"{_seeds(reporter['members'])} |",
        f"| {command.NAMES[gp.WRONG_ON_WHAT_IT_HELD]} | {len(wrong['members'])} "
        f"({sum(len(m['meetings']) for m in wrong['members'])} ejections) | "
        f"{_seeds(wrong['members'])} |",
    ]
    for name, fact in (
        (gp.TWO_KILLS_AFTER_ONE_REGROUP, gp.ANY_EJECTION),
        (gp.CAUGHT_VENTING, "CREWMATE_EJECT"),
        (gp.STRUCK_AFTER_THE_REGROUP, "IMPOSTOR_PARITY"),
    ):
        table = tables[name]
        (row,) = [row for row in table["rows"] if row["fact"] == fact]
        lines.append(
            f"| {command.NAMES[name]} | {table['members']} of {table['games']} | "
            f"{command.NAMES.get(fact, fact)} | {row['a']}, {row['b']}, {row['c']}, "
            f"{row['d']} | {command._p_text(row['p'])} | "
            f"{command.CLASS_WORDS[table['classification']]} |"
        )
    for reading in pre["tripwires"]["readings"]:
        entries = ", ".join(
            f"({e['seed']}, {e['meeting']})" for e in reading["entries"]
        )
        games = len({entry["seed"] for entry in reading["entries"]})
        lines.append(
            f"| {command.READING_WORDS[reading['name']]} | {len(reading['entries'])} "
            f"| {games} | {entries or 'none'} |"
        )
    endings = {game["seed"]: game["ending"] for game in reveal["games"]}
    tasks = [
        sum(
            1
            for shelf in pre["shelves"]
            if any(member["seed"] == game["seed"] for member in shelf["members"])
        )
        for game in pre["games"]
        if not game["tripped"] and endings[game["seed"]] == "CREWMATE_TASKS"
    ]
    lines.append(f"| `CREWMATE_TASKS` | {len(tasks)} | {sum(tasks) / len(tasks):.2f} |")
    return lines


def test_the_page_states_the_stamps_the_shelves_and_the_classes() -> None:
    page = _PAGE.read_text(encoding="utf-8")
    served = _committed()
    for line in (
        f"* rubric version: {served['rubric_version']}",
        f"* era: `{served['era']}`",
        f"* MANIFEST key: `{served['manifest_key']}`",
        f"* source fingerprint: `{served['source_fingerprint']}`",
        *_served_lines(served),
    ):
        assert line in page.splitlines(), line
    assert f"at least {gp.SLOW_BURN_TICKS} ticks" in page
    assert f"Any p below {gp.profile_constants().leak_p_level}" in " ".join(
        page.split()
    )


#: What naming a line, or relating one rate to another, reads like.
_RESTATEMENTS = (
    re.compile(r"\bbars?\b", re.IGNORECASE),
    re.compile(r"\bratios?\b", re.IGNORECASE),
    re.compile(r"\brelative risk\b", re.IGNORECASE),
    re.compile(r"\btimes (?:as|more|less) likely\b", re.IGNORECASE),
    re.compile(
        r"\brates?\b[^.|\n]*\b(?:divided by|over|against)\b[^.|\n]*\brates?\b",
        re.IGNORECASE,
    ),
)


def restatements(text: str) -> list[str]:
    return sorted(
        {match.group(0) for shape in _RESTATEMENTS for match in shape.finditer(text)}
    )


_ID_SHAPES = (
    re.compile(r"\b[A-Z]\d{1,2}\b"),
    re.compile(r"\b(?:Task|Phase|PR) #?\d"),
    re.compile(r"\baudit-\d{4}"),
    re.compile(r"§"),
    re.compile(r"[<>≤≥]=?\s*\d"),
)


def id_shapes(text: str) -> list[str]:
    return sorted(
        {match.group(0) for shape in _ID_SHAPES for match in shape.finditer(text)}
    )


def test_the_page_names_no_line_relates_no_two_rates_and_carries_no_id() -> None:
    page = _PAGE.read_text(encoding="utf-8")
    assert restatements(page) == []
    assert id_shapes(page) == []


def test_a_page_naming_a_bar_or_a_ratio_fails_the_scan() -> None:
    for planted, found in (
        ("A shelf of 14 clears the bar a round must reach.", ["bar"]),
        ("The ratio of the two shelves is 2.", ["ratio"]),
        (
            "The ejection rate over the skip rate reads 0.4.",
            ["rate over the skip rate"],
        ),
    ):
        assert restatements(planted) == found, planted
    assert id_shapes("see Task 13.8 and T1") == ["T1", "Task 1"]


def test_the_page_names_every_shelf_and_reading() -> None:
    for name in (
        *gp.CANDIDATES,
        *(name for name, _ in gp.REVEAL_SHELVES),
        gp.EYEWITNESS_CHIP,
    ):
        assert name in command.NAMES, name
    for reading, _, _ in gp.TRIPWIRE_READINGS:
        assert reading in command.READING_WORDS, reading
    assert set(command.CLASS_WORDS) == set(get_args(gp.Classification))
