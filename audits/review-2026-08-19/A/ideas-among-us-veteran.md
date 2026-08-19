# Ideation — the Among Us veteran's seat

Lens: I am a player with a few hundred hours in the real game, watching these replays as
matches, not as a system. I care about what would make me say *"what are you doing?"* out
loud, and about the plays I keep waiting for that never come.

Grounding: full spectator walks of `replays/samples/9p2i` seeds **2** and **17** and
`replays/samples/4p1i` seed **29**, plus raw-JSONL action traces and five measurement
scripts over all 300 committed games
(`scratchpad/work/ideas-among-us-veteran/{solo2,vet,vet2,alone,idle,endgame,eject_mem}.py`).
Every number below marked [VERIFIED] I computed myself in this pass unless it says
"prior track", in which case it is one of the verification verdicts handed to me.

---

## 0. What I saw in three games (the raw reactions)

**samples/9p2i seed 2 — the chase that cannot end.** [VERIFIED]
At t29 both p-3 (crew) and p-7* (impostor, last kill t17, cooldown 4) stand in MEDBAY.
Raw actions, t30:

```
t 30 p-3:move:{"to_room": "WEST_HALL"} | p-7:kill:{"target": "p-3"} | p-8:wait:{} | p-9:wait:{}
```

The kill is issued and silently annihilated — p-3 sorts first, moves first, escapes. Then:

```
t 31 p-3 -> ADMIN        | p-7 -> WEST_HALL
t 32 p-3 -> EAST_HALL    | p-7 -> ADMIN
t 33 p-3 -> ENGINEERING  | p-7 -> EAST_HALL
t 34 p-3 -> REACTOR      | p-7 -> ENGINEERING
t 35 p-3 reports body    | p-7 -> REACTOR
```

Six ticks of the impostor walking exactly one room behind its target, arriving each time at
the room the target just left. It is mathematically unable to catch a lower-numbered player
who keeps walking. Nothing is emitted: no event, no observation, no memory line. p-3 never
learns it was nearly murdered, and the audience sees a conga line.

Meanwhile `p-8:wait` and `p-9:wait` on **every tick from t28 to t35** — both finished, both
standing in the Cafeteria, while the last working crewmate walks the whole map alone.

**samples/9p2i seed 17 — the killer denies venting from inside the vent.** [VERIFIED]
The tick line at the meeting tick reads
`[t  6] ... p-2*@ENGINEERING:VENT(VENTING) ...` and `>>> MEETING headless-seed-17:meeting-0`.
p-2 then takes turn 1 of that meeting: *"I didn't vent anywhere, p-1, you're clearly making
this up..."*. He is, at that instant, inside the vent p-1 watched him use. The crew ejects
**p-1**, the honest witness, 7–1 — p-4* (the partner) invents *"I was in East Hall with p-1
at tick 5 and 6"*, two crewmates innocently mis-corroborate it, and the detector mints
`alibi_vs_sighting/strong` against p-1 and prints it **above** the correct
`vent_sighting/strong` against p-2 in the same block.

Then t13–t23: p-2*, cooldown expired since ~t9, fake-tasks in ENGINEERING for eleven
consecutive ticks, six of them **alone in the room with p-5**, and never swings. Then
t24–t29 it paces EAST_HALL↔ENGINEERING↔EAST_HALL↔ENGINEERING.

The one genuinely great sequence in everything I watched is also here: t41 p-2* sabotages the
reactor, the three idle Cafeteria crew march EAST_HALL→ENGINEERING together at t42–43, p-2*
peels off to ADMIN where p-5 went alone, and kills at t44. That is a real Among Us play — a
lure that splits the crew — and it works twice.

**samples/4p1i seed 29 — the final three that nobody votes.** [VERIFIED]
Three alive: p-1, p-2 (crew), p-4* (impostor). p-1 reports the body. p-2's ballot reads
*"Where is the proof? P-1's timeline is tight, but P-4 has an alibi. I see no kill, only
noise."* — the alibi being that she was standing next to p-4 in MEDBAY. All three SKIP.
Neither p-2 nor p-4 moves; at t11 p-4 kills p-2 in that same MEDBAY and wins by parity.
A skip at final three is a 0% line. Everyone at the table took it.

---

## 1. The measurements behind the proposals

| # | measurement | value | scope |
|---|---|---|---|
| M1 | rendered memories containing **any** ejection outcome ("ejected", "voted out", "was not", "remain") | **0 / 3,934** (1,799 of them rendered after an ejection had already happened) | all 4 sets [VERIFIED] |
| M2 | global taskbar line `## Tasks completed (global): N / M` present | **3,934 / 3,934** | all 4 sets [VERIFIED] |
| M3 | ejection rate at **CRITICAL** meetings (crew ≤ impostors + 1 → the next kill loses the game) | **73/157 = 46.5%**, vs **362/550 = 65.8%** at all other meetings | all 4 sets [VERIFIED] |
| M4 | games containing a skipped CRITICAL meeting | 84 → **56 impostor wins (66.7%)** | all 4 sets [VERIFIED] |
| M5 | impostor decision points **alone with exactly one crewmate, off cooldown** → declined | samples/9p2i **234/419 = 55.8%**; ml/9p2i 542/1063 = 51.0%; 4p1i 58.9% / 56.7% | all 4 sets [VERIFIED] |
| M6 | impostor A↔B oscillation runs (≥4 ticks pacing between two rooms) | **202 runs**, 78 of ≥6 ticks, longest **25 ticks** | all 4 sets [VERIFIED] |
| M7 | crew agent-ticks with **all tasks done** → action taken | **7,939 ticks**, `wait` **4,792 = 60.4%**; 5,617 of them standing in CAFETERIA; 684 wait-runs, mean 7.0, **max 36**, 28 runs ≥20 ticks | all 4 sets [VERIFIED] |
| M8 | sabotages issued, by kind | **110 reactor, 0 lights** — the lights sabotage has never been used in 300 games | all 4 sets [VERIFIED] |
| M9 | kills with a third party in the killer's room at t−1 | **46 — and in 46/46 the third party is the impostor's own partner.** A crewmate has never been in the room when a kill landed | all 4 sets [VERIFIED] |
| M10 | body-camping: ticks the killer stays in the corpse's room | mean 0.75; 260/798 leave instantly, only 2/798 stay ≥3 | all 4 sets [VERIFIED] |
| M11 | vent shape | 589 `enter` (589/589 same-room), 551 `exit` (551/551 different room). No same-room re-emerge, no multi-hop chain | all 4 sets [VERIFIED] |
| M12 | crew alone-rate vs a uniform-random-placement baseline, by living count | n=9: 17.6% vs 43.0% (0.41×) · n=4: 35.5% vs 72.9% (0.49×) · **n=3: 69.1% vs 81.0% (0.85×)** | 9p2i sets [VERIFIED] |
| M13 | self-reports by the killer | **0 / 626** reports | all 4 sets [VERIFIED] |
| M14 | fake `do_task` visible to a co-located crewmate | yes — seed 17 t19 `p-5 sees players=['p-2@ENGINEERING:task']` — while the spectator DTO shows `p-2*@ENGINEERING:MOVING` | [VERIFIED] |

On **M12**, the honest reading matters: the raw "72% of crew ticks at parity-1 are spent
alone" is mostly a small-*n* artifact. What survives is the *ratio*: at nine alive the crew
cluster at 0.41× the random baseline; at three alive — one kill from losing — they cluster at
0.85×, i.e. **essentially at random**. The crew's grouping instinct decays to nothing exactly
when a veteran's would peak. [VERIFIED counts, [JUDGMENT] on the reading.]

---

## 2. Ranked proposals

Ranked by (drama + believability recovered) ÷ (cost + risk), from the player's seat.

Standing risk note that applies to almost all of them: the committed replays are
state-hash-pinned, so any engine/policy/memory-render/prompt change invalidates them.
Per the project's own substrate-cadence doctrine these should be batched into **one wave
with a single combined re-record**, not shipped one at a time. Where a proposal is free of
that cost I say so explicitly.

---

### V1 — Announce the ejection result, and the impostor count. `S` · **rank 1**

**What.** After an ejection, write one line into every survivor's memory:
`[tick 14] p-4 was EJECTED — p-4 was an IMPOSTOR. 1 impostor remains.` (or `was a
CREWMATE`). Parameterise the persona line by impostor count while you are in there.

**Why (M1, and prior-track G-27/G-23).** In 3,934 rendered memories across 300 games there
is not one word about who was ejected or what they turned out to be — including the 1,799
memories rendered *after* an ejection already happened. Meanwhile the persona says "a hidden
impostor", singular, in 628/628 two-impostor meetings. The crew therefore cannot count, cannot
know the case is closed, and cannot tell a 2-impostor game from a 1-impostor game. This is
the direct cause of the corpus's most embarrassing meetings: seed 2 meeting-2 and meeting-3
are spent almost entirely re-prosecuting p-4, who was ejected at meeting-1 — p-8's turn is
`[invalid accusation target 'p-4' dropped] I saw p-4 vent in ENGINEERING at tick 11...`,
three meetings running.

In the real game "**X was not the Impostor. 1 Impostor remains.**" is the sentence the entire
mid- and endgame is built on. Without it there is no such thing as a cleared player, no
"we're 1-and-1", no reason to escalate.

**Effect.** Kills the corpse-relitigation meetings outright. Makes SKIP visibly expensive.
Makes the second impostor a real hunt instead of an unannounced surprise. Watchability: the
ejection finally *lands* — right now the airlock is silent.

**Risk.** Prompt-version bump + re-record. Firewall-clean (the ejected player's role is public
information the moment they are gone). Will move crew win-rate up; measure before tuning.

**Measure.** % of turns whose accusation is struck for naming an out-of-game player (5.0–5.5%
today); CRITICAL-meeting eject rate (M3); crew win-rate split by whether the first ejection
was correct.

---

### V2 — Tell the table when a skip loses the game. `S`–`M` · **rank 2**

**What.** In the ballot prompt, when `crew_alive ≤ impostors_alive + 1`, add a hard clause:
*"This is the last meeting you get. If nobody is ejected, the next kill ends the game and the
impostor wins. A skip here is a loss, not caution."* Optionally drop the skip threshold at
that state.

**Why (M3, M4).** CRITICAL meetings eject **46.5%** of the time versus **65.8%**
everywhere else — the crew becomes *nineteen points more passive* precisely where passivity
is fatal — and 84 skipped criticals produced **56 impostor wins (66.7%)**. I grepped the six
`qwen3_6_27b` templates: there is no parity, endgame, alive-count or last-meeting language
anywhere. What the ballot prompt *does* hand them is the arithmetic — `vote_ballot.j2:143-144`
literally states "the skip threshold is **0.60**" — which is why the corpus contains 208
utterances quoting "the 0.60 threshold" and why 4p1i seed 29's three-handed final vote reads
*"my suspicion of p-4 remains below the threshold"* one tick before p-4 wins.

Every Among Us player knows the final-three rule: you always vote. A 33% guess beats a 0%
skip. These agents do not know they are at final three, because nothing tells them.

**Effect.** Turns the last meeting into the climax the whole game is building toward. Forces
the impostor to actually defend itself instead of dropping a stock SKIP.

**Risk.** Prompt bump + re-record; directly shifts the win split, so land it with V1 and
measure the pair.

**Measure.** CRITICAL eject rate (target: above the non-critical rate, not below);
IMPOSTOR_PARITY share of impostor wins; skip rate by living-count bucket.

---

### V3 — Post-meeting reset: everyone to the Cafeteria, vents ejected, cooldown graced. `M` · **rank 3**

**What.** On meeting close: teleport every living player to CAFETERIA, force any venting
player out of the vent first, and either reset or grant a short grace on the kill cooldown.
Sweep bodies the meeting knew about.

**Why (prior-track G-5, plus my exemplars).** All living players were in CAFETERIA in
0/39, 0/165, 0/40 and 3/463 meetings; **111/707 (15.7%) of reporters are killed within three
ticks of the meeting they themselves called**; **69/707 (9.8%) of meetings have a participant
speaking from inside a vent**. My two cases are the ones I would clip:
seed 17 t6 — p-2* argues *"I didn't vent anywhere"* while the world state says
`p-2*@ENGINEERING:VENT(VENTING)`; 4p1i seed 29 — p-4* stands beside p-2 through the meeting,
neither moves, and kills her at t11.

Nobody who has played the game will accept this. You slam the button, everyone appears at the
table, and when the doors open you are all standing in the same room with a fresh cooldown.
Being murdered by the person you just debated, from the exact tile they were standing on,
is not a play — it reads as the world forgetting to run.

**Effect.** Removes the single most "this is broken" artifact. Creates the post-meeting
scatter that manufactures the alibis the meeting later argues over. Ends the free execution.

**Risk.** Engine change → full re-record; materially changes the kill economy (the impostor
loses ~15% of its kills). Determinism fine (deterministic teleport). Believability payoff is
the largest on the list.

**Measure.** reporter-killed-within-3 rate (target ≪15.7%); in-vent meeting participants
(target 0); distribution of kill ticks relative to meeting ticks.

---

### V4 — Resolve movement before kills, and emit the near-miss. `M` · **rank 4**

**What.** Either resolve `move` before `kill` within a tick, or seed-randomise the intra-tick
actor order and record it. Either way emit a `kill_attempt_evaded` event so the escapee, the
meeting and the spectator learn it happened.

**Why (prior-track G-10, plus seed 2).** 246 contested attempts corpus-wide: victim
lower-id escaped **156/156 (100%)**, victim higher-id died **90/90 (100%)**. Escape rate by
seat runs p-1 25% down to **p-9 0%**. That is a silent per-seat immunity over a quarter of all
kill attempts, and it produces the seed-2 conga line above: p-7 issues a kill at t30, it
vanishes, and it then trails p-3 one room behind for five more ticks without ever being able
to close. From the seat this looks like the impostor is *choosing* not to kill, which poisons
every other read the audience makes.

**Effect.** Fairness. 156 discarded set-pieces become the near-misses they should be — "he
lunged at me in Reactor and I walked out" is a *meeting-opening line* in the real game. The
chase resolves instead of looping.

**Risk.** Engine ordering change → full re-record. Byte-determinism preserved as long as the
order is seeded and recorded. `kill_attempt_evaded` must be scoped carefully — giving the
escapee certainty of the attacker's identity is a large crew buff; a "someone lunged at you"
without a name is the safer first version.

**Measure.** escape rate by seat (target: flat); count of ≥3-tick one-room-behind pursuits
(should go to ~0); meetings citing an evaded attempt.

---

### V5 — Give finished crewmates a job. `M` · **rank 5**

**What.** A crewmate with no pending task picks one of: patrol the rooms nobody has visited
recently, escort the nearest living crewmate, sweep for bodies, or walk to the button.
Anything but `wait`.

**Why (M7, M12, and prior-track G-6/G-15).** **7,939** crew agent-ticks in the corpus have
all tasks done; **60.4% of them are a literal `wait` action**, and **5,617 of those are spent
standing in the Cafeteria**. 684 distinct wait-runs, mean 7.0 ticks, **max 36**, 28 of them
≥20 ticks. Seed 17: p-9 waits from t12 to t41 — thirty ticks — while three teammates are
murdered; p-6 and p-8 join it and the three of them stand there together. Seed 2: p-8 and p-9
wait t28–t35 while p-3 walks the entire map alone to find the body that decides the game.

Downstream: 172/798 bodies are never reported and 96.5% of those lie in rooms no living
crewmate ever re-enters. And per M12 the crew's clustering *decays* to random exactly at
final three.

There is nothing in Among Us worse to watch than three finished players standing on the
cafeteria table. In the real game those players are the crew's whole second act — they follow,
they escort, they sweep, they are the reason a body gets found in twenty seconds instead of
never.

**Effect.** Halves the dead time (48.6%/45.9% of 9p2i ticks currently contain no event at
all). Finds the bodies. Manufactures the witnesses the meeting is starving for. Restores the
buddy system the format has never had.

**Risk.** Policy change → re-record. Shifts crew win-rate up and shortens the impostor's free
window; land it in the same wave as V6/V9 so the two sides move together.

**Measure.** `wait` share of done-crew ticks (M7); never-reported-body rate (21.6%);
event-free tick share; crew alone-rate ratio to baseline at n≤4 (M12).

---

### V6 — Impostor: look before you pop the vent. `S`–`M` · **rank 6**

**What.** Never `VENT_EXIT` into a room the impostor can already see is occupied — it has
adjacent-room vision, so the information is free. Don't reflex-vent the tick after every kill.
Prefer an exit that puts a room between you and the corpse.

**Why (prior-track G-13, plus seed 2).** Vent **exits** are seen by a crewmate 56.5% /
59.2% of the time; vent **enters** only 8.8% / 6.4%. 310/435 ejections (71%) are a
`vent_sighting`. Seed 2 is the cleanest possible demonstration: **both impostors lose the
game to the identical mistake.** t10 — p-4* exits STORAGE→ENGINEERING into a room where p-8
is tasking, and is ejected at meeting-1. t20 — p-7* exits REACTOR→STORAGE into a room where
p-3 is tasking, and is ejected at meeting-3. In both cases the impostor could see the
destination was occupied.

To a veteran this is the single dumbest recurring play in the corpus. You do not pop a vent
in front of someone. Ever. It is the first thing anyone learns.

**Effect.** Raises the impostor's skill floor from "beginner" to "competent". Breaks the
`vent_sighting` monoculture (71% of all ejections), which forces the crew to win on actual
deduction. Watchability: the impostor stops handing itself in.

**Risk.** Policy change → re-record. **Will lower the crew win-rate**, possibly a lot, since
vents are how the crew wins nearly every game it wins. Must ship in the same wave as V1/V2/V5
and be measured jointly.

**Measure.** exit-witnessed rate (target ≪56%); ejection-cause mix; crew win-rate and the
share of crew wins not carried by a vent.

---

### V7 — Stop calling two people disagreeing "VERIFIED evidence". `S` (relabel) / `M` (ground it) · **rank 7**

**What.** Split the flag block in two. *Proof*: `vent_sighting`, `alibi_vs_physical` —
engine-certified, keep the current language. *Conflicting accounts*: `alibi_vs_sighting`,
`alibi_conflict` — reworded to "one of these two accounts is wrong and nothing here says
which". Better: ground the sighting side against the sighter's own perception log the way the
vent flag already is (the `SightingRecord` machinery from Task 16.7 exists but is wired only
to the exculpatory vouch), or require two independent sources for STRONG.

**Why (prior-track G-2).** `vent_sighting` is 440/440 precise. `alibi_vs_sighting/strong`
names an impostor **17.2%** of the time against a **25.3%** random baseline — *below chance*,
p=0.0048 — and as the sole convicting evidence it goes **12 right / 70 wrong = 14.6%
precision**, while flipping a meeting's ejection rate from 13.7% to **93.9%** and landing on a
crewmate 84.4% of the time. 63.5% of the sighting sides were never perceived by the speaker
at that tick.

I watched it decide seed 17 meeting-0: the block prints two `alibi_vs_sighting/strong` flags
against the honest vent witness p-1 and *then* the correct `vent_sighting/strong` against p-2,
all under the same "VERIFIED evidence" header. p-8's ballot: *"1. p-1 claimed to see a vent in
Engineering. 2. p-4 and p-6 place p-1 in East Hall at that exact tick. 3. This verified
contradiction proves p-1 is lying."* The crew was reasoning correctly from a label the game
had no right to print.

From the seat: this is the game telling the table "the cams confirm it" when all it has is two
players remembering a hallway differently. It is why the crew looks sharp right up to the
moment it airlocks the one person who actually saw something.

**Effect.** The largest single believability win available in the meeting. Correct ejections
stop losing to bookkeeping noise. Innocents (79/435 = 18.2% of all ejections today) stop being
manufactured.

**Risk.** Prompt bump + detector change → re-record; a large swing in the ejection mix. Note
this is already tracked as a P1 Phase-19 item, and the LONE-STRONG relaxation was a twice-
ratified owner decision — so this is a *revisit*, not a bug report.

**Measure.** precision of each flag class **as sole convicting evidence**; innocent-ejection
rate; sole-flag meeting eject rate (93.9% today).

---

### V8 — Let a crewmate remember where they were standing. `S` · **rank 8**

**What.** Render the self-location trail the memory store already keeps
(`own_room_by_tick`): `[tick 12-16] You were in REACTOR.` And re-stamp the completed-task
line with the tick its room actually belongs to.

**Why (prior-track G-1).** The only self-position line in the entire render is the suffix of
`You completed <task> (you were in ROOM)` — 843 instances — and that room matches the agent's
actual room at the stated tick only **16.0%** of the time (it matches at N−1 97% of the time).
Meanwhile the accusation prompt orders every speaker to answer the roll-call with a room
"copied from your own record". Result: **20.5% of crew self-placements are false**, and
**44.3% of the 79 innocent ejections** are the victim mis-stating its own position into a
STRONG flag.

A crewmate who cannot retrace their own route is not a crewmate. In the real game that
retrace *is* the alibi — "Medbay, then Upper Engine, then Security" — and it is the only
thing standing between an innocent and the airlock.

**Effect.** Removes the biggest single source of innocent ejections. Makes the roll-call a
real mechanic instead of a trap that punishes whoever answers it honestly.

**Risk.** Memory-render change → prompt bump + re-record. Strongly crew-favouring. Cheapest
high-impact item on the list — the data is already in the store.

**Measure.** crew whereabouts-false rate (20.5% today); innocent-ejection share (18.2%);
`alibi_vs_sighting` flag volume.

---

### V9 — Make the impostor take the free kill, and stop the pendulum. `M` · **rank 9**

**What.** When alone with exactly one crewmate and off cooldown, kill — unless there is a
named reason not to (a witness one room away, a body already in the room, a meeting imminent).
Replace the A↔B pendulum with a dwell: stand still and fake a task, which co-located crew
*can* see.

**Why (M5, M6).** **55.8%** of clean solo-kill decision points in samples/9p2i are declined
(51–59% across all four sets). Seed 17 is the tail case: p-2*, off cooldown since ~t9,
fake-tasks beside p-5 in ENGINEERING for six straight ticks and never swings, then paces
EAST_HALL↔ENGINEERING for six more. Corpus-wide there are **202** such oscillation runs, 78 of
them ≥6 ticks, the longest **25 ticks**.

Also M9: in the 46 kills that happened with a third party in the room, that third party was
the impostor's own *partner* every single time. A crewmate has never been in the room when a
kill landed — which means the risk the policy is apparently pricing in does not exist.

A solo crewmate in a dead-end room is the money kill. Passing on six in a row, while
pretending to do the same task next to them, looks like the AI fell asleep.

**Effect.** Shortens games, raises tension, deletes the pendulum. The dwell also reads far
better than pacing: an impostor standing at a console next to his next victim is a *shot*.

**Risk.** Policy change → re-record; will swing the win-rate toward impostors, so it must land
with V1/V2/V5. Some declines are legitimate (a body would be found immediately) — the rule
should be "kill unless a named reason", not "always kill", so the reasons become inspectable.

**Measure.** declined-1v1 rate (M5); oscillation-run count (M6); mean game length; kills per
impostor-alive-tick.

---

### V10 — Let "I saw him kill" be evidence. `M` · **rank 10**

**What.** Add a `saw_kill` observation shape and a `kill_sighting/strong` contradiction kind,
weighted at or above `vent_sighting`.

**Why (prior-track G-8).** The turn schema has no witnessed-kill shape and the contradiction
vocabulary has no kill kind, so `You witnessed pN kill in ROOM` is **0.02%** of all rendered
memory lines and reaches peers as a **+0.08** belief nudge. 4p1i seed 22: p-3 holds the line,
opens with it at confidence 1.0, no flag fires, and the meeting SKIPs. 9p2i s45: two crew
witness the same kill and lose 3–3 to an `alibi_vs_sighting` flag on an innocent.

"I saw him kill" is the strongest sentence anyone ever says at an Among Us table. Here it is
worth less than a mis-remembered hallway. Note this pairs with V3/V5/V11: today (M9) a
crewmate is never in the room when a kill lands, so the channel would start empty — it becomes
live only once the crew stop standing still and start walking in on things.

**Effect.** Gives the crew a top-tier evidence channel and makes killing in company genuinely
risky, which is what makes an impostor's positioning a *decision*.

**Risk.** Schema + detector change → re-record. Firewall-clean.

**Measure.** count of kill sightings that reach a flag and convert; conversion rate versus
`vent_sighting`'s 96.7–97.1%.

---

### V11 — Let the crew see a corpse through an open doorway. `S` · **rank 11**

**What.** Extend crew visibility to adjacent-room **bodies only**. Players stay same-room-only.

**Why (prior-track G-6/G-14).** Cross-room body sightings: impostor 413, crewmate **0, ever**.
172/798 bodies (21.6%) are never reported and **96.5% of those lie in a room no living
crewmate ever re-enters** — a fifth of all the murders in this game happen entirely outside
the fiction. `engine/visibility.py:93` already gates bodies on the visible-room set; giving
bodies the base mode is a one-predicate change.

Walking past an open door with a corpse two metres inside and registering nothing is the
clearest "this is a simulation" moment in the whole product.

**Effect.** More reports, fewer silent deaths, shorter kill→report latency (median 4, max 30
today) — and it threads the needle: the Task-13.8 forcing function ("crew must *infer* kills")
is untouched, because they still never see the kill, only the aftermath.

**Risk.** Engine change → re-record; crew-favouring. Small and surgical.

**Measure.** never-reported-body rate; kill→report latency; report rate by room.

---

### V12 — Put a time of death on the body. `S` · **rank 12**

**What.** Stamp `found_body` with the death tick, or — safer — a `fresh` / `cold` band.

**Why (prior-track G-7).** All **963/963** `found_body` observations carry the *report* tick,
never the death tick: median offset 4, max 30, **zero exact**. Seed 2 meeting-0 opens with
p-1 saying *"I found poor p-2 cold as a cucumber in the Cafeteria **just a tick ago**"* — the
kill was at t4, the report at t7 — and the entire roll-call then interrogates ticks 5–7, a
window in which the killer had already left the room.

Every Among Us player calls it: "body was in Electrical, it was *fresh*". That one word is
what points the whole discussion at the right ninety seconds. Without it the meeting reliably
litigates the wrong window, which is upstream of a large share of the bad flags in V7.

**Effect.** Alibi windows finally point at the murder instead of at the discovery.

**Risk.** Observation-schema change → re-record. An exact tick leaks more than a corpse
plausibly reveals; the `fresh`/`cold` band is the version I would ship.

**Measure.** fraction of roll-call windows that contain the true kill tick (near 0 today).

---

### V13 — Let the impostor self-report. `S`–`M` · **rank 13**

**What.** Allow — and sometimes prefer — the impostor reporting its own kill, especially when
it was seen entering the room.

**Why (prior-track G-22/G-33).** **0/626** body reports and **0/707** meeting calls by an
impostor in 300 games. The pinned `impostor_report.qwen3_6_27b.v3` template has **0 calls out
of 7,932** meeting LLM calls — a version-bumped template that has never once executed. Add
that half of all impostor turns arrive with no `whereabouts` (crew: 99.6%), giving
P(impostor | no whereabouts) = 97.7–100%.

The self-report is the genre's signature bluff — you kill, you press the button, you tell the
story first, and you are the most credible person at the table for the next ninety seconds.
"The impostor has literally never reported a body" is a tell a human crew would find in one
game and never stop using.

**Effect.** Deletes a mechanical role tell, adds the best impostor set-piece in the genre, and
finally exercises a shipped template.

**Risk.** Policy change → re-record. Firewall-clean. Modest balance effect.

**Measure.** impostor share of reports; survival rate of self-reporting impostors versus
fleeing ones; P(impostor | turn has no whereabouts).

---

### V14 — Make the lights sabotage worth pressing. `S` · **rank 14**

**What.** Either make `lights` degrade the crew *below* their baseline (no co-presence
perception at all, or no name resolution — "someone is in here with you"), or let the impostor
keep base vision through it. As shipped it is a self-harm button.

**Why (M8, and `engine/visibility.py:113-127`).** **110 sabotages in 300 games, 100%
`reactor`, 0 `lights`** — the single most iconic impostor tool in the genre has never been
used. And it can't be: crew are already downgraded to `same_room_only` by the Task-13.8
asymmetry, while `lights` "still degrades EVERYONE, the impostor included" (the code's own
docstring). So pressing it costs the impostor its adjacent vision and costs the crew nothing.
It is strictly negative-value, and the policy has correctly never touched it.

Meanwhile the reactor sabotage already demonstrates what a working one looks like — seed 17
t41 is the best tactical sequence in the corpus: sabotage, the Cafeteria trio marches out
together, the impostor peels off and kills the straggler in ADMIN at t44, and repeats it at
t51.

**Effect.** Gives the impostor a second real lever and opens a whole class of argument —
"who was next to me when the lights went out" — which is also currently being *hallucinated*:
agents reference the lights going out in games (s36, 1089, 1008) that had no lights sabotage.

**Risk.** Engine + balance change → re-record. Small code surface, real balance consequences;
tune duration/repair alongside.

**Measure.** lights usage; kills during a lights window; kills within 4 ticks of any sabotage
(8 today).

---

### V15 — Fire the emergency button on hard evidence. `S` · **rank 15**

**What.** Trigger the button on any *new* first-hand vent or kill observation, regardless of
the prior suspicion level, and let a hard-evidence holder call through the cooldown.

**Why (prior-track G-17).** **112/112** presses carry the same canned
`reason: suspicion_accumulation`; **0/112** are made with a body in view; 71/112 fire at
t10–t11. It is a timer wearing a button's clothes. And the eligibility rule needs a *fresh*
below→above-0.6 crossing, so a crewmate who was already suspicious can witness a vent and be
*ineligible* to call: seed 2's p-3 holds a first-hand vent at belief 1.00 for **15 ticks** and
never presses.

That is the one thing the button exists for. A crewmate who watches someone vent and then
quietly goes back to wiring for fifteen ticks is not playing the game.

**Effect.** Converts the crew's best evidence immediately, while the memory of it is intact.
Makes the button a decision rather than a clock. Note the button already works when it fires:
all 81 emergency meetings carry a vent flag and 78/81 eject an impostor.

**Risk.** Policy change → re-record; crew-favouring; more meetings means more LLM cost per
game — worth checking the budget.

**Measure.** presses with a first-hand vent/kill in memory; median ticks from vent sighting to
the next meeting; presses per game.

---

### V16 — Show the fake task on the spectator surface. `S` · **free**

**What.** Project the *intended* action into the spectator DTO — `PRETEND_TASK`, `EMERGENCY`,
`REPAIR`, `BLOCKED` — instead of the last resolved engine label.

**Why (M14, prior-track G-38).** 1,747 fake `do_task` intents render as IDLE (800) or MOVING
(844) and **TASK 0 times**. I confirmed the in-world side is correct — at seed 17 t19 the
co-located crewmate genuinely sees `p-2@ENGINEERING:task` — so the impostor's best bluff
*works*, and the audience is the only party who cannot see it. What a viewer gets instead is
p-2 "walking in place" in Engineering for eleven consecutive ticks.

**Effect.** Pure watchability. The impostor coolly faking wiring beside the person it is about
to kill is the most watchable frame this simulation can produce, and it is currently invisible.

**Risk.** **None.** DTO/frontend only — it touches nothing the engine hashes, nothing in a
prompt, nothing in the eval. This is the one item on the list that can ship on its own,
immediately, with no re-record.

**Measure.** n/a — visual check against the intent stream.

---

## 3. Three things I would NOT change

**N1 — The crew's same-room-only vision (Task 13.8).**
It is tempting to "fix" the 41% of murders that happen one doorway from a blind crewmate. Do
not. It is both the project's deliberate forcing function — the crew must *infer* kills rather
than witness them, which is the only reason the meeting has to exist — and, separately, it is
exactly how the real game feels: you see your screen and nothing else, and the terror is
entirely about what you *cannot* see. Fix the corpse case (V11), which is the part that reads
as broken. Leave the players blind.

**N2 — The vent as the crew's one hard tell, at 100% precision.**
440/440 `vent_sighting` flags name an actual impostor, 99.6–100% of held vents reach the
table, and 96.7–97.1% convert to the correct ejection. That is the only clean channel in the
entire information economy and every good ejection in the corpus runs through it. Do not
dilute it with fabricated vent claims, do not soften its weight, do not hide it behind a
corroboration requirement. If V6 makes vents rarer, that is correct — rarer and still perfect
beats common and noisy. The problem was never the vent flag; it was everything sharing its
label (V7).

**N3 — Sabotage as a stall and a lure, not a win condition.**
The reactor sabotage never times out, has produced 0 IMPOSTOR_SABOTAGE wins in 300 games, and
is documented as a deliberate stall. Leave it that way. Seed 17 t41 already shows it doing the
job it should do — splitting a grouped crew so the impostor can pick off the straggler — and
that sequence is the best tactical play in the corpus precisely *because* it wins a kill, not
the game. Turning sabotage into a win lever would replace deduction with a timer, which is the
exact failure mode the project already dug itself out of once (the Wave-D stopwatch).

---

## 4. Sequencing note

Six of these move the win-rate hard and in opposite directions: V1, V2, V5, V8, V11, V15 push
crew-ward; V6, V9, V14 push impostor-ward; V3 and V4 change the kill economy outright. Shipping
any subset alone will produce a balance reading that says nothing. The project's own
substrate-cadence doctrine already prescribes the answer: batch them into one wave, freeze
during measurement, and take **one combined re-record**. The only item that escapes this
entirely is **V16**, which is frontend-only and can go today.

If I had to pick three to build first, from the seat: **V1** (the crew cannot count),
**V3** (the meeting is not a place), **V5** (half the crew is a statue). Those three are what
a viewer notices in the first game they watch.
