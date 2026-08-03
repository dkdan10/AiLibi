# Agent Prompt — 3.2 Shared meeting/output schemas and `BodyView.victim_id` boundary

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.2 — Shared meeting/output schemas and `BodyView.victim_id` boundary, anchored to DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md §1.3, DESIGN.md Appendix A. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-output-schemas`
**Depends on:** 3.1 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md §1.3, DESIGN.md Appendix A
**Complexity:** Medium

Two bundled deliverables that share schema-discipline work:

1. **Meeting / output schemas.** Centralize meeting artifacts in
   `meetings/schemas.py`. Agent strategic schemas may re-export or wrap
   the shared schemas, but must not duplicate independent schema
   definitions.
2. **R-4 retirement: `BodyView.victim_id` typed field.** Replace the
   `_BODY_ID_VICTIM_PATTERN` regex coupling in
   `agents/tactical/impostor_policy.py` (introduced by Task 2.10 as a
   Phase-2 inference bridge) with a typed `victim_id: PlayerId` field
   on `observation/packet.py::BodyView`. The packet builder populates
   `victim_id` directly from `BodyState.player_id`; perception surfaces
   `victim_id` in `saw_body` event payloads; the impostor policy reads
   the field instead of regex-parsing the body id. The body's victim
   id was already inferrable from the existing `body_id` format
   (`body-{victim_id}-{tick}` per `engine/rules.py:69`), so exposing it
   directly does not weaken the firewall — it formalizes what was
   already public and removes the agent→engine string coupling flagged
   as R-4 in `audits/audit-2026-05-16-0036-reconciled.md`.

The two deliverables are bundled because both are pure
schema-discipline work and both touch the boundary layer. The
meeting-schemas work alone would be Small; folding in R-4 retirement
makes the task Medium.

**Files in scope:**
- meetings/schemas.py
- agents/strategic/output_schemas.py
- observation/packet.py
- observation/service.py
- agents/perception.py
- agents/tactical/impostor_policy.py
- eval/leak_test.py
- tests/meetings/test_schemas.py
- tests/observation/test_service.py
- tests/observation/test_boundary_contracts.py
- tests/agents/test_perception.py
- tests/agents/test_impostor_policy.py

**Files NOT in scope:**
- engine/
- orchestrator/
- agents/tactical/crewmate_policy.py
- agents/tactical/pathing.py
- agents/runtime.py
- agents/base.py
- agents/memory/
- llm/
- api/
- frontend/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/test_crewmate_policy.py
- tests/agents/test_memory.py
- tests/agents/test_pathing.py
- tests/agents/test_runtime.py
- tests/engine/
- tests/eval/
- tests/orchestrator/
- tests/test_firewall.py

**Definition of done:**
- [ ] **Meeting / output schemas:** `ReportDocument`, `Statement`, `VoteBallot`, `MeetingResult`, and contradiction/result DTOs in `meetings/schemas.py` match DESIGN.md §5.3 and §5.5. `agents/strategic/output_schemas.py` re-exports or wraps shared meeting schemas without duplicating them. Schemas are suitable for structured LLM output. Relevant schema tests in `tests/meetings/test_schemas.py` pass.
- [ ] **R-4 — `BodyView.victim_id` field added.** `observation/packet.py::BodyView` gains a `victim_id: PlayerId` field. The Pydantic model validates the field as a non-empty string matching the canonical `p-N` id form (or whatever shape `PlayerId` is typed as).
- [ ] **R-4 — packet builder populates `victim_id`.** `observation/service.py` populates `BodyView.victim_id` from `BodyState.player_id` (the engine-side hidden field) when constructing every `BodyView` for every packet. This is a read of engine state inside the privileged ObservationService — no firewall violation, since ObservationService is the single privileged consumer per DESIGN.md §1.3.
- [ ] **R-4 — perception surfaces `victim_id`.** `agents/perception.py` constructs `saw_body` `EpisodicEvent` payloads with a `victim_id` key whose value is taken from `BodyView.victim_id`. The existing `body_id` payload field remains (it stays the canonical body identifier for deduplication / replay reference); `victim_id` is the authoritative source for downstream agent code that needs the body's player id.
- [ ] **R-4 — impostor policy reads `victim_id`, regex retired.** `agents/tactical/impostor_policy.py::_confirmed_dead_from_bodies` reads `victim_id` directly from each `saw_body` event payload. The `_BODY_ID_VICTIM_PATTERN` regex constant (`agents/tactical/impostor_policy.py:88-94`) is deleted entirely along with the regex import line if it becomes unused. The `ValueError` guard becomes: raise if `victim_id` is missing or not a string (mirroring the previous body-id missing-payload guard).
- [ ] **R-3 test (Task 2.13) updated for `victim_id`.** `tests/agents/test_impostor_policy.py::test_confirmed_dead_from_bodies_raises_on_missing_body_id` is renamed to `test_confirmed_dead_from_bodies_raises_on_missing_victim_id` (or equivalent) and updated to construct a `saw_body` payload missing `victim_id` (rather than `body_id`). The test continues to assert `ValueError`. Existing stale-target tests in `TestImpostorStaleAndDeadTargetPruning` continue to pass against the new `victim_id`-based implementation; verify with `uv run pytest tests/agents/test_impostor_policy.py -v -k "Stale or Dead or victim_id"`.
- [ ] **R-4 — boundary contract tests cover `victim_id`.** `tests/observation/test_service.py` and `tests/observation/test_boundary_contracts.py` gain assertions that `BodyView.victim_id` is populated on every `BodyView` and matches the originating `BodyState.player_id`. Add at least one negative pin: a `BodyView` constructed without `victim_id` should fail Pydantic validation.
- [ ] **R-4 — perception tests cover `victim_id` surfacing.** `tests/agents/test_perception.py` gains an assertion that `saw_body` events carry `victim_id` in their payload and that the value matches the originating `BodyView.victim_id`.
- [ ] **R-4 — leak scanner remains green.** Re-run `uv run pytest eval/leak_test.py` and confirm no new packet field trips a leak guard. The player id `p-N` does not contain `impostor` / `crewmate` / `crew` substrings; the field name `victim_id` is not in the hidden-keys list. If the recursive field-name scanner has an explicit allow/deny list that requires updating to account for the new field, make the edit in `eval/leak_test.py` and document the change in `## Decisions`. Run a full 10-game tournament leak scan as well: `uv run python scripts/run_tournament.py --num-games 10 --start-seed 0 --output-dir /tmp/task-3-2-leak --max-ticks 1000` and confirm the per-game audit logs pass the scanner.
- [ ] No imports from `engine/` under `agents/` (firewall preserved).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

See DESIGN.md §5.3 + §5.5 for the meeting-schemas surface. `meetings/schemas.py` owns the canonical Pydantic shapes for `ReportDocument`, `Statement`, `VoteBallot`, and `MeetingResult`. `agents/strategic/output_schemas.py` re-exports or wraps these — never duplicate.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-3-output-schemas` with a title like `task 3.2: shared meeting/output schemas and `bodyview.victim_id` boundary`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md §1.3, DESIGN.md Appendix A), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
