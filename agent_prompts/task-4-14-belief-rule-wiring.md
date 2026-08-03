# Agent Prompt — 4.14 Belief-rule wiring for observed venting and body proximity (pre-UX-session Finding 2)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.14 — Belief-rule wiring for observed venting and body proximity (pre-UX-session Finding 2), anchored to DESIGN.md §6.3, DESIGN.md §6.6, mid-phase DTO audit R-2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-belief-rule-wiring`
**Depends on:** 4.12 merged
**Section refs:** DESIGN.md §6.3, DESIGN.md §6.6, mid-phase DTO audit R-2
**Complexity:** Medium

UX self-audit Finding 2: the API returns `beliefs: []` for every
agent at every meeting. Verified via direct curl against the live
loader (`/replays/headless-seed-22/meetings/.../memory/p-2` →
`beliefs: []`). The BeliefMatrix renders empty cells across the
board, not because the matrix component is broken but because the
data is genuinely empty.

Root cause: `agents/memory/beliefs.py` exposes `BeliefState` with
mutation methods (`adjust_suspicion`, `adjust_trust`, etc.) but
nothing in the perception or memory-ingestion pipeline ever calls
them. DESIGN.md §6.3 specifies five rule-based belief updates; none
are wired. Beliefs stay at the default-empty `BeliefState` for every
agent, every tick, every meeting. The promise of the BeliefMatrix
spectator panel (DESIGN.md §6.3, §7) cannot be delivered.

**Scope decision: minimum-viable rule set (Rules 1 + 4), not the
full §6.3 list.**

DESIGN.md §6.3 lists five rule types:
1. +0.2 suspicion if seen near a body shortly before discovery.
2. +0.3 if claimed alibi contradicts another agent's testimony.
3. -0.4 trust adjustment if a verifiable shared task is completed.
4. +0.5 suspicion if observed venting (almost certain).
5. Time decay toward 0.5 over rounds without new evidence.

This task implements Rules 1 and 4 only. Rationale:
- **Rule 4 (observed venting):** the single strongest informational
  signal in Among Us — venting is impostor-exclusive. One witness
  collapses uncertainty almost to certainty. Without it the matrix
  can never reflect the strongest evidence agents actually have.
- **Rule 1 (body proximity):** the bread-and-butter Among Us
  deduction. Every meeting at a body-discovery trigger should
  surface elevated suspicion for agents recently co-present in that
  room.
- Rules 2, 3, 5 add nuance but require either meeting-transcript
  analysis (Rule 2) or per-tick scaffolding (Rule 5) that this task
  doesn't need to deliver to close Finding 2.

Rules 2, 3, 5 land as a Phase 5 follow-up (probably under "eval &
polish") when the belief-tuning loop becomes a measured concern.

**Suspicion weights as config, not constants.** DESIGN.md §6.3
explicitly says: "These weights are config, not constants — they
will be tuned against the eval harness." This task introduces a
single module-level constant per implemented rule (e.g.
`VENTING_SUSPICION_DELTA = 0.5`, `BODY_PROXIMITY_DELTA = 0.2`,
`BODY_PROXIMITY_WINDOW_TICKS = 3`). Future tuning is a one-line
edit. No external config file or dependency added.

**Out of scope** (explicit decisions deferred):

- **Rules 2, 3, 5.** Deferred to Phase 5.
- **Per-belief recency timestamping.** Task 4.9 deliberately renamed
  `last_updated_tick` → `snapshot_tick` and kept `PlayerBelief` as
  a timeless dataclass. This task does NOT add a `last_updated_tick`
  field to `PlayerBelief`. If a future task wants per-rule recency
  tracking it can add it then.
- **External config file for weights.** Module-level constants
  suffice for the MVP. A YAML / TOML config layer is Phase 5+.
- **Belief decay loops.** Rule 5 requires per-tick decay; this task
  doesn't implement it. Beliefs that fire from Rules 1/4 stay
  elevated for the rest of the game.
- **Wiring the rules into the LIVE tournament path.** The loader's
  memory reconstruction (via `_ingest_tick`) is what populates
  BeliefMatrix; both paths exercise the same `agents/perception.py`
  ingestion code, so a single fix unblocks both.

**Files in scope:**
- agents/memory/beliefs.py
- agents/perception.py
- tests/agents/test_perception.py
- tests/agents/test_beliefs.py

**Files NOT in scope:**
- engine/
- llm/
- meetings/
- observation/
- orchestrator/
- api/ (the loader's existing `_ingest_tick` → `agents/perception.py` path delivers populated beliefs to the DTO layer with zero changes)
- frontend/ (BeliefMatrix renders whatever the API serves; populated cells appear automatically)
- agents/strategic/ (rule firing is per-tick perception work, not strategic LLM reasoning)
- agents/tactical/
- agents/memory/episodic.py (no episodic-store changes; rules read from observation packets and write to BeliefState)
- agents/memory/working.py
- agents/memory/meeting_memo.py
- agents/memory/store.py
- agents/runtime.py (the per-tick AgentRuntime call already routes through perception)
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
- [ ] **Module-level weight constants** declared in [agents/memory/beliefs.py](agents/memory/beliefs.py): `VENTING_SUSPICION_DELTA: Final[float] = 0.5`, `BODY_PROXIMITY_SUSPICION_DELTA: Final[float] = 0.2`, `BODY_PROXIMITY_WINDOW_TICKS: Final[int] = 3`. All three reference DESIGN.md §6.3 in their docstring.
- [ ] **`apply_observation_rules` (or equivalently-named) function** in [agents/memory/beliefs.py](agents/memory/beliefs.py) takes `(beliefs: BeliefState, observation_packet, recent_co_presence) → BeliefState`. Pure function, returns a new `BeliefState`. Inputs:
  - `beliefs`: current belief state for the observing agent
  - `observation_packet`: the `ObservationPacket` for this tick (per [observation/packet.py](observation/packet.py))
  - `recent_co_presence`: a `Mapping[PlayerId, Sequence[tuple[int, RoomId]]]` describing which other players the agent has been co-located with in the prior `BODY_PROXIMITY_WINDOW_TICKS` ticks, derived from the agent's own episodic memory. The function does NOT reach into episodic store; the caller passes pre-computed co-presence.
  - Returns: updated `BeliefState` with Rule-4 and Rule-1 deltas applied.
- [ ] **Rule 4 (observed venting) fires.** When `observation_packet.audible_events` (or wherever vent-use observations land per the firewall design) contains a vent-use event attributed to a specific player, the function calls `beliefs.adjust_suspicion(player_id, delta=VENTING_SUSPICION_DELTA)`. Clamped to `[0, 1]` per the existing `adjust_suspicion` semantics.
- [ ] **Rule 1 (body proximity) fires.** When `observation_packet.visible_bodies` contains a newly-discovered body (one not present in the previous tick's packet — implementing agent decides how to detect "new"; simplest is to compare current vs prior packet), the function reads `recent_co_presence` for the body's room over the prior `BODY_PROXIMITY_WINDOW_TICKS` ticks and applies `beliefs.adjust_suspicion(other_player_id, delta=BODY_PROXIMITY_SUSPICION_DELTA)` for every other player who was in that room during the window.
- [ ] **`agents/perception.py::ingest_packet`** (or whichever function processes an `ObservationPacket` into memory updates — implementing agent identifies the right call site) invokes `apply_observation_rules` with the current packet + a co-presence map derived from the agent's episodic store. The episodic store's existing query API is used; do NOT add new episodic methods if existing ones suffice.
- [ ] **`tests/agents/test_perception.py` integration test.** Scripted scenario: observing agent witnesses a vent use by another player at tick 5; assert the observing agent's `BeliefState.view(venter).suspicion >= 0.5 + epsilon` after ingestion.
- [ ] **`tests/agents/test_perception.py` second test.** Scripted scenario: observing agent finds a body at tick 8 in room R; the agent was co-located with player X in room R at tick 6 (within the 3-tick window) and with player Y in room R at tick 4 (outside the window). Assert X's suspicion is elevated; Y's suspicion is unchanged at default 0.5.
- [ ] **`tests/agents/test_beliefs.py` unit test** asserts `apply_observation_rules` is a pure function: given identical inputs it returns equal `BeliefState`s; the input `BeliefState` is not mutated.
- [ ] **Loader/API integration.** After this task, a manual `curl /replays/headless-seed-22/meetings/.../memory/p-2 | jq '.beliefs'` returns a non-empty array for at least one agent (the one who witnessed the body discovery in seed 22, which triggered the meeting). Document the curl + response in `## Decisions` of the PR.
- [ ] **No leaks.** Belief rules read only from the agent's own packet and own episodic memory — never from engine state or other agents' beliefs. The firewall is unchanged. `uv run lint-imports` passes.
- [ ] **`mypy --strict`** on `agents/` continues to pass.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — Read [agents/memory/beliefs.py](agents/memory/beliefs.py) to confirm `BeliefState`'s existing mutation API (`adjust_suspicion`, `adjust_trust`) returns a new `BeliefState` (frozen dataclass per Phase 2 design). The new function chains those mutations.

Step 2 — Read [agents/perception.py](agents/perception.py) to find the per-packet ingestion entry point. The substrate report from the mid-phase DTO audit noted this function exists and is called by the loader's `_ingest_tick` ([api/replay_loader.py:471](api/replay_loader.py#L471)).

Step 3 — Read [observation/packet.py](observation/packet.py) to confirm the field names for vent-use events and body sightings. The cleanest detection of "newly-discovered body" is comparing `current_packet.visible_bodies` to `previous_packet.visible_bodies`; the perception module already tracks the prior packet for similar diffs (verify).

Step 4 — Implement `apply_observation_rules`:

```python
# agents/memory/beliefs.py — illustrative
def apply_observation_rules(
    beliefs: BeliefState,
    *,
    observation: ObservationPacket,
    previous_visible_bodies: Set[BodyId],
    recent_co_presence: Mapping[RoomId, Sequence[tuple[int, PlayerId]]],
) -> BeliefState:
    """Apply DESIGN.md §6.3 rule-based belief updates (Rules 1 + 4)."""
    result = beliefs
    # Rule 4 — observed venting
    for event in observation.audible_events:
        if event.kind == "vent_use":
            result = result.adjust_suspicion(
                event.subject, delta=VENTING_SUSPICION_DELTA,
            )
    # Rule 1 — body proximity (new bodies only)
    new_bodies = [
        body for body in observation.visible_bodies
        if body.body_id not in previous_visible_bodies
    ]
    for body in new_bodies:
        for tick, player_id in recent_co_presence.get(body.room, ()):
            if observation.tick - tick <= BODY_PROXIMITY_WINDOW_TICKS:
                result = result.adjust_suspicion(
                    player_id, delta=BODY_PROXIMITY_SUSPICION_DELTA,
                )
    return result
```

Step 5 — Wire into `ingest_packet`:

```python
# agents/perception.py — illustrative
def ingest_packet(self, packet: ObservationPacket) -> None:
    # ... existing episodic ingestion ...
    co_presence = self._episodic.co_presence_by_room(
        from_tick=packet.tick - BODY_PROXIMITY_WINDOW_TICKS,
        to_tick=packet.tick - 1,
    )
    previous_bodies = self._previous_visible_body_ids
    self._beliefs = apply_observation_rules(
        self._beliefs,
        observation=packet,
        previous_visible_bodies=previous_bodies,
        recent_co_presence=co_presence,
    )
    self._previous_visible_body_ids = {b.body_id for b in packet.visible_bodies}
```

If `co_presence_by_room` doesn't exist on the episodic store, add it OR derive co-presence inline from the existing query API.

Step 6 — Tests. The integration tests should be against synthetic scripted scenarios, not real replays — keeps them deterministic and fast.

Step 7 — End-to-end smoke. Boot the API, curl `/replays/headless-seed-22/meetings/.../memory/p-3` (or whichever agent discovered the body for the meeting that fires in seed 22), assert `beliefs` is non-empty. Paste the curl + JSON snippet in `## Decisions`.

## Public types this task introduces
- `agents.memory.beliefs.apply_observation_rules`
- `agents.memory.beliefs.VENTING_SUSPICION_DELTA`
- `agents.memory.beliefs.BODY_PROXIMITY_SUSPICION_DELTA`
- `agents.memory.beliefs.BODY_PROXIMITY_WINDOW_TICKS`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-4-belief-rule-wiring` with a title like `task 4.14: belief-rule wiring for observed venting and body proximity (pre-ux-session finding 2)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §6.3, DESIGN.md §6.6, mid-phase DTO audit R-2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
