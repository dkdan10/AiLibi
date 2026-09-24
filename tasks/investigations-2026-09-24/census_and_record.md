# Census and record: A1 (gameplay census), B5 (the 50-seed record), A3 (documentation truth)

Investigator memo, 2026-09-24. Read-only at `e886b663` (baseline 9). No commit, no provider call, no `.env`,
no held-out band, no prompt text printed. Every census below is count-only, keyed by (set, meeting).
Scratch scripts: `<session scratchpad>/census_rec/`
(`walk2.py`, `cen.py`, `b1cells.py`, `r8cells.py`, `handle.py`, `handle2.py`, `disc.py`), beside the synth scripts.

Set names: `s9` samples/9p2i, `c9` ml_corpus/9p2i, `s4` samples/4p1i, `c4` ml_corpus/4p1i.

---

## 0. The answer in eight lines

1. **Every analysis figure reproduces** on baseline 9, re-measured twice (the synth walk, and my own walk through the
   process-scorecard profile, which verifies tick hashes and supports experimental recordings). One count moves by one:
   moves thrown away on trigger ticks are **809, not 808** (a game-ending trigger tick the synth skipped; section 1).
2. **The partial-record hypothesis holds for the three untouched sets** (a missing experiment config means the historical
   defaults, and every reader that matters reads it that way) but **fails for the re-recorded s9 in twelve places**
   (section 2): eight of eleven replay-walk profiles refuse any recording that carries an experiment config, the
   doc-fact gate requires all four sets to share one substrate stamp, the recorder has no way to set an engine or
   tactical arm, the scorecard pools across the boundary while printing "one era", and merging publishes the candidate
   as the public demo.
3. **Recommendation, argued against the principle as written:** record the 50 seeds as a **candidate record in its own
   location** (class (c), the `replays/records/phase-21-wave2-finding/` precedent), and leave `replays/samples/9p2i` at
   its baseline-9 bytes. It is exactly what the owner asked for ("record the smaller group of 50 seeds, assess"),
   it makes the ladder wording true by construction, and it removes ten of the twelve failures instead of patching them.
   It also makes a second or third 50-seed round cheap, which the owner's "not all 300 each time" implies.
4. **One silent failure applies either way:** vent witnesses live only in engine events, never in `WorldState`
   (`engine/rules.py:29-44`, `:146-156`), so a reconstructor that forgets the physical-witness arm (R7) passes every
   state-hash check while serving wrong witness sets. The census must refuse an experiment field it does not thread.
5. **A1 design:** `eval/gameplay_census.py` + `scripts/publish_gameplay_census.py` (`docs/gameplay-census.md` + `.json`,
   `--check`, and a write-nothing `--set-dir` mode for a candidate), 34 cells with stated denominators, event kinds and
   per-arm behaviour, era-keyed pooling that refuses to pool across arm slates, and a conformance guard per
   by-construction cell.
6. **B5 design:** slate, ceilings (2,500 calls / 16.0M input / 700k output / 4 h wall in an 8 h window / $0.00),
   a fake-provider dress rehearsal first, a before column committed before the first seed, an assessment table that
   separates **conformance cells** (must read exactly as constructed) from **behavioural cells** (published with a
   reading, not a bar).
7. **Two corrections to the orchestrator's effectiveness list:** "in vent at meeting" is not zeroed by the reset (the
   reset runs at close; B1's waiting will likely raise meetings that open with an impostor in a vent); the zeroed cell is
   "in a vent when play resumes". And "teammate ballots 0" is 0 by construction on the recorded target; it must be read
   on the authored target (1 on s9, 13 pooled today).
8. **A3 is not file-disjoint** from the B cards: its typed trigger kind edits the same function B4 edits
   (`orchestrator/game.py:3440-3480`). Land A3 first.

---

## 1. Re-measurement on baseline 9

Commands (repo root, outputs to scratch only):

```
PYTHONPATH=. uv run --frozen python <synth0924>/walk.py <scratch>/walk.json      # 4.4 s for 300 games
python3 <synth0924>/an1.py ... an11.py <scratch>/walk.json
PYTHONPATH=. uv run --frozen python <census_rec>/walk2.py <scratch>/walk2.json  # process-scorecard profile, deterministic (two runs byte-identical)
python3 <census_rec>/cen.py <scratch>/walk2.json
python3 <census_rec>/b1cells.py <scratch>/walk.json
python3 <census_rec>/handle.py <repo root>                                      # count-only prompt scan
```

| figure (analysis memo) | s9 | 9p2i | pooled | reproduces |
|---|---|---|---|---|
| kills seen by crew | 3/175 | 19/725 | 20/849 | yes |
| vent entries seen by crew | 19/105 | 64/501 | 73/587 | yes |
| vent exits seen by crew | 62/85 | 271/435 | 313/512 | yes |
| ... seen in the exit room | 53/85 | 226 | 251 | yes |
| ... seen only from the room left | 9/85 | 45 | 62 | yes |
| impostor fate: seen venting, ejected | 70/77 | 284/304 | 330/355 | yes |
| vented unseen, ejected | 3/8 | 13/56 | 13/89 | yes |
| never vented, ejected | 8/15 | 25/40 | 26/56 | yes |
| vent convictions (vent_sighting flag on the ejected impostor) | 70 | 281 | 326 | yes |
| ... exit-only / both / entry-only | 51 / 2 / 17 | 217 / 10 / 54 | 253 / 10 / 63 | yes |
| ... resting only on crew in the room left | 8 | 37 | 50 | yes |
| vent-proof meetings / no-vent meetings | 70 / 75 | 285 / 309 | 330 / 346 | yes |
| impostor ejections without vent proof | 11 | 41 | 43 | yes |
| stale report meetings (body on the floor at the previous meeting's open) | 43/135 | 167/551 | 167/623 | yes |
| meetings opening with another unreported corpse | 74/145 | 325/594 | 335/676 | yes |
| first reply accuses the opener | 120/145 | 448/594 | 521/676 | yes |
| opener speaks a second time | 0/145 | 0/594 | 0/676 | yes |
| opener share of innocent ejections | 7/9 | 37/41 | 38/42 (37 report + 1 button) | yes |
| post-meeting kills within 2 ticks | 28/87 | 129/363 | 135/389 | yes |
| meetings opening with an impostor in a vent | 29/145 | 92/594 | 101/676 | yes |
| impostor cooldown 0 at meeting open | 63/210 | 301/861 | 326/943 | yes |
| impostor ballots SKIP | 164/210 | 694/861 | 760/943 | yes |
| thrown away on trigger ticks: report / kill / vent / button | 26 / 7 / 32 / 2 | 96 / 37 / 112 / 15 | 96 / 39 / 121 / 16 | yes |
| ... moves / task steps / waits | 188 / 205 / 69 | 754 / 718 / 329 | **809** / 745 / 358 | **moves: 809 not 808** |

**The one figure that does not reproduce exactly.** Read from the recorded `action_dispositions`
(`orchestrator/replay.py:206`, verified by the walk's `verify_action_dispositions`), moves discarded by a meeting are
809. The synth sliced `actions[len(events):]` only on ticks whose post-state phase is MEETING, so it missed one trigger
tick that also ended the game (s4 seed 3: the engine checks the win at the trigger and returns GAME_OVER). Everything
else in that row is identical, plus 4 sabotage repairs and 1 sabotage the memo did not list. The census must read the
recorded dispositions, not the event slice.

**New before-cells the assessment needs** (count-only, same walks):

| cell | s9 | pooled |
|---|---|---|
| exits into a room a crewmate occupied at the pre-tick | 53/85 | 250/512 |
| exits into a room the impostor could see and a crewmate occupied at the pre-tick | 31/85 | 134/512 |
| exits while a crewmate stood in the room being left at the pre-tick | 1/85 | 24/512 |
| vent trips lasting 2 ticks (the rest last 1) | 5/85 | 19/512 |
| entries within 2 ticks of the impostor's own kill | 97/105 | 512/587 |
| entries whose source room equals the destination room | 105/105 | 587/587 |
| play resumed after a meeting with an impostor still in a vent | 10/107 | 30/486 |
| play resumed with a corpse on the floor | 60/107 | 263/486 |
| corpse age at report (report tick minus kill tick): median / >=5 ticks / max | 4 / 46 of 135 / 29 | 4 / 216 of 623 / 32 |
| report openings whose recorded prompt carries the kill-tick body id (`body-p-N-T`) | 135/135 | 623/623 |
| ... every call carrying one (the extra are opener retries) | 138 | 642 |
| crew-witnessed kills held by a living witness at the next meeting / witness voted the killer / killer ejected | 3 / 3 / 2 | 20 / 19 / 12 |
| impostor EJECT ballots labelled `supported` | 44/46 | 178/183 |
| impostor ballots whose recorded target is a teammate | 0 | 0 (by the guard) |
| impostor ballots whose AUTHORED target was a teammate (`teammate_coerced`) | 1 | 13 (scorecard row 7) |

Two definitional facts fall out. **Entries already obey R7:** a vent entry's source and destination room are the same
room on all 587 (`engine/rules.py:140-141` requires it), so the physical rule changes exits only. **The body id leak is
the opening only:** every report opening carries it and no other speaker's prompt does.

---

## 2. The partial-record hypothesis against the code

**What holds.**

- A missing experiment config means the historical defaults (`orchestrator/experiment_config.py:1-6`,
  `normalize_experiment_config` `:137-142`); the baseline-9 rows carry none (0 `experiment_config` keys in
  `replays/samples/9p2i/replay-seed-0.jsonl` and `replays/ml_corpus/9p2i/replay-seed-1000.jsonl`). Default-OFF arms
  therefore leave c9, s4 and c4 byte-identical under `scripts/verify_samples.sh` and every walk.
- `RecordedExperimentConfig` already carries `meeting_reset`, `vent_exit_policy`, `bounded_rebuttal_version`,
  `self_report` (`orchestrator/experiment_config.py:29-47`), recorded per tick row (`orchestrator/replay.py:307-324`).
- The spectator loader reads recorded arms (`api/replay_loader.py:1454`, `:1810-1814` threads `meeting_reset`) and a
  versioned temporal stamp (`:787-792`), so `verify_samples.sh <dir>` can verify an arms-ON recording.
- The scorecard's two walks support experiments: routes via the process-scorecard profile
  (`eval/process_scorecard.py:773-788`), the report via the current-report profile (`eval/balance_eval.py:933-946`,
  used at `:715`). The scorecard can fold an arms-ON directory with `load_set_inputs` (`:835-874`).
- Craft rule 7's shape (default-OFF until an adopting record; graduation deletes the switch) fits experiment-config arms.

**Where it fails, exactly.**

| # | failure | where |
|---|---|---|
| F1 | Eight of eleven walk profiles raise `ValueError("... does not support experimental recordings")` on any recording whose rows carry an experiment config: validity-gate, evidence-honesty, kill-craft, kill-gift, solvability, win-condition-selfcheck, watchability-referee, funnel-instrument. So the per-leg validity gate and the `--honesty` first-seed probe (whose raise is a STOP) fail on seed 0. Only process-scorecard, current-report and leak-scan-factory support experiments. | `eval/replay_walk.py:503-515`; `eval/validity.py:508-516`; `eval/evidence_honesty.py:2605-2618`; `eval/kill_craft.py:527`; `eval/balance_eval.py:914-921`; `eval/solvability.py:698`; `eval/win_condition_selfcheck.py:205`; `eval/watchability.py:1544`; `eval/funnel.py:254` |
| F2 | The validity gate compares every game's substrate stamp to the BARE-shell snapshot, so a record with `temporal_observations` ON fails `cost_and_provenance_exact` in the bare shell the card requires (unlike the loader, which honours a versioned temporal stamp). B4 must not ride the temporal lever. | `eval/validity.py:960-993` vs `api/replay_loader.py:787-792` |
| F3 | The doc-fact gate requires all four recorded sets to share one model, one prompt-set token set and one substrate-flag stamp. Any arm that moves a prompt stamp on s9 alone (R10's ballot wording; any re-bodied template; prompt-byte arms must move stamps per `agents/strategic/prompts/loader.py:1300-1316`) or a flag stamp (the temporal lever) turns it red. It checks no experiment config at all, so arms-only changes pass it silently, which is itself a provenance gap. | `scripts/check_doc_facts.py:297-302`, `:2146-2273` (error at `:2258-2265`) |
| F4 | The recorder cannot set an engine, tactical or orchestrator arm: `scripts/run_tournament.py:244-470` has no experiment flag; arms are reachable only from `experiments/tactical_gameplay.py:99-109`. Meeting-profile arms reach it only through env (`AILIBI_BOUNDED_REBUTTAL`, `meetings/evidence_profile.py:14-31`, `:88-104`), and `HeadlessGame` raises if a passed config and the runner's profile disagree (`orchestrator/game.py:2253-2273`). `refresh_samples.sh` preflights only the five substrate toggles (`--expect-levers`, `:52-64`, `:302`); nothing preflights the arm slate. | as cited |
| F5 | Witnesses are event-only. The walker threads only `redistribution_policy` and `meeting_reset` (`eval/replay_walk.py:635-641`, `:754-761`); the rubric extractor threads nothing (`audits/workflows/extract_gameplay_facts.py:2235`, `:2751-2756`); the lab threads nothing (`experiments/tactical_gameplay.py:223`). A reconstructor that forgets an R7 arm passes every hash check and serves wrong witness sets. | `engine/rules.py:29-44`, `:146-156`; `engine/entities.py:43-49` (no witness in state) |
| F6 | Under `hub_with_grace` the rubric extractor's post-meeting hash mismatches every meeting (it calls `apply_meeting_result` without `meeting_reset`), so the 9p2i rubric step (`scripts/refresh_samples.sh:1049-1075`) floors every game. | `audits/workflows/extract_gameplay_facts.py:2751-2756` |
| F7 | The scorecard pools all four committed sets unconditionally and the published page hard-codes "These four sets are one era - baseline 9". An arms-ON s9 would be pooled across the boundary under a false sentence. | `eval/process_scorecard.py:1856-1861`, `:1883-1926`, `:1746-1761`; `scripts/publish_process_scorecard.py:252-259` |
| F8 | The frozen surrogate table refuses experimental recordings, and its tests walk s9. | `training/surrogate/dataset.py:1026`; `tests/training/test_surrogate_dataset.py:94`, `:109-256` |
| F9 | The MANIFEST has no arms column, so an arms-ON s9 reads as baseline 9 in its own manifest. | `scripts/_manifest_writer.py:155-196` |
| F10 | Publication. `pages.yml` rebuilds the demo from `replays/samples` on every push to main; four featured games are s9 seeds 23, 0, 29, 2 with count-bearing labels the journey spec binds. Merging an in-place candidate publishes the arms as the public face, which `AGENTS.md:21-26` calls a publication decision and which task completion never authorizes. | `.github/workflows/pages.yml:17-22`; `scripts/build_demo_bundle.py:90`; `frontend/src/components/ReplayPicker.tsx:109-150`; `frontend/e2e/journey.spec.ts:48-52` |
| F11 | The frozen watchability referee's baseline-9 floors are measured on s9 and are the default; bare `measure_baseline.py --watchability` would score candidate bytes against them (and the profile refuses them anyway, F1). | `eval/watchability.py:1039-1120`, `:1129`, `:2386-2390` |
| F12 | Test coupling: 72 files under `tests/` and `frontend/` name `samples/9p2i`; `tests/fixtures/phase10/corrected_w2_baseline.json` is "the current-era baseline" re-derived from s9 (`tests/eval/test_gate_spec_metrics.py:988-995`). The baseline-9 record re-pinned eight suites and left eight tests red (`audits/audit-2026-09-22-process-rerecord.md:1137-1235`). | as cited |

**The hypothesis also meets the direction's own text:** section 10 of `tasks/direction-2026-09-19-process-over-outcome.md`
says "Stop ... adding levers - five exist" (`:313-318`). New Stage-B switches should therefore be experiment-config arms
(recorded per row, read back by readers), never new `AILIBI_*` substrate levers.

---

## 3. Recommendation: a candidate record, not an in-place replacement

**Option B (recommended): record s9 seeds 0-49 into a candidate location.** Record into a scratch directory, push the
bytes to one orphan evidence commit, pin it in-tree at `replays/records/stage-b-candidate-1/` (`EVIDENCE-MANIFEST.md` +
`README.md` declaring the slate), exactly as `replays/records/phase-21-wave2-finding/README.md:1-60` does. Class (c) is
the registry's class for non-canonical evidence and its rule is "pinned sha" (`docs/artifacts.md:52-60`;
`scripts/verify_ml_evidence.py:2745`). `scripts/fetch_evidence.sh` restores it for the audit's commands.

Why, measured against the failures:

| | in place (A) | candidate (B) |
|---|---|---|
| F1 walk profiles | widen all eight (every test folds s9 through them) | widen only the validity gate (the per-leg gate) and add the census profile |
| F2 temporal stamp | avoid the lever | avoid the lever |
| F3 doc-fact gate | an invariant-gate amendment and an owner decision | untouched |
| F4 recorder | needed | needed |
| F5 witness threading | needed | needed |
| F6 rubric | must thread arms or the rubric floors | skipped by construction (`refresh_samples.sh:1049` runs only for `replays/samples/9p2i`) |
| F7 scorecard pooling | era-keyed pooling and a generated provenance paragraph | untouched; the candidate is folded alone |
| F8 surrogate | tests red | untouched |
| F9 manifest | arms column or a false manifest | the README and EVIDENCE-MANIFEST declare the slate |
| F10 publication | the merge publishes the candidate; featured labels false | nothing published; tour untouched |
| F11 floors | FAIL reported on every bare run | untouched |
| F12 re-pins | a large pass, repeated every round | none |
| ladder wording | "the samples set is a candidate while the tip is baseline 9" | true by construction |
| a second round | the whole cost again | one more pinned directory |

The owner's words are satisfied either way; what the owner did not ask for is a new public face or a re-pin pass.
**If the orchestrator keeps option A**, the card must carry all of F1-F12: era-keyed pooling in the scorecard with a
planted cross-era refusal, an owner-approved amendment of `check_vote_correctness_provenance` to key agreement by era,
an arms column in the manifest, re-pins or re-anchors of every s9-coupled test onto c9, the featured list re-run by the
spectator card's measured criterion (commit `1bf839da` is the precedent) or the four s9 entries withheld, no floor block
for an unadopted slate, and a README sentence that the shown 9-player samples are a candidate.

The local viewer can still show the candidate: point `AILIBI_REPLAY_DIR` at the restored parent
(`api/main.py:41`, `:121-160`).

---

## 4. A1: the gameplay census instrument

### 4.1 Shape (mirrors the scorecard; reuse, not re-implementation)

- **`eval/gameplay_census.py`.** An impure loader `load_census_inputs(set_dir) -> CensusInputs` and a pure fold
  `fold_set(inputs) -> CensusTally`, so every cell is plantable from a hand-built carrier with no replay on disk (the
  `SetInputs` pattern, `eval/process_scorecard.py:744-760`). `pool(tallies)` adds counts; rates recompute from the
  pooled numerator and denominator (`:1746-1761`).
- **Walk profile `gameplay-census`:** `dataclasses.replace(_CURRENT_REPORT_WALK_CONFIG, profile="gameplay-census",
  missing_meeting_row="violation", reject_duplicate_meeting_rows=True, require_terminal_tick=True)` (the lab's
  precedent, `experiments/tactical_gameplay.py:199`, `:363`). It verifies tick hashes, dispositions, meeting post hashes
  and chronology, and supports experiments and temporal delivery. Post-hash verification is what proves a recorded
  `hub_with_grace` reset was reproduced before the B2 cells read post-meeting state. Add its row to the drift table in
  the `eval/replay_walk.py` docstring (`:88-115`).
- **Thread-or-refuse guard (closes F5 for the census).** A classification of every `RecordedExperimentConfig` field as
  engine-threaded, agent-only or meeting-only, owned beside the walker; the walk raises on an engine-affecting field it
  does not thread. A test enumerates `RecordedExperimentConfig.model_fields` and fails on an unclassified field, so the
  R7 arm cannot land without its threading.
- **Roles** from `eval.validity.roles_by_seed`; **set lists** imported from `eval.process_scorecard.COMMITTED_SETS` /
  `NINE_PLAYER_SETS` (one list); **the vent band** is the scorecard's own rule, a `vent_sighting` flag naming the
  ejected player (`eval/process_scorecard.py:1115-1119`), not the synth's `"vent" in kind`.
- **Carrier facts, per game** (ids, rooms, ticks, kinds, labels only): kills (tick, actor, target, room, witnesses);
  vent acts (tick, kind, actor, source/destination room, source/destination/union witnesses, pre-tick rooms of living
  players, the impostor's sight set); body -> kill tick, joined when the body first appears in state to the
  `KilledEvent` of its victim on that tick, **never parsed from the id** (the id embeds the tick, `engine/rules.py:87`);
  meetings (typed trigger from `MeetingTriggeredEvent`, opener, trigger body, bodies at open with `discovered_by`,
  in-vent and cooldowns at open, living, outcome, ejected, flags, turns with index/speaker/kind/reply_to/accusations,
  ballots with voter, recorded target, authored target from `guard_redirected_from`/`guard_rewrite_reason`, grounding
  label); post-apply phase, in-vent and bodies; discarded action types from recorded dispositions; one boolean per
  meeting "the opener's first recorded prompt carries a `body-p-N-T` handle", computed in the loader so no text leaves it;
  the era key (normalized experiment config, substrate stamp, prompt-stamp set).
- **Era-keyed pooling.** `pool` raises if two tallies carry different era keys. On baseline 9 all four agree; the
  refusal is what keeps any future candidate or partial record from being averaged into the baseline.
- **Cost.** 300 games walk in 4.4 s through this profile family; the output is deterministic (two runs byte-identical).
  Register the census walk in `tests/_helpers/committed.py` (the single-home rule, `:1-30`).

### 4.2 Cells (denominator, events read, behaviour under each Stage-B arm)

Crew-only witnesses throughout. "Conf." marks a cell that becomes 0 by construction under an arm: the publisher renders
it as "0 by construction (arm)" only after asserting the count is 0, and raises otherwise.

| # | cell | numerator / denominator | reads | under the arms |
|---|---|---|---|---|
| C1 | kills seen | kills with a crew witness / kills | `KilledEvent.witnesses` | unchanged meaning |
| C2 | entries seen | entries with a crew witness / entries | `VentEnteredEvent.witnesses` | R7: unchanged (source = destination on 587/587) |
| C3 | exits seen | exits with a crew witness / exits | `VentExitedEvent.witnesses` as recorded | R7: reads the physical rule; compare against C4, not C3-before |
| C4 | exits seen in the exit room | exits with a crew destination witness / exits | `destination_witnesses` | the like-for-like B1 cell across R7 (s9 53/85) |
| C5 | exits seen only from the room left | crew source witness and none at destination / exits | both witness fields | R7: Conf. |
| C6 | exits into a visibly occupied room | destination in the impostor's sight set and a crewmate there at the pre-tick / exits | pre-tick state, map adjacency | B1 behavioural |
| C7 | exits into any occupied room | crewmate in the destination at the pre-tick / exits | pre-tick state | B1 behavioural |
| C8 | exits while the room left is occupied | crewmate in the source room at the pre-tick / exits | pre-tick state | B1 behavioural |
| C9 | vent trip length | exits by trip length in ticks | entry and exit ticks per actor | B1: the "waits inside" cell; capped waits counted separately |
| C10 | entries after the impostor's own kill | entries within K ticks of the actor's own kill in that room / entries | `KilledEvent`, `VentEnteredEvent` | B1 behavioural ("vent only after own kill") |
| C11 | impostor fate | per impostor: seen venting / vented unseen / never vented, each x ejected | vent events, meeting outcomes | unchanged meaning |
| C12 | vent-proof meetings | meetings with a `vent_sighting` flag naming a living player / meetings | recorded flags | unchanged; expected to fall |
| C13 | vent-band ejections | ejections whose ejected player a `vent_sighting` flag names / ejections | recorded flags | unchanged |
| C14 | which vent moment convicts | vent-band impostor ejections by crew-seen exit only / entry only / both before the meeting tick | vent events | R7: the exit-only share shrinks by construction |
| C15 | convictions resting only on the room left | vent-band ejections whose living crew witnesses saw only an exit from the source room | vent events, living set | R7: Conf. |
| C16 | no-vent meetings: eject / skip / impostor share | per outcome / no-vent meetings | flags, outcomes | unchanged |
| C17 | button meetings carrying vent proof | / button meetings | typed trigger, flags | unchanged; expected to fall |
| C18 | stale reports | report meetings whose trigger body was in state at the previous meeting's open / report meetings | bodies at open | B2: Conf. |
| C19 | corpse age at report | distribution of report tick minus kill tick | body-kill join | B2: bounded by ticks since the last meeting's close (a conformance bound) |
| C20 | meetings opening with another unreported corpse | / meetings | bodies at open | B2: meaning narrows to this inter-meeting window |
| C21 | play resumes with an impostor in a vent | / meetings resolving to PLAY | post-apply state | B2: Conf. |
| C22 | play resumes with a corpse on the floor | / meetings resolving to PLAY | post-apply state | B2: Conf. |
| C23 | post-meeting kills within the grace window | kills within 2 (and 4) ticks of a meeting / post-meeting kills | `KilledEvent` ticks | B2: Conf. (cooldown restarts at 4, `engine/meeting_reset.py:36-40`) |
| C24 | meetings opening with an impostor in a vent | / meetings | state at open | NOT zeroed by B2; B1 waiting may raise it |
| C25 | impostor cooldown 0 at meeting open | / impostor-meeting slots | state at open | unchanged |
| C26 | first reply accuses the opener | / meetings | turn 1 accusation claims | unchanged (the rebuttal is appended after roll-call, `meetings/manager.py:1508-1538`) |
| C27 | opener answered | meetings where a later speaker accused the opener and the opener spoke again after it / meetings where a later speaker accused the opener | turns, `reply_to` | B3 behavioural; Conf. 0 while `bounded_rebuttal_version` is None |
| C28 | rebuttals to someone other than the opener; second rebuttals | counts | turns | B3: second rebuttals Conf. 0 |
| C29 | opener share of innocent ejections, report and button split | / innocent ejections | outcomes, typed trigger | unchanged |
| C30 | impostor openers | / meetings | opener role | Conf. 0 while `self_report` is False and `contextual_self_report_version` is None (R6 OFF) |
| C31 | kill-tick handle in report openings | openings whose first recorded prompt carries `body-p-N-T` / report meetings | loader boolean | B4: Conf. |
| C32 | witnessed kills held and cited | crew-witnessed kills with a living witness at the next meeting; of those, witness ballots citing an own-evidence kill row | kills, ballots | R8 behavioural; the cited part is Conf. 0 before R8 |
| C33 | impostor ballots | SKIP / EJECT / EJECT labelled `supported` / authored teammate targets | ballots, guard fields | R10 behavioural; authored teammate targets must be 0 |
| C34 | actions thrown away on trigger ticks | by action type | recorded dispositions | unchanged (context) |

The win split and role-correct ejections are reported beside, read from the MANIFEST and outcomes, gating nothing.
No cell joins the nine-row scorecard (ruling R13; no D1 amendment).

### 4.3 Vacuity guards

- **Empty denominator** renders `n/a`, never `0%` (the scorecard's `RateCell` convention, `eval/process_scorecard.py:390-432`).
- **Arm-vacuous cells (Conf.)** carry the predicate that vacates them (for example `meeting_reset == "hub_with_grace"`
  for C18, C21, C22, C23). The publisher asserts the count is 0 and raises `GameplayCensusConformanceError` naming
  (set, seed, meeting) otherwise. A 0 is never published as a measured improvement.
- **Planted per guard:** one hand-built tally per Conf. cell with its arm ON and one violating fact (for example a
  stale report under `hub_with_grace`); the publisher must raise. The same fact with the arm OFF publishes `1/N`.

### 4.4 Publisher

`scripts/publish_gameplay_census.py`, a copy of the scorecard publisher's shape
(`scripts/publish_process_scorecard.py:54-82`, `:317-357`): destinations pre-flighted through `_report_output` with
every `replays/**` path, the recording roots and the census's own inputs protected; `docs/gameplay-census.md` and
`docs/gameplay-census.json` per set, pooled 9p2i and pooled four; `--check` recomputes and exits 1 on drift, naming the
regenerate command. **Add `--set-dir DIR --json-stdout`**: folds one directory and prints JSON to stdout, writing
nothing, for a candidate record. The page opens with the role-correctness note and says it is not the scorecard.

### 4.5 Planted tests

1. An exit seen only from the room left counts as seen (C3) and in C5; moving that crewmate out of the source room at
   the pre-tick flips both.
2. A stale corpse (C18) flips to fresh when its kill moves after the previous meeting's open.
3. Moving a `vent_sighting` flag onto a living, non-ejected player takes that ejection out of the vent band (C13) while
   the meeting stays vent-proof (C12): the two denominators are different cells on purpose (330 meetings vs 326 ejections).
4. A body whose id encodes a tick different from its victim's `KilledEvent` tick: C19 reads the event tick (proves the
   census never parses the id).
5. A game-ending trigger tick's discarded move is counted (the 808/809 case).
6. The authored teammate target is counted even though the recorded target is SKIP (C33).
7. Pooling two tallies with different era keys raises.
8. One conformance breach per Conf. cell raises (4.3).
9. The thread-or-refuse guard fails on an unclassified experiment field.
10. `check_report` is green on the tree, red on one edited cell, red on a missing file; the writer refuses a recording
    destination before computing.

### 4.6 Acceptance

`uv run python scripts/publish_gameplay_census.py --check` green, and the committed JSON reproduces section 1:
20/849, 73/587, 313/512 (251 and 62), 330/355, 13/89, 26/56, 330/346 meetings with 326/43 ejections, 326 = 253 + 10 + 63,
50 on the room left, 167/551 stale on 9p2i, 335/676, 521/676 and 0/676, 38/42, and the trigger-tick row with **809**
moves. `bash scripts/check.sh` passes. No re-record, no byte of `replays/` moves.

Expected files: `eval/gameplay_census.py`, `scripts/publish_gameplay_census.py`, `docs/gameplay-census.md`,
`docs/gameplay-census.json`, `tests/eval/test_gameplay_census.py`, `tests/scripts/test_gameplay_census.py`,
`tests/_helpers/committed.py` (the cache), `eval/replay_walk.py` (docstring table, and the field classification if it
lives there), `docs/artifacts.md` (a row like the scorecard's), `docs/glossary.md` if a term needs defining.

---

## 5. B5: the 50-seed record

### 5.1 Prerequisites (each lands, with its planted case, before the freeze)

1. The Stage-B arms, each a `RecordedExperimentConfig` field defaulting to the historical behaviour, with its thread
   through every reconstructor (`eval/replay_walk.py`, `api/replay_loader.py`, `experiments/tactical_gameplay.py`) and
   the thread-or-refuse classification. A new field must not change a historical config's serialized bytes (the
   version-preserving serializer, `orchestrator/experiment_config.py:96-106`; the frozen format-3 fixture round-trips).
2. Recorder plumbing: `scripts/run_tournament.py --experiment-config <json>` passed to `HeadlessGame` and
   `build_default_agent_factory` (`orchestrator/game.py:4437-4460`), with the tactical-policy stamp an experimental
   factory needs when a reader claims a policy (`api/replay_loader.py:636-662`); `scripts/refresh_samples.sh
   --expect-arms <json>` that refuses, before any seed stages, a resolved slate (flag plus `AILIBI_BOUNDED_REBUTTAL`)
   differing from the declared one, and prints it in `--dry-run`.
3. The validity-gate profile supports experiments, with a planted case: an arms-ON fixture verifies, and the same fixture
   walked with its reset dropped fails the post-hash check.
4. The census (A1) merged, so the before column comes from the shipped tool.
5. A **fake-provider dress rehearsal**: `AILIBI_LLM_PROVIDER=fake` records seeds 0-49 on the slate into a scratch
   directory (the recorder refuses a fake write under `replays/`, `scripts/refresh_samples.sh:615-639`); run the census
   conformance cells, the scorecard fold, the validity gate and `verify_samples.sh <dir>` on it. $0, and it proves the
   wiring before any spend.

### 5.2 The slate

s9 roster (9 players, 2 impostors, 2 tasks per crewmate), seeds 0-49, provider `featherless`, model
`Qwen/Qwen3.6-27B`, `AILIBI_PROMPT_SET=qwen3_6_27b`, substrate slate bare (`--expect-levers ""`). Arms ON:

| mechanism | arm (names illustrative; each card fixes its own) |
|---|---|
| B1 | `vent_exit_policy` = the new look-first value |
| R7 | a new engine arm, physical vent witnesses (exit witnessed by the room surfaced into only) |
| B2 | `meeting_reset = "hub_with_grace"` (the full reset: survivors regrouped, corpses and vents cleared, cooldown restarted; `engine/meeting_reset.py:10-41`) |
| B3 | `bounded_rebuttal_version = 1`; `reporter_reasoning` OFF |
| B4 | a body-handle arm switching only `described_body` to `public_body_id` (`orchestrator/game.py:3459-3465`); NOT the `temporal_observations` lever (F2, F3) |
| R8 | a witnessed-kill own-evidence row arm |
| R10 | the impostor-ballot arm (a prompt-byte arm with its own stamp overlay) |
| R6 | `self_report = False`, `contextual_self_report_version = None` |

### 5.3 Ceilings (for the owner to confirm)

Baseline-9 s9 leg: 1,694 calls, 9,850,930 input, 422,941 output, 2h24m55s on two workers
(`audits/audit-2026-09-22-process-rerecord.md:415`). Per meeting: 11.68 calls; per call 5,815 input and 250 output.
Movement is two-sided: in fake-provider lab games the reset cut 9-player calls 676 -> 484 and the vent-risk exit raised
them to 738 (`audits/tactical-gameplay/README.md:122-129`). B3 adds at most one call per meeting.

| | low (meetings x0.72, +1 call/meeting) | high (meetings x1.25, +1 call/meeting, +10% prompt) | proposed ceiling |
|---|---|---|---|
| calls | 1,322 | 2,297 | **2,500** |
| input tokens | 7.7 M | 14.7 M | **16,000,000** |
| output tokens | 330 k | 574 k | **700,000** |
| recording wall | 1h53m | 3h16m | **4 h**, inside an **8 h** window |
| marginal cost | $0.00 | $0.00 | **$0.00** (flat-rate; the statement is required, `AGENTS.md:89-91`) |

Re-project after the probe and after ten seeds, matched seed by seed against the baseline-9 bytes of the same seeds
(the section 2.2 method, `audits/audit-2026-09-22-process-rerecord.md:466-488`); stop and report if any projection
passes 90% of its ceiling.

### 5.4 Operating rules (carried from the previous card, adjusted)

- **Probe.** `--seeds 0`, then the probe, then `--seeds 1-49` (the two-phase shape, `tasks/work/process-rerecord.md:399-405`).
  The probe is the census conformance cells + the validity gate + the scorecard fold on the probe seed; a meeting-free
  probe is VACUOUS and re-runs on seeds 0-3. `measure_baseline.py --honesty` refuses arms-ON bytes (F1); keep it out of
  the probe unless its profile is widened before the freeze.
- **Stop rule.** Any `cost_usd` other than 0.0000; a leg past 1.5x its projected wall; a projection past 90% of a
  ceiling; a provider refusal surviving the eight-attempt retry budget; any conformance breach (a corpse after a
  meeting, a kill-tick handle in an opening, a second rebuttal, an in-vent impostor when play resumes) - that is a code
  defect, not a result.
- **Stall watchdog.** No completed seed for 45 minutes: kill and re-run the batch, or relaunch a fresh operator from the
  pushed checkpoint. A seed on disk never re-records to recover from a stall.
- **`(deadline_default)`.** A row carrying it is a failed recording; that seed alone re-records, the cause logged as it
  happens. No seed re-records for any other reason.
- **Keys.** The operator exports `FEATHERLESS_API_KEY` in the recording shell only; no step reads `.env`; every gate runs
  in a bare shell with the `AILIBI_*` count printed as 0; a count-only key scan over every new byte before any push
  (`audits/audit-2026-09-22-process-rerecord.md:1547-1568`).
- **Checkpoints.** Push after the probe and after the leg (to the evidence commit under option B; a checkpoint commit
  under option A).
- **Derived views.** `tournament-eval-report.json.gz` through `scripts/build_sample_report.py --sample-dir <dir>` and
  `eval/report_io.py`; under option B the rubric step does not run and `corrected_w2_baseline.json` is not regenerated.
- **Freeze.** From the first seed until the pull request merges, nothing merges into `engine/`, `agents/`, `meetings/`,
  `observation/`, `orchestrator/` or the prompt set; the audit shows the window's `git log` for those paths.

### 5.5 Before column, committed before the first seed

s9 on baseline 9, from the shipped census and scorecard (section 1 numbers; scorecard `docs/process-scorecard.md:133-166`):
grounded EJECT 494/496, grounded SKIP 79/349, deviating crew EJECTs 31/413, manufactured 0/17 (17 not evaluable),
unexplained 5/845, evidence mix vent 70 / contradiction 2 / first-hand 16 / hearsay 2 of 90, faithfulness 708/708,
agent-authored 841/845, wrong-but-believable 119/496, role-correct ejections 81/90, impostor wins 11/50.

### 5.6 The assessment the owner asked for

The after column is s9 only and is never pooled with the untouched sets. **Conformance** cells must read exactly as
built; a miss is a defect, reported and blocking adoption. **Behavioural** cells carry a stated reading, published with
a Wilson interval, and are not bars. The arms land together, so only by-construction cells attribute to one arm.

| mechanism | cell | s9 before | effective means | kind |
|---|---|---|---|---|
| B1 | C4 exits seen in the exit room | 53/85 | the share falls | behavioural |
| B1 | C6 exits into a visibly occupied room | 31/85 | near 0 (the rule forbids it unless forced after N waits); forced exits counted | behavioural, near-conformance |
| B1 | C8 exits while the room left is occupied | 1/85 | stays near 0 | behavioural |
| B1 | C9 trips longer than one tick; capped waits | 5/85; n/a | rises; no trip exceeds the cap | behavioural; the cap is conformance |
| B1 | C10 entries after own kill | 97/105 | 105/105 if the rule ships | conformance if specified |
| R7 | C5 exits seen only from the room left; C15 | 9/85; 8 | 0 | conformance |
| B2 | C18 stale reports | 43/135 | 0 | conformance |
| B2 | C19 corpse age at report | median 4, max 29 | bounded by ticks since the last close | conformance bound; distribution reported |
| B2 | C21, C22 play resumes with a vented impostor / a corpse | 10/107; 60/107 | 0; 0 | conformance |
| B2 | C23 post-meeting kills within 2 ticks | 28/87 | 0 | conformance |
| B3 | C27 opener answered | 0/125 | rises toward the accused count; C28 second rebuttals 0 | behavioural; C28 conformance |
| B4 | C31 kill-tick handle in openings | 135/135 | 0 | conformance |
| R8 | C32 witnessed kills cited as own evidence | 3 held, 0 citable | the witness cites the row when it holds one | behavioural; about 3 events in 50 games, so no power |
| R10 | C33 impostor EJECTs labelled `supported`; authored teammate targets | 44/46; 1 | every impostor EJECT supported; 0 teammate | conformance on the teammate cell; the rest behavioural |
| beside | C12 vent-proof meetings, C13 vent band, win split, role-correct ejections, scorecard rows 1-9 | 70/145; 70; 11/50; 81/90 | reported, gating nothing | reported |

Read C3 after against C4 before, not C3 before: R7 alone removes the 9 room-left exits. Read the fall in vent convictions
knowing R7 removes about 8 of 70 by construction. The owner already accepted that the voting statistics move.

### 5.7 What the record does not decide, the ladder, the docs, the demo, ML, the gates

- **Does not decide:** adoption (flipping defaults), graduation (deleting switches), re-recording c9, s4 or c4, the
  featured tour (ruling 11 defers it), any ML work (ruling 12), R6's revisit, whether a second round runs.
- **Ladder wording:** "The ladder tip stands at baseline 9. The stage-B record is a candidate recorded on the arms named
  below; it adopts nothing." `_LADDER_TIP_AUDIT` (`scripts/check_doc_facts.py:237`) stays on the baseline-9 record; the
  new audit repeats the tip sentence with 9, so the tip check (`:1751-1781`) still reads one tip.
- **Doc facts and floors (option B):** a class-(c) row in `docs/artifacts.md` plus its probe key in
  `scripts/verify_ml_evidence.py:2754` (the registry key set is cross-checked, so a row without a probe fails); the
  `audits/README.md` index row; no watchability floor block for an unadopted slate; `docs/gameplay-census.*` and
  `docs/process-scorecard.*` untouched (the candidate's columns live in the audit, reproduced by `--set-dir`).
- **Demo:** nothing moves under option B. Under option A the minimal handling is re-running the existing measured
  criterion on the four s9 entries, or withholding them; the A2 re-pick stays deferred.
- **Corpus freeze and ML keying:** untouched under option B by construction (`BAKEOFF_BASELINE_ID`, the fits'
  `fit-corpus.json` and `splits.json` all key on `replays/ml_corpus`). Under option A the surrogate tests break (F8).
- **Owner gates:** the ceilings; option A or B; where the candidate lives (pinned commit or in-tree, the open question
  `replays/records/phase-21-wave2-finding/README.md:43-48` records); the push of the evidence commit; the merge. Under
  option A the merge also publishes, and F3 needs an owner-approved gate amendment.

---

## 6. A3: documentation truth and the typed trigger kind

### 6.1 The out-of-date text the analysis names (Q7 item 6; re-verify each at the card's base)

`meetings/schemas.py:983-991` ("every committed recording reads None" - baseline 9 carries labels) and `:1081-1083`;
`meetings/manager.py:4294`, `:4522`; `meetings/voting.py:29`; `agents/memory/beliefs.py:220-221`; `agents/memory/store.py:94`;
`engine/maps/canonical_1.yaml:50-53`; DESIGN section 3.5 plus `engine/tick.py:399` ("DESIGN 3.5 (dropped)" while the map
redistributes) and `observation/service.py:670-673`; the glossary's "hard evidence" entry (`docs/glossary.md:157`);
`docs/architecture.md:116-120` (no baseline 9); `training/README.md:119-122` (baseline-6 corpus, verified);
`training/rewards.py` `correct_reports` and `patrol_coverage` (role-correct rewards). Plus the game-shape facts note and
the ML-README history label the plan lists.

### 6.2 The typed `MeetingTrigger` kind

Today the meeting layer decides emergency versus report by substring: `_trigger_is_emergency` returns
`EMERGENCY_TRIGGER_PHRASE in trigger.description` (`meetings/manager.py:598`, `:932-943`), used at `:1286`, `:1558`,
`:1887`, `:2138`, `:2218`; `tests/_helpers/committed.py:382-392` re-derives it the same way. The orchestrator already
holds the typed kind from the engine event (`orchestrator/game.py:3405-3440`) and drops it when building the DTO
(`:3477`).

- Add `kind: MeetingTriggerKind` (the existing `Literal["report", "emergency"]`, `meetings/transcript.py:356`) to the
  frozen `MeetingTrigger` (`meetings/manager.py:907-929`), **required**, no default (a default would silently file an
  emergency as a report). `_trigger_is_emergency` reads `trigger.kind`.
- Construction sites: `orchestrator/game.py:3477`, `eval/reasoning_evidence.py:284`, and about 35 test sites
  (tests/meetings, tests/orchestrator, tests/training, tests/agents).
- **Templates keep their substring branch** (`crewmate_report.j2:83`, `impostor_report.j2:70`,
  `impostor_report_roll_call.j2:67` in `qwen3_6_27b`): editing them risks the version-bump cascade for zero byte change.
  Pin the lockstep instead: for every trigger the production builder can construct, the typed kind equals the template's
  substring test.
- **Planted test (fails today):** a `report` trigger whose description contains "called an emergency meeting" is still
  treated as a report, observed through the reporter render id (`meetings/manager.py:2218`) or the contradiction trigger
  kind (`:1557-1559`). On today's code the substring wins and the assertion fails.
- **Acceptance:** prompt-byte golden tests and `verify_samples.sh` unchanged; the census and scorecard `--check` green.
  The census never reads this DTO: it takes the kind from `MeetingTriggeredEvent.trigger`.

### 6.3 Is A3 file-disjoint from the other cards? No.

| file A3 edits | also edited by |
|---|---|
| `orchestrator/game.py` (`_build_meeting_trigger`, `:3405-3480`) | B4, the same function (`:3459-3465`) |
| `meetings/manager.py` | R8, R10, possibly B3 |
| `agents/memory/store.py`, `agents/memory/beliefs.py` | R8 (own-evidence rows; `store.py:2244-2249` is the seen-kill citation site) |
| `engine/tick.py` (comment at `:399`) | R7 (threading the witness arm) |
| `docs/architecture.md` (`:116-120`, and B4's limitation at `:131-133`) | B4, B5 |
| `docs/glossary.md` ("hard evidence") | R8 |
| `tests/_helpers/committed.py` (`:382-392`) | A1 (the census cache) |

Land A3 first, or split it into a docs-only half and a typed-trigger half sequenced before B4.

---

## 7. Could not establish, and limits

- Real-model call counts under the combined slate: the lab figures are fake-provider games in both directions.
- Whether R8 and R10 re-body templates (that decides whether a prompt stamp moves, F3 under option A).
- The exact number of tests an in-place record would turn red; 72 files name s9 and the last record re-pinned eight suites.
- B3's selector gives the extra turn to the earliest pending new charge (`meetings/rebuttal.py:17-50`); structurally the
  opener gets it whenever turn 1 accuses the opener, otherwise it can go to someone else. Never run with a real model.
- R8 has about three events per 50 games on s9: its cell has no power at this size.
- The analysis's "62 entries with no recent own kill" is not re-derived; my own definition (own kill within 2 ticks)
  gives 75 of 587 without one. It is not in this card's acceptance list.
- The arms land together; except for by-construction cells, the record cannot attribute a change to one arm.
