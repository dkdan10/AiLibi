# Agent Prompt — 20.14 The solvability instrument: who could have done it, from the crew's own eyes

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.14 — The solvability instrument: who could have done it, from the crew's own eyes, anchored to FM-2 + ruling R4 (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.9, §5 ruling R4, §4 wave-2 "Y-axis"; audits/review-2026-08-19/D/synth-ambition.md FM-2); the census itself audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the 626-meeting table + the honest-pooling caveat) and its R2 proposal (the "recorded perception only, never engine truth" line); audits/review-2026-08-19/A/s4-info-economy-beliefs.md; audits/audit-phase-20-preregistration.md §2 instrument I-12, §3 (the `[REVIEW-DERIVED]` I-12 row this task's pin replaces), §5 (I-12 reported as the y-axis); eval/replay_walk.py:230-258 (`ReplayWalkConfig` — every check is a profile option), :259-271 (`TickOpened`, the packet-building seam), :273-281 (`TickAdvanced.pre_state`), :283-300 (`MeetingOpened.body_id`, `None` on an emergency trigger), :353-372 (`walk_replay`); eval/kill_craft.py:324-343 (the set driver) + :400-449 (the Task-19.25 consumer pattern this module copies — kills folded off `TickAdvanced.pre_state.players`); eval/validity.py:252, :267, :278 (`resolve_roster_knobs` / `seeds_on_disk` / `roles_by_seed`); engine/visibility.py:98-127 (the Task-13.8 role-asymmetric mode — a CREWMATE observer is `same_room_only` at base) + :130-160 (`compute_visibility_for_player`, `()` for a dead observer, vented players never visible); engine/rules.py:56-77 (`resolve_kill`; :76 "kill requires same room"); engine/events.py:70-77 (`KilledEvent`: tick, actor, target, room, witnesses); orchestrator/boundary.py:44-50 (one translated action batch per tick); orchestrator/game.py:1778-1786 (the +1 agent-clock seam — packets built from the pre-advance state, `input_tick = state.tick` recorded beside the post-advance state; the review's G-37 / C-36); engine/world.py:290-312 (`room_neighbors` / `vent_neighbors` / `vent_for_room`), :420 (`load_canonical_map`); engine/maps/canonical_1.yaml:229-271 (the 6-node vent graph); eval/deduction_metrics.py:852-871 (`_wilson_interval`), :873-926 (`WilsonRateCell`); scripts/measure_baseline.py:471-479 + :497-507 (the `--funnel` / `--vj` flag pattern) + :549-555 (the vj branch); eval/report_schema.py:289 + :354-359 (`TournamentReport`'s field block); api/routes/eval.py:112-125 (`_TournamentReportEvalView`, `extra="forbid"`) and tests/api/test_leak.py:445 + :753 (the recursive served-field snapshot) — the two mirrors that decide where the block may live.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-solvability-instrument`
**Depends on:** none (root)
**Section refs:** FM-2 + ruling R4 (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.9, §5 ruling R4, §4 wave-2 "Y-axis"; audits/review-2026-08-19/D/synth-ambition.md FM-2); the census itself audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the 626-meeting table + the honest-pooling caveat) and its R2 proposal (the "recorded perception only, never engine truth" line); audits/review-2026-08-19/A/s4-info-economy-beliefs.md; audits/audit-phase-20-preregistration.md §2 instrument I-12, §3 (the `[REVIEW-DERIVED]` I-12 row this task's pin replaces), §5 (I-12 reported as the y-axis); eval/replay_walk.py:230-258 (`ReplayWalkConfig` — every check is a profile option), :259-271 (`TickOpened`, the packet-building seam), :273-281 (`TickAdvanced.pre_state`), :283-300 (`MeetingOpened.body_id`, `None` on an emergency trigger), :353-372 (`walk_replay`); eval/kill_craft.py:324-343 (the set driver) + :400-449 (the Task-19.25 consumer pattern this module copies — kills folded off `TickAdvanced.pre_state.players`); eval/validity.py:252, :267, :278 (`resolve_roster_knobs` / `seeds_on_disk` / `roles_by_seed`); engine/visibility.py:98-127 (the Task-13.8 role-asymmetric mode — a CREWMATE observer is `same_room_only` at base) + :130-160 (`compute_visibility_for_player`, `()` for a dead observer, vented players never visible); engine/rules.py:56-77 (`resolve_kill`; :76 "kill requires same room"); engine/events.py:70-77 (`KilledEvent`: tick, actor, target, room, witnesses); orchestrator/boundary.py:44-50 (one translated action batch per tick); orchestrator/game.py:1778-1786 (the +1 agent-clock seam — packets built from the pre-advance state, `input_tick = state.tick` recorded beside the post-advance state; the review's G-37 / C-36); engine/world.py:290-312 (`room_neighbors` / `vent_neighbors` / `vent_for_room`), :420 (`load_canonical_map`); engine/maps/canonical_1.yaml:229-271 (the 6-node vent graph); eval/deduction_metrics.py:852-871 (`_wilson_interval`), :873-926 (`WilsonRateCell`); scripts/measure_baseline.py:471-479 + :497-507 (the `--funnel` / `--vj` flag pattern) + :549-555 (the vj branch); eval/report_schema.py:289 + :354-359 (`TournamentReport`'s field block); api/routes/eval.py:112-125 (`_TournamentReportEvalView`, `extra="forbid"`) and tests/api/test_leak.py:445 + :753 (the recursive served-field snapshot) — the two mirrors that decide where the block may live.
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run pytest tests/eval/test_solvability.py tests/scripts/test_measure_baseline_cli.py -q` green; `uv run python scripts/measure_baseline.py --solvability replays/samples/9p2i` prints the containment / singleton / singleton-correct / cleared-ejection cells matching the pins over 151 body meetings and 87 ejections at them, in under 60 s from a fresh clone (wall time pasted into the PR Summary); the four-set run prints 626 body meetings and 354 ejections at them.

This is the one new instrument the review sanctions, and the ruling says it is the last
(D/FINAL-synthesis.md §5 R4: "build exactly one (1.9), and say it is the last"). It answers
the question the project has never answered about itself: not "did the crew deduce?" but
"how much was there to deduce?" Computed with no LLM, from what living crewmates could
themselves perceive, the killer sits inside a computable candidate set in a large majority
of body-triggered meetings, the set is a singleton in a sixth of them and almost always the
right name — while a sixth of actual ejections land on someone the crew's own pooled
perception had already cleared. That converts the project's biggest standing admission
("deduction not demonstrated") from an apology into a measured gap with a denominator, and
it is the y-axis every later wave is read against (audit-phase-20-preregistration.md §5
lists I-12 as exactly that; §3 currently carries it as the only wholly `[REVIEW-DERIVED]`
instrument row, which Task 20.22 replaces with this task's committed pin).

The numbers in the review are review-measured and this task must RE-DERIVE them, never copy
them. Two halves of that were separated at HEAD by the planning session. The denominators
reproduce EXACTLY: walking all four committed sets under the walker and counting meetings
whose `MeetingOpened.body_id` is not `None` gives 626 body-triggered meetings and 354
ejections at them — per set, 151/87 (samples/9p2i, of 165 meetings), 35/8 (samples/4p1i, of
39), 411/250 (ml_corpus/9p2i, of 463), 29/9 (ml_corpus/4p1i, of 40). The candidate-set cells
do NOT reproduce from the review's one-sentence rule: a direct implementation of "clear every
living player whom a surviving crewmate was co-present with, in a room other than R, at the
kill tick" — observers restricted to crewmates alive both at the kill tick and at the
meeting, clearing via `compute_visibility_for_player` on the walker's PRE-advance state,
never self-clearing — measured containment 544/626, singleton 126/626 with 114/126 correct,
≤2 candidates 246/626, and 83/354 ejections landing outside the set, against the review's
581/626, 109/626, 103/109, 208/626 and 61/354. The planning probe is a cross-check, not a
target: it is tighter (it clears more), and the plausible causes are all definitional — the
reported body's own kill versus "the last kill before the meeting"; the candidate pool taken
at the meeting versus at the kill tick; whether a player's own uncorroborated self-placement
clears it; and whether clearing was read off engine perception (as here) or off the agents'
recorded rows, where the +1 agent clock lands a tick away. The FIRST job is to fix the
definition in prose, then count — the C5 define-before-counting lesson, and the reason this
contract pins the re-derived value with the review's beside it and the cause of every
difference stated.

The instrument is eval-privileged and must say so loudly. It reads engine state and then
narrows it through each surviving crewmate's own visibility — that is legitimate for a
measurement in `eval/`, and it is exactly what the crew CANNOT do, because nothing in the
game pools perception across agents. The module docstring must state that this view is never
an agent input; the review's own R2 note is the warning ("it must be built from recorded
perception only — never from engine truth — or it becomes omniscience and the firewall
argument collapses"), and a future gameplay lever that renders any of this into a prompt is
a different task under a different record. Nothing here changes a byte of gameplay: the
module is pure, offline, $0, reads committed bytes, and ships behind no lever.

The soundness argument is short and worth stating in code, because it is what makes the
ceiling a ceiling rather than a heuristic. A kill requires the killer to be in the victim's
room (engine/rules.py:76) and each player submits at most one action per tick
(orchestrator/boundary.py:44-50), so a player whom a surviving crewmate perceived in a room
other than the body's room, in the pre-advance state of the kill tick, cannot have killed at
that tick. No reachability computation is needed for the same-tick rule — doorway adjacency
and the vent graph enter only as the reason the rule is safe (a mover cannot also kill, and a
vented player is visible to nobody and therefore never cleared).

**Files in scope:**
- eval/solvability.py; (new — a replay_walk consumer computing, per body meeting, the co-presence candidate set from living crewmates' recorded perception; the cleared-ejection census; per-set summaries with Wilson intervals via eval.deduction_metrics._wilson_interval)
- tests/eval/test_solvability.py; (new — hand-built fixtures for the set logic; the four committed sets' cells pinned — the 109/626-class numbers re-derived and recorded as the pin)
- scripts/measure_baseline.py; (a `--solvability` emitter printing the cells, the pattern of the existing --vj/--funnel flags)
- tests/scripts/test_measure_baseline_cli.py
- eval/report_schema.py; (the `solvability` block's attachment seam — the provenance line plus the mirror tripwire; the block model itself lives in eval/solvability.py, because a defaulted field on TournamentReport is rejected by the two `extra="forbid"` mirrors named in Files NOT in scope)
- tests/eval/test_report_schema.py
- eval/replay_walk.py; (the profile-table docstring row for the new consumer only)

**Files NOT in scope:**
- api/ and frontend/ (display is a later phase; the instrument is CLI + pins) — in particular api/routes/eval.py's `_TournamentReportEvalView` mirror and tests/api/test_leak.py's `EXPECTED_EVAL_REPORT_FIELDS` snapshot, which is why the block's attachment is a recorded seam rather than a field here
- agents/ (reads packets via the walker; no agent code)
- eval/deduction_metrics.py (the Wilson helper is imported, not edited)
- meetings/, agents/memory/, engine/, replays/ (zero substrate movement; no replay byte moves; no prompt template is touched — the single prompt-set bump is Task 20.31's alone)
- orchestrator/replay.py (this task ships no lever, so there is nothing to register in the substrate stamp; Task 20.33 owns that registration for the levers that do)
- the compounding "unclearable tally" ranker from the same review section (the 286/463 top-ranked census) — a named non-goal: R4 sanctions ONE module producing the ceiling, not a second ranking instrument

**Definition of done:**
- [ ] Define-before-counting: `eval/solvability.py`'s module docstring states, in prose and before any cell is computed, the candidate-set rule — which meetings enter (body-triggered, `MeetingOpened.body_id is not None`), which kill anchors each one, who counts as an observer (crewmates alive at the kill tick AND at the meeting), what "could have been in the room" means and what clears a player, whether a player's own placement clears it, and what the metric does NOT measure (it assumes honest pooling; an impostor lying about co-presence could falsely clear a teammate, so containment is an upper bound).
- [ ] The candidate set is computed from living crewmates' perception only: per surviving crewmate, `engine.visibility.compute_visibility_for_player` on the walker's PRE-advance state of the kill tick (`TickOpened.state` / `TickAdvanced.pre_state` — the state the recorded actions were decided from, the kill-craft precedent at eval/kill_craft.py:420-449), never the post-advance state and never a raw roster read. A player is cleared only when a surviving crewmate OTHER than that player perceived it in a room other than the body's room; a player inside a vent is perceived by nobody and is therefore never cleared.
- [ ] `tests/eval/test_solvability.py` pins the set logic on hand-built fixtures, one behaviour per test, each of which fails when the rule is perturbed: a player cleared by one crewmate's sighting; the same player NOT cleared when its only witness is the impostor; NOT cleared when its only witness was killed before the meeting; NOT cleared when the witness stood in the body's own room; a vented player never cleared; a lights-sabotage tick (the degrade applies to everyone) leaving the rule unchanged for crew observers; an emergency meeting excluded entirely.
- [ ] `compute_solvability_report(sample_dir)` returns a frozen `SolvabilityReport` carrying, per set: games walked, body meetings, ejections at body meetings, and the cells — killer-in-set containment, singleton rate, singleton correctness, ≤2-candidate rate, and ejections landing on a player outside the set ("already cleared") — each as an `eval.deduction_metrics.WilsonRateCell` built from the imported `_wilson_interval` (the helper is imported, not copied and not edited), count-only fields so the block carries no roles, ids, or transcripts.
- [ ] Denominators re-derived and pinned per set and pooled: 626 body meetings and 354 ejections at them across the four committed sets, splitting 151/87, 35/8, 411/250, 29/9 in samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i (re-derived at HEAD by the planning session; the task re-derives them itself and the pin is its own recount).
- [ ] The four headline cells are pinned per set and pooled from the task's own recount, with the review's `[REVIEW-DERIVED]` values quoted BESIDE them in the test comments — containment 581/626, singleton 109/626, singleton correctness 103/109, ≤2 208/626, cleared-player ejections 61/354 (audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1) — and the cause of every difference stated as a definitional sentence, not a shrug. Where the module's rule is a choice, the rejected alternative is named in the docstring with the cell it would have produced.
- [ ] The soundness argument and the clock are in the docstring: the same-room kill requirement and one-action-per-tick premises that make the same-tick rule valid; doorway adjacency (engine/maps/canonical_1.yaml, `Map.room_neighbors`) and the vent graph (`Map.vent_neighbors` / `Map.vent_for_room`) named as why no reachability search is needed here and as the machinery any window variant would use; and the two-clock convention named explicitly — every tick in this module is an ENGINE tick from the walker, the agent-facing clock runs +1 (orchestrator/game.py:1778-1786), and no agent-recorded row is consumed.
- [ ] `scripts/measure_baseline.py --solvability [set_dir]` emits the cells, human-rendered by default and as a JSON array under `--json`, following the `--vj` / `--funnel` regions exactly (its own disjoint fold region, its own branch in `main`, the existing missing-dir / empty-dir usage errors unchanged); `tests/scripts/test_measure_baseline_cli.py` pins both renderings and the committed-set cells.
- [ ] Runtime: `--solvability replays/samples/9p2i` completes in under 60 s from a fresh clone with the wall time recorded in the PR (the planning session's four-set probe walked all 300 committed games in 3.7 s wall, so this budget is loose by design — record the number, do not assume it).
- [ ] The attachment seam is recorded rather than silently skipped: `eval/report_schema.py` gains ONE provenance line on `TournamentReport` naming `eval.solvability.SolvabilityReport` as the block's home and why it is not a field here — a defaulted field is dumped as `"solvability": null` by `model_dump(mode="json")`, which the `extra="forbid"` mirror at api/routes/eval.py:112-125 rejects on the re-validation that serves `/eval/tournament-report`, and an `exclude=True` field still appears in `model_json_schema()` and so still trips the recursive snapshot at tests/api/test_leak.py:445 — both legs reproduced in the PR Summary.
- [ ] `tests/eval/test_report_schema.py` gains the tripwire that makes the seam loud: `set(TournamentReport.model_fields)` equals its pinned six names, with a failure message naming both surfaces (`api/routes/eval.py::_TournamentReportEvalView` and `tests/api/test_leak.py::EXPECTED_EVAL_REPORT_FIELDS`) as the mirrors a new field must be added to in the same change.
- [ ] Nothing recorded, nothing moved: `bash scripts/verify_samples.sh` stays green, the prompt byte-golden stays green, no file under `replays/` changes, and the module makes no LLM call and no network call.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — write the definition paragraph first, then the code. The review's cells did not
reproduce from its one-sentence rule, which means the rule underdetermines the count; every
hour spent choosing and writing down the four choices named in the WHY (which kill anchors a
meeting; when the candidate pool is taken; whether self-placement clears; engine perception
vs agent rows) is repaid at the pin.

Step 2 — copy the walk from eval/kill_craft.py:400-449. Resolve the set with
`eval.validity.resolve_roster_knobs` / `seeds_on_disk` / `roles_by_seed` and
`engine.world.load_canonical_map`, then declare one module-level `ReplayWalkConfig`
(`profile="solvability"`, a `NoReturn` violation hook raising this module's own error type,
the referee-grade check set kill-craft uses: tick hashes, duplicate meeting rows, meeting
pre/post hashes, `missing_meeting_row="violation"`, terminal tick, trailing rows, game-end
row). An instrument that silently under-measures a truncated recording is worse than one
that fails loudly.

Step 3 — fold two things off the walk. On `TickAdvanced`, index `walk_event.pre_state` by
`entry.tick` and record each `KilledEvent` keyed by the body id the engine mints
(`f"body-{target}-{tick}"`, engine/rules.py:78) so a reported body resolves to its killer,
victim, room and tick. On `MeetingOpened`, skip `body_id is None` (emergency), look the body
up, and compute the set against the pre-advance state of that kill tick and the living
roster in `walk_event.state`.

Step 4 — keep the set function pure and separately testable: a module-level function taking
the pre-advance `WorldState`, the seed's roles, the body's room, the victim and the surviving
roster, returning a frozenset of candidate ids. Every fixture test in the DoD targets that
function directly; only the census tests walk a real replay. Note while writing it that a
CREWMATE observer resolves to `same_room_only` at base visibility (the Task-13.8 asymmetry,
engine/visibility.py:98-127) so "co-present" and "visible" coincide today — call
`compute_visibility_for_player` anyway, so the instrument stays honest if that ever changes,
and say in a comment that the equivalence is current-HEAD, not an assumption.

Step 5 — cells via `_cell`-shaped construction over the imported `_wilson_interval`; do not
re-derive the interval arithmetic and do not edit eval/deduction_metrics.py. Rare cells (the
4p1i sets contain 35 and 29 body meetings) are exactly why the interval rides beside the
rate.

Step 6 — the CLI branch is a copy of the `--vj` shape: one `add_argument`, one branch in
`main` before the core folds, `_emit_solvability_json` and `_render_solvability_human`
beside their siblings, and the region kept disjoint from the 15.1 / 15.2 / 15.3 / 16.10
regions the module docstring already partitions.

## Public types this task introduces
- `eval.solvability.SolvabilityReport`
- `eval.solvability.compute_solvability_report`
- `eval.solvability.candidate_set_for_body_meeting`

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
Open a PR from branch `phase-20-solvability-instrument` with a title like `task 20.14: the solvability instrument: who could have done it, from the crew's own eyes`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing FM-2 + ruling R4 (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.9, §5 ruling R4, §4 wave-2 "Y-axis"; audits/review-2026-08-19/D/synth-ambition.md FM-2); the census itself audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D1 (the 626-meeting table + the honest-pooling caveat) and its R2 proposal (the "recorded perception only, never engine truth" line); audits/review-2026-08-19/A/s4-info-economy-beliefs.md; audits/audit-phase-20-preregistration.md §2 instrument I-12, §3 (the `[REVIEW-DERIVED]` I-12 row this task's pin replaces), §5 (I-12 reported as the y-axis); eval/replay_walk.py:230-258 (`ReplayWalkConfig` — every check is a profile option), :259-271 (`TickOpened`, the packet-building seam), :273-281 (`TickAdvanced.pre_state`), :283-300 (`MeetingOpened.body_id`, `None` on an emergency trigger), :353-372 (`walk_replay`); eval/kill_craft.py:324-343 (the set driver) + :400-449 (the Task-19.25 consumer pattern this module copies — kills folded off `TickAdvanced.pre_state.players`); eval/validity.py:252, :267, :278 (`resolve_roster_knobs` / `seeds_on_disk` / `roles_by_seed`); engine/visibility.py:98-127 (the Task-13.8 role-asymmetric mode — a CREWMATE observer is `same_room_only` at base) + :130-160 (`compute_visibility_for_player`, `()` for a dead observer, vented players never visible); engine/rules.py:56-77 (`resolve_kill`; :76 "kill requires same room"); engine/events.py:70-77 (`KilledEvent`: tick, actor, target, room, witnesses); orchestrator/boundary.py:44-50 (one translated action batch per tick); orchestrator/game.py:1778-1786 (the +1 agent-clock seam — packets built from the pre-advance state, `input_tick = state.tick` recorded beside the post-advance state; the review's G-37 / C-36); engine/world.py:290-312 (`room_neighbors` / `vent_neighbors` / `vent_for_room`), :420 (`load_canonical_map`); engine/maps/canonical_1.yaml:229-271 (the 6-node vent graph); eval/deduction_metrics.py:852-871 (`_wilson_interval`), :873-926 (`WilsonRateCell`); scripts/measure_baseline.py:471-479 + :497-507 (the `--funnel` / `--vj` flag pattern) + :549-555 (the vj branch); eval/report_schema.py:289 + :354-359 (`TournamentReport`'s field block); api/routes/eval.py:112-125 (`_TournamentReportEvalView`, `extra="forbid"`) and tests/api/test_leak.py:445 + :753 (the recursive served-field snapshot) — the two mirrors that decide where the block may live.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
