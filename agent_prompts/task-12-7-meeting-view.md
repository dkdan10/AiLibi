# Agent Prompt — 12.7 Meeting view

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.7 — Meeting view, anchored to design/phase-12/stage-1-design.md §3.4, slice 5; the rendered target `design/phase-12/playful-system/screens/05-meeting.png` and the accusation-chain / ballots / `verdict` code in `playful-system/playful-system.dc.html`; the firewall (role-neutral outcome) + the REAL §4.6 rule in `design/phase-12/claude-design-brief.md`. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-meeting-view`
**Depends on:** 12.1, 12.2, 12.4, 12.5
**Section refs:** design/phase-12/stage-1-design.md §3.4, slice 5; the rendered target `design/phase-12/playful-system/screens/05-meeting.png` and the accusation-chain / ballots / `verdict` code in `playful-system/playful-system.dc.html`; the firewall (role-neutral outcome) + the REAL §4.6 rule in `design/phase-12/claude-design-brief.md`
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/MeetingView.tsx
- frontend/src/components/TurnCard.tsx
- frontend/src/components/BallotCard.tsx
- frontend/src/components/MeetingPill.tsx
- frontend/src/store/replayStore.ts
- frontend/src/components/MapView.tsx
- frontend/src/stories/MeetingView.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the meeting already mounts in the existing overlay slot (`<MeetingView/>`); rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `TurnView` / `BallotView` / `GateView` / `ContradictionView` (weak/strong + `rewrite_reasons`) already ship from 12.2; no DTO change, no re-record
- the belief / mind surfaces — other Wave-B slices

Rebuild the meeting surface the App.tsx overlay slot mounts (`<MeetingView/>`): the accusation chain as a threaded
**waterfall** (TurnCards indented by `reply_to`, speaker chip + structured claims / observations + a free-text toggle);
the **claim↔map cross-highlight** — hovering "saw Red in Electrical" lights the claim's PUBLIC referent — the room + agent NAMED in the transcript (public, safe in any perspective; the sightline and does-it-match-truth overlay are Omniscient-only, and in As-agent fog the highlight reveals no position the fog has hidden),
the single best legibility device for the transcript; contradiction **links** drawn weak = dashed / strong = solid (from
`ContradictionView.weak`); a ballots section (`BallotView`: voter→target, confidence bar, rationale, **rewrite-marker
chips** from `rewrite_reasons`, vote correctness by **shape / label, not hue**); and a **role-neutral** outcome banner.
The per-meeting **§4.6 verdict** renders from `GateView` — the REAL rule (plurality + at least one leader ballot ≥ 0.6,
tie → SKIP). The converge mock's "simple majority of living voters" copy is WRONG — do NOT replicate it. The
cross-highlight is hand-wired: a shared store field set on TurnCard hover, read by `MapView` to light the room + agent (an
additive overlay — do not touch 12.5's fog / leak logic). The transcript chrome (TurnCard / ballot / banner layout) comes
from a focused Claude-Design prompt: *"Design the meeting transcript view: a threaded accusation waterfall of TurnCards
(speaker chip, structured claims + free-text toggle), a contradictions section (weak=dashed / strong=solid links), a
ballots section (voter→target, confidence bar, rationale, marker chips, a §4.6 gate readout), and a role-neutral outcome
banner; states chain / single-turn / skipped / ejected; firewall — outcome + correctness role-neutral (shape/label, not
red/green); presentational only, tokens only"* → Share → Handoff to Claude Code → integrate.
**Definition of done:** the threaded waterfall renders (indented by `reply_to`); the claim↔map cross-highlight works
(hovering a sighting lights the claim's public referent — the named room + agent — with any sightline / truth-match overlay Omniscient-only and no fogged position revealed in As-agent); contradiction links render weak = dashed / strong = solid;
ballots show voter→target + confidence + rationale + rewrite-marker chips + correctness by shape / label (not hue); the
§4.6 readout comes from `GateView` (plurality + ≥ 0.6, tie → SKIP — NOT "majority"); the outcome banner is role-neutral;
the result matches the committed `05-meeting` render; a Storybook story covers chain / single-turn / skipped / ejected;
`npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.

## Implementation hint
rebuild `MeetingView` + `TurnCard` / `BallotCard` in place. Add a shared highlight field to `replayStore` (e.g.
`highlightedSighting: {agentId, roomId} | null`), set it on TurnCard hover, and read it in `MapView` to light the room +
agent — an additive overlay that must not perturb 12.5's fog logic. Render the §4.6 readout from `GateView` (never the
converge mock's "majority" text); draw contradiction weak / strong from `ContradictionView.weak`; the rewrite chips from
`rewrite_reasons` + `rationale_text_clean`.

## Integration risk
the cross-highlight touches the already-merged `MapView` (12.5) — keep it strictly additive (a highlight overlay reading
the store) so the fog + leak behaviour is unchanged. The highlight lights ONLY the claim's public referent (the named
room / agent), never a ground-truth position the current As-agent perspective has fogged; the sightline / truth-match
overlay is Omniscient-only — a hover handler that peeks at fogged ground truth is exactly the leak class this project
guards. The §4.6 readout MUST use `GateView`'s real rule (plurality + ≥ 0.6,
tie → SKIP); the converge mock literally renders the wrong "simple majority" copy, so do not copy its text. Outcome +
vote-correctness must read by shape / label, never red-vs-green (role-neutral firewall). Don't edit `App.tsx` (mount
discipline).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-12-meeting-view` with a title like `task 12.7: meeting view`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §3.4, slice 5; the rendered target `design/phase-12/playful-system/screens/05-meeting.png` and the accusation-chain / ballots / `verdict` code in `playful-system/playful-system.dc.html`; the firewall (role-neutral outcome) + the REAL §4.6 rule in `design/phase-12/claude-design-brief.md`), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
