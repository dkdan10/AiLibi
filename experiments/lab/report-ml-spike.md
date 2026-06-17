# ML Feasibility Spike — Results

> Charter: `experiments/lab/ml-spike-charter.md`. Code: `experiments/lab/ml_spike/`.
> $0, offline, pure-Python (no deps), ZERO engine edits. All three checks RAN with
> real numbers on the committed 9p2i substrate. This is the go/no-go memo.

## Headline

| Check | Result | Verdict |
|---|---|---|
| **1 — Determinism** (cornerstone) | 8/8 byte-identical replays + state-hash chains across two runs of a frozen genome; 8/8 load-bearing (genome ≠ FSM) | **PASS** |
| **2 — Learnability** | ES climbs kills **17 → 32** in-sample; held-out edge **+13** survives (champ 24 vs random 11, FSM 36) — generalizes | **PASS** |
| **2 — Bootstrap** | behavior-clone of the FSM: 60% move-parity, 22 kills (< FSM 37) — but the interpretation is confounded (see gaps) | **PARTIAL / inconclusive** |
| **3 — Surrogate fidelity** | detector tally predicts the ejection **56%** unconditional, **71% (22/31)** when a flag exists; 8/39 ejections have NO flag (testimony-driven) | **BELOW BAR** as a naive rule; the faithful pipeline was not graded |

**Overall: GO on the SUBSTRATE; the ML BET is NOT yet de-risked.** A two-skeptic
adversarial pressure-test (below) revised the original "conditional GO." What is
genuinely established: the injection seam works with **zero engine edits**, the engine
stays **byte-deterministic given recorded actions** (replay is structurally immune; a
pure-Python float MLP in the live-record loop is byte-identical same-machine), **$0
~20 games/s** throughput is real, and a **dense decision is learnable and generalizes**.
What is NOT established — and is what Phase C actually rides on — are three structural
questions the spike deferred: **sparse-lever learnability (kill/vent/sabotage), co-
evolution stability, and a climbable Goodhart-resistant rubric fitness.** See the gap
table; four cheap follow-on experiments should run BEFORE committing Phase C.

## What ran

- **Decision learned:** the impostor MOVE choice (frequent, always-legal). A proxy
  `AgentInterface` calls the real FSM `TacticalAgent`, then overrides ONLY a Move/Wait
  intent with a pure-Python MLP's pick among `{stay} ∪ adjacent` rooms; everything else
  (kills, vents, cover, do_task, and the whole meeting protocol) delegates to the inner
  agent unchanged. Injected through the existing `agent_factory` param — no engine edits.
- **Fitness:** total impostor kills over 8 seeds (random moves wreck the FSM stalk:
  FSM 37 vs random 17 over 8 seeds → a real gap to climb, non-degenerate).
- **Speed:** ~0.06 s/game with `AILIBI_LLM_PROVIDER=fake` (the ~900-game Check-2 run is
  ~60 s, single core), confirming the training-throughput assumption. $0.

## Check 1 — Determinism (PASS, decisively)

`check1_determinism.py`: 8 seeds, each run twice with the same frozen random genome.
**8/8 byte-identical replay files, 8/8 identical per-tick state-hash chains**, and 8/8
load-bearing (the genome run differs from the FSM run — so the pass is not the trivial
"the MLP changed nothing"). A float MLP argmax can drive recorded actions and the engine
stays byte-deterministic.

**Caveat (see pressure-test):** this used *pure-Python* IEEE-754 inference on ONE machine
in-process. It proves the *concept*; it does NOT prove a numpy/GPU production path is
cross-machine deterministic. Replaying a recording is immune regardless (the recorded
discrete action is authoritative); only live re-record is exposed, and the mitigation
(integer/quantized logits + lexical tie-break, kept tiny) is the documented fallback.

## Check 2 — Learnability + bootstrap (PASS / PARTIAL)

`check2_learnability.py`, 8 fitness seeds:
- **ES (learnability): 17 → 23 → 27 → 32** over 12 generations (a simple (1+9)-ES,
  Gaussian mutation σ=0.15). Monotonic climb to **32/37 = 86% of the hand-tuned FSM
  ceiling** from a random start. Learning works on the real harness.
- **Bootstrap (BC): 389 impostor move-decisions, 60% held-out top-1 move-parity, 22 kills.**
  Better than random (17) but short of FSM (37) — **does not reach parity.**

**The informative bit:** ES (32, optimizing the *outcome*) BEAT BC (22, cloning the FSM
from a single-tick encoding). The FSM's move policy is *history-dependent* (it stalks on
sightings accumulated over ticks); a **memoryless** encoder structurally cannot represent
it, so the clone caps out — exactly the "visible-subset → full-roster reconstruction needs
recurrence/memory" point from the obs audit, now empirical. Phase C's encoder must carry
memory features (the existing `MemoryStore` already accumulates them); BC-init then
becomes viable. It also confirms blindspot #2 the hard way: from-scratch underperforms the
hand-tuned FSM (86%), so BC-init matters — but only with memory.

## Check 3 — Surrogate fidelity (BELOW BAR — a real finding)

`check3_surrogate.py`, committed 9p2i (114 meetings: 39 eject / 75 SKIP):
- **Naive contradiction-tally → top subject:** ejection top-1 match **22/39 = 56%**,
  precision-when-it-names-someone 41%, SKIP agreement 69%, overall 65%.
- **Strong-only gate (drop weak signals):** **0/39** — every committed contradiction is a
  weak signal, so strong-gating predicts SKIP always (100% SKIP, 0 ejections).

56% beats random (~12% over ~8 alive) but is **below the ~75% bar**: the deterministic
detector flags only loosely drive the real ejection, because the outcome is an LLM
plurality vote keyed on more than raw flag counts. **Implication:** a cheap rule-based
surrogate cannot carry the training inner loop alone — Phase C needs a *learned* surrogate
(behavior-clone the LLM votes/transcripts) or must lean on a periodic real-Ollama
selection gate. Two flags for the pressure-test: (a) this tensions with the Phase-10
"listeners vote the flags" narrative — the coupling is looser than that implied; (b) 56% is
a *lower bound* for a naive tally — a smarter deterministic surrogate (§4.6 gate logic +
accumulator + co-location) might do better and was not tried.

## Settled data model (for Phase C)

- Encoder: fixed map (10 rooms/12 tasks/6 vents) onehot + per-room player/body counts +
  scalars (cooldown, in_vent, tasks%, sabotage) = 34 dims — **plus memory features (TODO,
  Check-2 finding).**
- Net: tiny MLP, **pure-Python or quantized** CPU inference for determinism (Check-1).
- Optimizer: **ES first** (climbs cleanly; NEAT deferred). BC-init once the encoder has memory.
- Fitness: real objective = rubric (not kills); kills was the spike proxy.
- Surrogate: **learned, not rule-based** + real-LLM gate (Check-3).

## Pressure-test: gaps that gate Phase C (two adversarial skeptics + held-out re-run)

Confirmed solid (tried to break, could not): the injection seam + zero engine edits; the
RNG-shift confound does NOT exist (engine draws one int/tick, discarded; policies use no
RNG); the BC backprop is numerically correct (finite-diff 2.2e-10); fake meetings never
eject (kill fitness is clean); `count_kills` is correct; the ES climb GENERALIZES held-out
(edge +16 in-sample → +13 on disjoint seeds). So the *plumbing* is real.

But the verdict's weight must match what was tested. The spike de-risked the EASY parts
(dense decision, frozen opponent, dense proxy fitness) and deferred the three structural
questions Phase C is DEFINED by:

| # | Gap | Severity | Why the spike gives false confidence | Cheapest de-risk ($0, hours-days on this harness) |
|---|---|---|---|---|
| 1 | **Move-only → whole policy** | BLOCKER | Move is dense/every-tick/smooth; the value is the SPARSE conjunctive kill/vent/sabotage levers (the Phase-11 economy) + the ~42-slot masked head, never built | Learn the **kill-timing gate** end-to-end (BC-init from `_scored_targets`), kills fitness |
| 2 | **Co-evolution untested** | BLOCKER | Clean climb was vs a FROZEN FSM crew; Phase C co-evolves both sides — cycling/Red-Queen/disengagement untouched | **2-population alternating-ES** cycling probe + Hall-of-Fame, plot vs a fixed held-out opponent |
| 3 | **Rubric Goodhart / fitness mismatch** | BLOCKER | Optimized dense kills; real fitness is a sparse per-game scalar ~80% controlled by the unlearned meeting layer (R1 pinned 0/50), and the only tactically-reachable term R7 rewards flag *presence* (gameable) | Run ES on the literal `_game_interestingness` + **eyeball** the top genome's games |
| 4 | **Memory-encoder re-opens Check 1** | MAJOR | Determinism proven on the memoryless encoder the report itself rejects; `BeliefState` float residue + dict-insertion-order `known_players()` as encoder inputs can flip the argmax; the WorldState-only hash wouldn't even catch a divergence that argmaxes the same room | Re-run Check 1 with a memory-augmented encoder, hash the **encoder vector + logits**, apply quantize+lexical-tie-break |
| 5 | **Surrogate is a moving target** | MAJOR | 56% (already <bar) was on FSM-generated replays; a learned mover changes the sighting/contradiction distribution by construction, and the planned testimony-ingestion repair adds an ejection channel the tally can't model | BC a **learned vote-surrogate** from committed ballots, measure ITS top-1; re-measure after the meeting repair |
| 6 | **Pure-Python won't scale** | MAJOR | Check 1's clean PASS is bound to pure-Python; Phase-C scale forces numpy/GPU, which re-opens cross-machine float determinism | Port `mlp_forward` to numpy, re-run Check 1 same-machine with the quantization mitigation applied |
| 7 | **Firewall untested w/ a custom agent** | MINOR | Holds by construction (inner agent has no engine ref; encoder reads only packet), but leak tests never run an `agent_factory` | Extend `test_leak_property` to accept a factory; run the spike/Phase-C factory through it once |

Corrections folded in from the pressure-test: the ES headline is in-sample (held-out edge
+13, real but smaller); the "ES beat BC ⇒ memoryless" inference is **confounded** (train/test
leak + objective mismatch + the encoder discards target IDENTITY, not just history — `core.py`
stores per-room counts only, but the FSM stalks specific targets), so BC's verdict should be
held-out move-parity, not kills; Check 3's 56% is floored by 8 zero-flag (testimony-driven)
ejections → 71% given a flag exists, and the naive tally is a strawman vs the real belief-
fold + 0.60-gate pipeline, which was NOT graded — so "must go learned" is not yet earned.

**Reframed bottom line:** the spike succeeded at its real job — it proved the substrate
plumbing AND converted a vague "build ML" into four crisp, cheap go/no-go experiments
(sparse-lever ES, 2-pop cycling probe, rubric-fitness ES + eyeball, numpy Check-1) plus
grading the faithful deterministic surrogate. Run those before a Phase-C commit; each can
independently turn the GO into a real GO or surface the NO-GO on a throwaway, not after a
phase.

## Follow-on probes — RESULTS (`fo1`–`fo5`, all $0, ran)

| Probe | Gap | Result | Closes gap? |
|---|---|---|---|
| **FO-4 determinism at scale** | 4, 6 | stateful/memory encoder byte-identical (2 runs); **216 per-decision logit hashes bit-identical** (a sub-argmax divergence can't hide); numpy backend agrees w/ pure-Python on 0/46 real states | **YES** (same-machine); only cross-MACHINE residual → quantize+lexical-tie-break |
| **FO-1 sparse lever** | 1 | move lever gated to post-kill only (~13 dec/game): ES drove exposure 117→66 (**below FSM 105** in-sample), **23% below random held-out** | **MOSTLY** — sparse-gated positional learning climbs; the pure binary take-vs-hold gate still not isolated |
| **FO-3 rubric fitness** | 3 | kills swing 2.4× (24→57) but R1/R7 **flat at 0** under fake meetings — tactical play can't move the rubric without the meeting layer | confirms the **mismatch**: rubric-fitness REQUIRES a real/surrogate meeting layer in the loop |
| **FO-5 faithful surrogate** | 5 | naive tally over-predicts (56% recall / 41% prec); faithful 0.60 gate under-predicts (**5% recall / ~100% prec / 100% SKIP**) — LLM ejections are testimony/plurality-driven, beyond the deterministic layer | **NO** — a rule-based surrogate can't predict ejections; needs a **learned vote-surrogate** (BC the ballots) or real-LLM gate |
| **FO-2 co-evolution** | 2 | naive 2-pop opposing-fitness ES **collapsed to a degenerate equilibrium in round 0** — crew trivially denies all kills (coevo 0 every round; evolved crew zeroes even the FSM impostor), impostor gets **zero gradient** (disengagement) | **NO** — co-evolution is unstable in the naive setup; needs balanced objectives + rubric-referee + Hall-of-Fame + a fuller-than-move policy |

**The follow-ons localize the risk into ONE coupled problem.** The *tactical-ML mechanics
are de-risked*: determinism is robust same-machine even with a stateful encoder + numpy
(FO-4), and both dense (Check 2) and sparse-gated (FO-1) decisions learn and generalize.
The risk concentrates in a **dependency chain**: rubric-fitness (the real objective) is
inert without the meeting layer (FO-3) → real LLM meetings are too slow for the inner loop
→ a surrogate is required → the *deterministic* surrogate can't predict the LLM's ejections
(FO-5) → so a **learned vote-surrogate** is the linchpin → and only with a faithful fitness
can co-evolution avoid the degenerate collapse FO-2 exhibited.

**Consolidated verdict (pre-FO-6): GO on the tactical substrate; the linchpin for Phase C is a
learned meeting/vote surrogate.** That spike was then run — FO-6 below.

## FO-6 — the LINCHPIN: a learned vote-surrogate (RAN)

`fo6_learned_vote_surrogate.py`, supervised, by-GAME split (35 train / 15 test, 11 test ejections).

**Reframe found first:** ALL 112 committed contradictions are alibi-based (`alibi_vs_sighting`
111 / `alibi_conflict` 1) — every flag needs the LLM's spoken alibi, so a *truly* no-LLM
surrogate has **zero flags**. The "deterministic detector" of FO-5 isn't available at training
time. So the honest test is a surrogate on **LLM-free physical features** — positions
reconstructed from the action stream → sightings, proximity-to-kill, reporter.

| Learned surrogate | RANK top-1 (vs naive 56%) | RANK top-2 | binary eject/SKIP |
|---|---|---|---|
| flag features (needs the LLM) | **73%** (beats the 56% tally) | 82% | collapses to SKIP |
| **physical features (LLM-FREE)** | **55%** (≈ the LLM-flag tally) | **82%** | collapses to SKIP |

**Findings:** (1) learning beats hand-tallying on the flag signal (73% vs 56%); (2) crucially,
the **LLM-FREE physical surrogate ranks the ejected player in its top-2 82% of the time** (top-1
55%) — matching the LLM-flag signal's top-2 and crushing FO-5's 5% rule-based gate. The "who is
suspicious" signal IS recoverable deterministically from reconstructed sightings. (3) The only
collapse is the **binary eject-vs-SKIP** calibration (both surrogates predict SKIP under an
accuracy-tuned threshold) — that decision is testimony/plurality-driven and not in the physical
state.

**What this changes:** the surrogate is **viable for the impostor side** — but as a **continuous
LLM-free suspicion-RANK** (82% top-2), not a binary ejection predictor. That is exactly the
Phase-11 information-economy thesis as a trainable fitness: *the impostor's objective = minimize
its own learned physical-suspicion rank*, $0 with no LLM in the inner loop. The binary meeting
OUTCOME (and the crew-side "eject correctly" fitness) is the part that still wants a real-LLM
selection gate. Caveats: small test (11 ejections, ±~15%); 6 simple features (a richer sighting
graph likely lifts it); calibrated on FSM-generated play so it's a moving target under learned
impostors (standing re-calibration) — but now there is a concrete, faithful thing to calibrate.

## Final consolidated verdict (after spike + 6 follow-ons)

**GO on the tactical substrate, and the linchpin is now substantially green — with one residual
design problem.**
- **De-risked:** injection seam (0 engine edits); byte-determinism robust same-machine even with
  a stateful encoder + numpy (Check 1, FO-4); dense AND sparse-gated decisions learn + generalize
  (Check 2, FO-1); $0 ~20 games/s.
- **Linchpin (surrogate) — viable as a continuous LLM-free suspicion-rank fitness** (FO-6, 82%
  top-2). The impostor side — the primary Phase-11 lever — is trainable cheaply offline; use a
  real-LLM gate only for the binary outcome / crew side.
- **Still open — co-evolution stability** (FO-2 collapsed naively). Now THE remaining Phase-C
  design problem, but it has a faithful continuous fitness (FO-6) to build on, with balanced
  objectives + rubric-as-referee + Hall-of-Fame + a fuller-than-move policy.
- **Rubric (FO-3):** inert without the meeting layer, but the FO-6 suspicion-rank is the
  tactically-reachable proxy for the impostor's contribution to it.

**Phase-C entry recommendation:** build the LLM-free suspicion-rank surrogate into the inner loop
and train the impostor tactical policy against it (real-LLM gate for selection); prototype co-
evolution on top of that faithful fitness; keep the binary/crew outcome on the real-LLM gate
until a learned binary calibrator clears a bar. The feasibility question is answered **yes for
the impostor-tactical half**; the open work is co-evolution engineering, not feasibility.
