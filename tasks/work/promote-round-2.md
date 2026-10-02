# Promote candidate round 2 as the shown set

**Status:** ready

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

- [ ] **The bytes move, identically.** `git mv` round 2's 50 replays, `MANIFEST.md`, `roster.json` and report
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
- [ ] **The candidate-round rule, and its rows.** Rule: a round whose bytes become a committed set is deleted in
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
- [ ] **One era registry, held to the bytes.** One module (for example `eval/eras.py`, named in Results) maps
  each committed set to its era: id (`baseline-9` or `stage-b-r2`), owning record, declared config file or
  none. Every consumer below reads it; nothing else names a set's era. Mechanism: a test folds each set's games
  to the census `EraKey` and requires one key per set, one key per era id, and the declared file equal to
  every game's recorded config. Planted: the registry naming `samples/9p2i` as `baseline-9` fails; a scratch
  set with one game's config edited fails.
- [ ] **The scorecard groups by era.** `compute_process_scorecard` groups sets by the registry, pools only
  within an era (the baseline-9 era pools its three sets; no 9-player pool remains), and publishes
  `samples/9p2i` as its own era with a before column: that set's entry of `docs/process-scorecard.json` at
  `d41c9006`, carried as a frozen block whose sha256 the module pins and the publisher never recomputes. The
  nine row definitions do not change; the schema version moves; the page's provenance text names both eras and
  dates. Mechanism: `publish_process_scorecard.py --check`. Planted: `pool` over two eras raises; one edited
  leaf of the before block fails `--check`.
- [ ] **The census groups by era.** `census_from_inputs` groups by the registry; constants (the grace window)
  are per era; pools exist only within an era; the "One era" section becomes per-era. Mechanism:
  `publish_gameplay_census.py --check`. Planted: the existing cross-era `GameplayCensusEraError`, plus a
  hand-built input list putting `samples/9p2i` in the baseline-9 group, raises.
- [ ] **The counterfactual stays in its era.** `CANONICAL_SETS` is the registry's baseline-9 sets (three); the
  `samples/9p2i` innocent pin leaves with a one-line history note; `--sets samples/9p2i` refuses, naming the
  era. Pooled pins are re-derived over the three sets and labelled as such, old to new in Results; the memo
  test holds `CANONICAL_SETS` to the memo's four sets less the promoted one. Planted: the four-set pins fail
  at the head; the refusal test.
- [ ] **The doc facts read per-set provenance** (`scripts/check_doc_facts.py`, planted cases in
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
- [ ] **The front door changes, under the budgets.** Mechanism: `check_doc_facts.py` (facts, agreement,
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
- [ ] **Watchability: a stage block and a per-set default; scoring frozen.** `_BASELINE_SUPPLY_FLOORS` gains
  `stage-b-r2` with only a `9p2i` entry, every pin measured from the promoted bytes and passing at equality;
  the default id resolves per set from the registry (`samples/4p1i` to `baseline-9`, `samples/9p2i` to
  `stage-b-r2`), and `measure_baseline.py --watchability` follows it; baseline-9's `9p2i` entry stays byte-identical
  as history and as the ML selection floor. The referee's gauges, rules and every existing block are
  unchanged; its walk declares the layers it must read after a per-layer review recorded in Results. The 15.2
  parity pin keeps its fixture as history and retires its byte recomputation, as the baseline-2 block did.
  Mechanism: `tests/eval/test_watchability.py`. Planted: the referee's JSON on `samples/4p1i`,
  `ml_corpus/9p2i` and `ml_corpus/4p1i` is byte-identical at base and head; one stage pin raised by one
  numerator fails its set; a recording with one layer undeclared is refused, naming the field.
- [ ] **The recorder records the next round against the new era.** A target in `replays/samples/<set>/` must
  carry exactly that set's declared config (sha256 of its `experiment-config.json`); a set with none takes
  no switched-on config; `replays/ml_corpus/` keeps refusing every switched-on config; the default target and
  the candidate rules are unchanged. The rubric step skips an era the extractor does not read, with one named
  line, and leaves no rubric. Mechanism: `scripts/_declared_experiment.py`, `refresh_samples.sh --dry-run`.
  Planted, each in `tests/scripts/test_refresh_samples.py` or `test_candidate_sets.py`: a bare run, round 1's
  config, and the era config with one byte changed, each aimed at `samples/9p2i`, refuse; the era config aimed
  at `samples/4p1i` or `ml_corpus/9p2i` refuses; the era config aimed at `samples/9p2i` passes the dry run.
- [ ] **The holding edit on the tour surfaces.** The sibling tour card owns these files after this card; here
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
- [ ] **The no-rubric copy is set-neutral.** The three strings that render when a set ships no rubric
  (`interestingnessAbsentLead` in `copy.ts`, and `ReplayPicker.tsx`'s empty state and banner) are rewritten
  with no claim about which set ships a rubric, no per-set counts and no "fast fixture" attribution; the copy
  gate (`frontend/src/lib/copy.test.ts`) stays clean. The comments at `TournamentDashboard.tsx:889` and
  `:1193` and `GuidedTour.tsx:29-31` stop saying the 9p2i default ships a rubric. Mechanism:
  `frontend/src/components/ReplayPicker.test.tsx`. Planted: a new 9p2i-unscored render (`rubricMissing`,
  `set="9p2i"`, both views) asserts the copy names no set as the unscored one and claims no rubric elsewhere;
  the `d41c9006` strings fail it.
- [ ] **The kill cooldown has public words, and the cases heading has no count.**
  `frontend/src/components/PublicResults.tsx`'s behaviour list names a recorded kill cooldown in plain words,
  with its tick count (audit 1.11). Its cases heading ("Three decisions to investigate", `:85`) becomes
  count-free, so the tour card can keep one, two or three re-derived cases without a false count; the tour
  card does not touch this file. Mechanism: vitest render tests. Planted: a group differing only by its
  cooldown renders the new phrase, and fails without it; a one-case render carries no "Three", and the
  `d41c9006` heading fails it.
- [ ] **The re-pin sweep, old to new.** Every test, fixture and code comment that reads or cites `samples/9p2i`
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
- [ ] **The corpus and the ML evidence do not move.** Mechanism: `uv run python scripts/verify_ml_evidence.py`
  (offline, every leg) and the campaign tier (`uv run pytest -m campaign`), both green at base and head with the
  same per-leg verdicts; `BAKEOFF_BASELINE_ID` and every FROZEN line unchanged. Planted: a stale samples file
  count fails the inventory leg. Any ML figure keyed to `samples/9p2i` bytes stops the card and goes to the
  owner.
- [ ] **The promotion record.** A dated addendum, section 9 of `audits/audit-2026-10-01-stage-b-r2.md`: the
  owner's ruling verbatim; the rule's reading and the reporter flag; the per-file sha256 identity; the win-split
  and conviction-partition tables above; the before-column source; the candidate-round rule, its departure
  from the memo's item 7 and `d41c9006`; that the round's s9-at-baseline-9 column reproduces at `d41c9006`,
  not after. Sections 1 to 8 stay
  byte-identical. Mechanism: the audit's own section-1 comparison (0 differing lines) and `check_doc_facts.py`.
  Perturbed: one character edited in section 1 of a scratch copy gives differing lines and exit 1.
- [ ] **Every gate, green.** `bash scripts/verify_samples.sh` (bare and per set), the five
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

Not started. The implementer records here: the commits and the sections relied on (this card, memo
sections 1 and 7, partial-record section 5, the round-2 audit sections 1.9, 6, 7 and 9, round 1's audit
section 6, `docs/architecture.md`'s ladder); the per-file sha256 list; the era registry and each consumer;
each set reader fixed to accept the in-tree config, if any; every re-pin old to new, the synthetic rubric
among them; the holding edit line by line, file by file (`evidence-journey.ts` included), for the tour card
to replace; the set-neutral copy, old to new; the referee's layer review; each planted failure with its red
and green run; the bundle diff; every validation command with its exit code; decisions and limitations, the
reporter flag and the departure from the memo's round-retirement proposal among them.
