"""Unit tests for scripts/check_doc_facts.py (Task 19.1).

The checker's contract is two-sided: it must pass on the committed front door
(so it can sit in a gate) and it must fail, naming the drifted fact, on every
drift class the 19.1 sweep cleaned. The fixture copies the five files the
checker reads into a tmp tree, and one test per perturbation asserts both the
failure and that the message names the right fact — a checker that fails for
the wrong reason is as useless as one that passes.

The substrate-lever registry is never copied: ``check_doc_facts`` always reads
it from the live ``orchestrator.replay`` import, so a perturbed .env.example is
checked against the levers this build actually ships.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import check_doc_facts

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "check_doc_facts.py"

# Exactly the files the checker reads. Copied preserving relative layout so the
# tmp tree is a faithful (and perturbable) stand-in for a checkout.
_COPIED = (
    "README.md",
    ".env.example",
    "replays/samples/4p1i/MANIFEST.md",
    "replays/samples/9p2i/MANIFEST.md",
    "audits/audit-phase-18-close.md",
)

_README = "README.md"
_ENV_EXAMPLE = ".env.example"
_MANIFEST_4P1I = "replays/samples/4p1i/MANIFEST.md"
_TOGGLE_EXAMPLE_LINE = "# AILIBI_IMPOSTOR_ROLL_CALL=0"


@pytest.fixture
def doc_tree(tmp_path: Path) -> Path:
    """A tmp checkout holding only the documents the checker reads."""

    for relative in _COPIED:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((_REPO_ROOT / relative).read_bytes())
    return tmp_path


def _read(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _write(root: Path, relative: str, text: str) -> None:
    (root / relative).write_text(text, encoding="utf-8")


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
    _substitute(doc_tree, _README, "34% (4p1i)", "30% (4p1i)")
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
        _read(doc_tree, _README) + "\nThe baseline-5 sets remain the ladder tip.\n",
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
        + f"\nThe baseline-5 sets, {filler}remain the ladder tip.\n",
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
        _read(doc_tree, _README) + "\nThese sets remain the ladder tip.\n",
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
    # AND its now-stale 34% claim contradicts the manifest.
    text = _read(doc_tree, _MANIFEST_4P1I)
    assert "| IMPOSTORS |" in text
    _write(doc_tree, _MANIFEST_4P1I, text.replace("| IMPOSTORS |", "| CREWMATES |", 1))
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 2
    assert "'32% (4p1i)'" in errors[0]
    assert "16/50" in errors[0]
    assert "claim '34% (4p1i)' disagrees" in errors[1]


def test_unparseable_manifest_fails_loud(doc_tree: Path) -> None:
    # Format drift must not read as "no impostor wins recorded": a manifest
    # with no parseable rows is a hard failure, not a vacuous pass.
    _write(doc_tree, _MANIFEST_4P1I, "# Sample Replay Manifest\n\nno table here.\n")
    errors = check_doc_facts.check_facts(doc_tree)
    assert len(errors) == 1
    assert "parsed zero table rows" in errors[0]
    assert _MANIFEST_4P1I in errors[0]


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
