# AiLibi — Agent Implementation Plan

**Companion to:** `DESIGN.md`
**Audience:** you, building this with provider-neutral AI coding agents
**Goal:** translate the design doc into a phased build plan that uses multiple AI coding agents safely and productively, even if you've never run agents in parallel before.

---

## Provider Notes

These task contracts are provider-neutral. Codex, Claude Code, and generic AI
coding agents are examples of runners that can consume the same task prompts.
Provider-specific setup, UI steps, authentication, billing, and launch commands
belong outside task contracts unless a task explicitly needs them.

---

## Table of contents

- [Provider Notes](#provider-notes)
- [Part 1 — Foundation: the rules of the road](#part-1--foundation-the-rules-of-the-road)
- [Part 2 — How to run multiple AI coding agents](#part-2--how-to-run-multiple-ai-coding-agents)
- [Part 3 — How to write a task prompt](#part-3--how-to-write-a-task-prompt)
- [Part 4 — Phase-by-phase plan](#part-4--phase-by-phase-plan)
- [Part 5 — Review and merge protocol](#part-5--review-and-merge-protocol)
- [Part 6 — Common pitfalls](#part-6--common-pitfalls)
- [Part 7 — Cost and time estimates](#part-7--cost-and-time-estimates)
- [Appendix A — AGENTS.md template](#appendix-a--agentsmd-template)
- [Appendix B — TASKS.md template (Phase 0 example)](#appendix-b--tasksmd-template-phase-0-example)
- [Appendix C — Task prompt templates](#appendix-c--task-prompt-templates)

---

> **Routing note (Task 19.1, 2026-08).** This build plan is the historical
> onboarding narrative — how the repo was bootstrapped and how agent work was
> dispatched, phase by phase. It is read once, at onboarding, not per task.
> Where it names `DESIGN.md` as the source of truth, that was true **at build
> time**; it is not the live routing. Today `AGENTS.md` carries the routing and
> points architecture reading at [`docs/architecture.md`](docs/architecture.md),
> the current-architecture note; `DESIGN.md` is the historical design record (a
> v0.1 draft, reconciled to HEAD as of the Phase 6 close, 2026-05-30), read for
> rationale and history. The per-PR implementation contract is still the task
> file under `tasks/phase-N.md`, and its section refs still bind. The embedded
> `AGENTS.md` and task-prompt templates in Appendices A and C — like the
> illustrative prompt quotes in the narrative parts below — are Phase-0
> artifacts, superseded by the live `AGENTS.md` and
> `scripts/prompt_template.md.j2`.

---

## Part 1 — Foundation: the rules of the road

### 1.1 The strategy in one paragraph

You are the architect and reviewer. The AI coding agent is the implementer:
sometimes one agent at a time, sometimes several in parallel. `DESIGN.md` was,
at build time, the single source of truth, and every task prompt anchored to a
specific section of it; today that anchoring role belongs to the task contract's
section refs in `tasks/phase-N.md`, with `AGENTS.md` routing architecture
reading to `docs/architecture.md`. Every task ends with tests passing. You never
let an agent merge its own work; you read every diff before merging, even if
briefly. This is the entire workflow. Everything below is the mechanics.

### 1.2 Three rules you must not break

1. **No agent works without anchoring to a written section reference.** Every task prompt must reference a section. "Implement Section 3.2 WorldState exactly as specified" beats "implement the world state" by a wide margin. *(The rule's original phrasing was "anchoring to DESIGN.md", and at build time the referenced sections were DESIGN.md's; today the binding refs are the task contract's in `tasks/phase-N.md`, and architecture reading is routed by `AGENTS.md` to `docs/architecture.md`.)*
2. **Two agents never edit the same files at the same time.** This is enforced by branches and (if running locally) by git worktrees. If you forget this rule, you will eat hours of merge pain.
3. **Tests are the contract, not vibes.** Each task has a concrete, runnable definition of done — usually a pytest that passes. "Looks right" is not done.

If you only remember three things from this document, remember these.

### 1.3 Prerequisites

Before you spin up the first AI coding agent, do the following yourself by hand. This is one evening of work and pays for itself many times over.

1. **Create the repo and push to GitHub.** A cloud agent runner needs a GitHub repo to operate on PRs. Even if you also use a local runner, having a remote is non-negotiable for diff review.
2. **Initialize the Python project skeleton.** Just `pyproject.toml`, an empty `engine/` and `agents/` package, a `tests/` folder, and a passing dummy test (`def test_smoke(): assert True`). This avoids AI coding agents inventing wildly different project structures across tasks.
3. **Commit `DESIGN.md` and this `AGENT_IMPLEMENTATION.md` at the repo root.** Every agent gets to read them.
4. **Create `AGENTS.md` at the repo root.** This is the convention file an AI coding agent reads on every task. Use the template in Appendix A.
5. **Set up CI on GitHub Actions** that runs `pytest` and `ruff` on every PR. You want a green/red signal you can trust before reading any agent's diff.
6. **Decide your default branch policy.** I recommend: `main` is protected, all work happens on `phase-N-*` branches, PRs must pass CI to merge. AI coding agents always work on a feature branch, never `main`.

### 1.4 What goes in your `AGENTS.md`

`AGENTS.md` is the file an AI coding agent reads at the start of every task. It is short and load-bearing. The full template is in Appendix A; the contents you must include:

- A pointer to `DESIGN.md` and `AGENT_IMPLEMENTATION.md`.
- The three load-bearing rules from `DESIGN.md` Section 0, restated.
- The observation firewall as a constraint the agent must not violate (don't import `engine` from `agents`).
- The "definition of done" checklist (tests, types, lint pass).
- Coding conventions (Python 3.11, Pydantic v2, asyncio, no global state).
- The "when in doubt, ask in PR description, don't guess" instruction.

### 1.5 The TASKS.md pattern

For each phase, you (the human) write a `tasks/phase-N.md` file that decomposes that phase into individual issue-shaped tasks. This is the playbook for the rest of the workflow.

Each task has a fixed shape:

```markdown
### Task N.M — short title
**Owner:** AI coding agent (cloud | local)
**Branch:** phase-N-{slug}
**Depends on:** Task N.K (must be merged first)
**Section refs:** DESIGN.md §3.2, §3.3
**Files in scope:** engine/world.py, engine/entities.py
**Files NOT in scope:** anything in agents/ or observation/
**Definition of done:**
- [ ] Pydantic models for WorldState and PlayerState as specified.
- [ ] Test `tests/engine/test_world_state.py::test_immutability` passes.
- [ ] mypy strict passes on engine/world.py.
- [ ] Diff has no edits outside files-in-scope.
**Task prompt:** (paste from Appendix C, fill in blanks)
```

Tasks under the same phase that share no files in scope can run **in parallel**. Tasks that touch the same file run **in series**. This is how you decide what to fan out.

---

## Part 2 — How to run multiple AI coding agents

There are three viable mechanisms, and you'll likely use a mix. Each is explained below.

### 2.2 Mechanism A — Cloud agent runner (recommended for parallel work)

A cloud agent runner lets you dispatch multiple tasks at once, each running in
its own isolated environment. Each task opens a pull request when it finishes.
This is the easiest way to run agents in parallel because every task gets a
fresh checkout of your repo.

**The workflow:**

1. Open your cloud runner's task UI.
2. Connect your GitHub repo if you haven't already.
3. For each parallel task:
   - Click "New task" (or equivalent).
   - Paste the prompt from your `tasks/phase-N.md`.
   - Specify the base branch (usually the phase branch, or `main` if it's the first task in the phase).
   - Submit.
4. The agent spins up a sandbox, runs the task, and opens a PR.
5. You review the PRs (Part 5).
6. Merge in order, resolving conflicts on later PRs if necessary.

**When to use it:** anything that touches a well-isolated set of files. Fan out 2–4 at a time for leaf-node work (frontend components, eval scripts, prompt templates, fixture data). More than 4 at once is a review bottleneck for one human.

**Important:** cloud runners may charge per task and per token. See Part 7 for
ballparks.

### 2.3 Mechanism B — Local agent runner in multiple terminals + git worktrees

When you want hands-on iteration with an agent (e.g., debugging an engine rule),
use a local agent runner. To run two local agents at once, use **git
worktrees**: a git feature that creates multiple working directories backed by
the same repo. This way two agents can edit two different branches at the same
time without confusing each other.

**Git worktrees in 60 seconds:**

```bash
# from your main repo checkout
cd ~/code/ailibi

# create a second working directory for a different branch
git worktree add ../ailibi-frontend phase-4-frontend

# now you have two folders, each on a different branch
ls ~/code/
# ailibi/           (on phase-3-meetings)
# ailibi-frontend/  (on phase-4-frontend)

# in terminal 1
cd ~/code/ailibi
agent-runner   # works on phase-3-meetings

# in terminal 2
cd ~/code/ailibi-frontend
agent-runner   # works on phase-4-frontend, no conflicts
```

When done, remove the worktree:

```bash
git worktree remove ../ailibi-frontend
```

**Why worktrees and not just two `git clone`s?** Worktrees share git history, so branches and refs stay in sync. If terminal 1 commits, terminal 2 sees the commit immediately on `git fetch`. Two separate clones drift.

**When to use it:** when you want to watch an agent work and intervene mid-task.
A local runner gives you a tighter feedback loop than a cloud runner, at the
cost of holding your machine.

### 2.5 Mechanism C — Hybrid

The pattern I recommend for AiLibi:

- **Foreground (local):** the active phase's "spine" task — usually one big sequential task that builds the phase's core (e.g., engine simulation core in Phase 1). You watch this one carefully.
- **Background (cloud):** 2–3 leaf-node tasks fanned out in parallel, opening PRs you'll review later.

Concretely: while you're driving local agent runner through Phase 1's engine work, you might have cloud agent runner working on the empty React/Pixi scaffolding for Phase 4 in the background. They never touch the same files.

### 2.6 Picking the mechanism per task

| Task type                                              | Mechanism      | Why                                          |
| ------------------------------------------------------ | -------------- | -------------------------------------------- |
| Architectural / firewall-sensitive (engine, obs, mem)  | Local, 1 agent | High stakes, need close oversight            |
| Leaf-node UI components (Pixi map, Meeting view)       | Cloud, fan out | Low stakes, isolated files, parallel-safe   |
| Prompt templates (`agents/strategic/prompts/*.j2`)     | Cloud          | One file each, perfectly parallelizable      |
| Eval scripts and fixtures                              | Cloud, fan out | Read-only against engine outputs             |
| API routes (one route per task)                        | Cloud          | Parallel-safe if one route per branch       |
| Memory rendering function                              | Local          | Cross-cutting; touches schemas + LLM input   |
| Big refactors                                          | Local          | Iterative, exploratory                       |

---

## Part 3 — How to write a task prompt

### 3.1 Anatomy of a good prompt

A good task prompt has seven parts, in this order:

1. **The role and context.** "You are working on the AiLibi project. Read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section before starting."
2. **The exact task and section reference.** "Implement Task 1.2 — State model, anchored to DESIGN.md §3.2."
3. **The copied task contract.** Paste the exact task body from `tasks/phase-N.md`, starting at `**Branch:**` and ending at the Definition of done checklist. This is what keeps prompts synchronized with the human task plan.
4. **Pre-flight checklist.** Require the agent to read the governing docs, inspect the current implementation before editing, confirm dependencies, and follow existing local patterns.
5. **Constraints / non-goals.** Protect source-of-truth docs, unrelated packages, the observation firewall, and phase boundaries.
6. **Verification checklist.** Require every DoD command, `git diff --name-only` scope review, and explicit reporting of unchecked DoD items.
7. **Output expectation.** "Open a PR titled `task 1.2: state model` from branch `phase-1-state-model`."

The prompt files in `agent_prompts/` are paste-ready wrappers around the task
contracts in `tasks/phase-*.md`. The task files remain the source of truth.
`scripts/validate_task_docs.py` enforces that every task has exactly one prompt,
that each prompt copies the task contract exactly, and that same-phase parallel
tasks do not edit the same files unless dependencies make them sequential.

### 3.2 Anatomy of a bad prompt (anti-patterns)

Things that look reasonable but produce drift:

- **"Implement the engine."** Too broad. The agent will make a hundred decisions you didn't review.
- **"Make it production quality."** Meaningless to an agent. Be concrete about what passes vs. fails.
- **"Use best practices."** Same. Specify Pydantic v2, asyncio, what counts as done.
- **"Add tests."** What tests? Specify the test names and what they assert.
- **"Refactor as needed."** Almost always a mistake — the agent will go on a refactor spree across files outside the scope.

### 3.3 Section-anchoring is the most important habit

The biggest win from `DESIGN.md` is that you can write prompts like "Implement §6.3 belief tracking with the exact suspicion update weights specified" and the agent will produce code that matches the design rather than inventing its own scheme. This is what keeps the architecture coherent across many independent tasks.

### 3.8 Definition of done

Every task has a checklist. The checklist is part of the prompt and ends up in the PR description. Example:

```
Definition of done:
- [ ] All Pydantic models from §3.2 implemented as frozen dataclasses
- [ ] tests/engine/test_world_state.py: 4 tests passing
- [ ] mypy --strict engine/world.py: 0 errors
- [ ] Diff touches only engine/world.py and engine/entities.py
- [ ] No imports from agents/ or observation/
```

If the agent says "done" and one box is unchecked, the PR is rejected. This is the one rule you must enforce — agents will absolutely declare victory prematurely otherwise.

### 3.9 Prompt/task validation

Run `uv run python scripts/validate_task_docs.py` whenever you add, rename, or
edit a task or prompt. The full `bash scripts/check.sh` gate runs it
automatically. A validator failure means the workflow docs are out of sync; fix
the task/prompt mismatch before dispatching more agents. Phase 0 and Phase 1
retain their historical IDs, but Phase 2 and later must use simple numeric task
IDs like `2.1`, `2.2`, and `3.10`; do not add lettered or prompt group IDs.
A single half-step suffix (e.g., `2.7.5`) is permitted only for an audit-repair
or hygiene task slotted between two sequential tasks, mirroring the `1.3.5`
precedent; do not nest deeper than one half-step.

---

## Part 4 — Phase-by-phase plan

Each phase below tells you: the goal, whether to run agents in series or parallel, the task breakdown, and the merge criteria.

### Phase 0 — Scaffolding (1 agent, ~half a day)

**Goal:** repo, CI, project skeleton, the lint rule that enforces the observation firewall, and a failing leak test.

**Parallelism:** none. Single sequential agent (local runner preferred so you can watch).

**Tasks:**

- **0.1 Repo skeleton.** Create `pyproject.toml`, `engine/`, `agents/`, `observation/`, `meetings/`, `orchestrator/`, `llm/`, `api/`, `eval/`, `tests/`. Empty `__init__.py` files. Smoke test passes.
- **0.2 CI workflow.** `.github/workflows/ci.yml` running `ruff`, `mypy`, `pytest`. Triggers on PR.
- **0.3 Import boundary lint rule.** Add `import-linter` config that fails if `agents/` imports from `engine/`. Verify by adding an intentional bad import in a test, watching CI fail, then removing it.
- **0.4 Skeleton leak test.** `eval/leak_test.py` that imports nothing from `engine/` directly but defines the test that will be implemented in Phase 1. Marked `@pytest.mark.skip` for now with a TODO.
- **0.5 ADR file.** `docs/adr/0001-three-load-bearing-decisions.md` capturing DESIGN.md §0 verbatim.

**Merge criteria:** all five tasks merged, CI green on `main`, you can clone the repo and `pytest` runs.

**Task prompt for 0.1 (template):**

```
Read AGENTS.md and DESIGN.md §2 (Repository structure) before starting.

Task: create the project skeleton for AiLibi exactly as specified in DESIGN.md §2.

Scope:
- Create pyproject.toml using uv with Python 3.11, Pydantic v2, FastAPI, pytest, mypy, ruff, import-linter as dev deps.
- Create empty packages: engine/, observation/, agents/, agents/tactical/, agents/strategic/, agents/strategic/prompts/, agents/memory/, meetings/, orchestrator/, llm/, api/, eval/, scripts/, tests/.
- Each package gets an empty __init__.py.
- Add a smoke test tests/test_smoke.py that asserts True.

Out of scope: any actual logic. Just the skeleton.

Definition of done:
- [ ] `pytest` runs and passes (the smoke test)
- [ ] `ruff check .` passes
- [ ] Repo tree matches DESIGN.md §2 exactly
- [ ] No file outside the listed scope is created

Open a PR titled "phase-0: project skeleton" against main.
```

### Phase 1 — Simulation core (1 agent foreground, 1 in parallel possible)

**Goal:** the engine ticks deterministically, ObservationService produces packets that pass the leak test, replay is byte-exact.

**Parallelism:** one foreground local agent on the engine. In parallel, you can
have a second cloud-runner agent build the determinism and leak test fixtures,
since they don't touch engine internals — they consume them.

**Foreground tasks (sequential, on `phase-1-engine`):**

- **1.1 Static map data.** `engine/world.py::Map`, room graph, vent network. One canonical map as YAML.
- **1.2 State model.** `WorldState`, `PlayerState`, `BodyState`, `TaskState`, `SabotageState` per §3.2.
- **1.3 Action types.** `engine/actions.py` Pydantic union per §A. Validators.
- **1.4 Rules.** `engine/rules.py` for kill, vent, report, sabotage, win conditions per §3.8 + §3.5.
- **1.5 advance_tick.** Pure function `(state, actions) -> (state', events)` per §3.1. RNG threaded through `engine/rng.py`.
- **1.6 Visibility.** `engine/visibility.py` per §3.10 + §1.3 simplifications (room + adjacent room).
- **1.7 ObservationService.** `observation/service.py` and `ObservationPacket` schema per §1.3 + §4.2. Audit log to disk.
- **1.8 Replay log.** `orchestrator/replay.py` writes JSONL of (tick, actions, state-hash) per game.

**Background tasks (parallel, on separate branches, cloud runner):**

- **1.B1 Test fixtures.** Hand-author `tests/fixtures/scripted_game_*.json` — short canned games used by the determinism test. Doesn't touch engine code; can be done as soon as the action schema is stable (after task 1.3 lands).
- **1.B2 Leak test implementation.** Once `ObservationPacket` exists (task 1.7), implement the actual assertions. Can be done in parallel with task 1.8.

**Merge criteria:**
- `pytest tests/engine/` green.
- `pytest eval/leak_test.py` green against three different scripted games.
- `pytest eval/determinism_test.py` green: identical seed + actions → identical replay log.
- `mypy --strict engine/ observation/` green.

**How to run this:** open local agent runner in the main checkout, work through 1.1 → 1.8 sequentially. After 1.3 merges, fan out task 1.B1 to cloud agent runner on a separate branch. After 1.7 merges, fan out 1.B2.

### Phase 2 — Tactical agents (1 agent foreground, parallel-friendly mid-phase)

**Goal:** rule-based crewmate and impostor agents complete games headlessly without crashing. Win rates land in a believable band even without LLMs.

**Parallelism:** serial through the firewall-safe boundary contracts, runtime, memory, perception, and pathing. Crewmate and impostor policies can then run in parallel because they live in separate files and both return `ActionIntent`. The single-game orchestrator and tournament harness run after both policies merge.

**Tasks:**

- **2.1 Boundary contracts.** Engine-free `ActionIntent` and `PublicMapView` plus orchestrator adapters that translate to engine-owned types.
- **2.2 Agent base + runtime.** `agents/base.py` and `agents/runtime.py` per §4.1. Runtime consumes `ObservationPacket` + `PublicMapView` and returns `ActionIntent`.
- **2.3 Memory scaffolding (no LLM).** `agents/memory/episodic.py`, `working.py`, `beliefs.py` per §6.1. Write paths only — no rendering yet.
- **2.4 Perception ingestion.** `agents/perception.py` converts `ObservationPacket` into typed episodic events.
- **2.5 Pathing.** `agents/tactical/pathing.py` — deterministic A* over `PublicMapView`.
- **2.6 Crewmate FSM.** `agents/tactical/crewmate_policy.py` per §4.4. Consumes memory/public map; returns `ActionIntent`. **(parallel branch)**
- **2.7 Impostor FSM.** `agents/tactical/impostor_policy.py` per §4.4. Consumes memory/public map; returns `ActionIntent`. **(parallel branch)**
- **2.8 Headless game orchestrator.** `orchestrator/game.py`, `seeder.py`, `scheduler.py`, and `scripts/run_game.py` wire seed setup, observations, agents, action-intent translation, replay, and game-over handling.
- **2.9 Headless tournament harness.** `scripts/run_tournament.py`, `eval/balance_eval.py` per §11.3. Aggregates many games; does not invent the single-game orchestrator.

**Parallelism plan:**
- Sequential: 2.1 → 2.2 → 2.3 → 2.4 → 2.5.
- After 2.5 merges, fan out 2.6 and 2.7 to two cloud-runner agents in parallel. They edit different files; they should not conflict.
- 2.8 runs after 2.6 and 2.7 are merged. 2.9 runs after 2.8.

**Merge criteria:**
- 100-game headless tournament completes without crashes.
- Both sides win > 20% of games (sanity check).
- Leak test still passes across all 100 games.
- `agents/` still has no direct or transitive imports from `engine/`.

### Phase 3 — Strategic agents and meetings (1 foreground agent, prompt work in parallel)

**Goal:** LLM-driven meetings work end-to-end. Openings, a reactive accusation chain, votes. Cost stays under budget.

**Parallelism:** LLM client, shared schemas, memory rendering, meeting state, reasoner, voting, contradiction detection, and meeting/orchestrator integration are serial. Prompt templates can run in parallel after memory rendering lands, because they depend on both schemas and rendered-memory inputs.

**Tasks (sequential foreground, on `phase-3-meetings`):**

- **3.1 LLM client.** `llm/client.py`, `llm/provider.py`, `llm/fake_provider.py`, cache, and budget. CI uses the fake provider only.
- **3.2 Shared meeting/output schemas.** `meetings/schemas.py` owns `MeetingTurn`, `MeetingTranscript`, `VoteBallot`, `MeetingResult`, and contradiction DTOs. `agents/strategic/output_schemas.py` may re-export/wrap them but must not duplicate definitions.
- **3.3 Memory rendering.** `agents/memory/store.py::render_for_prompt` per §6.6. This is the hard, important one.
- **3.8 Meeting state machine.** `meetings/manager.py` and `meetings/transcript.py` per §5.1 + §5.2 — the reactive accusation chain (opening → chain → opt-in info-share → vote). Returns `MeetingResult`; does not mutate engine state.
- **3.9 Strategic reasoner.** `agents/strategic/reasoner.py` — wires render_for_prompt → LLM → parsed output.
- **3.10 Voting.** `meetings/voting.py` per §5.5.
- **3.11 Contradiction detection.** `meetings/transcript.py::detect_contradictions` per §5.4 + §6.4.
- **3.12 Meeting/orchestrator integration.** Orchestrator applies `MeetingResult`, resumes gameplay, and records meeting artifacts, prompt versions, and LLM cost metadata in replay/eval records.

**Parallel tasks (cloud runner, after 3.3 merges):**
- **3.4 Crewmate opening prompt.** `agents/strategic/prompts/crewmate_report.j2`.
- **3.5 Impostor opening prompt.** `agents/strategic/prompts/impostor_report.j2`.
- **3.6 Accusation-chain turn prompt.** `agents/strategic/prompts/accusation_round.j2`.
- **3.7 Vote ballot prompt.** `agents/strategic/prompts/vote_ballot.j2`.

These are four files, four agents, fully parallel.

**Merge criteria:**
- 50-game eval: full-LLM games complete end-to-end.
- Impostor win rate in [25%, 65%] band.
- Cost per game ≤ $0.30 (or whichever provider's equivalent).
- Meeting transcripts are human-readable.
- Replay/eval records include meeting artifacts, prompt versions, and LLM cost metadata.

**Tip:** wire up budget caps in `llm/budget.py` early. agent tasks will sometimes loop on retries when prompts fail validation; you do not want that to drain your account.

### Phase 4 — Spectator UI (highly parallel)

**Goal:** browser-based live spectator + replay viewer.

**Parallelism:** this phase is the most parallel-friendly. After the API is up, every component is its own file with clear inputs.

**Tasks:**

- **4.1 FastAPI app skeleton and spectator DTOs.** `api/main.py`, `api/schemas.py`, basic routes, WebSocket endpoint per §7. **(serial)**
- **4.2 Game broadcast.** `api/ws.py` — broadcast sanitized tick and meeting events from a running game. **(serial)**
- **4.3 React + Vite + Tailwind setup.** `frontend/` skeleton, type-safe API client, npm with `package-lock.json` unless an existing repo choice says otherwise. **(serial)**
- **4.4 MapView.** PixiJS canvas rendering rooms + players. **(parallel)**
- **4.5 MeetingView.** Transcript renderer. **(parallel)**
- **4.6 ThoughtStream.** Per-agent memory + LLM call viewer. **(parallel)**
- **4.7 BeliefMatrix.** Heatmap of who suspects whom. **(parallel)**
- **4.8 ReplayControls.** Scrubber, speed control. **(parallel)**

**Parallelism plan:** 4.1 → 4.2 → 4.3 in series (cloud runner, but one at a
time). Task 4.3 owns the shared store/API interface. Then fan out 4.4–4.8 to
five cloud-runner agents at once. Each touches its own file in
`frontend/src/components/` and consumes the store shape from 4.3.

**Merge criteria:** non-technical viewer can watch a live game and replay any saved one; spectator API and WebSocket payloads expose sanitized DTOs only.

### Phase 5 — Eval and polish (highly parallel)

**Goal:** every prompt or rule change produces a measurable signal in the eval dashboard.

**Tasks (mostly parallel after 5.1):**

- **5.1 Eval report schema.** `eval/report_schema.py` defines the typed tournament/eval JSON report.
- **5.2 Vote-correctness metric.**
- **5.3 Accusation-calibration metric.**
- **5.4 Alibi-fabrication-rate metric.**
- **5.5 Cost dashboard (per-prompt-version cost).**
- **5.6 Tournament metric integration.** Wire 5.2–5.5 into tournament JSON output after parallel metric branches merge.
- **5.7 Tournament dashboard frontend page.**
- **5.8 Prompt regression test suite.**

5.2–5.5 are all independent files in `eval/` — perfect cloud fan-out (4
parallel tasks). They do not edit `scripts/run_tournament.py`; 5.6 owns that
integration to avoid conflicts.

**Merge criteria:** running `python scripts/run_tournament.py --N=200` produces a JSON report with all metrics; the frontend dashboard renders it.

### Phase 6 — Human player (post-MVP, single agent)

Held until MVP demonstrably works. Sequential local-runner work; UI changes plus a human seat on the WebSocket plus latency-tolerant tick pacing.

---

## Part 5 — Review and merge protocol

This is where you stay sane while running 3+ agents in parallel.

### 5.2 Your PR review checklist

For every PR an agent opens, before merging:

1. **Did CI pass?** If not, comment on the PR with the failure and ask the agent to fix it. Don't fix it yourself unless trivial.
2. **Does the diff stay in scope?** If the PR touches files outside the listed scope, reject. This is the most common drift.
3. **Did all definition-of-done boxes get checked?** Read the PR description, verify each.
4. **Does the code match the design section?** Skim DESIGN.md side-by-side. If the agent invented a different approach, ask why or reject.
5. **Did it introduce engine imports in agents/?** Run `import-linter` locally if CI is unclear.
6. **Eyeball the tests.** Are they testing real behavior or just the happy path? Add a TODO if a missing test should land in a follow-up task.

This takes 5–15 minutes per PR. Budget for it. If you have 4 PRs queued up and zero review time, you have too many agents running.

### 5.3 Merge order

When two parallel PRs both touch the same file (it happens despite scope), merge the smaller one first, then ask the second agent to rebase. Don't try to manually resolve the conflict yourself — give the rebase task back to the agent with clear instructions.

### 5.4 The "I'll just fix this myself" trap

You'll be tempted to fix small things in agent diffs by hand. Resist most of the time, because:
- Hand fixes don't improve the next agent's behavior.
- Hand fixes break the test-driven discipline.
- Hand fixes make it impossible to re-run a phase from scratch.

The exception: typos in non-code files (READMEs, ADRs). Fix those by hand; not
worth an agent round-trip.

### 5.5 Detecting design drift

Every 2–3 merged PRs, do a 5-minute "drift check":
- Re-read DESIGN.md §0 (the three load-bearing decisions).
- Spot-check that the latest code still embodies them. (Does any agent code import engine? Did the LLM creep into the tactical loop?)
- If something has drifted, open a corrective task immediately. Drift compounds.

---

## Part 6 — Common pitfalls

These are the failure modes most beginners hit on parallel-agent workflows. Forewarned is forearmed.

**Pitfall 1: agent stomping.** Two agents working on the same file at once. Symptom: merge conflicts, half-baked diffs, mysterious test failures. Cause: not specifying "files in scope" precisely, or fanning out before the shared scaffolding is merged.

**Pitfall 2: vague prompts.** "Implement the agent system" produces a dump of code that nominally compiles, doesn't pass tests, and bears only superficial resemblance to your design. Cause: skipping section anchors. Cure: never write a prompt without a specific `DESIGN.md §X.Y` reference.

**Pitfall 3: "it compiles" syndrome.** Agent declares done because nothing errored. No tests were run; the code might not even execute. Cause: a definition-of-done that lacks a runnable test. Cure: every task ends with a passing pytest or another working command.

**Pitfall 4: silent design drift.** Agent invents its own approach because it thinks it's better. Often the new approach is worse in subtle ways (e.g., it merges engine and observation into one module, killing the firewall). Cure: anchor every prompt; spot-check every PR; don't be afraid to reject and re-ask.

**Pitfall 5: review backlog.** Five cloud-runner tasks running, nothing
merged, you're mentally underwater. Cure: cap concurrent tasks at what you can
review. For most beginners this is 2 at a time.

**Pitfall 6: cost spirals.** Cloud runners may retry on failure, and failed
prompt retry loops can burn through credit fast. Cure: set hard budget caps where
the platform supports them; check usage daily for the first week; use cheaper
models for cosmetic tasks (e.g., styling tweaks).

**Pitfall 7: "fix it for me, you said you would."** Some agent runs will produce subtly broken work that the agent insists is correct. Don't argue with the agent — close the PR, refine the prompt, dispatch a fresh task. Conversational debugging with a wrong-headed agent is a time sink.

**Pitfall 8: tests written by the same agent that wrote the code.** Tests pass because they test what the agent wrote, not what the spec required. Cure: for safety-critical pieces (the leak test, the determinism test), write the test yourself or have a *different* agent task author the test against the spec, not against the existing implementation.

**Pitfall 9: untracked prompt versions.** You change a prompt template, win rates change, you can't reconstruct what changed. Cure: every prompt has a version string in its frontmatter; every game logs the prompt version it used; eval results are tagged with prompt version. This is in DESIGN.md §11.3 — enforce it.

**Pitfall 10: pushing past your context.** You're tired, an agent's diff looks plausible, you merge. Two days later the leak test fails because of that PR. Cure: when you can't review carefully, don't merge. Cloud-runner PRs can sit overnight.

---

## Appendix A — AGENTS.md template

> **Historical Phase-0 template — superseded by the live `AGENTS.md` at the repo
> root.** This is the file that was written by hand to bootstrap the repo; the
> live `AGENTS.md` has moved on (its routing, conventions and definition of done
> are the ones that bind). Read this for how the repo started, not as
> instruction. The "Source of truth" block below has been re-pointed to the
> current routing so the template cannot be pasted forward with stale authority;
> everything else is left as it was written.

Save this verbatim (with light edits) as `AGENTS.md` at the repo root.

```markdown
# AGENTS.md

You are an AI coding agent working on AiLibi. Read this file before every task,
then read the architecture routing it names and the task contract as referenced.

## Source of truth

- `docs/architecture.md` is the current-architecture note, authoritative for the
  system's layering as built. `DESIGN.md` is the historical design record (v0.1
  draft, reconciled to HEAD as of the Phase 6 close, 2026-05-30) — read it for
  design rationale, not for current architecture.
- The task contract in `tasks/phase-N.md` is the implementation contract for the
  PR, and its section refs bind. If the section says X, you do X — even if you
  think Y is better. If you genuinely think the contract is wrong, leave a
  comment in the PR description and stop. Do not change it unilaterally.
- `AGENT_IMPLEMENTATION.md` is the provider-neutral build plan, read once at
  onboarding. The current task description in the prompt overrides it where they
  conflict.

## Three load-bearing rules (DESIGN.md §0)

1. **Tick-based deterministic engine.** Engine is a pure function of state
   and actions. Replays must be byte-identical from a seed.
2. **Two-tier agent reasoning.** LLMs only at meetings or specific triggers.
   Tactical decisions are rule-based. Do not put LLM calls inside `agents/tactical/`.
3. **Structured memory first.** Agents reason from a typed event log and a
   derived belief state. The LLM sees a *rendered* memory view, not raw chat.

## Architectural constraints

- **The observation firewall is non-negotiable.** `agents/` MUST NOT import
  from `engine/`. This is enforced by `import-linter` in CI. If your task
  needs an engine type in agent code, it is the wrong task — stop and ask.
- **No global state.** No singletons, no module-level mutable state. All state
  is owned by an explicit object and passed through.
- **No silent fallbacks.** If something is invalid, raise. Do not paper over.

## Coding conventions

- Python 3.11. Type hints on every function. `mypy --strict` must pass on
  `engine/`, `observation/`, `agents/`.
- Pydantic v2 for all data classes that cross module boundaries. Frozen
  dataclasses for engine state.
- `asyncio` for concurrent agent dispatch. No threads.
- `ruff` and `ruff format` must pass.
- Tests are `pytest`. Property tests use `hypothesis`.

## Definition of done (always)

A task is not done until:
- All checkboxes in the task's "Definition of done" are checked.
- `bash scripts/check.sh` passes locally.
- The diff touches only the files listed as in scope.
- The PR description references the DESIGN.md section(s) implemented.

## When you're stuck

Don't guess. In the PR description, write a "Questions" section listing what
you need clarified. Stop and open the PR; the human will respond.
```

---

## Appendix B — TASKS.md template (Phase 0 example)

Save this as `tasks/phase-0.md`.

```markdown
# Phase 0 — Scaffolding

## Goal
Repo, CI, project skeleton, observation-firewall lint rule, skeleton leak test.

## Mechanism
local agent runner, single agent, sequential.

## Tasks

### Task 0.1 — Repo skeleton
**Owner:** local agent runner
**Branch:** phase-0-skeleton
**Depends on:** none
**Section refs:** DESIGN.md §2
**Files in scope:** pyproject.toml, .gitignore, all package __init__.py files, tests/test_smoke.py
**Files NOT in scope:** any logic in any package

**Definition of done:**
- [ ] `pyproject.toml` declares Python 3.11 and lists pydantic v2, fastapi, pytest, mypy, ruff, import-linter, hypothesis as dependencies.
- [ ] All packages from DESIGN.md §2 exist with empty `__init__.py`.
- [ ] `tests/test_smoke.py` has one passing test.
- [ ] `pytest` exits 0.
- [ ] `ruff check .` exits 0.

### Task 0.2 — CI workflow
**Owner:** local agent runner
**Branch:** phase-0-ci
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §11
**Files in scope:** .github/workflows/ci.yml
**Definition of done:**
- [ ] CI runs ruff, mypy, pytest on every PR.
- [ ] CI passes on this PR.

### Task 0.3 — Import boundary lint
**Owner:** local agent runner
**Branch:** phase-0-firewall
**Depends on:** 0.2 merged
**Section refs:** DESIGN.md §1.3
**Files in scope:** .importlinter, .github/workflows/ci.yml (extend), tests/test_firewall.py
**Definition of done:**
- [ ] `import-linter` config bans `agents.*` from importing `engine.*`.
- [ ] CI runs `lint-imports`.
- [ ] `tests/test_firewall.py` adds an intentional bad import in a temp file, runs lint-imports, asserts failure, removes the file.

### Task 0.4 — Skeleton leak test
**Owner:** local agent runner
**Branch:** phase-0-leaktest
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §11.2
**Files in scope:** eval/leak_test.py
**Definition of done:**
- [ ] File exists with a single `@pytest.mark.skip(reason="implemented in phase 1")` test that documents the assertion contract.

### Task 0.5 — ADR
**Owner:** local agent runner
**Branch:** phase-0-adr
**Depends on:** 0.1 merged
**Section refs:** DESIGN.md §0
**Files in scope:** docs/adr/0001-three-load-bearing-decisions.md
**Definition of done:**
- [ ] ADR captures the three load-bearing decisions verbatim with date and author.
```

---

## Appendix C — Task prompt templates

> **Historical Phase-0 template — superseded by `scripts/prompt_template.md.j2`.**
> Prompts are no longer hand-copied: `scripts/generate_prompts.py` renders every
> file under `agent_prompts/` from that Jinja template plus the task contracts,
> and `scripts/validate_task_docs.py` gates the result. The shape below is kept
> because it explains what the generated prompt is *for*; its routing lines have
> been brought into line with the live template so the two cannot be read in
> contradiction.

Copy this shape into `agent_prompts/task-*.md`. The phase task file remains
the source of truth; the prompt is a paste-ready wrapper around the copied task
contract. Replace the `{{...}}` placeholders.

### C.1 Canonical task prompt

```
# Agent Prompt — {{TASK ID}} {{TASK TITLE}}

You are working on AiLibi. Before starting, read AGENTS.md, the architecture
routing it names, and the task section in tasks/phase-{{N}}.md.

1. Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md
exactly; it names the authoritative architecture routing. The task contract
below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the
provider-neutral build plan and is read once during onboarding (see AGENTS.md),
not per task.

2. Exact section reference
Implement Task {{TASK ID}} — {{TASK TITLE}}, anchored to {{DESIGN SECTION REFS}}.
Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-{{N}}.md.
Follow it exactly, including branch, dependencies, section refs, files in scope,
files not in scope, and definition of done.

{{COPY THE TASK BODY FROM **Branch:** THROUGH THE DEFINITION OF DONE CHECKLIST}}

4. Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section
  before editing.
- Inspect the current implementation before editing.
- Confirm the dependency listed in the task contract is present in the current
  branch.
- Identify the existing local patterns for the files in scope and follow them.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in
scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If something is ambiguous, stop and add a Questions section in the PR
description rather than guessing.

6. Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR
  description instead of declaring the task complete.

7. Output expectation
Open a PR from branch `{{BRANCH}}` with a title like `task {{TASK ID}}:
{{TASK TITLE}}`.
The PR description must reference {{DESIGN SECTION REFS}}, list the
definition-of-done checklist, and include a Questions section if anything is
ambiguous.
```

---

## Quick-start checklist

Before you dispatch the first agent task, make sure all of these are true:

- [ ] GitHub repo exists, `main` is protected.
- [ ] `DESIGN.md` and `AGENT_IMPLEMENTATION.md` are committed to `main`.
- [ ] `AGENTS.md` from Appendix A is committed to `main`.
- [ ] `tasks/phase-0.md` from Appendix B is committed to `main`.
- [ ] CI is set up and runs ruff + pytest on PRs.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] You have a cloud agent runner connected to the repo or a local agent
      runner installed.
- [ ] You've set a budget cap on your runner account, where applicable.
- [ ] You can answer "what does DESIGN.md §0 say" without looking it up.

When all those are true, dispatch Task 0.1 and watch the first PR open. Review it, merge it, and repeat. By the end of the first day you'll have a much better feel for how the agent behaves on your specific repo, and you can start fanning out from there.

Good luck. The hard part of this project is not the code — it's keeping the architecture coherent across many small agent tasks. The discipline in this document exists to protect that.
