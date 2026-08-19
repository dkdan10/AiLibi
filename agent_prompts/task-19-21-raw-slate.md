# Agent Prompt — 19.21 The finalist raw slate: recover or label (owner)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.21 — The finalist raw slate: recover or label (owner), anchored to audits/audit-phase-19-triage.md §7 item 22 [C; VERIFIED §8 row 11]; training/reports/report-finalist-eval.md:115-118 ("the raw recordings … live outside the repo tree") + :1066-1070 (`~/ailibi-campaign-1826/scoring/…`); `git ls-files training/reports/_finalist_eval_raw` → empty; the 19.22 artifact classes (the store that would receive a recovered slate). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-raw-slate`
**Depends on:** 19.20 (the availability check runs BEFORE the evidence commit — the artifact-classes task consumes this ruling so the phase creates ONE immutable evidence commit, not two)
**Section refs:** audits/audit-phase-19-triage.md §7 item 22 [C; VERIFIED §8 row 11]; training/reports/report-finalist-eval.md:115-118 ("the raw recordings … live outside the repo tree") + :1066-1070 (`~/ailibi-campaign-1826/scoring/…`); `git ls-files training/reports/_finalist_eval_raw` → empty; the 19.22 artifact classes (the store that would receive a recovered slate)
**Complexity:** Small

The 449-game slate behind the phase-18 adoption decision exists only on the owner's
machine, if at all. OWNER STEP (minutes): check whether `~/ailibi-campaign-1826/scoring/`
still exists — BEFORE 19.22 creates the evidence commit, so preservation is one
transaction. If YES: content-address it — per-file sha-256 manifest committed under
`training/reports/_finalist_eval_raw/` — AND stage the bytes where the dispatched
artifact task can reach them: the owner step pushes a temporary
`evidence/raw-slate-staging` ref carrying the slate bytes (one scripted command,
manifest-verified on push), because an agent on a fresh checkout cannot materialize
files from their hashes; the artifact-classes task folds the staging ref into the
single immutable evidence commit and retires it. A dated erratum records the recovery
and where the bytes will live. If NO: a dated erratum labels event-level finalist lineage
NON-REPRODUCIBLE (the flattened rows and every derived statistic remain reproducible
from committed cells — state exactly that boundary). Either way: do NOT re-record — the
~57-busy-hour price is named and declined by charter.

**Files in scope:**
- training/reports/report-finalist-eval.md; (the availability erratum)
- training/reports/_finalist_eval_raw/MANIFEST.md (new, only on the recovery path)

**Files NOT in scope:**
- replays/ (nothing is recorded)
- training/artifacts/ (19.22's surface)

**Definition of done:**
- [ ] One of the two outcomes is recorded with a dated erratum; on recovery, the manifest's shas cover every file, the staging ref is pushed and verifies against the manifest, and the evidence-store destination is named; on loss, the reproducibility boundary is stated exactly.
- [ ] No re-recording occurred or is scheduled.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-19-raw-slate` with a title like `task 19.21: the finalist raw slate: recover or label (owner)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 22 [C; VERIFIED §8 row 11]; training/reports/report-finalist-eval.md:115-118 ("the raw recordings … live outside the repo tree") + :1066-1070 (`~/ailibi-campaign-1826/scoring/…`); `git ls-files training/reports/_finalist_eval_raw` → empty; the 19.22 artifact classes (the store that would receive a recovered slate)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
