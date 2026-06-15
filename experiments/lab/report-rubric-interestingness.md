# Lab report — Interestingness score (Phase 11 Wave 0)

**What:** a per-game **interestingness score** added to `rubric_score.py` (`interestingness()` +
`_game_interestingness()`), plus a set-level R5 win-shape diversity summary. **Date:** 2026-06-15.

**Why:** the lab proved the binary win split is "purchasable wholesale" (`report-stopwatch-lab.md`), so
Phase 11 optimizes *interestingness*, not a 50/50 win rate. This is the **primary success metric for Waves
1–3**; the win split is demoted to a sentinel. It is $0/offline (reads committed extractor facts) and runs
on any facts JSON, so it re-scores every wave's re-record.

**Score (0–100, per game, decoupled from who won):**
`100 × (0.35·R1 + 0.25·R2 + 0.20·R3 + 0.20·R7)` —
- **R1 decisive** (0.35): 1.0 if the game is `CREWMATE_EJECT` (deduction cleared the board), 0.5 if an
  impostor was ejected but the clock decided, 0.0 if pure stopwatch / kill-gifted.
- **R2 deception** (0.25): 1.0 if an impostor won *despite* being accused, 0.4 impostor-win via the
  parity/kill race, 0.6 survived an accusation (crew still won), 0.2 accused-and-caught, 0.0 never tested.
- **R3 arcs** (0.20): 0.5 for ≥2 meetings + 0.5 for a carry-driven (zero-contradiction) conviction.
- **R7 legible** (0.20): share of the game's meetings carrying structured evidence.
- **R5** (set level): count of distinct win shapes each ≥10% (target ≥3).

## W2 baseline (9p2i @ 891234b) — the number Phase 11 must move

| metric | value |
|---|---|
| mean interestingness | **38.2** (median 42.5, ceiling 62.5) |
| **eject-decided games (R1=1.0)** | **0 / 50** |
| R5 win shapes ≥10% | **2** (stopwatch-no-eject 25, stopwatch-some-eject 24, impostor-win 1) — target ≥3 |

**Validation (ranks interesting above dull):** the top games carry ejections + deception drama + arcs +
evidence; the bottom are stopwatch-no-eject with none. The single impostor-win (seed 18) ranks **#3 on
deception+arcs, not auto-top** — confirming the score is independent of the binary outcome. The ruler
*independently reproduces* the headline diagnosis: **no game is eject-decided**, so deduction never decides
and the set is uninteresting (mean 38, R5=2).

## Targets the Phase-11 waves move

- **Wave 1 (deception):** R2 up (accused impostors survive via vents) → mean rises, deception-bearing games
  climb the ranking.
- **Wave 2 (retune):** **eject-decided share > 0** and R1 up — gate Wave 2 on this, NOT the win %.
- **Wave 3 (sabotage):** R5 ≥3 win shapes (a sabotage-pressure shape appears).

Run: `uv run python experiments/lab/rubric_score.py FACTS_JSON`. Output appended to
`results-rubric-score.json` under `"interestingness"`. (The flat 4p1i set is short-by-design — few meetings —
so 9p2i is the interestingness-relevant set; the scorer runs on the flat facts too when generated.)
