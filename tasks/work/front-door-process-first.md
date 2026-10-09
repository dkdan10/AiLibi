# The front door leads with how the agents decide

**Status:** ready

## Outcome

On 2026-10-09 the owner ruled, verbatim, "Merge both when verified and retire the memo's D14 list" (decision memo
8.9). Under it the orchestrator merges this card once its review passes, and keeps two defaults unless the owner says
otherwise: no wrong-but-believable ejection is featured on the strip (the baselines memo's D7, the current state), and
the README leads with the process rows, with the two role-correct figures kept below as the honest "not demonstrated"
line (D8, the baselines memo's recommendation, whose option (b) changes the public tab's heading in the same merge).
Ruling 4 of 2026-10-06 (memo 8.1: "README should be current and can be a focus in the last steps, once the project is
stable") puts this card last in the finish wave. When it is done, on the set shown at dispatch:

- `README.md`'s results table leads with four process rows read from the committed scorecard page: eject ballots
  citing a line their voter held about the player they name (stated as a floor, because every eject ballot must
  cite); eject ballots for someone other than the voter's own top suspect; ballots with no stated reason; and ballots
  recorded as their voter wrote them, with the impostor ballots against a partner stated beside. `check_doc_facts.py`
  holds every figure and before cell to `docs/process-scorecard.md`, and an order rule keeps the four above every
  outcome and role-correct row. The two role-correct rows (proof against no proof; the vent headline) stay below,
  read by the existing "not demonstrated" sentence after the table. The README and the reading guide keep word
  ceilings that are not raised.
- The public results tab no longer heads a role read "Correct ejections"; its heading describes the count, through
  `SPECTATOR_COPY`.
- Every term the new rows introduce is defined in `docs/glossary.md` and linked at its first README use.
- A strip guard holds D7's default: no featured game ejects a crewmate at any meeting.

**Held for the owner, and not in this card.** The baselines memo poses three viewer halves beside D8, each ending
"The owner must say", and the decision memo records no word or default for any of them (8.5 leaves D9 open; 8.9
records only the D7 and D8 defaults): D8-L, the local Tournament dashboard's "gate" vocabulary and order, with the
published Resolution badge "vote gate"; D8.1, the belief panel's Error layer (re-label, re-cut, retire or keep) and
whether the ballot badge follows; and D9-L, whether a skip is read "by the line" or "by the label", with the
grounding-label partition of SKIP ballots after D9. This card changes none of them: no dashboard copy, no badge, no
belief-panel paint or word, no new route. A later card carries whichever the owner rules, on the design of the
baselines memo's Part 3.1 REPLACE rows (W46, W48, V3) and its D8-L.

Nothing in the engine, the agents, the meetings, the prompts, a recording, a committed report, the corpus or an ML
artifact moves. The README ships on GitHub and the public tab's heading ships in the bundle, through
`.github/workflows/pages.yml`; the merge is the orchestrator's under 8.9.

## Evidence

Every `path:line` is a citation at `225d2b77` ("at 225d2b77"), re-anchored by its symbol at dispatch; `335cbdc9`
changes only the decision memo, so each reads the same there. Counts are count-only, keyed by (set, meeting), measured
at authoring at `225d2b77` on `replays/samples/9p2i` (candidate round 2, era `stage-b-r2`) and re-measured at dispatch
on the set shown then; the dispatch figure governs. No rendered prompt, transcript text or seed-band prefix was
printed.

**The rulings and the design.** Decision memo 8.1 ruling 4, 8.2 item 5 (the front door deferred to the last steps;
until then `check_doc_facts.py` keeps every checked README figure true) and 8.9 with its amendment of 2026-10-09
(`tasks/decision-2026-09-24-stage-b-wave.md:1601-1622` at `335cbdc9`; the amendment keeps the comparison records and
leaves both defaults as they were). The design is the baselines memo
(`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`,
advisory, outside the tree): Part 4 D8, whose recommendation (b) reads "the process rows first, leading with those
that moved (Part 3.3 gives the order), then the citation row, then the pair under its existing 'not demonstrated'
sentence, and the Phase-21 paragraph kept as history below; the public tab's heading changed in the same merge"; D7;
Part 3.1's DEMOTE row for G18 (the README lead rows) and KEEP row for W42 (the public tab's heading); Part 3.3; and the
classes of Part 2.1 (S1, S3, S6, S9). Its D8-L, D8.1 and D9-L each end with what "the owner must say", and this card
takes none of them. The doctrine is `tasks/direction-2026-09-19-process-over-outcome.md` sections 7 and 8 with its
addenda, and `docs/game-shape.md`.

**1. The front door leads with role-correct figures.** At 225d2b77 the only decision figures in the results table
(`README.md:19-27`) are row `:25`, ejection accuracy with proof against without (24 / 24 = 1.0000 vs 20 / 42 =
0.4762), and row `:26`, the vent headline (24 / 44 = 55%); the "not demonstrated" paragraph is `:29`. The shown set's
scorecard table (`docs/process-scorecard.md:106-119`, recomputed by `publish_process_scorecard.py --check`) reads,
value against the baseline-9 before column:
- row 1 EJECT, 407/410 = 0.9927 against 494/496 = 0.9960 (`:108`), which the memo reads as a floor (S1);
- row 2 deviating EJECTs, 65/292 = 22.3% against 31/413 = 7.5% (`:111`);
- row 4 unexplained decisions, 11/691 = 0.0159 against 5/845 = 0.0059 (`:114`);
- row 7 agent-authored, 674/691 = 0.9754 against 841/845 = 0.9953 (`:117`); its detail line (`:133`) names
  `teammate_coerced 16` and `invalid_target 1`, which the memo asks to publish beside (S9).
`check_results_agreement` (`scripts/check_doc_facts.py:2773`) holds the table row by row to
`docs/reading-guide.md:16-26`, `check_before_columns` (`:2824`) the before cells, and `check_result_sources` (`:2911`)
with `check_conviction_partition` (`:3015`) re-derive four rows; nothing reads the scorecard page. Word budgets
(`_FRONT_DOOR_BUDGETS`, `:933-938`): README 1,600 and reading guide 1,350, against 1,579 and 1,338 by `wc -w`; a
ceiling is raised only by an owner-ratified contract (`:928-931`). `NO_CONSUMER_NOTE`
(`eval/process_scorecard.py:197-202`) says no component reads `docs/process-scorecard.json`; reading the markdown page
keeps it true and regenerates no scorecard file. If the promotion card merges first, the shown set and its before
column are the ones it leaves (the before column's form is settled under D12 before that card dispatches).

**2. The public tab.** `frontend/src/components/PublicResults.tsx:93` types "Correct ejections" inline over impostors
among ejected players (44/66 at authoring), with its description as an inline literal beside it, outside
`PUBLIC_RESULTS_COPY` (`frontend/src/lib/copy.ts:481`, exported at `:695`); `copy.test.ts:438-457` holds only the
recorded-behaviour span to the copy. `git grep -n -i 'correct ejections'` outside `tasks/` and `audits/` finds the
heading, the README's "not demonstrated" sentence (`README.md:29`, a reported role read that stays) and test and
history prose.

**3. The halves this card leaves to the owner** (cited so the boundary is exact, at 225d2b77). D8-L: the dashboard's
copy reads "the conversion and gate surface" (`copy.ts:165-166`), "Correct skips", "Missed skips" and "Threshold
inversions" (`:221-235`) and "Gate metrics" (`:237-258`), and the published Resolution badge reads "vote gate"
(`:374`, rendered at `MeetingView.tsx:317-321`). D8.1: `BeliefCell.tsx:127-153` paints any |error| at or above
`ERROR_ALIGNED_MAX = 0.32` LOUD with "false accusation" or "missed impostor", and the ballot badge
(`BallotCard.tsx:188-196`, `:211-224`) prints "correct" or "incorrect". D9-L: the skip tiles partition SKIP ballots by
the engine's advisory line, and no served view aggregates SKIPs by grounding label. None of these lines is written
here.

**4. The media and the strip.** `docs/media/provenance.json` names capture revision `52c4b1f3`; `HERO`
(`frontend/e2e/media.spec.ts:80-93`) is seed 19 at tick 9. The spec captures the map canvas, the meeting dialog and
the fog view (`frontend/e2e/media.spec.ts:292-373`, `:836-920`, `:964-1029`, `:1151-1162`) and never opens the public
results tab, so no still shows a string this card changes. `FEATURED_GAMES`
(`frontend/src/components/ReplayPicker.tsx:115-146`) holds 9p2i seeds 19 and 14 and 4p1i seeds 2, 11 and 29. Read
count-only through `SetLoaderRegistry` (each meeting's `ejected_player_id` against the roster), seed 19 ejects an
impostor at meetings 0 and 2 and skips meeting 1, seeds 14, 2 and 11 eject an impostor and seed 29 skips: 0 of 5 eject
a crewmate at any meeting. On round 2, 21 of the 22 crewmate ejections rest on ejecting ballots all labelled
`supported` (the memo's D6/D7 count), so crewmate ejections and wrong-but-believable ones nearly coincide. No test
reads every meeting of a featured game: the tour's ruling 2 (`tasks/work/spectator-tour-round-2.md:727-728`) and the
head pins (`tests/api/test_sets.py:871`, `:951`) read first meetings. The public case `disputed-route` stays withdrawn
(`tests/api/test_public_results.py:164`).

**5. Neighbours.** `stage-b-record-r3` freezes merges into `engine agents meetings observation orchestrator eval api
scripts llm` and related paths from its first seed to its merge (`tasks/work/stage-b-record-r3.md:379-383`). The step
after the round is the orchestrator's (memo 8.8); a promotion is one card with the tour's re-curation (8.7 item 3) and
moves the shown set, the strip, the README cells and the media. The D14 retirement (8.9, as amended) is one card whose
merge also waits for the freeze to lift, and it writes `scripts/check_doc_facts.py` before this card does.

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that turns its test red; each new test is
seen red before the code it guards exists. Every count is the set shown at dispatch, measured at the head that states
it.

- [ ] **The README leads with the four process rows, each held to the scorecard page.**
  - The rows read the shown set's per-set table and row-7 detail line of `docs/process-scorecard.md`, value and before
    cell, in plain words: grounded EJECT (stated as a floor: every eject ballot must cite), deviating EJECT (against
    the voter's own top suspect), unexplained decisions, and agent-authored with the teammate-coerced count beside. At
    authoring: 407/410 against 494/496, 65/292 against 31/413, 11/691 against 5/845, 674/691 against 841/845 with 16.
  - They follow the two integrity rows (replays, the observation boundary) and precede the citation row, the win rate,
    the proof row, the vent row and the learned-policies row. The proof and vent rows keep their claim text
    (`_PROOF_CLAIM`, `_VENT_CLAIM`) and their checks, and the "not demonstrated" sentence (`:29`) still follows the
    table and reads them. The row-1 SKIP half stays off the front door while D9 is open.
  - Mechanism: a new rule in `check_facts` (`scripts/check_doc_facts.py:1061`) that reads the markdown page, never the
    JSON. It locates the shown set's table by its heading, refuses a missing table or row by name, compares each README
    and reading-guide cell through `compare_result_figure` and `compare_before_figure`, and checks that every process
    row's index precedes every outcome or role-correct row's.
  - Planted (`tests/scripts/test_check_doc_facts.py`), each failing by row name: a README numerator edited; a before
    cell edited; a scorecard value edited with the README unchanged; a process row deleted; the proof row moved above a
    process row; the shown set's table removed; the teammate-coerced count edited.
- [ ] **Both pages keep their ceilings, and every figure keeps its check.** The README stays at or under 1,600 words
  and the reading guide at or under 1,350 (`check_front_door_budgets`), with `_FRONT_DOOR_BUDGETS` unchanged in the
  diff. The words come out of prose below the rows; the Phase-20 and Phase-21 bar paragraphs stay on the README,
  condensed if need be (moving them to `docs/history.md` is D8's open half, the owner's). `check_verdict_figures`,
  `check_finding_figures`, `check_injustice_cell` and `check_populated_report_example` stay green unweakened.
  Planted: the README padded one word over its ceiling fails; a condensed bar sentence whose `k of n = rate` no longer
  computes fails `check_verdict_figures`.
- [ ] **No new term reaches the front door undefined.** Each term the rows introduce that is not plain English (at
  least "top suspect") gets a `docs/glossary.md` entry, and each the README uses gets a `_DIALECT_TERMS` row (`:392`),
  so its first use links the glossary; no README cell carries threshold arithmetic. Mechanism: `check_dialect_terms`
  (`:2624`). Planted: the new term's first README use outside a glossary link fails, and its glossary heading deleted
  fails.
- [ ] **The public tab's heading describes its count.** "Correct ejections" (`PublicResults.tsx:93`) becomes a
  `PUBLIC_RESULTS_COPY` key that says what the fraction counts without calling it correct (proposed: "Ejected players
  who were impostors"), and the tile's description moves into the copy with it. The memo's "Ejections, by what the
  table held" is not used: the tile's number is a role read, not a grounding read, and a heading describes its own
  number. Process rows on this tab need a payload change (D8-L (c), riding D9) and are out of scope. Mechanism:
  `PublicResults.test.tsx` renders `PublicResultsView` from a fixture payload and asserts the heading and description
  are the copy values; `copy.test.ts`'s public-results describe gains a case holding the tile span to the copy
  (`proseLiterals` over it is empty) and a walk of `PUBLIC_RESULTS_COPY`'s string leaves (`stringLeaves`,
  `copy.test.ts:129`) for "correct ejection". Planted: "Correct ejections" restored as a literal fails the span case;
  restored as the copy value fails the leaf walk, naming the key.
- [ ] **No featured game ejects a crewmate.** A new test in `tests/api/test_sets.py` reads `FEATURED_GAMES` and every
  meeting of each served featured replay, and fails naming the set, seed and meeting index of any crewmate ejection:
  D7's default ("no wrong-but-believable ejection featured") at its conservative strength. The role read is curation
  and gates no record. Planted: a featured replay copied with one ejectee's role read as a crewmate fails. If the
  promotion's tour already pins the same at every meeting, Results cites that pin and this card adds none.
- [ ] **The stills stay as captured.** No still shows a string this card changes (Evidence 4), so nothing is
  re-captured and `docs/media/` and `frontend/e2e/media.spec.ts` are untouched. Mechanism:
  `test_media_hashes_and_labels_are_current` and `test_the_captions_scene_is_the_recorded_one`
  (`tests/scripts/test_public_recording_provenance.py:138`, `:411`) pass unchanged at H, and `git diff --stat B H --
  docs/media frontend/e2e/media.spec.ts tests/scripts/test_public_recording_provenance.py` prints nothing. Perturbed:
  the README caption's tick edited by one in a scratch copy fails the caption test, so the unchanged pass is not
  vacuous.
- [ ] **Live-tense sentences follow the change.** Every current-tense sentence about the README's old lead rows or the
  tab's old heading is rewritten in this PR (the README, the reading guide, `docs/glossary.md`, and any comment in
  `PublicResults.tsx`). `git grep -n -i 'correct ejections'` outside `tasks/` and `audits/` leaves only the README's
  reported sentence (`:29`), tests, `DESIGN.md` and other history, each hit justified in Results. Mechanism: the
  leaf walk and the span case. Planted: an old sentence restored in a copy value fails the walk.
- [ ] **One bounded mutation pass, and the gate record.** One pass over the listed classes (a dropped filter or
  wrapper, a swapped collection, a comparison made a None test, a role, kind, room or tick read made a constant, a
  dropped tuple member, swapped branches, a loaded source read as its literal, message arguments) over the process-row
  rule and its order check, the public heading's copy read and the strip guard. Survivors are killed or reported in
  Results; a message-argument survivor blocks only in the first review round (memo 8.7 item 2). CI's green run at the
  exact head, cited by run id, is the gate record (item 1).

## Constraints

**Dispatch and merge window against round 3's freeze.** This card dispatches from `main` after `stage-b-record-r3`
merges, after `retire-era-locked-pins` merges, and after the orchestrator has written the step after round 3 (memo
8.8); if that step is the promotion, after the promotion card merges too, because the featured head, the counts and
the before cells follow the shown set. It merges AFTER the round-3 record merges (from round 3's first seed to that
merge the freeze covers `scripts`, which this card writes, and the record's nothing-moves diff covers `frontend`) and
AFTER the retirement and, if taken, the promotion. The finish wave's order: the record, `retire-era-locked-pins`, the
promotion if taken, then this card, the last step ruling 4 names. If `main` moves under the branch, merge `main` in
(never rebase) and re-derive every count.

**One writer per file.** This card writes only Expected scope's files, after the cards before it, each of which lands
first. Written by `retire-era-locked-pins`, then the promotion if taken, then this card: `scripts/check_doc_facts.py`
and `tests/scripts/test_check_doc_facts.py`. Written by the promotion, then this card: `README.md`,
`docs/reading-guide.md`, `docs/glossary.md`, `tests/api/test_sets.py`, `frontend/src/lib/copy.ts`, `copy.test.ts`, and
`frontend/src/components/PublicResults.tsx` with its test. This card writes no file another card of the wave writes
after it; the close audit reads only. `tasks/README.md` and this card's Status line are the orchestrator's, on `main`.

**Not in scope.** The three halves held for the owner (Outcome): the dashboard's copy, order and skip tiles
(`TournamentDashboard.tsx`, the dashboard and meeting copy groups), the Resolution badge, the belief panel's Error
layer and its words (`BeliefCell.tsx`, `BeliefPanel.tsx`, `GuidedTour.tsx`, the Storybook story), the ballot badge
(`BallotCard.tsx`), and any route or served view of SKIPs by grounding label (`api/`). The dashboard's or the public
tab's process block (D8-L (c), riding D9) and D9's tenth scorecard row. G15's vote-correctness stamps: the README's
report-example sentence (`README.md:108`) stays, held by `check_populated_report_example`. Moving the Phase-21
paragraph off the front door (D8's open half). Renaming the proof and vent claims. D7 options (b) to (d) and any case
or featured-list change. Every media capture. Every scorecard, census, profile or report regeneration.

**Rules every change keeps.** The engine stays deterministic; `agents/` never imports `engine/`; no module-level
mutable state; invalid input raises (the rule on a missing table or row). No new `AILIBI_*` lever and no prompt
registry bump. No recorded byte is edited and no history re-scored; the corpus FROZEN line and every ML artifact stay
put, and `scripts/verify_ml_evidence.py` runs offline, never with `--complete`. Role-correctness is reported beside,
never a gate; nothing pushes an agent toward the correct answer; the meeting layer labels and never rewrites;
wrong-but-believable is the game working (direction sections 7 and 8). User-facing copy carries no task or audit ID,
no unexplained jargon and no threshold arithmetic. Every production line has a test that goes red when it is
neutered; each guarantee is stated at its delivered strength; no test is weakened, and a planted hunk in
`tests/scripts/test_check_doc_facts.py` that carries README text follows the new text with its assertion kept. No
live provider call.

**Process (memo 8.7).** CI is the gate record: no local `check.sh` at the final head and no card-only gate commit.
Message-argument survivors follow item 2. Never print a rendered prompt, transcript text or seed-band prefix;
censuses are count-only, keyed by (set, meeting).

**Delivery.** Branch `work/front-door-process-first`, one PR into `main`, merged or fast-forwarded, never squashed,
never amended after push. Focused commits; each commit body carries `Card: tasks/work/front-door-process-first.md`
immediately followed by the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The PR fills every
template section; agents post no PR comments.

**Publication.** This merge publishes through `.github/workflows/pages.yml`: the README on GitHub, and in the bundle
the public tab's heading and description. The PR body states every string that goes live, old against new, and the
bundle diff file by file, built at base and at head in one checkout with `scripts/build_demo_bundle.py --out`
(expected: compiled assets only, no `data/` file; the measured diff governs). The merge is the orchestrator's under
memo 8.9.

**Stop and ask** if either ceiling cannot be held without dropping a checked figure; the shown set's scorecard page
lacks a named row; a featured game ejects a crewmate (D7's residue is the owner's); a file here is written by an
unmerged card that the one-writer map does not order; or the owner's word on D8-L, D8.1 or D9-L arrives before
dispatch (the orchestrator then amends this card or opens the later card; this card never widens itself).

## Expected scope

- Front door: `README.md`, `docs/reading-guide.md`, `docs/glossary.md`.
- Checks: `scripts/check_doc_facts.py` (the process-row rule, its order check, `_DIALECT_TERMS` rows) and
  `tests/scripts/test_check_doc_facts.py`.
- Public tab: `frontend/src/components/PublicResults.tsx` and `PublicResults.test.tsx`; `frontend/src/lib/copy.ts`
  (the tile's heading and description keys) and `copy.test.ts`.
- Strip guard: `tests/api/test_sets.py`.
- This card's Results.

Directly necessary follow-through inside these boundaries is permitted and listed in Results; a file outside them goes
to the orchestrator. Never written: `engine/`, `agents/`, `meetings/`, `observation/`, `orchestrator/`, `llm/`, `api/`,
`eval/`, `training/`, `experiments/`, `replays/`, `tests/fixtures/`, `docs/process-scorecard*`, `docs/gameplay-census*`,
`docs/game-profile.md`, `docs/history.md`, `docs/artifacts.md`, `docs/media/`, `frontend/e2e/`,
`frontend/src/types/`, `TournamentDashboard.tsx`, `MeetingView.tsx`, `BeliefPanel.tsx`, `BeliefCell.tsx`,
`BallotCard.tsx`, `GuidedTour.tsx`, `ReplayPicker.tsx`, `frontend/src/lib/playback.ts`,
`scripts/build_demo_bundle.py`, the audits and `tasks/README.md`.

## Record impact

**What moves:** the README and reading guide's table order and four rows; glossary entries; one doc-facts rule and its
tests; the public tab's heading and description, moved into the copy; one strip guard.

**What stays unchanged:** every recording, MANIFEST, roster, experiment config and committed report under `replays/`;
the corpus and every ML artifact; the scorecard, census and profile pages and JSON; the public payload and every
`data/` file of the bundle; the media; the dashboard, the belief panel, both badges and every served view;
`VIEW_MODEL_VERSION`; the prompts, levers, defaults, ladder tip and era registry; every pre-registration and audit
verdict.

**Future behaviour:** none in play. **Evaluation:** none; the rows report, gate nothing and re-score nothing.
**Publication:** as Constraints states.

## Validation

Run from the branch's worktree; quote each exit code as it came back.

```sh
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
wc -w README.md docs/reading-guide.md
uv run pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_public_recording_provenance.py \
  tests/api/test_sets.py tests/api/test_public_results.py -q
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/publish_game_profile.py --check
for s in samples/4p1i samples/9p2i ml_corpus/4p1i ml_corpus/9p2i; do
  uv run python scripts/build_sample_report.py --sample-dir "replays/$s" --check; done
uv run python scripts/verify_ml_evidence.py            # offline; never --complete
git diff --exit-code <base> -- replays/ training/ api/ docs/media/ frontend/e2e/ docs/process-scorecard.md \
  docs/gameplay-census.md
(cd frontend && npm test && npm run tsc:check && npm run lint && npm run e2e)
git grep -n -i 'correct ejections' -- . ':!tasks' ':!audits'
uv run python scripts/build_demo_bundle.py --out <dir-base>   # at base, then at head into <dir-head>, one checkout
diff -r <dir-base> <dir-head>                                 # file by file into the PR body
```

The mutation pass's rows, the bundle diff and the strings that go live are quoted in Results and the PR; CI's run at
the exact head, by run id, is the gate record.

## Results

Not started.
