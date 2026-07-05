# Agent Prompt — 15.2 Selection referee: evidence-supply floors + the D1–D4 geomean, re-anchored to baseline 2

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.2 — Selection referee: evidence-supply floors + the D1–D4 geomean, re-anchored to baseline 2, anchored to experiments/lab/rubric_score.py (the D1–D4 geomean, weights :53, composition :823); experiments/lab/report-rubric-design.md; audits/post-phase-14-ML-training-signal.md §3.2, §4, §6 (referee-as-gate doctrine); audits/post-phase-14-ML-planning.md §12 (the perfect-stealth risk); eval/meeting_quality.py (supply/conversion gauges). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-watchability-referee`
**Depends on:** 15.1
**Section refs:** experiments/lab/rubric_score.py (the D1–D4 geomean, weights :53, composition :823); experiments/lab/report-rubric-design.md; audits/post-phase-14-ML-training-signal.md §3.2, §4, §6 (referee-as-gate doctrine); audits/post-phase-14-ML-planning.md §12 (the perfect-stealth risk); eval/meeting_quality.py (supply/conversion gauges)
**Complexity:** Medium

Build the committed champion-selection referee — the artifact that decides whether a trained candidate's
games are still a deduction game. Two layers, both selection-only (the module docstring states the
doctrine: this is a gate, NEVER a training reward). Layer 1, **evidence-supply floors** — the sharp,
data-grounded catch for the perfect-stealth failure mode: witnessed-event rate (baseline 2: 6/160 kills =
3.75% crew-witnessed in 9p2i), contradiction-flag production per meeting, and testimony-backed conversion,
wired from the existing supply/conversion gauges in `eval/meeting_quality.py`. The task measures each on
baseline 2 and pins floors at documented fractions of the measured values — evidence starvation (a
candidate whose games produce no flags and no witnesses) fails the referee even when meeting-rate stays
high, because bodies still trigger meetings after testimony has died. Layer 2, the **D1–D4 floor-gated
weighted geomean** promoted from lab-tier `experiments/lab/rubric_score.py` (which self-labels "NOT a
shipped eval gate" and is calibrated to baseline 1) into `eval/watchability.py`: weights {D1 .40, D2 .25,
D3 .15, D4 .20}, ε=1e-3, `score = 100 · floor · geomean`, floor∈{0,1} on a firewall/determinism breach,
friendly-fire, or railroad ejection — multiplicative, so a meeting-starved game collapses to ~0 by
construction. Re-anchor to baseline 2 and fold both layers into `scripts/measure_baseline.py
--watchability`.

**Files in scope:**
- eval/watchability.py (new: supply floors + geomean referee)
- scripts/measure_baseline.py (watchability fold region — 15.1 owns the core-folds region)
- tests/eval/test_watchability.py (new: parity, floor-trip, and supply-floor tests)

**Files NOT in scope:**
- experiments/lab/rubric_score.py + experiments/lab/rubric.md + replays/samples/9p2i/results-rubric-score.json (lab artifacts frozen; the API keeps serving the committed rubric file unchanged)
- api/ (no DTO/route change)
- eval/meeting_quality.py (gauges consumed, never edited)

**Definition of done:**
- [ ] Geomean parity: on the committed 9p2i facts, `eval/watchability.py` reproduces the lab scorer's per-game D1–D4 and composed scores (a parity test pins them), then the re-anchor to baseline 2 is applied with every changed threshold documented in the module docstring.
- [ ] The floor trips on synthetic fixtures: a railroaded ejection, a friendly-fire kill, and a determinism breach each force score 0.
- [ ] Evidence-supply floors: witnessed-event rate, flags-per-meeting, and testimony-backed conversion are measured on baseline 2, pinned as named constants with the measured values in comments, and a synthetic evidence-starved set (high meeting rate, zero flags, zero witnesses) FAILS the referee.
- [ ] The referee runs on BOTH sets from bytes — including 4p1i, which has no committed rubric artifact (the 9p2i/4p1i asymmetry is handled, not assumed away).
- [ ] `scripts/measure_baseline.py --watchability` emits per-game + aggregate referee results in the `--json` report consumed by 15.10 and 15.13.
- [ ] The module docstring states the selection-only doctrine and cites the Goodhart probe (15.9) as the referee's own acceptance test.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Promote, don't redesign: the geomean's structure already closed the known additive-rubric Goodhart traps
(masking, passive-survival gradients, railroad reward) — the deltas are committed+strict-typed, baseline-2
anchors, and byte/tournament-report inputs instead of the audit-tier facts JSON (document exactly which
facts-extraction subset is inlined). The supply gauges already exist in `eval/meeting_quality.py` — wire,
don't re-derive. Set the floors from measured baseline-2 values, not invented targets: the referee's job is
"do not accept a champion whose games produce structurally less evidence than the baseline," not "hit a
number." The lab file `GEOMEAN_RESULTS_FILENAME` machinery stays untouched — the committed 9p2i artifact is
the parity fixture, not a dependency.

## Public types this task introduces
- `eval.watchability.WatchabilityReport`
- `eval.watchability.compute_watchability`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.validity"`

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
Open a PR from branch `phase-15-watchability-referee` with a title like `task 15.2: selection referee: evidence-supply floors + the d1–d4 geomean, re-anchored to baseline 2`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/rubric_score.py (the D1–D4 geomean, weights :53, composition :823); experiments/lab/report-rubric-design.md; audits/post-phase-14-ML-training-signal.md §3.2, §4, §6 (referee-as-gate doctrine); audits/post-phase-14-ML-planning.md §12 (the perfect-stealth risk); eval/meeting_quality.py (supply/conversion gauges)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
