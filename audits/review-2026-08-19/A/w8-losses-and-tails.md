# w8-losses-and-tails — spectator review of impostor wins and long crew-task wins (9p2i)

Scope: `replays/samples/9p2i` (Qwen3.6-27B, prompt set v3, fsm-default). Games watched end-to-end with
`watch.py` (verbose per-tick visibility on all seven; `--memory` renders for the impostors in every impostor
win plus the decisive crew voters), plus a few purpose-built scripts on top of `ReplayLoader`
(`scratchpad/work/w8-losses-and-tails/stats.py`, `setwide.py`, `setwide2.py`, `imp_debug.py` — the last one
re-runs the recorded impostor FSM on reconstructed memory to explain a decision; it reproduces the recorded
actions byte-for-byte). Source code was only opened to explain something observed; file:line cited where used.

Games:
- IMPOSTORS wins: seed 12 (20 ticks, shortest), seed 21 (68 ticks, longest), seed 8 (60 ticks), seed 39 (35 ticks).
- CREWMATE_TASKS wins (the only 4 in the set are 7, 36, 37, 42): seed 36 (52 ticks), seed 42 (46 ticks), seed 7 (50 ticks).

Tick convention used below (verified against raw JSONL): the world line `[t N]` is the state AFTER tick N's actions;
an agent perceives that state at the start of tick N+1, and its memory stamps the observation `[tick N+1]`. So a
kill the world shows at t14 appears in memories as "[tick 15]". Meeting ticks quoted are world ticks unless the
quote is from a memory/prompt.

Labels: [VERIFIED] = seen in the bytes; [JUDGMENT] = my inference. Category tags: GLITCH (looks broken),
DESIGN (design choice that hurts believability), REASONING (quality of the LLM's reasoning).

---

## Set-wide numbers (all 50 9p2i games; `setwide.py`, `setwide2.py`) [VERIFIED]

- Meetings: 165 = 151 body-triggered + 14 emergency. Ejections: 78 impostors, 23 crew. **19 of the 23 wrong
  ejections carry a STRONG `alibi_vs_sighting` flag against the ejectee.**
- First kill at world t4 or t5 in 43/50 games; 18/50 first kills happen in CAFETERIA (spawn/hub); exactly one
  impostor per game (50/100) sits IDLE in CAFETERIA for t0–t3 waiting for the CAFETERIA-task crewmate.
- Crew alive-ticks: 7959; 17.5% of them IDLE, and 17.0% IDLE with all own tasks done (return-to-hub loitering).
- 65/165 meetings: the reporter is formally accused by ≥2 players; only 3 reporters ejected (reporter_exculpation works).
- 64/165 meetings end without an ejection. 53/971 turns carry `[invalid accusation target …]` husks in free_text.
- 97 crew vent-witness events; 92 got spoken as `saw_vent` at a later meeting; 5 witnesses died first; 10 vents fell on a meeting tick.

---

## Game 1 — seed 12 (IMPOSTORS, parity at t19; the fast loss)

Roster: p-1*, p-7* impostors. 2 meetings.

**Narrative.** t0–3: p-7* never leaves CAFETERIA (`p-7*@CAFETERIA:IDLE` t0–t3) while p-8 does the cafeteria task next
to him; t4 `EVENT kill: p-7 -> p-8 in CAFETERIA` (hub kill, no witnesses). t5 p-1* kills p-6 in STORAGE, t6 vents,
t7 exits the vent in ENGINEERING **in front of p-4** (`p-4 sees players=['p-1@ENGINEERING:vent'] … hears=[vent_use_heard]`)
— on the very tick p-2 reports p-8's body in CAFETERIA. Meeting-0 (t7): p-2 opens by accusing p-3 ("p-3 left Medbay
at tick 3, nowhere near here"); p-3 answers correctly ("I was in the Labs at tick 3, not Medbay"); the machinery mints
`[alibi_vs_sighting/strong] Alibi places p-3 in LABS (ticks 3-3); sighting reports p-3 in MEDBAY at tick 3` from p-9's
spoken sighting, and **p-3 (innocent) is ejected 6-0**, both impostors voting along. p-4, who saw the vent, gets it in
memory only after the meeting (`[obs p-4:8:1] [tick 8] You witnessed p-1 vent in ENGINEERING`, belief `p-1: suspicion 1.00`),
cannot call an emergency for 6 ticks (cooldown), and is killed by p-1 in ADMIN at t14 — the tick his cooldown expired
and his action switched from tasking to `move EAST_HALL` (walking to the button, [JUDGMENT]). p-9 walks into ADMIN on
that same tick and sees p-1 standing at the body (`p-9 sees players=['p-1@ADMIN:None'] bodies=['body-p-4-14@ADMIN']`),
reports one tick later — by which time p-1 has left and p-7 has walked in. Meeting-1 (t15): p-9 accuses p-7 (the
wrong impostor, on movement) and never mentions p-1 at the body; all 5 ballots SKIP at 0.55 ("Max suspicion 0.55.
Below threshold."). t19 p-7 kills p-9 in ADMIN → parity. p-6's body lies unreported in STORAGE from t5 to the end.

**(a) Information.**
- [VERIFIED] The decisive fact of the game — p-9 saw p-1 next to p-4's fresh body — is rendered as two unlinked lines
  ranked low: `[obs p-9:15:3] You discovered p-4's body in ADMIN` and, ten lines further down, `[obs p-9:15:1] You saw
  p-1 in ADMIN (moved from CAFETERIA, last seen there at tick 0)`. p-9's belief row for p-1 stayed at 0.50 (rendered as
  `p-1: alibi: in STORAGE at tick 6 per p-1`, no suspicion), and every voter's table showed `p-1: suspicion 0.50 … this
  meeting +0.00`. A human would say "p-1 was standing over the body". REASONING+DESIGN.
- [VERIFIED] The wrongful flag came from a movement line. p-9's memory: `[obs p-9:3:2] [tick 3] You saw p-3 move from
  MEDBAY to LABS`; p-9 encoded it as `saw_player tick 3 subject p-3 room MEDBAY`; p-3's truthful roll-call was `LABS at
  tick 3`. Same fact, opposite rooms, STRONG flag, "VERIFIED evidence" in every ballot prompt. GLITCH (encoding ambiguity
  of "move from A to B at tick T").
- [VERIFIED] The vent witness p-4 lost the sighting to timing: vent exit and meeting on the same world tick (t7), so
  meeting-0's memory for p-4 has no vent line; it appears only in his post-meeting memory. His beliefs then say
  `p-1: suspicion 1.00` but the emergency-button producer needs `cooldown_remaining == 0` (6 ticks after a meeting;
  `agents/tactical/crewmate_policy.py:110-125,140-165`). He died the tick it hit zero. DESIGN (cooldown vs. hard evidence).
- [VERIFIED] Testimony enters memory only as structured claim lines: `[tick 8] [meeting] CLAIM by p-7 (unverified): p-7
  was in CAFETERIA during ticks 5-7` — no free text, no outcome (nobody's memory says "p-3 was ejected at tick 7"; p-9's
  meeting-1 beliefs still list `p-3: last seen in LABS at tick 3`).
- [VERIFIED] Impostor memory (p-7 at meeting-1) is 80+ lines, mostly adjacent-room movement dumps ("You saw p-2 move from
  WEST_HALL to MEDBAY" seen from CAFETERIA) because impostors keep `same_room_and_adjacent` vision while crew are
  downgraded to `same_room_only` (`engine/visibility.py:98-125`). It contains `You (IMPOSTOR) killed p-8 in CAFETERIA` but
  nothing about the partner's kills or the partner's identity beyond the players block ("Your fellow saboteurs: p-1").
- [VERIFIED] The persona says "a hidden impostor is killing crewmates one at a time … the impostor wins by surviving until
  they equal the crew" — singular, in a 2-impostor game (every prompt in this game).

**(b) Decisions.**
- Opening (p-2): grounded but wrong-target; p-2's own structured obs said `saw_player tick 3 p-3 LABS` while the speech
  said "left Medbay" — speech/claim drift within one turn. p-9 the same: says "I was busy in Medbay with p-2 until tick 6,
  so I know they weren't near the Cafeteria" and files `accusation against p-2 (0.75)`. [VERIFIED]
- Ballots: 6/6 living non-p-3 voters cite turn-1 and "the flag"; p-4: "It might be that p-3's claim of being in Labs
  conflicts with the Medbay sighting". Pure flag-herding; the impostors ride it (p-1: "p-3's alibi crumbled against the
  verified sighting"). Wrong ejection.
- Impostor deception: p-7*'s structured alibi carries a self-tell in the record — `alibi … evidence: ('killed p-8 at
  tick 5',)` (spectator-visible only; not in other players' prompts, checked). p-7's ballot rationale at meeting-1: "Why
  trust p-5's weak claim over my own kill?" (rationale is not player-visible). p-1's opt-in at meeting-1: "I was in ADMIN
  when the body was found" (he was in EAST_HALL at t15; his roll-call `whereabouts tick 15 ADMIN`) — a lie that puts him
  at the scene, unchallenged. No partner-busing; both impostors pile onto whoever the crew is piling onto.
- Meeting-1 outcome: 5 SKIPs at exactly the "max 0.55 < 0.60" arithmetic printed in the ballot prompt ("when the max sits
  below the threshold, SKIP is the sound call"). p-5, who saw p-7 next door at t13, and p-9, who saw p-1 at the body,
  both skip. DESIGN: the scalar anchors the vote.
- Wording: p-7's reply "Where were you at tick 4? Tick 5? You were nowhere near Engineering" addressed to p-2 who never
  claimed Engineering.

**(c) World sim.**
- [VERIFIED] Bodies: reported body cleared at the meeting; unreported body persists (body-p-6-5 in STORAGE t5→t19, across
  two meetings, never found — nobody enters STORAGE again).
- [VERIFIED] Positions are NOT reset after a meeting (t8: everyone resumes where they stood at t7). p-9 and p-7* resume
  together in ADMIN after meeting-1; p-7 comes back and kills p-9 there at t19.
- [VERIFIED] Spawn camping (p-7 IDLE t0–3), hub kill at t4; kill-in-front-of-witness at t14 (p-9 co-present post-tick,
  p-7* also "saw p-1@ADMIN:kill" from WEST_HALL); vent exit in front of p-4 at t7 while a meeting was being called.
- [VERIFIED] Rejected kill: t17 p-7 (WEST_HALL) → p-2 (CAFETERIA): the queued kill on a co-located lower-id target who
  moved first (the id-order rule) — the crewmate "dodges" the knife by walking.
- [VERIFIED] p-1 ping-pongs ADMIN↔EAST_HALL/WEST_HALL t9–t13 waiting for cooldown; p-5 idles in CAFETERIA t13–t19 with
  all tasks done. Quiet ticks (no events): 11/21.
- One-tick reporting latency everywhere (see body at t, report at t+1) — the killer always gets a free tick.

**(d) Watchability.** Short and brutal; the rewinds are t7 (vent exit + meeting on the same tick), t14 (p-9 walks in on
the killer) and the meeting-1 skip. Boring: nothing. Frustrating: the omniscient viewer knows p-4 has the answer and
watches him get killed on his way to the button.

---

## Game 2 — seed 21 (IMPOSTORS, parity at t67; the longest game)

Roster: p-2*, p-5* impostors. 5 meetings, one ejection (p-2*, correct, at t10). p-5* then wins alone over 57 ticks with
four consecutive SKIP meetings.

**Narrative.** Same opener as seed 12: p-5* idles in CAFETERIA t0–3, kills p-7 there at t4; p-2* kills p-3 in STORAGE t5,
vents STORAGE→ENGINEERING at t7 in front of p-1 and p-9. Meeting-0 (t10, p-1 reports p-7): two grounded vent
witnesses, `[vent_sighting/strong]` ×2, p-2 ejected 5-0-2 (p-2 and p-5 skip). Then the long tail: by t18 four of the six
crew have all their tasks done (`tp=1.00`) and sit IDLE in CAFETERIA (p-8 idle t17–t46, p-6 t22–t36, p-4 t19–t29, p-9
t30–t46); the outstanding tasks are p-1's and p-9's, in STORAGE/REACTOR. p-5 stalks p-1 to REACTOR and kills him at t29
with nobody around, vents to ADMIN. Because `dead_task_rule: redistribute` (canonical map), p-1's unfinished tasks are
re-keyed to p-4 (`tp 1.00 → 0.45` at t29); p-4 walks alone to REACTOR, is killed there at t36; p-6 inherits (1.00→0.58),
finishes REACTOR at t45, walks to ADMIN alone, killed t53; p-8 inherits (1.00→0.53), killed in ADMIN at t67 → parity.
Each kill produced a meeting; each meeting SKIPped. Two reactor sabotages (t46, t59) only made the idle crew walk to
ENGINEERING and back.

**(a) Information.**
- [VERIFIED] Time of death is invisible. p-3 was killed at t5 and announced dead at meeting-0 (`Dead or ejected — never
  accuse: p-3, p-7` in every meeting-0 prompt), his body found only at t21. Meeting-1 then debated "the kill window" as
  ticks 16–21: p-1's opening "I found p-3 in Storage … p-9 is the most suspicious living player for being near him", p-8:
  "why did you leave the Cafeteria for East Hall at tick 19 right before the body was found?". Nobody's memory says "p-3
  has been dead since before meeting-0" or "last seen p-3 heading to STORAGE at tick 3" (p-1's memory has exactly that:
  `[obs p-1:3:4] [tick 3] You saw p-3 move from ENGINEERING to STORAGE`, and p-2 — already ejected — was the one who
  followed him). DESIGN: no death-time / last-seen rendering.
- [VERIFIED] The prompt forces re-litigation of a dead impostor's vent: "A witnessed vent is the single strongest fact …
  speak it FIRST, at this meeting, even if it happened many ticks ago and even if you already said it at an earlier
  meeting". p-9 obeys at meetings 1, 2, 3 and 4 ("I saw p-2 slip into a vent … that's the only snake in this grass"),
  each time producing `[invalid accusation target 'p-2' dropped]` in his free_text (meetings 2 and 3). p-1 opens
  meeting-1 with the dead vent too. Wasted turns; husk text in speech. GLITCH (prompt rule ignores the dead list).
- [VERIFIED] Idle crew learn nothing: p-6/p-8/p-9's memories for t20–t45 are "You saw p-8 in CAFETERIA (with p-4)" over
  and over; each victim was alone. So every post-t10 meeting has zero evidence and the impostor is never at risk.
- [VERIFIED] Impostor memory (p-5 at meeting-4): kills first, then `You heard a sabotage alarm` ×3 (his own sabotage),
  then ~60 movement lines from adjacent-room vision (`[tick 33] You saw p-4 move from ENGINEERING to REACTOR` seen from
  EAST_HALL — REACTOR is not even adjacent; departure-room adjacency suffices). Beliefs list his own victims (`p-1: last
  seen in REACTOR at tick 28`, `p-4: last seen in REACTOR at tick 33`) and "suspicion 0.59" for p-9 — an impostor
  running crew suspicion arithmetic on people he knows are innocent.

**(b) Decisions.**
- Meeting-0: model behavior. Both witnesses put `saw_vent` on the record with confidence 1.0; p-2*'s reply is a flat
  denial plus a deflection on p-9 ("I was just standing there watching p-9 and p-1 do their tasks in Engineering for like
  five ticks straight"); p-5* (partner) does NOT defend him — "Stop deflecting, p-2 … you are the impostor" (structured
  corroboration of p-1) but ballots SKIP with rationale "I killed p-7 myself, so I know p-2 is my partner and innocent; I
  cannot vote my own teammate" (rationale not player-visible; the persona forbids naming the role — it does it in the
  ballot anyway).
- Meeting-1: 5 of 6 speakers accuse the reporter/vent-witness p-1 on the rhetorical point "pivoted from dead p-2 to p-9"
  (p-4, p-5*, p-6, p-8 all use the same phrase "pivoted"); p-5* adds a true-but-loaded sighting ("I saw p-1 alone in East
  Hall at tick 16" — p-5 had tried to kill p-1 there, `KILL-REJECTED t16`). All SKIP; p-1: "the mob's hysteria against me
  is just noise". Herding on rhetoric with no evidence.
- Meeting-2 (t33): p-4 (reporter) is attacked for being at the scene: p-5*: "He places himself in the Reactor at tick 33,
  the exact moment the body was found. He was right there when p-1 died. Vote him out now!" while p-5's own roll-call
  says `whereabouts tick 33 REACTOR` — the impostor placed HIMSELF in the body room at the discovery tick (he was in
  EAST_HALL; his memory has no self-location line at all) and nobody noticed. p-6/p-8: "p-4 was alone in East Hall at
  tick 31, moving toward the Reactor" — walking to a task alone is treated as guilt. All SKIP.
- Meeting-3 (t40): p-6's opening reason is incoherent: "p-9 was right there with me in Cafeteria at that exact moment,
  giving them the opportunity to strike while I was distracted". Ballots quote the machinery: p-8 "p-9's suspicion is
  0.59, below the 0.60 threshold. No hard evidence. Skip."; p-6 "the evidence is thinner than the skip threshold".
- Meeting-4 (t56, three alive): p-8 votes p-9 (0.64) on "How did you get to Admin to kill p-6 and back to Cafeteria in
  two ticks?" — a wrong vote that would have ended the game if p-9 had not skipped; p-5* skips (rationale: "I killed p-6
  myself … voting now wastes a kill opportunity").
- Hallucination: p-9 at meeting-4 lists `saw_player tick 52 subject p-9 room CAFETERIA` — a sighting of himself.

**(c) World sim.**
- [VERIFIED] The task-relay-of-death: `redistribute` sends the dead crewmate's task to a living crewmate who walks alone
  to the same remote room where the impostor is already waiting (REACTOR t29 and t36, ADMIN t53 and t67). Combined with
  return-to-hub idling, the endgame is a queue. Task counter stuck at 11/14 from t26 to t45, 12/14 t45–t58, 13/14 to the
  end. Quiet ticks 40/69.
- [VERIFIED] Rejected kills at t16 (EAST_HALL→CAFETERIA) and t26 (STORAGE→ENGINEERING): the impostor swings at a
  crewmate it can see in the adjacent room / who just left (`KILL-REJECTED … actor room STORAGE, target room ENGINEERING`).
- [VERIFIED] Sabotage is a walk simulator: t46 reactor sabotage → p-6 repairs alone in ENGINEERING (repair_progress
  ENGINEERING 1,2), p-8/p-9 walk CAFETERIA→ENGINEERING→CAFETERIA and idle again. Neither sabotage came close to timing out.
- [VERIFIED] Bodies: p-3's body persisted across meeting-0 (t5–t21). Body found only when p-1's own task took him to STORAGE.
- [VERIFIED] The reporter of meeting-2 (p-4) resumes in REACTOR alone after the meeting and is killed there 3 ticks later.

**(d) Watchability.** Meeting-0 is a good scene (two witnesses vs. a denial). From t18 on the game is 50 ticks of
three crew standing in a room while one walks off to die; a spectator would fast-forward from t18 to t67. The four
SKIP meetings are interchangeable ("The smoke is too thick to see the fire" is p-9's ballot text at meetings 1, 2 and 3
and again in seed 12). Rewind moments: t29 (p-5 kills p-1 the moment p-9 leaves REACTOR), t53.

---

## Game 3 — seed 8 (IMPOSTORS, parity at t59)

Roster: p-3*, p-5*. 5 meetings; p-3 ejected correctly at t8 on a vent; final meeting ejects innocent p-9 → parity.
Structurally a near-clone of seed 21 (same opener, same partner-lost-to-vent, same lone p-5 conveyor).

**Narrative.** t4 p-5* kills p-8 in CAFETERIA (spawn camp). t6 p-3* kills p-6 in ADMIN, t7 enters the ADMIN vent as p-1
and p-7 walk in (`p-1 sees players=['p-3@ADMIN:vent']`); p-3 is still `VENTING` at t8 when p-1 reports — an impostor
inside a vent attends the meeting. Meeting-0: p-1 speaks the vent, p-3 replies "Glitch. P-1 entered ADMIN at tick 8.
Suspicious timing.", partner p-5* openly defends him ("I'm not buying p-1's vent story") and both impostors vote p-4 (a
bus attempt on the strong flag `Alibi places p-4 in EAST_HALL (ticks 8-8); sighting reports p-4 in ENGINEERING at tick 8`
— p-4 was in ENGINEERING at t7–t9; his roll-call was wrong). p-3 ejected 5-2. p-3's ballot: `[under-gate eject target
'p-1' redirected] P-1 lies about the vent…` — the vote guard rewrote his target from p-1 to p-4. Meeting-1 (t15) and
meeting-2 (t18) SKIP unanimously while p-1 and p-7 keep re-speaking the dead vent (`[invalid accusation target 'p-3'
dropped]` ×3). t36 p-5 kills p-1 in REACTOR after the t29 sabotage scattered the crew; meeting-3 (t40) SKIP 2-2 where
**both crew votes for p-5 are guard redirects**: `p-7 -> p-5 … [under-gate eject target 'p-4' redirected]`, `p-9 -> p-5
… [under-gate eject target 'p-4' redirected]` — the crew wanted to eject the reporter p-4 and the system moved their
votes onto the real impostor, still short of a majority. t56 p-5 kills p-4 in ADMIN. Meeting-4 (t59, three alive):
p-9's roll-call "EAST_HALL 54–58" is false (he was IDLE in CAFETERIA t54–t59), p-5*'s sighting "p-9 in CAFETERIA at 55"
is true → STRONG flag → p-9 ejected 2-1 → parity.

**(a) Information.**
- [VERIFIED] p-9's memory has `[tick 55] You saw p-7 in CAFETERIA`, `[tick 58] You saw p-7 move from CAFETERIA to
  EAST_HALL`; he turned the second line into "You saw me in East Hall at tick 58, right next to YOU" and an alibi
  `EAST_HALL 54-58`. There is no "You were in CAFETERIA" line anywhere in a crew memory (only completed_task rows carry
  own room), so self-placement is guesswork from co-location lines. DESIGN (root cause of most false roll-calls).
- [VERIFIED] p-7's speech at meeting-1 "I personally witnessed p-3 vent in ADMIN at tick 8" is a hallucination — his
  memory has no vent line (only `CLAIM by p-1 (unverified): accused p-3` absorbed from meeting-0); the world's vent
  visibility at t7 lists only p-1. Absorbed testimony was re-spoken as first-hand. REASONING.
- [VERIFIED] The suspicion scalar decided the endgame: p-9's ballot prompt at meeting-4 showed `p-5: suspicion 0.59 …
  carried prior +0.15` vs threshold 0.60; his rationale "P-5's suspicion is below the threshold. I skip." Impostor p-5
  hovered at 0.59 for the last 20 ticks (`p-8` in seed 21 says the same "0.59, below the 0.60 threshold").
- [VERIFIED] Impostor memory (p-5 at meeting-4): the t4 kill of p-8 has dropped out of the rendered memory (only kills at
  18/37/57 shown), `You heard a sabotage alarm` ×6 (his own), beliefs with numbers for people he killed
  (`p-1: suspicion 0.46 (last seen in REACTOR at tick 35)`).

**(b) Decisions.**
- Meeting-0 impostor play: open partner defense + coordinated bus of p-4 (both vote p-4). p-3's reply "Glitch." is odd
  wording (his voice is "terse"; still reads like a leaked token).
- Meeting-3 REASONING failure: p-7 and p-9 both argue "I saw p-4, p-5 and p-7 together in EAST_HALL at tick 34 … so p-4
  couldn't have been alone in REACTOR" (p-9: "impossible travel time to kill p-1 in REACTOR by tick 40 without venting")
  — six ticks is plenty; the crew invert cause and effect and attack the reporter. p-4's own reasoning was right ("p-5
  was last seen in WEST_HALL at tick 28 and has no account of their movements").
- Meeting-4: p-5*'s roll-call `whereabouts tick 59 ADMIN` ("I was in Admin when the body was discovered") — false; he
  was in ENGINEERING after venting ADMIN→REACTOR at t58. p-7 was in ADMIN alone and did not see him; no mechanism flags
  "claims to be in the reporter's room, reporter saw nobody". Zero challenge.
- Vote guard as an actor: `meetings/manager.py:3179-3253` (`guard_ballot_target_graph`) redirects an eject whose target has
  no over-gate row to the argmax-rendered candidate. Three ballots in this game were rewritten by it, two of them landing
  on the true impostor. DESIGN: a spectator sees "p-7 -> p-5" with a rationale about p-4.

**(c) World sim.**
- [VERIFIED] Vent in front of two arriving crew (t7) beside a fresh body; venting impostor at the meeting tick (t8).
- [VERIFIED] p-8's body lay in CAFETERIA — the hub — from t4 to t15 across meeting-0; nobody walked through the hub for
  10 ticks. Rejected kills t10 (EAST_HALL→ENGINEERING) and t32 (ADMIN→EAST_HALL).
- [VERIFIED] Idle: p-7 idle t19–29 and t35–49, p-9 t35–49; task counter 12/14 from t28 to t48. Sabotage t29 → everybody
  walks to ENGINEERING and back (t30–35); p-1 walks on to REACTOR alone and dies. Quiet ticks 35/61.
- [VERIFIED] After meeting-2 (t18) p-5* and p-7 resume together in CAFETERIA (no reset), t19–t22 p-1 does a task in
  CAFETERIA with p-5* and p-7 present.

**(d) Watchability.** Meeting-0 (partner defense, bus attempt) and meeting-4 (three players, one lie decides it) are the
scenes. t19–t35 and t41–t55 are dead air.

---

## Game 4 — seed 39 (IMPOSTORS, parity at t34)

Roster: p-3*, p-6*. 3 meetings; the reporter p-1 (innocent, and RIGHT about p-6) ejected 7-0 at t8; two SKIPs; the last
kill happens in front of two arriving crew and ends the game.

**Narrative.** p-6* camps CAFETERIA t0–3, kills p-8 there at t4, idles in EAST_HALL t6–8. p-1 passes through EAST_HALL
(t6), enters CAFETERIA (t7), reports at t8: "I saw p-6 leaving the Cafeteria and heading to East Hall alone at tick 7. P-6,
explain your path." Correct instinct. p-6* deflects onto the reporter; p-3* files `saw_player tick 8 p-1 EAST_HALL` (his
memory: `[tick 8] You saw p-1 move from EAST_HALL to CAFETERIA`, `[tick 7] You saw p-1 move from ENGINEERING to
EAST_HALL`) against p-1's truthful roll-call `CAFETERIA at tick 8` → `[alibi_vs_sighting/strong] Alibi places p-1 in
CAFETERIA (ticks 8-8); sighting reports p-1 in EAST_HALL at tick 8` → seven votes on p-1 ("Flagged lie. Vote p-1.",
"the verified flag proves p-1's alibi is a lie" — the latter from p-6*, the killer). Meeting-1 (t16, p-3 killed p-2 in
CAFETERIA at t13 with p-6* standing there): p-4 reports with p-6 beside him at the body; the crew end at "Max suspicion
0.60 … Skip." — p-6* sat exactly on the threshold and four crew declined to vote him ("barely over the threshold and I
don't want to waste a vote"). Meeting-2 (t28): p-5 found p-4 in STORAGE, having passed p-3 in ENGINEERING one tick after
p-3 exited the STORAGE→ENGINEERING vent (p-5 arrived the same tick and did not see the vent); p-3 lies about the map —
"Engineering is nowhere near Storage" (they are adjacent) — and both impostors attack the reporter; SKIP. t32 sabotage
lures p-7/p-9 out of CAFETERIA; t34 p-3 kills p-5 in ENGINEERING as p-7 and p-9 walk in (both `see players=['p-3@ENGINEERING'] bodies=['body-p-5-34']`) — parity, game over.

**(a) Information.** As above: the flag came from an impostor's movement-derived sighting; p-1's memory had the right
read on p-6 but nothing else. p-5 at meeting-2 says "I was right there when it happened" — he wasn't (kill t24, arrival
t27) — and "p-3 was the last person I saw … in Engineering at tick 27" (true, and it was the killer fresh out of the
vent). Body age again invisible.

**(b) Decisions.** Opening quality good (concrete path, right suspect). Replies: p-6* answers the accusation only with
"I was just passing through East Hall" (no whereabouts) and pivots; p-3* supplies the killing sighting. Ballots: 7/7 herd
on one flag from one (impostor) witness; the two players who could have contradicted it (p-7: "At tick 7, I saw p-1 leave
Engineering and move to East Hall alone" — which supports CAFETERIA at 8) instead cite it as confirmation. Impostor
coordination: p-6* accuses p-1 (0.6), p-3* piles on (0.75) — clean two-voice deflection. p-3's map lie unchallenged.
Impostor memory (p-3 at meeting-0): 40+ movement lines, no self-location, "You saw p-1 move …" ×6.

**(c) World sim.** Spawn camp + hub kill (t4); hub kill again at t13 with the partner present; vent exit as a crewmate
enters (t26); sabotage-lure kill in front of two witnesses (t34) — legal because parity fires immediately. p-7 idle
t22–t32. Quiet ticks 17/36. Meeting-1: p-4 and p-6* resume together in CAFETERIA.

**(d) Watchability.** Meeting-0 is a genuine tragedy for a viewer (right suspect, wrong ejection); t26–28 (p-5 walking
past the venter) is a good rewind; t34 is a cinematic ending. Middle (t17–t23) dull.

---

## Game 5 — seed 36 (CREWMATES by tasks at t51) — the crew win that the impostor threw

Roster: p-2*, p-4*. 4 meetings: SKIP, p-4* ejected (vent), p-6 (the vent witness) ejected wrongly, SKIP.

**Narrative.** t5 p-2* kills p-3 in EAST_HALL; p-7 walks in the same tick and finds p-2 and p-4 with the body ("I saw p-2
and p-4 right there with the body"); p-8/p-9 add "I saw p-2 leave for East Hall at tick 5". Meeting-0: 6 SKIP, 2 votes
p-2 — no flag, so no conviction. t9 p-4* kills p-8 in ENGINEERING, vents to LABS at t11 in front of p-6 → meeting-1: p-6
speaks the vent, p-4 ejected 5-1-1 (p-4's own vote goes to p-6; p-2* skips). t14–t30: crew finish own tasks and idle in
CAFETERIA (p-7 t14–24, p-9 t18–24); p-2* ping-pongs MEDBAY↔WEST_HALL for 12 ticks (t11–t23), sabotages at t24, kills p-1
in MEDBAY at t31, vents to ADMIN. Meeting-2 (t34): p-6 wastes his turn on the dead vent again (`[invalid accusation
target 'p-4' dropped] … I saw p-4 vent in LABS at tick 12`), gives a false roll-call `MEDBAY at tick 34` (he was IDLE in
CAFETERIA t29–t34) → two STRONG flags → **p-6 ejected 4-0, the killer p-2 casting the first vote**. t38 sabotage; t40
p-2 kills p-5 in ADMIN on the way to the repair. Meeting-3 (t45, three alive): p-9 gives the killer an alibi that is
false — "I heard the alarm at tick 40 and was right there in ADMIN with p-2, so he's clear" (p-9 was in EAST_HALL/
ENGINEERING); SKIP. Endgame t46–t51: p-7 alone in ADMIN on the last task; p-2*, kill ready since t44, walks
WEST_HALL→MEDBAY→WEST_HALL→ADMIN→WEST_HALL→ADMIN and never attacks; the task completes at t51.

**Why the impostor did not kill (code opened to explain).** Re-running `ImpostorPolicy.decide` on p-2's reconstructed
memory (`imp_debug.py`, matches the recorded actions exactly): at t50 `own ADMIN cd 0 … targets [('p-6','WEST_HALL',0,1.0),
('p-7','ADMIN',0,1.0),('p-9','CAFETERIA',0,1.0)]`. **p-6 was ejected at t34 but is still a kill target**: `confirmed_dead`
is derived only from bodies seen (`_confirmed_dead_from_bodies`, `agents/tactical/impostor_policy.py:290-297`); an
ejection produces no body, so the ejectee's last sighting (inside the 30-tick staleness window,
`_STALENESS_THRESHOLD=30`, line 185) keeps scoring 1.0 and wins the tie by lowest player id (`sort key (-score,
player_id)`, line ~1008). The FSM therefore STALKS the ghost (moves toward WEST_HALL), and when it stands in WEST_HALL
with the ghost "in the same room but not colocated" it falls through to the IDLE/pretend-task branch and walks toward
its fake task — hence the ADMIN↔WEST_HALL / MEDBAY↔WEST_HALL ping-pong, past the lone crewmate finishing the last task.
[VERIFIED] GLITCH — and the same ghost-target list is visible in seed 12 (`p-1` at t11 lists p-8 and ejected p-3) and
seed 42 (`p-7` at t41 lists ejected p-9). The manifest's "ping-pong pathing in 31 of 32 impostors" is largely this.

**(a)/(b).** Meeting-0: body + both impostors present + two "saw p-2 leave for East Hall at 5" sightings → 6 SKIP, 2
votes p-2 (the reporter p-7 skipped at 0.63 listing p-4 as his alternative; only p-8/p-9, who cited their own
`p-8:5:3`/`p-9:5:3` sightings, voted p-2). Meeting-1: model vent
conviction. Meeting-2: the vent hero is ejected on his own false roll-call (no self-location log; and his memory shows
`[tick 34] You saw p-7 in CAFETERIA (with p-9)` etc.); prompt-forced re-litigation of a dead vent burned his reply.
Meeting-3: crew hallucinated exculpation for the killer. Impostor talk: p-2* "I was just passing through" ×3 across the
game; p-4*'s reply at meeting-1 to a vent accusation is a proverb ("a fox don't need to be in the henhouse…") followed
by a lie that he was in ENGINEERING with the victim "just before the lights went out" (there was no lights sabotage).

**(c).** Positions not reset; p-2 ping-pong 12 ticks; crew idle 17.5% set-wide; sabotage kills (t40 on the way to
repair). Quiet ticks 30/53. Task counter 12/14 from t23 to t37.

**(d).** The endgame is the best spectator moment in the seven games IF you know the rule — a kill-ready impostor
pacing next to the last task — but as broadcast it looks like a bug (because it is one).

---

## Game 6 — seed 42 (CREWMATES by tasks at t45)

Roster: p-4*, p-7*. Two meetings: p-4* ejected (self-alibi lie caught by three sightings), then innocent p-9 ejected on
his own false roll-call; then 28 ticks with no kill and the impostor standing IDLE next to three crew while the last task
finishes.

**Narrative.** t5 p-4* kills p-5 in EAST_HALL with p-7* watching. Three crew (p-1, p-6, p-9) see the body at t10;
p-1 reports at t11 (the same tick p-4 tries to kill p-3 in MEDBAY — pre-empted by the meeting: `KILL-REJECTED t11 …
meeting_tick=True`). Meeting-0: p-4's roll-call "EAST_HALL 9–11" is a lie contradicted by p-3/p-8 sightings (LABS t10,
MEDBAY t11) → 3 STRONG flags → ejected 6-0. Impostor self-tell of the good kind (real lie, real witnesses). t14 p-7*
kills p-6 in CAFETERIA. Meeting-1 (t17): p-7*'s reply "p-9 was slinking off alone to Medbay right before the trouble
started" (true), p-9 answers with a self-contradicting turn — his own observations say `saw p-3 tick 15 MEDBAY (with p-1)`
and `saw p-1 tick 15 MEDBAY`, i.e. HE was in MEDBAY at 15, yet his roll-call says `EAST_HALL at 15` ("I was actually right
there in East Hall where I found p-5's body earlier" — he did not report that body either) → STRONG flag → ejected 5-1.
t18–t45: p-7* never kills again: t20–27 ping-pong CAFETERIA↔EAST_HALL, sabotage t28 and t35 (walk simulators), t41–45
IDLE in CAFETERIA beside p-2, p-3, p-8 while p-1 does the last task alone in ADMIN.

**Why no kill (code opened).** `imp_debug.py` at t41–t45: `targets [('p-2','CAFETERIA',2,0.11), ('p-3',…), ('p-8',…),
('p-9','WEST_HALL',2,0.11), ('p-1','ENGINEERING',3,0.06)]` — the last sighting of p-1 is the t38 repair crowd in
ENGINEERING (score 0.06), ejected p-9 is still a target, and the best target is a co-present-but-witnessed crewmate in
the impostor's own room, so the FSM `wait()`s (KILL_OPPORTUNITY hold) forever. [VERIFIED] The impostor has no notion of
"someone is finishing the last task alone one room away" and no re-plan when holding.

**(a)/(b).** Meeting-0 shows what the flags are good at: an impostor's roll-call lie vs several honest sightings. Meeting-1
shows the flip side: an honest crewmate's confused roll-call vs one honest sighting, same STRONG flag, same 5-vote herd
("p-3 saw both p-1 and p-9 in Medbay then, which directly contradicts p-9's claim" — p-3 herself, at 0.85). p-9's ballot
went to p-7 (the actual impostor, 0.67, citing his own `p-9:13:2` sighting) — the only correct vote in that meeting.

**(c).** Rejected kill on the meeting tick (t11). Body-in-EAST_HALL seen by three crew at t10, one report at t11.
p-7 idle t0–4 (spawn camp) and t41–45; ping-pong t5–10, t20–27, t31–38. Quiet 30/47.

**(d).** Meeting-0 satisfying; after t18 the game is a foregone conclusion the impostor cannot even lose properly.

---

## Game 7 — seed 7 (CREWMATES by tasks at t49)

Roster: p-2*, p-7*. Meetings: SKIP (both impostors at the body), p-7* ejected (vent, two witnesses), innocent p-6 ejected
(false roll-call), SKIP; last task done at t49 while the lone impostor is on cooldown / pretend-tasking in LABS.

**Narrative.** t5 p-2* kills p-3 in EAST_HALL; p-4 walks in on it (`p-4 sees players=['p-2@EAST_HALL','p-7@EAST_HALL']
bodies=['body-p-3-5']`), reports at t6: "When I arrived, p-2 and p-7 were already there". Both impostors turn on the
reporter — p-2*: "you literally just walked into East Hall from the Cafeteria at the exact same tick the body was there";
p-7*: "P-4 is lying. I saw them sprint from Cafeteria to East Hall at tick 5 … that is a timeline built for a kill" (p-4
did move CAFETERIA→EAST_HALL at t5, so the sighting is true and the spin is good). p-6/p-8 place p-2 entering EAST_HALL
at t5. Ballots: 7 SKIP, 1 vote p-7 (p-1); the reporter p-4 had `p-7: suspicion 0.65` in his own table and still skipped
(0.55). t10 p-7* kills p-4 in REACTOR, t12 exits the REACTOR→ADMIN vent in front of p-6 and p-9 → meeting-1 (t14):
p-6 "I saw p-7 vent in ADMIN at tick 13"; p-7*'s reply "You're lying, p-6. I was standing right there in ADMIN with p-9 at
tick 13. You didn't see a vent" (p-9 then confirms the vent); ejected 5-2. Then the seed-21 shape: crew idle in
CAFETERIA (p-8 t18–24, t30–35; p-9 t22–24, t30–35, t41–49), p-2* ping-pongs ADMIN↔WEST_HALL t14–23 and
WEST_HALL↔MEDBAY t24–30, kills p-1 in ADMIN at t32 (alone), meeting-2 (t35): p-6 (the vent witness again!) gives roll-call
`EAST_HALL at 35` while he was in CAFETERIA → two STRONG flags → ejected 4-0 with p-2* voting first ("[invalid accusation
target 'p-7' dropped]" husks in three turns of that meeting). t42 p-2 kills p-5 in ADMIN; meeting-3 SKIP (three alive);
p-8 finishes the last task alone in ADMIN at t49 while p-2*, cooldown 2→0 over t45–t48 (the meeting tick pauses cooldown),
does a pretend task in LABS at t47 (`do_task analyze_specimen`, engine-rejected) and heads for a stale sighting of p-8 in
EAST_HALL.

**(a)/(b).** Meeting-0 is the clearest demonstration that soft evidence never converts: a reporter who walked in on
both impostors with a warm body, two independent "p-2 went in at t5" sightings, and the tally is 7 SKIP. Meeting-2 shows
the vent witness burning his turn on the dead vent (prompt rule) and dying on his own roll-call. Impostor speech: p-2*'s
"Oh god, I mean … I'm just so scared" persona at meetings 2–3 is fine as voice but he also says "before I found the body"
about a body he did not report (t35 speech: "p-5 was the only one who could have gotten there to kill him before I
found the body") — a slip nobody catches. p-8's ballot at meeting-0: `SKIP conf=0.0`.

**(c).** Kill with a crewmate arriving the same tick (t5); vent exit in front of two crew (t12); reporter of meeting-1
resumes in REACTOR alone; sabotage t24/t35 = group walks; task counter 12/14 t23–t31, 13/14 t31–t49 (18 ticks for one
task that changed owner twice by death). Quiet 26/51.

**(d).** Meeting-0 and meeting-1 are watchable; t15–t31 and t36–t48 are not.

---

## Cross-game patterns

1. **The physical layer is a script.** All seven games (and 43/50 in the set) open identically: one impostor idles in
   CAFETERIA t0–3 and kills the cafeteria-task crewmate at t4/t5; the partner kills a lone tasker at t5/t6 and vents;
   the vent is witnessed roughly half the time and that impostor is ejected at the first meeting; the survivor then wins
   or loses a 30–50-tick endgame against crew who have finished their tasks and stand in CAFETERIA. Seeds 21 and 8 are
   near-identical beat for beat. [VERIFIED]
2. **Innocents die on "VERIFIED" flags built from speech vs. speech.** `_detect_alibi_vs_sightings`
   (`meetings/transcript.py:2380-2470`) compares a spoken alibi/roll-call with a spoken `saw_player`; unlike
   `vent_sighting` (grounded against the witness's own record, `meetings/transcript.py:3263`), the sighting is not
   checked against anything, and since 13.14 a self-stated alibi contradicted by one third-party sighting is STRONG. The
   ballot prompt then says "Each flag below is VERIFIED evidence … never side with one over a verified flag". Set-wide
   19/23 wrong ejections carry this flag; in my seven games: seed 12 p-3, seed 39 p-1, seed 8 p-9, seed 36 p-6, seed 42
   p-9, seed 7 p-6 (six of the seven games!). Two sub-causes:
   - (2a) movement lines `[tick T] You saw X move from A to B` get encoded as "X in A at T" while X's own memory says
     "in B at T" (seed 12 p-9→p-3; seed 39 p-3*→p-1; seed 8 p-9's own alibi). [VERIFIED]
   - (2b) crew have **no self-location record** — a crew memory is only "You saw …" lines plus completed tasks with a
     room — yet the roll-call rule demands "the room YOU were in at the tick that matters, copied from your own record".
     Innocent roll-calls are guesses (seed 8 p-9, seed 36 p-6, seed 42 p-9, seed 7 p-6, seed 8 p-4). [VERIFIED]
3. **Ballots follow the printed scalar, not the room.** "Max suspicion 0.55. Below threshold." / "0.59, below the 0.60
   threshold" / "Max suspicion 0.60 … Skip" appear across seeds 12, 21, 8, 39. Body proximity of two impostors (seeds 7,
   36) or an eyewitness at the body (seed 12) does not cross 0.60; a single flag does. The impostor sits at 0.59 for
   whole endgames. [VERIFIED]
4. **Attack the reporter.** 65/165 meetings have ≥2 formal accusations of the reporter; in every impostor win here the
   surviving impostor's standard move is "you were the one who rushed to the scene" and crew join in ("pivoted",
   "convenient timing"). Reporter_exculpation keeps ejections at 3, but it burns every meeting's evidence budget.
5. **Dead-vent re-litigation is prompt-mandated.** The opening/opt-in rule "speak it FIRST … even if you already said
   it" does not exclude ejected/dead venters; witnesses spend the rest of the game repeating it (seed 21 ×4, seed 8 ×3,
   seed 7 ×3, seed 36 ×1), each time leaving `[invalid accusation target 'p-N' dropped]` in their spoken text.
6. **Time of death and body age are invisible.** Bodies persist until found (seed 21: 16 ticks; seed 8: 11 ticks in the
   hub; seed 12: forever), everyone knows the victim is dead from the dead-list at the previous meeting, and yet the
   finding meeting always debates the last three ticks. Nobody's memory carries "last seen X at tick t" or "X announced
   dead at meeting k".
7. **The endgame conveyor.** `dead_task_rule: redistribute` + return-to-hub idling + solo pathing = the surviving crew
   take turns walking alone to REACTOR/ADMIN/STORAGE where the impostor waits (seed 21 ×4, seed 8 ×3, seed 7 ×2). Task
   counters stall for 15–20 ticks; 40/69 ticks in seed 21 have no event at all.
8. **Impostor FSM defects visible from the stands** (all [VERIFIED] by re-running the policy):
   - ejected players and unseen partner-victims stay in the kill/stalk target list → ghost stalking and the
     ADMIN↔WEST_HALL ping-pong; in seed 36 it cost the impostors a won game (kill ready, alone with the last tasker,
     twice, and it walked away);
   - KILL_OPPORTUNITY "hold position" next to a crowd forever while the last task finishes one room away (seed 42 t41–45);
   - stale sightings drive the chase (seed 7 t49); no urgency mode near a task loss;
   - kill attempts on targets in the adjacent room / who just moved (id-order dodge) — 1–2 rejected per game.
9. **Impostor deception is one-note but adequate.** "I was just passing through" (seeds 36, 39, 7), "you rushed to the
   scene", never a partner bus, occasional open partner defense (seed 8), one lie about the map (seed 39 "Engineering is
   nowhere near Storage"), several self-placements INSIDE the body room at the discovery tick that nobody challenges
   (seed 21 p-5 t33, seed 8 p-5 t59, seed 12 p-1 t15). Self-tells reach the record only in non-visible fields
   (structured alibi evidence "killed p-8 at tick 5", ballot rationales "I killed p-6 myself").
10. **Scaffolding in speech and odd wording**: `[invalid accusation target …]` husks in free_text (53/971 turns);
    `[under-gate eject target … redirected]` rewrites of ballots; "Glitch." as a reply; "the lights went out" with no
    lights sabotage; persona "a hidden impostor" (singular) in a 2-impostor game; "I found p-5's body" by non-reporters
    (seed 42 p-9, seed 7 p-2*); a self-sighting `saw_player subject p-9` by p-9 (seed 21).
11. **Sabotage = a walk.** 32 sabotages set-wide, none timed out; 8 kills within 4 ticks of one (seed 39 t34, seed 36
    t40 are the good ones); otherwise the idle crew shuffle to ENGINEERING and back.
12. **Not seen**: bodies reported twice (reported bodies are removed), agents walking past a visible body without
    reporting next tick (all `crew-saw-it` lists are [t, t+1]), kills/vents resolving ON a meeting tick (one kill was
    pre-empted by the same-tick report in seed 42; a venting impostor was mid-vent at meeting time in seed 8), position
    reset after meetings (never happens — DESIGN choice; killers and reporters resume side by side).

## Ranked findings (severity: how often it decides games × how wrong it looks)

1. **STRONG `alibi_vs_sighting` flags are speech-vs-speech yet labelled VERIFIED; they decide 19/23 wrong ejections
   set-wide and 6/7 games here** (seeds 12, 39, 8, 36, 42, 7). GLITCH/DESIGN. Root: (a) no self-location log for crew,
   (b) "move from A to B at tick T" ambiguity, (c) no grounding of the sighting against the speaker's record.
2. **Impostor FSM stalks ghosts** (`_confirmed_dead_from_bodies` ignores ejections/announcements) and **holds forever
   in crowds**; it lost seed 36 outright and produced the 28-tick no-kill tail of seed 42. GLITCH.
3. **The vote is anchored to a printed 0.60 scalar**; eyewitness facts that do not mint a flag (body proximity, seeing
   the killer at the body) never move it, so meetings 2..n in impostor wins are all SKIP. DESIGN.
4. **Endgame conveyor** (redistribute + hub idling + solo tasking) makes every long game the same dull relay; 17% of
   crew ticks are IDLE-with-tasks-done. DESIGN.
5. **Dead-vent re-litigation rule + `[invalid accusation target]` husks** waste the witness's turns and leak scaffolding
   into speech (53 turns). GLITCH (prompt) — trivially fixable.
6. **Time-of-death / body-age blindness**: stale bodies are litigated as fresh kills (seed 21 m1, seed 8 m1). DESIGN.
7. **Vent witnesses can be silenced by the meeting-tick race and a 6-tick emergency cooldown** (seed 12 p-4; 5/97
   set-wide). DESIGN.
8. **Reporter-attack reflex** (65/165 meetings) with impostors amplifying it; unchallenged impostor self-placement in
   the body room. REASONING/DESIGN (missing "reporter did not see you there" contradiction).
9. **Ballot rewrites by the target guard** (`[under-gate eject target … redirected]`) make the tally opaque to a viewer
   and, in seed 8 m3, moved two crew votes onto the true impostor by accident. DESIGN.
10. **Impostor perception/memory economy**: adjacent-room + departure-room movement vision generates 60–80-line memory
    dumps, own sabotage rendered as "You heard a sabotage alarm", beliefs about own victims, first kill aging out of the
    render (seed 8). DESIGN/legibility. Persona singular "a hidden impostor". Wording.

## Concrete ideas

1. **Give every agent a self-track**: render "You were in ROOM (ticks a–b)" lines (or a compact path string) in memory,
   and let the roll-call be filled from it mechanically (or auto-fill it and let the LLM only choose what to add). Most
   false roll-calls disappear; the remaining ones are real lies.
2. **Fix the sighting semantics before flagging**: render moves as "[tick T] X arrived in B from A (was in A at T-1)";
   ground a spoken `saw_player` against the speaker's own perception log the way `vent_sighting` is grounded, and only
   then call it VERIFIED; treat an alibi/sighting mismatch on a move tick as consistent; keep un-grounded sightings as
   testimony (they can still be argued).
3. **Impostor FSM**: fold the meeting-announced dead roster and ejections into `confirmed_dead`; break score ties toward
   the nearest/most-recent sighting rather than lowest id; when `near_win` and no witness-free target, re-plan toward the
   room where a task is being completed alone (the impostor can see the global counter); never `wait` more than N ticks
   in a crowd while a lone crewmate is one room away.
4. **Endgame pacing**: after tasks are done, crew should not stand in one room — pair up and escort the remaining
   tasker (buddy rule), or gain a "sweep" behaviour (walk rooms, find bodies) which also fixes the never-found bodies;
   alternatively give the impostor a reason to leave the hub (kill-target ranking already does) but make the hub
   crowd move as a group to the task room.
5. **Meeting protocol**: put "who was in the room when the body was found / who arrived with the reporter" on the record
   mechanically (the engine knows it), and mint a weak "body-proximity" evidence row that can reach the gate when two
   independent voices place someone at the scene; add an absence contradiction ("X claims to be in R at t; the reporter
   was in R at t and did not see X"); render body age ("p-3 has been dead since before meeting-0; last seen tick 3 heading
   to STORAGE") and drop the "speak the vent even if already said" clause once the venter is out of the game.
6. **Vote design**: show the scalar as a lead, not the arithmetic of the decision ("SKIP is the sound call"), or make
   the gate depend on evidence classes rather than one number; a witness who saw the killer at the body should be able to
   vote them without a flag. Emergency button: let a hard-evidence holder (witnessed vent/kill) call a meeting through
   the cooldown; also render the vent to the witness before the same-tick meeting resolves.
7. **World feel**: reset (or at least group) positions in CAFETERIA after a meeting so the reporter is not left alone
   with the killer; give kills a one-tick "reaction" so a crewmate arriving on the kill tick sees the kill action; make
   sabotage repair need two players in two rooms so it splits (or exposes) the crew instead of walking them in a herd.
8. **Text hygiene**: strip `[invalid accusation target …]` from free_text (or don't allow accusing the dead), never
   rewrite a ballot target silently (record and show "redirected"), fix the persona to the actual impostor count, and
   suppress "You heard a sabotage alarm" for the saboteur.

Working files: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/w8-losses-and-tails/`
(`s{12,21,8,39,36,42,7}.verbose.txt`, `stats.txt`, `stats.py`, `setwide.py`, `setwide2.py`, `imp_debug.py`, `cooldowns.py`, `s12_m1_prompts.txt`).
