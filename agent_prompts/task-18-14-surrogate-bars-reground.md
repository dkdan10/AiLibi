# Agent Prompt — 18.14 Surrogate re-ground + re-verdict + selection-bar re-pins (baseline 6)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.14 — Surrogate re-ground + re-verdict + selection-bar re-pins (baseline 6), anchored to training/reports/report-ballot-surrogate.md §8 (the executed re-grounding recipe); training/surrogate/ (the 17.10 machinery, re-run); training/bakeoff/harness.py:174-181 (`GOODHART_9P2I_BASELINE`) + `BAKEOFF_BASELINE_ID`; tasks/phase-17.md 17.10 + 17.11 (the two contracts this combines). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-surrogate-bars-reground`
**Depends on:** 18.13
**Section refs:** training/reports/report-ballot-surrogate.md §8 (the executed re-grounding recipe); training/surrogate/ (the 17.10 machinery, re-run); training/bakeoff/harness.py:174-181 (`GOODHART_9P2I_BASELINE`) + `BAKEOFF_BASELINE_ID`; tasks/phase-17.md 17.10 + 17.11 (the two contracts this combines)
**Complexity:** Medium

One turn of the standing re-grounding crank at the new substrate: re-validate the belief
walk on the baseline-6 corpus BEFORE trusting any fit, re-fit the ballot predictor
(6-feature fence kept — locked decision 1 rejected widening it), re-derive the staleness
cap under the ~143× rule, re-state the GO/NO-GO on the same population-relative bar, and
flip the selection constants (`BAKEOFF_BASELINE_ID` → `"baseline-6"`, the Goodhart
fake-path baseline re-measured, the report refreshed). The 17.10 honesty discipline
travels: the decision-channel diagnosis is re-stated on the new economy, whichever way it
reads.

**Files in scope:**
- training/artifacts/surrogate/ (weights + sidecar + max-uses, re-fit)
- training/artifacts/anchor_study/ + tests/training/test_anchor_study.py (the baseline-6 re-run of the 18.5 study artifacts — cheap and deterministic; clears their substrate tripwires; PR #301's scope question, resolved by coordination: the re-ground task re-grounds everything substrate-bound in one place)
- training/artifacts/impostor/map-elites/ + tests/training/test_bakeoff_methods.py (same, for the 18.6 cell artifacts)
- training/surrogate/runner.py (ONE additive fence: the loader/cap learns the corpus identity — `SurrogateStalenessCap` is blind to substrate drift today; sha-keying extends to the fit corpus, fail-loud on mismatch)
- training/reports/report-ballot-surrogate.md (the baseline-6 reading)
- training/bakeoff/harness.py; (the two constant blocks ONLY)
- tests/training/test_surrogate_runner.py
- tests/training/test_surrogate_fidelity.py
- tests/training/test_surrogate_dataset.py
- tests/training/test_bakeoff_harness.py; (the two constant blocks' pins ONLY)
- tests/training/test_goodhart_probe.py; (the re-measured fake-path baseline pin ONLY)

**Files NOT in scope:**
- training/surrogate/*.py (the machinery re-runs; it does not change)
- eval/watchability.py; (floors pinned at 18.12)

**Definition of done:**
- [ ] Walk re-validation (fold fidelity 0 mismatches; J1 divergence re-measured) recorded BEFORE the fit; the re-fit artifact + re-derived cap committed together with the re-stated verdict on the unchanged bar; coerced-SKIP census quoted.
- [ ] `BAKEOFF_BASELINE_ID` and the Goodhart baseline constants read baseline-6, with the fake-path ceiling re-measured, and every dependent pin green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The §8 recipe is executable as written. The measured inputs (18.13 verification, computed
from committed bytes): the baseline-6 corpus is **EJECT-MAJORITY** — 302/463 = 65.2%
ejected meetings, voter-ballot SKIP share 42.1% (baseline 5 was skip-majority at 58.4%) —
so axis 3's always-eject constant is back at FULL strength and a NO-GO is a plausible
honest verdict (its consequence is pre-committed: diagnostic-only + the fake-provider
fallback; the bake-off is never blocked, and 18.15's conviction model carries its own
independent GO). Fit-side meetings are **367** (train+val; test 96), so the ~143× cap
re-derives to **52,481**. Clear the seven `_PENDING_SURROGATE_REGROUND_1814` xfails and
the self-clearing tripwires this re-fit trips. Record-provenance note: cite committed
tests/README for corpus cells, never PR #301's body (pre-repair tables); the corpus
MANIFEST per-row shas are the recording truth (the FROZEN lines carry re-finalize shas).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`

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
Open a PR from branch `phase-18-surrogate-bars-reground` with a title like `task 18.14: surrogate re-ground + re-verdict + selection-bar re-pins (baseline 6)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/reports/report-ballot-surrogate.md §8 (the executed re-grounding recipe); training/surrogate/ (the 17.10 machinery, re-run); training/bakeoff/harness.py:174-181 (`GOODHART_9P2I_BASELINE`) + `BAKEOFF_BASELINE_ID`; tasks/phase-17.md 17.10 + 17.11 (the two contracts this combines)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
