# ML Feasibility Spike — Charter

> Status: PLAN ON PAPER (no code yet). This is the de-risk gate for the ML-agents
> direction. It is $0, offline, design-thread, and intentionally throwaway. It
> produces a **go/no-go + a settled data model**, nothing shippable.

## Why this exists (the gate)

The plan is to replace the hand-written **tactical** FSM policies
(`agents/tactical/impostor_policy.py`, `crewmate_policy.py`) with a learned
(neuroevolution) policy, **keeping the LLM meeting layer**. Before committing the
full ML build (Phase C) or letting it shape the front-end (Phase D), three
assumptions must be proven cheaply, because each one, if false, changes the whole
direction — and learning that *after* a phase commit is expensive. Three prior
read-only audits established the substrate is ML-ready at the tactical layer
(clean policy seam, fixed discrete action space, a $0 ~20-games/s runner, a per-game
rubric fitness) but the meeting layer is natural-language and **not** a NEAT target.
This spike turns those structural findings into three measured numbers.

See also: `experiments/lab/rubric.md` (the fitness), the impostor-info-ceiling and
phase-11 memories (why the tactical layer is the lever), and the Phase-7.5 episode
(why check 3 is mandatory: an unvalidated fake meeting model once read **76% when
the real provider was 0%**).

## Scope

**IN**
- ONE tactical decision, learned (recommended: the **impostor post-kill vent/move**
  choice — the validated −91%-catchability lever: high signal, low-dimensional,
  already hand-coded in 11.1 so it can be behavior-cloned).
- A single **shared-brain** policy (one genome for the role), tiny fixed MLP.
- Evolution by **ES** on the MLP (NEAT deferred — topology search is a later lever).
- Injection through the existing `agent_factory` seam — **zero engine edits**.
- The fake-provider tournament runner as the fitness harness.
- `rubric_score._game_interestingness` (+ a narrow per-decision proxy) as fitness.
- The existing deterministic detector (contradiction flags + §4.6 gate + accumulator
  + vote-tally) as the **surrogate meeting model** under test.

**OUT** (explicitly not this spike)
- Learning the meeting layer (stays LLM).
- Co-evolution (both sides learning at once), Hall-of-Fame, archetypes.
- The front-end. Production-grade code. Any change to engine rules / balance
  constants / the firewall / the replay format.

## The three checks

### Check 1 — Determinism (the cornerstone)
**Question.** Does a *frozen* genome produce byte-identical replays + per-tick state
hashes across repeated runs of the same seed, and across a re-record on the same
machine?
**Method.** Inject a frozen-genome policy via `agent_factory`; run the same seed
twice; diff the replay JSONL and the per-tick `state_hash` chain
(`orchestrator/replay.py`). Then run the existing byte-reconstruction
(`scripts/verify_samples.sh` style).
**Pass.** Zero divergences; deterministic single-thread CPU inference holds.
**If it fails — mitigation ladder** (audit-confirmed): (1) quantize logits to a fixed
integer grid and break ties with the existing lexical `player_id` sort
(mirrors the integer cross-multiplication already at `impostor_policy.py:619`);
(2) backstop — replay already records the *discrete action* and re-feeds it on
replay (`replay.py:278`), so replay determinism is structurally immune regardless;
only live re-record is exposed, and it shares that exposure with today's float
kill-scoring (`impostor_policy.py:999`).
**Artifact.** A diff log showing 0 divergences + the chosen inference-determinism config.

### Check 2 — Learnability + bootstrap
**Question.** (a) Can a tiny ES loop raise an impostor-fitness above random-init
against the frozen FSM crew and frozen rules? (b) Can **imitation-init** (behavior-
clone the FSM's choice on this decision) reach FSM-parity, so evolution starts from
competence rather than zero?
**Method.** Define a narrow fitness for the vent/move decision (flag-cleanliness /
post-kill survival proxy from rubric R2 + the detector). Run ES for N generations,
**fitness-averaged over K seeds** to beat the hair-trigger-clock noise. Separately,
supervised-clone the FSM's decision into the net and measure parity.
**Pass.** Fitness climbs above the random baseline over generations; BC-init matches
the FSM within a small margin.
**Why it matters.** This is where we learn (i) whether the landscape is climbable
given the chaotic clock (→ how many seeds per fitness eval), and (ii) whether
from-scratch is viable or **BC-init is mandatory** (the FSM is the product of Phases
7–11 of tuning; cold evolution may underperform it for a long time).
**Artifact.** A fitness-vs-generation curve + a BC-parity number.

### Check 3 — Surrogate fidelity
**Question.** Does the deterministic detector predict the real-LLM meeting ejection
well enough to serve as the **training inner-loop** surrogate (so we never pay LLM
wall-clock per training game)?
**Method.** On the committed 9p2i sample sets (real-Ollama meetings), compute the
detector's predicted ejection per meeting and correlate against the actual recorded
ejection. Refactor the core of `audits/workflows/extract_gameplay_facts.py` into a
callable `extract_facts(dir) -> dict` to feed both predicted and real outcomes.
**Pass.** Agreement high enough that training against the surrogate won't teach the
wrong lesson (bar: **≥~75% top-1 ejection match** or strong rank correlation), OR a
clear characterization of the gap → decide rule-based-surrogate vs learned-surrogate
(behavior-clone the LLM votes from committed replays) vs lean-harder on the real-LLM
selection gate.
**Tailwind.** The Phase-10 audits found LLM listeners mostly **vote the flags and
ignore spoken testimony**, so a detector-based surrogate may be *more* faithful than
feared today — but that is a known limitation slated for repair (testimony-ingestion),
so the surrogate is a **standing calibration liability**, re-checked after any meeting-
layer change, not build-once.
**Artifact.** A confusion table + an agreement number.

## Architecture decisions the spike will settle
- Observation → fixed-vector **encoder shape** (fixed map: 10 rooms / 12 tasks / 6
  vents / 2 sabotages; fixed-N roster mapped to fixed per-player slots; visible-subset
  → full-roster reconstruction via the existing `MemoryStore` accumulation).
- **ES vs NEAT** for the first real cut (default ES on a small MLP).
- The **fitness definition** (narrow per-decision proxy now; rubric + side-fitness later).
- The **action-masking** approach (turn the raise-on-illegal predicates in
  `engine/rules.py` into a `legal_actions(packet, public_map)` boolean mask).
- Confirmation that **shared-brain** is the right first cut (defer per-agent credit
  assignment and archetypes).

## Method / harness (grounded in the code seams)
- `AgentInterface.decide(packet, public_map) -> ActionIntent` (`agents/base.py`) is the
  contract; keep `TacticalAgent` (`orchestrator/game.py`) and swap only the policy
  object so memory-ingest + all four meeting-protocol methods come for free.
- `agent_factory: Callable[[PlayerId, Role], AgentInterface]` is a first-class param on
  `eval/balance_eval.py::run_tournament_eval` and `eval/benchmark.py` — inject the
  learned factory with no runner edits.
- `AILIBI_LLM_PROVIDER=fake` runs gameplay with no LLM (audit-measured: **50 games /
  2.47s, $0**). Gameplay is provider-independent, so training never touches the LLM;
  the surrogate replaces fake meetings for realism.

## Decision matrix (go / no-go)
| Check | Pass → | Fail → |
|---|---|---|
| 1 Determinism | proceed; record the inference-determinism config | quantize+lexical-tie-break; if still flaky, store-action backstop (replay safe regardless) |
| 2 Learnability | proceed; note seeds-per-eval + whether BC-init is required | if even BC-init can't climb, reconsider decision granularity / ES→other method before any Phase C commit |
| 3 Surrogate | proceed with rule-based surrogate + real-LLM gate | switch to a learned surrogate, or narrow training to detector-faithful regimes; do NOT train on an unvalidated surrogate |

**Overall GO** = all three pass (or fail with an in-hand mitigation). **NO-GO / rethink**
= check 2 can't climb even bootstrapped, or check 1 has no determinism path. Either way
the cost of finding out is a design-thread spike, not a committed phase.

## Cost
$0 (local, no API). Compute-bounded, not dollar-bounded. At ~20 games/s, a check-2 ES
run of ~50 genomes × ~30 seeds × ~100 generations is single-machine hours,
core-parallelizable. Checks 1 and 3 are minutes.

## Guardrails (inviolate even in a throwaway spike)
- The **observation firewall** and **byte-identical replay** are not negotiable; the
  spike must not weaken either to make a check pass.
- Engine rules / balance constants / §4.6 gate / tally / caps / the task clock stay
  **frozen** — the spike trains *against* them, it does not tune them for the learner.
- The **rubric is a proxy**; even at spike scale, eyeball a few evolved games to catch
  Goodhart (e.g., flag-manufacturing to spike R7) before trusting the number.

## Outputs
A short go/no-go memo carrying the three numbers (determinism diff, fitness curve +
BC-parity, surrogate agreement), the settled data model (encoder shape, ES/NEAT,
fitness, masking, shared-brain), and the throwaway spike code under `experiments/lab/`.
This memo gates Phase C (full ML) and informs Phase D (the ML-introspection front-end).
