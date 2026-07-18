# Phase-18 planning — the research dossier: the ML phase, priced from the bytes

**Date:** 2026-07-18.
**Author:** the Phase-18 planning/coordination session, per the owner's re-charter directive:
Phase 18 is the **ML phase** — advance the learned agents until deception and deduction arise
from environmental pressure rather than scripting. Presentation is deferred; **Phase 19 is
re-chartered as REVIEW-AND-REFRESH** (deep code review for dead spots/refactors + a frontend/
data-display refresh); the **human seat is OUT**; **heterogeneous-model lobbies are NOT in
Phase 19 either** — a model-vs-model comparison feature comes only after the review/refresh
work, as its own later decision. Those rulings are recorded here and serialized into
`tasks/post-phase-14-plan.md` by the phase-doc PR.
**Method:** five parallel deep dives (training stack, conviction-economy instruments,
meeting-layer uptake surfaces, literature, novel-option feasibility) run as isolated research
agents over the repo at `d15d1e9` (the 17.17 close), with every load-bearing claim
adversarially re-verified by an independent agent instructed to refute it (23/26 CONFIRMED;
the three PARTIALLY_WRONG verdicts are incorporated below as corrections, labeled). The
orchestrating session separately re-derived the inherited headline numbers from committed
bytes before any dive launched (§1). Web literature is cited inline (§6).
**Label key:** **[VERIFIED]** read/re-derived from committed sources this session ·
**[INFERRED]** arithmetic over verified cells (shown) · **[PROPOSED]** a recommendation the
owner ratifies or amends at the decision menu.

---

## 0. Verdict in one line

The phase-defining tension is real and priced — the win-optimal mover starves the evidence
economy (utility-es: win 0.52, Δ +0.16, referee FAIL at flags 0.4255 < 0.50279 and conversion
0.3585 < 0.5601) while the referee-passing mover is competitively annihilated (policy-es:
PASS 48.20, win 0.02) — and the codebase already contains most of what closing it needs: the
deception behaviors the owner wants are **already emergent in the meeting layer and merely
un-instrumented** (455 impostor frame attempts, 34 false teammate-vouches, 84 fabricated
whereabouts claims on the corpus bytes — but only 5 frame conversions), the training loop's
real blocker is that **conviction pressure is invisible at training time** (fake path mints
zero evidence; the surrogate is citation-blind by design, 0/116 vs 50/104), and the honest
fix is a layered training signal — a **conviction-economy proxy model over
live-reconstructable channels** in the loop plus **real-path selection** at ~2 h/generation —
under an **alternating-freeze co-evolution program with a frozen hall-of-fame** (~4–5
contracts), sequenced impostor-first because crew deduction fitness is structurally dead until
meetings convict at training time. One owner package decides the substrate: the
absence/uptake meeting-layer bundle (turn-taking round + endpoint-band relaxation ±
impostor-answer templates), which if taken runs FIRST (gate-before-corpus) and re-records
everything, and if declined leaves the phase training against baseline 5 as-is.

---

## 1. The verified state (re-derived this session, before any dive)

All four claims below were reproduced from committed bytes by this session **[VERIFIED]**:

- **The finalist rows** (`training/reports/results-finalist-eval.jsonl`, re-read): utility-es
  win 0.52, referee mean 41.47 FAIL — flags/meeting 0.42553 < 0.50279, testimony-backed
  conversion 0.35849 < derived floor 0.56015; policy-es win 0.02, referee 48.20 PASS (flags
  1.7748, conversion 0.9417 vs derived floor 0.1343). Stamp==sidecar `True` both.
- **The surrogate verdict** (re-derived end-to-end via `decide_go_no_go` over
  `replays/ml_corpus/9p2i`): GO — top-1 0.86 ≥ bar 0.615 (= 0.75 × ceiling 0.82), > FO-6
  0.22, SKIP-vs-eject 0.5192 > always-eject 0.4808; `training_time_runner="surrogate"`.
- **The absence/uptake pins**: `tests/agents/test_absence_prior.py::
  TestAbsencePriorOnCommittedBytes` (14 passed) and `tests/eval/test_funnel_pooling.py`
  (27 passed) — new-over-gate 53/179 = 0.296, crew roll-call coverage 0.4624, impostor
  0.0894, asked/answered 496/360.
- **Repo health**: `bash scripts/check.sh` pytest green (3730 passed, 20 skipped, 3 xfailed);
  `validate_task_docs.py` green (261 tasks / 261 prompts). (The frontend `tsc` failure in
  this container is a missing-`node_modules` environment artifact, not repo breakage.)

**The recorded flip bar stands as chartered** (`audits/audit-phase-17-close.md` §1.3)
**[VERIFIED]**: a default-mover flip needs flags/meeting lifted ≥ +0.0773 to the 0.50279
supply floor AND the (then-lower) derived conversion floor cleared (−0.2016 at today's
economy), while keeping win rate ≥ the same-substrate FSM's. Re-pricing it is an owner
decision, never an instrument edit.

---

## 2. The training-signal gap, priced

### 2.1 The seam is one kwarg; the constraint is wall-clock and noise, not plumbing

The meeting-model install point is a `Callable[[], MeetingRunner]` factory threaded through
every rollout layer: `TacticalRolloutEnv.__init__(..., meeting_runner_factory=None)` forces
the fake provider unless a factory is passed (`training/env.py:614-628`), and the bake-off's
`rollout_candidate` does the same (`training/bakeoff/harness.py:517,539-544`); the
orchestrator already bridges async→sync (`orchestrator/game.py:2287-2292`), so a real-LLM
runner is mechanically a one-kwarg change **[VERIFIED]**. Two corrections from adversarial
verification sharpen the design:

- **The determinism tier check would NOT trip on a real-LLM training loop** — it is a
  POLICY-determinism harness that hardcodes the fake provider
  (`training/determinism.py:413-415`) and digests the (features, logits, intent) frame
  stream, never the fitness. The ES purity requirement is a documented contract on
  `FitnessFn` (`training/bakeoff/es.py:51-55`), not a runtime assertion **[VERIFIED,
  correction]**. Consequence: real-path signal in the inner loop is possible but breaks the
  ES-run reproducibility discipline (`ESResult.digest()`) and injects selection noise; it is
  sanctioned only as a deliberately-labeled stage, never silently.
- **Headless meetings run deadline-free** (`orchestrator/game.py:397-399`) — a hung provider
  stalls a training rollout with no wall-clock guard; any real-path stage needs its own
  timeout discipline **[VERIFIED]**.

### 2.2 The cost arithmetic **[VERIFIED]**

Committed budgets: utility-es = 1 + 20×12 evals × 6 seeds = **1,446 games/run**
(`training/bakeoff/utility_es.py:708-718`); policy-es = 1 + 14×10 × 6 = **846**
(`training/bakeoff/policy_es.py:357-366`). At ~20 min/real game, 2 workers (~10 min
amortized):

| design | games | wall-clock | verdict |
|---|---|---|---|
| all-real ES, utility-es full | 1,446 | ~241 h ≈ 10 days | infeasible |
| all-real ES, policy-es full | 846 | ~141 h ≈ 6 days | infeasible |
| **A: final-selection only** (30-seed test split per finalist) | 30/finalist | **~5 h/finalist** | exists today (`--candidate-artifact`) |
| **B: per-generation top-K real re-rank** (K=2 × 6 seeds/gen) | 12/gen | **~2 h/gen; ~40 h/utility-es run** | feasible; the recommended selection channel |
| **C: champion-trace re-rank** (21 intermediate champions × 6 seeds) | 126/run | **~21 h/run** | feasible; cheapest in-run real signal |
| **D: real-path micro-budget fine-tune ES** (e.g. 5 gen × 6 pop × 2 seeds from a trained init) | ~122 | **~20 h/campaign** | feasible as a labeled non-pure stage |

### 2.3 The honest middle design: a conviction-economy proxy model [PROPOSED]

The 6-feature live-parity fence exists because transcript-derived channels (contradiction
flags, citations) do not exist at surrogate `run_meeting` time (`training/surrogate/
ballots.py:114-121` + docstring :32-41) — a citation-aware **ballot** surrogate would have to
train on features the live runner cannot serve, inflating offline fidelity while the deployed
runner behaves worse: exactly the failure the fence forbids. **Rejected.**

But the conviction economy is not transcript-only. A live runner CAN reconstruct, at
`run_meeting` time, the **physical pre-meeting evidence supply**: vent-witness records
(already consumed — `training/surrogate/runner.py:237-239`), per-voter first-hand sightings
(`sighting_records_for_meeting`, `orchestrator/game.py:480-499`), body-proximity and
seen-at-kill from episodic memory — the same channels the honest ceiling's
`proximity_legible` reads (`training/surrogate/fidelity.py:237-243,472-478`) **[VERIFIED]**.
The proposal: fit `g(pre-meeting typed state) → (expected flags minted, expected
testimony-backed conversion)` on the corpus's recorded triples, and use it two ways, neither
of which touches the ballot surrogate or its fence:

1. **A training-time fitness term** — the first in-loop pressure toward "supply and survive a
   convicting economy" (today that pressure is invisible: the fake path mints zero evidence).
   This is a REWARD-side term computed from tactical facts, not a watchability score — the
   gate/reward boundary stays intact (`training/bakeoff/harness.py:582-585`).
2. **A referee pre-screen** — predict whether a candidate would trip the flags/conversion
   floors before spending a 5-h real eval on it.

**Its fidelity protocol** mirrors `run_surrogate_fidelity`: by-game CV on `splits.json`,
scored against flags-minted/conversion labels, with the measured **voice-driven share**
(18.0% on this corpus — `HonestCeiling`, `fidelity.py:452-487`) as the structural ceiling.
Proposed GO bar [PROPOSED, gate finalizes]: held-out per-meeting flag-count rank correlation
≥ 0.5 AND conversion-prediction fidelity ≥ 0.75 × (1 − voice_driven_share), population-
relative per the ratified anti-absolute-number doctrine — never an absolute constant.

### 2.4 Two cheap training-side levers, adopted without an owner slot

- **λ (anchor-CE weight) as the watchability dial** — the piKL lesson (§6): the champion's
  referee FAIL is an under-anchored symptom; the anchor weight is already a training-time
  lever (`DEFAULT_ANCHOR_PENALTY_WEIGHT`, `harness.py`), and a λ sweep costs minutes/run on
  the fake path (utility-es full trains in 285 s **[VERIFIED]**, `report-impostor-bakeoff.md`
  §2). Selection across λ values uses the real-path designs above.
- **Filtered behavior cloning from the corpus as an anchor refinement** — keep only
  crew-winning/high-flag games and fit the option-feature anchor toward "watchable winning
  play" (numpy-friendly weighted logistic; ~200 games is 2–3 orders of magnitude below where
  offline-RL machinery earns its complexity — §6). The corpus is a prior source, never a
  training environment.

---

## 3. The current deception economy, measured

### 3.1 The census: deception exists; conversion does not **[VERIFIED — adversarially recounted]**

On `replays/ml_corpus/9p2i` (150 games, 541 meetings): impostors accuse crew **455** times
and their co-impostor **0** times; place the co-impostor via `saw_player` (false vouch /
cover) **34** times; make **84** whereabouts claims and **46** corroboration claims. Crew are
ejected in **13** meetings, impostors in **229**, nobody in 299. Meetings where a crewmate
was ejected AND an impostor had accused exactly that crewmate (frame → wrong eject): **5**.
Representative transcripts (seeds 1000/1004/1005) show fabricated co-presence vouches, frame
attempts weaponizing a real vent sighting of the teammate, and deny-and-deflect. The
behaviors the owner wants are **present and un-instrumented; the scarce quantity is
conversion** — deception that moves the eject plurality. That is the same conversion economy
the champion fails the referee on, seen from the other side.

### 3.2 The instrument shelf is deep; four of five owner metrics are cheap **[VERIFIED]**

Existing offline instruments: whereabouts-lie detection (`eval/funnel.py:1469`), roll-call
coverage + per-role split (`funnel.py:1366,1546`), vouch census (`funnel.py:1404`), grounded
vouching (`funnel.py:1430` → production `grounded_vouch_subjects`), alibi-fabrication
survival (`eval/alibi_fabrication.py:153`), accusation calibration
(`eval/accusation_calibration.py:331`), effective deflection
(`eval/meeting_quality.py:2277`), conversion buckets, testimony-backed conversion,
witnessed-kill reconstruction (`eval/watchability.py:1031`). Gap analysis:

| owner metric | typed data present | size |
|---|---|---|
| false-vouch rate (grounded vs fabricated split) | yes — 34 numerator events in corpus | Small |
| frame attempts + conversions | yes — 455 / 5 (rare-event ⇒ advisory) | Small |
| fabricated-alibi rate | survival exists; ground-truth-false needs the reconstruction walk | Small–Medium |
| kill-timing vs witness density | `KilledEvent.tick/room/witnesses` + walk exist; occupancy fold is new | Medium |
| behavioral diversity (action-stream entropy) | lexical diversity exists (`vj_instruments.py:719`); action entropy is new | Medium |

**Off-FSM-menu detection, corrected [VERIFIED, correction]:** `enumerate_options` is a pure
public oracle (`training/bakeoff/utility_es.py:209`, ported at
`agents/tactical/learned/forward.py:227`), and a per-decision membership test over a
recorded champion's bytes is buildable — but it is **vacuous for the menu-bounded champion**
(on-menu by construction) and meaningful only for free-policy-family recordings. It is the
right instrument for the co-evolution wave, not a general emergence gauge.

### 3.3 The endpoint band is why roll-call lies cannot convict **[VERIFIED]**

A whereabouts claim is indexed as a degenerate single-tick self-alibi
(`from_tick == to_tick`, `meetings/transcript.py:1927`, docstring :1932-1945), so any
contradicting sighting sits on an endpoint tick by construction and takes
`WEAK_REASON_ENDPOINT_TICK` (`transcript.py:529`, applied :2262-2270) — a roll-call lie can
**never** mint a STRONG flag. Corpus consequence: 25 whereabouts lies detected (rate 0.0227),
20 crew-authored / 5 impostor-authored, all weak-tier. The routed **endpoint-band
relaxation** is the single highest-leverage lever for making roll-call lies economically
punishable; it is a record-time substrate change (it moves persisted `contradictions` bytes,
`flags_per_meeting`, and the derived conversion floor) — one-layer-per-baseline.

### 3.4 The turn-taking decomposition: coverage is an allocation problem **[VERIFIED]**

The meeting is opening (1 turn, the reporter) → reactive accusation chain (mean 2.77
speakers; dies on no-new-accusation) → co-presence-gated opt-in
(`meetings/manager.py:952-1051, 1940-2010`). There is no turns-per-meeting knob beyond the
structural `len(living)` cap. On the canonical samples (179 meetings): living player-meetings
1057, took ≥1 turn 496, answered roll-call 360 — **561/1057 = 53% of living player-meetings
never speak at all**. Template asks therefore cap total coverage at asked/living = 496/1057 =
0.469 < the ratified 0.60 crew clause: **template-ask-only structurally cannot graduate the
absence prior**. The only surface that clears the bar is a dedicated roll-call round: +3.13
turn calls/meeting (496 → 1057, 2.13×), ≈ +36% meeting LLM calls, lengthening the ~14–15 h
corpus re-record accordingly.

The impostor side of the 0.363 aggregate is a **structural output-contract omission, not
prose refusal [VERIFIED, correction]**: the impostor opening and reply templates hard-code
`"observations": []` (`agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:109-110`;
`accusation_round.j2:198-200`), so impostors self-place only through the role-blind opt-in
branch (coverage 0.0894). Flipping impostor templates to ANSWER roll-call (plausibly lying)
manufactures exactly the contradiction material the alibi rules prosecute
(`agents/memory/beliefs.py:439-443` states this loop verbatim) — the richer deception
package — but it re-opens the ≥44% self-flag failure class the prompt ladder closed
(`impostor_report.j2:8-12,29-36`) and forces the ratified bar to re-read on fresh bytes
(gate audit Ruling 3(d)). Crew-side-only and impostor-answer are complements, not
substitutes; both are meeting-layer.

---

## 4. The option space, priced

| # | option | what it buys | cost | risk | verdict [PROPOSED] |
|---|---|---|---|---|---|
| 1 | Conviction-economy proxy model (§2.3) | first in-loop conviction pressure + cheap referee pre-screen | ~2 contracts + fidelity protocol | proxy mis-predicts (caught at real-path selection; instrument survives as diagnostic) | **RECOMMEND** |
| 2 | Real-path selection designs B/C (§2.2) | real conviction signal at selection, ~2 h/gen | ~1 contract (recorder loop) + operator h | provider nondeterminism noise (selection-tolerant) | **RECOMMEND** |
| 3 | Real-path micro-budget fine-tune ES (design D) | direct real-economy adaptation from a trained init | ~20 h/campaign, labeled non-pure stage | breaks ES-digest reproducibility (must be labeled, never silent) | OFFER (owner-visible, not default) |
| 4 | Citation-aware ballot surrogate (break the 6-feature fence) | — | — | trains on features the live runner cannot serve — the exact fence failure | **REJECT** |
| 5 | Absence/uptake package: roll-call round + endpoint relaxation (+ vent widening re-rule) | a lie-prosecuting evidence economy; the ratified graduation path | gate + adopting record + ~15–18 h re-record + surrogate re-ground + re-pins | ~2–3 operator sessions; all baseline-5 selection evidence goes stale | OWNER (Q2) |
| 6 | + impostor-answer templates (within 5) | catchable impostor lies — the densest deception signal | same cascade + template contracts | re-opens the self-flag class; bar re-reads on new bytes; gate-conditional fallback needed | OWNER (Q2) |
| 7 | Crew deployment surface (`crew_forward.py` port + stamp + Q4 bit-exact gate) | the missing half of co-evolution; opt-in only | ~1 contract (+ co-deploy stamp work if both sides record together) | none structural — adoption stays gated | **RECOMMEND** |
| 8 | Alternating-freeze co-evolution + stabilizer stack (frozen HoF, PFSP-lite sampling, absolute FSM anchor benchmark, exploiter probe) | the emergence engine: opponent pressure instead of a static optimum | ~4–5 contracts + training operator time | cycling (that is what the stack is for); naive simultaneous form stays barred | **RECOMMEND**, impostor-first |
| 9 | Full PSRO / live league | — | — | needs a real best-response oracle + continuous pool re-evals; incinerates the 20-min/game budget | **REJECT** (import PFSP-lite elements only) |
| 10 | MAP-Elites with referee-tension descriptors (flags/meeting × win) + per-cell genome persistence as the HoF source | populates the high-win/high-supply cell the scalar optimizer misses; watchability as **descriptor, never reward** | ~1–2 contracts (archive currently discards per-cell genomes at freeze — `map_elites.py:407-418,452-458`) | descriptor Goodhart (mitigated: quality=win, descriptors pre-registered) | **RECOMMEND** |
| 11 | λ anchor sweep + filtered-BC anchor refinement (§2.4) | the cheapest lever on the exact failed gauges | ~1 contract; minutes/run compute | none beyond selection cost | **RECOMMEND** |
| 12 | Scenario/curriculum staging (state-injection seam + skill scenarios) | per-skill pressure (kill-under-witness, vent-under-patrol, parity forcing, discovery-latency) without full games | ~1–2 contracts: `WorldState` is hand-constructible today (`tests/training/test_env.py:531-543`) but both entry points hardwire `seed_initial_state` (`orchestrator/game.py:1495-1501,1556`); dense terms already score truncated episodes (`training/rewards.py:250-256`) | scenario overfitting (mitigated: scenarios feed fitness, gates unchanged) | **RECOMMEND** (second half) |
| 13 | First-principles action primitives | — | — | wrong diagnosis: the masked intent space already spans move-per-room/kill/vent/report/sabotage/repair/do_task/wait (`training/env.py:239-361`) | **REJECT** |
| 14 | Encoder v3 + within-kind target resolution for the free-policy family | closes the PR #242 lexical-tie limit; witness-awareness/meeting-history/claimed-location features | ~2–3 contracts (encoder + memory channels) | advances the family that lost the bake-off — only worth it under opponent pressure (option 8) | **RECOMMEND**, sequenced inside co-evolution |
| 15 | Offline RL / Decision Transformer on the corpus | — | — | ~200 games is 2–3 orders below where DT/CQL pay; torch barred | **REJECT** (filtered-BC anchor only) |
| 16 | Torch re-promotion | — | — | no new evidence since pause decision 3 | NOT RE-OPENED |

---

## 5. Operationalizing "emergent behaviors and skills" [PROPOSED]

A phase chasing emergence without a pre-registered definition Goodharts itself. The proposed
operationalization, adopted from the measurement discipline of the emergence literature (§6)
and this repo's own counterfactual habits:

**Tier A — instruments pre-registered on committed bytes, before any training (Wave 0):**
false-vouch rate (grounded/fabricated split), frame-attempt & frame-conversion rate
(conversion advisory at n=5), fabricated-alibi survival (adopt existing), teammate-
non-accusation index (0/455 today), deflection efficacy (adopt existing). All
population-relative; all GATE-side diagnostics, never rewards.

**Tier B — new reconstruction folds, still offline:** kill-timing vs witness-density;
off-menu action rate (free-policy recordings only); action-stream behavioral entropy.

**Tier C — meeting-layer (rides the Q2 package or stays out):** interior roll-call-lie
flags via the endpoint-band relaxation.

**The emergence claim itself** requires, per pre-registration: (a) a named instrument delta
vs the same-seed scripted-FSM comparator on the real path, significant at |z| ≥ 1.96 on the
pre-registered denominator; (b) **reproducibility across the corpus seed-splits** (the
cross-run synchronized-onset bar from the reward-hacking literature); (c) a **counterfactual
ablation** — remove the enabling lever/feature and show the behavior recedes; (d) behaviors
credited as "skills" must be *selected-for*, i.e. present in the champion, not only in the
archive. "Watchability improved" is never itself the emergence claim (gate, not target).

**Success bars for the phase [PROPOSED, owner ratifies at Q4]:** the §1.3 flip bar stands as
the phase TARGET (flags ≥ 0.50279, conversion ≥ its derived floor, win ≥ same-substrate FSM)
with the pre-registered Tier-A/B emergence deltas as the co-equal second axis; a
findings-not-failures close is a measured miss on either axis with the instruments committed.

---

## 6. Literature: what transfers, what does not

Full annotated sweep in the workflow record; the load-bearing citations:

- **AlphaStar league** (Vinyals et al., Nature 2019) and **PSRO** (Lanctot et al., NeurIPS
  2017; Muller et al., ICLR 2020; McAleer et al., NeurIPS 2020; Bighashdel et al., IJCAI 2024
  survey): the transferable core at ES scale is the **frozen hall-of-fame + hardness-weighted
  opponent sampling (PFSP-lite) + main-agent/exploiter split + an absolute anchor benchmark
  as the cycling detector** — a numpy-scale kit. Full leagues/meta-Nash solvers do not
  transfer (weak oracle, budget). Deterministic seed-bounded evals make the empirical payoff
  matrix *exact* here — a luxury the papers lack.
- **Hide-and-seek** (Baker et al., ICLR 2020) and **FTW** (Jaderberg et al., Science 2019):
  import the **measurement discipline** (phase-transition statistics, behavior probes,
  counterfactual ablations), not the open-action-space premise — policy-es already ran the
  open-space experiment here and produced the vent tell.
- **Cicero/piKL** (Science 2022; Jacob et al., ICML 2022; Bakhtin et al., ICLR 2023): the
  KL-anchor-as-legibility-dial is the principled reading of the champion's referee FAIL —
  tune λ to the watchability-passing side of the Pareto front rather than folding
  watchability into fitness (forbidden).
- **Werewolf/Avalon/Among-Us LLM agents** (Xu et al. 2023; Wu et al. 2024; ReCon 2023;
  AvalonBench 2023; "Among Us: A Sandbox for Agentic Deception" 2025; WOLF 2025; "The
  Traitors" 2025): under a frozen talker, the only route to more strategic deception is
  **context-shaping** (retrieval/reflection memory, perspective-taking prompts) — i.e. more
  levers of the kind this repo already graduates through gates; and the **production-vs-
  detection split** is a ready-made instrument axis. This repo's engine-grounded citation
  gate is *stronger* than these benchmarks' free-lying regimes — do not loosen it to chase
  their headline deception rates.
- **Goodhart canon** (Pan et al. 2022; Skalse et al. 2022 — both already cited in
  `eval/watchability.py`; Gao et al. 2022 overoptimization laws; "Evolving Deception" 2026):
  unconstrained utility-driven evolution drifts to deception and degrades self-honesty —
  the anchor and the gate/reward separation are validated doctrine, and "emergence" must
  never itself become an optimizer target.
- **Small-corpus offline RL** ("Should We Ever Prefer Decision Transformer…", 2025):
  filtered BC beats DT/CQL in low-data regimes; at ~200 games only the anchor-refinement
  use survives.

---

## 7. The recommended phase shape [PROPOSED]

Sequencing is forced by standing rule 2 (nothing trains against a changing layer): if the Q2
meeting-layer package is taken, it runs FIRST and everything trained binds to its adopting
record; Wave 0 is layer-neutral by construction.

- **Wave 0 (parallel roots, no layer change):** Tier-A/B emergence instruments +
  pre-registration memo; λ-sweep + filtered-BC anchor study; MAP-Elites per-cell genome
  persistence; the crew forward-pass port (surface only, opt-in, adoption gated); the
  conviction-model dataset/fidelity groundwork that is layer-independent.
- **Wave 1 (the Q2 package, if ratified):** template/surface contracts → evidence-memo gate
  (owner; pre-registered bars incl. the impostor-answer arm's self-flag/win-band bars) →
  adopting record → corpus re-record (operator, ~18–20 h at the widened turn budget —
  14–15 h × the measured 1.36 call multiplier) → surrogate re-ground + conviction-model
  re-fit → floor/bar re-pins.
- **Wave 2 (training signal):** conviction-economy model fit + GO verdict; fitness-term
  integration; real-path selection recorder (design B/C) productized.
- **Wave 3 (co-evolution):** dual-role rollout + frozen HoF + alternating-freeze driver +
  stabilizers (anchor, PFSP-lite, exploiter probe, absolute benchmark); impostor campaign
  first; crew campaign once conviction signal exists; encoder-v3/head-resolution for the
  free-policy family inside this wave; scenario staging as skill pressure where the
  campaigns plateau.
- **Wave 4 (selection + close):** finalist real-path evals through the standing gates;
  the §1.3 flip reading (owner); emergence instrument reads against the pre-registered
  bars; adopting record iff the flip bar passes; phase close with corpus-denominator
  canaries per the Q3 discipline.

Model assignments follow the standing rule: Opus for loud-failure tasks (re-runs, re-pins,
byte-verifies, recorder productization), Fable for silent-failure tasks (instrument
semantics, the conviction model, gate memos, stabilizer design, audits).

---

## 8. The decision menu (asked in-session; recorded answers become locked decisions)

1. **Training signal** — layered proxy-model + real-path selection (Recommended) vs
   selection-only vs adding the labeled real-path fine-tune stage.
2. **The meeting-layer package** — full package incl. impostor-answer arm behind a
   gate-conditional fallback (Recommended) vs crew-side only vs skip (train on baseline 5
   as-is).
3. **Co-evolution scope** — alternating-freeze with the stabilizer stack, impostor-first,
   crew surface built now / adoption gated (Recommended) vs impostor-only vs defer.
4. **Success bars** — §1.3 flip bar as TARGET with pre-registered emergence instruments as
   the co-equal second axis (Recommended) vs flip-as-stretch vs flip-only.
5. **Action-space/architecture timing** — encoder-v3 + within-kind resolution inside the
   co-evolution wave; menu-bounded champion stays the shipping architecture; primitives
   rejected on the §4/#13 evidence (Recommended) vs advancing the free-policy family
   immediately vs freezing architecture entirely this phase.

---

## 9. Method note

The dive workers ran read-only over `d15d1e9`; every load-bearing claim was re-verified by an
independent adversarial agent before entering this dossier (verdicts and the three
corrections are labeled inline). The orchestrator's own §1 re-derivations ran before the
dives launched. Corpus censuses (§3.1) were recounted independently by the verifying agent.
Nothing in this dossier edits code, floors, or task docs; the phase-doc PR serializes the
ratified decisions.
