# Agent Prompt — 15.11 The meeting training table + surrogate fidelity harness (re-baseline FO-6 honestly)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.11 — The meeting training table + surrogate fidelity harness (re-baseline FO-6 honestly), anchored to audits/post-phase-14-ML-training-signal.md §2, §5.4-5.5, §7.2 (the table, the fidelity protocol, the honest ceiling); agents/memory/beliefs.py (the LLM-free belief fold); meetings/manager.py (derive_belief_evidence :2680; roster off result.ballots :2823); experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (the failed prior). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-meeting-table`
**Depends on:** 15.7, 15.8
**Section refs:** audits/post-phase-14-ML-training-signal.md §2, §5.4-5.5, §7.2 (the table, the fidelity protocol, the honest ceiling); agents/memory/beliefs.py (the LLM-free belief fold); meetings/manager.py (derive_belief_evidence :2680; roster off result.ballots :2823); experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (the failed prior)
**Complexity:** Medium

Build the supervised substrate the ballot surrogate trains and is judged on — against **baseline 3**
(this task runs after 15.7 so the table reflects the meeting layer the surrogate will simulate). For
every committed meeting, reconstruct OFFLINE (LLM-free, replay-deterministic) the per-(meeting, voter)
feature rows: the pre-meeting belief-fold state (rendered suspicion/trust toward each candidate — the
fold in `agents/memory/beliefs.py` is deterministic over recorded events and needs no LLM),
contradiction-flag structure (including the new vent flags), sighting/co-presence reconstruction,
reporter identity, kill-proximity and isolation, movement anomalies, and task-cadence features — joined
to the ACTUAL recorded ballots `{voter, target, confidence, primary_reason_id}` and to roles ground
truth from `tournament-eval-report.json` (raw replays carry no roles by firewall design). Ship the
fidelity harness the phase judges ALL meeting models with: by-GAME cross-validation (never by-meeting —
leakage), top-1/top-2 ejected-target ranking, SKIP-vs-eject decision accuracy, and Brier/ECE calibration
on ballot confidences — plus the HONEST CEILING: the measured voice-driven share of ejections a
physical+belief surrogate structurally cannot see. Re-run the FO-6 logistic under this harness to pin
the true prior baseline (its headline top-1 64% collapsed to 26%/43% on baseline 2, and its binary head
degenerates to always-SKIP), and mark the stale spike conclusion at its source:
`experiments/lab/report-ml-spike.md` gets a STALE banner pointing here. The table builder takes any
replay-set directory and reads a committed `splits.json` when present — it runs identically on the 15.12
corpus.

**Files in scope:**
- training/surrogate/__init__.py (new)
- training/surrogate/dataset.py (new: the table builder + splits.json loader)
- training/surrogate/fidelity.py (new: CV protocol + metrics + the honest ceiling — the GO/NO-GO wiring is 15.13's region)
- training/reports/report-meeting-table.md (new: table stats, FO-6 re-baseline, the honest ceiling)
- experiments/lab/report-ml-spike.md (STALE banner only — no other edit)
- tests/training/test_surrogate_dataset.py (new)
- tests/training/test_surrogate_fidelity.py (new)

**Files NOT in scope:**
- agents/memory/beliefs.py + meetings/manager.py (the fold is consumed read-only)
- experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (frozen probe; re-run, not edited)
- replays/ (read-only; the corpus lands in 15.12)

**Definition of done:**
- [ ] Table counts reproduce the ACTIVE committed sets exactly (meeting/ejection/ballot totals derived from the sets' tournament reports, not hardcoded — the sets are baseline 3 by this task's dependency order); every recorded ballot joins a feature row (100% join rate, asserted).
- [ ] Every feature column derives offline: no LLM call, no network, no engine import in `training/surrogate/` beyond the orchestrator-mediated reconstruction path; a determinism test rebuilds the table twice byte-identically.
- [ ] The fidelity harness enforces by-game CV (a leakage test proves two meetings of one game never split across folds) and reports top-1/top-2, SKIP-vs-eject accuracy, and Brier/ECE together — never a single headline number.
- [ ] The honest ceiling is computed from the committed bytes and stated in the report as the surrogate's maximum achievable top-1 — a measurement, not a target.
- [ ] The FO-6 re-baseline row appears in the report with its by-game-CV numbers and its always-SKIP failure made explicit.
- [ ] `experiments/lab/report-ml-spike.md` carries the STALE banner naming the regressed figure and pointing at the report this task commits.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The single biggest upgrade over FO-6's six raw counts is the belief-fold rendered suspicion — it already
integrates the accumulators the LLM votes on, and `derive_belief_evidence` (`meetings/manager.py:2680`)
re-derives the exact pre-meeting graph deterministically from recorded events. Mine
`audits/workflows/extract_gameplay_facts.py` and `eval/funnel.py` (15.3) for reconstruction recipes —
import the committed 15.3 folds where they fit; never import the audit script or the mypy-excluded
spike. Row grain is one row per (meeting, voter) — the roster the cross-meeting fold uses is read off
`result.ballots`, which fixes it.

## Public types this task introduces
- `training.surrogate.dataset.MeetingTableRow`
- `training.surrogate.dataset.build_meeting_table`
- `training.surrogate.fidelity.SurrogateFidelityReport`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.funnel"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import eval.watchability"`

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
Open a PR from branch `phase-15-meeting-table` with a title like `task 15.11: the meeting training table + surrogate fidelity harness (re-baseline fo-6 honestly)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-training-signal.md §2, §5.4-5.5, §7.2 (the table, the fidelity protocol, the honest ceiling); agents/memory/beliefs.py (the LLM-free belief fold); meetings/manager.py (derive_belief_evidence :2680; roster off result.ballots :2823); experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (the failed prior)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
