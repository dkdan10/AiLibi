"""The gameplay extractor's genuine-class self-check compares like with like, and bites.

``audits/workflows/extract_gameplay_facts.py`` folds its own genuine-class
supplied/converted pair and cross-checks it against the shipped
``eval.vote_correctness.compute_genuine_class_conversion`` over the same bytes,
writing the verdict as one of its self-checks. ``experiments/lab/rubric_score.py``
floors EVERY game's interestingness score to zero on any failing self-check, so
this one line decides whether the served rubric, the Highlights surface and the
demo bundle carry scores or zeros.

The shipped metric reads each meeting's RECORDED flags: the recording-time
detector held private grounding channels the transcript does not keep, so a
transcript-only re-run mints flags the game never had. The extractor used to
carry exactly that re-run, a replica of the definition the shipped metric
dropped, and the check failed on every set recorded since. The extractor now
reads the record through the one-home ``genuine_class_subjects``.

The extractor reads only recordings made without experiment settings, so since
the promotion of candidate round 2 (2026-10-02) it refuses the shown
``samples/9p2i`` set by name (pinned below) and that set ships no rubric. The
three cases run the real extractor over the baseline-9 era's nine-player set,
``ml_corpus/9p2i``, which it reads (read only; nothing under it is written):

* at head the check passes and no self-check fails (green);
* the historical replica planted in place of the one-home rule turns it red
  with the exact disagreement that floored the committed rubric;
* a one-pair perturbation of the shipped side turns it red by exactly that
  pair, whichever bytes are committed, so the gate tolerates no slack.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any

import pytest

from eval.report_schema import MeetingReport
from eval.vote_correctness import (
    GenuineClassConversionReport,
    compute_genuine_class_conversion,
)
from experiments.lab.rubric_score import _facts_integrity_ok, interestingness
from meetings.transcript import (
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_PROXY_INTRA_TURN,
    WEAK_REASON_RETARGETED_PROXY,
    detect_contradictions,
)

# Imported dynamically for the reason tests/experiments/
# test_gameplay_facts_suspicion_row.py gives: audits/workflows/ is not a package.
_facts: Any = importlib.import_module("audits.workflows.extract_gameplay_facts")

_GENUINE_CHECK = "re-derived genuine-class == shipped compute_genuine_class_conversion"


def _transcript_rerun_subjects(meeting: MeetingReport) -> frozenset[str]:
    """The replica the extractor carried before reading the record (PLANTED).

    Re-runs the detector over the transcript under the ballot-voter roster alone
    and keeps the non-endpoint, non-proxy ``alibi_vs_sighting`` subjects — the
    pre-record definition, kept here only to prove the self-check fails on it.
    """

    roster = frozenset(ballot.voter for ballot in meeting.ballots)
    subjects: set[str] = set()
    for flag in detect_contradictions(meeting.transcript, roster=roster):
        if flag.kind != "alibi_vs_sighting":
            continue
        if WEAK_REASON_ENDPOINT_TICK in flag.description:
            continue
        if WEAK_REASON_RETARGETED_PROXY in flag.description:
            continue
        if WEAK_REASON_PROXY_INTRA_TURN in flag.description:
            continue
        subjects.update(flag.subjects)
    return frozenset(subjects)


def _shipped_plus_one_pair(report: Any) -> GenuineClassConversionReport:
    """The shipped fold with one extra supplied-and-converted pair (PERTURBED)."""

    real = compute_genuine_class_conversion(report)
    supplied = real.supplied + 1
    converted = real.converted + 1
    return GenuineClassConversionReport(
        supplied=supplied,
        converted=converted,
        conversion_rate=converted / supplied,
    )


#: The committed nine-player set the extractor reads (the baseline-9 era).
_READ_SET = Path(__file__).resolve().parents[2] / "replays" / "ml_corpus" / "9p2i"


def test_the_extractor_refuses_the_promoted_set_by_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    with pytest.raises(
        SystemExit,
        match="this extractor reads only recordings made without experiment settings",
    ):
        _facts.main()
    assert not (tmp_path / "ailibi-gameplay-facts-9p2i.json").exists()


def _extract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the extractor over the read nine-player set; return (facts, summary)."""

    monkeypatch.setattr(_facts, "SAMPLE_DIR", _READ_SET)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    assert _facts.main() == 0
    summary: dict[str, Any] = json.loads(capsys.readouterr().out)
    facts_path = tmp_path / "ailibi-gameplay-facts-9p2i.json"
    facts: dict[str, Any] = json.loads(facts_path.read_text(encoding="utf-8"))
    return facts, summary


def _genuine_line(facts: dict[str, Any]) -> str:
    lines: list[str] = [c for c in facts["self_checks"] if c.startswith(_GENUINE_CHECK)]
    assert len(lines) == 1, facts["self_checks"]
    return lines[0]


def _crosscheck(facts: dict[str, Any]) -> dict[str, Any]:
    block: dict[str, Any] = facts["aggregates"]["wave1_decomposition"][
        "genuine_class_crosscheck"
    ]
    return block


def _genuine_findings(summary: dict[str, Any]) -> list[str]:
    return [
        f["severity"] for f in summary["findings"] if f["id"] == "GENUINE-CROSSCHECK"
    ]


def test_the_extractor_reads_the_record_and_every_self_check_passes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    facts, summary = _extract(tmp_path, monkeypatch, capsys)

    assert _genuine_line(facts).endswith(": OK")
    block = _crosscheck(facts)
    assert block["match"] is True
    assert (block["rederived_supplied"], block["rederived_converted"]) == (
        block["shipped_supplied"],
        block["shipped_converted"],
    )
    assert _genuine_findings(summary) == []
    # No self-check fails, so the rubric keeps its dimensions.
    assert not any("FAIL" in check for check in facts["self_checks"])
    assert _facts_integrity_ok(facts) is True


def test_a_transcript_rerun_in_place_of_the_record_fails_the_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(_facts, "genuine_class_subjects", _transcript_rerun_subjects)
    facts, summary = _extract(tmp_path, monkeypatch, capsys)

    # The re-run mints genuine flags the record does not carry: on the corpus
    # nine-player set it supplies 12 where the record supplies 1. (On the
    # baseline-9 samples bytes the exact line that floored the committed rubric
    # read "(supplied 1/0, converted 1/0)", a flag naming an impostor the first
    # meeting of seed 7 ejected.) A re-record that removes the divergence
    # re-anchors this exhibit on its own bytes.
    assert _genuine_line(facts).endswith("(supplied 12/1, converted 4/1): FAIL")
    assert _crosscheck(facts)["match"] is False
    assert _genuine_findings(summary) == ["blocking"]
    assert _facts_integrity_ok(facts) is False
    # One failing self-check floors every game, whatever its dimensions.
    rows = interestingness(facts)["per_game"]
    assert len(rows) == 150
    assert all(row["score"] == 0.0 for row in rows)


def test_one_pair_of_disagreement_fails_the_check_by_exactly_that_pair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        _facts, "compute_genuine_class_conversion", _shipped_plus_one_pair
    )
    facts, summary = _extract(tmp_path, monkeypatch, capsys)

    assert _genuine_line(facts).endswith(": FAIL")
    block = _crosscheck(facts)
    assert block["match"] is False
    assert block["shipped_supplied"] - block["rederived_supplied"] == 1
    assert block["shipped_converted"] - block["rederived_converted"] == 1
    assert _genuine_findings(summary) == ["blocking"]
    assert _facts_integrity_ok(facts) is False
