# A1: the gameplay census report

**Status:** active

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

- [x] **Shape.** `eval/gameplay_census.py` holds an impure `load_census_inputs(set_dir)` that walks
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
- [x] **The figures reproduce.** The committed JSON reproduces the Evidence table: 20/849, 73/587,
  313/512 with 251 from the exit room and 62 only from the room left, 330/355, 13/89, 26/56, 330
  meetings with vent proof and 346 without of 676, 326 vent-band impostor ejections (253 exit only,
  10 both, 63 entry only) and 43 without vent proof, 50 resting only on the room left, 167/551
  stale on the 9p2i pool, 335/676, 521/676, 0/676, 38/42, and 809 moves thrown away. Enforced by
  `--check` and by a test that reads each named figure from the committed JSON. Planted: `--check`
  is red on one edited cell and on a missing file. Each figure is re-measured at dispatch; a
  figure that moves is reported in Results with its cause, and never pinned to the memo's value.
- [x] **Body kill tick from the event.** Corpse age and staleness join each body to its victim's
  `KilledEvent` on the tick the body first appears. Enforced by the fold. Planted: a carrier whose
  body id encodes a tick different from the event tick reads the event tick.
- [x] **Thrown-away actions from the recorded dispositions.** The trigger-tick cell counts
  `discarded_by_meeting` dispositions by action type. Enforced by the fold. Planted: a move
  discarded on a game-ending trigger tick is counted (the 808 to 809 case).
- [x] **Exit witnesses.** Exits seen, seen from the exit room, and seen only from the room left
  read the recorded `source_witnesses` / `destination_witnesses`, crew only. Planted: an exit seen
  only from the room left counts as seen and as room-left-only, and moving that crewmate out of the
  room left at the pre-tick flips both.
- [x] **Stale reports.** A report meeting is stale when its trigger body was on the floor at the
  previous meeting's open. Planted: a stale corpse flips to fresh when its kill moves after the
  previous meeting's open.
- [x] **Vent band against vent proof.** Vent-proof meetings (a `vent_sighting` flag naming a living
  player) and the vent band (a flag naming the ejected player) are separate cells with separate
  denominators. Planted: moving the flag onto a living, non-ejected player takes that ejection out
  of the vent band while the meeting stays vent-proof.
- [x] **Impostor ballots.** Recorded SKIP, EJECT, EJECT labelled `supported`, recorded teammate
  targets, and authored teammate targets read from the typed guard fields. Planted: an authored
  teammate target is counted while the recorded target is SKIP.
- [x] **Era-keyed pooling.** Each game carries an era key: its normalized experiment config, its
  temporal-observation version, its substrate-flag stamp, and its prompt-stamp set taken only from
  MANIFEST rows that record a meeting. `pool` raises across eras, and the loader raises on a set
  whose games carry two eras. On baseline 9 the four sets are one era. Planted: pooling two
  carriers with different era keys raises; a set mixing two keys raises. Perturbed: a rule taking
  the stamp from every MANIFEST row splits `replays/samples/4p1i` on its 11 no-meeting rows and
  raises, while the ruled key reads one era.
- [x] **Conformance guards.** Each cell an arm makes zero by construction carries its arm
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
- [x] **The own-kill extraction, built now against the specified row.** The loader finds served
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
- [x] **The exit-policy predicate is the policy's own view.** A breach is a surfacing before the cap
  while a non-teammate stood, in the impostor's own observation at the pre-tick, in a room of the
  inferred-visible set: the own room plus its map neighbours, or the own room alone while any
  sabotage is active. It never tests the engine's visibility set. Planted: a surfacing during a
  reactor sabotage, with a crewmate in a neighbour that is truly visible, is not a breach; the
  same case with the crewmate in the own room is. The s9 value is re-measured on this definition
  and reported beside the memo's 31/85, with any difference attributed to exits under sabotage.
- [x] **The grace window is the map's.** The window after a regroup at meeting tick T is T+1 to
  T+`kill_cooldown_ticks`, read from the loaded map, never a literal. Enforced by the fold and a test
  pinning the window length to the map. Planted: a kill at T+4 after a regroup is a breach; a kill
  at T+5 is outside the window and publishes as an ordinary post-meeting kill.
- [x] **The added cells** (decision memo 2.6) are computed and each has a planted carrier. Exit
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
- [x] **Publisher.** `scripts/publish_gameplay_census.py` writes both files through
  `preflight_report_output` / `atomic_write_report`, with every `replays/**` path, the recording
  directories and the census's own inputs protected by containment; `--check` exits 1 on drift and
  names the regenerate command; `--set-dir DIR --json-stdout` folds one directory, prints JSON and
  writes nothing, and exits non-zero on a conformance breach. Enforced by
  `tests/scripts/test_publish_gameplay_census.py`, calling `check_report` as the scorecard's test
  does. Planted: a destination inside `replays/` is refused before anything is computed; a
  `--set-dir` run over a planted copy leaves the tree's file list unchanged.
- [x] **Copy.** The page opens by saying it is not the scorecard, that role-correctness is reported
  and gates nothing, and by defining each term it uses (vent band, era, regroup, opener, trigger
  tick, by construction). No cell is named by a memo number, a wave letter, a task or audit id, or
  threshold arithmetic; keys and titles are descriptive. Enforced by a test scanning the rendered
  page for those id shapes. Planted: a title carrying a memo-style id fails it.
- [x] **Registry.** `docs/artifacts.md` gains one class-(b) row, in git, sized "2 files", beside the
  scorecard's (`:111`); `_IN_TREE_PROBES` (`:2754`) and `_IN_TREE_INVENTORY` (`:2816`) in
  `scripts/verify_ml_evidence.py` gain matching entries. Enforced by the offline
  `verify_ml_evidence.py` run. Planted: the row without its probe entry fails it.
- [x] **The meeting-structure counts reach the direction.** On merge, one dated sentence is
  appended to the 2026-09-24 addendum of `tasks/direction-2026-09-19-process-over-outcome.md`: the
  first reply accuses the opener in 521 of 676 meetings, the opener speaks a second time in 0 of
  676, and `uv run python scripts/publish_gameplay_census.py --check` recomputes both. Enforced by
  the figures test above, which pins both counts in the committed JSON the sentence cites; the
  sentence is dated history and is not re-bound after an adoption. Perturbed: editing either count
  in the JSON reddens that test and `--check`. If the addendum is not on `main` yet, this card
  does not write it: it stops and asks.
- [x] **Nothing else moves.** The golden on s9 and s4, `verify_samples` on each of the four set
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

### 2026-09-25: implementation, measured at the branch head

**State: active, one acceptance item open.** Every item is met except the spine half of **Walk
profile and thread-or-refuse**. The census walks with the ruled `replace` of the current-report
profile, classifies every `RecordedExperimentConfig` field, and raises on a carrier or recording
naming a setting it has not classified. Not done: threading engine-layer arms through the spine's
engine-arguments helper and `FIELD_LAYER`, declaring the census's own `threaded_layers` in that
`replace`, and refusing a recorded field the walk does not thread. `stage-b-arm-spine` has not merged
(it is `ready` on `main` at `13f2c4d3`), and Constraints say this card waits for it rather than
stubbing it. The card therefore stays `active`, and the pull request is open for review. When the
spine lands, `main` is merged in and three things finish the item: the `threaded_layers` declaration,
the refusal test, and the equality form of the classification test (see Decisions, item 3).

**References.** `docs/architecture.md` on layering: `eval/` is an offline reader over the engine and
the orchestrator, `agents/` is untouched, and the four import-linter contracts are kept. It also
covers determinism: the census walk re-simulates every game and verifies tick hashes, dispositions,
meeting post-hashes and chronology. The design follows decision memo sections 0.3 (items 6 and 9),
0.4, 2.6, 3.2, and the 3.4 brief for this card. It also follows census memo section 4
(`tasks/investigations-2026-09-24/census_and_record.md`).

**What landed.**
- `eval/gameplay_census.py`: the impure `load_census_inputs`, the pure `fold_set` over a frozen
  carrier, `pool`, the setting predicates, `FIELD_CLASSIFICATION`, era keys, and the published models.
- `scripts/publish_gameplay_census.py`: publish, `--check`, and `--set-dir DIR --json-stdout`.
- `docs/gameplay-census.md` and `.json`: 67 cells and 8 tables, each per set and pooled.
- Tests: `tests/eval/test_gameplay_census.py` and `tests/scripts/test_publish_gameplay_census.py`.
- `tests/_helpers/committed.py`, census cache region: `census_inputs` and `census_walk_events`.
- `docs/artifacts.md`: the census row.
- `scripts/verify_ml_evidence.py`: one probe entry and one inventory entry.
- `tasks/direction-2026-09-19-process-over-outcome.md`: one appended sentence.

**Every figure, re-measured at the head through the production path.** The source is
`uv run python scripts/publish_gameplay_census.py --check` (consistent) and the committed JSON it
pins. The table below is read from that JSON, count-only. All reproduce the Evidence table and its
before values. No figure moved.

| cell | s9 | 9p2i pool | four-set pool |
|---|---|---|---|
| `kills_seen_by_crew` | 3/175 | 19/725 | 20/849 |
| `vent_entries_seen_by_crew` | 19/105 | 64/501 | 73/587 |
| `vent_exits_seen_by_crew` | 62/85 | 271/435 | 313/512 |
| `vent_exits_seen_from_exit_room` | 53/85 | 226/435 | 251/512 |
| `vent_exits_seen_only_from_room_left` | 9/85 | 45/435 | 62/512 |
| `impostors_seen_venting_ejected` | 70/77 | 284/304 | 330/355 |
| `impostors_vented_unseen_ejected` | 3/8 | 13/56 | 13/89 |
| `impostors_never_vented_ejected` | 8/15 | 25/40 | 26/56 |
| `meetings_with_vent_proof` | 70/145 | 285/594 | 330/676 |
| `vent_band_impostor_ejections` | 70/81 | 281/322 | 326/369 |
| `impostor_ejections_without_vent_proof` | 11/81 | 41/322 | 43/369 |
| `vent_band_resting_only_on_room_left` | 8/70 | 37/281 | 50/326 |
| `stale_report_meetings` | 43/135 | 167/551 | 167/623 |
| `meetings_opening_with_another_unreported_corpse` | 74/145 | 325/594 | 335/676 |
| `first_reply_accuses_opener` | 120/145 | 448/594 | 521/676 |
| `opener_speaks_again` | 0/145 | 0/594 | 0/676 |
| `openers_among_innocent_ejections` | 7/9 | 37/41 | 38/42 |
| `vent_entries_not_after_own_fresh_kill` | 13/105 | 101/501 | 103/587 |
| `surfacings_before_cap_in_view` | 52/85 | 264/435 | 299/512 |
| `vent_exits_into_visibly_occupied_room` | 31/85 | 122/435 | 134/512 |
| `trips_longer_than_cap` | n/a | n/a | n/a |
| `play_resumes_with_impostor_in_vent` | 10/107 | 30/452 | 30/486 |
| `play_resumes_with_corpse` | 60/107 | 263/452 | 263/486 |
| `post_meeting_kills_soon_after` | 28/87 | 129/363 | 135/389 |
| `meetings_opening_with_impostor_in_vent` | 29/145 | 92/594 | 101/676 |
| `report_openings_with_kill_tick_handle` | 135/135 | 551/551 | 623/623 |
| `opener_accused_after_opening` | 125/145 | 487/594 | 561/676 |
| `impostor_openers` | 0/145 (0 by construction) | 0/594 (0 by construction) | 0/676 (0 by construction) |
| `impostor_skip_ballots` | 164/210 | 694/861 | 760/943 |
| `impostor_eject_ballots` | 46/210 | 167/861 | 183/943 |
| `impostor_ejects_labelled_supported` | 44/46 | 164/167 | 178/183 |
| `recorded_teammate_ballot_targets` | 0/210 (0 by construction) | 0/861 (0 by construction) | 0/943 (0 by construction) |
| `authored_teammate_ballot_targets` | 1/210 | 13/861 | 13/943 |
| `ejections_carried_only_by_impostor_ballots` | 0/90 | 0/363 | 0/411 |
| `crew_witnessed_kills_held_at_next_meeting` | 3/3 | 19/19 | 20/20 |
| `held_kill_witnesses_voting_killer` | 3/3 | 18/19 | 19/20 |
| `held_kill_killers_ejected` | 2/3 | 12/19 | 12/20 |
| `role_correct_ejections` | 81/90 | 322/363 | 369/411 |
| `impostor_wins` | 11/50 | 56/200 | 88/300 |
| `vent_band_by_moment` | both 2, entry only 17, exit only 51 | both 10, entry only 54, exit only 217 | both 10, entry only 63, exit only 253 |
| `innocent_opener_ejections_by_trigger` | report 7 | emergency 1, report 36 | emergency 1, report 37 |
| `meetings_by_trigger` | emergency 10, report 135 | emergency 43, report 551 | emergency 53, report 623 |
| moves thrown away on trigger ticks | 188 | 754 | 809 |

Also reproduced from the Evidence text:
- Impostor ballots on s9: 210, of which 164 SKIP, 46 EJECT and 44 labelled `supported`.
- Ejections: 411 pooled, 369 of impostors and 42 of crewmates.
- The entry gate removes 13 of 105 entries on s9 and 103 of 587 pooled.
- Report openings carrying the kill-tick handle: 135 of 135 on s9, 623 of 623 pooled.
- Crew kill witnesses held, voting the killer, and seeing the killer ejected: 3/3/2 on s9, 20/19/12
  pooled.
- Floor met only by impostor ballots: 0 of 411.

The 809 thrown-away moves include `samples/4p1i` seed 3's game-ending trigger tick
(`test_the_loader_reads_the_game_ending_trigger_tick_of_samples_4p1i_seed_3`).

**The exit-policy predicate on s9: 52/85, beside the memo's 31/85.** The two count different
things, and the difference is fully attributed:
- The ruled predicate counts a surfacing before the cap while a non-teammate stood in any
  inferred-visible room: the vent's own room or a neighbour.
- The memo's 31/85 counts exits whose destination room was visible and occupied.
- The census publishes that destination-restricted count on the inferred-visible definition too
  ("Vent exits into a room the impostor could see a crewmate in"). It reads 31/85 on s9 and 134/512
  pooled, equal to the memo's engine-sight figures.
- Inferred and engine sight can differ only under a sabotage, so no s9 exit is attributable to
  exits under sabotage.
- The other 21 exits had a crewmate in a visible neighbour other than the destination.
- "Trips longer than the cap" reads `n/a` on every set: all 512 exits have 1 tick inside once the
  count restarts at a meeting boundary. The memo's 19 two-tick trips all span a meeting.

**Decisions.**
1. The own-kill pattern constant is `eval.gameplay_census.OWN_KILL_ROW_TEXT`
   (`"you watched them KILL in {room} at tick {tick}"`). Rows are found by the ballot template's
   evidence-row line around that text. The row joins to its kill through the cited observation id:
   agent-frame tick minus `AGENT_CLOCK_OFFSET`, with the killer equal to the row's subject. A row
   citing nothing is not evaluable.
2. `WALKERS` in `tests/_helpers/test_committed_single_home.py` gains `load_census_inputs`, the
   permitted line. The same file's docstring "six committed-set walks" becomes "seven" so the
   sentence stays true. `test_a_census_walk_outside_the_shared_cache_is_flagged` plants the case.
3. Five fields are read before the spine declares them: `vent_witness_rule`, `vent_entry_policy`,
   `report_body_handle_version`, `ballot_kill_row_version` and `impostor_ballot_version`. Their
   historical defaults sit in `_UNDECLARED_DEFAULTS`, and every other default is read from the model.
   `test_the_names_read_before_the_spine_declares_them` pins the five as exactly the difference, so
   the spine's merge turns it red and forces the retirement. This is not a stub of any spine symbol.
4. The kill-tick handle pattern is a census constant pinned equal to
   `experiments.held_out_prefixes.LEGACY_BODY_HANDLE_PATTERN` by a test. `eval/` does not import the
   held-out generator.
5. A regroup is a loader-computed carrier boolean: the recorded reset is `hub_with_grace` and play
   resumed. The grace window reads `kill_cooldown_ticks` from the loaded map.
6. "Corpse age above the ticks since the last close" is published as "Reported corpses older than
   the last regroup": the victim was killed on or before the previous meeting's tick. This avoids an
   off-by-one where a kill on the trigger tick itself would read "not above".
7. Publisher protection is the recording root (containment) plus every file under it (file identity
   for a hard link). Every census input lives under that root. The neuter pass showed separate
   set-directory and input entries were redundant, so they were dropped.
8. The MANIFEST prompt cell is read by the census itself: the third cell in every table width. A
   test pins it equal to `_manifest_writer.parse_manifest` on all four sets. A game with a meeting
   whose cell names no stamp raises.
9. The loader refuses any seed in 2100-2999 before opening it.
10. The selector-guard row has no publishing twin. At `bounded_rebuttal_version` 1 the selector guard
    raises; at the default the repeat-speaker guard raises instead. The two always-on guards have no
    OFF value. All three are pinned (`test_a_rebuttal_off_the_selector_raises_under_either_value`,
    `test_the_always_guards_raise_under_every_setting`).
11. A breach names the set and seed always. It names the meeting id for a meeting fact, and the
    tick for a play fact (a vent entry or exit, a trip, a kill). The acceptance text's "(set,
    seed, meeting)" is met at that strength, and the page, the error's docstring and the publisher
    say so.

**Follow-through outside Expected scope, declared.**
- `tests/scripts/test_verify_ml_evidence.py` links the census pair in its availability tree, two
  lines. Without them the new probed row reads missing in that scratch tree and fails
  `test_complete_accepts_a_manifestless_recorded_loss_end_to_end`.
- `tasks/README.md`'s derived inventory sentence is re-derived for this card's Status flip, as the
  dispatch instructed.

**Verification (all at the head).**

The table was measured at `d75ff36c`. `9800b718` changes only the text of the page's
"by construction" definition and the publisher's docstring. At `9800b718`, with this Results
section in place, the following were re-run:
- the two census suites: 146 passed;
- `--check`: consistent;
- `validate_task_docs.py`: exit 0;
- `bash scripts/check.sh`: exit 0, with the same counts as the table's last row.

Each exit code was captured directly, never through a pipe. The commits are `612bbeaa` (the
instrument, the publisher, the pages, the tests and the direction sentence), `d75ff36c` (the
registry), `9800b718` (the text fix) and this card commit.

| command | result |
|---|---|
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py -q` | 146 passed |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, both files consistent |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; the printed JSON equals the committed `samples/9p2i` section; `git status --porcelain` empty afterwards |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `bash scripts/verify_samples.sh <set>`, once for each of the four set directories | exit 0 each: 50, 50, 150 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, all four | exit 0 each, consistent |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | 25 passed |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/validate_task_docs.py` | exit 0, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: checks 62, OK 50, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 82 passed |
| `uv run lint-imports` | 4 contracts kept, 0 broken |
| `uv run mypy .` | no issues in 498 source files |
| `uv run pytest -m campaign` | 336 passed |
| `bash scripts/check.sh` | exit 0: 8,453 Python passed, 20 skipped, 3 xfailed; 558 frontend tests passed |

No frontend e2e: this card touches neither `api/` nor `frontend/`.

**Planted and perturbed failures.** Each item's planted case is a named test:
- Shape: `test_a_carrier_holding_a_rationale_fails_the_shape_check`.
- Classification: `test_a_classification_missing_one_field_fails`.
- Unknown key: `test_an_unknown_recorded_setting_raises`.
- `--check`: `test_one_edited_cell_turns_check_red` and `test_a_missing_published_file_is_red`.
- Body tick: `test_corpse_age_reads_the_kill_event_tick_never_the_body_id`.
- 809: `test_a_move_discarded_on_a_game_ending_trigger_tick_is_counted`.
- Exit witnesses: `test_an_exit_seen_only_from_the_room_left_flips_when_the_crewmate_leaves`.
- Stale reports: `test_a_stale_corpse_flips_to_fresh_when_its_kill_moves_after_the_last_open`.
- Vent band: `test_moving_the_flag_leaves_the_band_but_keeps_the_proof`.
- Ballots: `test_an_authored_teammate_target_counts_while_the_recorded_target_skips`.
- Eras: `test_pooling_two_eras_raises`, `test_a_set_mixing_two_eras_raises`, and
  `test_the_ruled_prompt_stamp_reads_samples_4p1i_as_one_era`. The every-row rule splits
  `samples/4p1i` on its 11 no-meeting rows.
- Guards: 16 parametrized pairs in
  `test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off`, plus the vacuity test.
- Own-kill: `test_the_row_is_found_in_the_specified_wording_and_nowhere_else` and the two own-kill
  guard pairs.
- Reactor sabotage: `test_a_reactor_surfacing_with_crew_in_a_visible_neighbour_is_no_breach`.
- Grace window: `test_a_kill_at_the_first_legal_tick_is_an_ordinary_post_meeting_kill`.
- Writer: `test_the_writer_refuses_a_recording_destination_before_computing`, 12 cases.
- `--set-dir`: `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing`.
- Copy: `test_a_title_carrying_a_memo_style_id_fails_the_copy_scan`.

**Registry, planted.** Each perturbation ran the offline verifier, then the file was restored
from a copy (sha256 identical afterwards; the verifier read exit 0 again):
- row without its probe entry: exit 1, FAIL on registry coverage;
- row without its inventory entry: exit 2, the inventory refuses an unscoped row;
- probe without its row: exit 1;
- the row stating 3 files: exit 1, FAIL on the in-tree family inventory.

**Scope check** (the demo-bundle proof: no path the bundle reads moved).
`git diff --stat 13f2c4d3 -- replays api frontend agents meetings engine orchestrator observation
scripts/build_demo_bundle.py` printed nothing at the head. Perturbed: with one comment line
appended to `api/schemas.py` from a saved copy, it printed ` api/schemas.py | 2 ++`. After
restoring from the copy it printed nothing again.

**The mechanical neuter pass**, over every production line of the census module and the
publisher, run with a scratch harness. The harness does not ship.
- Each mutation was generated from the AST: every `acc.count` hit set to `False`, every
  `acc.tally` and `acc.not_evaluable` call dropped, every cell guard set to `None`, every `raise`
  replaced by `pass`, and every carrier constructor argument set to a neutral value. To these were
  added hand-written perturbations of each constant, predicate value, default and publisher branch.
- For each one the harness ran both census test files with `-x`, recorded red or green, and
  restored the file from an in-memory copy taken before the pass, never from git.
- A sha256 check confirmed the files byte-identical afterwards.

| round | perturbed | red | green |
|---|---|---|---|
| 1, before the fixes below | 329 | 307 | 22 |
| 2 | 325 | 324 | 1 |
| 3, at `d75ff36c` | 324 | 324 | 0 |

The 22 probes that first came back green, and what closed each one:
- The `_field_default` refusal: `test_a_default_is_read_only_for_a_classified_field`.
- The opener-speaks-again hit: planted in
  `test_a_rebuttal_off_the_selector_raises_under_either_value`.
- The era's temporal version: `test_the_loader_reads_the_temporal_observation_version`.
- `Frame.in_vent`, `KillFact.victim` and `BodyFact.victim`: no cell read them, so they were deleted.
- `TurnFact.index` and `reply_to`: the turn-fact test now uses non-default values.
- `MeetingFact.meeting_id`, `sabotage_active` and `ballot_floor`, and `BallotFact.confidence` and
  `cited_observation_id`: `test_the_loader_copies_ids_the_floor_ballots_and_sabotage`.
- The regroup flag's play-resumed condition: a game-ending variant in
  `test_the_loader_reads_the_recorded_reset`.
- The publisher's path bootstrap and `raise SystemExit(main())`:
  `test_the_script_runs_from_any_directory_and_exits_with_mains_code`.
- The JSON-destination preflight: the refusal test now covers both destinations.
- The two `--check` messages: now asserted.
- The replay-file protection: `test_a_hard_link_to_a_recording_is_refused_by_file_identity`.
- The census-input and set-directory protection entries: redundant under the root's containment,
  so they were removed (Decisions, item 7).

Round 2's one green was `TurnFact.turn_kind`. No cell read it, so it was deleted before commit.

Five more perturbations outside the two files each went red, with each file restored:
- the `WALKERS` entry;
- the direction sentence;
- the census cache returning another set;
- the census walk events emptied;
- the availability tree without the census pair.

**Limitations.**
- The spine half of the walk-profile item is open (above).
- Fifteen cells read `n/a` on baseline 9 because no committed recording carries a regroup,
  a rebuttal, a served own-kill row, an in-place surfacing or a trip that waited. Their meaning rests on planted carriers until an
  arm card's end-to-end test and the round-1 record fill them.
- The census is count-only over recorded events and states. It cannot tell why a policy acted.
- The own-kill extraction depends on the ballot card rendering the row with the template's
  evidence-row line around `OWN_KILL_ROW_TEXT`. A different line format reads `n/a`, never 0.
- Nothing in this card joins the scorecard, gates a decision, or feeds any agent.
