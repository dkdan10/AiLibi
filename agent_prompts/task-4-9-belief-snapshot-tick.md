# Agent Prompt — 4.9 BeliefEntryView snapshot_tick rename (R-2 substrate)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.9 — BeliefEntryView snapshot_tick rename (R-2 substrate), anchored to DESIGN.md §6.3, mid-phase DTO audit R-2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-belief-snapshot-tick`
**Depends on:** 4.4 merged + mid-phase DTO audit passed + **4.7 merged** (shared edits to `api/schemas.py`, `api/replay_loader.py`, TS types, and DTO test fixtures — serialize to avoid merge churn)
**Section refs:** DESIGN.md §6.3, mid-phase DTO audit R-2
**Complexity:** Small

Mid-phase DTO audit R-2 informational finding (Unique-but-verified):
`api.schemas.BeliefEntryView.last_updated_tick` is the enclosing
meeting boundary tick, not a per-belief mutation timestamp. Every
row in a snapshot carries the same value, which will mislead
`BeliefMatrix` (4.10) if its component reads `last_updated_tick`
as a recency signal. The audit reconciler explicitly framed this as
"before Task 4.10 dispatch" — this task is the prereq.

**Why a rename, not a real recency wire.** Two options were on the
table:

1. **Rename `last_updated_tick` → `snapshot_tick`.** Cheap, honest,
   one PR. Documents the field's actual semantics (the tick at
   which the spectator API took the snapshot). Does NOT change
   `agents.memory.beliefs.PlayerBelief` — beliefs remain immutable
   snapshots that don't carry per-mutation timestamps.

2. **Wire a real per-belief recency** through `PlayerBelief`.
   Requires adding `last_updated_tick` to the belief store,
   threading a tick parameter through every mutation site
   (`adjust_suspicion`, `adjust_trust`, `record_alibi`,
   `record_contradiction`, `decay_suspicion`), updating all callers
   in `agents/` and `meetings/`, plus the loader propagation.
   Multi-file repair task, ~5x the surface area.

This task picks Option 1. The semantic question that motivated R-2
("a BeliefMatrix shouldn't claim per-cell recency it doesn't have")
is fully resolved by the rename — 4.10's contract notes that
`snapshot_tick` is per-meeting, not per-cell, and renders it once
in the footer ("all beliefs as of meeting tick N") rather than
per-cell. If Phase 5 decides per-belief recency adds product
value, that's a separate scoped task — not this one.

**Out of scope** (explicit decisions deferred):

- **`PlayerBelief` schema changes.** No change. The belief store
  stays timeless.
- **Belief mutation tick parameter threading.** Not done. See
  rationale above.
- **`AgentMemoryView` tick semantics.** Already clear (`tick` is
  the meeting boundary tick). No change.
- **TypeScript codegen.** Frontend types are hand-authored; this
  task hand-edits one line in `frontend/src/types/api.ts`.

**Files in scope:**
- api/schemas.py
- api/replay_loader.py
- frontend/src/types/api.ts
- tests/api/test_schemas.py
- tests/api/test_replay_loader.py
- tests/api/test_replays.py
- tests/api/fixtures/sample_replay.py

**Files NOT in scope:**
- engine/
- agents/ (PlayerBelief is NOT modified)
- llm/
- meetings/
- observation/
- orchestrator/
- frontend/src/components/
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/package.json
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- scripts/

**Definition of done:**
- [ ] **`BeliefEntryView.last_updated_tick` renamed to `snapshot_tick`.** [api/schemas.py:410](api/schemas.py#L410). Docstring updated to: "Meeting boundary tick at which this belief snapshot was taken. Beliefs themselves are timeless; this field timestamps when the spectator API observed the belief, not when the belief mutated. All BeliefEntryView entries within one AgentMemoryView share the same snapshot_tick."
- [ ] **Loader updated.** [api/replay_loader.py:1119](api/replay_loader.py#L1119) constructs `BeliefEntryView(snapshot_tick=tick, ...)` — field-name rename only; the `tick` parameter pass-through is unchanged.
- [ ] **Frontend types mirror.** [frontend/src/types/api.ts:275](frontend/src/types/api.ts#L275) renames `last_updated_tick: number` → `snapshot_tick: number`.
- [ ] **Test updates.** Every test that references `last_updated_tick` is updated. Grep `grep -rn "last_updated_tick" tests/` to find them; expect them in [tests/api/test_schemas.py](tests/api/test_schemas.py), [tests/api/test_replay_loader.py](tests/api/test_replay_loader.py), [tests/api/test_replays.py](tests/api/test_replays.py), and possibly [tests/api/fixtures/sample_replay.py](tests/api/fixtures/sample_replay.py).
- [ ] **No code outside the files-in-scope references `last_updated_tick`.** Confirm with `grep -rn "last_updated_tick" .` after edits; only `audits/` (historical) and possibly `tasks/phase-4.md` (this task's own description) should still contain the string.
- [ ] **`extra="forbid"` confirms strict rejection.** A test asserts that constructing `BeliefEntryView(last_updated_tick=5, ...)` (the OLD field name) raises a Pydantic validation error. This documents the rename.
- [ ] **DTO leak test updated if it references the field.** [tests/api/test_leak.py](tests/api/test_leak.py)'s `EXPECTED_DTOS` is field-list-agnostic per the 4.1 design — no edit expected. Confirm by running.
- [ ] **No backend semantics change.** No new endpoint; no new field elsewhere; the loader still pulls from the same per-meeting tick.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `api.schemas.BeliefEntryView.snapshot_tick` (renamed from `last_updated_tick`)`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-4-belief-snapshot-tick` with a title like `task 4.9: beliefentryview snapshot_tick rename (r-2 substrate)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §6.3, mid-phase DTO audit R-2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
