# The featured tour and spectator honesty on the promoted set

**Status:** done

## Outcome

Once the promotion card ([`promote-round-2`](promote-round-2.md)) lands, `replays/samples/9p2i` holds candidate
round 2's 50 games: the seven adopted arms, the kept vent exit and a kill cooldown of 6. The spectator's
curated surfaces still describe baseline-9 games that are no longer on disk. Every 9p2i card in the featured
strip makes a claim the new bytes falsify. The tour's head no longer opens on a grounded ejection. The three
public-results cases are pinned by sha to the old bytes and drop silently. The reading guide's exhibits narrate
meetings that no longer exist. The map draws the new game falsely in two places:
- it glides every player across the map at each regroup, which is really an instant gathering in the meeting
  room;
- it loses or truncates the vent trips a regroup closes, so an impostor inside a vent vanishes from the
  omniscient view.

This card is the opening analysis's spectator honesty pass, on the promoted bytes. When it is done:
- The strip is re-picked from `replays/samples` only. Each set's head is chosen by the measured criterion.
- The 9p2i row holds one vent game (the head), one impostor ejection with no vent evidence, and optionally one
  game whose ballots cite real evidence that points at an innocent player.
- Every label is true of its game and spoils nothing.
- The curated cases are re-derived on the new bytes, or withdrawn.
- The omniscient view gains three annotations: a reported corpse's age, the accused player's true route, and
  whether the accused opener got a reply. None of them can reach a crewmate's-eye view.
- The map shows the regroup and every vent trip as the engine recorded them.
- The e2e head-card guard runs green in both directions.

The pull request states, byte for byte, what the demo bundle changes. Its merge republishes the public demo,
the second of the wave's two publications after the promotion card's, so the merge is the owner's.

## Evidence

Every `path:line` below is at `d41c9006` (main, the merge of PR #494), labelled as such, and is re-anchored by
its named symbol at dispatch. Promotion had not happened at `d41c9006`, so every round-2 count below was
measured on `replays/candidates/stage-b-r2/9p2i`, the bytes the promotion card moves. They are counts only, with
no transcript or prompt text printed. At dispatch they are re-measured on `replays/samples/9p2i`, and the
dispatch figures govern.

**Rulings.** The owner, 2026-10-02, verbatim: "1. Merge 2. Promote and run the diagnostics." On 2026-09-24
the owner ruled "Tour fix can be deferred to after gameplay is finished" (ruling 11, decision memo
`tasks/decision-2026-09-24-stage-b-wave.md` section 0.1), and promotion now ends that deferral. Decision memo
section 1 ("What adoption means later", item 2(b) and item 8) lists the public-results and tour minimum. It also
lists the deferred viewer items: the `MapView.tsx` snap on a reset replay's first post-meeting frame, and the
`frontend/src/lib/bodies.ts` comment. The meeting-reset card, `tasks/work/meeting-reset-coherence.md`
("What stays out", at `d41c9006`), deferred both, plus a per-replay reset note, to adoption, because a viewer
change republishes on merge. `tasks/investigations-2026-09-24/partial_record.md` section 5, rows 13, 14
and 17, names this card's surfaces and the minimal truthful handling for each. Row 16 (the s9 digests in
`bodies.test.ts` and `contradictions.test.ts`) is the promotion card's; only the `bodies.test.ts` census leg
below is this card's. The scope is item A2 of the opening analysis memo, Part 3 (outside the repository, at
`~/.claude/projects/-Users-danielkeinan-projects-AiLibi/analysis-2026-09-24/analysis-memo.md`):
1. re-pick the tour from `replays/samples` only: a vent game, a non-vent impostor ejection chosen by a
   measured criterion, and optionally a game labelled wrong but believable;
2. add omniscient-only annotations for corpse age, the accused player's true route, and "the opener got no
   reply";
3. add planted tests: the no-reply note disappears when a rebuttal turn is added, and a fixture that leaks
   into a crewmate's view fails.

**The criterion, before and after.** `uv run python scripts/measure_featured_criterion.py --alternatives`
(at `d41c9006`), with `--parent replays/candidates/stage-b-r2` for the round-2 column:

| 9p2i | role-proof band | other-flag band | no-flag band | first meeting ejects on role proof | no flag, no ejection |
|---|---|---|---|---|---|
| baseline 9 (`samples`) | 70 ejections, 70 correct | 2, 1 | 18, 10 | 32 of 50 | seeds 2, 4, 10, 46 |
| round 2 (candidate) | 24, 24 | 2, 0 | 40, 20 | 11 of 50 | seeds 4, 15, 31, 36 |

On round 2 the `considered_alternatives` shape covers 691 ballots and 1,090 entries. 28 ballots list the voter
itself and 0 list the applied target. The 11 eligible openers on round 2 are seeds 3, 5, 6, 7, 10, 11, 19, 20,
27, 42 and 49. The script prints only the count; a scratch, count-only walk that reuses its
`opens_on_role_proof` named the seeds. `4p1i` does not move (19 of 50 eligible, head seed 2), so its three
cards stay true.

**The current 9p2i strip, read against round 2.** `FEATURED_GAMES` (`frontend/src/components/ReplayPicker.tsx:109-152`
at `d41c9006`) features 9p2i seeds 23, 0, 29 and 2. On round 2:
- **Seed 23** has 2 meetings and 14 turns. No meeting carries a flag, and the first ejects a crewmate, so it
  fails the head criterion (`tests/api/test_sets.py:511-545`, `:548-588`).
- **Seed 0** has 4 meetings and 26 turns, and its first meeting skips. The label claims three meetings and 21
  turns.
- **Seed 29** has one meeting, 8 turns and no flag. The label claims four meetings, vent sightings and
  contradictions.
- **Seed 2** has one meeting carrying two `cross_statement` flags. The label promises "no flagged
  contradictions".

Every 9p2i label check in `test_current_featured_claims_match_source_and_gate_bites` (`tests/api/test_sets.py:824-860`)
and the seed-0 shape test (`:695-729`) therefore fail on the promoted bytes.

**The holding edit this card replaces.** The promotion card cannot keep its gates green without touching these
surfaces, so at this card's base (that card's merge) they already read: a 9p2i strip of one criterion head
with a count-only label; `test_seed_7_isolates_the_role_proof_clause` and the seed-0 shape test deleted, and
`test_the_role_proof_clause_rejects_a_recategorised_head` landed on that head; the three cases withheld by
the source check, pinned as withheld in `tests/api/test_public_results.py`; `frontend/e2e/evidence-journey.ts`
flipped to the unscored 9p2i state, its case walks replaced by a no-case, no-source-link check, and its
evidence legs re-entered through the head's citation; the planted no-flags branch of `journey.spec.ts`
opening `4p1i` seed 11; the guide's exhibit paragraph naming the head and `4p1i` seed 11. The same card makes
`PublicResults.tsx`'s cases heading count-free and the no-rubric copy set-neutral. Its Results lists every
line, file by file; this card reads them there.

**Non-vent impostor ejections on round 2.** There are 20 impostor ejections outside the role-proof band, all
in the no-flag band. Seven of them are in a first meeting: seeds 8, 14, 17, 24, 34, 41 and 44. Two of those
games carry no flag anywhere and no vent event before their first meeting:
- **Seed 14:** one meeting, 8 turns, and no vent event in the whole game. Five EJECT ballots name the target,
  all from crewmates and all labelled `supported`, and three of them cite the voter's own observation.
- **Seed 44:** one meeting and 9 turns. Five EJECT ballots name the target, and four cite the voter's own
  observation.

Seeds 24 and 41 meet the criterion only without the vent clause. Seed 41's ballots include one `off_target`
label.

**Innocent ejections on round 2.** There are 22. Ten first meetings eject the opener, a reporter: seeds 9, 23,
28, 29, 33, 35, 39, 43, 46 and 48. The envelope flags this pattern: 17 of 114 report meetings eject the
reporter, above the 0.104 line (`audits/audit-2026-10-01-stage-b-r2.md` section 6.4). Featuring one is the
owner's call (analysis memo, Part 5 item 11). First-meeting ejections of a crewmate who is not the opener:
- seed 2, on two `alibi_vs_physical` flags;
- seeds 12, 13, 22 and 25, with no flag naming the target.

Scorecard row 8 (wrong but believable) counts ballots, not games. Its predicate,
`eval/process_scorecard.py:1466-1471` at `d41c9006`, is the measure for any such pick.

**The category clause has no committed isolating case on round 2.** The round-2 other-flag band holds two
ejections: seed 2 meeting 0 and seed 8 meeting 1, and both removed crewmates. Weakening the clause to "any
flag naming the ejected player" therefore lets them through to the role clause, which rejects them. 9p2i seed
7, the isolating case today (`tests/api/test_sets.py:675-692`), now ejects on role proof. So the clause's proof
must be a perturbed served replay, as `4p1i` already records it cannot supply one (`:646-652`).

**The curated cases.** `api/public_results.py` at `d41c9006` pins three cases to commit `9bae2b03` and to sha256
digests:
- `_SOURCE_ROOT` and the three `_SEED_*_SHA` constants are at `:35-41`;
- `_curated_cases` (`:45-93`) defines seed 23 meeting 0, seed 29 meeting 1 and seed 0 meeting 1;
- `_check_case` (`:96-327`) holds every sentence of each case with hand-written checks;
- the loop at `:489-495` skips a case whose recording sha differs (`continue`);
- `_source_url` (`:355-366`) returns a link only for the two baseline-9 set fingerprints, and builds the
  `4p1i` link as `_SOURCE_ROOT.replace("9p2i/", "4p1i/")` (`:362-366`); `build_demo_bundle.py` writes that link
  into `data/4p1i/eval/summary.json` (`source_url`), so moving the one root moves a `4p1i` byte.

So on the promoted bytes the cases vanish and the 9p2i source link becomes `None`. The demo bundle bakes a
case only if its game is featured (`scripts/build_demo_bundle.py:342-349`). Its test bakes a fixed seed list,
not the strip (`tests/scripts/test_build_demo_bundle.py:715-735`), so a case moved off the strip would vanish
from the demo with every test green. Round-2 meetings shaped like each case:
- **Supported:** emergency meetings opened by a crewmate who reports a vent sighting, with one role-proof flag,
  eject an impostor at seed 5 meeting 1, seed 37 meeting 1 and seed 39 meeting 1. Seed 39 also carries a weak
  flag.
- **Unsupported:** seed 2 meeting 0 ejects a crewmate on two `alibi_vs_physical` flags.
- **Unresolved:** seed 30 meeting 0 skips with one weak `alibi_vs_sighting` flag (6 SKIP ballots, 2 for
  crewmates), and so does seed 38 meeting 0.

At `d41c9006` the evidence e2e walks the old cases by title, tick and turn id
(`frontend/e2e/evidence-journey.ts:33-92`); the promotion card's holding edit replaces those walks.

**The map at a regroup.** The engine's regroup (`engine/meeting_reset.py:26-47`) moves every survivor to the
meeting room, clears `in_vent` and empties `bodies`. It emits no vent-exit event. The map pairs dives with exits
per actor in `buildVentSegments` (`frontend/src/components/MapView.tsx:186-227`), with two defects:
- a later dive overwrites an earlier unpaired one;
- a dive with no exit degrades to a one-tick pulse.

Omniscient tokens skip any player who is venting (`:641`), so for the rest of a closed trip the impostor is
absent from the map. On round 2's 140 dives (`gameplay_census` via `publish_gameplay_census.py --set-dir DIR
--json-stdout`):
- 72 end in an exit. 44 of those exits surface in the room they entered (scratch count). Their ticks inside
  are 1 tick 49, 2 ticks 3, 3 ticks 15, 4 ticks 5 (table `ticks_inside_per_trip`, which the scratch pairing
  reproduces exactly).
- 47 end at a regroup (`trips_closed_by_regroup`, 47 of 140).
- By subtraction, the remaining 21 end at a meeting with no regroup after it, or at the game's end.

Under the `d41c9006` rule, 22 dives get no segment at all and 46 get a one-tick pulse (scratch, count-only).

The single-step tween (`MapView.tsx:573-574`) animates the jump into the meeting room as travel. The comment
in `frontend/src/lib/bodies.ts:4-8` says the meeting deletes only the reported corpse, which is false under
the reset. The served bodies are already correct: the first post-meeting `TickView.bodies` is `()` under the
arm, as the meeting-reset card proved.

**The annotations' data, and their census twins.** All the data is already served:
- kill and `report_body` events;
- `agent_states[].room_id` and `is_venting`;
- each meeting's turns: speaker, `turn_kind`, `reply_to`, and accusation claims with `against`
  (`api/schemas.py:781-787`, `:820-848`).

No DTO field is needed. The census already counts the same facts on round 2:
- `corpse_age_at_report`, over 114 report meetings: 1 tick 19, 2 ticks 13, 3 ticks 33, 4 ticks 30, 5 ticks 6,
  6 ticks 6, 7 ticks 2, 8 ticks 2, 10 ticks 2, 11 ticks 1;
- `accused_opener_answers`, 87 of 105 (audit section 6.2).

The kill tick is the omniscient fact that the body-handle arm withholds from agents: 0 of 114 report openings
carry it (audit section 6.2).

**The viewer's gates.**
- The lens gates are `perspective.mode === "omniscient"` (`frontend/src/components/MeetingView.tsx:600`) and
  `BallotCard`'s `privateVisible`.
- Fog is tested end to end by "As-agent fog hides every omniscient-only fact"
  (`frontend/e2e/journey.spec.ts:796`).
- The copy gate's two legs (`frontend/src/lib/copy.test.ts`, `IN_SCOPE_SOURCES` at `:51-61`) bar dialect from
  `SPECTATOR_COPY` and from the listed component sources.
- The head-card guard reads the head's promise against the rendered flags (`journey.spec.ts:64`, `:475-482`).
  Its planted twin opens 9p2i seed 2 by name for the "no flags" branch (`:568-618`); the holding edit
  re-points it to `4p1i` seed 11.
- Reading-guide check 16 requires every seed the guide names to be featured, and at least two of them
  (`scripts/check_doc_facts.py:4783-4822`, `_MIN_EXHIBIT_SEEDS = 2` at `:590`). The guide's exhibits are
  at `docs/reading-guide.md:67-75`. It has 1,334 words against its 1,350 ceiling (`check_doc_facts.py:886-900`).

**The bundle.** `scripts/build_demo_bundle.py` bakes only the featured games, plus their picker metadata and the
summary. `.github/workflows/pages.yml` rebuilds and publishes it on every push to `main` (AGENTS.md:21-26).

## Acceptance

Each item names its enforcing mechanism and a planted or perturbed proof. Each new test is written first and
fails at this card's base for the stated reason; Results quotes that failing run. All user-facing copy goes
through `SPECTATOR_COPY` or the picker data. It carries no task or audit ID, no unexplained jargon and no
threshold arithmetic. A new component file joins `IN_SCOPE_SOURCES`.

- [x] Review correction (round 2): the singular corpse line's victim is pinned by two values. At `17abded4` the
  singular victim read as the constant p-3 passed, because the only singular case naming a victim reported p-3
  and the p-4 singular case asserted only "killed at tick 4, one tick before this meeting." That case now asserts
  the whole line, "The reported body is p-4's, killed at tick 4, one tick before this meeting." Mechanism:
  `frontend/src/components/MeetingView.test.tsx`, "names one tick in the singular". Proof: the mutant
  `victim: "p-3"` in the singular branch passes the `17abded4` suite (15 of 15) and fails now; with the other ten
  corpse-line mutants of the round, 11 of 11 are killed (Results, Review corrections, round 2).
- [x] Review correction (round 1): each tick fact of the supported case, and each case's meeting tick, is
  held by a planted case. Each of these is applied alone, every other fact as recorded: the turn's vent sighting
  retimed to tick 11; the cited reference's observation tick (11), scene tick (10), kind and subject; the
  recorded meeting moved one tick off each case (13, 30); each case's own `meeting_tick` moved off its meeting.
  Each withholds the case, and the unmoved replay passes. Mechanism: `tests/api/test_public_results.py`, the
  `_PERTURBATIONS` rows `venting-at-tick-12`, `the-vent-meeting-at-tick-12` and `the-weak-meeting-at-tick-31`,
  `test_each_fact_of_the_cited_observation_is_held_alone` and
  `test_a_case_naming_another_meeting_tick_withholds_publication`. Proof: the verifiers' four mutants (the
  turn's tick, the reference's observation and scene ticks read as constants, the meeting-tick check as a None
  test) and the reference's kind read as a constant pass the `c43b457b` suite and fail now (R-K1, R-K3, R-K4,
  R-N1 and R-K6 in Results, Review corrections, round 1).
- [x] Review correction (round 1): each argument of the omniscient corpse line is read off the recording. A DOM
  case reports p-3, not p-4: killed at tick 0, five ticks before its meeting, and killed at tick 2, one tick
  before a meeting at tick 3. A vent leg in Admin pins the route's room argument. Mechanism:
  `frontend/src/components/MeetingView.test.tsx`, "reads the victim, the kill tick and the age off the
  recording, in both forms" and "names the room of each vent leg off the recording". Proof: the plural
  victim, kill tick and age (the age is the verifiers' mutant), the singular victim and kill tick, and the vent
  room, each replaced by a constant, pass the `c43b457b` suite and fail now (M-M1 to M-M5 and M-M9). Review
  round 2 found one more: the singular victim read as p-3 still passed at `17abded4`, and the round-2 item above
  pins it (M-M13).
- [x] Review correction (round 1, the Codex P2 comment on PR 496): the map note speaks only of the meetings
  play resumes from. A meeting that ends its game is followed by no frame and no regroup, because
  `orchestrator/game.py` returns the game-over state before it regroups. 15 of the promoted set's 117 meetings
  end their game, among them the featured head's third. The note now reads "On this recording, whenever play
  resumes after a meeting, the survivors start from the meeting room with the bodies cleared, so the map jumps
  to where they stand on the next tick." The regroup item below is qualified to match. Mechanism:
  `frontend/src/lib/regroup.test.ts`, "the regroup note against the committed sets", over the committed
  skeleton; the copy pin in `copy.test.ts`; the e2e regroup-note test. Proof: the planted earlier wording
  throws ("claims every meeting, but 15 end"), and seed 19 meeting 2, at tick 44, has no later frame.
- [x] Review correction (round 1): the write-first counts are re-measured at the base, with the test-file
  revision and the command named. With the `646810c4` test files: Python 42 failed, 426 passed, 2 skipped;
  vitest 6 failed, with 3 files that cannot import; Playwright 8 failed, 6 passed, 3 skipped. With the
  `837c84d3` test files: Python 73 failed, 425 passed, 2 skipped; vitest 13 failed, with the same 3 files.
  Mechanism: the commands in Results, Review corrections, round 1. Proof: the earlier 44 and 8 reproduce from
  no committed revision, and they are corrected in place.
- [x] **The instrument names the candidates.** `scripts/measure_featured_criterion.py` gains `--list`. Per set
  it prints the seeds behind each count it already prints, plus two new lists:
  - the non-vent openers: games whose FIRST meeting ejects an impostor, with no flag anywhere in the game and
    no vent event at or before that meeting;
  - first meetings that eject a crewmate who is not the opener.

  It prints counts and seeds only. Mechanism: the script, run on `replays/samples`, quoted in Results.
  Proof, in `tests/scripts/test_measure_featured_criterion.py`: on the promoted bytes the lists equal the seeds
  above (re-measured at dispatch). Perturbed: a served replay with a vent event moved before the first meeting
  leaves the non-vent list, and one with the ejected role flipped leaves it too.
- [x] **The strip, re-picked on the promoted bytes.** `FEATURED_GAMES` keeps `4p1i` 2, 11 and 29 unchanged. Its
  9p2i row becomes:
  - **(a)** a head drawn from the eligible openers, its seed and reason named in Results. At authoring, seeds
    5, 6, 19, 20 and 27 show a look-and-wait stay of three ticks or more; of those, only seed 19 also has a
    dive a regroup closes, and seed 5's second meeting has the supported case's shape;
  - **(b)** one non-vent opener from the new list (seed 14 or 44 at authoring);
  - **(c)** optionally, one crewmate-ejecting first meeting from the new list, whose EJECT ballots row 8's
    predicate counts. That count is measured at dispatch and quoted.

  Membership beyond the head stays editorial, and the comment above `FEATURED_GAMES` says which picks are
  measured and by what. The role reads in these criteria (the head check's existing IMPOSTOR assert, and pick
  (b)'s impostor ejection) are curation: they describe the strip and gate no record, instrument or adoption,
  as the census states of its own role reads (`docs/gameplay-census.md:5`). Mechanism:
  `tests/api/test_sets.py`, which owns these checks:
  - `_assert_opens_on_role_proof` runs on every set's head;
  - a new `_assert_non_vent_opener` (re-implemented, not imported) runs on pick (b);
  - the seed-set pins are re-derived.

  Planted: the rejection parametrize the holding edit re-derived is extended on the promoted bytes, each case
  with its `match=`. Seed 23 (ejects a crewmate), seed 0 (first meeting skips) and seed 2 (other-flag crewmate
  ejection) are in it, plus non-vent rejections for seed 24 (vent before the meeting) and seed 8 (a later
  flag).
- [x] **The category clause, proved by perturbation, re-targeted.** No round-2 game isolates the `role_proof`
  comparison (Evidence), so the holding edit already deleted `test_seed_7_isolates_the_role_proof_clause` and
  landed `test_the_role_proof_clause_rejects_a_recategorised_head` on its holding head. This card re-targets
  that test to the head it picks and re-verifies it, rather than writing it first: it cannot fail at this
  card's base, so the write-first rule does not apply, and Results quotes its green run on the new head and
  its red run with the flag clause weakened. The test takes the head's served replay and recategorises its
  role-proof flag as `cross_statement`, every other field unchanged. It asserts that the criterion rejects the
  perturbed replay by the flag clause (`match=`), and that the weakened predicate (`ejected in flag.subjects`)
  accepts the same replay. The second assertion is what shows the perturbation isolates the clause.
- [x] **Every label is true and spoils nothing.** Each 9p2i label states only countable facts:
  - meetings and spoken turns, extending `_assert_featured_counts`' number vocabulary word by word;
  - a reported vent sighting;
  - "no flagged contradictions" for pick (b), whose game carries none.

  Each label also poses one question, and none names an ending, a player or a vote. Mechanism: the
  spoiler test (`test_sets.py:443-468`) and `test_current_featured_claims_match_source_and_gate_bites`,
  re-parametrized to the new pairs. Planted: each new label fails against its replay with its meetings
  removed, and each flag claim fails with only its flags stripped (the existing pattern, per pair).
  The seed-0 shape test is already gone (the holding edit deleted it with its card); Results confirms it is
  absent and nothing re-adds it. "Wrong but believable" is never on the strip,
  because it would spoil the game. If pick (c) is included, that framing appears only in its curated case's
  explanation, behind "Reveal case analysis (spoilers)", within the existing three classes. Adding a fourth
  classification would be a DTO change and is out of scope.
- [x] **The curated cases, re-derived or withdrawn, and always on the strip.** Each case in `_curated_cases`
  either is re-written on a promoted meeting that sits on a featured game, or is withdrawn. Each re-written case
  has:
  - a sha constant;
  - a `_check_case` branch holding every sentence of its setup and explanation against the served replay, the
    meeting memory and the recorded moves, as the baseline-9 re-curation did (commit `b064bcff`).

  Candidates are in Evidence. `_SOURCE_ROOT` is split in two: the 9p2i root is re-pointed to the promotion
  merge commit and `_source_url` is re-keyed to the promoted 9p2i fingerprint, while the `4p1i` root stays at
  `9bae2b03`, where its bytes are identical, so the `4p1i` link and `data/4p1i/eval/summary.json`'s
  `source_url` do not move. Mechanism: `tests/api/test_public_results.py`; this card owns its case assertions
  and the promotion card owns its summary counts. `PublicResults.tsx`'s cases heading is already count-free
  (the promotion card's), so keeping one or two cases renders no false count. Proof:
  - one planted perturbation per sentence family of each kept case, extending
    `test_a_case_sentence_the_recording_no_longer_shows_withholds_publication`;
  - the changed-source test (`:102-116`), kept;
  - a planted split-root test: the `4p1i` link built from the 9p2i root (the `d41c9006` rule) fails it;
  - a new test in `tests/scripts/test_build_demo_bundle.py` that bakes the strip's own `FEATURED_GAMES` and
    asserts that the baked summary carries every case `build_public_results` returns. Planted: a case pointed at
    an unfeatured game makes it fail.

  A withdrawn case is deleted with its check branch, sha and tests. Results states which were withdrawn and why.
  `frontend/e2e/evidence-journey.ts` replaces the holding edit's version: its case leg walks the kept cases,
  with their source link matching the promotion merge commit, and its evidence legs re-enter through a kept
  case or, if all three are withdrawn, keep the head's citation. Its 9p2i rubric leg stays the unscored state.
- [x] **Omniscient-only annotations.** A new pure module, `frontend/src/lib/annotations.ts`, derives three facts
  from the served replay:
  - **(1)** for a body meeting, the reported corpse's age: meeting tick minus the victim's kill tick;
  - **(2)** for each player an accusation in the meeting names, their recorded rooms from the last regroup
    (or tick 0) to the meeting tick, read from `agent_states`, with in-vent ticks named as such;
  - **(3)** whether the opener was accused by another speaker, and whether the opener then spoke again.

  `MeetingView` renders them only when `perspective.mode === "omniscient"`. Mechanism: the lens gate, plus
  vitest over a committed skeleton fixture: per frame the vent, kill and `report_body` events, rooms and
  `is_venting`; per meeting the turn skeletons with no free text. The fixture is bound by `corpusSha256`, as
  `frontend/src/lib/bodies.test.ts` binds its own. Proofs:
  - over promoted 9p2i, (1) reproduces the census table `corpse_age_at_report` and (3) reproduces the
    cell `accused_opener_answers` (114 meetings and 87 of 105 at authoring, re-measured at dispatch);
  - planted: the no-reply note appears on a meeting where the opener is accused with no second turn, and
    disappears when a rebuttal turn by the opener is added to the fixture;
  - planted: a route helper that reads the accused's spoken alibi instead of `agent_states` fails on seed 2
    meeting 0, where the two disagree;
  - planted leak: rendered under an agent lens, the DOM carries no corpse age, route or reply note. The same
    assertion helper applied to the omniscient render must throw, which proves the helper can fail;
  - the e2e fog test (`journey.spec.ts:796`) is extended to all three.
- [x] **The regroup, shown as it happens.** On a replay whose recorded `meeting_reset` is `hub_with_grace`, a
  single step onto the first frame after a meeting's close does not tween: tokens appear in the meeting room.
  Elsewhere a single step still tweens. A per-replay note in plain words says that each meeting the game
  outlives gathers the survivors in the meeting room and clears the bodies (qualified in review round 1). It shows on reset replays only; `4p1i` stays `preserve`
  and shows nothing new. The `bodies.ts` header comment is rewritten to say a regroup clears every corpse.
  Mechanism: a pure `isRegroupStep` in `frontend/src/lib/` that `MapView`'s `animate` reads. Proofs:
  - unit tests cover a reset step, a preserve step and a two-tick scrub;
  - planted: dropping the config check makes the preserve case snap or the reset case tween, so it fails;
  - a `bodies.test.ts` census leg confirms the rewritten comment: on promoted 9p2i no first post-regroup
    frame carries a body, while `4p1i` keeps unreported bodies across meetings. The retired accumulate rule
    stays the negative control and fails the new leg.
- [x] **Vent trips drawn as recorded, look-and-wait stays included.** Segment pairing moves to a pure
  `frontend/src/lib/vents.ts`. Rules:
  - every dive yields exactly one segment, and no later dive overwrites an earlier one;
  - a segment ends at its exit, or at the last frame where the served `is_venting` still holds for that actor.
    The second case is a regroup or the game's end, and draws an in-vent marker at the dive room with no
    emergence;
  - an in-place stay renders as a wait in its room for its whole window, with no travel.

  Mechanism: vitest over the skeleton fixture. Proof: on promoted 9p2i, the exit-ended windows reproduce
  `ticks_inside_per_trip` (49, 3, 15, 5), and the regroup-ended count reproduces `trips_closed_by_regroup` (47
  of 140). Planted: `MapView`'s `d41c9006` pairing rule, kept in the test as the retired control, fails the
  same census (22 dives without a segment, 46 one-tick pulses at authoring). A hand-built preserve trip that
  spans a meeting stays one segment.
- [x] **The e2e head-card guard, green in both directions.** The main leg (`journey.spec.ts:475-482`) takes the
  "has evidence" branch on the new head. The planted guard (`:568-618`) opens pick (b) by exact pill text in
  place of the holding edit's `4p1i` seed 11, and walks the "no flags" branch with both mismatches
  constructed against the real render.
  Mechanism: Playwright, run locally, because it sits outside `scripts/check.sh`. Proof: both branches are seen
  in the run, quoted in Results. Planted: pick (b)'s label with "no flagged contradictions" removed makes the
  guard's pairing assertion fail.
- [x] **The reading guide's exhibits follow the strip.** The paragraph at `docs/reading-guide.md:67-75` is
  rewritten in place, naming at least two featured promoted games and their meetings in countable terms.
  The sentence at `:62-65` stays true, and the rest of the page belongs to the promotion card. Mechanism:
  `check_doc_facts.py` check 16 and the 1,350-word ceiling. Planted: the paragraph naming seed 23, which the
  strip dropped, fails check 16. `wc -w` is quoted in Results.
- [x] **The bundle change, stated byte by byte.** `uv run python scripts/build_demo_bundle.py --out <scratch>/before`
  is run at the promotion merge commit, then `--out <scratch>/after` at this card's head, then
  `diff -rq <scratch>/before <scratch>/after`. Every changed path is listed in Results and in the pull request:
  the 9p2i replays added and removed by seed, `data/9p2i/eval/summary.json` (the cases), the picker metadata,
  and `assets/`. `data/4p1i/` must be identical, which the split source root keeps true. Perturbed, in scratch
  and reverted: reordering the `4p1i` entries shows `data/4p1i/` in the diff, which proves the diff can see it,
  and so does the `d41c9006` single-root rule (`data/4p1i/eval/summary.json`).

## Constraints

**Prerequisite and hand-off.** This card dispatches from `main` after the promotion card merges, and its PR
merges after it. The promotion card owns the bytes move, the instruments, the gates, the doc facts, the
artifacts rows, the candidate-directory rule and the re-pin sweep. That sweep includes the corpus digests in
`bodies.fixture.json` and `contradictions.fixture.json`, the summary counts in `test_public_results.py`, and
the rubric pins in `test_sets.py`. It also owns `PublicResults.tsx` whole, including the cases heading it
makes count-free (so this card can keep any number of cases), and the set-neutral no-rubric copy
(`copy.ts`'s `interestingnessAbsentLead`, `ReplayPicker.tsx`'s empty state and banner,
`ReplayPicker.test.tsx`, and the comments in `TournamentDashboard.tsx` and `GuidedTour.tsx`), which this card
leaves as written. This card owns:
- `ReplayPicker.tsx`'s strip and the featured and curated-case tests in `tests/api/test_sets.py`,
  `tests/api/test_public_results.py` and `tests/scripts/test_build_demo_bundle.py`;
- `api/public_results.py`'s curated cases, the split `_SOURCE_ROOT` and `_source_url`;
- the spectator annotations, the e2e head-card guard and `frontend/e2e/evidence-journey.ts`'s case leg;
- `scripts/measure_featured_criterion.py`, `MapView.tsx`, `bodies.ts` and the guide's exhibit paragraph.

Ownership is one writer at a time. The promotion card cannot keep its own gate green without some holding edit
here: every 9p2i label and the head criterion are falsified by the promoted bytes (Evidence). That holding edit
(Evidence, "The holding edit this card replaces") is listed line by line in the promotion card's Results;
this card reads it there and replaces it, including `frontend/e2e/evidence-journey.ts`, which it names in
Results as replaced. Files both cards write, in this order (the promotion card, then this card):
`frontend/src/components/ReplayPicker.tsx`, `tests/api/test_sets.py`, `tests/api/test_public_results.py`,
`frontend/e2e/journey.spec.ts`, `frontend/e2e/evidence-journey.ts`, `docs/reading-guide.md` (the exhibit
paragraph), `frontend/src/lib/copy.ts`, `frontend/src/lib/bodies.test.ts`,
`tests/scripts/test_build_demo_bundle.py`, `tests/scripts/test_measure_featured_criterion.py` and
`tasks/README.md`.

**Out of scope.**
- No byte under `replays/`, `audits/` or `tests/fixtures/` moves.
- No file under `engine/`, `agents/`, `meetings/`, `orchestrator/`, `llm/`, `eval/` or `training/` changes.
- No DTO, schema, loader mapping or generated type changes, and no new private field reaches any surface.
- No prompt family is touched, so no version bump; no lever, environment switch or experiment field is added.
- The ML corpus stays FROZEN, its artifacts keep their keys, and ML stays held (ruling 12).
- The candidate directories are the promotion card's to keep or retire; this card reads only `replays/samples`.
- No live provider call; the untracked `.env` is never read.
- No rendered prompt, transcript text or held-out seed band is printed; censuses are count-only.
- `frontend/src/components/PublicResults.tsx` belongs to the promotion card: its missing kill-cooldown label
  (round-2 audit section 1.11) and its cases heading, which that card makes count-free.
- The README's media stills and `frontend/e2e/media.spec.ts`'s hero (a baseline-9 seed-2 frame) are out of
  scope and named as a limitation.
- Copy uses tokens only (`frontend/CLAUDE.md`) and plain words: "regroup" is not user copy.
- Featuring a reporter-ejection game is the owner's call and is not taken here.

**Publication.** Every push to `main` rebuilds and republishes the demo (`.github/workflows/pages.yml`;
AGENTS.md:21-26). Two merges in this wave republish it: the promotion card's, then this card's, and each merge
is the owner's. This card's merge ends the interim public state the promotion leaves (one 9p2i card, no
curated cases, no 9p2i rubric); the 9p2i rubric stays absent after it. The pull request states the copy that
goes live and the bundle diff. Task completion authorizes no deployment beyond those two publications.

**Delivery.** The branch is `work/spectator-tour-round-2`, delivered as one pull request into `main` and merged by
merge commit or fast-forward, never squash. Each commit body ends with `Card: tasks/work/spectator-tour-round-2.md`
immediately followed by the line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Expected scope

- `frontend/src/components/ReplayPicker.tsx`: the strip, its labels and its criterion comment.
- `frontend/src/components/MapView.tsx`: it reads `vents.ts` and `isRegroupStep`.
- `frontend/src/components/MeetingView.tsx`, and `TurnCard.tsx` if the reply note sits on the turn.
- New modules `frontend/src/lib/annotations.ts`, `frontend/src/lib/vents.ts` and the regroup helper, with
  their tests and one committed skeleton fixture plus its regeneration recipe.
- `frontend/src/lib/bodies.ts` (the comment) and `bodies.test.ts` (the census leg).
- `frontend/src/lib/copy.ts` and `copy.test.ts`.
- `frontend/e2e/journey.spec.ts` and `frontend/e2e/evidence-journey.ts`.
- `api/public_results.py`.
- The tests named above in `tests/api/` and `tests/scripts/`.
- `scripts/measure_featured_criterion.py`.
- `docs/reading-guide.md` (the exhibit paragraph only).
- `tasks/README.md`'s inventory sentence, and this card.

Directly necessary follow-through within these files is permitted. A file outside this list is either the
promotion card's or needs the owner.

## Record impact

No recorded byte moves. `bash scripts/verify_samples.sh` and the four `build_sample_report.py --check` runs
recompute exactly what they recompute after the promotion merge. Nothing here is read back from a recording,
and no compatibility path is needed.

What changes is shipped viewer behaviour and the public payload: the landing game and the strip's labels, the
curated cases and their source link, three omniscient annotations, the regroup snap and the reset note, and the
vent-trip rendering. `4p1i` keeps its strip and its bytes, and its replays render as before, except that a dive
with no exit now holds its in-vent marker instead of a one-tick pulse. Each of these is a publication through
`pages.yml`, and the bundle diff bounds it. No agent reads anything new and no game plays out differently, so no evaluation
moves. At the next record that replaces `replays/samples/9p2i`, the criterion is re-run and the heads re-chosen,
which is why the pins assert criteria and not seeds alone.

## Validation

```
# development
uv run python scripts/measure_featured_criterion.py --alternatives --list
uv run pytest tests/api/test_sets.py tests/api/test_public_results.py tests/scripts/test_build_demo_bundle.py tests/scripts/test_measure_featured_criterion.py -q
cd frontend && npm run lint && npm run tsc:check && npm run test && npm run build
# nothing recorded moves
bash scripts/verify_samples.sh
uv run python scripts/build_sample_report.py --sample-dir <set> --check   # samples and ml_corpus, 9p2i and 4p1i
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run python scripts/verify_ml_evidence.py        # offline; never --complete
wc -w docs/reading-guide.md
# the browser legs, locally and serially (Playwright is outside check.sh)
cd frontend && npm run e2e
# the bundle diff, at the promotion merge commit and at this head, into scratch
uv run python scripts/build_demo_bundle.py --out <scratch>/before|after && diff -rq <scratch>/before <scratch>/after
# the full gate, whole, in a clean worktree, real exit code quoted
bash scripts/check.sh
```

Run `check.sh` to the end rather than to the first failure, because `set -e` masks later gates. Do not run a
live provider, the recorder, the held-out generator or any calibration as a check.

## Results

Done on `work/spectator-tour-round-2`, stacked on `work/promote-round-2` at `80d40422` (the promotion's PR #495,
open), by the orchestrator's ruling of 2026-10-02; the pull request says it must be retargeted to `main` after
#495 merges. Counts are count-only; no prompt, transcript or seed-band prefix was printed, and no live provider,
recorder or held-out generator ran.

**Commits**, in order: `dc0096db` the criterion's `--list`; `32c27446` the strip and its gates; `790f67d9` the
curated cases and the split source root; `1538ad5f` the map's vent trips and regroup snap, the omniscient
annotations and the skeleton fixture; `646810c4` the browser legs; `8d07a340` the answers to the neuter and
mutation passes; `ff79026f` the README media re-capture; `8a405d64` the strip comment's counts; `3a52c98f` the
head's reason at the strength the recording gives; `84fdb67d` these Results; `3a205c5e` the planted front
door's hunk; then the commit recording the `check.sh` run at `84fdb67d`.

**Sections relied on.** This card; the decision memo `tasks/decision-2026-09-24-stage-b-wave.md` sections 0.1
(ruling 11), 1 ("What adoption means later", items 2(b) and 8) and 7; `tasks/investigations-2026-09-24/partial_record.md`
section 5, rows 13, 14 and 17 (row 16 for the `bodies.test.ts` leg); `audits/audit-2026-10-01-stage-b-r2.md` sections
6 (6.2 for the census twins and the body handle, 6.4 for the reporter flag), 7 and 9; the promotion card's
Results ("The holding edit, file by file"); `docs/architecture.md`, "Layering" (api is a privileged post-game
reader; agent-lens controls constrain presentation) and "Determinism and the substrate ladder" (the shown set's
era).

### The instrument, the picks and the cases

`uv run python scripts/measure_featured_criterion.py --alternatives --list`, exit 0, on `replays/samples` at the
head (9p2i block; the 4p1i block reads 19 of 50 eligible, both new lists empty):

```
replays/samples/9p2i — 50 games
    role_proof flag   24 ejections  24 role-correct
    other flag         2 ejections   0 role-correct
    no flag           40 ejections  20 role-correct
  first meeting ejects on a role_proof flag: 11 of 50 games
  no flag and no ejection anywhere: seeds [4, 15, 31, 36]
    other flag ejections: 2:0 8:1
  first meeting ejects on a role_proof flag: seeds [3, 5, 6, 7, 10, 11, 19, 20, 27, 42, 49]
  first meeting ejects an impostor, no flag anywhere and no vent at or before it: seeds [14, 44]
  first meeting ejects a crewmate who did not open it: seeds [2, 12, 13, 22, 25]
     691 ballots  1090 recorded entries
```

(The band lines list every `seed:meeting`; quoted in the PR.) The lists equal the card's authoring seeds.

- **(a) Head: 9p2i seed 19.** Eligible (its first meeting, tick 12, ejects impostor p-6 on p-1's role-proof vent
  sighting). Of the eleven eligible openers, two record both vent behaviours the map now draws, a wait of three
  ticks or more inside a vent and a dive a regroup closes: seeds 6 and 19 (count-only walk; the card's authoring
  note named 19 alone, and seed 6's regroup-closed dive comes at its second meeting). Seed 19 shows both before
  its first meeting, the stretch the tour plays before it pauses (p-6 inside from Storage to Engineering, ticks 8
  to 11; p-9 diving at 10 and pulled out at the meeting at 12), and its first two meetings carry a supported and
  an unresolved case shape, so both kept cases sit on the landing game. Three meetings, nineteen turns.
  Re-measured at the head through `--list`. (Commit `32c27446`'s message says "the only one that also records
  both"; this paragraph is the correction, and the strip comment says "before its first meeting".)
- **(b) Second card: 9p2i seed 14**, of the two non-vent openers the one with no vent event anywhere in the game:
  one meeting, eight turns, no flag; five crewmate EJECT ballots name impostor p-1.
- **(c) omitted**, by the orchestrator's ruling (2): no crewmate-ejecting first meeting and no reporter ejection is
  featured; the wrong-but-believable framing appears nowhere, so row 8's count was not needed.
- Labels: "Three meetings, nineteen spoken turns, and a reported vent sighting. Which ballots rest on what their
  voter saw?" and "One meeting, eight spoken turns, and no flagged contradictions. What did each voter have to go
  on?". The 4p1i cards (2, 11, 29) are unchanged.
- **Kept cases**, both on seed 19 (sha256 `3c2f045f…bb28`): `witnessed-vent` (supported, meeting 0: a body report,
  then p-1's opt-in turn describing p-6 venting in Engineering, observation `p-1:12:1`, scene frame 11; p-1's
  ballot cites it; four other voters cite p-1's turn and vote p-6; role proof; p-6 ejected) and `weak-evidence`
  (unresolved, meeting 1: four speakers accuse the reporter p-1, no flag, p-1 replies with its own route, four
  skips each labelled "held nothing", one vote for p-1, no ejection). Every sentence is held by a `_check_case`
  clause. **Withdrawn**: `disputed-route`, with its branch, sha and tests: its game (seed 2 meeting 0's shape)
  is a crewmate-ejecting first meeting, which the ruling keeps off the strip, and no featured meeting ejects an
  innocent player on a disputed account.
- Source roots: the 9p2i root names `148fa211` (the commit that landed the promoted bytes; the promotion's merge
  commit did not exist yet, ruling (1)), keyed to the promoted fingerprint `sha256:ebb629f6…`; the 4p1i root stays
  at `9bae2b03` (its replays, manifest and roster are unchanged there; only its report later moved to `.json.gz`).

### The holding edit, replaced file by file

- `ReplayPicker.tsx`: the one-card 9p2i strip (seed 3) and its comment are replaced by seeds 19 and 14 and a
  comment naming which picks are measured and by what, and the curation clause.
- `tests/api/test_sets.py`: pins and planted seeds re-derived (seed 14 joins the head rejections);
  `_assert_non_vent_opener` added with its rejections (24 vent, 8 and 34 a later flag, 19 the head, 23 a
  crewmate, 0 a skip; the role clause and the vent boundary by perturbation); the category-clause test
  re-targeted to seed 19; the label checks re-parametrized pair by pair, plus a coverage pin and a one-question
  shape check. The seed-0 shape test stays absent (`git grep -n "seed_0\|seed-0 shape" tests/api/test_sets.py`
  finds nothing).
- `tests/api/test_public_results.py`: the withheld-case tests are replaced by per-sentence perturbations of the two
  kept cases, controls, the split-root test and the prose-facts test.
- `frontend/e2e/journey.spec.ts`: the planted guard opens 9p2i seed 14 by its exact pill (was 4p1i seed 11 via
  `?set=4p1i`); the fog test gains the meeting-record leg; a regroup-note test is added.
- `frontend/e2e/evidence-journey.ts`: **replaced**. It reads the published cases from the summary the app fetched,
  holds every card's and the set's source link to `148fa211` and 4p1i's to `9bae2b03`, opens the statement case
  on the reporter's reply, and re-enters the scene, fog, perspective and missing-reference legs through the
  supported case's cited observation. Both rubric legs keep the unscored state.
- `docs/reading-guide.md` exhibit paragraph: names 9p2i seeds 19 and 14 and 4p1i seed 11 in counts and the
  source-bound cases on the first 9-player card.
- `tests/scripts/test_build_demo_bundle.py`: the summary test bakes seed 19 and expects both cases; a new test bakes
  the strip's own `FEATURED_GAMES`.

**The category clause.** `uv run pytest tests/api/test_sets.py -k recategorised_head`: green, 1 passed. With the
flag clause weakened to `ejected in flag.subjects` in `_assert_opens_on_role_proof` (scratch edit, restored from a
copy): `Failed: DID NOT RAISE <class 'AssertionError'>`, 1 failed. The test also runs the weakened predicate on the
recategorised replay, which accepts it.

### The viewer

- `frontend/src/lib/vents.ts`: one trip per dive, ended by its exit or by the last frame whose served
  `is_venting` holds; shapes travel, stay and closed. Over promoted 9p2i (`vents.test.ts`): 140 dives, 0 without a
  trip; surfaced windows 1 tick 49, 2 ticks 3, 3 ticks 15, 4 ticks 5 (`ticks_inside_per_trip`); 47 closed by a
  regroup (`trips_closed_by_regroup`); the other 21 split 19 ejected inside a vent and 2 at the game's end. The
  retired `MapView` pairing, kept verbatim: 22 dives without a segment, 46 one-tick pulses. 4p1i: 44 dives, 0
  regroups. A preserve trip spanning a meeting stays one segment; a 500-schedule generated family recovers every
  trip.
- `frontend/src/lib/regroup.ts`: `isRegroupStep` / `shouldTween`, which `MapView`'s `animate` reads. The step
  between a meeting's frame and the next snaps on `hub_with_grace` in both directions; preserve, a config-less
  replay, a two-tick scrub and every other step behave as before; 102 regroup steps on 9p2i (one per meeting the
  game outlives), 0 on 4p1i. Measured: the first frame after a regroup already carries each survivor's first move
  (0 of 102 such frames have every survivor in the meeting room), so the snap lands on the meeting room or one
  corridor from it; the note's words say "the map jumps to where they stand on the next tick". The note shows on
  9p2i only (`journey.spec.ts`).
- `bodies.ts`'s header says a regroup clears every corpse; `bodies.test.ts`: 0 bodies served or drawn on the 102
  post-regroup frames (the retired accumulate rule paints 102 of 102); on 4p1i, 19 meetings outlived, one keeps
  an unreported body, and no reported body survives its meeting.
- `frontend/src/lib/annotations.ts` and `MeetingView`'s omniscient-only panel "What the recording shows". Over
  promoted 9p2i: corpse ages over 114 report meetings 1:19, 2:13, 3:33, 4:30, 5:6, 6:6, 7:2, 8:2, 10:2, 11:1
  (`corpse_age_at_report`); accused openers answered 87 of 105 (`accused_opener_answers`). The route reads
  `agent_states`; the spoken-alibi route fails on seed 2 meeting 0 for p-5 (and p-3), because a stated route is
  stamped on the players' clock, one tick ahead of the frames, which the panel's copy states.
- The skeleton fixture `frontend/src/lib/replay-skeleton.fixture.json` (structure only) is bound by
  `corpusSha256`; its recipe in `skeleton.testkit.ts` regenerated it byte for byte (sha256 `cb0ede3d…aa91`).

### Planted failures and the write-first runs

- The new tests at the base code (the base tree from `git archive 80d40422`, with the card's test files at
  `646810c4` laid over it; corrected in review round 1, which names the commands): Python 42 failed, 426 passed,
  2 skipped. The skips are two `test_check_doc_facts.py` cases that need full git history. The failures are
  counted by file, not attributed test by test: 27 in `test_public_results.py`, 6 in `test_sets.py`, 4 in
  `test_measure_featured_criterion.py`, 3 in `test_check_doc_facts.py` and 2 in `test_build_demo_bundle.py`.
  Examples: `('9p2i', 3) == ('9p2i', 19)`, `assert None == '…148fa211…/9p2i/'`, `module … has no attribute
  'opens_on_non_vent_impostor_ejection'`. Frontend: 6 failed (2 in `MapView.wiring.test.ts`, 4 in
  `MeetingView.test.tsx`), and 3 files cannot import, because `vents`, `regroup` and `annotations` are absent.
  Playwright: 8 failed, 6 passed, 3 skipped. Four failures are the evidence journey, the guard, the fog record
  and the regroup note. The other four are the static-bundle tests, whose bundle build stops when `tsc`
  type-checks the laid-over unit tests against the base. (This bullet first read 44 failed and 8 failed, which
  no committed revision reproduces.) Passing at the base by construction: the test-local criterion rejections and the `bodies.test.ts` leg
  (the shipped body rule already read the served rows; the leg proves the rewritten comment).
- Planted, each green now: the no-reply note appears without the opener's rebuttal and leaves when it is added
  (lib and DOM); the leak helper passes every agent lens and throws on the omniscient render; the config-blind
  regroup rule fails the preserve step; the retired rules fail the vent and body censuses; the label with "no
  flagged contradictions" removed and the promise over evidence both throw in the guard; the seed-23 exhibit fails
  check 16; a case moved to an unfeatured game fails the strip-bakes-every-case test; the single-root rule fails the
  split-root test.

### The neuter pass and the mutation pass

Every production line, row and argument this card adds or changes, neutered alone (237 probes: criterion 37,
cases 72, strip 7, viewer 121), its suite run, the file restored from a copy and its sha256 checked. First run:
224 killed, 13 came back green: N-C13 (`listing` default), N-C33 (`--list` renamed; argparse prefix match), N-P53
(accusation target), N-V07, N-V13, N-V20 (window's first tick), N-R04 (step size), N-A05, N-A06, N-M18 (heading
text), N-K11 (`MAP_COPY`), N-W16, N-W17 (traveller key). Answered in `8d07a340`: the default deleted, the usage
line pinned, an isolating perturbation, a redundant guard and a redundant type check deleted, tests for the
window's first tick, a two-tick scrub from the meeting, a vent before the report, the heading text, the map
note's words and the key. Re-probed: all killed except four equivalent: N-C13b (no caller relies on a default),
N-V07 (the dive's initializer is overwritten on the same frame), N-A07c (only kill events carry `victim_id`),
N-W16 (the fog branch never reads the trip map).

One bounded mutation pass, exactly the eight listed classes, 68 mutants over `scripts/measure_featured_criterion.py`,
`api/public_results.py`, `ReplayPicker.tsx`, `vents.ts`, `regroup.ts`, `annotations.ts`, `MeetingView.tsx` and
`MapView.tsx` (F drop a filter 8, S swap a collection 7, N None test 14, K read to constant 14, M message argument
10, T drop a tuple member 2, B swap branches 7, L loaded source to literal 6). First run: 55 killed, 11 came back
green (F4, K14, M1-M8, M10), 2 spans not applied (S8, N1). After the message-text and opener tests: 67 killed;
F4 is equivalent (deleting the current entry while iterating a JS `Map` is safe; the copy is defensive). The full
tables are in the PR. That count holds of those 68 mutants only, not of every mutant of the eight classes over
these spans. Review round 1 found five more that survived in `api/public_results.py` and `MeetingView.tsx`;
they are killed in Review corrections, round 1.

### The bundle

`build_demo_bundle.py --out` at `80d40422` (the stacked promotion head, standing in for the merge commit, ruling
(1)) and at the head, `diff -rq`: `data/9p2i/replays/headless-seed-3*` removed, `headless-seed-14*` and
`headless-seed-19*` added (with beliefs, meetings and memory); `data/9p2i/replays.json` (seeds [3] to [14, 19]);
`data/9p2i/eval/summary.json` (`cases` [] to the two cases, `source_url` null to the `148fa211` root; every count
identical); `README.md` ("Games: 4" to "Games: 5"); `index.html` and the hashed `assets/` (`index`, `MapView`,
`ReplayPicker`, `TournamentDashboard`, the three Pixi renderer chunks, `index-*.css`). `data/4p1i/`: `eval/summary.json`
and `sets.json` and every meeting, memory and belief file byte-identical; the three replay files and
`replays.json` differ only in `created_at` (each checkout's file mtime). Perturbed, in scratch copies: reordering
the 4p1i entries changes only the `ReplayPicker` asset (the bake is seed-sorted, so `data/4p1i/` keeps its
content); swapping 4p1i seed 11 for 12 shows `data/4p1i/replays/headless-seed-11*` removed and `-12*` added; the
`d41c9006` single-root rule shows `data/4p1i/eval/summary.json` differing.

### The README media (scope extension, ruling 4)

Re-captured with `AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts` (3 passed) from the bundle built at
`8d07a340`: the hero is seed 19 tick 9 (two bodies, both impostors on the map, one inside the vents; fog subject
p-5 in Labs sees one player and no body, then accuses crewmate p-4 at tick 12), every fact asserted against the
baked bytes. A second capture gave byte-identical stills and GIF; the clip differs run to run (as documented), and
the second run's clip ships. `provenance.json` names the served recording (its sha256 is held to the served bytes
by `test_public_recording_provenance.py`, with a moved digest planted to fail); `docs/media/README.md`, the README
caption and samples sentence, and the `docs/artifacts.md` media row (1.6 MB / 7 files) follow. The media are not
part of the demo bundle.

### Validation

| command | result |
|---|---|
| `measure_featured_criterion.py --alternatives --list` | 0 |
| `pytest tests/api/test_sets.py tests/api/test_public_results.py tests/scripts/test_build_demo_bundle.py tests/scripts/test_measure_featured_criterion.py tests/scripts/test_public_recording_provenance.py -n 6` | 0: 176 passed |
| `npm run lint`, `tsc:check`, `test`, `build` (frontend) | 0; 0; 0: 25 files, 645 tests; 0 |
| `verify_samples.sh` bare; `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i` | 0 (50 clean); 0 each (50, 50, 150, 50, 50) |
| `build_sample_report.py --check`, the five sets | 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `check_doc_facts.py`; `validate_task_docs.py` | 0; 0 |
| `verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `pytest -m campaign -n 6` | 0: 337 passed |
| `wc -w` | README 1,569 of 1,600; reading guide 1,338 of 1,350 |
| `npm run e2e` (local, serial, `CI=1`) | 0: 14 passed, 3 skipped (the media spec's) |
| bundle diff | above |
| `bash scripts/check.sh` at `84fdb67d` | 1: 1 failed, 10,031 passed, 20 skipped, 3 xfailed; the failure was `test_the_d41c9006_front_door_fails_on_the_promoted_tree`, whose planted hunk still carried the README samples sentence the media re-capture replaced; `3a205c5e` follows it (`test_check_doc_facts.py` 325 passed) |
| `bash scripts/check.sh`, once at the final pushed head | in the PR body (a card cannot carry the run of the commit that writes it) |

### Decisions

1. The 9p2i source root names `148fa211`, the commit that landed the promoted bytes, which `main` will contain
   after a merge-commit merge; the 4p1i root stays at `9bae2b03`; the bundle's before tree is `80d40422`
   (orchestrator ruling 1).
2. No reporter-ejection game and no crewmate-ejecting first meeting is featured; pick (c) is omitted and the
   wrong-but-believable framing appears nowhere (ruling 2).
3. The head is seed 19 for the reason above, measured at the head. The owner's diagnosis memo of 2026-10-02 has no
   committed copy, so it was not read; the orchestrator relayed its advice (seeds 7 or 19 as the opener, a strip
   of 1, 6, 0 and 3). Seed 19 is eligible and agrees with it; seed 7 is eligible but records no wait of three
   ticks or more inside a vent; the advised strip was not taken, since seeds 1 and 0 open on a skip and the
   card's second card must be a non-vent opener (ruling 3).
4. The curated cases keep two of three; `disputed-route` is withdrawn, and the per-sentence planted coverage is
   restored for both kept cases (ruling 5).
5. The README media were re-captured (ruling 4).
6. `PublicResults.tsx`, `copy.ts`'s `interestingnessAbsentLead`, the no-rubric empty state and banner are left as
   the promotion card wrote them (ruling 6); the 9p2i rubric leg stays the unscored state.
7. Annotations render only in the omniscient lens and only on a replay that carries frames (an isolated meeting
   fixture has none); the route window opens on the frame after the last regroup, and its ticks are the map's.
8. The regroup snaps in both directions of the step across it; the note shows in both lenses (it is a rule the
   players are told too).
9. Every trip with no exit is drawn held at the in-vent size until its last venting frame, and a stay is drawn
   held, coming up full size on its exit tick.
10. `skeleton.testkit.ts` holds the fixture reader and its recipe, shared by four test files.

### Limitations

- `MapView`'s canvas wiring (the tween decision, the trip poses, the traveller size) is pinned on its source by
  `MapView.wiring.test.ts` and in behaviour by the lib tests; no browser test reads pixels off the canvas.
- The reporter flag the promoted set carries (17/114, record 9.2) is untouched here; the strip features no
  reporter ejection.
- Four neuter probes and one mutant are equivalent (above).
- Reordering the 4p1i entries is invisible in `data/4p1i/` because the bake is seed-sorted; the diff's sight of
  that directory is shown by the seed swap and the single-root rule instead.
- Defects noted, not fixed, for the follow-up card `rubric-extractor-era` (owned elsewhere): `PublicResults.tsx`'s
  behaviour list still calls the adopted arms "experimental", which is literally true of the recorded config but
  reads as unadopted.
- The base runs used a git-less archive of `80d40422`.
- On macOS the evolution-strategy hash pin is Linux-only; CI is cited for it if `check.sh` reports it.

### Deviations

Files outside Expected scope, each directly necessary: `tests/scripts/test_check_doc_facts.py` (check 16's planted
tests name the guide's new exhibits); `frontend/src/components/PrivateReasoning.test.tsx` (its isolated meeting
fixture gains `ticks: []`); `frontend/src/components/MeetingView.test.tsx`, `MapView.wiring.test.ts` and
`frontend/src/lib/skeleton.testkit.ts` (new test files). Ruling 4's extension: `README.md` (caption and samples
sentence), `docs/media/*`, `frontend/e2e/media.spec.ts`, `tests/scripts/test_public_recording_provenance.py`
(the placement phrase "Archive only"), and the `docs/artifacts.md` media row.

### Review corrections, round 1 (2026-10-02)

A fix round from `c43b457b` on four verifier findings, one of them the Codex P2 comment on PR 496. Commits:
`a4242ae4` (the case tick facts and the corpse line's arguments), `837c84d3` (the map note), then the commit
that records this subsection. The changed files are `tests/api/test_public_results.py`,
`frontend/src/components/MeetingView.test.tsx`, `frontend/src/lib/copy.ts`, `copy.test.ts`, `regroup.ts` (one
doc comment), `regroup.test.ts`, `frontend/e2e/journey.spec.ts` and this card. The only production change is
the map note's wording. No recorded byte, fixture, DTO, audit row or front-door page moves. The promotion branch
had not moved: `origin/work/promote-round-2` is still `2087821e`, which this branch already merged, so nothing
was merged.

**Finding 1: the case tick facts.** At `c43b457b`, four listed-class mutants of `_check_case` passed the case
suite: the turn's sighting tick, the reference's observation tick and scene tick each read as a constant, and
the meeting-tick check replaced by a None test. No planted case moved those facts. Now each moves alone, every
other fact as recorded:
- `_PERTURBATIONS` gains `venting-at-tick-12` (the turn's `saw_vent` at tick 11), `the-vent-meeting-at-tick-12`
  (meeting 0 at tick 13) and `the-weak-meeting-at-tick-31` (meeting 1 at tick 30);
- `test_each_fact_of_the_cited_observation_is_held_alone` moves the cited reference's observation tick (11),
  scene tick (10), kind and subject, one per case, and first asserts the recorded values (`saw_vent`, p-6, 12, 11);
- `test_a_case_naming_another_meeting_tick_withholds_publication` moves each case's own `meeting_tick` (13, 30).

Each withholds the case by name, and the unmoved replay passes. `tests/api/test_public_results.py`: 64 passed at
`c43b457b`, 73 now.

**Finding 2: the corpse line's arguments.** Both corpse tests at `c43b457b` reported p-4. The plural one had age
3 and kill tick 2, and the singular one kill tick 4, so an argument replaced by those values passed. The new DOM
case "reads the victim, the kill tick and the age off the recording, in both forms" reports p-3. In one render
p-3 is killed at tick 0 and reported at tick 5 ("killed at tick 0, 5 ticks before this meeting"). In the other
it is killed at tick 2 and reported at tick 3 ("killed at tick 2, one tick before this meeting"). Neither render
names p-4. "Names the room of each vent leg off the recording" adds a vent leg in Admin. The bounded pass found
that the room argument read as "Labs" passed too. `MeetingView.test.tsx`: 13 passed at `c43b457b`, 15 now.
Review round 2 found that the singular victim read as p-3 still passed at `17abded4`, because the p-4 singular
case asserted no victim; Review corrections, round 2 pins it.

**Finding 3: the map note (the Codex P2 comment, valid).** `orchestrator/game.py` returns the game-over state
before `regroup_after_meeting`. So a meeting that ends its game is followed by no frame and no gathering, and no
bodies are cleared. Over the committed skeleton, the promoted 9p2i has 117 meetings: 102 are outlived by their
game and 15 end it. The featured head's third meeting (seed 19 meeting 2, tick 44) is one of the 15: tick 44 is
its last frame. The note said every meeting ends with the survivors gathered. It now reads: "On this recording,
whenever play resumes after a meeting, the survivors start from the meeting room with the bodies cleared, so the
map jumps to where they stand on the next tick." `regroup.test.ts` adds "the regroup note against the committed
sets". It counts the 15 game-ending meetings and shows that seed 19 meeting 2 has no later frame. It holds the
note to the meetings play resumes from, and the note's first wording, planted, throws ("claims every meeting,
but 15 end"). The copy pin in `copy.test.ts`, the e2e substring and the comments in `copy.ts`, `regroup.ts`,
`regroup.test.ts` and `journey.spec.ts` follow it. The regroup Acceptance item is qualified to match.
`git grep -n "every meeting ends\|survivors gathered"` now finds only the planted wording in `regroup.test.ts`.
The note still shows for the whole replay, and on 9p2i only.

**Finding 4: the write-first counts, re-run.** Both base trees are git-less extractions of `80d40422`. Each has
the card's test files at one revision laid over it:

```
git archive --format=tar -o <scratch>/base80.tar 80d40422           # extracted into one tree per revision
git show <rev>:<path> > <tree>/<path>                                 # rev 646810c4 or 837c84d3, each file below
uv run --directory <tree> --frozen pytest tests/api/test_sets.py tests/api/test_public_results.py \
  tests/scripts/test_build_demo_bundle.py tests/scripts/test_check_doc_facts.py \
  tests/scripts/test_measure_featured_criterion.py -q -p no:cacheprovider -n 6 -rfEs
cd <tree>/frontend && npx vitest run                                  # node_modules linked; package files identical
cd <tree>/frontend && CI=1 npx playwright test                        # the 646810c4 tree
```

The laid-over files are the five Python files above, plus these frontend files: `MapView.wiring.test.ts`,
`MeetingView.test.tsx`, `PrivateReasoning.test.tsx`, `annotations.test.ts`, `bodies.test.ts`, `copy.test.ts`,
`regroup.test.ts`, `vents.test.ts`, `skeleton.testkit.ts`, `replay-skeleton.fixture.json`, `e2e/journey.spec.ts`
and `e2e/evidence-journey.ts`.

| test files at | Python | vitest | Playwright |
|---|---|---|---|
| `646810c4` | 42 failed, 426 passed, 2 skipped; by file 27 public results, 6 sets, 4 criterion, 3 doc facts, 2 bundle | 6 failed, 583 passed; 3 files cannot import | 8 failed, 6 passed, 3 skipped |
| `837c84d3` | 73 failed, 425 passed, 2 skipped; by file 55, 6, 6, 4, 2 | 13 failed, 589 passed; the same 3 files | not run |

Notes on the table:
- The two skips are `test_check_doc_facts.py:4959` and `:4998`, which need full git history to resolve a pull
  request.
- The three files that cannot import are `annotations`, `regroup` and `vents`, whose modules the base lacks.
- Four Playwright failures are the evidence journey, the guard, the fog record and the regroup note. The other
  four are the static-bundle tests, whose build stops when `tsc` type-checks the laid-over unit tests against the
  base.
- `837c84d3`'s e2e files differ from `646810c4`'s only in the regroup-note substring and its comment, so the
  Playwright leg was not re-run on that tree.

The earlier "44 failed" and "8 failed" reproduce from no committed revision. They are corrected in place above,
and the claim that each failure is a new card test is dropped: the failures are counted by file.

**The bounded mutation pass.** The pass covers the spans this round changes and the spans the findings name,
using only the listed classes. That is 28 mutants: 14 in `api/public_results.py` and 14 in `MeetingView.tsx`.
Three neuter probes of the note's line are added. Each was applied alone, its suite run, and the file restored from
a copy with its sha256 checked. The suites are `pytest tests/api/test_public_results.py -x` and `vitest` on
`MeetingView.test.tsx`, or on `regroup.test.ts`, `copy.test.ts` and `MapView.wiring.test.ts` for the note.

First run, with the first version of the corpse case: 28 killed and 3 green (R-K6, M-M5 and M-M9). The kind and
subject projections, the second corpse meeting and the Admin vent leg answer them. Now: 31 of 31 killed. That
holds of those 31 only: review round 2 adds M-M13 to the table, which passed at `17abded4` and is killed from
the round-2 head (Review corrections, round 2). With the
`c43b457b` test files swapped in (and restored, sha256 checked), R-K1, R-K3, R-K4, R-N1, R-K6, M-M1 to M-M5 and
M-M9 all pass. Those are the verifiers' four mutants and the seven that the earlier cases' values hid.

| id | file | mutant (old → new) | first run | now |
|---|---|---|---|---|
| R-K1 | `public_results.py` | `(o.subject, o.room, o.tick)` → `(o.subject, o.room, 12)` | killed | killed |
| R-K2 | `public_results.py` | `o.room` in the turn check → `"ENGINEERING"` | killed | killed |
| R-K3 | `public_results.py` | `observation.observation_tick` → `12` | killed | killed |
| R-K4 | `public_results.py` | `observation.scene_tick` → `11` | killed | killed |
| R-K5 | `public_results.py` | `observation.room` → `"ENGINEERING"` | killed | killed |
| R-K6 | `public_results.py` | `observation.kind` → `"saw_vent"` | green | killed |
| R-K7 | `public_results.py` | `meeting.tick` in the meeting check → `12` | killed | killed |
| R-K8 | `public_results.py` | `case.meeting_tick` in the meeting check → `12` | killed | killed |
| R-N1 | `public_results.py` | `meeting.tick != case.meeting_tick` → `meeting.tick is None` | killed | killed |
| R-N2 | `public_results.py` | `meeting.tick != case.meeting_tick` → `==` | killed | killed |
| R-N3 | `public_results.py` | `case_turn is None` → `is not None` | killed | killed |
| R-N4 | `public_results.py` | `observation is None` → `is not None` | killed | killed |
| R-F1 | `public_results.py` | the `SawVentObservationView` filter on the turn's observations dropped | killed | killed |
| R-B1 | `public_results.py` | the reference tuple's `!=` → `==` | killed | killed |
| M-M1 | `MeetingView.tsx` | plural `victim` → `"p-4"` | killed | killed |
| M-M2 | `MeetingView.tsx` | plural `killTick` → `"2"` | killed | killed |
| M-M3 | `MeetingView.tsx` | plural `age` → `"3"` | killed | killed |
| M-M4 | `MeetingView.tsx` | singular `victim` → `"p-4"` | killed | killed |
| M-M5 | `MeetingView.tsx` | singular `killTick` → `"4"` | green | killed |
| M-M6 | `MeetingView.tsx` | `opener` → `"p-1"` | killed | killed |
| M-M7 | `MeetingView.tsx` | `accuser` → `"p-2"` | killed | killed |
| M-M8 | `MeetingView.tsx` | routes lead `from` → `"0"` | killed | killed |
| M-M9 | `MeetingView.tsx` | vent leg `room` → `"Labs"` | green | killed |
| M-M10 | `MeetingView.tsx` | one-tick span `tick` → `"5"` | killed | killed |
| M-M11 | `MeetingView.tsx` | span `from` → `"0"` | killed | killed |
| M-M12 | `MeetingView.tsx` | span `to` → `"2"` | killed | killed |
| M-M13 | `MeetingView.tsx` | singular `victim` → `"p-3"` (added in review round 2) | not run | green at `17abded4`; killed in review round 2 |
| M-N1 | `MeetingView.tsx` | `corpse.age === 1` → `!== 1` | killed | killed |
| M-B1 | `MeetingView.tsx` | the answered and unanswered branches swapped | killed | killed |
| N-K13 | `copy.ts` | the note's line → its first wording | killed | killed |
| N-K14 | `copy.ts` | the note's line → `""` | killed | killed |
| N-W15b | `MapView.tsx` | `{MAP_COPY.regroupNote}` → `{""}` | killed | killed |

The "killed" entries for R-K7, R-K8, R-N2, R-N3, R-N4 and R-B1 are errors in the module's summary fixture: the
real head summary is refused by name, which is a red suite.

**Validation at `837c84d3`.** Nothing these commands read moved except the copy, the tests and this card.

| command | result |
|---|---|
| `measure_featured_criterion.py --alternatives --list` | 0; the lists are unchanged |
| `pytest tests/api/test_sets.py tests/api/test_public_results.py tests/scripts/test_build_demo_bundle.py tests/scripts/test_measure_featured_criterion.py tests/scripts/test_public_recording_provenance.py tests/scripts/test_check_doc_facts.py -n 6` | 0: 510 passed |
| `npm run lint`, `tsc:check`, `test`, `build` (frontend) | 0; 0; 0: 25 files, 649 tests; 0 |
| `verify_samples.sh` bare; `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i` | 0 (50 clean); 0 each (50, 50, 150, 50, 50) |
| `build_sample_report.py --check`, the five sets | 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `check_doc_facts.py`; `validate_task_docs.py` | 0; 0, re-run after this subsection |
| `verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `pytest -m campaign -n 6` | 0: 337 passed, re-run after this subsection |
| `npm run e2e` (local, serial, `CI=1`) | 0: 14 passed, 3 skipped (the media spec's) |
| bundle diff, `80d40422` against `837c84d3` | the same paths as "The bundle" above |
| `bash scripts/check.sh`, once at the final pushed head | in the PR body |

For the bundle diff, both bundles were rebuilt into scratch. In `data/4p1i/`, the three replay files and
`replays.json` differ only in `created_at`, and `eval/summary.json` is byte-identical. The 9p2i summary differs
only in `cases` and `source_url`. The note's new words ship in `assets/index-*.js`, one of the hashed chunks
already listed.

**Decisions.**
1. The Codex P2 comment is valid and is answered as a finding. The note is qualified rather than hidden on
   game-ending meetings, because it is a rule of the recording, not of one frame.
2. The regroup Acceptance item and the earlier Results paragraphs (the write-first bullet, the 67-killed claim)
   are corrected in place, each with a note, so no false number or wording stays live.
3. The write-first legs are reported at two test revisions: `646810c4`, the one the first claim describes, and
   `837c84d3`, this round's tests.

**Limitations.**
- The Playwright leg over the base ran with the `646810c4` e2e files only. The static-bundle failures there come
  from the experiment's set-up, not from the specs.
- The mutation pass is bounded to the spans above. A survivor of another class or span is outside it.

### Review corrections, round 2 (2026-10-02)

A fix round from `17abded4` on one verifier finding (the docs lens). The other three round-1 repairs were not
reopened. Commits: `d16acc9c` (the assertion), then the commit that records this subsection, then one that
records the gate. The changed files are `frontend/src/components/MeetingView.test.tsx` (one assertion) and this card. No
production line, recorded byte, fixture, DTO, audit row, front-door page or bundle input moves:
`git diff --stat 17abded4` lists those two files only, and nothing imports a `*.test.tsx` file into the build.
The promotion branch had not moved: `origin/work/promote-round-2` is still `2087821e`, which this branch already
merged, so nothing was merged.

**The gate at `17abded4`.** Round 1's worker ended its turn before `check.sh` finished, so the orchestrator ran
`bash scripts/check.sh` in that worker's worktree at `17abded4`: exit 0, 10,045 passed, 20 skipped, 3 xfailed;
vitest 25 files, 649 tests. Those numbers are as the orchestrator relayed them; the log is in its scratchpad, not
committed. The PR body's row for that run says so. This round's own run is in the Validation table below.

**Finding: the singular corpse line's victim.** At `17abded4`, `victim: corpse.victimId` in the
`corpseAgeOneTick` branch of `MeetingView.tsx`, replaced by the constant `"p-3"`, passed `MeetingView.test.tsx`
(15 of 15). Reproduced here before the fix. The only singular case naming a victim reported p-3. The p-4 singular
case, "names one tick in the singular", asserted only "killed at tick 4, one tick before this meeting." So round 1's
claim that each argument of the corpse line is read off the recording was false for this argument. That case now
asserts the whole line: "The reported body is p-4's, killed at tick 4, one tick before this meeting." The old
assertion is a substring of the new one, so no check was weakened. The mutant now fails that case. The round-1
Acceptance item, its Finding 2 paragraph and its mutation table (row M-M13) carry a pointer here. The e2e checks
only "killed at tick", as the finding notes; the unit case is the pin.

**The bounded mutation pass.** It covers the span the finding names, the corpse line's two `fmt` calls and their
guards in `MeetingView.tsx`, with only the listed classes: a message argument replaced by a constant (each
argument by the value of the other planted case), a comparison replaced by a None test or its inverse, and
adjacent branches swapped. There are 11 mutants. Each was applied alone by an anchored replace, and
`npx vitest run src/components/MeetingView.test.tsx` was run in `frontend/`. The file was then restored from a
scratch copy, and `cmp` confirmed it. The `17abded4` column is the same run with `git show
17abded4:frontend/src/components/MeetingView.test.tsx` swapped in, then restored (sha256 checked).

| id | mutant (old → new) | at `17abded4` | now | killing case |
|---|---|---|---|---|
| M-M13 | singular `victim` → `"p-3"` | green | killed | names one tick in the singular |
| M-M4 | singular `victim` → `"p-4"` | killed | killed | reads the victim, the kill tick and the age |
| M-M5 | singular `killTick` → `"4"` | killed | killed | reads the victim, the kill tick and the age |
| M-M14 | singular `killTick` → `"2"` | killed | killed | names one tick in the singular |
| M-M1 | plural `victim` → `"p-4"` | killed | killed | reads the victim, the kill tick and the age |
| M-M15 | plural `victim` → `"p-3"` | killed | killed | states the corpse's age, the reply and each route |
| M-M16 | plural `killTick` → `"0"` | killed | killed | states the corpse's age, the reply and each route |
| M-M17 | plural `age` → `"5"` | killed | killed | states the corpse's age, the reply and each route |
| M-N2 | `corpse.age === 1` → `corpse.age === null` | killed | killed | both singular cases |
| M-B2 | the singular and plural branches swapped | killed | killed | three cases |
| M-N3 | `corpse !== null` → `corpse === null` | killed | killed | five cases |

At `17abded4`: 10 of 11 killed, M-M13 green. Now: 11 of 11 killed. No probe came back green after the fix.

**Validation at this round's head.** Only a test assertion and this card moved, so the recorded-bytes legs are
re-run as a check that nothing moved.

| command | result |
|---|---|
| `measure_featured_criterion.py --alternatives --list` | 0 |
| `pytest tests/api/test_sets.py tests/api/test_public_results.py tests/scripts/test_build_demo_bundle.py tests/scripts/test_measure_featured_criterion.py tests/scripts/test_public_recording_provenance.py tests/scripts/test_check_doc_facts.py -n 6` | 0: 510 passed |
| `npm run lint`, `tsc:check`, `test`, `build` (frontend) | 0; 0; 0: 25 files, 649 tests; 0 |
| `verify_samples.sh` bare; `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i` | 0 (50 clean); 0 each (50, 50, 150, 50, 50) |
| `build_sample_report.py --check`, the five sets | 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `check_doc_facts.py`; `validate_task_docs.py` | 0; 0 (92 work cards) |
| `verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `pytest -m campaign -n 6` | 0: 337 passed |
| `wc -w README.md docs/reading-guide.md` | 1,569; 1,338 |
| `npm run e2e` (local, serial, `CI=1`) | 0: 14 passed, 3 skipped (the media spec's) |
| `bash scripts/check.sh`, once at the final pushed head | in the PR body |

**Decisions.**
1. The finding is repaired by asserting the whole singular line, as the finding asks, not by adding a third
   corpse case. Each corpse argument is now pinned by two values, one per planted victim.
2. The round-1 Acceptance item, its Finding 2 paragraph and its "31 of 31" sentence are annotated in place, so no
   sentence claims more than the code delivered at `17abded4`.

**Limitations.**
- The pass is bounded to the corpse line's span. A survivor of another class or span is outside it.
- The `17abded4` gate numbers rest on the orchestrator's relayed log, not on a committed file.
