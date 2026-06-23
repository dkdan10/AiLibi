# Agent Prompt — 13.15 Geomean interestingness rubric as a held-out referee (replace the additive sum)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.15 — Geomean interestingness rubric as a held-out referee (replace the additive sum), anchored to experiments/lab/report-rubric-design.md (the D1-D4 geomean spec + the §6 validation checks); experiments/lab/rubric_score.py:528 (the additive sum to replace) + :442 (`_game_interestingness`); experiments/lab/forward_redesign_detector_sweep.py (the re-extraction that lights R7 so D1-D4 are non-degenerate); the Phase-13 grounding-audit verdict (the rubric is a held-out referee, NEVER the inner-loop gradient). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-geomean-rubric`
**Depends on:** 13.1, 13.14
**Section refs:** experiments/lab/report-rubric-design.md (the D1-D4 geomean spec + the §6 validation checks); experiments/lab/rubric_score.py:528 (the additive sum to replace) + :442 (`_game_interestingness`); experiments/lab/forward_redesign_detector_sweep.py (the re-extraction that lights R7 so D1-D4 are non-degenerate); the Phase-13 grounding-audit verdict (the rubric is a held-out referee, NEVER the inner-loop gradient)
**Complexity:** Medium
**Files in scope:**
- experiments/lab/rubric_score.py
- experiments/lab/report-rubric-design.md
**Files NOT in scope:**
- the engine / meetings / agents / firewall — none touched (a pure-stdlib offline lab scorer)
- the ML inner-loop fitness — the geomean is the held-out SELECTION referee, NEVER the gradient (the FO-6 suspicion rank is the inner-loop fitness; do not wire the geomean into training)

Replace the additive R1-R7 sum (`rubric_score.py:528`) with the **epsilon-floored, weighted geometric
mean** of D1-D4 (`floor_multiplier * geomean_weighted(D1,D2,D3,D4)`, per `report-rubric-design.md`), so one
dead dimension SINKS the score (the additive sum lets a live R2 mask a dead R1 — it ranks the seed-0/16
stopwatch wins ABOVE every eject-decided game). D4 gains a **swing** term (`plurality_margin == 1` +
cross-meeting suspicion movement). Keep the hard floors (railroad-eject / friendly-fire /
firewall-or-determinism breach → 0). It stays a **held-out referee** — it scores recorded replays offline
($0), never the gradient.

**Firewall/determinism:** a pure-stdlib offline scorer over recorded replays + roles (no live packet, no
engine); no firewall or determinism surface.
**Definition of done:** `rubric_score.py` composes `floor_multiplier * geomean_weighted(D1-D4)` (epsilon-
floored) replacing the additive sum; D4 includes the swing term; on a re-extracted committed set (R7 lit by
Task 13.14) it ranks ALL eject-decided games ABOVE all `CREWMATE_TASKS` stopwatch games with no perverse
R2/R3/R7 sub-gradient, emitted as a committed `results-*.json` artifact mirroring `results-rubric-score.json`;
the hard floors hold; `scripts/check.sh` green.

## Implementation hint
implement D1-D4 + `floor_multiplier` per `report-rubric-design.md` and swap the `score = 100 * (...)` line
at `rubric_score.py:528`; add an epsilon (e.g. 1e-3) inside the geomean so a single zero term sinks the
score but does not NaN; run it against the Task-13.14 re-extracted set so R7 is non-zero; mirror the §6
validation as a committed results file.

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
Open a PR from branch `phase-13-geomean-rubric` with a title like `task 13.15: geomean interestingness rubric as a held-out referee (replace the additive sum)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-rubric-design.md (the D1-D4 geomean spec + the §6 validation checks); experiments/lab/rubric_score.py:528 (the additive sum to replace) + :442 (`_game_interestingness`); experiments/lab/forward_redesign_detector_sweep.py (the re-extraction that lights R7 so D1-D4 are non-degenerate); the Phase-13 grounding-audit verdict (the rubric is a held-out referee, NEVER the inner-loop gradient)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
