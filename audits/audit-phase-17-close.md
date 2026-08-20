# Phase-17 close — NO-FLIP: the default mover stays scripted, no baseline 6 (Task 17.17)

**Date:** 2026-07-18.
**Task:** 17.17 — the mover baseline record + the phase close (operator + owner, $0), executed on
the contract's **NO-FLIP path**: Task 17.16 read 17.14's committed evidence against locked
decision 2 and ruled the **FAIL branch** (PR #285, merged `e30078d` — the owner's ratification,
the 15.18 convention), so **no record is performed**. The ladder tip STANDS at **baseline 5**
(the 16.17 close re-record, recording commit `2428044`, `Qwen/Qwen3.6-27B`, `qwen3_6_27b` v3,
nine always-on levers, `absence_prior` OFF).
**Sets:** `replays/samples/9p2i` + `replays/samples/4p1i` — **byte-untouched** by this close and
re-verified at HEAD (§2). `replays/ml_corpus/` — byte-untouched (recorded once at 17.9), the
Q3-restored canonical canary denominator (§3).
**Untouched by design (the FLIP-path artifacts):** `eval/watchability.py` floor blocks (no
baseline-6 block exists — grep-proven, `_BASELINE_SUPPLY_FLOORS` holds exactly baseline-2..5),
`audits/baseline5-final-measure.json` (never created — the BEFORE column exists only to
attribute a record, and no record happened), `agents/` + `training/` (frozen at 17.16).
**Grounding:** every number below is a fold over committed artifacts via the committed CLIs at
HEAD (`scripts/validity_gate.py`, `scripts/measure_baseline.py` core / `--funnel` /
`--watchability` / `--vj`, `scripts/verify_samples.sh` bare), plus two documented census folds
whose exact reproduce snippets are quoted in §9 (the 15.18 convention). Zero hand-computed
figures except the labeled Wilson/z statistics, whose inputs are quoted beside them.

**Verdict in one line:** Phase 17 **CLOSES with NO mover record** — locked decision 2's
AND-criterion (referee PASS **and** retained win edge) fails for both finalists on the real
baseline-5 path (`utility-es`: win 0.52 = 26/50, Δ **+0.16** over the same-seed FSM 0.36, but
referee FAIL on flags/meeting 0.4255 < 0.50279 and testimony-backed conversion 0.3585 < its
population-relative derived floor 0.5601; `policy-es`: referee PASS 48.20 but win 0.02 = 1/50,
Δ **−0.34** — the vent-tell annihilation, again), so the scripted FSM **stays the default
mover**, the learned champion **stays opt-in** (the 15.20/15.21 posture; byte-identical to the
re-selected finalist, sha `6d327dcb…`), **baseline 6 is NOT recorded**, and the ladder tip
stands at baseline 5. Both canonical sets and both corpus sets re-verify at HEAD (hard gate
10/10 PASS each; bare byte-identity clean; referee PASS at exact floor equality), and every
Wave-0 instrument repair is live in this close's own reads: the J1 clamp-exemption zeroes the
phantom breaches (5 → **0**, 17.1), the coerced-SKIP bucket files the two J2-coerced ballots
with inversions honest (99 → **98** + 2 coerced, 17.2), the spectator chips serve both live
markers view-layer-only (17.3), and the genuine-class successor instrument reads a NON-ZERO
denominator at last (63/70 = 0.90 on the 9p2i samples; **211/241 = 0.8755** on the corpus
denominator — canary-eligible for the first time, 17.6). The starved-economy referee FAIL on
`utility-es` is the selection bar working as designed — a co-adapted impostor makes convictions
harder, which is exactly what the population-relative conversion floor prices — recorded here
as the phase's honest finding, not a tooling defect.

---

## 1. The ruled path — locked decision 2 read against the committed evidence (the finding)

**The criterion (locked decision 2, `tasks/phase-17.md`):** the re-selected champion becomes
the DEFAULT mover iff it **PASSES the baseline-5 referee** (supply floors +
population-relative conversion + geomean) **AND retains its win edge** at the real-LLM finalist
eval. FAIL on either ⇒ it stays opt-in, the close records the finding, and NO mover baseline is
recorded — the ladder tip stays where the meeting layer left it.

### 1.1 The evidence (committed: `training/reports/results-finalist-eval.jsonl` + report §3.a)

Recorded 2026-07-18 on the real Featherless baseline-5 path, 50 seeds (0–49) 9p/2i per
finalist, $0, stamp-proven (50/50 `stamp == sidecar` each), validity gate PASS both:

| finalist | referee mean/med | imp. win | Δ vs FSM 0.36 | ej. accuracy | witnessed rate | flags/meeting | backed conv. |
|---|---|---|---|---|---|---|---|
| `utility-es` | 41.47 / 42.7 (**FAIL** — 2 gauges) | **0.52** | **+0.16** | 0.866 (58/9 of 67) | 0.2078 (48/231) | 0.4255 | **0.3585** (floor 0.5601) |
| `policy-es` | 48.20 / 49.6 (**PASS**) | **0.02** | **−0.34** | 1.000 (97/0 of 97) | 0.1194 (8/67) | 1.7748 | 0.9417 (floor 0.1343) |
| baseline 5 (FSM, same seeds) | 42.25 / 46.55 (**PASS**) | **0.36** | — | 0.914 (64/6 of 70) | 0.03448 (7/203) | 0.50279 (90/179) | 0.4741 (64/135) |

(One transcription note: the committed report's FSM row prints "42.25 / 0.2" — the 0.2 is the
4p1i median (`audits/audit-phase-16-close.md` §5); the 9p2i median re-read at HEAD is 46.55
(§2.2). Mean, floors, and every gauge cell agree exactly; no verdict is touched.)

### 1.2 The floor arithmetic (which floor failed, by how much)

The baseline-5 9p2i floor pins (`eval/watchability.py:755-762`, unchanged by this close) and
the 16.11 population-relative rule:

```
derived conversion floor = min(1.0, 0.4740740740740741 × (0.5027932960893855 / measured_flags_per_meeting))
```

| finalist | gauge | measured | floor (pin/derived) | distance | verdict | noise / clearance |
|---|---|---|---|---|---|---|
| **utility-es** | witnessed_event_rate | 0.2078 (48/231) | 0.03448 (7/203) | +0.1733 | PASS | z = +5.42σ |
| | flags_per_meeting | 0.4255 | 0.50279 (90/179) | **−0.0773** | **FAIL** | starved supply |
| | testimony_backed_conversion | 0.3585 | **0.5601** (derived: 0.474074 × 0.502793/0.4255) | **−0.2016** | **FAIL** | floor LIFTED by the starved flags |
| **policy-es** | witnessed_event_rate | 0.1194 (8/67) | 0.03448 (7/203) | +0.0849 | PASS | z = +2.63σ |
| | flags_per_meeting | 1.7748 | 0.50279 (90/179) | +1.2720 | PASS | the vent tell floods flags |
| | testimony_backed_conversion | 0.9417 | 0.1343 (derived) | +0.8074 | PASS | crew converts the tell |

Both witnessed-rate clearances sit well beyond 1σ against the rare-event 7/203 pin (SE ≈
0.0128) — no within-noise call applies, so the verdict is not a coin-flip rejection at the
band edge (the 17.12 discipline exists precisely so one would be legible).

**The AND, read:**

- `utility-es` — win edge **YES** (0.52 vs 0.36, Δ +0.16; 26 impostor wins, all by parity,
  inside games markedly evidence-richer than the FSM's: witnessed rate 0.208 vs 0.034,
  z = +5.42σ) but referee **FAIL**: it starves the flag economy (−0.0773 under the supply
  floor), and the starved supply LIFTS its population-relative conversion floor to 0.5601,
  which its 0.3585 conversion misses by −0.2016. **Fails the AND.**
- `policy-es` — referee **PASS** (48.20; every floor cleared because the crew reads its vent
  play trivially) but win edge **NO** (0.02, Δ −0.34; 49/50 crew wins, 47 by ejection, every
  one of its 97 ejections a true impostor). The same competitive annihilation the Phase-15
  pause recorded (0/50 there), re-confirmed on the co-adapted layer. **Fails the AND.**

**Consequence, implemented at 17.16 (the FAIL branch) and standing at this close:** the
scripted FSM stays the default mover on every default-SELECTOR surface, the champion stays
opt-in, and the swap clause was a no-op by identity — the re-selected finalist is
byte-identical (sha `6d327dcb…`) to the committed champion.
`tests/scripts/test_champion_flip_ruling.py` pins all of it from committed bytes: the
locked-decision-2 verdict re-derived (every floor, the conversion figures, the win edges
against the committed same-seed FSM comparator 18/50 = 0.36), the default-selector surfaces
(`scripts/run_tournament.py` default + the orchestrator's default factory selection) on the
scripted FSM, the absent-stamp fallback (`FSM_DEFAULT_POLICY_ID` untouched) on fresh and
committed canonical bytes, and the opt-in surface sha-coherent against the evidence row
field-for-field.

### 1.3 What Phase 18 would need (the honest scoping)

- **To flip the default:** a mover that closes `utility-es`'s two gaps **without surrendering
  the edge** — lift flags/meeting by ≥ +0.0773 to the 0.50279 supply floor AND lift conversion
  to its own (then-lower) derived floor (−0.2016 at today's economy), while keeping the win
  rate at or above the same-substrate FSM's. The bar itself STAYS (owner charter, the 17.12
  selection-bar-honesty ruling): a co-adapted impostor's objective is to make convictions
  harder, and the floor pricing that is the instrument working — the FAIL is the finding, and
  any future re-pricing of the bar is an owner decision, never an instrument edit.
- **The training-side gap the phase measured:** the re-grounded surrogate's decision channel
  is the always-SKIP constant (51.9% = 54/104 skip-majority; 0 ejections in 104 held-out
  meetings) and it is citation-blind by design (the 6-feature live-parity fence, locked
  decision 4; the 17.15 probe quantified the blindness: surrogate ejects 0/116 where the real
  path ejects 50/104). Training pressure toward the conviction economy the referee prices is
  therefore invisible on the surrogate path — a mover expected to CLEAR the conversion floor
  needs real-path training signal or a citation-aware surrogate, both Phase-18-scoped IF the
  co-adaptation program continues there (§6).

---

## 2. The close's own instrument reads over the existing bytes (HEAD, this session)

The NO-FLIP close performs the same instrument battery the FLIP path would have — over the
existing bytes, with no record. Every Wave-0 repair is live in these reads.

### 2.1 Hard validity gate + bare byte-verification — PASS everywhere

`validity_gate.py --expected-model Qwen/Qwen3.6-27B --require-zero-cost`, 10/10 checks green
per set:

| set | games | meeting rate / resolved | provenance | byte-identical (bare) |
|---|---|---|---|---|
| `replays/samples/9p2i` | 50 | 1.00 / 179 | exact (v3 × 4, 9 levers, $0) | 0 drift |
| `replays/samples/4p1i` | 50 | 0.78 / 39 | exact | 0 drift |
| `replays/ml_corpus/9p2i` | 150 | 1.00 / 541 | exact | 0 drift |
| `replays/ml_corpus/4p1i` | 50 | 0.80 / 40 | exact | 0 drift |

`verify_samples.sh` under a bare environment (zero `AILIBI_*` exports): all 50 + 50 canonical
samples verified clean. The stamped flags equal the 16.17 slate on every game_over record
(nine levers `True`, `absence_prior` `False`).

### 2.2 Selection referee — PASS at exact floor equality (floors unmoved)

`measure_baseline.py --watchability --json` at the default `baseline-5` floors: 9p2i
`referee_passed: true`, every gauge at exact equality with its pin (witnessed 7/203, flags
90/179, conversion 64/135 with derived-ratio exactly 1.0), mean 42.25 / median 46.55; 4p1i
`referee_passed: true` (witnessed 1/61 ADVISORY per the 15.19 rare-event rule), mean 4.09 /
median 0.2. Exact equality is the derivation self-consistency the 16.11 re-anchor guarantees —
these ARE the bytes the floors were pinned from, unchanged.

### 2.3 Core + funnel — byte-stable against the Phase-16 close

The core R-gate cells and every funnel row reproduce `audits/audit-phase-16-close.md` §3–§4
exactly (same bytes, same folds): 9p2i R1 25/50, reason histogram `{EJECT 25, PARITY 18,
TASKS 7}`, ejection accuracy 64/70 = 0.914, impostor win 0.36, ballot ECE 0.056 (n=405);
funnel structured-vent 83/106, vent-mentioned 82/106, killer-accused 101, kill-witnessed 7,
hard-clue 133, killer-in-set 156, votes-outside 7, reporter-ejected 0; 4p1i R1 10/50, win
0.30, ejection accuracy 10/10 = 1.000. No cell moved — the close's reads confirm the sets are
the same substrate the phase selected on.

### 2.4 The V&J instruments — identical except where Wave 0 repaired the instrument

`measure_baseline.py --vj --json` (9p2i) against the Phase-16 close's §2 cells:

| instrument | 16.17 close read | **this close (HEAD)** | why it moved |
|---|---|---|---|
| provenance-sum breaches / rows checked | 5 / 2879 | **0** / 2879 | **17.1** — the gauge learned the J1 clamp-exemption; the five phantom rows (seed 12 meeting-2, the clamp's signature) are individually pinned exempt, and a synthetic true-breach fixture still fails |
| rendered-row mismatches | 0 | 0 | — |
| zero-flag conviction rate | 2/70 = 0.0286 | 2/70 = 0.0286 | — (both survivors soft-only AND cited) |
| citation compliance | 405/405 = 1.000 (327 turn + 146 obs, 0 dangling) | identical | — |
| coerced zero-flag markers (J2 fired) | 2 | 2 | — |
| nulled observation-id markers | 1 | 1 | — |
| roll-call coverage mean | 0.3629 | 0.3629 | — (crew 0.4624 / impostor 0.0894 — 17.4's decomposition, the gate's evidence) |
| whereabouts lies detected | 6 | 6 | — |
| echo rate / distinct-2 | 0.0038 / 0.2875 | identical | — |

**The conversion partition, recomputed at HEAD (17.2 live):** the two J2-coerced SKIPs divert
into the by-design `citation_coerced_skip_ballots` bucket — recompute over the committed 9p2i
bytes reads skips 652, correct 511, missed **139** (41 impostor-voter + 0 invalid-target +
**98** threshold inversions), coerced **2** (`headless-seed-39` p-5 CREWMATE,
`headless-seed-48` p-7 IMPOSTOR — pinned in
`tests/eval/test_meeting_quality.py::test_committed_9p2i_recompute_pins_the_coerced_bucket`).
One precision the pin records: the Phase-16 close §8 said "2 of 99 inversions" — imprecise on
the bytes; one of the two coerced ballots was an impostor-bucket entry, not an inversion, so
the honest correction is inversions 99 → 98 and impostor voters 42 → 41. The STORED
`tournament-eval-report.json` block still carries the pre-17.2 partition (141/99/42, coerced
folded to 0) — single-era until the next re-record, by design.

**The genuine-class successor (17.6 live) — a non-zero denominator at last:** on the committed
9p2i samples `compute_supplied_channel_conversion` reads **63/70 = 0.90** (witnessed-vent
70 supplied / 63 converted — 75 recorded `vent_sighting` rows deduped to 70 (meeting,
impostor) pairs; sighting-contradiction 0/0 and whereabouts-lie 0/0 honestly empty — the 6
recorded whereabouts-lie flags all name CREW liars), beside the legacy alibi-anchored cell at
**0/0** (NO-DATA, its second consecutive substrate — preserved as a labeled reported column,
never a canary). 4p1i: successor **10/10 = 1.0**, legacy 0/0. Committed-bytes pins:
`tests/eval/test_vote_correctness.py::test_committed_9p2i_report_pins_the_successor_instrument`
(and the 4p1i twin).

**The spectator chips (17.3 live, view-layer only):** both live audit-trail rewrites on the
committed bytes — the J2 coercion marker and the 16.5 nulled-observation marker — serve as
`rewrite_reasons` chips through `api.replay_loader._BALLOT_PREFIX_MARKERS`, fixture-pinned on
the committed live cases; the committed sets load, serve, and byte-verify unchanged.

4p1i V&J: identical to the 16.17 close throughout (zero-flag 0/10, compliance 24/24, echo
0.000, breaches 0).

---

## 3. The canary anchors on the Q3-restored corpus denominator (no canary fires — no record)

**No canary is judged at this close**: the §0.4 bands judge a RECORD against a pre-registered
anchor, and the NO-FLIP path records nothing. What this close records instead is the anchor
set the next record's pre-registration reads — on the corpus denominator the Q3 restoration
made canonical again (`replays/ml_corpus/README.md`: "With this baseline-5 re-record the
corpus is again the **canonical canary denominator** … operative again from this record.
Future phase closes re-adopt it."). These are **anchors, not pre-registrations** — the 15.18
discipline puts pre-registration in the §0 block of the record that uses it, before its first
recorded seed.

### 3.1 The corpus cells (150-game 9p2i: 541 meetings, 1303 EJECT ballots, `fsm-default` movers)

| cell | corpus 9p2i | Wilson 95% CI | 50-seed samples (context) | cross-set z |
|---|---|---|---|---|
| **R1 eject-decided win share** | 93/150 = 0.620 | [0.540, 0.694] | 25/50 = 0.500 | −1.494 (agrees) |
| **genuine-class successor** (the canary-eligible cell) | **211/241 = 0.8755** | [0.828, 0.911] | 63/70 = 0.900 | +0.557 (agrees) |
| zero-flag conviction rate | 19/242 = 0.0785 | [0.051, 0.119] | 2/70 = 0.0286 | −1.469 (agrees) |
| ejection accuracy | 229/242 = 0.9463 | [0.910, 0.968] | 64/70 = 0.9143 | −0.986 (agrees) |
| testimony-backed conversion | 228/421 = 0.5416 | [0.494, 0.589] | 64/135 = 0.4741 | −1.367 (agrees) |
| citation compliance | 1303/1303 = 1.000 (1086 turn + 467 obs, 0 dangling) | — | 405/405 = 1.000 | — |
| impostor win rate | 49/150 = 0.3267 | — | 18/50 = 0.36 | — |
| roll-call coverage (crew / impostor) | 0.3723 (0.4743 / 0.0896) | — | 0.3629 (0.4624 / 0.0894) | — |
| whereabouts lies detected | 25 (rate 0.0227) | — | 6 (0.0167) | — |
| provenance-sum breaches | 0 / 8105 rows | — | 0 / 2879 | — |

Successor channel split on the corpus: witnessed-vent 210/237, sighting-contradiction **1/1**,
whereabouts-lie **2/5** (the per-meeting union dedupes 243 channel pairs to 241 supplied /
211 converted) — the first substrate where all three supplied channels are non-empty. The
LEGACY alibi cell reads **1/1** on the corpus (its first non-zero read since baseline 3) and
0/0 on the samples — still a labeled reported column, never a canary; a substrate that
re-supplies checkable alibi lies at scale re-examines it (§6). Every cross-set z is inside
±1.96: the two same-substrate populations agree, so corpus-anchored bands can honestly judge
future same-shape records.

### 3.2 Leaving the 50-seed UNDERPOWERED regime (the band arithmetic)

The Phase-16 close's R1 warning stands re-quoted: *"R1 landed exactly on the pre-registered
band edge (25/50) and the close PROCEEDS … one fewer eject-decided win would have paused the
phase."* At n = 50 the pooled two-proportion REGRESSION arm (|z| ≥ 1.96) fires only on a
~20 pp drop; the corpus denominator tightens that materially:

| canary | anchor | band-fire threshold at the anchor's own n | minimal detectable drop |
|---|---|---|---|
| R1, 50-seed anchor | 25/50 = 0.500 | ≤ 15/50 = 0.300 (z = −2.041) | 20.0 pp |
| **R1, corpus anchor** | 93/150 = 0.620 | ≤ 76/150 = 0.5067 (z = −1.979) | **11.3 pp** |
| successor, 50-seed anchor | 63/70 = 0.900 | ≤ 54/70 = 0.7714 (z = −2.053) | 12.9 pp |
| **successor, corpus anchor** | 211/241 = 0.8755 | ≤ 195/241 = 0.8091 (z = −2.000) | **6.6 pp** |

The next adopting/close record pre-registers its bands from these anchors on the corpus
denominator (with 17.6's successor as a named canary cell), quotes them in its §0 block
BEFORE the first recorded seed, and reports the samples as the continuity anchor — the Q3
ruling, operative.

---

## 4. The phase's evidence chain (committed, provenance-stamped)

- **17.9 — the corpus re-record** (`replays/ml_corpus/`): 150-game 9p2i (seeds 1000–1149) +
  50-game 4p1i (seeds 1000–1049) at the final baseline-5 meeting layer, `seed % 5` splits
  (90/30/30 + 30/10/10, non-degenerate), MANIFEST provenance exact, FROZEN at `64b8cb6`
  (9p2i, 2026-07-16) / `3774aa4` (4p1i, 2026-07-15) with honest per-seed mixed dates (the
  16.14 precedent). Gates re-verified PASS at HEAD this close (§2.1). The Q3 restoration is
  stated in its README and operative (§3).
- **17.10 — the surrogate re-ground**: first **GO** on any substrate — top-1 0.8600 vs bar
  0.6150 (0.75 × the 0.8200 strict-argmax ceiling); vs FO-6 re-baseline 0.2200; SKIP-vs-eject
  0.5192 vs always-eject 0.4808 — with the honest diagnosis recorded beside it: the decision
  channel passes as the always-SKIP constant on a skip-majority economy, not by
  discrimination. Usage tier: **training-time runner** (locked decision 4; champion numbers
  are never surrogate-scored). Staleness cap re-derived: **62,491** meetings = 143 × 437
  baseline-5 fit-side meetings, sha-keyed (`62d6cbfa…`), never held at 50,000 by habit.
- **17.11 — the selection-bar flip**: `BAKEOFF_BASELINE_ID` → `"baseline-5"`, the goodhart
  default with it; the `eval/watchability.py` lag note reads CLOSED. Every candidate the
  phase scored was judged on the close-era floors.
- **17.12 — the full-slate bake-off re-run**: all four methods completed; ordinal ranking
  **UNCHANGED** vs Phase 15 (utility-es, policy-es, map-elites, bc-dagger); finalists = top-2.
  Three recorded movements, explained not smoothed: the referee geomean collapsed onto the
  D1×D4 lattice (the 15.19 conversion-coupled D2 gate — fine-grain geomean no longer
  discriminates), the surrogate divergence column went flat (the always-SKIP predictor), and
  the floors flipped under the citation-era economy. All four entrants FAIL the referee on
  the fake path (0 flags minted — the starved-economy read, legible per the floor-sensitivity
  columns). Surrogate consumption metered: 403 + 3,490 (17.15) of 62,491.
- **17.13 — the crew track re-run (measurement-only)**: both bases reproduce their Phase-15
  champions BIT-IDENTICALLY (the ES loops are deterministic and the levers act at a conviction
  channel these games never reach — 0 ejections in every triggered meeting); every verdict
  unchanged; no crew artifact ships and none can (the learned factory is impostor-only). The
  report's Phase-18 routing statement is quoted in §6.
- **17.14 — the multi-finalist recorder + real-LLM eval**: `run_tournament.py
  --candidate-artifact` productized (sha-verified load, fail-loud before spend, auto-stamp
  from the artifact's own `stamp.json`, conflation-guarded); both finalists recorded 50/50 on
  the real path, stamp-proven, validity PASS, $0 — the §1 evidence.
- **17.15 — the Goodhart re-probe**: the no-exploitable-seam conclusion **survives baseline 5
  at the measured scale, re-earned and narrowed** — the baseline-3 forced-kill exploit closed
  (+155% → +11.1%); no genome launders past the composed selection gate on any path; one NEW
  above-bar fake-path `mean_score` exploit on the 4p1i reference roster (`d4-contest-farming`,
  +61.8%) recorded and carried (§6); the citation-blind seam quantified (surrogate 0/116
  ejects vs real 50/104) — real, but not a seam an optimizer can push a champion through
  (floors + validity fail-close).
- **17.16 — the evidence-gated flip, FAIL branch**: §1.2. Nothing swapped; the default
  provably did not move (pinned).

---

## 5. The permanent record: the Phase-18 staleness rule (re-stated) + corpus validity

**Everything this phase trained, fitted, selected, or pinned is BASELINE-5-SUBSTRATE-ANCHORED.
Heterogeneous lobbies change the meeting layer AGAIN — nothing in this phase's artifacts
survives that unexamined. Re-ground before any training.** Specifically:

- **`replays/ml_corpus/`** (17.9) is baseline-5 meeting-layer calibration data with
  `fsm-default` movers. **At this close it remains canonical and same-substrate in full**: the
  mover default did NOT flip, so both the meeting layer and the mover layer are unchanged
  since the record — the close states this explicitly per the contract. The forward rule, for
  whenever a mover flip DOES land: a mover flip does not invalidate meeting-layer calibration
  data, but impostor-behavior-conditioned cells become champion-era from that adopting
  baseline on and must be read with that caveat. A Phase-18 meeting-layer change (personas
  per-model, heterogeneous lobbies, any pooling-prompt uptake work that ships) makes the
  corpus PRIOR-SUBSTRATE-ANCHORED again — re-record before any training against it.
- **The surrogate** (17.10) is fitted on the baseline-5 corpus; its GO verdict, its 62,491-use
  cap (derived from THIS corpus's 437 fit-side meetings), and its measured always-SKIP
  decision channel are all corpus-bound. Any meeting-layer change re-grounds it (the FO-6
  lesson, third statement running).
- **The bake-off rankings, finalist rows, and floor-sensitivity reads** (17.12/17.14) are
  baseline-5-conditioned selection evidence — they do not transfer across a meeting-layer
  change, and the finalist eval's 0.36 FSM comparator is these seeds on these bytes.
- **The floors** (`eval/watchability.py` baseline-5 blocks) are record-pinned to the standing
  sets; they move only at a record (the next one to land pins its own).
- **The champion** (`agents/tactical/learned/`, `utility-es`) stays OPT-IN with its 17.14
  real-path row as the recorded evidence (win 0.52 / Δ +0.16 / referee FAIL on the conversion
  economy). Those numbers are baseline-5-anchored and go stale at the next meeting-layer
  change like everything else.
- **The ratified absence bar** (new-over-gate ≤ 0.20 AND crew roll-call coverage ≥ 0.60)
  re-reads on the Phase-18 bytes, never on these (the gate audit's Ruling 3(d): if impostor
  templates change, the bar re-reads on the new bytes).

---

## 6. The routed contracts (Phase 18) — contracts, never silent gaps

1. **The absence-prior package** (the 17.7 gate's Ruling 3, quoted): *"Phase 18 owns, as one
   package: (a) the pooling-prompt uptake work that raises the answer rate (aggregate 0.363;
   the target is the §6 bar's crew clause, ≥ 0.60 crew coverage — and §3 shows the residual
   gap is substantially players who never take a meeting turn, so the work is turn-taking
   surface as well as template asks); (b) re-running this counterfactual on the Phase-18
   substrate and graduating at a Phase-18 adopting record IFF the ratified §6 bar passes;
   (c) the vent widening travels with that package and is re-ruled with it (Ruling 2); (d) the
   impostor-template refusal artifact (§3) is a named input to the Phase-18
   heterogeneous-lobby prompt work."* The mechanisms stay in the tree, tested and inert
   (`absence_prior` resolver; `include_vent_sightings` flag, no production call site).
2. **The pooling-prompt uptake work** — (a) above, named separately because it gates more than
   the absence prior: the genuine-class whereabouts-lie channel (§3.1: 2/5 corpus, 0/0
   samples) and the roll-call coverage floor both ride the answer rate.
3. **The crew deployment surface** (the 17.13 report §7, quoted): *"a crew deployment surface
   is heterogeneous-lobby work … heterogeneous lobbies change the meeting layer AGAIN, so
   nothing in this phase's artifacts — these measurement-tier crew candidates included —
   survives that unexamined."* The open measurement (does the citation-era conviction channel
   move an owned-task crew's pace-to-wins conversion on the REAL path?) travels with it.
4. **The detector-band relaxation package** (record-time substrate changes, deliberately NOT
   done inside instrument tasks): relaxing the contradiction detector's endpoint band so
   roll-call lies mint interior flags (the 17.6 designer ruling routed it here), and feeding
   grounded vent placements into the physical-contradiction detector (the 17.5 scope
   firewall's flag-minting variant). Both are one-layer-per-baseline substrate moves for a
   Phase-18 adopting record.
5. **Carried findings**: the `d4-contest-farming` fake-path exploit on the 4p1i reference
   roster (17.15, +61.8% above the materiality bar — re-probe before any 4p1i-scored
   selection); the 4p1i sparse-roster geomean watch-flag (median 0.2 — a watchability
   finding, not a floor); the legacy alibi cell's re-examination trigger (a substrate that
   re-supplies checkable alibi lies — the corpus's 1/1 is the first flicker); the surrogate
   citation-channel gap (§1.3 — a citation-aware surrogate or real-path signal if mover
   training is to price the conviction economy); the impostor win rate at 0.36 (9p2i
   samples) / 0.3267 (corpus) with the champion opt-in holding +0.16 over it — the
   competitive headroom Phase 18's lobbies will surface.

---

## 7. Provenance + Q5

- **No record at this close ⇒ no new recording commit ⇒ no new Q5 tag point.** The contract's
  "Q5 tag" clause binds on the FLIP path; the NO-FLIP arm is the **fallback**, named here per
  the DoD: this close's provenance point is the 17.17 PR's merge commit itself — durable in
  `main`'s history and named by this audit — and the owner MAY additionally tag it
  (`git tag -a phase-17-close <merge-sha> -m "Q5: Task 17.17 NO-FLIP close" && git push origin
  phase-17-close`) at leisure. Nothing this close produced requires byte-level provenance
  beyond git itself: no replay bytes moved.
- **The phase's operator records already carry their Q5 arms** (the sha arm in both cases —
  this environment's credential refuses tag pushes, the 16.14/16.17 limitation):
  - the corpus (17.9): FROZEN-line shas `64b8cb6` (9p2i) / `3774aa4` (4p1i) + per-row MANIFEST
    `git_sha`; the recording commits are squash-unreachable from `main` (the record merged as
    `aa11ae6`, PR #278), and byte-verification is the operative guarantee — re-proven at HEAD
    by this close's gate runs (150/150 + 50/50 byte-identical, §2.1);
  - the finalist eval (17.14): `recording.recording_git_sha = 2a9b369` on both committed rows
    — the recorder-code commit, whose recorder (`scripts/run_tournament.py
    --candidate-artifact`) is a committed file at HEAD, so the rows are re-recordable from
    `main` alone (report §6).
- **The ladder tip's Q5 tag arm is COMPLETE**: `git ls-remote --tags origin` at this close
  observes `phase-16-baseline-5` → `2428044` (and `phase-16-baseline-4` → `a43b178`) on the
  remote — the deferred owner arm recorded in `audits/audit-phase-16-close.md` §7/§9 has been
  executed. The standing baseline's recording commit is durably reachable server-side by tag.

---

## 8. Decisions

- **The ruled path is NO-FLIP and nothing is recorded.** `replays/samples/`,
  `eval/watchability.py`, and the never-created `audits/baseline5-final-measure.json` are
  intentionally untouched: the BEFORE column exists to attribute a record, and no record
  happened (the implementation hint's "resist recording anything" honored). The close's value
  is the §1 finding.
- **No test changes ship in this PR.** No bytes moved, so every committed-bytes pin holds
  (§2 re-ran them green); the byte-coupled counterfactual sweep every record performs is
  vacuous with no new bytes; no test reads phase-doc banners or this audit (grep-proven —
  the only near-miss, `tests/scripts/test_champion_flip_ruling.py`, pins the 17.16 FAIL state
  from committed evidence bytes and is exactly the "default provably does not move" pin this
  close relies on).
- **The §3 corpus cells are anchors, not pre-registrations.** Pre-registration is a §0-block
  act of the record that uses it (the 15.18/16.17 discipline); this close records the anchor
  arithmetic so that record can pre-register on a powered denominator.
- **The "2 of 99" refinement is adopted from the 17.2 pin** (one coerced ballot was
  impostor-bucket, so inversions read 98, not 97): the Phase-16 close's §8 phrasing was
  imprecise on the bytes, and the recompute + pinned identities are the corrected record.
- **`compute_next_task.py --phase 17` is demonstrated with the real merged-title index.** The
  `gh` CLI is unavailable in this environment (the script's documented offline degradation),
  so the frontier was computed by feeding `compute_frontier` the 15 merged `task 17.*` PR
  titles from `git log` (§9): at HEAD the frontier is dispatchable `[17.17]` / blocked `[]` /
  merged 15; with this PR's title added it reads dispatchable `[]` / blocked `[]` / merged 16
  — the phase computes complete on merge. The task-doc parse is error-free (validator green).
- **The Q5 fallback arm is the merge commit + optional owner tag** (§7) — no recording commit
  exists to tag on the NO-FLIP path.
- **The banner, README, and roadmap record the close in the same PR** (`tasks/phase-17.md`
  STATUS → CLOSED; README project-status + roadmap paragraphs; the
  `tasks/post-phase-14-plan.md` spine annotates baseline 6 NOT RECORDED with this audit as
  provenance). The owner ratifies this close reading by merging this PR (the 15.18
  convention) — the phase's second owner gate.

---

## 9. Method + reproduction (all $0 against committed bytes, offline)

```
uv run python scripts/validity_gate.py replays/samples/9p2i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10)
uv run python scripts/validity_gate.py replays/samples/4p1i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10)
uv run python scripts/validity_gate.py replays/ml_corpus/9p2i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10, 150 games)
uv run python scripts/validity_gate.py replays/ml_corpus/4p1i \
    --expected-model Qwen/Qwen3.6-27B --require-zero-cost    # PASS (10/10)
uv run python scripts/measure_baseline.py --json                 # §2.3 core cells
uv run python scripts/measure_baseline.py --funnel --json        # §2.3 funnel
uv run python scripts/measure_baseline.py --watchability --json  # §2.2 referee (baseline-5)
uv run python scripts/measure_baseline.py --vj --json            # §2.4 V&J instruments
uv run python scripts/measure_baseline.py replays/ml_corpus/9p2i --json        # §3.1 R1 93/150
uv run python scripts/measure_baseline.py replays/ml_corpus/9p2i --vj --json   # §3.1 corpus V&J
bash scripts/verify_samples.sh                                   # byte-identical, BARE env
```

The two documented census folds (the only cells the CLIs do not emit directly), reproducible
from committed bytes only:

```python
# §2.4 / §3.1 — the successor genuine-class instrument + the HEAD conversion partition
from pathlib import Path
from eval.meeting_quality import TournamentEvalReport, compute_conversion_report
from eval.vote_correctness import compute_supplied_channel_conversion
for d in ["replays/samples/9p2i", "replays/samples/4p1i",
          "replays/ml_corpus/9p2i", "replays/ml_corpus/4p1i"]:
    rep = TournamentEvalReport.model_validate_json(
        (Path(d) / "tournament-eval-report.json").read_text(encoding="utf-8"))
    s = compute_supplied_channel_conversion(rep.report)   # 63/70, 10/10, 211/241, 20/20
    c = compute_conversion_report(rep.report.games)       # 9p2i samples: coerced 2, inversions 98
```

```python
# §8 — the phase-complete frontier with the real merged-title index (gh unavailable here)
import subprocess, sys; sys.path.insert(0, "scripts")
import compute_next_task as cnt
from _task_parser import parse_all_tasks
titles = [t for t in subprocess.run(["git", "log", "--format=%s", "--grep=^task 17"],
          capture_output=True, text=True, check=True).stdout.splitlines()
          if t.lower().startswith("task 17")]
errors: list[str] = []; tasks = parse_all_tasks(errors); assert not errors
print(cnt.compute_frontier(tasks, set(), titles, 17))                  # dispatchable: [17.17]
print(cnt.compute_frontier(tasks, set(), titles + ["task 17.17: x"], 17))  # dispatchable: []
```

The canary statistics are the standard formulas (pooled two-proportion z; Wilson 95% CI)
computed from the CLI cells quoted beside them in §3. The §1 evidence cells are read from the
committed `training/reports/results-finalist-eval.jsonl` + `report-finalist-eval.md` §3.a/§3.1a
(recorded 2026-07-18, stamp-proven, $0), and the 17.16 FAIL-branch pins re-run green in
`tests/scripts/test_champion_flip_ruling.py`.

## 10. Errata (coordination, 2026-08-19 — the Task 20.13 comparator-defect pass; additive, no in-place rewrites)

Anchor: the 2026-08-19 three-track review — `audits/review-2026-08-19/B/verdicts.md` C-3
(verdict **CONFIRMED and understated**) and `audits/review-2026-08-19/A/verdicts.md` G-12
(verdict **CONFIRMED-BUG**) — whose rates Task 20.15 landed as committed pins:
`tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` over
`eval/evidence_honesty.py`'s I-11 cells, with all four sets stated [VERIFIED] at
`audits/audit-phase-20-preregistration.md:174-175`. Every item below is **additive**: no
recorded byte, no table cell, no verdict and no hash above this section is rewritten. **One
reading does change, and it is named plainly** — item 1 makes §1's `utility-es` win edge an
upper bound. Item 2 records what this erratum does **not** touch.

1. **The same-seed scripted comparator this close measures against carries two identified
   target-selection defects, both of which depress it.** The review found that
   `agents/tactical/impostor_policy.py` re-validates only the top-ranked target at the kill
   seam, and builds its dead-set only from *seen* bodies. Measured over the committed 9p2i
   sets: **190/415 = 45.8 %** of legal zero-witness kill opportunities declined (**168** on
   the ranking branch's exact-1.0 score tie broken by the lower player id, **15**
   fellow-defer, **7** cover, **0 unattributed**), and **303/2461 = 12.3 %**
   (`replays/samples/9p2i`) / **555/6663 = 8.3 %** (`replays/ml_corpus/9p2i`) of impostor
   decisions topping the target list with a player already ejected — **0/632** and
   **0/579** on the two 4p1i sets, so it is a nine-player-roster phenomenon.

   **Scope of this item, honestly.** Those rates are measured on the committed sample and
   corpus sets, **not** re-measured on this close's own finalist recordings (raw slate
   off-repo, §7). What carries across is the *policy*: the FSM row §1 pairs against —
   `baseline 5 (FSM, same seeds)`, win **0.36** — is the same scripted policy, so it plays
   under the same two defects. Its 0.36 is therefore a floor, and `utility-es`'s
   **Δ +0.16** is an **upper bound** on the real gap.

2. **What item 1 does NOT touch.** The referee FAIL on `utility-es` stands: it failed on
   flags/meeting 0.4255 < 0.50279 and testimony-backed conversion 0.3585 < 0.5601, gauges
   about evidence supply rather than wins, and a comparator that killed more often would
   not have raised them. The **NO-FLIP ruling stands** — locked decision 2's AND-criterion
   fails on the referee half alone. `policy-es`'s Δ −0.34 collapse stands and is only made
   worse by a stronger comparator. No recorded byte, no instrument read and no canary in
   this close moves. **The repair is routed, not performed here:** Task 20.32 fixes the
   mover and Task 20.38 re-measures on corrected bytes.
