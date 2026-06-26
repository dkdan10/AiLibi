# Agent Prompt — 13.5.4 Movement perception (perceive room transitions; wire last_seen)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.5.4 — Movement perception (perceive room transitions; wire last_seen), anchored to the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`: "movement is never perceived — agents learn only an actor's CURRENT room; the engine emits `MovedEvent` + maintains `last_action` but the observation layer reads neither"); engine/tick.py (`MovedEvent` from_room/to_room ~:261-267, `PlayerState.last_action`); observation/service.py (`_observed_actions_for_agent`, the witness gate); observation/packet.py (`PlayerView`); agents/perception.py (`ingest_packet`, the `EVENT_*` types); agents/memory/store.py (`render_for_prompt`, the existing within-vision `_collect_transitions` / `_SALIENCE_TRANSITION` + `_collect_movement_breadcrumbs`, and the dead `last_seen` render hook ~:1323); agents/memory/working.py (`record_sighting` / `last_seen`, dead — wired here, earmarked by 13.5.1). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-5-movement-perception`
**Depends on:** 13.5.1, 13.5.2
**Section refs:** the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`: "movement is never perceived — agents learn only an actor's CURRENT room; the engine emits `MovedEvent` + maintains `last_action` but the observation layer reads neither"); engine/tick.py (`MovedEvent` from_room/to_room ~:261-267, `PlayerState.last_action`); observation/service.py (`_observed_actions_for_agent`, the witness gate); observation/packet.py (`PlayerView`); agents/perception.py (`ingest_packet`, the `EVENT_*` types); agents/memory/store.py (`render_for_prompt`, the existing within-vision `_collect_transitions` / `_SALIENCE_TRANSITION` + `_collect_movement_breadcrumbs`, and the dead `last_seen` render hook ~:1323); agents/memory/working.py (`record_sighting` / `last_seen`, dead — wired here, earmarked by 13.5.1)
**Complexity:** Integration
**Files in scope:**
- observation/service.py
- observation/packet.py
- agents/perception.py
- agents/memory/store.py
- agents/memory/working.py
- tests/observation/test_service.py
- tests/agents/test_perception.py
- tests/agents/test_memory_rendering.py
**Files NOT in scope:**
- agents/memory/beliefs.py and meetings/transcript.py — movement here is PERCEPTION + RENDER only; NO belief rule and NO detector change, which is what keeps this task file-disjoint from 13.5.3 so the two dispatch in parallel. A movement-driven belief/contradiction rule is a deliberate later item.
- orchestrator/game.py, meetings/manager.py — disjoint from 13.5.5
- the scalar belief path and the §4.6 gate — untouched
- engine/ and the recorded replays — observation reads the EXISTING `MovedEvent`; NO engine change, NO re-record

Today an agent perceives only a position SNAPSHOT (the actor's current room); the engine's
`MovedEvent` (room→room each tick) and `last_action` are never read, so a witness cannot perceive a
transition it directly saw, and the `WorkingMemory.last_seen` field (dead since Phase 2) never
populates. The render reconstructs coarse "moved from A" breadcrumbs from consecutive `saw_player`
deltas (Tasks 13.6/13.9), but a single-tick transit the agent witnessed is lost. This task surfaces
witnessed movement: `observation/service.py` derives a movement signal for a CO-LOCATED witness
from the engine `MovedEvent` (an actor the witness can see moving room→room), `agents/perception.py`
ingests it as a new first-hand event, `agents/memory/store.py` renders "You saw p-3 move from
CAFETERIA to ADMIN at tick 5", and the same path calls `working.record_sighting` → the now-live
"last seen in ROOM at tick T" belief-line suffix. Behind `AILIBI_MOVEMENT_PERCEPTION` (default OFF →
no movement event, `record_sighting` uncalled, render byte-identical to HEAD).

**Definition of done:** with the flag ON, a witness who could see an actor transition rooms gets a
first-hand perceived-movement episodic event (witness-gated exactly like `saw_player` — never for an
observer who could not see the actor, so no firewall/leak regression), rendered as a first-hand
sighting-class line; `working.last_seen` is populated via `record_sighting`, so the "last seen in
ROOM at tick T" belief suffix finally renders. Replay-deterministic: the movement signal is
re-derived from the recorded `MovedEvent` on the replay path, so committed replays reconstruct
byte-identically (`scripts/verify_samples.sh`). Flag OFF → every packet, episodic store, and memory
render is byte-identical to pre-task HEAD; the existing within-vision transition/breadcrumb renders
are unchanged. NO `agents/memory/beliefs.py` or `meetings/transcript.py` edit (the parallel-safety
boundary). New tests cover the witness gate, the movement render, the `last_seen` wiring, flag-off
byte-identity, and determinism. Full `scripts/check.sh` green; a 9B smoke (flag ON) shows the leak
suite passing and the render within the 1500-tok budget.

## Implementation hint
Mirror the `saw_player` witness gate: surface movement only for an observer already entitled to see
the actor (reuse the same visibility/witness path `_observed_actions_for_agent` uses), so the §4.7
firewall and the leak suite hold for free. Carry the transition on a new `observation/packet.py`
field (e.g. a `moved_from` on `PlayerView` or a small `moved_players` list) and ingest it in
`ingest_packet` as a new `EVENT_*`; gate the `record_sighting` call on the flag so `last_seen` stays
empty (and its suffix absent) when OFF — that is the byte-identity boundary. Salience is first-hand
class (a witnessed transition is direct observation, distinct from the reconstructed
`_SALIENCE_TRANSITION` breadcrumb). Keep `agents/` engine-free (read the engine `MovedEvent` only in
`observation/service.py`, the orchestrator-owned boundary). Run a memory-render fixture before/after
with the flag OFF to confirm byte-identity.

## Integration risk
A new first-hand perception channel + the first live writer of `WorkingMemory.last_seen`. The
firewall/leak surface is the main risk: movement MUST be witness-gated identically to `saw_player`
(a movement the observer could not see must never appear), so the leak suite is the hard gate.
Behind `AILIBI_MOVEMENT_PERCEPTION` (default OFF) so the merge is byte-identical and committed
replays are untouched; determinism holds because the signal re-derives from the recorded
`MovedEvent`. File-disjoint from 13.5.3 and 13.5.5 by construction (no `beliefs.py` / `transcript.py`
/ `game.py` / `manager.py`), so all three dispatch in parallel. No re-record (smoke only).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import agents.perception"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-13-5-movement-perception` with a title like `task 13.5.4: movement perception (perceive room transitions; wire last_seen)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`: "movement is never perceived — agents learn only an actor's CURRENT room; the engine emits `MovedEvent` + maintains `last_action` but the observation layer reads neither"); engine/tick.py (`MovedEvent` from_room/to_room ~:261-267, `PlayerState.last_action`); observation/service.py (`_observed_actions_for_agent`, the witness gate); observation/packet.py (`PlayerView`); agents/perception.py (`ingest_packet`, the `EVENT_*` types); agents/memory/store.py (`render_for_prompt`, the existing within-vision `_collect_transitions` / `_SALIENCE_TRANSITION` + `_collect_movement_breadcrumbs`, and the dead `last_seen` render hook ~:1323); agents/memory/working.py (`record_sighting` / `last_seen`, dead — wired here, earmarked by 13.5.1)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
