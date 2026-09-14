# Fresh-model deduction evaluation — run of 2026-09-13 (third attempt)

**The run stopped in its fourth unit of one hundred, on the per-unit output
token budget — an authorized stop condition, not a defect. Three units
completed, one seed carried both arms, and the primary outcome was never
graded, so the decision rule is not evaluable.** The stop authorizes no retry
and no widening of any limit. Nothing here is an adoption, and nothing here is
a measurement of the candidate's deduction either.

This directory is the partial evidence and the unresolved accounting that
[the execution manifest](../execution-manifest.md)'s stop rule requires a
stopped run to retain. It is the third such record and the first to reach
`main`. The two earlier ones are on closed pull requests' archive branches:

```sh
git show origin/work/fresh-deduction-run:audits/deduction-candidate/run-2026-09-10/RESULTS.md
git show origin/work/fresh-deduction-run-2:audits/deduction-candidate/run-2026-09-13/RESULTS.md
```

All three are compared at the end.

## The design that was attempted

One meeting per frozen held-out prefix under two paired arms — the reference
`repaired_clock` (`format_version=2`, `evidence_reasoning_version=2`) and the
candidate `combined_accounts` (the reference plus `public_account_version=1`
and `attributed_testimony_version=1`) — over the 50 proof-free scripted
prefixes of the **third** held-out band, 6000–6999, frozen by the owner's merge
of PR #449 as `c06ee085` (accepted seeds 6000–6058, 9 `witnessed_kill` skips,
freeze record sha256
`7ded19906a7026ae3724894af67cf3667d35f4230d532bf825e495d4666ecd37`).
Sequential, both arms per seed before the next seed, on Featherless
`Qwen/Qwen3.6-27B` under the limits the owner authorized by merging #437 as
`0f49d8e6` with the wall row widened for this run to 6 h of model work within
8 h elapsed ([the run's card](../../../tasks/work/fresh-deduction-authorization-3.md)).
50 prefixes × 2 arms = 100 units, about 600 model calls, scored on
`supported_correct_ejection` with the two-sided exact McNemar test over the
discordant pairs. **The run reached 22 provider attempts of about 600, and
unit 4 of 100.**

The run was made from commit `c461c9d0` on branch `work/fresh-deduction-run-3`,
with `experiments/fresh_deduction_instrument.py` at sha256
`22373f60 37d09169 d2fe15b4 910b4468 04afb2d9 959eb0c6 e9d01458 48141e85`:

```sh
.venv/bin/python -c "import hashlib, pathlib; \
print(hashlib.sha256(pathlib.Path('experiments/fresh_deduction_instrument.py').read_bytes()).hexdigest())"
```

The invocation was exactly the one
[the manifest documents](../execution-manifest.md) in its "The live gate"
section — the same module, provider, manifest path and runner flag, with
`--output-dir` and `--json` pointing outside the repository — run once, with
the API key delivered through `uv run --env-file` from a credential-only file
outside the repository that was deleted afterwards. It is not reproduced here:
no committed file outside the manifest and the instrument may carry the runner
flag, and
`tests/experiments/test_fresh_deduction_instrument.py::TestLiveGate::test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag`
scans every tracked file to keep that true.

**No report JSON exists.** `main()` writes the report only after
`run_instrument` returns, and it raised, so `--json` produced no file. The
instrument's own partial-state record is [stop.log](stop.log); the four per-unit
replays and the derived [usage-reconciliation.json](usage-reconciliation.json)
are the rest of the evidence.

Every figure below is reproducible from the files in this directory. The
per-unit totals come from:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
D = Path('audits/deduction-candidate/run-2026-09-13-3')
for p in sorted(D.glob('*.jsonl')):
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    m = [r for r in rows if r['kind'].startswith('meeting')][0]
    c = m['llm_calls']
    f = [r for r in rows if r['kind'] == 'failed_call' and (r['input_tokens'] or r['output_tokens'])]
    d = [r for r in rows if r['kind'] == 'failed_call' and r['error_type'] == 'deadline_default']
    print(p.name, m['kind'],
          'calls', len(c), 'in', sum(x['input_tokens'] for x in c), 'out', sum(x['output_tokens'] for x in c),
          '| charged-failed', len(f), sum(x['input_tokens'] for x in f), sum(x['output_tokens'] for x in f),
          '| defaults', len(d), '| outcome', m.get('outcome'), '| ejected', m.get('ejected_player_id'),
          '| models', sorted({x['model'] for x in c}),
          '| cost', sum(x['cost_usd'] for x in c))
"
```

```
combined_accounts-seed-6000.jsonl meeting calls 6 in 24282 out 3056 | charged-failed 0 0 0 | defaults 0 | outcome SKIPPED | ejected None | models ['Qwen/Qwen3.6-27B'] | cost 0.0
combined_accounts-seed-6001.jsonl meeting_aborted calls 3 in 9417 out 1661 | charged-failed 1 4541 1455 | defaults 1 | outcome None | ejected None | models ['Qwen/Qwen3.6-27B'] | cost 0.0
repaired_clock-seed-6000.jsonl meeting calls 6 in 22559 out 1601 | charged-failed 0 0 0 | defaults 0 | outcome SKIPPED | ejected None | models ['Qwen/Qwen3.6-27B'] | cost 0.0
repaired_clock-seed-6001.jsonl meeting calls 6 in 22105 out 1427 | charged-failed 0 0 0 | defaults 0 | outcome SKIPPED | ejected None | models ['Qwen/Qwen3.6-27B'] | cost 0.0
```

## What ran

| Unit | Arm | Seed | Result |
| --- | --- | --- | --- |
| 1 | `repaired_clock` | 6000 | completed; meeting resolved `SKIPPED`, no ejection |
| 2 | `combined_accounts` | 6000 | completed; meeting resolved `SKIPPED`, no ejection |
| 3 | `repaired_clock` | 6001 | completed; meeting resolved `SKIPPED`, no ejection |
| 4 | `combined_accounts` | 6001 | **stopped** during ballot collection, on the per-unit output budget |

Every meeting that resolved reached a verdict — three turns, three ballots, a
recorded outcome — so this is the first of the three attempts in which the
instrument carried a real model through complete units. All three verdicts were
`SKIPPED`. One paired seed (6000) carried both arms.

## The stop

Quoted from [stop.log](stop.log):

```
llm.budget.BudgetExceededError: LLM budget exceeded on output_tokens:
current=3116.0 + delta=1024.0 > cap=4000.0
```

```
InstrumentAborted: BudgetExceededError: LLM budget exceeded on output_tokens:
current=3116.0 + delta=1024.0 > cap=4000.0; 3/100 units completed, 369.1s
elapsed, 368.8s model work; combined_accounts: 10 calls, 38240 in, 6172 out,
repaired_clock: 12 calls, 44664 in, 3028 out
```

This is the first clause of `STOP_RULE` — "a token budget exhausted at either
the per-unit or the run level" — enforced where the manifest says it is
enforced: by the budget's pre-flight, on the call that would cross the ceiling.
The stop is the mechanism working, not failing.

### The arithmetic of the crossing

The per-unit output cap is 4,000. Four charged attempts of
`combined_accounts` seed 6001 reached it, and the fifth could not be started:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
D = Path('audits/deduction-candidate/run-2026-09-13-3')
rows = [json.loads(l) for l in (D / 'combined_accounts-seed-6001.jsonl').read_text().splitlines() if l.strip()]
m = [r for r in rows if r['kind'].startswith('meeting')][0]
charged = [(c['agent_id'], c['input_tokens'], c['output_tokens'], 'resolved') for c in m['llm_calls']]
charged += [(r.get('call_id'), r['input_tokens'], r['output_tokens'], r['error_type'])
            for r in rows if r['kind'] == 'failed_call' and r['output_tokens']]
print('charged outputs', [c[2] for c in charged], 'sum', sum(c[2] for c in charged))
print('rows', charged)
"
```

```
charged outputs [744, 694, 223, 1455] sum 3116
rows [('p-4', 2386, 744, 'resolved'), ('p-3', 2886, 694, 'resolved'), ('p-2', 4145, 223, 'resolved'), ('call-2', 4541, 1455, 'ValidationError')]
```

In order: the first turn resolved (744 output); the second turn — `call-2`,
p-2's — came back as a payload the schema refused, was billed for 1,455 output
tokens, charged after the fact off its parse-failure metadata and fail-softed by
the meeting layer to a placeholder turn; the third turn resolved (694); the
first ballot resolved (223). Running total 3,116. The second ballot's pre-flight
must reserve the full authorized vote cap of 1,024 before the call is made, and
3,116 + 1,024 = 4,140 > 4,000. The run stopped there, before spending it.

The refused payload's own error, from the same replay's `failed_call` row:

```
8 validation errors for MeetingTurn
claims.0
  Input tag 'whereabouts' found using 'type' does not match any of the expected
  tags: 'alibi', 'accusation', 'corroboration'
```

That is a schema-invalid payload, which the manifest calls a sample and never
retries, and which the meeting layer is designed to fail-soft. It is **not** a
truncation: 1,455 output tokens against a 2,048 turn cap.

### Why the ceiling was reachable at all — the finding this run does establish

The candidate arm writes roughly twice the reference arm's output per call, and
the per-unit output budget was sized on a projection about half of what either
arm actually produced.

| Unit | Arm | Charged output | % of the 4,000 per-unit cap | Charged input | % of the 45,000 cap |
| --- | --- | --- | --- | --- | --- |
| seed 6000 | `repaired_clock` | 1,601 | 40.0% | 22,559 | 50.1% |
| seed 6001 | `repaired_clock` | 1,427 | 35.7% | 22,105 | 49.1% |
| seed 6000 | `combined_accounts` | 3,056 | 76.4% | 24,282 | 54.0% |
| seed 6001 | `combined_accounts` | 3,116 (stopped) | 77.9% | 13,958 | 31.0% |

The candidate arm's one **completed** unit cleared the cap by 28 tokens. Its six
charged outputs were 528, 1,045, 1,011 (turns) and 204, 160, 108 (ballots); the
running total before its last ballot was 2,948, and that ballot's pre-flight
reserved 1,024 for a total of 3,972 against a ceiling of 4,000. The margin was
0.7% of the cap on a clean unit with no failed attempt at all.

The authorization's own projection (`Total token budget`, both the manifest and
the run's card) was 600 calls at 220 output tokens each. Measured here:
`repaired_clock` averaged 252 output per attempt (3,028 over 12) and
`combined_accounts` 617 (6,172 over 10). On three units this is not a rate, but
the direction is not marginal, and it makes two ceilings bind rather than one:

- **Per-unit output, 4,000.** Binding for the candidate arm today, as the stop
  shows. A clean candidate unit costs about 3,056; one charged-and-refused turn
  costs another 1,455; the pre-flight reserves 1,024 before each ballot.
- **Run-level output, 200,000.** A paired seed costs about 1,514
  (`repaired_clock` mean) + 3,056 (`combined_accounts`, its one clean unit) =
  4,570 output tokens. 200,000 / 4,570 ≈ 43.8, so on this sample the run
  ceiling supports about 43 of the 50 paired seeds — it would have bound before
  the design finished even if every unit ran clean.
- The input ceilings and both wall clocks had large margins (below).

## Primary outcome, discordant pairs and the decision rule

**Not graded.** The three graders are a pure function over finished
`UnitRecord`s that `run_instrument` calls only after the last unit; the run
never reached that point, so `grade_supported`, `grade_citation_relevance` and
`grade_privileged` did not run and no graded field exists anywhere in this
archive.

What the archive does fix, mechanically and without a grader:
`PRIMARY_OUTCOME_RUBRIC` scores a unit 1 only when "its meeting ejected the
player whose hidden role is IMPOSTOR". **All three completed meetings resolved
`SKIPPED` with `ejected_player_id` null**, so each would have scored 0 whatever
the support and relevance passes returned. That is a consequence of the rubric's
own wording applied to the recorded verdicts, not a grader result, and it is
stated that way.

| Quantity | Value |
| --- | --- |
| Paired units completed | **1 of 50** (seed 6000; seed 6001 completed the reference arm only) |
| Units completed | 3 of 100 (decision coverage 3%) |
| `repaired_clock` supported-correct ejections | 0 of its 2 completed units — no ejection occurred; not graded |
| `combined_accounts` supported-correct ejections | 0 of its 1 completed unit — no ejection occurred; not graded |
| Discordant pairs `b` (candidate 1, reference 0) | 0 |
| Discordant pairs `c` (reference 1, candidate 0) | 0 |
| Net `b - c` | 0 |

The one paired unit is concordant at 0/0, so it contributes to neither `b` nor
`c`. The exact test on that is the empty-sample constant, not a null result:

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
| Two-sided exact McNemar p over the discordant pairs | below 0.05 | **not evaluable** — 1 paired unit of the 50 the rule is stated on; the 1.0 above is the empty-sample constant |
| Net paired difference `b - c` | at least 10 of 50 | **not evaluable** — `b = c = 0` on one concordant pair |
| Candidate's net increase in wrongful crew ejections | no larger than `b - c` | **not evaluable** — see the bound below |

**Conjunction: not evaluable.** `combined_accounts` does not advance. It is also
not rejected: a run that graded nothing refutes nothing. Under `DECISION_RULE`'s
own wording "any other result is inconclusive, and inconclusive is not success",
and this is weaker than inconclusive, because inconclusive presumes a sample.

**Wrongful-ejection bound.** `WRONGFUL_EJECTION_TRADEOFF` counts a unit whose
meeting ejected a player whose hidden role is CREWMATE. **Zero wrongful
ejections on both arms** — three resolved meetings, three `SKIPPED` verdicts, no
ejection of anyone. The figure is true and carries no information: the bound is
a net increase over 50 paired units and cannot be computed on one.

**Ballots, for the record and not as a measure.** `repaired_clock` recorded 6
ballots over its 2 completed units — 5 SKIP and 1 naming (p-2 → p-1, citing the
transcript turn `headless-seed-6000:meeting-0:turn-2`). `combined_accounts`
recorded 3 ballots over its 1 completed unit, all SKIP, none carrying a
citation. No support or relevance verdict was computed for any of them.

## Meeting-internal defaults, charged failed attempts and transport attempts, per arm

| Arm | Units completed | Defaulted turns | Defaulted votes | By validation | By deadline | Degraded openings | Units with defaults | Charged failed attempts | Retried calls | Unaccounted attempts | Units with retries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `combined_accounts` | 1 (+1 stopped) | 1 | 0 | 1 | 0 | 0 | 1 | 1 (4,541 in / 1,455 out) | 0 | 0 | 0 |

The one default is the schema-invalid turn described above. Its recorded
message is `opt_in turn (turn 2) defaulted (validation); p-2 submitted no turn`,
which matches the instrument's own `_DEFAULTED_TURN_MESSAGE` pattern with
trigger `validation`, so the "a default this instrument cannot classify is a
stop" condition did not fire. The instrument's own `count_defaulted_attempts`
never ran on it — it runs when a meeting resolves, and this meeting aborted — so
the classification above was recomputed from the archived row with the same two
regexes the module uses, and
[usage-reconciliation.json](usage-reconciliation.json) records it.

**No transport retry fired.** No attempt on this run came back with no
completion at all: the provider answered every one of the 22 sends, no row
carries the `no-completion-returned` marker, and `retried_calls`,
`unaccounted_attempts` and `attempts_by_trigger` are empty on both arms. The
bound PR #450 added (4 attempts, 180 s per attempt) was in force and never
engaged — the empty-completion class that stopped the run of 2026-09-13 did not
recur. Verify the absence with:

```sh
grep -c "no-completion-returned" audits/deduction-candidate/run-2026-09-13-3/*.jsonl
```

which prints `:0` for all four files.

**What this run did exercise live, for the first time, is PR #447.** Two of its
three parts, and it matters which:

1. **The post-unit spend reconciliation ran live and passed** on all three
   completed units. No unit stopped on `SPEND_RECONCILIATION`, and no budget was
   found past its cap by `BUDGET_CAP_READBACK`. That path is now proved against
   a real provider rather than only offline.
2. **The client-side capture of a billed-and-refused call fired live.** The
   4,541 / 1,455 attempt is exactly the class #447 was written for — a payload a
   real provider validated and refused before the recording client could log it
   — and it reached the arm's partial accounting, which is why the stop line
   reports `combined_accounts: 10 calls, 38240 in, 6172 out` against nine
   resolved rows. The 2026-09-10 defect would have lost those 4,541 / 1,455
   tokens entirely.
3. **`_reconcile_recorded_spend`'s charged-failed-attempt branch is still
   unproved live.** The only unit that carried a charged failed attempt is the
   one that aborted, and the reconciliation runs only after a meeting resolves.
   The comparison it makes was never performed on a unit containing one.

## Usage against every authorized limit

| Arm | Attempts | of which resolved | of which charged-and-refused | Input tokens | Output tokens | `cost_usd` |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 12 | 12 | 0 | 44,664 | 3,028 | 0.0 |
| `combined_accounts` | 10 | 9 | 1 | 38,240 | 6,172 | 0.0 |
| **Run total** | **22** | **21** | **1** | **82,904** | **9,200** | **0.0** |

| Limit | Authorized | Actual | Used | Fired? |
| --- | --- | --- | --- | --- |
| Run input tokens | 2,400,000 | 82,904 | 3.45% | no |
| Run output tokens | 200,000 | 9,200 | 4.60% | no |
| Per-unit input tokens | 45,000 | 24,282 (largest unit) | 54.0% | no |
| **Per-unit output tokens** | **4,000** | **3,116 charged + a 1,024 reservation** | **103.5% at the pre-flight** | **YES — this is the stop** |
| Elapsed wall | 8 h (28,800 s) | 369.1 s | 1.28% | no |
| Model work | 6 h (21,600 s) | 368.8 s | 1.71% | no |
| Per-call output cap | 2,048 turn / 1,024 vote | largest output 1,455 (a turn, the refused one); largest resolved 1,045 | 71.0% of the turn cap | no |
| Transport attempts | 4 per call, 180 s each | 1 attempt per call, 22 of 22 | 25% of the bound | no |
| Dollar | $0.00 marginal | $0.00 | — | not an enforcement mechanism on this provider |

**Marginal cost: $0.00.** Every recorded `cost_usd` on this run is exactly 0.0,
by construction rather than by measurement: the Featherless provider's zero
pre-flight rate disables `BudgetedLLMClient`'s USD dimension
(`llm/featherless_client.py:243-244`, `llm/budgeted_client.py:118-126`). The
resources consumed were subscription capacity and 369.1 seconds of wall on one
worker.

**Pace.** 368.8 s of model work over 22 attempts is **16.8 s per attempt**,
between the 11.7 s of 2026-09-10 and the 26.6 s of 2026-09-13's second attempt.
At that pace 600 attempts would be about 2 h 48 m of model work against the
authorized 6 h, so the widened wall window this run was authorized under was
ample and the wall was never the binding constraint. The token budget was.

## Every stop condition, checked

`STOP_RULE`'s enumerated conditions, each against what the run recorded:

| Stop condition | Fired? | Evidence |
| --- | --- | --- |
| **Token budget exhausted, per-unit level** | **YES** | the pre-flight above: 3,116 + 1,024 > 4,000 output on `combined_accounts` seed 6001 |
| Token budget exhausted, run level | no | 3.45% / 4.60% of the run ceilings |
| Elapsed wall deadline | no | 369.1 s of 28,800 s |
| Model-work window | no | 368.8 s of 21,600 s; no attempt was cut off in flight |
| A response that reached its output cap (truncation) | no | largest output 1,455 against a 2,048 turn cap; largest ballot 223 against 1,024 |
| A held-out digest or skip differing from the frozen manifest | no | `verify_frozen_set` passed before any client existed: 50 accepted prefixes, 9 skips, freeze record sha256 `7ded1990…6ecd37` |
| A rendered prompt or regenerated prefix matching `body-p-\d+-\d+` | no | asserted over all 50 regenerated prefixes before the run; the rendered prompts carry only the v2 handles `body-p-1` and `body-p-4` (see below) |
| A unit whose recorded observation clock or experiment config is not the arm's | no | every replay records `temporal_observation_version` 2; the two `repaired_clock` units record both candidate versions null, the two `combined_accounts` units record `public_account_version` 1 and `attributed_testimony_version` 1 |
| A recorded meeting default the instrument cannot classify | no | the one recorded default matches `_DEFAULTED_TURN_MESSAGE` with trigger `validation` |
| A call that came back with no completion at all (transport) | no | 22 attempts, 22 completions; no `no-completion-returned` marker anywhere |
| The recorded-spend reconciliation (PR #447) | no | ran on all three completed units and passed |
| The post-unit budget cap read-back (`BUDGET_CAP_READBACK`) | no | ran on all three completed units and passed |

No stop condition reads an outcome, and none did here. The run stopped on a
resource ceiling at a fixed point in a fixed sample, with no interim analysis
and no optional stopping.

**On the body-handle check.** Scanning the whole archive for `body-p-\d+-\d+`
returns four matches and none of them is on a surface the stop condition covers:
each is the engine's own entity id inside a tick row's `actions` field, the raw
record of the scripted report step. What the condition covers is the regenerated
prefixes, the rendered prompts and the emitted report, and all of those are
clean — every prompt the model was handed carries only `body-p-1` or
`body-p-4`, which is what temporal v2 renders by construction. Reproduce both
halves with:

```sh
.venv/bin/python -c "
import json, re
from pathlib import Path
D = Path('audits/deduction-candidate/run-2026-09-13-3')
for p in sorted(D.glob('*.jsonl')):
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    m = [r for r in rows if r['kind'].startswith('meeting')][0]
    legacy = {(r['kind'], h) for r in rows for h in re.findall(r'body-p-\d+-\d+', json.dumps(r))}
    prompts = {h for c in m['llm_calls'] for h in re.findall(r'body-p-\d+(?:-\d+)?', c['prompt'] or '')}
    print(p.name, 'legacy handles:', sorted(legacy), '| handles in prompts:', sorted(prompts))
"
```

```
combined_accounts-seed-6000.jsonl legacy handles: [('tick', 'body-p-4-4')] | handles in prompts: ['body-p-4']
combined_accounts-seed-6001.jsonl legacy handles: [('tick', 'body-p-1-4')] | handles in prompts: ['body-p-1']
repaired_clock-seed-6000.jsonl legacy handles: [('tick', 'body-p-4-4')] | handles in prompts: ['body-p-4']
repaired_clock-seed-6001.jsonl legacy handles: [('tick', 'body-p-1-4')] | handles in prompts: ['body-p-1']
```

**On the source-identity check.** The two arms render different template
families by design and each carried exactly one marker set throughout, so no
source changed mid-run: `repaired_clock` recorded
`accusation_round.qwen3_6_27b.v5` / `crewmate_report.qwen3_6_27b.v5` /
`impostor_report.qwen3_6_27b.v5` / `vote_ballot.qwen3_6_27b.v5`, and
`combined_accounts` the `…_accounts.qwen3_6_27b.v2.accounts1.attributed1`
family. Both are recorded per unit in
[usage-reconciliation.json](usage-reconciliation.json).

## What this archive contains

| File | What it is |
| --- | --- |
| [stop.log](stop.log) | the run's stdout and stderr, ending in the instrument's own partial-state record |
| `repaired_clock-seed-6000.jsonl`, `combined_accounts-seed-6000.jsonl`, `repaired_clock-seed-6001.jsonl` | the three completed units' replays: ticks, the resolved meeting with its transcript, ballots, verdict and every recorded call with its rendered prompt |
| `combined_accounts-seed-6001.jsonl` | the stopped unit's replay: ticks, the `meeting_aborted` row with its three resolved calls, the charged-and-refused attempt and the default it produced |
| [usage-reconciliation.json](usage-reconciliation.json) | per-unit and per-arm usage, defaults, charged failed attempts, transport attempts and every authorized limit with the fraction used, derived from the files above |
| [rendered-prefixes.json](rendered-prefixes.json) | the two prefixes this run rendered — seeds 6000 and 6001 — with their frozen digests |

Nothing was left out: the whole archive is about 0.4 MB, far inside the size at
which the run's card would have made me choose. No report JSON exists, for the
reason given above.

## Held-out status

**Seeds 6000 and 6001 of the third band are revealed by this archive. Seeds
6002–6058 were never rendered to the model.**

The instrument serialized no prefix during the run — it never does, and
`assert_report_holds_no_prefix_bytes` refuses a report that carries one. What
this directory publishes is the four replays, whose meeting rows carry the
prompts those two prefixes rendered under each arm and whose tick rows carry the
scripted steps, plus `rendered-prefixes.json`, which is the two rendered
prefixes regenerated and written out AFTER the run. Both seeds were run, so
neither is held out any more, and the manifest's rule is that the prefixes are
archived with the results once that is true.

The other 48 accepted prefixes were regenerated in process, checked against the
frozen digests and then discarded unrendered. **They are deliberately NOT
archived here**, which is the decision the first two runners made and the same
reasoning: the manifest archives prefixes "when they are no longer held out",
and these 48 still are. Committing them would convert the rest of the band to
development data to no purpose. The runner opened, printed and reasoned about no
prefix before the run.

Three consequences the owner's next decision has to carry:

1. **This run did not convert the band's status.** The freeze manifest still
   reads `held_out`, and flipping it belongs to the decision that acts on this
   record, not to the runner. If this result informs a fix — and the per-unit
   output ceiling is exactly the kind of finding that would — the manifest's
   Roles section requires that flip and a new band under a new card.
2. **A re-run on this same band would not be a clean 50-unit held-out sample**,
   because two of its seeds are now public. Any future confirmation claim needs
   a new band frozen under a new card, by a preparer who has not read this
   document.
3. **Four seeds of held-out margin are now gone across three runs** — seed 3000
   of the first band, seed 5000 of the second, and seeds 6000 and 6001 of the
   third. This attempt is the first to reach a second seed, and it spent two.

## Compared with the two earlier attempts

| | 2026-09-10 (PR #445, closed) | 2026-09-13 (PR #448, closed) | 2026-09-13 (this run) |
| --- | --- | --- | --- |
| Band | 3000-3999 (now development) | 5000-5999 (now development) | 6000-6999 |
| Units completed | 1 of 100 | 0 of 100 | **3 of 100** |
| Paired units | 0 of 50 | 0 of 50 | **1 of 50** |
| Meetings that reached a verdict | 0 | 0 | **3** |
| Arms reached | both (unit 2 stopped) | reference only | both |
| Attempts | 12 resolved | 4 resolved, 1 failed | **22 resolved, 1 of them charged-and-refused** |
| Tokens | 36,003 in / 3,401 out | 13,182 in / 993 out | 82,904 in / 9,200 out |
| Elapsed / model work | 159.7 s / 140.2 s | 110.9 s / 106.3 s | 369.1 s / 368.8 s |
| Seconds per attempt | 11.7 | 26.6 | 16.8 |
| Cause | the instrument's spend reconciliation could not see a paid call | the provider returned a completion with no `choices` | the per-unit output budget, crossed at a ballot pre-flight |
| Whose defect | the instrument's — repaired by PR #447 | the provider's — absorbed by PR #450's bounded retry | **neither: an authorized limit, reached** |
| Seeds rendered | 3000 | 5000 | 6000, 6001 |
| Marginal cost | $0.00 | $0.00 | $0.00 |

The first run found a bug in this repository and it was fixed. The second found
a provider behaviour and it was absorbed. This one found neither: every gate it
reached was green, both repairs held — PR #447's client-side capture fired live
and its reconciliation passed on every completed unit, and PR #450's retry bound
was in force and was never needed — and the run stopped on a number the owner
authorized. What it establishes is that the evaluation's obstacle has moved from
the instrument and the endpoint to the **budget**: the per-unit output ceiling of
4,000 tokens is not sized for the candidate arm on this model, and on this
sample the run-level output ceiling of 200,000 would not have covered 50 paired
seeds either.

## Verdict

In the preregistration's own vocabulary — advance to an explicitly scoped
adopting review / revise and evaluate a new version / reject / gather more
evidence under a new authorized manifest — this run reaches **none of the
four**, because none of them is a statement a one-paired-unit sample supports.
The only route forward it identifies is **more evidence under a new authorized
manifest**, and the preregistration is explicit that "more evidence is not an
automatic spending authorization": that is an owner decision on a new card, with
its own limits.

**A result is a measurement and never an adoption.** This one is not a
measurement of deduction: `combined_accounts` neither advanced nor was rejected,
and this document changes no default, no experiment switch and no baseline. What
it does measure is the two arms' token appetite under the authorized
configuration, and that measurement is what a fourth authorization would have to
price:

- **The per-unit output budget of 4,000 is the binding constraint.** A clean
  candidate unit cost 3,056 and cleared its last pre-flight by 28 tokens. One
  schema-invalid turn — the class the manifest accepts at about 1 in 50 calls —
  cost another 1,455 and was enough to end the run. Any figure chosen has to
  cover the candidate arm's own output plus one accepted default plus the full
  1,024 reservation the vote pre-flight makes.
- **The run-level output budget of 200,000 would also bind.** About 4,570 output
  tokens per paired seed on this sample gives roughly 43 of the 50 seeds.
- **The input ceilings and both wall clocks have large margins.** 3.45% and
  4.60% of the run token ceilings, 1.28% and 1.71% of the two clocks, at 16.8 s
  per attempt; 600 attempts project to about 2 h 48 m of model work against 6 h.
- **A fourth run needs a fourth band**, because two of this one's seeds are now
  public.
- **Raising a number the owner authorized is not the runner's call.** This
  document records the ceiling that was reached and what the measured rates say
  about it; nothing here widens anything, and the stop authorized no retry.
