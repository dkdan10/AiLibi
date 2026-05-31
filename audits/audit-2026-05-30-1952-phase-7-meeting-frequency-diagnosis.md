# Phase 7 Pre-Planning Diagnosis — Why Games Rarely Reach Meetings (2026-05-30 19:52)

## 1. Verdict / root cause

The committed 50-game sample tournament reaches a meeting in only **4/50 games**
(seeds 22, 24, 26, 49 — all `CREWMATE_EJECT`). This starves every
agent-intelligence metric (vote-correctness, alibi-survival, accusation
calibration run on n=4). A 4-angle diagnostic workflow (read-only; replay-data
forensics + crew-task model + impostor-play trace + a measured config
counterfactual) found the cause is **structural game-brevity, not poor impostor
play**:

- **PRIMARY — low crew task requirement.** `orchestrator/seeder.py:165-176`
  hardcodes exactly **one task per crewmate**. The 4p/1i default → 3 crewmates →
  3 total tasks, and the dead-crewmate task-drop rule (`engine/tick.py:261-265`)
  shrinks the win denominator 3→2 the instant the impostor's first kill lands
  (median tick 3). Two survivors finish their short tasks and win
  `CREWMATE_TASKS` (`engine/win_conditions.py:53-56`) at **median final tick 9 of
  a 1000-tick budget** — before any kill→body-discovery→report chain can
  complete. 28/50 games end this way.
- **PRIMARY (co-equal) — roster (more players / impostors).** The only angle with
  a direct, *measured* counterfactual, and it is decisive (see §3). 4p/1i ≈ 10%
  meeting rate vs **7p/2i = 63%**. More impostors raise the parity kill-threshold
  (longer games); more players enlarge the 1-per-crew task pool and disperse
  bodies onto traveled routes. `num_impostors>1` is **fully wired and
  CLI-exposed** (smoke-ran 7p/2i, 8p/2i, 10p/2i, 6p/2i, 10p/3i with 0 crashes);
  DESIGN.md flags multi-impostor as post-MVP only for the *product* reason (no
  impostor coordination channel), not a code limit.
- **CONTRIBUTING — body-discovery / routing topology + dead emergency button.**
  The impostor kills reliably (70 kills/50 games, 0 failed, **0 witnessed**, a
  body minted every kill via `engine/rules.py`), so it does NOT "kill in ways
  that produce no body." Bodies go unreported because (a) a crewmate reports only
  a body in its **exact** room (`crewmate_policy.py:180`; cross-room reports
  rejected) and (b) after its single task a crewmate idles back to the **Cafeteria
  hub** (`_return_to_hub`, `crewmate_policy.py:220-242`), never re-crossing the
  isolated dead-end rooms where kills happen. **All 4 meeting games were Cafeteria
  kills.** The emergency button fires **0 times in 50 games** (no kill is ever
  witnessed) — an entire meeting-trigger pathway is dead.
- **MINOR / refuted-as-framed — poor impostor play.** The literal hypothesis
  ("impostor kills in ways that never produce a reported body") is wrong: bodies
  always exist; the kills are simply too *clean/isolated* for the current weak
  crewmate FSM to ever discover, and the impostor never sabotages to extend the
  game. Impostor behavior limits game length but is not why bodies go unreported.

**Net:** a meeting requires a body to outlive the win condition AND a survivor to
physically re-cross the body's room. The 4p/1i roster resolves both win paths in
4–12 ticks, leaving a ~5-tick window the hub-camping crew almost never uses.

## 2. Environment

- **Diagnosis run:** 2026-05-30 ~19:00, read-only multi-agent workflow (`phase-7-planning`, run `wf_0c804d0a-152`); 5 agents, ~456K subagent tokens.
- **Subject:** HEAD `aac2036` (Phase 6 close); committed `replays/samples/` (50 games, 4p/1i) + `tournament-eval-report.json`.
- **Counterfactuals** were measured with the deterministic fake provider (free), 20–30 seeds per config — directionally valid; real-provider magnitudes to be confirmed in Phase 7 Wave 0.

## 3. Measured config counterfactual (fake provider, 30 seeds)

Games-with-a-meeting by roster:

| Roster | Meeting rate | Parity kill-threshold | Crew task pool (1/crew) |
|--------|-------------|----------------------|-------------------------|
| 4p/1i (current) | ~10% | 2 kills | 3 |
| 5p/1i | 20% | 3 | 4 |
| 7p/1i | 53% | 5 | 6 |
| 10p/1i | 47% (all crew-task wins) | 8 | 9 |
| **7p/2i** | **63%** | 3 | 5 |
| 8p/2i | 57% | — | 6 |
| 10p/2i | 37% | 6 | 8 |
| 10p/3i | 7% | — | 7 |

Note: adding players *without* raising the task pool tilts hard to
`CREWMATE_TASKS` (10p/1i = all crew-task wins), so player count must rise *with*
the task pool. 10p/3i collapses meetings (parity too cheap relative to crew). The
sweet spot in this sweep is **7p/2i ≈ 63%**.

## 4. Key quantified findings

- Meetings: 4/50, all body-report; **0 emergency** meetings across 50 games.
- Actions across all 50 games: `do_task` 714, `move` 598, `wait` 274, `kill` 70, `report` 4; **0** emergency / vent / sabotage / repair_sabotage.
- 70 kills → 66 unreported bodies. Body present-but-unreported at game end in **46/46** no-meeting games.
- First-kill tick min 1 / median 3 / max 4. Game length min 4 / median 9 / max 12 (budget 1000).
- `CREWMATE_TASKS` games: exactly 1 kill each, report window (kill→end) median 5 ticks, 0 reports fired.
- `IMPOSTOR_PARITY` games: exactly 2 kills each; kill1→kill2 gap 5–8 ticks (gated by `kill_cooldown_ticks=4`).
- Crewmate-body co-location ticks: 4 total across 50 games = exactly the 4 meeting games; all 4 first-kills were in Cafeteria.
- Modeled task-rush window: 1 task/crew mean 10.9 ticks (8.1 after a kill); 2/crew ~20.6; 3/crew ~29.0.

## 5. Hypothesis scorecard (vs the project owner's three)

| Hypothesis | Verdict | Why |
|-----------|---------|-----|
| Low crew task requirement | **PRIMARY** | 1 task/crew + task-drop → crew wins at median tick 9; 28/50 games. |
| More players / 2 impostors | **PRIMARY (co-equal)** | Measured: 4p/1i 10% → 7p/2i 63%; fully wired, no code needed to flip roster. |
| Poor impostor play | **MINOR / refuted-as-framed** | Impostor kills fine (70/0/0); kills are too clean for the weak crew FSM; never sabotages. |
| (emergent) body-discovery/routing + dead emergency button | **CONTRIBUTING** | Same-room-only reports + hub-camping idle strand bodies; all 4 meetings were Cafeteria kills; emergency 100% dead. |

## 6. Implications for Phase 7

Agent-intelligence ("smarter agents") is **not measurable** until meetings happen
at volume. The fix is primarily **engine-balance/config** (more tasks + a larger
roster), secondarily an **agent-behavior** change (crewmate idle/discovery), and
only then the **agent-intelligence** content (richer detection, impostor tactics).
The Phase 7 plan + the project owner's locked decisions are recorded in
`tasks/phase-7-plan.md`.

## 7. Required closing fields

- **Root cause:** structural game-brevity (low crew task count + cheap parity at 4p/1i) + body-discovery gap; NOT poor killing.
- **Headline counterfactual:** 4p/1i ≈ 10% → 7p/2i = 63% meeting rate.
- **Method:** read-only diagnostic workflow, 4 angles, replay-data-grounded + measured roster sweep.
- **Follow-up:** `tasks/phase-7-plan.md`.
