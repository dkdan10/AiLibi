# Fresh-model deduction evaluation — run of 2026-09-16 (fifth attempt, complete)

**The run completed all one hundred units in one sitting, and the candidate
does NOT advance. On the fifty paired units `repaired_clock` scored the primary
outcome 0 times and `combined_accounts` 2, so `b = 2`, `c = 0`, the two-sided
exact McNemar p is 0.5 and the net paired difference is 2 against a bar of 10.
The third clause fails hardest and is the one to read: the candidate ejected 12
players to the reference's 1, and 8 of those 12 were crewmates, so its net
increase in wrongful ejections is +7 against a net paired gain of 2 — the
failure `WRONGFUL_EJECTION_TRADEOFF` was written to catch. The result is
INCONCLUSIVE under the frozen decision rule's own wording, and the manifest
declared before the run that the v4 revision would raise this arm's ejection
rate one-sidedly, so the bound has to be read against that declaration rather
than as a clean property of the candidate.**

No stop condition fired. There was one sitting and no resumption. Marginal cost
$0.00.

This is the first complete run of this evaluation: the four attempts before it
stopped at 1, 0, 3 and 25 units of 100. This directory is the whole of its
evidence, and nothing in it is an adoption.

**On this directory's date.** The sitting ran from `2026-09-16T08:33:05Z` to
`2026-09-16T10:27:58Z`, and the directory is named for the UTC date its own
records carry.

## The design

One meeting per frozen held-out prefix under two paired arms — the reference
`repaired_clock` (`format_version=2`, `evidence_reasoning_version=2`) and the
candidate `combined_accounts` (the reference plus `public_account_version=1`
and `attributed_testimony_version=1`) — over the 50 proof-free scripted
prefixes of the **fifth** held-out band, 8000–8999, frozen by the owner's merge
of PR #463 (accepted seeds 8000–8057, 8 `witnessed_kill` skips, freeze record
sha256 `46f2ba616dc4088f4ac3006191c559de9b98d75a0f1044e14220371881fb4c1e`).
Sequential, both arms per seed before the next seed, on Featherless
`Qwen/Qwen3.6-27B` (non-thinking, `json_object`) with the `qwen3_6_27b` prompt
set at **accounts revision v4**, under the limits the fifth authorization
re-sized from the second live development calibration: per-call caps turn 4,096
output / vote 1,024, temperatures 0.4 / 0.2, per-unit 116,000 input / 16,000
output, run-level 3,844,000 / 422,000, 6 h of model work within an 8 h elapsed
deadline, transport bound 4 attempts at 180 s each. 50 prefixes × 2 arms = 100
units, scored on `supported_correct_ejection` with the two-sided exact McNemar
test over the discordant pairs. **All 100 units ran: decision coverage is
100%.**

The run was made from commit `a495fec5` on branch `work/fresh-deduction-run-5`,
with `experiments/fresh_deduction_instrument.py` at sha256
`0c5d064fac0b4b9b0bd70220ebc24562c596a87faaf62958d538797181d6ccbc` and the
execution manifest at
`d116761f97f4722b4d4ed194026ab4d0930b3431db9185f5e41332a09c7ffddb`, both
recorded in [checkpoint-final.json](checkpoint-final.json) and the first of
them in [report.json](report.json):

```sh
.venv/bin/python -c "import hashlib, pathlib; \
print(hashlib.sha256(pathlib.Path('experiments/fresh_deduction_instrument.py').read_bytes()).hexdigest())"
```

The invocation was exactly the one
[the manifest documents](../execution-manifest.md) in its "The live gate"
section — the same module, provider, manifest path and runner flag, with
`--output-dir`, `--json` and `--checkpoint` pointing outside the repository —
run once, with the API key delivered through `uv run --env-file` from a
credential-only 0600 file outside the repository that was deleted afterwards.
It is not reproduced verbatim here, and it is elided in [run.log](run.log) as
well: no committed file outside the manifest and the instrument may carry the
runner flag, and
`tests/experiments/test_fresh_deduction_instrument.py::TestLiveGate::test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag`
scans every tracked file to keep that true.

Every figure below is reproducible from the files in this directory. The
reconciliation most of them are read off is itself a derivation rather than a
table somebody typed:

```sh
.venv/bin/python audits/deduction-candidate/run-2026-09-16/reconcile.py \
  audits/deduction-candidate/run-2026-09-16
```

which reprints [usage-reconciliation.json](usage-reconciliation.json) byte for
byte from the replays and the checkpoint beside it, the two pre-declared
diagnostics included.

## Primary outcome, discordant pairs and the decision rule

The three graders are a pure function over a finished `UnitRecord`, run after
each unit returned; no grader is called from the path that drives the model and
no stop condition anywhere reads an outcome, so the grades below are a readout
of a fixed 50-pair sample rather than an interim analysis that could have
changed what the run did next.

| Quantity | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| Units | 50 | 50 |
| Ejections | **1** | **12** |
| Role-correct ejections | 0 | 4 |
| Wrongful ejections (a crewmate) | **1** | **8** |
| `supported_correct_ejection` (the primary outcome) | **0** | **2** |
| Ballots naming the ejected player | 2 | 24 |
| Off-target citations among those | 0 | 7 |
| Terminal / partial units | 1 / 49 | 12 / 38 |

| Quantity | Value |
| --- | --- |
| Paired units | **50 of 50** |
| Discordant pairs `b` (candidate 1, reference 0) | **2** — seeds 8008 and 8025 |
| Discordant pairs `c` (reference 1, candidate 0) | **0** |
| Net `b - c` | **2** |
| Two-sided exact McNemar p | **0.5** |

```sh
.venv/bin/python -c "
import json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from paired_stats import exact_mcnemar_p
cp = json.loads(Path('audits/deduction-candidate/run-2026-09-16/checkpoint-final.json').read_text())
by = {}
for u in cp['units']:
    by.setdefault(u['seed'], {})[u['arm']] = u['supported_correct_ejection']
b = sorted(s for s, v in by.items() if v['combined_accounts'] and not v['repaired_clock'])
c = sorted(s for s, v in by.items() if v['repaired_clock'] and not v['combined_accounts'])
print('paired', len(by), '| b', len(b), b, '| c', len(c), c, '| p', exact_mcnemar_p(len(b), len(c)))
"
```

```
paired 50 | b 2 [8008, 8025] | c 0 [] | p 0.5
```

The three clauses of `DECISION_RULE`, each evaluated:

| Clause | Bar | Measured | Holds? |
| --- | --- | --- | --- |
| Two-sided exact McNemar p over the discordant pairs | below 0.05 | **0.5** | **no** |
| Net paired difference `b - c` | at least 10 of 50 | **2** | **no** |
| Candidate's net increase in wrongful crew ejections | no larger than `b - c` | **+7 against 2** | **no** |

**Conjunction: false. `combined_accounts` does not advance to an explicitly
scoped adopting review.** The instrument computes the same conjunction beside
the test rather than leaving it to a reader — `report.json`'s `paired` block
carries `meets_wrongful_ejection_tradeoff: false` and `meets_decision_rule:
false`:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
print(json.dumps(json.loads(Path('audits/deduction-candidate/run-2026-09-16/report.json').read_text())['paired'], indent=2))"
```

### The wrongful-ejection bound, read against the v4 revision's declared effect

`WRONGFUL_EJECTION_TRADEOFF` counts a unit whose meeting ejected a player whose
hidden role is CREWMATE and requires the candidate's net increase in those to
be no larger than its net paired gain: "one extra wrongful ejection has to be
paid for by at least one extra supported-correct ejection", because "the
failure it guards against is a candidate that merely raises the ejection RATE".

On this run the candidate arm ejected in 12 of 50 units against the reference's
1, and 8 of those 12 landed on a crewmate: **+7 wrongful against +2
supported-correct**. Read literally, that is exactly the failure mode the bound
names.

It must also be read against what the manifest declared BEFORE the run, in its
"Accounts prompt set v4 (2026-09-15)" section, under the heading **ONE-SIDED
EFFECT**: on the fourth run 13 of 14 candidate EJECT citations were nulled for
carrying the `obs ` tag word and 12 ballots were coerced to SKIP, so supplying
the bare citation form "converts coerced SKIPs into live ejections ON THE
TREATMENT ARM ONLY: the fix raises the candidate's ejection RATE, which is
precisely the failure `WRONGFUL_EJECTION_TRADEOFF` polices, and the next run
reads the wrongful-ejection bound against this entry rather than reading a
higher ejection count as a finding."

That is what happened, and the archive shows both halves of it:

* The citation channel is repaired. The candidate cast **73 supported ballots
  of 150** against the reference's 14, and **24 ballots named the ejected
  player** against the reference's 2.
* The coercion has not disappeared. **44 of the candidate's 46 guard-rewritten
  ballots are `uncited_coerced`** (the reference recorded 1 rewrite, an
  `under_gate_redirect`), so the arm still produces uncited EJECTs that the
  meeting layer turns into SKIPs — fewer than the fourth run's 12 of 17, but
  not none.

So the bound's failure is a joint statement about the candidate and about the
revision that made it measurable: the arm now ejects, and most of its ejections
are wrong. What this run cannot do is separate "the candidate deduces worse"
from "the v4 citation fix converted the arm's suppressed ejections into live
ones, and the underlying judgment was always this accurate". Both readings
predict these counts. The bound is stated as the rule states it — the candidate
does not clear it — and the attribution is left where the manifest put it.

### The second declared one-sided effect: citation relevance, downward

The manifest's second declaration is that the v4 turn bound shortens exactly
the two fields `grade_citation_relevance` walks (`free_text` and each claim's
`reason`), so "shorter prose names fewer players, so a ballot citing a bounded
turn is likelier to be graded OFF_TARGET for the ejected player and its unit
likelier to score 0", on the candidate arm alone.

The run records **7 off-target citations among the candidate's 24 naming
ballots, and 0 among the reference's 2**. Relevance rather than presence is
what two of the candidate's four role-correct ejections turned on:

| Seed | Ejected | Role | role_correct | supported_correct | naming | off-target | Why it did not score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8006 | p-4 | IMPOSTOR | yes | **no** | 2 | 1 | both naming ballots carried a citation the support pass found present; one of them does not bear on p-4 |
| 8008 | p-4 | IMPOSTOR | yes | **yes** | 2 | 0 | — |
| 8025 | p-1 | IMPOSTOR | yes | **yes** | 2 | 0 | — |
| 8056 | p-4 | IMPOSTOR | yes | **no** | 2 | 0 | both naming ballots were `uncited` (one an `under_gate_redirect` rewrite), so neither could be supported |

```sh
.venv/bin/python -c "
import json
from pathlib import Path
cp = json.loads(Path('audits/deduction-candidate/run-2026-09-16/checkpoint-final.json').read_text())
for u in sorted(cp['units'], key=lambda x: x['seed']):
    if u['ejected_player_id'] is None: continue
    print(u['arm'], u['seed'], u['ejected_player_id'], u['ejected_role'],
          '| role_correct', u['role_correct'], '| supported_correct', u['supported_correct_ejection'],
          '| naming', u['naming_ballots'], '| off_target', u['off_target_citations'])
"
```

Two of the candidate's four role-correct ejections were lost to the primary
outcome's other two conjuncts — one to relevance, one to support — and the two
that survived are the run's whole `b`. The two declared effects push in
opposite directions on the same arm, and this run does not separate them
either.

**Ballots, for the record.** Verdicts are per ballot; the guard column is an
OVERLAY on them rather than a fourth bucket.

| Arm | Ballots | supported | unsupported | uncited | guard-rewritten (overlay) | naming (non-SKIP) |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 150 | 14 | 0 | 136 | 1 (`under_gate_redirect`) | 14 |
| `combined_accounts` | 150 | 73 | 0 | 77 | 46 (44 `uncited_coerced`, 2 `under_gate_redirect`) | 75 |

```sh
.venv/bin/python -c "
import json
from collections import Counter
from pathlib import Path
cp = json.loads(Path('audits/deduction-candidate/run-2026-09-16/checkpoint-final.json').read_text())
v, g, naming = Counter(), Counter(), Counter()
for u in cp['units']:
    for b in u['supported']:
        v[(u['arm'], b['verdict'])] += 1
        if b['guard_rewrite_reason']: g[(u['arm'], b['guard_rewrite_reason'])] += 1
        if b['target'] != 'SKIP': naming[u['arm']] += 1
print(dict(v)); print(dict(g)); print(dict(naming))"
```

## The two pre-declared diagnostics

Neither is a gate. No stop condition reads either, the decision rule names
neither, and neither changes a primary outcome. They are reported beside the
result because the owner's decision 9 of 2026-09-15 said they would be.

### The public-transcript role leak

`ROLE_LEAK_RULE`: a leaking turn is a COMMITTED public turn whose speaker is an
IMPOSTOR and whose text states, in the first person and without attributing the
statement to someone else, either that role or a kill that speaker committed.

| Arm | Leaking turns | Units with a leaking turn | Units |
| --- | --- | --- | --- |
| `combined_accounts` | **1** | **1** (seed 8042) | 50 |
| `repaired_clock` | **1** | **1** (seed 8014) | 50 |

**The count is an ESTIMATE carrying error in BOTH directions and is not a
floor.** The rule says so in its own words: it reads no intent, so a confession
whose shapes it does not match is missed, and its guards see one sentence at a
time, so an attribution spread across two is counted. One leaking turn per arm
is a numerator of one on a two-sided rule, so it bounds the leak loosely rather
than measuring it.

Read against what came before: the fourth run counted 2 of 13 candidate games
and 0 of 39 reference turns, and the second calibration 1 of 60 candidate units
and 0 of 60 reference. This run is the first measurement in which the REFERENCE
arm leaks at all, which is worth stating rather than smoothing: at one event
per fifty units on each arm the diagnostic no longer separates the arms, and
the fourth run's 2-of-13 candidate-only reading is not reproduced here.

### The role-split ballot profile

Per arm, per call type, split by the AUTHOR's hidden role — which the
derivation reads off each replay's own tick rows, the actor of the scripted
kill being that seed's impostor. `p95` is the nearest-rank percentile
`PERCENTILE_RULE` states. A truncation is `output_tokens >= max_tokens`; the
provider's own `finish_reason` is the other signal and is discussed below.

| Arm | Call | Role | draws | out mean | out p95 | out max | cap | truncations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | turn | CREWMATE | 100 | 333.2 | 442 | 466 | 4,096 | 0 |
| `repaired_clock` | turn | IMPOSTOR | 50 | 216.7 | 443 | 523 | 4,096 | 0 |
| `repaired_clock` | ballot | CREWMATE | 100 | 103.0 | 124 | 129 | 1,024 | 0 |
| `repaired_clock` | ballot | IMPOSTOR | 50 | 99.5 | 119 | 130 | 1,024 | 0 |
| `combined_accounts` | turn | CREWMATE | 100 | 495.6 | 838 | **1,075** | 4,096 | 0 |
| `combined_accounts` | turn | IMPOSTOR | 50 | 425.6 | 857 | 894 | 4,096 | 0 |
| `combined_accounts` | ballot | CREWMATE | 100 | 97.8 | 127 | **132** | 1,024 | 0 |
| `combined_accounts` | ballot | IMPOSTOR | 50 | 87.6 | 112 | 129 | 1,024 | 0 |

**The impostor ballot the fourth run stopped on is gone.** That run's candidate
impostor `rationale_text` averaged 477 characters and reached 1,795, and its
38th ballot drew the 1,024-token cap. Here the candidate's largest
impostor-authored ballot is 129 output tokens — 12.6% of the cap — and its
largest ballot of either role is 132. The v4 bound holds on held-out inputs
what the second calibration measured on development ones.

**The impostor self-tell has not gone away**, which is the same finding the
calibration reported. Impostor-authored ballots whose rationale OPENS by naming
that role or a kill (`opens_with_a_self_tell`):

| Arm | Self-telling ballots | Impostor ballot draws | Share |
| --- | --- | --- | --- |
| `combined_accounts` | **29** | 50 | 58.0% |
| `repaired_clock` | **3** | 50 | 6.0% |

The behaviour and the stop had one root and only one of them is closed: the
model still writes the concealment plan from the private truth forward in about
three impostor ballots in five on the candidate arm, but it now does so in
about a hundred characters instead of five hundred.

Both diagnostics recompute from the archive:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
rec = json.loads(Path('audits/deduction-candidate/run-2026-09-16/usage-reconciliation.json').read_text())
for arm, block in rec['role_split_profile'].items():
    for kind, roles in block.items():
        for role, prof in roles.items():
            print(arm, kind, role, prof)
for arm, a in rec['arms'].items():
    print(arm, '| leaking turns', a['leaking_turns'], '| units with one', a['units_with_a_leaking_turn'],
          '| self-telling impostor ballots', a['self_telling_impostor_ballots'])"
```

## Meeting-internal defaults, charged failed attempts and transport attempts, per arm

| Arm | Units | Defaulted turns | Defaulted votes | By validation | By deadline | Degraded openings | Units with defaults | Charged failed attempts | Retried calls | Unaccounted attempts | Units with retries | Cap-signal disagreements |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `combined_accounts` | 50 | **1** | 0 | **1** | 0 | 0 | **1** | **1** (3,460 in / 245 out) | 0 | 0 | 0 | 0 |

**The one default and the one charged failed attempt are the same call**, on
`combined_accounts` seed 8010: the provider billed a completion and refused it
on its own schema validation (`ValidationError`, 3,460 input / 245 output), and
the meeting layer's shipped fail-soft substituted a placeholder turn, recording
a zero-token `deadline_default` row beside it. The instrument classified its
phase and trigger without complaint, so the "a default this instrument cannot
classify is a stop" condition did not fire. At 1 substitution in 601 attempts
the observed rate is well inside the ~1-in-50 the manifest accepts, and it is
the reference arm, not the candidate, that recorded none.

Two consequences the manifest requires a reader to carry, restated: a defaulted
ballot is a SKIP the voter did not choose, and because the privileged grader's
"every naming ballot supported" is an `all()`, a defaulted ballot removes a
constraint rather than failing it and biases the primary outcome upward.
Neither applies with force here — the one default was a TURN, not a ballot, and
`units_with_defaults` is 1 of the candidate's 50 units, which is the bound on
how many of its decisions rest on a partly unauthored meeting.

**No transport retry fired.** The provider answered every one of the 601
attempts with a completion or a billed refusal; no row carries the
`no-completion-returned` marker, and `retried_calls`, `unaccounted_attempts`
and `attempts_by_trigger` are empty on both arms. The bound (4 attempts, 180 s
each) was in force and never engaged.

```sh
grep -c "no-completion-returned" audits/deduction-candidate/run-2026-09-16/*.jsonl | grep -v ":0$" || echo "no file carries the marker"
```

**One unit recorded a seventh call, and it is neither a retry nor a default.**
`combined_accounts` seed 8026 carries seven resolved calls for its six meeting
slots: the meeting layer asked p-4's opening twice — a byte-identical re-ask on
its shipped single-retry path (`meetings/manager.py`, `retries=1`) — and
committed the second, whose payload carried one claim where the first carried
four. No `failed_call` row, `degraded_openings` 0, `retried_calls` 0: both
calls are charged and both are in the accounting below. Together with seed
8010's five resolved calls plus its one billed refusal, that is why the
candidate arm's attempt count is 301 rather than 300.

## Usage against every authorized limit

| Arm | Attempts | Completions | Charged-and-refused | Input tokens | Output tokens | `cost_usd` | Model work |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 300 | 300 | 0 | 1,059,714 | 59,427 | 0.0 | 2,988.2 s |
| `combined_accounts` | 301 | 300 | 1 | 1,184,209 | 85,250 | 0.0 | 3,897.6 s |
| **Run total** | **601** | **600** | **1** | **2,243,923** | **144,677** | **0.0** | **6,885.9 s** |

| Limit | Authorized | Actual | Used | Fired? |
| --- | --- | --- | --- | --- |
| Run input tokens | 3,844,000 | 2,243,923 | 58.4% | no |
| Run output tokens | 422,000 | 144,677 | 34.3% | no |
| Per-unit input tokens | 116,000 | 34,683 (largest unit, candidate) | 29.9% | no |
| Per-unit output tokens | 16,000 | 2,898 (largest unit, candidate) | 18.1% | no |
| Elapsed wall | 8 h (28,800 s) | 6,891.9 s | 23.93% | no |
| Model work | 6 h (21,600 s) | 6,885.9 s | 31.88% | no |
| Per-call output cap, turn | 4,096 | largest turn 1,075 (candidate) | 26.2% | no |
| Per-call output cap, vote | 1,024 | largest ballot 132 (candidate) | 12.9% | no |
| Transport attempts | 4 per call, 180 s each | 1 attempt per call, 601 of 601 | 25% of the bound | no |
| Dollar | $0.00 marginal | $0.00 | — | not an enforcement mechanism on this provider |

**Marginal cost: $0.00.** Every recorded `cost_usd` is exactly 0.0, by
construction rather than by measurement: the Featherless provider's zero
pre-flight rate disables `BudgetedLLMClient`'s USD dimension, so the token
budget and the wall deadline are the only limits that could have stopped this
run — and neither came close. The resources consumed were subscription capacity
and 6,891.9 seconds of wall on one worker.

**Pace.** 6,885.9 s of model work over 601 attempts is **11.46 s per attempt** —
9.96 s on the reference arm and 12.95 s on the candidate. The whole 600-call
design took 1.91 h of the authorized 6 h.

Per-unit and per-call profiles, for the record:

| Arm | Call | n | in mean | in p95 | in max | out mean | out p95 | out max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | turn | 150 | 3,334.2 | 4,159 | 4,374 | 294.4 | 443 | 523 |
| `repaired_clock` | ballot | 150 | 3,730.6 | 4,415 | 4,887 | 101.8 | 124 | 130 |
| `combined_accounts` | turn | 150 | 3,392.3 | 4,755 | 5,791 | 472.3 | 857 | 1,075 |
| `combined_accounts` | ballot | 150 | 4,479.3 | 5,993 | 7,301 | 94.4 | 126 | 132 |

Per unit: `repaired_clock` 21,194 input / 1,189 output mean, largest unit
24,282 / 1,581; `combined_accounts` 23,615 / 1,700 mean, largest unit 34,683 /
2,898. (The reference arm's largest unit being 24,282 exactly is a coincidence:
the same number is `CALIBRATION_SIZING_UNIT_INPUT_TOKENS`, which is the three
stopped runs' archive maximum and has nothing to do with this sitting.)

### Side by side with the calibration that sized these limits

| Figure | Calibration 2 (2026-09-15, development inputs, v4) | This run (held-out band 8000-8999, v4) |
| --- | --- | --- |
| Units / attempts | 120 / 720 | 100 / 601 |
| `repaired_clock` per unit | 20,862 in / 1,142 out | 21,194 in / 1,189 out |
| `combined_accounts` per unit | 22,734 in / 1,609 out | 23,615 in / 1,700 out |
| Largest unit | 38,440 in / 4,176 out | 34,683 in / 2,898 out |
| Largest candidate turn | 1,884 (46.0% of the 4,096 cap) | 1,075 (26.2%) |
| Largest candidate ballot | 135 (13.2% of the 1,024 cap) | 132 (12.9%) |
| Impostor candidate ballot truncations | 0 of 60 | **0 of 50** |
| Candidate impostor self-tells | 39 of 60 (65.0%) | 29 of 50 (58.0%) |
| Candidate units with a leaking turn | 1 of 60 | 1 of 50 |
| Reference units with a leaking turn | 0 of 60 | 1 of 50 |
| Pace per attempt | 10.28 s pooled | 11.46 s pooled |
| Refusals / defaults / retries | 0 / 0 / 0 | 1 / 1 / 0 |

The calibration's per-unit means held to within 6% on both arms and its maxima
came in ABOVE what the held-out run charged on every dimension, so the ceilings
it sized were, if anything, conservative. The dimension the fourth run's stop
turned on — the candidate impostor ballot's tail — is where the two agree most
closely and where both are now an order of magnitude below the cap.

### `finish_reason` and the cap signal

| Arm | Rows | Cap-signal disagreements | Inferred truncations (`output_tokens >= cap`) | Observed truncations (`finish_reason == "length"`) |
| --- | --- | --- | --- | --- |
| `repaired_clock` | 300 | **0** | **0** | **0** |
| `combined_accounts` | 301 | **0** | **0** | **0** |

Since 2026-09-15 the cap check reads the provider's own `finish_reason` beside
the `output_tokens >= max_tokens` inference and EITHER of them stops the run, and
a row on which the two disagree stops the run and is counted as
`cap_signal_disagreements`. This run completed all 601 attempts with both
counters at zero, which says three things at once: no call reported
`finish_reason == "length"`, no call reached its cap by the inference, and no
call reported some other word while at its cap.

**What this run does NOT record, stated rather than glossed:** the per-call
`finish_reason` DISTRIBUTION. Per-call `finish_reason` rows are a
calibration-mode output (`CalibrationReport.calls`); the evaluation's own
`InstrumentReport` carries the disagreement count and no per-call reading, and
the replays' `llm_calls` rows carry no such field. Producing one would have
meant changing the instrument, which
[this run's card](../../../tasks/work/fresh-deduction-authorization-5.md)'s
Expected scope forbids in the run's own pull request. The strongest statement
the archive supports is the one above; for reference, the second calibration
recorded `{"stop": 360}` on each arm through the same client, unchanged since.

## Every stop condition, checked

`STOP_RULE`'s enumerated conditions, each against what the run recorded:

| Stop condition | Fired? | Evidence |
| --- | --- | --- |
| Token budget exhausted, per-unit level | no | 29.9% / 18.1% of the per-unit ceilings at the largest unit |
| Token budget exhausted, run level | no | 58.4% / 34.3% of the run ceilings |
| Elapsed wall deadline | no | 6,891.9 s of 28,800 s |
| Model-work window | no | 6,885.9 s of 21,600 s; no attempt was cut off in flight |
| A response that reached its output cap (truncation) | no | largest ballot 132 of 1,024, largest turn 1,075 of 4,096; 0 by either signal, 0 disagreements |
| A held-out digest or skip differing from the frozen manifest | no | `verify_frozen_set` passed before any client existed — 50 accepted, 8 skips, record sha256 `46f2ba61…fb4c1e` — and all 50 rebuilt to their frozen digests again afterwards ([rendered-prefixes.json](rendered-prefixes.json)) |
| A rendered prompt or regenerated prefix matching `body-p-\d+-\d+` | no | asserted over all 50 regenerated prefixes before the run and over every rendered prompt after each unit; the archive's prompts carry only `body-p-1`…`body-p-4` |
| A unit whose recorded observation clock or experiment config is not the arm's | no | every replay records `temporal_observation_version` 2, and `usage-reconciliation.json`'s per-arm `experiment_configs` holds exactly one config per arm — the candidate versions on `combined_accounts`, both null on `repaired_clock` |
| A recorded meeting default the instrument cannot classify | no | the one default classified as a `validation` turn |
| A call that came back with no completion at all (transport) | no | 601 attempts, 600 completions and one billed-and-refused completion; no `no-completion-returned` marker anywhere |
| The recorded-spend reconciliation (`SPEND_RECONCILIATION`) | no | ran after each of the 100 units and passed; a failure is a stop and the run completed |
| The post-unit budget cap read-back (`BUDGET_CAP_READBACK`) | no | ran after each of the 100 units and passed, for the same reason |

No stop condition reads an outcome, and none did here.

**On the body-handle check.** Scanning the whole archive for `body-p-\d+-\d+`
returns one hundred matches and none of them is on a surface the stop condition
covers: each is the engine's own entity id inside a tick row's `actions` field,
the raw record of the scripted report step. What the condition covers is the
regenerated prefixes, the rendered prompts and the emitted report, and all of
those are clean:

```sh
.venv/bin/python -c "
import json, re
from collections import Counter
from pathlib import Path
legacy, in_prompts = Counter(), Counter()
for p in sorted(Path('audits/deduction-candidate/run-2026-09-16').glob('*.jsonl')):
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    m = next(r for r in rows if r['kind'].startswith('meeting'))
    for r in rows:
        for h in re.findall(r'body-p-\d+-\d+', json.dumps(r)): legacy[r['kind']] += 1
    for c in m['llm_calls']:
        for h in re.findall(r'body-p-\d+(?:-\d+)?', c['prompt'] or ''): in_prompts[h] += 1
print('legacy handles by row kind:', dict(legacy))
print('handles in rendered prompts:', dict(sorted(in_prompts.items())))"
```

```
legacy handles by row kind: {'tick': 100}
handles in rendered prompts: {'body-p-1': 25, 'body-p-2': 28, 'body-p-3': 16, 'body-p-4': 32}
```

**On the source-identity check.** The two arms render different template
families by design and each carried exactly one marker set throughout, so no
source changed mid-run: `repaired_clock` recorded
`accusation_round.qwen3_6_27b.v5` / `crewmate_report.qwen3_6_27b.v5` /
`impostor_report.qwen3_6_27b.v5` / `vote_ballot.qwen3_6_27b.v5`, and
`combined_accounts` the
`…_accounts.qwen3_6_27b.v4.accounts1.attributed1` family — **revision v4**, the
bodies PR #460 landed. Both are in `report.json`'s per-arm `prompt_versions`
and in the reconciliation's `prompt_version_markers`, and every recorded call
names the model `Qwen/Qwen3.6-27B`.

## Resumptions

**None, and none was needed.** The manifest's resumption clause of 2026-09-14
authorizes one resume per environmental stop; no stop occurred. The run had
exactly one sitting — `2026-09-16T08:33:05Z` to `2026-09-16T10:27:58Z`, exit 0
— and no `--resume` invocation was made. The checkpoint was written at every
pair boundary and its final state carries all 100 units, 50 completed paired
seeds and an empty `abandoned` block, which is what a run that abandoned no
pair records:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
cp = json.loads(Path('audits/deduction-candidate/run-2026-09-16/checkpoint-final.json').read_text())
print('units', len(cp['units']), '| paired seeds', len(cp['completed_seeds']),
      '| abandoned', cp['abandoned'])"
```

## What this archive contains

| File | What it is |
| --- | --- |
| [report.json](report.json) | the instrument's own report: per-arm counts, the paired result and the conjunction, the limits and sampling it ran under, the frozen rubrics and the stop rule |
| [run.log](run.log) | the sitting's log: the stamps, the exit code, the invocation with its credential, output paths and runner flag elided, and the stdout body (byte-identical to `report.json`) |
| `repaired_clock-seed-*.jsonl`, `combined_accounts-seed-*.jsonl` (100 files) | the per-unit replays: ticks, the meeting with its transcript, ballots, verdict and every recorded call with its rendered prompt |
| [checkpoint-final.json](checkpoint-final.json) | the checkpoint as the run left it: all 100 graded units with their ballot verdicts, the identity digests the run was held to, and the budgets it spent |
| [usage-reconciliation.json](usage-reconciliation.json) | per-unit and per-arm usage, verdicts, defaults, charged failed attempts, transport attempts, provenance, body handles, and the two pre-declared diagnostics, derived from the two above |
| [reconcile.py](reconcile.py) | the derivation that writes the file above, so its numbers can be recomputed rather than trusted |
| [rendered-prefixes.json](rendered-prefixes.json) | the fifty prefixes this run rendered, regenerated after the run and checked against their frozen digests |
| [render_rendered_prefixes.py](render_rendered_prefixes.py) | the derivation that writes the file above, reading the rendered seeds off the replays rather than off the freeze record |

Nothing was left out: the whole archive is about 10 MB, inside the size at
which [the run's card](../../../tasks/work/fresh-deduction-authorization-5.md)
would have made the runner choose what to keep. The archive was scanned for the
API key before it was committed — a count-only comparison against the whole key
and against its first six characters, over every file in this directory — and
carries neither: both counts are 0. `assert_report_holds_no_prefix_bytes` was
re-run over the committed report against all fifty rebuilt prefixes and passed.

## Held-out status

**All fifty accepted seeds of the fifth band are revealed by this archive:
8000–8057 in accepted order, the whole set.** This run rendered every one of
them, which is what a complete run means.

The instrument serialized no prefix during the run — it never does, and
`assert_report_holds_no_prefix_bytes` refuses a report that carries one. What
this directory publishes is the hundred replays, whose meeting rows carry the
prompts those prefixes rendered under each arm and whose tick rows carry the
scripted steps, plus `rendered-prefixes.json`, which is the fifty rendered
prefixes regenerated and written out AFTER the run. The runner opened, printed
and reasoned about no prefix before the run.

Three consequences the owner's next decision has to carry:

1. **This run does not itself convert the band's status.** The freeze record
   still reads `held_out`, and flipping it belongs to the decision that acts on
   this record, not to the runner — as the manifest's Roles section has it,
   "a held-out result that informs a fix marks this set development" and a new
   band is frozen under a new card.
2. **A re-run on this same band would not be a held-out sample at all**, since
   every one of its fifty seeds is now public. Any future confirmation claim
   needs a new band frozen under a new card by a preparer who has not read this
   document — and, unlike the four stopped runs, there is no unrendered
   remainder of this band to salvage.
3. **Sixty-seven seeds of held-out margin are now gone across five runs** —
   seed 3000 of the first band, 5000 of the second, 6000 and 6001 of the third,
   thirteen of the fourth and all fifty of the fifth. What the fifth bought for
   them is the first complete measurement this evaluation has produced.

## The verdict

In the preregistration's own vocabulary, whose four possible decisions are
"advance for an explicitly scoped adopting review, revise and evaluate a new
version, reject, or gather more evidence under a new authorized manifest":

**`combined_accounts` does not advance to an explicitly scoped adopting review.
The result is INCONCLUSIVE, and under `DECISION_RULE`'s own wording
"inconclusive is not success".** All three clauses fail: p is 0.5 against a bar
of 0.05, the net paired difference is 2 against a bar of 10, and the net
increase in wrongful ejections is +7 against a permitted 2. Unlike the fourth
run's, this conjunction IS evaluable — it was computed on the fifty paired
units the rule is stated on, with no stopping and no interim analysis.

Nor is the candidate REJECTED by this run, and the reason is the first declared
one-sided effect. The arm's ejection rate moved because the instrument's
citation channel was repaired between the fourth run and this one, so the 12
ejections and the 8 wrongful ones are a joint product of the candidate and of a
prompt fix that was made to let the arm be measured at all. A rejection would
have to attribute them to the candidate alone, and this design cannot. The
decision that follows — revise and evaluate a new version, gather more evidence
under a new authorized manifest, or reject — is the owner's, on a card, and the
preregistration is explicit that more evidence "is not an automatic spending
authorization".

**A result is a measurement and never an adoption.** That is true of a
conclusive result and it is true of this one. Nothing in this directory adopts
anything, flips any flag or makes any experiment ON; both candidate levers stay
default-OFF exactly as they were.

## Compared with the four earlier attempts and the two calibrations

| | 2026-09-10 (#445, closed) | 2026-09-13 (#448, closed) | 2026-09-13 (#451, closed) | 2026-09-15 (#458, unmerged) | 2026-09-16 (this run) |
| --- | --- | --- | --- | --- | --- |
| Band | 3000-3999 | 5000-5999 | 6000-6999 | 7000-7999 | **8000-8999** |
| Accounts revision | not stated in its archive | not stated in its archive | v2 | v3 | **v4** |
| Units completed | 1 of 100 | 0 of 100 | 3 of 100 | 25 of 100 | **100 of 100** |
| Paired seeds graded | 0 | 0 | 1 | 12 | **50** |
| Attempts | 12 | 5 | 22 | 156 | **601** |
| Input / output tokens | 36,003 / 3,401 | 13,182 / 993 | 82,904 / 9,200 | 612,588 / 58,986 | **2,243,923 / 144,677** |
| Stop | spend reconciliation (accounting defect) | empty 2xx body, no retry policy | per-unit output ceiling (4,000) | per-call vote cap (1,024): a truncation | **none — the run completed** |
| Resumable? | n/a | n/a | n/a | no — a truncation is final | **n/a — nothing to resume** |
| Seeds rendered | 1 | 1 | 2 | 13 | **50** |
| Marginal cost | $0.00 | $0.00 | $0.00 | $0.00 | **$0.00** |

The two development calibrations sit beside these as the live measurements that
were not held-out runs: 2026-09-14 (60 calls, 10 units, 17.23 s per attempt, at
v3) and 2026-09-15 (720 calls, 120 units, 10.28 s per attempt, at v4, zero
truncations in sixty impostor-authored candidate ballot draws). The second is
what sized this run's ceilings and predicted its shape, and it did both well:
every ceiling had large headroom, and the per-call tail it bounded stayed
bounded.

## Limitations

* **The two declared one-sided effects are not separated by this run.** The
  citation repair raises the candidate's ejection rate and the turn bound
  lowers its citation relevance, both on the treatment arm only. The
  wrongful-ejection bound fails, and this design cannot say how much of that
  failure is the candidate's deduction and how much is the revision that made
  its ejections visible. That is a property of what was changed between runs,
  not a defect in the measurement.
* **The fourth run's 24 complete units are not pooled with these**, and this
  record does not pool them: the manifest's v4 section rules that a unit
  recorded before the revision and a unit recorded after it are not two draws
  from one instrument.
* **Fifty paired units resolve a net of 10, not a net of 2.** The minimum
  actionable effect was chosen for this design's resolution, and a net of 2 is
  inside the noise this sample carries — `b = 6, c = 0` is the smallest
  difference the exact test can call at all. A larger sample might resolve a
  real effect of this size; nothing here says whether one exists.
* **Both diagnostics are loose at these numerators.** One leaking turn per arm
  and a rule with two-sided error bound the leak rather than measure it, and
  the self-tell is counted on the ballot's OPENING only, so a confession that
  arrives later in a rationale is not in the 29 or the 3.
* **No per-call `finish_reason` distribution exists for this run**, for the
  reason given above: it is a calibration-mode field and the run's card forbids
  moving an instrument byte in the run's own pull request. The cap-signal
  statement stands on the disagreement counters and the absence of a truncation
  stop.
* **This is one model on one prompt set at one roster.** The roster is 4p1i
  with three living voters, and the manifest is explicit that a change of
  roster invalidates the token budget and needs a new authorization. Nothing
  here carries over to another model, a metered provider, or the 9p2i shape.
