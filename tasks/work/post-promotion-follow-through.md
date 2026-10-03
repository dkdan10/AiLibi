# Follow-through on the promotion and tour reviews

**Status:** ready

## Outcome

The promotion of candidate round 2 ([`promote-round-2`](promote-round-2.md), PR #495, merged at `0e67f42a`) and the
featured tour on the promoted set ([`spectator-tour-round-2`](spectator-tour-round-2.md), PR #496, merged at
`59bbd1be`) are done. Their reviews left small, nonblocking defects that each card's Results or Limitations names
and neither repaired. On the owner's words of 2026-10-02, verbatim, "Merge both and continue", this card closes them.
When it is done:
- the scorecard's frozen before file, a pinned input since the promotion, is in the artifact registry and its
  inventory, and the scorecard row counts three files;
- the front door names the pictured game in plain words, not "the featured strip's head", and its caption says one
  impostor is inside a vent;
- the hero picture's own caption claims only what its right half shows: what p-5 could see at tick 9, not
  everything p-5 knew when it voted at tick 12;
- the public results page calls the seven adopted rules adopted, through `SPECTATOR_COPY`, and keeps the kill
  cooldown's words as they are;
- the recorder tests pass however pytest-xdist distributes them, because none of them writes into the real
  `replays/` tree;
- both merged cards' Results carry a dated note that corrects their wording-only imprecisions and records the
  owner's merge of the promotion with its two questions open. The note closes neither question by inference: Q1
  stays open for the owner, and Q2 needs no ruling because no pushed commit can be rewritten. Nothing written
  before that note changes.

The recorder's era refusal already derives its config path from the registry (Evidence, item 4); this card verifies
that and changes no recorder code. Its merge republishes the public demo, so the merge is the owner's.

## Evidence

Every `path:line` is at `59bbd1be` (labelled as such) and is re-anchored by its symbol at dispatch. Every count is
count-only, measured at authoring at `59bbd1be` unless labelled otherwise, and re-measured at dispatch; the
dispatch figure governs. The reviews' findings are listed outside the repository, at
`/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/cd3daac2-c664-44ef-918c-024def8b33b9/scratchpad/followup-nonblocking-findings.md`;
each item below restates its evidence so the card stands without that file.

**1. The before file is unregistered.** `eval/process_scorecard.py:1949` names `BEFORE_COLUMNS_PATH =
"docs/process-scorecard-before.json"` and `:1954-1956` pins its sha256; the publisher copies it and never
recomputes it. `docs/artifacts.md:115`, the scorecard row, names only the `.md` and `.json` pair and states
`2 files`. `scripts/verify_ml_evidence.py:2794-2797` (`_IN_TREE_PROBES`) and `:2860-2863` (`_IN_TREE_INVENTORY`)
list the same pair, and `tests/scripts/test_verify_ml_evidence.py:162-166` links only the pair into its scratch
tree. `uv run python scripts/verify_ml_evidence.py` passes regardless (63 checks, FAIL 0, as both merged cards
record): no leg asks whether a pinned input has a row.

**2. Front-door jargon.** `README.md:13` (the caption) reads "9p2i seed 19, the featured strip's head"; `:110` ends
"a capture of the 9-player set's featured head"; `docs/media/README.md:6` says "the featured strip's head". Neither
"strip" nor "head" is in `docs/glossary.md`, so craft rule 4 is broken on the front door. The caption also says
"both impostors are on the map", while `frontend/e2e/media.spec.ts:72-75` and `docs/media/README.md` say one of
them is inside the vents at tick 9. In plain words, seed 19 is the game the guided tour opens on:
`tests/api/test_sets.py:669` pins `featured[0] == ("9p2i", 19)` as "the tour's landing game". The README holds
1,569 of its 1,600 words (`wc -w README.md`). Two tests quote these words:
- `tests/scripts/test_public_recording_provenance.py:178-180` pins the caption's opening;
- `tests/scripts/test_check_doc_facts.py:1715-1720` carries the samples sentence as the current side of a planted
  `d41c9006` hunk, whose `readme.count(current) == 1` must hold. The tour's `3a205c5e` had to follow that hunk the
  last time the sentence moved.

**3. The hero caption overstates the fog panel.** `frontend/e2e/media.spec.ts:867-868` renders, into
`docs/media/spectator-two-truths.png`, the caption "Right: everything p-5 was allowed to know when it voted". The
right half is p-5's view at tick 9 (`:821-822` assert the deep link's tick). p-5 spoke and voted at the tick-12
meeting (`:776-784`), with observations made after tick 9; the tour's docs review read a tick-12 sighting on the
card in the same picture. The comment at `:803` repeats the claim. The caption is pixels, so it changes only
with a re-capture: `docs/media/README.md` gives the one command, and `docs/media/provenance.json` names
`capture_revision` `8d07a340` and each asset's sha256. The capture spec runs only under `AILIBI_CAPTURE_MEDIA=1`,
so no CI job reads the caption today.

**4. The recorder's era refusal is already registry-derived.** `scripts/_declared_experiment.py:426` reads
`declared = entry.era.declared_config`, and all three era templates take `config=declared`. Review round 3 of the
promotion added `test_an_era_refusal_names_the_set_and_the_declared_file_it_found`
(`tests/scripts/test_refresh_samples.py:2065`), whose planted registry gives `samples/4p1i` its own declared file.
At authoring, D10 was re-applied: `config=declared` in the wrong-config refusal was replaced with
`'replays/samples/9p2i/experiment-config.json'`, and the selection `-k "era_refusal_names_the_set or declared"`
read 2 failed, 11 passed (both variables of that case); the file was restored with `git checkout`. So D10 is
closed, as the promotion's round-3 R14 row says.

**5. The recorder tests race on the shared tree.** Several cases create and delete paths inside the real `replays/`:
- the `.test-symlink-decoy`, `.test-composed-decoy` and `_DECOY` directories (made at `:1320`, `:1349`, `:2443`);
- the planted round (`:2517`);
- the deliberate stray (`:2532`).
Other cases take whole-tree snapshots (`_new_replays_paths`, `:2299-2304`) or clean whole-tree strays
(`_replays_tree_restored`, `:1193-1231`). The guard's own walk raises when a directory vanishes mid-walk
(`scripts/_declared_experiment.py:325-344`). `tests/scripts/test_candidate_sets.py:234-248` reads the real
candidates family. Measured at authoring:
- `uv run pytest tests/scripts/test_refresh_samples.py -n 6 --dist load -q -p no:cacheprovider` failed 4 of 154
  cases in each of three runs (the symlink decoy, two `a switched-on config` targets, the round already on disk);
- with `tests/scripts/test_candidate_sets.py` added under `-n 8 --dist load`, two runs failed 4 and 3 cases, and the
  first of those failures included `test_every_committed_round_holds_its_declared_shape`;
- one run under `-n 4 --dist load` passed 154 of 154, and three runs of both files under `-n 2 --dist loadfile`
  passed 183 of 183. `check.sh` uses `--dist loadfile` (`scripts/check.sh:35-42`), so the gate stays green while
  the race remains.
`git status --porcelain --ignored -- replays` was empty after every run.

**6. Wording-only imprecisions in the merged cards' Results.** Each is reproduced here:
- **The referee.** The promotion's Results (`tasks/work/promote-round-2.md:601`) credits
  `tests/eval/test_watchability.py` with holding the referee's JSON byte-identical at base and head. No test there
  does that. Measured directly with `uv run python scripts/measure_baseline.py --watchability --json <set>`, the
  JSON is 21,981 bytes (sha256 prefix `badba42d`) on `samples/4p1i`, 64,432 bytes (`bc574592`) on
  `ml_corpus/9p2i` and 22,088 bytes (`79055133`) on `ml_corpus/4p1i`. These equal the review's base-and-head
  readings.
- **The re-pin count.** `:674` states 527 annotations across 38 files by a `grep -c "was"` style count. Over
  `git diff d41c9006 4a36dc03 -- tests/ frontend/src/`, a plain count of lines holding `was` gives 1,325; added lines
  matching `^\+.*(#|//) was` give 530 across 39 files, 529 with a trailing space. Two notes give the baseline-8
  value rather than the replaced one: `tests/meetings/test_citation_relevance.py:343` and
  `tests/agents/test_memory_meeting_history.py:807`.
- **The criterion row.** `:746` lists three `measure_featured_criterion.py` commands but two results. They read
  11 of 50 (`--set 9p2i`), 1 of 1 (`--games 9p2i:3`) and 0 of 1 (`--games 9p2i:23`), each exit 0.
- **The red-at-base run.** `:693-697` states 15 collection errors and "5 failed of 32". A review reproduction read
  11 errors (7 at collection, 4 at setup) with 3 skipped, and a 118-test frontend run.
- **The mutation pass.** `:710` uses COMPARE, CONST, NEGATE and DELETE, not the listed classes. Its survivor M14
  (the FloorPin numerator) stays open.
- **The owner's questions.** Q1 (the champion-flip comparator held at (11, 50)) and Q2 (twelve commits
  `148fa211`..`4a36dc03` carrying the Opus 5.5 trailer) were open when the owner merged both PRs.
  - The promotion's round-1 review corrections (`tasks/work/promote-round-2.md`, "Open owner questions; the
    merge waits on both") list Q1's options: (a) hold the `d41c9006` reading at 11/50, (b) re-derive it from the
    promoted MANIFEST at 24/50, (c) another ruling.
  - The owner's only words are "Merge both and continue". They rule on neither question.
  - The code as merged holds option (a), so Q1 stays open for the owner.
  - Q2 needs no ruling: the twelve commits are published on `main` and stand as pushed, and no rewrite is
    possible under either answer.
- **The tour card.**
  - The band lines are said to be "quoted in the PR" (`tasks/work/spectator-tour-round-2.md:548`); they are not.
  - The PR's copy-that-goes-live list omitted three items: the single-tick route words, the README samples
    sentence and the reading guide's exhibit paragraph.
  - The `git grep` sentence (`:816`) also matches the card's own past-tense lines and two comment lines in
    `regroup.test.ts`.
  - "five ticks" (`:228`) paraphrases the rendered "5 ticks".
  - The PR summary called the merged review round 3 test-only, but it also brought a card commit.
  - Commit `33f0e776` has no message body.
  - The Limitations (`:756-758`) route the PublicResults defect to `rubric-extractor-era`; this card takes it.

**The public results wording.** `BehaviorIdentity` (`frontend/src/components/PublicResults.tsx:6-27`) heads every
recorded setting "Recorded experiments:" (`:27`) and files the adopted `vent_entry_policy = own_fresh_kill` and
`meeting_reset = hub_with_grace` under "experimental movement or action policies" and "experimental round or task
rules" (`:22-23`). It labels the recorded factory kind `experimental` "Experimental agent factory" (`:24`). That
kind means exact built-in agents run with recorded tactical settings (`orchestrator/game.py:3227-3232`). Built at
authoring, the promoted set's public payload has one group: 50 games, kind `experimental`, a config. So the shown
set's card carries a form of "experiment" four times. The words live in the component, not in `SPECTATOR_COPY`
(`frontend/src/lib/copy.ts:198`), and `PublicResults.tsx` is not one of the disk leg's in-scope sources in
`frontend/src/lib/copy.test.ts:53-64`. The adoption record is `docs/experiment-arms.md:122-133`. It lists seven
`field = value` pairs, and `vent_exit_policy = look_and_wait` is kept but not adopted. The shown set's declared
config, `replays/samples/9p2i/experiment-config.json`, holds the seven pairs, `look_and_wait` and
`kill_cooldown_ticks` 6. The cooldown words came from the round-2 audit's follow-up
(`audits/audit-2026-10-01-stage-b-r2.md` section 1.11) and are pinned at `PublicResults.test.tsx:77-88`. The
diagnosis of 2026-10-02 (`tasks/diagnosis-2026-10-02/README.md`, Part 3, card 0) names this item.

**Every leftover's disposition.** In this card: items 1-6 above, and the PublicResults wording. Elsewhere:

| Leftover | Disposition |
| --- | --- |
| Trailers on `148fa211`..`4a36dc03` (Q2); `33f0e776` without a body | stand as pushed; recorded in the dated notes; Q2 needs no ruling, because no rewrite is possible; no history rewritten |
| `refresh_samples.sh` help text and comment; the no-rubric lead's scoring path | `rubric-extractor-era` |
| E3 (`ERAS`), C3 and the counterfactual spelling gap, C5, `pool()` | `census-reporter-base-rate` |
| Per-sentence curated-case coverage | closed by the tour (its Decision 4) |
| A6, R1, the W2 granularity, D10 | closed by the promotion's review rounds 3, 1, 1 and 3; D10 re-verified above |
| The regroup note's qualifier (Codex P2) | closed by the tour's review round 1 |
| The FSM comparator (Q1): (a) hold 11/50, (b) re-derive 24/50, (c) another ruling | open for the owner; the code holds option (a) as merged; recorded in the promotion's note; no code moves |
| M14 (stage-b-r2 FloorPin numerators) | open; no wave card owns it |
| `docs/deployment.md:127` "29 MB" (it measures about 33 MB) | open; no wave card owns it |
| The strip comment's wording (seed 19's trip, the seed pins) | open; a `ReplayPicker.tsx` comment, no card owns it |
| Equivalent or unlisted-class survivors (V16, M18, F4, N-*, the turn subject) | no action; named in their cards |
| Disclosed process notes (`check.sh` run twice, Codex not re-run, bundle `created_at`) | no action |

## Acceptance

Each item names its enforcing mechanism and a planted or perturbed proof. Each new test is written first and fails at
this card's base for the stated reason; Results quotes that run.

- [ ] **The before file is registered.**
  - `docs/artifacts.md`'s scorecard row names `docs/process-scorecard-before.json`, says it is the frozen before
    columns (sha256-pinned and never recomputed), and states `3 files`.
  - `_IN_TREE_PROBES` and `_IN_TREE_INVENTORY` name the three paths, and the scratch availability tree links them.
  - Mechanism: a new case in `tests/scripts/test_verify_ml_evidence.py`. It reads `BEFORE_COLUMNS_PATH` from
    `eval.process_scorecard`, the sourced constant. It requires that path in the row's probe and inventory entries,
    and the row's stated count to equal the index.
  - Planted: the row restated as `2 files` fails the inventory leg ("promises 2 files, the index tracks 3"). An
    inventory entry without the file fails the same leg. `BEFORE_COLUMNS_PATH` monkeypatched to another path fails
    the new case.
  - `verify_ml_evidence.py`, offline, keeps its check count and FAIL 0.
- [ ] **The front door names the pictured game in plain words.**
  - `README.md`'s caption, its samples sentence and `docs/media/README.md` call 9p2i seed 19 the game the demo's
    guided tour opens on, or other plain words a first reader understands. None says "strip" or "head".
  - The caption says one impostor is inside a vent, and the README stays at or under 1,600 words.
  - Mechanism: `tests/scripts/test_public_recording_provenance.py`. Its caption pin holds the new words, and a new
    assertion refuses "strip's head" and "featured head" in both files. `tests/api/test_sets.py:669` holds the
    claim itself true.
  - Planted: the `59bbd1be` caption, put back into a scratch README, fails that assertion by name.
  - `tests/scripts/test_check_doc_facts.py`'s planted `d41c9006` hunk carries the new sentence as its current side.
    Its previous side is unchanged, and the case still passes all four of its assertions.
- [ ] **The hero caption claims only what the picture shows.**
  - `frontend/e2e/media.spec.ts`'s caption and its `:803` comment say only this: the left half is what happened and
    the right half what p-5 could see, both at tick 9, and the card below is the accusation p-5 wrote at the meeting
    that followed, at tick 12. No clause says the panel is everything p-5 knew when it voted.
  - The four spectator assets are re-captured with the documented command. `provenance.json` names the capture
    revision and every new digest.
  - The meeting still and the GIF come out byte-identical, or Results names which did not and why. The clip is
    re-shot, as the media README documents.
  - Mechanism: `test_public_recording_provenance.py` keeps holding the asset digests and the recording's sha256. A
    new case reads the caption template out of `media.spec.ts`. It refuses "when it voted" and "allowed to know" and
    requires the tick placeholder.
  - Planted: the `59bbd1be` template in a scratch copy fails the new case. A changed image with unchanged provenance
    fails the existing digest check.
- [ ] **The public results page calls adopted rules adopted.**
  - Every word of `BehaviorIdentity` moves into a new public-results group of `SPECTATOR_COPY`, with `fmt`
    templates for counts. `PublicResults.tsx` joins the disk leg's in-scope sources with a rendered fragment.
  - A field at its adopted value, one of the seven pairs, is listed under a lead that says adopted, each in plain
    words. `own_fresh_kill` and `hub_with_grace` gain their own phrases, defined from `docs/glossary.md` and the
    linked cards. A recorded kill cooldown keeps its words, "a kill cooldown of N ticks set for these recordings",
    outside the adopted list. `look_and_wait` is named in plain words as set for these recordings, never as adopted.
  - Any other non-default value keeps a label that says experimental. A default group keeps "No enabled experiments
    recorded. This alone does not certify the default behavior." The factory kind `experimental` is labelled by
    what it records, built-in agents with recorded tactical settings, without the word experimental.
  - On the shown set's declared config, read from disk, the card's text carries no form of "experiment".
  - Mechanism: the seven pairs live in a new `frontend/src/lib/adoptedRules.ts`. Its test reads
    `docs/experiment-arms.md`'s "Adopted arms" paragraph and the declared config off disk, and requires the constant
    to equal the paragraph's seven pairs, each present in the config. `PublicResults.test.tsx` renders the cases.
  - Proof by exhaustive enumeration: 128 on/off combinations of the seven fields, times the three vent exit values,
    times cooldown set or unset, is 768 renders. In none is an adopted field at its adopted value called
    experimental or left out, and in none is a value outside the seven called adopted.
  - Planted: the paragraph with one pair's value edited, and a config copy with one adopted field moved, each fail
    the source pin. Each changed assertion is replaced by one at least as strong: the old phrase is asserted absent
    where its classification changed.
- [ ] **The recorder's era refusal stays registry-derived.**
  - Mechanism: `test_an_era_refusal_names_the_set_and_the_declared_file_it_found`.
  - Proof: D10 re-applied at dispatch fails it for both variables, and Results quotes the run.
  - Only if D10 survives does this card add a planted-registry case to `tests/scripts/test_refresh_samples.py`.
    `scripts/_declared_experiment.py` does not change.
- [ ] **The recorder tests pass under any distribution.**
  - While the guard under test holds, no case in `tests/scripts/test_refresh_samples.py` creates, edits or deletes a
    path under the real `replays/` tree.
  - Decoys, planted rounds and strays live under the case's own `tmp_path`. Otherwise the case aims, read-only, at an
    existing committed directory whose bytes it compares before and after, or at an absent path of its own unique
    name that the guard must refuse before anything is made.
  - Every "nothing was created" check still fails on the path a regressed guard would create for that case.
    Planted: on a scratch tree, a stray of the case's own kind is reported.
  - Mechanism: the file's own cases plus `git status --porcelain --ignored -- replays` after each run.
  - Perturbed proof: one case's decoy restored under `replays/samples/` turns the `-n 6 --dist load` runs red
    again, and Results quotes the count.
  - Proof: three runs each of `-n 4 --dist load` and `-n 6 --dist load`, and of both files under
    `-n 8 --dist load`, all green. The serial run and the `--dist loadfile` run stay green. No case is skipped,
    deleted or loosened to get there.
- [ ] **Both merged cards carry a dated note in Results, and nothing above it changes.**
  - The promotion's note records the owner's words verbatim, "Merge both and continue", and that Q1 and Q2 were
    both open at the merge. It records that the code holds Q1's option (a), the `d41c9006` reading at (11, 50),
    and that the twelve commits stand as pushed: Q2 needs no ruling, because no rewrite is possible. It lists Q1
    as open for the owner, beside M14, and never as closed.
  - It corrects the referee's named mechanism to the measured command and digests, the re-pin count to the exact
    regex and its count, the two baseline-8 notes, the criterion row's three results and the mutation classes. It
    re-runs the red-at-base recipe and records the counts, or marks the 15 and 32 unreproduced. It records D10
    closed, and Q1 and M14 open.
  - The tour's note corrects each item under "The tour card" in Evidence item 6. It records `33f0e776` closed as
    pushed and the PublicResults defect re-routed to and closed by this card.
  - Mechanism: `git diff --numstat 59bbd1be -- tasks/work/promote-round-2.md tasks/work/spectator-tour-round-2.md`
    shows zero deleted lines.
  - Proof: each corrected figure is re-measured by the command the note quotes, at the head that states it.
- [ ] **Every changed production line goes red when neutered, and one bounded mutation pass is run.**
  - The spans: `PublicResults.tsx`, the new copy group, `adoptedRules.ts`, the two `verify_ml_evidence.py` entries
    and the caption lines of `media.spec.ts`.
  - Results tabulates each neutered line with the test that failed. Equivalent probes are named with their reason.
  - One pass covers those spans in exactly the eight listed operator classes:
    - drop a filter on a collection;
    - swap one collection for a related one;
    - a None test or comparison to its inverse, or to a None test;
    - replace a read with a constant;
    - a message argument to a constant;
    - drop one member of a tuple of kinds;
    - swap adjacent branches;
    - a read of a loaded source to the canonical literal.
  - Each mutant is applied alone and the file is restored from a copy with its sha256 checked. Each survivor is
    killed or named equivalent with its reason.
- [ ] **The gates hold.**
  - Nothing recorded moves: `verify_samples.sh`, the five `build_sample_report.py --check` runs, both publishers'
    `--check` and `pytest -m campaign` read as at `59bbd1be`.
  - `npm run e2e` is green.
  - The bundle diff (`build_demo_bundle.py --out`, base against head, `diff -rq`) shows `data/` identical and only
    the hashed JS assets and `index.html` changed.
  - `bash scripts/check.sh` passes once at the pushed head, with the real exit code read.

## Constraints

- **Authorization.**
  - The owner's direction of 2026-10-02 is the scope: "Merge both and continue".
  - No live provider call, no recorder run outside the test suite's fake runs, no spend.
  - The untracked `.env` is never read.
  - No rendered prompt, transcript text or seed-band prefix is printed, and every count is count-only.
- **House rules.**
  - The engine stays deterministic, `agents/` never imports `engine/`, and there is no module-level mutable state.
  - Invalid input raises, with no silent fallbacks.
  - A new invariant gate includes a planted case.
  - Claims name their enforcing mechanism, and numbers come from committed evidence with the command in Results.
  - No new `AILIBI_*` lever or environment switch: the existing `AILIBI_CAPTURE_MEDIA` capture switch is used as
    documented.
  - No prompt registry bump.
  - No recorded byte is edited and no history is re-scored.
  - The corpus FROZEN line and every ML artifact stay put; `scripts/verify_ml_evidence.py` runs offline, never
    with `--complete`.
- **The wave's lessons.**
  - Each production line is held by a test that goes red when it is neutered.
  - Guarantees are stated at the strength delivered.
  - Live-tense sentences about old behaviour are fixed in the same PR.
  - Numbers are measured at the head that states them.
  - Universal guarantees get properties, here by exhaustive enumeration, since no new dependency is added.
  - No test is weakened.
  - A Hypothesis property that loads a map carries `settings(deadline=None)`.
  - Every sourced constant gets a planted source-change case.
  - One bounded mutation pass is run.
- **The owner's direction.**
  - Nothing here changes what an agent holds, how a vote or skip is reached, or what the meeting layer labels.
  - Role-correctness is not read.
  - ML stays held (ruling 12).
  - The change serves a showable state.
- **History.**
  - Pushed commits are never rewritten.
  - The two merged cards gain one dated subsection each in Results, and nothing above it is edited.
  - `docs/media/` assets are replaced only by the documented re-capture.
- **Not in this card.**
  - The trailers and the bodyless commit: they stand as pushed and are recorded only; Q2 needs no ruling.
  - The FSM comparator (Q1): no code change. It stays open for the owner (below).
  - `scripts/refresh_samples.sh`, owned by `rubric-extractor-era`.
  - The no-rubric lead, owned by the rubric card.
  - The census cells and E3, C3, C5 and `pool()`, owned by `census-reporter-base-rate`.
  - M14, `docs/deployment.md` and the strip comment: open for the orchestrator.
  - `scripts/check_doc_facts.py`: the jargon fix uses plain words and adds no term to its dialect list.
  - `api/`, its DTOs and the generated types.
- **Open for the owner.**
  - Q1, the champion-flip FSM comparator: (a) hold the `d41c9006` reading at 11/50, as the code does now; (b)
    re-derive it from the promoted MANIFEST at 24/50; (c) another ruling. "Merge both and continue" ruled on
    neither question, so this card records Q1 as open, beside M14, and moves no code.
- **One writer at a time.**
  - This card dispatches in parallel with `census-reporter-base-rate` and `route-check-replay` from `main` at the
    coordination commit that lands the four cards. The three merge one at a time: census, then route, then this
    card, by the owner. `rubric-extractor-era` dispatches from `main` after this card merges and merges last.
  - `tests/scripts/test_refresh_samples.py`: this card first (decoys, planted rounds and strays under `tmp_path`;
    the D10 re-check), then `rubric-extractor-era` (the dry-run and help cases of its rubric step). The census
    and route cards never touch it.
  - `frontend/src/lib/copy.ts`: this card first (the new public-results group of `SPECTATOR_COPY`), then
    `rubric-extractor-era` (the interestingness strings in the dashboard group).
  - `frontend/src/lib/copy.test.ts`: this card's (`PublicResults.tsx` joins the in-scope sources).
    `rubric-extractor-era` edits it only if its copy walk needs it, after this card merges.
  - `tests/scripts/test_public_recording_provenance.py` and `tests/scripts/test_verify_ml_evidence.py`: this card
    writes them; `rubric-extractor-era` only runs them.
  - This card alone writes `README.md`, `docs/media/*`, `frontend/e2e/media.spec.ts`, `PublicResults.tsx` and its
    test, `adoptedRules.ts` and its test, `scripts/verify_ml_evidence.py`, `tests/scripts/test_check_doc_facts.py`
    and the two merged cards.
  - `docs/artifacts.md`: one row per card, in the merge order. Census writes the gameplay-census row's text and
    route the `experiments/lab/` row; this card writes the process-scorecard row (3 files), and the `docs/media/`
    row only if its rounded size moves; `rubric-extractor-era` writes its three rows last. This card merges
    `main` and edits its rows in its last commit, then re-runs `scripts/verify_ml_evidence.py` offline.
  - `tasks/README.md`: the inventory sentence only, re-derived with `scripts/validate_task_docs.py` at this card's
    final merge of `main`, after the census and route cards'.
- **Publication.**
  - `pages.yml` rebuilds the demo on every push to `main`.
  - `PublicResults.tsx`, the new copy group and `adoptedRules.ts` ship in the bundle's JS. The README caption and the
    re-captured picture go live on the GitHub front door.
  - So the PR's merge is the owner's, not the orchestrator's. The PR states the copy that goes live, old and new
    words side by side, and the bundle diff.
- **Copy.** User-facing words carry no task or audit ID, no unexplained jargon ("arm", "regroup", "era" and "Stage-B"
  are not used on the public results card) and no threshold arithmetic.
- **Delivery.**
  - Branch `work/post-promotion-follow-through`, one PR into `main` with every section of the PR template, merged
    by merge commit or fast-forward, never squash.
  - Each commit body ends with `Card: tasks/work/post-promotion-follow-through.md`, immediately followed by the
    exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Expected scope

- `docs/artifacts.md`: the scorecard row. Only if the re-captured media move its rounded figure, the `docs/media/`
  row too.
- `scripts/verify_ml_evidence.py`: the scorecard entries of `_IN_TREE_PROBES` and `_IN_TREE_INVENTORY` only.
- `tests/scripts/test_verify_ml_evidence.py`.
- `README.md`: the caption and the samples sentence only.
- `docs/media/README.md`.
- `docs/media/provenance.json`, `docs/media/spectator-two-truths.png`, `docs/media/spectator-meeting.png`,
  `docs/media/spectator-journey.gif` and `docs/media/spectator-journey.webm`, by the documented re-capture only.
- `frontend/e2e/media.spec.ts`: the caption, its `:803` comment and the hero comment at `:70-75`.
- `tests/scripts/test_public_recording_provenance.py`.
- `tests/scripts/test_check_doc_facts.py`: the current side of the planted samples hunk only.
- `frontend/src/components/PublicResults.tsx` and `frontend/src/components/PublicResults.test.tsx`.
- `frontend/src/lib/copy.ts` (the new group) and `frontend/src/lib/copy.test.ts` (the in-scope source).
- `frontend/src/lib/adoptedRules.ts` and `frontend/src/lib/adoptedRules.test.ts` (new).
- `tests/scripts/test_refresh_samples.py`.
- `tasks/work/promote-round-2.md` and `tasks/work/spectator-tour-round-2.md`: one dated Results subsection each.
- `tasks/work/post-promotion-follow-through.md` and `tasks/README.md` (the inventory sentence).

Directly necessary follow-through inside these files is permitted and recorded in Results. Nothing changes under
`engine/`, `agents/`, `meetings/`, `orchestrator/`, `llm/`, `eval/`, `training/`, `api/`, `replays/` or
`tests/fixtures/`, or in `scripts/_declared_experiment.py`, `scripts/refresh_samples.sh` or
`scripts/check_doc_facts.py`. A file outside this list goes to the orchestrator first.

## Record impact

- No recorded byte, manifest, report, census, scorecard output or ML artifact moves, and no future recording
  changes.
- No prompt byte or experiment field changes, and no evaluation moves.
- The registry gains one file in an existing row.
- What changes for a reader:
  - the public results card's words for recorded settings and the factory label, which ship in the demo bundle;
  - the README caption and samples sentence, and the hero picture's caption, which go live on the front door.
- Older payloads render as before except for that wording, and no DTO changes.
- Measurement: the gates under Validation at base and head, the bundle diff and the distributed test runs.

## Validation

```sh
uv run python scripts/verify_ml_evidence.py             # offline; never --complete
uv run pytest tests/scripts/test_verify_ml_evidence.py tests/scripts/test_public_recording_provenance.py \
  tests/scripts/test_check_doc_facts.py -q
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
wc -w README.md
cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts   # the re-capture
shasum -a 256 docs/media/*.png docs/media/*.gif docs/media/*.webm        # against provenance.json
cd frontend && npm run lint && npm run tsc:check && npm run test && npm run build
cd frontend && npm run e2e
uv run pytest tests/scripts/test_refresh_samples.py -k "era_refusal_names_the_set or declared" -q  # D10 re-applied
uv run pytest tests/scripts/test_refresh_samples.py -n 4 --dist load -q -p no:cacheprovider        # three times
uv run pytest tests/scripts/test_refresh_samples.py -n 6 --dist load -q -p no:cacheprovider        # three times
uv run pytest tests/scripts/test_refresh_samples.py tests/scripts/test_candidate_sets.py -n 8 --dist load -q
git status --porcelain --ignored -- replays                                                       # empty each time
uv run pytest tests/scripts/test_refresh_samples.py tests/scripts/test_candidate_sets.py -q          # serially
uv run python scripts/measure_baseline.py --watchability --json replays/samples/4p1i               # and both corpus sets
uv run python scripts/measure_featured_criterion.py --set 9p2i                                      # and --games 9p2i:3, 9p2i:23
bash scripts/verify_samples.sh
uv run python scripts/build_sample_report.py --sample-dir <each of the five sets> --check
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run pytest -m campaign
uv run python scripts/build_demo_bundle.py --out <scratch>/before|after && diff -rq <scratch>/before <scratch>/after
git diff --numstat 59bbd1be -- tasks/work/promote-round-2.md tasks/work/spectator-tour-round-2.md
bash scripts/check.sh                                   # once, at the pushed head, in a clean worktree
```

Run `check.sh` to its end, because `set -e` masks later gates. On macOS the evolution-strategy hash pin is Linux-only;
gate in a clean worktree and cite CI for it.

## Results

Not started.
