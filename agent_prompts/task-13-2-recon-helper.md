# Agent Prompt — 13.2 Meeting-time position-reconstruction helper (transcript-only)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.2 — Meeting-time position-reconstruction helper (transcript-only), anchored to experiments/lab/report-phase-b-plan.md (the spine); experiments/lab/inference_feasibility_probe.py (the `reconstruct` logic to promote); meetings/transcript.py (`is_relevant_sighting`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-recon-helper`
**Depends on:** none
**Section refs:** experiments/lab/report-phase-b-plan.md (the spine); experiments/lab/inference_feasibility_probe.py (the `reconstruct` logic to promote); meetings/transcript.py (`is_relevant_sighting`)
**Complexity:** Medium
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_transcript_reconstruct.py
**Files NOT in scope:**
- engine/ and observation/ — the helper reads the PUBLIC transcript only, never engine WorldState or perception
- meetings/transcript.py's contradiction-detection rules — those are 13.3 / 13.4
- agents/memory/beliefs.py — belief wiring is 13.5; no re-record

Promote `experiments/lab/inference_feasibility_probe.py::reconstruct` into a pure, replay-deterministic helper in
`meetings/transcript.py` that rebuilds each subject's STATED room-by-tick path from the meeting transcript's
`saw_player` observations ONLY (never engine state, never perception). This is the substrate every new STRONG
inferential rule (13.3 / 13.4) consumes. No behaviour change — pure helper + unit tests only.
**Definition of done:** a pure function in `meetings/transcript.py` reconstructs per-subject stated paths from transcript
Observations alone (no engine/perception/observation import); a unit test over a hand-built transcript yields the
expected paths and asserts no engine import; the function is deterministic (run twice → byte-identical); no recording or
replay touched; `scripts/check.sh` is green.

## Implementation hint
port the probe's `reconstruct` semantics (engine actor-id order) but over STATED sightings, not engine truth; keep it a
pure function (transcript in → paths out, no side effects); reuse `is_relevant_sighting` for which sightings count.

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
Open a PR from branch `phase-13-recon-helper` with a title like `task 13.2: meeting-time position-reconstruction helper (transcript-only)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (the spine); experiments/lab/inference_feasibility_probe.py (the `reconstruct` logic to promote); meetings/transcript.py (`is_relevant_sighting`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
