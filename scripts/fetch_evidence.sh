#!/usr/bin/env bash
#
# fetch_evidence.sh — restore the Phase-18 class-(c) evidence bytes (Task 19.22).
#
# Task 19.22 pruned every byte under training/artifacts/coevo/ that no test
# pins, and folded them — together with the Phase-18 finalist raw slate
# recovered at Task 19.21 — into ONE orphan commit on evidence/phase-18-coevo.
# This script puts those bytes back.
#
# The pin is read from the manifest, never hardcoded here: the manifest
# (training/artifacts/coevo/EVIDENCE-MANIFEST.md) owns the tip sha, the per-file
# digests, and the record of what stayed in-tree. Two consequences that are the
# whole point of the design:
#
#   * the fetch is BY SHA, never by branch name. A branch name is a moving
#     pointer and a sha is not, so the sha is the immutability guarantee: bytes
#     restored here are the bytes the manifest hashed, or the verify fails.
#   * restored bytes are UNTRACKED BY DESIGN and must never be committed back.
#     `--clean` removes them again; `docs/artifacts.md` states the rule.
#
# Nothing here overwrites or deletes a byte it cannot re-fetch: the restore
# refuses on any local file that differs from the manifest, and `--clean`
# removes only files that still match it.
#
# Usage:
#   scripts/fetch_evidence.sh              fetch by the pinned sha, restore, verify
#   scripts/fetch_evidence.sh --verify     verify what is already restored
#   scripts/fetch_evidence.sh --clean      remove restored files that still match
#   scripts/fetch_evidence.sh --clean --force   ... and the modified ones too
#
# Needs network only for the fetch leg; --verify and --clean are offline.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

MANIFEST="$REPO_ROOT/training/artifacts/coevo/EVIDENCE-MANIFEST.md"
SLATE_MANIFEST="$REPO_ROOT/training/reports/_finalist_eval_raw/MANIFEST.md"
COEVO_DEST="$REPO_ROOT/training/artifacts/coevo"
SLATE_DEST="$REPO_ROOT/training/reports/_finalist_eval_raw"

# Where the fetched commit is pinned locally. A fetch with no ref leaves the
# objects unreachable, so a later `git gc` may prune them and a subsequent
# offline --verify would lose the branch README it must check. NOT under
# refs/heads: this is a pinned object, not a branch to work on.
LOCAL_REF="refs/evidence/phase-18-coevo"

mode="fetch"
force=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verify) mode="verify" ;;
    --clean) mode="clean" ;;
    --force) force=1 ;;
    -h | --help)
      sed -n '/^# fetch_evidence.sh /,/^# Needs network only/p' \
        "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "unknown argument '$1' (expected --verify, --clean, --force, --help)" >&2
      exit 2
      ;;
  esac
  shift
done
if [[ "$force" == "1" && "$mode" != "clean" ]]; then
  echo "--force only means anything with --clean." >&2
  exit 2
fi

# sha256sum (GNU) or shasum -a 256 (macOS). Both read the same manifest format
# — that is why the manifest is written shasum-compatible — and both report
# per-file results as "<path>: OK" / "<path>: FAILED", which --clean parses.
if command -v sha256sum >/dev/null 2>&1; then
  sha256_check() { sha256sum -c --quiet "$1"; }
  sha256_report() { sha256sum -c "$1" 2>/dev/null || true; }
  sha256_stdin() { sha256sum | cut -d' ' -f1; }
elif command -v shasum >/dev/null 2>&1; then
  sha256_check() { shasum -a 256 -c "$1" >/dev/null; }
  sha256_report() { shasum -a 256 -c "$1" 2>/dev/null || true; }
  sha256_stdin() { shasum -a 256 | cut -d' ' -f1; }
else
  echo "neither sha256sum nor shasum is available; cannot verify" >&2
  exit 1
fi

# --------------------------------------------------------------------------- #
# The pin, and the digest block, both read from the manifest.                  #
# --------------------------------------------------------------------------- #
read_pin() {
  local sha
  # `|| true`: with `set -o pipefail` a no-match grep fails the whole
  # substitution and kills the script BEFORE the diagnostic below can explain
  # why — the corrupt-manifest case would exit silently (Codex review, PR #346).
  sha="$(grep -F 'tip sha — THE PIN' "$MANIFEST" |
    grep -oE '[0-9a-f]{40}' | head -1 || true)"
  if [[ -z "$sha" ]]; then
    echo "no pinned sha in $MANIFEST (the '**tip sha — THE PIN**' row)" >&2
    exit 1
  fi
  printf '%s\n' "$sha"
}

# The manifest's §7 block covers coevo/ + the branch README; §8 delegates the
# slate's 1,569 digests to the 19.21 manifest rather than copying them, so the
# two blocks are composed here — and every path is rewritten to where the
# restore actually puts it. Paths that are not restored (the branch README) are
# dropped; it is checked separately, straight out of the commit.
peel_digests() {
  awk '/^```sha256$/{f=1;next} /^```$/{f=0} f' "$MANIFEST" |
    grep -v '  README.md$' |
    sed 's#  coevo/#  training/artifacts/coevo/#'
  awk '/^```sha256$/{f=1;next} /^```$/{f=0} f' "$SLATE_MANIFEST" |
    sed 's#  \./#  training/reports/_finalist_eval_raw/#'
}

restored_paths() {
  peel_digests | sed 's/^[0-9a-f]\{64\}  //'
}

tracked_paths() {
  git -C "$REPO_ROOT" ls-files -- training/artifacts/coevo \
    training/reports/_finalist_eval_raw | sort
}

# One cleanup list and one trap: several legs below need scratch files, and a
# second `trap ... EXIT` would silently replace the first and leak the earlier
# file. The path is returned through a caller-named variable rather than on
# stdout, because `f="$(scratch_file)"` runs the function in a SUBSHELL — the
# array would grow there and the parent's trap would clean nothing (Codex
# review, PR #346). `printf -v` keeps this working on bash 3.2 too.
_scratch=()
cleanup() {
  if [[ ${#_scratch[@]} -gt 0 ]]; then rm -f "${_scratch[@]}"; fi
}
trap cleanup EXIT
scratch_file() { # scratch_file VARNAME
  local f
  f="$(mktemp)"
  _scratch+=("$f")
  printf -v "$1" '%s' "$f"
}

# The manifest rows for evidence paths that exist on disk and are NOT tracked —
# i.e. everything a restore would overwrite and a clean would remove.
present_untracked_rows() { # present_untracked_rows OUTFILE
  local tracked
  scratch_file tracked
  tracked_paths > "$tracked"
  # `if`, not `&&`: a final iteration whose test is false would make the loop —
  # and so the pipeline — return 1, and `set -e` would kill the script here with
  # no output at all.
  peel_digests | while IFS= read -r row; do
    local rel="${row#*  }"
    if [[ -f "$REPO_ROOT/$rel" ]] && ! grep -qxF "$rel" "$tracked"; then
      printf '%s\n' "$row"
    fi
  done > "$1"
}

# --------------------------------------------------------------------------- #
# clean                                                                        #
# --------------------------------------------------------------------------- #
if [[ "$mode" == "clean" ]]; then
  # Tracked paths are never removed, whatever the manifest lists, and neither
  # are files that no longer MATCH the manifest: the restore guard refuses on a
  # modified local file and points here, so a --clean that deleted it anyway
  # would destroy exactly what that guard was protecting (Codex review, PR
  # #346). --force is the explicit opt-in to discard them.
  candidates=""
  scratch_file candidates
  present_untracked_rows "$candidates"

  removed=0
  kept=""
  scratch_file kept
  : > "$kept"
  if [[ -s "$candidates" ]]; then
    results=""
    scratch_file results
    (cd "$REPO_ROOT" && sha256_report "$candidates") > "$results"
    while IFS= read -r line; do
      rel="${line%: *}"
      verdict="${line##*: }"
      if [[ "$verdict" == "OK" || "$force" == "1" ]]; then
        rm -f "$REPO_ROOT/$rel"
        removed=$((removed + 1))
      else
        printf '%s\n' "$rel" >> "$kept"
      fi
    done < "$results"
  fi

  # Only directories the restore created can end up empty; tracked files keep
  # their own directories alive, so this never removes an in-tree path.
  find "$COEVO_DEST" "$SLATE_DEST" -mindepth 1 -type d -empty -delete 2>/dev/null || true

  echo "Removed $removed restored file(s). Tracked bytes are untouched."
  if [[ -s "$kept" ]]; then
    echo ""
    echo "KEPT $(wc -l < "$kept" | tr -d ' ') file(s) that do NOT match the manifest —" >&2
    echo "they are not restored evidence, so they are not this script's to delete:" >&2
    head -5 "$kept" >&2
    echo "Move them aside, or re-run with --clean --force to discard them." >&2
    exit 1
  fi
  exit 0
fi

# --------------------------------------------------------------------------- #
# fetch + restore                                                              #
# --------------------------------------------------------------------------- #
PINNED_SHA="$(read_pin)"

if [[ "$mode" == "fetch" ]]; then
  if ! git -C "$REPO_ROOT" cat-file -e "${PINNED_SHA}^{commit}" 2>/dev/null; then
    # Fetch through the remote NAME, and print only the name. `git remote
    # get-url` can carry inline credentials (https://x-access-token:<PAT>@...),
    # and echoing it would write the secret to the terminal and to CI logs
    # (Codex review, PR #346).
    echo "Fetching the evidence commit ${PINNED_SHA} from origin ..."
    git -C "$REPO_ROOT" fetch --depth 1 origin "$PINNED_SHA"
  fi

  # The pin buys immutability only if what came back really is the ONE-commit
  # orphan the manifest describes — asserted loudly, before a single byte lands
  # in the tree. Read from the RAW commit object, not from `rev-list --parents`:
  # a --depth 1 fetch makes the commit a shallow boundary, and rev-list then
  # suppresses its parents and reports any parented commit as an orphan
  # (Codex review on PR #346, reproduced against a two-commit repo). The `sed`
  # stops at the header/body boundary so a "parent ..." line in a commit
  # MESSAGE cannot masquerade as a header.
  if git -C "$REPO_ROOT" cat-file commit "$PINNED_SHA" |
    sed -n '/^$/q;p' | grep -q '^parent '; then
    echo "${PINNED_SHA} has a parent header; the evidence commit is an orphan." >&2
    echo "Refusing to restore from it." >&2
    exit 1
  fi

  # Pin the object locally so `git gc` cannot prune it: a bare sha fetch leaves
  # it unreachable, and a later offline --verify needs the commit to check the
  # branch README the manifest also covers.
  git -C "$REPO_ROOT" update-ref "$LOCAL_REF" "$PINNED_SHA"

  # A restore may only ADD files, so nothing already on disk may be clobbered.
  # Three ways that could happen, all refused BEFORE anything is written.
  #
  # (1) An evidence path that is also a TRACKED path. The moved and retained
  #     sets are disjoint by construction (EVIDENCE-MANIFEST.md §3), so this
  #     means the manifest and the commit have drifted apart — the one failure
  #     this whole scheme exists to make impossible to miss.
  overlap="$(comm -12 <(restored_paths | sort) <(tracked_paths))"
  if [[ -n "$overlap" ]]; then
    echo "The evidence commit carries paths that are ALSO tracked in-tree;" >&2
    echo "the manifest and the commit disagree. Nothing was written." >&2
    printf '%s\n' "$overlap" | head -5 >&2
    exit 1
  fi

  # (2) A DIRECTORY SYMLINK anywhere on a destination path — the layout an
  #     operator uses to park the ~399 MiB payload on another volume. GNU tar
  #     REPLACES such a symlink with a real directory unless
  #     --keep-directory-symlink is passed (verified against tar 1.35; the flag
  #     is not portable to BSD tar, so refusing is the portable answer), which
  #     would silently strand whatever the link pointed at (Codex review, PR
  #     #346). Every ancestor of every destination path is checked, deduped.
  symlinked="$(restored_paths | sed 's#/[^/]*$##' | sort -u |
    awk -F/ '{p=""; for (i=1; i<=NF; i++) {p = (i==1 ? $i : p "/" $i); print p}}' |
    sort -u |
    while IFS= read -r dir; do
      if [[ -L "$REPO_ROOT/$dir" ]]; then printf '%s\n' "$dir"; fi
    done)"
  if [[ -n "$symlinked" ]]; then
    echo "A destination path runs through a SYMLINKED directory; extracting" >&2
    echo "would replace the symlink with a real directory and strand whatever" >&2
    echo "it points at. Nothing was written. Resolve these first:" >&2
    printf '%s\n' "$symlinked" | head -5 >&2
    exit 1
  fi

  # (3) An evidence path that already exists UNTRACKED and DIFFERS from the
  #     manifest — an edited earlier restore, or regenerated output parked at
  #     the same path. `git ls-files` cannot see those, so they are checked by
  #     digest. Untracked files that already MATCH are not a collision:
  #     re-running the restore over them is a no-op, which keeps the command
  #     idempotent.
  present=""
  scratch_file present
  present_untracked_rows "$present"
  if [[ -s "$present" ]]; then
    if ! (cd "$REPO_ROOT" && sha256_check "$present"); then
      echo "" >&2
      echo "Files listed above already exist and do NOT match the manifest;" >&2
      echo "restoring would overwrite them. Nothing was written. Move them" >&2
      echo "aside, or discard them with 'fetch_evidence.sh --clean --force'." >&2
      exit 1
    fi
    echo "$(wc -l < "$present" | tr -d ' ') file(s) already restored and matching; re-restoring is a no-op."
  fi

  echo "Restoring coevo/ -> training/artifacts/coevo/ ..."
  git -C "$REPO_ROOT" archive "$PINNED_SHA" coevo |
    tar -x --strip-components=1 -C "$COEVO_DEST"

  echo "Restoring finalist-eval-raw/ -> training/reports/_finalist_eval_raw/ ..."
  git -C "$REPO_ROOT" archive "$PINNED_SHA" finalist-eval-raw |
    tar -x --strip-components=1 -C "$SLATE_DEST"
fi

# --------------------------------------------------------------------------- #
# verify                                                                       #
# --------------------------------------------------------------------------- #
digests=""
scratch_file digests
peel_digests > "$digests"
expected="$(wc -l < "$digests" | tr -d ' ')"

missing="$(while IFS= read -r rel; do
  if [[ ! -f "$REPO_ROOT/$rel" ]]; then printf '%s\n' "$rel"; fi
done < <(restored_paths) | wc -l | tr -d ' ')"
if [[ "$missing" != "0" ]]; then
  echo "$missing of $expected evidence file(s) are not present." >&2
  echo "Run 'bash scripts/fetch_evidence.sh' to restore them by the pinned sha." >&2
  exit 1
fi

echo "Verifying $expected restored file(s) against the manifest ..."
(cd "$REPO_ROOT" && sha256_check "$digests")

# The branch's own README is manifest-covered too, but it is branch metadata
# and is not restored into the tree — so it is checked straight out of the
# commit, which keeps "every file the evidence commit carries has a digest"
# literally true rather than true-except-one. If the commit object is not here,
# that file cannot be covered, and reporting a clean 2,952 would quietly
# under-deliver on what the manifest promises — so it FAILS instead of skipping
# (Codex review on PR #346; AGENTS.md "no silent fallbacks").
if ! git -C "$REPO_ROOT" cat-file -e "${PINNED_SHA}:README.md" 2>/dev/null; then
  echo "The pinned commit ${PINNED_SHA} is not in this repository, so the" >&2
  echo "evidence branch's own README.md cannot be verified and $expected of the" >&2
  echo "manifest's $((expected + 1)) files would be covered. Run" >&2
  echo "'bash scripts/fetch_evidence.sh' — it fetches the commit and pins it" >&2
  echo "locally at ${LOCAL_REF}, after which --verify works offline." >&2
  exit 1
fi
readme_expected="$(awk '/^```sha256$/{f=1;next} /^```$/{f=0} f' "$MANIFEST" |
  awk '$2 == "README.md" {print $1}')"
readme_actual="$(git -C "$REPO_ROOT" cat-file blob "${PINNED_SHA}:README.md" |
  sha256_stdin)"
if [[ "$readme_expected" != "$readme_actual" ]]; then
  echo "The evidence commit's README.md does not match its manifest digest." >&2
  exit 1
fi
expected=$((expected + 1))

echo "OK: $expected/$expected files match ${PINNED_SHA}."
echo "These bytes are UNTRACKED BY DESIGN — do not commit them back."
echo "Remove them again with: bash scripts/fetch_evidence.sh --clean"
