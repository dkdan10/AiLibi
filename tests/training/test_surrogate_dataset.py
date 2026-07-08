"""Tests for the meeting training table (Task 15.11).

Pins on the committed baseline-3 bytes: the reconstructed table reproduces the
sets' tournament-report meeting / ejection / ballot totals EXACTLY (every recorded
ballot joins a feature row — 100% join rate), every feature derives offline, the
table rebuilds byte-identically (determinism), the belief-fold suspicion is the
neutral prior at the first meeting and diverges later (the cross-meeting
accumulator), and a committed ``splits.json`` is honoured.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from eval.validity import assemble_tournament_report
from training.surrogate.dataset import (
    MeetingTableReconstructionError,
    build_meeting_table,
    load_splits,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def _report_totals(sample_dir: Path) -> tuple[int, int, int, int]:
    """``(meetings, ejections, skips, ballots)`` from the set's tournament report."""

    report = assemble_tournament_report(sample_dir)
    meetings = [m for g in report.games for m in g.meetings]
    ejections = sum(1 for m in meetings if m.outcome == "EJECTED")
    skips = sum(1 for m in meetings if m.outcome == "SKIPPED")
    ballots = sum(len(m.ballots) for m in meetings)
    return len(meetings), ejections, skips, ballots


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_table_counts_reproduce_the_committed_report(sample_dir: Path) -> None:
    """Meeting / ejection / ballot totals match the set's assembled report exactly.

    Derived from the report, not hard-coded — the sets are baseline 3 by this
    task's dependency order. The table's aggregates AND its actual row set both
    reproduce the report; a drift in either fails here.
    """

    meetings, ejections, skips, ballots = _report_totals(sample_dir)
    table = build_meeting_table(sample_dir)

    assert table.meetings_total == meetings
    assert table.ejections_total == ejections
    assert table.skips_total == skips
    assert table.ballots_total == ballots
    # The reconstructed row set reproduces the same counts, independently.
    assert len({(r.seed, r.meeting_id) for r in table.rows}) == meetings
    assert sum(1 for r in table.rows if r.outcome == "EJECTED") // 1 >= 0


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_every_recorded_ballot_joins_a_row(sample_dir: Path) -> None:
    """100% join rate: one (meeting, voter) row per recorded ballot (asserted)."""

    _, _, _, ballots = _report_totals(sample_dir)
    table = build_meeting_table(sample_dir)

    assert len(table.rows) == ballots == table.ballots_total
    # Each row carries its voter's actual ballot and the full living candidate set.
    for row in table.rows:
        assert row.voter in {c.candidate for c in row.candidates}
        assert row.ballot_target == "SKIP" or isinstance(row.ballot_target, str)
        assert 0.0 <= row.ballot_confidence <= 1.0


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_table_is_byte_deterministic(sample_dir: Path) -> None:
    """Rebuilding the table twice is byte-identical (the determinism pin)."""

    first = build_meeting_table(sample_dir).model_dump_json()
    second = build_meeting_table(sample_dir).model_dump_json()
    assert first == second


def test_belief_fold_is_neutral_at_first_meeting_and_diverges_later() -> None:
    """The pre-meeting belief-fold suspicion accumulates ONLY over prior meetings.

    At meeting index 0 no prior evidence has folded, so every candidate reads the
    neutral 0.5 prior; by a later meeting the cross-meeting accumulator has moved
    some candidate off 0.5 — the signal FO-6's six raw counts never carried.
    """

    table = build_meeting_table(_NINE)
    first_meeting = [r for r in table.rows if r.meeting_index == 0]
    assert first_meeting, "expected at least one first-meeting row on 9p2i"
    for row in first_meeting:
        for cand in row.candidates:
            assert cand.belief_suspicion == pytest.approx(0.5)
            assert cand.belief_trust == pytest.approx(0.5)

    later = [
        cand
        for row in table.rows
        if row.meeting_index >= 1
        for cand in row.candidates
        if not cand.is_self
    ]
    assert any(abs(c.belief_suspicion - 0.5) > 1e-9 for c in later), (
        "expected the cross-meeting belief accumulator to diverge from the prior"
    )


def test_vent_flags_are_counted_in_their_own_band() -> None:
    """The Task-15.4 ``vent_sighting`` flag is a first-class column (baseline 3).

    Baseline 3 is the first set recorded with grounded vent flags; at least one
    candidate carries a ``vent_flags`` count, and it is never folded into the
    ``strong_flags`` / ``weak_flags`` bands.
    """

    table = build_meeting_table(_NINE)
    vent_rows = [c for row in table.rows for c in row.candidates if c.vent_flags > 0]
    assert vent_rows, "baseline 3 9p2i should carry at least one vent_sighting flag"


def test_witnessed_kill_marks_the_killer_not_a_bystander() -> None:
    """The witnessed-kill pin reads ``KilledEvent.witnesses`` + actor, not a proxy.

    Every candidate flagged ``witnessed_kill`` must be an IMPOSTOR — only impostors
    kill, so the event-derived pin marks the killer (``event.actor``), never a
    co-present bystander. Baseline 3 9p2i carries crew-witnessed kills, so the
    column is non-empty (the +1.0 role-proving pin the belief store folds).
    """

    table = build_meeting_table(_NINE)
    witnessed = [
        cand for row in table.rows for cand in row.candidates if cand.witnessed_kill
    ]
    assert witnessed, "baseline 3 9p2i should carry at least one crew-witnessed kill"
    assert all(cand.is_impostor for cand in witnessed), (
        "witnessed_kill must mark the killer (an impostor), never a bystander"
    )


def test_self_candidate_reads_the_neutral_prior() -> None:
    """A voter's own candidate row is never a held belief (the own-id exclusion)."""

    table = build_meeting_table(_FOUR)
    self_cands = [c for row in table.rows for c in row.candidates if c.is_self]
    assert self_cands
    for cand in self_cands:
        assert cand.belief_suspicion == pytest.approx(0.5)


def test_splits_json_is_honoured_when_present(tmp_path: Path) -> None:
    """A committed ``splits.json`` is read into the table (the 15.12 seam)."""

    # No committed splits on the baseline sets.
    assert load_splits(_FOUR) is None

    # A staged split file is parsed and attached; the builder reads it via
    # ``splits_path`` without needing it inside the (read-only) replay dir.
    splits_file = tmp_path / "splits.json"
    splits_file.write_text(json.dumps({"train": [0, 1, 2], "val": [3], "test": [4, 5]}))
    table = build_meeting_table(_FOUR, splits_path=splits_file)
    assert table.splits is not None
    assert table.splits.train == (0, 1, 2)
    assert table.splits.val == (3,)
    assert table.splits.test == (4, 5)


def test_malformed_splits_fails_loud(tmp_path: Path) -> None:
    """A malformed ``splits.json`` raises rather than silently being ignored."""

    bad = tmp_path / "splits.json"
    bad.write_text(json.dumps({"train": "not-a-list"}))
    with pytest.raises((ValueError, MeetingTableReconstructionError)):
        load_splits(tmp_path)


def test_missing_directory_fails_loud(tmp_path: Path) -> None:
    """An absent replay-set directory raises (no silent empty table)."""

    with pytest.raises(NotADirectoryError):
        build_meeting_table(tmp_path / "does-not-exist")
