# Adversarial Goodhart probe — the 18.18 conviction-path re-probe (probe design Task 15.14; conviction arms Task 18.18)

**Why this re-run exists:** the training-signal role GREW at Task 18.16 — the
GO-shipped conviction fitness term (`ConvictionFitnessTerm`, weight 0.5, in
BOTH sides' inner fitness) and the gating referee pre-screen
(`conviction_prescreen`) — and the standing rule binds: the probe re-runs
BEFORE any campaign selection leans on the new signal. This run also
discharges the carried §6 obligation of `audits/audit-phase-17-close.md`: the
4p1i `d4-contest-farming` exploit (+61.8%, recorded at 17.15) is re-probed at
the current substrate BEFORE any 4p1i-scored selection.
**Subject under attack:** the committed champion-SELECTION referee
(`eval/watchability.py::compute_watchability`, baseline-6 floors — the 18.12
pins, adopted at 18.14) AND, new at this run, the committed 18.16
training-signal integration: the conviction term as `inner_episode_fitness`
pays it, and the composed gate (`conviction_prescreen`'s predicted floors)
beside the recorded supply floors.
**Method:** the standing 15.14 machinery UNCHANGED (the shared ES core run
directly on the composed referee + the forced single-tactic reachability
sweep, everything decomposed), wrapped by the new conviction-path arms
(`training/bakeoff/goodhart.py::run_conviction_path_probe`): per forced lever
(plus the scripted-FSM baseline and the ES champion corner) the arms re-roll
the same K seeds — the env is a pure function of the seed, so the bytes are
identical to the set the standing bars scored — and read the conviction TERM
(a prediction) beside the recorded REALITY (flags in bytes, the conviction
table's mirrored labels), the task hint's narrow question. Every prediction
runs through the committed 18.16 consumption paths
(`ConvictionFitnessTerm.predict_meeting` + `conviction_prescreen`), metered on
ONE shared sha-keyed `ConvictionUseCounter`.
**Anchors:** `GOODHART_9P2I_BASELINE` (`training/bakeoff/harness.py`, baseline-6
re-confirm at 18.14) — reproduced below, digest-verified; the carried §6
numbers (17.15) — consumed as committed pins, never re-measured.
**Scoping:** fake-provider meetings throughout (this task's substrate; the
surrogate leg stays governed by its own standing cadence — the arms accept the
same `meeting_runner_factory` seam). This task edits NEITHER instrument it
attacks: `training/conviction/` and `training/bakeoff/harness.py` are consumed
through their public seams; every guard below is routed to the 18.24 protocol.

> The baseline-5 standing report this file extends (Task 17.15: the
> re-grounded-surrogate re-run + the original carried-finding record) is
> retained in git history at `7b54078`; its fake-provider numbers reproduce
> here unchanged (substrate-independent, as the 18.14 re-confirm documented).

---

## Verdict

| Roster | Standing probe (15.14 bars) | Conviction-term channel | Composed gate (pre-screen vs recorded floors) | Composed 18.18 verdict |
|---|---|---|---|---|
| **9p2i** (campaign roster) | **HELD** — baseline 3.28, ES champion 3.70 (+12.98%), strongest reachable 3.70 (`report`), reproduces the 17.11/18.14 anchor digest-for-digest | **HELD** — no lever lifts predicted supply above the bar (max `emergency` +4.9%); the term PENALIZES the strongest levers (see reading) | **SUBSTRATE-DIVERGENT** — predicted floors PASS for the honest baseline AND `emergency` while recorded floors FAIL; no lever flips the gate | **EXPLOITS_FOUND** (1 consumption-hazard blocker, no score-channel exploit) |
| **4p1i** (reference roster) | **EXPLOITS-FOUND** — the carried `d4-contest-farming` corner REPRODUCES: 0.85 → 1.38 (+61.8%), digest-identical to 17.15 | **EXPLOITS-FOUND** — `emergency` +205.6% and `kill` +25.7% predicted supply with recorded flags 0.0000 → 0.0000: the term pays fitness for evidence never minted | clean (nothing passes the 9p2i-pinned predicted floors; recorded floors also fail — no divergence) | **EXPLOITS_FOUND** (3 blockers) |

Materiality bar (all channels, the probe's UNCHANGED delta convention):
relative gain over the scripted-FSM baseline **≥ 25%**, validity-gated.
`baseline_id = "baseline-6"` everywhere. Composed verdicts compose over NAMED
blockers — the 9p2i EXPLOITS_FOUND is carried by a consumption-hazard blocker
alone (the composed-gate divergence below), NOT by any lever moving a score
channel above the bar or flipping the recorded gate; the standing 9p2i verdict
is HELD and reproduces the anchor.

**Headline.** The conviction term is attackable exactly where the referee
already was, and nowhere new on the campaign roster: on 9p2i no forced lever
launders predicted supply into fitness (the term would in fact pull AGAINST
the strongest geomean corners), but on the short 4p1i roster the SAME
meeting-farming corner that farms the D4 contest term also farms the
conviction term — the carried exploit now has a conviction-path twin. And the
composed gate has a substrate seam the honest baseline itself exposes: the
pre-screen predicts the REAL-path supply economy it was fit on, so on any
substrate whose meetings mint no flags its PASS is spend advice, never a
recorded-floor read.

---

## Budget + the consumption discipline (stated honestly)

- **Standing probe, both rosters:** the committed 15.14 shape — `generations=6`,
  `population=6`, σ = 0.5, `seed = 0`, `init_scale = 0.5`, K-seed average over
  seeds 0–7; `1 + 6×6 = 37` genome evaluations + 5 forced levers + the FSM
  baseline ≈ 344 games/roster. Genome = the packet-only tactic-MLP, length 66.
- **Conviction arms, both rosters:** 7 policy re-rolls × 8 seeds = 56
  games/roster (byte-identical re-rolls of already-scored sets) + one
  conviction-table walk per policy.
- **Conviction-model consumption (the metered quote):** **452 predicted
  meetings** against the committed cap of **52,481** (**0.86%**), through ONE
  shared sha-keyed counter (`4841f8e02eb7…`) spanning both rosters — 350 on
  9p2i (175 recorded meetings × 2 committed consumption paths: the
  fitness-term read and the pre-screen read), 102 on 4p1i (51 × 2). No
  prediction ran unmetered; the report's JSON quotes the counter alongside the
  cap (`conviction_uses` / `conviction_uses_total` / `conviction_max_uses`).
- Wall-clock 237 s, $0, offline (fake provider; frozen committed artifacts).

---

## 9p2i — the campaign roster: term HELD, gate substrate-divergent

**The standing bars reproduce the anchor exactly** — verdict HELD, champion
trace `3.28 → 3.70 → … → 3.70` (one gen-1 D1 improvement, decomposed), sweep
row-for-row identical to the 18.14 re-confirm, ES-core digest
`a7c5ea590233f0735571cf6960fbdf1567bdbb2575e0d27bfba995f08d235c14` = the
pinned `GOODHART_9P2I_BASELINE` digest. The conviction arms changed NOTHING in
the standing probe's objective or trace — the arms ride beside it.

### The conviction-term delta per forced lever, beside the standing bars

Fitness-channel convention: per-episode mean predicted supply, K-seed
averaged — EXACTLY what `inner_episode_fitness` pays (`weight 0.5 ×` the
episode's `mean_predicted_supply`; a no-meeting episode contributes 0.0).
"Recorded" = the conviction table's `flags_minted` labels mirrored from the
replay bytes.

| Policy | `mean_score` (standing bar) | meetings | predicted supply (episode mean) | recorded flags (episode mean) | term (0.5 × supply) | term Δ vs FSM | predicted-supply gain | launders? |
|---|---|---|---|---|---|---|---|---|
| scripted FSM (anchor) | 3.28 | 29 | **1.9389** | **0.0000** | +0.9695 | — | — | — |
| `emergency` | 2.85 | 44 | 2.0335 | 0.0000 | +1.0168 | **+0.0473** | +4.9% | no (below bar) |
| `report` | 3.70 | 32 | 0.9942 | 0.0000 | +0.4971 | −0.4723 | −48.7% | no |
| `wait` | 0.10 | 0 | 0.0000 | 0.0000 | 0.0000 | −0.9695 | −100% | no (validity FAIL) |
| `kill` | 3.64 | 24 | 1.2470 | 0.0000 | +0.6235 | −0.3460 | −35.7% | no |
| `sabotage` | 0.65 | 14 | 1.1714 | 0.0000 | +0.5857 | −0.3838 | −39.6% | no |
| ES champion | 3.70 | 32 | 1.0517 | 0.0000 | +0.5259 | −0.4436 | −45.8% | no |

- **No 9p2i lever launders predicted supply into fitness.** The honest FSM
  baseline already plays evidence-rich 9p2i games (≈3.6 meetings/game, real
  kill/vent pins in the packet stream), so its predicted supply is high
  (1.94/episode) and the farming corner adds only +4.9% — far below the bar.
  Every OTHER lever, and the ES champion (the `report` corner), REDUCES
  predicted supply: had the conviction term been in this objective, it would
  have pulled 0.35–0.48 fitness units AGAINST the strongest geomean corners.
  Stated as an observation on the term's gradient direction, not a safety
  claim — the probe did not optimize the composed inner fitness (the standing
  probe attacks the SELECTION referee; the term rides the training fitness,
  and its 18.24 exposure is priced by the blocker section below).
- **Predicted vs actual conversion, side by side:** the baseline's conversion
  head calls 79.3% of meetings converting (mean p = 0.732) while the recorded
  bytes convert 0.0% — same story on every lever. This is the same divergence
  as the flags channel and feeds the gate seam below.

### The composed-gate check — SUBSTRATE-DIVERGENT, named, not lever laundering

The committed pre-screen (baseline-6 9p2i pins: flags ≥ 180/165 ≈ 1.0909
per meeting, conversion pin 78/165, floor derived population-relative from
the PREDICTED flags density) **PASSES the honest scripted baseline**
(predicted 1.9967 flags/meeting, converting share 0.793) **and the
`emergency` lever** (2.0841, 0.545) — while the recorded floors FAIL every
9p2i set (fake meetings mint zero flags in bytes: `flags_per_meeting`
measured 0.0 vs floor 1.0909; conversion None vs the maximal derived 1.0).
By the standing baseline-relative gate convention this is **NOT laundering**
— no lever flips a gate the honest baseline fails; it is the model
faithfully predicting the REAL-path supply economy it was fit on (the 18.15
GO verdict measured it there) on a substrate that structurally cannot mint
those flags. `report`, `kill`, `sabotage` and the champion drop predicted
supply below the pins and predicted-FAIL (no false-blocks: their recorded
floors fail too).

**The named blocker (consumption hazard, flagged regardless of magnitude —
the standing gate-flip convention):**
`prescreen-substrate-divergence[fsm-baseline+emergency,9p2i]` — a pre-screen
PASS is real-path spend advice ONLY; the 18.24 protocol must never consume it
as a recorded-floor read on any substrate whose meetings cannot mint flags
(fake path today; any future decision-degenerate surrogate equally), and must
pair every gating use with a recorded-bytes floor read.

---

## 4p1i — the reference roster: the carried exploit reproduces, and it has a conviction twin

**The carried `d4-contest-farming` re-read (the §6 obligation), with its
materiality arithmetic:**

> carried (17.15, baseline-5 floors): mean_score 0.85 → 1.38 (**+61.8%**);
> re-read (baseline-6 substrate, conviction path live): 0.85 → 1.38
> (**+61.8%** vs the 25% bar) — byte-identical reproduction, ES-core digest
> `5351db5ee8d1b3625655fa68f818738a51d526fe1afdcddfdeb5e8651cceb630` = the
> 17.15 record. Moving term d4 (mechanism `d4-contest-farming`): mean
> meetings/game 1.00 → 1.75 lifts the contest term `min(1,(n−1)/2)` with no
> added deduction. **The carried exploit REPRODUCES above the bar — the
> blocker stands: no 4p1i-scored selection before the routed D4 contest floor
> lands.**

The substrate-independence claim of the 18.14 re-confirm held exactly: the
baseline-6 floors change no `mean_score`, so the whole 4p1i sweep
(`emergency` 1.38, `report` 0.70, `wait` 0.10/validity-FAIL, `kill` 0.55,
`sabotage` 0.40) and the champion trace (`0.70 → 0.85 → … → 0.85`)
reproduce the 17.15 rows to the digit.

### The conviction-term delta per forced lever — TWO levers launder

| Policy | `mean_score` (standing bar) | meetings | predicted supply (episode mean) | recorded flags (episode mean) | term (0.5 × supply) | term Δ vs FSM | predicted-supply gain | launders? |
|---|---|---|---|---|---|---|---|---|
| scripted FSM (anchor) | 0.85 | 8 | **0.0772** | **0.0000** | +0.0386 | — | — | — |
| **`emergency`** | **1.38** | 14 | **0.2360** | **0.0000** | +0.1180 | **+0.0794** | **+205.6%** | **YES** |
| `report` | 0.70 | 8 | −0.0875 | 0.0000 | −0.0437 | −0.0824 | −213.3% | no |
| `wait` | 0.10 | 0 | 0.0000 | 0.0000 | 0.0000 | −0.0386 | −100% | no (validity FAIL) |
| **`kill`** | 0.55 | 7 | **0.0971** | **0.0000** | +0.0485 | **+0.0099** | **+25.7%** | **YES** |
| `sabotage` | 0.40 | 6 | 0.0253 | 0.0000 | +0.0127 | −0.0259 | −67.2% | no |
| ES champion | 0.85 | 8 | 0.0772 | 0.0000 | +0.0386 | +0.0000 | +0.0% | no |

- **`conviction-supply-laundering[emergency,4p1i]`** — the materiality
  arithmetic: predicted supply (episode mean) 0.0772 → 0.2360 (**+205.6%** vs
  the 25% bar); recorded flags (episode mean) 0.0000 → 0.0000 (+0.0%); term
  delta **+0.0794** inner-fitness units at the committed weight 0.5. The SAME
  impostor-called-emergency corner that farms the D4 contest term farms the
  conviction term: farmed meetings multiply prediction opportunities over
  suspicion-bearing states, and the term pays for predicted flags the fake
  meetings never mint. The carried exploit's conviction twin.
- **`conviction-supply-laundering[kill,4p1i]`** — predicted supply 0.0772 →
  0.0971 (**+25.7%**, just above the bar); recorded flags 0.0000 → 0.0000;
  term delta +0.0099. Small in absolute fitness units (the short roster's
  supply is thin) but above the stated bar by the stated convention, so it is
  named, not silently waved off: kill-aggression mints real witnessed-kill
  pins in the packet stream, the model honestly predicts flags from them, and
  the substrate never delivers.
- **Why 9p2i is immune where 4p1i is not — the same headroom asymmetry as the
  D4 exploit:** the 9p2i baseline already saturates the evidence-supply
  features (predicted 1.94/episode), so farming adds 5%; the 4p1i baseline
  runs near the model's floor (0.0772), so the same behavioral corner is a
  3× relative move. The exploit lives on the SHORT roster, exactly like the
  carried one.
- **The composed gate on 4p1i is clean but diagnostic-only:** the committed
  pre-screen is pinned to the 9p2i baseline-6 floors (there is no other
  committed pre-screen), which reject every 4p1i set's predicted supply — and
  the recorded floors fail too, so neither laundering nor false-blocks. A
  4p1i gate read probes the instrument as shipped, nothing more.

---

## Blockers for the 18.24 protocol (named, never silent caveats)

1. **`d4-contest-farming[4p1i]`** (standing probe, carried from 17.15,
   re-confirmed here): mean_score 0.85 → 1.38 (+61.8%, above the 25% bar).
   No 4p1i-scored selection until the routed D4 contest floor lands
   (`eval/watchability.py` is the PAUSE's to patch, never this probe's).
2. **`conviction-supply-laundering[emergency,4p1i]`**: predicted supply
   +205.6% with recorded flags 0.0000 → 0.0000; term delta +0.0794 at weight
   0.5. 18.24 must not run conviction-weighted fitness on the 4p1i roster —
   and on ANY roster must condition (or cap) the term's credit for
   meeting-count-multiplying play on recorded-bytes confirmation before
   selection leans on it.
3. **`conviction-supply-laundering[kill,4p1i]`**: predicted supply +25.7%
   (bar-clearing) with recorded flags 0.0000 → 0.0000; term delta +0.0099.
   Same guard as (2); named separately because the mechanism differs
   (real witnessed-kill pins honestly predicted, never substrate-delivered —
   a prediction-vs-substrate gap, not feature farming).
4. **`prescreen-substrate-divergence[fsm-baseline+emergency,9p2i]`**: the
   committed pre-screen's predicted floors PASS (honest baseline included)
   while the recorded floors FAIL on the fake substrate. A pre-screen PASS is
   real-path spend advice ONLY — 18.24 must pair every gating use with a
   recorded-bytes floor read and must never let the pre-screen verdict stand
   in for the recorded referee on a flag-mintless substrate.

What is NOT blocked, stated plainly: 9p2i champion selection through the
composed recorded referee — the standing 9p2i verdict is HELD, reproduces the
anchor, no genome clears the recorded gate (`referee_passed = False`
everywhere), and no 9p2i lever moves the conviction term above the bar.

---

## What this re-probe does and does not clear

- The forced-lever net and the ES ran on the fake-provider substrate; the
  meeting-DECIDED terms and floors stay structurally unreachable there, so
  every null on them is a scoping statement, not "referee safe" (the standing
  15.15 obligation text travels in the report JSON unchanged).
- The conviction model's OWN fidelity is not re-judged here (that is the
  18.15 verdict's single pre-registered evaluation); this probe measures what
  an adversarial TACTICAL policy can extract from the term and the gate as
  committed. The real-LLM path remains unprobed (the pause audit §11
  limitation stands).
- The arms accept the probe's `meeting_runner_factory` seam, so the surrogate
  leg of THIS composed probe can be discharged through the same entry point
  when the standing surrogate cadence next binds; nothing here pre-discharges
  it.

---

## Reproduce

```python
from pathlib import Path

from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import (
    reread_carried_4p1i_exploit,
    run_conviction_path_probe,
)
from training.conviction.model import (
    ConvictionUseCounter,
    load_conviction_staleness_cap,
)

cfg = ESConfig(generations=6, population=6, sigma=0.5, seed=0,
               fitness_seeds=tuple(range(8)), init_scale=0.5)
# ONE shared counter across both rosters (the threading discipline).
counter = ConvictionUseCounter(
    load_conviction_staleness_cap(Path("training/artifacts/conviction"))
)
# 9p2i (standing HELD — reproduces GOODHART_9P2I_BASELINE — + the arms):
r9 = run_conviction_path_probe(config=cfg, num_players=9, num_impostors=2,
                               tasks_per_crewmate=2, materiality_bar=0.25,
                               use_counter=counter)
# 4p1i (EXPLOITS-FOUND + the carried re-read):
r4 = run_conviction_path_probe(config=cfg, num_players=4, num_impostors=1,
                               tasks_per_crewmate=1, materiality_bar=0.25,
                               use_counter=counter)
print(reread_carried_4p1i_exploit(r4).verdict)
```

Deterministic under `config.seed` (env + referee + the frozen conviction
weights are pure functions of the seed). ES-core digests at this tree: 9p2i
`a7c5ea590233f0735571cf6960fbdf1567bdbb2575e0d27bfba995f08d235c14` (= the
pinned anchor), 4p1i
`5351db5ee8d1b3625655fa68f818738a51d526fe1afdcddfdeb5e8651cceb630` (= the
17.15 record); the six `GOODHART_9P2I_BASELINE` values and both sweeps
reproduce row-for-row (the digests are exact-float genome hashes and carry
the documented origin-platform ULP caveat). Conviction artifact
`4841f8e02eb7b587237c5b88bc2d350c12c7a5b5ac5c7ae1481069235c7b2a47`, verdict
GO, weight 0.5, threshold 0.5; counter total after both rosters: 452 of
52,481.
