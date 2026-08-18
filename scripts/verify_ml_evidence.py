#!/usr/bin/env python3
"""One read-only, offline command for the whole ML evidence story (Task 19.23).

The Phase-19 Codex audit reproduced this project's ML evidence by hand, one
recomputation at a time (`audits/audit-phase-19-input-codex.md` §"Executed
evidence": *"Offline ML evidence recomputation — PASS for corpus verifier,
surrogate, conviction, and composed runner"*), and the triage's work-list asked
for the consolidation: *"One `verify-ml-evidence` command for hashes, corpus
reconstruction, surrogate/conviction/composed recomputation, paired statistics,
and artifact-availability reporting"* (`audits/audit-phase-19-triage.md` §7 item
24 [S-Codex / S-Claude]). This is that command. Five legs, one exit code:

1. **sidecars** — PER-CLASS sha-256 verification. The in-tree sidecars verify
   fully offline on a bare checkout. The sidecars whose bytes Task 19.22 moved
   onto the pinned evidence commit verify hash-for-hash once
   `scripts/fetch_evidence.sh` has restored them, and otherwise report as their
   own EVIDENCE-BRANCH-ABSENT class with the count quoted — never a silent skip,
   and never a network call (this command does not fetch; it reads what is on
   disk and what the committed manifests say should be).
2. **corpus** — replay reconstruction, delegated to
   ``scripts/_verify_samples.py`` (the byte verifier behind
   ``scripts/verify_samples.sh``), plus the fit-corpus identity fingerprint the
   surrogate artifact commits.
3. **recompute** — the surrogate ranking/decision channels, the conviction
   model's flag and conversion channels, and the composed runner's decision and
   exact-outcome channels, each re-derived from the FROZEN committed weights and
   compared against the committed verdict that owns the number.
4. **paired** — the finalist paired statistics, via ``scripts/paired_stats``
   (Task 19.20), compared against the erratum table that report commits.
5. **availability** — the availability class of every named evidence artifact,
   read from `docs/artifacts.md`'s registry (in-tree / evidence-branch /
   repo-external / lost), including the Task 19.21 raw-slate outcome.

Nothing here retrains, re-records, or writes an artifact: every leg reads
committed bytes, and the only path this command ever writes to is a
:func:`tempfile.TemporaryDirectory` used by ``--fast`` to mirror a sampled
subset of a replay set. It never opens a socket.

Usage::

    uv run python scripts/verify_ml_evidence.py
    uv run python scripts/verify_ml_evidence.py --fast
    uv run python scripts/verify_ml_evidence.py --complete
    uv run python scripts/verify_ml_evidence.py --only sidecars --only availability

``--fast`` samples the corpus reconstruction rather than walking every committed
replay, and says so in the output (the sampled seeds are printed; a sampled run
is never reported as a full walk). ``--complete`` is the close gate
(`tasks/phase-19.md` Task 19.28): it FAILS on any byte that was promised
archival availability and is absent, while ACCEPTING an availability class that
a committed manifest RECORDS as lost — a ratified loss is a valid close state,
a silent one is not. ``--only`` restricts the run to named legs and is refused
under ``--complete``, because a partial run cannot certify completeness.

Exit codes: ``0`` every check passed, ``1`` at least one check failed, ``2``
usage error (bad leg name, missing repo file the run cannot proceed without).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path, PurePosixPath
from typing import Final, Literal

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR: Final = Path(__file__).resolve().parent

# A command whose banner says "no artifact is written" must not write bytecode
# either. On a fresh writable checkout with no warm caches, CPython creates
# ``__pycache__/*.pyc`` beside every module imported below — ``paired_stats``,
# ``_verify_samples``, and the ``training.*`` packages the recompute leg imports
# lazily — INSIDE the checkout being verified, which is a mutation the read-only
# contract forbids and which the read-only test could not see, because it
# snapshots the synthetic tree while the imports land in the real one (Codex
# review, PR #348). This must precede the bootstrap imports: it only governs
# imports that follow it.
sys.dont_write_bytecode = True

# Make both the top-level packages (``training``) and the sibling script modules
# (``paired_stats``, ``_verify_samples`` — top-level names per
# ``mypy_path = "scripts"``) importable under
# ``uv run python scripts/verify_ml_evidence.py``. Mirrors
# scripts/check_doc_facts.py.
for _bootstrap_path in (_REPO_ROOT, _SCRIPTS_DIR):
    if str(_bootstrap_path) not in sys.path:
        sys.path.insert(0, str(_bootstrap_path))

import paired_stats  # noqa: E402

from _verify_samples import verify_samples  # noqa: E402

# --------------------------------------------------------------------------- #
# The committed files this command reads. Every one of them is class (a)/(b) —  #
# in git — so a bare checkout can run every leg except the evidence-branch      #
# ones, which report themselves absent rather than failing.                     #
# --------------------------------------------------------------------------- #
ARTIFACTS_DOC: Final = "docs/artifacts.md"
PATHS_DOC: Final = "training/artifacts/coevo/PATHS.md"
EVIDENCE_MANIFEST: Final = "training/artifacts/coevo/EVIDENCE-MANIFEST.md"
SLATE_MANIFEST: Final = "training/reports/_finalist_eval_raw/MANIFEST.md"
COEVO_DEST: Final = "training/artifacts/coevo"
SLATE_DEST: Final = "training/reports/_finalist_eval_raw"

CORPUS_SET: Final = "replays/ml_corpus/9p2i"
SURROGATE_DIR: Final = "training/artifacts/surrogate"
CONVICTION_DIR: Final = "training/artifacts/conviction"
COMPOSED_DIR: Final = "training/artifacts/composed"

SURROGATE_REPORT: Final = "training/reports/report-ballot-surrogate.md"
CONVICTION_REPORT: Final = "training/reports/report-conviction-model.md"
FINALIST_REPORT: Final = "training/reports/report-finalist-eval.md"
FINALIST_RESULTS: Final = "training/reports/results-finalist-eval.jsonl"

REPLAY_ROOTS: Final[tuple[str, ...]] = ("replays/samples", "replays/ml_corpus")

#: The legs, in run order. ``--only`` selects from exactly these names.
LEGS: Final[tuple[str, ...]] = (
    "sidecars",
    "corpus",
    "recompute",
    "paired",
    "availability",
)

#: How many seeds per replay set ``--fast`` verifies. Eight is enough to catch a
#: whole-set drift (an engine change moves every chain, not one) while keeping
#: the leg to a second or two; the exact seeds are printed, so a --fast run is
#: never mistakable for the full walk.
FAST_SAMPLE_PER_SET: Final = 8

#: Directories the sidecar walk never descends into: build output, caches and
#: dependency trees hold no committed artifact, and `.git` holds every historical
#: version of the ones that count.
WALK_SKIP_DIRS: Final[frozenset[str]] = frozenset(
    {
        ".git",
        ".hypothesis",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "dist",
        "node_modules",
    }
)

_SIDECAR_SUFFIX: Final = ".sha256"
_REPLAY_GLOB: Final = "replay-seed-*.jsonl"
#: The per-set provenance record: what DECLARES a replay set to exist.
_SET_MANIFEST: Final = "MANIFEST.md"

#: The evidence commit's two top-level prefixes, as the manifests spell them.
_COEVO_PREFIX: Final = "coevo/"
_SLATE_PREFIX: Final = "finalist-eval-raw/"

#: The EVIDENCE-MANIFEST section heading whose table enumerates the bytes the
#: 19.22 prune RETAINED in-tree — the committed in-tree inventory.
_RETAINED_SECTION: Final = "## 3. What stayed in-tree"

# The fenced digest blocks both evidence manifests carry, and the row shape
# inside them: ``<64 hex>  <path>`` — shasum-compatible, which is why
# scripts/fetch_evidence.sh can feed them straight to ``sha256sum -c``.
_DIGEST_FENCE_OPEN: Final = "```sha256"
_DIGEST_FENCE_CLOSE: Final = "```"
_DIGEST_ROW: Final = re.compile(r"^([0-9a-f]{64})  (\S.*)$")
# The pin lives in EVIDENCE-MANIFEST.md §1; read, never hardcoded (the manifest
# owns it, exactly as scripts/fetch_evidence.sh reads it).
_PIN_ROW_MARKER: Final = "tip sha — THE PIN"
_SHA1_RE: Final = re.compile(r"\b[0-9a-f]{40}\b")

Status = Literal["OK", "FAIL", "ABSENT", "INFO"]

#: The availability vocabulary of `docs/artifacts.md`, plus the two outcomes for
#: named evidence the registry table does not hold a row for.
AvailabilityClass = Literal[
    "IN-TREE", "EVIDENCE-BRANCH", "REPO-EXTERNAL", "LOST", "REGENERATED"
]


class EvidenceError(RuntimeError):
    """A committed input this command cannot proceed without is missing or malformed.

    Raised — never swallowed — when the manifests, the registry document or a
    report have drifted out of the shape every guard below is built from.
    Reporting a green count off a manifest that no longer parses would be the
    silent fallback AGENTS.md forbids outright.
    """


# --------------------------------------------------------------------------- #
# Result rows                                                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CheckRow:
    """One check: what was measured, what the committed record says, and where.

    ``status`` is the whole verdict surface. ``OK`` passed; ``FAIL`` is a
    measured disagreement and always fails the run; ``ABSENT`` is a byte that is
    not on this checkout and is expected not to be (the evidence-branch class
    before a restore) — it passes a default run and FAILS ``--complete``;
    ``INFO`` is a recorded state that is not a measurement of this checkout
    (a repo-external working root, a manifest-recorded loss, a class-(d) view)
    and never fails.
    """

    name: str
    measured: str
    committed: str
    source: str
    status: Status
    detail: str = ""


@dataclass(frozen=True)
class LegResult:
    """Every row a leg produced, plus the notes it wants printed above them."""

    leg: str
    rows: tuple[CheckRow, ...]
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceRow:
    """One file the pinned evidence commit carries, as a manifest row.

    ``repo_path`` is where ``scripts/fetch_evidence.sh`` restores it, relative to
    the repo root; it is ``None`` for the evidence branch's own ``README.md``,
    which the manifest hashes but the restore deliberately does not place in the
    tree (it is branch metadata, checked straight out of the commit object).
    """

    digest: str
    manifest_path: str
    repo_path: str | None


@dataclass(frozen=True)
class Ruling:
    """A dated availability ruling recorded in `docs/artifacts.md`.

    ``lost`` is the whole point: a ruling that records a LOSS means the bytes it
    covers were never promised archival availability, so they are not part of
    the promised set ``--complete`` requires. A ratified loss is a valid close
    state; the deadlock it would otherwise cause is not.
    """

    date: str
    outcome: str

    @property
    def lost(self) -> bool:
        return self.outcome in _LOSS_RULINGS


@dataclass(frozen=True)
class Context:
    """Everything the legs share: the tree under test and the run's mode."""

    repo_root: Path
    fast: bool
    complete: bool
    evidence: tuple[EvidenceRow, ...]
    pinned_sha: str
    #: The Task 19.21 raw-slate ruling, or ``None`` when the document records
    #: none (which is itself a failure the availability leg reports).
    slate_ruling: Ruling | None

    @property
    def lost_prefixes(self) -> frozenset[str]:
        """Evidence-commit prefixes a committed ruling records as LOST.

        Every promised-byte check subtracts these. Excluding them at the SOURCE
        rather than relabelling a summary row afterwards is what makes a
        recorded loss acceptable to ``--complete``: with the coevo payload
        restored and a lost slate absent, an aggregate that still counted the
        slate would read PARTIAL and fail the close on bytes nobody promised.
        """

        if self.slate_ruling is not None and self.slate_ruling.lost:
            return frozenset({_SLATE_PREFIX})
        return frozenset()

    def is_lost(self, row: EvidenceRow) -> bool:
        return any(
            row.manifest_path.startswith(prefix) for prefix in self.lost_prefixes
        )


# --------------------------------------------------------------------------- #
# Small shared readers                                                         #
# --------------------------------------------------------------------------- #


def _read_text(repo_root: Path, rel: str) -> str:
    path = repo_root / rel
    if not path.is_file():
        raise EvidenceError(f"{rel} is missing from {repo_root} — cannot verify")
    return path.read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    """Stream a file's sha-256 (the manifests' digest, 1 MiB at a time)."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_digest_block(repo_root: Path, rel: str) -> list[tuple[str, str]]:
    """Peel a manifest's fenced ``sha256`` block into ``(digest, path)`` rows.

    The same block ``scripts/fetch_evidence.sh`` feeds to ``sha256sum -c``. A
    manifest with no block, or with a row that is not a digest row, is a drifted
    manifest and raises: every guard in this command is built from these rows, so
    a silently short list would shrink each of them at once (the failure mode PR
    #346 reproduced on the fetch side).
    """

    rows: list[tuple[str, str]] = []
    inside = False
    found_block = False
    for lineno, line in enumerate(_read_text(repo_root, rel).splitlines(), start=1):
        if not inside:
            if line.rstrip() == _DIGEST_FENCE_OPEN:
                inside = True
                found_block = True
            continue
        if line.rstrip() == _DIGEST_FENCE_CLOSE:
            inside = False
            continue
        match = _DIGEST_ROW.match(line)
        if match is None:
            raise EvidenceError(
                f"{rel}:{lineno}: not a '<sha256>  <path>' row inside the "
                f"sha256 block: {line!r}"
            )
        rows.append((match.group(1), match.group(2)))
    if inside:
        raise EvidenceError(f"{rel}: an unterminated ```sha256 block")
    if not found_block:
        raise EvidenceError(f"{rel}: no ```sha256 digest block to verify against")
    if not rows:
        raise EvidenceError(f"{rel}: the ```sha256 block is empty")
    return rows


def _confined(dest_root: str, relative: str, manifest: str, raw: str) -> str:
    """Map a manifest row under its destination root, refusing any escape.

    ``coevo/../surrogate/ballot-predictor.json`` passes a bare ``startswith``
    check and lands on an unrelated in-tree artifact, so a one-for-one row
    swap could keep every count green while the real archived path went
    unpromised and unchecked (Codex review, PR #348). Absolute paths and ``..``
    components are refused exactly as :func:`sidecar_targets` refuses them, and
    the normalized result must still sit beneath the destination root.
    """

    if relative.startswith("/") or ".." in PurePosixPath(relative).parts:
        raise EvidenceError(
            f"{manifest}: digest row {raw!r} escapes its destination root "
            f"({dest_root}); refusing to map it"
        )
    mapped = PurePosixPath(f"{dest_root}/{relative}")
    if not mapped.is_relative_to(PurePosixPath(dest_root)):
        raise EvidenceError(
            f"{manifest}: digest row {raw!r} normalizes to {mapped}, outside "
            f"{dest_root}; refusing to map it"
        )
    return str(mapped)


def evidence_rows(
    repo_root: Path, *, slate_lost: bool = False
) -> tuple[EvidenceRow, ...]:
    """Every file the pinned evidence commit carries, with its restore path.

    Composes the two manifests exactly as ``scripts/fetch_evidence.sh``'s
    ``peel_digests`` does: EVIDENCE-MANIFEST.md §7 covers ``coevo/`` plus the
    branch README, and §8 delegates the slate's 1,569 digests to the Task 19.21
    manifest rather than copying them. Both sides are rewritten to where the
    restore actually puts them.
    """

    rows: list[EvidenceRow] = []
    # A duplicated digest row keeps the total unchanged while one archived path
    # silently stops being promised — the payload loop just hashes the survivor
    # twice and reports everything restored (Codex review, PR #348). Both the
    # manifest spelling and the destination it maps to must be unique.
    seen_manifest: dict[str, str] = {}
    seen_repo: dict[str, str] = {}

    def _claim(manifest: str, manifest_path: str, repo_path: str | None) -> None:
        if manifest_path in seen_manifest:
            raise EvidenceError(
                f"{manifest}: duplicate digest row for {manifest_path!r} — a "
                "repeated row displaces an archived path without moving any count"
            )
        seen_manifest[manifest_path] = manifest
        if repo_path is not None:
            if repo_path in seen_repo:
                raise EvidenceError(
                    f"{manifest}: {manifest_path!r} maps to {repo_path!r}, which "
                    f"{seen_repo[repo_path]!r} already claims — two rows cannot "
                    "promise one destination"
                )
            seen_repo[repo_path] = manifest_path

    for digest, raw in read_digest_block(repo_root, EVIDENCE_MANIFEST):
        if raw == "README.md":
            # The branch's own README: hashed here, deliberately not restored.
            _claim(EVIDENCE_MANIFEST, raw, None)
            rows.append(EvidenceRow(digest=digest, manifest_path=raw, repo_path=None))
        elif raw.startswith(_COEVO_PREFIX):
            coevo_path = _confined(
                COEVO_DEST, raw[len(_COEVO_PREFIX) :], EVIDENCE_MANIFEST, raw
            )
            _claim(EVIDENCE_MANIFEST, raw, coevo_path)
            rows.append(
                EvidenceRow(digest=digest, manifest_path=raw, repo_path=coevo_path)
            )
        else:
            raise EvidenceError(
                f"{EVIDENCE_MANIFEST}: digest row {raw!r} is neither the branch "
                "README nor a 'coevo/' path — the restore map does not cover it"
            )

    # The slate manifest is created ONLY on Task 19.21's recovery path
    # (`tasks/phase-19.md`, 19.21 files in scope), so on the ratified LOSS path
    # it does not exist. Requiring it unconditionally made the whole
    # loss-acceptance route unreachable: the run died with usage error 2 inside
    # context construction, before `--complete` could accept the recorded loss
    # (Codex review, PR #348). Absent + a recorded loss is the expected shape;
    # absent + a recovery ruling is still a hard error.
    if (repo_root / SLATE_MANIFEST).is_file():
        for digest, raw in read_digest_block(repo_root, SLATE_MANIFEST):
            if not raw.startswith("./"):
                raise EvidenceError(
                    f"{SLATE_MANIFEST}: digest row {raw!r} is not a './' path — "
                    "the restore map does not cover it"
                )
            slate_path = _confined(SLATE_DEST, raw[2:], SLATE_MANIFEST, raw)
            _claim(SLATE_MANIFEST, f"{_SLATE_PREFIX}{raw[2:]}", slate_path)
            rows.append(
                EvidenceRow(
                    digest=digest,
                    manifest_path=f"{_SLATE_PREFIX}{raw[2:]}",
                    repo_path=slate_path,
                )
            )
    elif not slate_lost:
        raise EvidenceError(
            f"{SLATE_MANIFEST} is missing, and {ARTIFACTS_DOC} records no loss "
            "for the Phase-18 finalist slate. That manifest is created on Task "
            "19.21's RECOVERY path, so its absence beside a recovery ruling is a "
            "drifted tree, not a close state"
        )
    return tuple(rows)


def _slate_lost(repo_root: Path) -> bool:
    """Whether the committed ruling records the finalist slate as LOST.

    Read BEFORE the manifests, because on the loss path the slate manifest does
    not exist and the ruling is what says so.
    """

    ruling = read_slate_ruling(repo_root)
    return ruling is not None and ruling.lost


def read_pinned_sha(repo_root: Path) -> str:
    """The evidence commit's tip sha, read from the manifest row that owns it."""

    for line in _read_text(repo_root, EVIDENCE_MANIFEST).splitlines():
        if _PIN_ROW_MARKER in line:
            match = _SHA1_RE.search(line)
            if match is not None:
                return match.group(0)
    raise EvidenceError(
        f"{EVIDENCE_MANIFEST}: no pinned sha on the '{_PIN_ROW_MARKER}' row"
    )


def read_slate_ruling(repo_root: Path) -> Ruling | None:
    """The Task 19.21 raw-slate ruling, read from the registry document.

    ``None`` when the document records no dated ruling at all — which the
    availability leg reports as a FAILURE, because an unrecorded outcome is
    exactly the silent state the close forbids. Read rather than transcribed, so
    a later ruling change moves this command with it.
    """

    match = _RULING_RE.search(_read_text(repo_root, ARTIFACTS_DOC))
    if match is None:
        return None
    outcome = match.group(2)
    # Task 19.21 has exactly two outcomes. Treating an unrecognised one as
    # "not a loss" silently promoted a typo to RECOVERED and let it pass
    # --complete (Codex review, PR #348); the vocabulary is closed instead.
    if outcome not in _KNOWN_RULINGS:
        raise EvidenceError(
            f"{ARTIFACTS_DOC}: the Task 19.21 ruling records outcome "
            f"{outcome!r}, which is none of {sorted(_KNOWN_RULINGS)} — an "
            "unrecognised outcome is not a close state this command may read"
        )
    return Ruling(date=match.group(1), outcome=outcome)


def retained_in_tree_paths(repo_root: Path) -> list[str]:
    """The paths `EVIDENCE-MANIFEST.md` §3 enumerates as RETAINED in-tree.

    Task 19.22's consumer enumeration, taken empirically from a full pytest run
    and committed as the record of what may not move. It is the only committed
    INVENTORY of in-tree evidence this repository owns, which is what makes it
    the answer to "did a retained byte disappear?" — a question a walk of the
    working tree cannot ask itself, because a file and its sidecar deleted
    together simply shrink the walk.
    """

    text = _read_text(repo_root, EVIDENCE_MANIFEST)
    if _RETAINED_SECTION not in text:
        raise EvidenceError(
            f"{EVIDENCE_MANIFEST}: no '{_RETAINED_SECTION}' section — the "
            "committed in-tree inventory cannot be read"
        )
    section = text.split(_RETAINED_SECTION, 1)[1].split("\n## ", 1)[0]
    paths = [
        cells[0].strip("`")
        for cells in _table_rows(section)
        if len(cells) == 2 and cells[0].startswith("`") and cells[0].endswith("`")
    ]
    if not paths:
        raise EvidenceError(
            f"{EVIDENCE_MANIFEST} §3: no retained-path rows — the committed "
            "in-tree inventory cannot be read"
        )
    return paths


#: Git's own opt-out from partial-clone lazy fetching (git >= 2.41). The
#: DOCUMENTED clone for this repository is `git clone --filter=blob:none`
#: (README.md, docs/artifacts.md, docs/reading-guide.md), and on such a checkout
#: reading an omitted blob makes git fetch it from origin — verified on git
#: 2.43 under GIT_TRACE=1, which showed a `git fetch ... --filter=blob:none`
#: plus a promisor pack install and a maintenance run. That would put a network
#: call and a `.git` mutation inside a command whose contract is "offline and
#: read-only", and would hang on an actually offline machine. With this set the
#: read fails locally instead, which this command reports as ABSENT (Codex
#: review, PR #348).
_GIT_ENV: Final[dict[str, str]] = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes] | None:
    """Run a read-only git command with lazy fetching disabled, or ``None``."""

    try:
        return subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(repo_root), *args],
            capture_output=True,
            check=False,
            env=_GIT_ENV,
        )
    except OSError:
        return None


def git_tracked_sidecars(repo_root: Path) -> list[str] | None:
    """Every tracked ``*.sha256`` path, or ``None`` when there is no git index.

    Git is the only committed record of the in-tree sidecars that no manifest
    enumerates (the map-elites cells, the torch-probe artifacts). ``None`` is
    reported as its own ABSENT row rather than skipped: without an inventory the
    in-tree count is self-derived, and a self-derived count cannot notice a
    deletion.
    """

    completed = _git(repo_root, "ls-files", "-z", "--", f"*{_SIDECAR_SUFFIX}")
    if completed is None or completed.returncode != 0:
        return None
    return [name for name in completed.stdout.decode().split("\0") if name]


def git_tracked_under(repo_root: Path, pathspec: tuple[str, ...]) -> list[str] | None:
    """Every tracked path under ``pathspec``, or ``None`` when there is no index.

    The committed inventory of an in-tree registry family. ``None`` is reported
    as its own ABSENT row rather than skipped, for the same reason
    :func:`git_tracked_sidecars` does it: with no inventory the row can only
    confirm the anchors it was handed, and anchors cannot notice a deletion
    beside them.
    """

    if not pathspec:
        return []
    completed = _git(repo_root, "ls-files", "-z", "--", *pathspec)
    if completed is None or completed.returncode != 0:
        return None
    return [name for name in completed.stdout.decode().split("\0") if name]


def _git_blob(repo_root: Path, revision: str, path: str) -> bytes | None:
    """A blob out of a LOCAL git object, or ``None`` when it is not here.

    Offline by construction: :data:`_GIT_ENV` disables partial-clone lazy
    fetching, so on the documented blobless clone an omitted blob fails locally
    rather than being fetched from origin. ``None`` means the pinned commit's
    blob is not in this checkout, which is a reportable availability state, not
    an error.
    """

    completed = _git(repo_root, "cat-file", "blob", f"{revision}:{path}")
    if completed is None or completed.returncode != 0:
        return None
    return completed.stdout


# --------------------------------------------------------------------------- #
# Markdown readers — the committed verdicts that live in a report, not a JSON   #
# --------------------------------------------------------------------------- #


def _table_rows(text: str) -> Iterator[list[str]]:
    """Every markdown table row in ``text``, as its list of cells.

    A row is a line that both starts and ends with ``|`` after stripping — which
    excludes a table row QUOTED inside a blockquote (the reports quote their own
    rows in errata sections, and a quoted row is a citation of a number, not a
    second statement of it).
    """

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        yield [cell.strip() for cell in stripped[1:-1].split("|")]


def _normalize_label(cell: str) -> str:
    return cell.replace("**", "").replace("`", "").strip().lower()


_FRACTION: Final = re.compile(r"(?<![\d.])(\d+)\s*/\s*(\d+)(?![\d.])")


#: The two shapes the committed reports use to print a value BESIDE its
#: fraction: `**76.7%** (46/60)` (surrogate §3) and `90/96 = 0.9375`
#: (conviction §4). Reading only the fraction meant the adjacent figure could be
#: edited to contradict it while every recomputation row still read OK, and the
#: report a human opens visibly stated a different result (Codex review, PR
#: #348).
#:
#: Matched as ADJACENCY rather than by scanning the cell for numbers, which is
#: the important part: report cells also carry confidence intervals —
#: `0.05263 (23/437) [0.0353, 0.0777]` in the finalist report — and a bare scan
#: reads those bounds as figures contradicting the fraction. A verifier that
#: false-fails on a correct report is worse than a narrow one, because it
#: teaches its reader to ignore it.
_VALUE_THEN_FRACTION: Final = re.compile(
    r"(\d+(?:\.\d+)?)\s*%\**\s*\(\s*(\d+)\s*/\s*(\d+)\s*\)"
)
_FRACTION_THEN_VALUE: Final = re.compile(
    r"(\d+)\s*/\s*(\d+)\s*\**\s*=\s*\**\s*(\d*\.\d+)"
)
#: `12/50 (24.0%)` — the mirror of :data:`_VALUE_THEN_FRACTION`. Omitting it left
#: a shape that reads as validated and was not: the fraction still parsed, so the
#: recomputation row stayed OK while the percentage beside it said anything at
#: all — and the round-4 test asserted this very form as "benign", which
#: documented the gap as intentional (Codex review, PR #348).
_FRACTION_THEN_PERCENT: Final = re.compile(
    r"(\d+)\s*/\s*(\d+)\s*\**\s*\(\s*(\d+(?:\.\d+)?)\s*%"
)


def _displayed_drift(cell: str) -> list[str]:
    """Published values in ``cell`` that the fraction beside them does not give.

    Compared at the precision the report itself chose, because that is the claim
    it makes: `76.7%` asserts 46/60 to one decimal place, not to full precision.
    """

    drift: list[str] = []
    for shown, numerator, denominator, scale, suffix in (
        *((s, n, d, 100.0, "%") for s, n, d in _VALUE_THEN_FRACTION.findall(cell)),
        *((s, n, d, 100.0, "%") for n, d, s in _FRACTION_THEN_PERCENT.findall(cell)),
        *((s, n, d, 1.0, "") for n, d, s in _FRACTION_THEN_VALUE.findall(cell)),
    ):
        if not int(denominator):
            continue
        places = len(shown.partition(".")[2])
        value = int(numerator) / int(denominator)
        if round(value * scale, places) != float(shown):
            drift.append(f"shows {shown}{suffix} beside {numerator}/{denominator}")
    return drift


def fraction_from_report(repo_root: Path, rel: str, label: str) -> tuple[int, int]:
    """The ``n/d`` a report's table states for ``label`` — the committed verdict.

    The surrogate's decision channel and the conviction model's conversion
    accuracy have no machine-readable verdict artifact: the committed report IS
    the record (`training/reports/report-ballot-surrogate.md` §3;
    `training/reports/report-conviction-model.md` §4). Rather than transcribe
    those numbers into this file — a copied fact, which the phase's ruling puts
    below a generated one — they are read back out of the row that owns them, so
    a report edit that drifts the figure turns this command red.

    Every row whose first cell equals ``label`` and whose value cell states a
    fraction must state the SAME fraction; a row with no fraction (a sibling
    table quoting a bare percentage) is not a second statement and is skipped.
    Zero fractions, or two that disagree, raise.
    """

    found: dict[tuple[int, int], int] = {}
    contradictions: list[str] = []
    for cells in _table_rows(_read_text(repo_root, rel)):
        if len(cells) < 2 or _normalize_label(cells[0]) != label.lower():
            continue
        matches = _FRACTION.findall(cells[1])
        for numerator, denominator in matches:
            pair = (int(numerator), int(denominator))
            found[pair] = found.get(pair, 0) + 1
        contradictions.extend(_displayed_drift(cells[1]))
    if contradictions:
        raise EvidenceError(
            f"{rel}: the row labelled {label!r} states a value that its own "
            f"fraction does not produce ({'; '.join(contradictions)}) — the "
            "published figure and the fraction beside it must agree"
        )
    if not found:
        raise EvidenceError(
            f"{rel}: no table row labelled {label!r} states an 'n/d' fraction — "
            "the committed verdict this check compares against is gone"
        )
    if len(found) > 1:
        stated = ", ".join(f"{n}/{d}" for n, d in sorted(found))
        raise EvidenceError(
            f"{rel}: rows labelled {label!r} state DIFFERENT fractions "
            f"({stated}); the report disagrees with itself"
        )
    return next(iter(found))


#: The finalist erratum's multiplicity conclusion: `**α = 0.05 / 4 = 0.0125**`
#: and the arms it names as surviving that bar.
_ALPHA_STATEMENT: Final = re.compile(r"α\s*=\s*([\d.]+)\s*/\s*(\d+)\s*=\s*([\d.]+)")
_ENTRANT: Final = re.compile(r"`(p18-[A-Za-z0-9_-]+)`")
#: The erratum's conclusion is read as a whole PARAGRAPH split into clauses,
#: not as a window ending at the first "survive it". Stopping at that phrase
#: silently dropped any survivor the report named after it — "A and B survive
#: it; C also survives" would have been read as two survivors and passed
#: (Codex review, PR #348). Paragraph scoping is also what keeps "survive item
#: 1 untouched", sixty lines further down, out of the match.
_PARAGRAPH_END: Final = re.compile(r"\n[ \t]*\n")
#: Clause boundaries: `;` and a sentence-ending `.`. The lookbehind excludes the
#: decimal points inside the p-values each arm is quoted with.
_CLAUSE_SPLIT: Final = re.compile(r";|(?<=[A-Za-z)*])\.(?=\s|$)")
_SURVIVES: Final = re.compile(r"surviv|\bclears?\b", re.IGNORECASE)
#: A clause that REFUTES survival names its arm too, so it must not be read as a
#: claim: "`p18-imp-7f73929d` fails the multiplicity correction" is the arm that
#: does NOT survive.
_REFUTES: Final = re.compile(r"fail|\bnot\b|\bno longer\b", re.IGNORECASE)


def bonferroni_from_report(repo_root: Path) -> tuple[float, int, float, list[str]]:
    """The family-wise bar and surviving arms the finalist report publishes.

    Read rather than transcribed, for the same reason the fractions are: the
    erratum IS the committed record of this conclusion, so an edit to it must
    turn the command red instead of being quietly out-voted by a recomputation
    that never looks at it.

    The survivor list is taken from the window BETWEEN the alpha statement and
    the phrase that closes it, so an unrelated "only" elsewhere in a 2,600-line
    report cannot widen the span and drag in arms the sentence never named.
    """

    text = _read_text(repo_root, FINALIST_REPORT)
    alpha = _ALPHA_STATEMENT.search(text)
    if alpha is None:
        raise EvidenceError(
            f"{FINALIST_REPORT}: no 'α = <alpha> / <family> = <bar>' statement — "
            "the multiplicity conclusion this check compares against is gone"
        )
    paragraph = _PARAGRAPH_END.split(text[alpha.end() :], 1)[0]
    claims = [
        clause
        for clause in _CLAUSE_SPLIT.split(paragraph)
        if _SURVIVES.search(clause) and not _REFUTES.search(clause)
    ]
    if not claims:
        raise EvidenceError(
            f"{FINALIST_REPORT}: the family-wise bar is stated but the paragraph "
            "carrying it asserts no surviving arm"
        )
    survivors = sorted({arm for clause in claims for arm in _ENTRANT.findall(clause)})
    if not survivors:
        raise EvidenceError(
            f"{FINALIST_REPORT}: the survivor clause names no arm; "
            "the report's own list of surviving arms is unreadable"
        )
    return float(alpha.group(1)), int(alpha.group(2)), float(alpha.group(3)), survivors


# --------------------------------------------------------------------------- #
# Leg 1 — per-class sidecar / sha verification                                 #
# --------------------------------------------------------------------------- #


def walk_sidecars(repo_root: Path) -> list[Path]:
    """Every ``*.sha256`` in the working tree, skipping caches and build output."""

    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = sorted(name for name in dirnames if name not in WALK_SKIP_DIRS)
        for filename in sorted(filenames):
            if filename.endswith(_SIDECAR_SUFFIX):
                found.append(Path(dirpath) / filename)
    return found


def sidecar_targets(sidecar: Path) -> list[tuple[str, str]]:
    """A sidecar's ``(digest, name)`` rows; names are relative to its directory.

    Covers both shapes the repo ships: the one-line ``weights.json.sha256``
    beside a genome, and the multi-line per-tranche
    ``recordings-manifest*.sha256`` that hashes a whole recording tree with
    ``./``-prefixed paths. A row that escapes the sidecar's own directory is
    refused rather than followed.
    """

    rows: list[tuple[str, str]] = []
    for lineno, line in enumerate(
        sidecar.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        match = _DIGEST_ROW.match(line)
        if match is None:
            raise EvidenceError(
                f"{sidecar}:{lineno}: not a '<sha256>  <path>' row: {line!r}"
            )
        name = match.group(2)
        if name.startswith("./"):
            name = name[2:]
        if name.startswith("/") or ".." in Path(name).parts:
            raise EvidenceError(
                f"{sidecar}:{lineno}: target {name!r} escapes the sidecar's "
                "directory; refusing to follow it"
            )
        rows.append((match.group(1), name))
    if not rows:
        raise EvidenceError(f"{sidecar}: no digest rows — an empty sidecar")
    return rows


def _verify_sidecar(sidecar: Path, repo_root: Path) -> tuple[int, list[str]]:
    """Verify every target a sidecar names; returns ``(checked, failures)``."""

    failures: list[str] = []
    checked = 0
    for digest, name in sidecar_targets(sidecar):
        target = sidecar.parent / name
        rel = _relative(target, repo_root)
        if not target.is_file():
            failures.append(f"{rel}: named by {_relative(sidecar, repo_root)}, absent")
            continue
        checked += 1
        actual = sha256_file(target)
        if actual != digest:
            failures.append(
                f"{rel}: sha256 {actual[:12]}… != sidecar {digest[:12]}… "
                f"({_relative(sidecar, repo_root)})"
            )
    return checked, failures


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def run_sidecars(ctx: Context) -> LegResult:
    """Per-class sha verification: in-tree offline, evidence-branch on restore."""

    # The FULL moved set classifies what is not in-tree; the PROMISED subset is
    # what a restore is required to produce (a recorded loss is not a promise).
    moved_paths = {row.repo_path for row in ctx.evidence if row.repo_path is not None}
    moved_sidecars = sorted(
        row.repo_path
        for row in ctx.evidence
        if row.repo_path is not None
        and row.repo_path.endswith(_SIDECAR_SUFFIX)
        and not ctx.is_lost(row)
    )
    on_disk = walk_sidecars(ctx.repo_root)
    in_tree = [
        path for path in on_disk if _relative(path, ctx.repo_root) not in moved_paths
    ]

    rows: list[CheckRow] = []

    # --- class IN-TREE: verifies on a bare checkout, no network, no restore. ---
    in_tree_targets = 0
    in_tree_failures: list[str] = []
    for sidecar in in_tree:
        checked, failures = _verify_sidecar(sidecar, ctx.repo_root)
        in_tree_targets += checked
        in_tree_failures.extend(failures)
    rows.append(
        CheckRow(
            name="sidecars[IN-TREE]",
            measured=(
                f"{len(in_tree)} sidecars / {in_tree_targets} targets verified, "
                f"{len(in_tree_failures)} failure(s)"
            ),
            # Deliberately NOT "<n> sidecars, as expected": a walk of the working
            # tree cannot state its own expected size. A file and its sidecar
            # deleted together shrink the walk and every count derived from it,
            # so the inventory is checked against a committed record below —
            # this row only says that what IS here hashes correctly.
            committed="every sidecar present hashes its target (inventory: below)",
            source="the working tree (every *.sha256 outside caches/build output)",
            status="FAIL" if in_tree_failures else "OK",
            detail="\n".join(in_tree_failures[:10]),
        )
    )

    # --- the in-tree INVENTORY, from the two committed records that own it. ---
    tracked = git_tracked_sidecars(ctx.repo_root)
    if tracked is None:
        rows.append(
            CheckRow(
                name="sidecars[IN-TREE] inventory",
                measured=f"{len(in_tree)} on disk; no git index here",
                committed="`git ls-files '*.sha256'` — the committed inventory",
                source="git (the only record covering non-manifest sidecars)",
                status="ABSENT",
                detail=(
                    "without an inventory the in-tree count is self-derived, and "
                    "a self-derived count cannot notice a deletion — so this is "
                    "reported, never assumed clean"
                ),
            )
        )
    else:
        expected = {path for path in tracked if path not in moved_paths}
        found = {_relative(path, ctx.repo_root) for path in in_tree}
        missing = sorted(expected - found)
        extra = sorted(found - expected)
        rows.append(
            CheckRow(
                name="sidecars[IN-TREE] inventory",
                measured=f"{len(found)} on disk, {len(missing)} tracked but absent",
                committed=f"{len(expected)} tracked in-tree sidecars",
                source="`git ls-files '*.sha256'` minus the moved set",
                status="FAIL" if missing else "OK",
                detail="\n".join(
                    part
                    for part in (
                        "tracked but absent: " + ", ".join(missing[:10])
                        if missing
                        else "",
                        # Untracked extras are local state, not a defect —
                        # reported so the count is explainable, never failed on.
                        f"{len(extra)} untracked sidecar(s) on disk: "
                        + ", ".join(extra[:5])
                        if extra
                        else "",
                    )
                    if part
                ),
            )
        )

    # --- the RETAINED in-tree evidence the prune's own enumeration names. ---
    retained = retained_in_tree_paths(ctx.repo_root)
    # `.is_file()`, not `.exists()`: a directory created at a retained byte's
    # pathname satisfies `exists()` and would report the inventory complete
    # (Codex review, PR #348). §3 enumerates files, so anything else is missing.
    retained_missing = [
        rel for rel in retained if not (ctx.repo_root / COEVO_DEST / rel).is_file()
    ]
    rows.append(
        CheckRow(
            name="retained in-tree evidence",
            measured=(
                f"{len(retained) - len(retained_missing)}/{len(retained)} present"
            ),
            committed=f"{len(retained)} paths the prune retained",
            source=f"{EVIDENCE_MANIFEST} §3 (the consumer enumeration)",
            status="FAIL" if retained_missing else "OK",
            detail=(
                "absent: " + ", ".join(retained_missing[:10])
                if retained_missing
                else ""
            ),
        )
    )

    # --- class EVIDENCE-BRANCH: the sidecars whose bytes 19.22 moved. ---
    present = [path for path in moved_sidecars if (ctx.repo_root / path).is_file()]
    restored = set(present)
    absent = [path for path in moved_sidecars if path not in restored]
    moved_failures: list[str] = []
    moved_targets = 0
    by_path = {row.repo_path: row for row in ctx.evidence if row.repo_path is not None}
    for rel in present:
        path = ctx.repo_root / rel
        # Two hashes, both required: the sidecar's OWN digest against the
        # manifest (the restore put back the right sidecar) and the targets it
        # names (the sidecar still describes the bytes beside it). A weight in
        # one place and its sidecar in the other is the manifest error
        # EVIDENCE-MANIFEST.md §5 exists to make impossible.
        actual = sha256_file(path)
        if actual != by_path[rel].digest:
            moved_failures.append(
                f"{rel}: sha256 {actual[:12]}… != manifest {by_path[rel].digest[:12]}…"
            )
            continue
        checked, failures = _verify_sidecar(path, ctx.repo_root)
        moved_targets += checked
        moved_failures.extend(failures)
    if moved_failures:
        moved_status: Status = "FAIL"
    elif absent and not present:
        moved_status = "ABSENT"
    elif absent:
        moved_status = "FAIL"
    else:
        moved_status = "OK"
    rows.append(
        CheckRow(
            name="sidecars[EVIDENCE-BRANCH]",
            measured=(
                f"{len(present)} of {len(moved_sidecars)} restored; "
                f"{moved_targets} target(s) verified; {len(absent)} "
                "EVIDENCE-BRANCH-ABSENT"
            ),
            committed=(
                f"{len(moved_sidecars)} sidecars moved to the evidence commit "
                f"@ {ctx.pinned_sha[:12]}…"
            ),
            source=f"{EVIDENCE_MANIFEST} §4/§5/§7",
            status=moved_status,
            detail=(
                "\n".join(moved_failures[:10])
                if moved_failures
                else (
                    "not restored on this checkout — run "
                    "`bash scripts/fetch_evidence.sh` to place them, then re-run"
                    if absent
                    else ""
                )
            ),
        )
    )

    # --- class EVIDENCE-BRANCH: the whole payload, not only its sidecars. ---
    # The PROMISED set only. Bytes a committed ruling records as LOST were never
    # promised archival availability, so they are subtracted here rather than
    # relabelled downstream: with the coevo payload restored and a lost slate
    # absent, an aggregate that still counted the slate would read PARTIAL and
    # fail the close on bytes nobody promised (Codex review, PR #348).
    promised = [
        (row.repo_path, row.digest)
        for row in ctx.evidence
        if row.repo_path is not None and not ctx.is_lost(row)
    ]
    payload_present = 0
    payload_failures: list[str] = []
    for repo_path, digest in promised:
        path = ctx.repo_root / repo_path
        if not path.is_file():
            continue
        payload_present += 1
        actual = sha256_file(path)
        if actual != digest:
            payload_failures.append(
                f"{repo_path}: sha256 {actual[:12]}… != manifest {digest[:12]}…"
            )
    payload_absent = len(promised) - payload_present
    if payload_failures:
        payload_status: Status = "FAIL"
    elif payload_absent == len(promised):
        payload_status = "ABSENT"
    elif payload_absent:
        payload_status = "FAIL"
    else:
        payload_status = "OK"
    rows.append(
        CheckRow(
            name="evidence payload",
            measured=(
                f"{payload_present} of {len(promised)} restored and hashed; "
                f"{payload_absent} EVIDENCE-BRANCH-ABSENT"
            ),
            committed=f"{len(promised)} PROMISED files on {ctx.pinned_sha[:12]}…",
            source=f"{EVIDENCE_MANIFEST} §7 + {SLATE_MANIFEST} §7",
            status=payload_status,
            detail=(
                "\n".join(payload_failures[:10])
                if payload_failures
                else (
                    "not restored on this checkout — run "
                    "`bash scripts/fetch_evidence.sh` to place them, then re-run"
                    if payload_absent
                    else ""
                )
            ),
        )
    )

    # --- and, separately, whatever a ruling records as LOST. ---
    lost_rows = [row for row in ctx.evidence if ctx.is_lost(row)]
    if lost_rows:
        ruling = ctx.slate_ruling
        assert ruling is not None  # lost_prefixes is empty without a ruling
        rows.append(
            CheckRow(
                name="evidence payload[LOST]",
                measured=(
                    f"{len(lost_rows)} file(s) recorded LOST "
                    f"({ruling.outcome}, {ruling.date})"
                ),
                committed=f"{ruling.outcome} — a ratified loss, not a promise",
                source=f"{ARTIFACTS_DOC} (the Task 19.21 ruling)",
                status="INFO",
                detail=(
                    "the bytes are gone and the record is not; a recorded loss "
                    "is a valid close state, which is why --complete accepts it"
                ),
            )
        )

    # --- the branch's own README: hashed by the manifest, never restored. ---
    readme_rows = [row for row in ctx.evidence if row.repo_path is None]
    if len(readme_rows) != 1:
        raise EvidenceError(
            f"{EVIDENCE_MANIFEST}: expected exactly one non-restored row (the "
            f"branch README), found {len(readme_rows)}"
        )
    readme = readme_rows[0]
    blob = _git_blob(ctx.repo_root, ctx.pinned_sha, readme.manifest_path)
    if blob is None:
        readme_status: Status = "ABSENT"
        readme_measured = "the pinned commit object is not in this checkout"
    else:
        actual = hashlib.sha256(blob).hexdigest()
        readme_status = "OK" if actual == readme.digest else "FAIL"
        readme_measured = f"sha256 {actual[:12]}…"
    rows.append(
        CheckRow(
            name="evidence branch README",
            measured=readme_measured,
            committed=f"sha256 {readme.digest[:12]}…",
            source=f"{EVIDENCE_MANIFEST} §7 (row 'README.md')",
            status=readme_status,
            detail=(
                ""
                if readme_status != "ABSENT"
                else (
                    "branch metadata, checked straight out of the commit — "
                    "`bash scripts/fetch_evidence.sh` pins it locally"
                )
            ),
        )
    )
    return LegResult(leg="sidecars", rows=tuple(rows))


# --------------------------------------------------------------------------- #
# Leg 2 — corpus reconstruction                                                #
# --------------------------------------------------------------------------- #


def replay_sets(repo_root: Path) -> list[Path]:
    """Every committed replay set (a directory holding ``replay-seed-*.jsonl``)."""

    sets: list[Path] = []
    for root_rel in REPLAY_ROOTS:
        root = repo_root / root_rel
        if not root.is_dir():
            raise EvidenceError(f"{root_rel} is missing — the corpus cannot be walked")
        for child in sorted(root.iterdir()):
            # A set is DECLARED by its MANIFEST.md, not by the replays still on
            # disk. Requiring a replay file meant a set whose games were all
            # deleted vanished from the walk entirely — so the manifest's own
            # missing-seed check never ran and `--complete` certified a checkout
            # missing a whole committed set (Codex review, PR #348). A declared
            # set with nothing left in it is now handed to the verifier, which
            # reports every absent seed.
            if child.is_dir() and (
                (child / _SET_MANIFEST).is_file() or any(child.glob(_REPLAY_GLOB))
            ):
                sets.append(child)
    if not sets:
        raise EvidenceError(
            f"no committed replay sets under {', '.join(REPLAY_ROOTS)} — "
            "there is nothing to reconstruct"
        )
    return sets


def _seed_of(path: Path) -> int:
    return int(path.stem[len("replay-seed-") :])


def sampled_seeds(set_dir: Path, limit: int) -> list[int]:
    """A deterministic, evenly-spread subset of a set's seeds (``--fast``).

    Evenly spread rather than the first ``limit``: a drift from an engine change
    moves every chain, but a sample taken off one end of the seed order would
    read as a full-coverage claim while covering one corner of the set.
    """

    seeds = sorted(_seed_of(path) for path in set_dir.glob(_REPLAY_GLOB))
    if len(seeds) <= limit:
        return seeds
    step = len(seeds) / limit
    return [seeds[int(index * step)] for index in range(limit)]


def mirror_sampled_set(set_dir: Path, seeds: Sequence[int], dest: Path) -> None:
    """Mirror ``seeds`` of ``set_dir`` into ``dest`` so the real verifier runs on it.

    ``--fast`` samples by handing the unmodified verifier a smaller set, rather
    than by reimplementing a per-seed walk: the state-hash chain check, the
    meeting pre-hash cross-check and the manifest completeness check all still
    run, over fewer games. The replays and the set's auxiliary files are
    SYMLINKED (nothing is copied and nothing in the repo is written); only
    ``MANIFEST.md`` is rewritten, filtered to the sampled rows so the verifier's
    completeness check stays meaningful instead of reporting every unsampled
    seed missing.
    """

    keep = set(seeds)
    for seed in sorted(keep):
        source = set_dir / f"replay-seed-{seed}.jsonl"
        os.symlink(source, dest / source.name)
    for child in sorted(set_dir.iterdir()):
        if child.name.startswith("replay-seed-") or child.name == "MANIFEST.md":
            continue
        if child.is_file():
            os.symlink(child, dest / child.name)
    manifest = set_dir / "MANIFEST.md"
    if not manifest.is_file():
        return
    lines: list[str] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            first = stripped.strip("|").split("|", 1)[0].strip()
            if first.isdigit() and int(first) not in keep:
                continue
        lines.append(line)
    (dest / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_corpus(ctx: Context) -> LegResult:
    """Replay reconstruction + the committed fit-corpus identity fingerprint."""

    rows: list[CheckRow] = []
    notes: list[str] = []
    for set_dir in replay_sets(ctx.repo_root):
        rel = _relative(set_dir, ctx.repo_root)
        total = len(list(set_dir.glob(_REPLAY_GLOB)))
        # Nothing to sample: a set that declares seeds but holds no replays is
        # walked in FULL in every mode, so --fast cannot turn an empty set into
        # a vacuous pass.
        if ctx.fast and total:
            seeds = sampled_seeds(set_dir, FAST_SAMPLE_PER_SET)
            with tempfile.TemporaryDirectory(prefix="verify-ml-evidence-") as tmp:
                dest = Path(tmp)
                mirror_sampled_set(set_dir, seeds, dest)
                failures = verify_samples(dest)
            measured = (
                f"{len(seeds) - len(failures)}/{len(seeds)} reconstructed "
                f"(SAMPLED from {total}; seeds {', '.join(str(s) for s in seeds)})"
            )
            committed = f"{total} committed replays (--fast sampled {len(seeds)})"
        else:
            failures = verify_samples(set_dir)
            measured = f"{total - len(failures)}/{total} reconstructed"
            committed = f"{total} committed replays"
            if not total:
                measured = (
                    f"NO REPLAYS ON DISK; {len(failures)} declared seed(s) absent"
                )
                committed = f"{rel}/{_SET_MANIFEST} declares this set"
        rows.append(
            CheckRow(
                name=f"corpus reconstruction: {rel}",
                measured=measured,
                committed=committed,
                source=f"{rel}/MANIFEST.md via scripts/_verify_samples.py",
                status="FAIL" if failures else "OK",
                detail="\n".join(failure.render() for failure in failures[:10]),
            )
        )
    if ctx.fast:
        notes.append(
            "--fast: the reconstruction walked a SAMPLE of each set (seeds listed "
            f"per row, {FAST_SAMPLE_PER_SET} per set). This is not a full-corpus "
            "verification; drop --fast, or run `bash scripts/verify_samples.sh`, "
            "for the whole walk."
        )

    # The fit-corpus identity the surrogate artifact commits: one digest over
    # every replay byte plus the split and the provenance, so it moves when ANY
    # recorded game, the by-game split, or the manifest moves. Always full — it
    # only hashes, so --fast has nothing to save here.
    from training.surrogate.runner import fit_corpus_fingerprint

    fit_corpus = json.loads(
        _read_text(ctx.repo_root, f"{SURROGATE_DIR}/fit-corpus.json")
    )
    committed_sha = str(fit_corpus["corpus_sha256"])
    measured_sha = fit_corpus_fingerprint(ctx.repo_root / CORPUS_SET)
    rows.append(
        CheckRow(
            name="fit-corpus identity fingerprint",
            measured=f"sha256 {measured_sha[:16]}…",
            committed=f"sha256 {committed_sha[:16]}…",
            source=f"{SURROGATE_DIR}/fit-corpus.json (corpus_sha256)",
            status="OK" if measured_sha == committed_sha else "FAIL",
            detail=(
                ""
                if measured_sha == committed_sha
                else (
                    f"{CORPUS_SET} no longer fingerprints to the corpus the "
                    "committed surrogate weights were fitted on"
                )
            ),
        )
    )
    return LegResult(leg="corpus", rows=tuple(rows), notes=tuple(notes))


# --------------------------------------------------------------------------- #
# Leg 3 — surrogate / conviction / composed recomputation                      #
# --------------------------------------------------------------------------- #


#: The comparison tolerance for a recomputed channel — the same absolute
#: tolerance the committed pin tests use (``tests/training/test_surrogate_runner.py``).
#: These are inferences from FIXED committed weights, so anything looser would
#: stop being a pin, and anything tighter would read platform libm variance as
#: evidence drift.
FLOAT_TOLERANCE: Final = 1e-12

#: The three adoption constraints the composed verdict was adopted with, in
#: order and IN FULL. Carried metadata: the fidelity report holds nothing that
#: could re-derive them, so the identity row splices them from the committed
#: side — which means a transcription pin here is the only thing that can catch
#: an edit. Comparing only the key before the ":" let the substantive guidance
#: drift silently while the verifier reported every field identical, and that
#: guidance is surfaced verbatim to campaign meters by `training/coevo/driver.py`
#: (Codex review, PR #348). Transcribed deliberately, and the whole string is
#: compared.
_COMPOSED_ADOPTION_CONSTRAINTS: Final[tuple[str, ...]] = (
    "composed-provenance-validity[all-arms,9p2i]: every composed-path probe arm fails the recorded validity gate on cost_and_provenance_exact (no model row on a zero-LLM meeting path) — composed-substrate probe reads are diagnostic-grade, never validity-passing evidence",
    "prescreen-substrate-divergence-shape[fsm-baseline+emergency,9p2i]: predicted floors PASS while the composed substrate mints 0 flags in bytes — a pre-screen PASS is real-path spend advice ONLY; pair every gating use with a recorded-bytes floor read",
    "emergency-predicted-supply-above-bar[emergency,9p2i]: forced-emergency predicted-supply delta +29.5% >= the 25% materiality bar with recorded 0.0 — the laundering shape, validity-gated out of the machinery's findings",
)


def _float_row(
    name: str,
    measured: float,
    committed: float,
    source: str,
    *,
    census: str = "",
    note: str = "",
) -> CheckRow:
    """One recomputed float against its committed verdict.

    ``census`` is the integer count behind the ratio (``46/60``), printed beside
    the float because a ratio is easier to argue with than a decimal; ``note``
    is standing context and is printed whether the row passes or fails.
    """

    return CheckRow(
        name=name,
        measured=f"{measured:.10f}" + (f"  ({census})" if census else ""),
        committed=f"{committed:.10f}",
        source=source,
        status="OK" if abs(measured - committed) <= FLOAT_TOLERANCE else "FAIL",
        detail=note,
    )


def run_recompute(ctx: Context) -> LegResult:
    """Re-derive the three instruments from the FROZEN committed weights.

    Wraps the existing entry points rather than reimplementing a metric: the
    surrogate channels come from the frozen predictor over the committed
    held-out split (the ``BallotSurrogateModel(predictor=…)`` reload path), the
    conviction channels from ``run_conviction_fidelity`` + ``decide_conviction_go``,
    and the composed channels from ``run_composed_fidelity`` + ``decide_composed_go``.
    Nothing refits and nothing retrains.
    """

    from training.composed_runner import (
        build_composed_manifest,
        decide_composed_go,
        load_composed_manifest,
        load_composed_verdict,
        run_composed_fidelity,
    )
    from training.conviction.dataset import build_conviction_table
    from training.conviction.fidelity import (
        decide_conviction_go,
        load_conviction_verdict,
        run_conviction_fidelity,
    )
    from training.conviction.model import load_conviction_model_artifact
    from training.surrogate.ballots import (
        BallotSurrogateModel,
        load_ballot_predictor_artifact,
    )
    from training.surrogate.dataset import build_meeting_table
    from training.surrogate.fidelity import build_meeting_views

    corpus = ctx.repo_root / CORPUS_SET
    surrogate_dir = ctx.repo_root / SURROGATE_DIR
    conviction_dir = ctx.repo_root / CONVICTION_DIR
    composed_dir = ctx.repo_root / COMPOSED_DIR
    rows: list[CheckRow] = []

    # ---- the ballot surrogate: the RANKING channel kept, the DECISION arm's
    # all-SKIP census retired (training/README.md §2a). ----
    table = build_meeting_table(corpus)
    if table.splits is None:
        raise EvidenceError(
            f"{CORPUS_SET} ships no committed splits.json; the surrogate numbers "
            "are a single held-out evaluation and cannot be re-derived without it"
        )
    test_seeds = frozenset(table.splits.test)
    predictor, surrogate_sha = load_ballot_predictor_artifact(surrogate_dir)
    frozen = BallotSurrogateModel(table, predictor=predictor)
    test_views = [
        view for view in build_meeting_views(table) if view.seed in test_seeds
    ]
    top1_hits = 0
    ejections = 0
    correct_decisions = 0
    for view in test_views:
        prediction = frozen.predict(view)
        if view.is_ejection:
            ejections += 1
            if prediction.ranking[0] == view.ejected:
                top1_hits += 1
        if prediction.ejected == view.ejected:
            correct_decisions += 1

    top1_num, top1_den = fraction_from_report(
        ctx.repo_root, SURROGATE_REPORT, "top-1 (ejected target ranked first)"
    )
    rows.append(
        _float_row(
            "surrogate top-1 (ranking channel)",
            top1_hits / ejections,
            top1_num / top1_den,
            f"{SURROGATE_REPORT} §3 ('top-1 (ejected target ranked first)' "
            f"= {top1_num}/{top1_den})",
            census=f"{top1_hits}/{ejections}",
        )
    )
    decision_num, decision_den = fraction_from_report(
        ctx.repo_root, SURROGATE_REPORT, "SKIP-vs-eject decision accuracy"
    )
    rows.append(
        _float_row(
            "surrogate SKIP-vs-eject decision accuracy",
            correct_decisions / len(test_views),
            decision_num / decision_den,
            f"{SURROGATE_REPORT} §3 ('SKIP-vs-eject decision accuracy' "
            f"= {decision_num}/{decision_den})",
            census=f"{correct_decisions}/{len(test_views)}",
        )
    )

    # ---- the conviction model: the WHETHER channel. ----
    conviction_table = build_conviction_table(corpus)
    model, conviction_sha = load_conviction_model_artifact(conviction_dir)
    conviction_report, _ = run_conviction_fidelity(conviction_table, model=model)
    conviction_rederived = decide_conviction_go(
        conviction_report, weights_sha256=conviction_sha
    )
    conviction_committed = load_conviction_verdict(conviction_dir)
    rows.append(
        _float_row(
            "conviction flag-count Spearman",
            conviction_report.flag_spearman,
            conviction_committed.flag_spearman,
            f"{CONVICTION_DIR}/verdict.json (flag_spearman)",
        )
    )
    conversion_num, conversion_den = fraction_from_report(
        ctx.repo_root, CONVICTION_REPORT, "conversion accuracy"
    )
    rows.append(
        _float_row(
            "conviction conversion-label accuracy",
            conviction_report.conversion_accuracy,
            conversion_num / conversion_den,
            f"{CONVICTION_REPORT} §4 ('conversion accuracy' "
            f"= {conversion_num}/{conversion_den})",
            note=(
                "this is CONVERSION-LABEL accuracy, never a meeting decision "
                "number (training/README.md §2, the terminology ruling)"
            ),
        )
    )
    rows.append(
        _verdict_identity_row(
            "conviction verdict.json reproduces",
            rederived=conviction_rederived.model_dump(),
            committed=conviction_committed.model_dump(),
            repo_root=ctx.repo_root,
            # The committed artifact stores the REPO-RELATIVE corpus path; this
            # run built its table from an absolute one, so the identity field is
            # resolved on both sides and every other field compares raw (the
            # test_committed_verdict_reproduces_from_the_frozen_weights idiom).
            path_fields=("replay_set_dir",),
            source=f"{CONVICTION_DIR}/verdict.json",
        )
    )

    # ---- the composed runner: the FROZEN optional-diagnostic composition. ----
    composed_report = run_composed_fidelity(
        corpus,
        conviction_artifact_dir=conviction_dir,
        surrogate_artifact_dir=surrogate_dir,
    )
    composed_committed = load_composed_verdict(composed_dir)
    composed_rederived = decide_composed_go(
        composed_report,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
    )
    rows.append(
        _float_row(
            "composed decision accuracy",
            composed_report.decision_accuracy,
            composed_committed.decision_accuracy,
            f"{COMPOSED_DIR}/verdict.json (decision_accuracy)",
        )
    )
    rows.append(
        _float_row(
            "composed exact-outcome match",
            composed_report.exact_outcome_match,
            composed_committed.exact_outcome_match,
            f"{COMPOSED_DIR}/verdict.json (exact_outcome_match)",
        )
    )
    rows.append(
        _float_row(
            "composed convicting top-1",
            composed_report.convicting_top1,
            composed_committed.convicting_top1,
            f"{COMPOSED_DIR}/verdict.json (convicting_top1)",
        )
    )
    # ``adoption_constraints`` is the Goodhart leg's CARRIED metadata: the
    # re-derived verdict cannot produce it (nothing in the fidelity report holds
    # it), so it is spliced from the committed side before the identity compare
    # — and then pinned by name in its own row below, because excluding it
    # outright meant the three named constraints could be edited or emptied and
    # the identity row would still read "all fields identical" (Codex review,
    # PR #348). This is exactly what tests/training/test_composed_runner.py does.
    composed_rederived_dump = composed_rederived.model_dump()
    composed_committed_dump = composed_committed.model_dump()
    composed_rederived_dump["adoption_constraints"] = composed_committed_dump[
        "adoption_constraints"
    ]
    rows.append(
        _verdict_identity_row(
            "composed verdict.json reproduces",
            rederived=composed_rederived_dump,
            committed=composed_committed_dump,
            repo_root=ctx.repo_root,
            path_fields=("replay_set_dir",),
            source=f"{COMPOSED_DIR}/verdict.json",
        )
    )
    carried = tuple(str(item) for item in composed_committed.adoption_constraints)
    constraint_drift = [
        f"[{index}] committed {committed_item!r} != pinned {pinned!r}"
        for index, (committed_item, pinned) in enumerate(
            zip_longest(carried, _COMPOSED_ADOPTION_CONSTRAINTS)
        )
        if committed_item != pinned
    ]
    rows.append(
        CheckRow(
            name="composed adoption constraints",
            measured=(
                f"{len(carried)} carried, compared in full: "
                + ", ".join(item.split(":", 1)[0] for item in carried)
                if carried
                else "none carried"
            ),
            committed=(
                f"{len(_COMPOSED_ADOPTION_CONSTRAINTS)} constraints, full text pinned"
            ),
            source=f"{COMPOSED_DIR}/verdict.json (adoption_constraints)",
            status="OK" if not constraint_drift else "FAIL",
            detail="\n".join(constraint_drift[:5]),
        )
    )

    # ---- the manifest that pins the whole composed configuration. ----
    # Checking only the two weight hashes left every OPERATING PARAMETER in this
    # file unverified: `decision_threshold`, `skip_confidence_threshold`,
    # `replay_set_dir`, `corpus_set` and the two verdicts could each drift while
    # the recomputation above quietly went on using the imported constants and
    # the committed corpus — so the command could certify a configuration that
    # contradicts the computation it had just performed (Codex review, PR #348).
    # Both sides go through the product's OWN typed surface rather than a dict
    # this file assembles. Hand-building the expected mapping meant the verifier
    # could certify a manifest the product refuses to construct: `ComposedManifest`
    # pins `conviction_verdict` to `Literal["GO"]` and forbids extra fields, and
    # `build_composed_manifest()` rejects a non-GO conviction component outright,
    # none of which an untyped dict comparison applies (Codex review, PR #348).
    # Building through it also means nothing here is transcribed at all — the
    # thresholds and the corpus come from the constructor's own constants.
    committed_manifest = load_composed_manifest(composed_dir)
    try:
        rederived_manifest = build_composed_manifest(
            composed_rederived, conviction_verdict=conviction_rederived
        )
    except ValueError as error:  # the product refuses this composition
        raise EvidenceError(
            f"{COMPOSED_DIR}/manifest.json cannot be re-derived: {error}"
        ) from error
    rows.append(
        _verdict_identity_row(
            "composed manifest.json reproduces",
            rederived=rederived_manifest.model_dump(),
            committed=committed_manifest.model_dump(),
            repo_root=ctx.repo_root,
            path_fields=("replay_set_dir",),
            source=f"{COMPOSED_DIR}/manifest.json",
        )
    )
    for label, measured_sha, committed_sha, source in (
        (
            "surrogate weights sha256",
            surrogate_sha,
            committed_manifest.surrogate_weights_sha256,
            f"{COMPOSED_DIR}/manifest.json",
        ),
        (
            "conviction weights sha256",
            conviction_sha,
            committed_manifest.conviction_weights_sha256,
            f"{COMPOSED_DIR}/manifest.json",
        ),
    ):
        rows.append(
            CheckRow(
                name=label,
                measured=f"{measured_sha[:16]}…",
                committed=f"{committed_sha[:16]}…",
                source=source,
                status="OK" if measured_sha == committed_sha else "FAIL",
            )
        )
    return LegResult(leg="recompute", rows=tuple(rows))


def _verdict_identity_row(
    name: str,
    *,
    rederived: dict[str, object],
    committed: dict[str, object],
    repo_root: Path,
    path_fields: tuple[str, ...],
    source: str,
) -> CheckRow:
    """The strongest pin: the whole committed verdict object, field for field.

    ``path_fields`` name the corpus-identity fields the committed artifact
    stores REPO-RELATIVE while a live run produces an absolute path. They are
    normalized and then COMPARED — not dropped. Dropping them meant a verdict
    pointing at a different corpus still read "all fields identical", which is
    the opposite of what an identity pin is for (Codex review, PR #348). Every
    other field, including carried metadata, compares raw.
    """

    keys = set(rederived) | set(committed)
    drifted: list[str] = []
    for key in sorted(keys):
        ours, theirs = rederived.get(key), committed.get(key)
        if key in path_fields:
            # Same corpus, spelled two ways: resolve both against the repo root.
            if not (isinstance(ours, str) and isinstance(theirs, str)):
                drifted.append(key)
                continue
            if (repo_root / ours).resolve() != (repo_root / theirs).resolve():
                drifted.append(key)
            continue
        if ours != theirs:
            drifted.append(key)
    return CheckRow(
        name=name,
        measured=f"{len(keys) - len(drifted)}/{len(keys)} fields identical",
        committed=(
            f"{len(keys)} fields ({len(path_fields)} corpus-path field(s) "
            "compared after resolving)"
        ),
        source=source,
        status="OK" if not drifted else "FAIL",
        detail="\n".join(
            f"{key}: re-derived {rederived.get(key)!r} != committed "
            f"{committed.get(key)!r}"
            for key in drifted[:10]
        ),
    )


# --------------------------------------------------------------------------- #
# Leg 4 — the paired finalist statistics (via scripts/paired_stats, 19.20)     #
# --------------------------------------------------------------------------- #

#: The erratum table's arm rows: entrant, n, "wins arm / comparator", delta,
#: "b/c", exact p, and the two Wilson intervals.
_ERRATUM_ARM: Final = re.compile(r"^`(p18-imp-[0-9a-f]+)`$")
_WINS_CELL: Final = re.compile(r"^(\d+)\s*/\s*(\d+)$")
_DISCORDANT_CELL: Final = re.compile(r"^(\d+)\s*/\s*(\d+)(?:\s*\(\d+ seeds\))?$")
_FIRST_FLOAT: Final = re.compile(r"[-+]?\d+\.\d+")
_INTERVAL_CELL: Final = re.compile(r"^\[\s*(\d+\.\d+)\s*,\s*(\d+\.\d+)\s*\]$")


def _decimals(text: str) -> int:
    """How many decimal places a committed cell states (its own precision)."""

    match = _FIRST_FLOAT.search(text)
    if match is None:
        raise EvidenceError(f"no decimal number in {text!r}")
    _, _, fraction = match.group(0).partition(".")
    return len(fraction)


def _cell_float(text: str) -> float:
    match = _FIRST_FLOAT.search(text)
    if match is None:
        raise EvidenceError(f"no decimal number in {text!r}")
    return float(match.group(0))


def erratum_paired_rows(repo_root: Path) -> dict[str, list[str]]:
    """The finalist report's paired-statistics erratum table, arm by arm.

    Task 19.20 committed this table into `training/reports/report-finalist-eval.md`
    §18 item 1; it is the committed verdict this leg's recomputation is compared
    against. Rows are keyed by entrant and kept as raw cells so each number can
    be compared at the precision the report itself states.
    """

    rows: dict[str, list[str]] = {}
    for cells in _table_rows(_read_text(repo_root, FINALIST_REPORT)):
        if len(cells) != 8:
            continue
        match = _ERRATUM_ARM.match(cells[0].replace("**", "").strip())
        if match is None:
            continue
        entrant = match.group(1)
        if entrant in rows:
            raise EvidenceError(
                f"{FINALIST_REPORT}: two paired-erratum rows for {entrant!r}"
            )
        rows[entrant] = cells
    if not rows:
        raise EvidenceError(
            f"{FINALIST_REPORT}: no paired-statistics erratum rows "
            "(`p18-imp-…` | n | wins | delta | b/c | p | Wilson | Wilson) — the "
            "committed verdict this leg compares against is gone"
        )
    return rows


def run_paired(ctx: Context) -> LegResult:
    """Recompute the paired finalist statistics and pin them to the erratum."""

    stats = paired_stats.compute_paired_stats(ctx.repo_root / FINALIST_RESULTS)
    committed = erratum_paired_rows(ctx.repo_root)
    measured = {row.entrant: row for row in stats}

    rows: list[CheckRow] = []
    # Coverage in both directions: an erratum row with no recomputation behind
    # it is an unverifiable published statistic, and a recomputed arm with no
    # erratum row is a published table that no longer describes the measurement.
    unmatched = sorted(set(committed) - set(measured))
    unpublished = sorted(set(measured) - set(committed))
    if unmatched or unpublished:
        rows.append(
            CheckRow(
                name="paired arm coverage",
                measured=f"{len(measured)} arm(s) recomputed: {', '.join(measured)}",
                committed=f"{len(committed)} arm(s) in the erratum table",
                source=f"{FINALIST_REPORT} §18 item 1",
                status="FAIL",
                detail="\n".join(
                    part
                    for part in (
                        f"no recomputation for: {', '.join(unmatched)}"
                        if unmatched
                        else "",
                        f"recomputed but not in the erratum table: "
                        f"{', '.join(unpublished)}"
                        if unpublished
                        else "",
                    )
                    if part
                ),
            )
        )
    for entrant in sorted(committed):
        if entrant not in measured:
            continue
        cells = committed[entrant]
        arm = measured[entrant]
        problems: list[str] = []

        n_cell = int(cells[1])
        if arm.n != n_cell:
            problems.append(f"n {arm.n} != {n_cell}")
        wins = _WINS_CELL.match(cells[2].replace("**", "").strip())
        if wins is None:
            raise EvidenceError(
                f"{FINALIST_REPORT}: {entrant} wins cell {cells[2]!r} is not 'a / b'"
            )
        if (arm.arm_wins, arm.baseline_wins) != (
            int(wins.group(1)),
            int(wins.group(2)),
        ):
            problems.append(
                f"wins {arm.arm_wins}/{arm.baseline_wins} != "
                f"{wins.group(1)}/{wins.group(2)}"
            )
        delta_cell = cells[3].replace("**", "").strip()
        if round(arm.delta, _decimals(delta_cell)) != _cell_float(delta_cell):
            problems.append(f"delta {arm.delta} != {delta_cell}")
        discordant = _DISCORDANT_CELL.match(cells[4].replace("**", "").strip())
        if discordant is None:
            raise EvidenceError(
                f"{FINALIST_REPORT}: {entrant} discordant cell {cells[4]!r} "
                "is not 'b/c'"
            )
        if (arm.b, arm.c) != (int(discordant.group(1)), int(discordant.group(2))):
            problems.append(
                f"discordant {arm.b}/{arm.c} != "
                f"{discordant.group(1)}/{discordant.group(2)}"
            )
        p_cell = cells[5]
        if round(arm.p_exact, _decimals(p_cell)) != _cell_float(p_cell):
            problems.append(f"p_exact {arm.p_exact} != {p_cell}")
        for label, cell, low, high in (
            ("arm Wilson", cells[6], arm.arm_wilson_low, arm.arm_wilson_high),
            (
                "baseline Wilson",
                cells[7],
                arm.baseline_wilson_low,
                arm.baseline_wilson_high,
            ),
        ):
            interval = _INTERVAL_CELL.match(cell.replace("**", "").strip())
            if interval is None:
                raise EvidenceError(
                    f"{FINALIST_REPORT}: {entrant} {label} cell {cell!r} is not "
                    "'[low, high]'"
                )
            places = len(interval.group(1).partition(".")[2])
            if (round(low, places), round(high, places)) != (
                float(interval.group(1)),
                float(interval.group(2)),
            ):
                problems.append(
                    f"{label} [{low:.4f}, {high:.4f}] != "
                    f"[{interval.group(1)}, {interval.group(2)}]"
                )
        rows.append(
            CheckRow(
                name=f"paired McNemar + Wilson: {entrant}",
                measured=(
                    f"n={arm.n} wins {arm.arm_wins}/{arm.baseline_wins} "
                    f"delta {arm.delta:+.4f} discordant {arm.b}/{arm.c} "
                    f"p_exact {arm.p_exact:.4f}"
                ),
                committed=(
                    f"n={cells[1]} wins {cells[2]} delta {delta_cell} "
                    f"discordant {cells[4].replace('**', '')} "
                    f"p {p_cell.replace('**', '')}"
                ),
                source=f"{FINALIST_REPORT} §18 item 1 via scripts/paired_stats",
                status="FAIL" if problems else "OK",
                detail="\n".join(problems),
            )
        )

    # The multiplicity line the erratum draws its conclusion from, recomputed AND
    # compared. Leaving it at INFO ("reported, not pinned") meant the erratum's
    # bar or its named survivors could be edited to contradict the very p values
    # verified row-by-row above, and this command would still exit 0 — the
    # published conclusion is part of the committed record, not commentary
    # (Codex review, PR #348).
    threshold = paired_stats.FAMILY_ALPHA / len(stats)
    clears = sorted(row.entrant for row in stats if row.p_exact < threshold)
    stated_alpha, stated_family, stated_bar, stated_clears = bonferroni_from_report(
        ctx.repo_root
    )
    bar_drift: list[str] = []
    if stated_alpha != paired_stats.FAMILY_ALPHA:
        bar_drift.append(
            f"alpha: report {stated_alpha} != {paired_stats.FAMILY_ALPHA} "
            "(scripts/paired_stats.FAMILY_ALPHA)"
        )
    if stated_family != len(stats):
        bar_drift.append(f"family size: report {stated_family} != {len(stats)} arms")
    if abs(stated_bar - threshold) > FLOAT_TOLERANCE:
        bar_drift.append(f"bar: report {stated_bar} != {threshold:.4f}")
    if stated_clears != clears:
        bar_drift.append(
            f"survivors: report {', '.join(stated_clears) or '(none)'} != "
            f"recomputed {', '.join(clears) or '(none)'}"
        )
    rows.append(
        CheckRow(
            name="Bonferroni family bar",
            measured=(
                f"alpha {paired_stats.FAMILY_ALPHA}/{len(stats)} = {threshold:.4f}; "
                f"clears: {', '.join(clears) if clears else '(none)'}"
            ),
            committed=(
                f"alpha {stated_alpha}/{stated_family} = {stated_bar}; "
                f"survives: {', '.join(stated_clears)}"
            ),
            source=f"{FINALIST_REPORT} (multiplicity erratum)",
            status="OK" if not bar_drift else "FAIL",
            detail="\n".join(bar_drift),
        )
    )
    return LegResult(leg="paired", rows=tuple(rows))


# --------------------------------------------------------------------------- #
# Leg 5 — the artifact-availability report                                     #
# --------------------------------------------------------------------------- #

#: The registry document's ``where`` cell, mapped to an availability class. An
#: unrecognised value fails the run: `docs/artifacts.md` is the authority on what
#: each class means, so a new phrasing is a decision this command must be taught,
#: never one it may guess at.
_WHERE_TO_CLASS: Final[dict[str, AvailabilityClass]] = {
    "in git": "IN-TREE",
    "pinned sha": "EVIDENCE-BRANCH",
    "regenerated (`.gitignore`d)": "REGENERATED",
}

#: Which `docs/artifacts.md` CLASS cells may sit beside which `where` cell. The
#: document defines four classes and a storage policy per class, so a row whose
#: class contradicts its storage is an invalid committed input — and reading the
#: availability from `where` alone meant such a row was carried into the label
#: and still reported OK (Codex review, PR #348). Class (a)/(b) live in git,
#: (c) on the pinned sha, (d) is regenerated; a combined "(a) + (b)" cell is the
#: document's own shorthand for bytes plus their manifest.
_ALLOWED_CLASS_WHERE: Final[dict[str, str]] = {
    "(a)": "in git",
    "(b)": "in git",
    "(a) + (b)": "in git",
    "(c)": "pinned sha",
    "(d)": "regenerated (`.gitignore`d)",
}

#: The probe paths for each registry row, keyed by the row's FIRST backticked
#: token. The doc's artifact cell is prose (it names sibling directories
#: relatively and expands a brace), so the paths are declared here — and the KEY
#: SET is cross-checked against the document on every run, so a row added to
#: `docs/artifacts.md` fails this command rather than going unreported.
_IN_TREE_PROBES: Final[dict[str, tuple[str, ...]]] = {
    "replays/samples/": ("replays/samples/4p1i", "replays/samples/9p2i"),
    "replays/ml_corpus/": ("replays/ml_corpus/4p1i", "replays/ml_corpus/9p2i"),
    "agents/tactical/learned/{weights,crew_weights}.json": (
        "agents/tactical/learned/weights.json",
        "agents/tactical/learned/weights.json.sha256",
        "agents/tactical/learned/crew_weights.json",
        "agents/tactical/learned/crew_weights.json.sha256",
    ),
    "tests/fixtures/": ("tests/fixtures",),
    "data/personas.json": ("data/personas.json",),
    "training/artifacts/impostor/": (
        "training/artifacts/impostor",
        "training/artifacts/crew",
        "training/artifacts/anchor_study",
    ),
    "training/artifacts/surrogate/": (
        SURROGATE_DIR,
        CONVICTION_DIR,
        COMPOSED_DIR,
    ),
    "training/artifacts/coevo/": (COEVO_DEST, f"{COEVO_DEST}/PATHS.md"),
    "training/artifacts/coevo/EVIDENCE-MANIFEST.md": (EVIDENCE_MANIFEST,),
    "training/reports/": ("training/reports", FINALIST_RESULTS),
    "training/reports/_finalist_eval_raw/MANIFEST.md": (SLATE_MANIFEST,),
    "audits/": ("audits",),
    "docs/media/": ("docs/media",),
    "design/phase-12/": ("design/phase-12",),
    "experiments/lab/": ("experiments/lab", "experiments/model_probe"),
    "replays/*.jsonl": (),
}

#: The git pathspec whose tracked files each IN-TREE registry row promises, and
#: the paths a more specific row owns instead. Read from `docs/artifacts.md`'s
#: own descriptions rather than reused from :data:`_IN_TREE_PROBES`: the probes
#: are existence ANCHORS, and taking them as inventory scope was
#: under-inclusive — their union missed `replays/ml_corpus/README.md`, one of the
#: 209 files that row promises — and could not express the two rows that nest
#: (Codex review, PR #348).
#:
#: The two nestings do NOT behave alike, which is why neither is inferred:
#: `training/reports/`'s 21 files INCLUDE `_finalist_eval_raw/MANIFEST.md` even
#: though that file also has its own row, while `training/artifacts/coevo/`'s 90
#: EXCLUDE `EVIDENCE-MANIFEST.md`, which likewise has its own.
#:
#: This table cannot be silently wrong. The registry states a file count for
#: almost every row, and the parity check compares it against the index, so a
#: mis-scoped entry turns the command red instead of mis-reporting.
_IN_TREE_INVENTORY: Final[dict[str, tuple[tuple[str, ...], tuple[str, ...]]]] = {
    "replays/samples/": (("replays/samples",), ()),
    "replays/ml_corpus/": (("replays/ml_corpus",), ()),
    "agents/tactical/learned/{weights,crew_weights}.json": (
        (
            "agents/tactical/learned/weights.json",
            "agents/tactical/learned/weights.json.sha256",
            "agents/tactical/learned/crew_weights.json",
            "agents/tactical/learned/crew_weights.json.sha256",
        ),
        (),
    ),
    "tests/fixtures/": (("tests/fixtures",), ()),
    "data/personas.json": (("data/personas.json",), ()),
    "training/artifacts/impostor/": (
        (
            "training/artifacts/impostor",
            "training/artifacts/crew",
            "training/artifacts/anchor_study",
        ),
        (),
    ),
    "training/artifacts/surrogate/": (
        (SURROGATE_DIR, CONVICTION_DIR, COMPOSED_DIR),
        (),
    ),
    "training/artifacts/coevo/": ((COEVO_DEST,), (EVIDENCE_MANIFEST,)),
    "training/artifacts/coevo/EVIDENCE-MANIFEST.md": ((EVIDENCE_MANIFEST,), ()),
    "training/reports/": (("training/reports",), ()),
    "training/reports/_finalist_eval_raw/MANIFEST.md": ((SLATE_MANIFEST,), ()),
    "audits/": (("audits",), ()),
    "docs/media/": (("docs/media",), ()),
    "design/phase-12/": (("design/phase-12",), ()),
    "experiments/lab/": (("experiments/lab", "experiments/model_probe"), ()),
}

#: The registry's own per-row file count, e.g. `1.5 MB / 105 files`. The word
#: matters: the slate row reads "1,569 digests", which is a digest count and not
#: an inventory of files on this checkout.
_STATED_FILES: Final = re.compile(r"([\d,]+) files")


def inventory_problems(
    repo_root: Path, inventories: Sequence[tuple[str, list[str], int | None]]
) -> list[str]:
    """Every disagreement between the registry, the git index, and the disk.

    Two independent questions, because one of them cannot answer the other:

    * is every tracked file actually on disk? — catches a working-tree deletion;
    * does the index hold as many files as `docs/artifacts.md` PROMISES? —
      catches a COMMITTED deletion, which removes the path from the index too,
      so a check that used the index count as its own expectation watched both
      sides shrink together and still read OK (Codex review, PR #348). This is
      round 1's finding in a second place: an inventory derived from the thing
      it is checking cannot notice a deletion.
    """

    problems: list[str] = []
    for key, tracked, stated_count in inventories:
        gone = [path for path in tracked if not (repo_root / path).is_file()]
        if gone:
            problems.append(
                f"{key}: {len(gone)} tracked file(s) absent from disk "
                f"({', '.join(gone[:5])})"
            )
        if stated_count is not None and stated_count != len(tracked):
            problems.append(
                f"{key}: {ARTIFACTS_DOC} promises {stated_count} files, "
                f"the index tracks {len(tracked)}"
            )
    return problems


def in_tree_inventory(repo_root: Path, key: str) -> list[str] | None:
    """The tracked files an in-tree registry row promises, or ``None`` without git."""

    scope = _IN_TREE_INVENTORY.get(key)
    if scope is None:
        raise EvidenceError(
            f"{ARTIFACTS_DOC}: in-tree registry row {key!r} has no inventory "
            "scope in this command; a row whose bytes nothing enumerates cannot "
            "be reported as complete"
        )
    pathspec, owned_elsewhere = scope
    tracked = git_tracked_under(repo_root, pathspec)
    if tracked is None:
        return None
    return [path for path in tracked if path not in owned_elsewhere]


#: The two class-(c) rows, keyed the same way, with the evidence-commit prefix
#: whose manifest rows they cover.
_EVIDENCE_PREFIXES: Final[dict[str, str]] = {
    "coevo/": "coevo/",
    "finalist-eval-raw/": "finalist-eval-raw/",
}

#: Named evidence that `docs/artifacts.md`'s registry table holds no row for,
#: because it is not in this repository and never will be. Each entry names the
#: committed line that RECORDS its class — the anchor is re-read on every run, so
#: a class this command reports is always one the tree still states.
_OFF_TREE_ANCHORS: Final[tuple[tuple[str, AvailabilityClass, str, str], ...]] = (
    (
        "co-evolution audit sidecars (`**/*.audit.jsonl`)",
        "REPO-EXTERNAL",
        PATHS_DOC,
        "Audit sidecars (`*.audit.jsonl`) are excluded from the committed tree",
    ),
    (
        "operator campaign root `~/ailibi-campaign-1824/` (Phase-18 co-evolution)",
        "REPO-EXTERNAL",
        PATHS_DOC,
        "/Users/danielkeinan/ailibi-campaign-1824/",
    ),
    (
        "operator campaign root `~/ailibi-campaign-1825/` (the 18.25 crew campaign)",
        "REPO-EXTERNAL",
        PATHS_DOC,
        "operator root `/Users/danielkeinan/ailibi-campaign-1825/`",
    ),
    (
        "operator campaign root `~/ailibi-campaign-1826/` (the finalist slate)",
        "REPO-EXTERNAL",
        FINALIST_REPORT,
        "Working root `~/ailibi-campaign-1826/`",
    ),
)

#: The Task 19.21 raw-slate ruling, read out of the registry document rather than
#: transcribed. RECOVERED means the bytes are on the pinned commit (and the
#: evidence-branch row above covers them); a LOST/NON-REPRODUCIBLE ruling is the
#: manifest-recorded loss ``--complete`` accepts as a valid close state.
_RULING_RE: Final = re.compile(r"\*\*Ruling (\d{4}-\d{2}-\d{2}): ([A-Z-]+)\*\*")
_LOSS_RULINGS: Final[frozenset[str]] = frozenset({"LOST", "NON-REPRODUCIBLE"})
#: The recovery outcome, and with it the CLOSED vocabulary Task 19.21 allows.
_RECOVERY_RULINGS: Final[frozenset[str]] = frozenset({"RECOVERED"})
_KNOWN_RULINGS: Final[frozenset[str]] = _LOSS_RULINGS | _RECOVERY_RULINGS


#: The registry table's header row, which is how it is located: the table is
#: read from there to the first non-table line, so EVERY row in it is classed
#: and none can be passed over by failing to match a pattern.
_REGISTRY_HEADER: Final[tuple[str, ...]] = ("artifact", "class", "where", "size")
_TABLE_SEPARATOR: Final = re.compile(r"^[-: ]+$")


def registry_rows(repo_root: Path) -> list[tuple[str, str, str, str]]:
    """`docs/artifacts.md`'s registry table as ``(key, class, where, size)``.

    ``key`` is the row's first backticked token, which is what
    :data:`_IN_TREE_PROBES` / :data:`_EVIDENCE_PREFIXES` are keyed by. A row
    whose ``where`` cell is not one of the document's three known values raises:
    `docs/artifacts.md` is the authority on what each class means, so a new
    phrasing is a decision this command must be taught, never one it may skip.
    """

    rows: list[tuple[str, str, str, str]] = []
    inside = False
    for lineno, line in enumerate(
        _read_text(repo_root, ARTIFACTS_DOC).splitlines(), start=1
    ):
        stripped = line.strip()
        is_row = stripped.startswith("|") and stripped.endswith("|")
        cells = [cell.strip() for cell in stripped[1:-1].split("|")] if is_row else []
        if not inside:
            if is_row and tuple(cell.lower() for cell in cells) == _REGISTRY_HEADER:
                inside = True
            continue
        if not is_row:
            break
        if cells and all(_TABLE_SEPARATOR.match(cell) for cell in cells):
            continue
        if len(cells) != len(_REGISTRY_HEADER):
            raise EvidenceError(
                f"{ARTIFACTS_DOC}:{lineno}: registry row has {len(cells)} cells, "
                f"not {len(_REGISTRY_HEADER)}"
            )
        where = cells[2].replace("**", "").strip()
        if where not in _WHERE_TO_CLASS:
            raise EvidenceError(
                f"{ARTIFACTS_DOC}:{lineno}: registry row states where={where!r}, "
                f"which is none of {sorted(_WHERE_TO_CLASS)} — this command must "
                "be taught a new availability class, never guess at one"
            )
        match = re.search(r"`([^`]+)`", cells[0])
        if match is None:
            raise EvidenceError(
                f"{ARTIFACTS_DOC}:{lineno}: registry row {cells[0]!r} names no "
                "artifact path"
            )
        declared = cells[1].replace("**", "").strip()
        if declared not in _ALLOWED_CLASS_WHERE:
            raise EvidenceError(
                f"{ARTIFACTS_DOC}:{lineno}: registry row declares class "
                f"{declared!r}, which is none of {sorted(_ALLOWED_CLASS_WHERE)}"
            )
        if _ALLOWED_CLASS_WHERE[declared] != where:
            raise EvidenceError(
                f"{ARTIFACTS_DOC}:{lineno}: class {declared!r} is stored "
                f"{_ALLOWED_CLASS_WHERE[declared]!r}, but this row says "
                f"{where!r} — the declared class contradicts its storage policy"
            )
        rows.append((match.group(1), declared, where, cells[3]))
    if not inside:
        raise EvidenceError(
            f"{ARTIFACTS_DOC}: no registry table "
            f"(a `| {' | '.join(_REGISTRY_HEADER)} |` header) — the availability "
            "classes cannot be read"
        )
    if not rows:
        raise EvidenceError(f"{ARTIFACTS_DOC}: the registry table has no rows")
    return rows


def _availability_row(
    name: str,
    measured: AvailabilityClass | str,
    recorded: AvailabilityClass,
    source: str,
    status: Status,
    detail: str = "",
) -> CheckRow:
    return CheckRow(
        name=name,
        measured=str(measured),
        committed=recorded,
        source=source,
        status=status,
        detail=detail,
    )


def run_availability(ctx: Context) -> LegResult:
    """The availability class of every named evidence artifact, measured."""

    rows: list[CheckRow] = []
    doc_rows = registry_rows(ctx.repo_root)
    known = set(_IN_TREE_PROBES) | set(_EVIDENCE_PREFIXES)
    doc_keys = {key for key, _, _, _ in doc_rows}
    # Double entry: the document is the registry, and this command's probe table
    # must cover it exactly. A row added to docs/artifacts.md that nothing here
    # probes would be an artifact silently absent from the availability report,
    # which is precisely what this leg exists to prevent.
    if doc_keys != known:
        missing = ", ".join(sorted(doc_keys - known)) or "(none)"
        extra = ", ".join(sorted(known - doc_keys)) or "(none)"
        rows.append(
            CheckRow(
                name="registry coverage",
                measured=f"{len(known)} probed row(s)",
                committed=f"{len(doc_keys)} registry row(s)",
                source=ARTIFACTS_DOC,
                status="FAIL",
                detail=(
                    f"in {ARTIFACTS_DOC} but not probed here: {missing}\n"
                    f"probed here but not in {ARTIFACTS_DOC}: {extra}"
                ),
            )
        )
    else:
        rows.append(
            CheckRow(
                name="registry coverage",
                measured=f"{len(known)} row(s) probed",
                committed=f"{len(doc_keys)} row(s) in the registry",
                source=ARTIFACTS_DOC,
                status="OK",
            )
        )

    present_by_prefix: dict[str, int] = {}
    total_by_prefix: dict[str, int] = {}
    for row in ctx.evidence:
        if row.repo_path is None:
            continue
        prefix = row.manifest_path.split("/", 1)[0] + "/"
        total_by_prefix[prefix] = total_by_prefix.get(prefix, 0) + 1
        if (ctx.repo_root / row.repo_path).is_file():
            present_by_prefix[prefix] = present_by_prefix.get(prefix, 0) + 1

    for key, class_cell, where, size_cell in doc_rows:
        recorded = _WHERE_TO_CLASS[where]
        label = f"{key} [{class_cell}]"
        if recorded == "IN-TREE":
            probes = _IN_TREE_PROBES.get(key, ())
            # These probes are ANCHORS, and several rows anchor on directories
            # (`tests/fixtures`, `audits`, `docs/media`), so `.exists()` is the
            # right test here. What anchors CANNOT do is notice a file deleted
            # beside them — that is the aggregate inventory row below, which
            # checks files with `.is_file()`.
            missing_paths = [p for p in probes if not (ctx.repo_root / p).exists()]
            rows.append(
                _availability_row(
                    label,
                    "IN-TREE" if not missing_paths else "MISSING",
                    recorded,
                    f"{ARTIFACTS_DOC} (registry: '{where}')",
                    "OK" if not missing_paths else "FAIL",
                    detail="absent: " + ", ".join(missing_paths)
                    if missing_paths
                    else "",
                )
            )
        elif recorded == "EVIDENCE-BRANCH":
            prefix = _EVIDENCE_PREFIXES[key]
            total = total_by_prefix.get(prefix, 0)
            present = present_by_prefix.get(prefix, 0)
            # The registry states each class-(c) row's file count; those bytes
            # are immutable by construction, so the manifest must agree with it.
            stated = re.search(r"([\d,]+) files", size_cell)
            count_note = ""
            if stated is not None and int(stated.group(1).replace(",", "")) != total:
                count_note = (
                    f"{ARTIFACTS_DOC} states {stated.group(1)} files; the "
                    f"manifest carries {total}"
                )
            # The RECORDED LOSS is decided FIRST. On the loss path Task 19.21
            # writes no slate manifest at all, so `total` is 0 while the registry
            # still states the count those bytes HAD — a parity check between a
            # live count and a historical one, which failed the close on exactly
            # the state this command is required to accept. Third round on this
            # path (Codex review, PR #348); an end-to-end `--complete` test over
            # a manifestless-loss tree now covers the whole pipeline rather than
            # the one branch each round happened to name.
            if prefix in ctx.lost_prefixes:
                ruling = ctx.slate_ruling
                status: Status = "INFO"
                measured: str = (
                    f"LOST (recorded {ruling.date})"
                    if ruling is not None
                    else "LOST (recorded)"
                )
                count_note = ""
            elif count_note:
                status = "FAIL"
                measured = "MANIFEST/REGISTRY DISAGREE"
            elif present == total:
                status = "OK"
                measured = "EVIDENCE-BRANCH-RESTORED"
            elif present == 0:
                status = "ABSENT"
                measured = "EVIDENCE-BRANCH-ABSENT"
            else:
                status = "FAIL"
                measured = "EVIDENCE-BRANCH-PARTIAL"
            rows.append(
                _availability_row(
                    label,
                    f"{measured} ({present}/{total} present)",
                    recorded,
                    f"{ARTIFACTS_DOC} + {EVIDENCE_MANIFEST} §1 "
                    f"(pin {ctx.pinned_sha[:12]}…)",
                    status,
                    detail=count_note
                    or (
                        "restore with `bash scripts/fetch_evidence.sh`"
                        if status == "ABSENT"
                        else ""
                    ),
                )
            )
        else:
            rows.append(
                _availability_row(
                    label,
                    "REGENERATED (class (d) — never committed)",
                    recorded,
                    f"{ARTIFACTS_DOC} (registry: '{where}')",
                    "INFO",
                    detail="regenerated by the documented command, not preserved",
                )
            )

    # ---- the in-tree families, file by file rather than by anchor. ----
    # The per-family rows above confirm the ANCHORS the probe table names, which
    # is a handful of paths per family. Every other byte in those families —
    # `training/artifacts/impostor/bc-dagger/config.json` is the review's own
    # example — could be deleted with the family directory still standing, and
    # no leg here reads it, so every row stayed OK and `--complete` certified a
    # checkout missing a promised class-(a) byte (Codex review, PR #348). Git is
    # the committed inventory of what each family holds; the round-1 fix
    # established this idiom for the sidecars, and this is the same idiom applied
    # to the registry's own in-tree rows. Without an index the row reports ABSENT
    # (which `--complete` fails) rather than certifying an inventory it could not
    # read.
    inventories: list[tuple[str, list[str], int | None]] = []
    unverifiable = False
    for row_key, _cls, row_where, row_size in doc_rows:
        if _WHERE_TO_CLASS[row_where] != "IN-TREE":
            continue
        tracked = in_tree_inventory(ctx.repo_root, row_key)
        if tracked is None:
            unverifiable = True
            break
        stated_files = _STATED_FILES.search(row_size)
        inventories.append(
            (
                row_key,
                tracked,
                int(stated_files.group(1).replace(",", "")) if stated_files else None,
            )
        )

    if unverifiable:
        rows.append(
            CheckRow(
                name="in-tree family inventory",
                measured="INVENTORY UNVERIFIABLE",
                committed=f"{ARTIFACTS_DOC}'s per-row file counts",
                source=f"{ARTIFACTS_DOC} (registry) + `git ls-files`",
                status="ABSENT",
                detail=(
                    "no git index in this checkout, so the committed file list "
                    "for each in-tree family cannot be read; the anchor rows "
                    "above cannot notice a file deleted beside them"
                ),
            )
        )
    else:
        # Double entry, and the reason it has to be. Using the index count as
        # its own expectation reproduced round 1's finding exactly: a COMMITTED
        # deletion drops the path from `git ls-files` too, so both sides shrank
        # together and the row still read OK while the registry went on
        # promising the file (Codex review, PR #348). The document's stated
        # count is the independent side — it does not move when the index does.
        problems = inventory_problems(ctx.repo_root, inventories)
        tracked_total = sum(len(tracked) for _key, tracked, _stated in inventories)
        pinned = sum(1 for _key, _tracked, stated in inventories if stated is not None)
        rows.append(
            CheckRow(
                name="in-tree family inventory",
                measured=(
                    f"{tracked_total} tracked file(s) present across "
                    f"{len(inventories)} row(s)"
                ),
                committed=f"{pinned} row(s) state a file count; all compared",
                source=f"{ARTIFACTS_DOC} (registry) + `git ls-files`",
                status="OK" if not problems else "FAIL",
                detail="\n".join(problems),
            )
        )
    # ---- named evidence with no registry row: recorded off-tree, or lost. ----
    for name, recorded_class, anchor_file, anchor_text in _OFF_TREE_ANCHORS:
        anchored = anchor_text in _read_text(ctx.repo_root, anchor_file)
        rows.append(
            _availability_row(
                name,
                recorded_class if anchored else "UNRECORDED",
                recorded_class,
                f"{anchor_file} ({anchor_text!r})",
                "INFO" if anchored else "FAIL",
                detail=""
                if anchored
                else (
                    f"{anchor_file} no longer records this class; an availability "
                    "class this command reports must be one the tree still states"
                ),
            )
        )

    # ---- the Task 19.21 raw-slate ruling, read from the registry document. ----
    slate_ruling = ctx.slate_ruling
    if slate_ruling is None:
        rows.append(
            CheckRow(
                name="Phase-18 finalist raw slate (Task 19.21 outcome)",
                measured="NO RULING RECORDED",
                committed="a dated '**Ruling <date>: <outcome>**' line",
                source=f"{ARTIFACTS_DOC} (the class-(c) rows in detail)",
                status="FAIL",
                detail=(
                    "Task 19.21 records either recovery or loss; an unrecorded "
                    "outcome is the silent state the close forbids"
                ),
            )
        )
    else:
        ruling_date, outcome = slate_ruling.date, slate_ruling.outcome
        lost = slate_ruling.lost
        slate_present = present_by_prefix.get(_SLATE_PREFIX, 0)
        slate_total = total_by_prefix.get(_SLATE_PREFIX, 0)
        if lost:
            slate_status: Status = "INFO"
            slate_measured = f"LOST (recorded {ruling_date})"
        elif slate_present == slate_total and slate_total:
            slate_status = "OK"
            slate_measured = (
                f"{outcome} → EVIDENCE-BRANCH-RESTORED ({slate_present}/{slate_total})"
            )
        elif slate_present == 0:
            slate_status = "ABSENT"
            slate_measured = (
                f"{outcome} → EVIDENCE-BRANCH-ABSENT (0/{slate_total} restored)"
            )
        else:
            slate_status = "FAIL"
            slate_measured = (
                f"{outcome} → EVIDENCE-BRANCH-PARTIAL ({slate_present}/{slate_total})"
            )
        rows.append(
            CheckRow(
                name="Phase-18 finalist raw slate (Task 19.21 outcome)",
                measured=slate_measured,
                committed=f"Ruling {ruling_date}: {outcome}",
                source=f"{ARTIFACTS_DOC} (the class-(c) rows in detail)",
                status=slate_status,
                detail=(
                    "a manifest-recorded loss is a valid close state — the bytes "
                    "are gone, the record is not"
                    if lost
                    else (
                        "restore with `bash scripts/fetch_evidence.sh`"
                        if slate_status == "ABSENT"
                        else ""
                    )
                ),
            )
        )
    return LegResult(leg="availability", rows=tuple(rows))


# --------------------------------------------------------------------------- #
# Rendering + the CLI                                                          #
# --------------------------------------------------------------------------- #

LEG_TITLES: Final[dict[str, str]] = {
    "sidecars": "per-class sha-256 verification (in-tree + evidence branch)",
    "corpus": "corpus reconstruction (engine playback) + corpus identity",
    "recompute": "surrogate / conviction / composed, from the frozen weights",
    "paired": "the paired finalist statistics (scripts/paired_stats, 19.20)",
    "availability": "the artifact-availability report (docs/artifacts.md classes)",
}


def render(result: LegResult) -> str:
    lines = [
        "",
        f"--- {result.leg}: {LEG_TITLES[result.leg]} ---",
    ]
    for note in result.notes:
        lines.extend([f"  ! {note}", ""])
    for row in result.rows:
        lines.append(f"[{row.status:^6}] {row.name}")
        lines.append(f"          measured : {row.measured}")
        lines.append(f"          committed: {row.committed}")
        lines.append(f"          source   : {row.source}")
        if row.detail:
            for detail_line in row.detail.splitlines():
                lines.append(f"          note     : {detail_line}")
    return "\n".join(lines)


def _failed(rows: Sequence[CheckRow], *, complete: bool) -> list[CheckRow]:
    """The rows that fail this run. ``ABSENT`` fails only under ``--complete``."""

    return [
        row
        for row in rows
        if row.status == "FAIL" or (complete and row.status == "ABSENT")
    ]


#: Leg name -> the function that runs it. Kept beside :data:`LEG_TITLES` so a
#: leg cannot be selectable without both a runner and a heading.
LEG_RUNNERS: Final[dict[str, Callable[[Context], LegResult]]] = {
    "sidecars": run_sidecars,
    "corpus": run_corpus,
    "recompute": run_recompute,
    "paired": run_paired,
    "availability": run_availability,
}


def run_legs(ctx: Context, legs: Sequence[str]) -> list[LegResult]:
    """Run the named legs in order. ``main`` streams instead, leg by leg."""

    return [LEG_RUNNERS[leg](ctx) for leg in legs]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the whole ML evidence story in one read-only, offline "
            "command (Task 19.23): per-class sidecar/sha verification, corpus "
            "reconstruction, surrogate/conviction/composed recomputation, the "
            "paired finalist statistics, and the artifact-availability report."
        ),
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help=(
            "sample the corpus reconstruction instead of walking every committed "
            f"replay ({FAST_SAMPLE_PER_SET} seeds per set; the sampling is "
            "disclosed in the output)"
        ),
    )
    parser.add_argument(
        "--complete",
        action="store_true",
        help=(
            "the close gate: FAIL on any byte promised archival availability "
            "that is absent, while accepting a manifest-recorded LOST class. Run "
            "`bash scripts/fetch_evidence.sh` first"
        ),
    )
    parser.add_argument(
        "--only",
        action="append",
        choices=LEGS,
        metavar="LEG",
        help=(
            f"run only the named leg (repeatable; one of {', '.join(LEGS)}). "
            "Refused with --complete: a partial run cannot certify completeness"
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_REPO_ROOT,
        help=(
            "the checkout to verify — must be this script's own checkout. To "
            "verify a different one, run THAT checkout's copy of this script"
        ),
    )
    args = parser.parse_args(argv)
    fast: bool = args.fast
    complete: bool = args.complete
    only: list[str] | None = args.only
    repo_root: Path = args.repo_root

    # The verifier CODE always comes from this script's own checkout: the
    # bootstrap above pins `sys.path`, and the recompute leg imports `training.*`
    # (and the corpus leg `_verify_samples`) through it. Verifying a DIFFERENT
    # checkout's evidence with this checkout's engine and ML code is a
    # cross-revision run, and issuing a certificate for it is exactly the false
    # certificate this command exists to prevent (Codex review, PR #348). The
    # honest way to verify another checkout is to run its own copy — which needs
    # no flag, and picks up that revision's verifier rather than this one.
    if repo_root.resolve() != _REPO_ROOT:
        print(
            f"--repo-root {repo_root} is not this script's checkout "
            f"({_REPO_ROOT}). This command's verifier code is imported from its "
            "own checkout, so it cannot certify another one's evidence; run "
            "that checkout's copy instead:\n"
            f"    uv run python {repo_root}/scripts/verify_ml_evidence.py",
            file=sys.stderr,
        )
        return 2

    if complete and only:
        print(
            "--complete verifies EVERY leg; it cannot be combined with --only "
            "(a partial run cannot certify completeness).",
            file=sys.stderr,
        )
        return 2
    if complete and fast:
        print(
            "--complete verifies every committed replay; it cannot be combined "
            "with --fast (a sampled walk is not a complete one).",
            file=sys.stderr,
        )
        return 2
    legs = [leg for leg in LEGS if only is None or leg in only]

    try:
        ctx = Context(
            repo_root=repo_root,
            fast=fast,
            complete=complete,
            evidence=evidence_rows(repo_root, slate_lost=_slate_lost(repo_root)),
            pinned_sha=read_pinned_sha(repo_root),
            slate_ruling=read_slate_ruling(repo_root),
        )
        mode = "complete" if complete else ("fast" if fast else "full")
        print(f"=== verify-ml-evidence ({mode}) — {repo_root} ===")
        print(f"evidence pin: {ctx.pinned_sha} ({EVIDENCE_MANIFEST} §1)")
        print("read-only and offline: no artifact is written and no socket is opened.")
        if only is not None:
            print(f"PARTIAL RUN — only: {', '.join(legs)}")
        # Streamed leg by leg rather than collected first: the recomputation leg
        # is tens of seconds of corpus tables, and a command whose whole job is
        # to show its work should not sit silent through it.
        results: list[LegResult] = []
        for leg in legs:
            result = LEG_RUNNERS[leg](ctx)
            results.append(result)
            print(render(result), flush=True)
    except EvidenceError as exc:
        print(f"verify-ml-evidence: {exc}", file=sys.stderr)
        return 2

    every_row = [row for result in results for row in result.rows]
    failures = _failed(every_row, complete=complete)
    absent = [row for row in every_row if row.status == "ABSENT"]
    print("")
    print(
        f"checks: {len(every_row)} | "
        f"OK {sum(1 for row in every_row if row.status == 'OK')} | "
        f"FAIL {sum(1 for row in every_row if row.status == 'FAIL')} | "
        f"ABSENT {len(absent)} | "
        f"INFO {sum(1 for row in every_row if row.status == 'INFO')}"
    )
    if absent and not complete:
        print(
            f"{len(absent)} check(s) report EVIDENCE-BRANCH-ABSENT — the bytes "
            "Task 19.22 moved are not on this checkout. That is the expected "
            "state of a fresh clone; `bash scripts/fetch_evidence.sh` restores "
            "them and `--complete` requires them."
        )
    if failures:
        print("")
        print("FAILED:")
        for row in failures:
            print(f"  - [{row.status}] {row.name}: {row.measured}")
        return 1
    print("verify-ml-evidence: every check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
