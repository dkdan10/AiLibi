# Phase-20 adopting record — baseline 7: the four legs, the pre-registered read, the decision executed (Task 20.36)

**Status:** IN PROGRESS. §0 is committed BEFORE the first recorded seed lands, so the actual
wall clock is read against a projection someone else committed to in advance
(`audits/audit-phase-20-smoke.md` §10). Every later section is written from the recorded bytes
and nothing else.

**Reads against:** `audits/audit-phase-20-preregistration.md` §4 (the eight primary bars), §5
(the secondary cells and the ±15-point win-split band), §6 (the decision rule), §7 (the
declared co-intervention), §8 (the abandon criteria), §9 (the record order and the freeze),
§10 (THE RATIFIED DECISION) and §11 (the amendment log);
`audits/audit-phase-20-counterfactual.md` §0, §6, §8 and §9;
`audits/audit-phase-20-smoke.md` §10, §12, §13 and §14;
`audits/audit-phase-18-baseline-6.md` §§0-10 (the record-audit shape this one mirrors).

---

## 0. The pre-record projection, and the actual against it

### 0.1 The projection, committed in advance

Both figures are `audits/audit-phase-20-smoke.md` §10's, re-derived there from measured
tokens rather than assumed, and copied here before the record started. The record is 300
games: `samples/9p2i` 50, `ml_corpus/9p2i` 150, `samples/4p1i` 50, `ml_corpus/4p1i` 50.

| projection | basis | figure |
|---|---|---|
| at the smoke's own game lengths | 142,396 tokens per 9p2i game; the committed 4p1i:9p2i tokens-per-game ratio 0.066; 29.4 M tokens ÷ 368.2 tokens/s | **22.2 h** |
| at baseline-6 game lengths | 176,267 tokens per `samples/9p2i` game; 34.9 M tokens ÷ 368.2 tokens/s | **26.3 h** |

The measured operating constants behind both: 368.2 aggregate tokens per second at **two**
Featherless seed workers (184.1 per worker-second), 4,188 tokens per meeting call, zero
retries absorbed over the smoke's five seeds, $0 on the flat-rate plan. The lever that moves
the estimate is worker count, capped by the provider at two inference units per 27B request
against a four-unit cap — not by the recorder.

For comparison, the MEASURED baseline-6 legs (`replays/ml_corpus/README.md`:300-310) were
4p1i 0h45m for 50 games, 9p2i 19h26m for 150 games, plus a 2h43m phantom-repair pass:
~22h54m for 200 corpus games.

### 0.2 The recording protocol actually run

Four legs in the ratified §9 value order — `replays/samples/9p2i` → `replays/ml_corpus/9p2i`
→ `replays/samples/4p1i` → `replays/ml_corpus/4p1i`. The corpus 9p2i leg precedes both 4p1i
legs because that is where the power is: the non-direct conviction cell is n=89 there against
n=33 in the samples and n=3 / n=0 on the 4p1i sets.

Every leg ran at the frozen Phase-20 slate, exported in one block before any worker process
started:

```
AILIBI_LLM_PROVIDER=featherless
AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_LLM_MEETING_MODEL=Qwen/Qwen3.6-27B
AILIBI_TASK_COMPLETION_FROM_EVENTS=1  AILIBI_SELF_LOCATION_TRAIL=1
AILIBI_MOVEMENT_CLAIM_SHAPE=1         AILIBI_GROUNDED_PROSECUTION=1
AILIBI_MAP_AWARE_ARBITRATION=1        AILIBI_STRUCTURED_TURN_MARKERS=1
AILIBI_MEETING_OUTCOME_MEMORY=1       AILIBI_COALESCED_MEMORY_RENDER=1
AILIBI_REFRESH_WORKERS=2              AILIBI_SEED_MAX_ATTEMPTS=8
```

`AILIBI_IMPOSTOR_ROLL_CALL` is unset on every leg — the one live toggle that stays OFF. The
operator's `FEATHERLESS_API_KEY` is not reproduced here or anywhere in this record.

Three operating notes carried from `audits/audit-phase-20-smoke.md` §13, all three executed:

1. The gate and the instruments run in a shell carrying the same eight `AILIBI_*` exports as
   the recording, because `api/replay_loader.py::_assert_substrate_matches` refuses a
   cross-substrate reconstruction. The bare committed-set gate runs without them.
2. `--expect-levers` is passed on the dry run too. Since Task 20.33 the preflight runs on the
   preview path, so a bare `--dry-run` under a Phase-20 shell exits 1. That is the guard
   working.
3. **The validity gate is not a measurement gate.** It passed cleanly on the smoke's five
   seeds while the honesty instrument could not fold them at all. This record therefore runs
   `scripts/measure_baseline.py --honesty` on the FIRST completed seed of EVERY leg, before
   the rest of that leg queues, and a raise is a STOP rather than a warning.

### 0.3 The actual, per leg

_PENDING — filled from the recorded legs._

| leg | games | wall | against the projection |
|---|---|---|---|

---

## 1. The validity gate

_PENDING._

## 2. The recorded substrate stamp

_PENDING._

## 3. The pre-registered read, bar by bar

_PENDING — every bar quoted with its own instrument's cell on the new bytes beside the
baseline-6 value and its denominator, in the memo's own order, each verdict MET or MISSED in
one word. No bar is re-priced; a missed bar is reported as missed with its number._

## 4. The four I-13 injustice fixtures, individually

_PENDING._

## 5. The secondary cells — observed, reported, never gated

_PENDING._

## 6. THE VERDICT

_PENDING._

## 7. The per-lever eligibility verdict (narrative only — never executed as a graduation)

_PENDING._

## 8. The referee and the baseline-7 floors

_PENDING._

## 9. Provenance

_PENDING._

## 10. What this record does NOT discharge

_PENDING._

## 11. Decisions

_PENDING._

## 12. Method + reproduction (all $0 against committed bytes, offline)

_PENDING._
