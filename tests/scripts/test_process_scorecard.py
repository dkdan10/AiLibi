"""The committed scorecard must match a recomputation from the recordings.

``tests/scripts/test_build_sample_report.py`` calls ``check_report`` on the
committed sets and ``scripts/check.sh`` runs pytest, so the consistency gate
needs no new shell line — this module is the second, independent ``--check``
over the NEW artifact, added the same way.

Three things are pinned here. The published pair recomputes byte-identically
from the committed recordings; ``--check`` goes RED on a single edited cell,
demonstrated by planting one rather than asserted in prose; and the writer
refuses a destination inside a recording location BEFORE it computes anything,
so the command cannot be aimed at the bytes it reads. The third is CONTAINMENT
and not file identity: a destination that does not exist yet, inside a recording
set, is refused too, and the perturbed half shows the files-only list accepting
the same destination.

The committed fold runs ONCE here, in the first test. The planted-drift case
runs the real ``publish`` / ``check_report`` pair against a planted scorecard in
a temp tree, so the gate itself is exercised end to end without a second walk.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

import publish_process_scorecard as command
from _report_output import _check_destination
from eval import process_scorecard as scorecard_module
from eval.process_scorecard import (
    BEFORE_COLUMNS_PATH,
    DECISION_DATE,
    NO_CONSUMER_NOTE,
    RECORDINGS_ROOT,
    ROLE_CORRECTNESS_NOTE,
    ROW_DEFINITIONS,
    SCHEMA_VERSION,
    BeforeColumnsError,
    EraScorecard,
    ProcessScorecard,
    ProcessTally,
    compute_process_scorecard,
    read_before_columns,
    scorecard_from_tally,
)

ROOT = Path(__file__).resolve().parents[2]


def test_the_committed_scorecard_matches_a_recomputation() -> None:
    """The gate: both published files are what the recordings say they are.

    This is the only committed-bytes fold in the suite for this instrument; the
    per-row semantics are planted in ``tests/eval/test_process_scorecard.py``,
    which walks nothing.
    """

    assert command.check_report(ROOT) == 0, (
        "docs/process-scorecard.md / .json are STALE — re-run "
        f"`{command.REGENERATE_COMMAND}` and commit the result."
    )


def _planted_scorecard() -> ProcessScorecard:
    """A whole scorecard built from counts, with no recording behind it."""

    card = scorecard_from_tally(
        ProcessTally(
            games=1,
            meetings=1,
            ballots=2,
            eject_ballots=1,
            skip_ballots=1,
            grounded_eject=1,
            ejections=1,
            ejections_role_correct=1,
            authored_ballots=2,
        ),
        label="planted",
        sources=("planted",),
    )
    return ProcessScorecard(
        schema_version=SCHEMA_VERSION,
        decision_date=DECISION_DATE,
        role_correctness_is_a_gate=False,
        role_correctness_reported=True,
        role_correctness_note=ROLE_CORRECTNESS_NOTE,
        no_consumer_note=NO_CONSUMER_NOTE,
        row_definitions=dict(ROW_DEFINITIONS),
        report_format_version=2,
        recording_provenance=("planted",),
        eras=(
            EraScorecard(
                era_id="planted",
                record="planted",
                recorded_on="2026-01-01",
                sets=("planted",),
                pooled=card,
            ),
        ),
        sets=(card,),
        before=(),
    )


def test_one_edited_cell_turns_check_red(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Publish, verify green, move ONE integer, and watch the gate go red."""

    planted = _planted_scorecard()
    monkeypatch.setattr(command, "compute_process_scorecard", lambda _root: planted)
    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    command.publish(root)
    assert command.check_report(root) == 0

    published = root / command.JSON_PATH
    payload = json.loads(published.read_text(encoding="utf-8"))
    payload["eras"][0]["pooled"]["role_correct_ejection"]["numerator"] += 1
    published.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    assert command.check_report(root) == 1
    message = capsys.readouterr().out
    assert str(command.JSON_PATH) in message
    assert command.REGENERATE_COMMAND in message


def test_a_published_json_carrying_the_retired_appendix_turns_check_red(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Schema 3 carries no appendix: a restored ``appendix`` key is drift.

    A version-2 reader expects the key; the version bump and the recomputation
    are what keep a stale page from passing as the current one.
    """

    planted = _planted_scorecard()
    monkeypatch.setattr(command, "compute_process_scorecard", lambda _root: planted)
    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    command.publish(root)
    assert command.check_report(root) == 0
    assert SCHEMA_VERSION == 3

    published = root / command.JSON_PATH
    payload = json.loads(published.read_text(encoding="utf-8"))
    assert "appendix" not in payload
    payload["appendix"] = {"label": "Appendix: the fifth run (2026-09-16)"}
    published.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    assert command.check_report(root) == 1


def test_main_prints_one_line_per_era(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Planted: a pooled era and a one-set era; each prints its own group's counts."""

    planted = _planted_scorecard()
    (pooled_era,) = planted.eras
    solo = planted.sets[0].model_copy(
        update={"label": "solo", "sources": ("solo",), "ballots": 7, "meetings": 5}
    )
    two_eras = planted.model_copy(
        update={
            "eras": (
                pooled_era,
                EraScorecard(
                    era_id="solo-era",
                    record="planted",
                    recorded_on="2026-01-02",
                    sets=("solo",),
                    pooled=None,
                ),
            ),
            "sets": (planted.sets[0], solo),
        }
    )
    monkeypatch.setattr(command, "compute_process_scorecard", lambda _root: two_eras)
    monkeypatch.setattr(command, "_REPO_ROOT", tmp_path)
    (tmp_path / "docs").mkdir()
    assert command.main([]) == 0
    printed = capsys.readouterr().out.splitlines()
    assert [line.split(":", 1)[0] for line in printed] == [
        f"Wrote {command.MARKDOWN_PATH} and {command.JSON_PATH}, era planted",
        f"Wrote {command.MARKDOWN_PATH} and {command.JSON_PATH}, era solo-era",
    ]
    assert " 2 ballots over 1 meetings;" in printed[0]
    assert " 7 ballots over 5 meetings;" in printed[1]


def _before_tree(tmp_path: Path) -> Path:
    """A scratch tree holding the committed pages and the pinned before columns."""

    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    for relative in (command.MARKDOWN_PATH, command.JSON_PATH, BEFORE_COLUMNS_PATH):
        (root / relative).write_bytes((ROOT / relative).read_bytes())
    return root


def test_the_before_column_is_the_replaced_sets_baseline_9_entry() -> None:
    """The one before block: ``samples/9p2i`` at baseline 9, as published at d41c9006."""

    (block,) = read_before_columns(ROOT)
    assert (block.set, block.era_id, block.commit) == (
        "replays/samples/9p2i",
        "baseline-9",
        "d41c9006",
    )
    card = block.scorecard
    assert (card.label, card.games, card.meetings, card.ballots) == (
        "samples/9p2i",
        50,
        145,
        845,
    )
    published = json.loads((ROOT / command.JSON_PATH).read_text(encoding="utf-8"))
    assert published["before"] == [
        json.loads((ROOT / BEFORE_COLUMNS_PATH).read_text(encoding="utf-8"))[0]
    ]


def test_one_edited_leaf_of_the_before_column_turns_check_red(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Planted: one integer of the frozen column moves; the fold refuses."""

    root = _before_tree(tmp_path)
    assert read_before_columns(root) == read_before_columns(ROOT)
    path = root / BEFORE_COLUMNS_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload[0]["scorecard"]["role_correct_ejection"]["numerator"] -= 1
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(BeforeColumnsError, match="never edited or recomputed"):
        read_before_columns(root)
    assert command.check_report(root) == 1
    message = capsys.readouterr().out
    assert message.startswith(f"--check: {BEFORE_COLUMNS_PATH} reads sha256 ")
    assert "a before column is history and is never edited or recomputed" in message


def _pinned_planted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: object
) -> Path:
    """A scratch tree whose before file the module's pin is moved to accept."""

    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    data = (json.dumps(payload) + "\n").encode("utf-8")
    (root / BEFORE_COLUMNS_PATH).write_bytes(data)
    monkeypatch.setattr(
        scorecard_module, "BEFORE_COLUMNS_SHA256", hashlib.sha256(data).hexdigest()
    )
    return root


def test_a_before_file_that_is_not_a_list_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _pinned_planted(tmp_path, monkeypatch, {"set": "replays/samples/9p2i"})
    with pytest.raises(BeforeColumnsError, match="must hold one JSON list"):
        read_before_columns(root)


def test_a_before_column_for_a_set_the_registry_does_not_name_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the committed block moved onto a candidate round's path."""

    block = json.loads((ROOT / BEFORE_COLUMNS_PATH).read_text(encoding="utf-8"))[0]
    moved = {**block, "set": "replays/candidates/stage-b-r1/9p2i"}
    root = _pinned_planted(tmp_path, monkeypatch, [moved])
    with pytest.raises(BeforeColumnsError, match="the era registry does not name"):
        compute_process_scorecard(root)


def test_a_missing_published_file_is_red_rather_than_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        command, "compute_process_scorecard", lambda _root: _planted_scorecard()
    )
    root = tmp_path / "tree"
    (root / "docs").mkdir(parents=True)
    assert command.check_report(root) == 1


@pytest.mark.parametrize(
    "relative",
    (
        # Existing recordings: file identity refuses these.
        "replays/samples/4p1i/replay-seed-0.jsonl",
        "replays/samples/9p2i/roster.json",
        "replays/ml_corpus/9p2i/tournament-eval-report.json.gz",
        "audits/deduction-candidate/run-2026-09-16/RESULTS.md",
        # Destinations that do NOT exist yet, inside a recording location.
        # Nothing on a files-only protected list matches them, so containment —
        # the recording roots — is the only thing that can refuse them.
        "replays/new-process-scorecard.md",
        "replays/samples/9p2i/new-scorecard.md",
        "audits/deduction-candidate/run-2026-09-16/new-scorecard.md",
    ),
)
def test_the_writer_refuses_a_recording_destination_before_computing(
    monkeypatch: pytest.MonkeyPatch, relative: str
) -> None:
    """A destination inside a recording location is refused, nothing computed.

    An existing recording must keep its bytes; a destination that does not exist
    yet must still not exist after the refusal, because ``preflight_report_output``
    CREATES its destination as an exclusivity probe once the containment test has
    passed. That creation is the damage a files-only list allowed.
    """

    source = ROOT / relative
    before = source.read_bytes() if source.exists() else None

    def forbidden(_root: Path) -> Any:
        raise AssertionError("the fold must not start for an invalid destination")

    monkeypatch.setattr(command, "compute_process_scorecard", forbidden)
    monkeypatch.setattr(command, "MARKDOWN_PATH", Path(relative))
    with pytest.raises(ValueError, match="overlaps"):
        command.publish(ROOT)
    if before is None:
        assert not source.exists(), "the refusal must leave nothing behind"
    else:
        assert source.read_bytes() == before


def test_the_recording_roots_are_protected_by_containment() -> None:
    """The perturbation: strip the roots and the same destination is ACCEPTED.

    ``protected_inputs`` carries the recording DIRECTORIES beside the files. With
    them, a not-yet-existing destination inside a recording set is refused; with
    the pre-correction, files-only half of the list, ``_check_destination``
    matches nothing and lets it through — which is the defect this containment
    fixes, planted here rather than asserted in prose.
    """

    protected = command.protected_inputs(ROOT)
    roots = {path.resolve() for path in protected if path.is_dir()}
    assert (ROOT / RECORDINGS_ROOT).resolve() in roots
    for archive in command.PROTECTED_ARCHIVES:
        assert (ROOT / archive).resolve() in roots

    destination = ROOT / RECORDINGS_ROOT / "samples" / "9p2i" / "new-scorecard.md"
    assert not destination.exists()
    files_only = [path for path in protected if path.is_file()]
    _check_destination(destination, files_only)
    with pytest.raises(ValueError, match="overlaps"):
        _check_destination(destination, protected)


def test_the_fifth_run_archive_is_protected_from_the_writer() -> None:
    """Every byte of the fifth run's archive stays on the protected list.

    The page stopped folding the archive on 2026-10-09; the archive keeps its
    bytes, so the writer still refuses to write there.
    """

    protected = {path.resolve() for path in command.protected_inputs(ROOT)}
    archive = ROOT / "audits" / "deduction-candidate" / "run-2026-09-16"
    present = [path for path in archive.iterdir() if path.is_file()]
    assert present, archive
    assert all(path.resolve() in protected for path in present)


# --------------------------------------------------------------------------- #
# ``--set-dir DIR --json-stdout``: one directory's scorecard, written nowhere.  #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def candidate_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A fake set two levels below a planted ``replays/`` root."""

    from tests._helpers.scripted_meeting import record_game

    root = tmp_path_factory.mktemp("planted")
    directory = root / "replays" / "candidates" / "round-1" / "9p2i"
    for seed in (0, 1):
        record_game(directory, seed=seed, config=None)
    return directory


def _listing(root: Path) -> list[tuple[str, int, int]]:
    return sorted(
        (str(path.relative_to(root)), path.stat().st_size, path.stat().st_mtime_ns)
        for path in root.rglob("*")
    )


def _repository_listing() -> str:
    """The checkout's own status where this script writes, and its two files."""

    import subprocess

    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", "docs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    published = [
        (path.name, path.stat().st_size, path.stat().st_mtime_ns)
        for path in (ROOT / command.MARKDOWN_PATH, ROOT / command.JSON_PATH)
    ]
    return f"{status}{published}"


def test_set_dir_prints_the_in_process_fold_and_writes_nothing(
    candidate_set: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dataclasses import replace

    from eval.process_scorecard import fold_set, load_set_inputs

    planted_root = candidate_set.parents[3]

    def _no_writer(*args: object, **kwargs: object) -> None:
        raise AssertionError("--set-dir reached a writer")

    monkeypatch.setattr(command, "atomic_write_report", _no_writer)
    monkeypatch.setattr(command, "preflight_report_output", _no_writer)
    before = (_listing(planted_root), _repository_listing())
    assert command.main(["--set-dir", str(candidate_set), "--json-stdout"]) == 0
    printed = capsys.readouterr().out
    assert (_listing(planted_root), _repository_listing()) == before

    inputs = load_set_inputs(candidate_set)
    source = command.set_source(candidate_set, root=command._REPO_ROOT)
    card = scorecard_from_tally(
        fold_set(replace(inputs, source=source)),
        label=inputs.label,
        sources=(source,),
    )
    assert json.loads(printed) == card.model_dump(mode="json")
    assert printed == (
        json.dumps(
            card.model_dump(mode="json"), indent=2, sort_keys=True, ensure_ascii=False
        )
        + "\n"
    )
    assert card.games == 2


def test_set_dir_names_the_directory_it_walked(
    candidate_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import types

    from eval.process_scorecard import load_set_inputs

    planted_root = candidate_set.parents[3]
    printed = json.loads(command.set_dir_json(candidate_set, root=planted_root))
    assert printed["sources"] == ["replays/candidates/round-1/9p2i"]
    # The loader's own naming, which the replacement works around, drops a level.
    assert load_set_inputs(candidate_set).source == "replays/round-1/9p2i"
    # Perturbed: without the replacement the misnamed source is printed.
    monkeypatch.setattr(
        command,
        "dataclasses",
        types.SimpleNamespace(replace=lambda inputs, **changes: inputs),
    )
    misnamed = json.loads(command.set_dir_json(candidate_set, root=planted_root))
    assert misnamed["sources"] == ["replays/round-1/9p2i"]
    outside = command.set_source(candidate_set, root=ROOT)
    assert outside == str(candidate_set.resolve())


@pytest.mark.parametrize(
    "arguments",
    [
        ["--set-dir", "{set}", "--json-stdout", "--check"],
        ["--set-dir", "{set}"],
        ["--json-stdout"],
        ["--set-dir", "{empty}", "--json-stdout"],
    ],
    ids=["with-check", "without-json-stdout", "json-stdout-alone", "no-replays"],
)
def test_set_dir_refuses_what_it_cannot_serve(
    candidate_set: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    arguments: list[str],
) -> None:
    resolved = [item.format(set=candidate_set, empty=tmp_path) for item in arguments]
    with pytest.raises(SystemExit) as refused:
        command.main(resolved)
    assert refused.value.code == 2
    error = capsys.readouterr().err
    # argparse prints the usage, then "<prog>: error: <message>" as its last line.
    if "{empty}" in arguments:
        message = f"error: --set-dir {tmp_path} holds no replay files"
    else:
        message = "error: --set-dir and --json-stdout go together, without --check"
    assert error.splitlines()[-1].endswith(f": {message}")
