# Promote candidate round 3 as the shown set, with the tour re-curated

**Status:** ready

## Outcome

This card is conditional. It dispatches only if the orchestrator, deciding the step after round 3 under the owner's
delegation (decision memo `tasks/decision-2026-09-24-stage-b-wave.md` section 8.8), promotes candidate round 3. If
round 2 stays shown, the card closes unexecuted with a dated note (Constraints, "Conditional dispatch").

Candidate round 3 is `replays/candidates/stage-b-r3/9p2i`, recorded by `tasks/work/stage-b-record-r3.md`: the same
seeds 0-49 and rules as round 2, plus the route field (`route_lines_version = 1`). On promotion its bytes replace
`replays/samples/9p2i` in place, as round 2's replaced baseline 9's ([`promote-round-2`](promote-round-2.md)), and the
spectator surfaces are re-curated on the new bytes in the same pull request, as
[`spectator-tour-round-2`](spectator-tour-round-2.md) did. On 2026-10-09 the owner ruled, verbatim, "Keep the
comparison records" (memo 8.9, "Amendment of 2026-10-09"): a promotion of round 3 keeps round 2's bytes as
`replays/candidates/stage-b-r2`, and only the promoted round's candidate copy retires. When it is done:
- `replays/candidates/stage-b-r2/` holds round 2's bytes, moved out of `replays/samples/9p2i` with each file's sha256
  unchanged: its 50 replays, `MANIFEST.md`, `roster.json` and report gz as the round's `9p2i` set, its declared config
  (316 bytes, sha256 `0c02fa61...192b`) as the round's `experiment-config.json`, and a new `README.md` carrying the
  round's declaration. `results-game-profile.json` does not move, because the candidate layout admits no other file;
  the profile is regenerated in place for round 3.
- `replays/samples/9p2i` holds round 3's 50 replays, `MANIFEST.md`, `roster.json` and report gz, each byte-identical to
  the candidate copy, with round 3's declared config at `replays/samples/9p2i/experiment-config.json`. Round 3's
  candidate copy is deleted. `samples/4p1i`, `ml_corpus/9p2i` and `ml_corpus/4p1i` stay byte-identical, and so does
  round 1's candidate directory; the corpus FROZEN line and every ML artifact do not move.
- The era registry names a `stage-b-r3` era for the shown 9-player set; `stage-b-r2` owns no committed set, and its
  declared config is read at the candidate copy. Every instrument groups by era and never pools across two. The ladder
  tip stays at baseline 9, and baseline 10 stays reserved for a full re-record.
- The route field is named in plain words wherever the shown set's rules are listed, and the game-shape profile is
  re-derived on the new bytes by its own publisher.
- The featured strip is re-picked by the measured criterion; the curated cases are re-derived or withdrawn; the README
  hero and media are re-captured; the reading guide's exhibits follow the strip; the e2e head-card guard is green in
  both directions.
- The front door is current under its budgets, and the promotion is a dated section of the round-3 audit.

This is one card, one pull request and one merge (memo 8.7 item 3), so no holding edit is needed. The orchestrator
merges it once verified (memo 8.9), and the merge republishes the demo with the promoted set.

## Evidence

Every `path:line` below is a citation at `225d2b77`, labelled as such, and is re-anchored by its symbol at dispatch;
`335cbdc9` (the amendment's commit) changes only the decision memo, so each reads the same there. Every count is
reproducible from the tree or the named audit, was measured at authoring and is re-measured at dispatch; the
dispatch figure governs. All counts are count-only: no prompt, transcript text or seed-band prefix is printed.

**Rulings, verbatim.** Memo 8.8, the owner, 2026-10-09: "I will let this session, as the orchestrator, decide about
promoting round 3. Keep what I want for the project in mind. I lean towards wanting to promote round 3, but if there
is an issue you find with recording, or think it is really a step down in terms of gameplay, you can make the decision
to keep round 2." Memo 8.9, 2026-10-09: "Merge both when verified and retire the memo's D14 list", with the
orchestrator's defaults that no wrong-but-believable ejection is featured on the strip and that the README leads with
the process rows (the front-door card's). Its amendment the same day (`tasks/decision-2026-09-24-stage-b-wave.md:1612-1622`
at `335cbdc9`): "Keep the comparison records", so round 1 stays, the proposal that round r+1 deletes round r is
declined, and a promotion of round 3 keeps round 2's bytes as `replays/candidates/stage-b-r2`. Memo 8.7, 2026-10-09: "Apply all five redundancy removals and confirm the
five points as proposed"; its item 3 makes a promotion one card. Memo 8.1 ruling 4: "README should be current and can
be a focus in the last steps, once the project is stable." Memo 8.3: the champion-flip comparator is held at 11 of 50
(`FSM_COMPARATOR_AT_D41C9006`, `scripts/regen_test_goldens.py:70` at `225d2b77`).

**Known now: the shown set this card replaces (round 2).** 50 replays; one MANIFEST `git_sha`, `43b5ee45`
(`tests/api/test_sets.py:496` at `225d2b77`); 24 of 50 impostor wins (`README.md:23`); 117 meetings and 691 ballots
(`_RETIRED_GUARD_PINS`, `tests/meetings/test_prompt_byte_golden.py:1366` at `225d2b77`); a declared config of 316 bytes,
sha256 `0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b` (`shasum -a 256`); beside the recordings, the
served profile `results-game-profile.json`. `uv run python scripts/measure_featured_criterion.py --set 9p2i --list`
reads 11 of 50 games opening on a role-proof ejection (seeds 3, 5, 6, 7, 10, 11, 19, 20, 27, 42, 49), two non-vent
impostor openers (14, 44) and five first meetings ejecting a crewmate who did not open them (2, 12, 13, 22, 25).

The surfaces built on those bytes, at `225d2b77`:
- The strip (`frontend/src/components/ReplayPicker.tsx:115-146`) is 9p2i seeds 19 and 14 and 4p1i seeds 2, 11 and 29,
  with its criterion comment at `:83-113`; `tests/api/test_sets.py:871` pins `featured[0] == ("9p2i", 19)`.
- The curated cases (`api/public_results.py:58-96`) are `witnessed-vent` (supported) and `weak-evidence`
  (unresolved), both on seed 19; the 9p2i source root is `148fa211` (`:40-41`), the 4p1i root `9bae2b03` (`:43-44`),
  and the e2e literal `frontend/e2e/evidence-journey.ts:45`.
- The hero (`frontend/e2e/media.spec.ts:80-93`) is seed 19 at tick 9 (fog subject p-5, accused p-4, meeting at tick
  12), captioned at `README.md:13`.
- The served profile's reveal-only shelf "decided without proof: wrong on what it held" holds 20 games, neither 19 nor
  14 (its "right" half 18), read count-only from `replays/samples/9p2i/results-game-profile.json`. So the public demo
  shows no wrong-but-believable ejection today.

**Supplied at dispatch.** The round-3 audit (`audits/audit-<date>-stage-b-r3.md`) supplies the pre-registered
readings, the orchestrator's step with the readings it rests on (memo 8.8), the route-check count M, and P's sha (the
one MANIFEST `git_sha`). The declared config's bytes come from the round directory; the record card projects 342 bytes
and sha256 `a788b9eb...6d57d` if the field merged as `route_lines_version`, which P recomputes. This card measures on
round 3's bytes at dispatch: the eligible heads, the non-vent openers, the case candidates, the hero scene and every
re-pinned literal. None of these is known now.

**What a swap breaks or misreads** (code reading at `225d2b77`; the swap was not run):
1. **Registry.** `eval/eras.py:81-101` files `samples/9p2i` under `STAGE_B_R2`, whose `declared_config` is
   `replays/samples/9p2i/experiment-config.json`, and `ERAS` must equal the registered eras (`tests/eval/test_eras.py`).
   `experiments/lab/route_check_replay.py:286-300` reads r2's declared config through `STAGE_B_R2.declared_config` at
   the column's own commit, where the file sits at the samples path; once the registry names the candidate copy, that
   read needs the path the column was recorded at, as `R1_CONFIG_PATH` does for r1.
2. **Referee.** `REFEREE_READS` already declares `route_lines_version`, with its layer review recorded at
   `eval/watchability.py:1580-1605`, so no widening is needed. The stage block `"stage-b-r2"` (`:1142-1157`) pins
   floors on bytes that leave. `BAKEOFF_BASELINE_ID` stays `"baseline-9"` (`training/bakeoff/harness.py:188`).
3. **Scorecard.** The before file is a JSON list holding one frozen block, baseline 9's `replays/samples/9p2i` entry
   (`commit` `d41c9006`, `era_id` `baseline-9`), pinned by `BEFORE_COLUMNS_SHA256` (`eval/process_scorecard.py:1960-1967`;
   `b6b8ecaa...38a7`); `docs/artifacts.md:115` describes the file as "each replaced set's entry as published before its
   bytes moved". Whether that column grows a block per promotion is the owner's (the baselines memo's D12, and its Part
   3.1 REBASE row for S15 and L8), unruled: memo 8.5 decides none of D9, D12, D13 or D15 to D18.
4. **Doc facts.** `_WIN_SPLIT_HEADERS` keys each era's record table (`scripts/check_doc_facts.py:642-647`);
   `check_featured_exhibits` (`:5228`; `_MIN_EXHIBIT_SEEDS = 2` at `:604`) holds the guide's exhibits to the strip.
   Budgets (`:933-938`) against `wc -w` at authoring: README 1,579 of 1,600; reading guide 1,338 of 1,350; ML page
   2,134 of 2,150; lessons 1,444 within 800-1,500; architecture 1,300 of 1,300
   (`tests/scripts/test_check_doc_facts.py:4419`).
5. **The census against the route-check lab.** `tests/eval/test_gameplay_census.py:10337` and `_round_column`
   (`:10697-10706`) hold each round column's recordings (`_ROUND_COLUMNS = ("r2", "r1")`, `:10621`) to HEAD's blob for
   blob (`recording_blob_problems`, `:10286`). r2's path is `replays/samples/9p2i`, so the swap turns them red; its
   recording files move to `replays/candidates/stage-b-r2/9p2i`, so the HEAD side of the comparison moves with them.
   CI clones shallow (`.github/workflows/ci.yml` names no `fetch-depth`), so r2's recorded sha is not there to read,
   and the helper's shallow branch reads the recorded tree from HEAD's listing at the path it is given.
6. **The sweep.** The widened pattern of Validation matches 96 files under `tests/` and 12 under `frontend/src` and
   `frontend/e2e`, plus 56 production files under `api/`, `eval/`, `orchestrator/`, `scripts/` and `experiments/`; 53
   files outside `tasks/` and `audits/` name `stage-b-r2` (`git grep -l`).
7. **Public words.** `recordedSettings` (`frontend/src/components/PublicResults.tsx:18-33`) has no branch for
   `route_lines_version`, so round 3's config would render nothing about it; `ADOPTED_RULES`
   (`frontend/src/lib/adoptedRules.ts`) is held to the "Adopted arms" paragraph (`docs/experiment-arms.md:134`). The
   record card's menu names this follow-up.
8. **Registry rows.** `docs/artifacts.md:100` (samples, 39 MB / 108 files) and `:103` (candidates, 35 MB / 56 files),
   held to the git index by `scripts/verify_ml_evidence.py` (`_IN_TREE_PROBES` `:2754`, `_IN_TREE_INVENTORY` `:2826`).
   After the record the candidates family holds round 1 (55 files), round 3 (55 if it matches round 2) and the
   family README: 111. This card deletes round 3's 55 and adds round 2's 55 (53 set files, the config and a new
   README), so the row reads 111 again, with different bytes; the samples row keeps its count.
9. **The candidate family.** `replays/candidates/README.md` says a round whose bytes become a committed set is deleted
   in the promoting change and "any other round stays until a later change names its retirement"; its layout admits
   only `README.md`, `experiment-config.json` and the set directories. `tests/scripts/test_candidate_sets.py`
   (`test_every_committed_round_holds_its_declared_shape`, `:234`) and `scripts/verify_samples.sh` (`:61-62`)
   enumerate every round, so a second round is read without a code change. The golden raises on an unpinned set
   (`_retired_guard_pin`, `tests/meetings/test_prompt_byte_golden.py:1372-1378`).

**The D14 card lands first.** Under 8.9, `retire-era-locked-pins` retires the baselines memo's D14 list (Part 4 D14
with D14-T1 to T3, and the RETIRE rows of Part 3.1) after the record merges, without the round-1 item, which the
amendment keeps (L6). Among the retired items are the transcription half of the re-pin family (L9, including the two
`frontend/e2e/` commit literals), the S9 disclosure tuple (G21) and the W fixtures and anchors (G27). Whatever that
card has already turned into a registry-derived read needs no re-pin here; the sweep re-counts at dispatch. Its swap
rehearsal moved round 2 to the candidate copy as this card does, and its Results list the failures it left for this
card by test id. The baselines memo is
`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`; its
Part 3.1 row W35 keeps the role clause of the second card's criterion while D7 reads "never".

## Acceptance

Each item names its enforcing mechanism and a planted or perturbed proof. Each new test is written first and fails at
this card's base for its stated reason, and Results quotes that run. Every production line this card writes is held
by a test that goes red when the line is neutered; every sourced constant has a planted source-change case; no test
is weakened, and a retired check is deleted with its mechanism and one history line, never loosened. User-facing copy
goes through `SPECTATOR_COPY` or the picker data, with no task or audit ID, no unexplained jargon and no threshold
arithmetic.

- [ ] **Round 2's bytes are kept as the candidate copy `replays/candidates/stage-b-r2`, identically** (the
  amendment). First, `git mv` the 50 `replay-seed-*.jsonl`, `MANIFEST.md`, `roster.json` and
  `tournament-eval-report.json.gz` from `replays/samples/9p2i/` to `replays/candidates/stage-b-r2/9p2i/`, and
  `replays/samples/9p2i/experiment-config.json` to `replays/candidates/stage-b-r2/experiment-config.json`; write
  `replays/candidates/stage-b-r2/README.md` in plain words (the rules the round recorded, that it was the shown set
  from 2026-10-02 until this promotion, and that it adopts nothing) with exactly one `candidate-declaration` block:
  the config's `shasum -a 256` line and `9p2i seeds 0-49`. `results-game-profile.json` stays at `replays/samples/9p2i`
  (the layout admits no other file) and is regenerated there for round 3. `STAGE_B_R2.declared_config` names
  `replays/candidates/stage-b-r2/experiment-config.json`; `experiments/lab/route_check_replay.py` reads r2's column
  config through a constant holding the path the column was recorded at, as `R1_CONFIG_PATH` does, so its committed
  r2 column stays byte-identical. Mechanism: the sha256 identity both ways, each of the 54 moved files at this card's
  base against its new path at the head, listed in the promotion record; `tests/scripts/test_candidate_sets.py`
  (declared sha, declared seeds, one recording sha, every game on the declared config, every recording reproduces,
  each report equal to a rebuild) and `bash scripts/verify_samples.sh` with no argument, both now reading rounds 1 and
  2 (a test names both rounds, so the enumeration cannot silently skip one); the README's copy passes
  `test_the_new_copy_carries_no_identifier_and_no_threshold_arithmetic`; `uv run python -m
  experiments.lab.route_check_replay --check` exits 0 at the head. Planted: one byte of the moved config fails the
  declared sha; a declaration naming `9p2i seeds 0-50` fails the seed check; the route instrument pointed at the
  registry's new path for r2 fails at the column's own commit, naming the path.
- [ ] **Round 3's bytes move in, identically.** Then `git mv` round 3's 50 replays, `MANIFEST.md`, `roster.json` and
  report gz into `replays/samples/9p2i`, and its `experiment-config.json` to
  `replays/samples/9p2i/experiment-config.json`; round 3's `README.md` is deleted with the emptied round directory.
  Mechanism: each moved file's sha256 equals the candidate file's at this card's base (listed in the promotion
  record); the validity gate on `samples/9p2i` passes with the model, zero cost, the four prompt pairs,
  `--expected-experiment-config` that file, `--expected-seeds 0-49` and `--require-one-recording-sha`;
  `verify_samples.sh` and `build_sample_report.py --sample-dir replays/samples/9p2i --check` pass. Perturbed:
  `--expected-seeds 0-50` exits 1, and so does round 2's config as the expected one. `git diff --stat <base>..HEAD` is
  empty over `replays/samples/4p1i`, `replays/candidates/stage-b-r1/`, every `replays/ml_corpus/` set file, `training/`
  and `agents/tactical/learned/`.
- [ ] **One era registry, held to the bytes.** `eval/eras.py` gains `STAGE_B_R3` (record: the round-3 audit; date:
  the MANIFEST's `refreshed_at`; declared config: the in-tree file above) and files `samples/9p2i` under it; `ERAS`
  and `COMMITTED_SETS` drop `STAGE_B_R2`, whose constant stays, with one docstring line, for the candidate copy and
  the route instruments' r2 column, its declared config at `replays/candidates/stage-b-r2/experiment-config.json`.
  Mechanism: `tests/eval/test_eras.py` folds each set's games to one census `EraKey`, one key
  per era id, the declared file equal to every game's config, and `ERAS` equal to the registered eras. Planted: the
  registry filing `samples/9p2i` under `stage-b-r2` fails; a scratch set with one game's config edited fails; `ERAS`
  still listing `STAGE_B_R2` fails.
- [ ] **The instruments group by era.** The scorecard, the census, the counterfactual and `measure_baseline.py` read
  the registry and pool only within an era; the counterfactual's `--sets samples/9p2i` refuses, naming `stage-b-r3`.
  Mechanism: `publish_process_scorecard.py --check` and `publish_gameplay_census.py --check`, after regenerating
  `docs/process-scorecard.*` and `docs/gameplay-census.*` by their publishers. Planted: a pool over two eras raises,
  and so does a hand-built input list filing `samples/9p2i` under `baseline-9`.
- [ ] **The before column grows by the recording it replaced, as D12's clause is settled before dispatch.** Whether
  the frozen before column grows a block per promotion is the owner's (the baselines memo's D12, unruled; Constraints,
  "Prerequisites"). This item is contracted on the grow form, the one that moves no frozen byte and is reversible: the
  baseline-9 block stays in `docs/process-scorecard-before.json` byte for byte, and round 2's `samples/9p2i` entry of
  `docs/process-scorecard.json` at this card's base is appended as a second block (`commit` the commit that held
  round 2's bytes, `era_id` `stage-b-r2`, `set` `replays/samples/9p2i`), carried as frozen bytes the publisher never
  recomputes. `BEFORE_COLUMNS_SHA256` is re-pinned to the grown file, with one dated line in its comment naming the
  old digest (`b6b8ecaa...38a7`); each set's before column is read from the block of the era its bytes replaced
  (`samples/9p2i`, now `stage-b-r3`, reads the `stage-b-r2` block), and a set with no such block has none. Results and
  the promotion record state that the choice is reversible: removing the appended block restores the old file's
  content and the old pin. If the owner's word, or the default the orchestrator records for it, names another form,
  the card stops and asks before writing this item. Mechanism: `read_before_columns`'s sha256 pin and
  `publish_process_scorecard.py --check`. Planted: one edited leaf of either block refuses the fold, naming the file;
  a scratch registry filing `samples/9p2i` under `stage-b-r2` reads the baseline-9 block and fails the page's
  `--check`; the head file's first block equals the base file's only block, leaf for leaf and as text (a count-only
  comparison quoted in Results).
- [ ] **The census agreement follows the bytes.** No test reads a round column's recordings at a HEAD path that no
  longer holds them. r2's legs of `test_the_route_check_columns_read_the_recordings_now_at_head`, of
  `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting` and of the reach test that shares
  `_ROUND_COLUMNS` are retargeted, not retired: `recording_blob_problems` takes the HEAD path a column's recordings now
  live at (r2: `replays/candidates/stage-b-r2/9p2i`), compares blob for blob when the recorded commit is in the clone,
  and in a shallow clone still proves every recording file unchanged, or fails by name. The shown set keeps a lab twin:
  the committed route-check results gain an r3 column, written by the instrument's own command at this card's bytes
  commit and path `replays/samples/9p2i`, with `declared_config_path("r3")` read from the era registry; r2's reads the
  constant of the first item. The s9, r1 and r2 columns stay byte-identical (`--check`), and `_ROUND_COLUMNS` reads
  `("r3", "r2", "r1")`. Mechanism: those census tests over r3, r2 and r1, and
  `tests/experiments/test_route_check_replay.py`. Planted: one r3 misjudged flag flipped names its meeting; one r2
  replay blob changed at the candidate path fails naming the file; the base helper, reading r2 at
  `replays/samples/9p2i` against the promoted tree, fails naming r2.
- [ ] **Watchability: a stage block for the shown era; scoring frozen.** `_BASELINE_SUPPLY_FLOORS` gains `stage-b-r3`
  with only a `9p2i` entry, each pin measured on the promoted bytes and passing at equality, and the default resolves
  `samples/9p2i` to it (`default_baseline_id`, `eval/watchability.py:2475` at `225d2b77`). The `stage-b-r2` block,
  whose bytes left, is deleted with its equality tests and one history line (craft rule 3). `baseline-9`'s entries
  stay byte-identical as history and as the ML selection floor. The referee's gauges, rules, scoring and
  `REFEREE_READS` do not change; Results confirms the route field's recorded layer review against the promoted bytes.
  Mechanism: `tests/eval/test_watchability.py`; `measure_baseline.py --watchability --json` on each untouched set is
  byte-identical at base and head, measured directly and quoted with its sha256. Planted: one stage pin raised by one
  numerator fails its set; a recording carrying one setting outside `REFEREE_READS` is refused, naming the field.
- [ ] **The recorder records the next round against the new era.** A run aimed at `samples/9p2i` must carry round 3's
  config sha256, read from the registry's declared file (`era_target_problem`, `scripts/_declared_experiment.py:396`
  at `225d2b77`). Mechanism: `tests/scripts/test_refresh_samples.py` and `refresh_samples.sh --dry-run`. Planted: a
  bare run, round 2's config and round 3's config with one byte changed, each aimed at `samples/9p2i`, refuse; round
  3's config aimed at `samples/4p1i` or `ml_corpus/9p2i` refuses; aimed at `samples/9p2i` it passes the dry run.
- [ ] **The candidate-round rule, and its rows.** `replays/candidates/stage-b-r3/` is deleted, its record citing the
  commit that held it (the record's merge); `replays/candidates/stage-b-r1/` stays byte for byte, and
  `replays/candidates/stage-b-r2/` holds round 2 (the first item). `replays/candidates/README.md` states the rule as
  the amendment rules it, with one dated history line: a promotion deletes the promoted round's candidate copy, whose
  bytes become the committed set, and keeps the bytes it replaces as that round's candidate copy, the comparison record
  that isolates one dial; every other round stays (the proposal that round r+1 deletes round r was declined on
  2026-10-09). Its "Not canonical" paragraph names round 3 as the shown set and round 2's directory as its former
  copy. In `_RETIRED_GUARD_PINS` the record card's `candidates/stage-b-r3/9p2i` row retires, the
  `candidates/stage-b-r2/9p2i` row is added (the golden raises on an unpinned set) and `samples/9p2i`'s row reads
  round 3's walk, each in the form `retire-era-locked-pins` left (semantic zeros as literals, counts derived), and
  the `candidates/stage-b-r1/9p2i` row stays. `docs/artifacts.md` recomputes the samples, candidates and audits rows
  (`du -sh`, file counts: candidates 111 files if round 3 has 55) and its prose names round 3 as the shown set and the
  kept candidate copies. Mechanism: `verify_ml_evidence.py`'s inventory parity against the git index, the candidate
  test and the golden. Planted: the candidates row one file off fails parity (the count alone cannot show the swap,
  since 55 files leave and 55 arrive, so Results also quote `git ls-files replays/candidates | cut -d/ -f1-3 | sort -u`
  at base and head); the golden without the `candidates/stage-b-r2/9p2i` row raises `KeyError` naming it; a
  stray file in `replays/candidates/stage-b-r2/` fails the candidate test.
- [ ] **The route field is named, in plain words,** as the orchestrator's step in the round-3 audit names it; adopted
  is the default the record card's menu gives for the era-keyed promotion. On that default, the "Adopted arms"
  paragraph of `docs/experiment-arms.md` gains one dated sentence naming `route_lines_version = 1` and the step;
  `ADOPTED_RULES` gains the field; `SPECTATOR_COPY.adoptedRules` gains plain words ("each voter sees a line about
  which stated places the map can link", or close; "route line" is defined at `docs/glossary.md:293`). No switch is
  deleted; graduation waits for a full re-record. Mechanism: `frontend/src/lib/adoptedRules.test.ts` (the list held
  to the paragraph and to the shown set's declared config) and `PublicResults.test.tsx`. Planted: the base seven-rule
  list fails against the new paragraph; a config without the field renders no route words; the copy gate
  (`frontend/src/lib/copy.test.ts`) stays clean.
- [ ] **The doc facts read per-set provenance** (`scripts/check_doc_facts.py`; planted cases in
  `tests/scripts/test_check_doc_facts.py`). The win split comes from the promotion record's
  `| set | round-2 impostor rate | promoted impostor rate |` table, keyed `stage-b-r3` in `_WIN_SPLIT_HEADERS`;
  `stage-b-r2`'s key retires unless a history claim still reads it. Each dated claim names its set and equals that
  set's MANIFEST date. The composite-stamp parse reads the route arm's token, and the vote-correctness lead-in
  (`eval/vote_correctness.py`) names each era's id, model and tokens. Planted: "48% (9p2i)" as the current figure
  fails; "the 2026-10-01 record (9p2i)" as current fails; a fixture MANIFEST with round 3's stamp and the route token
  dropped fails; the base front door run against the promoted tree fails, naming at least the 9p2i date, the 9p2i rate
  and the era sentence.
- [ ] **The front door is current, under the budgets.** `README.md` re-derives its results cells, the before cells
  (now round 2's), the samples paragraph, the report example and the hero caption, keeping today's table order (the
  process-first reorder is `front-door-process-first`'s). `docs/reading-guide.md` follows with the same cells and its
  narrative. `docs/glossary.md` ("era", "baseline N", "the ladder tip") and `docs/architecture.md` (the ladder
  paragraph, net-zero words) stay true. `docs/history.md` gains one dated paragraph; `docs/experiment-arms.md` records
  round 3 as the shown set and round 2's bytes as its candidate copy, its Candidate round 1 section unchanged;
  `docs/ml-program.md` changes only where a sentence names the shown era; `audits/README.md`
  updates round 3's row; `replays/ml_corpus/README.md` updates its dated note; `docs/deployment.md` changes only its
  stated 9p2i report size. Every live-tense sentence about round 2 as the shown set is fixed in this PR. Mechanism:
  `check_doc_facts.py` (facts, agreement, budgets), with `wc -w` per page in Results, each at or under its ceiling;
  raising one is the owner's. Perturbed: the base copy of each page, dropped into the promoted tree in scratch, fails.
- [ ] **The strip is re-picked by the measured criterion.** `FEATURED_GAMES` keeps 4p1i seeds 2, 11 and 29 unchanged.
  Its 9p2i row becomes (a) a head whose first meeting ejects on a role-proof flag, chosen by the criterion, its seed
  and reason measured and named in Results and in the comment above the list; and (b) one non-vent opener from
  `--list` (first meeting ejects an impostor, no flag anywhere, no vent at or before it), or the head alone if that
  list is empty. No crewmate-ejecting first meeting and no reporter ejection is featured, and no featured 9p2i game is
  a member of the re-derived profile's reveal-only shelf `decided_without_proof_wrong`, so no wrong-but-believable
  ejection is featured (the 8.9 default). The role reads in these criteria are curation and gate no record,
  instrument or adoption (`docs/gameplay-census.md:5`); the role clause stays while D7 reads "never" (W35).
  Mechanism: `tests/api/test_sets.py`: `_assert_opens_on_role_proof` on each set's head, `_assert_non_vent_opener` on
  pick (b), a new test holding every featured 9p2i seed out of the served profile's wrong shelf, and re-derived
  seed-set pins. Planted: the rejection parametrize is re-derived on the new bytes, each case with its `match=` (the
  old head and second card where they now fail); a strip naming one wrong-shelf seed fails, naming it. If no eligible
  head stays off the shelf, the card stops and asks.
- [ ] **The category clause is re-proved by perturbation.** `test_the_role_proof_clause_rejects_a_recategorised_head`
  is re-targeted to the new head: its role-proof flag recategorised as `cross_statement`, the criterion rejects it by
  the flag clause (`match=`), and the weakened predicate accepts it. Mechanism: that test. Proof: its green run on the
  new head and its red run with the clause weakened, quoted in Results.
- [ ] **Every label is true and spoils nothing.** Each 9p2i label states only countable facts (meetings and spoken
  turns in `_assert_featured_counts`' number words; a reported vent sighting; "no flagged contradictions" for a
  flag-free pick) and poses one question, naming no ending, player or vote. Mechanism: the spoiler test and
  `test_current_featured_claims_match_source_and_gate_bites`, re-parametrized. Planted: each label fails with its
  meetings removed, and each flag claim with only its flags stripped.
- [ ] **The curated cases are re-derived or withdrawn, and always on the strip.** Each case in `_curated_cases` is
  re-written on a promoted meeting of a featured game, in the base cases' shapes (supported: a cited vent sighting with
  role proof, ejecting; unresolved: a weak or absent flag, a skip), or withdrawn with its check branch, sha and tests.
  No case frames a wrong-but-believable ejection, and `disputed-route` stays withdrawn. Each kept case has its sha
  constant and a `_check_case` branch holding every sentence of its setup and explanation to the served replay, the
  meeting memory and the recorded moves. The 9p2i source root moves to this PR's bytes commit (reachable from `main`
  by a merge commit) and `_SOURCE_ROOTS` is keyed by the promoted fingerprint; the 4p1i root stays at `9bae2b03`, so
  `data/4p1i/eval/summary.json` does not move. Mechanism: `tests/api/test_public_results.py`, and a bundle test that
  bakes the strip's own `FEATURED_GAMES` and requires every built case in the baked summary. Proof: one planted
  perturbation per sentence family of each kept case; the changed-source test; a case pointed at an unfeatured game
  fails the bundle test; the 4p1i link built from the 9p2i root fails.
- [ ] **The viewer's corpus fixtures and their census twins.** `replay-skeleton.fixture.json`, `bodies.fixture.json`
  and `contradictions.fixture.json` are regenerated by their recipes (`frontend/src/lib/skeleton.testkit.ts` and the
  fixture tests), 4p1i halves unchanged. On the promoted bytes the corpse age reproduces `corpse_age_at_report`, the
  no-reply note `accused_opener_answers`, the exit-ended vent windows `ticks_inside_per_trip`, the regroup-ended trips
  `trips_closed_by_regroup`, and the regroup note's count of meetings that end their game is re-derived. Mechanism:
  vitest over the regenerated fixture, bound by `corpusSha256`. Planted: the retired pairing rule, kept as the
  control, fails the new census; the base fixture fails against the new digest.
- [ ] **The e2e head-card guard, green both ways, and the evidence journey.** `frontend/e2e/journey.spec.ts`'s main
  leg takes the "has evidence" branch on the new head; its planted twin opens pick (b) by exact pill text and walks the
  "no flags" branch (or opens 4p1i seed 11 through `?set=4p1i` if there is no pick (b)).
  `frontend/e2e/evidence-journey.ts` walks the kept cases with the source link matching the new root (unless the D14 card derived it) and re-enters its
  evidence legs through a kept case or the head's first cited observation. Mechanism: CI's `frontend-e2e` job
  (`npm run e2e`). Planted: pick (b)'s label without "no flagged contradictions" fails the guard's pairing assertion;
  the base evidence journey against the promoted tree fails.
- [ ] **The reading guide's exhibits follow the strip.** The exhibit paragraph (`docs/reading-guide.md:71-75` at
  `225d2b77`) names at least two featured promoted games and their meetings in counts. Mechanism:
  `check_featured_exhibits` and the 1,350-word ceiling. Planted: the paragraph naming a seed the strip dropped fails.
- [ ] **The README hero and media are re-captured on the new head.** `HERO` (`frontend/e2e/media.spec.ts`) is
  re-chosen on the new head at a tick where the omniscient half and a fog subject's half differ, every caption clause
  asserted against the served bytes, the caption claiming only what each half shows. The capture runs as
  `AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts` (an existing switch, not a new lever);
  `docs/media/provenance.json`, `docs/media/README.md`, the stills, the README caption and the media row of
  `docs/artifacts.md` follow. Mechanism: `tests/scripts/test_public_recording_provenance.py`
  (`test_media_hashes_and_labels_are_current`, `test_the_captions_scene_is_the_recorded_one`). Planted: the base
  caption against the promoted bytes fails by name; a moved digest fails.
- [ ] **The game-shape profile is re-derived by its publisher.** `uv run python scripts/publish_game_profile.py`
  rewrites `replays/samples/9p2i/results-game-profile.json` and `docs/game-profile.md` on the promoted bytes, the leak
  and saturation classes recomputed for the era; `test_the_promoted_set_ships_its_profile_on_its_own_key` reads P's
  MANIFEST key; the Highlights bake follows the new strip. Mechanism: `publish_game_profile.py --check`, run twice
  with no diff. Planted: the base profile left in the promoted tree fails `--check`, naming the file.
- [ ] **The re-pin sweep, old to new.** Every test, fixture and comment that reads or cites `samples/9p2i` bytes or the
  `stage-b-r2` era (re-counted at dispatch by the Validation command, plus helper indirection) is re-derived through
  its production computation, with its old value inline (`# was <old>` or `// was <old>`). Instruments that refuse the
  era assert their named refusal, and the one-sha MANIFEST test reads P's sha. Mechanism: CI's green run. Proof: each
  changed pin fails at the base bytes, quoted per file family, and `git diff <base>..HEAD -- tests/ frontend/src/`
  counts the inline notes per file.
- [ ] **The corpus and the ML evidence do not move.** Mechanism: `scripts/verify_ml_evidence.py` offline (never
  `--complete`) and `uv run pytest -m campaign` by hand, at base and head with the same per-leg verdicts and both
  counts recorded; `tests/scripts/test_champion_flip_ruling.py` holds `(11, 50)` unchanged; `BAKEOFF_BASELINE_ID` and
  every FROZEN line are unchanged. Planted: a stale samples file count fails the inventory leg. Any ML figure keyed to
  `samples/9p2i` bytes stops the card.
- [ ] **The promotion record.** A dated section closes the round-3 audit after the orchestrator's step. It holds the
  step and the rulings verbatim (8.8, 8.9 and its amendment); the per-file sha256 identity both ways: between
  `replays/samples/9p2i` at base and `replays/candidates/stage-b-r2/` at head, and between
  `replays/candidates/stage-b-r3/` at base and `replays/samples/9p2i` at head (each replay, the MANIFEST, `roster.json`,
  the report gz and the config); the win-split table; the before column's form, its owner word or recorded default, the
  old and new digests and the reversal; the commits that held round 2's and round 3's bytes at their old paths; and the
  candidate-round rule as the amendment states it. Every earlier section stays byte-identical. Mechanism: a section-by-section
  comparison against the record's merge (0 differing lines) and `check_doc_facts.py`. Perturbed: one character edited
  in an earlier section of a scratch copy gives differing lines and exit 1.
- [ ] **The bundle change, stated file by file, in one checkout.** `build_demo_bundle.py --out <scratch>/before` runs
  at the base and `--out <scratch>/after` at the head, in the same checkout, so unchanged files keep their mtimes.
  `diff -rq` lists every changed path in Results and the PR body: the 9p2i replays added and removed by seed, the 9p2i
  summary and cases, the profile, the picker metadata and `assets/`. `data/4p1i/` is identical. Perturbed, in scratch
  and reverted: one 4p1i seed swapped shows `data/4p1i/` in the diff.
- [ ] **The gate, recorded as CI.** CI's green run at the exact pushed head, cited by run id in Results and the PR,
  is the gate record (memo 8.7 item 1): `project-checks` (`bash scripts/check.sh`), `frontend-checks` and
  `frontend-e2e`. No local `check.sh` runs at the final head, and no commit exists only to record a gate. Run locally
  and quoted: the media capture, the campaign tier, offline `verify_ml_evidence.py`, the bundle diff and the base-side
  red runs.
- [ ] **One bounded mutation pass.** Each mutant is applied alone over the lines this card writes, its targeted suite
  run, the file reverted. The operator classes are memo 8.7 item 2's: a dropped filter or wrapper, a swapped
  collection, a comparison made a None test, a role, kind, room or tick read made a constant, a dropped tuple member,
  swapped branches, a loaded source read as its literal, and a message argument made a constant. Mechanism: the table
  in Results. Behavioural survivors block; message-argument survivors are nonblocking after the first fix round.

## Constraints

- **Conditional dispatch.** The card dispatches only after the round-3 audit records the orchestrator's step
  promoting round 3 (memo 8.8). If round 2 stays shown, round 3 stays as `replays/candidates/stage-b-r3`, a
  comparison record under the amendment, and the orchestrator closes this card on `main` as a `docs:` commit, on the
  pattern of `tasks/work/held-out-prefix-freeze-6.md` in the wording the wave's other closure uses: the title becomes
  "Closed unexecuted: candidate round 3 was not promoted" ("retire" is craft rule 3's deletion, which this is not),
  Status done, one checked item stating that nothing ran, and Results a dated note naming the step and its section.
- **Authorization and house rules.** The promotion is the orchestrator's step under the owner's delegation (8.8), and
  its merge the orchestrator's under 8.9 once verified. No live provider call, no recorder run, no held-out generation,
  no spend; the untracked `.env` is never read. The engine stays deterministic; `agents/` never imports `engine/`; no
  module-level mutable state; invalid input raises. No `AILIBI_*` lever, environment switch or experiment field is
  added, and the prompt registry is not bumped. No recorded byte is edited (each moved file keeps its sha256) and no
  history is re-scored; the corpus FROZEN line and every ML artifact never move, and ML stays held. Role-correctness
  is reported, never a gate; nothing pushes an agent toward the correct answer; the meeting layer labels and never
  rewrites; wrong-but-believable is the game working and is never shown before the reveal.
- **Rulings kept from round 2's two cards.** The frozen referee's walk declares the layers, and this card widens
  nothing. The ladder tip stays at baseline 9, with baseline 10 reserved for a full re-record. No reporter-ejection
  game and no crewmate-ejecting first meeting is featured. The role reads in curation are curation, not gates. The
  comparator stays held at 11 of 50. Graduation of any switch waits for a full re-record.
- **Prerequisites and merge window against round 3's freeze.** Dispatch from `main` after, and merge after, both
  `stage-b-record-r3` (whose freeze, from round 3's first seed to its merge, covers `engine agents meetings
  observation orchestrator eval api scripts llm`, `training`, `experiments`, `audits/tactical-gameplay` and the
  record's nothing-moves paths, `replays/samples`, `api`, `frontend` and the census and scorecard docs among them,
  which this card writes or moves; round 1's directory, also in that diff, it never touches) and
  `retire-era-locked-pins` (so fewer literals are re-pinned). Two more preconditions, before dispatch: the
  orchestrator's step promoting round 3 is written into the round-3 audit (memo 8.8), and D12's before-column clause
  is settled, by the owner's word or by a default the orchestrator records in a dated memo line the owner can
  override, as 8.9 did for D7 and D8 (this card takes neither on itself). Merge BEFORE `front-door-process-first`,
  which builds the process-first README on the promoted set. If `main` moves under the branch, merge `main` in (never
  rebase) and re-run what it touches. `rubric-extractor-era` is closed before this card dispatches, and
  `retire-temporal-evidence-v1` stays `ready` and blocked pending the owner's D15 word; neither runs beside this card.
- **One writer per file.** This card writes Expected scope's files after `retire-era-locked-pins` merges and before
  `front-door-process-first` dispatches. Written by the record first, then this card: `replays/candidates/` (the
  record adds `stage-b-r3`; this card deletes it, adds `stage-b-r2` and updates the family README), `audits/README.md`
  and the round-3 audit (this card appends the promotion section only), `docs/experiment-arms.md`, the golden, and
  `docs/artifacts.md`. Written by `retire-era-locked-pins` first, then this card: the sweep's tests (the L9 family,
  `frontend/src/lib/bodies.test.ts` and `contradictions.test.ts` among them), `tests/meetings/test_prompt_byte_golden.py`,
  `scripts/check_doc_facts.py` and its test, `docs/artifacts.md`, `replays/ml_corpus/README.md`,
  `frontend/e2e/evidence-journey.ts`, `docs/history.md`, `eval/process_scorecard.py`,
  `scripts/publish_process_scorecard.py`, `docs/process-scorecard.md` and `.json`, `scripts/counterfactual_phase21.py`
  (one comment), and, only where the retirement's ledger moves a pin, `tests/eval/test_gameplay_census.py`,
  `tests/experiments/test_route_check_replay.py` and `tests/scripts/test_refresh_samples.py`. Written by this card
  alone in the wave: `docs/process-scorecard-before.json`, `eval/eras.py`, `eval/watchability.py` and their tests,
  `experiments/lab/route_check_replay.py` with its committed r3 column and r2 constant, `replays/candidates/README.md`,
  `tests/scripts/test_candidate_sets.py`, `tests/scripts/test_counterfactual_phase21.py`, `api/public_results.py` and
  `ReplayPicker.tsx`. Written by this card, then
  `front-door-process-first`: `README.md`, `docs/reading-guide.md`, `docs/glossary.md`, `scripts/check_doc_facts.py` and
  its test, `frontend/src/lib/copy.ts`, `frontend/src/components/PublicResults.tsx` with its test, and
  `tests/api/test_sets.py`. Each later card dispatches from `main` after this merge. `tasks/README.md` and this card's
  Status line are the orchestrator's.
- **Publication.** `.github/workflows/pages.yml` republishes on every push to `main`. This merge puts live the
  promoted set's summary, its re-picked 9p2i strip, the re-derived cases or their withdrawal, the served profile on the
  new featured games and the route field's public words; the README hero and media change on GitHub. The PR states the
  copy that goes live and the bundle diff file by file. The orchestrator merges under 8.9; task completion authorizes
  nothing beyond this publication.
- **Copy and curation.** "Regroup", "Stage-B" and era ids are not user copy. Featured labels state counts and one
  question. Wrong-but-believable framing appears only behind "Reveal case analysis (spoilers)", within the existing
  classes; adding a class is a DTO change and out of scope.
- **Delivery.** Branch `work/promote-round-3`, one PR into `main` with every section of
  `.github/pull_request_template.md`, merged by merge commit or fast-forward, never squash, never amended after push.
  Each commit body ends with `Card: tasks/work/promote-round-3.md` immediately followed by the exact line
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The PR ends with the Claude Code attribution line; agents
  post no PR comments. Document-only follow-up commits get the documentation lens only (8.7 item 4).
- **Stop and ask** if: the round-3 audit's step is not a promotion, or names another route-field disposition; D12's
  before-column clause has neither an owner word nor a recorded default at dispatch, or names a form other than the
  grow form; any byte of round 1's directory or of round 2's moved files would change; the round directory's config
  sha differs from P's; no eligible head stays off the wrong shelf; an ML figure is keyed to
  `samples/9p2i` bytes; a gate needs a recorded byte, a `tests/fixtures/` file or a FROZEN line to move; a page needs
  a raised budget; or `retire-era-locked-pins` left a surface in a shape this card did not anticipate.

## Expected scope

- `replays/samples/9p2i/`: the 50 `replay-seed-*.jsonl`, `MANIFEST.md`, `roster.json`, `tournament-eval-report.json.gz`
  and `experiment-config.json` (round 2's moved out, round 3's moved in); `results-game-profile.json` (regenerated).
- `replays/candidates/stage-b-r2/` (new: `README.md`, `experiment-config.json`, and `9p2i/` with round 2's 50 replays,
  `MANIFEST.md`, `roster.json` and `tournament-eval-report.json.gz`, all moved but the README);
  `replays/candidates/stage-b-r3/` (deleted whole); `replays/candidates/README.md`. `replays/candidates/stage-b-r1/` is
  never written.
- `eval/eras.py`, `tests/eval/test_eras.py`; `eval/watchability.py`, `tests/eval/test_watchability.py`;
  `eval/process_scorecard.py` (the before pin), `docs/process-scorecard-before.json`, `docs/process-scorecard.md`,
  `docs/process-scorecard.json`, `tests/eval/test_process_scorecard.py`; `eval/vote_correctness.py`;
  `eval/gameplay_census.py` (only if a per-era constant names an era); `docs/gameplay-census.md` and
  `docs/gameplay-census.json` (regenerated); `docs/game-profile.md` (regenerated).
- `scripts/check_doc_facts.py`, `tests/scripts/test_check_doc_facts.py`; `scripts/counterfactual_phase21.py` and
  `tests/scripts/test_counterfactual_phase21.py`; `scripts/measure_baseline.py`; `scripts/_declared_experiment.py` (only
  if the registry read needs it), `tests/scripts/test_refresh_samples.py`, `tests/scripts/test_candidate_sets.py`.
- `experiments/lab/route_check_replay.py` (`declared_config_path("r3")` from the registry, and r2's recorded path as a
  constant),
  `experiments/lab/results-route-check-replay.json` and `experiments/lab/report-route-check-replay.md` (the r3 column,
  by the instrument's command);
  `tests/experiments/test_route_check_replay.py`; `tests/eval/test_gameplay_census.py`;
  `tests/meetings/test_prompt_byte_golden.py`.
- `api/public_results.py`, `tests/api/test_public_results.py`, `tests/api/test_sets.py`,
  `tests/scripts/test_build_demo_bundle.py`, `tests/scripts/test_measure_featured_criterion.py`.
- `frontend/src/components/ReplayPicker.tsx`; `frontend/src/lib/adoptedRules.ts` and `adoptedRules.test.ts`;
  `frontend/src/lib/copy.ts`; `frontend/src/components/PublicResults.tsx` and `PublicResults.test.tsx`;
  `frontend/src/lib/{replay-skeleton,bodies,contradictions}.fixture.json` and their tests (`bodies.test.ts`,
  `contradictions.test.ts`, `vents.test.ts`, the regroup and annotation tests); `frontend/e2e/journey.spec.ts`,
  `frontend/e2e/evidence-journey.ts`, `frontend/e2e/media.spec.ts`.
- `docs/media/` (the stills, `provenance.json`, `README.md`) and `tests/scripts/test_public_recording_provenance.py`.
- `README.md`, `docs/reading-guide.md`, `docs/glossary.md`, `docs/architecture.md`, `docs/history.md`,
  `docs/experiment-arms.md`, `docs/ml-program.md`, `docs/artifacts.md`, `docs/deployment.md` (the report size only),
  `audits/README.md` (round 3's row), `audits/audit-<date>-stage-b-r3.md` (the promotion section only),
  `replays/ml_corpus/README.md` (the dated note only).
- The sweep: each file the Validation command lists under `tests/` and `frontend/`, and the comments it lists in
  production readers, re-run at dispatch with its file list quoted in Results; and this card's Results.

Directly necessary follow-through inside these boundaries is permitted and listed in Results; a file outside them goes
to the orchestrator. Nothing changes under `engine/`, `agents/`, `meetings/`, `observation/`, `llm/`, `training/`,
`replays/ml_corpus/*/` or `tests/fixtures/`, and `orchestrator/` changes only in a comment the sweep finds.

## Record impact

The shown 9-player set's bytes change: `replays/samples/9p2i` holds round 3's recording, so every figure, report and
served game for that set moves, and the merge republishes the demo. Round 2's recording stays in the tree as
`replays/candidates/stage-b-r2`, verified on every change like round 1, and the frozen before column grows by its
block (the form D12 settles). No new recording is made and no recorded byte is rewritten; each moved file keeps its
sha256. Future recordings change only in that the recorder requires round 3's declared config for `samples/9p2i`.
The three other sets, round 1's directory, the corpus, the ML fits and their keys, and the committed s9, r1 and r2
lab columns are untouched; the ladder tip stays at baseline 9. If the step adopts the route field,
`docs/experiment-arms.md` records it; no default moves and no switch is deleted. Measurement: the gates of Validation
at base and head, the per-era scorecard and census, the stage block at equality, and CI at the exact head.

## Validation

```sh
env | grep -c '^AILIBI_'                                          # 0, in a bare shell
uv run python scripts/validity_gate.py replays/samples/9p2i --expected-model Qwen/Qwen3.6-27B \
  --require-zero-cost --expected-prompt-versions <the four pairs the round-3 audit names> \
  --expected-experiment-config replays/samples/9p2i/experiment-config.json \
  --expected-seeds 0-49 --require-one-recording-sha              # and --expected-seeds 0-50: exit 1
shasum -a 256 replays/samples/9p2i/*                              # each equal to the base candidate file's
shasum -a 256 replays/candidates/stage-b-r2/experiment-config.json replays/candidates/stage-b-r2/9p2i/*
                                                                  # each equal to the base samples/9p2i file's
git ls-files replays/candidates | cut -d/ -f1-3 | sort -u         # README.md, stage-b-r1, stage-b-r2
git diff --stat <base>..HEAD -- replays/candidates/stage-b-r1     # empty
uv run pytest tests/scripts/test_candidate_sets.py -q             # rounds 1 and 2
bash scripts/verify_samples.sh                                    # bare (every set and both rounds), then per set
uv run python scripts/build_sample_report.py --sample-dir <each committed set> --check
# the sweep, re-counted (then the same pattern over api/ eval/ orchestrator/ scripts/ experiments/)
git grep -l -E 'samples/9p2i|samples" / "9p2i|"samples", "9p2i"|SAMPLES_9P2I|9p2i seed [0-9]|committed 9p2i' -- tests/ frontend/
git grep -l -E 'stage-b-r2|STAGE_B_R2' -- . ':!tasks' ':!audits'
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/publish_game_profile.py --check            # twice, no diff
uv run python -m experiments.lab.route_check_replay --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/measure_baseline.py --watchability --json <each untouched set>   # byte-identical at base, head
uv run python scripts/measure_featured_criterion.py --set 9p2i --list
wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md docs/architecture.md
AILIBI_SAMPLE_DIR=replays/samples/9p2i AILIBI_MANIFEST=replays/samples/9p2i/MANIFEST.md \
  AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2 \
  bash scripts/refresh_samples.sh --dry-run --seeds 0 --expect-levers "" \
  --experiment-config replays/samples/9p2i/experiment-config.json   # passes; bare and round 2's: refused
uv run python scripts/verify_ml_evidence.py                      # offline; never --complete
uv run pytest -m campaign                                         # at base and head, counts recorded
cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts
uv run python scripts/build_demo_bundle.py --out <scratch>/before # at the base, then --out <scratch>/after at the
diff -rq <scratch>/before <scratch>/after                         # head, both in one checkout
gh run list --branch work/promote-round-3 --limit 3               # CI's green run at the exact head, by run id
```

`check.sh` is not run locally at the final head: CI's run is the gate record (memo 8.7 item 1). A local `check.sh`
during development runs to its end, because `set -e` masks later gates. On macOS the evolution-strategy hash pin is
Linux-only, and CI is cited for it.

## Results

Not started. The card is conditional on the orchestrator's step after round 3 (memo 8.8) and on D12's before-column
clause being settled before dispatch. On dispatch, Results records each acceptance item's evidence, the sha256
identity both ways, the CI run id at the exact head, the bundle diff, the decisions (the head, the cases kept or
withdrawn, the before column's form with the word or default behind it, the route field's disposition), limitations
and deviations.
