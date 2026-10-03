# Follow-through on the promotion and tour reviews

**Status:** done

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
- the recorder tests pass however pytest-xdist distributes them among the rest of the default tier, because none of
  them writes into the real `replays/` tree and, as measured at this card's head, no other test of that tier does;
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

- [x] Review correction (round 2): every claim of the README caption's scene is read out of the caption and held to
  the served replay. `_caption_scene_problems` takes the tick, the number of dead (a word), the room the impostor
  outside the vents stands in (by the map's own room name), the fog subject, the one player it sees and the accuser
  from the caption line. It holds the tick to the capture spec's `HERO.tick`, each claim to the frame at that tick,
  and the accusation to the earliest meeting after it. Before, the case compared the replay to literal copies of the
  tick, count and room, so the verifiers' edits of MedBay to Admin, two players to three and tick 9 to tick 12 left
  the file green (13 passed each at `c6e98fef`). Mechanism: `test_the_captions_scene_is_the_recorded_one`,
  `test_a_caption_naming_another_scene_fails_by_name` and `test_the_caption_counts_its_dead_in_words` in
  `tests/scripts/test_public_recording_provenance.py`. Proof: seven scratch READMEs, each with one scene phrase
  changed, and a scratch spec shooting another tick each fail by name; the three edits applied to the real README
  now fail the scene case (Results, Review corrections, round 2).
- [x] Review correction (round 1): no test of the default tier writes into a committed set directory, so the
  recorder tests' whole-tree fixture fails only on a real write into `replays/`. The feature sweep in
  `tests/agents/test_features.py` wrote its observation audit log beside each recording in `replays/samples/<set>/`
  and removed it again, and the fixture reported it from a recorder case running beside it (181 passed, 16 errors for
  the pair under `-n 2 --dist loadfile` at `878d05db`). The sweep now writes that log in a temporary directory.
  Mechanism: `test_the_sweep_leaves_the_committed_set_directory_untouched`. Proof: the log put back beside the
  recording fails it; the pair under `-n 2 --dist loadfile` reads 182 passed in each of three runs; the whole default
  tier between two stat inventories of `replays/` changes none of its 386 entries (Results, Review corrections,
  round 1).
- [x] Review correction (round 1): the distribution guarantee is stated at the strength delivered, in the Outcome,
  this list and Results. The recorder tests pass under any distribution of the default tier because none of them
  writes into `replays/` and, measured at this card's head, no other test of the tier does. A future test that writes
  there would turn a concurrent recorder case red, and the fixture names its path. Mechanism: the autouse fixture
  `_replays_tree_untouched` and the inventory run in Results. The bounded mutation pass over the inventory found one
  survivor, the directory test negated; the new planted kind "a rewritten file with its time put back" in
  `test_the_no_trace_checks_report_a_stray_of_each_kind` kills it.
- [x] Review correction (round 1): every live comment that states the 9p2i eval report's size agrees with
  `docs/deployment.md` and with the measured bytes. `frontend/src/api/client.ts` and `frontend/e2e/bundle.spec.ts`
  said 29 MB, and `scripts/build_demo_bundle.py` said 33.86 MB uncompressed and 2.89 MB gzipped, which are binary
  megabytes of the report before the promotion. They now say 33 MB, and the docstring gives the bytes. Mechanism:
  these are comments that no test holds; the commands that measure them are in Results. Proof:
  `git grep -n -E "29 ?MB|33\.86|2\.89 ?MB"` outside `tasks/` and `audits/` finds none, and bundles built in one
  checkout at `878d05db` and at this round's code head give an empty `diff -rq`.

- [x] **The before file is registered.**
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
- [x] **The front door names the pictured game in plain words.**
  - `README.md`'s caption, its samples sentence and `docs/media/README.md` call 9p2i seed 19 the game the demo's
    guided tour opens on, or other plain words a first reader understands. None says "strip" or "head".
  - The caption says one impostor is inside a vent, and the README stays at or under 1,600 words.
  - Mechanism: `tests/scripts/test_public_recording_provenance.py`. Its caption pin holds the new words, and a new
    assertion refuses "strip's head" and "featured head" in both files. `tests/api/test_sets.py:669` holds the
    claim itself true.
  - Planted: the `59bbd1be` caption, put back into a scratch README, fails that assertion by name.
  - `tests/scripts/test_check_doc_facts.py`'s planted `d41c9006` hunk carries the new sentence as its current side.
    Its previous side is unchanged, and the case still passes all four of its assertions.
- [x] **The hero caption claims only what the picture shows.**
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
- [x] **The public results page calls adopted rules adopted.**
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
- [x] **The recorder's era refusal stays registry-derived.**
  - Mechanism: `test_an_era_refusal_names_the_set_and_the_declared_file_it_found`.
  - Proof: D10 re-applied at dispatch fails it for both variables, and Results quotes the run.
  - Only if D10 survives does this card add a planted-registry case to `tests/scripts/test_refresh_samples.py`.
    `scripts/_declared_experiment.py` does not change.
- [x] **The recorder tests pass under any distribution of the default tier.**
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
- [x] **Both merged cards carry a dated note in Results, and nothing above it changes.**
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
- [x] **Every changed production line goes red when neutered, and one bounded mutation pass is run.**
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
- [x] **The gates hold.**
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

Done on `work/post-promotion-follow-through`, from `origin/main` at `5877adb4`. Every count is count-only: no rendered
prompt, transcript text or seed-band prefix was printed or logged. Scratch work stayed under a private subdirectory
of the session scratchpad.

**Commits**, in order: `acdaddb6` the front-door words and the hero caption template; `52c4b1f3` the public results
wording; `c91e604b` the media re-capture; `a74045b3` the recorder tests off the shared tree; `e5403bb0` the M14
numerator pin; `dd1a4b17` the deployment figure; `cd77b998` the two dated notes; `d392b108` the probes the first pass
left green; `e35b052f` the registry rows with this Results; then the commit recording the `check.sh` run.

**Sections relied on.** This card; `AGENTS.md`; `docs/workflow.md` (card format, reopen pattern); the Stage B
decision memo (`tasks/decision-2026-09-24-stage-b-wave.md`) sections 0, 1, 3.1-3.3 and 7; the diagnosis
(`tasks/diagnosis-2026-10-02/README.md`) Part 3, card 0, and Part 4; `audits/audit-2026-10-01-stage-b-r2.md` sections
1.11 and 9; `docs/experiment-arms.md` "Adopted arms"; `docs/artifacts.md` "The four classes"; `docs/media/README.md`;
`docs/architecture.md` "Determinism and the substrate ladder" (unchanged: no engine, agent, meeting or recorded
byte moves).

### The before file is registered

- `docs/artifacts.md`'s scorecard row names `docs/process-scorecard-before.json` as the frozen before columns,
  sha256-pinned in `eval/process_scorecard.py`, copied into every publication and never recomputed, and states
  `3 files`. `_IN_TREE_PROBES` and `_IN_TREE_INVENTORY` name the three paths; the scratch availability tree links all
  three.
- Mechanism (`tests/scripts/test_verify_ml_evidence.py`): `test_the_scorecard_row_registers_its_pinned_before_file`
  reads `BEFORE_COLUMNS_PATH` off `eval.process_scorecard` at call time and requires it in the row's words, its probe,
  its inventory scope and the index, and the row's count to equal the index.
- Written first, red at the base (`pytest tests/scripts/test_verify_ml_evidence.py -k "scorecard_row or before_path or
  before_file"`): 3 failed, 1 passed (the registration case, the two planted inventory cases; the moved-path case
  passes at both commits).
- Planted: the row restated as `2 files` reads "docs/process-scorecard.md: docs/artifacts.md promises 2 files, the
  index tracks 3"; the scope without the before file reads "promises 3 files, the index tracks 2";
  `BEFORE_COLUMNS_PATH` monkeypatched to another path fails the case with four named problems.
- `uv run python scripts/verify_ml_evidence.py` (offline): 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5, as before.

### The front door names the pictured game in plain words

- `README.md`'s caption and samples sentence and `docs/media/README.md` call 9p2i seed 19 the game the demo's guided
  tour opens on (`tests/api/test_sets.py` pins it as the featured list's first entry). The caption says one impostor
  stands in MedBay and the other is inside a vent. `wc -w README.md`: 1,579 (budget 1,600, held by
  `check_doc_facts.py`).
- Mechanism (`tests/scripts/test_public_recording_provenance.py`): the caption pin holds the new words;
  `test_the_front_door_names_the_pictured_game_in_plain_words` refuses the words strip and head in both pages and
  requires the vent clause; `test_the_captions_scene_is_the_recorded_one` reads the tick, the number of dead, the
  room, the fog subject, the player it sees and the accuser out of the caption and holds each to the served replay
  at the tick the capture spec shoots, because the capture harness checks only that both impostors are alive in a
  room. Until review round 2 the case compared the replay to literal copies of the tick, count and room instead.
  `acdaddb6`'s message said the harness checks the vent; `c91e604b` corrects it.
- Red at the base: 3 failed, 9 passed (the caption pin, the front-door case, the caption case). Planted: the
  `59bbd1be` caption in a scratch README is reported as `["README.md"]`; the `59bbd1be` scene, both impostors in
  rooms, fails with "says one impostor is inside a vent, the replay has 0" (the message since review round 2).
- `tests/scripts/test_check_doc_facts.py`'s planted `d41c9006` hunk carries the new samples sentence as its current
  side; its previous side is unchanged and `test_the_d41c9006_front_door_fails_on_the_promoted_tree` passes all four
  of its assertions.

### The hero caption claims only what the picture shows

- `frontend/e2e/media.spec.ts`: "Left: what happened at tick 9. Right: what p-5 could see at the same tick. Below: the
  accusation p-5 wrote at the meeting that followed, at tick 12.", from `HERO.tick`, `HERO.fogSubject` and
  `HERO.meetingTick`. The right-half comment and the HERO comment say the same.
- Mechanism: `test_the_hero_caption_claims_only_what_the_picture_shows` reads the template out of the spec, refuses
  "when it voted" and "allowed to know" anywhere in it, requires both tick placeholders, and pins the whole template.
  Planted: the `59bbd1be` caption and comment fail with all four named problems.
- Re-capture, by the documented command (`cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test
  e2e/media.spec.ts`), twice at `52c4b1f3`: both runs gave the two-truths sheet `a921c55c`, the meeting still
  `2da7cab6` and the GIF `80dc7add` (13 frames, 640x400); the clip differs run to run as documented, and the second
  run's ships (`2119ce78`, 1440x900, 9.00 s). `provenance.json` names capture revision `52c4b1f3` and the four new
  digests; the recording and its sha256 are unchanged. `shasum -a 256 docs/media/*.png docs/media/*.gif
  docs/media/*.webm` equals `provenance.json`. Both stills keep their documented sizes (2036x864, 1440x900).
- The meeting still and the GIF are not byte-identical to the `8d07a340` capture, and this card is not why. Captured
  through `AILIBI_DEMO_BUNDLE_DIR`, one bundle per revision built in this checkout: the `8d07a340` bundle reproduces
  the committed still (`c827b6ac`) and GIF (`0a5aa048`) exactly; the `5877adb4` base bundle gives this head's new
  digests. They moved with the viewer between those commits (the tour's review round 1 reworded the regroup note the
  map draws).
- Planted: before `provenance.json` moved, the re-captured images failed the existing digest check, naming all four
  assets.

### The public results page calls adopted rules adopted

- Every word of the recorded-behavior group is in the new `publicResults` group of `SPECTATOR_COPY`, with `fmt`
  templates for counts. A field is listed under "Rules adopted for the current game:" only at one of the seven pairs
  in `frontend/src/lib/adoptedRules.ts`; `own_fresh_kill` reads "impostors enter a vent only beside a body they have
  just killed" (the look-and-wait card's Outcome) and `hub_with_grace` reads "after each meeting, the survivors start
  again from the meeting room with the bodies cleared" (the glossary's regroup). The kept vent exit and a recorded
  kill cooldown ("a kill cooldown of N ticks set for these recordings", unchanged) are listed under "Also in place:".
  Any other value off its default keeps an experiment label; a default group keeps "No enabled experiments recorded.
  This alone does not certify the default behavior."; the `experimental` factory kind reads "Built-in agents with
  recorded tactical settings".
- On the shown set's declared config, read off disk, the rendered results section carries no form of "experiment"
  and none of "arm", "regroup", "era" or "Stage-B".
- Mechanism: `adoptedRules.test.ts` reads the paragraph's adoption sentence and the declared config off disk and
  requires the list to equal the paragraph's seven pairs, in order, each held by the config. Planted: the paragraph
  with `meeting_reset = preserve` and a config copy with `vent_entry_policy = any_body` each fail the pin.
- Exhaustive enumeration (`PublicResults.test.tsx`): 128 on/off combinations of the seven fields, times the three vent
  exits, times a cooldown set or unset (768), each also with one non-default value of each of eleven other fields
  (orchestrator ruling 2): 9,216 renders. In none is an adopted value called an experiment or left out, and in none is
  a value outside the seven called adopted.
- Changed assertions: each old one is replaced by one at least as strong, with the old phrase asserted absent where its
  classification changed ("Recorded experiments: a kill cooldown", "Recorded experiments: experimental movement or
  action policies.", "Experimental agent factory").
- `copy.test.ts`: `PublicResults.tsx` joins the disk leg's sources with the rendered fragment "What the recordings
  show"; a new case requires the recorded-behavior span to carry no prose literal, with a planted literal and a
  planted text node caught.
- Red at the base (the new test files over a `git archive` of `5877adb4`'s frontend): `adoptedRules.test.ts` fails to
  import its module; `PublicResults.test.tsx` 5 failed of 11; `copy.test.ts` 2 failed of 268.

### The recorder's era refusal stays registry-derived

D10 re-applied (`config=declared` in the wrong-config refusal replaced by
`'replays/samples/9p2i/experiment-config.json'`): `uv run pytest tests/scripts/test_refresh_samples.py -k
"era_refusal_names_the_set or declared" -q` read 2 failed, 11 passed, both variables of
`test_an_era_refusal_names_the_set_and_the_declared_file_it_found`. The file was restored from a copy (sha256
`c97f4c87...` before and after). `scripts/_declared_experiment.py` does not change; no case was added.

### The recorder tests pass under any distribution of the default tier

- No case writes into the real `replays/` tree while the guard it tests holds. The symlink cases link from `tmp_path`
  to the committed `replays/samples/4p1i`, read only, and aim at a directory below it of their own unique name; the
  switched-on config family compares the bytes of each committed directory it is aimed at; the round case aims read
  only at the committed `stage-b-r1`, and its planted twin plants a round under `tmp_path` and runs the rule over that
  scratch repository; the replays-target cases fill their absent names per run.
- The autouse fixture `_replays_tree_untouched` (orchestrator ruling 3) compares a stat inventory of `replays/` (kind,
  size, modification time, the tree root included) before and after every case and fails naming any difference.
  `test_the_no_trace_checks_report_a_stray_of_each_kind` plants each kind of stray on a scratch tree (a set below a
  committed set, a stage directory, a round, a set inside a round, a top-level path, a rewritten file, a decoy made
  and removed) and the inventory reports each one.
- Red at the base: the base file with only the fixture added, serially: 154 passed, 4 errors, exactly the symlink
  decoy, the composed decoy, the switched-on config's decoy and the planted round.
- Perturbed: one decoy restored under `replays/samples/` turns `-n 6 --dist load` red, 162 passed with 8 errors and 162
  passed with 9 errors in two runs, each error naming `samples/.test-symlink-decoy`.
- Runs (`git status --porcelain --ignored -- replays` empty after every one):

| command | result |
| --- | --- |
| `test_refresh_samples.py -n 4 --dist load`, three runs | 162 passed each (28.5 s, 30.3 s, 27.8 s) |
| `test_refresh_samples.py -n 6 --dist load`, three runs | 162 passed each |
| both files `-n 8 --dist load`, the first three runs | 191 passed, 191 passed, then 1 failed and 190 passed (failure not captured, see Limitations) |
| both files `-n 8 --dist load`, fifteen further runs with `-rfE` (three under a concurrent `-n 4` watchability run) | 191 passed each |
| both files `-n 2 --dist loadfile` | 191 passed |
| both files serially | 191 passed |

- The box is checked on the triples above that are green; the one red `-n 8` run is disclosed under Limitations, at
  the strength measured: 17 of 18 both-file `-n 8` runs green.
- `tests/scripts/test_record_ml_corpus.py`'s one decoy case made `replays/ml_corpus/.test-corpus-decoy`, which a
  concurrent refresh case would now report; it links to the committed `replays/ml_corpus/4p1i`, read only, and names
  a directory below it of its own (Deviations). That file: 109 passed under `-n 6`.

### Both merged cards carry a dated note

`### Follow-through note (2026-10-02)` closes each card's Results. `git diff --numstat 59bbd1be --
tasks/work/promote-round-2.md tasks/work/spectator-tour-round-2.md`: 55 0 and 27 0. Re-measured at this head:

| figure | command | reading |
| --- | --- | --- |
| referee JSON | `uv run python scripts/measure_baseline.py --watchability --json <set>` | 21,981 B `badba42d` (`samples/4p1i`); 64,432 B `bc574592` (`ml_corpus/9p2i`); 22,088 B `79055133` (`ml_corpus/4p1i`); exit 0 each |
| re-pin notes | `git diff d41c9006 4a36dc03 -- tests/ frontend/src/ \| grep -c was`; `\| grep -cE '^\+.*(#\|//) was'`; the same with a trailing space | 1,325; 530 across 39 files; 529 |
| criterion | `measure_featured_criterion.py --set 9p2i`; `--games 9p2i:3`; `--games 9p2i:23` | 11 of 50; 1 of 1; 0 of 1; exit 0 each |
| tour grep | `git grep -n "every meeting ends\|survivors gathered" 59bbd1be` | 5 lines: 3 in `regroup.test.ts` (`:135`, `:162`, `:165`), 2 in the tour card (`:809`, `:816`) |
| M14 | witnessed-kill numerator raised to 15 | earlier stage suite 6 passed; the new case fails |
| D10 | above | 2 failed, 11 passed |

The red-at-base counts (15 errors, 5 of 32) are marked unreproduced.

### M14 and the deployment figure (orchestrator ruling 5)

- `test_stage_b_r2_floor_numerators_equal_the_measured_counts` (`tests/eval/test_watchability.py`) reads the
  `SupplyGaugeValues` the referee's walk hands `evaluate_supply_floors` on `replays/samples/9p2i` and requires each of
  the five stage pins' numerators to equal its count (14, 53, 44, 15, 38). Planted: each numerator moved by one, its
  value unchanged, fails by name. The mutant (numerator 15) passes the earlier stage tests (`-k "(stage_b_r2 or
  stage_pin) and not numerators"`: 6 passed) and fails the new case; numerator 13 is also caught by the existing
  raised-by-one case. `eval/watchability.py` was restored from a copy (sha256 `e3720555...` before and after).
- `docs/deployment.md:127` reads 33 MB: `gzip -dc replays/samples/9p2i/tournament-eval-report.json.gz | wc -c` reads
  32,952,472 bytes. The bundle built in this checkout (`scripts/build_demo_bundle.py --out`) holds no
  `tournament-eval-report` file and measures 3.1 MB.

### The neuter pass

Each changed production line neutered alone, its targeted suite run (`vitest` over `PublicResults.test.tsx`,
`adoptedRules.test.ts` and `copy.test.ts`; `test_verify_ml_evidence.py -n 6`; `test_public_recording_provenance.py`),
the file restored from a copy with its sha256 checked:

| ids | span | probes | killed |
| --- | --- | --- | --- |
| N1-N23 | `PublicResults.tsx`: the null guard, the adopted filter, each set-for-recordings and experiment push, the return, the factory table and lookup, the count, the nothing-recorded test, each rendered line | 23 | 23 |
| C1-C35 | the `publicResults` copy group: each leaf, and the export | 35 | 35 |
| A1-A8 | `adoptedRules.ts`: each of the seven rows, and `holdsAdoptedValue` | 8 | 8 |
| V1-V2 | `verify_ml_evidence.py`: the before file in the probe entry and in the inventory scope | 2 | 2 |
| S1-S3 | `media.spec.ts`: each caption template line | 3 | 3 |

71 of 71 killed. Run against the tests as committed in `52c4b1f3` and `c91e604b`, before `d392b108`, four probes
first came back green: S2 (the caption's middle line deleted) and the mutants M26, M27 and M29 below. `d392b108`
pins the whole caption template and renders a recorded tactical policy; all four are killed now. M35 was already
killed there.

### One bounded mutation pass

Exactly the eight listed classes, over the spans above; each mutant applied alone, its targeted suite run, the file
restored from a copy with its sha256 checked.

| id | class | mutant | result |
| --- | --- | --- | --- |
| M1 | drop a filter or wrapper on a collection | the adopted filter dropped | killed |
| M2 | drop a filter or wrapper on a collection | `Object.freeze` dropped from `ADOPTED_RULES` | equivalent: nothing writes to the list, and `as const` keeps it read-only to the compiler |
| M3 | swap one collection for a related one | the adopted line joins `setForRecordings` | killed |
| M4 | swap one collection for a related one | the set-for-recordings line joins `experiments` | killed |
| M5 | swap one collection for a related one | the scorecard probe entry holds the census pair | killed |
| M6 | swap one collection for a related one | the scorecard inventory scope holds the census pair | killed |
| M7 | comparison to its inverse | `vent_exit_policy === "look_and_wait"` to `!==` | killed |
| M8 | comparison to its inverse | `kill_cooldown_ticks != null` to `== null` | killed |
| M9 | comparison to its inverse | `kill_cooldown_ticks === 1` to `!== 1` | killed |
| M10 | comparison to its inverse | `!== "target_distance"` to `===` in the movement clause | killed |
| M11 | comparison to its inverse | `!== "look_and_wait"` to `===` in the movement clause | killed |
| M12 | comparison to its inverse | `redistribution_policy !== "lowest_id"` to `===` | killed |
| M13 | comparison to its inverse | `crew_idle_policy !== "hub_wait"` to `===` | killed |
| M14 | comparison to its inverse | `sabotage_threshold !== "six_sevenths"` to `===` | killed |
| M15 | comparison to its inverse | `holdsAdoptedValue`'s `===` to `!==` | killed |
| M16 | comparison to its inverse | `if (!config)` to `if (config)` | killed |
| M17 | comparison to its inverse | `adopted.length > 0` to `=== 0` | killed |
| M18 | comparison to its inverse | `count === 1` to `!== 1` | killed |
| M19 | a kind read to a constant | the factory kind read as `"experimental"` | killed |
| M20 | a tick read to a constant | the cooldown ticks read as `"6"` | killed |
| M21 | a tick read to a constant | the caption's `HERO.tick` as `9` | killed |
| M22 | a tick read to a constant | the caption's `HERO.meetingTick` as `12` | killed |
| M23 | a message argument to a constant | the adopted rules argument as `""` | killed |
| M24 | a message argument to a constant | the recording count as `"1"` | killed |
| M25 | a message argument to a constant | the evidence version as `"1"` | killed |
| M26 | a message argument to a constant | the impostor policy as "not recorded" | killed (first green) |
| M27 | a message argument to a constant | the crew policy as "not recorded" | killed (first green) |
| M28 | a message argument to a constant | the clock version as `"1"` | killed |
| M29 | a message argument to a constant | the caption's fog subject as `p-5` | killed (first green) |
| M30 | drop one member of a tuple of kinds | the `vent_entry_policy` row | killed |
| M31 | drop one member of a tuple of kinds | the `scripted` factory label | killed |
| M32 | drop one member of a tuple of kinds | `process-scorecard.json` from the inventory scope | killed |
| M33 | swap adjacent branches | the recording count's one and many | killed |
| M34 | swap adjacent branches | the cooldown's one and many | killed |
| M35 | swap adjacent branches | recorded and not-recorded rule settings | killed |
| M36 | swap adjacent branches | the clock's not-recorded and version | killed |
| M37 | a read of a loaded source to the canonical literal | the group's game count as 50 | killed |

36 killed, 1 equivalent. No other class was run.

### Validation

| command | result |
| --- | --- |
| `uv run python scripts/verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `pytest tests/scripts/test_verify_ml_evidence.py tests/scripts/test_public_recording_provenance.py tests/scripts/test_check_doc_facts.py` | 0: 428 passed (`-n 6`) |
| `uv run python scripts/check_doc_facts.py`; `uv run python scripts/validate_task_docs.py` | 0; 0 (96 work cards before this card's flip) |
| `wc -w README.md` | 1,579 |
| the re-capture, twice; `shasum -a 256` against `provenance.json` | 3 passed each; equal |
| `npm run lint`, `tsc:check`, `test`, `build` (frontend) | 0; 0; 0: 26 files, 695 tests; 0 |
| `npm run e2e` (local, serial, `CI=1`) | 0: 14 passed, 3 skipped (the media spec's, without its capture switch) |
| `bash scripts/verify_samples.sh`; per set | 0 (50 clean); `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i`: 0 each (50, 50, 150, 50, 50) |
| `build_sample_report.py --check`, the five sets | 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `uv run pytest -m campaign` | 0: 337 passed, as at `59bbd1be` |
| bundle `build_demo_bundle.py --out` at `5877adb4` and at `52c4b1f3`, one checkout, `diff -rq` | `data/` identical; only the seven hashed JS assets and `index.html` differ |
| `git diff --numstat 59bbd1be` over the two merged cards | 55 0; 27 0 |
| `bash scripts/check.sh`, once at the pushed head `e35b052f`, exit code read directly | 0: 10,061 passed, 20 skipped, 3 xfailed; import contracts 4 kept; mypy clean over 522 files; vitest 26 files, 695 tests; frontend build ok. The commit that records this row changes only this card |

### Decisions

1. Orchestrator ruling 1: Q1 stays open for the owner exactly as the card states. The promotion's note quotes the
   owner's words verbatim, records that the code holds option (a) and that the twelve commits stand as pushed.
2. Orchestrator ruling 2: the page calls adopted only the seven pairs of `docs/experiment-arms.md`'s Adopted arms
   paragraph. `vent_exit_policy = look_and_wait` and the kill cooldown are named as set for these recordings, never as
   adopted or experimental. The enumeration repeats every one of the 768 renders with one non-default value of each
   of the eleven other config fields.
3. Orchestrator ruling 3: the xdist race gets the deterministic guard, the autouse inventory fixture, plus the three
   `-n 4 --dist load` runs above.
4. Orchestrator ruling 4: Record impact names the replaced media and the moved `docs/media/` row (below).
5. Orchestrator ruling 5: M14 and the `docs/deployment.md:127` figure are this card's. M14 is pinned in the test that
   owns the stage pins, so the promotion's note records M14 closed; the card's "Q1 and M14 open" sentence predates the
   ruling. The figure is the 9p2i report's size, which the bundle leaves out, so it is measured from the report; the
   one-checkout bundle confirms the exclusion.
6. The new copy lead for settings kept but not adopted reads "Also in place:"; each such setting's own words end "set
   for these recordings", which keeps the cooldown's words unchanged.
7. The front-door check refuses the words strip and head in both pages outright, stronger than the two phrases the
   card names; neither page uses either word otherwise.
8. A recorded tactical policy's method, and recorded rule settings, are now asserted; before, no case rendered them.

### Record impact

- No recorded byte, manifest, report, census, scorecard output or ML artifact moves; no prompt byte or experiment field
  changes; no evaluation moves.
- Replaced, class (a), by the documented re-capture only: `docs/media/spectator-two-truths.png`,
  `spectator-meeting.png`, `spectator-journey.gif`, `spectator-journey.webm` and `docs/media/provenance.json`.
- `docs/artifacts.md`: the scorecard row gains its third file (3 files); the `docs/media/` row's rounded size moves from
  1.6 MB to 1.4 MB (1,406,205 tracked bytes, was 1,575,772; the clip is smaller), 7 files.
- What changes for a reader: the public results card's words for recorded settings and the factory label (in the
  bundle's JS); the README caption and samples sentence and the hero picture's caption (on the front door). Older
  payloads render as before except for that wording; no DTO changes.

### Limitations

- One run of the both-files `-n 8 --dist load` command failed one case; its name was not captured (the runner kept
  only the summary line). The replays/ status was clean after it, and fifteen further runs with failure reports,
  three under extra load, were all green, so the case and cause are unidentified.
- The promotion's red-at-base counts stay unreproduced.
- The capture harness still checks only that both impostors stand in a room; the caption's room and vent clauses,
  with the rest of its scene, are held by the Python scene cases instead, which read them out of the README.
- On macOS the evolution-strategy hash pin is Linux-only; CI is cited for it if `check.sh` reports it.

### Deviations

- `tests/scripts/test_record_ml_corpus.py` is outside Expected scope: its one decoy case made a directory in the real
  `replays/ml_corpus/`, which the ruled autouse fixture in `test_refresh_samples.py` would report from a concurrent
  case under `check.sh`'s `--dist loadfile`. The change is that case alone, reviewed by the orchestrator in the PR.
- `tests/eval/test_watchability.py` and `docs/deployment.md` are outside Expected scope by orchestrator ruling 5.
- `acdaddb6`'s message overstated what the capture harness checks; `c91e604b` corrects it, and no pushed commit is
  rewritten.

### Review corrections, round 1 (2026-10-02)

Three blocking findings from the round-1 verifiers, and the PR's three Codex comments. Commits: `32501b6a` the feature
sweep off the committed sets; `494a7599` the report-size comments; `374f217f` the planted kind the mutation pass
asked for; then this record and the commit recording `check.sh`. Every count is count-only.

**Findings 1 and 2 (correctness; integrity): the fixture failed the recorder tests beside the feature sweep.**

- Cause: `tests/agents/test_features.py::_iter_committed_packets` wrote its observation audit log as
  `_sweep_audit_replay-seed-N.jsonl` beside each recording in `replays/samples/<set>/` and deleted it on close. The
  autouse fixture `_replays_tree_untouched` saw the file, or the set directory's moved modification time, from any
  recorder case running at the same moment.
- Reproduced at `878d05db`: `uv run pytest tests/agents/test_features.py tests/scripts/test_refresh_samples.py -n 2
  --dist loadfile -q -p no:cacheprovider` read 181 passed, 16 errors.
- Fix (`32501b6a`): the sweep writes its audit log in a temporary directory, as the committed-set walk in
  `tests/_helpers/committed.py` does. The fixture's docstring now says a difference can also come from a test in
  another file writing beside it, and that the paths it names show which.
- Mechanism: `test_the_sweep_leaves_the_committed_set_directory_untouched` (`tests/agents/test_features.py`) holds
  `replays/samples/4p1i`'s listing while the walk is open and its modification time after the walk closes.
- Planted: with the audit log put back beside the recording, the case fails; the open walk lists
  `_sweep_audit_replay-seed-0.jsonl`. The file was restored from a copy (sha256 `c640c0e2...` before and after), and
  the one stray the planted run left was removed; `git status --porcelain --ignored -- replays` was empty after.
- Runs, `git status --porcelain --ignored -- replays` empty after each. The pair ran on the tree committed as
  `32501b6a` (one comment in the new case was reworded while they ran); the default tier ran at `374f217f`:

| command | result |
| --- | --- |
| the pair above under `-n 2 --dist loadfile`, three runs | 182 passed each (190.98 s, 227.17 s, 151.09 s) |
| the whole default tier as `check.sh` runs it (`uv run pytest -n auto --dist loadfile`), between two stat inventories of `replays/` (kind, size and modification time of every entry, the root included) | exit 0: 10,063 passed, 20 skipped, 3 xfailed; 386 entries before and after, 0 changed |

- The guarantee, restated at the strength delivered: the recorder tests pass under any distribution of the default
  tier, because none of them writes into `replays/` while its guard holds and, measured at this head by the inventory
  run above, no other test of the tier does either. The fixture is not a property over every possible future test:
  a test that writes into `replays/` would turn a concurrent recorder case red, and the path the fixture names would
  identify it. The Outcome bullet, the Acceptance item and the Results heading above now say "of the default tier".
- The one red `-n 8` run under Limitations involved only `test_refresh_samples.py` and `test_candidate_sets.py`, not
  the feature sweep, so this cause does not explain it; it stays unidentified.

**Finding 3 (docs; the Codex P2): the report's size was corrected in one place and stale in three.**

| file | was | now |
| --- | --- | --- |
| `frontend/src/api/client.ts` (the `getTournamentReport` comment) | 29 MB | 33 MB |
| `frontend/e2e/bundle.spec.ts` (the compact-results case's comment) | 29 MB | 33 MB |
| `scripts/build_demo_bundle.py` (the module docstring) | 33.86 MB uncompressed, 2.89 MB gzipped; ML corpus 102.70 MB | 32,952,472 bytes uncompressed, about 33 MB, and 2,790,383 bytes gzipped; ML corpus 107,690,098 bytes |

- Measured at this head: `gzip -dc replays/samples/9p2i/tournament-eval-report.json.gz | wc -c` reads 32,952,472;
  `ls -l` gives the `.gz` as 2,790,383 bytes; `gzip -dc replays/ml_corpus/9p2i/tournament-eval-report.json.gz | wc -c`
  reads 107,690,098.
- The old docstring figures were binary megabytes of the pre-promotion report: `git show
  d41c9006:replays/samples/9p2i/tournament-eval-report.json.gz` is 3,027,379 bytes (2.89 MiB) and 35,500,305
  uncompressed (33.86 MiB). `docs/deployment.md`'s 33 MB is decimal, so the docstring now gives bytes, which no reader
  can take in the other unit. `docs/artifacts.md` and `eval/report_io.py` keep 102.70 MB for the ML corpus report,
  which is the binary figure GitHub's 100 MB limit is measured in; neither is in this card's scope.
- Mechanism: these are comments, and no test holds them. `git grep -n -E "29 ?MB|33\.86|2\.89 ?MB"` outside `tasks/`
  and `audits/` now finds none.
- Comment-only, so no shipped byte moves: bundles built in this one checkout at `878d05db` and at `494a7599` give an
  empty `diff -rq`. `374f217f` and the card commits change only tests and this card.

**The Codex comments.**

- P2, "Synchronize the remaining report-size claims": valid; it is finding 3, fixed above.
- P1, "Keep the cited capture revision reachable": not valid for this PR. Codex reviewed a synthesized squash
  (`5b523696`, one parent, `5877adb4`). On the branch, `git merge-base --is-ancestor 52c4b1f3 HEAD` exits 0, and
  AGENTS.md's delivery rule merges by merge commit or fast-forward, never squash. So `52c4b1f3`, the capture revision
  `docs/media/provenance.json` names, stays reachable from `main` after the owner's merge. No change.
- P1, "Record the full-gate result before marking the card done": valid at `e35b052f`, the head Codex reviewed.
  `878d05db` recorded that run (exit 0), and this round's last commit records the run at this round's head.

**The bounded mutation pass**, over the spans this round changes and the spans the findings name (the sweep's audit
path and the inventory behind the fixture). The listed classes only; each mutant applied alone, its targeted case run,
the file restored from a copy with its sha256 checked.

| id | class | mutant | killed by | result |
| --- | --- | --- | --- | --- |
| P1 | swap one collection for a related one | the sweep's audit directory, the temporary one, back to the recording's set directory, `replay_path.parent / f"_sweep_audit_{replay_path.stem}.jsonl"` | `test_the_sweep_leaves_the_committed_set_directory_untouched` | killed |
| FM1 | swap one collection for a related one | the inventory walks `files` only | the planted stray kinds: 6 of 8 fail | killed |
| FM2 | swap one collection for a related one | the inventory walks `subdirectories` only | 2 of 8 fail | killed |
| FM3 | comparison to its inverse | `before.get(path) != after.get(path)` to `==` | 8 of 8 fail | killed |
| FM4 | swap one collection for a related one | `before.keys() \| after.keys()` to `before.keys()` | 5 of 8 fail | killed |
| FM5 | comparison to its inverse | `stat.S_ISDIR(...)` negated | the new kind, a rewritten file with its time put back | killed (first green) |
| FM6 | swap adjacent branches | the link and directory tests swapped | none | equivalent: under `lstat` a symbolic link is never a directory, so the two tests are exclusive and their order cannot change an entry |

FM5 first came back green: it records a file by its modification time alone, and every planted kind moved a time.
`374f217f` adds the kind "a rewritten file with its time put back" (a committed file rewritten at a new size, its
modification time restored with `os.utime`), which only the size reports; the inventory as written reports it, and
FM5 fails it. 6 of 7 killed, 1 equivalent. No other class was run.

**Bundle diff, rebuilt for this round** (`scripts/build_demo_bundle.py --out`, at `5877adb4`, `878d05db` and
`494a7599` in this one checkout): `878d05db` against `494a7599`, `diff -rq` empty. `5877adb4` against `494a7599`,
`data/` identical; only the seven hashed JS assets and `index.html` differ, as before. The head bundle holds 109 files,
3,237 KiB. What goes live at the merge is unchanged by this round.

**Observed, not changed.** `frontend/e2e/bundle.spec.ts:170` says the bundle is about 8 MB of built output; the
bundle above measures 3,237 KiB. That comment is outside the findings, and this round leaves it for the orchestrator to
route.

**Validation at `374f217f`**, `git status --porcelain --ignored -- replays` empty after each:

| command | result |
| --- | --- |
| `uv run python scripts/verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `uv run python scripts/check_doc_facts.py`; `uv run python scripts/validate_task_docs.py` | 0; 0 (96 work cards) |
| `bash scripts/verify_samples.sh`, then once per set directory | 0; `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i`: 0 each (50, 50, 150, 50, 50 clean) |
| `build_sample_report.py --sample-dir <set> --check`, the five sets | 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `pytest tests/scripts/test_verify_ml_evidence.py tests/scripts/test_public_recording_provenance.py tests/scripts/test_check_doc_facts.py tests/scripts/test_build_demo_bundle.py -n 6` | 0: 459 passed |
| `uv run pytest -m campaign` | 0: 337 passed |
| `npm run lint`, `tsc:check`, `test` (frontend) | 0; 0; 0: 26 files, 695 tests |
| `CI=1 npm run e2e -- --workers=1` (local, serial) | 0: 14 passed, 3 skipped (the media spec's, without its capture switch) |
| `bash scripts/check.sh`, once at the pushed head `d49e0313`, exit code read directly | 0: ruff and format clean; import contracts 4 kept; mypy clean over 522 files; 10,063 passed, 20 skipped, 3 xfailed; vitest 26 files, 695 tests; frontend build ok. The `replays/` inventory around the run: 386 entries, 0 changed. The commit that records this row changes only this card |

**Decisions.**

9. The test-file writer into `replays/` is fixed at its source, as both findings prescribe, rather than narrowing the
   fixture to each case's own paths: the whole-tree fixture keeps catching a concurrent writer, which is what it is
   for.
10. `scripts/build_demo_bundle.py` states the report in bytes, so the binary-against-decimal megabyte ambiguity cannot
    reopen; the two one-line comments say 33 MB, as `docs/deployment.md` does.
11. The mutation pass's one non-equivalent survivor is killed with a new planted kind in the existing parametrized
    case, not by changing the inventory.

**Deviations, this round.** Each is outside Expected scope and outside this card's one-writer map; please confirm or
ask for a revert.

- `tests/agents/test_features.py`: the sweep's audit path and one new case, as findings 1 and 2 prescribe. No wave-1
  card's Expected scope names it (`census-reporter-base-rate`, `route-check-replay`), and `rubric-extractor-era` does
  not either.
- `frontend/src/api/client.ts`, `frontend/e2e/bundle.spec.ts` and `scripts/build_demo_bundle.py`: one comment or
  docstring passage each, as finding 3 prescribes. `rubric-extractor-era`, which dispatches after this card merges,
  edits other comment lines of `client.ts` (`:366-372`) and builds on these.

**Record impact, this round.** None: no recorded byte, media asset, manifest, report, census, scorecard output or ML
artifact moves, and no shipped byte moves (the bundle diff above). The registry rows this card set are unchanged.

### Review corrections, round 2 (2026-10-02)

One blocking finding from the round-2 verifiers. Commits: `bab91b5e` the scene read out of the caption; `faf2d316` the
media page's sentence on which check holds which claim; then this record and the commit recording `check.sh`. Every
count is count-only; the scene facts quoted below are agent ids, room ids and counts read off the served replay's
frames, never transcript text.

**The finding (correctness): the README caption's new scene words were not held by any test.**

- Cause: `test_the_captions_scene_is_the_recorded_one` compared the served replay to the literals `_HERO_TICK = 9`,
  `_HERO_ROOM = "MEDBAY"` and a body count of two, never to the caption, so its comment and this card's Results
  claimed more than it held.
- Reproduced: the `c6e98fef` test file against each of the verifiers' three edits to `README.md` (MedBay to Admin,
  two players to three, tick 9 to tick 12), `uv run pytest tests/scripts/test_public_recording_provenance.py -q -p
  no:cacheprovider`: 13 passed each. The README and the test file were restored from copies, their sha256 checked.
- Fix (`bab91b5e`): `_caption_scene_problems(caption, replay, picture_tick)` reads every claim of the caption's scene
  clause out of the caption line, with one pattern of named groups, and holds each to the served replay:

| the caption's words | read as | held to |
| --- | --- | --- |
| at tick 9 | the tick | the tick the capture spec's `HERO` shoots, read by `_picture_tick`; the scene is the frame at that tick |
| two players lie dead | a count word, `no` to `nine` | the frame's bodies |
| one impostor stands in MedBay | the room, by the map's own name (`replay.map.rooms`) | the room of the living impostor outside the vents |
| and the other is inside a vent | (fixed words) | exactly one living impostor inside a vent |
| p-5 can see only p-4 | the fog subject and the player seen | the subject's visible players at that tick |
| whom p-5 accuses at the meeting that follows | the accuser | the accuser's accusations at the earliest meeting after the tick |

- `_readme_scene_problems(root, replay)` reads the caption from `root/README.md` and the tick from
  `root/frontend/e2e/media.spec.ts`, so the real tree and every scratch copy go through the same reads. A caption that
  does not match the pattern reads "the caption names no scene". The game stays `headless-seed-19`, which
  `test_media_hashes_and_labels_are_current` holds to the captured recording and to the caption's seed.
- The guarantee, at the strength delivered: each word of the caption's scene clause that the table names is read from
  the README and checked against the served replay in every run of the default tier. The fixed words of the clause
  (its grammar) are not variables: a caption that rephrases them names no scene and fails.

**Mechanism and planted proofs** (`tests/scripts/test_public_recording_provenance.py`, 31 cases, 13 before):

- `test_the_captions_scene_is_the_recorded_one`: the real README and spec read no problem. Planted: a scratch spec
  shooting tick 10 reads "names tick 9, the picture shows tick 10"; at the pictured tick, both impostors standing,
  both inside a vent, the venting impostor dead, or one body, each fail by name; the map's MedBay renamed fails the
  true caption with "names no room called MedBay" and passes a caption naming the new name; the meetings listed in
  reverse order still pass.
- `test_a_caption_naming_another_scene_fails_by_name`: seven scratch READMEs, each the real one with one scene phrase
  changed:

| case | edit | problems reported |
| --- | --- | --- |
| another-room | MedBay to Admin | says one impostor stands in Admin, the replay has ['MEDBAY'] |
| no-such-room | MedBay to Sickbay | names no room called Sickbay |
| another-count | two players to three players | says three players lie dead, the replay has 2 |
| another-tick | tick 9 to tick 12 | names tick 12, the picture shows tick 9; says one impostor stands in MedBay, the replay has ['ENGINEERING']; says p-5 accuses p-4 at the meeting that follows, the replay has [] |
| another-sighting | can see only p-4 to p-3 | says p-5 can see only p-3, the replay has ['p-4']; says p-5 accuses p-3 at the meeting that follows, the replay has ['p-4'] |
| another-subject | p-5 can see to p-3 can see | says p-3 can see only p-4, the replay has [] |
| another-accuser | whom p-5 accuses to whom p-6 accuses | says p-6 accuses p-4 at the meeting that follows, the replay has ['p-1'] |

- `test_the_caption_counts_its_dead_in_words`: each count word from `no` to `nine` holds on a frame with that many
  bodies and fails by name on one more (ten cases).
- `test_the_59bbd1be_caption_names_no_scene`: the `59bbd1be` caption reads "the caption names no scene".

**The verifiers' procedure, at `faf2d316`.** Each edit applied alone to the real `README.md`; `uv run pytest
tests/scripts/test_public_recording_provenance.py tests/scripts/test_check_doc_facts.py -n 4 -q -p no:cacheprovider`;
`uv run python scripts/check_doc_facts.py`; the README restored from a copy, sha256 `ec6608b0...` before and after:

| edit to `README.md` | the two files | `check_doc_facts.py` |
| --- | --- | --- |
| MedBay to Admin | 18 failed, 338 passed | 0 |
| two players to three players | 17 failed, 339 passed | 0 |
| tick 9 to tick 12 | 18 failed, 338 passed | 0 |
| can see only p-4 to p-3 | 18 failed, 338 passed | 0 |
| whom p-5 accuses to whom p-6 accuses | 18 failed, 338 passed | 0 |
| p-5 can see to p-3 can see | 18 failed, 338 passed | 0 |
| the room and vent clause to "both impostors are on the map" | 19 failed, 337 passed | 0 |

In every row `test_the_captions_scene_is_the_recorded_one` fails, through the same reads as the matching planted case
(the last row's caption names no scene, as the `59bbd1be` case's does). The planted cases fail too, because each
one edits the README it reads. The last row also fails the front-door case.
`check_doc_facts.py` holds the word budgets and citations, not the scene, so it stays 0.

**Follow-through (`faf2d316`).** `docs/media/README.md` said the capture harness checks "these scene and accusation
facts" against the served bytes. The harness checks the body count, the kill, how many players `p-5` can see and the
accusation; the room and the vent are held by the scene cases above. The paragraph now says which check holds which
claim. `git grep` for the old sentence finds no other live copy; `frontend/e2e/media.spec.ts`'s comment that the
Python file holds the caption's vent clause stays true and is unchanged.

**The bounded mutation pass**, over the spans this round changes and the span the finding names: the scene helpers in
`tests/scripts/test_public_recording_provenance.py`. The listed classes only; each mutant applied alone, the file's
scene cases run (`-k "scene or caption_counts or 59bbd1be_caption"`, 19 cases), the file restored from a copy with its
sha256 checked. Run at `bab91b5e`'s test file:

| ids | class | mutants | killed by |
| --- | --- | --- | --- |
| A1-A7 | drop a filter or wrapper on a collection | the impostor filter whole; its living clause; the outside-the-vents filter; the tick filter on frames; the after-the-tick filter on meetings; the accuser filter; the accusation type filter | A1, A3, A4, A7: the scene, naming and count cases; A2: the scene case alone; A5, A6: the naming cases alone |
| B1-B3 | swap one collection for a related one | visible players to visible bodies; bodies to events; the living impostors to every agent state | the scene, naming and count cases |
| C1-C16 | a comparison to its inverse or a None test | each comparison and membership test in the helpers, `_picture_tick`'s count included | the scene, naming and count cases; C14 also the `59bbd1be` case |
| D1-D5 | a role, kind, room or tick read to a constant | the caption's tick as 9; the role read as IMPOSTOR; the room id as MEDBAY; `_picture_tick` as 9; the meeting order key as 0 | D1, D3: the naming cases alone; D2: the scene, naming and count cases; D4, D5: the scene case alone (D5 first came back green) |
| E1-E7 | a message argument to a constant | the body count, the venting count, the standing rooms, the players seen, the accused, the unknown room, the picture's tick | E1: the scene and count cases; E2, E7: the scene case alone; E3: the scene and naming cases; E4, E5, E6: the naming cases alone |
| F1 | drop one member of a tuple of kinds or types | `three` from the count words | the count cases |
| G1 | swap adjacent branches | the seen list's two arms | the scene, naming and count cases |
| H1-H2 | a read of a loaded source to the canonical literal | the README read as the current caption; the spec read as 9 | H1: the naming cases alone; H2: the scene case alone (the scratch spec) |

42 of 42 killed. D5 (the meetings' minimum taken by a constant key) first came back green: the served replay lists its
meetings in tick order, so the first listed was also the earliest. The reversed-meetings plant kills it. The pass ran
42 mutants, two over the bound of 40 the orchestrator set; no other class was run.

**Bundle diff** (`uv run python scripts/build_demo_bundle.py --out <dir>`, at `c6e98fef` and then at `faf2d316`, in
this one checkout): `diff -rq` is empty; the head bundle holds 109 files. This round ships nothing: neither the test
file nor `docs/media/README.md` is a bundle input. What goes live at the merge is unchanged.

**Validation at `faf2d316`**, `git status --porcelain --ignored -- replays` empty after:

| command | result |
| --- | --- |
| `uv run python scripts/verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| `uv run python scripts/check_doc_facts.py`; `uv run python scripts/validate_task_docs.py` | 0; 0 (96 work cards) |
| `bash scripts/verify_samples.sh`, then once per set directory | 0; `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i`: 0 each (50, 50, 150, 50, 50 clean) |
| `build_sample_report.py --sample-dir <set> --check`, the five sets | 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `pytest tests/scripts/test_verify_ml_evidence.py tests/scripts/test_public_recording_provenance.py tests/scripts/test_check_doc_facts.py tests/scripts/test_build_demo_bundle.py -n 6` | 0: 477 passed (459 at `374f217f`, plus the 18 new cases) |
| `uv run pytest -m campaign` | 0: 337 passed |
| `uv run ruff format --check`, `ruff check`, `mypy` over the test file | clean |
| `bash scripts/check.sh`, once at this round's pushed head | recorded by the commit after this one |

No frontend file changes this round, so the frontend suites and the e2e are not re-run; `check.sh` runs vitest and the
build.

**Decisions.**

12. The scene is parsed into named claims rather than pinned as one sentence built from the frame, so a drifted
    caption fails with the claim that drifted, as the finding asks.
13. The caption's tick is held to the capture spec's `HERO.tick` as well as to the replay. A tick whose frame happens
    to carry the same scene would otherwise pass while the picture shows another.
14. The room is matched by the map's own room name from the served replay, so the caption's MedBay and the viewer's
    label are one source.
15. `docs/media/README.md`'s sentence on what the capture harness checks is restated in this round. It is this card's
    file, and it overstated the harness in the same way the finding names.

**Deviations, this round.** The mutation pass ran 42 mutants, two over the bound of 40. Each of this round's commits
ends with the attribution line the session's harness names, `Co-Authored-By: Claude Opus 5.5`, not the line the
orchestrator's brief gives.

**Record impact, this round.** No recorded byte, media asset, manifest, report, census, scorecard output or ML artifact
moves, and no shipped byte moves (the bundle diff above). `docs/media/README.md` is class (a) text: the directory's
tracked bytes move from 1,406,205 to 1,406,386, and the `docs/media/` row stays 1.4 MB / 7 files;
`verify_ml_evidence.py` (FAIL 0) and `tests/scripts/test_verify_ml_evidence.py` pass at this head.
