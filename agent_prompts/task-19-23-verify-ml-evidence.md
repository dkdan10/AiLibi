# Agent Prompt — 19.23 `verify-ml-evidence`: one command

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.23 — `verify-ml-evidence`: one command, anchored to audits/audit-phase-19-triage.md §7 item 24 [S-Codex/S-Claude]; the Codex audit's executed-evidence table (each recomputation exists piecemeal today: sidecar/sha verification, corpus reconstruction, surrogate 0.7667/0.375, conviction 0.9375, composed 0.8646/0.7917); training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:11 (`_REPO = "/Users/danielkeinan/projects/AiLibi"` — the invocation folklore); scripts/paired_stats.py (19.20). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-verify-ml-evidence`
**Depends on:** 19.19, 19.20, 19.21, 19.22 (the availability report consumes the recorded raw-slate ruling)
**Section refs:** audits/audit-phase-19-triage.md §7 item 24 [S-Codex/S-Claude]; the Codex audit's executed-evidence table (each recomputation exists piecemeal today: sidecar/sha verification, corpus reconstruction, surrogate 0.7667/0.375, conviction 0.9375, composed 0.8646/0.7917); training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:11 (`_REPO = "/Users/danielkeinan/projects/AiLibi"` — the invocation folklore); scripts/paired_stats.py (19.20)
**Complexity:** Medium

One read-only command for the whole ML evidence story: `scripts/verify_ml_evidence.py`
runs sidecar/sha verification (296 sidecars), corpus reconstruction (delegating to the
existing verifiers), surrogate/conviction/composed recomputation against the committed
verdicts, the paired finalist statistics (via `scripts/paired_stats`), and an
artifact-availability report per `docs/artifacts.md` class (in-tree / evidence-branch /
repo-external / lost) — offline, $0, one exit code. Beside it, preserve the exact
campaign invocations: a committed appendix in `training/README.md` recording the
harness invocations currently living as hard-coded-path provenance folklore, rewritten
repo-relative.

**Files in scope:**
- scripts/verify_ml_evidence.py (new)
- tests/scripts/test_verify_ml_evidence.py (new)
- training/README.md; (the invocation appendix — dep-ordered behind 19.18/19.19)

**Files NOT in scope:**
- training/ (recomputation delegates to existing modules; nothing retrains)
- scripts/paired_stats.py (consumed, not edited)

**Definition of done:**
- [ ] The command runs green at HEAD in one invocation, listing every check with its measured value vs the committed verdict, and the availability class of every named evidence artifact (including the 19.21 outcome).
- [ ] It is read-only (no artifact writes outside a temp dir) and offline; a perturbed-input test proves it fails loud.
- [ ] The invocation appendix reproduces the recorded harness invocations repo-relative, citing the provenance files it replaces.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Wrap, don't reimplement: each leg calls the existing verifier/recomputation entry point
and compares against the committed verdict file. The runtime budget matters — the full
run should finish in minutes; put the corpus reconstruction behind a `--fast` flag that
samples if the full walk exceeds that budget, with the sampling disclosed in output.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.realpath_schema"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-19-verify-ml-evidence` with a title like `task 19.23: `verify-ml-evidence`: one command`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 24 [S-Codex/S-Claude]; the Codex audit's executed-evidence table (each recomputation exists piecemeal today: sidecar/sha verification, corpus reconstruction, surrogate 0.7667/0.375, conviction 0.9375, composed 0.8646/0.7917); training/artifacts/coevo/provenance/harnesses/harness_run_c1.py.txt:11 (`_REPO = "/Users/danielkeinan/projects/AiLibi"` — the invocation folklore); scripts/paired_stats.py (19.20)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
