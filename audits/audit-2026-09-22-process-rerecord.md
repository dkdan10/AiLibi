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
| model calls | 7,271 | 9,500 | (§2) |
| input tokens | 31,756,112 | 43,000,000 | (§2) |
| output tokens | 1,598,475 | 2,200,000 | (§2) |
| recording wall | about 12h05m | 16 h | (§2) |
| elapsed window | about 15h48m | 24 h | (§2) |
| marginal cost | `$0.0000` | `$0.00` | (§2) |

The cost is `$0.00` **marginal** against the flat-rate Featherless
subscription, whose standing fee is already paid and is not incurred by this
run.

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

## 2. The legs, as recorded

*(written as each leg completes)*

## 3. The gates, per leg

*(written as each leg completes)*

## 4. The AFTER column

*(written once the four legs are in)*

## 5. The re-record log

*(every `(deadline_default)` row, with its cause, as it happened)*

## 6. The tour, and the ladder

*(written after the legs)*

## 7. What this record does not discharge

*(written at the close)*

## 8. The freeze, shown rather than asserted

*(the window's `git log`, written at the close)*
