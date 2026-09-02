# Phase-21 Wave-2 smoke — the lever slate ON, live, ruled against the ratified memos (Task 21.23)

**Date:** 2026-09-02. **Task:** 21.23. **Branch:** `phase-21-smoke-wave2`, opened from
`origin/main` `14854a06`.

## 0. The verdict, in one line

**GO** — five live seeds recorded at the ratified Wave-2 slate, the validity gate PASSED on all ten
checks, both reconstructions byte-identical, **all seven §8.1 tripwires PASS against their own
sample-local predicates** (`verdict: every GATED predicate PASSES on these bytes`, the reader
exiting 0 with `stopped_cells` empty), **no §9.2 abandon criterion met**, and the committed record
untouched. The criterion it is ruled against is
`audits/audit-phase-21-preregistration.md` §9.2, read one by one in §14.

**Two things this smoke found that no previous bytes could show, both registered rather than
drift:** a crew speaker filed the project's **first spoken `saw_kill`** (baseline 8 holds zero
anywhere), and with it the **cross-lever ballot interaction Errata E.1 re-registered FIRED for the
first time on live bytes** (§8.4). Neither is a STOP; both are named here because the record will
meet them at scale.

**Source state this report certifies:** `14854a06`. The freeze the ratified pre-registration
declares (`audits/audit-phase-21-preregistration.md` §9) governs from its own stated merge point.
Any merge into `agents/`, `meetings/`, `observation/`, `orchestrator/` or
`agents/strategic/prompts/` between this report and the record reopens the window; the smoke then
runs again from zero, on the changed source, with every number re-derived.

**The memos own the criteria.** `audits/audit-phase-21-preregistration.md` owns the bars, the
decision rule, the seven tripwire predicates, the abandon criteria and the preconditions;
`audits/audit-phase-21-counterfactual.md` owns the predicted cells and its Errata. **Where this
report's reading and a memo disagree, the memo wins and the disagreement is the finding.** This
report invents no criterion, and a class no criterion names is reported in the memo's own words.

**No pre-registered bar is declared met or missed on five seeds.** Every cell below is labelled
**directional at this n**. Where this report needs the standing canon it states it: **baseline 7 is
canon by explicit owner override of a FINDING verdict**, with bar 1 missed at 61/103 = 0.5922
against ≥ 0.60 and bar 2 missed at 42 against < 35 (`audits/audit-phase-20-baseline-7.md` §6, §6.1).
Nothing here states or implies that those bars passed.

---

## 1. What this smoke is

Five live Featherless seeds of the 9p2i roster, recorded at the ratified Wave-2 slate into a
scratch directory OUTSIDE the repository, gated, instrumented, and ruled against the two ratified
memos. It decides nothing. It produces a report and a fork: **GO** means the adopting record's
window opens on this exact source state; **ABANDON** means the defect is described concretely
enough to author a follow-up contract, the routing is named, and the record does not start.

## 2. The recorded configuration

The whole environment was exported in one block before any worker process started; every lever is
read at runner construction, never mid-run. The operator's `FEATHERLESS_API_KEY` is sourced from the
gitignored `.env` at the main checkout and is **not reproduced here, in the PR, or in any log
excerpt in this record** — the wrapper prints an eight-character prefix at
`scripts/refresh_samples.sh`:551 and this report keeps none of it.

```
AILIBI_LLM_PROVIDER=featherless
AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
AILIBI_NUM_PLAYERS=9  AILIBI_NUM_IMPOSTORS=2  AILIBI_TASKS_PER_CREWMATE=2
AILIBI_SAMPLE_DIR=/Users/danielkeinan/ailibi-smoke-21-23/9p2i     # absolute, OUTSIDE the repo
AILIBI_REPORTER_REASONING=1
AILIBI_CORROBORATION_DISCIPLINE=1
AILIBI_TESTIMONY_SHAPES=1
# AILIBI_IMPOSTOR_ROLL_CALL — unset, in this and in every later gate/instrument shell
# AILIBI_REFRESH_WORKERS   — unset; the wrapper's featherless default is 2 (:441)
# AILIBI_SEED_MAX_ATTEMPTS — unset; the wrapper's featherless default is 4 (:461)
```

**The three lever env names were read out of the registry and `.env.example`, not typed from the
contract.** `orchestrator/replay.py`:675-682 holds the four live toggles and
`orchestrator.replay.env_var_for_lever` derives each variable as `AILIBI_<UPPER_SNAKE>`;
`.env.example` documents them at :143 (`AILIBI_IMPOSTOR_ROLL_CALL=0`), :166
(`AILIBI_REPORTER_REASONING=0`), :189 (`AILIBI_CORROBORATION_DISCIPLINE=0`) and :223
(`AILIBI_TESTIMONY_SHAPES=0`). `AILIBI_MANIFEST` needs no export: it defaults under the sample dir
(`scripts/refresh_samples.sh`:37).

**The declared slate is quoted from the ratified pre-registration, not from this report.** §9: *"The
slate: the THREE Wave-2 keys ON, `impostor_roll_call` OFF … The registered slate is therefore
`reporter_reasoning` = True, `corroboration_discipline` = True, `testimony_shapes` = True,
`impostor_roll_call` = False"*, ratified at §10. **It contains three ON keys** out of the four live
toggles.

`$SMOKE_DIR` is outside the repository for the three reasons the contract names: a bare
`bash scripts/verify_samples.sh` walks EVERY set under the samples root
(`scripts/verify_samples.sh`:16-23), so a scratch set under `replays/samples/` would silently join
the committed gate; the per-refresh stage is created under `dirname "$SAMPLE_DIR"`
(`scripts/refresh_samples.sh`:737); and §12 preserves these bytes.

### 2.1 The two shells, and the mechanism that makes crossing them a refusal

**Shell A** carries the three Wave-2 exports and is the ONLY shell that touched `$SMOKE_DIR`:
the recording, the validity gate, both reconstructions, both instrument runs and the tripwire
reader. **Shell B** carries no lever export at all and is the only shell that ran the bare
committed-set gate. Both halves are recorded as run below.

Crossing them does not produce a wrong number — it produces a refusal.
`api/replay_loader.py`:655 (`_assert_substrate_matches`, reached at :1201) compares a recording's
stamped slate against the live substrate through
`orchestrator.replay.substrate_stamp_mismatches` and fails loud on any difference. That is the
mechanism, and it is why the shell discipline is proven rather than asserted.

### 2.2 The preflight refuses in every direction — proven, not asserted

The wrapper's substrate-lever preflight (`scripts/refresh_samples.sh`:303, delegating to
`orchestrator.replay.substrate_slate_mismatches`) runs on the DRY-RUN path (:524) as well as the
real one (:650). Four refusals and one sanctioned preview were run before any seed staged, and
`/Users/danielkeinan/ailibi-smoke-21-23` held nothing after any of them.

**(a) an export nobody declared** — the slate exported, `--expect-levers` omitted:

```
Error: the live substrate-lever slate does not match --expect-levers.
       Expected ON: (none — the bare slate: every live toggle OFF)
       Mismatch: reporter_reasoning must be OFF but the live slate reads ON
       (AILIBI_REPORTER_REASONING); corroboration_discipline must be OFF but the live slate
       reads ON (AILIBI_CORROBORATION_DISCIPLINE); testimony_shapes must be OFF but the live
       slate reads ON (AILIBI_TESTIMONY_SHAPES)
       Export exactly the levers you named and unset every other AILIBI_*
       lever export, then re-run. Nothing was staged.
```

**(b) the whole slate declared and none of it exported:**

```
Error: the live substrate-lever slate does not match --expect-levers.
       Expected ON: reporter_reasoning,corroboration_discipline,testimony_shapes
       Mismatch: reporter_reasoning must be ON but the live slate reads OFF
       (AILIBI_REPORTER_REASONING); corroboration_discipline must be ON but the live slate
       reads OFF (AILIBI_CORROBORATION_DISCIPLINE); testimony_shapes must be ON but the live
       slate reads OFF (AILIBI_TESTIMONY_SHAPES)
```

**(c) a HALF slate — ONE lever removed from the export.** This is the direction (b) cannot prove,
and it is the one the contract calls newly possible now that the slate is not bare:

```
Error: the live substrate-lever slate does not match --expect-levers.
       Expected ON: reporter_reasoning,corroboration_discipline,testimony_shapes
       Mismatch: corroboration_discipline must be ON but the live slate reads OFF
       (AILIBI_CORROBORATION_DISCIPLINE)
```

**(d) exported AND declared — the sanctioned preview**, which is the recorded configuration:

```
[dry-run] mode: seeds
[dry-run] seeds: 4,17,19,26,46
[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2
[dry-run] sample dir: /Users/danielkeinan/ailibi-smoke-21-23/9p2i
[dry-run] provider: featherless
[dry-run] meeting model: Qwen/Qwen3.6-27B
[dry-run] prompt set: qwen3_6_27b
[dry-run] substrate flags: expected levers ON = reporter_reasoning,corroboration_discipline,
          testimony_shapes; every other live toggle OFF; the graduated levers unconditional ON
[dry-run] seed workers: 2 parallel (each records one seed, then pulls the next available seed
          from the queue; Featherless: 2 units per 32B request → 4-unit cap)
[dry-run] seed crash-retry: up to 4 attempt(s) per seed on a transport/crash error
[dry-run] no API calls made; no files written.
Substrate slate OK: expected levers ON = reporter_reasoning,corroboration_discipline,
testimony_shapes; every other live toggle OFF; the graduated levers unconditional ON.
```

The real run's own preflight block, before any seed staged:

```
Using Featherless API key prefix: <redacted — the wrapper prints 8 characters; this record keeps none>
Locked substrate OK: AILIBI_PROMPT_SET=qwen3_6_27b.
Model-set coupling OK: qwen3_6_27b on Qwen/Qwen3.6-27B.
Model registry OK: Qwen/Qwen3.6-27B is registered in the production client.
Substrate slate OK: expected levers ON = reporter_reasoning,corroboration_discipline,
testimony_shapes; every other live toggle OFF; the graduated levers unconditional ON.
```

## 3. The seed slate, and the census it was drawn from

**The axis is A-47's stratification, and it is the DESIGN of the draw rather than a reference
cell.** A-47's verifier dissolved the emergency-meeting control and replaced it with a
stratification measured on baseline-7 bytes: report meetings WITH a `vent_sighting` eject the
reporter **0 times in 276**, while report meetings WITHOUT one eject the reporter **30 times in
342** and see the reporter drawing two or more accusers in **65.2%** of cases against **15.9%**.
**The reporter penalty exists only in the no-hard-evidence stratum**, so a slate drawn from
vent-flag meetings would exercise `reporter_reasoning` where the outcome it targets never occurs
and every cell would read green for a reason that has nothing to do with the lever. The re-record
publishes no comparable split, so this stratification is quoted as the axis's design and **the
stratum count is verified on the smoke's own recorded meetings in §5 rather than compared to
these numbers.**

**The census is a PROXY and is named as one.** It is drawn on OFF bytes while these seeds record
ON; the levers move trajectories, so the stratum is verified after the run and never assumed from
the draw (the 21.14 §3 precedent, in those words).

**The census, re-derived at this HEAD over the committed `replays/samples/9p2i`** (the script is
§17.1; meeting kind is read the way `eval/reporter_justice.py`:300-350 reads it — the meeting
opener's own APPLIED `report`/`emergency` action at that tick):

```
set=replays/samples/9p2i  seeds=50
  meetings: 151          body: 141          emergency: 10
  body_no_vent: 83       body_vent: 58
  ejections: 95          reporter_ejected: 7
  spoken saw_kill: 0
  ending:CREWMATE_EJECT: 35   ending:IMPOSTOR_PARITY: 15
```

Four of those cells are the pre-registration's own baseline-8 pins and reproduce exactly:
`samples/9p2i` body-report meetings **141/151** (§3.1, I-2), innocent-ejection denominator
**95** (I-1), reporter ejected per slot **7/141** (I-2). The census reader is therefore calibrated
against committed pins before it is trusted to draw a slate.

**The crew-witnessed-kill census** (§17.2), run through the same walk the counterfactual reader
uses, so nothing is re-implemented: **5 crew-witnessed kill observations across the 50 committed
seeds**, carried by **four** seeds — 17 (1), 19 (1), 26 (2), 46 (1). That is the shape
`testimony_shapes`'s elicitation half would speak, and A-22 counts 20 across 300 games (roughly one
per fifteen), so five seeds usually carry none. **All four seeds that carry one are drawn.**

**The drawn slate is 4, 17, 19, 26, 46**, verified per seed against the contract's coverage axes:

| seed | meetings | body | **no-vent body** | vent body | emerg | eject | **reporter ejected** | **witnessed kill** | ending |
|---|---|---|---|---|---|---|---|---|---|
| 4 | 4 | 4 | **4** | 0 | 0 | 2 | **1** | 0 | IMPOSTOR_PARITY |
| 17 | 4 | 4 | 3 | 1 | 0 | 2 | 0 | **1** | CREWMATE_EJECT |
| 19 | 5 | 4 | 3 | 1 | **1** | 3 | **1** | **1** | CREWMATE_EJECT |
| 26 | 4 | 4 | 3 | 1 | 0 | 2 | **1** | **2** | IMPOSTOR_PARITY |
| 46 | 4 | 4 | **4** | 0 | 0 | 2 | **1** | **1** | IMPOSTOR_PARITY |
| **slate** | **21** | **20** | **17** | **3** | **1** | **11** | **4** | **5** | CREW 2 / IMP 3 |

Why each axis is covered:

* **the no-vent-flag body-report stratum first** — 17 of the slate's 20 body reports sit in it, and
  two seeds (4, 46) are pure no-vent at 4/4. This is the only stratum in which the reporter penalty
  exists at all;
* **the outcome bars 3 and 4 gate** — four of the seven committed seeds carrying a baseline-8
  reporter conviction are drawn (4, 19, 26, 46 of 1/4/6/19/26/27/46);
* **the witnessed-kill half** — all four seeds carrying a crew-witnessed kill are drawn;
* **multi-meeting games** — every seed carries at least four meetings, so the ballot render is
  exercised repeatedly (110 committed ballots over these five seeds);
* **the INERT emergency control** — seed 19 carries one emergency meeting.
  `meetings/manager.py`:1981-1982 records that an emergency call arms neither the fold cap nor the
  threaded annotation, so a lever that changed an emergency meeting's prompts is a defect this
  slate catches for free.

## 4. The two ratified PRECONDITIONS, both DISCHARGED before the first seed

`audits/audit-phase-21-preregistration.md` §9.1 names two. Both are confirmed here, with the
evidence, before any seed staged.

### 4.1 Precondition (a) — the corpus recorder's hardcoded prompt-version map: FIXED

**The defect was measured, not assumed.** Under the declared slate the live registry resolves four
COMPOSITE strings, and the hardcoded constant named four bare v5 literals. Both readings, verbatim:

```
--- slate-resolved (three Wave-2 keys ON) — orchestrator.game.prompt_versions_for_set ---
accusation_round = accusation_round.qwen3_6_27b.v5.reporter_reasoning+accusation_round.qwen3_6_27b.v5.testimony_shapes
crewmate_report  = crewmate_report.qwen3_6_27b.v5.reporter_reasoning+crewmate_report.qwen3_6_27b.v5.testimony_shapes
impostor_report  = impostor_report.qwen3_6_27b.v5
vote_ballot      = vote_ballot.qwen3_6_27b.v5.corroboration_discipline+vote_ballot.qwen3_6_27b.v5.testimony_shapes

--- raw PROMPT_VERSION_SETS['qwen3_6_27b'] (what the constant named) ---
accusation_round = accusation_round.qwen3_6_27b.v5
crewmate_report  = crewmate_report.qwen3_6_27b.v5
impostor_report  = impostor_report.qwen3_6_27b.v5
vote_ballot      = vote_ballot.qwen3_6_27b.v5
```

**Which check sees the defect, and which does not.** `check_prompt_version_registry` compares
against the RAW `PROMPT_VERSION_SETS` map and therefore PASSES under any slate — it cannot see this
at all. The check that breaks a lever-ON record is `check_recorded_prompt_versions`, which compares
each MANIFEST row against the expected map and runs only on the FREEZE path, i.e. after roughly
22 hours of the record's spend.

**The fix**, confined to `scripts/record_ml_corpus.sh` (the ratified §9.1 fix only):

* the four v5 literals are kept as `REQUIRED_PROMPT_VERSIONS_BASE` — the owner-decision pin, whose
  value has not moved. `check_prompt_version_registry` still asserts the registry resolves to it, so
  a later registry bump still stops the recorder cold;
* `REQUIRED_PROMPT_VERSIONS` and `REQUIRED_PROMPT_VERSIONS_CLI` are DERIVED below the argument
  parse — `--expect-levers` is not known where the constant used to sit — through
  `orchestrator.game.prompt_versions_for_set`, with the declared lever keys turned into an
  environment by the committed `orchestrator.replay.env_var_for_lever`. A key that is not a live
  toggle is refused before anything stages;
* `check_prompt_version_registry` additionally re-derives the slate-resolved map in a fresh process
  and refuses if it has moved since startup, so a lever export that changed mid-run cannot record
  one substrate and freeze against another;
* `check_recorded_prompt_versions` and the two dry-run echoes read the derived map.

**Under the bare slate the derivation reproduces the committed literals byte-for-byte**, so nothing
about a bare-slate record changes:

```
[dry-run] prompt versions: the declared slate resolves to [accusation_round.qwen3_6_27b.v5,
crewmate_report.qwen3_6_27b.v5, impostor_report.qwen3_6_27b.v5, vote_ballot.qwen3_6_27b.v5]
(the registry's base map is asserted at preflight; rows off the resolved map are refused at freeze)
```

**Under the declared slate it resolves the composites** (`--set 4p1i --dry-run --expect-levers
reporter_reasoning,corroboration_discipline,testimony_shapes`, run under Shell A):

```
[dry-run] prompt versions: the declared slate resolves to
[accusation_round.qwen3_6_27b.v5.reporter_reasoning+accusation_round.qwen3_6_27b.v5.testimony_shapes,
 crewmate_report.qwen3_6_27b.v5.reporter_reasoning+crewmate_report.qwen3_6_27b.v5.testimony_shapes,
 impostor_report.qwen3_6_27b.v5,
 vote_ballot.qwen3_6_27b.v5.corroboration_discipline+vote_ballot.qwen3_6_27b.v5.testimony_shapes]
```

**And a typo is refused before anything stages** (`--expect-levers reporter_resoning`):

```
Error: --expect-levers names 'reporter_resoning', which is not a live substrate toggle
(live toggles: impostor_roll_call, reporter_reasoning, corroboration_discipline, testimony_shapes).
The prompt-version map a record freezes against is derived from the
declared slate, so an unrecognized key would silently freeze against
the wrong map; nothing was recorded.
```

**The fix is smoke-validated by a PLANTED case that bites, not by a recording leg.** No wrapper path
reaches the freeze check: the corpus dry-run exits before it, and a `--seeds` subset run skips the
finalize outright (`scripts/record_ml_corpus.sh`:1618-1626 — *"A `--seeds` run finalizes NOTHING,
even when every locked seed happens to be on disk"*). So
`tests/scripts/test_record_ml_corpus.py` drives the committed derivation and the committed
`check_recorded_prompt_versions` directly, against synthetic MANIFEST rows, in both directions:

| case | declared slate | planted MANIFEST row | expected | result |
|---|---|---|---|---|
| `test_freeze_accepts_the_rows_the_declared_slate_stamps` | bare | the four v5 literals | accept | exit 0 |
| `test_freeze_accepts_the_rows_the_declared_slate_stamps` | the three Wave-2 keys | the four composites | accept | exit 0 |
| `test_freeze_refuses_rows_recorded_under_another_slate` | the three Wave-2 keys | the four v5 literals — **the exact row the old constant made PASS** | refuse | exit ≠ 0, *"do not carry EXACTLY the slate-resolved prompt versions"* |
| `test_freeze_refuses_rows_recorded_under_another_slate` | bare | the four composites | refuse | exit ≠ 0 |

The third row is the planted case: before this fix the expected map WAS the bare literals, so a
lever-ON record's real rows were refused while that row passed. Both directions now bite.

**And the live record confirms it on its own bytes.** The smoke's MANIFEST row carries exactly the
composites the derivation produces:

```
| 19 | Qwen/Qwen3.6-27B | accusation_round.qwen3_6_27b.v5.reporter_reasoning+accusation_round.qwen3_6_27b.v5.testimony_shapes,
crewmate_report.qwen3_6_27b.v5.reporter_reasoning+crewmate_report.qwen3_6_27b.v5.testimony_shapes,
impostor_report.qwen3_6_27b.v5,
vote_ballot.qwen3_6_27b.v5.corroboration_discipline+vote_ballot.qwen3_6_27b.v5.testimony_shapes | … |
```

### 4.2 Precondition (b) — the tripwire reader taught to read a lever-ON recording: MERGED

PR #422 merged 2026-09-02 as `96b61318`, and PR #423 as `88bc8be7`. Both are ancestors of this
branch's base `14854a06`. The reader is
`uv run python scripts/counterfactual_phase21.py --recording "$SMOKE_DIR" --recorded-slate on --json`,
run under the SAME lever-ON shell the recording was made in, after the validity gate. It prints
every §8.1 predicate beside its reading and its verdict, names its stopped cells in
`payload["stopped_cells"]`, marks the pooled block as informational with
`payload["pooled_is_informational"]`, and **EXITS 1 on any STOP and 0 otherwise**.

## 5. The per-seed table, as recorded

The first seed was recorded ALONE and probed before the remaining four queued
(`audits/audit-phase-20-smoke.md` §13 note 3), then 4/17/26/46 ran on two workers.

| seed | wall (serial) | meetings | ejections | ending | winner | calls | tokens | cost |
|---|---|---|---|---|---|---|---|---|
| 19 | 419 s | 4 | 3 | CREWMATE_EJECT | CREWMATES | 46 | 239,246 | $0.0000 |
| 17 | 300 s | 2 | 2 | CREWMATE_EJECT | CREWMATES | 28 | 130,800 | $0.0000 |
| 4 | 384 s | 3 | 0 | IMPOSTOR_PARITY | IMPOSTORS | 36 | 185,120 | $0.0000 |
| 46 | 262 s | 2 | 1 | IMPOSTOR_PARITY | IMPOSTORS | 22 | 111,897 | $0.0000 |
| 26 | 448 s | 4 | 1 | IMPOSTOR_PARITY | IMPOSTORS | 44 | 228,201 | $0.0000 |
| **all** | **19m28s wall** | **15** | **7** | — | CREW 2 / IMP 3 | **176** | **895,264** | **$0.0000** |

Wall clock: seed 19 alone **7m00s** (recorded first, for the §6 probe), then 4/17/26/46 on two
workers in **12m28s**. Total operator wall **19m28s**.

### 5.1 Stratum coverage as OBSERVED, not assumed from the census

The DoD verifies the stratum on the smoke's own recorded meetings, because the census that drew the
slate is a proxy over OFF bytes:

```
seeds=5  meetings=15  body reports=14  emergency=1  ejections=7
body reports WITHOUT a vent_sighting: 12    WITH one: 2
reporter ejected: 0            spoken saw_kill observations: 2
endings: CREWMATE_EJECT 2, IMPOSTOR_PARITY 3
```

**12 of the 14 recorded body reports sit in the no-vent-flag stratum** — the only stratum in which
A-47's verifier found a reporter penalty at all. The slate is therefore **NOT vacuous for the
reporter lever**, and that is verified rather than assumed.

**The proxy moved, exactly as the contract warned.** Against the committed census the drawn seeds
predicted 21 meetings / 20 body reports / 17 no-vent / 11 ejections / 4 reporter convictions; the ON
run recorded 15 / 14 / 12 / 7 / 0. Seed 4 recorded 3 meetings and 0 ejections where the committed
bytes carry 4 and 2. Six behavioural repairs and three levers move trajectories; the census selects,
it does not predict.

**One axis is UNTESTED at this n and is named rather than discovered:** no recorded meeting produced
a task-completion ending, and the committed census carries none either, so that path is untested
here as it was at 21.14.

## 6. The gate

Run in Shell A, carrying the three Wave-2 exports: `eval/validity.py`'s
`cost_and_provenance_exact` derives its comparison snapshot from the gate process's own
environment, and `byte_identical_reconstruction` reaches `api/replay_loader.py`:655 through
`verify_samples`, so a bare shell would refuse rather than mis-measure.

### 6.1 `scripts/validity_gate.py` — all ten checks, named individually

```
uv run python scripts/validity_gate.py "$SMOKE_DIR" \
  --expected-model Qwen/Qwen3.6-27B --require-zero-cost
```

```
Validity gate over /Users/danielkeinan/ailibi-smoke-21-23/9p2i (5 games):
  [PASS] all_games_reach_game_over: 5/5 games reached a reconstructed game_over with a consistent win condition
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 15 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 15 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 88 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 310 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 88 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 5 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

The two the DoD quotes verbatim are the last two, above:
**`cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact
on 5 games`** and **`byte_identical_reconstruction: 0 samples drifted from byte-identical
reconstruction (want 0)`**.

### 6.2 `verify_samples.sh`, twice, in the same shell

```
$ bash scripts/verify_samples.sh "$SMOKE_DIR"     # run 1
All 5 samples verified clean.
$ bash scripts/verify_samples.sh "$SMOKE_DIR"     # run 2
All 5 samples verified clean.
```

### 6.3 The bare committed-set gate, in Shell B

Run in a shell with **no lever export at all**:

```
=== verifying replays/samples/4p1i/ ===   All 50 samples verified clean.
=== verifying replays/samples/9p2i/ ===   All 50 samples verified clean.
$ git status --porcelain replays/
(empty)
```

`scripts/counterfactual_phase21.py --sets all` also ran in that bare shell and exited 0, which is
the committed-record mode's contract. **The two shells refuse each other's bytes by design**, and
that refusal — not a wrong number — is what `api/replay_loader.py`:655 produces.

## 7. The recorded substrate stamp, read off the five `game_over` rows

Read from the recording, never from a live snapshot:

```
seeds with a game_over stamp: [4, 17, 19, 26, 46]
live SUBSTRATE_FLAG_KEYS: 25
distinct recorded stamps: 1   ->  keys: 25   ON: 24   OFF: ['impostor_roll_call']
substrate_stamp_mismatches(stamp)  ->  differing=[] unknown=[]   (each of the five)
retired_levers_stamped_off(stamp)  ->  []                        (each of the five)
substrate_slate_mismatches(['reporter_reasoning','corroboration_discipline','testimony_shapes']) -> []
```

**TWENTY-FIVE keys, twenty-four ON, `impostor_roll_call` the only False** — the twenty-one retired
levers all True and the three declared Wave-2 keys True, exactly as the DoD predicted. The two
comparisons are the two the contract names and neither is re-derived here:
`orchestrator.replay.substrate_stamp_mismatches` (a recorded stamp against the live substrate, what
`api/replay_loader.py` calls) is empty for each of the five, and
`orchestrator.replay.substrate_slate_mismatches` (the live slate against the declared one, what the
wrapper preflight calls) is empty in that same shell. **The wrapper's preflight and the recorded
stamps agree**; there was nothing to reconcile by hand.

**The MANIFEST `flags` cell lists 24 ON keys against the committed sets' 21, and is NOT
byte-identical to them.** That difference is the substrate self-describing correctly — the three
Wave-2 keys did not exist when the committed bytes were recorded — and is not a defect.

## 8. The lever-coverage table

Built from the recorded prompts, the recorded ballots and the recorded transcripts directly (§17.3),
and cross-read by the ON-recording instrument's own block-level cells (§15's command), so a marker
cannot be silently satisfied by an instrument looking elsewhere. **Every row is directional at this
n.** The reference column is the RATIFIED memos' baseline-8 value; a row with no ratified
counterpart says "no reference" rather than borrowing a baseline-7 figure.

### 8.1 `reporter_reasoning`

| cell | smoke (5 seeds) | ratified baseline-8 reference |
|---|---|---|
| body-report openings gaining the discovery-account block (`R-13`, block level) | **14/14 = 100%** | 620/620 (counterfactual §10.1) |
| — the same cell counted by byte diff (informational) | 14/14 = 100%, agrees | — |
| non-reporter speech turns in a body-report meeting gaining the base-rate block (`R-14`, block level) | **67/67 = 100%** | 2,715/2,715 |
| — the same cell counted by byte diff (informational) | 67/67 = 100%, agrees | — |
| emergency-meeting prompts gaining either block | **0** | 0 |
| ballots gaining a reporter block (`R-15`) | **0/88** | 0/3,631 |
| prompts carrying `<who_reported>` (direct byte read) | 67 of 73 speech, 14 of 15 openings | no reference |
| prompts carrying the `at_body` line (direct byte read) | 4 of 73 speech | no reference |
| lines the block adds, per opening | 44/15 = **2.93** | 1,964/672 = 2.92 (counterfactual §6.2) |
| lines the block adds, per changed speech turn | 380/71 = **5.35** | 15,051/2,879 = 5.23 |

The six speech prompts and one opening without `<who_reported>` are the emergency meeting's, which
has no reporter. **The reporter thread lands on every body report and nowhere else.**

### 8.2 `corroboration_discipline`

| cell | smoke (5 seeds) | ratified baseline-8 reference |
|---|---|---|
| ballots gaining the source-count block (`C-9`, block level) | **88/88 = 100%** | 3,614/3,631 = 99.5% |
| — the same cell counted by byte diff (informational) | 88/88 = 100%, agrees | — |
| ballots carrying `<testimony_sources>` (direct byte read) | 88/88 | no reference |
| ballots rendering a sole-source chain ("an answer to a charge, not a second witness") | 61/88 | no reference |
| ballots rendering the map's impossible-transit counter | 44/88 | no reference |
| accused subjects with NO first-hand source (`C-1`) | 13/35 = 37.1% | 475/1,525 = 31.1% |
| ejected subjects with NO first-hand source (`C-2`) | 1/7 = 14.3% `[ADV]` | 11/425 = 2.6% |
| ejections whose charge ANSWERED the ejectee's own (`C-3`) | 0/7 `[ADV]` | 33/429 |
| ejected subjects with a map-satisfied placement pair (`C-4`) | 0/7 `[ADV]` | 48/429 |
| **the ejecting-ballot citation mix** (`C-5`/`C-6`/`C-7`, over the 7 ballots that ejected the 2 innocents) | **hearsay 2 / own-observation 1 / own-turn 4 / other 0 / uncited 0** | 89 / 37 / 23 / 0 / 1 of 150 (counterfactual §4.3) |
| openings and speech turns gaining anything under this lever alone | **0** | 0 |
| lines the block adds, per ballot | 730/88 = **8.30** | 26,522/3,614 = 7.34 (Errata E.1) |

The citation mix is 7 ballots and is directional to the point of being anecdotal; it is reported
because the DoD names it, with its denominator beside it.

### 8.3 `testimony_shapes`

| cell | smoke (5 seeds) | ratified baseline-8 reference |
|---|---|---|
| CREW speech turns gaining the elicitation block (`T-9a`) | **49/49 = 100%** | 2,023 of 2,959 aggregate (§10.1 `T-9`) |
| IMPOSTOR speech turns gaining an elicitation block (`T-9b`) | **0/24** | 0 |
| openings gaining an elicitation block (direct byte read) | 15/15 | 672/672 (§5.6) |
| `whereabouts` statements surviving the reduction | **81** (OFF: 0) | 0 → 3,157 (§5.2) |
| `saw_move` statements surviving the reduction | **41** (OFF: 0) | 0 → 1,606 |
| `saw_kill` statements surviving the reduction | **2** (OFF: 0) | 0 → 0 (`T-4`, `[ADV]`) |
| episodic rows the ingest writes at recorded boundaries (`T-5`) | 1,935 ON against 1,280 OFF | 73,218 against 49,667 |
| location accounts reaching the alibi map (`T-6`) | **102/102 = 100%** ON, 21/102 = 20.6% OFF | 4,173/4,173 ON, 1,016/4,173 = 24.35% OFF |
| spoken vent accounts naming a player who never vented (`T-7`) | **0/3** `[ADV]` | 0/512 |

**The witnessed-kill half is EXERCISED, not untested.** The census (§3) found four committed seeds
carrying a crew-witnessed kill and all four were drawn; on the smoke's own bytes the walk finds
**3 crew-witnessed kill observations across seeds 19 (1) and 26 (2)**, and **two of them were
SPOKEN as structured `saw_kill` observations**. A-22's 20-in-300-games rate is quoted here as the
reason the half is usually untestable at five seeds, not as an excuse: it was testable because the
slate was drawn for it.

### 8.4 The first spoken `saw_kill`, and its two registered consequences

**Baseline 8 holds zero spoken `saw_kill` anywhere** (`grep -rn saw_kill replays/` returns nothing),
so the `saw_kill` path had zero committed exposure and these are the first bytes in the project that
could carry one. **They do.** Seed 19, meeting 3, turn 0:

```json
{"room": "ENGINEERING", "subject": "p-9", "tick": 16, "type": "saw_kill"}
```

spoken as *"I walked into Engineering at tick 16 and found p-7's body. I saw p-9 kill him right
there."* Two spoken `saw_kill` observations were filed in total (seeds 19 and 26).

The DoD requires the two REGISTERED consequences be named rather than filed as drift, and both are
observed:

1. **The role-blind PUBLIC-TRANSCRIPT row reaches every later speaker, impostors included.** The
   direct byte read finds the row `(spoken account, nothing confirms it)` in **10 of 73 speech
   prompts and 12 of 88 ballots**. This is CORRECT — it is the one table every seat reads, it is
   pinned by `tests/agents/test_bespoke_prompt_sets.py::test_a_spoken_kill_reaches_every_later_speaker`,
   and §8.1 EXCLUDES it from T5 by construction. T5's impostor half reads 0/24 with those rows
   present, which is the reader doing exactly what the ratified note says it must.
2. **The joint-slate ballot moves by more than the two arms alone.** The leave-one-out leg that
   withdraws `testimony_shapes` while `corroboration_discipline` stays ON moves **12 of 88 ballots,
   by −12 lines and −1,026 bytes**. On the committed baseline-8 bytes that same leg moves the ballot
   by **exactly zero** (Errata E.1: *"on the recorded bytes the ballot's added bytes are identical on
   the `corroboration_discipline`, `two-ON` and `all-three-ON` legs"*). **The interaction E.1
   re-registered has now fired on live bytes for the first time**, which E.1 itself predicts in as
   many words: *"the FIRST spoken kill at 21.23 or 21.24 will move the joint ballot by more than the
   two arms alone, which is expected and is not unregistered drift."** This report does not
   decompose that delta between the public-transcript row and the adopted-clause fork, and does not
   re-price E.1's per-row arithmetic — that is pinned on a synthetic kill meeting by
   `tests/meetings/test_corroboration.py::TestAdoptedClauseWording`.

### 8.5 The slate's own render prediction

Counterfactual §8.4 predicts added prose is additive in LINES on every seam and that the only
cross-lever interaction is the ballot's. On the smoke's leave-one-out legs the opening reads
14 + 30 = 44 lines against the whole slate's 44 (additive to the line), the speech turn reads
272 + 108 = 380 against 380 (additive to the line), and **the ballot reads 718 + 12 = 730 against
730 — additive in lines, with the 12-line testimony term existing only because a kill was spoken.**

## 9. The three watch cells

The register's verifiers ruled against the obvious reading of each, so each is a watch item rather
than a pass/fail row. **All three are directional at this n and none is a criterion.**

### 9.1 Agreement with the opener must NOT be flattened (A-19)

A-19's verifier WITHDREW the advice to down-weight agreement with the opener: same-target turn ≥ 2
crew accusations hit 79.2% (n=48) and 88.5% (n=122) against different-target 4.7% (n=106) and 3.1%
(n=287). **A lever that flattens that is a regression to report, not a success.** No committed
reader emits this split — it is §5.1's measured-but-not-registered class — so it is computed here as
a session walk (§17 names the reader), on the smoke bytes and on the SAME five committed seeds with
the same code:

| cell | committed same-five (OFF) | **smoke (ON)** |
|---|---|---|
| turn-0 CREW accusations, accuracy | 14/21 = 66.7% | **11/15 = 73.3%** |
| turn ≥ 2 CREW accusations, SAME target as turn 0 | 22/22 = 100.0% | **17/19 = 89.5%** |
| turn ≥ 2 CREW accusations, DIFFERENT target | 2/24 = 8.3% | **2/21 = 9.5%** |

**Agreement with the opener is NOT flattened**: the same-target/different-target separation stays
enormous (89.5% against 9.5%), and both columns reproduce the shape A-19's verifier measured. The
same-target cell falls from 100% to 89.5% on 19 cases — two convictions — which one game moves; it
is reported, and it is not a regression this n can establish.

### 9.2 The co-discoverer hazard (A-38), and who actually received framing

A-38's proposed widening was REJECTED because **71 of 145 = 49.0% of the non-reporter co-discoverer
slots are IMPOSTORS at baseline 8** (counterfactual §1.4, §3.4, row `R-12`). The DoD asks for the
impostor share of every co-discoverer who received exculpatory framing.

**Measured, and the answer has two halves.** First, the shipped block frames only the REPORTER, so
**no co-discoverer receives exculpatory framing at all** — A-38's widening did not land, which is
the ratified outcome. Second, the one per-speaker line the block does render to a non-reporter is
the neutral self-addressed `at_body` sentence, and that is the seam the widening would have used:

| cell | smoke (5 seeds) | ratified baseline-8 reference |
|---|---|---|
| body-report meetings carrying a non-reporter co-discoverer (`R-11`) | 3/14 | 118/620 |
| co-discoverer slots, CREW / IMPOSTOR (`R-12`) | 2 / 2 = **50.0% impostor** | 71/145 = **49.0% impostor** |
| prompts that received the `at_body` line | 4 | no reference |
| — of those, the speaker was an IMPOSTOR | **2 of 4 = 50.0%** | no reference |

**The hazard the counterfactual measured reproduces on the smoke's own bytes to within a point**,
at a denominator of four. It is a WATCH item: no §9.2 criterion names this class, and this report
invents none.

### 9.3 The confession net (A-16) — nothing to publish, and why

A-16's verifier requires any published confession cell to carry its precision beside its count. On
the smoke bytes the disambiguated pair #416 shipped reads **`model_self_disclosure_visible_turns` 0
and `crew_self_disclosure_control_turns` 0**, with `player_visible_leak_turns` **0 of 88 turns**.
There is no cell to publish, so none is published; the register's "10 fires, 20% precision" is a
baseline-7 figure over a pre-disambiguation net and is not quoted as a cell here (counterfactual
§5.5).

## 10. The honesty and solvability cells

Run under the recorded slate, after the gate, over the whole set — and beside a LIKE-FOR-LIKE OFF
column re-derived at `$0` from the SAME five committed seeds. **Every row is directional at this n.**

| cell | committed same-five (OFF) | **smoke (ON)** |
|---|---|---|
| I-2 false crew self-placement | 0/80 | **0/68** |
| — copyable from a rendered self-location line | 5/80 = 6.25% | **6/68 = 8.82%** |
| I-3 sole-flag precision | 0/0 (no sole-flag meeting) | **0/0** |
| I-4 grounded sighting side | 0/0 | **0/0** |
| I-5 fabricated completion lines | 0/34 | **0/25** |
| I-6 adjacent-room STRONG share | 0/0 | **0/0** |
| I-7 movement-origin flags | 0/2 | **1/1** `[ADV]` (move-backed 1, memory-truthful 1) |
| I-8 marker contamination (turns / prompts) | 0/110, 0/221 | **0/88, 0/176** |
| I-9 singular-persona prompts | 0/221 | **0/176** |
| I-10 meetings with a venting participant | 2/21 | **2/15** |
| I-11 free zero-witness kills declined | 0/28 | **1/24** (fellow-defer 1) |
| — ghost-top decisions mismatched | 0/249 | **0/209** |
| render budget, mean rendered lines/snapshot | 40.52 over 221 | **38.09 over 176** |
| render budget, testimony rows (≤4 / 5-6 / ≥7) | 4,181 (2,090 / 1,859 / 232) | **3,748 (1,082 / 2,182 / 484)** |
| I-5 containment: killer in candidate set | 19/20 = 0.95 | **13/14 = 0.9286** |
| — one candidate, and it is the killer | 6/20; 6/6 | **3/14; 3/3** |
| — ejected an already-cleared player | 3/10 = 0.30 | **0/6 = 0.00** |

`measure_baseline.py --honesty` exited 0 on the FIRST completed seed alone (seed 19, 4 meetings —
**not vacuous**) and again over the whole set; `--solvability` exited 0. **Neither raised.**

### 10.1 The secondary cells §5 registers, observed and never gated

| cell | committed same-five (OFF) | **smoke (ON)** | ratified baseline-8 reference |
|---|---|---|---|
| win split | CREW 2 / IMP 3 (impostor 60%) | **CREW 2 / IMP 3 (impostor 60%)** | `samples/9p2i` 15/50 = 30% |
| decisiveness (body-report ejections / body-report meetings) | 10/20 = 50.0% | **6/14 = 42.9%** | 377/620 = 60.8% |
| bar 1's cell split by a spoken kill (`P-1k`) | 0 of 7 | **1/4 = 25.0%** `[ADV]` | 0 of 96 |
| — of those, convicted an IMPOSTOR (`P-1ka`) | 0/0 `[ADV]` | **1/1 = 100%** `[ADV]` | 0/0 `[ADV]` |
| I-6 zero-flag convictions | not re-derived | **4/7**, 2 CREW / 2 IMPOSTOR | 86/429, 37 CREW |

The win split is 5 games against a ±15-point band written for a 50-game leg; it is printed because
§5 registers it and it decides nothing. **`P-1k` is non-empty for the first time**: one of the four
non-direct convictions named an ejectee a spoken `saw_kill` identified, and that conviction was
correct. Baseline 8 reads 0 of 96 because nothing could speak one.

## 11. The Wave-1 no-regression check, and the watch item scanned by hand

### 11.1 No Wave-1 repair regressed under the levers

The 21.14 marker pass, run unchanged (§17 quotes its two censuses; the marker pass itself is
`audits/audit-phase-21-smoke.md` §7.3), against the smoke bytes and the same five committed seeds:

| # | repair | marker | committed same-five | **smoke (ON)** | reading |
|---|---|---|---|---|---|
| 1 | A-6 (21.1) | the taught oracle line inside a rendered proof block | 0 of 221 prompts; 46 `Proof.` blocks; banned vocabulary absent | **0 of 176 prompts; 41 `Proof.` blocks; banned vocabulary absent** | **NO REGRESSION** |
| 1b | A-6, spoken | the oracle net over `free_text`, rationales and claim reasons | 0 hits / 351 utterances (FLOOR net fires 109) | **0 hits / 294 utterances (FLOOR net fires 89)** | **NO REGRESSION** — the over-broad floor demonstrably reaches these surfaces |
| 2 | A-17 (21.2) | structured testimony rows in the vote-ballot prompts | 110/110 carry `saw:`/`claims:`/`said:` | **88/88 carry all three**, over 546 rendered turn heads | **NO REGRESSION** |
| 3 | A-14 (21.3) | every recorded action row carries an explicit disposition | 184/184 tick rows | **133/133 tick rows**; 58 of 844 = 6.9% `discarded_by_meeting` over 15 trigger ticks | **NO REGRESSION** |
| 4 | A-3 (21.3) | redirected ballots carry machine-readable provenance | 110 ballots, 0 missing provenance | **88 ballots, 6 machine rows (`under_gate_redirect` 5, `teammate_coerced` 1), 0 missing** | **NO REGRESSION** |
| 5 | B-8 (21.4) | the belief line's last-seen agrees with the agent's own sightings | 0/650 stale | **0/476 stale, 0 stale-and-wrong-room** | **NO REGRESSION** |
| 6 | A-31 (21.5) | exactly one memory row per witnessed vent | 20 witnessed, 0 heard, 0 double | **14 witnessed, 0 heard, 0 double**, 4 distinct, 0 heard-only | **NO REGRESSION** |

### 11.2 The watch item, scanned by hand and not delegated to the gate

The validity gate has no `deadline_default` check at all. Scanned directly over the recorded bytes:

```
failed_call rows by error_type: {} (none recorded)
deadline_default rows (EITHER shape): 0
```

**No recorded `failed_call` row of any kind exists in the five seeds**, so the question of
`error_type == "deadline_default"` is answered under both shapes at once, and the
`"(deadline_default)"` model sentinel is likewise absent from every row. The freeze guard
`check_replay_provenance` refused two seeds for exactly this at the baseline-7 record; nothing here
would trip it.

The recorder's own summary counters, from the whole-set eval-report rebuild:

```
lost_openings 0 (defaults 0) | vote_defaults 0 (must_vote 0) | ballot_redirects 5 (eject 5)
missed_skip 9 | meeting_rate 1.00 (15 meetings) | ejection_accuracy 0.7143 (5/7)
```

**Zero lost openings, zero defaults, zero vote defaults.**

## 12. Operating data, and the re-priced projection

Measured, not inherited.

```
15 meetings | 176 LLM calls | 856,878 input + 38,386 output = 895,264 tokens | $0.0000
tokens/call    5,086.7
calls/meeting     11.73
tokens/meeting 59,684.3
per-seed serial wall: 419, 300, 384, 262, 448 s  (mean 362.6, min 262, max 448)
total operator wall: 19m28s  (7m00s serial first seed + 12m28s on two workers)
```

**Worker occupancy:** the parallel leg did 1,394 s of serial seed work across 748 s of wall on two
workers = **93.2%**; the idle 6.8% is the tail after seed 46 finished while seed 26 ran on. The
first leg was one seed by design, so its capacity figure is not comparable and is not averaged in.

**Retries, transport blips, worker diagnostics: none.** Both run logs were scanned for `WARN`,
`ERROR`, `Traceback`, retry, lock, dead-owner and claim diagnostics — the only matches were the
substring `lock` inside `Locked substrate OK`. **No seed consumed a second attempt of its budget.**

### 12.1 The inflation, measured like-for-like

The 21.14 §11 method, re-run rather than inherited. The PRIMARY denominator is the SAME five
committed seeds; the re-derived all-games mean is its CROSS-CHECK. **Both are published.**

| denominator | meetings | tokens | tokens/meeting | ratio against the smoke |
|---|---|---|---|---|
| **the SAME FIVE committed seeds** (the like-for-like, and the primary) | 21 | 1,041,851 | **49,612.0** | **×1.2030 (+20.3%)** |
| both committed 9p2i legs, 200 games (the cross-check, re-derived from the bytes) | 590 | 31,939,656 | 54,135.0 | ×1.1025 (+10.3%) |
| the smoke | 15 | 895,264 | 59,684.3 | — |

**The two denominators DISAGREE by 8.4% on the OFF side, where 21.14's agreed to 0.1%, and that
disagreement is the finding this check exists to produce.** The drawn five are token-LIGHTER per
meeting than the set average (49,612.0 against 54,135.0), because this slate was drawn for lever
coverage — the no-vent-flag stratum, the reporter-conviction seeds and every witnessed-kill seed —
rather than for typicality. **The five drawn seeds are therefore NOT a representative sample on
tokens-per-meeting, and the like-for-like ratio is an upper bound on the inflation the record will
see.** The all-games cross-check is carried as the projection's low end for exactly that reason.

The per-meeting increase splits, against the same five committed seeds:

| | same-five committed | smoke | factor |
|---|---|---|---|
| calls per meeting | 10.52 | 11.73 | **×1.1149 (+11.5%)** |
| tokens per call | 4,714.3 | 5,086.7 | **×1.0790 (+7.9%)** |
| **tokens per meeting** | **49,612.0** | **59,684.3** | **×1.2030 (+20.3%)** |

and the two factors multiply to the third exactly (1.1149 × 1.0790 = 1.2030). **So roughly
two-fifths of the per-meeting increase is larger prompts and roughly three-fifths is a higher call
rate.** The prompt-size term is the Wave-2 blocks paying their way, measured; the call-rate term is
a trajectory effect at n = 15 meetings, not a render fact, and 10.52 → 11.73 is well inside what
five seeds can wander.

### 12.2 The four-leg projection, re-derived

Method, stated so 21.24 re-runs it rather than inherits it: the re-record's MEASURED per-leg actuals
(`audits/audit-phase-21-rerecord.md` §2 — 3h07m00s / 7h59m32s / 23m15s / 24m41s-incomplete, total
11h54m28s over 299 of 300 games) are scaled to a full 300 games by pricing leg 4's 49 recorded games
up to 50 (×50/49), giving **11h54m58s**, and that baseline is scaled by this smoke's measured
tokens-per-meeting ratio. The bracket's low end is the all-games cross-check ratio; its centre is
the like-for-like ratio, which the ratified reading rule makes primary; its high end is the
like-for-like ratio multiplied by a latency allowance taken from this run's own measured per-seed
spread (slowest 448 s over the mean 362.6 s = ×1.2355), because with `$0` flat-rate billing the wall
is dominated by hosted-provider latency, which five seeds measure coarsely.

| | scaling factor | **four-leg total** |
|---|---|---|
| low (all-games cross-check ratio) | ×1.1025 | **13h08m16s** |
| **centre (like-for-like ratio, primary)** | **×1.2030** | **14h20m08s** |
| high (like-for-like × the latency allowance) | ×1.4864 | **17h42m42s** |

**The bracket is 13h08m – 17h43m, centred at 14h20m**, against the re-record's realized 11h54m28s
for 299 games and the phase-20 record's 23h25m42s for 300. **The Wave-2 levers add rendered prompt
bytes, and this ratio is the single number that decides whether the next record fits its window: at
the centre it does, with roughly nine hours of margin against the phase-20 wall.**

## 13. What this smoke does NOT cover

Named rather than left to be discovered.

1. **One wrapper, one roster.** The smoke drives `scripts/refresh_samples.sh` on 9p2i only. Legs 2
   and 4 of the record (`samples/4p1i`, `ml_corpus/4p1i`) are exercised here only through their
   dry-run preflights (§4.1) and through the hermetic recorder coverage Task 21.10 shipped.
2. **The corpus recorder's freeze path is exercised by a PLANTED case, not by a recording leg.** Its
   per-set seed ranges are fixed (`scripts/record_ml_corpus.sh`:227-237) and its `--seeds` slice
   (:204-212) finalizes nothing (:1618-1626), so no wrapper path reaches `check_recorded_prompt_versions`
   or the freeze-path `check_replay_provenance`. §4.1's four-case table is the coverage those two
   checks have here.
3. **The 4p1i roster is not live-smoked**, and its contribution to §12.2's projection is an inference
   from the re-record's measured legs, labelled one there.
4. **A task-completion ending is UNTESTED** (§5.1), as it was at 21.14.
5. **The dead-owner streak back-port is proven by its own tests, not by this run.** `bash --version`
   on this machine is GNU bash 3.2.57(1) (macOS's stock shell), which predates `$BASHPID`, so
   dead-owner detection degrades to a documented no-op (`scripts/refresh_samples.sh`:768-776). The
   mkdir mutex and its release still serialize correctly, and no MANIFEST row was lost across two
   concurrent writers.
6. **No measurement.** Five seeds, 15 meetings, 7 ejections. Every cell above says so where it
   appears, and **no pre-registered bar is declared met or missed on five seeds.**

## 14. The criteria, quoted VERBATIM and read one by one

`audits/audit-phase-21-preregistration.md` §9.2 is the abandon-criteria section and is quoted in
full. **The counterfactual publishes no abandon-criteria section of its own**: its §9 tripwire
CANDIDATES were dispositioned into the pre-registration's §8.1, which is where they are read, and
its §11.1 refusals are properties of the instrument rather than criteria for a run.

| § 9.2 criterion, verbatim | reading on this run | verdict |
|---|---|---|
| "a `scripts/validity_gate.py` FAIL on any leg" | one leg, all ten checks PASS (§6.1) | **NOT MET** |
| "a seed whose opening defaults (the `(deadline_default)` watch item)" | 0 lost openings, 0 defaults, 0 `failed_call` rows of any kind, 0 `(deadline_default)` sentinels under either shape (§11.2) | **NOT MET** |
| "a guard trip" | no guard fired: the wrapper's four preflights passed on the sanctioned slate and refused every deviation, `check_replay_provenance` was not reached by this wrapper, and the ON-recording reader's four refusals (counterfactual §11.1) all passed | **NOT MET** |
| "a lever-stamp mismatch between the recorded snapshot and the declared slate, compared through `orchestrator.replay.substrate_slate_mismatches` and **never re-derived**" | `substrate_slate_mismatches(['reporter_reasoning','corroboration_discipline','testimony_shapes'])` → `[]`, and `substrate_stamp_mismatches` empty on each of the five recorded stamps (§7) | **NOT MET** |
| "any of the seven §8.1 tripwires failing **its predicate** — the sample-local criterion in §8.1's third column, evaluated over whatever the run actually recorded. A denominator smaller than baseline 8's is expected at the smoke and is NOT a trip." | all seven PASS (§15); the reader exits 0 and `payload["stopped_cells"]` is empty | **NOT MET** |

**Classes this run observed that no criterion names.** Three, recorded in the memo's own words
rather than stretched to fit: the `at_body` line's 50% impostor share (§9.2), the first spoken
`saw_kill` and its ballot interaction (§8.4), and the like-for-like/all-games denominator
disagreement (§12.1). **No §9.2 criterion names any of these classes verbatim, and this report
invents none.**

**And the standing canon, stated where the report needs it:** baseline 7 is canon by explicit owner
override of a FINDING verdict, with bar 1 missed at 61/103 = 0.5922 against ≥ 0.60 and bar 2 missed
at 42 against < 35. No surface in this report states or implies that those bars passed.

## 15. The seven tripwires, each against its own SAMPLE-LOCAL predicate

Reader, run under the SAME lever-ON shell the recording was made in, after the validity gate:

```bash
uv run python scripts/counterfactual_phase21.py \
  --recording "$SMOKE_DIR" --recorded-slate on --json
```

It exited **0**, `payload["stopped_cells"]` is **empty**, `payload["pooled_is_informational"]` is
**true** (the pooled block is not the verdict — the verdict is the union over recordings), and the
table ends with **`verdict: every GATED predicate PASSES on these bytes`**.

| tripwire | cell | the ratified SAMPLE-LOCAL predicate | reading on these bytes | verdict |
|---|---|---|---|---|
| **T1** (never-worse bar + STOP) | `T-7` | the count is 0, whatever the denominator | **0/3 = 0.0000** `[ADV]` | **PASS** |
| **T2** (STOP) | `R-13` | every observed body-report opening gains the block — 100% of the observed denominator | **14/14 = 1.0000**; emergency openings that gained one = 0; byte-diff column 14/14, agrees | **PASS** |
| **T2** (STOP) | `R-14` | every observed non-reporter speech turn in a body-report meeting gains it — 100%, and no emergency-meeting prompt gains either | **67/67 = 1.0000**; emergency speech prompts that gained one = 0; byte-diff column 67/67, agrees | **PASS** |
| **T3** (STOP) | `R-15` | the count is 0, whatever the ballot denominator | **0/88 = 0.0000** | **PASS** |
| **T4** (STOP) | `T-6` | 100% of observed location accounts reach the map under ON (and the OFF reconstruction of the same run is strictly below it) | **102/102 = 1.0000** ON against **21/102 = 0.2059** OFF — strictly below, so the ordering clause bites rather than passing on the equality the owner ruled permissible | **PASS** |
| **T5** (never-worse bar + STOP) | `T-9a` | every observed CREW speech turn gains the ELICITATION block | **49/49 = 1.0000** | **PASS** |
| **T5** (never-worse bar + STOP) | `T-9b` | the count of IMPOSTOR speech prompts gaining an ELICITATION block is 0 | **0/24 = 0.0000**, with the role-blind public-transcript row present in impostor prompts and correctly EXCLUDED by construction (§8.4) | **PASS** |
| **T6** (STOP) | `C-9` | the observed share is ≥ 99% of ballots | **88/88 = 1.0000**; byte-diff column 88/88, agrees | **PASS** |
| **T7** (STOP) | `B-1m1` | the meeting-1 row count is identical between the run's own OFF and ON columns | **1412/72 = 19.6111 in both columns** | **PASS** |

**The population column binds neither run.** Every denominator here is smaller than baseline 8's —
14 openings against 620, 67 speech turns against 2,715, 88 ballots against 3,631, 102 location
accounts against 4,173 — and §8.1 ratifies that as expected and **NOT a trip**. Each row is judged
on its predicate; the baseline-8 figure appears in §8's tables as a reference and nowhere as a
criterion. **No tripwire is a graduating bar and none contributes to any verdict but this smoke's.**

## 16. The verdict, the bytes, and what happens next

**GO.** Ruled against `audits/audit-phase-21-preregistration.md` §9.2: **no abandon criterion is
met** (§14), all seven §8.1 tripwires PASS against their sample-local predicates (§15), the validity
gate PASSED on all ten checks with both reconstructions byte-identical (§6), the recorded substrate
stamp is the declared slate on all five seeds by both registered comparisons (§7), no Wave-1 repair
regressed (§11.1), and the committed record is untouched (§6.3).

**The adopting record's window opens on `14854a06`**, this report's certified source state, and the
freeze governs from the pre-registration's own merge point. Any merge into `agents/`, `meetings/`,
`observation/`, `orchestrator/` or `agents/strategic/prompts/` between this report and the record
reopens it.

**The bytes are PRESERVED, not deleted:**

```
/Users/danielkeinan/ailibi-smoke-21-23/9p2i     6,305,418 bytes over 8 files
```

so a routed repair can be re-measured on the same bytes at `$0` without re-recording a seed. The
like-for-like OFF reference this report reads against is preserved beside them at
`/Users/danielkeinan/ailibi-smoke-21-23/committed-same-five` (five copies of committed replays,
read-only; nothing under `replays/` moved).

**Three items the record inherits**, none of them a STOP and none of them blocking:

1. **The first spoken `saw_kill` and its ballot interaction** (§8.4). The record will meet both at
   scale. Both are registered — the public-transcript row by `test_a_spoken_kill_reaches_every_later_speaker`
   and the ballot fork by Errata E.1 — and 21.24's audit should report the interaction's realized
   size rather than E.1's synthetic per-row arithmetic.
2. **The seed slate is not a representative token sample** (§12.1). The projection's low end is the
   all-games cross-check for that reason, and the record should re-derive its own ratio per leg.
3. **The `at_body` line reached an impostor in 2 of 4 firings** (§9.2), reproducing the
   counterfactual's 49.0% co-discoverer hazard at n = 4. It is observed and gated by nothing.

## 17. Appendix — the readers this report ran, in full

Each is stdlib-only or imports only committed repo surfaces, so an owner or a later re-measure
reproduces both columns from the preserved smoke bytes and the committed record alone, at `$0`.

### 17.1 The per-seed census that drew the slate

Run as `AILIBI_CENSUS_DIR=<set> uv run python census.py`, from the repo root.

```python
"""Per-seed census of a 9p2i replay set, stratified the way A-47's verifier ruled.

The reporter penalty exists only in the no-vent-flag body-report stratum, so a
smoke slate must cover it. Meeting kind is read the way eval/reporter_justice.py
reads it: the meeting opener's own APPLIED report/emergency action at that tick.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ.get("AILIBI_REPO_ROOT", os.getcwd()))
SET_DIR = Path(
    os.environ.get("AILIBI_CENSUS_DIR", str(ROOT / "replays" / "samples" / "9p2i"))
)

_KINDS = {"report": "body_report", "emergency": "emergency"}


def entries(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def meeting_kind(rows: list[dict], meeting: dict) -> str:
    for row in rows:
        if row.get("kind") != "tick" or row.get("tick") != meeting.get("tick"):
            continue
        dispositions = row.get("action_dispositions")
        for index, action in enumerate(row.get("actions") or []):
            kind = _KINDS.get(str(action.get("type")))
            if kind is None or action.get("actor") != meeting.get("triggered_by"):
                continue
            if dispositions is not None and dispositions[index] != "applied":
                continue
            return kind
    return "unknown"


def main() -> int:
    totals: Counter[str] = Counter()
    per_seed: dict[int, dict] = {}
    for path in sorted(SET_DIR.glob("replay-seed-*.jsonl")):
        seed = int(path.stem.rsplit("-", 1)[1])
        rows = entries(path)
        info: dict = {
            "meetings": 0, "body": 0, "body_no_vent": 0, "body_vent": 0,
            "emergency": 0, "ejections": 0, "reporter_ejected": 0,
            "saw_kill": 0, "ending": None, "winner": None,
        }
        for row in rows:
            if row.get("kind") == "game_over":
                info["ending"] = row.get("end_reason") or row.get("reason")
                info["winner"] = row.get("winner")
            if row.get("kind") != "meeting":
                continue
            info["meetings"] += 1
            kind = meeting_kind(rows, row)
            blob = json.dumps(row)
            has_vent = "vent_sighting" in blob
            info["saw_kill"] += blob.count('"saw_kill"')
            if kind == "body_report":
                info["body"] += 1
                if has_vent:
                    info["body_vent"] += 1
                else:
                    info["body_no_vent"] += 1
            else:
                info["emergency"] += 1
            ejected = row.get("ejected_player_id")
            if ejected:
                info["ejections"] += 1
                if kind == "body_report" and ejected == row.get("triggered_by"):
                    info["reporter_ejected"] += 1
        per_seed[seed] = info
        for key in (
            "meetings", "body", "body_no_vent", "body_vent", "emergency",
            "ejections", "reporter_ejected", "saw_kill",
        ):
            totals[key] += info[key]
        totals[f"ending:{info['ending']}"] += 1

    print(f"set={SET_DIR}  seeds={len(per_seed)}")
    for key in sorted(totals):
        print(f"  {key}: {totals[key]}")
    print()
    print("seed meetings body no_vent vent emerg eject rep_eject saw_kill ending")
    for seed, info in sorted(per_seed.items()):
        print(
            f"{seed:>4} {info['meetings']:>8} {info['body']:>4} "
            f"{info['body_no_vent']:>7} {info['body_vent']:>4} "
            f"{info['emergency']:>5} {info['ejections']:>5} "
            f"{info['reporter_ejected']:>9} {info['saw_kill']:>8} {info['ending']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 17.2 The crew-witnessed-kill census

Run the same way. It reuses the committed golden walk rather than re-implementing perception, so
the memories it reads are the memories the live agents held.

```python
"""Per-seed crew-witnessed-kill census over a committed replay set."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(os.environ.get("AILIBI_REPO_ROOT", os.getcwd()))
sys.path.insert(0, str(ROOT))

from engine.world import load_canonical_map  # noqa: E402
from tests.meetings.test_prompt_byte_golden import (  # noqa: E402
    _canonical_renderers,
    walk_replay_meetings,
)

SET_DIR = Path(
    os.environ.get("AILIBI_CENSUS_DIR", str(ROOT / "replays" / "samples" / "9p2i"))
)


def main() -> int:
    game_map = load_canonical_map()
    renderers = _canonical_renderers()
    per_seed: Counter[int] = Counter()
    for path in sorted(SET_DIR.glob("replay-seed-*.jsonl")):
        seed = int(path.stem.rsplit("-", 1)[1])
        seen: set[tuple[str, int, str]] = set()
        for meeting in walk_replay_meetings(
            path, game_map=game_map, renderers_for_set=renderers
        ):
            roles = {p.agent_id: p.role for p in meeting.participants}
            for player_id, memory in meeting.memories.items():
                for event in memory.episodic.recent(since_tick=0):
                    payload = event.payload or {}
                    action = payload.get("action") or payload.get("observed_action")
                    if isinstance(action, dict):
                        action = action.get("action")
                    if action != "kill":
                        continue
                    if roles.get(player_id) == "IMPOSTOR":
                        continue
                    seen.add(
                        (player_id, event.tick, json.dumps(payload, sort_keys=True))
                    )
        per_seed[seed] = len(seen)
    print(f"set={SET_DIR}")
    print(f"crew-witnessed kill observations, total: {sum(per_seed.values())}")
    print("seeds carrying one:", {s: n for s, n in sorted(per_seed.items()) if n})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 17.3 The lever-marker pass over the RECORDED prompts

Stdlib only; imports nothing from the repo. Every literal is copied out of the shipped
`qwen3_6_27b` templates. Run as `uv run python lever_markers.py <dir> [<dir> …]`.

```python
"""The lever-coverage read, straight off the RECORDED prompts — stdlib only."""

from __future__ import annotations

import collections
import json
import pathlib
import sys

BALLOT = "## How to decide"
OPENING = "## This meeting"
IMPOSTOR_OPENING = "## Your cover"
SPEECH = "## Your turn"

MARKERS = (
    ("reporter_block_speech", "<who_reported>"),
    ("reporter_block_opening", "You reported the body that opened this meeting"),
    ("reporter_at_body", "Your own record shows you saw the body when it was reported."),
    ("elicitation_kill_mandate", "If instead you watched a KILL happen"),
    ("elicitation_schema_row", '{"type": "saw_kill"'),
    ("public_kill_row", "(spoken account, nothing confirms it)"),
    ("transcript_whereabouts_row", "places THEMSELVES in"),
    ("transcript_saw_move_row", ", arriving in "),
    ("source_count_block", "<testimony_sources>"),
    ("sole_source_chain", "an answer to a charge, not a second witness"),
    ("map_transit_counter", "one door apart, so walking fits both"),
    ("ballot_exculpation_15_5", "## Who reported the body"),
)


def classify(prompt: str) -> str:
    if BALLOT in prompt:
        return "vote_ballot"
    if IMPOSTOR_OPENING in prompt:
        return "impostor_report"
    if OPENING in prompt:
        return "crewmate_report"
    if SPEECH in prompt:
        return "accusation_round"
    return "other"


def analyse(root: pathlib.Path) -> None:
    by_class: collections.Counter[str] = collections.Counter()
    hits: dict[str, collections.Counter[str]] = collections.defaultdict(
        collections.Counter
    )
    spoken = collections.Counter()
    for path in sorted(root.glob("replay-seed-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("kind") != "meeting":
                continue
            for turn in (row.get("transcript") or {}).get("turns") or []:
                for obs in turn.get("observations") or []:
                    spoken[str(obs.get("type"))] += 1
            for call in row.get("llm_calls") or []:
                prompt = call["prompt"]
                cls = classify(prompt)
                by_class[cls] += 1
                for name, marker in MARKERS:
                    if marker in prompt:
                        hits[cls][name] += 1
    print(f"\n{root}")
    print(f"  prompts by class: {dict(sorted(by_class.items()))}")
    for cls in sorted(by_class):
        print(f"  {cls} ({by_class[cls]}): {dict(sorted(hits[cls].items()))}")
    print(f"  spoken observation kinds: {dict(sorted(spoken.items()))}")


for arg in sys.argv[1:]:
    analyse(pathlib.Path(arg))
```

### 17.4 The operating-data reader

`AILIBI_OPDATA_DIR=<set> [AILIBI_OPDATA_SEEDS=a,b,c] uv run python opdata.py` — sums recorded
`llm_calls` tokens and cost per seed, and scans every recorded `failed_call` row for
`error_type == "deadline_default"` and for the `(deadline_default)` model sentinel, under both
shapes. It is the watch-item scan of §11 and the token source of §12.

### 17.5 The agreement-with-the-opener session walk (§9.1)

No committed reader emits this split — it is the pre-registration's §5.1
measured-but-not-registered class — so it is computed here and published, and the same code produces
both columns. Roles come from the committed `eval.validity.roles_by_seed` re-seeding, never from the
replay (roles are firewalled out of the JSONL).

```python
"""A-19's watch cell: agreement with the opener, as a session walk."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AILIBI_REPO_ROOT", os.getcwd()))
sys.path.insert(0, str(ROOT))

from eval.validity import resolve_roster_knobs, roles_by_seed  # noqa: E402

TARGET = Path(os.environ.get("AILIBI_WATCH_DIR", os.environ.get("SMOKE_DIR", ".")))
ONLY = {
    int(token)
    for token in os.environ.get("AILIBI_WATCH_SEEDS", "").split(",")
    if token.strip()
}


def accusations(turn: dict) -> list[str]:
    return [
        str(claim["against"])
        for claim in turn.get("claims") or []
        if claim.get("type") == "accusation" and claim.get("against")
    ]


def main() -> int:
    players, impostors, tasks = resolve_roster_knobs(TARGET)
    roles_all = roles_by_seed(
        TARGET,
        num_players=players,
        num_impostors=impostors,
        tasks_per_crewmate=tasks,
    )
    same, diff, opener = [0, 0], [0, 0], [0, 0]
    for path in sorted(TARGET.glob("replay-seed-*.jsonl")):
        seed = int(path.stem.rsplit("-", 1)[1])
        if ONLY and seed not in ONLY:
            continue
        roles = roles_all[seed]
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("kind") != "meeting":
                continue
            turns = (row.get("transcript") or {}).get("turns") or []
            if not turns:
                continue
            first = turns[0]
            first_targets = set(accusations(first))
            if roles.get(str(first.get("speaker"))) == "CREWMATE":
                for target in accusations(first):
                    opener[1] += 1
                    opener[0] += roles.get(target) == "IMPOSTOR"
            for turn in turns:
                if int(turn.get("turn_index", 0)) < 2:
                    continue
                if roles.get(str(turn.get("speaker"))) != "CREWMATE":
                    continue
                for target in accusations(turn):
                    bucket = same if target in first_targets else diff
                    bucket[1] += 1
                    bucket[0] += roles.get(target) == "IMPOSTOR"

    def rate(pair: list[int]) -> str:
        return f"{pair[0]}/{pair[1]}" + (
            f" = {pair[0] / pair[1]:.1%}" if pair[1] else " = n/a"
        )

    print(f"turn-0 CREW accusations, accuracy:          {rate(opener)}")
    print(f"turn>=2 CREW accusations, SAME target:      {rate(same)}")
    print(f"turn>=2 CREW accusations, DIFFERENT target: {rate(diff)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### 17.6 The `at_body` recipient read (§9.2)

The same roster/roles resolution, over every recorded prompt carrying
`Your own record shows you saw the body when it was reported.`, printing each recipient's recorded
role and the impostor share. It is the only cell in this report that reads a per-speaker line of the
reporter block against ground truth, and it is what makes §9.2's watch reading a measurement rather
than an inference.
