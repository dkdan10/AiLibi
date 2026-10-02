# Promote candidate round 2 as the shown set

**Status:** done

## Outcome

Candidate round 2 (`replays/candidates/stage-b-r2/9p2i`: the seven adopted Stage-B arms, the kept vent exit and
`kill_cooldown_ticks = 6`, seeds 0-49) becomes the shown 9-player set, `replays/samples/9p2i`, replacing that
set's baseline-9 bytes in place, as every earlier adopting record replaced its samples. The other three sets
(`samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`) keep their baseline-9 bytes; the corpus stays FROZEN and
every ML artifact keeps its keys. The tree then holds two eras, and the project says so everywhere it counts:
- every instrument that pooled or keyed across the four sets groups them by recorded era and never pools
  across one; the shown 9-player set is published as its own era, with a dated before column where a
  report compares;
- the front door names each set's era and record; the substrate ladder tip stays at baseline 9, because no
  substrate lever moved, and baseline 10 stays reserved for the full re-record that re-freezes the corpus;
- the recorder records the next 9-player round against the new era's declared config and refuses the old one;
- round 2's candidate copy retires, because its bytes are now the samples set; round 1 stays as the comparison
  record.

The owner ruled on 2026-10-02, verbatim: "1. Merge 2. Promote and run the diagnostics." The merge is done
(`d41c9006`). This card is the promotion. The diagnostics named in the same ruling are separate, read-only
work and gate nothing here. This card's merge republishes the demo, the first of the wave's two
publications (the tour card's merge is the second), so the merge is the owner's.

## Evidence

Every `path:line` is at `d41c9006` (labelled as such) and is re-anchored by its symbol at dispatch. Every
count is reproducible from the tree or the named audits and is re-measured at dispatch; the dispatch figure
governs. Counts are count-only; no prompt, transcript or seed-band prefix is printed.

**The plan this card executes.** The decision memo (`tasks/decision-2026-09-24-stage-b-wave.md`, section 1,
"What adoption means later", item 2(b), and items 5, 7 and 8; section 7) names the era-keyed promotion as the
path compatible with the ML hold: era-keyed scorecard pooling, an era-keyed vote-correctness provenance check,
a watchability stage block, the public-results and tour minimum, and the s9 re-pin sweep. No v8 archive is
needed: there is no prompt bump, and the ballot arms already serve `v8.<arm>` overlay stamps from the recorded
config (`docs/experiment-arms.md`, "Config-only ballot fields"). `tasks/investigations-2026-09-24/partial_record.md`
section 5 lists the mixed-tree surfaces; rows 9-12, 15, 16 and 18-20 are this card's, and rows 13, 14 and 17
are shared with the sibling tour card (Constraints). Row 16 (the s9 digests in `bodies.test.ts` and
`contradictions.test.ts`) is this card's whole; the tour card adds only a census leg to `bodies.test.ts`.
The round-2 audit (`audits/audit-2026-10-01-stage-b-r2.md`)
gives the three columns (1.9), the assessment (6) and the menu (7); round 1's audit section 6 gives round 1's
column.

**The round-3 rule named no step; the owner's ruling is the authorization.** Every Conf. cell read 0 and the
win share (24/50 = 0.48) sat inside the envelope, but reporters ejected per report meeting read 17/114 =
0.149, flagged above the pre-registered 0.104, so the rule's promotion branch did not fire (audit 6.4, 7). The
owner's ruling of 2026-10-02 promotes regardless. The flag is a stated limitation of the promoted set, written
into the promotion record and the experiment-arms page; no reading is re-run or re-worded.

**The bytes.** Round 2 holds 50 replays, `MANIFEST.md` (one `git_sha`, `43b5ee45`; every row refreshed
2026-10-01; 24 impostor and 26 crew wins), `roster.json` (byte-identical to the samples set's) and the report
gz, which names no directory path (`gzip -dc | grep -c 'replays/\|candidates/\|stage-b-r2'` reads 0). The declared
config is `replays/candidates/stage-b-r2/experiment-config.json`, 316 bytes, sha256
`0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b` (audit 1.4). The validity gate passed on
the round with that config, seeds 0-49 and one recording sha (audit 5.1). `samples/9p2i` today holds 11/50
impostor wins, refreshed 2026-09-22, sha `27646d67`, plus `results-rubric-score.json`, which round 2 does not
have. `samples/4p1i` is 18/50, 2026-09-22.

**What breaks or misreads on a mixed tree** (code reading at `d41c9006`; the swap itself was not run here):
1. **Census.** `census_from_inputs` refuses sets at different kill cooldowns (`eval/gameplay_census.py:3270-3283`)
   and pools all four and both 9p2i sets (`:3292-3302`); `resolve_era` (`:517-545`) raises on any cross-era pool.
2. **Scorecard.** `compute_process_scorecard` pools all four and the two 9p2i sets with no era check
   (`eval/process_scorecard.py:1944-1953`); the page states "These four sets are one era"
   (`scripts/publish_process_scorecard.py:265`).
3. **Doc facts** (`scripts/check_doc_facts.py`). One tip audit (`:237`) owns every set's win split
   (`record_win_rates`, `:1601-1650`, header `:623`); one newest date across both manifests (`:1393-1405`, and
   `current_record_dates`, `:1544-1561`); one before column, "At baseline 8" (`:507`); the vote-correctness
   provenance requires all four sets to agree (`:2146-2275`); the corpus disclosures re-derive S9 from
   `samples/9p2i` (`:908-913`). The prompt-token parse ignores the `+` composite stamp (`:1362`, `:2197`):
   on round 2's MANIFEST it derives the families `qwen3_6_27b` and `v8`, the versions `v6` and
   `impostor_ballot_v1`, and drops `qwen3_6_27b.v8` and the kill-row arm (count-only run at authoring).
4. **Watchability.** `_DEFAULT_BASELINE_ID` is one global (`eval/watchability.py:1129`); the baseline-9 9p2i
   floors (`:1039-1076`: 3/175, 107/145, 79/112, 17/145, 90/145) are pinned on bytes that leave; the referee's
   walk profile (`:1542-1557`) does not support experiment recordings and is refused at
   `eval/replay_walk.py:566-578`; `BAKEOFF_BASELINE_ID = "baseline-9"` (`training/bakeoff/harness.py:188`)
   keys the ML selection floors separately.
5. **Counterfactual.** `CANONICAL_SETS` is four (`scripts/counterfactual_phase21.py:205-210`); its innocent
   pins key `samples/9p2i: 9` (`:261-266`); pooled pins (`tests/scripts/test_counterfactual_phase21.py:879-905`).
6. **Rubric.** The gameplay-facts extractor refuses Stage-B recordings by name (`tasks/work/stage-b-readers.md`),
   so neither `replays/samples/9p2i/results-rubric-score.json` nor `experiments/lab/results-rubric-geomean.json`
   can be regenerated; the 15.2 parity pin keys on the s9 MANIFEST sha (`tests/eval/test_watchability.py:126-193`);
   the recorder's rubric step runs whenever the target is `samples/9p2i` (`scripts/refresh_samples.sh:1125`).
   An unscored set is supported: the bundle skips it and the viewer shows its empty state
   (`scripts/build_demo_bundle.py:402-412`). The words of that state are not set-neutral:
   `interestingnessAbsentLead` (`frontend/src/lib/copy.ts:377`) says the absence is expected for 4p1i and that
   the default 9p2i set ships a rubric, and `ReplayPicker.tsx`'s empty state (`:390-404`) and banner
   (`:437-442`) blame 4p1i as the fast fixture, with 39 of its 50 games. Once the rubric goes, all three render
   on 9p2i in the published demo. The comments at `TournamentDashboard.tsx:889` and `:1193` and
   `GuidedTour.tsx:29-31` say the 9p2i default ships a rubric. `tests/scripts/test_build_demo_bundle.py:276-290`
   bakes the 9p2i rubric, the only committed one.
7. **Recorder.** `refuse_unsafe_target` refuses any switched-on config aimed at `replays/samples/`
   (`scripts/_declared_experiment.py:335-397`), and a bare run into `samples/9p2i` is allowed today.
8. **Tour guards.** `uv run python scripts/measure_featured_criterion.py --parent replays/candidates/stage-b-r2
   --games 9p2i:23 9p2i:0 9p2i:29 9p2i:2`: 0 of the 4 featured 9p2i games opens on a role-proof ejection
   (11 of 50 round-2 games do; 32 of 50 at baseline 9). So the head criterion, the featured labels, the
   three curated cases (sha-pinned at `api/public_results.py:35-41`), the e2e head guard and the guide's
   exhibits (`docs/reading-guide.md:67-75`) all fail or go false on the promoted bytes. The evidence journey
   (`frontend/e2e/evidence-journey.ts:8-30`) requires the 9p2i browser to show the rubric's score legend and
   not "ships no", then opens the cases "A sighting the table can check" and "Follow an accusation across the
   map" with a source link matching `9bae2b03`; `evidence.spec.ts` and `bundle.spec.ts` both run it, and CI's
   `frontend-e2e` job runs `npm run e2e`. `PublicResults.tsx:85` heads any non-empty case list "Three
   decisions to investigate", whatever the count. The guide's "Open Results & cases for source-bound examples"
   (`docs/reading-guide.md:67`) is false while the cases are withheld. The planted no-flags branch of the head
   guard (`frontend/e2e/journey.spec.ts:568-618`) opens 9p2i seed 2, which a one-card 9p2i strip drops.
9. **Golden.** `_RETIRED_GUARD_PINS` (`tests/meetings/test_prompt_byte_golden.py:1359-1364`): `samples/9p2i`
   (145, 845, 0, 0) and `candidates/stage-b-r2/9p2i` (117, 691, 0, 0).
10. **The sweep.** `git grep -l -E 'samples/9p2i|samples" / "9p2i|"samples", "9p2i"|SAMPLES_9P2I' -- tests/`
    lists 73 files. Widened to byte citations in code and comments,
    `git grep -l -E 'samples/9p2i|samples" / "9p2i|"samples", "9p2i"|SAMPLES_9P2I|9p2i seed [0-9]|committed 9p2i' -- tests/ frontend/src`
    lists 84 files under `tests/` and 8 under `frontend/src` (`BallotCard.tsx`, `EventTicker.tsx` and its
    test, `PrivateReasoning.test.tsx`, `TournamentDashboard.tsx`, `copy.ts` and two stories); the same pattern
    also matches readers and comments under `api/`, `eval/`, `orchestrator/` and `scripts/`. The frontend
    digests are `frontend/src/lib/bodies.test.ts:436-441` and `contradictions.test.ts:447-452`. Comments that
    cite s9 bytes include `BallotCard.tsx:111`, `copy.ts:425`, `EventTicker.tsx:117` and `:397` (seed 1's tick 7
    and tick 8) and `TournamentDashboard.tsx:262` (72 of 78).
11. **Registry rows.** `docs/artifacts.md:100` (samples, 40 MB / 107 files) and `:103` (candidates,
    70 MB / 111 files) hold the counts; `scripts/verify_ml_evidence.py` checks each against the git index
    (`_IN_TREE_PROBES` and `_IN_TREE_INVENTORY`, `:2755-2830`). The samples row's prose ("the baseline-9
    process re-record", "these are the canonical bytes") describes one era.
12. **Budgets** (`check_doc_facts.py:896-901`): README 1,469 of 1,600 words, reading guide 1,334 of 1,350,
    ML page 2,128 of 2,150 (`wc -w` at authoring).
13. **The leak paragraph.** `README.md:45-47` says default opening prompts reveal a hidden death tick through a
    body identifier and that the repair is unadopted; the reading guide's twin is `docs/reading-guide.md:44-46`.
    On round 2 the body handle reads 0 of 114 report openings (audit 6.2), so both go false for the shown set
    and stay true for the three baseline-9 sets.
14. **The candidates README.** `replays/candidates/README.md:21-23` says the committed sets are recorded with
    every switch off and that a candidate never replaces one of their bytes; both halves go false.

## Acceptance

Each item names its enforcing mechanism and a planted or perturbed proof. Each new test is written first and
fails at this card's base for the stated reason; Results quotes that run.

- [x] Review correction: the corrected-baseline re-derivation is pinned whole again. The operator command's
  serialized output on the promoted bytes (all seven blocks and `sample_dir`) is held to a sha256 literal, and
  its 44-site channel map to a sha256 of the map's sorted-key JSON; the old values ride beside them (the
  fixture's bytes and its 81-site map, each held by the W2 anchor test). Mechanism:
  `tests/eval/test_gate_spec_metrics.py::TestCommittedW2GateSpecPins::test_the_corrected_baseline_rederivation_is_pinned_whole`
  and `test_committed_ejections_decompose_into_channels`. Proof: probes G1 (`effective_deflection` built from
  the indistinguishability tally) and G2 (`supply_gauges` emptied) in `scripts/build_sample_report.py` pass at
  `4a36dc03` (30 passed) and fail now (1 failed each); `tests/fixtures/` is untouched.
- [x] Review correction: the reporter-justice era identity is held to its source. The promoted set's
  `recorded_settings` equals the exact nine off-default settings of `replays/samples/9p2i/experiment-config.json`
  (the literal is checked against the file); two scratch sets switching on the same nine fields with one value
  moved (`vent_exit_policy` to `observed_risk`) are refused by `pool_reporter_justice`, and the moved set's
  identity follows its recording; a set whose games recorded two configs is refused by
  `compute_reporter_justice`, with same-era controls passing. Mechanism: `tests/eval/test_reporter_justice.py`
  (`test_the_promoted_set_records_exactly_its_eras_off_default_settings`,
  `test_the_pool_refuses_two_eras_that_switch_the_same_fields`,
  `test_a_set_whose_games_recorded_two_configs_fails_loud`). Proof: mutants J1 (the off-default filter
  dropped), J2 (its comparison inverted) and J3x (the per-set refusal disabled) pass at `4a36dc03` (31 passed)
  and fail now.
- [x] Review correction: the recorder's era verdict follows the declared file on disk. A scratch checkout whose
  `replays/samples/9p2i/experiment-config.json` holds different valid bytes passes with that file's sha256 and
  refuses round 2's. Mechanism:
  `tests/scripts/test_refresh_samples.py::test_the_era_verdict_follows_the_declared_file_on_disk`. Proof: mutant
  D1 (the sha read replaced by round 2's literal sha) passes the head's suites and fails now.
- [x] Review correction: the champion-flip comparator is the owner's question, not this card's decision. The
  comparator reading sits in `scripts/regen_test_goldens.py`, outside Expected scope, and feeds three golden
  fields; it is held at its `d41c9006` reading (11 of 50), so no ML figure moves, while the owner rules.
  Mechanism: the open question in Results (Review corrections, round 1) and in the PR's Questions, marked
  blocking; `tests/scripts/test_champion_flip_ruling.py` holds the golden unchanged.
- [x] Review correction: the commit-trailer deviation is the owner's to rule on at merge. The twelve commits
  `148fa211` to `4a36dc03` carry the Opus 5.5 line, pushed and not rewritten; every later commit carries the
  card's Fable 5.1 line. Mechanism: the open question in Results and the PR's Questions; `git log
  --format=%B 4a36dc03..HEAD` shows the Fable 5.1 line on each fix commit.
- [x] Review correction: the reporter-justice comparison inversion (verifier docs' finding) is killed by the
  same planted pair as the filter: under `value == default`, the era and the moved config fold to the same
  identity and the pool would accept them; the planted case requires the refusal. Mechanism and proof as the
  reporter-justice correction above (J2).
- [x] **The bytes move, identically.** `git mv` round 2's 50 replays, `MANIFEST.md`, `roster.json` and report
  gz over `replays/samples/9p2i`, and its `experiment-config.json` to `replays/samples/9p2i/experiment-config.json`
  (the era's declared config, in-tree); delete `results-rubric-score.json` with the baseline-9 bytes. Mechanism:
  each moved file's sha256 equals the candidate file's at `d41c9006` (listed in the promotion record); the
  validity gate on `samples/9p2i` with `--expected-experiment-config` that file, `--expected-seeds 0-49` and
  `--require-one-recording-sha` passes; `build_sample_report.py --sample-dir replays/samples/9p2i --check` passes.
  Perturbed: `--expected-seeds 0-50` exits 1. `git diff --stat d41c9006..HEAD` is empty over `samples/4p1i`,
  `ml_corpus/` (every set file), `candidates/stage-b-r1`, `training/` and `agents/tactical/learned/`. Each set
  reader (set discovery, `verify_samples`, the bundle, the census and scorecard loaders, the recording
  fingerprint) accepts or ignores the config file. The fingerprint ignores it today
  (`orchestrator/recording_fingerprint.py:37-58`). Any reader that rejects it is fixed in this card, with a
  test that fails at the base on a scratch set holding the file, and is listed in Results.
- [x] **The candidate-round rule, and its rows.** Rule: a round whose bytes become a committed set is deleted in
  the promoting change, and its record cites the commit that held it (`d41c9006`); any other round stays
  until a later card names its retirement. Round 2's directory goes; round 1 stays as the comparison record
  both round audits read. This departs from the decision memo's proposal (section 1, item 7) that the card
  landing round r+1 deletes round r: round 1 is kept because both the round-1 and round-2 audits read it as a
  column, and the promotion record says so. `replays/candidates/README.md` states the rule and rewrites the
  whole "Not canonical" sentence (`:21-23`): the committed sets are not all recorded with every switch off
  (the shown 9-player set carries its era's declared config), and a candidate can now replace one of their
  sets by promotion. `docs/artifacts.md` rows are recomputed (`du -sh`, file counts), and the samples row's
  prose names both eras (the baseline-9 process re-record for three sets, round 2 for the shown 9-player set)
  in place of "these are the canonical bytes" of one record. Mechanism: `tests/scripts/test_candidate_sets.py`
  and `verify_ml_evidence.py`'s inventory parity against the git index. Planted: the old candidates count (111)
  left in the row fails parity.
- [x] **One era registry, held to the bytes.** One module (for example `eval/eras.py`, named in Results) maps
  each committed set to its era: id (`baseline-9` or `stage-b-r2`), owning record, declared config file or
  none. Every consumer below reads it; nothing else names a set's era. Mechanism: a test folds each set's games
  to the census `EraKey` and requires one key per set, one key per era id, and the declared file equal to
  every game's recorded config. Planted: the registry naming `samples/9p2i` as `baseline-9` fails; a scratch
  set with one game's config edited fails.
- [x] **The scorecard groups by era.** `compute_process_scorecard` groups sets by the registry, pools only
  within an era (the baseline-9 era pools its three sets; no 9-player pool remains), and publishes
  `samples/9p2i` as its own era with a before column: that set's entry of `docs/process-scorecard.json` at
  `d41c9006`, carried as a frozen block whose sha256 the module pins and the publisher never recomputes. The
  nine row definitions do not change; the schema version moves; the page's provenance text names both eras and
  dates. Mechanism: `publish_process_scorecard.py --check`. Planted: `pool` over two eras raises; one edited
  leaf of the before block fails `--check`.
- [x] **The census groups by era.** `census_from_inputs` groups by the registry; constants (the grace window)
  are per era; pools exist only within an era; the "One era" section becomes per-era. Mechanism:
  `publish_gameplay_census.py --check`. Planted: the existing cross-era `GameplayCensusEraError`, plus a
  hand-built input list putting `samples/9p2i` in the baseline-9 group, raises.
- [x] **The counterfactual stays in its era.** `CANONICAL_SETS` is the registry's baseline-9 sets (three); the
  `samples/9p2i` innocent pin leaves with a one-line history note; `--sets samples/9p2i` refuses, naming the
  era. Pooled pins are re-derived over the three sets and labelled as such, old to new in Results; the memo
  test holds `CANONICAL_SETS` to the memo's four sets less the promoted one. Planted: the four-set pins fail
  at the head; the refusal test.
- [x] **The doc facts read per-set provenance** (`scripts/check_doc_facts.py`, planted cases in
  `tests/scripts/test_check_doc_facts.py`):
  - each set's win split comes from its own record: `4p1i` from the tip audit's table, `9p2i` from the
    promotion record's `| set | baseline-9 impostor rate | promoted impostor rate |` table (11/50, 24/50);
    planted: "22% (9p2i)" in a live cell fails, and so does "48% (9p2i)" in a sentence naming baseline 9;
  - each refresh-date or current-record date claim names its set and equals that set's MANIFEST date;
    planted: "the 2026-09-22 record (9p2i)" fails, and a date naming both sets fails;
  - composite stamps split on `+` before the token parse, in both checks; planted: the d41c9006 parse fails
    a fixture MANIFEST carrying round 2's stamp;
  - vote-correctness provenance agrees within each era, and the lead-in names each era's id and tokens;
    planted: one era's token missing fails;
  - the ladder tip stays baseline 9 (`check_ladder_tip` unchanged), and the README's sample paragraph must name
    each set's era with its record link; "era" joins `_DIALECT_TERMS` with a glossary heading; planted: the
    whole `d41c9006` front door run against the promoted tree fails, naming at least the 9p2i date, the 9p2i
    win rate and the era sentence;
  - the conviction partition reads per-set rows: after, the promotion record's `samples/9p2i` row; before,
    the tip audit's `samples/9p2i` row; planted: the four-set "326 / 326 vs 43 / 85" kept as the current
    figure fails;
  - the corpus disclosures' S9 cells are held to their `d41c9006` values as history, named in the checker
    with that commit, as the baseline-2 block's precedent (`eval/watchability.py:560`); planted: one S9 cell
    moved fails.
- [x] **The front door changes, under the budgets.** Mechanism: `check_doc_facts.py` (facts, agreement,
  budgets). Proof: `wc -w` per page in Results, each at or under today's ceiling; raising one needs the
  owner's ratification, which this card does not carry. Perturbed: the `d41c9006` copy of each page, dropped
  into the promoted tree in scratch, fails the checker (the planted case above).
  - `README.md`: the line under "What the measurements said" names the shown 9-player set (recorded
    2026-10-01 under the adopted gameplay changes, its own era) beside baseline 9 (the 4-player set and the
    corpus); the before column is headed "Before", one cell per set's replaced recording; every ejection row
    reads `9p2i` alone, re-derived, its before that set's baseline-9 value; the four-set figures stay only in
    the history paragraph, past tense; the vent paragraph, the report example and the sample paragraph
    (per-set dates, 36% (4p1i), 48% (9p2i), both eras) are re-derived; the second header link reads
    "Inspect results and decisions", with no count; the "Known evidence leak" paragraph (`:45-47`) says, per
    era, that the shown 9-player set's report openings no longer carry the death tick (0 of 114) while the
    baseline-9 sets' still do, and that the temporal repair stays default-off.
  - `docs/reading-guide.md`: the same table and history wording, section 3's cross-tab narrative re-derived,
    the boundary paragraph (`:44-46`) saying, per era as the README does, that the shown set's openings no
    longer carry the death tick (body handle 0/114), and the exhibit paragraph held to the strip below;
    trimmed to fit 1,350.
  - `docs/glossary.md`: a new "era" entry; "baseline N" and "the ladder tip" each gain one sentence that the
    shown 9-player set moved to a later era while the ladder tip stands at baseline 9.
  - `docs/architecture.md`: the ladder paragraph gains the promotion (era, record, the three sets at baseline 9,
    instruments never pool across eras); "their experiments remain OFF and unadopted" is made true per era.
  - `docs/history.md` (one dated paragraph), `docs/ml-program.md:161` (era-attributed, no ML figure moves),
    `docs/experiment-arms.md` (round 2 becomes the shown set; the reporter flag stated), `docs/game-shape.md`
    (its rules per era), `audits/README.md` (the round-2 row), `replays/ml_corpus/README.md` (one dated note
    that S9 means the baseline-9 bytes as of `d41c9006`).
- [x] **Watchability: a stage block and a per-set default; scoring frozen.** `_BASELINE_SUPPLY_FLOORS` gains
  `stage-b-r2` with only a `9p2i` entry, every pin measured from the promoted bytes and passing at equality;
  the default id resolves per set from the registry (`samples/4p1i` to `baseline-9`, `samples/9p2i` to
  `stage-b-r2`), and `measure_baseline.py --watchability` follows it; baseline-9's `9p2i` entry stays byte-identical
  as history and as the ML selection floor. The referee's gauges, rules and every existing block are
  unchanged; its walk declares the layers it must read after a per-layer review recorded in Results. The 15.2
  parity pin keeps its fixture as history and retires its byte recomputation, as the baseline-2 block did.
  Mechanism: `tests/eval/test_watchability.py`. Planted: the referee's JSON on `samples/4p1i`,
  `ml_corpus/9p2i` and `ml_corpus/4p1i` is byte-identical at base and head; one stage pin raised by one
  numerator fails its set; a recording with one layer undeclared is refused, naming the field.
- [x] **The recorder records the next round against the new era.** A target in `replays/samples/<set>/` must
  carry exactly that set's declared config (sha256 of its `experiment-config.json`); a set with none takes
  no switched-on config; `replays/ml_corpus/` keeps refusing every switched-on config; the default target and
  the candidate rules are unchanged. The rubric step skips an era the extractor does not read, with one named
  line, and leaves no rubric. Mechanism: `scripts/_declared_experiment.py`, `refresh_samples.sh --dry-run`.
  Planted, each in `tests/scripts/test_refresh_samples.py` or `test_candidate_sets.py`: a bare run, round 1's
  config, and the era config with one byte changed, each aimed at `samples/9p2i`, refuse; the era config aimed
  at `samples/4p1i` or `ml_corpus/9p2i` refuses; the era config aimed at `samples/9p2i` passes the dry run.
- [x] **The holding edit on the tour surfaces.** The sibling tour card owns these files after this card; here
  only enough moves to keep the gates green and nothing false public (partial-record row 14):
  - `FEATURED_GAMES` keeps its `4p1i` entries and reduces 9p2i to one head chosen by the criterion, labelled
    with re-read meeting and turn counts only, with no "no flagged contradictions" promise;
  - `tests/api/test_sets.py` re-derives its pins and planted rejection seeds, deletes the seed-0 shape test
    with its card, and replaces `test_seed_7_isolates_the_role_proof_clause` (no round-2 game isolates the
    clause) with `test_the_role_proof_clause_rejects_a_recategorised_head`, the head's served replay with its
    role-proof flag recategorised as `cross_statement`;
  - `tests/api/test_public_results.py` re-derives the summary counts and pins the three cases as withheld by
    the source check, with no source link;
  - `frontend/e2e/journey.spec.ts` keeps both guard branches running: the main leg takes the "has evidence"
    branch on the head, and the planted no-flags branch opens `4p1i` seed 11 (its card promises no flagged
    contradictions) through the set switch (`?set=4p1i`, as the evidence journey already enters that set),
    because the one-card 9p2i strip has no no-flags card;
  - `frontend/e2e/evidence-journey.ts`: its 9p2i rubric leg flips to the unscored state (the set-level
    no-rubric banner shows, the score legend does not), both rubric legs (9p2i and 4p1i) match the set-neutral
    copy below rather than the old "ships no" wording, and the two case walks are replaced by a check that
    the 9p2i results show no case and no source link ("No source-matched editorial cases are published for
    this set", and no "Inspect this pinned source set and manifest" link); the evidence legs after them (the
    scene frame, the fog lens, the perspective switch, the missing reference) re-enter through the head's
    first cited observation, its ids re-read from the served replay, so they keep running;
  - the guide's exhibit paragraph names the head and `4p1i` seed 11 in counts, and its opening sentence
    ("Open Results & cases for source-bound examples", `docs/reading-guide.md:67`) is reworded so it promises
    no curated case for the 9-player set.

  Mechanism: those tests, check 16 of `check_doc_facts.py`, Playwright locally (`evidence.spec.ts`,
  `bundle.spec.ts` and `journey.spec.ts`). Planted: the old head (seed 23) fails the criterion with its
  `match=`; the `d41c9006` evidence journey run against the promoted tree fails on the score legend. Results
  lists every line changed, file by file, for the tour card to replace.
- [x] **The no-rubric copy is set-neutral.** The three strings that render when a set ships no rubric
  (`interestingnessAbsentLead` in `copy.ts`, and `ReplayPicker.tsx`'s empty state and banner) are rewritten
  with no claim about which set ships a rubric, no per-set counts and no "fast fixture" attribution; the copy
  gate (`frontend/src/lib/copy.test.ts`) stays clean. The comments at `TournamentDashboard.tsx:889` and
  `:1193` and `GuidedTour.tsx:29-31` stop saying the 9p2i default ships a rubric. Mechanism:
  `frontend/src/components/ReplayPicker.test.tsx`. Planted: a new 9p2i-unscored render (`rubricMissing`,
  `set="9p2i"`, both views) asserts the copy names no set as the unscored one and claims no rubric elsewhere;
  the `d41c9006` strings fail it.
- [x] **The kill cooldown has public words, and the cases heading has no count.**
  `frontend/src/components/PublicResults.tsx`'s behaviour list names a recorded kill cooldown in plain words,
  with its tick count (audit 1.11). Its cases heading ("Three decisions to investigate", `:85`) becomes
  count-free, so the tour card can keep one, two or three re-derived cases without a false count; the tour
  card does not touch this file. Mechanism: vitest render tests. Planted: a group differing only by its
  cooldown renders the new phrase, and fails without it; a one-case render carries no "Three", and the
  `d41c9006` heading fails it.
- [x] **The re-pin sweep, old to new.** Every test, fixture and code comment that reads or cites `samples/9p2i`
  bytes (re-counted at dispatch by the widened Evidence command over `tests/` and `frontend/src`, the same
  pattern over the production readers' comments, plus helper indirection) is re-derived by its production
  computation and listed old to new in Results; a comment whose example no longer exists on the promoted bytes
  (`EventTicker.tsx:117`, `:397`; `TournamentDashboard.tsx:262`) cites a promoted game re-read the same way, or
  names its set and era. Rates pooled across eras are split; pure counts of what the
  tree holds are re-pinned with a label; s9-only frontend digests (`bodies.fixture.json`,
  `contradictions.fixture.json`) are regenerated by their recipes, `4p1i` untouched. No committed set ships a
  rubric after the promotion, so `test_rubric_is_trimmed_to_the_baked_seeds`
  (`tests/scripts/test_build_demo_bundle.py:276-290`) keeps the rubric bake path covered with a synthetic
  rubric in a scratch samples directory, and Results says so. Instruments that keep
  refusing the era (off-menu, the anchor study, the surrogate and conviction tables) assert their named refusal
  on `samples/9p2i` instead of measuring it. The one-sha MANIFEST test (`tests/api/test_sets.py:372-384`) stays
  as written and reads `43b5ee45`. Mechanism: the full gate. Proof: each changed pin fails at the base bytes,
  quoted per file family.
- [x] **The corpus and the ML evidence do not move.** Mechanism: `uv run python scripts/verify_ml_evidence.py`
  (offline, every leg) and the campaign tier (`uv run pytest -m campaign`), both green at base and head with the
  same per-leg verdicts; `BAKEOFF_BASELINE_ID` and every FROZEN line unchanged. Planted: a stale samples file
  count fails the inventory leg. Any ML figure keyed to `samples/9p2i` bytes stops the card and goes to the
  owner.
- [x] **The promotion record.** A dated addendum, section 9 of `audits/audit-2026-10-01-stage-b-r2.md`: the
  owner's ruling verbatim; the rule's reading and the reporter flag; the per-file sha256 identity; the win-split
  and conviction-partition tables above; the before-column source; the candidate-round rule, its departure
  from the memo's item 7 and `d41c9006`; that the round's s9-at-baseline-9 column reproduces at `d41c9006`,
  not after. Sections 1 to 8 stay
  byte-identical. Mechanism: the audit's own section-1 comparison (0 differing lines) and `check_doc_facts.py`.
  Perturbed: one character edited in section 1 of a scratch copy gives differing lines and exit 1.
- [x] **Every gate, green.** `bash scripts/verify_samples.sh` (bare and per set), the five
  `build_sample_report.py --check` runs (two samples, two corpus, round 1), both publishers' `--check`,
  `check_doc_facts.py`, `validate_task_docs.py`, offline `verify_ml_evidence.py`, the campaign tier, a local
  Playwright run, and `bash scripts/check.sh`, each run to its end, real exit codes in Results.
  `measure_baseline.py replays/samples/9p2i --honesty --json` folds the set alone and reproduces the round-2
  audit's honesty cells 3 and 5; `--funnel` and `--vj` fold it alone too (no mode pools across sets).
  Perturbed: `verify_samples.sh` on a scratch copy of the promoted set with one replay byte flipped exits
  non-zero.

## Constraints

- **Authorization.** The owner's ruling of 2026-10-02 authorizes the promotion; no live provider call, no
  recorder run, no spend. The untracked `.env` is never read. No rendered prompt, transcript or seed-band
  prefix is printed; censuses are count-only.
- **Partial-record principle.** `samples/4p1i`, `ml_corpus/9p2i` and `ml_corpus/4p1i` keep verifying
  byte-identically; the corpus FROZEN lines, `training/provenance.py` keying and every ML artifact never move;
  ML stays held (ruling 12). No prompt bump, no ambient lever, no new experiment field; every default stays
  as it is, and a missing key keeps its historical meaning. Graduation (deleting switches, the config-field
  retirement procedure of memo item 6, baseline 10) waits for the full re-record.
- **The referee.** Its scoring stays frozen. Declaring its walk's layers is the one widening, taken because memo
  1(b) names the stage block as a promotion requirement; if the owner rules the referee keeps refusing, the
  stage block is not built, `samples/9p2i`'s default refuses by name, and the baseline-9 pins become history.
- **One writer at a time, with the sibling tour card**
  ([`spectator-tour-round-2`](spectator-tour-round-2.md)). This card owns the bytes move, the era registry, the
  instruments, the gates, the doc facts and front-door pages, the artifacts rows, the recorder rule, the
  re-pin sweep (frontend digests and count comments included), the set-neutral no-rubric copy
  (`copy.ts`'s `interestingnessAbsentLead`, `ReplayPicker.tsx`'s empty state and banner,
  `ReplayPicker.test.tsx`, and the comments in `TournamentDashboard.tsx` and `GuidedTour.tsx`, which the tour
  card leaves as written) and `PublicResults.tsx` whole: its kill-cooldown label and its count-free cases
  heading, which the tour card relies on and does not touch. It makes only the holding edit in `ReplayPicker.tsx`'s strip,
  `tests/api/test_sets.py`, `tests/api/test_public_results.py`, `frontend/e2e/journey.spec.ts`,
  `frontend/e2e/evidence-journey.ts` and the guide's exhibit paragraph; it does not touch
  `api/public_results.py`, `MapView.tsx`, `bodies.ts`, `measure_featured_criterion.py` or any spectator
  annotation. Files both cards write, in this order (this card, then the tour card, which dispatches from
  `main` after this merge): `frontend/src/components/ReplayPicker.tsx`, `tests/api/test_sets.py`,
  `tests/api/test_public_results.py`, `frontend/e2e/journey.spec.ts`, `frontend/e2e/evidence-journey.ts`,
  `docs/reading-guide.md` (the exhibit paragraph), `frontend/src/lib/copy.ts`,
  `frontend/src/lib/bodies.test.ts`, `tests/scripts/test_build_demo_bundle.py`,
  `tests/scripts/test_measure_featured_criterion.py` and `tasks/README.md`. The tour card replaces the holding
  edit and builds on the rest.
- **Publication.** `.github/workflows/pages.yml` republishes on every push to `main`. Two merges in this wave
  republish the demo: this card's, then the tour card's, and each merge is the owner's. What this card's merge
  puts live: one featured 9-player game (the holding head) and the whole promoted set's summary, the one-game
  9-player strip, no curated cases (the source check withholds them), no rubric for that set, the set-neutral
  no-rubric words and the new public words. That interim public state (one 9p2i card, no cases, no 9p2i
  rubric) lasts until the tour card merges. The PR states the bundle diff (`build_demo_bundle.py --out` at the
  base and the head, `diff -rq`) and that `data/4p1i/` is identical.
- **Copy.** User-facing copy carries no task or audit ID, no unexplained jargon ("era" is defined in the
  glossary; "Stage-B" and "regroup" are not user copy) and no threshold arithmetic.
- **Curation.** The holding head is chosen by the criterion, whose existing IMPOSTOR assert reads the ejected
  player's role to describe the strip: that read is curation and gates no record, instrument or adoption, as
  the census states of its own role reads (`docs/gameplay-census.md:5`).
- **Mixed-tree items deliberately left.** (1) The rubric extractor does not read the era, so the shown set
  ships no rubric and the 15.2 parity pin is history, until a card widens the extractor. (2) The corpus
  README's S9 figures are history. (3) Training reports naming `samples/9p2i`
  (`training/reports/report-finalist-eval.md`, `report-meeting-table.md`, `report-ballot-surrogate.md`)
  stay as dated history under the ML hold. (4) The tour work itself (the sibling card).
- **Delivery.** Branch `work/promote-round-2`, one PR into `main` with every section of the PR template,
  merged by merge commit or fast-forward, never squash. Each commit body ends with
  `Card: tasks/work/promote-round-2.md` immediately followed by the exact line
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Inspect consumers before changing a symbol; stop
  and ask on any protected decision this card does not name.

## Expected scope

- `replays/samples/9p2i/` (the moved bytes, the declared config, the rubric removed);
  `replays/candidates/stage-b-r2/` (deleted); `replays/candidates/README.md`.
- The era module (new) and its test; `eval/process_scorecard.py`, `eval/gameplay_census.py`,
  `eval/watchability.py`, the referee's walk declaration, `eval/vote_correctness.py` (lead-in and stamps).
- `scripts/check_doc_facts.py`, `scripts/publish_process_scorecard.py`, `scripts/publish_gameplay_census.py`,
  `scripts/counterfactual_phase21.py`, `scripts/measure_baseline.py`, `scripts/_declared_experiment.py`,
  `scripts/refresh_samples.sh`; `docs/process-scorecard.*`, `docs/gameplay-census.*` (regenerated).
- `README.md`, `docs/reading-guide.md`, `docs/glossary.md`, `docs/architecture.md`, `docs/history.md`,
  `docs/ml-program.md`, `docs/experiment-arms.md`, `docs/game-shape.md`, `docs/artifacts.md`, `audits/README.md`,
  `audits/audit-2026-10-01-stage-b-r2.md` (section 9 only), `replays/ml_corpus/README.md` (one note).
- The holding edit (Constraints), including `frontend/e2e/evidence-journey.ts`, and
  `frontend/src/components/PublicResults.tsx` with its test.
- The set-neutral no-rubric copy: `frontend/src/lib/copy.ts`, `frontend/src/components/ReplayPicker.tsx`,
  `frontend/src/components/ReplayPicker.test.tsx`, and the comments in `TournamentDashboard.tsx` and
  `GuidedTour.tsx`.
- Any set reader that rejects the in-tree `experiment-config.json`, with its test.
- The sweep: the s9-reading tests, `frontend/src/lib/{bodies,contradictions}.{test.ts,fixture.json}`, and the
  count and byte-citation comments in `BallotCard.tsx`, `EventTicker.tsx`, `TournamentDashboard.tsx`, `copy.ts`,
  the two stories and the production readers.
- `tasks/README.md` (inventory sentence, index line) and this card.

Directly necessary follow-through inside these boundaries is permitted and recorded in Results. Nothing
under `engine/`, `agents/`, `meetings/`, `llm/`, `training/`, `replays/ml_corpus/*/` or `tests/fixtures/`
changes.

## Record impact

The samples set's bytes change: `replays/samples/9p2i` now holds the round-2 recording, so every figure,
report and served game for that set moves, and the merge republishes the demo. No new recording is made, no
recorded byte is rewritten (each moved file keeps its sha256), and no future recording changes behaviour,
except that the recorder now requires the shown era's config for `samples/9p2i`. The three other sets, the
corpus, the ML fits and their keys, and round 1 are untouched. The substrate ladder tip stays at baseline 9.
Measurement: the gates in Validation at base and head, the per-era scorecard and census, and the stage block
measured at equality on the promoted bytes.

## Validation

```sh
# the bytes, at the head
uv run python scripts/validity_gate.py replays/samples/9p2i --expected-model Qwen/Qwen3.6-27B \
  --require-zero-cost --expected-prompt-versions <the four pairs, audit 5.1> \
  --expected-experiment-config replays/samples/9p2i/experiment-config.json \
  --expected-seeds 0-49 --require-one-recording-sha     # and --expected-seeds 0-50: exit 1
shasum -a 256 replays/samples/9p2i/experiment-config.json   # 0c02fa61...
bash scripts/verify_samples.sh                          # bare, then once per set directory
uv run python scripts/build_sample_report.py --sample-dir <each of the five sets> --check
# the sweep, re-counted (and the same pattern over the production readers' comments)
git grep -l -E 'samples/9p2i|samples" / "9p2i|"samples", "9p2i"|SAMPLES_9P2I|9p2i seed [0-9]|committed 9p2i' -- tests/ frontend/src
# the instruments and the facts
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/measure_baseline.py --watchability --json   # each set against its own era
uv run python scripts/measure_featured_criterion.py --set 9p2i    # the holding head
wc -w README.md docs/reading-guide.md docs/ml-program.md docs/lessons.md
# the corpus and the ML evidence, unchanged
uv run python scripts/verify_ml_evidence.py             # offline; never --complete
uv run pytest -m campaign
# the recorder, preview only
AILIBI_SAMPLE_DIR=replays/samples/9p2i AILIBI_MANIFEST=replays/samples/9p2i/MANIFEST.md \
  AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2 \
  bash scripts/refresh_samples.sh --dry-run --seeds 0 --expect-levers "" \
  --experiment-config replays/samples/9p2i/experiment-config.json   # passes; bare: refused
# the browser leg, locally, and the bundle diff, into scratch
cd frontend && npm run e2e
uv run python scripts/build_demo_bundle.py --out <scratch>/before|after && diff -rq <scratch>/before <scratch>/after
# the whole gate, in a clean worktree, run to its end
bash scripts/check.sh
```

Run each gate to its end: `set -e` in `check.sh` masks later gates. On macOS the evolution-strategy hash pin
is Linux-only; gate in a clean worktree and cite CI for it.

## Results

Done on `work/promote-round-2`, from `origin/main` at `23698a0f`. All counts below are count-only; no prompt,
transcript or seed-band prefix was printed. Scratch work stayed under the session scratchpad.

**Commits**, in order: `148fa211` the promoted bytes; `7900fdc8` the era registry; `e75780b7` the era-aware
instruments; `429d1b4b` the recorder rule; `2f2160d1` the viewer holding edit and set-neutral copy; `d29fa175`
the viewer digests and byte citations; `c7abd2a5` the Python re-pin sweep; `0ff6713f` the front door and the
doc facts; `b6f75091` the promotion record; `f3392317` this card's Results; `091bd2a5` the lint, format and
typing findings `check.sh` raised at `f3392317`; then the commit recording that run. Intermediate commits were
not gated one by one; the head is.

**Sections relied on.** This card; the decision memo (`tasks/decision-2026-09-24-stage-b-wave.md`) sections 1
(items 2(b), 5, 7, 8) and 7; `tasks/investigations-2026-09-24/partial_record.md` section 5 (rows 9-20); the
round-2 audit sections 1.4, 1.9, 1.10, 1.11, 5.1, 6 (6.2, 6.4), 7 and the new 9; round 1's audit section 6;
`docs/architecture.md`, "Determinism and the substrate ladder"; `docs/experiment-arms.md`.

### The bytes and the rule

- Round 2's 50 replays, `MANIFEST.md` and report moved into `replays/samples/9p2i` (`roster.json` was already
  byte-identical); its `experiment-config.json` is `replays/samples/9p2i/experiment-config.json`, sha256
  `0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b`, byte-identical to round 2's. Per-file
  sha256 list: the promotion record, section 9.3 (54 files, 0 differing against `d41c9006`). The set's
  `results-rubric-score.json` left with the baseline-9 bytes. `git diff --stat d41c9006..HEAD` is empty over
  `replays/samples/4p1i`, both `replays/ml_corpus/` set directories, `replays/candidates/stage-b-r1`,
  `training/`, `agents/`, `engine/`, `meetings/`, `llm/` and `tests/fixtures/`; under `replays/ml_corpus/` only
  the README gains its one dated note.
- **Set readers.** None rejects the in-tree config, so none was changed: set discovery and the bundle serve the
  set (the e2e and bundle runs below), `verify_samples.sh` globs replay files, the census and scorecard
  loaders read it through the registry, the validity gate takes it as `--expected-experiment-config`, and the
  recording fingerprint ignores it (`test_a_declared_experiment_config_is_not_a_recording`).
- **The candidate-round rule.** Round 2's directory is deleted; round 1 stays, because both round audits read it
  as a column. This departs from the memo's section 1 item 7 (the card landing round r+1 deletes round r), and
  section 9.9 of the record says so. `replays/candidates/README.md` states the rule and rewrites the "Not
  canonical" sentence. `docs/artifacts.md`: `replays/samples/` reads both eras, 39 MB / 107 files;
  `replays/candidates/` 35 MB / 56 files; `audits/` 28,136,878 tracked bytes / 333 files. Planted: the old
  candidates count, `70 MB / 111 files`, fails the inventory leg ("promises 111 files, the index tracks 56").

### The era registry and its consumers

`eval/eras.py` names two eras: `baseline-9` (record `audits/audit-2026-09-22-process-rerecord.md`, recorded
2026-09-22, no declared config: `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`) and `stage-b-r2` (record
`audits/audit-2026-10-01-stage-b-r2.md`, recorded 2026-10-01, declared config the file above:
`samples/9p2i`); `LADDER_TIP_ERA` is `baseline-9`. Consumers: `eval/process_scorecard.py`,
`eval/gameplay_census.py`, `eval/watchability.py`, `scripts/counterfactual_phase21.py`,
`scripts/_declared_experiment.py` (the recorder) and `scripts/check_doc_facts.py`. `tests/eval/test_eras.py`
folds each set's games to the census `EraKey` (one key per set, one per id, the declared file equal to every
game's config); planted: `samples/9p2i` filed under `baseline-9`, and a scratch set with one game's config
edited, each fail.

### The instruments

- **Scorecard**: groups by the registry; the baseline-9 era pools its three sets; `samples/9p2i` is its own era
  with its `d41c9006` entry carried verbatim in `docs/process-scorecard-before.json`, pinned at sha256
  `b6b8ecaa5ecdde48630a1cb5eec9628d799553fdd6911ab38efdb654e95e38a7`; `schema_version` 1 to 2. Planted:
  pooling two eras raises; one edited leaf of the before block turns `--check` red.
- **Census**: groups by the registry, the grace window per era, pools only within an era; planted: the
  cross-era error and a hand-built list filing `samples/9p2i` under baseline-9 raise.
- **Reporter justice** carries each set's recorded settings and refuses to pool two.
- **Counterfactual**: `CANONICAL_SETS` is the three baseline-9 sets; `--sets samples/9p2i` refuses naming the
  era; the pooled pins re-derived over three sets (accused without a first-hand source 529/1,516 to 422/1,192;
  ejected without one 16/409 to 12/321; answering turn 36/411 to 29/321; walkable pair 69/411 to 56/321;
  record section 9.8); innocent pins 32, 0, 1. The four-set pins fail at the head.
- **`measure_baseline.py`** folds each set alone in every mode; on `samples/9p2i` alone `--honesty` reproduces
  the round-2 audit's cells 3 (`0/111`) and 5 (23 kill holders, 21/23 citing; audit 6.2).

### Watchability, and the referee's layer review

`_BASELINE_SUPPLY_FLOORS` gains `stage-b-r2` with only a `9p2i` entry, measured on the promoted bytes and passing
at equality: witnessed-event rate 14/195, flags per meeting 53/117 (38 vent, 15 transcript), testimony-backed
conversion 44/94. The default block resolves per set (`samples/4p1i` to `baseline-9`, `samples/9p2i` to
`stage-b-r2`); baseline-9's 9p2i entry is byte-identical as history and as the ML selection floor
(`BAKEOFF_BASELINE_ID` unchanged). The 15.2 parity pin keeps its fixture as history and retires its byte
recomputation. **Layer review** (recorded beside `REFEREE_READS`): engine (`vent_witness_rule`,
`kill_cooldown_ticks`, `redistribution_policy`) threaded by `engine_arguments`; orchestrator (`meeting_reset`,
`report_body_handle_version`) applied through the shared helper, the handle touching only report trigger text no
gauge reads; tactical (`vent_exit_policy`, `vent_entry_policy`) reaching the walk only as recorded actions;
meeting (`bounded_rebuttal_version`, `ballot_kill_row_version`, `impostor_ballot_version`) read as recorded
rows, the suspicion-graph parse reading only the suspicion block both ballot arms leave in place. Gauges, rules
and scoring are unchanged; every other setting stays refused. Planted: each stage pin raised by one numerator
fails its set; a recording with one layer undeclared is refused naming the field; the referee's JSON on
`samples/4p1i` and both corpus sets is byte-identical at base and head (`tests/eval/test_watchability.py`).

### The recorder

A target in `replays/samples/<set>/` whose era declares a config must carry that file's sha256; a declared
config missing from disk is refused by name; a set with none takes no switched-on config; `ml_corpus/` refuses
every one; the default target and the candidate rules are unchanged; the rubric step skips the era with one
named line. Planted (`tests/scripts/test_refresh_samples.py`): a bare run, round 1's config and the era config
with one byte changed, aimed at `samples/9p2i`, refuse; the era config aimed at `samples/4p1i` or
`ml_corpus/9p2i` refuses; the era config aimed at `samples/9p2i` passes the dry run.

### The doc facts and the front door

`scripts/check_doc_facts.py` reads per-set provenance: each set's win split from its own era record (4p1i from
the tip audit's table, 9p2i from section 9.5: 11/50 to 24/50), a promoted rate in a sentence naming baseline 9
held to the history value; each dated claim names its set and equals that set's MANIFEST date; composite stamps
split on `+` in both checks; the vote-correctness lead-in names each era's id, model and tokens, matched whole;
the proof row reads `samples/9p2i` alone (after: section 9.6, `24 / 24 = 1.0000 vs 20 / 42 = 0.4762`; before:
the tip audit's `samples/9p2i` rows, `70 / 70 = 1.0000 vs 11 / 20 = 0.5500`, the two records held to each
other); the pooled reads are still checked where the history paragraph quotes them; the S9 disclosure cells are
history (145/145, crew 635/635, impostor 104/210, re-derived from the `d41c9006` report) named with that commit;
"era" joined `_DIALECT_TERMS` with its glossary heading. Planted, each red against the promoted tree: the whole
`d41c9006` README (names the 9p2i date, the 9p2i rate and the era sentence); `22% (9p2i)` in a live cell;
`48% (9p2i)` in a baseline-9 sentence; `the 2026-09-22 record (9p2i)`; a date naming both sets; the old token
parse on round 2's stamp; one era's token missing; the four-set `326 / 326 vs 43 / 85` as the current figure;
one S9 cell moved. The front door: `README.md`, `docs/reading-guide.md`, `docs/glossary.md` (era entry, two
sentences), `docs/architecture.md`, `docs/history.md`, `docs/ml-program.md:161`, `docs/experiment-arms.md`,
`docs/game-shape.md`, `audits/README.md`, `replays/ml_corpus/README.md`, plus `docs/ownership-case-study.md`
(two stale live-tense sentences). Words (`wc -w`): README 1,544 of 1,600; reading guide 1,325 of 1,350; ML page
2,134 of 2,150; lessons 1,444 (800-1,500); architecture 1,300 of 1,300. `eval/vote_correctness.py`: the
9p2i stamp `35/44 = 0.7955` (was 76/81), lead-in per era, zero-flag text 20 of 44, 11 rescued, 9 unbacked.

### The holding edit, file by file (for the tour card to replace)

- `frontend/src/components/ReplayPicker.tsx`: `FEATURED_GAMES` keeps 4p1i seeds 2, 11, 29 and reduces 9p2i to
  seed 3 (first meeting ejects on a role-proof flag: 1 of 1; the old head, seed 23, 0 of 1), labelled "Four
  meetings, twenty-three spoken turns. Read which each ballot cites, and who else its voter weighed."; the
  comment above the list.
- `tests/api/test_sets.py`: pins and planted seeds re-derived; the seed-0 shape test deleted with its card;
  `test_seed_7_isolates_the_role_proof_clause` replaced by
  `test_the_role_proof_clause_rejects_a_recategorised_head`.
- `tests/api/test_public_results.py`: summary counts re-derived; `test_the_curated_cases_are_withheld_by_their_source_check`;
  `test_the_disputed_route_meeting_is_absent_from_the_promoted_game`.
- `frontend/e2e/journey.spec.ts`: the no-flags branch opens 4p1i seed 11 via `?set=4p1i`; the vent-route guard
  holds the feed's routes, as a multiset, to the served exit events (44 of the promoted set's 72 exits surface
  where the impostor dived).
- `frontend/e2e/evidence-journey.ts`: both rubric legs read the unscored, set-neutral state; the case walks are
  replaced by a no-case, no-source-link check; the scene, fog, perspective and missing-reference legs enter
  through the head's first cited observation, ids read from the served replay.
- `docs/reading-guide.md` exhibit paragraph: names 9p2i seed 3 and 4p1i seed 11 in counts and promises no
  curated 9-player case. `frontend/src/components/GuidedTour.tsx` intro: "for each set's figures and any
  decisions to investigate" (was "for three decisions to investigate").
- `tests/scripts/test_build_demo_bundle.py`: the rubric bake path runs on a scratch samples directory holding
  two promoted games and a synthetic rubric stamped with that directory's key; the committed sets bake no rubric.
- `tests/scripts/test_measure_featured_criterion.py`: the alternatives shapes re-read (seed 2 (7, 10, 2, 0),
  seed 13 (13, 22, 1, 0), seed 3 (19, 26, 1, 0), seed 23 (12, 24, 0, 0)).

### The set-neutral copy, and the public words

- `interestingnessAbsentLead`: "The selected set ships no rubric — expected for 4p1i, the fast technical fixture
  (median 12 ticks, at most one meeting per game). Switch back to the default 9p2i set, which ships one, or run"
  becomes "The selected set ships no rubric, so its games carry no interestingness score. To score them, run".
- Empty state: "ships no rubric — expected for 4p1i, the fast technical fixture: median 12 ticks, at most one
  meeting (39 of its 50 games hold exactly one, 11 hold none)[, and 23 of 50 decided by the task timer...]. Browse
  Replays to inspect this set without highlight scores." becomes "ships no interestingness rubric, so its games
  carry no highlight scores. Browse Replays to inspect this set without them."
- Banner: "... — its games are unscored. 4p1i is a fast technical fixture (median 12 ticks, at most one meeting
  per game), not the spectator set." becomes "... — its games are unscored."
- `PublicResults.tsx`: a recorded cooldown reads "a kill cooldown of 6 ticks set for these recordings"; the
  cases heading "Three decisions to investigate" becomes "Decisions to investigate".

### The re-pin sweep

Every re-pinned literal carries its old value inline (`# was <old>` or `// was <old>`): 527 of them across 38
files (`git diff d41c9006..HEAD -- tests/ frontend/src/ | grep -c "was"` style count, per file: deduction 59,
evidence honesty 61, measure_baseline CLI 51, vj instruments 36, vote correctness 28, meeting quality 23,
funnel pooling 22, funnel 21, reporter justice 21, kill craft 16, wave-2 metrics 16, gate spec 14, solvability
13, bodies 11, absence prior 11, and fewer elsewhere). Headlines: ballots 845 to 691, eject ballots 496 to 410,
meetings 145 to 117, ejections 90 to 66, impostor wins 11 to 24, vote correctness 76/81 to 35/44, the
retired-guard census (145, 845, 0, 0) to (117, 691, 0, 0), the body census 1,208 to 2,039 frames, the flag
census 127 to 73. Instruments that refuse the era (off-menu, the anchor study, the surrogate, conviction and
fidelity tables, the gameplay-facts extractor) assert their named refusal on `samples/9p2i` and run their
property cases on `ml_corpus/9p2i`; the fidelity harness's FO-6 pins move to the corpus read 5-fold (top-1 25/90
to 142/273; ejection meetings 90 to 273; skips 86 to 164). The I-11 live-repair claims move to `ml_corpus/9p2i`
(44/747 declined); the promoted set folds under its recorded arm policy, pinned separately (55/297). Comments
citing the set's bytes are re-read or name their recording (ticker cases 9p2i seed 0 tick 27 and seed 1 tick
10; 20,783 agent-frames; 28 of 691 self-listing ballots; the baseline-6 seed 22 redirect; the deduction
docstrings' triage-era figures named as baseline-6). Frontend digests regenerated by their recipes, 4p1i halves
unchanged. The one-sha MANIFEST test reads `43b5ee45` unchanged.

### Planted failures, red and green

- Head tests against the base code and bytes (a `git archive` of `origin/main`): 447 failed, 15 collection errors
  (modules importing `eval.eras`), 3,089 passed — per family, check_doc_facts 202, validity-gate CLI 23,
  deduction 22, census 13, test_sets 11, census publisher 10, contradictions 10, reporter justice 10, and so on
  across 53 files. Head frontend tests against the base: 5 failed of 32 (cooldown words, count-free heading,
  set-neutral copy, both digests).
- The `d41c9006` evidence journey against the promoted tree: exit 1, "Expected substring: The 0–100 score is an
  internal pacing/structure heuristic … element(s) not found".
- `verify_samples.sh` on a scratch copy of the promoted set with one replay byte flipped: exit 1, seed 7 diverged
  at tick 0.
- The audit's sections 1 to 8 against `d41c9006`: 1,447 lines, 0 differing, exit 0; one character edited in
  section 1.9 of a scratch copy: 2 differing, exit 1.
- The validity gate with `--expected-seeds 0-50`: exit 1 ("missing [50]"); without the era config: exit 1.
- The recorder dry run with the era config: exit 0; bare: exit 1 ("Refused: ... whose recordings all carry its
  era's declared config").

### One bounded mutation pass

Operator classes COMPARE, CONST, NEGATE, DELETE; each mutant alone, its tests run, reverted.

| id | class | file | result |
|---|---|---|---|
| M1 | CONST | `eval/eras.py` (stage-b-r2 date) | killed |
| M2 | COMPARE | `scripts/_declared_experiment.py` (config sha `!=` to `==`) | killed |
| M3 | DELETE | `scripts/_declared_experiment.py` (missing-config refusal) | killed |
| M4 | NEGATE | `check_doc_facts.py` (history or replaced, to and) | killed |
| M5 | CONST | `check_doc_facts.py` (token slice) | killed |
| M6 | DELETE | `check_doc_facts.py` (no-set date refusal) | killed |
| M7 | COMPARE | `check_doc_facts.py` (summands must sum) | killed |
| M8 | NEGATE | `check_doc_facts.py` (whole-token match) | killed |
| M9 | CONST | `check_doc_facts.py` (S9 history cell) | not applied: the anchor no longer matched after formatting |
| M10 | DELETE | `check_doc_facts.py` (the records' cross-check) | killed |
| M11 | CONST | `PublicResults.tsx` (heading count) | killed |
| M12 | DELETE | `PublicResults.tsx` (cooldown words) | killed |
| M13 | CONST | `copy.ts` (no-rubric lead) | killed |
| M14 | COMPARE | `eval/watchability.py` (a stage pin's numerator alone) | survived |

M14 survives because `FloorPin.numerator` drives only the advisory rare-event rule; no test holds it to
`value` times the denominator, in this block or any earlier one. M9 is covered by
`test_s9_history_cells_are_the_d41c9006_values` and `test_one_s9_history_cell_moved_detected`, unexercised by
the pass. One pass, as ruled; neither is reworked here.

### Validation, each run to its end

| command | exit |
|---|---|
| `validity_gate.py replays/samples/9p2i` with model, zero cost, the four prompt pairs, the era config, seeds 0-49, one sha | 0, ten checks PASS |
| the same with `--expected-seeds 0-50` / without the era config | 1 / 1 |
| `shasum -a 256 replays/samples/9p2i/experiment-config.json` | `0c02fa61…92b` |
| `verify_samples.sh` bare; per set (`samples/9p2i`, `samples/4p1i`, both corpus sets, round 1) | 0; 0 each |
| `build_sample_report.py --check`, the five sets | 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `check_doc_facts.py`; `validate_task_docs.py` | 0; 0 |
| `measure_baseline.py --watchability --json`; `replays/samples/9p2i --honesty`, `--funnel`, `--vj` (`--json`) | 0; 0, 0, 0 |
| `measure_featured_criterion.py --set 9p2i`; `--games 9p2i:3`; `--games 9p2i:23` | 0 (1 of 1); 0 (0 of 1) |
| `verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 |
| the same at base (git-less archive) | 0: OK 47, ABSENT 11; the four extra ABSENT legs read the git index |
| `pytest -m campaign` at base / at head | 336 passed / 337 passed (the new refusal case) |
| `pytest -n auto` (full, before the last three fixes) | 1: 9,959 passed, 3 failed (an audit identifier in the candidates README, the `audits/` byte row, the parity leg it feeds); each fixed and its file re-run green |
| `pytest -n auto` (full, at `091bd2a5`'s tree) | 0: 9,962 passed, 20 skipped, 3 xfailed |
| `npm run e2e` (local Playwright) | 0: 13 passed, 3 skipped (the media spec's intentional skips) |
| bundle `build_demo_bundle.py --out` at base and head, `diff -rq` | `data/4p1i/`: same 24 files, 20 byte-identical, 4 differing only in `created_at` (each checkout's file mtime); `data/9p2i/`: four baked games (0, 2, 23, 29) and the rubric replaced by seed 3, summary re-derived; the JS assets and `index.html` rebuilt |
| `bash scripts/check.sh` at `f3392317` | 1: stopped at `ruff check` (`Final` undefined in `tests/eval/test_gameplay_census.py`); its later static legs, run one by one, found the rest `091bd2a5` fixes |
| `bash scripts/check.sh` at the pushed head | recorded in the PR body (this card cannot carry the run of the commit that writes it) |

### Decisions

Decisions 1 to 6 record the orchestrator's rulings of 2026-10-02 on the card's open points, each as
the card proposed it.

1. The referee's walk declares the Stage-B layers after the per-layer review above; gauges, rules and scoring
   are frozen.
2. The gameplay-facts extractor keeps refusing the new era: `samples/9p2i` ships no `results-rubric-score.json`,
   the 15.2 geomean parity pin is history, and a follow-up card, `rubric-extractor-era`, is named to widen it.
3. The candidate-round rule as stated above; round 2's copy retires, round 1 stays, the artifact rows recomputed.
4. The ladder tip stays at baseline 9; baseline 10 is reserved for the full re-record.
5. The era config lives at `replays/samples/9p2i/experiment-config.json`, byte-identical to round 2's; readers
   accept or ignore it.
6. The holding edit on the tour surfaces is this card's; the tour card replaces it.
7. ML-table tests assert their refusal on `samples/9p2i` and run on `ml_corpus/9p2i`, as this card's sweep
   clause names. The champion-flip FSM comparator, first settled here, is an open owner question (Review
   corrections, round 1).
8. The verdict check scopes the proof set's small conviction populations to lines naming 9p2i, so an unrelated
   twenty-of-something sample is not taken for its cell, and reports the pooled reads itself now that the
   proof row reads one set.
9. Old values ride inline beside each re-pinned literal rather than in a 527-line list here.
10. Follow-through inside the boundaries: the architecture note tightened three adjacent ladder sentences to fit
    its 1,300-word ceiling; the ML page sentence was shortened to keep the ML-table planted cases under that
    page's budget; the guided tour's intro and the case study's results link were made count-free.

### Limitations

- The promoted set carries the round's reporter flag: reporters ejected per report meeting 17/114 = 0.149,
  above the pre-registered 0.104; the owner's ruling promotes regardless (record 9.2).
- Interim public state until the tour card merges: one featured 9-player game, no curated cases (the source
  check withholds all three), no 9p2i rubric. The disputed-route case's meeting does not exist in the promoted
  game; `api/public_results.py`, not touched here, is the tour card's.
- The promoted set's recorded-arm targeting fold reads 55/297 free kills declined, above the 10% the live repair
  is held to on `ml_corpus/9p2i`; observed, not gated.
- The mutation survivor M14 and the unapplied M9 above.
- The base runs used a git-less archive of `origin/main`; the base `verify_ml_evidence.py` legs that read the git
  index report ABSENT there.
- `docs/deployment.md` states the 9p2i report as 29 MB; it read 35.5 MB at the base and 33.0 MB now (stale before
  this card; not touched).
- On macOS the evolution-strategy hash pin is Linux-only; CI is cited for it.

### Deviations

- The twelve commits `148fa211` to `4a36dc03` carry `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  in place of the card's Fable 5.1 line. They are pushed and are not rewritten; every later commit carries the
  card's line, and the deviation is an open question for the owner at merge (Review corrections, round 1).
- `tasks/README.md` has no index line naming this card; only the inventory sentence is re-derived.

### Review corrections, round 1 (2026-10-02)

A fix round from `4a36dc03` on the six verifier findings (commits: `833b7ce6` the tests, then the commit
recording this subsection). Only tests and this card change: no production
line, recorded byte, fixture, golden or front-door page moves, so every gate figure above stands.

**The corrected-baseline pin (finding 1).** At `d41c9006`, `test_corrected_w2_baseline_matches_a_rederivation`
held the whole serialized re-derivation byte-equal to `corrected_w2_baseline.json`. The promotion reduced it
to determinism plus one block, and reduced the 44-site channel map to per-channel counts. Now
`test_the_corrected_baseline_rederivation_is_pinned_whole` pins the operator command's whole output on the
promoted bytes (seven blocks and `sample_dir`) at sha256 `3a556a56c0f9c76d5838169bc357cbe760dc4a5d17c55d246b9c0f6172eb10e0`,
and `test_committed_ejections_decompose_into_channels` pins the map's sorted-key JSON at
`52ab23881ed37f687bd5e8c5b4c5bfbaa798d0fb06fcdb00f22a9ac490b90dec`. The old values sit beside them and the W2
anchor test holds both: the fixture's bytes at `a472a70d820d0ad61d51140c1b12734910ebe662d73db9dd598b1ad54542fb5d`
and its 81-site map at `2d54603723aeb76f2c3ede44fa8e15740dbb9e536ba783b8f2ae55d2c36cb6ed`. `tests/fixtures/` is
untouched. Each new value was computed through the production path (`corrected_baseline_from_report`, then
`serialize_corrected_baseline` on `replays/samples/9p2i`). The values are digests, so nothing is printed.

**The reporter-justice era identity (findings 2 and 6).** Three tests are new in `tests/eval/test_reporter_justice.py`:
- `test_the_promoted_set_records_exactly_its_eras_off_default_settings` holds `recorded_settings` to the nine
  off-default settings. The literal is checked against `replays/samples/9p2i/experiment-config.json`, whose
  `format_version` 1 is the default.
- `test_the_pool_refuses_two_eras_that_switch_the_same_fields` builds two one-game scratch sets: the promoted
  game, and the same game recorded with `vent_exit_policy` moved to `observed_risk` on every tick row and its
  terminal row. The moved set's identity follows its recording, the pool refuses the pair, and a same-era pair
  still pools.
- `test_a_set_whose_games_recorded_two_configs_fails_loud` is the planted case for the per-set refusal: two
  games, one moved, are refused by `compute_reporter_justice`, and the unmoved pair folds as one era.

**The recorder's era sha (finding 3).** `tests/scripts/test_refresh_samples.py::test_the_era_verdict_follows_the_declared_file_on_disk`
uses a scratch checkout whose `replays/samples/9p2i/experiment-config.json` holds the era config with
`vent_exit_policy` moved. `refuse_unsafe_target` passes with that file's sha256 and refuses with round 2's
sha256 (`0c02fa61...192b`, asserted), so the verdict follows the file on disk.

**The ML figure keyed to `samples/9p2i` (finding 4).** The card's stop rule names this case: any ML figure keyed
to the set's bytes stops the card and goes to the owner. The promotion settled one on the card's own authority
(Decision 7, now split), in `scripts/regen_test_goldens.py`, a file outside Expected scope. It is now an open
owner question (Q1 below). The code keeps the hold, which moves no figure, until the owner rules.

**The commit trailers (finding 5).** The twelve commits `148fa211` to `4a36dc03` carry the Opus 5.5 line in
place of the card's Fable 5.1 line. Pushed commits are not rewritten. This round's commits carry the card's
line, and the deviation goes to the owner (Q2 below). The PR's Decisions no longer ratify it.

**Open owner questions; the merge waits on both.**
- **Q1, the champion-flip FSM comparator.** `scripts/regen_test_goldens.py::fsm_comparator_win_rate` read the
  `samples/9p2i` MANIFEST's impostor wins at `d41c9006`. It now returns `FSM_COMPARATOR_AT_D41C9006 = (11, 50)`,
  and `tests/scripts/test_champion_flip_ruling.py` holds an independent `(11, 50)` with an era tripwire. The
  golden fields keyed to it, in `tests/scripts/_goldens/champion_flip_ruling.json` (unchanged), are:
  `fsm_comparator_win_rate` (0.22), `finalists.utility-es.win_edge_vs_fsm` (0.30000000000000004) and
  `finalists.policy-es.win_edge_vs_fsm` (-0.2). The `p18` block reads its own comparator row and is not keyed
  to it. The options:
  - (a) hold the `d41c9006` reading until a ladder-tip re-record, as now;
  - (b) re-derive it from the promoted MANIFEST, 24/50, giving 0.48, 0.04 and -0.46. This is a cross-era
    comparison; the ruling's shape holds (utility-es keeps the edge and fails the referee, policy-es passes it
    and loses the edge);
  - (c) another ruling.
- **Q2, the trailer deviation.** Accept the twelve commits as they are, or rule otherwise at merge. No pushed
  commit is rewritten under either answer.

**One bounded mutation pass**, over the spans the findings name and the spans this round tests. Only the
listed operator classes, plus J3x: J3x disables the per-set refusal outright and is the planted-case proof
that craft rule 2 asks of that gate. Each mutant was applied alone, its targeted suite was run, and the file
was restored from a copy. The column "at `4a36dc03`" runs that head's test files, so a SURVIVED there is a
probe that first came back green.

| id | class | span | at `4a36dc03` | now |
|---|---|---|---|---|
| G1 | swap one collection for a related one | `build_sample_report.py`: `effective_deflection` from the indistinguishability tally | survived, 30 passed | killed, 1 failed |
| G2 | replace a read with a constant | `build_sample_report.py`: `supply_gauges` as `{}` | survived, 30 passed | killed, 1 failed |
| J1 | drop a filter on a collection | `_recorded_settings`: the off-default filter | survived, 31 passed | killed, 3 failed |
| J2 | comparison to its inverse | `_recorded_settings`: `!=` to `==` | survived, 31 passed | killed, 3 failed |
| J3 | comparison to its inverse | per-set refusal `len(settings) != 1` to `== 1` | not run | killed, 15 failed, 14 errors |
| J3x | gate disabled (planted proof) | per-set refusal `and False` | survived, 31 passed | killed, 1 failed |
| J4 | None test to its inverse | `if config is None` to `is not None` | not run | killed, 19 failed, 12 errors |
| J5 | drop one member of a tuple of kinds | `_IDENTITY_FIELDS` without `recorded_settings` | not run | killed, 1 failed, 12 errors |
| J6 | swap one collection for a related one | `pool_reporter_justice`: the era set as a list | not run | killed, 1 failed, 12 errors |
| J7 | replace a read with a constant | the pooled identity `eras.pop()` as `()` | not run | killed, 1 failed |
| D1 | read of a loaded source to the canonical literal | `era_target_problem`: the declared file's sha256 as round 2's literal | survived, 45 passed | killed, 1 failed |
| D2 | read of a loaded source to the canonical literal | `repo_root / declared` as `_REPO_ROOT / declared` | not run | killed, 2 failed |
| D3 | comparison to a None test | `config_sha256 != expected` to `config_sha256 is None` | not run | killed, 2 failed |

The targeted suites:
- G: `tests/eval/test_gate_spec_metrics.py`.
- J: `tests/eval/test_reporter_justice.py`.
- D: `tests/scripts/test_refresh_samples.py` and `tests/scripts/test_candidate_sets.py`, selected by
  `-k "era or declared or committed or candidate"` (46 tests) and run serially.

The pass leaves no survivor. The verifiers' wider runs at `4a36dc03` agree on the head column: J1 survived 222
tests, and D1 survived 656 tests over ten files.

**Validation of this round.** Everything ran on the fix tree. Its non-test, non-card bytes equal `4a36dc03`'s.

| command | result |
|---|---|
| the three changed test files and `test_champion_flip_ruling.py`, serially | 224 passed |
| `verify_samples.sh` per set (`samples/9p2i`, `samples/4p1i`, both corpus sets, round 1) and bare | exit 0 each; every replay clean (50 per set, 150 in `ml_corpus/9p2i`) |
| `build_sample_report.py --check`, the five sets | exit 0 each |
| `publish_process_scorecard.py --check`; `publish_gameplay_census.py --check` | 0; 0 |
| `check_doc_facts.py`; `validate_task_docs.py` | 0; 0 |
| `verify_ml_evidence.py` (offline) | 0: 63 checks, OK 51, FAIL 0, ABSENT 7, INFO 5 (unchanged) |
| `pytest -m campaign` | 337 passed (as at `4a36dc03`) |
| `npm --prefix frontend test`; `npm run e2e` | 562 passed; 13 passed, 3 skipped |
| round 2's 54 files at `23698a0f` against `replays/samples/9p2i` at the fix tree (git blobs, then sha256 of each file's bytes) | 54 identical, 0 differing, none missing or extra |
| `git diff --stat 23698a0f` over `samples/4p1i`, both corpus sets, `training/`, `agents/tactical/learned/`, `tests/fixtures/` | empty |
| `bash scripts/check.sh`, once at the pushed head | in the PR body (a card cannot carry the run of the commit that writes it) |

One observation, outside this round. `test_a_switched_on_config_is_refused_at_every_unsafe_target[a hidden round name]`
failed once under `-n 4` beside `test_candidate_sets.py`, with no mutant applied. It passed alone, serially and
in every later run. The case snapshots the real `replays/` tree, and this card leaves the case unchanged.
