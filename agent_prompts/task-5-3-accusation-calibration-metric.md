# Agent Prompt — 5.3 Accusation-calibration metric

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.3 — Accusation-calibration metric, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-accusation-calibration-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

A pure analyzer over `eval.report_schema.TournamentReport` that answers
DESIGN.md §11.3's calibration question: are high-confidence accusations
correct (the target really is an impostor) more often than low-confidence
ones? A well-calibrated agent population shows actual-impostor-rate rising
monotonically with stated confidence.

Accusations carry an explicit confidence in two places, both reachable from
the report:

- `AccusationClaim` (`type="accusation"`, `against: PlayerId`, `confidence:
  float` in [0,1], `reason: str`) — nested in `Statement.claims` and
  `ReportDocument.claims` inside `MeetingReport.transcript`.
- `VoteBallot` (`voter`, `target: PlayerId | "SKIP"`, `confidence: float`) on
  `MeetingReport.ballots`.

Correctness is decided by `GameReport.roles[target] == "IMPOSTOR"` — the
ground-truth map the 5.6 loader fills, never an inferred role.

**Files in scope:**
- eval/accusation_calibration.py
- tests/eval/test_accusation_calibration.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/report_schema.py
- eval/vote_correctness.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/accusation_calibration.py` exposes a pure function from a `TournamentReport` to a frozen Pydantic result model binning accusations by confidence and reporting per-bin actual-impostor-rate, count, and mean confidence.
- [ ] Bin edges are an explicit, documented choice (e.g. fixed-width deciles or quartiles over [0,1]); the binning is deterministic and total. Because `confidence` is `Field(ge=0.0, le=1.0)`, `1.0` is a legal value: bins are half-open `[lo, hi)` except the final bin, which is closed `[lo, 1.0]`, so `confidence == 1.0` lands in the top bin (implement as `bin_index = min(int(c * n_bins), n_bins - 1)`).
- [ ] Each accusation's correctness is `roles[target] == "IMPOSTOR"` (subscript, not `.get`); a `"SKIP"` ballot target is excluded BEFORE the lookup (it accuses no one). `roles` is post-game ground truth covering every player by construction, so a target absent from `roles` signals a malformed report and MUST fail loud (raise) — AGENTS.md "no silent fallbacks". Do not add an "unresolved" bucket and do not let a failed lookup silently count as a non-hit (which would bias that bin's actual-impostor-rate downward). The no-accusations / no-meetings / all-`SKIP` robustness below applies to the ABSENCE of accusations, never to a present accusation with an unresolvable target.
- [ ] Decision recorded in the PR's `## Decisions` block: which confidence source(s) the metric consumes — `AccusationClaim` only, `VoteBallot` only, or both (and if both, whether they are pooled into one curve or reported as two). Bias: report `AccusationClaim`-based and `VoteBallot`-based calibration separately, since a vote and a mid-meeting accusation are different acts.
- [ ] The result model exposes enough to judge calibration (per-bin actual-impostor-rate vs bin midpoint); a scalar calibration error (e.g. expected-calibration-error) is optional but, if included, documented.
- [ ] Partial-replay robustness: a game with no accusations, no meetings, or all-`SKIP` ballots produces empty/zero bins without raising.
- [ ] `tests/eval/test_accusation_calibration.py` builds report fixtures directly covering: high-confidence accusations against real impostors (well-calibrated); high-confidence accusations against crewmates (mis-calibrated); a spread across bins including `confidence` exactly `0.0` and exactly `1.0` (to pin the boundary convention); the no-accusations / all-`SKIP` case; and a malformed accusation whose target is absent from `roles`, asserting the analyzer raises.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

See DESIGN.md §11.3. Walk every `MeetingReport`; pull `AccusationClaim`s out
of `transcript.reports[*].claims` and `transcript.statements[*].claims`
(filter the `Claim` union on `type == "accusation"`), and/or `ballots` per
the source decision. For each `AccusationClaim`, bucket by `confidence` and
tally `roles[claim.against] == "IMPOSTOR"`. For a `VoteBallot` (if the source
decision includes ballots), first skip `target == "SKIP"`, then tally
`roles[ballot.target] == "IMPOSTOR"` — note the ballot field is `target` (not
`against`) and may be the literal `"SKIP"`. A bin's actual-impostor-rate is
`impostor_hits / accusations_in_bin`. Calibration is read off by comparing
that rate to the bin's confidence midpoint. Build fixtures by instantiating
the schema models directly; this task does NOT touch the tournament runner
(that is Task 5.6).

## Public types this task introduces
- `eval.accusation_calibration.AccusationCalibrationReport`
- `eval.accusation_calibration.CalibrationBin`
- `eval.accusation_calibration.compute_accusation_calibration`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.report_schema"`
- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-5-accusation-calibration-metric` with a title like `task 5.3: accusation-calibration metric`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
