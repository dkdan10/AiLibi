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
# Usage:
#   scripts/fetch_evidence.sh            fetch by the pinned sha, restore, verify
#   scripts/fetch_evidence.sh --verify   verify what is already restored
#   scripts/fetch_evidence.sh --clean    remove the restored bytes again
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
case "${1:-}" in
  "") ;;
  --verify) mode="verify" ;;
  --clean) mode="clean" ;;
  -h | --help)
    sed -n '3,27p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  *)
    echo "unknown argument '$1' (expected nothing, --verify, --clean or --help)" >&2
    exit 2
    ;;
esac

# sha256sum (GNU) or shasum -a 256 (macOS). Both read the same manifest format —
# that is why the manifest is written shasum-compatible.
if command -v sha256sum >/dev/null 2>&1; then
  sha256_check() { sha256sum -c --quiet "$1"; }
  sha256_stdin() { sha256sum | cut -d' ' -f1; }
elif command -v shasum >/dev/null 2>&1; then
  sha256_check() { shasum -a 256 -c "$1" >/dev/null; }
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
  sha="$(grep -F 'tip sha — THE PIN' "$MANIFEST" |
    grep -oE '[0-9a-f]{40}' | head -1)"
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

# One cleanup list and one trap: several legs below need scratch files, and a
# second `trap ... EXIT` would silently replace the first and leak the earlier
# file.
_scratch=()
cleanup() {
  if [[ ${#_scratch[@]} -gt 0 ]]; then rm -f "${_scratch[@]}"; fi
}
trap cleanup EXIT
scratch_file() {
  local f
  f="$(mktemp)"
  _scratch+=("$f")
  printf '%s\n' "$f"
}

# --------------------------------------------------------------------------- #
# clean                                                                        #
# --------------------------------------------------------------------------- #
if [[ "$mode" == "clean" ]]; then
  # Tracked paths are never removed, whatever the manifest lists. The two sets
  # are disjoint by construction; this makes "--clean cannot delete your
  # checkout" true by code rather than by that construction holding.
  tracked="$(scratch_file)"
  git -C "$REPO_ROOT" ls-files -- training/artifacts/coevo \
    training/reports/_finalist_eval_raw | sort > "$tracked"
  removed=0
  while IFS= read -r rel; do
    if [[ -f "$REPO_ROOT/$rel" ]] && ! grep -qxF "$rel" "$tracked"; then
      rm -f "$REPO_ROOT/$rel"
      removed=$((removed + 1))
    fi
  done < <(restored_paths)
  # Only directories the restore created can end up empty; tracked files keep
  # their own directories alive, so this never removes an in-tree path.
  find "$COEVO_DEST" "$SLATE_DEST" -mindepth 1 -type d -empty -delete 2>/dev/null || true
  echo "Removed $removed restored file(s). Tracked bytes are untouched."
  exit 0
fi

# --------------------------------------------------------------------------- #
# fetch + restore                                                              #
# --------------------------------------------------------------------------- #
PINNED_SHA="$(read_pin)"

if [[ "$mode" == "fetch" ]]; then
  if ! git -C "$REPO_ROOT" cat-file -e "${PINNED_SHA}^{commit}" 2>/dev/null; then
    remote_url="$(git -C "$REPO_ROOT" remote get-url origin)"
    echo "Fetching the evidence commit ${PINNED_SHA} from ${remote_url} ..."
    git -C "$REPO_ROOT" fetch --depth 1 "$remote_url" "$PINNED_SHA"
  fi
  # The pin buys immutability only if what came back really is the ONE-commit
  # orphan the manifest describes — asserted loudly, before a single byte lands
  # in the tree. Read from the RAW commit object, not from `rev-list --parents`:
  # a --depth 1 fetch makes the commit a shallow boundary, and rev-list then
  # suppresses its parents and reports any parented commit as an orphan
  # (Codex review on PR #346, reproduced against a two-commit repo).
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
  # Two ways that could happen, both refused BEFORE anything is written:
  #
  #   1. an evidence path that is also a TRACKED path — the moved and retained
  #      sets are disjoint by construction (EVIDENCE-MANIFEST.md §3), so this
  #      means the manifest and the commit have drifted apart, which is the one
  #      failure this whole scheme exists to make impossible to miss;
  #   2. an evidence path that already exists UNTRACKED and differs from the
  #      manifest — an edited earlier restore, or regenerated output parked at
  #      the same path. `git ls-files` cannot see those (Codex review on PR
  #      #346), so they are checked by digest. Untracked files that already
  #      MATCH the manifest are not a collision: re-running the restore over
  #      them is a no-op, which keeps the command idempotent.
  overlap="$(comm -12 <(restored_paths | sort) \
    <(git -C "$REPO_ROOT" ls-files -- training/artifacts/coevo \
      training/reports/_finalist_eval_raw | sort))"
  if [[ -n "$overlap" ]]; then
    echo "The evidence commit carries paths that are ALSO tracked in-tree;" >&2
    echo "the manifest and the commit disagree. Nothing was written." >&2
    printf '%s\n' "$overlap" | head -5 >&2
    exit 1
  fi

  present="$(scratch_file)"
  # `if`, not `&&`: a final iteration whose test is false would make the loop —
  # and so the pipeline — return 1, and `set -e` would kill the script here with
  # no output at all.
  peel_digests | while IFS= read -r row; do
    if [[ -f "$REPO_ROOT/${row#*  }" ]]; then printf '%s\n' "$row"; fi
  done > "$present"
  if [[ -s "$present" ]]; then
    if ! (cd "$REPO_ROOT" && sha256_check "$present"); then
      echo "" >&2
      echo "Files listed above already exist and do NOT match the manifest;" >&2
      echo "restoring would overwrite them. Nothing was written. Remove or move" >&2
      echo "them (or run 'bash scripts/fetch_evidence.sh --clean') and retry." >&2
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
digests="$(scratch_file)"
peel_digests > "$digests"
expected="$(wc -l < "$digests" | tr -d ' ')"

missing="$(while IFS= read -r rel; do
  [[ -f "$REPO_ROOT/$rel" ]] || printf '%s\n' "$rel"
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
