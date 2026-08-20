# The ML program: four learned impostors won more games, and none of them shipped

Two phases of black-box search (17 and 18, July–August 2026) trained impostor policies for
AiLibi's deterministic social-deduction engine. Four beat the scripted policy on wins over
the same 50 seeds; none became the default, because each failed a bar written down before
the measurement that judged it — and the comparator they beat is itself defective in two
measured ways. Every figure names the committed file that owns it.

## Problem

AiLibi is a nine-player hidden-role game — seven crewmates, two impostors — on a
tick-deterministic engine behind an observation firewall
([`docs/architecture.md`](architecture.md)). Tactical play is rule-based every tick;
meeting speech and voting call an LLM. The tactical impostor is therefore a small, fully
observable decision problem under an expensive frozen social layer, and the question is
whether **search can improve its arbitration without un-making the deduction game above
it** — an impostor merely better at not being seen starves meetings of testimony and turns
the game into a stealth simulator. The objective is two-sided; the second side is a gate,
not a reward.

## Environment

`training/env.py`'s `TacticalRolloutEnv` drives the **real** production loop —
`orchestrator.game.HeadlessGame` with an injected agent factory, never a bespoke training
game — interposing once, at the factory, where a wrapper overrides the real agent's chosen
intent. The policy **observes** exactly what an agent does — the visibility-filtered
`ObservationPacket` and `PublicMapView` — and cannot import the engine (an import-linter
contract). The legal **action mask** comes from the pure predicates in `engine/rules.py`
and `engine/tick.py`, mirrored agent-side from the packet plus two small trackers; it
splits engine-legal *resolved* actions from observation-meaningful *submissions*, which
keeps the impostor's engine-rejected pretend `do_task` submittable as camouflage. The
**reward** (`training/rewards.py`) reads side-specific terms off the typed event log
(kills, un-witnessed-ness, survival, meetings survived) plus the
terminal win, and adds potential-based shaping in the Ng-1999 *form* that is **not
policy-invariant, as that module now says**: the potential is a cumulative count, so at
γ = 1 the shaping sum equals the terminal kill count. Telescoping is not invariance — it is
a real +1-per-kill incentive that can change the optimal policy. That docstring's old
invariance claim was false as deployed; it is corrected in code and carried as errata
([`report-finalist-eval.md`](../training/reports/report-finalist-eval.md) §18).

```
seed ─▶ HeadlessGame, real loop, intent selector interposed at the agent factory
     ─▶ EpisodeRollout (reconstructed, state-hash verified) ─▶ shaped return
     ─▶ (1 + λ) ES over the 19-weight genome ─▶ candidate
     ─▶ held-out referee ─▶ PASS: adopt · FAIL: keep opt-in, record the miss
```

## Method

The entrant keeps the scripted impostor's option **generation** verbatim and replaces only
its **arbitration**: `enumerate_options` calls the FSM's own pure static helpers, so the
policy structurally cannot emit an off-menu or illegal intent
(`training/bakeoff/utility_es.py`); a linear utility scores each option and the argmax wins.
That scorer is 19 weights — 18 per-option features on the `impostor-option-features-v1`
basis plus a bias (`agents/tactical/learned/forward.py`: `OPTION_FEATURE_NAMES`,
`ENCODER_VERSION`, `GENOME_LENGTH`) — and the shipped forward pass is a `math.fsum` dot
product with **no numpy, no torch, no activation**, because BLAS reductions are not
bit-stable across machines.

Search is a `(1 + λ)` evolution strategy (`training/bakeoff/es.py`) on an inner fitness of
tactically-reachable impostor terms plus the shaping, minus a cross-entropy anchor toward
the frozen FSM. Selection is separate and held out: `eval/watchability.py` is a
**selection-only** referee — evidence-supply floors plus a geometric mean, applied *after*
training and **never a training reward** (its SELECTION-ONLY DOCTRINE, owner-ratified
2026-07-05), because optimizing it directly produces the stealth simulator above.

## Results

Nine arms × 50 seeds on the hosted eval model, recorded once. The win cells are quoted from
[`audit-phase-18-close.md`](../audits/audit-phase-18-close.md) §1.1; the p-values are
recomputed on a fresh clone by
`uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl`.

| policy | impostor win | same-seed scripted comparator | paired exact McNemar p | referee |
|---|---|---|---|---|
| `ea4bc955…` (put to the bar) | 26/50 = 0.52 | 13/50 = 0.26 | **0.0072** | **FAIL** |
| `bfd145cb…` | 28/50 = 0.56 | 13/50 = 0.26 | **0.0041** | **FAIL** |
| `6d327dcb…` (shipped, opt-in) | 19/50 = 0.38 | 13/50 = 0.26 | **0.3075 — not significant** | **FAIL** |
| `7f73929d…` (n = 49) | 21/49 = 0.42857 | 12/49 = 0.24490 | 0.0352 — fails Bonferroni α = 0.0125 | **FAIL** |
| `p18-fsm-comparator` (scripted) | 13/50 = 0.26 | — | — | PASS |

**The edge of the policy this repo actually ships is statistically unresolved**: 15 vs 9
discordant seeds, p = 0.3075. The family-wise bar over four arms is Bonferroni α = 0.0125,
which `7f73929d…` also fails; two of the four survive it
([`report-finalist-eval.md`](../training/reports/report-finalist-eval.md) §18 item 1). Phase
17 ended the same way a recording earlier: `utility-es` 0.52 = 26/50 against the same-seed
scripted 0.36, Δ +0.16, referee FAIL
([`audit-phase-17-close.md`](../audits/audit-phase-17-close.md) §1.1). Every learned arm
fails the same two supply gauges, flags per meeting and testimony-backed conversion; the
scripted policy is the only PASS. The bar was *win edge AND a still-watchable game*; nothing
met both, twice.

## What the search actually found

Two behaviours separate the learned impostor from the scripted one
([`audit-phase-18-flip-emergence.md`](../audits/audit-phase-18-flip-emergence.md) §8.3):

- **N1 — it kills into witnesses at ~3.3× the scripted rate.** Crew-witnessed-kill rate
  30/197 = 0.15228 against 8/174 = 0.04598, z = +3.370, sign-reproduced 3/3.
- **N2 — it emits a kill class the scripted policy structurally cannot: co-present kills.**
  20/197 = 0.10152 against 0/174, z = +4.321, 3/3. The committed FSM kills only when alone.

That is specification gaming of a social-deduction referee, not better deception.
Convictions here are near-perfect on engine-certified evidence and near-chance without it
(310/310 = 1.000 with direct proof against 46/125 = 0.368 without, all four recorded sets;
[`audit-phase-19-close.md`](../audits/audit-phase-19-close.md) §4.1), and a witnessed kill
mints no certified flag — so being *seen killing* is cheap where being *seen venting* is
fatal, and the search found the cheap side. Both are nonetheless ruled
**NOT-DEMONSTRATED under the pre-registered emergence discipline**, and this framing does
not upgrade them: clause (c) wants a lever whose ablation switches the behaviour off, and
both appear on the un-levered control arm, so no such lever exists. Findings, not
demonstrated emergence.

## The comparator carries two measured defects, and they run one way

The 2026-08-19 review found the scripted comparator's target selection defective two ways,
both 9p2i-only, both **depressing the comparator**:

1. **Declined free kills.** The kill seam re-validates only the top-ranked target, so
   **190/415 = 45.8 %** of legal zero-witness kills are declined — 168 inside the ranking
   branch's exact-1.0 score tie broken by the lower player id, 15 fellow-defer, 7 cover,
   **0 unattributed**.
2. **Stalking dead players.** The dead-set is built only from *seen* bodies, so an ejected
   player stays targetable: **303/2461 = 12.3 %** (samples 9p2i) and **555/6663 = 8.3 %**
   (corpus 9p2i) of impostor decisions top the target list with someone the whole table
   watched get ejected. Both 4p1i sets are clean — **0/632 and 0/579** — so it is a
   nine-player-roster phenomenon, and one seed is a demonstrably thrown game.

Both rates are committed pins from that review: `eval/evidence_honesty.py`'s I-11 cells,
asserted by `tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` over
10,335 reconstructed decisions with **zero mismatches** against the recorded action stream.

**Direction of the confound, plainly:** a weakened comparator inflates every win edge above,
so those edges are **upper bounds**. Nothing else moves — the referee verdicts, the NO-FLIP
rulings and the pre-registration ordering all stand, and the gate failures are if anything
understated, since a stronger comparator would not have made these arms more watchable. The
mover repair is Task 20.32; the re-measurement on corrected bytes is Task 20.38.

## Limitations

One model (`Qwen/Qwen3.6-27B`, locked 2026-07-12 —
[`audit-phase-16-model-lock.md`](../audits/audit-phase-16-model-lock.md)), one prompt set,
50 games per arm per set.
The bar's floors are population-relative, derived from one reference recording, so "FAIL" is
a statement about this bar, not a universal one; re-pricing it is an owner decision, never an
instrument edit. The finalist eval's raw recordings live outside the repo tree; what is
committed is their *measurement*
([`report-finalist-eval.md`](../training/reports/report-finalist-eval.md) §2, §19). Only the
impostor's tactical arbitration was searched, so nothing here is evidence about learned
*social* play.

## Related work

The environment sits near Hanabi (Bard et al., 2020) for reasoning about other agents'
beliefs and near the deception work around Diplomacy (FAIR et al., *Science*, 2022) — here,
though, the social layer is frozen and only the *tactical* layer learns. The method is the ES
family (Salimans et al., 2017): tiny parameter count, no gradient through a simulator. The
shaping analysis is Ng, Harada & Russell (1999), and the selection scalar is kept off the
objective for the reasons the referee's own citations give (Pan et al., 2022; Skalse et al.,
2022).

---

Next: the [reading guide](reading-guide.md) for the corpus-level numbers,
[`training/README.md`](../training/README.md) for the disposition of every surface this
program built, and the [phase-17](../audits/audit-phase-17-close.md) /
[phase-18](../audits/audit-phase-18-close.md) closes.
