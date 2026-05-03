# Codex Prompt — 3.12 Meeting/orchestrator integration

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section in tasks/phase-3.md.

1. Role and context
You are a Codex implementation agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, CODEX_IMPLEMENTATION.md is the build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 3.12 — Meeting/orchestrator integration, anchored to DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-meeting-orchestrator-integration`
**Depends on:** 3.11 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4

Apply `MeetingResult` through the orchestrator, resume gameplay, and record
meeting artifacts in replay/eval records.

**Files in scope:**
- orchestrator/game.py
- orchestrator/replay.py
- tests/orchestrator/test_meeting_integration.py
- tests/orchestrator/test_replay_meetings.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Orchestrator applies `MeetingResult` ejection/skip outcomes to engine-owned world state.
- [ ] Gameplay resumes after meetings with tick/cooldown behavior matching DESIGN.md §3.1 and §5.1.
- [ ] Replay records meeting transcripts, ballots, contradiction flags, prompt versions, and LLM cost metadata.
- [ ] Engine remains pure; MeetingManager does not mutate engine state directly.
- [ ] Relevant integration tests pass with fake LLM outputs.
- [ ] `uv run mypy --strict engine observation agents meetings orchestrator llm` passes.
- [ ] `uv run ruff check .` passes.

4. Pre-flight checklist
- Read AGENTS.md, DESIGN.md, CODEX_IMPLEMENTATION.md, and the task section before editing.
- Inspect the current implementation before editing.
- Confirm the dependency listed in the task contract is present in the current branch.
- Identify the existing local patterns for the files in scope and follow them.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify CODEX_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.
If something is ambiguous, stop and add a Questions section in the PR description rather than guessing.

6. Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

7. Output expectation
Open a PR from branch `phase-3-meeting-orchestrator-integration` with a title like `task 3.12: meeting/orchestrator integration`.
The PR description must reference DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
