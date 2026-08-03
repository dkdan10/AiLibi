# Agent Prompt — 6.6 Backend replay-loader efficiency, pagination, and corrupted-file resilience

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.6 — Backend replay-loader efficiency, pagination, and corrupted-file resilience, anchored to Audit G-G-2, G-G-3, H-H-2, H-H-3, K-K-8 (backend half); DESIGN.md §11.1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-replay-loader-efficiency-pagination`
**Depends on:** none
**Section refs:** Audit G-G-2, G-G-3, H-H-2, H-H-3, K-K-8 (backend half); DESIGN.md §11.1
**Complexity:** Medium

The replay loader re-parses files redundantly and has no pagination, which grows
linearly with the replay directory size (audit Class G/H). `cost_summary()`
reads each replay file twice (`api/replay_loader.py:236`), and
`list_replays()` → `_metadata_view` does two full reads plus two Pydantic passes
per file, none memoized — a 200-game directory is ~400 file parses per
`/eval/cost-summary` and per `/replays` request, re-globbed each call (G-G-2).
`GET /replays` has no limit/offset and builds a metadata view for every file in
one synchronous request (G-G-3). The per-process LRU cache key never incorporates
mtime, so an in-place replay rewrite (the refresh-samples workflow already does
this) serves stale data (H-H-2). And `update_manifest` does a non-atomic
read-modify-write with no lock, so a crash mid-write truncates the MANIFEST
(`scripts/_manifest_writer.py:314`, H-H-3).

This task reads each replay file once per request and derives both cost and
outcome from one `read_all_entries`; folds the double read in `_metadata_view`;
adds a per-file metadata cache keyed on `(path, mtime)` given the documented
immutability; folds mtime into the existing LRU cache key so an in-place refresh
invalidates correctly even pre-scale; adds optional `limit`/`offset` pagination to
`GET /replays`; and makes the manifest writer atomic via write-to-temp +
`os.replace`. The cross-worker shared cache and import-time loader construction
(H-H-6) remain documented scale-phase boundaries — do not build the shared cache
here.

This task also fixes the backend root-cause of the picker crash (K-K-8): today
`list_replays` does not catch `CorruptedFileError`, so a single corrupted replay
file throws an uncaught 500 that blocks the entire picker (`Task 4.16` made
`ReplayLog` raise `CorruptedFileError` on a malformed file). Make `list_replays`
tolerate a bad file: catch `CorruptedFileError` per file, exclude that file from
the listing, and emit a warning log so the corruption is recorded rather than
silently swallowed — the picker then still lists every healthy replay. This is
the server-side resilience fix only; the frontend's friendly error surfaces,
`aria-live` regions, and a dedicated corrupted-file UI are the other (a11y) half
of K-K-8 and stay in Phase 7 with the redesign.

**Files in scope:**
- api/replay_loader.py
- api/routes/replays.py
- scripts/_manifest_writer.py
- tests/api/test_replay_loader.py
- tests/scripts/test_manifest_writer.py

**Files NOT in scope:**
- api/main.py (Task 6.1; do not move import-time loader construction here)
- api/routes/eval.py (Task 6.5)
- api/schemas.py (Task 6.5)
- frontend/ (the frontend pagination/windowing is Task 6.7; the K-K-8 error-display/a11y half is Phase 7)
- replays/samples/ (no fixture regeneration)

**Definition of done:**
- [ ] `cost_summary()` and the metadata path read each replay file exactly once per request and derive both cost and outcome from a single `read_all_entries`; the double-read in `_metadata_view` is gone (G-G-2). A test asserts a single read per file (e.g. via a read counter/spy).
- [ ] A per-file metadata cache keyed on `(path, mtime)` memoizes the metadata view, given documented immutability; the existing per-process LRU cache key incorporates mtime so an in-place rewrite invalidates correctly (H-H-2). A test asserts a rewritten file (new mtime) is not served stale.
- [ ] `GET /replays` accepts optional `limit`/`offset` query params and slices `_replay_paths()` before building views; absent params preserve current behavior. A test covers pagination bounds (G-G-3).
- [ ] `update_manifest` (and the sibling `prune_manifest`/`rebuild_manifest`) write to a temp file and `os.replace` for atomicity; a crash mid-write cannot truncate the live MANIFEST (H-H-3). A test asserts the temp-then-replace path.
- [ ] No cross-worker shared cache is added (documented scale boundary, H-H-6); a comment marks the import-time loader construction as the scale boundary.
- [ ] `list_replays` catches `CorruptedFileError` per file, excludes the bad file from the listing, and logs a warning (not a silent drop), so one corrupted replay no longer 500s the whole picker (K-K-8 backend half). A test asserts that a directory containing one corrupted file still lists the healthy replays and logs the corruption.
- [ ] No behavior change to served DTO shapes; existing route tests pass unchanged.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `api/replay_loader.py` (the `cost_summary` double read at line 236, the
`_metadata_view` reads at line ~216, the LRU caches `_cached_load`/
`_cached_memories` at line ~209), `api/routes/replays.py` (the `GET /replays`
handler), and `scripts/_manifest_writer.py:314` (`update_manifest`). Derive cost
and outcome from one parsed entry list rather than two passes. For the cache key,
fold `path.stat().st_mtime_ns` into the key so an in-place rewrite is a cache
miss. For pagination, slice the path list before constructing any view so the
work is bounded. For atomicity, write the new MANIFEST to a sibling temp path and
`os.replace` it into place — `os.replace` is atomic on the same filesystem. Keep
the shared cross-worker cache out of scope; it belongs to the scale phase and
would pull in `api/main.py`. For the corrupted-file fix, find where
`list_replays` iterates files and wrap the per-file metadata build in a
try/except for `CorruptedFileError` (the type Task 4.16 added to `ReplayLog`):
skip the offending file, log a warning with its path, and continue — never let
one bad file abort the whole listing.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-6-replay-loader-efficiency-pagination` with a title like `task 6.6: backend replay-loader efficiency, pagination, and corrupted-file resilience`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit G-G-2, G-G-3, H-H-2, H-H-3, K-K-8 (backend half); DESIGN.md §11.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
