# Lab synthesis v1 — 2026-06-13 (Tiers 0–2 complete)

Five experiments run (rubric, tally, stopwatch, deception battery, decay+census), $0
spent, ~62 live qwen calls. Every finding below is indexed to the decision it feeds.
Per-experiment detail: the `report-*.md` files beside this memo.

## What changed about decisions

1. **Wave-2 architecture (10.10/10.11) — DECIDED BY DATA: policy-authored deception.**
   The 9B can't invent a lie (2/18 spontaneous) but performs a handed script almost
   perfectly (11/12 cover-story deployment, every lie sheltered weak-only against a true
   witness). The toolkit contract should mint cover stories deterministically at kill
   time and inject them into rendered memory — never instruct "be deceptive". The probe
   task shrinks to confirmatory + three targeting baselines the toolkit A/B must move:
   deflection legality 73%, teammate-deflection 18%, accuser-room-confirmation leak 36%.
   Bonus: 30% story-drift under pressure mints real self-flags — scripted deception is
   already catchable (R2's "sometimes fails" for free).
2. **gp-8 tally stays PARKED, now on evidence.** The SKIP bloc is the largest store of
   unconverted correct suspicion (option-c: +18 impostor meetings on W0), but its
   cost doubled post-testimony (4.5:1 → 1.9:1) — 10.6/10.7 eat the same mass with a
   finer tool. If ever revisited: V3 skip-halfweight (+8/0 on W0), never option-c.
3. **Balance tuning doctrine for Wave 2: the task clock is a hair-trigger.** Δ6 ticks
   flips ~25% of outcomes, Δ12 ~half, Δ24 ~85% (identical on both byte-sets). Move in
   2–4-tick steps if at all; prefer per-game pacing levers (10.8 emergency) over global
   clock; win split is confirmed purchasable and stays a non-gate.
4. **Decay revisit stays DEFERRED on mechanism, not taste.** Single-step sweep on
   validated transitions: decay rate 0.10 vs 0.40 changes nothing (0 crossings, identical
   survival) — the 0.05 lattice swallows one-step differences. It can only matter at 3+
   compounding quiet meetings, which needs 10.8's pacing first.
5. **New watch item — impostor self-accusation (E2): 8–9 per set, and it decides games**
   (seed 12 = PR #147's F2: impostor self-accuses, crew adopt the target, 3-2-2
   ejection). The 10.9.2 guard does not touch this seam. Candidate repair (a
   self-accusation drop at claim validation, 10.2-style) is FROZEN until after the fresh
   10.9 record — flag it to the Wave-1 close audit instead.
6. **Structural zeros confirmed:** impostor reporters 0/set (Wave-2's self-report
   affordance is greenfield); honest-self-placement 8/18 in self-reports (the model
   incriminates itself by truthfulness — another reason cover stories must be minted,
   not improvised).

## Upside verdict (the owner's "better than initially thought?" question)

Yes, conditionally: the deception faculty exists and is GOOD — it was never reachable
because nothing hands the model a script. One injected line turned a truth-teller into a
competent, detector-sheltered liar that holds its story 70% under pressure. Combined with
Wave-1's working conviction engine, the pieces for actual social deduction exist on a $0
local 9B; Wave 2 is assembly, not research. The model-ceiling A/B (14B/32B pull, ~10–20GB)
remains available but is no longer load-bearing for the W2 go decision.

## Standing lab state

- Tier 3 (scratch micro-sets with policy-minted covers) is prepped conceptually and HELD
  until the fresh 10.9 record lands; the deception result de-risks it.
- Re-run on fresh 10.9 bytes when available: tally lab, stopwatch curve, census (with the
  E1 living-filter fix), trajectory sweep with chained re-folds.
- Larger-model battery: awaiting an owner call on pulling a 14B/32B-class model.
- Everything uncommitted under experiments/lab/ pending owner commit.
