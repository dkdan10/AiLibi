# Agent Prompt — 10.17 Wave-2 combined re-record and phase-close gate

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.17 — Wave-2 combined re-record and phase-close gate, anchored to DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-13-1816-gameplay-data.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-wave2-rerecord`
**Depends on:** 10.9, 10.14, 10.15, 10.16
**Section refs:** DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-13-1816-gameplay-data.md
**Complexity:** Integration

Operator task, local session, after the Stage-3 source + 10.16 merge (all merged @ c864775). The
wave's ONLY measurement and the 3rd/final re-record. ONE combined re-record of BOTH sets (flat 4p/1i
+ 9p2i) on qwen3.5:9b via scripts/refresh_samples.sh, smoke-first with STOP-for-go, then the stacked
gate + the phase-close audit. The A/B baseline is the corrected W1 set read from
`tests/fixtures/phase10/corrected_w1_baseline.json` (+ the 10.16 metric values below), NEVER a
re-derivation inside this task.

THE CONFOUNDING NOTE: this record measures TWO adversarial changes at once (10.14 impostor toolkit +
10.15 crew belief-spread). The win split is therefore a GUARDRAIL, not a signal — attribution comes
from the 10.16 channel decomposition (the inform channel separates the crew lever from the toolkit)
and the separately-measurable impostor behaviors. Impostor buff is primary, crew lever is gentle.

LOCKED A/B BASELINE (corrected W1, this set @ 0ed6962):
- conversion: genuine_class 2/8, multi_signal 11/11, conversion_per_meeting 11/88
- effective_deflection 9 of 27 active (59 survivals) — the deception-skill number
- impostor do_task 0 (crew 3673); impostor wait_share 0.52 vs crew 0.10; top_idler 0.38
- crew belief-spread offline prediction: +6 of the 37-bloc (10.15 floor — only recorded SKIP voters in [0.55,0.60) flip)
- ejection_accuracy 0.58 (NON-GATE), wrong-ejection games 8, threshold_inversions 0, friendly-fire 0

**Files in scope:**
- replays/samples/** (both sets re-recorded; MANIFEST provenance per the rev-parse-HEAD convention)
- tests/fixtures/** (era pins that legitimately move; each move named in the PR Decisions, including the seed-8 telemetry relabel that finally populates and the EMERGENCY_COOLDOWN_TICKS re-derivation)
- tasks/phase-10.md (check off; record the gate table)

**Files NOT in scope:**
- everything else — any source change discovered mid-record is a STOP-and-escalate on a smoke-abandon branch; no papering edits (the 9.5/10.5/10.9 doctrine)

**Definition of done:**
- [x] Smoke (5 seeds 12/16/27/29/40, 9p2i) green, then STOP for explicit owner go. ($0/35m: 5/5 game_over, byte-identical, no thinking-leak; toolkit fired do_task 0→39 / wait 0.52→0.08, inform 2, conv/meeting 0.125→0.364; owner GO given.) The 10.16 metrics + `rubric_score.py` ran as the pre-flight. The smoke's 5 seeds fired 0 emergency meetings, so the v7 path went unexercised — the **flat-first full run then crashed on the v7 emergency-no-body fail-loud guard (seed 11 m0)**, a STOP-and-escalate handled by the **10.11.1 deterministic-strip fix (PR #157, merged @ 2fd1ace)**; both sets then re-recorded on the fixed source.
- [x] HARD validity gate (stacked) — **ALL GREEN both sets** @ 2fd1ace: game_over 100/100; friendly-fire 0 (157 9p2i kills, 0 impostor victims); betrayal ballots/accusations 0/0; byte-identical reconstruction clean ×2; threshold_inversions 0 both sets; thinking-leak 0; dangling reason ids 0; meeting_rate 1.00 (9p2i, ≥ 0.60 floor; flat 4p/1i 0.22 is the structurally meeting-sparse MVP baseline); **no emergency-no-body crash** — 16 emergency meetings recorded clean, the 10.11.1 guard never fired (the strip makes it unreachable).
- [x] Wave-2 directional gates vs the locked W1 baseline: impostor do_task **0→371**; impostor wait_share **0.52→0.09** (≈ crew 0.10); conversion_per_meeting **0.125→0.250** (24/96); 10.15 inform conversions **14** realized (vs the +6 offline floor — the channel over-delivered); ANTI-RAILROAD **HARD GREEN** — wrong-ejection games **8→3**, gp-7 unattributed 0, innocents-at-1.0 0. ONE directional MISS: **effective_deflection 9→6** (DOWN) — impostors blend but get caught without deflecting; read with the close audit.
- [x] R1 load-bearing check: **CREWMATE_EJECT 1/50 → 0/50** (regressed). The meeting layer is MORE active (24 impostor ejections at 24/27 accuracy across 96 meetings, vs W1's ~6-9; emergency 7→16) but DECIDES 0 games — the crew out-tasks (98% CREWMATE_TASKS) before ejecting the *second* impostor. Directional; the headline finding for the close audit.
- [x] Balance GUARDRAIL (reported, non-gate): impostor win rate **2%** (9p2i 1/50; flat 22%) — **CRATERED at the ~2 floor**. Owner-adjudicated 2026-06-14: LAND as the W2 baseline (HARD green; the close audit decides any targeted retune — soften 10.15 inform / strengthen 10.14 deflection — on data, not now). The smoke's 0/5 was an early signal of this crew overshoot, not noise.
- [x] EMERGENCY_COOLDOWN_TICKS re-derived: mean inter-kill interval **5.56 ticks** (107 intervals, 157 kills) ≈ the 6-tick anchor — no material shift, anchor stays frozen at 6.
- [x] Channel telemetry: do_task/fake-task census imp 371 (fake) / crew 3497 (real); **no fake task advanced the real win counter** — the 10.14 integrity invariant holds (extractor genuine-class self-check OK; win-condition self-check green). Inform-channel conversions 14; defaulted-ballot 0 / redirect 0 (no runaway); firewall betrayal 0.
- [x] Funnel table: in the PR (locked W1 baseline → this record across every metric; win split REPORTED non-gate; rubric R1-R7 before/after).
- [x] Provenance tuple in the PR (replays/samples/{9p2i,flat}, commit 2fd1ace, model qwen3.5:9b); `bash scripts/check.sh` green; 0 truncation runaway (vote_defaults 0, no cap hits; caps frozen).

## Implementation hint

Mirror the 10.9 operator rhythm exactly (smoke, go, both sets, gate, funnel), now with the rubric
pre-flight folded into the smoke. Expect impostor do_task to jump from 0, wait-share to drop, more
meetings/conversions, and (the headline hope) ejection-driven wins to climb off 1/50. Run
`experiments/lab/rubric_score.py` on the smoke facts and again on the full facts. If any HARD line
goes red, push the smoke-abandon branch and report; do not iterate source inside this task.

## Integration risk

This is the wave's one measurement and the last in the 3-re-record budget, so the smoke-first
STOP-for-go is the load-bearing safeguard against the two-adversarial-changes overshoot. The two
specific new failure modes: the emergency-no-body fail-loud crash (a real STOP, surfaced not papered)
and the confounded win split (read attribution from the decomposition, never the split). The
phase-close audit runs after merge and authors nothing new — it is the Phase-10 close verdict.

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
Open a PR from branch `phase-10-wave2-rerecord` with a title like `task 10.17: wave-2 combined re-record and phase-close gate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §9, §11.4; tasks/phase-9.md 9.5 protocol; audits/audit-2026-06-13-1816-gameplay-data.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
