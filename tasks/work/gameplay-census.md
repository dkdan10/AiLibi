# A1: the gameplay census report

**Status:** ready

## Outcome

The project gains a second committed report, beside and separate from the nine-row process
scorecard: a count of what happens in the games themselves. It folds the four committed sets,
with zero model calls, into cells for vent entries and exits and who saw them, kills and their
witnesses, corpses at each meeting, the state play resumes in, the meeting's speaking order, and
the impostors' ballots. Every cell publishes its numerator, its denominator, its not-evaluable
count and the event kinds it reads, per set and pooled within one era. Every cell that a Stage-B
arm makes zero by construction carries that arm's predicate and a guard that raises on a breach,
so the record card can stop on a code defect instead of reading it as a result.

`scripts/publish_gameplay_census.py` writes `docs/gameplay-census.md` and `.json`; `--check`
recomputes both and fails on drift; `--set-dir DIR --json-stdout` folds one directory (the
round-1 candidate, or a scratch rehearsal) and writes nothing. The committed pages stay on
baseline 9 through the whole wave. No agent behaviour, prompt byte, schema field, detector,
recorded byte or scorecard row moves. Role-correctness is reported beside, gates nothing, and
feeds nothing back to any agent. Wave 0, card 2 of the decision memo's section 3.1 table.

## Evidence

Line numbers below are at `e886b663`; the implementer re-anchors each by the symbol named with it
before editing. The memo paths are under
`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/stage-b-2026-09-24/`:
`decision-memo.md` sections 0, 2.6, 3.2, 3.4 card 2 and 4, and `census_and_record.md` sections 1
and 4 (this card's investigation).

**Rulings relied on.** The owner's rulings of 2026-09-24, verbatim: "We should implement stage B";
and on the record, "Let's not re-record all 300 seeds each time. When it's time to record, record
the smaller group of 50 seeds, assess if the implementations have been effective and resulted in
desired results." The census is the instrument that assessment reads. "Hold off on ML as D
suggests until gameplay is finished." and "Tour fix can be deferred to after gameplay is finished"
keep it away from training code and the viewer. The orchestrator's rulings under the owner's
delegation of 2026-09-24 ("What do you think is best?"): **R13**, "the gameplay census stays a
separate published report beside the nine-row scorecard; no cell joins the scorecard; no D1
amendment", with candidate columns computed by `--set-dir` modes that write nothing; **R6**,
impostor self-report stays OFF, which the census reports as a conformance cell; decision 0.3
item 6, a recorded arm value's meaning is frozen once round 1 is recorded; decision 0.3 item 9,
the pending-arm guard.

**Every acceptance figure reproduces today.** Re-measured on 2026-09-24 at `e886b663` with the
investigation's count-only walk (`scratchpad/census_rec/walk2.py` through the process-scorecard
walk profile, then `cen.py`); its output was byte-identical to the investigator's walk. Scratch
scripts are not an instrument: every figure is re-measured at dispatch by the committed census,
and a difference is reported in Results, never pinned over.

| cell | s9 | 9p2i pool | four-set pool |
|---|---|---|---|
| kills seen by crew | 3/175 | 19/725 | 20/849 |
| vent entries seen by crew | 19/105 | 64/501 | 73/587 |
| vent exits seen by crew | 62/85 | 271/435 | 313/512 |
| exits seen from the exit room / only from the room left | 53 / 9 | 226 / 45 | 251 / 62 |
| impostors seen venting / vented unseen / never vented: ejected | 70/77, 3/8, 8/15 | 284/304, 13/56, 25/40 | 330/355, 13/89, 26/56 |
| meetings with vent proof / without | 70 / 75 | 285 / 309 | 330 / 346 of 676 |
| impostor ejections in the vent band / without vent proof | 70 / 11 | 281 / 41 | 326 / 43 |
| vent band by moment: exit only / both / entry only | 51 / 2 / 17 | 217 / 10 / 54 | 253 / 10 / 63 |
| vent-band ejections resting only on crew in the room left | 8 | 37 | 50 |
| stale report meetings | 43/135 | 167/551 | 167/623 |
| meetings opening with another unreported corpse | 74/145 | 325/594 | 335/676 |
| first reply accuses the opener | 120/145 | 448/594 | 521/676 |
| opener speaks a second time | 0/145 | 0/594 | 0/676 |
| openers among innocent ejections | 7/9 | 37/41 | 38/42 (37 report, 1 button) |
| moves thrown away on trigger ticks | 188 | 754 | 809 |

The same walk gives the before values the record card's assessment table quotes (s9; pooled):
play resumes with an impostor in a vent 10/107 (30/486) and with a corpse 60/107 (263/486);
post-meeting kills within 2 ticks 28/87 (135/389); meetings opening with an impostor in a vent
29/145 (101/676); impostor ballots 210 with 164 SKIP, 46 EJECT, 44 labelled `supported`; the
opener accused after turn 0 in 125 (561) meetings; impostor openers 0/676; repeat-speaker turns 0;
411 pooled ejections (369 impostor, 42 crew); 623 report and 53 button meetings. The ruled entry
gate (own victim in that room, killed at most 3 ticks earlier, no meeting between) removes 13 of
105 s9 entries and 103 of 587 pooled (`scratchpad/synth_b/entry_gate.py`, re-run). From the
memos, not re-run here: 135/135 s9 report openings (623/623 pooled) carry the kill-tick body id,
on 632 calls (s9 138, c9 422, s4 36, c4 36; decision memo 0.4); exits into a room the impostor
could see and a crewmate occupied, 31/85 (134/512), measured on the engine's sight set; crew kill
witnesses alive at the next meeting / voting the killer / killer ejected, 3/3/2 (20/19/12);
ejections whose confidence floor only impostor ballots met, 0 of 411.

**One definitional correction is already known.** The analysis memo's 808 thrown-away moves is
809: read from the recorded `action_dispositions` (`orchestrator/replay.py:206`), a trigger tick
that also ended the game (s4 seed 3) counts; slicing events on meeting-phase ticks misses it.

**The shape to copy exists.** `eval/process_scorecard.py` separates an impure loader from a pure
fold over a hand-buildable carrier (`SetInputs` `:745`, `load_set_inputs` `:835`, `fold_set`
`:1293`, `pool` `:1746`), publishes `RateCell` (`:390`) with an `n/a` rule for an empty
denominator, takes its set lists from `COMMITTED_SETS` / `NINE_PLAYER_SETS` (`:1856`, `:1862`)
and defines the vent band as a `vent_sighting` flag naming the ejected player (`:1116`). Its
publisher (`scripts/publish_process_scorecard.py`: `protected_inputs` `:54`, `publish` `:317`,
`check_report` `:331`) preflights every destination through `scripts/_report_output.py`, and it
states "These four sets are one era" as fixed text (`:252`), which the census must not copy: the
census derives the era from the recordings.

**Why the census needs its own walk profile.** Eight of eleven walk profiles refuse any recording
that carries an experiment config (`eval/replay_walk.py:505-508`). The current-report profile
supports experiments and verifies tick hashes, dispositions, meeting post hashes and chronology
(`eval/balance_eval.py:933-949`); the lab derives its profiles from it with `replace`
(`experiments/tactical_gameplay.py:199`, `:363`). Vent witnesses live only in engine events,
never in state, so a walk that forgets an engine arm passes every hash check with wrong witness
sets (census memo F5); the census must refuse any field it does not thread.

**Facts the cells rest on.** The body id embeds the kill tick (`engine/rules.py:87`), so the
census joins a body to its victim's `KilledEvent`, never to the id. After a regroup the impostor
kill cooldown restarts at the map's `kill_cooldown_ticks` (`engine/meeting_reset.py:36-40`, 4 at
`engine/maps/canonical_1.yaml:34`); a kill needs cooldown 0 at validation (`engine/rules.py:82`),
so after a meeting at tick T kills are illegal at T+1 to T+4 and first legal at T+5 (decision memo
0.4). The rebuttal is the only turn by a player who already spoke (`meetings/manager.py:1508-1539`,
`select_bounded_rebuttal` at `meetings/rebuttal.py:17`). The emergency button cooldown is 6 ticks
(`EMERGENCY_COOLDOWN_TICKS`, `agents/tactical/crewmate_policy.py:109`). An in-vent impostor gets no
visible-room list; the ruled exit policy infers own room plus map neighbours, and own room only
under any active sabotage (`vent_witness_and_exit.md` section 1.3). The tree's one kill-tick handle
pattern is `LEGACY_BODY_HANDLE_PATTERN` (`experiments/held_out_prefixes.py:168`). A MANIFEST row for
a game with no meeting records no prompt stamp: 11 of 50 rows in `replays/samples/4p1i` and 7 of 50
in `replays/ml_corpus/4p1i`. Authored teammate targets (`teammate_coerced`) are 1 on s9 and 13
pooled (`docs/process-scorecard.md:164`, `:57`).

## Acceptance

Unless an item names another mechanism, it is enforced by `tests/eval/test_gameplay_census.py`
over hand-built carriers, with no replay on disk.

- [ ] **Shape.** `eval/gameplay_census.py` holds an impure `load_census_inputs(set_dir)` that walks
  one set and a pure fold over a frozen carrier holding only ids, rooms, ticks, kinds, labels,
  dispositions, plain recorded arm values and loader-computed booleans; `pool` adds counts and
  recomputes rates from pooled numerators and denominators. Enforced by a test that walks the
  carrier's fields and fails on any string-typed field outside a named allow-list of id, room, kind
  and label fields. Planted: a carrier class with a `rationale: str` field fails it.
- [ ] **Walk profile and thread-or-refuse.** The census walks with
  `replace(_CURRENT_REPORT_WALK_CONFIG, profile="gameplay-census",
  missing_meeting_row="violation", reject_duplicate_meeting_rows=True, require_terminal_tick=True)`,
  threads engine-layer arms through the spine's engine-arguments helper and layer classification,
  declares its own `threaded_layers` in that `replace` (never inheriting `current-report`'s, which
  record plumbing declares), and raises on a recorded field it does not thread. The census also classifies every
  `RecordedExperimentConfig` field as read by a named cell predicate or deliberately not read.
  Enforced by a test enumerating `RecordedExperimentConfig.model_fields`. Planted: a classification
  with one field removed fails that test, and a carrier with an unknown recorded arm key raises.
- [ ] **The figures reproduce.** The committed JSON reproduces the Evidence table: 20/849, 73/587,
  313/512 with 251 from the exit room and 62 only from the room left, 330/355, 13/89, 26/56, 330
  meetings with vent proof and 346 without of 676, 326 vent-band impostor ejections (253 exit only,
  10 both, 63 entry only) and 43 without vent proof, 50 resting only on the room left, 167/551
  stale on the 9p2i pool, 335/676, 521/676, 0/676, 38/42, and 809 moves thrown away. Enforced by
  `--check` and by a test that reads each named figure from the committed JSON. Planted: `--check`
  is red on one edited cell and on a missing file. Each figure is re-measured at dispatch; a
  figure that moves is reported in Results with its cause, and never pinned to the memo's value.
- [ ] **Body kill tick from the event.** Corpse age and staleness join each body to its victim's
  `KilledEvent` on the tick the body first appears. Enforced by the fold. Planted: a carrier whose
  body id encodes a tick different from the event tick reads the event tick.
- [ ] **Thrown-away actions from the recorded dispositions.** The trigger-tick cell counts
  `discarded_by_meeting` dispositions by action type. Enforced by the fold. Planted: a move
  discarded on a game-ending trigger tick is counted (the 808 to 809 case).
- [ ] **Exit witnesses.** Exits seen, seen from the exit room, and seen only from the room left
  read the recorded `source_witnesses` / `destination_witnesses`, crew only. Planted: an exit seen
  only from the room left counts as seen and as room-left-only, and moving that crewmate out of the
  room left at the pre-tick flips both.
- [ ] **Stale reports.** A report meeting is stale when its trigger body was on the floor at the
  previous meeting's open. Planted: a stale corpse flips to fresh when its kill moves after the
  previous meeting's open.
- [ ] **Vent band against vent proof.** Vent-proof meetings (a `vent_sighting` flag naming a living
  player) and the vent band (a flag naming the ejected player) are separate cells with separate
  denominators. Planted: moving the flag onto a living, non-ejected player takes that ejection out
  of the vent band while the meeting stays vent-proof.
- [ ] **Impostor ballots.** Recorded SKIP, EJECT, EJECT labelled `supported`, recorded teammate
  targets, and authored teammate targets read from the typed guard fields. Planted: an authored
  teammate target is counted while the recorded target is SKIP.
- [ ] **Era-keyed pooling.** Each game carries an era key: its normalized experiment config, its
  temporal-observation version, its substrate-flag stamp, and its prompt-stamp set taken only from
  MANIFEST rows that record a meeting. `pool` raises across eras, and the loader raises on a set
  whose games carry two eras. On baseline 9 the four sets are one era. Planted: pooling two
  carriers with different era keys raises; a set mixing two keys raises. Perturbed: a rule taking
  the stamp from every MANIFEST row splits `replays/samples/4p1i` on its 11 no-meeting rows and
  raises, while the ruled key reads one era.
- [ ] **Conformance guards.** Each cell an arm makes zero by construction carries its arm
  predicate, read from the carrier's plain recorded values (a missing key means the historical
  default); the predicates never build a `RecordedExperimentConfig`, because this card merges while
  `WAVE_ARMS_PENDING` still refuses those values at config validation. With the predicate true the
  publisher asserts 0 and renders "0 by construction", naming the field and value; a non-zero count
  raises `GameplayCensusConformanceError` naming (set, seed, meeting). Planted, one pair per row
  below: a hand-built carrier with the arm ON and one violating fact raises, and the same fact with
  the arm OFF publishes 1 of N. Vacuity: with the arm ON and an empty denominator the cell renders
  `n/a`, never 0. The rows:

  | cell | predicate | s9 today (arm off) |
  |---|---|---|
  | exits seen only from the room left; vent-band ejections resting on them | `vent_witness_rule == "physical"` | 9/85; 8 |
  | entries not after the impostor's own fresh kill (own victim in that room, killed at most 3 ticks earlier, no meeting between) | `vent_entry_policy == "own_fresh_kill"` | 13/105 |
  | surfacings before the cap with a non-teammate in the inferred-visible set; trips longer than the cap | `vent_exit_policy == "look_and_wait"` | re-measured; n/a |
  | stale reports; play resumes with an impostor in a vent; play resumes with a corpse | `meeting_reset == "hub_with_grace"` | 43/135; 10/107; 60/107 |
  | kills in the grace window after a regroup; corpse age above the ticks since the last close | `meeting_reset == "hub_with_grace"` | n/a; n/a |
  | report openings carrying the kill-tick body id | `report_body_handle_version == 1` | 135/135 |
  | rebuttals differing from the selector's pick | `bounded_rebuttal_version == 1` | n/a |
  | a second repeat-speaker turn in one meeting (a second rebuttal) | always | 0 |
  | any repeat-speaker turn; an accused opener answering | `bounded_rebuttal_version` None | 0; 0/125 |
  | impostor openers | `self_report` False and `contextual_self_report_version` None | 0/145 |
  | recorded teammate ballot targets | always (the guard) | 0 |
  | own-kill rows naming a teammate or held by a non-witness | `ballot_kill_row_version == 1` | n/a |

  The two tick counts that define an arm value are named constants documented as that value's
  frozen meaning (decision 0.3 item 6): the fresh-kill window of 3 and the in-vent cap of 4 play
  ticks, restarted at a meeting boundary. The exit-policy card's end-to-end test is where its
  own constants are pinned equal to these; that is a note for that card, not this card's check.
- [ ] **The own-kill extraction, built now against the specified row.** The loader finds served
  own-kill rows by the ballot card's specified row: kind `own_kill`, text `you watched them KILL in
  {room} at tick {tick}`, cited by the kill's observation id. The text is one named pattern
  constant in `eval/gameplay_census.py`; the ballot card pins its row text to that constant and
  never edits this file. The cited id joins the row to its `KilledEvent`: a row whose killer is the
  voter's teammate, or whose voter is not among that kill's witnesses, is a breach. Rows found are
  the cell's denominator, so a wording mismatch reads `n/a`, never 0. There is no unsupported-arm
  error: a recording with `ballot_kill_row_version` 1 loads like any other. Mechanism: the pattern
  constant and the fold. Planted: with the arm ON, a carrier holding one own-kill row cited by a
  teammate's kill raises, and so does one held by a voter who did not witness the kill; the same
  carriers with the arm OFF publish 1 of N; a loader unit test extracts the row from a synthetic
  prompt string in the specified wording and finds none in a different wording, printing nothing.
- [ ] **The exit-policy predicate is the policy's own view.** A breach is a surfacing before the cap
  while a non-teammate stood, in the impostor's own observation at the pre-tick, in a room of the
  inferred-visible set: the own room plus its map neighbours, or the own room alone while any
  sabotage is active. It never tests the engine's visibility set. Planted: a surfacing during a
  reactor sabotage, with a crewmate in a neighbour that is truly visible, is not a breach; the
  same case with the crewmate in the own room is. The s9 value is re-measured on this definition
  and reported beside the memo's 31/85, with any difference attributed to exits under sabotage.
- [ ] **The grace window is the map's.** The window after a regroup at meeting tick T is T+1 to
  T+`kill_cooldown_ticks`, read from the loaded map, never a literal. Enforced by the fold and a test
  pinning the window length to the map. Planted: a kill at T+4 after a regroup is a breach; a kill
  at T+5 is outside the window and publishes as an ordinary post-meeting kill.
- [ ] **The added cells** (decision memo 2.6) are computed and each has a planted carrier. Exit
  behaviour: forced (cap) exits; ticks inside per trip; in-place surfacings where a crewmate enters
  or shares the corpse room before the impostor walks out; kills within 2 ticks of a surfacing.
  Regroup: trips closed by a regroup (an entry with no exit event); kill-witness button calls within
  6 ticks of a regroup; trigger-tick move and task events a regroup discards; sabotage active at a
  regroup. Rebuttal: claim structure (alibi, whereabouts, sighting, redirect only); rebuttal
  accusations against players who already spoke; beneficiary kind with the accuser's role; opener
  rebuttals answering the charged tick. Ballots: ejections carried only by impostor ballots, with the
  floor read from the tally's own parameter. Also reported: meetings per game, SKIP at report
  meetings, the win split and role-correct ejections. On baseline 9 each arm-dependent cell renders
  `n/a`, and its planted carrier fills it.
- [ ] **Publisher.** `scripts/publish_gameplay_census.py` writes both files through
  `preflight_report_output` / `atomic_write_report`, with every `replays/**` path, the recording
  directories and the census's own inputs protected by containment; `--check` exits 1 on drift and
  names the regenerate command; `--set-dir DIR --json-stdout` folds one directory, prints JSON and
  writes nothing, and exits non-zero on a conformance breach. Enforced by
  `tests/scripts/test_publish_gameplay_census.py`, calling `check_report` as the scorecard's test
  does. Planted: a destination inside `replays/` is refused before anything is computed; a
  `--set-dir` run over a planted copy leaves the tree's file list unchanged.
- [ ] **Copy.** The page opens by saying it is not the scorecard, that role-correctness is reported
  and gates nothing, and by defining each term it uses (vent band, era, regroup, opener, trigger
  tick, by construction). No cell is named by a memo number, a wave letter, a task or audit id, or
  threshold arithmetic; keys and titles are descriptive. Enforced by a test scanning the rendered
  page for those id shapes. Planted: a title carrying a memo-style id fails it.
- [ ] **Registry.** `docs/artifacts.md` gains one class-(b) row, in git, sized "2 files", beside the
  scorecard's (`:111`); `_IN_TREE_PROBES` (`:2754`) and `_IN_TREE_INVENTORY` (`:2816`) in
  `scripts/verify_ml_evidence.py` gain matching entries. Enforced by the offline
  `verify_ml_evidence.py` run. Planted: the row without its probe entry fails it.
- [ ] **The meeting-structure counts reach the direction.** On merge, one dated sentence is
  appended to the 2026-09-24 addendum of `tasks/direction-2026-09-19-process-over-outcome.md`: the
  first reply accuses the opener in 521 of 676 meetings, the opener speaks a second time in 0 of
  676, and `uv run python scripts/publish_gameplay_census.py --check` recomputes both. Enforced by
  the figures test above, which pins both counts in the committed JSON the sentence cites; the
  sentence is dated history and is not re-bound after an adoption. Perturbed: editing either count
  in the JSON reddens that test and `--check`. If the addendum is not on `main` yet, this card
  does not write it: it stops and asks.
- [ ] **Nothing else moves.** The golden on s9 and s4, `verify_samples` on each of the four set
  directories, the four `build_sample_report --check` runs, `publish_process_scorecard --check`
  and the c9 refit pins including the campaign tier read as before, and `git diff` from the merge
  base shows no path under `replays/`, `api/`, `frontend/`, `agents/`, `meetings/`, `engine/`,
  `orchestrator/` or `observation/`. Enforced by those gates and the scope check in Validation.
  Perturbed: the scope check run against a scratch commit touching `api/` prints that path; each
  gate keeps its own planted failure in its suite, and this card removes none.

## Constraints

**Wave and order.** Wave 0, parallel with `docs-truth-typed-trigger` (A3); starts now, on `main` at
`e886b663` or later. It merges after `stage-b-arm-spine`, and before every arm card
(`vent-witness-physical`, then the B1, B4, B2 and B6 cards), before `stage-b-record-plumbing`
(which merges after readers and this card), and before `stage-b-readers`, which writes
`tests/_helpers/committed.py` after this card. It consumes the spine's `FIELD_LAYER`, its
engine-arguments helper and the eight declared fields, so it cannot pass its classification test
until the spine has merged; it waits for the spine rather than stubbing them. Each arm card then
adds one end-to-end test in its own test file: a fake or scripted arm-ON recording reads 0 on its
cell, and a perturbed copy raises. The record card's STOP rules rely on both halves.

**One writer per file (decision memo 3.2).** `eval/gameplay_census.py`,
`tests/eval/test_gameplay_census.py`, the new script, its test and the two `docs/gameplay-census.*`
files are this card's alone. Shared, in order: `tests/_helpers/committed.py` (A3 writes the trigger
kind at `:382-392`, then this card writes only a new census cache region, then readers, then record
plumbing, then B2, all serial); `docs/artifacts.md` (this card's census row first, then, in merge
order, readers, record plumbing, look-and-wait, the meeting reset and the record card, each writing
only its own row); `scripts/verify_ml_evidence.py` (this card's probe and inventory entry, then
record plumbing); the direction file (the orchestrator's `docs:`
addendum commit lands first, then this card's one appended sentence). The 3.2 map says this card
"rebases on A3": under the wave rules that means merging `main` into the branch after A3 merges,
never a rebase. This card writes no line of `eval/replay_walk.py` (the spine, then B2, own it), so
the census profile is documented in `eval/gameplay_census.py`, not in that file's drift table.

**The partial-record principle, where it binds.** Only `replays/samples/9p2i` is ever re-recorded,
and only into a candidate directory under `replays/candidates/`, by the record card, never here.
Every Stage-B switch is a `RecordedExperimentConfig` field, default-OFF and omitted from the payload
at its default; the census reads a missing key as the historical default. Every committed
recording, derived view, fixture, gate and doc fact keeps verifying byte-identically. No registry
prompt version moves. `docs/gameplay-census.*` stays on baseline 9 until an adopting decision; a
candidate's columns come from `--set-dir` into the record's audit, never into these files.

**Measurement discipline.** Fake and replay providers only; no live provider call, no recorder
run, no `.env` read, no held-out band (2100-2999 stays unseen), no seed-band prefix printed. The
census is count-only: the loader reads a recorded prompt only to compute a boolean or an id
inside itself, and no prompt, speech or rationale text leaves it or reaches any output, log or
test message. Role-correctness is reported and never a gate; roles are read for reported cells and
structural guards only and feed nothing back to any agent. No instrument pushes an agent toward
the correct answer, and the census changes nothing the meeting layer does: the meeting layer
labels and never rewrites. No scorecard cell and no D1 amendment (R13). No ML consumer (ruling 12).

**Delivery.** Branch `work/gameplay-census`; one pull request into `main`, with every section of
`.github/pull_request_template.md` filled: Summary, Definition of done, Decisions and Questions,
the body ending with the Claude Code attribution line. Merge or fast-forward, never squash; never
amend a pushed commit; take `main` by merging it in, never by rebasing. Every commit body ends
`Card: tasks/work/gameplay-census.md` immediately followed by
the `Co-Authored-By:` attribution line the worker's own session supplies (never a model name copied from this card). No agent posts PR comments. The merge is
the owner's.

**Status and the task index.** `tasks/README.md` is the orchestrator's: its inventory sentence is
derived from every card's `**Status:**`, so the worker fills Results and leaves the Status line to
the orchestrator, who flips it with the sentence in one commit.

**Stop and ask.** A figure that does not reproduce at dispatch is reported with its cause, not
tuned. A breach on baseline-9 bytes of a guard whose predicate is already true today (the
always-on guards and the arm-OFF guards) stops the card.

**The own-kill extraction is ruled.** The orchestrator ruled it before dispatch: this card builds
the extraction now against the ballot card's specified row (the acceptance item above), with no
unsupported-arm error, and the ballot card pins its row text to this card's constant and never
edits `eval/gameplay_census.py`. No writer exception exists.

## Expected scope

New: `eval/gameplay_census.py`, `scripts/publish_gameplay_census.py`, `docs/gameplay-census.md`,
`docs/gameplay-census.json`, `tests/eval/test_gameplay_census.py`,
`tests/scripts/test_publish_gameplay_census.py`. Edited: `tests/_helpers/committed.py` (one cached
census walk, the single-home rule at `:1-30`); `docs/artifacts.md` (one row);
`scripts/verify_ml_evidence.py` (one probe and one inventory entry);
`tasks/direction-2026-09-19-process-over-outcome.md` (one appended sentence); this card's Results.
Permitted follow-through, declared in Results: if the single-home pin must name the census loader
in `WALKERS`, one line in `tests/_helpers/test_committed_single_home.py` (the 3.2 map gives that file
to no other card; the orchestrator confirms at dispatch).

Not in scope: `eval/replay_walk.py`, `eval/process_scorecard.py`,
`scripts/publish_process_scorecard.py`, `docs/process-scorecard.*`, `docs/glossary.md` (the page
defines its own terms; a term that needs a glossary entry goes to the orchestrator for the
glossary's writer order), `orchestrator/experiment_config.py`, every file under `engine/`,
`agents/`, `meetings/`, `observation/`, `orchestrator/`, `api/`, `frontend/`, `llm/`, `training/`,
`experiments/` and `replays/`, every prompt template, and `tasks/README.md`.

## Record impact

Nothing recorded moves: no recording, MANIFEST, report gz, fixture, prompt byte, weight or DTO. No
experiment turns ON and no adopting record is created. Two new committed files are the change,
class (b) in `docs/artifacts.md` by the same reasoning as the scorecard's row: a regenerated view
whose bytes a gate pins is a record. Their numbers describe baseline 9 and stay there through the
wave; the round-1 candidate is read only through `--set-dir`, which writes nothing.

Publication: a push to `main` republishes the demo bundle (`.github/workflows/pages.yml`). This card
touches no path the bundle reads (nothing under `api/`, `frontend/`, `replays/samples/` or the
featured list, and not `scripts/build_demo_bundle.py`), so the republished bundle is byte-identical;
the scope check in the last acceptance item is the proof, and Results quotes it.

Measurement: every cell is a count with a stated denominator, per set and within one era; rates are
never pooled across eras. Once an arm is recorded, its conformance cells read 0 by construction, and
the page says so instead of presenting a measured improvement.

## Validation

- `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py -q`
- `uv run python scripts/publish_gameplay_census.py --check`
- `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout`
  (compared with the committed s9 section; `git status --porcelain` empty afterwards)
- `uv run python scripts/publish_process_scorecard.py --check`
- `bash scripts/verify_samples.sh replays/samples/9p2i`, then the same for `replays/samples/4p1i`,
  `replays/ml_corpus/9p2i` and `replays/ml_corpus/4p1i`, once per set directory
- `uv run python scripts/build_sample_report.py --sample-dir <set> --check` for each of the four sets
- `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` (the golden on s9 and s4)
- `uv run python scripts/check_doc_facts.py` and `uv run python scripts/validate_task_docs.py`
- `uv run python scripts/verify_ml_evidence.py` offline, never `--complete`, with
  `uv run pytest tests/scripts/test_verify_ml_evidence.py -q`
- `uv run lint-imports` and `uv run mypy .`
- `uv run pytest -m campaign` (the c9 refit pins' campaign half; `pyproject.toml:91` excludes it by
  default)
- `bash scripts/check.sh` whole, in a clean worktree, with its real exit code reported
- `git diff --stat $(git merge-base origin/main HEAD) -- replays api frontend agents meetings engine
  orchestrator observation scripts/build_demo_bundle.py` empty
- No frontend e2e: this card touches neither `api/` nor `frontend/`; the frontend unit tests run
  inside `check.sh`.

## Results

Empty until implementation. The worker records here: each acceptance item's evidence with the
command that produced it; every figure as re-measured at dispatch beside the Evidence table; the
s9 exit-policy predicate value on the inferred-visible definition beside 31/85; the scope check's
output; material decisions (the own-kill pattern constant's name, any `WALKERS` edit); and limitations.
