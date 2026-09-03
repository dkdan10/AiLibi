# Phase-21 Wave-2 smoke — the lever slate ON, live, ruled against the ratified memos (Task 21.23)

**Date:** 2026-09-02. **Task:** 21.23. **Branch:** `phase-21-smoke-wave2`, opened from
`origin/main` `14854a06`.

## 0. The verdict, in one line

**GO — with one watch item FIRED, reported rather than absorbed.** Five live seeds recorded at the
ratified Wave-2 slate; the validity gate PASSED on all ten checks; both reconstructions
byte-identical; **all seven §8.1 tripwires PASS against their own sample-local predicates**
(`verdict: every GATED predicate PASSES on these bytes`, the reader exiting 0 with `stopped_cells`
empty); **no `audits/audit-phase-21-preregistration.md` §9.2 abandon criterion met**, read one by
one in §14; and the committed record untouched.

**The watch item fired, and it is the headline the record must plan around.** One recorded
`failed_call` row on seed 26 carries `error_type == "deadline_default"` — the first this phase has
seen — and the corpus recorder's freeze guard is demonstrated refusing that seed (§11.2). §9.2's
criterion names **a seed whose OPENING defaults**, and no opening defaulted (`lost_openings 0`); the
defaulted turn is an `opt_in` speech turn, so the criterion as written is NOT met and this report
does not stretch it. The remedy is the one the recorder itself prescribes — re-record the seed — and
it has a precedent at the baseline-7 record. **The seed was NOT re-recorded to make this report
green**: a smoke that re-rolls until it is clean measures nothing. **The contract's own DoD item at
`tasks/phase-21.md`:6868 — "no recorded failed-call row carries `error_type == "deadline_default"`
under either shape" — is therefore NOT SATISFIED** (§14.1), the disagreement between that item and
the ratified §9.2 criterion is the owner's to settle at the gate, and both halves of it are ROUTED to
21.24 in §16, the first as a precondition.

**Three further things no previous bytes could show.** A crew speaker filed the project's **first
spoken `saw_kill`** (baseline 8 holds zero anywhere), and with it the **cross-lever ballot
interaction Errata E.1 re-registered FIRED for the first time on live bytes** — both registered
rather than drift (§8.4). And what the table then DID with those accounts, which no offline
instrument could reach: **both were true, both named a real impostor, neither convicted, and one
ended with the truthful crew witness ejected instead** (§8.5). Two cases decide nothing and no
criterion names them; they are the most decision-relevant thing these bytes contain for 21.24.

**Source state this report certifies:** `14854a06`. The freeze the ratified pre-registration
declares (`audits/audit-phase-21-preregistration.md` §9) governs from its own stated merge point.
Any merge into `agents/`, `meetings/`, `observation/`, `orchestrator/` or
`agents/strategic/prompts/` between this report and the record reopens the window; the smoke then
runs again from zero, on the changed source, with every number re-derived.

**The MANIFEST's `git_sha` is `3fd12a03`, and that is not a second source state.** The wrapper
stamps the commit the working tree was at when the recording ran; `3fd12a03` is a commit on THIS
PR's branch, and `14854a06` is the branch's base and the state this report certifies. The whole
difference between them is:

```
$ git diff --stat 14854a06..3fd12a03
 audits/README.md                       |    9 +
 audits/audit-phase-21-smoke-wave2.md   | 1355 ++++++++++++++++++++++++++++++++
 docs/artifacts.md                      |    2 +-
 scripts/record_ml_corpus.sh            |  188 +++--
 tests/scripts/test_record_ml_corpus.py |  200 ++++-
 5 files changed, 1690 insertions(+), 64 deletions(-)
```

**No frozen directory appears in it** — nothing under `agents/`, `meetings/`, `observation/`,
`orchestrator/` or `agents/strategic/prompts/` — so the substrate that rendered these prompts and
stepped these games IS `14854a06`'s, and the two shas name the same recording substrate. Of the
five paths that did move, `audits/`, `docs/` and `tests/` render nothing, and
`scripts/record_ml_corpus.sh` is the CORPUS recorder, which this run never drove: the smoke records
through `scripts/refresh_samples.sh` (§2). The stamp is reported as recorded rather than corrected
by hand, and this paragraph is the reconciliation.

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
AILIBI_REFRESH_WORKERS=2
AILIBI_SEED_MAX_ATTEMPTS=8
AILIBI_REPORTER_REASONING=1
AILIBI_CORROBORATION_DISCIPLINE=1
AILIBI_TESTIMONY_SHAPES=1
# AILIBI_IMPOSTOR_ROLL_CALL — unset, in this and in every later gate/instrument shell
```

**That is the contract's Step-3 block exactly**, and the wrapper's own preview confirms both knobs
took effect: `seed workers: 2 parallel` and `seed crash-retry: up to 8 attempt(s) per seed`. The
wrapper's featherless defaults are 2 and **4** (`scripts/refresh_samples.sh`:441, :461), so the
retry budget is an override and is exported rather than assumed. **Neither knob is recorded into
any byte this run preserved** — `AILIBI_SEED_MAX_ATTEMPTS` is read at :461 and stamped nowhere — so
this block and the wrapper's echo are what attest them, not `$SMOKE_DIR` (§12).

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

### 2.0 Two attempts, and why this report certifies the second

**A first attempt ran at the wrapper's DEFAULT retry budget of 4 rather than the Step-3 export of
8.** The reasoning at the time — that the contract's re-verified anchor list names 4 as the
wrapper's default, so the two halves of the contract disagreed — was wrong: the anchor describes a
DEFAULT and Step 3 overrides it, and those are not in tension. Zero seeds consumed a second attempt
on either run, so the deviation changed no recorded byte; it still meant the execution
configuration was not the one the contract prescribes, and a smoke may not certify a run it did not
perform as written.

**So the five seeds were recorded again under the full Step-3 block, and this report reads the
second run only.** Not one cell below comes from the first attempt. Both are preserved:

| attempt | retry budget | path | status |
|---|---|---|---|
| 1 | 4 (the wrapper default) | `/Users/danielkeinan/ailibi-smoke-21-23/9p2i-attempt-1-default-retry-budget` | superseded; quoted nowhere AS A CELL (five labelled context mentions, enumerated below) |
| **2** | **8 (the contracted export)** | `/Users/danielkeinan/ailibi-smoke-21-23/9p2i` | **the run this report certifies** |

A live model is sampled per call, so the two attempts are different bytes, not a re-derivation of
the same ones. **The first attempt is kept and named rather than deleted** — an operator who wants
to know what the wrong configuration produced can read it.

**"Quoted nowhere" means quoted nowhere AS A CELL, and the qualifier is exact.** No number in any
table, tripwire row, projection or verdict below comes from the first attempt. It IS quoted five
times as labelled non-cell CONTEXT, each mention naming the attempt as superseded and each true
against its own bytes:

| § | what the superseded attempt is quoted for |
|---|---|
| §8.4 | it also carried a spoken `saw_kill` and also fired the E.1 interaction — stated as reachability, explicitly NOT as a rate |
| §11.1 | it exercised the guard-redirect marker (5 redirects, 6 machine rows, 0 missing), which is why row 4 here is marked UNEXERCISED rather than borrowing it |
| §11.2 | 0 defaulted turns in 176 recorded calls, beside this run's 1 in 204 — two observations with their denominators, and no rate |
| §15 | its `C-9` read 88/88 = 100%, which is why this run's 101/102 is the reading that actually tested the ≥ 99% predicate |
| §16 | its path and byte count, as preserved bytes |

**No published cell depends on any of them**: delete all five and every table, every tripwire
verdict and every projection figure in this report is unchanged.

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
[dry-run] seed crash-retry: up to 8 attempt(s) per seed on a transport/crash error
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

Three of those cells are the pre-registration's own baseline-8 pins and reproduce exactly:
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
  and refuses if it has moved since startup. **What that catches is narrower than a lever drift,
  and the report states it precisely rather than claiming the stronger guarantee:** the
  re-derivation builds its own environment from the `--expect-levers` DECLARATION
  (`env = {env_var_for_lever(key): "1" for key in keys}`, `scripts/record_ml_corpus.sh`:796-798),
  never from the live environment, so a lever export that changed mid-run is invisible to it. What
  it does catch is a REGISTRY or OVERLAY change between the startup derivation and this check —
  the two launches resolving the same declaration differently — which is the way the map a record
  freezes against could stop being the map its meetings stamp. The live exports are judged
  elsewhere: by the wrapper's substrate preflight before recording (§2.2) and by
  `api/replay_loader.py`:655 at every reconstruction (§2.1);
* `check_recorded_prompt_versions` and the two dry-run echoes read the derived map;
* the acceptance CLI's `KEY=VALUE` pairs are emitted by the SAME derivation, **from the map's own
  keys**. This is the one place the shape of the old constant could not be carried forward: the old
  code inferred each template key from its version string's first dot-segment, which is correct
  only while key and value share a prefix. An arm that swaps a variant FILE breaks that —
  `impostor_roll_call` resolves `accusation_round` to
  `accusation_round_roll_call.qwen3_6_27b.v1` — so an inferred key would print an
  `--expected-prompt-versions` map `scripts/validity_gate.py` REJECTS, after the record had already
  frozen. The derivation now prints both renderings and the shell re-derives neither.

  **The planted case for that half is `impostor_roll_call`, the arm this phase records OFF**, which
  is exactly why it needs one: `test_acceptance_pairs_carry_the_maps_own_keys_not_the_version_prefix`
  first asserts the premise (at least one key differs from its value's first dot-segment, so the
  case cannot pass vacuously), then drives the committed dry-run under that arm and pins the printed
  line to `accusation_round=accusation_round_roll_call.qwen3_6_27b.v1, …`. Under the old inference
  it read `accusation_round_roll_call=…` and failed.

**And one refusal the derivation had to restore, because deriving the map removed it by accident.**
The hardcoded literal refused a slate whose STAMP outpaces its BODIES — a slate composing an arm
that swaps in a VARIANT FILE with a sibling whose block lives in the DEFAULT body — not by design
but because no composite ever matched four fixed literals. A derived map has no such accident, so
`check_slate_bodies_carry_their_stamps` restores the refusal deliberately, and **generally**: the
colliding triples are derived from the registry rather than named, an arm SWAPPING template `T` when
its overlay value's first dot-segment is not `T` and a sibling RE-BODYING `T` when its overlay value
for `T` differs from the default. On today's registry that derives exactly two colliding pairs and
refuses both:

```
$ … --expect-levers impostor_roll_call,reporter_reasoning
Error: --expect-levers names a slate whose stamps would outpace its bodies.
  'impostor_roll_call' swaps a variant file for 'accusation_round', which 'reporter_reasoning'
  also re-bodies — 'reporter_reasoning''s block never reaches that render
$ … --expect-levers impostor_roll_call,testimony_shapes
  … 'impostor_roll_call' swaps a variant file for 'accusation_round', which 'testimony_shapes'
  also re-bodies — 'testimony_shapes''s block never reaches that render
```

while `impostor_roll_call,corroboration_discipline` (which re-bodies only the ballot), either arm
alone, and **the ratified three-key slate** all still resolve. The mechanism is the one
`orchestrator.game.prompt_versions_for_set` states and
`tests/meetings/test_prompt_byte_golden.py::test_a_file_swapping_arm_serves_a_body_its_siblings_do_not_reach`
pins; this guard does not patch that known gap, it refuses to freeze a record on top of it.

**The guard runs on EVERY path that accepts a derived map** — the startup derivation and the
preflight's registry check — from one definition, because a guard wired into only the first would
leave the second able to freeze a record against provenance its prompts do not carry. Four planted
cases drive it: one asserts the registry still produces exactly the two enumerated pairs (so the
refusal tests cannot pass over a set nobody re-checked), two drive each path with each colliding
pair, and one walks five non-colliding slates through both paths and requires them to pass.

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
| 19 | 480 s | 5 | 3 | CREWMATE_EJECT | CREWMATES | 54 | 278,435 | $0.0000 |
| 17 | 373 s | 2 | 2 | CREWMATE_EJECT | CREWMATES | 28 | 130,690 | $0.0000 |
| 4 | 434 s | 3 | 0 | IMPOSTOR_PARITY | IMPOSTORS | 36 | 183,823 | $0.0000 |
| 26 | 411 s | 4 | 2 | IMPOSTOR_PARITY | IMPOSTORS | 43 | 220,219 | $0.0000 |
| 46 | 388 s | 4 | 0 | IMPOSTOR_PARITY | IMPOSTORS | 43 | 231,949 | $0.0000 |
| **all** | **21m42s wall** | **18** | **7** | — | CREW 2 / IMP 3 | **204** | **1,045,116** | **$0.0000** |

Wall clock: seed 19 alone **8m00s** (recorded first, for the §6 probe), then 4/17/26/46 on two
workers in **13m42s**. Total operator wall **21m42s**.

### 5.1 Stratum coverage as OBSERVED, not assumed from the census

The DoD verifies the stratum on the smoke's own recorded meetings, because the census that drew the
slate is a proxy over OFF bytes:

```
seeds=5  meetings=18  body reports=17  emergency=1  ejections=7
body reports WITHOUT a vent_sighting: 14    WITH one: 3
reporter ejected: 2            spoken saw_kill observations: 2
endings: CREWMATE_EJECT 2, IMPOSTOR_PARITY 3
```

**14 of the 17 recorded body reports sit in the no-vent-flag stratum** — the only stratum in which
A-47's verifier found a reporter penalty at all — and **the penalty occurred: 2 reporters were
ejected**, both of them innocent. The slate is therefore **NOT vacuous for the reporter lever**, and
that is verified on the recorded meetings rather than assumed from the draw.

**The proxy moved, exactly as the contract warned.** Against the committed census the drawn seeds
predicted 21 meetings / 20 body reports / 17 no-vent / 11 ejections / 4 reporter convictions; the ON
run recorded 18 / 17 / 14 / 7 / 2. Seed 46 recorded 4 meetings and 0 ejections where the committed
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
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 18 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 18 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 102 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 396 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 102 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 5 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

**The gate is green and one seed still carries a defaulted turn** (§11.2). That is not a
contradiction: `eval/validity.py` has no `deadline_default` check at all, which the corpus
recorder's own ledger comment states in as many words — *"the validity gate has no deadline_default
check at all — the recorder is deliberately stricter than the gate"*
(`scripts/record_ml_corpus.sh`, the freeze-guard branch). **This is exactly why the DoD scans that
watch item by hand and forbids delegating it to the gate.**

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
the committed-record mode's contract.

### 6.4 The two shells refuse each other's bytes — proven, not asserted

Both crossings were run deliberately, and both refuse rather than mis-measure.

**(i) the SMOKE bytes reconstructed in the BARE shell** — `api/replay_loader.py`:655 →
`_assert_recorded_substrate`, exit 1:

```
api.replay_loader.ReplaySubstrateMismatchError: replay substrate mismatch for 'headless-seed-4':
recorded with {... 'corroboration_discipline': True, ... 'reporter_reasoning': True, ...
'testimony_shapes': True} but reconstructing under {... 'reporter_reasoning': False,
'corroboration_discipline': False, 'testimony_shapes': False}
(differing levers: ['corroboration_discipline', 'reporter_reasoning', 'testimony_shapes'];
unknown levers: []). Toggleable lever(s) [...] differ: match the environment to the stamp
(AILIBI_CORROBORATION_DISCIPLINE, AILIBI_REPORTER_REASONING, AILIBI_TESTIMONY_SHAPES) [...]
(This is not a determinism break — the per-tick state hash is substrate-independent.)
```

**(ii) the COMMITTED-set reader in the LEVER-ON shell** — the counterfactual's own second refusal
(§11.1 there), exit 1:

```
the ambient environment is not the record's substrate at start: the recording needs every live
toggle OFF, but this process reads reporter_reasoning ON (AILIBI_REPORTER_REASONING),
corroboration_discipline ON (AILIBI_CORROBORATION_DISCIPLINE), testimony_shapes ON
(AILIBI_TESTIMONY_SHAPES). Seven consumers re-derive the meeting reduction with no env argument,
so a shell that disagrees with the recording makes every imported instrument read a substrate the
bytes were never made under.
```

**An operator who does not know which shell they are in reads either of these as a defect.** They
are the discipline working.

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
| body-report openings gaining the discovery-account block (`R-13`, block level) | **17/17 = 100%** | 620/620 (counterfactual §10.1) |
| — the same cell counted by byte diff (informational) | 17/17 = 100%, agrees | — |
| non-reporter speech turns in a body-report meeting gaining the base-rate block (`R-14`, block level) | **78/78 = 100%** | 2,715/2,715 |
| — the same cell counted by byte diff (informational) | 78/78 = 100%, agrees | — |
| emergency-meeting prompts gaining either block | **0** | 0 |
| ballots gaining a reporter block (`R-15`) | **0/102** | 0/3,631 |
| prompts carrying `<who_reported>` (direct byte read) | 77 of 83 speech, 18 of 19 openings | no reference |
| prompts carrying the `at_body` line (direct byte read) | 4 of 83 speech | no reference |
| lines THIS LEVER adds, per opening it changes (leave-one-out) | 17/17 = **1.00** | 620/620 = 1.00 (counterfactual §3.3) |
| lines THIS LEVER adds, per speech turn it changes (leave-one-out) | 316/78 = **4.05** | 11,005/2,715 = 4.05 |

The six speech prompts and one opening without `<who_reported>` are the emergency meeting's, which
has no reporter. **The reporter thread lands on every body report and nowhere else**, and the
per-prompt prose it adds reproduces the counterfactual's per-prompt values to two decimal places.

### 8.2 `corroboration_discipline`

| cell | smoke (5 seeds) | ratified baseline-8 reference |
|---|---|---|
| ballots gaining the source-count block (`C-9`, block level) | **101/102 = 99.02%** | 3,614/3,631 = 99.5% |
| — the same cell counted by byte diff (informational) | 101/102 = 99.02%, agrees | — |
| ballots carrying `<testimony_sources>` (direct byte read) | 101/102 — the instrument and the byte read agree exactly | no reference |
| ballots rendering a sole-source chain ("an answer to a charge, not a second witness") | 66/102 | no reference |
| ballots rendering the map's impossible-transit counter | 42/102 | no reference |
| accused subjects with NO first-hand source (`C-1`) | 15/41 = 36.6% | 475/1,525 = 31.1% |
| ejected subjects with NO first-hand source (`C-2`) | 2/7 = 28.6% `[ADV]` | 11/425 = 2.6% |
| ejections whose charge ANSWERED the ejectee's own (`C-3`) | 2/7 = 28.6% `[ADV]` | 33/429 |
| ejected subjects with a map-satisfied placement pair (`C-4`) | 0/7 `[ADV]` | 48/429 |
| **the ejecting-ballot citation mix** (`C-5`/`C-6`/`C-7`, over the 5 ballots that ejected the 2 innocents) | **hearsay 3 / own-observation 0 / own-turn 2 / other 0 / uncited 0** | 89 / 37 / 23 / 0 / 1 of 150 (counterfactual §4.3) |
| openings and speech turns gaining anything under this lever alone | **0** | 0 |
| lines THIS LEVER adds, per ballot it changes (leave-one-out) | 799/101 = **7.91** | 26,522/3,614 = 7.34 (Errata E.1) |

**The one ballot of 102 that does NOT gain the block is the residue §8.1 names**, in its own words:
"meetings whose ledger holds no row for any of that voter's candidate targets". §8.1 rules that
residue "context rather than a second criterion, because `C-9` publishes the share and not the
residue's membership", and the share is 99.02% against a ≥ 99% floor. The citation mix is 5 ballots
and is directional to the point of being anecdotal; it is reported because the DoD names it, with
its denominator beside it.

**ERRATUM 2026-09-03 — additive; the table above is NOT rewritten.** This section's
`ratified baseline-8 reference` column quotes the corroboration cells as they stood BEFORE PR #424
(`ffaf9991`), i.e. through the counterfactual's Errata `E.1`: **475/1,525** (`C-1`), **11/425**
(`C-2`), **48/429** (`C-4`) and **26,522/3,614 = 7.34** lines per changed ballot. #424 amended the
ledger's grounding semantics before the record, and the counterfactual's Errata `E.2` republishes
those cells — they now read **460/1,525**, **10/425**, **79/429** and **27,654/3,614 = 7.65**.
`C-3` (33/429) is unmoved and `C-9` still reads 3,614/3,631, because no ledger row is added or
removed.

**The smoke's own column does not move, and that is why this is an erratum rather than an edit.**
The five-seed cells beside the reference were measured on bytes recorded and certified at
`14854a06` — pre-#424 semantics — so re-pointing the reference column at `E.2` would set a
post-#424 reference against a pre-#424 measurement and invite exactly the comparison §0 forbids.
**The smoke's ON cells are pinned to `14854a06` semantics**; the reference column stays as
published, and this erratum names which pin it quotes. §18 is the run made under `E.2` semantics.
Logged as a row in `audits/audit-phase-21-preregistration.md` §11.

### 8.3 `testimony_shapes`

| cell | smoke (5 seeds) | ratified baseline-8 reference |
|---|---|---|
| CREW speech turns gaining the elicitation block (`T-9a`) | **55/55 = 100%** | 2,023 of 2,959 aggregate (§10.1 `T-9`) |
| IMPOSTOR speech turns gaining an elicitation block (`T-9b`) | **0/29** | 0 |
| openings gaining an elicitation block (direct byte read) | 19/19 | 672/672 (§5.6) |
| `whereabouts` statements surviving the reduction | **102** (OFF: 0) | 0 → 3,157 (§5.2) |
| `saw_move` statements surviving the reduction | **35** (OFF: 0) | 0 → 1,606 |
| `saw_kill` statements surviving the reduction | **2** (OFF: 0) | 0 → 0 (`T-4`, `[ADV]`) |
| episodic rows the ingest writes at recorded boundaries (`T-5`) | 2,020 ON against 1,339 OFF | 73,218 against 49,667 |
| location accounts reaching the alibi map (`T-6`) | **130/130 = 100%** ON, 28/130 = 21.5% OFF | 4,173/4,173 ON, 1,016/4,173 = 24.35% OFF |
| spoken vent accounts naming a player who never vented (`T-7`) | **0/4** `[ADV]` | 0/512 |
| lines THIS LEVER adds, per opening / speech turn / ballot it changes (leave-one-out) | 36/18 = **2.00**, 121/58 = **2.09**, 13/13 = **1.00** | 1,344/672 = 2.00, 4,046/2,023 = 2.00, **0** (Errata E.1) |

**The witnessed-kill half is EXERCISED, not untested.** The census (§3) found four committed seeds
carrying a crew-witnessed kill and all four were drawn; on the smoke's own bytes the walk finds
**3 crew-witnessed kill observations across seeds 19 (1) and 26 (2)**, and **two of them were
SPOKEN as structured `saw_kill` observations**. A-22's 20-in-300-games rate is quoted here as the
reason the half is usually untestable at five seeds, not as an excuse: it was testable because the
slate was drawn for it.

### 8.4 The first spoken `saw_kill`, and its two registered consequences

**Baseline 8 holds zero spoken `saw_kill` anywhere** (`grep -rn saw_kill replays/` returns nothing),
so the `saw_kill` path had zero committed exposure and these are the first bytes in the project that
could carry one. **They do — twice, both by a reporter opening a body report:**

```json
seed 19, meeting-3, turn 0, p-1:  {"room": "ENGINEERING", "subject": "p-9", "tick": 16, "type": "saw_kill"}
seed 26, meeting-0, turn 0, p-1:  {"room": "EAST_HALL",   "subject": "p-3", "tick": 6,  "type": "saw_kill"}
```

spoken as *"I found p-7's body in Engineering at tick 16, and I saw p-9 perform the kill right
there"* and *"I found p-8's body in East Hall at tick 6, and I saw p-3 kill him right there."*

The DoD requires the two REGISTERED consequences be named rather than filed as drift, and both are
observed:

1. **The role-blind PUBLIC-TRANSCRIPT row reaches every later speaker, impostors included.** The
   direct byte read finds the row `(spoken account, nothing confirms it)` in **11 of 83 speech
   prompts and 13 of 102 ballots**. This is CORRECT — it is the one table every seat reads, it is
   pinned by `tests/agents/test_bespoke_prompt_sets.py::test_a_spoken_kill_reaches_every_later_speaker`,
   and §8.1 EXCLUDES it from T5 by construction. T5's impostor half reads 0/29 with those rows
   present, which is the reader doing exactly what the ratified note says it must.
2. **The joint-slate ballot moves by more than the two arms alone.** The leave-one-out leg that
   withdraws `testimony_shapes` while `corroboration_discipline` stays ON moves **13 of 102 ballots,
   by −13 lines and −1,160 bytes**. On the committed baseline-8 bytes that same leg moves the ballot
   by **exactly zero** (Errata E.1: *"on the recorded bytes the ballot's added bytes are identical on
   the `corroboration_discipline`, `two-ON` and `all-three-ON` legs"*). **The interaction E.1
   re-registered has now fired on live bytes for the first time**, which E.1 itself predicts in as
   many words: *"the FIRST spoken kill at 21.23 or 21.24 will move the joint ballot by more than the
   two arms alone, which is expected and is not unregistered drift."* This report does not
   decompose that delta between the public-transcript row and the adopted-clause fork, and does not
   re-price E.1's per-row arithmetic — that is pinned on a synthetic kill meeting by
   `tests/meetings/test_corroboration.py::TestAdoptedClauseWording`.

**Two speech denominators appear in this report, and they are different bases rather than a
discrepancy.** §8's byte census counts RECORDED calls — 83 `accusation_round` prompts in
`llm_calls`, by §17.3's classifier — while T5 counts one per RECONSTRUCTED render, which is the
**84** speech turns the transcripts carry (102 turns less 18 openings; 55 crew + 29 impostor in
§15). The single turn between them is seed 26's defaulted husk (§11.2): it exists as a transcript
turn, but its burned generation is recorded in the `failed_call` channel rather than in
`llm_calls`, so the byte census cannot see it and the render count can. Every other meeting's two
counts agree exactly, and the same split explains 19 recorded opening prompts against 18 opening
turns (seed 46's meeting-0 recorded two).

**The superseded first attempt (§2.0) also carried a spoken `saw_kill` and also fired the
interaction.** Two independent five-seed samples at this slate each produced one, which is stated as
an observation about the shape's reachability and NOT as a rate: two samples cannot price one.

### 8.5 What the table DID with the two spoken kills — a model fact, at n = 2

The render is only half the question, and the counterfactual's §7 puts the other half beyond any
offline instrument: *"whether crew stop laundering witnessed kills into `saw_vent` rows"* and every
vote outcome are on its NOT-PREDICTABLE-OFFLINE list. **These are the first two live data points the
project has**, and they are reported as such — two cases, no rate, no criterion.

| | seed 19, meeting 3 | seed 26, meeting 0 |
|---|---|---|
| speaker | p-1, CREWMATE, **and the meeting's own reporter** | p-1, CREWMATE, **and the meeting's own reporter** |
| named as the killer | p-9 — **a real IMPOSTOR** | p-3 — **a real IMPOSTOR** |
| ballot tally | p-1 ×3, p-9 ×1, SKIP ×1 | SKIP ×5, p-3 ×3 |
| outcome | **EJECTED p-1** — the truthful witness, a CREWMATE | **SKIPPED** |
| engine contradiction naming anyone | none | none |

**Both accounts were TRUE and neither converted.** In seed 19 the table ejected the reporter who had
just testified to watching the kill, three votes to one for the impostor he named. That is A-4's
reporter class (`audits/review-2026-08-26/A/collated-findings.md`:431) occurring with the strongest
testimony the game can produce on the record, and under the very lever that exists to elicit it.

**What this is not.** It is not a bar, not a tripwire, and no §9.2 criterion names it — T5 governs
whether the elicitation block RENDERS, and it rendered on 55 of 55 crew turns. It is not evidence
that the lever fails: two meetings cannot separate a lever effect from a five-seed draw, and the
counterfactual's governing sentence applies unchanged — **a sentence added to a prompt is not a vote
that changes.** It is the single most decision-relevant thing these bytes contain for 21.24, which
is why it is on the page rather than in a footnote.

### 8.6 The slate's own render prediction

Counterfactual §8.4 predicts added prose is additive in LINES on every seam and that the only
cross-lever interaction is the ballot's. On the smoke's leave-one-out legs the opening reads
17 + 36 = 53 lines against the whole slate's 53 (additive to the line), the speech turn reads
316 + 121 = 437 against 437 (additive to the line), and **the ballot reads 799 + 13 = 812 against
812 — additive in lines, with the 13-line testimony term existing only because a kill was spoken.**
**The prediction holds on all three seams.**

## 9. The three watch cells

The register's verifiers ruled against the obvious reading of each, so each is a watch item rather
than a pass/fail row. **All three are directional at this n and none is a criterion.**

### 9.1 Agreement with the opener must NOT be flattened (A-19)

A-19's verifier WITHDREW the advice to down-weight agreement with the opener: same-target turn ≥ 2
crew accusations hit 79.2% (n=48) and 88.5% (n=122) against different-target 4.7% (n=106) and 3.1%
(n=287). **A lever that flattens that is a regression to report, not a success.** No committed
reader emits this split — it is §5.1's measured-but-not-registered class — so it is computed here as
a session walk (§17.5 carries the reader), on the smoke bytes and on the SAME five committed seeds with
the same code:

| cell | committed same-five (OFF) | **smoke (ON)** |
|---|---|---|
| turn-0 CREW accusations, accuracy | 14/21 = 66.7% | **11/18 = 61.1%** |
| turn ≥ 2 CREW accusations, SAME target as turn 0 | 22/22 = 100.0% | **14/16 = 87.5%** |
| turn ≥ 2 CREW accusations, DIFFERENT target | 2/24 = 8.3% | **2/21 = 9.5%** |

**Agreement with the opener is NOT flattened**: the same-target/different-target separation stays
enormous (87.5% against 9.5%), and both columns reproduce the shape A-19's verifier measured — the
ON column lands between his two published same-target readings (79.2% and 88.5%). The same-target
cell falls from 100% to 87.5% on 16 cases — two convictions — which one game moves; it is reported,
and **it is not a regression this n can establish.**

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
| body-report meetings carrying a non-reporter co-discoverer (`R-11`) | 3/17 | 118/620 |
| co-discoverer slots, CREW / IMPOSTOR (`R-12`) | 2 / 2 = **50.0% impostor** | 71/145 = **49.0% impostor** |
| prompts that received the `at_body` line | 4 | no reference |
| — of those, the speaker was an IMPOSTOR | **2 of 4 = 50.0%** | no reference |

**The hazard the counterfactual measured reproduces on the smoke's own bytes to within a point**,
at a denominator of four. It is a WATCH item: no §9.2 criterion names this class, and this report
invents none.

### 9.3 The confession net (A-16) — nothing to publish, and why

A-16's verifier requires any published confession cell to carry its precision beside its count. On
the smoke bytes the disambiguated pair #416 shipped reads **`model_self_disclosure_visible_turns` 0
and `crew_self_disclosure_control_turns` 0**, with `player_visible_leak_turns` **0 of 102 turns**.
There is no cell to publish, so none is published; the register's "10 fires, 20% precision" is a
baseline-7 figure over a pre-disambiguation net and is not quoted as a cell here (counterfactual
§5.5).

## 10. The honesty and solvability cells

Run under the recorded slate, after the gate, over the whole set — and beside a LIKE-FOR-LIKE OFF
column re-derived at `$0` from the SAME five committed seeds. **Every row is directional at this n.**

The contract requires BOTH probes quoted with denominators — the first completed seed alone, before
the remaining four queued, and the whole set — so both columns are here.

| cell | committed same-five (OFF) | **first seed ALONE (ON)** | **whole set (ON)** |
|---|---|---|---|
| games / meetings | 5 / 21 | **1 / 5** | **5 / 18** |
| agent-clock sightings proved | — | **69** | **387** |
| I-2 false crew self-placement | 0/80 | **0/21** | **0/82** |
| — copyable from a rendered self-location line | 5/80 = 6.25% | **2/21 = 9.52%** | **5/82 = 6.10%** |
| I-3 sole-flag precision | 0/0 (no sole-flag meeting) | **0/0** | **0/0** |
| I-4 grounded sighting side | 0/0 | **0/0** | **0/0** |
| I-5 fabricated completion lines | 0/34 | **0/4** | **0/25** |
| I-6 adjacent-room STRONG share | 0/0 | **0/0** | **0/0** |
| I-7 movement-origin flags | 0/2 | **0/0** | **0/1** `[ADV]` (move-backed 1, destination 1) |
| I-8 marker contamination (turns / prompts) | 0/110, 0/221 | **0/27, 0/54** | **0/102, 0/204** |
| I-9 singular-persona prompts | 0/221 | **0/54** | **0/204** |
| I-10 meetings with a venting participant | 2/21 | **0/5** | **2/18** |
| — reporter killed within 3 ticks | 2/21 | **0/5** | **3/18** |
| I-11 free zero-witness kills declined | 0/28 | **0/6** | **2/27** (fellow-defer 2) |
| — ghost-top decisions mismatched | 0/249 | **0/43** | **0/249** |
| render budget, mean rendered lines/snapshot | 40.52 over 221 | **42.52 over 54** | **39.57 over 204** |
| render budget, testimony rows (≤4 / 5-6 / ≥7) | 4,181 (2,090 / 1,859 / 232) | **1,588 (304 / 1,284 / 0)** | **4,920 (948 / 3,606 / 366)** |
| solvability (the memo's I-5): killer in candidate set | 19/20 = 0.95 | — | **16/17 = 0.9412** |
| — one candidate, and it is the killer | 6/20; 6/6 | — | **4/17; 4/4** |
| — ejected an already-cleared player | 3/10 = 0.30 | — | **1/6 = 0.1667** `[ADV]` |

**The first-seed column is a `$0` OFFLINE RE-RUN of the same invocation on the PRESERVED bytes**, not
a transcription of the live console: seed 19 was copied out of the certified run into
`/Users/danielkeinan/ailibi-smoke-21-23/first-seed-19` and
`uv run python scripts/measure_baseline.py --honesty <that dir>` was run in the same lever-ON shell
the Measurement line used. It reproduces the live probe's own header and render budget to the digit
(`1 games, 5 meetings; +1 agent clock proved on 69 discriminating sightings`;
`mean rendered lines/snapshot 42.52 over 54 snapshots; reported-testimony rows 1588`), which is what
makes it the same reading rather than a second one. The solvability rows have no first-seed column
because that probe was run over the whole set only.

The `I-n` labels in the first thirteen rows are `measure_baseline.py --honesty`'s own numbering and
are NOT the pre-registration's §2 instrument list; the two solvability rows carry the memo's label
explicitly so the collision cannot be misread.

`measure_baseline.py --honesty` exited 0 on the FIRST completed seed alone (seed 19, **5 meetings —
not vacuous**, so the probe is a passed probe and not an empty one) and again over the whole set;
`--solvability` exited 0. **Neither raised**, on either invocation.

### 10.1 The secondary cells §5 registers, observed and never gated

| cell | committed same-five (OFF) | **smoke (ON)** | ratified baseline-8 reference |
|---|---|---|---|
| win split | CREW 2 / IMP 3 (impostor 60%) | **CREW 2 / IMP 3 (impostor 60%)** | `samples/9p2i` 15/50 = 30% |
| decisiveness (body-report ejections / body-report meetings) | 10/20 = 50.0% | **6/17 = 35.3%** | 377/620 = 60.8% |
| bar 1's cell split by a spoken kill (`P-1k`) | 0 of 7 by construction — the census finds no spoken `saw_kill` anywhere in the committed bytes | **0/3** `[ADV]` | 0 of 96 |
| — of those, convicted an IMPOSTOR (`P-1ka`) | 0/0 `[ADV]` | **0/0** `[ADV]` | 0/0 `[ADV]` |
| zero-flag convictions (`eval/vj_instruments.py`) | not re-derived | **3/7**, 2 CREW / 1 IMPOSTOR | 86/429, 37 CREW |

The win split is 5 games against a ±15-point band written for a 50-game leg; it is printed because
§5 registers it and it decides nothing.

**`P-1k` reads 0/3 and NOT `n/a`**, per §12's own reader rule for an empty denominator. The split is
empty for the reason §8.5 sets out: **neither spoken kill convicted anybody**, so no conviction of
any kind — direct or non-direct — has a spoken kill behind it. **A spoken kill was filed and the
split is still empty**, and the report does not read that zero as absence of the shape.

## 11. The Wave-1 no-regression check, and the watch item scanned by hand

### 11.1 No Wave-1 repair regressed under the levers

The 21.14 marker pass, run unchanged (§17 quotes its two censuses; the marker pass itself is
`audits/audit-phase-21-smoke.md` §7.3), against the smoke bytes and the same five committed seeds:

| # | repair | marker | committed same-five | **smoke (ON)** | reading |
|---|---|---|---|---|---|
| 1 | A-6 (21.1) | the taught oracle line inside a rendered proof block | 0 of 221 prompts; 46 `Proof.` blocks; banned vocabulary absent | **0 of 204 prompts; 45 `Proof.` blocks; banned vocabulary absent** | **NO REGRESSION** |
| 1b | A-6, spoken | the oracle net over `free_text`, rationales and claim reasons | 0 hits / 351 utterances (FLOOR net fires 109) | **0 hits / 325 utterances (FLOOR net fires 91)** | **NO REGRESSION** — the over-broad floor demonstrably reaches these surfaces |
| 2 | A-17 (21.2) | structured testimony rows in the vote-ballot prompts | 110/110 carry `saw:`/`claims:`/`said:` | **102/102 carry all three**, over 614 rendered turn heads | **NO REGRESSION** |
| 3 | A-14 (21.3) | every recorded action row carries an explicit disposition | 184/184 tick rows | **159/159 tick rows**; 65 of 965 = 6.7% `discarded_by_meeting` over 17 trigger ticks | **NO REGRESSION** |
| 4 | A-3 (21.3) | redirected ballots carry machine-readable provenance | 110 ballots, 2 display-marked, 4 machine rows, 0 missing | **102 ballots, 0 display-marked, 0 machine rows, 0 missing** | **NO REGRESSION**, and UNEXERCISED — no ballot was redirected on these bytes, so the marker is vacuous here rather than green |
| 5 | B-8 (21.4) | the belief line's last-seen agrees with the agent's own sightings | 0/650 stale | **0/515 stale, 0 stale-and-wrong-room** | **NO REGRESSION** |
| 6 | A-31 (21.5) | exactly one memory row per witnessed vent | 20 witnessed, 0 heard, 0 double | **16 witnessed, 0 heard, 0 double**, 5 distinct, 0 heard-only | **NO REGRESSION** |

Row 4 is marked UNEXERCISED rather than passed: `ballot_redirects 0 (eject 0)` on this run, so a
guard-redirect provenance defect could not have shown here. The superseded first attempt did
exercise it (5 redirects, 6 machine rows, 0 missing), but that run is quoted nowhere as a cell
(§2.0) and this row does not borrow it.

### 11.2 The watch item — SCANNED BY HAND, and it FIRED

The validity gate has no `deadline_default` check at all. Scanned directly over the recorded bytes:

```
failed_call rows by error_type: {'deadline_default': 1}
deadline_default rows (EITHER shape): 1
```

**One recorded `failed_call` row on seed 26 carries `error_type == "deadline_default"`.** This is
the watch item the DoD forbids delegating to the gate, and it fired. The row in full, with the
prompt and the raw response elided:

```
game_id      headless-seed-26      meeting_id  headless-seed-26:meeting-1   tick 11
error_type   deadline_default      model  Qwen/Qwen3.6-27B   cost_usd 0.0
error_message
  opt_in turn (turn 5) defaulted (validation); p-5 submitted no turn
  [ValidationError: 1 validation error for MeetingTurn
   observations.1
     Input tag 'corroboration' found using 'type' does not match any of the expected tags:
     'saw_player', 'completed_task', 'found_body', 'saw_vent', 'saw…]
```

and the transcript carries the husk it left:

```json
{"turn_id": "headless-seed-26:meeting-1:turn-5", "turn_index": 5, "speaker": "p-5",
 "turn_kind": "opt_in", "observations": [], "claims": [],
 "free_text": "(missed deadline; no turn submitted)"}
```

**Four things about it, each stated rather than inferred.**

1. **No OPENING defaulted.** The recorder's own counters read `lost_openings 0 (defaults 1)`: the
   defaulted turn is `turn_index 5`, an `opt_in` speech turn. §9.2's criterion names *"a seed whose
   opening defaults"*, so **the criterion as written is NOT met** (§14) and this report does not
   stretch it to fit.
2. **No deadline was missed — the cause is a SCHEMA VALIDATION failure, and `error_type` is the
   DOCUMENTED shared channel rather than a mislabel.** The model put a `corroboration` item, which
   is a CLAIM type, into `observations`, and the turn failed `MeetingTurn` validation. The
   labelling is `orchestrator/game.py`:2486-2508 (`_record_deadline_defaults`), and its own
   docstring DESIGNS the shared channel in as many words: *"written into the EXISTING failed-call
   channel … with ``error_type="deadline_default"`` -- no new replay record kind … The defaulted
   phase and the trigger kind (deadline vs validation) are named in ``error_message`` so the husk
   is auditable."* Both branches stamp it accordingly — the burned-generation row at :2543 (the one
   that fired here, carrying the real model and its tokens) and the zero-spend marker at :2557 —
   and **this row honours the contract**: its `error_message` reads *"opt_in turn (turn 5)
   defaulted (validation); p-5 submitted no turn"*, naming the trigger exactly where the docstring
   says to look. **So `error_type` is a channel name BY DESIGN; reading it as a cause is a
   consumer's error, not a recorder defect, and this report withdraws the word "mislabel" for it.**
   What remains is a LEGIBILITY defect, and it is the husk's `free_text`: `meetings/manager.py`:209
   mints the literal `"(missed deadline; no turn submitted)"` for every default whatever its cause,
   so a validation slip leaves a transcript row ASSERTING a missed deadline that never happened,
   and unlike `error_message` that string carries no trigger at all. **That** is what §16 routes.
   One consequence of the shared channel stands on its own and is not a defect either:
   `check_replay_provenance` keys on `error_type` deliberately (its own comment says so), so no
   guard or gate separates a wall-clock miss from a schema slip without reading `error_message` —
   which is §16 item 1's asymmetry, not this item.
3. **The corpus freeze guard WOULD refuse this seed, and it is demonstrated doing so** rather than
   asserted. `check_replay_provenance` keys on `error_type` (deliberately — *"the burned-generation
   branch stamps the REAL baseline model, so a model-only check misses it entirely"*), and its
   branch run against these bytes exits 1:

   ```
   check_replay_provenance (deadline_default branch): 1 violation(s) in …/9p2i —
   replay-seed-26.jsonl: 1 deadline_default failed-call row(s) — the turn(s) were DEFAULTED,
   so the transcript carries a fallback husk rather than model output; re-record the seed
   ```

   That guard is on the **corpus** path only; `scripts/refresh_samples.sh` contains no
   `deadline_default` check (`grep -c` → 0) and neither does the validity gate. So the two roster
   families would treat this seed differently — a known, ledgered asymmetry, in the recorder's own
   words: *"the validity gate has no deadline_default check at all — the recorder is deliberately
   stricter than the gate."*
4. **The seed was NOT re-recorded.** The recorder's prescribed remedy is to re-record it, and the
   baseline-7 record did exactly that for two seeds. Applying it here would have made this report
   green by re-rolling, which is the one thing a smoke must not do. **The record inherits the item
   with its remedy named** (§16).

The recorder's own summary counters, from the whole-set eval-report rebuild:

```
lost_openings 0 (defaults 1) | vote_defaults 0 (must_vote 0) | ballot_redirects 0 (eject 0)
missed_skip 15 | meeting_rate 1.00 (18 meetings) | ejection_accuracy 0.7143 (5/7)
```

**Zero lost openings and zero vote defaults; one non-opening default.** The observed rate is **1
defaulted turn in 204 recorded calls**; the superseded first attempt carried 0 in 176 (§2.0). Two
five-seed samples cannot price this, and the report gives no rate for the record to plan against —
only the two observations and their denominators. **The contract's own DoD item for this scan cannot be ticked on these bytes; §14.1 walks it.**

## 12. Operating data, and the re-priced projection

Measured, not inherited.

```
18 meetings | 204 LLM calls | 1,001,257 input + 43,859 output = 1,045,116 tokens | $0.0000
tokens/call    5,123.1
calls/meeting     11.33
tokens/meeting 58,062.0
per-seed serial wall: 480, 373, 434, 411, 388 s  (mean 417.2, min 373, max 480)
total operator wall: 21m42s  (8m00s serial first seed + 13m42s on two workers)
```

**The basis, stated because two totals are defensible.** Every figure above — and §12.1's, §12.2's
and §11.2's "204 recorded calls" — counts `llm_calls` rows in the recorded meetings ONLY. The
seed-26 `failed_call` row (§11.2) was a COMPLETED provider call whose spend is real and is recorded
outside that channel: **4,637 input + 262 output = 4,899 tokens, $0**. Counted inclusively the run
reads **205 calls and 1,050,015 tokens**, which is exactly what `tournament-eval-report.json`'s
`cost_dashboard` reports (1,005,894 input + 44,121 output). **The projection uses the `llm_calls`
basis**, and the difference is not cosmetic on the ON side alone: the like-for-like OFF reference
carries zero `failed_call` rows, so switching bases would lift the §12.1 ratio from ×1.1703 to
×1.1758 (58,334.2 tokens/meeting) and the §12.2 centre by about four minutes — inside the bracket's
own width, and disclosed here rather than folded in.

**Worker occupancy:** the parallel leg did 1,606 s of serial seed work across 822 s of wall on two
workers = **97.7%**; the idle 2.3% is the tail after seed 26 finished while seed 46 ran on. The
first leg was one seed by design, so its capacity figure is not comparable and is not averaged in.

**Retries, transport blips, worker diagnostics: none.** Both run logs were scanned for `WARN`,
`ERROR`, `Traceback`, retry, dead-owner and claim diagnostics — **zero matches in either**. **No seed
consumed a second attempt of its budget of 8**, which is why the retry budget never bound (§2.0).
The one defaulted turn (§11.2) is not a retry: a recorded parse failure is non-fatal to the wrapper
by design (`scripts/refresh_samples.sh`:457-461) and consumes no attempt.

**Both of those readings come from the operator's shell and the wrapper's logs, NOT from the
preserved bytes, and the report says so rather than implying the bytes attest them.** No recorded
byte carries a retry budget or a per-seed attempt count: `AILIBI_SEED_MAX_ATTEMPTS` is read only at
`scripts/refresh_samples.sh`:461 and is never stamped into a replay row, into `MANIFEST.md` or into
`tournament-eval-report.json` (`grep -c attempt` over all three → 0). So "budget of 8" and "zero
retries" are attested by the exported block quoted in §2, by the wrapper's own dry-run echo
(*"seed crash-retry: up to 8 attempt(s) per seed"*) and by the scanned run logs — checkable, but
not re-derivable from `$SMOKE_DIR` alone by a later reader. §2.0's account of the two attempts
rests on the same evidence.

### 12.1 The inflation, measured like-for-like

The 21.14 §11 method, re-run rather than inherited. The PRIMARY denominator is the SAME five
committed seeds; the re-derived all-games mean is its CROSS-CHECK. **Both are published.**

| denominator | meetings | tokens | tokens/meeting | ratio against the smoke |
|---|---|---|---|---|
| **the SAME FIVE committed seeds** (the like-for-like, and the primary) | 21 | 1,041,851 | **49,612.0** | **×1.1703 (+17.0%)** |
| both committed 9p2i legs, 200 games (the cross-check, re-derived from the bytes) | 590 | 31,939,656 | 54,135.0 | ×1.0725 (+7.3%) |
| the smoke | 18 | 1,045,116 | 58,062.0 | — |

**The two denominators DISAGREE by 8.4% on the OFF side, and that disagreement is the finding this
check exists to produce.** The drawn five are token-LIGHTER per
meeting than the set average (49,612.0 against 54,135.0), because this slate was drawn for lever
coverage — the no-vent-flag stratum, the reporter-conviction seeds and every witnessed-kill seed —
rather than for typicality. **The five drawn seeds are therefore NOT a representative sample on
tokens-per-meeting, and the like-for-like ratio is an upper bound on the inflation the record will
see.** The all-games cross-check is carried as the projection's low end for exactly that reason.

**8.4% against 21.14's 0.1% is a change of measurement, not a degradation of the sample, and this
report does not present them as like quantities.** 21.14's 0.1% (`audits/audit-phase-21-smoke.md`
§11: 148,084.8 against 148,135.8) compared the same five seeds against the **fifty**-game
`samples/9p2i` leg, on tokens per **GAME**, on the **pre-21.15** bytes — and its own 200-game
both-legs row already disagreed by 3.7% on the ratio (142,844.1 tokens/game, ×1.2399 against
the like-for-like ×1.1961). The 8.4% here
compares the same five seeds against the **two-hundred**-game both-legs population, on tokens per
**MEETING**, on the corrected bytes. Different comparator, different unit, different bytes: neither
number bounds the other, and 21.14's figure is cited as the precedent for running the check, never
as a threshold this run missed.

**The scaling unit changed deliberately, and the contract prescribes the change.** 21.14 scaled its
projection on tokens/game; this one scales on tokens/meeting, which the DoD names in as many words
(*"scaled by this smoke's measured tokens-per-meeting ratio"*). So the like-for-like ratio on
tokens/GAME is published here as a third figure, to make the change of unit visible rather than
silent:

| like-for-like unit | same-five committed | smoke | ratio |
|---|---|---|---|
| tokens per **meeting** (the contract's unit, and this report's centre) | 49,612.0 | 58,062.0 | **×1.1703** |
| tokens per **game** (21.14's unit, published for continuity only) | 208,370.2 | 209,023.2 | **×1.0031** |

**×1.0031 is not evidence the levers are nearly free**, and the centre stays on tokens/meeting
because of what it hides: the ON run produced **18** meetings where the same five committed seeds
carry **21**, so a per-game unit lets a trajectory difference in meeting count cancel the prompt
growth the levers actually cause. A record is priced by the meetings it renders, and the per-game
figure prices a game-count that neither run controls.

The per-meeting increase splits, against the same five committed seeds:

| | same-five committed | smoke | factor |
|---|---|---|---|
| calls per meeting | 10.52 | 11.33 | **×1.0769 (+7.7%)** |
| tokens per call | 4,714.3 | 5,123.1 | **×1.0867 (+8.7%)** |
| **tokens per meeting** | **49,612.0** | **58,062.0** | **×1.1703 (+17.0%)** |

and the two factors multiply to the third exactly (1.0769 × 1.0867 = 1.1703). **So the per-meeting
increase splits almost evenly between larger prompts and a higher call rate.** The prompt-size term
is the Wave-2 blocks paying their way, measured; the call-rate term is a trajectory effect at
n = 18 meetings, not a render fact, and 10.52 → 11.33 is well inside what five seeds can wander.

### 12.2 The four-leg projection, re-derived

Method, stated so 21.24 re-runs it rather than inherits it: the re-record's MEASURED per-leg actuals
(`audits/audit-phase-21-rerecord.md` §2 — 3h07m00s / 7h59m32s / 23m15s / 24m41s-incomplete, total
11h54m28s over 299 of 300 games) are scaled to a full 300 games by pricing leg 4's 49 recorded games
up to 50 (×50/49), giving **11h54m58s**, and that baseline is scaled by this smoke's measured
tokens-per-meeting ratio. The bracket's low end is the all-games cross-check ratio; its centre is
the like-for-like ratio, which the ratified reading rule makes primary; its high end is the
like-for-like ratio multiplied by a latency allowance taken from this run's own measured per-seed
spread (slowest 480 s over the mean 417.2 s = ×1.1505), because with `$0` flat-rate billing the wall
is dominated by hosted-provider latency, which five seeds measure coarsely.

| | scaling factor | **four-leg total** |
|---|---|---|
| low (all-games cross-check ratio) | ×1.0725 | **12h46m50s** |
| **centre (like-for-like ratio, primary)** | **×1.1703** | **13h56m45s** |
| high (like-for-like × the latency allowance) | ×1.3465 | **16h02m42s** |

**The bracket is 12h47m – 16h03m, centred at 13h57m**, against the re-record's realized 11h54m28s
for 299 games and the phase-20 record's 23h25m42s for 300. **The Wave-2 levers add rendered prompt
bytes, and this ratio is the single number that decides whether the next record fits its window: at
the centre it does, with roughly nine and a half hours of margin against the phase-20 wall.**

**One honest limit on the bracket.** The projection prices PROMPT growth; it does not price a
re-record. Each seed the freeze guard refuses for a defaulted turn (§11.2) costs its own wall again
— the baseline-7 record spent 12m33s re-recording two — and this smoke gives no rate to plan that
with. The record should carry the re-record cost as a line item rather than inside this bracket.

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
6. **No measurement.** Five seeds, 18 meetings, 7 ejections. Every cell above says so where it
   appears, and **no pre-registered bar is declared met or missed on five seeds.**
7. **The guard-redirect provenance marker is UNEXERCISED** on these bytes — zero ballots were
   redirected (§11.1 row 4), so that repair is neither confirmed nor contradicted here.
8. **The defaulted-turn rate is NOT priced.** Two five-seed samples produced 1 and 0 defaults over
   204 and 176 calls (§11.2). That is two observations, not a rate, and §12.2's bracket deliberately
   excludes any re-record cost derived from it.

## 14. The criteria, quoted VERBATIM and read one by one

`audits/audit-phase-21-preregistration.md` §9.2 is the abandon-criteria section and is quoted in
full. **The counterfactual publishes no abandon-criteria section of its own**: its §9 tripwire
CANDIDATES were dispositioned into the pre-registration's §8.1, which is where they are read, and
its §11.1 refusals are properties of the instrument rather than criteria for a run.

| § 9.2 criterion, verbatim | reading on this run | verdict |
|---|---|---|
| "a `scripts/validity_gate.py` FAIL on any leg" | one leg, all ten checks PASS (§6.1) | **NOT MET** |
| "a seed whose opening defaults (the `(deadline_default)` watch item)" | **the closest call on the page, and it is NOT met.** The criterion's subject is an OPENING, and `lost_openings 0 (defaults 1)`: no opening defaulted. One `opt_in` speech turn on seed 26 did, and its `failed_call` row carries `error_type == "deadline_default"` (§11.2). The criterion as written does not reach a non-opening turn, and this report records that rather than stretching it | **NOT MET — and the watch item FIRED; see §11.2 and §16** |
| "a guard trip" | no guard fired on this run: the wrapper's four preflights passed on the sanctioned slate and refused every deviation, and the ON-recording reader's four refusals (counterfactual §11.1) all passed. `check_replay_provenance` is **not in this wrapper's path at all**, so it could not fire — and driven by hand against these bytes it REFUSES seed 26 (§11.2). Stated plainly: no guard tripped, and a guard the record runs would have | **NOT MET** |
| "a lever-stamp mismatch between the recorded snapshot and the declared slate, compared through `orchestrator.replay.substrate_slate_mismatches` and **never re-derived**" | `substrate_slate_mismatches(['reporter_reasoning','corroboration_discipline','testimony_shapes'])` → `[]`, and `substrate_stamp_mismatches` empty on each of the five recorded stamps (§7) | **NOT MET** |
| "any of the seven §8.1 tripwires failing **its predicate** — the sample-local criterion in §8.1's third column, evaluated over whatever the run actually recorded. A denominator smaller than baseline 8's is expected at the smoke and is NOT a trip." | all seven PASS (§15); the reader exits 0 and `payload["stopped_cells"]` is empty | **NOT MET** |

**Classes this run observed that no criterion names.** Five, recorded in the memo's own words rather
than stretched to fit: the `at_body` line's 50% impostor share (§9.2); the first spoken `saw_kill`
and its ballot interaction (§8.4); **what the table did with those two accounts — both true, neither
convicting, one of them getting the truthful witness ejected** (§8.5); the like-for-like/all-games
denominator disagreement (§12.1); and **the non-opening defaulted turn and its `deadline_default`
label** (§11.2). **No §9.2 criterion names any of these classes verbatim, and this report invents
none.** The precedent for saying so in those words is `audits/audit-phase-20-smoke.md` §12.

### 14.1 The contract's own DoD item that CANNOT be ticked

The ratified §9.2 criteria are one surface; the task contract's Definition of done is another, and
they disagree here. `tasks/phase-21.md`:6868 requires:

> no recorded failed-call row carries `error_type == "deadline_default"` under either shape, and the
> recorder's own summary counters for lost openings and vote defaults are quoted

**That item is NOT SATISFIED on these bytes**, and this report marks it so rather than reading it
generously. The scan was performed and the counters are quoted; the stated result is not what was
observed. The row, verbatim from the recorded bytes:

```
game_id     headless-seed-26          meeting_id  headless-seed-26:meeting-1    tick 11
error_type  deadline_default          model       Qwen/Qwen3.6-27B              cost_usd 0.0
turn_kind   opt_in                    turn_index  5                             speaker  p-5
error_message
  opt_in turn (turn 5) defaulted (validation); p-5 submitted no turn
  [ValidationError: 1 validation error for MeetingTurn
   observations.1
     Input tag 'corroboration' found using 'type' does not match any of the expected tags:
     'saw_player', 'completed_task', 'found_body', 'saw_vent', 'saw…]
```

**The cause is established, not inferred**: a schema-validation failure that
`orchestrator/game.py`:2486-2508 (`_record_deadline_defaults`) stamps `deadline_default` on both
its branches (:2543 burned-generation, :2557 zero-spend marker) BY DOCUMENTED DESIGN, with the
trigger kind named in `error_message` as its docstring prescribes — so the row is correctly recorded
and the DoD item's subject, `error_type`, reads exactly what the recorder contracts it to read
(§11.2). The one thing that is genuinely wrong is downstream of it: `meetings/manager.py`:209 mints
the husk's `"(missed deadline; no turn submitted)"` regardless of cause, and that is what §16
routes.

**What no criterion names.** §9.2's second criterion is *"a seed whose opening defaults (the
`(deadline_default)` watch item)"*, and its subject is an OPENING; the recorder's counters read
`lost_openings 0 (defaults 1)` and `vote_defaults 0 (must_vote 0)`. **This row is neither an opening
nor a vote.** No §9.2 criterion names that class verbatim, and this report invents none — the
precedent for saying exactly that is `audits/audit-phase-20-smoke.md` §12.

**So the two surfaces give two answers, and this report gives both.** Under the ratified §9.2 text
the criterion is NOT MET and the memo's own answer is GO. Under the parenthetical read as the
operative clause — the DoD item's shape — the run carries a `deadline_default` row and the call
would be ABANDON. **The memo governs where this report and it disagree, so the verdict is GO; the
choice between the two readings is the OWNER's at the gate**, and §16 carries the routing either
way.

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
| **T1** (never-worse bar + STOP) | `T-7` | the count is 0, whatever the denominator | **0/4 = 0.0000** `[ADV]` | **PASS** |
| **T2** (STOP) | `R-13` | every observed body-report opening gains the block — 100% of the observed denominator | **17/17 = 1.0000**; emergency openings that gained one = 0; byte-diff column 17/17, agrees | **PASS** |
| **T2** (STOP) | `R-14` | every observed non-reporter speech turn in a body-report meeting gains it — 100%, and no emergency-meeting prompt gains either | **78/78 = 1.0000**; emergency speech prompts that gained one = 0; byte-diff column 78/78, agrees | **PASS** |
| **T3** (STOP) | `R-15` | the count is 0, whatever the ballot denominator | **0/102 = 0.0000** | **PASS** |
| **T4** (STOP) | `T-6` | 100% of observed location accounts reach the map under ON (and the OFF reconstruction of the same run is strictly below it) | **130/130 = 1.0000** ON against **28/130 = 0.2154** OFF — strictly below, so the ordering clause bites rather than passing on the equality the owner ruled permissible | **PASS** |
| **T5** (never-worse bar + STOP) | `T-9a` | every observed CREW speech turn gains the ELICITATION block | **55/55 = 1.0000** | **PASS** |
| **T5** (never-worse bar + STOP) | `T-9b` | the count of IMPOSTOR speech prompts gaining an ELICITATION block is 0 | **0/29 = 0.0000**, with the role-blind public-transcript row present in impostor prompts and correctly EXCLUDED by construction (§8.4) | **PASS** |
| **T6** (STOP) | `C-9` | the observed share is ≥ 99% of ballots | **101/102 = 0.9902**; byte-diff column 101/102, agrees. The one ballot short is §8.1's own stated residue, which it rules context rather than a second criterion | **PASS** |
| **T7** (STOP) | `B-1m1` | the meeting-1 row count is identical between the run's own OFF and ON columns | **1425/73 = 19.5205 in both columns** | **PASS** |

**T6 is the row this run actually tested.** On the superseded first attempt `C-9` read 88/88 = 100%,
which passes a ≥ 99% floor without ever approaching it; here it reads 99.02% with one ballot in the
residue, so the predicate was exercised against a real margin rather than satisfied by construction.

**The population column binds neither run.** Every denominator here is smaller than baseline 8's —
17 openings against 620, 78 speech turns against 2,715, 102 ballots against 3,631, 130 location
accounts against 4,173 — and §8.1 ratifies that as expected and **NOT a trip**. Each row is judged
on its predicate; the baseline-8 figure appears in §8's tables as a reference and nowhere as a
criterion. **No tripwire is a graduating bar and none contributes to any verdict but this smoke's.**

## 16. The verdict, the bytes, and what happens next

**GO, with one watch item FIRED.** Ruled against `audits/audit-phase-21-preregistration.md` §9.2:
**no abandon criterion is met** (§14), all seven §8.1 tripwires PASS against their sample-local
predicates (§15), the validity gate PASSED on all ten checks with both reconstructions
byte-identical (§6), the recorded substrate stamp is the declared slate on all five seeds by both
registered comparisons (§7), no Wave-1 repair regressed (§11.1), and the committed record is
untouched (§6.3).

**The GO is not a clean bill, and one contract item cannot be ticked.** One seed carries a defaulted
turn whose `failed_call` row the corpus freeze guard refuses (§11.2). §9.2's criterion does not reach
it — its subject is an OPENING and no opening defaulted — so the memo's own answer is GO. But the
task contract's DoD item at `tasks/phase-21.md`:6868 requires that **no** recorded failed-call row
carry `error_type == "deadline_default"` under either shape, and **that item is NOT SATISFIED**
(§14.1). The two surfaces disagree; the memo governs, so the verdict stands, and **the call under the
parenthetical reading is the owner's at the gate.** Items 1 and 2 below are ROUTED to 21.24 with
their homes, the first as a precondition the record cannot start without.

**The adopting record's window opens on `14854a06`**, this report's certified source state, and the
freeze governs from the pre-registration's own merge point. Any merge into `agents/`, `meetings/`,
`observation/`, `orchestrator/` or `agents/strategic/prompts/` between this report and the record
reopens it.

**One such merge is already in flight, and it is named here rather than left to be discovered.**
PR #424 (`phase-21-ledger-grounding`, OWNER-GATED and open at this writing) edits
`meetings/corroboration.py`, `meetings/manager.py`, `meetings/transcript.py` and
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2` — two frozen directories — so **by this
section's own rule it REOPENS this smoke's window the moment it merges.** That is not a formality
for these bytes: under #424 the lever-ON tripwire reader can no longer walk this preserved
recording, because the changed ballot block stops matching what was recorded — seeds 17 and 46 lose
**7 of 16** and **6 of 13** recorded ballot prompts — so the seven tripwires could not simply be
re-read on the same bytes at `$0`. The fork at 21.24's re-anchor is therefore between a short
re-smoke on the merged head and accepting this GO on the OFF-byte-identity argument. **That choice
is the owner's**; this report neither makes it nor prices it, and it applies equally to item 2's
`meetings/` fix below.

**The bytes are PRESERVED, not deleted** — both attempts, at stable absolute paths:

```
/Users/danielkeinan/ailibi-smoke-21-23/9p2i                              7,330,736 bytes over 8 files
  — the CONTRACTED run, and the only one this report reads
/Users/danielkeinan/ailibi-smoke-21-23/9p2i-attempt-1-default-retry-budget   6,305,418 bytes over 8 files
  — superseded (§2.0); quoted nowhere as a cell
```

so a routed repair can be re-measured on the same bytes at `$0` without re-recording a seed. The
like-for-like OFF reference this report reads against is preserved beside them at
`/Users/danielkeinan/ailibi-smoke-21-23/committed-same-five` (five copies of committed replays,
read-only; nothing under `replays/` moved).

**Six items the record inherits** — the first two ROUTED with homes, the rest observed, none of them a STOP and none of them blocking:

1. **ROUTED TO 21.24, AS A PRECONDITION — the guard/criterion asymmetry must be reconciled before
   the record starts.** `check_replay_provenance` (`scripts/record_ml_corpus.sh`, the freeze-guard
   branch) refuses **ANY** `deadline_default` row and says `re-record the seed`; the ratified §9.2
   criterion and the validity gate name only **an OPENING** (the gate names nothing at all). On
   these bytes those two answers differ, and on a 300-game record they will differ repeatedly. **The
   record cannot start until the owner reconciles them**, in one of two directions — narrow the
   guard to the memo's shape (refuse only a defaulted opening, or only a wall-clock miss), or widen
   the memo to the guard's (make any `deadline_default` row an abandon criterion, with the
   re-record cost priced in). Either is an owner decision, not an operator one. **Priced as a 21.24
   precondition** beside the two §9.1 preconditions this task discharged. Its blast radius is the
   corpus legs only: `scripts/refresh_samples.sh` contains no `deadline_default` check
   (`grep -c` → 0), so the two samples legs would carry such a husk into the committed record
   unnoticed.
2. **ROUTED TO 21.24, AS A LEGIBILITY FIX BEFORE THE RECORD — the husk's `free_text`, and NOT
   `error_type`.** The shared `error_type` is the DESIGN, not a mislabel:
   `orchestrator/game.py`:2486-2508 documents one `error_type="deadline_default"` for both trigger
   kinds with the trigger named in `error_message`, both branches (:2543, :2557) stamp it as
   documented, and this row honours it — its `error_message` names the validation trigger (§11.2).
   What is neither documented nor recoverable is the husk itself: `meetings/manager.py`:209 mints
   `"(missed deadline; no turn submitted)"` as the `free_text` of EVERY default whatever its cause,
   so a schema slip leaves a transcript row asserting a deadline miss that never occurred — a false
   sentence inside the corpus, which is the surface a later model reads. **Fix that string before
   21.24**, so the record's own watch item means what it says; `error_type` needs no fix and every
   consumer wanting the trigger reads `error_message`. **It lives in `meetings/`, a FROZEN
   directory (§0), so landing it reopens this smoke's window exactly as PR #424 does — an OWNER
   decision before 21.24, not an operator one**, and it belongs in one window with item 1's
   reconciliation rather than as a second reopen. The remedy for the seed itself is unchanged and
   is the recorder's own (`re-record the seed`; the precedent is baseline 7's two seeds in 12m33s),
   and that cost sits outside §12.2's bracket.
3. **What the table did with the two spoken kills** (§8.5). Both accounts were true, neither
   convicted, and one ended with the truthful crew witness ejected. Two cases decide nothing; they
   are the first live evidence on a question the counterfactual declares unreachable offline, and
   21.24's audit should read this cell deliberately rather than incidentally.
4. **The first spoken `saw_kill` and its ballot interaction** (§8.4). Both are registered — the
   public-transcript row by `test_a_spoken_kill_reaches_every_later_speaker` and the ballot fork by
   Errata E.1 — and 21.24's audit should report the interaction's realized size rather than E.1's
   synthetic per-row arithmetic.
5. **The seed slate is not a representative token sample** (§12.1). The projection's low end is the
   all-games cross-check for that reason, and the record should re-derive its own ratio per leg.
6. **The `at_body` line reached an impostor in 2 of 4 firings** (§9.2), reproducing the
   counterfactual's 49.0% co-discoverer hazard at n = 4. It is observed and gated by nothing.

### 16.1 The project gate — run COMPLETE, nothing skipped

`bash scripts/check.sh` — the full command, **no `AILIBI_SKIP_FRONTEND`**, from the worktree root:

```
$ bash scripts/check.sh; echo EXIT=$?
…
Contracts: 4 kept, 0 broken.
Task docs validation passed: 390 tasks and 390 prompts.
All 390 prompts are in sync.
Success: no issues found in 377 source files          (mypy)
=========== 6013 passed, 20 skipped, 3 xfailed in 126.78s (0:02:06) ============
Running frontend checks...
  eslint .                                   — clean
  tsc --noEmit (+ tsconfig.node.json, e2e/tsconfig.json)  — clean
  vitest run   — Test Files 9 passed (9);  Tests 440 passed (440)
  vite build   — ✓ built in 231ms
EXIT=0
```

The frontend dependencies were installed in this worktree (`cd frontend && npm ci`) specifically so
this gate could run unskipped; the earlier declaration of a skipped frontend leg is superseded.
Nothing in this PR touches `frontend/`, and the four frontend legs pass anyway.

**The one exception the contract asks be recorded, and it did not occur:**
`tests/training/test_es.py::test_evolve_is_deterministic_and_hash_pinned` is a Linux-CI hash pin
known to fail on this Mac on bare `main`; in this worktree it **passed**, so there is no known local
failure to report and none is claimed. Had it failed it would have been reported as the known local
failure it is and never as a smoke finding.

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

### 17.4 The operating-data reader — the §11.2 watch scan and the §12 token source

Stdlib only. Reproduces §5's per-seed table, §11.2's watch-item scan and §12's token figures:

```bash
AILIBI_OPDATA_DIR=/Users/danielkeinan/ailibi-smoke-21-23/9p2i uv run python opdata.py
# the like-for-like OFF column of §12.1:
AILIBI_OPDATA_DIR=replays/samples/9p2i AILIBI_OPDATA_SEEDS=4,17,19,26,46 uv run python opdata.py
```

```python
"""Operating data over a recorded set: calls, tokens, cost, meetings, failed calls.

Also the hand-scanned watch item: any failed_call row of any kind, and the
`(deadline_default)` sentinel under either shape.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

TARGET = Path(os.environ.get("AILIBI_OPDATA_DIR", os.environ.get("SMOKE_DIR", ".")))
ONLY = {
    int(token)
    for token in os.environ.get("AILIBI_OPDATA_SEEDS", "").split(",")
    if token.strip()
}


def main() -> int:
    per_seed: dict[int, dict] = {}
    failed_kinds: Counter[str] = Counter()
    deadline_rows = 0
    for path in sorted(TARGET.glob("replay-seed-*.jsonl")):
        seed = int(path.stem.rsplit("-", 1)[1])
        if ONLY and seed not in ONLY:
            continue
        info = {
            "meetings": 0,
            "ejections": 0,
            "calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0.0,
            "ending": None,
            "winner": None,
            "failed_calls": 0,
        }
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("kind") == "game_over":
                info["ending"] = row.get("end_reason") or row.get("reason")
                info["winner"] = row.get("winner")
            if row.get("kind") == "failed_call":
                info["failed_calls"] += 1
                failed_kinds[str(row.get("error_type"))] += 1
                if row.get("error_type") == "deadline_default":
                    deadline_rows += 1
                if row.get("model") == "(deadline_default)":
                    deadline_rows += 1
                continue
            if row.get("kind") != "meeting":
                continue
            info["meetings"] += 1
            if row.get("ejected_player_id"):
                info["ejections"] += 1
            for call in row.get("llm_calls") or []:
                info["calls"] += 1
                info["input_tokens"] += int(call.get("input_tokens") or 0)
                info["output_tokens"] += int(call.get("output_tokens") or 0)
                info["cost"] += float(call.get("cost_usd") or 0.0)
                if call.get("model") == "(deadline_default)":
                    deadline_rows += 1
        per_seed[seed] = info

    print(f"set={TARGET}")
    print("seed meetings ejections calls in_tokens out_tokens tokens cost ending winner")
    tot = Counter()
    for seed, info in sorted(per_seed.items()):
        tokens = info["input_tokens"] + info["output_tokens"]
        print(
            f"{seed} {info['meetings']} {info['ejections']} {info['calls']} "
            f"{info['input_tokens']} {info['output_tokens']} {tokens} "
            f"{info['cost']:.4f} {info['ending']} {info['winner']}"
        )
        for key in ("meetings", "ejections", "calls", "input_tokens", "output_tokens"):
            tot[key] += info[key]
        tot["failed_calls"] += info["failed_calls"]
    tokens = tot["input_tokens"] + tot["output_tokens"]
    print()
    print(
        f"TOTAL meetings={tot['meetings']} ejections={tot['ejections']} "
        f"calls={tot['calls']} input={tot['input_tokens']} "
        f"output={tot['output_tokens']} tokens={tokens}"
    )
    if tot["meetings"]:
        print(f"tokens/meeting = {tokens / tot['meetings']:.1f}")
        print(f"calls/meeting  = {tot['calls'] / tot['meetings']:.2f}")
    if tot["calls"]:
        print(f"tokens/call    = {tokens / tot['calls']:.1f}")
    print(f"failed_call rows by error_type: {dict(failed_kinds) or '{} (none recorded)'}")
    print(f"deadline_default rows (EITHER shape): {deadline_rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

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

### 17.6 The freeze-guard branch, driven by hand (§11.2)

`scripts/refresh_samples.sh` never calls `check_replay_provenance`, so the smoke's own run could not
trip it. This asks the same question the corpus path asks — does any recorded `failed_call` row
carry `error_type == "deadline_default"` — over the smoke bytes, so "the record's guard would refuse
this seed" is demonstrated rather than asserted. Its message is the committed guard's own, copied
verbatim so the two cannot drift apart in this report's telling.

```python
for path in sorted(TARGET.glob("replay-seed-*.jsonl")):
    defaulted = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("kind") == "failed_call" and row.get("error_type") == "deadline_default":
            defaulted += 1
    if defaulted:
        bad.append(
            f"{path.name}: {defaulted} deadline_default failed-call row(s) — the "
            "turn(s) were DEFAULTED, so the transcript carries a fallback husk "
            "rather than model output; re-record the seed"
        )
```

### 17.7 The spoken-kill outcome read (§8.5)

Roles come from the committed `eval.validity.roles_by_seed` re-seeding, never from the replay —
roles are firewalled out of the JSONL — so "the account was true" is checked against ground truth
rather than against the transcript that made the claim. Run under Shell A:

```bash
SMOKE_DIR=/Users/danielkeinan/ailibi-smoke-21-23/9p2i uv run python kill_outcomes.py
```

```python
"""What happened at the two meetings where a crew speaker filed a spoken saw_kill.

Roles come from the committed re-seeding (eval.validity.roles_by_seed), never from
the replay: roles are firewalled out of the JSONL.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AILIBI_REPO_ROOT", os.getcwd()))
sys.path.insert(0, str(ROOT))

from eval.validity import resolve_roster_knobs, roles_by_seed  # noqa: E402

TARGET = Path(os.environ["SMOKE_DIR"])
players, impostors, tasks = resolve_roster_knobs(TARGET)
roles = roles_by_seed(
    TARGET, num_players=players, num_impostors=impostors, tasks_per_crewmate=tasks
)

for path in sorted(TARGET.glob("replay-seed-*.jsonl")):
    seed = int(path.stem.rsplit("-", 1)[1])
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("kind") != "meeting":
            continue
        for turn in (row.get("transcript") or {}).get("turns") or []:
            for obs in turn.get("observations") or []:
                if obs.get("type") != "saw_kill":
                    continue
                speaker = str(turn["speaker"])
                named = str(obs["subject"])
                ejected = row.get("ejected_player_id")
                print(f"seed {seed} {row['meeting_id']}")
                print(f"  speaker {speaker} = {roles[seed].get(speaker)}  (reporter: {row.get('triggered_by')})")
                print(f"  named   {named} = {roles[seed].get(named)}")
                print(f"  outcome {row.get('outcome')}  ejected {ejected} = {roles[seed].get(str(ejected)) if ejected else '-'}")
                tally = {}
                for ballot in row.get("ballots") or []:
                    tally[str(ballot.get("target"))] = tally.get(str(ballot.get("target")), 0) + 1
                print(f"  ballot tally {tally}")
```

### 17.8 The `at_body` recipient read (§9.2)

The same roster/roles resolution, over every recorded prompt carrying the `at_body` sentence. It is
the only cell in this report that reads a per-speaker line of the reporter block against ground
truth, and it is what makes §9.2's watch reading a measurement rather than an inference. Run under
Shell A:

```bash
SMOKE_DIR=/Users/danielkeinan/ailibi-smoke-21-23/9p2i uv run python at_body.py
```

```python
"""Who received the reporter block's `at_body` line, and what role were they.

A-38's proposed widening (extend exculpatory framing to non-reporter
co-discoverers) was REJECTED on measurement. The shipped block frames only the
reporter; the one other per-speaker line it renders is the neutral self-addressed
`at_body` sentence. This names every seat that received it and its recorded role,
so the smoke's sharpest watch cell is measured rather than assumed.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("AILIBI_REPO_ROOT", os.getcwd()))
sys.path.insert(0, str(ROOT))

from eval.validity import resolve_roster_knobs, roles_by_seed  # noqa: E402

TARGET = Path(os.environ["SMOKE_DIR"])
AT_BODY = "Your own record shows you saw the body when it was reported."
REPORTER_LINE = "` reported the body that opened this meeting."


def main() -> int:
    players, impostors, tasks = resolve_roster_knobs(TARGET)
    roles_all = roles_by_seed(
        TARGET,
        num_players=players,
        num_impostors=impostors,
        tasks_per_crewmate=tasks,
    )
    rows: list[tuple[int, str, str]] = []
    for path in sorted(TARGET.glob("replay-seed-*.jsonl")):
        seed = int(path.stem.rsplit("-", 1)[1])
        roles = roles_all[seed]
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("kind") != "meeting":
                continue
            for call in row.get("llm_calls") or []:
                if AT_BODY not in call["prompt"]:
                    continue
                agent = str(call.get("agent_id"))
                rows.append((seed, agent, roles.get(agent, "?")))
    impostor = sum(1 for _s, _a, role in rows if role == "IMPOSTOR")
    print(f"prompts carrying the at_body line: {len(rows)}")
    for seed, agent, role in rows:
        print(f"  seed {seed}: {agent} = {role}")
    if rows:
        print(f"IMPOSTOR share: {impostor}/{len(rows)} = {impostor / len(rows):.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Every reader in this appendix was re-run against the preserved bytes after the report was written,
and each reproduces the numbers it is cited for to the digit.**

---

## 18 — Post-#424 re-smoke, 2026-09-03

**ADDITIVE. Nothing above this line is rewritten.** §§0–17 stand exactly as merged: they are the
record of the five-seed run certified at `14854a06`, and every cell in them still reads what it read.
This section is a SECOND run on a SECOND source state, and it says so in every place the two could be
confused.

### 18.0 The verdict, in one line

**GO on the reopened window — and this time the watch item did NOT fire.** Two live seeds (17 and 46)
recorded at the ratified Wave-2 slate on the merged head; the validity gate PASSED on all ten checks
with both reconstructions byte-identical; **all seven §8.1 tripwires PASS against their own
sample-local predicates** (`verdict: every GATED predicate PASSES on these bytes`, the reader exiting
0 with `stopped_cells` empty); **no `audits/audit-phase-21-preregistration.md` §9.2 abandon criterion
is met**, read one by one in §18.6; the committed record untouched; and **zero recorded `failed_call`
rows of any kind, so `deadline_default` reads 0 under either shape** (§18.5).

**Source state this section certifies: `44f0a28c`** — `origin/main` at this writing, carrying PR #425
(`e2b252db`, this report) and PR #424 (`ffaf9991`, the ledger's grounding semantics). The freeze rule
in §0 and §16 governs from here unchanged: any further merge into `agents/`, `meetings/`,
`observation/`, `orchestrator/` or `agents/strategic/prompts/` reopens the window again.

**The MANIFEST's `git_sha` is `44f0a28c` too**, and there is nothing to reconcile this time: the
recording ran from a worktree whose only untracked content is a gitignored `scratchpad/`, so the
stamp and the certified state are the same commit. (§0's reconciliation paragraph for `3fd12a03`
belongs to the five-seed run and is untouched.)

### 18.1 Why the window reopened, and why these two seeds

§16 states the rule and named the merge in flight. It landed. **Exactly four files under the frozen
directories moved between the certified state and this head, and all four are #424's:**

```
$ git diff --stat 14854a06..44f0a28c -- agents meetings observation orchestrator
 agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2   |   2 +-
 meetings/corroboration.py                             | 241 ++++++++++++++++++---
 meetings/manager.py                                   |  21 +-
 meetings/transcript.py                                | 104 ++++++++-
 4 files changed, 323 insertions(+), 45 deletions(-)
```

**Seeds 17 and 46 are the two §16 names**, and they are drawn for the reason §16 gives rather than
re-stratified: they are the seeds whose recorded ballots the lever-ON reader can no longer reconstruct
under #424 (7 of 16 and 6 of 13 recorded ballot prompts), so they are precisely the bytes the
reopened window costs. **This is a RE-SMOKE of a named consequence, not a second seed draw**: §3's
stratification is the five-seed run's and is not re-derived here, and no cell below is compared to a
stratum count.

`scripts/counterfactual_phase21.py` also moved by 21 lines over the same range — #424's re-pin of
`COMMITTED_CORROBORATION_CELLS`. **The reader run below is therefore the merged head's reader**, not
the one §15 ran.

### 18.2 The recorded configuration — the Step-3 block, verbatim

The same block §2 publishes, with one path changed. The operator's `FEATHERLESS_API_KEY` is sourced
from the gitignored `.env` at the main checkout and is **not reproduced here, in the PR, or in any log
excerpt in this record**; the wrapper prints an eight-character prefix at `scripts/refresh_samples.sh`:551
and this section keeps none of it.

```
AILIBI_LLM_PROVIDER=featherless
AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
AILIBI_NUM_PLAYERS=9  AILIBI_NUM_IMPOSTORS=2  AILIBI_TASKS_PER_CREWMATE=2
AILIBI_SAMPLE_DIR=/Users/danielkeinan/ailibi-smoke-21-23/post-424-9p2i   # absolute, OUTSIDE the repo
AILIBI_REFRESH_WORKERS=2
AILIBI_SEED_MAX_ATTEMPTS=8
AILIBI_REPORTER_REASONING=1
AILIBI_CORROBORATION_DISCIPLINE=1
AILIBI_TESTIMONY_SHAPES=1
# AILIBI_IMPOSTOR_ROLL_CALL — unset, in this and in every later gate/instrument shell
```

**The two shells are §2.1's, unchanged.** Shell A carries the three Wave-2 exports and is the only
shell that touched the new `$SMOKE_DIR`: the recording, the validity gate, both reconstructions and the
tripwire reader. Shell B carries no lever export at all and is the only shell that ran the bare
committed-set gate. `api/replay_loader.py`:655 is still the mechanism that makes crossing them a
refusal rather than a wrong number, and §18.4 records the crossing that was actually run.

**Two wrapper preflights were run before any seed staged**, and `/Users/danielkeinan/ailibi-smoke-21-23`
gained nothing from either. The sanctioned preview — exported AND declared — echoed the two overridden
knobs, which is what attests them (no recorded byte carries either; §12's basis note applies unchanged):

```
[dry-run] seeds: 17,46
[dry-run] sample dir: /Users/danielkeinan/ailibi-smoke-21-23/post-424-9p2i
[dry-run] substrate flags: expected levers ON = reporter_reasoning,corroboration_discipline,
          testimony_shapes; every other live toggle OFF; the graduated levers unconditional ON
[dry-run] seed workers: 2 parallel …
[dry-run] seed crash-retry: up to 8 attempt(s) per seed on a transport/crash error
Substrate slate OK: expected levers ON = reporter_reasoning,corroboration_discipline,testimony_shapes;
every other live toggle OFF; the graduated levers unconditional ON.
```

and the HALF-slate direction — one lever removed from the export, the whole slate still declared —
refuses and exits 1:

```
Error: the live substrate-lever slate does not match --expect-levers.
       Expected ON: reporter_reasoning,corroboration_discipline,testimony_shapes
       Mismatch: corroboration_discipline must be ON but the live slate reads OFF
       (AILIBI_CORROBORATION_DISCIPLINE)
       Export exactly the levers you named and unset every other AILIBI_*
       lever export, then re-run. Nothing was staged.
```

The real run's own preflight block, before any seed staged:

```
Using Featherless API key prefix: <redacted — the wrapper prints 8 characters; this record keeps none>
Locked substrate OK: AILIBI_PROMPT_SET=qwen3_6_27b.
Model-set coupling OK: qwen3_6_27b on Qwen/Qwen3.6-27B.
Model registry OK: Qwen/Qwen3.6-27B is registered in the production client.
Substrate slate OK: expected levers ON = reporter_reasoning,corroboration_discipline,testimony_shapes;
every other live toggle OFF; the graduated levers unconditional ON.
```

**Both seeds carry the four COMPOSITE prompt-version strings**, which is §4.1's fix confirmed a second
time on live bytes at the merged head — the MANIFEST rows read
`accusation_round.qwen3_6_27b.v5.reporter_reasoning+accusation_round.qwen3_6_27b.v5.testimony_shapes,
crewmate_report.qwen3_6_27b.v5.reporter_reasoning+crewmate_report.qwen3_6_27b.v5.testimony_shapes,
impostor_report.qwen3_6_27b.v5,
vote_ballot.qwen3_6_27b.v5.corroboration_discipline+vote_ballot.qwen3_6_27b.v5.testimony_shapes` for
seeds 17 and 46 alike, with `git_sha` `44f0a28c` and `cost_usd` `0.0000` on both.

### 18.3 The two seeds, as recorded

| seed | wall (serial) | meetings | ejections | ending | winner | calls | tokens | cost |
|---|---|---|---|---|---|---|---|---|
| 17 | 576 s | 4 | 1 | **CREWMATE_TASKS** | CREWMATES | 42 | 210,078 | $0.0000 |
| 46 | 573 s | 5 | 2 | CREWMATE_EJECT | CREWMATES | 44 | 233,098 | $0.0000 |
| **both** | **9m36s refresh / 9m38s operator wall** | **9** | **3** | — | CREW 2 / IMP 0 | **86** | **443,176** | **$0.0000** |

```
9 meetings | 424,945 input + 18,231 output = 443,176 tokens | $0.0000
tokens/call    5,153.2
calls/meeting     9.56
tokens/meeting 49,241.8
```

Both seeds ran concurrently on the two workers from the first second, so the leg's wall is the slower
seed: 1,149 s of serial seed work across 576 s of wall on two workers = **99.7% occupancy**. Total
operator wall **9m38s** (07:23:58Z → 07:33:36Z), the wrapper's own `Refresh complete in 9m36s`.

**Retries, transport blips, worker diagnostics: none**, and no seed consumed a second attempt of its
budget of 8. As in §12, that reading comes from the operator's shell and the wrapper's log rather than
from the preserved bytes, which stamp no attempt count.

The recorder's own summary counters, from the whole-set eval-report rebuild:

```
lost_openings 0 (defaults 0) | vote_defaults 0 (must_vote 0) | ballot_redirects 1 (eject 1)
meeting_rate 1.00 (9 meetings) | ejection_accuracy 1.0000 (3/3)
```

**Two things these two seeds exercise that the five-seed run could not**, both stated as observations
and gated by nothing:

* **a task-completion ending.** Seed 17 ends `CREWMATE_TASKS`. §5.1 and §13 item 4 record that path as
  UNTESTED at 21.14 and at the certified run, and the committed census carries none either. It is
  exercised here. No criterion names it and none is invented.
* **the guard-redirect provenance marker, row 4 of §11.1, is EXERCISED and green.** The certified run
  marked it UNEXERCISED because no ballot was redirected. Here one was, and it carries machine-readable
  provenance rather than only a display string: **43 ballots, 1 display-marked (`under_gate_redirect`),
  1 machine row (`guard_redirected_from='p-5'`, seed 17 meeting-1, voter p-4 → p-8), 0 missing.**

**A third live spoken `saw_kill`, and it behaves like the first two.** §8.4's shape fires again on
these bytes — the testimony census reads `saw_kill: 1` under ON against 0 under OFF — and §17.7's
reader, run under Shell A with roles from the committed re-seeding, gives its outcome:

```
seed 17 headless-seed-17:meeting-3  turn_index 0
  observation {"room": "EAST_HALL", "subject": "p-4", "tick": 29, "type": "saw_kill"}
  speaker p-1 = CREWMATE  (reporter: p-1)
  named   p-4 = IMPOSTOR
  outcome SKIPPED  ejected None = -
  ballot tally {'p-4': 1, 'p-1': 1, 'SKIP': 1}
```

**True, naming a real impostor, and not converted** — three for three across the two runs, which is
§16 item 3's cell gaining a third case. Three cases still decide nothing and no criterion names them;
they are carried forward for 21.24's audit exactly as §16 routes them.

### 18.4 The gate, the stamp, and the two shells

**`scripts/validity_gate.py`, Shell A, all ten checks:**

```
uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost
```

```
Validity gate over /Users/danielkeinan/ailibi-smoke-21-23/post-424-9p2i (2 games):
  [PASS] all_games_reach_game_over: 2/2 games reached a reconstructed game_over with a consistent win condition
  [PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 9 resolved meetings; 0 unresolved
  [PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 9 (want 0)
  [PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
  [PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
  [PASS] no_betrayal_ballots_or_accusations: 0 teammate-betrayal ballots/accusations over 43 multi-impostor ballots (want 0)
  [PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 157 rendered crew suspicions (want 0)
  [PASS] no_dangling_primary_reason_id: 0 dangling primary_reason_id over 43 ballots (want 0)
  [PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions, substrate stamped exact on 2 games
  [PASS] byte_identical_reconstruction: 0 samples drifted from byte-identical reconstruction (want 0)
Validity gate PASSED (all checks green).
```

`bash scripts/verify_samples.sh "$SMOKE_DIR"` in that same shell, twice: `All 2 samples verified clean.`
both times.

**The recorded substrate stamp, read off the two `game_over` rows** rather than a live snapshot:

```
seeds with a game_over stamp: [17, 46]
live SUBSTRATE_FLAG_KEYS: 25
distinct recorded stamps: 1   ->  keys: 25   ON: 24   OFF: ['impostor_roll_call']
substrate_stamp_mismatches(stamp)  ->  differing=[] unknown=[]   (each of the two)
retired_levers_stamped_off(stamp)  ->  []                        (each of the two)
substrate_slate_mismatches(['reporter_reasoning','corroboration_discipline','testimony_shapes']) -> []
```

**Shell B — the bare committed-set gate**, run with no lever export at all:

```
=== verifying replays/samples/4p1i/ ===   All 50 samples verified clean.
=== verifying replays/samples/9p2i/ ===   All 50 samples verified clean.
$ git status --porcelain replays/
(empty)
```

`scripts/counterfactual_phase21.py --sets all` also ran in that bare shell and exited 0, and its
`corroboration_pins` block reads **#424's four re-pinned cells at this head**, `"checked": true`:

```
{'checked': True, 'measured': {'accused_without_a_first_hand_source': [460, 1525],
 'ejected_without_a_first_hand_source': [10, 425], 'ejected_on_an_answering_turn': [33, 429],
 'ejected_with_a_walkable_pair': [79, 429]}}
```

### 18.5 The watch item, scanned by hand — and it did NOT fire

The validity gate still has no `deadline_default` check at all, so the scan is by hand, over the
recorded bytes, with §17.4's reader:

```
failed_call rows by error_type: {} (none recorded)
deadline_default rows (EITHER shape): 0
```

and the recorder's own counters beside it: **`lost_openings 0 (defaults 0)`** and
**`vote_defaults 0 (must_vote 0)`**. There is no row to quote, because there is no row.

**The corpus freeze guard would refuse nothing here, and that is demonstrated in BOTH directions**
rather than asserted. §17.6's branch, driven by hand over the two byte sets:

```
$ SMOKE_DIR=…/post-424-9p2i   → check_replay_provenance (deadline_default branch): 0 violations, exit 0
$ SMOKE_DIR=…/9p2i            → check_replay_provenance (deadline_default branch): 1 violation(s) —
    replay-seed-26.jsonl: 1 deadline_default failed-call row(s) — the turn(s) were DEFAULTED, so the
    transcript carries a fallback husk rather than model output; re-record the seed, exit 1
```

**The second run is the planted case for the first**: the same scan over the certified bytes still
bites on seed 26, so the 0 above is a scan that could have failed and did not — not a scan that cannot
fail (AGENTS.md craft rule 2).

**The contract's DoD item IS SATISFIED on these bytes.** §14.1 marks it NOT SATISFIED for the
five-seed run and that verdict is untouched. The item — the watch-item line §14.1 cites at
`tasks/phase-21.md`:6868, which sits at `:6906` at this head after the phase doc took the two
merge-reality paragraphs — requires:

> no recorded failed-call row carries `error_type == "deadline_default"` under either shape, and the
> recorder's own summary counters for lost openings and vote defaults are quoted

Both halves hold here: zero rows under either shape, and the two counters are quoted above. **Two
seeds do not price a rate and this section gives none** — the observations now stand at 1 default in
204 recorded calls (the certified run), 0 in 176 (the superseded attempt, §2.0) and 0 in 86 (here).
**Nothing about §16 items 1 and 2 changes:** the guard/criterion asymmetry and the husk's `free_text`
wording are defects in the machinery, not facts about a seed, and both remain ROUTED to 21.24 exactly
as §16 routes them. A clean two-seed run does not discharge either.

### 18.6 The seven tripwires, and the §9.2 criteria

**The reader, run under the SAME lever-ON shell the recording was made in, after the validity gate**,
exactly as the contract names it:

```bash
uv run python scripts/counterfactual_phase21.py --recording "$SMOKE_DIR" --recorded-slate on --json
```

It exited **0**, `payload["stopped_cells"]` is **`[]`**, `payload["pooled_is_informational"]` is
**true**, and the same command without `--json` ends with
**`verdict: every GATED predicate PASSES on these bytes`**. The recorded slate the reader checked
against its own stamp is `on`; the pooled block is the union over one recording and decides nothing.

| tripwire | cell | the ratified SAMPLE-LOCAL predicate | reading on these bytes | verdict |
|---|---|---|---|---|
| **T1** (never-worse bar + STOP) | `T-7` | the count is 0, whatever the denominator | **0/2 = 0.0000** `[ADV]` | **PASS** |
| **T2** (STOP) | `R-13` | every observed body-report opening gains the block — 100% of the observed denominator | **9/9 = 1.0000**; emergency openings that gained one = 0; byte-diff column 9/9, agrees | **PASS** |
| **T2** (STOP) | `R-14` | every observed non-reporter speech turn in a body-report meeting gains it — 100%, and no emergency-meeting prompt gains either | **34/34 = 1.0000**; emergency speech prompts that gained one = 0; byte-diff column 34/34, agrees | **PASS** |
| **T3** (STOP) | `R-15` | the count is 0, whatever the ballot denominator | **0/43 = 0.0000** | **PASS** |
| **T4** (STOP) | `T-6` | 100% of observed location accounts reach the map under ON (and the OFF reconstruction of the same run is strictly below it) | **50/50 = 1.0000** ON against **14/50 = 0.2800** OFF — strictly below, so the ordering clause bites rather than passing on the equality the owner ruled permissible | **PASS** |
| **T5** (never-worse bar + STOP) | `T-9a` | every observed CREW speech turn gains the ELICITATION block | **22/22 = 1.0000** | **PASS** |
| **T5** (never-worse bar + STOP) | `T-9b` | the count of IMPOSTOR speech prompts gaining an ELICITATION block is 0 | **0/12 = 0.0000** `[ADV]` | **PASS** |
| **T6** (STOP) | `C-9` | the observed share is ≥ 99% of ballots | **43/43 = 1.0000** — no residue on these bytes; byte-diff column 43/43, agrees | **PASS** |
| **T7** (STOP) | `B-1m1` | the meeting-1 row count is identical between the run's own OFF and ON columns | **544/28 = 19.4286 in both columns** | **PASS** |

**T6 reads 100% here where the certified run read 99.02%, and that is a weaker exercise of the
predicate, not a stronger result.** §15 records why the five-seed reading mattered: one ballot in
§8.1's stated residue put the ≥ 99% floor against a real margin. These 43 ballots carry no residue, so
T6 passes without approaching its floor — the same thing §15 says about the superseded attempt's 88/88.
This section states it rather than reading 100% as an improvement.

**Every denominator here is smaller again** — 9 openings, 34 speech turns, 43 ballots, 50 location
accounts — and §8.1 ratifies that as expected and **NOT a trip**. The baseline-8 population column
binds neither run and is not restated here; §8's tables hold it.

**The four corroboration cells the reader prints for these bytes, as THIS RUN's OWN cells.** They are
`OBSERVED` rows of §5, never gated, and they are **not a prediction of and not a re-derivation of**
#424's re-pinned committed cells — those are a 672-meeting pooled walk over the committed record and
are quoted beside them only so the two cannot be confused:

| cell | **these two seeds (ON)** | #424's re-pinned COMMITTED cell (pooled, four sets) |
|---|---|---|
| `C-1` accused subjects with NO first-hand source | **9/24 = 37.5%** | 460/1,525 |
| `C-2` ejected subjects with NO first-hand source | **0/3 = 0.0000** `[ADV]` | 10/425 |
| `C-3` ejections whose charge ANSWERED the ejectee's own | **0/3 = 0.0000** `[ADV]` | 33/429 |
| `C-4` ejected subjects with a map-satisfied placement pair | **0/3 = 0.0000** `[ADV]` | 79/429 |

Three of the four sit on a denominator of three. **They are directional to the point of being
anecdotal and no criterion names any of them**; they are on the page because the re-smoke's brief asks
for the run's own cells beside the re-pinned ones.

**The §9.2 criteria, quoted VERBATIM and read one at a time:**

| § 9.2 criterion, verbatim | reading on this run | verdict |
|---|---|---|
| "a `scripts/validity_gate.py` FAIL on any leg" | one leg, all ten checks PASS (§18.4) | **NOT MET** |
| "a seed whose opening defaults (the `(deadline_default)` watch item)" | no opening defaulted and **no turn of any kind did**: `lost_openings 0 (defaults 0)`, and zero `failed_call` rows of any error_type over 86 recorded calls (§18.5). The criterion is not reached, and on these bytes neither is the wider reading §14.1 walks | **NOT MET** |
| "a guard trip" | no guard fired: both wrapper preflights behaved as designed (the sanctioned slate passed, the half-slate refused with nothing staged), and `check_replay_provenance` — still **not in this wrapper's path at all** — refuses nothing when driven by hand over these bytes (§18.5) | **NOT MET** |
| "a lever-stamp mismatch between the recorded snapshot and the declared slate, compared through `orchestrator.replay.substrate_slate_mismatches` and **never re-derived**" | `substrate_slate_mismatches(['reporter_reasoning','corroboration_discipline','testimony_shapes'])` → `[]`, and `substrate_stamp_mismatches` empty on each of the two recorded stamps (§18.4) | **NOT MET** |
| "any of the seven §8.1 tripwires failing **its predicate** — the sample-local criterion in §8.1's third column, evaluated over whatever the run actually recorded. A denominator smaller than baseline 8's is expected at the smoke and is NOT a trip." | all seven PASS; the reader exits 0 and `payload["stopped_cells"]` is empty | **NOT MET** |

**Classes this run observed that no criterion names**, recorded in the memo's own words rather than
stretched to fit: the task-completion ending and the exercised guard-redirect marker (§18.3); the
third spoken `saw_kill`, true, naming a real impostor, and not converting (§18.3); T6 passing without
a residue to test it against (above); and the two-seed token reading (§18.7). **No §9.2 criterion
names any of these, and this section invents none.** The precedent for saying so in those words is
`audits/audit-phase-20-smoke.md` §12.

### 18.7 The certified bytes under the merged head — the fact that made this run necessary

**The preserved five-seed bytes still validate.** The OFF-side tools reach them unchanged: run in the
lever-ON shell at this head, `scripts/validity_gate.py` over
`/Users/danielkeinan/ailibi-smoke-21-23/9p2i` PASSES all ten checks over its 5 games, 18 meetings and
102 ballots, `byte_identical_reconstruction` included. **The recording is intact; #424 did not corrupt
it.**

**What #424 removed is the ON reader's ability to walk it.** The same reader §18.6 ran, pointed at the
certified bytes, exits **1** before it reaches a single tripwire:

```
qwen3_6_27b headless-seed-17:meeting-0: 7 of 16 recorded prompts were NOT reproduced by the walk, so
the recorded-response stub missed and the manager defaulted those calls. The first one starts:
'<persona>\nYou are p-2, voting at an AiLibi meeting: two hidden impostors kill crewmates; the crew
wins by voting both impostors out, the impostors by surviving until they equal or '. This is a DEFECT
IN THIS SCRIPT's reconstruction (the wrong renderer bundle, or a shell whose levers are not the
recording's), not a finding about the recorded bytes
```

**7 of 16, on seed 17's first meeting, and the prompt it names is a vote ballot** — exactly the count
and exactly the surface §16 predicted from #424's diff. **This is why the seven tripwires could not
simply be re-read on the same bytes at `$0`, and it is the whole reason this section exists.** The
refusal is the instrument being honest about a renderer that no longer matches the record, not a defect
in either.

**One two-seed operating reading, published with its limits.** Against the SAME two committed seeds
(the like-for-like denominator §12.1 uses), tokens per meeting read **48,536.9 OFF against 49,241.8
ON = ×1.0145**. **This does not re-price §12.1 or §12.2 and must not be read as doing so**: it is two
seeds and nine meetings against the certified run's five and eighteen, the two ON runs disagree with
each other on the same two seeds (the certified run's seeds 17 and 46 alone read 60,439.8 tokens per
meeting over six meetings, because a live model is sampled per call and the trajectories differ), and
§12.1's own finding is that a slate drawn for lever coverage is not a representative token sample.
**The record's basis stays §12.1's ×1.1703 centre and §12.2's 12h47m–16h03m bracket**, both derived
from five seeds; this figure is one more observation beside them and bounds nothing.

### 18.8 What this re-smoke does NOT cover

Named rather than left to be discovered. §13's eight items stand; these are the ones specific to a
two-seed run on the merged head.

1. **Two seeds, nine meetings, three ejections.** Smaller than the certified run in every denominator.
   **No pre-registered bar is declared met or missed here either**, and every cell above is
   directional at this n.
2. **The §8 lever-coverage tables, the §9 watch cells, §10's honesty and solvability probes and
   §11.1's Wave-1 marker pass are NOT re-run.** This section re-runs what the reopened window
   invalidated — the gate, the stamp, the seven tripwires and the watch scan — and leaves the
   five-seed run's measurement sections standing as what they are: measurements of those bytes at
   `14854a06`, which §18.7 shows are still valid bytes.
3. **The projection is not re-derived** (§18.7), and §12.2's bracket is unchanged.
4. **One wrapper, one roster**, as at §13 item 1: `scripts/refresh_samples.sh` on 9p2i only.
5. **The corpus recorder's freeze path is still exercised only by §4.1's planted cases**, and its
   `--seeds` slice still finalizes nothing.

### 18.9 The verdict, the bytes, and what is unchanged

**GO on the reopened window**, ruled against `audits/audit-phase-21-preregistration.md` §9.2: no
abandon criterion is met (§18.6), all seven §8.1 tripwires PASS against their sample-local predicates,
the validity gate PASSED on all ten checks with both reconstructions byte-identical, the recorded
substrate stamp is the declared slate on both seeds by both registered comparisons, the committed
record is untouched, and no recorded `failed_call` row exists of any kind.

**The adopting record's window opens on `44f0a28c`.** The §16 rule is unchanged and governs from here:
any further merge into `agents/`, `meetings/`, `observation/`, `orchestrator/` or
`agents/strategic/prompts/` reopens it again. **§16's two ROUTED items are untouched by a clean run**
— item 1 (the guard/criterion asymmetry, a 21.24 PRECONDITION) and item 2 (the husk's `free_text`
wording, and a `meetings/` edit that will itself reopen this window) are defects in the machinery, and
a two-seed run that happened not to default cannot discharge either. Items 3–6 stand, with item 3
gaining the third case §18.3 records.

**The bytes are PRESERVED, not deleted**, beside the four sets §16 names:

```
/Users/danielkeinan/ailibi-smoke-21-23/post-424-9p2i    3,115,956 bytes over 5 files
  — THIS section's run, seeds 17 and 46 at 44f0a28c
```

so a routed repair can be re-measured on them at `$0` without re-recording a seed.

**And the standing canon, stated where this section needs it, exactly as §0 and §14.1 state it:**
baseline 7 is canon by explicit owner override of a FINDING verdict, with bar 1 missed at
61/103 = 0.5922 against ≥ 0.60 and bar 2 missed at 42 against < 35
(`audits/audit-phase-20-baseline-7.md` §6, §6.1). Nothing in this section states or implies that those
bars passed.
