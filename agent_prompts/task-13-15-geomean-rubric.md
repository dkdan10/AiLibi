# Agent Prompt — 13.15 Geomean interestingness rubric as a held-out referee (replace the additive sum)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.15 — Geomean interestingness rubric as a held-out referee (replace the additive sum), anchored to experiments/lab/report-rubric-design.md (the D1-D4 geomean spec + the §6 validation checks); experiments/lab/rubric_score.py:528 (the additive sum to replace) + :442 (`_game_interestingness`); experiments/lab/forward_redesign_detector_sweep.py (the re-extraction that lights R7 so D1-D4 are non-degenerate); the Phase-13 grounding-audit verdict (the rubric is a held-out referee, NEVER the inner-loop gradient). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-geomean-rubric`
**Depends on:** 13.1
**Section refs:** experiments/lab/report-rubric-design.md (the D1-D4 geomean spec + the §6 validation checks); experiments/lab/rubric_score.py:528 (the additive sum to replace) + :442 (`_game_interestingness`); experiments/lab/forward_redesign_detector_sweep.py (the re-extraction that lights R7 so D1-D4 are non-degenerate); the Phase-13 grounding-audit verdict (the rubric is a held-out referee, NEVER the inner-loop gradient)
**Complexity:** Medium
**Files in scope:**
- experiments/lab/rubric_score.py
- experiments/lab/report-rubric-design.md
**Files NOT in scope:**
- api/schemas.py + tests/api/test_view_model.py — UNCHANGED; per_game KEEPS its `r1`–`r7` keys (the geomean replaces only `score`), so `RubricGameView` (requires `r1_decisive`/`r7_legible`) does not break
- the engine / meetings / agents / firewall — none touched (a pure-stdlib offline lab scorer)
- the ML inner-loop fitness — the geomean is the held-out SELECTION referee, NEVER the gradient (the FO-6 suspicion rank is the inner-loop fitness; do not wire the geomean into training)

Replace the additive R1-R7 sum (`rubric_score.py:528`) with the **epsilon-floored, weighted geometric
mean** of D1-D4 (`floor_multiplier * geomean_weighted(D1,D2,D3,D4)`, per `report-rubric-design.md`), so one
dead dimension SINKS the score (the additive sum lets a live R2 mask a dead R1 — it ranks the seed-0/16
stopwatch wins ABOVE every eject-decided game). D4 gains a **swing** term (`plurality_margin == 1` +
cross-meeting suspicion movement). Keep the hard floors (railroad-eject / friendly-fire /
firewall-or-determinism breach → 0). per_game KEEPS its `r1`–`r7` keys — the geomean replaces ONLY the `score`
value, so `RubricGameView` (`api/schemas.py:933`) does not break. It stays a **held-out referee** — it scores
recorded replays offline ($0), never the gradient.

**Decisions the implementer must fix (NOT in `report-rubric-design.md`, a narrative not a numeric spec):** the
4 geomean weights; the `floor_multiplier` value (recommend a hard 0, R4-style); the epsilon (1e-3); each Dₙ's
[0,1] mapping — esp. D2's suspicion-SEPARATION scalar (the raw data exists at `extract_gameplay_facts.py`; the
formula does NOT — specify it, do not re-extract). The "ranks ALL eject-decided above ALL `CREWMATE_TASKS`"
target may not hold under one weight vector — REPORT the achieved ranking in a `## Decisions` section, do not
tune weights to force it.

**Firewall/determinism:** a pure-stdlib offline scorer over recorded replays + roles (no live packet, no
engine); no firewall or determinism surface.
**Definition of done:** `rubric_score.py` composes `floor_multiplier * geomean_weighted(D1-D4)` (epsilon-
floored) replacing the additive sum; D4 includes the swing term; per_game still emits `r1`–`r7` keys (no
`RubricGameView` break); the geomean ranks eject-decided games above `CREWMATE_TASKS` stopwatch games with the
ACHIEVED ranking REPORTED in `## Decisions` (it does NOT collapse to 0 — D1-D4 route around the dead R7, so it
lands independently of R7), emitted as a committed `results-*.json` artifact mirroring `results-rubric-score.json`;
the hard floors hold; `scripts/check.sh` green.

## Implementation hint
implement D1-D4 + `floor_multiplier` per `report-rubric-design.md` and swap the `score = 100 * (...)` line
at `rubric_score.py:528`; add an epsilon (e.g. 1e-3) inside the geomean so a single zero term sinks the
score but does not NaN; D1-D4 do NOT require R7 (they route around the dead term), so run it on the committed
set directly; mirror the §6 validation as a committed results file.

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
Open a PR from branch `phase-13-geomean-rubric` with a title like `task 13.15: geomean interestingness rubric as a held-out referee (replace the additive sum)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-rubric-design.md (the D1-D4 geomean spec + the §6 validation checks); experiments/lab/rubric_score.py:528 (the additive sum to replace) + :442 (`_game_interestingness`); experiments/lab/forward_redesign_detector_sweep.py (the re-extraction that lights R7 so D1-D4 are non-degenerate); the Phase-13 grounding-audit verdict (the rubric is a held-out referee, NEVER the inner-loop gradient)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
