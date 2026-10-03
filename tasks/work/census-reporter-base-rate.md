# The reporter flag read beside its base rate

**Status:** ready

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

- [ ] **The per-seat cells.** Mechanism: one fold over report meetings (`trigger_kind == "report"`). It uses the
  existing vent-proof predicate (a vent-sighting flag naming a player alive at the open, as
  `meetings_with_vent_proof` reads it) and the reporter-first partition of `eval/reporter_justice.py`. It produces the
  nine cells (reporter, other crewmate, impostor, each in total, without vent proof and with it) and the two share
  cells, under one new heading. Planted: a hand-built carrier gives exact counts and turns red on each defect named
  here:
  - a role-first partition, shown by an impostor reporter in a self-report era;
  - a button meeting counted;
  - a dead player counted as a seat;
  - the ejected player's vent band used in place of the meeting's vent proof.
- [ ] **The base rate agrees with the scorecard's context.** Mechanism: a test compares the census's per-seat totals
  (without plus with vent proof) with `compute_reporter_justice` on each of the four committed sets. The fields are
  `reporter_slots`, `reporter_ejections`, `innocent_non_reporter_slots`, `innocent_non_reporter_ejections`,
  `impostor_slots` and `impostor_slot_ejections`. Perturbed: a carrier with one seat dropped from `living` breaks the
  equality. If the two seat definitions (living at the open, against ballot voters) ever differ on committed bytes,
  the test names the meeting, and Results reports it rather than loosening the test.
- [ ] **The kill-witness outcome table and cells.** Mechanism: the existing held-kill fold
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
- [ ] **The counterfactual tallies and the tally identity.** Mechanism: the fold calls `meetings.voting.tally_ballots`
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
- [ ] **The holds-nothing label.** Mechanism: a cell over every SKIP ballot, whatever the voter's role, counting
  `grounding_label == "none_held"`. A table gives every SKIP by label: the members of `BallotGroundingLabel`, read
  from the type with `typing.get_args` so no label is copied, plus `unlabelled` for a ballot recorded before the
  field. The definition says the label records the voter's own declaration, not a checked fact. Planted:
  - an unlabelled SKIP never lands in `none_held`;
  - a `none_held` EJECT is not counted;
  - a label outside the vocabulary raises.
- [ ] **Ballots citing a rebuttal.** Mechanism: the carrier keeps each ballot's `primary_reason_id` and
  `counter_reason_id`. Two cells, scoped to `bounded_rebuttal_version = 1`, count ballots whose turn citation names a
  rebuttal turn of the same meeting, and separately ballots whose counter slot does. Both are over ballots at meetings
  with a rebuttal. Planted:
  - a ballot citing the rebuttal speaker's first turn is not counted;
  - a ballot citing a rebuttal turn id from another meeting is not counted;
  - in the baseline-9 era both cells read n/a.
- [ ] **The regroup notice.** Mechanism: the loader keeps one boolean per recorded call with an agent id at a meeting
  after a regroup. The boolean says whether the prompt carries the notice of every earlier regroup in that game,
  formatted from the regroup's tick and room as the renderer formats them. No prompt text leaves the loader. The
  census holds the wording as its own constant, pinned equal to the renderer's. The cell counts prompts missing a
  notice, guarded by `meeting_reset = hub_with_grace`, so it reads 0 by construction and the fold raises on a
  breach. Planted, each red on its defect:
  - a prompt missing an earlier regroup's notice raises, naming the set, seed and meeting;
  - a prompt at a game's first meeting is outside the denominator;
  - a perturbed copy of the renderer's wording fails the pin (the sourced constant's source-change case).
- [ ] **The census stays a census.** Mechanism: tests over the published page and JSON.
  - The page names no envelope line and carries no ratio of two rates.
  - No new cell has a guard or scope that reads a role.
  - `docs/process-scorecard.md` and `.json` stay byte-identical (`publish_process_scorecard.py --check` green and
    `git diff` empty).
  - Planted: adding a relative-risk cell to the cell table turns the page test red.
- [ ] **Era grouping for every new cell.** Mechanism: the new cells pool only through the existing `pool()` and
  `census_from_inputs`. Planted:
  - a tally carrying round 1's era key pooled with one carrying the promoted era's raises `GameplayCensusEraError`
    before any new cell is summed;
  - each scoped cell reads n/a in an era without its setting, never 0.
  - Round 1 is read with `--set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` and is never pooled.
- [ ] **Properties.** Mechanism: Hypothesis over hand-built carriers. The generators reach impostor reporters (a
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
- [ ] **E3, `ERAS` held to the registry.** Mechanism: a helper in `eval/eras.py` returns the distinct eras a registry
  names, oldest first, and a test holds `ERAS` equal to it. Planted: `ERAS` without `STAGE_B_R2`, and a registry
  naming a third era, each turn it red.
- [ ] **C3, the counterfactual refusal by era identity.** Mechanism: `run()` resolves each named set to its directory
  under `replays/` and looks the directory up in the registry by resolved path. It refuses a registered set whose
  `era` is not `BASELINE_9`, naming that entry's era id. Planted:
  - `./samples/9p2i` and `samples//9p2i` are refused;
  - a monkeypatched registry holding a third era is refused with that era's id in the message.
  - An unregistered directory keeps today's path, as the existing sentinel test states.
- [ ] **`pool()` refuses what it cannot place.** Mechanism: `eval/process_scorecard.py` `pool()` raises when a source
  is not named by its registry, or when sources and tallies differ in number. Planted:
  - a candidate directory pooled with a baseline-9 set raises;
  - `sources=()` with two tallies raises.
  - The existing arithmetic tests pass a scratch registry naming their sources in one era. The pinned unregistered
    pass-through becomes the planted refusal, which strengthens the test.
- [ ] **C5, the census cooldown refusal's era id.** Mechanism: the message names the era its registry gives. Planted:
  a scratch registry with a second era holding two sets at different cooldowns raises with that era's id.
- [ ] **One bounded mutation pass.** Mechanism: a single pass over every production line this card adds or changes,
  using only the eight listed operator classes: F filter, S swap, N comparison, C constant for a role, kind, room or
  tick read, M message, T tuple member, B branch swap, L loaded source to literal. Each mutant runs alone against the
  touched suites, and Results lists it. A survivor is killed by a new test or named equivalent with its reason.
  Results also carries a per-line neuter table: each production line, the test that goes red when it is neutered.
- [ ] **Published and verified.** `publish_gameplay_census.py --check` is green on the regenerated page and JSON,
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

Not started.
