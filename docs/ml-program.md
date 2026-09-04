# The ML program: four learned impostors won more games, and none became the default

Two phases of black-box search (17 and 18, July–August 2026) trained impostor policies for
AiLibi's deterministic social-deduction engine. Four beat the scripted policy on wins over
the seeds they share with it — 50 for three, the 49-seed intersection for the fourth — and
none became the default: each failed a bar written down before the measurement that judged
it, and the comparator they beat is itself defective in two measured ways. Every figure
names the committed file that owns it.

## Problem

AiLibi is a nine-player hidden-role game — seven crewmates, two impostors — on a
tick-deterministic engine behind an observation firewall
([`docs/architecture.md`](architecture.md)). Tactical play is rule-based every tick; meeting
speech and voting call an LLM. The tactical impostor is therefore a small, **partially**
observable decision problem under a frozen social layer: it sees the filtered packet an
agent sees, never the world. The question — **can search improve that arbitration without
un-making the deduction game above it?** — is two-sided on purpose: an impostor merely
better at not being seen starves meetings of testimony, so the second side is a gate, not a
reward.

## Environment

`training/env.py`'s `TacticalRolloutEnv` drives the **real** production loop —
`orchestrator.game.HeadlessGame` with an injected agent factory — interposing once, at the
factory, where a wrapper overrides the agent's chosen intent. The policy **observes** what
an agent observes, the visibility-filtered `ObservationPacket` and `PublicMapView`, and
cannot import the engine (an import-linter contract). The legal **action mask** comes from
the pure predicates in `engine/rules.py` and `engine/tick.py`, mirrored agent-side from the
packet; it splits engine-legal *resolved* actions from observation-meaningful
*submissions*, which keeps the impostor's engine-rejected pretend `do_task` submittable as
camouflage. The **reward** (`training/rewards.py`) reads
side-specific terms off the typed event log — impostor: the un-witnessed share of kills,
impostor survival, the share of meetings survived; crew: task progress, survival, the
share of impostors routed out by a crew body report, patrol coverage — plus the terminal
win, and adds potential-based shaping in the Ng-1999 *form*. Every dense term and the
shaping are **bounded fractions in [0, 1]**: the potential is a progress count over the
side's own win total (kills over the initial crew; completed tasks over the task total),
so the shaping pays the win condition once rather than once per unit of progress, and the
terminal weight is derived from the count of bounded channels — which is what makes every
reachable win outrank every reachable loss (`training/rewards.py::derive_terminal_weight`,
gated by the ordering test in `tests/training/test_rewards.py`).

The shaping is still **not policy-invariant, as that module says**: the potential is a
cumulative count, so at γ = 1 the shaping sum equals the terminal progress share.
Telescoping is not invariance — it is a real per-kill incentive that can change the
optimal policy, now at 1/`initial_crew` per kill (1/`tasks_total` per task) instead of
+1. Bounding shrinks the magnitude; it does not remove the non-invariance. The correction
is carried as errata by the campaign report
([`report-finalist-eval.md`](../training/reports/report-finalist-eval.md) §18).

The arm table below, and every fitness number in `training/reports/`, was produced under
the PREVIOUS raw-count objective and is republished by the ML re-ground, not edited here.
`training.rewards.FITNESS_OBJECTIVE_ID` names the current objective and no committed row
carries it, so a number from one objective can never be silently compared against a number
from the other.

```
seed ─▶ HeadlessGame, real loop, intent selector interposed at the agent factory
     ─▶ EpisodeRollout (reconstructed, state-hash verified) ─▶ shaped return
     ─▶ (1 + λ) ES over the 19-weight genome ─▶ candidate
     ─▶ held-out referee ─▶ PASS: adopt · FAIL: keep opt-in, record the miss
```

## Method

The entrant keeps the scripted impostor's option **generation** verbatim and replaces only
its **arbitration**: `enumerate_options` calls the FSM's own pure static helpers, so the
policy structurally cannot emit an off-menu or non-submission-legal intent
(`training/bakeoff/utility_es.py`); the pretend `do_task` above is on the menu because the
mask admits it as a submission. A linear utility scores each option and the argmax wins.
That scorer is 19 weights — 18 per-option features on the
`impostor-option-features-v1` basis plus a bias
(`agents/tactical/learned/forward.py::OPTION_FEATURE_NAMES`, `::ENCODER_VERSION`,
`::GENOME_LENGTH`) — and the forward pass is a `math.fsum` dot product with **no numpy and
no torch**, because BLAS reductions are not bit-stable across machines.

Search is a `(1 + λ)` evolution strategy (`training/bakeoff/es.py`) on an inner fitness of
the bounded tactically-reachable impostor terms plus the shaping, weighted by the side's
objective profile so the terminal win dominates, minus a cross-entropy anchor toward the
frozen FSM whose weight is capped at the largest value any committed harness uses (a
heavier one would make stalling the scheduler score better than playing). Selection is
separate and held out: `eval/watchability.py` is a
**selection-only** referee — evidence-supply floors plus a geometric mean, applied *after*
training and **never a training reward** (its SELECTION-ONLY DOCTRINE, owner-ratified
2026-07-05); optimized directly it produces the stealth simulator above.

## Results

Nine arms on the hosted eval model, recorded once; the four impostor-side candidates and
their comparator are below, quoted from
[`audit-phase-18-close.md`](../audits/audit-phase-18-close.md) §1.1 and reproduced by
`uv run python scripts/paired_stats.py training/reports/results-finalist-eval.jsonl`.

| policy | impostor win | same-seed scripted comparator | paired exact McNemar p | referee |
|---|---|---|---|---|
| `ea4bc955…` (put to the bar) | 26/50 = 0.52 | 13/50 = 0.26 | **0.0072** | **FAIL** |
| `bfd145cb…` | 28/50 = 0.56 | 13/50 = 0.26 | **0.0041** | **FAIL** |
| `6d327dcb…` (the committed opt-in champion) | 19/50 = 0.38 | 13/50 = 0.26 | **0.3075 — not significant** | **FAIL** |
| `7f73929d…` (n = 49) | 21/49 = 0.42857 | 12/49 = 0.24490 | 0.0352 — fails Bonferroni α = 0.0125 | **FAIL** |
| `p18-fsm-comparator` (scripted) | 13/50 = 0.26 | — | — | PASS |

**The edge of the one learned policy this repo committed is statistically unresolved**:
15 vs 9 discordant seeds, p = 0.3075; two of the four clear the family-wise Bonferroni bar
the p column names
([`report-finalist-eval.md`](../training/reports/report-finalist-eval.md) §18 item 1). Phase
17 ended the same way a recording earlier — `utility-es` 0.52 = 26/50 against the same-seed
scripted 0.36, Δ +0.16, referee FAIL
([`audit-phase-17-close.md`](../audits/audit-phase-17-close.md) §1.1). Every learned arm
fails the referee on evidence supply: testimony-backed conversion on all four, flags per
meeting on three (`bfd145cb…`'s flags gauge was ruled UNRESOLVABLE and excluded, so it fails
on conversion alone). The scripted policy is the only PASS: the bar was *win edge AND a
still-watchable game*, and nothing met both, twice.

## What the search actually found

Two behaviours separate the two policies
([`audit-phase-18-flip-emergence.md`](../audits/audit-phase-18-flip-emergence.md) §8.3):

- **N1 — it kills into witnesses at ~3.3× the scripted rate.** Crew-witnessed-kill rate
  30/197 = 0.15228 against 8/174 = 0.04598, z = +3.370, sign-reproduced 3/3.
- **N2 — it emits a kill class the scripted policy structurally cannot: co-present kills.**
  20/197 = 0.10152 against 0/174, z = +4.321, 3/3. The committed FSM kills only when alone.

That is specification gaming of a social-deduction referee, not better deception.
Convictions here are near-perfect on engine-certified evidence and near-chance without it
(310/310 = 1.000 with direct proof against 46/125 = 0.368 without, all four recorded sets;
[`audit-phase-19-close.md`](../audits/audit-phase-19-close.md) §4.1), and a witnessed kill
mints no certified flag: being *seen killing* is cheap where being *seen venting* is fatal.
Both are nonetheless ruled **NOT-DEMONSTRATED under the pre-registered emergence
discipline**, and this framing does not upgrade them: clause (c) wants a lever whose
ablation switches the behaviour off, and both appear on the un-levered control arm, so no
such lever exists. Findings, not demonstrated emergence.

## The comparator carried two measured defects, and they ran one way

The 2026-08-19 review found two target-selection defects, both 9p2i-only, both
**depressing the comparator**:

1. **Declined free kills.** The policy declines **190/415 = 45.8 %** of its legal
   zero-witness kill opportunities, and **168 of those — 40.5 % of all free kills — are the
   defect**: the kill seam re-validates only the top-ranked target, whose ranking branch
   breaks an exact-1.0 score tie by the lower player id. The other 22 are deliberate
   branches (15 fellow-defer, 7 cover); **0 are unattributed**.
2. **Stalking dead players.** The dead-set is built only from *seen* bodies, so an ejected
   player stays targetable: **303/2461 = 12.3 %** (samples 9p2i) and **555/6663 = 8.3 %**
   (corpus 9p2i) of impostor decisions top the target list with someone the table watched
   get ejected. Both 4p1i sets are clean — **0/632 and 0/579** — a nine-player-roster
   effect, and one seed is a demonstrably thrown game.

Both rates are committed pins from that review — `eval/evidence_honesty.py`'s I-11 cells,
asserted by `tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` over
10,335 reconstructed decisions with **zero mismatches** against the recorded actions.

**Direction of the confound, plainly:** a weakened comparator inflates every win edge above,
so those edges are **upper bounds**. Nothing else moves: the referee verdicts, the NO-FLIP
rulings and the pre-registration ordering all stand, and the gate failures are if anything
understated, since a stronger comparator would not have made these arms more watchable.

**Erratum, and it is not closed.** Both defects are repaired in the tree as it stands: the
kill seam and the sabotage guard now scan the whole ranking for a co-located, zero-witness
candidate instead of testing only its head, and a target whose freshest sighting predates the
last meeting boundary can no longer rank at all. Nothing was retrained and nothing was re-run
against the repaired policy, so the comparator every edge in the table above was measured
against no longer exists in that form, and those edges were never re-measured. They are stale
by construction — upper bounds against a policy this repository no longer ships — and
re-grounding them means a fresh campaign on the current mover, which is an owner decision and
not a documentation edit. Until that happens the table stands as recorded, with this
paragraph attached to it.

## What the next recording changed under all of this

The social layer these policies were searched against was rebuilt after the campaign closed,
and the committed sets re-recorded twice, most recently at impostor win rates
36% (4p1i) and 30% (9p2i).
[`audit-phase-20-baseline-7.md`](../audits/audit-phase-20-baseline-7.md) §3
read the first: two bars met, two missed — **a FINDING, not an adoption; that
recording is canon by an owner override dated 2026-08-26 (§6.1)**. A later recording met
three of four bars: innocent ejections fell from 46 to 20, but 11 of 20 = 0.5500 were the
meeting's own reporter, against a registered 0.40 — **a finding again, nothing adopted**
([the record](../audits/audit-phase-21-adopting-record.md)). Neither re-prices a referee
verdict.

## What the instruments now stand on

The three committed ML instruments were re-fit on the corpus that second re-recording left
behind, so each reads the bytes its weights were made from — `replays/ml_corpus/9p2i`,
fingerprint `cc54d3c0…`. Every row below re-derives under
`scripts/verify_ml_evidence.py --complete`.

| instrument | verdict | the axes it was judged on |
|---|---|---|
| ballot surrogate | **NO-GO** (ranking passes, decision fails) | who it ranks first, against the ceiling; whether to eject, against always-eject |
| conviction model | **GO** | its flag-count rank correlation; its recall, against a share of the ceiling; its accuracy, against the best constant answer |
| composed runner | **GO** | its meeting decision, against always-eject; its ranking on convicting meetings, against the ceiling |

Each bar is a fraction of a constant measured on the same split, so none of it transfers as
an absolute; the numbers live in `training/reports/` and each `verdict.json`. The
surrogate's NO-GO keeps it diagnostic-only.

Two things the re-ground did not do. It did not re-search the λ grid under the repaired
fitness objective — those cells record a search under the prior one, which the stale-seed
fence cannot see. And it did not re-price the arm table above: **those edges were measured
against a comparator this repository no longer ships**, as its erratum says. Both are owner
decisions.

## Limitations

One model (`Qwen/Qwen3.6-27B`, locked 2026-07-12 —
[`audit-phase-16-model-lock.md`](../audits/audit-phase-16-model-lock.md)), one prompt set,
50 games per arm for three arms and 49 for `7f73929d…` after seed 35 was excluded. The
bar's floors are population-relative, derived from one reference recording, so "FAIL" is a
statement about this bar and re-pricing it is an owner decision. The raw recordings live
outside the repo tree; what is committed is their *measurement*
([`report-finalist-eval.md`](../training/reports/report-finalist-eval.md) §2, §19). Only the
impostor's tactical arbitration was searched, so nothing here is evidence about learned
*social* play.

## Related work

The environment sits near Hanabi (Bard et al., 2020) and the Diplomacy deception work
(FAIR et al., *Science*, 2022) — here the social layer is frozen and only the *tactical*
layer learns. The method is the ES family (Salimans et al., 2017); the shaping analysis is
Ng, Harada & Russell (1999); and the selection scalar is kept off the objective for the
reasons the referee itself cites (Pan et al., 2022; Skalse et al., 2022).

Next: the [reading guide](reading-guide.md) and
[`training/README.md`](../training/README.md).
