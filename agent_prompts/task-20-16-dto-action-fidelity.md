# Agent Prompt — 20.16 Spectator action fidelity: PRETEND_TASK, EMERGENCY, REPAIR, BLOCKED in the DTO; every fetch through the client

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.16 — Spectator action fidelity: PRETEND_TASK, EMERGENCY, REPAIR, BLOCKED in the DTO; every fetch through the client, anchored to audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/s2-movement-positions.md §"BUG — B3" and §2.3; audits/review-2026-08-19/B/collated-findings.md §C-8; audits/review-2026-08-19/B/frontend-a.md §F2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 1.10 and the sequencing-hazard note beneath the wave table; audits/review-2026-08-19/D/cross-track-map.md §G-38, §C-8. Anchors re-verified at HEAD: api/replay_loader.py:2208-2228 (`_current_action`, keyed on `last_action` alone), :1487 (its only call site), :1420-1433 (`_tick_view`), :1150-1151 (the walk that already holds the tick's deserialized `actions`); api/schemas.py:249-251 (the inline seven-value `Literal`), :49 (`VIEW_MODEL_VERSION = "1"`), :622 (the `EvidenceCategory` TypeAlias pattern to mirror); engine/tick.py:215-220 (`_with_actor_last_action` — only an ACCEPTED action updates the label), :271-306 (`_apply_do_task` rejects an actor that owns no instance of the map task, at :290-293), :382 (a killed victim's `last_action` is cleared), :593-604 (rejections become `ActionRejectedEvent`; a `MEETING` phase change returns early and silently DROPS every later action in the list); engine/events.py:146-151 (`MeetingTriggeredEvent.actor`), :28-33 (`ActionRejectedEvent.actor` / `.action`); observation/service.py:435-436 + :438-455 (the fake-task lever keys the crew's `action="task"` off exactly that rejection event); scripts/gen_frontend_types.py:94 (the `AgentAction` alias tuple); frontend/src/types/api.ts:22, :25, :116; frontend/src/assets/map/glyphs.ts:66-77 (`ACTION_GLYPH` is an exhaustive `Record` over the alias); frontend/src/components/MapView.tsx:495-498 (`selfActionGlyph`), :672 (omniscient tokens), :686 (the fog view's SELF token); frontend/src/api/client.ts:117-133 (`assertViewModelVersion`), :135-159 (`getJson`, module-private), :319-321 (`getRubric`); frontend/src/components/TournamentDashboard.tsx:1025-1060; frontend/src/components/BeliefMatrix.tsx:33-48; tests/api/test_replay_loader.py:131.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-dto-action-fidelity`
**Depends on:** 20.1, 20.2, 20.4, 20.7 — the map's body layer and its pure-derivation split land first, so the glyph work here sits on the restructured component instead of racing it; the dashboard's product-copy pass lands first, so rewriting its data fetch is a mechanical change against settled copy; the loader's corrupt-file resilience fix lands first because both changes edit the loader and the same loader test module; and the static bundle's Tournament empty-state card lands first, so routing the dashboard through the typed client preserves exactly the missing-report behaviour the bundle relies on.
**Section refs:** audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/s2-movement-positions.md §"BUG — B3" and §2.3; audits/review-2026-08-19/B/collated-findings.md §C-8; audits/review-2026-08-19/B/frontend-a.md §F2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 1.10 and the sequencing-hazard note beneath the wave table; audits/review-2026-08-19/D/cross-track-map.md §G-38, §C-8. Anchors re-verified at HEAD: api/replay_loader.py:2208-2228 (`_current_action`, keyed on `last_action` alone), :1487 (its only call site), :1420-1433 (`_tick_view`), :1150-1151 (the walk that already holds the tick's deserialized `actions`); api/schemas.py:249-251 (the inline seven-value `Literal`), :49 (`VIEW_MODEL_VERSION = "1"`), :622 (the `EvidenceCategory` TypeAlias pattern to mirror); engine/tick.py:215-220 (`_with_actor_last_action` — only an ACCEPTED action updates the label), :271-306 (`_apply_do_task` rejects an actor that owns no instance of the map task, at :290-293), :382 (a killed victim's `last_action` is cleared), :593-604 (rejections become `ActionRejectedEvent`; a `MEETING` phase change returns early and silently DROPS every later action in the list); engine/events.py:146-151 (`MeetingTriggeredEvent.actor`), :28-33 (`ActionRejectedEvent.actor` / `.action`); observation/service.py:435-436 + :438-455 (the fake-task lever keys the crew's `action="task"` off exactly that rejection event); scripts/gen_frontend_types.py:94 (the `AgentAction` alias tuple); frontend/src/types/api.ts:22, :25, :116; frontend/src/assets/map/glyphs.ts:66-77 (`ACTION_GLYPH` is an exhaustive `Record` over the alias); frontend/src/components/MapView.tsx:495-498 (`selfActionGlyph`), :672 (omniscient tokens), :686 (the fog view's SELF token); frontend/src/api/client.ts:117-133 (`assertViewModelVersion`), :135-159 (`getJson`, module-private), :319-321 (`getRubric`); frontend/src/components/TournamentDashboard.tsx:1025-1060; frontend/src/components/BeliefMatrix.tsx:33-48; tests/api/test_replay_loader.py:131.
**Complexity:** Medium
**Record impact:** none — the projection is read-side only: no recorded `actions` row, no engine transition and no `state_hash` moves, so nothing here is re-recorded and no committed replay changes.
**Measurement:** `uv run pytest tests/api/test_replay_loader.py tests/api/test_view_model.py -q` green with the action-class census pinned over `replays/samples/9p2i` (415 impostor `do_task` intents leave the stale-label classes: IDLE 0 / MOVING 0 / TASK 0, with at most 5 of them landing on BLOCKED; 19 EMERGENCY; 114 REPAIR); `uv run python scripts/gen_frontend_types.py --check` clean; `cd frontend && npm run tsc:check && npm run test` green; and `grep -rn 'fetch(' frontend/src --include='*.tsx' --include='*.ts' | grep -v src/api/client | grep -v '.test.'` prints nothing (it prints exactly 2 lines at HEAD).

The spectator's `current_action` reports the last action the engine ACCEPTED, not the action
the agent took, and four whole classes of behaviour are therefore rendered as a lie.
`engine/tick.py:215-220` only stamps `last_action` from inside a successful handler, so a
rejected or dropped intent leaves the previous tick's label standing; `_current_action` at
api/replay_loader.py:2208 then reads that stale label and collapses `emergency` into REPORT
and `repair_sabotage` into TASK on top. The A-track census
(audits/review-2026-08-19/A/s2-movement-positions.md §"BUG — B3") measured the damage over
the 300 committed games: 1,747 impostor fake `do_task` intents render IDLE 800 / MOVING 844
/ **TASK 0**; 112 emergency-button presses render REPORT; 408 `repair_sabotage` intents
render TASK 302 / MOVING 95 / IDLE 11; and 1,964 agent-ticks show MOVING while the token
does not move. Those three intent totals were recomputed at HEAD from the committed replay
bytes for this contract and match exactly (1,747 / 112 / 408 across
`replays/samples/{9p2i,4p1i}` and `replays/ml_corpus/{9p2i,4p1i}`); over
`replays/samples/9p2i` alone the same census reads 415 / 19 / 114.

The fake-task case is the one that costs the project something.
`observation/service.py:435-455` already keys the crew's witnessed `action="task"` off the
very `ActionRejectedEvent` the impostor's `do_task` produces — a co-located crewmate
correctly sees the impostor working, which is the point of the fake-task lever — while the
omniscient spectator dump shows the same agent aimlessly MOVING. The replay viewer, whose
whole job since Phase 12 is to make the deception legible, is blind at exactly the moments
the deception is succeeding. Every byte needed to fix this is already recorded: the per-tick
`actions` array carries every submitted intent including the rejected ones, and the walk at
api/replay_loader.py:1150-1151 already has it in hand and throws it away. This is a
projection bug, not a data gap.

The fix is additive and mechanical: name the DTO field's value set
(`api.schemas.CurrentAction`, mirroring the `EvidenceCategory` TypeAlias at
api/schemas.py:622), add PRETEND_TASK, EMERGENCY, REPAIR and BLOCKED, and derive the label
from THIS tick's recorded intent plus its outcome instead of from the last accepted action.
A label can then never be stale: the "MOVING while standing still" class disappears by
construction rather than by patching, because the projection no longer has a previous tick
to inherit from.

Changing the DTO bumps `VIEW_MODEL_VERSION`, and that is what forces the second half of this
task into the same PR. `VIEW_MODEL_VERSION` has never been bumped, so C-8 has been latent:
`frontend/src/api/client.ts:117-133` is the one runtime check standing between a
version-skewed server and silently-wrong UI, and two components skip it with a bare `fetch`
— `TournamentDashboard.tsx:1028` re-implements `getRubric` by hand for one of only two
stamped payloads, and `BeliefMatrix.tsx:42` does the same for an endpoint the client has no
getter for (audits/review-2026-08-19/B/frontend-a.md §F2; the grep returns exactly those two
lines at HEAD). On the first bump, a stale build talking to a fresh server fails loud in the
tour and the picker and renders a thousand lines of statistics from foreign bytes in the
dashboard. Shipping the bump without the routing fix would be shipping the failure mode;
audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 1.10 names them as one item for exactly
this reason.

**Files in scope:**
- api/replay_loader.py; (`_current_action` derives PRETEND_TASK / EMERGENCY / REPAIR / BLOCKED from the recorded intent + outcome)
- api/schemas.py; (the CurrentAction enum; viewModelVersion bump)
- frontend/src/types/api.ts; (regenerated by scripts/gen_frontend_types.py --check)
- frontend/src/types/api.fidelity.ts; (same)
- frontend/src/components/AgentToken.tsx; (glyphs for the new classes)
- frontend/src/components/MapView.tsx; (selfActionGlyph mapping)
- frontend/src/components/TournamentDashboard.tsx; (the raw fetch routed through api/client getRubric/getJson)
- frontend/src/components/BeliefMatrix.tsx; (same)
- frontend/src/api/client.ts; (a shared getJson with the version guard if missing)
- frontend/src/api/client.test.ts
- tests/api/test_replay_loader.py; (the four action classes pinned over the committed samples/9p2i replays: 415 impostor fake tasks → PRETEND_TASK, of the 1,747 corpus-wide; emergency → EMERGENCY; meeting-frozen move → BLOCKED)
- tests/api/test_view_model.py; (the version bump pin)
- frontend/src/assets/map/glyphs.ts; (ACTION_GLYPH gains the four classes; the alias rename lands here)
- scripts/gen_frontend_types.py; (the _ENUM_ALIASES entry for the widened action enum)

**Files NOT in scope:**
- engine/ and observation/ (the recorded actions already carry the intent; this is a DTO projection and no engine byte moves)
- meetings/ (no transcript change)
- the As-agent fog layer's witnessed actions (unchanged: co-located crew already see `task` for a fake task, via `visibility.visible_players[].action`, which is a different field from `current_action`)
- frontend/src/assets/map/*.svg (the four new classes reuse committed glyph assets; no new artwork here)
- scripts/build_demo_bundle.py (the bundle bakes payloads at build time and pins no version of its own)
- eslint.config.js (the no-raw-fetch guard ships as an executable test, not a lint-config edit)
- agents/strategic/prompts/ (a prompt-template edit belongs only to the single Phase-20 prompt-set bump, never here)

**Definition of done:**
- [ ] `api.schemas.CurrentAction` exists as a documented `TypeAlias = Literal[...]` in the
  shape of `EvidenceCategory`, carries the seven existing values plus PRETEND_TASK,
  EMERGENCY, REPAIR and BLOCKED, and `AgentTickStateView.current_action` is annotated with
  it instead of the inline literal; the docstring states that the label describes THIS
  tick's recorded intent and its outcome, never the last accepted action.
- [ ] `_current_action` derives the label from the tick's recorded action for that actor
  plus this tick's events, under a stated precedence: an intent the engine never attempted
  (positioned after the tick's `MeetingTriggeredEvent` actor) or rejected because the actor
  died earlier in the same tick → BLOCKED; an impostor `do_task` → PRETEND_TASK; any other
  rejected intent → BLOCKED; an accepted `emergency` → EMERGENCY, `repair_sabotage` →
  REPAIR, and the existing five mappings unchanged; no recorded intent for that actor this
  tick (a dead agent, the synthesized Start frame) → IDLE.
- [ ] The census is pinned in `tests/api/test_replay_loader.py` over the committed
  `replays/samples/9p2i` set: all 415 impostor `do_task` intents leave the stale-label
  classes (IDLE 0 / MOVING 0 / TASK 0 for that intent), at most 5 of them read BLOCKED (the
  intents sharing a tick with an earlier meeting trigger) and the rest read PRETEND_TASK; 19
  agent-ticks read EMERGENCY and 114 read REPAIR; and no agent-tick anywhere in the walk
  carries a label inherited from a previous tick. The PR quotes the produced census table.
- [ ] The gate bites: a unit test builds a tick in which an impostor submits `do_task` and
  asserts PRETEND_TASK, and asserts that the pre-fix derivation (the actor's `last_action`
  at that moment) would have produced a DIFFERENT label — so reverting the projection fails
  the test rather than passing it silently.
- [ ] `VIEW_MODEL_VERSION` is bumped in api/schemas.py; `tests/api/test_view_model.py` pins
  the new value and its lockstep appearance in the regenerated `frontend/src/types/api.ts`;
  `uv run python scripts/gen_frontend_types.py --check` is clean with `api.ts` and
  `api.fidelity.ts` committed.
- [ ] The generated TypeScript alias and the Python alias carry ONE name — `CurrentAction` —
  with all eleven values, and every consumer of the old `AgentAction` alias is updated;
  nothing in the frontend indexes the action set with a mapping that silently omits a value
  (an exhaustive mapping stays exhaustive and fails to compile if a value is added later).
- [ ] The map renders the new classes with committed glyph assets and no new artwork:
  PRETEND_TASK and BLOCKED are drawn as an INTENT (a hollow chip variant on `AgentToken`,
  glyphs `task` and `idle` respectively), EMERGENCY and REPAIR as resolved outcomes (solid
  chip, glyphs `report` and `task`); IDLE still draws nothing. The As-agent view is
  byte-for-byte unchanged: the fog branch still reads `witnessedActionGlyph(vp.action)` for
  every other agent and only the selected agent's own token reads `current_action`.
- [ ] `TournamentDashboard` uses `getRubric(seedSet)` with `err instanceof ApiError &&
  err.status === 404` for the absent-rubric state (the pattern `ReplayPicker` already uses),
  and `BeliefMatrix` uses a new exported `getBeliefFrames(gameId, set)` on `api/client.ts`;
  neither component constructs a URL or calls `fetch` any more.
- [ ] `frontend/src/api/client.test.ts` asserts that a stamped-but-skewed payload throws
  `ViewModelVersionError` through BOTH newly-routed getters, that a non-200 from the belief
  route throws `ApiError` rather than a bare `Error`, and — as a source scan over
  `frontend/src` — that no file outside `src/api/client.ts` calls `fetch(`; the scanner is
  exercised against a planted fixture string so it is proven to bite. The belief payload is
  a bare array and therefore carries no stamp today: the test says so explicitly rather than
  implying a guard that is a no-op on that shape.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read the outcome, not the state. The walk at api/replay_loader.py:1150-1151 already
holds both halves: `actions` (the deserialized recorded intents for this tick) and `events`
(what `advance_tick` did with them). Thread `actions` through `_tick_view` as a keyword
argument alongside the events it already receives, and build one small per-tick lookup
before projecting the agents — actor to submitted action, plus the set of actors carrying an
`ActionRejectedEvent`, plus the drop cut-off. The synthesized Start frame at :1131 passes an
empty sequence and every agent stays IDLE, which is what tests/api/test_replay_loader.py:131
already pins.

Step 2 — the drop rule is exact, not heuristic. `advance_tick` returns the moment a handler
flips the phase to MEETING (engine/tick.py:599-600), so every action positioned strictly
AFTER the triggering actor's action in the recorded list was never attempted and emitted no
event at all. `MeetingTriggeredEvent.actor` names the trigger, so the cut-off is the index
of that actor's action in `actions`. Over `replays/samples/9p2i` this is what puts up to 227
move intents and up to 5 impostor `do_task` intents into BLOCKED; measure the real split
rather than asserting these bounds.

Step 3 — PRETEND_TASK reads the same evidence the fog layer reads. An impostor owns no task
instance, so `_apply_do_task` always rejects it (engine/tick.py:290-293) and
observation/service.py:435-436 turns that same `ActionRejectedEvent` into the crew's
`action="task"`. Deriving PRETEND_TASK from the recorded intent plus the actor's role keeps
the two projections describing one event; say so in a comment so nobody later "fixes" one
side alone. Role is on `state.players[pid].role`, already used two lines away by
`_task_progress`.

Step 4 — no new leak. `AgentTickStateView` is the omniscient spectator DTO and
`ReplayView.players[].role` is already served, so PRETEND_TASK exposes nothing new; the
firewall question is only whether an As-agent perspective can reach it. MapView.tsx:686
reads `current_action` for the SELECTED agent's own token and MapView.tsx:693-701 reads
`visibility.visible_players[].action` for everyone else, so the answer today is no — keep it
that way and assert it in the test rather than in prose.

Step 5 — the version bump is a two-file lockstep plus a regeneration. `api/schemas.py:49` is
the source; `frontend/src/types/api.ts:22` is generated from it; the fidelity fixture at
frontend/src/types/api.fidelity.ts is rebuilt by the same script from a 4p1i game that
submits no actions, so its only diff should be the stamp string. If more than the stamp
changes there, stop and understand why before committing it.

Step 6 — grep the blast radius before touching the alias. At HEAD exactly one file imports
the generated action alias (the map's glyph registry) and one story types a prop off
`AgentTickStateView["current_action"]`; `tests/api/test_schemas.py` constructs views with
existing values and stays valid because the change is additive. If your grep finds a
consumer outside the files in scope, stop and ask rather than widening.

Step 7 — the client is the only place that knows a URL. Copy `ReplayPicker`'s existing 404
handling into the dashboard rather than inventing a second shape, and give the belief route
a real getter next to `getMemory` instead of exporting `getJson` raw — an exported `getJson`
is a new bypass wearing a seatbelt.

## Public types this task introduces
- `api.schemas.CurrentAction`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-20-dto-action-fidelity` with a title like `task 20.16: spectator action fidelity: pretend_task, emergency, repair, blocked in the dto; every fetch through the client`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/s2-movement-positions.md §"BUG — B3" and §2.3; audits/review-2026-08-19/B/collated-findings.md §C-8; audits/review-2026-08-19/B/frontend-a.md §F2; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 1.10 and the sequencing-hazard note beneath the wave table; audits/review-2026-08-19/D/cross-track-map.md §G-38, §C-8. Anchors re-verified at HEAD: api/replay_loader.py:2208-2228 (`_current_action`, keyed on `last_action` alone), :1487 (its only call site), :1420-1433 (`_tick_view`), :1150-1151 (the walk that already holds the tick's deserialized `actions`); api/schemas.py:249-251 (the inline seven-value `Literal`), :49 (`VIEW_MODEL_VERSION = "1"`), :622 (the `EvidenceCategory` TypeAlias pattern to mirror); engine/tick.py:215-220 (`_with_actor_last_action` — only an ACCEPTED action updates the label), :271-306 (`_apply_do_task` rejects an actor that owns no instance of the map task, at :290-293), :382 (a killed victim's `last_action` is cleared), :593-604 (rejections become `ActionRejectedEvent`; a `MEETING` phase change returns early and silently DROPS every later action in the list); engine/events.py:146-151 (`MeetingTriggeredEvent.actor`), :28-33 (`ActionRejectedEvent.actor` / `.action`); observation/service.py:435-436 + :438-455 (the fake-task lever keys the crew's `action="task"` off exactly that rejection event); scripts/gen_frontend_types.py:94 (the `AgentAction` alias tuple); frontend/src/types/api.ts:22, :25, :116; frontend/src/assets/map/glyphs.ts:66-77 (`ACTION_GLYPH` is an exhaustive `Record` over the alias); frontend/src/components/MapView.tsx:495-498 (`selfActionGlyph`), :672 (omniscient tokens), :686 (the fog view's SELF token); frontend/src/api/client.ts:117-133 (`assertViewModelVersion`), :135-159 (`getJson`, module-private), :319-321 (`getRubric`); frontend/src/components/TournamentDashboard.tsx:1025-1060; frontend/src/components/BeliefMatrix.tsx:33-48; tests/api/test_replay_loader.py:131.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
