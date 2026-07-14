# Agent Prompt — 17.8 [GATE-GO ONLY] The absence adopting record (its own meeting-layer baseline)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.8 — [GATE-GO ONLY] The absence adopting record (its own meeting-layer baseline), anchored to audits/audit-phase-17-absence-gate.md (the GO ruling + whether the vent widening ships with it); tasks/phase-16.md 16.17 (the graduate-at-record runbook: resolver constant-true, registry → retired, floors re-pin, Q5 tag); audits/audit-phase-16-close.md §0.5 (the operator concurrency notes). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-absence-adopting-record`
**Depends on:** 17.7
**Section refs:** audits/audit-phase-17-absence-gate.md (the GO ruling + whether the vent widening ships with it); tasks/phase-16.md 16.17 (the graduate-at-record runbook: resolver constant-true, registry → retired, floors re-pin, Q5 tag); audits/audit-phase-16-close.md §0.5 (the operator concurrency notes)
**Complexity:** Integration

GO path only — under STAY-OFF this contract is removed by 17.7's surgery. Graduate the
absence prior exactly as 16.17 graduated its slate: `absence_prior_enabled` constant-true
with the env override removed, the registry entry moves to the retired list, and — if
the gate shipped it — the vent widening's flag flips to the always-on path at the same
record (ONE meeting-layer change: the absence package). Atomic re-record of both sample
sets (baseline 6), MANIFEST provenance exact, validity gates, byte-identical bare
reconstruction, floors re-pinned in `eval/watchability.py` under the 16.11 definition,
Q5 annotated tag (owner completes the push if the credential refuses), before/after on
16.10's instruments, close-style audit section appended to the gate memo.

**Files in scope:**
- agents/memory/beliefs.py (resolver graduation + the widening consumer if shipped)
- orchestrator/replay.py (registry → retired)
- meetings/transcript.py (the widening flag's always-on flip — only if the gate shipped it)
- replays/samples/9p2i/ + replays/samples/4p1i/ (the baseline-6 record)
- eval/watchability.py (baseline-6 floors)
- audits/audit-phase-17-absence-gate.md (the record section)
- tests/ (graduation re-pins + the byte-coupled sweep)
- .env.example (the lever block retires)

**Files NOT in scope:**
- replays/ml_corpus/ (17.9 records AFTER this — the sequencing the gate exists for)
- training/ (nothing trains until the corpus lands)

**Definition of done:**
- [ ] Both sets re-recorded at the graduated substrate and PASS `scripts/validity_gate.py --expected-model Qwen/Qwen3.6-27B --require-zero-cost`; byte-identical bare reconstruction; MANIFEST rows stamp the new flag set exactly.
- [ ] The graduated lever is unconditional (no env read survives), the registry's live-toggle set is empty again, and the prompt-byte golden is green on the new bytes.
- [ ] Baseline-6 floors pinned from the committed bytes under the 16.11 definition; the before/after instrument read (16.10's report) is committed in the audit with the absent-set shrinkage vs the gate memo's prediction quoted.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone the 16.17 graduation commit shape exactly (resolver → registry → record → floors →
audit); the only novelty is the optional widening flip, which follows the same
constant-true pattern on its flag. Preflight the golden + bare verify BEFORE any spend.

## Integration risk

This is a meeting-layer record between the gate and the corpus run — if it slips, the
corpus (17.9) waits; never let them interleave (rule 1). The 16.14/16.17 concurrency
notes apply verbatim (staggered workers, jittered backoff, attempts ≥8). The widening,
if shipped, changes the absent set the record's own instruments measure — the audit
must report the realized shrinkage against 17.5's counterfactual prediction.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-17-absence-adopting-record` with a title like `task 17.8: [gate-go only] the absence adopting record (its own meeting-layer baseline)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-17-absence-gate.md (the GO ruling + whether the vent widening ships with it); tasks/phase-16.md 16.17 (the graduate-at-record runbook: resolver constant-true, registry → retired, floors re-pin, Q5 tag); audits/audit-phase-16-close.md §0.5 (the operator concurrency notes)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
