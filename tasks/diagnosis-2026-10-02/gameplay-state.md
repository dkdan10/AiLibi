# Gameplay state after Stage-B round 2: is it a good Among-Us-like game yet?

Investigator memo, topic `gameplay_state`, 2026-10-02. Read-only on `main` at `d41c9006` (detached worktree). No
model call, no recorder, no commit, no tracked file edited, no `.env` read, 0 `AILIBI_*` exports in the shell. No
prompt was printed. Model speech appears only as five short paraphrases in section 6; each original excerpt was
checked word for word by a script that prints True or False. Every census below is count-only and keyed by
(set, meeting).
Role-correctness is reported here to describe the games. It gates nothing, and nothing here feeds back to any agent.

**Three columns, never pooled.** `s9` is `replays/samples/9p2i` at baseline 9. `r1` is
`replays/candidates/stage-b-r1/9p2i`, the eight Stage-B arms. `r2` is `replays/candidates/stage-b-r2/9p2i`, the
same arms plus `kill_cooldown_ticks = 6`. All three use the same 50 seeds (0-49) of the 9-player, 2-impostor roster.
r1 and r2 differ in one key. Each is a single hosted recording, so any r1-to-r2 difference is the dial's only within
hosted-generation noise (`audits/audit-2026-10-01-stage-b-r2.md:1430-1434`).

---

## 0. Verdict in one screen

- **The game's mechanics are now in a good, genre-like state.**
  - Every conformance cell reads 0, including the cooldown cell at all three writers
    (`audits/audit-2026-10-01-stage-b-r2.md:1278-1300`, `:1363-1371`).
  - Games run about 39 ticks with 2.3 meetings.
  - They end three ways: 13 crew wins by ejection, 13 crew wins by tasks and 24 impostor wins by parity.
  - Bodies are fresh when found: 0 stale reports, and every corpse is at most 11 ticks old.
  - Every regroup clears the floor and pulls impostors out of the vents. No kill lands inside the grace window.
  - A vent is now risky only when a crewmate walks in on the same tick.
  - Balance sits inside the envelope: 24/50 = 0.48 (0.35-0.61).
- **The process side holds.**
  - 407/410 EJECT ballots are grounded (`:1263`), and rationale faithfulness is 580/580 (`:1271`).
  - Crew whereabouts claims are true in 628 of 632 (honesty command, section 11).
- **One gameplay flaw remains, and it is in the meeting layer, not the engine.** I call it the reporter trap.
  - An innocent body reporter is voted out in 17 of 114 report meetings, 0.149 (0.10-0.23). This is the
    envelope's only flag, and it is why the round-3 rule names no step (`:1379`, `:1386-1389`).
  - **New here:** in 12 of those 17, the reporter's opening had accused the real impostor on a sighting that the
    engine confirms. 10 of the 24 impostor wins ran through such an ejection.
  - The ejections are crew-driven: a crew-only tally would still have ejected the reporter in 15 of 22 innocent
    ejections.
  - The excerpts show the cause: a walkable route is called impossible, the same failure baseline 9 had
    (analysis memo Q6).
  - Under ruling D1 these ballots are "wrong but believable" (scorecard row 8, 189/410), so the game is working as
    designed. For the genre and for a showable tour, they are the game at its worst.
- **Nothing is broken in code.** Three things must be fixed before round 2 can be shown, all outside the recording:
  - The viewer has no beat for the regroup: survivors jump to the hub with no on-screen reason.
  - The public-results page has no words for the kill cooldown (`PublicResults.tsx:8-21`).
  - The 9-player featured strip would be wrong on round-2 bytes. Its head (seed 23) fails the measured criterion,
    and its labels count meetings that no longer happen.
- **Showability.** 11 of 50 round-2 games qualify as a tour head under the spectator card's measured criterion:
  seeds 3, 5, 6, 7, 10, 11, 19, 20, 27, 42 and 49.
  - Best heads: seed 7 (a vent sighting, then a kill witness) and seed 19 (a vent sighting, a skip, then a kill
    witness).
  - Worst games: 4, 36, 15 and 31 establish nothing. Seed 48 ejects two innocent reporters back to back.
    Seeds 2 and 12 end at tick 22 after one wrong ejection.

---

## 1. How a game runs (Q1)

Source: `walk2.py` (a per-tick walk through `eval.replay_walk.walk_replay` with the census profile, which verifies
every state hash) and `q1.py`. Section 11 gives the commands.

| | s9 | r1 | r2 |
|---|---|---|---|
| games ending: crew by ejection / crew by tasks / impostor parity | 38 / 1 / 11 | 12 / 4 / 34 | **13 / 13 / 24** |
| game-over tick: mean (median, range) | 22.2 (20, 11-48) | 32.8 (29.5, 15-61) | **38.8 (35, 20-66)** |
| meetings per game (spread) | 2.90 (1:5, 2:14, 3:15, 4:13, 5:3) | 2.48 | **2.34 (1:7, 2:23, 3:16, 4:4)** |
| meetings opened by a report / by the button | 135 / 10 | 118 / 6 | 114 / 3 |
| first meeting, median tick | 8 | 8 | 11 |
| kills per game; first kill, median tick | 3.50; 4.5 | 4.54; 4.5 | 3.90; 7 |
| sabotages started (games with any) | 8 (7) | 15 (13) | 46 (32) |

**Mean game-over tick by ending.** r2: crew ejection 34.5, tasks 42.2, impostor parity 39.2. s9: ejection 20.7 and
parity 26.3.

**The rhythm the arms produce.**

- **The round start.** The 6-tick cooldown applies from the first tick (round-start writes, 100 of 100), so the
  first kill comes at a median tick of 7 instead of 4.5.
- **The grace window.** After every regroup the grace window holds: 0 of 109 post-meeting kills fall at T+1 to T+6.
- **The kill wave.** The kills arrive as a wave just after the window closes. Of the 109 post-meeting kills, 70 land
  at T+7 to T+10 (exact spread: 7:23, 8:20, 9:17, 10:10, 11:8, then a tail).
  - That matches the genre: in Among Us the kill cooldown restarts after every meeting.
  - On s9, 28 of 87 post-meeting kills landed within 2 ticks.
- **Sabotage.** It is now visible: 46 sabotages in 32 games. It is the impostors' stall near a task win, and it
  appears in all 13 task wins (section 7). Sabotage never ends a game.
- **The button.** It has nearly gone, from 10 button meetings to 3. On baseline 9 every button meeting carried vent
  proof (`docs/gameplay-census.md:131`), so the button was effectively a vent-witness button. Seen vents are now
  rare, so the button is too.

**Verdict.** Fine. This is the right shape for the genre. Games are longer, kills are paced by a visible cooldown,
the three ways to end all occur, and the trigger-tick and regroup rules hold.

---

## 2. How impostors get voted out (Q2)

**The five-way split.** Each ejection goes into the highest band it reaches:

1. vent flag (scorecard row 5's `vent_flag` band);
2. kill sighting (a living crewmate who saw that player kill, or a served own-kill row naming them);
3. contradiction (a non-vent flag);
4. first-hand sighting (the rest of row 5's `first_hand` band);
5. accusation only (row 5's hearsay or unevidenced bands).

`bands.py` records row 5's own classifier (`eval/process_scorecard.py:1134-1166`, unchanged) per meeting, and
`q2.py` adds the kill-sighting split. The row-5 totals reproduce the audit (`audits/audit-2026-10-01-stage-b-r2.md:1270`).

| ejections (of which impostors) | s9 | r1 | r2 |
|---|---|---|---|
| vent flag | 70 (70) | 24 (24) | **24 (24)** |
| kill sighting | 2 (2) | 3 (3) | **8 (8)** |
| first-hand sighting | 14 (8) | 24 (11) | **31 (12)** |
| contradiction | 2 (1) | 2 (0) | 2 (0) |
| accusation only | 2 (0) | 1 (1) | 1 (0) |
| **all** | 90 (81) | 54 (39) | **66 (44)** |

**What changed.** The vent tell went from 78% of ejections (70/90) to 36% (24/66).

- Both channels that are certain are perfect: the vent flag is 24 of 24 and the kill sighting 8 of 8.
- **The kill-witness channel has grown into a real second channel.**
  - 14 of 195 kills were seen by crew (s9: 3/175).
  - All 14 seen kills were held by a living witness at the next meeting. In 13 the witness voted for the killer,
    and 6 killers were ejected (census cells `crew_witnessed_kills_held_at_next_meeting` and
    `held_kill_*`).
  - The holder cited its own-kill row in 21 of 23 cases (`audits/audit-2026-10-01-stage-b-r2.md:1347-1351`).
- **Without vent proof the table decides more often** (42 of 93 meetings eject; s9: 20 of 75), and decides at
  about 1.6 times chance:
  - 20 of 42 ejections removed an impostor: 0.476 (0.33-0.62);
  - the mean impostor share of the living at those meetings was 0.293 (`q7.py`; s9 11/20 against 0.253).
- **Every innocent ejection is in the first-hand, contradiction or accusation band.** 19 of the 22 are first-hand,
  and 17 of the 22 are reporters (`openers_among_innocent_ejections` 17/22).

**Verdict.** Fine as a process. The certain channels are certain, and the kill witness now does real work. The
first-hand band is where wrong ejections live (31 ejections, 12 of them impostors); section 6 explains why.

---

## 3. Vents (Q3)

Census cells (`publish_gameplay_census.py --set-dir`) plus `q3.py` and `q3b.py`.

| | s9 | r1 | r2 |
|---|---|---|---|
| vent entries; vent exits | 105; 85 | 142; 72 | 140; 72 |
| impostors who ever vented | 85/100 | 81/100 | 76/100 |
| entries a crewmate saw | 19/105 | 18/142 | 16/140 |
| exits seen from the exit room | 53/85 | 8/72 | **8/72 = 0.111 (0.06-0.20)** |
| exits into an occupied room | 53/85 | 0/72 | 0/72 |
| ticks inside per surfaced trip | all 1 | 1:51, 2:6, 3:2, 4:13 | 1:49, 2:3, 3:15, 4:5 |
| forced exits at the 4-tick cap | n/a | 13/72 | 5/72 |
| in-place surfacings a crewmate reaches | 0/0 | 2/37 | 2/44 |
| trips closed by a regroup | n/a | 46/142 | 47/140 |
| meetings opening with an impostor in a vent | 29/145 | 66/124 | **66/117 = 0.564 (0.47-0.65)** |
| impostors seen venting, then ejected | 70/77 | 24/26 | 24/24 |
| impostors who vented unseen, then ejected | 3/8 | 11/55 | 12/52 |
| impostors who never vented, then ejected | 8/15 | 4/19 | 8/24 |
| kills soon after the killer surfaced | 3/175 | 0/227 | 0/195 |

**How the vents now play.**

- **Every seen vent is a walk-in.** No exit surfaces into an occupied room (0/72), so all 8 seen exits and all 16
  seen entries were crewmates arriving on the same tick. That is the genre's risk: you vent when nobody is looking,
  and you are caught if somebody walks in.
- **The wait is real.** Trips last 1 to 4 ticks, and only 5 of 72 were forced out at the cap.
- **An impostor often sits out the meeting call inside a vent.** It hides after its kill, the body is reported
  while it waits, and the regroup brings it to the table: 47 trips ended this way, and 66 of 117 meetings open with
  an impostor inside a vent. Among Us does the same.
  - An impostor still in a vent is hidden from sight, so nobody can place it at the kill.
  - It is the main reason vent proof fell to 24/117 meetings.

**Verdict.** Fine; this is the design as built. The look-and-wait reading is **effective** for the second time
(`:1309-1319`).

---

## 4. Bodies, the regroup, and what the viewer would show (Q4)

| | s9 | r1 | r2 |
|---|---|---|---|
| stale report meetings | 43/135 | 0/118 | **0/114** |
| oldest corpse at report (ticks) | 29 | 14 | 11 (95 of 114 at 4 ticks or less) |
| meetings opening with another unreported corpse | 74/145 | 57/124 | 48/117 |
| play resumes with a corpse | 60/107 | 0/110 | 0/102 |
| play resumes with an impostor in a vent | 10/107 | 0/110 | 0/102 |
| kills in the grace window | n/a | 0/139 | 0/109 |
| report meetings that skip | 55/135 | 70/118 | 51/114 |
| sabotage active at a regroup | n/a | 3/110 | 5/102 |
| trigger-tick events a regroup drops | n/a | Moved 51, TaskProgressed 26, TaskCompleted 6 | Moved 46, TaskProgressed 22, TaskCompleted 10 |

**The engine side is genre-correct.** Every meeting is about a fresh body, the floor is cleared, vents are emptied,
and every cooldown restarts (census definitions, `docs/gameplay-census.md:17-18`).

- In 48 meetings a second victim (usually the other impostor's kill in the same wave) is never found as a body.
  That victim is announced at the meeting and the corpse is cleared at the regroup. Among Us also clears bodies at
  meetings.

**What the viewer would show: a defect for the promotion, not for the recording.**

- After every meeting all survivors appear in the hub and every corpse vanishes. Nothing on screen says why.
- `api/replay_loader.py` uses the regroup only internally:
  - `:1806` derives the regroup ticks;
  - `:1945` passes the regroup room into the memory fold;
  - `:1956` composes the resume events.
- No view field carries it, and `frontend/src` contains no regroup handling at all (a code search finds none).
- The public-results page names every Stage-B arm except the kill cooldown (`frontend/src/components/PublicResults.tsx:8-21`).
  It also still calls the adopted policies "experimental" (`:19-20`).
- The round-2 audit already lists the cooldown label as a follow-up (`audits/audit-2026-10-01-stage-b-r2.md:375-380`).

---

## 5. The opener's reply, and the reporter trap (Q5, part 1)

| | s9 | r1 | r2 |
|---|---|---|---|
| the first reply accuses the opener | 120/145 | 97/124 | 80/117 |
| an accused opener answers | 0/125 | 101/112 | 87/105 |
| **an accused opener is ejected** | 7/125 = 0.056 | 13/112 = 0.116 | **17/105 = 0.162 (0.10-0.24)** |
| after replying with an alibi: ejected / skip / someone else ejected | n/a | 11 / 61 / 29 | 15 / 44 / 28 |
| impostor first replies with an accusation and no account | 101/102 | 88/89 | **89/91** |
| rebuttals that only redirect | n/a | 17/121 | 27/117, and 27 of the 28 impostor rebuttals |

Sources: census cells, `q5a.py` and `q5e.py`.

**Is the reply believed?** Mostly yes. Of the 87 accused openers who replied, 72 survived. But the reply does not
protect the ones who are ejected: 15 of the 17 ejected reporters had replied with an alibi.

**The reporter trap, counted.**

- **The setup.** These are report meetings with no vent proof, where the reporter's opening accused a player AND
  carried a placement of that player that the engine confirms (exact, or within 1 tick). Source: `q5c.py`.
- **The outcome.** In r2, 55 openings named an impostor this way:
  - the impostor was ejected 19 times;
  - the table skipped 23 times;
  - **the reporter was ejected 12 times** (s9: 3 of 31; r1: 5 of 41);
  - another crewmate was ejected once.
- **The seeds.** 8, 9, 26, 28, 29, 30, 33, 35, 39, 43, 45, 48. 10 of these games are impostor wins, which is
  **10 of 24 impostor wins**.
- **Who drives it.**
  - Impostor ballots were pivotal in only 5 of the 22 innocent ejections. For the other 17, a crew-only tally ejects
    the same player (`q7.py`).
  - In 15 of 22 a majority of crew ballots voted to eject.
  - Of the 49 crew ballots that ejected an innocent reporter, 20 cite a crewmate's turn, 14 an impostor's turn,
    10 the voter's own turn and 5 the reporter's own turn (`q5d.py`).
- **The game already tells the voter not to do this.** The ballot tells voters that finding the body first proves nothing
  by itself (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:328-331`). It also says a door-apart pair fits a
  walk (`:270`).
- **The game guarantees reporters are innocent, and the voters do not know it.** Impostors never report: 0 of 117
  openers, by construction under R6 (`tasks/decision-2026-09-24-stage-b-wave.md:52`). So every reporter ejection
  is wrong, and in this game reporter suspicion is never right. In Among Us it sometimes is, because impostors
  self-report.

**Verdict.** No code defect. This is a reasoning limit of the model meeting a structure:

- the impostor's evidence-free counter-accusation;
- the reporter is always at the body;
- vent proof is now rare.

Under D1 the ballots are grounded and wrong, which the scorecard reports and never penalises (`:1273`).

---

## 6. Meeting quality: a single-rater rubric over 20 round-2 meetings (Q5, part 2)

**The sample.** A deterministic stride, `int(k * 117 / 20)` for k = 0..19, over the 117 r2 meetings ordered by
(seed, meeting index). Source: `q5b.py`.

**How I rated.**

- From the structured record: turns, reply links, accusations, observations and alibi legs.
- Each placement claim was checked against the engine's positions at that tick (T = true, ~ = off by one tick,
  F = false).
- From the ballots.
- No prompt was read, and turn text was read only as windows of at most 18 words.

**Scale.** 0 to 3 on three axes: coherence, groundedness (claims true and about the accused), and whether the
decision follows the talk.

| meeting | outcome | coherence | grounded | follows talk |
|---|---|---|---|---|
| seed 0 m0 | skip | 2 | 3 | 2 |
| seed 1 m1 | impostor ejected (kill-scene sighting) | 3 | 3 | 3 |
| seed 3 m3 | skip, 3 alive | 2 | 2 | 3 |
| seed 6 m1 | skip | 2 | 2 | 2 |
| seed 9 m0 | **reporter ejected after naming the killer** | 2 | 1 | 3 |
| seed 11 m1 | impostor ejected (vent) | 3 | 3 | 3 |
| seed 15 m1 | skip | 2 | 2 | 2 |
| seed 17 m0 | impostor ejected (seen at the body) | 3 | 3 | 3 |
| seed 19 m0 | impostor ejected (vent) | 3 | 3 | 3 |
| seed 21 m1 | reporter ejected | 2 | 1 | 3 |
| seed 24 m0 | impostor ejected (seen leaving the body room) | 3 | 3 | 3 |
| seed 26 m1 | skip | 2 | 2 | 2 |
| seed 29 m0 | **reporter ejected after naming the killer** | 2 | 1 | 3 |
| seed 32 m2 | skip | 2 | 2 | 3 |
| seed 35 m0 | **reporter ejected after naming the killer** | 1 | 1 | 3 |
| seed 37 m2 | impostor ejected (two at the body) | 3 | 3 | 3 |
| seed 39 m1 | impostor ejected (vent, button) | 3 | 3 | 3 |
| seed 41 m2 | skip, 3 alive | 2 | 2 | 3 |
| seed 45 m1 | reporter ejected (the impostor took the reply) | 2 | 1 | 3 |
| seed 47 m3 | impostor ejected | 3 | 2 | 3 |

**Means.**

- **Decided by a held sighting** (vent 3, scene or kill 5; 8 meetings): coherence 3.00, grounded 2.88,
  follows 3.00.
- **Contested** (12 meetings): coherence 1.92, grounded 1.58, follows 2.67.
- **Baseline 9's 54-meeting rubric** (analysis memo Q6): vent-decided 2.92 / 3.00 / 3.00; not vent-decided
  1.86 / 1.59 / 2.28.

So the decided meetings stay excellent, and the contested ones are no better or worse in coherence or grounding.
"Follows the talk" rose because the talk now converges on the reporter, and the table follows it. Here a high
score is not good news.

**Patterns in the sample.**

- **Crew speech is true.** Across all 20 meetings, crew placements and alibi legs read T almost everywhere. The
  honesty command agrees: false crew whereabouts 4/632.
- **The accused impostor's first reply always has the same shape.** It carries no observation and no alibi, only a
  counter-accusation (89/91 over the round). This is a legible tell for a spectator that crew voters do not use.
- **The one-reply selector can hand the slot to the impostor.** In seed 9 m0 and seed 45 m1 the impostor took it and
  re-accused the reporter, who never spoke again. Round-wide that is 28 rebuttals to "another impostor, answering a
  crewmate", and 2 of the 17 ejected reporters got no reply.

**Five excerpts, paraphrased here; each original was checked word for word against the bytes**
(`verify_quotes.py` prints True for all five):

1. r2 seed 11, meeting 1, turn 0, crewmate p-1, a vent witness: it reports seeing p-7 vent and asks p-7 to account
   for vanishing into the vent. p-7, an impostor, was ejected.
2. r2 seed 29, meeting 0, turn 1, impostor p-8, replying to the reporter who had placed it at the body: it claims
   a tick-11 sighting of p-5 in Admin and argues from it that p-5's claim cannot hold.
   - The engine has p-8 killing in Cafeteria at play tick 12.
   - p-5's route was Admin, then East Hall at 12, then Cafeteria at 13: adjacent moves, and every leg reads true.
3. Same meeting, turn 7, the reporter p-5's reply: it gives its route as Admin, East Hall (tick 12), Cafeteria
   (tick 13). It is true. p-5 was ejected 6 to 1, and both impostors voted for it.
4. r2 seed 35, meeting 0, turn 5, crewmate p-4: it doubts that p-2, placed in Labs, could have seen anything happen
   in MedBay.
   - Labs and MedBay are a walk apart.
   - p-4 itself had placed the impostor p-5 beside the victim (MedBay, tick 10).
   - The reporter p-2, who had named p-5 at the body, was ejected 5 to 1.
5. r2 seed 9, meeting 0, turn 0, the reporter p-6: it places p-4 in Engineering on that same tick. It is true: the
   engine has p-4 killing in Engineering at play tick 6. p-6 was ejected 6 to 2.

**Verdict.**

- **Fine** where evidence exists: coherent, true and decisive.
- **Choices to keep:** the evidence-free counter-accusation and the impostor's own-turn citations.
  - 19 of 111 impostor EJECTs cite the impostor's own accusing turn. That is inside R10's wording, which counts
    any accusation made against the target at this table (`vote_ballot.j2:322`).
  - The honesty reading still holds: 0/111 cite only a neutral row (`:1352`).
- **The reporter trap** is the one pattern a spectator should not see unexplained.

---

## 7. The task win (Q6)

Source: `q6.py`.

| | s9 | r1 | r2 |
|---|---|---|---|
| task instances per game | 14 (2 games: 13) | 14 (3 games: 13) | 14 |
| half the tasks done, median tick | 14 | 15 | 13.5 |
| games where every task was done | 1 | 4 | **13** |
| task share at the end of impostor wins: mean; games at 0.8 or more | 0.59; 3 of 11 | 0.71; 7 of 34 | **0.81; 12 of 24** |
| task wins with a sabotage started | 1 of 1 | 4 of 4 | 13 of 13 |
| task wins: living impostors at the end | 1 | 1:3, 2:1 | 1:10, 2:3 |

**The lever is the cooldown, not the task count.**

- The task count is the same in all three columns: 2 per crewmate, 14 instances.
- The task pace is unchanged: half the tasks are done by about tick 14 everywhere.
- r1 and r2 differ in one key. From r1 to r2:
  - kills per game fell from 4.54 to 3.90, and the first kill moved from tick 4.5 to tick 7;
  - games grew from 32.8 to 38.8 ticks;
  - the same task pace therefore finished the list in 13 games instead of 4.
- That is the mechanism, read within hosted noise.
- Task count is still a lever the owner holds (the roster's `tasks_per_crewmate`), but it is not what moved.
- The race is close: 12 of the 24 impostor wins ended with 80% or more of the tasks done.

**Is a task win a good game to watch?** Usually.

- 10 of the 13 also eject an impostor, and every one shows the impostors' sabotage stall. In Among Us, crew winning
  on tasks while one impostor is still loose is a normal ending.
- 3 task wins eject no impostor:
  - seeds 15 and 31 establish nothing at all;
  - seed 29 ejects an innocent reporter.
- Those three are poor tour material.

**Verdict.** Fine, and a choice to keep. 13/50 = 0.26 (0.16-0.40).

---

## 8. Balance (Q7)

- **The win share is inside the envelope.**
  - Impostor win share 24/50 = 0.48 (0.35-0.61), inside 0.20-0.60 (`:1377`).
  - Round 1's interval (0.54-0.79) overlaps this one.
  - The upper bound, 0.61, does not exclude a share just above the envelope.
- **The round-3 rule** reads the point share. Neither cooldown branch fires, and the reporter flag blocks the
  promotion branch (`:346-360`, `:1386-1389`).
- **What remains in the envelope:**
  - reporters ejected per report meeting, 17/114 = 0.149 (0.10-0.23), flagged above 0.104;
  - innocent ejections, 22 of 66;
  - role-correct ejections, 44/66 = 0.667;
  - meetings with vent proof, 24/117.
  - Impostors able to kill when a meeting opened: 54/200 (`:1392-1401`).
- **The two findings are linked.** 10 of the 24 impostor wins followed the reporter trap (section 5).
  - A fix there would move the share down, by an amount not measurable from these bytes.
  - With 14 impostor wins outside the trap, the share would still sit above the 0.20 floor even if every trapped
    game flipped.
- **The cooldown dial should not move again.** The rule names no cooldown step, and the share is mid-envelope.

---

## 9. Showability (Q8)

**The criterion.** This is the spectator card's measured criterion
(`tasks/work/spectator-tour-and-alternatives.md:35-60`; `scripts/measure_featured_criterion.py`; pinned per set by
`tests/api/test_sets.py:511`). The head's FIRST meeting must eject an impostor who carries a `role_proof` (vent)
flag in that meeting.

| | s9 | r1 | r2 |
|---|---|---|---|
| role_proof / other flag / no flag ejections (role-correct) | 70 (70) / 2 (1) / 18 (10) | 24 (24) / 2 (0) / 28 (15) | 24 (24) / 2 (0) / 40 (20) |
| games whose first meeting ejects on role_proof | 32 of 50 | 9 of 50 | **11 of 50: seeds 3, 5, 6, 7, 10, 11, 19, 20, 27, 42, 49** |
| games with no flag and no ejection anywhere | 2, 4, 10, 46 | 12 games | 4, 15, 31, 36 |

**Games for a featured tour** (meeting sequences from `q8b.py`):

- **Seed 7**, head choice. Two meetings, 15 turns.
  - Tick 10: a vent sighting ejects an impostor.
  - Tick 28: a crewmate who saw the second impostor kill names it, and it is ejected.
  - Crew win at tick 28.
  - It shows both certain channels in a short game.
- **Seed 19**, alternative head. Three meetings, 19 turns: a vent ejection at tick 12, a contested skip at tick 31,
  and a kill-witness ejection at tick 44. Crew win.
- **Strip, and why each is worth watching:**
  - seed 1: no vent proof. A first-hand ejection, then a kill-witness ejection, a deduction game. It fails as a head
    because its first meeting skips.
  - seed 6: a vent opener, then a skip, then a task win under sabotage.
  - seed 0: four meetings, 26 turns. Two skips, then a vent ejection, then a kill-witness ejection.
  - seed 3: a vent opener, then three skips, and the impostors win at tick 62: the table that stalls.
- **Games that show the game at its worst:**
  - 4 and 36: two skips, then parity, with nothing established.
  - 15 and 31: task wins with nothing established.
  - 48: two innocent reporters ejected back to back, parity at tick 25.
  - 2 and 12: one meeting that ejects an innocent, parity at tick 22.
  - The twelve reporter-trap seeds in section 5. Seeds 29 and 35 are the clearest. They could only be shown as an
    honestly labelled "drama of a reasoning mistake", the analysis memo's Q6 framing.

**The current strip on round-2 bytes.** The 9-player list is `frontend/src/components/ReplayPicker.tsx:109-133`.

- Head, seed 23: an impostor win with one innocent reporter ejected and one skip. It fails the criterion.
- Seed 0: fine to keep, but not as head.
- Seed 29: a reporter-trap game.
- Seed 2: parity at tick 22 after one wrong ejection.
- The labels ("Four meetings, twenty-six spoken turns", and so on) no longer match.

So a promotion must re-curate the strip, as the comment at `:96-107` intends. The owner deferred the tour until
gameplay is finished (ruling 11, `tasks/decision-2026-09-24-stage-b-wave.md:40`).

---

## 10. The ledger

| behaviour on round 2 | class | evidence | mechanism; recorded arm? |
|---|---|---|---|
| Engine arms as built: physical witness, look-and-wait, fresh-kill entry, full reset, cooldown 6 | **fine** | every Conf. cell 0 (`audits/audit-2026-10-01-stage-b-r2.md:1278-1300`) | recorded arms, adopted (7) and dialled (cooldown) |
| Game shape: 39 ticks, 2.3 meetings, three endings, 13 task wins | **fine** | section 1 | cooldown and grace window |
| Vents risky only on a walk-in; vent proof certain | **fine** | 0/72 exits into occupied rooms; 24/24 | look-and-wait plus physical witness |
| Kill witness as a second certain channel | **fine** | 8 of 8 kill-sighting ejections are impostors; 21/23 rows cited | `ballot_kill_row_version = 1` |
| Grounded, faithful, truthful speech | **fine** | 407/410; 580/580; 628/632 | substrate, unchanged |
| Balance | **fine** | 0.48 (0.35-0.61) | cooldown 6; no further step named |
| Regroup invisible in the viewer; cooldown unlabelled; "experimental" wording for adopted arms | **defect (presentation)** | section 4 | promotion follow-up, not recorded |
| Featured 9-player strip wrong on round-2 bytes | **defect at promotion** | section 9 | re-curation card |
| Impostors never self-report, so every reporter is innocent | **choice to keep, or revisit (R6)** | 0/117 impostor openers | `self_report` exists (`orchestrator/experiment_config.py:50`), a recorded tactical field |
| The accused impostor's first reply is an evidence-free counter | **choice to keep** | 89/91 | the model's play |
| Impostor EJECT cites its own accusing turn | **choice to keep** (within R10) | 19/111 | `vote_ballot.j2:322` |
| The one reply can go to an impostor | **choice to keep** (B3 rider, v1 not opener-only) | 28 of 117; 2 of 17 ejected reporters had no reply | `meetings/rebuttal.py:17-55` |
| Synchronised post-regroup kill wave | **choice to keep** (genre) | 70/109 at T+7 to T+10 | full reset plus cooldown |
| The button nearly gone | **choice to keep** | 3 of 117 | follows from rare vent sightings |
| **Reporter trap**: an innocent reporter ejected, often after naming the real killer | **model limit meeting a structure**; the envelope's only flag | 17/114; 12 after a true sighting; 10 of 24 impostor wins | see below |

**What one more round could fix** (only the reporter trap; no engine change is indicated):

- **A. The existing walking check: `evidence_reasoning_version = 2`.**
  - It already exists as a recorded meeting-layer field (`orchestrator/experiment_config.py:52`). It renders
    conditional walking counterevidence (`agents/memory/evidence_context.py:248-258`). That is the mechanism aimed
    at the impossible-route error behind excerpts 2 and 4 (analysis memo Q6).
  - Cost: it needs experiment `format_version = 2` (`orchestrator/experiment_config.py:103-111`) and new prompt
    bytes behind the gate.
  - Version 1 is refused beside the regroup (`:138-144`). Version 2 is allowed, but untested under the regroup.
    It needs a lab and fake rehearsal first.
- **B. An opener-first selector, `bounded_rebuttal_version = 2`.**
  - New code under a new value, the option in decision memo section 5 item 4.
  - Its upside is bounded: 2 of the 17 ejected reporters had no reply.
- **C. `impostor_ballot_version = 2`**, which would not let an impostor cite its own turn as the line pointing
  toward a crewmate.
  - A new value with new prompt bytes.
  - Its upside is bounded by the 5 innocent ejections where impostor ballots were pivotal.
- **D. Revisit R6 with `self_report = True`.** It is an existing recorded tactical field.
  - It makes reporter suspicion sometimes correct, as in the genre.
  - It also changes what the reporter flag means, and gives impostors a cover action, which carries balance risk.
- **No cooldown round.** The rule names none.

---

## 11. Reproduction (count-only; repo root at `d41c9006`, bare shell)

**Committed instruments**, which write nothing:

```
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r2/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout
uv run python scripts/publish_process_scorecard.py --set-dir replays/candidates/stage-b-r2/9p2i --json-stdout
uv run python scripts/publish_process_scorecard.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
uv run python scripts/measure_baseline.py replays/candidates/stage-b-r2/9p2i --funnel
uv run python scripts/measure_baseline.py replays/candidates/stage-b-r2/9p2i --honesty --json
uv run python scripts/measure_featured_criterion.py --parent replays/candidates/stage-b-r2 --set 9p2i
uv run python scripts/measure_featured_criterion.py --parent replays/candidates/stage-b-r1 --set 9p2i
uv run python scripts/measure_featured_criterion.py --set 9p2i
```

**What they gave.**

- Every census and scorecard run exited 0. The census cells and the row-5 bands equal the round-2 audit's columns.
- The funnel printed `reporter ejected 17/63 (17 innocent)` and `killer self-reported 0`.
- The honesty run printed `crew_false 4/632`.
- The criterion printed 11, 9 and 32 eligible openers, with the seed lists above.

**Session scripts** (count-only, kept in the session scratch directory
`diagnosis-2026-10-02/gameplay_state-scripts/`, not committed). Run each from the repo root as
`uv run python <dir>/<script>`:

| script | what it does |
|---|---|
| `load.py s9 r1 r2` | pickles `eval.gameplay_census.load_census_inputs` for each set (the census walk verifies state hashes) |
| `walk2.py s9 r1 r2` | per-tick tasks, kills, sabotage and the game-over row, through `eval.replay_walk.walk_replay` under `CENSUS_WALK_CONFIG` |
| `bands.py s9 r1 r2` | wraps the scorecard's own `_ejection_band`, unchanged, to key row 5 by (set, meeting) |
| `q1.py` | section 1 |
| `q2.py`, `q2b.py` | section 2 |
| `q3.py`, `q3b.py` | section 3 |
| `q5a.py`, `q5c.py`, `q5c2.py`, `q5d.py`, `q5e.py`, `q7.py` | sections 5 and 8 |
| `q5b.py` | the rubric's structured view; prints claims and engine truth, no turn text |
| `q6.py` | section 7 |
| `q8.py`, `q8b.py` | section 9 |
| `excerpt.py` | printed the 18-word windows |
| `verify_quotes.py` | prints only True or False per excerpt, plus the cited kill facts |

---

## 12. For the parallel ML question

[`ml-tactical.md`](ml-tactical.md) owns that topic; this is only the gameplay half of it.

- **What changed for decisions made without the model:**
  - when impostors kill is now pinned by the grace window (70 of 109 post-meeting kills at T+7 to T+10);
  - vent exits are rule-bound and almost never seen (8/72);
  - crew catch kills by walking in (14/195).
- **Where a learned policy could matter:**
  - crew movement after the regroup (who walks with whom, and where, when the wave lands);
  - impostor target choice in that wave.
- The flaw that remains is in the meeting layer, not the tactical one.
- The owner's ruling 12 still holds: ML waits until gameplay is finished. The tactical substrate looks settled
  enough to be that stable base once the owner takes or declines the promotion.

## 13. What this memo could not establish

- **How common the route error is.** It was not counted round-wide. Full turn text may not be printed, and no text
  classifier was run. The five excerpts and the 20-meeting sample show it; they do not count it.
- **Whether the r1-to-r2 changes are the cooldown's alone.** One key separates the rounds, but each is a single
  hosted recording. The win-share intervals overlap.
- **What the viewer renders on the regroup.** It was inferred from a code search (no regroup handling in
  `frontend/src`; the API keeps it internal), not observed in a running viewer.
- **Whether `evidence_reasoning_version = 2` would reduce reporter ejections under the regroup.** No lab run was
  made.
- **Two pre-registered cells stay uncarried.** Ballots citing a rebuttal, and `none_held` SKIPs on round 2.
- **The rubric is one rater's,** on structured claims plus short windows. It is not blind and not a multi-rater
  study.
