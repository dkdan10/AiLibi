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
)

# The front-door checks also ENUMERATE paths whose contents they never open:
# the phase contracts, the audit corpus, and every relative link target. The
# fixture stands those up as empty files (directories as directories) so the
# tmp tree answers the same questions the checkout does, without copying the
# ~5 MB of prose behind them into every test.
_ENUMERATED_GLOBS = (("tasks", "phase-*.md"), ("audits", "*.md"))

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
_AUDITS_INDEX = "audits/README.md"
# The one dialect term the front door keeps, and the link that defines it.
_BASELINE_LINK = "[baseline 6](docs/glossary.md#baseline-n-the-reference-recording)"
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
    # (a) The pre-19.1 README claimed the baseline-5-era refresh date.
    _substitute(doc_tree, _README, "2026-07-20", "2026-07-14")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "refresh date '2026-07-20'" in errors[0]
    assert _README in errors[0]


def test_paragraph_date_drift_not_alibied_elsewhere(doc_tree: Path) -> None:
    # The provenance claim is bound to its paragraph: the correct date
    # appearing somewhere else in the file must not satisfy a drifted
    # paragraph (the pre-hardening checker accepted exactly this).
    _substitute(doc_tree, _README, "regenerated 2026-07-20", "regenerated 2026-07-14")
    _write(
        doc_tree,
        _README,
        _read(doc_tree, _README)
        + "\nAn unrelated historical note mentioning 2026-07-20.\n",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'regenerated 2026-07-14'" in errors[0]
    assert "refresh date '2026-07-20'" in errors[0]


def test_duplicate_stale_date_clause_detected(doc_tree: Path) -> None:
    # Every regenerated-date clause in the paragraph must match — a stale
    # duplicate beside the correct clause is drift, same as the win rates.
    _substitute(
        doc_tree,
        _README,
        "regenerated 2026-07-20",
        "regenerated 2026-07-20 (an earlier draft said regenerated 2026-07-14)",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'regenerated 2026-07-14'" in errors[0]
    assert "refresh date '2026-07-20'" in errors[0]


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
        "`qwen3_6_27b` `v3` prompt set",
        "`qwen3_6_27b` `v2` prompt set",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'v3'" in errors[0]
    assert "`prompt_versions` column" in errors[0]


def test_missing_provenance_paragraph_fails_loud(doc_tree: Path) -> None:
    # Losing the paragraph anchor is format drift, not a vacuous pass.
    _substitute(doc_tree, _README, "regenerated 2026-07-20", "refreshed 2026-07-20")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "exactly one sample-provenance paragraph" in errors[0]


def test_wrong_win_rate_detected(doc_tree: Path) -> None:
    # (b) A win rate that no longer matches the manifest it is drawn from:
    # the paragraph misses the expected substring AND carries a claim that
    # contradicts the manifest — both are reported.
    _substitute(doc_tree, _README, "rates 34% (4p1i)", "rates 30% (4p1i)")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'34% (4p1i)'" in errors[0]
    assert "17/50" in errors[0]
    assert "claim '30% (4p1i)' disagrees" in errors[1]


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
    assert "ladder tip at baseline 6" in errors[0]


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
        "34% (4p1i) and 30% (9p2i)",
        "34% (4p1i) and 30% (9p2i) (an earlier draft misquoted 35% (9p2i))",
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "win-rate claim '35% (9p2i)' disagrees" in errors[0]
    assert "15/50 = 30%" in errors[0]


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
    assert "baseline 6" in errors[0]


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


def test_graduated_aside_inside_section_does_not_count(doc_tree: Path) -> None:
    # Tighter still: a mention inside the SECTION but outside the graduated
    # NOTE (a historical aside before the toggle paragraph) must not stand in
    # for the note's graduated/always-ON label either.
    _substitute(doc_tree, _ENV_EXAMPLE, "movement_perception", "")
    _substitute(
        doc_tree,
        _ENV_EXAMPLE,
        "# The ONE live toggle",
        "# Historical aside: movement_perception was once default-OFF.\n\n"
        "# The ONE live toggle",
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
    assert len(errors) == 3
    assert "'32% (4p1i)'" in errors[0]
    assert "16/50" in errors[0]
    assert all("claim '34% (4p1i)' disagrees" in error for error in errors[1:])


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
    _substitute(doc_tree, _VOTE_CORRECTNESS, "72/78 = 0.9231", "71/78 = 0.9103")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _VOTE_CORRECTNESS in errors[0]
    assert "replays/samples/9p2i" in errors[0]
    assert "71/78 = 0.9103" in errors[0]
    assert "records 72/78 = 0.9231" in errors[0]


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
    assert "replays/samples/9p2i (72/78)" in errors[0]


def test_eval_report_rate_drift_detected(doc_tree: Path) -> None:
    # The rate is never a literal in the checker: it is re-derived from the
    # report's own two counts, so a rate field drifting away from them fails
    # with the set and both values named.
    _substitute(
        doc_tree,
        _EVAL_REPORT_9P2I,
        '"vote_correctness_rate": 0.9230769230769231',
        '"vote_correctness_rate": 0.99',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _EVAL_REPORT_9P2I in errors[0]
    assert "0.99" in errors[0]
    assert "72/78 = 0.9231" in errors[0]


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
    _substitute(doc_tree, _VOTE_CORRECTNESS, "baseline-6", "baseline-5")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _VOTE_CORRECTNESS in errors[0]
    assert "'baseline-6'" in errors[0]


def test_zero_impostor_ejection_set_wants_an_undefined_rate_stamp(
    doc_tree: Path,
) -> None:
    # A set that ejected no impostor has an UNDEFINED rate, not a zero one.
    # The checker must accept the recording and demand the "n/a" stamp rather
    # than reject the set outright — a re-record could legitimately produce it.
    _substitute(
        doc_tree,
        _EVAL_REPORT_4P1I,
        '"impostor_ejections": 10,\n    "crewmate_ejections": 2,\n'
        '    "evidence_backed_impostor_ejections": 10,\n'
        '    "vote_correctness_rate": 1.0,',
        '"impostor_ejections": 0,\n    "crewmate_ejections": 2,\n'
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
        '"evidence_backed_impostor_ejections": 72,',
        '"evidence_backed_impostor_ejections": 79,',
    )
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _EVAL_REPORT_9P2I in errors[0]
    assert "no larger than impostor_ejections" in errors[0]


def test_eval_report_without_vote_correctness_block_fails_loud(
    doc_tree: Path,
) -> None:
    # Format drift must not read as "nothing to check": a report with no
    # vote_correctness block leaves the stamps sourceless.
    _write(doc_tree, _EVAL_REPORT_9P2I, "{}\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert _EVAL_REPORT_9P2I in errors[0]
    assert '"vote_correctness":' in errors[0]


def test_unlinked_dialect_term_detected(doc_tree: Path) -> None:
    # The one private-dialect term the front door keeps loses its glossary
    # link: a reader now meets "baseline 6" with nowhere to look it up.
    _substitute(doc_tree, _README, _BASELINE_LINK, "baseline 6")
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
    # Every other error is the same deletion seen through the link check: the
    # four front-door documents that pointed at the record now point at nothing.
    assert all(
        "indexes audit-phase-19-close.md" in error or "does not exist" in error
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
    # guide is two answers to the same question.
    _substitute(doc_tree, _README, "| 100 of 100 |", "| 99 of 100 |")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "'99 of 100'" in errors[0]
    assert "'100 of 100'" in errors[0]


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
    kept = [
        line
        for line in text.splitlines()
        if not (line.startswith("| Impostor win rate") or line.startswith("| Eject "))
    ]
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
        doc_tree, _README, "counted as of 2026-08-19", "counted as of 2026-13-45"
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
    _substitute(doc_tree, _README, "2026-07-20", "2026-07-14")
    _substitute(doc_tree, _README, "34% (4p1i)", "30% (4p1i)")
    assert check_doc_facts.main(["--repo-root", str(doc_tree)]) == 1
    err = capsys.readouterr().err
    assert "Doc-fact check failed:" in err
    assert "'34% (4p1i)'" in err
    assert "'2026-07-20'" in err


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
