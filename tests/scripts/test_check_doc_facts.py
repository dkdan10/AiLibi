"""Unit tests for scripts/check_doc_facts.py (Task 19.1).

The checker's contract is two-sided: it must pass on the committed front door
(so it can sit in a gate) and it must fail, naming the drifted fact, on every
drift class it guards. The fixture stands up a tmp tree holding exactly the
files the checker reads, and one test per perturbation asserts both the failure
and that the message names the right fact — a checker that fails for the wrong
reason is as useless as one that passes.

The substrate-lever registry is never copied: ``check_doc_facts`` always reads
it from the live ``orchestrator.replay`` import, so a perturbed .env.example is
checked against the levers this build actually ships.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

import check_doc_facts

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "check_doc_facts.py"


@pytest.mark.parametrize(
    "example",
    [
        "`[example](missing.md)`",
        "``[example](missing.md) with ` inside``",
        "`a multiline\n[example](missing.md) code span`",
        "```md\n[example](missing.md)\n```",
        "~~~md\n[example](missing.md)\n~~~~",
        "````md\n```\n[example](missing.md)\n````",
        "```md\n[example](missing.md)\n",
        "> ```md\n> [example](missing.md)\n",
        "    [example](missing.md)",
        r"\\`[example](missing.md)`",
    ],
)
def test_relative_links_ignore_code_examples(tmp_path: Path, example: str) -> None:
    text = f"[real](actual.md)\n\n{example}"
    assert list(check_doc_facts.relative_targets(tmp_path, "docs/page.md", text)) == [
        ("actual.md", tmp_path / "docs" / "actual.md")
    ]


def test_relative_links_retain_broken_links_after_code(tmp_path: Path) -> None:
    text = "`[example](ignored.md)` then [broken](missing.md)"
    assert list(check_doc_facts.relative_targets(tmp_path, "page.md", text)) == [
        ("missing.md", tmp_path / "missing.md")
    ]


@pytest.mark.parametrize(
    "text",
    [
        "`unmatched\n\n[broken](missing.md)\n\n`later`",
        "`unmatched\n# Heading\n[broken](missing.md)\n`later`",
        "`unmatched\n- [broken](missing.md)\n\n`later`",
        r"\`[broken](missing.md)`",
        "[broken][ref]\n\n[ref]: missing.md",
    ],
)
def test_relative_links_preserve_rendered_links(tmp_path: Path, text: str) -> None:
    assert list(check_doc_facts.relative_targets(tmp_path, "page.md", text)) == [
        ("missing.md", tmp_path / "missing.md")
    ]


def test_relative_links_decode_paths_and_include_images(tmp_path: Path) -> None:
    text = '[space](<two words.md>) ![image](pic.png "caption")'
    assert list(check_doc_facts.relative_targets(tmp_path, "page.md", text)) == [
        ("two%20words.md", tmp_path / "two words.md"),
        ("pic.png", tmp_path / "pic.png"),
    ]


# Exactly the files the checker reads, in their relative layout so the tmp tree
# is a faithful (and perturbable) stand-in for a checkout.
_COPIED = (
    "README.md",
    ".env.example",
    "replays/samples/4p1i/MANIFEST.md",
    "replays/samples/9p2i/MANIFEST.md",
    "audits/audit-phase-18-close.md",
    "audits/audit-phase-19-close.md",
    # The three audits the checker actually reads: the fixture stands every
    # other audits/*.md up EMPTY, so these are copied whole. The ladder tip
    # publishes the current record's cells, the baseline-7 record the history
    # column's, and the adopting record the four bars its verdict table decided.
    "audits/audit-phase-21-rerecord.md",
    "audits/audit-phase-20-baseline-7.md",
    "audits/audit-phase-21-adopting-record.md",
    # ...and the memo that registered the four targets before the bytes
    # existed, which the adopting record's copies of them are held to.
    "audits/audit-phase-21-preregistration.md",
    "eval/vote_correctness.py",
    "replays/samples/4p1i/tournament-eval-report.json",
    "replays/samples/9p2i/tournament-eval-report.json",
    "replays/ml_corpus/4p1i/tournament-eval-report.json",
    "replays/ml_corpus/9p2i/tournament-eval-report.json",
    "replays/ml_corpus/4p1i/MANIFEST.md",
    "replays/ml_corpus/9p2i/MANIFEST.md",
    "docs/glossary.md",
    "docs/history.md",
    "docs/reading-guide.md",
    "audits/README.md",
    "replays/ml_corpus/README.md",
    "tests/eval/test_vj_instruments.py",
    "tests/eval/test_deduction_metrics.py",
    "frontend/src/components/ReplayPicker.tsx",
    "docs/ml-program.md",
    "training/reports/results-finalist-eval.jsonl",
    # The two published pages and the phase contract the review index's
    # acted-on map is resolved against.
    "docs/lessons.md",
    "audits/review-2026-08-19/README.md",
    "tasks/phase-20.md",
)

# The front-door checks also ENUMERATE paths whose contents they never open:
# the phase contracts, the audit corpus, and every relative link target. The
# fixture stands those up as empty files (directories as directories) so the
# tmp tree answers the same questions the checkout does, without copying the
# ~5 MB of prose behind them into every test.
_ENUMERATED_GLOBS = (
    ("tasks", "phase-*.md"),
    ("audits", "*.md"),
    # The committed replays are counted, never opened: the results row saying
    # 100 of 100 reconstruct is re-derived from how many there are.
    ("replays/samples/4p1i", "*.jsonl"),
    ("replays/samples/9p2i", "*.jsonl"),
)

# Above this size a fixture entry is symlinked rather than copied: the four
# committed eval reports total >100 MB, and every test gets its own tree. Every
# writer here REPLACES a fixture file (``_write`` unlinks first), so a link is
# never followed back into the checkout.
_LINK_ABOVE_BYTES = 1_000_000

_README = "README.md"
_ENV_EXAMPLE = ".env.example"
_MANIFEST_4P1I = "replays/samples/4p1i/MANIFEST.md"
_MANIFEST_9P2I = "replays/samples/9p2i/MANIFEST.md"
_TOGGLE_EXAMPLE_LINE = "# AILIBI_IMPOSTOR_ROLL_CALL=0"
_VOTE_CORRECTNESS = "eval/vote_correctness.py"
_EVAL_REPORT_9P2I = "replays/samples/9p2i/tournament-eval-report.json"
_EVAL_REPORT_4P1I = "replays/samples/4p1i/tournament-eval-report.json"
_ML_CORPUS_MANIFEST_9P2I = "replays/ml_corpus/9p2i/MANIFEST.md"
_GLOSSARY = "docs/glossary.md"
_HISTORY = "docs/history.md"
_READING_GUIDE = "docs/reading-guide.md"
_CITATION_INSTRUMENT = "tests/eval/test_vj_instruments.py"
_AUDITS_INDEX = "audits/README.md"
_LESSONS = "docs/lessons.md"
_CORPUS_README = "replays/ml_corpus/README.md"
# A well-formed ``public_response_coverage`` block for the hand-written eval
# reports the trigger cases use, so each of them perturbs one thing only.
_COVERAGE_BLOCK = {
    "crew_turns": 2,
    "crew_turns_with_whereabouts": 2,
    "impostor_turns": 1,
    "impostor_turns_with_whereabouts": 0,
}
_REVIEW_INDEX = "audits/review-2026-08-19/README.md"
# One acted-on map row, cell by cell: the finding, the task credited with
# closing it, and the pull request that carries the change.
_MAP_FINDING = "`C-31`"
_MAP_TASK_CELL = "| 20.8 |"
# A finding the index names ONLY in its map row, so deleting that row really
# does remove it from the document (C-31 is also named in the severity block).
_MAP_ONLY_FINDING = "`C-9`"
# The record the history column is history OF: the recording the current one
# replaced, read through the same bar sections as the current one.
_PROOF_AUDIT = "audits/audit-phase-20-baseline-7.md"
_PROOF_ACCURACY_HEADING = "### Bar 1 — I-1 non-direct conviction accuracy: **MISSED**"
_PROOF_ACCURACY_POOLED = (
    "| **pooled** | **46/125 = 0.3680** [0.2886, 0.4553] | "
    "**61/103 = 0.5922** [0.4957, 0.6822] |"
)
_PROOF_INNOCENT_POOLED = "| **pooled** | **79** | **42** |"
_PROOF_DIRECT_POOLED = "**326/326 = 1.000** pooled"
# The record whose pre-registered rule DECIDED, and the four rows of its verdict
# table the front door quotes. Each drifted twin moves one cell only.
_FINDING_AUDIT = "audits/audit-phase-21-adopting-record.md"
# ...and the memo that registered its four targets, and bar 1's per-set floor
# and power threshold, before a byte of it existed.
_PREREGISTRATION_AUDIT = "audits/audit-phase-21-preregistration.md"
_FINDING_ACCURACY_ROW = (
    "| 1 | `EjecteeProofCrossTab.non_direct_accuracy` pooled | "
    "≥ 0.60, no powered set < 0.50 | 50/96 = 0.5208 | 46/66 = 0.6970 | **MET** |"
)
_FINDING_ACCURACY_DRIFTED = _FINDING_ACCURACY_ROW.replace(
    "46/66 = 0.6970", "45/66 = 0.6818"
)
_FINDING_INNOCENT_ROW = (
    "| 2 | `MeetingFlagCrossTab` innocent ejections pooled | < 35 | 46 | 20 | **MET** |"
)
_FINDING_INNOCENT_DRIFTED = _FINDING_INNOCENT_ROW.replace("| 20 |", "| 19 |")
_FINDING_REPORTER_ROW = (
    "| 3 | `reporter_innocent_ejections` pooled | ≤ 12 | 34 | 11 | **MET** |"
)
_FINDING_REPORTER_DRIFTED = _FINDING_REPORTER_ROW.replace("| 11 |", "| 10 |")
_FINDING_SHARE_ROW = (
    "| 4 | `reporter_share_of_innocent_ejections` pooled | < 0.40 | "
    "34/46 = 0.7391 | 11/20 = 0.5500 | **MISSED** |"
)
_FINDING_SHARE_DRIFTED = _FINDING_SHARE_ROW.replace("11/20 = 0.5500", "9/20 = 0.4500")
# Bar 1's own section: the powered per-set row its second clause is about, and
# the pooled row the verdict table summarises.
_FINDING_POWERED_SET_ROW = (
    "| `ml_corpus/9p2i` | 32/61 = 0.5246 | 36/51 = 0.7059 (n = 51, **POWERED**) |"
)
_FINDING_ACCURACY_SECTION_POOLED = "| pooled | 50/96 = 0.5208 | **46/66 = 0.6970** |"
_FINDING_INNOCENT_SECTION_POOLED = "| pooled | 46 | **20** |"
# The history cell both front-door tables carry for the conviction partition.
_PREVIOUS_PARTITION_CELL = "326 / 326 = 1.0000 vs 61 / 103 = 0.5922"
_ML_PAGE = "docs/ml-program.md"
_ML_ARM_ROW = "| `ea4bc955…` (put to the bar) | 26/50 = 0.52 | 13/50 = 0.26 |"
_ML_DROPPED_ARM_ROW = (
    "| `bfd145cb…` | 28/50 = 0.56 | 13/50 = 0.26 | **0.0041** | **FAIL** |\n"
)
_ML_COMPARATOR_ROW = "| `p18-fsm-comparator` (scripted) | 13/50 = 0.26 |"
_PICKER = "frontend/src/components/ReplayPicker.tsx"
_DEDUCTION_INSTRUMENT = "tests/eval/test_deduction_metrics.py"
# The record that adopted the current recording: the ladder tip, the
# pre-registered bar read the results row publishes, and the win split whose
# before column the front door quotes.
_LADDER_TIP_AUDIT = "audits/audit-phase-21-rerecord.md"
_CITATION_ROW_CLAIM = (
    "Eject ballots carrying a valid citation, a turn or an observation id (9p2i)"
)
# The reading guide's §3 cross-tab, as committed.
_FLAGGED_ROW = "| yes (68 meetings) | 68 | 0 |"
_UNFLAGGED_ROW = "| no (83 meetings) | 14 | 13 |"
# The one dialect term the front door keeps, and the link that defines it. Its
# first use is the results table's before-column header.
_BASELINE_LINK = "[baseline 7](docs/glossary.md#baseline-n-the-reference-recording)"
_BEFORE_COLUMN_LINK = (
    "[At baseline 7](docs/glossary.md#baseline-n-the-reference-recording)"
)
_BASELINE_ANCHOR_HEADING = "### baseline N (the reference recording)"
# "ladder tip" is private dialect too, so a planted ladder-tip sentence has to
# carry its glossary link — otherwise the dialect check fires alongside the
# ladder-tip check and the perturbation stops being about one thing.
_LADDER_TIP_LINK = (
    "[ladder tip](docs/glossary.md#the-ladder-tip-the-newest-reference-recording)"
)


@pytest.fixture
def doc_tree(tmp_path: Path) -> Path:
    """A tmp checkout holding only the documents the checker reads."""

    for relative in _COPIED:
        source = _REPO_ROOT / relative
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.stat().st_size > _LINK_ABOVE_BYTES:
            destination.symlink_to(source)
        else:
            destination.write_bytes(source.read_bytes())
    _stand_in_enumerated_paths(tmp_path)
    return tmp_path


def _stand_in_enumerated_paths(root: Path) -> None:
    """Empty stand-ins for the paths the checks stat but never read.

    Derived from the checkout and from the checker's own link parser, so the
    fixture cannot drift from what the checks look for: a link added to the
    front door stands itself up here on the next run.
    """

    wanted: set[str] = set()
    for directory, pattern in _ENUMERATED_GLOBS:
        wanted.update(
            f"{directory}/{path.name}"
            for path in (_REPO_ROOT / directory).glob(pattern)
        )
    wanted.update(
        f"audits/{child.name}/"
        for child in (_REPO_ROOT / "audits").iterdir()
        if child.is_dir()
    )
    for document in (
        check_doc_facts._LINKED_DOCUMENTS + check_doc_facts._PUBLISHED_DOCUMENTS
    ):
        text = (root / document).read_text(encoding="utf-8")
        for _, resolved in check_doc_facts.relative_targets(_REPO_ROOT, document, text):
            relative = resolved.relative_to(_REPO_ROOT).as_posix()
            wanted.add(f"{relative}/" if resolved.is_dir() else relative)

    for relative in sorted(wanted):
        destination = root / relative.rstrip("/")
        if relative.endswith("/"):
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.touch()


def _read(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _write(root: Path, relative: str, text: str) -> None:
    # Replace, never open in place: a large fixture entry is a symlink into the
    # checkout, and an in-place write would perturb the committed file.
    path = root / relative
    path.unlink(missing_ok=True)
    path.write_text(text, encoding="utf-8")


def _map_row(index: str, finding: str) -> str:
    """The acted-on map row for ``finding`` (backticked), asserting it is there."""

    rows = [line for line in index.splitlines() if line.startswith(f"| {finding} |")]
    assert len(rows) == 1, f"{finding} is not mapped exactly once"
    return rows[0]


def _substitute(root: Path, relative: str, old: str, new: str) -> None:
    """Rewrite ``old`` -> ``new``, asserting the perturbation actually landed."""

    text = _read(root, relative)
    assert old in text, f"{relative} no longer contains {old!r}"
    _write(root, relative, text.replace(old, new))


def test_committed_front_door_passes() -> None:
    assert check_doc_facts.check_facts(_REPO_ROOT) == []


def test_unperturbed_copy_passes(doc_tree: Path) -> None:
    # Guards the fixture itself: every later failure must come from the
    # perturbation, not from a file the copy forgot.
    assert check_doc_facts.check_facts(doc_tree) == []


def test_stale_sample_date_detected(doc_tree: Path) -> None:
    # (a) The pre-19.1 README claimed the baseline-5-era refresh date. Every
    # place the README dates the current recording is held to the manifests,
    # so a blanket rewrite is named once per claim rather than once per file.
    _substitute(doc_tree, _README, "2026-08-31", "2026-08-19")
    errors = check_doc_facts.check_facts(doc_tree)
    assert all(_README in error for error in errors)
    paragraph = [error for error in errors if "refresh date '2026-08-31'" in error]
    assert len(paragraph) == 1
    dated = [
        error for error in errors if "dates the current reference recording" in error
    ]
    assert len(dated) == len(errors) - 1 >= 1


def test_paragraph_date_drift_not_alibied_elsewhere(doc_tree: Path) -> None:
    # The provenance claim is bound to its paragraph: the correct date
    # appearing somewhere else in the file must not satisfy a drifted
    # paragraph (the pre-hardening checker accepted exactly this).
    _substitute(doc_tree, _README, "regenerated 2026-08-31", "regenerated 2026-08-19")
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README)
        + "\nAn unrelated historical note mentioning 2026-08-31.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        "'regenerated 2026-08-19'" in error and "refresh date '2026-08-31'" in error
        for error in errors
    )
    # The same clause is a dated claim wherever it appears, so the widened
    # scan names it a second time, by line.
    assert any(
        "'regenerated 2026-08-19' dates the current reference recording" in error
        for error in errors
    )


def test_duplicate_stale_date_clause_detected(doc_tree: Path) -> None:
    # Every regenerated-date clause in the paragraph must match — a stale
    # duplicate beside the correct clause is drift, same as the win rates.
    _substitute(
        doc_tree,
        _README,
        "regenerated 2026-08-31",
        "regenerated 2026-08-31 (an earlier draft said regenerated 2026-08-19)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        "'regenerated 2026-08-19'" in error and "refresh date '2026-08-31'" in error
        for error in errors
    )
    assert any(
        "'regenerated 2026-08-19' dates the current reference recording" in error
        for error in errors
    )


def test_wrong_total_sample_count_detected(doc_tree: Path) -> None:
    # The paragraph's total-replay count is a manifest fact too: the expected
    # claim is missing AND the drifted one contradicts the row totals.
    _substitute(doc_tree, _README, "100 sample replays", "80 sample replays")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'100 sample replays'" in errors[0]
    assert "'80 sample replays'" in errors[1]


def test_wrong_tournament_size_detected(doc_tree: Path) -> None:
    # As is the per-set tournament size — both facets reported.
    _substitute(doc_tree, _README, "50-game", "40-game")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'50-game'" in errors[0]
    assert "'40-game'" in errors[1]


def test_stale_count_beside_correct_detected(doc_tree: Path) -> None:
    # A contradictory count clause beside the correct substring is drift —
    # every count-shaped claim in the paragraph is held to the row totals.
    _substitute(
        doc_tree,
        _README,
        "two 50-game tournaments",
        "one stale 40-game tournament and one 50-game tournament",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'40-game'" in errors[0]


def test_wrong_recording_model_detected(doc_tree: Path) -> None:
    # The recording model named in the paragraph is a manifest fact.
    _substitute(
        doc_tree,
        _README,
        "against `Qwen/Qwen3.6-27B`",
        "against `Qwen/Qwen3-32B`",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'Qwen/Qwen3.6-27B'" in errors[0]
    assert "`model` column" in errors[0]


def test_wrong_prompt_set_version_detected(doc_tree: Path) -> None:
    # As is the prompt-set version token the prompt_versions column records.
    _substitute(
        doc_tree,
        _README,
        "`qwen3_6_27b` `v5` prompt set",
        "`qwen3_6_27b` `v2` prompt set",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'v5'" in errors[0]
    assert "`prompt_versions` column" in errors[0]


def test_missing_provenance_paragraph_fails_loud(doc_tree: Path) -> None:
    # Losing the paragraph anchor is format drift, not a vacuous pass.
    _substitute(doc_tree, _README, "regenerated 2026-08-31", "refreshed 2026-08-31")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "exactly one sample-provenance paragraph" in errors[0]


def test_repeated_claims_survive_a_lost_provenance_paragraph(doc_tree: Path) -> None:
    # ...and it must not take the rest of the front door's gate down with it:
    # the other documents repeat these facts on their own account.
    _substitute(doc_tree, _README, "regenerated 2026-08-31", "refreshed 2026-08-31")
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| 36% (4p1i), 30% (9p2i) |",
        "| 36% (4p1i), 22% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("exactly one sample-provenance paragraph" in error for error in errors)
    assert any(
        error.startswith(_READING_GUIDE) and "claim '22% (9p2i)' disagrees" in error
        for error in errors
    )


def test_wrong_win_rate_detected(doc_tree: Path) -> None:
    # (b) A win rate that no longer matches the manifest it is drawn from:
    # the paragraph misses the expected substring AND carries a claim that
    # contradicts the manifest — both are reported.
    _substitute(doc_tree, _README, "rates 36% (4p1i)", "rates 30% (4p1i)")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any("'36% (4p1i)'" in error and "18/50" in error for error in errors)
    assert any("claim '30% (4p1i)' disagrees" in error for error in errors)


def test_stale_ladder_tip_sentence_detected(doc_tree: Path) -> None:
    # (c) The pre-19.1 README claimed the baseline-5 sets were still the tip.
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README)
        + f"\nThe baseline-5 sets remain the {_LADDER_TIP_LINK}.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names baseline 5" in errors[0]
    assert "ladder tip at baseline 8" in errors[0]


def test_stray_win_rate_claim_detected(doc_tree: Path) -> None:
    # A wrong rate claim OUTSIDE the provenance paragraph is drift too — the
    # paragraph being right must not license a false claim elsewhere.
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README)
        + "\nHistorically the impostors held 36% (9p2i) of the games.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "win-rate claim '36% (9p2i)'" in errors[0]
    assert "15/50 = 30%" in errors[0]


def test_in_paragraph_stale_claim_detected(doc_tree: Path) -> None:
    # The correct substring being present must not exempt the paragraph's
    # OTHER claims: a stale duplicate beside the correct value is drift.
    _substitute(
        doc_tree,
        _README,
        "36% (4p1i) and 30% (9p2i)",
        "36% (4p1i) and 30% (9p2i) (an earlier draft misquoted 25% (9p2i))",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "win-rate claim '25% (9p2i)' disagrees" in errors[0]
    assert "15/50 = 30%" in errors[0]


def test_long_ladder_tip_sentence_detected(doc_tree: Path) -> None:
    # The scan covers the WHOLE sentence: a baseline mention more than 120
    # characters from the "ladder tip" phrase (the pre-hardening window cap)
    # is still the same claim.
    # One long hyphenated token rather than a run of words: what this exercises
    # is the DISTANCE in characters, and the README sits close enough to its
    # word ceiling that padding it with prose would fire a second, unrelated
    # error and stop the perturbation being about one thing.
    filler = "and-the-qualifying-clauses-go-on-" * 4
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README)
        + f"\nThe baseline-5 sets, {filler}remain the {_LADDER_TIP_LINK}.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names baseline 5" in errors[0]


def test_ladder_tip_sentence_without_baseline_detected(doc_tree: Path) -> None:
    # A ladder-tip claim that names no baseline at all is unverifiable prose
    # on the one fact this checker exists to pin; require the tip by name.
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README) + f"\nThese sets remain the {_LADDER_TIP_LINK}.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names no baseline at all" in errors[0]
    assert "baseline 8" in errors[0]


def test_missing_live_toggle_example_detected(doc_tree: Path) -> None:
    # (d) The one live toggle stops being documented at all.
    _substitute(doc_tree, _ENV_EXAMPLE, _TOGGLE_EXAMPLE_LINE + "\n", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'impostor_roll_call'" in errors[0]
    assert "AILIBI_IMPOSTOR_ROLL_CALL" in errors[0]


def test_uncommented_live_toggle_example_detected(doc_tree: Path) -> None:
    # The example must stay COMMENTED: an active assignment in a copied .env
    # would flip the substrate away from the committed baseline-6 record.
    # Both facets are reported: the commented example is gone AND an active
    # export is present.
    _substitute(
        doc_tree, _ENV_EXAMPLE, _TOGGLE_EXAMPLE_LINE, "AILIBI_IMPOSTOR_ROLL_CALL=0"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "no commented example line" in errors[0]
    assert f"'{_TOGGLE_EXAMPLE_LINE}'" in errors[0]
    assert "active export" in errors[1]


def test_active_toggle_export_beside_example_detected(doc_tree: Path) -> None:
    # Keeping the required commented example does not license an ADDITIONAL
    # active export of the same toggle.
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        _TOGGLE_EXAMPLE_LINE,
        _TOGGLE_EXAMPLE_LINE + "\nAILIBI_IMPOSTOR_ROLL_CALL=1",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "active export of live toggle 'impostor_roll_call'" in errors[0]


def test_retired_lever_assignment_detected(doc_tree: Path) -> None:
    # (e) A graduated lever handed back out as a knob this build cannot read.
    _write(
        doc_tree,
        _ENV_EXAMPLE,
        _read(doc_tree, _ENV_EXAMPLE) + "AILIBI_CITATION_GATE=0\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'AILIBI_CITATION_GATE='" in errors[0]
    assert "'citation_gate'" in errors[0]


def test_unknown_substrate_knob_detected(doc_tree: Path) -> None:
    # An assignment in the belief-substrate section whose key is not in the
    # registry at all — misspelled, or never registered — is a no-op knob and
    # must be rejected, not silently skipped by the known-keys iteration.
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        _TOGGLE_EXAMPLE_LINE,
        _TOGGLE_EXAMPLE_LINE + "\n# AILIBI_STALE_SUBSTRATE_KNOB=0",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'AILIBI_STALE_SUBSTRATE_KNOB='" in errors[0]
    assert "not in the live lever registry" in errors[0]


def test_missing_lever_section_banner_detected(doc_tree: Path) -> None:
    # The section audit fails loud when the banner it keys on disappears,
    # rather than silently auditing nothing.
    _substitute(doc_tree, _ENV_EXAMPLE, "# Belief-substrate levers", "# Levers")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'# Belief-substrate levers'" in errors[0]
    assert "cannot be located" in errors[0]


def test_missing_retired_lever_key_detected(doc_tree: Path) -> None:
    # (f) A graduated lever dropped from the note, so a reader cannot map a
    # recording's stamped flag back to anything documented.
    _substitute(doc_tree, _ENV_EXAMPLE, "movement_perception", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'movement_perception'" in errors[0]
    assert "graduated-levers note" in errors[0]


def test_graduated_mention_outside_note_does_not_count(doc_tree: Path) -> None:
    # The graduated label lives in the belief-substrate section's note — a
    # historical mention elsewhere in the file must not stand in for it.
    _substitute(doc_tree, _ENV_EXAMPLE, "movement_perception", "")
    _write(
        doc_tree,
        _ENV_EXAMPLE,
        _read(doc_tree, _ENV_EXAMPLE)
        + "\n# Historical note: movement_perception was measured in Phase 13.5.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'movement_perception'" in errors[0]
    assert "graduated-levers note" in errors[0]


# The first line of the first live-toggle paragraph in the belief-substrate
# section — an anchor for planting an aside ABOVE the toggles, named here so a
# reworded heading is a one-line fix rather than a hunt through the assertions.
_TOGGLE_PARAGRAPH_HEADING = "# The Phase-18 impostor-answer template arm"


def test_graduated_aside_inside_section_does_not_count(doc_tree: Path) -> None:
    # Tighter still: a mention inside the SECTION but outside the graduated
    # NOTE (a historical aside before the toggle paragraph) must not stand in
    # for the note's graduated/always-ON label either.
    _substitute(doc_tree, _ENV_EXAMPLE, "movement_perception", "")
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        _TOGGLE_PARAGRAPH_HEADING,
        "# Historical aside: movement_perception was once default-OFF.\n\n"
        + _TOGGLE_PARAGRAPH_HEADING,
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'movement_perception'" in errors[0]
    assert "graduated-levers note" in errors[0]


def test_graduated_note_wording_drift_detected(doc_tree: Path) -> None:
    # Listing every key is not enough: the note's WORDING is the label. If it
    # stops saying always-ON or drifts back to default-OFF phrasing, both
    # facets are reported.
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        "# GRADUATED LEVERS — always ON, nothing to set.",
        "# GRADUATED LEVERS — default OFF pending re-record.",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "no longer says 'always ON'" in errors[0]
    assert "'default OFF'" in errors[1]
    assert "graduation-sweep convention" in errors[1]


def test_missing_graduated_note_marker_detected(doc_tree: Path) -> None:
    # Losing the note's marker is format drift, not a silent skip.
    _substitute(doc_tree, _ENV_EXAMPLE, "# GRADUATED LEVERS", "# RETIRED LEVERS")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'# GRADUATED LEVERS'" in errors[0]


def test_toggle_example_outside_section_does_not_count(doc_tree: Path) -> None:
    # The commented example must live in the belief-substrate section — the
    # place a reader copying the lever config actually looks; the same line
    # in an appendix elsewhere must not satisfy the check.
    _substitute(doc_tree, _ENV_EXAMPLE, _TOGGLE_EXAMPLE_LINE + "\n", "")
    _write(
        doc_tree,
        _ENV_EXAMPLE,
        _read(doc_tree, _ENV_EXAMPLE) + "\n" + _TOGGLE_EXAMPLE_LINE + "\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'impostor_roll_call'" in errors[0]
    assert "appears nowhere in the belief-substrate section" in errors[0]


def test_manifest_outcome_flip_detected(doc_tree: Path) -> None:
    # (g) The bytes move under the prose: one recorded winner cell flips, so
    # the re-derived rate slides 34% -> 32%; the README misses the new rate
    # AND its now-stale 34% claim contradicts the manifest in both of the
    # two places the rewritten front door states it.
    text = _read(doc_tree, _MANIFEST_4P1I)
    assert "| IMPOSTORS |" in text
    _write(doc_tree, _MANIFEST_4P1I, text.replace("| IMPOSTORS |", "| CREWMATES |", 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("'34% (4p1i)'" in error and "17/50" in error for error in errors)
    # Every document that repeats the rate names it, not README alone.
    stale = [error for error in errors if "claim '36% (4p1i)' disagrees" in error]
    assert {error.split(":")[0] for error in stale} == {
        _README,
        _READING_GUIDE,
        _ML_PAGE,
    }
    # ...and the record's own win-split table, which published the same cell,
    # is held to the bytes with them.
    assert any("the win-split table records 18/50 for 4p1i" in e for e in errors)
    assert len(errors) == len(stale) + 2


def test_unparseable_manifest_fails_loud(doc_tree: Path) -> None:
    # Format drift must not read as "no impostor wins recorded": a manifest
    # with no parseable rows is a hard failure, not a vacuous pass.
    # The win-rate check, the vote-correctness provenance check and the corpus
    # disclosures' substrate reconciliation all read this manifest, so all three
    # lose their source and all three must say so.
    # The 9p2i set is the one blanked because the 4p1i set carries the LATER
    # recording date: losing that one moves the re-derived refresh date as well,
    # and the perturbation would stop being about the unparseable manifest.
    _write(doc_tree, _MANIFEST_9P2I, "# Sample Replay Manifest\n\nno table here.\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 3
    assert all("parsed zero table rows" in error for error in errors)
    assert all(_MANIFEST_9P2I in error for error in errors)


def test_vote_correctness_stamp_drift_detected(doc_tree: Path) -> None:
    # The module's per-set stamp is bound to that set's committed report: a
    # numerator drifting away from the recorded one is named on both sides.
    _substitute(doc_tree, _VOTE_CORRECTNESS, "75/82 = 0.9146", "74/82 = 0.9024")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _VOTE_CORRECTNESS in errors[0]
    assert "replays/samples/9p2i" in errors[0]
    assert "74/82 = 0.9024" in errors[0]
    assert "records 75/82 = 0.9146" in errors[0]


def test_structural_pin_prose_detected(doc_tree: Path) -> None:
    # The claim this check exists to keep dead: a recorded set reading below
    # 1.0 refutes "structurally pinned", so reinstating the phrase must fail
    # with the phrase quoted back.
    _substitute(
        doc_tree,
        _VOTE_CORRECTNESS,
        "**``vote_correctness_rate`` is a diagnostic, NOT a KPI.**",
        "**``vote_correctness_rate`` is structurally pinned by the vote gate.**",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'structurally pinned'" in errors[0]
    assert "replays/samples/9p2i (75/82)" in errors[0]


def test_eval_report_rate_drift_detected(doc_tree: Path) -> None:
    # The rate is never a literal in the checker: it is re-derived from the
    # report's own two counts, so a rate field drifting away from them fails
    # with the set and both values named.
    _substitute(
        doc_tree,
        _EVAL_REPORT_9P2I,
        '"vote_correctness_rate": 0.9146341463414634',
        '"vote_correctness_rate": 0.99',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    # Twice over: the stamp check catches the rate contradicting its own
    # counts, and the README's real-report example no longer matches the
    # report it points a reader at.
    assert len(errors) == 2
    assert any(
        _EVAL_REPORT_9P2I in error and "75/82 = 0.9146" in error for error in errors
    )
    assert any("vote correctness 0.990" in error for error in errors)


def test_vote_correctness_provenance_drift_detected(doc_tree: Path) -> None:
    # A rate is only meaningful beside the substrate that produced it, so the
    # model the stamps are attributed to is the manifests' model, not prose.
    _substitute(doc_tree, _VOTE_CORRECTNESS, "Qwen/Qwen3.6-27B", "Qwen/Qwen3.5-9B")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _VOTE_CORRECTNESS in errors[0]
    assert "recording model 'Qwen/Qwen3.6-27B'" in errors[0]


def test_recorded_sets_disagreeing_on_the_substrate_fails_loud(
    doc_tree: Path,
) -> None:
    # One provenance line cannot describe two substrates: a set recorded on a
    # different model must fail rather than be papered over by whichever
    # manifest happened to be read first.
    _substitute(
        doc_tree, _ML_CORPUS_MANIFEST_9P2I, "Qwen/Qwen3.6-27B", "Qwen/Qwen3.5-9B"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "disagree on the recording model" in errors[0]
    assert "Qwen/Qwen3.5-9B" in errors[0]


def test_recorded_sets_disagreeing_on_substrate_flags_fails_loud(
    doc_tree: Path,
) -> None:
    # The flag stamp is part of the substrate the rates are attributed to: a
    # set recorded without one baseline-6 lever is a different substrate, even
    # when its model and prompt token still match. Two checks notice it from
    # their own angles: the sets no longer agree with each other, and the set no
    # longer carries a lever this build has graduated.
    _substitute(doc_tree, _ML_CORPUS_MANIFEST_9P2I, "absence_prior, ", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        "disagree on the substrate flags" in error and "absence_prior" in error
        for error in errors
    )
    assert any(
        "stamps graduated lever(s) ['absence_prior'] OFF" in error for error in errors
    )


def test_vote_correctness_baseline_attribution_drift_detected(doc_tree: Path) -> None:
    # The baseline the stamps are attributed to has a committed source too: a
    # rate hung on the wrong baseline is a wrong claim even when its
    # arithmetic checks out.
    _substitute(doc_tree, _VOTE_CORRECTNESS, "baseline-8", "baseline-5")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _VOTE_CORRECTNESS in errors[0]
    assert "'baseline-8'" in errors[0]


def test_zero_impostor_ejection_set_wants_an_undefined_rate_stamp(
    doc_tree: Path,
) -> None:
    # A set that ejected no impostor has an UNDEFINED rate, not a zero one.
    # The checker must accept the recording and demand the "n/a" stamp rather
    # than reject the set outright — a re-record could legitimately produce it.
    _substitute(
        doc_tree,
        _EVAL_REPORT_4P1I,
        '"impostor_ejections": 20,\n    "crewmate_ejections": 4,\n'
        '    "evidence_backed_impostor_ejections": 19,\n'
        '    "vote_correctness_rate": 0.95,',
        '"impostor_ejections": 0,\n    "crewmate_ejections": 4,\n'
        '    "evidence_backed_impostor_ejections": 0,\n'
        '    "vote_correctness_rate": null,',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "replays/samples/4p1i" in errors[0]
    assert "0/0 = n/a" in errors[0]


def test_provenance_token_elsewhere_does_not_alibi_the_lead_in(
    doc_tree: Path,
) -> None:
    # The substrate claims are bound to the paragraph directly above the
    # stamps: a correct model token surviving in an unrelated comment must not
    # satisfy a lead-in that names the wrong one.
    _substitute(
        doc_tree,
        _VOTE_CORRECTNESS,
        "model ``Qwen/Qwen3.6-27B``",
        "model ``Qwen/Qwen3.5-9B``",
    )
    _write(
        doc_tree,
        _VOTE_CORRECTNESS,
        _read(doc_tree, _VOTE_CORRECTNESS)
        + "\n# An unrelated note mentioning Qwen/Qwen3.6-27B.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "provenance lead-in" in errors[0]
    assert "recording model 'Qwen/Qwen3.6-27B'" in errors[0]


def test_set_supplying_no_prompt_provenance_fails_loud(doc_tree: Path) -> None:
    # A sibling manifest must not vouch for a set that records nothing: a
    # manifest whose prompt cells carry no dotted entry establishes no prompt
    # set, and the claim covers all four sets.
    text = _read(doc_tree, _ML_CORPUS_MANIFEST_9P2I)
    lines = [
        re.sub(r"\| [^|]*qwen3_6_27b[^|]*\|", "| no-meetings |", line)
        if "qwen3_6_27b" in line
        else line
        for line in text.splitlines(keepends=True)
    ]
    _write(doc_tree, _ML_CORPUS_MANIFEST_9P2I, "".join(lines))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _ML_CORPUS_MANIFEST_9P2I in errors[0]
    assert "records no prompt set on any row" in errors[0]


def test_evidence_count_above_its_denominator_fails_loud(doc_tree: Path) -> None:
    # More evidence-backed ejections than impostor ejections is the impossible
    # state VoteCorrectnessReport rejects; a corrupted report must fail here
    # rather than be documented as a valid measurement.
    _substitute(
        doc_tree,
        _EVAL_REPORT_9P2I,
        '"evidence_backed_impostor_ejections": 75,',
        '"evidence_backed_impostor_ejections": 92,',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _EVAL_REPORT_9P2I in errors[0]
    assert "no larger than impostor_ejections" in errors[0]


def test_eval_report_without_vote_correctness_block_fails_loud(
    doc_tree: Path,
) -> None:
    # Format drift must not read as "nothing to check": a report with no
    # vote_correctness block leaves both the stamps and the README's
    # real-report example sourceless, one with no public_response_coverage
    # block leaves the corpus coverage cells the same way, and one with no
    # meeting rows leaves the crew-triggered cell derived from nothing.
    _write(doc_tree, _EVAL_REPORT_9P2I, "{}\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 4
    assert all(_EVAL_REPORT_9P2I in error for error in errors)
    assert len([error for error in errors if '"vote_correctness":' in error]) == 2
    assert any('"public_response_coverage":' in error for error in errors)
    assert any("0 meeting rows" in error for error in errors)


def test_unlinked_dialect_term_detected(doc_tree: Path) -> None:
    # The one private-dialect term the front door keeps loses its glossary
    # link at its FIRST use — the results table's before-column header — so a
    # reader meets "baseline" with nowhere to look it up.
    _substitute(doc_tree, _README, _BEFORE_COLUMN_LINK, "At baseline 7")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'baseline'" in errors[0]
    assert "outside a glossary link" in errors[0]


def test_missing_glossary_entry_detected(doc_tree: Path) -> None:
    # The link survives, the entry it points at does not — the front door
    # sends the reader to an anchor that lands nowhere.
    _substitute(
        doc_tree, _GLOSSARY, _BASELINE_ANCHOR_HEADING, "### the reference recording"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _GLOSSARY in errors[0]
    assert "#baseline-n-the-reference-recording" in errors[0]


def test_glossary_entry_for_an_unused_term_still_required(doc_tree: Path) -> None:
    # The list is the set of words the front door may not use undefined, so the
    # entry has to exist whether or not README uses the term today — otherwise
    # deleting it quietly re-opens the door to the term.
    _substitute(doc_tree, _GLOSSARY, "### referee (the selection gate)", "### the gate")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "#referee-the-selection-gate" in errors[0]
    assert "whether or not README.md happens to use it" in errors[0]


def test_repeated_results_claim_detected(doc_tree: Path) -> None:
    # A stale row left beside a corrected one would otherwise satisfy the
    # row-by-row comparison while the page shows a reader two numbers.
    row = "| Committed sample replays that reconstruct byte-identically | 100 of 100 |"
    text = _read(doc_tree, _README)
    assert row in text
    stale = row.replace("| 100 of 100 |", "| 99 of 100 |")
    # The stale row carries an empty third cell rather than a worded one: the
    # README sits close enough to its word ceiling that a few words of padding
    # would fire a second, unrelated error beside the drift under test.
    _write(doc_tree, _README, text.replace(row, f"{stale}|\n{row}", 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 4
    assert (
        "states 'Committed sample replays that reconstruct byte-identically' twice"
        in (errors[0])
    )
    assert "'99 of 100'" in errors[1]
    # The stale copy is too narrow to reach the history column, so it has no
    # before cell at all — and the page then answers the history question two
    # ways as well.
    assert any("has no 'At baseline 7' cell" in error for error in errors)
    assert any("reads ''" in error for error in errors)


def test_new_undefined_dialect_term_detected(doc_tree: Path) -> None:
    # A term that is defined nowhere in the tree walks back onto the front
    # door — the drift class the glossary was written to end.
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README) + "\nEvery arm was priced by the referee.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any("'referee'" in error for error in errors)
    assert any("'arm'" in error for error in errors)


def test_replay_count_figure_derived_from_the_committed_replays(
    doc_tree: Path,
) -> None:
    # Agreement between the two tables cannot catch a figure edited identically
    # in both, so this row is recomputed from the replay files on disk.
    _substitute(doc_tree, _README, "| 100 of 100 |", "| 96 of 96 |")
    _substitute(doc_tree, _READING_GUIDE, "| 100 of 100 |", "| 96 of 96 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        "'96 of 96'" in error and "100 committed replays" in error for error in errors
    )
    # The edit also leaves the row claiming its figure moved from 100 to 96,
    # which nothing owns — the same drift read from the history column.
    assert any("states a moved figure" in error for error in errors)


def test_empty_replay_corpus_fails_loud(doc_tree: Path) -> None:
    # An empty corpus must not read as "nothing to re-derive": that would let
    # any replay figure stand.
    for name in ("4p1i", "9p2i"):
        for replay in (doc_tree / "replays" / "samples" / name).glob("*.jsonl"):
            replay.unlink()
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no committed replays found" in errors[0]


def test_citation_figure_derived_from_the_committed_instrument(
    doc_tree: Path,
) -> None:
    # Same for the citation row: its source is the instrument's pinned
    # assertions, not the other document's copy of the number.
    _substitute(
        doc_tree,
        _README,
        "| 526 / 527, zero dangling |",
        "| 525 / 526, zero dangling |",
    )
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| 526 / 527, zero dangling |",
        "| 525 / 526, zero dangling |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'525 / 526, zero dangling'" in errors[0]
    assert _CITATION_INSTRUMENT in errors[0]


def test_instrument_pin_move_reaches_the_front_door(doc_tree: Path) -> None:
    # The binding runs the other way too: a re-record that moves the pinned
    # count must move the documents, rather than leaving them stale and green.
    _substitute(
        doc_tree,
        _CITATION_INSTRUMENT,
        "assert nine.turn_citations_dangling == 0",
        "assert nine.turn_citations_dangling == 3",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'526 / 527, 3 dangling'" in errors[0]


def test_vent_headline_derived_from_the_crosstab(doc_tree: Path) -> None:
    # The headline is arithmetic over the cross-tab under it, so the two cannot
    # drift: 68 of 68 + 14 correct ejections rode a vent flag.
    _substitute(
        doc_tree, _READING_GUIDE, _FLAGGED_ROW, "| yes (68 meetings) | 60 | 0 |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'68 / 82 = 83%'" in errors[0]
    assert "'60 / 74 = 81%'" in errors[0]
    # ...and the drifted cell is no longer the one the instrument pins.
    assert "cross-tab's 'yes' row reads 60 impostor / 0 innocent" in errors[1]


def test_non_replay_jsonl_is_not_counted(doc_tree: Path) -> None:
    # The recorder writes a `<stem>.audit.jsonl` sidecar beside a replay, and
    # verify_samples.sh reconstructs only canonical replay-seed-N.jsonl files.
    # Counting a sidecar would inflate a figure claiming N of N were verified.
    (doc_tree / "replays" / "samples" / "9p2i" / "scratch.audit.jsonl").touch()
    assert check_doc_facts.check_facts(doc_tree) == []


def test_vent_crosstab_read_by_label_not_position(doc_tree: Path) -> None:
    # Reading the rows by position would derive 14 / 82 from a reordered
    # table that says those fourteen ejections had NO vent flag. Keyed on the
    # labels, reordering changes nothing...
    text = _read(doc_tree, _READING_GUIDE)
    assert _FLAGGED_ROW + "\n" + _UNFLAGGED_ROW in text
    _write(
        doc_tree,
        _READING_GUIDE,
        text.replace(
            _FLAGGED_ROW + "\n" + _UNFLAGGED_ROW,
            _UNFLAGGED_ROW + "\n" + _FLAGGED_ROW,
        ),
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_swapped_vent_crosstab_labels_detected(doc_tree: Path) -> None:
    # ...while swapping which population is flagged does change the
    # headline, and is caught: 14 of 82 correct ejections would then be
    # the vent-backed ones.
    text = _read(doc_tree, _READING_GUIDE)
    assert _FLAGGED_ROW + "\n" + _UNFLAGGED_ROW in text
    swapped = "| no (68 meetings) | 68 | 0 |\n| yes (83 meetings) | 14 | 13 |"
    _write(
        doc_tree,
        _READING_GUIDE,
        text.replace(_FLAGGED_ROW + "\n" + _UNFLAGGED_ROW, swapped),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "'68 / 82 = 83%'" in error and "'14 / 82 = 17%'" in error for error in errors
    )
    # The pins name the same swap in their own terms: the flagged row is the
    # one the instrument recorded 68/0 for, whichever way round it is written.
    assert any(
        "cross-tab's 'yes' row reads 14 impostor / 13 innocent" in e for e in errors
    )


def test_mislabelled_vent_crosstab_row_fails_loud(doc_tree: Path) -> None:
    # A row whose label is neither yes nor no leaves the two populations
    # unidentifiable, which must fail rather than derive something.
    _substitute(
        doc_tree, _READING_GUIDE, "| yes (68 meetings) |", "| flagged (68 meetings) |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no vent cross-tab" in errors[0]


def test_proof_partition_derived_from_the_previous_record(doc_tree: Path) -> None:
    # The before column is the read the recording this one replaced published,
    # so a moved cell there moves the history the front door states rather than
    # being absorbed.
    _substitute(
        doc_tree, _PROOF_AUDIT, _PROOF_DIRECT_POOLED, "**318/326 = 0.975** pooled"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    figure = [error for error in errors if "326 / 326 = 1.0000" in error]
    assert len(figure) == 1
    assert "'318 / 326 = 0.9755 vs 61 / 103 = 0.5922'" in figure[0]


def test_published_partition_derived_from_the_record(doc_tree: Path) -> None:
    # The published figure is the CURRENT record's own pre-registered read, so
    # a moved pooled cell there moves the front door rather than being absorbed.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| **pooled** | **61/103 = 0.5922** | **50/96 = 0.5208** [0.4224, 0.6178] |",
        "| **pooled** | **61/103 = 0.5922** | **53/96 = 0.5521** [0.4224, 0.6178] |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("'333 / 333 = 1.0000 vs 53 / 96 = 0.5521'" in error for error in errors)
    # ...and the record's two decided bars now contradict each other.
    assert any("its non-direct accuracy cell reads 53/96" in error for error in errors)


def test_record_innocent_bar_reaches_the_front_door(doc_tree: Path) -> None:
    # The wrongful-ejection count the row publishes is the record's bar-2
    # pooled cell, not a number this page remembers.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| **pooled** | **42** | **46** |",
        "| **pooled** | **42** | **40** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "'40 of 40 innocent ejections sit in the no-proof cell'" in error
        for error in errors
    )
    assert any("its wrongful-ejection cell reads 40" in error for error in errors)


def test_record_direct_proof_cell_reaches_the_front_door(doc_tree: Path) -> None:
    # A record that ever convicted an innocent WITH engine-certified proof
    # falsifies the row's own placement claim, and must fail here rather than
    # leave the front door still saying there were none.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "**333/333 = 1.0000** pooled",
        "**332/333 = 0.9970** pooled",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("1 proof-present innocent ejection(s)" in error for error in errors)
    assert any("'332 / 333 = 0.9970 vs 50 / 96 = 0.5208'" in error for error in errors)


def test_missing_record_bar_fails_loud(doc_tree: Path) -> None:
    # Losing the bar's pooled row must not read as "nothing to derive from".
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "### Published cell 1 — non-direct conviction accuracy",
        "### The first bar — I-1 non-direct conviction accuracy",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _LADDER_TIP_AUDIT in errors[0]
    assert "conviction-partition cells cannot be located" in errors[0]


def test_previous_record_pooled_row_read_by_label_not_position(doc_tree: Path) -> None:
    # The pooled row is keyed on its own label, so moving it inside the bar's
    # table changes nothing...
    text = _read(doc_tree, _PROOF_AUDIT)
    assert _PROOF_INNOCENT_POOLED in text
    rows = text.split(_PROOF_INNOCENT_POOLED)
    assert len(rows) == 2
    moved = text.replace("| `samples/9p2i` | 23 | **14** |\n", "", 1).replace(
        _PROOF_INNOCENT_POOLED,
        f"{_PROOF_INNOCENT_POOLED}\n| `samples/9p2i` | 23 | **14** |",
        1,
    )
    _write(doc_tree, _PROOF_AUDIT, moved)
    assert check_doc_facts.check_facts(doc_tree) == []


def test_swapped_previous_record_columns_detected(doc_tree: Path) -> None:
    # ...while swapping the before and after halves of that row inverts the
    # history: the column would state what the recording BEFORE the previous one
    # read, on a page whose header names the previous one.
    _substitute(
        doc_tree,
        _PROOF_AUDIT,
        _PROOF_ACCURACY_POOLED,
        "| **pooled** | **61/103 = 0.5922** [0.4957, 0.6822] | "
        "**46/125 = 0.3680** [0.2886, 0.4553] |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("326 / 326 = 1.0000 vs 46 / 125 = 0.3680" in error for error in errors)


def test_previous_record_innocent_total_drift_detected(doc_tree: Path) -> None:
    # The before column's own arithmetic: 61/103 fixes 42 wrongful ejections, so
    # the two bars of the previous record are checked against each other exactly
    # as the current record's are.
    _substitute(
        doc_tree,
        _PROOF_AUDIT,
        _PROOF_INNOCENT_POOLED,
        "| **pooled** | **79** | **44** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    arithmetic = [
        error for error in errors if "non-direct accuracy cell reads 61/103" in error
    ]
    assert len(arithmetic) == 1
    assert _PROOF_AUDIT in arithmetic[0]
    assert "wrongful-ejection cell reads 44" in arithmetic[0]


def test_missing_previous_record_bar_fails_loud(doc_tree: Path) -> None:
    # Losing the bar must not read as "nothing to derive from".
    _substitute(
        doc_tree,
        _PROOF_AUDIT,
        _PROOF_ACCURACY_HEADING,
        "### The first bar — I-1 non-direct conviction accuracy: **MISSED**",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _PROOF_AUDIT in errors[0]
    assert "conviction-partition cells cannot be located" in errors[0]


def test_renamed_previous_record_pooled_row_fails_loud(doc_tree: Path) -> None:
    # A pooled row this derivation cannot identify must fail rather than pool a
    # half-sum out of the per-set rows it does recognize.
    _substitute(
        doc_tree,
        _PROOF_AUDIT,
        _PROOF_INNOCENT_POOLED,
        "| **all four sets** | **79** | **42** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _PROOF_AUDIT in errors[0]
    assert "conviction-partition cells cannot be located" in errors[0]


def test_innocent_ejections_moved_to_the_wrong_cell_detected(doc_tree: Path) -> None:
    # The count alone is not the claim. A row stating the same 46 of 46 but
    # putting them in the proof-present cell states the opposite finding, so
    # matching the number without the placement would gate shape, not meaning.
    _substitute(
        doc_tree,
        _README,
        "46 of 46 innocent ejections sit in the no-proof cell",
        "46 of 46 innocent ejections sit in the proof-present cell",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'46 of 46 innocent ejections sit in the no-proof cell'" in errors[0]


def test_ml_arm_win_count_derived_from_the_finalist_jsonl(doc_tree: Path) -> None:
    # The ML page publishes the program's headline table; every cell is
    # recomputed from the committed measurement, not trusted as prose.
    _substitute(doc_tree, _ML_PAGE, "| 26/50 = 0.52 |", "| 27/50 = 0.54 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "reads 27/50" in errors[0]
    assert "recomputes to 26/50" in errors[0]


def test_ml_p_value_drift_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _ML_PAGE, "| **0.0072** |", "| **0.0100** |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "states 0.0100" in errors[0]
    assert "0.0072" in errors[0]


def test_ml_rate_that_contradicts_its_own_fraction_detected(doc_tree: Path) -> None:
    # The rate is checked at the precision the cell prints: the table may round
    # as it likes, but it may not round to a different number.
    _substitute(doc_tree, _ML_PAGE, "| 26/50 = 0.52 |", "| 26/50 = 0.60 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "states the rate 0.60" in errors[0]
    assert "rounds to 0.52" in errors[0]


def test_ml_comparator_row_drift_detected(doc_tree: Path) -> None:
    _substitute(
        doc_tree,
        _ML_PAGE,
        _ML_COMPARATOR_ROW,
        "| `p18-fsm-comparator` (scripted) | 15/50 = 0.30 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "reads 15/50" in errors[0]
    assert "recomputes to 13/50" in errors[0]


def test_ml_dropped_arm_detected(doc_tree: Path) -> None:
    # Publishing only the flattering arms is the failure mode a one-directional
    # check would miss: every entrant the JSONL carries must have a row.
    _substitute(doc_tree, _ML_PAGE, _ML_DROPPED_ARM_ROW, "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "p18-imp-bfd145cb" in errors[0]
    assert "the results table does not state" in errors[0]


def test_ml_arm_absent_from_the_jsonl_fails_loud(doc_tree: Path) -> None:
    # An arm nobody recorded must fail rather than be skipped as unmatched.
    _substitute(doc_tree, _ML_PAGE, "`ea4bc955…`", "`deadbeef…`")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("'p18-imp-deadbeef'" in error for error in errors)


def test_ml_referee_verdict_flip_detected(doc_tree: Path) -> None:
    # The referee column IS the adoption gate — it is what "none became the
    # default" means — so a FAIL flipped to PASS must not ship.
    _substitute(
        doc_tree,
        _ML_PAGE,
        "| **0.3075 — not significant** | **FAIL** |",
        "| **0.3075 — not significant** | **PASS** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "states PASS" in errors[0]
    assert "referee_passed = False" in errors[0]


def test_ml_unreadable_referee_verdict_fails_loud(doc_tree: Path) -> None:
    # A cell stating neither verdict is not a pass: the gate outcome has to be
    # legible before it can be compared.
    _substitute(
        doc_tree,
        _ML_PAGE,
        "| **0.3075 — not significant** | **FAIL** |",
        "| **0.3075 — not significant** | — |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "is neither PASS nor FAIL" in errors[0]


def test_ml_invented_arm_row_detected(doc_tree: Path) -> None:
    # The reverse-coverage check proves every measured arm is published; this
    # proves the converse, that nothing unmeasured is.
    _substitute(
        doc_tree,
        _ML_PAGE,
        _ML_DROPPED_ARM_ROW,
        _ML_DROPPED_ARM_ROW
        + "| `mystery-arm` | 50/50 = 1.00 | 13/50 = 0.26 | **0.0001** | PASS |\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "neither the comparator nor an arm sha" in errors[0]


def test_ml_lookalike_comparator_row_detected(doc_tree: Path) -> None:
    # The comparator identity is matched whole, not as a substring: a
    # `fake-p18-fsm-comparator` row carrying the comparator's own cells would
    # otherwise ride in as a second PASS.
    _substitute(
        doc_tree,
        _ML_PAGE,
        _ML_DROPPED_ARM_ROW,
        _ML_DROPPED_ARM_ROW
        + "| `fake-p18-fsm-comparator` | 13/50 = 0.26 | — | — | PASS |\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "neither the comparator nor an arm sha" in errors[0]


def test_ml_duplicated_comparator_row_detected(doc_tree: Path) -> None:
    # Every arm is measured against exactly one comparator, so the table states
    # exactly one — two rows would leave the reader two baselines.
    text = _read(doc_tree, _ML_PAGE)
    row = "| `p18-fsm-comparator` (scripted) | 13/50 = 0.26 | — | — | PASS |\n"
    assert row in text
    _write(doc_tree, _ML_PAGE, text.replace(row, row + row, 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "holds 2 'p18-fsm-comparator' rows" in errors[0]


def test_ml_negated_referee_verdict_detected(doc_tree: Path) -> None:
    # "not a FAIL" contains FAIL and states its opposite; the cell has to BE a
    # verdict, not contain one.
    _substitute(
        doc_tree,
        _ML_PAGE,
        "| **0.3075 — not significant** | **FAIL** |",
        "| **0.3075 — not significant** | not a FAIL |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "this column carries a verdict, not prose" in errors[0]


def test_ml_short_results_row_fails_loud(doc_tree: Path) -> None:
    # A row missing the referee column must be reported alongside the other
    # fact errors, never raise out of the gate.
    _substitute(
        doc_tree,
        _ML_PAGE,
        "| `bfd145cb…` | 28/50 = 0.56 | 13/50 = 0.26 | **0.0041** | **FAIL** |",
        "| `bfd145cb…` | 28/50 = 0.56 | 13/50 = 0.26 | **0.0041** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any("holds 4 cells, not the 5" in error for error in errors)
    assert any("p18-imp-bfd145cb" in error for error in errors)


def test_partition_innocent_total_contradicting_its_own_accuracy_detected(
    doc_tree: Path,
) -> None:
    # An ejection is either correct or it convicted an innocent, so the
    # record's own 50/96 fixes 46. Moving the wrongful-ejection bar while
    # updating the README to match must still fail: the record would then be
    # internally contradictory under one date.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| **pooled** | **42** | **46** |",
        "| **pooled** | **42** | **45** |",
    )
    _substitute(
        doc_tree,
        _README,
        "46 of 46 innocent ejections sit in the no-proof cell",
        "45 of 45 innocent ejections sit in the no-proof cell",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "its non-direct accuracy cell reads 50/96" in error
        and "wrongful-ejection cell reads 45" in error
        for error in errors
    )
    # ...and every surface still narrating the record's own 46 is now naming a
    # count the record no longer records, which is the same drift read forward.
    stale = [error for error in errors if "wrongful-ejection sentence" in error]
    assert {error.split(":")[0] for error in stale} == {
        _README,
        _READING_GUIDE,
        _HISTORY,
        _ML_PAGE,
    }


def test_missing_ml_results_table_fails_loud(doc_tree: Path) -> None:
    # Losing the table must not read as "nothing to derive from".
    _substitute(doc_tree, _ML_PAGE, "| policy | impostor win |", "| model | win |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no results table" in errors[0]


# --------------------------------------------------------------------------- #
# The audits index's ladder tip, the word budgets, the corpus disclosures.     #
# --------------------------------------------------------------------------- #


def test_audits_index_ladder_tip_drift_detected(doc_tree: Path) -> None:
    # The index is where a reader is sent to find the record, and a "ladder
    # tip" sentence there sat outside the scan until 21.11 put it in scope. The
    # index states no tip of its own today, so the stale sentence is planted
    # rather than rewritten — the scan has to reach it either way.
    _write(
        doc_tree,
        _AUDITS_INDEX,
        _read(doc_tree, _AUDITS_INDEX) + "\nThe ladder tip stands at baseline 6.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_AUDITS_INDEX}:")
    assert "names baseline 6" in errors[0]
    assert "ladder tip at baseline 8" in errors[0]


def test_front_door_page_over_its_ceiling_detected(doc_tree: Path) -> None:
    # The budgets were Measurement-field targets nothing could fail; padding
    # the front door past its ceiling has to be an error now.
    _write(doc_tree, _README, _read(doc_tree, _README) + "\n" + "padding " * 200)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_README}: ")
    assert "over its 3550-word ceiling" in errors[0]


def test_lessons_under_its_floor_detected(doc_tree: Path) -> None:
    # A range budget with only a ceiling is half a gate: the essay shrinking
    # out of its band is the same drift read the other way.
    _write(doc_tree, _LESSONS, "# Lessons\n\n" + "word " * 100)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_LESSONS}: ")
    assert "under its 800-word floor" in errors[0]


def test_corpus_disclosure_coverage_cell_drift_detected(doc_tree: Path) -> None:
    # The exact drift A-15 found: a coverage cell left as recorded on the
    # previous substrate while the section was relabelled onto this one.
    _substitute(doc_tree, _CORPUS_README, "crew S9 **651/651", "crew S9 **723/726")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_CORPUS_README}:")
    assert "'crew S9' cell reads 723/726" in errors[0]
    assert "the recorded reports give 651/651" in errors[0]


def test_corpus_disclosure_stale_duplicate_cell_detected(doc_tree: Path) -> None:
    # A stale copy beside the correct value is drift too: every occurrence of a
    # cell's label is held to the recorded value, not just the first.
    _write(
        doc_tree,
        _CORPUS_README,
        _read(doc_tree, _CORPUS_README)
        + "\nAn earlier draft quoted impostor C9 **342/684 = 50.0%**.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'impostor C9' cell reads 342/684" in errors[0]
    assert "give 292/636" in errors[0]


def test_corpus_disclosure_substrate_relabel_detected(doc_tree: Path) -> None:
    # The root cause of A-15, reproduced: the substrate name is advanced and
    # every number is left as recorded on the previous one. Re-deriving the
    # numbers alone would pass this the moment the reports were replaced too,
    # so the label is bound to the ladder-tip audit.
    _substitute(
        doc_tree,
        _CORPUS_README,
        "the same baseline-8\nsubstrate",
        "the same baseline-9\nsubstrate",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_CORPUS_README}:")
    assert "labelled baseline-9 substrate" in errors[0]
    assert "ladder tip at baseline 8" in errors[0]


def test_corpus_disclosure_without_a_substrate_label_detected(doc_tree: Path) -> None:
    # Deleting the label must not be the way to silence the check: numbers with
    # no stated substrate are not true of anything.
    text = _read(doc_tree, _CORPUS_README).replace(
        "baseline-8\nsubstrate", "recorded\nsubstrate"
    )
    _write(
        doc_tree,
        _CORPUS_README,
        text.replace("baseline-8 substrate", "recorded substrate"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names no 'baseline-N substrate' at all" in errors[0]


def _trigger_report(tmp_path: Path, games: list[dict[str, object]]) -> Path:
    """A minimal eval report carrying a coverage block and the given games.

    Every case below perturbs exactly one thing, so the coverage block is always
    well-formed here; its own absence is a separate case.
    """

    report = tmp_path / "tournament-eval-report.json"
    report.write_text(
        json.dumps(
            {
                "deduction": {"public_response_coverage": _COVERAGE_BLOCK},
                "report": {"games": games},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return report


def test_an_impostor_triggered_meeting_lowers_the_crew_numerator(
    tmp_path: Path,
) -> None:
    # The claim is that NO meeting was impostor-triggered, so the numerator has
    # to be counted from the meeting rows' own trigger roles. Synthesising it
    # from the denominator would make the claim unfalsifiable — this report has
    # two meetings and only one crew trigger.
    report = _trigger_report(
        tmp_path,
        [
            {
                "game_id": "g-1",
                "roles": {"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
                "meetings": [
                    {"triggered_by": "p-1", "trigger": "report"},
                    {"triggered_by": "p-2", "trigger": "emergency"},
                ],
            }
        ],
    )
    errors: list[str] = []
    facts = check_doc_facts.read_disclosure_facts(tmp_path, report.name, errors)
    assert facts is not None
    assert (facts[0], facts[1]) == (1, 2)
    assert facts[2] == _COVERAGE_BLOCK
    assert errors == []


def test_a_trigger_is_never_resolved_against_another_games_roles(
    tmp_path: Path,
) -> None:
    # `p-1` is a crewmate in the first game and an impostor in the second, so a
    # parser that carried the first game's map forward would count the second
    # game's meeting as crew-triggered. The map is dropped at each game_id, and
    # a trigger with no map of its own fails loud rather than resolving.
    report = _trigger_report(
        tmp_path,
        [
            {
                "game_id": "g-1",
                "roles": {"p-1": "CREWMATE", "p-2": "IMPOSTOR"},
                "meetings": [{"triggered_by": "p-1"}],
            },
            {"game_id": "g-2", "meetings": [{"triggered_by": "p-1"}]},
        ],
    )
    errors: list[str] = []
    assert check_doc_facts.read_disclosure_facts(tmp_path, report.name, errors) is None
    assert len(errors) == 1
    assert "resolve to no role in their own game's map" in errors[0]


def test_a_trigger_naming_nobody_in_its_role_map_fails_loud(tmp_path: Path) -> None:
    # Counting an unknown id as non-crew would understate the numerator, which
    # is the direction that lets a false cell pass.
    report = _trigger_report(
        tmp_path,
        [
            {
                "game_id": "g-1",
                "roles": {"p-1": "CREWMATE"},
                "meetings": [{"triggered_by": "p-9"}],
            }
        ],
    )
    errors: list[str] = []
    assert check_doc_facts.read_disclosure_facts(tmp_path, report.name, errors) is None
    assert "['p-9']" in errors[0]


def test_a_disclosed_set_predating_the_substrate_detected(doc_tree: Path) -> None:
    # The label alone is not enough: if the ladder advances by graduating a
    # lever and these sets are not re-recorded, relabelling the section to the
    # new tip would otherwise pass. A set whose stamp lacks a graduated key
    # predates the substrate its numbers would be labelled with.
    manifest = "replays/ml_corpus/9p2i/MANIFEST.md"
    _substitute(doc_tree, manifest, "absence_prior, citation_gate", "citation_gate")
    errors = check_doc_facts.check_facts(doc_tree)
    # The vote-correctness sentinel notices the same perturbation as a cross-set
    # disagreement; this check is the one that names it as a set predating the
    # substrate its numbers would be labelled with.
    assert len(errors) == 2
    predating = [error for error in errors if error.startswith(f"{manifest}: ")]
    assert len(predating) == 1
    assert "stamps graduated lever(s) ['absence_prior'] OFF" in predating[0]
    assert "predates the substrate baseline 8 names" in predating[0]


def test_a_report_with_no_meeting_rows_fails_loud(tmp_path: Path) -> None:
    # Format drift must not read as "every meeting was crew-triggered".
    report = _trigger_report(tmp_path, [])
    errors: list[str] = []
    assert check_doc_facts.read_disclosure_facts(tmp_path, report.name, errors) is None
    assert len(errors) == 1
    assert "0 meeting rows" in errors[0]


def test_meeting_rows_without_a_role_map_fail_loud(tmp_path: Path) -> None:
    # Triggers with no roles to resolve them against would silently count as
    # impostor-triggered; that is drift in the report, not a finding about the
    # game.
    report = _trigger_report(tmp_path, [{"meetings": [{"triggered_by": "p-1"}]}])
    errors: list[str] = []
    assert check_doc_facts.read_disclosure_facts(tmp_path, report.name, errors) is None
    assert len(errors) == 1
    assert "resolve to no role in their own game's map" in errors[0]


def test_a_report_without_a_coverage_block_fails_loud(tmp_path: Path) -> None:
    # The single pass collects the coverage block too, so its absence is drift
    # this reports rather than a silently missing set of cells.
    report = tmp_path / "tournament-eval-report.json"
    report.write_text(
        json.dumps(
            {"report": {"games": [{"game_id": "g-1", "roles": {}, "meetings": []}]}},
            indent=2,
        ),
        encoding="utf-8",
    )
    errors: list[str] = []
    assert check_doc_facts.read_disclosure_facts(tmp_path, report.name, errors) is None
    # Both losses are named, not just the first noticed.
    assert len(errors) == 2
    assert any('"public_response_coverage":' in error for error in errors)
    assert any("0 meeting rows" in error for error in errors)


def test_corpus_disclosure_meeting_total_drift_detected(doc_tree: Path) -> None:
    # The meeting total is summed across all four reports, so it drifts
    # independently of any one set's coverage pair.
    _substitute(
        doc_tree,
        _CORPUS_README,
        "meetings crew-triggered **672/672**",
        "meetings crew-triggered **707/707**",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'meetings crew-triggered' cell reads 707/707" in errors[0]
    assert "give 672/672" in errors[0]


# --------------------------------------------------------------------------- #
# The claim-shaped facts, wherever the front door repeats them.                #
# --------------------------------------------------------------------------- #


def test_stale_guide_win_rate_detected(doc_tree: Path) -> None:
    # The reading guide repeats the rate the README states; a recording that
    # moved it and left this copy behind is the drift that survived the last
    # one, and README-only scanning could not see it.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| 36% (4p1i), 30% (9p2i) |",
        "| 34% (4p1i), 24% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 3
    stale = [error for error in errors if error.startswith(_READING_GUIDE)]
    assert len(stale) == 2
    assert any("claim '34% (4p1i)' disagrees" in error for error in stale)
    assert any("claim '24% (9p2i)' disagrees" in error for error in stale)
    # ...and the figure no longer equals the README's, which is the same drift
    # read from the other side.
    assert any("records '34% (4p1i), 24% (9p2i)'" in error for error in errors)


def test_stale_ml_page_win_rate_detected(doc_tree: Path) -> None:
    # The ML page dates and rates the recording its comparator now sits
    # against, so it is scanned with the rest of the front door.
    _substitute(
        doc_tree, _ML_PAGE, "36% (4p1i) and 30% (9p2i)", "30% (4p1i) and 30% (9p2i)"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_ML_PAGE)
    assert "claim '30% (4p1i)' disagrees" in errors[0]


def test_stale_guide_record_date_detected(doc_tree: Path) -> None:
    # Every document that dates the current recording is held to the
    # manifests, not the README alone.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "reference recording 8, 2026-08-31 — [instrument]",
        "reference recording 8, 2026-07-20 — [instrument]",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "'reference recording 8, 2026-07-20'" in errors[0]
    assert "'2026-08-31'" in errors[0]


def test_unnumbered_guide_record_date_detected(doc_tree: Path) -> None:
    # The front door also dates the recording without numbering it. That shape
    # is about the current one by construction, so it is held to the manifests
    # too — a numbered claim is what carries an exemption, not an unnumbered.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "current reference recording, made 2026-08-31",
        "current reference recording, made 2026-07-20",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "'reference recording, made 2026-07-20'" in errors[0]
    assert "'2026-08-31'" in errors[0]


def test_older_recording_date_is_left_alone(doc_tree: Path) -> None:
    # The front door is allowed to say what the recording it replaced was
    # dated; holding a numbered claim about recording 6 to today's manifests
    # would force the page to forget its own history.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| Pre-registered emergence rulings demonstrated, phase 18 | 0 of 14 | 0 of 14 |",
        "| Pre-registered emergence rulings demonstrated, phase 18 | 0 of 14 | 0 of 14 "
        "(reference recording 6, 2026-07-20) |",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_moved_figure_quoted_without_its_baseline_stamp_detected(
    doc_tree: Path,
) -> None:
    # A row that loses its before cell states a moved figure with nothing to
    # read it against; the column is the page's own before/after.
    _substitute(
        doc_tree,
        _README,
        "| 526 / 527, zero dangling | 538 / 538, zero dangling |",
        "| 526 / 527, zero dangling |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        error.startswith(_README)
        and "has no 'At baseline 7' cell" in error
        and _CITATION_ROW_CLAIM in error
        for error in errors
    )


def test_dropped_before_column_fails_loud(doc_tree: Path) -> None:
    # Losing the column entirely must fail rather than quietly stop checking
    # every history cell on the page.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| What | Figure | At baseline 7 |",
        "| What | Figure |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        f"{_READING_GUIDE}: its results table has no 'At baseline 7' column" in error
        for error in errors
    )


def test_before_column_drift_between_the_two_tables_detected(doc_tree: Path) -> None:
    # The history half is stated once too, so the two tables are compared on it
    # exactly as they are on the figure.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| 526 / 527, zero dangling | 538 / 538, zero dangling |",
        "| 526 / 527, zero dangling | 512 / 512, zero dangling |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'538 / 538, zero dangling'" in errors[0]
    assert "'512 / 512, zero dangling'" in errors[0]


def test_before_column_win_rate_held_to_the_record(doc_tree: Path) -> None:
    # A history cell is checked, not skipped: the record's own win-split table
    # says what the previous recording read, so a made-up before value fails.
    _substitute(
        doc_tree,
        _README,
        "| 36% (4p1i), 30% (9p2i) | 36% (4p1i), 24% (9p2i) |",
        "| 36% (4p1i), 30% (9p2i) | 12% (4p1i), 24% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "win-rate claim '12% (4p1i)' in the before column disagrees with "
        f"{_LADDER_TIP_AUDIT}'s win-split table (18/50 = 36%)" in error
        for error in errors
    )


def test_missing_win_split_table_fails_loud(doc_tree: Path) -> None:
    # Losing the record's win-split table must not read as "no history to
    # check": every before-column rate would then pass unexamined.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| set | baseline-7 impostor rate |",
        "| leg | baseline-7 impostor rate |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no win-split table" in errors[0]


# --------------------------------------------------------------------------- #
# The reading guide's narrative, and the games it names.                       #
# --------------------------------------------------------------------------- #


def test_stale_guide_ballot_prose_detected(doc_tree: Path) -> None:
    # The exact drift the last recording left behind: the table moved to
    # 526 / 527 and the paragraph under it kept saying 520.
    _substitute(doc_tree, _READING_GUIDE, "all 527 eject", "all 520 eject")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "'all 520 eject ballots'" in errors[0]
    assert _CITATION_INSTRUMENT in errors[0]


def test_stale_guide_crosstab_prose_detected(doc_tree: Path) -> None:
    # ...and the same class one paragraph down: the cross-tab re-quoted, the
    # sentence introducing it left at the previous recording's total.
    _substitute(doc_tree, _READING_GUIDE, "all 151\ncommitted", "all 165\ncommitted")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'all 165 committed 9p2i meetings'" in errors[0]
    assert _DEDUCTION_INSTRUMENT in errors[0]


def test_deleted_guide_narrative_fails_loud(doc_tree: Path) -> None:
    # A paragraph that quietly loses its figure must fail rather than leave
    # the pin bound to nothing.
    _substitute(doc_tree, _READING_GUIDE, "all 527 eject ballots", "every eject ballot")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no longer narrated anywhere" in errors[0]


def test_guide_crosstab_row_label_held_to_the_pins(doc_tree: Path) -> None:
    # The row labels carry the meeting counts, and those are pinned too: a
    # table whose cells are right and whose populations are wrong is still
    # describing a recording that is not this one.
    _substitute(
        doc_tree, _READING_GUIDE, _FLAGGED_ROW, "| yes (70 meetings) | 68 | 0 |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "row is labelled 70 meetings" in errors[0]
    assert "pins 68" in errors[0]


def test_unpinned_crosstab_fails_loud(doc_tree: Path) -> None:
    # Losing the instrument's pin must not read as "nothing to check".
    _substitute(
        doc_tree,
        _DEDUCTION_INSTRUMENT,
        "assert cross_tab.meetings_total == 151",
        "assert cross_tab.meeting_count == 151",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no pinned assertion for meetings_total" in errors[0]


def test_contradicting_crosstab_pins_fail_loud(doc_tree: Path) -> None:
    # Two pins for one cell leave the guide with two answers; the checker must
    # say so rather than take whichever came last.
    _substitute(
        doc_tree,
        _DEDUCTION_INSTRUMENT,
        "    assert cross_tab.meetings_total == 151",
        "    assert cross_tab.meetings_total == 151\n"
        "    assert cross_tab.meetings_total == 150",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("pins meetings_total at both 151 and 150" in error for error in errors)


def test_stale_guide_no_proof_ratio_detected(doc_tree: Path) -> None:
    # The most-quoted sentence on the page is the unflagged half read as a
    # ratio, and it is read off the cross-tab's own cells.
    _substitute(
        doc_tree, _READING_GUIDE, "coin flip — 14 of 27", "coin flip — 15 of 27"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "narrated ratio 15 of 27" in errors[0]
    assert "pins at 14 of 27" in errors[0]


def test_deleted_guide_no_proof_ratio_fails_loud(doc_tree: Path) -> None:
    # Dropping the sentence must fail rather than leave the reading unbound.
    _substitute(
        doc_tree, _READING_GUIDE, "close to a coin flip — 14 of 27", "close to chance"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no longer narrated anywhere" in errors[0]


def test_stale_partner_ballot_denominator_detected(doc_tree: Path) -> None:
    # The teammate-firewall row lives only in the guide, so README agreement
    # cannot reach it; the instrument that counts those ballots owns it.
    _substitute(doc_tree, _READING_GUIDE, "| 0 of 218 |", "| 0 of 217 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'0 of 217'" in errors[0]
    assert "pins '0 of 218'" in errors[0]


def test_partner_ballot_row_without_its_pin_fails_loud(doc_tree: Path) -> None:
    # Losing the pin must not read as "nothing to check".
    _substitute(
        doc_tree,
        _DEDUCTION_INSTRUMENT,
        "samples.model_partner_naming_ballots, samples.impostor_ballots",
        "samples.model_partner_naming_ballots, samples.impostor_ballot_count",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no pinned impostor-ballot total" in errors[0]


def test_guide_only_row_losing_its_before_cell_detected(doc_tree: Path) -> None:
    # The guide carries rows the README does not, and they state history too.
    _substitute(doc_tree, _READING_GUIDE, "| 0 of 218 | 0 of 219 |", "| 0 of 218 |  |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "'Impostor ballots cast against a partner (9p2i)'" in errors[0]
    assert "has no 'At baseline 7' cell" in errors[0]


def test_truncated_row_losing_its_before_cell_detected(doc_tree: Path) -> None:
    # Removing the cell AND its delimiter must fail like an emptied one: a row
    # narrower than the header has no history cell, and reading whatever cell
    # happens to sit at the index would check it against the wrong column.
    _substitute(doc_tree, _READING_GUIDE, "| 0 of 218 | 0 of 219 |", "| 0 of 218 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "'Impostor ballots cast against a partner (9p2i)'" in errors[0]
    assert "not as wide as the header" in errors[0]


def test_unowned_moved_history_cell_detected(doc_tree: Path) -> None:
    # A row whose history cell differs from its figure claims something moved.
    # Either this checker re-derives that value or the row is named as one it
    # only compares — otherwise the two tables can drift together, which is the
    # one failure the before/after column exists to prevent.
    row = "| 100 of 100 | 100 of 100 |"
    drifted = "| 100 of 100 | 99 of 100 |"
    _substitute(doc_tree, _README, row, drifted)
    # One-sided first: that is the agreement check's finding, not this one.
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'99 of 100'" in errors[0] and "records '100 of 100'" in errors[0]
    # Made in BOTH tables it survives agreement, and only this check sees it —
    # no row is exempt, including the ones whose FIGURE is re-derived, because
    # deriving today's count says nothing about the one before it.
    _substitute(doc_tree, _READING_GUIDE, row, drifted)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "states a moved figure" in errors[0]
    assert "'99 of 100'" in errors[0]


def test_verdict_rate_that_contradicts_its_own_fraction_detected(
    doc_tree: Path,
) -> None:
    # The verdict passage states the same cell the results row states. Every
    # "k of n = rate" on the front door is its own arithmetic, so a moved
    # denominator in the prose cannot survive a correct table.
    _substitute(doc_tree, _README, "61 of 103 = 0.5922", "61 of 104 = 0.5922")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'61 of 104 = 0.5922' does not recompute" in errors[0]
    assert "61/104 is 0.5865" in errors[0]


def test_verdict_wrongful_ejection_count_drift_detected(doc_tree: Path) -> None:
    # ...and the bare count beside it is held to the record the same way a
    # "ladder tip" sentence is held to the baseline. The sentence perturbed here
    # names BOTH recordings' counts, which is the shape the gate requires of a
    # record whose own count it does not carry — so the perturbation moves both
    # ends, leaving the sentence with neither.
    _substitute(
        doc_tree,
        _HISTORY,
        "wrongful ejections rose from 42 to 46",
        "wrongful ejections rose from 43 to 47",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "a wrongful-ejection sentence names neither the count" in errors[0]
    assert "(46)" in errors[0]


def test_verdict_fraction_rewritten_consistently_detected(doc_tree: Path) -> None:
    # Self-consistent arithmetic is not enough: a fraction over a conviction
    # population the record measured has to BE the cell the record recorded, or
    # the prose argues past the finding while adding up.
    _substitute(doc_tree, _README, "50 of 96 = 0.5208", "51 of 96 = 0.5312")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "is over a conviction population" in errors[0]
    assert "whose cell is 50/96" in errors[0]


def test_wrongful_ejection_count_inside_a_longer_number_detected(
    doc_tree: Path,
) -> None:
    # The count is matched as a whole number: "146" contains "46" and is not it.
    _substitute(
        doc_tree,
        _HISTORY,
        "wrongful ejections rose from 42 to 46",
        "wrongful ejections rose from 142 to 146",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names neither the count the record read (46)" in errors[0]


def test_wrongful_ejection_sentence_may_state_the_previous_count(
    doc_tree: Path,
) -> None:
    # The front door is allowed to say what the recording before this one read,
    # which is the whole point of the before column.
    guide = _read(doc_tree, _READING_GUIDE)
    _write(
        doc_tree,
        _READING_GUIDE,
        guide + "\nThe one before it read 42 wrongful ejections.\n",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_finding_accuracy_bar_reaches_the_front_door(doc_tree: Path) -> None:
    # The deciding record's own bar-1 cell. Nothing else in this module reads
    # that audit, so without this check the figure could drift on every page.
    _substitute(
        doc_tree, _FINDING_AUDIT, _FINDING_ACCURACY_ROW, _FINDING_ACCURACY_DRIFTED
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        error.startswith(f"{_HISTORY}:")
        and "'46 of 66 = 0.6970'" in error
        and "whose cell is 45/66" in error
        for error in errors
    )
    # ...and the summary cell has stopped summarising the bar section above it.
    assert any(
        "bar 1's this record cell reads '45/66 = 0.6818' in the verdict table" in error
        for error in errors
    )


def test_finding_share_bar_reaches_the_front_door(doc_tree: Path) -> None:
    # Bar 4's cell is the one the record MISSED, so it is the figure a reader
    # is most likely to check and the one a summary is most tempted to soften.
    _substitute(doc_tree, _FINDING_AUDIT, _FINDING_SHARE_ROW, _FINDING_SHARE_DRIFTED)
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "'11 of 20 = 0.5500'" in error and "whose cell is 9/20" in error
        for error in errors
    )
    # ...and the share stops being the two count bars taken over each other.
    assert any(
        "cell reads 9/20, but bars 3 and 2 read 11 and 20" in error for error in errors
    )


def test_finding_innocent_bar_reaches_the_front_door(doc_tree: Path) -> None:
    # Bar 2's cell is a bare count, so it is pinned through the wording the
    # verdict passage carries rather than through a rate claim.
    _substitute(
        doc_tree, _FINDING_AUDIT, _FINDING_INNOCENT_ROW, _FINDING_INNOCENT_DRIFTED
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "does not state 'innocent ejections fell from 46 to 19'" in error
        for error in errors
    )


def test_finding_reporter_bar_reaches_the_front_door(doc_tree: Path) -> None:
    # ...and so is bar 3's, through the sentence that names both ends of it.
    _substitute(
        doc_tree, _FINDING_AUDIT, _FINDING_REPORTER_ROW, _FINDING_REPORTER_DRIFTED
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        '"10 of those 20 were the meeting\'s own reporter, against 34 of 46"' in error
        for error in errors
    )


def test_finding_verdict_column_is_recomputed(doc_tree: Path) -> None:
    # The verdict column is not quoted: it is recomputed from the bar's own
    # target and its own cell, so a record cannot publish a verdict its numbers
    # do not support.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_SHARE_ROW,
        _FINDING_SHARE_ROW.replace("**MISSED**", "**MET**"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 4's own target and cell make it MISSED, but the verdict column "
        "says MET" in error
        for error in errors
    )


def test_verdict_word_follows_the_bars_in_both_directions(doc_tree: Path) -> None:
    # The other direction, which is the one no committed tree exercises: a
    # record whose bars ALL passed may not be published under the finding
    # wording, so the front door's verdict word is derived rather than typed.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_SHARE_ROW,
        "| 4 | `reporter_share_of_innocent_ejections` pooled | < 0.40 | "
        "34/46 = 0.7391 | 7/20 = 0.3500 | **MET** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "does not state 'the rule returns an adoption'" in error for error in errors
    )


def test_powered_set_below_its_floor_makes_the_bar_a_miss(doc_tree: Path) -> None:
    # Bar 1's target is compound: a pooled pass AND no adequately powered set
    # below the floor. Reading only the leading comparator would publish a
    # verdict the record's own per-set table refutes.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_POWERED_SET_ROW,
        "| `ml_corpus/9p2i` | 32/61 = 0.5246 | 20/51 = 0.3922 (n = 51, **POWERED**) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "set 'ml_corpus/9p2i' reads 20/51" in error
        and "makes a MISSED, but the pooled cell clears the bar" in error
        for error in errors
    )
    # ...which flips the recomputed verdict, so the stated MET fails too.
    assert any(
        "bar 1's own target and cell make it MISSED, but the verdict column "
        "says MET" in error
        for error in errors
    )


def test_deleting_bar_1s_per_set_clause_fails_loud(doc_tree: Path) -> None:
    # The clause is read off the target cell, so the cell could delete it and
    # take that half of the gate along. The bars that registered one are named,
    # and losing the words is reported rather than silently obeyed.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| ≥ 0.60, no powered set < 0.50 |",
        "| ≥ 0.60 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "bar 1 registered a per-set clause beside its pooled target" in errors[0]


def test_underpowered_set_below_the_floor_binds_nothing(doc_tree: Path) -> None:
    # The other half of the same clause: a set with too few ejections takes no
    # part in it, so moving one below the floor must NOT flip the verdict — a
    # per-set gate that fired on every set would be a different bar. The nine
    # ejections move to the powered set rather than vanishing, so the pooled
    # row still sums and this perturbation stays about the clause alone.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| `samples/9p2i` | 14/27 = 0.5185 | 10/15 = 0.6667 (n = 15, not powered) |",
        "| `samples/9p2i` | 14/27 = 0.5185 | 1/15 = 0.0667 (n = 15, not powered) |",
    )
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_POWERED_SET_ROW,
        _FINDING_POWERED_SET_ROW.replace("36/51 = 0.7059", "45/51 = 0.8824"),
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_two_bars_over_one_population_must_agree(doc_tree: Path) -> None:
    # The rate registry is keyed on the population, so two bars measuring the
    # same denominator with different numerators would leave the later row
    # silently deciding what the front door is held to.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_SHARE_ROW,
        _FINDING_SHARE_ROW.replace("11/20 = 0.5500", "44/66 = 0.6667"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 4 reads 44/66 over a population another bar reads 46/66" in error
        for error in errors
    )


def test_verdict_table_missing_a_bar_fails_loud(doc_tree: Path) -> None:
    # A table that lost a row still parses and still satisfies the share
    # identity, while the figure that row pinned quietly stops being checked.
    _substitute(doc_tree, _FINDING_AUDIT, _FINDING_ACCURACY_ROW + "\n", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "does not carry exactly bars 1, 2, 3, 4" in errors[0]


def test_verdict_cell_rate_that_contradicts_its_fraction_detected(
    doc_tree: Path,
) -> None:
    # The printed decimal is re-derived from the fraction beside it: a cell
    # whose two halves disagree has no single value, and a decimal on the far
    # side of a target would otherwise drive the verdict from false arithmetic.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_ACCURACY_ROW,
        _FINDING_ACCURACY_ROW.replace("46/66 = 0.6970", "46/66 = 0.9000"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "one of the two cannot be read as a number at the precision it prints" in error
        for error in errors
    )


def test_verdict_cell_drifting_from_its_bar_section_detected(doc_tree: Path) -> None:
    # The verdict table SUMMARISES the read above it, so its cells and that
    # bar's own pooled row are one statement made twice.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_INNOCENT_SECTION_POOLED,
        "| pooled | 46 | **21** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 2's this record cell reads '20' in the verdict table and '21' in "
        "the bar's own pooled row" in error
        for error in errors
    )


def test_finding_history_cell_disagreeing_with_the_ladder_tip_detected(
    doc_tree: Path,
) -> None:
    # The deciding record's account of what it moved FROM is the ladder-tip
    # recording's own published cell, so the two are held together rather than
    # the summary being taken on trust.
    drifted = _FINDING_ACCURACY_ROW.replace("50/96 = 0.5208", "49/96 = 0.5104")
    _substitute(doc_tree, _FINDING_AUDIT, _FINDING_ACCURACY_ROW, drifted)
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_ACCURACY_SECTION_POOLED,
        "| pooled | 49/96 = 0.5104 | **46/66 = 0.6970** |",
    )
    # ...and the set row the pooled history cell is the sum of, so the drift
    # under test is the one against the recording that owns the cell.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| `samples/9p2i` | 14/27 = 0.5185 |",
        "| `samples/9p2i` | 13/27 = 0.4815 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "bar 1's history cell reads '49/96 = 0.5104'" in errors[0]
    assert f"{_LADDER_TIP_AUDIT} — the recording it is read against" in errors[0]
    assert "published (50, 96)" in errors[0]


def test_finding_count_wording_checked_on_every_claim_document(
    doc_tree: Path,
) -> None:
    # The bare counts reach no rate scan, and the older count keeps
    # _INJUSTICE_SENTENCE satisfied — so a page that states the fall at all is
    # held to the record's own numbers, not only the README.
    # The three pages hard-wrap at different columns, so each is perturbed on
    # the words it actually carries on one line.
    for document, wording in (
        (_HISTORY, "innocent ejections fell from 46 to 20"),
        (_READING_GUIDE, "innocent ejections fell from 46 to 20"),
        (_ML_PAGE, "ejections fell from 46 to 20"),
    ):
        _substitute(doc_tree, document, wording, wording.replace("to 20", "to 21"))
    errors = check_doc_facts.check_facts(doc_tree)
    assert {
        error.split(":")[0]
        for error in errors
        if "innocent ejections fell from 46 to 20" in error
    } == {_HISTORY, _READING_GUIDE, _ML_PAGE}


def test_a_claim_document_that_never_states_the_fall_is_not_required_to(
    doc_tree: Path,
) -> None:
    # The converse, so the rule is a wording gate on the pages that publish the
    # count and not a demand that every page publish it: the glossary and the
    # audits index carry neither claim and stay green.
    assert "innocent ejections fell from" not in _read(doc_tree, _GLOSSARY)
    assert "innocent ejections fell from" not in _read(doc_tree, _AUDITS_INDEX)
    assert check_doc_facts.check_facts(doc_tree) == []


def test_duplicated_verdict_bar_row_fails_loud(doc_tree: Path) -> None:
    # Rows are read into a dict, so a duplicate label would let the later row
    # win while the key set still looked complete — two conflicting verdicts
    # published under one bar number.
    contradictory = _FINDING_SHARE_ROW.replace("11/20 = 0.5500", "7/20 = 0.3500")
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_SHARE_ROW,
        f"{contradictory}\n{_FINDING_SHARE_ROW}",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("verdict table cannot be located" in error for error in errors)


def test_reattributed_verdict_bar_cell_detected(doc_tree: Path) -> None:
    # The numbers do not say what they measure: a row that keeps its figures
    # while naming another metric re-attributes the bar, and every check after
    # it reads those figures as this bar's.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| 3 | `reporter_innocent_ejections` pooled |",
        "| 3 | `some_other_cell` pooled |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 3 registered the cell 'reporter_innocent_ejections'" in error
        for error in errors
    )


def test_target_moved_away_from_the_preregistration_detected(doc_tree: Path) -> None:
    # The whole worth of a pre-registered bar is that its target cannot move
    # after the measurement, so both of the record's copies are held to the
    # memo that was merged before a byte was generated.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_SHARE_ROW,
        _FINDING_SHARE_ROW.replace("| < 0.40 |", "| < 0.60 |"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 4's verdict table states the target '< 0.60'" in error
        and "registered '< 40%' before the bytes existed" in error
        for error in errors
    )


def test_bar_section_target_moved_away_from_the_preregistration_detected(
    doc_tree: Path,
) -> None:
    # ...and the bar's own section, which is the copy a reader checks the
    # summary against.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "Target **< 0.40 pooled**.",
        "Target **< 0.60 pooled**.",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 4's own section states the target '< 0.60 pooled'" in error
        for error in errors
    )


def test_deleted_powered_set_row_fails_loud(doc_tree: Path) -> None:
    # The only powered set is the one observation able to fail bar 1's compound
    # target, and an absent row reads as a set that constrains nothing.
    _substitute(doc_tree, _FINDING_AUDIT, _FINDING_POWERED_SET_ROW + "\n", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 1's section is missing a row for ml_corpus/9p2i" in error
        for error in errors
    )


def test_per_set_rate_that_contradicts_its_fraction_detected(doc_tree: Path) -> None:
    # The per-set cells are read for their fraction, so their printed decimals
    # would otherwise be the one place in the read nothing recomputes.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_POWERED_SET_ROW,
        _FINDING_POWERED_SET_ROW.replace("36/51 = 0.7059", "36/51 = 0.9999"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 1's 'ml_corpus/9p2i' cell '36/51 = 0.9999 (n = 51, POWERED)' "
        "prints a rate its own fraction does not recompute to" in error
        for error in errors
    )


def test_an_unrelated_sample_of_the_same_size_is_left_alone(doc_tree: Path) -> None:
    # The bars are ejection cells, so a fraction is read as one only inside a
    # sentence about ejections — otherwise a sample that happens to be twenty
    # of anything would be rejected for not being the reporter cell.
    history = _read(doc_tree, _HISTORY)
    _write(
        doc_tree,
        _HISTORY,
        history + "\nA separate sample covered 5 of 20 = 0.2500 games.\n",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_an_ejection_statistic_over_a_bar_population_is_left_alone(
    doc_tree: Path,
) -> None:
    # ...and "a sentence about ejections" is not narrow enough either: every
    # one of the four cells IS an ejection cell, so an ejection statistic that
    # happens to be over twenty would be rejected as the reporter's share. The
    # sentence has to be about that bar's own measurement.
    history = _read(doc_tree, _HISTORY)
    _write(
        doc_tree,
        _HISTORY,
        history + "\nHere 5 of 20 = 0.2500 ejection ballots carried a note.\n",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_reporter_claim_over_the_bar_population_is_still_held(
    doc_tree: Path,
) -> None:
    # The other half of the same rule, so narrowing the scope did not empty it:
    # a sentence that DOES name the bar's subject is held to the bar's cell.
    history = _read(doc_tree, _HISTORY)
    _write(
        doc_tree,
        _HISTORY,
        history + "\nThe reporter took 5 of 20 = 0.2500 of that total.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "the claim '5 of 20 = 0.2500' is over a population" in error
        and "whose cell is 11/20" in error
        for error in errors
    )


def test_per_set_floor_relaxed_after_the_measurement_detected(doc_tree: Path) -> None:
    # The leading comparator is half of a compound target. Relaxing the per-set
    # floor leaves the pooled cell clearing its own bar and the clause still
    # syntactically present, so both of the record's copies are held to the
    # memo that fixed the floor before the bytes existed.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "≥ 0.60, no powered set < 0.50",
        "≥ 0.60, no powered set < 0.40",
    )
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "with no adequately powered set below 0.50",
        "with no adequately powered set below 0.40",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert all(
        "registered 'no ADEQUATELY POWERED set below" in error for error in errors
    )
    assert any("verdict table states the per-set clause" in error for error in errors)
    assert any("own section states the per-set clause" in error for error in errors)


def test_registered_power_threshold_the_checker_does_not_read_detected(
    doc_tree: Path,
) -> None:
    # The clause's third part: which sets it binds. The threshold this module
    # APPLIES is its own constant, so a memo registering another one would
    # leave the floor read over a different set of sets.
    _substitute(
        doc_tree,
        _PREREGISTRATION_AUDIT,
        "a non-direct denominator of **n ≥ 30**",
        "a non-direct denominator of **n ≥ 40**",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 1's clause is registered at n ≥ 40, and this checker reads it at "
        "n ≥ 30" in error
        for error in errors
    )


def test_section_target_line_that_drops_the_per_set_clause_detected(
    doc_tree: Path,
) -> None:
    # The record states the clause twice, and only the verdict table's copy is
    # read by the recomputation. A Target line that drops the words leaves the
    # pooled comparator matching, the memo agreeing with the copy that is left
    # and nothing at all saying the section stopped stating half of the gate.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "Target **≥ 0.60 pooled**, with no adequately powered set below 0.50, where",
        "Target **≥ 0.60 pooled**, where",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "bar 1's own section states no per-set clause at all" in errors[0]
    assert "registered 'no ADEQUATELY POWERED set below" in errors[0]


def test_verdict_history_cell_rate_contradicting_its_fraction_detected(
    doc_tree: Path,
) -> None:
    # The summary's history cell is compared as a FIGURE, which reduces both
    # copies to a k/n — so a false printed rate beside the right fraction reads
    # as agreement everywhere, and is published as the baseline it moved from.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_ACCURACY_ROW,
        _FINDING_ACCURACY_ROW.replace("| 50/96 = 0.5208 |", "| 50/96 = 0.9999 |"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert (
        "bar 1's verdict-table history cell '50/96 = 0.9999' prints a rate its "
        "own fraction does not recompute to" in errors[0]
    )


def test_reattributed_cell_extending_the_registered_name_detected(
    doc_tree: Path,
) -> None:
    # A row naming `…non_direct_accuracy_adjusted` CONTAINS the registered
    # identifier and states a different metric, so the name is matched whole
    # rather than as a substring.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| 1 | `EjecteeProofCrossTab.non_direct_accuracy` pooled |",
        "| 1 | `EjecteeProofCrossTab.non_direct_accuracy_adjusted` pooled |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 1 registered the cell 'EjecteeProofCrossTab.non_direct_accuracy' "
        "and its verdict-table row now names "
        "'EjecteeProofCrossTab.non_direct_accuracy_adjusted'" in error
        for error in errors
    )


def test_descriptive_words_outside_the_cell_identifier_stay_the_records(
    doc_tree: Path,
) -> None:
    # ...and the words the record writes AROUND the code span are its own, so
    # matching the identifier whole did not freeze the row's prose.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| 1 | `EjecteeProofCrossTab.non_direct_accuracy` pooled |",
        "| 1 | `EjecteeProofCrossTab.non_direct_accuracy` pooled over four sets |",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_pooled_row_contradicted_by_its_own_set_rows_detected(doc_tree: Path) -> None:
    # The pooled cell the verdict is read off is a SUM. Set cells reading 0/15
    # and 30/51 pool to 30/66, which misses the bar, while the pooled row and
    # the verdict above them go on saying 46/66 and MET.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| `samples/9p2i` | 14/27 = 0.5185 | 10/15 = 0.6667 (n = 15, not powered) |",
        "| `samples/9p2i` | 14/27 = 0.5185 | 0/15 = 0.0000 (n = 15, not powered) |",
    )
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_POWERED_SET_ROW,
        _FINDING_POWERED_SET_ROW.replace("36/51 = 0.7059", "30/51 = 0.5882"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 1's this record pooled row reads '46/66 = 0.6970', but its own "
        "four set rows pool to 30/66" in error
        for error in errors
    )


def test_pooled_count_contradicted_by_its_own_set_rows_detected(doc_tree: Path) -> None:
    # The same rule on the other cell shape: a count column pools by addition
    # too, so a bare total is held to the four counts under it.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| `samples/9p2i` | 13 | 5 |",
        "| `samples/9p2i` | 13 | 4 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 2's this record pooled row reads '20', but its own four set rows "
        "pool to 19" in error
        for error in errors
    )


def test_share_identity_broken_on_a_set_but_not_pooled_detected(
    doc_tree: Path,
) -> None:
    # The pooled cells are a sum, so moving one set's share up and another's
    # down by the same ejection preserves every pooled figure while the per-set
    # rows contradict the reporter counts printed a section above them.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| `samples/9p2i` | 7/13 = 0.5385 | 3/5 = 0.6000 |",
        "| `samples/9p2i` | 7/13 = 0.5385 | 2/5 = 0.4000 |",
    )
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| `ml_corpus/9p2i` | 23/29 = 0.7931 | 8/15 = 0.5333 |",
        "| `ml_corpus/9p2i` | 23/29 = 0.7931 | 9/15 = 0.6000 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "bar 4's 'samples/9p2i on this record' cell reads 2/5, but bars 3 and "
        "2 read 3 and 5" in error
        for error in errors
    )
    assert any(
        "bar 4's 'ml_corpus/9p2i on this record' cell reads 9/15, but bars 3 "
        "and 2 read 8 and 15" in error
        for error in errors
    )


def test_adoption_claim_beside_the_finding_sentence_detected(doc_tree: Path) -> None:
    # The required verdict sentence can be satisfied while the paragraph around
    # it says the opposite. This record adopted nothing and records no override
    # of its finding, so a page may not assert one beside its fall.
    _substitute(
        doc_tree,
        _HISTORY,
        "override was made.\n[Record]",
        "override was made. The owner overrode that finding and adopted the "
        "Wave-2 slate.\n[Record]",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "it states this record's fall beside 'overrode'" in error
        and "adopted nothing and records no override of it" in error
        for error in errors
    )


def test_the_previous_recordings_dated_override_is_left_alone(
    doc_tree: Path,
) -> None:
    # ...and the front door's account of the recording BEFORE this one — a real
    # override, stated beside the date it was made on, in the same paragraph as
    # this record's fall — is not a contradiction, so the rule did not become a
    # ban on the word.
    guide = _read(doc_tree, _READING_GUIDE)
    blocks = [
        block
        for _, block in check_doc_facts.prose_blocks(guide)
        if "innocent ejections fell from 46 to 20" in block
    ]
    assert len(blocks) == 1
    assert "override dated 2026-08-26" in blocks[0]
    assert check_doc_facts.check_facts(doc_tree) == []


def test_published_pass_count_that_the_verdicts_refute_detected(
    doc_tree: Path,
) -> None:
    # The verdict WORD carries no inventory: one bar missed out of four reads
    # "a finding" exactly as three missed out of four does, so the tally beside
    # it is its own claim and is held to the recomputed verdict column.
    _substitute(
        doc_tree,
        _README,
        "written down before the next recording; three passed",
        "written down before the next recording; two passed",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "states 'two' of them passed, and " in error and "makes it 'three'" in error
        for error in errors
    )


def test_published_registered_bar_count_that_the_table_refutes_detected(
    doc_tree: Path,
) -> None:
    # ...and the other half of the same tally: how many bars were registered at
    # all, which is the denominator every "three of four" claim rests on.
    _substitute(
        doc_tree,
        _README,
        "Four bars were written down before the next recording",
        "Three bars were written down before the next recording",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "states 'three' bars registered, and " in error and "makes it 'four'" in error
        for error in errors
    )


def test_front_door_recording_size_drift_detected(doc_tree: Path) -> None:
    # The provenance count a reader checks the whole account against is stated
    # on the front door and measured in the record, so it is derived from the
    # record's own four legs rather than typed beside them.
    _substitute(doc_tree, _HISTORY, "A 300-game recording", "A 301-game recording")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "the claim '301-game recording' is the size of the recording" in error
        and "come to 300 games" in error
        for error in errors
    )


def test_recording_size_follows_the_records_own_legs(doc_tree: Path) -> None:
    # ...derived, not pinned: a leg recorded at another size moves the count the
    # front door has to state, rather than the front door moving alone.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| 2 | `ml_corpus/9p2i` | 150/150 |",
        "| 2 | `ml_corpus/9p2i` | 140/140 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "the claim '300-game recording' is the size of the recording" in error
        and "come to 290 games" in error
        for error in errors
    )


def test_unreadable_leg_table_fails_loud(doc_tree: Path) -> None:
    # ...and a leg whose two halves disagree makes the total unreadable rather
    # than wrong. Reading on without one would disable every recording-size
    # check at once, so the table is reported by name; restored, it still holds
    # the front door's own count.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| 2 | `ml_corpus/9p2i` | 150/150 |",
        "| 2 | `ml_corpus/9p2i` | 150/151 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "its leg table cannot be located, or one of its legs states" in errors[0]
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| 2 | `ml_corpus/9p2i` | 150/151 |",
        "| 2 | `ml_corpus/9p2i` | 150/150 |",
    )
    _substitute(doc_tree, _HISTORY, "A 300-game recording", "A 301-game recording")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "the claim '301-game recording' is the size of the recording" in error
        and "come to 300 games" in error
        for error in errors
    )


def test_missing_verdict_table_fails_loud(doc_tree: Path) -> None:
    # Losing the table must not read as "nothing to be held to".
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        "| bar | cell | target |",
        "| criterion | cell | target |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_FINDING_AUDIT}:")
    assert "verdict table cannot be located" in errors[0]


def test_verdict_table_of_the_wrong_width_fails_loud(doc_tree: Path) -> None:
    # A dropped column would shift which cell reads as the verdict, which is
    # the one cell nothing else could catch — so the width is required.
    _substitute(
        doc_tree,
        _FINDING_AUDIT,
        _FINDING_INNOCENT_ROW,
        "| 2 | `MeetingFlagCrossTab` innocent ejections pooled | < 35 | 20 | **MET** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "verdict table cannot be located" in errors[0]


def test_standalone_finding_count_sentence_is_refused(doc_tree: Path) -> None:
    # The shape collision this passage is written around: the wrongful-ejection
    # gate admits only a count one of the two conviction partitions carries, so
    # a sentence naming ONLY this record's own count lands red...
    _substitute(
        doc_tree,
        _README,
        "Innocent ejections fell from 46 to 20, and 11 of those 20",
        "The recording fell to 20 innocent ejections. 11 of those 20",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        error.startswith(f"{_README}:")
        and "a wrongful-ejection sentence names neither the count" in error
        for error in errors
    )
    # ...and the two-part wording the committed page carries is what passes,
    # which ``test_unperturbed_copy_passes`` proves on the same tree.


def test_history_cell_naming_the_recording_before_the_previous_one_detected(
    doc_tree: Path,
) -> None:
    # The header names the recording this one replaced, so a history cell
    # holding the value from the recording BEFORE that — correct once, and
    # still internally consistent between the two tables — has to fail.
    stale = "310 / 310 = 1.0000 vs 46 / 125 = 0.3680"
    for document in (_README, _READING_GUIDE):
        _substitute(doc_tree, document, _PREVIOUS_PARTITION_CELL, stale)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "the 'At baseline 7' cell of results row" in errors[0]
    assert "recomputes to '326 / 326 = 1.0000 vs 61 / 103 = 0.5922'" in errors[0]


def test_vent_row_without_its_population_fails_loud(doc_tree: Path) -> None:
    # A row that drops its "(N meetings)" label still reads as a table but is
    # no longer checked against the pin, so the label itself is required.
    _substitute(doc_tree, _READING_GUIDE, "| yes (68 meetings) |", "| yes |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "the cross-tab's 'yes' row carries no '(N meetings)' population" in errors[0]


def test_unbolded_guide_exhibit_the_picker_dropped_detected(doc_tree: Path) -> None:
    # The rule binds every game the guide NAMES; markdown emphasis is not what
    # makes a mention count.
    _substitute(doc_tree, _READING_GUIDE, "**4p1i seed 11**", "4p1i seed 41")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names 4p1i seed 41 as an exhibit" in errors[0]


def test_guide_exhibit_the_picker_no_longer_carries_detected(doc_tree: Path) -> None:
    # The curated strip is committed data. A guide naming a game it dropped
    # points a reader at a card the spectator never opens.
    _substitute(doc_tree, _READING_GUIDE, "**9p2i seed 46**", "**9p2i seed 17**")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "names 9p2i seed 17 as an exhibit" in errors[0]
    assert _PICKER in errors[0]


def test_guide_exhibits_follow_a_recurated_picker(doc_tree: Path) -> None:
    # The picker decides, not the guide: dropping a featured entry breaks the
    # guide that still names it, which is what forces the two to be curated
    # together.
    text = _read(doc_tree, _PICKER)
    entry = '    set: "9p2i",\n    seed: 46,\n'
    assert entry in text
    _write(doc_tree, _PICKER, text.replace(entry, '    set: "9p2i",\n    seed: 47,\n'))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names 9p2i seed 46 as an exhibit" in errors[0]


def test_guide_with_too_few_exhibits_fails_loud(doc_tree: Path) -> None:
    # A paragraph that lost its exhibits would otherwise pass vacuously.
    _substitute(
        doc_tree, _READING_GUIDE, "**9p2i seed 46**", "that other nine-player game"
    )
    _substitute(doc_tree, _READING_GUIDE, "**4p1i seed 11**", "the smallest table here")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "names 1 featured games, fewer than the 2" in errors[0]


def test_missing_featured_list_fails_loud(doc_tree: Path) -> None:
    # Losing the list must not read as "no exhibits to check".
    _substitute(
        doc_tree,
        _PICKER,
        "export const FEATURED_GAMES: readonly FeaturedGame[] = [",
        "export const CURATED: readonly FeaturedGame[] = [",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no FEATURED_GAMES list" in errors[0]


def test_report_example_ejection_count_drift_detected(doc_tree: Path) -> None:
    # The example exists because the fake provider's report is empty; its
    # scalars come from the committed report, not from prose.
    _substitute(doc_tree, _README, "records 95 ejections", "records 97 ejections")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'95 ejections'" in errors[0]
    assert "total_ejections" in errors[0]


def test_report_example_rate_drift_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _README, "vote correctness 0.915", "vote correctness 0.950")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'vote correctness 0.915'" in errors[0]


def test_report_example_accuracy_drift_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _README, "ejection accuracy 0.863", "ejection accuracy 0.800")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'ejection accuracy 0.863'" in errors[0]


def test_missing_report_example_paragraph_fails_loud(doc_tree: Path) -> None:
    # Dropping the example must not read as "nothing to check": the front door
    # would then be silent about what a fake-provider report looks like.
    _substitute(
        doc_tree,
        _README,
        "The fake provider's report is empty on purpose.",
        "The fake provider's report is unusual.",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no paragraph naming" in errors[0]


def test_missing_vent_crosstab_fails_loud(doc_tree: Path) -> None:
    # Losing the table must not read as "nothing to derive from".
    _substitute(
        doc_tree, _READING_GUIDE, "| Meeting contains a vent flag |", "| Meetings |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no vent cross-tab" in errors[0]


def test_glossary_ladder_tip_drift_detected(doc_tree: Path) -> None:
    # Every document that may state the tip is scanned, not only the README:
    # the glossary defines the term, so a stale tip there is the same drift.
    _substitute(
        doc_tree,
        _GLOSSARY,
        "the newest — the ladder tip — is baseline 8",
        "the newest — the ladder tip — is baseline 5",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_GLOSSARY)
    assert "names baseline 5" in errors[0]


def test_unaccounted_phase_contract_detected(doc_tree: Path) -> None:
    # A new phase document that neither the phase table nor the history links:
    # the front door would silently stop covering the project.
    (doc_tree / "tasks" / "phase-99.md").write_text("# Phase 99\n", encoding="utf-8")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "tasks/phase-99.md" in errors[0]
    assert _HISTORY in errors[0]


def test_unindexed_audit_detected(doc_tree: Path) -> None:
    # A new audit lands and nobody indexes it — the orphan state the index was
    # written to end, reintroduced one file at a time.
    (doc_tree / "audits" / "audit-phase-99-close.md").write_text(
        "# Phase 99 close\n", encoding="utf-8"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "audit-phase-99-close.md is not indexed" in errors[0]


def test_indexed_audit_that_no_longer_exists_detected(doc_tree: Path) -> None:
    # The other direction: an indexed record is deleted and the row becomes a
    # dead link a reader follows.
    (doc_tree / "audits" / "audit-phase-19-close.md").unlink()
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("indexes audit-phase-19-close.md" in error for error in errors)
    # Every other error is the same deletion seen through another reader: the
    # front-door documents that pointed at the record now point at nothing, and
    # the conviction-partition figure loses the table it is derived from.
    assert all(
        "indexes audit-phase-19-close.md" in error
        or "does not exist" in error
        or "unreadable" in error
        for error in errors
    )


def test_duplicated_audit_index_row_detected(doc_tree: Path) -> None:
    # Two rows for one record are two descriptions to keep in step.
    row = "- [audit-phase-19-close.md](audit-phase-19-close.md) — the phase close"
    text = _read(doc_tree, _AUDITS_INDEX)
    assert row in text
    _write(doc_tree, _AUDITS_INDEX, text.replace(row, f"{row}\n{row}", 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "audit-phase-19-close.md is indexed 2 times" in errors[0]


def test_unnamed_audits_subdirectory_detected(doc_tree: Path) -> None:
    # Sub-directories are indexed as units, but they ARE indexed: dropping the
    # review directory's name leaves its dozens of files unreachable.
    _substitute(doc_tree, _AUDITS_INDEX, "review-2026-08-19/", "the review/")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("does not name the review-2026-08-19/ directory" in e for e in errors)


def test_results_figure_drift_detected(doc_tree: Path) -> None:
    # The numbers are stated once: a figure edited in the README and not in the
    # guide is two answers to the same question. The firewall row is the one
    # with no countable source, so this exercises the agreement check alone.
    _substitute(
        doc_tree,
        _README,
        "| Observation-firewall violations, all phases | zero |",
        "| Observation-firewall violations, all phases | one |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'one'" in errors[0]
    assert "'zero'" in errors[0]


def test_results_row_absent_from_the_guide_detected(doc_tree: Path) -> None:
    # A README row the canonical table does not carry has no committed source
    # behind it.
    _substitute(
        doc_tree,
        _README,
        "| Observation-firewall violations, all phases |",
        "| Observation-firewall violations, ever |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'Observation-firewall violations, ever'" in errors[0]
    assert _READING_GUIDE in errors[0]


def test_stubbed_results_table_detected(doc_tree: Path) -> None:
    # Agreement over a stub is not agreement: a gutted table must fail rather
    # than pass vacuously.
    text = _read(doc_tree, _README)
    gutted = (
        "| Impostor win rate",
        "| Eject ",
        "| Ejection accuracy ",
        "| Learned tactical policies ",
    )
    kept = [line for line in text.splitlines() if not line.startswith(gutted)]
    _write(doc_tree, _README, "\n".join(kept) + "\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("fewer than the 4 this check needs" in error for error in errors)


def test_unstamped_volatile_count_detected(doc_tree: Path) -> None:
    # A merged-PR count stated without an as-of date is stale the week after
    # it is written, and nothing in the repo can tell the reader that.
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README) + "\nThe project has 364 merged pull requests.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "merged pull requests count '364 merged pull requests'" in errors[0]
    assert "as of YYYY-MM-DD" in errors[0]


def test_malformed_volatile_stamp_detected(doc_tree: Path) -> None:
    # The stamp's SHAPE is what this check owns — the value cannot be checked
    # without reaching the network, and a stamp that is not a date is drift.
    _substitute(
        doc_tree,
        _README,
        "snapshot of `main` as of 2026-08-19",
        "snapshot of `main` as of 2026-13-45",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 3
    assert all("is not a calendar date" in error for error in errors)


def test_line_citation_in_the_reading_guide_detected(doc_tree: Path) -> None:
    # A file:line citation is correct until the next edit of the file it names;
    # the guide carried two dozen of them and now pins the zero.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "the recursive packet\nsweep in [eval/leak_scan.py](../eval/leak_scan.py)",
        "the recursive packet\nsweep in eval/leak_scan.py:214",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'eval/leak_scan.py:214'" in errors[0]
    assert "cite a heading anchor" in errors[0]


def test_broken_relative_link_detected(doc_tree: Path) -> None:
    # The front door's relative links are 0-broken and stay that way.
    _substitute(
        doc_tree,
        _README,
        "[Architecture](docs/architecture.md)",
        "[Architecture](docs/architecture-notes.md)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'docs/architecture-notes.md'" in errors[0]
    assert "does not exist" in errors[0]


def test_broken_relative_link_on_a_published_page_detected(doc_tree: Path) -> None:
    # The lessons page and the review index carry the same link rule as the
    # front door: they are published surfaces, not scratch notes.
    _substitute(
        doc_tree,
        _LESSONS,
        "(../CONTRIBUTING.md)",
        "(../CONTRIBUTING.markdown)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_LESSONS}: ")
    assert "'../CONTRIBUTING.markdown'" in errors[0]
    assert "does not exist" in errors[0]


def test_broken_relative_link_on_the_review_index_detected(doc_tree: Path) -> None:
    _substitute(
        doc_tree,
        _REVIEW_INDEX,
        "(A/verdicts.md)",
        "(A/verdict.md)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert errors and all(error.startswith(f"{_REVIEW_INDEX}: ") for error in errors)
    assert all("'A/verdict.md'" in error for error in errors)


def test_mapped_task_with_no_contract_detected(doc_tree: Path) -> None:
    # The map's whole claim is "here is the change that closed it": a task id
    # no contract owns makes that unverifiable, and the row is named.
    _substitute(doc_tree, _REVIEW_INDEX, _MAP_TASK_CELL, "| 20.99 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _MAP_FINDING.strip("`") in errors[0]
    assert "20.99" in errors[0]
    assert "not a contract" in errors[0]


def test_map_row_moved_to_a_neighbouring_task_detected(doc_tree: Path) -> None:
    # A real contract that never names this finding: the id has to appear in
    # the section credited with closing it, or the row is decoration.
    _substitute(doc_tree, _REVIEW_INDEX, _MAP_TASK_CELL, "| 20.11 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert f"never names {_MAP_FINDING.strip('`')}" in errors[0]


def test_map_row_whose_link_disagrees_with_its_label_detected(doc_tree: Path) -> None:
    _substitute(
        doc_tree,
        _REVIEW_INDEX,
        "[#363](https://github.com/dkdan10/AiLibi/pull/363)",
        "[#363](https://github.com/dkdan10/AiLibi/pull/633)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "#363 but links pull request #633" in errors[0]


def test_map_row_pointing_at_another_repository_detected(doc_tree: Path) -> None:
    # A number this history carries says nothing about someone else's fork.
    _substitute(
        doc_tree,
        _REVIEW_INDEX,
        "[#363](https://github.com/dkdan10/AiLibi/pull/363)",
        "[#363](https://github.com/someone-else/a-fork/pull/363)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _MAP_FINDING in errors[0]
    assert "does not parse" in errors[0]


def test_dropped_map_row_detected(doc_tree: Path) -> None:
    # The index's stated invariant is that it accounts for every finding the
    # phase touched. Deleting one row must fail, not quietly shrink the table.
    index = _read(doc_tree, _REVIEW_INDEX)
    row = _map_row(index, _MAP_ONLY_FINDING)
    _write(doc_tree, _REVIEW_INDEX, index.replace(row + "\n", ""))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    finding = _MAP_ONLY_FINDING.strip("`")
    assert errors[0].startswith(f"{_REVIEW_INDEX}: {finding} is named")
    assert "appears nowhere in the index" in errors[0]


def test_duplicated_map_row_detected(doc_tree: Path) -> None:
    index = _read(doc_tree, _REVIEW_INDEX)
    row = _map_row(index, _MAP_ONLY_FINDING)
    _write(doc_tree, _REVIEW_INDEX, index.replace(row + "\n", row + "\n" + row + "\n"))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "is mapped twice" in errors[0]
    assert _MAP_ONLY_FINDING.strip("`") in errors[0]


def test_deleted_acted_on_map_fails_loud(doc_tree: Path) -> None:
    # An emptied table must not read as "nothing drifted".
    index = _read(doc_tree, _REVIEW_INDEX)
    header = "| " + " | ".join(check_doc_facts._REVIEW_MAP_HEADER) + " |"
    kept = [line for line in index.splitlines() if not line.startswith("| `")]
    _write(doc_tree, _REVIEW_INDEX, "\n".join(kept))
    assert header in index
    errors = check_doc_facts.check_facts(doc_tree)
    assert errors and "no acted-on map rows found" in errors[0]


def test_missing_document_reported(doc_tree: Path) -> None:
    (doc_tree / _ENV_EXAMPLE).unlink()
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_ENV_EXAMPLE}: unreadable")


def test_main_reports_every_failure_at_once(
    doc_tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _substitute(doc_tree, _README, "2026-08-31", "2026-08-19")
    _substitute(doc_tree, _README, "36% (4p1i)", "30% (4p1i)")
    assert check_doc_facts.main(["--repo-root", str(doc_tree)]) == 1
    err = capsys.readouterr().err
    assert "Doc-fact check failed:" in err
    assert "'36% (4p1i)'" in err
    assert "'2026-08-31'" in err


def test_main_clean_repo_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert check_doc_facts.main(["--repo-root", str(_REPO_ROOT)]) == 0
    assert "Doc facts verified" in capsys.readouterr().out


def test_cli_entry_point_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Doc facts verified" in proc.stdout


# --------------------------------------------------------------------------- #
# The architecture exhibit: the committed picture, the note's size, and the
# contract -> prompt -> pull-request triple on the front door.
#
# These pin COMMITTED BYTES rather than exercising the checker above, so each is
# written as a pure function of the text it reads and every one runs twice: once
# against the tree, once against a perturbation that has to make it fire. They
# live here because the front door is what they guard.
# --------------------------------------------------------------------------- #

_ARCHITECTURE_SVG = "docs/media/architecture.svg"
_ARCHITECTURE_NOTE = "docs/architecture.md"
# Two printed pages of prose. The note was 1,089 words when the portfolio review
# called it the document a reader wants first; the ceiling exists so its growth
# fails a gate instead of a reader.
_ARCHITECTURE_WORD_BUDGET = 1_300
# A hand-authored diagram bigger than this is a raster export in disguise, or has
# stopped being one picture.
_SVG_BYTE_CEILING = 60_000

# What the picture must SAY, not merely how it is built: the packages of the
# layering, the protocol the reasoning layer reaches a model through, the
# firewall contract by name, and the legend that stops arrows being read as
# imports. Matched against the concatenated <text> content, so labels flattened
# into outlined paths fail here too.
_SVG_REQUIRED_LABELS = (
    "engine/",
    "observation/",
    "agents/",
    "meetings/",
    "llm/",
    "orchestrator/",
    "eval/",
    "api/",
    "frontend/",
    "LLMClient Protocol",
    "ObservationPacket",
    "ActionIntent",
    "GENERATED",
    "Agents must not",
    "import engine",
    "import-linter",
    "Arrows are data flow",
    "imports run the other way",
)
_DARK_THEME_BLOCK = "@media (prefers-color-scheme: dark)"
_HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b")
_COLOUR_KEYWORD = re.compile(r"\b(?:black|white)\b", re.IGNORECASE)
_CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]*)")

# Legibility is a contrast ratio, not the absence of the two extreme colours: a
# palette of two near-identical mid-tones is unreadable and contains neither.
# The two `svg { … }` blocks are the light palette and the dark one the media
# query swaps in; every ink is measured against every ground it is painted on.
_PALETTE_BLOCK = re.compile(r"svg\s*\{([^}]*)\}")
_CUSTOM_PROPERTY = re.compile(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;")
_CONTRAST_FLOOR = 4.5

# The backdrop is deliberately translucent, so the ground under a label on it is
# not the declared colour but the composite over whatever page carries the image
# — and `prefers-color-scheme` follows the reader's OS while GitHub's own theme
# does not have to, so both pages are live for both palettes. The mismatch case
# (light palette on a dark page) is the one that decides legibility, and reading
# the declared colour instead of the composite is what hid it (Codex, PR #374).
_BACKDROP_OPACITY = re.compile(r'class="backdrop"[^>]*fill-opacity="([\d.]+)"')
_PAGE_GROUNDS = (("a light page", "#ffffff"), ("a dark page", "#0d1117"))

# Which ground each text class is painted on. The BINDING from a class to the
# colour it inks with is read out of the stylesheet, never assumed, so
# repointing `.body` at `--card` fails here instead of rendering invisibly
# (Codex, PR #374). Only the layout — which class sits on which rect — is
# pinned, and the covering assertion below makes that safe by default: a text
# class that is not in this table is unaccounted for and fails.
_TEXT_CLASS_GROUNDS: dict[str, tuple[str, ...]] = {
    "title": ("backdrop",),
    "subtitle": ("backdrop",),
    "legend": ("backdrop",),
    "flow-label": ("backdrop",),
    "fire-label": ("backdrop",),
    "fire-note": ("backdrop",),
    "name": ("card-strong",),
    "name-sm": ("card",),
    "body": ("card", "card-strong"),
}
_CSS_RULE = re.compile(r"\.([\w-]+)\s*\{([^}]*)\}")
_FILL_VARIABLE = re.compile(r"fill:\s*var\(--([\w-]+)\)")
_TEXT_CLASS_ATTR = re.compile(r'<text[^>]*class="([\w-]+)"')

# The artifacts the front-door exhibit quotes, in the order it quotes them. The
# two markers share no prefix, so losing the opener cannot be mistaken for an
# empty exhibit that happens to start at the closer.
_EXHIBIT_OPEN = "<!-- EXHIBIT:"
_EXHIBIT_CLOSE = "<!-- EXHIBIT-END -->"
_EXHIBIT_SOURCES = (
    "tasks/phase-19.md",
    "agent_prompts/task-19-2-in-code-truth.md",
)
# A line the README elides rather than quotes. Every other line inside a fence is
# a claim that those bytes are in the source file.
_ELISION = "…"
_FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.MULTILINE | re.DOTALL)
# The repository is captured, not assumed: a number reachable in THIS history
# says nothing about a link that points at someone else's pull request.
_EXHIBIT_REPO = "dkdan10/AiLibi"
_PULL_REQUEST_URL = re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)")
_PR_SUBJECT_SUFFIX = re.compile(r"\(#(\d+)\)\s*\Z")
# A squashed task merge: the task it closed and the pull request it arrived on.
# "follow-up" merges carry the same task id, so the LAST one read wins and the
# map may credit either — both are that task's work.
_TASK_SUBJECT = re.compile(r"\Atask (\d+\.\d+)(?: follow-up)?: .*\(#(\d+)\)\s*\Z")


def _committed(name: str) -> str:
    return (_REPO_ROOT / name).read_text(encoding="utf-8")


def _channels(colour: str) -> tuple[int, int, int]:
    digits = colour.lstrip("#")
    if len(digits) in (3, 4):
        digits = "".join(digit * 2 for digit in digits)
    red, green, blue = (int(digits[index : index + 2], 16) for index in (0, 2, 4))
    return red, green, blue


def _relative_luminance(colour: str) -> float:
    """WCAG relative luminance of a `#rgb` / `#rrggbb` colour."""

    linear = [
        value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
        for value in (channel / 255 for channel in _channels(colour))
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(ink: str, ground: str) -> float:
    luminances = sorted((_relative_luminance(ink), _relative_luminance(ground)))
    return (luminances[1] + 0.05) / (luminances[0] + 0.05)


def _over(colour: str, page: str, alpha: float) -> str:
    """`colour` at `alpha` composited over `page` — the ground a reader sees."""

    return "#" + "".join(
        f"{round(alpha * front + (1 - alpha) * back):02x}"
        for front, back in zip(_channels(colour), _channels(page), strict=True)
    )


def _contrast_problems(text: str) -> list[str]:
    """Every ink/ground pair, in both palettes, that falls under the floor."""

    palettes = _PALETTE_BLOCK.findall(text)
    if len(palettes) != 2:
        return [
            f"{_ARCHITECTURE_SVG}: found {len(palettes)} `svg {{ … }}` palette "
            "blocks, not the light one and the dark one"
        ]
    light = dict(_CUSTOM_PROPERTY.findall(palettes[0]))
    dark = {**light, **dict(_CUSTOM_PROPERTY.findall(palettes[1]))}

    opacity = _BACKDROP_OPACITY.search(text)
    if opacity is None or float(opacity.group(1)) >= 1.0:
        return [
            f"{_ARCHITECTURE_SVG}: the backdrop is opaque; it must let the "
            "reader's page through, so that a light card is never painted flat "
            "over a dark one"
        ]
    alpha = float(opacity.group(1))

    problems: list[str] = []
    used = set(_TEXT_CLASS_ATTR.findall(text))
    unaccounted = used - _TEXT_CLASS_GROUNDS.keys()
    unused = _TEXT_CLASS_GROUNDS.keys() - used
    if unaccounted or unused:
        problems.append(
            f"{_ARCHITECTURE_SVG}: the text classes and the ground table "
            f"disagree — unaccounted {sorted(unaccounted)}, "
            f"unused {sorted(unused)}"
        )

    inks = {
        name: match.group(1)
        for name, body in _CSS_RULE.findall(text)
        if (match := _FILL_VARIABLE.search(body)) is not None
    }
    for name in sorted(used & _TEXT_CLASS_GROUNDS.keys()):
        if name not in inks:
            problems.append(
                f"{_ARCHITECTURE_SVG}: .{name} inks with no `fill: var(--…)`, "
                "so nothing here can measure what it renders as"
            )
            continue
        ink = inks[name]
        for theme, palette in (("light", light), ("dark", dark)):
            for ground_name in _TEXT_CLASS_GROUNDS[name]:
                if ink not in palette or ground_name not in palette:
                    problems.append(
                        f"{_ARCHITECTURE_SVG}: the {theme} palette defines no "
                        f"--{ink} on --{ground_name} pair"
                    )
                    continue
                if ground_name != "backdrop":
                    # Cards are painted opaque, so their fill IS the ground.
                    ratio = _contrast_ratio(palette[ink], palette[ground_name])
                    if ratio < _CONTRAST_FLOOR:
                        problems.append(
                            f"{_ARCHITECTURE_SVG}: .{name} (--{ink}) on "
                            f"--{ground_name} in the {theme} palette contrasts "
                            f"{ratio:.1f}:1, under the {_CONTRAST_FLOOR}:1 floor"
                        )
                    continue
                for where, page in _PAGE_GROUNDS:
                    ground = _over(palette["backdrop"], page, alpha)
                    ratio = _contrast_ratio(palette[ink], ground)
                    if ratio < _CONTRAST_FLOOR:
                        problems.append(
                            f"{_ARCHITECTURE_SVG}: .{name} (--{ink}) on the "
                            f"{theme} backdrop over {where} ({ground}) contrasts "
                            f"{ratio:.1f}:1, under the {_CONTRAST_FLOOR}:1 floor"
                        )
    return problems


def _svg_problems(text: str) -> list[str]:
    """Every way the committed picture stops being hand-authored, legible text."""

    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        return [f"{_ARCHITECTURE_SVG}: does not parse as XML ({exc})"]

    problems: list[str] = []
    size = len(text.encode("utf-8"))
    if size > _SVG_BYTE_CEILING:
        problems.append(
            f"{_ARCHITECTURE_SVG}: {size} bytes, over the {_SVG_BYTE_CEILING}-byte "
            "ceiling for a hand-authored diagram"
        )

    tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
    problems.extend(
        f"{_ARCHITECTURE_SVG}: carries <{banned}>; the picture must be "
        "hand-authored SVG, not an embedded raster or a foreign document"
        for banned in ("image", "foreignObject")
        if banned in tags
    )
    if any(
        name.rsplit("}", 1)[-1] == "href"
        for element in root.iter()
        for name in element.attrib
    ):
        problems.append(
            f"{_ARCHITECTURE_SVG}: an element carries an href; the picture must "
            "reference nothing outside itself"
        )
    if "@font-face" in text or "data:" in text:
        problems.append(
            f"{_ARCHITECTURE_SVG}: declares a downloaded or embedded asset; "
            "system font families and inline shapes only"
        )
    problems.extend(
        f"{_ARCHITECTURE_SVG}: url({target!r}) points outside the file"
        for target in _CSS_URL.findall(text)
        if not target.startswith("#")
    )

    for token in _HEX_COLOUR.findall(text):
        digits = token[1:]
        if len(digits) in (3, 4):
            digits = "".join(digit * 2 for digit in digits)
        if digits[:6].lower() in {"000000", "ffffff"}:
            problems.append(
                f"{_ARCHITECTURE_SVG}: uses {token}; pure black and pure white "
                "read as damage in one of the two GitHub themes"
            )
    keyword = _COLOUR_KEYWORD.search(text)
    if keyword is not None:
        problems.append(
            f"{_ARCHITECTURE_SVG}: uses the colour keyword {keyword.group(0)!r}; "
            "pure black and pure white read as damage in one of the two themes"
        )
    if _DARK_THEME_BLOCK not in text:
        problems.append(
            f"{_ARCHITECTURE_SVG}: has no {_DARK_THEME_BLOCK} block, so it cannot "
            "follow the reader's theme"
        )
    problems.extend(_contrast_problems(text))

    spoken = "\n".join(
        element.text or ""
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "text"
    )
    if not spoken.strip():
        problems.append(
            f"{_ARCHITECTURE_SVG}: holds no <text>; a diagram of outlined paths is "
            "neither searchable nor diffable"
        )
    problems.extend(
        f"{_ARCHITECTURE_SVG}: never says {label!r}"
        for label in _SVG_REQUIRED_LABELS
        if label not in spoken
    )
    return problems


def _word_budget_problems(text: str) -> list[str]:
    """The architecture note against the two-page ceiling it is held to."""

    words = len(text.split())
    if words <= _ARCHITECTURE_WORD_BUDGET:
        return []
    return [
        f"{_ARCHITECTURE_NOTE}: {words} words, over the "
        f"{_ARCHITECTURE_WORD_BUDGET}-word ceiling — it is the page a reader is "
        "sent to first, and it has to stay readable in one sitting"
    ]


def _verbatim_runs(block: str) -> list[str]:
    """A fenced excerpt split into the runs it claims are verbatim."""

    runs: list[str] = []
    current: list[str] = []
    for line in block.splitlines():
        if line.startswith(_ELISION):
            if current:
                runs.append("\n".join(current))
                current = []
            continue
        current.append(line)
    if current:
        runs.append("\n".join(current))
    return [run for run in runs if run.strip()]


def _pull_request_numbers(repo_root: Path) -> set[int] | None:
    """Every ``(#N)`` merged onto this branch, or ``None`` with no full history.

    ``None`` on a shallow clone as well as on a missing git: hosted CI checks out
    depth 1, and a truncated log would report every pull request as unreachable.
    Callers report that as a skip, never as a pass — the ``in_tree_inventory``
    precedent in ``scripts/verify_ml_evidence.py``.
    """

    try:
        shallow = subprocess.run(
            ["git", "rev-parse", "--is-shallow-repository"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if shallow.returncode != 0 or shallow.stdout.strip() != "false":
            return None
        log = subprocess.run(
            ["git", "log", "--format=%s"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if log.returncode != 0:
        return None
    numbers: set[int] = set()
    for subject in log.stdout.splitlines():
        match = _PR_SUBJECT_SUFFIX.search(subject)
        if match is not None:
            numbers.add(int(match.group(1)))
    return numbers


def _merged_task_ids(repo_root: Path) -> dict[int, str] | None:
    """``{pull request: task id}`` from the merge subjects, or ``None``.

    ``None`` under the same conditions as :func:`_pull_request_numbers`: without
    full history the mapping would be missing arbitrary rows.
    """

    try:
        shallow = subprocess.run(
            ["git", "rev-parse", "--is-shallow-repository"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if shallow.returncode != 0 or shallow.stdout.strip() != "false":
            return None
        log = subprocess.run(
            ["git", "log", "--format=%s"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if log.returncode != 0:
        return None
    tasks: dict[int, str] = {}
    for subject in log.stdout.splitlines():
        match = _TASK_SUBJECT.match(subject)
        if match is not None:
            tasks[int(match.group(2))] = match.group(1)
    return tasks


def _map_pull_request_problems(
    index: str, pull_requests: set[int], merged_tasks: dict[int, str]
) -> list[str]:
    """Every acted-on map row whose pull request does not resolve to its task.

    The git-history half of the map check: ``check_doc_facts`` resolves the task
    id against the phase contract, and this resolves the number against the
    subjects merged onto this branch — both that some commit carries it, and
    that the commit carrying it is the row's OWN task, so two valid numbers
    cannot be swapped between rows. It lives here because the caller can skip on
    a shallow clone, which a gate script running in CI could not.
    """

    problems: list[str] = []
    for line, finding, task, number in check_doc_facts.review_map_rows(index):
        if number not in pull_requests:
            problems.append(
                f"{_REVIEW_INDEX}:{line}: the {finding} row credits pull request "
                f"#{number}, which closed nothing reachable from HEAD — no commit "
                "subject ends in its number."
            )
        elif merged_tasks.get(number) != task:
            problems.append(
                f"{_REVIEW_INDEX}:{line}: the {finding} row credits task {task} "
                f"with pull request #{number}, whose merge subject names "
                f"{merged_tasks.get(number, 'no task')}."
            )
    return problems


def _exhibit_problems(
    readme: str, repo_root: Path, pull_requests: set[int]
) -> list[str]:
    """Every way the contract -> prompt -> pull-request exhibit stops resolving."""

    start = readme.find(_EXHIBIT_OPEN)
    end = readme.find(_EXHIBIT_CLOSE)
    if start < 0 or end < start:
        return [f"{_README}: the exhibit's {_EXHIBIT_OPEN} … marker pair is gone"]
    region = readme[start:end]

    problems: list[str] = []
    quoted = _FENCE.findall(region)
    if len(quoted) != len(_EXHIBIT_SOURCES):
        return [
            f"{_README}: the exhibit quotes {len(quoted)} sources, not "
            f"{len(_EXHIBIT_SOURCES)} — the contract, then the prompt made from it"
        ]

    for source, block in zip(_EXHIBIT_SOURCES, quoted, strict=True):
        if f"]({source})" not in readme:
            problems.append(f"{_README}: the exhibit no longer links {source}")
        path = repo_root / source
        if not path.is_file():
            problems.append(f"{_README}: the exhibit quotes {source}, which is gone")
            continue
        original = path.read_text(encoding="utf-8")
        problems.extend(
            f"{_README}: the excerpt beginning {run.splitlines()[0]!r} is no longer "
            f"a verbatim run of {source}"
            for run in _verbatim_runs(block)
            if run not in original
        )

    links = _PULL_REQUEST_URL.findall(region)
    if len(links) != 1:
        problems.append(
            f"{_README}: the exhibit names {len(links)} pull requests, not one"
        )
    for repository, number in links:
        if repository != _EXHIBIT_REPO:
            problems.append(
                f"{_README}: the exhibit points at a pull request in "
                f"{repository}, not {_EXHIBIT_REPO}"
            )
        elif int(number) not in pull_requests:
            problems.append(
                f"{_README}: pull request #{number} closed nothing reachable from "
                "HEAD — no commit subject ends in its number"
            )
    return problems


def test_the_committed_picture_is_hand_authored_legible_text() -> None:
    assert _svg_problems(_committed(_ARCHITECTURE_SVG)) == []


@pytest.mark.parametrize(
    ("original", "planted"),
    [
        ('<rect class="backdrop"', '<image href="shot.png" class="backdrop"'),
        ("<defs>", '<foreignObject width="1" height="1"/><defs>'),
        ("--ink: #1f2b36;", "--ink: #000000;"),
        ("--card: #f8fafb;", "--card: white;"),
        (_DARK_THEME_BLOCK, "@media (min-width: 900px)"),
        ("ui-sans-serif", "url(https://fonts.example/f.woff2), ui-sans-serif"),
        (">frontend/<", ">the web app<"),
        # The leading ">" keeps these off the <desc>, whose copy of the same
        # words is not what a reader of the picture sees.
        (">Arrows are data flow;", ">Boxes and lines,"),
        (">Agents must not<", ">Nothing may<"),
    ],
)
def test_a_perturbed_picture_is_rejected(original: str, planted: str) -> None:
    """One defect at a time, each of which has to make the pin fire."""

    committed = _committed(_ARCHITECTURE_SVG)
    perturbed = committed.replace(original, planted, 1)
    assert perturbed != committed, original
    assert _svg_problems(perturbed), planted


def test_an_oversized_picture_is_rejected() -> None:
    bloated = _committed(_ARCHITECTURE_SVG).replace(
        "</svg>", f"<!-- {'p' * _SVG_BYTE_CEILING} -->\n</svg>", 1
    )
    assert any("over the" in problem for problem in _svg_problems(bloated))


def test_an_unparseable_picture_is_rejected() -> None:
    problems = _svg_problems("<svg><rect></svg>")
    assert problems and "does not parse" in problems[0]


def test_the_architecture_note_stays_inside_two_pages() -> None:
    assert _word_budget_problems(_committed(_ARCHITECTURE_NOTE)) == []


def test_an_architecture_note_that_outgrows_two_pages_is_rejected() -> None:
    padded = _committed(_ARCHITECTURE_NOTE) + " word" * _ARCHITECTURE_WORD_BUDGET
    problems = _word_budget_problems(padded)
    assert problems and "word ceiling" in problems[0]


def test_the_front_door_exhibit_resolves() -> None:
    pull_requests = _pull_request_numbers(_REPO_ROOT)
    if pull_requests is None:
        pytest.skip("no full git history here; the exhibit's PR cannot be resolved")
    assert _exhibit_problems(_committed(_README), _REPO_ROOT, pull_requests) == []


def test_an_exhibit_excerpt_that_drifted_from_its_source_is_rejected() -> None:
    """The point of the pin: a contract edit cannot silently falsify the quote."""

    drifted = _committed(_README).replace(
        "- meetings/transcript.py; (same)", "- meetings/transcript.py; (unchanged)", 1
    )
    problems = _exhibit_problems(drifted, _REPO_ROOT, {328})
    assert any("verbatim run" in problem for problem in problems), problems


def test_an_exhibit_pull_request_absent_from_history_is_rejected() -> None:
    problems = _exhibit_problems(_committed(_README), _REPO_ROOT, {1})
    assert any("reachable from HEAD" in problem for problem in problems), problems


def test_an_exhibit_pull_request_in_another_repository_is_rejected() -> None:
    """A number this history can reach says nothing about someone else's repo."""

    elsewhere = _committed(_README).replace(
        f"https://github.com/{_EXHIBIT_REPO}/pull/",
        "https://github.com/someone-else/a-fork/pull/",
        1,
    )
    problems = _exhibit_problems(elsewhere, _REPO_ROOT, {328})
    assert any("someone-else/a-fork" in problem for problem in problems), problems


def test_the_review_maps_pull_requests_resolve() -> None:
    """ "Here is the fix" is a claim, so every number in it is resolved."""

    pull_requests = _pull_request_numbers(_REPO_ROOT)
    merged_tasks = _merged_task_ids(_REPO_ROOT)
    if pull_requests is None or merged_tasks is None:
        pytest.skip("no full git history here; the map's PRs cannot be resolved")
    index = _committed(_REVIEW_INDEX)
    assert check_doc_facts.review_map_rows(index), "the acted-on map parsed to no rows"
    assert _map_pull_request_problems(index, pull_requests, merged_tasks) == []


def test_a_mapped_pull_request_absent_from_history_is_rejected() -> None:
    index = _committed(_REVIEW_INDEX)
    rows = check_doc_facts.review_map_rows(index)
    merged = {number: task for _, _, task, number in rows}
    dropped = rows[0][3]
    named = {finding for _, finding, _, number in rows if number == dropped}
    problems = _map_pull_request_problems(index, set(merged) - {dropped}, merged)
    assert len(problems) == len(named), problems
    assert all(any(finding in problem for finding in named) for problem in problems)
    assert all("reachable from HEAD" in problem for problem in problems), problems


def test_two_valid_pull_requests_swapped_between_rows_are_rejected() -> None:
    """Reachability alone is not resolution: the number must be the row's own."""

    index = _committed(_REVIEW_INDEX)
    by_task = {
        task: number for _, _, task, number in check_doc_facts.review_map_rows(index)
    }
    first, second = sorted(by_task)[:2]
    swapped = dict(by_task)
    swapped[first], swapped[second] = by_task[second], by_task[first]
    merged = {number: task for task, number in swapped.items()}
    problems = _map_pull_request_problems(index, set(merged), merged)
    assert problems, "a swapped pull request has to be caught"
    assert all("whose merge subject names" in problem for problem in problems), problems


def test_a_low_contrast_palette_is_rejected() -> None:
    """The legibility gate measures contrast, not the absence of the extremes."""

    washed_out = _committed(_ARCHITECTURE_SVG).replace(
        "--muted: #485560;", "--muted: #e6eaee;", 1
    )
    problems = _svg_problems(washed_out)
    assert any("under the 4.5:1 floor" in problem for problem in problems), problems
    assert all("pure black" not in problem for problem in problems), problems


def test_an_ink_that_only_fails_composited_is_rejected() -> None:
    """The ground is the composite, not the declared backdrop.

    `#a8452a` clears the floor against the declared `#eef1f5` and falls under it
    once the 90%-opaque backdrop is composited over a dark page — the exact hole
    a check that read the declared colour could not see.
    """

    flat_only = _committed(_ARCHITECTURE_SVG).replace(
        "--fire: #973b21;", "--fire: #a8452a;", 1
    )
    assert _contrast_ratio("#a8452a", "#eef1f5") >= _CONTRAST_FLOOR
    problems = _svg_problems(flat_only)
    assert any("over a dark page" in problem for problem in problems), problems


def test_an_opaque_backdrop_is_rejected() -> None:
    """An opaque light card over a dark page is the failure mode being avoided."""

    painted_flat = _committed(_ARCHITECTURE_SVG).replace(
        'fill-opacity="0.9"', 'fill-opacity="1"', 1
    )
    problems = _svg_problems(painted_flat)
    assert any("backdrop is opaque" in problem for problem in problems), problems


def test_a_text_class_repointed_at_its_own_ground_is_rejected() -> None:
    """The ink of a class is read from the stylesheet, never assumed.

    An ordinary-looking style edit — `.body` inking with the card colour it is
    painted on — renders every card label invisible while changing no palette
    value, so a checker holding hard-coded pairs would see nothing.
    """

    invisible = _committed(_ARCHITECTURE_SVG).replace(
        ".body { fill: var(--muted);", ".body { fill: var(--card);", 1
    )
    problems = _svg_problems(invisible)
    assert any(".body (--card)" in problem for problem in problems), problems


def test_a_text_class_missing_from_the_ground_table_is_rejected() -> None:
    """A class nothing accounts for cannot be reported as legible."""

    renamed = _committed(_ARCHITECTURE_SVG).replace(
        '<text class="legend"', '<text class="footnote"', 1
    )
    problems = _svg_problems(renamed)
    assert any("ground table" in problem for problem in problems), problems


def test_an_exhibit_that_stopped_linking_its_source_is_rejected() -> None:
    unlinked = _committed(_README).replace("](tasks/phase-19.md)", "](tasks/)", 1)
    problems = _exhibit_problems(unlinked, _REPO_ROOT, {328})
    assert any("no longer links" in problem for problem in problems), problems


def test_a_deleted_exhibit_is_rejected() -> None:
    problems = _exhibit_problems(
        _committed(_README).replace(_EXHIBIT_OPEN, "<!-- gone:", 1), _REPO_ROOT, {328}
    )
    assert any("marker pair is gone" in problem for problem in problems), problems
