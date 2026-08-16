# Agent Prompt — 19.12 The frontend test baseline: Vitest, ESLint, one Playwright journey

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.12 — The frontend test baseline: Vitest, ESLint, one Playwright journey, anchored to audits/audit-phase-19-triage.md §7 item 13 [C]; frontend/package.json:6-14 (no test script); the two `eslint-disable` comments with no linter (frontend/src/components/MapView.tsx:329, AgentToken.tsx:142 — verified: no eslint config or dependency exists); frontend/src/store/replayStore.ts:468 + :511 (one error field, three meanings; a third write site at :370) [S-Claude — re-verified at HEAD]; frontend/src/lib/playback.ts (407 LOC of pure functions, the natural unit-test target). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-frontend-test-baseline`
**Depends on:** 19.7, 19.10, 19.11 (the last is MeetingView.stories.tsx serialization — the taxonomy fixture lands before the error-split touches the same file)
**Section refs:** audits/audit-phase-19-triage.md §7 item 13 [C]; frontend/package.json:6-14 (no test script); the two `eslint-disable` comments with no linter (frontend/src/components/MapView.tsx:329, AgentToken.tsx:142 — verified: no eslint config or dependency exists); frontend/src/store/replayStore.ts:468 + :511 (one error field, three meanings; a third write site at :370) [S-Claude — re-verified at HEAD]; frontend/src/lib/playback.ts (407 LOC of pure functions, the natural unit-test target)
**Complexity:** Integration

The flagship surface has zero tests and suppresses a linter that does not exist. Land the
baseline: Vitest with unit tests for `lib/playback.ts`'s pure functions (tick/frame
mapping, key moments, the new pause/beat/finale helpers) and the store's race guards;
split the three-meaning error field into distinct states; flat-config ESLint whose rule
set actually includes the rules the two existing disables reference; and ONE Playwright
journey — featured replay → play → meeting pause → inspect ballots → finale (unspoiled →
reveal) — plus assertions pinning the keyboard transport, fog enforcement, and
reduced-motion behaviors that already work. Wire vitest + eslint into `scripts/check.sh`
and CI; the Playwright journey runs in CI and on demand locally (the environment's
pre-installed Chromium; never `playwright install` in CI without caching).

**Files in scope:**
- frontend/package.json
- frontend/package-lock.json
- frontend/vitest.config.ts (new)
- frontend/eslint.config.js (new)
- frontend/src/lib/playback.test.ts (new)
- frontend/src/tokens.test.ts (new — the durable ramp-integrity check 19.6 defers here)
- frontend/src/store/replayStore.ts
- frontend/src/store/replayStore.test.ts (new)
- frontend/e2e/ (new)
- frontend/playwright.config.ts (new)
- frontend/src/components/ReplayPicker.tsx; (ONLY the `currentReplayError` selector update the error-field split forces — verified consumer: the selector at :551, read at :728 and :733)
- frontend/src/components/MindInspector.tsx; (same — verified consumer at :758)
- frontend/src/hooks/usePlayback.ts; (ONLY the error-selector routing at :302/:431-460 — the URL-hydration clear keys off the REPLAY-LOAD error specifically after the split; 19.10's playback behavior is untouched)
- frontend/src/stories/MeetingView.stories.tsx; (the typed store-state fixture seeds the split fields — the seed block at :428-440)
- frontend/src/stories/MapStage.stories.tsx; (same — the `useReplayStore.setState({` block at :279)
- .github/workflows/ci.yml
- scripts/check.sh

**Files NOT in scope:**
- frontend/src/App.tsx (19.10's file — tested here, not edited; usePlayback.ts is IN scope above for the error-selector routing ONLY, never for playback behavior)
- frontend/src/components/ (beyond the two named selector updates — behavior pinned, not changed)

**Definition of done:**
- [ ] `npm run test` (vitest) and `npm run lint` exist and pass; the two pre-existing disables reference rules the config enables; new lint debt is zero or explicitly inline-justified.
- [ ] The error-field split is landed with a store test proving stale-response races cannot clobber newer state.
- [ ] The Playwright journey passes headless against the local dev servers, covering pause → finale with the keyboard/fog/reduced-motion pins.
- [ ] check.sh runs vitest + eslint; CI runs all three legs green with the journey's runtime and flake posture noted in the PR.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Keep the journey to ONE spec file with generous, condition-based waits (no sleeps) and a
single retry in CI; flake here poisons the whole gate's credibility. The browser is
SPECIFIED, not assumed: either `channel: "chrome"` against the system browser or a
pinned Playwright browser version with an explicit CI cache — "preinstalled Chromium"
is an environment observation, not a configuration. The store race guards are testable
without the DOM — drive the store directly with out-of-order promise resolutions.

## Integration risk

check.sh and CI are shared, load-bearing surfaces (19.7 just touched both — this task
depends on it precisely to serialize). The risk is gate-runtime creep and browser flake:
vitest/eslint are cheap and belong in check.sh; the browser journey is CI + on-demand,
and its CI job must reuse the preinstalled browser rather than downloading one per run.

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
Open a PR from branch `phase-19-frontend-test-baseline` with a title like `task 19.12: the frontend test baseline: vitest, eslint, one playwright journey`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 13 [C]; frontend/package.json:6-14 (no test script); the two `eslint-disable` comments with no linter (frontend/src/components/MapView.tsx:329, AgentToken.tsx:142 — verified: no eslint config or dependency exists); frontend/src/store/replayStore.ts:468 + :511 (one error field, three meanings; a third write site at :370) [S-Claude — re-verified at HEAD]; frontend/src/lib/playback.ts (407 LOC of pure functions, the natural unit-test target)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
