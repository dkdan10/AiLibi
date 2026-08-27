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
import re
import shutil
import subprocess
import sys
import tomllib
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
    """A Context wired exactly as ``main`` wires it.

    ``slate_lost`` is threaded through deliberately: ``main`` reads the ruling
    BEFORE the manifests, so Task 19.21's recovery-only slate manifest may be
    absent on the loss path. A helper that quietly took the default would be
    testing a wiring production does not have.
    """

    ruling = (
        vme.read_slate_ruling(root) if (root / vme.ARTIFACTS_DOC).is_file() else None
    )
    return vme.Context(
        repo_root=root,
        fast=fast,
        complete=complete,
        evidence=vme.evidence_rows(root, slate_lost=ruling is not None and ruling.lost),
        pinned_sha=vme.read_pinned_sha(root),
        slate_ruling=ruling,
    )


def _availability_tree(root: Path) -> None:
    """Every probe anchor ``run_availability`` reads, as symlinks.

    Deliberately does NOT create `docs/artifacts.md` or the slate manifest: the
    loss path is defined by the absence of the latter, and tests that rewrite the
    ruling need their own copy of the former.
    """

    for probe in (
        "replays/samples/4p1i",
        "replays/ml_corpus/4p1i",
        "tests/fixtures",
        "data/personas.json",
        "training/artifacts/impostor",
        "training/artifacts/crew",
        "training/artifacts/anchor_study",
        vme.SURROGATE_DIR,
        vme.CONVICTION_DIR,
        vme.COMPOSED_DIR,
        "audits",
        "docs/media",
        "design/phase-12",
        "experiments/lab",
        "experiments/model_probe",
        "agents/tactical/learned/weights.json",
        "agents/tactical/learned/weights.json.sha256",
        "agents/tactical/learned/crew_weights.json",
        "agents/tactical/learned/crew_weights.json.sha256",
        "replays/samples/9p2i",
        "replays/ml_corpus/9p2i",
    ):
        _link(root, probe)
    # coevo/ is rebuilt from its TRACKED entries only — never linked whole.
    # The real directory's state is environment-dependent: after
    # `bash scripts/fetch_evidence.sh` the gitignored evidence payload sits
    # restored in place, and a wholesale symlink would drag that state into the
    # scratch tree, flipping the `coevo/ [(c)]` availability row this tree pins
    # as un-restored (the phase-19 close audit's F1). Linking exactly the
    # committed inventory keeps the tree's meaning fixed on any checkout; the
    # manifest and PATHS.md are tracked, so the probe's anchors still resolve.
    coevo_tracked = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "ls-files", "--", vme.COEVO_DEST],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert coevo_tracked, f"no tracked files under {vme.COEVO_DEST}"
    for rel in coevo_tracked:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(_REPO_ROOT / rel)
    # training/reports is built file by file rather than linked whole: linking
    # the real directory would drag `_finalist_eval_raw/MANIFEST.md` in with it
    # and quietly undo the condition the loss test puts under test.
    (root / "training/reports").mkdir(parents=True, exist_ok=True)
    for name in ("results-finalist-eval.jsonl", "report-finalist-eval.md"):
        (root / "training/reports" / name).symlink_to(
            _REPO_ROOT / "training/reports" / name
        )


def _index(root: Path, *paths: str) -> None:
    """Make ``root`` a git repo whose index holds exactly ``paths``.

    ``git ls-files`` reads the INDEX, so no commit is needed — and staging only
    the named paths lets a test state the committed inventory it is verifying
    against instead of inheriting whatever the scratch tree happens to contain.
    """

    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
    }
    subprocess.run(["git", "init", "-q", str(root)], check=True, env=env)
    subprocess.run(["git", "-C", str(root), "add", "--", *paths], check=True, env=env)


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
    # Four per-arm rows plus the Bonferroni row, which is compared against the
    # erratum's published conclusion rather than merely reported.
    assert [row.status for row in result.rows if row.status != "INFO"] == ["OK"] * 5
    assert _row(result.rows, "Bonferroni family bar").status == "OK"
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


#: The finalist report's availability-erratum headings. The errata are additive,
#: so the LAST one is the current record: a later section supersedes an earlier
#: one's promise instead of rewriting it.
_AVAILABILITY_ERRATUM = re.compile(r"^## \d+\. Availability erratum.*$", re.MULTILINE)


def _latest_availability_erratum(report: str) -> str:
    """The text of the finalist report's most recent availability erratum."""

    sections = re.split(r"^(?=## )", report, flags=re.MULTILINE)
    errata = [section for section in sections if _AVAILABILITY_ERRATUM.match(section)]
    assert errata, f"{vme.FINALIST_REPORT} carries no availability erratum"
    return errata[-1]


#: The destination PAIRING the erratum has to state: the evidence branch, then
#: the sha it is pinned at. Presence of the sha somewhere in the section is not
#: the claim — the section also cites the superseded staging ref by its own sha,
#: so a pairing naming the wrong commit while the real pin survived nearby as
#: history would read as verified (Codex review, PR #394).
_ERRATUM_DESTINATION = re.compile(
    r"evidence/phase-18-coevo[`*\s]*@[`*\s]*([0-9a-f]{40})"
)


def _erratum_disagreements(
    erratum: str, *, pinned_sha: str, ruling: vme.Ruling | None
) -> list[str]:
    """Where the erratum's availability story and the machinery's disagree."""

    if ruling is not None and ruling.lost:
        return [
            f"the erratum omits {token!r}, which the recorded "
            f"{ruling.outcome} ruling of {ruling.date} states"
            for token in (ruling.outcome, ruling.date)
            if token not in erratum
        ]
    named: list[str] = _ERRATUM_DESTINATION.findall(erratum)
    if not named:
        return ["the erratum states no `evidence/phase-18-coevo` @ <sha> destination"]
    return [
        f"the erratum pins the evidence commit at {sha}, not {pinned_sha}"
        for sha in sorted(set(named))
        if sha != pinned_sha
    ]


def _perturbed_errata(
    erratum: str, *, pinned_sha: str, ruling: vme.Ruling | None
) -> list[str]:
    """Copies of the erratum text a gate worth having has to reject."""

    if ruling is not None and ruling.lost:
        return [
            erratum.replace(ruling.outcome, "MISLAID"),
            erratum.replace(ruling.date, "1999-01-01"),
        ]
    decoy = "b" * len(pinned_sha)
    return [
        erratum.replace(pinned_sha, decoy),
        # The case mere presence cannot catch: the destination pairing names
        # another commit while the real pin survives as superseded history.
        _ERRATUM_DESTINATION.sub(
            lambda m: m.group(0).replace(m.group(1), decoy), erratum, count=1
        )
        + f"\n\n(superseded: {pinned_sha})\n",
    ]


def test_the_report_availability_erratum_agrees_with_the_machinery() -> None:
    """The research reader's document states the availability the gate measures.

    On the recovery path the erratum has to pin the evidence branch to the sha
    `read_pinned_sha` reads — the pairing, not the token, because that is what
    turns "where the raw slate lives" into one fetch a stranger can run. On a
    recorded loss it has to carry `read_slate_ruling`'s outcome AND its date.
    Both sides are read, never transcribed.

    The perturbation legs are copies of the erratum a correct gate must reject,
    including the one substring presence cannot see: a destination naming another
    commit while the real pin survives beside it as superseded history.
    """

    report = (_REPO_ROOT / vme.FINALIST_REPORT).read_text(encoding="utf-8")
    erratum = _latest_availability_erratum(report)
    pinned_sha = vme.read_pinned_sha(_REPO_ROOT)
    ruling = vme.read_slate_ruling(_REPO_ROOT)

    assert not _erratum_disagreements(erratum, pinned_sha=pinned_sha, ruling=ruling)

    for drifted in _perturbed_errata(erratum, pinned_sha=pinned_sha, ruling=ruling):
        assert drifted != erratum, "the perturbation changed nothing"
        assert _erratum_disagreements(drifted, pinned_sha=pinned_sha, ruling=ruling)


def test_recompute_reads_every_committed_verdict_against_the_declared_gap() -> None:
    """The three instruments re-derive from the FROZEN weights, and land STALE.

    The slow leg (~30s: two corpus tables plus the composed fidelity). It is the
    command's whole point — the Codex audit's executed-evidence row, run as one
    check — so it is asserted end to end rather than sampled.

    The baseline-7 record re-recorded ``replays/ml_corpus`` without re-fitting
    the ML artifacts (a named follow-up, audits/audit-phase-20-baseline-7.md
    §10.2), so every recomputed figure now measures a frozen fit against a corpus
    it never saw. The leg reports that as STALE rather than FAIL, and this test
    pins the whole shape of it: NOTHING may FAIL, the grounding row must be the
    one saying why, and the re-derived figures are pinned as measurements in
    their own right. The committed side of each row still carries the baseline-6
    number, so the two are readable against each other here and in the output.
    """

    result = vme.run_recompute(_context(_REPO_ROOT))
    failed = [row for row in result.rows if row.status == "FAIL"]
    assert not failed, "\n".join(f"{row.name}: {row.detail}" for row in failed)

    # The gap is declared by ONE row, and every other non-OK row points at it.
    grounding = _row(result.rows, "ML grounding")
    assert grounding.status == "STALE"
    assert "§10.2" in grounding.detail
    stale = [row for row in result.rows if row.status == "STALE"]
    assert len(stale) > 1  # non-vacuous: the recomputations are read, not skipped
    for row in stale:
        if row.name != "ML grounding":
            assert "ML grounding" in row.detail, row.name

    # The six figures the audit's executed-evidence table names, by name.
    assert {row.name for row in result.rows} >= {
        "surrogate top-1 (ranking channel)",
        "surrogate SKIP-vs-eject decision accuracy",
        "conviction flag-count Spearman",
        "conviction conversion-label accuracy",
        "composed decision accuracy",
        "composed exact-outcome match",
    }
    # Left: measured on the baseline-7 corpus. Right: the committed baseline-6
    # figure the row is read against. Pinned in pairs so neither can drift alone.
    for name, measured, committed in (
        ("surrogate top-1 (ranking channel)", "0.8181818", "0.7666666"),
        ("surrogate SKIP-vs-eject decision accuracy", "0.3908045", "0.3750000"),
        # was 0.6991081 — the corrected recorded flag label fits BETTER
        ("conviction flag-count Spearman", "0.7145778975", "0.5781584"),
        # was 0.9310344 — the conversion label now admits a spoken saw_move at
        # its destination, so it carries conversions the frozen fit never saw
        ("conviction conversion-label accuracy", "0.9080459", "0.9375000"),
        ("composed decision accuracy", "0.8620689", "0.8645833"),
        ("composed exact-outcome match", "0.8160919", "0.7916666"),
    ):
        row = _row(result.rows, name)
        assert row.measured.startswith(measured), row.measured
        assert row.committed.startswith(committed), row.committed


def test_the_stale_amnesty_stops_at_the_corpus_dependent_rows() -> None:
    """A corpus-INDEPENDENT disagreement still FAILS during the stale period.

    The grounding gap explains rows whose value is a measurement of frozen
    weights against the corpus. It explains nothing about the weight hashes, the
    manifest's configuration identity, or the composed adoption constraints:
    those are the same on any corpus, so a regression in one of them must turn
    the command red even while the ML fits are stale. This pins the boundary
    from both sides — the amnesty's membership, and that it is not the whole leg.
    """

    result = vme.run_recompute(_context(_REPO_ROOT))
    emitted = {row.name for row in result.rows}
    # Every named row is a row the leg actually produces (run_recompute raises
    # otherwise, so this is the readable statement of the same guard).
    assert vme._CORPUS_DEPENDENT_RECOMPUTE_ROWS <= emitted
    # And the leg is MORE than the amnesty: the corpus-independent rows exist,
    # are outside it, and are green on this checkout rather than downgraded.
    outside = emitted - vme._CORPUS_DEPENDENT_RECOMPUTE_ROWS - {"ML grounding"}
    assert outside == {
        "composed adoption constraints",
        "composed manifest.json reproduces",
        "surrogate weights sha256",
        "conviction weights sha256",
    }
    for name in outside:
        assert _row(result.rows, name).status == "OK", name
    # No row outside the amnesty was downgraded.
    for row in result.rows:
        if row.status == "STALE" and row.name != "ML grounding":
            assert row.name in vme._CORPUS_DEPENDENT_RECOMPUTE_ROWS, row.name


def test_a_perturbed_weight_hash_fails_even_while_the_fits_are_stale(
    tmp_path: Path,
) -> None:
    """The planted case: perturb a corpus-INDEPENDENT row and it goes red.

    ``composed/manifest.json`` records the weight digests the composed runner was
    assembled from — a fact about the artifacts, not about any corpus. Moving one
    of them must FAIL, and the declared grounding gap must not launder it into
    STALE. Without this, the amnesty's boundary would be asserted only by the
    membership list above and never exercised.
    """

    import json

    scratch = tmp_path / "repo"
    _manifests(scratch)
    for rel in (
        vme.CORPUS_SET,
        vme.SURROGATE_DIR,
        vme.CONVICTION_DIR,
        vme.ARTIFACTS_DOC,
        "training/reports/report-ballot-surrogate.md",
        "training/reports/report-conviction-model.md",
        "training/reports/report-composed-runner.md",
    ):
        _link(scratch, rel)
    composed = _copy(scratch, f"{vme.COMPOSED_DIR}/manifest.json")
    for rel in sorted(path.name for path in (_REPO_ROOT / vme.COMPOSED_DIR).iterdir()):
        if rel != "manifest.json":
            _link(scratch, f"{vme.COMPOSED_DIR}/{rel}")
    payload = json.loads(composed.read_text(encoding="utf-8"))
    payload["surrogate_weights_sha256"] = "b" * 64
    composed.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = vme.run_recompute(_context(scratch))
    assert _row(result.rows, "ML grounding").status == "STALE"  # the gap is declared
    assert _row(result.rows, "surrogate weights sha256").status == "FAIL"
    assert vme._failed(result.rows, complete=False)


def test_an_undeclared_corpus_still_fails_the_grounding_row(tmp_path: Path) -> None:
    """STALE is granted to ONE declared pair of digests, not to any mismatch.

    The planted case behind the leniency above: a corpus that is neither the fit
    corpus nor the one this checkout declares as the pending re-ground is an
    undeclared substrate, and the grounding row FAILS on it. Without this, the
    STALE branch would be an unconditional amnesty for corpus drift.
    """

    root = tmp_path / "repo"
    _manifests(root)
    _link(
        root,
        f"{vme.SURROGATE_DIR}/fit-corpus.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json.sha256",
    )
    corpus = root / vme.CORPUS_SET
    corpus.mkdir(parents=True)
    for child in sorted((_REPO_ROOT / vme.CORPUS_SET).iterdir()):
        (corpus / child.name).symlink_to(child)
    # One added recording moves the fingerprint off the declared digit string.
    (corpus / "replay-seed-999999.jsonl").symlink_to(
        _REPO_ROOT / vme.CORPUS_SET / "replay-seed-1000.jsonl"
    )

    row, stale = vme._grounding_row(root)
    assert not stale
    assert row.status == "FAIL"
    assert "undeclared substrate" in row.detail


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


def _broken_sidecar_pair(directory: Path) -> Path:
    """A sidecar and a target whose bytes do NOT hash to it. Returns the sidecar.

    Deliberately broken so the exclusion tests below cannot pass vacuously: if
    the walk reaches this pair, ``_verify_sidecar`` fails on it.
    """

    directory.mkdir(parents=True, exist_ok=True)
    (directory / "weights.json").write_text('{"w": 1}\n', encoding="utf-8")
    sidecar = directory / "weights.json.sha256"
    sidecar.write_text(f"{'0' * 64}  weights.json\n", encoding="utf-8")
    return sidecar


@pytest.mark.parametrize("marker_is_a_file", [True, False])
def test_a_nested_checkout_is_excluded_from_the_sidecar_walk(
    tmp_path: Path, marker_is_a_file: bool
) -> None:
    """A directory that marks itself as a checkout answers to its own index.

    A linked worktree writes a ``.git`` FILE, a clone a ``.git`` directory; both
    mean the same thing, so both are skipped. Without this, a developer with
    sibling worktrees checked out under the repo hashes THEIR staged bytes and
    reads a red row that says nothing about this checkout.
    """

    root = tmp_path / "repo"
    _manifests(root)
    nested = root / ".claude" / "worktrees" / "agent-1"
    sidecar = _broken_sidecar_pair(nested / "training" / "artifacts")
    marker = nested / ".git"
    if marker_is_a_file:
        marker.write_text(
            "gitdir: /elsewhere/.git/worktrees/agent-1\n", encoding="utf-8"
        )
    else:
        marker.mkdir()

    # The planted pair really is broken: it is excluded, not benign.
    assert vme._verify_sidecar(sidecar, root)[1]  # noqa: PLC2701
    assert sidecar not in vme.walk_sidecars(root)
    assert (
        _row(vme.run_sidecars(_context(root)).rows, "sidecars[IN-TREE]").status == "OK"
    )


def test_a_mismatched_sidecar_outside_a_nested_checkout_still_fails(
    tmp_path: Path,
) -> None:
    """The leg still bites: the nested-checkout rule narrows it, never disarms it."""

    root = tmp_path / "repo"
    _manifests(root)
    sidecar = _broken_sidecar_pair(root / "training" / "artifacts")

    assert sidecar in vme.walk_sidecars(root)
    row = _row(vme.run_sidecars(_context(root)).rows, "sidecars[IN-TREE]")
    assert row.status == "FAIL"
    assert "weights.json" in row.detail
    assert "!= sidecar" in row.detail


def test_the_walk_never_excludes_the_root_it_starts_at(tmp_path: Path) -> None:
    """The rule applies to DESCENDANTS: a checkout does not skip itself.

    Every real repo root holds a ``.git``, so a rule tested at the root would
    make the whole walk empty — and an empty walk also reports "0 failure(s)".
    """

    root = tmp_path / "repo"
    _manifests(root)
    sidecar = _broken_sidecar_pair(root / "training" / "artifacts")
    (root / ".git").mkdir()

    assert sidecar in vme.walk_sidecars(root)


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
    _link(
        root,
        f"{vme.SURROGATE_DIR}/fit-corpus.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json.sha256",
        vme.CORPUS_SET,
    )
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
    # STALE, not OK: this checkout declares one grounding gap (the corpus was
    # re-recorded under a frozen fit). What matters here is that it is not FAIL —
    # the perturbation above is located in the row it perturbed, not smeared
    # across the leg.
    assert _row(result.rows, "fit-corpus identity fingerprint").status == "STALE"
    assert result.notes and "SAMPLE" in result.notes[0]


def test_perturbed_corpus_fails_the_identity_fingerprint(tmp_path: Path) -> None:
    """A corpus whose bytes moved no longer fingerprints to the committed sha."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(
        root,
        f"{vme.SURROGATE_DIR}/fit-corpus.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json.sha256",
    )
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
    # The record is compared field by field, so the failure names WHICH field
    # drifted — an added replay moves the corpus digest and nothing else.
    assert "corpus_sha256" in row.detail
    assert "weights_sha256" not in row.detail


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
        f"{vme.SURROGATE_DIR}/ballot-predictor.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json.sha256",
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


# --------------------------------------------------------------------------- #
# 6. the third review round (Codex, PR #348)                                    #
# --------------------------------------------------------------------------- #


def test_complete_accepts_a_manifestless_recorded_loss_end_to_end(
    tmp_path: Path,
) -> None:
    """The WHOLE availability leg accepts a loss with no slate manifest.

    Three review rounds each found a different branch that still failed the
    ratified-loss close: the promised-set aggregate, then context construction,
    then the registry's count-parity check. Each previous fix was correct and
    each was too narrow, because each was tested at the branch it named. This
    test drives the leg end to end over the real registry document with the
    ruling rewritten to LOST and NO slate manifest present — the actual shape of
    Task 19.21's loss path — and asserts nothing in it fails `--complete`.
    """

    root = tmp_path / "repo"
    _availability_tree(root)
    doc = _copy(root, vme.ARTIFACTS_DOC)
    doc.write_text(
        doc.read_text().replace(
            "**Ruling 2026-08-15: RECOVERED**", "**Ruling 2026-08-15: LOST**"
        )
    )
    # The loss path's defining shape: Task 19.21 writes this only on recovery.
    assert not (root / vme.SLATE_MANIFEST).exists()

    ctx = _context(root, complete=True)
    assert ctx.lost_prefixes == frozenset({vme._SLATE_PREFIX})
    rows = vme.run_availability(ctx).rows

    slate_registry = next(
        row for row in rows if row.name.startswith("finalist-eval-raw/")
    )
    assert slate_registry.status == "INFO", slate_registry.detail
    assert "LOST" in slate_registry.measured
    slate_ruling = _row(rows, "Phase-18 finalist raw slate (Task 19.21 outcome)")
    assert slate_ruling.status == "INFO"

    # NOTHING about the lost slate's EVIDENCE fails the close gate — the whole
    # leg, not the single branch each review round happened to name.
    failed = {row.name for row in vme._failed(rows, complete=True)}
    assert slate_registry.name not in failed
    assert slate_ruling.name not in failed

    # Exactly three rows fail, and none of them is about the lost slate's
    # evidence. Asserted by name so the scratch tree's shape stays visible rather
    # than hidden behind a loose assertion:
    #
    #  * `coevo/` — those bytes are PROMISED (not lost) and this tree has not
    #    restored them, so ABSENT failing --complete is the correct behaviour;
    #  * the slate MANIFEST's own registry row — this tree pairs a LOST ruling
    #    with the registry as it stands TODAY, which still lists that file as a
    #    class-(b) in-git artifact. A real ratified loss would drop that row
    #    (and its probe here) in the same change that flipped the ruling;
    #  * the in-tree family inventory — a symlink scratch tree has no git index,
    #    so the committed file list cannot be read. ABSENT rather than a silent
    #    pass is the point of that row, and `--complete` failing on it is the
    #    same refusal-to-certify the sidecar inventory already makes.
    assert failed == {
        "coevo/ [(c)]",
        f"{vme.SLATE_MANIFEST} [(b)]",
        "in-tree family inventory",
    }


def test_a_declared_set_with_no_replays_fails(tmp_path: Path) -> None:
    """Deleting every replay in a committed set must not make the set vanish.

    Discovery keyed on "has a replay file" meant an emptied set dropped out of
    the walk, so the manifest's own missing-seed check never ran and even
    `--complete` certified a checkout missing a whole baseline set.
    """

    root = tmp_path / "repo"
    _manifests(root)
    _link(
        root,
        f"{vme.SURROGATE_DIR}/fit-corpus.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json",
        f"{vme.SURROGATE_DIR}/ballot-predictor.json.sha256",
        vme.CORPUS_SET,
    )
    emptied = root / _SAMPLE_SET
    emptied.mkdir(parents=True)
    (emptied / "MANIFEST.md").symlink_to(_REPO_ROOT / _SAMPLE_SET / "MANIFEST.md")

    # --fast must not turn an empty set into a vacuous pass either.
    row = _row(
        vme.run_corpus(_context(root, fast=True)).rows,
        f"corpus reconstruction: {_SAMPLE_SET}",
    )
    assert row.status == "FAIL"
    assert "NO REPLAYS ON DISK" in row.measured
    assert "is missing" in row.detail


def test_a_retained_entry_replaced_by_a_directory_fails(tmp_path: Path) -> None:
    """`.exists()` accepts a directory; the §3 inventory promises files."""

    root = tmp_path / "repo"
    _manifests(root)
    # Every retained path present as the REAL committed file except one, which
    # is a directory at the same pathname.
    retained = vme.retained_in_tree_paths(root)
    for rel in retained:
        dest = root / vme.COEVO_DEST / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(_REPO_ROOT / vme.COEVO_DEST / rel)
    swapped = retained[0]
    (root / vme.COEVO_DEST / swapped).unlink()
    (root / vme.COEVO_DEST / swapped).mkdir()

    row = _row(vme.run_sidecars(_context(root)).rows, "retained in-tree evidence")
    assert row.status == "FAIL"
    assert swapped in row.detail


def test_an_unknown_ruling_outcome_raises(tmp_path: Path) -> None:
    """Task 19.21 has two outcomes; a typo must not read as RECOVERED."""

    root = tmp_path / "repo"
    doc = _copy(root, vme.ARTIFACTS_DOC)
    doc.write_text(
        doc.read_text().replace(
            "**Ruling 2026-08-15: RECOVERED**", "**Ruling 2026-08-15: UNKNOWN**"
        )
    )
    with pytest.raises(vme.EvidenceError, match="which is none of"):
        vme.read_slate_ruling(root)


def test_a_duplicated_manifest_row_is_refused(tmp_path: Path) -> None:
    """A repeated row displaces an archived path without moving any count."""

    root = tmp_path / "repo"
    (root / vme.COEVO_DEST).mkdir(parents=True)
    (root / vme.COEVO_DEST / "PATHS.md").write_text("stub\n")
    (root / vme.EVIDENCE_MANIFEST).write_text(
        "| **tip sha — THE PIN** | **" + "a" * 40 + "** |\n"
        f"{_RETAINED_SECTION_STUB}"
        "```sha256\n"
        f"{'0' * 64}  coevo/kept.json\n"
        f"{'1' * 64}  coevo/kept.json\n"
        "```\n"
    )
    with pytest.raises(vme.EvidenceError, match="duplicate digest row"):
        vme.evidence_rows(root, slate_lost=True)


def test_a_report_value_contradicting_its_fraction_raises(tmp_path: Path) -> None:
    """The published figure beside a fraction is part of the committed verdict.

    Reading only the ``n/d`` meant the adjacent value could be edited to say
    something the fraction does not produce, and every recomputation row still
    read OK while the report a human opens visibly stated a different result.
    Both committed shapes are covered, each with its unperturbed control first.
    """

    decimal_root = tmp_path / "decimal"
    report = _copy(decimal_root, vme.CONVICTION_REPORT)
    assert vme.fraction_from_report(
        decimal_root, vme.CONVICTION_REPORT, "conversion accuracy"
    ) == (90, 96)
    report.write_text(report.read_text().replace("90/96 = 0.9375", "90/96 = 0.5000"))
    with pytest.raises(vme.EvidenceError, match="its own fraction does not produce"):
        vme.fraction_from_report(
            decimal_root, vme.CONVICTION_REPORT, "conversion accuracy"
        )

    percent_root = tmp_path / "percent"
    surrogate = _copy(percent_root, vme.SURROGATE_REPORT)
    label = "top-1 (ejected target ranked first)"
    assert vme.fraction_from_report(percent_root, vme.SURROGATE_REPORT, label) == (
        46,
        60,
    )
    surrogate.write_text(
        surrogate.read_text().replace("**76.7%** (46/60)", "**99.9%** (46/60)")
    )
    with pytest.raises(vme.EvidenceError, match="its own fraction does not produce"):
        vme.fraction_from_report(percent_root, vme.SURROGATE_REPORT, label)

    # A verifier that false-fails on a correct report teaches its reader to
    # ignore it, so the published value is matched by ADJACENCY to the fraction
    # rather than by scanning the cell for numbers: report cells also carry
    # confidence intervals, and a bare scan reads those bounds as contradictions.
    for benign in (
        "0.05263 (23/437) [0.0353, 0.0777]",  # the finalist report's shape
        "12/50 (24.0%) [0.1345, 0.3821]",
        "0/0 undef",
        "**76.7%** (46/60)",
        "90/96 = 0.9375",
    ):
        assert vme._displayed_drift(benign) == [], benign

    # ...but "no drift" must mean VALIDATED, not unexamined. `n/d (pct%)` is the
    # mirror of `pct% (n/d)`, and listing it as benign while no pattern read it
    # documented a gap as intentional: the fraction parsed, so the row stayed OK
    # while the percentage beside it could say anything.
    for contradicting in ("12/50 (99.0%)", "46/60 (99.9%)", "90/96 = 0.5000"):
        assert vme._displayed_drift(contradicting) != [], contradicting


def test_a_family_file_no_anchor_names_is_still_required(tmp_path: Path) -> None:
    """A tracked byte inside an in-tree family cannot vanish unnoticed.

    The per-family rows check ANCHORS, so a file no probe names and no other leg
    opens could be deleted with the family directory still standing and every row
    stayed OK. The review's own example is used verbatim, and the test asserts
    the DISCRIMINATION: the same tree passes with the file present.
    """

    root = tmp_path / "repo"
    _availability_tree(root)
    _link(root, vme.ARTIFACTS_DOC, vme.SLATE_MANIFEST)
    family = "training/artifacts/impostor"
    unanchored = f"{family}/bc-dagger/config.json"
    # Stage a file the probe table never names, so the inventory is exactly the
    # thing under test rather than whatever else the scratch tree holds.
    (root / family).unlink()
    _link(root, unanchored, f"{family}/map-elites/config.json")
    _index(root, unanchored, f"{family}/map-elites/config.json")

    # This tree cannot satisfy the registry's per-row COUNTS — it stages two
    # files against rows promising hundreds — so the row fails either way here.
    # The signal under test is therefore the specific disk problem naming this
    # file, which must appear only once the file is gone. (Count parity itself is
    # pinned by `test_a_committed_deletion_fails_the_inventory` and, at HEAD, by
    # `test_every_counted_registry_row_matches_the_index`.)
    present = _row(
        vme.run_availability(_context(root)).rows, "in-tree family inventory"
    )
    assert "absent from disk" not in present.detail, present.detail

    (root / unanchored).unlink()
    gone = _row(vme.run_availability(_context(root)).rows, "in-tree family inventory")
    assert gone.status == "FAIL"
    assert "absent from disk" in gone.detail
    assert unanchored in gone.detail
    # The family's own anchor row still reads OK — which is precisely why the
    # inventory row has to exist.
    anchor = next(
        row
        for row in vme.run_availability(_context(root)).rows
        if row.name.startswith(f"{family}/")
    )
    assert anchor.status == "OK"


def test_a_tree_without_a_git_index_reports_the_inventory_absent(
    tmp_path: Path,
) -> None:
    """No index is a reportable state, never a silent pass."""

    root = tmp_path / "repo"
    _availability_tree(root)
    _link(root, vme.ARTIFACTS_DOC, vme.SLATE_MANIFEST)
    row = _row(vme.run_availability(_context(root)).rows, "in-tree family inventory")
    assert row.status == "ABSENT"
    assert "no git index" in row.detail
    rows = vme.run_availability(_context(root, complete=True)).rows
    assert "in-tree family inventory" in {
        failing.name for failing in vme._failed(rows, complete=True)
    }


def test_a_drifted_bonferroni_conclusion_fails(tmp_path: Path) -> None:
    """The erratum's published multiplicity conclusion is compared, not quoted.

    Left at INFO, the bar or its named survivors could be edited to contradict
    the very p-values this leg verifies row by row and the command still exited
    0. Both halves of the statement are perturbed.
    """

    survivors_root = tmp_path / "survivors"
    _manifests(survivors_root)
    _link(survivors_root, vme.ARTIFACTS_DOC, vme.FINALIST_RESULTS)
    report = _copy(survivors_root, vme.FINALIST_REPORT)
    baseline = vme.bonferroni_from_report(survivors_root)
    assert (baseline.alpha, baseline.family, baseline.bar) == (0.05, 4, 0.0125)
    assert baseline.survivors == ("p18-imp-bfd145cb", "p18-imp-ea4bc955")
    assert baseline.refuted == ("p18-imp-7f73929d",)
    report.write_text(
        report.read_text().replace(
            "`p18-imp-bfd145cb` (p = 0.0041) survive it",
            "`p18-imp-6d327dcb` (p = 0.3075) survive it",
        )
    )
    row = _row(vme.run_paired(_context(survivors_root)).rows, "Bonferroni family bar")
    assert row.status == "FAIL"
    assert "survivors" in row.detail

    bar_root = tmp_path / "bar"
    _manifests(bar_root)
    _link(bar_root, vme.ARTIFACTS_DOC, vme.FINALIST_RESULTS)
    bar_report = _copy(bar_root, vme.FINALIST_REPORT)
    bar_report.write_text(
        bar_report.read_text().replace(
            "**α = 0.05 / 4 = 0.0125**", "**α = 0.05 / 2 = 0.0250**"
        )
    )
    bar_row = _row(vme.run_paired(_context(bar_root)).rows, "Bonferroni family bar")
    assert bar_row.status == "FAIL"
    assert "family size" in bar_row.detail and "bar:" in bar_row.detail


def test_a_drifted_composed_manifest_field_is_compared(tmp_path: Path) -> None:
    """Every manifest field is compared, not only the two weight hashes.

    `manifest.json` pins the operating parameters the recomputation applies, so a
    drifted `decision_threshold` or `corpus_set` would have let the command
    certify a configuration contradicting the computation it just performed. The
    re-derived side is exercised end to end by
    ``test_recompute_reproduces_every_committed_verdict``; this test pins the
    comparison's discrimination without paying for the 30s leg twice.
    """

    committed = json.loads(
        (_REPO_ROOT / f"{vme.COMPOSED_DIR}/manifest.json").read_text()
    )
    source = f"{vme.COMPOSED_DIR}/manifest.json"
    clean = vme._verdict_identity_row(
        "composed manifest.json reproduces",
        rederived=dict(committed),
        committed=committed,
        repo_root=_REPO_ROOT,
        path_fields=("replay_set_dir",),
        source=source,
    )
    assert clean.status == "OK"
    assert clean.measured.startswith(f"{len(committed)}/{len(committed)}")

    # Every field the previous revision ignored, one at a time.
    for field in (
        "decision_threshold",
        "skip_confidence_threshold",
        "composed_verdict",
        "conviction_verdict",
        "corpus_set",
        "replay_set_dir",
    ):
        drifted = dict(committed)
        drifted[field] = (
            "replays/ml_corpus/4p1i" if field == "replay_set_dir" else "DRIFTED"
        )
        row = vme._verdict_identity_row(
            "composed manifest.json reproduces",
            rederived=drifted,
            committed=committed,
            repo_root=_REPO_ROOT,
            path_fields=("replay_set_dir",),
            source=source,
        )
        assert row.status == "FAIL", field
        assert field in row.detail


def test_the_command_writes_no_bytecode() -> None:
    """The read-only contract covers `__pycache__`, not just artifacts.

    On a fresh writable checkout CPython would otherwise write `*.pyc` beside
    every module the command imports — inside the tree being verified. The
    ordering assertion is the substantive one: the flag only governs imports that
    follow it, so setting it after the bootstrap block would be a no-op for
    exactly the modules that matter.
    """

    assert sys.dont_write_bytecode is True
    lines = (_REPO_ROOT / "scripts/verify_ml_evidence.py").read_text().splitlines()
    flag = next(
        index for index, line in enumerate(lines) if "dont_write_bytecode" in line
    )
    first_bootstrap_import = next(
        index
        for index, line in enumerate(lines)
        if line.startswith(("import paired_stats", "from _verify_samples"))
    )
    assert flag < first_bootstrap_import


def test_a_foreign_repo_root_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A checkout this command cannot import from is one it cannot certify.

    `--repo-root` advertised "the checkout to verify", but the verifier code —
    `training.*`, `_verify_samples`, `paired_stats` — always resolves through the
    script's own `sys.path`. Recomputing one revision's evidence with another
    revision's engine is precisely the false certificate this command exists to
    prevent, so the combination is refused and the message names the honest way.
    """

    assert vme.main(["--repo-root", str(tmp_path)]) == 2
    stderr = capsys.readouterr().err
    assert "is not this script's checkout" in stderr
    assert "scripts/verify_ml_evidence.py" in stderr


def test_a_survivor_named_after_the_closing_phrase_is_counted(tmp_path: Path) -> None:
    """The erratum's conclusion is read whole, not up to its first clause.

    A window ending at the first "survive it" silently dropped any arm the report
    named afterwards, so a conclusion claiming a third survivor still compared
    equal to the recomputed two.
    """

    root = tmp_path / "repo"
    report = _copy(root, vme.FINALIST_REPORT)
    assert vme.bonferroni_from_report(root).survivors == (
        "p18-imp-bfd145cb",
        "p18-imp-ea4bc955",
    )
    report.write_text(
        report.read_text().replace(
            "(p = 0.0041) survive it.",
            "(p = 0.0041) survive it; `p18-imp-6d327dcb` also survives.",
        )
    )
    assert vme.bonferroni_from_report(root).survivors == (
        "p18-imp-6d327dcb",
        "p18-imp-bfd145cb",
        "p18-imp-ea4bc955",
    )

    # And the arm the same paragraph says FAILS is still not read as a survivor:
    # a refuting clause names its arm too, and is classified separately.
    assert "p18-imp-7f73929d" not in vme.bonferroni_from_report(_REPO_ROOT).survivors


def test_a_committed_deletion_fails_the_inventory(tmp_path: Path) -> None:
    """The index cannot be its own expectation — that is round 1's finding again.

    A working-tree deletion leaves the path tracked and missing from disk. A
    COMMITTED deletion removes it from the index too, so both sides of a
    self-derived count shrink together and the row still reads OK while
    `docs/artifacts.md` goes on promising the file. Only the document's stated
    count notices, which is why the two are compared.
    """

    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "b.json").write_text("{}")

    assert vme.inventory_problems(tmp_path, [("fam/", ["a.json", "b.json"], 2)]) == []

    committed_deletion = vme.inventory_problems(tmp_path, [("fam/", ["a.json"], 2)])
    assert len(committed_deletion) == 1
    assert "promises 2 files" in committed_deletion[0]
    assert "tracks 1" in committed_deletion[0]

    (tmp_path / "b.json").unlink()
    working_tree_deletion = vme.inventory_problems(
        tmp_path, [("fam/", ["a.json", "b.json"], 2)]
    )
    assert any("absent from disk" in problem for problem in working_tree_deletion)
    # A row the registry states no count for is still checked against the disk.
    assert vme.inventory_problems(tmp_path, [("fam/", ["a.json", "b.json"], None)])


def test_every_counted_registry_row_matches_the_index() -> None:
    """The scope table and `docs/artifacts.md` agree at HEAD, row by row.

    This is what makes the scope table safe to hand-write: a mis-scoped entry
    disagrees with the count the document states and turns the command red,
    rather than quietly inventorying the wrong set of bytes.
    """

    row = _row(
        vme.run_availability(_context(_REPO_ROOT)).rows, "in-tree family inventory"
    )
    assert row.status == "OK", row.detail
    counted = int(row.committed.split(" row(s)", 1)[0])
    assert counted >= 10, row.committed
    # Every in-tree registry row has a scope; a row nothing enumerates raises.
    for key, _cls, where, _size in vme.registry_rows(_REPO_ROOT):
        if vme._WHERE_TO_CLASS[where] == "IN-TREE":
            assert vme.in_tree_inventory(_REPO_ROOT, key) is not None


def test_a_registry_row_with_no_inventory_scope_raises() -> None:
    """A row whose bytes nothing enumerates cannot be reported as complete."""

    with pytest.raises(vme.EvidenceError, match="no inventory scope"):
        vme.in_tree_inventory(_REPO_ROOT, "some/row/the/table/does/not/cover")


def test_a_manifest_the_product_rejects_cannot_be_certified(tmp_path: Path) -> None:
    """Both sides go through `ComposedManifest`, so its invariants apply.

    A dict comparison this file assembled would happily match two sides that
    both said `conviction_verdict: NO-GO` — a composition `build_composed_manifest`
    refuses to construct and `ComposedManifest` does not permit.
    """

    from training.composed_runner import (
        COMPOSED_MANIFEST_FILENAME,
        load_composed_manifest,
    )

    committed = json.loads(
        (_REPO_ROOT / f"{vme.COMPOSED_DIR}/manifest.json").read_text()
    )
    assert load_composed_manifest(_REPO_ROOT / vme.COMPOSED_DIR).conviction_verdict

    for field, value in (
        ("conviction_verdict", "NO-GO"),  # the product permits only GO
        ("composed_verdict", "MAYBE"),  # outside the verdict vocabulary
    ):
        root = tmp_path / field
        root.mkdir()
        drifted = dict(committed)
        drifted[field] = value
        (root / COMPOSED_MANIFEST_FILENAME).write_text(json.dumps(drifted))
        with pytest.raises(Exception):
            load_composed_manifest(root)

    # An ADDED field is refused too (`extra="forbid"`), so a manifest that grew a
    # key cannot slip past a field-for-field comparison.
    root = tmp_path / "extra"
    root.mkdir()
    (root / COMPOSED_MANIFEST_FILENAME).write_text(
        json.dumps({**committed, "unreviewed_knob": 1})
    )
    with pytest.raises(Exception):
        load_composed_manifest(root)


def test_a_clause_this_command_cannot_classify_raises(tmp_path: Path) -> None:
    """An ambiguous conclusion is refused, not guessed at.

    A whole-clause filter dropped any clause carrying a refutation marker — so
    "`A` fails while `B` also clears" discarded the asserted survivor `B`, and
    because the earlier clause still named the expected pair, the row read OK
    while the report claimed an extra survivor. Chasing that with finer-grained
    heuristics is unbounded; the rule is inverted instead. This is deliberately
    stricter than the prose allows: a legitimate rewording now fails loudly,
    which is fixable, rather than being mis-read, which is not.
    """

    root = tmp_path / "mixed"
    report = _copy(root, vme.FINALIST_REPORT)
    report.write_text(
        report.read_text().replace(
            "**fails the multiplicity correction**;",
            "**fails the multiplicity correction** while `p18-imp-6d327dcb` "
            "also clears;",
        )
    )
    with pytest.raises(vme.EvidenceError, match="cannot tell what it claims"):
        vme.bonferroni_from_report(root)

    # An arm named with NO verdict at all is equally unreadable.
    bare_root = tmp_path / "bare"
    bare = _copy(bare_root, vme.FINALIST_REPORT)
    bare.write_text(
        bare.read_text().replace(
            "`p18-imp-7f73929d` (p = 0.0352) **fails the multiplicity correction**;",
            "`p18-imp-7f73929d` (p = 0.0352) was also measured;",
        )
    )
    with pytest.raises(vme.EvidenceError, match="cannot tell what it claims"):
        vme.bonferroni_from_report(bare_root)


def test_a_report_refuting_an_arm_the_p_values_clear_fails(tmp_path: Path) -> None:
    """The refuted half of the conclusion is a claim about the p-values too."""

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, vme.ARTIFACTS_DOC, vme.FINALIST_RESULTS)
    report = _copy(root, vme.FINALIST_REPORT)
    # Swap the two halves: say the arm that clears (0.0041 < 0.0125) fails, and
    # the arm that fails (0.0352) survives.
    report.write_text(
        report.read_text()
        .replace(
            "`p18-imp-7f73929d` (p = 0.0352) **fails the multiplicity correction**",
            "`p18-imp-bfd145cb` (p = 0.0041) **fails the multiplicity correction**",
        )
        .replace(
            "and `p18-imp-bfd145cb` (p = 0.0041) survive it",
            "and `p18-imp-7f73929d` (p = 0.0352) survive it",
        )
    )
    row = _row(vme.run_paired(_context(root)).rows, "Bonferroni family bar")
    assert row.status == "FAIL"
    assert "survivors" in row.detail
    assert "refuted" in row.detail
    assert "p18-imp-bfd145cb" in row.detail


def test_a_fit_corpus_record_keyed_to_other_weights_fails(tmp_path: Path) -> None:
    """The fit-corpus record is checked WHOLE, through the product's loader.

    `load_surrogate_runner_factory` cross-checks `weights_sha256` unconditionally
    — the Task 18.14 substrate fence — and refuses the artifact when it drifts.
    Reading a raw mapping and checking only `corpus_sha256` meant this command
    could certify an artifact the product will not load.
    """

    from training.surrogate.runner import load_fit_corpus_record

    root = tmp_path / "repo"
    _manifests(root)
    _link(root, vme.ARTIFACTS_DOC, vme.CORPUS_SET, _SAMPLE_SET)
    for name in ("ballot-predictor.json", "ballot-predictor.json.sha256"):
        _link(root, f"{vme.SURROGATE_DIR}/{name}")
    record = _copy(root, f"{vme.SURROGATE_DIR}/fit-corpus.json")
    committed = json.loads(record.read_text())
    assert load_fit_corpus_record(root / vme.SURROGATE_DIR).corpus_sha256

    # The corpus digest is untouched; only the weights key moves.
    record.write_text(
        json.dumps({**committed, "weights_sha256": "0" * 64}, indent=2) + "\n"
    )
    row = _row(vme.run_corpus(_context(root)).rows, "fit-corpus identity fingerprint")
    assert row.status == "FAIL"
    assert "weights_sha256" in row.detail
    assert "substrate fence" in row.detail

    # And the corpus-set name is checked as well.
    record.write_text(json.dumps({**committed, "corpus_set": "4p1i"}, indent=2) + "\n")
    drifted_set = _row(
        vme.run_corpus(_context(root)).rows, "fit-corpus identity fingerprint"
    )
    assert drifted_set.status == "FAIL"
    assert "corpus_set" in drifted_set.detail


# --------------------------------------------------------------------------- #
# 7. the gate fence — the restore destinations sit outside `mypy .`            #
# --------------------------------------------------------------------------- #

_FETCH_SCRIPT = "scripts/fetch_evidence.sh"
_DEST_ASSIGNMENT = re.compile(
    r'^(?P<var>COEVO_DEST|SLATE_DEST)="\$REPO_ROOT/(?P<rel>[^"]+)"$', re.MULTILINE
)


def _restore_destinations() -> dict[str, str]:
    """The repo-relative roots ``fetch_evidence.sh`` restores into, from the script.

    Read out of the script's own assignments rather than restated here, so the mypy
    fence below is pinned to what the restore actually writes.
    """

    text = (_REPO_ROOT / _FETCH_SCRIPT).read_text()
    found = {m.group("var"): m.group("rel") for m in _DEST_ASSIGNMENT.finditer(text)}
    assert set(found) == {"COEVO_DEST", "SLATE_DEST"}, (
        f"{_FETCH_SCRIPT} no longer assigns both destinations as "
        f'VAR="$REPO_ROOT/<rel>"; got {sorted(found)}'
    )
    return found


def _mypy_exclude() -> str:
    config = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text())
    exclude = config["tool"]["mypy"]["exclude"]
    assert isinstance(exclude, str)
    return exclude


def _exclude_alternatives(exclude: str) -> tuple[str, ...]:
    """The top-level alternatives inside the exclude's ``^( … )`` group.

    Split at parenthesis depth 0: one alternative carries a nested group of its own,
    so a plain ``str.split("|")`` would tear it apart.
    """

    assert exclude.startswith("^(") and exclude.endswith(")"), exclude
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in exclude[2:-1]:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "|" and depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return tuple(parts)


def _tracked_python() -> list[str]:
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "ls-files", "--", "*.py"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()


def test_mypy_exclude_fences_both_restore_destinations() -> None:
    """``mypy .`` must not walk what ``scripts/fetch_evidence.sh`` restores.

    The per-destination ``.gitignore`` the restore writes fences ``git add``, not a
    type checker, so without this the documented restore and the documented gate
    exclude each other: the restored slate's untracked operator helpers were never
    held to the strict bar and reported 15 errors over 358 files against the clean
    state's 354 (audits/audit-phase-19-close.md §1 F1).
    """

    destinations = _restore_destinations()
    assert destinations["COEVO_DEST"] == vme.COEVO_DEST
    assert destinations["SLATE_DEST"] == vme.SLATE_DEST

    pattern = re.compile(_mypy_exclude())
    for dest in destinations.values():
        for probe in (f"{dest}/", f"{dest}/helper.py", f"{dest}/nested/deep/help.py"):
            assert pattern.search(probe), f"mypy exclude does not fence {probe!r}"


def test_the_destination_alternatives_swallow_no_tracked_python() -> None:
    """The fence is exactly the two restore roots — it hides no committed module.

    Checked per added alternative rather than over the whole regex: the pre-existing
    ``experiments/lab/`` and ``design/`` alternatives legitimately cover tracked
    files.
    """

    alternatives = _exclude_alternatives(_mypy_exclude())
    tracked = _tracked_python()
    assert tracked, "no tracked Python files found"
    for dest in _restore_destinations().values():
        alternative = f"{dest}/"
        assert alternative in alternatives, (
            f"mypy exclude no longer carries {alternative!r} as its own alternative"
        )
        added = re.compile(f"^({alternative})")
        swallowed = [path for path in tracked if added.search(path)]
        assert swallowed == [], (
            f"{alternative!r} would hide tracked modules: {swallowed}"
        )


def test_the_fence_can_fail_when_a_destination_alternative_is_dropped() -> None:
    """Narrow the exclude back to its pre-fence form and the destinations return.

    Without this, the pin above would still pass on an exclude that fenced the
    destinations only by accident — a coincidental prefix, or a broadened
    ``training/`` alternative that also swallowed real code.
    """

    alternatives = _exclude_alternatives(_mypy_exclude())
    destinations = set(_restore_destinations().values())
    added = {f"{dest}/" for dest in destinations}
    kept = [alternative for alternative in alternatives if alternative not in added]
    assert len(kept) == len(alternatives) - len(added)
    narrowed = re.compile("^(" + "|".join(kept) + ")")

    for dest in destinations:
        assert not narrowed.search(f"{dest}/helper.py"), (
            f"{dest!r} is fenced by something other than its own alternative; "
            "dropping that alternative would not expose it"
        )
    # The narrowing removed only the two alternatives under test.
    assert narrowed.search("experiments/lab/ml_spike/core.py")
    assert narrowed.search("design/phase-12/gen_map_reference.py")
