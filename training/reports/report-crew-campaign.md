# The crew campaign — the counter-adaptation half of the phase's co-evolution (Task 18.25, operator, multi-session)

**Task:** 18.25 — THE CREW CAMPAIGN (operator, multi-session, ~30–40h real-path legs)
**Machinery consumed (frozen, never edited here):** training/coevo/driver.py (18.19/18.20/18.21/18.31), training/crew/ (15.16/15.22), training/realpath.py (18.17/18.31 + the 18.32 crew re-rank arm), scripts/generate_campaign_tables.py (18.31), scripts/run_tournament.py --crew-artifact (18.19)
**Section refs:** the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)
**Date started:** 2026-07-28
**Last evidence recorded:** 2026-07-28 (session 1)
**Status:** IN PROGRESS — fake-path runs recording; real-path legs blocked on the 18.32 amendment (the Amend + overlap ruling, owner 2026-07-28).

Every table in this report is GENERATED from committed artifacts via
`scripts/generate_campaign_tables.py` (the F12 lesson), never hand-assembled.

## 1. Protocol (fixed before any run)

### 1.1 The seed decision and reachability honesty

The impostor side enters via `impostor.initial_genome` seeded from the committed 18.24
candidate `ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f`
(intermediates/run-02-utility-lambda4/gen-2 — finalist 1a, pooled 6/6, the λ=4 regime;
`anchor_weight=4.0` on the impostor side per the seed's own config.json). There is NO
seam for adopting 18.24's committed hall as this campaign's opponent pool (the merged
driver, 316d4e5): the seed re-freezes as a fresh lineage in this campaign's own hall at
the first impostor-moving swap boundary, and the counter-adaptation reading is against
that lineage plus this campaign's accumulating hall. The runner-up alternative
`bfd145cb…` (runnerups/run-02-utility-lambda4/gen-9 — never a champion) is the
documented alternative seed; both load through `--candidate-artifact` (F14, verified
session 1 before any run). If full-pool continuity is judged load-bearing, that is a
routed amendment, never a silent driver edit.

### 1.2 Founder honesty

The committed MAP-Elites founder pool is v2 free-policy (1049-gene); the utility-family
(19-gene) impostor side CANNOT ingest it (the driver's genome-length reload check), so
`founder_cells_dir` stays UNSET and the opponent pool starts EMPTY, accumulating
swap-frozen members + exploiter finds only. If pool diversity proves load-bearing
mid-campaign, the routed conditional is a utility-family founder-persistence run
(18.6-shaped), recorded in 18.28's deferred ledger. F3 (founder-game pricing) is moot
while founders cannot load.

### 1.3 The crew sides, the conviction counterweight, and the guards

Both crew bases run, one per campaign run:

| run | crew base | encoder_version | genome | initial_genome |
|---|---|---|---|---|
| run-c1-crew-owned-tasks | owned-task (15.22) | `crew-option-features-v2` | 27 | training/artifacts/crew/crew-owned-tasks-es |
| run-c2-crew-general | general (15.16) | `crew-option-features-v1` | 22 | training/artifacts/crew/crew-utility-es |

The conviction-supply term (GO verdict, `training/artifacts/conviction/`, weight 0.5) is
the crew-fitness counterweight: `correct_reports` requires a crewmate-routed body report
that EJECTS an impostor (`training/rewards.py::_crew_terms`), so on the forced-fake
meeting path it is identically 0 every episode — a dead gradient the conviction term
replaces. A FRESH `ConvictionFitnessTerm` is constructed per run (the 18.24 §9 mutable
use-counter note). The 18.24 F6 twin evidence is on this campaign's side: the run-01
same-seed `conviction=None` twin reproduced the impostor champion lineage sha-for-sha
while CREW selection diverged (with-term crew gen-12 champion `31ca14b5…` vs without-term
`81ea76a4…` — committed twin halls at `training/artifacts/coevo/run-01-utility-champion/`
and `…/ablation-run-01-conviction-term/`; quoted from committed artifacts, not report
prose, per §12 Errata).

Crew mechanics the driver pins (verified at config preflight, session 1): `first_side="crew"`;
the crew side structurally REJECTS `anchor_policy` (crew anchor-CE is FSM-fixed by
construction — `CrewDecisionTrace` anchors on the scripted FSM only); the crew builder
emits a `crew-`-prefixed `encoder_version` (the 18.19 conflation guard, both directions);
`run_label` is set per run (never the default). The 15.22 interrupt-preserving guard
holds structurally on the owned-task base (a visible body → ONLY `report` in the
selectable set — starvation unreachable by construction). **Scope caveat:** the general
(v1) base predates the guard and keeps `report` as one option among many; for run-c2 the
starvation-family exclusion rests on the selection filters and the validity/referee
gates, and is watched per entrant (the DoD's gate-validity discipline).

### 1.4 Scenario adoption — DECLINED for the main runs

The scenario library holds exactly ONE crew scenario (`body-discovery-latency`, max 1.0);
meaningful crew scenario pressure beyond discovery latency means AUTHORING new crew
specs — new work, not configuration. Scenario terms also add AFTER the slate mean,
making row fitness scalars non-comparable to 18.24's rows and to any pre-scenario rows.
Decision (session 1): the main runs adopt NO scenario provider; comparability and the
single-thin-scenario reality both argue against. If adopted later in an ablation twin,
it will use the AGENT-FACTORY seam only (the selector seam drives every seat under an
unenforced delegation convention and is never a campaign configuration), and its
`games_per_evaluation` is advisory only (nothing meters it) — quoted here per contract.

### 1.5 Meeting layer honesty

The campaign runs under the default forced-fake meeting layer: every meeting resolves
SKIPPED, so the kill-witness survival clause is vacuous and `correct_reports` never
fires (see §1.3). The composed runner is GO (`training/artifacts/composed/verdict.json`)
but is NOT adopted for the fake-path runs — final champion numbers are never
composed-runner-scored (standing rule), and the campaign keeps 18.24's fake-path
benchmark comparability. Force-parity's unnamed crew-ejection channel therefore stays
dormant in this campaign's fake path; the real-path legs (real LLM meetings) are where
ejection is live.

### 1.6 Sizing + meters

Mirrors 18.24 runs 01–03: `num_swaps=4`, `generations_per_swap=3` (12 generations/run,
crew moving swaps 0/2, impostor swaps 1/3), population 6, slate 3,
`fitness_seeds=(1000,1001,1002,1005,1006,1007)`, `benchmark_seeds=(2000,2001,2002,2003)`,
`payoff_seeds=(3000,3001,3002,3003)`, `master_seed` 182501 (c1) / 182502 (c2), substrate
`compute_substrate_sha` = `9bc00af0f9e76719cb78d66c5593ec178312716528715f4a580677fb519f04f4`
(asserted equal to 18.24's recorded composite at harness start — stale-seed honesty).
Projected fake-path bound 3,816 games/run under the 25,000 ceiling.

### 1.7 The real-path protocol (pre-registered; legs pending 18.32)

Two-leg concurrency is the runbook default (owner directive 2026-07-28, superseding
18.24's F7 one-leg correction): TWO legs concurrently, always different tranches or
work_dirs (the 18.31 tranche claim refuses same-tranche concurrency), staggered starts
with jittered backoff, `meeting_timeout_seconds=900`, 3-seed tranches (4000–4002 /
4003–4005), each leg internally sequential. F7's one-leg numbers were measured under a
partially-impaired provider window; if impairment symptoms reappear (rising timeout or
retry-exhaustion rates in the native leg logs), degrade to one leg and record the switch
here — duration honesty prices whichever posture actually ran. The §4.0-style stability
table is computed after the FIRST retested candidate, and the campaign does not proceed
at a seed budget whose measured noise exceeds 25% of any threshold it tests (F12).
Recording env: `AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b` +
`FEATHERLESS_API_KEY`; recordings follow the F5 convention (`roster.json` present, audit
sidecars out). Every crew artifact this campaign freezes carries the five-field stamp
(native 18.31 loadable freezes), and the re-rank legs are the first dual-stamped crew
recordings (18.7/18.19's first live crew exercise — any conflation or leak finding stops
the campaign leg until routed).

## 2. Session ledger (the multi-session index)

| session | date | work | evidence |
|---|---|---|---|
| 1 | 2026-07-28 | Protocol fixed; F14 seed smokes; run-c1 + run-c2 fake-path runs; 18.32 routed (Amend + overlap ruling); checkpoint-push per run | this report §1/§3; `training/artifacts/coevo/run-c1-crew-owned-tasks/`; commit a9a74bc |

## 3. The campaign rows (fake/surrogate path; per run)

### 3.1 run-c1-crew-owned-tasks (session 1 — COMPLETE, 2432 games, 12 rows)

| gen | swap | moving | pool | champion_fitness | updated | anchor_champ | anchor_fsm | exploiter | conv_uses | games_cum |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | crew | 0 | 12.6592 | yes | 9.6731 | 17.2500 | **frozen** 19.50>17.25 | 165 | 170 |
| 2 | 0 | crew | 1 | 11.4966 | yes | 10.4026 | 17.5000 | **frozen** 21.50>17.50 | 297 | 344 |
| 3 | 0 | crew | 2 | 11.5314 | yes | 10.4373 | 17.5000 | **frozen** 21.50>17.50 | 459 | 522 |
| 4 | 1 | impostor | 1 | 18.6421 | yes | 17.5889 | 9.8409 | **frozen** 13.42>9.84 | 617 | 696 |
| 5 | 1 | impostor | 2 | 18.6615 | no | 17.5889 | 9.8409 | duplicate | 786 | 874 |
| 6 | 1 | impostor | 2 | 18.6615 | no | 17.5889 | 9.8409 | duplicate | 955 | 1052 |
| 7 | 2 | crew | 4 | 11.0986 | yes | 10.4878 | 17.5000 | **frozen** 21.50>17.50 | 1295 | 1280 |
| 8 | 2 | crew | 5 | 11.3945 | yes | 10.5190 | 17.5000 | **frozen** 21.50>17.50 | 1784 | 1554 |
| 9 | 2 | crew | 6 | 11.1466 | yes | 10.4660 | 17.5000 | **frozen** 20.00>17.50 | 2145 | 1790 |
| 10 | 3 | impostor | 3 | 18.7026 | no | 17.5889 | 9.8409 | **frozen** 13.42>9.84 | 2473 | 2014 |
| 11 | 3 | impostor | 4 | 18.6615 | no | 17.5889 | 9.8409 | **frozen** 12.91>9.84 | 2670 | 2200 |
| 12 | 3 | impostor | 5 | 18.6615 | no | 17.5889 | 9.8409 | **frozen** 13.42>9.84 | 3021 | 2432 |

Meters: conviction 3021 uses; games 2432 / bound 3816. Frozen swap champions: swap 0
crew `72adb41c…`; swap 1 impostor `0ca3a382…`; swap 2 crew `0bf179b7…`; swap 3 impostor
deduped (`champion_frozen=False`, sha `0ca3a382…` already a member). Exploiter freezes: 10.

Digest: `7a6136962e6884cebde84286947bfa6dd8e3ef315c323cbc1b83d9602774c201`.

First readings (session 1, fake path — screens, not verdicts): the crew champion's
fitness DECLINES within crew-moving swaps as the opponent pool hardens (12.66 → 11.53 in
swap 0 at pool 0→2; 11.10 → 11.15 at pool 4→6) while its anchor-CE benchmark stays flat
(anchor_champ ~10.4–10.5) — opponent pressure, not anchor drift. The seeded impostor
improved exactly once (gen-4, `champion_updated=yes`, genome moved off the ea4bc955 seed
to `0ca3a382…`) and then plateaued for both its swaps — consistent with 18.24's run-02
plateau signature on the same lineage. Cycling verdict deferred to §3.6 (needs both runs).

### 3.2 run-c2-crew-general (session 1 — COMPLETE, 2574 games, 12 rows)

| gen | swap | moving | pool | champion_fitness | updated | anchor_champ | anchor_fsm | exploiter | conv_uses | games_cum |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | crew | 0 | 16.0548 | no | 15.2257 | 10.2500 | **frozen** 16.50>10.25 | 0 | 170 |
| 2 | 0 | crew | 1 | 10.5070 | yes | 15.3738 | 9.5000 | **frozen** 16.75>9.50 | 1 | 344 |
| 3 | 0 | crew | 2 | 11.2659 | yes | 15.5000 | 9.0000 | **frozen** 17.00>9.00 | 24 | 564 |
| 4 | 1 | impostor | 1 | 14.5632 | yes | 17.7415 | 10.6254 | **frozen** 14.33>10.63 | 58 | 738 |
| 5 | 1 | impostor | 2 | 14.5632 | no | 17.7415 | 10.6254 | **frozen** 14.33>10.63 | 94 | 916 |
| 6 | 1 | impostor | 3 | 14.9903 | no | 17.7415 | 10.6254 | duplicate | 167 | 1140 |
| 7 | 2 | crew | 4 | 11.4778 | yes | 6.2017 | 6.0000 | **frozen** 17.50>6.00 | 256 | 1410 |
| 8 | 2 | crew | 5 | 11.5651 | no | 6.2017 | 6.0000 | **frozen** 17.50>6.00 | 324 | 1642 |
| 9 | 2 | crew | 6 | 11.3060 | yes | 6.2178 | 6.0000 | **frozen** 17.50>6.00 | 393 | 1878 |
| 10 | 3 | impostor | 4 | 14.5883 | yes | 17.7461 | 10.6254 | **frozen** 14.14>10.63 | 434 | 2064 |
| 11 | 3 | impostor | 5 | 15.1517 | no | 17.7461 | 10.6254 | **frozen** 14.36>10.63 | 554 | 2338 |
| 12 | 3 | impostor | 6 | 14.5882 | yes | 17.8085 | 10.6254 | **frozen** 14.33>10.63 | 635 | 2574 |

Meters: conviction 635 uses; games 2574 / bound 3816. Frozen swap champions: swap 0 crew
`7fa59718…`; swap 1 impostor `1577942b…`; swap 2 crew `515fc066…`; swap 3 impostor
`105f7a88…` (fresh — no dedup, unlike c1). Exploiter freezes: 11.

Digest: `7e6823772f783fdc48f24878f518c10022dff4216323729fd715f45e3dae70e0`.

First readings (session 1, fake path — screens, not verdicts): **the starvation-family
watch is LIVE for this lineage.** Conviction served 635 uses across the run vs c1's
3021, with ZERO uses at gen-1 — the general (v1) base has no structural report guard
(§1.3 scope caveat) and its early lineage is meeting-scarce; every c2 entrant named
downstream carries this watch through the validity/referee gates. Unlike c1's plateau,
c2's impostor champion kept UPDATING (gens 4/10/12) — the general crew applies live
opponent pressure the owned-task crew did not. The swap-2 benchmark pair collapses
(anchor_champ 15.5 → 6.2 beside anchor_fsm 9.0 → 6.0) after the swap-1 impostor froze —
a benchmark-environment shift to read against the real path, not a crew regression alone.

### 3.6 Cross-run readings — PENDING (fuller reading rides the real-path legs)

The two bases separate on the fake path already: the owned-task (c1) crew is
meeting-rich (conviction 3021) and its impostor opponent plateaus; the general (c2) crew
is meeting-scarce (635, 0 at gen-1) and its impostor opponent keeps improving. Which
converts pace to wins on the REAL path (the 17.13 cell) is exactly what §4 measures.

## 4.0 MEASUREMENT RELIABILITY — read this before any §4 number

PENDING — computed via `generate_campaign_tables.py stability` after the FIRST retested
candidate (the F12 precondition; the campaign does not proceed at a seed budget whose
measured noise exceeds 25% of any threshold it tests).

## 4. Real-path re-rank legs (18.17/18.31/18.32 machinery; 17.14 table discipline)

BLOCKED on 18.32 (the crew re-rank arm) — routed session 1, the Amend + overlap ruling:
`run_realpath_rerank` as merged at e2a040b is impostor-only (candidate family whitelist,
no frozen-opponent seam, no dual-stamp read-back), so the contract's dual-stamped crew
re-rank legs cannot be discharged through the mandated machinery until the amendment
lands. Fake-path evolution proceeded in the overlap (this section's legs re-rank the
committed gen-champions — persistence is default-on, so no back-fill recovery is needed,
the F1 lesson closed).

<!-- all legs recorded -->

## 5. Emergence-instrument sweeps — PENDING (rides the real-path recordings)

<!-- all sweeps recorded -->

## 6. Counterfactual ablations (the 18.4-named discipline) — PENDING

## 7. Findings (integration findings + routed items; never silent patches)

**CF1 — the crew re-rank seam did not exist (routed, not patched).** The 18.25 contract
requires per-generation real-path re-ranks whose recordings are the first dual-stamped
crew recordings, with `realpath-rerank` rankings, native leg-logs, resume, and tranche
claims; `training/realpath.py` at e2a040b supports none of it for crew families
(`RealPathCandidate` whitelists impostor encoders only; `_build_agent_factory` never
dispatches to the crew builder; no opponent seam; `_verify_stamps` reads the impostor
stamp only). The only committed dual-stamp recorder (`run_tournament.py --crew-artifact`)
produces no ranking/leg-log/resume/tranche machinery. Routed as Task 18.32 (owner
ruling 2026-07-28: Amend + overlap — fake-path evolution proceeds, real legs wait).

<!-- SESSION-FINDINGS: extended as they land -->

## 8. Ranked shortlist for 18.26 — PENDING (a screen, not a verdict)

## 9. Reproduce — PENDING (harnesses + manifest census at close)

## 10. How downstream consumes this — PENDING

## 12. Errata — (none yet)
