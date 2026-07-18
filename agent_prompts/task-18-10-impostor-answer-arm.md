# Agent Prompt — 18.10 The impostor-answer template arm (variant, default untouched)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.10 — The impostor-answer template arm (variant, default untouched), anchored to audits/audit-phase-18-planning.md §3.4 (the structural refusal: hard-coded empty observations); agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:8-12, 29-36, 76, 109-110 (the ladder history + the ≥44% self-flag caution) + accusation_round.j2:179, 198-200; agents/strategic/prompts/loader.py:155-157, 481-483 (role-selected routing); audits/audit-phase-17-absence-gate.md Ruling 3(d) (template changes re-read the bar on new bytes). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-impostor-answer-arm`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.4 (the structural refusal: hard-coded empty observations); agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:8-12, 29-36, 76, 109-110 (the ladder history + the ≥44% self-flag caution) + accusation_round.j2:179, 198-200; agents/strategic/prompts/loader.py:155-157, 481-483 (role-selected routing); audits/audit-phase-17-absence-gate.md Ruling 3(d) (template changes re-read the bar on new bytes)
**Complexity:** Medium

The gate's highest-variance arm, built inert: a flag-selected impostor template variant in
which the impostor opening and reply ANSWER the whereabouts ask with a structured
self-placement (which the two-tier design lets be a lie — the tactical record is what it
is; the claim is the LLM's), instead of the hard-coded `"observations": []`. The cover
instruction ("every location detail you mention must be about OTHER players") is replaced in
the variant with plausible-self-account guidance. Default routing untouched — the variant
is reachable only through the flag, and the standing prompt-registry versioning applies.
This arm exists so the 18.11 probe can MEASURE what the ladder only feared: the impostor
self-flag rate and win cost when impostors must account for themselves.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (the variant templates)
- agents/strategic/prompts/loader.py (the flag-selected variant routing + resolver)
- orchestrator/game.py; (the `prompt_versions_for_set` registry entries for the variant ONLY — recorded `prompt_versions` come from this registry, not the loader, so without this the variant renders different bytes while recordings still stamp the old versions)
- tests/agents/; (routing fixtures: default path renders byte-identically; variant path renders the self-placement contract; version stamps distinguish the variant in the registry AND the recorded bytes)

**Files NOT in scope:**
- meetings/ (18.8/18.9's regions)
- eval/funnel.py (its refusal-artifact note updates only at an adopting record)

**Definition of done:**
- [ ] With the flag OFF the rendered prompt set is byte-identical to the committed registry (pinned across the fixture sweep); ON, impostor opening and reply render the structured whereabouts self-placement ask and the variant's prompt-version stamp appears in recorded bytes.
- [ ] The variant's design rationale and the ladder's ≥44% self-flag caution are quoted in the template header (the house convention), naming the 18.11 bars that will judge it.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The variant must keep the teammate firewall intact — a self-placement never places or
implicates the co-impostor (the §7.12 input-side guard). Follow the registry's version-bump
conventions so validity-gate provenance can tell variant bytes from default bytes.

## Public types this task introduces
- `agents.strategic.prompts.loader.impostor_roll_call_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-18-impostor-answer-arm` with a title like `task 18.10: the impostor-answer template arm (variant, default untouched)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §3.4 (the structural refusal: hard-coded empty observations); agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:8-12, 29-36, 76, 109-110 (the ladder history + the ≥44% self-flag caution) + accusation_round.j2:179, 198-200; agents/strategic/prompts/loader.py:155-157, 481-483 (role-selected routing); audits/audit-phase-17-absence-gate.md Ruling 3(d) (template changes re-read the bar on new bytes)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
