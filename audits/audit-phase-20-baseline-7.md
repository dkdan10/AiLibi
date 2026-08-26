# Phase-20 adopting record — baseline 7: the four legs, the pre-registered read, the decision executed (Task 20.36)

**Verdict: FINDING.** Bars 1 and 2 are MISSED on their pooled point estimates. Under the
ratified decision rule (`audits/audit-phase-20-preregistration.md` §6) that is FINDING, no lever
graduates, and **the ladder tip stands at baseline 6**. The bytes and the read are the
deliverable, and they are published here because that is the discipline the phase exists for.

**Reads against:** `audits/audit-phase-20-preregistration.md` §4 (the eight primary bars), §4.1
(the rare-event discipline), §5 (the secondary cells and the ±15-point win-split band), §6 (the
decision rule), §7 (the declared co-intervention), §8 (the abandon criteria), §9 (the record
order and the freeze), §10 (THE RATIFIED DECISION) and §11 (the amendment log);
`audits/audit-phase-20-counterfactual.md` §0, §6, §8 and §9; `audits/audit-phase-20-smoke.md`
§10, §12, §13 and §14; `audits/audit-phase-18-baseline-6.md` §§0-10 (the record-audit shape this
one mirrors).

---

## 0. The pre-record projection, and the actual against it

### 0.1 The projection, committed in advance

Both figures are `audits/audit-phase-20-smoke.md` §10's, re-derived there from measured tokens
rather than assumed, and committed to this file (commit `5c5c48be`) **before the first recorded
seed landed**. The record is 300 games: `samples/9p2i` 50, `ml_corpus/9p2i` 150, `samples/4p1i`
50, `ml_corpus/4p1i` 50.

| projection | basis | figure |
|---|---|---|
| at the smoke's own game lengths | 142,396 tokens per 9p2i game; the committed 4p1i:9p2i tokens-per-game ratio 0.066; 29.4 M tokens ÷ 368.2 tokens/s | **22.2 h** |
| at baseline-6 game lengths | 176,267 tokens per `samples/9p2i` game; 34.9 M tokens ÷ 368.2 tokens/s | **26.3 h** |

The measured operating constants behind both: 368.2 aggregate tokens per second at **two**
Featherless seed workers, 4,188 tokens per meeting call, zero retries absorbed over the smoke's
five seeds, $0 on the flat-rate plan. The lever that moves the estimate is worker count, capped
by the provider at two inference units per 27B request against a four-unit cap — not by the
recorder.

For comparison, the MEASURED baseline-6 legs (`replays/ml_corpus/README.md`) were 4p1i 0h45m for
50 games, 9p2i 19h26m for 150 games, plus a 2h43m phantom-repair pass: ~22h54m for 200 games.

### 0.2 The recording protocol actually run

Four legs in the ratified §9 value order — `replays/samples/9p2i` → `replays/ml_corpus/9p2i` →
`replays/samples/4p1i` → `replays/ml_corpus/4p1i`. The corpus 9p2i leg precedes both 4p1i legs
because that is where the power is: the non-direct conviction cell is n=68 there against n=30 in
the samples and n=2 / n=3 on the 4p1i sets **at the record** (n=89 / 33 / 3 / 0 before it).

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

1. The gate and the instruments run in a shell carrying the same eight `AILIBI_*` exports as the
   recording, because `api/replay_loader.py::_assert_substrate_matches` refuses a cross-substrate
   reconstruction. §10.1 is where that mechanism becomes this record's open question.
2. `--expect-levers` is passed on the dry run too. Since Task 20.33 the preflight runs on the
   preview path, so a bare `--dry-run` under a Phase-20 shell exits 1. That is the guard working.
3. **The validity gate is not a measurement gate.** It passed cleanly on the smoke's five seeds
   while the honesty instrument could not fold them at all. This record therefore ran
   `scripts/measure_baseline.py --honesty` on the FIRST completed seed of EVERY leg, before the
   rest of that leg queued, with a raise defined as a STOP. **No probe raised.** The instrument
   folded every cell family on v4 lever-ON bytes at the first seed of legs 1, 2 and 4 — the
   §11 smoke defect class is lifted in the recording that matters, not only on the preserved
   smoke bytes.

   One probe is recorded rather than counted: leg 3's first completed seed (`samples/4p1i` seed
   0) carried **zero meetings** — the impostor won before one was called — so that probe folded
   a game with nothing in it. It was re-run mid-leg over 19 games / 15 meetings and folded every
   cell family. A vacuous probe is not a passed probe, and this record says which one it was.

### 0.3 The actual, per leg

| leg | games | wall | notes |
|---|---|---|---|
| `replays/samples/9p2i` | 50 | **5h42m06s** | seed 0 alone (15m35s) for the honesty probe, then 1..49 on two workers |
| `replays/ml_corpus/9p2i` | 150 | **16h00m16s** + **0h12m33s** repair | the phantom repair below |
| `replays/samples/4p1i` | 50 | **0h42m30s** | |
| `replays/ml_corpus/4p1i` | 50 | **0h47m01s** | |
| **window** | **300** | **23h25m42s** (2026-08-25 00:30:24Z → 23:56:06Z) | **$0.0000** |

**23h25m42s against 22.2 h and 26.3 h** — inside the pre-committed bracket, nearer the lower
figure. The ETA re-derived at the first leg's completion (411 s per 9p2i game measured on leg 1,
4p1i at the committed 0.066 ratio) projected 23.6 h for the four sets; the actual came in 9
minutes under that. The clock was measured, not hoped, and it held.

### 0.4 Re-records, with cause

**Two seeds re-recorded, both in the corpus 9p2i leg, both logged as they happened rather than
reconstructed afterwards.** All 150 seeds recorded on the first pass, but
`scripts/record_ml_corpus.sh`'s freeze guard `check_replay_provenance` refused to freeze:

```
check_replay_provenance: 2 violation(s) in replays/ml_corpus/9p2i —
  replay-seed-1080.jsonl: 1 deadline_default failed-call row(s) — the turn(s) were DEFAULTED,
    so the transcript carries a fallback husk rather than model output; re-record the seed;
  replay-seed-1138.jsonl: 1 deadline_default failed-call row(s) — ... re-record the seed
```

This is the `(deadline_default)` watch item `audits/audit-phase-18-baseline-6.md` §7 carries
forward, and the same phantom class the 18.13 corpus leg paid a 2h43m repair pass for at
**10/150**. Here it was **2/150**, repaired in **12m33s**. Both replays were dropped and
re-recorded by the same recorder on the same slate; the resumed run then froze and gated clean.
Nothing else was re-recorded, and **no transport retry was absorbed anywhere in the 23-hour
window** — zero `WARN … retrying` lines across all four legs.

The freeze guard doing exactly this is the watch item working. A defaulted turn means the
transcript holds a fallback husk instead of model output, and a frozen record must not contain
one under either of the two shapes `_record_deadline_defaults` writes.

---

## 1. The validity gate — PASS on all four legs

`uv run python scripts/validity_gate.py <set> --expected-model Qwen/Qwen3.6-27B
--require-zero-cost`, run under the recorded slate after each leg and before the next began:

| leg | result |
|---|---|
| `replays/samples/9p2i` | **PASS** (2026-08-25 06:12:30Z) |
| `replays/ml_corpus/9p2i` | **PASS** (2026-08-25 22:26:35Z) |
| `replays/samples/4p1i` | **PASS** (2026-08-25 23:09:05Z) |
| `replays/ml_corpus/4p1i` | **PASS** (2026-08-25 23:56:06Z) |

No §8 abandon criterion fired during recording: no validity FAIL, no guard trip, no lever-stamp
mismatch. The two defaulted seeds are the `(deadline_default)` criterion — handled by the
standing re-record rule (§0.4), which is what that rule is for.

### 1.1 Byte-verification and reconstruction

Run under the recorded slate, because the reconstruction is substrate-coupled (§10.1):

* `bash scripts/verify_samples.sh` — **100/100 clean**, 50 on each committed samples set.
* `uv run python scripts/verify_ml_evidence.py` (FULL, not `--fast`) — **corpus reconstruction
  300/300** across all four declared sets: 50/50 `samples/4p1i`, 50/50 `samples/9p2i`, 50/50
  `ml_corpus/4p1i`, 150/150 `ml_corpus/9p2i`.

The same run reports **11 FAILs, and every one of them is an ML-fit pin** ground on the
baseline-6 corpus this record replaced — the surrogate's ranking and SKIP-vs-eject channels, the
conviction model's Spearman / label / verdict fields, the composed runner's four cells, and the
fit-corpus identity fingerprint that moved because the corpus moved. Five further rows report
EVIDENCE-BRANCH-ABSENT, the expected state of a checkout that has not run
`scripts/fetch_evidence.sh`. **None of the eleven is a defect in these bytes**; they are the
measured size of the ML re-ground §10.2 names and does not discharge. Recording that the debt is
now quantified rather than merely stated is the point of running the command in full.

## 2. The recorded substrate stamp

Every MANIFEST row on every set carries the same twenty-one-key flags cell — the thirteen
retired always-on levers plus the eight Phase-20 levers — with `impostor_roll_call` absent
(recorded OFF), the four v4 templates, the `fsm-default` tactical policy, and `0.0000`:

```
| 0 | Qwen/Qwen3.6-27B
  | accusation_round.qwen3_6_27b.v4, crewmate_report.qwen3_6_27b.v4,
    impostor_report.qwen3_6_27b.v4, vote_ballot.qwen3_6_27b.v4
  | absence_prior, citation_gate, coalesced_memory_render, evidence_quality_lift,
    grounded_prosecution, hard_evidence_gate, map_aware_arbitration, meeting_outcome_memory,
    movement_claim_shape, movement_perception, observation_id_rendering, reporter_exculpation,
    roll_call_round, self_location_trail, structured_turn_markers, task_completion_from_events,
    testimony_as_content, unfreeze_memory, vent_placement_contradictions,
    whereabouts_interior_flags, witnessed_kill_evidence
  | fsm-default | 2026-08-25 | <sha> | 0.0000 | CREWMATES |
```

The stamp equals the declared slate exactly, on all 300 rows. No row stamps a v3 template: the
v3 prompt archive has no committed reader left.

---

## 3. The pre-registered read, bar by bar

Every bar is quoted from the instrument that owns it and no other, on the new bytes, beside its
baseline-6 value and its denominator, in the memo's own order, each verdict in one word. **No
bar is re-priced.** Where a bar is missed it is reported as missed with its number.

### Bar 1 — I-1 non-direct conviction accuracy: **MISSED**

Target: 0.368 → **≥ 0.60 pooled**, and no adequately powered set below 0.50.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 10/33 = 0.3030 | **16/30 = 0.5333** [0.3614, 0.6977] |
| `ml_corpus/9p2i` | 35/89 = 0.3933 | **42/68 = 0.6176** [0.4988, 0.7239] |
| `samples/4p1i` | 1/3 = 0.3333 | **1/2 = 0.5000** [0.0945, 0.9055] — ADVISORY |
| `ml_corpus/4p1i` | 0/0 (None) | **2/3 = 0.6667** [0.2077, 0.9385] — ADVISORY |
| **pooled** | **46/125 = 0.3680** [0.2886, 0.4553] | **61/103 = 0.5922** [0.4957, 0.6822] |

**MISSED by 0.0078 — less than one ejection.** 62/103 would be 0.6019 and would have met it.
The bar is missed and is reported as missed; the interval is context, not the test (§4.1's
point-estimate convention), and rounding 0.5922 to "0.59" or reading the interval as covering
0.60 would both be re-pricing. The powered per-set clause is satisfied — both n ≥ 30 sets
(`samples/9p2i` n=30, `ml_corpus/9p2i` n=68) sit above 0.50 — but a satisfied sub-clause does
not rescue a missed pooled gate.

Advisory labels, applied at the RECORDED denominator by §4.1's own `1/n > |target − baseline|`
test against a margin of 0.232: the 4p1i cells (n=2 → step 0.500; n=3 → step 0.333) are
advisory and take no part in the verdict in either direction. Note `samples/9p2i` fell to n=30,
exactly the powering floor: step 1/30 = 0.033, still an order of magnitude inside the margin.

The direct-proof cell stays perfect and grew: **326/326 = 1.000** pooled (69 + 212 + 19 + 26),
against 310/310 before.

### Bar 2 — I-1 innocent ejections: **MISSED**

Target: 79 → **< 35 pooled**. All of them sit inside the non-direct cell; the direct-proof cell
is innocent-free on both records.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 23 | **14** |
| `ml_corpus/9p2i` | 54 | **26** |
| `samples/4p1i` | 2 | **1** |
| `ml_corpus/4p1i` | 0 | **1** |
| **pooled** | **79** | **42** |

**MISSED.** 42 against a bar of < 35. The fall is real — 79 → 42 is a 47% reduction in wrongful
convictions — and it is not enough for the bar that was written before the levers existed.

### Bar 3 — I-2 false crew self-placement: **MET**

Target: 21.0% → **< 5% on `samples/9p2i`, and every set < 8%**.

| set | before | after | clause |
|---|---|---|---|
| `samples/9p2i` | 152/723 = 21.0% | **3/659 = 0.46%** [0.0015, 0.0133] | < 5% ✔ |
| `ml_corpus/9p2i` | 409/2038 = 20.1% | **17/1892 = 0.90%** [0.0056, 0.0143] | < 8% ✔ |
| `samples/4p1i` | 10/78 = 12.8% | **1/80 = 1.25%** [0.0022, 0.0675] | < 8% ✔ |
| `ml_corpus/4p1i` | 16/79 = 20.3% | **0/91 = 0.00%** [0.0000, 0.0405] | < 8% ✔ |
| **pooled** | **587/2918 = 20.12%** | **21/2722 = 0.77%** [0.0051, 0.0118] | |

**MET, on every clause, by more than an order of magnitude.** This is the record's clearest
result: crewmates in this substrate almost never mis-state where they were. The denominators
held (2,918 → 2,722), so this is not a suppression artifact — the claims are still being made,
they are just true now. Every set's clause is powered at the recorded denominator except
`samples/9p2i`, whose 3/659 cell carries the rare-count label the instrument prints; the clause
is met at any reading of it.

### Bar 4 — I-3 sole-`alibi_vs_sighting` convicting precision: **MISSED** (and the §6 waiver applies)

Target: 14.6% → **≥ 50% pooled**, AND the class impostor share above the living-voter base rate.
The population is `sole_flag_precision.per_victim_precision` — the kind-sole cell the §10 ruling
binds, not the exactly-one-flag companion.

| cell | before | after |
|---|---|---|
| per-victim precision | 12/82 = 14.6% | **0/0 (None)** — the class is empty on all four sets |
| class impostor share | 33/192 = 17.2% | **0/0 (None)** |
| living-voter base rate | 255/1017 = 25.1% | **0/0 (None)** |

**MISSED.** The bar is conjunctive and neither half can be read: there is no precision to
compare to 50% and no class share to compare to a base rate. A bar whose cell is empty has not
been met, and §10 requires a miss to be reported as one.

**Separately — and this is a different statement — §6's class-closed waiver IS satisfied.** The
decision rule accepts its bar-4 clause when "the pooled denominator of
`sole_flag_precision.per_victim_precision` has fallen below 20". It has fallen from 82 to
**0**. The class that convicted 70 innocents on a single alibi-versus-sighting flag no longer
exists on these bytes. The bar is missed; the rule's bar-4 clause is nevertheless satisfied.
Nothing here re-prices bar 4.

The exactly-one-flag companion (`per_victim_single_flag_precision`, 8/58 before) is also 0/0,
so the two readings that differed on baseline 6 agree here — both by being empty.

### Bar 5 — I-4 grounded sighting side: **MET (vacuously)** — SUPPRESSED-NOT-FIXED

Target: **100% of the surviving STRONG sighting sides**, at tick.

| cell | before | after |
|---|---|---|
| grounded at tick | 124/234 = 53.0% | **0/0 (None)** — zero surviving STRONG sighting sides |
| within ±1 (reported beside, never in place of) | 154/234 = 65.8% | **0/0 (None)** |

**MET, vacuously**, on §4.1's own rule for this bar, quoted rather than interpreted: bar 5 is a
COUNT bar whose "target of ZERO occurrences … is decided on the numerator … one occurrence
fails, none passes, at any denominator, **and an empty denominator passes vacuously**." There
are zero ungrounded surviving STRONG sighting sides because there are zero surviving STRONG
sighting sides.

**Labelled SUPPRESSED-NOT-FIXED**, exactly as §4.1 requires: the denominator fell from 234 to 0,
far below the 24 (10% of baseline) threshold that triggers the label. The verdict does not
change — suppressing an ungrounded flag is the intended repair, not a dodge — but the mechanism
is not left implicit. The levers did not ground this evidence; they stopped it from being minted
as STRONG at all.

The counterfactual predicted this bar would MISS at 10/12 = 83.3%. It did not miss; it emptied.
The difference is the one §6 of that memo named as falsifiable in the useful direction: the
record mints its flags in live meetings under the new substrate, where the surviving-STRONG
population is not the frozen twelve.

### Bar 6 — I-5 fabricated completion lines: **MET**

Target: **0 on every set**.

| set | before | after |
|---|---|---|
| `samples/9p2i` | 19/458 | **0/308** [0.0000, 0.0123] |
| `ml_corpus/9p2i` | 40/1311 | **0/979** [0.0000, 0.0039] |
| `samples/4p1i` | 15/61 | **0/38** [0.0000, 0.0918] |
| `ml_corpus/4p1i` | 14/58 | **0/40** [0.0000, 0.0876] |
| **pooled** | **88/1888 = 4.66%** | **0/1365 = 0.00%** [0.0000, 0.0028] |

**MET on all four sets.** No SUPPRESSED-NOT-FIXED label: the §4.1 threshold for this bar is
`samples/9p2i` falling under 46 rendered rows (10% of 458) and it holds 308. The rendered-row
population shrank (1,888 → 1,365, the coalesced render doing its job) but stayed an order of
magnitude above the label's floor, and the fabrication count went to zero rather than the
population going to zero. `render_offset_matches` is 308/308, 979/979, 38/38, 40/40 — the +1
render offset holds everywhere.

### Bar 7 — I-6 adjacent-room STRONG share: reported with both readings; **not decision-bearing here**

Target: 63.2% → **~0, operationalised as ≤ 5% pooled**. The numerator is
`adjacent_room_flags.adjacent` — one doorway apart AND the sighting within ≤ 1 tick of the alibi
window — with the un-gated `adjacent_any_gap` reported beside it and never in place of it.

| cell | before | after |
|---|---|---|
| adjacent (the registered numerator) | 148/234 = 63.2% [0.5690, 0.6917] | **0/0 (None)** |
| `adjacent_any_gap` (beside it) | 148/234 | **0/0 (None)** |
| distance 2 / ≥3 / single-tick window | 71 / 15 / 187 | **0 / 0 / 0** |

**The adjacent-flag COUNT fell from 148 to 0, and the STRONG denominator from 234 to 0.** The
rate is undefined.

Two readings exist and this record states both rather than choosing the convenient one:

* **As a count**, the bar's own words — "63.2% → ~0" — are satisfied in the strongest available
  sense: there is not one adjacent-room STRONG flag left on 300 games.
* **As a rate**, which is how §4 operationalises it ("≤ 5% pooled"), the cell is `None` and a
  bar whose cell is undefined has not been arithmetically met. §4.1's explicit vacuous-pass rule
  is scoped to the COUNT bars 5 and 6 and does not reach bar 7.

**This record does not need to resolve that**, and deliberately does not: bars 1 and 2 are
missed, §6 is conjunctive over bars 1, 2, 3, 5, 6 and 7, so the verdict is FINDING under either
reading of bar 7. Choosing a reading here — with the verdict already fixed and nothing riding on
it — would be exactly the re-pricing §10 forbids. The cell is published; the question is
recorded for whoever writes the next set of bars.

### Bar 8 — the four I-13 injustice fixtures: **4/4 FLIPPED** — see §4

---

## 4. The four I-13 injustice fixtures, individually

Four separate verdicts, never one aggregate. Each anchored meeting was re-read from the recorded
bytes through the real `ReplayLoader`, and each is recorded as FLIPPED, SURVIVING or RE-ANCHORED
from data.

### (a) Provenance-impossible sighting — `9p2i` seed 23 M1: **FLIPPED**

*Before:* a crewmate ejected on a cross-statement flag whose sighting half was spoken by an
impostor whose ability to make it was never examined.
*After:* the meeting carries **no flags at all**, outcome **SKIPPED**, **nobody ejected**. The
injustice has no material left to be made of.

### (b) Content-vs-own-memory miss — `9p2i` seed 12 M0: **FLIPPED**

*Before:* both sides of the fatal flag authored by innocents; two honest, slightly-wrong
accounts ejected a truthful crewmate.
*After:* outcome **SKIPPED**, **nobody ejected**. Two flags naming p-5 survive and **both band
WEAK** (`alibi_conflict` and `alibi_vs_sighting`, category `weak_signal`). The flags still
inform; they can no longer convict alone. This is the grounded-prosecution mechanism doing
precisely what 20.26's under-the-lever pin predicted for this anchor.

### (c) One-tick interval artifact — `4p1i` seeds 49 and 41 M0: **FLIPPED**

*Before:* seed 49's two flags weak-stamped and obeyed anyway; seed 41's one-tick roll-call
placement took the 18.9 interior exemption and minted a STRONG flag — same material, opposite
weighting.
*After:* **neither meeting carries a directional flag at all.** Seed 49 ejects p-4, an
**IMPOSTOR**, on a grounded `vent_sighting` role proof; seed 41 ejects p-3, an **IMPOSTOR**, on
the same kind of proof. The one-tick population that drove the artifact is empty.

### (d) Equal-weight conflict — `4p1i` seed 41 M0: **FLIPPED**

*Before:* the meeting carried a grounded `vent_sighting` naming the real impostor AND a
cross-statement flag naming a crewmate, and the ejection went to the crewmate (p-4).
*After:* the meeting carries **exactly one flag** — the `role_proof` `vent_sighting` naming p-3
— and **ejects p-3, the IMPOSTOR**. There is no competing cross-statement flag left for the
proof to be weighed equally against.

**Bar 8: four of four flipped.** §6's "at least three of the four fixtures flip" clause is met
with one to spare. No fixture had to be re-anchored, and none was silently weakened; every
anchor still names a committed replay and a real meeting.

---

## 5. The secondary cells — observed, reported, never gated

None of these can decide the verdict (§5, §10). They are reported because a record that
publishes only its gated cells is not a record.

### 5.1 The win split, against the pre-registered ±15-point band

| set | baseline-6 impostor rate | baseline-7 | delta | inside ±15 |
|---|---|---|---|---|
| `samples/9p2i` | 15/50 = 30% | **12/50 = 24%** | −6 | ✔ |
| `ml_corpus/9p2i` | 38/150 = 25.3% | **36/150 = 24%** | −1.3 | ✔ |
| `samples/4p1i` | 17/50 = 34% | **18/50 = 36%** | +2 | ✔ |
| `ml_corpus/4p1i` | 11/50 = 22% | **13/50 = 26%** | +4 | ✔ |

**Every leg inside its band.** Per §7 the split cannot attribute anything: the scripted-mover
repair (20.32) rides this same record as a declared co-intervention, so a win-split move is
un-attributable by construction. It is reported and nothing is built on it.

### 5.2 The solvability y-axis (I-12)

| cell | before (pooled) | after (pooled) |
|---|---|---|
| containment (killer in the candidate set) | 544/626 = 86.9% | **555/618 = 89.8%** [0.8717, 0.9195] |
| singleton candidate sets | 126/626 = 20.1% | **80/618 = 12.9%** |
| singleton correct | 114/126 = 90.5% | **72/80 = 90.0%** |
| ejections on an already-cleared player | 83/354 = 23.4% | **68/379 = 17.9%** [0.1441, 0.2212] |

The cleared-player cell fell, as §5 expected it to. Containment rose. Both 4p1i sets score
1.000 containment and **zero** cleared-player ejections.

### 5.3 The context and co-intervention cells

| cell | before (pooled) | after (pooled) |
|---|---|---|
| I-7 movement-origin flags | 38/313 | **1/91** [0.0019, 0.0597] |
| I-8 marker contamination (turns) | 192/3934 | **0/3602** |
| I-8 marker contamination (prompts) | 917/7932 | **0/7211** |
| I-9 singular-persona prompts | 1956/1956, 5502/5502 (9p sets) | **0/1746, 0/4961** violations; the 4p sets stay NOT-APPLICABLE (one impostor) |
| I-10 meetings with a venting participant | 69/707 | **91/668** [0.1123, 0.1643] |
| I-10 reporter killed ≤ 3 ticks after | 111/707 | **80/668** |
| I-11 free zero-witness kills declined | frozen at the pre-repair sha (§11 erratum) | live-policy fold: 8/228, 41/704, 0/67, 0/61 |
| I-11 ghost-top decisions | frozen (§11 erratum) | 5/1750, 4/5528, 0/551, 0/529 — **0 reconstruction mismatches over 8,358 decisions** |

**Marker contamination went to zero on both halves**, on all four sets — the structured-turn-marker
lever's own cell, and the cleanest secondary result in the table. I-11's baseline is read from
the frozen `eval.evidence_honesty.RATIFIED_I11_CELLS` per the 2026-08-20 erratum, never from the
live fold, because the policy the committed baseline-6 bytes were recorded with is no longer in
the tree; the "after" column above is the live-policy fold and is not compared against it.

### 5.4 The render census (20.30's cells)

| set | before | after |
|---|---|---|
| `samples/9p2i` | 1,956 snapshots, mean 51.1038 rendered rows, 18,319 testimony rows (≤4: 2,794; 5-6: 11,772; ≥7: 3,753) | **1,746 snapshots, mean 37.03, 26,735 testimony rows (≤4: 8,108; 5-6: 17,245; ≥7: 1,382)** |
| `ml_corpus/9p2i` | — | **4,961 snapshots, mean 37.06, 71,521 rows (≤4: 22,488; 5-6: 44,217; ≥7: 4,816)** |
| both 4p1i sets | zero testimony rows | **zero testimony rows** (mean 11.08 and 11.68) |

Mean rendered lines per snapshot fell 51.10 → 37.03 while retained testimony rows rose 18,319 →
26,735: the coalesced render spends less budget per snapshot and keeps more testimony inside it.
Reported per bucket, never as one blended number, because both 4p1i sets still carry zero
testimony rows.

### 5.5 The meeting population

Meetings pooled: **707 → 668** (152 + 432 + 40 + 44). Ejections pooled: **435 → 429**.

---

## 6. THE VERDICT

The rule, applied verbatim (`audits/audit-phase-20-preregistration.md` §6): **ADOPTED** iff bars
1, 2, 3, 5, 6 and 7 are met AND at least three of the four fixtures flip AND either bar 4 is met
or the pooled `per_victim_precision` denominator has fallen below 20. **FINDING** otherwise.

| bar | target | recorded | verdict |
|---|---|---|---|
| 1 | non-direct accuracy ≥ 0.60 pooled | 61/103 = 0.5922 | **MISSED** |
| 2 | innocent ejections < 35 pooled | 42 | **MISSED** |
| 3 | false self-placement < 5% / < 8% | 0.46% / 0.90% / 1.25% / 0.00% | **MET** |
| 4 | per-victim precision ≥ 50% + class share > base rate | 0/0 | **MISSED** (waiver satisfied: denominator 82 → 0 < 20) |
| 5 | zero ungrounded surviving STRONG sighting sides | 0/0 | **MET** (vacuous; SUPPRESSED-NOT-FIXED) |
| 6 | zero fabricated completion lines, every set | 0/308, 0/979, 0/38, 0/40 | **MET** |
| 7 | adjacent-room STRONG share ≤ 5% pooled | 0/0 (count 148 → 0) | **reported both ways; not decision-bearing** |
| 8 | ≥ 3 of 4 fixtures flip | 4 of 4 | **MET** |

**Bars 1 and 2 are MISSED. The verdict is FINDING.**

Executed in this PR, per §6 and the contract:

* **The registry is unchanged.** The eight `*_enabled` resolvers stay env-gated, their keys stay
  in `_TOGGLEABLE_LEVER_RESOLVERS`, and `substrate_flag_snapshot({})` still stamps them False.
* **No lever graduates.** Partial adoption graduates nothing: a subset slate matches neither
  committed record's stamp, so all eight graduate together under ADOPTED or none does. None
  does.
* **`_DEFAULT_BASELINE_ID` stays `"baseline-6"`.**
* **The ladder tip stands at baseline 6.**

**What the record actually found, stated plainly.** The evidence-honesty substrate did what it
was built to do and then some: false self-placement fell 20.1% → 0.77%, fabricated completion
lines went to zero on every set, marker contamination went to zero on both halves, the STRONG
`alibi_vs_sighting` class that convicted 70 innocents closed completely, and all four injustice
fixtures flipped. What it did **not** do is move the crew's non-direct conviction accuracy to
0.60 or push wrongful ejections below 35. Removing bad evidence made the crew wrong less often —
79 → 42 innocent ejections, 0.368 → 0.592 accuracy — but it did not make them right often
enough for bars written before any of it existed.

Bar 1 missing by 0.0078 is the sharpest thing in this record, and it is reported as a miss.
Pre-registration exists so that a number this close cannot be argued into a pass afterwards.

**Against the counterfactual's prediction.** `audits/audit-phase-20-counterfactual.md` §6
predicted FINDING and named bars 5 and 7 as the expected misses. **The verdict matches; the
reasoning does not.** Bars 5 and 7 did not miss — their populations emptied. Bars 1 and 2, which
that memo correctly declared NOT PREDICTABLE OFFLINE, are what actually decided it. The offline
instrument was right about the outcome and right about its own limits, which is the more useful
of the two.

---

## 7. The per-lever eligibility verdict — narrative only, never executed

§6's eligibility test is conjunctive: (i) the lever's named bar is met on the recorded bytes,
(ii) 20.34's published OFF/ON table predicted that direction and magnitude for that lever's own
cell before the record was spent, and (iii) it is independently stampable — which 20.33
guarantees for all eight. Published lever by lever below; **executed as a graduation for none of
them**, because under FINDING nothing graduates and no subset may graduate under any verdict.

| lever | its bar | bar met? | 20.34 predicted the direction? | ELIGIBLE |
|---|---|---|---|---|
| `task_completion_from_events` | bar 6 (fabricated completion lines) | **yes**, 0 on all four sets | yes — 0/347, 0/1045, 0/46, 0/44 offline | **yes** |
| `map_aware_arbitration` | bar 7 (adjacent-room STRONG share) | count yes, rate undefined | yes — predicted 140 of 148 adjacent flags demoted | **partial** — turns on §3's unresolved bar-7 reading |
| `grounded_prosecution` | bar 5 (grounded sighting side) | yes, vacuously | yes — predicted the STRONG class collapsing 234 → 12; the record emptied it | **yes**, with the SUPPRESSED-NOT-FIXED label attached |
| `self_location_trail` | bar 3 (false self-placement) | **yes**, by an order of magnitude | **no** — §7 of the counterfactual states this cell is NOT PREDICTABLE OFFLINE | **no** (clause ii fails) |
| `structured_turn_markers` | none (I-8 is §5 secondary) | n/a | its cell went to zero on both halves | **no** — no ratified bar rides it |
| `movement_claim_shape` | none (I-7 is §5 secondary) | n/a | movement-origin flags 38/313 → 1/91 | **no** — no ratified bar rides it |
| `meeting_outcome_memory` | none | n/a | render-census only | **no** — no ratified bar rides it |
| `coalesced_memory_render` | none (render census is §5 secondary) | n/a | mean rendered lines 51.10 → 37.03 | **no** — no ratified bar rides it |

The two bug-class levers §6 named as the expected members — `task_completion_from_events` and
`map_aware_arbitration` — are the two that come closest, exactly as the memo anticipated.
`self_location_trail` produced the record's largest single effect and is **not** eligible,
because no offline table predicted it in advance; that is the eligibility test working as
designed rather than a comment on the lever.

An eligible lever keeps its default-OFF gate. Its ON-path evidence is carried forward —
published here, counterfactual-predicted where it could be, fixture-pinned — and it graduates at
the next record made at its own slate.

---

## 8. The referee and the baseline-7 floors

The three Layer-1 supply gauges, measured on the recorded bytes through `compute_watchability`'s
own gauge seam, with the raw numerators:

| gauge | `samples/9p2i` | `samples/4p1i` |
|---|---|---|
| `witnessed_event_rate` | **3/177 = 0.01694915254237288** | **1/65 = 0.015384615384615385** |
| `flags_per_meeting` | **134/152 = 0.881578947368421** (92 persisted vent + 42 re-derived transcript flags) | **20/40 = 0.5** (20 persisted vent + 0 re-derived) |
| `testimony_backed_conversion` | **80/115 = 0.6956521739130435** | **19/31 = 0.6129032258064516** |

Both `witnessed_event_rate` numerators (3 and 1) are rare counts. The 4p1i gauge is marked
ADVISORY by the standing 15.19 rule at numerator 1, as it already was on baseline 6; the 9p2i
gauge at numerator 3 is **not** marked advisory by that rule, and the block says so rather than
claiming a label the machinery does not apply — one witnessed kill still moves it by a third of
itself, which is how it should be read.

Scored against the **baseline-6** floors it is still the default for, the record reads:
`samples/9p2i` referee **FAIL** (witnessed 0.0169 < 0.0339; flags 0.8816 < 1.0909; conversion
0.6957 < 0.7097 population-relative) and `samples/4p1i` referee **PASS** (flags 0.5 ≥ 0.4103;
conversion 0.6129 ≥ 0.2462; the witnessed gauge fails advisorily). **That FAIL is the expected
and correct reading, not a defect**: baseline 6's floors are pinned to baseline 6's own evidence
supply, and this substrate deliberately mints fewer flags — 180/165 = 1.0909 became 134/152 =
0.8816 because the flags it stopped minting are the ones bar 5 and bar 7 were about. A referee
that passed a set which suppressed its own bad evidence would be measuring the wrong thing.

The baseline-7 block is pinned from the numbers above with the same 16.11 population-relative
derivation, and its self-consistency property holds by construction: flags ratio exactly 1.0 →
derived conversion floor = pin → the record scores PASS against its own floors at exact
equality. `_DEFAULT_BASELINE_ID` **stays `"baseline-6"`** under FINDING, so the new block is
scoreable only via an explicit `--baseline-id`, exactly as baselines 3, 4 and 5 are.

The training-side selection constants deliberately lag: `BAKEOFF_BASELINE_ID`
(`training/bakeoff/harness.py`) is untouched by this record. The ML re-ground is a future owner
decision and is named in §10, not discharged here.

---

## 9. Provenance

| field | value |
|---|---|
| model | `Qwen/Qwen3.6-27B`, non-thinking, via Featherless (the Task-16.2 lock) |
| prompt set | `qwen3_6_27b`, all four templates at **v4** on all 300 rows |
| lever slate | the thirteen retired always-on levers + the eight Phase-20 levers ON; `impostor_roll_call` OFF |
| tactical policy | `fsm-default` in every MANIFEST `policy` cell, on all 300 rows |
| co-intervention | Task 20.32's scripted-impostor-mover repair, inside the freeze — its identity carried by the `git_sha` column |
| cost | **$0.0000** on every row; flat-rate provider |
| window | 2026-08-25 00:30:24Z → 23:56:06Z, 23h25m42s, two parallel seed workers |
| re-records | 2 (`ml_corpus/9p2i` seeds 1080 and 1138, `deadline_default` rows — §0.4) |
| transport retries absorbed | **0** |
| `(deadline_default)` watch item | **FIRED, at 2/150 on the corpus 9p2i leg** — caught by the freeze guard before the freeze, repaired by re-record, and closed. Down from 10/150 at the 18.13 baseline-6 record. |
| git shas | the record spans several branch commits; each MANIFEST row keeps the sha of the session that recorded its bytes, per the recorder's own per-seed provenance rule |

**The co-intervention, and its attribution consequence.** Task 20.32's mover repair landed before
the freeze and rides these bytes. Per §7 of the pre-registration, **no honesty bar in §3 may be
attributed to a lever on the strength of the win split.** Attribution rests on (a) the offline
counterfactual over frozen baseline-6 bytes, which holds the mover constant by construction, and
(b) the recorded per-cell before/after in §3 and §5. The §5.1 band is reported and nothing is
built on it. The repaired mover's own cells are the I-11 rows in §5.3, read as a live-policy
fold and never against the frozen baseline.

---

## 10. What this record does NOT discharge

### 10.1 The open ruling: where a FINDING record's bytes live

**This is the one thing blocking the rest of the task, and it is an owner decision, not an agent
judgment call.**

`api/replay_loader.py::_assert_substrate_matches` raises on ANY differing `SUBSTRATE_FLAG_KEYS`
entry. Under ADOPTED the eight levers become unconditional, a bare-environment snapshot equals
the baseline-7 stamp, and the committed bytes reconstruct. **Under FINDING they stay toggles, a
bare snapshot stamps them False, and the committed baseline-7 bytes cannot reconstruct in a bare
shell.** Proven, not argued — `bash scripts/verify_samples.sh replays/samples/9p2i` in a shell
with no lever exports:

```
api.replay_loader.ReplaySubstrateMismatchError: replay substrate mismatch for 'headless-seed-0':
recorded with {... all eight True ...} but reconstructing under {... all eight False ...}
(differing levers: ['coalesced_memory_render', 'grounded_prosecution', 'map_aware_arbitration',
'meeting_outcome_memory', 'movement_claim_shape', 'self_location_trail',
'structured_turn_markers', 'task_completion_from_events'])
```

Pre-registration §6 states the mechanism — "under ADOPTED all eight graduate and the bare
snapshot equals the baseline-7 stamp; under FINDING all eight stay toggles and the bare snapshot
equals the baseline-6 stamp; there is no third substrate" — but it does not say **where a
FINDING record's bytes live**. Task 20.36's files-in-scope place them in the canonical set dirs,
which is coherent only under ADOPTED.

The consequence is mechanical: `scripts/verify_samples.sh`, the API's serving path and every
test that asserts the committed bytes load under the DEFAULT substrate cannot pass while
lever-ON bytes sit in the canonical set dirs and the levers remain toggles.

**Measured, so the ruling is made on numbers rather than on this paragraph.** The full suite is
`432 failed, 4911 passed, 48 errors` under the recorded slate and `434 failed, 4909 passed, 48
errors` in a bare shell — the exports barely move it, which is the useful finding. The failures
split into three classes, and only the first is blocked:

| class | evidence | blocked by the ruling? |
|---|---|---|
| tests that assert the committed bytes load under the DEFAULT substrate | 182 `ReplaySubstrateMismatchError` occurrences, **identical under both environments** — these tests build a bare environment deliberately, which is the invariant FINDING breaks | **yes** — no re-pin fixes them |
| reconstruction-path divergence | 78 `reconstructed state_hash_after` mismatches, chiefly the prompt byte golden's meeting rebuild | **partly** — a real fix, whose shape depends on the answer |
| stale value pins | the remainder: ordinary before/after numbers with well-defined new values (e.g. `meetings_total` 165 → 152, I-2 `(152, 723)` → `(3, 659)`) | **no** — these are the census-driven sweep and are re-pinnable today |

So the sweep is not "un-runnable": most of it is ordinary re-pinning. What no amount of re-pinning
reaches is the first class, and `check.sh` cannot go green while it stands.

**The bytes are not what is in question.** Under the recorded slate the same commands are clean:
`verify_samples.sh` reports 100/100 and `verify_ml_evidence.py` reports 300/300 reconstruction
(§1.1). What is in question is which substrate the repository declares as ambient.

**Two further sweep items are recorded here so the ruling is made with them in view.**

1. `tests/meetings/test_prompt_byte_golden.py` diverges on the meeting-level `state_hash_after`
   rebuild for `9p2i` seed 0 meeting 0 **even under the recorded slate** — its rebuild path needs
   substantive updating for a lever-ON meeting fold, not just a re-pinned constant. That work is
   part of the `tests/meetings/` sweep and is only worth doing once the substrate question is
   settled, because the shape of the fix depends on the answer. It is also why the v3
   prompt-archive retirement is not taken here: retiring the archive without being able to run
   the golden or its one-byte perturbation leg would be an unverified change to a gate.
2. **The byte-coupled pin census is wider than the contract's.** The contract's census starts
   from `grep -rln 'replays/samples\|replays/ml_corpus' tests/` (38 files) plus the Phase-20
   instrument tests. It misses at least one pin outside `tests/`:
   `frontend/src/lib/bodies.test.ts` recomputes a `corpusSha256` digest over
   `replays/samples/<set>` on every run and compares it to `bodies.fixture.json`, alongside
   census assertions (`games`, `frames`, body-state counts) folded from the same bytes. The
   frontend suite therefore fails on this record, and regenerating the fixture alone would not
   fix it — the census assertions in the test body move too. Whoever runs the sweep should start
   from a repo-wide grep, not a `tests/`-scoped one.

Amending the pre-registration is not available: §11's convention is that amendments "land BEFORE
the record or not at all for this phase's claims."

### 10.2 Deliberately out of scope, and named so nobody assumes otherwise

* **The ML re-ground.** `training/` artifacts and fits are frozen. The corpus this record
  re-recorded is the surrogate's calibration corpus; the surrogate has not been re-ground on it
  and `BAKEOFF_BASELINE_ID` still reads `baseline-5`. Whoever re-grounds it owns that task; the
  staleness rule is STATED here, not discharged.
* **The ladder-tip prose, the results table's before/after column and its narrative reading.**
  Task 20.38 owns them. Note that the raw win-rate and citation-compliance CELLS still have to
  move — `check_sample_provenance`'s win-rate sweep runs file-wide over README, and
  `check_result_sources` re-derives the citation row from the `tests/eval/test_vj_instruments.py`
  pin this record moves — so those cells are this record's to move and the sentences around them
  are not.
* **The production-side duplicate `alibi_vs_sighting` mint.** 20.43's erratum repaired the
  instrument side and routed the production side POST-record, so it **rides inside these bytes**.
  One witness who states both a static placement and the transition it came from still raises
  two flags in production; the instrument folds them to one. That is a known, dated, deliberate
  carry, and it is inside the recorded bytes rather than outside them.
* **The `samples/9p2i` MANIFEST's hand-maintained disclosure section.** It was dropped by the
  refresh, as its own note warned it would be ("a `refresh_samples.sh` manifest rewrite
  regenerates the table only and would drop it, and a re-record invalidates its numbers, so
  re-measure and re-add it after any refresh"). Its baseline-6 figures are invalid on these
  bytes and it must be re-measured, not restored.

---

## 11. Decisions

1. **Each set's prior bytes were moved aside before its leg, rather than resumed over.** A
   re-record at a new substrate cannot resume over off-substrate replays: both recorders' skip
   scans treat a present in-range replay as already recorded, and their provenance guards judge
   it against the declared slate. Moving them aside is the only way the recorders record what
   the record needs. The prior bytes were preserved, not deleted, for the duration.
2. **The corpus 9p2i freeze failure was treated as a phantom repair, not an abandon.** The
   contract's Step 3 standing rule is that a defaulted seed is a FAILED recording and re-records;
   the recorder's own message says to remove the file and re-record; the baseline-6 leg paid the
   same pass at 10/150. Logged with its cause as it happened (§0.4).
3. **Bar 7's empty-denominator reading is left open and stated both ways** (§3). It is not
   decision-bearing — bars 1 and 2 already miss — and choosing a reading with nothing riding on
   it would be re-pricing.
4. **The derived lab rubric artifacts move with the bytes.** `experiments/lab/results-rubric-score.json`
   and `results-rubric-geomean.json` are regenerated by `scripts/refresh_samples.sh`'s own
   committed recipe and are read by `tests/eval/test_watchability.py`; leaving them at
   baseline-6 values would contradict the record they describe.
5. **The first-seed honesty probe for `samples/4p1i` is recorded as vacuous and re-run** (§0.2),
   rather than counted as a pass on a game with no meetings in it.

---

## 12. Method + reproduction (all $0 against committed bytes, offline)

Every number in §§3-5 and §8 is recomputed from the committed bytes by a committed instrument.
The eight `AILIBI_*` lever exports of §0.2 must be present, because the reconstruction is
substrate-coupled (§10.1).

```bash
# The eight bars and the pooled arithmetic, per set and pooled:
uv run python scripts/measure_baseline.py --honesty     replays/samples/9p2i
uv run python scripts/measure_baseline.py --honesty     replays/ml_corpus/9p2i
uv run python scripts/measure_baseline.py --honesty     replays/samples/4p1i
uv run python scripts/measure_baseline.py --honesty     replays/ml_corpus/4p1i
uv run python scripts/measure_baseline.py --solvability replays/samples/9p2i    # and the other three

# Bars 1 and 2 come from the deduction cross-tabs in each set's committed eval report:
uv run python - <<'PY'
import json, pathlib
n = d = innocent = 0
for s in ("samples/9p2i", "ml_corpus/9p2i", "samples/4p1i", "ml_corpus/4p1i"):
    r = json.loads(pathlib.Path(f"replays/{s}/tournament-eval-report.json").read_text())
    c = r["deduction"]["ejectee_proof_cross_tab"]
    n += c["non_direct_accuracy"]["numerator"]
    d += c["non_direct_accuracy"]["denominator"]
    innocent += c["non_direct_ejections"] - c["non_direct_impostor"]
print(f"bar 1 pooled {n}/{d} = {n / d:.4f}; bar 2 pooled {innocent}")
PY

# The win split, re-derived from the MANIFEST winner column rather than quoted:
uv run python -c "
import pathlib, sys; sys.path.insert(0, 'scripts')
from _manifest_writer import parse_manifest
for s in ('samples/9p2i','ml_corpus/9p2i','samples/4p1i','ml_corpus/4p1i'):
    rows = parse_manifest(pathlib.Path(f'replays/{s}/MANIFEST.md').read_text()).values()
    rows = list(rows)
    imp = sum(1 for r in rows if r.winner.strip().upper() == 'IMPOSTORS')
    print(s, f'{imp}/{len(rows)} = {round(100 * imp / len(rows))}%')
"

# The floor-block gauges with their raw numerators:
uv run python -c "
from pathlib import Path
from eval.watchability import compute_watchability
for d in ('replays/samples/9p2i', 'replays/samples/4p1i'):
    for g in compute_watchability(Path(d)).supply_gauges:
        print(d, g)
"

# The four I-13 fixtures, re-read through the real loader:
uv run pytest -q tests/api/test_evidence_mechanisms.py
```

The recording itself is not reproducible at $0 — it is 300 hosted generations — but it is
re-runnable at the same slate by the two committed recorders:

```bash
# the §0.2 environment block, exported first, then per leg:
bash scripts/refresh_samples.sh   --full        --expect-levers <the eight>   # the samples sets
bash scripts/record_ml_corpus.sh  --set 9p2i    --expect-levers <the eight>   # the corpus sets
uv run python scripts/validity_gate.py <set> --expected-model Qwen/Qwen3.6-27B --require-zero-cost
```

**Cite this audit for the record's truth, never the PR body.** PR bodies quote first-cut numbers
and have already caused one downstream citation error in this repository's history.
