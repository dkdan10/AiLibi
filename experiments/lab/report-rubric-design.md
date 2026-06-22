# From-scratch rubric design — score the deterministic chain, not the flags

*Authored 2026-06-21 (design thread), grounded in a 4-subsystem engine/perception/meeting/data map. Supersedes the R1–R7
framing for Phase-13 Wave C. Pairs with Task 13.11 (perception enrichment); both validated on one combined smoke.*

## 0. Why from zero

The repaired R1–R7 rubric is sound in calibration but built on a dead foundation: it measures deduction through the
**detector's flag strength** (R7 = STRONG contradictions naming an impostor). Three independent tests — the $0 committed
re-extract (0/50) and two real-`qwen3.5:9b` smokes (0/17, 0/14 meetings) — agree that `alibi_vs_physical` essentially
never fires. R7 is structurally unreachable on this substrate. So the rubric is rebuilt from the engine's actual
behaviour.

## 1. What the game actually is (ground truth)

- **Two-horse race; the task clock is not a horse.** Budget 1000 ticks; an uncontested crew finishes ~14 task-instances
  in ~15–25 ticks. `CREWMATE_TASKS` (37/50 committed) is the **"nothing happened" outcome** — an idle impostor out-waited.
  The real contest is **impostor kills → `IMPOSTOR_PARITY`** vs **crew deduces → `CREWMATE_EJECT`**. `IMPOSTOR_SABOTAGE`
  is dormant (reactor tuned as a stall, 0 wins).
- **Crew are blind to kills by design** (room-only): they find bodies, never witness the kill or attribution. Deduction
  is a meeting-time inference problem on sparse firsthand sightings.
- **The LLM only emits free-text + structured claims + a ballot.** Chain routing, the 3 contradiction detectors, the
  suspicion deltas (strong +0.3 / weak +0.08, capped 0.3; testimony spread +0.05/+0.12/+0.15 by independent-voice count),
  the §4.6 gate (plurality + ≥1 ballot ≥0.6, tie→SKIP), and the ejection are **all deterministic** from those claims. The
  whole chain `claim → contradiction → suspicion → ballot → ejection → outcome` is exactly measurable and replay-exact.
- **The crew can already identify impostors — they just don't convert.** Committed data: **ejection accuracy 0.846**
  (33/39), but **conversion 0.323** (accused impostors ejected only a third of the time; the rest SKIP), and only 6
  `CREWMATE_EJECT` wins. Deduction works when it fires; it rarely fires decisively.

The key replacement: the **suspicion graph is always populated** — every meeting yields a per-voter suspicion number for
every player, built from testimony + weak flags. *That* is the live, rich, reachable signal — not the detector's flags.

## 2. Seven design principles

1. **Score the deterministic chain's outcomes**, not the prose or the flags. Suspicion, ballots, ejections, kills,
   resolution — all exact, all $0 to recompute (extractor bucket D).
2. **Primary job: separate decided-by-play from the stopwatch.** Never reward the task race as a positive.
3. **Measure deduction as truth-tracking, not flag-counting** — does collective suspicion rank true impostors above crew,
   and does it convert to correct ejections?
4. **Require contest; compose multiplicatively.** Additive R1–R7 let one live term mask a dead one. A near-geometric mean
   means a dead dimension can't be hidden.
5. **Gate every side-positive on *active* play.** Impostor "survival" counts only when *accused* (active deflection);
   crew ejection counts only when *evidence-backed*, never a railroad. The gate is what makes the gradient non-perverse.
6. **Reachability is a hard constraint** — every term must be something `qwen3.5:9b` + this engine demonstrably produces,
   verified against committed data. No aspirational terms.
7. **Roles are the only re-seed-required input; all behaviour is $0 from replay + engine-walk.** Impostor identity is even
   inferable from resolved kills/vents for the ML inner loop.

## 3. The rubric — four contest dimensions + hard floors

Each dimension ∈ [0,1]; each maps to a concrete measurable signal; each has its safety gate.

### D1 — Resolution (did *play* decide it, not the clock?)
- **Signal:** `eject_decided` / `first_zero_impostor_tick` / `reason`; an `IMPOSTOR_PARITY` reached **after** ≥1 meeting
  (buckets C/D).
- **Scores high:** `CREWMATE_EJECT`, or a *contested* `IMPOSTOR_PARITY` (meetings happened). **Scores ~0:** a
  `CREWMATE_TASKS` stopwatch and a pre-meeting stomp alike.
- **Anti-perverse:** rewards *deciding*, not *winning* — both sides can score; passivity and the clock cannot.

### D2 — Crew deduction (does collective suspicion track truth and convert?)
- **Signal:** **suspicion separation** = mean rendered-suspicion(true impostors) − mean(crew), averaged over meetings
  (from `rendered_suspicion_by_target` / `suspicion_graph_by_voter` + roles); **conversion** of observation-backed
  accusations of true impostors → correct ejection (the `conversion` / `missed_conversions` blocks).
- **Anti-perverse:** rewards impostor-**over**-crew separation — a railroad raises suspicion on an *innocent*, which
  *lowers* separation, so it is penalized, not rewarded. Correct ejection counts only when **observation-backed**
  (testimony with the `observation_backed` bit), never a flagless conviction.
- **Reachable:** the suspicion graph is always populated and already separates (0.846 ejection accuracy proves it) — unlike
  R7's dead strong-flag requirement.

### D3 — Impostor craft (is deception + agency load-bearing?)
- **Signal:** **active-deflection survival** (accused → responded → survived: `gate_metrics.accused_impostor_survivals`,
  `effective_deflection`); **wrong-ejection steering** (an innocent ejected where impostor testimony drove the plurality:
  `redirect_records` / `self_accusation_records` / chain-driver); **evasion** = low FO-6 physical-suspicion rank (bucket
  B reconstruction, $0, no LLM); **tool use** (vents/sabotage/cover actions).
- **Anti-perverse (kills the R2 trap):** survival counts **only when accused**; steering **only when impostor-caused**. A
  passive impostor that is simply never accused scores 0 — passivity is not rewarded.
- **Reachable:** impostor-alibi survival 0.541 in committed data.

### D4 — Arc (a contested build, not a one-shot)
- **Signal:** meetings > 1 with **suspicion movement across them** (Δ rendered-suspicion on the eventual target,
  `prevote_folds` + cross-meeting trajectory); accusation-chain length / replies, not openings→SKIP.
- **Anti-perverse:** rewards suspicion *movement* and contested chains, not raw length (no reward for stalling).

### Composition — requires contest
```
interestingness = floor_multiplier × geomean_weighted(D1, D2, D3, D4)
```
A geometric-style mean (not a sum): a stopwatch (D1≈0), a SKIP-fest (D2,D4≈0), or a passive-impostor game (D3≈0) each drag
the whole score down *regardless* of the others. This is the structural fix for the additive masking flaw.

### Hard floors (`floor_multiplier` → 0 / heavy dock; only punish, never reward)
- **Railroad ejection** — an innocent ejected with no observation-backed suspicion (the R4 violation).
- **Friendly-fire kill** (impostor kills impostor — engine forbids it; the floor guards regressions).
- **Firewall / determinism breach** — any role/attribution leak or state-hash mismatch.

These are integrity gates, not tradeable dimensions — they can only sink a game.

## 4. Set-level diversity sentinel (not per-game fitness)
Over a *batch*: the distribution of win-reasons, kill counts, and meeting outcomes. A healthy set shows multiple win-shapes
and a spread of dynamics; a set collapsed to one mode (all stopwatch, all identical stomps) is flagged. This is R5's valid
core, kept as a population diagnostic — and the guard against ML monoculture later.

## 5. How this becomes ML fitness (side-specific projection)
The symmetric `interestingness` is the **held-out selection gate**. The inner-loop **fitness is side-specific**:
- **Impostor fitness** = D3 craft, anchored on the **FO-6 LLM-free physical-suspicion rank** (top-1 64%) as the $0
  inner-loop objective (minimize your own learned suspicion rank), with the real-LLM meeting only at the selection gate.
- **Crew fitness** = D2 deduction (separation + evidence-backed conversion) minus the railroad floor.
- The symmetric rubric never *is* the inner-loop fitness (Goodhart-prone, meeting-gated); it is the referee.

## 6. Validation plan (prove it before it gates anything) — all $0 over committed replays
1. **Ranks the known-good seeds above the stopwatch games** (audit's contested seeds top; the 37 `CREWMATE_TASKS` idlers
   bottom).
2. **No perverse gradient** — regress each dimension against the others and against win/lose; confirm none rewards losing,
   railroading, or passivity (the traps that killed R2/R3/R7).
3. **Reachability** — every dimension is non-zero somewhere in the committed data (unlike R7, 0/50).
4. **Watch-the-games** — eyeball top- and bottom-ranked seeds; the ranking must match a human's interesting/boring call.

## 7. The combined-smoke gate (with Task 13.11)
The rubric STRUCTURE above is robust to the information level — it scores outcomes and the suspicion graph, which exist at
any fidelity. Its **calibration** (what counts as high D2) shifts with the information economy, so it is **locked after**
the Wave-C smoke, not before. One combined real-`qwen3.5:9b` smoke validates both at once:
- **Enrichment works** if D2 (suspicion separation + conversion) RISES under 13.11 vs the starved baseline.
- **Rubric is sound** if it ranks the enriched games above the stopwatch with no perverse gradient (the §6 checks on the
  enriched data).
- **Balance holds** if the impostor stays near the Phase-11 ~14% floor (13.11 eases crew deduction; the fake-task cover
  offsets — net is the empirical question).

Designing the rubric on today's starved data would be measuring a game we are about to replace; calibrating it on the
enriched economy is the point.
