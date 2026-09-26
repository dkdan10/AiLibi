"""The committed gameplay census must match a recomputation from the recordings.

``--check`` is exercised through ``check_report`` as the scorecard's test does,
with the walk served from ``tests/_helpers/committed.py`` so the four sets are
walked once per worker. Everything else here runs the real ``publish`` /
``check_report`` / ``main`` against a planted census or a planted copy of one
set, so the writer's refusals and the write-nothing mode are exercised end to end.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest

import publish_gameplay_census as command
from _manifest_writer import parse_manifest
from _report_output import _check_destination
from eval import gameplay_census as census
from eval.gameplay_census import (
    CensusCell,
    CensusInputs,
    EraKey,
    GameFacts,
    GameplayCensus,
    MeetingFact,
    census_from_inputs,
)
from eval.process_scorecard import RECORDINGS_ROOT
from tests._helpers.committed import (
    COMMITTED_SETS,
    SAMPLES_4P1I,
    SAMPLES_9P2I,
    census_inputs,
    repo_root,
)

ROOT = repo_root


def _committed() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(
        (ROOT / command.JSON_PATH).read_text(encoding="utf-8")
    )
    return payload


def _section(label: str) -> dict[str, Any]:
    return next(item for item in _committed()["sets"] if item["label"] == label)


def test_the_committed_census_matches_a_recomputation(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The gate: both published files are what the recordings say they are."""

    assert command.check_report(ROOT, load=census_inputs) == 0, (
        "docs/gameplay-census.md / .json are STALE: re-run "
        f"`{command.REGENERATE_COMMAND}` and commit the result."
    )
    assert "are consistent with the committed recordings" in capsys.readouterr().out


def test_set_dir_prints_the_committed_section_of_that_set() -> None:
    printed = json.loads(command.set_dir_json(SAMPLES_9P2I, load=census_inputs))
    assert printed == _section("samples/9p2i")


PLANTED_ERA = EraKey(
    settings=(),
    temporal_observation_version=None,
    substrate_flags=(("absence_prior", True), ("reporter_reasoning", False)),
    prompt_stamps=("vote_ballot.qwen3_6_27b.v8",),
)


def _planted_inputs(
    *meetings: MeetingFact,
    era: EraKey = PLANTED_ERA,
    label: str = "samples/9p2i",
    rows_without_dispositions: int = 1,
    discarded: tuple[str, ...] = ("move",),
) -> CensusInputs:
    game = GameFacts(
        seed=7,
        roles=MappingProxyType({"p-0": "IMPOSTOR", "p-1": "CREWMATE"}),
        era=era,
        kills=(),
        vents=(),
        bodies=(),
        frames=MappingProxyType({}),
        meetings=meetings,
        discarded=tuple(census.DiscardedAction(5, kind) for kind in discarded),
        rows_without_dispositions=rows_without_dispositions,
        winner="IMPOSTORS",
        terminal_tick=5,
    )
    return CensusInputs(
        label=label,
        source=f"replays/{label}",
        era=game.era,
        kill_cooldown_ticks=4,
        neighbours=MappingProxyType({}),
        games=(game,),
    )


def _planted() -> GameplayCensus:
    return census_from_inputs([_planted_inputs()])


def test_one_edited_cell_turns_check_red(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Publish, verify green, move ONE integer, and watch the gate go red."""

    planted = _planted()
    received: list[Path] = []

    def computed(tree: Path, load: Any) -> GameplayCensus:
        received.append(tree)
        return planted

    monkeypatch.setattr(command, "compute_gameplay_census", computed)
    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    command.publish(root)
    assert command.check_report(root) == 0
    assert capsys.readouterr().out == (
        f"--check: {command.MARKDOWN_PATH} and {command.JSON_PATH} are consistent "
        "with the committed recordings.\n"
    )

    published = root / command.JSON_PATH
    original = published.read_text(encoding="utf-8")
    payload = json.loads(original)
    payload["pooled"]["cells"]["impostor_wins"]["numerator"] -= 1
    published.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    assert command.check_report(root) == 1
    message = capsys.readouterr().out
    assert str(command.JSON_PATH) in message
    assert command.REGENERATE_COMMAND in message
    assert message == _stale_message(command.JSON_PATH)

    published.write_text(original, encoding="utf-8")
    page = root / command.MARKDOWN_PATH
    page.write_text(page.read_text(encoding="utf-8") + "edited\n", encoding="utf-8")
    assert command.check_report(root) == 1
    message = capsys.readouterr().out
    assert str(command.MARKDOWN_PATH) in message
    assert message == _stale_message(command.MARKDOWN_PATH)
    assert received == [root, root, root, root]


def _stale_message(stale: Path) -> str:
    """The whole of ``--check``'s report when ``stale`` alone has drifted."""

    return (
        f"--check: {stale} is STALE: it does not match a recomputation from the "
        f"committed recordings. Re-run `{command.REGENERATE_COMMAND}` and commit "
        "the result.\n"
    )


@pytest.mark.parametrize("missing", (command.JSON_PATH, command.MARKDOWN_PATH))
def test_a_missing_published_file_is_red(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    missing: Path,
) -> None:
    planted = _planted()
    monkeypatch.setattr(command, "compute_gameplay_census", lambda _root, load: planted)
    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    command.publish(root)
    (root / missing).unlink()
    assert command.check_report(root) == 1
    assert f"no committed census at {root / missing}" in capsys.readouterr().out


def test_check_reports_an_absent_census_before_computing_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    computed: list[Path] = []

    def computing(root: Path, load: Any) -> GameplayCensus:
        computed.append(root)
        return _planted()

    monkeypatch.setattr(command, "compute_gameplay_census", computing)
    assert command.check_report(tmp_path) == 1
    assert computed == []
    assert capsys.readouterr().out == (
        f"--check: no committed census at {tmp_path / command.MARKDOWN_PATH}\n"
    )


@pytest.mark.parametrize("destination", ("MARKDOWN_PATH", "JSON_PATH"))
@pytest.mark.parametrize(
    "relative",
    (
        "replays/samples/4p1i/replay-seed-0.jsonl",
        "replays/samples/9p2i/roster.json",
        "replays/ml_corpus/9p2i/MANIFEST.md",
        "replays/new-gameplay-census.md",
        "replays/samples/9p2i/new-census.md",
        "replays/candidates/stage-b-r1/9p2i/census.md",
    ),
)
def test_the_writer_refuses_a_recording_destination_before_computing(
    monkeypatch: pytest.MonkeyPatch, relative: str, destination: str
) -> None:
    source = ROOT / relative
    before = source.read_bytes() if source.exists() else None

    def forbidden(_root: Path, load: Any) -> Any:
        raise AssertionError("the fold must not start for an invalid destination")

    monkeypatch.setattr(command, "compute_gameplay_census", forbidden)
    monkeypatch.setattr(command, destination, Path(relative))
    with pytest.raises(ValueError, match="overlaps") as refused:
        command.publish(ROOT)
    # The refusal names the destination under the tree it was given and the
    # recording root that contains it.
    assert str(refused.value) == (
        "Report destination overlaps a recording output: "
        f"{ROOT / relative} and {ROOT / RECORDINGS_ROOT}"
    )
    if before is None:
        assert not source.exists(), "the refusal must leave nothing behind"
    else:
        assert source.read_bytes() == before


def test_the_recording_roots_are_protected_by_containment() -> None:
    """The perturbation: strip the roots and the same destination is ACCEPTED."""

    protected = command.protected_inputs(ROOT)
    roots = {path.resolve() for path in protected if path.is_dir()}
    assert roots == {(ROOT / RECORDINGS_ROOT).resolve()}
    destination = ROOT / RECORDINGS_ROOT / "samples" / "9p2i" / "new-census.md"
    assert not destination.exists()
    files_only = [path for path in protected if path.is_file()]
    _check_destination(destination, files_only)
    with pytest.raises(ValueError, match="overlaps"):
        _check_destination(destination, protected)


def test_every_census_input_lies_under_the_protected_root() -> None:
    protected = command.protected_inputs(ROOT)
    for name in census.CENSUS_SETS:
        for relative in ("MANIFEST.md", "replay-seed-new.jsonl"):
            with pytest.raises(ValueError, match="overlaps"):
                _check_destination(ROOT / name / relative, protected)


def test_a_hard_link_to_a_recording_is_refused_by_file_identity(
    tmp_path: Path,
) -> None:
    """The perturbation: without the file entries the same alias is ACCEPTED."""

    recording = SAMPLES_4P1I / "replay-seed-0.jsonl"
    alias = tmp_path / "gameplay-census.md"
    os.link(recording, alias)
    protected = command.protected_inputs(ROOT)
    roots_only = [path for path in protected if path.is_dir()]
    _check_destination(alias, roots_only)
    with pytest.raises(ValueError, match="overlaps"):
        _check_destination(alias, protected)


def test_the_script_runs_from_any_directory_and_exits_with_mains_code(
    tmp_path: Path,
) -> None:
    """Run as a program from outside the tree: the path bootstrap and exit code."""

    copy = tmp_path / "samples" / "4p1i"
    shutil.copytree(SAMPLES_4P1I, copy)
    environment = {
        key: value for key, value in os.environ.items() if key != "PYTHONPATH"
    }
    script = ROOT / "scripts" / "publish_gameplay_census.py"
    finished = subprocess.run(
        [sys.executable, str(script), "--set-dir", str(copy), "--json-stdout"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert finished.returncode == 0, finished.stderr[-2000:]
    assert json.loads(finished.stdout) == _section("samples/4p1i")
    refused = subprocess.run(
        [sys.executable, str(script), "--set-dir", str(copy)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert refused.returncode == 2


def _listing(directory: Path) -> list[tuple[str, int]]:
    return sorted(
        (path.relative_to(directory).as_posix(), path.stat().st_size)
        for path in directory.rglob("*")
    )


def test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    copy = tmp_path / "samples" / "4p1i"
    shutil.copytree(SAMPLES_4P1I, copy)
    before = _listing(tmp_path)
    published = [
        (ROOT / path).read_bytes()
        for path in (command.MARKDOWN_PATH, command.JSON_PATH)
    ]

    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("--set-dir must write nothing")

    monkeypatch.setattr(command, "atomic_write_report", forbidden)
    monkeypatch.setattr(command, "preflight_report_output", forbidden)
    assert command.main(["--set-dir", str(copy), "--json-stdout"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed == _section("samples/4p1i")
    assert _listing(tmp_path) == before
    assert [
        (ROOT / path).read_bytes()
        for path in (command.MARKDOWN_PATH, command.JSON_PATH)
    ] == published


def test_set_dir_exits_non_zero_on_a_conformance_breach(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tests.eval.test_gameplay_census import _impostor_opener, inputs

    breaching = inputs(_impostor_opener({}))
    monkeypatch.setattr(command, "load_census_inputs", lambda _path: breaching)
    assert command.main(["--set-dir", "anywhere", "--json-stdout"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "conformance breach" in captured.err
    assert "set planted/set, seed 7, meeting meeting-0" in captured.err


@pytest.mark.parametrize(
    "argv",
    (
        ["--set-dir", "anywhere"],
        ["--json-stdout"],
        ["--check", "--set-dir", "anywhere", "--json-stdout"],
    ),
)
def test_set_dir_and_json_stdout_go_together(
    argv: Sequence[str], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as exited:
        command.main(list(argv))
    assert exited.value.code == 2
    assert "--set-dir and --json-stdout go together, without --check" in (
        capsys.readouterr().err
    )


def test_set_dir_lets_a_failure_other_than_a_breach_propagate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing(_path: Path) -> CensusInputs:
        raise RuntimeError("not a breach")

    monkeypatch.setattr(command, "load_census_inputs", failing)
    with pytest.raises(RuntimeError, match="^not a breach$"):
        command.main(["--set-dir", "anywhere", "--json-stdout"])


def test_main_publishes_and_checks_the_tree_it_is_given(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    planted = _planted()
    received: list[Path] = []

    def computed(tree: Path, load: Any) -> GameplayCensus:
        received.append(tree)
        return planted

    monkeypatch.setattr(command, "compute_gameplay_census", computed)
    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    monkeypatch.setattr(command, "_REPO_ROOT", root)
    assert command.main([]) == 0
    printed = capsys.readouterr().out
    assert "1 games" in printed
    assert printed == (
        f"Wrote {command.MARKDOWN_PATH} and {command.JSON_PATH}: 1 games, "
        f"{planted.pooled.meetings} meetings; role-correctness is reported and "
        "gates nothing.\n"
    )
    assert (root / command.JSON_PATH).read_text(
        encoding="utf-8"
    ) == census.serialize_json(planted)
    assert command.main(["--check"]) == 0
    # --check checks: a drifted file stays as it is and the exit is 1.
    drifted = (root / command.JSON_PATH).read_text(encoding="utf-8") + "\n"
    (root / command.JSON_PATH).write_text(drifted, encoding="utf-8")
    assert command.main(["--check"]) == 1
    assert (root / command.JSON_PATH).read_text(encoding="utf-8") == drifted
    assert received == [root, root, root]


def test_help_prints_the_commands_own_description(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exited:
        command.main(["--help"])
    assert exited.value.code == 0
    printed = " ".join(capsys.readouterr().out.split())
    assert "Publish the gameplay census over the committed recordings." in printed
    for option, meaning in (
        (
            "--check",
            "Recompute both files and diff against the committed ones; exit 1 on "
            "drift.",
        ),
        (
            "--set-dir SET_DIR",
            "Fold one replay directory instead of the committed sets.",
        ),
        (
            "--json-stdout",
            "With --set-dir: print that directory's section as JSON; write nothing.",
        ),
    ):
        assert f"{option} {meaning}" in printed, option
    assert (
        printed.index("--check Recompute")
        < printed.index("--set-dir SET_DIR Fold")
        < printed.index("--json-stdout With")
    )


def test_the_protected_root_is_the_recordings_root_the_scorecard_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the recording root moves, and the protected list follows it."""

    (tmp_path / "elsewhere" / "set").mkdir(parents=True)
    recording = tmp_path / "elsewhere" / "set" / "replay-seed-0.jsonl"
    recording.write_text("", encoding="utf-8")
    monkeypatch.setattr(command, "RECORDINGS_ROOT", "elsewhere")
    assert command.protected_inputs(tmp_path) == [tmp_path / "elsewhere", recording]


# --------------------------------------------------------------------------- #
# The page's copy                                                              #
# --------------------------------------------------------------------------- #

#: The id shapes a published title or key must never carry: memo cell and
#: ruling numbers and wave letters (C12, R7, B1), task, phase, pull-request and
#: audit ids, section marks, and threshold arithmetic.
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


def test_the_page_says_what_it_is_not_and_defines_its_terms() -> None:
    page = (ROOT / command.MARKDOWN_PATH).read_text(encoding="utf-8")
    opening = page.split("## The counts", 1)[0]
    assert page.startswith(
        "# The gameplay census\n\n**This is not the process scorecard."
    )
    assert census.ROLE_CORRECTNESS_NOTE in opening
    for term in (
        "vent band",
        "era",
        "regroup",
        "opener",
        "trigger tick",
        "by construction",
    ):
        assert f"* **{term}**:" in opening, term
    assert id_shapes(page) == []


def test_a_title_carrying_a_memo_style_id_fails_the_copy_scan() -> None:
    for planted in (
        "| C12 vent-proof meetings |",
        "| B1 surfacings |",
        "Task 13.8 cap",
        "see audit-2026-09-22",
        "effective when the share is <= 0.30",
    ):
        assert id_shapes(planted), planted


def test_cell_values_render_counts_n_a_and_the_by_construction_zero() -> None:
    def rendered(**overrides: Any) -> str:
        fields: dict[str, Any] = {
            "title": "t",
            "heading": "h",
            "definition": "d",
            "reads": (),
            "numerator": 3,
            "denominator": 8,
            "not_evaluable": 0,
            "rate": 0.375,
            "guard": None,
            "by_construction": None,
            "scope": None,
            "in_scope": True,
        }
        fields.update(overrides)
        return command._value(CensusCell(**fields))

    assert rendered() == "3/8 (37.5%)"
    assert rendered(not_evaluable=2) == "3/8 (37.5%), 2 not evaluable"
    assert rendered(numerator=0, denominator=0, rate=None) == "n/a"
    assert (
        rendered(numerator=0, denominator=0, rate=None, by_construction="x = 1")
        == "n/a"
    )
    assert (
        rendered(numerator=0, rate=0.0, guard="x = 1", by_construction="x = 1")
        == "0/8 by construction"
    )
    out_of_scope = rendered(
        numerator=0, denominator=0, rate=None, scope="x = 1", in_scope=False
    )
    assert out_of_scope == "n/a"


def _table_block(page: str, title: str) -> list[str]:
    """The table rows under one bold table title, up to the blank line."""

    lines = page.splitlines()
    start = lines.index(f"**{title}.**") + 4
    return lines[start : lines.index("", start)]


def test_a_table_out_of_its_scope_reads_n_a_and_in_scope_reads_its_count() -> None:
    """Planted: the regroup table in an era without and with the regroup."""

    title = census.TABLES["trigger_tick_events_dropped_by_regroup"].title
    without = command.render_markdown(_planted())
    assert _table_block(without, title) == ["| (none) | n/a | n/a | n/a |"]
    regroup_era = EraKey(
        settings=(("meeting_reset", "hub_with_grace"),),
        temporal_observation_version=None,
        substrate_flags=PLANTED_ERA.substrate_flags,
        prompt_stamps=PLANTED_ERA.prompt_stamps,
    )
    with_regroup = command.render_markdown(
        census_from_inputs([_planted_inputs(era=regroup_era)])
    )
    assert _table_block(with_regroup, title) == ["| (none) | 0 | 0 | 0 |"]
    beneficiaries = census.TABLES["rebuttal_beneficiaries"].title
    assert _table_block(without, beneficiaries) == ["| (none) | n/a | n/a | n/a |"]
    thrown = census.TABLES["actions_thrown_away_on_trigger_ticks"].title
    assert _table_block(without, thrown)[0] == "| move | 1 | 1 | 1 |"


def test_the_definitions_name_the_setting_a_scoped_count_needs() -> None:
    page = command.render_markdown(_planted())
    counted = "Counted only in games recorded with `{}`; in any other era it reads n/a."
    scopes = {key: spec.scope for key, spec in census.CELLS.items()}
    scopes.update((key, spec.scope) for key, spec in census.TABLES.items())
    for key, scope in scopes.items():
        line = next(item for item in page.splitlines() if f"(`{key}`)." in item)
        if scope is None:
            assert "Counted only" not in line, key
        else:
            assert line.endswith(counted.format(scope.describe())), key


def test_the_page_renders_tables_and_their_not_evaluable_rows() -> None:
    page = command.render_markdown(_planted())
    assert "| move | 1 | 1 | 1 |" in page
    assert "| not evaluable | 1 | 1 | 1 |" in page
    assert "| (none) | 0 | 0 | 0 |" in page
    assert "Zero by construction in every recording." in page
    assert "Zero by construction while `self_report = off and" in page
    assert (
        "prompt stamps, read from the MANIFEST rows of games that held a meeting: "
        in page
    )
    assert "`vote_ballot.qwen3_6_27b.v8`" in page
    assert "substrate flags on: absence_prior; off: reporter_reasoning;" in page


def test_the_manifest_reader_agrees_with_the_manifest_writers_parser() -> None:
    for set_dir in COMMITTED_SETS:
        text = (set_dir / "MANIFEST.md").read_text(encoding="utf-8")
        expected = {
            seed: row.prompt_versions for seed, row in parse_manifest(text).items()
        }
        assert dict(census._manifest_prompt_cells(set_dir)) == expected


def test_a_not_evaluable_row_shows_when_any_group_has_one() -> None:
    page = command.render_markdown(
        census_from_inputs(
            [
                _planted_inputs(),
                _planted_inputs(label="samples/4p1i", rows_without_dispositions=0),
            ]
        )
    )
    assert "| not evaluable | 1 | 1 | 1 | 0 |" in page


def test_a_table_with_no_rows_lists_none_before_its_not_evaluable_row() -> None:
    page = command.render_markdown(census_from_inputs([_planted_inputs(discarded=())]))
    assert "| (none) | 0 | 0 | 0 |\n| not evaluable | 1 | 1 | 1 |\n" in page


def test_the_era_lines_name_every_recorded_part_or_say_none() -> None:
    def era_text(era: EraKey) -> str:
        return "\n".join(
            command._era_lines(census_from_inputs([_planted_inputs(era=era)]))
        )

    stamped = era_text(
        EraKey(
            settings=(("meeting_reset", "hub_with_grace"),),
            temporal_observation_version=2,
            substrate_flags=(("absence_prior", True), ("temporal_observations", True)),
            prompt_stamps=None,
        )
    )
    assert "recorded experiment settings: `meeting_reset = hub_with_grace`;" in stamped
    assert "temporal observations: version 2;" in stamped
    assert "substrate flags on: absence_prior, temporal_observations; off: none;" in (
        stamped
    )
    assert "held a meeting: none." in stamped
    bare = era_text(
        EraKey(
            settings=(),
            temporal_observation_version=None,
            substrate_flags=None,
            prompt_stamps=None,
        )
    )
    assert "recorded experiment settings: none beyond the historical defaults;" in bare
    assert "temporal observations: not delivered;" in bare
    assert "substrate flags on: none; off: none;" in bare
    all_off = era_text(
        EraKey(
            settings=(),
            temporal_observation_version=None,
            substrate_flags=(("absence_prior", False),),
            prompt_stamps=None,
        )
    )
    assert "substrate flags on: none; off: absence_prior;" in all_off


def test_the_era_lines_list_settings_and_flags_in_name_order() -> None:
    """Planted: an era whose settings and flags arrive out of name order."""

    unsorted_flags = EraKey(
        settings=(),
        temporal_observation_version=None,
        substrate_flags=(
            ("zeta_flag", True),
            ("alpha_flag", True),
            ("omega_flag", False),
            ("beta_flag", False),
        ),
        prompt_stamps=None,
    )
    planted = census_from_inputs([_planted_inputs(era=unsorted_flags)])
    pooled_era = planted.pooled.era.model_copy(
        update={
            "settings": {
                "vent_witness_rule": "physical",
                "meeting_reset": "hub_with_grace",
            }
        }
    )
    reordered = planted.model_copy(
        update={"pooled": planted.pooled.model_copy(update={"era": pooled_era})}
    )
    text = "\n".join(command._era_lines(reordered))
    assert (
        "recorded experiment settings: `meeting_reset = hub_with_grace`, "
        "`vent_witness_rule = physical`;"
    ) in text
    assert "substrate flags on: alpha_flag, zeta_flag; off: beta_flag, omega_flag;" in (
        text
    )


def test_a_row_only_a_four_player_set_holds_is_published_for_every_group() -> None:
    """Planted: only the four-player set throws a report away or lacks dispositions."""

    page = command.render_markdown(
        census_from_inputs(
            [
                _planted_inputs(rows_without_dispositions=0),
                _planted_inputs(
                    label="samples/4p1i",
                    discarded=("move", "report"),
                    rows_without_dispositions=2,
                ),
            ]
        )
    )
    thrown = census.TABLES["actions_thrown_away_on_trigger_ticks"].title
    assert _table_block(page, thrown) == [
        "| move | 2 | 1 | 1 | 1 |",
        "| report | 1 | 0 | 0 | 1 |",
        "| not evaluable | 2 | 0 | 0 | 2 |",
    ]


def test_a_tables_rows_are_listed_numeric_first_then_alphabetically() -> None:
    """Planted: one table holding numeric and text rows, thrown away out of order."""

    page = command.render_markdown(
        census_from_inputs([_planted_inputs(discarded=("b", "10", "a", "2"))])
    )
    thrown = census.TABLES["actions_thrown_away_on_trigger_ticks"].title
    assert [line.split(" | ")[0] for line in _table_block(page, thrown)] == [
        "| 2",
        "| 10",
        "| a",
        "| b",
        "| not evaluable",
    ]
