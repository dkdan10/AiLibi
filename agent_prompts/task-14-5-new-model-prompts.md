# Agent Prompt — 14.5 Author redesigned per-model prompt set + A/B re-sweep

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.5 — Author redesigned per-model prompt set + A/B re-sweep, anchored to tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-25 (simple instructions + role + memory). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-new-model-prompts`
**Depends on:** 14.2, 14.4
**Section refs:** tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-25 (simple instructions + role + memory)
**Complexity:** Integration

Author a NEW, independent prompt set for the chosen model under its own `agents/strategic/prompts/<set>/`
directory — simpler "game instructions + role + memory → deduction + interesting sim" prompts with lighter
guard-rails than the 9B needed (the v8/v9 templates were rebuilt to fight the 9B's attention drift; a stronger
model should need less). Register the new set's versions and re-run the 14.4 sweep over the SAME reconstructed
contexts to A/B the new prompts vs the pinned-9B prompts ON the new model, recording the delta. If 14.4 showed
the cover directive is the binding lever, wire it into the reply path of the new set (not gated off the
body-report opening as it is today).

**Files in scope:**
- agents/strategic/prompts/<chosen_set>/crewmate_report.j2 (new)
- agents/strategic/prompts/<chosen_set>/impostor_report.j2 (new)
- agents/strategic/prompts/<chosen_set>/accusation_round.j2 (new; cover directive wired into the reply path if 14.4 showed it binding)
- agents/strategic/prompts/<chosen_set>/vote_ballot.j2 (new)
- orchestrator/game.py (register the new set in the per-set `DEFAULT_PROMPT_VERSIONS` registry)
- experiments/lab/report-featherless-sweep.md (append the new-prompts-vs-pinned A/B delta on the chosen model)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_5_9b/ (the pinned 9B set is frozen — never edited)
- agents/strategic/prompts/loader.py (the selector seam landed in 14.2; this only adds a set directory)
- replays/samples/ (re-record is 14.7)
- llm/ (provider work is 14.1)

**Definition of done:**
- [ ] A new prompt set for the chosen model is authored under `agents/strategic/prompts/<set>/` with lighter guard-rails than the 9B set, registered in the per-set version registry and selectable via `AILIBI_PROMPT_SET`.
- [ ] A re-sweep over the SAME reconstructed contexts records the new prompts' delta vs the pinned-9B prompts ON the new model (mechanical metrics + parse-success); the pinned `qwen3_5_9b` set is unchanged.
- [ ] If 14.4 showed the cover directive is the binding lever, it is wired into the new set's reply path (not gated off the body-report opening); otherwise the report records why it was not.
- [ ] The new set renders under `StrictUndefined` with the existing loader kwargs (no template kwarg drift); a render smoke test over a reconstructed context passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

This is where the owner's "simple instructions, generate deduction + interesting sim" intent lands. Start from
the structural skeleton of the 9B templates (same MeetingTurn / VoteBallot output contract, same kwargs the
loader passes — `agent_id`, `rendered_memory`, `transcript`, `contradictions`, `prior_turn`, `turn_kind`,
`living_ids`, `dead_ids`, `is_impostor`, `is_body_report`) but strip the stacked-imperative guard-rails the 9B
needed. The output JSON contract is FROZEN (the schema is shared) — only the natural-language instruction body
changes. Re-use the 14.3/14.4 harness to A/B: render the new set over the same `contexts.pkl` and grade with
the identical `_grade`. Keep the new set self-contained so a future model gets its own sibling directory.

## Integration risk

The new prompts co-vary with the model by design (owner decision), so the 9B comparison is a REFERENCE point,
not a controlled ablation — say so in the report and do not over-claim causality. The output schema must not
drift: a reworded prompt that changes the emitted JSON shape breaks `model_validate_json` and the recording
seam. Validate every new template renders under `StrictUndefined` with the exact loader kwargs before the
re-sweep, or the sweep aborts on an `UndefinedError` rather than a behavior signal.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Open a PR from branch `phase-14-new-model-prompts` with a title like `task 14.5: author redesigned per-model prompt set + a/b re-sweep`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-25 (simple instructions + role + memory)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
