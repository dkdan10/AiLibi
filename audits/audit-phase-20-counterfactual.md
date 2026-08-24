# Phase-20 offline counterfactual — every predictable bar predicted on frozen bytes, before the record (Task 20.34)

**Status:** published BEFORE the smoke (20.35) and the record (20.36). The DAG enforces the order.
**Instrument:** `scripts/counterfactual_phase20.py`, $0, offline, no LLM call, 28 s over the 300
committed games.
**Reads against:** `audits/audit-phase-20-preregistration.md` §2 (instruments), §3 (baseline cells),
§4 (bars), §4.1 (the rare-event discipline), §5 (secondary cells), §6 (the decision rule), §8 (the
protocol this memo executes), §9 (record order), §10 (THE RATIFIED DECISION), §11 (the I-11
erratum). This memo **never re-prices a bar** (§10) and **proposes no graduation subset** (§6:
partial adoption is a per-lever VERDICT, never a partial graduation).

## 0. The headline, in one sentence

Of the 79 innocent ejections, **70 convicted on a STRONG flag naming the victim** and nine carried
none. On the frozen baseline-6 bytes the eight-lever slate strips that evidence from **67 of those
70** (95.7%), mints a new STRONG flag against **0 of the nine** that had none, and collapses the
STRONG `alibi_vs_sighting` class from **234 flags to 12** — but it does **not** reach bar 5
(10/12 = 83.3% grounded at tick, against a target of 100%) or bar 7 (6/12 = 50.0% adjacent, against
≤ 5%) **as rates**, because the denominator falls faster than the numerator. The offline table
therefore predicts **FINDING**, not ADOPTED, and names exactly which two bars it expects to miss and
why.

The 67 is a **per-meeting OFF/ON join**, not `79 − 3`: a wrongful ejection that carried no STRONG
flag cannot lose one, and a detector lever can mint one where there was none, so the subtraction
would be the wrong arithmetic in both directions. The script computes both directions and publishes
each with its own denominator (`E` rows in §4).

## 1. What this instrument is, and what it is not

Ruling R3 admits the scripted-mover repair (20.32) into the record as a declared co-intervention and
then names the price: the record alone can no longer attribute a delta to the honesty levers
(pre-registration §7). This table is the instrument that pays it. It holds the model, the mover, the
seeds and the recorded bytes constant and moves **only the detector and render rules**, so whatever
it shows is caused by the levers and nothing else. Detector-and-render-only is not a limitation of
the method here; it is the method.

It is **not** a projection of the record. Every ON number below is the frozen baseline-6 transcript
re-banded under the new rules. At the record the flags are minted inside live meetings whose agents
read different prompts, so the ON *denominators* here are the old population re-scored, not the
population baseline 7 will produce. Where that distinction changes how a bar should be read, this
memo says so on the row.

Three columns, and the third is only worth reading once the first two agree:

| column | what it is |
|---|---|
| **RECORDED-OFF** | the committed instrument (`eval.evidence_honesty`, `eval.solvability`) over the recorded bytes — this IS the ratified §3 baseline |
| **RECONSTRUCTED-OFF** | the same cell folded from re-derived inputs with all eight levers OFF |
| **ON** | the same reconstruction with the eight levers ON, toggled through each resolver's `env` parameter |

A cell whose two OFF readings disagree prints **no ON value**: the counterfactual would be measuring
the reconstruction rather than the lever, and that is a defect in the script, not a finding about the
bytes. The script says so in its own failure message and exits non-zero.

## 2. The command, the slate, the reproduction

```bash
uv run python scripts/counterfactual_phase20.py --sets all          # the table below
uv run python scripts/counterfactual_phase20.py --sets all --json   # the same table, machine-readable
uv run pytest -q tests/scripts/test_counterfactual_phase20.py       # the pins, incl. this memo's table
```

The slate is read off the substrate registry (`orchestrator.replay.TOGGLEABLE_SUBSTRATE_FLAG_KEYS`
less `impostor_roll_call`), never listed locally, so a lever registered at 20.33 cannot silently drop
out of the prediction: `task_completion_from_events`, `self_location_trail`, `movement_claim_shape`,
`grounded_prosecution`, `map_aware_arbitration`, `structured_turn_markers`, `meeting_outcome_memory`,
`coalesced_memory_render`. It is threaded as an argument. The script never assigns to `os.environ`,
never writes a replay and never calls a model; it refuses to start under a stale `AILIBI_*` export
and re-checks the ambient slate at exit.

## 3. The OFF column IS the committed baseline

Proven before any ON number is believed, and asserted in
`tests/scripts/test_counterfactual_phase20.py` rather than eyeballed here:

* every RECORDED-OFF cell equals its committed 20.15 / 20.14 pin — pooled `12/82`, `33/192`,
  `255/1017`, `124/234`, `154/234`, `148/234` (and `adjacent_any_gap` also 148), `38/313`,
  `192/3934` turns, `917/7932` prompts, `7932/7932` personas, `88/1888` completion rows, `544/626`,
  `126/626`, `114/126`, `83/354`;
* the RECONSTRUCTED-OFF leg re-derives **the recorded flag tuple on all 707 committed meetings** —
  every flag cell's two OFF readings are equal, digit for digit;
* the innocent-ejection enumeration reproduces the committed 19.14 non-direct split
  **23 / 54 / 2 / 0 = 79**, and independently re-derives the review's G-2 census: **70 of those 79
  rode a STRONG flag**, every one of them kind-sole `alibi_vs_sighting`.

**I-11 is excluded by §11's erratum.** The ratified cells are the frozen
`eval.evidence_honesty.RATIFIED_I11_CELLS`; the policy that produced them left the tree at the 20.32
mover repair, so a live-policy fold reports `impostor_targeting.reconstruction_mismatches > 0` by
construction. No ratified bar rides I-11. This script neither recomputes nor gates on it.

## 4. The pooled OFF/ON table

Every row is `numerator/denominator`. `—` means the cell has no reading in that column, with the
reason in the row's own note (§4.1 below). The evidence-label key is the pre-registration's, copied
rather than invented: **[VERIFIED]** recomputed from committed bytes by the command in §2;
**[INFERRED]** derived from a verified cell by stated arithmetic.

<!-- POOLED-TABLE-START -->

| cell | measure | OFF (baseline 6) | ON (all eight) | reading |
|---|---|---|---|---|
| I-3 | sole-flag convicting precision (per victim) | 12/82 | 1/4 | 14.6% → 25.0%; bar 4 asks ≥ 50% — a MISS, with §6's class-closed waiver applying separately (denominator 4 < 20) |
| I-3 | class impostor share (STRONG alibi_vs_sighting, dedup subjects) | 33/192 | 1/6 | 17.2% → 16.7% against a base rate of 22.9%; the class stays below chance |
| I-3 | living-voter base rate at those meetings | 255/1017 | 8/35 | 25.1% → 22.9%; the comparison base for the row above |
| I-4 | grounded sighting side (at tick) | 124/234 | 10/12 | 53.0% → 83.3%; bar 5 asks 100% — predicted MISS by two sides |
| I-4 | grounded sighting side (within +/-1 tick) | 154/234 | 12/12 | 65.8% → 100%; reported beside bar 5, never the bar |
| I-4 | grounded sighting side (within +/-2 ticks) | 160/234 | 12/12 | 68.4% → 100%; the production grounding tolerance, and the reason two survivors miss bar 5 |
| I-4 | resolvable sighting sides (of all STRONG sides) | 234/234 | 12/12 | every side resolves on both slates; the unresolvable remainder is zero |
| I-6 | adjacent-room STRONG share | 148/234 | 6/12 | 63.2% → 50.0%; bar 7 asks ≤ 5% — predicted MISS as a rate, though the count falls 148 → 6 |
| I-6 | adjacent-room STRONG share (un-gated adjacent_any_gap) | 148/234 | 6/12 | the two readings have NOT separated on this slate |
| I-7 | movement-origin flags | 38/313 | 88/363 | 12.1% → 24.2%; the class GROWS — the lever's price, §5 secondary, no bar |
| I-8 | marker contamination (turns) | 192/3934 | 0/3934 | 4.9% → 0; a predicted-exactly-zero cell, and therefore a §9 tripwire |
| I-8 | marker contamination (prompts) | 917/7932 | — | PROMPT-SET-COUPLED: a prompt re-renders only under a Jinja set |
| I-9 | singular-persona prompts | 7932/7932 | — | PROMPT-SET-COUPLED: the persona block is template bytes |
| I-5 | fabricated completion lines | 88/1888 | 0/1482 | 4.7% → 0 on every set; a predicted-exactly-zero cell, and a §9 tripwire |
| R | rendered memory rows per snapshot (mean) | 386907/7932 | 309625/7932 | 48.78 → 39.03 rows at the FULL eight-lever slate |
| R | rendered memory rows per snapshot (mean), less lever 7 | 386907/7932 | 312761/7932 | 39.43 rows with `meeting_outcome_memory` withheld: the decomposition, not a second headline |
| R | reported-testimony rows retained | 69535/386907 | 137996/309625 | 18.0% → 44.6%; testimony outranks routine co-presence |
| R | reported-testimony rows retained, less lever 7 | 69535/386907 | 133489/312761 | 42.7% with lever 7 withheld: the WHOLE lever is worth +1.9 points, not the gain |
| I-12 | containment (killer in the candidate set) | 544/626 | 544/626 | LEVER-INVARIANT by construction |
| I-12 | singleton candidate sets | 126/626 | 126/626 | LEVER-INVARIANT by construction |
| I-12 | singleton correct | 114/126 | 114/126 | LEVER-INVARIANT by construction |
| I-12 | ejections on an already-cleared player | 83/354 | 83/354 | LEVER-INVARIANT by construction |
| R | reported-testimony rows, <=4 living | 10890/69535 | 38084/137996 | 10,913 → 38,084 rows on the reconstruction: the band gains most |
| R | reported-testimony rows, 5-6 living | 47623/69535 | 84568/137996 | 47,719 → 84,568 rows |
| R | reported-testimony rows, >=7 living | 11022/69535 | 15344/137996 | 11,040 → 15,344 rows |
| E | innocent ejections still carrying a STRONG flag | 70/79 | 3/79 | 88.6% → 3.8% |
| E | innocent ejections whose STRONG flags were all alibi_vs_sighting | 70/79 | 3/79 | the kind-sole conviction bar 4 prices |
| E | innocent ejections that LOSE the STRONG flag they convicted on | 0/70 | 67/70 | **95.7% of the convictions that had evidence lose it** — a per-meeting join |
| E | innocent ejections that NEWLY carry a STRONG flag | 0/9 | 0/9 | the other direction: no lever mints a conviction where there was none |

<!-- POOLED-TABLE-END -->

`tests/scripts/test_counterfactual_phase20.py::test_the_memo_table_equals_the_scripts_output` parses
the table above back out and asserts every row against the script's own JSON — both directions, so a
memo row the script does not compute and a computed row the memo drops are both failures. One
changed digit is caught (a planted `148/234` → `149/234` is the perturbation that proves it bites).

### 4.1 The rows that carry a reading rule, and why

* **I-8 (prompts) and I-9 are PROMPT-SET-COUPLED.** Both cells read whole prompt bytes. A prompt
  re-renders only under a Jinja prompt set, and the default set at HEAD is the frozen `qwen3_5_9b`
  reference set while the committed bytes were recorded under `qwen3_6_27b` (AGENTS.md, "LLM
  providers"). A reconstruction under the wrong template family would measure the template, not the
  lever, so both are printed with their RECORDED value and no ON. The turn half of I-8 is *not*
  prompt-set-coupled — the transcript is frozen bytes — and is measured by parsing each recorded
  turn's audit markers back into typed annotations through `api.replay_loader`'s own repr-aware
  parser, which IS the `structured_turn_markers` ON shape over those bytes.
* **The render census counts one snapshot per RECORDED PROMPT, not per meeting-agent.** The
  registered census's unit is the recorded LLM call, and a meeting issues a different number of
  opening / reply / opt-in / ballot calls per agent. An agent's memory does not change inside a
  meeting (the fold lands at `MeetingApplied`), so its rendered view is constant across that
  meeting's calls, and the reconstruction weights the single render by the recorded per-agent call
  count. That makes the two OFF readings share one denominator — **7,932 snapshots, the recorded
  population exactly** — instead of a differently-weighted 3,934 stand-in. The residual is 313 rows
  on 386,907 (0.08%) and 137 testimony rows on 69,535 (0.20%), carried and not smoothed. The I-5
  completion fold is deliberately NOT weighted: it deduplicates by `(agent, observation_id)` across
  the whole game, so a repeated prompt is one row either way, and its OFF leg reproduces the recorded
  cell exactly (88/1888).
* **The render census IS the full eight-lever slate, with the seven-lever reading beside it.**
  `meeting_outcome_memory` ON re-tags a rendered testimony frame `[meeting N]`
  (`agents/memory/store.py::_render_reported_testimony`), which the instrument's OFF-shaped
  `_TESTIMONY_ROW` / `_RENDERED_ROW` patterns could not match — a tagged row silently left the
  budget. The fix landed in `eval/evidence_honesty.py`, the single home of that definition (the
  patterns now read `[meeting]` or `[meeting N]`, and nothing else changed), under the ratified scope
  amendment logged at pre-registration §11, **2026-08-24**. OFF-neutrality is proven rather than
  argued: the pre-widening patterns are re-stated inside
  `tests/eval/test_evidence_honesty.py::test_the_widened_meeting_frame_is_off_neutral` and asserted to
  count an OFF-shaped block identically (planted near-misses still rejected), and
  `test_no_committed_prompt_carries_a_tagged_meeting_frame` shows the committed 9p2i bytes carry
  **18,319 bare frames and zero tagged ones** — exactly the committed `testimony_rows_total` pin — so
  no recorded cell can move. The headline census is therefore the slate the record ships, and the
  withheld-lever leg is kept as its **decomposition**: 39.03 rows/snapshot at eight against 39.43 at
  seven, and 44.6% testimony retention against 42.7%. **Read that ±1.9 points as the WHOLE lever's
  marginal contribution, not as the frame tag's.** Once the patterns count `[meeting]` and
  `[meeting N]` identically the tag itself moves no count; what the withheld leg removes is all of
  `meeting_outcome_memory` at once — the retained `saw_vent` testimony content *and* the non-elastic
  `## Meetings so far:` block, which sits above the observations and displaces elastic rows under a
  tight budget (`agents/memory/store.py:512-530`). No offline instrument separates those three, and
  this memo does not pretend one does; a tag-only ablation would be a new instrument, not a reading
  of this one.
* **The testimony rows are reported per living-roster bucket, never blended.** The registered
  census splits them `≤4` / `5-6` / `≥7` because budget pressure differs across those populations
  and a retention gain confined to one band would otherwise hide inside an aggregate. It is not
  confined: on the reconstruction all three bands rise in absolute rows (10,913 → 38,084;
  47,719 → 84,568; 11,040 → 15,344), with the small-roster band gaining most. Both 4p1i sets carry
  zero testimony rows on either slate, which is why the census is never one blended number.
* **I-12 is lever-invariant by construction, not by measurement.** The solvability oracle reads the
  engine's kill and visibility record and the recorded ballots. No lever in the slate writes either
  offline, so ON equals OFF identically. It is reported because §8 names it, not because it moved.

## 5. Per-set, for the bars that carry per-set clauses

| cell | samples/9p2i | ml_corpus/9p2i | samples/4p1i | ml_corpus/4p1i |
|---|---|---|---|---|
| I-4 at tick, OFF → ON | 31/58 → 1/1 | 92/173 → 9/11 | 1/2 → 0/0 | 0/1 → 0/0 |
| I-6 adjacent, OFF → ON | 38/58 → 0/1 | 108/173 → 6/11 | 1/2 → 0/0 | 1/1 → 0/0 |
| I-5 fabricated, OFF → ON | 19/458 → 0/347 | 40/1311 → 0/1045 | 15/61 → 0/46 | 14/58 → 0/44 |
| I-8 turns, OFF → ON | 53/971 → 0/971 | 139/2726 → 0/2726 | 0/117 → 0/117 | 0/120 → 0/120 |
| render rows/snapshot, all eight ON | 51.13 → 40.77 | 50.84 → 40.71 | 15.47 → 12.17 | 15.99 → 12.64 |
| render rows/snapshot, less lever 7 | 51.13 → 41.33 | 50.84 → 41.08 | 15.47 → 12.17 | 15.99 → 12.64 |
| testimony retained, all eight ON | 18.3% → 47.9% | 18.3% → 44.5% | 0% → 0% | 0% → 0% |
| testimony retained, less lever 7 | 18.3% → 45.9% | 18.3% → 42.6% | 0% → 0% | 0% → 0% |
| innocent ejections still STRONG | 19/23 → 0/23 | 50/54 → 3/54 | 1/2 → 0/2 | 0/0 → 0/0 |

Three of the four per-set ON cells for I-4 and I-6 have a denominator of 0 or 1. Under §4.1's
granularity rule those are ADVISORY by an enormous margin and take no part in any verdict, in either
direction; they are printed because a suppressed denominator must never be left implicit.

The two render rows carry the same headline-plus-decomposition pair as the pooled table, so a per-set
comparison at the record is like-for-like; their OFF column is the RECONSTRUCTED leg (51.13, not the
recorded 51.10), which is the apples-to-apples reading against a reconstructed ON. Both 4p1i sets
render zero reported-testimony rows on either slate, so the two slates coincide there exactly — which
is the same fact the pooled bucket rows carry, and the reason the census is never one blended number.

### 5.1 The four I-13 injustice fixtures — the FLAG half, which IS computable offline

Bar 8 is four individual verdicts, and a fixture FLIPS when the meeting no longer exhibits its
injustice. Half of that question is frozen-byte arithmetic and is published here; the other half (the
ejection that followed) is not, and §7 says so. Anchors are the committed ones
(`tests/api/fixtures/evidence_mechanisms.py`); the 4p1i seed-41 meeting anchors two of the four.

| fixture | anchor | STRONG flags OFF → ON | STRONG flags naming the ejectee OFF → ON |
|---|---|---|---|
| (a) provenance-impossible sighting | samples/9p2i seed 23, M1 | 1 → 0 | 1 → 0 |
| (b) content-vs-own-memory miss | samples/9p2i seed 12, M0 | 1 → 0 | 1 → 0 |
| (c) one-tick interval artifact | samples/4p1i seed 49, M0 | 0 → 0 | 0 → 0 |
| (c) + (d) one-tick artifact / equal-weight conflict | samples/4p1i seed 41, M0 | 2 → 1 | 1 → 0 |

**Read them one at a time, as §4 bar 8 requires.** (a) and (b) lose their only STRONG flag outright:
the sighting that convicted an innocent no longer stands. (c)'s seed-49 anchor already carried **no**
STRONG flag OFF — its two recorded flags were WEAK — so the lever slate has nothing to remove there
and the fixture's flag half cannot move; whether it flips is entirely the ejection half. The seed-41
meeting is the interesting one and the best single exhibit in this memo: it goes 2 STRONG → 1, and
the survivor is **not** the flag against the ejected crewmate (1 → 0). That is fixture (d)'s
equal-weight conflict resolving in the intended direction — the grounded vent flag naming the real
impostor keeps its band while the sighting flag against the innocent loses it — which is exactly what
"equal weight" was the defect of.

**Prediction:** the flag half of (a), (b) and (d) moves the right way on frozen bytes; (c)'s flag
half cannot move at all. No fixture is predicted to FLIP on this evidence, because a flip is defined
on the meeting's outcome and the outcome is the half no offline instrument reaches.

## 6. The predicted verdict, bar by bar

Predictions, not summaries. Each row states the direction, the offline value with its denominator
where the instrument computes one, and the bar it is predicted against.

| bar | target (§4, ratified) | prediction | value, offline |
|---|---|---|---|
| 1 | I-1 non-direct accuracy 0.368 → ≥ 0.60 pooled | **NOT PREDICTABLE OFFLINE** | — |
| 2 | I-1 innocent ejections 79 → < 35 pooled | direction DOWN, magnitude **NOT PREDICTABLE** | the *evidence* under 67 of the 70 that had any is gone; the ballots are not |
| 3 | I-2 false self-placement 21.0% → < 5% | **NOT PREDICTABLE OFFLINE** | — |
| 4 | I-3 precision 14.6% → ≥ 50% pooled, class share above base rate | **MISS** on both halves — §6's class-closed waiver applies to the DECISION RULE, and does not turn the miss into a pass | precision 1/4 = 25.0% (target ≥ 50%); class share 1/6 = 16.7% against a base rate of 8/35 = 22.9%; the pooled denominator falls to 4, below the waiver's 20 |
| 5 | I-4 grounded sighting side → 100% at tick | **MISS**, by two sides | 10/12 = 83.3% (within ±1: 12/12 = 100%) |
| 6 | I-5 fabricated completion lines → 0 on every set | **MET**, on all four sets | 0/347, 0/1045, 0/46, 0/44 |
| 7 | I-6 adjacent-room STRONG share → ≤ 5% pooled | **MISS** as a rate, though the count falls 96% | 6/12 = 50.0%; 148 flags → 6 |
| 8 | I-13 four fixtures, individually | flag half published per fixture (§5.1); the **ejection half is not predictable** | (a) 1→0, (b) 1→0, (c) 0→0 (nothing to remove), (d) 2→1 with the innocent's flag the one that goes |

**Why bar 4 misses, and what §6 does with that.** Bar 4's own target is conjunctive — precision
≥ 50% pooled AND the class impostor share above the living-voter base rate — and the counterfactual
misses both (25.0% precision; 16.7% share against a 22.9% base rate). §10 requires a miss to be
reported as a miss, so it is reported as one. Separately, §6's decision rule accepts its bar-4 clause
when the pooled denominator of `per_victim_precision` has fallen below 20, and it falls to 4 — the
class has closed. Those are two different statements and this memo keeps them apart: **the bar is
MISSED; the decision rule's bar-4 clause is nevertheless satisfied by the class-closed waiver.**
Nothing here re-prices bar 4.

**Why bar 5 is predicted to miss.** `grounded_prosecution` bands an ungrounded sighting WEAK using
a ±2-tick grounding window; bar 5 reads the AT-TICK cell (`nearest == 0`). Two of the twelve
survivors are grounded at ±1 (the ±1 and ±2 readings are both 12/12) and therefore stand STRONG
while failing the bar's own cell. This
is a mechanism/bar mismatch, published as a prediction. §10 forbids re-pricing a bar after
ratification and this memo does not: the ±1 reading (12/12) is reported *beside* the bar, exactly as
§4 bar 5 instructs, and never in place of it.

**Why bar 7 is predicted to miss.** `map_aware_arbitration` demotes 140 of the 148 adjacent flags
(the eight it keeps sit two or more ticks inside their alibi window, which the detector's tick half
deliberately preserves). `grounded_prosecution` then demotes most of the rest of the class, so the
STRONG denominator collapses 234 → 12 while six adjacent flags survive both rules. **A count that
falls 96% and a rate that rises are the same fact seen twice.** §4.1's SUPPRESSED-NOT-FIXED label is
registered against the COUNT bars (5 and 6) and does not reach bar 7, which is a rate bar — so the
honest statement is the one made here: bar 7 is predicted to miss on the rate, and the absolute
adjacent-flag count is predicted to fall from 148 to single digits.

**The composite reading.** §6 makes ADOPTED conjunctive on bars 1, 2, 3, 5, 6 and 7 plus three of
four fixtures plus bar 4 (or its class-closed waiver). Bars 5 and 7 are predicted to miss offline and
bar 4 is predicted to miss on its own terms, so **this memo's prediction for the record is
FINDING**. That prediction is falsifiable in the useful direction: the
record mints its flags in live meetings under the new substrate, where the surviving-STRONG
population is not the frozen twelve. If bar 5 or bar 7 is MET at the record, the difference is
attributable to what the new substrate made agents *say*, and the record audit should say so.

## 7. What this instrument CANNOT predict offline, and why

**A flag that stops being minted is not a vote that changes.** Everything below is downstream of new
model behaviour and no offline arithmetic reaches it. Asserting otherwise would be the exact
overreach this phase exists to demonstrate against.

* **I-1 non-direct conviction accuracy, and the innocent-ejection count itself (bars 1 and 2).**
  These are bars about how agents vote once the substrate moves. The recorded ballots were cast under
  the old one. What this table can show — and does — is that the *evidence* 67 of the 70 wrongful
  ejections that HAD a STRONG flag rode is gone, and that none of the nine that had none gains one;
  whether the votes follow is the record's question.
* **I-2 false crew self-placement (bar 3).** The cell measures what the model *says*; `self_location_trail`
  changes what the model can *read*. There is no offline projection from the old prompts to the new
  answers, and the trail's coverage (does the record the roll-call asks for exist?) is a different
  cell from the rate.
* **The EJECTION half of the four I-13 injustice fixtures (bar 8).** The flag census at each anchored
  meeting IS computable from frozen bytes and is published in §5.1; the ejection that followed it is
  not. A fixture FLIPS when the meeting no longer exhibits its injustice, and "no longer exhibits"
  includes the vote.
* **The win split (§5 secondary).** Downstream of every one of the above, and un-attributable by
  construction while the mover repair rides the same record (§7 of the pre-registration).
* **I-8's prompt half and I-9.** Prompt-set-coupled — see §4.1.

## 8. Per-lever predictions (leave-one-out), and what no offline instrument supports

Lever interaction is **reported, not summed**. The per-lever censuses each lever task pinned
double-count: grounding the prosecution removes flags the map-aware arbitration would also have
removed, and the movement-claim shape removes a third overlapping set. The ON column above is ONE
shipping slate; the attribution below is the slate with one lever withheld, so each row's number is
that lever's *marginal* contribution on top of the other seven.

| leg | innocent ejections still STRONG (of 79) | STRONG alibi_vs_sighting class | marginal effect of the withheld lever |
|---|---|---|---|
| all eight OFF | 70 | 234 | — |
| all eight ON | 3 | 12 | — |
| ON less `grounded_prosecution` | 26 | 95 | **23 wrongful convictions and 83 flags** — the dominant lever |
| ON less `map_aware_arbitration` | 5 | 16 | 2 wrongful convictions and 4 flags |
| ON less `movement_claim_shape` | 2 | 9 | **−1** wrongful conviction and −3 flags: this lever NETS a conviction |

`movement_claim_shape` is the honest one to read carefully. Withholding it leaves *fewer* surviving
convictions, because re-indexing a mis-spoken origin at the record's own destination mints flags the
committed meeting did not have (I-7 grows 38/313 → 88/363, the direction 20.23's own census called
"the price"). The lever is still the right repair — a flag built on the origin half of a transition
the speaker's own memory contradicts is a manufactured flag — but its offline effect on the wrongful
ejection census is *negative by one*, and no reading of this table should claim otherwise.

**The levers no offline instrument supports, with the reason:**

* `self_location_trail` — its cell (I-2) is a model-output cell. The trail's *coverage* is pinned by
  20.24 beside the instrument; its *effect* is not offline-computable.
* `structured_turn_markers` — the turn half IS measured here (192/3934 → 0/3934), but the prompt half
  is prompt-set-coupled and the downstream effect (does a model reason better when audit strings stop
  appearing inside quoted dialogue?) is a model question.
* `meeting_outcome_memory` — supported on both seams. The *ingest* seam is the ON memory lineage
  carrying the testimony rows the OFF lineage drops; the *render* seam is now measurable too, and the
  decomposition rows price it: withholding this one lever moves the census 39.03 → 39.43
  rows/snapshot and testimony retention 44.6% → 42.7%. What it does NOT support is the downstream
  question — whether a model votes differently once a claim says which meeting it came from.
* `task_completion_from_events` — fully supported: I-5 falls to 0 on every set, on a denominator that
  is 78.5% of its baseline value (1482 of 1888), so §4.1's SUPPRESSED-NOT-FIXED threshold (below 10%
  of baseline) is nowhere near reached. The lever grounds the row rather than suppressing it.
* `coalesced_memory_render` — supported on the census: 48.82 → 39.03 rendered rows per snapshot at
  the full slate, with reported testimony rising from 18.0% to 44.6% of the surviving rows. The
  compression is this lever's; the retention shift is shared with the other render levers, which is
  why the census is a §5 secondary cell and no bar rides it.

**No graduation subset is proposed.** The ratified §6 rules that partial adoption yields a published
per-lever VERDICT and never a partial graduation, because a subset slate matches neither committed
record's stamp. This section is the narrative input to that per-lever verdict under either outcome;
it is not a shortlist.

## 9. Abandon criteria — operator STOP conditions

Read as written. Each is a mechanical check requiring no judgment call. Any one of them STOPS the run
and reports; the go/no-go on restarting is the owner's.

1. **A `scripts/validity_gate.py` FAIL on any leg.** STOP. (§8)
2. **A seed whose opening defaults** — the `(deadline_default)` watch item on the opening turn. STOP.
   An opening that never parsed leaves the chain dead and every ballot voting on a husk. (§8)
3. **A substrate stamp that does not equal the intended slate.** Run
   `orchestrator.replay.substrate_slate_mismatches` against the eight Phase-20 keys with
   `impostor_roll_call` OFF; a non-empty result STOPS the record before it spends an hour. (§8, §9)
4. **A guard trip** — any firewall or leak guard raising during the run. STOP. (§8)
5. **A cell-level tripwire: a cell this memo predicts to reach exactly 0 that is non-zero on the
   smoke seeds is an ABANDON at any n.** Exactly two cells are predicted to reach zero:
   * **I-5 fabricated completion lines** — predicted 0 on every set. One fabricated row on the smoke
     is a live-path defect in `task_completion_from_events`, not sampling noise: the ON rule mints a
     completion only from an engine event, so a fabricated row means the lever is not on the path.
   * **I-8 marker contamination in turn `free_text`** — predicted 0/3934. One marked turn on the
     smoke means `structured_turn_markers` is not reaching `MeetingManager._collect_turn`.
6. **NOT an abandon, explicitly:** a directional bar that merely misses on five smoke seeds. Five
   seeds cannot locate any bar in §4 — the n≥30 clause exists for precisely this reason (§4.1) — so a
   miss there is sampling noise. It is **recorded in the smoke report and carried forward** to the
   record audit, never acted on at the smoke.
7. **Also NOT an abandon:** bars 5 and 7 missing at the record. This memo predicts both to miss
   offline (§6). A prediction that comes true is evidence, not a stop condition; a prediction that
   comes true is exactly what makes the FINDING verdict readable.

## 10. The one instrument repair this task made, and the observation it did not

This task toggles the lever modules and never edits them (files-not-in-scope), and never re-implements
an instrument cell. One instrument defect had to be repaired at its source before the census could be
published at the slate the record ships; one further observation is recorded for the record audit
rather than patched.

1. **The render census's row patterns were OFF-shaped — repaired in the instrument, under a ratified
   scope amendment.** `eval.evidence_honesty._TESTIMONY_ROW` and `_RENDERED_ROW` matched the untagged
   `[meeting] CLAIM by` frame only, so with `meeting_outcome_memory` ON — where the frame becomes
   `[meeting N]` — both patterns silently stopped counting the row and the eight-lever census read
   far below the seven-lever one, the whole difference being *uncounted* testimony rather than shed
   rows. Publishing a seven-lever number in the record's place would have defeated §8's purpose, so
   the owner-delegated ruling widened the patterns **once, in the instrument module** (the single home
   of that definition), and nothing else; the amendment is logged at pre-registration §11,
   **2026-08-24**. The conditions it rode with are all met: OFF-neutrality proven by re-stating the
   pre-widening patterns in a test and asserting an identical count on an OFF-shaped block with
   planted near-misses, plus a byte-level scan showing the committed 9p2i recordings carry 18,319 bare
   frames and **zero** tagged ones; the full eight-lever census published as the §4.1 headline; and
   the seven-lever reading kept beside it as the lever-7 decomposition. No committed cell moved.
2. **`adjacent` and `adjacent_any_gap` do not separate on this slate** (both 6/12). §10 registered
   bar 7 on `adjacent` precisely because the two *can* separate once a lever moves the flags; on the
   frozen bytes under the full slate they still coincide. Not a defect — an observation the record
   audit should re-check on baseline-7 bytes rather than assume.

## 11. Reproduction

Everything above is recomputed from committed bytes by two commands, both offline and $0:

```bash
uv run python scripts/counterfactual_phase20.py --sets all
uv run pytest -q tests/scripts/test_counterfactual_phase20.py
```

The pytest file asserts the OFF column against the committed 20.15 / 20.14 pins, the enumeration
against the 19.14 innocent split, the environment purity before and after a full run, and this
memo's own table against the script's JSON — with a planted perturbation for each gate proving it
bites.
