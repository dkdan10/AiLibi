# Agent Prompt — 14.6 Lock the baseline tuple (model + prompt set + thinking policy)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.6 — Lock the baseline tuple (model + prompt set + thinking policy), anchored to tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md; audits/audit-2026-06-25-0859-phase-13-close.md; agent_prompts/task-9-5-model-migration-rerecord.md (the pause-and-decide shape). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-lock-decision`
**Depends on:** 14.5
**Section refs:** tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md; audits/audit-2026-06-25-0859-phase-13-close.md; agent_prompts/task-9-5-model-migration-rerecord.md (the pause-and-decide shape)
**Complexity:** Small

Design-thread decision (no code): read the 14.4/14.5 sweep evidence and lock the baseline tuple before any
re-record exists — the chosen meeting_model + trigger_model Featherless ids, the chosen prompt set (ONE of the
14.5 bespoke sets; the baseline stays HOMOGENEOUS — the other bespoke sets remain available but unrecorded,
for the Phase-15 heterogeneous-games task they enable), the recorded-baseline thinking policy (`fail_loud` unless the owner signs off on `strip`), the
`response_format_mode` (`json_object` default per the 14.1 live finding 2026-06-27 — strict `json_schema` is
rejected by the slate; `json_schema` stays selectable), the substrate-flag
config for the re-record (all 4 13.5 flags ON per owner decision 2026-06-26; 14.8's per-lever ablation
characterizes each, non-gating), and a go/no-go for the re-record. Mirror the Phase-9 pause between 9.4
(client) and 9.5 (re-record): the decision is re-answered
against the sweep's data, and a NO-GO is an allowed outcome (no candidate clears the structured-output /
behavior bar → stay on 9B / escalate the information ceiling), since the merge criterion is a VALID baseline,
not an improved one.

**LOCKED DECISION (owner, 2026-06-30) — GO:**
- **meeting_model = trigger_model = `Qwen/Qwen3-32B`** (homogeneous; qwen3_32b used for EVERYTHING — both call kinds).
- **prompt set = `qwen3_32b`** (the Task 14.5 bespoke set; registered `…​.qwen3_32b.v2`, selectable via `AILIBI_PROMPT_SET=qwen3_32b`).
- **mode = `non_thinking`** (the request-time thinking toggle OFF).
- **thinking policy = `fail_loud`** (non-thinking baseline expects NO reasoning channel; a populated one is an auditable error, not silently stripped).
- **response_format_mode = `json_object`** (the 14.1 live finding: strict `json_schema` 400s on the slate; `json_schema` stays selectable, no silent fallback).
- **substrate flags = all 4 13.5 levers ON** (`AILIBI_TESTIMONY_AS_CONTENT` / `AILIBI_WITNESSED_KILL_EVIDENCE` / `AILIBI_MOVEMENT_PERCEPTION` / `AILIBI_UNFREEZE_MEMORY`); 14.8's per-lever ablation is characterization (non-gating).
- **Evidence:** Qwen3-32B non-thinking on the qwen3_32b set is validity-clean — reply parse-success 16/16 (100%) on both substrates, vote conversion 8/8, ~27.1s/turn isolated (vs ~226.1s thinking, an ~8× time cost over a 50-seed × 2-format run). The mechanical self-co tell is mixed vs the pinned-9B prompts (an information-ceiling artifact, NOT a model gap — 14.4/14.8), so the recorded baseline is chosen on VALIDITY + latency, which non-thinking wins; the tell is scoped to Phase 15. The other four bespoke sets (incl. the strong-tell-reduction thinking set and GLM at 100% parse) stay available but unrecorded, for the Phase-15 heterogeneous-games task. NO validity NO-GO — proceed to the 14.7 smoke.

**Files in scope:**
- tasks/phase-14.md (record the locked decision: chosen meeting_model, trigger_model, prompt set, thinking policy, response_format_mode (json_object), substrate-flag config (all 4 ON), and the re-record go/no-go with its evidence)

**Files NOT in scope:**
- llm/ + agents/ + replays/ (no implementation; this is a recorded decision)
- experiments/ (the sweep is done; this reads its report)
- agent_prompts/ (the 14.7 prompt is regenerated mechanically by `generate_prompts.py`, not hand-edited here)

**Definition of done:**
- [ ] The locked (meeting_model, trigger_model) Featherless ids are recorded in `tasks/phase-14.md` with their evidence from the sweep report.
- [ ] The chosen prompt set and the recorded-baseline thinking policy (`fail_loud` unless the owner signs off on `strip`) are recorded with rationale.
- [ ] The locked baseline is HOMOGENEOUS — ONE (meeting_model, trigger_model, prompt set, mode); the other 14.5 bespoke sets remain available but are NOT recorded (heterogeneous-model play is a Phase-15 task enabled by them).
- [ ] The `response_format_mode` is recorded = `json_object` (the 14.1 live finding 2026-06-27: strict `json_schema` 400s on the slate), with `json_schema` noted as selectable for a future endpoint and no silent fallback between modes.
- [ ] The re-record substrate-flag config is recorded = all 4 13.5 flags ON (owner decision 2026-06-26), with 14.8's per-lever ablation noted as characterization (non-gating).
- [ ] A re-record go/no-go is recorded, explicitly allowing a NO-GO ("no candidate clears the structured-output / behavior bar; stay on 9B / escalate the information ceiling").
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Open a PR from branch `phase-14-lock-decision` with a title like `task 14.6: lock the baseline tuple (model + prompt set + thinking policy)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md; audits/audit-2026-06-25-0859-phase-13-close.md; agent_prompts/task-9-5-model-migration-rerecord.md (the pause-and-decide shape)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
