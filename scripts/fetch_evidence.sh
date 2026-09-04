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
#     The restore writes a .gitignore at each destination root so `git add -A`
#     cannot stage them; `--clean` removes both; `docs/artifacts.md` states the
#     rule.
#
# Nothing here overwrites or deletes a byte it cannot re-fetch. Every mode
# refuses, before touching anything, on: a symlink anywhere along a destination
# path (the off-volume layout), a manifest path that is also tracked, or a local
# file whose digest differs from the manifest. `--clean` removes only files that
# still match, and the restore leaves the metadata of existing directories alone.
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
# Task 21.24's FINDING record — a SECOND evidence family on its own orphan
# commit. Its 300 recorded games read only with the three Wave-2 levers ON,
# so they cannot live under the canonical replay roots and are pinned here.
WAVE2_MANIFEST="$REPO_ROOT/replays/records/phase-21-wave2-finding/EVIDENCE-MANIFEST.md"
WAVE2_DEST="$REPO_ROOT/replays/records/phase-21-wave2-finding"

# Where the fetched commit is pinned locally. A fetch with no ref leaves the
# objects unreachable, so a later `git gc` may prune them and a subsequent
# offline --verify would lose the branch README it must check. NOT under
# refs/heads: this is a pinned object, not a branch to work on.
LOCAL_REF="refs/evidence/phase-18-coevo"
WAVE2_LOCAL_REF="refs/evidence/phase-21-wave2-finding"

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
else
  if ! command -v shasum >/dev/null 2>&1; then
    echo "neither sha256sum nor shasum is available; cannot verify" >&2
    exit 1
  fi
  sha256_check() { shasum -a 256 -c "$1" >/dev/null; }
  sha256_report() { shasum -a 256 -c "$1" 2>/dev/null || true; }
  sha256_stdin() { shasum -a 256 | cut -d' ' -f1; }
fi

# stat(1) is not portable: GNU spells the mode %a, BSD spells it %Lp.
if stat -c '%a' . >/dev/null 2>&1; then
  file_mode() { stat -c '%a' "$1"; }
  file_owner() { stat -c '%u:%g' "$1"; }
else
  file_mode() { stat -f '%Lp' "$1"; }
  file_owner() { stat -f '%u:%g' "$1"; }
fi

# --------------------------------------------------------------------------- #
# The pin, and the digest block, both read from the manifest.                  #
# --------------------------------------------------------------------------- #
read_pin() { # read_pin [MANIFEST]
  local manifest="${1:-$MANIFEST}" sha
  # `|| true`: with `set -o pipefail` a no-match grep fails the whole
  # substitution and kills the script BEFORE the diagnostic below can explain
  # why — the corrupt-manifest case would exit silently (Codex review, PR #346).
  sha="$(grep -F 'tip sha — THE PIN' "$manifest" |
    grep -oE '[0-9a-f]{40}' | head -1 || true)"
  if [[ -z "$sha" ]]; then
    echo "no pinned sha in $manifest (the '**tip sha — THE PIN**' row)" >&2
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
  # The FINDING record's block. Its branch README is dropped for the same reason
  # the coevo one is — and here it MUST be: its destination would be the in-tree
  # wrapper README of the same name, so restoring it would overwrite the very
  # file docs/artifacts.md registers.
  awk '/^```sha256$/{f=1;next} /^```$/{f=0} f' "$WAVE2_MANIFEST" |
    grep -v '  wave2-finding/README.md$' |
    sed 's#  wave2-finding/#  replays/records/phase-21-wave2-finding/#'
}

restored_paths() {
  peel_digests | sed 's/^[0-9a-f]\{64\}  //'
}

# Every directory the restore writes into — EVERY prefix, not just each file's
# immediate parent. `intermediates/`, `runnerups/` and the `realpath-*` roots
# hold retained tracked files but no moved file directly, so an
# immediate-parents-only list left 13 existing directories out of the
# mode-preservation pass below (Codex review, PR #346).
dest_dirs() {
  # Confined to the two destination roots: the prefix expansion also yields
  # `training/` and `training/artifacts/`, which sit ABOVE the `tar -C` roots
  # and so can never be written by a restore. They are dropped rather than
  # merely harmless, so neither the mode pass nor `--clean`'s pruning reaches a
  # directory this script does not own.
  restored_paths |
    awk -F/ '{p=""; for (i=1; i<NF; i++) {p = (i==1 ? $i : p "/" $i); print p}}' |
    grep -E '^(training/artifacts/coevo|training/reports/_finalist_eval_raw|replays/records/phase-21-wave2-finding)/' |
    sort -u
}

# The two `tar -C` targets themselves. Deliberately NOT part of dest_dirs —
# that list also drives `--clean`'s pruning, which must never try to rmdir a
# destination root. They still need the mtime bookkeeping below: tar writes into
# them, and GNU tar's default --overwrite unlinks and recreates each file, which
# moves the root's mtime even on a re-fetch that adds nothing (found while
# verifying the round-6 fix, PR #346).
dest_roots() {
  printf '%s\n' "${COEVO_DEST#"$REPO_ROOT/"}" "${SLATE_DEST#"$REPO_ROOT/"}" \
    "${WAVE2_DEST#"$REPO_ROOT/"}"
}

tracked_paths() {
  git -C "$REPO_ROOT" ls-files -- training/artifacts/coevo \
    training/reports/_finalist_eval_raw \
    replays/records/phase-21-wave2-finding | sort
}

# One cleanup list and one trap: several legs below need scratch files, and a
# second `trap ... EXIT` would silently replace the first and leak the earlier
# file. The path is returned through a caller-named variable rather than on
# stdout, because `f="$(scratch_file)"` runs the function in a SUBSHELL — the
# array would grow there and the parent's trap would clean nothing (Codex
# review, PR #346). `printf -v` keeps this working on bash 3.2 too.
_scratch=()
# 1 only between "the first byte may now be written" and "the restore
# finished". An extraction that dies inside that window — a full disk, a killed
# tar — otherwise exits under `set -e` BEFORE the directory metadata is put
# back, leaving tracked-tree directories carrying the archive's mode and date:
# the corruption rounds 3 and 5 fixed, resurrected on the failure path (Codex
# review, PR #346; reproduced by capping the file size mid-restore).
_restore_started=0
cleanup() {
  if [[ "$_restore_started" == "1" ]]; then
    restore_dir_metadata || true
    echo "" >&2
    echo "The restore did NOT finish — the destinations hold a PARTIAL copy of" >&2
    echo "the evidence. Directory metadata has been put back, and the .gitignore" >&2
    echo "written at each destination BEFORE extraction keeps the partial bytes" >&2
    echo "out of 'git add -A'. Clear them with:" >&2
    echo "  bash scripts/fetch_evidence.sh --clean          # whole files" >&2
    echo "  bash scripts/fetch_evidence.sh --clean --force  # + any half-written one" >&2
  fi
  if [[ ${#_scratch[@]} -gt 0 ]]; then rm -rf "${_scratch[@]}"; fi
}
trap cleanup EXIT
scratch_file() { # scratch_file VARNAME
  local f
  f="$(mktemp)"
  _scratch+=("$f")
  printf -v "$1" '%s' "$f"
}

# --------------------------------------------------------------------------- #
# Guard: every destination path is absent, or is the plain thing we expect.     #
# --------------------------------------------------------------------------- #
# `tar -x` and `rm -f` both walk straight through anything unexpected sitting on
# a destination path, and the shell tests that would notice are the ones that
# follow links. Two families, both refused in EVERY mode — `--clean` included —
# before any candidate is collected (Codex review, PR #346):
#
#   * SYMLINKS, leaf or ancestor. Parking the ~399 MiB payload on another volume
#     behind a link is a layout an operator may reasonably choose; `tar`
#     REPLACES the link with a real entry (verified against GNU tar 1.35) and
#     `[[ -f … ]]` follows it, so a plain `--clean` would delete the off-volume
#     file.
#   * NON-REGULAR entries: a FIFO, socket or device where a file belongs (tar
#     silently replaces a FIFO with a regular file — verified), a directory
#     where a file belongs (extraction fails partway, after earlier entries have
#     landed), or a non-directory where a directory belongs. `[[ -f … ]]` is
#     FALSE for all of these, so the digest collision check never saw them.
#
# Expanding each manifest path into its own prefixes covers the leaf and every
# ancestor in one pass; `-L` is tested first because `-e` follows links.
assert_destination_paths_are_plain() {
  local offenders
  offenders="$(restored_paths |
    awk -F/ '{p=""; for (i=1; i<NF; i++) {p = (i==1 ? $i : p "/" $i); print "dir " p} print "file " $0}' |
    sort -u |
    while IFS=' ' read -r kind p; do
      if [[ -L "$REPO_ROOT/$p" ]]; then
        printf '%s — symlink\n' "$p"
      elif [[ "$kind" == "dir" && -e "$REPO_ROOT/$p" && ! -d "$REPO_ROOT/$p" ]]; then
        printf '%s — exists but is not a directory\n' "$p"
      elif [[ "$kind" == "file" && -e "$REPO_ROOT/$p" && ! -f "$REPO_ROOT/$p" ]]; then
        printf '%s — exists but is not a regular file\n' "$p"
      fi
    done)"
  if [[ -n "$offenders" ]]; then
    echo "A destination path is not what it must be. Extracting would replace" >&2
    echo "it (and strand whatever it stands for); cleaning would delete it." >&2
    echo "Nothing was touched. Resolve these first:" >&2
    printf '%s\n' "$offenders" | head -5 >&2
    exit 1
  fi
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

# The restored bytes are untracked, and nothing in .gitignore covers them, so a
# routine `git add -A` would stage up to 399 MiB of class-(c) evidence straight
# back into the tree the prune emptied. A terminal warning is not an enforcement
# mechanism (Codex review, PR #346), so the restore writes one of these at each
# destination root. Tracked files are unaffected by an ignore rule, so the
# retained in-tree bytes keep showing up in `git status` exactly as before.
#
# These two paths are NOT in the manifest, so they bypass the guards above and
# need their own: this script writes and deletes only files it can prove it
# wrote, identified by the marker on their first line. Anything else at that
# path — an operator's own ignore rules, or a symlink pointing off-tree that a
# redirection would truncate — refuses the run (Codex review, PR #346).
GITIGNORE_MARKER="# fetch_evidence.sh-owned — safe to delete (Task 19.22)"

gitignore_is_ours() { # gitignore_is_ours PATH
  [[ ! -L "$1" ]] && [[ -f "$1" ]] && [[ "$(head -1 "$1")" == "$GITIGNORE_MARKER" ]]
}

assert_gitignores_are_ours_or_absent() {
  local dest offenders=""
  for dest in "$COEVO_DEST" "$SLATE_DEST" "$WAVE2_DEST"; do
    if [[ -L "$dest/.gitignore" ]]; then
      offenders+="${dest#"$REPO_ROOT/"}/.gitignore — symlink"$'\n'
    elif [[ -e "$dest/.gitignore" ]] && ! gitignore_is_ours "$dest/.gitignore"; then
      offenders+="${dest#"$REPO_ROOT/"}/.gitignore — not written by this script"$'\n'
    fi
  done
  if [[ -n "$offenders" ]]; then
    echo "A destination already has its own .gitignore. This script only writes" >&2
    echo "and removes ignore files it wrote itself, so it will not touch these:" >&2
    printf '%s' "$offenders" >&2
    echo "Move them aside first (the restored bytes must stay unstageable)." >&2
    exit 1
  fi
}

# The canonical body for ONE destination, defined once so the skip test below
# can compare against it byte for byte instead of sampling a line.
#
# The rules name the restored files ONE BY ONE, anchored, rather than the `*`
# this used to write. `*` ignored the whole directory, so an unrelated untracked
# file an operator had left in a destination vanished from `git status` and from
# `git add -A` — this script hiding local work it does not own (Codex review,
# PR #346). None of the 2,952 manifest paths contains a gitignore
# metacharacter, checked, so each path is its own literal rule.
gitignore_body() { # gitignore_body DEST_REL
  cat <<IGNORE
$GITIGNORE_MARKER
#
# Each line below is one RESTORED CLASS-(c) EVIDENCE file: it lives on the
# pinned evidence commit (training/artifacts/coevo/EVIDENCE-MANIFEST.md) and
# must never be committed back here (docs/artifacts.md). This file exists so
# \`git add -A\` cannot stage them. Tracked files are unaffected by ignore rules,
# so the retained in-tree bytes still show up in \`git status\` — and so does
# anything else you leave here, which is why these rules are per-file.
#
# \`bash scripts/fetch_evidence.sh --clean\` removes the restored bytes and this
# file with them.
IGNORE
  # This file itself. The blanket `*` used to cover it implicitly; per-file
  # rules do not, and without this line the generated ignore file is itself an
  # untracked file that `git add -A` would stage (caught while verifying the
  # round-9 fix, PR #346).
  printf '/.gitignore\n'
  restored_paths | grep "^$1/" | sed "s#^$1/#/#" | sort
}

# What is actually untracked under a destination right now — read from the
# filesystem and `git ls-files`, with no reference to the manifest. `--clean`
# decides whether to keep an ignore file from THIS, because deriving it from
# `restored_paths` meant a truncated manifest could leave real evidence on disk
# while the same truncated list reported nothing was left (Codex review,
# PR #346).
untracked_under() { # untracked_under DEST_REL
  comm -23 \
    <(find "$REPO_ROOT/$1" \( -type f -o -type l \) |
      sed "s#^$REPO_ROOT/##" |
      grep -v "^$1/\.gitignore" |
      sort) \
    <(git -C "$REPO_ROOT" ls-files -- "$1" | sort)
}

write_gitignore() { # write_gitignore DEST
  local dest="$1" tmp rel
  rel="${dest#"$REPO_ROOT/"}"
  # Skip ONLY on an exact match with the canonical body. "Has our marker and a
  # line that is `*`" was not strong enough: gitignore(5) gives the LAST
  # matching pattern precedence, so an appended `!some-evidence-file` re-includes
  # that file while still passing the spot check, and the payload this script
  # claims to protect is stageable again (Codex review, PR #346). Anything not
  # byte-identical — edited, truncated, negated — is rewritten.
  if [[ ! -L "$dest/.gitignore" ]] && [[ -f "$dest/.gitignore" ]] &&
    [[ "$(cat "$dest/.gitignore")" == "$(gitignore_body "$rel")" ]]; then
    return 0
  fi
  # Build beside the target and rename it into place: rename(2) within a single
  # directory is atomic, so a reader sees the old file or the complete new one
  # and never a half-written one. The sibling is made by `mktemp`, not by a
  # PID-predictable name — a symlink parked at a predictable name would be
  # FOLLOWED by the redirect and its target truncated, off-tree and outside
  # every destination guard (Codex review, PR #346). mktemp creates exclusively,
  # so it neither follows a link nor clobbers an existing entry.
  tmp="$(mktemp "$dest/.gitignore.XXXXXX")"
  _scratch+=("$tmp")
  gitignore_body "$rel" > "$tmp"
  chmod 644 "$tmp"
  mv -f "$tmp" "$dest/.gitignore"
}

# The manifest is the allowlist EVERY guard is built from — the collision scan,
# the type guard, the expected verify count — and nothing checked that it
# actually enumerates the archive. A truncated digest block with the pin still
# readable therefore shrank every guard silently while `git archive` went on
# extracting the whole tree: reproduced by dropping ONE row, after which tar
# overwrote an unrelated untracked file no guard had preflighted, and the run
# still reported `OK: 2952/2952` (Codex review, PR #346).
archive_paths() {
  git -C "$REPO_ROOT" ls-tree -r --name-only "$PINNED_SHA" |
    grep -v '^README.md$' |
    sed -e 's#^coevo/#training/artifacts/coevo/#' \
      -e 's#^finalist-eval-raw/#training/reports/_finalist_eval_raw/#'
  # The second family's commit, listed the same way. Its README is dropped here
  # too, so this list and peel_digests describe the same set on both sides.
  git -C "$REPO_ROOT" ls-tree -r --name-only "$WAVE2_PINNED_SHA" |
    grep -v '^README.md$' |
    sed 's#^#replays/records/phase-21-wave2-finding/#'
}

# Called by the two modes that have the commit in hand. `--clean` is offline by
# design and returns long before this, so it cannot make the comparison — and it
# does not need to: it removes only what already matches a digest.
assert_archive_matches_manifest() {
  local only_archive only_manifest
  only_archive="$(comm -23 <(archive_paths | sort) <(restored_paths | sort))"
  only_manifest="$(comm -13 <(archive_paths | sort) <(restored_paths | sort))"
  if [[ -n "$only_archive" ]] || [[ -n "$only_manifest" ]]; then
    echo "The pinned commit and the manifest describe DIFFERENT file sets, so" >&2
    echo "the manifest cannot be used as the allowlist. Refusing." >&2
    if [[ -n "$only_archive" ]]; then
      echo "  in the commit but NOT in the manifest ($(printf '%s\n' "$only_archive" | wc -l | tr -d ' ')):" >&2
      printf '%s\n' "$only_archive" | head -5 | sed 's/^/    /' >&2
    fi
    if [[ -n "$only_manifest" ]]; then
      echo "  in the manifest but NOT in the commit ($(printf '%s\n' "$only_manifest" | wc -l | tr -d ' ')):" >&2
      printf '%s\n' "$only_manifest" | head -5 | sed 's/^/    /' >&2
    fi
    exit 1
  fi
}

# The directory mode/mtime pass, shared by the success path and the EXIT trap so
# a half-finished restore cannot leave the tracked tree stamped by the archive.
# Reads two scratch files captured BEFORE extraction: $modes (mode + stamp id +
# path, for the destination directories that already existed) and $absent
# (gaining-directory + entry, for every entry that was not on disk yet).
restore_dir_metadata() {
  local gained want stamp d parent child repaired n=0 failed=0 know_gains=1
  restored_meta=0
  # NOTHING is allocated in here. This also runs from the EXIT trap on the
  # disk-full path, where /tmp is very often the filesystem that just filled, so
  # a `mktemp` fails exactly when it is needed most — and because `cleanup`
  # calls this as `restore_dir_metadata || true`, bash suppresses errexit for
  # the whole function: the failed allocation stopped nothing, the redirect died
  # silently, every gain test read false, and directories that HAD received
  # entries were handed back their pre-restore date while the script announced
  # the metadata was repaired. Reproduced by fault injection (Codex review,
  # PR #346). That is a silent fallback producing a wrong answer, which
  # AGENTS.md forbids outright, so the gain set now lives in a shell variable
  # and every failure below is counted and reported rather than swallowed.
  if [[ ! -r "$modes" ]]; then
    echo "WARNING: the captured directory modes are unreadable, so NO directory" >&2
    echo "metadata could be repaired; directories keep whatever the extraction" >&2
    echo "left them ($modes)." >&2
    return 0
  fi

  # A directory GAINED an entry iff one of the entries that was absent before
  # extraction is on disk now. Deciding that from the ENTRIES, rather than from
  # each restored file's immediate parent, is what makes it right in three cases
  # the parents-only list got wrong (Codex review, PR #346, both halves
  # reproduced): a directory that gains only a new SUBDIRECTORY changed just as
  # surely as one that gains a file (`intermediates/` gains
  # `run-03-utility-bcanchor/` and `run-04-freepolicy-v3/` and nothing else — 6
  # such directories here, all of them handed back their OLD mtime); a re-fetch
  # that adds nothing must move NO mtime, where the old list moved 462; and a
  # restore that aborted part-way counts only what actually landed.
  gained=$'\n'
  if [[ -r "$absent" ]]; then
    while IFS=$'\t' read -r parent child; do
      if [[ -e "$REPO_ROOT/$child" ]] &&
        [[ "$gained" != *$'\n'"$parent"$'\n'* ]]; then
        gained+="$parent"$'\n'
      fi
    done < "$absent"
  else
    know_gains=0
    echo "WARNING: the pre-extraction entry record is unreadable, so which" >&2
    echo "directories gained entries cannot be established. Modes are still" >&2
    echo "repaired, and every captured directory is stamped NOW ($absent)." >&2
  fi

  while read -r want owner stamp d; do
    if [[ -d "$REPO_ROOT/$d" ]]; then
      repaired=0
      if [[ "$(file_mode "$REPO_ROOT/$d")" != "$want" ]]; then
        if chmod "$want" "$REPO_ROOT/$d" 2>/dev/null; then
          repaired=1
        else
          failed=$((failed + 1))
        fi
      fi
      if [[ "$(file_owner "$REPO_ROOT/$d")" != "$owner" ]]; then
        if chown "$owner" "$REPO_ROOT/$d" 2>/dev/null; then
          repaired=1
        else
          failed=$((failed + 1))
        fi
      fi
      if [[ "$know_gains" == "1" ]]; then
        if [[ "$gained" == *$'\n'"$d"$'\n'* ]]; then
          # It really did gain entries, so its mtime moved — to now, which is
          # when that happened, rather than to the evidence commit's date.
          touch "$REPO_ROOT/$d" 2>/dev/null || failed=$((failed + 1))
        elif touch -r "$stamps/$stamp" "$REPO_ROOT/$d" 2>/dev/null; then
          repaired=1
        else
          failed=$((failed + 1))
        fi
      else
        # Gains unknown. NOW is the one timestamp certainly true of this tree —
        # the extraction just ran through it. Leaving tar's value would keep a
        # date fabricated by the archive (the thing this whole pass exists to
        # remove), and restoring every original would backdate whatever really
        # did gain entries.
        touch "$REPO_ROOT/$d" 2>/dev/null || failed=$((failed + 1))
      fi
      if [[ "$repaired" == "1" ]]; then n=$((n + 1)); fi
    fi
  done < "$modes"
  restored_meta="$n"
  if [[ "$failed" != "0" ]]; then
    echo "WARNING: $failed directory metadata repair(s) FAILED — those" >&2
    echo "directories keep the mode or date the extraction left on them." >&2
  fi
}

# EVERY mode runs this, and it is called HERE — once, before any mode branches —
# rather than inside each branch. Three rounds of review found the same defect
# shape (a guard added to restore but not clean, to directories but not leaves,
# to immediate parents but not ancestors), and `--verify` was the next instance:
# it followed a symlinked path and reported the payload fully restored. A single
# unconditional call is what stops that class, rather than remembering to repeat
# it (Codex review, PR #346).
assert_destination_paths_are_plain

# --------------------------------------------------------------------------- #
# clean                                                                        #
# --------------------------------------------------------------------------- #
if [[ "$mode" == "clean" ]]; then
  assert_gitignores_are_ours_or_absent

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

  # The ignore file goes only when the payload it protects is actually gone.
  # Removing it unconditionally meant a --clean that KEPT a modified evidence
  # file (the case above, which exits non-zero) left that file behind with
  # nothing stopping `git add -A` from staging it (Codex review, PR #346).
  for dest in "$COEVO_DEST" "$SLATE_DEST" "$WAVE2_DEST"; do
    rel="${dest#"$REPO_ROOT/"}"
    # Counted from the FILESYSTEM, not from the manifest. `--clean` is offline
    # and cannot run the archive/manifest comparison, so a manifest truncated
    # after the restore would report "nothing left" from the same short list
    # that hid the leftovers — and this branch would then remove the ignore file
    # protecting them (Codex review, PR #346).
    left="$(untracked_under "$rel" | wc -l | tr -d ' ')"
    if [[ "$left" -eq 0 ]]; then
      if gitignore_is_ours "$dest/.gitignore"; then
        rm -f "$dest/.gitignore"
      fi
    else
      # Keeping it is not enough: an owned file that had been truncated or had a
      # negation appended was kept AS-IS and reported as protecting a payload it
      # no longer covered. Rewrite it to canonical, which is a no-op when it
      # already is (Codex review, PR #346).
      write_gitignore "$dest"
      echo "Kept $rel/.gitignore — $left untracked evidence file(s) remain there." >&2
    fi
  done

  # Only directories this restore could have created, deepest first, and only
  # when empty. A blanket `find -type d -empty -delete` over the destinations
  # would also delete an unrelated empty directory the user put there, which is
  # local state this script does not own (Codex review, PR #346).
  dest_dirs |
    awk -F/ '{p=""; for (i=1; i<=NF; i++) {p = (i==1 ? $i : p "/" $i); print p}}' |
    sort -ru |
    while IFS= read -r d; do
      rmdir "$REPO_ROOT/$d" 2>/dev/null || true
    done

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
WAVE2_PINNED_SHA="$(read_pin "$WAVE2_MANIFEST")"

if [[ "$mode" == "fetch" ]]; then
  # Every evidence family, one loop. The pin buys immutability only if what came
  # back really is the ONE-commit orphan its manifest describes — asserted
  # loudly, before a single byte lands in the tree. Read from the RAW commit
  # object, not from `rev-list --parents`: a --depth 1 fetch makes the commit a
  # shallow boundary, and rev-list then suppresses its parents and reports any
  # parented commit as an orphan (Codex review on PR #346, reproduced against a
  # two-commit repo). The `sed` stops at the header/body boundary so a
  # "parent ..." line in a commit MESSAGE cannot masquerade as a header.
  #
  # Each object is then pinned locally so `git gc` cannot prune it: a bare sha
  # fetch leaves it unreachable, and a later offline --verify needs the commit to
  # check the branch README its manifest also covers.
  for family in "$PINNED_SHA $LOCAL_REF" "$WAVE2_PINNED_SHA $WAVE2_LOCAL_REF"; do
    sha="${family%% *}"
    ref="${family##* }"
    if ! git -C "$REPO_ROOT" cat-file -e "${sha}^{commit}" 2>/dev/null; then
      # Fetch through the remote NAME, and print only the name. `git remote
      # get-url` can carry inline credentials (https://x-access-token:<PAT>@...),
      # and echoing it would write the secret to the terminal and to CI logs
      # (Codex review, PR #346).
      echo "Fetching the evidence commit ${sha} from origin ..."
      git -C "$REPO_ROOT" fetch --depth 1 origin "$sha"
    fi
    if git -C "$REPO_ROOT" cat-file commit "$sha" |
      sed -n '/^$/q;p' | grep -q '^parent '; then
      echo "${sha} has a parent header; the evidence commit is an orphan." >&2
      echo "Refusing to restore from it." >&2
      exit 1
    fi
    git -C "$REPO_ROOT" update-ref "$ref" "$sha"
  done

  # A restore may only ADD files, so nothing already on disk may be clobbered.
  # Three ways that could happen, all refused BEFORE anything is written.
  #
  # (1) The two generated .gitignore files are not manifest paths, so the
  #     mode-independent guard above cannot see them; they get their own
  #     ownership check, here and in --clean, the two modes that touch them.
  assert_gitignores_are_ours_or_absent

  # (2) An evidence path that is also a TRACKED path. The moved and retained
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

  # 33 of the archive's directories ALREADY EXIST, because they hold retained
  # tracked files. GNU tar's documented default is --overwrite-dir, so an
  # extraction rewrites their mode and mtime from the archive — git encodes
  # directories as 0775, so a 0755 checkout directory comes back 0775 and an
  # "add-only" restore has quietly relaxed permissions inside the tracked tree
  # (Codex review, PR #346; reproduced). Their modes are captured here and
  # reapplied below. Done by hand rather than with --no-overwrite-dir because
  # that flag is GNU-only and this script also supports the BSD side.
  modes=""
  scratch_file modes
  stamps="$(mktemp -d)"
  _scratch+=("$stamps")
  # The manifest is this restore's allowlist, so prove it matches the commit
  # BEFORE anything is captured or written.
  assert_archive_matches_manifest

  # A re-fetch must not rewrite files that are already correct. The preflight
  # has already refused unless every existing destination file matches its
  # digest, so anything present is by definition the right bytes — replacing it
  # discards whatever mode, owner or timestamp it carries locally, on a run the
  # collision path reports as a no-op (Codex review, PR #346). `--skip-old-files`
  # is GNU-only, so it is probed rather than assumed; without it the behaviour
  # falls back to replacing, exactly as before.
  TAR_SKIP=()
  if tar --skip-old-files --version >/dev/null 2>&1; then
    TAR_SKIP=(--skip-old-files)
  fi

  # Mode AND mtime. tar rewrites both from the archive, so a directory that
  # already existed came back stamped with the evidence commit's timestamp —
  # a fabricated past date on a tracked-tree directory (Codex review, PR #346).
  # `touch -r` carries the timestamp portably, with no strftime parsing.
  i=0
  while IFS= read -r d; do
    if [[ -d "$REPO_ROOT/$d" ]]; then
      i=$((i + 1))
      touch -r "$REPO_ROOT/$d" "$stamps/$i"
      # Owner too, not just mode: `--same-owner` is tar's default for the
      # superuser, so a root restore rewrote the uid/gid of every pre-existing
      # directory it extracted into — reproduced, 65534:65534 -> 0:0 on a
      # directory that was only GAINING entries (Codex review, PR #346).
      printf '%s %s %s %s\n' "$(file_mode "$REPO_ROOT/$d")" \
        "$(file_owner "$REPO_ROOT/$d")" "$i" "$d" >> "$modes"
    fi
  done < <({ dest_roots; dest_dirs; })
  # Every entry the restore will materialise that is NOT on disk yet, recorded
  # as "the directory that will gain it" + "the entry itself". Files AND
  # directories, because a directory entry is a change to its parent too. This
  # is read back after extraction (`restore_dir_metadata`) to decide which
  # directories really changed, so the answer stays right whether the restore
  # adds everything, nothing, or — on the failure path — some of it.
  absent=""
  scratch_file absent
  { restored_paths; dest_dirs; } | sort -u | while IFS= read -r p; do
    if [[ ! -e "$REPO_ROOT/$p" ]]; then printf '%s\t%s\n' "${p%/*}" "$p"; fi
  done > "$absent"

  # The ignore files go down BEFORE the first byte, not after the last one.
  # Their whole job is to keep restored evidence out of `git add -A`, and the
  # bytes become stageable the moment tar starts writing — so an extraction that
  # dies half-way (a full disk) previously left ~1,877 untracked paths with
  # nothing stopping a commit (Codex review, PR #346; reproduced). Writing them
  # first also covers what no trap can: a SIGKILL, or the power going out.
  for dest in "$COEVO_DEST" "$SLATE_DEST" "$WAVE2_DEST"; do
    write_gitignore "$dest"
  done

  _restore_started=1

  echo "Restoring coevo/ -> training/artifacts/coevo/ ..."
  git -C "$REPO_ROOT" archive "$PINNED_SHA" coevo |
    tar -x ${TAR_SKIP[@]+"${TAR_SKIP[@]}"} --strip-components=1 -C "$COEVO_DEST"

  echo "Restoring finalist-eval-raw/ -> training/reports/_finalist_eval_raw/ ..."
  git -C "$REPO_ROOT" archive "$PINNED_SHA" finalist-eval-raw |
    tar -x ${TAR_SKIP[@]+"${TAR_SKIP[@]}"} --strip-components=1 -C "$SLATE_DEST"

  # The FINDING record's commit has no single top-level prefix directory — its
  # entries ARE the set directories — so this one extracts whole, with no
  # --strip-components, and the README is excluded because the destination
  # already holds the committed wrapper of that name.
  echo "Restoring wave2-finding/ -> replays/records/phase-21-wave2-finding/ ..."
  git -C "$REPO_ROOT" archive "$WAVE2_PINNED_SHA" |
    tar -x ${TAR_SKIP[@]+"${TAR_SKIP[@]}"} --exclude=README.md -C "$WAVE2_DEST"

  restore_dir_metadata
  _restore_started=0
  if [[ "$restored_meta" != "0" ]]; then
    echo "Repaired metadata on $restored_meta pre-existing director(ies)."
  fi
fi

# --------------------------------------------------------------------------- #
# verify                                                                       #
# --------------------------------------------------------------------------- #
# Also here, so `--verify` cannot report a green count that silently omits the
# rows a truncated manifest dropped. Cheap, and re-running it after a restore
# costs two `ls-tree`s rather than a per-mode conditional to get wrong.
assert_archive_matches_manifest

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

# The SECOND family's branch README, checked the same way and INDEPENDENTLY:
# against its own in-tree manifest, out of its own pinned commit. Sharing the
# first family's digest or pin here would report a green README for a branch
# nothing had looked at.
if ! git -C "$REPO_ROOT" cat-file -e "${WAVE2_PINNED_SHA}:README.md" 2>/dev/null; then
  echo "The pinned commit ${WAVE2_PINNED_SHA} is not in this repository, so the" >&2
  echo "recording's own README.md cannot be verified. Run" >&2
  echo "'bash scripts/fetch_evidence.sh' — it fetches the commit and pins it" >&2
  echo "locally at ${WAVE2_LOCAL_REF}, after which --verify works offline." >&2
  exit 1
fi
wave2_readme_expected="$(awk '/^```sha256$/{f=1;next} /^```$/{f=0} f' "$WAVE2_MANIFEST" |
  awk '$2 == "wave2-finding/README.md" {print $1}')"
wave2_readme_actual="$(git -C "$REPO_ROOT" cat-file blob "${WAVE2_PINNED_SHA}:README.md" |
  sha256_stdin)"
if [[ -z "$wave2_readme_expected" ]]; then
  echo "$WAVE2_MANIFEST carries no digest row for its branch README." >&2
  exit 1
fi
if [[ "$wave2_readme_expected" != "$wave2_readme_actual" ]]; then
  echo "The recording commit's README.md does not match its manifest digest." >&2
  exit 1
fi
expected=$((expected + 1))

echo "OK: $expected/$expected files match ${PINNED_SHA} + ${WAVE2_PINNED_SHA}."
echo "These bytes are UNTRACKED BY DESIGN and are .gitignore'd at each"
echo "destination root — do not commit them back."
echo "Remove them again with: bash scripts/fetch_evidence.sh --clean"
