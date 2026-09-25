# B2: the full meeting reset, coherent for agents and instruments

**Status:** ready

## Outcome

The existing `meeting_reset = "hub_with_grace"` arm is the full reset the owner ruled; no engine line changes.
At a meeting's close it gathers the living players in the meeting room, clears every corpse, empties the vents,
stops ongoing actions and restarts each living impostor's kill cooldown at the map's value (4). Tasks, sabotage
and button uses survive. This card makes what agents perceive, and what instruments measure, agree with that
reset, so the round-1 candidate records no false perception and no unexplained teleport. Every fix keys on the
recorded arm or on the public regroup row it produces, so each is byte-neutral on `preserve`:

1. **Resume perception.** One shared helper composes the resume tick's events. After a regroup it keeps only
   kill and vent events and reports what it dropped.
2. **Own-completion placement.** A task finished on the trigger tick is placed where it was done, not in the
   meeting room.
3. **The regroup notice on the default evidence path.** The existing line also renders when evidence
   reasoning is off. Version 1 stays excluded.
4. **A symmetric regroup relevance window.** A regroup tick and the tick after it carry no alibi evidence,
   whether they would corroborate an alibi or prosecute one (`alibi_vs_sighting`). Their sightings stay out
   of the ballot's own-evidence rows.
5. **Legible memory.** The regroup co-presence folds into one line; the self-location trail marks the regroup.
6. **Every reader follows:** game, replay helpers, loader, walk, funnel, evidence honesty, scorecard, the
   phase-20 counterfactual, transcript detectors, manager, corroboration and agent memory.

`eval/off_menu.py` is not edited: it is FROZEN and keeps refusing experiment recordings. No viewer file is
edited this wave. The arm stays default-OFF; only the record card records it ON, into the candidate directory.
This card carries out the owner's full-reset ruling, and so it supersedes the direction's section-9 deferral of
the body-freshness band and cleanup decision A-28.

## Evidence

Every `path:line` below is a citation at `e886b663`, labelled by its symbol; the implementer re-anchors each
by that symbol at dispatch. Sources, in `~/.claude/projects/-Users-danielkeinan-projects-AiLibi/`:
`stage-b-2026-09-24/decision-memo.md` (sections 0, 1, 2.3, 3.1, 3.2, 3.4 card 9 and 4),
`stage-b-2026-09-24/meeting_reset_full.md` (sections 1, 2.2 to 2.9, 4 and 5) and, for the planted tests,
Part 3 B2 of `analysis-2026-09-24/analysis-memo.md`.

**The owner's rulings of 2026-09-24, verbatim.** Ruling 1: "We should implement stage B". Ruling 3: "B2. full
reset." Ruling 11: "Tour fix can be deferred to after gameplay is finished". Ruling 12: "Hold off on ML as D
suggests until gameplay is finished." The record paragraph: "Let's not re-record all 300 seeds each time. When
it's time to record, record the smaller group of 50 seeds, assess if the implementations have been effective
and resulted in desired results. Also it is understood that updating the vent and body reset logic will
probably have a substantial effect on previous limits and statistics around the baseline voting results, that
is okay."

**The orchestrator's rulings, made under the owner's delegation of 2026-09-24.**
- Decision memo 2.3: "Record on the existing arm with no engine change". "Sabotage surviving the reset is
  documented, not changed." It also accepts the fold and trail marker, the symmetric window, the own-row
  exclusion, the priced resume loss and full caller threading.
- Decision 0.3 item 8 signs off Outcome items 3 and 4 (the memo's fixes 3 and 5): "Both are new prompt bytes
  and a detector change beyond the literal words "full reset". They are signed off here as material decisions
  and must be recorded as such in the B2 card." The reason: "without them, the recorded reset writes false
  perceptions and unexplained teleports into every post-meeting prompt, which is a defect, not an experiment."
- Decision 0.3 item 6: "Once round 1 is recorded, an arm value's meaning is frozen." It applies to
  `hub_with_grace` too. Decision 0.3 item 10: off-menu and the other policy-rerunning or frozen instruments
  "keep refusing".
- R6: impostor self-report stays OFF, and the reset adds no impostor callers. R13: no scorecard cell. The spine
  lands the validator's refusals of evidence version 1, and of `post_meeting_retarget`, with the reset.
- The dated direction addendum (decision memo section 6) reads: "B2 ("full reset") supersedes section 9's
  deferral of the body-freshness band and cleanup decision A-28." The superseded texts are "**Defer:** body
  freshness band" (`tasks/direction-2026-09-19-process-over-outcome.md:307`, restated at `:396`) and the A-28
  row (`docs/cleanup-dispositions.md:46`).

**The reset as coded.** In `apply_meeting_result` the trigger corpse is deleted (`orchestrator/game.py:1901-1904`)
and the win check returns on a win (`:1910-1921`). Only then does `regroup_after_meeting` run (`:1923-1924`;
`engine/meeting_reset.py:10-41`), followed by one tick and RNG advance. It clears `in_vent` and `last_action`,
moves the living players to the meeting room, sets cooldowns to `kill_cooldown_ticks` (4,
`engine/maps/canonical_1.yaml:34`) and empties `bodies`. `resolve_kill` needs cooldown 0 (`engine/rules.py:82`),
and the decrement runs after each play tick's actions (`engine/tick.py:629`, `:665`). So after a meeting at
tick T, kills are illegal at T+1 to T+4 and first legal at T+5 (pinned for the helper at
`tests/engine/test_meeting_reset_experiment.py:17-88`, with a crew-win case at `:98-130`). The docstring at
`orchestrator/game.py:1821-1825` still says the meeting freezes the cooldown counters.

**What the arm gets wrong today.** Count-only scratch walks over baseline 9, quoted from `meeting_reset_full.md`
sections 2.2, 2.3 and 5 and decision memo 2.3. Re-measure them at dispatch with that memo's appendix scripts; no
acceptance item depends on a quoted count.

| on 9p2i (s9 + c9) unless marked | count |
|---|---|
| non-terminal resumes with at least one false perception, arm as coded | 149 of 452 (s9 41 of 107) |
| movement views the observer could not have seen / task sightings placed in the meeting room wrongly | 95 / 914 |
| own trigger-tick completions misplaced into the meeting room | 39 of 43 |
| trigger-tick views the resume filter will drop | 398 movement, 136 task |
| visible-player rows on s9, `preserve` against the regroup | 421 against 3,009 |

The mechanisms:
- **Resume events.** `HeadlessGame._run_loop` builds the resume packet from the post-meeting state plus the
  trigger tick's events (`orchestrator/game.py:2635`). `ReplayLoader._walk` (`api/replay_loader.py:1958`),
  `_walk_replay` (`eval/replay_walk.py:795`), off-menu (`eval/off_menu.py:540`) and the golden's
  `walk_replay_meetings` (`tests/meetings/test_prompt_byte_golden.py:753`) copy it. `ObservationService` gates
  movement and task sightings on the post-state (`observation/service.py:541-631`), so after a regroup they
  read the regrouped rooms; kills and vents are witness-gated at event time. Evidence honesty's `_perceive_tick`
  and the leak scan read the walk's `last_events`.
- **Own completions.** `_build_observations` places a completion at the room of the self-state row where the
  task left the owned set (`agents/memory/store.py:1917-1948`, `completion_room` at `:1925`). After a regroup
  that row is the resume row.
- **The notice.** `_run_and_apply_meeting` (`orchestrator/game.py:2832-2850`), `ReplayLoader._walk`
  (`api/replay_loader.py:1936-1954`) and policy reconstruction (`orchestrator/policy_reconstruction.py:164-172`)
  call `ingest_public_regroup`, which returns unless evidence is version 2
  (`agents/memory/evidence_context.py:207`). The line renders only under version 2
  (`agents/memory/store.py:704-709`). The round-1 record runs evidence None.
- **The relevance gate.** `is_relevant_sighting` excludes only the spawn window, ticks 0 and 1
  (`meetings/transcript.py:850-856`, `:1202`). It is called in `reconstruct_stated_paths` (`:1425`),
  `detect_corroborations` (`:2132`), `_carries_relevant_observation` (`:2368`), `grounded_vouch_subjects`
  (`:3763`) and `derive_belief_evidence` (`meetings/manager.py:4822`). `_detect_alibi_vs_sightings`
  (`meetings/transcript.py:3175`) never calls it.
- **The ballot's own rows.** `_own_channel_evidence_rows` makes each sighting record a class-0 `own_sighting`
  row (`meetings/manager.py:3500-3522`). `MAX_EVIDENCE_ROWS_PER_SUBJECT = 8` (`:3407`) drops the earliest
  arrivals of a (subject, class) group (`:3883-3888`), so regroup co-presence can push an early `own_vent` row
  out of the block.
- **Fold and trail.** `_spawn_group_indices` folds only tick-0 runs (`agents/memory/store.py:2146-2179`,
  `:2170`). The trail docstrings (`:540-543` in `render_for_prompt`, `:1521-1524` in
  `_collect_self_location_spans`) say a meeting freezes movement.
- **Instruments.** `walk_routes` keeps the trigger tick's post-advance rooms, never the regrouped frame
  (`eval/process_scorecard.py:812-830`); its convention census 955 / 104 / 103 / 2 (`:78`) is pinned. Evidence
  honesty's `room_at` table in `_fold_game` (`eval/evidence_honesty.py:1453-1456`) and `_assert_clock_alignment`
  (`:1719`) would reject honest post-regroup sightings; the readers card leaves the reset refused there by
  name, for this card to lift.

**Callers to thread** (a `git grep` over non-test Python at `e886b663`):
- `extract_belief_evidence`: `api/replay_loader.py:1883`, `eval/evidence_honesty.py:1366`, `eval/funnel.py:1298`,
  `scripts/counterfactual_phase20.py:526`, `orchestrator/game.py:3261` (`_absorb_meeting_beliefs`).
- `reconstruct_stated_paths`: `eval/funnel.py:1419`, `meetings/corroboration.py:648`, and inside
  `meetings/transcript.py` at `:1619`, `:1901` and `:1912`.
- `fold_meeting_outcome_into_memories` (`orchestrator/replay.py:1282`): `api/replay_loader.py:1933`,
  `eval/evidence_honesty.py:1380`, `scripts/counterfactual_phase20.py:543` and the golden (`:744`).
- Kept at the no-regroup default, because each refuses experiment recordings or reads only committed
  `preserve` bytes: `eval/off_menu.py:520` and `:540` (FROZEN at `:1-2`, refusal at `:359-361`),
  `training/anchor_study.py:645` and `training/surrogate/dataset.py:943` (ML held), and
  `experiments/lab/inference_testimony_probe.py:70` (FROZEN).

**What the reset does not zero.** Openings with an impostor in a vent (s9 29 of 145): 102 of 105 pooled in-vent
slots (s9 28 of 29) were entered after the previous meeting, and the reset runs at close, so B2 zeroes "in a
vent when play resumes" (s9 10 of 107), not the opening (decision memo 0.4). `EMERGENCY_COOLDOWN_TICKS = 6`
(`agents/tactical/crewmate_policy.py:109`) gates the suspicion walk, but the kill-witness walk to the button
(`:382-387`) is ungated, hence a cell for kill-witness button calls within 6 ticks of a regroup. Sabotage
survives: 8 of 594 9p2i meetings opened with an active reactor, 5 of them non-terminal with 5 or 6 ticks left.

**No committed recording stamps the arm.** `git grep -l '"meeting_reset"' -- '*.jsonl' | wc -l` gives 101 files
(100 in `audits/deduction-candidate/run-2026-09-16`, 1 in `tests/fixtures/v3_policy_reconstruction`), and
`git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl' | sort | uniq -c` gives 956 occurrences, all
`"preserve"`. No file under `replays/` carries the key. Count-only at `e886b663` on 2026-09-24; re-run at dispatch.

## Acceptance

- [ ] **The reset at the orchestrator entry.** Mechanism: the arm-gated `regroup_after_meeting` call in
  `apply_meeting_result`. The fixture is a MEETING state with the trigger corpse, two unreported corpses, an
  impostor in a vent with cooldown 0, an active reactor with repair progress, and used button presses. Under
  the arm the result has no corpses, nobody in a vent, the impostor at the map's `kill_cooldown_ticks` (4) and
  every living player in the meeting room. Tasks, sabotage, emergency uses and alive flags are unchanged; the
  tick is +1 and the RNG advanced once. Planted proof: the same assertions fail on the `preserve` twin, which
  keeps the two unreported corpses, the vent and cooldown 0 and loses only the trigger corpse.
  `git diff --stat <merge-base> -- engine/` is empty.
- [ ] **Order and openings.** Mechanism: the win check returns before the regroup call; a button names no body.
  - An impostor-parity win at the meeting (a crewmate ejection that reaches parity) ends before any reset,
    beside the existing crew-win case.
  - A button meeting under the arm with an unreported corpse on the floor: the description names no body,
    `_assert_no_emergency_opening_body` passes, the corpse is gone after the close, and the victim is in
    `dead_ids` at the next meeting.
  - Planted proof: moving the regroup call above the win check fails the parity case, and a `found_body`
    emergency opening still raises.
- [ ] **The grace window, end to end.** Mechanism: the cooldown the regroup sets, read from the map. A kill
  through `apply_meeting_result` and `advance_tick` is rejected at T+1 to T+4 after a regroup at meeting tick T
  and succeeds at T+5. A1's census window for that meeting, read through its write-nothing `--set-dir` fold, is
  T+1 to T+4. Planted proof: under `preserve` with cooldown 0 at the meeting, the same kill succeeds at T+1;
  a carrier with the kill moved to T+4 raises the census breach.
- [ ] **Resume perception, one helper.** Mechanism: one helper in `orchestrator/replay.py` composes the resume
  events, with a keyword-only regroup flag that defaults to no regroup. After a regroup it keeps `KilledEvent`,
  `VentEnteredEvent` and `VentExitedEvent`, drops the rest, and returns the dropped movement and task events by
  kind. It is called at `orchestrator/game.py:2635`, `api/replay_loader.py:1958`, `eval/replay_walk.py:795` and
  the golden (`:753`); evidence honesty and the leak scan inherit it through the walk.
  - Fixture: on the trigger tick before a report, one crewmate leaves the meeting room, another does a task
    step in MEDBAY, and an impostor vents in view of a third. Under the arm no observer gets a movement view or
    a meeting-room task sighting for the first two, and the vent witness still gets the vent.
  - Planted proof: removing the filter fails the test, and a helper that also drops `KilledEvent` fails a
    kill-witness case. The `preserve` twin still delivers the MEDBAY task sighting to the MEDBAY observer.
- [ ] **Own-completion placement.** Mechanism: a completion detected across a public regroup row takes the
  previous self-state row's room (a `do_task` tick is never a move tick). A trigger-tick completion in LABS
  renders "(you were in LABS)" under the arm. Planted proof: reverting the placement renders the meeting room.
  The `preserve` render is byte-identical.
- [ ] **The regroup notice on the default path** (signed-off decision 1).
  - Mechanism: `ingest_public_regroup` ingests under evidence None as well as version 2, and still returns
    under version 1. The existing line renders whenever a public row exists and the version is not 1.
  - The ingestion moves into `fold_meeting_outcome_into_memories` behind a keyword-only regroup argument, so
    the live loop, the loader, the golden, evidence honesty and the counterfactual share one home. Policy
    reconstruction's direct call routes through it, or Results names that call as unchanged and idempotent.
  - Test: under the arm with evidence None, the second meeting's rendered memory carries the line, and the
    loader's `get_meeting_memory` text equals the live prompt's memory block.
  - Planted proof: removing the ingestion from the fold fails both. `preserve` renders no line, and an
    evidence-version-1 memory ingests nothing.
- [ ] **Legible memory: the fold and the trail marker.** Mechanism: under a public regroup row,
  `_spawn_group_indices` and its caller also fold runs that begin at the regroup tick when they name every other
  living player in the row's `player_ids`, all in the meeting room. The trail renders the regroup as its own
  step, in the notice's words. The two freeze docstrings and `apply_meeting_result`'s name the reset.
  - A planted 9-player regroup renders one fold line where it rendered eight rows; a partial view (one player
    unseen) keeps its rows. Under the arm, memory rendered with the public row differs from memory rendered
    without it only in the notice line, the fold line and the trail step.
  - Planted proof: removing the fold extension restores eight rows, and removing the marker restores the bare
    arrow. The golden keeps `preserve` byte-identical.
- [ ] **The symmetric regroup window** (signed-off decision 2).
  - Mechanism: one function beside the resume helper derives the regroup ticks R from the recorded config and
    the meeting rows. R is the resume tick (meeting tick + 1), as the public row records it
    (`tests/orchestrator/test_public_regroup_evidence.py:68-75` pins meetings at 2 and 6 against regroups at 3
    and 7). The orchestrator passes the ticks to `MeetingManager.run` beside `dead_ids`; they are public
    knowledge and never become a field of a recorded schema. `is_relevant_sighting` gains a keyword-only
    `regroup_ticks` argument, empty by default, and excludes R and R+1. `_detect_alibi_vs_sightings` excludes
    the same sightings from prosecution.
  - Tests: a co-presence sighting at R, or at R+1, does not corroborate; with no regroup ticks it does. An
    envelope alibi spanning a regroup, contradicted only by a sighting at R, mints no flag; with no regroup
    ticks it does. The spawn window is unchanged.
  - Planted proof: each case fails with the exclusion removed.
- [ ] **Regroup sightings stay out of the ballot's own rows.** Mechanism: `_own_channel_evidence_rows` skips
  sighting records at R or R+1; the spawn-window rows are unchanged, because changing them would move
  `preserve` bytes. Planted test: a voter holds an `own_vent` row for subject X at tick 5, seven ordinary
  sightings of X after tick 5, and co-presence sightings of X at R and R+1. The `own_vent` row survives the
  8-row budget. Removing the exclusion drops it and fails the test.
- [ ] **Full caller threading, proved by equality.** Mechanism: the regroup ticks and the resume helper reach
  every production caller that can read a reset recording: the live meeting run and its detectors, the vouch
  gate in `derive_belief_evidence`, every caller listed in Evidence (including `meetings/corroboration.py:648`),
  and `agents/memory` through the public row. `scripts/counterfactual_phase20.py` (`:526`, `:543`, `:781`) is
  threaded, or keeps the named refusal the readers card gave it; Results says which.
  - Fixture: one fake-provider arm-ON game (`HeadlessGame` from a declared config, no environment variable)
    recorded into `tmp_path`; the test asserts at least two non-terminal meetings. At each meeting open, four
    readings agree: the live agents' beliefs and rendered memory, the `ReplayLoader` reconstruction, the golden
    walker (every prompt byte-equal) and the evidence-honesty walk.
  - Planted proof, parametrised over the threaded sites: withholding the regroup ticks, or the resume helper,
    at any one site fails the test.
- [ ] **Instruments and the viewer data layer.**
  - `walk_routes` takes a meeting tick's room table from `MeetingApplied.state`. Under the arm a resume-tick
    self-claim naming the meeting room scores true. Planted proof: reverted, it scores false.
  - Evidence honesty walks a reset fixture, and its `room_at` table and clock alignment pass. Planted proof:
    reverted, the alignment raises.
  - Each `meeting_reset` refusal the readers card named as pending this card (read from that PR's Decisions) is
    lifted, and only with its fix. Planted proof: every other field that card refused is still refused.
  - The loader's first post-meeting `TickView.bodies` is `()` under the arm, and the `preserve` twin shows the
    unreported corpse. This covers the analysis memo's "no corpse after a meeting" without a frontend edit.
- [ ] **The `process-scorecard` walk profile declares its layers.** Mechanism: the profile
  (`eval/process_scorecard.py:787`) sets the spine's `threaded_layers` to the layers the scorecard
  reads, named in Results; the spine names this card as its owner. Proof: it reads the spine's fake
  full-config recording (a copy of a fake recording on today's arms, its tick rows and footer
  rewritten to carry every wave field at its ON value, with the pending set patched empty) with
  every hash verified, and it refuses a planted unknown field (a stand-in added to the config model
  and `FIELD_LAYER` in a layer the profile does not declare) by name before its first advance.
  Perturbed: the profile with its layer declaration removed refuses the full-config copy. The
  record card's scorecard `--set-dir` on the candidate walks this profile.
- [ ] **The census, end to end** (in this card's own test file). Mechanism: A1's conformance cells whose arm
  predicate is `meeting_reset == "hub_with_grace"`, folded through its `--set-dir` path. The fake arm-ON game
  reads 0 on stale reports, on play resuming with an impostor in a vent or with a corpse, and on kills in the
  grace window. Its trigger-tick discard count equals the sum of the resume helper's dropped counts. It reads a
  count, not `n/a`, on trips closed by a regroup and on sabotage active at a regroup. Every living agent holds
  exactly one `public_regroup` row per non-terminal regroup.
  - A kill-witness button call within 6 ticks of a regroup is counted. The case comes from a count-only scan of
    fake arm-ON development games (seeds 1000-1007), or failing that from a carrier built from this game's walk
    with the call inserted; Results names which.
  - Planted proof: a perturbed carrier with one corpse restored at a resume raises that cell's breach, and so
    does one with a kill moved to T+4. B5's conformance stops on corpses, vents and grace kills rely on this.
- [ ] **The OFF path, the c9 and c4 derivations and the demo bundle are byte-identical.** Mechanism: every fix
  keys on the recorded arm or on a public regroup row, and no committed recording holds either. At the branch
  head: `verify_samples` once per set directory for all four sets; the four `build_sample_report --check` runs;
  the golden on s9 and s4; `publish_process_scorecard --check` (the 955 / 104 / 103 / 2 census cannot move);
  `publish_gameplay_census --check`; and `uv run pytest -m campaign` for the campaign-tier half of the c9 refit
  pins. The demo bundle reads `api/replay_loader.py`, so `scripts/build_demo_bundle.py` at the merge base and
  at the head gives an empty `diff -r` of the two `data/` trees, and `npm --prefix frontend test` and the
  Playwright journey pass. Planted proof: applying the resume filter under `preserve` turns the golden and the
  census `--check` red; Results names both failures.
- [ ] **The documents, and the copy.**
  - `docs/observation-contract.md` states the resume rule (after a regroup the resume packet carries only the
    trigger tick's kills and vents) and the default-path ingestion of the public row. It also takes the
    body-handle card's hand-off: the sentence at `:35-38` names the recorded body-handle setting.
  - `docs/glossary.md` gains "regroup": what moves, what is cleared, and that tasks, button uses and an active
    sabotage survive. `docs/cleanup-dispositions.md` A-28 gains one line: superseded by the owner's full-reset
    ruling, pointing at the direction addendum. `audits/tactical-gameplay/README.md` gains a dated note that
    its reset row measured the arm before these fixes.
  - Mechanism: a test asserts that the contract and the glossary name each event kind in the helper's keep-set
    (read from the helper's constant) and that the glossary has a "regroup" heading. A copy test scans the new
    model-facing strings (notice, fold, trail step) and the glossary entry for task, audit and card
    identifiers and for arithmetic.
  - Planted proof: an event kind added to the keep-set without the documents fails the first test, and a
    planted identifier fails the copy test.
- [ ] **The registry row follows the audit bytes.** This card edits `audits/tactical-gameplay/README.md`, so
  the `audits/` row of `docs/artifacts.md` (`:109`, 26,635,440 tracked bytes / 329 files at `e886b663`, moved
  since by earlier cards) is recomputed with `git ls-files` as the last step, after the final merge of `main`.
  Mechanism: `test_every_counted_registry_row_matches_the_index` (`tests/scripts/test_verify_ml_evidence.py`,
  run by `check.sh`) and the offline `scripts/verify_ml_evidence.py`. Perturbed: with the row left stale after
  the README note, that test fails; Results quotes the red run.

## Constraints

**The partial-record principle binds this card.**
- Only `replays/samples/9p2i`'s seeds 0-49 are ever re-recorded, only into `replays/candidates/stage-b-r1/9p2i/`,
  and only by the record card. This card records nothing.
- Every switch is a `RecordedExperimentConfig` field, default-OFF and omitted at its default. This card adds none:
  it gives the existing `meeting_reset` value its coherent meaning, and does not touch
  `orchestrator/experiment_config.py` (`hub_with_grace` is not in `WAVE_ARMS_PENDING`).
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying byte-identically. No
  registry prompt bump and no template change.
- Role-correctness is reported and never a gate; the B2 outcome cells are reported only. Nothing pushes an agent
  toward the correct answer: the notice, fold and trail step state a public relocation.
- The meeting layer labels and never rewrites: the window marks relevance, an excluded sighting stays in the
  voter's memory block, and no transcript turn is altered.

**Wave, order and prerequisites.** Wave 3, card 9 of the decision memo's section 3.1.
- Starts after `tasks/work/stage-b-readers.md` has merged, which follows `tasks/work/stage-b-arm-spine.md`, which
  follows `tasks/work/docs-truth-typed-trigger.md`. `tasks/work/gameplay-census.md` and
  `tasks/work/vent-witness-physical.md` are on `main` first.
- Runs in parallel with `tasks/work/vent-look-and-wait.md` (B1) and `tasks/work/report-body-handle.md` (B4), and
  merges after both. Merges before `tasks/work/ballot-kill-row-and-impostor-strategy.md` (B6), which starts only
  once this card has merged; `tasks/work/stage-b-record-r1.md` records last.
- The dated direction addendum is on `main` (the `docs:` commit before wave 1); if it is not, stop and ask.
  Every merge is the owner's.

**Shared files, one writer at a time** (decision memo 3.2).
- `orchestrator/game.py` is region-owned. This card's regions: the resume composition in `_run_loop` (`:2635`),
  the regroup ticks passed to `MeetingManager.run` (near `:1283`), the regroup ingestion in
  `_run_and_apply_meeting` (`:2832-2850`), the belief call in `_absorb_meeting_beliefs` (`:3261`) and the
  `apply_meeting_result` docstring (`:1821-1825`). Not `_build_meeting_trigger` (A3's construction, the
  spine's keyword, B4's body), the live tick or the runner construction (spine), or B6's protocol,
  participants and accessor. B4 merges first. Where the memo says "B2 rebases", this card merges `main` into
  its branch and never rebases.
- Serial, in order: `meetings/manager.py` (A3; this card's `run` threading, vouch gate and own-row exclusion;
  B6); `meetings/transcript.py` (readers, this card);
  `meetings/corroboration.py` (this card, B6); `agents/memory/store.py` (A3, this card);
  `orchestrator/replay.py`, `eval/replay_walk.py` and `api/replay_loader.py` (spine, this card);
  `eval/evidence_honesty.py` (readers, this card, B6); `eval/funnel.py` (readers, this card); the golden
  (readers, this card, B6); `tests/_helpers/committed.py` (A3, A1, readers, record plumbing, this card: record
  plumbing is the prior writer, and this card starts its edit of that file only after record plumbing has
  merged and `main` is merged in); `docs/artifacts.md` (A1, readers, record plumbing, B1, this card, B5, in
  merge order, each writing only its own row: this card's is the `audits/` row);
  `docs/observation-contract.md` (B0, this card); `docs/glossary.md` (A3, spine, this card);
  `audits/tactical-gameplay/README.md` (B1, this card).
- This card alone: `eval/process_scorecard.py`, `scripts/counterfactual_phase20.py`,
  `agents/memory/evidence_context.py`, `docs/cleanup-dispositions.md`, the new test files, and
  `orchestrator/policy_reconstruction.py` only if its call must route through the fold.
- Not written here: `engine/`, `observation/`, `orchestrator/experiment_config.py`, `eval/gameplay_census.py`,
  `eval/off_menu.py`, `eval/leak_scan.py`, `frontend/`, `api/schemas.py`, `docs/architecture.md`, the direction
  file and `tasks/README.md`.

**Decisions this card makes; the PR's Decisions and Results record each one.**
- Outcome items 3 and 4 are the orchestrator's signed-off material decisions (0.3 item 8), named as such.
- The resume keep-set is exactly kills and the two vent kinds. Re-gating the other channels against
  pre-regroup visibility is rejected: it needs two visibility frames in one packet.
- One derivation of R feeds every reader, so all of them compute the same window.
- The vent branch of accusation backing (`meetings/transcript.py:2364-2366`) keeps only its spawn test: a
  witnessed vent is gated at event time and stays evidence across a regroup.
- Sabotage survives the reset; it is documented, not changed. The fold and the trail marker key on the public
  row, so they also apply to evidence-version-2 memories. No committed recording carries that row; any test
  expectation that moves is listed in Results with its reason.

**What stays out.**
- No engine change. No `eval/off_menu.py` edit: it is FROZEN, its inline composition stays, it keeps refusing.
- No viewer edit. The `frontend/src/components/MapView.tsx` snap and the `frontend/src/lib/bodies.ts` comment
  move to adoption (decision memo section 1, adoption item 8): the demo does not serve the candidate, and a
  viewer change republishes on merge. `frontend/src/lib/bodies.fixture.json` stays bound to unchanged s9
  bytes, and the tour waits (ruling 11).
- No ML: the training readers keep refusing (ruling 12). No new field, lever or environment switch, and no
  recorded schema gains a field. No census cell definition (A1's), no scorecard cell (R13), no change to
  `post_meeting_retarget`; self-report stays off (R6).
- Fake provider and scripted clients only: no live call, no `.env`, no held-out band. Never print a rendered
  prompt or a seed-band prefix; probes are count-only.

**Delivery.** Branch `work/meeting-reset-coherence`, one PR into `main`, merged or fast-forwarded and never
squashed. Never amend a pushed commit; take `main` by merging, never by rebasing. Each commit body carries
`Card: tasks/work/meeting-reset-coherence.md` immediately followed by
the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs). The PR body has Summary, Definition of done,
Decisions and Questions, ending with the Claude Code attribution line. Agents post no PR comments.
`tasks/README.md` and this card's Status line are the orchestrator's; the worker fills Results.

**Stop and ask** if a `preserve` byte, derived view or census cell moves; the golden needs more than threading
to stay green on s9 or s4; the keep-set would grow beyond kills and vents; a reader outside Expected scope would
read a reset recording at the no-regroup default; a fix needs `engine/`, `frontend/` or `eval/off_menu.py`; or
merging B1 or B4 overlaps a region of this card.

## Expected scope

- Orchestrator: `orchestrator/game.py` (the regions above); `orchestrator/replay.py` (the resume helper, the
  regroup-tick derivation, the fold's regroup argument); `orchestrator/policy_reconstruction.py` only if its
  call must route through the fold.
- Readers: `api/replay_loader.py`, `eval/replay_walk.py`, `eval/funnel.py`, `eval/evidence_honesty.py`,
  `eval/process_scorecard.py` (with the `process-scorecard` profile's layers), `scripts/counterfactual_phase20.py`.
- Meetings: `meetings/transcript.py`, `meetings/manager.py`, `meetings/corroboration.py`.
- Agent memory: `agents/memory/evidence_context.py`, `agents/memory/store.py`. No engine import; `.importlinter`
  is unchanged.
- Test helpers: `tests/meetings/test_prompt_byte_golden.py` (the resume helper, and regroup ingestion through
  the fold) and `tests/_helpers/committed.py` (the reset).
- Docs: `docs/observation-contract.md`, `docs/glossary.md`, `docs/cleanup-dispositions.md`,
  `audits/tactical-gameplay/README.md`, and the `audits/` row of `docs/artifacts.md`, recomputed last.
- New tests: `tests/orchestrator/test_meeting_reset_coherence.py` (entry, order, grace, resume, equality,
  census, viewer data, documents), `tests/agents/test_regroup_memory.py`,
  `tests/meetings/test_regroup_relevance_window.py`, `tests/eval/test_regroup_instruments.py`.
- Directly necessary test follow-through in these files, and this card's Results.

## Record impact

**What moves: nothing.** No committed recording stamps the arm: no file under `replays/` carries the key, and
the 101 files that do all hold `"preserve"`. The four sets with their MANIFESTs and report gz files,
`docs/process-scorecard.*`, `docs/gameplay-census.*`, the fixtures, the prompt stamps, the ladder tip, the ML
fits and every doc fact keep their bytes. The c9 and c4 derivations read the default path, which
`verify_samples` and the campaign-tier pins prove.

**The first recording.** The new model-facing bytes (the default-path notice, the fold line, the trail step and
the excluded rows) appear only in an arm-ON recording, whose recorded config carries their provenance, so no
stamp is needed. The record card records the arm ON into the candidate. Its pre-registered B2 cells (decision
memo section 4) read against s9's before-column: stale reports 43/135, resumes with a vented impostor 10/107,
resumes with a corpse 60/107. The conformance cells must read 0 and the notice must be present at every
regroup. Outcome cells are reported, never gated; the owner has accepted that the statistics move.

**Meaning and history.** `hub_with_grace` gains its coherent meaning here, while no recording stamps it; from
round 1 that meaning is frozen, and a revision adds a new value. The lab's reset row
(`audits/tactical-gameplay/README.md:141`, `development.json`, `held-out.json`) measured the arm before these
fixes and is not regenerated, since a later experiment never changes an earlier verdict; the note says so.

**Publication.** A push to `main` republishes the demo bundle (`.github/workflows/pages.yml`). This card edits
`api/replay_loader.py`, which the bundle executes, and no shown replay or viewer file. The empty `data/` diff,
`npm --prefix frontend test` and the Playwright journey are the proof.

**Adoption, stated now.** A missing config means `preserve` while any committed recording lacks the key, so each
`preserve` branch stays a reader path. Graduation also needs `post_meeting_retarget` and evidence version 1
retired first, the fixes made unconditional, the viewer snap, the `bodies.ts` comment and a per-replay reset
note, and the `RecordedExperimentConfig` retirement procedure the adopting card writes. A limitation stays: the
fake provider ejects nobody, so how a model reasons after a regroup is first measured by the record.

## Validation

```sh
uv run pytest -p no:cacheprovider tests/orchestrator/test_meeting_reset_coherence.py \
  tests/agents/test_regroup_memory.py tests/meetings/test_regroup_relevance_window.py \
  tests/eval/test_regroup_instruments.py tests/engine/test_meeting_reset_experiment.py \
  tests/orchestrator/test_public_regroup_evidence.py tests/meetings/test_prompt_byte_golden.py -q
uv run lint-imports
bash scripts/verify_samples.sh replays/samples/9p2i
bash scripts/verify_samples.sh replays/samples/4p1i
bash scripts/verify_samples.sh replays/ml_corpus/9p2i
bash scripts/verify_samples.sh replays/ml_corpus/4p1i
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/gen_frontend_types.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py
git ls-files audits | wc -l                        # the audits/ row's file count
git ls-files -z audits | xargs -0 cat | wc -c      # the audits/ row's tracked bytes
uv run pytest -m campaign
git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl' | sort | uniq -c
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head
npm --prefix frontend test
npm --prefix frontend run e2e
bash scripts/check.sh; echo "check.sh exit $?"
```

Build the base bundle the same way in a detached worktree at the merge base, then `diff -r` the two `data/`
trees; it must print nothing. Every gate runs in a bare shell with 0 `AILIBI_*` exports, and the PR prints that
count. `verify_ml_evidence` runs offline, never with `--complete`. `check.sh` runs whole in a clean worktree, so
no gate after a first failure is masked, and Results quotes its real exit code. Fixtures and probes print ids,
rooms, ticks and counts only.

## Results

Not started. The worker records here and in the PR: the sections relied on (decision memo 2.3, 3.2 and 3.4
card 9, the spine's arm page `docs/experiment-arms.md`, `docs/observation-contract.md`); the two signed-off
decisions and every decision under Constraints; each caller's disposition; the equality fixture's seed and
meeting count and the kill-witness case's source; each planted failure with its red output; every Validation
command with its exit code and the bundle diff; changed test expectations with reasons; and the limitations.
