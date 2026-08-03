# Agent Prompt — 12.10 Dashboard refresh

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.10 — Dashboard refresh, anchored to design/phase-12/stage-1-design.md §3.6, slice 8; the honesty rules ("no false precision") in `design/phase-12/claude-design-brief.md`. No converge screen — a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-dashboard`
**Depends on:** 12.1, 12.2
**Section refs:** design/phase-12/stage-1-design.md §3.6, slice 8; the honesty rules ("no false precision") in `design/phase-12/claude-design-brief.md`. No converge screen — a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/TournamentDashboard.tsx
- frontend/src/components/StatTile.tsx
- frontend/src/components/CalibrationCurve.tsx
- frontend/src/components/MetricCaveat.tsx
- frontend/src/stories/TournamentDashboard.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the Tournament route already mounts `<TournamentDashboard/>`; rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `/eval/tournament-report` (typed `conversion` + `gate_metrics`) + `/eval/rubric` already ship from 12.2; no DTO change, no re-record
- the browser / map / belief / meeting / inspector surfaces — other slices

Refresh the tournament dashboard the App.tsx Tournament route mounts (`<TournamentDashboard/>`): keep the existing
metrics; surface the **typed `conversion` + `gate_metrics`** (sent on the wire, typed by 12.2); **render the honesty
caveats** — small-n / low-power / populated-bins badges (`vote_correctness_small_n`, `contradictions_flagged_but_ignored`,
…) **attached to the metric each one qualifies** (never a bare metric — that is false precision, a binding honesty rule);
**StatTiles** + a **calibration curve**; and an **interestingness histogram** (from `RubricView`) whose buckets **deep-link into the Highlights reel** by building a Highlights-view URL with the **shared filter keys 12.9
reads** — `scoreBucket=<bucket>` (+ the current `set`), never an invented param. Data-bound — wire to `/eval/tournament-report` (typed) + `/eval/rubric`. The
chrome comes from a NEW Claude-Design pass: *"Refresh the tournament dashboard: StatTiles, a calibration curve, a
metric-caveat treatment (small-n / low-power badges), and an interestingness histogram; states loading / loaded /
no-report; presentational only, tokens only"* → Share → Handoff to Claude Code → integrate.
**Definition of done:** the dashboard renders via the existing `TournamentDashboard` slot; the typed `conversion` +
`gate_metrics` render; the honesty caveats (small-n / low-power / populated-bins) render as badges attached to the metrics
they qualify (no bare metric); a calibration curve + StatTiles render; an interestingness histogram links into the
Highlights reel; loading / loaded / no-report states render; a Storybook story covers them; `npm run tsc:check` +
`npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.

## Implementation hint
refresh `TournamentDashboard` in place; wire to `/eval/tournament-report` (the typed `conversion` / `gate_metrics`) +
`/eval/rubric` (the histogram). Render each caveat badge ATTACHED to the metric it qualifies (the honesty rule — never a
bare number). The histogram buckets deep-link to the Highlights view by building a URL with the shared filter keys 12.9 reads —
`scoreBucket=<bucket>` + the current `set` (NOT an invented `?bucket=`); target the route (present since the 12.4 shell)
so it works even if 12.9 lands second.

## Integration risk
the honesty caveats are binding — a metric shown without its small-n / low-power caveat is false precision; render them
attached, not as a footnote. `conversion` / `gate_metrics` are already typed by 12.2 — consume, don't re-type. 12.9 + 12.10
land in the same batch; the histogram→Highlights deep-link rides the SHARED query keys (`set` / `winner` / `winShape` /
`scoreBucket` / `hasEjection`) that 12.9 reads — 12.10 must use those exact keys (not invent `?bucket=`) or the filter
silently no-ops. The link targets the shell ROUTE (present since 12.4), so it degrades gracefully if 12.9 lands second. No converge screen — verify against the brief. Don't edit `App.tsx` (mount discipline).

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
Open a PR from branch `phase-12-dashboard` with a title like `task 12.10: dashboard refresh`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §3.6, slice 8; the honesty rules ("no false precision") in `design/phase-12/claude-design-brief.md`. No converge screen — a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
