# Adversarial Goodhart probe — red-teaming the selection referee (Task 15.14)

**Subject under attack:** the committed champion-SELECTION referee
(`eval/watchability.py::compute_watchability` — Task 15.2, with the baseline-3
evidence-supply floors from Task 15.7).
**Method:** run the shared ES core (`training/bakeoff/es.py`) DIRECTLY on the
COMPOSED referee — the deliberately-forbidden objective (the SELECTION-ONLY
DOCTRINE, `audits/post-phase-14-ML-training-signal.md` §3.2; the un-run charter
guardrail §7.1.9; `experiments/lab/ml-spike-charter.md` gap 3) — plus a systematic
single-tactic reachability sweep, and decompose everything that moves. The fitness
is the composed referee: `referee_passed` (the supply-floor gate AND integrity) is
a dominating bonus term, with the Layer-2 `mean_score` geomean as the tie-break
among the genomes that fail the gate — so the ES hunts for a genome that clears the
whole gate first, and only maximizes the geomean because (under fake meetings) none
can. It is NOT the geomean alone.
**Anchors:** `experiments/lab/ml_spike/fo3_rubric_goodhart.py` (the prior probe
shape); `audits/post-phase-14-ML-planning.md` §12.2 (reward-hacking guards).
**Scoping:** the training env (`training/env.py::TacticalRolloutEnv`) on
**fake-provider meetings**. A null result on the meeting-DEPENDENT terms is
EXPECTED and is reported WITH the surrogate caveat, never as "referee safe". This
task does NOT edit the referee it attacks — every patch is a recommendation routed
to the PAUSE.

---

## Verdict

| Roster | Verdict | Baseline `mean_score` | ES champion | Strongest reachable | `referee_passed` (any genome) |
|---|---|---|---|---|---|
| **9p2i** (baseline-3 primary substrate) | **EXPLOITS-FOUND** | 6.51 | 6.63 (+1.8%) | **16.62 (+155%)** | **False** — supply-floor gate holds |
| **4p1i** (flat determinism/leak reference) | **HELD** | 1.45 | 1.45 (+0.0%) | 1.45 (+0.0%) | False — supply-floor gate holds |

Materiality bar: a genome is an exploit only if the HARD validity gate passes AND
its relative geomean gain over the scripted-FSM baseline is **≥ 25%**.

**The two-layer referee is NOT broken as a champion-selection GATE today, but its
`mean_score` geomean sub-metric IS Goodhart-able on 9p2i.** A tactical genome that
just kills aggressively pushes `mean_score` 6.51 → 16.62 (2.55×) WITHOUT producing
any real deduction — the referee's own second layer (the evidence-supply floors)
still rejects it (`referee_passed = False`), so no degenerate champion is laundered
as "watchable" through the *composed* referee. But a consumer that reads
`mean_score` ALONE (without the supply-floor gate) would be fooled, and the
mechanism is a fake-provider artifact that MUST be re-checked under the surrogate
(§ Surrogate obligation).

---

## Budget (stated honestly — cheap insurance, not an exhaustive search)

Identical for both rosters:

- **ES:** `generations = 6`, `population = 6` (λ), so `1 + 6×6 = 37` genome
  evaluations, each a **K-seed average over `seeds = 0..7`** (8 fixed seeds) →
  the referee's own per-game mean over the set. σ = 0.5, `seed = 0`,
  `init_scale = 0.5`. Genome = a packet-only tactic-MLP, length **66**
  (8 features → 4 hidden → 6 tactics).
- **Reachability sweep:** `5` extra evaluations, one per single-tactic lever
  (`emergency`, `report`, `wait`, `kill`, `sabotage`), each forced to the top of
  the ranking — the physically-reachable corners a bounded random-init ES may not
  stumble into.
- **Total games:** `(37 + 5) × 8 + 8` (baseline) ≈ **344 games/roster**.

The ES climbs a chaotic per-seed fitness, so the K-seed averaging (the spike's
check-2 lesson) is load-bearing; the sweep is the systematic net so a null ES trace
never launders a false HELD.

---

## 9p2i — EXPLOITS-FOUND

### ES trace (every improvement decomposed — no undecomposed gains)

Champion `mean_score` per generation (index 0 = the seeded random genome):

```
3.28 → 5.44 → 5.44 → 6.63 → 6.63 → 6.63 → 6.63
```

The random-init ES only RECOVERS to ~the scripted-FSM level (6.63 vs 6.51,
+1.8% — below the bar); it did not converge to the kill-aggression corner within
6×6. Both strict improvements decompose to the SAME mechanism:

| Gen | Moving term | Δ fitness | Behavioral cause |
|---|---|---|---|
| 1 | **D2** | +2.16 | D2 separation 0.00 → 0.12, conversion pinned at 0.00 — the fake provider's rendered suspicion tracks the impostor's kill/exposure count, so aggressive play lifts the "crew-deduction" term with no ejection: suspicion theater, not deduction. |
| 3 | **D2** | +1.19 | D2 separation 0.12 → 0.22, conversion still 0.00 — same mechanism, larger. |

### Reachability sweep (the systematic net)

| Lever | `mean_score` | rel. gain | moving term | validity | `referee_passed` |
|---|---|---|---|---|---|
| `emergency` (meeting-farming) | 6.10 | −6% | d2 | pass | False |
| `report` | 3.70 | −43% | d1 | pass | False |
| `wait` (stall-to-clock) | 0.10 | −98% | d3 | **FAIL** | False |
| **`kill` (aggression)** | **16.62** | **+155%** | **d2** | pass | False |
| `sabotage` | 0.76 | −88% | d3 | pass | False |

Two findings worth stating plainly:

- **Meeting-farming is a NULL result here** (`emergency` → 6.10, *below*
  baseline). On 9p2i the FSM already averages 3–4 meetings/game, so the D4 contest
  term `min(1, (n−1)/2)` is already saturated at 1.0; extra impostor-called
  meetings only risk the impostor's own ejection. This is exactly FO-3's
  prediction — the meeting-DEPENDENT terms are not tactically reachable under fake
  meetings — and is reported WITH the surrogate caveat, not as "safe".
- **`stall-to-clock` is self-defeating** — a no-meeting game trips the validity
  gate's meeting-rate floor, so the constraint (the only one) rejects it.

### The exploit (routed to the PAUSE)

- **Mechanism (D2 separation, "suspicion theater"):** forcing kills drives
  `mean_score` **6.51 → 16.62 (+155%)**. The mover is the **D2 separation**
  sub-term: mean rendered-suspicion(true impostors) − mean(crew) rises **0.20 →
  0.84** while D2 **conversion stays pinned at 0.00** (no impostor is ever
  ejected), D3 stays 0, and `flags_per_meeting` stays 0. Under the fake provider,
  rendered suspicion tracks the impostor's kill/exposure count, so raw aggression
  inflates the "crew is deducing" dimension without ANY real deduction. Because the
  geomean is multiplicative, lifting D2 from ~0.1 to ~0.42 has outsized leverage on
  the score.
- **Trajectory evidence:** `forced-kill` lever, seeds 0–7, 9p2i — baseline
  `mean_score = 6.51` (mean 3.62 meetings/game) → `mean_score = 16.62` (mean 3.00
  meetings/game); D1 0.53 → 0.60, **D2 0.10 → 0.42 (separation 0.20 → 0.84,
  conversion 0.00)**, D3 0.00, D4 0.20 → 0.19. `referee_passed = False` throughout.
- **Recommended floor (NOT applied here — `eval/watchability.py` is out of
  scope):** GATE the D2 separation sub-term on conversion/evidence — separation
  without an ejection or a contradiction flag is suspicion theater, not deduction.
  Cap or condition separation on backed conversion, and NEVER read `mean_score`
  without the supply-floor gate. Routed to the PAUSE.

### Why no champion is laundered TODAY — the supply-floor gate

Evidence-supply floors on the strongest (kill-aggression) set, fake meetings:

| Gauge | measured | floor (baseline-3, 9p2i) | passed |
|---|---|---|---|
| `witnessed_event_rate` | 0.30 | 0.032 | ✅ |
| `flags_per_meeting` | **0.0** | 1.863 | ❌ |
| `testimony_backed_conversion` | **None** | 0.607 | ❌ |

The meeting-driven floors cannot clear under the fake provider (it mints no
contradiction flags and no observation-backed accusations), so
`referee_passed = False` for EVERY genome — the composed referee's champion-
selection GATE holds by its two-layer design, independent of the geomean. The
exploit lives entirely on the `mean_score` sub-metric.

---

## 4p1i — HELD

Champion trace: `0.70 → 1.45 → 1.45 → 1.45 → 1.45 → 1.45 → 1.45` (the ES recovers
from a poor random init to the FSM level; one gen-1 D2-separation improvement,
same mechanism, decomposed). Reachability sweep — NO lever clears the bar
(`emergency` 1.38, `report` 0.70, `wait` 0.10 [validity FAIL], `kill` 1.15,
`sabotage` 0.40); every gain is ≤ baseline (1.45). On this short, sparse roster the
kill-aggression separation lever has no headroom, and meeting-farming does not help.
`referee_passed = False` for all (same fake-meeting supply-floor story). **HELD** —
no exploit above the materiality bar. This is NOT "referee safe": it is a null
result under fake meetings and carries the same surrogate obligation.

---

## Scoping and the surrogate-path re-run obligation (Task 15.15)

Under fake meetings, the meeting-DECIDED terms (D2 separation/conversion, D3
deflection) and the meeting-driven supply floors (`flags_per_meeting`,
`testimony_backed_conversion`) are structurally unreachable/un-clearable — the fake
provider supplies no evidence to move or clear them. So:

- the D2-separation exploit found here is a **fake-provider artifact** (suspicion
  responds to kills but never converts). Under a real/surrogate crew, aggressive
  killing might ALSO drive conversion (legit deduction) — or the separation might
  persist without conversion (the exploit survives). Only the surrogate decides.
- the supply-floor GATE that currently rejects every genome is only meaningful once
  the meeting layer supplies evidence.

**OBLIGATION discharged at Task 15.15:** re-run this probe under the 15.13 learned
meeting surrogate on the fixed eval seed set — when the meeting-controlled terms
open to tactical pressure — and append the delta verdict vs this baseline to the
impostor-bakeoff report. Until then, the two verdicts above are provisional on the
fake-meeting scoping.

---

## Reproduce

```python
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import run_goodhart_probe

cfg = ESConfig(generations=6, population=6, sigma=0.5, seed=0,
               fitness_seeds=tuple(range(8)))
# 9p2i (EXPLOITS-FOUND):
run_goodhart_probe(config=cfg, num_players=9, num_impostors=2,
                   tasks_per_crewmate=2, materiality_bar=0.25)
# 4p1i (HELD):
run_goodhart_probe(config=cfg, num_players=4, num_impostors=1,
                   tasks_per_crewmate=1, materiality_bar=0.25)
```

Deterministic under `config.seed` (the env + referee are pure functions of the
seed). ES-core digests (pin the champion + fitness trace): 9p2i
`410b800c8474408b13da49669d6a7dca08b4e8e7f4ce320025fdf1cffe35eeeb`; 4p1i
`48c43bc92123f83fa7cfe4f0e528ee615947b18352111aa6cd8dbb9effd1f746`.
