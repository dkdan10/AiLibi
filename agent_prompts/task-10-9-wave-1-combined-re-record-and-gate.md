# Agent Prompt — 10.9 Wave-1 combined re-record and gate

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.9 — Wave-1 combined re-record and gate, anchored to DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-11-2218-gameplay-data.md gp-7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-wave1-rerecord`
**Depends on:** 10.6, 10.7, 10.8, 10.9.1, 10.9.2
**Section refs:** DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-11-2218-gameplay-data.md gp-7
**Complexity:** Integration

Operator task, local session, after 10.6-10.8 AND the two PR #147 repairs (10.9.1, 10.9.2)
merge. ONE combined re-record of BOTH sets (flat 4p/1i + 9p2i) on qwen3.5:9b via
scripts/refresh_samples.sh, smoke-first with STOP-for-go, then the stacked gate. The A/B
baseline is the 10.6-re-derived corrected W0 table read from
`tests/fixtures/phase10/corrected_w0_baseline.json` — the one home 10.6 committed; never
PR #143's raw numbers, never a re-derivation inside this task.

ATTEMPT-1 PROVENANCE: the first run STOPPED per the hard-red clause — PR #147 @ aa259f5,
the smoke-abandon evidence branch, closed UNMERGED. Sole red line: game_over 49/50 (seed-8
vote-ballot truncation abort, repaired by 10.9.1); every other HARD line and every Wave-1
gate was GREEN there (emergency 7, median 2.0, genuine 2/8, multi-signal 11/12, over-gate
listeners 1.625, wrong-ejection games 7, accuracy 0.63). Treat that table as the expected
shape, not a guarantee — this is a fresh record on a changed source state (the fail-soft
and the target guard alter bytes wherever they fire), so every number re-derives from
scratch and the full smoke-first protocol runs again from zero.

**Files in scope:**
- replays/samples/** (both sets re-recorded; MANIFEST provenance per the rev-parse-HEAD convention)
- tests/fixtures/** (era pins that legitimately move; each move named in the PR Decisions)
- tasks/phase-10.md (check off; record the gate table)

**Files NOT in scope:**
- everything else — any source change discovered mid-record is a STOP-and-escalate, recorded on a smoke-abandon branch per doctrine; no papering edits

**Definition of done:**
- [x] Smoke (5 seeds, 9p2i) green, then STOP for explicit owner go before the full run. (Smoke 0/8/12/24/39 in 24m18s: 5/5 game_over, 0 thinking-leak, byte-identical clean, both repairs fired on their canary seeds — seed-8 fail-soft, seed-12 redirect; owner go given.)
- [x] HARD validity gate (stacked) — ALL GREEN both sets: friendly-fire 0 (140 kills, 0 impostor victims); game_over 50/50 both sets (no aborts — the seed-8 truncation class gone); betrayal ballots/accusations 0/0; byte-identical reconstruction clean ×2; threshold inversions 0 both sets; thinking-leak trips 0; dangling reason ids 0; meeting_rate 0.92 (≥ 0.60 floor).
- [x] Wave-1 gates: emergency_meetings 7 (>0); genuine_class 2/8 ≥ baseline 1/7; multi_signal count 11 UP vs 4 (rate 11/11); over-gate listeners 1.62 UP vs 1.41; gp-7 unattributed impostor ejections 0; innocents-at-1.0 0. TWO owner-adjudicated deviations: ANTI-RAILROAD wrong-ejection games 8 vs the W0 ceiling 7 — the +1 is seed-12, where the 10.9.2 redirect moved 3 bare-accusation ballots off under-gate impostor p-1 onto each voter's own ≥0.60 argmax (crew p-6); ALL 8 wrong ejections are graph-consistent (no bare-pile-on), and the owner ACCEPTED gating anti-railroad on character not the count proxy. meetings/game median 1.5 (50% ≥2, one game short of 2.0; within run-to-run variance vs attempt-1's 2.0/52%, accepted with the land decision).
- [x] Channel telemetry: 16 pre-vote fold events, voices observation-backed; spot-walks (seed38 m0 fold-crossed showcase — 3-voice fold on p-3 lifts listeners p-1/p-7/p-8/p-9 to 0.63, all rendered MUST-vote, all voted p-3, impostor ejected; seed24 m0 / seed3 m0 2-voice folds); VARYING_ROOMS-class flags 0; retry/unsure-degrade present (lost_openings 2 / defaults 3); defaulted-ballot (10.9.1) 1 on seed-8, target-redirect (10.9.2) 6 eject-redirects on seeds 12/33/40, each spot-walked; no seed-30-class bare-pile-on (all 8 wrong ejections graph-consistent at 0.60–0.88).
- [x] The funnel table in the PR (supply gauges, conversion vs corrected baseline, meetings histogram, emergency usage, win split labelled non-gate, decay/carry accounting).
- [x] Provenance tuple in the PR (replays/samples/{9p2i,flat}, commit 0ed6962, model qwen3.5:9b); `bash scripts/check.sh` green; no truncation runaway (0 cap hits set-wide; cap frozen).

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
