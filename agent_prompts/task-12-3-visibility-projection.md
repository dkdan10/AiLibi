# Agent Prompt — 12.3 Per-tick visibility projection + UI leak test

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.3 — Per-tick visibility projection + UI leak test, anchored to design/phase-12/stage-1-design.md §3.2 (fog), §7 (the visibility row of the view-model table), slice 1b; design/phase-12/stage-0-understand.md §0.5 (fog is the one genuinely-expensive projection); the firewall rules in design/phase-12/claude-design-brief.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-visibility-projection`
**Depends on:** 12.2
**Section refs:** design/phase-12/stage-1-design.md §3.2 (fog), §7 (the visibility row of the view-model table), slice 1b; design/phase-12/stage-0-understand.md §0.5 (fog is the one genuinely-expensive projection); the firewall rules in design/phase-12/claude-design-brief.md
**Complexity:** Integration
**Files in scope:**
- api/replay_loader.py
- api/schemas.py
- frontend/src/types/api.ts
- tests/api/test_leak.py
- tests/api/test_view_model.py
**Files NOT in scope:**
- the map render layer + fog *rendering* — Task 12.5 consumes this projection
- engine/ and observation/ — read `compute_visibility_for_player` / the `ObservationPacket`; never change them; no re-record
- the per-meeting belief / contradiction / §4.6 projections — already shipped in 12.2

A hand-coded backend/loader projection (no Claude Design), deliberately isolated as the one genuinely-expensive compute so
it does not block the cheap 12.2 contract. Persist each living agent's per-tick **field of view** into the view-model so
the As-agent perspective can *simulate* the firewall rather than inherit it. Today `ReplayLoader._walk(collect_memory=True)` runs the full observation pipeline but
routes its audit to a throwaway `tempfile.TemporaryDirectory` and **discards the visibility** — only an `is_venting` bool
survived per tick (see the VentEventView note in `api/schemas.py` that explicitly reserves this for Task 12.3). Capture,
per tick per living agent, each agent's already-firewall-filtered observation packet — `visible_players` / `visible_bodies` (the visual field, from
`engine/visibility.py::compute_visibility_for_player`, graph- and lights-dependent; a naive same-room dim is both wrong
AND a leak) plus `audible_events` (a *separate* audio path, `ObservationService._audible_events` — vent-use-heard /
sabotage-alarm) — all of which `observation/service.py` already assembles per tick, and surface it as a per-tick
`AgentVisibilityView` attached to the agent's tick state. This is **the one genuinely-expensive new compute** (a visibility solve per living agent per tick):
reuse the pipeline output already produced inside the re-walk instead of re-solving, cost it honestly, and cache through
the existing LRU (window it like the other per-tick frames if it inflates the single payload). Ship a **UI leak test** in
`tests/api/test_leak.py` mirroring `eval/leak_test.py`'s recursive hidden-field walk: build the As-agent–filtered view for
a chosen agent across a committed 9p2i game and assert it never exposes a player, body, event, or field that agent could
not have seen at that tick (other-room presence, role, `fellow_impostor_ids`, kill attribution). The projection is a pure
function of the recorded actions — keep it byte-deterministic.
**Definition of done:** per-tick per-living-agent `visible_players` / `visible_bodies` / `audible_events` in the served
view-model, derived from `compute_visibility_for_player` (not same-room shorthand); a **UI leak test** mirroring
`eval/leak_test.py` asserts the As-agent filtered view leaks no unseen field across a committed 9p2i game; the projection
is cached + cost-bounded (no per-request recompute) and documented as the expensive one; the existing leak + determinism
tests stay green; NO re-record; `scripts/check.sh` is green.

## Implementation hint
capture the packet the observation pipeline already builds inside the `collect_memory=True` re-walk — read its
`visible_players` / `visible_bodies` / `audible_events` instead of letting the temp-dir audit drop them; do NOT re-solve
visibility a second time. The As-agent view is a server-side projection (compute once, cache), never a client-side hide;
window the per-tick payload as the existing per-tick frames are windowed if it grows.

## Public types this task introduces
- `api.schemas.AgentVisibilityView`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk
this is the cost hotspot — a visibility solve per living agent per tick across a whole game; measure and cache or it
regresses load time. The leak surface is the entire point: the test must mirror `eval/leak_test.py`'s recursive
hidden-field walk (role, `fellow_impostor_ids`, kill attribution, cross-room presence) or a subtle leak ships. Reading the
engine visibility / observation modules must not perturb the engine walk — the existing leak + determinism tests must stay
green and the replays are not re-recorded.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-12-visibility-projection` with a title like `task 12.3: per-tick visibility projection + ui leak test`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §3.2 (fog), §7 (the visibility row of the view-model table), slice 1b; design/phase-12/stage-0-understand.md §0.5 (fog is the one genuinely-expensive projection); the firewall rules in design/phase-12/claude-design-brief.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
