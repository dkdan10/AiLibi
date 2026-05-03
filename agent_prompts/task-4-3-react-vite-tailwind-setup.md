# Agent Prompt — 4.3 React + Vite + Tailwind setup

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.3 — React + Vite + Tailwind setup, anchored to DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-react-vite-tailwind-setup`
**Depends on:** 4.2 merged
**Section refs:** DESIGN.md §7
**Complexity:** Small

frontend/ skeleton, type-safe API client, and shared store interface. Use npm
with package-lock.json unless a frontend package manager has already been
chosen in the repo before this task starts.

**Files in scope:**
- frontend/package.json
- frontend/package-lock.json
- frontend/vite.config.ts
- frontend/tailwind.config.js
- frontend/postcss.config.js
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/store/index.ts
- scripts/setup_env.sh
- scripts/check.sh

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/ beyond API client contract needs
- .github/workflows/ci.yml
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] React, Vite, and Tailwind frontend skeleton exists.
- [ ] Type-safe API client exists for the sanitized API DTOs from 4.1.
- [ ] Shared store interface is defined before component fan-out.
- [ ] Frontend package manager is npm with `package-lock.json`, unless an existing repo choice requires otherwise.
- [ ] scripts/setup_env.sh installs frontend dependencies once frontend/package.json exists, without changing Python setup behavior.
- [ ] scripts/check.sh runs the configured frontend build/check command, without changing Python check behavior.
- [ ] Frontend build/check command passes if configured.

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
Open a PR from branch `phase-4-react-vite-tailwind-setup` with a title like `task 4.3: react + vite + tailwind setup`.
The PR description must reference DESIGN.md §7, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
