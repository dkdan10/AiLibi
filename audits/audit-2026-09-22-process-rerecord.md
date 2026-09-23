# The process re-record — the substrate wave's adopting record (2026-09-22)

Card: [`tasks/work/process-rerecord.md`](../tasks/work/process-rerecord.md).
Base: `main` at `39a568c6`, the merge of PR #476, the last card of the substrate
wave. Branch `work/process-rerecord`, one pull request into `main`.

## What this record is, and what it decides

It decides nothing. It is the ONE combined re-record the standing cadence
doctrine calls for after a substrate wave settles: the four committed sets are
re-recorded at the same seeds on the wave's bytes, and
[the process scorecard](../docs/process-scorecard.md)'s nine rows are published
before and after. There is no pre-registration, no bar and no verdict, and no
cell here is attributed to one card of the wave — the three substrate cards
([the route claim](../tasks/work/alibi-as-route.md),
[the grounded SKIP and the labelling guards](../tasks/work/grounded-skip-and-guard-labels.md),
[the weighing channel](../tasks/work/ballot-weighing-channel.md)) all land in
one window and this record says so rather than splitting the credit.

Role-correct ejection is **reported beside every cell and gates nothing**
(ruling D1 of
[the direction of 2026-09-19](../tasks/direction-2026-09-19-process-over-outcome.md)
section 12). Two rows carry their reading in the cell rather than being read as
measured gains, and both are named where they appear.

The merge of this record's pull request is the owner's: it makes the new bytes
the shown baseline and republishes the demo.

## 0. Preflight, on the base and before the first seed

### 0.1 The base, and the gate on it

`git log --oneline -6` at the window's open:

```
39a568c6 Merge pull request #476 from dkdan10/work/ballot-weighing-channel
48f0ab8e docs: restate the round-4 probe counts at the head they describe
28422168 test: pin each sighting shape the ballot's provenance reads
d7b6be94 fix: read a testimony row's provenance off the public transcript only
0ba95723 fix: stop the ballot calling the voter's own words a perception
04214220 fix: keep an impostor's own teammate out of its ballot and unblind the railroad gate
```

`bash scripts/check.sh` on that base: **exit 0** (8,264 passed, 20 skipped,
3 xfailed; 558 frontend tests; task-docs validation 390 historical phase tasks
and 390 prompts, 73 work cards). Run whole in this clean worktree, so no gate
after a first failure was masked.

### 0.2 The version strings, confirmed and NOT edited

The wave leaves four version strings. `orchestrator/game.py:439-442`:

```python
    "qwen3_6_27b": {
        **_bespoke_versions("qwen3_6_27b", version="v6"),
        "vote_ballot": "vote_ballot.qwen3_6_27b.v8",
    },
```

`scripts/record_ml_corpus.sh:171` ALREADY reads exactly those four strings — the
weighing card advanced the pin, so **no edit was made to either recorder**:

```
REQUIRED_PROMPT_VERSIONS_BASE="accusation_round.qwen3_6_27b.v6, crewmate_report.qwen3_6_27b.v6, impostor_report.qwen3_6_27b.v6, vote_ballot.qwen3_6_27b.v8"
```

Both recorders are used as they stand. `scripts/run_tournament.py` and
`scripts/refresh_samples.sh` are untouched.

### 0.3 The four dry-runs, and their resolved configuration

Every leg previewed with `--dry-run` before anything staged; all four exited 0,
made no API call and wrote nothing. The resolved configuration each printed:

**Leg 1 — `replays/samples/9p2i`** (`AILIBI_LLM_PROVIDER=featherless`,
`AILIBI_PROMPT_SET=qwen3_6_27b`, `AILIBI_NUM_PLAYERS=9`,
`AILIBI_NUM_IMPOSTORS=2`, `AILIBI_TASKS_PER_CREWMATE=2`,
`AILIBI_SAMPLE_DIR=replays/samples/9p2i`,
`AILIBI_MANIFEST=replays/samples/9p2i/MANIFEST.md`,
`bash scripts/refresh_samples.sh --full --expect-levers ""`):

```
[dry-run] mode: full
[dry-run] seeds: 0,1,2,...,49
[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2
[dry-run] sample dir: replays/samples/9p2i
[dry-run] provider: featherless
[dry-run] model-set coupling: would require the effective featherless meeting model ... to be 'Qwen/Qwen3.6-27B'
[dry-run] prompt set: qwen3_6_27b
[dry-run] substrate flags: expected levers ON = (none — the bare slate: every live toggle OFF); every other live toggle OFF; the graduated levers unconditional ON
Substrate slate OK.
```

**Leg 2 — `replays/ml_corpus/9p2i`** (`AILIBI_PROMPT_SET=qwen3_6_27b`,
`bash scripts/record_ml_corpus.sh --set 9p2i --expect-levers ""`):

```
[dry-run] provider: featherless (LOCKED — the corpus substrate pins it)
[dry-run] prompt set: qwen3_6_27b (must be exported as AILIBI_PROMPT_SET)
[dry-run] model: Qwen/Qwen3.6-27B (meeting + trigger pinned; a non-baseline override is refused)
[dry-run] endpoint: https://api.featherless.ai/v1 (pinned; a non-default override is refused)
[dry-run] prompt versions: the declared slate resolves to [accusation_round.qwen3_6_27b.v6, crewmate_report.qwen3_6_27b.v6, impostor_report.qwen3_6_27b.v6, vote_ballot.qwen3_6_27b.v8]
[dry-run]   seed range: 1000..1149 (150 games)
[dry-run] tactical policy stamp: fsm-default
Substrate slate OK.
```

**Leg 3 — `replays/samples/4p1i`** (`AILIBI_LLM_PROVIDER=featherless`,
`AILIBI_PROMPT_SET=qwen3_6_27b`, `refresh_samples.sh --full --expect-levers ""`
at its 4p1i defaults): `roster: num_players=4 num_impostors=1
tasks_per_crewmate=1`, seeds `0..49`, same provider, model and slate lines.

**Leg 4 — `replays/ml_corpus/4p1i`** (`--set 4p1i --expect-levers ""`): seed
range `1000..1049` (50 games), same pins as leg 2.

The acceptance command both corpus dry-runs print, and the one this record runs
per leg:

```
scripts/validity_gate.py <set> --expected-model Qwen/Qwen3.6-27B --require-zero-cost \
  --expected-prompt-versions accusation_round=accusation_round.qwen3_6_27b.v6,\
crewmate_report=crewmate_report.qwen3_6_27b.v6,\
impostor_report=impostor_report.qwen3_6_27b.v6,\
vote_ballot=vote_ballot.qwen3_6_27b.v8
```

### 0.4 The authorization, and the ceilings it fixes

Confirmed by the owner on 2026-09-20 (the card's Evidence, and the addendum to
the direction memo's section 12). Provider `featherless`, model
`Qwen/Qwen3.6-27B` exactly, the default endpoint,
`AILIBI_PROMPT_SET=qwen3_6_27b`, the bare slate. Each ceiling is a hard stop:

| limit | measured on the committed bytes | authorized | actual |
|---|---|---|---|
| model calls | 7,271 | 9,500 | **7,270** (§2) |
| input tokens | 31,756,112 | 43,000,000 → **46,000,000** (§0.4a) | **41,556,280** (§2) |
| output tokens | 1,598,475 | 2,200,000 | **1,827,165** (§2) |
| recording wall | about 12h05m | 16 h | **10h53m28s** (§2) |
| elapsed window | about 15h48m | 24 h | **11h05m48s** (§2) |
| marginal cost | `$0.0000` | `$0.00` | **`$0.0000`** on every recorded call (§2) |

The cost is `$0.00` **marginal** against the flat-rate Featherless
subscription, whose standing fee is already paid and is not incurred by this
run.

### 0.4a The input ceiling, raised mid-leg-1 — 2026-09-22

The owner, on 2026-09-22, relayed verbatim by the orchestrator:

> Raise the input ceiling to 46M

So the authorized input-token ceiling is **46,000,000** from that point on. The
original `43,000,000` stays in the table above as recorded; it is annotated,
not rewritten.

**The projection that prompted it.** The first ten seeds of leg 1 measured
**210,195 input tokens per game**, read as 1.357x the previous record's
per-game input and projected to **43.09 M** over all 300 games — over the
original ceiling by a margin too thin to record against. That is the reading
the decision was taken on, and it is recorded here as the reason given.

**The operator's own re-derivation, which lands lower, and what the 1.357x is.**
This record re-measured the ratio MATCHED SEED BY SEED — the same ten seeds,
the same roster, the new bytes against the preserved old ones — rather than
against the previous record's whole run:

| | calls | input | output | input per game |
|---|---|---|---|---|
| NEW, seeds 0-9 of `samples/9p2i` | 352 | 2,101,949 | 90,732 | 210,194 |
| OLD, the same ten seeds | 370 | 1,677,230 | 81,750 | 167,723 |
| ratio new/old | **0.9514** | **1.2532** | **1.1099** | |

The 210,195 figure reproduces to the digit. The **1.357x** is not a per-game
ratio. It reproduces only as the projection over the previous record's total
input: 43.09 M / 31,756,112 = 1.357, where 43.09 M = 210,195 x 205. The record
does not show how the 205 was derived, and this close could not reproduce it.
This section first said the 1.357x divides the 9p2i per-game figure by the
previous record's average over all four sets. That is false: the average is
31,756,112 / 300 = 105,854, and 210,195 / 105,854 = 1.986. Matched seed by seed
the input ratio is **1.2532**, and scaling the previous record's whole-run
totals by the matched ratios projects:

| | projection | against the ceiling |
|---|---|---|
| input tokens | 39,797,600 | 86.5% of 46,000,000 (92.6% of the original 43,000,000) |
| model calls | 6,917 | 72.8% of 9,500 |
| output tokens | 1,774,102 | 80.6% of 2,200,000 |

On that ten-seed arithmetic the run looked to fit inside the ORIGINAL ceiling,
and this section first called the raise headroom rather than a requirement.
**That reading was too strong, and is corrected here against the measured
run.** A 9p2i corpus game costs more input than a sample one (about 204K
against 197K), so the projection re-derived per set at 111 of 300 games came to
about **42.2 M** input — **98.1%** of the original 43,000,000 — and the actual,
§2.2, landed at **41,556,280**, 96.6% of it: a margin of about 3%, far too thin
to record against with re-records still possible. **The raise was needed.**
Against the actual 41,556,280, the owner's 43.09 M projection overshot by
1.53 M. The matched-ratio projections undershot: the ten-seed 39.80 M above by
1.76 M, and the fifty-seed 40.36 M of §2.2 by 1.20 M. Both matched projections
scale the whole previous run by a ratio measured on `samples/9p2i` alone, and
`ml_corpus/9p2i` grew more than that set did: 1.3251 against 1.2708 (22,680,439
to 30,053,852 input, and 7,751,883 to 9,850,930).
The calls ratio is worth its own line: the wave's bytes make **fewer** model
calls per game, not more (0.9514), so the input growth is prompt size — the
larger ballot body — and not extra traffic.

**Every other ceiling is unchanged**: 9,500 model calls, 2,200,000 output
tokens, a 16 h recording wall inside a 24 h window, `$0.00` marginal. The stop
rule of §0.5 and the per-leg budget accounting of §2 read 46,000,000 from here
on. The running leg was not interrupted: the amendment was folded in at the
next boundary at which this record already touched the card and the audit.

### 0.5 The stop rule, pre-committed

Stop and report to the owner, before the next leg, on: any recorded `cost_usd`
other than `0.0000`; a leg past 1.5x its projected wall; a named-not-to-move
cell moving; a hard provider refusal surviving the eight-attempt retry budget; a
stall (no completed seed for 45 minutes), where the batch is killed and re-run
or a fresh operator relaunched from the pushed checkpoint. **A seed on disk
never re-records to recover from a stall**; a `(deadline_default)` row is a
failed recording whose seed re-records, with its cause logged as it happens.
If the 24 h window closes, the record stops at a SET boundary and §2 names the
legs that exist: a partial record is not a baseline.

### 0.6 The freeze

From the first seed until this pull request merges, nothing merges into
`engine/`, `agents/`, `meetings/`, `observation/`, `orchestrator/` or the prompt
set. §8 shows the window's `git log` rather than asserting it.

### 0.7 Retention

Each set's prior bytes moved aside and are preserved OUT OF TREE for the
duration (both recorders read a present in-range replay as already recorded).
Nothing is archived into the tree: the baseline-8 bytes stay reachable in git
history at `39a568c6` and its ancestors, and a second in-tree copy would be a
duplicate registry row rather than a backup.

## 1. The BEFORE column, computed and committed before the first seed

Computed on the still-committed bytes with the shipped tool,
`uv run python scripts/publish_process_scorecard.py`, whose `--check` was
consistent on the base:

```
--check: docs/process-scorecard.md and docs/process-scorecard.json are consistent
with the committed recordings.
```

Rulings D4 and D6 invalidate comparisons against these recordings, so a
back-filled column would be a reconstruction rather than a reading; this column
is committed here, before the first seed stages.

### 1.1 The four cross-checks the card names, reproduced

| cross-check | the card | reproduced |
|---|---|---|
| EJECT cited, `samples/9p2i` | 526/527 | 527 EJECT − 1 uncited = **526/527** |
| EJECT cited, `ml_corpus/9p2i` | 1,498/1,499 | 1,499 EJECT − 1 uncited = **1,498/1,499** |
| grounded SKIP, the two 9p2i sets | 0 of 1,359 | **0/1359** (342 + 1,017) |
| guard-redirected ballots | 57/2,516 and 23/869 | **57/2516**, **23/869** |
| crew EJECTs off the suspicion argmax | 81 of 1,270, 7 role-correct | **81/1270**, **7** role-correct |

### 1.2 The before column — pooled, all four committed sets

300 games, 672 meetings, 3,631 ballots (2,146 EJECT, 1,485 SKIP).

| # | row | before |
|---|---|---|
| 1 | grounded-decision rate, EJECT | 2078/2146 = 0.9683 |
| 1 | grounded-decision rate, SKIP | 0/1485 = 0.0000 **by instruction** |
| 1 | grounded-decision rate, all ballots | 2078/3631 = 0.5723 |
| 2 | argmax-independence: deviating EJECTs | 116/1811 = 6.4% |
| 2 | argmax-independence: accuracy, followers vs deviators | 1602/1695 = 94.5% vs 9/116 = 7.8% (chance 31.6%) |
| 3 | manufactured-contradiction rate | 159/192 = 0.8281 (not evaluable 32) |
| 4 | unexplained-decision rate | 20/3631 = 0.0055 |
| 5 | evidence-quality mix | contradiction_flag 10, first_hand 75, hearsay 8, unevidenced 3, vent_flag 333 |
| 6 | rationale faithfulness (TOKENS) | 2874/2874 = 1.0000 (not evaluable 757) |
| 7 | agent-authored share | 3531/3631 = 0.9725 |
| 8 | wrong-but-believable rate | 383/2146 = 0.1785 — reported, never penalised |
| 9 | role-correct ejection rate | 383/429 = 0.8928 — **reported beside, gating nothing** |

**Row 1 SKIP reads `0` BY INSTRUCTION**, not as a measured failure: the
pre-wave ballot template
(`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`, at the lines the
grounded-SKIP card moved) told the voter to leave a SKIP's basis empty, so no
committed SKIP could carry one. The grounded-SKIP card changes the instruction;
the after cell measures what the agents do with it.

### 1.3 The before column — per set

**`replays/samples/9p2i`** — 50 games, 151 meetings, 869 ballots (527 EJECT, 342 SKIP)

| # | row | before |
|---|---|---|
| 1 | grounded-decision rate, EJECT | 507/527 = 0.9620 |
| 1 | grounded-decision rate, SKIP | 0/342 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 507/869 = 0.5834 |
| 2 | argmax-independence: deviating EJECTs | 31/434 = 7.1% |
| 2 | argmax-independence: accuracy, followers vs deviators | 358/403 = 88.8% vs 2/31 = 6.5% (chance 30.5%) |
| 3 | manufactured-contradiction rate | 53/57 = 0.9298 (not evaluable 4) |
| 4 | unexplained-decision rate | 4/869 = 0.0046 |
| 5 | evidence-quality mix | contradiction_flag 7, first_hand 17, hearsay 3, vent_flag 68 |
| 6 | rationale faithfulness (TOKENS) | 705/705 = 1.0000 (not evaluable 164) |
| 7 | agent-authored share | 842/869 = 0.9689 |
| 8 | wrong-but-believable rate | 113/527 = 0.2144 |
| 9 | role-correct ejection rate | 82/95 = 0.8632 |

**`replays/ml_corpus/9p2i`** — 150 games, 439 meetings, 2,516 ballots (1,499 EJECT, 1,017 SKIP)

| # | row | before |
|---|---|---|
| 1 | grounded-decision rate, EJECT | 1455/1499 = 0.9706 |
| 1 | grounded-decision rate, SKIP | 0/1017 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 1455/2516 = 0.5783 |
| 2 | argmax-independence: deviating EJECTs | 81/1270 = 6.4% |
| 2 | argmax-independence: accuracy, followers vs deviators | 1143/1189 = 96.1% vs 7/81 = 8.6% (chance 30.4%) |
| 3 | manufactured-contradiction rate | 105/134 = 0.7836 (not evaluable 28) |
| 4 | unexplained-decision rate | 15/2516 = 0.0060 |
| 5 | evidence-quality mix | contradiction_flag 3, first_hand 52, hearsay 4, unevidenced 2, vent_flag 220 |
| 6 | rationale faithfulness (TOKENS) | 2014/2014 = 1.0000 (not evaluable 502) |
| 7 | agent-authored share | 2446/2516 = 0.9722 |
| 8 | wrong-but-believable rate | 251/1499 = 0.1674 |
| 9 | role-correct ejection rate | 252/281 = 0.8968 |

**`replays/samples/4p1i`** — 50 games, 39 meetings, 117 ballots (51 EJECT, 66 SKIP)

| # | row | before |
|---|---|---|
| 1 | grounded-decision rate, EJECT | 50/51 = 0.9804 |
| 1 | grounded-decision rate, SKIP | 0/66 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 50/117 = 0.4274 |
| 2 | argmax-independence: deviating EJECTs | 3/47 = 6.4% |
| 2 | argmax-independence: accuracy, followers vs deviators | 42/44 = 95.5% vs 0/3 = 0.0% (chance 50.0%) |
| 3 | manufactured-contradiction rate | 0/0 = n/a (not evaluable 0) |
| 4 | unexplained-decision rate | 1/117 = 0.0085 |
| 5 | evidence-quality mix | first_hand 4, hearsay 1, vent_flag 19 |
| 6 | rationale faithfulness (TOKENS) | 72/72 = 1.0000 (not evaluable 45) |
| 7 | agent-authored share | 116/117 = 0.9915 |
| 8 | wrong-but-believable rate | 9/51 = 0.1765 |
| 9 | role-correct ejection rate | 20/24 = 0.8333 |

**`replays/ml_corpus/4p1i`** — 50 games, 43 meetings, 129 ballots (69 EJECT, 60 SKIP)

| # | row | before |
|---|---|---|
| 1 | grounded-decision rate, EJECT | 66/69 = 0.9565 |
| 1 | grounded-decision rate, SKIP | 0/60 = 0.0000 |
| 1 | grounded-decision rate, all ballots | 66/129 = 0.5116 |
| 2 | argmax-independence: deviating EJECTs | 1/60 = 1.7% |
| 2 | argmax-independence: accuracy, followers vs deviators | 59/59 = 100.0% vs 0/1 = 0.0% (chance 50.0%) |
| 3 | manufactured-contradiction rate | 1/1 = 1.0000 (not evaluable 0) |
| 4 | unexplained-decision rate | 0/129 = 0.0000 |
| 5 | evidence-quality mix | first_hand 2, unevidenced 1, vent_flag 26 |
| 6 | rationale faithfulness (TOKENS) | 83/83 = 1.0000 (not evaluable 46) |
| 7 | agent-authored share | 127/129 = 0.9845 |
| 8 | wrong-but-believable rate | 10/69 = 0.1449 |
| 9 | role-correct ejection rate | 29/29 = 1.0000 |

## 1.4 The absolute flag census, before — and why row 3 needs it

Row 3 is a RATE, and its denominator is about to move. The basis test that owns
the split is `eval.process_scorecard._flag_scored_claim_truth`
(`eval/process_scorecard.py:1014`): `_claim_truth` walks each segment against
the engine route, and `meetings.transcript.maximal_stays` decides the cut. It is
a **shape** gate rather than a prompt-version one. A claim whose route carries
more than one maximal stay returns not-evaluable, because a recorded flag names
the CLAIM's event id and not the stay it rests on, so scoring it across the
whole route would file a caught lie as manufactured.

**Every committed claim is a one-segment route** — measured, not assumed:
`stays {1: 1003}` over all four sets below, 0 multi-stay. So no old recording is
re-scored under the new rule, and the multi-segment shape arrives WITH this
re-record. That makes row 3's denominator liable to shrink on the new bytes, and
**a falling rate over a shrinking denominator says little**. The absolute counts
below are published beside it so the cell can be read for what it is: the route
claim's own thesis is that honest multi-room movers stop minting flags at all,
which should show as a falling absolute alibi-flag count at a comparable meeting
count, independently of any rate.

The shape split is pinned by planted fixtures of each shape, already shipped by
the scorecard card: `tests/eval/test_process_scorecard.py:755` (a one-segment
route IS scored), `:722` (a part-true multi-segment route is not-evaluable
rather than manufactured) and `:770` (re-cutting one stay changes nothing).

**BEFORE — absolute contradiction flags by kind, with the meeting count.**
Read with the shipped loader and the shipped `maximal_stays`, out of tree,
changing no instrument. `samples/9p2i` is read from the preserved copy, the
other three from the still-committed bytes.

| set | games | meetings | alibi_conflict | alibi_vs_sighting | alibi_vs_physical | vent_sighting | alibi-class | all flags | flags/meeting | alibi/meeting |
|---|---|---|---|---|---|---|---|---|---|---|
| `samples/9p2i` | 50 | 151 | 21 | 31 | 5 | 90 | 57 | 147 | 0.9735 | 0.3775 |
| `ml_corpus/9p2i` | 150 | 439 | 40 | 86 | 8 | 315 | 134 | 449 | 1.0228 | 0.3052 |
| `samples/4p1i` | 50 | 39 | 0 | 0 | 0 | 20 | 0 | 20 | 0.5128 | 0.0000 |
| `ml_corpus/4p1i` | 50 | 43 | 1 | 0 | 0 | 28 | 1 | 29 | 0.6744 | 0.0233 |
| **pooled** | **300** | **672** | **62** | **117** | **13** | **453** | **192** | **645** | **0.9598** | **0.2857** |

**Self-alibi claim census, before**: 1,003 claims, **0 multi-stay**
(`samples/9p2i` 259, `ml_corpus/9p2i` 696, `samples/4p1i` 29,
`ml_corpus/4p1i` 19). Three independent cross-checks that this census reads the
same population the published instruments do: the pooled alibi-class count
**192** is row 3's published denominator; the pooled self-alibi count **1,003**
is the scorecard's own claim census; and `samples/9p2i`'s 147 flags over 151
meetings is exactly `eval/watchability.py`'s baseline-8 `flags_per_meeting` pin.

## 2. The legs, as recorded

Each leg is fully gated before the next begins, and its range checkpoint-pushed.
Every recorded `cost_usd` on every leg is `0.0000`.

| leg | set | games | recording wall (elapsed) | calls | input | output | cost | previous record's wall |
|---|---|---|---|---|---|---|---|---|
| 1 | `replays/samples/9p2i` | 50/50 | **2h24m55s** (2h25m19s) | 1,694 | 9,850,930 | 422,941 | `$0.0000` | 3h07m00s |
| 2 | `replays/ml_corpus/9p2i` | 150/150 | **7h45m05s** (7h47m25s) | 5,084 | 30,053,852 | 1,298,156 | `$0.0000` | 7h59m32s |
| 3 | `replays/samples/4p1i` | 50/50 | **20m44s** (21m51s) | 234 | 782,265 | 51,657 | `$0.0000` | 23m15s |
| 4 | `replays/ml_corpus/4p1i` | 50/50 | **22m44s** (23m01s) | 258 | 869,233 | 54,411 | `$0.0000` | 24m41s (incomplete) |
| **total** | **four sets** | **300/300** | **10h53m28s** (window 11h05m48s) | **7,270** | **41,556,280** | **1,827,165** | **`$0.0000`** | |

**The record is complete at 300 of 300 games**, every seed in one window
(2026-09-22 04:21:56Z to 15:27:44Z). The recording wall sums each leg's
recording phases from the operator's own start and end stamps (probe seed, the
rest of the leg, any seed repair, the finalize); elapsed adds the gaps between
them. The spend is counted from the committed bytes' own `llm_calls` rows with
the tally command the card's Evidence quotes, so it covers every call that
reached a committed replay and **not** the three discarded first attempts of
§5's seed repairs, whose husks were removed before any tally; those were
`$0.0000` like every other call and their token count is not recoverable.

**Leg 1** opened 2026-09-22 04:21:56Z and closed 06:47:15Z. The honesty probe
ran on the first completed seed before the rest queued: seed 0, three meetings
so not vacuous, every instrument folding with no raise and no unfoldable cell
family. The remaining 49 seeds then recorded on two workers.

**Leg 2** opened 06:52:03Z with the probe seed 1000 (227 s, two meetings, not
vacuous; the honesty probe folded clean), ran its main phase 06:57:00Z to
14:24:33Z, repaired three seeds (§5) and froze at 14:39:28Z: `splits.json` 90
train / 30 val / 30 test, the FROZEN line at `git_sha` 820704be.

**Leg 3** opened 14:41:58Z. Its first probe seed was VACUOUS — seed 0 an
impostor win with zero meetings — so seeds 1-3 recorded next and the probe
re-ran on that fold (four games, two meetings), clean (§5). The rest recorded
14:43:58Z to 15:03:49Z.

**Leg 4** opened 15:04:43Z with probe seed 1000 (a meeting, so not vacuous;
clean), recorded the rest and froze at 15:27:44Z: `splits.json` 30 / 10 / 10,
the FROZEN line at `git_sha` 9bae2b03.

### 2.0 The spend, against the ceilings

| limit | authorized | actual | share |
|---|---|---|---|
| model calls | 9,500 | 7,270 | 76.5% |
| input tokens | 46,000,000 (43,000,000 before the raise) | 41,556,280 | 90.3% (96.6% of the original) |
| output tokens | 2,200,000 | 1,827,165 | 83.1% |
| recording wall | 16 h | 10h53m28s | 68.1% |
| elapsed window | 24 h | 11h05m48s | 46.2% |
| marginal cost | `$0.00` | `$0.0000` on every recorded call | — |

No ceiling was reached and no stop condition fired. The calls land within one
of the previous record's 7,271 while input rises 31% (31,756,112 →
41,556,280): the wave's bytes make no more model calls, they make larger ones —
the ballot body the weighing channel enlarged.

### 2.2 The budget, against the ceilings

Re-derived matched seed by seed over the WHOLE leg rather than projected from a
handful — the same seeds, the same roster, the new bytes against the preserved
old ones:

| | calls | input | output |
|---|---|---|---|
| NEW, `samples/9p2i` 50 seeds | 1,694 | 9,850,930 | 422,941 |
| OLD, the same 50 seeds | 1,740 | 7,751,883 | 382,977 |
| ratio new/old | **0.9736** | **1.2708** | **1.1044** |

Scaling the previous record's whole-run totals by those ratios projects
**40,355,000** input tokens (87.7% of the authorised 46,000,000, and 93.9% of
the original 43,000,000), **7,079** model calls (74.5%) and **1,765,277** output
tokens (80.2%) — inside every ceiling, so leg 2 opened with no stop. This is the
figure §0.4a's ten-seed reading is settled against: 1.2708 over fifty matched
seeds against 1.2532 over the first ten. The 1.357 the raise was taken on is
not a matched ratio at all (§0.4a gives the arithmetic that reproduces it).

**The calls ratio is below 1.** The wave's bytes make FEWER model calls per game,
so the input growth is prompt size — the larger ballot body — and not extra
traffic.

## 2.3 What leg 1's bytes already show

Not a verdict and not a bar; the cells are published in §4. These are the
movements that are legible on the first leg alone, `samples/9p2i` before against
after:

| cell | before | after leg 1 |
|---|---|---|
| grounded SKIP | **0 / 342** (by instruction) | **79 / 349** |
| guard-redirected ballots | 23 | **0** |
| grounded EJECT | 507/527 = 0.9620 | 494/496 = 0.9960 |
| ballots with no rendered suspicion row | 0 | **0** |

The SKIP row moves off zero for the first time, which is what the grounded-SKIP
card was for. The redirect census reaching zero is the labelling guards: they
label rather than re-aim, which is why the retired evidence-judgement rewrites
(`under_gate_redirect` and `uncited_coerced`) read 0 **by construction** rather
than as a measured gain. The agent-authored share itself is not 1.0: §4.2 reads
it at 3609/3630 = 0.9942, because the two rewrites the wave kept
(`invalid_target` and `teammate_coerced`) remain; `samples/9p2i` alone reads
841/845. The last row is the control that
separates a stale reader from a substrate regression, and it is why §2.1a is a
parser finding and not a missing channel.

## 2.1 A reader this record repaired, and one it deliberately did not

### 2.1a The stale suspicion-row pattern, widened

Leg 1's rubric came back scoring **0.0 on all 50 games**, where the pre-record
one scored 21 of 50 with a live `r3_arcs`. The cause is one literal.
`audits/workflows/extract_gameplay_facts.py` matched a rendered suspicion row
as `` `p-N`: suspicion X, trust Y ``, and
[the weighing channel](../tasks/work/ballot-weighing-channel.md) deleted the
trust column rather than keep displaying a constant. The pattern then matched
nothing, which emptied `rendered_suspicion_by_target`, built no accumulator
trajectory, and scored `r3_arcs` 0 on every game — **silently, with no error**.

**It is a stale reader, not a substrate regression, and the way that was
established is worth keeping.** The obvious fear was the opposite: that the
weighing channel had removed the rendered suspicion rows altogether, which would
make row 2 — argmax-independence, one of the two rows the direction memo calls
the point of the revision — unmeasurable on the new bytes. The scorecard reads
those rows through a different, structured channel, so it answers the question
directly: on the new `samples/9p2i` bytes it reports **`argmax_no_row` = 0**,
every ballot carrying a rendered row, with 382 followers and 31 deviators. The
rows are there; only this parser stopped seeing them.

**Routed, not scope creep.** That card's own deviation 5
(`tasks/work/ballot-weighing-channel.md:717-723`) widened the identical pattern
in `eval/meeting_quality.py` and `eval/validity.py`, left this third reader
narrowed because it could not move `audits/` bytes or recompute their
`docs/artifacts.md` row, and said the re-record card should take it. It is taken
here, as the same one-line widening, on the orchestrator's decision of
2026-09-22.

**The neutrality proof is exhaustive, and replaces the single re-run.** The
intended proof was to re-run the rubric step over the preserved pre-record bytes
and reproduce the committed pre-record `results-rubric-score.json`. That proof
is **impossible for any parser**, because the committed rubric never described
its own bytes: it agrees with the pre-record eval report on **29 of 50 seeds**,
carries the provenance key `multi:fbdfaedea493` rather than a git sha, and has
no `source_fingerprint` field at all. On seed 1 the pre-record eval report reads
`IMPOSTOR_PARITY` over 4 meetings and the committed rubric claims
`CREWMATE_EJECT` over 3; a fresh run over those same preserved bytes reproduces
the eval report, not the rubric. **The committed rubric was already stale on
`main` before this card.**

So the proof was made stronger instead of weaker. Over **every** recorded prompt
in the preserved pre-record bytes of both 9p2i sets — **6,779 prompts, 3,378
carrying a suspicion graph, 14,599 rows parsed** — the narrowed and the widened
pattern produce **0 mismatches**. No committed figure moves. The planted shapes
behave as they must: the old row parses identically under both, and the new
trust-less row parses only under the widened one. Both, and the narrowed
pattern's silent emptiness, are pinned by
`tests/experiments/test_gameplay_facts_suspicion_row.py`.

### 2.1b The integrity floor, left alone

Widening the pattern restores `r3_arcs` — and the rubric still scores **0.0 on
every game**, including games whose four dimensions all read 1.0. A second and
independent cause floors them. One of the extractor's seventeen self-checks
fails:

```
re-derived genuine-class == shipped compute_genuine_class_conversion
  (supplied 1/0, converted 0/0): FAIL
```

That is the leg-1 run. On the final bytes, with the widened pattern, the step
was re-run ALONE at the close (the extractor, then
`experiments/lab/rubric_score.py <facts> --set-dir replays/samples/9p2i`, both
exit 0) and the same check reads
`(supplied 1/0, converted 1/0): FAIL` — the re-derivation counts one supplied
and one converted genuine-class meeting where the shipped function counts none.
The other sixteen self-checks pass, including the win split (39/11) and the
eject-decided wins (38/38). The committed rubric is that run's output: 50
games, 0.0 each.

`experiments/lab/rubric_score.py::_facts_integrity_ok` reads that list, any
`FAIL` sets the floor multiplier to 0, and every game's score becomes 0
regardless of its dimensions. **It is independent of the pattern**, provably:
over the old bytes the two patterns parse identically, so every downstream
value, `self_checks` included, is unchanged. It predates this record, and it is
what explains the staleness above — the rubric has not been regenerable since
that check began failing.

**This record does not touch it.** It is a genuine disagreement between two
production computations, and deciding which side is wrong is instrument work,
which stays frozen during a measurement. §7.1 routes it to the owner.

**What is committed, and why.** The regenerated rubric, zeros included, as what
the shipped tool computes on these bytes. A regenerated file that states the
tool's own output is a record; the stale committed one was not. By the card's
letter the refresh is **complete** — the rubric step runs and exits 0 on every
leg, and the card reads only its *failure* as incompleteness — and it is
**degraded** by the defect above. Both statements are true and both are made.

**Measured before the tour was re-pointed, because zeros would otherwise select
or break it:** neither the featured criterion nor the head-card guard reads the
rubric at all. `scripts/measure_featured_criterion.py` carries no rubric
reference (its criterion is the `role_proof` predicate over the set loader), and
`frontend/e2e/journey.spec.ts` carries none (its guard binds the blurb's claim
to the rendered evidence count). The rubric feeds only the separate
`/eval/rubric` highlights surface, so the tour is unaffected either way.

## 3. The gates, per leg

Every gate runs in a BARE shell with no `AILIBI_*` export, verified by printing
the environment's `AILIBI_*` count (0) before each run.

### Leg 1 — `replays/samples/9p2i`

`scripts/validity_gate.py replays/samples/9p2i --expected-model Qwen/Qwen3.6-27B
--require-zero-cost --expected-prompt-versions <the four KEY=VER pairs>`
**PASSED**, all ten checks green and named individually:

```
[PASS] all_games_reach_game_over: 50/50 games reached a reconstructed game_over
[PASS] meeting_rate_and_resolution: meeting_rate 1.0 (floor 0.60); 145 resolved; 0 unresolved
[PASS] no_duplicate_meeting_rows: 0 duplicate meeting rows over 145 (want 0)
[PASS] no_tick_1_kills: 0 kills at tick <= 1 (want 0)
[PASS] no_friendly_fire_kills: 0 impostor-on-impostor kills (want 0)
[PASS] no_betrayal_ballots_or_accusations: 0 over 845 multi-impostor ballots (want 0)
[PASS] no_railroaded_crew_ejections: 0 railroaded crew rows over 2588 rendered crew suspicions
[PASS] no_dangling_primary_reason_id: 0 dangling over 845 ballots (want 0)
[PASS] cost_and_provenance_exact: model='Qwen/Qwen3.6-27B', 4 prompt versions,
       substrate stamped exact on 50 games
[PASS] byte_identical_reconstruction: 0 samples drifted (want 0)
```

`bash scripts/verify_samples.sh replays/samples/9p2i`: **all 50 samples verified
clean**.

**Canonicality**, the explicit check that stands in for `--full`'s
`canonicalize` sweep (deviation 1 of the card): exactly the seeds `0..49`, no
zero-padded alias, no out-of-range replay, and 50 MANIFEST data rows. The sweep
itself is a no-op here because the set dir was emptied before the leg and
exactly 0-49 recorded, but the property it guarantees is checked rather than
assumed.

### Legs 2 to 4

The same gate, the same bare shell, each leg before the next began. Every
check PASSED on every leg; the lines that carry a count:

| check | leg 2 `ml_corpus/9p2i` | leg 3 `samples/4p1i` | leg 4 `ml_corpus/4p1i` |
|---|---|---|---|
| `all_games_reach_game_over` | 150/150 | 50/50 | 50/50 |
| `meeting_rate_and_resolution` | 1.0 (floor 0.60); 449 resolved, 0 unresolved | 0.78; 39 resolved, 0 unresolved | 0.86; 43 resolved, 0 unresolved |
| `no_duplicate_meeting_rows` | 0 over 449 | 0 over 39 | 0 over 43 |
| `no_tick_1_kills` | 0 | 0 | 0 |
| `no_friendly_fire_kills` | 0 | 0 | 0 |
| `no_betrayal_ballots_or_accusations` | 0 over 2,539 multi-impostor ballots | 0 over 0 | 0 over 0 |
| `no_railroaded_crew_ejections` | 0 over 7,584 rendered crew suspicions | 0 over 63 | 0 over 65 |
| `no_dangling_primary_reason_id` | 0 over 2,539 ballots | 0 over 117 | 0 over 129 |
| `cost_and_provenance_exact` | the model, 4 prompt versions, substrate exact on 150 games | on 50 games | on 50 games |
| `byte_identical_reconstruction` | 0 drifted | 0 drifted | 0 drifted |

`bash scripts/verify_samples.sh <set>` verified all 150, 50 and 50 clean.
Canonicality for leg 3 (the other sample leg): exactly seeds `0..49`, 50
MANIFEST rows, no alias. The corpus legs' canonicality is the recorder's own
freeze guard, which refuses anything but the exact locked seed set.

## 3.5 The delivery path: four gzipped reports, and the proof they moved nothing

**What happened.** The push carrying leg 2 was refused by a pre-receive hook:
`replays/ml_corpus/9p2i/tournament-eval-report.json` had reached **102.70 MB**
against GitHub's hard **100 MB** per-file limit. That file is a derived view,
and it grew **+29.5%** (from 79.29 MB) because it embeds the prompts and
transcripts the wave's larger ballot body inflated — the same ~27% the token
counts show. The repo configures no Git LFS. The owner decided on 2026-09-22 to
deliver all four reports gzipped.

| set | uncompressed | gzipped | ratio |
|---|---|---|---|
| `replays/ml_corpus/9p2i` | 102.70 MB | **8.92 MB** | 11.51x |
| `replays/samples/9p2i` | 33.86 MB | **2.89 MB** | 11.73x |
| `replays/ml_corpus/4p1i` | 3.71 MB | **0.50 MB** | 7.35x |
| `replays/samples/4p1i` | 3.37 MB | **0.46 MB** | 7.35x |

The ratios are measured on the committed archives: 3,886,666 / 528,633 and
3,535,583 / 480,717 bytes for the two 4p1i reports. The 7.48x and 6.91x in
commit `134b10de`'s message are superseded. They were the old `ml_corpus/4p1i`
report and a four-game partial of `samples/4p1i`.

**The proof that no measured value moved.** For each set, three digests of the
same bytes: the uncompressed file held out of tree BEFORE the change, the
decompressed archive AFTER it, and a fresh in-memory rebuild from the replays
(`build_sample_report.py --check`, which was consistent on all four).

| set | sha256 of the pre-change bytes = sha256 of the decompressed archive |
|---|---|
| `samples/9p2i` | `ca7e190b3405e89efc19cb0bb7e0b68b9252157c43a5af4a8bfff6ce223ea29a` |
| `ml_corpus/9p2i` | `9b17bf9c5ed7a61ed624cf159ede1103b53cdf210947816b71b57bb105f28848` |
| `samples/4p1i` | `0e91743f60e7a078ced12725717d64c57b483f7f221a5a3d293db13bb39951ce` |
| `ml_corpus/4p1i` | `ebf03641ff18e32ddc14d23e6ecd8479d21e1a8477338be8ecee510dde8f5146` |

The archive is a pure function of its contents: `mtime=0` and no embedded
filename, so compressing the same report twice is byte-identical and `--check`
stays a real gate instead of noise.

**One home, not ten.** `eval/report_io.py` owns the name, the writer, the
reader and a line-iterable opener — the last so `check_doc_facts.py` keeps
decoding ONE block by streaming rather than loading a hundred megabytes to read
a few lines. Every reader listed in the delivery survey now goes through it.

**Two bounds, stated rather than buried.** `meetings/schemas.py:1171` is the
only mention inside a frozen directory and it is a DOCSTRING, not a reader — the
freeze forbids touching it, so that one prose reference still reads `.json`.
And `scripts/run_tournament.py`'s STAGED per-run sidecar is deliberately not
converted: nothing reads it, it is per-seed and never committed, and converting
it would reach into `atomic_write_report` and the progress digest — the staging
and resume machinery the recording depends on — for no delivery benefit.

**Why the committed rubric's staleness matters here too.** §2.1a found a
committed derived view that had silently stopped describing its own bytes. A
gzipped report is exactly as exposed to that failure, which is why the planted
test in `tests/eval/test_report_io.py` asserts the distinction directly: a
well-formed archive of the WRONG payload reads back cleanly and is still wrong.
Readability is not correctness, and only `--check` gates the second.

## 4. The AFTER column

Computed on the re-recorded bytes with the same shipped tool as §1, nothing
redefined:

```
$ uv run python scripts/publish_process_scorecard.py
Wrote docs/process-scorecard.md and docs/process-scorecard.json: 3630 ballots over
676 meetings; grounded 2434/3630; deviating EJECTs 178/1775; manufactured flags
0/74; role-correctness is reported and gates nothing.
$ uv run python scripts/publish_process_scorecard.py --check
--check: docs/process-scorecard.md and docs/process-scorecard.json are consistent
with the committed recordings.
```

Every cell below is copied from `docs/process-scorecard.md` (after) and §1.2 /
§1.3 (before); none is computed here. 300 games in both columns; 672 → 676
meetings; 3,631 → 3,630 ballots (2,146 → 2,098 EJECT, 1,485 → 1,532 SKIP).

### 4.1 The before/after table

Each cell reads **before → after**. `s9` is `samples/9p2i`, `c9`
`ml_corpus/9p2i`, `s4` `samples/4p1i`, `c4` `ml_corpus/4p1i`.

| # | row | pooled | `s9` | `c9` | `s4` | `c4` |
|---|---|---|---|---|---|---|
| 1 | grounded, EJECT | 2078/2146 = 0.9683 → **2083/2098 = 0.9929** | 507/527 = 0.9620 → 494/496 = 0.9960 | 1455/1499 = 0.9706 → 1476/1487 = 0.9926 | 50/51 = 0.9804 → 49/49 = 1.0000 | 66/69 = 0.9565 → 64/66 = 0.9697 |
| 1 | grounded, SKIP | 0/1485 **by instruction** → **351/1532 = 0.2291** | 0/342 → 79/349 = 0.2264 | 0/1017 → 230/1052 = 0.2186 | 0/66 → 23/68 = 0.3382 | 0/60 → 19/63 = 0.3016 |
| 1 | grounded, all ballots | 2078/3631 = 0.5723 → **2434/3630 = 0.6705** | 507/869 = 0.5834 → 573/845 = 0.6781 | 1455/2516 = 0.5783 → 1706/2539 = 0.6719 | 50/117 = 0.4274 → 72/117 = 0.6154 | 66/129 = 0.5116 → 83/129 = 0.6434 |
| 2 | argmax-independence: deviating share of crew EJECTs | 116/1811 = 6.4% → **178/1775 = 10.0%** | 31/434 = 7.1% → 31/413 = 7.5% | 81/1270 = 6.4% → 147/1264 = 11.6% | 3/47 = 6.4% → 0/43 = 0.0% | 1/60 = 1.7% → 0/55 = 0.0% |
| 2 | argmax-independence: role-correct, followers vs deviators (chance) | 94.5% vs 7.8% (31.6%) → **1537/1597 = 96.2% vs 17/178 = 9.6% (31.5%)** | 88.8% vs 6.5% → 359/382 = 94.0% vs 3/31 = 9.7% (29.8%) | 96.1% vs 8.6% → 1081/1117 = 96.8% vs 14/147 = 9.5% (30.6%) | 95.5% vs 0/3 → 42/43 = 97.7% vs 0/0 n/a | 100.0% vs 0/1 → 55/55 = 100.0% vs 0/0 n/a |
| 3 | manufactured-contradiction rate (numerator/denominator; not evaluable) | 159/192 = 0.8281; 32 → **0/74; 74 — measured nothing** | 53/57; 4 → 0/17; 17 | 105/134; 28 → 0/57; 57 | 0/0; 0 → 0/0; 0 | 1/1; 0 → 0/0; 0 |
| 4 | unexplained-decision rate | 20/3631 = 0.0055 → **17/3630 = 0.0047** | 4/869 → 5/845 | 15/2516 → 12/2539 | 1/117 → 0/117 | 0/129 → 0/129 |
| 5 | evidence-quality mix (vent / contradiction / first-hand / hearsay / unevidenced, over ejections) | 333 / 10 / 75 / 8 / 3 of 429 → **326 / 5 / 70 / 10 / 0 of 411** | 68/7/17/3/0 of 95 → 70/2/16/2/0 of 90 | 220/3/52/4/2 of 281 → 211/3/51/8/0 of 273 | 19/0/4/1/0 of 24 → 19/0/1/0/0 of 20 | 26/0/2/0/1 of 29 → 26/0/2/0/0 of 28 |
| 6 | rationale faithfulness (TOKENS; not evaluable) | 2874/2874 = 1.0000; 757 → **3015/3017 = 0.9993; 613** | 705/705; 164 → 708/708; 137 | 2014/2014; 502 → 2135/2136; 403 | 72/72; 45 → 80/81; 36 | 83/83; 46 → 92/92; 37 |
| 7 | agent-authored share | 3531/3631 = 0.9725 → **3609/3630 = 0.9942** (see 4.2) | 842/869 → 841/845 | 2446/2516 → 2522/2539 | 116/117 → 117/117 | 127/129 → 129/129 |
| 8 | wrong-but-believable rate — reported, never penalised | 383/2146 = 0.1785 → **462/2098 = 0.2202** | 113/527 → 119/496 | 251/1499 → 327/1487 | 9/51 → 7/49 | 10/69 → 9/66 |
| 9 | role-correct ejection rate — **reported beside, gating nothing** | 383/429 = 0.8928 → **369/411 = 0.8978** | 82/95 → 81/90 | 252/281 → 241/273 | 20/24 → 20/20 | 29/29 → 27/28 |

### 4.2 The two cells that carry their reading

**Row 1, SKIP, before: `0` BY INSTRUCTION.** The pre-wave ballot template told
the voter to leave a SKIP's basis empty, so no committed SKIP could carry one
(§1.2). The after cell, 351 of 1,532, is the first measurement of what the
agents do once the instruction asks for a basis. It is not a measured gain
over zero; the zero was never a measurement.

**Row 7, after: `1.0` BY CONSTRUCTION — for the rewrites the wave retired, and
not for the whole row.** The card anticipated an after cell of 1.0 once the
guards label rather than re-aim. The bytes say **0.9942**, and the difference is
stated rather than rounded away. The two rewrite classes that made an evidence
judgement — `under_gate_redirect` (83 before) and `uncited_coerced` (6 before)
— read **0 after, by construction**: the grounded-SKIP card deleted both paths,
and the redirect-marker census reads 0 on every set. What remains is the two
rewrites that card KEPT on purpose and named as the only target-rewriting paths
(`TestTheOnlyTargetRewrites`): `invalid_target` **8** (an illegal target cannot
be tallied, so it records SKIP, labelled) and `teammate_coerced` **13** (the
teammate firewall, a role rule the voter was told in its own prompt, not an
evidence judgement). Before, those two read 4 and 7. So the guarantee is exactly
this strong: **no ballot on these bytes was re-aimed on an evidence judgement**;
21 were re-aimed by the two rules that are not about evidence. Citation-only
rewrites, which never count against the share, fell 13 → 5.

### 4.3 Row 3: a rate over nothing, and the census that carries the reading

**Row 3 measured nothing on these bytes, and it must not read as a fall from
0.8281 to 0.0000.** Every one of the 74 alibi-class flags is NOT EVALUABLE, so
the evaluable denominator is **zero**. The basis test that owns the split is
`eval.process_scorecard._flag_scored_claim_truth` (§1.4): a claim whose route
carries more than one maximal stay is refused, because a recorded flag names the
claim's event id and not the stay it rests on. The not-evaluable flags, split by
cause with the shipped helpers (count-only, out of tree, no instrument changed):

| set | alibi-class flags | rest on a multi-stay route | name no self-alibi speaker | evaluable |
|---|---|---|---|---|
| `samples/9p2i` | 17 | 13 | 4 | 0 |
| `ml_corpus/9p2i` | 57 | 29 | 28 | 0 |
| `samples/4p1i` | 0 | 0 | 0 | 0 |
| `ml_corpus/4p1i` | 0 | 0 | 0 | 0 |
| **pooled** | **74** | **42** | **32** | **0** |

The same split over the preserved pre-record bytes reads 160 evaluable and 32
naming no self-alibi speaker (4 in `samples/9p2i`, 28 in `ml_corpus/9p2i`) —
the same class and, set by set, the same count as after. So the whole collapse
of the evaluable denominator, 160 → 0, is the 42 multi-stay refusals plus the
flags that stopped being minted at all; the refusals are new with the route
claim, exactly as §1.4 and §7.1 anticipated.

**The absolute census, after**, beside the before census of §1.4 (the same
count-only reader, the same shipped `maximal_stays`):

| set | meetings | alibi_conflict | alibi_vs_sighting | alibi_vs_physical | vent_sighting | alibi-class | all flags | flags/meeting | alibi/meeting |
|---|---|---|---|---|---|---|---|---|---|
| `samples/9p2i` | 151 → 145 | 21 → 0 | 31 → 11 | 5 → 6 | 90 → 90 | 57 → **17** | 147 → 107 | 0.9735 → 0.7379 | 0.3775 → **0.1172** |
| `ml_corpus/9p2i` | 439 → 449 | 40 → 3 | 86 → 35 | 8 → 19 | 315 → 317 | 134 → **57** | 449 → 374 | 1.0228 → 0.8330 | 0.3052 → **0.1269** |
| `samples/4p1i` | 39 → 39 | 0 → 0 | 0 → 0 | 0 → 0 | 20 → 20 | 0 → 0 | 20 → 20 | 0.5128 → 0.5128 | 0 → 0 |
| `ml_corpus/4p1i` | 43 → 43 | 1 → 0 | 0 → 0 | 0 → 0 | 28 → 28 | 1 → **0** | 29 → 28 | 0.6744 → 0.6512 | 0.0233 → 0 |
| **pooled** | **672 → 676** | **62 → 3** | **117 → 46** | **13 → 25** | **453 → 455** | **192 → 74** | **645 → 529** | **0.9598 → 0.7825** | **0.2857 → 0.1095** |

**Self-alibi claim census**: 1,003 claims with **0** multi-stay before; **1,021
claims, 959 multi-stay (0.9393)** after (`samples/9p2i` 231 of 240,
`ml_corpus/9p2i` 675 of 715, `samples/4p1i` 28 of 35, `ml_corpus/4p1i` 25 of
31). The scorecard's own claim census beside it: claims false under the envelope
test 106 → 11, false under the strict test (in that room at no tick the claim
covers) 2 → 0, and alibi claims naming another player 13 → 0.

**What this census can and cannot say.** At a comparable meeting count (672 →
676) the alibi-class flags fell from 192 to 74 and their rate per meeting from
0.2857 to 0.1095, while the vent flags — which the route claim does not touch —
held at 453 → 455. The `alibi_conflict` kind nearly vanished (62 → 3). That is
the route claim's thesis, that an honest multi-room mover stops minting flags,
read off absolute counts rather than a rate, and §6.1 shows it on a single
featured game. It is NOT a measurement of how many of the remaining 74 flags
are manufactured: row 3 cannot say, and no number here stands in for it. The
`alibi_vs_physical` kind rose, 13 → 25; this record publishes that and does
not explain it away.

### 4.4 The other rows, read without a verdict

- **Row 1**: grounded EJECT rose to 0.9929 pooled; the all-ballots cell rose
  0.5723 → 0.6705 almost entirely through the SKIP half.
- **Row 2**: deviations from the rendered suspicion argmax rose, 6.4% → 10.0%
  pooled, with most of the rise in `ml_corpus/9p2i` (6.4% → 11.6%). The
  direction memo asks that deviations be **at least as accurate** as follows;
  they are not — 9.6% role-correct against 96.2%, and below the 31.5% chance
  line computed over the same ballots. Reported, not ruled on. The 4p1i sets
  carry no deviator at all after.
- **Row 4**: 17 unexplained decisions, all SKIPs naming no player; no EJECT
  with an unresolving citation (2 before).
- **Row 5**: the unevidenced band emptied (3 → 0); vent flags carry 326 of 411
  ejections (79%), against 333 of 429 (78%) before.
- **Row 6**: two extracted tokens of 7,458 are absent from what their voters
  held, against 0 of 6,796 before — two ballots. Row 6 tests tokens, not
  propositions (§1).
- **Row 8**: 0.1785 → 0.2202; the owner's preferred wrong case, reported and
  never penalised.
- **Row 9**: 0.8928 → 0.8978, **reported beside, gating nothing**.

## 5. The re-record log, and the operating events

**Three seeds re-recorded, all on leg 2 and all for the one reason the card
sanctions** — a `(deadline_default)` row (event 3). No seed re-recorded for any
other reason, and none to recover from a stall; there was no stall. The events
below are logged as they happened rather than smoothed away.

| leg | transients (handled retries) | `(deadline_default)` re-records | vacuous probe |
|---|---|---|---|
| 1 `samples/9p2i` | 1 — seed 25, attempt 1 of 8 | 0 | no |
| 2 `ml_corpus/9p2i` | 1 — seed 1104, attempt 1 of 8 | 3 — seeds 1030, 1059, 1142 | no |
| 3 `samples/4p1i` | 0 | 0 | **yes** — seed 0, re-run on seeds 0-3 |
| 4 `ml_corpus/4p1i` | 0 | 0 | no |

1. **Leg 1, seed 25 — one handled transient.** Attempt 1 of 8 failed with
   `RuntimeError: Featherless response carried no choices (model=
   'Qwen/Qwen3.6-27B'); refusing to record an empty completion.` The recorder
   retried after 15 s and the seed landed on the retry. Measured against the
   stop rule it trips nothing: the cost stayed `0.0000`, it was attempt 1 of 8
   rather than a refusal surviving the budget, and it was not a stall — the
   other worker completed seeds throughout, including one 12 s later. The
   client refusing to record an empty completion is the guard working.

2. **Leg 2's probe phase exited non-zero, by design.** Recording the first seed
   alone (`--seeds 1000`) leaves a 1-of-150 set, and the corpus recorder's
   freeze guard refused it: `check_seed_count: ... is not the exact locked set
   1000..1149 (150 games) — 149 MISSING seed(s) ... Refusing to freeze a
   short/dirty corpus`. That is the documented resume path, not a failure: seed
   1000 recorded cleanly in 227 s at `$0.0000`, its MANIFEST row was written,
   the honesty probe folded it (two meetings, so not vacuous), and the leg's
   main phase then reported `Resume: 1/150 selected seed(s) already recorded;
   149 remaining` and re-proved that replay's provenance before trusting it.

3. **Leg 2, seeds 1030, 1059 and 1142 — three `(deadline_default)` re-records,
   cause logged as it happened.** The main phase recorded 149 of 149 and then
   REFUSED TO FREEZE at 14:24:33Z: `check_replay_provenance: 6 violation(s)`,
   two per seed — each replay carried one `deadline_default` failed-call row
   and, with it, the `(deadline_default)` sentinel recorded as a non-baseline
   model. A defaulted turn leaves a fallback husk in the transcript instead of
   model output, so the guard's own words apply: presence alone must not make it
   a corpus game. The three husks were removed and those three seeds alone
   re-recorded (`--seeds 1030,1059,1142`, 505 s, 585 s and 302 s, every one
   meeting-bearing, 14:25:27Z to 14:38:58Z); the plain `--set 9p2i` run then
   skipped all 150 present replays, re-proved each one's provenance and froze.
   Against the previous record's 5 over 250 games, this one carried 3 over 150.
   Nothing about them tripped the stop rule: cost stayed `0.0000`, no refusal
   survived the retry budget, and the leg never stalled.

4. **Leg 2, seed 1104 — the leg's one handled transient.** Attempt 1 of 8,
   `Featherless response carried no choices`, landed on the retry; the provider
   was otherwise clean for 447 minutes.

5. **Leg 2's push was refused, and the delivery path changed (§3.5).** The
   derived eval report of `ml_corpus/9p2i` reached 102.70 MB against GitHub's
   100 MB per-file limit. The leg's commit was re-made without the report
   (never pushed with it, so no published history was rewritten) and pushed as
   `7fd7040f`; the owner then chose gzip for all four reports.

   **One consequence was missed at the time: `samples/4p1i` stamps the
   refused commit.** The refused commit was `5c75028e` (made 14:40:29Z). Leg 3
   opened at 14:41:58Z, before the re-made `7fd7040f` (14:46:18Z), and every
   leg-3 recorder run started in that gap. `scripts/refresh_samples.sh:693`
   reads `HEAD` once when a run starts. So all 50 rows of
   `replays/samples/4p1i/MANIFEST.md` stamp `git_sha` `5c75028e`. That commit
   was never pushed, is not an ancestor of this branch and is held by no remote
   ref, so a clone cannot resolve it. Its tree is `7fd7040f`'s plus the one
   untracked report, so **the recording code state of `samples/4p1i` is
   `7fd7040f`**. Measured in the recording checkout, where the commit still
   exists as an unreachable object:

   ```
   $ git log -1 --format='%h %p' 5c75028e ; git log -1 --format='%h %p' 7fd7040f
   5c75028e 820704be
   7fd7040f 820704be
   $ git diff --stat 5c75028e 7fd7040f
    replays/ml_corpus/9p2i/tournament-eval-report.json | 235845 ------------------
    1 file changed, 235845 deletions(-)
   $ git show 5c75028e:replays/ml_corpus/9p2i/tournament-eval-report.json | shasum -a 256
   9b17bf9c5ed7a61ed624cf159ede1103b53cdf210947816b71b57bb105f28848  -
   ```

   Both commits share the parent `820704be`, and the only difference is that
   report. Its bytes are the `ml_corpus/9p2i` report that §3.5 delivers gzipped
   (the same sha256). The MANIFEST is left as recorded and not hand-edited,
   like the corpus FROZEN lines of §7.2.

6. **Leg 3's first probe was VACUOUS and re-ran.** Seed 0 of `samples/4p1i`
   recorded an impostor win with zero meetings, so folding the honesty
   instruments on it would have certified nothing. Per the previous record's
   §0.2 rule 5 a meeting-free probe is recorded VACUOUS and never counted as a
   pass: seeds 1-3 recorded next (seeds 1 and 2 bore meetings) and the probe
   re-ran on that four-game fold (two meetings), clean — no raise, no
   unfoldable cell family. Seed 0 was kept, not re-recorded: it is a valid game
   that happens to hold no meeting. The previous record hit the same thing on
   the same leg; small 4p1i games often hold none (39 meetings over 50 games
   here).

7. **Legs 3 and 4 made zero provider retries.** Leg 4's probe phase exited 1 by
   design, exactly as leg 2's did (the freeze guard refusing a 1-of-50 set), and
   its probe seed bore a meeting.

## 6. The tour, and the ladder

### 6.1 The tour

Re-pointed by [the spectator card](../tasks/work/spectator-tour-and-alternatives.md)'s
measured criterion, re-run on the new bytes of both sample sets:

```
$ uv run python scripts/measure_featured_criterion.py
replays/samples/4p1i — 50 games
    role_proof flag   19 ejections  19 role-correct
    other flag         0 ejections   0 role-correct
    no flag            1 ejections   1 role-correct
  first meeting ejects on a role_proof flag: 19 of 50 games
replays/samples/9p2i — 50 games
    role_proof flag   70 ejections  70 role-correct
    other flag         2 ejections   1 role-correct
    no flag           18 ejections  10 role-correct
  first meeting ejects on a role_proof flag: 32 of 50 games
  no flag and no ejection anywhere: seeds [2, 4, 10, 46]
```

The eligible openers, derived with the same predicate `tests/api/test_sets.py`
re-implements: 9p2i seeds 0 1 3 5 6 8 11 15 16 17 18 19 20 21 22 23 24 25 27
28 29 31 32 33 34 35 37 41 43 45 48 49; 4p1i seeds 1 2 4 6 13 14 18 19 20 26
32 33 40 41 42 46 47 48 49. **Both heads stay eligible** (9p2i 23, 4p1i 2).

Each featured game, measured on the served replay (turns per meeting; flags;
the ejection per meeting):

| game | baseline 8 | baseline 9 | label |
|---|---|---|---|
| 9p2i 23 (head) | 4 meetings, 8/7/6/5; m0 vent, EJECT; m1 two weak alibi flags, SKIP; m2 none, SKIP; m3 vent, EJECT | 4 meetings, 8/7/6/5; m0 vent, EJECT; **m1 no flag**, SKIP; m2 none, SKIP; m3 vent, EJECT | kept, **second clause dropped** |
| 9p2i 13 | 3 meetings, 7/6/5 | **1 meeting, 7 turns**, no flag | **falsified; replaced by seed 0** |
| 9p2i 46 | 4 meetings, 6/5/5/4; one weak flag; two ejections | 4 meetings, 6/5/5/5; **no flag, all four SKIP** | **replaced by seed 29** |
| 9p2i 2 | 1 meeting, 7 turns, no flag | unchanged | true, kept |
| 9p2i 0 (new) | — | 3 meetings, 8/7/6; m0 vent, EJECT; m1 three weak alibi-vs-sighting flags, SKIP; m2 vent, EJECT | eligible opener |
| 9p2i 29 (new) | — | 4 meetings, 7/6/4/3; m0 vent, EJECT; m1 two cross-statement contradictions, EJECT; m2 none, SKIP; m3 vent, EJECT | eligible opener |
| 4p1i 2 (head), 11, 29 | one meeting each, three turns | unchanged (29 now skips its meeting, which its label never claimed) | true, kept |

**Seed 23's lost clause is game-level corroboration of §4.3.** The label read
"...and the meeting files that apart from one account merely contradicting
another", contrasting meeting 0's vent sighting with meeting 1's
`alibi_conflict` and `alibi_vs_sighting` flags. On the same seed, re-recorded,
meeting 1 carries no flag at all. Those two flags were the single-room envelope
artifacts the route claim exists to stop minting against honest movers; here
they stopped, on a game the tour leads with. The clause went because it was
false, and the census in §4.3 is the same movement counted across all 676
meetings.

**Labels, all spoiler-free** (no ending, ejection, winner or tally; no task or
audit IDs):

- 9p2i 23: "Four meetings, twenty-six spoken turns. A player reports seeing
  someone use a vent. Read which each ballot cites, and who else its voter
  weighed."
- 9p2i 0: "Three meetings, twenty-one spoken turns. A player reports seeing
  someone use a vent, and a later meeting's only flags are weak signals.
  Compare what each ballot cites in the two."
- 9p2i 29: "Four meetings, twenty spoken turns. Reported vent sightings, and a
  meeting whose flags are contradictions instead. Follow how the table turns
  sightings and statements into accusations."
- 9p2i 2 and the three 4p1i labels are unchanged.

Every countable claim in a label (meetings, turns, "vent", "only flags are weak
signals", "flags are contradictions", "no flagged contradictions") is read back
from the served replay by `tests/api/test_sets.py`, each clause with its own
planted failure.

**The head-card guard, proven in both directions** (`cd frontend && npm run
e2e`, `frontend/e2e/journey.spec.ts`): green on the re-pointed strip; with the
head label's promise planted as "No flagged contradictions." the guard fails
(1 failed / 7 passed, `journey.spec.ts:477`, expected 0, received 1); restored
byte-identically (`cmp`) it passes (8 passed). The opposite direction, a
flag-free game promoted to the head with a promise of flags, fails too
(2 failed / 6 passed) and was restored the same way.

**What the criterion could no longer isolate.** The planted rejections behind
the head pin were re-derived by measurement: seed 7 is the new isolating case
for the `role_proof` clause (its first meeting ejects an impostor two
cross-statement flags name, and no flag in it is role proof; weakening the
clause turns exactly that case green, 1 failed / 51 passed). No game in either
set now has a first meeting that ejects a crewmate on any flag, so the role
clause has no bracketing case of its own on these bytes; that gap is stated in
the test rather than papered over.

### 6.2 The ladder, and the cells the front door quotes

**The ladder tip stands at baseline 9.** It moves with this record rather than
with a relabel: the four sets above are the recording, and
`scripts/check_doc_facts.py`'s `_LADDER_TIP_AUDIT` names this document in the
same pull request. The owner's merge is what makes it the shown baseline.

**These are PUBLISHED CELLS, not bars.** This record pre-registered nothing, so
nothing below carries a verdict, a target or a pass/fail. They are published in
the shape the front door's fact checker reads, so the front door quotes a
committed source rather than a remembered one. Each is read off the four
rebuilt eval reports' `deduction.ejectee_proof_cross_tab` block (the partition
`scripts/build_sample_report.py` prints as "EJECTEE-proof partition"); the
before column is the baseline-8 record's own published cells
([`audit-phase-21-rerecord.md`](audit-phase-21-rerecord.md) §5.1). Intervals are
Wilson 95%.

#### Published cell 1 — non-direct conviction accuracy

The ejections the crew reached WITHOUT engine-certified proof of the ejectee's
role.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 14/27 = 0.5185 | **11/20 = 0.5500** [0.3421, 0.7418] |
| `ml_corpus/9p2i` | 32/61 = 0.5246 | **30/62 = 0.4839** [0.3641, 0.6055] |
| `samples/4p1i` | 1/5 = 0.2000 | **1/1 = 1.0000** [0.2065, 1.0] — ADVISORY |
| `ml_corpus/4p1i` | 3/3 = 1.0000 | **1/2 = 0.5000** [0.0945, 0.9055] — ADVISORY |
| **pooled** | **50/96 = 0.5208** | **43/85 = 0.5059** [0.4017, 0.6096] |

The pooled cell moved 0.5208 → 0.5059, inside overlapping intervals, and this
record has no power to call that movement real in either direction. It is
published unchanged.

The direct-proof cell stays perfect: **326/326 = 1.0000** pooled (70 + 211 +
19 + 26), against 333/333 before.

#### Published cell 2 — innocent ejections

| set | before | after |
|---|---|---|
| `samples/9p2i` | 13 | **9** |
| `ml_corpus/9p2i` | 29 | **32** |
| `samples/4p1i` | 4 | **0** |
| `ml_corpus/4p1i` | 0 | **1** |
| **pooled** | **46** | **42** |

Every innocent ejection still sits in the non-direct cell: the proof-present
cell is innocent-free on both records, 0 of 326 here and 0 of 333 before. The
two cells agree with each other by construction, and the arithmetic checks:
85 − 43 = 42.

#### The win split

| set | baseline-8 impostor rate | baseline-9 impostor rate |
|---|---|---|
| `samples/9p2i` | 30% (15/50) | **22% (11/50)** |
| `samples/4p1i` | 36% (18/50) | **36% (18/50)** |
| `ml_corpus/9p2i` | 24% (36/150) | **30% (45/150)** |
| `ml_corpus/4p1i` | 26% (13/50) | **28% (14/50)** |

Read from each set's `MANIFEST.md` `winner` column. Win split is not a gate and
is published only because the front door quotes it.

### 6.3 Pins this record re-derived and publishes as their source

`scripts/counterfactual_phase21.py` asserts four corroboration cells over the
pooled four-set walk, which the counterfactual audit's Errata E.2 published for
baseline 8. Re-derived by the script's own walk over these bytes, under the same
Errata E.2 rule; this section is now their committed source:

| cell | baseline 8 | baseline 9 |
|---|---|---|
| accused without a first-hand source | 460 / 1,525 | **529 / 1,516** |
| ejected without a first-hand source | 10 / 425 | **16 / 409** |
| ejected on an answering turn | 33 / 429 | **36 / 411** |
| ejected with a walkable pair | 79 / 429 | **69 / 411** |

Its `COMMITTED_INNOCENT_EJECTIONS` pin now cites published cell 2 above (9, 32,
0, 1), which the script's own enumeration reproduces exactly.

### 6.4 What the new bytes falsified, left red and reported

Every test value that moved was re-derived from the new bytes through the
production computation and is listed old → new in the card's Results. The tests
below were NOT: each asserts a property that is no longer true of the committed
bytes, and re-pinning it would have meant deleting or weakening an assertion.
They stay red; `bash scripts/check.sh` fails on them, and on the ML tests of
§7.3, and on nothing else. None was caused by an edit here: the re-record moved
the world under them. The campaign tier, which `check.sh` excludes, had one more.
The third review round re-anchored it, and it follows the table with the
reversal the re-anchoring exposed.

| test | what the bytes now say |
|---|---|
| `tests/meetings/test_contradictions.py::TestGroundedProsecutionCommittedCensus::test_the_fully_grounded_leg_drops_the_whole_class` | "Entirely weak" is false: the fully grounded re-derivation now keeps 8 STRONG flags beside 113 weak (was 0 and 120), all 8 on impostor subjects, all in meetings where movement diverges. |
| `…::TestGroundedProsecutionInjusticeShapes::test_no_committed_ejection_rides_a_strong_sighting_flag` | "The class is empty" is false: 5 ejections ride a strong sighting flag, every ejectee an impostor; 4 exist only in the records-free re-derivation, 1 (`ml_corpus/9p2i` seed 1041 meeting 1) in the recording. |
| `tests/meetings/test_transcript.py::TestCommittedBytesArtifactCollapse::test_rederivation_diverges_only_at_the_repaired_sites` | 4 new re-derived pairings are neither a weak proxy re-target nor the corridor band (seed 7 meeting 0 twice, one of them STRONG; seed 32 meeting 0; seed 38 meeting 1). |
| `tests/agents/test_reported_testimony.py::test_reported_rows_survive_in_every_candidate_bucket` | The render keeps 5,927 of 7,539 offered testimony rows = 0.786 in the >150-candidate bucket, under the 0.80 floor (0.962 before; the rows offered in that bucket doubled). A render-budget question for the owner. |
| `tests/eval/test_evidence_honesty.py::test_the_instrument_and_the_detector_read_one_adjacency_rule` | The detector and the adjacency instrument measure a multi-leg route from different points: all 29 adjacent flags the detector keeps STRONG sit on multi-leg routes, and for 26 the sighting is within one tick of an INNER leg boundary but more than one tick from the route's outer ends, which the detector measures from. Single-leg routes never exposed the difference. |
| `…::test_the_band_change_not_the_fold_is_what_costs_first_hand_coverage` | With the old reported band restored, the fold now renders 32,123 rows against 32,037 recorded — slightly more, not fewer — though it still covers more first-hand ticks (28,359 against 20,629). |
| `tests/api/test_view_model.py::test_report_tick_fog_keeps_the_reported_body` | **A real viewer gap the new bytes exposed.** At seed 13 tick 13 a body report and the game-ending kill share a tick; `api/replay_loader.py` restores the reported body only in MEETING phase, so the reporter's fogged view drops it (1 of 136 body reports). A product fix, out of this record's scope. |
| `tests/scripts/test_counterfactual_phase21.py::test_the_memo_table_equals_a_live_four_set_run`, `::test_the_memo_marks_every_advisory_cell` | They hold `audits/audit-phase-21-counterfactual.md`, a baseline-8 memo, to a live run on the committed bytes: 42 of 43 pooled cells differ. A new table or erratum, or a re-scoped drift gate, is the owner's call. |

**The campaign tier's tie-break census: re-anchored, and a reversal for the
owner.** `uv run pytest -m campaign` runs the frozen campaign families that
`check.sh` leaves out (§7.1 and §7.3 give the whole tier).
`tests/training/test_surrogate_fidelity.py::test_the_tie_break_moves_the_decision_census_but_not_the_ranking`
asserts that FO-6's decision census moves between the lowest and the highest
tied tau while every ranking and calibration channel stays identical, on "the
set where the census actually moves". That set was `samples/9p2i`, and the new
bytes stopped the move there. Measured on each committed set through
`training.surrogate.fidelity.fo6_rebaseline` (the shipped head, which takes the
highest tied tau) against the test's own lowest-tied-tau control:

| set | predicted ejections, low / high tau | ejection meetings predicted SKIP, low / high | skip-vs-eject accuracy, low / high | ranking and calibration |
|---|---|---|---|---|
| `samples/9p2i` | 7 / 7 | 86 / 86 | 0.3862 / 0.3862 | identical |
| `samples/4p1i` | 18 / 16 | 9 / 10 | 0.5897 / 0.5897 | identical |
| `ml_corpus/9p2i`, test side | 5 / 0 | 50 / 52 | 0.4362 / 0.4468 | identical |
| `ml_corpus/4p1i`, test side | 5 / 5 | 1 / 1 | 0.75 / 0.75 | identical |

On baseline 8, `samples/9p2i` read (10, 0), 90 and 95. The third review round
re-anchored the test on `samples/4p1i`, which carries the shape the test names:
the census moves (18 against 16), the ranking does not, and the two accuracies
are equal (23/39 each), because the one true ejection the low tau catches costs
it one correct skip. Every assertion is unchanged, including
`new.skip_vs_eject_accuracy <= old.skip_vs_eject_accuracy`, and the card lists
the move as a RE-ANCHOR.

**The reversal, for the owner's ruling.** The test's docstring said the tuned
head "never scores BETTER". On the `ml_corpus/9p2i` test side, the population
the GO bar is measured on, it does. The shipped head ejects on 0 meetings
against the low tau's 5, and scores 0.4468 (42/94) against 0.4362 (41/94): the
low tau's 5 ejections catch 2 true ejections and cost 3 correct skips. So the
never-better claim is false on the corpus. The docstring now scopes the claim to
`samples/4p1i` and names this reversal. The neighbouring test's comment said the
corpus test side decides identically across the tied plateau; it now says the
side does not. No test asserts on the corpus's accuracy either way, so no
assertion was weakened. The owner rules on whether the higher-tau tie-break
stands when the tuned head scores better on the measured population, or whether
the claim is re-scoped. This is routed with the re-ground (§7.1).


**Frozen rather than re-pinned: four exhibits the new bytes no longer carry.**
Seven of the eight tests above assert on a shape that the route claim or the
labelling guards removed from every committed meeting. Each now reads that
shape's baseline-8 recording, frozen under `tests/fixtures/baseline8_exhibits/`
from the `main` commit `39a568c6`. The README there gives each file's source,
transform and sha256, and a snippet that rebuilds all five files from git byte
for byte. Every assertion is unchanged, and all seven pass on the unchanged
detector and loader:

| exhibit | tests reading it | what the new bytes say |
|---|---|---|
| seed 41 meeting 2, the line verbatim | `tests/meetings/test_contradictions.py::TestTheAlibiIsARoute` (the 3 red, and the 2 green ones that were running on a meeting which had lost its exhibit), and the honest-route sibling | meeting 2 carries 0 recorded flags and p-9 now states a six-leg route; no successor in 676 meetings |
| the 17 `samples/9p2i` meetings holding the 21 `alibi_conflict` flags, model calls emptied | `tests/meetings/test_transcript.py::…::test_seed25_m0_weak_cross_speaker_conflict_not_retargeted` | `samples/9p2i` carries 0 `alibi_conflict` flags, and the only 3 in the four sets are single-author |
| all 190 meetings of both sample sets, model calls emptied | `tests/meetings/test_reported_testimony_derive.py::TestRoutesOverTheCommittedRecord` (the 2 red and the view check) | every one of the 1,021 committed alibis is a route, and production reduces a route to one statement per maximal stay, which differs from one per leg in 3 of 184 meetings; the whole-line round trip still reads the live sets and holds |
| `samples/9p2i` seed 11 and its roster, verbatim | `tests/api/test_view_model.py::test_finale_recap_flags_a_rewritten_ballot_and_withholds_judgment` | all 21 target rewrites (8 `invalid_target`, 13 `teammate_coerced`) tally SKIP; the one on a last meeting (`ml_corpus/9p2i` seed 1056) is among them |

The eighth, `tests/api/test_evidence_mechanisms.py::test_the_flip_search_finds_exactly_the_named_meetings`,
was re-pinned to its measured value. Its walk finds no statement-pair
wrongful conviction on these bytes, so `_STATEMENT_PAIR_CONVICTIONS` is now the
empty set (it named seed 41 meeting 2). Empty is the stricter growth tripwire,
because any meeting that convicts this way now fails it. The planted case still
proves the predicate fires, and the baseline-8 loss is still stated, on the
frozen seed-41 line through the loader's own flag projection: two STRONG
cross-statement `alibi_vs_sighting` flags naming the ejected p-9.

**Restated rather than re-pinned, for the owner to confirm.** Where a pinned
example seed no longer carried its shape, the same property was re-stated on a
game that does, found by measurement: the wrong-ejection finale (seed 47 → 5),
the weak-only innocent ejection (samples seed 47 → `ml_corpus/9p2i` seed 1135),
the role-proof isolating case (seed 10 → 7), the gate-marker chip (a
redirect chip, retired by ruling D6, → seed 7's invalid-target chip), the
reporter-justice risk cases (swapped between the two 4p1i sets), the guard-drop
reconciliation (now non-empty on one set, `ml_corpus/9p2i`, where it was
non-empty on all four), and the legacy-projection tests of
`build_sample_report` (every committed report is now stamped, so they run on a
committed game with its stamps cleared). The card's Results lists each.

## 7. What this record does not discharge

### 7.1 For the owner — three follow-ups this record exposes, and does not take

**First: re-ground the ML fits on the baseline-9 corpus — the successor of Task
21.17.** The committed surrogate, conviction and composed fits were ground by
Task 21.17 on the baseline-8 `replays/ml_corpus/9p2i`. This record replaced
that corpus, and its card forbids touching a fit, an artifact or
`BAKEOFF_BASELINE_ID`, so the fits now describe games that are no longer in the
tree. §7.3 quantifies every consequence: the offline
`scripts/verify_ml_evidence.py` rows that FAIL, and the tests that load a fit
through its corpus fence and are refused. **Task 21.17 deleted the STALE amnesty
the previous re-record leaned on** ("so no future re-record can reach for a
row-scoped downgrade again"), so there is no honest way to mark these rows as a
declared gap here: they FAIL, and they stay red until the re-ground. Recommended
as **the first card after this pull request merges**, on the SAME baseline-9
bytes — re-fit by each instrument's committed recipe, re-derive the verdicts and
reports, move `BAKEOFF_BASELINE_ID` with the fits, exactly as 21.17 did for
baseline 8. It is a re-fit, not a re-record, and spends no model call.

**The campaign tier goes with the re-ground, and this record does not
discharge it.** `bash scripts/check.sh` runs the default tier only. The frozen
campaign families run under `uv run pytest -m campaign`, which
`.github/workflows/campaign-tier.yml` runs weekly on `main` and on demand. On
the base `39a568c6` the tier reads 335 passed. At this record's head it reads
308 passed, 25 failed and 2 errors, all 27 in `tests/training`. So the first
scheduled run on `main` after the merge fails on them unless the re-ground
lands first. All 27 are the fits' corpus (§7.3), and the re-ground owns them.
Six more were re-derived from these bytes, and the card lists each. Two are
FO-6 pins that fit fresh on the committed table and load no artifact (second
review round). Three read both frozen fits on the re-recorded split through
`run_composed_fidelity` or its recompute, without editing an artifact (third
review round). The last is the tie-break census, re-anchored on `samples/4p1i`
(third review round). The re-anchoring exposed a reversal on `ml_corpus/9p2i`,
which needs the owner's ruling beside the re-ground (§6.4). The previous
re-record named the same tier as not
discharged (`audits/audit-phase-21-rerecord.md` §7 item 1), and it was green
again at this record's base.

**Second: the genuine-class integrity disagreement that floors the rubric.**
§2.1b names it in full. One of the gameplay extractor's self-checks reports that
its re-derived genuine-class census disagrees with the shipped
`compute_genuine_class_conversion` (`supplied 1/0, converted 1/0` on the final
bytes), and `experiments/lab/rubric_score.py::_facts_integrity_ok` turns any
such `FAIL` into a floor of 0 on **every** game's rubric score. Two production
computations disagree about the same quantity; this record does not decide
which is right, because that is instrument work and the instruments stay frozen
during a measurement.

Recommended as **a small card immediately after this pull request merges**: fix
the disagreement, then regenerate `results-rubric-score.json` on the SAME
baseline-9 bytes. It is a derived view, so that is a regeneration and **not a
re-record** — the highlights surface is restored without reopening this record
or spending a model call. Until then the committed rubric states what the
shipped tool computes on these bytes, which is a record; the file it replaced
described no bytes at all.

**Discharged 2026-09-23** by `tasks/work/rubric-genuine-class-selfcheck.md`, landed into this record's branch before it merges (owner delegation of 2026-09-23): the extractor's re-derivation was the wrong side, a transcript-only replica of the definition the shipped metric left at Task 21.7; it now reads the recorded flags by the one-home rule, every self-check passes, and the rubric is regenerated on these same bytes (5 of 50 games at 0.0, each a per-game railroad floor).

**Third: a per-STAY basis test for row 3, so a multi-stay route becomes evaluable.**
Today a recorded contradiction flag names the claim's event id, not the stay it
rests on, so `_flag_scored_claim_truth` refuses any claim with more than one
maximal stay rather than risk filing a caught lie as manufactured (§1.4). That
refusal was decided deliberately by the alibi-as-route card and is correct for
the instrument as it stands. Its cost only becomes visible now: the route claim
is what makes multi-stay accounts common, so the very change row 3 exists to
measure is the change that moves claims out of row 3's denominator.

The fix is to attribute a flag to the stay it was minted against, and then score
per stay. That is **a new card after this one**, and it is **never a re-score of
this record**: this record reads each recording as recorded, and a later
instrument reads later bytes. Nothing here builds it, and nothing here is
blocked on it — the absolute counts in §1.4 and §4 carry the reading in the
meantime. §4.3 shows why it matters: on these bytes row 3's evaluable
denominator is zero.

### 7.2 Deliberate staleness, named rather than hidden

- **`meetings/schemas.py:1171`** is a docstring naming
  `tournament-eval-report.json`, the one mention of the report inside a frozen
  directory. It is not a reader, and the freeze forbids the edit, so it still
  says `.json` until the freeze lifts.
- **`scripts/run_tournament.py`'s staged per-run sidecar** stays uncompressed:
  nothing reads it, it is per-seed and never committed, and converting it would
  reach into the staging and resume machinery the recording depends on (§3.5).
- **The lab probes under `experiments/lab/`** that open
  `tournament-eval-report.json` by name (`forward_redesign_*`,
  `inference_feasibility_probe.py`, `visibility_probe.py`) are historical lab
  scripts no gate runs; they would need the `eval/report_io.py` reader to run
  on today's tree, and are left as they stand.
- **The corpus FROZEN lines carry a stale label.**
  `scripts/record_ml_corpus.sh:1066` hard-codes "Task 15.12, baseline-8
  re-record per Task 21.15" into the line it appends at the freeze, so both
  committed corpus MANIFESTs say that of baseline-9 bytes. The line is the
  recorder's output and the MANIFEST is fingerprinted: relabelling it by hand
  would re-fingerprint the corpus, and editing the recorder's string is outside
  the one edit this card allows the recorders. Routed to the owner as a
  one-line recorder fix before the next corpus recording.
- **Frozen prose that now describes history.** `meetings/manager.py` (about
  lines 330 and 425) cites 83 and 6 committed ballots carrying the markers
  ruling D6 retired; these bytes carry none. `orchestrator/game.py:423` still
  says there is no separate archived v4 set, true and dated. The freeze forbids
  both edits.
- **Mechanisms with no committed consumer left.** `scripts/build_sample_report.py`'s
  historical-projection branch (every committed report is now stamped, so none
  is legacy-shaped; its tests run on a committed game with the stamps cleared),
  and the ruling-D6 reconstruction accommodation in
  `tests/meetings/test_prompt_byte_golden.py` (no committed ballot carries a
  retired marker). Retiring either is a decision, not a re-pin; they are named
  here and left.
- **Historical records keep their baseline-8 fingerprints**:
  `audits/tactical-gameplay/held-out.json` and
  `tasks/work/portfolio-evidence-experience.md` describe the bytes of their own
  day and were not edited.

### 7.3 Limitations, stated at the strength the code delivers

- **The rubric is zeros, and the viewer shows them.** Complete by the card's
  letter, degraded by the pre-existing self-check failure (§2.1b, §7.1 second
  item). Because the regenerated rubric now matches its recording, the served
  view is fresh rather than stale, so every `samples/9p2i` card — in the local
  viewer and in the published demo bundle — shows a "0/100" pacing badge where
  the stale rubric showed "score unavailable". The badge is labelled an
  internal heuristic; it is still a visible consequence of shipping the zeros,
  and the owner's merge publishes it.
- **Nine tests outside the ML set stay red** because the new bytes
  falsified what they assert (§6.4); `check.sh` fails on them and on the ML
  tests below, and on nothing else. Eight more now read frozen baseline-8
  exhibits or a re-pinned empty set (§6.4). In the campaign tier, which
  `check.sh` does not run, the one falsified property, the tie-break census,
  was re-anchored on `samples/4p1i` in the third review round. The reversal
  the re-anchoring exposed on `ml_corpus/9p2i` is reported for the owner
  (§6.4).
- **The ML fits are not grounded on these bytes** (§7.1 first item), and the
  gate says so rather than hiding it: the rows and tests below stay red.

  **Why no row reads STALE.** The previous re-record re-derived only the
  measured side of each pinned pair and moved a status to STALE where the
  verifier itself returned it, through a declared grounding gap keyed to the
  two corpus digests. Task 21.17 deleted that mechanism outright when it
  re-ground the fits, "so no future re-record can reach for a row-scoped
  downgrade again": the status vocabulary is OK / FAIL / ABSENT / INFO, and
  `git log -S` shows nothing has re-added a declaration since. So nothing here
  is marked STALE, and nothing was invented to mark it.

  `uv run python scripts/verify_ml_evidence.py`, offline (never `--complete`):
  61 checks, 36 OK, 13 FAIL, 7 ABSENT, 5 INFO, exit 1, measured before the
  close recomputed the registry rows. The corpus on disk fingerprints to
  `6536c68c…`; both committed fits record `cc54d3c0…`, the baseline-8 corpus.
  Every drifted verdict field is corpus-derived, none corpus-independent, and
  the weight-hash rows, the composed manifest (8/8) and the adoption
  constraints all read OK.

  | # | row | measured on baseline 9 | frozen committed figure | why the replaced corpus explains it |
  |---|---|---|---|---|
  | 1 | fit-corpus identity fingerprint | `6536c68c…` | `cc54d3c0…` | the record replaced the 150 replays and the MANIFEST of `ml_corpus/9p2i`; only the corpus digest differs, no weights, set or version keying |
  | 2 | ML grounding | `6536c68c…` on disk | surrogate and conviction both fitted on `cc54d3c0…` | both fits were made on the baseline-8 corpus |
  | 3 | surrogate top-1 (ranking) | 0.8846 (46/52) | 0.8246 (47/57) | the frozen weights scored on the re-recorded held-out split |
  | 4 | surrogate SKIP-vs-eject | 0.4894 (46/94) | 0.3956 (36/91) | the same, over 94 re-recorded test meetings |
  | 5 | surrogate verdict.json reproduces | 15 of 31 fields | 31 | the 16 differing fields are all corpus-derived |
  | 6 | conviction flag-count Spearman | 0.8191 | 0.6670 | frozen conviction weights on the new test meetings |
  | 7 | conviction conversion accuracy | 0.9255 (87/94) | 0.9451 (86/91) | the same |
  | 8 | conviction verdict.json reproduces | 11 of 21 fields | 21 | the 10 differing fields are all corpus-derived |
  | 9 | composed decision accuracy | 0.8404 | 0.9011 | the composed runner over both frozen fits on the new meetings |
  | 10 | composed exact-outcome match | 0.8298 | 0.8352 | the same |
  | 11 | composed convicting top-1 | 0.8846 | 0.8246 | the same |
  | 12 | composed verdict.json reproduces | 9 of 17 fields | 17 | the 8 differing fields are all corpus-derived |
  | 13 | in-tree family inventory | fixtures 2,196,053 B; audits growing | 2,196,250 B; 26,571,844 B | NOT an ML row: `docs/artifacts.md` lagged this branch (the regenerated W2 baseline fixture, the growing audit); recomputed at the close, after which the row reads OK |

  **A finding that belongs with the re-ground.** Re-fitting the ballot
  surrogate fresh on these bytes (as its own tests do) gives a held-out top-1 of
  46/52, ABOVE the "honest ceiling" of 41/52 that
  `training/surrogate/fidelity.py` documents as the most any surrogate of its
  kind could reach, so `top1_ceiling_gap` reads −0.0962. No test asserts that
  bound for the ballot surrogate; the measured gap is pinned, and whether the
  ceiling still means what its docstring says is a question for the re-ground.
  The frozen committed surrogate reads the same 46/52 on the re-recorded split,
  through the composed path and through an independent recompute, against the
  same 41/52 ceiling. `test_composed_fidelity_scores_the_committed_test_split`
  pins both values as measured. On baseline 8 the two were equal, at 47/57.

  **The ML tests that stay red**, 45 before the registry recompute, 43 after
  it, and 41 after the third review round re-derived two, all for one cause,
  the fits' corpus:
  - 28 where the product's fit-corpus fence refuses the replaced corpus ("fit
    corpus or derivation drifted", recorded `cc54d3c0…`, measured `6536c68c…`):
    26 in `tests/training` — `test_surrogate_runner.py` (11, two at setup),
    `test_goodhart_probe.py` (9, seven at setup), `test_bakeoff_harness.py` (5),
    `test_model_evidence_provenance.py` (1) — and 2 outside it,
    `tests/eval/test_balance_eval_meeting_runner.py` and
    `tests/experiments/test_torch_probe_excluded.py`;
  - 7 that assert a frozen fit or a committed training artifact equals the live
    corpus (`test_surrogate_runner.py` 4, `test_conviction_model.py` 2,
    `test_bakeoff_methods.py`'s map-elites stamp 1), which could only be fixed
    under `training/artifacts/`. Two more were filed here until the third review
    round and now re-derive green without an artifact edit:
    `test_conviction_model.py::test_axis_three_is_a_floor_the_live_model_clears_on_all_three`
    and
    `test_surrogate_runner.py::test_no_go_verdict_holds_on_live_served_clamped_features`.
    Each reads the committed weights directly, without the fence, and scores
    them on the re-recorded held-out split through the production computation,
    so its value is an out-of-sample measurement of the frozen fit rather than
    an equality between an artifact and the corpus. The conviction weights read
    confusion (42, 5, 2, 45) over 94 meetings, accuracy 87/94 against the
    trivial 50/94, GO; the surrogate on live-served features reads 21 replaced
    cells, top-1 46, 90 predicted skips and 42 correct, the NO-GO axes unchanged;
  - 6 in `tests/scripts/test_verify_ml_evidence.py` whose OK controls run on the
    real corpus and now read FAIL on rows 1-2 or the recompute rows (the other
    2 of its 8 were the registry row 13, cleared by the recompute). Every status
    assertion was left at OK: moving one to FAIL would be asserting the defect.

  **And 27 more in the campaign tier** (`uv run pytest -m campaign`, which
  `check.sh` does not run; §7.1), for the same cause, all in `tests/training`:
  - 24 refused by the fit-corpus fence. 16 go through the surrogate's fence,
    all in `test_composed_runner.py`; two of those fail at setup
    (`test_full_composed_game_meetings_are_real_tallies` and
    `test_composed_goodhart_leg_runs_and_meters_both_counters`). 8 go through
    the conviction fence: `test_crew_scorer.py` 3, `test_crew_owned_tasks.py` 2,
    `test_coevo_driver.py` 2 and `test_anchor_study.py::test_run_anchor_study_ci_budget`.
    Six of the 24 test a different refusal, such as a corrupt weights file, a
    NO-GO verdict or a foreign policy, and fail because the fence refuses first;
  - 3 that hold a committed artifact or verdict to the live corpus. Each
    reads a committed fit or artifact under `training/artifacts/`, so it stays
    red until the re-ground. One is the committed composed `verdict.json` in
    `test_composed_runner.py`: its re-derivation differs on corpus-derived
    fields, among them decision accuracy, 0.8404 against 0.9011 (row 9 above).
    The other two are
    `test_anchor_study.py::test_committed_study_artifacts_are_the_baseline8_fit`
    (the study stamps substrate `c845602d…`, live `894f4daf…`) and
    `test_hall_of_fame.py::test_committed_pool_restores_only_with_explicit_historical_identity`
    (the map-elites pool stamps `4a25ccdf…`, live `8b174cab…`, the same stamp
    as the default tier's map-elites test).

  Three more `test_composed_runner.py` tests were filed with them until the
  third review round, and now re-derive green without an artifact edit. They
  score both frozen fits on the re-recorded split through
  `run_composed_fidelity` and the test's own recompute:
  `test_composed_fidelity_scores_the_committed_test_split` (94 test meetings,
  52 ejections, convicting top-1 46/52, top-1 ceiling 41/52, the tally
  ejecting on 4 and skipping 90),
  `test_composed_fidelity_top1_matches_an_independent_recompute` (52
  ejections, the recompute equal to the composed top-1) and
  `test_go_verdict_holds_under_the_live_teammate_exclusion_ranking`
  ((decision hits, ejections) (79, 52), top-1 46, exact 78, GO). The tier's
  falsified tie-break census is re-anchored and green. The reversal on
  `ml_corpus/9p2i` is in §6.4.

- **Row 3 is not evaluable on these bytes** (§4.3): 74 of 74 alibi-class flags,
  42 of them because the route claim made the accused's account multi-stay.
  The absolute census is the reading until a per-stay basis test exists.
- **A legibility residual the weighing card left for this record.** A
  contradiction evidence row renders as `not first-hand: <subject> stated it at
  this table`, and the sentence beside it is the DETECTOR's
  (`flag.description`), not the subject's: accurate about provenance, misleading
  about authorship. It is pinned
  (`test_a_flag_somebody_else_spoke_into_is_a_statement_here`), changing it is a
  prompt-byte change, and the prompt set is frozen under this record, so it
  ships in these bytes as the weighing card left it.
- **A pre-existing leak the wave recorded for the owner, not a wave item.** A
  contradiction flag's description carries the weak-reason vocabulary
  (`[weak signal: ungrounded sighting]` and its sibling), chosen by the
  SPEAKER's own private record and rendered to every voter in the ballot's
  contradictions block — measured by the weighing card's round 4 as moving in
  23 of 60 generated meetings when only other participants' private records
  change. Nothing in this record caused, widened or fixes it; whether a public
  detector may price a private record is the owner's to route.
- **The spend is counted from the committed bytes** (§2): it omits the three
  discarded first attempts of leg 2's seed repairs, whose token counts were not
  recoverable after the husks were removed. They were `$0.0000`.

## 8. The freeze, shown rather than asserted

`main` did not move during the window: `git log --oneline 39a568c6..origin/main`
prints nothing. The branch's own log, from the base to the close's last commit
before this section:

```
f4961ad1 fix: keep the ML page inside its word budget and follow the moved citation
c8c950fd frontend: re-derive the ballot-alternatives counts and regenerate the corpus fixtures
b064bcff publish: re-curate the three public cases on baseline 9, every sentence checked against its recording
8aac0d49 test: re-anchor the view-model, taxonomy and evidence-mechanism exhibits by measurement
f21b2c6e docs: make four stale passages true of baseline 9
f549f9e7 test: re-pin the corpus-only training values; the fenced fits stay red
948abae1 test: re-pin the api, scripts and orchestrator suites on baseline 9
d1b21e60 test: re-pin the eval, meeting and agent suites on baseline 9
1bf839da tour: re-point the featured strip by the measured criterion on the new bytes
07605e67 docs: re-derive the front door on baseline 9
5d3b7a60 check_doc_facts: read the gzipped reports, follow the new record, compare prompt stamps per row
a4bbee7f test: close the v5 prompt window — every committed recording stamps v6 and v8
3eba9495 style: format the suspicion-row pin the parser commit left unformatted
b3b007bf eval: the baseline-9 supply floors, measured on the new bytes, become the default
946ab7ba docs: publish the process scorecard's after column on baseline 9
83148aa6 derive: the rubric and the corrected W2 baseline, rebuilt on the new bytes
134b10de build: deliver the four eval reports gzipped, proving no measured value moves
ac2023ab record: leg 4 of 4 — replays/ml_corpus/4p1i, 50 of 50, FROZEN and gated
9bae2b03 record: leg 3 of 4 — replays/samples/4p1i, 50 of 50, gated
7fd7040f record: leg 2 of 4 — replays/ml_corpus/9p2i, 150 of 150, FROZEN and gated
820704be docs: write leg 1 into the record while leg 2 records
ee9c8dcf fix: let the gameplay extractor read a suspicion row without a trust column
c1990957 record: leg 1 of 4 — replays/samples/9p2i, 50 of 50, gated
50fe1526 docs: record the absolute flag census before the old bytes are gone
1395b19d docs: record the owner's input-ceiling raise, and re-derive the projection
27646d67 docs: commit the re-record's before column before the first seed stages
```

And the same log restricted to the frozen directories —
`git log --oneline 39a568c6..HEAD -- engine agents meetings observation orchestrator`,
which covers the prompt set under `agents/strategic/prompts/` — prints
**nothing**. The card re-runs that command at the pull request's head.

**The key scan, count-only, over every new byte.** Every file this branch adds or
changes (`git diff --name-only --diff-filter=AM 39a568c6..HEAD`, the gzipped
reports decompressed), matched against five key shapes — a Featherless `rc_`
key, an `sk-` key, a bearer token, a `FEATHERLESS_API_KEY=` assignment of a
real-looking value (eight or more key characters), an `api_key` assignment —
printing counts only:

```
$ uv run python <out-of-tree>/keyscan.py 39a568c6
files scanned: 418; bytes scanned (gz decompressed): 304,924,306
TOTAL matches: 0
```

Each pattern fires on a planted key (one match each), so the zero is a
measurement and not a pattern that cannot match. A looser first version of the
assignment pattern matched twice, in `replays/ml_corpus/README.md`: both are the
documented `export FEATHERLESS_API_KEY=...` placeholder, whose value is the
literal three dots, and both were already on `main` at the base. Run during the
close;
the card re-runs it at the pull request's head. The key file the recording used
was deleted from the operator's scratch directory, and no step of the close
read the repository's `.env`.
