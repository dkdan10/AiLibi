# Agent Prompt — 4.6 ThoughtStream

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.6 — ThoughtStream, anchored to DESIGN.md §6, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-thoughtstream`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §6, DESIGN.md §7
**Complexity:** Medium

Per-agent memory + LLM call viewer for one selected agent. Spectator
selects an agent; sees that agent's `render_for_prompt`-style view +
the LLM call records (prompt + response + cost) attached to that
agent during meetings.

**Files in scope:**
- frontend/src/components/ThoughtStream.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] ThoughtStream displays the selected agent's memory view (role, tasks-completed, salience-ordered observations, beliefs, contradictions) as exposed by the spectator API.
- [ ] LLM call records for the agent: prompt template id, model id, input/output tokens, cost in USD, prompt + response text (truncated with expand-on-click for long responses).
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Component renders prompt versions and cost metadata when present.
- [ ] Frontend build/check command passes.

## Implementation hint

See DESIGN.md §6.6. Per-agent memory + belief view. The agent's role is in this view per the firewall design — the spectator API exposes it because the spectator is privileged (post-game replay). For live-game spectator (deferred), role would be redacted.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-4-thoughtstream` with a title like `task 4.6: thoughtstream`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §6, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
