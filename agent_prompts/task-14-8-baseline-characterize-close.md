# Agent Prompt — 14.8 Characterize baseline 1 (R-gate as measurement) + fix recommendations

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.8 — Characterize baseline 1 (R-gate as measurement) + fix recommendations, anchored to audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py; PR #213 (baseline-1 findings). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-baseline-characterize-close`
**Depends on:** 14.7
**Section refs:** audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py; PR #213 (baseline-1 findings)
**Complexity:** Medium

Design-thread characterization (the phase CLOSE moves to 14.12, after the evidence-quality fixes and the
baseline-2 re-record). The headline is already known: R1 eject-decided **27/50** vs the 9B's 3/50, impostor
win 0.32 vs 0.84 — the new model DRIVES the corrected substrate, so the Phase-13 information-ceiling
hypothesis is REVISED, not confirmed: the ceiling bound impostor CONCEALMENT (the 14.4 tell persists) but the
live binding constraint was crew CONVERSION, and that broke. The problem has INVERTED to OVER-conviction:
ejection accuracy 0.566 (~43% of ejections take out crew), a 5-row crew railroad (2–9 stacked same-meeting
contradiction flags defeat the Phase-10.1 lift cap at the new model's 4× flag density; 3 innocents ejected —
the downgraded tripwire in `tests/meetings/test_manager.py` pins the exact set), and dialogue-level
self-sabotage measured on the committed bytes: ~10% of self-alibis are contradicted by the speaker's OWN
same-turn task observation (greedy tick spans — the railroad's fuel), 47/891 ballots guard-normalized (invalid
dead targets / bad `primary_reason_id`), 64 accusations at confidence 1.0, 33% of ballots sharing one literal
rationale template, 23 missed-deadline turns. This task: (1) compute the full R-gate measurement (R1, R4
floor, R7, impostor win rate, rubric geomean) vs the final-9B baseline; (2) quantify how much of R1=27
survives DISCOUNTING the railroad rows (genuine deduction vs pile-on); (3) run the per-lever ablation of the
4 substrate flags (offline, $0; kill-scene fired 0× in the 9B smoke — UNMEASURED, not negative); (4) write
the characterization audit whose deliverable is the CONCRETE fix specs for 14.10 (the 10.1 cap defeat —
diagnose the exact bypass mechanism) and 14.11 (the v4 prompt fixes, with the per-defect counts above as the
baseline the re-record must beat).

**STATUS (2026-07-02) — MEASURED (audit: `audits/audit-2026-07-01-phase-14-baseline1-characterization.md`).**
R-gate on baseline 1 (9p2i): R1 **27/50** (9B 3/50), R4 wrong-ejection games **39** (9B 4 — the inversion
headline), impostor win **0.32** (floor ✓), R7 **43/152 (28%)** (9B 13/195), geomean eject-decided median
61.3 vs stopwatch max 43.5 with 25/27 above every stopwatch (the 2 exceptions are the rubric's own railroad
floor firing — seeds 12/21 at 0.0). **Railroad-discounted R1 = 25/50** (only seeds 13/16 of the 27 run
through a pinned railroad meeting). Hypothesis verdict: REVISED as charted — the ceiling bound concealment,
conversion OVERSHOT into over-conviction (ejection accuracy 0.566). Cap-bypass diagnosis (exact fold
reproduction, 2482/2482 recorded render rows matched): the 10.1/13.14 caps HOLD — one STRONG
`alibi_vs_sighting` lift-key group saturates the +0.30 budget and gate-crosses the WHOLE roster at 0.80,
and the pre-13.5 Rule-1 body-proximity prior (0.70) compounds to the 1.00 clamp for at-scene voters
(impostors, in all 5 pinned rows); fuel = factually-false testimony (97–100% of flagged ejectee alibis
false vs engine truth; 47–67% of refuting sightings false). Per-lever ablation committed
(`experiments/lab/results-substrate-ablation.jsonl`): no lever harmful, none causes the railroad (5 rows in
every cell) — **14.9 default-ON set confirmed**; kill-scene detector fired 1×/152 meetings (effectively
UNMEASURED, not negative); unfreeze verified 554/554 on recorded bytes. **Confirmed 14.10 targets:**
certain-guilt exclusion (transient flag lift never renders 1.0 absent first-hand conclusive evidence) +
sloppy-testimony downgrade (self-refuted alibi group → WEAK delta; 0/57 impostor vs 6/31 crew flagged
ejections — zero conversion cost); witness-count weighting and ≥2-strong-group gating are measured
ANTI-signals (do not implement). **Confirmed 14.11 targets (the counts v4 must beat):** 30/295 (10.2%)
self-contradicted self-alibis, 27 invalid-target + 20 invalid-reason-id ballots (= the 47 guard-normalized),
64/505 conf-1.0 accusations, 320/891 (35.9%) "p-N's alibi …" template-family rationales, 23 missed-deadline
turn markers (all 27 `deadline_default` rows validation-triggered — output discipline, caps stay FROZEN).

**Files in scope:**
- audits/audit-2026-07-01-phase-14-baseline1-characterization.md (new: the R-gate measurement + railroad-discounted R1 + the per-lever ablation + the REVISED hypothesis verdict + the 14.10/14.11 fix specs)
- api/replay_loader.py (a small ANALYSIS-ONLY override on the reconstruction entry — e.g. `allow_substrate_mismatch: bool = False` threaded to `_assert_substrate_matches` — because the per-lever ablation DELIBERATELY re-derives the stamped all-ON baseline under toggled levers, which the Task-14.7 guard otherwise correctly refuses; default False so the serving/verify paths keep failing loud, additive only)
- experiments/lab/results-substrate-ablation.jsonl (new: per-lever ablation — each of the 4 flags toggled offline over the baseline replays via the override, R-gate / conversion metrics per cell, each row recording that the mismatch was deliberate; $0)
- tasks/phase-14.md (a STATUS banner recording the measurement outcome and the confirmed 14.10/14.11 targets)
- experiments/lab/report-rubric-interestingness.md (re-ranked offline — data regen; the score json was already regenerated by the 14.7 refresh)
- tests/api/test_replay_loader.py (the override: default-off keeps the guard firing; True permits the mismatch; no other loader behavior change)

**Files NOT in scope:**
- llm/ + agents/ + meetings/ + engine/ (no behavior change here beyond the loader's opt-in analysis override; the fixes are 14.10/14.11)
- replays/samples/ (the 14.7 bytes are baseline 1; this READS them)
- eval/ source (the analyzers are reused as-is; this folds, it does not change them)

**Definition of done:**
- [ ] The R-gate is computed offline over the 14.7 flags-ON baseline (R1, R4 floor, R7, impostor win rate, rubric geomean ranking) and compared to the final-9B baseline (R1 3/50, impostor 84%, eject 9%).
- [ ] The railroad-discounted R1 is computed (R-gate with the 5 pinned railroad rows' meetings discounted) so 14.12 can tell genuine-deduction gains from pile-on gains.
- [ ] A per-lever ablation (each of the 4 13.5 flags toggled offline over the baseline replays) characterizes each lever's contribution and confirms the 14.9 default-ON set; the kill-scene flag's 0× firing is noted as UNMEASURED (needs a richer scenario), not a negative result. THIS TASK IS THE LAST CHANCE to run it: 14.9 deletes the very toggles the ablation flips — the ablation must be complete and committed before 14.9 dispatches.
- [ ] The analysis-only substrate-mismatch override is added to the loader (default OFF — the serving/verify paths still fail loud; the ablation harness passes it explicitly) with a test for both positions; no other reconstruction behavior changes.
- [ ] The audit states the REVISED hypothesis verdict honestly: the ceiling bound concealment, not conversion; the live problem is now over-conviction (ejection accuracy 0.566) — with the evidence for each claim.
- [ ] The audit specifies the 14.10 fix (the exact mechanism by which ≥2 same-meeting flags defeat the 10.1 cap, from the pinned rows) and the 14.11 targets (the measured per-defect counts: 10% self-contradicted alibis, 47 guard-normalized ballots, 64 conf-1.0 accusations, 33% template rationales, 23 missed-deadline turns).
- [ ] The rubric interestingness report is re-ranked offline over the committed replays ($0, no code change); no number is retrofit to pass.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Pure offline folds over the new `TournamentReport`: `eval/vote_correctness.py` (`ejection_accuracy`,
`compute_genuine_class_conversion`), `eval/accusation_calibration.py` (ECE), `eval/alibi_fabrication.py`
(survival_rate), assembled by `eval/meeting_quality.py`, plus the rubric geomean from
`experiments/lab/rubric_score.py` — all $0, no provider. The 5 railroad rows to discount are pinned in
`tests/meetings/test_manager.py` (`known_railroad`: seed-13 m0 p-7, seed-16 m0 p-6, seed-28 m0 p-3/p-6,
seed-44 m1 p-1); seed-44 m1 is the worked example of the fuel — crew p-1's greedy alibi (`CAFETERIA t5-14`
spanning their own recorded `STORAGE t14` task) minted the contradictions the pile-on ran on. The ablation
mechanics: the baseline replays are STAMPED all-ON, and `api/replay_loader.py:_assert_substrate_matches`
(correctly) refuses a mismatched re-derivation — so add the analysis-only override FIRST (a keyword threaded
from the reconstruction entry at `replay_loader.py:717`, default False), then toggle one lever at a time via
env for the ablation cells. Run the full-suite ablation BEFORE 14.9 lands (14.9 deletes the toggles). The
framing is the deliverable: the audit's job is a MEASUREMENT plus two actionable fix specs, so 14.10/14.11
dispatch against precise targets instead of vibes. Do not retrofit any number.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Open a PR from branch `phase-14-baseline-characterize-close` with a title like `task 14.8: characterize baseline 1 (r-gate as measurement) + fix recommendations`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py; PR #213 (baseline-1 findings)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
