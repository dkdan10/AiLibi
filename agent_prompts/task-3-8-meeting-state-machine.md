# Agent Prompt — 3.8 Meeting state machine

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.8 — Meeting state machine, anchored to DESIGN.md §5.1, DESIGN.md §5.2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-meeting-state-machine`
**Depends on:** 3.3 merged, 3.4 merged, 3.5 merged, 3.6 merged, 3.7 merged
**Section refs:** DESIGN.md §5.1, DESIGN.md §5.2
**Complexity:** Medium

`meetings/manager.py` and `meetings/transcript.py` per §5.1 + §5.2. The
state machine moves through report intake → accusation rounds → voting →
resolution, consuming the four prompt templates landed in Tasks 3.4–3.7
and returning a structured `MeetingResult` for the orchestrator (3.12)
to apply.

**C-3 directive from
`audits/audit-2026-05-16-0611-claude.md`:** the post-3.3 audit
identified that `MeetingTranscript` (`meetings/schemas.py:217-225`) is
`tuple[ReportDocument, ...]` + `tuple[Statement, ...]` with no
guaranteed statement ordering, no `round_max` invariant, and no test
exercising a multi-round transcript end-to-end. Without resolution
here, every downstream consumer (3.9 strategic reasoner, 3.10 voting,
3.11 contradiction detection) would have to invent its own sort
convention, risking drift. Task 3.8 must close this. Pick one of two
options (see DoD + Implementation hint) and document the choice in the
PR's `## Decisions` block.

**Files in scope:**
- meetings/manager.py
- meetings/transcript.py
- tests/meetings/test_manager.py
- tests/meetings/test_transcript.py
- meetings/schemas.py
- tests/meetings/test_schemas.py

**Files NOT in scope:**
- engine/ core rule changes
- orchestrator/
- agents/tactical/
- agents/strategic/
- agents/memory/
- agents/perception.py
- agents/runtime.py
- agents/base.py
- observation/
- llm/
- api/
- frontend/
- eval/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/llm/
- tests/agents/
- tests/observation/
- tests/orchestrator/
- tests/engine/
- tests/eval/
- tests/_helpers/
- tests/fixtures/
- tests/test_firewall.py

**Definition of done:**
- [ ] **`MeetingManager` follows trigger lifecycle in DESIGN.md §5.1.** Construction takes the LLM client, the four prompt callables (Tasks 3.4–3.7's deliverables), and a deadline configuration. It does not start until a meeting trigger fires; once triggered it runs to resolution.
- [ ] **Protocol implements report intake, accusation rounds, voting, and resolution per DESIGN.md §5.2.** Each phase consumes the appropriate prompt template; the state machine wires them together.
- [ ] **Missed deadlines yield default no-statement / no-vote behavior** as specified in §5.2. The default action is recorded in the transcript so the audit trail is complete.
- [ ] **Manager returns `MeetingResult`; it does not mutate engine state.** The orchestrator (3.12) applies the result. `MeetingManager` does not import from `engine/`; `lint-imports` must pass.
- [ ] **C-3 — statement ordering contract resolved.** Pick exactly one option and implement it:
  - **Option (a) — recommended: producer-guaranteed canonical order.** `MeetingManager` emits `Statement` instances into the transcript in canonical order: ascending `round_index`, then ascending insertion order within a round (stable). The contract is documented as a docstring on `MeetingManager.run` (or wherever the state machine produces the transcript) stating: *"Consumers may read `transcript.statements` in tuple order and trust that statements are sorted by `(round_index, insertion_order)` without re-sorting."* No schema change required.
  - **Option (b) — alternative: schemas add `round_max` + consumer sort discipline.** `meetings/schemas.py::MeetingTranscript` gains a `round_max: int = Field(ge=1)` field constraining the configured number of rounds, with a validator that no `Statement.round_index >= round_max`. Every consumer of the transcript is responsible for sorting. The contract is documented on the schema.
- [ ] **C-3 — statement-ordering pin test.** `tests/meetings/test_manager.py` (or `test_transcript.py`, depending on where the contract lives) gains a regression that drives `MeetingManager` through at least two accusation rounds with multiple participants, captures the resulting `MeetingTranscript`, and asserts either (a) `statements` is already sorted by `(round_index, insertion_order)` if option (a) was picked, OR (b) the `round_max` invariant rejects an out-of-range `round_index` if option (b) was picked. The test must fail against an implementation that allows ambiguous ordering.
- [ ] **Relevant meeting tests pass using fake strategic participants.** Use the existing `llm/fake_provider.py` plus shim participants — no real Anthropic calls.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy --strict meetings agents llm` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

See DESIGN.md §5.1 + §5.2. `MeetingManager` is a state machine that moves through report intake → accusation rounds → voting → resolution. It must NOT mutate engine state; it returns a `MeetingResult` that the orchestrator (3.12) applies.

The four prompt templates from Tasks 3.4–3.7 are already wired through `meetings/schemas.py` types. The state machine's job is sequencing — it does not re-implement the prompt logic.

## Public types this task introduces
- `meetings.manager.MeetingManager`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-3-meeting-state-machine` with a title like `task 3.8: meeting state machine`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.1, DESIGN.md §5.2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
