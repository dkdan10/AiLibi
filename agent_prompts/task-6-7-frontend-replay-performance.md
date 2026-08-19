# Agent Prompt — 6.7 Frontend replay performance: memoize the map render path and window the payload

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.7 — Frontend replay performance: memoize the map render path and window the payload, anchored to Audit K-K-1, K-K-2, G-G-1, G-G-5; DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-frontend-replay-performance`
**Depends on:** none
**Section refs:** Audit K-K-1, K-K-2, G-G-1, G-G-5; DESIGN.md §11.4
**Complexity:** Medium

`MapView` has no memoization (`frontend/src/components/MapView.tsx:191`): on every
`currentTick` change `visibleBodies` re-scans every tick from 0 to `currentTick`,
and `roomsById`/`playerIndexById`/`colorById`/`ventEdges`/the fit transform are
rebuilt from scratch each render. Full playback of an N-tick replay is O(N²) tick
scans — ~500K at the 1000-tick default, ~50M at 10000 — the dominant frontend
bottleneck, and at 4× playback the scan re-runs roughly eight times a second
(audit K-K-2 = G-G-1). Separately, the entire `ReplayView` (every tick, every
meeting transcript, full LLM prompt/response text, failed_calls) is loaded in one
payload into the Zustand store (`frontend/src/store/replayStore.ts:106`); the
per-tick `getTick` endpoint exists but is never called, so the store grows
linearly with game length with no windowing (K-K-1 = G-G-5).

This task lands the performance substrate only — it must survive the Phase 7
redesign, so no visual/accessibility changes here. Memoize MapView's per-replay
invariants (the lookup Maps, color map, vent edges, fit transform) on
`currentReplay` identity, and replace the O(currentTick) body re-scan with a
per-tick cumulative body-state array computed once per replay (useMemo) and
indexed in O(1). Window the bulk payload: keep only the timeline + roster + map
in the store, drop raw prompt/response text from the bulk view, and lazy-fetch
meetings/memory on demand via the existing `getTick`/`getMeeting` endpoints
(fetch the LLM call body when an `LLMCallCard` is expanded). Backend G-G-1/G-G-5
are the same surface from the API side; this is the frontend half.

**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/src/components/LLMCallCard.tsx

**Files NOT in scope:**
- frontend/src/components/ (other than MapView.tsx and LLMCallCard.tsx)
- frontend/src/types/api.ts (no DTO shape change; reuse existing types)
- frontend/src/index.css (no visual change; that is Phase 7)
- api/ (the backend half is Tasks 6.5/6.6)

**Definition of done:**
- [ ] MapView's per-replay invariants (`roomsById`, `playerIndexById`, `colorById`, `ventEdges`, fit transform) are memoized on `currentReplay` identity (useMemo), rebuilt only when the loaded replay changes, not every tick (K-K-2/G-G-1).
- [ ] Body discovery is O(1) per tick step: a per-tick cumulative body-state array is computed once per replay (useMemo) and indexed by `currentTick`, replacing the 0..currentTick re-scan (K-K-2/G-G-1).
- [ ] The bulk store payload is windowed: raw LLM prompt/response bodies are dropped from the bulk `ReplayView` held in the store; meetings/memory and LLM call bodies are lazy-fetched via the existing `getTick`/`getMeeting` endpoints, and an `LLMCallCard` fetches its body on expand (K-K-1/G-G-5).
- [ ] Playback correctness is unchanged: stepping, scrubbing, speed changes, and snap-to-meeting all render the same map state as before, verified against an existing sample replay.
- [ ] No visual restyle, no accessibility change, no DTO shape change — this is performance only (Phase 7 owns the redesign).
- [ ] `cd frontend && npm run tsc:check` passes (no new `any`, no `@ts-ignore`).
- [ ] `cd frontend && npm run build` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `bash scripts/check.sh` passes locally (frontend checks included).

## Implementation hint

Read `frontend/src/components/MapView.tsx` (the per-render rebuilds and the
`visibleBodies` scan around line 191), `frontend/src/store/replayStore.ts:106`
(the single-payload load), `frontend/src/api/client.ts` (the existing `getTick`/
`getMeeting` methods, currently unused for windowing), and
`frontend/src/components/LLMCallCard.tsx`. Wrap the static lookups in `useMemo`
keyed on the loaded replay object identity. For bodies, precompute an array where
index `t` holds the set of discovered-body positions as of tick `t` — a single
forward pass per replay — then index it directly. For windowing, trim the store
shape to timeline + roster + map and fetch heavier payloads on demand; keep the
existing component props stable so the Phase 7 redesign can still swap
implementations file-by-file. Confirm there is no behavioral regression by
scrubbing a known sample replay before and after.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-6-frontend-replay-performance` with a title like `task 6.7: frontend replay performance: memoize the map render path and window the payload`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit K-K-1, K-K-2, G-G-1, G-G-5; DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
