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

import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest

import check_doc_facts

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "check_doc_facts.py"

# Exactly the files the checker reads, in their relative layout so the tmp tree
# is a faithful (and perturbable) stand-in for a checkout.
_COPIED = (
    "README.md",
    ".env.example",
    "replays/samples/4p1i/MANIFEST.md",
    "replays/samples/9p2i/MANIFEST.md",
    "audits/audit-phase-18-close.md",
    "audits/audit-phase-19-close.md",
    # The ladder-tip audit: the fixture stands every other audits/*.md up EMPTY,
    # so the one the checker actually reads has to be copied whole.
    "audits/audit-phase-20-baseline-7.md",
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
    "tests/eval/test_vj_instruments.py",
    "tests/eval/test_deduction_metrics.py",
    "frontend/src/components/ReplayPicker.tsx",
    "docs/ml-program.md",
    "training/reports/results-finalist-eval.jsonl",
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
_PROOF_AUDIT = "audits/audit-phase-19-close.md"
_PROOF_ROW = (
    "| **direct-proof accuracy** | **68/68 = 1.000** [0.947, 1.0] | "
    "**213/213 = 1.000** [0.982, 1.0] | 9/9 = 1.000 | 20/20 = 1.000 |\n"
)
_NON_PROOF_ROW = (
    "| **non-direct accuracy** | **10/33 = 0.303** [0.174, 0.473] | "
    "**35/89 = 0.393** [0.298, 0.497] | 1/3 = 0.333 (advisory) | 0/0 — no cell |\n"
)
_INNOCENT_ROW = "| innocent ejections (all in the non-direct cell) | 23 | 54 | 2 | 0 |"
_PROOF_INNOCENT_ROW = (
    "| proof-present innocent ejections | **0** | **0** | **0** | **0** |"
)
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
_LADDER_TIP_AUDIT = "audits/audit-phase-20-baseline-7.md"
# The reading guide's §3 cross-tab, as committed.
_FLAGGED_ROW = "| yes (69 meetings) | 69 | 0 |"
_UNFLAGGED_ROW = "| no (83 meetings) | 16 | 14 |"
# The one dialect term the front door keeps, and the link that defines it. Its
# first use is the results table's before-column header.
_BASELINE_LINK = "[baseline 7](docs/glossary.md#baseline-n-the-reference-recording)"
_BEFORE_COLUMN_LINK = (
    "[At baseline 6](docs/glossary.md#baseline-n-the-reference-recording)"
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
    for document in check_doc_facts._LINKED_DOCUMENTS:
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
    _substitute(doc_tree, _README, "2026-08-25", "2026-08-19")
    errors = check_doc_facts.check_facts(doc_tree)
    assert all(_README in error for error in errors)
    paragraph = [error for error in errors if "refresh date '2026-08-25'" in error]
    assert len(paragraph) == 1
    dated = [
        error for error in errors if "dates the current reference recording" in error
    ]
    assert len(dated) == len(errors) - 1 >= 1


def test_paragraph_date_drift_not_alibied_elsewhere(doc_tree: Path) -> None:
    # The provenance claim is bound to its paragraph: the correct date
    # appearing somewhere else in the file must not satisfy a drifted
    # paragraph (the pre-hardening checker accepted exactly this).
    _substitute(doc_tree, _README, "regenerated 2026-08-25", "regenerated 2026-08-19")
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README)
        + "\nAn unrelated historical note mentioning 2026-08-25.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        "'regenerated 2026-08-19'" in error and "refresh date '2026-08-25'" in error
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
        "regenerated 2026-08-25",
        "regenerated 2026-08-25 (an earlier draft said regenerated 2026-08-19)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert any(
        "'regenerated 2026-08-19'" in error and "refresh date '2026-08-25'" in error
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
        "`qwen3_6_27b` `v4` prompt set",
        "`qwen3_6_27b` `v2` prompt set",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'v4'" in errors[0]
    assert "`prompt_versions` column" in errors[0]


def test_missing_provenance_paragraph_fails_loud(doc_tree: Path) -> None:
    # Losing the paragraph anchor is format drift, not a vacuous pass.
    _substitute(doc_tree, _README, "regenerated 2026-08-25", "refreshed 2026-08-25")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "exactly one sample-provenance paragraph" in errors[0]


def test_repeated_claims_survive_a_lost_provenance_paragraph(doc_tree: Path) -> None:
    # ...and it must not take the rest of the front door's gate down with it:
    # the other documents repeat these facts on their own account.
    _substitute(doc_tree, _README, "regenerated 2026-08-25", "refreshed 2026-08-25")
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| 36% (4p1i), 24% (9p2i) |",
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
    assert "ladder tip at baseline 7" in errors[0]


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
    assert "12/50 = 24%" in errors[0]


def test_in_paragraph_stale_claim_detected(doc_tree: Path) -> None:
    # The correct substring being present must not exempt the paragraph's
    # OTHER claims: a stale duplicate beside the correct value is drift.
    _substitute(
        doc_tree,
        _README,
        "36% (4p1i) and 24% (9p2i)",
        "36% (4p1i) and 24% (9p2i) (an earlier draft misquoted 25% (9p2i))",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "win-rate claim '25% (9p2i)' disagrees" in errors[0]
    assert "12/50 = 24%" in errors[0]


def test_long_ladder_tip_sentence_detected(doc_tree: Path) -> None:
    # The scan covers the WHOLE sentence: a baseline mention more than 120
    # characters from the "ladder tip" phrase (the pre-hardening window cap)
    # is still the same claim.
    filler = "and the qualifying clauses go on " * 6
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
    assert "baseline 7" in errors[0]


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
    # Both the win-rate check and the vote-correctness provenance check read
    # this manifest, so both lose their source and both must say so.
    _write(doc_tree, _MANIFEST_4P1I, "# Sample Replay Manifest\n\nno table here.\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert all("parsed zero table rows" in error for error in errors)
    assert all(_MANIFEST_4P1I in error for error in errors)


def test_vote_correctness_stamp_drift_detected(doc_tree: Path) -> None:
    # The module's per-set stamp is bound to that set's committed report: a
    # numerator drifting away from the recorded one is named on both sides.
    _substitute(doc_tree, _VOTE_CORRECTNESS, "78/85 = 0.9176", "77/85 = 0.9059")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _VOTE_CORRECTNESS in errors[0]
    assert "replays/samples/9p2i" in errors[0]
    assert "77/85 = 0.9059" in errors[0]
    assert "records 78/85 = 0.9176" in errors[0]


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
    assert "replays/samples/9p2i (78/85)" in errors[0]


def test_eval_report_rate_drift_detected(doc_tree: Path) -> None:
    # The rate is never a literal in the checker: it is re-derived from the
    # report's own two counts, so a rate field drifting away from them fails
    # with the set and both values named.
    _substitute(
        doc_tree,
        _EVAL_REPORT_9P2I,
        '"vote_correctness_rate": 0.9176470588235294',
        '"vote_correctness_rate": 0.99',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    # Twice over: the stamp check catches the rate contradicting its own
    # counts, and the README's real-report example no longer matches the
    # report it points a reader at.
    assert len(errors) == 2
    assert any(
        _EVAL_REPORT_9P2I in error and "78/85 = 0.9176" in error for error in errors
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
    # when its model and prompt token still match.
    _substitute(doc_tree, _ML_CORPUS_MANIFEST_9P2I, "absence_prior, ", "")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "disagree on the substrate flags" in errors[0]
    assert "absence_prior" in errors[0]


def test_vote_correctness_baseline_attribution_drift_detected(doc_tree: Path) -> None:
    # The baseline the stamps are attributed to has a committed source too: a
    # rate hung on the wrong baseline is a wrong claim even when its
    # arithmetic checks out.
    _substitute(doc_tree, _VOTE_CORRECTNESS, "baseline-7", "baseline-5")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _VOTE_CORRECTNESS in errors[0]
    assert "'baseline-7'" in errors[0]


def test_zero_impostor_ejection_set_wants_an_undefined_rate_stamp(
    doc_tree: Path,
) -> None:
    # A set that ejected no impostor has an UNDEFINED rate, not a zero one.
    # The checker must accept the recording and demand the "n/a" stamp rather
    # than reject the set outright — a re-record could legitimately produce it.
    _substitute(
        doc_tree,
        _EVAL_REPORT_4P1I,
        '"impostor_ejections": 20,\n    "crewmate_ejections": 1,\n'
        '    "evidence_backed_impostor_ejections": 19,\n'
        '    "vote_correctness_rate": 0.95,',
        '"impostor_ejections": 0,\n    "crewmate_ejections": 1,\n'
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
        '"evidence_backed_impostor_ejections": 78,',
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
    # real-report example sourceless.
    _write(doc_tree, _EVAL_REPORT_9P2I, "{}\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert all(
        _EVAL_REPORT_9P2I in error and '"vote_correctness":' in error
        for error in errors
    )


def test_unlinked_dialect_term_detected(doc_tree: Path) -> None:
    # The one private-dialect term the front door keeps loses its glossary
    # link at its FIRST use — the results table's before-column header — so a
    # reader meets "baseline" with nowhere to look it up.
    _substitute(doc_tree, _README, _BEFORE_COLUMN_LINK, "At baseline 6")
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
    _write(
        doc_tree, _README, text.replace(row, f"{stale} an earlier count |\n{row}", 1)
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 3
    assert (
        "states 'Committed sample replays that reconstruct byte-identically' twice"
        in (errors[0])
    )
    assert "'99 of 100'" in errors[1]
    # The stale copy carries a stale before cell with it, and that is compared
    # too: the page would otherwise answer the history question twice as well.
    assert "'an earlier count'" in errors[2]


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
    assert len(errors) == 1
    assert "'96 of 96'" in errors[0]
    assert "100 committed replays" in errors[0]


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
        "| 538 / 538, zero dangling |",
        "| 537 / 537, zero dangling |",
    )
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| 538 / 538, zero dangling |",
        "| 537 / 537, zero dangling |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'537 / 537, zero dangling'" in errors[0]
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
    assert "'538 / 538, 3 dangling'" in errors[0]


def test_vent_headline_derived_from_the_crosstab(doc_tree: Path) -> None:
    # The headline is arithmetic over the cross-tab under it, so the two cannot
    # drift: 69 of 69 + 16 correct ejections rode a vent flag.
    _substitute(
        doc_tree, _READING_GUIDE, _FLAGGED_ROW, "| yes (69 meetings) | 60 | 0 |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'69 / 85 = 81%'" in errors[0]
    assert "'60 / 76 = 79%'" in errors[0]
    # ...and the drifted cell is no longer the one the instrument pins.
    assert "cross-tab's 'yes' row reads 60 impostor / 0 innocent" in errors[1]


def test_non_replay_jsonl_is_not_counted(doc_tree: Path) -> None:
    # The recorder writes a `<stem>.audit.jsonl` sidecar beside a replay, and
    # verify_samples.sh reconstructs only canonical replay-seed-N.jsonl files.
    # Counting a sidecar would inflate a figure claiming N of N were verified.
    (doc_tree / "replays" / "samples" / "9p2i" / "scratch.audit.jsonl").touch()
    assert check_doc_facts.check_facts(doc_tree) == []


def test_vent_crosstab_read_by_label_not_position(doc_tree: Path) -> None:
    # Reading the rows by position would derive 16 / 85 from a reordered
    # table that says those sixteen ejections had NO vent flag. Keyed on the
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
    # headline, and is caught: 16 of 85 correct ejections would then be
    # the vent-backed ones.
    text = _read(doc_tree, _READING_GUIDE)
    assert _FLAGGED_ROW + "\n" + _UNFLAGGED_ROW in text
    swapped = "| no (69 meetings) | 69 | 0 |\n| yes (83 meetings) | 16 | 14 |"
    _write(
        doc_tree,
        _READING_GUIDE,
        text.replace(_FLAGGED_ROW + "\n" + _UNFLAGGED_ROW, swapped),
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "'69 / 85 = 81%'" in error and "'16 / 85 = 19%'" in error for error in errors
    )
    # The pins name the same swap in their own terms: the flagged row is the
    # one the instrument recorded 69/0 for, whichever way round it is written.
    assert any(
        "cross-tab's 'yes' row reads 16 impostor / 14 innocent" in e for e in errors
    )


def test_mislabelled_vent_crosstab_row_fails_loud(doc_tree: Path) -> None:
    # A row whose label is neither yes nor no leaves the two populations
    # unidentifiable, which must fail rather than derive something.
    _substitute(
        doc_tree, _READING_GUIDE, "| yes (69 meetings) |", "| flagged (69 meetings) |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no vent cross-tab" in errors[0]


def test_proof_partition_derived_from_the_close_audit(doc_tree: Path) -> None:
    # The before column is the column sum of the previous recording's own
    # partition table, so a moved cell there moves the history the front door
    # states rather than being absorbed.
    _substitute(doc_tree, _PROOF_AUDIT, "**68/68 = 1.000**", "**60/68 = 0.882**")
    errors = check_doc_facts.check_facts(doc_tree)
    figure = [error for error in errors if "310 / 310 = 1.0000" in error]
    assert len(figure) == 1
    assert "'302 / 310 = 0.9742 vs 46 / 125 = 0.3680'" in figure[0]
    # The arithmetic cross-check reads the same drift independently: eight of
    # the proof-present cell's ejections would now have convicted an innocent,
    # against a row that still totals zero.
    assert len(errors) == 2
    assert any("proof-present cell reads 302/310" in error for error in errors)


def test_published_partition_derived_from_the_record(doc_tree: Path) -> None:
    # The published figure is the CURRENT record's own pre-registered read, so
    # a moved pooled cell there moves the front door rather than being absorbed.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| **pooled** | **46/125 = 0.3680** [0.2886, 0.4553] "
        "| **61/103 = 0.5922** [0.4957, 0.6822] |",
        "| **pooled** | **46/125 = 0.3680** [0.2886, 0.4553] "
        "| **65/103 = 0.6311** [0.4957, 0.6822] |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("'326 / 326 = 1.0000 vs 65 / 103 = 0.6311'" in error for error in errors)
    # ...and the record's two decided bars now contradict each other.
    assert any("its non-direct accuracy bar reads 65/103" in error for error in errors)


def test_record_innocent_bar_reaches_the_front_door(doc_tree: Path) -> None:
    # The wrongful-ejection count the row publishes is the record's bar-2
    # pooled cell, not a number this page remembers.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| **pooled** | **79** | **42** |",
        "| **pooled** | **79** | **40** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "'40 of 40 innocent ejections sit in the no-proof cell'" in error
        for error in errors
    )
    assert any("its wrongful-ejection bar reads 40" in error for error in errors)


def test_record_direct_proof_cell_reaches_the_front_door(doc_tree: Path) -> None:
    # A record that ever convicted an innocent WITH engine-certified proof
    # falsifies the row's own placement claim, and must fail here rather than
    # leave the front door still saying there were none.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "**326/326 = 1.000** pooled",
        "**325/326 = 0.997** pooled",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("1 proof-present innocent ejection(s)" in error for error in errors)
    assert any("'325 / 326 = 0.9969 vs 61 / 103 = 0.5922'" in error for error in errors)


def test_missing_record_bar_fails_loud(doc_tree: Path) -> None:
    # Losing the bar's pooled row must not read as "nothing to derive from".
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "### Bar 1 — I-1 non-direct conviction accuracy",
        "### The first bar — I-1 non-direct conviction accuracy",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _LADDER_TIP_AUDIT in errors[0]
    assert "conviction-partition cells cannot be located" in errors[0]


def test_proof_partition_read_by_label_not_position(doc_tree: Path) -> None:
    # Reading the rows by order would invert the claim on a reordered table.
    # Keyed on the labels, reordering changes nothing...
    text = _read(doc_tree, _PROOF_AUDIT)
    assert _PROOF_ROW + _NON_PROOF_ROW in text
    _write(
        doc_tree,
        _PROOF_AUDIT,
        text.replace(_PROOF_ROW + _NON_PROOF_ROW, _NON_PROOF_ROW + _PROOF_ROW),
    )
    assert check_doc_facts.check_facts(doc_tree) == []


def test_swapped_proof_partition_labels_detected(doc_tree: Path) -> None:
    # ...while swapping which cell is the proof cell inverts the finding, and
    # is caught: convictions would then be near-chance WITH proof.
    text = _read(doc_tree, _PROOF_AUDIT)
    assert _PROOF_ROW in text and _NON_PROOF_ROW in text
    swapped = _PROOF_ROW.replace(
        "**direct-proof accuracy**", "**non-direct accuracy**"
    ) + _NON_PROOF_ROW.replace("**non-direct accuracy**", "**direct-proof accuracy**")
    _write(doc_tree, _PROOF_AUDIT, text.replace(_PROOF_ROW + _NON_PROOF_ROW, swapped))
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("'46 / 125 = 0.3680 vs 310 / 310 = 1.0000'" in error for error in errors)
    # And both injustice identities break with them, because the swap moves the
    # 79 wrongful convictions into the cell that had none.
    assert len(errors) == 3


def test_proof_present_innocent_ejection_contradicts_the_close_audit(
    doc_tree: Path,
) -> None:
    # The previous recording's own table must stay internally consistent: it
    # recorded a perfect 310/310, so a proof-present innocent ejection in it
    # contradicts its own accuracy cell.
    _substitute(
        doc_tree,
        _PROOF_AUDIT,
        _PROOF_INNOCENT_ROW,
        "| proof-present innocent ejections | **1** | **0** | **0** | **0** |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "proof-present cell reads 310/310" in errors[0]


def test_innocent_ejection_total_drift_detected(doc_tree: Path) -> None:
    # The before column's own arithmetic: 46/125 fixes 79 wrongful ejections.
    _substitute(
        doc_tree,
        _PROOF_AUDIT,
        _INNOCENT_ROW,
        "| innocent ejections (all in the non-direct cell) | 25 | 54 | 2 | 0 |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no-proof cell reads 46/125" in errors[0]
    assert "totals 81" in errors[0]


def test_missing_proof_partition_table_fails_loud(doc_tree: Path) -> None:
    # Losing the table must not read as "nothing to derive from".
    _substitute(
        doc_tree,
        _PROOF_AUDIT,
        "| cell | samples 9p2i |",
        "| population | samples 9p2i |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _PROOF_AUDIT in errors[0]
    assert "conviction-partition cells cannot be located" in errors[0]


def test_renamed_proof_partition_row_fails_loud(doc_tree: Path) -> None:
    # A row this derivation cannot identify must fail rather than pool a
    # half-sum out of the rows it does recognize.
    _substitute(
        doc_tree, _PROOF_AUDIT, "| **direct-proof accuracy** |", "| **proof cell** |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _PROOF_AUDIT in errors[0]
    assert "conviction-partition cells cannot be located" in errors[0]


def test_innocent_ejections_moved_to_the_wrong_cell_detected(doc_tree: Path) -> None:
    # The count alone is not the claim. A row stating the same 42 of 42 but
    # putting them in the proof-present cell states the opposite finding, so
    # matching the number without the placement would gate shape, not meaning.
    _substitute(
        doc_tree,
        _README,
        "42 of 42 innocent ejections sit in the no-proof cell",
        "42 of 42 innocent ejections sit in the proof-present cell",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'42 of 42 innocent ejections sit in the no-proof cell'" in errors[0]


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
    # record's own 61/103 fixes 42. Moving the wrongful-ejection bar while
    # updating the README to match must still fail: the record would then be
    # internally contradictory under one date.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| **pooled** | **79** | **42** |",
        "| **pooled** | **79** | **41** |",
    )
    _substitute(
        doc_tree,
        _README,
        "42 of 42 innocent ejections sit in the no-proof cell",
        "41 of 41 innocent ejections sit in the no-proof cell",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "its non-direct accuracy bar reads 61/103" in errors[0]
    assert "wrongful-ejection bar reads 41" in errors[0]


def test_missing_ml_results_table_fails_loud(doc_tree: Path) -> None:
    # Losing the table must not read as "nothing to derive from".
    _substitute(doc_tree, _ML_PAGE, "| policy | impostor win |", "| model | win |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no results table" in errors[0]


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
        "| 36% (4p1i), 24% (9p2i) |",
        "| 34% (4p1i), 30% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 3
    stale = [error for error in errors if error.startswith(_READING_GUIDE)]
    assert len(stale) == 2
    assert any("claim '34% (4p1i)' disagrees" in error for error in stale)
    assert any("claim '30% (9p2i)' disagrees" in error for error in stale)
    # ...and the figure no longer equals the README's, which is the same drift
    # read from the other side.
    assert any("records '34% (4p1i), 30% (9p2i)'" in error for error in errors)


def test_stale_ml_page_win_rate_detected(doc_tree: Path) -> None:
    # The ML page dates and rates the recording its comparator now sits
    # against, so it is scanned with the rest of the front door.
    _substitute(
        doc_tree, _ML_PAGE, "36% (4p1i) and 24% (9p2i)", "30% (4p1i) and 24% (9p2i)"
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
        "reference recording 7, 2026-08-25 — [instrument]",
        "reference recording 7, 2026-07-20 — [instrument]",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "'reference recording 7, 2026-07-20'" in errors[0]
    assert "'2026-08-25'" in errors[0]


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
        "| 538 / 538, zero dangling | 520 / 520, zero dangling |",
        "| 538 / 538, zero dangling |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "'At baseline 6' cell of results row" in error
        and "reads 'reference recording 7, 2026-08-25" in error
        for error in errors
    )


def test_dropped_before_column_fails_loud(doc_tree: Path) -> None:
    # Losing the column entirely must fail rather than quietly stop checking
    # every history cell on the page.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| What | Figure | At baseline 6 |",
        "| What | Figure |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        f"{_READING_GUIDE}: its results table has no 'At baseline 6' column" in error
        for error in errors
    )


def test_before_column_drift_between_the_two_tables_detected(doc_tree: Path) -> None:
    # The history half is stated once too, so the two tables are compared on it
    # exactly as they are on the figure.
    _substitute(
        doc_tree,
        _READING_GUIDE,
        "| 538 / 538, zero dangling | 520 / 520, zero dangling |",
        "| 538 / 538, zero dangling | 512 / 512, zero dangling |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'520 / 520, zero dangling'" in errors[0]
    assert "'512 / 512, zero dangling'" in errors[0]


def test_before_column_win_rate_held_to_the_record(doc_tree: Path) -> None:
    # A history cell is checked, not skipped: the record's own win-split table
    # says what the previous recording read, so a made-up before value fails.
    _substitute(
        doc_tree,
        _README,
        "| 36% (4p1i), 24% (9p2i) | 34% (4p1i), 30% (9p2i) |",
        "| 36% (4p1i), 24% (9p2i) | 12% (4p1i), 30% (9p2i) |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any(
        "win-rate claim '12% (4p1i)' in the before column disagrees with "
        f"{_LADDER_TIP_AUDIT}'s win-split table (17/50 = 34%)" in error
        for error in errors
    )


def test_missing_win_split_table_fails_loud(doc_tree: Path) -> None:
    # Losing the record's win-split table must not read as "no history to
    # check": every before-column rate would then pass unexamined.
    _substitute(
        doc_tree,
        _LADDER_TIP_AUDIT,
        "| set | baseline-6 impostor rate |",
        "| leg | baseline-6 impostor rate |",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no win-split table" in errors[0]


# --------------------------------------------------------------------------- #
# The reading guide's narrative, and the games it names.                       #
# --------------------------------------------------------------------------- #


def test_stale_guide_ballot_prose_detected(doc_tree: Path) -> None:
    # The exact drift the last recording left behind: the table moved to
    # 538 / 538 and the paragraph under it kept saying 520.
    _substitute(doc_tree, _READING_GUIDE, "all 538 eject", "all 520 eject")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(_READING_GUIDE)
    assert "'all 520 eject ballots'" in errors[0]
    assert _CITATION_INSTRUMENT in errors[0]


def test_stale_guide_crosstab_prose_detected(doc_tree: Path) -> None:
    # ...and the same class one paragraph down: the cross-tab re-quoted, the
    # sentence introducing it left at the previous recording's total.
    _substitute(doc_tree, _READING_GUIDE, "all 152\ncommitted", "all 165\ncommitted")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'all 165 committed 9p2i meetings'" in errors[0]
    assert _DEDUCTION_INSTRUMENT in errors[0]


def test_deleted_guide_narrative_fails_loud(doc_tree: Path) -> None:
    # A paragraph that quietly loses its figure must fail rather than leave
    # the pin bound to nothing.
    _substitute(
        doc_tree, _READING_GUIDE, "all 538 eject\nballots", "every eject ballot"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "no longer narrated anywhere" in errors[0]


def test_guide_crosstab_row_label_held_to_the_pins(doc_tree: Path) -> None:
    # The row labels carry the meeting counts, and those are pinned too: a
    # table whose cells are right and whose populations are wrong is still
    # describing a recording that is not this one.
    _substitute(
        doc_tree, _READING_GUIDE, _FLAGGED_ROW, "| yes (70 meetings) | 69 | 0 |"
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "row is labelled 70 meetings" in errors[0]
    assert "pins 69" in errors[0]


def test_unpinned_crosstab_fails_loud(doc_tree: Path) -> None:
    # Losing the instrument's pin must not read as "nothing to check".
    _substitute(
        doc_tree,
        _DEDUCTION_INSTRUMENT,
        "assert cross_tab.meetings_total == 152",
        "assert cross_tab.meeting_count == 152",
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
        "    assert cross_tab.meetings_total == 152",
        "    assert cross_tab.meetings_total == 152\n    assert cross_tab.meetings_total == 151",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert any("pins meetings_total at both 152 and 151" in error for error in errors)


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
    _substitute(doc_tree, _README, "records 99 ejections", "records 97 ejections")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'99 ejections'" in errors[0]
    assert "total_ejections" in errors[0]


def test_report_example_rate_drift_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _README, "vote correctness 0.918", "vote correctness 0.950")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'vote correctness 0.918'" in errors[0]


def test_report_example_accuracy_drift_detected(doc_tree: Path) -> None:
    _substitute(doc_tree, _README, "ejection accuracy 0.859", "ejection accuracy 0.800")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'ejection accuracy 0.859'" in errors[0]


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
        "the newest — the ladder tip — is baseline 7",
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


def test_missing_document_reported(doc_tree: Path) -> None:
    (doc_tree / _ENV_EXAMPLE).unlink()
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert errors[0].startswith(f"{_ENV_EXAMPLE}: unreadable")


def test_main_reports_every_failure_at_once(
    doc_tree: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _substitute(doc_tree, _README, "2026-08-25", "2026-08-19")
    _substitute(doc_tree, _README, "36% (4p1i)", "30% (4p1i)")
    assert check_doc_facts.main(["--repo-root", str(doc_tree)]) == 1
    err = capsys.readouterr().err
    assert "Doc-fact check failed:" in err
    assert "'36% (4p1i)'" in err
    assert "'2026-08-25'" in err


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
