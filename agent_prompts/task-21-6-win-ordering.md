# Agent Prompt — 21.6 The win check runs when the game is decided, meeting or no meeting

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.6 — The win check runs when the game is decided, meeting or no meeting, anchored to A-1 [ADJUSTED, P1, "defect, but SPECIFIED-and-test-pinned"] — audits/review-2026-08-26/A/collated-findings.md §A-1 (the finder's three probes, the 300-game census, the two realized seeds, the margin histogram, and the verifier's independent re-run + severity correction P0 → P1); B-2 [ADJUSTED, P2, "defect (latent; zero realized exposure)"] — audits/review-2026-08-26/B/collated-findings.md §B-2, the independent Track-B twin (its own parity/flip probes and its "the skip is in the test's own name" observation). Anchors re-verified at HEAD (4002f19b): engine/tick.py:599 `if working_state.phase == "MEETING":` with the bare `return working_state, events` at :600, inside the step-1 action loop that begins at :593; engine/tick.py:624 `# 3) Check victory.` and :625 `resolve_win_conditions(working_state)`, i.e. the check the early return jumps over; engine/rules.py:290 `resolve_win_conditions` (a one-line delegate to `engine.win_conditions.evaluate_win_conditions`, engine/win_conditions.py:22-63, whose §3.5 order — parity → sabotage → impostors-eliminated → tasks — is itself correct and is NOT touched here); engine/win_conditions.py:42-44, the comment stating that parity is ordered first "so an offensive impostor action that resolves on the same tick still attributes to the offense per §3.5" — the promise the skipped check breaks; engine/tick.py:271 `_apply_do_task` (task completion resolves in step 1, which is why a crew task win can be satisfied on a meeting-trigger tick at all); orchestrator/game.py:1327-1330, the comment asserting "A skipped meeting cannot newly satisfy a win condition by itself", and :1331 the post-meeting `resolve_win_conditions(working)` it guards — the only other call site in the tree (`grep -rn resolve_win_conditions engine/ orchestrator/` returns exactly engine/tick.py:625 and orchestrator/game.py:1331); orchestrator/game.py:1840 `while state.phase != "GAME_OVER":`, :1858 `last_events = tuple(events)`, :1869 `if state.phase == "MEETING":` and :1904 `self._game_over_event(last_events)` — the live loop that needs no edit once the engine concludes the tick; tests/engine/test_tick.py:1073 `test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks` and :1118 the emergency twin (the register cites :1109/:1117; the defs at HEAD are :1073 and :1118); tasks/phase-1.md:220, the Task-1.5 Integration risk that specified the skip verbatim; audits/audit-2026-05-09-1901.md:119 (the 1.5 row) and :160-171 (§I-2) which signed it off as conforming; the three reconstruction homes that compare a re-derived hash to the recorded one — eval/replay_walk.py:428, api/replay_loader.py:1222, training/surrogate/dataset.py:903 — and the GAME_OVER breaks that already accept the new recorded shape (eval/replay_walk.py:445, api/replay_loader.py:1272, training/surrogate/dataset.py's `if state.phase == "GAME_OVER": break` at :914); eval/replay_walk.py:453 `if meeting_entry is None` and the six profiles that treat a missing meeting row as a violation; tests/_helpers/test_committed_single_home.py:332 `UNCACHED_BY_DESIGN`, the allow-list any new committed-set walk must join.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-win-ordering`
**Depends on:** 21.3, 21.8, 21.10
**Section refs:** A-1 [ADJUSTED, P1, "defect, but SPECIFIED-and-test-pinned"] — audits/review-2026-08-26/A/collated-findings.md §A-1 (the finder's three probes, the 300-game census, the two realized seeds, the margin histogram, and the verifier's independent re-run + severity correction P0 → P1); B-2 [ADJUSTED, P2, "defect (latent; zero realized exposure)"] — audits/review-2026-08-26/B/collated-findings.md §B-2, the independent Track-B twin (its own parity/flip probes and its "the skip is in the test's own name" observation). Anchors re-verified at HEAD (4002f19b): engine/tick.py:599 `if working_state.phase == "MEETING":` with the bare `return working_state, events` at :600, inside the step-1 action loop that begins at :593; engine/tick.py:624 `# 3) Check victory.` and :625 `resolve_win_conditions(working_state)`, i.e. the check the early return jumps over; engine/rules.py:290 `resolve_win_conditions` (a one-line delegate to `engine.win_conditions.evaluate_win_conditions`, engine/win_conditions.py:22-63, whose §3.5 order — parity → sabotage → impostors-eliminated → tasks — is itself correct and is NOT touched here); engine/win_conditions.py:42-44, the comment stating that parity is ordered first "so an offensive impostor action that resolves on the same tick still attributes to the offense per §3.5" — the promise the skipped check breaks; engine/tick.py:271 `_apply_do_task` (task completion resolves in step 1, which is why a crew task win can be satisfied on a meeting-trigger tick at all); orchestrator/game.py:1327-1330, the comment asserting "A skipped meeting cannot newly satisfy a win condition by itself", and :1331 the post-meeting `resolve_win_conditions(working)` it guards — the only other call site in the tree (`grep -rn resolve_win_conditions engine/ orchestrator/` returns exactly engine/tick.py:625 and orchestrator/game.py:1331); orchestrator/game.py:1840 `while state.phase != "GAME_OVER":`, :1858 `last_events = tuple(events)`, :1869 `if state.phase == "MEETING":` and :1904 `self._game_over_event(last_events)` — the live loop that needs no edit once the engine concludes the tick; tests/engine/test_tick.py:1073 `test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks` and :1118 the emergency twin (the register cites :1109/:1117; the defs at HEAD are :1073 and :1118); tasks/phase-1.md:220, the Task-1.5 Integration risk that specified the skip verbatim; audits/audit-2026-05-09-1901.md:119 (the 1.5 row) and :160-171 (§I-2) which signed it off as conforming; the three reconstruction homes that compare a re-derived hash to the recorded one — eval/replay_walk.py:428, api/replay_loader.py:1222, training/surrogate/dataset.py:903 — and the GAME_OVER breaks that already accept the new recorded shape (eval/replay_walk.py:445, api/replay_loader.py:1272, training/surrogate/dataset.py's `if state.phase == "GAME_OVER": break` at :914); eval/replay_walk.py:453 `if meeting_entry is None` and the six profiles that treat a missing meeting row as a violation; tests/_helpers/test_committed_single_home.py:332 `UNCACHED_BY_DESIGN`, the allow-list any new committed-set walk must join.
**Complexity:** Medium
**Record impact:** the record itself — every game recorded after this merges, riding 21.15; the committed baseline-7 bytes are not edited and are re-verified to reconstruct unchanged
**Measurement:** `uv run pytest tests/engine/test_tick.py tests/eval/test_replay_walk.py tests/api/test_replay_loader.py -q` green; `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically; the two-seed census test re-derives the superseded pair from the committed 4p1i sets and the PR quotes its output.

`advance_tick` returns from inside its step-1 action loop the moment an action flips the
phase to MEETING (engine/tick.py:599-600), and step 3's win check sits 25 lines below that
return (:624-625). So on the one tick where a kill, a final task completion and a report can
all land together, the engine never asks whether the game is already over. It hands back a
MEETING state, the orchestrator runs a full LLM meeting on it, and the only win check that
ever sees the world is orchestrator/game.py:1331 — which runs *after* the ejection has been
applied. The comment above that gate (:1327-1330) says out loud what its author believed:
"A skipped meeting cannot newly satisfy a win condition by itself." Both realized cases are
skipped meetings that emitted GameOver there, so the belief is false.

The behaviour is specified, not accidental, and this contract is the ruling that overrides
the specification. tasks/phase-1.md:220 reads verbatim "MEETING phase: when an action
triggers MEETING, return early; do not run passive effects or win checks within that tick";
audits/audit-2026-05-09-1901.md:119 and §I-2 signed it off as conforming; and two regression
tests carry the skip in their own names (tests/engine/test_tick.py:1073, :1118). What was
never specified is the consequence. engine/win_conditions.py:42-44 states the §3.5 rationale
in the code itself — parity is checked first "so an offensive impostor action that resolves
on the same tick still attributes to the offense" — and the skipped check is the one place
that promise cannot be kept. A kill that reaches parity on a tick whose report sorts after it
produces `WinResult(IMPOSTORS, IMPOSTOR_PARITY)` on the returned state, no GameOverEvent, a
full meeting, and — if that meeting ejects the impostor — a recorded `CREWMATES /
CREWMATE_EJECT`. Both review tracks proved that inversion from scratch on live state
(A-1 finder LATENT CONSEQUENCE 2 and its verifier's `inv.py`; B-2 PROBE 1 + PROBE 2).

This is a latent-correctness repair, not a record repair, and the contract says so in the
verifier's own words: "realised corruption on the frozen bytes is ZERO. Both realised cases
resolved SKIPPED and recorded the CORRECT winner and reason (CREWMATE_TASKS at the right
tick); the only realised harm is 2 of 668 meetings' worth of wasted LLM turns plus 2 corpus
meetings that a correct engine would never have produced." Nothing in the committed record
is wrong; nothing about it is re-priced here. Baseline 7 is canon by explicit owner override
of a FINDING verdict, and this task does not touch that record or any pin derived from it.

The census re-runs exactly at HEAD. Walking all four committed sets and evaluating win
conditions at every MEETING transition: 300 games, 668 meetings, 2 opened on an
already-decided world — `replays/samples/4p1i/replay-seed-3.jsonl` tick 10 and
`replays/ml_corpus/4p1i/replay-seed-1009.jsonl` tick 7, both `CREWMATES / CREWMATE_TASKS`,
both resolving SKIPPED. The 4p1i legs give 100 games / 84 meetings / 2 hits, margin
histogram `{1: 84}`; the 9p2i legs give 200 games / 584 meetings / 0 hits, margins
`{1: 64, 2: 116, 3: 257, 4: 140, 5: 7}` and 9 same-tick-kill meetings at margins
`{2: 6, 3: 3}` — every figure identical to the register's, re-derived at drafting time by
folding `eval.replay_walk.walk_replay`'s `MeetingOpened` events through
`engine.win_conditions.evaluate_win_conditions`, which is the same recipe the census test
below runs in-suite. One correction the implementer
must carry: B-2's cell "Re-walking all 200 baseline-7 corpus games … MEETING-trigger ticks
whose state already satisfied a win: 0" does NOT reproduce — seed 1009 of
`replays/ml_corpus/4p1i` is one, and A-1's census is the binding one. The re-record draws
the lottery again: 148 of 668 meetings open one death from parity and 9 opened on the same
tick as a kill, so the two components are both common and only their co-occurrence is rare.

The ruling goes in the engine, not in the loop that convenes meetings, for one reason worth
stating: the engine is the project's declared single source of truth for the rules, and
`advance_tick` has four independent drivers that resolve meetings themselves —
orchestrator/game.py:1869 (the live loop), training/rollout.py:550, training/env.py:1037 and
training/anchor_study.py:562. A gate at the convening seam would have to be installed in all
four and in the next one written; a gate in `advance_tick` closes them at once, and closes
the ES rollouts whose win label is the target the surrogate and conviction models are fit
against. It also costs zero edits at those four sites: the live loop already assigns
`last_events = tuple(events)` before its MEETING branch (orchestrator/game.py:1858), so a
GameOverEvent emitted on the trigger tick exits `while state.phase != "GAME_OVER"` and
`_game_over_event` finds it and writes the `game_over` row unchanged.

Two properties of the corrected tick are load-bearing and must not be widened. Passive
effects still do not run — the sabotage clock and the cooldowns stay frozen across a meeting
trigger exactly as Phase 1 specified, so `IMPOSTOR_SABOTAGE` cannot newly fire on this path
(it needs `remaining_ticks == 0`, which the previous tick's own step-3 check would already
have caught). And actions queued behind the trigger are still dropped, unchanged: their
disposition is A-14's subject and Task 21.3's to record, and this task must not pre-empt it.

Reconstruction is where the cost lands, and it is bounded to two games. `phase` is a
`WorldState` field and `orchestrator/replay.py::_state_hash` serializes every field, so a
tick that now ends GAME_OVER hashes differently from the one those two recordings pinned.
Three homes re-derive and compare that hash — eval/replay_walk.py:428, api/replay_loader.py:1222
and training/surrogate/dataset.py:903 — and all three would raise. The answer is not to edit
the record and not to move a pin: each home gains a four-line allowance that fires only when
the engine newly concludes a meeting-trigger tick, the recording carries a meeting row for
that tick, AND the re-derived pre-ruling hash equals the recorded hash *exactly*. That third
condition is the whole safety argument — it can only accept a recording produced by an engine
identical to this one but for the ruling, so it cannot mask a determinism break, a roster
mismatch or a future engine defect. Every instrument cell, every corpus pin and
`scripts/verify_samples.sh`'s 100/100 stay exactly where the record left them. The allowance
expires by failing: after 21.15 re-records on the corrected engine no game needs it, the
census test reads zero, and the whole mechanism is deleted under the "retire means delete"
rule.

Nothing here is a lever and nothing here is a profile option. The ruling ships
unconditionally, with no `AILIBI_*` gate, nothing to register in the substrate stamp and
nothing to add to `orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS` — Phase 21's Wave 1a
is a set of unconditional repairs, and `--expect-levers` stays empty at 21.15. The allowance
is deliberately not a `ReplayWalkConfig` field either: a config flag is something a future
caller can switch off, and this is not a validation preference but a fact about two
recordings, self-describing from the bytes and gone the moment they are replaced.

Recordings made from here on need nothing new. A decided trigger tick records its tick row
with the GAME_OVER hash and no meeting row, and all three homes already break on
`state.phase == "GAME_OVER"` before they look for one (eval/replay_walk.py:445,
api/replay_loader.py:1272, training/surrogate/dataset.py:914) — which is why the six profiles
that treat a missing meeting row as a violation (eval/replay_walk.py:453) are never reached.
That path is asserted with a synthetic recording rather than assumed, because 21.15's record
will contain such games and must load in every profile on the first attempt.

**Files in scope:**
- engine/tick.py; (the win check on the MEETING transition, and `superseded_meeting_tick`, the replay-only inverse)
- tests/engine/test_tick.py; (the two Phase-1 pins re-aimed, the parity regression, the exhaustive decided-trigger table)
- eval/replay_walk.py; (the allowance at the tick-hash check at :428 — no profile option, no new config field)
- api/replay_loader.py; (the same allowance at :1222)
- training/surrogate/dataset.py; (the same allowance at :903)
- tests/eval/test_replay_walk.py; (the allowance's planted-failure cases and the new-shape recording)
- tests/engine/test_win_ordering_census.py; (new: the two-seed census over the committed 4p1i sets, and the four-set totals under `campaign`)
- tests/_helpers/test_committed_single_home.py; (the census test joins `UNCACHED_BY_DESIGN` at :332 with its reason)
- DESIGN.md; (§3.1 and §3.5 gain the dated ruling note in the document's own Superseded style)

**Files NOT in scope:**
- orchestrator/game.py (the live loop needs no edit — `last_events` at :1858 already carries the engine's GameOverEvent out of the while loop at :1840; the post-meeting gate at :1331 stays, and its :1327-1330 comment is corrected only by 21.15's record no longer producing the case it mis-describes)
- training/rollout.py, training/env.py, training/anchor_study.py (they drive `advance_tick` and inherit the ruling; grep-verified and re-run, never edited)
- engine/win_conditions.py, engine/rules.py (the §3.5 order and `resolve_win_conditions` are correct as written and are read, not changed)
- orchestrator/replay.py (no recorded row shape changes; the `game_over` row a decided trigger tick writes is the same row every other game writes — the recorded action-row disposition is Task 21.3's)
- replays/ (no byte is edited and no seed is re-recorded; the two superseded recordings stay exactly as the baseline-7 record left them)
- tests/meetings/, tests/eval/test_evidence_honesty.py and every other corpus pin (nothing this task does moves a committed cell — if one moves, the allowance is wrong and the answer is to fix it, not to re-pin)
- eval/win_condition_selfcheck.py (the §6.3 self-check reads a *recorded* game's zero-impostor tick and is unaffected; a decided-trigger game satisfies it vacuously)
- audits/workflows/extract_gameplay_facts.py (an audit workflow, not a gate; its own walk is reported in the PR, not repaired here)
- tasks/phase-1.md, audits/audit-2026-05-09-1901.md (history: the Phase-1 ruling and its sign-off are quoted, never rewritten; this contract is the override of record)

**Definition of done:**
- [ ] On the MEETING transition in `engine.tick.advance_tick` (:599), `resolve_win_conditions(working_state)` runs before the return; when it returns a `WinResult` the tick appends a `GameOverEvent` (tick, winner, reason — the same construction step 3 uses at :628-635) and returns `replace(working_state, phase="GAME_OVER")`. The `MeetingTriggeredEvent` already emitted stays in the event list: the report or emergency legitimately resolved, and suppressing it would be the engine recording a fiction.
- [ ] Passive effects still do not run on that tick and the remaining queued actions are still dropped — the tick's `rng_state` and `sabotage.remaining_ticks` are asserted unchanged in the new tests, so the only behaviour this task changes is the win declaration.
- [ ] `tests/engine/test_tick.py::test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks` (:1073) and its emergency twin (:1118) are re-aimed rather than deleted: renamed to drop the now-false `_and_win_checks` half, with every existing assertion (`next_state.tick == state.tick`, `rng_state` unchanged, `sabotage.remaining_ticks == 1`, `events == ["MeetingTriggered"]`) kept as written, since neither fixture satisfies a win condition.
- [ ] A new regression pins the inversion the ruling closes, in the shape B-2 probed: an impostor kill that reaches parity on a tick whose report sorts after it yields `events == ["Killed", "MeetingTriggered", "GameOver"]`, `phase == "GAME_OVER"`, and `GameOverEvent(winner="IMPOSTORS", reason="IMPOSTOR_PARITY")` — and the same state fed to `orchestrator.game.apply_meeting_result` is never reached because no meeting opens. Write it first and watch it fail at HEAD.
- [ ] A sibling pins the realized shape: a final task completion plus a same-tick report yields `CREWMATES / CREWMATE_TASKS` at the trigger tick and no MEETING state — the corrected engine's answer for `replays/samples/4p1i/replay-seed-3.jsonl` tick 10.
- [ ] A table-driven test asserts the ruling is total, not two cases: over one decided state, every trigger kind (`report`, `emergency`) concludes the tick, and over one undecided state both still open a meeting — so the gate is attributable to the win condition, not to the action type.
- [ ] `engine.tick.superseded_meeting_tick(state, events)` returns the `(state, events)` pair a pre-ruling engine produced for this tick — `replace(state, phase="MEETING")` with the trailing `GameOverEvent` removed — or `None` when the tick is not one the ruling newly concludes. It reads nothing outside its arguments: no seed list, no game id, no env.
- [ ] Each of eval/replay_walk.py:428, api/replay_loader.py:1222 and training/surrogate/dataset.py:903 calls it on a hash mismatch and accepts the restored pair ONLY when a meeting row exists for that tick AND `_state_hash(restored)` equals the recorded hash; otherwise the existing violation/raise fires unchanged. The restored events must be the ones handed downstream, so no consumer sees a premature `GameOverEvent`.
- [ ] The allowance ships with three planted cases in `tests/eval/test_replay_walk.py` proving it bites: (a) a recording whose tick hash diverges for any other reason still violates even though the tick is a meeting trigger; (b) a decided trigger tick with NO meeting row still ends the walk at GAME_OVER and never restores; (c) a recording carrying a meeting row whose recorded hash matches neither the corrected nor the pre-ruling state still violates.
- [ ] A synthetic recording of the NEW shape — a tick row whose hash is the GAME_OVER state, a `MeetingTriggered` in its events, no meeting row, then a `game_over` row — walks clean under every profile in eval/replay_walk.py including the six with `missing_meeting_row="violation"`, loads through `api.replay_loader.ReplayLoader`, and satisfies `require_terminal_tick` / `require_reconstructed_outcome` / `verify_recorded_outcome`. This is the shape 21.15 will record; it is asserted here, not discovered there.
- [ ] `tests/engine/test_win_ordering_census.py` walks `replays/samples/4p1i` and `replays/ml_corpus/4p1i` and asserts the allowance is needed by exactly two games — seed 3 at tick 10 and seed 1009 at tick 7, both `CREWMATES / CREWMATE_TASKS` — so a third occurrence and a stale entry both turn it red; a `campaign`-marked sibling asserts the four-set totals (300 games, 668 meetings, 2 decided triggers, margins `{1: 148, 2: 116, 3: 257, 4: 140, 5: 7}`). The test's docstring names Task 21.15 as its expiry: when the re-record lands, this census reads zero and `superseded_meeting_tick` and all three call sites are deleted.
- [ ] The census test is added to `UNCACHED_BY_DESIGN` in tests/_helpers/test_committed_single_home.py:332 with its reason (it walks for a property the cached reports do not expose), so the single-home gate stays green and the exemption is documented rather than silent.
- [ ] `DESIGN.md` records the ruling additively in its dated Superseded style: a short note at §3.1 stating that a meeting-trigger tick evaluates win conditions before returning and declares the game over when one is satisfied, and a matching note at §3.5 that the §3.5 order therefore holds on every tick including this one. The historical §3.1 loop text is left as written.
- [ ] The synthetic new-shape recording is written into a temporary set directory and accepted by `uv run python scripts/validity_gate.py <dir> --json`, with the run quoted in the PR. 21.15 gates every leg with that script, and a decided trigger tick is the one shape that record can contain and the committed one cannot — finding it out inside a 23-hour operator run is not an option.
- [ ] The ruling ships unconditionally: no `AILIBI_*` variable, no entry added to `orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS` or `_TOGGLEABLE_LEVER_RESOLVERS`, no new `*_enabled` resolver, and `uv run pytest tests/meetings/test_lever_registry.py -q` stays green — the substrate stamp a Phase-21 recording writes is byte-for-byte the 22-key block the committed record already carries.
- [ ] `bash scripts/verify_samples.sh` reports all 100 committed samples reconstructing byte-identically, and the PR states the conclusion it supports: the corrected engine changes no committed byte and moves no committed pin.
- [ ] The PR quotes a fresh blast-radius grep for the four `advance_tick` drivers that resolve meetings themselves (orchestrator/game.py:1869, training/rollout.py:550, training/env.py:1037, training/anchor_study.py:562) and records that each inherits the ruling with no edit, plus the census output above and the note that B-2's zero-over-ml_corpus cell does not reproduce.
- [ ] `uv run pytest -m campaign -q` is run and the PR records either that no pinned ML value moved or which one did and why.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — write the two regression tests and the census test first, and watch all three fail
at HEAD. The census is the cheap proof the ruling has a subject: it should print the two
seeds before any engine line is written. `eval.validity.resolve_roster_knobs(set_dir)`
returns `(num_players, num_impostors, tasks_per_crewmate)` for a committed set, and
`eval.replay_walk.walk_replay` takes those plus `seed` (parsed from the file stem) and
`game_map=load_canonical_map()`; folding `MeetingOpened` and calling
`engine.win_conditions.evaluate_win_conditions(event.state)` is the whole census. The two
4p1i sets are 100 short games and run in the default tier; keep the four-set totals behind
`@pytest.mark.campaign`.

Step 2 — the engine. Four lines inside the existing `if working_state.phase == "MEETING":`
block at :599, above the current `return`. Reuse step 3's `GameOverEvent` construction
verbatim (:628-635) rather than writing a second one — the `tick=state.tick` there is the
pre-increment tick and is what the `game_over` row records. One comment, not a paragraph:
state that a tick which decides the game does not open a meeting, and leave the provenance
to a single trailing line.

Step 3 — `superseded_meeting_tick`. It is the inverse of step 2 and belongs directly beneath
it: return `None` unless the events end in a `GameOverEvent` preceded by a
`MeetingTriggeredEvent` and `state.phase == "GAME_OVER"`; otherwise return
`(replace(state, phase="MEETING"), tuple(e for e in events if not isinstance(e, GameOverEvent)))`.
Keep it free of any replay vocabulary — the caller owns the "is there a meeting row" half.

Step 4 — the three call sites. The shape is identical in all three; write it once and paste
it, because divergence between these three loops is exactly what Task 19.25 was fought over:

    if actual != entry.state_hash:
        restored = superseded_meeting_tick(state, events)
        if restored is not None and meeting_by_tick.get(entry.tick) is not None:
            candidate_state, candidate_events = restored
            if _state_hash(candidate_state) == entry.state_hash:
                state, events, actual = candidate_state, candidate_events, entry.state_hash
        if actual != entry.state_hash:
            <the existing violation / raise, untouched>

`meeting_by_tick` already exists in all three (eval/replay_walk.py, api/replay_loader.py's
loop, training/surrogate/dataset.py:875-876), and all three already import `_state_hash` from
`orchestrator.replay`. Do not add a `ReplayWalkConfig` field for this: it is not a profile
option, it is a fact about two recordings, and a config flag would let a future caller turn
the check off.

Step 5 — the new-shape synthetic recording. Build it the way tests/api/fixtures/sample_replay.py
builds its fixtures (seed a state, drive `advance_tick`, write the rows), not by hand-writing
JSON: a hand-written hash is a hash the engine never produced, and the point of this case is
that the engine produces it. Drive a 4-player state to a final task completion plus a
same-tick report and record what comes back.

Step 6 — before pushing, run `uv run pytest -m campaign` as well as the default gate. The
default filter is `-m 'not campaign'`, and the ES/bakeoff machinery that drives
`advance_tick` and resolves its own meetings does not run unless you ask for it — that is
precisely the code whose win labels this ruling corrects.

## Public types this task introduces
- `engine.tick.superseded_meeting_tick`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`

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
Open a PR from branch `phase-21-win-ordering` with a title like `task 21.6: the win check runs when the game is decided, meeting or no meeting`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-1 [ADJUSTED, P1, "defect, but SPECIFIED-and-test-pinned"] — audits/review-2026-08-26/A/collated-findings.md §A-1 (the finder's three probes, the 300-game census, the two realized seeds, the margin histogram, and the verifier's independent re-run + severity correction P0 → P1); B-2 [ADJUSTED, P2, "defect (latent; zero realized exposure)"] — audits/review-2026-08-26/B/collated-findings.md §B-2, the independent Track-B twin (its own parity/flip probes and its "the skip is in the test's own name" observation). Anchors re-verified at HEAD (4002f19b): engine/tick.py:599 `if working_state.phase == "MEETING":` with the bare `return working_state, events` at :600, inside the step-1 action loop that begins at :593; engine/tick.py:624 `# 3) Check victory.` and :625 `resolve_win_conditions(working_state)`, i.e. the check the early return jumps over; engine/rules.py:290 `resolve_win_conditions` (a one-line delegate to `engine.win_conditions.evaluate_win_conditions`, engine/win_conditions.py:22-63, whose §3.5 order — parity → sabotage → impostors-eliminated → tasks — is itself correct and is NOT touched here); engine/win_conditions.py:42-44, the comment stating that parity is ordered first "so an offensive impostor action that resolves on the same tick still attributes to the offense per §3.5" — the promise the skipped check breaks; engine/tick.py:271 `_apply_do_task` (task completion resolves in step 1, which is why a crew task win can be satisfied on a meeting-trigger tick at all); orchestrator/game.py:1327-1330, the comment asserting "A skipped meeting cannot newly satisfy a win condition by itself", and :1331 the post-meeting `resolve_win_conditions(working)` it guards — the only other call site in the tree (`grep -rn resolve_win_conditions engine/ orchestrator/` returns exactly engine/tick.py:625 and orchestrator/game.py:1331); orchestrator/game.py:1840 `while state.phase != "GAME_OVER":`, :1858 `last_events = tuple(events)`, :1869 `if state.phase == "MEETING":` and :1904 `self._game_over_event(last_events)` — the live loop that needs no edit once the engine concludes the tick; tests/engine/test_tick.py:1073 `test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks` and :1118 the emergency twin (the register cites :1109/:1117; the defs at HEAD are :1073 and :1118); tasks/phase-1.md:220, the Task-1.5 Integration risk that specified the skip verbatim; audits/audit-2026-05-09-1901.md:119 (the 1.5 row) and :160-171 (§I-2) which signed it off as conforming; the three reconstruction homes that compare a re-derived hash to the recorded one — eval/replay_walk.py:428, api/replay_loader.py:1222, training/surrogate/dataset.py:903 — and the GAME_OVER breaks that already accept the new recorded shape (eval/replay_walk.py:445, api/replay_loader.py:1272, training/surrogate/dataset.py's `if state.phase == "GAME_OVER": break` at :914); eval/replay_walk.py:453 `if meeting_entry is None` and the six profiles that treat a missing meeting row as a violation; tests/_helpers/test_committed_single_home.py:332 `UNCACHED_BY_DESIGN`, the allow-list any new committed-set walk must join.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
