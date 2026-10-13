# w5-4p1i-featured — spectator review of replays/samples/4p1i seeds 29, 2, 41 (featured) + 0, 1, 5, 10

Method: watched every tick with `watch.py --verbose` (all 7 games), read every living voter's rendered
memory at every meeting (`dumpmem.py` on top of `ReplayLoader.get_meeting_memory`), and read the full LLM
prompt+response of every meeting call for seeds 41, 5, 29, 0, 10, 1, 2. Code was opened only to explain
observed behaviour; each such citation is marked file:line. Tick convention: world ticks `t N` are the
watch.py tick index; the agents' memory/observation ticks run ONE AHEAD (obs `[tick 5]` = world `t4`;
spawn frame `t-1` = obs tick 0). I quote both where it matters.

Map (engine/maps/canonical_1.yaml): CAFETERIA–{UPPER_HALL,EAST_HALL,WEST_HALL}; UPPER_HALL–ADMIN;
ADMIN–{EAST_HALL,WEST_HALL}; EAST_HALL–ENGINEERING; ENGINEERING–{REACTOR,STORAGE}; WEST_HALL–MEDBAY;
MEDBAY–LABS. Vents: REACTOR–STORAGE–ENGINEERING–LABS–MEDBAY–ADMIN–REACTOR ring. kill_cooldown_ticks=4.
4p1i uses tasks_per_crewmate=1 (3 tasks total in the game). Crewmates see ONLY their own room; the
impostor sees own + adjacent rooms (engine/visibility.py:98-128, Task 13.8 asymmetry).

---------------------------------------------------------------------------------------------------
## Seed 29 — IMPOSTORS (parity), 12 ticks, 1 meeting (SKIPPED). p-4* impostor.

**Narrative.** t0-t1 the crew splits: p-1+p-2 west (MEDBAY), p-3+p-4* east (ENGINEERING). t2-t3 p-4*
fake-tasks next to p-3 in ENGINEERING (p-3 sees `p-4@ENGINEERING:task` — the rejected impostor do_task is
rendered byte-identical to a real task, observation/service.py:387-450). t4 p-4* kills p-3 (no witnesses),
t5 enters ENGINEERING_VENT, t6 exits in LABS (empty), t7-t8 fake-tasks in LABS while watching p-2 tasking in
MEDBAY through the adjacent-room window, t9 walks into MEDBAY beside p-2. Meanwhile p-1 abandons its LABS
task at 2/4 ticks (see "inheritance" below), walks LABS→MEDBAY→WEST_HALL→ADMIN→EAST_HALL→ENGINEERING (5
hops, t5-t9), sees the body at t9, reports at t10. Same tick t10 p-4* SUBMITS `kill p-2` in MEDBAY (raw
JSONL t10: `{'actor':'p-4','payload':{'target':'p-2'},'type':'kill'}`) — the report (lower actor id)
resolves first, the meeting opens, the kill is not applied. Meeting: all three SKIP (conf 0.4 each). t11,
nobody has moved (p-4* still in MEDBAY with p-2), p-4* kills p-2 → parity. The meeting delayed the kill by
exactly one tick.

**(a) Information.** p-1 knew: it saw p-2 in MEDBAY at obs 2 and 6, "completed log_findings" (FALSE — see
bug B1), discovered body at obs 10. Nothing about p-4 after spawn. p-2 knew: p-1's MEDBAY entries/exits (obs
3,6,7 — movement perception works: "You saw p-1 move from MEDBAY to LABS"), and "[obs p-2:10:1] You saw p-4
in MEDBAY (moved from CAFETERIA, last seen there at tick 0)". p-4* knew everything (adjacent vision), plus
8 lines of "Your kill cooldown is N ticks" clutter. Nobody's memory contains their OWN location trail — p-1
cannot say "I was in LABS 3-4, MEDBAY 5, WEST_HALL 6, ADMIN 7, EAST_HALL 8, ENGINEERING 9" because the
render never emits it (agents/memory/store.py renders own room only inside the "(you were in X)" suffix of
completed-task lines). Rendering redundancy: p-2's memory carries the same movement twice ("[obs p-2:7:1]
[tick 7] You saw p-1 move from MEDBAY to WEST_HALL" AND an un-id'd "[tick 7] p-1 left MEDBAY"). The
report-tick's own sightings are NOT in memory at the meeting (p-2 sees `p-4@MEDBAY` at t10 but the last
memory line is obs 10 = t9) — fine here, decisive in seed 5.
Human-obvious things the agents do not know: who was standing next to whom when the report happened; that
p-3 was the only witness of p-4's whereabouts and p-3 is the one who died; time of death (nobody knows the
kill was 6 ticks before discovery, so p-2's "p-4 was in Medbay with me at tick 10" alibi is irrelevant but
lands as exculpatory).

**(b) Decisions.** Opening (p-1): grounded, sensible elimination ("no information on p-4's whereabouts...
primary suspect by elimination", conf 0.5). Reply (p-4*): never states where it was (the impostor reply
template forbids it: "explain nothing about your own whereabouts", seed-41 prompt dump), and invents a map
argument: "p-1 was in Labs at tick 5 and suddenly appeared at the scene by tick 10, which is a very tight
window to cross the station" — [VERIFIED] LABS→ENGINEERING is exactly 5 hops; p-1's walk was the minimum
path, not tight. Opt-in (p-2): "I saw p-4 in Medbay at tick 10!" (true, irrelevant) + accuses the reporter
p-1 at 0.7 "left Medbay at tick 7 — how did you get to Engineering so fast?" (it took 3 more ticks; normal).
Ballots: three SKIPs, all conf 0.4, rationales "too thin/noise". The ballot prompt showed every voter
suspicion 0.50 with "this meeting +0.00" for everybody (seed29.prompts.txt lines 444, 525-526, 608): the
spoken accusations moved no number, threshold 0.60 → SKIP is what the arithmetic prescribes. Outcome: wrong
in effect (SKIP = loss in 4p1i after one kill), but no voter had anything better than a hunch. Impostor
deception: adequate (calm, redirect) but it never offers an alibi, which a human table would notice.

**(c) Sim holes.** [VERIFIED] no relocation after the meeting (t11: p-1@ENGINEERING, p-4*@MEDBAY,
p-2@MEDBAY — exactly where they were at t10); [VERIFIED] kill cooldown not reset by the meeting → kill at
t11, one tick after; [VERIFIED] impostor kill submitted ON the report tick (rejected/ignored, correct);
[VERIFIED] the previous body is gone at t11 (bodies cleared by the meeting). watch.py shows p-4* as
`LABS:VENT` at t7-t8 while the raw action is `do_task analyze_specimen` — that is a watch.py artefact
(rejected do_task leaves last_action=vent), not the sim; crew observers correctly saw "task".
Fake-tasking is convincing (p-3 saw p-4 "task" for 2 ticks). Kill was in a dead-end room with the only
witness as victim: good impostor play. p-1's task abandonment at 2/4 (t5) is FSM behaviour, not intent.

**(d) Watchability.** Tight, 12 ticks, one real beat: the t10 double action (report vs. kill in the same
tick) and the t11 execution. Rewind point: t10. Boring: nothing — but also nothing to deduce; the meeting is
decorative.

---------------------------------------------------------------------------------------------------
## Seed 2 — CREWMATES (eject), 12 ticks, 1 meeting (EJECTED p-2*, correct). p-2* impostor.

**Narrative.** p-4 does empty_trash in CAFETERIA t0-t3 (done) and then IDLES in CAFETERIA t4-t11 (8 ticks,
`wait` actions). p-3 tasks in ADMIN, p-1 in MEDBAY. p-2* trails p-3 into ADMIN (t5), kills at t6, enters
ADMIN_VENT t7, and at t8 EXITS THE VENT INTO MEDBAY WHERE p-1 IS TASKING: `p-1 sees players=['p-2@MEDBAY:vent']
hears=[vent_use_heard MEDBAY]`. p-1 walks WEST_HALL t9 → CAFETERIA t10 → presses the emergency button t11
(the body in ADMIN is never found). Meeting: vent_sighting flag (role_proof/strong), p-1 0.95 + p-4 0.85 →
p-2* ejected → crew win.

**(a) Information.** p-1's memory: "[obs p-1:9:1] [tick 9] You witnessed p-2 vent in MEDBAY." + "You heard
a vent use in MEDBAY" + a movement line "[tick 9] p-2 entered MEDBAY" (a vent EXIT is logged as an
"entered", slightly misleading). Belief p-2 = 1.00 already before the meeting. p-4 knew nothing (idle in
CAFETERIA; last saw everyone leave at obs 1). p-2* knew p-1 saw it ("[tick 9] You saw p-1 task in MEDBAY").
**(b) Decisions.** Opening: correct and decisive, folksy voice ("get this fox out of the henhouse"), but
mis-describes the event ("I watched p-2 slip INTO a vent right HERE in Medbay" — it came OUT, and the meeting
is in CAFETERIA). p-2* reply "I was nowhere near Medbay" — flat denial, no counter-detail. p-4 opt-in gives
a true structured alibi (CAFETERIA 0-11) but its free_text says "I was busy emptying trash in the Cafeteria at
tick 9" — [VERIFIED false] the task completed at obs 4 (t3); it was idle. Ballots follow the flag; p-2*
SKIPs at conf 0.0 (impostor never counter-votes). Correct outcome for the right reason.
**(c) Sim holes.** [VERIFIED] impostor vent-exit into an occupied room (t8): the impostor could not see
MEDBAY from ADMIN (not adjacent), so the FSM vented blind — a "vent in front of witnesses" self-own that
decides the game. [VERIFIED] 8-tick idle at spawn by a done crewmate (agents/tactical/crewmate_policy.py:41-47:
no pending task → return to meeting room and wait). Body in ADMIN persisted, unfound, until game end.
**(d) Watchability.** One beat (t8), then a foregone meeting. Rewind: t8. The 8 idle ticks of p-4 are dead
weight for a spectator.

---------------------------------------------------------------------------------------------------
## Seed 41 — IMPOSTORS (parity via WRONG ejection), 10 ticks, 1 meeting (EJECTED p-4, a crewmate). p-3* impostor.

**Narrative.** p-1+p-4 go west (MEDBAY t1), p-4 continues to LABS t2 (p-1 sees the departure: "[obs
p-1:3:1] [tick 3] You saw p-4 move from MEDBAY to LABS"). p-2+p-3* go east; p-3* fake-tasks beside p-2 in
ENGINEERING t2-t3, kills p-2 at t4, vents t5, and at t6 EXITS THE VENT INTO LABS WHERE p-4 IS TASKING
(`p-4 sees players=['p-3@LABS:vent'] hears=[vent_use_heard LABS]`). p-4 abandons its LABS task at 4/8 and walks MEDBAY t7 → WEST_HALL t8 ([JUDGMENT] the button path;
its belief p-3=1.00 was set at t6) but p-1 — who abandoned its MEDBAY scan at 3/10 to walk to the inherited ENGINEERING task —
finds p-2's body at t8 and reports at t9 first. Meeting: p-1 (reporter) accuses p-4 (0.5) for the
MEDBAY→LABS move; p-4 replies with the vent sighting (conf 1.0) AND a "whereabouts tick 3 MEDBAY" roll-call
answer; the detector emits TWO strong flags — `alibi_vs_sighting` against p-4 ("Alibi places p-4 in MEDBAY
(ticks 3-3); sighting reports p-4 in LABS at tick 3") and `vent_sighting` against p-3*; p-3* says "That vent
claim is a serious fabrication" and points at the timeline slip; p-1 and p-3* vote p-4 (0.85 each), p-4
votes p-3* (1.0). p-4 ejected → 1v1 → impostor parity.

**(a) Information.** p-4's memory (seed41.prompts.txt lines 55-70): vent line, "You saw p-1 in MEDBAY [tick
2]", spawn lines. It has NO line saying where p-4 itself was at tick 3 (it was in LABS). Asked by the
template to answer "the tick in question" (tick 3) "copied from your own record", it had no record and
guessed MEDBAY — off by one — and the machine turned that into a STRONG cross-statement flag. p-1's memory:
the true MEDBAY→LABS movement of p-4, a false "You completed submit_scan" (bug B1), the body. p-3*: full
adjacent-vision picture incl. p-4's LABS→MEDBAY→WEST_HALL run toward the button.
**(b) Decisions.** The pivotal ballot: p-1's prompt (lines 440-513) shows suspicion `p-3: 0.80` and `p-4:
0.80`, both "this meeting +0.30" — [VERIFIED] the suspicion engine weighed an off-by-one whereabouts slip
EQUAL to a witnessed vent (category role_proof). The prompt says "never side with an unverified counter-
accusation over a verified flag" but gives no ordering between two verified flags. p-1 then broke the tie
toward its own opening suspect ("p-4's alibi crumbled like a stale cracker, so I'm voting them out before
they vent my patience"). p-3*'s deception was good given the tools: it did not defend, it amplified the
machine's flag against the only witness. p-4's own play was fine except the fatal roll-call guess. Wording
mismatch worth noting in the reply prompt: p-4 is asked for "ONE room, one tick, copied from your own
record" — an instruction that cannot be followed because the record has no self rows.
**(c) Sim holes.** [VERIFIED] second vent-exit-into-witness in three games (t6). [VERIFIED] the crewmate who
witnessed the vent needed 3+ ticks to reach the button and lost the race to a body report; the report then
handed the opening (and the framing) to the un-informed player. Kill in a dead-end with the only witness as
victim again.
**(d) Watchability.** The best game of the set: a witnessed vent, a race to the button, a meeting where the
truth is on the table and the crew still ejects the witness. Rewind points: t6 (vent), the p-4 reply
(whereabouts slip), the ballots. Frustrating in the good, social-deduction way — but the frustration is
caused by scaffolding (self-trail gap + flag weighting), not by the impostor.

---------------------------------------------------------------------------------------------------
## Seed 0 — IMPOSTORS (parity), 20 ticks, 1 meeting (SKIPPED). p-3* impostor.

**Narrative.** p-3* shadows p-4 to REACTOR (dead-end), kills at t5, vents REACTOR→ADMIN t6-t7, then walks
WEST_HALL→MEDBAY(t9, seen by p-2)→LABS(t10, seen by p-1). p-1 finishes analyze_specimen (t10, real), p-2
finishes submit_scan (t11, real) and returns to CAFETERIA to idle t14-t19 (six `wait` actions). p-3* SUBMITS
`kill p-1` at t11 in LABS — p-1 (lower id) moves to MEDBAY the same tick and escapes (DESIGN.md §3 "a
lower-id target's same-tick move legitimately escapes a kill"); the spectator sees nothing of this
near-miss. p-3* then stalks p-1 one room behind for 7 ticks (WEST_HALL t13, ADMIN t14, EAST_HALL t15,
ENGINEERING t16 — its memory logs every leg: "[obs p-3:17:3] You saw p-1 move from ENGINEERING to REACTOR")
while p-1 walks to the inherited REACTOR task, finds p-4's body t16, reports t17 with the killer in the
adjacent room. Meeting: p-1 accuses p-3* (0.5, "was right there with me [in Labs]"); p-3* replies "I was
simply finishing my task in LABS when p-1 left" (an impostor has no tasks; also violates its own template's
"explain nothing about your own whereabouts") and blames p-1's path to REACTOR (which it truthfully
observed); p-2 herds onto the reporter (0.65: "p-1 vanished between Medbay and the Reactor"). All SKIP. t18
p-1 resumes the REACTOR task where it stood, p-3* walks in, t19 kill → parity.

**(a) Information.** p-1 knew p-3 was in LABS at obs 11 and nothing after; p-2 knew p-3 came through MEDBAY
(obs 10-11) and p-1 came through at obs 12-13. Neither knew p-1's 5-room walk (p-1 itself cannot narrate it
— no self trail — so "unaccounted for" sticks). Ballot suspicion for p-3: 0.55 ("+0.05, no flag; carried/
soft only") — the only non-zero soft signal in the whole set of no-flag meetings I read.
**(b) Decisions.** Reasoning is thin on all sides; p-2's herding on the reporter is the classic pattern here
(seeds 29, 1, 5, 10 too). p-3*'s deception is competent (uses true observations of the reporter's route).
**(c) Sim holes.** [VERIFIED] no relocation + no cooldown reset → the meeting saves nobody (t18-19).
[VERIFIED] 6-tick idle at spawn (p-2). [VERIFIED] the invisible near-miss kill at t11. Dead time: t6-t15 is
walking/tasking with no visible event (10 ticks). p-2's task fraction drops 1.00→0.70 at t19 (p-1's tasks
re-keyed to p-2 on p-1's death, engine/tick.py:346-366) — correct rule, but for a spectator "p-2 who was
done suddenly is not done" reads as a glitch without a caption.
**(d) Watchability.** Slow. Rewind: t11 (if it were surfaced), t16-t19. The stalk (t12-t18) is genuinely
creepy IF the viewer knows roles; the crew cannot perceive it (own-room-only vision).

---------------------------------------------------------------------------------------------------
## Seed 1 — IMPOSTORS (parity), 14 ticks, 1 meeting (SKIPPED). p-4* impostor.

**Narrative.** Mirror of 29: p-4* fake-tasks beside p-3 in ENGINEERING t2-t3, kills t4, vents to LABS t6,
fake-tasks in LABS t7-t8 and, through the adjacent-room window onto MEDBAY, sees p-1 "move from MEDBAY to
WEST_HALL" (obs 7).
p-2 completes upload_logs (t7, real), walks to CAFETERIA and idles t10-t12. p-1 abandons LABS at 2/4 to walk to
the inherited ENGINEERING task, passes p-2 in ADMIN(t7)/EAST_HALL(t8), finds the body t9, reports t10.
Meeting: p-1 accuses p-2 (0.5) "moving from ADMIN to EAST_HALL at ticks 8 and 9" — the very walk p-1 made
alongside p-2 (silly). p-2 counters "you were with me in the hall a moment prior, you claim ENGINEERING at
tick 10" (adjacent rooms; not suspicious) at 0.6. p-4* opt-in: structured `alibi WEST_HALL ticks 7-10` +
`whereabouts tick 10 WEST_HALL` — [VERIFIED false]: p-4* was in LABS at obs 7-9 and MEDBAY at obs 10-11. It
built the lie from an adjacent-vision sighting ("I was chilling in West Hall, watching p-1 drift by like a
lost sock"). Nobody can check it: p-1 WAS in WEST_HALL at obs 7, alone, but p-1's memory has no "you were in
WEST_HALL at 7 and saw nobody" line, and the detector has no absence evidence. All SKIP. t11-t13 p-4* walks
to CAFETERIA and kills the idle p-2 in the hub.
**(a)/(b)** As above. Note the stock ballot phrasing: p-2 "The evidence is too thin to act on." (identical
sentence to seed-10 p-4's ballot). **(c)** [VERIFIED] kill in CAFETERIA (hub) at t13 of a crewmate idling
there since t9; no relocation; body cleared. **(d)** Low. Rewind: the p-4* opt-in lie (only visible with the
omniscient view).

---------------------------------------------------------------------------------------------------
## Seed 5 — CREWMATES (tasks), 10 ticks, 1 meeting (SKIPPED). p-1* impostor.

**Narrative.** p-2+p-4 task in ADMIN together (t2-t4); p-1* fake-tasks beside p-3 in ENGINEERING, kills t4,
vents ENGINEERING→STORAGE t5-t6, then WALKS BACK INTO ENGINEERING at t7 — the same tick p-2 (who inherited
p-3's ENGINEERING task and walked over) reports the body: `p-2 sees players=['p-1@ENGINEERING:None']
bodies=['body-p-3-4']`. Meeting: p-2's opening accuses p-4 (0.5) — its own alibi partner ("p-4 was in Admin
at tick 5. Suspicious gap.") — and never mentions p-1, whom nobody has seen since spawn. p-4 replies (0.7):
"You found the body in Engineering but you were just in Admin with me. You're lying about your timeline"
(p-2's timeline is fully consistent: ADMIN t4 → EAST_HALL t5 → ENGINEERING t6 → report t7) and adds "saw p-2
move to EAST_HALL at tick 6, potential vent path" (crewmates cannot vent). Then p-1* opt-in: "I must
correct the record, p-4; I was in Engineering with p-3 at tick 5, not in Admin" with structured
`whereabouts tick 5 ENGINEERING` + `saw_player p-3 ENGINEERING co_present [p-1]` — obs tick 5 = world t4 =
THE KILL TICK. [VERIFIED] the impostor placed itself alone with the victim in the kill room at the moment of
death. Nobody reacted: p-4 ballot alts=['p-2'] only ("my own eyes saw him tasking in Admin"), p-2 SKIP "No
hard evidence. Suspicion below threshold." — the suspicion rows for p-1 stayed 0.50 / +0.00
(seed5.prompts.txt lines 495-496, 645): a self-placement with the victim moves nothing. All SKIP. Crew wins
by tasks at t9 (3/3) — p-1* never sabotages, never gets a second kill window.
**Why the self-tell**: the impostor's opt-in prompt DOES carry the "Secret: you are the saboteur… naming a
kill you committed instantly exposes you" block (seed5.prompts.txt line 331), but the info-share RULES block
is the crew one ("Answer the roll-call: one structured whereabouts observation … copied from your own
record"), and the impostor's only self-located record line is "[tick 5] You (IMPOSTOR) killed p-3 in
ENGINEERING". The model obeyed the roll-call rule over the secret. Compare seed 1 where the same template
produced a fabricated alibi instead — a coin flip on model judgement.
**(c)** [VERIFIED] impostor returns to the body room 3 ticks after venting away (FSM cover behaviour is
pointless here); [VERIFIED] report while the killer stands in the room, and that sighting is NOT in the
reporter's memory at the meeting (last memory line is obs 7 = t6; the t7 sighting would be obs 8) — a human
reporter would open with "p-1 walked in as I found the body". [VERIFIED] no sabotage in the whole game (or in
any game of the 50-seed set: zero `sabotage` actions). Tasks: 3 total → the crew wins 2 ticks after the
meeting.
**(d)** Short and, with the omniscient view, funny (self-tell ignored). Rewind: t7 (killer walks in as the
body is reported), p-1*'s opt-in.

---------------------------------------------------------------------------------------------------
## Seed 10 — IMPOSTORS (parity), 17 ticks, 1 meeting (SKIPPED). p-4* impostor.

**Narrative.** p-3 does fix_wiring in CAFETERIA t0-t4 and then idles there t5-t16 (12 `wait` ticks — the
longest dead stretch in my set). p-4* follows p-2 EAST_HALL→ENGINEERING→REACTOR (dead-end), kills t5, vents
REACTOR→ADMIN t6-t7, and from ADMIN sees p-1 leave EAST_HALL for ENGINEERING ("[obs p-4:8:2] You saw p-1
move from EAST_HALL to ENGINEERING"). p-1 abandoned upload_logs in ADMIN at 4/6 to walk to the inherited
REACTOR task, finds the body t8, reports t9. Meeting: p-1 accuses p-4* (0.5, "last time I saw him
breathing, he was walking arm-in-arm with p-4 in the EAST_HALL" — obs tick 1, eight ticks earlier); p-4*
replies "We were just passing in the hall… You were the one heading straight to Engineering right after"
(grounded); p-3 opt-in: "p-4 is completely innocent; I saw them with p-2 in East Hall, so they couldn't have
killed anyone in Reactor… p-1 was the only one who vanished from that group" (0.6) — a non-sequitur from a
player who saw nothing after tick 1, and its structured `whereabouts tick 1 EAST_HALL` is [VERIFIED false]:
p-3 never left CAFETERIA all game (it inferred its own position from "You saw p-1 move from CAFETERIA to
EAST_HALL"). All SKIP (p-3 conf 0.58 — "Actually, the evidence is too thin to eject anyone, so I'm
skipping."). Post-meeting: p-1 stays in REACTOR tasking t10-t15; p-4* oscillates WEST_HALL(t9)→MEDBAY(t10)→
WEST_HALL(t11) then walks the long way round ADMIN→EAST_HALL→ENGINEERING→REACTOR and kills p-1 at t16 on the
very tick p-1 completes start_reactor (2/3 tasks). Parity.
**(a)** p-1's ballot prompt lists only `p-4: 0.58 (+0.08, no flag; carried/soft only)` — the +0.08 is the
"seen with victim" soft signal; p-3 not even listed. p-3's memory: three "left CAFETERIA" lines and its own
completed task; it had literally nothing and still accused at 0.6.
**(c)** [VERIFIED] 12-tick idle at spawn; [VERIFIED] impostor room oscillation t9-t11; [VERIFIED] no
relocation after meeting (p-1 keeps tasking in the room where the body lay); dead time t10-t15 (6 ticks of
one player tasking, one idling, one walking).
**(d)** Slow. Rewind: t16 (kill lands on the task-completion tick — a nice near-miss for the crew, but only if
you know tasks were 2/3 with the third one now re-keyed to the idle p-3 in CAFETERIA).

---------------------------------------------------------------------------------------------------
## Cross-game findings (ranked by severity), with the set-wide numbers that back them

Set-wide context (all 50 seeds of replays/samples/4p1i, computed from the raw JSONL): winners CREW-TASKS 23,
IMPOSTOR-PARITY 17, CREW-EJECT 10; mean length 11.6 ticks (min 4, max 26); 39 meetings, never more than 1
per game; 12 ejections = 10 right (9 on a `vent_sighting` flag, 1 on `alibi_vs_sighting`) + 2 wrong (seeds
41, 49, both on `alibi_vs_sighting`); every one of the 26 meetings WITHOUT a flag ended SKIP (13 flagged: 12 ejections + seed 24 SKIP on a lone alibi_conflict); the
impostor voted SKIP in 38/39 meetings; ZERO sabotage actions in 50 games; 11 games had no meeting at all
(4 with no kill — crew won tasks by tick 4-7; seeds 25/30: two kills, no body ever found).

1. **[VERIFIED, bug] Agents have no memory of their OWN location trail — and it costs games.** The rendered
   memory carries other players' positions and moves but never "you were in ROOM at tick N" (only inside
   completed-task suffixes). Consequences observed: seed 41 p-4 (the vent witness) guessed its tick-3 room
   wrong → STRONG `alibi_vs_sighting` flag → ejected; seed 10 p-3 hallucinated `whereabouts tick 1 EAST_HALL`
   while never leaving CAFETERIA; seed 1 p-1 could not refute p-4*'s "I was in WEST_HALL at 7 watching you"
   although p-1 was alone there; seeds 0/29/1 reporters cannot narrate their walk so "unaccounted for" sticks.
   The prompt literally instructs "copy your own record" for a row that does not exist.
2. **[VERIFIED, design/quality] The suspicion arithmetic ranks a one-tick whereabouts slip equal to a witnessed
   vent (seed 41: p-3 0.80 vs p-4 0.80, both "+0.30").** `vent_sighting` is category role_proof; it should
   dominate any cross_statement flag. Combined with (1) it produced the only wrong ejection in my set and
   turned a crew-won game into an impostor win.
3. **[VERIFIED, design] No-flag meetings cannot decide.** In every no-flag meeting I read (29, 0, 1, 5, 10) the
   ballot prompt showed suspicion 0.50 (+0.00) for all targets (max +0.08 for "seen with victim") against a
   0.60 threshold, and the prompt says "when the max sits below the threshold, SKIP is the sound call". Spoken
   accusations/corroborations move nothing (`testimony_as_content` is on, but no testimony in these games
   produced a non-zero delta). Set-wide 26/26 no-flag meetings → SKIP. The discussion is decorative; the
   game is decided by whether the impostor's FSM vents into a witness.
4. **[VERIFIED, bug] False "You completed <task>" memory lines minted on a crewmate's death.** In seeds 29, 41,
   1, 10 the reporter's memory says "[tick 5/6] You completed log_findings / submit_scan / log_findings /
   upload_logs" while its own view shows tasks 0/2 and no task_completed event exists. Mechanism: on a death,
   engine/tick.py:346-366 re-keys the victim's tasks to the LOWEST-ID living crewmate; the memory store's
   completion inference (agents/memory/store.py:1154-1195) assumes "none is added mid-game" and reads any
   change of the lexicographically-first pending id as a completion. The false line then becomes a
   `completed_task` alibi observation in the opening (seed 29/41 p-1). Side effects: the recipient's FSM
   abandons its in-progress task (2/4, 3/10, 2/4, 4/6 ticks) and beelines to the inherited task — which is in
   the room where the victim died — so in 5/5 body-report games of my set the reporter is p-1/p-2 the
   inheritor, "summoned" to the body by task redistribution.
5. **[VERIFIED, design] Meetings save nobody: no relocation to CAFETERIA and no kill-cooldown reset.** Seed 29
   the kill was submitted on the report tick and landed one tick after the meeting; seed 0 the impostor waits
   in the adjacent room and kills two ticks after; seed 10 six ticks. In a 4p1i game the meeting is therefore
   "eject the impostor now or lose", and the post-meeting phase is a foregone chase.
6. **[VERIFIED, design/FSM] The impostor vents blind and exits into occupied rooms** (seeds 2 t8, 41 t6; set-wide
   9 of the 10 correct ejections came from a `vent_sighting`). It is the crew's only real weapon and it is
   an FSM gift, not deduction.
7. **[VERIFIED, quality] The impostor's self-placement with the victim (seed 5) moved nobody** — neither the
   suspicion engine (+0.00) nor the crew voters. "Last seen alone with the victim in the kill room" is the
   strongest circumstantial fact in the genre and the machinery does not represent it.
8. **[VERIFIED, design] Impostor replies contain no self-account** (template: "explain nothing about your own
   whereabouts", observations kept empty). The accused impostor never says where it was (29, 41, 10, 2), which
   a human table would treat as a tell; the flip side is that the impostor can never be caught in a
   whereabouts lie via the flag machinery, only in the opt-in template (seed 1's fabricated WEST_HALL alibi,
   unchallengeable because of finding 1).
9. **[VERIFIED, quality] Reporter-herding and non-sequitur accusations.** Seeds 29, 0, 1, 5, 10: the second and
   third speakers accuse the reporter at 0.6-0.7 on "was near / walked toward the body" grounds; seed 5 p-2
   accuses its own alibi partner; seed 10 p-3 clears p-4* on an 8-tick-old sighting; seed 5 p-4 invents a
   "vent path" for a crewmate. Voices are lively (fox/henhouse, lost sock/noose, stale cracker) but stock
   ballot sentences repeat verbatim across games ("The evidence is too thin to act on."; "Actually, the
   evidence is too thin to eject anyone, so I'm skipping.").
10. **[VERIFIED, pacing] Dead time and idle-at-spawn.** Done crewmates walk to CAFETERIA and `wait` (seed 10:
    12 ticks; seed 2: 8; seed 0: 6; seed 1: 3) and are killed there (seed 1). Nothing else happens in a
    4p1i game between the first kill and the report (seed 0: 10 event-free ticks). No sabotage ever.
    Redistribution snapping a finished player's task bar from 1.00 to 0.70 (seed 0 t19) reads as a glitch.
11. **[VERIFIED, minor]** Report-tick sightings are not in memory at the meeting (seed 5: the killer standing
    beside the reporter; seed 29: p-4 beside p-2). Impostor memory carries ~8 "Your kill cooldown is N" lines
    (noise). Movement is rendered twice (obs line + raw "entered/left" line). A vent exit is logged as
    "p-2 entered MEDBAY". Free-text slips: "slip INTO a vent" for an exit, "right HERE in Medbay" while in
    CAFETERIA (seed 2); "busy emptying trash at tick 9" five ticks after finishing (seed 2 p-4). No scaffolding
    ids leaked into free_text/rationale in any of the 7 games; no singular/plural impostor wording issues (1
    impostor).

## Ideas that would make these simulations better

1. **Render a self-location trail** ("[tick 2-4] You were in MEDBAY; [tick 5] you moved to WEST_HALL…"), and
   let alibi/whereabouts claims cite it. Removes findings 1 and most of 9; also enables "I was in X at N and
   saw nobody" absence testimony that would have caught seed 1's lie.
2. **Order the flags**: role_proof (vent/kill witnessed) must dominate cross_statement flags in the suspicion
   fold and in the ballot prompt ("a witnessed vent outranks a timeline slip"), and treat a one-tick
   whereabouts slip as WEAK.
3. **Meeting resolution like the genre**: teleport everyone to CAFETERIA and reset kill cooldowns (or at
   least a 2-3 tick grace) so a SKIP is not a death sentence and the post-meeting phase has play.
4. **Make "last seen with the victim / entered the body room" a first-class soft signal** with a real weight
   (seed 5's self-tell, seed 29's dead witness), and add the report-tick sightings to memory before the
   meeting ("p-1 walked in as I found the body").
5. **Fix the completion inference for redistributed tasks** (compare owned-instance sets, not the pending
   pointer), and stop the FSM from abandoning an in-progress task for a newly inherited one; consider
   distributing dead tasks round-robin instead of lowest-id so p-1 is not always the summoned reporter.
6. **Impostor FSM: peek before venting out** (adjacent-room vision exists) and vary cover; **crew FSM: after
   tasks, patrol/buddy** rather than `wait` in CAFETERIA (also gives the done crewmate something to testify
   about).
7. **Let the impostor give a (lying) self-account in replies** so the flag machinery has something to catch,
   and give crew testimony a non-zero fold so a no-flag meeting can at least converge on a leader.
8. **4p1i format**: with 3 tasks the crew wins in 4-9 ticks and with one kill the meeting is all-or-nothing;
   either 2 tasks per crewmate or a lights sabotage that actually fires would create a second act.
