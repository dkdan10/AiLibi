# Fresh-model deduction evaluation — run of 2026-09-15 (fourth attempt)

**The run stopped in its twenty-sixth unit of one hundred, on a per-call
truncation — a ballot response that reached its 1,024-token output cap. That is
an authorized stop condition, not a defect. Twenty-five units completed, twelve
paired seeds were graded, neither arm scored the primary outcome on any of them,
and the decision rule is stated on fifty paired units, so it is not evaluable.**
The stop authorizes no retry and no widening of any limit, and it is one of the
classes the manifest's resumption clause makes FINAL, so this run had one
sitting and has no second one. Nothing here is an adoption, and nothing here is
a measurement of the candidate's deduction either.

This directory is the partial evidence and the unresolved accounting that
[the execution manifest](../execution-manifest.md)'s stop rule requires a
stopped run to retain. It is the fourth such record and the first proposed for
`main`: the three earlier ones sit on the archive branches of pull requests the
owner closed unmerged.

```sh
git show origin/work/fresh-deduction-run:audits/deduction-candidate/run-2026-09-10/RESULTS.md
git show origin/work/fresh-deduction-run-2:audits/deduction-candidate/run-2026-09-13/RESULTS.md
git show origin/work/fresh-deduction-run-3:audits/deduction-candidate/run-2026-09-13-3/RESULTS.md
```

All four are compared at the end, beside the development calibration of
2026-09-14.

**On this directory's date.** The owner authorized the run on 2026-09-14
([the card](../../../tasks/work/fresh-deduction-authorization-4.md)) and the
sitting ran from `2026-09-15T03:34:25Z` to `2026-09-15T04:05:52Z` — late on
2026-09-14 in the machine's own zone (EDT). The directory is named for the UTC
date the archived records themselves carry, so that a reader comparing a
timestamp against the folder never has to reconcile two clocks.

## The design that was attempted

One meeting per frozen held-out prefix under two paired arms — the reference
`repaired_clock` (`format_version=2`, `evidence_reasoning_version=2`) and the
candidate `combined_accounts` (the reference plus `public_account_version=1` and
`attributed_testimony_version=1`) — over the 50 proof-free scripted prefixes of
the **fourth** held-out band, 7000–7999, frozen by the owner's merge of PR #456
(accepted seeds 7001–7057, 8 `witnessed_kill` skips, freeze record sha256
`5fe4b1e3e1ca931b5712d05785d9d72fff261502bcd2bd7ab71071e5a458ed8b`). Sequential,
both arms per seed before the next seed, on Featherless `Qwen/Qwen3.6-27B` under
the limits the fourth authorization re-sized from the live development
calibration of 2026-09-14: per-call caps turn 4,096 output / vote 1,024,
per-unit 106,000 input / 16,000 output, run-level 3,710,000 / 459,000, 6 h of
model work within an 8 h elapsed deadline, transport bound 4 attempts at 180 s
each. 50 prefixes × 2 arms = 100 units, about 600 model calls, scored on
`supported_correct_ejection` with the two-sided exact McNemar test over the
discordant pairs. **The run reached 156 provider attempts of about 600, and unit
26 of 100.**

The run was made from commit `10a19df8` on branch `work/fresh-deduction-run-4`,
with `experiments/fresh_deduction_instrument.py` at sha256
`3c2ebaf5 6e76de31 e556c63b 4953aa0c 892b1687 da5c03f6 9c60afa4 9a58d526` and
the execution manifest at `04bf714b…cc658d`, both recorded in
[checkpoint-final.json](checkpoint-final.json):

```sh
.venv/bin/python -c "import hashlib, pathlib; \
print(hashlib.sha256(pathlib.Path('experiments/fresh_deduction_instrument.py').read_bytes()).hexdigest())"
```

The invocation was exactly the one
[the manifest documents](../execution-manifest.md) in its "The live gate"
section — the same module, provider, manifest path and runner flag, with
`--output-dir`, `--json` and `--checkpoint` pointing outside the repository —
run once, with the API key delivered through `uv run --env-file` from a
credential-only file outside the repository that was deleted afterwards. It is
not reproduced here: no committed file outside the manifest and the instrument
may carry the runner flag, and
`tests/experiments/test_fresh_deduction_instrument.py::TestLiveGate::test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag`
scans every tracked file to keep that true.

**No report JSON exists.** `main()` writes the report only after
`run_instrument` returns, and it raised, so `--json` produced no file — the same
as on 2026-09-13. The instrument's own partial-state record is [stop.log](stop.log);
the twenty-six per-unit replays, the final [checkpoint-final.json](checkpoint-final.json)
written on the stop path, and the derived [usage-reconciliation.json](usage-reconciliation.json)
are the rest of the evidence.

Every figure below is reproducible from the files in this directory. The
reconciliation those figures are read off is itself a derivation rather than a
table somebody typed:

```sh
.venv/bin/python audits/deduction-candidate/run-2026-09-15/reconcile.py \
  audits/deduction-candidate/run-2026-09-15
```

which reprints [usage-reconciliation.json](usage-reconciliation.json) byte for
byte from the replays and the checkpoint beside it.

## What ran

Twelve paired seeds completed both arms and were graded — 7001, 7003, 7004,
7005, 7006, 7008, 7009, 7010, 7012, 7013, 7014, 7015. Seed 7016's reference arm
completed and its candidate arm stopped, so that pair is abandoned rather than
graded, and both halves of its spend are carried in the accounting below.

| Units | Arm | Result |
| --- | --- | --- |
| 1–24 (12 pairs) | both | completed and graded; 23 meetings resolved `SKIPPED`, one `EJECTED` |
| 25 | `repaired_clock` seed 7016 | completed; meeting resolved `SKIPPED`. Its pair never closed, so it is abandoned spend, not a graded unit |
| 26 | `combined_accounts` seed 7016 | **stopped** during ballot collection, on the per-call output cap |

Per-unit rows:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
rows = json.loads(Path('audits/deduction-candidate/run-2026-09-15/usage-reconciliation.json').read_text())['per_unit']
for r in rows:
    print(f\"{r['arm']:18s} {r['seed']} {r['replay_kind']:15s} calls {r['calls']} in {r['input_tokens']:6d} out {r['output_tokens']:5d} \"
          f\"| defaults {r['deadline_default_rows']} | outcome {r['outcome']} | ejected {r['ejected_player_id']}\")
"
```

## The stop

Quoted from [stop.log](stop.log):

```
PerCallCapExceeded: a response reached its 1024-token output cap (1024 tokens);
a truncation is a stop, not a datum
```

```
InstrumentAborted: PerCallCapExceeded: a response reached its 1024-token output
cap (1024 tokens); a truncation is a stop, not a datum; 25/100 units completed,
1886.3s elapsed, 1884.6s model work; combined_accounts: 78 calls, 348971 in,
44482 out, repaired_clock: 78 calls, 263617 in, 14504 out
```

This is `STOP_RULE`'s clause "a per-call response that reached its output cap
(a truncation is a stop, not a datum)", enforced where the manifest says it is
enforced: by `_InstrumentClient`, on the call that returns the response. The
stop is the mechanism working, not failing, and the rule is explicit that a
truncated body is a sample and is never retried.

### What the truncated call was

A ballot on `combined_accounts` seed 7016, cut off at exactly the authorized
vote cap. It does not appear on the replay's meeting row, because the instrument
refused it before the recording client could log it; it is visible as the
difference between the arm's abandoned spend and its aborted replay:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
D = Path('audits/deduction-candidate/run-2026-09-15')
rec = json.loads((D / 'usage-reconciliation.json').read_text())
ab = rec['abandoned']['combined_accounts']
rows = [json.loads(l) for l in (D / 'combined_accounts-seed-7016.jsonl').read_text().splitlines() if l.strip()]
m = [r for r in rows if r['kind'].startswith('meeting')][0]
on_row = {'calls': len(m['llm_calls']),
          'in': sum(c['input_tokens'] for c in m['llm_calls']),
          'out': sum(c['output_tokens'] for c in m['llm_calls'])}
print('abandoned  ', ab['calls'], ab['input_tokens'], ab['output_tokens'])
print('on the row ', on_row['calls'], on_row['in'], on_row['out'])
print('the refused call', ab['calls'] - on_row['calls'],
      ab['input_tokens'] - on_row['in'], ab['output_tokens'] - on_row['out'])
"
```

```
abandoned   5 18953 2881
on the row  4 14219 1857
the refused call 1 4734 1024
```

**4,734 input, 1,024 output — the cap to the token.** The truncated body then
failed to parse, which is what the manifest predicts of a body cut off at its
cap and is why the cap check is applied to the completion rather than to the
parse. From [stop.log](stop.log):

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for ModelAuthoredVoteBallot
  Invalid JSON: EOF while parsing a string at line 11 column 3620
```

The fragment the error quotes shows a ballot that began correctly and then ran
on into unrelated prose before the cap cut it — it opens `{"voter": "p-2",
"tar…` and ends mid-sentence on the subject of logic puzzles. This is a
runaway generation, not a large but legitimate ballot.

### Why the cap was reachable at all — the finding this run does establish

The vote cap is the one authorized number the fourth authorization did NOT
re-size. It is #437's 1,024 throughout, and the card's own justification for
leaving it is recorded there: "the vote cap is unchanged (largest measured
ballot 237)". That figure came from the development calibration of 2026-09-14 —
thirty candidate-arm ballots, largest 237. This run drew 37 candidate ballots
that resolved and one that did not:

| Arm | Call type | n (resolved) | mean output | max output | cap | max as % of cap |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | turn | 39 | 271.5 | 423 | 4,096 | 10.3% |
| `repaired_clock` | ballot | 39 | 100.4 | 144 | 1,024 | 14.1% |
| `combined_accounts` | turn | 40 | 917.9 | 1,900 | 4,096 | 46.4% |
| `combined_accounts` | ballot | 37 | 182.3 | 624 | 1,024 | 60.9% |
| `combined_accounts` | ballot (refused) | 1 | — | **1,024** | 1,024 | **100% — the stop** |

Reproduce with:

```sh
.venv/bin/python -c "
import json
from collections import defaultdict
from pathlib import Path
by = defaultdict(list)
for p in sorted(Path('audits/deduction-candidate/run-2026-09-15').glob('*.jsonl')):
    arm = p.stem.partition('-seed-')[0]
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    m = [r for r in rows if r['kind'].startswith('meeting')][0]
    for c in m['llm_calls']:
        payload = json.loads(c['response_text'])
        by[(arm, 'ballot' if 'target' in payload else 'turn')].append(c['output_tokens'])
for k in sorted(by):
    v = sorted(by[k]); print(k, 'n', len(v), 'mean %.1f' % (sum(v)/len(v)), 'max', v[-1])
"
```

Three things follow, and only the first is a claim about this run:

1. **The candidate arm's ballots have a long tail the calibration did not
   reach.** Its largest resolved ballot here is 624 tokens against a calibrated
   maximum of 237, and its 38th drew the cap. Thirty calls is not a bound on a
   rare tail — a point
   [the calibration record](../calibration-2026-09-14/CALIBRATION.md) makes
   about its own zero refusal count in the same words: "30 attempts is not a
   bound on a rare rate".
2. **Every other ceiling had large margins** (below). Input, output, per-unit,
   run-level and both wall clocks were nowhere near binding, and at the per-unit
   means this run measured, a complete 50-pair run would have charged about
   2.38 M input (64% of the run ceiling) and about 229 K output (50%). The
   re-sizing of 2026-09-14 did what it was asked to do; the dimension it did
   not re-size is the one that stopped the run.
3. **What follows from that is the owner's, not this run's.** A stop authorizes
   no widening of any limit, and this record proposes none. It states the
   measurement and hands it over.

## Primary outcome, discordant pairs and the decision rule

The three graders are a pure function over a finished `UnitRecord`, run after
the unit has returned, and they ran for each of the 24 units that completed a
pair. Nothing they produce reaches a listener or a tactic — no grader is called
from the path that drives the model, and no stop condition anywhere reads an
outcome — so the grades below are a readout of a fixed sample, not an interim
analysis that could have changed what the run did next. They are in
[checkpoint-final.json](checkpoint-final.json).

| Quantity | Value |
| --- | --- |
| Paired units graded | **12 of 50** (seed 7016 completed its reference arm only) |
| Units completed | 25 of 100 (decision coverage 25%) |
| `repaired_clock` supported-correct ejections | **0 of 12** |
| `combined_accounts` supported-correct ejections | **0 of 12** |
| Discordant pairs `b` (candidate 1, reference 0) | **0** |
| Discordant pairs `c` (reference 1, candidate 0) | **0** |
| Net `b - c` | **0** |

```sh
.venv/bin/python -c "
import json
from pathlib import Path
cp = json.loads(Path('audits/deduction-candidate/run-2026-09-15/checkpoint-final.json').read_text())
by = {}
for u in cp['units']:
    by.setdefault(u['seed'], {})[u['arm']] = u['supported_correct_ejection']
b = sum(1 for v in by.values() if v['combined_accounts'] and not v['repaired_clock'])
c = sum(1 for v in by.values() if v['repaired_clock'] and not v['combined_accounts'])
print('paired seeds', len(by), '| b', b, '| c', c, '| net', b - c)
"
```

```
paired seeds 12 | b 0 | c 0 | net 0
```

All twelve pairs are concordant at 0/0, so none contributes to `b` or `c`. The
exact test on that is the empty-sample constant, not a null result:

```sh
.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); \
from paired_stats import exact_mcnemar_p as p; print(p(0, 0))"
```

```
1.0
```

`exact_mcnemar_p`'s own docstring says so: with no discordant pairs there is no
evidence either way and p is 1.0.

The three clauses of `DECISION_RULE`, each evaluated:

| Clause | Bar | State |
| --- | --- | --- |
| Two-sided exact McNemar p over the discordant pairs | below 0.05 | **not evaluable** — 12 paired units of the 50 the rule is stated on; the 1.0 above is the empty-sample constant |
| Net paired difference `b - c` | at least 10 of 50 | **not evaluable** — `b = c = 0` on twelve concordant pairs; the bar is a count out of fifty |
| Candidate's net increase in wrongful crew ejections | no larger than `b - c` | **not evaluable** — 0 against 0 on twelve pairs; see the bound below |

**Conjunction: not evaluable.** `combined_accounts` does not advance. It is also
not rejected: twelve pairs in which neither arm scored refutes nothing about a
design that resolves fifty. Under `DECISION_RULE`'s own wording "any other
result is inconclusive, and inconclusive is not success", and this is weaker
than inconclusive, because inconclusive presumes the sample the rule is stated
on.

**Wrongful-ejection bound.** `WRONGFUL_EJECTION_TRADEOFF` counts a unit whose
meeting ejected a player whose hidden role is CREWMATE. **Zero wrongful
ejections on both arms**, across all 25 completed units: 24 meetings resolved
`SKIPPED` and the one ejection landed on the impostor. The figure is true and
carries little information — the bound is a net increase over fifty paired units
and cannot be computed on twelve.

### The one ejection, and why it did not score

`combined_accounts` seed 7015 ejected `p-4`, whose hidden role is IMPOSTOR:
`role_correct` is true and `supported_correct_ejection` is false. The reason is
the primary outcome's own conjunction rather than the relevance rule. Both
ballots naming `p-4` were **uncited** — they carried neither a
`primary_reason_id` nor a `primary_reason_observation_id` — so neither could be
supported, and `off_target_citations` is 0 because a ballot with no citation has
none to be off target. The third ballot was guard-rewritten to SKIP
(`uncited_coerced`).

```sh
.venv/bin/python -c "
import json
from pathlib import Path
cp = json.loads(Path('audits/deduction-candidate/run-2026-09-15/checkpoint-final.json').read_text())
u = [x for x in cp['units'] if x['seed'] == 7015 and x['arm'] == 'combined_accounts'][0]
print('ejected', u['ejected_player_id'], u['ejected_role'], '| role_correct', u['role_correct'],
      '| supported_correct', u['supported_correct_ejection'],
      '| naming', u['naming_ballots'], '| off_target', u['off_target_citations'])
for b in u['supported']:
    print(' ', b['voter'], '->', b['target'], '| verdict', b['verdict'], '| guard', b['guard_rewrite_reason'])
"
```

```
ejected p-4 IMPOSTOR | role_correct True | supported_correct False | naming 2 | off_target 0
  p-1 -> p-4 | verdict uncited | guard None
  p-2 -> p-4 | verdict uncited | guard None
  p-4 -> SKIP | verdict uncited | guard uncited_coerced
```

This is one unit. It is reported because a reader of a stopped run is entitled
to know what the instrument actually recorded, and it is a measurement of
nothing: one meeting of a design that resolves fifty paired seeds.

**Ballots, for the record and not as a measure.** Over the 24 graded units:

| Arm | Ballots | supported | unsupported | uncited | guard-rewritten (overlay) | naming (non-SKIP) |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 36 | 5 | 0 | 31 | 0 | 5 |
| `combined_accounts` | 36 | 1 | 0 | 35 | 13 | 3 |

The guard-rewritten column is an OVERLAY on the verdict columns rather than a
fourth bucket, so it does not add to the 36. The candidate arm's 13 are 12
`uncited_coerced` and 1 `under_gate_redirect`; the reference arm recorded none.

```sh
.venv/bin/python -c "
import json
from collections import Counter
from pathlib import Path
cp = json.loads(Path('audits/deduction-candidate/run-2026-09-15/checkpoint-final.json').read_text())
verdicts, guards, naming = Counter(), Counter(), Counter()
for u in cp['units']:
    for b in u['supported']:
        verdicts[(u['arm'], b['verdict'])] += 1
        if b['guard_rewrite_reason']: guards[(u['arm'], b['guard_rewrite_reason'])] += 1
        if b['target'] != 'SKIP': naming[u['arm']] += 1
print(dict(verdicts)); print(dict(guards)); print(dict(naming))
"
```

## Meeting-internal defaults, charged failed attempts and transport attempts, per arm

| Arm | Units graded | Defaulted turns | Defaulted votes | By validation | By deadline | Degraded openings | Units with defaults | Charged failed attempts | Retried calls | Unaccounted attempts | Units with retries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `combined_accounts` | 12 (+1 stopped) | 2 | 0 | 2 | 0 | 0 | 2 | 1 (4,734 in / 1,024 out) | 0 | 0 | 0 |

Both candidate-arm defaults are schema-validation substitutions of a placeholder
turn, on seeds 7004 and 7012, each recorded as a zero-token `deadline_default`
`failed_call` row whose message the instrument classified without complaint — so
the "a default this instrument cannot classify is a stop" condition did not fire.
At 2 in 156 attempts the observed substitution rate is inside the ~1-in-50 the
manifest accepts. Both fell on the candidate arm, as on 2026-09-13.

Two consequences the manifest requires a reader to carry, restated here: a
defaulted ballot is a SKIP the voter did not choose, and because the privileged
grader's "every naming ballot supported" is an `all()`, a defaulted ballot
removes a constraint rather than failing it and biases the primary outcome
upward. Neither default here was a ballot, and `units_with_defaults` is 2 of the
candidate arm's 12 graded units — the bound on how many of its decisions rest on
a partly unauthored meeting.

**The one charged failed attempt is the truncated ballot** described above. It is
not on any replay row and it is not a schema fail-soft: the instrument stopped
the run on it rather than letting the meeting layer substitute for it.

**No transport retry fired.** The provider answered every one of the 156 sends
with a completion; no row carries the `no-completion-returned` marker, and
`retried_calls`, `unaccounted_attempts` and `attempts_by_trigger` are empty on
both arms, so **unaccounted attempts are 0 on both arms**. The bound PR #450
added (4 attempts, 180 s each) was in force and never engaged. Verify the
absence with:

```sh
grep -c "no-completion-returned" audits/deduction-candidate/run-2026-09-15/*.jsonl
```

which prints `:0` for all twenty-six files.

## Usage against every authorized limit

Per arm, graded units plus the abandoned pair — the whole of what was charged:

| Arm | Attempts | Completions | Charged-and-refused | Input tokens | Output tokens | `cost_usd` | Model work |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 78 | 78 | 0 | 263,617 | 14,504 | 0.0 | 548.2 s |
| `combined_accounts` | 78 | 77 | 1 | 348,971 | 44,482 | 0.0 | 1,336.4 s |
| **Run total** | **156** | **155** | **1** | **612,588** | **58,986** | **0.0** | **1,884.6 s** |

Of those, 145 calls / 572,380 in / 54,884 out are on graded units and 11 calls /
40,208 in / 4,102 out are the abandoned pair's (seed 7016, both arms).

| Limit | Authorized | Actual | Used | Fired? |
| --- | --- | --- | --- | --- |
| Run input tokens | 3,710,000 | 612,588 | 16.51% | no |
| Run output tokens | 459,000 | 58,986 | 12.85% | no |
| Per-unit input tokens | 106,000 | 36,743 (largest unit, candidate seed 7009) | 34.7% | no |
| Per-unit output tokens | 16,000 | 4,816 (largest unit, candidate seed 7009) | 30.1% | no |
| Elapsed wall | 8 h (28,800 s) | 1,886.3 s | 6.55% | no |
| Model work | 6 h (21,600 s) | 1,884.6 s | 8.73% | no |
| Per-call output cap, turn | 4,096 | largest turn 1,900 (candidate) | 46.4% | no |
| **Per-call output cap, vote** | **1,024** | **1,024 (one ballot, candidate seed 7016)** | **100%** | **YES — this is the stop** |
| Transport attempts | 4 per call, 180 s each | 1 attempt per call, 156 of 156 | 25% of the bound | no |
| Dollar | $0.00 marginal | $0.00 | — | not an enforcement mechanism on this provider |

**Marginal cost: $0.00.** Every recorded `cost_usd` on this run is exactly 0.0,
by construction rather than by measurement: the Featherless provider's zero
pre-flight rate disables `BudgetedLLMClient`'s USD dimension
(`llm/featherless_client.py:243-244`, `llm/budgeted_client.py:118-126`). The
resources consumed were subscription capacity and 1,886.3 seconds of wall on one
worker.

**Pace.** 1,884.6 s of model work over 156 attempts is **12.08 s per attempt** —
7.03 s on the reference arm and 17.13 s on the candidate. At the pooled pace 600
attempts would be about 2 h 1 m against the authorized 6 h. The wall was never
close to binding.

### Side by side with the calibration that sized these limits

| Figure | Calibration (2026-09-14, development inputs) | This run (held-out band 7000-7999) |
| --- | --- | --- |
| Units | 10 (5 paired seeds) | 25 (12 paired seeds graded) |
| Attempts | 60 | 156 |
| `repaired_clock` per unit | 21,026 in / 1,108 out | 20,197 in / 1,107 out |
| `combined_accounts` per unit | 28,430 in / 3,137 out | 27,502 in / 3,467 out |
| Largest unit | 35,232 in / 4,590 out | 36,743 in / 4,816 out |
| Largest candidate turn | 2,036 (against a 2,048 cap) | 1,900 (against a 4,096 cap) |
| Largest candidate ballot | 237 | 624 resolved, and one at the 1,024 cap |
| Pace per attempt | 17.23 s pooled | 12.08 s pooled |
| Refusals / defaults | 0 / 0 | 1 truncation / 2 defaulted turns |

The per-unit means the calibration measured held almost exactly, and the per-unit
maxima came in about 4-5% above its largest measured unit — still one third of
the ceilings. The one dimension that did not carry over is the per-call ballot
tail, which is the dimension the calibration's own thirty-ballot sample could not
bound and the one number the fourth authorization did not move.

## Every stop condition, checked

`STOP_RULE`'s enumerated conditions, each against what the run recorded:

| Stop condition | Fired? | Evidence |
| --- | --- | --- |
| Token budget exhausted, per-unit level | no | 34.7% / 30.1% of the per-unit ceilings at the largest unit |
| Token budget exhausted, run level | no | 16.51% / 12.85% of the run ceilings |
| Elapsed wall deadline | no | 1,886.3 s of 28,800 s |
| Model-work window | no | 1,884.6 s of 21,600 s; no attempt was cut off in flight |
| **A response that reached its output cap (truncation)** | **YES** | one ballot at exactly 1,024 output tokens against the 1,024 vote cap, `combined_accounts` seed 7016 |
| A held-out digest or skip differing from the frozen manifest | no | `verify_frozen_set` passed before any client existed: 50 accepted prefixes, 8 skips, freeze record sha256 `5fe4b1e3…58ed8b` |
| A rendered prompt or regenerated prefix matching `body-p-\d+-\d+` | no | asserted over all 50 regenerated prefixes before the run; the rendered prompts carry only the v2 handles `body-p-1` … `body-p-4` (see below) |
| A unit whose recorded observation clock or experiment config is not the arm's | no | every replay records `temporal_observation_version` 2; `usage-reconciliation.json`'s `per_unit[].experiment_config` carries the candidate versions on `combined_accounts` and null on `repaired_clock` |
| A recorded meeting default the instrument cannot classify | no | both recorded defaults classified as `validation` turns |
| A call that came back with no completion at all (transport) | no | 156 attempts, 155 completions and one refused completion; no `no-completion-returned` marker anywhere |
| The recorded-spend reconciliation (`SPEND_RECONCILIATION`) | no | ran on all 24 graded units and passed |
| The post-unit budget cap read-back (`BUDGET_CAP_READBACK`) | no | ran on all 24 graded units and passed |

No stop condition reads an outcome, and none did here. The run stopped on a
per-call cap at a fixed point in a fixed sample, with no interim analysis and no
optional stopping.

**On the body-handle check.** Scanning the whole archive for `body-p-\d+-\d+`
returns twenty-six matches and none of them is on a surface the stop condition
covers: each is the engine's own entity id inside a tick row's `actions` field,
the raw record of the scripted report step. What the condition covers is the
regenerated prefixes, the rendered prompts and the emitted report, and all of
those are clean — every prompt the model was handed carries only `body-p-1`
through `body-p-4`, which is what temporal v2 renders by construction:

```sh
.venv/bin/python -c "
import json, re
from collections import Counter
from pathlib import Path
legacy, in_prompts = Counter(), Counter()
for p in sorted(Path('audits/deduction-candidate/run-2026-09-15').glob('*.jsonl')):
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    m = [r for r in rows if r['kind'].startswith('meeting')][0]
    for r in rows:
        for h in re.findall(r'body-p-\d+-\d+', json.dumps(r)): legacy[r['kind']] += 1
    for c in m['llm_calls']:
        for h in re.findall(r'body-p-\d+(?:-\d+)?', c['prompt'] or ''): in_prompts[h] += 1
print('legacy handles by row kind:', dict(legacy))
print('handles in rendered prompts:', dict(in_prompts))
"
```

```
legacy handles by row kind: {'tick': 26}
handles in rendered prompts: {'body-p-2': 6, 'body-p-3': 9, 'body-p-4': 8, 'body-p-1': 4}
```

**On the source-identity check.** The two arms render different template families
by design and each carried exactly one marker set throughout, so no source
changed mid-run: `repaired_clock` recorded `accusation_round.qwen3_6_27b.v5` /
`crewmate_report.qwen3_6_27b.v5` / `impostor_report.qwen3_6_27b.v5` /
`vote_ballot.qwen3_6_27b.v5`, and `combined_accounts` the
`…_accounts.qwen3_6_27b.v3.accounts1.attributed1` family — revision v3, the
corrected account prompts PR #452 landed. Both are in
[usage-reconciliation.json](usage-reconciliation.json)'s per-arm
`prompt_version_markers`, and every recorded call names the model
`Qwen/Qwen3.6-27B`.

## Resumptions

**None, and none was permitted.** The manifest's resumption clause of 2026-09-14
authorizes one resume per stop for transport exhaustion, a credential failure or
a process crash, and makes a stop by "a limit, a truncation, a digest or
provenance mismatch, or the legacy body handle" final. This stop is a truncation.
The run had exactly one sitting: it began at `2026-09-15T03:34:25Z`, stopped at
`2026-09-15T04:05:52Z`, and no `--resume` invocation was made. The checkpoint
mechanism nevertheless did its job — the final checkpoint written on the stop
path carries the abandoned pair's 11 calls, 40,208 input, 4,102 output and
112.4 model-work seconds, which is why the accounting above balances against the
stop line to the token.

## What this archive contains

| File | What it is |
| --- | --- |
| [stop.log](stop.log) | the run's stdout and stderr, ending in the instrument's own partial-state record |
| `repaired_clock-seed-*.jsonl`, `combined_accounts-seed-*.jsonl` (26 files) | the per-unit replays: ticks, the meeting with its transcript, ballots, verdict and every recorded call with its rendered prompt. `combined_accounts-seed-7016.jsonl` is the stopped unit's, with a `meeting_aborted` row |
| [checkpoint-final.json](checkpoint-final.json) | the checkpoint written on the stop path: the 24 graded units, the identity digests the run was held to, the budgets it spent and the abandoned pair's spend |
| [usage-reconciliation.json](usage-reconciliation.json) | per-unit and per-arm usage, verdicts, defaults, charged failed attempts, transport attempts, provenance and body handles, derived from the two above |
| [reconcile.py](reconcile.py) | the derivation that writes the file above, so its numbers can be recomputed rather than trusted |
| [rendered-prefixes.json](rendered-prefixes.json) | the thirteen prefixes this run rendered — seeds 7001, 7003, 7004, 7005, 7006, 7008, 7009, 7010, 7012, 7013, 7014, 7015, 7016 — regenerated after the run and checked against their frozen digests |
| [render_rendered_prefixes.py](render_rendered_prefixes.py) | the derivation that writes the file above, reading the rendered seeds off the replays rather than off the freeze record |

Nothing was left out: the whole archive is about 2.8 MB, far inside the size at
which [the run's card](../../../tasks/work/fresh-deduction-authorization-4.md)
would have made the runner choose. No report JSON exists, for the reason given
above. The archive was scanned for the API key before it was committed and
carries neither the key nor its first six characters.

## Held-out status

**Thirteen seeds of the fourth band are revealed by this archive: 7001, 7003,
7004, 7005, 7006, 7008, 7009, 7010, 7012, 7013, 7014, 7015 and 7016. The other
thirty-seven accepted seeds were never rendered to the model.**

The instrument serialized no prefix during the run — it never does, and
`assert_report_holds_no_prefix_bytes` refuses a report that carries one. What
this directory publishes is the twenty-six replays, whose meeting rows carry the
prompts those thirteen prefixes rendered under each arm and whose tick rows carry
the scripted steps, plus `rendered-prefixes.json`, which is the thirteen rendered
prefixes regenerated and written out AFTER the run.

The other thirty-seven accepted prefixes were regenerated in process, checked
against the frozen digests and then discarded unrendered. **They are deliberately
NOT archived here**, which is the decision the first three runners made and the
same reasoning: the manifest archives prefixes "when they are no longer held
out", and these thirty-seven still are. Committing them would convert the rest of
the band to development data to no purpose. The runner opened, printed and
reasoned about no prefix before the run.

Three consequences the owner's next decision has to carry:

1. **This run did not convert the band's status.** The freeze manifest still
   reads `held_out`, and flipping it belongs to the decision that acts on this
   record, not to the runner. If this result informs a fix — and a per-call cap
   is exactly the kind of finding that would — the manifest's Roles section
   requires that flip and a new band under a new card.
2. **A re-run on this same band would not be a clean 50-unit held-out sample**,
   because thirteen of its seeds are now public. Any future confirmation claim
   needs a new band frozen under a new card, by a preparer who has not read this
   document.
3. **Seventeen seeds of held-out margin are now gone across four runs** — seed
   3000 of the first band, 5000 of the second, 6000 and 6001 of the third, and
   thirteen of the fourth. This attempt spent more than the three before it
   together, and it also got much further: twelve graded pairs against one.

## The verdict

In the preregistration's own vocabulary, whose four possible decisions are
"advance for an explicitly scoped adopting review, revise and evaluate a new
version, reject, or gather more evidence under a new authorized manifest":

**`combined_accounts` does not advance to an explicitly scoped adopting review,
and it is not rejected.** The decision rule's conjunction is not evaluable on
twelve of fifty paired units, and neither arm scored the primary outcome on any
of them. The only one of the four decisions a stopped run can point to is
gathering more evidence under a new authorized manifest — and the preregistration
is explicit that more evidence "is not an automatic spending authorization". What
this run measured, and what it did not, is above; which decision follows is the
owner's, on a card.

**A result is a measurement and never an adoption.** That is true of a
conclusive result and it is true of this one. Nothing in this directory adopts
anything, flips any flag or makes any experiment ON; the candidate stays
default-OFF exactly as it was.

## Compared with the three earlier attempts and the calibration

| | 2026-09-10 (PR #445, closed) | 2026-09-13 (PR #448, closed) | 2026-09-13 (PR #451, closed) | 2026-09-15 (this run) |
| --- | --- | --- | --- | --- |
| Band | 3000-3999 (now development) | 5000-5999 (now development) | 6000-6999 (now development) | 7000-7999 |
| Units completed | 1 of 100 | 0 of 100 | 3 of 100 | **25 of 100** |
| Paired seeds graded | 0 | 0 | 1 | **12** |
| Attempts | 12 | 5 | 22 | **156** |
| Input / output tokens | 36,003 / 3,401 | 13,182 / 993 | 82,904 / 9,200 | **612,588 / 58,986** |
| Stop | spend reconciliation (accounting defect) | empty 2xx body, no retry policy | per-unit output ceiling (4,000) | **per-call vote cap (1,024): a truncation** |
| Stop class | repaired (#447) | repaired (#450) | re-sized (#457) | **final under the resumption clause** |
| Resumable? | n/a | n/a | n/a | **no — a truncation is final** |
| Seeds rendered | 1 | 1 | 2 | **13** |
| Marginal cost | $0.00 | $0.00 | $0.00 | **$0.00** |

The development calibration of 2026-09-14 sits beside these as the one live
measurement that was not a held-out run: 60 calls, 10 units, 17.2 s per attempt,
zero refusals, $0.00, on development inputs. Its per-unit figures predicted this
run's almost exactly. Its per-call tail did not.
