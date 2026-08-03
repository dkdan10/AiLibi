# Agent Prompt — 12.12 Multi-set serving + set selector

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.12 — Multi-set serving + set selector, anchored to design/phase-12/stage-1-design.md §2.1 (top-level nav / the 9p2i-vs-4p1i set), §7; `scripts/run_spectator.sh` (`AILIBI_REPLAY_DIR=replays/samples`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-multi-set`
**Depends on:** 12.2, 12.3, 12.4, 12.7, 12.9, 12.10
**Section refs:** design/phase-12/stage-1-design.md §2.1 (top-level nav / the 9p2i-vs-4p1i set), §7; `scripts/run_spectator.sh` (`AILIBI_REPLAY_DIR=replays/samples`).
**Complexity:** Integration
**Files in scope:**
- replays/samples/4p1i/
- api/replay_loader.py
- api/routes/replays.py
- api/routes/eval.py
- api/routes/sets.py
- api/main.py
- frontend/src/store/replayStore.ts
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TournamentDashboard.tsx
- tests/api/test_sets.py
- scripts/_manifest_writer.py
- scripts/_verify_samples.py
- scripts/verify_samples.sh
- scripts/refresh_samples.sh
- scripts/build_sample_report.py
- scripts/run_spectator.sh
- tests/api/test_eval_routes.py
- tests/api/test_replay_dir_fallthrough.py
- tests/scripts/test_manifest_writer.py
- tests/scripts/test_refresh_samples.py
- tests/scripts/test_build_sample_report.py
**Files NOT in scope:**
- the engine / recorded game CONTENT — the 4p1i move is a `git mv` only; NO re-record
- the chrome surfaces' internals (map / belief / meeting / mind) — only the set-fetch wiring in the browser + dashboard

Let the spectator serve **all** recorded sets in one run, with a live **set selector** (no reload) that auto-grows as new
sets are recorded. Three parts:
- **Restructure (the foundation — bigger than it looks; it reaches the substrate sample tooling).** `replays/samples/` is
  inconsistent today — **4p1i is flat at the root** (`replay-seed-*.jsonl` + `MANIFEST.md` + `tournament-eval-report.json`)
  while **9p2i is already a subdir**. `git mv` the root 4p1i files into `replays/samples/4p1i/` so `replays/samples/`
  becomes a uniform **parent of per-set subdirs** (`4p1i/`, `9p2i/`, + future) — no content change, no re-record. This
  **collapses the flat-4p1i-baseline special-casing** several tools carry: `_manifest_writer.py`'s `is_default_sample_dir`
  / `_DEFAULT_SAMPLE_DIR`, and `refresh_samples.sh`'s "refusing to refresh the flat 4p/1i baseline" guard, exist only
  because 4p1i sits at the root where a misconfigured refresh lands. Once every set is a named subdir that footgun is gone,
  so **remove** the special case (a simplification) rather than re-point it. Then update **every** root-layout reference —
  grep the repo for `replays/samples`, `SAMPLE_DIR`, `_DEFAULT_SAMPLE_DIR` and fix each: the determinism gate
  (`verify_samples.sh` / `_verify_samples.py`), the re-record workflow (`refresh_samples.sh`), the manifest writer + report
  (`_manifest_writer.py`, `build_sample_report.py`), the loader default (`api/main.py::_resolve_replay_dir`, now resolving
  to a set subdir such as `4p1i` rather than the flat root), and their tests.
- **Backend (set-aware loader).** `AILIBI_REPLAY_DIR` (`replays/samples`) becomes the **parent**; `get_replay_loader`
  takes a `set` (query param; sane default) → resolves `<parent>/<set>/` → a **per-set loader cached** (`lru_cache` keyed
  by set, so each set's engine re-walk caches independently). Thread `set` through `/replays`, `/replays/{game_id}/*`,
  `/eval/rubric`, `/eval/tournament-report`. Add **`GET /sets`** → list the parent's subdirs (the available sets),
  skipping stray non-set files — this **auto-grows**: a newly-recorded `replays/samples/<set>/` appears with no code
  change. Determinism + the leak guard run **per set**.
- **Frontend (set selector).** The browser's existing **SET dropdown** (12.9) + the dashboard fetches become set-driven.
  On load, fetch `/sets` → populate the selector + the store's `availableSets`; the active set rides the **existing `set`
  URL key** that `usePlayback.ts` already syncs to the `seedSet` store field (see `usePlayback.ts:52,473`) — `seedSet` is
  the store field name only, so **do not introduce a second URL key** or the existing deep-links / 12.9 filters break. The
  selector just calls `setSeedSet` (already URL-synced). On change, re-fetch `/replays?set=` + `/eval/rubric?set=` +
  `/eval/tournament-report?set=` — **switch live, no reload**. `run_spectator.sh` is unchanged (its `replays/samples` is
  now the parent).
**Definition of done:** `replays/samples/` is a uniform parent of per-set subdirs (`4p1i/` + `9p2i/`); the flat-4p1i
special-casing is removed (no `is_default_sample_dir` / flat-baseline refuse-guard remains); every root-layout reference
is updated (the determinism gate, the re-record workflow, the manifest writer + report, the loader default, and their
tests) and `scripts/verify_samples.sh replays/samples/4p1i` passes; `GET /sets` lists the subdirs and auto-grows; `/replays`
+ `/eval/*` are set-parametrized over a per-set cached loader; the frontend set selector toggles sets **live (no reload)**
via the existing `set` URL key, and a newly-recorded set appears with no code change; `run_spectator.sh` serves all sets in
one run; determinism + leak tests pass **per set**; NO re-record (the 4p1i move is a `git mv`); `scripts/check.sh` is
green.

## Implementation hint
do it in order: (1) `git mv` the root `replay-seed-*.jsonl` + `MANIFEST.md` + `tournament-eval-report.json` into `4p1i/`
(no content edit); (2) grep the repo for `replays/samples` / `SAMPLE_DIR` / `_DEFAULT_SAMPLE_DIR` and fix every code
reference, removing the flat-baseline special case rather than re-pointing it; (3) run `scripts/verify_samples.sh
replays/samples/4p1i` to confirm byte-determinism survived the move; (4) make `get_replay_loader` resolve
`<AILIBI_REPLAY_DIR>/<set>` and cache per-set (`lru_cache` by set), and add `GET /sets`; (5) wire the frontend selector to
`/sets` + the per-set re-fetch, reusing the existing `set` URL key (do not add a new one).

## Integration risk
this reaches the **substrate sample tooling** — `verify_samples.sh` / `_verify_samples.py` is the byte-determinism gate
the gameplay/ML cadence depends on, and `refresh_samples.sh` is the real-provider re-record workflow; update both with
care and run `verify_samples.sh` after the move. The move + the loader/scripts/tests must land together — moving the files
alone breaks the root-`glob`, the `is_default_sample_dir` logic, and every test asserting the flat root (and `check.sh`
runs `pytest`, so those failures block green). The `set` param needs a sane default so existing deep-links + the dashboard
still resolve; per-set loader caching must be bounded (LRU cap); `/sets` must skip stray non-set entries (a top-level
README, etc.); determinism + leak tests run per-set. 12.11 depends on this task (it does the all-surface a11y including
the set selector), so dispatch 12.12 first.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-12-multi-set` with a title like `task 12.12: multi-set serving + set selector`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §2.1 (top-level nav / the 9p2i-vs-4p1i set), §7; `scripts/run_spectator.sh` (`AILIBI_REPLAY_DIR=replays/samples`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
