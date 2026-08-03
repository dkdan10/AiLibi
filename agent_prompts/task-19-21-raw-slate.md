# Agent Prompt — 19.21 The finalist raw slate: recover or label (owner)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.21 — The finalist raw slate: recover or label (owner), anchored to audits/audit-phase-19-triage.md §7 item 22 [C; VERIFIED §8 row 11]; training/reports/report-finalist-eval.md:115-118 ("the raw recordings … live outside the repo tree") + :1066-1070 (`~/ailibi-campaign-1826/scoring/…`); `git ls-files training/reports/_finalist_eval_raw` → empty; the 19.22 artifact classes (the store that would receive a recovered slate). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-raw-slate`
**Depends on:** 19.20, 19.22
**Section refs:** audits/audit-phase-19-triage.md §7 item 22 [C; VERIFIED §8 row 11]; training/reports/report-finalist-eval.md:115-118 ("the raw recordings … live outside the repo tree") + :1066-1070 (`~/ailibi-campaign-1826/scoring/…`); `git ls-files training/reports/_finalist_eval_raw` → empty; the 19.22 artifact classes (the store that would receive a recovered slate)
**Complexity:** Small

The 449-game slate behind the phase-18 adoption decision exists only on the owner's
machine, if at all. OWNER STEP (minutes): check whether `~/ailibi-campaign-1826/scoring/`
still exists. If YES: content-address it — per-file sha-256 manifest committed under
`training/reports/_finalist_eval_raw/` (manifest only; the bytes go to the 19.22
evidence store as class (c)) — and a dated erratum records the recovery and where the
bytes live. If NO: a dated erratum labels event-level finalist lineage NON-REPRODUCIBLE
(the flattened rows and every derived statistic remain reproducible from committed
cells — state exactly that boundary). Either way: do NOT re-record — the ~57-busy-hour
price is named and declined by charter.

**Files in scope:**
- training/reports/report-finalist-eval.md; (the availability erratum)
- training/reports/_finalist_eval_raw/MANIFEST.md (new, only on the recovery path)
- docs/artifacts.md; (the class-(c) registry row)

**Files NOT in scope:**
- replays/ (nothing is recorded)
- training/artifacts/ (19.22's surface)

**Definition of done:**
- [ ] One of the two outcomes is recorded with a dated erratum; on recovery, the manifest's shas cover every file and the evidence-store location is named; on loss, the reproducibility boundary is stated exactly.
- [ ] No re-recording occurred or is scheduled.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-19-raw-slate` with a title like `task 19.21: the finalist raw slate: recover or label (owner)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 22 [C; VERIFIED §8 row 11]; training/reports/report-finalist-eval.md:115-118 ("the raw recordings … live outside the repo tree") + :1066-1070 (`~/ailibi-campaign-1826/scoring/…`); `git ls-files training/reports/_finalist_eval_raw` → empty; the 19.22 artifact classes (the store that would receive a recovered slate)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
