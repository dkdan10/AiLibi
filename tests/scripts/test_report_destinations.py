"""Reject report collisions before spending and preserve reports on write failure."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest

import run_tournament as rt
from eval.meeting_quality import TournamentEvalReport


def _args(output_dir: Path, report: Path) -> list[str]:
    return [
        "--output-dir",
        str(output_dir),
        "--report-output",
        str(report),
        "--start-seed",
        "5",
        "--num-games",
        "3",
        "--max-ticks",
        "2",
        "--force",
    ]


def _refuse_evaluator(monkeypatch: pytest.MonkeyPatch) -> list[bool]:
    called: list[bool] = []

    def evaluator(**kwargs: Any) -> None:
        called.append(True)
        raise AssertionError("destination validation must precede the evaluator")

    monkeypatch.setattr(rt, "run_tournament_eval", evaluator)
    return called


@pytest.mark.parametrize("suffix", ["", ".audit"])
@pytest.mark.parametrize(
    "alias", ["direct", "normalized", "parent_link", "leaf_link", "hardlink"]
)
def test_report_cannot_alias_any_selected_recording(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, suffix: str, alias: str
) -> None:
    output_dir = tmp_path / "games"
    output_dir.mkdir()
    recording = output_dir / f"replay-seed-7{suffix}.jsonl"
    recording.write_bytes(b"previous recording\n")
    if alias == "direct":
        report = recording
    elif alias == "normalized":
        (output_dir / "spare").mkdir()
        report = output_dir / "spare" / ".." / recording.name
    elif alias == "parent_link":
        link = tmp_path / "linked-games"
        link.symlink_to(output_dir, target_is_directory=True)
        report = link / recording.name
    else:
        report = tmp_path / "report.json"
        if alias == "leaf_link":
            report.symlink_to(recording)
        else:
            report.hardlink_to(recording)
    called = _refuse_evaluator(monkeypatch)
    with pytest.raises((ValueError, OSError)):
        rt.main(_args(output_dir, report))
    assert called == []
    assert recording.read_bytes() == b"previous recording\n"
    assert not (output_dir / "replay-seed-5.jsonl").exists()


@pytest.mark.parametrize("suffix", ["", ".audit"])
def test_report_rejects_a_fresh_case_alias_on_insensitive_filesystems(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, suffix: str
) -> None:
    probe = tmp_path / "case-probe"
    probe.touch()
    insensitive = (tmp_path / "CASE-PROBE").exists()
    probe.unlink()
    if not insensitive:
        pytest.skip("filesystem is case-sensitive")
    output_dir = tmp_path / "games"
    output_dir.mkdir()
    recording = output_dir / f"replay-seed-7{suffix}.jsonl"
    report = recording.with_name(recording.name.upper())
    called = _refuse_evaluator(monkeypatch)
    with pytest.raises(ValueError, match="overlap"):
        rt.main(_args(output_dir, report))
    assert called == []
    assert not recording.exists()
    assert not report.exists()


@pytest.mark.parametrize(
    "kind", ["directory", "blocked_parent", "device", "broken_link", "nested"]
)
def test_invalid_report_destinations_fail_before_evaluation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    output_dir = tmp_path / "games"
    output_dir.mkdir()
    preserved = tmp_path / "preserved"
    preserved.write_bytes(b"keep\n")
    if kind == "directory":
        report = output_dir
    elif kind == "blocked_parent":
        report = preserved / "report.json"
    elif kind == "device":
        report = Path(os.devnull)
    elif kind == "broken_link":
        report = tmp_path / "report.json"
        report.symlink_to(tmp_path / "absent")
    else:
        report = output_dir / "replay-seed-7.audit.jsonl" / "report.json"
    called = _refuse_evaluator(monkeypatch)
    with pytest.raises((ValueError, OSError)):
        rt.main(_args(output_dir, report))
    assert called == []
    assert preserved.read_bytes() == b"keep\n"
    assert not (output_dir / "replay-seed-5.jsonl").exists()


def test_unwritable_report_parent_fails_before_evaluation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = tmp_path / "report.json"
    report.write_bytes(b"previous report\n")
    called = _refuse_evaluator(monkeypatch)

    def denied(*args: Any, **kwargs: Any) -> tuple[int, str]:
        raise PermissionError("injected report-directory denial")

    monkeypatch.setattr(tempfile, "mkstemp", denied)
    with pytest.raises(PermissionError, match="injected"):
        rt.main(_args(tmp_path / "games", report))
    assert called == []
    assert report.read_bytes() == b"previous report\n"


def _small_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> TournamentEvalReport:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    assert (
        rt.main(["--output-dir", str(tmp_path), "--num-games", "1", "--max-ticks", "2"])
        == 0
    )
    return TournamentEvalReport.model_validate_json(
        (tmp_path / "tournament-eval-report.json").read_text()
    )


def test_custom_report_destination_preserves_recording_jsonl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    output_dir = tmp_path / "games"
    report = tmp_path / "summaries" / "custom.json"
    assert rt.main(_args(output_dir, report)) == 0
    parsed = TournamentEvalReport.model_validate_json(report.read_text())
    assert [game.seed for game in parsed.report.games] == [5, 6, 7]
    for seed in range(5, 8):
        for suffix in ("", ".audit"):
            path = output_dir / f"replay-seed-{seed}{suffix}.jsonl"
            assert len(path.read_text().splitlines()) >= 2
            assert all(
                isinstance(json.loads(row), dict)
                for row in path.read_text().splitlines()
            )
    assert list(report.parent.glob(".ailibi-report-*")) == []


def test_partial_report_write_does_not_truncate_previous_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = _small_report(tmp_path / "source", monkeypatch)
    destination = tmp_path / "existing.json"
    destination.write_bytes(b"previous report\n")
    original_write = Path.write_text

    def partial_write(path: Path, data: str, *args: Any, **kwargs: Any) -> int:
        original_write(path, data[:12], *args, **kwargs)
        raise OSError("injected interrupted report write")

    monkeypatch.setattr(Path, "write_text", partial_write)
    with pytest.raises(OSError, match="interrupted"):
        rt._emit_report_json(report, destination)
    assert destination.read_bytes() == b"previous report\n"
    assert list(tmp_path.glob(".ailibi-report-*")) == []


def test_failed_report_replace_keeps_previous_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = _small_report(tmp_path / "source", monkeypatch)
    destination = tmp_path / "existing.json"
    destination.write_bytes(b"previous report\n")

    def denied(path: Path, target: Path) -> Path:
        assert path.read_text().endswith("\n")
        TournamentEvalReport.model_validate_json(path.read_text())
        raise PermissionError("injected report replacement denial")

    monkeypatch.setattr(Path, "replace", denied)
    with pytest.raises(PermissionError, match="replacement denial"):
        rt._emit_report_json(report, destination)
    assert destination.read_bytes() == b"previous report\n"
    assert list(tmp_path.glob(".ailibi-report-*")) == []


def test_report_cleanup_failure_preserves_the_publication_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    report = _small_report(tmp_path / "source", monkeypatch)
    destination = tmp_path / "existing.json"
    destination.write_bytes(b"previous report\n")
    write_error = OSError("injected write failure")
    cleanup_error = PermissionError("injected cleanup failure")

    def interrupted(path: Path, data: str, *args: Any, **kwargs: Any) -> int:
        raise write_error

    def denied(path: Path, missing_ok: bool = False) -> None:
        raise cleanup_error

    monkeypatch.setattr(Path, "write_text", interrupted)
    monkeypatch.setattr(Path, "unlink", denied)
    with pytest.raises(BaseExceptionGroup) as caught:
        rt._emit_report_json(report, destination)
    assert caught.value.exceptions == (write_error, cleanup_error)
    assert destination.read_bytes() == b"previous report\n"
    retained = list(tmp_path.glob(".ailibi-report-*"))
    assert len(retained) == 1
    assert str(retained[0]) in str(caught.value)
