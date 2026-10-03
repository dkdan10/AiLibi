# The interestingness rubric for a set recorded under a declared era

**Status:** ready

## Outcome

Candidate round 2 was promoted on 2026-10-02. Since then `replays/samples/9p2i` has held 50 games recorded under
the declared era config `replays/samples/9p2i/experiment-config.json`, and the shown set has shipped no
interestingness rubric. The gameplay-facts extractor that feeds the scorer re-simulates every recording with no
settings, so it refuses the era by name. The Highlights reel and the dashboard histogram show their empty state on
the default set; the dashboard tells the reader to run a scorer that cannot score the set; the refresh
script skips the step with one named line; and the geomean parity pin between the lab scorer and the
watchability referee survives only as history.

This card contracts option (a) of Evidence: widen the extractor, keep its source. When it is done:
- The extractor reads a recording under its own recorded config. The seeding, every advance and every applied
  meeting take their engine values from the one engine-arguments helper. Every applied meeting takes the recorded
  meeting reset. The chain re-walk and the contradiction re-derivation see the arms the live meeting ran with.
  The extractor names, field by field, the recorded settings it reads, and refuses any other by name before its
  first advance.
- The production path regenerates `replays/samples/9p2i/results-rubric-score.json`. It is stamped with the set's
  MANIFEST key and source fingerprint exactly as `experiments/lab/rubric_score.py` stamps it, and it is committed.
  The era's two lab artifacts are committed under names that carry the era id. The facts JSON stays a temp file.
- Baseline-9 history does not move. The retired rubric stays at `d41c9006`, and the two unkeyed lab files stay
  byte-identical. The widened extractor reproduces both from the baseline-9 bytes.
- The parity pin is keyed by era: baseline 9 is held as history, and the promoted era is re-derived from its
  bytes on every run.
- `4p1i` still ships no rubric, by design. The refresh script, the viewer copy and every comment that says no
  committed set ships a rubric then say what is true.

The rubric's R-items, its geomean, its floors and the scorer's functions stay exactly what they are.

## Evidence

Every `path:line` is at `59bbd1be` (labelled as such) and is re-anchored by its symbol at dispatch. Every count
is count-only, reproduced as described here, and re-measured at dispatch; the dispatch figure governs. No
prompt, transcript or seed-band prefix was printed. The scratch probes below are not committed; the
implementation's tests re-measure each figure at its head.

**Where the served rubric comes from** (at `59bbd1be`). `scripts/refresh_samples.sh:1123-1166` runs only when
the target is `replays/samples/9p2i`. It runs `audits/workflows/extract_gameplay_facts.py`, which writes its facts
to `${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json` (`:4648-4652`), then
`experiments/lab/rubric_score.py FACTS --set-dir DIR`. There `regen_for_set` (`:1337-1378`) writes the served
file, and `main` (`:1381-1481`) also writes `experiments/lab/results-rubric-score.json` and
`results-rubric-geomean.json` under fixed names (`:1453`, `:1467`). `api/replay_loader.py` serves the file at
`/eval/rubric`; `scripts/build_demo_bundle.py:402-412` bakes it trimmed to the baked seeds and skips a set
without one. Both lab files are the baseline-9 scoring (`git_head` `27646d67`, unchanged since `d41c9006`); the
second is the fixture `tests/eval/test_watchability.py:130-166` holds as history. Run on the promoted set today,
`main` would overwrite both.

**The refusal, and what it hides.** `refuse_experiment_settings` (`extract_gameplay_facts.py:184-206`, called at
`:2152`) exits at the first seed with any setting off its default; on the promoted set that is seed 0. The
extractor seeds at `:2135-2141`, advances at `:2265` and applies meetings at `:2781-2786`, none of them with the
recording's settings. With the refusal replaced by a no-op (scratch), the run on the promoted set records 1,885
invariant failures (1,801 tick-hash and 81 post-meeting-hash mismatches), reaches 81 of the 117 meetings, tallies
34 impostor and 17 crew ejections against the shipped report's 44 and 22, and fails three of its sixteen
self-checks. `rubric_score._facts_integrity_ok` (`:711-741`) floors every game on any failing self-check.

**The minimal widening, measured.** A scratch copy of the extractor changes two things: it threads
`engine_arguments(recorded_experiment_config(entries))` (`orchestrator/experiment_config.py:338-369`) into the
three calls, and the recorded `meeting_reset` into the meeting call. On the promoted set it reads 16 of 16
self-checks OK and no invariant failure. Its findings:
- 44 cross-room and 99 dead-actor rejections, the kinds the walk always reports;
- 114 `OPTIN` and 3 `TERM` "high" findings. These are exactly the 117 meetings whose last turn is the bounded
  rebuttal: in every promoted meeting, the last reply is the one `meetings.rebuttal.select_bounded_rebuttal`
  re-derives from the turns before it.

The same copy also ran on a `git archive` export of `d41c9006`'s `replays/samples/9p2i`. That export carries the
retired served file at the very path the scorer writes (`git ls-tree d41c9006 replays/samples/9p2i`: blob
`4879637e`), so the file was moved aside before the run. The scorer then wrote a served file byte-identical to the
retired one (`git show d41c9006:replays/samples/9p2i/results-rubric-score.json`) and a geomean body
byte-identical to `experiments/lab/results-rubric-geomean.json`.

**The promoted set, scored by that copy** (count-only): 50 rows, mean 25.1, median 18.4, top 86.2, and 16 games
at 0; win shapes impostor-win 24, eject-decided 13, stopwatch-some-eject 10, stopwatch-no-eject 3. Every zero
comes from the scorer's railroad floor, none from a friendly kill: the floor fires on 17 crew ejections whose
rendered suspicion among the ejectors sits under the scorer's 0.60 vote line. On the baseline-9 bytes the same
floor zeroed 5 games (`test_watchability.py:165`). The scorer does not change; these are its readings of the era.

The watchability referee already reads the era through `eval/replay_walk.py`, with the ten readable settings
reviewed (`eval/watchability.py:1604-1625`). In its frozen `historical_15_2` mode (`:2265`) it equals that scratch
geomean on all 50 games and all eleven pinned keys.

**The arms, and what each asks of the extraction.**

| recorded setting | layer | what the extractor must do |
|---|---|---|
| `redistribution_policy` (default in the era) | engine | take it from the helper at every advance and every meeting, as every reader does |
| `kill_cooldown_ticks` 6 | engine | take it from the helper at the seeding, every advance and every meeting; without it the hashes diverge |
| `vent_witness_rule` physical | engine | take it from the helper; no extractor fact reads a witness event (vent channels are rebuilt from recorded flags, `:437-521`) |
| `meeting_reset` hub_with_grace | orchestrator | pass it to every applied meeting; pass the derived regroup ticks to the contradiction re-derivation, as the live manager does (`meetings/manager.py:1476-1484`) |
| `bounded_rebuttal_version` 1 | meeting | accept exactly the one trailing reply the selector picks (`meetings/transcript.py:487-527`, `walk_chain`); today it reads as 117 protocol findings |
| `report_body_handle_version` 1 | orchestrator | nothing: it changes only a report's trigger text, which no fact reads |
| `ballot_kill_row_version` 1, `impostor_ballot_version` 1 | meeting | prompt composition only; the slot classifier and the suspicion-graph parse (`:572-634`) must keep classifying |
| `vent_exit_policy` look_and_wait, `vent_entry_policy` own_fresh_kill | tactical | nothing: they reach the walk as recorded actions, and no policy is re-run |

Two of these read as no-ops on the promoted bytes and are kept because the live game has them. The regroup
ticks: 67 of 117 meetings carry them, and the re-derived flags are identical either way (78). The prompt
classification: 120 opening, 420 opt-in, 271 reply and 691 vote calls, none unclassified, and every vote call
parses at least one suspicion row (3,101 in all). The composite `v8` prompt stamps never reach the extractor,
which reads no prompt-version field.

**The alternatives weighed.**
- **(a) Widen the extractor: contracted.** The measured cost is three threaded calls, the reset, the rebuttal
  acceptance and the regroup ticks. The output on the baseline-9 bytes is byte-identical to the retired rubric.
  The scorer, its inputs and its integrity floor stay one home.
- **(b1) Serve the referee's facts.** The referee reproduces the geomean, but the served row also carries
  `r7_legible`, `accused_impostors`, `survived_accused`, `win_shape` and the set's win-shape counts, and the lab
  table carries R-items the referee does not fold (threshold inversions, free-text lengths, ballots that follow
  the chain). Producing those there is a second scorer, the drift the scorer's one-home rule exists to prevent,
  and the served file's producer would differ by era, so the eras would no longer compare like with like.
- **(b2) A narrow, era-neutral facts source over the recorded rows only.** The integrity floor reads the
  extractor's state-hash self-checks and refuses a facts file without them (`rubric_score.py:711-741`). A source
  that does not re-simulate could only certify integrity by default. Kill victims' roles, testimony records and
  suspicion trajectories would be re-implemented beside the extractor's.
- **Not taken: moving the extractor onto `eval/replay_walk.py`.** That would put the threading in one place.
  But moving a 4,670-line fold is a refactor with its own byte-parity contract. The helper threading reaches the
  same engine values and is pinned by the same scan.

**What goes false once the rubric returns** (at `59bbd1be`):
- **The scorer instruction.** `frontend/src/lib/copy.ts:376-378` and `TournamentDashboard.tsx:893-897` tell the
  reader to run `experiments/lab/rubric_score.py` over a set that ships none. After this card, the only served set
  that renders that state is 4p1i, and the extractor is never run on it.
- **Comments that say no committed set ships a rubric:** `client.ts:366-372`; `ReplayPicker.tsx:19-21`, `:317`;
  `TournamentDashboard.tsx:130-132`, `:885-887`, `:1188-1190`; `HighlightCard.tsx:17-19`;
  `ReplayBrowser.stories.tsx:7-8`, `:71-72`, `:120`; `api/replay_loader.py:1269-1270`, `:3961`;
  `api/routes/eval.py:235-236`; `api/schemas.py:1734`.
- **Tests that pin the absence or the refusal:** `tests/api/test_sets.py:328-336`, `:454-468`;
  `tests/scripts/test_build_demo_bundle.py:41-42`, `:313-314`, `:363-371`;
  `tests/experiments/test_gameplay_facts_genuine_class.py:18-21`, `:100-110`;
  `tests/experiments/test_gameplay_facts_refuses_experiments.py` (whole);
  `tests/eval/test_recorded_arm_readers.py:1660-1700`; `tests/scripts/test_refresh_samples.py:2147-2153`; and the
  evidence journey's 9p2i leg, `frontend/e2e/evidence-journey.ts:58-68`.
- **The recorder.** The skip clause (`refresh_samples.sh:1134-1138`; its dry-run line at `:585-589`) goes false.
  So do two passages the promotion review flagged as stale: the `--experiment-config` help (`:68-77`) and the
  comment above `declared_args` (`:304-312`). Both still say that a switched-on config records only outside the
  committed sets.
- **The lab report's run line** (`experiments/lab/report-rubric-interestingness.md:65-68`) names the unkeyed
  outputs.

The promotion card's Results (Decision 2) and the tour card's Limitations name this card.

## Acceptance

- [ ] **The extractor names what it reads and refuses the rest by name.**
  - A module constant names the recorded settings the extractor reads: the ten of
    `eval.recorded_settings.READABLE_SETTINGS`, looked up at call time, as the referee does. The module docstring
    gives one line of reason per field, from the arm table.
  - Before the first advance, a seed with a recorded setting outside that list is refused through
    `refuse_unread_settings`. The message names the seed, the reader and the field.
  - `refuse_experiment_settings` is deleted, together with its consumers.
  - Mechanism: a new test module, plus a Hypothesis property over the closed config space (every field, every
    value, every valid format). The extractor refuses exactly when that function refuses, names the same field,
    and never advances first.
  - Planted:
    - a `self_report` true config, a `crew_idle_policy` patrol config and a format-2 config are each refused by
      name;
    - a tick row whose `experiment_config` carries a key the model does not know is refused at parse, and the
      error names the key;
    - with `READABLE_SETTINGS` narrowed by `kill_cooldown_ticks`, the extractor refuses the cooldown game with
      `kill_cooldown_ticks=6` in the message (it joins `INSTRUMENTS`, `tests/eval/test_kill_cooldown_readers.py:579`).
- [ ] **The re-simulation runs the recorded engine and reset.**
  - The seeding, every advance and every applied meeting take their values from the engine-arguments helper.
    Every applied meeting also takes the recorded `meeting_reset` and redistribution rule.
  - On `replays/samples/9p2i` the extraction completes with every self-check OK and no invariant failure; with
    the refusal bypassed and nothing threaded, the run recorded 1,885 failures.
  - Mechanism:
    - the extractor joins `_RESIMULATION_MODULES` (`tests/orchestrator/test_experiment_arms.py:428`), whose `ast`
      scan fails any engine call made without the helper's arguments;
    - the cooldown site table and gate (`test_kill_cooldown_readers.py:375`, `:492-516`) gain the extractor's
      three calls, as `extractor: seeding`, `advance` and `meeting`.
  - Planted: `_forgotten_at` at each of the three sites makes the gate name that site. The scan's own planted
    sources stay.
- [ ] **The chain re-walk reads the recorded rebuttal.**
  - With `bounded_rebuttal_version` 1, the re-walk accepts one trailing reply when, and only when, it equals
    the selector's pick. It reads that through the one home, `walk_chain` or `select_bounded_rebuttal`, never a
    replica. Otherwise every chain finding keeps its meaning.
  - Mechanism: a count test on the promoted set. `OPTIN` and `TERM` read 0, and the rejection findings stay at
    44 and 99.
  - Planted:
    - the scripted rebuttal recording (`tests/_helpers/scripted_meeting.py`, `ACCUSE_THE_OPENER`) yields no chain
      finding;
    - read with the version as `None`, it yields one;
    - with the rebuttal's speaker swapped, or with a second trailing reply appended, it still yields one.
- [ ] **The contradiction re-derivation sees the regroup.**
  - Each meeting's re-derivation receives the regroup ticks that `orchestrator.replay.derive_regroup_ticks`
    (`:1498`) derives from the meetings that resumed play. That is the set the live manager passes.
  - On the promoted set no re-derived flag changes (67 meetings carry ticks; 78 flags). Results states this as a
    no-op on these bytes.
  - Planted: a constructed meeting whose alibi falls inside a regroup window mints the flag without the ticks,
    and does not mint it with them.
- [ ] **Prompt-derived facts classify on the era.**
  - On the promoted set, every meeting call classifies to a named slot (120, 420, 271 and 691; none
    unclassified), and every vote call parses at least one suspicion row.
  - Mechanism: a count test on the committed set.
  - Planted (source change): with the era's graph header removed from `_SUSPICION_GRAPH_HEADERS`, the vote count
    falls to 0 and the test fails; an era vote prompt whose first header is rewritten lands in the unclassified
    slot.
- [ ] **Each arm changes only what it affects.**
  - For each of the ten readable settings, a fake recording of one seed with that setting alone off its default
    extracts with every self-check OK.
  - For the cooldown, the reset and the rebuttal, the same seed recorded without the setting yields facts that
    differ in the fields the arm table names: kill and meeting ticks, post-meeting positions, chain turns.
  - For each setting the table marks "nothing", the module docstring states why, and dropping the setting from
    the read list makes that recording refused by name.
  - Mechanism: the new test module, on fixed seeds with the fake provider.
  - Planted: dropping the reset from the meeting call turns the post-meeting self-check red on the reset
    recording; dropping the cooldown at any one site turns the tick-hash self-check red.
- [ ] **The production path regenerates the served rubric, and it is committed.**
  - The refresh step's commands, run from the repository root, write `replays/samples/9p2i/results-rubric-score.json`.
    Its `git_head` is the set's MANIFEST key (`43b5ee45`) and its `source_fingerprint` is the set's recording
    fingerprint. The loader serves it fresh.
  - Mechanism:
    - a currency test re-runs the extraction on the committed set, with facts in `tmp_path`. It asserts that the
      committed `interestingness` equals `rubric_score.interestingness(facts)` and that both stamps equal the
      set's own;
    - `tests/api/test_sets.py:454` is re-targeted to a fresh, served rubric with its counts: 50 rows, and the
      zero-score and top-score figures as re-measured at dispatch. It keeps the producer-and-loader key agreement.
  - Planted: a `tmp_path` copy of the committed file with one score changed fails the currency check. The stale
    controls in `tests/scripts/test_public_recording_provenance.py` stay.
- [ ] **The parity pin is keyed by era.** The historical pin in `test_watchability.py` becomes a table keyed by
  era id.
  - `baseline-9`: the frozen fixture is held to itself and to `27646d67` and is never re-derived. Its assertions
    are unchanged.
  - `stage-b-r2`: the committed `experiments/lab/results-rubric-geomean.stage-b-r2.json`, stamped with the set's
    key, equals `compute_game_score(..., historical_15_2=True)` over `replays/samples/9p2i` for every game and
    every pinned key, to 1e-6. It is re-derived on every run (50 of 50 at authoring).
  - Planted: changing one cell in a `tmp_path` copy fails the pin, and so does a copy stamped with another key.
- [ ] **Lab outputs are keyed by era, and history is never rewritten.**
  - `rubric_score.py`'s `main` names its two lab outputs by the era the set belongs to (`eval/eras.py`):
    `results-rubric-score.<era id>.json` and `results-rubric-geomean.<era id>.json`.
  - No code path writes the two unkeyed baseline-9 files again, and both stay byte-identical to `d41c9006`.
  - For a directory the registry does not name, `main` writes only the served copy and says so in one line
    naming the directory.
  - The `--set-dir` help says that the file is stamped with the MANIFEST key.
  - Mechanism: a unit test of the naming, over the registry and over a planted registry.
  - Planted: a registry that names the set under another era id changes both names, and a naming that returns
    an unkeyed name for `baseline-9` fails.
- [ ] **Baseline 9 reproduces from its own bytes.** On a `git archive` export of `d41c9006`'s
  `replays/samples/9p2i`, the widened extractor (given that directory as `--sample-dir`) and the scorer write a
  served file byte-identical to the retired one. The geomean they compute equals the frozen fixture's body.
  - The export carries the retired `results-rubric-score.json` at the path the scorer writes. It is deleted right
    after the export, and the run checks that it is gone, so only the scorer can put a file there.
  - The extractor and the scorer each exit 0; Results quotes both exit codes.
  - Mechanism: the Validation commands, quoted in Results; the bytes are no longer in the tree, so no test can
    read them.
  - Planted: with the file deleted and the scorer not run, the same `cmp` fails on the missing file; and the same
    `cmp` against a copy with one per-game score changed reports the difference. Results quotes both red runs.
- [ ] **The recorder's text and its rubric step are true.**
  - The skip clause and its dry-run line go. For `replays/samples/9p2i` under its era config, the step
    regenerates the rubric, passing `--sample-dir` explicitly, and the dry run says "would regenerate". Any other
    target prints no rubric line.
  - The `--experiment-config` help and the comment above `declared_args` state the era rule: a committed set
    records only with its own era's declared config, or bare when its era declares none; a candidate round or a
    scratch directory takes any config.
  - Mechanism: dry-run and `--help` cases in `tests/scripts/test_refresh_samples.py`, run with `--dist loadfile`.
  - Planted: restoring the old skip line fails the dry-run case, and restoring the old help sentence fails the
    help case.
- [ ] **The viewer copy is true.**
  - `interestingnessAbsentLead` stays set-neutral and carries no instruction to run a scorer.
    `interestingnessAbsentTail` and the dashboard's code element go.
  - The empty state and the banner in `ReplayPicker.tsx` stay set-neutral.
  - Every comment listed in Evidence says that the shown 9-player set ships a rubric, and that a set without one
    renders the empty state.
  - Mechanism:
    - `ReplayPicker.test.tsx`: the absent lead names no path and asks for no run;
    - a render test of the dashboard's absent branch;
    - the evidence journey: the 9p2i leg shows the score legend and no "ships no", and the 4p1i leg keeps the
      unscored state.
  - The copy carries no task or audit ID, no unexplained term and no threshold arithmetic; the copy walk checks
    this.
  - Planted: restoring the old lead fails the copy test, and the journey's 9p2i assertions fail on the base
    bundle, which has no rubric.
- [ ] **4p1i ships no rubric, and the bundle carries 9p2i's.**
  - `test_eval_rubric_is_per_set` keeps its 4p1i 404 and now serves 9p2i.
  - `test_the_committed_sets_bake_no_rubric` becomes: 9p2i bakes its rubric trimmed to the baked seeds, and 4p1i
    bakes none.
  - Planted: the trimmed-bake test keeps its scratch path, and a bake that skips the trim fails it.
- [ ] **The registry rows follow the bytes.** In `docs/artifacts.md`, three rows are recomputed as the last step,
  after the final merge of `main`: the `replays/samples/` row (107 files to 108), the `audits/` row (exact bytes)
  and the `experiments/lab/`, `experiments/model_probe/` row. That row gains this card's two lab files, so it
  states 2 more files than it reads at this card's final merge of `main`: 167 to 169, because
  `route-check-replay` merges first and moves it from 164 to 167. No figure is carried from authoring.
  Mechanism: `test_every_counted_registry_row_matches_the_index` and the offline `scripts/verify_ml_evidence.py`,
  never with `--complete`. Planted: with a row left stale the test fails; Results quotes the red run.
- [ ] **The wave lessons hold.**
  - The neuter pass: every production line this card adds or changes is neutered alone, and its suite goes red.
    Results lists the probes.
  - One bounded mutation pass, over the changed spans, with exactly the eight listed classes: F drop a filter,
    S swap a collection, N None test, K read to constant, M message argument, T drop a tuple member, B swap
    branches, L loaded source to literal. Every survivor is killed or named equivalent.
  - No test is weakened. Results names each re-targeted test's old assertion and the strength it keeps.

## Constraints

**Dispatch order and shared files.** The wave runs in two parts. `census-reporter-base-rate`,
`route-check-replay` and `post-promotion-follow-through` dispatch in parallel from `main` at the coordination
commit that lands the four cards, and merge one at a time in that order: census, route, then the follow-through
card (by the owner). This card dispatches from `main` after the follow-through card merges, so its base holds all
three, and its pull request merges last, by the owner. The files it shares, and who writes them first:
- `docs/artifacts.md`: one row per card, written in the merge order. `census-reporter-base-rate` writes the
  gameplay-census row's text; `route-check-replay` the `experiments/lab/` row (164 to 167 files);
  `post-promotion-follow-through` the process-scorecard row (3 files), and the `docs/media/` row only if its
  rounded size moves. This card writes the `replays/samples/` and `audits/` rows and recounts the
  `experiments/lab/` row last, on the `main` it merges into (2 more files than it reads then: 167 to 169). Each
  card merges `main` and edits its own row in its last commit, then re-runs `scripts/verify_ml_evidence.py`
  offline.
- `tasks/README.md`: the inventory sentence only. The coordination commit sets it, and each card re-derives it
  with `scripts/validate_task_docs.py` at its own final merge of `main`, in the merge order; this card is last.
- `tests/scripts/test_refresh_samples.py`: the follow-through card first (its decoys, planted rounds and strays
  move under `tmp_path`), then this card (the dry-run and help cases of the rubric step). The census and route
  cards never touch it.
- `frontend/src/lib/copy.ts`: the follow-through card first (the new public-results group), then this card (the
  interestingness strings in the dashboard group).
- `frontend/src/lib/copy.test.ts`: the follow-through card's (`PublicResults.tsx` joins the in-scope sources).
  This card edits it only if its copy walk needs it, after that merge, and names the edit in Results.
- `tests/scripts/test_public_recording_provenance.py` and `tests/scripts/test_verify_ml_evidence.py`: the
  follow-through card writes them; this card only runs them.
- `eval/eras.py`, `eval/gameplay_census.py`, `eval/process_scorecard.py`, `scripts/counterfactual_phase21.py`,
  `scripts/publish_gameplay_census.py` and `docs/gameplay-census.md` and `.json`: `census-reporter-base-rate`'s.
  This card only reads `eval/eras.py` (`era_of`) for its lab names, on a base that already holds the census merge.
- `experiments/lab/`: no file is shared. `route-check-replay` adds its instrument, report and JSON; this card adds
  the two `stage-b-r2` JSONs and edits the run line in `report-rubric-interestingness.md`.
- `replays/samples/9p2i/`: this card alone adds `results-rubric-score.json`, and no recorded byte moves.
  `route-check-replay` reads that directory by a pinned commit sha, never `HEAD`, so the new file does not move
  its committed JSON.
- `tests/eval/test_kill_cooldown_readers.py`: this card's alone.

This card does not write `frontend/src/components/PublicResults.tsx` or `README.md`; those are the follow-through
card's. The tour card's Limitations routed `PublicResults.tsx`'s "experimental" wording here, and it goes with
that file. If a file here turns out to be held by an undispatched card, the orchestrator orders the two.

**Out of scope.**
- The rubric's R-items, its weights, its floors and its scoring functions; no history is re-scored.
- Any recorded byte: no replay, MANIFEST, roster, report or config under `replays/` moves.
- `replays/candidates/stage-b-r1/` is untouched. The ladder tip stays at baseline 9.
- Engine, agent, meeting, orchestrator, LLM and training code. The only exception is the comment-only lines in
  `api/` that Evidence lists.
- No DTO, schema, loader mapping or generated type changes. `RubricGameView` keeps its shape.
- No new `AILIBI_*` lever, environment switch or experiment field, and no prompt registry or prompt version bump.
- The ML corpus's FROZEN line and every ML artifact stay put, and ML stays on hold (ruling 12).
- No live provider call, no recorder run and no held-out generator; the untracked `.env` is never read.
- Censuses are count-only, keyed by (set, meeting). No rendered prompt, transcript text or seed-band prefix is
  printed.

**House rules carried.** The engine stays a pure, deterministic tick, and replays stay byte-identical in their
recorded scope. `agents/` never imports `engine/`. No module-level mutable state: the read list is an immutable
constant. Invalid input raises, with no silent fallback. Each new gate carries a planted case that fails on its
claimed defect. Every claim names its enforcing mechanism, and every number is measured at the head that states
it, with its command in Results. Guarantees are stated at the strength delivered, and a live-tense sentence about
old behaviour is fixed in the same pull request. Universal guarantees are Hypothesis properties; any property
that loads the map carries `settings(deadline=None)`. Every sourced constant has a planted source-change case:
the read list from `READABLE_SETTINGS`, the lab key from `eval/eras.py`, the stamp from the MANIFEST, the slot
literals from the era's templates. One writer per file.

**Publication.** Every push to `main` rebuilds and republishes the demo (`.github/workflows/pages.yml`), and this
card's change ships in the bundle: the served rubric reaches the API and `data/9p2i/eval/rubric.json`, the
Highlights reel and the dashboard histogram score the default set, and the viewer copy changes. So the merge is
the owner's. The pull request states the copy that goes live, the score distribution the reel will show
(including the zero-score games), and the bundle diff between the base and the head.

**Delivery.** The branch is `work/rubric-extractor-era`, delivered as one pull request into `main` and merged by
merge commit or fast-forward, never squash. Each commit body ends with `Card: tasks/work/rubric-extractor-era.md`,
immediately followed by the line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Expected scope

- `audits/workflows/extract_gameplay_facts.py`: the read list, the refusal, the threading, the reset, the
  rebuttal acceptance, the regroup ticks, an optional `--sample-dir` (default `replays/samples/9p2i`) and the
  docstring.
- `experiments/lab/rubric_score.py`: the era-keyed lab names and the `--set-dir` help. Its scoring is untouched.
- `scripts/refresh_samples.sh`: the rubric step, its dry-run line, the help and the `declared_args` comment.
- New committed outputs: `replays/samples/9p2i/results-rubric-score.json`,
  `experiments/lab/results-rubric-score.stage-b-r2.json` and `experiments/lab/results-rubric-geomean.stage-b-r2.json`.
- `frontend/src/lib/copy.ts` (the interestingness strings), `frontend/src/components/TournamentDashboard.tsx`,
  the new `frontend/src/components/TournamentDashboard.test.tsx`, `frontend/src/components/ReplayPicker.tsx`,
  `frontend/src/components/ReplayPicker.test.tsx`, `frontend/src/components/HighlightCard.tsx` (the comment),
  `frontend/src/api/client.ts` (the comment), `frontend/src/stories/ReplayBrowser.stories.tsx` (the comments)
  and `frontend/e2e/evidence-journey.ts` (the rubric legs).
- Comment-only: `api/replay_loader.py`, `api/routes/eval.py`, `api/schemas.py`.
- Tests: the new `tests/experiments/test_gameplay_facts_era.py`;
  `tests/experiments/test_gameplay_facts_refuses_experiments.py` (rewritten in place for the read-list rule);
  `tests/experiments/test_gameplay_facts_genuine_class.py`; `tests/eval/test_recorded_arm_readers.py`;
  `tests/eval/test_kill_cooldown_readers.py`; `tests/eval/test_watchability.py`;
  `tests/orchestrator/test_experiment_arms.py`; `tests/api/test_sets.py`;
  `tests/scripts/test_build_demo_bundle.py`; `tests/scripts/test_refresh_samples.py`.
- `docs/artifacts.md` (three rows), and `experiments/lab/report-rubric-interestingness.md` (the run line only).
- `tasks/README.md`'s inventory sentence, and this card.

Directly necessary follow-through inside these files is permitted. Any other file belongs to another card or
needs the owner.

## Record impact

- **What is added.** No recorded byte is edited. One new file sits beside the recordings:
  `replays/samples/9p2i/results-rubric-score.json`. It is outside the recording fingerprint, as the baseline-9
  rubric was. Two era-keyed lab artifacts are added. The facts JSON stays a temp file.
- **What is unchanged.** `bash scripts/verify_samples.sh` and the four `build_sample_report.py --check` runs
  recompute exactly what they did before.
- **History.** The baseline-9 rubric stays at `d41c9006`, and the two unkeyed lab files and the frozen pin stay
  byte-identical. The baseline-9 reproduction runs in scratch and writes nothing into the tree.
- **Behaviour.** The extractor, an offline audit tool, now reads the era. No agent, engine, meeting or tactical
  path changes, and no game plays out differently. No scorecard, census, evaluation or ML artifact moves.
- **What ships.** The served rubric, the Highlights reel order and the dashboard histogram for 9p2i, and the
  viewer copy, all published through `pages.yml`. The bundle diff bounds the change.
- **The next re-record.** When `replays/samples/9p2i` is next re-recorded, the refresh step regenerates the
  served file and the era's lab files in the same change.

## Validation

```
# development
uv run pytest tests/experiments/ tests/eval/test_watchability.py tests/eval/test_kill_cooldown_readers.py \
  tests/eval/test_recorded_arm_readers.py tests/orchestrator/test_experiment_arms.py tests/api/test_sets.py \
  tests/scripts/test_build_demo_bundle.py tests/scripts/test_public_recording_provenance.py -q
uv run pytest tests/scripts/test_refresh_samples.py -n 4 --dist loadfile -q
cd frontend && npm run lint && npm run tsc:check && npm run test && npm run build
# the production path, from the repository root ($0, no provider), run twice; the second leaves no diff
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py --sample-dir replays/samples/9p2i >/dev/null
uv run python experiments/lab/rubric_score.py "${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json" \
  --set-dir replays/samples/9p2i
git status --porcelain     # the served file and the two era lab files, nothing else
git diff --exit-code d41c9006 -- experiments/lab/results-rubric-score.json experiments/lab/results-rubric-geomean.json
# baseline 9 from its own bytes, in scratch only
git archive d41c9006 replays/samples/9p2i | tar -x -C <scratch>
# the export holds the retired served file at the path the scorer writes: delete it first
rm <scratch>/replays/samples/9p2i/results-rubric-score.json
test ! -e <scratch>/replays/samples/9p2i/results-rubric-score.json
git show d41c9006:replays/samples/9p2i/results-rubric-score.json \
  | cmp - <scratch>/replays/samples/9p2i/results-rubric-score.json   # planted: fails on the missing file
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py \
  --sample-dir <scratch>/replays/samples/9p2i >/dev/null            # exit 0
uv run python experiments/lab/rubric_score.py "${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json" \
  --set-dir <scratch>/replays/samples/9p2i                          # exit 0
git show d41c9006:replays/samples/9p2i/results-rubric-score.json \
  | cmp - <scratch>/replays/samples/9p2i/results-rubric-score.json   # identical
uv run python -c "import json, pathlib as p; from experiments.lab import rubric_score as r; \
f = json.loads(p.Path('${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json').read_text()); \
g = json.loads(p.Path('experiments/lab/results-rubric-geomean.json').read_text()); \
print(all(g[k] == v for k, v in r.geomean_validation(f).items()))"
# nothing recorded moves; the gates
bash scripts/verify_samples.sh
uv run python scripts/build_sample_report.py --sample-dir <set> --check   # samples and ml_corpus, 9p2i and 4p1i
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run python scripts/verify_ml_evidence.py        # offline; never --complete
cd frontend && npm run e2e                         # serially; Playwright is outside check.sh
uv run python scripts/build_demo_bundle.py --out <scratch>/before|after && diff -rq <scratch>/before <scratch>/after
bash scripts/check.sh                              # whole, in a clean worktree, real exit code quoted
```

Run `check.sh` to the end rather than stopping at the first failure, because `set -e` masks later gates.

## Results

Not started.
