# Fresh-model deduction evaluation — run of 2026-09-10

**The run stopped after 1 of 100 units. No paired unit completed, so the
primary outcome was not measured and the decision rule is not evaluable.** The
stop authorizes no retry and no widening of any limit. Nothing here is an
adoption, and nothing here is a measurement of the candidate either.

This directory is the partial evidence and the unresolved accounting that
[the execution manifest](../execution-manifest.md)'s stop rule requires a
stopped run to retain.

## The design that was attempted

One meeting per frozen held-out prefix under two paired arms — the reference
`repaired_clock` (`format_version=2`, `evidence_reasoning_version=2`) and the
candidate `combined_accounts` (the reference plus `public_account_version=1`
and `attributed_testimony_version=1`) — over the 50 proof-free scripted
prefixes frozen by the owner's merge of #438 as `23a23c2d`, run sequentially,
both arms per seed before the next seed, on Featherless `Qwen/Qwen3.6-27B`
under the limits the owner authorized by merging #437 as `0f49d8e6`. 50
prefixes x 2 arms = 100 units, about 600 model calls, scored on
`supported_correct_ejection` with the two-sided exact McNemar test over the
discordant pairs. The run reached unit 2 of 100.

## What ran

| Unit | Arm | Seed | Result |
| --- | --- | --- | --- |
| 1 | `repaired_clock` | 3000 | completed; meeting resolved `SKIPPED`, no ejection |
| 2 | `combined_accounts` | 3000 | **stopped** during the post-unit spend reconciliation |

The invocation was exactly the one
[the manifest documents](../execution-manifest.md) in its "The live gate"
section — the same module, provider, manifest path and runner flag, with
`--output-dir` and `--json` pointing outside the repository — run once from the
worktree root at `5281e297`. It is not reproduced here: no committed file
outside the manifest and the instrument may carry the runner flag, and
`tests/experiments/test_fresh_deduction_instrument.py::TestLiveGate::test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag`
scans every tracked file to keep that true.

**No report JSON exists.** `main()` writes the report only after
`run_instrument` returns, and it raised, so `--json` produced no file. The
instrument's own partial-state record is [stop.log](stop.log); the two per-unit
replays are the archived per-unit records.

## The stop

Quoted from [stop.log](stop.log):

```
InstrumentError: seed 3000 on arm combined_accounts: the recorded spend
(13263 in / 1448 out / 0.0 USD) differs from the enforced budget
(15491 in / 2309 out / 0.0 USD)
```

```
InstrumentAborted: ...; 1/100 units completed, 159.7s elapsed, 140.2s model
work; combined_accounts: 5 calls, 13263 in, 1448 out, repaired_clock: 6 calls,
20512 in, 1092 out
```

### What actually happened, from the archived rows

Reproduce every figure in this section with:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
D = Path('audits/deduction-candidate/run-2026-09-10')
for arm in ('repaired_clock', 'combined_accounts'):
    rows = [json.loads(l) for l in (D / f'{arm}-seed-3000.jsonl').read_text().splitlines() if l.strip()]
    meeting = next(r for r in rows if r['kind'] == 'meeting')
    failed = [r for r in rows if r['kind'] == 'failed_call']
    paid = [r for r in failed if r['input_tokens'] or r['output_tokens']]
    mi = sum(c['input_tokens'] for c in meeting['llm_calls'])
    mo = sum(c['output_tokens'] for c in meeting['llm_calls'])
    fi = sum(r['input_tokens'] for r in failed)
    fo = sum(r['output_tokens'] for r in failed)
    print(arm, '| meeting rows', len(meeting['llm_calls']), f'{mi} in / {mo} out',
          '| failed rows', len(failed), f'({len(paid)} paid) {fi} in / {fo} out',
          '| true spend', len(meeting['llm_calls']) + len(paid), f'{mi+fi} in / {mo+fo} out',
          '| outcome', meeting['outcome'], '| ejected', meeting['ejected_player_id'])
"
```

```
repaired_clock | meeting rows 6 20512 in / 1092 out | failed rows 0 (0 paid) 0 in / 0 out | true spend 6 20512 in / 1092 out | outcome SKIPPED | ejected None
combined_accounts | meeting rows 5 13263 in / 1448 out | failed rows 3 (1 paid) 2228 in / 861 out | true spend 6 15491 in / 2309 out | outcome SKIPPED | ejected None
```

The candidate arm's unit carries three `failed_call` rows. One is a **paid**
call — `call-2`, model `Qwen/Qwen3.6-27B`, 2,228 input / 861 output tokens —
whose payload failed `MeetingTurn` schema validation:

```
9 validation errors for MeetingTurn
claims.0
  Input tag 'whereabouts' found using 'type' does not match any of the
  expected tags: 'alibi', 'accusation', 'corroboration'
```

The other two are the shipped fail-soft's zero-usage markers, both carrying the
`validation` trigger: `reply turn (turn 1) defaulted (validation); p-3 submitted
no turn` and `opt_in turn (turn 2) defaulted (validation); p-2 submitted no
turn`. Only one of the two can be attributed to the paid failure above — see
"Meeting-internal defaults" below.

The arithmetic closes exactly. 13,263 + 2,228 = 15,491 and 1,448 + 861 = 2,309:
the whole of the discrepancy is that one paid call. `whereabouts` is a valid
*observation* type (`meetings/schemas.py:208`) that the prompt set asks for by
name (`agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:288`,
`crewmate_report.j2:154`), and the model placed it in `claims` — which admits
only `alibi`, `accusation` and `corroboration` — instead of `observations`.
This is the schema-validation class the manifest anticipated at about 1 in 50
calls; it arrived inside the run's first 12 paid calls. One occurrence
establishes no rate.

### Why a counted default became a stop

Four components saw that call differently:

| Component | Saw the paid failure? | Consequence |
| --- | --- | --- |
| `GameBudget` (via `BudgetedLLMClient`) | **yes** — `llm/budgeted_client.py:328-343` charges usage riding on the exception | budget snapshot 15,491 / 2,309 |
| `FailedCallReplayEntry` row | **yes** — `meetings/manager.py:1689-1716` records it with its usage | `failed_call` row 2,228 / 861 |
| `MeetingReplayEntry.llm_calls` | no — it carries successful calls only | meeting rows 13,263 / 1,448 |
| `_InstrumentClient._calls` | no — the exception propagates out of `self._inner.complete(...)` and only `TimeoutError` is caught there | partial accounting 5 calls |

`_reconcile_recorded_spend` (`experiments/fresh_deduction_instrument.py:1916-1935`)
compares the third against the first, so a paid schema-validation failure makes
them differ by construction and stops the run.

The meeting layer documents this property in the very handler that produced the
row (`meetings/manager.py:1712-1716`):

> A REAL provider validates internally and raises *before* the recording client
> logs the call, so its spend is lost from `llm_calls` unless we carry it on the
> surfaced default.

So "the recorded spend on the replay row equals the enforced budget" is a
property of the fake provider, not of the system. On a real provider it is false
by design whenever a payload fails validation, and the instrument reconciles
against it anyway.

That is a contradiction inside the manifest, not a provider fault. The
enforcement section says of the token budget that "the RECORDED per-call spend
on the replay row is reconciled against the enforced budget snapshot, and a
difference is a stop". The amended `STOP_RULE` says the opposite about this
class: "A meeting-internal default is NOT itself a stop … a fixed 50-unit
paired sample cannot be abandoned for a substitution the engine is designed to
make." `STOP_RULE`'s own enumeration of stop conditions does not list the spend
reconciliation at all. The 2026-09-09 amendment (`bfd5696b`) that relaxed the
stop rule reached `STOP_RULE` and `count_defaulted_attempts`; it did not reach
`_reconcile_recorded_spend`.

It survived 152 instrument tests and six review rounds because it cannot occur
offline. Every planted default in
`tests/experiments/test_fresh_deduction_instrument.py` carries
`input_tokens=0, output_tokens=0` (the one constructed `FailedCallReplayEntry`
is at `:1494`), and the fake provider always returns a schema-valid payload, so
no fixture ever produced a call that was paid for and absent from the meeting
row. `grep -c reconcil tests/experiments/test_fresh_deduction_instrument.py`
returns 0.

A second consequence is worth recording separately: because
`_InstrumentClient` did not capture the failed attempt either, the instrument's
own partial accounting **understates** the run's real token spend by exactly
that call — 5 calls / 13,263 / 1,448 reported against 6 calls / 15,491 / 2,309
actually spent. The manifest promises partial accounting that carries "the
stopped unit's spent-but-unusable calls"; for a paid schema-validation failure
it does not.

## Primary outcome, discordant pairs and the decision rule

**Not measured.** The primary outcome is a per-seed paired binary and no seed
completed both arms, so there are zero paired units against the 50 the design
requires.

| Quantity | Value |
| --- | --- |
| Paired units completed | 0 of 50 |
| Units completed | 1 of 100 (decision coverage 1%) |
| `repaired_clock` supported-correct ejections | 0, on 1 unit that resolved `SKIPPED` |
| `combined_accounts` supported-correct ejections | not computed; its unit stopped before grading |
| Discordant pairs `b` | not evaluable (no paired unit) |
| Discordant pairs `c` | not evaluable (no paired unit) |

No grader ran. Grading is a pure function over finished `UnitRecord`s that
`run_instrument` calls only after the last unit, and it never reached that
point.

`exact_mcnemar_p` on zero discordant pairs returns 1.0, and that value is an
artifact of an empty sample rather than a result:

```sh
.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); \
from paired_stats import exact_mcnemar_p as p; print(p(0, 0))"
```

```
1.0
```

The docstring says so itself: "With no discordant pairs at all there is no
evidence either way and p is 1.0." It must not be read as a null result.

The three clauses of `DECISION_RULE`, each evaluated:

| Clause | Bar | State |
| --- | --- | --- |
| Two-sided exact McNemar p over the discordant pairs | below 0.05 | **not evaluable** — no paired unit; the 1.0 above is the empty-sample constant |
| Net paired difference `b - c` | at least 10 of 50 | **not evaluable** — `b` and `c` are undefined on 0 paired units |
| Candidate's net increase in wrongful crew ejections | no larger than `b - c` | **not evaluable** — see the bound below |

**Conjunction: not evaluable.** `combined_accounts` does not advance. It is
also not rejected: a run that produced no outcome refutes nothing. Under
`DECISION_RULE`'s own wording, "any other result is inconclusive, and
inconclusive is not success" — and this is weaker than inconclusive, because
inconclusive presumes a sample.

**Wrongful-ejection bound.** `WRONGFUL_EJECTION_TRADEOFF` counts a unit whose
meeting ejected a player whose hidden role is CREWMATE. Zero wrongful
ejections were recorded on either arm, because neither meeting ejected anyone:
both resolved `SKIPPED` with `ejected_player_id` null. On one unit per arm that
is a fact about two meetings, not a bound the candidate cleared — the bound is
defined as a *net increase over 50 paired units* and cannot be computed on
zero.

## Meeting-internal defaults, counted per arm

Counted here from the archived rows, since no report was written. The
instrument classifies a `deadline_default` row by phase and trigger from its
message; both markers below classify, so the "a default this instrument cannot
classify is a stop" condition did not fire.

| Arm | Units | Defaulted turns | Defaulted votes | By validation | By deadline | Degraded openings | Units with defaults |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| `combined_accounts` | 1 (stopped) | 2 | 0 | 2 | 0 | 0 | 1 |

Both markers carry the `validation` trigger, and only one of the two is
attributable to the paid schema failure above: the other turn's call is
recorded on `llm_calls` as a normal success, so the client parsed it and a
later validation stage rejected it. The candidate arm runs one the reference
arm does not — `PublicAccountValidationError`
(`meetings/manager.py:1686`, caught with `ValidationError` at `:1689-1692`) —
but one unit is not enough to attribute it, and this document does not.

What the counts do show is the scale: on the one unit that produced any,
defaults replaced 2 of that meeting's 3 turns. The manifest states that a
defaulted ballot biases the primary outcome upward and that "a run whose arms
differ materially on it is not a clean comparison". One unit establishes no
rate, and this is a cell a resumed run should watch rather than a finding.

## Usage against every authorized limit

Actual spend, including the paid call that the instrument's own accounting
missed:

| Arm | Paid calls | Input tokens | Output tokens | `cost_usd` |
| --- | --- | --- | --- | --- |
| `repaired_clock` | 6 | 20,512 | 1,092 | 0.0 |
| `combined_accounts` | 6 | 15,491 | 2,309 | 0.0 |
| **Run total** | **12** | **36,003** | **3,401** | **0.0** |

| Limit | Authorized | Actual | Used | Fired? |
| --- | --- | --- | --- | --- |
| Run input tokens | 2,400,000 | 36,003 | 1.5% | no |
| Run output tokens | 200,000 | 3,401 | 1.7% | no |
| Per-unit input tokens | 45,000 | 20,512 (`repaired_clock`), 15,491 (`combined_accounts`) | 45.6% / 34.4% | no |
| Per-unit output tokens | 4,000 | 1,092 / 2,309 | 27.3% / 57.7% | no |
| Elapsed wall | 6 h (21,600 s) | 159.7 s | 0.74% | no |
| Model work | 4 h (14,400 s) | 140.2 s | 0.97% | no |
| Per-call output cap | 2,048 turn / 1,024 vote | largest output 861 (a turn) | 42% of its cap | no |
| Dollar | $0.00 marginal | $0.00 | — | not an enforcement mechanism on this provider |

**Marginal cost: $0.00.** Every recorded `cost_usd` on this run is exactly 0.0,
by construction rather than by measurement: the Featherless provider's
zero pre-flight rate disables `BudgetedLLMClient`'s USD dimension
(`llm/featherless_client.py:243-244`, `llm/budgeted_client.py:118-126`). The
resources consumed were subscription capacity and 159.7 seconds of wall on one
worker.

One projection figure is worth keeping, because it is the only thing this run
measured cleanly: 140.2 seconds of model work over 12 paid calls is 11.7 s per
call, against the 12-23 s band the wall deadline was set on. At that rate 600
calls is about 1 h 57 m of model work — comfortably inside the authorized 4 h.
The wall budget was not the binding constraint and, on this evidence, would not
have been.

## Every stop condition, checked

`STOP_RULE`'s enumerated conditions, each against what the run recorded:

| Stop condition | Fired? | Evidence |
| --- | --- | --- |
| Token budget exhausted, per-unit or run level | no | 1.5% / 1.7% of the run ceilings; 45.6% of the largest per-unit ceiling |
| Elapsed wall deadline | no | 159.7 s of 21,600 s |
| Model-work window | no | 140.2 s of 14,400 s |
| A response that reached its output cap (truncation) | no | largest output 861 against a 2,048 turn cap |
| A held-out digest or skip differing from the frozen manifest | no | `verify_frozen_set` passed: 50 prefixes, 8 skips, manifest sha256 `b6a3bdc5b216e1b7b3d6c1eb46e5f416bb23fba77a8087ef025c31819bff1367` |
| A rendered prompt or regenerated prefix matching `body-p-\d+-\d+` | no | asserted over all 50 regenerated prefixes before the run, and over unit 1's rendered prompts; unit 2 stopped before its own prompt assertion |
| A unit whose recorded clock or experiment config is not the arm's | no | `_assert_arm_provenance` passed on both units — it runs before the reconciliation |
| A recorded meeting default the instrument cannot classify | no | both `deadline_default` markers classify by phase and trigger (verified offline against the archived rows) |
| **The recorded-spend reconciliation** | **YES** | the stop above — and this condition is named in the manifest's enforcement section but is **absent from `STOP_RULE`'s enumeration** |

No stop condition reads an outcome, and none did here: the run stopped on
accounting, at a fixed point in a fixed sample, with no interim analysis.

## Held-out status

**Seed 3000 is revealed by this archive. Seeds 3001-3057 were never rendered to
the model.**

The instrument serialized no prefix — it never does, and
`assert_report_holds_no_prefix_bytes` refuses a report that carries one. What
this directory publishes is the two replay files for seed 3000, which carry the
prompts that prefix rendered under both arms. That prefix was run, so it is no
longer held out, and the manifest's rule is that the prefixes are archived with
the results once that is true.

The other 49 accepted prefixes were regenerated in process and checked against
the frozen digests, and then discarded unrendered. The runner opened, printed
and reasoned about no prefix before the run.

Two consequences the owner's next decision has to carry:

1. **This result will inform a fix**, and the manifest's Roles section says a
   held-out result that informs a fix marks the set development — recorded by
   setting the freeze manifest's `status` to `development` — with a new band
   frozen under a new card. **This run did not convert that status**; the freeze
   manifest still reads `held_out` and changing it belongs to the decision that
   acts on this diagnosis, not to the runner.
2. **A re-run on this same band would not be a clean 50-unit held-out sample**,
   because one of its seeds is now public. Any future confirmation claim needs a
   new band frozen under a new card, by a preparer who has not read this
   document.

## Verdict

In the preregistration's own vocabulary — advance to an explicitly scoped
adopting review / revise and evaluate a new version / reject / gather more
evidence under a new authorized manifest — this run reaches **none of the
four**, because none of them is a statement a zero-unit sample supports. The
only route forward it identifies is **more evidence under a new authorized
manifest**, and the preregistration is explicit that "more evidence is not an
automatic spending authorization": that is an owner decision on a new card, with
its own limits.

What this run does establish, at $0.00 and 160 seconds, is a defect in the
instrument rather than anything about the candidate:

- the live path stops on a class the manifest's amended stop rule exempts;
- the stop condition that fired is not in `STOP_RULE`'s enumeration;
- the instrument's partial accounting understates spend for that same class;
- and none of it is reachable offline, which is why 152 tests and six review
  rounds did not find it.

**A result is a measurement and never an adoption.** This one is not even a
measurement: it is an operating record of a stop. `combined_accounts` neither
advanced nor was rejected, and this document changes no default, no experiment
switch and no baseline.
