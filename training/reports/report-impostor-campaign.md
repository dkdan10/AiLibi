# The impostor campaign — the phase's first live co-evolution campaign (Task 18.24, operator, multi-session)

**Task:** 18.24 — THE IMPOSTOR CAMPAIGN (operator, multi-session).
**Machinery consumed (frozen, never edited here):** the 18.21 alternating-freeze driver +
stabilizers (`training/coevo/driver.py`, merged `316d4e5`), the 18.20 hall of fame +
PFSP-lite sampler, the 18.16 conviction fitness stack (`ConvictionFitnessTerm`, weight 0.5,
artifact `4841f8e02eb7…`), the 18.17 real-path re-rank library (`training/realpath.py`),
the 18.5 anchor-study candidates, the 18.6 MAP-Elites persisted cells, the 18.1/18.2/18.3
emergence instruments.
**Section refs:** audits/audit-phase-18-planning.md §7 (the campaign shape);
audits/audit-phase-17-close.md §1.3 (the flip bar the campaign aims at);
audits/audit-phase-18-emergence-preregistration.md (the 18.4 ratified bars);
report-goodhart-probe.md "Blockers" (the four named blockers, folded verbatim in §1.2).
**Date started:** 2026-07-23 (session 1).
**Status:** IN PROGRESS — multi-session. §2 is the session ledger; every row, leg, and
sweep below states which session produced it.

---

## 1. Protocol (fixed before any run)

### 1.1 The conviction protocol decision (the 18.30 hand-off)

The contract's decision point: *non-composed + `conviction=` under blocker (2)'s guard,
composed, or neither.* **Decided: non-composed + `conviction=`.** Every campaign run
constructs the GO-gated term via `load_conviction_fitness_term(training/artifacts/conviction)`
(verdict GO, `fitness_term="ships"`, weight 0.5, sha `4841f8e02eb7…`) and passes it as
`CoevoCampaignConfig(conviction=…)` — served LIVE into BOTH sides' training fitness (the
merged driver has no metering-only mode; the addend is
`0.5 × trace.mean_predicted_supply()` in both `inner_episode_fitness` and
`crew_inner_episode_fitness`). Rationale:

- The 9p2i roster is the one roster where the 18.18 re-probe HELD the term: no forced
  lever lifts predicted supply above the 25% materiality bar (max `emergency` +4.9%), and
  the term pulls AGAINST the strongest geomean corners (report-goodhart-probe.md, 9p2i
  table). The laundering shapes live on the 4p1i roster, which this campaign never runs.
- Composed is deliberately NOT the opening configuration: the contract starts the campaign
  without 18.29 and allows a LATER swap to adopt it (GO verdict landed, `6339116`), only
  through the runner-factory seam, only after a miniature composed smoke campaign, with the
  three `adoption_constraints` from `training/artifacts/composed/verdict.json` carried
  verbatim into the meters. No session has adopted it yet (§2).
- "Neither" would reproduce the exact training-signal gap this phase exists to close
  (conviction pressure invisible at training time — planning audit §2).

**Blocker (2)'s guard, operationalized** (there is deliberately NO code for this — the
conditioning is protocol, discharged in this report):

1. **Roster guard:** every run is 9p2i (`tasks_per_crewmate=2`) — blockers (1) and (2)'s
   4p1i prohibitions are satisfied structurally; no 4p1i-scored anything appears anywhere
   in this campaign.
2. **Meeting-count meter:** per generation the report quotes the predicted-meetings-per-
   training-game proxy (Δ`conviction_uses` / games) beside the scripted-FSM anchor
   (~3.6 meetings/game on 9p2i, the 18.18 probe's census). An entrant whose meter exceeds
   the FSM anchor by ≥ 25% (the probe's materiality convention) without recorded-bytes
   flag confirmation on its REAL-path recordings has its conviction credit flagged
   SUSPECT in §4's selection reading, and selection falls back to conviction-free ordering
   for that entrant.
3. **Selection pairing (blocker 4's shape):** no selection step (top-K choice for a real
   leg, finalist naming) leans on conviction-influenced ordering without a recorded-bytes
   floor read. The pre-screen verdict before every real spend is quoted as SPEND ADVICE
   ONLY beside the recorded referee read of the real bytes (`RealPathRerankRow.watchability`).
   On the fake substrate the recorded read is 0 flags by construction (flag-mintless) —
   quoted as such, never treated as a pass or a fail of the entrant.

### 1.2 The four named blockers (folded verbatim, report-goodhart-probe.md "Blockers")

1. `d4-contest-farming[4p1i]` — no 4p1i-scored selection until the routed D4 contest floor
   lands. **Discharge: no 4p1i anywhere in this campaign.**
2. `conviction-supply-laundering[emergency,4p1i]` — no conviction-weighted fitness on the
   4p1i roster; on ANY roster the term's credit for meeting-count-multiplying play is
   conditioned/capped on recorded-bytes confirmation before selection leans on it.
   **Discharge: §1.1 guard items 1–3; meters in §3, selection reads in §4.**
3. `conviction-supply-laundering[kill,4p1i]` — same guard; named separately (honest
   witnessed-kill pins predicted, never substrate-delivered). **Discharge: same as (2).**
4. `prescreen-substrate-divergence[9p2i]` — a pre-screen PASS is real-path spend advice
   ONLY; every gating use pairs with a recorded-bytes floor read on flag-mintless
   substrates. **Discharge: §1.1 guard item 3; every §4 leg quotes the pre-screen verdict
   beside the fake-substrate recorded flags (always 0) and the real-bytes referee read.**

### 1.3 Entrants + seed provenance (the stale-seed fence, verified before any run)

Two seed families exist and are MUTUALLY EXCLUSIVE per side (different genome length and
encoder; a hall is single-family by the driver's reload length-check). Two substrate-sha
definitions dispatch per family (the two-definition rule): utility-family study artifacts
carry `training.anchor_study.compute_substrate_sha` (composite); free-policy artifacts and
the MAP-Elites founder cells carry `training.bakeoff.map_elites.bakeoff_substrate_sha`
(raw MANIFEST digest). Verified at this tree before any run (session 1):

| definition | current value | consumed by |
|---|---|---|
| `compute_substrate_sha` (composite) | `9bc00af0f9e76719cb78d66c5593ec178312716528715f4a580677fb519f04f4` | runs 01–03 (`substrate_sha_kind="compute_substrate_sha"`) |
| `bakeoff_substrate_sha` (MANIFEST) | `e4547789167039aea0cecb7c48522eed6e09e0d7b8d27a970ccbc76b251dedf2` | runs 04–05 (`substrate_sha_kind="bakeoff_substrate_sha"`) |

Stale-seed fence readings: `lambda-4.0` and `filtered-bc-anchor` `config.json`
`substrate_sha` both equal the current composite (`9bc00af0…`) — **no re-fit needed**;
the MAP-Elites `cells/index.json` `substrate.substrate_sha256` equals the current MANIFEST
digest (`e4547789…`) — **founder ingest fence clean**. The driver re-verifies the founder
fence read-only before any mkdir (its own preflight); the anchor-study fence is caller
discipline (the driver does not fence `initial_genome`) and was executed by the session
harness (`preflight()` in §9).

The entrant lineages (each a sequential fresh driver run; the multi-session no-resume
shape — an existing hall root or rows file is a no-clobber error, so later sessions
continue a lineage as a FRESH run seeded via `initial_genome=` from the prior frozen
champion, the pool restarting from substrate-fenced founders where the family permits):

| run | family / encoder | genome | impostor seed (sha-verified reload) | anchor | founders | master_seed |
|---|---|---|---|---|---|---|
| run-01-utility-champion | utility / `impostor-option-features-v1` | 19 | committed champion `training/artifacts/impostor/utility-es` (`6d327dcb…`) | scripted-FSM default, λ=1.0 | none (no utility founder pool exists — §7 F2) | 182401 |
| run-02-utility-lambda4 | utility / `impostor-option-features-v1` | 19 | `training/artifacts/anchor_study/lambda-4.0` (`3cc4058b…`) | scripted-FSM default, **λ=4.0** (the lineage keeps its legibility pressure) | none | 182402 |
| run-03-utility-bcanchor | utility / `impostor-option-features-v1` | 19 | committed champion (`6d327dcb…`) | **`anchor_policy` = filtered-bc-anchor** (`23632a85…`, the 18.16 anchor-policy seam; λ=1.0) | none | 182403 |
| run-04-freepolicy-v3 | free-policy / `v3` (18.22, hidden 8) | 1442 | random init from master seed (**no committed v3 genome exists**) | scripted-FSM default, λ=1.0 | none (committed founders are v2/1049 — the v3 side cannot reload them; §7 F2) | 182404 |
| run-05-freepolicy-v2-founders | free-policy / `v2` (hidden 8) | 1049 | `training/artifacts/impostor/policy-es` champion | scripted-FSM default, λ=1.0 | **30 MAP-Elites cells ingested** (`training/artifacts/impostor/map-elites`) | 182405 |

Crew side, all runs: the committed owned-task crew champion
(`training/artifacts/crew/crew-owned-tasks-es`, 27 genes, `crew-option-features-v2`),
`initial_genome` sha-verified via `load_candidate_weights`. The crew hall starts empty in
every run: swap-0 impostor training is against the frozen SCRIPTED crew (the pool-empty
FSM sentinel), exactly the contract's "frozen scripted crew"; later swaps use the frozen
crew champions the alternation accumulates.

### 1.4 Sizing + meters

Runs 01–04: `num_swaps=4`, `generations_per_swap=3` (12 generations; impostor moves swaps
0/2, crew swaps 1/3), population 6, slate 3, `fitness_seeds=(1000,1001,1002,1005,1006,1007)`
(the committed utility-es fitness set), `benchmark_seeds=(2000..2003)`,
`payoff_seeds=(3000..3003)`, exploiter 5×6 (default; cannot be disabled), staleness cap 8,
`game_ceiling=25 000`, `allow_over_ceiling=False`. Projected game bound 3 816/run
(runs 01–04; run 05: 1 176) — under the ceiling with the exploiter term
(31 × |benchmark_seeds| = 124/generation) dominating, as the contract prices.

Run 05 is deliberately smaller (`num_swaps=2`, `generations_per_swap=2`,
`payoff_seeds=(3000,3001)`, `benchmark_seeds=(2000,2001,2002)`): measured fake-path cost
against MAP-Elites founder opponents is ~10–15 s/game (low-kill founder corners stall
games toward the 1000-tick cap), so the exact-pool-cover payoff row over the 30-founder
pool dominates wall-clock; the reduced budget keeps the founder-exercising lineage
affordable in session 1. This cost fact is a campaign finding (§7 F3).

Conviction metering: one fresh `ConvictionUseCounter` per run (the committed cap 52 481,
sha-keyed; a fresh run's counter restarts at 0 — there is no cross-run consumption
ledger), quoted per row (`conviction_uses`, cumulative) and per run in §3. Pre-screen
reads use their own fresh counters, quoted per leg in §4. No counter approached its cap
in session 1 (§3).

---

## 2. Session ledger (the multi-session index)

| session | date | work | status |
|---|---|---|---|
| 1 | 2026-07-23 | Protocol fixed (§1); five fake-path lineage runs recorded, 10 378 games, all COMPLETE (§3); the conviction-term ablation twin run (§6.1); leg 04 tranche 1 recorded + ranked + swept (§4.1/§5.1, under the F7 impaired-status window); leg 01 tranche 1 launched | this session |

| 2 | 2026-07-24 | Overnight detached chain: leg 03 t1 + leg 05 t1 + leg 04 t2 + leg 01 t2 recorded, ranked, swept (§4.4–4.6, §5.4–5.5); leg 02 t2 in flight; F8 recorded | this session |

Real-path legs remaining after the session-2 morning pass: leg 02 t2 (in flight),
leg 03 t2, leg 05 t2 — 18 real games. Then: finalist naming (§8), contingent
meeting-layer ablation recordings, final gates.

Real-path legs completed / pending, ablations run, and the finalist reading are tracked in
§4/§6/§8 as they land; the close (18.28) waits on 18.23 + 18.29 regardless.

---

## 3. The campaign rows (fake/surrogate path; per run)

Committed rows: `training/reports/results-impostor-campaign.jsonl` — the five runs'
`campaign-rows.jsonl` streams concatenated in run order (schema `coevo-campaign-v1`, one
row per generation; run boundaries recoverable from `generation_index` restarting at 1).
Frozen artifacts: `training/artifacts/coevo/<run-name>/{impostor,crew}/…` (weights +
sha sidecars + index, written by the driver). Everything below is read from those bytes.

**The conviction meeting-count meter (§1.1 guard item 2), read once for all runs:** the
row's `conviction_uses` delta per generation divided by TRAINING games (games_gen minus
the 128 benchmark+exploiter games that never serve the term: 4 + (1+5×6)×4; run 05:
3 + 31×3 = 96) is the predicted-meetings-per-training-game meter. Across every
generation of every run it reads 0.5–3.8 (utility runs 2.0–3.8, max 3.76 at run-03
gen 2–3; free-policy v3 0.5–1.4; v2+founders 1.2–3.5) against the scripted-FSM census of
~3.63 meetings/game (29/8 seeds, the 18.18 probe). **No entrant multiplied meeting
count** — the max excursion is +3.7%, two orders under the 25% materiality bar.
Blocker (2)'s meeting-count condition is clean for every session-1 lineage; no
conviction credit is flagged SUSPECT.

### 3.1 run-01-utility-champion (session 1 — COMPLETE, 2 358 games, 12 rows)

| gen | swap | moving | pool | champion_fitness | updated | anchor_champ | anchor_fsm | exploiter | conv_uses | games_cum |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | impostor | 0 | 20.5544 | no | 19.8713 | 11.7684 | not-found | 151 | 170 |
| 2 | 0 | impostor | 0 | 20.5544 | no | 19.8713 | 11.7684 | not-found | 299 | 340 |
| 3 | 0 | impostor | 0 | 20.5544 | no | 19.8713 | 11.7684 | not-found | 454 | 510 |
| 4 | 1 | crew | 1 | 12.2743 | yes | 4.8024 | 9.0000 | **frozen** 20.75>9.00 | 586 | 684 |
| 5 | 1 | crew | 2 | 10.7298 | no | 4.8024 | 9.0000 | **frozen** 20.75>9.00 | 744 | 862 |
| 6 | 1 | crew | 3 | 10.7298 | no | 4.8024 | 9.0000 | **frozen** 20.50>9.00 | 1046 | 1086 |
| 7 | 2 | impostor | 1 | 19.7439 | yes | 17.4345 | 12.1674 | not-found | 1200 | 1260 |
| 8 | 2 | impostor | 1 | 19.7439 | no | 17.4345 | 12.1674 | not-found | 1355 | 1434 |
| 9 | 2 | impostor | 1 | 19.7439 | no | 17.4345 | 12.1674 | **frozen** 12.24>12.17 | 1511 | 1608 |
| 10 | 3 | crew | 5 | 10.9868 | yes | 4.8385 | 9.0000 | **frozen** 20.00>9.00 | 1862 | 1840 |
| 11 | 3 | crew | 6 | 11.5338 | no | 4.8385 | 9.0000 | **frozen** 19.50>9.00 | 2217 | 2076 |
| 12 | 3 | crew | 7 | 11.6537 | yes | 10.5242 | 16.7500 | **frozen** 21.00>16.75 | 2717 | 2358 |

Meters: conviction 2 717 / 52 481 (5.18%); games 2 358 / bound 3 816. Frozen champions:
swap 0 = `6d327dcb…` (**the committed champion itself** — three generations of ES at
σ=0.15 never displaced it against the scripted crew), swap 1 crew `22c9707e…`, swap 2 =
`8ac3652a…` (**displaced only under co-adapted crew opposition**), swap 3 crew
`31ca14b5…`. Exploiter finds froze 6 members (5 impostor-family exploits of the crew
champion at 19.5–21.0 vs bars 9.0–16.75; 1 crew-family exploit at 12.24 vs 12.17).

**Cycling verdict (vs the pre-registered signature — flat anchor + oscillating
co-matchup = Red-Queen; monotone anchor = progress):** the impostor side is NOT flat: the
champion-side anchor STEPS DOWN 19.87 → 17.43 exactly at the swap-2 displacement while
the co-matchup payoff rises 14.97 → 16.82 — relative gain against the trained pool with
absolute regression against the FSM anchor. One displacement event (n=6 generations) is
thin evidence, but the shape is the Red-Queen-adjacent trade the detector exists to
surface, stated as such. The crew side reads as real progress (champion-side anchor
+5.72 across the run, ending 10.52).

### 3.2 run-02-utility-lambda4 (session 1 — COMPLETE, 2 424 games, 12 rows)

| gen | swap | moving | pool | champion_fitness | updated | anchor_champ | anchor_fsm | exploiter | conv_uses | games_cum |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | impostor | 0 | 18.6030 | yes | 17.2826 | 9.7540 | **frozen** 12.06>9.75 | 145 | 170 |
| 2 | 0 | impostor | 1 | 18.8471 | yes | 17.5724 | 9.8409 | **frozen** 10.96>9.84 | 306 | 344 |
| 3 | 0 | impostor | 2 | 18.8707 | yes | 17.3171 | 9.7540 | **frozen** 12.07>9.75 | 478 | 522 |
| 4 | 1 | crew | 1 | 11.0843 | yes | 4.4180 | 9.7500 | duplicate | 634 | 696 |
| 5 | 1 | crew | 1 | 11.1302 | yes | 8.9842 | 17.0000 | duplicate | 727 | 870 |
| 6 | 1 | crew | 1 | 11.1302 | no | 8.9842 | 17.0000 | **frozen** 19.50>17.00 | 856 | 1044 |
| 7 | 2 | impostor | 4 | 18.4258 | no | 17.3171 | 9.7540 | **frozen** 12.07>9.75 | 1173 | 1272 |
| 8 | 2 | impostor | 5 | 18.6483 | no | 17.3171 | 9.7540 | **frozen** 12.07>9.75 | 1643 | 1546 |
| 9 | 2 | impostor | 6 | 18.2686 | yes | 17.3352 | 9.7540 | **frozen** 10.59>9.75 | 1831 | 1740 |
| 10 | 3 | crew | 3 | 11.1733 | yes | 8.9927 | 17.2500 | **frozen** 19.25>17.25 | 2122 | 1964 |
| 11 | 3 | crew | 4 | 11.1733 | no | 8.9927 | 17.2500 | **frozen** 19.25>17.25 | 2302 | 2150 |
| 12 | 3 | crew | 5 | 10.9988 | no | 8.9927 | 17.2500 | **frozen** 19.25>17.25 | 2749 | 2424 |

Meters: conviction 2 749 / 52 481 (5.24%); games 2 424 / 3 816. Frozen champions: swap 0
`10c1f9f3…` (the lambda-4.0 seed WAS displaced in generation 1 — the λ=4 objective moved
off the 18.5 fit immediately), swap 2 `2ca47451…`; crew `1baf6fef…` / `53d75516…`.
Exploiter froze 9 members across the run — the densest exploit stream of the session
(both directions).

**Cycling verdict:** neither signature half fires — the impostor champion-side anchor is
flat (net +0.05, max step 0.29) AND the co-matchup payoff is flat (net +0.06, one 0.65
wobble): a plateau, not Red-Queen motion. The λ=4 lineage holds a stable anchor-heavy
optimum under opponent pressure. Crew side: step to 8.98/17.25 then flat — one early gain,
then stable.

### 3.3 run-03-utility-bcanchor (session 1 — COMPLETE, 2 424 games, 12 rows)

| gen | swap | moving | pool | champion_fitness | updated | anchor_champ | anchor_fsm | exploiter | conv_uses | games_cum |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | impostor | 0 | 20.6328 | no | 19.9643 | 11.7684 | not-found | 151 | 170 |
| 2 | 0 | impostor | 0 | 20.6328 | no | 19.9643 | 11.7684 | not-found | 309 | 340 |
| 3 | 0 | impostor | 0 | 20.6328 | no | 19.9643 | 11.7684 | **frozen** 12.74>11.77 | 467 | 510 |
| 4 | 1 | crew | 1 | 12.2471 | no | 9.6720 | 17.2500 | **frozen** 20.00>17.25 | 598 | 684 |
| 5 | 1 | crew | 2 | 12.6441 | yes | 10.4218 | 17.2500 | **frozen** 21.00>17.25 | 904 | 904 |
| 6 | 1 | crew | 3 | 12.0804 | yes | 9.6288 | 17.2500 | **frozen** 20.75>17.25 | 1195 | 1128 |
| 7 | 2 | impostor | 2 | 19.8688 | yes | 18.9394 | 11.3041 | **frozen** 11.38>11.30 | 1361 | 1306 |
| 8 | 2 | impostor | 3 | 19.8688 | no | 18.9394 | 11.3041 | **frozen** 11.93>11.30 | 1539 | 1488 |
| 9 | 2 | impostor | 4 | 19.2990 | yes | 19.5455 | 10.5830 | not-found | 1722 | 1674 |
| 10 | 3 | crew | 5 | 11.5813 | yes | 9.6570 | 17.2500 | **frozen** 19.75>17.25 | 2151 | 1948 |
| 11 | 3 | crew | 6 | 10.8755 | yes | 9.6657 | 17.2500 | **frozen** 20.25>17.25 | 2605 | 2226 |
| 12 | 3 | crew | 7 | 12.9476 | no | 9.6657 | 17.2500 | **frozen** 20.00>17.25 | 2821 | 2424 |

Meters: conviction 2 821 / 52 481 (5.38%); games 2 424 / 3 816. Frozen champions: swap 0
= `6d327dcb…` (the committed champion again — the filtered-BC anchor re-keys the CE term
but did not displace the champion against scripted crew; run-01 and run-03 independently
converged on holding it), swap 2 `a89be618…` (displaced under co-adapted crew, with the
champion-side anchor RISING 18.94 → 19.55 at the gen-9 update — the only impostor
lineage whose displacement improved the absolute anchor).

**Cycling verdict:** small-amplitude oscillation on both channels (impostor anchor net
−0.42 with a 1.02 max step; co-matchup net +0.11 with a 1.51 wobble) — neither monotone
progress nor the flat-anchor cycling shape; inconclusive at this budget, stated as such.

### 3.4 run-04-freepolicy-v3 (session 1 — COMPLETE, 2 308 games, 12 rows)

| gen | swap | moving | pool | champion_fitness | updated | anchor_champ | anchor_fsm | exploiter | conv_uses | games_cum |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | impostor | 0 | 1.2668 | yes | −0.8229 | 17.5387 | **frozen** 17.61>17.54 | 21 | 170 |
| 2 | 0 | impostor | 1 | 1.2385 | yes | −1.7240 | 17.4798 | **frozen** 17.59>17.48 | 66 | 344 |
| 3 | 0 | impostor | 2 | 1.5790 | yes | −1.3041 | 17.5649 | **frozen** 17.63>17.56 | 107 | 522 |
| 4 | 1 | crew | 1 | 19.7571 | yes | 10.3835 | 17.5000 | not-found | 182 | 696 |
| 5 | 1 | crew | 1 | 19.8381 | yes | 10.4785 | 18.0000 | not-found | 251 | 870 |
| 6 | 1 | crew | 1 | 19.8661 | yes | 10.5156 | 16.7500 | not-found | 303 | 1044 |
| 7 | 2 | impostor | 4 | 1.4491 | no | −1.3041 | 17.5649 | duplicate | 367 | 1272 |
| 8 | 2 | impostor | 4 | 2.6684 | yes | −1.2241 | 17.4687 | **frozen** 17.49>17.47 | 475 | 1500 |
| 9 | 2 | impostor | 5 | 3.0633 | no | −1.2241 | 17.4687 | **frozen** 17.51>17.47 | 676 | 1774 |
| 10 | 3 | crew | 2 | 19.5292 | yes | 10.4909 | 17.5000 | not-found | 736 | 1952 |
| 11 | 3 | crew | 2 | 19.5517 | yes | 10.5242 | 17.5000 | not-found | 815 | 2130 |
| 12 | 3 | crew | 2 | 19.5517 | no | 10.5242 | 17.5000 | not-found | 886 | 2308 |

Meters: conviction 886 / 52 481 (1.69%); games 2 308 / 3 816. Frozen champions: swap 0
`348df066…`, swap 2 `27f852fe…` (both trained against slates containing the gen-1 crew
exploiter `76a0e8c5…`); crew `43e5b869…` / `9dc8432f…`. The from-scratch v3 lineage
moved EVERY impostor generation it could (7 of 9 updates across the run).

**Cycling verdict: the pre-registered signature is PRESENT on the impostor side** — the
co-matchup payoff rises strongly (0.04 → 3.20, +3.16) while the champion-side absolute
anchor stays flat-to-down (−0.82 → −1.22): motion against the co-adapting pool without
absolute progress against the FSM anchor. This is the clearest Red-Queen reading of the
session (and the expected one for a from-scratch policy adapting to its opponent
distribution). The crew side reads as mild real progress (+0.14 anchor, payoffs up).

### 3.5 run-05-freepolicy-v2-founders (session 1 — COMPLETE, 848 games, 4 rows)

| gen | swap | moving | pool | champion_fitness | updated | anchor_champ | anchor_fsm | exploiter | conv_uses | games_cum |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | impostor | 0 | 20.4604 | no | 19.4909 | 12.8047 | **frozen** 12.82>12.80 | 148 | 138 |
| 2 | 0 | impostor | 1 | 19.6405 | yes | 19.0540 | 12.7796 | **frozen** 12.79>12.78 | 251 | 278 |
| 3 | 1 | crew | **31** | 11.8602 | yes | 3.6765 | 5.0000 | **frozen** 20.67>5.00 | 629 | 562 |
| 4 | 1 | crew | **32** | 16.4891 | yes | 11.2015 | 17.0000 | **frozen** 21.33>17.00 | 862 | 848 |

Meters: conviction 862 / 52 481 (1.64%); games 848 / bound 1 176. Frozen champions:
swap 0 `43b113ec…` (the policy-es seed held one generation, displaced at gen 2 against a
slate containing the gen-1 crew exploiter), swap 1 crew `3921f86a…`. **The founder
clause is exercised**: both crew generations trained against the 31–32-member impostor
pool (30 MAP-Elites founders + the swap-0 champion + an exploiter), and the crew champion
improved sharply against it (co-matchup payoff 5.72 → 13.00, champion-side anchor
3.68 → 11.20). No retirements (2 servable generations vs cap 8).

**Cycling verdict:** the budget (2 impostor generations) is below any signature read;
recorded for provenance, verdict N/A at this depth. The lineage's value in session 1 is
structural: the only family whose sequential-session restarts can reload committed
founders (F2), exercised end-to-end here.

### 3.6 Cross-run readings

- **The committed champion is locally optimal against scripted crew** — two independent
  lineages (01, 03) held `6d327dcb…` through three ES generations each; displacement
  happened ONLY once co-adapted crew entered the opponent pool. Opponent pressure, not
  more scripted-crew ES, is what moves the utility champion — the phase's premise,
  observed directly.
- **Exploiter probe earns its cost:** 20 frozen exploits across four runs, in both
  directions; every crew champion of the session is exploitable by an impostor-family
  exploiter at +2 to +11 over the FSM bar, and those exploits then serve as opponents.
- **No retirement events fired** (staleness cap 8 vs ≤6 servable generations per pool
  member at this budget) — the retire-and-replace sanity read stays pending a
  longer-horizon session.

---

## 4. Real-path re-rank legs (18.17 machinery; 17.14 table discipline)

Standing shape per leg: pre-screen (spend advice ONLY, blocker 4) → `run_realpath_rerank`
(design B / `MODE_TOP_K`, 9p2i, baseline-6, seeds `4000–4005` run in tranches of 3 —
the library's ranking write is all-or-nothing per invocation, so tranches keep a session
boundary from losing hours of recordings; per-seed retry budget 8,
`meeting_timeout_seconds=900` — the library default 300 s was measured too tight for a
real 9-player meeting at this plan's throughput, see F7) under the canonical Featherless
real path
(`AILIBI_LLM_PROVIDER=featherless`, `AILIBI_PROMPT_SET=qwen3_6_27b`, model
`Qwen/Qwen3.6-27B`) — legs run ONE at a time (finding F7: two concurrent legs starve the
library's 300 s per-meeting wall-clock proxy on the 4-unit plan and burn the per-seed
retry budget on timeouts; the corpus runbook's 2-worker shape belongs to
`run_tournament`'s seed-range workers, not to concurrent `run_realpath_rerank`
processes). Stamp proofs are the library's own `_verify_stamps` (stamp read BACK from
bytes, uniform, sha == computed genome digest); floor sensitivity is quoted per entrant
from the recorded `watchability.supply_gauges` (signed distance beside PASS/FAIL, the
population-relative conversion floor, the rare-event z where applicable).

**A machinery-shape finding (§7 F1) binds this section:** the merged driver persists NO
per-generation champion genomes (only swap champions and exploiter finds reach the hall),
so the contract's "per-generation top-K re-ranks" is not mechanically servable — legs
re-rank per IMPOSTOR SWAP over frozen hall members (K=2: the swap champions, newest
first, exploiter finds as alternates), the same 18.17 machinery and the same
~12-games-per-leg arithmetic.

### 4.1 Leg 04 — run-04-freepolicy-v3, tranche 1 (seeds 4000–4002; session 1, COMPLETE)

Recorded solo under `meeting_timeout_seconds=900`, during the F7 impaired-status window
(wall-clock not representative). Candidates: the run's two frozen swap champions.

**Pre-screen (spend advice ONLY — blocker 4), quoted beside the recorded reads:**

| candidate | predicted flags/meeting | predicted floors | fake recorded flags | REAL recorded flags/meeting |
|---|---|---|---|---|
| `27f852fe…` (gen 9) | 4.1642 | PASS | 0 (flag-mintless) | **6.6667** |
| `348df066…` (gen 3) | 5.2389 | PASS | 0 (flag-mintless) | **5.5000** |

The prescreen's supply prediction was directionally confirmed by the real bytes — and
the pairing discipline held: no gating read ever stood on the prediction alone.

**Ranking (17.14 discipline — stamp proofs + signed floor distances):**

| rank | candidate | selection | validity | referee | stamp proof |
|---|---|---|---|---|---|
| 1 | `27f852fe…` gen 9 | 20.33 | PASS | **FAIL** | 3/3 games stamped, uniform, sha == computed digest |
| 2 | `348df066…` gen 3 | 17.10 | PASS | **FAIL** | 3/3 games stamped, uniform, sha == computed digest |

Floor sensitivity (measured − floor, signed):

| candidate | witnessed_event_rate | flags_per_meeting | testimony_backed_conversion |
|---|---|---|---|
| `27f852fe…` | None vs 0.0339 → **FAIL** (0 kills — denominator empty) | 6.6667 − 1.0909 = **+5.5758 PASS** | 0.7500 − 0.0939 = **+0.6561 PASS** |
| `348df066…` | None vs 0.0339 → **FAIL** (0 kills) | 5.5000 − 1.0909 = **+4.4091 PASS** | 0.6000 − 0.1138 = **+0.4862 PASS** |

Core channels: impostor win 0.0 (both), ejection accuracy 1.0, meetings/game 0.67 / 1.0.
Reading (per the 17.12 selection-bar-honesty ruling — a legible instrument outcome, not
a silent rejection): the v3 lineage's real economy is **supply-rich because the impostor
is weak and gets prosecuted** — the crew converts testimony against it at 0.60–0.75,
flags mint at 5–6× the floor, and the impostor never kills (hence the degenerate
witnessed-kill gauge and referee FAIL). Watchability-gauge-passing, win-0: not flip-bar
material; the selection weight rides on the utility legs (pending).

### 4.2 Leg 01 — run-01-utility-champion, tranche 1 (seeds 4000–4002; session 1, COMPLETE)

Recorded solo, `meeting_timeout_seconds=900`, still inside the F7 impaired-status
window. Candidates: the swap-2 co-adaptation champion vs the swap-0 champion (= the
committed champion) — the campaign's central selection question on real bytes.

Pre-screen (spend advice ONLY): `8ac3652a…` predicted 1.6109 flags/meeting PASS,
`6d327dcb…` 1.6180 PASS; fake recorded flags 0 (flag-mintless) quoted beside. Real
recorded reads below are the paired recorded-bytes floor reads.

**Ranking (17.14 discipline):**

| rank | candidate | selection | validity | referee | win | ejection acc | stamp proof |
|---|---|---|---|---|---|---|---|
| 1 | `8ac3652a…` gen 9 (co-adapted) | 62.60 | PASS | FAIL | **0.000** | 0.857 | 3/3, uniform, sha == digest |
| 2 | `6d327dcb…` gen 3 (committed champion) | 41.27 | PASS | FAIL | **0.667** | 0.750 | 3/3, uniform, sha == digest |

Floor sensitivity (measured − floor, signed):

| candidate | witnessed_event_rate | flags_per_meeting | testimony_backed_conversion |
|---|---|---|---|
| `8ac3652a…` | 0.2308 − 0.0339 = **+0.1969 PASS** | 0.8333 − 1.0909 = **−0.2576 FAIL** | 0.5000 − 0.7508 = **−0.2508 FAIL** |
| `6d327dcb…` | 0.1429 − 0.0339 = **+0.1090 PASS** | 0.8889 − 1.0909 = **−0.2020 FAIL** | 0.6000 − 0.7039 = **−0.1039 FAIL** |

**Reading (the 17.12 honesty ruling applies):** the library's `selection_score` ranks by
watchability (+ referee bonus), so rank 1 is NOT the flip-bar reading. On the full row:
the co-adapted champion is watchability-RICHER (62.60 vs 41.27; witnessed rate 0.23;
4 meetings/game economy) and wins ZERO of three real games, while the committed champion
keeps the win edge (0.667 ≥ the same-substrate FSM 0.36) with the familiar starved-supply
referee FAIL. **Co-adaptation moved the champion along the §1.3 tension axis — toward
supply, away from winning — rather than past the flip bar**; its fake-path specialization
against the trained crew scorer did not transfer to real games (consistent with its
anchor-benchmark drop in §3.1). n=3 seeds; tranche 2 doubles this before any 18.26
naming leans on it.

### 4.3 Leg 02 — run-02-utility-lambda4, tranche 1 (seeds 4000–4002; session 1, COMPLETE)

Recorded solo, 900 s bound, F7 window. Candidates: the λ=4 lineage's two swap champions.
Pre-screen (advice only): both candidates predicted 1.2300 flags/meeting, floors PASS;
fake recorded flags 0 quoted beside; real recorded reads below.

**Ranking (17.14 discipline):**

| rank | candidate | selection | validity | referee | win | ejection acc | stamp proof |
|---|---|---|---|---|---|---|---|
| 1 | `10c1f9f3…` gen 3 | 35.90 | PASS | FAIL | **1.000** | 0.333 | 3/3, uniform, sha == digest |
| 2 | `2ca47451…` gen 9 | 32.33 | PASS | FAIL | **1.000** | 0.667 | 3/3, uniform, sha == digest |

Floor sensitivity (measured − floor, signed):

| candidate | witnessed_event_rate | flags_per_meeting | testimony_backed_conversion |
|---|---|---|---|
| `10c1f9f3…` | 0.3846 − 0.0339 = **+0.3507 PASS** | 1.0909 − 1.0909 = **+0.0000 PASS (at the floor)** | 0.2000 − 0.5735 = **−0.3735 FAIL** |
| `2ca47451…` | 0.3125 − 0.0339 = **+0.2786 PASS** | 0.0909 − 1.0909 = **−1.0000 FAIL** | 0.1818 − 1.0000 = **−0.8182 FAIL** |

**Reading: the strongest flip-bar candidate of the session.** `10c1f9f3…` wins 3/3 real
games (≥ the same-substrate FSM 0.36), passes the witnessed-kill gauge (+0.35), and
meets the flags floor EXACTLY — the first campaign candidate to clear two of three
supply gauges while holding the win edge. The remaining gap is the testimony-backed
conversion floor (0.20 vs the derived 0.57). Its opponents' ejection accuracy is 0.333
(crew ejections mostly WRONG against it — see the deflection cell, §5.3). n=3; tranche 2
is the priority next leg before any 18.26 naming.

### 4.4 Leg 03 — run-03-utility-bcanchor, tranche 1 (seeds 4000–4002; session 1, COMPLETE)

Recorded solo, 900 s bound, F7 window. Candidates: the bc-anchor lineage's swap
champions. Pre-screen (advice only): `a89be618…` predicted 1.2700 flags, **predicted
floors FAIL**; `6d327dcb…` 1.6180 PASS. Per blocker (4) the FAIL never gated — both
were recorded, and the real bytes REVERSED the advice (below).

**Ranking (17.14 discipline; stamp proofs 3/3, uniform, sha == digest on both):**

| rank | candidate | selection | validity | referee | win | ejection acc |
|---|---|---|---|---|---|---|
| 1 | `6d327dcb…` gen 3 (committed champion) | 51.70 | PASS | FAIL | 0.667 | 1.000 |
| 2 | `a89be618…` gen 9 (bc-anchor co-adapted) | 43.93 | PASS | FAIL | **0.667** | 0.750 |

Floor sensitivity (measured − floor, signed):

| candidate | witnessed_event_rate | flags_per_meeting | testimony_backed_conversion |
|---|---|---|---|
| `6d327dcb…` | +0.0994 PASS | 0.7273 − 1.0909 = −0.3636 FAIL | 0.5000 − 0.8603 = −0.3603 FAIL |
| `a89be618…` | +0.2161 PASS | 1.4000 − 1.0909 = **+0.3091 PASS** | 0.3750 − 0.4469 = **−0.0719 FAIL (the closest miss of the session)** |

**Two readings.** (1) `a89be618…` is now the candidate closest to the FULL flip bar:
win 0.667 ≥ FSM 0.36, witnessed +0.22 PASS, flags +0.31 PASS, conversion just −0.072
short — and it is the candidate whose pre-screen predicted FAIL. The prescreen-as-
spend-advice discipline (blocker 4) is vindicated in the direction the probe did not
emphasize: gating on the prediction would have DISCARDED the best candidate. Quoted
into §7 as finding F8. (2) The committed champion's appearance in two legs on the SAME
seeds is an incidental provider-noise replication: win 0.667 in both, flags 0.889 vs
0.727, conversion 0.60 vs 0.50 — win stable, gauge channels noisy at ±0.1–0.16, the
selection-tolerant noise scale design B priced in.

### 4.5 Leg 05 — run-05-freepolicy-v2-founders, tranche 1 (seeds 4000–4002; session 2 overnight chain, COMPLETE)

Candidates: the run's single swap champion (`43b113ec…`) + the impostor-family
exploiter (`119e5374…`, K=2 alternate — the first exploiter-probe member to reach a
real leg). Pre-screens PASS (3.06 / 3.22 predicted flags), advice only.

| rank | candidate | selection | validity | referee | win | witnessed | flags | conversion |
|---|---|---|---|---|---|---|---|---|
| 1 | `119e5374…` (exploiter) | 64.70 | PASS | FAIL | 0.000 | **0.0000 − 0.0339 FAIL** (5 kills, 0 witnessed) | 5.5000 **PASS** | 0.7500 **PASS** |
| 2 | `43b113ec…` (champion) | 53.60 | PASS | FAIL | 0.000 | **0.0000 FAIL** (7 kills, 0 witnessed) | 2.1429 **PASS** | 0.7143 **PASS** |

Stamp proofs 3/3, uniform, sha == digest on both. Distinct from the v3 shape: these
candidates DO kill (12 kills pooled) — every kill unwitnessed — while still losing
every game; the witnessed-kill gauge fails on stealth rather than on abstinence.

### 4.6 Tranche-2 extensions (seeds 4003–4005; session 2 overnight chain)

**Leg 04 t2** replicates t1 on fresh seeds — win 0.000 both candidates, zero kills,
flags 6.00 / 6.25 PASS, conversion 1.00 / 1.00 PASS, witnessed degenerate FAIL. The v3
supply-rich/win-0 economy is now stable across 6 seeds per candidate, not seed noise.

**Leg 01 t2**: `8ac3652a…` win 1/3, `6d327dcb…` win 1/3 on the fresh seeds. **Pooled
6-seed reads: committed champion win 3/6 = 0.500; co-adapted champion 1/6 = 0.167** —
the tranche-1 conclusion holds with doubled denominators (the committed champion keeps
the win edge ≥ the FSM 0.36; the co-adapted champion's watchability premium persists,
44.10 vs 30.97 on t2). Flags floors FAIL for both on both tranches.

<!-- SESSION-1-LEGS: extended per leg -->

---

## 5. Emergence-instrument sweeps (18.1/18.2/18.3 over the campaign's REAL-path recordings)

Discipline: byte-completeness FIRST — `compute_kill_craft_report` is the only instrument
with the completeness fence (the 18.2 model; 18.3 accepts EOF-truncated files by design),
so every recording dir passes kill-craft before any off-menu or deception denominator is
trusted. Deltas are quoted against the 18.4 memo's baseline cells **re-anchored at the
current committed corpus bytes** (the memo's own mechanical re-anchor rule: cells re-quote
at adopting records without re-ratification; the memo's prose values are baseline-5 and
the 18.13 baseline-6 re-record moved them). Current-tree corpus-9p2i anchor cells,
computed this session by the same instrument code over `replays/ml_corpus/9p2i`:

| cell | corpus 9p2i (baseline 6, current tree) |
|---|---|
| meetings / games | 463 / 150 |
| frame-attempt meetings | 437/463 = 0.9438 |
| frame conversions | 23/437 = 0.0526 |
| teammate accusations | 0/549 |
| false-vouch (saw_player) | 74/602 = 0.1229 |
| false-vouch (corroboration) | 31/176 = 0.1761 |
| false-vouch subject events (grounded+fabricated) | 63 (fabricated 16) |
| alibi survival | 59/77 = 0.7662 |
| effective deflection | 69/152 = 0.4539 |
| kills / crew-witnessed | 505 / 12 = 0.0238 |
| witnessed point-biserial (within one hop) | 0.2586 |
| action entropy (impostor mean conditional) | 0.6526 (300 agents / 6663 decisions) |
| action entropy (crew mean conditional) | 0.8693 (1050 agents / 22095 decisions) |
| off-menu | 0/6663 = 0.0 |

Claims are deferred to 18.27 — this section reports deltas, never rules. Entropy cells
are quoted but UNJUDGEABLE under §6.a of the memo as-recorded (no per-agent variance
field is emitted; the routed follow-up contract owns it).

### 5.1 Sweep — leg 04 tranche 1 (6 real games, byte-completeness fence PASSED first)

`compute_kill_craft_report` passed both candidate dirs (every game reached GAME_OVER
with a stamped terminal row) before any off-menu/deception denominator was read.
Cells (candidate arm / the re-anchored corpus column), n stated — at 3 games and 3–4
meetings per arm every rate cell is advisory-scale; z reads defer to 18.27 with the
18.26 same-seed FSM comparator arm, per the memo:

| cell | `27f852fe…` (gen 9) | `348df066…` (gen 3) | corpus 9p2i |
|---|---|---|---|
| **off-menu rate** | **79/101 = 0.782** | **114/120 = 0.950** | 0/6663 = 0.0 (structural) |
| meetings / games | 3 / 3 | 4 / 3 | 463 / 150 |
| kills (crew-witnessed) | 0 (–) | 0 (–) | 505 (12) |
| frame-attempt meetings | 3/3 | 3/4 | 437/463 |
| frame conversions | 0/3 | 0/3 | 23/437 |
| teammate accusations | 0/3 | 0/4 | 0/549 |
| false-vouch (saw_player) | 1/2 | 0/3 | 74/602 |
| impostor alibis (survived) | 0 (0) | 0 (0) | 77 (59) |
| impostor action entropy (cond.) | 0.4821 (6 ag / 101 dec) | 0.4735 (6 ag / 120 dec) | 0.6526 (300 / 6663) |
| crew action entropy (cond.) | 0.9086 | 0.9790 | 0.8693 |

**The headline cell: off-menu rate 0.78 / 0.95 against a structural-0 baseline** — the
first free-policy recordings the instrument has ever scored, and it fires massively.
Interpretation discipline: a free-policy agent CAN emit any legal intent by
construction, so a nonzero off-menu rate is the FAMILY's action space showing, and the
enabling lever is the family itself — the counterfactual "ablation" is the menu-bounded
utility lineage, whose recordings are on-menu by construction (0/…). Both arms of that
counterfactual exist in this campaign's artifacts; whether the specific off-menu
DISTRIBUTION (which kinds, which targets) constitutes a skill is 18.27's reading, fed
by the by-kind breakdowns in the sweep JSON. Zero kills across all 6 games also makes
kill-craft cells degenerate for this lineage (no downward tail exists; stated, not
scored). Entropy cells quoted but UNJUDGEABLE per the memo (no per-agent variance
field — the routed follow-up contract).

### 5.2 Sweep — leg 01 tranche 1 (6 real games, completeness fence PASSED first)

| cell | `8ac3652a…` (co-adapted) | `6d327dcb…` (committed) | corpus 9p2i |
|---|---|---|---|
| off-menu rate | **0/142 = 0.0** | **0/132 = 0.0** | 0/6663 (structural) |
| meetings / games | 12 / 3 | 9 / 3 | 463 / 150 |
| kills (crew-witnessed) | 13 (3) | 14 (2) | 505 (12) |
| frame-attempt meetings | 12/12 | 9/9 | 437/463 = 0.944 |
| frame conversions | 0/12 | 1/9 | 23/437 = 0.0526 |
| teammate accusations | 0/14 | 0/12 | 0/549 |
| false-vouch (saw_player) | 2/16 (1 fabricated) | 3/16 (1 fabricated) | 74/602 (16 fab.) |
| impostor alibis (survived) | 2/2 | 3/3 | 77 (59) |
| effective deflection | 0/5 | 1/2 | 69/152 |
| impostor action entropy (cond.) | 0.4358 | 0.4452 | 0.6526 |

The utility arms are **on-menu by construction (0.0)** — the structural counterfactual
to §5.1's 0.78/0.95, both arms now recorded inside this campaign's artifacts. The
co-adapted champion's meeting economy is denser (4.0 meetings/game vs the committed
champion's 3.0 and the corpus 3.1) with 100% frame-attempt meetings and no conversions;
alibi survival is 5/5 pooled (advisory n). No cell at this n is claim-grade; deltas
defer to 18.27 with the 18.26 comparator arms.

### 5.3 Sweep — leg 02 tranche 1 (6 real games, completeness fence PASSED first)

| cell | `10c1f9f3…` (gen 3, the flip-bar candidate) | `2ca47451…` (gen 9) | corpus 9p2i |
|---|---|---|---|
| off-menu rate | 0/153 = 0.0 (structural) | 0/140 = 0.0 | 0/6663 |
| meetings / games | 11 / 3 | 11 / 3 | 463 / 150 |
| kills (crew-witnessed) | 13 (5) | 16 (5) | 505 (12) |
| frame-attempt meetings | 11/11 | 11/11 | 437/463 |
| frame conversions | 1/11 | 0/11 | 23/437 |
| teammate accusations | 0/17 | 0/14 | 0/549 |
| false-vouch (saw_player) | 0/14 (0 fabricated) | 1/14 (0 fab.) | 74/602 |
| impostor alibis (survived) | 2/2 | 7/7 | 77 (59) |
| **effective deflection** | **6/8 = 0.750** | 1/9 = 0.111 | 69/152 = 0.454 |
| impostor action entropy (cond.) | 0.4410 | 0.5717 | 0.6526 |

**Candidate behavior surfaced: elevated deflection efficacy on the flip-bar candidate**
(0.750 vs corpus 0.454, and vs its own sibling's 0.111) — coherent with its 0.333
opponent ejection accuracy: when this impostor is actively suspected, its meeting-layer
deflection survives at an elevated rate. Advisory-scale n (8 active survivals);
candidacy is PENDING tranche-2 denominators before it reads as a §6-claimable delta.
The 18.4-named lever is `anchor-lambda=4.0`; the fake-path ablation twin
(`ablation-run-02-anchor-lambda`: identical config + master seed, anchor weight
reverted to the committed λ=1.0) is RUNNING at this section's session-1 close — its
provenance lands in §6.2 regardless of how candidacy resolves, and any meeting-layer
half of the ablation (real-path re-recording) is priced for a later session only if
tranche 2 sustains the delta.

### 5.4 Sweep — leg 03 tranche 1 (6 real games, completeness fence PASSED first)

| cell | `6d327dcb…` (committed) | `a89be618…` (bc-anchor) | corpus 9p2i |
|---|---|---|---|
| off-menu rate | 0/139 (structural) | 0/136 | 0/6663 |
| meetings / games | 10 / 3 | 11 / 3 | 463 / 150 |
| kills (crew-witnessed) | 12 (3) | 15 (2) | 505 (12) |
| frame attempts / conversions | 9/10, 1/9 | 10/11, 0/10 | 437/463, 23/437 |
| teammate accusations | 0/11 | 0/14 | 0/549 |
| impostor alibis (survived) | 3/3 | 3/3 | 77 (59) |
| effective deflection | 2/6 | 0/3 | 69/152 |
| impostor action entropy (cond.) | 0.6005 | 0.4700 | 0.6526 |

No new candidate behaviors at this n beyond the §5.3 deflection cell (which this leg's
committed-champion arm does NOT reproduce — 2/6 — sharpening it as λ=4-lineage-specific
if tranche 2 sustains it). Pooled alibi survival across utility legs is now 13/13.

### 5.5 Sweeps — leg 05 t1 + tranche-2 extensions (completeness fence PASSED on all six dirs)

| cell | v2 champion | v2 exploiter | v3 gen9 (t2) | v3 gen3 (t2) | utility gen9 (t2) | utility gen3 (t2) | corpus |
|---|---|---|---|---|---|---|---|
| **off-menu rate** | **41/114 = 0.360** | **41/106 = 0.387** | 75/83 = 0.904 | 73/83 = 0.880 | 0/155 | 0/181 | 0.0 |
| meetings / games | 7 / 3 | 6 / 3 | 4 / 3 | 4 / 3 | 11 / 3 | 10 / 3 | 3.1/g |
| kills (witnessed) | 7 (0) | 5 (0) | 0 | 0 | 14 (4) | 13 (5) | 505 (12) |
| frame attempts / conv | 5/7, 0 | 5/6, 0 | 3/4, 0 | 3/4, 0 | 10/11, 0 | 9/10, 0 | 437/463, 23 |
| impostor entropy (cond.) | **0.883** | **0.939** | 0.388 | 0.510 | 0.441 | 0.882 | 0.6526 |

**The off-menu family gradient is now measured at both free-policy points: utility 0.0
(structural) → v2 ≈ 0.36–0.39 → v3 ≈ 0.88–0.95** (v3's t2 replicating t1). The v2
candidates' kill profile is stealth-shaped (12 kills, 0 witnessed pooled — vs the
corpus 2.4% witnessed rate this is unremarkable statistically at n=12, but coherent
with the exploiter's breeding objective), and v2 impostor entropy sits ABOVE the corpus
FSM (0.88–0.94 vs 0.65) where utility/v3 sit below. All cells remain advisory-scale;
z reads defer to 18.27 with the 18.26 comparator arms.

<!-- SESSION-1-SWEEPS: extended per leg -->

---

## 6. Counterfactual ablations (the 18.4-named discipline)

For every candidate emergence behavior §5 surfaces (a delta the 18.27 reading could rule
on), the named ablation `ablation:<instrument-key>/<lever-id>` is RUN — disable the
enabling lever (conviction-term, anchor-lambda=<value>, pfsp-sampler, encoder-v3, …),
re-run the enabling leg under identical seeds, and record the behavior receding (or not).
Fake-path re-runs suffice where the behavior is tactical; provenance is never mixed
(fake ablation vs same-seed fake FSM arm; real ablation vs the 18.26 real comparator).
An unablated candidate reads NOT-DEMONSTRATED by construction.

### 6.1 `ablation:*/conviction-term` — the run-01 twin (session 1, RUN, complete)

Pre-positioned for whichever conviction-term-enabled behavior the sweeps surface (the
term is the protocol decision's own lever), and standing protocol evidence in its own
right. Config: byte-identical to run-01 (same `master_seed=182401`, same budgets/seeds)
with `conviction=None`; 2 400 games, 12 rows; frozen artifacts at
`training/artifacts/coevo/ablation-run-01-conviction-term/`.

**Result: the impostor champion lineage is IDENTICAL with the term on and off** — swap 0
`6d327dcb…`, crew swap 1 `22c9707e…`, swap 2 `8ac3652a…` reproduce sha-for-sha; only the
final crew champion diverges (`31ca14b5…` with the term vs `81ea76a4…` without, and the
ablated twin's final crew swap froze three extra impostor-family exploits). Reading: at
this budget on the utility lineage the conviction term shifted fitness VALUES by its
addend (~+0.8 ≈ 0.5 × mean predicted supply) but was **non-decisive for impostor
selection**; the crew side's selection DID respond to the term. Consequences: (a) any
sweep delta on run-01's impostor champion cannot be attributed to the conviction term
(the ablated twin selects the same genome — the behavior cannot recede because it is
identical by construction); (b) the term's live selection pressure this phase is
currently a CREW-side phenomenon on the utility family — quoted into §7 as finding F6
and available to 18.25.

### 6.2 `ablation:*/anchor-lambda=4.0` — the run-02 twin (session 1, RUN, complete)

Named lever for the λ=4 lineage's §4.3 flip-bar result and the §5.3 deflection
candidate. Config: byte-identical to run-02 (same `master_seed=182402`, same seed
budgets, same lambda-4.0 `initial_genome`, conviction term kept) with `anchor_weight`
reverted to the committed λ=1.0; 2 532 games, 12 rows; frozen artifacts at
`training/artifacts/coevo/ablation-run-02-anchor-lambda/`.

**Result: the lever is SELECTION-DECISIVE on this lineage** — the impostor champion
diverges at generation 1 (swap 0 freezes `ea4bc955…`, not `10c1f9f3…`), the ablated
lineage's champion-side anchors run ~1.9 points closer to the FSM (19.21–19.32 vs
17.28–17.57), and its swap-2 impostor champion never updates (no swap-2 freeze). The
crew champions reproduce sha-identical across the pair despite facing different
impostor opponents (the crew selection basin is robust at this budget). Contrast with
§6.1: the conviction term was non-decisive; the anchor weight is the lever that
actually steers utility-family impostor selection here. Consequences: (a) the §5.3
deflection candidate HAS a live counterfactual arm — the ablated champion is a
different genome, so a recede read is meaningful; (b) completing that read for a
meeting-layer cell requires the ablated champion's REAL-path recordings (priced ~2 h,
scheduled only if tranche 2 sustains the delta); the fake-path halves (artifacts,
provenance, trajectory divergence) are recorded here either way.

<!-- SESSION-ABLATIONS: extended as candidates surface -->

---

## 7. Findings (integration findings + routed items; never silent patches)

- **F1 — per-generation champion genomes are not persisted by the merged driver.** Only
  swap champions and exploiter finds reach the hall; the per-generation
  `champion_weights_sha256` in the rows has no reloadable genome. The contract's
  "per-generation real-path top-K re-ranks" therefore runs per impostor SWAP here (§4).
  Routed: a driver amendment (persist per-generation champion genomes, or expose the ES
  champion trace per generation) if per-generation real selection proves load-bearing —
  never a silent machinery patch in this campaign.
- **F2 — the founder-restart clause is family-gated.** The only committed MAP-Elites
  founder pool is v2/1049 (`bakeoff_substrate_sha`-fenced). Utility (19) and v3 (1442)
  lineages cannot ingest it (the driver's reload length-check), so their sessions restart
  with EMPTY pools (FSM mode until fresh champions freeze). If cross-session pool
  continuity proves load-bearing for those families, the routed item is a per-family
  founder pool (a 18.6-shaped cell persistence run at the current substrate).
- **F3 — founder-opponent games are ~2 orders costlier than champion games.** ~10–15
  s/game vs ~0.1 s (low-kill founder corners run toward the 1000-tick cap), so the
  exact-pool-cover payoff row dominates a founder campaign's wall-clock. Priced into
  run-05's budget (§1.4); a routed consideration for 18.25's sizing.
- **F4 — the 18.4 memo's prose cells are stale at baseline 6.** The memo's own re-anchor
  rule covers this (§5); noted so no future reader quotes the memo's baseline-5 numbers
  against baseline-6 recordings.
- **F5 — operational: instrument/table walks over rollout recordings need the roster
  sidecar and no audit sidecars.** `rollout_coevo` writes neither convention
  (`roster.json` absent → the walk defaults to 4p1i and the state-hash fence refuses;
  `*.audit.jsonl` present → the seed glob refuses). The session harness writes
  `roster.json` and drops audit sidecars for its pre-screen dirs — the same idiom
  `training/realpath.py` applies to its own recordings.

- **F7 — one re-rank leg at a time.** Two concurrent `run_realpath_rerank` processes on
  the 4-unit Featherless plan (a 27B request uses 2 units; a meeting's parallel ballot
  phase can fill both slots from ONE game) push per-meeting wall-clock past the
  library's 300 s timeout proxy, and every timeout burns one of the 8 per-seed
  attempts — observed live in session 1 (both legs' first seeds stalled at their first
  meeting through 7 attempts; the 8th attempt then timed out even SOLO —
  `RealPathSeedExhaustedError`, 8/8 timeouts on `meeting-0`). A real 9-player meeting
  (opening + chain + opt-ins + 9 parallel ballots ≈ up to ~20 27B calls with
  rendered-memory prompts) exceeds 300 s at this plan's throughput even with one leg.
  The standing "2 staggered workers" runbook line is about `run_tournament` seed-range
  workers and does NOT transfer to concurrent re-rank legs. Session-1 remedy, both via
  documented config: one leg at a time + `meeting_timeout_seconds=900` (still a real
  hang bound; the proxy exists to catch hangs, not to price slow meetings).
  **Measurement provenance caveat:** the session-1 timeout exhaustion and per-game
  wall-clock were recorded during a Featherless status window the owner reports as
  PARTIALLY IMPAIRED — the 300 s default may be adequate at healthy status, and this
  leg's wall-clock is NOT representative pricing. Re-measure the timeout question at
  healthy provider status before folding this repricing into 18.25's duration honesty;
  the recordings themselves stay valid regardless (the validity gate checks model +
  cost, never latency).
- **F8 — the pre-screen's advisory-only status protected the best candidate.** The
  session's closest full-flip-bar candidate (`a89be618…`, §4.4: win 0.667 + witnessed
  PASS + flags PASS, conversion −0.072) is the one candidate whose pre-screen predicted
  floors FAILED. Blocker (4) frames the divergence hazard as predicted-PASS/recorded-
  FAIL; session 1 exhibited the mirror image — predicted-FAIL/recorded-mostly-PASS —
  and the spend-advice-only discipline is what kept the candidate in play. The
  prescreen's value at this budget is directional supply prediction, not candidate
  gating in either direction.
- **F6 — the conviction term was non-decisive for impostor selection on the utility
  lineage at this budget.** The run-01 same-seed `conviction=None` twin (§6.1) reproduced
  the impostor champion lineage sha-for-sha; only crew selection diverged. The term's
  in-loop pressure is real (fitness values shift by the addend) but below the selection
  threshold on this family/budget; its selection-relevant effect in session 1 is
  crew-side. This bounds what any 18.27 emergence claim may attribute to the term on
  this lineage, and is direct input to 18.25 (where the term is the crew-fitness
  counterweight by design).

<!-- SESSION-FINDINGS: extended as they land -->

---

## 8. Finalists for 18.26

Named when the campaign's legs and sweeps are complete (a later session). The naming will
quote, per finalist: the frozen artifact sha, the real-path re-rank row (stamp proof,
floor sensitivity), the conviction-meter reading under §1.1's guard, and the sweep cells
its candidacy rests on.

<!-- SESSION-FINALISTS: pending -->

---

## 9. Reproduce

Every figure re-derives from committed bytes. The five run configs are exactly:

```python
# session harness (operator-authored; the machinery is consumed frozen)
from pathlib import Path
from training.anchor_study import compute_substrate_sha
from training.bakeoff.harness import load_candidate_weights, load_conviction_fitness_term
from training.bakeoff.map_elites import bakeoff_substrate_sha
from training.bakeoff.policy_es import build_masked_mlp_policy
from training.bakeoff.utility_es import build_utility_scorer_policy
from training.coevo.driver import CoevoCampaignConfig, CoevoSideConfig, run_alternating_freeze
from training.crew.options import OwnedTaskOptionBasis
from training.crew.scorer import build_crew_scorer

composite = compute_substrate_sha()      # 9bc00af0…  (fails the stale-seed fence loudly if moved)
manifest = bakeoff_substrate_sha()       # e4547789…
crew = CoevoSideConfig(
    side="crew", genome_length=27,
    build_policy=lambda g: build_crew_scorer(g, basis=OwnedTaskOptionBasis()),
    encoder_version="crew-option-features-v2",
    initial_genome=load_candidate_weights(Path("training/artifacts/crew/crew-owned-tasks-es")),
)
common = dict(
    crew=crew, num_swaps=4, generations_per_swap=3,
    fitness_seeds=(1000, 1001, 1002, 1005, 1006, 1007),
    benchmark_seeds=(2000, 2001, 2002, 2003), payoff_seeds=(3000, 3001, 3002, 3003),
    conviction=load_conviction_fitness_term(Path("training/artifacts/conviction")),
)
champion = load_candidate_weights(Path("training/artifacts/impostor/utility-es"))
# run-01: impostor side = utility family, initial_genome=champion, master_seed=182401,
#         substrate=(composite, "compute_substrate_sha"), work_dir/hall_root fresh.
# run-02: initial_genome=load_candidate_weights(…/anchor_study/lambda-4.0), anchor_weight=4.0, seed 182402.
# run-03: initial_genome=champion, anchor_policy=build_utility_scorer_policy(
#         load_candidate_weights(…/anchor_study/filtered-bc-anchor)), seed 182403.
# run-04: genome_length=1442, build_policy=lambda g: build_masked_mlp_policy(g, hidden=8,
#         encoder_version="v3"), encoder_version="v3", no initial_genome, seed 182404,
#         substrate=(manifest, "bakeoff_substrate_sha").
# run-05: genome_length=1049, encoder_version="v2", initial_genome=load_candidate_weights(
#         …/impostor/policy-es), founder_cells_dir=…/impostor/map-elites, seed 182405,
#         substrate=(manifest, "bakeoff_substrate_sha"), num_swaps=2, generations_per_swap=2,
#         payoff_seeds=(3000, 3001), benchmark_seeds=(2000, 2001, 2002).
# hall_root = training/artifacts/coevo/<run-name>; work_dir outside the tree.
# result = run_alternating_freeze(CoevoCampaignConfig(work_dir=…, substrate_sha256=…,
#          substrate_sha_kind=…, impostor=…, master_seed=…, **common))
```

Verification pins over the committed rows: `uv run pytest
tests/training/test_coevo_driver.py -k CommittedImpostorCampaign`.

Determinism caveat (house convention): the fake-path runs are deterministic under
`master_seed` on the recording platform (macOS this session); float channels carry the
documented origin-platform ULP caveat — committed bytes + sha sidecars are the ground
truth, and the row pins assert structure, never absolute floats.

Real legs (per §4): `AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b
AILIBI_SEED_MAX_ATTEMPTS=8` + `FEATHERLESS_API_KEY`, then `run_realpath_rerank`
(seeds 4000–4005) over hall-reloaded genomes; sweeps per §5 run kill-craft first.

---

## 10. How downstream consumes this

- **18.25 (crew campaign):** trains against the frozen impostor champions in
  `training/artifacts/coevo/<run>/impostor/` via `impostor.initial_genome` (no hall-as-pool
  seam); F3's founder-cost pricing informs its sizing.
- **18.26 (real-LLM finalist eval):** consumes §8's named finalists + frozen artifacts;
  records the same-seed scripted-FSM comparator arms the emergence claims need.
- **18.27 (the reading):** consumes §5's sweep cells + §6's ablation provenance under the
   18.4 four-part discipline; §3's cycling verdicts and §4's floor sensitivity are its
  selection-evidence base. This report never rules.
- **18.28 (the close):** carries §7's routed findings; the composed-provenance-validity
  open item rides the close either way.
