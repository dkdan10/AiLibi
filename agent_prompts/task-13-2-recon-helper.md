# Agent Prompt — 13.2 Meeting-time position-reconstruction helper (transcript-only)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

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
Open a PR from branch `phase-13-recon-helper` with a title like `task 13.2: meeting-time position-reconstruction helper (transcript-only)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (the spine); experiments/lab/inference_feasibility_probe.py (the `reconstruct` logic to promote); meetings/transcript.py (`is_relevant_sighting`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
