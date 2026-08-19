# Agent Prompt — 15.3 Information-funnel diagnostics: commit the oracle / possession / transmission folds

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.3 — Information-funnel diagnostics: commit the oracle / possession / transmission folds, anchored to tasks/post-phase-14-clean-up.md §2 (the charter measurement this task reproduces), H3; api/replay_loader.py:804-1035 (the `_walk` reconstruction recipe); orchestrator/seeder.py; engine/visibility.py:98-127 (crew same-room-only vision); meetings/manager.py:1821-1870 (the opt-in eligibility gate). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-funnel-diagnostics`
**Depends on:** 15.1
**Section refs:** tasks/post-phase-14-clean-up.md §2 (the charter measurement this task reproduces), H3; api/replay_loader.py:804-1035 (the `_walk` reconstruction recipe); orchestrator/seeder.py; engine/visibility.py:98-127 (crew same-room-only vision); meetings/manager.py:1821-1870 (the opt-in eligibility gate)
**Complexity:** Medium

Promote the clean-up charter's three-stage information measurement into committed, reusable `eval/`
folds, so Wave 0's effect is measured by the same instrument before and after, forever. Stage 1
(EXISTENCE): the pooled-testimony oracle — re-seed each game, replay recorded actions through
`advance_tick` + `apply_meeting_result` with per-tick state-hash verification, and compute, at each
body-report meeting, the killer-candidate set under perfect sharing of every living crew member's
legitimate same-room sightings (alibi-elimination at the kill tick, plus the ±1-tick window variant).
Stage 2 (POSSESSION): the held-clue census per meeting — kill witnessed, killer placed at scene, victim
last-seen-with-killer, impostor vent witnessed. Stage 3 (TRANSMISSION): what reached the meeting —
structured killer-placement observations, vent mentions, killer accused, speakers-vs-holders, votes
inside/outside the oracle candidate set, and the reporter-ejection census. Output: per-set + per-meeting
`--json` rows through a `scripts/measure_baseline.py --funnel` section. The charter's baseline-2 table
is this task's reproduction gate.

**Files in scope:**
- eval/funnel.py (new: the walk + the three-stage folds + report types)
- scripts/measure_baseline.py (funnel fold region — 15.1 owns core, 15.2 owns watchability)
- tests/eval/test_funnel.py (new: scripted-fixture unit tests + the reproduction pins)

**Files NOT in scope:**
- api/replay_loader.py (the walk recipe is mirrored, not imported — the loader is API-tier and carries serving concerns; mirror the seed/advance/apply/hash-verify loop directly against orchestrator/engine)
- engine/ + orchestrator/ (consumed read-only)
- replays/samples/ (read-only input)

**Definition of done:**
- [ ] On the committed baseline-2 9p2i bytes, the folds reproduce the charter §2 figures EXACTLY: oracle candidate-set median 3 (mean 2.86), ±1-tick-window mean 2.29 / single-candidate 38/129 (killer-unique 36/129) / ≤2 84/129, killer-in-set 122/129; hard clue held in 98/129 (vent 74, last-seen-with 37, scene 32, witnessed 6); vent mentioned 36/74; votes outside a ≤3 candidate set 37/68; reporter ejected 22/106 with 22 innocent. Any mismatch is a task failure. (Figures per the charter §2 as corrected 2026-07-07 — the one-off script's ±1/hard/votes cells were proven mutually inconsistent with its own exact-tick row; see the charter's §2 preamble.)
- [ ] Every recorded state hash is verified during the walk (a corrupted or drifted set fails loud, never silently mis-measures).
- [ ] The oracle's assumptions (upper bound: honest pooling, kill-time knowledge, crew-only witnesses) and the known same-tick move+kill frame artifact are documented in the module docstring — this is a diagnostic ceiling, not a claim about achievable play.
- [ ] The folds run on any replay-set directory and on both roster presets (4p1i included), keyed by the set's roster/report artifacts.
- [ ] `scripts/measure_baseline.py --funnel` emits the per-meeting rows + aggregates in the `--json` report; 15.7 consumes it for the before/after close finding.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The reconstruction loop is: `seed_initial_state(seed=…, game_map=…, num_players=…, num_impostors=…,
tasks_per_crewmate=…)` (roster from the set's `roster.json`, defaults for the flat 4p1i set) →
`_deserialize`-equivalent of recorded actions → `advance_tick` → verify `state_hash` → on MEETING phase,
build the result from the meeting entry and `apply_meeting_result` (verify `state_hash_after`) — the
same loop `api/replay_loader.py::_walk` runs; mirror it against `orchestrator.replay` +
`orchestrator.seeder` + `engine.tick` directly. `MeetingTriggeredEvent.body_id` + `BodyState.player_id`
map the reported body to its `KilledEvent`. Crew vision is same-room-only
(`engine/visibility.py:98-127`); vents carry `source_witnesses`/`destination_witnesses` on the engine
event. Keep the folds pure and $0.

## Public types this task introduces
- `eval.funnel.InformationFunnelReport`
- `eval.funnel.compute_information_funnel`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.validity"`

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
Open a PR from branch `phase-15-funnel-diagnostics` with a title like `task 15.3: information-funnel diagnostics: commit the oracle / possession / transmission folds`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/post-phase-14-clean-up.md §2 (the charter measurement this task reproduces), H3; api/replay_loader.py:804-1035 (the `_walk` reconstruction recipe); orchestrator/seeder.py; engine/visibility.py:98-127 (crew same-room-only vision); meetings/manager.py:1821-1870 (the opt-in eligibility gate)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
