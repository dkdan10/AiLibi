# Stage B, card B2: the full meeting reset (`meeting_reset = "hub_with_grace"`)

Investigator memo, 2026-09-24. Read-only on `main` at `e886b663` (worktree
`wf_a8b97a8c-495-3`). No live provider call, no recorder run, no held-out band,
nothing committed. Every census below is count-only, keyed by (set, meeting), and
writes ids, rooms, ticks and kinds only. The one fresh-game probe used the CI
`FakeProvider` through `experiments.tactical_gameplay.run_candidate` into a scratch
directory and printed counts and booleans only.

Citations are `path:line` at `e886b663`.

---

## 0. The answer in ten lines

1. **Yes, `hub_with_grace` as coded is the full reset the owner ruled.** It gathers
   survivors in the meeting room, empties vents and corpses, restarts the kill
   cooldown at 4 and stops ongoing actions. Task progress, button uses and sabotage
   survive. No change to `engine/meeting_reset.py` is needed.
2. **Sabotage surviving is right for this project.** It diverges from the reference
   genre for reactor-type sabotage, and that divergence should be written down, not
   changed. The risk it creates is about zero: 5 of 594 9p2i meetings resumed with a
   live reactor, at 5 or 6 ticks left, and the nearest panel is 2 hops from the
   meeting room.
3. **The arm is coherent in the engine only, not in what agents perceive.** Recorded
   as it stands, it would write false perceptions into the 50-seed record.
   - The resume packet re-reads the trigger tick's events against the regrouped
     positions.
   - Counterfactually on baseline 9 (9p2i), 149 of 452 resumes would carry at least
     one false perception:
     - 914 task sightings stamped in the Cafeteria for players who were elsewhere;
     - 95 movement sightings the observer could not have seen;
     - 39 of the agents' own task completions placed in the Cafeteria.
4. **Models on the default evidence path are never told about the regroup.** The
   public-regroup memory line exists, but only for evidence v2
   (`agents/memory/evidence_context.py:207`, `agents/memory/store.py:704`). Meanwhile
   the map card tells them every door is one tick of walking.
5. **The meeting layer treats post-regroup Cafeteria sightings as real alibi
   support.** The spawn-window relevance gate excludes only ticks 0 and 1
   (`meetings/transcript.py:849-856`, `:1202`). Its own rationale applies unchanged
   to every regroup.
6. **The working hypothesis (arm default-OFF, recorded ON, adopted later) holds for
   the mechanic but fails in two places:**
   - the recorder cannot stamp an arm (`eval/balance_eval.py:386-400`);
   - several readers of samples/9p2i refuse experiments or assume `preserve`:
     - the evidence-honesty walk and its clock check;
     - the prompt-byte golden;
     - the process-scorecard route table;
     - the rubric extractor;
     - the test helpers;
     - the scorecard's pooled 9p2i group.
7. **Re-measure.** Counts are 9p2i unless marked pooled.
   - Stale reports: 167 of 551.
   - They produced 58 impostor ejections:
     - 50 of the 58 carried a vent flag naming the ejected impostor;
     - 41 of those 50 flags rest on a sighting made after the previous meeting;
     - in 46 of the 50, a flag speaker still held an unused button press;
     - only 8 of the 58 rested on table deduction.
   - Held vent sightings: 25 of 26 repeats were spoken. All 26 are on 9p2i.
8. **B4 does not require evidence v2 to ride along.** Make the existing regroup line
   render on the default path, gated on the arm. That keeps B4's narrow handle arm.
9. **Card scope.**
   - No engine change.
   - Five arm-gated coherence fixes, each byte-neutral on the three `preserve` sets:
     1. resume perception;
     2. where the agent's own completion is placed;
     3. the regroup notice;
     4. the relevance window;
     5. the scorecard and honesty route tables.
   - The golden and the other readers thread the arm.
   - The viewer snaps tokens and drops the corpse note per replay.
   - Ten planted tests.
10. **Graduation later needs more than the lever-retirement procedure.**
    - A missing config means `preserve`, so the default cannot simply flip.
    - The other three sets and the frozen fixtures must be re-recorded, or `preserve`
      kept as a reader-only path.
    - The meeting follow-through arm dies with it.
    - Evidence v1 must be retired first.

---

## 1. Is `hub_with_grace` the full reset? What resets, what survives

The code is `engine/meeting_reset.py:10-41`. It is called only from
`apply_meeting_result` at `orchestrator/game.py:1923-1924`. That call comes after
the vote is applied (`:1851-1890`), after the trigger corpse is deleted
(`:1901-1904`) and after the win check, which returns first on a win (`:1910-1921`).

| State | Under `hub_with_grace` | Line |
| --- | --- | --- |
| Living players' room | set to the meeting room (CAFETERIA, `engine/maps/canonical_1.yaml:434-435`) | `meeting_reset.py:29` |
| Living players' position | `(index, 0.0)` in sorted-id order | `:20-25`, `:30` |
| `in_vent` | False for every player | `:31` |
| `last_action` | None for every player, so ongoing multi-tick actions stop | `:32` |
| Kill cooldowns | every living impostor set to `kill_cooldown_ticks` = 4 (`canonical_1.yaml:34`); dead entries dropped | `:36-40` |
| Bodies | all removed, reported or not | `:41` |
| Tasks (ownership, progress, completion) | unchanged | not touched |
| Sabotage (kind, remaining ticks, active flag, repair progress) | unchanged; the timer is also paused through the meeting under both arms, because the trigger tick skips passive effects (`engine/tick.py:641-658`) and `apply_meeting_result` never advances it | not touched |
| Emergency uses | unchanged (one per player per game, `canonical_1.yaml` `uses_per_player: 1`) | not touched |
| Alive and role, dead players' room | unchanged | `:29-30` |
| Tick and RNG | caller advances once, as under `preserve` (`game.py:1926-1941`) | |

- **The grace is real.** Kills are rejected on the 4 ticks after the meeting, and the
  first legal kill is on meeting tick + 5. This is pinned by
  `tests/engine/test_meeting_reset_experiment.py:78-88`, and it matches round start
  (`orchestrator/seeder.py:106-113`).
- **The genre match is close.** The reference game gathers everyone at the table,
  clears bodies, pulls players out of vents, restarts the kill cooldown, and keeps
  task progress and per-player button limits.
- **It is exactly the option the memo offered.** The owner's "full reset" answered
  the memo's "full reset or narrow clear" (analysis memo Part 3 B2), and the memo
  defines the full reset as this arm. The tactical README describes it the same way:
  "one combined intervention ... cannot be described as a cosmetic location reset"
  (`audits/tactical-gameplay/README.md:141`).

**Sabotage survival.**

- **How the genre differs.** In the reference game, which is general knowledge rather
  than repository evidence, a body report during a critical sabotage (reactor or
  oxygen) ends it, and the button is disabled while one runs.
- **This engine allows both kinds of meeting during an active reactor.**
  - The emergency button has no sabotage check (`engine/rules.py:213-235`).
  - Reporting has none either (`engine/rules.py:191-210`).
  - This is independent of B2.
- **Why keep it.**
  - The Phase-11 reactor is a task-race stall with repair urgency, owner intent
    2026-06-16 (`engine/maps/canonical_1.yaml:394-421`).
  - Clearing it at a reset would turn every meeting into a free reactor cancel. That
    is a new sub-option inside the arm, against the direction's stop on adding levers.
- **Why the risk is negligible.**
  - After the regroup every crewmate is 2 hops from ENGINEERING and 3 from REACTOR.
    Hop distances come from `load_canonical_map()`: EAST_HALL 1, ENGINEERING 2,
    REACTOR 3.
  - Repair gains +1 per repairing crewmate per tick (`engine/tick.py:504-527`). So
    three crew finish on the third tick, and one crewmate alone needs 5 remaining
    ticks.
  - Observed: 8 of 594 9p2i meetings opened with an active reactor; 5 were
    non-terminal, with 5 or 6 ticks left.
  - Crew rank repair above tasks (`agents/tactical/crewmate_policy.py:389-402`).
- **Verdict.** Keep. Document the divergence. Add a census cell for sabotage wins
  within 6 ticks of a regroup.

---

## 2. What must change for a live record on this arm

### 2.1 Checking the partial-record hypothesis for B2

**What holds.**

- The arm exists with default `preserve` (`orchestrator/experiment_config.py:36`).
  A missing config means historical defaults (`:1-6`, `:116-122`, `:137-142`).
- The arm is stamped on every tick row and the footer, and checked for agreement
  (`:145-165`).
- The readers apply it:
  - the spectator loader (`api/replay_loader.py:1805-1816`, `:1934-1955`);
  - the replay walk, for profiles that support experiments
    (`eval/replay_walk.py:752-761`);
  - format-3 policy reconstruction (`orchestrator/policy_reconstruction.py:164-170`).
- `verify_samples` uses `ReplayLoader` (`scripts/_verify_samples.py:32`, `:132`), so
  it re-simulates a reset recording correctly. The probe in section 5.4 confirms it.
- The three `preserve` sets keep loading byte-identically, because nothing here
  touches the `preserve` branch.

**Where it fails.** Each item says whether it belongs to B2 or to the record card.

| # | Failure | Evidence | Owner |
| --- | --- | --- | --- |
| F1 | The recorder cannot stamp any arm: the tournament path builds `HeadlessGame` with no `experiment_config` | `eval/balance_eval.py:386-400`; `scripts/run_tournament.py` has no flag | record card (census_and_record memo, section 5.1 item 2) |
| F2 | Resume packets fabricate perceptions under the arm | section 2.2 | **B2** |
| F3 | An agent's own task completion is placed in the Cafeteria | section 2.3 | **B2** |
| F4 | No regroup notice on the default evidence path | section 2.4 | **B2** |
| F5 | The relevance gate knows only the spawn window | section 2.5 | **B2** |
| F6 | Readers that assume `preserve` or refuse experiments | section 2.7 | B2 for the reset-specific fixes; record card for the generic refusal and pooling list |

**Is gating on the arm consistent with craft rule 7?**

- F2 to F5 are prompt-byte, perception and detector changes. Rule 7 wants those
  default-OFF behind an explicit experimental gate. The recorded
  `meeting_reset == "hub_with_grace"` is that gate.
- They are consequences of the arm, not independent choices. So gating them on the
  arm adds no lever, which the direction forbids
  (`tasks/direction-2026-09-19-process-over-outcome.md:315-318`, "Stop: adding
  levers").
- They are byte-neutral on every `preserve` recording by construction. The golden
  proves it.

### 2.2 Perception at the resume tick. Defect found; must fix before recording

**The mechanism.**

- After a meeting the loop builds the next packets from the post-meeting state plus
  the trigger tick's events: `last_events = pre_meeting_events + tuple(post_events)`
  (`orchestrator/game.py:2635`).
- The loader mirrors this (`api/replay_loader.py:1958`), and so do the replay walk
  (`eval/replay_walk.py:795`), `eval/off_menu.py:540`, and the golden
  (`tests/meetings/test_prompt_byte_golden.py:753`).
- The design pinned in `tests/orchestrator/test_meeting_integration.py:657` is right
  under `preserve`: positions did not change, so the vision gates read the same
  frame an ordinary tick would.
- Under the regroup, the two vision-gated channels read the regrouped positions:
  - **Movement.** A move is shown if its departure room is visible in the post-state
    (`observation/service.py:580-631`; "Legacy snapshots gate the departure room
    against post-tick visibility", `observation/packet.py:108-115`). Everyone in the
    Cafeteria is therefore credited with seeing every trigger-tick departure from the
    Cafeteria. Impostors, who also see adjacent rooms, are credited with more.
  - **Task activity.** A task sighting is stamped on any actor currently visible,
    with the actor's current room (`observation/service.py:555-577`). Every
    trigger-tick task step is therefore delivered to everyone as happening in the
    Cafeteria.
  - **Kills and vents** are witness-gated at event time (`:541-554`) and stay
    correct.

**Measured.**

- Method: every baseline-9 resume was rebuilt twice with the real
  `ObservationService`, once on the recorded post-meeting state and once after
  `regroup_after_meeting`. The script is `walk_b2.py`; see the appendix.

| 9p2i (s9 + c9) | preserve (as recorded) | under the regroup, as coded |
| --- | --- | --- |
| non-terminal resumes | 452 | 452 |
| resumes with any false perception | 0 | **149** (s9: 41 of 107) |
| movement views | 398 | 210, of which **95 could not have been seen** (87 observer slots, 45 resumes) |
| task sightings | 136 | 1,017, of which **914 stamp CAFETERIA for an actor who was elsewhere** (652 observer slots, 127 resumes) |

- **Example: s9 seed 0, meeting at tick 10, resume tick 11.**
  - Crewmate p-1, who was in LABS, receives "p-3 task in CAFETERIA" and
    "p-4 task in CAFETERIA".
  - In fact p-3 was in ADMIN and p-4 was in LABS.
  - Under `preserve`, p-1 correctly receives only "p-4 task in LABS".
- **These are not leak-scan failures.** The leak scan applies the same post-state
  gate (`eval/leak_scan.py:1222-1234`), so it passes them.
- **The fake-provider screens could not see this.** They record counts only
  (`audits/tactical-gameplay/README.md:60-131`).

**Fix, gated on the arm.**

- When a regroup ran, the resume events keep only the witness-gated and self
  channels: `KilledEvent`, `VentEnteredEvent` and `VentExitedEvent`.
- They drop `MovedEvent`, `TaskProgressedEvent`, `TaskCompletedEvent` and
  `do_task` rejections.
- Put this in one shared helper that composes the resume events. Use it in the live
  loop and in every reconstructor listed above, so the golden enforces agreement.
- **What is lost.** The trigger tick's walk-and-task sightings, which a genre player
  also never "sees" after being pulled to the table. Kills and vents seen on the
  trigger tick are still delivered.
- **Rejected alternative: re-gating those channels against pre-regroup
  visibility.** It needs a second visibility frame inside one packet, and it produces
  rows whose room and tick disagree.

### 2.3 An agent's own task completion across the regroup. Defect found; small fix

- **How completions are placed.** The memory store places an own completion at the
  room of the self-state row in which the task left the owned set
  (`agents/memory/store.py:1905-1948`, `completion_room = self_room` at `:1925`).
- **Under the regroup that row is the resume row,** so the room is CAFETERIA.
- **Measured on 9p2i.** 43 own completions happened on non-terminal trigger ticks.
  39 of them were outside the Cafeteria. Under the arm, each would render as
  "You completed X (you were in CAFETERIA)", a false self-placement the agent may
  speak at roll-call. Script: `trig_complete.py`.
- **Fix.** For a completion detected across a public regroup row, place it at the
  previous self-state row's room. A `do_task` tick is never a move tick, so this is
  also the true room in general. Gate it on the regroup row, so the `preserve` bytes
  cannot move.

### 2.4 The model is never told about the regroup. Must fix for the default path

- **Where the regroup is recorded today.** The live loop ingests a
  `public_regroup` row after every non-terminal meeting under the arm
  (`orchestrator/game.py:2831-2850`). The spectator loader mirrors it
  (`api/replay_loader.py:1934-1955`).
- **But the ingestion returns early** unless `evidence_reasoning_version == 2`
  (`agents/memory/evidence_context.py:199-229`, guard at `:207`).
- **And the line** "Public regroup at the start of tick N: living players were
  placed in CAFETERIA; this was not a walking journey." renders only under evidence
  v2 (`agents/memory/store.py:703-709`).
- **The 50-seed record runs evidence None.** Baseline 9 stamps no experiment config
  and `temporal_observations: false`, per the first row of every samples/9p2i replay.
  So after a regroup the model sees:
  - its route jump several hops in one tick;
  - every other player in the Cafeteria;
  - no explanation;
  - while the map card says "Every door below is ONE tick of walking"
    (`agents/strategic/prompts/loader.py:481-484`).
- **This also feeds a known failure.** The analysis already names walkable routes
  called impossible as the main cause of 15 of 42 innocent ejections. A real
  impossible jump with no explanation feeds exactly that failure.
- **The fake probe confirms it** (section 5.4). Under the arm with evidence None, the
  second meeting's opener memory has no regroup line.
- **Fix.** Ingest the row for evidence None as well, keeping v1 excluded (FU-ALIBI-2,
  `tasks/work/retire-temporal-evidence-v1.md:33-35`). Render the existing line
  whenever such a public row exists.
  - Fold the ingestion into the shared post-meeting helper
    (`orchestrator/replay.py:1282`, `fold_meeting_outcome_into_memories`), so every
    memory rebuilder mirrors it: the loader, the golden
    (`tests/meetings/test_prompt_byte_golden.py:744`), and evidence honesty
    (`eval/evidence_honesty.py:1345-1380`).
  - Today only the live loop, the loader and policy reconstruction call
    `ingest_public_regroup`.
- **Answer to the B3/B4 memo's exception.** Evidence v2 does **not** need to ride
  along to make the regroup legible. Evidence v2 needs experiment format 2 or 3
  (`orchestrator/experiment_config.py:65-94`) and changes every prompt. So B4's
  narrow handle arm stands.

### 2.5 The relevance gate's spawn window. Should fix; detector change gated on the arm

- **What the gate does today.** It treats sightings at ticks at or below
  `SPAWN_WINDOW_LAST_TICK = 1` as carrying no evidence, because "every player
  co-spawns in CAFETERIA, so a sighting there confirms nothing ... 52% of Wave-0
  impostor accusation flow cancelled in-meeting on this class of vouch"
  (`meetings/transcript.py:849-856`; predicate `:1167-1205`).
- **Where it feeds.** Corroboration, stated paths, accusation backing and vouches
  (`:1425`, `:2132`, `:2365-2368`, `:3763`; `meetings/manager.py:4822`).
- **Under the arm, each regroup recreates the spawn situation.**
  - At the resume tick every living player is in the Cafeteria.
  - At the next tick, players are one hop out.
  - A wide alibi starting at the regroup tick can be corroborated by those sightings.
- **Fix.**
  - The orchestrator passes the public regroup ticks to the meeting layer. It already
    derives `dead_ids` and `impostor_count` the same way (`orchestrator/game.py:1260-1290`).
  - The regroup ticks come from the recorded arm and prior meeting close ticks, so
    any reader that recomputes flags derives the same window.
  - `is_relevant_sighting` then excludes a regroup tick and the tick after it,
    mirroring ticks 0 and 1.
- **This labels relevance; it does not rewrite a decision.** It is the same class of
  gate the meeting layer already applies.

### 2.6 The reporter opening and the button opening. No change needed

- **The report trigger text** is "X reported body B at tick T"
  (`orchestrator/game.py:3449-3470`). It reads the victim from `state.bodies` at
  trigger time, before any reset.
- **The reporter template** does not assume corpses persist
  (`agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:96-100`, `:135`).
- **The button text** is "X called an emergency meeting at tick T" (`game.py:3471-3476`).
  Button meetings name no body.
- **Button meetings can still open with an unreported corpse on the floor** under the
  arm: a corpse killed since the last meeting. So the fabricated-body guard
  (`orchestrator/game.py:3298-3338`) and the phrase-keyed detection
  (`meetings/manager.py:932-943`) stay load-bearing.
- **The dead are still announced at every meeting.** `dead_ids` is rendered as
  "Dead or ejected - never accuse" (`orchestrator/game.py:1266-1287`;
  `crewmate_report.j2:115-116`, `accusation_round.j2:227-228`).
  - The roster ingestion at `game.py:2666-2680` is evidence-gated and does nothing on
    the default path (`evidence_context.py:169-170`).
  - With a reset, where an unfound victim fell is lost; that they died is not.

### 2.7 Instruments and readers

**Reset-specific. B2 should own these.**

- **Process scorecard, row 3** (`manufactured_contradiction_rate` and the envelope
  census). Its route table records the trigger tick's post-advance rooms and never
  the regrouped resume frame: `per_tick.setdefault` in `eval/process_scorecard.py:821-830`.
  An agent-frame claim for the resume tick (offset 1, `:192`) is therefore scored
  against pre-regroup rooms.
  - The fake probe (section 5.4) shows route[t] disagreeing with the resume frame for
    6 of 8, 2 of 6 and 3 of 5 living players under the arm, and 0 under `preserve`.
  - Fix: take the room table for a meeting tick from `MeetingApplied.state`. Rooms
    are unchanged under `preserve`, so the 955 / 104 / 103 / 2 census cannot move.
- **Evidence honesty.**
  - Its walk profile refuses experiments (`eval/evidence_honesty.py:2605-2613`;
    default `supports_experiments=False`, `eval/replay_walk.py:355`, refusal
    `:505-508`). The probe confirms: "does not support experimental recordings".
  - Its `room_at` table (`:1453-1457`) and clock-alignment proof (`:1719-1764`) would
    reject honest post-regroup sightings.
  - Same fix, plus the resume helper in its `_perceive_tick`.
  - `tests/_helpers/committed.py:465-504` reuses that profile.
- **Prompt-byte golden.**
  - It walks samples/9p2i and samples/4p1i (`tests/meetings/test_prompt_byte_golden.py:174-177`).
  - It calls `apply_meeting_result` without `meeting_reset` (`:723-730`), so a
    reset recording fails its post-hash check.
  - It must thread the recorded arm, the regroup ingestion and the resume helper.
- **Rubric extractor.** Same defect (`audits/workflows/extract_gameplay_facts.py:2751-2756`;
  F6 in the census_and_record memo).

**Generic. The record card owns these; listed so nothing is dropped.**

- **Walk profiles that refuse experiments:**
  - `eval/validity.py:508`;
  - `eval/solvability.py:698`;
  - `eval/watchability.py:1544`;
  - `eval/funnel.py:254`;
  - `eval/kill_craft.py:527`;
  - `eval/win_condition_selfcheck.py:205`;
  - `eval/balance_eval.py:914`.
- **Pooling.** The scorecard publishes `pooled` and `pooled_9p2i`
  (`eval/process_scorecard.py:595-596`). After the record, s9 (on the arm) and c9
  (`preserve`) must not be summed.
- **Frontend fixture.** `frontend/src/lib/bodies.fixture.json` is bound by digest to
  replays/samples/9p2i (`frontend/src/lib/bodies.test.ts:17-25`, `:436-445`). It must
  be regenerated and its pins re-derived after any s9 re-record.
- **ML readers stay untouched while ML is held.** The anchor study
  (`training/anchor_study.py:666`) and the surrogate dataset
  (`training/surrogate/dataset.py:1184`) must refuse the arm rather than misread it.

**If the record goes to an assessment directory rather than over s9** (the
census_and_record and B3/B4 memos recommend that):

- The generic refusals stop blocking the gate.
- The reset-specific fixes above are still needed. Without them the owner's
  assessment of that directory would be computed on mis-attributed routes.

### 2.8 The viewer

- **Corpses.** Bodies render from engine truth (`frontend/src/lib/bodies.ts:1-8`,
  `api/schemas.py:574-578`), so under the arm they vanish at the meeting close on
  their own. In the probe, the first post-meeting frame had 0 bodies under the arm
  and 1 under `preserve` (section 5.4).
- **Token movement.**
  - There is no frame of the regroup itself. The frame after a meeting is the state
    after tick t+1's moves.
  - Tokens tween whenever consecutive frames differ by one index
    (`frontend/src/components/MapView.tsx:573-574`).
  - So every token slides straight from its pre-meeting room to one hop out of the
    Cafeteria, across the map.
- **Fixes.**
  - Snap (`animate = false`) on the first frame after a meeting when
    `experiment_config.meeting_reset === "hub_with_grace"`. `ReplayMetadataView`
    already carries the config (`frontend/src/types/api.ts:66`).
  - Update the `bodies.ts` header comment. It says only the trigger corpse is deleted.
  - Make A2's "corpses stay on the floor" note per replay, keyed on the arm, rather
    than dropped. Three of four sets remain `preserve`.
- **User-facing copy.** `PublicResults.tsx:16` already labels the group "experimental
  round or task rules". A plain one-line note on reset replays ("after each meeting
  everyone returns to the Cafeteria and bodies are cleared") would define the term.
  "Regroup" would then belong in `docs/glossary.md`.

### 2.9 Census cells (A1) under the arm

- **Zero by construction under the arm.** Publish these with the arm predicate, not as
  behaviour:
  - stale reports;
  - vents carried through a meeting;
  - kills in the grace window;
  - resume false perceptions, after the fix.
- **Still meaningful:**
  - impostor in a vent at meeting open;
  - ejected while in a vent;
  - corpse age, now bounded by the time since the last meeting.
- **New cells:**
  - unreported corpses cleared at close;
  - vent trips closed by a regroup, meaning an entry with no exit event;
  - button meetings within one tick of a regroup;
  - regroup-window exclusions made by the relevance gate;
  - sabotage active at a regroup, and sabotage wins within 6 ticks.
- **Why the vent-trip cell matters.** In the fake screen, 56 entries against 45 exits
  under the arm, versus 53 and 53 at baseline (held-out 9p, from
  `audits/tactical-gameplay/held-out.json`). B1's waiting-in-vent makes this cell
  grow. R7's physical witness rule sees no exit for these trips, because the regroup
  emits no event.

---

## 3. Interactions

**B4 (public body handle).**

- The two are independent code paths. The trigger reads the victim before the reset.
- Under the reset every reported corpse was killed since the last close, so the leak's
  range narrows but its exact tick still leaks. B4 is still needed.
- B4's handle (`body-<victim>`, `observation/body_ids.py:6-11`) is unique per victim;
  the reset cannot create a collision.
- Joint planted test: a report after a regroup names the handle without a tick, and a
  button meeting names no body.

**Temporal observations** (default OFF; the record keeps them OFF under B4's narrow
ruling).

- The regroup emits no engine event: `apply_meeting_result` returns only
  `GameOverEvent` (`game.py:1845-1945`), and event batches are built only after
  `advance_tick` (`game.py:2588-2599`).
- So the teleport produces no movement view, no temporal batch and no `saw_move`, in
  either channel. That is honest: nobody walked.
- The only thing that makes it legible to a listener is a public statement, which is
  the fix in section 2.4.
- With temporal v1 ON, moves and kills are delivered at their source tick and filtered
  from the snapshot (`observation/service.py:362-371`). The movement half of section
  2.2 would vanish, but task sightings would still be re-stamped.
- Temporal v2 (format 3) is coherent by design: action evidence is event-local only
  (`:372-374`), and the regroup row is public.
- So the section 2.2 fix is needed under both OFF and v1.

**B1 (the vent exit waits).**

- An impostor waiting inside a vent when a meeting is called is surfaced at the table
  by the regroup, with no exit event and no exit witness.
- That is genre-faithful. It will raise "vent trips closed by regroup" and should be
  counted separately from unseen exits.

**R7 (physical vent witness).** No conflict. A regroup-closed trip has no exit to
witness.

**R8 (a seen kill as an own-evidence row).**

- A kill witnessed on the trigger tick is still delivered at the resume, because the
  kill channel is kept by the section 2.2 fix.
- The R8 row lands there.

**B3 and R10.** No interaction.

**R6 (self-report OFF).** Consistent: the self-report arm would add impostor callers.
The reset does not.

**Meeting follow-through (`post_meeting_retarget`).**

- It assumes preserved locations and is silently inert under the reset
  (`audits/tactical-gameplay/README.md:140`; review G3-3,
  `audits/review-2026-09-06/REVIEW_APPENDIX_findings.md:101`).
- It is OFF in this wave. Graduation of the reset kills it (section 6).

**Evidence v1 with the reset.** Known defect FU-ALIBI-2 (false impossible-travel
accusations). It is not in this record. Optionally the config validator could reject
that combination now (AGENTS rule 5: invalid input raises).

---

## 4. Planted tests (each with the twin that proves it bites)

| # | Test | Twin that must fail or differ |
| --- | --- | --- |
| T1 | `apply_meeting_result` on a MEETING state with: the trigger corpse plus two unreported corpses; an impostor in a vent with cooldown 0; an active reactor with repair progress; used button presses. Under the arm: no bodies; nobody in a vent; the impostor's cooldown is 4; every living player is in CAFETERIA; tasks, sabotage, emergency uses and alive flags unchanged; tick + 1; RNG advanced once. Extends `tests/engine/test_meeting_reset_experiment.py:17-88` from the helper to the orchestrator entry | same fixture under `preserve`: only the trigger corpse is gone; the two others remain; the vent and cooldown 0 remain |
| T2 | A game won at the meeting ends before any reset. The crew-win case exists (`:98-130`); add an impostor-parity case (a crewmate ejection that reaches parity) | move the regroup call above the win check and the test fails |
| T3 | A button meeting under the arm, with an unreported corpse on the floor: the description names no body; the opening guard passes; after close the corpse is gone and the victim is in `dead_ids` at the next meeting | a `found_body` emergency opening still raises (`tests/orchestrator/test_meeting_integration.py:2687-2713`) |
| T4 | Viewer data layer: the first post-meeting `TickView.bodies == ()` under the arm. Frontend: `animate` is false across a regroup frame; the regenerated fixture's census cell reads "bodies after regroup = 0" | the `preserve` twin shows the unreported corpse; the snap rule is not applied to `preserve` replays |
| T5 | Resume perception: on the trigger tick, before a report, a crewmate leaves CAFETERIA and another does a task step in MEDBAY. Under the arm no observer gets a movement view or a CAFETERIA task sighting for them, while the witness of a trigger-tick vent still gets the vent sighting | remove the resume filter and it fails; the `preserve` twin still delivers the MEDBAY task sighting to the MEDBAY observer |
| T6 | Own completion on the trigger tick in LABS renders "(you were in LABS)" under the arm | revert the placement fix and it renders CAFETERIA |
| T7 | Under the arm with evidence None, the second meeting's rendered memory carries the public-regroup line | `preserve` renders none; the golden stays byte-identical on all `preserve` sets; evidence v1 stays excluded |
| T8 | A co-presence sighting at a regroup tick (and the tick after) does not corroborate | the same sighting with no regroup tick supplied does corroborate; the spawn window is unchanged |
| T9 | Scorecard row 3: a resume-tick self-claim naming CAFETERIA scores true under the arm | revert the room-table fix and it scores false; the `preserve` census 955 / 104 / 103 / 2 is unchanged |
| T10 | Evidence honesty walks a reset fixture and its clock alignment passes | revert the `room_at` fix and the alignment raises |

- **Fixtures.** Use `experiments.tactical_gameplay.run_candidate` or the canned
  meeting runners already in `tests/orchestrator/test_meeting_integration.py`. Both
  use the fake provider and make no live call.

---

## 5. Re-measure (count-only)

### 5.1 The stale-report population reproduces

- Script: the synth `walk.py` and `an2.py`, `an7.py`, re-run at `e886b663`.

| | stale | fresh | p (Fisher, two-sided) |
| --- | --- | --- | --- |
| 9p2i report meetings | **167 / 551** (s9 43/135, c9 124/416) | 384 | |
| skip | 92/167 | 138/384 | < 0.001 |
| impostor ejected | **58/167** | 223/384 | < 0.001 |
| crewmate ejected | 17/167 | 23/384 | 0.11 |
| reporter ejected | 14/167 | 22/384 | 0.26 |
| mean corpse age at report | 9.0 ticks (1,507/167) | 3.4 ticks (1,299/384) | |

- **samples/9p2i alone** (the before column for the 50-seed assessment):
  - stale 43/135;
  - skip 26/43 stale versus 29/92 fresh;
  - impostor ejected 14/43 versus 57/92;
  - reporter ejected 1/43 versus 6/92.

### 5.2 What the crew loses

**The 58 stale-meeting impostor ejections on 9p2i:**

- **50 carried a vent flag naming the ejected impostor.**
  - 41 of those 50 flags rest on a sighting made after the previous meeting. The
    evidence would still be held without the stale corpse.
  - In 46 of the 50, a flag speaker still held an unused button press at open. That
    witness crosses the 0.6 gate and walks to the button
    (`agents/tactical/crewmate_policy.py:404-409`). Under the reset they would be
    standing on it.
- **8 had no vent flag.** These rested on table deduction. This is the population
  genuinely at risk. Whether a later meeting would reach the same verdict cannot be
  counted without a model.
- **15 of the 58 came after the stale body's killer had already been ejected.**
- **The same stale meetings also produced 17 crewmate ejections, 14 of them
  reporters.** The reset removes those meetings too.

**Held vent sightings are re-spoken.**

- Script: the vents census (`vent_walk.py` + `respeak.py`), re-run.
- Crew spoke 25 of 26 repeats and 425 of 426 first mentions pooled.
- On 9p2i, **all 26 repeats** occur, and 377 of 378 first mentions.
- So evidence that a removed stale meeting would have aired reaches the next meeting
  about 96% of the time.

### 5.3 What a reset would change on the 9p2i baseline (counterfactual, structure only)

| cell | 9p2i | pooled |
| --- | --- | --- |
| meetings / terminal at the meeting (no reset) / resumes | 594 / 142 / 452 | 676 / 190 / 486 |
| meetings opening with another unreported corpse | 325 | 335 |
| unreported corpses a reset would clear (non-terminal) | 317 | 317 |
| meetings opening with an impostor in a vent | 92 | 101 |
| impostor cooldowns already 0 at meeting open | 301 / 861 | 326 / 943 |
| post-meeting kills inside the 4-tick grace (impossible under the reset) | **227 / 363** | 243 / 389 |
| living-player slots outside the Cafeteria at open (teleported) | 2,708 / 3,384 | 2,911 / 3,630 |
| active reactor at open (non-terminal; ticks left) | 8 (5; 5 or 6) | same |
| resumes with a false perception, as coded | 149 / 452 | 151 / 486 |
| own completions misplaced, as coded | 39 of 43 | |

- **4-player sets.** A reset clears 0 corpses in both. All their other-corpse meetings
  were terminal.

### 5.4 Fake-provider probe (mechanics only; the fake provider ejects nobody)

- **Setup:** seed 1000, 9p2i roster, one game per arm, read back through the committed
  readers.
- **Under `preserve`:** meetings at ticks 8 and 12. Route table and resume frame agree
  (0 disagreements). The evidence-honesty walk runs. The first post-meeting frame
  still shows 1 body.
- **Under the arm:** meetings at ticks 8, 20 and 31.
  - The route table disagrees with the resume frame for 6 of 8, 2 of 6 and 3 of 5
    living players.
  - The evidence-honesty profile refuses the recording.
  - Every first post-meeting frame shows 0 bodies.
  - The second meeting's opener memory has no regroup line.

---

## 6. Does graduating the arm later need more than the retirement procedure? Yes

- **Scope of the existing procedure.** `docs/agent-procedures.md:6-34` covers
  `AILIBI_*` substrate levers: delete the resolver, keep the stamp key in
  `_RETIRED_ALWAYS_ON_LEVERS`. `meeting_reset` is a `RecordedExperimentConfig` field,
  which has a different contract.

**What graduating the arm additionally needs.**

1. **The absent-config contract.** A missing config means `preserve`
   (`experiment_config.py:1-6`, `:116-122`, `:137-142`), and the model forbids extra
   fields and unknown literals.
   - So the default cannot flip, and `"preserve"` cannot be deleted, while any
     committed recording or fixture relies on it. That covers three sets, the
     tactical, deduction and investigation audit runs, and the frozen fixtures under
     `tests/fixtures/`.
   - Either re-record every `preserve` set (the ml_corpus MANIFEST requires a
     re-freeze first) and migrate the fixtures, or keep `preserve` as a reader-only
     path and require new recordings to stamp the arm.
2. **Delete coupled consumers (craft rule 3).** The meeting follow-through arm
   (`post_meeting_retarget`) is premised on preserved locations and is inert under
   the reset.
3. **Order against evidence v1.** Retire evidence v1 first
   (`tasks/work/retire-temporal-evidence-v1.md`, blocked), or reject v1 with the
   reset. Otherwise FU-ALIBI-2 becomes live.
4. **The arm-gated fixes become unconditional.** Their `preserve` branches survive only
   as legacy-reader paths, for as long as `preserve` recordings exist.
5. **Docs to rewrite or amend:**
   - `orchestrator/game.py:1820-1825`: the docstring's section 5.1 freeze claim;
   - `DESIGN.md:493`: historical, cite rather than edit;
   - `docs/architecture.md:147-165`: "experiments remain OFF and unadopted";
   - `docs/cleanup-dispositions.md:46`, decision A-28;
   - the direction's section-9 deferral (`tasks/direction-2026-09-19-process-over-outcome.md:307`,
     `:396`);
   - the glossary.

---

## 7. Recommended B2 card scope

- **Suggested slug:** `work/meeting-reset-record-ready`.
- **Status:** ready once B1 and the recorder plumbing are sequenced. It shares
  `orchestrator/game.py` with the B1, B3 and B4 cards; see the file-ownership note
  below.

### Code

Every item is gated on the recorded `meeting_reset == "hub_with_grace"`, and every
item is byte-neutral on `preserve`.

1. **No change** to `engine/meeting_reset.py` or to the arm's semantics. Update the
   `apply_meeting_result` docstring to name the arm's exception to the freeze.
2. **Resume perception.** One shared helper composes the resume events. Under the arm
   it keeps only kill and vent events. Use it at `orchestrator/game.py:2635`,
   `api/replay_loader.py:1958`, `eval/replay_walk.py:795`, `eval/off_menu.py:540`, the
   golden, and the evidence-honesty perception.
3. **Own-completion placement** across a regroup row (`agents/memory/store.py:1905-1948`).
4. **The regroup notice on the default evidence path.**
   `ingest_public_regroup` accepts evidence None, with v1 still excluded. The existing
   line renders whenever the public row exists. Fold the ingestion into the shared
   post-meeting helper.
5. **The relevance window.** The orchestrator passes public regroup ticks to
   `MeetingManager.run`. `is_relevant_sighting` excludes a regroup tick and the tick
   after it.
6. **Instruments.**
   - The scorecard room table (`eval/process_scorecard.py:821-830`).
   - Evidence honesty: `room_at`, the clock alignment, and profile support.
   - The golden and `tests/_helpers/committed.py` thread the arm.
   - The rubric extractor threads `meeting_reset`.
7. **Viewer.** The snap rule, the `bodies.ts` comment, and a per-replay reset note.
8. **Optional guards.** The config validator rejects evidence v1 with the reset, and
   `post_meeting_retarget` with the reset.

### Tests

- T1 to T10 (section 4).
- A fake-provider dress rehearsal of the full slate into a scratch directory,
  checking:
  - census "resume false perceptions = 0";
  - every regroup has its line;
  - `verify_samples` passes.

### Docs

- `docs/architecture.md:147-165`. State that the arm is recorded ON for the 50-seed
  assessment only, and add the resume-perception rule and the regroup notice.
- `docs/observation-contract.md`: the resume rule.
- `docs/glossary.md`: "regroup".
- A one-line supersession note on A-28 (`docs/cleanup-dispositions.md:46`).
- A dated amendment to the direction.
  - It records that the owner's B2 ruling of 2026-09-24 supersedes the section-9
    deferral of body-freshness work.
  - Put it beside R9's amendment, so there is one amendment block.
- The reactor divergence from the genre, written into the architecture text.

### Record impact

- The three `preserve` sets are byte-identical.
- The golden proves the `preserve` bytes. The frontend bodies fixture must be
  regenerated for any s9 re-record.
- **Measured for the owner's assessment.** Structural cells, attributable to B2 by
  construction:
  - stale 0;
  - corpses cleared;
  - vent carry-over 0;
  - grace kills 0;
  - false resume perceptions 0;
  - regroup lines present;
  - window exclusions.
- **Outcome cells.** These are reported, not gated:
  - skip rate at report meetings (s9 before: 26/43 stale, 29/92 fresh);
  - impostor ejections;
  - reporter ejections;
  - meetings and calls.
- **Attribution.** The outcome cells measure the combined wave effect, since B1, B3
  and B4 land on the same record. A B2-only fake-provider paired screen on
  development seeds 1000-1007 can isolate B2's mechanics, as
  `audits/tactical-gameplay` did, but not its reasoning effects.

### What stays for adoption

This is the owner's decision after the 50-seed assessment:

- flip the default or make the stamp mandatory;
- re-record ml_corpus/9p2i, samples/4p1i and ml_corpus/4p1i, with an ml_corpus
  re-freeze;
- migrate or retire the `preserve` fixtures;
- retire `post_meeting_retarget` and evidence v1;
- make the gated fixes unconditional;
- re-derive the pins.

### File ownership

- The following are shared with B1, B3, B4 and the record card:
  - `orchestrator/game.py`, the resume and meeting-runner call;
  - `api/replay_loader.py`;
  - `eval/replay_walk.py`;
  - the golden;
  - `tests/_helpers/committed.py`.
- Land the shared resume and threading helpers once, in whichever card goes first.
  The others consume them.

---

## 8. Could not establish

- **How a model reasons after a regroup, with or without the notice.** That needs
  live calls, which are out of scope. So does the size of the relevance-window effect
  on real speech.
- **Whether a reset changes who is ejected.** The fake provider ejects nobody
  (`audits/tactical-gameplay/README.md:75`). The 50-seed record is the first
  model-driven evidence on this arm. The arm has never met a model on the default
  evidence path; the only model-facing runs were evidence-v2 deduction scenarios.
- **Whether alibi flags that span a regroup become manufactured contradictions.** The
  claim would be literally false, since the regroup moved the speaker. Needs the
  record: split the scorecard's row 3 by "window spans a regroup tick".
- **Whether adding public-regroup rows on the default path perturbs any other part of
  that render.** For example, whether the observation selector ignores unknown row
  types. This must be proven by the golden at implementation.
- **How often crew press the button right after a regroup.** They stand on it, and
  there is no post-meeting button cooldown. Counterfactual; measure it in the record.
- **The genre rule on reactor sabotage and body reports** is general knowledge, not
  repository evidence.

---

## Appendix: reproduction (scratch outputs only; nothing written in the tree)

All scripts are in
`<session scratchpad>/b2reset/`.
Run them from the repo root with `PYTHONPATH=. uv run --frozen python`.

- `../synth0924/walk.py walk.json`, then `python3 ../synth0924/an2.py walk.json` and
  `an7.py`. Gives 167/551 and the stale/fresh table. `an2_s9.py` is the s9-only
  variant.
- `walk_b2.py walk_b2.json`, then `python3 an_b2.py walk_b2.json`. Gives the section
  5.2 and 5.3 cells: resume diffs, sabotage at open, grace kills, the vent-flag
  decomposition of the 58.
- `trig_complete.py`. Gives the 43 / 39 own completions.
- `example.py`. Gives the seed-0 resume example (ids and rooms only).
- The vents census, re-run:
  `vent_walk.py <repo> vc samples/9p2i ml_corpus/9p2i samples/4p1i ml_corpus/4p1i`,
  then `respeak.py vc` (pooled) and `respeak.py vc9` (9p2i). Gives 25/26 and 426/425.
- `probe_fake.py fake 1000`. Fake-provider probe (section 5.4).
- `hops.py`. Hop distances from the meeting room.
