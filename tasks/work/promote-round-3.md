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

- [x] Review correction (round 4): the round-3 sweep count reproduces. The sweep command quoted in the round-3
  Review correction item below, in "Review corrections, round 3" and in the PR body's round-3 item now ends with the
  pathspec `':!tasks/work/promote-round-3.md'`, which leaves out this card, whose own lines quote the figures and the
  command. With it the command lists 16 at `9de107b9`, at `a2ba69a9` and at this round's head; without it, 16, 26 and
  30, the difference being this card's own 0, 10 and 14 lines. Mechanism:
  `git grep -n -E '32,?952,?472|2,?790,?383|33 ?MB|33MB|33 megabytes' <head> -- . ':!tasks/work/promote-round-3.md' | wc -l`
  at each head, the same without the pathspec, and with `-- tasks/work/promote-round-3.md` alone for the card's own lines
  (table in "Review corrections, round 4"). Perturbed: the bare command at `a2ba69a9` lists 26, not the 16 stated.
- [x] Review correction (round 3): no comment or docstring still gives round 2's report as the shown 9p2i report's
  size. The module docstring of `scripts/build_demo_bundle.py` reads 34,579,235 bytes uncompressed, about 35 MB, and
  3,057,359 gzipped (was 32,952,472, about 33 MB, and 2,790,383), and the comments of `frontend/src/api/client.ts`
  (`getTournamentReport`) and `frontend/e2e/bundle.spec.ts` (the compact-results case) read 35 MB (was 33 MB).
  Mechanism: `gzip -dc replays/samples/9p2i/tournament-eval-report.json.gz | wc -c` and `stat -f %z` on the same gz;
  the sweep `git grep -n -E '32,?952,?472|2,?790,?383|33 ?MB|33MB|33 megabytes' -- . ':!tasks/work/promote-round-3.md'`,
  re-run at the fix head (16 hits: the three inline old values and 13 lines of history in round 2's two cards).
  Perturbed: the present-tense scan `git grep -n -E '(is|one is) (33 MB|32,952,472)' -- .` lists 3 at `9de107b9` and
  0 at the fix head.
- [x] Review correction (round 3): orchestrator ruling 5 (Decisions) replaces the text of the route-field box below.
  The route field is a recorded setting, named in plain words beside the kill cooldown through
  `SPECTATOR_COPY.routeLines`; `ADOPTED_RULES` and the "Adopted arms" paragraph stay at seven pairs, and that
  paragraph's one dated sentence names `route_lines_version = 1` as a setting these recordings carry. Mechanism:
  `frontend/src/components/PublicResults.test.tsx` ("names the route lines as set for these recordings, never adopted
  or experimental"), which pins the delivered words and plants a config without the field and one with it null, and
  `frontend/src/lib/adoptedRules.test.ts` ("are the paragraph's seven pairs, in its order, each held by the shown
  set's config", with its planted widened list); 57 passed over those two files and `src/api/client.test.ts`.
- [x] Review correction (round 3): the experiments row of `docs/artifacts.md` reads 7,558,279 tracked bytes / 170
  files (was 7.0 MB / 170 files, measured at `B`, where the tracked bytes were 7,367,891; this card's lab columns in
  `fc77fc50` add 190,388), by the audits row's formula. Mechanism: `git ls-tree -r -l HEAD -- experiments/lab
  experiments/model_probe`, its size column summed, and `git ls-files experiments/lab experiments/model_probe | wc
  -l`; `verify_ml_evidence.py`'s inventory parity holds a stated tracked-bytes figure exactly, through
  `test_every_counted_registry_row_matches_the_index`. Planted: 7,558,280, and `B`'s 7,367,891 at the head, each
  fail that test naming the row.
- [x] Review correction (round 3): the PR body's gate item names this round's pushed head as the final head and
  cites every CI run in order, and the thirteen `Co-Authored-By: Claude Opus 5.5` lines of `d9c3ada3` to `9de107b9`
  are recorded as a deviation from the Delivery constraint, not a decision, under "Review corrections, round 3" and
  in the PR body's Decisions; this round's commit carries the card's Fable line verbatim. Mechanism: `git log -1
  --format=%B` at the pushed head, `gh pr view 507 --json body` read against it, and CI's green run at that head,
  cited by run id in the PR body.
- [x] Review correction (round 2): no test comment still states round 2's bytes as the shown set's. The three
  the verifiers quoted are re-derived with the old value inline: the marker pin of `test_vote_tally_parity.py`
  reads 10 teammate coercions and 0 invalid targets (was 16 and 1), seed 2 m0 of `test_transcript.py` 12 pairs
  (was 9), and `test_validity_gate_cli.py` three `.v8` arm stamps (was two). The eleven present-tense headers they
  listed now name round 3 since 2026-10-09, with round 2's dates and readings labelled. The re-run found more
  round-2 readings stated as current in `test_beliefs.py`, `test_beliefs_hard_evidence_gate.py`,
  `test_contradictions.py`, `test_deduction_metrics.py`, `test_evidence_honesty.py`, `test_absence_prior.py`,
  `test_main.py` and `test_manager.py`; each is re-derived the same way, listed under "Review corrections,
  round 2" in Results with the count-only command that reads it. Mechanism: the scan
  `git grep -n -i -E 'candidate round 2|since 2026-10-02' -- tests/`, re-run at the fix head (16 hits, each
  classified in Results); perturbed: the same scan at `18febe41` lists 31, the stale state. The seventeen edited
  files pass (1397 passed).
- [x] Review correction: the replaced-era check reads the shown set's era off the registry, never a fixed id.
  `test_the_replaced_era_check_reads_the_shown_sets_era_off_the_registry` files `samples/9p2i` under round 2 beside
  the grown before file (no error: round 2 shows baseline 9's block, the era it replaced) and then leaves round 2's
  block alone (the exact no-block message). With `check_replaced_era`'s `era.id` read replaced by the literal
  `"stage-b-r3"` the test fails (mutant F1, killed).
- [x] Review correction: a tip record without a later set's win-split row is named, not skipped.
  `test_a_tip_record_without_a_later_sets_row_is_named` drops the `samples/9p2i` row of baseline 9's win-split table
  and asserts the one exact error. With the `tip_found` line of `check_repeated_claims` dropped it fails (mutant F2,
  killed); with that line's `not in errors` filter dropped, `test_missing_win_split_table_fails_loud` fails (F3,
  killed).
- [x] Review correction: the re-pin sweep is re-run over every file its pattern matches, production comments
  included, and each live-tense sentence still stating round 2's bytes as the shown set's is re-derived on round 3's
  bytes with its old value inline or labelled as round 2's: three production comments and the story (the next item),
  and twenty-one sentences in twelve test files, listed with their commands under "Review corrections, round 1"
  in Results. Mechanism: the sweep's `git grep` pattern and the era-name scan, re-run at the fix head; the targeted
  suites pass.
- [x] Review correction: the four comments re-derived on round 3's bytes, old value inline. `eval/watchability.py`
  39 of 54 vent flags (was 38 of 53; `measure_baseline.py --watchability --json`); `eval/vote_correctness.py` 0.7826
  beside 46/61 = 0.7541, 15 of 61 crewmates (was 0.7955, 44/66 = 0.6667, 22 of 66; the report gz);
  `TournamentDashboard.tsx` 36 of 46, 0.783 (was 35 of 44, 0.795); `MeetingView.stories.tsx` 27 of 702 (was 28 of
  691; `measure_featured_criterion.py --set 9p2i --alternatives`), with the seed-2 example dropped (seed 2 now lists
  none, 0 of 7). `check_doc_facts.py`, which reads `eval/vote_correctness.py`, exits 0.
- [x] Review correction: the media table's GIF row reads 13 frames again. `ffprobe -count_frames` on the committed
  GIF (sha256 `754e61b3...1cc8`, the provenance digest) reads 640x400, 13 frames, 8.5 s: twelve of 0.5 s and one of
  2.5 s, the 17 captured stills after Pillow merges repeats. `test_public_recording_provenance.py` passes.
- [x] **Round 2's bytes are kept as the candidate copy `replays/candidates/stage-b-r2`, identically** (the
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
- [x] **Round 3's bytes move in, identically.** Then `git mv` round 3's 50 replays, `MANIFEST.md`, `roster.json` and
  report gz into `replays/samples/9p2i`, and its `experiment-config.json` to
  `replays/samples/9p2i/experiment-config.json`; round 3's `README.md` is deleted with the emptied round directory.
  Mechanism: each moved file's sha256 equals the candidate file's at this card's base (listed in the promotion
  record); the validity gate on `samples/9p2i` passes with the model, zero cost, the four prompt pairs,
  `--expected-experiment-config` that file, `--expected-seeds 0-49` and `--require-one-recording-sha`;
  `verify_samples.sh` and `build_sample_report.py --sample-dir replays/samples/9p2i --check` pass. Perturbed:
  `--expected-seeds 0-50` exits 1, and so does round 2's config as the expected one. `git diff --stat <base>..HEAD` is
  empty over `replays/samples/4p1i`, `replays/candidates/stage-b-r1/`, every `replays/ml_corpus/` set file, `training/`
  and `agents/tactical/learned/`.
- [x] **One era registry, held to the bytes.** `eval/eras.py` gains `STAGE_B_R3` (record: the round-3 audit; date:
  the MANIFEST's `refreshed_at`; declared config: the in-tree file above) and files `samples/9p2i` under it; `ERAS`
  and `COMMITTED_SETS` drop `STAGE_B_R2`, whose constant stays, with one docstring line, for the candidate copy and
  the route instruments' r2 column, its declared config at `replays/candidates/stage-b-r2/experiment-config.json`.
  Mechanism: `tests/eval/test_eras.py` folds each set's games to one census `EraKey`, one key
  per era id, the declared file equal to every game's config, and `ERAS` equal to the registered eras. Planted: the
  registry filing `samples/9p2i` under `stage-b-r2` fails; a scratch set with one game's config edited fails; `ERAS`
  still listing `STAGE_B_R2` fails.
- [x] **The instruments group by era.** The scorecard, the census, the counterfactual and `measure_baseline.py` read
  the registry and pool only within an era; the counterfactual's `--sets samples/9p2i` refuses, naming `stage-b-r3`.
  Mechanism: `publish_process_scorecard.py --check` and `publish_gameplay_census.py --check`, after regenerating
  `docs/process-scorecard.*` and `docs/gameplay-census.*` by their publishers. Planted: a pool over two eras raises,
  and so does a hand-built input list filing `samples/9p2i` under `baseline-9`.
- [x] **The before column grows by the recording it replaced, as D12's clause is settled before dispatch.** Whether
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
- [x] **The census agreement follows the bytes.** No test reads a round column's recordings at a HEAD path that no
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
- [x] **Watchability: a stage block for the shown era; scoring frozen.** `_BASELINE_SUPPLY_FLOORS` gains `stage-b-r3`
  with only a `9p2i` entry, each pin measured on the promoted bytes and passing at equality, and the default resolves
  `samples/9p2i` to it (`default_baseline_id`, `eval/watchability.py:2475` at `225d2b77`). The `stage-b-r2` block,
  whose bytes left, is deleted with its equality tests and one history line (craft rule 3). `baseline-9`'s entries
  stay byte-identical as history and as the ML selection floor. The referee's gauges, rules, scoring and
  `REFEREE_READS` do not change; Results confirms the route field's recorded layer review against the promoted bytes.
  Mechanism: `tests/eval/test_watchability.py`; `measure_baseline.py --watchability --json` on each untouched set is
  byte-identical at base and head, measured directly and quoted with its sha256. Planted: one stage pin raised by one
  numerator fails its set; a recording carrying one setting outside `REFEREE_READS` is refused, naming the field.
- [x] **The recorder records the next round against the new era.** A run aimed at `samples/9p2i` must carry round 3's
  config sha256, read from the registry's declared file (`era_target_problem`, `scripts/_declared_experiment.py:396`
  at `225d2b77`). Mechanism: `tests/scripts/test_refresh_samples.py` and `refresh_samples.sh --dry-run`. Planted: a
  bare run, round 2's config and round 3's config with one byte changed, each aimed at `samples/9p2i`, refuse; round
  3's config aimed at `samples/4p1i` or `ml_corpus/9p2i` refuses; aimed at `samples/9p2i` it passes the dry run.
- [x] **The candidate-round rule, and its rows.** `replays/candidates/stage-b-r3/` is deleted, its record citing the
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
- [x] **The route field is named, in plain words,** as the orchestrator's step in the round-3 audit names it; adopted
  is the default the record card's menu gives for the era-keyed promotion. On that default, the "Adopted arms"
  paragraph of `docs/experiment-arms.md` gains one dated sentence naming `route_lines_version = 1` and the step;
  `ADOPTED_RULES` gains the field; `SPECTATOR_COPY.adoptedRules` gains plain words ("each voter sees a line about
  which stated places the map can link", or close; "route line" is defined at `docs/glossary.md:293`). No switch is
  deleted; graduation waits for a full re-record. Mechanism: `frontend/src/lib/adoptedRules.test.ts` (the list held
  to the paragraph and to the shown set's declared config) and `PublicResults.test.tsx`. Planted: the base seven-rule
  list fails against the new paragraph; a config without the field renders no route words; the copy gate
  (`frontend/src/lib/copy.test.ts`) stays clean.
- [x] **The doc facts read per-set provenance** (`scripts/check_doc_facts.py`; planted cases in
  `tests/scripts/test_check_doc_facts.py`). The win split comes from the promotion record's
  `| set | round-2 impostor rate | promoted impostor rate |` table, keyed `stage-b-r3` in `_WIN_SPLIT_HEADERS`;
  `stage-b-r2`'s key retires unless a history claim still reads it. Each dated claim names its set and equals that
  set's MANIFEST date. The composite-stamp parse reads the route arm's token, and the vote-correctness lead-in
  (`eval/vote_correctness.py`) names each era's id, model and tokens. Planted: "48% (9p2i)" as the current figure
  fails; "the 2026-10-01 record (9p2i)" as current fails; a fixture MANIFEST with round 3's stamp and the route token
  dropped fails; the base front door run against the promoted tree fails, naming at least the 9p2i date, the 9p2i rate
  and the era sentence.
- [x] **The front door is current, under the budgets.** `README.md` re-derives its results cells, the before cells
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
- [x] **The strip is re-picked by the measured criterion.** `FEATURED_GAMES` keeps 4p1i seeds 2, 11 and 29 unchanged.
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
- [x] **The category clause is re-proved by perturbation.** `test_the_role_proof_clause_rejects_a_recategorised_head`
  is re-targeted to the new head: its role-proof flag recategorised as `cross_statement`, the criterion rejects it by
  the flag clause (`match=`), and the weakened predicate accepts it. Mechanism: that test. Proof: its green run on the
  new head and its red run with the clause weakened, quoted in Results.
- [x] **Every label is true and spoils nothing.** Each 9p2i label states only countable facts (meetings and spoken
  turns in `_assert_featured_counts`' number words; a reported vent sighting; "no flagged contradictions" for a
  flag-free pick) and poses one question, naming no ending, player or vote. Mechanism: the spoiler test and
  `test_current_featured_claims_match_source_and_gate_bites`, re-parametrized. Planted: each label fails with its
  meetings removed, and each flag claim with only its flags stripped.
- [x] **The curated cases are re-derived or withdrawn, and always on the strip.** Each case in `_curated_cases` is
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
- [x] **The viewer's corpus fixtures and their census twins.** `replay-skeleton.fixture.json`, `bodies.fixture.json`
  and `contradictions.fixture.json` are regenerated by their recipes (`frontend/src/lib/skeleton.testkit.ts` and the
  fixture tests), 4p1i halves unchanged. On the promoted bytes the corpse age reproduces `corpse_age_at_report`, the
  no-reply note `accused_opener_answers`, the exit-ended vent windows `ticks_inside_per_trip`, the regroup-ended trips
  `trips_closed_by_regroup`, and the regroup note's count of meetings that end their game is re-derived. Mechanism:
  vitest over the regenerated fixture, bound by `corpusSha256`. Planted: the retired pairing rule, kept as the
  control, fails the new census; the base fixture fails against the new digest.
- [x] **The e2e head-card guard, green both ways, and the evidence journey.** `frontend/e2e/journey.spec.ts`'s main
  leg takes the "has evidence" branch on the new head; its planted twin opens pick (b) by exact pill text and walks the
  "no flags" branch (or opens 4p1i seed 11 through `?set=4p1i` if there is no pick (b)).
  `frontend/e2e/evidence-journey.ts` walks the kept cases with the source link matching the new root (unless the D14 card derived it) and re-enters its
  evidence legs through a kept case or the head's first cited observation. Mechanism: CI's `frontend-e2e` job
  (`npm run e2e`). Planted: pick (b)'s label without "no flagged contradictions" fails the guard's pairing assertion;
  the base evidence journey against the promoted tree fails.
- [x] **The reading guide's exhibits follow the strip.** The exhibit paragraph (`docs/reading-guide.md:71-75` at
  `225d2b77`) names at least two featured promoted games and their meetings in counts. Mechanism:
  `check_featured_exhibits` and the 1,350-word ceiling. Planted: the paragraph naming a seed the strip dropped fails.
- [x] **The README hero and media are re-captured on the new head.** `HERO` (`frontend/e2e/media.spec.ts`) is
  re-chosen on the new head at a tick where the omniscient half and a fog subject's half differ, every caption clause
  asserted against the served bytes, the caption claiming only what each half shows. The capture runs as
  `AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts` (an existing switch, not a new lever);
  `docs/media/provenance.json`, `docs/media/README.md`, the stills, the README caption and the media row of
  `docs/artifacts.md` follow. Mechanism: `tests/scripts/test_public_recording_provenance.py`
  (`test_media_hashes_and_labels_are_current`, `test_the_captions_scene_is_the_recorded_one`). Planted: the base
  caption against the promoted bytes fails by name; a moved digest fails.
- [x] **The game-shape profile is re-derived by its publisher.** `uv run python scripts/publish_game_profile.py`
  rewrites `replays/samples/9p2i/results-game-profile.json` and `docs/game-profile.md` on the promoted bytes, the leak
  and saturation classes recomputed for the era; `test_the_promoted_set_ships_its_profile_on_its_own_key` reads P's
  MANIFEST key; the Highlights bake follows the new strip. Mechanism: `publish_game_profile.py --check`, run twice
  with no diff. Planted: the base profile left in the promoted tree fails `--check`, naming the file.
- [x] **The re-pin sweep, old to new.** Every test, fixture and comment that reads or cites `samples/9p2i` bytes or the
  `stage-b-r2` era (re-counted at dispatch by the Validation command, plus helper indirection) is re-derived through
  its production computation, with its old value inline (`# was <old>` or `// was <old>`). Instruments that refuse the
  era assert their named refusal, and the one-sha MANIFEST test reads P's sha. Mechanism: CI's green run. Proof: each
  changed pin fails at the base bytes, quoted per file family, and `git diff <base>..HEAD -- tests/ frontend/src/`
  counts the inline notes per file.
- [x] **The corpus and the ML evidence do not move.** Mechanism: `scripts/verify_ml_evidence.py` offline (never
  `--complete`) and `uv run pytest -m campaign` by hand, at base and head with the same per-leg verdicts and both
  counts recorded; `tests/scripts/test_champion_flip_ruling.py` holds `(11, 50)` unchanged; `BAKEOFF_BASELINE_ID` and
  every FROZEN line are unchanged. Planted: a stale samples file count fails the inventory leg. Any ML figure keyed to
  `samples/9p2i` bytes stops the card.
- [x] **The promotion record.** A dated section closes the round-3 audit after the orchestrator's step. It holds the
  step and the rulings verbatim (8.8, 8.9 and its amendment); the per-file sha256 identity both ways: between
  `replays/samples/9p2i` at base and `replays/candidates/stage-b-r2/` at head, and between
  `replays/candidates/stage-b-r3/` at base and `replays/samples/9p2i` at head (each replay, the MANIFEST, `roster.json`,
  the report gz and the config); the win-split table; the before column's form, its owner word or recorded default, the
  old and new digests and the reversal; the commits that held round 2's and round 3's bytes at their old paths; and the
  candidate-round rule as the amendment states it. Every earlier section stays byte-identical. Mechanism: a section-by-section
  comparison against the record's merge (0 differing lines) and `check_doc_facts.py`. Perturbed: one character edited
  in an earlier section of a scratch copy gives differing lines and exit 1.
- [x] **The bundle change, stated file by file, in one checkout.** `build_demo_bundle.py --out <scratch>/before` runs
  at the base and `--out <scratch>/after` at the head, in the same checkout, so unchanged files keep their mtimes.
  `diff -rq` lists every changed path in Results and the PR body: the 9p2i replays added and removed by seed, the 9p2i
  summary and cases, the profile, the picker metadata and `assets/`. `data/4p1i/` is identical. Perturbed, in scratch
  and reverted: one 4p1i seed swapped shows `data/4p1i/` in the diff.
- [x] **The gate, recorded as CI.** CI's green run at the exact pushed head, cited by run id in Results and the PR,
  is the gate record (memo 8.7 item 1): `project-checks` (`bash scripts/check.sh`), `frontend-checks` and
  `frontend-e2e`. No local `check.sh` runs at the final head, and no commit exists only to record a gate. Run locally
  and quoted: the media capture, the campaign tier, offline `verify_ml_evidence.py`, the bundle diff and the base-side
  red runs.
- [x] **One bounded mutation pass.** Each mutant is applied alone over the lines this card writes, its targeted suite
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

Built on `work/promote-round-3` from `origin/main` at `2eed2e92` (`B` below), on 2026-10-09, after the round-3
record (`c71ea63e`, PR #505) and `retire-era-locked-pins` (PR #506) merged; `main` did not move under the branch, so
nothing was merged in. The step this card executes is section 11 of `audits/audit-2026-10-09-stage-b-r3.md`, the
orchestrator's promotion of round 3 under the owner's delegation (memo 8.8). Every census here is count-only: no
rendered prompt, transcript text or seed-band prefix was printed, band 2100-2999 stayed unseen, the held-out
generator was not run, no provider was called and the untracked `.env` was not read. Scratch work stayed under the
session scratchpad and nothing from it is committed. The Status line is the orchestrator's (Constraints, "One writer
per file"); this commit fills Results and the acceptance boxes only.

**Commits.** `5095a1c2` the byte moves (the bytes commit); `526fd409` the era registry; `60059688` the game-shape
profile; `fc77fc50` the route-check twin and r2's constant; `2e291780` the watchability stage block; `28d1a3a5` the
grown before column; `20fca2fa` the census per era; `37c65945` the recorder and the counterfactual; `c0eff87d` the
candidate rule and its rows; `c94b0844` the route field's public words; `c0592a13` the strip and the cases;
`7e4498f2` the viewer fixtures; `d9feb09d` the honesty cells; `5c82536e` the route-lines twin and round 2's
classification; `d9c3ada3` the promotion record (section 12); `7f65759b` the front door and the checker;
`75a8817d` the viewer stamps; `58c7cf03` strict typing of the census helpers; `c9e1a601` the media re-capture;
`9b763a98` the replaced-era plants; `b9cb15fa` the two tests the mutation pass asked for; `7dfda292` the
plant's import for strict mypy; then this Results commit.

**Sections relied on.** This card; `docs/architecture.md` ("Determinism and the substrate ladder", eras and the
ladder tip, the layering and the firewall); `docs/agent-procedures.md` ("Retiring substrate levers", "Environment
and history", "GitHub operations"); `docs/workflow.md`; `docs/artifacts.md`; `docs/experiment-arms.md`; the decision
memo sections 8.7 to 8.9 with the amendment of 2026-10-09; the round-3 record sections 1 to 11; the promote-round-2
and spectator-tour-round-2 cards for the shapes reused.

### Decisions

Orchestrator rulings, as given at dispatch and recorded here:
1. Round 2 is kept by `git mv` as `replays/candidates/stage-b-r2` with a declaration README; the registry's
   `STAGE_B_R2` entry is re-pointed at that copy's config; the route-check instrument reads r2's column config
   through the constant `R2_CONFIG_PATH` (the path its commit holds); round 3's candidate directory is retired; the
   artifact rows are recomputed.
2. The before column takes the grow form (the orchestrator's dated default in memo 8.9, which the owner may replace):
   the baseline-9 block stays byte for byte and round 2's block is appended. Reversal: deleting the appended block
   restores the old file's content, and the old pin `b6b8ecaa...38a7` with it.
3. The frozen referee's walk already declares the route field's layer (`REFEREE_READS`, its review recorded in
   `eval/watchability.py`); nothing is widened, and the stage block is re-derived on round 3's bytes.
4. The game-shape profile is re-derived by its publisher; Highlights reads the new shelves.
5. The route field is a recorded setting, not adopted: the public page names it in plain words beside the kill
   cooldown through `SPECTATOR_COPY.routeLines`, and `ADOPTED_RULES` and the "Adopted arms" paragraph stay at seven
   pairs. This replaces the card's menu default (adopted); `docs/experiment-arms.md` gains one dated sentence
   naming `route_lines_version = 1` as a setting these recordings carry.
6. The tour is re-curated as the card describes: strip re-picked by the measured criterion, cases re-derived or
   withdrawn, the source root moved to the bytes commit, the e2e guard green both ways, the guide's exhibits and the
   README hero and media re-captured.
7. The re-pin sweep includes the three front-door literals (flag partition, scaffold leakage, citation
   compliance), each re-derived by its instrument with the old value inline.
8. Publication: the PR body states the copy that goes live and the bundle diff file by file; the merge is the
   orchestrator's.

Decisions of this build:
- **The strip keeps its seeds.** Re-measured on round 3's bytes, the criterion still picks 9p2i seed 19 as the head
  and seed 14 as the second card (details under the strip item). The pre-meeting play of every seed is the same on
  both rounds (the route lines act only at the meeting), so the eligible list and the vent behaviours repeat; the
  reasons are re-measured, not carried.
- **Both curated cases are kept, re-derived.** `witnessed-vent` (supported) and `weak-evidence` (unresolved) on seed
  19 pass `_check_case` sentence by sentence against round 3's served replay, meeting memory and moves; only the
  seed-19 sha constant, the source root and the fingerprint key move. No case frames a wrong-but-believable ejection;
  `disputed-route` stays withdrawn.
- **The hero is kept.** `HERO` stays seed 19 at tick 9 with fog subject p-5 and accused p-4: the harness re-reads each
  caption clause off the served bytes and passes; the hero grows to 2036x909 because the accusation card is longer.
- **The r3 lab column is recorded at `60059688`, not at the bytes commit.** At `5095a1c2` the shown set's
  `results-game-profile.json` still held round 2's profile, so a column pinned there could not pass the census's
  shallow-clone proof against HEAD (a stale profile blob beside the recordings). `60059688` holds the same recording
  bytes plus the regenerated profile; every r3 recording blob is identical at both commits.
- **The route-lines twin gains an r3 column too** (`experiments/lab/results-route-lines-replay.json` and its report,
  outside Expected scope): the census reach test reads every column of that twin, and without the shown set's column
  it could not run over r3. Mode `served`, M 29, reach 26, W 7 of 7, parity true; s9, r1 and r2 unchanged.
- **One evidence-mechanism exhibit changes status.** In `tests/api/fixtures/evidence_mechanisms.py` seed 23's
  meeting 1 now ejects a crewmate (PARTLY FLIPPED, was FLIPPED) and seed 12's meeting 0 carries one weak
  alibi-versus-sighting flag; the planted source tuple is re-derived `(1, 0, 0)`. These are measured facts of round
  3's bytes, re-pinned with the old values inline.
- **The commit trailer.** Commits from `d9c3ada3` on end with `Co-Authored-By: Claude Opus 5.5
  <noreply@anthropic.com>`, the model that wrote them after a mid-session model change; the earlier commits carry
  the card's `Claude Fable 5.1` line. Both keep the `Card:` trailer immediately before. Correction (review round
  3): this is a deviation from the Delivery constraint, not a decision; "Review corrections, round 3" records it.
- **The README names the route lines as a recorded setting** in its samples paragraph ("plus the route lines, a
  recorded setting"), so the stamp's third arm is not read as adopted.

### Acceptance evidence

- **Round 2 kept, identically.** The per-file sha256 table (54 files, 0 differing) is section 12.2 of the round-3
  record. `tests/scripts/test_candidate_sets.py` reads rounds 1 and 2 (`test_the_committed_rounds_are_round_1_and_round_2`),
  with planted cases: one byte of the moved config fails the declared sha, a declaration naming `9p2i seeds 0-50`
  fails the seed check, and a stray file in round 2's directory fails. `bash scripts/verify_samples.sh` bare exits 0
  over both committed sets and both rounds; `python -m experiments.lab.route_check_replay --check` exits 0
  (reproduced, 58.3 s). Planted: `test_r2_read_at_the_registrys_new_path_fails_at_its_own_commit` fails naming the
  path. The README's copy passes the identifier and threshold scan.
- **Round 3 moved in, identically.** Section 12.2's second table (54 files, 0 differing). The validity gate on
  `samples/9p2i` with the model, zero cost, the four prompt pairs, the declared config, seeds 0-49 and one
  recording sha: exit 0, ten checks PASS (119 resolved meetings, 702 ballots, 0 dangling). Perturbed: seeds 0-50
  exits 1 (seed 50 missing from replays and MANIFEST); round 2's config as the expected one exits 1 (every game's
  recorded config differs). `verify_samples.sh replays/samples/9p2i` and `build_sample_report.py --check` exit 0 on
  all six sets. `git diff --stat B..HEAD` over `replays/samples/4p1i`, `replays/candidates/stage-b-r1`, `training`,
  `agents/tactical/learned`, `engine`, `agents`, `meetings`, `observation`, `llm` and `tests/fixtures` is empty;
  under `replays/ml_corpus` only the top-level README's dated note moves.
- **One era registry.** `eval/eras.py` names `STAGE_B_R3` (record the round-3 audit, 2026-10-09, config
  `replays/samples/9p2i/experiment-config.json`) and files `samples/9p2i` under it; `STAGE_B_R2` keeps its constant
  for the candidate copy. `tests/eval/test_eras.py` passes, with planted cases: filing `samples/9p2i` under
  `stage-b-r2` is refused ("seed 0 recorded settings that differ from the stage-b-r2 era's declared config"), one
  game's config edited fails, and `ERAS` listing `STAGE_B_R2` fails.
- **The instruments group by era.** `publish_process_scorecard.py --check` and `publish_gameplay_census.py --check`
  exit 0 after regeneration; the counterfactual's refusal names `stage-b-r3`; the pool and hand-built-list plants
  are re-pointed to the new era id and fail as before.
- **The before column grows.** `docs/process-scorecard-before.json` holds two blocks, the head's first equal to the
  base file's only block leaf for leaf and as text; `BEFORE_COLUMNS_SHA256` moves `b6b8ecaa...38a7` to
  `df88d369...363b` with a dated comment line; `samples/9p2i` (now `stage-b-r3`) reads the `stage-b-r2` block.
  Planted: an edited leaf of either block refuses the fold naming the file; a scratch registry filing
  `samples/9p2i` under `stage-b-r2` reads the baseline-9 block and fails the page's `--check`; a duplicated
  (set, era) block is refused.
- **The census follows the bytes.** `recording_blob_problems` takes the HEAD path and the files lifted beside it;
  r2 is read at `replays/candidates/stage-b-r2/9p2i`, r3 at `replays/samples/9p2i`, and the shallow-clone proof
  rebuilds each recorded tree. The r3 column was written by the instrument's own command (M 29, W 7, R 25,
  R_W 7). Planted: one r3 (and r2) misjudged flag flipped names its meeting; one replay changed at a moved
  column's new path fails by name; r2 read at its recorded path fails against the promoted tree.
- **Watchability.** The `stage-b-r3` block pins 14/192, 54/119 (transcript 15/119, persisted vent 39/119) and
  46/94, each at equality; the `stage-b-r2` block (14/195, 53/117, 44/94) is deleted with one history line.
  Gauges, rules, scoring and `REFEREE_READS` are unchanged. `measure_baseline.py --watchability --json` is
  byte-identical at `B` and the head on `samples/4p1i` (`badba42d...97c9`), `ml_corpus/9p2i` (`bc574592...365b`),
  `ml_corpus/4p1i` (`79055133...f24a`) and `candidates/stage-b-r1/9p2i` (`fef91745...2caf`).
- **The recorder.** `refresh_samples.sh --dry-run` aimed at `samples/9p2i` with round 3's config passes (no API
  call, nothing written); bare and round 2's config are refused, as are the planted cases in
  `tests/scripts/test_refresh_samples.py`.
- **The candidate rule and its rows.** `git ls-files replays/candidates | cut -d/ -f1-3 | sort -u` reads
  `README.md`, `stage-b-r1`, `stage-b-r3` at `B` and `README.md`, `stage-b-r1`, `stage-b-r2` at the head, 111 files
  at both. The family README states the amendment's rule with one dated history line. The golden's
  `candidates/stage-b-r3/9p2i` row retired, `candidates/stage-b-r2/9p2i` added (665 forced-ON over that copy), and
  `samples/9p2i`'s counted row reads round 3. `docs/artifacts.md`: candidates 111 files; audits 31,595,671 tracked
  bytes / 335 files; media 1.6 MB / 7 files. Offline `verify_ml_evidence.py` passes the inventory leg.
- **The route field in plain words.** Named as a recorded setting, not adopted (ruling 5, which replaces the
  card's adopted default): `SPECTATOR_COPY.routeLines` renders beside the kill cooldown, `ADOPTED_RULES` and the
  "Adopted arms" paragraph keep seven pairs, and `docs/experiment-arms.md` gains one dated sentence. No switch is
  deleted. `PublicResults.test.tsx` and `adoptedRules.test.ts` pass; planted: a config without the field (or with it
  null) renders no route words, and the route lines listed as adopted fail the pin; `copy.test.ts` stays clean. At
  `B` the two new tests fail (the shown config has no route field and the page names none).
- **Doc facts.** `check_doc_facts.py` exits 0. The win split reads the `stage-b-r3` table; a later era's before
  cells read the record of the era it replaced, named by id (`replaced_era`), and the scorecard's before block must
  name the same era (`check_replaced_era`). Planted (all in `tests/scripts/test_check_doc_facts.py`): "48% (9p2i)"
  as current fails; "the 2026-10-01 record (9p2i)" as current fails; a MANIFEST row with the route arm dropped fails;
  the README at `B`, and at `d41c9006`, dropped into the promoted tree each fail naming the 9p2i date, rate and era;
  the scorecard's before file as baseline 9's block alone fails naming both eras; an unnamed era raises.
- **The front door.** `wc -w`: README 1,587 of 1,600; reading guide 1,336 of 1,350; ML page 2,134 of 2,150;
  lessons 1,444 within 800-1,500; architecture 1,298 of 1,300. Results cells re-derived: impostor rate 34% (was
  48%); citations 397 / 397 (was 410 / 410); proof 24 / 24 = 1.0000 vs 22 / 37 = 0.5946 (was 24 / 24 vs 20 / 42 =
  0.4762); 15 of 15 innocent ejections in the no-proof cell (was 22 of 22); vent-backed 24 / 46 = 52% (was 24 / 44 =
  55%); the report example 61 ejections, vote correctness 0.783, ejection accuracy 0.754.
- **The strip.** On round 3's bytes eleven games open on a role-proof ejection (3, 5, 6, 7, 10, 11, 19, 20, 27, 42,
  49); three show both vent behaviours before their first meeting (6, 19, 20); seed 19 alone has its sighting from a
  second voice, so it stays the head. Five games are non-vent openers; seed 14 records no vent event at all and is
  pick (b). Neither is on the profile's wrong shelf. `tests/api/test_sets.py` holds the head, pick (b), the
  re-derived rejection cases (each with its `match=`) and the new wrong-shelf test, whose planted strip naming one
  shelf member fails naming it.
- **The category clause.** `test_the_role_proof_clause_rejects_a_recategorised_head` passes on seed 19 (the
  recategorised flag rejected by the flag clause; the weakened predicate accepts it).
- **Labels.** The spoiler test and `test_current_featured_claims_match_source_and_gate_bites` pass on round 3's
  bytes: seed 19 three meetings and nineteen turns, seed 14 one meeting and eight turns, unchanged.
- **The cases.** Kept and re-derived (Decisions). The 9p2i source root is `5095a1c2`, keyed by fingerprint
  `ea53a00f...5329`; the 4p1i root stays `9bae2b03`. `tests/api/test_public_results.py` passes with its per-family
  plants and the changed-source test.
- **Viewer fixtures.** Regenerated by their recipes; the 9p2i halves bind round 3's corpus digest (`3a31bb0a` to
  `9333c9d7`), the 4p1i halves are identical; 814 viewer tests pass, and the base fixtures failed against the new
  digest in five suites.
- **The e2e guard.** `npm run e2e`: 15 passed, 3 skipped (the media capture); the main leg takes the "has evidence"
  branch on seed 19, its twin opens seed 14 by exact pill and walks "no flags", and MISMATCH A (pick (b)'s label
  without "no flagged contradictions") throws. The evidence journey needs no change: `retire-era-locked-pins`
  derived its source links from the served summary, and its seed-19 legs hold on round 3's bytes.
- **The guide's exhibits.** Seed 19 (three meetings, nineteen turns), seed 14 (one meeting, eight turns) and 4p1i seed
  11; `check_featured_exhibits` passes.
- **Media.** Re-captured with `AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts` (3 passed); provenance
  names `01bbbd8b...f31c`, recorded 2026-10-09, era `stage-b-r3`, landed in `5095a1c2`, capture revision `58c7cf03`.
  `tests/scripts/test_public_recording_provenance.py` passes. Planted: the README caption at the base date
  (2026-10-01) fails `test_media_hashes_and_labels_are_current` (exit 1), and the provenance naming round 2's
  seed-19 digest fails the served-bytes check (exit 1).
- **The profile.** `publish_game_profile.py --check` exits 0, twice, no diff; Highlights reads the new shelves.
  Planted: the base profile left in the promoted tree fails `--check` naming
  `replays/samples/9p2i/results-game-profile.json` as stale (exit 1).
- **The sweep.** At dispatch the samples pattern matched 95 files under `tests/` and 14 under `frontend/`, 53
  production files, and 46 files outside `tasks/` and `audits/` named `stage-b-r2`. 43 test and viewer files changed;
  inline old values per file: honesty 40, watchability 16, deduction 7, census 6, eras 6, check_doc_facts 5, census
  publisher 4, and 1 to 3 in each of 17 more.
- **The corpus and the ML evidence.** Offline `verify_ml_evidence.py` at `B` and at the head: 64 checks, 52 OK, 0
  FAIL, 7 ABSENT, 5 INFO, per-leg verdicts identical. `pytest -m campaign`: 439 passed at `B` and at the head. The
  comparator stays 11 of 50; `BAKEOFF_BASELINE_ID` and every FROZEN line are unchanged. Planted: the samples
  row one file off (107 for 108) fails the in-tree inventory leg (exit 1).
- **The promotion record.** Section 12 of the round-3 record; sections 1 to 11 compared line by line against
  `c71ea63e`: 2,134 lines, 0 differing. Perturbed: one character edited in a scratch copy gives 2 differing lines and
  exit 1.
- **The bundle.** Built with `build_demo_bundle.py` at `B` and at the head in this checkout, then `diff -rq`: 38
  paths. `assets/`: 7 hashed chunks replaced (CanvasRenderer, MapView, ReplayPicker, TournamentDashboard,
  WebGLRenderer, WebGPURenderer, index); `index.html`; `data/9p2i/replays.json`, `eval/summary.json` and
  `eval/game-profile.json`; seed 19's replay, beliefs, three meeting files and twelve memory files; seed 14's
  replay, its meeting and one memory file. No 9p2i seed is added or removed, and `data/4p1i/` is identical.
  Perturbed in scratch: one unfeatured 4p1i seed dropped puts five `data/4p1i/` paths in the diff (a filename swap of
  a featured seed is refused by the builder, "featured seeds absent").
- **The gate.** CI at `c9e1a601`: run 37983570497 green (project checks, frontend checks, frontend e2e). At
  `9b763a98` run 37985126742 failed one gate, strict mypy on a test's import (fixed in `7dfda292`). At 7dfda292 run 37986165157 is green (project checks, frontend checks, frontend e2e).
  CI at the final head is cited by run id in the PR body (memo 8.7 item 1); no commit exists only to record it,
  and `check.sh` was not run locally at the final head.
- **Mutation.** One pass of 30 mutants (M1 to M31; M14 was withdrawn before the run as outside the listed
  classes), each applied alone with its targeted suite and the file restored; the tree was clean after. First run:
  27 killed, 3 survived. Two survivors were behavioural and `b9cb15fa` adds a test for each; re-run, both are
  killed. The third is equivalent: the viewer's type admits only `1` or `null` for the route field, so `=== 1` and
  `!= null` agree on every admitted value.

  | id | class | where | verdict |
  |---|---|---|---|
  | M1 | dropped filter | `before_column_of`, the set filter | survived, then killed |
  | M2 | comparison made a None test | `before_column_of`, the era match | killed |
  | M3 | dropped wrapper | `before_column_of`, the truncation | killed |
  | M4 | swapped collection | `before_column_of`, first block for last | killed |
  | M5 | dropped wrapper | `read_before_columns`, the seen set | killed |
  | M6 | message argument made a constant | duplicate-block refusal | killed |
  | M7 | loaded source read as its literal | publisher, the era id | killed |
  | M8 | dropped wrapper | publisher, `before_column_of` | killed |
  | M9 | swapped collection | `ERAS` naming round 2 | killed |
  | M10 | swapped collection | `samples/9p2i` filed under round 2 | killed |
  | M11 | loaded source read as its literal | round 2's config at the samples path | killed |
  | M12 | swapped branches | route check, r2 and r3 configs | killed |
  | M13 | loaded source read as its literal | route check, r3 config literal | killed |
  | M15 | dropped wrapper | `check_replaced_era` call | killed |
  | M16 | dropped filter | `check_replaced_era`, the era comparison | killed |
  | M17 | comparison made a None test | `check_replaced_era`, the tip guard | survived, then killed |
  | M18 | message argument made a constant | `check_replaced_era` message | killed |
  | M19 | swapped collection | `_REPLACED_ERAS` round 3 to the tip | killed |
  | M20 | dropped wrapper | `replaced_era`, the unnamed-era raise | killed |
  | M21 | swapped branches | win-rate source, history and tip | killed |
  | M22 | swapped collection | win-rate source, tip to manifest | killed |
  | M23 | loaded source read as its literal | `record_win_rates`, replaced era | killed |
  | M24 | loaded source read as its literal | `proof_set_records` | killed |
  | M25 | dropped tuple member | `stage-b-r3` win-split header | killed |
  | M26 | role, kind, room or tick read made a constant | tip-rate era read | killed |
  | M27 | swapped collection | watchability stage-block key | killed |
  | M28 | comparison made a None test | route words, version test | survived, equivalent |
  | M29 | dropped wrapper | route words, unconditional | killed |
  | M30 | dropped filter | route words, removed | killed |
  | M31 | loaded source read as its literal | seed-19 sha constant | killed |

**Base-side red runs.** The re-pin sweep's base side: the base tests on the swapped bytes (before any re-pin)
read 328 failed, by file: check_doc_facts 187, route_lines_arm 20, evidence_honesty 20, sets 12, route_check 11,
gameplay_census 10, game_profile_view 9, measure_featured_criterion 7, watchability 7, public_results 7,
publish_game_profile 5, build_demo_bundle 5, evidence_mechanisms 5, public_recording_provenance 4,
route_lines_replay 4, prompt_byte_golden 3, publish_gameplay_census 2, eras 2, deduction_metrics 2, and one each
in refresh_samples, process_scorecard, recording_fingerprint, watchability_reanchor, vote_correctness and
vj_instruments. The category clause's red run: with the criterion's flag clause weakened, the recategorised-head
test fails (exit 1). The card's new tests, copied onto `B`'s code and bytes: 18 failed and 11 errored at
collection (the symbols they read do not exist at `B`: `STAGE_B_R3`, `before_column_of`, `R2_CONFIG_PATH`), and 5
passed for stated reasons: the wrong-shelf guard and the head-choice test hold on round 2's bytes too (the same
seeds qualify), the moved-column drift test exercises the test file's own helper on a synthetic repository, and
the two summand tests re-target an existing read. On the viewer, the two new tests and two re-pinned ones fail at `B`.

**Follow-through outside Expected scope.** `experiments/lab/results-route-lines-replay.json` and its report (the
r3 column, Decisions); `tests/_helpers/committed.py` and `tests/_helpers/scripted_routes.py` (round 2's paths);
`tests/meetings/test_route_lines_arm.py` and `tests/orchestrator/test_recording_fingerprint.py` (re-pins);
`tests/api/fixtures/evidence_mechanisms.py`, `tests/api/test_evidence_mechanisms.py`,
`tests/eval/test_vote_correctness.py`, `tests/eval/test_vj_instruments.py`, `tests/eval/test_deduction_metrics.py`
(re-pins with old values inline); `frontend/src/components/BallotCard.tsx`, `PrivateReasoning.test.tsx` and two
stories (comments and stamps).

### Limitations

- The route field's public words describe a recorded setting; graduation waits for a full re-record.
- The before column's form is the orchestrator's recorded default; the owner may replace it before merge, and the
  reversal is one block.
- The r3 lab column sits at `60059688` rather than the bytes commit (Decisions).

### Review corrections, round 1 (2026-10-09)

Built on `work/promote-round-3` at `44546084`, the head the three verifier lenses read (CI run 37988023512 green
there). Five blocking findings and two Codex comments; each is repaired or refuted here, and no test is
weakened. Every census stayed count-only, no provider was called and the untracked `.env` was not read.

**The replaced-era read (correctness).** `check_replaced_era` picked the before block with `era.id`, but no test
filed the shown set under any era but `stage-b-r3`, so the literal `"stage-b-r3"` in its place survived.
`test_the_replaced_era_check_reads_the_shown_sets_era_off_the_registry` (in `tests/scripts/test_check_doc_facts.py`)
plants `era_of` as `STAGE_B_R2` beside the grown before file and asserts no error, because round 2 then shows the
baseline-9 block, the era round 2 replaced. It then leaves round 2's block alone and asserts the exact message
naming "the no era's block".

**The tip record's row (correctness).** The read of baseline 9's win-split table for a later era's set moved out of
`record_win_rates`, and no test removed that set's row, so dropping the line that reports it survived and claims
naming baseline 9 beside a 9p2i rate went unexamined. `test_a_tip_record_without_a_later_sets_row_is_named`
removes the `samples/9p2i` row from that table and asserts the one error, "the win-split table has no
'samples/9p2i' row".

**The sweep, re-run (integrity and docs).** The card's pattern
(`samples/9p2i|samples" / "9p2i|"samples", "9p2i"|SAMPLES_9P2I|9p2i seed [0-9]|committed 9p2i`) was re-run over
`tests/`, `frontend/` and the production trees, with a scan for `stage-b-r2`, "promoted stage-b-r2", the round-2
dates and the "round 2" phrasings. `agent_prompts/`, `design/`, the dated lab reports and the audits are history and
stay as written. Each sentence still stating round 2's bytes as the shown set's is now re-derived on round 3's bytes
with the old value inline, or labelled as round 2's.

| file | sentence | now (was) | command |
|---|---|---|---|
| `eval/watchability.py` | vent flags in `_supply_gauge_values` | 39 of 54 (38 of 53) | `measure_baseline.py --watchability --json replays/samples/9p2i`: flags 0.4538 and persisted vent 0.3277 over 119 meetings |
| `eval/vote_correctness.py` | the rate-versus-accuracy gap | 0.7826, 46/61 = 0.7541, 15 of 61 (0.7955, 44/66 = 0.6667, 22 of 66) | the `vote_correctness` block of each report gz, at the head and at `B` |
| `frontend/src/components/TournamentDashboard.tsx` | the rate is not 1.0 | 36 of 46, 0.783 (35 of 44, 0.795) | the same block |
| `frontend/src/stories/MeetingView.stories.tsx` | ballots listing the voter | 27 of 702 (28 of 691); the seed-2 example dropped | `measure_featured_criterion.py --set 9p2i --alternatives`; `--games 9p2i:2 --alternatives` reads 0 of 7 |
| `tests/eval/test_vj_instruments.py` | module docstring | stage-b-r3, three ballot overlays (two); ECE 0.2792 at n=397 (0.3049 at n=410); 36 of 61 zero-flag, 8 / 19 / 9 / 0, agreeing on 31 (40 of 66, 10 / 15 / 14 / 1, 35); the clamp-row count now a pointer to its test | `measure_baseline.py --vj --json` on `samples/9p2i` and on `candidates/stage-b-r2/9p2i`; the calibration fold reads 397, 0.2792, 0 excluded |
| `tests/meetings/test_manager.py` | inform-yield docstring | round 3, 2026-10-09; 65 / 20, 0 converted (66 / 17, 0) | `_derive_inform_yield()` from that module, called in a one-line `uv run python -c` |
| `tests/eval/test_deduction_metrics.py` | four sentences: the category comment, the redirect class, the weak-only class twice | round 3's bytes; its one weak-only conviction ejects an innocent at seed 12's first meeting (seed 8's p-9) | the test's own weak-only walk, run on each report; the report cell reads 1 and 1 |
| `tests/eval/test_reporter_justice.py` | three sentences | stage-b-r3 since 2026-10-09; the ledger equals its recorded ejections, 15 innocent of 61 (22 of 66) | `compute_reporter_justice(replays/samples/9p2i)`: 61, 15, 46 |
| `tests/eval/test_evidence_honesty.py` | five era comments | stage-b-r3; the off-mean note labelled as round 2's reading | era registry |
| `tests/eval/test_funnel.py`, `test_funnel_pooling.py`, `test_meeting_quality.py`, `test_gameplay_census.py` | one sentence each | the promoted stage-b-r3 bytes | era registry; each test passes on them |
| `tests/meetings/test_corroboration.py`, `test_prompt_byte_golden.py`, `tests/api/test_public_results.py` | one sentence each | round 3, promoted 2026-10-09 | era registry; each test passes on them |

Correction (review round 2): this paragraph first said every remaining hit was annotated with its round,
labelled as history or true of both rounds. That was wrong: fourteen test comments the round-2 verifiers named,
and more the re-run found, still stated round 2's bytes or readings as the shown set's. "Review corrections,
round 2" below re-derives them and lists what remains.

**The GIF row (docs).** `docs/media/README.md` reads "640×400, 13 frames" again. `ffprobe -count_frames` on the
committed GIF (sha256 `754e61b3...1cc8`, equal to `docs/media/provenance.json`) reads 640x400, 13 frames, 8.5 s,
and `-show_entries frame=duration_time` reads twelve frames of 0.5 s and one of 2.5 s. The capture takes 17 stills
at 0.5 s and Pillow merges the repeats. The note of `c9e1a601` ("the GIF has 17 frames") is wrong, and this line
corrects it; the pushed commit is not rewritten.

**Codex.** The P2 on `eval/watchability.py` (the docstring's 38 of 53) is the first row of the table above. The P1
("Record the promoted route field as adopted") is refuted, not taken. The acceptance item names the field "as the
orchestrator's step in the round-3 audit names it", with adopted only as the menu's default. Section 11 of that
audit promotes the round and names no adoption. The orchestrator's dispatch ruling 5 (Decisions) names the field a
recorded setting beside the cooldown, never called adopted, and AGENTS.md holds that task completion never
authorizes an experimental adoption. So `ADOPTED_RULES` and the "Adopted arms" paragraph keep seven pairs, and "Also
in place" is the true heading for the route lines.

**Mutation (bounded).** Three mutants over the named spans, each applied alone with the file restored after it (the
diff of `scripts/check_doc_facts.py` was empty after each):

| id | class | where | verdict |
|---|---|---|---|
| F1 | loaded source read as its literal | `check_replaced_era`, `era.id` to `"stage-b-r3"` | killed by the new registry-era test |
| F2 | dropped wrapper | `check_repeated_claims`, the `tip_found` report line | killed by the new tip-row test |
| F3 | dropped filter | the same line, `if error not in errors` | killed by `test_missing_win_split_table_fails_loud` |

**Verification at the fix head.** `pytest` over `test_check_doc_facts`, `test_deduction_metrics`, `test_funnel`,
`test_funnel_pooling`, `test_meeting_quality`, `test_vj_instruments`, `test_corroboration`, `test_gameplay_census`,
`test_reporter_justice`, `test_public_results`, `test_vote_correctness` and `test_watchability`: 1397 passed. Over
`test_evidence_honesty`, `test_manager` and `test_prompt_byte_golden`: 444 passed. `test_public_recording_provenance`:
31 passed. `check_doc_facts.py` exits 0. `ruff check` and `ruff format --check` are clean on the changed Python, and
`eslint` is clean on the two changed TSX files. The fix dispatch asks for one local `bash scripts/check.sh` at the
fix head. Its exit code and CI's run at the head are cited by run id in the PR body, and no commit records them.

### Review corrections, round 2 (2026-10-09)

Built on `work/promote-round-3` at `18febe41`, the head the verifier lenses read (CI run 37996822272 green there).
One blocking finding (the documentation lens); no new Codex comment. The change is comment-only: no production
line, no assertion and no recorded byte moves, and no test is weakened. Every census stayed count-only, no provider
was called and the untracked `.env` was not read.

**The finding.** The round-1 sweep stopped short. Test comments still stated round 2's bytes as the shown set's,
three of them with round 2's numbers, and the round-1 paragraph above claimed the rest were labelled. Two scans
found them: the verifiers' scan (`candidate round 2`, `since 2026-10-02`) and a second pass over every comment the
round-2 promotion (`0e67f42a`, `59bbd1be`) or the retirement card wrote that survives unchanged here, plus the prose
beside each re-pin this card made. Each sentence is re-derived on round 3's bytes with round 2's value inline, or
labelled as round 2's.

| file | sentence | now (was, on round 2's bytes) | read by |
|---|---|---|---|
| `tests/meetings/test_vote_tally_parity.py` | the set-list era comment; the marker pin | round 3 since 2026-10-09; `teammate_coerced` 10 and `invalid_target` 0 (16 and 1) | the marker loop of `test_committed_guard_marker_counts_are_pinned` over `_recorded_meetings` on `samples/9p2i` and `candidates/stage-b-r2/9p2i`: 119 meetings, 702 ballots (117, 691) |
| `tests/meetings/test_transcript.py` | seed 2 m0's pairs; the strong-flag surface | 12 pairs (9; 5 on the baseline-9 bytes); 39 strong, all `vent_sighting`, 15 weak (40: 38 `vent_sighting` and 2 `alibi_vs_physical`, 13 weak) | `detect_corroborations` on seed 2's first meeting with the ballot roster; `is_weak_contradiction` over every recorded flag of each set |
| `tests/scripts/test_validity_gate_cli.py` | the era-config comment; `_locked_pin`'s docstring | round 3, 2026-10-09; three `.v8` arm stamps (two) | `_locked_pin()` from that module: `ballot_kill_row_v1`, `impostor_ballot_v1` and `route_lines_v1` |
| `tests/scripts/test_measure_baseline_cli.py` | module docstring | round 3, its own era since 2026-10-09; the pins are held to the recorded surfaces | era registry; the test's own derivations |
| `tests/agents/test_absence_prior.py` | the era sentence; the emergency count twice | round 3 since 2026-10-09, cells derived; 4 emergency meetings (3) | `recorded_counts(...).applied_actions["emergency"]` on each set |
| `tests/agents/test_beliefs.py` | the class docstring and seven census sentences | innocent-reporter census 10 of 57 report ejections (17 of 63); buckets 3 exculpated, 6 already sub-gate, 1 out of the damp's reach (7, 9, 1); 28 hard-backed ejections (31); none innocent | the class's own walks (`_innocent_reporter_meetings`, `_rederive`, `_is_hard_backed`) run as a scratch subclass with `_SET_DIR` and the funnel pointed at each set |
| `tests/agents/test_beliefs_hard_evidence_gate.py` | five sentences | 57 report ejections (63); 28 soft-only (30); 29 hard-backed of 57 (33 of 63); sub-gate 11 crew + 4 impostor, over the gate 2 + 11 (16 + 1, 2 + 11); 119 meetings walked (117) | the class's `counterfactual` and `walk` fixtures, the same scratch subclass on each set |
| `tests/meetings/test_contradictions.py` | the exemption census; seven meeting totals; the corridor class; the one-segment routes | {CREWMATE: 3, IMPOSTOR: 1} / {whereabouts: 4} / 5 flags on both rounds, none STRONG; 650 committed meetings (648); 1 STRONG and 43 WEAK `alibi_vs_sighting` (1 and 44); 73 of 1,112 alibi claims one-segment (74 of 1,091) | `_committed_lever_census()`; `_iter_alibis(include_whereabouts=False)` keyed by event id over the four sets, which reproduces 74 of 1,091 with round 2's copy in the shown set's place |
| `tests/eval/test_deduction_metrics.py` | six sentences | impostor roll-call share 47.5% pooled and 46.5% macro (46.5%, 45.4%); role statements 1 on the sample set (0); 389 envelope quotations (415); 10 target rewrites (17); 192 kills, 14 crew-witnessed (195, 14); both partitions 37 (42) | `_committed()` on each set's report gz: `public_response_coverage`, `scaffold_leakage`, `witnessed_supply`, the two cross tabs, and the envelope loop of `test_the_pre_guard_body_is_the_parsed_field_not_the_raw_envelope` |
| `tests/eval/test_evidence_honesty.py` | four sentences beside this card's re-pins | 664 of 665 claim ticks rendered (631 of 632, the seed-47 example kept as round 2's); a STRONG band of 11 reads 4 (9 read 4); 0 impostors among 10 subjects and none under the grounded lever (1 among 7; 2 crewmates); one sole-flag victim, a crewmate whose STRONG flag the slate strips (none) | the pins beside each sentence: `(664, 664)`, `(0, 2, 0, 11, 4)`, `(10, 0)` and `(0, 0)`, `(1, 0)` with both still-strong sums 0 |
| `tests/_helpers/test_scripted_meeting.py`, `tests/eval/test_deception_instruments.py`, `tests/eval/test_off_menu.py`, `tests/training/test_conviction_model.py`, `tests/training/test_surrogate_dataset.py`, `tests/api/test_main.py`, `tests/meetings/test_manager.py` | one era sentence each | round 3 since 2026-10-09, round 2's dates labelled; the seed 3 m0 anchor holds on round 3's bytes | era registry; each test passes on the shown set |

**What remains.** The verifiers' scan, re-run at the fix head, lists 16 hits, and none states round 2's bytes as the
shown set's. Twelve are history with a date or a range: `_helpers/committed.py:739`, `test_eras.py:37`,
`test_vote_correctness.py:1961`, `test_watchability.py:138` and `:727`, `test_counterfactual_phase21.py:133`,
`test_refresh_samples.py:1927`, `test_surrogate_fidelity.py:67`, `test_corroboration.py:2609`,
`test_evidence_mechanisms.py:312`, `test_gameplay_census.py:1028` and the re-anchor note at `test_manager.py:5505`.
Four are true of both rounds: `test_impostor_policy.py:2310` (the recorded arm policy), `test_public_results.py:988`
(the experimental factory), `test_gameplay_facts_genuine_class.py:19` (the refusal) and
`test_surrogate_fidelity.py:429` (the corpus fold). A second scan for present-tense phrasings (`holds round 2`, `round 2 is shown`, `promoted
set, round 2`) finds two hits, a scratch plant in `test_route_lines_arm.py` and a commit's tree in
`test_route_check_replay.py`, both true. The `frontend/` comments name round 2's readings as round 2's.

**Mutation (bounded).** No mutant. Every change is a comment or a docstring, and no listed operator class applies
to prose. The spans the finding names are comments too, and the assertions beside them are unchanged.

**Verification at the fix head.** `pytest` over the seventeen edited files: 1397 passed. `ruff check` and
`ruff format --check` are clean, and `scripts/validate_task_docs.py` exits 0. The fix dispatch asks for one local
`bash scripts/check.sh` at the fix head. Its exit code and CI's run at the head are cited by run id in the PR body,
and no commit records them.

### Review corrections, round 3 (2026-10-09)

Built on `work/promote-round-3` at `9de107b9`, the head the documentation lens read (CI run 38004651235 and the
campaign-tier run 38004651280 green there). One blocking finding (the documentation lens) and three nonblocking
follow-throughs the orchestrator folded into the round, each a sentence the merge would otherwise publish or leave
stale. The round is documentation only (memo 8.7 item 4): one docstring, two comments, one registry row, this card
and the PR body. No recorded byte, replay, assertion or production line moves, and no test is weakened. Every census
stayed count-only, no provider was called and the untracked `.env` was not read. No new Codex comment: the two on
the PR (at `c9e1a601`) are answered under round 1.

**The shown report's size (the finding).** Three sentences gave round 2's report as the shown 9p2i report, by its
size. Each is re-derived on the promoted bytes with the old value inline.

| file | sentence | now (was, round 2's report) |
|---|---|---|
| `scripts/build_demo_bundle.py` | the module docstring's omitted-report clause | 34,579,235 bytes uncompressed, about 35 MB, 3,057,359 gzipped (32,952,472, about 33 MB, 2,790,383) |
| `frontend/src/api/client.ts` | the `getTournamentReport` comment | 35 MB (33 MB) |
| `frontend/e2e/bundle.spec.ts` | the compact-results case's comment | 35 MB (33 MB) |

Read by `gzip -dc replays/samples/9p2i/tournament-eval-report.json.gz | wc -c` (34579235) and `stat -f %z
replays/samples/9p2i/tournament-eval-report.json.gz` (3057359; `stat -c %s` on Linux). The same two commands on
`replays/candidates/stage-b-r2/9p2i/tournament-eval-report.json.gz` read 32952472 and 2790383, round 2's figures.
`gzip -dc replays/ml_corpus/9p2i/tournament-eval-report.json.gz | wc -c` reads 107690098, the docstring's corpus
figure, unchanged. The sweep
`git grep -n -E '32,?952,?472|2,?790,?383|33 ?MB|33MB|33 megabytes' -- . ':!tasks/work/promote-round-3.md'` lists 16
hits at `9de107b9` and at the fix head. At the fix head they are the three inline old values and 13 lines of history
in `tasks/work/post-promotion-follow-through.md` (11) and `tasks/work/promote-round-2.md` (2), round 2's cards
measuring round 2's bytes at their own heads. The present-tense scan `git grep -n -E '(is|one is) (33
MB|32,952,472)' -- .` lists 3 at `9de107b9` (the three above) and 0 at the fix head. A wider scan outside `tasks/`
and `audits/` (`32\.9|2\.79 ?MB|about 33|33 ?MiB|2\.[78] ?MB`) finds no other report size: one hit is an unrelated
percentage in `agent_prompts/` and one a lock-file hash. `docs/deployment.md` already reads 35 MB.

**The route-field box (folded in).** Its ticked text reads as the card's menu default; orchestrator ruling 5
delivered a recorded setting instead, and a new Review correction item at the head of Acceptance states that the
ruling replaces the box's text. The delivered words are pinned by `PublicResults.test.tsx` ("names the route lines
as set for these recordings, never adopted or experimental"), and the seven-pair list by `adoptedRules.test.ts`.
`npx vitest run src/api/client.test.ts src/lib/adoptedRules.test.ts src/components/PublicResults.test.tsx`: 57
passed.

**The experiments row (folded in).** `docs/artifacts.md` read `7.0 MB / 170 files`, measured at `B`; this card's
lab columns (`fc77fc50`: the r3 columns of both route instruments and the r2 constant) moved its bytes. Re-derived
by the audits row's formula, the row reads 7,558,279 tracked bytes / 170 files (was 7.0 MB / 170 files; 7,367,891
tracked bytes at `B`, so 190,388 added). Read by `git ls-tree -r -l HEAD -- experiments/lab experiments/model_probe
| awk '{s+=$4} END {print s}'` (and with `2eed2e92` for `B`) and `git ls-files experiments/lab
experiments/model_probe | wc -l` (170). A stated tracked-bytes figure is an exact promise:
`verify_ml_evidence.py`'s inventory parity sums the tracked files, so the row now moves with every lab byte, as the
audits row does. `test_every_counted_registry_row_matches_the_index` passes; planted, 7,558,280 fails it ("promises
7,558,280 tracked bytes, the tracked files contain 7,558,279 bytes"), and so does `B`'s 7,367,891.

**The gate item and the trailer (folded in).** The PR body's gate item called `18febe41` the final head. It now
names this round's pushed head as the final head and cites the CI runs in order: 37983570497 green at `c9e1a601`;
37985126742 and 37985880305 red at `9b763a98` and `b9cb15fa` (one strict-mypy error on a test's import, fixed in
`7dfda292`); 37986165157 green at `7dfda292`; 37988023512 at `44546084`, 37996481750 at `736dbdb0` and 37996822272
at `18febe41`, each green; 38004651235 and the campaign-tier run 38004651280 green at `9de107b9`; then the run at
this round's head, cited in the PR body.

Deviation, recorded 2026-10-09: the thirteen pushed commits `d9c3ada3` to `9de107b9` end with `Co-Authored-By:
Claude Opus 5.5 <noreply@anthropic.com>` in place of the line the Delivery constraint names, because their workers
followed a harness attribution reminder rather than the card. This is a deviation, not a decision. The precedent is
round 2's promotion: its twelve commits `148fa211` to `4a36dc03` (PR #495) carried the same line, recorded as a
deviation in `tasks/work/promote-round-2.md`, and were merged on the owner's words of 2026-10-02, "Merge both and
continue" (quoted in `tasks/work/post-promotion-follow-through.md`; the merge `0e67f42a` is recorded in section 8 of
the decision memo, before 8.1). Pushed commits are never rewritten. This round's commit, written by an Opus 5.5
worker, ends with the card's line verbatim, `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, directly
after the `Card:` trailer, checked with `git log -1 --format=%B` before the push.

**Mutation (bounded).** Two plants on the one gated span, the experiments row, each applied alone and reverted:
7,558,280 and `B`'s 7,367,891, both killed by `test_every_counted_registry_row_matches_the_index`. The other changes
are a docstring and comments, and no listed operator class applies to prose.

**Verification at the fix head.** `pytest tests/scripts/test_check_doc_facts.py tests/scripts/test_verify_ml_evidence.py`:
423 passed. `scripts/verify_ml_evidence.py` offline: 64 checks, 0 FAIL, the in-tree family inventory OK.
`tests/scripts/test_build_demo_bundle.py`: 34 passed. The three vitest files: 57 passed. `ruff check`
and `ruff format --check` are clean on `scripts/build_demo_bundle.py`, `eslint` is clean on the two changed
TypeScript files, `scripts/validate_task_docs.py` and `scripts/check_doc_facts.py` exit 0. `tests/docs/` does not
exist. No local `bash scripts/check.sh` runs at this head (memo 8.7 item 1): CI's green run at the pushed head, cited
by run id in the PR body, is the gate record, and no commit records it.

### Review corrections, round 4 (2026-10-09)

Built on `work/promote-round-3` at `a2ba69a9`, the head the documentation lens read (CI run 38008844971 and the
campaign-tier run 38008844981 green there). One blocking finding, from the documentation lens. The round is
documentation only (memo 8.7 item 4): this card and the PR body. No recorded byte, replay, comment, docstring,
assertion or production line moves, and no test is weakened. No census ran, no provider was called and the untracked
`.env` was not read. No new Codex comment: the two on the PR (at `c9e1a601`) are answered under round 1.

**The sweep count (the finding).** Round 3 stated that its sweep lists 16 hits at `9de107b9` and at the fix head. At
`a2ba69a9` the quoted command lists 26: the 16 classified there plus 10 lines of this card that quote the round-2
figures or the command itself, whose text matches through its `33MB` alternative. That exclusion was unstated. The
command now ends with the pathspec `':!tasks/work/promote-round-3.md'` in all three places it is quoted: the round-3
Review correction item, "Review corrections, round 3" and the PR body's round-3 item. Nothing else in those
sentences moves.

| head | with the pathspec | without it | this card's own lines |
|---|---|---|---|
| `9de107b9` | 16 | 16 | 0 |
| `a2ba69a9` | 16 | 26 | 10 |
| this round's head | 16 | 30 | 14 |

Read by
`git grep -n -E '32,?952,?472|2,?790,?383|33 ?MB|33MB|33 megabytes' <head> -- . ':!tasks/work/promote-round-3.md' | wc -l`,
the same without the pathspec, and with `-- tasks/work/promote-round-3.md`
alone for the card's own lines. At each head the 16 are one line each in `scripts/build_demo_bundle.py`,
`frontend/src/api/client.ts` and `frontend/e2e/bundle.spec.ts` (at `9de107b9` the three present-tense sentences
round 3 re-derived, since then their inline old values) and 13 lines of history in
`tasks/work/post-promotion-follow-through.md` (11) and `tasks/work/promote-round-2.md` (2). The present-tense scan
`git grep -n -E '(is|one is) (33 MB|32,952,472)' -- .` needs no pathspec: it lists 0 at `a2ba69a9` and at this
round's head, this card included.

**Mutation (bounded).** One perturbation on the stated count: the command without the pathspec, run at `a2ba69a9`,
lists 26, so the 16 stated there did not reproduce from the command as quoted. No other mutant: the changes are
prose in this card and the PR body, and no listed operator class applies to them.

**The trailer.** This round's commit, written by an Opus 5.5 worker, ends with the card's line verbatim,
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, directly after the `Card:` trailer, checked with `git log
-1 --format=%B` before the push. The thirteen earlier lines stay recorded as the deviation under round 3.

**Verification at the fix head.** `scripts/validate_task_docs.py` and `scripts/check_doc_facts.py` exit 0, and
`pytest tests/scripts/test_check_doc_facts.py` passes (333 passed). `tests/docs/` does not exist, and no
frontend file moves, so no vitest file is in reach. No local `bash scripts/check.sh` runs at this head (memo 8.7 item
1): CI's green run at the pushed head, cited by run id in the PR body, is the gate record, and no commit records it.
