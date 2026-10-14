# Post-Phase-6 Real-Provider Eval — 2026-05-30 18:27

## 1. Verdict

**PHASE 6 CLOSE GATE: PASS**

The Phase 6 close-gate real-provider eval passes. The two substrate-level changes
this gate exists to validate are confirmed behaviorally live under a real model,
not merely present in code: the win-condition impostor-elimination fix (Task 6.3)
and the contradiction-detection wiring + belief Rule 2 + `BeliefState`-into-
perception (Task 6.4). No information leak surfaced, no cost blow-up occurred, and
the refreshed tournament establishes a clean, all-decisive balance baseline for
Phase 7 tuning.

This was run as one real-provider pass over the 50 committed sample seeds via
`scripts/refresh_samples.sh --full`; the typed `TournamentEvalReport` was then
assembled offline from those exact refreshed replays (no second run), so the
served samples, the MANIFEST cost record, and the dashboard report all describe
the same games — which also resolves the report-vs-MANIFEST cost disagreement
flagged in the MVP-close audit (F-F-1).

## 2. Environment

- **Run timestamp:** 2026-05-30 18:27 (EDT)
- **Audited HEAD:** `aac20363fbd3b204fc578dcb59f2ea061218fda6` — "Merge pull request #93 … contradiction-detection-wiring" (2026-05-30 18:04 -0400); all 9 Phase 6 tasks merged.
- **Provider:** real Anthropic provider (`AILIBI_LLM_PROVIDER=anthropic`), default meeting model (recorded per-seed in `replays/samples/MANIFEST.md`).
- **Tournament:** 50 games, seeds 0–49 (the committed sample set).
- **Total spend:** $1.0049 (per MANIFEST). Real LLM calls occur only in the 4 meeting-bearing games; the 46 no-meeting games make zero LLM calls and are deterministic, so only seeds 22/24/26/49 changed on disk.
- **Post-refresh gate:** `bash scripts/check.sh` → 1037 passed, 13 skipped; mypy clean (149 files); 90/90 prompts in sync; task-doc validation passed; frontend `tsc:check` + `vite build` clean.

## 3. Close-gate criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Zero leaks across observation packets and rendered prompts | **PASS** — the leak suite plus the Task 6.2 property-based sweep (role-aware Hypothesis strategy over `ObservationService` for every living agent each tick across many seeds) are green on HEAD; the firewall pipeline is unchanged by the refresh and is game-content-independent, so the refreshed games are leak-free by construction. |
| 2 | A detected contradiction demonstrably exercised in live meetings | **PASS** — see §4. Contradictions went from 0 (pre-6.4, hardcoded `contradictions=()`) to 45 across the 4 meeting games; those meetings resolve with `vote_correctness_rate = 1.0` and produce the new `CREWMATE_EJECT` outcomes. |
| 3 | No cost blow-up vs the Phase 3/5 per-game envelope | **PASS** — $1.0049 / 50 games. Real cost concentrates in the 4 meeting games (~$0.25 each); the per-game envelope is consistent with prior real-provider runs (~$0.9 for the original 50-seed eval). |
| 4 | Record the post-Phase-6 balance baseline for Phase 7 | **PASS** — see §5. |

## 4. Substrate liveness (the reason this gate ran)

**Task 6.3 — win-condition impostor-elimination (J-8).** Outcomes by reason over
the 50 games: `CREWMATE_TASKS: 28`, `IMPOSTOR_PARITY: 18`, `CREWMATE_EJECT: 4`,
and crucially **0 no-winner games**. Before 6.3, games where the last impostor
was ejected before tasks completed ran on as zombies and recorded as
tick-budget/task outcomes; the 4 `CREWMATE_EJECT` games are exactly those
formerly-zombie games now resolving decisively as crew ejection wins. The fix is
live and the eval population is now leak-of-meaning-free (no zombie games
distorting the aggregates).

**Task 6.4 — contradiction wiring + Rule 2 + BeliefState-into-perception
(J-1/J-9/J-4/A-4).** Across the 4 meeting-bearing games (seeds 22, 24, 26, 49)
the refreshed replays record **45 detected contradictions** (every meeting game
now carries a non-zero count); pre-6.4 every meeting recorded `contradictions=0`
because `detect_contradictions` was invoked only by tests. The detector is now
recomputed in the live meeting loop and threaded into the agent-facing prompts.
The meeting games resolve with `vote_correctness_rate = 1.0` — crew votes land on
impostors — consistent with detection now feeding the vote.

Note: this confirms the wiring is behaviorally live (detection fires and meetings
resolve correctly); a per-meeting causal trace isolating a single
contradiction→vote flip was not performed and is not required by the gate.

## 5. Post-Phase-6 balance baseline (for Phase 7)

- **Impostor win rate:** 36% (18/50), all games decisive (0 no-winner).
- **Outcome split:** crew 32 (28 tasks + 4 ejection), impostor 18 (parity).
- **vote_correctness_rate:** 1.0
- **alibi_survival_rate:** 0.6 (over 5 impostor alibis) — down from the Phase 5 close-gate's 0.8. This is the expected direction: with contradiction detection now live, more impostor alibis are challenged, so fewer survive. Treat 0.6 as the new baseline, not a regression; the denominator (5) is small because only 4 games hold meetings.
- **Total cost:** $1.0049 / 50 games.

The 36% baseline supersedes the pre-Phase-6 figure (which was computed over a
population including zombie games); Phase 7 balance tuning should anchor on this
all-decisive run.

## 6. Artifacts

- **Committed changes (pending sign-off):** `replays/samples/MANIFEST.md` and the 4 meeting replays `replay-seed-{22,24,26,49}.jsonl`. The other 46 samples are byte-identical (no LLM calls) and unchanged.
- **Regenerated, gitignored:** `replays/tournament-eval-report.json` (the dashboard reads it from disk at runtime; 50 games, `format_version=1`).
- **This report:** `audits/audit-2026-05-30-1827-post-phase-6-real-provider-eval.md`.

## 7. Required closing fields

- **Verdict:** PHASE 6 CLOSE GATE PASS
- **Games / spend:** 50 / $1.0049
- **Leaks:** 0
- **Impostor win rate (new baseline):** 36%
- **Remaining Phase 6 close item:** the design-thread DESIGN.md reconciliation (audit Class A + H-1).
