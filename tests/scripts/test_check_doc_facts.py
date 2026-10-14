"""Unit tests for scripts/check_doc_facts.py, and a pin on two README phrases.

The checker must pass on the committed results page (RESULTS.md) and fail, naming the drifted
figure, on each drift it guards. The fixture stands up a tmp tree holding only
the files the checker reads; each test perturbs one of them and asserts both
the failure and that the message names the right figure.

The lever and experiment registries are never copied: the checker reads them
from the live imports, so a perturbed .env.example is checked against what this
build ships.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import check_doc_facts
from eval.eras import BASELINE_9, STAGE_B_R3, Era
from eval.report_io import REPORT_FILENAME, read_report_text, write_report_text
from meetings.evidence_profile import EXPERIMENT_ENV_NAMES, MeetingEvidenceProfile

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "check_doc_facts.py"

# ── the README pin ───────────────────────────────────────────────────────────
#
# What the README must keep saying whatever else a rewrite changes: the two
# facts about who wrote the code and what the audits are. Its figures are
# checked on RESULTS.md, the page the checker reads, so a rewrite of the README
# in the owner's own words never touches the checker.
_README_HONESTY = (
    "without hand-writing the production code",
    "not independent human assurance",
)


def _readme_pin_problems(readme: str) -> list[str]:
    """Which of the pinned phrases ``readme`` no longer carries."""

    flat = " ".join(readme.split())
    return [f"missing {phrase!r}" for phrase in _README_HONESTY if phrase not in flat]


def test_the_readme_keeps_its_pinned_phrases() -> None:
    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert _readme_pin_problems(readme) == []


@pytest.mark.parametrize(
    ("pinned", "problem"),
    [(phrase, f"missing {phrase!r}") for phrase in _README_HONESTY],
)
def test_the_readme_pin_fails_on_each_removal(pinned: str, problem: str) -> None:
    # Planted: one pinned phrase struck from the committed README.
    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.count(pinned) == 1
    assert _readme_pin_problems(readme.replace(pinned, "")) == [problem]


# ── the checker's fixture ────────────────────────────────────────────────────

# Exactly the files the checker reads, in their relative layout so the tmp tree
# is a faithful (and perturbable) stand-in for a checkout.
_COPIED = tuple(
    dict.fromkeys(
        (
            "RESULTS.md",
            # The front page, whose findings quote figures the sources produce.
            "README.md",
            ".env.example",
            "replays/samples/4p1i/MANIFEST.md",
            "replays/samples/9p2i/MANIFEST.md",
            # The win-rate and proof rows' frozen before cells.
            "docs/results-before.json",
            # The generated pages: the scorecard's shown-set table owns the four
            # process rows, the census's vent-proof table the vent and proof rows.
            "eval/reports/process-scorecard.md",
            "eval/reports/gameplay-census.md",
            # The report the results page's real-report example quotes.
            "replays/samples/9p2i/tournament-eval-report.json.gz",
            # The instrument whose pinned assertions own the citation row.
            "tests/eval/test_vj_instruments.py",
            "docs/ml-program.md",
            "training/reports/results-finalist-eval.jsonl",
            # The import-linter config, whose contract sections the results page counts.
            ".importlinter",
        )
    )
)

# The checks also COUNT paths they never open: the committed replays behind the
# replay row and the demo count, and the candidate rounds' replays the install
# block counts with them. The fixture stands those up as empty files, and every
# relative link target too, without copying their bytes into every test.
_ENUMERATED_GLOBS = (
    ("replays/samples/4p1i", "*.jsonl"),
    ("replays/samples/9p2i", "*.jsonl"),
    ("replays/candidates", "*/*/*.jsonl"),
)

# Above this size a fixture entry is symlinked rather than copied: the committed
# eval report runs to megabytes, and every test gets its own tree. Every writer
# here REPLACES a fixture file (``_write`` unlinks first), so a link is never
# followed back into the checkout.
_LINK_ABOVE_BYTES = 1_000_000

_RESULTS = "RESULTS.md"
_FRONT_PAGE = "README.md"
_ENV_EXAMPLE = ".env.example"
_MANIFEST_4P1I = "replays/samples/4p1i/MANIFEST.md"
_MANIFEST_9P2I = "replays/samples/9p2i/MANIFEST.md"
_TOGGLE_EXAMPLE_LINE = "# AILIBI_IMPOSTOR_ROLL_CALL=0"
_EVAL_REPORT_9P2I = "replays/samples/9p2i/tournament-eval-report.json.gz"
_CITATION_INSTRUMENT = "tests/eval/test_vj_instruments.py"
_CORRECTION_INDEX = "process/audits/review-2026-09-06/README.md"
_ML_PAGE = "docs/ml-program.md"
_ML_DROPPED_ARM_ROW = (
    "| `bfd145cb…` | 28/50 = 0.56 | 13/50 = 0.26 | **0.0041** | **FAIL** |\n"
)
_ML_COMPARATOR_ROW = "| `p18-fsm-comparator` (scripted) | 13/50 = 0.26 |"
_CENSUS_PAGE = "eval/reports/gameplay-census.md"
_RESULTS_BEFORE = "docs/results-before.json"
_CENSUS_SOURCE = (
    "the samples/9p2i column of eval/reports/gameplay-census.md's vent-proof table"
)
_VENT_CLAIM = "Impostors ejected after a reported sighting of them venting (9p2i)"
# The records each sample set's era links in the samples paragraph.
_BASELINE_9_RECORD = BASELINE_9.record
_ROUND_3_RECORD = STAGE_B_R3.record


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

    Derived from the checkout and from the link parser, so the fixture cannot
    drift from what the checks look for: a link added to a checked page stands
    itself up here on the next run.
    """

    wanted: set[str] = set()
    for directory, pattern in _ENUMERATED_GLOBS:
        wanted.update(
            path.relative_to(_REPO_ROOT).as_posix()
            for path in (_REPO_ROOT / directory).glob(pattern)
        )
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
    # An eval report is committed gzipped; its text is read through the one
    # module that owns that format, exactly as the checker streams it.
    if relative.endswith(REPORT_FILENAME):
        return read_report_text(root / relative)
    return (root / relative).read_text(encoding="utf-8")


def _write(root: Path, relative: str, text: str) -> None:
    # Replace, never open in place: a large fixture entry is a symlink into the
    # checkout, and an in-place write would perturb the committed file.
    path = root / relative
    path.unlink(missing_ok=True)
    if relative.endswith(REPORT_FILENAME):
        write_report_text(path, text)  # the same deterministic archive
        return
    path.write_text(text, encoding="utf-8")


def _without_front_page(errors: list[str]) -> list[str]:
    """``errors`` minus the front page's: a perturbed source fails the README's
    figures too, and the tests of that source assert the source's own errors."""

    return [error for error in errors if not error.startswith(_FRONT_PAGE)]


def _substitute(root: Path, relative: str, old: str, new: str) -> None:
    """Rewrite ``old`` -> ``new``, asserting the perturbation actually landed."""

    text = _read(root, relative)
    assert old in text, f"{relative} no longer contains {old!r}"
    _write(root, relative, text.replace(old, new))


def _set_census_cell(root: Path, row: str, cell: str) -> None:
    """Rewrite the shown set's cell, the last column, of one census row."""

    page = _read(root, _CENSUS_PAGE)
    lines = [line for line in page.splitlines() if line.startswith(f"| {row} |")]
    assert len(lines) == 1, row
    head, _, _ = lines[0].removesuffix(" |").rpartition(" | ")
    _substitute(root, _CENSUS_PAGE, lines[0], f"{head} | {cell} |")


def test_committed_results_page_passes() -> None:
    assert check_doc_facts.check_facts(_REPO_ROOT) == []


def test_unperturbed_copy_passes(doc_tree: Path) -> None:
    # Guards the fixture itself: every later failure must come from the
    # perturbation, not from a file the copy forgot.
    assert check_doc_facts.check_facts(doc_tree) == []


# ── 1. sample provenance ─────────────────────────────────────────────────────


def test_stale_sample_date_detected(doc_tree: Path) -> None:
    # (a) The pre-19.1 README claimed the baseline-5-era refresh date. Every
    # place the README dates the 9p2i recording is held to that set's own
    # manifest, so a blanket rewrite is named once per claim rather than once
    # per file.
    _substitute(doc_tree, _RESULTS, "2026-10-09", "2026-08-19")
    # The set's record's file name carries the date too; the blanket rewrite
    # is about the claims, so the link is put back rather than broken.
    _substitute(
        doc_tree,
        _RESULTS,
        "audit-2026-08-19-stage-b-r3.md",
        "audit-2026-10-09-stage-b-r3.md",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert all(_RESULTS in error for error in errors)
    paragraph = [
        error for error in errors if "'regenerated 2026-10-09 (9p2i)'" in error
    ]
    assert len(paragraph) == 1
    dated = [
        error
        for error in errors
        if "dates the 9p2i recording '2026-08-19'" in error and "'2026-10-09'" in error
    ]
    assert len(dated) == len(errors) - 1 >= 1


def test_paragraph_date_drift_not_alibied_elsewhere(doc_tree: Path) -> None:
    # The provenance claim is bound to its paragraph: the correct date
    # appearing somewhere else in the file must not satisfy a drifted
    # paragraph (the pre-hardening checker accepted exactly this).
    _substitute(
        doc_tree,
        _RESULTS,
        "regenerated 2026-10-09 (9p2i)",
        "regenerated 2026-08-19 (9p2i)",
    )
    _write(
        doc_tree,
        _RESULTS,
        _read(doc_tree, _RESULTS)
        + "\nAn unrelated historical note mentioning 2026-10-09.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        "'regenerated 2026-10-09 (9p2i)'" in error
        and "newest refresh on 2026-10-09" in error
        for error in errors
    )
    # The same clause is a dated claim wherever it appears, so the widened
    # scan names it a second time, by line.
    assert any(
        "'regenerated 2026-08-19' dates the 9p2i recording" in error for error in errors
    )


def test_duplicate_stale_date_clause_detected(doc_tree: Path) -> None:
    # Every regenerated-date clause in the paragraph must match — a stale
    # duplicate beside the correct clause is drift, same as the win rates.
    _substitute(
        doc_tree,
        _RESULTS,
        "regenerated 2026-09-22 (4p1i)",
        "regenerated 2026-09-22 (4p1i) (an earlier draft said regenerated 2026-08-19 "
        "(4p1i))",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'regenerated 2026-08-19' dates the 4p1i recording '2026-08-19'" in errors[0]
    assert "records '2026-09-22'" in errors[0]


def test_date_claim_naming_no_set_detected(doc_tree: Path) -> None:
    # The two sets were recorded on different days, so a dated claim names the
    # set it dates; one naming neither is refused, whatever date it carries.
    _substitute(
        doc_tree, _RESULTS, "regenerated 2026-10-09 (9p2i)", "regenerated 2026-10-09"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "'regenerated 2026-10-09' names no sample set" in error for error in errors
    )
    assert any("'regenerated 2026-10-09 (9p2i)'" in error for error in errors)


def test_date_claim_naming_both_sets_detected(doc_tree: Path) -> None:
    # Planted: one date naming both sets is false for one of them.
    _write(
        doc_tree,
        _RESULTS,
        _read(doc_tree, _RESULTS)
        + "\nBoth sets are the 2026-09-22 record (4p1i, 9p2i).\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'the 2026-09-22 record' dates the 9p2i recording '2026-09-22'" in errors[0]
    assert "records '2026-10-09'" in errors[0]


def test_baseline_9_date_for_the_promoted_set_detected(doc_tree: Path) -> None:
    # Planted: the 9p2i set dated by the recording it replaced.
    _substitute(
        doc_tree,
        _RESULTS,
        "the 2026-10-09 record (9p2i) — [instrument]",
        "the 2026-09-22 record (9p2i) — [instrument]",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "dates the 9p2i recording '2026-09-22'" in errors[0]


def test_unnumbered_record_date_detected(doc_tree: Path) -> None:
    # An unnumbered "reference recording" claim is about a current recording,
    # so it is held to the manifest of the set it names.
    _write(
        doc_tree,
        _RESULTS,
        _read(doc_tree, _RESULTS)
        + "\nThe 4-player set is the reference recording, made 2026-07-20 (4p1i).\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert (
        "'reference recording, made 2026-07-20' dates the 4p1i recording" in errors[0]
    )
    assert "'2026-09-22'" in errors[0]


def test_older_recording_date_is_left_alone(doc_tree: Path) -> None:
    # A numbered claim names an older recording: the README may say when the
    # recording it replaced was made without being held to today's manifests.
    _write(
        doc_tree,
        _RESULTS,
        _read(doc_tree, _RESULTS)
        + "\nThe first sets were reference recording 6, 2026-07-20.\n",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_wrong_total_sample_count_detected(doc_tree: Path) -> None:
    # The paragraph's total-replay count is a manifest fact too: the expected
    # claim is missing AND the drifted one contradicts the row totals.
    _substitute(doc_tree, _RESULTS, "100 sample replays", "80 sample replays")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'100 sample replays'" in errors[0]
    assert "'80 sample replays'" in errors[1]


def test_wrong_tournament_size_detected(doc_tree: Path) -> None:
    # As is the per-set tournament size — both facets reported.
    _substitute(doc_tree, _RESULTS, "50-game", "40-game")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'50-game'" in errors[0]
    assert "'40-game'" in errors[1]


def test_stale_count_beside_correct_detected(doc_tree: Path) -> None:
    # A contradictory count clause beside the correct substring is drift —
    # every count-shaped claim in the paragraph is held to the row totals.
    _substitute(
        doc_tree,
        _RESULTS,
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
        _RESULTS,
        "played by the `Qwen/Qwen3.6-27B` model",
        "played by the `Qwen/Qwen3-32B` model",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'Qwen/Qwen3.6-27B'" in errors[0]
    assert "`model` column" in errors[0]


def test_wrong_prompt_set_version_detected(doc_tree: Path) -> None:
    # The paragraph leaves the prompt stamps to the manifests it links, so a
    # version it does name is a claim the prompt_versions column must record.
    _substitute(
        doc_tree,
        _RESULTS,
        "played by the `Qwen/Qwen3.6-27B` model",
        "played by the `Qwen/Qwen3.6-27B` model on `v2` prompts",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'v2'" in errors[0]
    assert "`prompt_versions` column" in errors[0]


@pytest.mark.parametrize(
    ("stamp", "kind"),
    [
        ("v5", "prompt-set version"),
        ("`v5`", "prompt-set version"),
        ("`route_lines_v2`", "prompt arm"),
        ("route_lines_v2", "prompt arm"),
    ],
)
def test_samples_paragraph_naming_an_unrecorded_stamp_detected(
    doc_tree: Path, stamp: str, kind: str
) -> None:
    # Planted: a stamp the manifests do not record, backticked or bare.
    _substitute(
        doc_tree,
        _RESULTS,
        "played by the `Qwen/Qwen3.6-27B` model",
        f"played by the `Qwen/Qwen3.6-27B` model with {stamp}",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    token = stamp.strip("`")
    assert f"names the {kind} {token!r}" in errors[0]
    assert "no row's `prompt_versions` column records" in errors[0]


def test_samples_paragraph_naming_recorded_stamps_passes(doc_tree: Path) -> None:
    # The converse: a stamp the manifests do record may be named.
    _substitute(
        doc_tree,
        _RESULTS,
        "played by the `Qwen/Qwen3.6-27B` model",
        "played by the `Qwen/Qwen3.6-27B` model on `v6` prompts and `route_lines_v1`",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_stamp_like_token_outside_the_samples_paragraph_is_not_read(
    doc_tree: Path,
) -> None:
    # The stamp rule reads the samples paragraph only: a version-like word in
    # another paragraph is not a claim about the recorded prompts.
    _substitute(
        doc_tree,
        _RESULTS,
        "\n## Checks you can run",
        "\nThe viewer reads replay format v5.\n\n## Checks you can run",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


@pytest.mark.parametrize("name", ["4p1i", "9p2i"])
def test_samples_paragraph_without_a_manifest_link_detected(
    doc_tree: Path, name: str
) -> None:
    # Planted: one set's MANIFEST link removed, its text kept. The stamps are
    # the manifest's to state, so the paragraph links each set's manifest.
    manifest = f"replays/samples/{name}/MANIFEST.md"
    links = (
        "game by game ([4p1i](replays/samples/4p1i/MANIFEST.md), "
        "[9p2i](replays/samples/9p2i/MANIFEST.md))"
    )
    _substitute(doc_tree, _RESULTS, links, links.replace(f"[{name}]({manifest})", name))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert f"does not link {manifest}" in errors[0]


def test_missing_provenance_paragraph_fails_loud(doc_tree: Path) -> None:
    # Losing the paragraph anchor is format drift, not a vacuous pass.
    for name, day in (("4p1i", "2026-09-22"), ("9p2i", "2026-10-09")):
        _substitute(
            doc_tree,
            _RESULTS,
            f"regenerated {day} ({name})",
            f"refreshed {day} ({name})",
        )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "exactly one sample-provenance paragraph" in errors[0]


def test_repeated_claims_survive_a_lost_provenance_paragraph(doc_tree: Path) -> None:
    # ...and it must not take the claim scan down with it: a rate the README
    # states elsewhere is still held to its manifest.
    for name, day in (("4p1i", "2026-09-22"), ("9p2i", "2026-10-09")):
        _substitute(
            doc_tree,
            _RESULTS,
            f"regenerated {day} ({name})",
            f"refreshed {day} ({name})",
        )
    _substitute(
        doc_tree,
        _RESULTS,
        "| 36% (4p1i), 34% (9p2i) |",
        "| 36% (4p1i), 30% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("exactly one sample-provenance paragraph" in error for error in errors)
    assert any("claim '30% (9p2i)' disagrees" in error for error in errors)


def test_wrong_win_rate_detected(doc_tree: Path) -> None:
    # (b) A win rate that no longer matches the manifest it is drawn from:
    # the paragraph misses the expected substring AND carries a claim that
    # contradicts the manifest — both are reported.
    _substitute(doc_tree, _RESULTS, "rate 36% (4p1i)", "rate 30% (4p1i)")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any("'36% (4p1i)'" in error and "18/50" in error for error in errors)
    assert any("claim '30% (4p1i)' disagrees" in error for error in errors)


def test_promoted_rate_held_to_its_own_manifest(doc_tree: Path) -> None:
    # Planted: the 9p2i set's round-2 rate left in a live claim (was its
    # baseline-9 rate, 22%, before round 3's promotion).
    _substitute(doc_tree, _RESULTS, "rate 34% (9p2i)", "rate 48% (9p2i)")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any("'34% (9p2i)'" in error and "17/50" in error for error in errors)
    assert any(
        "claim '48% (9p2i)' disagrees" in error and "17/50 = 34%" in error
        for error in errors
    )


def test_stray_win_rate_claim_detected(doc_tree: Path) -> None:
    # A wrong rate claim OUTSIDE the provenance paragraph is drift too — the
    # paragraph being right must not license a false claim elsewhere.
    _write(
        doc_tree,
        _RESULTS,
        _read(doc_tree, _RESULTS)
        + "\nHistorically the impostors held 36% (9p2i) of the games.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "win-rate claim '36% (9p2i)'" in errors[0]
    assert "17/50 = 34%" in errors[0]


def test_in_paragraph_stale_claim_detected(doc_tree: Path) -> None:
    # The correct substring being present must not exempt the paragraph's
    # OTHER claims: a stale duplicate beside the correct value is drift.
    _substitute(
        doc_tree,
        _RESULTS,
        "rate 34% (9p2i)",
        "rate 34% (9p2i) (an earlier draft misquoted 25% (9p2i))",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "win-rate claim '25% (9p2i)' disagrees" in errors[0]
    assert "17/50 = 34%" in errors[0]


def test_manifest_outcome_flip_detected(doc_tree: Path) -> None:
    # The bytes move under the prose: one recorded winner cell flips, so the
    # re-derived rate slides 36% -> 34%. The README misses the new rate, and
    # both places that state the old one as current are named; the Before cell
    # beside it is history and still holds.
    text = _read(doc_tree, _MANIFEST_4P1I)
    assert "| IMPOSTORS |" in text
    _write(doc_tree, _MANIFEST_4P1I, text.replace("| IMPOSTORS |", "| CREWMATES |", 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("'34% (4p1i)'" in error and "17/50" in error for error in errors)
    stale = [error for error in errors if "claim '36% (4p1i)' disagrees" in error]
    assert len(stale) == 2
    assert len(errors) == 3


def test_unparseable_manifest_fails_loud(doc_tree: Path) -> None:
    # Format drift must not read as "no impostor wins recorded": a manifest
    # with no parseable rows is a hard failure, not a vacuous pass.
    _write(doc_tree, _MANIFEST_9P2I, "# Sample Replay Manifest\n\nno table here.\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "parsed zero table rows" in errors[0]
    assert _MANIFEST_9P2I in errors[0]


# The README as it stood at d1220ead, frozen: the base the historical front
# doors below are rebuilt from, so rewording the live page leaves them intact.
_FROZEN_README = Path(__file__).parent / "_goldens" / "README-d1220ead.md"

# The README as it stood at 2eed2e92, the last commit before round 3's
# promotion, kept as the hunks that differ from the frozen d1220ead page: each
# pair is (the d1220ead text, the 2eed2e92 text). Applied in order, they rebuild
# the whole round-2 front door inside the promoted tree.
_ROUND_2_README_HUNKS: tuple[tuple[str, str], ...] = (
    (
        """# AiLibi — can agents reason from what they actually saw?

*Recorded AI social deduction*
""",
        """# AiLibi — can agents reason from what they actually saw?
""",
    ),
    (
        (
            "**[Watch the recorded demo](https://dkdan10.github.io/AiLibi/)** · [See the "
            "results](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament) · [Read "
            "the five-minute guide](docs/reading-guide.md)\n"
        ),
        """**[Watch the recorded demo](https://dkdan10.github.io/AiLibi/)** · [Inspect results and decisions](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament) · [Read an ownership decision](docs/ownership-case-study.md)
""",
    ),
    (
        (
            "Daniel Keinan directed the project and decided what was accepted, without "
            "hand-writing the production code; AI agents wrote it, and the audits here are "
            "AI reviews, not independent human assurance. Each change arrived on its own "
            "branch with a written task, a pull request and the full gate.\n"
        ),
        """Daniel directed product scope, acceptance criteria, priorities, and adoption decisions. Claude Code implemented the initial project; Codex reviewed it and now also implements cleanup. Agents wrote production code and substantial supporting plans, cards, tests, documentation, and audits. Daniel did not hand-write the production code. “Independent” audits here mean separate AI reviewers, not independent human assurance.
""",
    ),
    (
        """*At tick 9 two players lie dead, one impostor stands in MedBay and the other is inside a vent, while p-5 can see only p-4, whom p-5 accuses at the meeting that follows. This is 9p2i seed 19, the game the demo's guided tour opens on, from the 2026-10-09 record (9p2i); [media provenance](docs/media/README.md#provenance) records its source and asset identities.*

[![The same game playing from its first tick to the meeting](docs/media/spectator-journey.gif)](https://dkdan10.github.io/AiLibi/)
""",
        """*9p2i seed 19, the game the demo's guided tour opens on, from the 2026-10-01 record (9p2i): at tick 9 two players lie dead, one impostor stands in MedBay and the other is inside a vent, while p-5 can see only p-4, whom p-5 accuses at the meeting that follows. [Media provenance](docs/media/README.md#provenance) records the source and asset identities; the [short clip](docs/media/spectator-journey.webm) walks the same game.*
""",
    ),
    (
        (
            "The shown 9-player set was recorded 2026-10-09 under the adopted gameplay "
            "changes; the 4-player set and the ML training games were recorded 2026-09-22. "
            "Three things hold there, each with its command in the [reading "
            "guide](docs/reading-guide.md):\n"
        ),
        """The shown 9-player set was recorded 2026-10-01 under the adopted gameplay changes, in [its own era](docs/glossary.md#era-recordings-that-share-one-recorded-identity); the 4-player set and the ML corpus stay at [baseline 9](docs/glossary.md#baseline-n-the-reference-recording), recorded 2026-09-22. No figure pools the two. Each before cell is what that set's replaced recording read.
""",
    ),
    (
        """| Sample games that replay byte for byte | 100 of 100 (100%) | 100 of 100 (100%) | every commit — `scripts/verify_samples.sh` |
""",
        """| Committed sample replays that reconstruct byte-identically | 100 of 100 | 100 of 100 | every commit — `scripts/verify_samples.sh` |
""",
    ),
    (
        """| Eject ballots citing what the voter saw or heard about the accused (9p2i) | 394 of 397 (99%) | 407 of 410 (99%) | [process scorecard](docs/process-scorecard.md); a floor: the ballot asks every eject to cite |
| Crew eject ballots naming someone other than the voter's [top suspect](docs/glossary.md#top-suspect-the-player-a-voters-own-suspicion-rates-highest) (9p2i) | 56 of 291 (19%) | 65 of 292 (22%) | [process scorecard](docs/process-scorecard.md) |
| Ballots with no stated reason (9p2i) | 6 of 702 (1%) | 11 of 691 (2%) | [process scorecard](docs/process-scorecard.md) |
| Ballots whose target is the one their voter wrote (9p2i) | 692 of 702 (99%); 10 impostor votes against a partner turned into skips | 674 of 691 (98%) | [process scorecard](docs/process-scorecard.md) |
| Eject ballots with a valid citation of a statement or sighting (9p2i) | 397 of 397 (100%), zero dangling | 410 of 410 (100%), zero dangling | the 2026-10-09 record (9p2i) — [instrument](tests/eval/test_vj_instruments.py) |
| Impostor win rate, sample games | 36% (4p1i), 34% (9p2i) | 36% (4p1i), 48% (9p2i) | the 2026-09-22 record (4p1i), the 2026-10-09 record (9p2i) — [4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md) |
| Impostors among those ejected, with and without proof of their role (9p2i) | 24 of 24 (100%) vs 22 of 37 (59%) | 24 of 24 (100%) vs 20 of 42 (48%) | the 2026-10-09 record (9p2i) — [the record](audits/audit-2026-10-09-stage-b-r3.md) §12.5, against [round 2's](audits/audit-2026-10-01-stage-b-r2.md) §9.6; 15 of 15 innocent ejections sit in the no-proof cell |
| Impostors ejected after a reported sighting of them venting (9p2i) | 24 of 46 (52%) | 24 of 44 (55%) | the 2026-10-09 record (9p2i) — the cross-tab in the [reading guide](docs/reading-guide.md). Reading: general social deduction, **not** demonstrated |
""",
        """| Impostor win rate, committed samples | 36% (4p1i), 48% (9p2i) | 36% (4p1i), 22% (9p2i) | the 2026-09-22 record (4p1i), the 2026-10-01 record (9p2i) — [4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md) |
| Eject ballots carrying a valid citation, a turn or an observation id (9p2i) | 410 / 410, zero dangling | 496 / 496, zero dangling | the 2026-10-01 record (9p2i) — [instrument](tests/eval/test_vj_instruments.py) |
| Ejection accuracy with engine-certified proof of the ejectee's role, against without (9p2i) | 24 / 24 = 1.0000 vs 20 / 42 = 0.4762 | 70 / 70 = 1.0000 vs 11 / 20 = 0.5500 | the 2026-10-01 record (9p2i) — [the record](audits/audit-2026-10-01-stage-b-r2.md) §9.6, against [baseline 9's](audits/audit-2026-09-22-process-rerecord.md) §6.2; 22 of 22 innocent ejections sit in the no-proof cell |
| Correct 9p ejections riding an ejectee-specific vent sighting | 24 / 44 = 55% | 70 / 81 = 86% | the 2026-10-01 record (9p2i) — the cross-tab in the [reading guide](docs/reading-guide.md). Reading: general social deduction, **not** demonstrated |
""",
    ),
    (
        ("*Valid* means resolvable, not supported. "),
        """*Valid* means resolvable, not supported. No citation check establishes that the source bears out its accusation. In the shown 9-player set, 24 of 44 correct ejections follow certified vent evidence; without it, 20 of 42 ejections target impostors and 22 convict crewmates. This demonstrates processing of certified facts and deception, **not general social deduction**. The [reading guide](docs/reading-guide.md) reads these 50 games alone.
""",
    ),
    (
        """**Targets written down before measuring were missed twice:** the owner adopted the first recording anyway, in writing, and nothing from the second ([what each measured](docs/history.md#evidence-honesty-phase-20)).
""",
        """**Two bars were written down first, and both were missed.** Baseline 7 measured conviction accuracy without proof at 61 of 103 = 0.5922 against 0.60, and wrongful ejections at 42 against fewer than 35. Its rule returned **FINDING**, but Daniel adopted that recording by explicit owner override on 2026-08-26; the bars did not pass. Baseline 8 registered no bars and measured 50 of 96 = 0.5208 and 46 innocent ejections. Baseline 9 registered none either and measured 43 of 85 = 0.5059 and 42 innocent ejections over its four recorded sets, a movement too small for these samples to call real. [The decision and its limitations](docs/ownership-case-study.md) preserve both judgments.

**An experiment on baseline 8 met three of four fresh bars.** Innocent ejections fell from 46 to 20; 11 of those 20 were the meeting's own reporter, against 34 of 46. That share, 0.5500, missed 0.40, so the rule returns **a finding**, with no override and no adoption ([record](audits/audit-phase-21-adopting-record.md)).
""",
    ),
    (
        (
            "Four learned impostor policies won more games than the scripted one and none "
            "became the default; each failed a gate written before measuring: [methods, "
            "negative results and limits](docs/ml-program.md).\n"
        ),
        """**Four learned impostor policies beat their scripted comparator on wins; none became the default.** Each failed a pre-registered evidence-quality gate. The retained candidate's advantage is not statistically significant at 50 games; the old comparator also had two since-repaired defects, and those learned comparisons were not re-run. [ML methods, negative results, and limits](docs/ml-program.md).
""",
    ),
    (
        (
            "- **An observation boundary.** Agents never touch engine state. They receive "
            "sanitized packets and a public map; import rules and planted-leak tests "
            "enforce the line; only the viewer sees everything.\n"
        ),
        """- **Observation firewall:** agents receive sanitized packets and a public map. Import-linter, planted import leaks, and recursive packet sweeps defend this boundary. The spectator is deliberately privileged.
""",
    ),
    (
        (
            "**One known leak.** In the 2026-09-22 recordings the opening prompts name "
            "each body by a label that reveals when it died; the shown 9-player set's "
            "report openings no longer carry it (0 of 115). The full repair stays switched "
            "off, not adopted. [Observation contract and "
            "limitations](docs/observation-contract.md).\n"
        ),
        """**Known evidence leak:** in the baseline-9 recordings, default opening prompts
reveal a hidden death tick through a body identifier. The shown 9-player set's
report openings no longer carry it (0 of 114). The full temporal repair stays
default-off, not adopted. [Observation contract and limitations](docs/observation-contract.md).
""",
    ),
    (
        (
            "[How a change gets in](docs/workflow.md) · [Lessons](docs/lessons.md) · [One "
            "decision, traced](docs/ownership-case-study.md) · [History](docs/history.md)\n"
        ),
        """The [ownership case study](docs/ownership-case-study.md) traces one consequential decision through evidence, alternatives, implementation, review, and what remained unproven. [Lessons](docs/lessons.md) and the [rolling workflow](docs/workflow.md) explain how findings become bounded changes. The cleanup branch merged into main on 2026-09-07; historical phase closes are not a claim that every current issue is resolved. [History](docs/history.md) · [Current work](tasks/README.md).
""",
    ),
    (
        (
            "You need [uv](https://docs.astral.sh/uv/getting-started/installation/), "
            "Python 3.11 (`uv python install 3.11`) and Node.js 22 or newer; the locked "
            "install takes a few minutes:\n"
        ),
        """(22.x works from 22.13). Installation downloads locked dependencies; allow
""",
    ),
    (
        ("Nothing below needs a provider account or network access.\n"),
        """Stop serving with Ctrl-C. Fake runs test mechanics; samples preserve hosted
dialogue. Each replay has an audit sidecar; `--force` replaces both together.
""",
    ),
    (
        ("Two of three reproducibility claims are proven: "),
        """### Three reproducibility scopes

Three distinct claims:

""",
    ),
    (
        (
            "Bit-identical learned-optimizer output across machines is seen on "
            "Linux/x86-64 only.\n"
        ),
        """3. **Cross-platform optimizer portability** — independent hosts producing bit-identical learned-optimizer bytes. **Designed for, not yet confirmed.** The sampler uses only operations IEEE-754 requires to be correctly rounded, but has been observed on Linux/x86-64 alone; no caller should rely on it until a run on the recorded failure host reproduces the pinned digest.
""",
    ),
    (
        (
            "The spectator's API is an unauthenticated game-master view and stays "
            "loopback-only. Real generation needs a selected provider plus token, cost and "
            "wall-time limits: [provider setup](llm/README.md), "
            "[.env.example](.env.example), [recording procedure](docs/deployment.md).\n"
        ),
        """The default fake provider tests mechanics offline. Real generation needs an explicitly selected provider and token, cost, and wall-time limits, even with flat-rate service. Follow [provider setup](llm/README.md), [.env.example](.env.example), and [bounded tournament/resume instructions](docs/deployment.md); keep new outputs in a separate directory. Fresh model dialogue is not reproduced by a seed alone.
""",
    ),
    (
        (
            "**The fake provider's report is empty on purpose.** A real report, gzipped at "
            "[replays/samples/9p2i/tournament-eval-report.json.gz](replays/samples/9p2i/tournament-eval-report.json.gz), "
            "records 61 ejections; 46 removed an impostor, 36 of those 46 with evidence "
            "against that player on the meeting's record.\n"
        ),
        """**The fake provider's report is empty on purpose.** It normally skips and does not measure model reasoning. A real report, gzipped at [replays/samples/9p2i/tournament-eval-report.json.gz](replays/samples/9p2i/tournament-eval-report.json.gz), records 66 ejections, vote correctness 0.795, and ejection accuracy 0.667. The demo publishes a smaller, strictly validated summary; reported usage is separate from verified outcomes and is not a billing guarantee.
""",
    ),
    (
        (
            "A clone includes 100 sample replays under `replays/samples/`: two 50-game "
            "tournaments played by the `Qwen/Qwen3.6-27B` model. The 4-player set was "
            "regenerated 2026-09-22 (4p1i) with every experimental switch off ([its "
            "record](audits/audit-2026-09-22-process-rerecord.md)): impostor win rate 36% "
            "(4p1i). The 9-player set was regenerated 2026-10-09 (9p2i) under the adopted "
            "gameplay changes plus the [route "
            "lines](docs/glossary.md#route-line-what-the-doors-say-about-a-players-stated-places), "
            "a recorded setting ([its record](audits/audit-2026-10-09-stage-b-r3.md)): "
            "impostor win rate 34% (9p2i). Each set's manifest lists its prompt versions "
            "game by game ([4p1i](replays/samples/4p1i/MANIFEST.md), "
            "[9p2i](replays/samples/9p2i/MANIFEST.md)). The picture above is from the "
            "9-player game the guided tour opens on.\n"
        ),
        """**The samples.** A clone includes 100 sample replays under `replays/samples/`: two 50-game tournaments using `Qwen/Qwen3.6-27B` and `qwen3_6_27b` `v6` prompts with a `v8` ballot, each in its own era. The 4-player set was regenerated 2026-09-22 (4p1i) at [baseline 9](audits/audit-2026-09-22-process-rerecord.md), every experimental switch off: impostor win rate 36% (4p1i). The 9-player set was regenerated 2026-10-01 (9p2i) under the adopted gameplay changes ([its record](audits/audit-2026-10-01-stage-b-r2.md)), its ballot stamped `impostor_ballot_v1` and `ballot_kill_row_v1`: impostor win rate 48% (9p2i). Each manifest records per-game provenance. The picture above is from the 9-player game the guided tour opens on.
""",
    ),
)


# The README as it stood at d41c9006, the last commit before round 2's
# promotion, kept as the hunks that differ from the round-2 page: each pair is
# (the 2eed2e92 text, the d41c9006 text). Applied after the round-2 hunks, they
# rebuild the whole d41c9006 front door inside the promoted tree.
_D41C9006_README_HUNKS: tuple[tuple[str, str], ...] = (
    (
        """**[Watch the recorded demo](https://dkdan10.github.io/AiLibi/)** · [Inspect results and decisions](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament) · [Read an ownership decision](docs/ownership-case-study.md)
""",
        """**[Watch the recorded demo](https://dkdan10.github.io/AiLibi/)** · [Inspect results and three decisions](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament) · [Read an ownership decision](docs/ownership-case-study.md)
""",
    ),
    (
        """The shown 9-player set was recorded 2026-10-01 under the adopted gameplay changes, in [its own era](docs/glossary.md#era-recordings-that-share-one-recorded-identity); the 4-player set and the ML corpus stay at [baseline 9](docs/glossary.md#baseline-n-the-reference-recording), recorded 2026-09-22. No figure pools the two. Each before cell is what that set's replaced recording read.
""",
        """The current reference recording was completed 2026-09-22. Figures compare it with the previous reference.
""",
    ),
    (
        """| What | Figure | Before | Recorded on, and where it lives |
""",
        """| What | Figure | [At baseline 8](docs/glossary.md#baseline-n-the-reference-recording) | Recorded on, and where it lives |
""",
    ),
    (
        """| Impostor win rate, committed samples | 36% (4p1i), 48% (9p2i) | 36% (4p1i), 22% (9p2i) | the 2026-09-22 record (4p1i), the 2026-10-01 record (9p2i) — [4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md) |
| Eject ballots carrying a valid citation, a turn or an observation id (9p2i) | 410 / 410, zero dangling | 496 / 496, zero dangling | the 2026-10-01 record (9p2i) — [instrument](tests/eval/test_vj_instruments.py) |
| Ejection accuracy with engine-certified proof of the ejectee's role, against without (9p2i) | 24 / 24 = 1.0000 vs 20 / 42 = 0.4762 | 70 / 70 = 1.0000 vs 11 / 20 = 0.5500 | the 2026-10-01 record (9p2i) — [the record](audits/audit-2026-10-01-stage-b-r2.md) §9.6, against [baseline 9's](audits/audit-2026-09-22-process-rerecord.md) §6.2; 22 of 22 innocent ejections sit in the no-proof cell |
| Correct 9p ejections riding an ejectee-specific vent sighting | 24 / 44 = 55% | 70 / 81 = 86% | the 2026-10-01 record (9p2i) — the cross-tab in the [reading guide](docs/reading-guide.md). Reading: general social deduction, **not** demonstrated |
""",
        """| Impostor win rate, committed samples | 36% (4p1i), 22% (9p2i) | 36% (4p1i), 30% (9p2i) | the 2026-09-22 record — [4p1i](replays/samples/4p1i/MANIFEST.md), [9p2i](replays/samples/9p2i/MANIFEST.md) |
| Eject ballots carrying a valid citation, a turn or an observation id (9p2i) | 496 / 496, zero dangling | 526 / 527, zero dangling | reference recording 9, 2026-09-22 — [instrument](tests/eval/test_vj_instruments.py) |
| Ejection accuracy with engine-certified proof of the ejectee's role, against without | 326 / 326 = 1.0000 vs 43 / 85 = 0.5059 | 333 / 333 = 1.0000 vs 50 / 96 = 0.5208 | the 2026-09-22 record, pooled over four recorded sets — [the record](audits/audit-2026-09-22-process-rerecord.md) §6.2, against [the one before it](audits/audit-phase-21-rerecord.md) §5.1; 42 of 42 innocent ejections sit in the no-proof cell |
| Correct 9p ejections riding an ejectee-specific vent sighting | 70 / 81 = 86% | 68 / 82 = 83% | reference recording 9, 2026-09-22 — the cross-tab in the [reading guide](docs/reading-guide.md). Reading: general social deduction, **not** demonstrated |
""",
    ),
    (
        """*Valid* means resolvable, not supported. No citation check establishes that the source bears out its accusation. In the shown 9-player set, 24 of 44 correct ejections follow certified vent evidence; without it, 20 of 42 ejections target impostors and 22 convict crewmates. This demonstrates processing of certified facts and deception, **not general social deduction**. The [reading guide](docs/reading-guide.md) reads these 50 games alone.
""",
        """*Valid* means resolvable, not supported. No citation check establishes that the source bears out its accusation. In the canonical 9-player set, 70 of 81 correct ejections follow certified vent evidence; without it, 11 of 20 ejections target impostors and 9 convict crewmates. This demonstrates processing of certified facts and deception, **not general social deduction**. The [reading guide](docs/reading-guide.md) separates these 50 games from the four-set pooled figures above.
""",
    ),
    (
        """**Two bars were written down first, and both were missed.** Baseline 7 measured conviction accuracy without proof at 61 of 103 = 0.5922 against 0.60, and wrongful ejections at 42 against fewer than 35. Its rule returned **FINDING**, but Daniel adopted that recording by explicit owner override on 2026-08-26; the bars did not pass. Baseline 8 registered no bars and measured 50 of 96 = 0.5208 and 46 innocent ejections. Baseline 9 registered none either and measured 43 of 85 = 0.5059 and 42 innocent ejections over its four recorded sets, a movement too small for these samples to call real. [The decision and its limitations](docs/ownership-case-study.md) preserve both judgments.
""",
        """**Two bars were written down first, and both were missed.** Baseline 7 measured conviction accuracy without proof at 61 of 103 = 0.5922 against 0.60, and wrongful ejections at 42 against fewer than 35. Its rule returned **FINDING**, but Daniel adopted that recording by explicit owner override on 2026-08-26; the bars did not pass. Baseline 8 registered no bars and measured 50 of 96 = 0.5208 and 46 innocent ejections. The current recording, baseline 9, registered none either and measures 43 of 85 = 0.5059 and 42 innocent ejections, a movement too small for these samples to call real. [The decision and its limitations](docs/ownership-case-study.md) preserve both judgments.
""",
    ),
    (
        """**Known evidence leak:** in the baseline-9 recordings, default opening prompts
reveal a hidden death tick through a body identifier. The shown 9-player set's
report openings no longer carry it (0 of 114). The full temporal repair stays
default-off, not adopted. [Observation contract and limitations](docs/observation-contract.md).
""",
        """**Known evidence leak:** default opening prompts reveal a hidden death tick
through a body identifier. The repair is implemented in the default-off temporal
experiment; it is not adopted. [Observation contract and limitations](docs/observation-contract.md).
""",
    ),
    (
        """**The fake provider's report is empty on purpose.** It normally skips and does not measure model reasoning. A real report, gzipped at [replays/samples/9p2i/tournament-eval-report.json.gz](replays/samples/9p2i/tournament-eval-report.json.gz), records 66 ejections, vote correctness 0.795, and ejection accuracy 0.667. The demo publishes a smaller, strictly validated summary; reported usage is separate from verified outcomes and is not a billing guarantee.
""",
        """**The fake provider's report is empty on purpose.** It normally skips and does not measure model reasoning. A real report, gzipped at [replays/samples/9p2i/tournament-eval-report.json.gz](replays/samples/9p2i/tournament-eval-report.json.gz), records 90 ejections, vote correctness 0.938, and ejection accuracy 0.900. The demo publishes a smaller, strictly validated summary; reported usage is separate from verified outcomes and is not a billing guarantee.
""",
    ),
    (
        """**The samples.** A clone includes 100 sample replays under `replays/samples/`: two 50-game tournaments using `Qwen/Qwen3.6-27B` and `qwen3_6_27b` `v6` prompts with a `v8` ballot, each in its own era. The 4-player set was regenerated 2026-09-22 (4p1i) at [baseline 9](audits/audit-2026-09-22-process-rerecord.md), every experimental switch off: impostor win rate 36% (4p1i). The 9-player set was regenerated 2026-10-01 (9p2i) under the adopted gameplay changes ([its record](audits/audit-2026-10-01-stage-b-r2.md)), its ballot stamped `impostor_ballot_v1` and `ballot_kill_row_v1`: impostor win rate 48% (9p2i). Each manifest records per-game provenance. The picture above is from the 9-player game the guided tour opens on.
""",
        """**The samples.** A clone includes 100 sample replays under `replays/samples/`: two 50-game tournaments, regenerated 2026-09-22 using `Qwen/Qwen3.6-27B`, `qwen3_6_27b` `v6` prompts with a `v8` ballot, with impostor win rates 36% (4p1i) and 22% (9p2i). Each manifest records per-game provenance. Existing historical imagery is labelled separately.
""",
    ),
)


def _readme_rebuilt(doc_tree: Path, *steps: tuple[tuple[str, str], ...]) -> list[str]:
    readme = _FROZEN_README.read_text(encoding="utf-8")
    for hunks in steps:
        for current, previous in hunks:
            assert readme.count(current) == 1, current[:60]
            readme = readme.replace(current, previous)
    _write(doc_tree, _RESULTS, readme)
    errors = check_doc_facts.check_facts(doc_tree)
    return [error for error in errors if error.startswith(_RESULTS)]


def test_the_round_2_results_text_fails_on_the_promoted_tree(doc_tree: Path) -> None:
    # Planted: the whole README as it stood before round 3's promotion, dropped
    # into the promoted tree. It fails naming at least the 9p2i set's date, its
    # win rate and the era sentence, each from the set's own manifest and record.
    readme_errors = _readme_rebuilt(doc_tree, _ROUND_2_README_HUNKS)
    assert any("'regenerated 2026-10-09 (9p2i)'" in error for error in readme_errors)
    assert any(
        "'34% (9p2i)'" in error and "17/50 games" in error for error in readme_errors
    )
    assert any(
        "claim '48% (9p2i)' disagrees" in error and "17/50 = 34%" in error
        for error in readme_errors
    )
    assert any(
        "does not link the 9p2i set's era, stage-b-r3" in error
        for error in readme_errors
    )


def test_the_d41c9006_results_text_fails_on_the_promoted_tree(doc_tree: Path) -> None:
    # Planted: the whole README as it stood before round 2's promotion, dropped
    # into the promoted tree; it fails on the same three facts (it failed on the
    # round-2 tree too, against 24/50 and stage-b-r2).
    readme_errors = _readme_rebuilt(
        doc_tree, _ROUND_2_README_HUNKS, _D41C9006_README_HUNKS
    )
    assert any("'regenerated 2026-10-09 (9p2i)'" in error for error in readme_errors)
    assert any(
        "'34% (9p2i)'" in error and "17/50 games" in error for error in readme_errors
    )
    assert any(
        "claim '22% (9p2i)' disagrees" in error and "17/50 = 34%" in error
        for error in readme_errors
    )
    assert any(
        "does not link the 9p2i set's era, stage-b-r3" in error
        for error in readme_errors
    )


def test_samples_paragraph_dropping_only_the_promoted_sets_record_detected(
    doc_tree: Path,
) -> None:
    # Planted: the samples paragraph keeps baseline 9's record link and drops
    # only the promoted set's. Each set is linked to its own era's record, so
    # the ladder tip's link never stands in for the 9p2i set's.
    _substitute(doc_tree, _RESULTS, f" ([its record]({_ROUND_3_RECORD}))", "")
    paragraph = check_doc_facts.provenance_paragraph(_read(doc_tree, _RESULTS))
    assert paragraph is not None
    assert f"]({_BASELINE_9_RECORD})" in paragraph
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "does not link the 9p2i set's era, stage-b-r3" in errors[0]
    assert f"({_ROUND_3_RECORD})" in errors[0]


def test_samples_paragraph_dropping_only_the_tips_record_detected(
    doc_tree: Path,
) -> None:
    # Planted, the mirror case: the promoted set's record link kept, baseline
    # 9's dropped. Only the 4p1i set, the one baseline-9 set the paragraph
    # names, is reported; the 9p2i set's own link still holds.
    _substitute(doc_tree, _RESULTS, f" ([its record]({_BASELINE_9_RECORD}))", "")
    paragraph = check_doc_facts.provenance_paragraph(_read(doc_tree, _RESULTS))
    assert paragraph is not None
    assert f"]({_ROUND_3_RECORD})" in paragraph
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "does not link the 4p1i set's era, baseline-9" in errors[0]
    assert f"({_BASELINE_9_RECORD})" in errors[0]


# ── the frozen before cells ──────────────────────────────────────────────────


def test_before_column_win_rate_held_to_the_frozen_cells(doc_tree: Path) -> None:
    # A history cell is checked, not skipped: a made-up before value fails.
    _substitute(
        doc_tree,
        _RESULTS,
        "| 36% (4p1i), 34% (9p2i) | 36% (4p1i), 48% (9p2i) |",
        "| 36% (4p1i), 34% (9p2i) | 12% (4p1i), 48% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert (
        "win-rate claim '12% (4p1i)' in the before column disagrees with "
        f"{_RESULTS_BEFORE} (18/50 = 36%)" in errors[0]
    )


def test_before_column_held_to_each_sets_own_cells(doc_tree: Path) -> None:
    # Planted: the 9p2i before cell left at the rate of the recording before
    # the one it replaced.
    _substitute(
        doc_tree,
        _RESULTS,
        "| 36% (4p1i), 34% (9p2i) | 36% (4p1i), 48% (9p2i) |",
        "| 36% (4p1i), 34% (9p2i) | 36% (4p1i), 22% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "claim '22% (9p2i)' in the before column" in errors[0]
    assert "(24/50 = 48%)" in errors[0]


def test_proof_before_cell_held_to_the_frozen_cells(doc_tree: Path) -> None:
    _substitute(
        doc_tree,
        _RESULTS,
        "| 24 of 24 (100%) vs 20 of 42 (48%) |",
        "| 24 of 24 (100%) vs 21 of 42 (50%) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert errors == [
        f"{_RESULTS}: the 'Before' cell of results row {_PROOF_CLAIM!r} reads "
        f"'24 of 24 (100%) vs 21 of 42 (50%)', but {_RESULTS_BEFORE} recomputes "
        "to '24 of 24 (100%) vs 20 of 42 (48%)'."
    ]


def test_dropped_before_column_fails_loud(doc_tree: Path) -> None:
    # Losing the column must fail rather than quietly stop checking every
    # history cell: the rows held to a before cell say so, and the old rates
    # left in the row are then read as current claims.
    _substitute(doc_tree, _RESULTS, "| What | Figure | Before |", "| What | Figure |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("the results table has no 'Before' column" in error for error in errors)
    assert any("claim '48% (9p2i)' disagrees" in error for error in errors)


def test_an_edited_before_file_fails_its_pin(doc_tree: Path) -> None:
    # One edited byte fails the digest pin, and the file is named rather than
    # read: a before cell is history and is never edited in place.
    path = doc_tree / _RESULTS_BEFORE
    path.write_bytes(path.read_bytes().replace(b'"games": 50', b'"games": 51', 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_RESULTS_BEFORE}: reads sha256 ")
    assert "never edited" in errors[0]


@pytest.mark.parametrize(
    ("entries", "refusal"),
    [
        pytest.param(
            [{"proof": [25, 24]}],
            "25 of 24 is not a count of a population",
            id="count-over-its-population",
        ),
        pytest.param([{}, {}], "names one replaced recording twice", id="twice"),
        pytest.param(
            [{"cells": 1}], "Extra inputs are not permitted", id="extra-field"
        ),
    ],
)
def test_malformed_before_cells_are_refused(
    doc_tree: Path,
    monkeypatch: pytest.MonkeyPatch,
    entries: list[dict[str, object]],
    refusal: str,
) -> None:
    # Planted: a file with a malformed entry, its pin moved to match, so the
    # refusal comes from reading the cells and not from the digest.
    entry: dict[str, object] = {
        "commit": "dadce2ed",
        "games": 50,
        "impostor_wins": 24,
        "read_from": "a record",
        "replaced": "stage-b-r2",
        "set": "replays/samples/9p2i",
    }
    data = json.dumps([entry | planted for planted in entries]).encode()
    (doc_tree / _RESULTS_BEFORE).write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    monkeypatch.setattr(check_doc_facts, "_RESULTS_BEFORE_SHA256", digest)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_RESULTS_BEFORE}: ")
    assert refusal in errors[0]


def test_a_set_without_cells_for_its_replaced_recording_is_named(
    doc_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Planted: the registry filing both sets at baseline 9, whose sets replaced
    # baseline 8's recording; the file holds that recording for 4p1i alone.
    monkeypatch.setattr(check_doc_facts, "era_of", lambda path: BASELINE_9)
    errors: list[str] = []
    assert list(check_doc_facts.before_cells(doc_tree, errors)) == ["4p1i"]
    assert errors == [
        f"{_RESULTS_BEFORE}: holds no before cells for replays/samples/9p2i at the "
        "baseline-8 recording it replaced."
    ]


def test_each_era_names_the_recording_its_sets_replaced() -> None:
    # An era with no name raises rather than falling back to another's cells.
    assert check_doc_facts.replaced_era(STAGE_B_R3) == "stage-b-r2"
    assert check_doc_facts.replaced_era(BASELINE_9) == "baseline-8"
    unnamed = Era("baseline-10", "a record", "2026-11-01", None)
    with pytest.raises(KeyError, match="no replaced era is named for the baseline-10"):
        check_doc_facts.replaced_era(unnamed)


# ── 2. the .env.example registries ───────────────────────────────────────────


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


def test_shell_style_toggle_export_detected(doc_tree: Path) -> None:
    # The planted proof for the assignment forms: `^AILIBI_X=` matched neither
    # an `export` prefix nor padding around the `=`, so both slipped past the
    # rule while setting the toggle exactly as the bare form does.
    for line in (
        "export AILIBI_IMPOSTOR_ROLL_CALL=1",
        "AILIBI_IMPOSTOR_ROLL_CALL = 1",
    ):
        _substitute(
            doc_tree,
            _ENV_EXAMPLE,
            _TOGGLE_EXAMPLE_LINE,
            _TOGGLE_EXAMPLE_LINE + "\n" + line,
        )
        errors = check_doc_facts.check_facts(doc_tree)
        assert len(errors) == 1, line
        assert "active export of live toggle 'impostor_roll_call'" in errors[0]
        _substitute(
            doc_tree,
            _ENV_EXAMPLE,
            _TOGGLE_EXAMPLE_LINE + "\n" + line,
            _TOGGLE_EXAMPLE_LINE,
        )


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
_TOGGLE_PARAGRAPH_HEADING = "# The impostor-answer template arm"


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


# The four independently versioned meeting experiments (P-04). The registry is
# read from meetings.evidence_profile, never copied, for the same reason the
# substrate levers are.
_EXPERIMENT_EXAMPLE_LINE = "# AILIBI_PUBLIC_ACCOUNTS=0"


def test_renamed_experiment_switch_detected(doc_tree: Path) -> None:
    # The planted rename: .env.example renames a switch and its documentation
    # is not updated. Two facets are reported -- the registered switch is
    # undocumented, and the section advertises a knob no registry claims.
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        _EXPERIMENT_EXAMPLE_LINE,
        "# AILIBI_PUBLIC_ACCTS=0",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "AILIBI_PUBLIC_ACCOUNTS is undocumented" in errors[0]
    assert "'AILIBI_PUBLIC_ACCTS='" in errors[1]
    assert "experiment registry" in errors[1]


def test_deleted_experiment_switches_detected(doc_tree: Path) -> None:
    # The appendix's probe: dropping all four lines left the gate green.
    text = _read(doc_tree, _ENV_EXAMPLE)
    for variable in EXPERIMENT_ENV_NAMES:
        text = text.replace(f"# {variable}=0\n", "")
    _write(doc_tree, _ENV_EXAMPLE, text)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == len(EXPERIMENT_ENV_NAMES)
    assert all("is undocumented" in error for error in errors)


def test_uncommented_experiment_switch_detected(doc_tree: Path) -> None:
    # A candidate stays default-OFF until an adopting record, so a copied .env
    # may not turn one on. Both facets are reported.
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        _EXPERIMENT_EXAMPLE_LINE,
        "AILIBI_PUBLIC_ACCOUNTS=1",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "no commented example line" in errors[0]
    assert f"'{_EXPERIMENT_EXAMPLE_LINE}'" in errors[0]
    assert "active export of experiment switch" in errors[1]


def test_shell_style_experiment_export_detected(doc_tree: Path) -> None:
    # A sourced template that carries `export AILIBI_PUBLIC_ACCOUNTS=1` turns a
    # candidate ON just as the bare line does; the rule that says a switch may
    # appear only as a commented example has to see both, and the padded form.
    for line in ("export AILIBI_PUBLIC_ACCOUNTS=1", "AILIBI_PUBLIC_ACCOUNTS = 1"):
        _substitute(
            doc_tree,
            _ENV_EXAMPLE,
            _EXPERIMENT_EXAMPLE_LINE,
            _EXPERIMENT_EXAMPLE_LINE + "\n" + line,
        )
        errors = check_doc_facts.check_facts(doc_tree)
        assert len(errors) == 1, line
        assert "active export of experiment switch AILIBI_PUBLIC_ACCOUNTS" in errors[0]
        _substitute(
            doc_tree,
            _ENV_EXAMPLE,
            _EXPERIMENT_EXAMPLE_LINE + "\n" + line,
            _EXPERIMENT_EXAMPLE_LINE,
        )


def test_missing_experiment_section_banner_detected(doc_tree: Path) -> None:
    # The section audit fails loud when its banner disappears rather than
    # silently auditing nothing.
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        "# Independently versioned experiments",
        "# Experiments",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'# Independently versioned experiments'" in errors[0]
    assert "cannot be located" in errors[0]


def test_experiment_registry_is_read_from_the_live_module() -> None:
    # The register is code, not a copy: every name the checker holds
    # .env.example to is the name meetings.evidence_profile resolves.
    for variable, field in EXPERIMENT_ENV_NAMES.items():
        enabled = MeetingEvidenceProfile.from_environment({variable: "1"})
        assert getattr(enabled, field) is not None
        assert getattr(MeetingEvidenceProfile.from_environment({}), field) is None


# ── 3. the results table ─────────────────────────────────────────────────────


def test_repeated_results_claim_detected(doc_tree: Path) -> None:
    # A stale row left beside a corrected one is named, and the first copy is
    # the one held to the source.
    row = "| Sample games that replay byte for byte | 100 of 100 (100%) |"
    text = _read(doc_tree, _RESULTS)
    assert row in text
    stale = row.replace("| 100 of 100 (100%) |", "| 99 of 100 (99%) |")
    _write(doc_tree, _RESULTS, text.replace(row, f"{stale}|\n{row}", 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "states 'Sample games that replay byte for byte' twice" in errors[0]
    assert "'99 of 100 (99%)'" in errors[1]


def test_replay_count_figure_derived_from_the_committed_replays(
    doc_tree: Path,
) -> None:
    # The row is recomputed from the replay files on disk.
    _substitute(doc_tree, _RESULTS, "| 100 of 100 (100%) |", "| 96 of 96 (100%) |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'96 of 96 (100%)'" in errors[0]
    assert "100 committed replays" in errors[0]


def test_empty_replay_corpus_fails_loud(doc_tree: Path) -> None:
    # An empty corpus must not read as "nothing to re-derive": that would let
    # any replay figure stand.
    for name in ("4p1i", "9p2i"):
        for replay in (doc_tree / "replays" / "samples" / name).glob("*.jsonl"):
            replay.unlink()
    errors = _without_front_page(check_doc_facts.check_facts(doc_tree))
    assert len(errors) == 2
    assert "no committed replays found" in errors[0]
    # The install block still counts the 100 candidate replays left beside them.
    assert "'200 sample and candidate recordings'" in errors[1]
    assert "makes it '100 sample and candidate recordings'" in errors[1]


def test_non_replay_jsonl_is_not_counted(doc_tree: Path) -> None:
    # The recorder writes a `<stem>.audit.jsonl` sidecar beside a replay, and
    # verify_samples.sh reconstructs only canonical replay-seed-N.jsonl files.
    # Counting a sidecar would inflate a figure claiming N of N were verified.
    (doc_tree / "replays" / "samples" / "9p2i" / "scratch.audit.jsonl").touch()
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_removed_replay_moves_the_count_figure(doc_tree: Path) -> None:
    # The replay count is read off the files on disk: one replay fewer, and the
    # figure the row must state is 99 of 99, not the 100 it says.
    replay = next(
        (doc_tree / "replays" / "samples" / "4p1i").glob("replay-seed-*.jsonl")
    )
    replay.unlink()
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        error.startswith(f"{_RESULTS}: the results row 'Sample games that replay")
        and "recomputes to '99 of 99 (100%)'" in error
        for error in errors
    )


def test_citation_figure_derived_from_the_committed_instrument(
    doc_tree: Path,
) -> None:
    # The citation row's source is the instrument's pinned assertions.
    _substitute(
        doc_tree,
        _RESULTS,
        "| 397 of 397 (100%), zero dangling |",
        "| 396 of 397 (100%), zero dangling |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'396 of 397 (100%), zero dangling'" in errors[0]
    assert _CITATION_INSTRUMENT in errors[0]


def test_instrument_pin_move_reaches_the_results_page(doc_tree: Path) -> None:
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
    assert "'397 of 397 (100%), 3 dangling'" in errors[0]


def test_the_cited_count_pin_moves_the_citation_figure(doc_tree: Path) -> None:
    # Both counts of the citation row are the instrument's pins: the cited
    # count moved there moves the figure the row must state.
    _substitute(
        doc_tree,
        _CITATION_INSTRUMENT,
        "assert nine.cited_eject_ballots == 397",
        "assert nine.cited_eject_ballots == 396",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "recomputes to '396 of 397 (100%), zero dangling'" in error for error in errors
    )


def test_vent_and_proof_rows_derived_from_the_census(doc_tree: Path) -> None:
    # Planted: one impostor ejection fewer in the census's vent band. The vent
    # row reads that cell directly, and the proof row's two halves move with it.
    _set_census_cell(doc_tree, "Impostor ejections in the vent band", "23/46 (50.0%)")
    errors = check_doc_facts.check_facts(doc_tree)
    assert errors == [
        f"{_RESULTS}: the results row {_VENT_CLAIM!r} reads '24 of 46 (52%)', but "
        f"{_CENSUS_SOURCE} recomputes to '23 of 46 (50%)'.",
        f"{_RESULTS}: the results row {_PROOF_CLAIM!r} reads '24 of 24 (100%) vs "
        f"22 of 37 (59%)', but {_CENSUS_SOURCE} recomputes to '23 of 23 (100%) "
        "vs 23 of 38 (61%)'.",
    ]


def test_a_crewmate_in_the_vent_band_refutes_the_injustice_clause(
    doc_tree: Path,
) -> None:
    # Planted: one crewmate ejection inside the vent band. The proof row's
    # "with proof" half is no longer clean, and its clause saying every
    # innocent ejection sits in the no-proof cell is refused by name.
    _set_census_cell(doc_tree, "Crewmate ejections in the vent band", "1/15 (6.7%)")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2, errors
    assert "recomputes to '24 of 25 (96%) vs 22 of 36 (61%)'" in errors[0]
    assert "puts 1 crewmate ejection(s) in the vent band" in errors[1]


def test_innocent_ejections_moved_to_the_wrong_cell_detected(doc_tree: Path) -> None:
    # The count alone is not the claim. A row stating the same 15 of 15 but
    # putting them in the proof-present cell states the opposite finding, so
    # matching the number without the placement would gate shape, not meaning.
    _substitute(
        doc_tree,
        _RESULTS,
        "15 of 15 innocent ejections sit in the no-proof cell",
        "15 of 15 innocent ejections sit in the proof-present cell",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'15 of 15 innocent ejections sit in the no-proof cell'" in errors[0]


def test_four_set_figure_kept_as_the_current_figure_detected(doc_tree: Path) -> None:
    # Planted: the figure pooled over four sets, as the README stated it before
    # the shown set moved to its own era, kept as the 9p2i set's figure.
    _substitute(
        doc_tree,
        _RESULTS,
        "| 24 of 24 (100%) vs 22 of 37 (59%) |",
        "| 326 of 326 (100%) vs 43 of 85 (51%) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'24 of 24 (100%) vs 22 of 37 (59%)'" in errors[0]
    assert _CENSUS_SOURCE in errors[0]


@pytest.mark.parametrize(
    ("old", "new", "refusal"),
    [
        pytest.param(
            "### Vent proof at meetings",
            "### Vent proof",
            "no '### Vent proof at meetings' section",
            id="section",
        ),
        pytest.param(
            "| samples/9p2i (stage-b-r3) |",
            "| the shown set |",
            "the '### Vent proof at meetings' table has no samples/9p2i column",
            id="column",
        ),
        pytest.param(
            "| Crewmate ejections in the vent band |",
            "| Crewmates in the band |",
            "the '### Vent proof at meetings' table has no samples/9p2i "
            "'Crewmate ejections in the vent band' cell reading 'k/n'",
            id="row",
        ),
    ],
)
def test_an_unreadable_census_table_fails_loud(
    doc_tree: Path, old: str, new: str, refusal: str
) -> None:
    # Losing the table must not read as "nothing to derive from", and the
    # prose check that reads the same cells does not report it twice.
    _substitute(doc_tree, _CENSUS_PAGE, old, new)
    errors = check_doc_facts.check_facts(doc_tree)
    assert errors == [
        f"{_CENSUS_PAGE}: {refusal} — the {_RESULTS} vent and proof rows have "
        "nothing to be derived from."
    ]


def test_a_census_cell_that_is_no_count_fails_loud(doc_tree: Path) -> None:
    _set_census_cell(doc_tree, "Meetings with vent proof", "n/a")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'Meetings with vent proof' cell reading 'k/n'" in errors[0]


# ── the process rows, read off the scorecard page ────────────────────────────
#
# The results page leads with how the votes were cast. Each of the four rows is held,
# value and before cell, to the shown set's table on the GENERATED markdown page
# (never its JSON). Every case below fails naming the row it moved.

_SCORECARD_PAGE = "eval/reports/process-scorecard.md"
_GROUNDED_CLAIM = (
    "Eject ballots citing what the voter saw or heard about the accused (9p2i)"
)
_DEVIATING_CLAIM = (
    "Crew eject ballots naming someone other than the voter's top suspect (9p2i)"
)
_UNEXPLAINED_CLAIM = "Ballots with no stated reason (9p2i)"
_AUTHORED_CLAIM = "Ballots whose target is the one their voter wrote (9p2i)"
_PROOF_CLAIM = (
    "Impostors among those ejected, with and without proof of their role (9p2i)"
)
_SCORECARD_SOURCE = "the samples/9p2i table of eval/reports/process-scorecard.md"
# The shown set's row-4 and row-7 lines on the page: round 2's before cell,
# then round 3's value.
_SCORECARD_UNEXPLAINED_ROW = (
    "| 4 | unexplained-decision rate | 11/691 = 0.0159 | 6/702 = 0.0085 |"
)
_SCORECARD_AUTHORED_ROW = (
    "| 7 | agent-authored share | 674/691 = 0.9754 | 692/702 = 0.9858 |"
)


def _results_row_line(text: str, claim: str) -> str:
    """The one table line of ``text`` whose first cell, links reduced, is ``claim``."""

    lines = [
        line
        for line in text.splitlines()
        if (cells := check_doc_facts.table_cells(line)) is not None
        and check_doc_facts.strip_links(cells[0]) == claim
    ]
    assert len(lines) == 1, claim
    return lines[0]


def _scorecard_section(page: str) -> str:
    """The shown set's section of the page: its heading to the next heading."""

    start = page.index("\n### samples/9p2i\n")
    end = page.index("\n### ", start + 1)
    return page[start:end]


def test_the_shown_sets_process_cells_are_read_off_the_page() -> None:
    # The committed page, read the way the rule reads it: each row's value and
    # round 2's before cell (the era the shown set replaced), and the row-7
    # detail line's teammate count.
    page = (_REPO_ROOT / _SCORECARD_PAGE).read_text(encoding="utf-8")
    cells = check_doc_facts.scorecard_process_cells(page, "samples/9p2i", "stage-b-r2")
    assert cells.rows == {
        "grounded-decision rate, EJECT": ("394/397 = 0.9924", "407/410 = 0.9927"),
        "argmax-independence: deviating EJECTs": ("56/291 = 19.2%", "65/292 = 22.3%"),
        "unexplained-decision rate": ("6/702 = 0.0085", "11/691 = 0.0159"),
        "agent-authored share": ("692/702 = 0.9858", "674/691 = 0.9754"),
    }
    assert cells.teammate_coerced == 10


def test_the_coerced_clause_counts_in_words() -> None:
    assert check_doc_facts.coerced_clause(10) == (
        "10 impostor votes against a partner turned into skips"
    )
    assert check_doc_facts.coerced_clause(1) == (
        "1 impostor vote against a partner turned into a skip"
    )
    assert check_doc_facts.coerced_clause(0) == (
        "0 impostor votes against a partner turned into skips"
    )


def test_a_process_numerator_edited_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _RESULTS, "| 394 of 397 (99%) |", "| 393 of 397 (99%) |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_RESULTS}: the results row {_GROUNDED_CLAIM!r}")
    assert "reads '393 of 397 (99%)'" in errors[0]
    assert f"{_SCORECARD_SOURCE} recomputes to '394 of 397 (99%)'" in errors[0]


def test_a_process_before_cell_edited_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _RESULTS, "| 65 of 292 (22%) |", "| 64 of 292 (22%) |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_RESULTS}: the 'Before' cell of results row {_DEVIATING_CLAIM!r}"
    )
    assert f"{_SCORECARD_SOURCE} recomputes to '65 of 292 (22%)'" in errors[0]


def test_a_scorecard_value_moved_under_an_unchanged_results_page_detected(
    doc_tree: Path,
) -> None:
    # Planted: the page moves and the README does not.
    _substitute(
        doc_tree,
        _SCORECARD_PAGE,
        _SCORECARD_UNEXPLAINED_ROW,
        _SCORECARD_UNEXPLAINED_ROW.replace("6/702 = 0.0085", "7/702 = 0.0100"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_RESULTS}: the results row {_UNEXPLAINED_CLAIM!r}")
    assert "recomputes to '7 of 702 (1%)'" in errors[0]


def test_a_deleted_process_row_detected(doc_tree: Path) -> None:
    line = _results_row_line(_read(doc_tree, _RESULTS), _DEVIATING_CLAIM)
    _substitute(doc_tree, _RESULTS, line + "\n", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_RESULTS}: the results table has no {_DEVIATING_CLAIM!r} row"
    )


def test_the_shown_sets_table_removed_detected(doc_tree: Path) -> None:
    # Planted: the page loses the shown set's section heading, then its table.
    page = _read(doc_tree, _SCORECARD_PAGE)
    _write(
        doc_tree,
        _SCORECARD_PAGE,
        page.replace("\n### samples/9p2i\n", "\n### samples/9p2i, moved\n"),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_SCORECARD_PAGE}: no '### samples/9p2i' section")
    section = _scorecard_section(page)
    table = "\n".join(line for line in section.splitlines() if line.startswith("|"))
    assert table in page
    _write(doc_tree, _SCORECARD_PAGE, page.replace(table + "\n", ""))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: the '### samples/9p2i' section has no '| # | row |' table"
    )


def test_a_scorecard_row_missing_from_the_page_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _SCORECARD_PAGE, _SCORECARD_AUTHORED_ROW + "\n", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: the '### samples/9p2i' table has no "
        "'agent-authored share' row"
    )


def test_a_before_column_of_another_era_detected(doc_tree: Path) -> None:
    # Planted: the page's before column names an era the shown set did not
    # replace, so its cells are not the previously shown recording's.
    _substitute(
        doc_tree,
        _SCORECARD_PAGE,
        "| # | row | before: stage-b-r2, as published",
        "| # | row | before: baseline-9, as published",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: the '### samples/9p2i' table has no before column "
        "naming the stage-b-r2 era"
    )


def test_the_teammate_count_edited_detected(doc_tree: Path) -> None:
    # Planted: the count beside the authored share moved...
    _substitute(
        doc_tree,
        _RESULTS,
        "; 10 impostor votes against a partner turned into skips |",
        "; 9 impostor votes against a partner turned into skips |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_RESULTS}: the results row {_AUTHORED_CLAIM!r}")
    assert (
        "recomputes to '692 of 702 (99%); 10 impostor votes against a partner "
        "turned into skips'"
    ) in errors[0]


def test_the_page_teammate_count_moved_detected(doc_tree: Path) -> None:
    # ...and the page's row-7 detail moved under an unchanged README.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    moved = section.replace(
        "typed guard rewrites teammate_coerced 10;",
        "typed guard rewrites teammate_coerced 11;",
    )
    assert moved != section
    _write(doc_tree, _SCORECARD_PAGE, page.replace(section, moved))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert f"results row {_AUTHORED_CLAIM!r}" in errors[0]
    assert "11 impostor votes against a partner" in errors[0]


def test_the_row_7_detail_line_missing_detected(doc_tree: Path) -> None:
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    detail = next(
        line for line in section.splitlines() if line.startswith("Row 7 detail:")
    )
    _write(
        doc_tree, _SCORECARD_PAGE, page.replace(section, section.replace(detail, ""))
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: the '### samples/9p2i' section has no "
        "'Row 7 detail: typed guard rewrites' line"
    )


def test_an_unreadable_row_7_detail_detected(doc_tree: Path) -> None:
    # Planted: the detail line's typed reasons lose their counts, so the
    # teammate count beside the authored share has nothing to be read from.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    garbled = section.replace(
        "typed guard rewrites teammate_coerced 10;",
        "typed guard rewrites teammate_coerced ten;",
    )
    assert garbled != section
    _write(doc_tree, _SCORECARD_PAGE, page.replace(section, garbled))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: the '### samples/9p2i' section's row-7 detail reads "
        "'teammate_coerced ten'"
    )


def test_a_shown_set_with_no_replaced_era_is_named(
    doc_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An era with no named replaced recording has no before column on the page
    # that could be the previous recording's: refused by name.
    unnamed = Era("baseline-10", "a record", "2026-11-01", None)
    monkeypatch.setattr(check_doc_facts, "era_of", lambda path: unnamed)
    errors: list[str] = []
    check_doc_facts.check_process_rows(doc_tree, _read(doc_tree, _RESULTS), errors)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: no replaced era is named for the baseline-10 era"
    )


def test_the_before_column_follows_the_registrys_replaced_era(
    doc_tree: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The before column is picked by the era the registry says the shown set's
    # recording replaced, never by a fixed id. Planted: the registry filing
    # samples/9p2i under round 2, whose recording replaced baseline 9's. The
    # committed page's before column names round 2, so it is refused, naming
    # baseline 9...
    from eval.eras import STAGE_B_R2

    monkeypatch.setattr(check_doc_facts, "era_of", lambda path: STAGE_B_R2)
    errors: list[str] = []
    check_doc_facts.check_process_rows(doc_tree, _read(doc_tree, _RESULTS), errors)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: the '### samples/9p2i' table has no before column "
        "naming the baseline-9 era"
    )
    # ...and a page whose before column names baseline 9 is read from it.
    _substitute(
        doc_tree,
        _SCORECARD_PAGE,
        "| # | row | before: stage-b-r2, as published",
        "| # | row | before: baseline-9, as published",
    )
    errors = []
    check_doc_facts.check_process_rows(doc_tree, _read(doc_tree, _RESULTS), errors)
    assert errors == []


def test_a_page_with_no_typed_rewrites_reads_a_zero_count(doc_tree: Path) -> None:
    # Planted: the page's row-7 detail reads "none", the way a set with no
    # guard rewrite prints it; the count beside the authored share is then 0.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    none = section.replace(
        "typed guard rewrites teammate_coerced 10;", "typed guard rewrites none;"
    )
    assert none != section
    _write(doc_tree, _SCORECARD_PAGE, page.replace(section, none))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert f"results row {_AUTHORED_CLAIM!r}" in errors[0]
    assert (
        "'692 of 702 (99%); 0 impostor votes against a partner turned into skips'"
        in errors[0]
    )


def _shown_set_page_cells(page: str) -> tuple[dict[str, tuple[str, str]], int]:
    """The rule's read of the shown set's table: its rows and teammate count."""

    cells = check_doc_facts.scorecard_process_cells(page, "samples/9p2i", "stage-b-r2")
    return cells.rows, cells.teammate_coerced


def test_the_value_and_before_columns_are_found_by_their_headers(
    doc_tree: Path,
) -> None:
    # Each cell is read from the column its header names, never from a fixed
    # position. Planted: the shown set's table with its before and value
    # columns traded, the header and every row, so the same cells sit in each
    # other's place and are read the same.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    traded: list[str] = []
    for line in section.splitlines(keepends=True):
        cells = check_doc_facts.table_cells(line)
        if cells is not None:
            cells[-2], cells[-1] = cells[-1], cells[-2]
            line = "| " + " | ".join(cells) + " |\n"
        traded.append(line)
    assert "| # | row | value | before: stage-b-r2, as published" in "".join(traded)
    planted = page.replace(section, "".join(traded))
    assert _shown_set_page_cells(planted) == _shown_set_page_cells(page)
    _write(doc_tree, _SCORECARD_PAGE, planted)
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_table_ahead_of_the_row_table_is_passed_over(doc_tree: Path) -> None:
    # The section's row table is the one whose header opens "| # | row |", not
    # its first table. Planted: a small table between the section's before
    # sentence and the row table, which the rule reads past.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    header = "| # | row | before: stage-b-r2, as published"
    assert section.count(header) == 1
    lead = (
        "| set | games | meetings |\n| --- | --- | --- |\n"
        "| samples/9p2i | 50 | 119 |\n\n"
    )
    planted = page.replace(section, section.replace(header, lead + header))
    assert _shown_set_page_cells(planted) == _shown_set_page_cells(page)
    _write(doc_tree, _SCORECARD_PAGE, planted)
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_table_after_the_row_table_is_passed_over(doc_tree: Path) -> None:
    # The row table ends at its first line that is not a table line, so a later
    # table in the section is never read into it. Planted: a table of the row
    # table's width between the row table and the row-2 detail line, whose
    # second cell carries a process row's label; the rule reads past it.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    detail = "\nRow 2 detail: "
    assert section.count(detail) == 1
    trail = (
        "\n| set | row | before | value |\n| --- | --- | --- | --- |\n"
        "| samples/9p2i | agent-authored share | 1/2 = 0.5000 | 1/1 = 1.0000 |\n"
    )
    planted = page.replace(section, section.replace(detail, trail + detail))
    assert _shown_set_page_cells(planted) == _shown_set_page_cells(page)
    _write(doc_tree, _SCORECARD_PAGE, planted)
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_row_table_with_no_value_column_is_refused(doc_tree: Path) -> None:
    # Planted: the shown set's table loses its value column, the header and
    # every row, so no cell of it is the shown recording's own. The page is
    # refused naming the column, never read from another one.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    dropped: list[str] = []
    for line in section.splitlines(keepends=True):
        cells = check_doc_facts.table_cells(line)
        if cells is not None:
            line = "| " + " | ".join(cells[:-1]) + " |\n"
        dropped.append(line)
    assert "| # | row | before: stage-b-r2, as published at `2eed2e92` |\n" in (
        "".join(dropped)
    )
    planted = page.replace(section, "".join(dropped))
    refusal = "the '### samples/9p2i' table has no 'value' column"
    with pytest.raises(check_doc_facts.ScorecardPageError) as raised:
        _shown_set_page_cells(planted)
    assert raised.value.args == (refusal,)
    _write(doc_tree, _SCORECARD_PAGE, planted)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_SCORECARD_PAGE}: {refusal} — ")


def test_the_teammate_count_is_read_among_other_typed_rewrites(
    doc_tree: Path,
) -> None:
    # The row-7 detail line lists each typed reason with its count, sorted by
    # name, as the ml_corpus/9p2i line on this page and round 2's line at
    # 2eed2e92 do. Planted: the shown set's line with a reason on either side
    # of the teammate count; the count read beside the authored share stays
    # 10, and the front door still agrees.
    page = _read(doc_tree, _SCORECARD_PAGE)
    section = _scorecard_section(page)
    mixed = section.replace(
        "typed guard rewrites teammate_coerced 10;",
        "typed guard rewrites invalid_target 1, teammate_coerced 10, "
        "uncited_coerced 2;",
    )
    assert mixed != section
    planted = page.replace(section, mixed)
    assert _shown_set_page_cells(planted) == _shown_set_page_cells(page)
    assert _shown_set_page_cells(planted)[1] == 10
    _write(doc_tree, _SCORECARD_PAGE, planted)
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_truncated_scorecard_row_is_refused(doc_tree: Path) -> None:
    # Planted: the page's row-4 line loses its value cell, so its last cell is
    # the before column's and no cell of it can be read as the value.
    _substitute(
        doc_tree,
        _SCORECARD_PAGE,
        _SCORECARD_UNEXPLAINED_ROW,
        "| 4 | unexplained-decision rate | 11/691 = 0.0159 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(
        f"{_SCORECARD_PAGE}: the '### samples/9p2i' table has no "
        "'unexplained-decision rate' row"
    )


def test_a_linked_claim_is_still_read_as_its_row(doc_tree: Path) -> None:
    # A link inside a claim leaves it the same claim, and every check that
    # reads the whole row still finds it: planted, the proof row's claim
    # carries a link and its injustice clause moves.
    linked = _PROOF_CLAIM.replace(
        "proof of their role", "[proof of their role](docs/glossary.md)"
    )
    assert linked != _PROOF_CLAIM
    _substitute(doc_tree, _RESULTS, f"| {_PROOF_CLAIM} |", f"| {linked} |")
    assert check_doc_facts.check_facts(doc_tree) == []
    _substitute(
        doc_tree,
        _RESULTS,
        "15 of 15 innocent ejections sit in the no-proof cell",
        "14 of 14 innocent ejections sit in the no-proof cell",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert (
        "does not state '15 of 15 innocent ejections sit in the no-proof cell'"
        in errors[0]
    )


@pytest.mark.parametrize(
    ("numerator", "denominator", "figure"),
    [
        (394, 397, "394 of 397 (99%)"),
        (56, 291, "56 of 291 (19%)"),
        (6, 702, "6 of 702 (1%)"),
        (0, 198, "0 of 198 (0%)"),
        (24, 24, "24 of 24 (100%)"),
        # Rounded as the win rates are, round(100 * k / n): half to even.
        (1, 8, "1 of 8 (12%)"),
        (3, 8, "3 of 8 (38%)"),
    ],
)
def test_one_helper_renders_each_fraction(
    numerator: int, denominator: int, figure: str
) -> None:
    assert check_doc_facts.fraction_figure(numerator, denominator) == figure


def test_a_fraction_over_no_population_raises() -> None:
    with pytest.raises(ValueError, match="no population"):
        check_doc_facts.fraction_figure(0, 0)


@pytest.mark.parametrize(
    ("cell", "figure"),
    [
        ("394/397 = 0.9924", "394 of 397 (99%)"),
        ("56/291 = 19.2%", "56 of 291 (19%)"),
        (" 11/691 = 0.0159 ", "11 of 691 (2%)"),
    ],
)
def test_a_scorecard_cell_is_restated_in_the_tables_form(
    cell: str, figure: str
) -> None:
    assert check_doc_facts.scorecard_fraction(cell) == figure


@pytest.mark.parametrize(
    "cell", ["394 / 397 = 0.9924", "394/397", "0.9924", "394 of 397 (99%)", ""]
)
def test_a_scorecard_cell_of_another_shape_is_refused(cell: str) -> None:
    with pytest.raises(check_doc_facts.ScorecardPageError) as refused:
        check_doc_facts.scorecard_fraction(cell)
    assert refused.value.args[0] == (
        f"the cell {cell!r} is not a 'k/n = rate' fraction"
    )


def test_a_partition_cell_is_two_fractions_in_the_tables_form() -> None:
    assert (
        check_doc_facts.partition_figure((24, 24), (22, 37))
        == "24 of 24 (100%) vs 22 of 37 (59%)"
    )


# ── 4. the real-report example ───────────────────────────────────────────────


def test_report_example_ejection_count_drift_detected(doc_tree: Path) -> None:
    # The example exists because the fake provider's report is empty; its
    # scalars come from the committed report, not from prose.
    _substitute(doc_tree, _RESULTS, "records 61 ejections", "records 92 ejections")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'61 ejections'" in errors[0]
    assert "total_ejections" in errors[0]


def test_report_example_impostor_count_drift_detected(doc_tree: Path) -> None:
    # (was the vote-correctness rate, before the example stated counts)
    _substitute(doc_tree, _RESULTS, "46 removed an impostor", "45 removed an impostor")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'46 removed an impostor'" in errors[0]
    assert "impostor_ejections" in errors[0]


def test_report_example_evidence_count_drift_detected(doc_tree: Path) -> None:
    # (was the ejection-accuracy rate, before the example stated counts)
    _substitute(doc_tree, _RESULTS, "36 of those 46 with", "40 of those 46 with")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'36 of those 46 with evidence against that player'" in errors[0]
    assert "evidence_backed_impostor_ejections" in errors[0]


def test_missing_report_example_paragraph_fails_loud(doc_tree: Path) -> None:
    # Dropping the example must not read as "nothing to check": the front door
    # would then be silent about what a fake-provider report looks like.
    _substitute(
        doc_tree,
        _RESULTS,
        "The fake provider's report is empty on purpose:",
        "The fake provider's report is unusual:",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no paragraph naming" in errors[0]


def test_eval_report_count_drift_reaches_the_report_example(doc_tree: Path) -> None:
    # A count moved in the report itself moves the README's example with it,
    # beside the stamp the count's own rate no longer matches.
    _substitute(
        doc_tree,
        _EVAL_REPORT_9P2I,
        '"impostor_ejections": 46,',
        '"impostor_ejections": 47,',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        error.startswith(f"{_RESULTS}:")
        and "'47 removed an impostor'" in error
        and "impostor_ejections as 47" in error
        for error in errors
    )
    # ...and the evidence clause's denominator, which is the same count read
    # again, so the example cannot keep "36 of those 46" once the report says 47.
    assert any(
        error.startswith(f"{_RESULTS}:")
        and "'36 of those 47 with evidence against that player'" in error
        for error in errors
    )


def test_a_moved_ejection_total_reaches_the_report_example(doc_tree: Path) -> None:
    # Planted: the report's own total of ejections moved by one. The README's
    # example states that total, so it no longer matches the report it cites.
    _substitute(
        doc_tree,
        _EVAL_REPORT_9P2I,
        '"total_ejections": 61,',
        '"total_ejections": 62,',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    readme = [error for error in errors if error.startswith(f"{_RESULTS}:")]
    assert readme == [
        f"{_RESULTS}: the real-report example does not state '62 ejections' — "
        f"{_EVAL_REPORT_9P2I} records total_ejections as 62."
    ]


def test_eval_report_without_vote_correctness_block_fails_loud(
    doc_tree: Path,
) -> None:
    # Format drift must not read as "nothing to check": a report with no
    # vote_correctness block leaves the real-report example sourceless.
    _write(doc_tree, _EVAL_REPORT_9P2I, "{}\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _EVAL_REPORT_9P2I in errors[0]
    assert '"vote_correctness":' in errors[0]


# ── 5. the prose figures ─────────────────────────────────────────────────────


# The results page's prose figures, each perturbed in the live page: (the text, its
# perturbation, the claim the error names, the claim the source makes it).
_PROSE_PERTURBATIONS = (
    pytest.param(
        "[215 of 235 times]",
        "[214 of 235 times]",
        "hit an impostor 214 of 235 times (91%)",
        "hit an impostor 215 of 235 times (91%)",
        id="followers-hit",
    ),
    pytest.param(
        "times](eval/reports/process-scorecard.md) (91%)",
        "times](eval/reports/process-scorecard.md) (92%)",
        "hit an impostor 215 of 235 times (92%)",
        "hit an impostor 215 of 235 times (91%)",
        id="followers-percent",
    ),
    pytest.param(
        "the 56 against it hit one twice (4%)",
        "the 56 against it hit one once (4%)",
        "the 56 against it hit one once (4%)",
        "the 56 against it hit one twice (4%)",
        id="deviators-hit",
    ),
    pytest.param(
        "the 56 against it",
        "the 55 against it",
        "the 55 against it hit one twice (4%)",
        "the 56 against it hit one twice (4%)",
        id="deviators",
    ),
    pytest.param(
        "chance is about one in three",
        "chance is about one in four",
        "chance is about one in four",
        "chance is about one in three",
        id="chance",
    ),
    pytest.param(
        "In the 24 meetings with one",
        "In the 23 meetings with one",
        "In the 23 meetings with one",
        "In the 24 meetings with one",
        id="vent-flagged-meetings",
    ),
    pytest.param(
        "in the 95 without",
        "in the 96 without",
        "in the 96 without, 22 of 37 did and 15 removed crewmates",
        "in the 95 without, 22 of 37 did and 15 removed crewmates",
        id="vent-unflagged-meetings",
    ),
    pytest.param(
        "[22 of 37](eval/reports/gameplay-census.md) did",
        "[21 of 37](eval/reports/gameplay-census.md) did",
        "in the 95 without, 21 of 37 did and 15 removed crewmates",
        "in the 95 without, 22 of 37 did and 15 removed crewmates",
        id="vent-unflagged-share",
    ),
    pytest.param(
        "15 removed crewmates",
        "14 removed crewmates",
        "in the 95 without, 22 of 37 did and 14 removed crewmates",
        "in the 95 without, 22 of 37 did and 15 removed crewmates",
        id="vent-unflagged-innocent",
    ),
    pytest.param(
        "[394 of 397](eval/reports/process-scorecard.md) votes to eject",
        "[393 of 397](eval/reports/process-scorecard.md) votes to eject",
        "393 of 397 votes to eject",
        "394 of 397 votes to eject",
        id="cited-votes",
    ),
    pytest.param(
        "carries all 100 games",
        "carries all 96 games",
        "carries all 96 games",
        "carries all 100 games",
        id="demo-games",
    ),
    pytest.param(
        "One of five import contracts",
        "One of four import contracts",
        "of four import contracts",
        "of five import contracts",
        id="import-contracts",
    ),
    pytest.param(
        "Re-run the 200 sample and candidate recordings",
        "Re-run the 199 sample and candidate recordings",
        "199 sample and candidate recordings",
        "200 sample and candidate recordings",
        id="verified-recordings",
    ),
)


@pytest.mark.parametrize(("old", "new", "stated", "derived"), _PROSE_PERTURBATIONS)
def test_a_drifted_prose_figure_fails_by_name(
    doc_tree: Path, old: str, new: str, stated: str, derived: str
) -> None:
    # Planted: one figure of the live README's prose moved off its source. Each
    # is named once, with the claim as stated and as its source makes it.
    _substitute(doc_tree, _RESULTS, old, new)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1, errors
    assert f"the claim {stated!r} disagrees" in errors[0]
    assert f"which makes it {derived!r}" in errors[0]


# Each prose claim reworded out of its shape: the sentence stops stating the
# figure, which fails rather than leaving the source bound to nothing.
_PROSE_REWORDINGS = (
    pytest.param("hit an impostor [215", "found an impostor [215", id="followers"),
    pytest.param("hit one twice", "hit one rarely, twice", id="deviators"),
    pytest.param("about one in three", "about a third", id="chance"),
    pytest.param("meetings with one,", "meetings with such a sighting,", id="flagged"),
    pytest.param("95 without,", "95 others,", id="unflagged"),
    pytest.param("every ejection removed", "each ejection removed", id="clean-record"),
    pytest.param("never ejected a crewmate", "ejected no crewmate", id="headline"),
    pytest.param("votes to eject cite", "eject votes cite", id="cited-votes"),
    pytest.param("carries all 100 games", "carries every game", id="demo-games"),
    pytest.param("One of five import", "One import", id="import-contracts"),
    pytest.param("sample and candidate recordings", "recordings", id="verified"),
)


@pytest.mark.parametrize(("old", "new"), _PROSE_REWORDINGS)
def test_a_prose_figure_reworded_away_fails_loud(
    doc_tree: Path, old: str, new: str
) -> None:
    _substitute(doc_tree, _RESULTS, old, new)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1, errors
    assert "no sentence matching" in errors[0]
    assert "no longer stated" in errors[0]


def test_the_demo_count_enumerates_the_games_the_bundle_bakes() -> None:
    # The checker restates the builder's rule rather than importing it, so the
    # two listings are held equal over the committed samples.
    import build_demo_bundle

    assert check_doc_facts.demo_bundle_games(_REPO_ROOT) == tuple(
        (game.set_name, game.seed) for game in build_demo_bundle.games_to_bake()
    )


def test_a_new_sample_set_moves_the_demo_count(doc_tree: Path) -> None:
    # Planted: a third set directory holding one recording. The bundle bakes it,
    # so the README's demo count fails by name, as does the verifier count that
    # walks the same root; a count over the two named sets alone would pass.
    recording = doc_tree / "replays" / "samples" / "5p1i" / "replay-seed-1.jsonl"
    recording.parent.mkdir()
    recording.touch()
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2, errors
    demo = [error for error in errors if "'carries all 100 games' disagrees" in error]
    assert len(demo) == 1, errors
    assert "which makes it 'carries all 101 games'" in demo[0]
    assert any(
        "'200 sample and candidate recordings' disagrees" in error for error in errors
    ), errors


@pytest.mark.parametrize(
    ("sentence", "stated", "derived"),
    [
        pytest.param(
            "Followers were right 214 of 235 times.",
            "214 of 235",
            "215 of 235",
            id="another-follower-claim",
        ),
        pytest.param(
            "Without one, 20 of 37 ejections removed an impostor.",
            "20 of 37",
            "22 of 37",
            id="another-unflagged-share",
        ),
        pytest.param(
            "Elsewhere 16 removed crewmates.",
            "16 removed crewmates",
            "15 removed crewmates",
            id="another-innocent-count",
        ),
    ],
)
def test_a_second_copy_of_a_prose_figure_is_held_too(
    doc_tree: Path, sentence: str, stated: str, derived: str
) -> None:
    # Planted: a correct sentence kept and a stale retelling appended beside it.
    # The copy is refused rather than left to drift on its own.
    _write(doc_tree, _RESULTS, _read(doc_tree, _RESULTS) + f"\n{sentence}\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1, errors
    assert f"the claim {stated!r} disagrees" in errors[0]
    assert f"which makes it {derived!r}" in errors[0]


_ROLE_CORRECT_CELL = "215/235 = 91.5% vs 2/56 = 3.6% (chance 32.8%)"


def test_a_re_recorded_role_correct_cell_moves_the_prose(doc_tree: Path) -> None:
    # Planted: the scorecard re-recorded under the README; the sentence that
    # retells the old cell fails rather than standing beside the new one.
    _substitute(
        doc_tree,
        "eval/reports/process-scorecard.md",
        f"| {_ROLE_CORRECT_CELL} |",
        "| 220/240 = 91.7% vs 1/51 = 2.0% (chance 24.6%) |",
    )
    every = check_doc_facts.check_facts(doc_tree)
    assert any(error.startswith(_FRONT_PAGE) and "'215'" in error for error in every)
    errors = _without_front_page(every)
    assert len(errors) == 3, errors
    assert "makes it 'hit an impostor 220 of 240 times (92%)'" in errors[0]
    assert "makes it 'the 51 against it hit one once (2%)'" in errors[1]
    assert "makes it 'chance is about one in four'" in errors[2]


def test_a_deviator_count_past_twice_reads_as_times() -> None:
    # A re-record whose deviators hit three times reads "hit one three times",
    # and the claim shape still reads that sentence.
    assert [check_doc_facts.repeat_word(count) for count in (1, 2, 3)] == [
        "once",
        "twice",
        "three times",
    ]
    match = check_doc_facts._DEVIATOR_PROSE.search(
        "the 56 against it hit one three times (5%)"
    )
    assert match is not None
    assert match.groups() == ("56", "three times", "5")


def test_a_misshapen_role_correct_cell_fails_loud(doc_tree: Path) -> None:
    _substitute(
        doc_tree,
        "eval/reports/process-scorecard.md",
        f"| {_ROLE_CORRECT_CELL} |",
        "| 215/235 = 91.5% vs 2/56 = 3.6% |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1, errors
    assert "role-correct, followers vs deviators" in errors[0]
    assert "cannot be derived from it" in errors[0]


def test_a_scorecard_without_the_role_correct_row_fails_loud(doc_tree: Path) -> None:
    # Planted: the row the sentence retells dropped from the shown set's table.
    # No other check reads it, so this one names it.
    page = _read(doc_tree, "eval/reports/process-scorecard.md")
    row = next(
        line
        for line in page.splitlines(keepends=True)
        if line.endswith(f"| {_ROLE_CORRECT_CELL} |\n")
    )
    _write(doc_tree, "eval/reports/process-scorecard.md", page.replace(row, ""))
    errors = _without_front_page(check_doc_facts.check_facts(doc_tree))
    assert len(errors) == 1, errors
    assert (
        "has no 'argmax-independence: role-correct, followers vs deviators' row"
        in errors[0]
    )


def test_a_re_recorded_grounded_cell_moves_the_cited_vote_sentence(
    doc_tree: Path,
) -> None:
    # Planted: the scorecard's grounded EJECT cell re-recorded under the README.
    # The results row is named, and the prose that retells the same cell is
    # named with it rather than left behind.
    _substitute(
        doc_tree,
        "eval/reports/process-scorecard.md",
        "| 394/397 = 0.9924 |",
        "| 393/397 = 0.9899 |",
    )
    errors = _without_front_page(check_doc_facts.check_facts(doc_tree))
    assert len(errors) == 2, errors
    assert "recomputes to '393 of 397 (99%)'" in errors[0]
    assert "the claim '394 of 397 votes to eject' disagrees" in errors[1]
    assert "which makes it '393 of 397 votes to eject'" in errors[1]


def test_a_crewmate_ejected_with_vent_proof_refutes_the_clean_record(
    doc_tree: Path,
) -> None:
    # Planted: one more crewmate ejection, in a meeting with vent proof but
    # outside the band. Both README sentences saying no such meeting ejected a
    # crewmate are refused by name, and the proof row's crewmate count moves.
    _set_census_cell(doc_tree, "Crewmate ejections in the vent band", "0/16 (0.0%)")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 4, errors
    assert "'16 of 16 innocent ejections sit in the no-proof cell'" in errors[1]
    assert "'never ejected a crewmate' is refuted" in errors[2]
    assert "'every ejection removed an impostor' is refuted" in errors[3]
    assert "ejected 1 crewmate(s)" in errors[3]


def test_a_re_recorded_unflagged_cell_moves_the_vent_sentence(doc_tree: Path) -> None:
    # Planted: a re-record with one more crewmate ejected in a meeting without
    # vent proof, both census cells moved together.
    _set_census_cell(
        doc_tree, "Ejections without vent proof that removed an impostor", "22/38"
    )
    _set_census_cell(doc_tree, "Crewmate ejections in the vent band", "0/16 (0.0%)")
    errors = _without_front_page(check_doc_facts.check_facts(doc_tree))
    assert len(errors) == 3, errors
    assert "vs 22 of 38 (58%)" in errors[0]
    assert "'16 of 16 innocent ejections sit in the no-proof cell'" in errors[1]
    assert (
        "makes it 'in the 95 without, 22 of 38 did and 16 removed crewmates'"
        in errors[2]
    )


def test_a_sixth_import_contract_moves_the_count(doc_tree: Path) -> None:
    config = _read(doc_tree, ".importlinter")
    sixth = (
        "\n[importlinter:llm_must_not_import_engine]\n"
        "name = LLM must not import engine\n"
        "type = forbidden\n"
        "source_modules =\n    llm\n"
        "forbidden_modules =\n    engine\n"
    )
    _write(doc_tree, ".importlinter", config + sixth)
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1, errors
    assert "makes it 'of six import contracts'" in errors[0]
    assert "6 contract sections of .importlinter" in errors[0]


def test_a_config_without_contracts_fails_loud(doc_tree: Path) -> None:
    _write(doc_tree, ".importlinter", "[importlinter]\nroot_packages =\n    agents\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1, errors
    assert "no '[importlinter:<name>]' contract section" in errors[0]


def test_a_removed_candidate_replay_moves_the_verified_count(doc_tree: Path) -> None:
    # The install block counts every replay the bare verifier re-runs, the
    # candidate rounds' with the samples'; the demo serves the samples alone.
    replays = sorted((doc_tree / "replays" / "candidates").glob("*/*/*.jsonl"))
    assert len(replays) == 100
    replays[0].unlink()
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1, errors
    assert "makes it '199 sample and candidate recordings'" in errors[0]


# ── 6. the ML results table ──────────────────────────────────────────────────


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


def test_missing_ml_results_table_fails_loud(doc_tree: Path) -> None:
    # Losing the table must not read as "nothing to derive from".
    _substitute(doc_tree, _ML_PAGE, "| policy | impostor win |", "| model | win |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no results table" in errors[0]


# ── 7. the command line ──────────────────────────────────────────────────────


def test_main_reports_every_failure_at_once(
    doc_tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _substitute(doc_tree, _RESULTS, "2026-09-22", "2026-08-19")
    _substitute(doc_tree, _RESULTS, "36% (4p1i)", "30% (4p1i)")
    assert check_doc_facts.main(["--repo-root", str(doc_tree)]) == 1
    err = capsys.readouterr().err
    assert "Doc-fact check failed:" in err
    assert "'36% (4p1i)'" in err
    assert "'2026-09-22'" in err


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


# ── 11. the front page's figures ─────────────────────────────────────────────


def test_a_front_page_figure_off_by_one_detected(doc_tree: Path) -> None:
    # Planted: one figure under the README's findings heading moved by one.
    _substitute(
        doc_tree,
        _FRONT_PAGE,
        "hit an impostor 215 of 235 times",
        "hit an impostor 216 of 235 times",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_FRONT_PAGE}:")
    assert "'216'" in errors[0]


def test_a_front_page_figure_follows_its_source(doc_tree: Path) -> None:
    # Planted: the scorecard's role-correct cell moved under an unchanged README,
    # so the README's 215 is no longer a figure the sources produce. The results
    # page fails on the same move; only the front-page error is asserted here.
    _substitute(doc_tree, _SCORECARD_PAGE, "215/235 = 91.5%", "216/235 = 91.9%")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        error.startswith(f"{_FRONT_PAGE}:") and "'215'" in error for error in errors
    )


def test_a_front_page_without_its_findings_heading_fails_loud(
    doc_tree: Path,
) -> None:
    _substitute(doc_tree, _FRONT_PAGE, "## What I found\n", "## Findings\n")
    assert check_doc_facts.check_facts(doc_tree) == [
        f"{_FRONT_PAGE}: no '## What I found' section — the front page's figures "
        "have nothing to be checked against."
    ]


def test_names_and_decimals_under_the_findings_heading_are_not_figures(
    doc_tree: Path,
) -> None:
    # A token glued to a letter, a dot, a comma or a hyphen is a set name, a
    # player id, a decimal or a thousands group, never a figure to bind.
    _substitute(
        doc_tree,
        _FRONT_PAGE,
        "## What I found\n",
        "## What I found\n\nIn 9p2i, p-5 accused p-4; 91.5% of 2,500 lines.\n",
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_a_missing_witness_row_fails_loud(doc_tree: Path) -> None:
    # Planted: the census's lone-witness rows gone, so the README's witness
    # figures have no source; the check names the band rather than passing.
    page = _read(doc_tree, _CENSUS_PAGE)
    kept = [
        line for line in page.splitlines() if not line.startswith("| one living crew")
    ]
    _write(doc_tree, _CENSUS_PAGE, "\n".join(kept) + "\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        error.startswith(f"{_CENSUS_PAGE}:") and "one living crew witness" in error
        for error in errors
    )
