# Agent Prompt — 1.7 ObservationService

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-1.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 1.7 — ObservationService, anchored to DESIGN.md §1.3, DESIGN.md §4.2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-observation-service`
**Depends on:** 1.6 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §4.2
**Complexity:** Medium

observation/service.py and ObservationPacket schema per §1.3 + §4.2. Audit log to disk.

**Files in scope:**
- observation/service.py
- observation/packet.py
- observation/audit.py

**Files NOT in scope:**
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] ObservationPacket schema matches DESIGN.md §4.2.
- [ ] ObservationService is the only boundary crossing from engine truth to agent observations.
- [ ] Audit log records every packet.
- [ ] Relevant observation tests pass.
- [ ] mypy --strict passes on observation/.
- [ ] ruff check . passes.

## Implementation hint

See DESIGN.md §1.3 + §4.2. `ObservationService` is the only boundary-crossing object. Input: `(WorldState, agent_id, engine_events)`. Output: `ObservationPacket`. Strip every hidden field; the leak test (`eval/leak_test.py`) is the contract. Audit every packet to disk via `ObservationAuditLog`.

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
Open a PR from branch `phase-1-observation-service` with a title like `task 1.7: observationservice`.
The PR description must reference DESIGN.md §1.3, DESIGN.md §4.2, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
