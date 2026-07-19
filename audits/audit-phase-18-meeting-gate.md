# Phase-18 meeting-layer gate — the package probe + ruling (Task 18.11)

**Date:** 2026-07-19 (the offline evidence sections and the §2 pre-registered bars were
assembled and quoted BEFORE any probe seed recorded and BEFORE the ruling was requested — the
15.18 pause shape, evidence first, decision slots explicit; the 17.7 memo-then-ruling shape).
**Task:** 18.11 — THE MEETING-LAYER GATE: probe + ruling (operator ~8–9 h + owner) + phase-doc
surgery.
**What is being ruled:** the Phase-18 meeting-layer PACKAGE, as one substrate decision
(`tasks/phase-18.md` locked decision 2; `audits/audit-phase-18-planning.md` §3.4 + §7): the
18.8 roll-call round + the 18.9 endpoint-band whereabouts exemption + the 18.9 vent-placement
flag-minting variant + the 18.10 impostor-answer template arm, with the absence-prior
graduation (`audits/audit-phase-17-absence-gate.md` Ruling 3's re-measure path) riding the
ruling. The owner rules **FULL / CREW-ONLY / NONE**; the CREW-ONLY fallback and the NONE
surgery are pre-authored below (§9). The four mechanisms are BUILT (18.7–18.10, merged) and
inert default-OFF; this gate rules what GRADUATES, it never edits a mechanism.
**Method:** every OFFLINE evidence row below is a committed, test-pinned cell quoted with its
source file and line — zero fresh offline measurement (the gate reads Wave-1's already-merged
counterfactuals: 18.9's exemption + vent censuses, 18.8's turn-cost arithmetic, and the
baseline-5 absence + roll-call-coverage pins). The LIVE probe cells (§7) are the two 25-seed
real-path recordings the ruling turns on; they are the operator leg and are recorded to
working artifacts OUTSIDE the tree (the finalist-eval separation discipline), with only the
measurements folded into this memo.
**Label key:** **[VERIFIED]** read directly in a committed source / test pin · **[INFERRED]**
reasoned from verified cells (arithmetic quoted) · **[PENDING]** awaits the operator probe or
the owner ruling — recorded here as an explicit open slot, never a guessed value.

## 0. Verdict in one line

**PENDING — offline evidence complete; the LIVE probe and the owner ruling have NOT been
executed.** The four mechanisms are merged and inert; the substrate-flag snapshot registry that
makes a probe/adoption recording self-describe its arms is wired in this PR (§6), and the
offline `extract_gameplay_facts` opt-in-eligibility gate is relaxed under the recorded roll-call
stamp so ON-path recordings do not false-flag (verified correct AND load-bearing against real
roll-call transcripts, §6). What remains is the OPERATOR leg — two 25-seed 9p2i real-path
recordings (FULL and CREW-ONLY), ~8–9 h at 2 workers — and the OWNER ruling on the assembled
cells. Per the Task-18.11 integration-risk note and the 17.14 PENDING pattern, **this PR stays
open with the memo complete and the DoD honest; no ruling that has not happened is recorded, and
no surgery in a ruled direction is performed.** The ruling slots (§9) are pre-authored so the
owner rules against a criterion, not a vibe (the 15.18 convention); the surgery (§10) executes
only once the probe lands and the owner signs.

## 1. What this gate decides — the package and its arms [VERIFIED]

`tasks/phase-18.md` locked decision 2 ratified the meeting-layer package to run in-phase, FIRST,
behind THIS gate, BEFORE any adoption. The four arms (`audits/audit-phase-18-planning.md` §3.3–
§3.4, §7):

1. **The roll-call round (18.8)** — a flag-gated turn-allocation surface: after the co-presence
   opt-in phase and before ballots, every living player who has not yet spoken takes exactly one
   terminal `opt_in`-surface whereabouts turn, ascending id order. The ONLY surface that can
   reach the ratified ≥ 0.60 crew clause (template asks structurally cap coverage at 496/1057 =
   0.469 — §3, `audits/audit-phase-18-planning.md` §3.4). Cost: +3.13 turn calls/meeting (496 →
   1057 over the samples denominator, 2.13×), ~+36 % meeting LLM calls.
2. **The endpoint-band whereabouts exemption (18.9, lever 1)** — a degenerate single-tick
   self-alibi (`from_tick == to_tick`) contradicted by a first-hand sighting mints a STRONG
   `alibi_vs_sighting` flag instead of being endpoint-banded to weak. Converts a roll-call
   answer into conviction-economy currency.
3. **The vent-placement flag variant (18.9, lever 2)** — a GROUNDED spoken vent sighting (matched
   against the speaker's own `VentWitnessRecord`, the 15.4 chokepoint) whose record contradicts
   the subject's own stated path mints a STRONG `alibi_vs_physical` flag. The 17.7 Ruling-2 HOLD
   travels here and is re-ruled with the package; the FULL probe runs it ON so its live flag
   yield is measured, not extrapolated.
4. **The impostor-answer template arm (18.10)** — a flag-selected impostor template variant
   (`qwen3_6_27b` only) in which the impostor opening and reply ANSWER the whereabouts ask with a
   structured self-placement (which the two-tier design lets be a lie) instead of the hard-coded
   `"observations": []`. The gate's highest-variance arm: it manufactures catchable impostor lie
   material but re-opens the ≥ 44 % self-flag class the prompt ladder closed.

Riding the ruling: the **absence-prior graduation** (`audits/audit-phase-17-absence-gate.md`
Ruling 3(b) routed the baseline-5 re-measure to Phase 18; §6 there ratified the bar: graduate
only when new-over-gate ≤ 0.20 AND crew roll-call coverage ≥ 0.60). Both clauses are re-read on
the probe bytes (§4, §3), so the absence prior graduates iff the round delivers the calibration
the close's theory predicted.

## 2. The pre-registered bars [VERIFIED — quoted from `tasks/phase-18.md`:715-721]

The bars are fixed BEFORE the probe records (pre-registration binds the rules before
measurement — the 18.4 discipline; `audits/audit-phase-18-emergence-preregistration.md`). The 25-seed
probe is deliberately underpowered for fine effects; the bars are chosen so a **fail is a > 1σ
read at n = 25** — the crew-coverage and self-flag cells have per-meeting denominators well above
25 (a 25-seed 9p2i probe reconstructs ~80–95 meetings with ~7 living crew each, so the crew
placement denominator is in the hundreds), and the two-proportion z is quoted beside each
verdict.

| # | bar | threshold | measured on | ships |
|---|---|---|---|---|
| **(a)** | crew roll-call coverage on the probe | **≥ 0.60** | live probe, `roll_call_coverage_crew_mean` (`eval/funnel.py:1835`) | the round + the crew clause (and the absence graduation) |
| **(b)** | absence counterfactual, new-over-gate, re-run on probe bytes | **≤ 0.20** | live probe, the `TestAbsencePriorOnCommittedBytes` walk re-pointed at the probe dir | the absence-prior graduation |
| **(c)** | impostor-answer arm: probe impostor win **≥ 0.20** (not annihilated; FSM comparator 0.36) **AND** STRONG self-flag rate **≤ 0.25** of answered impostor roll-calls | **≥ 0.20 / ≤ 0.25** | live FULL probe | the impostor-answer template arm |
| **(d)** | the vent widening **AND** its flag-minting variant, re-ruled with the package (the 17.7 Ruling-2 HOLD travels here) | live yield measured, not extrapolated | live FULL probe (variant ON) | the vent variant |

**The z convention (the phase-16/17 close canaries; `audits/audit-phase-18-emergence-preregistration.md`:463-467):**
the POOLED two-proportion z,

> z = (p̂_c − p̂_f) / √( p̂ (1 − p̂) (1/n_c + 1/n_f) ),  p̂_c = k_c/n_c, p̂_f = k_f/n_f,
> p̂ = (k_c + k_f)/(n_c + n_f),

fired two-sided at |z| ≥ 1.96; where the pooled rate is 0 or 1 the z is undefined and no delta
exists. Each verdict below quotes the z against the relevant comparator (the OFF-path baseline
cell, or the bar threshold treated as the null proportion on the probe denominator).

## 3. Evidence row 1 — crew roll-call coverage: the round is the only surface to 0.60 [VERIFIED]

Source: `tests/eval/test_funnel_pooling.py` committed pins (baseline-5 9p2i), the 17.4 uptake
breakdown the 17.7 gate already ratified.

| cell (9p2i, OFF-path — no round) | committed pin | source |
|---|---|---|
| crew roll-call coverage mean | **0.46238361266294226** | test_funnel_pooling.py:712-714 |
| impostor coverage mean | **0.0893854748603352** | :715-717 |
| roll-call placed totals (crew / impostor) | **331 / 29** | :704-705 |
| asked / answered / answer-rate among speakers | **496 / 360 / 0.7258** | :728-730 |
| aggregate coverage mean | 0.3628558127161479 | :642 |
| 4p1i crew / impostor coverage | 0.7821 / 0.1538 | :746-749 |

**The read:** on the current substrate crew coverage is **0.4624 < 0.60 — the ratified clause
FAILS off-path**, and `audits/audit-phase-18-planning.md` §3.4 pins the structural ceiling:
template-ask-only caps total coverage at asked/living = 496/1057 = 0.469, so **no template change
can reach 0.60**. The roll-call round is the only surface that asks every living non-speaker
(561/1057 = 53 % of living player-meetings never speak at all off-path). Whether the round
DELIVERS ≥ 0.60 crew coverage — every living crewmate self-placing every meeting — is exactly
what the live probe measures (bar (a)); it cannot be read off-path because the round does not
exist in the committed bytes. **[PENDING — §7 cell (a).]**

## 4. Evidence row 2 — the absence counterfactual: 0.296 off-path, the round must shrink it [VERIFIED]

Source: `tests/agents/test_absence_prior.py::TestAbsencePriorOnCommittedBytes` (baseline-5 9p2i,
the same walk the 17.7 gate ruled on).

| cell | baseline-5 committed pin | source |
|---|---|---|
| meetings walked | 179 | :1343 |
| non-empty absent sets | 163/179 = 0.911 (mean \|absent\| ~3.09, median 3.0) | :1355 |
| **new at-or-over-the-gate candidate minted** | **53/179 = 0.296** | :1396 |
| top rendered-candidate churn (informational) | 114/179 = 0.637 | :1409 |

**The read:** off-path (no round) the absence lever mints a new over-gate candidate in **0.296 >
0.20 — the ratified ceiling FAILS**, exactly the reading the 17.7 gate declined graduation on
(§6 there). The close's theory is that live roll-call shrinks the absent set (answering roll-call
removes a player from "unaccounted for"), which should LOWER new-over-gate; the 16.15 elicitation
already shrank the SETS (median 4 → 3) but NOT the gate-relevant channel (0.244 → 0.296, context
read). The dedicated roll-call ROUND — every living non-speaker asked — is the stronger shrink
the close's calibration premise predicts. Whether it reaches ≤ 0.20 is bar (b), re-run on the
probe bytes. **[PENDING — §7 cell (b).]** The absence prior graduates iff BOTH (a) ≥ 0.60 AND
(b) ≤ 0.20 hold on the probe (the ratified §6 bar).

## 5. Evidence row 3 — the endpoint exemption promotion census (lever 1) [VERIFIED]

Source: `tests/meetings/test_contradictions.py::TestExemptionCensus` (the would-be-STRONG
census: `exempt_off == exempt_on_strong`, byte-stable) + `TestExemptionCensusFunnelReconciliation`.

| set | meetings | promoted flags | by role | by class | source |
|---|---|---|---|---|---|
| ml_corpus/9p2i | 541 | **16** | CREWMATE 13 / IMPOSTOR 3 | whereabouts 14 + alibi 2 (both crew) | test_contradictions.py:2589-2594 |
| samples/9p2i | 179 | **4** | CREWMATE 4 | whereabouts 4 | :2572-2574 |
| samples/4p1i, ml_corpus/4p1i | 39, 40 | 0, 0 | — | — | :2578-2585, :2605-2613 |
| **corpus + samples total** | — | **20** | **CREWMATE 17 / IMPOSTOR 3** | — | [INFERRED — 16+4, 13+4/3] |

**The honest price [VERIFIED / INFERRED]:** the exemption promotes **20 claims across corpus +
samples, 17 crew-authored / 3 impostor-authored — the honest price runs ~5.7 : 1 AGAINST crew**
(crew lie about whereabouts more, because impostors default to `"observations": []` and rarely
answer roll-call off-path). Reconciliation with the audit's 25-lie whereabouts cell
(`audits/audit-phase-18-planning.md` §3.3): the ml_corpus/9p2i funnel reads 25 whereabouts lies,
`{CREWMATE: 20, IMPOSTOR: 5}` (test_contradictions.py:2635), decomposing cleanly into
`{alibi_conflict: 11, alibi_vs_sighting: 14}` (:2653-2660). **The exemption promotes ONLY the 14
`alibi_vs_sighting` claims** (the "whereabouts"-class rows of the exemption census); **the 11
`alibi_conflict`-only lies stay WEAK** — the exemption lives only in `_detect_alibi_vs_sightings`
and does not touch the self-pair/narrow/boundary/adversarial weak guards (:2661-2680). So of the
25 detected whereabouts lies, **14/25 convert to STRONG under lever 1 and 11/25 stay weak — say
so.** This is a real evidence-economy gain, but it lands mostly on crew.

## 6. Evidence row 4 — the vent variant census (lever 2) [VERIFIED]

Source: `tests/meetings/test_contradictions.py::TestVentPlacementCensus` (the grounded
`alibi_vs_physical` counterfactual, minted ON).

| set | vent flags minted | subjects (by role) | source |
|---|---|---|---|
| ml_corpus/9p2i | **5** | 5 DISTINCT impostor subjects (seeds 1031/p-5, 1053/p-1, 1071/p-9, 1081/p-6, 1119/p-6) | test_contradictions.py:2722-2725 |
| samples/9p2i | **2** | 1 impostor subject (seed 43 p-9, flagged twice) | :2712-2713 |
| 4p1i (both sets) | 0 | — | :2716-2718, :2728-2730 |
| **total** | **7 flags / 6 subjects** | **ALL impostor** | [INFERRED — 5+2, 5+1] |

**The read:** the vent variant mints **7 flags across 6 subjects, ALL impostor** — the cleanest
impostor-targeted lever in the package (grounded-only is the firewall; an ungrounded vent claim
mints nothing). Unlike the exemption (5.7 : 1 against crew), the vent variant's price is
impostor-side by construction: it prosecutes a subject placed by a grounded vent sighting in
contradiction with their own stated path, and the recorded impostors are the ones who vent.

**The registry + tooling leg landed in this PR (the pre-probe obligations):**

- The four lever flags — `roll_call_round`, `whereabouts_interior_flags`,
  `vent_placement_contradictions`, `impostor_roll_call` — are registered in
  `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` (each bound to its home-module resolver BY
  IDENTITY), BEFORE any probe seed records, so a probe/adoption recording's `game_over`
  `substrate_flags` stamp self-describes the arms under test. All DEFAULT-OFF: a bare-environment
  recording stamps all five toggles False, byte-identical (via the missing-key-reads-False rule
  the loader and validity gate share) to the committed baseline-5 sets — the committed 9p2i +
  4p1i sets re-verify byte-identical (reconstruction clean; the registry addition moves no
  existing bytes). Fixture-pinned in `tests/orchestrator/test_replay.py` (registration by
  identity, FULL/CREW-ONLY arm stamp round-trips) and `tests/experiments/test_probe_backends.py`
  (`_FLAGS_ON` grows with the snapshot).
- The 18.7 verifier's one soft spot is closed while in `replay.py`: a dedicated committed-set
  round-trip pin for the crew stamp (`tests/orchestrator/test_replay_policy_stamp.py::
  TestCrewStampCommittedSetRoundTrip`) — every committed 9p2i + 4p1i `game_over` carries no
  `crew_tactical_policy` key and reads back None = the scripted crew default.
- The offline audit tool `audits/workflows/extract_gameplay_facts.py` re-derives Phase-3 opt-in
  eligibility and would false-flag ON-path roll-call recordings (the round appends an
  `opt_in`-surface turn for every living non-speaker, exceeding `_opt_in_eligible_ids`). It is
  now relaxed under the RECORDED `roll_call_round` stamp: an ON-path recording expects the
  co-presence eligible ids followed by the sorted remaining living non-speakers; an OFF-path
  recording (the committed baseline-5 sets, which stamp the lever absent = OFF) keeps the exact
  strict gate. **Verified correct AND load-bearing** against 12 real roll-call transcripts: with
  the stamp ON the tool emits 0 OPTIN-eligibility findings; with the stamp stripped the strict
  gate flags 45 divergences across the 12 seeds (every roll-call meeting). The DESIGN.md §5.2
  companion note recording this turn-allocation surface is owner-side (the 18.12 adopting
  record), not edited here.

## 7. The live probe — what it measures, the two arms, the runbook [PENDING — operator leg]

The ruling turns on cells that CANNOT be read offline: the round changes the recorded
transcripts, so crew coverage under the round (a), the absence counterfactual re-run on the
round's bytes (b), and the impostor-answer arm's win + self-flag (c) exist only in a fresh
recording. Two probe sets, 25 seeds 9p2i each, real Featherless path ($0 flat-rate), the arms
stamp-proven via the substrate-flag snapshot in the recorded bytes:

- **FULL** = `AILIBI_ROLL_CALL_ROUND=1 AILIBI_WHEREABOUTS_INTERIOR_FLAGS=1
  AILIBI_VENT_PLACEMENT_CONTRADICTIONS=1 AILIBI_IMPOSTOR_ROLL_CALL=1` (plus
  `AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b`). The impostor-answer variant
  exists ONLY for `qwen3_6_27b` (any other prompt set fails loud); its recorded version strings
  are `impostor_report_roll_call.qwen3_6_27b.v1` / `accusation_round_roll_call.qwen3_6_27b.v1`.
- **CREW-ONLY** = the first two flags only (round + exemption; the vent variant travels with the
  package and is measured on the FULL arm; impostor templates stay default).

Every lever read happens at runner CONSTRUCTION, so the full arm environment is exported BEFORE
any worker process starts, never mid-run. Operator runbook (the standing 16.14/16.17 discipline;
`scripts/record_ml_corpus.sh`): 2 staggered Featherless seed workers, `AILIBI_SEED_MAX_ATTEMPTS=8`,
jittered backoff, per-seed atomic staging, working artifacts OUTSIDE the tree (only the
measurements are committed — no probe record lands in `replays/`). Duration honesty: the
baseline-5 samples re-record ran ~11.8 min/worker per 9p2i meeting-bearing seed
(`audits/audit-phase-16-close.md`:31-32, 50 seeds / 2 workers / 4 h 54 m); the round adds ~+36 %
meeting calls and the FULL arm adds the impostor-answer turns on top, so **~8–9 h total across
both arms at 2 workers** (consistent with a single FULL-arm seed exceeding 7 min of wall in a
one-off timing check during this PR). Acceptance per set before any cell is read:
`uv run python scripts/validity_gate.py <probe-dir> --expected-model Qwen/Qwen3.6-27B
--require-zero-cost` PASS, then byte-verify.

**The measurement recipe (pure, offline, over the probe dir):**

| cell | how | bar |
|---|---|---|
| (a) crew coverage | `eval.funnel.compute_pooling_funnel(<probe-dir>).roll_call_coverage_crew_mean` | ≥ 0.60 |
| (b) new-over-gate | the `TestAbsencePriorOnCommittedBytes` walk re-pointed at `<probe-dir>` → new_over_gate_meetings / meetings | ≤ 0.20 |
| (c) impostor win | `sum(read_game_outcome(seed)=="IMPOSTORS")/25` on the FULL probe | ≥ 0.20 (FSM 0.36) |
| (c) STRONG self-flag rate | answered impostor roll-calls (impostor `WhereaboutsClaim` turns) that carry a STRONG `alibi_vs_sighting`/`alibi_vs_physical` flag naming the answerer / total answered impostor roll-calls | ≤ 0.25 |
| (d) vent live yield | count of `alibi_vs_physical` flags in the FULL probe contradictions, by subject role | measured (informational vs the offline 7/6-impostor census) |

| cell | pre-registered bar | probe (FULL) | probe (CREW-ONLY) | two-proportion z | verdict |
|---|---|---|---|---|---|
| (a) crew coverage | ≥ 0.60 | **[PENDING]** | **[PENDING]** | vs 0.60 null on the crew-meeting denominator | **[PENDING]** |
| (b) new-over-gate | ≤ 0.20 | **[PENDING]** | **[PENDING]** | vs 0.20 null on the meeting denominator | **[PENDING]** |
| (c) impostor win | ≥ 0.20 | **[PENDING]** | n/a (default templates) | vs FSM 0.36 on n=25 | **[PENDING]** |
| (c) self-flag rate | ≤ 0.25 | **[PENDING]** | n/a | vs 0.25 null on answered-roll-call denominator | **[PENDING]** |
| (d) vent live yield | measured | **[PENDING]** | **[PENDING]** | — | **[PENDING]** |

## 8. Pricing both directions honestly [VERIFIED / INFERRED]

Per the 15.18 discipline, each ruling direction is priced with its NO path, on the offline
evidence in hand:

- **What FULL buys:** the richest deception economy — the round makes crew coverage reachable
  (bar (a)), the exemption converts 14/25 whereabouts lies to STRONG (§5), the vent variant adds
  7 impostor-targeted physical flags (§6), AND the impostor-answer arm manufactures NEW catchable
  impostor lie material (impostors must account for themselves instead of refusing). **What FULL
  risks:** the impostor-answer arm re-opens the ≥ 44 % self-flag class the prompt ladder closed
  (`impostor_report.j2`:8-12); bar (c) is the guard (win ≥ 0.20 AND self-flag ≤ 0.25), and it is
  a LIVE-only read — the arm was built inert precisely so the probe measures what the ladder only
  feared.
- **What CREW-ONLY buys:** the crew-side evidence economy (round + exemption + vent) without the
  self-flag risk — the round + exemption graduate the crew clause and the absence prior if (a)/(b)
  pass, and the vent variant travels with the package. **What CREW-ONLY forfeits:** NO new
  impostor lie material — impostors keep refusing (`"observations": []`), so the densest
  deception signal the phase was chartered to grow (catchable impostor lies) does not ship. The
  exemption's 5.7 : 1 crew skew (§5) is unmitigated by any impostor-side answer channel.
- **What NONE buys:** no meeting-layer change — the corpus records at the baseline-5 layer, all
  Phase-18 selection evidence stays on the current substrate, and the ~18–20 h re-record is
  avoided. **What NONE forfeits:** the crew clause stays failed (0.4624 < 0.60), the absence
  prior stays OFF with the ratified bar unmet, and roll-call lies stay economically unpunishable
  (endpoint-banded to weak) — the exact gaps the phase's training signal needs.

## 9. The ruling slots — pre-authored, PENDING owner [PENDING]

The §1–§8 memo is assembled FIRST; the ruling is put to the owner in-session against the probe
cells (the 17.7 shape). Each slot follows the Task-14.6 locked-decision shape. **No slot is
filled until the probe lands AND the owner signs — this memo records the criteria, not a
guessed outcome.**

### Ruling A — the package: **[PENDING — FULL / CREW-ONLY / NONE]**

- **FULL** ships iff (a) ≥ 0.60 AND (b) ≤ 0.20 AND (c) win ≥ 0.20 AND self-flag ≤ 0.25. Surgery:
  no structural change (all four arms graduate at 18.12; `tasks/phase-18.md` Baseline-numbering
  block — "a FULL or CREW-ONLY ruling changes no structure").
- **CREW-ONLY** ships iff (a) ≥ 0.60 AND (b) ≤ 0.20 but (c) fails (win < 0.20 OR self-flag >
  0.25). Surgery: no structural change; the impostor-answer arm stays inert (unshipped arms stay
  default-OFF), the round + exemption + vent graduate at 18.12.
- **NONE** if (a) < 0.60 OR (b) > 0.20 (the crew clause / absence bar unreachable even with the
  round). Surgery (§10): remove 18.12/18.13/18.14, rewire 18.15/18.16 deps to the baseline-5
  corpus, renumber the 18.28 mover baseline 7 → 6; the absence prior stays OFF with the ratified
  bar restated unmet.

### Ruling B — the absence-prior graduation: **[PENDING — GRADUATE / STAY-OFF]**

Rides Ruling A: GRADUATE iff (a) ≥ 0.60 AND (b) ≤ 0.20 on the probe (the ratified
`audits/audit-phase-17-absence-gate.md` §6 bar, re-read on the round's bytes); else STAY-OFF with
the probe cells named. Under NONE the absence prior stays OFF by construction (no adopting record
to carry it).

### Ruling C — the vent widening + its flag-minting variant: **[PENDING — SHIP / HOLD]**

The 17.7 Ruling-2 HOLD travels here. Re-ruled WITH the package: under FULL or CREW-ONLY the vent
variant SHIPS with the meeting-layer record (it is meeting-layer and now has an adopting record
to travel with, unlike the 17.7 STAY-OFF branch); under NONE it HOLDs again. Its live yield (§7
cell (d)) is measured on the FULL probe, so the ruling reads a measured flag count, not the
offline 7/6-impostor extrapolation.

## 10. The surgery record [PENDING — executes only in the ruled direction]

Per `tasks/phase-18.md` Baseline-numbering block, executed only AFTER Ruling A is recorded:

- **FULL / CREW-ONLY:** changes no structure (the arms that ship are 18.12's business;
  18.12–18.14 proceed either way). This memo's ruling banner is added to `tasks/phase-18.md`;
  prompts regenerate; validator green.
- **NONE:** removes 18.12, 18.13, 18.14 (contracts + prompts, with a drop record naming this
  audit), rewires 18.15's `Depends on:` to `18.11`, rewires 18.16's `Depends on:` to `18.15`
  alone (the removed 18.14's constant-flip is moot under NONE — the bar stays baseline-5; the
  Wave-2 DAG edge becomes `18.15 -> 18.16`), binds 18.15 to the standing baseline-5 corpus,
  leaves `BAKEOFF_BASELINE_ID = "baseline-5"` untouched, and renumbers the 18.28 mover record
  baseline 7 → 6. The absence prior stays OFF with the ratified bar unmet, restated here.

**Until the ruling is recorded, NO surgery is performed and the phase DAG is unchanged** — the
gate is dispatchable-consistent with the surviving DAG exactly as it stands (18.12–18.14 remain,
awaiting the ruling), and `scripts/compute_next_task.py --phase 18` is green on the current
graph.

## 11. Status

- **Offline evidence:** COMPLETE (§3–§6, all cells committed and test-pinned).
- **Registry + tooling leg:** COMPLETE and verified (§6 — the four flags registered, byte-identity
  preserved, the crew-stamp committed-set pin closed, `extract_gameplay_facts` relaxed and
  verified correct + load-bearing).
- **Live probe (operator, ~8–9 h):** **PENDING** — the two 25-seed real-path recordings (§7).
- **Owner ruling (FULL / CREW-ONLY / NONE + absence graduation + vent re-rule):** **PENDING** —
  the ruling slots (§9) are pre-authored; the owner rules on the assembled probe cells.
- **Surgery:** **PENDING** — executes only in the ruled direction (§10); the DAG is unchanged
  until then.

Per the Task-18.11 integration-risk note (the 17.14 PENDING pattern): the PR stays open with
this memo complete and the DoD honest. **No ruling that has not happened is recorded here.**
