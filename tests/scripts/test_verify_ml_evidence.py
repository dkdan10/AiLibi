"""Tests for scripts/verify_ml_evidence.py (Task 19.23).

Drives the legs and ``main`` directly (no subprocess). Three families:

* **the real tree** — the cheap legs run against this checkout and must be green
  at HEAD, with the evidence-branch classes reported as their own class rather
  than skipped, whether or not ``scripts/fetch_evidence.sh`` has run here (both
  states are asserted explicitly: all-restored or none-restored, never a silent
  middle);
* **perturbed inputs** — a flipped artifact byte, a drifted evidence-manifest
  digest, a drifted report cell and a corrupted replay each turn a leg red, so
  the "PASS" this command prints is a measurement and not a formality;
* **the modes** — ``--complete`` fails on absent promised bytes while accepting a
  manifest-recorded LOST class, and the argument combinations that cannot mean
  what they say are refused.

Every perturbation is built in ``tmp_path`` out of symlinks to the committed
bytes plus the one file under test, so nothing in the repository is written —
which is also what the read-only test asserts.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from collections.abc import Sequence
from pathlib import Path

import pytest

import verify_ml_evidence as vme

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLE_SET = "replays/samples/4p1i"

#: The minimum §3 section a synthetic EVIDENCE-MANIFEST needs: the sidecar leg
#: reads the retained-path enumeration from it, so a scratch manifest carries an
#: empty-but-well-formed one rather than none.
_RETAINED_SECTION_STUB = (
    "## 3. What stayed in-tree — the consumer enumeration\n\n"
    "| retained path | retained because |\n"
    "|---|---|\n"
    "| `PATHS.md` | **rule** |\n\n"
)


# --------------------------------------------------------------------------- #
# scratch-tree helpers                                                          #
# --------------------------------------------------------------------------- #


def _link(root: Path, *rels: str) -> None:
    """Symlink committed repo paths into a scratch root (nothing is copied)."""

    for rel in rels:
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(_REPO_ROOT / rel)


def _copy(root: Path, rel: str) -> Path:
    """Copy one committed path into a scratch root so a test may perturb it."""

    dest = root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    source = _REPO_ROOT / rel
    if source.is_dir():
        shutil.copytree(source, dest)
    else:
        shutil.copy2(source, dest)
    return dest


def _manifests(root: Path) -> None:
    """The two evidence manifests every :class:`Context` is built from."""

    _link(root, vme.EVIDENCE_MANIFEST, vme.SLATE_MANIFEST)


def _context(root: Path, *, fast: bool = False, complete: bool = False) -> vme.Context:
    return vme.Context(
        repo_root=root,
        fast=fast,
        complete=complete,
        evidence=vme.evidence_rows(root),
        pinned_sha=vme.read_pinned_sha(root),
        slate_ruling=(
            vme.read_slate_ruling(root)
            if (root / vme.ARTIFACTS_DOC).is_file()
            else None
        ),
    )


def _row(rows: Sequence[vme.CheckRow], name: str) -> vme.CheckRow:
    matches = [row for row in rows if row.name == name]
    assert len(matches) == 1, f"expected exactly one {name!r} row, got {len(matches)}"
    return matches[0]


def _tree_snapshot(root: Path) -> dict[str, tuple[bool, str]]:
    """(is-symlink, content digest or link target) for every entry under ``root``."""

    snapshot: dict[str, tuple[bool, str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(dirnames)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            rel = str(path.relative_to(root))
            if path.is_symlink():
                snapshot[rel] = (True, os.readlink(path))
            else:
                snapshot[rel] = (
                    False,
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                )
    return snapshot


# --------------------------------------------------------------------------- #
# 1. the real tree — green at HEAD                                             #
# --------------------------------------------------------------------------- #


def test_sidecar_leg_verifies_every_in_tree_sidecar() -> None:
    """The in-tree sidecar class verifies fully offline on a bare checkout."""

    result = vme.run_sidecars(_context(_REPO_ROOT))
    in_tree = _row(result.rows, "sidecars[IN-TREE]")
    assert in_tree.status == "OK", in_tree.detail
    assert "0 failure(s)" in in_tree.measured
    # Every sidecar the walk finds is verified, and there is more than a token
    # of them — a walk that silently found none would also read "0 failure(s)".
    assert vme.walk_sidecars(_REPO_ROOT)


@pytest.mark.parametrize(
    "name", ["sidecars[EVIDENCE-BRANCH]", "evidence payload", "evidence branch README"]
)
def test_evidence_branch_classes_are_reported_never_skipped(name: str) -> None:
    """The moved bytes are their OWN class, in both of its two valid states.

    A checkout without ``scripts/fetch_evidence.sh`` reports ABSENT with the
    count quoted; a checkout with it reports OK having hashed them. Anything
    else — a partial restore, a digest drift — is a failure. There is no third,
    quiet outcome, which is the property Task 19.22's manifest asks for by name
    (``EVIDENCE-MANIFEST.md`` §5).
    """

    row = _row(vme.run_sidecars(_context(_REPO_ROOT)).rows, name)
    assert row.status in {"OK", "ABSENT"}, row.detail
    if row.status == "ABSENT":
        assert "fetch_evidence.sh" in row.detail


def test_paired_leg_reproduces_the_committed_erratum() -> None:
    """Every arm's paired statistics reproduce the 19.20 erratum table."""

    result = vme.run_paired(_context(_REPO_ROOT))
    assert [row.status for row in result.rows if row.status != "INFO"] == ["OK"] * 4
    assert {row.name for row in result.rows} >= {
        f"paired McNemar + Wilson: {entrant}"
        for entrant in vme.erratum_paired_rows(_REPO_ROOT)
    }


def test_availability_registry_covers_the_document() -> None:
    """Every `docs/artifacts.md` registry row is probed and classed."""

    result = vme.run_availability(_context(_REPO_ROOT))
    coverage = _row(result.rows, "registry coverage")
    assert coverage.status == "OK", coverage.detail
    slate = _row(result.rows, "Phase-18 finalist raw slate (Task 19.21 outcome)")
    assert slate.status in {"OK", "ABSENT", "INFO"}, slate.detail
    assert slate.committed.startswith("Ruling ")
    # The two off-tree classes the registry table holds no row for are reported
    # rather than omitted, each against the line that records them.
    assert [row.status for row in result.rows if "REPO-EXTERNAL" in row.committed] == [
        "INFO"
    ] * len(vme._OFF_TREE_ANCHORS)


def test_recompute_reproduces_every_committed_verdict() -> None:
    """The three instruments re-derive from the FROZEN weights, to the pin.

    The slow leg (~30s: two corpus tables plus the composed fidelity). It is the
    command's whole point — the Codex audit's executed-evidence row, run as one
    check — so it is asserted end to end rather than sampled.
    """

    result = vme.run_recompute(_context(_REPO_ROOT))
    failed = [row for row in result.rows if row.status != "OK"]
    assert not failed, "\n".join(f"{row.name}: {row.detail}" for row in failed)
    # The six figures the audit's executed-evidence table names, by name.
    assert {row.name for row in result.rows} >= {
        "surrogate top-1 (ranking channel)",
        "surrogate SKIP-vs-eject decision accuracy",
        "conviction flag-count Spearman",
        "conviction conversion-label accuracy",
        "composed decision accuracy",
        "composed exact-outcome match",
    }
    assert _row(result.rows, "surrogate top-1 (ranking channel)").measured.startswith(
        "0.7666666"
    )
    assert _row(
        result.rows, "surrogate SKIP-vs-eject decision accuracy"
    ).measured.startswith("0.3750000")
    assert _row(
        result.rows, "conviction conversion-label accuracy"
    ).measured.startswith("0.9375000")
    assert _row(result.rows, "composed decision accuracy").measured.startswith(
        "0.8645833"
    )
    assert _row(result.rows, "composed exact-outcome match").measured.startswith(
        "0.7916666"
    )


def test_main_runs_the_cheap_legs_green_at_head(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI plumbing: three legs, one exit code, the modes disclosed."""

    assert (
        vme.main(["--only", "sidecars", "--only", "paired", "--only", "availability"])
        == 0
    )
    out = capsys.readouterr().out
    assert "PARTIAL RUN — only: sidecars, paired, availability" in out
    assert "read-only and offline" in out
    assert "verify-ml-evidence: every check passed." in out


# --------------------------------------------------------------------------- #
# 2. perturbed inputs — the command fails loud                                  #
# --------------------------------------------------------------------------- #


def test_perturbed_artifact_byte_fails_the_in_tree_sidecar_class(
    tmp_path: Path,
) -> None:
    """One flipped byte under a committed sidecar turns the sidecar leg red."""

    root = tmp_path / "repo"
    _manifests(root)
    weights = _copy(root, "training/artifacts/surrogate/ballot-predictor.json")
    _copy(root, "training/artifacts/surrogate/ballot-predictor.json.sha256")

    clean = vme.run_sidecars(_context(root))
    assert _row(clean.rows, "sidecars[IN-TREE]").status == "OK"

    payload = json.loads(weights.read_text())
    payload["__perturbed__"] = True
    weights.write_text(json.dumps(payload))

    perturbed = _row(vme.run_sidecars(_context(root)).rows, "sidecars[IN-TREE]")
    assert perturbed.status == "FAIL"
    assert "ballot-predictor.json" in perturbed.detail
    assert "!= sidecar" in perturbed.detail


def test_absent_sidecar_target_fails_rather_than_passing_vacuously(
    tmp_path: Path,
) -> None:
    """A sidecar whose target is gone is a failure, not a sidecar with no work."""

    root = tmp_path / "repo"
    _manifests(root)
    weights = _copy(root, "training/artifacts/surrogate/ballot-predictor.json")
    _copy(root, "training/artifacts/surrogate/ballot-predictor.json.sha256")
    weights.unlink()

    row = _row(vme.run_sidecars(_context(root)).rows, "sidecars[IN-TREE]")
    assert row.status == "FAIL"
    assert "absent" in row.detail


def test_drifted_evidence_manifest_digest_fails_the_payload_check(
    tmp_path: Path,
) -> None:
    """A restored byte that does not match the manifest fails, restored or not.

    Built rather than fetched: the scratch manifest names ONE file, which is
    present in the scratch tree with the wrong digest — exactly the state a
    corrupted or edited restore would leave, without needing 399 MiB of it.
    """

    root = tmp_path / "repo"
    (root / vme.COEVO_DEST).mkdir(parents=True)
    (root / vme.COEVO_DEST / "moved.json").write_text("{}\n")
    (root / vme.EVIDENCE_MANIFEST).write_text(
        "| **tip sha — THE PIN** | **" + "a" * 40 + "** |\n"
        f"{_RETAINED_SECTION_STUB}"
        "```sha256\n"
        f"{'0' * 64}  coevo/moved.json\n"
        f"{'1' * 64}  README.md\n"
        "```\n"
    )
    (root / vme.COEVO_DEST / "PATHS.md").write_text("stub\n")
    (root / vme.SLATE_DEST).mkdir(parents=True)
    (root / vme.SLATE_MANIFEST).write_text(
        f"```sha256\n{'2' * 64}  ./absent.jsonl\n```\n"
    )

    rows = vme.run_sidecars(_context(root)).rows
    payload = _row(rows, "evidence payload")
    assert payload.status == "FAIL"
    assert "moved.json" in payload.detail
    # The slate row is absent, not drifted: a PARTIAL restore is itself a
    # failure, because "some of the promised bytes" is not a class.
    assert "1 of 2 restored" in payload.measured


def test_drifted_report_cell_fails_the_paired_leg(tmp_path: Path) -> None:
    """A report edit that drifts a committed statistic turns the paired leg red."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, vme.FINALIST_RESULTS)
    report = _copy(root, vme.FINALIST_REPORT)
    report.write_text(
        report.read_text().replace(
            "| `p18-imp-6d327dcb` | 50 | 19 / 13 | +0.12 | 15/9 |",
            "| `p18-imp-6d327dcb` | 50 | 19 / 13 | +0.12 | 14/10 |",
        )
    )

    row = _row(
        vme.run_paired(_context(root)).rows,
        "paired McNemar + Wilson: p18-imp-6d327dcb",
    )
    assert row.status == "FAIL"
    assert "discordant 15/9 != 14/10" in row.detail


def test_perturbed_replay_fails_the_corpus_leg(tmp_path: Path) -> None:
    """A single altered state hash fails the reconstruction leg, sampled or not."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, f"{vme.SURROGATE_DIR}/fit-corpus.json", vme.CORPUS_SET)
    perturbed_set = root / "replays/samples/perturbed"
    perturbed_set.mkdir(parents=True)
    _link(root, f"{_SAMPLE_SET}/roster.json")
    (perturbed_set / "roster.json").symlink_to(_REPO_ROOT / _SAMPLE_SET / "roster.json")
    source = (_REPO_ROOT / _SAMPLE_SET / "replay-seed-0.jsonl").read_text()
    first, _, rest = source.partition("\n")
    recorded = json.loads(first)
    recorded["state_hash"] = "0" * 64
    (perturbed_set / "replay-seed-0.jsonl").write_text(
        json.dumps(recorded, separators=(",", ":"), sort_keys=True) + "\n" + rest
    )

    result = vme.run_corpus(_context(root, fast=True))
    row = _row(result.rows, "corpus reconstruction: replays/samples/perturbed")
    assert row.status == "FAIL"
    assert "0/1 reconstructed" in row.measured
    assert "headless-seed-0" in row.detail
    # The unperturbed legs of the same run stay green, so the failure is located
    # rather than merely global.
    assert _row(result.rows, "fit-corpus identity fingerprint").status == "OK"
    assert result.notes and "SAMPLE" in result.notes[0]


def test_perturbed_corpus_fails_the_identity_fingerprint(tmp_path: Path) -> None:
    """A corpus whose bytes moved no longer fingerprints to the committed sha."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, f"{vme.SURROGATE_DIR}/fit-corpus.json")
    (root / "replays/samples").mkdir(parents=True)
    # The corpus is mirrored by symlink, then gains ONE more game: the
    # fingerprint folds every replay's digest, so an added recording moves it
    # without copying 161 MB to prove it.
    corpus = root / vme.CORPUS_SET
    corpus.mkdir(parents=True)
    for child in sorted((_REPO_ROOT / vme.CORPUS_SET).iterdir()):
        (corpus / child.name).symlink_to(child)
    (corpus / "replay-seed-999999.jsonl").symlink_to(
        _REPO_ROOT / vme.CORPUS_SET / "replay-seed-1000.jsonl"
    )

    result = vme.run_corpus(_context(root, fast=True))
    row = _row(result.rows, "fit-corpus identity fingerprint")
    assert row.status == "FAIL"
    assert "no longer fingerprints" in row.detail


def test_registry_row_with_no_probe_fails_the_availability_leg(
    tmp_path: Path,
) -> None:
    """A row added to `docs/artifacts.md` fails rather than going unreported."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, vme.PATHS_DOC, vme.FINALIST_REPORT)
    doc = _copy(root, vme.ARTIFACTS_DOC)
    doc.write_text(
        doc.read_text().replace(
            "| `audits/` ",
            "| `training/artifacts/brand_new/` — a later phase's family | (a) "
            "| in git | 1 file |\n| `audits/` ",
            1,
        )
    )

    row = _row(vme.run_availability(_context(root)).rows, "registry coverage")
    assert row.status == "FAIL"
    assert "training/artifacts/brand_new/" in row.detail


def test_registry_row_with_an_unknown_where_raises(tmp_path: Path) -> None:
    """A new availability phrasing must be taught, never guessed at or skipped."""

    root = tmp_path / "repo"
    doc = _copy(root, vme.ARTIFACTS_DOC)
    doc.write_text(doc.read_text().replace("| in git |", "| on a bucket |", 1))

    with pytest.raises(vme.EvidenceError, match="must be taught a new availability"):
        vme.registry_rows(root)


def test_a_corpus_path_field_is_compared_not_dropped(tmp_path: Path) -> None:
    """A normalized field is RESOLVED and compared — never excluded.

    Excluding it meant a verdict pointing at a different corpus still read "all
    fields identical", which is the opposite of what an identity pin is for
    (Codex review, PR #348).
    """

    same = vme._verdict_identity_row(
        "same corpus, two spellings",
        rederived={"replay_set_dir": str(_REPO_ROOT / vme.CORPUS_SET), "n": 1},
        committed={"replay_set_dir": vme.CORPUS_SET, "n": 1},
        repo_root=_REPO_ROOT,
        path_fields=("replay_set_dir",),
        source="test",
    )
    assert same.status == "OK", same.detail

    different = vme._verdict_identity_row(
        "a different corpus",
        rederived={"replay_set_dir": "replays/ml_corpus/4p1i", "n": 1},
        committed={"replay_set_dir": vme.CORPUS_SET, "n": 1},
        repo_root=_REPO_ROOT,
        path_fields=("replay_set_dir",),
        source="test",
    )
    assert different.status == "FAIL"
    assert "replay_set_dir" in different.detail


def test_malformed_manifest_block_raises_rather_than_shrinking_the_guards(
    tmp_path: Path,
) -> None:
    """A manifest whose digest block will not parse stops the run, loudly."""

    root = tmp_path / "repo"
    (root / vme.EVIDENCE_MANIFEST).parent.mkdir(parents=True)
    (root / vme.EVIDENCE_MANIFEST).write_text("no digest block here\n")
    with pytest.raises(vme.EvidenceError, match="no ```sha256 digest block"):
        vme.evidence_rows(root)


def test_sidecar_row_escaping_its_directory_is_refused(tmp_path: Path) -> None:
    """A sidecar naming a path outside its own directory is refused, not followed."""

    sidecar = tmp_path / "weights.json.sha256"
    sidecar.write_text(f"{'0' * 64}  ../../etc/passwd\n")
    with pytest.raises(vme.EvidenceError, match="escapes the sidecar's directory"):
        vme.sidecar_targets(sidecar)


def test_report_that_disagrees_with_itself_raises(tmp_path: Path) -> None:
    """Two rows stating different fractions for one label is a drifted report."""

    report = tmp_path / "report.md"
    report.write_text(
        "| conversion accuracy | 90/96 = 0.9375 |\n"
        "| conversion accuracy | 91/96 = 0.9479 |\n"
    )
    with pytest.raises(vme.EvidenceError, match="disagrees with itself"):
        vme.fraction_from_report(tmp_path, "report.md", "conversion accuracy")


def test_missing_report_label_raises(tmp_path: Path) -> None:
    """The committed verdict a check compares against cannot silently vanish."""

    report = tmp_path / "report.md"
    report.write_text("| something else | 1/2 |\n")
    with pytest.raises(vme.EvidenceError, match="no table row labelled"):
        vme.fraction_from_report(tmp_path, "report.md", "conversion accuracy")


def test_quoted_table_rows_are_not_second_statements(tmp_path: Path) -> None:
    """A row QUOTED inside an erratum blockquote is a citation, not a claim."""

    report = tmp_path / "report.md"
    report.write_text(
        "| conversion accuracy | 90/96 = 0.9375 |\n"
        "   > `| conversion accuracy | 91/96 = 0.9479 |`\n"
    )
    assert vme.fraction_from_report(tmp_path, "report.md", "conversion accuracy") == (
        90,
        96,
    )


# --------------------------------------------------------------------------- #
# 3. the modes                                                                  #
# --------------------------------------------------------------------------- #


def test_complete_fails_absent_bytes_but_a_default_run_does_not() -> None:
    """ABSENT is the expected state of a fresh clone, and the close's failure."""

    rows = (
        vme.CheckRow("promised", "0 of 9 restored", "9 files", "manifest", "ABSENT"),
        vme.CheckRow("recorded loss", "LOST", "LOST", "manifest", "INFO"),
        vme.CheckRow("measured", "ok", "ok", "manifest", "OK"),
    )
    assert vme._failed(rows, complete=False) == []
    assert [row.name for row in vme._failed(rows, complete=True)] == ["promised"]


def _lost_ruling_tree(tmp_path: Path) -> Path:
    """A scratch tree whose 19.21 ruling records the slate as LOST."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, vme.PATHS_DOC, vme.FINALIST_REPORT)
    doc = _copy(root, vme.ARTIFACTS_DOC)
    doc.write_text(
        doc.read_text().replace(
            "**Ruling 2026-08-15: RECOVERED**", "**Ruling 2026-08-15: LOST**"
        )
    )
    return root


def test_complete_accepts_a_manifest_recorded_loss(tmp_path: Path) -> None:
    """A ratified LOSS is a valid close state; an unrecorded absence is not.

    The 19.21 outcome at HEAD is RECOVERED, so the loss path is exercised by
    rewriting the ruling the registry document owns: the slate then reports LOST
    with no restored bytes, and ``--complete`` does NOT fail on it.
    """

    root = _lost_ruling_tree(tmp_path)
    ctx = _context(root, complete=True)
    assert ctx.lost_prefixes == frozenset({vme._SLATE_PREFIX})

    rows = vme.run_availability(ctx).rows
    slate = _row(rows, "Phase-18 finalist raw slate (Task 19.21 outcome)")
    assert slate.status == "INFO"
    assert slate.measured == "LOST (recorded 2026-08-15)"
    assert slate not in vme._failed(rows, complete=True)
    # The class-(c) registry row for the slate must ALSO stop demanding the
    # bytes; leaving it ABSENT is what deadlocked the close. (The coevo row is
    # still ABSENT here — those bytes ARE promised and this tree has none.)
    registry_row = next(
        row for row in rows if row.name.startswith("finalist-eval-raw/")
    )
    assert registry_row.status == "INFO"
    # NOTHING about the slate fails the close gate. (Other rows in this scratch
    # tree do — it has no artifact families and no restored coevo bytes — so the
    # assertion is scoped to the slate rather than to an empty failure list.)
    failed = {row.name for row in vme._failed(rows, complete=True)}
    assert slate.name not in failed
    assert registry_row.name not in failed


def test_a_recorded_loss_does_not_deadlock_a_restored_payload(
    tmp_path: Path,
) -> None:
    """The whole-payload check excludes recorded-lost bytes, not just the summary.

    The deadlock this pins (Codex review, PR #348): with the coevo payload
    RESTORED and a LOST slate absent, an aggregate that still counted the slate
    read PARTIAL — a `FAIL` that exits `--complete` non-zero on bytes nobody
    promised, before the slate's own INFO row could accept the loss. Here the
    scratch tree restores every coevo byte the manifest names and leaves the
    lost slate absent; nothing in the leg may fail.
    """

    root = tmp_path / "repo"
    coevo_byte = root / vme.COEVO_DEST / "restored.json"
    coevo_byte.parent.mkdir(parents=True)
    coevo_byte.write_text("{}\n")
    (root / vme.COEVO_DEST / "PATHS.md").write_text("stub\n")
    (root / vme.EVIDENCE_MANIFEST).write_text(
        "| **tip sha — THE PIN** | **" + "a" * 40 + "** |\n"
        f"{_RETAINED_SECTION_STUB}"
        "```sha256\n"
        f"{vme.sha256_file(coevo_byte)}  coevo/restored.json\n"
        f"{'1' * 64}  README.md\n"
        "```\n"
    )
    (root / vme.SLATE_DEST).mkdir(parents=True)
    (root / vme.SLATE_MANIFEST).write_text(
        f"```sha256\n{'2' * 64}  ./gone.jsonl\n```\n"
    )
    (root / vme.ARTIFACTS_DOC).parent.mkdir(parents=True, exist_ok=True)
    (root / vme.ARTIFACTS_DOC).write_text("**Ruling 2026-08-15: LOST**\n")

    ctx = _context(root, complete=True)
    assert ctx.lost_prefixes == frozenset({vme._SLATE_PREFIX})
    rows = vme.run_sidecars(ctx).rows

    payload = _row(rows, "evidence payload")
    # 1 promised byte, restored and hashed — the lost slate is not counted.
    assert payload.status == "OK", payload.detail
    assert payload.measured.startswith("1 of 1 restored")
    assert "PROMISED" in payload.committed
    lost_row = _row(rows, "evidence payload[LOST]")
    assert lost_row.status == "INFO"
    assert lost_row.measured.startswith("1 file(s) recorded LOST")
    # Neither row fails the close gate — that is the deadlock this pins.
    failed = vme._failed(rows, complete=True)
    assert payload not in failed
    assert lost_row not in failed


def test_unrecorded_ruling_fails_the_availability_leg(tmp_path: Path) -> None:
    """No ruling at all is the silent state the close forbids."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, vme.PATHS_DOC, vme.FINALIST_REPORT)
    doc = _copy(root, vme.ARTIFACTS_DOC)
    doc.write_text(doc.read_text().replace("**Ruling 2026-08-15: RECOVERED**", "(tbd)"))

    row = _row(
        vme.run_availability(_context(root)).rows,
        "Phase-18 finalist raw slate (Task 19.21 outcome)",
    )
    assert row.status == "FAIL"
    assert row.measured == "NO RULING RECORDED"


def test_off_tree_class_that_lost_its_anchor_fails(tmp_path: Path) -> None:
    """A class this command reports must be one the tree still states."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, vme.ARTIFACTS_DOC, vme.FINALIST_REPORT)
    paths_doc = _copy(root, vme.PATHS_DOC)
    paths_doc.write_text(
        paths_doc.read_text().replace(
            "Audit sidecars (`*.audit.jsonl`) are excluded from the committed tree",
            "Audit sidecars are handled elsewhere",
        )
    )

    row = _row(
        vme.run_availability(_context(root)).rows,
        "co-evolution audit sidecars (`**/*.audit.jsonl`)",
    )
    assert row.status == "FAIL"
    assert row.measured == "UNRECORDED"


@pytest.mark.parametrize(
    "argv",
    [
        ["--complete", "--only", "sidecars"],
        ["--complete", "--fast"],
    ],
)
def test_modes_that_cannot_mean_what_they_say_are_refused(argv: list[str]) -> None:
    """A partial or sampled run cannot certify completeness."""

    assert vme.main(argv) == 2


def test_unreadable_repo_root_is_a_usage_error(tmp_path: Path) -> None:
    """A tree with no manifests exits 2 with the missing file named."""

    assert vme.main(["--repo-root", str(tmp_path)]) == 2


def test_every_leg_has_a_runner_and_a_title() -> None:
    """``--only`` cannot name a leg the run has no runner or heading for."""

    assert set(vme.LEG_TITLES) == set(vme.LEGS) == set(vme.LEG_RUNNERS)
    assert [result.leg for result in vme.run_legs(_context(_REPO_ROOT), [])] == []


# --------------------------------------------------------------------------- #
# 4. read-only                                                                  #
# --------------------------------------------------------------------------- #


def test_the_command_writes_nothing_outside_a_temp_dir(tmp_path: Path) -> None:
    """Every leg the scratch tree can run leaves that tree byte-identical.

    ``--fast`` is included deliberately: it is the one mode that writes at all,
    and what it writes must be inside :func:`tempfile.TemporaryDirectory` and
    gone when the leg returns.
    """

    root = tmp_path / "repo"
    _manifests(root)
    _link(
        root,
        vme.ARTIFACTS_DOC,
        vme.PATHS_DOC,
        vme.FINALIST_REPORT,
        vme.FINALIST_RESULTS,
        f"{vme.SURROGATE_DIR}/fit-corpus.json",
        vme.CORPUS_SET,
        _SAMPLE_SET,
    )
    (root / "replays/ml_corpus").mkdir(parents=True, exist_ok=True)

    before = _tree_snapshot(root)
    ctx = _context(root, fast=True)
    vme.run_sidecars(ctx)
    vme.run_corpus(ctx)
    vme.run_paired(ctx)
    vme.run_availability(ctx)
    assert _tree_snapshot(root) == before


# --------------------------------------------------------------------------- #
# 5. the second review round (Codex, PR #348)                                   #
# --------------------------------------------------------------------------- #


def test_the_loss_path_may_omit_the_slate_manifest(tmp_path: Path) -> None:
    """Task 19.21's LOSS path creates no slate manifest, and must still run.

    `tasks/phase-19.md` puts `_finalist_eval_raw/MANIFEST.md` in scope "only on
    the recovery path", so on a ratified loss it does not exist. Reading it
    unconditionally killed context construction with usage error 2 — making the
    whole loss-acceptance route unreachable (Codex review, PR #348).
    """

    root = tmp_path / "repo"
    (root / vme.COEVO_DEST).mkdir(parents=True)
    (root / vme.COEVO_DEST / "PATHS.md").write_text("stub\n")
    (root / vme.EVIDENCE_MANIFEST).write_text(
        "| **tip sha — THE PIN** | **" + "a" * 40 + "** |\n"
        f"{_RETAINED_SECTION_STUB}"
        "```sha256\n"
        f"{'0' * 64}  coevo/moved.json\n"
        f"{'1' * 64}  README.md\n"
        "```\n"
    )
    (root / vme.ARTIFACTS_DOC).parent.mkdir(parents=True, exist_ok=True)
    (root / vme.ARTIFACTS_DOC).write_text("**Ruling 2026-08-15: LOST**\n")
    assert not (root / vme.SLATE_MANIFEST).exists()

    rows = vme.evidence_rows(root, slate_lost=True)
    assert rows and not any(
        row.manifest_path.startswith(vme._SLATE_PREFIX) for row in rows
    )

    # ... and the same tree with a RECOVERY ruling is a drifted tree, not a
    # close state: the manifest's absence then has to fail loud.
    with pytest.raises(vme.EvidenceError, match="records no loss"):
        vme.evidence_rows(root, slate_lost=False)


def test_an_evidence_row_cannot_escape_its_destination(tmp_path: Path) -> None:
    """A `..` in a digest row would map onto an unrelated in-tree artifact."""

    root = tmp_path / "repo"
    (root / vme.COEVO_DEST).mkdir(parents=True)
    (root / vme.EVIDENCE_MANIFEST).write_text(
        "| **tip sha — THE PIN** | **" + "a" * 40 + "** |\n"
        f"{_RETAINED_SECTION_STUB}"
        "```sha256\n"
        f"{'0' * 64}  coevo/../surrogate/ballot-predictor.json\n"
        "```\n"
    )
    with pytest.raises(vme.EvidenceError, match="escapes its destination root"):
        vme.evidence_rows(root, slate_lost=True)


def test_git_reads_disable_partial_clone_lazy_fetching() -> None:
    """The documented clone is blobless; a blob read must not reach the network.

    `git clone --filter=blob:none` is what README.md / docs/artifacts.md /
    docs/reading-guide.md tell a reader to run, and on such a checkout reading an
    omitted blob makes git fetch it from origin — a network call and a `.git`
    mutation inside a command whose contract is offline and read-only.
    """

    assert vme._GIT_ENV["GIT_NO_LAZY_FETCH"] == "1"
    # The helper every git read goes through, so neither call site can regress.
    completed = vme._git(_REPO_ROOT, "rev-parse", "--is-inside-work-tree")
    assert completed is not None and completed.returncode == 0


def test_adoption_constraints_are_compared_in_full(tmp_path: Path) -> None:
    """Editing a constraint's text after its name must not pass.

    The prefix-only comparison let the substantive guidance drift while every
    field still read identical — and that text reaches campaign meters verbatim
    (Codex review, PR #348).
    """

    committed = json.loads((_REPO_ROOT / vme.COMPOSED_DIR / "verdict.json").read_text())
    assert [str(item) for item in committed["adoption_constraints"]] == list(
        vme._COMPOSED_ADOPTION_CONSTRAINTS
    )
    # The pin is over whole strings, not names: every one carries its guidance.
    for pinned in vme._COMPOSED_ADOPTION_CONSTRAINTS:
        name, _, guidance = pinned.partition(":")
        assert guidance.strip(), f"{name} pinned by name only"
        assert len(pinned) > len(name) + 40


def test_a_registry_class_contradicting_its_storage_raises(tmp_path: Path) -> None:
    """`(a)` beside `pinned sha` is an invalid committed input, not a label."""

    root = tmp_path / "repo"
    doc = _copy(root, vme.ARTIFACTS_DOC)
    doc.write_text(
        doc.read_text().replace(
            "| **(c)** | pinned sha |", "| **(a)** | pinned sha |", 1
        )
    )
    with pytest.raises(vme.EvidenceError, match="contradicts its storage policy"):
        vme.registry_rows(root)
