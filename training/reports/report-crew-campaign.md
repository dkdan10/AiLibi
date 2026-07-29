# The crew campaign — the counter-adaptation half of the phase's co-evolution (Task 18.25, operator, multi-session)

**Task:** 18.25 — THE CREW CAMPAIGN (operator, multi-session, ~30–40h real-path legs)
**Machinery consumed (frozen, never edited here):** training/coevo/driver.py (18.19/18.20/18.21/18.31), training/crew/ (15.16/15.22), training/realpath.py (18.17/18.31 + the 18.32 crew re-rank arm), scripts/generate_campaign_tables.py (18.31), scripts/run_tournament.py --crew-artifact (18.19)
**Section refs:** the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)
**Date started:** 2026-07-28
**Last evidence recorded:** 2026-07-29 (session 2 close — all four legs + sweeps recorded)
**Status:** COMPLETE — fake path 2 runs + 2 ablation twins; real path 4 legs / 36 games, STOPPED by the §4.0 F12 ruling after the pre-registered two-tranche core (~8.7 h wall-clock vs the ~30–40 h envelope — duration honesty: the envelope was deliberately NOT spent at a noise level that cannot support the verdicts it would buy; the two-leg rolling posture ran throughout, zero retry exhaustion, no degrade).

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
| 2 | 2026-07-28 | 18.32 merged (088d4c2, #315) + coordination a752f85; leg pair 1 launched (c1-t1 + c2-t1, tranche 4000–4002, two-leg runbook, vs ea4bc955) | §4; `provenance/session2-leg-c1-t1.log`, `…-c2-t1.log` (committed at leg close) |
| 2 (cont., 2026-07-28→29) | overnight | Rolling-pair posture ratified; all four legs recorded (36 games); F12 stability RULED (stop after c1 legs); ablation twin pair; report close | §4.0–§4.4, §6; provenance/session2-leg-*.log; commits 4339a23…e96e352 |

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

### 3.6 Cross-run readings

The two bases separate on the fake path and the separation SURVIVES the real path at
the lineage level: the owned-task (c1) crew is meeting-rich (conviction 3021 uses; all
real-path arms validity-PASS both tranches) and its impostor opponent plateaus; the
general (c2) crew is meeting-scarce (635 uses, 0 at gen-1; gen-0 starves outright on
the real path) and its impostor opponent keeps improving. The 17.13 cell — does the
citation-era conviction channel move an owned-task crew's pace advantage into WINS —
answers from the campaign's real re-rank data: **NOT RESOLVABLE at this budget, and
the structural half is answered.** The owned-task crew reliably reaches the meeting/
conviction economy against the frozen champion (every arm, every tranche — the pace
advantage converts into meetings, flags above floor, and occasional accurate
ejections), but win conversion swings a full game per arm between tranches (§4.4), so
whether the conviction channel moves WINS is exactly 18.26's 50-seed question. The
ablation pair (§6) adds the mechanism: the term's selection effect is real and
crew-side on both bases, with a base-dependent locus.

## 4.0 MEASUREMENT RELIABILITY — read this before any §4 number

**Every real-path read in this report is a SCREEN, not a verdict.** Computed via
`generate_campaign_tables.py stability` immediately after the FIRST retested candidates
(the c2 slate, both tranches — the F12 precondition honored at hour ~1 of legs, not
hour 40):

| stability check — **2 ARMS** (2 distinct genomes) recorded on both tranches | value |
|---|---|
| mean absolute swing in `flags_per_meeting` between tranches | **2.0000** |
| the floor that quantity is tested against | 1.0909 |
| **noise as a fraction of the threshold** | **183%** |
| arms whose derived conversion floor saturated at 1.000 on ≥1 tranche | **2 of 2** |
| mean absolute win-rate swing, in games | 0.00 |
| arms swinging ≥ 1 game in win rate between tranches | **0 of 2** |
| referee PASSes recorded / retested / replicated | **2 / 2 / 0** |

Machine-readable: `realpath-crew/run-c2-crew-general/measurement-stability-c2.json`.
Input provenance (disclosed): the committed rankings include the gen-0 arm, which
recorded ZERO meetings on tranche 1 — an unmeasured `flags_per_meeting` gauge the
stability tool refuses outright (CF3); the read above runs over the two arms measured
on BOTH tranches, via derived input copies at `stability-inputs-filtered/` (gen-0 row
dropped, ranks re-indexed contiguously, no measured value altered). The native
exclusion-with-reporting fix is routed, never hand-patched (CF3).

**Consequence (the F12 ruling, session 2):** 183% ≫ the 25% precondition. Both t1
referee PASSes failed to replicate on fresh seeds — the 18.24 `f280962f…` lesson
reproduced exactly. At the 3-seed tranche budget, referee/flags verdicts are NOT
resolvable for this campaign. Disposition: the two in-flight c1 legs complete the
pre-registered two-tranche core (their arms need the retest for the c1-side stability
row), then real-path spend STOPS — no gen-champion legs, no additional n=3 comparator
legs (the committed 18.24 back-fill rows already carry the ea4bc955-vs-FSM cell) —
and verdict-grade depth routes to 18.26's 50-seed protocol with its pre-registered
UNRESOLVABLE third outcome. Duration honesty: the ~30–40 h leg envelope the contract
priced is deliberately NOT spent at a noise level that cannot support the verdicts it
would buy.

## 4. Real-path re-rank legs (18.17/18.31/18.32 machinery; 17.14 table discipline)

The 18.32 crew re-rank arm merged 088d4c2 (#315) and unblocked this section (routed
session 1 as CF1; the Amend + overlap ruling). Leg protocol as run:

**Leg pair 1 (session 2, tranche 4000–4002, two legs concurrent per the runbook —
different work_dirs, staggered starts with 60–120 s jitter, each leg internally
sequential, `meeting_timeout_seconds=900`):**

- `leg-c1-t1` — run-c1 slate vs the frozen opponent `ea4bc955…` (the 18.24 champion
  artifact, loaded + sha-verified before any spend through the 18.32 seam):
  `c1-gen0-owned-tasks-es` (the committed pre-campaign champion — the counter-adaptation
  CONTROL), `c1-swap0-champ-gen3` (`72adb41c…`), `c1-swap2-champ-gen9` (`0bf179b7…`).
- `leg-c2-t1` — run-c2 slate vs the same opponent: `c2-gen0-utility-es` (control),
  `c2-swap0-champ-gen3` (`7fa59718…`), `c2-swap2-champ-gen9` (`515fc066…`).

The trained-vs-gen-0 delta against the SAME frozen opponent is the counter-adaptation
cell; the FSM-opponent comparator legs (opponent None) follow the stability read.

**Posture amendment (session 2, owner discussion):** the two-leg directive is run as a
ROLLING pair — when a leg finishes, the next protocol leg launches immediately rather
than waiting for its pair-mate (leg-c2-t2 launched beside the still-recording leg-c1-t1
the moment this was ratified). Rationale: the F7 constraint was never overlap
correctness (per-element replays, no cross-game state, no real-path byte-determinism
claim) but provider throughput + the library's leg-owns-its-tranche recording model; a
lone meeting-rich game leaves plan capacity idle during its sequential meeting phases,
which a second in-flight leg soaks. True element-level work-stealing (two workers
pulling seeds from ONE leg) needs a record/score split the tranche flock exists to
refuse today — routed to 18.28's deferred ledger as a next-campaign ergonomics item,
never a mid-campaign amendment (the 3-seed tranche shape is F12-load-bearing).
Pre-screen: none rides these legs — the slate ordering is protocol-fixed (gen-0 control
+ lineage swap champions), not conviction-influenced, so blocker-4's pairing obligation
does not bind; the native `leg-log.jsonl` is the ordering evidence (Decision, session 2).
These recordings are the FIRST dual-stamped crew recordings (18.7/18.19 live exercise);
rows carry schema `realpath-rerank-v3` with crew-stamp read-back proofs. Tranche 2
(4003–4005) re-runs both slates for the F12 stability read before any further spend.

### 4.1 leg-c2-t1 (session 2 — COMPLETE, 9 games, tranche 4000–4002, vs `ea4bc955…`)

Table generated by `generate_campaign_tables.py legs` over the committed
`realpath-crew/run-c2-crew-general/ranking-4000-4002.jsonl` (schema `realpath-rerank-v3`;
every game dual-stamp verified — the first dual-stamped crew recordings):

| rank | candidate | selection | validity | referee | win | ejection acc | stamp proof |
|---|---|---|---|---|---|---|---|
| 1 | `888046d0…` gen0 | -1.00 | FAIL | FAIL | 1.000 | None | 3/3 games stamped, uniform, sha == computed digest |
| 2 | `7fa59718…` gen3 | -1.00 | FAIL | PASS | 1.000 | 1.000 | 3/3 games stamped, uniform, sha == computed digest |
| 3 | `515fc066…` gen9 | -1.00 | FAIL | PASS | 1.000 | 1.000 | 3/3 games stamped, uniform, sha == computed digest |

Floor sensitivity (signed, from the generator): gen-0 `flags_per_meeting` /
`conversion` denominator-empty (zero meetings); both trained arms
`flags_per_meeting 2.0000 − 1.0909 = +0.9091 PASS`, conversion `+0.1872` / `+0.6872`
PASS, witnessed-event-rate PASS all three.

**Reading (n=3 per arm — a SCREEN, per §4.0 discipline; the stability table rules).**
Every c2 arm fails validity on `meeting_rate` (floor 0.60): gen-0 recorded ZERO meetings
in 3 games (its second failure, no-model-on-cost-rows, is the cascade — no meetings, no
LLM calls); both trained champions recorded exactly one meeting each (0.33), and in that
meeting supplied 2.0 flags (above floor), converted testimony, and ejected an impostor
(accuracy 1.000, referee PASS). The impostor champion swept 9/9 wins. Isolation: the
committed 18.24 back-fill rows show `ea4bc955…` vs SCRIPTED crew on the SAME seeds at
`meeting_rate 1.0` (win also 1.0) — so the meeting scarcity is crew-side and
lineage-wide, not champion kill-speed, and no crew (learned or scripted) closes this
champion's win edge on these 3 seeds. Direction of the counter-adaptation signal:
training under the conviction term moved the general base from fully starved (0.0) to
0.33 meeting rate with above-floor per-meeting supply and accurate convictions — the
conviction-economy gradient is visibly pulling even the unguarded v1 base toward
evidence play — but not past the validity floor. Gate-validity discipline outcome: NO
c2 arm survives selection at this tranche (selection −1.0 sentinel), exactly as the
starvation-family exclusion demands.

### 4.2 leg-c2-t2 (session 2 — COMPLETE, 9 games, tranche 4003–4005, vs `ea4bc955…`)

| rank | candidate | selection | validity | referee | win | ejection acc | stamp proof |
|---|---|---|---|---|---|---|---|
| 1 | `515fc066…` gen9 | 5.83 | PASS | FAIL | 1.000 | 1.000 | 3/3 games stamped, uniform, sha == computed digest |
| 2 | `7fa59718…` gen3 | 1.67 | PASS | FAIL | 1.000 | None | 3/3 games stamped, uniform, sha == computed digest |
| 3 | `888046d0…` gen0 | -1.00 | FAIL | FAIL | 0.667 | None | 3/3 games stamped, uniform, sha == computed digest |

**Reading.** The c2 retest that fed §4.0: both trained arms flip to validity PASS
(meeting rate cleared 0.60) while both of t1's referee PASSes fail to replicate, and
gen-0 wins a game it swept-lost on t1. Read jointly with §4.1 in CF2 — the
trained-vs-gen-0 meeting-rate delta persists across tranches; every per-meeting gauge
swings at full scale.

### 4.3 leg-c1-t1 (session 2 — COMPLETE, 9 games, tranche 4000–4002, vs `ea4bc955…`)

| rank | candidate | selection | validity | referee | win | ejection acc | stamp proof |
|---|---|---|---|---|---|---|---|
| 1 | `0bf179b7…` gen9 | 47.30 | PASS | FAIL | 0.667 | 0.571 | 3/3 games stamped, uniform, sha == computed digest |
| 2 | `bd6fdd0a…` gen0 | 25.73 | PASS | FAIL | 1.000 | 0.250 | 3/3 games stamped, uniform, sha == computed digest |
| 3 | `72adb41c…` gen3 | 24.40 | PASS | FAIL | 1.000 | 0.000 | 3/3 games stamped, uniform, sha == computed digest |

**Reading (n=3 — a SCREEN; §4.0 rules).** The counter-adaptation cell points the hoped
direction on every instrument simultaneously: the trained gen-9 champion ranks FIRST,
nearly doubles its gen-0 control's selection score (47.30 vs 25.73), lifts ejection
accuracy monotonically along the lineage where it matters (gen-0 0.250 → gen-9 0.571;
gen-3 sits at 0.000 — training time, not lineage age, is the gradient), and dents the
frozen champion's win edge by one game (0.667 vs the control's 1.000 sweep). ALL c1
arms pass validity — the owned-task lineage is meeting-rich everywhere the general
lineage starved (the 15.22 structural guard's fingerprint, per CF2). Honesty: a
one-game win dent is exactly the swing scale §4.0 measured as noise; whether gen-9's
edge dent replicates is what leg-c1-t2 retests, and verdict grade remains 18.26's.

### 4.4 leg-c1-t2 (session 2 — COMPLETE, 9 games, tranche 4003–4005, vs `ea4bc955…` — the campaign's FINAL real-path leg per the §4.0 ruling)

| rank | candidate | selection | validity | referee | win | ejection acc | stamp proof |
|---|---|---|---|---|---|---|---|
| 1 | `72adb41c…` gen3 | 58.13 | PASS | FAIL | 0.667 | — | 3/3 games stamped, uniform, sha == computed digest |
| 2 | `bd6fdd0a…` gen0 | 41.00 | PASS | FAIL | 0.667 | — | 3/3 games stamped, uniform, sha == computed digest |
| 3 | `0bf179b7…` gen9 | 32.10 | PASS | FAIL | 1.000 | — | 3/3 games stamped, uniform, sha == computed digest |

**Reading (the retest that disciplines §4.3).** Complete rank INVERSION vs tranche 1:
gen-3 — bottom-ranked on t1 with ejection accuracy 0.000 — wins the leg AND takes a
game off the champion; gen-0 takes a game too; gen-9's t1 win dent does not replicate
(0.667 → 1.000). Every per-arm ordering claim from §4.3 (the selection gap, the
ejection-accuracy "training gradient", the win dent) is inside the measured swing.
What survives the retest — the campaign's tranche-STABLE real-path results: every c1
arm passes validity on BOTH tranches (the owned-task lineage is structurally
meeting-rich under the frozen champion), zero referee passes campaign-wide, and the
c1-vs-c2 lineage contrast (§4.1/§4.2). The c1-side stability row
(`measurement-stability-c1.json`): flags noise 33% of threshold (vs c2's 183% — the
meeting-rich lineage measures more stably per meeting), but ALL 3 arms swung ≥ 1
win-game between tranches (mean 1.00 game), and 33% still exceeds the 25% F12
precondition — the §4.0 stop ruling stands on both slates.

<!-- all legs recorded -->

## 5. Emergence-instrument sweeps (18.1/18.2/18.3 over the campaign's real-path recordings)

Committed sweep JSONs beside each ranking (`sweep-<tranche>.json`, one entry per
candidate dir, the 18.24 shape byte-for-byte in key structure; recipe validated by
recomputing the corpus-9p2i baseline block at this tree — byte-identical to the block
every committed 18.24 sweep embeds). **Byte-completeness fence: PASS on all 12
candidate dirs** before any instrument read (every game GAME_OVER-stamped, every
state_hash verified) — every denominator below is trusted.

**Instrument scope on CREW arms (the honest read, stated before any cell):** these are
the tree's first learned-crew recordings, and two of the three shelf instruments are
impostor-arm instruments by construction. `off_menu` scores only impostor decisions —
the frozen champion is menu-bounded, so 0/119…0/203 on all 12 dirs is VACUOUS for the
crew claim (its own scope_note says as much). The `deception_instruments` cells fold
the frozen OPPONENT's speech/outcomes; the crew candidate enters only through eject
outcomes and deflection's survival half — and on c2 most denominators are 0–2
(absent-denominator, not low-rate). `kill_craft` is the one instrument that directly
reads the learned arm (crew-witnessed census, point-biserial, the CREWMATE entropy
cell). Routed note for coordination: 18.24's §5.1 prose says the off-menu
DISTRIBUTION is preserved in the committed sweeps, but every committed sweep drops
`off_menu_decisions` (the aggregates survive) — an 18.24 §12-errata-channel item,
recorded here, not silently fixed.

Key cells (from the committed sweep JSONs; n=3 games/arm — advisory scale, §4.0
applies; corpus anchor 9p2i baseline-6 in the right column):

| cell (c1 arms t1/t2 pooled range) | c1 owned-tasks | c2 general | corpus 9p2i |
|---|---|---|---|
| meetings per 3 games | 8–12 | **0–2** | ~9.3 |
| crew-witnessed kill rate | 0.154–0.357 | 0.188–0.308 | **0.024** |
| frame conversions | 0–2 per leg | 0 everywhere | 23/437 |
| teammate accusations | 0 everywhere | 0 everywhere | 0/549 |
| witnessed point-biserial (one hop) | 0.13–0.46 | 0.21–0.70 | 0.2585 |
| crew H(cond) | 0.80–0.93 | 0.58–0.90 | 0.8693 |
| off-menu rate | 0 (vacuous) | 0 (vacuous) | 0/6663 |

Largest movements, stated not ruled: **crew-witnessed kill rate runs an order of
magnitude above corpus on EVERY crew leg** — both arms confounded (learned crew
witnessing more vs the champion killing more brazenly against these crews than
candidates did against scripted crew) — a named 18.26 comparator question, not a
campaign ruling. And c2's meeting layer is nearly absent in raw bytes (verified: the
gen-0 games carry zero meeting rows), the §4.1/CF2 starvation read at the byte level.

<!-- all sweeps recorded -->

## 6. Counterfactual ablations (the 18.4-named discipline)

### 6.1 ablation:run-c2/conviction-term (session 2 — COMPLETE, 2574-game twin)

Config byte-identical to run-c2 (same `master_seed=182502`, same budgets/seeds) with
`conviction=None`. Committed twin: `training/artifacts/coevo/
ablation-run-c2-conviction-term/` (hall + `campaign-rows.jsonl` + `campaign-plan.json`)
+ `gen-champions/ablation-run-c2-conviction-term/`. Byte-level lineage diff (quoted from
committed artifacts):

| lineage point | run-c2 (term ON) | twin (term OFF) | verdict |
|---|---|---|---|
| crew gen-1/gen-2 champions | `888046d0…`, `bd7770af…` | identical | SAME |
| crew swap-0 champion (gen-3) | `7fa59718…` | `fc43ba4e…` | **DIVERGES** |
| crew swap-2 champion (gen-9) | `515fc066…` | `b07c2a3a…` | **DIVERGES** |
| every crew hall member gen ≥ 3 | — | — | **all differ** |
| impostor swap-1 champion (gens 4–6) | `1577942b…` | identical | SAME |
| impostor swap-3 champion (gen-12) | `105f7a88…` | `aa337c7e…` | **DIVERGES** |

**Reading.** The divergence onset is dose-aligned: run-c2's conviction meter served 0 /
1 / 24 uses across gens 1–3 (§3.2), and crew selection is sha-identical exactly while
the term is unserved (gens 1–2), diverging at the FIRST generation with real meeting
service (gen-3) and at every crew freeze after. The impostor lineage is initially
robust to the divergent crew opponent (swap-1 champion identical) and diverges only by
gen-12 — the term's selection-relevant effect is CREW-SIDE and propagates to the
impostor through co-evolution, extending 18.24's F6 (which found the same crew-side
locus from the impostor-first direction). Emergence-claim status per the 18.4 four-part
discipline: this is the counterfactual-ablation limb (c) — the enabling lever is
selection-relevant; but limb (a), the |z| ≥ 1.96 instrument delta on the real path, is
NOT satisfiable at this campaign's n=3 budget (§4.0), so the "conviction term produces
meeting-seeking crew" claim reads **NOT-DEMONSTRATED at this budget** with the ablation
direction recorded — the 18.26/50-seed protocol is the venue for the claim-grade read.

### 6.2 ablation:run-c1/conviction-term (session 2 — COMPLETE, 2432-game twin)

Config byte-identical to run-c1 (same `master_seed=182501`) with `conviction=None`.
Committed twin: `training/artifacts/coevo/ablation-run-c1-conviction-term/` +
`gen-champions/ablation-run-c1-conviction-term/`; twin digest `43570747…`. Lineage diff
(quoted from committed artifacts):

| lineage point | run-c1 (term ON) | twin (term OFF) | verdict |
|---|---|---|---|
| crew swap-0 champion (gen-3) | `72adb41c…` | identical | SAME |
| crew exploiter finds, gens 5–6 | **none passed the bar** | `d007fc37…`, `2530b11d…` | **DIVERGES** |
| impostor swap-1 champion (gen-6) | `0ca3a382…` | `7ddc3709…` | **DIVERGES** |
| crew swap-2 champion (gen-9) | `0bf179b7…` | `a0ab72e2…` | **DIVERGES** |

**Reading.** The complement of §6.1: on the meeting-RICH owned-task base (conviction
served from gen-1: 165/297/459 uses across swap 0), the crew's own first-swap selection
is term-INSENSITIVE — the supply addend did not reorder an already-meeting-seeking top.
The term's first selection-relevant effect is on the EXPLOITER channel: crew-side
exploiter probes climb `crew_inner_episode_fitness`, which carries the term when
configured, and with the term ON no crew exploiter cleared the freeze bar during the
impostor's swap while with it OFF two did — changing the impostor's opponent pool
mid-swap, diverging the impostor swap-1 champion, and cascading into a different crew
swap-2 champion. Paired reading of §6.1 + §6.2: the conviction term's selection effect
is crew-side in BOTH campaigns (F6 extended), but its locus depends on the base — it
reorders crew selection directly where meetings are scarce (v1) and acts through the
exploiter/opponent-pool channel where meetings are already rich (v2). Emergence-claim
status: same as §6.1 — ablation limb recorded, claim NOT-DEMONSTRATED at this budget.

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

**CF2 — the general-base lineage is meeting-scarce on the real path; the conviction
term moves it toward the evidence economy, and the effect is REAL but UNSTABLE at n=3.**
The fake path's watch (§3.2: conviction 635 uses, 0 at gen-1) predicted scarcity; the
real path measured it both ways: tranche 1 — gen-0 zero meetings, trained arms 0.33
meeting rate with 2.0 flags/meeting and a correct ejection each, ALL arms validity-FAIL;
tranche 2 — both trained arms validity-PASS (meeting rate cleared 0.60; selection 5.83 /
1.67) with 0.0 measured flags, gen-0 still validity-FAIL but winning a game (0.667
impostor win). The trained-vs-gen-0 meeting-rate delta persists across BOTH tranches
(the counter-adaptation direction is consistent); every per-meeting gauge swings at
full scale (§4.0). The 15.22 structural guard exists only on the owned-task basis —
v1's meeting scarcity is the measured cost of its absence. Selection consequence:
no c2 arm survives this campaign's selection bars at n=3; whether the trained arms'
validity-passing behavior is real is exactly a 50-seed (18.26) question.

**CF3 — the stability instrument refuses the crew campaign's data shapes (routed, not
patched).** Two guards, both correct for 18.24's corpus, both tripped by crew data:
(a) a zero-meeting arm has an unmeasured `flags_per_meeting`, and the tool refuses the
ENTIRE read rather than reporting the arm as unmeasured-on-a-tranche; (b) a
derived input set with a dropped arm trips the contiguous-rank total-order guard.
Session-2 workaround: disclosed derived copies (§4.0). The routed fix is native
exclusion-with-reporting in `generate_campaign_tables.py stability` (an
`arms_unmeasured_on_a_tranche` count beside the swing means) — 18.28's deferred
ledger, alongside the record/score-split ergonomics item (§4 posture amendment).

**CF4 — `training/artifacts/coevo/realpath/` is a RESERVED namespace (found by the
gates, fixed by relocation, routed as a maintenance note).** `DEFAULT_RANKING_ROOTS`
folds the whole `realpath/` tree, and the committed 18.24 `measurement-stability.json`
is byte-pinned over a default-roots recomputation — so ANY new ranking landing under
`realpath/` silently changes (or, with a zero-meeting arm, hard-refuses) the pinned
reproduction: 15 test failures at this campaign's gate run. Fix: 18.25's rankings live
under `training/artifacts/coevo/realpath-crew/` (PATHS.md updated); the general rule —
a future campaign takes a SIBLING root, never a subdir of a default root. Routed note
(the 18.31 hand-maintained-list residual class, for 18.28's ledger):
`DEFAULT_RANKING_ROOTS`, like `WORK_DIR_OWNED_NAMES`, is a hand-maintained namespace
list whose collision class re-opens with every new campaign.

<!-- SESSION-FINDINGS: extended as they land -->

## 8. Hand-off to 18.26 (a screen, not a verdict — and deliberately NOT a ranked shortlist)

**No crew finalist clears the bars from this campaign's evidence, and no per-arm
ordering survives its own retest (§4.4), so this section names CANDIDATES with their
tranche-stable properties instead of ranking them** — a ranked list would launder §4.0
noise into a hand-off. If 18.26 takes crew arms (owner-justified slots per its
contract), the campaign's four named candidates, all F14-verified through
`--crew-artifact` at hand-off (session 2):

| candidate | artifact (crew hall) | tranche-stable evidence |
|---|---|---|
| `0bf179b7…` c1 gen-9 | `run-c1-crew-owned-tasks/crew/gen-9/…` | validity PASS ×2; won its t1 leg; the most-trained owned-task champion |
| `72adb41c…` c1 gen-3 | `run-c1-crew-owned-tasks/crew/gen-3/…` | validity PASS ×2; won its t2 leg with a game off the champion |
| `515fc066…` c2 gen-9 | `run-c2-crew-general/crew/gen-9/…` | validity 1/2 tranches; the strongest general-base arm; carries the CF2 starvation watch |
| `7fa59718…` c2 gen-3 | `run-c2-crew-general/crew/gen-3/…` | validity 1/2 tranches; carries the CF2 watch |
| (control) `bd6fdd0a…` gen-0 owned-tasks | training/artifacts/crew/crew-owned-tasks-es (3-file measurement tier — loads via the 18.7 learned-crew factory, NOT `--crew-artifact`) | the counter-adaptation control; validity PASS ×2 |

The dual-stamped crew-vs-champion cell 18.26's contract pre-registers is exactly what
these recordings piloted; the campaign's protocol recommendation to 18.26: pair every
crew arm with the same-seed gen-0 control, and read win conversion only at n=50.

## 9. Reproduce

Fake path (deterministic under `master_seed` on the recording platform, macOS; the
row pins assert structure, never floats): the two run harnesses + two ablation twins
are §1.3/§1.6/§6 configs applied to the 18.24 §9 snippet shape — `first_side="crew"`,
`run_label` set per run, fresh `ConvictionFitnessTerm` (or `None` for twins),
`hall_root=training/artifacts/coevo/<run>`, work_dir under the operator root
`/Users/danielkeinan/ailibi-campaign-1825/` (PATHS.md carries the prefix map).
Verification pins: `uv run pytest tests/training/test_coevo_driver.py -k
CommittedCrewCampaignRows`. Run digests: c1 `7a613696…`, c2 `7e682377…`, twin-c1
`43570747…`, twin-c2 (committed rows at `ablation-run-c2-conviction-term/`).

Real path (selection-only, non-deterministic): `AILIBI_LLM_PROVIDER=featherless
AILIBI_PROMPT_SET=qwen3_6_27b AILIBI_SEED_MAX_ATTEMPTS=8` + `FEATHERLESS_API_KEY`,
`run_realpath_rerank(..., config=RealPathRerankConfig(meeting_timeout_seconds=900.0),
opponent_artifact=<the ea4bc955 artifact dir>)` per leg (§4 slates; schema
`realpath-rerank-v3`). Every leg's `leg-log.jsonl` + `leg-<tranche>-<invocation>.json`
+ `prescreen` state are committed inside the mirrored `recordings-<tranche>/` dirs;
session chain logs at `training/artifacts/coevo/provenance/session2-leg-*.log`.
Verify every recordings manifest from a fresh checkout:

```bash
find training/artifacts/coevo/realpath/run-c[12]-* -name 'recordings-manifest*.sha256' -print0 | \
  xargs -0 -I{} sh -c 'cd "$(dirname {})" && shasum -a 256 -c "$(basename {})"'
```

## 10. How downstream consumes this

- **18.26** takes §8's candidates (owner-justified slots; adoption is NOT this task's
  call) and the §4/§4.0 lesson that every crew verdict needs the 50-seed protocol with
  the UNRESOLVABLE third outcome; the dual-stamped crew-vs-champion recording recipe is
  piloted here (the first dual-stamped crew recordings in the tree).
- **18.27** reads the emergence discipline outcome: the conviction-term claim carries
  its ablation limb (§6, both bases, dose-aligned + channel-resolved) and is
  NOT-DEMONSTRATED overall at this budget; F6's crew-side locus is extended, not
  contradicted.
- **18.28** inherits the deferred-ledger items: the record/score split (element-level
  leg concurrency, §4 posture amendment), the stability tool's zero-meeting-arm
  handling (CF3), and the standing 18.31 residuals.
- **Phase-19-facing**: CF2 (the v1 base without the 15.22 guard is starvation-family
  under a strong impostor) prices any future general-base crew work.

## 12. Errata — (none yet)
