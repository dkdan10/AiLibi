# Agent Prompt — 14.5 Author bespoke per-candidate prompt sets + A/B re-sweep

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.5 — Author bespoke per-candidate prompt sets + A/B re-sweep, anchored to tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/qwen3_5_9b/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-30 (bespoke per-candidate sets, same-schema invariant). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-new-model-prompts`
**Depends on:** 14.2, 14.4, 14.4.1
**Section refs:** tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/qwen3_5_9b/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-30 (bespoke per-candidate sets, same-schema invariant)
**Complexity:** Integration

Author a NEW, independent BESPOKE prompt set for EACH candidate (model, mode) under its own
`agents/strategic/prompts/<set>/` directory — built from the ground up (simpler "game instructions + role +
memory → deduction + interesting sim"), NOT derived from the 9B templates, so each model is prompted to its
own strengths rather than inheriting the v8/v9 scaffolding rebuilt to fight the 9B's attention drift. The
candidate sets are `qwen3_32b` (non-thinking), `qwen3_32b_thinking`, `qwen3_30b_a3b`, `glm_4_32b`, and
`cydonia_24b` (owner decision 2026-06-30; bespoke now, to learn each model's ceiling before sharing structure
later). The ONE hard invariant is the output JSON schema: every set's turns must emit the SAME
`MeetingTurn` / `VoteBallot` shape so all sets parse identically and the graders / recording seam are
unchanged. Register each set's versions and re-run the 14.4 sweep over the SAME reconstructed contexts to A/B
each new set vs the pinned-9B prompts ON its own model (the one clean control in a co-designed change),
recording the delta. Where 14.4 showed the cover directive is a binding lever, wire it into the reply path of
the new set(s) (not gated off the body-report opening as it is today). The non-Qwen sets require the 14.4.1
adapter fix so they iterate against the real client, not the harness bare-send.

**Files in scope:**
- agents/strategic/prompts/qwen3_32b/ (new bespoke set: the 4 templates — crewmate_report, impostor_report, accusation_round [cover directive wired into the reply path if 14.4 showed it binding], vote_ballot — same output schema)
- agents/strategic/prompts/qwen3_32b_thinking/ (new bespoke set for the thinking variant; may share most templates with `qwen3_32b`, author only what genuinely differs)
- agents/strategic/prompts/qwen3_30b_a3b/ (new bespoke set)
- agents/strategic/prompts/glm_4_32b/ (new bespoke set; requires the 14.4.1 adapter fix to run on the real client)
- agents/strategic/prompts/cydonia_24b/ (new bespoke set; requires the 14.4.1 adapter fix)
- orchestrator/game.py (register each new set in the per-set prompt-version registry; preserve the merged 13.5 flag wiring)
- experiments/lab/report-featherless-sweep.md (append the per-set new-vs-pinned-9B A/B delta on each set's own model)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_5_9b/ (the pinned 9B set is frozen — never edited)
- agents/strategic/prompts/loader.py (the selector seam landed in 14.2; this only adds set directories)
- replays/samples/ (re-record is 14.7)
- llm/ (the provider adapter is 14.1; the `enable_thinking` conditional is 14.4.1)
- per-agent model/set routing for heterogeneous-model games (structural; deferred to Phase 15 — these sets are the enabler, but 14.5 authors + validates them HOMOGENEOUSLY)

**Definition of done:**
- [ ] A bespoke prompt set is authored for EACH candidate (`qwen3_32b`, `qwen3_32b_thinking`, `qwen3_30b_a3b`, `glm_4_32b`, `cydonia_24b`) under its own `agents/strategic/prompts/<set>/`, built from the ground up (not copied from the 9B set), registered in the per-set version registry and selectable via `AILIBI_PROMPT_SET`.
- [ ] Every set's turns emit the SAME output JSON schema (`MeetingTurn` / `VoteBallot`) so all sets parse identically — a cross-set parse check over a reconstructed context confirms it; the output contract is the one hard invariant.
- [ ] A re-sweep over the SAME reconstructed contexts records each set's delta vs the pinned-9B prompts ON its own model (mechanical metrics + parse-success); the pinned `qwen3_5_9b` set is unchanged.
- [ ] Where 14.4 showed the cover directive is a binding lever, it is wired into the new set's reply path (not gated off the body-report opening); otherwise the report records why it was not.
- [ ] Every new set renders under `StrictUndefined` with the existing loader kwargs (no template kwarg drift); a render smoke test over a reconstructed context passes for each.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

This is where the owner's "simple instructions, generate deduction + interesting sim" intent lands, per
candidate. For each set, start from the OUTPUT contract (the shared `MeetingTurn` / `VoteBallot` schema and the
loader kwargs the templates may reference — `agent_id`, `rendered_memory`, `transcript`, `contradictions`,
`prior_turn`, `turn_kind`, `living_ids`, `dead_ids`, `is_impostor`, `is_body_report`) and write the
natural-language instruction body FRESH for that model — do NOT port the 9B's stacked-imperative guard-rails.
The JSON contract is FROZEN (only the instruction prose changes), which is what keeps `model_validate_json` and
the recording seam working across every set and is the precondition for later heterogeneous play. The
`qwen3_32b_thinking` set will usually differ from `qwen3_32b` in only a template or two (a thinking model needs
less step-by-step coaxing) — author only what differs, but keep it a self-contained directory. Re-use the
14.3/14.4 harness to A/B: render each set over the same `contexts.pkl` and grade with the identical `_grade`.
GLM / Cydonia need the 14.4.1 adapter fix to iterate against the real client rather than the sweep's
bare-send.

## Integration risk

The new prompts co-vary with the model by design (owner decision), so the 9B comparison is a REFERENCE point,
not a controlled ablation — say so in the report and do not over-claim causality. Authoring 5 bespoke sets
multiplies the schema-drift surface: each set is an independent output surface, and a single set drifting the
emitted JSON shape breaks `model_validate_json`, its own recording, AND the same-schema invariant that later
heterogeneous play depends on. Validate every new template renders under `StrictUndefined` with the exact
loader kwargs AND parses to the shared schema before the re-sweep, or the sweep aborts on an `UndefinedError` /
`ValidationError` rather than a behavior signal.

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
Open a PR from branch `phase-14-new-model-prompts` with a title like `task 14.5: author bespoke per-candidate prompt sets + a/b re-sweep`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/qwen3_5_9b/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-30 (bespoke per-candidate sets, same-schema invariant)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
