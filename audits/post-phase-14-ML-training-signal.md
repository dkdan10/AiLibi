# Post-Phase-14 planning — the training signal: a better R-score and an accurate no-LLM meeting model for ML tactical agents

**Date:** 2026-07-04
**Author task:** the owner has chosen the ML direction — learned tactical agents that play **between** the LLM
meetings. This document maps the *clean path to a sound training signal* before any policy is trained. It
targets the owner's two named asks — **reconstruct a better "R-score" from scratch** and **build an accurate
no-LLM meeting simulation** — plus what **tests and data** must be gathered, and (owner's explicit steer)
**better-grounded training objectives than a fuzzy "watchability" score.**
**Status:** PLANNING DOCUMENT. Read-only with respect to source; the only repo output is this file. It is a
sibling of `post-phase-14-ML-planning.md`, `post-phase-14-Voice-and-Judgment-planning.md`, and
`post-phase-14-pause.md`, and it **supersedes** the ML-planning doc's FO-6 linchpin (§2.1) and its
baseline-1-anchored referee (§3.1).
**Baseline:** Phase 14 closed on **baseline 2** — `replays/samples/{9p2i,4p1i}` (50 games each), `Qwen/Qwen3-32B`
(Featherless, $0), prompt set `qwen3_32b.v4` (`audits/audit-phase-14-close.md`).

## Evidence discipline

- **[VERIFIED]** — confirmed against code (`file:line`) or the committed replay bytes on current HEAD.
- **[INFERRED]** — a reasoned consequence of verified facts.
- **[PROPOSED]** — a design suggestion; nothing in the repo implements it.
- **[OPEN]** — asked about, does not exist, or could not be confirmed.
- **[RESEARCH]** — grounded in the external literature (cited inline; full list §11).

Where a prior artifact's claim is superseded by the committed bytes it is flagged **[STALE]**.

---

## 0. TL;DR — the one insight and the recommended path

**The owner's two asks are the same broken thing viewed twice.** [VERIFIED] The current design
(`experiments/lab/report-rubric-design.md:104-108`) makes the impostor's **inner-loop training fitness** equal
to the **FO-6 physical-suspicion-rank surrogate** — which *is* the no-LLM meeting model. That surrogate
**regressed top-1 64% → 26%** on baseline-2 ([V-ran] `post-phase-14-ML-planning.md:§8`), because baseline-2
moved ejections onto the **voice/zero-flag channel that is physically invisible**
(`post-phase-14-Voice-and-Judgment-planning.md:§2.2`, 82% of zero-flag convictions are soft-band). So
"reconstruct a better R-score" and "build an accurate no-LLM meeting sim" collapse into **one problem: the
training signal for a between-meetings policy is currently ungrounded.** Fixing it is the precondition for any
learner — you cannot train a genome against a fitness that mis-predicts the meeting three times out of four.

**Recommended path (this document argues it, in detail below):**

1. **Stop conflating three different things the word "R-score" is doing** (§3): a hard **validity gate**, a
   held-out **watchability referee** (the D1–D4 geomean), and the **tactically-reachable inner-loop fitness**.
   Build them as *separate, committed* artifacts. Two of the three do not exist as code today ([VERIFIED]).
2. **Do not train on "watchability/interestingness."** [RESEARCH] It is a fuzzy, Goodhart-prone scalar (the
   code itself calls it "a design-thread analyzer, NOT a shipped eval gate," `rubric_score.py:6-7`). Train
   instead on **measurable objectives**: side-specific **competence**, **KL-regularized toward an anchor
   policy** (piKL/CICERO — legible *and* strong without a fuzzy reward), **population-relative fitness**
   (PSRO/league — strength + diversity *emerge*, quality = exploitability), illuminated by **Quality-Diversity**
   (watchability becomes measurable behavioral *coverage*). Keep the geomean + validity as **gates**, never
   rewards (§4).
3. **Rebuild the meeting model as a ballot predictor that feeds the real deterministic tally** (§5), not a
   per-meeting ejection classifier — this structurally fixes FO-6's always-SKIP collapse. Evaluate it on
   calibration **and** ranking **and** top-k, by-game CV. Treat it as a **moving target** that must re-ground on
   real LLM meetings.
4. **Gather the data the corpus lacks** (§7): 118 committed ejections is thin; record more baseline-2 seeds
   ($0) and pin a frozen ML-calibration corpus.
5. **Sequence harness-first** (§8): the validity gate + referee productization is direction-agnostic and pays
   off no matter which optimizer wins — and, per the pause doc, is Phase-15 task-zero regardless.

Open owner decisions in §10; external grounding in §11.

---

## 1. Scope and method

**In scope:** the *measurement and simulation substrate* a learned tactical policy trains against — the
fitness/reward design ("R-score"), the no-LLM meeting model, and the tests + data to gather. **Out of scope:**
the LLM meeting layer itself (stays), and the policy architecture beyond what the training signal dictates
(covered in `post-phase-14-ML-planning.md`, which this doc complements — read it for the encoder/action-space/
provenance detail).

**Method.** Direct reads of `experiments/lab/rubric_score.py` + `rubric.md` + `report-rubric-*.md`,
`experiments/lab/ml_spike/` (esp. `core.py`, `fo5`, `fo6`), `meetings/{voting,manager,schemas}.py`,
`orchestrator/game.py`, `agents/memory/beliefs.py`, `eval/*`, `observation/*`, `agents/tactical/*`; the
committed replay bytes (corpus counts recomputed by re-reading `replays/samples/*/replay-seed-*.jsonl`); and
`pyproject.toml`/`uv.lock` for the dependency posture. External literature searched for the training-objective
and surrogate-fidelity questions (§11). Every claim is labelled per the discipline above.

---

## 2. What is actually broken (the linchpin), verified

**2.1 — The impostor's training fitness rests on a surrogate that no longer works. [VERIFIED]+[V-ran]**
`report-rubric-design.md:104-108` is explicit: the symmetric rubric is the *held-out selection gate*, and the
**inner-loop fitness is side-specific** — *"Impostor fitness = D3 craft, anchored on the FO-6 LLM-free
physical-suspicion rank (top-1 64%) as the $0 inner-loop objective."* The ML-planning doc re-ran FO-6 on the
committed baseline-2 corpus and got **top-1 26% / top-2 43%** (≈ base rate) — the corpus was re-recorded after
the spike and ejections shifted toward the voice/testimony channel. [INFERRED] **The impostor inner-loop
fitness is therefore currently ungrounded**, and everything downstream (S4 impostor training in the ML doc)
inherits that break.

**2.2 — Why the physical surrogate regressed is structural, not a tuning miss. [VERIFIED]** The crew's *entire*
deduction signal under same-room-only vision is "the impostor was seen where it shouldn't be" (112/112 committed
contradictions are `alibi_vs_sighting`, `post-phase-14-ML-planning.md:§6.2`). Baseline-2's fixes thinned the
flag channel and the untouched **zero-flag / voice channel rose to dominate** (22→31, and **82% of zero-flag
convictions sit at rendered suspicion 0.60–0.69 with no flag and no body-proximity** —
`post-phase-14-Voice-and-Judgment-planning.md:§2.2`). A physical surrogate reconstructs sightings and
kill-proximity; it **cannot see** a conviction that formed from spoken narrative momentum. So as the meeting
layer became more voice-driven, the physically-predictable fraction of ejections fell — exactly the FO-6
regression. [INFERRED] **This is a ceiling, not a bug: any physical surrogate has an irreducible error equal to
the voice-driven share of ejections.** §5.5 makes this the honest framing rather than a target to chase.

**2.3 — The measurement tooling the whole thing assumes is not committed code. [VERIFIED]** Reproduced from the
pause doc and re-checked: `scripts/validity_gate.py` and `scripts/measure_baseline.py` **do not exist**; there
is **no `__main__`/`argparse`/`def main` anywhere in `eval/`** — the metrics are library folds with no
one-command gate. The referee (`rubric_score.py`) self-labels *"a design-thread analyzer, NOT a shipped eval
gate"* (`:6-7`) and its calibration is anchored to **baseline-1 (v3), not baseline-2 (v4)**
(`report-rubric-interestingness.md:23`) — [STALE] for the committed bytes.

---

## 3. Reconstructing the "R-score" — separate three concerns the current design conflates

The word "R-score" is doing three incompatible jobs. Cleanly splitting them *is* the "from-scratch"
reconstruction; each piece then has a single, testable definition.

**3.1 — What exists today, verified.**
- **R1–R7** = directional design *targets* in prose (`experiments/lab/rubric.md`, v1; "last known" values are
  Wave-1/PR#147 — [STALE]). `rubric_score.py::score()` returns a scorecard of `(item, value, direction)` rows,
  **no scalar**. [VERIFIED]
- **The numeric fitness** = the **D1–D4 floor-gated weighted geomean**:
  `score = 100 × floor × exp(Σ wₙ·ln(max(Dₙ, ε)))`, weights `{D1 .40, D2 .25, D3 .15, D4 .20}`, `ε=1e-3`
  (`rubric_score.py:53-62, 472-486, 792-824`). D1 resolution (play decided vs the task clock), D2 crew
  deduction (suspicion separation + observation-backed conversion), D3 impostor craft (== `r2_deception`,
  effective deflection), D4 arc (cross-meeting suspicion movement). `floor∈{0,1}` → **0** on a
  firewall/determinism breach, a friendly-fire kill, or a **railroad** crew ejection (gate-bypass OR
  evidence-free conviction). [VERIFIED]
- Known Goodhart traps are **already closed** in the geomean (additive masking; R2 passive-survival gradient;
  R3 railroad-reward; R7 weak-flag counting), and R7 is structurally unreachable (0/50) so D1–D4 route around it.
  [VERIFIED] The geomean's *structure* is sound — this is genuinely a prior "from-scratch" reconstruction
  (`report-rubric-design.md`). The problems are (a) it's lab-tier not committed, (b) calibrated to the wrong
  baseline, and (c) it was never meant to be the training signal — which is where the break is.

**3.2 — The reconstruction: three artifacts, three jobs. [PROPOSED]**

| Concern | What it is | Job | Status today |
|---|---|---|---|
| **Validity gate** | Hard pass/fail on a set of games | Reject invalid/leaky/degenerate runs before anything is graded | [OPEN] — not committed |
| **Watchability referee** | The D1–D4 geomean, re-anchored to baseline-2, promoted to committed `eval/` | Held-out **selection** of champions; never a training reward | [OPEN] — lab-tier only |
| **Tactically-reachable fitness** | Side-specific, measurable, what a between-meetings policy can actually move | The **inner-loop training reward** | [OPEN] — the broken part |

- **Validity gate** — the criteria are audit prose (`audit-phase-14-close.md:§1`) that must become code by
  *wiring existing folds*, not writing new metrics: every game reaches `game_over`; 0 friendly-fire /
  betrayal-firewall breaches (`eval/win_condition_selfcheck.py`, `eval/leak_test.py`); **meeting-rate ≥ 0.60 and
  ≥ 30 resolved meetings** (`eval/meeting_quality.py::compute_meeting_rate`); 0 tick-1 kills; byte-identical
  replays (`scripts/verify_samples.sh`); exact provenance rows. *DoD:* one command, reproduces baseline-2 from
  committed bytes. [PROPOSED, ~80% wiring]
- **Watchability referee** — keep the geomean; **re-anchor** the D2 separation scale / D-thresholds to
  baseline-2 (currently baseline-1); **promote** `rubric_score.py` + the `r1_eject_decided_wins` fold
  (`extract_gameplay_facts.py:611`) + the R1 "ejection-driven win share" into committed `eval/`. It stays the
  **selection gate**, and — critically — the *adversarial Goodhart probe* (run ES directly on the geomean to
  see if a genome games it) must be run before it is trusted as a gate (§6, and the charter's un-run guardrail).
  [PROPOSED]
- **Tactically-reachable fitness** — FO-3 [VERIFIED] showed tactical play alone cannot move the
  meeting-controlled rubric terms (R1/R7 flat under fake meetings). So the inner-loop reward must be *reachable*:
  - **Impostor:** resolved kills + un-witnessed-ness (from `Killed.witnesses`, `engine/events.py:76`) + survival
    + meetings-survived + the surrogate-suspicion coupling (§5). Penalize being witnessed / venting-in-view.
  - **Crew:** task-completion progress + survival + correctly-routed reports + buddy/patrol coverage of
    last-seen suspects + D2 separation (crew's contribution to correct ejections).
  - **Both:** the win as the terminal sparse reward, plus **potential-based shaping** (Ng 1999, policy-invariant
    [RESEARCH]) toward legible setups so stealth optimization doesn't silently starve the meetings.

[INFERRED] This split is the load-bearing move: the *validity gate* protects integrity, the *referee* selects
for watchability without being gameable as a gradient, and the *reachable fitness* is the only thing the
optimizer ever maximizes — so the watchability↔stealth tension (§6) is resolved by construction, not hoped away.

---

## 4. The better answer to "watchability is hard to train on" (the owner's steer)

The owner is right to be skeptical: "interestingness" and "watchability" are exactly the kind of fuzzy,
hand-weighted objective the RL literature warns against — reward hacking **worsens with capability and shows
phase transitions** (Pan et al. 2022), and **no reward is fully hack-proof** (Skalse et al. 2022) [RESEARCH].
The repo's own code agrees: the geomean is "a design-thread analyzer, NOT a shipped eval gate," and the
grounding audit found the additive rubric "unsafe as raw Phase-C fitness (perverse R2/R3/R7 gradients)"
(`report-rubric-interestingness.md:9-11`) [VERIFIED]. **So don't optimize it. Optimize measurable things and
let watchability be a *gate* and an *emergent property*.** Four better-grounded objectives, in order of fit:

**4.1 — Anchor-KL-regularized competence (the single best answer). [RESEARCH]+[PROPOSED]**
Maximize a *measurable* objective (kills / survival / detection / win) while penalizing KL-divergence from an
**anchor policy** — the scripted FSM, or a behavior-cloned reference. This is exactly **piKL / CICERO**
(Bakhtin et al. 2022, arXiv:2210.05492) and **KL-regularized search** (Jacob et al. 2021, arXiv:2112.07544):
the result is *simultaneously more human-like and stronger* than either pure self-play or pure imitation. The
anchor **is** the watchability regularizer — you never write down "interesting," you constrain toward a
reference that already produces legible, contested play. This directly answers the owner's concern: **you don't
train on watchability, you train toward a legible anchor.** It also fits AiLibi's substrate perfectly — the FSM
is a free, queryable anchor (the DAgger oracle), and BC-init is already the ML doc's warm-start.

**4.2 — Population-relative fitness / PSRO / league. [RESEARCH]+[PROPOSED]**
Don't score against an absolute rubric; score against a **population of opponents**. Fitness = performance vs
the league; the rigorous quality metric is the **best-response / exploitability gap**, which is *measurable, not
fuzzy*. **Strength and behavioral diversity emerge** from the league (AlphaStar Nature 2019; OpenAI Five 2019
train 80% vs current pop / 20% vs frozen past; PSRO, Lanctot et al. 2017). AiLibi is *general-sum hidden-role
team*, so use the **correlated-equilibrium meta-solver PSRO** variant (Marris et al. 2021, arXiv:2106.09435) +
diversity oracles (arXiv:2106.04958) — **not** 2p-zero-sum Nash (which does not transfer; the ML doc's DeepRole
caveat). This is the honest "we want strong, varied, robust play" objective without hand-authoring what
"interesting" means.

**4.3 — Quality-Diversity / MAP-Elites (makes diversity measurable). [RESEARCH]+[PROPOSED]**
Reframe watchability as **behavioral coverage**: define behavioral descriptors — kill-timing distribution,
witness-exposure rate, meeting-trigger rate, vent-usage, task-cadence mimicry, win-shape — and *illuminate an
archive* of high-quality cells (Mouret & Clune 2015; deep-neuroevolution QD, Colas et al. 2020,
arXiv:2003.01825). "Quality" per cell is a real objective (win / exploitability); the *diversity* is the
watchability proxy, now a measured grid rather than a fuzzy scalar. **This structurally counters the
perfect-stealth monoculture** (§6): a stealth genome occupies *one* cell while MAP-Elites rewards filling the
others. MAP-Elites is also seed-robust and CPU-parallel (Nilsson & Cully 2021, arXiv:2009.08438) — it fits the
$0/determinism posture natively.

**4.4 — Learned reward / discriminator (a research probe, not the spine). [RESEARCH]+[PROPOSED]**
Distill an "is this game like the human-interesting baseline-2 corpus?" signal from the recorded bytes (+ an
optional small set of human interesting/boring labels — `DESIGN.md:947` already rosters the annotation tool).
GAIL/AIRL-style discriminator reward (Ho & Ermon 2016; AIRL, Fu et al. 2018) or a distilled-LLM-judge reward
(JudgeLM/PAD pattern). **Caveat:** GAIL/AIRL are training-unstable (C-GAIL, arXiv:2402.16349) and learned reward
models Goodhart — so use it as a *soft* auxiliary with the hard validity gate as backstop, not as the sole
reward.

**Recommended spine (they compose):** optimize **side-specific measurable competence**, **KL-anchored** to the
FSM/BC reference (legibility for free), inside a **population/PSRO** loop (emergent strength + diversity),
**illuminated by MAP-Elites** over watchability descriptors, with the **D1–D4 geomean + validity gate** as the
held-out selection filter. Nothing in that loop ever maximizes "interestingness."

---

## 5. The accurate no-LLM meeting simulation, rebuilt from scratch

**5.1 — Verified contract a surrogate must satisfy.** [VERIFIED] `MeetingRunner` is a `@runtime_checkable`
Protocol (`orchestrator/game.py:402-422`): `async run_meeting(*, meeting_id, trigger, state, agents) ->
MeetingArtifacts`; **must not mutate `state`**; return `MeetingArtifacts(result=MeetingResult, llm_calls=(),
prompt_versions={})` (game.py:372-399). The `MeetingResult` (`meetings/schemas.py:329-373`) must **echo
`trigger.triggered_by` / `trigger_tick` / `meeting_id`** (validated, game.py:907-943), obey the
outcome↔ejection coupling (schemas.py:363-373), and carry **one `VoteBallot` per living voter** or the
cross-meeting belief fold sees an empty roster (roster read off `result.ballots`, `meetings/manager.py:2823`).
Inject via `HeadlessGame(meeting_runner=<surrogate>)` (game.py:1136). `meeting_runner=None` is a truncation
(`MEETING_PHASE_REACHED`), **not** a fitness path (game.py:1257-1270) — the ML doc's §8.1 warning holds.

**5.2 — Why the prior surrogates failed, verified.**
- **FO-5 (rule-based §4.6 gate)** — [VERIFIED] `fo5_faithful_surrogate.py`: the committed flags are too weak to
  reach 0.60, so it has ~5% ejection recall (high SKIP precision, near-zero eject recall). A hand-rule surrogate
  cannot predict the ejections. Dead end.
- **FO-6 (learned logistic, 6 physical features)** — [VERIFIED] `fo6_learned_vote_surrogate.py` fits a
  pure-Python standardized logistic on `{witnessed, isolation, seen_at_kill, reporter, meeting-idx,
  alive-count}` per candidate. Two structural flaws: (a) the features are thin; (b) its **binary eject-vs-SKIP
  decision collapses to always-SKIP** (the report notes this) — the SKIP/eject decision is testimony/plurality
  driven and *absent* from physical features. Its single top-1 number *hid* the always-SKIP failure.

**5.3 — The rebuild: predict BALLOTS, feed the REAL tally. [PROPOSED]**
The deterministic tally `tally_ballots(ballots, skip_confidence_threshold=0.60)` (`meetings/voting.py:120-213`)
is [VERIFIED] pure and LLM-free: plurality + SKIP-first-class + tie→SKIP + a confidence≥0.60 gate on the
leader's max ballot. **So the surrogate's job is not to predict the ejection — it is to predict each living
voter's ballot `(target, confidence)`, and let the real tally produce the outcome.** This is the key structural
fix:
- It **eliminates the always-SKIP collapse**: the SKIP/eject decision now emerges from the real
  plurality+confidence tally, not from a mis-calibrated binary head.
- It **restores belief persistence**: one ballot per voter is exactly what the fold's roster needs (§5.1).
- It is **finer-grained supervision**: N ballots/meeting instead of 1 label — more signal from the same 118
  ejections (the corpus records every ballot: `voter, target, confidence, primary_reason_id, rationale_text`
  — [VERIFIED] `replay.py`/`schemas.py:257-271`).

**5.4 — Richer features (the belief fold is free and offline). [VERIFIED substrate]+[PROPOSED features].**
The single biggest upgrade over FO-6: reconstruct the **full pre-meeting per-voter suspicion graph** offline.
The belief fold (`agents/memory/beliefs.py`) is LLM-free and replay-deterministic, and
`derive_belief_evidence` (manager.py:2680) re-derives the exact graph the LLM saw — **no LLM needed**. Feature
set per (voter, candidate): rendered suspicion from the belief graph; contradiction structure (strong +0.3 /
weak +0.08 flags naming the candidate); sighting / co-presence graph (`core.reconstruct`,
`ml_spike/core.py:222-288`); reporter identity + role; kill-proximity and isolation-over-time; movement
anomalies; task-completion cadence. The belief-fold rendered suspicion alone is a far stronger predictor than
FO-6's six raw counts, because it *already integrates* the accumulators the LLM votes on.

**5.5 — Evaluate it properly, and know its ceiling. [RESEARCH]+[PROPOSED].**
FO-6's one top-1 number was misleading. The fidelity harness must report, **by-GAME cross-validation** (never
by-meeting — leakage):
- **Ejection ranking** — top-1 / top-2 match of the ejected player (the continuous suspicion-rank signal).
- **SKIP-vs-eject accuracy** — the decision FO-6 failed at (now delegated to the real tally on predicted
  ballots).
- **Calibration** — Brier score and ECE on the ballot confidences. **Brier and ranking measure different
  things** (Brier is numeric-probability fidelity; AUROC/rank is ordering — arXiv:2504.18278; WOLF reports
  Brier ~0.26–0.29 for exactly this kind of werewolf vote prediction, arXiv:2512.09187) — report both.
- **Honest ceiling (§2.2):** the surrogate's error floor = the voice-driven share of ejections it structurally
  cannot see. So the plan does **not** chase a high top-1 number. Two responses: (a) use the surrogate for the
  physically-legible component + a **periodic real-LLM selection gate** for the rest; (b) accept that the
  surrogate's main job is the meeting-outcome **coupling** (who is ejected → parity/win), and lean the training
  reward on the tactically-reachable signals (§3.2) that don't depend on it.

**5.6 — The surrogate is a moving target — re-grounding is mandatory. [RESEARCH]+[VERIFIED history].**
FO-6 already regressed once on a re-record (§2.1). A learned *mover* changes the sighting/contradiction
distribution *by construction*, and any meeting-layer change moves the vote distribution. So (model-based-RL
model-exploitation, MBPO/Dreamer): **never train indefinitely against a frozen surrogate.** Periodically call
the real LLM to re-anchor (a DAgger/active-learning loop on the meeting model), re-calibrate after **any** mover
or meeting-layer change, and pin a **frozen "ML-calibration corpus"** as an explicit release artifact separate
from the LLM-prompt baseline (the ML doc's owner-question Q5).

**5.7 — Bonus: the same corpus distills into a cheap reward.** [PROPOSED] The recorded LLM ballots are also
training data for a distilled-LLM-judge reward (§4.4) — one corpus, two uses (surrogate + reward), one Goodhart
backstop (the validity gate).

---

## 6. The deepest risk this signal design must hold: a strong learner, not a weak one

[VERIFIED]+[INFERRED] The social game currently rides on the impostor being *forced* to garble testimony and on
its imperfect stealth (kills 3.75% crew-witnessed, take-rate 0.48 — `post-phase-14-ML-planning.md:§4`). A
learned impostor that achieves *perfect* stealth produces **no flags → meetings starve of testimony →
R1/R5/R7 collapse → the deduction game un-makes itself.** This is the game-theoretic norm — optimal
imperfect-information play is randomized, minimally-communicative, illegible ("secret handshakes," Pluribus's
"alien" strategies) — and the field's response is exactly **human-regularization** (CICERO; piKL; "Winning
Isn't Everything," Zhao et al. 2020) [RESEARCH]. The training-signal design in §3–§4 is built to hold this:
- The **anchor-KL** term (§4.1) directly penalizes drift away from legible FSM-like play.
- **MAP-Elites** (§4.3) makes perfect-stealth occupy one archive cell instead of dominating.
- The **watchability referee + validity meeting-rate bar** are **hard selection GATES** (`rubric_score.py:823`
  geomean is multiplicative → a meeting-starved game floors to ~0 by construction, [VERIFIED]), so a champion
  that wins more by starving meetings is *rejected*, not selected.
- **Potential-based shaping** (§3.2) pulls toward legible setups without changing the optimum.

[INFERRED] This is why the reward must be measurable-competence + anchor + gate, and never the fuzzy
watchability scalar: optimizing "interesting" directly is both un-trainable *and* the exact thing that, taken to
its optimum, destroys interestingness.

---

## 7. Tests and data to gather

**7.1 — Tests to build (most do not exist; [OPEN] unless noted).**
1. **Validity gate** — committed one-command pass/fail wiring the existing folds (§3.2). [OPEN]
2. **Watchability referee** — productized + re-anchored to baseline-2 from `rubric_score.py` +
   `extract_gameplay_facts.py`. [OPEN]
3. **Surrogate fidelity harness** — top-1/top-2 + SKIP-accuracy + Brier/ECE + rank-corr, by-game CV (§5.5). [OPEN]
4. **Determinism harness for a learned policy** — extend the spike's Check-1 / `eval/determinism_test.py` to
   hash the **encoder-vector + logits** (not just `WorldState`), with quantize + lexical tie-break. [OPEN]
5. **`eval/leak_test.py` accepts an `agent_factory`** — [VERIFIED] today it runs 3 scripted fixtures with no
   factory; a learned agent drives regions those fixtures never reach. [OPEN — both prior docs list this]
6. **Reward instrumentation** — surface a per-tick reward vector as env `info` (kills, witnessed-ness, task
   progress, coverage) from the 14 engine event types (`engine/events.py`), so ES/QD don't re-derive from
   replay. [OPEN]
7. **Tactically-reachable vs meeting-controlled decomposition** — a fold that reports which reward terms a
   tactical learner can move (formalizes FO-3). [OPEN]
8. **Gym/PettingZoo-Parallel wrapper contract test + `legal_actions` mask** — from the pure `rules.py`/`tick.py`
   predicates; note the two non-packet legality inputs (emergency-uses-remaining, map sabotage kinds) the ML doc
   §5.1 flags. [OPEN]
9. **Watchability/Goodhart adversarial probe** — run ES *directly on the geomean* to surface exploits before
   trusting the referee as a gate (the charter's un-run guardrail). [OPEN]

**7.2 — Data to gather.**
1. **More real-LLM meeting data (the biggest gap).** [VERIFIED] the corpus is thin — **9p2i: 142 meetings /
   118 ejections / 24 skips; 4p1i: 39 meetings / 13 ejections / 26 skips** (recomputed from committed bytes);
   FO-6 trained on 35 games. A learned ballot model + calibration needs more. Record additional
   baseline-2-config seeds (`Qwen/Qwen3-32B` v4, Featherless, **$0**) into a by-game train/val/test split.
2. **A flat per-meeting training table** — reconstructed physical + belief-fold features + actual
   ballots/ejection + `roles` ground truth (extend `core.reconstruct` + `extract_gameplay_facts`). The
   `tournament-eval-report.json` already carries per-game `roles` (impostor ground truth) and the
   report/emergency trigger kind. [VERIFIED substrate]
3. **A frozen "ML-calibration corpus"** pinned as a release artifact, separate from the LLM-prompt baseline (§5.6).
4. **A re-grounding corpus / cadence** — the ability to record fresh real-LLM meetings on demand for DAgger
   re-anchoring.
5. **Optional human interesting/boring labels** — a small set to train/validate the watchability discriminator
   (§4.4; `DESIGN.md:947`).
6. **Self-play rollouts + behavioral-descriptor logs** — generated $0 during training; the MAP-Elites archive
   substrate.

---

## 8. Staged plan (algorithm-agnostic stages first; the phase-15 skeleton)

Sized like this repo's phase tasks; S0–S3 pay off no matter which optimizer wins. This is the **skeleton a
later `tasks/phase-15.md` formalizes** once §10 is decided.

- **S0 — Productize the gate (no learning).** Committed **validity gate** + **D1–D4 referee** re-anchored to
  baseline-2, reproducing every baseline-2 number from committed bytes. Wire existing folds; don't re-implement.
  *This is Phase-15 task-zero regardless of direction* (the pause doc §2.1). *DoD:* one command, reproduces
  baseline-2. **[Algorithm-agnostic]**
- **S1 — Training harness.** Gym/PettingZoo-Parallel wrapper over `agent_factory` (zero engine edits) +
  `legal_actions` mask + policy-id/weights-hash provenance stamp (mirror `substrate_flags`) + reward-vector
  `info` channel. *DoD:* a random-genome policy runs, mask is exact, replays reconstruct byte-identically + carry
  the stamp. **[Algorithm-agnostic]**
- **S2 — Memory-carrying encoder + determinism/leak harness.** Extend the 34-dim encoder with belief/last-seen
  features (BC-init needs memory, §the spike's cap); hash encoder+logits; quantize + lexical tie-break;
  `leak_test` accepts an `agent_factory`. *DoD:* byte-identical same-machine + leak-clean. **[Algorithm-agnostic]**
- **S3 — Rebuild the no-LLM meeting model (GO/NO-GO).** Ballot-prediction surrogate → real tally (§5.3); rich
  belief-fold features (§5.4); proper fidelity eval (§5.5); documented re-grounding cadence + frozen calibration
  corpus (§5.6). *Gate:* a stated fidelity bar or a documented fallback (learned vote surrogate / periodic
  real-LLM selection gate). **[Training-specific but foundational]**
- **S4 — First learned policy, both sides.** Learned scorer over the FSM's legal options, BC/DAgger-init,
  **anchor-KL-regularized** (§4.1), ES-refined on the S3 fitness against the frozen FSM. Watchability gate live
  from the first champion. *DoD:* beats the FSM on take-rate/win without failing S0. **[Training-specific]**
- **S5 — Population + Quality-Diversity.** MAP-Elites over behavioral descriptors (§4.3) + PSRO/league relative
  fitness (§4.2); referee-as-selection + the adversarial Goodhart probe (§7.1.9). **[Training-specific]**
- **S6 — Bounded co-evolution / torch ceiling (deferred).** Shared role-conditioned policy + Hall-of-Fame +
  PFSP + reduced virulence; PPO + recurrent only if S4–S5 ceiling out, behind the record-path determinism
  mitigation. **[Deferred]**
- **S7 (owner-gated, orthogonal) — structural-information levers** (sabotage/vents/vision) that give richer
  learned tactics something legible to produce and lift the ~45% detection ceiling. **[Not ML; owner call]**

---

## 9. Dependency / ML-stack recommendation

[VERIFIED] The repo is **strictly pure-Python** today (pydantic/fastapi/jinja2/ollama/anthropic; **no
numpy/torch/sklearn/gymnasium anywhere in `uv.lock`**) — that is what makes it $0 and byte-deterministic. The
owner is open to all three tiers and curious about a torch experiment. Recommendation: **staged escalation, so
determinism is never silently lost.**
- **Start pure-Python + numpy** (ES / MAP-Elites + a pure-Python-or-numpy surrogate): preserves $0 +
  byte-determinism, CPU-parallel, seed-robust (arXiv:2009.08438), validates the harness cheaply. This carries
  S0–S5.
- **Graduate to torch** only for the population-based ceiling (PPO + PSRO/league + recurrent POMDP memory),
  behind the **record-path determinism mitigation** (cross-machine float bit-identity is otherwise unattainable
  — FP non-associativity, arXiv:2408.05148). This is the "interesting experiment" the owner wanted, sequenced
  after the pure-Python path demonstrably ceilings.
- **Surrogate model choice:** gradient-boosted trees (sklearn/lightgbm) are best-calibrated on small tabular
  data (arXiv:2305.02997) but need integer-threshold care for determinism; a **pure-Python multinomial logistic
  / tiny MLP is the determinism-safe default**. Recommend numpy-tier for the surrogate; reserve torch for the
  policy ceiling. [RESEARCH]+[PROPOSED]

---

## 10. Open decisions for the owner

1. **Dependency ceiling per stage** — numpy now; torch when (only after S4–S5 ceiling, or sooner for the
   experiment)?
2. **Primary paradigm confirmation** — the §4 spine (measurable competence + anchor-KL + PSRO + MAP-Elites,
   watchability as a gate). Any objection to dropping "interestingness" as a trained scalar entirely?
3. **Watchability contract** — is a rise in impostor win-rate from *smarter* play acceptable, and up to what
   ceiling, provided the meeting-rate / R5 / R7 gates hold?
4. **Recording spend** — approve recording additional baseline-2 seeds ($0 wall-clock only) to thicken the
   surrogate corpus, and pin a frozen ML-calibration corpus?
5. **Both-sides-in-parallel** (owner's stated preference) vs impostor-first if compute binds — confirm.
6. **Anchor choice** — regularize toward the scripted FSM, a behavior-cloned FSM, or (later) the human labels?
7. **Also stub `tasks/phase-15.md`** from the S0–S7 skeleton now, or wait until the above are locked
   (recommended: wait).

---

## 11. Method, reproduction, and references

**Reproduction.** Corpus counts: re-read every `replays/samples/{9p2i,4p1i}/replay-seed-*.jsonl`, tally
`kind=="meeting"` by `outcome` → 9p2i 142/118/24, 4p1i 39/13/26. Absent scripts: `find` for
`validity_gate.py`/`measure_baseline.py` → none; grep `eval/` for `__main__|argparse|def main` → none.
Geomean/surrogate facts read directly at the cited `file:line`. Dependency posture: `pyproject.toml` +
`uv.lock` grep for numpy/torch/sklearn/gymnasium → none.

**Key in-repo artifacts.** `experiments/lab/rubric_score.py` + `rubric.md` + `report-rubric-design.md` +
`report-rubric-interestingness.md` (the referee); `experiments/lab/ml_spike/{core,fo5_faithful_surrogate,
fo6_learned_vote_surrogate}.py` (the surrogate probes); `meetings/{voting,manager,schemas}.py` +
`orchestrator/game.py` (the meeting contract); `agents/memory/beliefs.py` (the offline belief fold);
`eval/*` (the folds to wire); `audits/post-phase-14-ML-planning.md` (the substrate map this complements).

**External references.** Human-regularization / anchor-KL: piKL & CICERO (Bakhtin et al. 2022,
arXiv:2210.05492; Meta Science 2022), KL-regularized search (Jacob et al. 2021, arXiv:2112.07544), "Winning
Isn't Everything" (Zhao et al. 2020). Population / league / PSRO: AlphaStar (Nature 2019), OpenAI Five
(arXiv:1912.06680), PSRO (Lanctot et al. 2017, arXiv:1711.00832), general-sum CE meta-solvers (Marris et al.
2021, arXiv:2106.09435), behavioral+response diversity (arXiv:2106.04958). Quality-Diversity: MAP-Elites
(Mouret & Clune 2015), deep-neuroevolution QD (Colas et al. 2020, arXiv:2003.01825), MAP-Elites vs PPO
determinism/CPU (Nilsson & Cully 2021, arXiv:2009.08438). Learned reward / imitation: GAIL (Ho & Ermon 2016),
AIRL (Fu et al. 2018), C-GAIL stability (arXiv:2402.16349), distilled LLM-judge (JudgeLM / PAD). Reward hacking:
Pan et al. 2022 (arXiv:2201.03544), Skalse et al. 2022 (arXiv:2209.13085), potential-based shaping (Ng, Harada
& Russell 1999). Surrogate fidelity: Brier-vs-ranking calibration review (arXiv:2504.18278), WOLF werewolf
deception (arXiv:2512.09187), GBM-vs-NN on tabular (arXiv:2305.02997). Determinism: FP non-associativity
(arXiv:2408.05148). Model-based-RL exploitation: MBPO (Janner et al. 2019), DreamerV3 (Hafner et al. 2023).
