# Partial record: re-recording `samples/9p2i` alone on the Stage-B arms

Investigator memo, topic `partial_record`, 2026-09-24. Read-only on `main` at `e886b663`
(baseline 9). Every citation is `path:line` at that commit. No model call, no recorder
against a provider, no held-out band, no rendered prompt printed, nothing committed.
Every probe used the in-process fake provider and wrote only to the session scratchpad
(`.../scratchpad/pr0924/`); the reproduction list is at the end. All census figures are
count-only.

Set names as in the analysis memo: `s9` = `replays/samples/9p2i`, `c9` =
`replays/ml_corpus/9p2i`, `s4` = `replays/samples/4p1i`, `c4` = `replays/ml_corpus/4p1i`.

---

## 0. Bottom line

1. **The working hypothesis holds at the engine and loader layer and fails everywhere
   downstream.**
   - It holds: an arm recorded in `RecordedExperimentConfig` is re-simulated from the
     recorded row, not the shell. A bare-shell `verify_samples` passes on arms-ON and
     temporal-ON fake recordings. The shared replay walk re-verifies every tick and
     meeting hash of a full wave-config recording once a profile is allowed to read it.
   - It fails in three places:
     1. **The recorder.** It has no way to set the tactical or engine arms.
     2. **The recorder's own post-steps.** Both crash on an arms-ON set.
     3. **Twelve committed-set consumers refuse the set outright.** Eight replay-walk
        profiles, the off-menu instrument, the frozen surrogate and conviction tables, the
        prompt-byte golden and the rubric extractor. Several more pool across the four sets.
2. **Only recording-bound switches are compatible with a partial record.** A new ambient
   substrate lever that is ON in a committed set fails the bare-shell loader. That is the
   Phase-21 wall (`audits/audit-phase-21-adopting-record.md:1050-1058`). So every Stage-B
   switch must be a `RecordedExperimentConfig` field. That includes B4: a narrow body-handle
   field, not the `temporal_observations` lever. Temporal ON adds a second refusal class
   across the same eleven consumers. It also fails the validity gate's provenance check in a
   bare shell.
3. **Recommended landing:** record s9 seeds 0-49 first as assessment evidence **outside**
   `replays/samples/`.
   - This follows the Phase-21 precedent: an orphan evidence commit, or an in-tree
     `replays/records/` set with a `docs/artifacts.md` row.
   - It needs three prerequisite cards (recorder, reader support, validity gate) and
     nothing else. No tour, public-results, scorecard, doc-fact, watchability or s9 re-pin
     sweep. Nothing publishes through `pages.yml`, and the owner can iterate 50-seed records
     without churning the canonical tree.
   - Moving the games into `replays/samples/9p2i` in place is then the adoption step, with
     the mixed-tree card listed in section 5.
   - If the owner wants in place now, section 5 is the complete list.

---

## 1. The hypothesis, checked line by line

Hypothesis: the wave adds or extends arms default-OFF, the 50-seed record is recorded with
them ON, the other three sets keep loading, verifying and feeding every gate, and adoption is
later.

| claim | verdict | evidence |
|---|---|---|
| Arms exist and are stamped on every tick row; a missing config means historical defaults | HOLDS | `orchestrator/experiment_config.py:29-47`, `:137-165`; `orchestrator/replay.py:307-314`, `:741-775`. The committed s9/c9/s4/c4 rows carry no `experiment_config` key at all. Only `audits/deduction-candidate/run-2026-09-16` (format 2) and `tests/fixtures/v3_policy_reconstruction` do. |
| The loader re-simulates under the recorded config, not the shell | HOLDS | `api/replay_loader.py:1454-1458`, `:1633-1640` (redistribution), `:1813` and `:1938` (meeting reset); `eval/replay_walk.py:740-760`. Probe: the wave set walked with all hashes verified (section 3). |
| A lever-ON set verifies in a bare shell | HOLDS ONLY for `temporal_observations` | The reader carve-out at `api/replay_loader.py:785-790` forces temporal ON when the tick rows carry a version. Every other toggle is compared against the ambient slate (`:745-783`) and refused. That is the Phase-21 precedent (`audits/audit-phase-21-adopting-record.md:1050-1058`). |
| The shipped recorder can record the arms ON | FAILS for meeting_reset, vent_exit_policy, the R7 witness arm and any new field; HOLDS via env for bounded rebuttal and temporal | Section 2. |
| The other three sets keep feeding every gate | FAILS for in-place landing | Consumers that pool the four sets or key one baseline for the tree (section 5). The other three sets' bytes and per-set checks are untouched. |
| Default-OFF keeps the ML fits valid | HOLDS | The committed fits are version-one records: `corpus_sha256` 6536c68c in `training/artifacts/{surrogate,conviction}/fit-corpus.json`, a digest of corpus bytes only (`training/provenance.py:57-68`). The v2 derivation fingerprint covers 109 files, including `engine/rules.py`, `engine/meeting_reset.py`, `orchestrator/game.py` and `meetings/manager.py` (measured with `derivation_files()`). It binds only future v2 fits. The committed-artifact refit pins re-derive from c9 with current code, so each Stage-B card must leave the OFF path byte-identical on c9. |

---

## 2. Question 1: can the shipped recorders record with the arms ON?

**Only partly, and not the arms Stage B needs most.**

- **What `refresh_samples.sh` passes.** Per seed it calls `scripts/run_tournament.py` with
  exactly seven flags:
  - `--start-seed`;
  - `--num-games 1`;
  - `--output-dir`;
  - `--num-players`, `--num-impostors`, `--tasks-per-crewmate`;
  - `--force`.

  Source: `scripts/refresh_samples.sh:879-886`, printed verbatim by the dry run (section 7).
- **`run_tournament.py` has no experiment flag.** Its argparse block (`:248-456`) offers the
  roster, max-ticks, force, the policy stamp, the agent factory and artifacts, resume, and the
  spending caps. None of them sets a `RecordedExperimentConfig` field.
- **The tournament path never passes a config.** `eval/balance_eval.py:364-367` builds the
  default agent factory with no config. `:386-400` constructs `HeadlessGame` without
  `experiment_config`.
- **Who does construct non-default configs.** Outside tests, only the offline experiment
  harnesses:
  - `experiments/tactical_gameplay.py:99-109`, `:585-605`;
  - `experiments/investigation_evaluation.py:87-135`;
  - `experiments/deduction_evaluation.py:55-70`;
  - `experiments/fresh_deduction_instrument.py:1153-1160`.

  All of them are fake-provider, and none writes a sample set.
- **What CAN be recorded today, through the environment:**
  - `bounded_rebuttal_version=1`, via `AILIBI_BOUNDED_REBUTTAL=1`.
    `build_default_meeting_runner` reads the evidence profile from the environment
    (`orchestrator/game.py:1377-1380`; `meetings/evidence_profile.py:14-31`, `:91-104`).
    `HeadlessGame` merges that profile into the recorded config (`orchestrator/game.py:2250-2288`).
    Probe: rows stamped `{format_version 1, bounded_rebuttal_version 1}`.
  - `temporal_observations`, via `AILIBI_TEMPORAL_OBSERVATIONS=1|2` plus
    `--expect-levers temporal_observations`.
- **Blind spot in the pre-spend check.** The positive slate check `substrate_slate_mismatches`
  (`orchestrator/replay.py:1220-1279`) covers only the five toggleable levers
  (`:1063-1071`). It does not cover the four-switch experiment registry
  (`meetings/evidence_profile.py:25-32`: `AILIBI_EVIDENCE_REASONING`,
  `AILIBI_BOUNDED_REBUTTAL`, `AILIBI_PUBLIC_ACCOUNTS`, `AILIBI_ATTRIBUTED_TESTIMONY`).
  - **Probe:** with a stray `AILIBI_BOUNDED_REBUTTAL=1` and `--expect-levers ""`, the dry
    run printed "Substrate slate OK". A stray experiment export silently changes the
    recording. It shows only in the tick rows, not in the MANIFEST, whose columns carry
    substrate flags and the policy but no experiment config
    (`scripts/_manifest_writer.py:108-130`).

**Minimal recorder change (card: recorder threads a declared experiment config).**

1. **`run_tournament.py --experiment-config FILE`.**
   - The file is validated as a `RecordedExperimentConfig`.
   - It is threaded to `run_tournament_eval(experiment_config=...)`. That function passes it
     to `HeadlessGame(experiment_config=...)` and to
     `build_default_agent_factory(experiment_config=...)`. The factory is required:
     `orchestrator/game.py:2855-2873` refuses a factory that does not implement a recorded
     tactical arm.
   - The meeting runner is built with an env mapping that serves the config's meeting-profile
     fields (bounded rebuttal). `HeadlessGame` refuses a runner that disagrees with the config
     (`orchestrator/game.py:2254-2264`).
   - The config goes into the resume `configuration` dict (`scripts/run_tournament.py:1380-1403`).
     All `AILIBI_*` env values are already hashed (`scripts/_tournament_progress.py:92-99`), but
     a file is not.
2. **`refresh_samples.sh --experiment-config FILE`.**
   - A passthrough.
   - A dry-run echo of the parsed config.
   - A whole-slate refusal of any ambient experiment-registry export.
   - A refusal of a non-default config unless `AILIBI_SAMPLE_DIR` is explicit. The default
     target is `replays/samples/4p1i` (`scripts/refresh_samples.sh:35`), so a forgotten export
     would re-record s4 on the wave.
3. **Policy-stamp honesty.** An experimental tactical arm runs `ExperimentalImpostorPolicy`,
   but the recorder stamps `fsm-default` (`scripts/run_tournament.py:1081`;
   `orchestrator/replay.py:532-548`). The replay also records `agent_factory_kind`
   "experimental" and the config, so the facts are recoverable. The card should either stamp a
   distinct id or state in the stamp docstring that fsm-default plus a config means the arm.
4. **Planted tests:**
   - a stray `AILIBI_BOUNDED_REBUTTAL` is refused;
   - a config file with an unknown field is refused;
   - the default-target guard bites;
   - a fake-provider seed recorded through the recorder stamps exactly the file's config.

**Config format.** B1, B2 and B3 are format-1 legal (`orchestrator/experiment_config.py:65-94`).
The new fields (R7 witness rule, B4 handle, R8 and R10) should follow the file's own
convention:
- a new `format_version` 4 whose serializer drops the new keys below 4, as
  `_preserve_version_one_bytes` does (`:96-107`);
- format 3 is unusable here, because it requires evidence version 2 (`:75-76`).

---

## 3. Question 2: does an arms-ON or lever-ON recording verify in a bare shell?

**Test sets.** Fake-provider 9p2i scratch sets, each checked in a shell with 0 `AILIBI_*`
exports:
- `bare`: the recorder, as shipped;
- `temponly`: `AILIBI_TEMPORAL_OBSERVATIONS=1`;
- `rebutonly`: `AILIBI_BOUNDED_REBUTTAL=1`;
- `wave`: `meeting_reset=hub_with_grace`, `vent_exit_policy=observed_risk` (the stand-in for
  B1), bounded rebuttal and temporal v1;
- `wavenotemp`: the same arms without temporal.

| consumer | bare | temponly | rebutonly / wave |
|---|---|---|---|
| `scripts/_verify_samples.py` (API loader, the bare `verify_samples.sh` leg) | clean 4/4 | clean 2/2 | clean 2/2 and 4/4 |
| shared walk with support flags flipped in memory (no file edit), tick, disposition and meeting-post hashes verified | - | - | wave: 4 games, 136 tick hashes, 9 meeting post-hashes, 4 reached game over |
| `scripts/validity_gate.py` | PASS 10/10 | FAIL: 3 checks unavailable ("does not support temporal observations"); check 9 fails, stamp vs build snapshot on `temporal_observations` | FAIL: 3 checks unavailable ("does not support experimental recordings"); check 9 passes |
| `build_sample_report.py` (the recorder's own post-step, `scripts/refresh_samples.sh:1036-1037`) | ran | REFUSED at `eval/kill_craft.py:420` | REFUSED, same place |
| rubric-step extractor (`scripts/refresh_samples.sh:1049-1076`) | returned 0 | SystemExit: toggle stamped differently from the shell (`audits/workflows/extract_gameplay_facts.py:2167-2173`) | wavenotemp: RuntimeError, "61 extraction invariant(s) failed". It applies meetings without the reset (`:2751-2758`) |
| prompt-byte golden walk (`tests/meetings/test_prompt_byte_golden.py`) | 168/168 prompts byte-equal | refused at `:656` | rebutonly 104/104, but vacuous: no rebuttal fired. wavenotemp: meeting-0 `state_hash_after` mismatch |
| solvability, funnel, pooling funnel, evidence honesty, kill-craft, win-condition self-check | ran | all REFUSED (temporal) | all REFUSED (experimental) |
| off-menu (`eval/off_menu.py:359-363`) | ran | REFUSED | REFUSED |
| watchability referee | ran | fails closed, `integrity_ok=False` | fails closed |
| surrogate meeting table and conviction table (`training/surrogate/dataset.py:1025-1026`) | ran | REFUSED | REFUSED (the temporal check fires first on wave) |
| process-scorecard fold, public results, leak scan | ran | ran | ran |

**Findings.**

1. **The eight walk refusals are declared-scope refusals.** They are not reconstruction gaps.
   - The profiles carry `supports_experiments=False` and `supports_temporal_observations=False`:
     - `eval/balance_eval.py:914` (kill-gift);
     - `eval/evidence_honesty.py:2605`;
     - `eval/funnel.py:254`;
     - `eval/kill_craft.py:527`;
     - `eval/solvability.py:698`;
     - `eval/validity.py:506-514`;
     - `eval/watchability.py:1544`;
     - `eval/win_condition_selfcheck.py:205`.
   - Refusal points: `eval/replay_walk.py:354-355`, `:505-515`.
   - Only `current-report` (`eval/balance_eval.py:933`), `process-scorecard`
     (`eval/process_scorecard.py:782-787`) and `leak-scan-factory` (`eval/leak_scan.py:950`)
     accept both.
2. **Each flip needs a per-instrument reading, not a blanket flip.**
   - Instruments that read engine events and recorded meeting rows are safe to extend once
     the walk threads every recorded arm: validity, kill-craft, kill-gift, win-condition,
     solvability, funnel.
   - Instruments that re-run a live policy against recorded actions must keep refusing an
     experimental tactical arm:
     - off-menu;
     - evidence honesty's `live_impostor_policy` (`eval/evidence_honesty.py:896-900`);
     - `training/anchor_study.py:443-447`.
3. **The validity gate needs code in both halves.**
   - Its walk refuses the arms.
   - Its provenance check compares every stamp with `substrate_flag_snapshot()`
     (`eval/validity.py:960-992`) and has no temporal carve-out. It also has no check that
     every game carries the same experiment config (`eval/validity.py:40-60` lists the ten
     checks). A set in which some seeds were recorded without the arms would pass check 9.
4. **B4 through the temporal lever costs a second refusal class and more.**
   - It fails the gate's check 9 in the bare pytest shell.
   - `tests/conftest.py:67`, `:110-119` clears every `AILIBI_*` variable, so no lever-ON
     shell is available to pytest.
   - It trips `tests/orchestrator/test_replay.py:2227-2244`, which compares every committed
     stamp against a bare build.
   - B4 as a narrow recording-bound field (as the sibling memo `rebuttal_and_body_handle.md`
     option (b) also concludes) adds no refusal class. B1-B3 already make the config
     non-null.
5. **R7's witness rule is invisible to the hash chain.** The tick rows record actions and a
   state hash only (`orchestrator/replay.py:307-324`). Vent witness sets live in events
   (`engine/events.py:94-113`; `engine/rules.py:146-172`), not in `WorldState`.
   - A reader that walks an R7-ON set without threading the arm reproduces every hash. It
     silently derives the wrong vent observations and flags:
     - `observation/service.py:651-663`;
     - `eval/funnel.py:428-437`;
     - `eval/leak_scan.py:138-147`, `:851-859`;
     - the loader's memory rebuild, the golden, the rubric extractor, and the census's
       `walk.py`.
   - `advance_tick` has 14 non-test call sites and 182 in tests (counted), and today's
     precedent arm `redistribution_policy` defaults silently (`engine/tick.py:594-601`).
   - **Mitigations:** record the rule in the config, make the new keyword required at every
     reader call site, and add a planted event-level test per reader. The hash cannot catch
     it; no verify leg does.

---

## 4. Question 3: the exact 50-seed invocation, and what the validity gate must be told

**Prerequisites:** the recorder card (section 2), the reader-support card and the
validity-gate card (section 8). The field names below are placeholders for the implementing
cards.

**`wave.json`** (the declared config; format 4 per section 2):

```
{"format_version": 4,
 "meeting_reset": "hub_with_grace",            # B2 full reset (existing arm)
 "vent_exit_policy": "<B1 new literal>",        # B1 look-first exit
 "bounded_rebuttal_version": 1,                 # B3 alone; no reporter_reasoning
 "vent_witness_rule": "physical",               # R7 engine arm
 "report_body_handle_version": 1,               # B4 minimal handle
 "<R8 field>": 1, "<R10 field>": 1}             # if those cards are recording-bound arms
```

**Shell.** Only these exports; no other `AILIBI_*` variable:

```
AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2
AILIBI_SAMPLE_DIR=<target> AILIBI_MANIFEST=<target>/MANIFEST.md
AILIBI_REFRESH_WORKERS=2 AILIBI_SEED_MAX_ATTEMPTS=8     # baseline-9 operating values
FEATHERLESS_API_KEY=<set by the operator; never printed>
```

**Phases:**

```
# 0  preview, no call, no write
bash scripts/refresh_samples.sh --full --expect-levers "" --experiment-config wave.json --dry-run
# 1  probe seed, then the honesty probe and the census on it
bash scripts/refresh_samples.sh --seeds 0 --expect-levers "" --experiment-config wave.json
# 2  the rest, at the SAME HEAD as phase 1 (no commit between phases)
bash scripts/refresh_samples.sh --seeds 1,2,...,49 --expect-levers "" --experiment-config wave.json
```

`<target>` is `replays/records/stage-b-s9` for assessment-first landing (recommended), or
`replays/samples/9p2i` in place.

**Acceptance, in a bare shell (0 `AILIBI_*` exports, as baseline 9 ran it:
`audits/audit-2026-09-22-process-rerecord.md:615-647`):**

```
uv run python scripts/validity_gate.py <target> \
  --expected-model Qwen/Qwen3.6-27B --require-zero-cost \
  --expected-prompt-versions accusation_round=accusation_round.qwen3_6_27b.v6,\
crewmate_report=crewmate_report.qwen3_6_27b.v6,\
impostor_report=impostor_report.qwen3_6_27b.v6,\
vote_ballot=<vote_ballot.qwen3_6_27b.v8, or R8/R10's arm stamp> \
  --expected-experiment-config wave.json          # NEW flag (validity card)
bash scripts/verify_samples.sh <target>
```

**What the gate must be told, and why:**

- **Expected model and zero cost.** As baseline 9.
- **The prompt versions.**
  - Bounded rebuttal and temporal move no version stamp. Measured with
    `prompt_versions_for_set`: `AILIBI_BOUNDED_REBUTTAL=1`, `AILIBI_TEMPORAL_OBSERVATIONS=1`
    and `=2` all return the base map. Only the prompt levers move stamps:
    `reporter_reasoning` moves `accusation_round` and `crewmate_report`; `impostor_roll_call`
    moves `accusation_round` and `impostor_report`.
  - So the four base strings stand unless R8 or R10 changes `vote_ballot` bytes. That card
    decides the stamp (section 6).
- **The expected experiment config** (new). This is the only gate that would catch a
  within-set mix of arms or a stray experiment export.
- **`--expect-levers` stays `""`** when B4 is the narrow field.
  - If the orchestrator instead chooses temporal for B4: export
    `AILIBI_TEMPORAL_OBSERVATIONS=2` and pass `--expect-levers temporal_observations`.
  - The slate check cannot tell v1 from v2.
  - The gate's check 9 then needs the loader's recorded-version carve-out.

**Budget, as a proposal for the owner's spend ruling.**
- The baseline-9 s9 leg: 1,694 calls, 9,850,930 input, 422,941 output, 2h24m55s, $0
  (`audits/audit-2026-09-22-process-rerecord.md:415`).
- B3 adds at most one call per meeting: at most 145, the baseline-9 s9 meeting count
  (`:628`).
- B2 removes meetings:
  - fake-provider 9p paired games: 676 -> 484 calls (`audits/tactical-gameplay/README.md:123`, `:129`);
  - my fake seeds 0-1: 8 -> 5 meetings.
- R8 may enlarge the ballot body.
- Suggested ceilings: 2,100 calls, 12.5M input, 0.55M output, 3.5 h recording wall, $0 on
  flat-rate Featherless.

---

## 5. Question 4: every surface whose meaning changes under a mixed-baseline tree

This applies only if the new games land IN `replays/samples/9p2i`. With assessment-first
landing, rows 1-8 still apply to the staging set and rows 9-20 do not change at all.

| # | surface | what breaks or changes meaning | minimal truthful handling |
|---|---|---|---|
| 1 | `scripts/validity_gate.py` and `eval/validity.py:506-514`, `:939-992` | refuses the arms; no config homogeneity check | the validity card: profile support after review, `--expected-experiment-config`, a temporal carve-out only if temporal is used. Planted: a mixed-config set FAILS. |
| 2 | `scripts/build_sample_report.py:177-208` (and its `--check`) | kill-craft refusal; the recorder exits non-zero after the MANIFEST rows are written | extend `eval/kill_craft.py:527` after review. `--check` is per set, so the s9 before and after are the committed report at `e886b663` and the rebuild; nothing is pooled. |
| 3 | rubric extractor (`audits/workflows/extract_gameplay_facts.py:179`, `:2150-2180`, `:2235`, `:2751`) | experiment-blind walk; ambient-bound stamp check | route it through `eval.replay_walk` with the recorded config (the one-home rule), or thread `meeting_reset`, redistribution and R7. Runs only when the target `-ef` s9 (`refresh_samples.sh:1049`). |
| 4 | prompt-byte golden (`tests/meetings/test_prompt_byte_golden.py:174`, `:431-466`, `:656`, `:781`) | walks s9 and s4; builds the manager without the recorded evidence profile; applies meetings without the reset; refuses temporal | build the manager and the walk from the recorded config (profile, reset, R7, B4 handle). Planted: a scripted rebuttal meeting reproduces byte-equal, and dropping the profile fails. |
| 5 | walk profiles: solvability, funnel, win-condition, kill-gift, watchability referee, evidence honesty | refuse | flip after review (section 3, finding 2). The cached committed walks in `tests/_helpers/committed.py:71-80` for funnel, kill-craft, deception (which walks through the funnel profile, `eval/deception_instruments.py:169`) and solvability otherwise error at fixture setup for every s9 test that reads them. |
| 6 | off-menu, `training/anchor_study.py`, surrogate and conviction tables (`tests/training/test_surrogate_dataset.py:50` is default tier; `test_conviction_model.py` and `test_surrogate_fidelity.py` are `campaign`) | refuse, correctly (they re-run baseline policies or are frozen ML instruments) | keep refusing; drop s9 from their committed-set parametrizations, since ML is on hold (ruling 12) and the fits read c9 only. |
| 7 | R7 readers (section 3, finding 5) | a silent wrong-witness risk | required keyword plus a planted event-level test per reader |
| 8 | `scripts/refresh_samples.sh` itself | section 2 | the recorder card |
| 9 | `eval/process_scorecard.py:1856-1925`; `docs/process-scorecard.md` provenance text ("These four sets are one era") | pools all four sets and the two 9p2i sets unconditionally, which crosses the boundary | era-aware pooling: group sets by their recorded identity (normalized config, temporal version, prompt versions, stamp) and pool only within an era. Publish s9 as its own era. Its before column is the s9 row of the committed `docs/process-scorecard.json` at `e886b663`. The nine-row scorecard is otherwise unchanged, and no census cell joins it (R13). |
| 10 | `scripts/counterfactual_phase21.py:204-209`, `:259-266`; pooled pins in `tests/scripts/test_counterfactual_phase21.py:365-390` | a pooled four-set walk; the baseline-9 s9 pin 9; refuses temporal | scope `CANONICAL_SETS` to the baseline-9 era. The pooled cells are then a three-set population, so re-derive and label them rather than keeping the four-set pins. |
| 11 | `scripts/check_doc_facts.py`: `_LADDER_TIP_AUDIT` (`:237`), `record_win_rates` (`:1600-1650`), the newest-date rule (`:1368-1405`), `check_ladder_tip` (`:1705-1795`), `check_conviction_partition` (`:2732-2770`) | one tip for the tree; the tip audit's win-split after column must equal both sample MANIFESTs; the README may state only the newest refresh date, so it cannot truthfully give s4's older date | leave the tip at baseline 9 (no adoption). Add a per-set provenance source naming the s9 record's audit for `samples/9p2i` facts, and per-set refresh dates. Do not pool the front-door headline pair across eras. |
| 12 | `eval/watchability.py:559`, `:1039-1129` (baseline-9 floors), `:1129` (`_DEFAULT_BASELINE_ID`, global); `tests/eval/test_watchability.py:195-203`, `:736-779` | the baseline-9 9p2i pins lose their byte source; the default id serves both rosters; the referee is FROZEN (Phase 19) | a new block keyed to the record (a stage id, not "baseline-10": nothing is adopted) with only a `9p2i` entry, pinned from the new bytes; a per-set default id; baseline-9's 9p2i entry becomes history, as baseline-8's did. |
| 13 | `api/public_results.py:35-41` (source root pinned to commit 9bae2b03 and the s9 seed 0, 23 and 29 sha256), `:355-366`, `:488-494` | on any s9 byte change the three curated cases drop silently (sha mismatch -> `continue`) and `source_url` becomes None | a publication decision: re-derive the cases on the new bytes, or withdraw them. Plus the tests in `tests/api/test_public_results.py`. |
| 14 | tour: `frontend/src/components/ReplayPicker.tsx:109-150` (four s9 cards with countable claims), `tests/api/test_sets.py:548-700` (the per-set head criterion and planted seeds 2, 7, 10, 12, 13, 36, 44, 46), `frontend/e2e/journey.spec.ts:64`, `:477-486` | every s9 claim and planted case is falsifiable by B1-B3 | the tour is deferred. The minimal green change: re-run `scripts/measure_featured_criterion.py`; keep the s4 cards; reduce the s9 strip to one head chosen by the criterion, with a label making only re-read counts and no "no flagged contradictions" promise; re-derive the planted s9 rejection seeds. If no s9 first meeting ejects on role proof, the per-set head clause (`test_sets.py:583-586`) needs the owner's ruling. |
| 15 | `tests/api/test_sets.py:372-384` (one recording sha per MANIFEST) | the two-phase guard (section 6) | keep it as is; it is the protection |
| 16 | frontend fixtures `frontend/src/lib/bodies.test.ts:109`, `:441` and `contradictions.test.ts` (per-set `corpusSha256`) | the s9 digest moves | re-derive s9 only; s4 is unchanged; nothing is pooled |
| 17 | `scripts/build_demo_bundle.py:90`; `.github/workflows/pages.yml:19-20` | merging to `main` publishes the new s9 games and featured list | publication ruling at merge (AGENTS.md "A push to main publishes") |
| 18 | about 68 test files reading s9 (counted with `git grep`); pooled pins such as `tests/meetings/test_contradictions.py`'s committed-meeting count | the ordinary re-pin sweep | re-derive by the production computation and list old -> new. Rates pooled across eras are split; pure counts of what the tree holds may be re-pinned with a label. |
| 19 | `replays/ml_corpus/*/MANIFEST.md` FROZEN lines; `training/provenance.py`; `scripts/verify_ml_evidence.py:134` | unchanged: the corpus bytes do not move and v1 fits key on them | nothing, provided every card keeps c9's OFF derivation byte-identical |
| 20 | `orchestrator/replay.py` lever registry; `.env.example`; `check_lever_registry` and `check_experiment_registry` | unchanged, if no new lever is added | Stage B adds no substrate lever (section 0.2) |

---

## 6. Question 5: two prompt versions side by side, the two-phase protection, and graduation

**If s9 moves to `vote_ballot` v9 while the corpus and s4 stay at v8** (R8 or R10 as a direct
registry bump, the way the substrate wave bumped v6 -> v7 -> v8 at `orchestrator/game.py:430-442`):

1. **The prompt-byte golden walks s9 and s4** (`tests/meetings/test_prompt_byte_golden.py:174`).
   - s4's v8 stamps would match no live set, and `resolve_prompt_set` raises (`:468-503`).
   - **What must exist:**
     - an `ARCHIVED_PROMPT_VERSION_SETS` entry and byte copies of the v8 bodies under
       `tests/fixtures/prompt_archive/<name>/` (`:180-201`);
     - an `ARCHIVED_MAP_CARDS` entry if the map card moved;
     - `test_the_bump_in_flight_window_is_closed_and_the_archive_is_empty` (`:1445-1467`)
       inverted to an open-window test.
   - This is the shape of the v5 archive retired at `a4bbee7f`.
   - Under a partial record the window stays open until s4, c9 and c4 are re-recorded.
2. **Other surfaces a bump moves:**
   - `scripts/record_ml_corpus.sh:171` pins the live registry and its preflight asserts it
     (`:778`; `tests/scripts/test_record_ml_corpus.py:627-630`, `:985`), so the pin must move
     even though the corpus bytes stay v8;
   - the validity gate is given versions per set;
   - `check_sample_provenance` needs the README to name both v8 and v9 (`scripts/check_doc_facts.py:1469-1478`).
3. **Recommended instead (AGENTS.md craft rule 7).** A recording-bound version overlay:
   - The R8/R10 arm serves a composite stamp such as `vote_ballot.qwen3_6_27b.v8.<arm>` from
     the recorded config.
   - The live default stays v8, the archive stays empty, and s4, c9 and c4 resolve through
     the live registry as today.
   - The golden resolves s9 through its overlay-owner index (`:512-555`), extended to
     experiment-bound arms.
   - Today's overlays key only on ambient substrate levers (`orchestrator/game.py:591-660`),
     so this is a small extension of `prompt_versions_for_set`. An ambient-bound lever
     would hit the Phase-21 wall.

**The two-phase `--seeds` run, and what protects it.**

- **Why two phases.** Baseline 9 ran `--seeds 0` (the probe), then `--seeds 1..49`
  (`tasks/work/process-rerecord.md:399-405`). `refresh_samples.sh` re-records any named seed
  even if it is on disk; there is no skip. So phase 2 must not name seed 0.
- **Canonicality must be checked by hand.** `--seeds` mode does not run the canonicalize
  sweep (`scripts/refresh_samples.sh:1015-1020`).
- **Protection against a seed that is never re-recorded:** the one-sha MANIFEST test
  (`tests/api/test_sets.py:372-384`).
  - A seed skipped in both phases keeps its baseline-9 row and git_sha, so the test fails.
  - HEAD is read once per run (`scripts/refresh_samples.sh:693`). A commit between the two
    phases therefore also fails it; do not checkpoint between phases.
  - This protection applies only where a test walks the target. For a staging set, the
    validity card's config-homogeneity check and an explicit canonicality check (exactly
    seeds 0-49, 50 rows) are the guard.
- **Do not use `--meetings` mode.** It derives seeds from the MANIFEST's prompt-version
  column (`:88-103`), so seeds without a meeting would keep their old bytes. All 50 s9 seeds
  had meetings at baseline 9, but a stale MANIFEST cannot promise that for the next record.
- **The default target is s4** (`:35`). Among other exports, the s4 `roster.json` (4/1/1)
  guard catches only a forgotten sample dir with 9/2/2 exported. The recorder card's
  explicit-target guard closes the rest.

**Graduation, at a later full record of c9, s4 and c4 on the wave:**

- **Recording-bound arms** (meeting_reset, the B1 literal, bounded rebuttal, the R7 rule, the
  B4 handle, R8 and R10):
  - The recorder switch is retired. The recorders always write the adopted config, and the
    `AILIBI_BOUNDED_REBUTTAL` entry in `EXPERIMENT_ENV_NAMES` and `.env.example` is deleted.
  - The recorded fields stay as the stamp (craft rule 3). "Missing config means historical
    defaults" (`orchestrator/experiment_config.py:137-142`) must keep meaning the OLD
    behaviour, so the adopted values are written explicitly.
  - The OFF code paths (the `preserve` reset, the target-distance exit, the both-rooms
    witness rule, the raw body id) are deleted only when no committed recording reads them.
    Today that includes the fifth-run archive at `audits/deduction-candidate/run-2026-09-16`
    (format 2, `meeting_reset` preserve), which the scorecard appendix folds, and
    `tests/fixtures/v3_policy_reconstruction`.
- **If temporal had been used:** it moves to `_RETIRED_ALWAYS_ON_LEVERS`
  (`orchestrator/replay.py:998-1020`) and its resolver is deleted. That requires every set
  re-recorded, because a retired lever stamped OFF is refused.
- **If a registry bump had been used:** the archive closes.
- **Everything else that moves at the full record:**
  - the stage watchability block becomes baseline 10 for both rosters;
  - `_LADDER_TIP_AUDIT` moves;
  - the corpus re-freezes and the ML re-ground refits on the new c9 digest.

---

## 7. The dry run, measured

**Invocation:**

```
AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2
AILIBI_SAMPLE_DIR=replays/samples/9p2i AILIBI_MANIFEST=replays/samples/9p2i/MANIFEST.md
bash scripts/refresh_samples.sh --full --expect-levers "" --dry-run
```

**Resolved configuration, count-only:**
- exit 0; 0 provider calls; 0 files changed (`git status --porcelain`: 0 lines); 0.40 s wall;
- mode full, 50 seeds (0-49);
- roster 9/2/2, with a `roster.json` consistency check;
- provider featherless;
- 3 preflights described (key, model coupling `Qwen/Qwen3.6-27B`, registry), none executed;
- prompt set `qwen3_6_27b`;
- lever slate bare, with 0 toggles expected ON;
- 2 seed workers, 4 attempts per seed;
- 1 `run_tournament.py` call per seed carrying 7 flags, 0 of them experiment flags;
- 1 report rebuild; the rubric step applies because the target is s9.

**Cosmetic.** The printed seed list ends in a trailing comma (macOS `seq -s,`). The array
split drops it, so it has no effect.

**Other dry-run probes:**
- `--expect-levers temporal_observations` without the export: refused, exit 1, naming
  `AILIBI_TEMPORAL_OBSERVATIONS`.
- With the export: OK.
- With a stray `AILIBI_BOUNDED_REBUTTAL=1` and `""`: OK. That is the blind spot of section 2.

**Fake end-to-end runs through the shipped recorder (scratch targets only):**
- `--seeds 0,1,2,3` on the bare slate: 5.7 s wall, $0, 4/4 seeds reached a meeting,
  13 meetings, the report rebuilt.
- The same with temporal and/or rebuttal ON: seeds and MANIFEST rows written, then exit
  non-zero at the kill-craft refusal.
- **The fake provider cannot exercise B3.** With rebuttal ON, seeds 0 and 1 recorded the
  same turn and call counts as bare (33 and 19 turns): the fake never accuses the opener.
  B3's planted tests need a scripted client.

---

## 8. Cards

1. **Recorder threads a declared experiment config** (section 2). A prerequisite for any
   record.
2. **Readers support the recorded arms.**
   - Per-instrument review; flip the event-level profiles.
   - Thread every recorded arm, including R7 as a required keyword, through the walk, the
     loader, the golden and the rubric extractor.
   - Keep policy-re-running instruments refusing.
   - Planted tests per reader.
   - A prerequisite, because the assessment needs the gate, the report and the census on the
     new set.
3. **The validity gate learns arms.** `--expected-experiment-config`, config homogeneity,
   profile support. Planted: a mixed-config set fails, and a set with the recorded arm
   missing fails. A prerequisite.
4. **(Optional, recommended) Stage landing.** A `docs/artifacts.md` row and a class-(b)
   wrapper, or an orphan evidence pin, for the 50-seed assessment set, per the Phase-21 §6.1
   mechanism.
5. **(Only for in-place landing, or later at adoption) The mixed-tree card**, section 5 rows
   9-18:
   - era-aware scorecard pooling;
   - counterfactual scope;
   - per-set doc-fact provenance and dates;
   - watchability per-set default and stage block;
   - public-results and tour minimum;
   - the s9 re-pin sweep.

   The owner rules on publication.

---

## 9. Could not establish

- The real-model effect of B3. The fake provider never triggers a rebuttal.
- Whether any s9 game still satisfies the tour's head criterion after B1 and B2. That needs
  the real record.
- The exact field names and format of the R7, B4, R8 and R10 arms. Those belong to their
  cards; this memo uses placeholders.
- Whether evidence honesty's non-policy cells can be separated from its `live_impostor_policy`
  cells, so part of it could accept experimental sets. Not read in full.
- A full pytest count of what an in-place s9 swap turns red. I did not overwrite the tracked
  s9. Fake bytes would move every pin anyway, so the count could not separate refusals from
  re-pins.

---

## 10. Reproduction

Scratch scripts, in `<session scratchpad>/pr0924/`.
Run from the repo root with `PYTHONPATH=. uv run --frozen python <script> <set>`:

- `wave_probe.py <out> 0,1,2,3 [temporal]`: records fake-provider 9p2i games with the
  stand-in arms (writes only to `<out>`);
- `consumers_probe.py <set>`: runs the thirteen consumers and prints RAN or REFUSED plus the
  exception class;
- `walk_probe.py <set>`: the validity walk with support flags flipped in memory;
- `golden_probe.py <set>`: the golden's own set walk, printing byte-equal counts;
- `facts_probe.py <set>`: the rubric extractor re-pointed in memory;
- `count_calls.py <sets...>`: meetings, turns and calls per seed;
- `walkcfg.py`: the support flags of the eleven named walk profiles.

The scratch sets (`bare`, `lever`, `temponly`, `rebutonly`, `wave`, `wavenotemp`) were made
by `refresh_samples.sh` with `AILIBI_LLM_PROVIDER=fake` and scratch `AILIBI_SAMPLE_DIR` and
`AILIBI_MANIFEST`, or by `wave_probe.py`.
