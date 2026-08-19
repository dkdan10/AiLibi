# Agent Prompt — 19.10 Playback coherence: the meeting pause, the unspoiled mode, the finale card

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.10 — Playback coherence: the meeting pause, the unspoiled mode, the finale card, anchored to audits/audit-phase-19-triage.md §7 item 11 [S-Codex; VERIFIED §8 row 10]; frontend/src/hooks/usePlayback.ts:40 (500 ms base cadence), :304-331 (auto-advance), :333-382 (auto-follow selects a meeting on its single frame and clears it on the next — :366/:376); frontend/src/App.tsx:290 (the header renders `meta.winner` unconditionally), :366-489 (RosterRail mixes pre-ejection `agent_states` with post-ejection `advantage` counts); api/replay_loader.py:1200-1207 (the loader's own deliberate-mix comment). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-playback-coherence`
**Depends on:** 19.5, 19.6, 19.9 (the 19.5 edge is api/schemas.py + generated-types serialization; the 19.6 edge is HighlightCard.tsx serialization)
**Section refs:** audits/audit-phase-19-triage.md §7 item 11 [S-Codex; VERIFIED §8 row 10]; frontend/src/hooks/usePlayback.ts:40 (500 ms base cadence), :304-331 (auto-advance), :333-382 (auto-follow selects a meeting on its single frame and clears it on the next — :366/:376); frontend/src/App.tsx:290 (the header renders `meta.winner` unconditionally), :366-489 (RosterRail mixes pre-ejection `agent_states` with post-ejection `advantage` counts); api/replay_loader.py:1200-1207 (the loader's own deliberate-mix comment)
**Complexity:** Integration

The app's core content cannot be consumed on the default Play path: a meeting gets one
500 ms frame, the header spoils the winner from frame zero, the game simply stops with no
resolution, and a meeting frame carries two different times. Fix the narrative spine:
(a) autoplay pauses on meeting entry with Resume and next-beat affordances; (b) unspoiled
mode is the default AND INDEPENDENT OF PERSPECTIVE — outcome reveal is its own store
state, defaulted off, NOT implied by omniscient view (the store currently defaults to
OMNISCIENT and resets every selected replay to it at `replayStore.ts:223/:301`, which
would defeat "unspoiled by default" if perspective implied reveal; omniscient governs
what the CURRENT FRAME shows, reveal governs the FUTURE/OUTCOME) — and every
outcome-derived surface is gated by it: the header, the finale card, the entry cards'
full outcome copy (win shape and ejection counts at `HighlightCard.tsx:94`, not just the
WinnerTag), and the outcome FILTERS (`ReplayFilters.tsx` — winner/winShape/ejection
options render behind the reveal affordance with an explicit spoiler warning, and URL
state carries the reveal flag deliberately, never accidentally); (c) a real finale card — winner, win
reason, the decisive events, a compact per-agent "what they knew vs the truth" recap, and
the reveal toggle — built from data already recorded in the replay (exposed as additive
DTO fields where the view model lacks them); (d) one frame, one time: model the meeting's
pre-resolution and post-resolution states separately or label the transition explicitly,
resolving the deliberate mix the loader documents.

**Files in scope:**
- frontend/src/hooks/usePlayback.ts
- frontend/src/App.tsx
- frontend/src/components/HighlightCard.tsx; (the entry-card WinnerTag honors unspoiled mode — verified pre-open spoiler at :186 — and the stale "4p1i default" comments at :16-17/:33 are rewritten post-flip)
- frontend/src/components/ReplayPicker.tsx; (ONLY the winner data passed into the entry cards at :118/:129 — unspoiled gating, no copy changes)
- frontend/src/components/ReplayFilters.tsx; (the outcome filters gate behind the reveal affordance — winner/winShape/ejection expose outcomes pre-open)
- frontend/src/store/replayStore.ts; (ONLY the reveal state: independent of perspective, default off, preserved across the per-replay perspective reset — 19.12's error-field split is untouched)
- frontend/src/stories/MeetingView.stories.tsx; (its complete `ReplayView` fixture gains the finale field or tsc fails)
- frontend/src/stories/MapStage.stories.tsx; (same — `FIXTURE` constructs the full generated type)
- frontend/src/lib/playback.ts; (pure helpers for pause/beat/finale state — keep them pure, 19.12 tests them)
- api/replay_loader.py
- api/schemas.py; (additive DTO fields only)
- frontend/src/types/api.ts; (regenerated)
- frontend/src/types/api.fidelity.ts; (regenerated — the generator emits BOTH artifacts and the drift test checks both)
- tests/api/

**Files NOT in scope:**
- frontend/src/components/MeetingView.tsx (19.11's file)
- frontend/src/components/GuidedTour.tsx (19.9's file — ReplayPicker.tsx is IN scope above, for the entry-card winner gating only)
- replays/ (frozen)

**Definition of done:**
- [ ] Default Play on a featured replay pauses at each meeting, resumes on demand, and ends on the finale card; outcome reveal is a store state INDEPENDENT of perspective, defaults off for every replay (the per-replay perspective reset does not re-reveal — pinned), and no outcome-derived surface renders without it: header, finale, entry-card outcome copy (win shape/ejection counts included), outcome filters (spoiler-warned), and URL state.
- [ ] Meeting-tick frames expose explicit pre/post-resolution semantics (fixture-pinned through the loader: the roster a meeting deliberates over and the advantage after its result are never conflated in one unlabeled frame).
- [ ] The stale 4p1i-default claims in this task's files are swept post-flip: `api/replay_loader.py:812` (the `rubric()` docstring's "4p1i default" line) and `api/schemas.py:1000-1001`; the third pre-flip claim, `default_set()`'s docstring, was already rewritten by 19.9 itself (this task depends on the flip, so the sweep lands ordered).
- [ ] HighlightCard's rubric score badge (:69-82) carries the narrow internal-heuristic label, and its stale "4p1i default" comments (:16-17, :33) are rewritten post-flip (19.9's rules, applied here because this task owns the file and depends on 19.9).
- [ ] The DTO additions are additive (existing committed fixtures still parse; the fidelity fixture regenerates green).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The pause belongs in the playback reducer, not the component: emit a "meeting-entered"
beat from the frame index (the key-moment machinery in `lib/playback.ts` already knows
meeting frames) and let the hook consume it. The finale's raw material (`winner`,
`winner_reason`, final tick, decisive events) is in the recorded `game_over`/meeting
records — thread it through `api/schemas.py` as one additive `GameFinale` view rather
than scattering fields.

## Public types this task introduces
- `api.schemas.GameFinale`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This changes default user-visible behavior on purpose; the risk is regressing the pinned
interactions that already work (keyboard transport, fog enforcement, URL state). Until
19.12's automated pins exist, the PR carries a manual checklist over those behaviors, and
the DTO change is additive-only so older committed fixtures keep parsing.

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
Open a PR from branch `phase-19-playback-coherence` with a title like `task 19.10: playback coherence: the meeting pause, the unspoiled mode, the finale card`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 11 [S-Codex; VERIFIED §8 row 10]; frontend/src/hooks/usePlayback.ts:40 (500 ms base cadence), :304-331 (auto-advance), :333-382 (auto-follow selects a meeting on its single frame and clears it on the next — :366/:376); frontend/src/App.tsx:290 (the header renders `meta.winner` unconditionally), :366-489 (RosterRail mixes pre-ejection `agent_states` with post-ejection `advantage` counts); api/replay_loader.py:1200-1207 (the loader's own deliberate-mix comment)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
