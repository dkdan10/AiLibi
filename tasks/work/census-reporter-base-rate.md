# The reporter flag read beside its base rate

**Status:** done

## Outcome

Round 2 is the shown 9-player set (`replays/samples/9p2i`, era `stage-b-r2`). Its record flags one number: innocent
reporters were voted out at 17 of 114 report meetings. The gameplay census shows that rate alone. A reader cannot
see what any other seat at the same meetings risked, whether vent proof was on the table, what happened to crewmates
who watched a kill, or how much the impostors' strategic ballots carried. The census also cannot say whether a skip
rested on anything, so the owner's first goal (a vote or a skip rests on data the agent holds, true or false) reads
for ejections only. Four cells pre-registered for the round are "not carried" by any named source.

When this card is done, the census (`eval/gameplay_census.py`, published by `scripts/publish_gameplay_census.py` to
`docs/gameplay-census.md` and `.json`) carries these new count-only cells. Every cell is grouped by era and never
pools across eras:

1. **Ejections at report meetings, by seat.** Every living player at a report meeting is one seat. Seats split into
   the reporter, the other crewmates and the impostors, reporter first, whatever the reporter's role. Each class
   reads ejected over seats, in total, at meetings without vent proof and at meetings with it. Beside them sit two
   shares: the reporters' share of crewmate ejections and of crewmate seats.
2. **What happened to a kill witness.** Take each crew-witnessed kill a meeting followed while a crew witness was
   alive at it. A table gives the next meeting's outcome (the killer ejected, a witness ejected, another player
   ejected, no one) for one living witness and for two or more, apart. One cell counts killers ejected at any later
   meeting and one counts witnesses ejected.
3. **The two counterfactual tallies.** Re-tally each meeting with every impostor ballot read as SKIP, and again with
   impostor ballots removed. Use the game's own tally function at the meeting's recorded floor. Count the ejections
   that would not stand, beside the existing floor-only cell, with a table of every outcome change.
4. **The holds-nothing skip label.** SKIP ballots whose recorded grounding label is `none_held`, beside a table of
   every SKIP by label.
5. **Two of the four uncarried cells, sourced.** Ballots citing a rebuttal turn, and recorded meeting prompts after a
   regroup that lack its notice. The holds-nothing label is item 4. The fourth uncarried cell, false resume
   perceptions, has no committed source; it stays an open point for the owner (Constraints).

The card also hardens the era registry these cells extend, from the promotion review's nonblocking findings:

- `ERAS` is held to the registry.
- The counterfactual's era refusal matches by era identity on the resolved directory.
- The scorecard's `pool()` refuses a source the registry cannot place in an era.
- The census cooldown refusal names its era under a planted registry.

Nothing gates on any of this. Role appears only as a reported column. No cell reads a role to judge a decision, and
nothing feeds back to an agent.

## Evidence

Every `path:line` below is a citation at `59bbd1be`, labelled by its symbol. The implementer re-anchors each one by
that symbol at dispatch. Every count is re-measured at dispatch through the production path, never copied from here.

**The flag and the rule around it.**
- The envelope row reads 17/114 = 0.149 against a line of 0.104 (`audits/audit-2026-10-01-stage-b-r2.md:1379`). The
  four uncarried cells are listed at `:1439-1441` (6.2 and 6.4 give the readings). Whether that line should be read
  relative to the other-innocent rate is the owner's question (diagnosis Part 4 item 2). This card does not restate it.
- The census stays a separate report with no scorecard cell (ruling R13,
  `tasks/decision-2026-09-24-stage-b-wave.md:57`).
- The census today carries the reporter numerator only: the table `innocent_opener_ejections_by_trigger` and the cell
  `openers_among_innocent_ejections` (`docs/gameplay-census.md:234`, `:249`).

**The base rate already exists, outside the census.** `eval/reporter_justice.py:446-490` (`_fold_meeting`) partitions
each report meeting's seats reporter first. The scorecard prints its totals as context, not as a row: "reporter slots
17/114 ejected against innocent non-reporter slots 5/367" for `samples/9p2i` (`docs/process-scorecard.md:135`), and
30/488 against 2/1390 for the pooled baseline-9 era (`:59`). It has no split by vent proof and no impostor column on
the page.

**The diagnosis** (`tasks/diagnosis-2026-10-02/README.md`) is advisory. Part 1.4 gives the per-seat reading,
Part 2.2 the counterfactual and witness tables, Part 3 card 1 this instrument, and the Appendix the count-only
reproduction. Its `s9` column is the former `samples/9p2i`. Those bytes
left the committed sets at the promotion and are readable only at `d41c9006`, so the census cannot show that column.
At this head the baseline-9 era is `ml_corpus/9p2i`, `ml_corpus/4p1i` and `samples/4p1i`.

**Authoring counts.** These came from a scratch count-only fold over the census carrier (`load_census_inputs`) and
the recorded ballots at `59bbd1be`. They agree with the diagnosis wherever both read the same bytes. The implementer
re-measures every one.

| reading | `samples/9p2i` (round 2) | `candidates/stage-b-r1/9p2i` (round 1) | `ml_corpus/9p2i` (baseline 9) |
|---|---|---|---|
| reporter seats ejected: no vent proof; with it | 17/93; 0/21 | 11/98; 0/20 | 28/234; 1/182 |
| other crewmate seats ejected: no proof; with it | 5/291; 0/76 | 2/303; 0/69 | 2/666; 0/652 |
| impostor seats ejected: no proof; with it | 20/158; 21/37 | 15/160; 20/34 | 30/303; 180/294 |
| reporters' share of crew ejections; of crew seats | 17/22; 114/481 | 11/13; 118/490 | 29/31; 416/1734 |
| held witnessed kills: one witness (killer, witness, other, no one); two or more (killer) | 9 (1, 5, 1, 2); 5 (5) | 3 (3, 0, 0, 0); 0 | 15 (9, 2, 1, 3); 1 (1) |
| held kills whose killer some meeting ejected | 8/14 | 3/3 | 13/16 |
| ejections undone, impostor ballots as SKIP; removed | 14/66; 5/66 | 8/54; 2/54 | 14/273; 6/273 |
| SKIP ballots labelled `none_held` | 214/281 | 256/330 | 702/1052 |
| ballots whose turn citation names a rebuttal; whose counter slot does | 57/691; 175/691 | 70/707; 150/707 | n/a |
| prompts after a regroup carrying every earlier regroup's notice | 722/722 | 782/782 | n/a |

Notes on the table:
- Of the undone ejections, reporters are 10 of 14 and 4 of 5 in round 2, 7 of 8 and 2 of 2 in round 1, and 12 of 14
  and 6 of 6 in `ml_corpus/9p2i`.
- The two 4p1i sets add 1 reporter ejection over 72 reporter seats.
- Tallying the recorded ballots unchanged reproduced the recorded outcome at every meeting of all five sets read (0
  mismatches).
- The seat totals equal the scorecard's context lines for `ml_corpus/9p2i` and `samples/9p2i`
  (`docs/process-scorecard.md:98`, `:135`).

**Sources for the four uncarried cells.**
- `none_held` SKIPs: the label is recorded on each ballot (`meetings/schemas.py:974-982`, written at
  `meetings/manager.py:4712-4713`). The census carrier already keeps `BallotFact.grounding_label`
  (`eval/gameplay_census.py:632-647`) and reads no `none_held`.
- Ballots citing a rebuttal: each recorded ballot carries `primary_reason_id` (a turn id of its meeting) and
  `counter_reason_id` (`meetings/schemas.py:1065-1068`). A rebuttal is a repeat-speaker turn (`_repeat_turns`,
  `eval/gameplay_census.py:2111`). The carrier drops both ids today.
- The regroup notice: every meeting prompt is recorded (`LLMCallRecord.prompt`, `orchestrator/replay.py:187-215`).
  The notice wording is `_REGROUP_NOTICE` (`agents/memory/store.py:423-426`). It renders in the non-elastic meetings
  block whenever the evidence version is not 1 (`:793-798`). The config refuses version 1 beside the regroup
  (`orchestrator/experiment_config.py:138-143`).
- False resume perceptions: no record holds what each observer perceived on the resume tick. Every reader that
  rebuilds perception goes through the one helper, `compose_resume_events` (`orchestrator/replay.py:1427`): the live
  loop, the walk, evidence honesty and the golden. A census count through it would check the helper against itself.
  What stands behind the cell is the helper's planted tests and the golden's byte-equal re-render of all 1,502
  recorded round-2 prompts (record 6.2).

**The hardening findings.**
- E3: dropping `STAGE_B_R2` from `ERAS` (`eval/eras.py:88`) survives the era suites (528 tests in the review's run).
- C3: the refusal in `run()` (`scripts/counterfactual_phase21.py:4396-4407`) tests membership in `CANONICAL_SETS` by
  exact name, so `./samples/9p2i` and `samples//9p2i` get past it, and the message's era id is not held.
- `pool()` filters unregistered sources out before its era check (`eval/process_scorecard.py:1835-1837`), and a test
  pins that pass-through (`tests/eval/test_process_scorecard.py:1447-1450`).
- C5: the cooldown refusal's era id (`eval/gameplay_census.py:3321-3326`) is not held under a planted registry.

These come from the promotion reviews' nonblocking list (`followup-nonblocking-findings.md`, the orchestrator's
session scratchpad, 2026-10-02); the reporter-justice survivor there is equivalent and is not taken up.

## Acceptance

Every item names its enforcing mechanism and the planted or perturbed case that must turn its test red.

- [x] Review correction: the floor test's re-derived carrier catches an authored-target read again. `test_the_impostor_only_floor_reads_recorded_targets_on_either_side` had gained a second impostor ballot for the ejected player at 0.9, which a floor reading `authored_target` still found; that ballot now sits at 0.1, below the floor, so the tally still ejects and the floor reads only the rewritten ballot. Proved by the probe that reads `ballot.authored_target` in the floor, which survived at `ecf51aa1` and is red at this head (Results, review corrections round 1), and by Decision 8 listing the carrier's old and new ballot.
- [x] **The per-seat cells.** Mechanism: one fold over report meetings (`trigger_kind == "report"`). It uses the
  existing vent-proof predicate (a vent-sighting flag naming a player alive at the open, as
  `meetings_with_vent_proof` reads it) and the reporter-first partition of `eval/reporter_justice.py`. It produces the
  nine cells (reporter, other crewmate, impostor, each in total, without vent proof and with it) and the two share
  cells, under one new heading. Planted: a hand-built carrier gives exact counts and turns red on each defect named
  here:
  - a role-first partition, shown by an impostor reporter in a self-report era;
  - a button meeting counted;
  - a dead player counted as a seat;
  - the ejected player's vent band used in place of the meeting's vent proof.
- [x] **The base rate agrees with the scorecard's context.** Mechanism: a test compares the census's per-seat totals
  (without plus with vent proof) with `compute_reporter_justice` on each of the four committed sets. The fields are
  `reporter_slots`, `reporter_ejections`, `innocent_non_reporter_slots`, `innocent_non_reporter_ejections`,
  `impostor_slots` and `impostor_slot_ejections`. Perturbed: a carrier with one seat dropped from `living` breaks the
  equality. If the two seat definitions (living at the open, against ballot voters) ever differ on committed bytes,
  the test names the meeting, and Results reports it rather than loosening the test.
- [x] **The kill-witness outcome table and cells.** Mechanism: the existing held-kill fold
  (`eval/gameplay_census.py:2378`) is extended. Every held crew-witnessed kill lands in exactly one of eight rows:
  one living crew witness, or two or more, crossed with the next meeting's outcome (the killer ejected, a witness
  ejected, another player ejected, no one). Two cells sit beside the table: killers ejected at any later meeting, and
  witnesses ejected at the next meeting. A test holds the rows' sum to the numerator of
  `crew_witnessed_kills_held_at_next_meeting`, and the killer rows to `held_kill_killers_ejected`. Planted, each red
  on its defect:
  - an impostor among the recorded witnesses counted as corroboration;
  - a witness dead by the meeting counted;
  - a meeting on the kill's own tick skipped;
  - the killer's ejection at a second meeting counted as a next-meeting outcome.
- [x] **The counterfactual tallies and the tally identity.** Mechanism: the fold calls `meetings.voting.tally_ballots`
  (`meetings/voting.py:192`), the game's own function, at the meeting's recorded floor (`MeetingFact.ballot_floor`).
  It tallies three times: unchanged, with impostor ballots read as SKIP, and with impostor ballots removed. The
  unchanged tally must reproduce the recorded outcome; a meeting where it does not raises
  `GameplayCensusConformanceError` naming the set, seed and meeting. This is a new invariant gate. Two cells count
  the ejections that would not stand, one per variant, and a table states every change. Its rows are
  `<variant>: <recorded outcome> -> <result>`: the reporter, another crewmate, an impostor or no one ejected, becoming
  no one ejected or a different player ejected. The table's description says every other ballot is held fixed.
  Planted, each red on its defect:
  - a meeting whose recorded ejected player disagrees with its ballots raises;
  - a SKIP variant that drops ballots instead of converting them gives a different, pinned count;
  - a fixed 0.6 floor in place of the recorded one changes a pinned outcome;
  - an ejection moving to another player is not read as standing.
- [x] **The holds-nothing label.** Mechanism: a cell over every SKIP ballot, whatever the voter's role, counting
  `grounding_label == "none_held"`. A table gives every SKIP by label: the members of `BallotGroundingLabel`, read
  from the type with `typing.get_args` so no label is copied, plus `unlabelled` for a ballot recorded before the
  field. The definition says the label records the voter's own declaration, not a checked fact. Planted:
  - an unlabelled SKIP never lands in `none_held`;
  - a `none_held` EJECT is not counted;
  - a label outside the vocabulary raises.
- [x] **Ballots citing a rebuttal.** Mechanism: the carrier keeps each ballot's `primary_reason_id` and
  `counter_reason_id`. Two cells, scoped to `bounded_rebuttal_version = 1`, count ballots whose turn citation names a
  rebuttal turn of the same meeting, and separately ballots whose counter slot does. Both are over ballots at meetings
  with a rebuttal. Planted:
  - a ballot citing the rebuttal speaker's first turn is not counted;
  - a ballot citing a rebuttal turn id from another meeting is not counted;
  - in the baseline-9 era both cells read n/a.
- [x] **The regroup notice.** Mechanism: the loader keeps one boolean per recorded call with an agent id at a meeting
  after a regroup. The boolean says whether the prompt carries the notice of every earlier regroup in that game,
  formatted from the regroup's tick and room as the renderer formats them. No prompt text leaves the loader. The
  census holds the wording as its own constant, pinned equal to the renderer's. The cell counts prompts missing a
  notice, guarded by `meeting_reset = hub_with_grace`, so it reads 0 by construction and the fold raises on a
  breach. Planted, each red on its defect:
  - a prompt missing an earlier regroup's notice raises, naming the set, seed and meeting;
  - a prompt at a game's first meeting is outside the denominator;
  - a perturbed copy of the renderer's wording fails the pin (the sourced constant's source-change case).
- [x] **The census stays a census.** Mechanism: tests over the published page and JSON.
  - The page names no envelope line and carries no ratio of two rates.
  - No new cell has a guard or scope that reads a role.
  - `docs/process-scorecard.md` and `.json` stay byte-identical (`publish_process_scorecard.py --check` green and
    `git diff` empty).
  - Planted: adding a relative-risk cell to the cell table turns the page test red.
- [x] **Era grouping for every new cell.** Mechanism: the new cells pool only through the existing `pool()` and
  `census_from_inputs`. Planted:
  - a tally carrying round 1's era key pooled with one carrying the promoted era's raises `GameplayCensusEraError`
    before any new cell is summed;
  - each scoped cell reads n/a in an era without its setting, never 0.
  - Round 1 is read with `--set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` and is never pooled.
- [x] **Properties.** Mechanism: Hypothesis over hand-built carriers. The generators reach impostor reporters (a
  self-report era), meetings with no impostor voter, meetings whose only EJECT ballots are impostors' (one voter
  included), and kills with two or more living witnesses. Any test that loads the map carries
  `settings(deadline=None)`. Each property names the perturbed fold that must turn it red:
  - **Partition.** The three seat classes partition the living seats of every report meeting, and the reporter's
    seat sits in the reporter class whatever its role. Perturbed: a role-first partition, given an impostor
    reporter, fails it.
  - **Identity.** With no impostor voter, both counterfactual variants equal the recorded outcome; and when every
    EJECT ballot is an impostor's, both variants eject no one. Perturbed: a SKIP variant that also converts a
    crew ballot fails the first half, and one that leaves an impostor ballot in place fails the second.
  - **Sum.** The witness table's rows sum to the held kills. Perturbed: a fold that drops the two-or-more witness
    row fails it.
  - Results quotes each perturbed run red, by name, and each property green on the production fold.
- [x] **E3, `ERAS` held to the registry.** Mechanism: a helper in `eval/eras.py` returns the distinct eras a registry
  names, oldest first, and a test holds `ERAS` equal to it. Planted: `ERAS` without `STAGE_B_R2`, and a registry
  naming a third era, each turn it red.
- [x] **C3, the counterfactual refusal by era identity.** Mechanism: `run()` resolves each named set to its directory
  under `replays/` and looks the directory up in the registry by resolved path. It refuses a registered set whose
  `era` is not `BASELINE_9`, naming that entry's era id. Planted:
  - `./samples/9p2i` and `samples//9p2i` are refused;
  - a monkeypatched registry holding a third era is refused with that era's id in the message.
  - An unregistered directory keeps today's path, as the existing sentinel test states.
- [x] **`pool()` refuses what it cannot place.** Mechanism: `eval/process_scorecard.py` `pool()` raises when a source
  is not named by its registry, or when sources and tallies differ in number. Planted:
  - a candidate directory pooled with a baseline-9 set raises;
  - `sources=()` with two tallies raises.
  - The existing arithmetic tests pass a scratch registry naming their sources in one era. The pinned unregistered
    pass-through becomes the planted refusal, which strengthens the test.
- [x] **C5, the census cooldown refusal's era id.** Mechanism: the message names the era its registry gives. Planted:
  a scratch registry with a second era holding two sets at different cooldowns raises with that era's id.
- [x] **One bounded mutation pass.** Mechanism: a single pass over every production line this card adds or changes,
  using only the eight listed operator classes: F filter, S swap, N comparison, C constant for a role, kind, room or
  tick read, M message, T tuple member, B branch swap, L loaded source to literal. Each mutant runs alone against the
  touched suites, and Results lists it. A survivor is killed by a new test or named equivalent with its reason.
  Results also carries a per-line neuter table: each production line, the test that goes red when it is neutered.
- [x] **Published and verified.** `publish_gameplay_census.py --check` is green on the regenerated page and JSON,
  and `bash scripts/check.sh` passes at the head that states the numbers.

## Constraints

- **House rules.**
  - The engine stays deterministic, and `agents/` never imports `engine/`. The census is an `eval/` reader and may
    import `agents/`, `meetings/` and `engine/`.
  - No module-level mutable state: new tables are `Final` tuples or read-only mappings.
  - Invalid input raises, with no silent fallback.
  - Each new invariant gate (the tally identity, the notice guard) carries its planted case.
  - Each claim names its mechanism, and every number in Results comes with its command.
- **No new switch.**
  - No new `AILIBI_*` lever, no environment switch, no experiment-config field.
  - No prompt registry bump and no prompt or detector byte change: the census is an offline reader that nothing feeds
    back from.
  - No recorded byte is edited and no history is re-scored. The round-2 record's "not carried" lines stay as
    recorded, and a later instrument never changes an earlier verdict.
  - The corpus FROZEN line and the ML artifacts never move. Offline `scripts/verify_ml_evidence.py` passes; never
    `--complete`.
- **Role and the owner's direction.**
  - Role-correctness is reported, never a gate. Role appears only as a reported column: the impostor seat class, the
    impostor ballots the counterfactual converts.
  - No cell judges a decision by its target's role, and nothing pushes an agent toward the correct answer.
  - The meeting layer labels and never rewrites; the census reads its labels as recorded.
- **Not restated here.** The envelope's pre-registered reporter line (0.104, absolute) is not restated, recomputed
  or reframed relative to the other-innocent rate. The page shows the two numbers side by side and draws no line.
  Reading the line relative is the owner's decision (diagnosis Part 4 item 2).
- **The census stays out of the scorecard** (ruling R13). No scorecard row or context line changes.
- **Page copy.** The page's own Terms section defines every new term in plain words: seat, one or more living
  witnesses, re-tally, holds-nothing label, rebuttal citation. The copy carries no task or audit IDs, unexplained
  jargon or threshold arithmetic. It says the counterfactual holds every other ballot fixed, and that real voters
  would have heard different speech.
- **Data handling.** Count-only, keyed by (set, meeting). No rendered prompt, transcript text or seed-band prefix is
  printed. No live provider call is made, and the untracked `.env` is never read.
- **The open point is not decided here.** False resume perceptions stay "not carried": no committed source holds a
  per-observer perception record, and none is invented. Recording one would be a recording change, outside this card.
- **Ownership and merge order.** This card dispatches in parallel with `route-check-replay` and
  `post-promotion-follow-through` from `main` at the coordination commit that lands the four cards, and it merges
  first. Route merges second, the follow-through card third (by the owner), and `rubric-extractor-era`, dispatched
  after the follow-through merge, last.
  - This card alone writes `eval/gameplay_census.py`, `eval/eras.py`, `eval/process_scorecard.py`,
    `scripts/counterfactual_phase21.py`, `scripts/publish_gameplay_census.py` and `docs/gameplay-census.md` and
    `.json`. `route-check-replay` reads `load_census_inputs` and `IMPOSSIBLE_TRANSIT_PATTERN` and re-runs its
    denominator agreement on `main` after this card merges; `rubric-extractor-era` only reads `era_of`.
  - `docs/artifacts.md`: this card writes only the gameplay-census row's text, in its last commit after merging
    `main`, then re-runs `scripts/verify_ml_evidence.py` offline. The other rows are the other three cards'.
  - `tasks/README.md`: the inventory sentence only, re-derived with `scripts/validate_task_docs.py` at this card's
    final merge of `main`. The other cards re-derive it after this one, in the merge order.
  - It does not touch `scripts/_declared_experiment.py`, `scripts/refresh_samples.sh` or
    `tests/scripts/test_refresh_samples.py`; other cards own them.
  - `tests/eval/test_kill_cooldown_readers.py` is `rubric-extractor-era`'s. The C5 planted case lives in
    `tests/eval/test_gameplay_census.py`. A break that this card's new raises cause in the cooldown readers' file
    goes to the orchestrator, never into an edit here.
  - One writer per file: the files under Expected scope are this card's for its dispatch.
- **Lessons from the Stage-B wave.**
  - Every production line is enforced by a test that goes red when it is neutered.
  - Each guarantee is stated at the strength delivered.
  - A live-tense sentence about old behaviour is fixed in the same PR. That includes the `pool()` docstring ("carries
    no era to check"), the comment above `CANONICAL_SETS` ("refused by name") and the name and docstring of
    `test_a_committed_set_of_another_era_is_refused_by_name`.
  - Numbers are measured at the head that states them, and universal guarantees are stated as properties.
  - No test is weakened.
- **Delivery.**
  - Branch `work/census-reporter-base-rate`, one PR into `main`, merge commit or fast-forward, never a squash.
  - Each commit body ends with `Card: tasks/work/census-reporter-base-rate.md`, followed immediately by the exact line
    `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Publication.** The change is eval code, scripts, tests and docs only. The census and scorecard pages are not in
  the demo bundle: `pages.yml` builds from `replays/samples`, the featured list and the public-results payload, and
  `scripts/build_demo_bundle.py` imports none of the touched modules. The merge publishes nothing new, so it is the
  orchestrator's merge.

**Open points for the owner.**
1. False resume perceptions have no committed count source. Either accept the shared helper and the golden's
   byte-equal re-render as what carries it, or ask for a per-observer perception record, which is a recording change
   beyond this card.
2. The reporter line, absolute or relative (diagnosis Part 4 item 2). This card only puts the numbers side by side.
3. The pre-registration names no ballot slot for "ballots citing a rebuttal". The card takes the turn citation as
   that cell and reports the counter slot beside it.
4. C5 is folded in beyond the three hardening items the dispatch named, because it sits in a file this card already
   owns. The orchestrator may strike it.

## Expected scope

- `eval/gameplay_census.py`, with these changes:
  - the new heading, cells, tables and terms;
  - new carrier fields, each defaulting empty so a hand-built carrier without them counts nothing (as
    `cooldown_writes` does), which leaves other files that build carriers unedited;
  - the loader's citation ids and notice booleans;
  - the tally identity;
  - the C5 message.
  `SCHEMA_VERSION` stays 2 because the change is additive. Results confirms that no in-tree reader of the JSON breaks.
- `scripts/publish_gameplay_census.py`: rendering of the new heading and tables, where its generic rendering needs it.
- `docs/gameplay-census.md` and `docs/gameplay-census.json`: regenerated, never hand-edited.
- `eval/eras.py`: the E3 helper.
- `eval/process_scorecard.py`: `pool()` only.
- `scripts/counterfactual_phase21.py`: `run()`'s era refusal and the comment above `CANONICAL_SETS` only.
- `tests/eval/test_gameplay_census.py`: the planted cases, the properties and the reporter-justice agreement.
- `tests/scripts/test_publish_gameplay_census.py`: the page tests.
- `tests/eval/test_eras.py`: E3.
- `tests/eval/test_process_scorecard.py`: the `pool()` cases.
- `tests/scripts/test_counterfactual_phase21.py`: C3.
- `docs/artifacts.md`: the census row's description of what the page counts, and nothing else.
- `tasks/work/census-reporter-base-rate.md`: this card's Status and Results.
- `tasks/README.md`: the inventory sentence, as the validator derives it.

Follow-through outside this list needs a line in Results naming the file and why. A file another card of the wave owns
is not touched; the conflict is raised with the orchestrator instead.

## Record impact

- **Recorded bytes.** None. Nothing under `replays/` moves, and no MANIFEST, stamp, prompt or detector byte changes.
- **Future behaviour.** None. No agent, meeting or engine path reads the census. The new conformance raises (the
  tally identity, the notice guard) stop only the census fold, and they read 0 on every committed set at authoring.
- **Compatibility.** The census JSON gains cells and tables additively, at schema version 2.
  - The scorecard page and JSON are byte-identical.
  - `pool()` and the counterfactual refuse inputs they used to accept: an unregistered pooling source, and an
    aliased spelling of a non-baseline-9 committed set. No production path passed either.
- **Evaluation.** The census page gains the base rate, the witness outcomes, the counterfactual tallies, the
  holds-nothing label and three of the four pre-registered cells, per era. No verdict, envelope line or ruling
  changes.
- **Adoption.** Not applicable: there is no experimental behaviour.

Measurement: the cells read on the four committed sets at the implementation head, and the round-1 column read with
`--set-dir`. Results quotes the commands below with their output.

## Validation

```
env | grep -c '^AILIBI_'                      # 0
uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py \
  tests/eval/test_eras.py tests/eval/test_process_scorecard.py tests/scripts/test_counterfactual_phase21.py \
  -n 6 --dist loadfile
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
uv run python scripts/publish_process_scorecard.py --check
uv run python -m eval.reporter_justice replays/samples/9p2i replays/ml_corpus/9p2i
uv run python scripts/verify_ml_evidence.py   # offline; never --complete
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
git diff --stat main -- replays/ docs/process-scorecard.md docs/process-scorecard.json   # empty
bash scripts/check.sh
```

Results records the following:
- each command's exit code and the counts it printed;
- the planted cases red before the change and green after, by name;
- the neuter table and the mutation pass;
- the sections this card rests on: `docs/architecture.md` "Layering" (`eval/` as a privileged reader), "Enforced
  boundaries" and "Determinism and the substrate ladder" (instruments never pool eras);
- ruling R13, the diagnosis Part 3 card 1, and the round-2 record 1.9 and 6.2;
- the open points under Constraints, and the limitations.

Limitations to state:
- The `s9` column the diagnosis quotes is not reproducible at this head.
- Each round is one hosted recording of 50 games.
- The counterfactual holds every other ballot fixed.
- The holds-nothing label is the voter's own statement.

## Results

Done on `work/census-reporter-base-rate`, from `origin/main` at `5877adb4`; `origin/main` had not moved when the
last gate ran. Every count below is count-only, keyed by (set, meeting); no prompt, transcript text or seed-band
prefix was printed. Scratch work stayed under the session scratchpad.

**Commits**, in order: `854202a2` E3, `ERAS` held to the registry; `29d95d0f` `pool()` refuses what it cannot
place; `61535fb5` C3, the counterfactual's refusal by resolved directory; `3eb8cc5b` the census cells, the two
gates, the C5 case and the regenerated page and JSON; `badadaaf` the two mutation-pass survivors killed and the
module exports pinned; `65a4a0cf` the two gaps the neuter pass found closed; then this card's Results, the census
row and the inventory sentence; then the commit recording the final `check.sh` run.

**Sections relied on.** This card; `docs/architecture.md` "Layering" (`eval/` is a privileged reader and may
import `agents/`, `meetings/` and `engine/`), "Enforced boundaries" (no `agents/` import of `engine/` is added;
the census is the importer) and "Determinism and the substrate ladder" (instruments never pool eras); ruling R13
(`tasks/decision-2026-09-24-stage-b-wave.md:57`, the census stays out of the scorecard); the diagnosis
(`tasks/diagnosis-2026-10-02/README.md`) Part 1.4, Part 2.2, Part 3 card 1 and Part 4 items 2 and 7; the round-2
record (`audits/audit-2026-10-01-stage-b-r2.md`) 1.9 (each cell's source) and 6.2 (the golden's byte-equal
re-render that stands behind the resume-perception cell), 6.4 and 8.

### What the census now carries

Measured at this head through the production fold (`load_census_inputs`, `fold_set`), and read back from the
regenerated `docs/gameplay-census.json` by `test_the_committed_json_reproduces_the_base_rate_figures`. Round 1 is
`publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` (written nowhere, never
pooled). The baseline-9 era is `ml_corpus/9p2i`, `ml_corpus/4p1i` and `samples/4p1i`, pooled.

| cell | `samples/9p2i` (stage-b-r2) | round 1 (`--set-dir`) | baseline 9, pooled | `ml_corpus/9p2i` |
|---|---|---|---|---|
| reporter seats ejected: total; without vent proof; with it | 17/114; 17/93; 0/21 | 11/118; 11/98; 0/20 | 30/488; 29/271; 1/217 | 29/416; 28/234; 1/182 |
| other crewmate seats ejected: total; without; with | 5/367; 5/291; 0/76 | 2/372; 2/303; 0/69 | 2/1390; 2/703; 0/687 | 2/1318; 2/666; 0/652 |
| impostor seats ejected: total; without; with | 41/195; 20/158; 21/37 | 35/194; 15/160; 20/34 | 247/669; 32/340; 215/329 | 210/597; 30/303; 180/294 |
| reporters among crewmates ejected; among crewmate seats | 17/22; 114/481 | 11/13; 118/490 | 30/32; 488/1878 | 29/31; 416/1734 |
| held kills: one living witness (killer, witness, other, no one); two or more (killer) | 9 (1, 5, 1, 2); 5 (5) | 3 (3, 0, 0, 0); 0 | 16 (9, 2, 1, 4); 1 (1) | 15 (9, 2, 1, 3); 1 (1) |
| held kills whose killer some later meeting ejected; whose living witness was ejected | 8/14; 5/14 | 3/3; 0/3 | 13/17; 2/17 | 13/16; 2/16 |
| ejections that would not stand: impostor ballots as SKIP; removed | 14/66; 5/66 | 8/54; 2/54 | 15/321; 7/321 | 14/273; 6/273 |
| of those, the reporter ejected (as SKIP; removed) | 10; 4 | 7; 2 | 13; 7 | 12; 6 |
| SKIP ballots labelled `none_held` | 214/281 | 256/330 | 764/1183 | 702/1052 |
| ballots whose cited turn names a rebuttal; whose counter slot does | 57/691; 175/691 | 70/707; 150/707 | n/a; n/a | n/a; n/a |
| prompts after a regroup missing an earlier regroup's notice | 0/722 by construction | 0/782 by construction | n/a | n/a |

Every count equals the card's authoring table wherever both read the same bytes. The two 4p1i sets add 1 reporter
ejection over 72 reporter seats (`ml_corpus/4p1i` 1/36, `samples/4p1i` 0/36). The recorded ballots, re-tallied as
recorded at their recorded floor, reproduce the recorded outcome at every meeting of all five sets read: the fold
raises on a mismatch and raised on none (648 committed meetings plus round 1's 124).

The reporter and other-crewmate rows stand side by side on the page. No line, ratio, relative risk or verdict is
drawn between them; the envelope's pre-registered reporter line is not restated
(`test_the_census_names_no_line_and_relates_no_two_rates`).

### Planted failures, red and green

Each new gate or cell has a hand-built case that is red on the named defect and green on the production fold.
The commands are `uv run pytest <file>::<test>`; each passed at this head, and each red was shown by the
perturbed fold named (a monkeypatched function inside the test, or a mutant of the pass below).

| defect | test (red on the defect, green on the fold) |
|---|---|
| a role-first seat partition (impostor reporter, self-report era) | `test_an_impostor_reporter_sits_in_the_reporter_class`; property `test_a_role_first_partition_fails_the_partition_property` |
| a button meeting seated; a dead player seated; the ejected player's vent band read as the meeting's proof | `test_the_seat_cells_count_every_living_seat_of_every_report_meeting` (exact counts; mutants M01-M07) |
| a seat dropped from `living` breaks the agreement with the reporter instrument | `test_a_seat_dropped_from_living_breaks_the_agreement` (names the meeting) |
| an impostor witness read as corroboration; a witness dead by the meeting; the kill-tick meeting skipped; the killer's later ejection read as the next meeting's | `test_an_impostor_among_the_witnesses_is_no_corroboration`, `test_a_witness_dead_by_the_meeting_is_not_a_living_witness`, `test_a_meeting_on_the_kills_own_tick_is_its_next_meeting`, `test_a_killer_ejected_at_a_second_meeting_is_no_next_meeting_outcome`, `test_a_meeting_before_the_kill_is_not_a_later_meeting` |
| the tally identity: ballots ejecting another player; a skip whose ballots eject; an ejection with no ballot | `test_a_meeting_whose_ballots_eject_another_player_is_refused`, `test_a_skip_or_an_ejection_its_ballots_do_not_give_is_refused` (set, seed and meeting each varied, so none is read as a constant) |
| a SKIP re-tally that drops instead of converting (pinned 1 of 1, would read 0 of 1) | `test_a_skip_re_tally_converts_impostor_ballots_and_a_removal_drops_them` |
| a fixed 0.6 floor in place of the recorded 0.5 | `test_every_tally_reads_the_meetings_recorded_floor` (mutant M10) |
| an ejection moving to another player read as standing | `test_an_ejection_moving_to_another_player_does_not_stand` (mutant M12) |
| an unlabelled SKIP read as `none_held`; a `none_held` EJECT counted; a label outside the vocabulary | `test_the_holds_nothing_cell_counts_every_skip_and_only_skips`, `test_a_label_outside_the_vocabulary_is_refused_on_any_ballot` |
| the label rows copied instead of read from the type (source change) | `test_the_label_rows_follow_the_type_when_its_vocabulary_changes` (mutant M23) |
| a ballot citing the rebuttal speaker's first turn; a rebuttal id from another meeting | `test_ballots_citing_a_rebuttal_read_their_own_meetings_rebuttal_turns` |
| both citation cells outside the rebuttal era | `test_without_the_rebuttal_both_citation_cells_read_n_a_never_zero`; on the committed baseline-9 columns, `test_on_baseline_9_every_scoped_cell_and_table_reads_n_a` |
| a prompt missing an earlier regroup's notice (the guard) | `test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off[prompts_missing_a_regroup_notice-...]`; on a real round-2 game, `test_a_prompt_missing_an_earlier_regroups_notice_is_refused` (set, seed 0, meeting named) |
| a prompt at a game's first meeting in the denominator; a meeting's own regroup read as earlier | `test_the_promoted_harness_reproduces_the_committed_game`, `test_a_meetings_own_regroup_is_no_earlier_regroup` |
| a perturbed copy of the renderer's wording (the sourced constant's source-change case) | `test_a_perturbed_renderer_wording_fails_the_notice_pin` |
| the notice's tick or room read from anything but the resumed state and the walk | `test_the_notice_reads_the_resumed_states_tick_and_the_walks_room`, `test_a_regroup_the_walk_names_no_room_for_is_refused` |
| a relative-risk cell added to the cell table | `test_a_relative_risk_cell_turns_the_restatement_scan_red` |
| round 1's era key pooled with the promoted era's before any cell is summed | `test_round_1_never_pools_with_the_promoted_era_before_any_cell_is_summed` (the cells mapping raises if read; the era refusal comes first) |
| E3: `ERAS` without `STAGE_B_R2`; a registry naming a third era | `test_eras_held_to_the_registry_turns_red_on_either_side`; the real removal is neuter E01 below |
| C3: `./samples/9p2i`, `samples//9p2i`, `candidates/../samples/9p2i`; a third era by a monkeypatched registry | `test_a_committed_set_of_another_era_is_refused_by_its_resolved_directory`, `test_a_registered_set_of_a_third_era_is_refused_with_that_eras_id` |
| `pool()`: a candidate beside a baseline-9 set; `sources=()` with two tallies | `test_a_candidate_pooled_with_a_baseline_9_set_is_refused`, `test_sources_and_tallies_must_pair_one_to_one` |
| C5: a scratch registry's second era holding two sets at different cooldowns | `test_the_cooldown_refusal_names_the_era_its_registry_gives` |

**Properties** (Hypothesis, `settings(deadline=None, database=None)`), each green on the production fold and each
quoted red on its perturbed fold:

| property | production | perturbed fold, red |
|---|---|---|
| Partition: the three classes partition every report meeting's living seats; the reporter's seat is the reporter's whatever its role (generator: any living subset, any reporter, impostors included, self-report era) | `test_the_seat_classes_partition_every_report_meetings_living_seats` green | role-first `seat_class`: `test_a_role_first_partition_fails_the_partition_property` asserts the run raises `AssertionError` |
| Identity, first half: with no impostor voter both re-tallies equal the record | `test_without_an_impostor_voter_both_re_tallies_are_the_record` green | a SKIP re-tally that also converts crew ballots: `test_a_skip_re_tally_converting_a_crew_ballot_fails_the_identity` red |
| Identity, second half: when every EJECT ballot is an impostor's (one voter included) both re-tallies eject no one | `test_when_only_impostors_eject_both_re_tallies_eject_no_one` green | a SKIP re-tally leaving one impostor ballot: `test_a_skip_re_tally_leaving_an_impostor_ballot_fails_the_identity` red |
| Sum: the witness rows sum to the held kills; the killer and witness rows to their next-meeting cells (generator reaches two or more living witnesses) | `test_the_witness_rows_sum_to_the_held_kills` green | a fold dropping the two-or-more row: `test_a_fold_dropping_the_two_or_more_row_fails_the_witness_sum` red |

**The base rate agrees with the scorecard's context.** `test_the_seat_totals_are_the_reporter_instruments_slots`,
on each of the four committed sets, holds the census's per-seat totals (without plus with vent proof, and each
class's total cell equal to that sum) to `compute_reporter_justice`'s `reporter_slots`, `reporter_ejections`,
`innocent_non_reporter_slots`, `innocent_non_reporter_ejections`, `impostor_slots` and
`impostor_slot_ejections`, and lists every report meeting whose living seats differ from its ballot voters. That
list is empty on all four sets: the two seat definitions agree on the committed bytes.

### One bounded mutation pass

The eight classes and no others, each mutant alone against the touched suites (`test_gameplay_census.py` and
`test_publish_gameplay_census.py` for the census; the era, scorecard and counterfactual suites for theirs), the
file restored from an in-memory copy after each run. Script: `<session scratchpad>/crbr/mutate.py`.

| id | class | file: mutant | first run | killed by |
|---|---|---|---|---|
| M01 | F | census: crew shares read impostor seats too | killed | `test_the_seat_cells_count_every_living_seat_of_every_report_meeting` |
| M02 | S | census: seats from `game.roles` in place of `meeting.living` | killed | `test_the_seat_classes_partition_every_report_meetings_living_seats` |
| M03 | N | census: a seat ejected read as `ejected is not None` | killed | partition property |
| M04 | B | census: the vent-proof columns swapped | killed | seat cells |
| M05 | C | census: the reporter read as `p-2` | killed | partition property |
| M06 | B | census: impostor and crewmate seat classes swapped | killed | seat cells |
| M07 | F | census: the crew-ejection share counts every crew seat | killed | seat cells |
| M08 | F | census: the SKIP re-tally converts every ballot | killed | `test_the_change_table_names_the_recorded_seat_and_what_the_re_tally_gives` |
| M09 | S | census: the SKIP re-tally drops instead of converting | killed | `test_an_ejection_moving_to_another_player_does_not_stand` |
| M10 | L | census: the recorded floor read as 0.6 | killed | identity property, first half |
| M11 | N | census: the tally identity inverted | killed | (every carrier) `test_corpse_age_reads_the_kill_event_tick_never_the_body_id` |
| M12 | N | census: an undone ejection read as `result is None` | killed | moving-ejection test |
| M13 | F | census: the undone cells count skipped meetings | killed | change-table test |
| M14 | B | census: impostor and crewmate recorded classes swapped | killed | moving-ejection test |
| M15 | C | census: the trigger kind read as report | **survived** | killed after: `test_a_button_presser_ejected_is_another_crewmate_not_the_reporter` |
| M16 | B | census: the two result classes swapped | killed | moving-ejection test |
| M17 | M | census: the identity message's set read as a constant | killed | `test_a_meeting_whose_ballots_eject_another_player_is_refused` |
| M18 | B | census: the witness bands swapped | killed | `test_a_meeting_on_the_kills_own_tick_is_its_next_meeting` |
| M19 | N | census: a witness ejected read as `ejected is not None` | killed | kill-tick meeting test |
| M20 | F | census: the later-meeting filter dropped | killed | `test_a_meeting_before_the_kill_is_not_a_later_meeting` |
| M21 | S | census: witnesses ejected read from `following.living` | killed | kill-tick meeting test |
| M22 | F | census: the witness table's zero rows dropped | killed | `test_the_witness_table_lists_all_eight_rows_even_at_zero` |
| M23 | L | census: the label vocabulary as its literal | killed | `test_the_label_rows_follow_the_type_when_its_vocabulary_changes` |
| M24 | F | census: the SKIP filter on the label cells dropped | killed | holds-nothing test |
| M25 | M | census: the label refusal's set read as a constant | killed | `test_a_label_outside_the_vocabulary_is_refused_on_any_ballot` |
| M26 | S | census: rebuttal ids from every turn | killed | rebuttal-citation test |
| M27 | N | census: the counter slot read as `is not None` | killed | rebuttal-citation test |
| M28 | N | census: the notice count inverted | killed | `test_a_prompt_missing_an_earlier_regroups_notice_is_refused` |
| M29 | L | census: the regroup room as the canonical `CAFETERIA` | killed | `test_the_notice_reads_the_resumed_states_tick_and_the_walks_room` |
| M30 | F | census: calls without an agent id held to the notice | killed | `test_a_notice_is_held_per_agent_call_and_only_after_a_regroup` |
| M31 | N | eras: the one-id refusal inverted | killed | `test_eras_is_the_registrys_eras_oldest_first` |
| M32 | F | eras: the date sort dropped | killed | `test_registered_eras_sort_by_date_then_first_appearance` |
| M33 | N | scorecard: the count refusal inverted | killed | `test_sources_and_tallies_must_pair_one_to_one` |
| M34 | F | scorecard: the registered filter on the unplaced list dropped | killed | `test_pooling_adds_counts_and_recomputes_every_rate` |
| M35 | M | scorecard: the refusal's label read as a constant | killed | `test_pooling_two_eras_is_refused_and_one_era_pools` |
| M36 | N | counterfactual: the unregistered test inverted | killed | `test_a_committed_set_of_another_era_is_refused_by_its_resolved_directory` |
| M37 | C | counterfactual: the era id read as `stage-b-r2` | killed | `test_a_registered_set_of_a_third_era_is_refused_with_that_eras_id` |
| M38 | L | counterfactual: the registry read as the canonical import | killed | third-era test |
| M39 | F | counterfactual: the `.resolve()` on the named directory dropped | **survived** | killed after: the `candidates/../samples/9p2i` spelling in the resolved-directory test |

39 mutants; 37 killed on the first run, 2 survived (M15, M39), both killed by the cases `badadaaf` adds (re-run:
`mutate.py M15 M39`, both KILLED). None is named equivalent.

### The per-line neuter table

Every production line, table row, dict row and call-site argument this card adds or changes, neutered one at a
time (a value replaced, a statement removed, a branch turned off), the touched suite run with `-x`, the file
restored from an in-memory copy. Script: `<session scratchpad>/crbr/neuter.py`; 134 units. Rows that one test
turns red for the same reason are grouped.

| units | what was neutered | first red test |
|---|---|---|
| U01 | the notice wording | `test_the_regroup_notice_wording_is_the_renderers` |
| U02, U03 | `HOLDS_NOTHING_LABEL`; `UNLABELLED` | `test_the_holds_nothing_cell_counts_every_skip_and_only_skips` |
| U04-U09 | each of the two witness bands and four next-meeting outcomes | `test_the_witness_table_lists_all_eight_rows_even_at_zero` |
| U10 | `AS_RECORDED`'s value | green: **equivalent**, a private key of `retally`'s mapping read only through the constant and never published |
| U11-U13 | the two re-tally names; the removal row of `RETALLY_VARIANTS` | `test_the_committed_json_reproduces_the_base_rate_figures` |
| U14 | the removal row of `_UNDONE_CELLS` | `test_a_skip_re_tally_converts_impostor_ballots_and_a_removal_drops_them` |
| U15-U17 | each seat-class name | `test_an_impostor_reporter_sits_in_the_reporter_class` |
| U18-U20 | each `_SEAT_CELLS` row | seat-cells test; `test_the_seat_totals_are_the_reporter_instruments_slots[samples/4p1i]` |
| U21, U22, U24-U51 | a `_SEAT_READS` member; the heading text; each of the 19 new cell titles, 3 table titles and 6 term keys | `test_the_committed_census_matches_a_recomputation` |
| U23 | the heading's `HEADINGS` row | `test_every_cell_and_table_is_published_and_ordered_under_a_heading` |
| U52, U60-U63 | the seat-fold call; each of its four counts | `test_the_seat_cells_count_every_living_seat_of_every_report_meeting` |
| U53-U55 | the notice count; its `where` and `seed` arguments | the regroup-notice guard pair |
| U56, U57 | `_has_vent_proof`'s body; the proof cell's read of it | `test_moving_the_flag_leaves_the_band_but_keeps_the_proof` |
| U58, U59 | the reporter branch of `seat_class`; the seat fold's proof read | `test_a_seat_is_read_from_the_meetings_own_vent_proof_and_reporter` |
| U64 | the seat fold's `where` | green: **equivalent**, the seat cells carry no guard, so `where` is read only by a breach message that cannot fire |
| U65, U66 | the two citation counts | `test_ballots_citing_a_rebuttal_read_their_own_meetings_rebuttal_turns` |
| U67 | the turn-citation cell reading the counter slot | **green first**: both slots counted one ballot; `65a4a0cf` adds a second citing ballot, re-run red |
| U68, U71 | the as-recorded branch; the tally's `target` argument | `test_an_ejection_carried_only_by_impostor_ballots_reads_the_recorded_floor` |
| U69 | the removal branch | `test_an_ejection_moving_to_another_player_does_not_stand` |
| U70 | the unknown-tally refusal | `test_an_unknown_tally_is_refused` |
| U72, U74 | the tally's `confidence` argument; its floor argument | `test_every_tally_reads_the_meetings_recorded_floor` |
| U73 | the tally's `voter` argument | green: **equivalent**, `tally_ballots` reads only target and confidence |
| U75, U76 | the as-recorded member of `retally`; the no-one branch of the recorded class | the stale-report guard pair (every meeting re-tallies) |
| U77 | the reporter branch of the recorded class | `test_the_change_table_names_the_recorded_seat_and_what_the_re_tally_gives` |
| U78, U84-U87 | the no-one result; the recorded class; the undone count; the change tally; the change row's result | `test_a_skip_re_tally_converts_impostor_ballots_and_a_removal_drops_them` |
| U79-U83, U88 | the identity raise; each of its four message arguments; the re-tally call | `test_a_meeting_whose_ballots_eject_another_player_is_refused`, `test_a_skip_or_an_ejection_its_ballots_do_not_give_is_refused` |
| U89, U93, U94 | the label zero rows; the holds-nothing count; the label tally | holds-nothing test |
| U90, U92 | the unlabelled zero row; the refusal message's label | `test_the_label_rows_follow_the_type_when_its_vocabulary_changes` |
| U91 | the label refusal | `test_a_label_outside_the_vocabulary_is_refused_on_any_ballot` |
| U95-U98 | the later-meeting count; the witnesses-ejected count; the table tally; the killer branch | `test_an_impostor_among_the_witnesses_is_no_corroboration` |
| U99, U100 | the loader's two citation arguments | `test_the_loader_copies_each_ballots_turn_and_counter_citations` |
| U101 | the loader's notice argument | `test_a_prompt_missing_an_earlier_regroups_notice_is_refused` |
| U102, U103 | the empty-notice guard; the every-notice read | `test_a_notice_is_held_per_agent_call_and_only_after_a_regroup` |
| U104, U109 | the earlier-notices argument; the notice's tick | `test_the_promoted_harness_reproduces_the_committed_game` |
| U105 | the regroup-recorded filter on earlier notices | `test_the_seat_totals_are_the_reporter_instruments_slots[ml_corpus/9p2i]` (a baseline-9 game with two meetings asks for a room) |
| U106 | the phase filter on earlier notices | green: **equivalent**, a meeting that ended the game is its last, so no later meeting reads its notice |
| U107 | the earlier slice reaching the meeting's own close | `test_the_loader_reads_the_recorded_reset` |
| U108 | the no-room refusal | `test_a_regroup_the_walk_names_no_room_for_is_refused` |
| U110-U122 | each new `__all__` entry | `test_the_module_exports_every_public_name_it_defines` |
| E01 | `STAGE_B_R2` dropped from `ERAS` (the review's E3 mutant) | `test_eras_is_the_registrys_eras_oldest_first` |
| E02 | the one-id refusal | `test_two_eras_filed_under_one_id_are_refused` |
| E03 | the date sort key | `test_eras_held_to_the_registry_turns_red_on_either_side` |
| E04 | `registered_eras` in `__all__` | the era module's exports test |
| P01, P04 | the count refusal; its message | `test_sources_and_tallies_must_pair_one_to_one` |
| P02 | the unplaced refusal | `test_pooling_two_eras_is_refused_and_one_era_pools` |
| P03 | `era_groups`'s `registry` argument | `test_pooling_adds_counts_and_recomputes_every_rate` |
| C01, C02, C04 | the refusal; the entry match; the message's set name | `test_a_committed_set_of_another_era_is_refused_by_its_resolved_directory` |
| C03 | the resolve of the registry's own path | **green first**: every committed entry is already canonical; `65a4a0cf` plants an entry spelled through another directory, re-run red |

Green first: U67 and C03, both closed by `65a4a0cf` and re-run red (`neuter.py U67 C03`). Equivalent: U10, U64,
U73 and U106, each for the reason in its row. Every other unit was red on the first run.

### Validation, each run to its end

Run at `65a4a0cf` (the head before this card's Results commit, whose tree differs only in this card, the census
row and the inventory sentence), each to its end with its exit code captured directly.

| command | exit, and what it printed |
|---|---|
| `env \| grep -c '^AILIBI_'` | `0` |
| `uv run pytest` over the card's five suites, `-n 6 --dist loadfile` | 0: 581 passed |
| `uv run python scripts/publish_gameplay_census.py --check` | 0: both files consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0: section `stage-b-r1/9p2i`, 50 games, 124 meetings, the round-1 column above; nothing written |
| `uv run python scripts/publish_process_scorecard.py --check` | 0: both scorecard files consistent; `git diff --stat main -- replays/ docs/process-scorecard.md docs/process-scorecard.json` empty |
| `uv run python -m eval.reporter_justice replays/samples/9p2i replays/ml_corpus/9p2i` | 0: per-slot reporter 17/114, innocent non-reporter 5/367, impostor 41/195; and 29/416, 2/1318, 210/597 (the census's seat totals) |
| `uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `uv run python scripts/validate_task_docs.py` | 0: 390 historical phase tasks and 390 prompts; 96 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 |
| `bash scripts/verify_samples.sh <dir>`, once per set: `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, round 1 | 0 each |
| `uv run python scripts/build_sample_report.py --check --sample-dir <dir>`, the same five sets | 0 each |
| `uv run pytest -m campaign -n 6` | 0: 337 passed |
| the census's other readers (`test_kill_cooldown_readers.py`, `test_vent_witness_readers.py`, `test_ballot_arms.py`, `test_report_body_handle.py`, `test_meeting_reset_coherence.py`, `test_scripted_meeting.py`, both look-and-wait suites, `test_verify_ml_evidence.py`) | 0: 550 passed, none edited; the JSON's additive cells break no in-tree reader |
| demo bundle: `build_demo_bundle.py --out` at `5877adb4`, then at the head, in this one checkout; `diff -rq` | 0: the two bundles' 109 files are byte-identical; nothing ships |
| `bash scripts/check.sh` at the pushed head `6a745209`, run once, its exit code captured directly | 0: ruff and format clean (551 files), the four import-linter contracts kept, task docs valid, strict mypy clean (522 source files), 10,106 Python tests passed (20 skipped, 3 xfailed), frontend lint and type checks clean, 649 frontend tests passed (25 files), the frontend build green. The commit recording this changes only this row |

No frontend file changed, so `npm --prefix frontend test` and the e2e were not run.

### Decisions

Decisions 1 to 6 record the orchestrator's rulings of 2026-10-02 on the card's open points.

1. **C5 stays folded in** (ruling 1), since it sits in the file this card owns: the cooldown refusal already named
   `era.id`; the planted case under a scratch registry now holds it.
2. **False resume perceptions** (ruling 2): no source is invented. The cell stays "not carried"; what carries it is
   the shared helper `compose_resume_events` (`orchestrator/replay.py:1427`) with its planted tests and the
   golden's byte-equal re-render of all 1,502 recorded round-2 prompts (round-2 record 6.2). A per-observer
   perception record would be a recording change; it is open point 1 for the owner.
3. **The envelope's reporter line is not restated** (ruling 3): the page reports the reporter's and the other
   seats' rates side by side with no line, ratio or verdict, and a page test refuses one.
4. **Ballots citing a rebuttal** (ruling 4): the turn citation (`primary_reason_id`) is the cell, with the counter
   slot (`counter_reason_id`) beside it. This is the card's interpretation of a pre-registration that named no
   slot.
5. **The `pool()` hardening flips one pinned expectation** (ruling 5), and the new one is the era refusal named by
   its message. Old (`tests/eval/test_process_scorecard.py`, `test_pooling_two_eras_is_refused_and_one_era_pools`):
   `pool([left, right], label="hand-built", sources=("replays/samples/9p2i", "b"))` returned, with
   `sources == ("replays/samples/9p2i", "b")`. New: the same call raises `ValueError` matching
   `^hand-built: the era registry places no b in an era; the scorecard pools only sets of one recorded era$`.
   The two arithmetic tests pass `_SCRATCH_REGISTRY` (`a` and `b` in baseline 9); their pinned values are
   unchanged.
6. **Properties carry their perturbed folds** (ruling 6): each property above names the fold that turns it red,
   and every Hypothesis property here carries `settings(deadline=None)`.
7. **The tally identity runs last in each meeting's ballot fold**, after the per-ballot cells, so the existing
   guards (the teammate ballot) and role-read refusals keep raising first, as their tests pin.
8. **Hand-built carriers re-derived.** The identity refuses a meeting whose recorded outcome its ballots do not
   give, which the carriers of 16 existing tests and 3 shared builders in `tests/eval/test_gameplay_census.py`
   did (an ejection with no ballot, or a target ballot under a recorded skip). Each now carries the ballots that
   give its outcome (the `ejecting()` helper, or a crewmate's SKIP that ties the vote); no carrier in another
   file needed it. Every asserted count is unchanged except one:
   `test_the_impostor_only_floor_reads_only_confident_ballots_for_the_ejected` pinned an ejection with no ballot at
   the floor (old: one impostor ballot at 0.1, expected `(0, 1, 0)`), a tally the game cannot produce. Its new
   case is an impostor ballot at 0.9 beside a crewmate's at 0.1 (expected `(1, 1, 0)`); dropping the confidence
   filter still turns it red. The cell's `bool(confident)` guard is now unreachable on a conforming carrier.
   One carrier gained a ballot of another shape: `test_the_impostor_only_floor_reads_recorded_targets_on_either_side`
   held one impostor ballot for the ejected `p-2` (rewritten from `p-4`) beside a SKIP and a ballot for `p-3`, a
   tie the tally skips. `3eb8cc5b` added the other impostor's ballot for `p-2` at 0.9, which a floor reading the
   authored target also found, so the test stopped catching that read. Review round 1 lowered it below the
   floor: old `ballot("p-1", "p-2")` at 0.9, new `ballot("p-1", "p-2", confidence=0.1)`. The tally still
   ejects `p-2` (two ballots, one at the floor), the expected `(1, 1, 0)` is unchanged, and the authored-target
   read gives `(0, 1, 0)`, red.
   One pin of this card's own moved during the neuter pass: the rebuttal-citation test gained a second citing
   ballot, so its counts went from `(1, 6, 0)` for both cells to `(2, 7, 0)` and `(1, 7, 0)`.
9. **The recorded outcome's seat is reporter-first only at a report meeting**: a button meeting's presser ejected
   reads "another crewmate ejected". The crewmate shares exclude an impostor reporter's seat.
10. **Zero rows are listed** in the label table (every member of `BallotGroundingLabel` plus `unlabelled`) and the
    witness table (all eight rows), so each table shows its whole shape; the change table lists only changes.
11. **The regroup notice** is formed from the resumed state's tick and the walk's regroup room (the arguments the
    live fold hands `ingest_public_regroup`), only when a later meeting of the game reads it; a regroup the walk
    names no room for raises. The cell has the regroup guard and no scope: its denominator exists only after a
    regroup.
12. **Follow-through inside owned files:** the counterfactual's module docstring line said the promoted set "is
    refused by name"; it now says by the registry entry of its resolved directory. `eval/eras.py`'s docstring
    names the new `ERAS` pin. The new terms are defined on the page's own Terms section, as the card asks;
    `docs/glossary.md` is not in this card's scope and is unchanged.

### Open points for the owner

1. False resume perceptions have no committed count source (Decision 2): accept the shared helper and the
   golden's byte-equal re-render as what carries the cell, or ask for a per-observer perception record, a
   recording change beyond this card.
2. The reporter line, absolute or relative (diagnosis Part 4 item 2). This card only puts the numbers side by side.
3. The pre-registration named no ballot slot for "ballots citing a rebuttal" (Decision 4).
4. C5 was folded in beyond the three hardening items the dispatch named (Decision 1).

### Limitations

- The diagnosis's `s9` column (the former `samples/9p2i` baseline-9 bytes) is not reproducible at this head: those
  bytes are readable only at `d41c9006`. The baseline-9 era here is `ml_corpus/9p2i` plus the two 4p1i sets.
- Each round is one hosted recording of 50 games; round 1 and round 2 differ within the noise between recordings.
- The re-tallies hold every other ballot fixed. Real voters would have heard different speech.
- The holds-nothing label restates the voter's own statement about what it held; nothing checks it.
- Ballots citing a rebuttal read the turn citation as the cell (Decision 4); the counter slot is beside it.
- The 4p1i sets hold 36 report meetings each, so their per-seat rates are small-sample.
- Several cells are small: 14 held kills in round 2, 3 in round 1, 17 in the pooled baseline-9 era.

### Deviations

None outside the Expected scope. The follow-through in Decision 12 stays inside files this card owns.

### Review corrections, round 1 (2026-10-02)

One blocking finding from the integrity review of the pull request, repaired on top of `ecf51aa1`. `origin/main`
was still `5877adb4`, and no `audits/`, `replays/`, `docs/media` or `tests/fixtures/` byte moved, so the inventory
sentence and this card's row of `docs/artifacts.md` stand as derived. No production line changed.

**The finding.** Re-deriving the hand-built carriers for the tally identity (Decision 8) had weakened
`test_the_impostor_only_floor_reads_recorded_targets_on_either_side`. The ballot `3eb8cc5b` added, the second
impostor's for the ejected `p-2`, sat at 0.9, so a floor that read `authored_target` in place of the recorded
`target` still found an impostor-only floor and the test stayed green. The repair lowers that ballot to 0.1, below
the floor. The tally still ejects `p-2` (two ballots against one SKIP and one for `p-3`, one of the two at the
floor), and the floor reads only the rewritten ballot. Decision 8 now lists the carrier's old and new ballot; the
expected `(1, 1, 0)` is unchanged.

**The probe, green first and then red.** The probe makes the floor's filter read `ballot.authored_target`. It ran
against the three suites that read the cell (`tests/eval/test_gameplay_census.py`,
`tests/scripts/test_publish_gameplay_census.py`, `tests/meetings/test_ballot_arms.py`), with the module restored
from a copy after each run:
- against `ecf51aa1`'s test file: survived, 471 passed (the green the review found);
- against this head's: killed, 1 failed and 470 passed, the named test red.

**A bounded mutation pass over the span the finding names**: the `ejections_carried_only_by_impostor_ballots`
count in `_fold_ballots` (`eval/gameplay_census.py`). It used only the listed operator classes; 13 mutants, each
alone against the same three suites.

| id | class | mutant | result | red, or the reason |
|---|---|---|---|---|
| W01 | swap a collection for a related one | the filter reads `authored_target` | killed | `test_the_impostor_only_floor_reads_recorded_targets_on_either_side` |
| F02 | drop a filter | the confidence filter dropped | killed | 3 tests: `test_an_ejection_carried_only_by_impostor_ballots_reads_the_recorded_floor`, `test_the_impostor_only_floor_reads_only_confident_ballots_for_the_ejected`, `test_the_honesty_cells_count_the_scripted_ballots` |
| F03 | drop a filter | the ejected-target filter dropped | killed | 2 tests: both impostor-only floor tests |
| F04 | drop a wrapper | the `bool(confident)` guard dropped | equivalent | an ejection with no ballot at the floor for the ejected player is not a tally the game produces (rule 4 of `tally_ballots`), and the tally identity refuses it before the fold returns (Decision 8) |
| C05 | comparison to its inverse | `meeting.ejected is None` | killed | 8 tests, among them `test_the_committed_census_matches_a_recomputation` |
| C06 | comparison to its inverse | `ballot.target != meeting.ejected` | killed | 8 tests |
| C07 | comparison to its inverse | `ballot.confidence < meeting.ballot_floor` | killed | 3 tests |
| R08 | role read to a constant | every confident voter read as an impostor | killed | 5 tests |
| R09 | role read to a constant | no confident voter read as an impostor | killed | 4 tests |
| S10 | swap a collection for a related one | the voter list reads `ballot.target` | killed | 8 tests |
| S11 | swap a collection for a related one | the ballots read through the impostor-as-SKIP re-tally | killed | 4 tests |
| L12 | loaded source to the canonical literal | the recorded floor read as 0.6 | killed | `test_an_ejection_carried_only_by_impostor_ballots_reads_the_recorded_floor` |
| M13 | message argument to a constant | `where="x"` | equivalent | the cell carries no guard, so `_Accumulator.count` never formats `where` for it |

Green first: W01 alone, against `ecf51aa1`'s test file. Equivalent: F04 and M13, each for its reason. The script
and its copies lived in the session scratchpad.

**Validation at the fix commit**, each run to its end with its exit code captured directly:

| command | exit, and what it printed |
|---|---|
| `env \| grep -c '^AILIBI_'` | `0` |
| `uv run pytest` over the card's five suites, `-n 6 --dist loadfile` | 0: 581 passed |
| `uv run pytest tests/meetings/test_ballot_arms.py` | 0: 84 passed |
| `uv run ruff check` and `ruff format --check` on the test file | 0: clean, already formatted |
| `uv run python scripts/publish_gameplay_census.py --check` | 0: both files consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0: section `stage-b-r1/9p2i`, 50 games, 124 meetings; nothing written |
| `uv run python scripts/publish_process_scorecard.py --check` | 0: both scorecard files consistent; `git diff --stat main -- replays/ docs/process-scorecard.md docs/process-scorecard.json` empty |
| `uv run python -m eval.reporter_justice replays/samples/9p2i replays/ml_corpus/9p2i` | 0: per-slot reporter 17/114, innocent non-reporter 5/367, impostor 41/195; and 29/416, 2/1318, 210/597 |
| `uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `bash scripts/verify_samples.sh <dir>`, once per set: `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, round 1 | 0 each |
| `uv run python scripts/build_sample_report.py --check --sample-dir <dir>`, the same five sets | 0 each |
| `uv run pytest -m campaign -n 6` | 0: 337 passed |
| `uv run python scripts/validate_task_docs.py` | 0: 390 historical phase tasks and 390 prompts; 96 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 |
| demo bundle: `build_demo_bundle.py --out` at `5877adb4`, then at the fix commit `0b6fa67d`, in this one checkout; `diff -rq` | 0: the two bundles' 109 files are byte-identical; nothing ships |
| `bash scripts/check.sh` at the pushed head `45e5ec54`, run once, its exit code captured directly | 0: ruff and format clean (551 files), the four import-linter contracts kept, task docs valid, strict mypy clean (522 source files), 10,106 Python tests passed (20 skipped, 3 xfailed), frontend lint and type checks clean, 649 frontend tests passed (25 files), the frontend build green. The commit recording this changes only this row |

No frontend file changed, so `npm --prefix frontend test` and the e2e were not run.
