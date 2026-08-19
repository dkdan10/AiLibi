# Agent Prompt — 4.13 Initial-state TickView synthesis (pre-UX-session Finding 1)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.13 — Initial-state TickView synthesis (pre-UX-session Finding 1), anchored to DESIGN.md §3.1, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-initial-state-tick`
**Depends on:** 4.12 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §11.4
**Complexity:** Small

UX self-audit Finding 1: the MapView's "tick 0" shows agents already
spread across rooms — p-2 in WEST_HALL, p-3 in EAST_HALL, p-4 in
CAFETERIA for seed 22 — instead of the expected initial spawn state
where every player starts in CAFETERIA. The data is honestly what the
recording captures: `ReplayLog.record_tick(input_tick=0, actions,
state=state_after_advance_tick)` snapshots state AFTER `advance_tick`
has processed tick 0's actions (including any `move` actions agents
submitted on their first turn). The pre-action initial state from
`seed_initial_state` is never persisted.

For a non-technical viewer, "tick 0 = start of game" is the only
intuitive mental model, and the current behavior breaks it on the
first impression. This is comprehension-breaking for the UX session;
fix before dispatching the non-tech viewer.

**Scope decision: synthesize on the loader side, no JSONL format
change.** The seeded initial state is fully recoverable from the
`game_id` (which encodes the seed). The loader already calls
`seed_initial_state(seed=N, game_map=...)` at
[api/replay_loader.py:328](api/replay_loader.py#L328); we snapshot
that state into a synthetic `TickView` with `tick=-1` and prepend it
to the `ticks` array. The JSONL format is unchanged; backward-compat
is trivial; old replays inherit the synthesis for free.

The `tick=-1` sentinel is intentional. Existing tick numbers stay
0-indexed and continue to match logs / audit reports / meeting tick
references. The frontend special-cases `tick=-1` to display "Start"
on the scrubber and tick label, so the viewer sees "Start" → "Tick 0"
→ "Tick 1" → ... rather than a confusing negative number.

**Out of scope** (explicit decisions deferred):

- **Changing `record_tick` semantics to capture pre-advance state.**
  That would break every committed replay's `state_hash` baseline and
  require re-running every eval. Synthesis on read is cheaper and
  doesn't invalidate the recorded artifacts.
- **Persisting the synthesized initial entry to JSONL.** No write
  changes; this task is read-side only.
- **Reshaping `TickView.tick` to be a string or enum.** Stays
  `int`; `-1` is the sentinel. Frontend handles the display label.
- **Adding `tick=-1` as a separately-fetchable endpoint slot.** The
  existing `GET /replays/{id}/ticks/{tick}` endpoint accepts the
  sentinel naturally; no new route needed.
- **Updating `ReplayMetadataView.total_ticks` to include the
  synthesized entry.** `total_ticks` continues to mean "number of
  recorded tick entries", which equals the engine's actual play
  length. `ticks[]` has length `total_ticks + 1` (the synthesized
  initial plus the recorded ticks). The frontend reads
  `ticks.length` for scrubber bounds, not `total_ticks`.

**Files in scope:**
- api/replay_loader.py
- frontend/src/components/ReplayControls.tsx
- tests/api/test_replay_loader.py
- tests/api/test_replays.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/schemas.py (no DTO change; `int` accommodates `-1`)
- api/routes/ (existing endpoints handle `tick=-1` naturally)
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/src/types/api.ts
- frontend/src/components/MapView.tsx (reads `currentReplay.ticks[currentTick]` — synthesized entry renders naturally)
- frontend/src/components/MeetingPill.tsx (no meetings at `tick=-1`; pill stays hidden — correct behavior)
- frontend/src/components/MeetingView.tsx
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/ReplayPicker.tsx
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
- [ ] **Loader synthesizes the initial `TickView`.** [api/replay_loader.py](api/replay_loader.py) `load_replay` (or its `_walk`) constructs a `TickView` from `initial_state` immediately after `seed_initial_state(...)` returns and before the entry loop begins. The synthesized view has: `tick=-1`, `agent_states` derived from `initial_state.players` (all players alive, `room_id=spawn_room` from the seeder, `is_venting=False`, `current_action="IDLE"`, `task_progress=0.0` for crewmates / `None` for impostors), `events=()`, `sabotage_active=()`, `tasks_completed_total=0`, `tasks_required_total=len(initial_state.tasks)`. Prepended to the `ticks` list at index 0.
- [ ] **`ReplayMetadataView.total_ticks` unchanged.** `total_ticks` still equals the number of recorded `ReplayEntry`s in the JSONL — it does NOT include the synthesized initial entry. Verify by asserting `len(replay.ticks) == replay.metadata.total_ticks + 1` in a test.
- [ ] **`GET /replays/{game_id}/ticks/-1`** returns the synthesized initial `TickView`. The existing route handler accepts negative ticks (or is extended to do so); endpoint test confirms 200 with the expected spawn state.
- [ ] **Out-of-range tick returns 404 unchanged.** Tick values < -1 or >= total_ticks still 404. Test covers both.
- [ ] **Loader test asserts spawn semantics.** In [tests/api/test_replay_loader.py](tests/api/test_replay_loader.py), a new test loads a real replay (the `sample_replay` fixture or one of `replays/samples/`) and asserts `replay.ticks[0].tick == -1` AND every `agent_states[*].room_id` equals the canonical map's spawn room (`"CAFETERIA"` per `engine/maps/canonical_1.yaml`).
- [ ] **Endpoint test in [tests/api/test_replays.py](tests/api/test_replays.py)** drives `GET /ticks/-1` via `TestClient` and asserts the response JSON contains all four players in `CAFETERIA`.
- [ ] **ReplayControls handles `tick=-1` as "Start".** [frontend/src/components/ReplayControls.tsx](frontend/src/components/ReplayControls.tsx): the scrubber's `min` becomes `-1` (or `0` if currentTick is mapped through an index, depending on the existing implementation), the tick label displays the literal text `"Start"` when `currentReplay.ticks[currentTick].tick === -1`, and `"Tick {n}"` otherwise. Step-backward from tick 0 lands at "Start"; step-forward from "Start" lands at tick 0.
- [ ] **Play-from-Start works.** Click "Start" → press Play → auto-advance walks through tick 0, 1, 2, ... at the configured speed. No off-by-one in the advance loop. Verify manually + assert in a smoke note in the PR description.
- [ ] **MapView renders the initial state correctly.** Manual check: at the synthesized "Start" position, all 4 player tokens cluster in the CAFETERIA rectangle. No jitter-overflow concerns are introduced (this task does NOT fix the jitter-overflow if any remains; the data fix alone resolves Finding 1 even if jitter is imperfect).
- [ ] **Screenshot in PR.** One screenshot of the "Start" scrubber position showing all 4 agents in CAFETERIA for seed 22. This is the visible proof Finding 1 is closed.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/`. `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas.BeliefEntryView"`
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
Open a PR from branch `phase-4-initial-state-tick` with a title like `task 4.13: initial-state tickview synthesis (pre-ux-session finding 1)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.1, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
