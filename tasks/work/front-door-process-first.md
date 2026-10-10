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

- [x] Review correction: the strip guard is proven to read the picker's own featured list (the three-lens review of
  `1b53d86d`, the correctness and docs lenses: the list read made its literal survived). Mechanism: the guard's
  read-and-load path, `_featured_replays` in `tests/api/test_sets.py`. Planted:
  `test_the_strip_guard_reads_the_pickers_featured_list`, a copy of `ReplayPicker.tsx` with 9p2i seed 1 appended to
  `FEATURED_GAMES`, named `9p2i seed 1 meeting 0`; red on the literal-list mutant (S5), green on the guard.
- [x] Review correction: the strip guard is proven to read every featured game, not only each set's head (the
  three-lens review of `1b53d86d`, the integrity lens: the featured list swapped for the featured heads survived).
  Mechanism: `test_no_featured_game_ejects_a_crewmate_at_any_meeting`. Planted: 9p2i seed 14's and 4p1i seed 11's
  meeting-0 ejectee read as a crewmate, each named by set, seed and meeting index; red on the heads mutant (S6),
  green on the guard.
- [x] Review correction: check 22 is proven to pick the before column by the era the registry says the shown set
  replaced (the three-lens review of `1b53d86d`, the correctness and integrity lenses: the replaced-era read made
  the literal `stage-b-r2` survived). Mechanism: `check_process_rows`. Planted:
  `test_the_before_column_follows_the_registrys_replaced_era`, the registry filing samples/9p2i under round 2, so
  the committed page is refused naming the baseline-9 era, and a page whose before column names baseline 9 is read
  clean; red on the literal-era mutant (P32), green on the rule.
- [x] Review correction: the order rule holds the two integrity rows above the four process rows, as its
  docstring and message say (review round 1, the Codex review of `11eb133a`). Mechanism: `check_process_order`.
  Planted: `test_an_integrity_row_moved_below_the_process_rows_detected`, either integrity row moved below the
  last process row in both tables, red on the previous rule and green on the fix.
- [x] **The README leads with the four process rows, each held to the scorecard page.**
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
- [x] **Both pages keep their ceilings, and every figure keeps its check.** The README stays at or under 1,600 words
  and the reading guide at or under 1,350 (`check_front_door_budgets`), with `_FRONT_DOOR_BUDGETS` unchanged in the
  diff. The words come out of prose below the rows; the Phase-20 and Phase-21 bar paragraphs stay on the README,
  condensed if need be (moving them to `docs/history.md` is D8's open half, the owner's). `check_verdict_figures`,
  `check_finding_figures`, `check_injustice_cell` and `check_populated_report_example` stay green unweakened.
  Planted: the README padded one word over its ceiling fails; a condensed bar sentence whose `k of n = rate` no longer
  computes fails `check_verdict_figures`.
- [x] **No new term reaches the front door undefined.** Each term the rows introduce that is not plain English (at
  least "top suspect") gets a `docs/glossary.md` entry, and each the README uses gets a `_DIALECT_TERMS` row (`:392`),
  so its first use links the glossary; no README cell carries threshold arithmetic. Mechanism: `check_dialect_terms`
  (`:2624`). Planted: the new term's first README use outside a glossary link fails, and its glossary heading deleted
  fails.
- [x] **The public tab's heading describes its count.** "Correct ejections" (`PublicResults.tsx:93`) becomes a
  `PUBLIC_RESULTS_COPY` key that says what the fraction counts without calling it correct (proposed: "Ejected players
  who were impostors"), and the tile's description moves into the copy with it. The memo's "Ejections, by what the
  table held" is not used: the tile's number is a role read, not a grounding read, and a heading describes its own
  number. Process rows on this tab need a payload change (D8-L (c), riding D9) and are out of scope. Mechanism:
  `PublicResults.test.tsx` renders `PublicResultsView` from a fixture payload and asserts the heading and description
  are the copy values; `copy.test.ts`'s public-results describe gains a case holding the tile span to the copy
  (`proseLiterals` over it is empty) and a walk of `PUBLIC_RESULTS_COPY`'s string leaves (`stringLeaves`,
  `copy.test.ts:129`) for "correct ejection". Planted: "Correct ejections" restored as a literal fails the span case;
  restored as the copy value fails the leaf walk, naming the key.
- [x] **No featured game ejects a crewmate.** A new test in `tests/api/test_sets.py` reads `FEATURED_GAMES` and every
  meeting of each served featured replay, and fails naming the set, seed and meeting index of any crewmate ejection:
  D7's default ("no wrong-but-believable ejection featured") at its conservative strength. The role read is curation
  and gates no record. Planted: a featured replay copied with one ejectee's role read as a crewmate fails. If the
  promotion's tour already pins the same at every meeting, Results cites that pin and this card adds none.
- [x] **The stills stay as captured.** No still shows a string this card changes (Evidence 4), so nothing is
  re-captured and `docs/media/` and `frontend/e2e/media.spec.ts` are untouched. Mechanism:
  `test_media_hashes_and_labels_are_current` and `test_the_captions_scene_is_the_recorded_one`
  (`tests/scripts/test_public_recording_provenance.py:138`, `:411`) pass unchanged at H, and `git diff --stat B H --
  docs/media frontend/e2e/media.spec.ts tests/scripts/test_public_recording_provenance.py` prints nothing. Perturbed:
  the README caption's tick edited by one in a scratch copy fails the caption test, so the unchanged pass is not
  vacuous.
- [x] **Live-tense sentences follow the change.** Every current-tense sentence about the README's old lead rows or the
  tab's old heading is rewritten in this PR (the README, the reading guide, `docs/glossary.md`, and any comment in
  `PublicResults.tsx`). `git grep -n -i 'correct ejections'` outside `tasks/` and `audits/` leaves only the README's
  reported sentence (`:29`), tests, `DESIGN.md` and other history, each hit justified in Results. Mechanism: the
  leaf walk and the span case. Planted: an old sentence restored in a copy value fails the walk.
- [x] **One bounded mutation pass, and the gate record.** One pass over the listed classes (a dropped filter or
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

Built on `work/front-door-process-first` from `origin/main` at `76d1c826` (`B` below), on 2026-10-09, after the
round-3 record (#505), the D14 retirement (#506) and the promotion (#507) merged and the step after round 3 was
written (audit section 11); `main` did not move under the branch, so nothing was merged in. Pull request #508. Every
count was re-measured on round 3's bytes (the shown set, era `stage-b-r3`) at the head that states it; the Evidence
section's counts were measured on round 2 and are now the before cells. Every census is count-only, keyed by (set,
meeting): no rendered prompt, transcript text or seed-band prefix was printed, band 2100-2999 stayed unseen, the
held-out generator was not run, no provider was called and the untracked `.env` was not read. Scratch work stayed
under the session scratchpad. The Status line is the orchestrator's (Constraints, "One writer per file"); this
commit fills Results and the acceptance boxes only.

**Commits.** `4bf37433` the four rows, check 22, the glossary entry and the trims; `a729d545` the public tab's
heading; `d980fd9e` the strip guard; `11eb133a` the condensed bar paragraph keeps its verdict word; `71abf7be` the
review-round fix (the integrity rows held above the process rows); then this Results commit.

**Sections relied on.** This card; `docs/architecture.md` ("Packages": the `frontend/` paragraph, copy over typed
DTOs, and the `eval/` paragraph; "Enforced boundaries", untouched); `docs/workflow.md`; decision memo sections 8.1
(ruling 4), 8.2 item 5, 8.7 (items 1, 2 and 4) and 8.9 with its amendment and its two defaults; the baselines memo
(advisory, outside the tree) Part 4 D7 and D8, Part 3.1 (G18 DEMOTE, W42 KEEP, S1 and S9) and Part 3.3; the direction
`tasks/direction-2026-09-19-process-over-outcome.md` sections 7 and 8; the scorecard page's own row definitions
(`eval/process_scorecard.py` `ROW_DEFINITIONS`).

### Decisions

Orchestrator rulings at dispatch, as applied:
1. D8 default (b): the four process rows lead, read from the markdown page, never the JSON; the two role-correct rows
   stay below under the existing "not demonstrated" sentence; the public tab's heading changes in the same merge
   through `PUBLIC_RESULTS_COPY`, to the proposed "Ejected players who were impostors".
2. D7 at its conservative strength: the strip guard fails naming set, seed and meeting index of any crewmate
   ejection. All five featured games are clean, so nothing stopped and the featured list is unchanged.
3. The grown before column: each process before cell reads round 2's block, the era the shown set replaced, through
   `compare_before_figure`; the rule refuses a before column whose header names another era. Both pages now say each
   before cell is what the set's "previously shown recording" read (was "replaced recording").
4. Both ceilings hold without dropping a checked figure. The Phase-20 and Phase-21 bar paragraphs stay on the README;
   the Phase-20 one is condensed, its verdict word and every figure kept.
5. Nothing in `docs/media` or `frontend/e2e` moves.
6. The live-tense sweep is item 7 below.
7. The three halves held for the owner are untouched and no line of theirs is written: D8-L (the dashboard's "gate"
   vocabulary and order, the "vote gate" badge), D8.1 (the belief panel's Error layer and the ballot badge) and D9-L
   (skips by the line or by the label). No diff under `TournamentDashboard.tsx`, `MeetingView.tsx`,
   `BeliefPanel.tsx`, `BeliefCell.tsx`, `BallotCard.tsx`, `GuidedTour.tsx` or `api/`.
8. Publication: the PR body lists every string that goes live, old against new, and the bundle diff file by file;
   the merge is the orchestrator's under memo 8.9.

Decisions of this build:
- **The rows' order** is the card's own: grounded EJECT first, labelled a floor; then deviating; unexplained;
  authored. The baselines memo's "lead with those that moved" was measured on round 2 against baseline 9; against
  round 2, all four of round 3's rows moved little, and the first row states the goal itself under its floor label.
- **Figures quote the page verbatim** (`394/397 = 0.9924`), with no reformatting step; the authored row carries the
  teammate count in words (`coerced_clause`). The page's row-1 SKIP half stays off the front door while D9 is open.
- **The order rule is stronger than the card's wording:** the two integrity rows open the table (each present one
  above every process row, since review round 1), and every other row must sit below all four process rows, so the
  citation row is held too and no new row slips above them unannounced. A row out of place is named with the
  nearest process row it crosses.
- **Link-insensitive claim keys.** To link "top suspect" at its first README use (inside the deviating row's claim)
  within the word budget, `results_rows`, `results_before_column` and `results_row` key a claim with its links
  reduced to text; each table links the term from its own directory and still states one claim. A planted case holds
  that a linked claim keeps its whole-row checks (the injustice clause).
- **Existing tests followed the new text with their assertions kept** (Constraints): the round-2 rebuild hunks were
  regenerated and still rebuild `2eed2e92`'s README byte for byte (16 hunks, checked in scratch);
  `test_stubbed_results_table_detected` also guts the four new rows; `test_results_row_absent_from_the_guide_detected`
  now also asserts the order error its renamed row earns, a second error rather than a looser count.
- **Directly necessary follow-through, inside Expected scope:** `compare_result_figure` and `compare_before_figure`
  gained a `document` keyword (defaulting to the README) so the guide's cells are compared too; the module docstring
  gained check 22 and its summary line names the process rows.
- **The card's Status line stays `ready`.** The house rule and the card's Constraints make it the orchestrator's on
  `main`.

### Acceptance evidence

1. **The rows, held to the page.** Shown set (`docs/process-scorecard.md`, `### samples/9p2i`, rows 1, 2, 4, 7 and the
   row-7 detail line, before column `before: stage-b-r2, as published at 2eed2e92`): grounded EJECT 394/397 = 0.9924
   against 407/410 = 0.9927; deviating 56/291 = 19.2% against 65/292 = 22.3%; unexplained 6/702 = 0.0085 against
   11/691 = 0.0159; authored 692/702 = 0.9858 against 674/691 = 0.9754, with `teammate_coerced 10` stated as "10
   impostor votes against a partner turned into skips". Order in both tables: replays, boundary, the four rows,
   citation, win rate, proof, vent, then (guide) partner ballots and emergence rulings, then learned policies. The
   proof and vent rows keep `_PROOF_CLAIM`, `_VENT_CLAIM` and their checks; the not-demonstrated sentence
   (`README.md:33` at the head) follows the table and reads them. Mechanism: check 22 in `check_facts`. Red first:
   the 17 new doc-facts tests ran before the rule existed, `17 failed, 2 passed` (the two passes are existing tests
   the `-k` filter matched); the rule then ran on the unchanged README and named all four missing rows in both
   tables. Planted, each red by row name: `test_a_process_numerator_edited_in_both_tables_detected`,
   `test_a_process_before_cell_edited_in_both_tables_detected`,
   `test_a_scorecard_value_moved_under_an_unchanged_front_door_detected`, `test_a_deleted_process_row_detected`,
   `test_the_proof_row_moved_above_a_process_row_detected` (README and guide),
   `test_a_process_row_moved_below_the_win_rate_detected`, `test_the_shown_sets_table_removed_detected` (heading,
   then table), `test_a_scorecard_row_missing_from_the_page_detected`, `test_a_truncated_scorecard_row_is_refused`,
   `test_a_before_column_of_another_era_detected`, `test_the_teammate_count_edited_in_both_tables_detected`,
   `test_the_page_teammate_count_moved_detected`, `test_a_page_with_no_typed_rewrites_reads_a_zero_count`,
   `test_the_row_7_detail_line_missing_detected`, `test_an_unreadable_row_7_detail_detected`,
   `test_a_shown_set_with_no_replaced_era_is_named`,
   `test_a_row_above_reordered_process_rows_names_the_first_beneath_it`, `test_a_linked_claim_is_still_read_as_its_row`,
   and, from review round 1, `test_an_integrity_row_moved_below_the_process_rows_detected` (both integrity rows).
2. **Ceilings.** `wc -w README.md docs/reading-guide.md`: 1,585 and 1,339 against 1,600 and 1,350;
   `_FRONT_DOOR_BUDGETS` is unchanged in the diff. Cut from prose below the rows: a duplicated sentence each in the
   not-demonstrated, ML, firewall, install, scopes, running-locally, real-report and samples paragraphs, and the
   condensed Phase-20 paragraph; in the guide, the Phase-20 sentence, §2's run and click paragraphs and the flag
   qualification, §3's guard and alibi-flag sentences, and the ML pointer. `check_verdict_figures`,
   `check_finding_figures`, `check_injustice_cell` and `check_populated_report_example` are unchanged and green.
   Planted: `test_front_door_page_over_its_ceiling_detected` (one word over) and
   `test_verdict_rate_that_contradicts_its_own_fraction_detected` (the condensed sentence's `61 of 103 = 0.5922`
   moved to `61 of 104`, failing `check_verdict_figures`) pass against the new text.
3. **The new term.** `### top suspect (the player a voter's own suspicion rates highest)` in `docs/glossary.md`; a
   `_DIALECT_TERMS` row; first README use inside the deviating row's link. No README cell carries threshold
   arithmetic. Planted: `test_top_suspect_unlinked_at_its_first_use_detected`,
   `test_top_suspect_glossary_heading_deleted_detected`.
4. **The public tab's heading.** `PUBLIC_RESULTS_COPY.ejectionsHeading` = "Ejected players who were impostors",
   `ejectionsDescription` = the old description's words as a template. Mechanism: `PublicResults.test.tsx` "heads the
   ejection tile with what its fraction counts, in the copy's words"; `copy.test.ts` "renders the ejection tile's
   heading and description from the copy" (span case) and "says what the fraction counts, and calls no ejection
   correct" (leaf walk). Red first: `4 failed | 387 passed` before the copy keys existed. Planted: "catches the old
   heading typed back into the tile" (span case) and "catches the old heading, or an old sentence, restored as a copy
   value" (the walk names `PUBLIC_RESULTS_COPY.ejectionsHeading`, then `.ejectionsDescription`).
5. **The strip guard.** No earlier pin read every meeting (the promotion's verifier found only first meetings
   pinned), so `test_no_featured_game_ejects_a_crewmate_at_any_meeting` is added. Count-only on the served bytes: 9p2i
   seed 19 meetings (impostor, skip, impostor), seed 14 (impostor); 4p1i seeds 2 (impostor), 11 (impostor), 29
   (skip): 5 impostor ejections, 2 skips, 0 crewmate ejections. Planted inside the test: seed 19's meeting-0 and then
   meeting-2 ejectee, and 4p1i seed 2's, read as a crewmate, each named by set, seed and meeting index; since the
   three-lens review, 9p2i seed 14's and 4p1i seed 11's too, two games behind their set's head. Perturbed strip,
   committed since that review as `test_the_strip_guard_reads_the_pickers_featured_list`: the picker's list plus
   9p2i seed 1, one of 14 shown-set games that eject a crewmate at some meeting, read through the guard's own
   read-and-load path (`_featured_replays`), names `9p2i seed 1 meeting 0` and nothing else.
6. **The stills.** `git diff --stat B H -- docs/media frontend/e2e/media.spec.ts
   tests/scripts/test_public_recording_provenance.py` prints nothing; both provenance tests pass unchanged. Perturbed
   (scratch copy through `_scratch_front_door`): the caption's tick edited by one reads `names tick 10, the picture
   shows tick 9` plus two scene problems; unchanged, it reads none.
7. **Live tense.** `git grep -n -i 'correct ejections' -- . ':!tasks' ':!audits'` lists 23 hits: `README.md:33`, the
   reported not-demonstrated sentence (kept); `DESIGN.md:982`, historical rationale; `docs/ownership-case-study.md:109`,
   a published account of a past decision on an older recording; `experiments/fresh_deduction_instrument.py:5764` and
   `experiments/lab/report-rubric-design.md:39`, lab history; and 18 in tests (the new planted cases in
   `copy.test.ts` and `PublicResults.test.tsx`, the round-2 rebuild hunks and comments in
   `tests/scripts/test_check_doc_facts.py`, and comments in five eval, experiment and training tests). None is in
   `PublicResults.tsx` or the copy. No sentence in the README, the reading guide or the glossary describes the old
   lead rows or the old heading; the guide's "zero-betrayal-votes row above" now reads "the partner row above".
8. **Mutation pass and gate record.** One pass, 36 mutants, all killed, none surviving, and 3 more on review round
   1's new branch (P29 to P31 below), all killed: 39 in all (scratch `mutate.py`, each an
   exact-text edit restored byte for byte; guarding command: the doc-facts file for the rule, the strip-guard case for
   the guard, the two frontend files for the heading). By class: drop a filter or wrapper 11 (P3, P13, P15, P17, P18,
   P20, P23, P25, P26, P27, F2); comparison to a None test or its inverse 6 (P8, P9, P12, P16, P21, S2); swap a
   related collection 4 (P5, P14, S3, F3); drop a tuple member 4 (P4, P6, P7, P28); a role, kind, room or tick read
   made a constant 3 (P11, P19, S1); swap adjacent branches 2 (P10, P22); a loaded source read as its literal 3 (P1,
   F1, F4); message arguments 3 (P2, P24, S4). While the pass was designed, four tests were added for mutants the
   earlier cases did not reach (P13, P18, P23, P27); the pass then ran once over all 36. The three-lens review of
   `1b53d86d` then found three listed-class mutants outside those 39 that survived; each is killed by a planted case
   added in "Review corrections, round 1" below (S5, S6, P32). The mutant list is in the
   pull request body. The gate record is CI's run at the exact head of the pull request, cited there by run id (memo
   8.7 item 1 bars a further card-only commit to record it); run 38016862362 is CI at `11eb133a`, the head the
   review read.

### Validation

Run from the branch's worktree with `.venv/bin/python` (the card's `uv run`), count-only; no local `check.sh` at the
final head (memo 8.7 item 1).

- `check_doc_facts.py`: exit 0. `validate_task_docs.py`: exit 0, "390 historical phase tasks and 390 prompts; 106 work
  cards".
- `wc -w README.md docs/reading-guide.md`: 1585, 1339.
- `pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_public_recording_provenance.py
  tests/api/test_sets.py tests/api/test_public_results.py -q`: 527 passed at `71abf7be`.
- `publish_process_scorecard.py --check`, `publish_gameplay_census.py --check`, `publish_game_profile.py --check`:
  exit 0 each; `build_sample_report.py --check` for `samples/4p1i`, `samples/9p2i`, `ml_corpus/4p1i`,
  `ml_corpus/9p2i`: exit 0 each.
- `verify_ml_evidence.py` (offline, never `--complete`): exit 0, every check passed, 7 EVIDENCE-BRANCH-ABSENT (the
  expected fresh-clone state). `UV_OFFLINE=1 bash scripts/verify_samples.sh`: exit 0, 4 sets of 50 verified clean.
- `git diff --exit-code 76d1c826 -- replays/ training/ api/ docs/media/ frontend/e2e/ docs/process-scorecard.md
  docs/gameplay-census.md`: exit 0.
- `cd frontend`: `npm test` 821 passed (27 files); `npm run tsc:check` exit 0; `npm run lint` exit 0; `npm run e2e`
  15 passed, 3 skipped (the media-capture specs, which run only under their capture switch).
- Ruff, ruff format and strict mypy on the three changed Python files: clean.
- Bundle: `build_demo_bundle.py --out` at `76d1c826` and at `11eb133a` in this one checkout, compared file by file
  (`diff -rq`, then each differing file with hashed chunk names masked): 110 files, no `data/` file and not the
  bundle's `README.md` note differs; eight compiled files differ: `index.html` and the `CanvasRenderer`, `MapView`,
  `ReplayPicker`, `WebGLRenderer` and `WebGPURenderer` chunks in hashed import names only, and the `index` chunk (the
  copy's two new keys) and the `TournamentDashboard` chunk (the tile reads the copy) in content. The later commits
  change no file under `frontend/`, so the bundle built at `11eb133a` is the head's.
- The campaign tier does not trigger: no file under `tests/training/` changed.

### Review round 1 (2026-10-10 UTC)

The Codex review of `11eb133a` (one P2 finding, `scripts/check_doc_facts.py`, the order check): the rule exempted the
two integrity rows, so moving either below the four process rows in both pages passed while the docstring and the
error message said the integrity rows open the table. Fixed in `71abf7be`: each integrity row present must sit above
every process row and is named with the first process row above it when it is not; the docstrings say so. Planted:
`test_an_integrity_row_moved_below_the_process_rows_detected`, parametrized over both integrity rows, two errors
each (README and guide); run against the previous rule it failed (`2 failed`), against the fix it passes. Mutants
of the new branch, each killed by the doc-facts file: P29 its missing-row filter (`-1 <`) dropped, P30 its comparison
inverted, P31 its report dropped. The doc-facts file then reads 358 passed, and `check_doc_facts.py` exits 0.

### Review corrections, round 1 (2026-10-09)

The three-lens review of `1b53d86d` (correctness, integrity, docs) raised five blocking findings, three distinct
defects, each a listed-class mutant the pass above never applied; all three are fixed by planted cases, and no
production line moves (`scripts/check_doc_facts.py`, the frontend, the README and the reading guide are
byte-identical to `1b53d86d`). One acceptance item per defect is prepended above, naming the lenses that raised it.

1. **The strip guard's featured-list read made its literal** (correctness lens S3, docs lens V5; here S5). The
   guard's read of `FEATURED_GAMES` replaced by today's five pairs passed, because no case varied the picker's
   source. Fix: the read and the loads moved, unchanged, into `_featured_replays`, which the guard calls, and the new
   `test_the_strip_guard_reads_the_pickers_featured_list` writes a copy of `ReplayPicker.tsx` with 9p2i seed 1
   appended (count-only: one meeting, a crewmate ejected), points `_PICKER_TSX` at it, and asserts the guard's output
   is exactly `9p2i seed 1 meeting 0 ejects <its ejectee>, a crewmate`. S5 red (`1 failed, 65 passed`, that test),
   green on the guard.
2. **The featured list swapped for the featured heads** (integrity lens; here S6). Every planted case sat in a head
   game, so a guard reading only 9p2i seed 19 and 4p1i seed 2 passed. Fix: the guard test now also reads 9p2i seed
   14's and 4p1i seed 11's meeting-0 ejectee as a crewmate and asserts each is named by set, seed and meeting index.
   S6 red (`2 failed, 64 passed`: this case on `KeyError: ('9p2i', 14)`, and the picker case on seed 1), green on
   the guard.
3. **Check 22's replaced-era read made the literal `stage-b-r2`** (correctness lens P01, integrity lens; here P32).
   Only the `KeyError` path varied the era, so following the registry's replaced era was unpinned. Fix:
   `test_the_before_column_follows_the_registrys_replaced_era` files samples/9p2i under round 2 (`era_of`
   monkeypatched to `STAGE_B_R2`), whose recording replaced baseline 9's: on the committed page `check_process_rows`
   returns one error, `the '### samples/9p2i' table has no before column naming the baseline-9 era`; with the page's
   before header renamed to baseline 9 it returns none. P32 red (`1 failed, 358 passed`, that test), green on the rule.

**Probe of the spans named and changed** (scratch `mutate.py`, each an exact-text edit restored byte for byte,
checked by digest; guarding command the whole file: `tests/api/test_sets.py` or
`tests/scripts/test_check_doc_facts.py`): 7 runs, all killed. New: S5 (a loaded source read to the canonical
literal), S6 (swap a related collection), P32 (a loaded source read to the canonical literal). Re-run on the guard
the refactor touched: S1 the role read made a constant, S2 the None test inverted, S3 only the first meeting read, S4
the meeting index in the message made 0. The pass and this round together cover 42 distinct mutants: the 39 above
and the three the review named.

**Validation at this commit** (count-only; no local `check.sh`, memo 8.7 item 1): `check_doc_facts.py` exit 0;
`wc -w README.md docs/reading-guide.md` 1585 and 1339; `pytest tests/scripts/test_check_doc_facts.py
tests/scripts/test_public_recording_provenance.py tests/api/test_sets.py tests/api/test_public_results.py -q`
529 passed; `publish_process_scorecard.py --check`, `publish_gameplay_census.py --check`,
`publish_game_profile.py --check` exit 0 each; `build_sample_report.py --check` on the four sets exit 0 each;
`verify_ml_evidence.py` (offline) exit 0, every check passed; `validate_task_docs.py` exit 0; `git diff --exit-code 76d1c826 --
replays/ training/ api/ docs/media/ frontend/e2e/ docs/process-scorecard.md docs/gameplay-census.md` exit 0; `git
grep -n -i 'correct ejections' -- . ':!tasks' ':!audits'` still 23 hits, as item 7 justifies; ruff, ruff format and
strict mypy on the two changed test files clean. No file under `frontend/`, `scripts/` or `docs/` and neither page
changed since `1b53d86d`, so the frontend results and the bundle diff above stand for this head; CI at the exact
head, cited by run id in the pull request, is the gate record. The card's Status line stays the orchestrator's.

### Limitations

- The process rows report one set, the shown 9-player set; the 4-player set's rows stay on the scorecard page only,
  and no figure pools eras. They gate nothing and re-score nothing.
- Row 1 is a floor, not a quality reading: the ballot asks every eject to cite, so it sits near its ceiling by
  construction; row 2 reads deviation from the arithmetic, not whether the deviation was right.
- The public tab gains no process rows: that needs a payload change (D8-L option (c), riding D9) and stays out of
  scope; the tab's numbers and its proof split are unchanged.
- The strip guard holds today's featured list; whether a wrong-but-believable ejection is ever featured stays the
  owner's (D7's residue). The guard reads the role, for curation only.
- Moving the Phase-20 and Phase-21 bar paragraphs off the README (D8's open half) and the three held viewer halves
  (D8-L, D8.1, D9-L) remain the owner's.
