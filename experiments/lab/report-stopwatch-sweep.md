# Stopwatch / task-clock retune sweep — what breaks the stopwatch?

*2026-06-22 (design thread). $0 fake-provider sweep over task/clock configs (`stopwatch_sweep.py`),
50 seeds/arm, 9p2i. Motivated by the Wave-C combined smoke (enriched perception): deduction quality
rose (vote accuracy 0.88) but the game stayed the **stopwatch** (8/8 `CREWMATE_TASKS`, 0 ejection-decided).
The task clock is the binding constraint; this finds the lever.*

## Method + its one limitation

The fake provider runs the full physical FSM (movement, tasks, kills, body-reports → meetings)
deterministically; only the meeting *resolution* is dead (no deduction → ~no ejections). So the sweep
measures **pacing + the no-deduction balance floor**: game length, meetings/game, kills, and whether
games end by `CREWMATE_TASKS` (crew out-task) vs `IMPOSTOR_PARITY` (impostor kills). The **real** balance
— with the crew's ~0.88 deduction — must be confirmed on a real-Ollama run; this narrows the levers first.

Three dead-crewmate-task rules tested (sim-only monkeypatch of `engine.tick._apply_kill`):
`drop` (engine default — kill deletes the victim's incomplete instances), `keep` (instances stay,
uncompletable), `redistribute` (instances re-key to a living crewmate, carrying progress).

## Results (50 fake seeds/arm)

| arm | dur | rule | mtg/game | kills | CREW_TASKS | IMP_PARITY | TIMEOUT |
|---|---|---|---|---|---|---|---|
| baseline (tpc2) | ×1 | drop | 2.3 | 4.7 | 39 | 11 | 0 |
| tpc3 | ×1 | drop | 1.7 | 2.8 | 47 | 3 | 0 |
| tpc4 | ×1 | drop | **0.1** | 0.2 | **50** | 0 | 0 |
| dur1.2 | ×1.2 | drop | 2.5 | 4.9 | 30 | 20 | 0 |
| dur1.5 | ×1.5 | drop | 2.6 | 5.4 | 19 | 31 | 0 |
| dur2.0 | ×2 | drop | 2.5 | 5.2 | 17 | 33 | 0 |
| keep | ×1 | keep | 2.4 | 4.6 | 0 | 7 | **43 (stall)** |
| **redistribute** | ×1 | redist | **3.7** | 6.5 | **3** | 47 | 0 |
| redist + dur1.5 | ×1.5 | redist | 3.4 | 5.9 | **0** | **50** | 0 |

## Findings

1. **More tasks/player is the *wrong* lever — decisively.** `tpc4` → 0 meetings, 0.2 kills, 100%
   stopwatch. Crew go heads-down and the engine still lets them cluster/finish, so the impostor
   isolates no one → no bodies → no meetings. Longer games, emptier.

2. **The mechanism: meetings come from kills; kills come from *isolated* crew.** So the lever is
   whatever makes crew *more killable*, not *busier*.

3. **Per-task duration is a clean, monotonic, dialable lever.** Stopwatch falls 39→30→19→17 as ×1.2→2,
   meetings hold (2.3→2.6), kills rise — longer tasks pin a crewmate isolated at a console.

4. **`keep` (uncompletable) removes the stopwatch but *stalls* in fake** (86% timeout): the crew can't
   finish, the impostor can't isolate idlers → 1000-tick budget. Fake can't score it (no deduction to
   break the stall).

5. **`redistribute` is the strongest lever — and the right one.** It **terminates** (0 timeouts, unlike
   `keep`), **doubles meetings** (2.3→3.7 — the biggest deduction-room gain of anything tested, and the
   metric the smoke said we lacked), and **removes the stopwatch** (`CREWMATE_TASKS` 39→3). The crew can
   no longer out-task by attrition; the only crew win path becomes **ejection** — i.e. deduction.

## The redirect

`redistribute` *alone* (×1) pushes the impostor to **94%** fake-parity; **redist + dur1.5 → 100%**. The
two levers compound, so with redistribute the duration knob is now the *wrong direction* — you want
durations **at baseline or shorter** to give the crew clock, not longer. Redistribute subsumes the
duration lever and adds the meeting-count win.

## Verdict + recommendation

- **`redistribute` at ×1 is the lever.** It converts the game into a pure **deduction-vs-kills race
  with no stopwatch escape** — the genre-correct dynamic, exactly the Wave-C goal — and it doubles the
  meeting count the crew need to deduce in.
- **Do not pair it with longer durations** (overshoots to 100% fake-parity); **do not raise
  `tasks_per_crewmate`** (empties the game).
- **The balance is the open question.** 94% fake-parity is the *no-deduction ceiling*; the real crew
  (0.88 vote accuracy, +60% meetings) will convert many parity-threats into ejection wins. Confirmed by
  one real-`qwen3.5:9b` run at redistribute ×1 → gate on `CREWMATE_TASKS` falling + `CREWMATE_EJECT`
  rising (deduction decides) + impostor staying balanced. If impostor-favored, dial durations *down* or
  soften redistribute (carry less progress / a fraction of tasks); if crew-favored, nudge durations up.

## Caveat for a real implementation

The redistribute probe reads roles in the engine to pick a living-crewmate recipient — fine here (the
engine already knows roles; this is a $0 sim patch). A production version of the rule must keep that
re-key **firewall-clean** (no role/attribution exposed to agents) and **deterministic** (lowest-id
recipient, as here) to preserve byte-replay.
