# Agent Prompt — 13.1 Repair the rubric scorer (R2/R3/R7 perverse gradients)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.1 — Repair the rubric scorer (R2/R3/R7 perverse gradients), anchored to experiments/lab/report-grounding-audit.md (the audit findings + punch-list; on main via PR #181); experiments/lab/rubric_score.py; eval/meeting_quality.py; audits/workflows/extract_gameplay_facts.py; agents/strategic/../transcript.py (`is_weak_contradiction`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-rubric-repair`
**Depends on:** none
**Section refs:** experiments/lab/report-grounding-audit.md (the audit findings + punch-list; on main via PR #181); experiments/lab/rubric_score.py; eval/meeting_quality.py; audits/workflows/extract_gameplay_facts.py; agents/strategic/../transcript.py (`is_weak_contradiction`)
**Complexity:** Integration
**Files in scope:**
- experiments/lab/rubric_score.py
- experiments/lab/results-rubric-score.json
- experiments/lab/report-rubric-interestingness.md
**Files NOT in scope:**
- agents/memory/beliefs.py and the detector — the inferential-suspicion path is workstream B (a later Phase-13 task), NOT this one
- the ML fitness architecture (FO-6-rank inner-loop, rubric-as-held-out-gate, watch-the-games) — Phase-C entry, recorded in the ML plan
- engine/ and the recorded replays — the rubric is computed offline from committed replays; NO re-record
- frontend/ and api/ — they consume `results-rubric-score.json` as DATA; regenerating it re-ranks Highlights with no code change

Repair `experiments/lab/rubric_score.py` so its per-game score stops rewarding degenerate play (the audit's
three verified perverse gradients), reusing signals the codebase already computes — then regenerate the
artifact and PROVE the gradients are gone. **R2 (passive-survival → anti-correlated).** Today
`survived_accused` is alive-and-not-ejected with no active gate (`rubric_score.py:270-297`), so a passive
LOSS (R2 0.6) outscores a passive WIN (R2 0.4) and R2 is anti-correlated with the total (Pearson −0.281).
Gate R2 credit on an ACTIVE-deflection event — reuse `eval/meeting_quality.py::compute_effective_deflection`'s
ACTIVE-DEFLECTED class — scoring passive/clock survival ~0.0–0.2; and report **R1 and R2 as SEPARATE outputs**
(do not let R1 swamp R2 in one scalar). **R3 (flagless-carry → rewards the railroad R4 forbids).** Today
`r3` gives 0.5 for ≥2 meetings + 0.5 for any `carry_eject`, including a flagless meeting-0 conviction of an
innocent (seed-15 scores R3 1.0; `rubric_score.py:300-305`). Require the ejected subject's rendered suspicion
to RISE across ≥2 meetings AND land on a true impostor — source from the extractor's `accumulator_trajectories`
(`extract_gameplay_facts.py`) + the firewalled role. **R7 (weak-flag presence).** Today `r7` counts raw
`n_contradictions>0` (`rubric_score.py:308`); all 112 baseline flags are WEAK `alibi_vs_sighting` (+0.08,
below the 0.60 gate, eject nobody). Count a meeting as evidence-bearing only if it carries a STRONG
(non-weak) contradiction naming a true impostor — reuse `is_weak_contradiction` (`transcript.py`) + the role;
cap per-meeting credit at 1. Also **drop `ballot_follows_chain` from any fitness aggregate** and relabel it a
diagnostic (remove the "UP-is-good" note at `rubric_score.py:227-233`) — 65% of non-skip ballots are
null-reason BY DESIGN, so it measures a coherence the meeting architecture deliberately suppresses. **Hygiene
(P2):** give `IMPOSTOR_SABOTAGE` its own `_win_shape` branch before the `startswith('IMPOSTOR')` catch-all
(`rubric_score.py:242`), and stamp the SET manifest sha (not scoring HEAD) on the lab-local
`results-rubric-score.json` write. R1's `CREWMATE_EJECT` definition is SOUND — keep it byte-identical.
**Definition of done:** R2 is gated on active deflection (passive/clock survival ≤ 0.2) and R1/R2 are reported
as separate terms; R3 credits only a cross-meeting suspicion RISE onto a true impostor (seed-15's innocent
conviction no longer scores R3 > 0); R7 counts only STRONG contradictions naming a true impostor (the
all-weak baseline scores R7 = 0); `ballot_follows_chain` is out of the fitness aggregate and labeled a
diagnostic; `IMPOSTOR_SABOTAGE` has its own win-shape; `results-rubric-score.json` is regenerated stamped with
the SET manifest sha; a VALIDATION re-run over the committed 9p2i set shows the three perverse gradients are
gone (R2 no longer anti-correlated with the total; the seed-15 R3 and all-weak R7 cases fall to 0) while
calibration at the extremes is preserved (the audit's top-3 seeds 5/47/34 still rank above the dull bottom);
R1 unchanged; NO re-record; `scripts/check.sh` is green.

## Implementation hint
reuse the existing signals by import — `compute_effective_deflection` (`eval/meeting_quality.py`),
`accumulator_trajectories` (the extractor), `is_weak_contradiction` (`transcript.py`) — never re-derive; keep
R1's `CREWMATE_EJECT` branch byte-identical. Emit the score as a STRUCTURED object (R1, R2, R3, R7 reported
separately) rather than only the collapsed scalar, so Phase-C can take multi-objective axes. Re-run the scorer
over the committed 9p2i set and diff the per-seed scores to confirm the intended ranking shift (perverse cases
down, genuine cases up) before regenerating the committed artifact.

## Integration risk
the score change RIPPLES to consumers — the front-end `/eval/rubric` + Highlights/Dashboard read
`results-rubric-score.json` (regenerate it and let the staleness guard re-stamp; no front-end code change, but
the reel re-ranks) and Phase-C will read these terms as fitness, so keep R1 byte-identical and the term names
stable. Offline-only (committed replays in, JSON out): NO engine change, NO re-record, firewall/determinism
untouched. Validate against the audit's SPECIFIC cases (the Pearson sign on R2, seed-15 R3, the all-weak R7) —
a repair that does not flip those has not fixed the gradient.

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
Open a PR from branch `phase-13-rubric-repair` with a title like `task 13.1: repair the rubric scorer (r2/r3/r7 perverse gradients)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-grounding-audit.md (the audit findings + punch-list; on main via PR #181); experiments/lab/rubric_score.py; eval/meeting_quality.py; audits/workflows/extract_gameplay_facts.py; agents/strategic/../transcript.py (`is_weak_contradiction`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
