# Agent Prompt — 4.15 MeetingView width/overflow polish (pre-UX-session Finding 3)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.15 — MeetingView width/overflow polish (pre-UX-session Finding 3), anchored to DESIGN.md §5, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-meetingview-overflow-fix`
**Depends on:** 4.12 merged
**Section refs:** DESIGN.md §5, DESIGN.md §7
**Complexity:** Small

UX self-audit Finding 3: the MeetingView overlay reads fine at 90%
browser zoom but clips content at 100%. The overlay's outer panel is
[max-w-4xl (896px) at MeetingView.tsx:332](frontend/src/components/MeetingView.tsx#L332);
the overlay width itself doesn't change with zoom. Something inside
the panel is forcing horizontal overflow at native zoom that's
clipped by the panel boundary or the viewport edge. Most likely
culprits per the 4.6 contract structure: the 3 `ReportCard` instances
laid out horizontally without `flex-wrap`, OR a `<pre>` rendering
`free_text` without `whitespace-pre-wrap`, OR a child with implicit
fixed width (e.g. a `<code>` block, an unbroken long string like a
contradiction id).

Cosmetic per se — the viewer can zoom out as a workaround — but
fixing it removes a stumble in the UX session ("why does it look
weird?") that costs nothing to address.

**Out of scope** (explicit decisions deferred):

- **Responsive redesign for mobile / narrow viewports.** This task
  targets desktop at 100% zoom on typical laptop/desktop widths
  (1280–1920px). A general mobile/tablet pass is a separate effort.
- **Sidebar layout (split MapView + MeetingView).** The 4.6 contract
  chose the overlay pattern. This task does not redesign; only fixes
  the overflow within the existing pattern.
- **Tailwind theme / design-system extraction.** No new design
  tokens, no shared CSS abstractions. Local fixes only.
- **MapView, ThoughtStream, BeliefMatrix overflow audits.** Only
  MeetingView is in scope. If the UX session surfaces overflow in
  other components, file separately.

**Files in scope:**
- frontend/src/components/MeetingView.tsx
- frontend/src/components/ReportCard.tsx
- frontend/src/components/StatementCard.tsx
- frontend/src/components/BallotCard.tsx
- frontend/src/components/ContradictionBadge.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/src/types/api.ts
- frontend/src/components/MapView.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/RoomRect.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/ReplayControls.tsx
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/MeetingPill.tsx
- frontend/src/components/AgentSelector.tsx
- frontend/src/components/MemoryPanel.tsx
- frontend/src/components/BeliefRow.tsx
- frontend/src/components/BeliefCell.tsx
- frontend/src/components/LLMCallCard.tsx
- frontend/src/components/SabotageOverlay.tsx
- frontend/src/components/VentEdge.tsx
- frontend/src/components/BodyMarker.tsx
- frontend/src/App.tsx
- frontend/package.json
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- scripts/
- tests/

**Definition of done:**
- [ ] **Overlay reads cleanly at 100% browser zoom on a 1440×900 viewport.** No horizontal clipping inside the overlay panel; no horizontal scrollbar appearing inside the panel itself. Vertical scrolling inside the modal is fine.
- [ ] **Root-cause fix, not a workaround.** Identify the specific child whose layout forces overflow (likely the reports row, possibly a `<pre>` block, possibly an unbroken long string). Fix the offending element with `min-w-0`, `flex-wrap`, `break-words`, `whitespace-pre-wrap`, OR widening the panel's `max-w-*` — whichever is the minimum sufficient fix. Document the diagnosis + fix choice in `## Decisions`.
- [ ] **Long free_text doesn't break the layout.** Test with the longest `free_text` value in any committed sample (likely the impostor's defensive report in one of seeds 22/24/26/49). The text wraps without forcing horizontal scroll.
- [ ] **Long structured content doesn't break the layout.** Test with `rendered_memory_text` if it leaks into MeetingView via ContradictionBadge or similar — confirm it wraps.
- [ ] **Long agent_ids and contradiction_ids don't break the layout.** Even a hypothetical 60-char agent_id should wrap or truncate gracefully. Use `break-all` or `truncate` as appropriate.
- [ ] **All four card types render correctly at 100% zoom.** Manually exercise: open the meeting in one of `replays/samples/replay-seed-{22,24,26,49}.jsonl`, confirm `ReportCard`, `StatementCard`, `BallotCard`, `ContradictionBadge` each render without clipping.
- [ ] **No regression at 90%, 110%, 125% zoom.** Spot-check these three additional zoom levels. The original "fits at 90%" behavior must be preserved.
- [ ] **No new npm dependencies.** Pure Tailwind class changes.
- [ ] **TypeScript strict still passes.** `npm run tsc:check`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Two screenshots in PR.** (a) 100% zoom showing the full meeting overlay for seed 22 with no clipping. (b) The pre-fix state, captured before the edit lands, showing the clipping for comparison. The before/after pair is the cleanest evidence.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (Python tests unaffected).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-4-meetingview-overflow-fix` with a title like `task 4.15: meetingview width/overflow polish (pre-ux-session finding 3)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
