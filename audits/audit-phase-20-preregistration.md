# Phase-20 pre-registration — the falsifiability contract for the evidence-honesty record: instruments, baseline cells, bars, the decision rule (PROVISIONAL at the planning PR; pinned and ratified at Task 20.22)

**Date:** 2026-08-19 (planning PR). **Status:** PROVISIONAL — every baseline cell below is
REVIEW-DERIVED (measured by the 2026-08-19 review's session scripts over the committed
baseline-6 bytes at `b809b19c`; sources named beside each cell). Task 20.22 replaces each
cell with the committed pin from Task 20.14 (`eval/solvability.py`) and Task 20.15
(`eval/evidence_honesty.py`) — or with the already-committed pin where one exists
(`eval/deduction_metrics.py`, Task 19.14) — states every bar verbatim as
[PROPOSED — ratified at merge], and the owner ratifies by merging 20.22's PR. Amendments
after that are dated errata. The 18.4 label key applies: **[VERIFIED]** quoted from a
committed pin · **[REVIEW-DERIVED]** measured by the review, to be pinned · **[PROPOSED]**
a bar or rule the owner ratifies at 20.22.

**What is being pre-registered:** the instrument list (§2), the baseline cells (§3), the
primary bars (§4), the secondary observed-not-gated cells (§5), the decision rule (§6), the
co-intervention declaration (§7), the offline-counterfactual protocol (§8), and the record
order (§9). The memo is read VERBATIM by 20.34 (the counterfactual) and 20.36 (the record).

---

## 0. Verdict in one line

**Eight primary bars, every one computable from committed bytes by a committed instrument,
judge ONE adopting record: the non-direct conviction cell must become a real inference
channel (0.368 → ≥ 0.60) with the innocent-ejection count falling (79 → < 35), the three
honesty mechanisms must close (false self-placement < 5%; sole-flag precision ≥ 50%;
grounded sighting side 100%), the two bugs must be gone (fabricated completions 0;
adjacent-room STRONG ~0), and the four committed injustice fixtures must each flip —
measured on the new bytes against the baseline-6 cells, with the win split observed inside a
band and never gated, and the decision rule (§6) written before any lever exists.**

## 1. Why these cells, and why now

The Phase-19 close (`audits/audit-phase-19-close.md` §4.1) measured the deduction economy
as proof-lookup: conviction accuracy **1.000 where ejectee-specific proof exists (310/310
pooled)** and **0.368 where it does not (46/125)**, with **79/79 innocent ejections in the
non-direct cell** [VERIFIED: `tests/eval/test_deduction_metrics.py` pins the four sets'
cells]. The 2026-08-19 review located the mechanisms that make the non-direct cell fail and
measured each over the same bytes (`audits/review-2026-08-19/A/verdicts.md`,
`B/verdicts.md`). Phase 20 fixes those mechanisms behind levers and records once. These
cells are the before; the record produces the after; this memo is the contract between them.

## 2. The instruments

| id | instrument | owner module | status |
|---|---|---|---|
| I-1 | Proof-vs-inference conviction cells (direct / non-direct; innocent ejections by cell) | `eval/deduction_metrics.py` (19.14) | committed |
| I-2 | False crew self-placement rate (a spoken `whereabouts` whose room matches the speaker's true room at neither agent-tick N nor N−1) | `eval/evidence_honesty.py` (20.15) | new |
| I-3 | Sole-`alibi_vs_sighting` convicting precision (meetings whose ONLY strong flag is `alibi_vs_sighting`: ejections right / wrong) and the class impostor share vs base rate | 20.15 | new |
| I-4 | Grounded sighting side (share of resolvable spoken sighting sides the speaker's own record supports, ±1 agent tick) | 20.15 | new |
| I-5 | Fabricated completion lines (rendered "You completed X" with no completion event at any earlier tick) | 20.15 | new |
| I-6 | Adjacent-room STRONG share (STRONG `alibi_vs_sighting` whose two rooms are one doorway apart with ≤1 tick between) | 20.15 | new |
| I-7 | Movement-origin flags (`alibi_vs_sighting` whose sighting is the origin half of a `move A→B` line in the speaker's memory) | 20.15 | new |
| I-8 | Dev-marker contamination (turn free_text beginning with a bracketed marker; prompts containing one) | 20.15 | new |
| I-9 | Singular-persona prompts in a 2-impostor game | 20.15 | new |
| I-10 | Meetings with a participant inside a vent; reporters killed ≤ 3 ticks after their meeting | 20.15 | new (context cells) |
| I-11 | Free zero-witness kills declined; ghost-top impostor decisions (policy reconstruction, 0 mismatches vs recorded actions) | 20.15 | new (co-intervention cells) |
| I-12 | Solvability: killer-in-candidate-set containment; singleton rate and correctness; ejections landing on an already-cleared player | `eval/solvability.py` (20.14) | new |
| I-13 | The four 19.11 injustice fixtures (provenance-impossible sighting 9p2i s23 M1; content-vs-own-memory miss s12 M0; one-tick interval artifact 4p1i s41/s49; equal-weight conflict s41) | `tests/api/test_evidence_mechanisms.py` (19.11) | committed |

## 3. Baseline cells (baseline 6, `main` @ `b809b19c`)

Every cell is over the committed bytes; denominators quoted. REVIEW-DERIVED cells name the
review file that owns them; 20.22 replaces each with its 20.14/20.15 pin.

| cell | samples/9p2i | ml_corpus/9p2i | samples/4p1i | ml_corpus/4p1i | source |
|---|---|---|---|---|---|
| I-1 direct-proof accuracy | 68/68 | 213/213 | 9/9 | 20/20 | [VERIFIED] 19.14 pins |
| I-1 non-direct accuracy | 10/33 = 0.303 | 35/89 = 0.393 | 1/3 | 0/0 | [VERIFIED] 19.14 pins; pooled 46/125 = 0.368 |
| I-1 innocent ejections (all non-direct) | 23 | 54 | 2 | 0 | [VERIFIED] 19.14; pooled 79 |
| I-2 false crew self-placement | 148/723 = 20.5% | 402/2038 = 19.7% | 7/78 = 9.0% | 11/79 = 13.9% | [REVIEW-DERIVED] A/verdicts.md G-1 |
| I-3 sole-flag precision (pooled, four sets) | 12 right / 70 wrong = 14.6% | — | — | — | [REVIEW-DERIVED] A/verdicts.md G-2 |
| I-3 STRONG `alibi_vs_sighting` impostor share (dedup subjects, pooled) | 33/192 = 17.2% vs 25.3% base | (4/47 samples; 28/142 corpus) | — | — | [REVIEW-DERIVED] A/verdicts.md G-2 |
| I-4 grounded sighting side (resolvable sides) | 36.5% grounded (63.5% never perceived) | — | — | — | [REVIEW-DERIVED] A/verdicts.md G-2 |
| I-5 fabricated completion lines | 53/529 = 10.0% | 140/1528 = 9.2% | 15/65 = 23.1% | 14/64 = 21.9% | [REVIEW-DERIVED] A/verdicts.md G-3; B/verdicts.md C-2 |
| I-6 adjacent-room STRONG share | 148/234 = 63.2% (pooled) | — | — | — | [REVIEW-DERIVED] A/ideas-multi-agent-researcher.md |
| I-7 movement-origin flags | 7/76 | 30/233 | 0/3 | 1/1 | [REVIEW-DERIVED] A/verdicts.md G-9 (38/313 pooled) |
| I-8 marker contamination (turns; prompts) | 53/971; 246/1956 | 139/2726; 671/5502 | 0/117 | 0/120 | [REVIEW-DERIVED] A/verdicts.md G-25 |
| I-9 singular-persona prompts | 1956/1956 | 5502/5502 | n/a (1i) | n/a | [REVIEW-DERIVED] A/verdicts.md G-25 (b) |
| I-10 venting participant meetings; reporters killed ≤3 | 16/165; 27/165 | 50/463; 75/463 | 1/39; 5/39 | 2/40; 4/40 | [REVIEW-DERIVED] A/verdicts.md G-5 |
| I-11 free kills declined; ghost-top decisions | 190/415; 303/2461 | —; 555/6663 | —; 0/632 | —; 0/579 | [REVIEW-DERIVED] B/verdicts.md C-3; A/verdicts.md G-12 |
| I-12 solvability (pooled 9p2i+4p1i, 626 body meetings) | containment 581/626; singleton 109/626, correct 103/109; cleared-player ejections 61/354 | | | | [REVIEW-DERIVED] A/ideas-multi-agent-researcher.md |
| I-13 injustice fixtures | 4/4 exhibit the injustice | | | | [VERIFIED] 19.11 fixtures |

## 4. Primary bars [PROPOSED — ratified at 20.22]

Measured on the baseline-7 bytes by the same instruments, pooled over the recorded sets
with per-set cells shown:

1. I-1 non-direct conviction accuracy **0.368 → ≥ 0.60** (pooled), with no set below 0.50.
2. I-1 innocent ejections **79 → < 35** (pooled over the four sets).
3. I-2 false crew self-placement **20.5% → < 5%** (9p2i samples; every set < 8%).
4. I-3 sole-`alibi_vs_sighting` convicting precision **14.6% → ≥ 50%**; the class impostor
   share above the base rate.
5. I-4 grounded sighting side **→ 100%** of surviving STRONG sighting sides.
6. I-5 fabricated completion lines **→ 0** on every set.
7. I-6 adjacent-room STRONG share **63.2% → ≤ 5%**.
8. I-13 the four injustice fixtures: **each flips** (no longer exhibits its injustice under
   the adopted substrate).

## 5. Secondary cells (observed, reported, never gated)

The win split per set (baseline 6: impostor 34% 4p1i / 30% 9p2i) reported inside a
pre-registered band of ±15 points; I-7, I-8, I-9, I-10, I-11 reported; I-12 reported as the
y-axis (containment, singleton correctness, cleared-player ejections — the last expected to
fall); mean rendered lines per snapshot and reported-testimony retention (20.30's cells);
token cost per meeting call (the v4 map card and the meetings block add tokens — reported).

## 6. The decision rule [PROPOSED — ratified at 20.22]

**ADOPTED (the levers graduate; the ladder tip moves to baseline 7)** iff bars 1, 2, 3, 5,
6 and 7 are met AND at least three of the four fixtures flip AND bar 4 is met or the sole-flag
meeting count has fallen below 20 pooled (a class too small to judge precision is a class
that has closed). **FINDING (the levers stay toggles; the tip stays at baseline 6; the bytes
and the read are committed as the finding record)** otherwise. **Partial adoption** is
permitted only for levers whose own cell meets its bar AND whose offline counterfactual
(20.34) predicted it — the two bug-class levers (`task_completion_from_events` → bar 6;
`map_aware_arbitration` → bar 7) are the expected members; 20.34 fixes the final eligible
list before the record, and 20.36 may graduate that list even under a FINDING verdict for
the rest. No bar is re-priced after 20.22; a miss is reported as a miss.

## 7. The co-intervention, declared

Task 20.32 repairs the scripted impostor mover (C-3: all-target re-validation with a
proximity term; G-12: the dead-set reads meeting history) BEFORE the freeze. It is a defect
repair to the comparator every ML ruling was measured against, not a balance lever; it is
declared here because it changes game dynamics in the same record. Attribution of the
honesty bars therefore rests on the offline counterfactual (detector/render levers over
FROZEN baseline-6 bytes, §8) plus the record; the win split is secondary (§5). The policy id
stays `fsm-default`; the MANIFEST `git_sha` is the provenance of the repaired mover.

## 8. The offline-counterfactual protocol (20.34)

Before 20.35 starts: `scripts/counterfactual_phase20.py --sets all` re-runs the eight
levers' ON-path over the reconstructed inputs of all 300 committed games and publishes, in
`audits/audit-phase-20-counterfactual.md`: for every cell the instruments can compute
offline (I-3's class size and impostor share, I-4, I-5, I-6, I-7, I-8, I-9, the render cells,
the 79 wrongful-ejection meetings' surviving STRONG flags), the OFF and ON values; for every
cell it cannot compute offline (I-1 accuracy, I-2 after the trail exists, the fixtures'
model-dependent halves) an explicit "not predictable offline" with the reason; and the
abandon criteria for the smoke and the record (a validity-gate FAIL; a seed whose opening
defaults; a guard trip; a lever stamp mismatch).

## 9. The record order and the freeze

Freeze `agents/`, `meetings/`, `observation/`, `orchestrator/` and the prompt set at the
20.33 merge. Smoke (20.35): 5 seeds of 9p2i into a scratch dir; STOP-and-report. Record
(20.36): `replays/samples/9p2i` → `replays/ml_corpus/9p2i` → `replays/samples/4p1i` →
`replays/ml_corpus/4p1i`, each checkpoint-pushed per completed seed range; the corpus 9p2i
leg before any 4p1i leg because the non-direct cell has n=89 there vs n=33 in the samples —
power lives there. Model `Qwen/Qwen3.6-27B` non-thinking via Featherless, prompt set
`qwen3_6_27b` v4, lever slate all eight ON, `impostor_roll_call` OFF, `$0`.

## 10. Sign-off

Ratified by the owner's merge of Task 20.22's PR. Until then this memo is provisional. The
DAG enforces "pre-registration before the first fix": every lever task and the
co-intervention (20.32) depend on 20.22, so no substrate change can merge before the bars
are ratified.
