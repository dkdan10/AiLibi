# Make the fresh-model deduction instrument's rehearsal see what the provider does

**Status:** ready

## Outcome

Before any live call, the instrument can refuse limits it cannot honour, and
its rehearsal exercises the dimension that has actually bound: a usage
profile keyed by arm and call type taken from real archived calls, including
the two provider behaviours that stopped earlier attempts. A run stopped by an
environmental cause can be resumed from a per-unit checkpoint, outcome-blind,
once the owner authorizes that clause; the mechanism exists and is proved.

## Evidence

[The diagnosis of 2026-09-13](../diagnosis-2026-09-13-live-run-stops.md)
records the three stops and the root cause: the per-unit output ceiling was
sized on charged spend and enforced on reserved spend
(`llm/budgeted_client.py:259` reserves the full per-call cap; one unit's
schedule is `3 x 2,048 + 3 x 1,024 = 9,216` against a 4,000 ceiling), and no
pre-run surface could show it: `DryRunProvider` reports 66 output tokens per
call on both arms (`experiments/fresh_deduction_instrument.py`, its usage is
derived from the serialised payload's length), the manifest's headroom check
covers input only (`audits/deduction-candidate/execution-manifest.md:852-859`),
and the only mention of the output ceilings in the test module is a
constant-value assertion. The retry classifier's empty-completion markers
cover two of the four fail-loud shapes the client raises; "carried no usage
block" and "usage block omitted prompt_tokens / completion_tokens"
(`llm/featherless_client.py:844,850`) still re-raise bare, uncharged and
unretried. The 36 resolved live calls archived on the three run branches carry
real usage per call, and the archived refusals carry usage on a schema-refused
payload. No checkpoint or resume path exists although the decision memo named
a per-unit checkpoint as owed (`tasks/owner-decisions-2026-09-07.md`, B.4).

## Acceptance

- [ ] `assert_ready_for_a_live_run` gains a feasibility gate, pure arithmetic
  over module constants: it refuses a per-unit output ceiling below the
  reservation schedule one unit makes (turns x turn cap + living voters x vote
  cap, with the policy stated in the manifest) and run-level ceilings below the
  calibrated per-unit figure times the unit count; planted with attempt 3's
  numbers (4,000 against 9,216) it goes red, with feasible numbers green, and
  it runs before any credential or client exists.
- [ ] A usage-replaying provider double, keyed by (arm, call type), seeded
  deterministically, samples response length and usage from a committed
  profile built from the 36 archived resolved calls on the run branches
  (recorded as aggregate rows: arm, call type, input tokens, output tokens;
  never a prompt or a prefix), with modes for a billed-and-refused payload
  carrying usage, an empty body, a no-usage body and a transport error. Under
  today's authorized limits the 100-unit rehearsal reproduces attempt 3's stop
  string; a call-type-blind sampler is shown to manufacture a false
  truncation, which is the regression the keying prevents.
- [ ] The retry classifier covers every fail-loud empty-response shape the
  authorized client raises, enumerated from the client's own messages rather
  than typed, with a planted test per shape; an uncovered shape fails the
  enumeration test.
- [ ] A per-unit checkpoint is written after every completed paired seed
  (arm results, usage, attempts, the manifest digest, the frozen-set digest
  and the instrument source digests), and `--resume <checkpoint>` continues
  at the next unrendered seed of the ascending list under the same manifest
  with the budgets carried; a resumed rehearsal produces a report identical to
  the uninterrupted one, and a planted change to any arm-surface byte, the
  manifest or the frozen set is refused. The live gate keeps refusing a resume
  until the manifest carries the owner's resumption clause (a test proves the
  refusal).
- [ ] The manifest's "How each limit is enforced" section states the units of
  account explicitly (reserved versus charged), the reservation schedule per
  unit, and that the rehearsal's headroom check now covers output; a dated
  section "Amendments after the diagnosis of 2026-09-13" records the change.
  The frozen analysis strings are byte-identical (a test asserts it).
- [ ] Every new gate has a planted failure proving it detects the claimed
  defect; the fake-provider and replay-double rehearsals run at $0 and Results
  records aggregate counts only.

## Constraints

No live provider call. No change to `llm/budgeted_client.py`'s reservation
policy (it serves every recorded campaign); the per-unit policy is stated and
gated, not altered. The primary outcome, decision rule, minimum actionable
effect and tradeoff bound do not change. Do not edit
`experiments/held_out_prefixes.py`. The usage profile carries token counts
only; no prompt, prefix or response text from the archives is committed. The
resume clause is not enabled for live runs by this card; the owner's
authorization card enables it. Any `audits/` byte change recomputes the
`docs/artifacts.md` audits row.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`tests/experiments/burned_call_double.py` (extend) or a sibling replay double,
a committed usage profile under `tests/experiments/` or `experiments/`
(aggregate rows only), `audits/deduction-candidate/execution-manifest.md`,
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived
inventory sentence, this card. Delivered on
`work/fresh-deduction-instrument-realism` and one pull request into `main`.

## Record impact

Amends the execution manifest (an `audits/` document) with a dated section and
an enforcement clarification; adds a committed aggregate usage profile; no
recording, report, DTO or weight byte moves; no experiment becomes ON; no
adopting record is created; the three run archives are not touched.

## Validation

`uv run pytest tests/experiments -q` (fake and replay doubles only), then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.
Do not run the live evaluation as a check.
