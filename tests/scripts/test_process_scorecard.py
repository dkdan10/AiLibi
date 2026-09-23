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

import json
from pathlib import Path
from typing import Any

import pytest

import publish_process_scorecard as command
from _report_output import _check_destination
from eval.process_scorecard import (
    DECISION_DATE,
    FIFTH_RUN_ARCHIVE,
    NO_CONSUMER_NOTE,
    RECORDINGS_ROOT,
    ROLE_CORRECTNESS_NOTE,
    ROW_DEFINITIONS,
    SCHEMA_VERSION,
    FifthRunAppendix,
    FifthRunArm,
    ProcessScorecard,
    ProcessTally,
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
    appendix = FifthRunAppendix(
        label="planted appendix",
        archive="planted",
        note="planted",
        arms=(
            FifthRunArm(
                arm="planted",
                recordings=1,
                meetings=1,
                eject_ballots=1,
                eject_ballots_cited=1,
                skip_ballots=1,
                skip_ballots_cited=0,
            ),
        ),
        ballots_per_meeting={"3": 1},
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
        sets=(card,),
        pooled=card,
        pooled_9p2i=card,
        appendix=appendix,
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
    payload["pooled"]["role_correct_ejection"]["numerator"] += 1
    published.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    assert command.check_report(root) == 1
    message = capsys.readouterr().out
    assert str(command.JSON_PATH) in message
    assert command.REGENERATE_COMMAND in message


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
    assert (ROOT / FIFTH_RUN_ARCHIVE).resolve() in roots

    destination = ROOT / RECORDINGS_ROOT / "samples" / "9p2i" / "new-scorecard.md"
    assert not destination.exists()
    files_only = [path for path in protected if path.is_file()]
    _check_destination(destination, files_only)
    with pytest.raises(ValueError, match="overlaps"):
        _check_destination(destination, protected)


def test_the_fifth_run_archive_is_protected_from_the_writer() -> None:
    """Every archive byte the appendix reads is on the protected list."""

    protected = {path.resolve() for path in command.protected_inputs(ROOT)}
    archive = ROOT / "audits" / "deduction-candidate" / "run-2026-09-16"
    present = [path for path in archive.iterdir() if path.is_file()]
    assert present, archive
    assert all(path.resolve() in protected for path in present)
