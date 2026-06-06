"""Consistency gate for ``scripts/build_sample_report.py``.

Closes the "refresh regenerates replays but not the report" gap: rebuilding the
FROZEN flat 4p/1i set's report from its committed replays must equal the committed
``tournament-eval-report.json``, so a stale committed report (the CI-invisible
failure mode flagged at the Phase 7 Wave 0 close — a refresh that forgets the
separate offline report build) fails here instead of shipping.

The 7p/2i set is intentionally NOT covered yet: its committed report predates the
Task 7.11 reporting fields and the set is about to be re-recorded (Phase 7 Wave
0.5). It joins this gate once the re-record + ``refresh_samples.sh``'s new build
step regenerate it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import build_sample_report as bsr
from eval.meeting_quality import TournamentEvalReport

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FLAT_4P1I = _REPO_ROOT / "replays" / "samples"
_COMMITTED_REPORT = _FLAT_4P1I / "tournament-eval-report.json"

# Every test in this module reads the committed flat 4p/1i bytes (directly or
# via _copy_flat_replays), which were invalidated by the Phase-8 byte-breakers:
# the Task 8.1 per-player task re-key changed every per-tick state_hash and the
# Task 8.7 meeting reshape changed the recorded transcript shape, so the
# committed replays no longer parse/reconstruct. Task 8.12 re-records both
# committed sets and re-enables this module (mirrors the 8.1/8.7 skips in
# tests/scripts/test_verify_samples.py).
pytestmark = pytest.mark.skip(
    reason=(
        "Committed sample bytes invalidated by the Task 8.1 state_hash change "
        "(DESIGN.md §3.2) and the Task 8.7 meeting-record reshape (§5.2); "
        "re-recorded and re-enabled in Task 8.12."
    )
)


def _copy_flat_replays(dst: Path) -> None:
    """Copy the committed flat 4p/1i replay JSONL into ``dst`` (no roster.json).

    A directory with no ``roster.json`` is the flat 4p/1i default, so a rebuild in
    ``dst`` re-seeds 4p/1i exactly as the committed set does.
    """

    for jsonl in _FLAT_4P1I.glob("replay-seed-*.jsonl"):
        (dst / jsonl.name).write_bytes(jsonl.read_bytes())


def test_rebuild_matches_committed_flat_4p1i() -> None:
    """A rebuild from the committed 4p/1i replays equals the committed report."""

    rebuilt = bsr.build_report(_FLAT_4P1I).model_dump(mode="json")
    committed = json.loads(_COMMITTED_REPORT.read_text(encoding="utf-8"))
    assert rebuilt == committed, (
        "The committed flat 4p/1i tournament-eval-report.json is STALE — it does "
        "not match a rebuild from its own replays. Run `uv run python "
        "scripts/build_sample_report.py --sample-dir replays/samples` and commit it."
    )


def test_check_reports_consistent_on_committed_flat_4p1i() -> None:
    """``--check`` returns 0 when the committed report matches its replays."""

    assert bsr.check_report(_FLAT_4P1I) == 0


def test_check_flags_a_stale_report(tmp_path: Path) -> None:
    """``--check`` returns 1 when the on-disk report drifts from a rebuild."""

    _copy_flat_replays(tmp_path)
    stale = json.loads(_COMMITTED_REPORT.read_text(encoding="utf-8"))
    stale["meeting_rate"]["meetings_total"] += 7  # tamper: no longer matches replays
    (tmp_path / "tournament-eval-report.json").write_text(json.dumps(stale))
    assert bsr.check_report(tmp_path) == 1


def test_write_report_emits_a_loadable_consistent_file(tmp_path: Path) -> None:
    """``write_report`` writes a model-valid report matching the committed one."""

    _copy_flat_replays(tmp_path)
    bsr.write_report(tmp_path)
    written = (tmp_path / "tournament-eval-report.json").read_text(encoding="utf-8")
    # Round-trips through the frozen model and equals the committed flat report
    # (same replays, same flat-default roster).
    assert TournamentEvalReport.model_validate_json(written)
    assert json.loads(written) == json.loads(
        _COMMITTED_REPORT.read_text(encoding="utf-8")
    )
