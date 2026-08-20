# Phase-18 close — NO-FLIP: the default mover stays scripted, no baseline 7; zero EMERGENT among the fourteen pre-registered rulings; NO crew adoption (Task 18.28)

**Date:** 2026-08-01.
**Task:** 18.28 — the mover baseline record + the phase close (operator + owner, $0), executed on
the contract's **NO-FLIP path**: Task 18.27 read 18.26's committed evidence against locked
decision 4's §1.3 flip bar and ruled **FAIL on the whole slate** (PR #318, merged `d98b598` — the
owner's ratification, the 15.18 convention), so **no record is performed**. The ladder tip STANDS
at **baseline 6** (the 18.12 CREW-ONLY adopting record, merge `0c08758`, `Qwen/Qwen3.6-27B`,
`qwen3_6_27b` v3 × 4 templates, **thirteen levers ON** with `impostor_roll_call` OFF).
**Sets:** all four — `replays/samples/9p2i`, `replays/samples/4p1i`, `replays/ml_corpus/9p2i`,
`replays/ml_corpus/4p1i` — **byte-untouched** by this close and re-verified at HEAD (§2). The
corpus is the Q3-restored canonical canary denominator, re-grounded onto baseline 6 at 18.13 (§3).
**Untouched by design (the FLIP-path artifacts):** `eval/watchability.py` floor blocks (**no
baseline-7 block exists** — grep-proven, `_BASELINE_SUPPLY_FLOORS` holds exactly
baseline-2..baseline-6 and `_DEFAULT_BASELINE_ID` is `"baseline-6"`), the FLIP path's
BEFORE-column measure JSON (`audits/baseline6-final-measure.json` — never created; `audits/` holds
baseline2..baseline5 only, because the BEFORE column exists to attribute a record and no record
happened), and `agents/` + `training/` (frozen at 18.27's ruling).
**Grounding:** every number below is a fold over committed artifacts via the committed CLIs at
HEAD — `scripts/validity_gate.py`, `scripts/measure_baseline.py` core / `--funnel` /
`--watchability` / `--vj`, `scripts/verify_samples.sh` bare, `uv run pytest
tests/scripts/test_champion_flip_ruling.py`, `scripts/compute_next_task.py` — plus the three
module folds the 18.12 record added (`eval.deception_instruments`, `eval.kill_craft`,
`eval.off_menu`), two documented census folds, and the fresh canary-anchor computation, all with
runnable snippets in §10 (the 15.18 convention). Everything ran `$0`, offline, deterministic,
under a bare environment (zero `AILIBI_*` exports); the only network calls are the two read-only
remote queries named in §8/§10. Zero hand-computed figures except the labeled Wilson/z statistics,
whose inputs are quoted beside them.

**Verdict in one line:** Phase 18 **CLOSES with NO mover record** — the §1.3 flip bar's
conjunction (referee PASS **and** retained win edge) fails on **every arm of the ratified slate**
at the 18.26 real-LLM eval: the champion candidate `ea4bc955…` keeps the edge (26/50 = 0.52 vs the
same-seed FSM comparator 13/50 = 0.26, Δ **+0.26**) and fails the baseline-6 referee on both live
supply gauges (flags/meeting 0.93548 < 1.09091; testimony-backed conversion 0.36667 < its
population-relative derived floor 0.66882), and so does `bfd145cb…` (+0.30, conversion alone),
`6d327dcb…` (+0.12) and `7f73929d…` (+0.18367 at n=49) — **referee FAIL ×4, win edge ×4, zero
PASSes**, the Phase-17 starved-supply shape reproduced on a co-adapted slate at n=50 — so the
scripted FSM **stays the default mover**, the committed champion **stays opt-in and unswapped**
(sha `6d327dcb…`), **baseline 7 is NOT recorded**, and the ladder tip stands at baseline 6. On the
emergence axis the tally is **0 EMERGENT / 14 NOT-DEMONSTRATED** under the ratified conjunctive
discipline (ten rulings fail clause (a) or admit no delta; rulings 9 and 11 pass (a)/(b)/(d) and
fail only the unsatisfiable ablation clause — recorded as the phase's two named behavioral
findings N1/N2, learned-impostor kill placement at z = +3.370 and z = +4.321; rulings 13–14
unjudgeable as recorded), and the crew-adoption slot closes **NO-ADOPTION** (`0bf179b7…`
considered; the c1 pair null at n=49, McNemar exact p = 1.0). All four committed sets re-verify at
HEAD (validity gate **10/10 PASS** each; bare byte-identity clean, **0 drift over 300/300
replays**; the referee **PASSES at exact self-consistent floor equality on both canonical sets**),
the ruling pins re-run green (**10 passed**), the phase **computes complete on 18.28's merge**
(dispatchable `[18.28]` → `[]`, merged 31 → 32), and the canary-family cells are **re-anchored
fresh on the baseline-6 corpus denominator** — the one outstanding re-anchor this close owns —
with every cross-set z inside ±1.96 (max |z| = 1.143). The referee FAIL is the selection bar
working as designed: a co-adapted impostor's objective is to make convictions harder, and the
population-relative floor prices exactly that. The FAIL is the finding, recorded here.

---

## 1. The ruled path — the 18.27 ruling read at the close (the finding)

**The criterion (locked decision 4, the standing §1.3 bar carried from
`audits/audit-phase-17-close.md` §1.3 and quoted in `audits/audit-phase-18-flip-emergence.md`
§1.1):** a mover flips the default only if it closes `utility-es`'s two supply gaps **without
surrendering the edge** — clearing the supply floor AND its own derived conversion floor while
holding win rate at or above the same-substrate FSM's. *"The bar itself STAYS (owner charter, the
17.12 selection-bar-honesty ruling): a co-adapted impostor's objective is to make convictions
harder, and the floor pricing that is the instrument working — the FAIL is the finding, and any
future re-pricing of the bar is an owner decision, never an instrument edit."*

### 1.1 The evidence (committed: `training/reports/results-finalist-eval.jsonl` + `report-finalist-eval.md` §16.a)

Recorded at 18.26 on the real Featherless baseline-6 path, `Qwen/Qwen3.6-27B`, 9 arms × 50 seeds
(449 recorded seed-games), $0, every row `baseline_id: "baseline-6"`, stamp-verified against the
candidate artifact's own `stamp.json`, validity gate PASS on every impostor-side arm. **The
champion candidate put to axis 1 is `ea4bc955…`** (`coevo/intermediates/run-02-utility-lambda4/gen-2`
— the arm the phase already operationally froze as the frozen impostor champion; every other
finalist counts as archive for clause (d), flip audit §4.1).

| arm | witnessed (floor 0.03390) | flags (floor 1.09091) | conversion (derived floor) | referee | mean / median | impostor win | comparator | win edge |
|---|---|---|---|---|---|---|---|---|
| `ea4bc955…` (champion) | 0.15228 PASS† | **0.93548 FAIL** (−0.15543) | **0.36667 FAIL** vs 0.66882 (−0.30215) | **FAIL** | 48.90 / 50.15 | 26/50 = 0.52 | 13/50 = 0.26 | **+0.26** |
| `bfd145cb…` | 0.14778 PASS† | 0.90000 — UNRESOLVABLE (excluded) | **0.35099 FAIL** vs 0.69519 (−0.34419) | **FAIL** (conversion alone) | 47.24 / 48.00 | 28/50 = 0.56 | 13/50 = 0.26 | **+0.30** |
| `6d327dcb…` (incumbent control) | 0.22280 PASS† | **0.96914 FAIL** (−0.12177) | **0.44444 FAIL** vs 0.64559 (−0.20115) | **FAIL** | 51.15 / 63.95 | 19/50 = 0.38 | 13/50 = 0.26 | **+0.12** |
| `7f73929d…` (n=49) | 0.22000 PASS† | **0.82840 FAIL** (−0.26251) | **0.38926 FAIL** vs 0.75527 (−0.36601) | **FAIL** | 52.49 / 53.70 | 21/49 = 0.42857 | **12/49 = 0.24490** | **+0.18367** |
| `p18-fsm-comparator` | 0.04598 PASS† | 1.19745 PASS (+0.10654) | 0.55147 PASS vs 0.52250 (+0.02897) | **PASS** | 54.96 / 53.55 | 13/50 = 0.26 | — | — |

† The memo's own footnote: *"PASS on the floor; the gauge is UNRESOLVABLE for between-arm
discrimination on every arm (§2.2.i) — the PASS stands, and nothing in this ruling rests on it."*

The comparator is the **fresh same-seed scripted-FSM arm recorded beside the candidates at 18.26**
(`p18-fsm-comparator`: seeds 0–49, the five-field `fsm-default` stamp read back from bytes,
`opponent_absence_proven: true`, `crew_stamp_games: 0`, `learned_stamp_games: 0`, validity PASS) —
never the Phase-17 report's 18/50 = 0.36 (baseline-5, stale) and never the canonical
`replays/samples/9p2i` manifest's 15/50 = 0.30 (a different recording of the same seeds). The
pairing map is exact: the comparator's **full-50** cells pair the three full arms;
**`7f73929d…` pairs the 49-seed intersection, 12/49 = 0.24490, never 0.26** (seed 35 excluded,
§6.4 E2), which is the +0.18367 in the table. The cross-seed-set read against the full-50
comparator row (**+0.16857**, the unpaired figure this close's battery also reproduces as
+0.168571) is named in the memo only to be rejected, and is not used here.

Cross-checked at source (`report-finalist-eval.md` §16.a, which carries the ejection-accuracy and
stamp columns the flip audit's table elides): `ea4bc955` ejection accuracy 0.7108 (59/24 of 83),
witnessed 30/197; `bfd145cb` 0.6707 (55/27 of 82), 30/203; `6d327dcb` 0.7333 (66/24 of 90),
43/193; `7f73929d` 0.75000 (63/21 of 84), 44/200; comparator 0.8351 (81/16 of 97), 8/174.

**The AND, read (flip audit §3):** every candidate has the win edge (all four
`core.impostor_win_rate` values exceed their paired comparator, **+0.12 to +0.30**) and every
candidate fails the referee (`watchability.referee_passed: false` on all four; the comparator is
the only PASS). **No candidate satisfies referee-PASS AND win-edge. The conjunction fails on the
whole slate.**

**Consequence, ruled at 18.27 (A2) and standing at this close:** the scripted FSM stays the
default mover on every default-SELECTOR surface; the committed champion stays opt-in and unswapped
(`utility-es`, sha `6d327dcb…` — no finalist referee-dominates it: none passes the referee at all,
and the incumbent control carries the least-bad margin on BOTH live gauges, flags −0.12177 and
conversion −0.20115 against every alternative's −0.15543/−0.30215, −0.34419, and
−0.26251/−0.36601); `agents/tactical/learned/` does not move; **18.28 closes NO-FLIP**.
`tests/scripts/test_champion_flip_ruling.py` pins all of it from committed bytes — the axis-1
ruling re-derived per candidate row, the mechanics (witnessed noise above the 25% ceiling on all
nine arms; `bfd145cb…`'s flags 0.29291 > 0.27273), the F13 cell, the axis-2 tally, and the FAIL
branch itself: the default-selector surfaces still select the scripted FSM, the absent-stamp
fallback is untouched, and the opt-in artifacts are unswapped
(`committed_weights_sha256() == 6d327dcb…`, `committed_crew_weights_sha256() == bd6fdd0a…`). Those
pins re-ran green at this close (§2, **10 passed**).

### 1.2 The floor arithmetic (which floor failed, by how much)

The baseline-6 9p2i pins (`eval/watchability.py`, unchanged by this close, quoted by
`audits/audit-phase-18-baseline-6.md` §5) and the 16.11 population-relative rule:

```
witnessed_event_rate       >= 6/177   = 0.03389830508474576
flags_per_meeting          >= 180/165 = 1.0909090909090908
testimony_backed_conversion>= min(1.0, 0.5735294117647058 * (1.0909090909090908 / measured_flags_per_meeting))
                              # 78/136 baseline-6 conversion pin, population_relative_conversion=True
```

Per-arm derived floors, reproduced from the memo's §15 arithmetic block:

```
min(1.0, (78/136) * ((180/165) / 0.9354838709677419))   # ea4bc955 -> 0.6688179974
min(1.0, (78/136) * ((180/165) / 0.9))                  # bfd145cb -> 0.6951871658
min(1.0, (78/136) * ((180/165) / 0.9691358024691358))   # 6d327dcb -> 0.6455941960
min(1.0, (78/136) * ((180/165) / 0.8284023668639053))   # 7f73929d -> 0.7552711994
min(1.0, (78/136) * ((180/165) / 1.197452229299363))    # comparator -> 0.5224997156
```

The mechanism, stated the way §1.3 prices it (flip audit §4.2's closing paragraph): *"At baseline 6
the flag economy floor rose with the graduated meeting layer (0.50279 → 1.09091) and the learned
movers' supply stayed below it on every arm (0.828–0.969 vs the comparator's 1.197), which LIFTS
every arm's population-relative conversion floor (0.646–0.755) far above its measured conversion
(0.351–0.444) — the starved-supply mechanism of the Phase-17 FAIL, reproduced on a co-adapted
slate at n=50. The win edge, meanwhile, is real and larger than Phase 17's (+0.26 on the champion
vs +0.16 then)."* The floor is not a moved goalpost: it is the same population-relative derivation
the 16.11 re-anchor fixed, re-pinned at 18.12 from the canonical samples, and it clears on the
scripted comparator recorded beside the candidates.

### 1.3 What a future flip would need (the honest scoping)

- **The two gaps, at the baseline-6 economy.** A mover that flips must lift `flags_per_meeting` by
  **≥ +0.15543** (champion) to the 1.09091 supply floor and, having done so, clear the conversion
  floor its own supply then derives — at the champion's measured supply that floor is 0.66882
  against a measured 0.36667, a **−0.30215** gap; the same shape holds on every other arm
  (−0.12177/−0.20115, −0.34419, −0.26251/−0.36601) — while keeping the win rate at or above the
  same-substrate FSM's 0.26. Nothing in the slate closed either gap.
- **The bar STAYS as ratified.** Re-pricing it — including any response to the witnessed gauge's
  structural unresolvability — is an **owner decision outside the memo**, never an instrument
  edit. This close changes no floor, no gauge, and no verdict rule.
- **The witnessed gauge is structurally unresolvable at n=50, on all nine arms.** The 18.26
  pre-registered noise precondition (a gauge whose split-half noise exceeds 25% of its threshold
  reads **UNRESOLVABLE**, and only gauges clearing the precondition feed the axis-1 ruling) fails
  everywhere: the floor is the rare-event point estimate 6/177 = 0.03390, so its 25% ceiling is
  **0.00847**, while measured half-to-half noise runs **0.01479** (`c2-gen0`) to **0.08671**
  (`7f73929d…`) — **1.75× to 10.2× the ceiling**; the comparator's own reads 0.02299. The ratified
  three-gauge referee is therefore **effectively two gauges** for this ruling. `bfd145cb…`'s flags
  cell is also UNRESOLVABLE (split-half noise **0.29291** against the **0.27273** ceiling, a 7%
  overshoot — the only impostor arm to fail the precondition there), so its FAIL rests on
  conversion alone; its numeric flags miss (0.90000 < 1.09091) is reported, not counted.
  `testimony_backed_conversion` clears the precondition on **all eight arms that have meetings**
  (noise 0.00380–0.08357) and is the gauge the ruling reads most safely. UNRESOLVABLE is exactly
  what it says — not a PASS, not a FAIL, and not a reason to move anything. It routes to §6.1 L2.
- **F13, the selection-rule question, is closed as unsupported.** Hypothesis A (the ES trades
  evidence-supply for wins; runner-ups sit one step less far along the trade) predicted persistent
  runner-up gauge margins at n=50. All three pooled margins on the 49-seed intersection are
  **NEGATIVE** — witnessed −0.00650, flags −0.09189, conversion −0.03483 — and all three are
  noise-barred (witnessed and flags by both sides; conversion by the champion side), and **zero
  referee passes survive on any finalist arm at n=50**, including `7f73929d…`'s own n≤6 screening
  PASS. **A is REJECTED as unsupported**; B (n≤6 referee reads are noise) stands as the OPERATIVE
  reading without being a demonstrated claim of its own. **Consequence: no selection-rule defect is
  demonstrated, so no next-campaign/Phase-19 selection-rule FIX contract routes from F13.** One
  residual survives the within-lineage read (`ea4bc955…` vs `bfd145cb…`, the one lineage-held-constant
  pair): a conversion difference of **−0.02231**, exceeding `bfd145cb…`'s intersection noise
  (0.01504) while sitting inside `ea4bc955…`'s (0.09459) — one gauge wide, on one pair, recorded as
  an observation below claim grade (§6.1 L3).

---

## 2. The close's own instrument reads over the existing bytes (HEAD, this session)

The NO-FLIP close performs the same instrument battery the FLIP path would have — over the
existing bytes, with **no record** (the 17.17 "resist recording anything" discipline, inherited by
the 18.28 contract). The battery is the 18.12 record's shape (`audits/audit-phase-18-baseline-6.md`
§10) extended over all four committed sets. HEAD is `6ac4f59`; the working tree was clean and no
repo file was edited by the battery.

### 2.1 Hard validity gate + bare byte-verification — PASS everywhere (10/10, all four sets)

`validity_gate.py --expected-model Qwen/Qwen3.6-27B --require-zero-cost`, exit `0` with *"Validity
gate PASSED (all checks green)"* on every set:

| set | games | meeting rate (floor 0.60) | resolved meetings | provenance | byte-identical reconstruction |
|---|---|---|---|---|---|
| `replays/samples/9p2i` | 50 | 1.0 | 165 (0 unresolved) | `model='Qwen/Qwen3.6-27B'`, 4 prompt versions, substrate stamped exact on 50 games | 0 samples drifted |
| `replays/samples/4p1i` | 50 | 0.78 | 39 (0 unresolved) | same, exact on 50 games | 0 samples drifted |
| `replays/ml_corpus/9p2i` | 150 | 1.0 | 463 (0 unresolved) | same, exact on 150 games | 0 samples drifted |
| `replays/ml_corpus/4p1i` | 50 | 0.8 | 40 (0 unresolved) | same, exact on 50 games | 0 samples drifted |

All ten named checks are green on all four sets: `all_games_reach_game_over`,
`meeting_rate_and_resolution`, `no_duplicate_meeting_rows`, `no_tick_1_kills`,
`no_friendly_fire_kills`, `no_betrayal_ballots_or_accusations`, `no_railroaded_crew_ejections`,
`no_dangling_primary_reason_id`, `cost_and_provenance_exact`, `byte_identical_reconstruction`. The
behavioral zeroes at scale: **0 teammate-betrayal ballots** over 971 (samples 9p2i) and 2726
(corpus 9p2i) multi-impostor ballots; **0 railroaded crew rows** over 3346 and 8552 rendered crew
suspicions; **0 dangling `primary_reason_id`** over 971 / 117 / 2726 / 120 ballots.

**Bare byte-identity — all four sets clean.** `scripts/verify_samples.sh` run with zero `AILIBI_*`
exports (the wrapper's no-argument form for the canonical sets; the explicit-single-set arm for the
corpus, the path `replays/ml_corpus/README.md:333` documents), exit `0` on all three invocations:
*"All 50 samples verified clean"* (4p1i), *"All 50 samples verified clean"* (9p2i), *"All 150
samples verified clean"* (corpus 9p2i), *"All 50 samples verified clean"* (corpus 4p1i) —
**300/300 replays byte-identical**.

### 2.2 Selection referee — PASS at exact self-consistent floor equality (the canonical sets)

`measure_baseline.py --watchability --json` at the default `--baseline-id baseline-6` (the
committed canonical block since 18.12):

| set | `referee_passed` | `supply_floors_passed` | `integrity_ok` | mean | median |
|---|---|---|---|---|---|
| `replays/samples/9p2i` | **true** | true | true | **54.58** | 52.3 |
| `replays/samples/4p1i` | **true** | true | true | **4.70** | 0.75 |

| set | gauge | measured (numerator) | floor | passed |
|---|---|---|---|---|
| 9p2i | `witnessed_event_rate` | 0.03389830508474576 (**6/177**) | 0.03389830508474576 | true |
| 9p2i | `flags_per_meeting` | 1.0909090909090908 (**180/165** = 96 persisted vent + 84 re-derived transcript) | 1.0909090909090908 | true |
| 9p2i | `testimony_backed_conversion` | 0.5735294117647058 (**78/136**) | 0.5735294117647058 | true |
| 4p1i | `witnessed_event_rate` | 0.01639344262295082 (**1/61**) | 0.01639344262295082 | true (rare-event ADVISORY, the 15.19 rule) |
| 4p1i | `flags_per_meeting` | 0.41025641025641024 (**16/39**) | 0.41025641025641024 | true |
| 4p1i | `testimony_backed_conversion` | 0.3 (**9/30**) | 0.3 | true |

Exact equality on every gauge is the derivation self-consistency the 16.11 population-relative
re-anchor guarantees — **these ARE the bytes the baseline-6 floors were pinned from at 18.12**, and
nothing has moved since. This is the statement the referee makes at this close, and its scope is
the canonical samples.

**Beside it, an honest cross-population read: the corpus scored against the samples-pinned floors.**
`measure_baseline.py replays/ml_corpus/9p2i --watchability --json` reads `referee_passed: false` on
**one** gauge — `witnessed_event_rate` **12/505 = 0.023762** vs the samples-pinned **6/177 =
0.033898**, a shortfall of −0.0101 — while `flags_per_meeting` **576/463 = 1.24406** clears the
floor (1.1404×) and `testimony_backed_conversion` **239/394 = 0.60660** clears its
population-relative derived floor 0.50292 (+0.10367), with mean 55.26 / median 54.45, **above** the
samples' 54.58. Corpus 4p1i PASSES (`referee_passed: true`, mean 8.22; its lone zero-witnessed
gauge, 0/55, is ADVISORY by the rare-event rule). **This judges nothing.** The baseline-6 floor
block is record-pinned to the canonical **samples** set by construction, the corpus is a different
150-game population that was never the pin source, and no committed record reads the referee on the
corpus — the 17-close's §9 battery never ran it, and the 18.13 corpus record carries no referee
verdict. The read is **first-taken here, informational, recorded as-is and not repaired**; the
gauge that misses is the same rare-event channel the 15.19 rule already marks fragile (12 events
over 505 kills). It is not a canary, not a defect, and not a contradiction of the referee PASS
above, whose scope is the canonical sets.

### 2.3 Core R-gate + information funnel — byte-stable against the 18.12 record

| cell | samples 9p2i | samples 4p1i | corpus 9p2i | corpus 4p1i |
|---|---|---|---|---|
| games_total | 50 | 50 | 150 | 50 |
| crew / impostor wins | 35 / 15 | 33 / 17 | 112 / 38 | 39 / 11 |
| **impostor_win_rate** | **0.30** | 0.34 | **0.25333** | 0.22 |
| tick_budget_reached | 0 | 0 | 0 | 0 |
| reason_histogram | `{EJECT 31, PARITY 15, TASKS 4}` | `{TASKS 23, PARITY 17, EJECT 10}` | `{EJECT 106, PARITY 38, TASKS 6}` | `{EJECT 20, TASKS 19, PARITY 11}` |
| **r1_eject_decided_wins** | **31** (31/50 = 0.62) | 10 | **106** (106/150 = 0.7067) | 20 |
| total / impostor / crew ejections | 101 / 78 / 23 | 12 / 10 / 2 | 302 / 248 / 54 | 20 / 20 / 0 |
| **ejection_accuracy** | **0.77228** (78/101) | 0.83333 | **0.82119** (248/302) | 1.0 |
| meeting_rate / resolved | 1.0 / 165 | 0.78 / 39 | 1.0 / 463 | 0.8 / 40 |
| accusation_claim_ece (n) | 0.26614 (778) | 0.29720 (107) | 0.27140 (2188) | 0.25880 (108) |
| **vote_ballot_ece** (n) | **0.16863** (520) | 0.08778 (27) | 0.12325 (1578) | 0.04778 (45) |

Every canonical-set cell reproduces `audits/audit-phase-18-baseline-6.md` §4 exactly — **R1 31/50,
ejection accuracy 78/101 = 0.7723, impostor win 0.30** — the sets are byte-stable since the record.

**Funnel** (set-level rows, `per_meeting` elided). The canonical 9p2i rows reproduce the record's
§3 exactly: report meetings **151**, killer in candidate set **132**, killer accused **92**, report
ejections **87**, votes outside the small set **18**, reporter ejected (innocent) **2**, killer
self-reported **0**; candidate-set median 2.0 / mean 2.6159; hard clue held 120; vent witnessed 93;
last seen with killer 50; killer at scene 30; kill witnessed 6; structured vent observed 93;
small-set ejections 56. The corpus carries the same signature at scale — report meetings 411,
killer in set 348, killer accused 245, report ejections 250, votes outside 57, kill witnessed 12,
**`reporter_ejected_innocent` 6 of 250 report-ejections = 2.4% against the samples' 2 of 87 =
2.3%**: the same precision cost the record adopted, reproducing on the independent corpus. The
4p1i pair (samples / corpus): report meetings 35 / 29, killer in set 35 / 29, killer accused
27 / 24, votes outside the small set 0 / 0, reporter ejected 0 / 0, killer self-reported 0 / 0.

### 2.4 The V&J instruments — identical to the record where the record read them

| instrument | 18.12 record read (samples 9p2i) | **this close, samples 9p2i (HEAD)** | corpus 9p2i | corpus 4p1i |
|---|---|---|---|---|
| provenance-sum breaches / rows | 0 / 4550 | **0 / 4550** | **0 / 11888** | 0 / 139 |
| rendered-row mismatches / rows | 0 (from 459 at baseline 5) | **0 / 4550** | **0 / 11888** | 0 / 139 |
| convictions (zero-flag, rate) | 101 (11, 0.1089; 3 crew / 8 imp) | **101 (11, 0.10891; 3 crew / 8 imp)** | 302 (27, 0.08940; 1 crew / 26 imp) | 20 (0, 0.0) |
| citation compliance | 520/520 = 1.000 | **520/520 = 1.0** | **1574/1578 = 0.99747** | 45/45 = 1.0 |
| coerced zero-flag markers (J2) | — | **1** | 1 | 0 |
| nulled reason-id / observation-id markers | — | 2 / 0 | 1 / 2 | 0 / 0 |
| whereabouts lies detected (rate) | 50 | **50** (0.05931) | 147 (0.06176) | 1 (0.01190) |
| roll-call coverage mean (crew / impostor) | 0.9958 / 0.4545 | **0.86284 (0.99576 / 0.45455)** | 0.86396 (0.99698 / 0.46544) | 0.7 (0.9875 / 0.125) |
| echo ballots / within-meeting echo rate | — | **0 / 0.0** (971 voice ballots) | 0 / 0.0 (2726) | 0 / 0.0 (120) |
| turn / observation citations (dangling) | — | 478 (0) / 156 (0) | 1438 (0) / 495 (0) | 35 (0) / 21 (0) |
| distinct-1 / distinct-2 | — | 0.09441 / 0.33247 | 0.05454 / 0.21821 | 0.24869 / 0.55432 |

The fourth set, `replays/samples/4p1i`, is elided from the table for width and reads clean
throughout: 39 meetings, 12 convictions, zero-flag 0 (0.0), breaches **0 / 133**, rendered-row
mismatches **0 / 133**, citation compliance **27/27 = 1.0** (22 turn + 12 observation citations, 0
dangling), coerced markers 0, echo rate 0.0 over 117 voice ballots, whereabouts lies 3 (0.03488),
roll-call coverage 0.73504 (crew 1.0 / impostor 0.20513).

Every canonical 9p2i cell reproduces the record audit's §2/§4 reads exactly. **The one instrument
not at unity anywhere is corpus citation compliance: 1574/1578 = 0.99747** — four EJECT ballots on
the 150-game corpus carry no citation, against 0 on all three other sets. No committed record
carries a corpus citation-compliance cell at baseline 6 (18.12 recorded 520/520 = 1.000 on the
samples; the 18.13 corpus record does not read it), so this is **first-noticed at this close**,
recorded as a finding and **not repaired** (§9).

**The two census folds** (the cells the CLIs do not emit directly; snippet in §10):

*Fold 1 — `compute_supplied_channel_conversion`, the genuine-class SUCCESSOR (the canary-eligible
cell):*

| channel | samples 9p2i | samples 4p1i | corpus 9p2i | corpus 4p1i |
|---|---|---|---|---|
| witnessed-vent | 68/76 | 9/10 | 213/242 | 20/20 |
| sighting-contradiction | 2/2 | 1/1 | 6/9 | 0/0 |
| whereabouts-lie | 5/7 | 0/0 | 26/37 | 0/0 |
| **TOTAL (per-meeting union)** | **70/79 = 0.88608** | **10/11 = 0.90909** | **222/259 = 0.85714** | **20/20 = 1.0** |
| legacy alibi (reported column only) | 3/4 = 0.75 | 1/1 = 1.0 | 18/28 = 0.64286 | 0/0 = None |

The samples cell reproduces the record's 70/79 = 0.8861 exactly. **All three supplied channels are
non-empty on both 9p2i sets** — the whereabouts-lie channel, empty on the baseline-5 samples (0/0
at the 17-close), now supplies 7 (samples) / 37 (corpus): the whereabouts-exemption graduation
feeding the successor instrument. The LEGACY alibi cell reads non-zero on three of four sets — its
first sustained non-zero supply — and stays a labeled reported column, never a canary.

*Fold 2 — `compute_conversion_report` over the 9p2i samples games (the HEAD conversion partition):*
total ejections 101, impostor ejections 78, ejection accuracy 0.77228, impostor-accused meetings
134 with 78 conversions (0.58209), **skips 451, correct 321, missed 129** (= 41 impostor-voter + 1
invalid-target + **87 threshold inversions**), **coerced 1** (the J2 bucket), unclassified 0,
teammate-coerced 0. The partition moved off the baseline-5 block exactly as it does at every
substrate change: coerced **2 → 1**, inversions **98 → 87**, impostor voters 41 unchanged. This is
a fresh fold over the committed baseline-6 bytes, not a stored block.

### 2.5 The Phase-18 instrument tier (the reads the 17-close table did not have)

Module folds per `audits/audit-phase-18-baseline-6.md` §10 — `eval.deception_instruments`,
`eval.kill_craft`, `eval.off_menu`:

| Tier-A deception cell | samples 9p2i | samples 4p1i | corpus 9p2i | corpus 4p1i |
|---|---|---|---|---|
| meetings_total / impostor accusations | 165 / 201 | 39 / 38 | 463 / 549 | 40 / 39 |
| **frame_attempts** (frame-attempt meetings) | **201** (161) | 38 (38) | **549** (437) | 39 (39) |
| impostor self-accusations | **0** | **0** | **0** | **0** |
| **teammate_accusations** | **0/201** | 0/38 | **0/549** | 0/39 |
| frame conversions | 11/161 = 0.06832 | 1/38 = 0.02632 | 23/437 = 0.05263 | 0/39 = 0.0 |
| **false_vouches_total** | **34** | 0 | **105** | 0 |
| … saw_player (obs, rate) | 20/202 = **0.09901** | 0/10 | 74/602 = 0.12292 | 0/6 |
| … corroborations (rate) | 14/56 = 0.25 | 0/1 | 31/176 = 0.17614 | 0/1 |
| … grounded / fabricated (share) | **14 / 4 (0.77778)** | 0 / 0 | 47 / 16 (0.74603) | 0 / 0 |
| alibi fabrication total / survived (rate) | 22 / 19 (0.86364) | 7 / 6 (0.85714) | 77 / 59 (0.76623) | 4 / 4 (1.0) |
| deflection: accused / survivals / active | 148 / 70 / 67 | 31 / 22 / 22 | 416 / 173 / 152 | 35 / 15 / 15 |
| … effective / named-target / third-party | 23 / 8 / 15 | 1 / 1 / 0 | 69 / 18 / 51 | 0 / 0 / 0 |

The canonical 9p2i row reproduces the record audit's §2 cells exactly (frame attempts 201 over 165
meetings, self-accusations 0, false vouches 34 with grounded 14 / fabricated 4, grounded-share
0.778, saw_player rate 0.099). **Teammate immunity holds at zero on every set** — 0 teammate
accusations over 827 impostor accusations pooled: the 7.12 firewall, still live.

| kill-craft / off-menu cell | samples 9p2i | samples 4p1i | corpus 9p2i | corpus 4p1i |
|---|---|---|---|---|
| **kills_total / crew_witnessed** | **177 / 6** | 61 / 1 | **505 / 12** | 55 / 0 |
| co-present histogram | `{0: 177}` | all-zero | all-zero | all-zero |
| mean one-hop witnessed / unwitnessed | **2.33333 / 0.83041** | 1.0 / 0.2 | 2.75 / 0.84787 | None / 0.25455 |
| point-biserial (within one hop) | **0.23833** | 0.22688 | 0.25852 | None |
| point-biserial (co-present) | None (structural zero) | None | None | None |
| impostor decisions / **off_menu_total (rate)** | 2461 / **0 (0.0)** | 632 / **0 (0.0)** | 6663 / **0 (0.0)** | 579 / **0 (0.0)** |
| action entropy IMPOSTOR (agents, decisions, cond) | 100, 2461, 0.70691 | 50, 632, 0.49086 | 300, 6663, 0.65258 | 50, 579, 0.52932 |
| action entropy CREWMATE (agents, decisions, cond) | 350, 8136, 0.87895 | 150, 1584, 0.65293 | 1050, 22095, 0.86932 | 150, 1489, 0.64083 |

The off-menu instrument's own `scope_note` governs its reading: *"The menu-bounded champion is
on-menu by construction (off-menu rate 0 always), so this instrument is VACUOUS for the champion
and meaningful only for free-policy-family recordings … FSM-generated bytes are the all-on-menu
fixture (rate 0)."* All four committed sets are `fsm-default` mover bytes, so the all-on-menu
reading is the expected one. The entropy point estimates are **reported, not judged** — the
`ActionEntropyCells` per-agent variance contract remains unlanded (§6.1 L9).

**The vent-variant live yield reproduces the record's state.** A `kind` census of each set's
committed `tournament-eval-report.json` (supplementary to the referee's re-derived
`flags_per_meeting` numerator, which stays the authoritative supply number) reads: `vent_sighting`
96 / 11 / 313 / 20; `alibi_vs_sighting` 76 / 3 / 233 / 1; **`alibi_vs_physical` (the grounded-vent
variant) 6 / 0 / 36 / 0**. The samples' **6** is identical to the 18.12 record's own first-live-yield
read, whose disposition governs here: *"This lands **one below** the pre-registered **[7, 28]**
sanity bracket … a REPORTED near-miss of the band's lower edge, not a banded canary."* This is that
recorded state reproducing at HEAD, **not a new fire**. The corpus carries **36 over 150 games** =
12.0 per 50 games, comfortably inside the bracket at the band's 50-game unit — independent evidence
that the samples' 6 is a small-sample low draw and the mechanism is healthy.

---

## 3. The canary anchors on the baseline-6 corpus denominator (the re-anchor this close owns)

**No canary is judged at this close**: the bands judge a RECORD against a pre-registered anchor, and
the NO-FLIP path records nothing. What this close owns is the outstanding re-anchor the 18.13
verification flagged, stated in the 18.28 contract verbatim:

> The 17.17 contract's "resist recording anything on the NO-FLIP path" discipline holds. One
> outstanding re-anchor this close owns (the 18.13 verification flagged it): the canary-family
> cells (R1 eject-decided share, the genuine-class successor, roll-call coverage, whereabouts-lie
> mints, ejection accuracy, impostor win) were never re-anchored on the restored baseline-6 corpus
> denominator — this close's §0 pre-registration derives its bands from the baseline-6 corpus,
> computing the anchors fresh.

The flag entered at commit `bfd8a62` (2026-07-21, the corpus-record fold-in). The 17-close's §3
anchors were computed on the **baseline-5** corpus, whose 9p2i set carried 541 meetings; the 18.13
re-record's carries **463**. Both the anchor and the denominator moved, so the family is recomputed
here from the restored denominator, from the same `eval/` folds `scripts/measure_baseline.py`
wires — every cell equals the §2 CLI output cell-for-cell.

**These are ANCHORS, not pre-registrations.** Pre-registration is a §0-block act of the record that
uses them (the 15.18 discipline), before its first recorded seed — and this close records nothing.

### 3.1 The corpus cells (150-game 9p2i: 463 meetings, 302 convictions, `fsm-default` movers)

Non-proportion cells (per-meeting fmeans — no Wilson CI applies, stated rather than faked):

| cell | corpus 9p2i | samples 9p2i (continuity) |
|---|---|---|
| roll-call coverage mean | 0.8640 | 0.8628 |
| … crew decomposition | 0.9970 | 0.9958 |
| … impostor decomposition | 0.4654 | 0.4545 |
| whereabouts lies detected (count) | 147 | 50 |
| citation compliance | **1574/1578 = 0.99747** | 520/520 = 1.000 |
| provenance-sum breaches | 0 / 11888 rows | 0 / 4550 |
| zero-flag conviction rate | 27/302 = 0.08940 | 11/101 = 0.10891 |

Proportion cells, with the corpus Wilson 95% score interval and the cross-set pooled
two-proportion z (both computed numerically in the anchor script, never by hand — §10):

| cell | corpus k/n | rate | Wilson 95% CI | samples k/n | rate | z |
|---|---|---|---|---|---|---|
| **R1 eject-decided win share** | **106/150** | **0.7067** | **[0.6294, 0.7736]** | 31/50 | 0.6200 | −1.143 |
| **genuine-class successor** (named canary cell) | **222/259** | **0.8571** | **[0.8093, 0.8945]** | 70/79 | 0.8861 | +0.657 |
| ejection accuracy | 248/302 | 0.8212 | [0.7740, 0.8603] | 78/101 | 0.7723 | −1.082 |
| impostor win rate | 38/150 | 0.2533 | [0.1905, 0.3285] | 15/50 | 0.3000 | +0.648 |
| whereabouts-lie mint rate | 147/2380 | 0.0618 | [0.0528, 0.0722] | 50/843 | 0.0593 | −0.255 |
| roll-call coverage (pooled crew) | 2035/2042 | 0.9966 | [0.9929, 0.9983] | 723/726 | 0.9959 | −0.272 |
| roll-call coverage (pooled impostor) | 342/684 | 0.5000 | [0.4626, 0.5374] | 120/245 | 0.4898 | −0.274 |
| roll-call answer rate | 2377/2726 | 0.8720 | [0.8589, 0.8840] | 843/971 | 0.8682 | −0.303 |

**Every cross-set z is inside ±1.96** (largest |z| = **1.143**, on R1) — the two same-substrate
populations agree, so corpus-anchored bands can honestly judge future same-shape records. (The
pooled crew/impostor rows are the proportion FORM of roll-call coverage — Σ placed / Σ living over
meetings — supplied so the coverage family has a Wilson-able cell; the per-meeting fmean above is
the cell the record audits quote.) Successor channel split on the corpus: witnessed-vent 213/242,
sighting-contradiction 6/9, whereabouts-lie 26/37, the per-meeting union deduping to 259 supplied /
222 converted; legacy alibi 18/28 = 0.6429, reported column only.

### 3.2 The band arithmetic — at the corpus anchor's own n

For each proportion canary: the largest k at the anchor's own n whose pooled two-proportion z
against the anchor is ≤ −1.96 (the REGRESSION arm's firing point), and the implied minimal
detectable drop.

| canary | anchor k/n | rate | band-fire threshold | min detectable drop |
|---|---|---|---|---|
| **R1 eject-decided win share** | 106/150 | 0.7067 | **≤ 89/150 = 0.5933 (z = −2.058)** | **11.3 pp** |
| **genuine-class successor** | 222/259 | 0.8571 | **≤ 205/259 = 0.7915 (z = −1.963)** | **6.6 pp** |
| ejection accuracy | 248/302 | 0.8212 | ≤ 228/302 = 0.7550 (z = −1.991) | 6.6 pp |
| impostor win rate | 38/150 | 0.2533 | ≤ 24/150 = 0.1600 (z = −1.996) | 9.3 pp |
| whereabouts-lie mint rate | 147/2380 | 0.0618 | ≤ 116/2380 = 0.0487 (z = −1.967) | 1.3 pp |
| roll-call coverage (pooled crew) | 2035/2042 | 0.9966 | ≤ 2025/2042 = 0.9917 (z = −2.047) | 0.5 pp |
| roll-call coverage (pooled impostor) | 342/684 | 0.5000 | ≤ 305/684 = 0.4459 (z = −2.004) | 5.4 pp |
| roll-call answer rate | 2377/2726 | 0.8720 | ≤ 2327/2726 = 0.8536 (z = −1.968) | 1.8 pp |

The two named canary cells land on **exactly the same power as the 17-close's baseline-5 corpus
anchors — R1 11.3 pp, successor 6.6 pp — despite both the anchor and the denominator moving** (R1
0.620 → 0.7067, successor 0.8755 → 0.8571; meetings 541 → 463). The baseline-6 corpus is a
like-for-like replacement denominator for band purposes.

For contrast, the same arithmetic at the 50-seed samples anchor — the underpowered regime the
17-close named, standing verbatim on the new bytes: R1 31/50 = 0.6200 fires only at ≤ 21/50 = 0.4200
(z = −2.002), a **20.0 pp** drop; successor 70/79 = 0.8861 at ≤ 60/79 = 0.7595 (z = −2.083), 12.7
pp; ejection accuracy 78/101 at ≤ 65/101 (z = −2.012), 12.9 pp; impostor win 15/50 at ≤ 6/50
(z = −2.210), 18.0 pp; whereabouts-lie mint 50/843 at ≤ 32/843 (z = −2.038), 2.1 pp; roll-call
pooled crew 723/726 at ≤ 715/726 (z = −2.148), 1.1 pp; pooled impostor 120/245 at ≤ 98/245
(z = −2.000), 9.0 pp; answer rate 843/971 at ≤ 812/971 (z = −1.982), 3.2 pp. The corpus denominator
nearly halves the R1 arm's blind spot. **The next adopting/close record pre-registers from §3.2,
quoting the samples as the continuity anchor** — the Q3 pairing, operative.

---

## 4. The phase's evidence chain (committed, provenance-stamped)

Thirty-one merged `task 18.*` titles at HEAD (18.28 = this close), grouped by wave.

**Wave A — the instruments and the pre-registration (18.1–18.4).**
- **18.1** Tier-A deception instruments (#296, `9ef07aa`): the `false-vouch` / `frame` /
  `teammate-immunity` folds plus the alibi and deflection wrappers — `eval/deception_instruments.py`.
- **18.2** kill-craft fold (#288, `05e6e50`): kill timing vs witness density + action-stream entropy
  — `eval/kill_craft.py`.
- **18.3** off-menu instrument (#290, `1e837c9`): off-menu rate on the engine intent-KIND plane —
  `eval/off_menu.py`.
- **18.4 THE EMERGENCE PRE-REGISTRATION (owner)** (#298, `ef841c9`): 13 claim rows →
  **14 rulings** (`action-entropy` ruled once per side), the four-part **conjunctive** discipline —
  (a) |z| ≥ 1.96 vs the same-seed scripted-FSM comparator on the real path, (b) reproduction on ≥ 2
  of 3 corpus seed-splits, (c) a named counterfactual ablation showing recession, (d) selected-for
  presence in the champion's own recordings — *"failing any one reads NOT-DEMONSTRATED — there is no
  'partially emergent'."* Its §9 amendment log is empty.
  `audits/audit-phase-18-emergence-preregistration.md`.

**Wave B — training-stack groundwork (18.5–18.7).**
- **18.5** anchor study (#292, `f329a4a`): λ sweep + filtered-BC anchor refinement, consumed by
  run-02/run-03 — `training/artifacts/anchor_study/`.
- **18.6** MAP-Elites cell persistence (#294, `3d7a657`): persisted founder cells + referee-tension
  descriptors — `training/artifacts/impostor/map-elites/`.
- **18.7** crew deployment surface (#291, `bce9731`): the opt-in, adoption-gated crew surface (the
  17.13 routed contract) — `agents/` + `--crew-artifact`.

**Wave C — the meeting-layer levers and the gate (18.8–18.11).**
- **18.8** roll-call round (#289, `c472499`) and **18.9** endpoint-band exemption +
  vent-placement variant (#293, `55dc23d`): three default-OFF levers with counterfactuals.
- **18.10** impostor-answer template arm (#297, `f72191b`): the variant arm, default untouched.
- **18.11 THE MEETING-LAYER GATE** (#299, `b65d22f`): a 2 × 25-seed 9p2i real-path probe (seeds
  2000–2024, 6 h 07 m at 2 workers) and the owner's ruling, verbatim **"CREW-ONLY, go ahead with the
  recomendation"** — **(A)** the roll-call round and the endpoint-band exemption SHIP; the
  impostor-answer arm stays **INERT** (bar (c) failed both clauses: impostor win 4/25 = 0.16 < 0.20;
  STRONG self-flag 42/100 = 0.42 > 0.25 at z = +3.93 — the arm and its bars stay in the tree for a
  future owner-gated re-probe, never silently deleted); **(B)** the absence prior **GRADUATES** (the
  ratified 17.7 §6 bar passes both clauses for the first time: crew coverage 1.00 ≥ 0.60,
  new-over-gate 3/75 = 0.04 ≤ 0.20; top-churn 4/75 = 0.053, down from 114/179 = 0.637 off-path);
  **(C)** the vent variant + widening SHIP (28 STRONG `alibi_vs_physical` flags, all impostor
  subjects, all vent-grounded). `audits/audit-phase-18-meeting-gate.md` §9.

**Wave D — the two records (18.12–18.13).**
- **18.12 THE ADOPTING RECORD: baseline 6** (#300, `0c08758`): both canonical sets re-recorded on
  the real path; validity PASS both (10/10, meeting rate 1.00 / 0.78, $0); the substrate stamp is
  **thirteen levers True** with `impostor_roll_call` **False**; the floor block re-pinned at
  self-consistent equality (witnessed 6/177, flags 180/165, conversion 78/136) and
  `_DEFAULT_BASELINE_ID` flipped to `baseline-6`; **neither §0.4 banded canary fires** (R1 rose to
  31/50 = 0.62, successor 70/79 = 0.8861); watchability mean 42.25 → **54.58**. The measured costs
  it recorded honestly: ejection accuracy fell 64/70 = 0.9143 → 78/101 = 0.7723 and zero-flag
  conviction rose 2/70 = 0.0286 → 11/101 = 0.1089, against roll-call coverage 0.4624/0.0894 →
  0.9958/0.4545 and whereabouts lies 6 → 50. `audits/audit-phase-18-baseline-6.md`.
- **18.13 the corpus re-record at baseline 6** (#301, `4156b2d`): 150-game 9p2i (seeds 1000–1149) +
  50-game 4p1i (seeds 1000–1049) at exact baseline-6 config, `seed mod 5` splits (90/30/30 +
  30/10/10), measured **~22 h 54 m** (9p2i 19 h 26 m, 4p1i 0 h 45 m, phantom-repair pass over 10
  seeds 2 h 43 m), FROZEN at `fb8c07f` (9p2i) / `d5c31c7` (4p1i) with honest mixed per-row dates
  (the 16.14 precedent). It **discharges the Phase-18 staleness rule** and makes the **Q3
  restoration operative again**: the corpus is the canonical canary denominator, the 18.12 samples
  are the continuity anchor. `replays/ml_corpus/` + its README.

**Wave E — the re-ground, the models, and the composition (18.14–18.16, 18.29, 18.30, 18.18).**
- **18.14** surrogate re-ground + selection-bar re-pins (#303, `76faa96`): re-fit on the baseline-6
  corpus; staleness cap re-derived to **52,481** = 143 × 367 fit-side meetings —
  `training/artifacts/surrogate/`, `training/reports/report-ballot-surrogate.md`.
- **18.15** the conviction-economy model (#302, `6a2f339`): dataset / fit / fidelity / GO bar —
  **GO**, conversion recall **45/47 = 0.95745** against a 0.6375 bar (ceiling 0.85), flag spearman
  **0.57816** against a 0.5 bar, `model_role: "training-signal"`, `prescreen_role: "gating"`,
  weights `4841f8e0…`, fitted on `replays/ml_corpus/9p2i`. Its **held-out decision accuracy on its
  own conversion label is 0.9375** (the phase docs round it to 0.938) — a property of the conviction
  model, never of the composed runner's gate (§6.4 note; the composed channel measures 0.8646).
  `training/artifacts/conviction/verdict.json`.
- **18.16** fitness-term + referee pre-screen integration (#304, `67c53b8`): `ConvictionFitnessTerm`
  at weight 0.5 over artifact `4841f8e0…`, plus the pre-screen seam — `training/bakeoff/harness.py`.
- **18.29** the composed meeting-outcome runner (#310, `6339116`) — the owner-directed amendment:
  **GO** on its own pre-registered bar, `composed_role: "optional-campaign-configuration"`.
  Held-out cells: **decision accuracy 83/96 = 0.8646** vs the 0.625 always-eject constant;
  **convicting-meeting top-1 46/60 = 0.7667** vs the 0.6375 bar (0.75 × the 0.8500 honest ceiling);
  exact-outcome match 76/96 = 0.7917 (informational, never gates); gate confusion tp/fp/fn/tn
  48/1/12/35; the live candidate-view variant reads decision accuracy 0.8646 identical and top-1
  45/60 = 0.7500 — *"the GO verdict is invariant to the live channel"*. Rollout effect on the
  composed substrate (8 scripted-FSM games, seeds 0–7, 9p2i): **28 meetings resolved 13 ejections
  (46.4%)** against 0% on the fake path and 65.2% on the real baseline-6 path. Consumption: 1029
  composed meetings; the conviction counter charged 1365 of 52,481 (2.60%), the surrogate counter
  1029 (1.96%). Its first committed adoption constraint is the diagnostic-grade fence, verbatim from
  `training/artifacts/composed/verdict.json`:
  > composed-provenance-validity[all-arms,9p2i]: every composed-path probe arm fails the recorded
  > validity gate on cost_and_provenance_exact (no model row on a zero-LLM meeting path) —
  > composed-substrate probe reads are diagnostic-grade, never validity-passing evidence

  The other two name the pre-screen/substrate divergence shape and the forced-emergency
  predicted-supply laundering shape (+29.5% predicted against a recorded 0.0, validity-gated out of
  the machinery's findings).
- **18.30** live conviction serving path (#307, `9295a19`): kill/body accessors, in-loop term
  wiring, the live/offline parity pin — `training/conviction/serving.py`.
- **18.18** Goodhart re-probe (#305, `8626c85`): the conviction path plus the carried 4p1i exploit,
  materiality bar 0.25 — `training/reports/report-goodhart-probe.md`.

**Wave F — the co-evolution machinery (18.17, 18.19–18.23, 18.31, 18.32).**
- **18.17** real-path re-rank recorder (#295, `5a69541`): designs B/C productized as
  `training/realpath.py` — the machinery every campaign leg runs.
- **18.19** dual-role co-evo rollout + the two-identity stamp (#306, `4bd35e8`): both sides learned
  in one rollout, with the conflation guard; first live exercise at 18.25's legs.
- **18.20** hall of fame + PFSP-lite sampler (#309, `4173ef1`) — `training/coevo/hall_of_fame.py`.
- **18.21** alternating-freeze driver + stabilizers (#311, `316d4e5`) — `training/coevo/driver.py`,
  frozen machinery from here on.
- **18.22** encoder v3 + within-kind target resolution (#308, `ea0eb62`): the free-policy-family
  encoder, 1442 genes vs v2's 1049; its disposition is F11 (§6.2 I3).
- **18.23** scenario staging (#313, `d63ffab`): state injection, the skill-scenario library, the
  `scenario_provider` seam — consumed only as the zero-valued capturing term (§6.5).
- **18.31** campaign ergonomics (#314, `e2a040b`): resume, per-generation persistence, loadable
  freezes, generated tables — `scripts/generate_campaign_tables.py`.
- **18.32** crew re-rank arm (#315, `088d4c2`): crew candidates, the frozen-opponent seam, dual
  stamps; rows land under `realpath-rerank-v3` — `training/realpath.py`.

**Wave G — the two campaigns (18.24–18.25).**
- **18.24 THE IMPOSTOR CAMPAIGN** (#312, `b19b952`): 5 lineages, **10 362 fake + 183 real games**;
  **Status: STOPPED, and NOT CONTRACT-COMPLETE (2026-07-27)** — *"The contract's per-generation
  top-K re-ranks are complete for run-02 only, tranche-1-only for run-01/run-03, and absent for
  run-04/run-05. This task therefore does NOT satisfy Task 18.24 as written, and 'stopped' is an
  owner decision taken on the §4.0 evidence — not a claim of completion. … 18.26 must not treat §8
  as a contract-satisfying finalist slate — it is a screening shortlist."* Coverage split as
  committed: **21 candidates at both tranches (6 seeds)**, **12 at tranche 1 only (3 seeds)**.
  `training/reports/report-impostor-campaign.md`.
- **18.25 THE CREW CAMPAIGN** (#316, `e9da533`): 2 runs + 2 ablation twins on the fake path, **4 real
  legs / 36 games**, STOPPED by the F12 stability ruling — mean absolute `flags_per_meeting` swing
  between tranches **2.0000** against the 1.0909 floor = **noise at 183% of the threshold**, against
  a 25% precondition, so *"at the 3-seed tranche budget, referee/flags verdicts are NOT resolvable
  for this campaign"*; 2 of 2 arms saturate the derived conversion floor at 1.000 on ≥ 1 tranche;
  referee PASSes recorded/retested/replicated **2 / 2 / 0**. It named **no crew finalist**.
  `training/reports/report-crew-campaign.md`.

**Wave H — the eval and the ruling (18.26–18.27).**
- **18.26 the real-LLM finalist eval** (#317, `384effc`): 9 arms × 50 seeds, **449 recorded
  seed-games**, $0, two pre-registered cells, and the §10.3 verdict rule that made UNRESOLVABLE a
  third outcome beside PASS/FAIL. It is the evidence base of §1.
  `training/reports/report-finalist-eval.md` Part II + `results-finalist-eval.jsonl` (11 rows: the
  two Phase-17 baseline-5 rows preserved under the APPEND rule, plus the nine 18.26 arms).
- **18.27 the flip + emergence reading (owner)** (#318, `d98b598`): **NO-FLIP + 0 EMERGENT + NO
  crew adoption**; F13 hypothesis A rejected as unsupported; the ruling pinned in
  `tests/scripts/test_champion_flip_ruling.py`; the deferral ledger routed to this close.
  `audits/audit-phase-18-flip-emergence.md` §13.

**The axis-2 tally, in full (flip audit §7, candidate `p18-imp-ea4bc955` vs `p18-fsm-comparator`
full-50):** **0 EMERGENT, 14 NOT-DEMONSTRATED.** Rulings 1–8 and 10 fail clause (a) outright
(false-vouch saw_player 26/206 vs 20/196, z = +0.761; corroboration 12/54 vs 6/54, z = +1.549;
fabricated share 5/21 vs 9/19, z = −1.560; frame attempt rate 151/155 vs 148/157, z = +1.393; frame
conversion 10/151 vs 6/148, z = +0.987; alibi survival 26/33 vs 23/30, z = +0.202; deflection
efficacy 42/95 vs 23/59, z = +0.639; within-one-hop point-biserial r = 0.21108 @ 197 vs 0.27505 @
174, Fisher z = −0.648). Rulings 6 and 12 admit **no delta at all** (teammate accusations 0/214 vs
0/190; off-menu 0/2015 vs 0/2299 — vacuous by construction). Rulings **9** and **11** pass (a), (b)
and (d) and fail only clause (c) — the phase's two named findings, §6.1 L4. Rulings **13–14** are
**unjudgeable as recorded** (impostor mean conditional entropy 0.60780 over 100 agents / 2015
decisions vs 0.66839 over 100 / 2299; crew 0.74780 over 350 / 6128 vs 0.88099 over 350 / 7767) —
the per-agent variance field never landed, and ruling 14 additionally has no §2.1 comparator.
*"The advisory flags on rulings 3, 5, 6, 7 changed nothing: every read above is the arm-vs-arm §6
discipline, and no baseline-anchored read rules anywhere in this memo."*

**The crew-adoption slot (flip audit §10): NO-ADOPTION.** The candidate considered was
`0bf179b7…` (run-c1-crew-owned-tasks gen-9, `crew-option-features-v2` — the only crew arm on the
slate with a PASS validity gate). 18.25 named no crew finalist; the 18.26 crew block is
owner-directed **DIAGNOSTIC** (2026-07-29); on that diagnostic the c1 pair reads **null at n=49**
(26/49 = 0.53061 vs the same-opponent gen-0 control's 25/49 on the 49 paired seeds — +1 game, 6–5
discordant, **McNemar exact p = 1.0**; the full-row cell is 26/50 = 0.52; rider margin −0.00793,
95% CI [−0.0808, +0.0649]); the c2 lineage is gate-invalid at both generations; and no crew arm has
a §2.1 comparator for any axis-2 claim. The three crew rows that fail the validity gate **8/10**
(`p18-crew-c1-gen0`, `p18-crew-c2-gen9`, `p18-crew-c2-gen0` — two carrying
`stalemate_games_no_game_over` and `integrity_ok: false`, one reading `ejection_accuracy: null`
on zero resolved meetings at impostor win 0.98) are **crew-side diagnostics outside the ratified
slate**, never slate arms; they are the committed record of the "crew cells NOT-DEMONSTRABLE"
finding and they feed this NO-ADOPTION context. **RULING: NO-ADOPTION — no crew-adoption question
survives the evidence to be put beyond this slot.** The crew surface stays opt-in (`learned-crew`)
on the committed `crew-owned-tasks-es` artifact (`bd6fdd0a…`), unswapped.

---

## 5. The permanent record: the Phase-19 staleness rules

**Everything this phase trained, fitted, selected, or pinned is BASELINE-6-SUBSTRATE-ANCHORED. A
Phase-19 change to the meeting layer makes all of it prior-substrate-anchored again — re-ground
before any training against it.** Specifically:

- **`replays/ml_corpus/`** (18.13) is baseline-6 meeting-layer calibration data with `fsm-default`
  movers. **At this close it remains canonical and same-substrate in full**: the meeting layer has
  not moved since 18.12/18.13, and the mover default did **not** flip at 18.27, so the corpus and
  the canonical samples sit on the same rung and nothing downstream trains across a substrate seam.
  It stays the **canonical canary denominator** (Q3), with the 18.12 samples as the continuity
  anchor. **The forward rule, for whenever a mover flip DOES land:** a mover flip does not
  invalidate meeting-layer calibration data, but impostor-behavior-conditioned cells become
  **champion-era** from that adopting baseline on and must be read with that caveat.
- **Any Phase-19 meeting-layer change re-grounds the whole stack**: the corpus record, the 18.14
  surrogate (fitted on the baseline-6 corpus, cap 52,481 = 143 × 367 fit-side meetings), the 18.15
  conviction model (fitted on `replays/ml_corpus/9p2i`, same cap) and its 18.29 composition, and
  every bake-off / finalist selection read. The review-and-refresh charter does not by itself move
  the meeting layer; if any refresh work does, this rule binds.
- **The 18.26 finalist evidence is baseline-6-conditioned selection evidence.** Every row scores
  `baseline_id: "baseline-6"`, and the win-edge comparator is the fresh 18.26 arm recorded beside
  the candidates (13/50 = 0.26) — never Phase-17's 0.36 and never the samples manifest's 0.30. Those
  rows do not transfer across a meeting-layer change.
- **The floors** (`eval/watchability.py` baseline-6 block) are record-pinned to the standing sets
  and **move only at a record**. No baseline-7 block exists; the next one to land pins its own.
- **The champion** (`agents/tactical/learned/`, `utility-es`, sha `6d327dcb…`) stays **OPT-IN** with
  its 18.26 row as the recorded evidence (win 19/50 = 0.38, Δ +0.12, referee FAIL on both live
  supply gauges). Those numbers are baseline-6-anchored and go stale at the next meeting-layer
  change like everything else. The crew surface stays opt-in on `bd6fdd0a…` on the same terms.
- **The ratified bars re-read on new bytes, never on these**: the §1.3 flip bar, the 17.7 §6 absence
  bar, and the 18.4 emergence discipline all bind on whatever substrate a future record produces.

---

## 6. The routed contracts + the deferral ledger (findings, not failures)

Every deferral is named here as a routed contract, an explicit lapse, or a recorded observation —
**none is silent**. The FAILs in this section are instruments working: the referee FAIL is the bar
pricing a co-adapted impostor's objective; the campaigns closed as measured findings; zero EMERGENT
is a measured tally under a conjunctive discipline.

### 6.1 The 18.27 ruling's own ledger (memo §12, all ten items)

- **L1 — NO-FLIP close path** (§4.2): no mover record; the battery re-runs over existing bytes at
  HEAD; the 17.17 "resist recording anything" discipline holds. **Discharged by this close** (§2).
- **L2 — the witnessed-gauge structural unresolvability** (§4.3): the rare-event floor's 25% ceiling
  (0.00847 against measured noise 0.01479–0.08671) is unclearable at n = 50 on **all nine arms** —
  an instrument finding for the close. **Any bar re-pricing is an owner decision outside the memo**;
  this close makes none. Routed forward as an owner-only question.
- **L3 — the F13 residual** (§5.3): the within-lineage conversion cell **−0.02231** (one gauge, one
  pair) — an observation, no contract. No selection-rule fix routes.
- **L4 — findings N1 / N2** (§8.3). **N1 — the learned mover kills into witnesses at ~3.3× the
  scripted rate**: crew-witnessed-kill rate **30/197 = 0.15228** vs the comparator's **8/174 =
  0.04598** (z = **+3.370**, sign-reproduced 3/3: 16/121−6/102, 9/39−1/36, 5/37−1/36). **N2 — the
  learned mover emits a kill class the scripted FSM cannot: co-present kills** — **20/197 = 0.10152
  vs 0/174** (z = **+4.321**, 3/3: 12/121−0/102, 4/39−0/36, 4/37−0/36; the committed FSM kills only
  when alone — 0 co-present kills on all 863 corpus-pinned kills). Both are selected-for (present on
  the champion's own arm and, as archive corroboration, on all eight learned-impostor arms:
  witnessed 0.143–0.223, co-present departure 0.076–0.187) and both read **NOT-DEMONSTRATED** because
  clause (c) is unsatisfiable by construction — the behaviors appear on the un-levered incumbent
  control (`6d327dcb…`: witnessed 43/193, co-present 36/193), so no campaign lever enables them and
  no `ablation:kill-craft/<lever-id>` exists to name. **Routed contract: a §6.c-satisfiable claim
  needs a lever-scoped training contract in a future campaign.**
- **L5 — the F11 encoder-v3 disposition** (inherited (c)): see §6.2 I3 for the numbers. The
  measurement is input, no ruling; the keep/drop disposition routes forward with the off-menu family
  context.
- **L6 — the conviction-term recede recording** (§8.1): withheld under the F12 stop; **belongs to a
  50-seed venue as a routed contract if the claim is pursued.** The standing attribution fence: per
  F6 (extended, not contradicted, by 18.25's paired twins) the term's demonstrated selection locus
  is **crew-side on both bases** with a base-dependent channel, and **no ruling attributes any
  impostor-side selection effect to the conviction term**. The clause-(c) ablation ledger as
  recorded: complete on **zero of the five impostor campaign runs and zero of the two crew runs**
  (run-01's twin reproduces the impostor champion lineage sha-for-sha so a recede read is impossible
  by construction; run-02's ablation ran on the fake path only; run-03 and run-05 recorded none;
  run-04's is a tranche-1 **n=3** screen whose tranche 2 validity-failed and was never re-recorded).
- **L7 — the scripted-crew-vs-`ea4bc955…` comparator arm** (§10): **DECLINED for this phase** —
  recording it now would be evidence assembled after the ruling it would serve. Stays available as a
  routed contract for any future crew claim. Owner-optional.
- **L8 — equivalence margins** (§9): **no post-hoc equivalence criterion is adopted** — writing an
  equivalence margin after seeing the data is the fitted-bar move the pre-registration exists to
  prevent. Both paired cells read as measured NULLS and are **INCONCLUSIVE as recorded** (the rider
  pair: gen-9 30/191 = 0.15707 vs gen-0 33/200 = 0.16500, margin −0.00793, 95% CI [−0.0808,
  +0.0649]; the conversion pair: 20 both-win / 6 gen-9-only / 5 gen-0-only / 18 neither-win, McNemar
  exact p = 1.0). **Routed: any future phase wanting a generation-pair equivalence read
  pre-registers the margin before recording.** Owner-optional.
- **L9 — the entropy variance field** (rulings 13–14): the 18.4-routed `ActionEntropyCells`
  per-agent variance contract **remains unlanded**; entropy claims stay unjudgeable until it lands
  with re-pins. This close reports entropy point estimates (§2.5) and judges none.
- **L10 — cycling-detector inputs** (context): the **Red-Queen signature is PRESENT** on the
  general-base impostor (flat anchor + oscillating co-matchup); the owned-task crew reads progress
  while its impostor plateaus — Phase-19-visible context, not a contract.

Also recorded from axis 2, reportable and never EMERGENT (flip audit §8.4): the incumbent control's
archive cells — `6d327dcb…` false-vouch saw_player 40/213 = 0.18779 vs 20/196 (z = +2.449),
corroboration 30/71 = 0.42254 vs 6/54 (z = +3.809), within-one-hop r = 0.52142 @ 193 vs 0.27505 @
174 (Fisher z = +2.808); `7f73929d…` corroboration 20/60 = 0.33333 vs 6/53 (z = +2.774, 2/3). And
the off-menu free-policy departure (§8.2): off-menu rate **79/101 = 0.782** (`27f852fe…`, v3 gen-9
hall champion) and **114/120 = 0.950** (`348df066…`, gen-3) against a structural-0 baseline, ruled
**NOT-DEMONSTRATED** on two independent limbs — (d) fails, and (c) is a tranche-1 n=3 screen with no
recede on either committed pair (gen-9 79/101 = 0.7822 vs ablated 136/186 = 0.7312; gen-3 114/120 =
0.9500 vs 86/179 = 0.4804, a halving that still misses the recede-to-half bar by 0.0054) — *"the
ablation reads UNFINISHED-as-recorded, and no causal attribution (encoder-v3 vs action space) is
made."* The family gradient (utility 0.0 → v2 ≈ 0.36–0.39 → v3 ≈ 0.88–0.95) carries forward with
I3.

### 6.2 The 18.24 inheritance (F10, the §12 Errata, F11, the founder-persistence conditional)

- **I1 — F10, the champion-slice coverage gap: DEMONSTRATED, quantified, and routed to the owner as
  a live decision.** The contract's per-generation real-path top-K re-ranks read K=2; the campaign
  evaluated the K=1 slice (all 14 distinct champions) plus K=2 at every swap boundary, and *"that
  argument is empirically dead"* — session 4's recovery of run-02's K=2 runner-ups (36 real games)
  put two of six at or above existing finalist entries on the win axis (`bfd145cb…` 6/6 = 1.000,
  `3a89655f…` 5/6 = 0.833), and a third produced the campaign's only referee PASS on its first
  tranche, which then failed to replicate. If F10's champion-slice sentence is quoted, **§12 erratum
  6 is quoted beside it: F10's "60 generations" is corrected to the committed record of 52 rows
  (4 × 12 + 2 × 2)** — and §12 erratum 5 governs the trap: the report's §2 "Remaining task work"
  paragraph is a **superseded revision still sitting in the committed file** (it still carries the
  doubled "~40 runner-ups / ~240 games / 80–120 h"); **F10 governs**, never §2.
  **The exposure, as re-derived from the committed rows:** the four unprobed lineages hold **20**
  runner-ups (6 + 6 + 6 in runs 01/03/04 and 2 in run 05) ⇒ completion is **120 real games ≈ 40–50 h**
  at measured pace. **The decision trail:** Option B (owner, 2026-07-26) funded the two UTILITY
  lineages — run-01 and run-03, **12 runner-ups, planned 72 games over two tranches** — skipping
  run-04/run-05 on the evidence that all 12 of their arms win 0.000; **superseded 2026-07-27**:
  tranche 1 ran (**36 games**) and **tranche 2 was STOPPED under §4.0**, because a second tranche at
  n=3 would add measurements that demonstrably do not replicate. **The residual carried into this
  close:** those **12 funded runner-ups carry 3-seed screens, not 6-seed reads** (the committed
  coverage split: 21 candidates at both tranches, 12 at tranche 1 only), and **run-04's 6 + run-05's
  2 = 8 runner-ups are both unevaluated AND un-recovered** — no frozen artifacts exist for them
  (`training/artifacts/coevo/runnerups/` holds only run-01, run-02, run-03), so recovering them costs
  a re-run, priced by F10's own rate. **Routed as a live owner decision with evidence attached, not
  a scope defence:** fund the remaining runner-up evaluation, or accept a finalist slate known to be
  complete only for run-02. This close closes the phase on the latter, as measured.
- **I2 — the session-5 provenance-log gap (honest caveat on I1's blocker), §12 erratum 10:**
  *"no chain/leg log exists for the 36 Option B games"*, so the report's "every §4 leg quotes the
  pre-screen verdict" and its blanket log-coverage sentence are **sessions 1–4 scoped**; the Option B
  `prescreen-quotes-4000-4002.json` files are committed but carry no invocation stamps, so
  **pre-screen-before-spend ordering for session 5 rests on operator testimony only**. Recorded, not
  repairable; the routed fix (native leg-log writing) landed as the pre-18.25 machinery task.
- **I3 — F11, the encoder-v3 disposition.** *"Encoder v3 cost more than it bought at this budget"*:
  the `ablation:off-menu/encoder-v3` twin — run-04's config with the encoder reverted to v2 under an
  identical master seed — reached champion fitness **11.61 vs v3's 3.06** (3.8×) with a champion-side
  anchor benchmark of **+12.74 vs −1.22**, updating in **5 of 6** impostor generations vs **4 of 6**.
  For a from-scratch ES at 12 generations the v3 channels (witness / recency / meeting-history + a
  per-target kill head; **1442 genes vs 1049**) are a net loss. The campaign reports the measurement
  and rules nothing; **the keep/drop disposition and free-policy campaign sizing route forward**,
  carrying the off-menu family gradient (§6.1) as context.
- **I4 — the conditional utility-family founder-persistence run: NOT TRIGGERED, recorded as a
  lapse.** The only committed MAP-Elites founder pool is v2/1049 and is `bakeoff_substrate_sha`-fenced,
  so the utility (19-gene) and v3 (1442-gene) lineages cannot ingest it and their sessions start with
  **empty pools**; both campaigns therefore ran with `founder_cells_dir` UNSET. The routed conditional
  was an 18.6-shaped per-family founder-persistence run **if pool diversity proved load-bearing** —
  **18.25 closed COMPLETE on the fake path without invoking it**, so per the contract's own wording
  it *"lapses to a Phase-19 note."* F3 (founder-game pricing) stays moot while founders cannot load.

### 6.3 The 18.25 additions

- **C1 — the record/score leg-concurrency split (routed ergonomics, never a mid-campaign
  amendment).** The two-leg directive ran as a ROLLING pair by a session-2 owner-ratified posture
  amendment (a leg launches the moment its predecessor finishes rather than waiting for its
  pair-mate), because the F7 constraint was never overlap correctness but provider throughput plus
  the library's leg-owns-its-tranche recording model. *"True element-level work-stealing (two workers
  pulling seeds from ONE leg) needs a record/score split the tranche flock exists to refuse today —
  routed to 18.28's deferred ledger as a next-campaign ergonomics item, never a mid-campaign
  amendment (the 3-seed tranche shape is F12-load-bearing)."*
- **C2 — CF2, the general-base starvation finding.** The general-base lineage is meeting-scarce on
  the real path; its TRAINED arms move toward the evidence economy (a trained-lineage association;
  term attribution awaits the recede recording of L6) and **the effect is REAL but UNSTABLE at n=3**:
  tranche 1 — gen-0 zero meetings, trained arms 0.33 meeting rate with 2.0 flags/meeting and a
  correct ejection each, ALL arms validity-FAIL; tranche 2 — both trained arms validity-PASS
  (meeting rate cleared 0.60; selection 5.83 / 1.67) with 0.0 measured flags, gen-0 still
  validity-FAIL but winning a game (0.667 impostor win). The trained-vs-gen-0 meeting-rate delta
  persists across both tranches while the flags gauge swings 2.0 → 0.0. **The 15.22 structural guard
  exists only on the owned-task basis — v1's meeting scarcity is the measured cost of its absence**,
  and *"the v1 base without the 15.22 guard is starvation-family under a strong impostor — prices any
  future general-base crew work."* No c2 arm survives the campaign's selection bars at n=3.
- **C3 — CF3, the stability instrument refuses the crew campaign's data shapes (routed, not
  patched).** Two guards, both correct for 18.24's corpus, both tripped by crew data: a zero-meeting
  arm has an unmeasured `flags_per_meeting` and the tool refuses the ENTIRE read rather than
  reporting the arm as unmeasured-on-a-tranche; and a derived input set with a dropped arm trips the
  contiguous-rank total-order guard. Session-2 used disclosed derived copies. **The routed fix is
  native exclusion-with-reporting in `generate_campaign_tables.py stability` — an
  `arms_unmeasured_on_a_tranche` count beside the swing means.**
- **C4 — CF4, `training/artifacts/coevo/realpath/` is a RESERVED namespace, and the general rule.**
  `DEFAULT_RANKING_ROOTS` folds the whole `realpath/` tree and the committed 18.24
  `measurement-stability.json` is byte-pinned over a default-roots recomputation, so any new ranking
  landing under `realpath/` silently changes (or, with a zero-meeting arm, hard-refuses) the pinned
  reproduction — **15 test failures at the campaign's gate run**. Fixed by relocation
  (`realpath-crew/`, PATHS.md updated). **The general rule: a future campaign takes a SIBLING root,
  never a subdir of a default root.** The routed residual class:
  `scripts/generate_campaign_tables.py:105 DEFAULT_RANKING_ROOTS`, like
  `training/coevo/driver.py:350 WORK_DIR_OWNED_NAMES`, is a **hand-maintained namespace list whose
  collision class re-opens with every new campaign**.
- **C5 — the missing sweep-table generator family.** Every row/leg/stability table in the crew report
  is generated from committed artifacts via `scripts/generate_campaign_tables.py` (the F12 lesson);
  its three families are `rows`, `legs`, `stability`. The §5 sweep cells are quoted from committed
  `sweep-*.json` files but their tabular **assembly is the report's own, because no generator family
  renders sweeps** — a routed ergonomics note. Related, from 18.24 §12 erratum 15: the committed
  sweep JSONs carry **no `off_menu_decisions` key**, so any off-menu denominator comes from the named
  non-finalist exhibit recordings directly, never from the sweep artifacts.
- **C6 — duration honesty.** The crew report's **header figure "~8.7 h wall-clock" is disowned by its
  own §12 erratum 2** as not derivable from committed evidence. The derivable figures are **6.76 h
  (union of leg spans)** and **7.32 h (summed per-game `wall_seconds`)**; a third, **11.9 h (summed
  leg durations)**, also exists and is named here so its omission from the contract's quoted
  6.76–7.32 h range is deliberate rather than an oversight. Likewise the header's "the two-leg
  rolling posture ran throughout" is overstated — **§12 erratum 3** records a **~56-minute single-leg
  window** from the committed leg logs (c2-t1 done 21:53:50Z → c2-t2 start 22:49:37Z). This close
  quotes only errata-approved figures.

### 6.4 The 18.26 additions

- **E1 — three stuck-seed classes, and a routed runner-level fix.** *"The campaign's three stuck
  seeds are three distinct classes, and the runner's single `rc != 0` retry trigger sees only one of
  them:"* **(1) impure validation** (`fsm-comparator` seed 5, `7f73929d` seed 35) — rc 99, retryable,
  and the two seeds took the same 14 attempts to opposite ends (seed 5 converged on attempt 14, seed
  35 never converged); **(2) LLM-free deterministic stalemate** (`c2-gen9` seeds 19, 20) — rc 0,
  **unretryable by construction**, reproduced byte-identically in ~80 s; **(3) meeting-bearing robust
  stalemate** (`c1-gen0` seed 20) — rc 0, nondeterministic, **retryable in principle and hopeless in
  practice** at 8 attempts, holding 2 meetings and therefore making LLM calls, and still stalling at
  tick 999 on all 8 tries — *"nondeterminism is therefore not sufficient for a retry to help."*
  Classes 2 and 3 exit rc 0, so the retry machinery never sees them; both were caught by the scorer's
  `game_over` check, not by the runner. **Routed: the runner-level fix that lets the runner see the
  rc-0 stuck classes.**
- **E2 — the seed-35 pathology (recorded with forensics kept).** **14 logged attempts, every one rc
  99** — 4 in-leg passes ending in `leg-abort`, 6 stubborn rounds, and a final owner-directed retry
  run of 4 more passes dispatched after the PR was already open (970 + 587 + 607 + 817 = **2981 s**
  summed wall). *"The failure anatomy is identical in every kept forensic copy: the game's first
  meeting (`meeting-0`, tick 10), opening turn 0, agent `p-8`, defaults on validation."* The
  pre-meeting prefix is engine-deterministic, so every attempt presents the identical opening prompt
  — **a content-triggered pathology (invalid completion with observed probability 14/14), not a
  transient**. The seed is excluded and the arm scores at **n=49**, annotated on every cell.
- **E3 — the rare-event-floor structural finding (owner-only re-pricing).** L2's UNRESOLVABLE census
  is a structural property of a rare-event floor at n=50, not an instrument defect: **only the owner
  may re-price the bar**, and this close does not. Any future phase that wants the witnessed gauge to
  discriminate between arms must either raise n or change what the floor is anchored on — an
  owner decision, outside any memo or audit.
- **E4 — the declined scripted-crew comparator arm** (owner-optional; = L7). Owner decision,
  2026-07-31, ratified in-session: *"Two options were open: record the missing arm now, or label the
  cells. The owner chose labelling"* — the crew block's axis-2 cells are **NOT-DEMONSTRABLE** rather
  than rescued by a new recording, because every crew arm ran against the frozen champion `ea4bc955…`
  and the ratified slate contains no scripted-crew-vs-`ea4bc955…` row (`p18-fsm-comparator` is
  scripted on **both** sides, a different pairing). Recording it is a routed follow-up, taken up only
  if a future phase wants crew-side axis-2 claims.
- **E5 — the equivalence-margin pre-registration gap** (owner-optional; = L8). 18.26's §11.2 fixes
  the reporting form but never operationalizes "gen-9 ≈ gen-0"; the margin must be pre-registered
  before recording in any future phase that wants the read.
- **E6 — duration honesty.** Pre-registered: serial 12.2077 min/game, one 50-seed arm ≈ 5 h at the
  two-leg posture, the 9-arm slate **≈ 46 h**. Measured: serial **12.5175** pooled (**15.7877** on
  meeting-bearing legs only), one arm **≈ 6.37 h** busy-span, the slate **≈ 57.3 h** busy-span
  (**≈ 58.8 h** on the full span). *"The projection was honest and optimistic by about a fifth. …
  What the projection missed was the posture … so the slate landed at ≈ 57.3 h against ≈ 46 h, 25%
  over — ≈ 58.8 h and 28% over if the post-PR idle is counted as calendar time. The gap is not the
  provider"*: recording-idle inside the slate is 0.1175 h and the other 1.4286 h of idle is the gap
  before the owner-directed seed-35 retry; the cost is the meeting-bearing legs' 15.7877 min/game,
  three sleep stalls (3.881 h) and **36 recording attempts spent on three stuck seeds to salvage
  one**. Supporting components: recorded-game wall 348 488 s = 96.8022 h over 464 recordings; in-leg
  rc99 attempts 22 465 s = 6.2403 h over 30; the stubborn loop 7821 s = 2.1725 h over 11; **full
  attempt wall 378 774 s = 105.2150 h over 505 attempts**; busy span 57.1589 h = 58.705 − 1.5461
  idle; 449 recorded seed-games.

### 6.5 Scenario accounting — NOT-ADOPTED on both campaigns (the contract clause, resolved honestly)

The 18.28 contract asks that "wherever a campaign adopted scenarios the close states the provider
config (scenario set, seeds, meeting layer) and quotes `games_per_evaluation` beside
`projected_game_bound`". Measured against the committed rows, **neither campaign adopted a scenario
provider**, so the clause resolves as a recorded **NOT-ADOPTED** on both sides:

- **All 52 committed impostor rows and all 24 committed crew rows carry `scenario_labels: []`,
  `meeting_runner: "fake-provider"`, and `adoption_constraints: []`.** 18.25 states the decline
  explicitly — *"the main runs adopt NO scenario provider; comparability and the
  single-thin-scenario reality both argue against"* (the library holds exactly one crew scenario,
  `body-discovery-latency`, max 1.0; scenario terms add after the slate mean, making row fitness
  scalars non-comparable to 18.24's rows) — and 18.24 used the `scenario_provider` seam **only as a
  zero-valued capturing term** to recover intermediates from deterministic re-runs with
  byte-identical selection (the F1 mechanism, extended for the K=2 recovery).
- **`projected_game_bound` against measured `games_played_cumulative`:** 18.24 runs 01–04 projected
  **3 816 games/run** under a 25 000 ceiling and measured **2358 / 2424 / 2424 / 2308**; run-05
  projected **1 176** and measured **848** (Σ = 10 362). 18.25 projected **3 816 games/run** on both
  runs and measured **2432** (run-c1) / **2574** (run-c2). Every run landed under its projection and
  far under the ceiling. (Final `conviction_uses`: 2717 / 2749 / 2821 / 886 / 862 impostor; 3021 /
  635 crew.)
- **`games_per_evaluation` exists nowhere in the committed rows** — it is a `ScenarioProvider`
  config knob the crew report labels *"advisory only (nothing meters it)"*, so there is no committed
  value to quote beside `projected_game_bound`. Stated rather than fabricated.
- Meeting-layer honesty, for the record: both campaigns ran under the **default forced-fake meeting
  layer** (every meeting resolves SKIPPED); the composed runner is GO but was **NOT adopted** for the
  fake-path runs.

### 6.6 The roadmap's standing physical-channels deferral — re-evaluated at this close, as its trigger demands

`tasks/post-phase-14-plan.md` §5 carries a pre-Phase-15 deferral whose re-evaluation trigger names
this close: *"New physical information channels (cameras/door logs, task-visual confirmation as soft
alibis, sabotage retune so meetings happen under pressure) → still deferred; re-evaluate at the
Phase-18 close against the evidence economy that phase leaves behind."* The re-evaluation, against
the evidence economy this phase measured:

- **The demand side these channels would feed now exists and is priced.** Baseline 6 doubled the
  flag-supply floor (0.50279 → 1.09091, §1.2), the learned movers starve it on every arm (§1.1), and
  the `witnessed_event_rate` gauge is the rare-event channel the phase found structurally
  unresolvable at n = 50 (§6.1 L2; 12 witnessed events over 505 corpus kills, §2.2) — new physical
  witness channels are exactly the class of witnessed-supply widening a future substrate wave could
  price against those gauges, with the §3 corpus anchors as the before-column.
- **No contract can route to Phase 19**: Phase 19 is REVIEW-AND-REFRESH by owner charter — not a
  feature phase — and this close adds no new evidence beyond the battery, so authoring a substrate
  wave here would be exactly the surprise the two-owner-gate compression forbids.
- **Disposition: REMAINS DEFERRED, trigger refreshed** — re-evaluate at the authoring of the next
  FEATURE phase (the first phase after the Phase-19 review/refresh), reading §6.1 L2 (the
  witnessed-gauge unresolvability), §2.2 (the supply economy at baseline 6), and the §3 anchors as
  its inputs. The roadmap §5 bullet is refreshed to this disposition in this PR — a named deferral
  with a live trigger, not a silent gap.

---

## 7. The Phase-19 hand-off — REVIEW INPUTS, NOT CONTRACTS

**Everything in this section is a review input, not a contract.** Phase 19 is REVIEW-AND-REFRESH: it
decides what, if anything, to do with each item. Nothing here is pre-authorized work, and no item
carries a bar, a budget, or a due gate.

| # | review input | anchor | what is actually there |
|---|---|---|---|
| 1 | Three `eval/` per-game walk implementations | `eval/funnel.py:287` `_walk_game`, `:1138` `_walk_game_vj`, `:1857` `_walk_set_vj`; `eval/kill_craft.py:414` `_walk_game`; `eval/off_menu.py:323` `_walk_game` | three independent per-game reconstruction walks |
| 2 | The disclosed duplication (self-reported by the modules) | `eval/kill_craft.py:104-118` module docstring — *"the walk is duplicated locally, and the duplication is noted for Phase 19's review"*; repeated `:405-407`; `eval/off_menu.py:36-44`; `eval/deception_instruments.py:166` (the one module that DOES import the shared walk) | a deliberate, documented duplication — review it as a design question, not a bug |
| 3 | "Retired seams" | `tasks/phase-18.md:2282` (contract text only) | **no in-repo anchor exists** — see the note below |
| 4 | The `episode_boundary` orphan | `training/rollout.py:71` (the type alias), validator `:77`, branch `:588`; `training/env.py:577,587,612,630,725,958,1037,1140`; `training/rewards.py:287` | every production caller passes `"full_game"` explicitly (`training/crew/scorer.py:946`, `training/bakeoff/harness.py:722`, `training/coevo/rollout.py:214`); `"first_meeting"` is exercised **only in tests** — a deliberate truncation mode with no live consumer |
| 5 | The recorder lock-race | `scripts/record_ml_corpus.sh:966-999` | the portable `mkdir` mutex with dead-owner detection; the recorded limitation: *"On 3.2 every worker shares `$$` … so dead-owner detection degrades to a no-op — the mkdir mutex + release still serialize correctly; only the rare 'a worker was SIGKILLed mid-critical-section' safety net is lost."* Related historical finding: `audits/audit-2026-05-30-0059-mvp-close.md:96` |
| 6 | The un-unit-tested `deadline_default` freeze-guard branch | `scripts/record_ml_corpus.sh:581-600` | grep-verified: `tests/scripts/test_record_ml_corpus.py` contains **zero** occurrences of `deadline_default` — the branch has no unit test. Both shapes are documented at `replays/ml_corpus/README.md:240-251` |
| 7 | The validity-gate `deadline_default` blindness (unassigned) | grep-verified: `scripts/validity_gate.py` and `eval/validity.py` contain **zero** occurrences of `deadline_default` | in-repo statement: *"`scripts/validity_gate.py` has no `deadline_default` check at all; it rejects the sentinel shape only incidentally, via the model column. The corpus recorder is deliberately stricter than the gate here."* Routed by PR #299 and marked "inherited by the close if unclaimed" — **this close does not claim it; it hands it to Phase 19 as a review input** |
| 8 | The stamped-substrate question for LLM-free meeting paths | `eval/validity.py:864` `check_cost_and_provenance` (check emitted `:982` / `:1209`) | the machine-readable statement already exists in `training/artifacts/composed/verdict.json.adoption_constraints[0]` (quoted in §4): composed-substrate probe reads are diagnostic-grade *"until the provenance check has a stamped-substrate answer for LLM-free meeting paths (an eval-side question)"*. A composed meeting makes zero LLM calls, so no model row exists to stamp — structural for ANY zero-LLM meeting path, not behavioral; every behavioral check passes on the same set |
| 9 | The platform-sensitive `test_es` hash pin | `tests/training/test_es.py:74` (`:85-89` — *"digest is a fixed constant. If this changes, the ES core drifted"*) | grep-verified: no platform guard (`sys.platform` / `platform.system` absent). In-repo record of the failure mode: `tasks/phase-18.md:2659` — *"(the macOS-only ES hash pin verified pre-existing on bare main, identical digest; CI Linux green)"* |
| 10 | The `composed_artifact_dir` type-annotation-only escape | `training/coevo/driver.py:80-81`, `:426`, `:437`, consumed `:1531-1533` | the "structurally unreachable" guarantee is the **type annotation only** — `training/composed_runner.py:342` still declares `composed_artifact_dir: Path \| None` and `:372-396` implements the `None` diagnostic branch |
| 11 | The silently-overwritable `campaign-plan.json` | `training/coevo/driver.py:323` `CAMPAIGN_PLAN_FILENAME`, `:118` (the write), `:340` + `:1206` (path-collision commentary), pinned `tests/training/test_coevo_driver.py:973,1003` | the no-clobber preflight covers `WORK_DIR_OWNED_NAMES`; the plan file itself is written per run |
| 12 | The scenario selector seam's unenforced delegation convention | `tasks/phase-18.md:1823-1825`; restated `report-crew-campaign.md:86-88` | *"the selector seam drives EVERY seat including the opponents under an unenforced delegation convention and is never a campaign configuration"* — never exercised: both campaigns' rows carry `scenario_labels: []` |
| 13 | Resume refuses non-canonical maps (18.31 residual) | `training/realpath.py:4158-4167`; recorded `tasks/phase-18.md:2577-2578` | *"custom-map campaigns have no resume path without an eval/ change"* |
| 14 | Hand-maintained `WORK_DIR_OWNED_NAMES` (18.31 residual) | `training/coevo/driver.py:350`, consumers `:1202`/`:1223`, export `:2240`, pins `tests/training/test_coevo_driver.py:983,994` | *"any future driver-owned path must be declared there or the collision class re-opens"*; its twin is `scripts/generate_campaign_tables.py:105 DEFAULT_RANKING_ROOTS` (§6.3 C4) |

**On item 3, stated plainly: "retired seams" has no in-repo anchor.** It appears only in the 18.28
contract text and its generated prompt; a grep over `*.py` and `*.md` finds no other occurrence.
This close hands it to Phase 19 as a **review PROMPT**, not as a catalogued finding, with the two
instances this phase can substantiate: the retired always-on lever set
(`orchestrator/replay.py:531` `_RETIRED_ALWAYS_ON_LEVERS`, consumed `:585`/`:622`, **grown by four
at 18.12**) and the deliberately-inert 18.10 impostor-answer arm, which the gate ruling keeps in the
tree *"for a future owner-gated re-probe on trained bytes"* and explicitly never silently deletes.

Additional Phase-19-visible context, carried from §6 rather than restated as work: the **Red-Queen
cycling signature** (present on the general-base impostor — flat anchor + oscillating co-matchup;
the owned-task crew reads progress while its impostor plateaus, §6.1 L10); **CF2's general-base
starvation pricing** for any future general-base crew work (§6.3 C2); the missing sweep-table
generator family (§6.3 C5); and **the N1/N2 lever-scoped-contract note** — the phase's two named
behavioral findings are unablatable by construction on this evidence, so a §6.c-satisfiable claim
would need a lever-scoped training contract in a future campaign (§6.1 L4). None of these is a
Phase-19 contract; they are inputs a review may weigh.

**Restated, because it is the point of this section: these are review inputs, not contracts.**

---

## 8. Provenance + Q5

- **No record at this close ⇒ no new recording commit ⇒ no new Q5 tag point.** The contract's Q5
  tag clause binds on the FLIP path; the NO-FLIP arm is the **fallback**, named here per the DoD:
  this close's provenance point is the **18.28 PR's merge commit itself** — durable in `main`'s
  history and named by this audit — and the owner MAY additionally tag it
  (`git tag -a phase-18-close <merge-sha> -m "Q5: Task 18.28 NO-FLIP close" && git push origin
  phase-18-close`) at leisure. Nothing this close produced requires byte-level provenance beyond git
  itself: **no replay bytes moved.** Honest precedent note: the 17-close offered the same optional
  arm and **`phase-17-close` was never minted** — `git ls-remote --tags origin` at this close shows
  no such tag.
- **The phase's records carry their Q5 arms asymmetrically, and both arms are stated as they are:**
  - **The 18.13 corpus record's tag arm is COMPLETE.** `git ls-remote --tags origin` observes
    `dc65c72214b7389046ea4053548d07f869271e8f refs/tags/phase-18-corpus-8f5f434` and
    `8f5f434b5851e1e98117beaf56115eced9c6de5a refs/tags/phase-18-corpus-8f5f434^{}` — the annotated
    tag object resolving to commit `8f5f434`, exactly the `phase-18-corpus-<sha>` convention the
    corpus README's "finding these bytes later" arm names. Its FROZEN lines are `fb8c07f` (9p2i) and
    `d5c31c7` (4p1i), recorded 2026-07-21.
  - **The 18.12 samples record carries the sha arm only.** There is **no `phase-18-baseline-6` tag**
    on the remote: the ladder tip's own bytes are pinned by the per-row MANIFEST `git_sha` column
    (`samples/9p2i`: `2454379` ×44, `545f361` ×4, `f011848` ×2; `samples/4p1i`: `fa518ab` ×50, all
    dated 2026-07-20) plus the merge commit `0c08758`, with the record audit's §7 statement — *"The
    recording sha is Q5-back-filled on merge"* — as the operative provenance claim. This is the
    16.14/16.17 environment limitation (dispatch environments refuse tag pushes, so the tag is an
    operator-session step), not an omission by this close. Byte-verification is the operative
    guarantee and was re-proven at HEAD (§2.1: 300/300 byte-identical).
  - **The 18.26 rows carry `recording_git_sha` per row**, so the evidence is re-recordable from
    `main`: `p18-imp-ea4bc955` `bf50f792514713855629f057a43d6cd8b065c467`; `p18-imp-bfd145cb`
    `58f8fe73db92abca69e9209127b848d7790a85da`; `p18-imp-6d327dcb`
    `5b4aaf8b682053a42a86977d610f715cb49565dd`; `p18-imp-7f73929d` and `p18-fsm-comparator` both
    `753ea05dd8dc98655d53a71f63a111c84c9028cd`; the four crew rows
    `af60a680…`, `d0723293…`, `ae3b9388…`, `7659373d…`; and the two preserved Phase-17 rows
    `2a9b369fd1fd8930f71851f6811eed93e209b76a`.
  - **The corpus 9p2i FROZEN sha (`fb8c07f`) appears in no per-row `git_sha`** (rows carry `96ee2fa`
    ×135, `43bd14d` ×10, `d5c31c7` ×5) — **by construction**: the FROZEN line names HEAD at the
    moment the recorder ran for the freeze pass, and the README states it is deliberately not a
    pointer to the commit that contains the bytes.
- **Remote tags observed at this close** (read-only query): `attempt-1-phase-10-wave1-rerecord`,
  `phase-16-baseline-4` → `a43b178`, `phase-16-baseline-5` → `2428044`, `phase-18-corpus-8f5f434` →
  `8f5f434`. Nothing else.

---

## 9. Decisions

- **The ruled path is NO-FLIP and nothing is recorded.** `replays/`, `eval/watchability.py`, and the
  never-created BEFORE-column measure JSON are intentionally untouched: the BEFORE column exists to
  attribute a record, and no record happened (the implementation hint's "resist recording anything"
  honored). `agents/` and `training/` stay frozen at 18.27. The close's value is the §1 finding, the
  §2 re-verification, and the §3 anchors.
- **No test changes ship in this PR.** No bytes moved, so every committed-bytes pin holds — the
  ruling pins re-ran green (`tests/scripts/test_champion_flip_ruling.py`, **10 passed in 0.36s**),
  and the byte-coupled counterfactual sweep every record performs is vacuous with no new bytes. No
  test reads the phase-doc banner, the README, or this audit (grep-proven; the only near-miss,
  `test_champion_flip_ruling.py`, pins the 18.27 FAIL state from committed evidence bytes and is
  exactly the "default provably does not move" pin this close relies on). The full suite ran green
  for this close in a Linux container at the close tree (**4531 passed, 20 skipped, 3 xfailed** —
  the gate of record for the platform-sensitive Linux-only `test_es` hash pin, which fails on a
  bare macOS interpreter at HEAD independently of this PR; §7 item 9 records it as a Phase-19
  review input).
- **The §3 cells are anchors, not pre-registrations.** Pre-registration is a §0-block act of the
  record that uses them (the 15.18 discipline); this close records the anchor arithmetic on the
  restored baseline-6 denominator so the next record can pre-register on a powered denominator.
- **The corpus referee read is recorded, not repaired.** `replays/ml_corpus/9p2i` reads
  `referee_passed: false` on `witnessed_event_rate` alone (12/505 vs the samples-pinned 6/177)
  against a floor block that is samples-pinned by construction. It is a cross-population diagnostic,
  judges nothing, and no floor, gauge, or byte was touched in response.
- **The corpus citation-compliance anomaly is recorded, not repaired.** 1574/1578 = 0.99747 — four
  uncited EJECT ballots on the 150-game corpus, against unity on all three other sets, and
  first-noticed at this close (no committed record carries the cell at baseline 6).
- **The vent-variant yield of 6 is the 18.12-recorded state reproducing, not a new fire.** The
  record already read it as a reported near-miss of the [7, 28] sanity bracket's lower edge and
  explicitly not a banded canary; the corpus's 12.0-per-50-games scaling supports that reading.
- **The scenario-accounting clause resolves NOT-ADOPTED on both campaigns**, with
  `projected_game_bound` quoted against measured `games_played_cumulative` and the absence of any
  committed `games_per_evaluation` value stated rather than papered over (§6.5).
- **Durations are quoted from errata-approved figures only** — 18.25 at 6.76 h / 7.32 h (never the
  disowned ~8.7 h header, and with the 11.9 h summed-leg figure named), 18.26 at ≈ 57.3 h against a
  pre-registered ≈ 46 h, 18.13 at ~22 h 54 m, 18.11's probe at 6 h 07 m.
- **`compute_next_task.py --phase 18` is demonstrated on the NORMAL path.** Unlike the 17-close's
  environment, `gh` is available and authenticated here (v2.92.0), so the CLI ran without offline
  degradation: **merged 31, dispatchable `18.28`, blocked 0**, exit `0`. A second, independent
  index — feeding `compute_frontier` the merged `task 18*` titles from `git log` — agrees exactly
  (**AT HEAD: dispatchable `['18.28']` / blocked `[]` / merged 31**; **WITH 18.28 MERGED:
  dispatchable `[]` / blocked `[]` / merged 32**), and the strict `^task 18` anchor misses no merged
  task title (the broader case-insensitive grep returns 35, the 4-title difference being entirely
  coordination commits). `parse_all_tasks` returned **zero errors**. **The phase computes complete on
  18.28's merge.**
- **The banner, README, and roadmap record the close in the same PR** (`tasks/phase-18.md` STATUS →
  CLOSED; the README project-status and roadmap paragraphs, which were stale on two counts — they
  still described Phase 18 as presentation, a charter superseded on 2026-07-18; and the
  `tasks/post-phase-14-plan.md` spine, whose "baseline 6 (NOT RECORDED)" node is Phase-17-scoped
  prose that 18.12 superseded, and whose "baseline 6 (+7)" conditional resolves here: **the
  meeting-layer record LANDED as baseline 6; the mover record was NOT taken, so there is no baseline
  7**). The owner ratifies this close reading by merging this PR (the 15.18 convention) — the
  phase's second owner gate, and the reason this PR carries **no new evidence**: the merge ratifies a
  reading, never a surprise.

---

## 10. Method + reproduction (all $0 against committed bytes; offline except the two named remote queries)

```
uv run python scripts/validity_gate.py replays/samples/9p2i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost      # §2.1 PASS (10/10)
uv run python scripts/validity_gate.py replays/samples/4p1i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost      # §2.1 PASS (10/10)
uv run python scripts/validity_gate.py replays/ml_corpus/9p2i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost      # §2.1 PASS (10/10, 150 games)
uv run python scripts/validity_gate.py replays/ml_corpus/4p1i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost      # §2.1 PASS (10/10)
uv run python scripts/measure_baseline.py --json                        # §2.3 core cells
uv run python scripts/measure_baseline.py --funnel --json               # §2.3 funnel
uv run python scripts/measure_baseline.py --watchability --json         # §2.2 referee (baseline-6 default)
uv run python scripts/measure_baseline.py --vj --json                   # §2.4 V&J instruments
uv run python scripts/measure_baseline.py replays/ml_corpus/9p2i --json # §2.3 corpus core
uv run python scripts/measure_baseline.py replays/ml_corpus/9p2i --funnel --json
uv run python scripts/measure_baseline.py replays/ml_corpus/9p2i --watchability --json
uv run python scripts/measure_baseline.py replays/ml_corpus/9p2i --vj --json
uv run python scripts/measure_baseline.py replays/ml_corpus/4p1i --json # (+ --funnel/--watchability/--vj)
bash scripts/verify_samples.sh                                          # §2.1 BARE env, both canonical sets
bash scripts/verify_samples.sh replays/ml_corpus/9p2i                   # README.md:333, the explicit-set arm
bash scripts/verify_samples.sh replays/ml_corpus/4p1i
uv run pytest tests/scripts/test_champion_flip_ruling.py -q             # §9  10 passed
uv run python scripts/compute_next_task.py --phase 18                   # §9  merged 31, dispatchable 18.28
git ls-remote --tags origin                                             # §8  (read-only remote query)
```

The two documented census folds (the only §2.4 cells the CLIs do not emit directly), reproducible
from committed bytes only:

```python
# §2.4 — the successor genuine-class instrument + the HEAD conversion partition
from pathlib import Path
from eval.meeting_quality import TournamentEvalReport, compute_conversion_report
from eval.vote_correctness import compute_supplied_channel_conversion
for d in ["replays/samples/9p2i", "replays/samples/4p1i",
          "replays/ml_corpus/9p2i", "replays/ml_corpus/4p1i"]:
    rep = TournamentEvalReport.model_validate_json(
        (Path(d) / "tournament-eval-report.json").read_text(encoding="utf-8"))
    s = compute_supplied_channel_conversion(rep.report)   # 70/79, 10/11, 222/259, 20/20
    c = compute_conversion_report(rep.report.games)       # 9p2i samples: coerced 1, inversions 87
```

```python
# §9 — the phase-complete frontier, cross-checked against the gh-fed CLI with a git-log title index
import subprocess, sys; sys.path.insert(0, "scripts")
import compute_next_task as cnt
from _task_parser import parse_all_tasks
titles = [t for t in subprocess.run(["git", "log", "--format=%s", "--grep=^task 18"],
          capture_output=True, text=True, check=True).stdout.splitlines()
          if t.lower().startswith("task 18")]
errors: list[str] = []; tasks = parse_all_tasks(errors); assert not errors
print(cnt.compute_frontier(tasks, set(), titles, 18))            # dispatchable ['18.28'], merged 31
print(cnt.compute_frontier(tasks, set(), titles + [
    "task 18.28: the mover record + the phase close (operator + owner, $0)"], 18))  # dispatchable [], merged 32
```

The §2.5 Phase-18 instrument tier is the three module folds the 18.12 record audit's §10 names —
`eval.deception_instruments.compute_deception_instruments`,
`eval.kill_craft.compute_kill_craft_report`, `eval.off_menu.compute_off_menu_report` — walked over
each set's committed `tournament-eval-report.json`, plus an ad-hoc `kind` census for the
contradiction-flag table. The §3 anchors are computed from the same `eval/` folds
`scripts/measure_baseline.py` wires (`measure_baseline.measure_baseline` for R1 / ejection accuracy
/ impostor win, `eval.vote_correctness.compute_supplied_channel_conversion` for the successor,
`eval.funnel.compute_pooling_funnel` for roll-call and whereabouts lies), so every anchor cell
equals the CLI output above cell-for-cell. All canary statistics — Wilson 95% score interval,
pooled two-proportion z, and the band-fire threshold search — are computed numerically by the
snippet below from the §3.1 table's own k/n cells (its output reproduces every §3.1 CI/z column and
every §3.2/§3.3 threshold row cell-for-cell): **zero hand-computed figures anywhere in this
audit.**

```python
# §3 — the canary statistics, from the §3.1 table's own k/n cells (no other inputs)
from math import sqrt

Z = 1.959963984540054  # two-sided 95%

def wilson(k: int, n: int) -> tuple[float, float]:
    p, z2 = k / n, Z * Z
    c = (p + z2 / (2 * n)) / (1 + z2 / n)
    h = (Z / (1 + z2 / n)) * sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return c - h, c + h

def pooled_z(k_new: int, n_new: int, k_anchor: int, n_anchor: int) -> float:
    pp = (k_new + k_anchor) / (n_new + n_anchor)
    se = sqrt(pp * (1 - pp) * (1 / n_new + 1 / n_anchor))
    return (k_new / n_new - k_anchor / n_anchor) / se

def band_fire(k_anchor: int, n_anchor: int) -> int:
    # largest future k at the anchor's own n with pooled z <= -1.96 (the REGRESSION arm)
    return max(k for k in range(k_anchor) if pooled_z(k, n_anchor, k_anchor, n_anchor) <= -1.96)

CELLS = [  # name, corpus k/n (anchor), samples k/n (continuity)
    ("R1 eject-decided win share", 106, 150, 31, 50),
    ("genuine-class successor",    222, 259, 70, 79),
    ("ejection accuracy",          248, 302, 78, 101),
    ("impostor win rate",           38, 150, 15, 50),
    ("whereabouts-lie mint rate",  147, 2380, 50, 843),
    ("roll-call coverage (crew)", 2035, 2042, 723, 726),
    ("roll-call coverage (imp)",   342, 684, 120, 245),
    ("roll-call answer rate",     2377, 2726, 843, 971),
]
for name, kc, nc, ks, ns in CELLS:
    lo, hi = wilson(kc, nc)                            # §3.1 Wilson CI (corpus)
    z = pooled_z(ks, ns, kc, nc)                       # §3.1 cross-set z (samples vs anchor)
    t_c, t_s = band_fire(kc, nc), band_fire(ks, ns)    # §3.2 corpus / §3.3 samples thresholds
    print(name, (round(lo, 4), round(hi, 4)), round(z, 3),
          f"{t_c}/{nc}", round(kc / nc - t_c / nc, 3), f"{t_s}/{ns}", round(ks / ns - t_s / ns, 3))
``` The §1 evidence cells are read from the committed
`training/reports/results-finalist-eval.jsonl` and `report-finalist-eval.md` §16.a, and the ruling
itself from `audits/audit-phase-18-flip-emergence.md` §3–§13.

## 11. Errata (coordination, 2026-08-19 — the Task 20.13 comparator-defect pass; additive, no in-place rewrites)

Anchor: the 2026-08-19 three-track review — `audits/review-2026-08-19/B/verdicts.md` C-3
(verdict **CONFIRMED and understated**) and `audits/review-2026-08-19/A/verdicts.md` G-12
(verdict **CONFIRMED-BUG**) — whose rates Task 20.15 landed as committed pins:
`tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` over
`eval/evidence_honesty.py`'s I-11 cells, with all four sets stated [VERIFIED] at
`audits/audit-phase-20-preregistration.md:174-175`. Every item below is **additive**: no
recorded byte, no table cell, no verdict and no hash above this section is rewritten, and
the committed `training/reports/results-finalist-eval.jsonl` is read, never edited. **One
reading does change, and it is named plainly** — items 1–2 make §1.1's win-edge column an
upper bound rather than a point estimate. Item 3 records what these items do **not** touch.

1. **The scripted comparator declines 45.8 % of its own free kills.** The kill seam
   re-validates only `targets[0]`, so over the 50 committed 9p2i seeds
   **190/415 = 45.8 %** of the policy's legal, zero-witness kill opportunities are
   declined. The misses are fully attributed: **168** in the ranking branch's exact-1.0
   score tie, broken by the lower player id; **15** in the named fellow-defer branch; **7**
   in the cover branch; **0 unattributed**. Instrument:
   `eval/evidence_honesty.py`'s I-11 free-kill cells, pinned by
   `tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins`. The
   reconstruction replays `decide()` against the recorded bytes, so this is the committed
   comparator's own behaviour, not a model of it.

2. **The same policy spends 8–12 % of its 9p2i decisions ranking a player already out of
   the game.** The dead-set is built only from *seen* bodies, so an ejected player stays
   targetable: **303/2461 = 12.3 %** on `replays/samples/9p2i` (222 of them ejected, 81
   never-witnessed deaths) and **555/6663 = 8.3 %** on `replays/ml_corpus/9p2i`, against
   **0/632** and **0/579** on the two 4p1i sets — a nine-player-roster phenomenon. 10,335
   impostor decisions were re-run offline against the recorded action stream with **0
   mismatches**, and one seed (36) is a demonstrably thrown game. Same instrument, same
   pins.

   **Direction of the confound, stated plainly.** Both defects **depress the comparator**:
   they cost it kills and waste its decision budget. §1.1's `p18-fsm-comparator` cell
   (13/50 = 0.26) is therefore a floor, and the four learned arms' win edges (**+0.12 to
   +0.30**) are **upper bounds** on the real gap. So are the paired impostor-side McNemar
   cells the Task-19.20 erratum added at `training/reports/report-finalist-eval.md` §18
   item 1, which test those same edges against those same comparator rows. A corrected
   comparator can only narrow them.

3. **What items 1–2 do NOT touch.** The referee verdicts stand — the defects cost the
   comparator wins, not evidence supply, and a stronger comparator would not have made a
   learned arm more watchable, so the four referee FAILs are if anything understated. The
   **NO-FLIP ruling stands** (it turns on the AND-criterion, and every candidate fails the
   referee half outright). The fourteen pre-registered emergence rulings, the zero-EMERGENT
   tally, and N1/N2's rate contrasts stand: they are witnessed-kill and co-present-kill
   *rates*, measured per kill, not win-rate differences. This close's own McNemar cell is
   the **crew** pair (§4, `0bf179b7…` gen-9 against its same-opponent gen-0 control,
   exact p = 1.0) — a different comparison against a different control, untouched here.
   The pre-registration ordering stands. **The repair is routed, not performed here:**
   Task 20.32 fixes the mover and
   Task 20.38 re-measures on corrected bytes. This erratum states the confound; it neither
   repairs it nor re-measures anything.
