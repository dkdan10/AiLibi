# Why three live runs of the fresh-model deduction instrument stopped

Diagnosis of 2026-09-13, written by the coordinator from four independent
read-only investigations, one synthesis and three adversarial refutations of
that synthesis. Every figure below was recomputed by at least two of those
sessions from the archives on the closed pull requests' branches
(`work/fresh-deduction-run`, `work/fresh-deduction-run-2`,
`work/fresh-deduction-run-3`) and from the tree at `c461c9d0`.

## The three stops

| Attempt | Stopped at | Proximate cause | Spend |
| --- | --- | --- | --- |
| 1 (2026-09-10, PR #445) | unit 1 of 100 | the post-unit spend reconciliation summed only the meeting's recorded calls; a billed turn the schema refused (861 output tokens) rode the surfaced default | 12 attempts, 36,003 in / 3,401 out |
| 2 (2026-09-13, PR #448) | call 5 | the provider returned a 2xx body with no `choices`; the manifest made a transport failure a stop with no retry | 5 attempts, 13,182 in / 993 out |
| 3 (2026-09-13, PR #451) | unit 4 of 100 | the per-unit output ceiling (4,000) was cleared at 3,116 charged when the next ballot's pre-flight reserved its full 1,024 cap; the charged 3,116 included a billed turn the schema refused (1,455) | 22 attempts, 82,904 in / 9,200 out |

All at $0.00 marginal. Pooled pace 15.78 s per attempt over 39 attempts, so
600 sequential calls need about 2.6 h against 6 h of model work. The wall
clocks, the per-call caps, cost, provenance and the frozen set were never the
cause. The two merged repairs (#447 accounting, #450 transport retry) held
live in attempt 3 and are not implicated in it.

## Root cause

The instrument was sized and enforced in two different units of account, and
the only place it ever met the real provider was the held-out run itself.

1. **Sized on charged spend, enforced on reserved spend.** The per-unit output
   ceiling was sized as `600 x 220` charged tokens from a 9p2i corpus of a
   prompt family the candidate arm does not use
   (`tasks/owner-decisions-2026-09-07.md:192`,
   `audits/deduction-candidate/execution-manifest.md:387`). It is enforced by a
   pre-flight that reserves the full per-call cap before every call
   (`llm/budgeted_client.py:259`). One unit's reservation schedule is
   `3 x 2,048 + 3 x 1,024 = 9,216` against a 4,000 ceiling: the instrument
   authorized six legal, untruncated calls it could not pay for. Attempt 3
   needed a ceiling of about 4,314 (3,116 charged plus the 1,024 reservation
   plus the ballot's measured mean); the stop was manufactured by the
   reservation arithmetic, not by spend. This mismatch is static and could
   have been refused at startup without a provider.
2. **The candidate arm's prompt asks for a shape its schema refuses.** The
   accounts rules template tells the model to emit
   `{"type":"whereabouts",...}` items (`agents/strategic/prompts/qwen3_6_27b/_account_rules.j2:9`)
   while `MeetingTurn.claims` admits only `alibi`, `accusation` and
   `corroboration` (`meetings/schemas.py:373-388,552-556`). Two of the
   candidate arm's turns across two runs were billed and refused on exactly
   that union tag (861 and 1,455 output tokens); zero refusals in 23
   reference-arm attempts. The same arm emits 617 output tokens per call
   against the reference arm's 252 — the prompt over-generates and
   off-schema, and both the refusals and the output blow-up land on the arm
   the design is trying to measure.
3. **No pre-run surface could observe either.** `DryRunProvider` derives usage
   from the length of the payload it serialises (66 output tokens per call,
   identical on both arms, 396 per unit, 9.9% of the ceiling); the manifest's
   pre-run headroom check covers input only
   (`execution-manifest.md:852-859`); no test plants a realistic per-call
   output distribution across a six-call unit; and #437 barred every live call
   except the confirmation run itself
   (`tasks/work/fresh-deduction-authorization.md:159-160`). Each attempt
   therefore discovered one provider-facing property live and paid a held-out
   band for it.

Attempts 1 and 2 are the same story one level down: attempt 1 was an internal
accounting seam an amendment did not reach (reproducible offline; nobody wrote
the test), attempt 2 was the no-retry policy meeting a rare provider fault.
Neither is a defect of the model or of the design being measured.

## What the run would need if it ran today

Measured on the four archived live units: reference units charged 1,092 /
1,601 / 1,427 output; the clean candidate unit 3,056; the stopped one 3,116
over four of six calls. Input peaked at 24,282 (54% of 45,000). Projected for
50 paired seeds: run output 202,792 to 221,467 (101% to 111% of 200,000), run
input 2.07 M to 2.34 M (86% to 98% of 2.4 M). Two of the four token ceilings
would have stopped a complete run near its end even with the per-unit ceiling
fixed. On a flat-rate provider with zero pre-flight rates these ceilings buy
no money; they are a stop rule, and should be sized as an anomaly detector at
about three times the measured maximum rather than as a budget at 1.3 times a
projection.

## Fix plan

Two cards need no owner decision and are opened with this diagnosis:

- [Instrument realism](work/fresh-deduction-instrument-realism.md): a startup
  feasibility gate that refuses any ceiling below the reservation schedule the
  same run will make; a usage-replaying provider double keyed by arm and call
  type from the 36 archived resolved calls plus the refusal and empty-body
  modes, so the 100-unit rehearsal exercises the output dimension and the
  reservation schedule; coverage of the two empty-response markers the retry
  classifier still misses (`llm/featherless_client.py:844,850`); a per-unit
  checkpoint and an outcome-blind resume mechanism, built but not yet
  authorized for live use.
- [Accounts turn schema alignment](work/accounts-turn-schema-alignment.md):
  make the accounts prompt and the turn schema agree on `whereabouts`, with
  the version-bump cascade, on the default-OFF candidate path only.

Three decisions are the owner's, because they change spending or the
preregistered protocol:

1. **A bounded live calibration on development inputs** before any fourth
   held-out run: about 5 paired seeds regenerated from the converted 3000-3999
   band (development data by rule), about 60 calls, under the existing
   per-call caps, whose only outputs are the measured per-arm token profile
   and refusal rate. This lifts the "no pilot" clause of #437 for
   development inputs only. It is the one step that closes the root cause for
   provider behaviour not yet seen.
2. **A resumption clause**: a run stopped by an environmental cause (transport
   exhaustion, credential, crash) may resume at the next unrendered seed under
   the same manifest and the same budgets, since no stop condition reads an
   outcome; a stop caused by a limit or by anything that invalidates the
   design still ends the run.
3. **Re-sized ceilings** for the fourth authorization, from the calibration
   in decision 1 rather than from these four units: provisionally per-unit
   60,000 in / 12,000 out, run 3,600,000 in / 350,000 out, wall unchanged at
   6 h in 8 h, and `BUDGET_SIZING_ARM` set to the arm the measurement shows is
   larger.

Not adopted from the synthesis, after refutation: a per-pair quarantine bound
(it would drop candidate-arm units preferentially and re-scale the frozen
constants), a change to the shared budgeted client's reservation policy (it
would alter every recorded campaign), and a per-seed conversion rule (the
set-level rule stands until the owner changes it).
