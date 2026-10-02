# The featured tour and spectator honesty on the promoted set

**Status:** ready

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

- [ ] **The instrument names the candidates.** `scripts/measure_featured_criterion.py` gains `--list`. Per set
  it prints the seeds behind each count it already prints, plus two new lists:
  - the non-vent openers: games whose FIRST meeting ejects an impostor, with no flag anywhere in the game and
    no vent event at or before that meeting;
  - first meetings that eject a crewmate who is not the opener.

  It prints counts and seeds only. Mechanism: the script, run on `replays/samples`, quoted in Results.
  Proof, in `tests/scripts/test_measure_featured_criterion.py`: on the promoted bytes the lists equal the seeds
  above (re-measured at dispatch). Perturbed: a served replay with a vent event moved before the first meeting
  leaves the non-vent list, and one with the ejected role flipped leaves it too.
- [ ] **The strip, re-picked on the promoted bytes.** `FEATURED_GAMES` keeps `4p1i` 2, 11 and 29 unchanged. Its
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
- [ ] **The category clause, proved by perturbation, re-targeted.** No round-2 game isolates the `role_proof`
  comparison (Evidence), so the holding edit already deleted `test_seed_7_isolates_the_role_proof_clause` and
  landed `test_the_role_proof_clause_rejects_a_recategorised_head` on its holding head. This card re-targets
  that test to the head it picks and re-verifies it, rather than writing it first: it cannot fail at this
  card's base, so the write-first rule does not apply, and Results quotes its green run on the new head and
  its red run with the flag clause weakened. The test takes the head's served replay and recategorises its
  role-proof flag as `cross_statement`, every other field unchanged. It asserts that the criterion rejects the
  perturbed replay by the flag clause (`match=`), and that the weakened predicate (`ejected in flag.subjects`)
  accepts the same replay. The second assertion is what shows the perturbation isolates the clause.
- [ ] **Every label is true and spoils nothing.** Each 9p2i label states only countable facts:
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
- [ ] **The curated cases, re-derived or withdrawn, and always on the strip.** Each case in `_curated_cases`
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
- [ ] **Omniscient-only annotations.** A new pure module, `frontend/src/lib/annotations.ts`, derives three facts
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
- [ ] **The regroup, shown as it happens.** On a replay whose recorded `meeting_reset` is `hub_with_grace`, a
  single step onto the first frame after a meeting's close does not tween: tokens appear in the meeting room.
  Elsewhere a single step still tweens. A per-replay note in plain words says that each meeting gathers the
  survivors in the meeting room and clears the bodies. It shows on reset replays only; `4p1i` stays `preserve`
  and shows nothing new. The `bodies.ts` header comment is rewritten to say a regroup clears every corpse.
  Mechanism: a pure `isRegroupStep` in `frontend/src/lib/` that `MapView`'s `animate` reads. Proofs:
  - unit tests cover a reset step, a preserve step and a two-tick scrub;
  - planted: dropping the config check makes the preserve case snap or the reset case tween, so it fails;
  - a `bodies.test.ts` census leg confirms the rewritten comment: on promoted 9p2i no first post-regroup
    frame carries a body, while `4p1i` keeps unreported bodies across meetings. The retired accumulate rule
    stays the negative control and fails the new leg.
- [ ] **Vent trips drawn as recorded, look-and-wait stays included.** Segment pairing moves to a pure
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
- [ ] **The e2e head-card guard, green in both directions.** The main leg (`journey.spec.ts:475-482`) takes the
  "has evidence" branch on the new head. The planted guard (`:568-618`) opens pick (b) by exact pill text in
  place of the holding edit's `4p1i` seed 11, and walks the "no flags" branch with both mismatches
  constructed against the real render.
  Mechanism: Playwright, run locally, because it sits outside `scripts/check.sh`. Proof: both branches are seen
  in the run, quoted in Results. Planted: pick (b)'s label with "no flagged contradictions" removed makes the
  guard's pairing assertion fail.
- [ ] **The reading guide's exhibits follow the strip.** The paragraph at `docs/reading-guide.md:67-75` is
  rewritten in place, naming at least two featured promoted games and their meetings in countable terms.
  The sentence at `:62-65` stays true, and the rest of the page belongs to the promotion card. Mechanism:
  `check_doc_facts.py` check 16 and the 1,350-word ceiling. Planted: the paragraph naming seed 23, which the
  strip dropped, fails check 16. `wc -w` is quoted in Results.
- [ ] **The bundle change, stated byte by byte.** `uv run python scripts/build_demo_bundle.py --out <scratch>/before`
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

Not started. The implementer records here:
- the commits, and the sections relied on: this card, decision memo sections 1 and 7, partial-record section 5
  rows 13, 14 and 17 (row 16 only for the census leg), the round-2 audit sections 6 and 7, and
  `docs/architecture.md`;
- what the promotion card's holding edit was, file by file, and how it was replaced (`evidence-journey.ts`
  named as replaced), plus the re-targeted category-clause test's green and weakened-clause red runs;
- the instrument's `--list` output, the picks with their reasons, and each kept or withdrawn case;
- every planted failure, with its test id and its red and green runs, and the census agreements;
- the bundle diff;
- every validation command with its exit code, and the limitations, the README stills among them;
- optionally, a cross-read of the owner's gameplay diagnosis, only if a committed copy is in the repository
  at dispatch: each game it names good or bad that is on the strip or among the candidates, with one line
  agreeing or disagreeing with the measured pick. It informs only and never overrides the criterion; without a
  committed copy, Results says it was not read.
