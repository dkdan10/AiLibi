# Agent Prompt — 10.9 Wave-1 combined re-record and gate

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.9 — Wave-1 combined re-record and gate, anchored to DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-11-2218-gameplay-data.md gp-7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-wave1-rerecord`
**Depends on:** 10.6, 10.7, 10.8
**Section refs:** DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-11-2218-gameplay-data.md gp-7
**Complexity:** Integration

Operator task, local session, after 10.6-10.8 merge. ONE combined re-record of BOTH sets
(flat 4p/1i + 9p2i) on qwen3.5:9b via scripts/refresh_samples.sh, smoke-first with
STOP-for-go, then the stacked gate. The A/B baseline is the 10.6-re-derived corrected W0
table read from `tests/fixtures/phase10/corrected_w0_baseline.json` — the one home 10.6
committed; never PR #143's raw numbers, never a re-derivation inside this task.

**Files in scope:**
- replays/samples/** (both sets re-recorded; MANIFEST provenance per the rev-parse-HEAD convention)
- tests/fixtures/** (era pins that legitimately move; each move named in the PR Decisions)
- tasks/phase-10.md (check off; record the gate table)

**Files NOT in scope:**
- everything else — any source change discovered mid-record is a STOP-and-escalate, recorded on a smoke-abandon branch per doctrine; no papering edits

**Definition of done:**
- [ ] Smoke (5 seeds, 9p2i) green, then STOP for explicit owner go before the full run.
- [ ] HARD validity gate (stacked, all green): friendly-fire 0; game_over 50/50 both sets; betrayal ballots/accusations 0; byte-identical reconstruction; threshold inversions 0; thinking-leak trips 0; dangling reason ids 0; meeting_rate at or above the 0.60 floor.
- [ ] Wave-1 gates: emergency_meetings above 0 set-wide; meetings/game median at or above 2 (report the share of games with 2+ meetings beside it); genuine_class_conversion at or above the corrected baseline; multi_signal_conversion UP vs the corrected baseline — gate on the conversion COUNT (4 on the corrected W0), report the rate beside it: a larger ejection denominator must never read as regression; over-gate listeners per accused-impostor meeting UP (1.41 on the corrected W0); ANTI-RAILROAD HARD: games with a wrong ejection NOT above the W0 count of 7, innocents-at-1.0 still 0.
- [ ] Channel telemetry: every pre-vote fold event lists its voices with observation backing (spot-walk 3 from the bytes, and at least one spot-walk must be a ballot whose voter crossed 0.60 BY the pre-vote fold — verify the rendered verdict read MUST-vote and the ballot complied; that is the new render seam where a fresh inversion class would appear); VARYING_ROOMS-class flags 0; retry/unsure-degrade telemetry present; no seed-30-class conversion (a bare-pile-on ejection anywhere fails the gate).
- [ ] The funnel table in the PR: supply gauges (zero-contradiction share, genuine-subject share, over-gate listeners), conversion metrics vs corrected baseline, meetings histogram, emergency usage, win split REPORTED and labelled non-gate, decay/carry survival accounting (the decay-vs-cadence question is answered with data here, decided in a later wave if at all).
- [ ] Provenance tuple (sample dir + commit + model) in the PR; `bash scripts/check.sh` green; any truncation runaway is a STOP (the cap stays frozen).

## Implementation hint

Mirror the 10.5 operator rhythm exactly (smoke, go, both sets, gate, funnel). Expect total
meeting count UP (emergency channel) and contradiction volume DOWN vs PR #143 (the
placeholder fix) — the corrected baseline makes that legible. If any HARD line goes red,
stop, push the smoke-abandon branch, and report; do not iterate prompts or constants inside
this task.

## Integration risk

This is the wave's only measurement; everything frozen stays frozen during it. The two
known tensions to watch in the funnel: added meetings vs the pacing inversion (the
anti-railroad gate is the arbiter) and the testimony channel vs §4.6 inversions (must stay
0 — the gate reads post-fold values but its rule is untouched).

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
Open a PR from branch `phase-10-wave1-rerecord` with a title like `task 10.9: wave-1 combined re-record and gate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-11-2218-gameplay-data.md gp-7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
