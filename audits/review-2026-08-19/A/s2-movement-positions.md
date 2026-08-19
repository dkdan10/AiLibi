# s2 — MOVEMENT / POSITIONS / PACING: corpus-wide mechanical sweep

Scope: all **300** committed replays — `replays/samples/4p1i` (50), `replays/samples/9p2i` (50),
`replays/ml_corpus/4p1i` (50), `replays/ml_corpus/9p2i` (150). Every set is the same build
(Qwen3.6-27B, prompt `*.qwen3_6_27b.v3`, policy `fsm-default`, identical substrate flags — per each
set's `MANIFEST.md`), so the four columns differ only by roster size and seed block.

Method: `api/replay_loader.py::ReplayLoader.load_replay` per-tick `agent_states`
(`room_id / current_action / is_venting / task_progress / visibility`) joined against the raw
JSONL `kind=tick` **action intents**, the map graph from `engine/maps/canonical_1.yaml`, and the
meeting records. Scripts:
`…/scratchpad/work/s2-movement-positions/{sweep.py,sweep2.py,sweep3.py,vents.py,idorder.py,whereabouts.py,whereabouts2.py,paths.py,final_checks.py,agg.py}`.

**Parser sanity check (required):** hand-verified against `watch.py` on two games before trusting
any aggregate — `replays/samples/9p2i` seed 2 (36 ticks, 9p/2i) and `replays/samples/4p1i` seed 7
(12 ticks, 4p/1i). Every counter reproduced by hand: seed 2 → 1 A→B→A→B window (p-7,
ENGINEERING↔EAST_HALL, t21–t24), IDLE runs `{IMPOSTOR:[4,3], CREWMATE:[7,11]}` (p-8 t29–t35,
p-9 t25–t35), 4 vent events, 51 impostor + 147 crew living agent-ticks, 8 escort pairs including
p-8+p-9 in CAFETERIA t28–t35; seed 7 → 4 MOVING-without-motion ticks, one 8-tick crew IDLE run
(p-4, t4–t11), 2 vent events, 0 witnessed. Two metrics were **corrected after the check** and the
corrected numbers are what is reported below (see Q2 and the note under §2.6).

---

## 1. Corpus shape and pacing

| metric | samples/4p1i | samples/9p2i | ml/4p1i | ml/9p2i |
|---|---|---|---|---|
| games | 50 | 50 | 50 | 150 |
| ticks/game mean · median · range | 12.6 · 12 · 5–27 | 34.4 · 34 · 13–68 | 11.6 · 11 · 5–19 | 29.9 · 27 · 11–65 |
| meetings/game | 0.78 | 3.30 | 0.80 | 3.09 |
| kills/game | 1.22 | 3.54 | 1.10 | 3.37 |
| first-kill tick (mean; min observed = 4 everywhere) | 5.3 | 4.9 | 5.4 | 5.4 |
| **"dead" ticks** (no kill/report/vent/task-completed/meeting/sabotage) | **61.4 %** | **48.6 %** | **59.8 %** | **45.9 %** |
| ticks after the last meeting (mean) | 4.2 | 2.8 | 3.2 | 2.1 |
| games that END on a meeting tick | 28 % | 68 % | 42 % | 74.7 % |
| games with 0 meetings | 22 % | 0 % | 20 % | 0 % |
| win: CREWMATE_EJECT / CREWMATE_TASKS / IMPOSTOR_PARITY | 20/46/34 % | 62/8/30 % | 40/38/22 % | 70.7/4.0/25.3 % |

Pacing is *not* the problem it looks like from the tail: the dead tail after the last
kill-or-meeting averages 0.3–1.8 ticks, and 68–75 % of 9p2i games end on the meeting tick itself.
The dead time is spread **through** the game, not parked at the end. [VERIFIED]

## 2. Movement mechanics

| metric | samples/4p1i | samples/9p2i | ml/4p1i | ml/9p2i |
|---|---|---|---|---|
| living agent-ticks | 2 155 | 10 420 | 2 013 | 28 253 |
| room changes (hops) | 903 | 3 940 | 825 | 10 785 |
| **non-adjacent moves ("teleports")** | **0** | **0** | **0** | **0** |
| A→B→A→B 4-tick oscillations | 26 | 173 | 1 | 384 |
| … per 1000 hops | 28.8 | 43.9 | 1.2 | 35.6 |
| games with ≥1 A→B→A→B | 5/50 | **30/50** | 1/50 | **83/150** |
| A→B→A backtracks (3-tick) | 57 | 378 | 26 | 923 |
| DTO says MOVING but the room did not change | 130 | 492 | 130 | 1 212 |
| rejected `move` intents (100 % on a meeting tick, all sets) | 27 | 227 | 23 | 634 |
| distinct rooms visited / agent | 3.37 | 4.67 | 3.29 | 4.49 |
| agent-ticks in hallways / in CAFETERIA | 17.9 % / 18.1 % | 17.1 % / 25.8 % | 17.3 % / 19.9 % | 17.3 % / 23.9 % |

**2.1 The movement engine itself is clean.** [VERIFIED] Zero of the 16 453 room changes in the
corpus were between non-adjacent rooms once vent traversals are excluded, and **every** rejected
`move` intent in the corpus (911/911) is a meeting-tick freeze, never an illegal target. The FSM
never proposes a move it cannot make. No teleport bug exists.

**2.2 Path efficiency splits hard by role.** [VERIFIED] Per maximal run of consecutive `move`
intents, hops taken vs. BFS shortest path over `canonical_1.yaml` edges:

| set | role | move-runs | hops taken | hops needed | runs over shortest | wasted hops |
|---|---|---|---|---|---|---|
| samples/4p1i | CREWMATE | 207 | 522 | 515 | 1.9 % | **1.3 %** |
| samples/4p1i | IMPOSTOR | 138 | 372 | 222 | 32.6 % | **40.3 %** |
| samples/9p2i | CREWMATE | 1 050 | 2 691 | 2 423 | 14.0 % | **10.0 %** |
| samples/9p2i | IMPOSTOR | 429 | 1 361 | 640 | 44.5 % | **53.0 %** |
| ml/4p1i | CREWMATE | 194 | 487 | 478 | 3.6 % | 1.8 % |
| ml/4p1i | IMPOSTOR | 138 | 329 | 221 | 26.1 % | 32.8 % |
| ml/9p2i | CREWMATE | 2 931 | 7 419 | 6 741 | 13.2 % | 9.1 % |
| ml/9p2i | IMPOSTOR | 1 174 | 3 632 | 1 848 | 44.1 % | **49.1 %** |

Crewmates walk essentially straight lines (their 9–10 % excess in 9p2i is re-targeting after a task
is redistributed or a body pulls them). Impostors waste **half of every hop they take**. The
excess is not scenic routing, it is a two-room pendulum (§3, D3).

**2.3 "MOVING" while the token does not move — 1 964 agent-ticks corpus-wide.** [VERIFIED]
Decomposed by the actual submitted intent that tick: `do_task` 934, `move` 583 (all meeting-tick
freezes), `kill` 145, `repair_sabotage` 95, `report` 90, `wait` 72, `emergency` 31, `sabotage` 11,
`vent` 3. `AgentTickStateView.current_action` (api/schemas.py:249) simply keeps the last
*resolved* label, so anything the engine rejected or has no enum value for renders as the previous
action.

## 3. Idle time, dead time, co-presence

| metric | samples/4p1i | samples/9p2i | ml/4p1i | ml/9p2i |
|---|---|---|---|---|
| CREWMATE agent-ticks IDLE | 13.9 % | 17.5 % | 11.4 % | 14.6 % |
| IMPOSTOR agent-ticks IDLE | 0.5 % | 15.6 % | 2.2 % | 15.4 % |
| crew IDLE runs ≥3 ticks **with all own tasks done** | 16 | 110 | 18 | 269 |
| ticks inside those runs / all living agent-ticks | **5.7 %** | **10.3 %** | **4.6 %** | **8.0 %** |
| longest such run | 17 (seed 8, p-4) | **36 (seed 32, p-9)** | 7 | 28 (seed 1016) |
| agent-ticks completely alone in a room | 68.5 % | 38.5 % | 62.3 % | 37.9 % |
| mean co-present others | 0.39 | 1.06 | 0.51 | 1.08 |
| pair co-presence runs ≥4 ticks / game | 0.76 | 10.6 | 0.86 | 10.2 |
| impostor CAFETERIA loiter runs ≥3 ticks (longest) | 2 (4) | 68 (12) | 2 (6) | 185 (13) |
| impostor stands in a room with a body ≥2 ticks | 39 | 139 | 35 | 432 |
| 2 impostors in the SAME room (of both-alive ticks) | — | **17.9 %** | — | **19.6 %** |

## 4. Impostor action outcomes

| metric | samples/4p1i | samples/9p2i | ml/4p1i | ml/9p2i |
|---|---|---|---|---|
| kill attempts | 64 | 225 | 57 | 640 |
| kills landed | 61 | 177 | 55 | 505 |
| **whiff: target left the room that tick** | 3.1 % | **18.7 %** | 1.8 % | **17.3 %** |
| kill annihilated by a meeting elsewhere | 1.6 % | 2.7 % | 1.8 % | 3.8 % |
| impostor FAKE `do_task` intents | 119 | 415 | 112 | 1 101 |
| … rendered TASK in the spectator DTO | **0** | **0** | **0** | **0** |
| … rendered IDLE / MOVING | 0 / 107 | 200 / 203 | 0 / 104 | 600 / 430 |

## 5. Vents, bodies, meetings

| metric | samples/4p1i | samples/9p2i | ml/4p1i | ml/9p2i |
|---|---|---|---|---|
| vent ENTERs | 37 | 125 | 34 | 393 |
| … someone alive at either endpoint room | 2 | 17 | 3 | 48 |
| … **seen by a CREWMATE** | 1 (2.7 %) | 11 (**8.8 %**) | 2 (5.9 %) | 25 (**6.4 %**) |
| vent EXITs | 36 | 115 | 32 | 368 |
| … someone alive at either endpoint room | 17 | 85 | 21 | 275 |
| … **seen by a CREWMATE** | 10 (27.8 %) | 65 (**56.5 %**) | 19 (59.4 %) | 218 (**59.2 %**) |
| `saw_vent` rows cited in meetings | 11 | 164 | 20 | 553 |
| `vent_sighting` contradictions raised | 11 | 96 | 20 | 313 |
| bodies created | 61 | 177 | 55 | 505 |
| **bodies NEVER reported** | **42.6 %** | 14.7 % | **47.3 %** | 18.6 % |
| report latency mean / median / max (ticks) | 4.8 / 4 / 12 | 5.3 / 4 / **29** | 3.8 / 4 / 7 | 5.3 / 4 / **30** |
| crew leaves a body room WITHOUT reporting | 0/37 | 0/170 | 0/31 | 0/462 |
| meetings | 39 | 165 | 40 | 463 |
| … with ALL living agents in the CAFETERIA | **0 %** | **0 %** | **0 %** | **0.6 %** |
| … mean fraction of living agents in CAFETERIA | 0.26 | 0.27 | 0.28 | 0.27 |
| … fraction in CAFETERIA the tick AFTER (→ no reset) | 0.15 | 0.19 | 0.10 | 0.17 |
| … with ≥1 participant INSIDE A VENT | 2.6 % | **9.7 %** | 5.0 % | **10.8 %** |
| `task_progress` DECREASES (teammate died → redistribute) | 25 | 117 | 21 | 322 |

---

# RANKED FINDINGS

## BUG — B1. Contested kills are decided 100 % by player number (246/246)

[VERIFIED] Across all 300 games there are **246 kill attempts in which the victim submitted a
`move` on the same tick**. Every single one resolved by seat order, with no exceptions:

| victim id vs. killer id | outcome | n |
|---|---|---|
| victim **lower** (e.g. p-4 fleeing p-8) | **escaped** | **156 / 156 (100 %)** |
| victim **higher** (e.g. p-8 fleeing p-4) | **died** | **90 / 90 (100 %)** |

That is 25 % of all 986 kill attempts in the corpus. Exemplars (raw dump lines):

```
samples/9p2i seed 0  t4   killer=p-8 target=p-4  both in CAFETERIA at t3, p-4 moves to WEST_HALL   -> ESCAPES
samples/9p2i seed 0  t15  killer=p-8 target=p-1  both in EAST_HALL at t14, p-1 moves to ENGINEERING -> ESCAPES
samples/4p1i seed 0  t11  killer=p-3 target=p-1  both in LABS at t10, p-1 moves to MEDBAY           -> ESCAPES
```

`DESIGN.md` §3.4 does document this: *"Intra-tick simultaneity is canonically id-ordered … a
lower-id target's same-tick move legitimately escapes a kill. This is the documented rule, not a
race (2026-06-07 audit decision); revisit only if a future wave gates on per-seat fairness."* The
corpus says the "future wave" condition is already met: this is not a rare tie-break, it is a
**deterministic per-seat immunity** covering a quarter of all kill attempts. p-1 can always outrun
anyone; p-9 can never outrun anyone. Any per-seat statistic in the ML corpus (survival, suspicion
rank, victim priors) is contaminated by it. Same mechanism, second symptom: **26/26** vent
sightings attributed to an observer who is standing in neither vent endpoint room at the end of the
tick have `observer_id > venter_id` — the observer was in the room when the vent resolved and moved
away later in the same tick (`engine/rules.py:29-44` `_witnesses_in_room` reads pre-move state).
Severity: **high** — silent fairness break + it makes replay frames look like a visibility leak.
*Idea:* resolve movement for all actors first, then kills/vents against the post-move world; or
randomise the intra-tick actor order per tick from the game seed and record it.

## BUG — B2. Two different clocks inside the same prompt

[VERIFIED] The tick number an agent's own memory stamps on a perception is **one greater** than the
replay/spectator tick index of that event, but the meeting prompt header uses the replay index.

* `saw_vent` observations: **740/748** corpus-wide are stamped `event_tick + 1` (1 exact, 7 matching neither tick).
* `completed_task` observations: **785/853** stamped `event_tick + 1`; **zero** exact matches in any set.
* Meeting prompt header `"It is tick N"`: **771/771** LLM calls equal the replay's meeting tick exactly.

Exemplar, `samples/9p2i` seed 8. Replay: the vent event fires at **t7**
(`EVENT vent: {'actor_id': 'p-3', 'phase': 'enter', 'from_room_id': 'ADMIN', …}` at `[t  7]`), the
report at **t8**. The prompt p-1 is actually shown (raw `llm_calls[0].prompt`):

```
## This meeting
It is tick 8 and a meeting just started: p-1 reported body body-p-6-6 at tick 8.
…
- [obs p-1:8:3] [tick 8] You discovered p-6's body in ADMIN.
- [obs p-1:8:1] [tick 8] You witnessed p-3 vent in ADMIN.
```

Both perceptions really happened at replay t7, and "now" really is replay t8 — but every number in
the prompt reads 8. In a game whose entire evidence currency is *"where were you at tick N"*, the
model is being handed a timeline in which the present and the previous tick share a label. It also
means a spectator reading the transcript beside the tick timeline can never line the two up.
Severity: **high** (contaminates the contradiction detector's inputs and every audit that quotes a
tick). *Idea:* stamp observations with the tick of the world they describe, and assert
`obs.tick <= meeting.tick - 1` in a test.

## BUG — B3. The spectator `current_action` misrepresents four whole action classes

[VERIFIED] `AgentTickStateView.current_action` is a 7-value enum with no `EMERGENCY` and no
`REPAIR`, and it is never updated for a rejected intent. Corpus totals:

| what the agent actually submitted | what the spectator DTO shows | n |
|---|---|---|
| impostor fake `do_task` (1 747 total) | IDLE 800 / MOVING 844 / **TASK 0** | 1 747 |
| `emergency` (button press) | **REPORT** 81 / MOVING 31 | 112 |
| `repair_sabotage` | TASK 302 / MOVING 95 / IDLE 11 | 408 |
| any intent on a meeting tick | previous tick's label | 1 964 total MOVING-without-motion |

The fake-task case is the sharpest: co-located crewmates *do* see the impostor as
`action="task"` (`observation/service.py:438-455`, the Task 13.9 fake-task lever) — I see it in the
visibility frames, e.g. `samples/9p2i` seed 2 t2 `p-5 sees players=['p-4@ENGINEERING:task', …]` —
while the omniscient spectator dump shows `p-4*@ENGINEERING:MOVING`. So the replay viewer makes
the impostor look like it is aimlessly wandering at exactly the moments it is successfully
pretending to work. Severity: **medium** (spectator-surface only, no gameplay effect), but it
directly undercuts the Phase-12 viewer's job of making the deception legible.
*Idea:* project the observation layer's `_ObservedAction` into the DTO (adding `PRETEND_TASK`,
`EMERGENCY`, `REPAIR`, `BLOCKED`) rather than the resolved engine label.

## DESIGN HOLE — D1. The meeting is a disembodied conference call

[VERIFIED] Over **707 meetings**: all living agents were in the Cafeteria in **0/39, 0/165, 0/40
and 3/463** of them; mean fraction present 0.27; the fraction is *lower* the tick after
(0.10–0.19), so no reset happens either. Nothing in `DESIGN.md` §5.1 asks for it — it only
"freezes engine state" — yet `canonical_1.yaml` declares `meeting: room: CAFETERIA` and
`emergency: button_room: CAFETERIA`, and the map notes call the Cafeteria "meeting room, emergency
button, agent spawn". The declared meeting room is never enforced on bodies.

Two consequences I can point at:

1. **9.8 % of meetings (69/707) have at least one speaker physically inside a vent.**
   `samples/9p2i` seed 8, t8: `p-3*@ADMIN:VENT(VENTING)`, and in the same meeting p-3 says
   > `Glitch. P-1 entered ADMIN at tick 8. Suspicious timing.`
   and votes with the rationale
   > `[under-gate eject target 'p-1' redirected] P-1 lies about the vent. I didn't vent. Vote him.`
   — while mid-traversal in the ADMIN vent. (`ml/9p2i` seed 1001 meeting-0 has **two** venting
   participants, p-2 and p-3.)
2. **The impostor resumes standing next to its next victim.** `samples/9p2i` seed 2: meeting-0
   resolves at t7 (`ejected=None`); `[t 8] … p-4*@STORAGE:KILL … EVENT kill: {'killer_id': 'p-4',
   'victim_id': 'p-6', 'room_id': 'STORAGE'}`. p-6 spoke at that meeting and was murdered one tick
   later without moving.

Severity: **high for believability**. *Idea:* on a meeting trigger, teleport every living agent to
`meeting.room` (forcing a vent exit), and on resolution either leave them in the Cafeteria (classic
Among Us, and it would kill D2 as a side effect by re-scattering everyone) or restore positions
explicitly and say so in DESIGN §5.1.

## DESIGN HOLE — D2. A crewmate who finishes its tasks becomes a statue

[VERIFIED] **10.3 %** of ALL living agent-ticks in `samples/9p2i` (1 074/10 420) and **8.0 %** in
`ml/9p2i` (2 267/28 253) are a crewmate standing IDLE with `task_progress == 1.0`. There is no
end-of-tasks behaviour at all: no emergency button, no escorting, no body sweep, no shadowing a
working teammate.

The showcase is `samples/9p2i` seed 32 (58 ticks, IMPOSTOR_PARITY). From t20 onward:

```
[t 20] tasks 9/14 | p-4@STORAGE:TASK tp=0.40  p-5*@EAST_HALL:MOVING  p-7@CAFETERIA:IDLE tp=1.00  p-8@CAFETERIA:IDLE tp=1.00  p-9@CAFETERIA:IDLE tp=1.00
…
[t 41] … p-5*@MEDBAY:KILL  p-7@CAFETERIA:IDLE tp=0.46  p-8@CAFETERIA:IDLE tp=1.00  p-9@CAFETERIA:IDLE tp=1.00 | dead: p-1,p-2,p-3,p-4,p-6
[t 48] … p-5*@MEDBAY:KILL  p-8@CAFETERIA:IDLE tp=0.61  p-9@CAFETERIA:IDLE tp=1.00 | dead: …,p-7
[t 57] … p-5*@ADMIN:KILL  p-9@ENGINEERING:MOVING tp=0.61 | dead: …,p-8
```

p-9 stands still in the Cafeteria for **36 consecutive ticks** (t20–t55) while its three remaining
teammates are murdered one at a time; the crew loses on parity with 12/14 tasks. `samples/4p1i`
seed 8 is the same shape at small scale: p-4 IDLEs in the Cafeteria for **17 of the game's 22
ticks** (t5–t21). Severity: **high** — it is both the single largest source of dead time and the
reason the crew never contests the map after the mid-game. *Idea:* an explicit "finished" FSM state
— patrol unvisited rooms, tail the nearest living crewmate, or walk to the button.

## DESIGN HOLE — D3. The impostor's idle policy is a visible two-room pendulum

[VERIFIED] The impostor's 40–53 % wasted-hop figure (§2.2) is almost entirely A↔B shuttling: 173
four-tick A→B→A→B windows in `samples/9p2i` (30/50 games) and 384 in `ml/9p2i` (83/150 games).
Worst cases:

```
samples/9p2i seed 32, p-5* :  t18 EAST_HALL  t19 ADMIN  t20 EAST_HALL  t21 ADMIN  t22 EAST_HALL
                              t23 ADMIN  t24 WEST_HALL … t38 ADMIN  t39 WEST_HALL
                              -> 22 consecutive pendulum ticks in a 58-tick game
                              (one recorded move-run: ADMIN -> MEDBAY, 33 hops, shortest = 2)
samples/4p1i seed 8,  p-1* :  t8 WEST_HALL t9 MEDBAY t10 WEST_HALL t11 MEDBAY t12 WEST_HALL
                              t13 ADMIN t14 WEST_HALL … t21 ADMIN
                              -> 14 of the game's 22 ticks spent oscillating in empty corridors
```

This is the most obviously non-human behaviour in the corpus. It is also *free evidence the crew
can never use*: nothing in the perception layer records "p-1 crossed this corridor nine times", and
`movement_perception` only surfaces a single from→to transition per tick.
*Idea:* replace the "no target → shuttle" fallback with a dwell (loiter in a task room and fake a
task, which the crew CAN see as `task`), and/or add a `paced_room` perception row so pendulum
behaviour becomes an accusable tell.

## DESIGN HOLE — D4. Vent evidence exists only at the emerge, never at the dive

[VERIFIED] Dives are effectively invisible, emerges are usually seen:

| | samples/9p2i | ml/9p2i |
|---|---|---|
| vent ENTER seen by a crewmate | 11/125 = **8.8 %** | 25/393 = **6.4 %** |
| vent EXIT seen by a crewmate | 65/115 = **56.5 %** | 218/368 = **59.2 %** |

Mechanically this is correct and documented — `DESIGN.md` §3.4 *"Vent use is observable to living
non-vented players in the source/destination room"*, implemented same-room-only in
`engine/rules.py:29-44`. [JUDGMENT] The *consequence* is a design hole: the impostor dives from
exactly the rooms `canonical_1.yaml` designed to be lonely ("Storage is doubly isolated… the
canonical 'body found here' crime scene"; "Reactor… Long task here invites kills"), so the dive is
never witnessed, and the only vent evidence the crew ever gets is "he came out of a wall over
here" — decoupled from the body. That is why the 748 `saw_vent` rows and 440 `vent_sighting`
contradictions in the corpus read as teleport-sightings rather than as kill-adjacency. *Idea:*
make the dive audible one room further (there is already an `AudibleEvent(kind='vent_use_heard')`
channel — it currently fires only for the same-room witness), or leave a short-lived "vent recently
used in ROOM" trace an entering crewmate can pick up.

## DESIGN HOLE — D5. Bodies rot; the crew never patrols

[VERIFIED] **42.6 %** (samples/4p1i) and **47.3 %** (ml/4p1i) of bodies are never reported at all;
14.7 % / 18.6 % in the 9p2i sets. Median latency 4 ticks, max **30** (`ml/9p2i` seed 1148) and
**29** (`samples/9p2i` seed 6). This is NOT a reporting-logic failure: **0 of 700** crew agent-ticks
in a body room ended with the crewmate walking away un-reported — the rule is "arrive at t, report
at t+1", exceptionlessly. The bodies rot because nobody ever goes back to that room. Combined with
D2 (finished crew stop moving) this is the same hole seen from the other side. *Idea:* a finished
crewmate's patrol (D2) would close most of this on its own.

## DESIGN HOLE — D6. The meeting tick silently eats every other intent, kills included

[VERIFIED] By design (`DESIGN.md` §5.1 "Freezes engine state (no movement, no kills, cooldowns
paused)", and `orchestrator/game.py:1187` cites it), but three things are worth naming: (a) it is
the *only* thing that ever rejects an action — 911/911 rejected moves, 727 crew
`do_task` intents that made no progress, 75 `vent`, 90 `report`; (b) **32 kill attempts corpus-wide
(2.7 % / 3.8 % of 9p2i attempts) were
annihilated by a meeting happening somewhere else on the map**, and the impostor paid no cooldown
for it; (c) none of this is projected into the replay's tick events (there is no `ActionRejected`
in `TickEventView`), so from the spectator timeline it looks like the agent simply stood still.
Exemplar `samples/9p2i` seed 2: raw intent at t7 is
`{'actor': 'p-4', 'payload': {'target': 'p-6'}, 'type': 'kill'}` — dropped by p-1's report from the
Cafeteria — and re-issued identically at t8, where it lands.

## DESIGN HOLE — D7. Impostor pairs travel together and nothing notices

[VERIFIED] In 9p2i the two impostors are in the same room **17.9 %** (samples) / **19.6 %** (ml) of
the ticks they are both alive. [JUDGMENT] In human play "those two are always together" is a
primary tell; here neither the perception layer nor the belief layer has any notion of repeated
co-presence, so the impostors pay nothing for it while looking mechanical to a spectator.

---

## QUALITY (not broken, but weak)

* **Q1. Half of every game is empty.** 48.6 % / 45.9 % of 9p2i ticks and 61.4 % / 59.8 % of 4p1i
  ticks contain no kill, report, vent, task-completion, meeting or sabotage. [VERIFIED]
* **Q2. Impostor kill *opportunism* is essentially perfect — and my first pass said otherwise.**
  With a naive cooldown model (ready whenever ≥4 ticks since the last kill) I counted 161 ≥2-tick
  "missed kill" windows. Modelling the real rule (seeded to `kill_cooldown_ticks=4` at spawn — the
  earliest kill anywhere in the corpus is t4 and the smallest same-impostor gap is 5 — and **paused
  during meetings**, §5.1) collapses it to **exactly ONE window in 300 games**: `ml/9p2i` seed 1145,
  p-1 alone with p-3 in ADMIN at t32–t33 with a ready cooldown, no adjacent witness, and no kill.
  The impostor never sits on a ready knife. [VERIFIED]
* **Q3. The kill decision lags perception by one tick.** 156 attempts (18.7 % of `samples/9p2i`,
  17.3 % of `ml/9p2i`) fire at a victim who leaves that same tick — i.e. the impostor is aiming at
  last tick's picture. Exemplar `samples/9p2i` seed 2: p-7 arrives in MEDBAY at t29 where p-3 is,
  submits `{'type':'kill','payload':{'target':'p-3'}}` at t30, and p-3 has already walked to
  WEST_HALL. (Whether the target then escapes is B1's coin-flip-by-seat.) [VERIFIED]
* **Q4. Nobody escorts anybody.** 38.5 % of 9p2i and 68.5 % of 4p1i agent-ticks are spent alone;
  mean co-present others 1.06 / 0.39. The "≥4-tick pair" runs are task co-location or shared idling,
  not protection: the longest in `samples/9p2i` is p-8+p-9 for **34 ticks** (seed 17) — both IDLE in
  the Cafeteria with tasks done. [VERIFIED]
* **Q5. `task_progress` runs backwards.** 485 decreases corpus-wide, all caused by
  `dead_task_rule: redistribute` re-keying a dead crewmate's instances and growing the survivor's
  denominator. `samples/4p1i` seed 6 t5: p-1 goes `tp=0.75 → tp=0.70` on the tick p-2 is murdered,
  having done nothing wrong. Documented in `canonical_1.yaml` (the Wave-D lever), but a progress bar
  that goes down reads as a bug in the viewer. [VERIFIED / by design]
* **Q6. One in five crew self-alibis is positionally false.** Under the most generous tick reading
  (claim matches the speaker's room at the claimed tick *or* the claimed tick − 1): CREWMATE
  `whereabouts` rows are false 148/723 = **20.5 %** (`samples/9p2i`) and 402/2038 = **19.7 %**
  (`ml/9p2i`); impostors 47.5 % / 46.2 % (that is them lying, which is intended). Exemplar
  `samples/4p1i` seed 32: p-3 claims `WEST_HALL@t8` and says
  > `I-I mean, look, I was right there with p-1 in WEST_HALL at tick 7, so they couldn't possibly have been in ADMIN to kill p-4, not unless they can teleport…`
  while actually standing in MEDBAY at both t7 and t8. [VERIFIED] — flagged for the testimony track
  (s1/s3); recorded here because it is a *positional* falsehood and it is exactly what the
  contradiction detector consumes.

## Things that are demonstrably FINE (worth not re-litigating)

* Zero teleports in 16 453 room changes; zero illegal move targets in 986+4 970+… intents. [VERIFIED]
* Crew pathing is near-optimal (1.3–1.8 % wasted hops in 4p1i, 9–10 % in 9p2i). [VERIFIED]
* Crew reporting is exceptionless: 0/700 walk-aways from a visible body. [VERIFIED]
* Games do not drag after the decision: mean 0.3–1.8 ticks of tail after the last kill/meeting;
  68–75 % of 9p2i games end on the meeting tick. [VERIFIED]

## Top 5 changes, in the order I would make them

1. **Resolve movement before kills/vents (or seed-randomise the actor order per tick)** — kills B1
   outright and removes the phantom "vent seen from the wrong room" frames.
2. **Give a finished crewmate something to do** (patrol / tail / button) — one change closes D2, most
   of D5, a large slice of Q1, and the "38 % alone" figure.
3. **Physically gather agents in the Cafeteria for the meeting** — closes D1 (venting speakers,
   next-tick executions from the same square) and re-scatters everyone afterwards.
4. **Unify the observation clock and assert it in a test** (B2) — cheap, and every downstream audit
   that quotes a tick depends on it.
5. **Replace the impostor's pendulum with a dwell/fake-task loiter, and project the real action into
   the spectator DTO** (D3 + B3) — the same two edits make the impostor look like a person to a
   viewer and give the crew something to accuse.
