# Lab report — Interestingness score (Phase 11 Wave 0; repaired Phase 13.1)

**What:** a per-game **interestingness score** in `rubric_score.py` (`interestingness()` +
`_game_interestingness()`), plus a set-level R5 win-shape diversity summary. **Updated:** 2026-06-21
(Task 13.1 — the pre-ML grounding repair of R2/R3/R7).

**Why:** the lab proved the binary win split is "purchasable wholesale" (`report-stopwatch-lab.md`), so
Phase 11 optimizes *interestingness*, not a 50/50 win rate. The 2026-06-20 grounding audit
(`report-grounding-audit.md`) then found the rubric **unsafe as raw Phase-C fitness**: three of the four
scored terms (R2/R3/R7) had a verified perverse gradient. Task 13.1 repairs those terms so the score stops
rewarding degenerate play; it stays $0/offline (reads committed extractor facts) and re-scores on any facts
JSON.

**Score (0–100, per game, decoupled from who won):**
`100 × (0.35·R1 + 0.25·R2 + 0.20·R3 + 0.20·R7)` — R1/R2/R3/R7 are also emitted **separately** (multi-objective
axes for Phase-C, not just the collapsed scalar):

- **R1 decisive** (0.35) — *unchanged, SOUND.* 1.0 if the game is `CREWMATE_EJECT` (fires iff
  `alive_impostors==0`, and crew cannot kill impostors → deduction cleared the board), 0.5 if an impostor was
  ejected but the clock decided, 0.0 if pure stopwatch / kill-gifted.
- **R2 deception** (0.25) — *repaired: gated on an ACTIVE-DEFLECTION event.* 1.0 if an accused impostor's
  counter-accusation MOVED the eject-plurality off itself (effective deflection — real skill), 0.6 if it
  actively counter-accused and survived but was SKIP-saved, **0.2 if it was accused yet only passively/clock
  survived or was caught**, 0.0 if no true impostor was ever accused. (Reproduces
  `eval/meeting_quality.py::compute_effective_deflection`'s ACTIVE-DEFLECTED split over the same accusation
  data; validated to match its aggregate exactly: active 34, effective 10, skip-saved 24.) *Before:* passive
  survival banked 0.6, so a lose-while-accused-alive game outscored a win-unaccused game and R2 was
  **anti-correlated** with the total (Pearson −0.281).
- **R3 arcs** (0.20) — *repaired: a cross-meeting suspicion RISE that LANDED on a true impostor.* 1.0 iff an
  ejected player is a true impostor whose rendered suspicion (the extractor's `accumulator_trajectories`) rose
  across ≥2 meetings up to the ejection; else 0.0. *Before:* 0.5 for ≥2 meetings + 0.5 for any flagless
  carry-eject — which gave full credit to a meeting-0 conviction of an innocent (the railroad R4 forbids).
- **R7 legible** (0.20) — *repaired: STRONG-evidence share.* the share of the game's meetings carrying a
  STRONG (non-weak) contradiction whose subject is a true impostor (reuses `transcript.py::is_weak_contradiction`
  via the extractor's `strong` bit + the firewalled role; per-meeting credit capped at 1). *Before:* raw
  `n_contradictions>0` counted below-gate weak `alibi_vs_sighting` flags that eject nobody.
- **R5** (set level): count of distinct win shapes each ≥10% (target ≥3). `IMPOSTOR_SABOTAGE` now has its own
  `sabotage-win` shape (before, the `startswith('IMPOSTOR')` catch-all hid it).
- **`ballot-follows-chain`** is a **diagnostic only**, dropped from any fitness aggregate (≈65% of non-skip
  ballots are null-reason BY DESIGN, so it measures a coherence the meeting architecture suppresses).

## Repaired baseline (9p2i @ `1e48c40`)

| metric | value |
|---|---|
| mean interestingness | **25.9** (median 22.5, ceiling 62.5) |
| eject-decided games (R1=1.0) | 6 / 50 |
| R2 by level | 0.0 ×1, 0.2 ×23, 0.6 ×17, 1.0 ×9 |
| R3=1.0 (arc landed on a true impostor) | 6 / 50 |
| R7 (strong-evidence share) | **0** everywhere — all 112 baseline flags are weak |
| R5 win shapes ≥10% | 4 (stopwatch-some-eject 21, stopwatch-no-eject 16, impostor-win 7, eject-decided 6) |

The mean falls from the pre-repair 45.1 because the perverse credit is gone: passive-survival R2 drops 0.6→0.2,
flagless R3 is no longer farmable, and R7 honestly reads 0 on an all-weak baseline. That compression is the
point — the substrate has little strong evidence and few genuine cross-meeting arcs, and the score now says so.

## Validation — the three perverse gradients are gone (audit's specific cases)

- **R2 no longer anti-correlated.** Pearson(R2, total) = **+0.451** (was −0.281): the optimizer is no longer
  pushed toward "both impostors caught" / "prefer to lose slowly".
- **R3 no longer rewards the railroad.** seed-15 (a flagless meeting-0/-1 conviction of an INNOCENT crewmate)
  now scores **R3 = 0** (was 1.0); the term lands only on a true impostor with a rising arc (e.g. seeds 0, 5,
  47).
- **R7 no longer counts weak presence.** the all-weak baseline scores **R7 = 0** across all 50 games.
- **Calibration preserved at the extremes.** the audit's top-3 seeds 5/47/34 (scores 60/60/40) all rank above
  the dull bottom (seeds 3/19/37/44 at 5.0). R1 is byte-identical to the pre-repair artifact on all 50 games.

## Targets the later Phase-13 / Phase-C work moves

- **Deduction rework (workstream B):** an inferential suspicion path + testimony ingestion makes STRONG flags
  and cross-meeting arcs reachable, so R7 and R3 can climb off the floor on a re-record.
- **Phase-C entry:** use these repaired R1/R2/R3/R7 as held-out multi-objective SELECTION axes (NOT the
  tactical inner-loop fitness — that is the FO-6 physical-suspicion rank, per the ML plan).

Run: `uv run python experiments/lab/rubric_score.py FACTS_JSON --set-dir SET_DIR`. Output appended to
`results-rubric-score.json` under `"interestingness"` and co-located into the served set (stamped with the
set's MANIFEST sha). (The flat 4p1i set is short-by-design — few meetings — so 9p2i is the
interestingness-relevant set.)
