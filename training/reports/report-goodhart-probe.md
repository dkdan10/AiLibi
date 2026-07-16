# Adversarial Goodhart probe — the baseline-5 re-run on the re-grounded surrogate (Task 17.15; probe design Task 15.14)

**Subject under attack:** the committed champion-SELECTION referee
(`eval/watchability.py::compute_watchability` — Task 15.2), now with the
**baseline-5 evidence-supply floors** (the 16.11 population-relative derivation;
the bake-off flipped to them at Task 17.11) and the **15.19 conversion-coupled
D2 term** — the floor this probe's own baseline-3 run recommended, since applied.
**Method:** unchanged from Task 15.14 — the shared ES core
(`training/bakeoff/es.py`) run DIRECTLY on the COMPOSED referee (the
deliberately-forbidden objective, SELECTION-ONLY DOCTRINE), plus the forced
single-tactic reachability sweep, everything decomposed — now run on BOTH
committed meeting models: (1) **fake-provider meetings** (re-earning the
two-roster baseline at baseline-5), and (2) the **17.10 re-grounded ballot
surrogate**, threaded through the probe's own entry point
(`run_goodhart_probe(meeting_runner_factory=…)`) by the committed harness driver
(`training/bakeoff/harness.py::run_goodhart_surrogate_rerun`, CLI
`goodhart-surrogate`).
**Anchors:** `GOODHART_9P2I_BASELINE` (`training/bakeoff/harness.py` — the
fake-provider delta anchor RE-MEASURED at Task 17.11, never hand-copied;
reproduced below, digest-verified); the 17.10 re-verdict
(`training/reports/report-ballot-surrogate.md` — GO, ranking-earned); the
binding channel verdicts of `audits/audit-phase-15-pause.md` §4.
**Scoping:** neither committed meeting model is the real-LLM path (the pause
audit's §11 limitation stands). This task does NOT edit the referee it attacks —
every patch is a recommendation routed to the PAUSE.

---

## Verdict

| Path | Roster | Verdict | Baseline `mean_score` | ES champion | Strongest reachable | `referee_passed` (any genome) |
|---|---|---|---|---|---|---|
| fake provider, seeds 0–7 | **9p2i** | **HELD** | 3.28 | 3.70 (+12.98%) | 3.70 (`report` lever; the ES ties it) | False — supply-floor gate holds |
| fake provider, seeds 0–7 | **4p1i** | **EXPLOITS-FOUND** | 0.85 | 0.85 (+0.0%) | **1.38 (+61.8%, `emergency`)** | False — supply-floor gate holds |
| **re-grounded surrogate**, 30 eval seeds | **9p2i** | **HELD** (wrong-reason regime — see §Surrogate) | 3.33 | 3.47 (+4.4%) | 3.33 (= the baseline; every candidate inadmissible) | False — validity fail-closes every set |

Materiality bar (all runs): relative geomean gain over the scripted-FSM baseline
**≥ 25%**, validity-gated. `baseline_id = "baseline-5"` everywhere.

**The delta verdict (the 17.11 anchor threaded through the committed driver):**

> 15.14 fake-provider verdict HELD (strongest reachable 3.7 via report) ->
> surrogate-path verdict HELD (champion 3.47, strongest reachable 3.33,
> referee_passed=False)

**Headline:** the Phase-15 no-exploitable-seam conclusion **survives baseline 5
at the measured scale, but it had to be re-earned and it narrowed.** No genome
on either meeting model clears the materiality bar on 9p2i or launders past the
composed selection gate (`referee_passed = False` for every genome on every
path). Three things moved under it:

1. **The baseline-3 exploit channel is closed.** The 9p2i fake-path verdict
   flipped EXPLOITS-FOUND → HELD because the 15.19 conversion-coupled D2 floor —
   the exact patch the original probe routed to the pause — now zeroes ungated
   separation: the forced-`kill` "suspicion theater" lever collapsed from 16.62
   (+155%) to 3.64 (+11.1%).
2. **A new fake-path exploit opened on the short roster.** On 4p1i,
   meeting-farming (`emergency`) now clears the bar: 0.85 → 1.38 (+61.8%) via
   the D4 contest term (mechanism `d4-contest-farming`). Routed to the PAUSE
   below.
3. **The surrogate-vs-real divergence flipped sign and collapsed at the
   outcome level.** Phase-15's surrogate over-ejected (ejection rate 0.924 vs
   the fake path's 0.000 — the two models bracketed the real path). The
   re-grounded baseline-5 surrogate **never ejects** (0/116 meetings on the
   eval seeds, SKIP rate 1.000) — the mirror regime, driven by the citation
   economy the 6-feature surrogate cannot see (§Citation blindness). The
   recorded real-LLM test split ejects 50/104 meetings (0.481), so the
   surrogate-vs-REAL decision-level divergence is now maximal and one-signed.

---

## Budget (stated honestly — cheap insurance, not an exhaustive search)

- **Fake provider (both rosters):** the committed 15.14 shape — `generations=6`,
  `population=6` (λ), `1 + 6×6 = 37` genome evaluations, each a K-seed average
  over `seeds 0..7`; σ = 0.5, `seed = 0`, `init_scale = 0.5`; genome = the
  packet-only tactic-MLP, length **66** (8 features → 4 hidden → 6 tactics).
  Reachability sweep: 5 forced single-tactic levers. ≈ **344 games/roster**.
- **Surrogate path (9p2i):** the same ES shape re-anchored on the fixed eval
  seed set (the frozen corpus test split, 30 seeds `1004, 1009, …, 1149`;
  `seed % 5 == 4`) — 37 genome evaluations + 5 sweep levers + the FSM baseline
  = `(37+5)×30 + 30` = **1,290 games** (the Phase-15 §6 prose said "≈ 1,320";
  that figure was inflated by one evaluation), plus the 30-seed × 2-path
  ejection/SKIP measurement. Surrogate staleness
  usage: **3,490 simulated meetings** metered against the committed
  `max-uses.json` cap of **62,491** (≈ 5.6%), through one shared
  `SurrogateUseCounter`. Wall-clock 295 s.

---

## 9p2i, fake provider — HELD (the 17.11 anchor, reproduced)

This run IS the re-measured delta anchor: its headline row matches
`GOODHART_9P2I_BASELINE` field-for-field and its ES-core digest matches the
pinned `a7c5ea590233f0735571cf6960fbdf1567bdbb2575e0d27bfba995f08d235c14` —
reproduced at this tree, never hand-copied.

Champion `mean_score` per generation (index 0 = the seeded random genome):

```
3.28 → 3.70 → 3.70 → 3.70 → 3.70 → 3.70 → 3.70
```

One strict improvement, decomposed (no undecomposed gains): gen 1, **D1**
(+0.42) — a resolution/meeting-mix shift (mean meetings 3.88 → 4.00), not an
evidence term. The champion converges to the same corner as the forced-`report`
lever (both 3.70), so the anchor names the lever.

### Reachability sweep (the systematic net)

| Lever | `mean_score` | rel. gain | moving term | validity | `referee_passed` |
|---|---|---|---|---|---|
| `emergency` (meeting-farming) | 2.85 | −13% | d2 (noise) | pass | False |
| **`report`** | **3.70** | **+12.98%** | **d1** | pass | False |
| `wait` (stall-to-clock) | 0.10 | −97% | d2 (noise) | **FAIL** | False |
| `kill` (aggression) | 3.64 | +11.1% | d1 | pass | False |
| `sabotage` | 0.65 | −80% | d2 (noise) | pass | False |

- **The baseline-3 kill exploit does not reproduce**: 3.64 (+11.1%, D1
  meeting-mix, mean meetings 3.62 → 3.00) vs 16.62 (+155%, D2 separation) at
  baseline 3. The 15.19 conversion-coupled D2 term gates separation on
  deduction evidence (a converted backed accusation or a contradiction/vent
  flag); under fake meetings there is none, so suspicion theater now scores 0
  on D2 — the channel the pause contracted shut IS shut.
- The strongest reachable corner is now the mild `report`/D1 meeting-mix shift
  at +12.98% — **below the bar**; `wait` still self-defeats (meeting-rate floor
  → validity FAIL).

### Why no champion is laundered — the supply-floor gate (baseline-5, 9p2i)

Champion-set gauges (fake meetings): `witnessed_event_rate` 0.0 vs floor
0.0345 ❌; `flags_per_meeting` 0.0 vs 0.5028 ❌; `testimony_backed_conversion`
None vs 1.0 ❌ (the population-relative conversion floor evaluates at its 1.0
cap when measured flags are 0). The fake provider mints no contradiction flags
and no observation-backed accusations, so `referee_passed = False` for every
genome — the two-layer gate holds independent of the geomean, exactly as at
baseline 3.

---

## 4p1i, fake provider — EXPLOITS-FOUND (meeting-farming on the short roster)

Champion trace: `0.70 → 0.85 → 0.85 → 0.85 → 0.85 → 0.85 → 0.85` (one gen-1 D1
improvement, decomposed; the ES only recovers to the scripted-FSM level 0.85,
+0.0%). The sweep is what finds it, again:

| Lever | `mean_score` | rel. gain | moving term | validity | `referee_passed` |
|---|---|---|---|---|---|
| **`emergency` (meeting-farming)** | **1.38** | **+61.8%** | **d4** | pass | False |
| `report` | 0.70 | −18% | d2 (noise) | pass | False |
| `wait` (stall-to-clock) | 0.10 | −88% | d2 (noise) | **FAIL** | False |
| `kill` | 0.55 | −35% | d2 (noise) | pass | False |
| `sabotage` | 0.40 | −53% | d2 (noise) | pass | False |

- **Mechanism (`d4-contest-farming`):** impostor-called emergency meetings lift
  mean meetings/game **1.00 → 1.75**, moving the D4 contest term
  `min(1, (n−1)/2)` with no added deduction. At baseline 3 this lever sat BELOW
  the 4p1i baseline (1.38 vs 1.45, a null); the referee's D2 re-coupling since
  15.19 lowered the honest FSM baseline to 0.85 while the farming corner is
  unchanged — the same corner is now +61.8%, above the bar. The 9p2i roster
  stays immune for the original FO-3 reason: its FSM baseline already averages
  ~3.6 meetings/game, so the contest term is saturated; on the short roster one
  meeting/game leaves headroom.
- **Trajectory evidence:** forced-`emergency` lever, seeds 0–7, 4p1i — baseline
  `mean_score = 0.85` (mean 1.00 meetings) → 1.38 (mean 1.75 meetings);
  `referee_passed = False` throughout — the supply-floor gate rejects it (the
  fake provider mints no contradiction flags and no observation-backed
  accusations, so the meeting-driven baseline-5 floors — `flags_per_meeting`
  0.4103, conversion at its population-relative cap — cannot clear). Champion-set
  gauges for the roster: `witnessed_event_rate` 0.0 vs 0.0164 ❌,
  `flags_per_meeting` 0.0 vs 0.4103 ❌, conversion None vs 1.0 ❌ — the same
  two-layer story as 9p2i.
- **Recommended floor (NOT applied here — `eval/watchability.py` is out of
  scope):** cap the D4 contest term's reward for raw meeting COUNT (it already
  saturates at n ≥ 3); gate contest on a per-meeting evidence floor so
  impostor-farmed empty meetings cannot inflate it. Routed to the PAUSE.
- **Blast radius, stated plainly:** the composed selection gate still rejects
  every genome (supply floors), champion selection runs on 9p2i, and 4p1i is
  the determinism/leak reference roster — so no champion can be laundered
  through this today. The exploit lives on the `mean_score` sub-metric for any
  consumer that reads it alone, on the short roster.

---

## The surrogate-path re-run (Task 17.15 — the divergence reading)

Discharged through the probe's OWN entry point —
`run_goodhart_probe(meeting_runner_factory=load_surrogate_runner_factory(…))`
via the committed `goodhart-surrogate` CLI — including the forced reachability
sweep, against the **17.10 re-grounded artifact**
(`training/artifacts/surrogate/ballot-predictor.json`, sha256
`62d6cbfa3173bf9d56ccce7646c0722fd4e341e11c1ef2a6d2208b74c1408d28`, fit on the
17.9 baseline-5 corpus, GO verdict).
Verdict: **HELD (champion 3.47, +4.4%; zero exploits; zero improvements)** —
and, exactly as in Phase 15, **a HELD here must NOT be read as exploit-caught.**
It is held in the wrong-reason regime the task contract warns about:

1. **The validity gate still fail-closes EVERY surrogate-path set, including
   the scripted-FSM baseline** (`baseline_validity_passed = false`; the ES
   fitness trace is pinned at the invalid sentinel −1.0 for the seeded genome
   and all 6 generations —
   a flat all-invalid landscape, zero improvements to decompose; the
   "strongest reachable" 3.33 is the inadmissible baseline itself). The failing
   check is unchanged: `cost_and_provenance_exact` — surrogate meetings record
   no LLM calls, so the set carries no model provenance row. The Phase-15
   routed-to-pause ask (a declared synthetic provenance stamp, or an explicit
   surrogate-path gate mode) is still open; until it lands, surrogate probe
   runs stay diagnostic-only.
2. **The ejection/SKIP rate, alongside the verdict** (scripted-FSM baseline,
   the same 30 eval seeds): the re-grounded surrogate resolves **0/116 meetings
   with an ejection (ejection rate 0.000, SKIP rate 1.000)**; the fake-provider
   path on the same seeds also resolves 0/116. The recorded **real-LLM test
   split ejects 50/104 (0.481)**. Phase-15's bracket (fake 0.000 / surrogate
   0.924, straddling the real path) has **collapsed onto the fake side**: the
   under-ejection regime the 15.15 contract warned about is now the measured
   one. The meeting-driven floors hold for supply reasons — champion-set
   gauges: `witnessed_event_rate` 0.0204 vs floor 0.0345 ❌,
   `flags_per_meeting` 0.0 ❌ (the surrogate synthesizes ballots, never the
   contradiction flags the gauge counts), conversion None vs the 1.0
   population-relative cap ❌ — never because the referee caught an exploit.
3. **What the sweep DID show:** nothing near the bar. `kill` 3.59 (+7.8% vs
   the surrogate-path FSM baseline 3.33; +11.1% under fake meetings — both far
   under 25%); `report` 3.47 (+4.4%); `emergency` meeting-farming 2.68 (−19%:
   farmed meetings that all SKIP just dilute the set); `wait` 0.10
   (floor-tripped); `sabotage` 1.14 (−66%). No genome flips `referee_passed`;
   no gate-laundering candidate exists on either path.

**Because the surrogate now skips every tally, it opens NOTHING the fake
provider doesn't:** D2 conversion, D3 deflection and the meeting-driven supply
floors are exactly as unreachable under this surrogate as under fake meetings.
This re-run therefore probes strictly LESS of the referee than Phase-15's
over-ejecting surrogate did — a null on the meeting-decided terms remains a
scoping statement, not "referee safe".

---

## Citation blindness — the seam this re-run was pointed at, addressed explicitly

Baseline 5's economy change is that **convictions demand citations**: the J2
citation gate (unconditional since the 16.17 record) coerces any zero-flag
EJECT ballot that cites neither a transcript turn (`primary_reason_id`) nor a
first-hand observation (`primary_reason_observation_id`) to SKIP. That made the
recorded economy skip-majority (voters SKIP 58.4% of ballots; 54/104 test
meetings resolve SKIP) and raised the impostor win rate 0.24 → 0.36.

The 6-feature surrogate is blind to that structure on three counts, by design
(the live-parity fence, locked decision 4): its features
(`belief_suspicion, belief_trust, is_reporter, witnessed_vent, meeting_index,
alive_count`) carry no citation channel; the ballots it emits leave both
citation fields None; and it feeds `tally_ballots` directly, bypassing the J2
gate entirely.

**Where the gap actually opened:** not as a referee-score seam — as
**decision-channel collapse**. Fit on the skip-majority corpus, the predictor
casts SKIP on 86% of individual ballots and its sparse non-SKIP ballots never
assemble a plurality past the 0.60 tally gate: 0 ejections in 104 held-out
meetings (the 17.10 fidelity census; decision accuracy 51.9% = the always-SKIP
constant). The 17.10 GO is earned by the RANKING channel (top-1 86.0% vs the
82.0% honest ceiling); the decision channel is population-prior-shaped, not
learned. This probe measures the consequence: the surrogate's behavioral
divergence from the real economy is maximal exactly where the citation
structure decides outcomes (eject vs skip: 0.000 vs 0.481), while its
divergence from the fake provider is nil. **The citation-blind seam is real and
now quantified — it just is not a seam an optimizer can push a champion
through, because the composed referee re-scores candidates where the blindness
fails floors (flags, conversion) and the validity gate fail-closes the
substrate outright.**

---

## Does the Phase-15 conclusion survive baseline 5?

**Yes at the measured scale, with its meaning narrowed and stated:** bounded
divergence on every score channel the probe can reach (max lever delta +7.8%
surrogate / +12.98% fake on 9p2i, both below the bar), no exploitable seam INTO
champion selection (no gate-laundering genome on any path; supply floors +
validity fail-close hold), and one NEW above-bar `mean_score` exploit on the
4p1i reference roster (d4-contest-farming, fake path) routed to the PAUSE. The
surrogate-side reading is deliberately weaker than Phase-15's wording: this
HELD clears nothing on its own (the pause's §4 rule), and the substrate now
under-ejects so the meeting-decided channels went unprobed — the honest
statement is "no seam reachable at this scale on this substrate", re-earned,
not "no seam".

---

## Implication for 17.12 (the probe is an instrument, not a gate)

The divergence reading BOUNDS how hard the bake-off's optimizers may lean on
the surrogate: it is ranking-faithful but decision-degenerate, so any
training-time signal routed through meeting OUTCOMES (ejections, post-meeting
survival, meeting-driven floors) is flat or optimistic under it — an optimizer
can learn meeting impunity the real path punishes. The max-uses budget already
prices this lean (this entire re-run consumed 3,490 of the committed 62,491
simulated meetings), and the bake-off protocol re-scores every reported number
on a real meeting path with surrogate-vs-real divergence reported side by
side, where this seam surfaces as data. That is the implication; the bake-off
plan itself is 17.12's contract, not this report's.

---

## Standing obligations and routing

- The probe machinery's standing surrogate obligation is discharged **for
  baseline 5 (9p2i)** by this run; it re-arises at the next re-grounding, per
  the pause's locked re-grounding cadence.
- The real-LLM path remains unprobed (pause audit §11) — both committed meeting
  models are proxies, and they no longer bracket the real path.
- Routed to the PAUSE: (a) the 4p1i `d4-contest-farming` floor recommendation
  (above); (b) the still-open synthetic-provenance stamp / surrogate-path gate
  mode, without which every surrogate probe run stays validity-fail-closed
  diagnostics.

---

## Reproduce

```python
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import run_goodhart_probe

cfg = ESConfig(generations=6, population=6, sigma=0.5, seed=0,
               fitness_seeds=tuple(range(8)))
# 9p2i fake provider (HELD — reproduces the 17.11 GOODHART_9P2I_BASELINE anchor):
run_goodhart_probe(config=cfg, num_players=9, num_impostors=2,
                   tasks_per_crewmate=2, materiality_bar=0.25)
# 4p1i fake provider (EXPLOITS-FOUND):
run_goodhart_probe(config=cfg, num_players=4, num_impostors=1,
                   tasks_per_crewmate=1, materiality_bar=0.25)
```

Surrogate path (the committed driver; prints the full probe report + meeting
stats + the delta verdict):

```
uv run python -m training.bakeoff.harness goodhart-surrogate --budget committed
```

Deterministic under `config.seed` (env + referee + surrogate are pure functions
of the seed). ES-core digests: 9p2i fake
`a7c5ea590233f0735571cf6960fbdf1567bdbb2575e0d27bfba995f08d235c14` (matches the
17.11 anchor pin); 4p1i fake
`5351db5ee8d1b3625655fa68f818738a51d526fe1afdcddfdeb5e8651cceb630`; 9p2i
surrogate
`2492db5244d504db4de97ee728d8accfbaa6fa202f8af7a9c209a0c4190017f0`.
