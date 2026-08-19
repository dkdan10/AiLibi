# w1-9p2i-featured-a — spectator review of replays/samples/9p2i seeds 2, 17, 0, 1, 3

Method: watched every game with `watch.py` (seeds 2 and 17 with `--verbose`), dumped rendered
memories + beliefs + full LLM prompts/responses with a small ReplayLoader script
(`scratchpad/work/w1-9p2i-featured-a/mem.py`), and re-walked engine state (tasks, cooldowns,
rejected actions, in-vent, post-meeting rooms) with `state.py` in the same dir. Source code was
opened only to explain observed behaviour; file:line cited where it was.

Tick convention (important for reading every citation below): `watch.py [tN]` is the world
state AFTER raw tick N's actions. The agents' memory/transcript ticks are N+1 (the packet
delivered after tick N is stamped N+1). So "vent at tick 11" in a meeting = world `[t10]`.
I write world ticks as `t10` and agent-side ticks as `mem 11`.

Roster facts verified from the map (`engine/maps/canonical_1.yaml`): kill cooldown 4 ticks;
crew visibility is SAME ROOM ONLY, impostors see room + adjacent rooms
(`engine/visibility.py:104-127`, "asymmetric visibility"); emergency button 1 use/player;
dead crewmates' tasks are REDISTRIBUTED to living crew (`dead_task_rule: redistribute`).

---------------------------------------------------------------------------------------------
## GAME 1 — seed 2 (CREWMATES win, CREWMATE_EJECT, 36 ticks, 4 meetings) — hand-featured
Roster: impostors p-4*, p-7*. Memory watched: p-1 & p-3 & p-9 (crew voters), p-4* & p-7*.

### Narrative
- Act 1 (t0–t7). Everyone leaves CAFETERIA except p-2 (empty_trash) and p-7* who idles next
  to her faking a task for 4 ticks (raw actions t0–t3 `p-7 do_task empty_trash`, all
  engine-rejected "actor owns no task instance"). The moment cooldown expires p-7* kills p-2
  in the hub (t4). p-4* (partner, in EAST_HALL, adjacent-vision) sees the body at t4 and never
  reports. p-1 abandons a half-done submit_scan in MEDBAY at t5 (see redistribution bug
  below), walks to CAFETERIA, sees the body t6, reports t7. p-7* stands in EAST_HALL next door
  watching p-1 report (t6–t7 `p-7* sees players=['p-1@CAFETERIA'] bodies=['body-p-2-4']`).
- Meeting 0 (t7). p-1 opens: "p-4 was standing right there at the start and hasn't said a
  peep since" (nonsense). p-4* deflects onto its own partner: "Might we ask p-7 why they were
  lingering alone in East Hall at tick 6". The crew (p-3, p-5) run with the impostor's hint.
  p-7* volunteers "I was in the Cafeteria with p-2 right before they died" (obs
  `saw_player tick 5 p-2 CAFETERIA`, no co-present) — i.e. the killer admits being alone with
  the victim at the kill tick — and nobody uses it. 2 votes p-7, 6 SKIP. Outcome SKIPPED.
- Act 2 (t8–t14). No teleport after the meeting: p-4* is still in STORAGE with p-6 and kills
  her at t8, ONE tick after the meeting (its kill was already queued at raw tick 7 and pre-empted
  by the report). p-4* vents STORAGE→ENGINEERING (t9–t10) and pops out in front of p-8, who is
  doing align_engine_output (`p-8 sees players=['p-4@ENGINEERING:vent'] hears=[vent_use_heard]`).
  Same tick p-7* kills p-1 in CAFETERIA (t10, second hub kill, again unwitnessed). p-3
  abandons log_findings in LABS at 3/4 progress at t11 (redistribution bug again), walks to
  CAFETERIA, finds p-1, reports t14. Bodies: p-2's was cleared at meeting 0; p-6's in
  STORAGE is NOT (unreported).
- Meeting 1 (t14). p-8: "I... I might be wrong, but I distinctly recall seeing p-4 vent in
  Engineering at tick 11". Contradiction engine: `[vent_sighting/strong] ... matches the
  witness's own record`. 4 votes p-4, impostors SKIP (p-7*'s recorded rationale: "p-4 is my
  partner. I can't vote him out."). p-4* ejected. Correct.
- Act 3 (t15–t19). p-7* kills p-5 in REACTOR t17 (p-5 was 8 ticks into a 10-tick
  start_reactor, alone in the dead-end). p-7* enters REACTOR_VENT t18. p-3 finds p-6's
  9-tick-old body in STORAGE at t18, reports t19 — while p-7* is INSIDE A VENT during the
  meeting (`[t19] p-7*@REACTOR:VENT(VENTING)`, state walk `invent=['p-7']`).
- Meeting 2 (t19). About a body killed by the already-ejected p-4. p-8 and p-9 re-litigate
  p-4's vent, both leaking `[invalid accusation target 'p-4' dropped]` into their spoken
  free_text. SKIP.
- Act 4 (t20–t35). p-7* exits the vent into STORAGE at t20 directly in front of p-3
  (`p-3 sees players=['p-7@STORAGE:vent'] hears=[vent_use_heard]`). p-3's belief in p-7 goes
  to 1.00 — and p-3 does NOT press the emergency button; it finishes fuel_reserves, then walks
  a 12-room loop ENGINEERING→EAST_HALL→ADMIN→WEST_HALL→MEDBAY→LABS (log_findings t28)
  →MEDBAY→WEST_HALL→ADMIN→EAST_HALL→ENGINEERING→REACTOR to do start_reactor (inherited from
  p-5), while p-8 and p-9 idle in CAFETERIA t25–t35 (10 ticks). p-7* follows p-3 around the
  map one room behind for 15 ticks (t20–t34, always seeing p-3 in the room it just left) and
  attempts exactly ONE kill (raw t30, engine `kill requires same room` — p-3 had already moved).
  A single kill would have been 2v1 = impostor parity win. p-3 finally walks into REACTOR at
  t34, sees p-5's 17-tick-old body, reports t35.
- Meeting 3 (t35). p-3: "I saw p-7 vent in STORAGE at tick 21 — that is the kill" (a vent
  it had been sitting on for 15 ticks). Verified flag, 3–0, p-7* ejected. Crew win.

### (a) Information gathering
- [VERIFIED] Rendered memory is rich in raw sightings and thin in synthesis. p-3's memory at
  meeting 3 is ~90 lines: co-presence sightings, "You saw p-7 move from EAST_HALL to
  ENGINEERING" (movement_perception), heard cues, "[meeting] CLAIM by p-7 (unverified):
  accused p-3" lines for spoken testimony, and a beliefs block. Testimony DOES enter memory,
  but only as structured claim stubs (accused / backed / saw X in Y). The one thing that
  matters most — "p-8 said he SAW p-4 VENT" — is rendered to p-9 merely as
  "[tick 15] [meeting] CLAIM by p-8 (unverified): accused p-4" (p-9's memory, meeting 3).
  The vent content of testimony is dropped.
- [VERIFIED — bug] Memory mints FALSE "You completed <task>" lines when a dead crewmate's
  task is redistributed. p-1 at meeting 0: `[obs p-1:5:0] [tick 5] You completed submit_scan
  (you were in MEDBAY)`; engine state: p-1's submit_scan was 3/10 and never completed; what
  happened at t4 is p-2 died and her `fix_wiring_cafeteria` (1/5) was re-keyed to p-1
  (state walk: p-1's task list grows from 2 to 3 at t4). The renderer infers completion from
  "pending_task_id changed" under the assumption the owned set only shrinks
  (`agents/memory/store.py:1156-1163`), which `dead_task_rule: redistribute` violates. Same
  bug: p-3's memory at meeting 3 has "You completed log_findings" TWICE (`[tick 11]` and
  `[tick 29]`; only the second is real). p-1's speech at meeting 0 then rests on it: "I was
  busy with my scans in Medbay". Seed 1 shows the worst form: p-1's AgentMemoryView says
  `tasks 0/5` while its rendered memory says "[tick 6] You completed log_findings".
- [VERIFIED] The same redistribution mechanic silently re-routes crew mid-task to the DEAD
  player's task room — usually the murder room. p-1 dropped submit_scan at 3/10 to go do
  p-2's cafeteria wiring (found p-2), p-3 dropped log_findings at 3/4 to go do p-1's cafeteria
  wiring (found p-1), p-3 later inherited p-6's fuel_reserves (found p-6) and p-5's
  start_reactor (found p-5). Four of four bodies in this game were found by the crewmate who
  inherited the victim's task. Great for pacing, but as a mechanic it makes "who found the
  body" a function of the alphabet, not of play, and it forces visible task abandonment
  (spectator sees a crewmate walk away from a half-done task for no reason).
- [VERIFIED] The FSM does tasks in alphabetical order of task id (pending =
  lexicographically-first unfinished task, `observation/service.py:645-650`, consumed at
  `agents/tactical/crewmate_policy.py:414`). That is why p-3 at t22 walked from ENGINEERING
  past the adjacent REACTOR (start_reactor) all the way to LABS (log_findings) and back —
  12 rooms of pure transit — while the impostor trailed it.
- [VERIFIED] Voter knowledge at the decisive votes was minimal but correct: meeting 1 —
  only p-8 had first-hand knowledge (the vent); p-3/p-5/p-9 voted p-4 purely on p-8's word +
  the "VERIFIED" flag. Meeting 3 — only p-3 had first-hand knowledge; p-9 "corroborated" with
  a FABRICATED sighting: turn 3 obs `saw_player tick 21 subject p-7 room STORAGE` — p-9's
  rendered memory has no such line (p-9 was in ADMIN; crew cannot see other rooms). The
  model turned p-3's testimony into its own eyewitness claim. Hallucinated corroboration.
- [VERIFIED] Things a human would know that agents don't: (1) who else was standing at the
  body / where everyone was when the meeting was called (no arrival-time or "last room"
  roll-call is provided by the engine; each agent only knows its own same-room sightings);
  (2) that p-7 admitted being alone with p-2 at the kill tick (meeting 0) — the transcript
  shows it, no one connects it; (3) that p-4 SAW p-2's body at t4 (p-4's meeting-1 obs
  `found_body tick 12 body_of p-1` — the impostor even puts on record that it saw p-1's body
  before p-3 reported it) and never reported — nobody asks why.
- [JUDGMENT] "Most salient first" ordering + dozens of "You saw p-9 in CAFETERIA (with p-8)"
  idle repeats (seed 17 p-8 has 30 such lines) make the memory hard to read even for me; the
  27B model demonstrably misreads it (see seed 17).

### (b) Decisions / accusations / votes
- Opening reports: p-1's meeting-0 opening accuses p-4 with the reason "hasn't said a peep"
  (fabricated grievance); p-3's openings are formulaic "I found X dead in Y at tick N. Where
  were you at tick M?" but usable.
- Accusations grounded? Meeting 0: crew accusations of p-7 were grounded ONLY in p-4*'s
  hint ("lingering alone in East Hall"), i.e. hearsay from an impostor; p-5 then repeated it
  as if it were his own observation ("p-7 was isolated in East Hall at tick 6", his obs list
  contains no p-7 sighting). p-6's alibi claim `1..7 ENGINEERING` is false (she was in
  STORAGE from t2; her own memory says so) — crewmates misstate their own alibis.
- Replies: p-7*'s reply to being accused ("Your timeline is garbage. You were in Labs at
  tick 11 and suddenly near the Cafeteria at tick 14? Explain that gap") does not answer
  the question asked of it (where were you between 6 and 14) — replies are almost always
  counter-accusations, never answers. p-4*'s meeting-1 reply cites `whereabouts tick 13
  EAST_HALL` (false; ENGINEERING at world t12) — a lie, fine for an impostor.
- Ballots: follow the flag when there is one (4–0 and 3–0 on the vent flags), otherwise mass
  SKIP with template-like rationales ("The evidence is too thin"). Only p-1 and p-5 voted on
  the meeting-0 hunch. Herding is total once a flag exists.
- Impostor deception: p-4* busses p-7 in meeting 0 (design says "never incriminate" the
  partner). p-7*'s "I was in the Cafeteria with p-2 right before they died" is a self-tell.
  Recorded (non-visible) rationales state the role outright: p-7* m1 "p-4 is my partner",
  m3 "I am the impostor. I cannot vote myself". No coordination between the two.
- Hallucinations: p-9's fabricated `saw_player p-7 STORAGE tick 21` (above); p-1's
  "my scans" alibi rests on a false memory line (substrate, not model).
- Scaffolding leaks: `[invalid accusation target 'p-4' dropped]` inside spoken free_text
  three times (m2 p-8, m2 p-9, m3 p-8). Wording: the persona/ballot prompt says "a hidden
  impostor kills crewmates" (singular) in a 2-impostor game (verified in the seed-17 prompt
  dumps; same template).
- Outcome: both ejections correct, both driven purely by first-hand vent sightings.

### (c) Holes / glitches
- [VERIFIED] No teleport to CAFETERIA after a meeting (state walk: post-meeting-0 rooms
  `p-4: STORAGE, p-6: STORAGE, p-7: EAST_HALL, ...`). Consequences seen: kill 1 tick after a
  meeting on the person you were standing next to (t8), an impostor attending meeting 2 from
  inside a vent and exiting next to the reporter (t19→t20).
- [VERIFIED] Reported bodies are cleared at meeting resolution; UNREPORTED bodies persist
  across meetings (body-p-6-8 survived meeting 1; body-p-5-17 sat 18 ticks). A body cannot be
  reported twice (cleared).
- [VERIFIED] Report lag: every reporter sees the body one tick and reports the next
  (t6→t7, t13→t14, t18→t19, t34→t35).
- [VERIFIED] Two hub kills (t4, t10) — the FSM impostor kills wherever the target is alone.
- [VERIFIED] Impostor lag-chase: p-7* trailed p-3 one room behind for 15 ticks; its one
  kill attempt was rejected because the target moved the same tick. Kills only land on
  stationary (tasking/idle) targets.
- [VERIFIED] Emergency button never pressed despite a first-hand vent (belief 1.00 for 15
  ticks). Cause (code): the button fires only on a FRESH below→above-0.6 crossing after the
  last meeting; p-3's suspicion of p-7 was already ≈0.6 at meeting 2 (voted p-7 at 0.72),
  so the vent at t20 raised it 0.6→1.0 without a "crossing"
  (`agents/tactical/crewmate_policy.py:158-166, 224-260`).
- [VERIFIED] Dead time: t21–t34 = 14 ticks with 3 task completions and no other event;
  p-8/p-9 idle in CAFETERIA 10 ticks.
- [VERIFIED] Rejected kill at the meeting tick: p-4*'s `kill p-6` was submitted at raw
  tick 7 (same tick as p-1's report) and pre-empted, then re-issued at t8.

### (d) Watchability
Rewind moments: t4 hub kill next to the fake-tasker; t10 p-4 popping out of a vent in
front of p-8; t19–t20 impostor voting from inside a vent then surfacing beside the reporter;
p-7 shadowing p-3 across the whole map t24–t34 while the win is one kill away. Boring:
meeting 2 (re-litigating an ejected player), the 14-tick tail, mass-SKIP ballots.

---------------------------------------------------------------------------------------------
## GAME 2 — seed 17 (CREWMATES win, 62 ticks, 5 meetings) — hand-featured
Roster: impostors p-2*, p-4*. Truthful vent witness = p-1 (meeting 0). Memory watched:
p-1 (witness), p-4* and p-2* (impostors), p-7, p-8, p-9.

### Narrative
- Act 1 (t0–t6). p-2* kills p-3 in ENGINEERING at t4 (p-3 was 2 ticks into
  align_engine_output). p-4* in EAST_HALL sees the body next door at t4 (adjacent vision),
  says nothing. p-1's memory mints "[tick 5] You completed swipe_card" (false — p-3's
  align_engine_output was redistributed to p-1), p-1 walks to ENGINEERING and at t5 sees
  p-2* enter the vent (`p-1 sees players=['p-2@ENGINEERING:vent'] bodies=['body-p-3-4']`),
  reports at t6 while p-2* is still in the vent.
- Meeting 0 (t6) — THE WRONG EJECTION. p-1 opens truthfully: "I saw p-2 vent right there
  at tick 6" (structured saw_vent, engine-verified `matches the witness's own record`).
  p-2* replies with a lie ("you were with me in East Hall at tick 5"). p-4* (partner) piles
  on with a fabricated sighting `saw_player tick 6 p-1 EAST_HALL` — p-4*'s own memory says
  "[tick 6] You saw p-1 move from EAST_HALL to ENGINEERING" and p-4* itself was in CAFETERIA
  at mem 6 (its `whereabouts tick 6 EAST_HALL` is a second lie). Then crewmate p-7 says
  "at tick 6, we all moved to East Hall, proving p-1 was nowhere near Engineering" and emits
  `saw_player tick 6 p-1 EAST_HALL` — p-7's own memory line is "[tick 6] You saw p-1 move
  from EAST_HALL to ENGINEERING": p-7 misread the transition sentence and turned an
  observation that CORROBORATES p-1 into one that convicts him. Crewmate p-9 does the same
  off-by-one ("I was right there in the Cafeteria with you at tick 4 and 5" — her memory:
  "[tick 5] You saw p-1 in EAST_HALL (with p-4) (moved from CAFETERIA...)"). The
  contradiction engine then produces TWO `[alibi_vs_sighting/strong]` flags against p-1
  (built from p-4*'s lie and p-7's misreading) next to the ONE `[vent_sighting/strong]` flag
  against p-2. The ballot prompt tells voters every flag "is VERIFIED evidence ... it tells
  you whose account broke". p-8's own suspicion table read p-2 0.80 > p-1 0.75, and p-8 still
  voted p-1: "This verified contradiction proves p-1 is lying." Final 7–1, p-1 (crew, the
  only witness) ejected. The system's own annotation distinguished the two flag classes
  (the vent flag "matches the witness's own record"; the sighting flags are just two claims
  in tension) but nothing in the prompt tells voters that a self-record-verified vent
  outranks two unverified counter-sightings.
- Act 2 (t7–t15). p-2* exits the vent into STORAGE. p-4* kills p-7 in STORAGE t10, vents
  to ENGINEERING and exits at t12 in front of p-5 AND p-2*. p-5's suspicion crosses the gate
  → p-5 walks to CAFETERIA and presses the button at t15 (one of 19 emergency calls in the
  50-game set; the mechanic works when the crossing is fresh).
- Meeting 1 (t15, emergency). p-5: "I saw p-4 drop into a vent" (it was an exit; memory
  says only "witnessed p-4 vent"). p-2* BUSSES its partner in free text: "I swear I saw p-4
  drop into the vent... it's definitely p-4" — then SKIPs with rationale "they're my
  partner". Cause: p-2*'s memory contains "You witnessed p-4 vent in ENGINEERING" and the
  impostor prompt carries the crew rule verbatim: "A witnessed vent outranks everything else
  you hold — speak it FIRST... ALWAYS put it on the record" four lines after "never accuse or
  incriminate [p-4]" (prompt dump, seed 17 m1 p-2). p-4* ejected 4–0.
- Act 3 (t16–t44). 25 ticks of nothing: p-9 idles in CAFETERIA t12–t41 (30 ticks), p-6/p-8
  join at t26. p-2* stands in ENGINEERING doing fake tasks t15–t23 while p-5 does
  align_engine_output ALONE beside it for 5 ticks (t18–t22) with cooldown 0 — no kill.
  Then p-2* ping-pongs EAST_HALL↔ENGINEERING t24–t40 (17 ticks) while p-5 does fuel_reserves
  alone in dead-end STORAGE t29–t33 with p-2* watching from next door ("You saw p-5 task in
  STORAGE" ×5 in p-2*'s memory) — no kill. Cause (code + memory): the impostor's target
  ranking never removes EJECTED players (`_confirmed_dead_from_bodies`, bodies only,
  `agents/tactical/impostor_policy.py:813-838`); p-2*'s best-scoring target was p-1 —
  ejected at t6 — last seen alone in ENGINEERING ("p-1: last seen in ENGINEERING at tick 6"
  in p-2*'s belief block, meeting 3), so the FSM parked in ENGINEERING waiting for a ghost
  until the sighting aged out of the 30-tick window. Meeting 2 (t28, p-5 reports p-7's
  18-tick-old body): pure re-litigation of the ejected p-4's vent, five SKIPs.
- Act 4 (t41–t61). The FSM sabotage lever finally works as drama: reactor sabotage at t41,
  three idle crew sprint from CAFETERIA to ENGINEERING and repair at t44 (`SabotageRepaired`
  by p-9), p-5 routes via ADMIN and p-2* follows and kills her there at t44, vents
  ADMIN→REACTOR. p-6 walks back through ADMIN, finds p-5, reports t47.
- Meeting 3 (t47). p-8/p-9 accuse the REPORTER p-6 for "vanishing between tick 44 and 47"
  (p-8's memory: p-6 was with p-8 and p-9 in ENGINEERING at 44–45; p-6 simply left first).
  Nobody performs the elimination a human does instantly: four alive, three of us were
  together fixing the reactor when p-5 died, therefore p-2. p-6 names p-2 at 0.55 only
  "for lack of a verified alibi". SKIP.
- t51 second sabotage, same choreography; p-6 goes back to ADMIN for swipe_card, p-2* follows
  and kills her at t58; p-8 finds the body t60, reports t61.
- Meeting 4 (t61, 3 alive). p-8: "p-2 moving into ADMIN at tick 53, placing them in the room
  alone for eight ticks" — false (p-2* was in ENGINEERING with p-8 at t54), p-2*'s reply "I
  was just passing through ADMIN at tick 53" is TRUE, but 2–0 ejects p-2*. Right verdict,
  wrong reasoning, no verified flag needed at 3 players.

### (a) Information gathering (seed 17 specifics)
- [VERIFIED] The truthful witness had exactly what he needed: memory "[obs p-1:6:1] You
  witnessed p-2 vent in ENGINEERING" + heard cue; his structured saw_vent was engine-verified.
  It lost to two unverified sightings that were labelled with the same word, VERIFIED.
- [VERIFIED] The transition rendering "You saw X move from A to B" is misread as "X was in
  A" by the 27B model (p-7, and p-9's "(moved from CAFETERIA...)" parenthetical). This is the
  proximate cause of both false flags against p-1.
- [VERIFIED] Sabotage is in memory only as "You heard a sabotage alarm" ×3; the joint repair
  ("you and p-6, p-9 repaired the reactor in ENGINEERING at tick 45") is not rendered — the
  strongest alibi cluster in the game is invisible to the agents that formed it.
- [VERIFIED] The impostor knows and says it saw the body before the reporter (p-4* meeting 0
  obs `found_body tick 5 body_of p-3`) — free information the crew never uses.

### (b) Decisions (seed 17 specifics)
- Wrong ejection of the only witness on 7–1 is the single worst outcome in the five games;
  cause chain = memory-phrasing misread (crew) + fabricated sighting (impostor) + prompt
  labels all flags "VERIFIED" without ranking + herd (p-8 voted against its own numbers).
- Impostor coordination is negative: p-2* busses p-4* on prompt instruction; p-4*'s
  meeting-0 lie was the best impostor play in the set (and it worked).
- Reporter-blaming is habitual: m3 both crew accuse the reporter despite the prompt's
  "self-report is weakly exculpatory" paragraph.
- Wording/persona: p-2*'s voice ("I'm just so nervous...") produces 60-word run-ons; p-6's
  "I must respectfully..." register is fine; p-9's "Where were you at tick 8? Why...?"
  interrogative voice never states an observation. Recorded rationales: "I know I'm the
  killer so I can't vote myself" (p-2*, m4).

### (c) Holes / glitches (seed 17)
- [VERIFIED] Impostor paralysis 25+ ticks from ghost-targeting an ejected player (above).
- [VERIFIED] Vent exits land in front of witnesses: p-4* exits into ENGINEERING with p-5 +
  p-2 present (t12); the exit choice avoids only rooms with a visible BODY, not visible
  players (`impostor_policy.py` VENT_EXIT docstring "a connected vent whose room holds no
  visible body").
- [VERIFIED] Reporter reports while the killer is in the same room (t6: p-2* in the
  ENGINEERING vent during the report; meeting 0 opens with the impostor sitting in a vent).
- [VERIFIED] Idle streaks: p-9 30 ticks; p-6/p-8 15 ticks; two separate 12-tick stretches
  with no event but fake tasks and ping-pong.
- [VERIFIED] The dead p-7's body sat in STORAGE t10–t28 (18 ticks) two doors from the hub;
  the meeting it finally triggered was about a kill by an already-ejected impostor.
- [VERIFIED] Sabotage-during-meeting is fine (t26 in seed 3), but the sabotage kills here
  were only possible because the crew idle in CAFETERIA — the lever works BECAUSE of the
  idle-in-hub behaviour.

### (d) Watchability
Meeting 0 is genuinely dramatic (a truthful witness lynched by a lie + a misread) — a human
would rewind to t5 to check who saw what. Sabotage-split kills t41–t44 and t51–t58 are the
best "impostor play" moments in the set. Everything between t16 and t40 is unwatchable.

---------------------------------------------------------------------------------------------
## GAME 3 — seed 0 (CREWMATES win, 24 ticks, 3 meetings)
Impostors p-6*, p-8*.
- p-8* idles in CAFETERIA t0–t4 beside p-4 (common task) — "loitering at spawn" is the
  standard opening for one impostor in 4 of 5 games; the kill lands only if the target is
  still alone at t4 (here p-4 left at t4, no kill).
- p-6* kills p-2 in STORAGE t5, vents to ENGINEERING and exits at t7 in front of p-5 who is
  tasking there. p-5's suspicion crosses → button at t10 (emergency #2 in my set). p-3 adds a
  real deduction: "p-6 in Engineering at tick 5 and Admin at tick 10 with no intermediate
  movement" (a teleport inference — one of the few non-vent inferences in 5 games; note it is
  wrong on the map: ENGINEERING→ADMIN is 2 hops, easily walked in 5 ticks). p-8* (partner)
  even says "Eject p-6" then SKIPs. p-6* ejected 6–0.
- Meeting 1 (t17): p-1 reports p-2's 12-tick-old body (killed by the ejected p-6). Whole
  meeting re-litigates p-6 with three `[invalid accusation target 'p-6' dropped]` husks.
  p-8* claims `whereabouts 17 STORAGE` + `found_body` (it was in ENGINEERING next door;
  another "I found the body but didn't report" self-tell) and accuses the reporter. p-9 asks
  p-1 to explain travelling MEDBAY→STORAGE in 4 ticks (it is exactly 4 hops). SKIP.
- p-8* walks into STORAGE t18 where p-1 is now doing the inherited fuel_reserves and kills him
  at t19 in the room where the last body was found, vents to ENGINEERING and exits in front
  of p-3 (t21). p-3 came that way because p-1's tasks were redistributed to it (tp 1.00→0.36
  at t19) — third game where the inheritor walks to the body. Meeting 2: 5–0, p-8* ejected.
- Notable: crew p-3, p-4, p-7 idle in CAFETERIA t13–t23; p-8* wanders EAST_HALL/CAFETERIA
  t11–t16 unable to kill (co-present); vent exits again into the busiest room.

---------------------------------------------------------------------------------------------
## GAME 4 — seed 1 (CREWMATES win, 13 ticks, 2 meetings) — the shortest, and the best game
Impostors p-6*, p-7*.
- t5 p-6* kills p-3 in STORAGE, vents, exits into ENGINEERING in front of p-2 (t7). t7 p-7*
  kills p-4 in ADMIN at the very tick p-8 walks in (KilledEvent witnesses=() — entering the
  room on the kill tick does not witness). p-8 reports t8: "p-7 walked in right at tick 8,
  same time I did. You were there when the body was fresh." — a correct, human-like report.
- Meeting 0: p-7* lies ("I was in EAST_HALL at tick 7 and only entered ADMIN at tick 8" —
  it entered at world t6); crewmate p-1 attacks the reporter ("classic deflection tactic");
  p-2's verified vent on p-6 decides it, 6–1, p-6* ejected. Side flag: `alibi_vs_sighting`
  against crewmate p-1 because p-1 answered the roll-call with LABS at mem 8 while it was in
  WEST_HALL — p-1's memory contains NO line about its own position at ticks 7–8 (it walked
  alone; nothing rendered), so the prompt's "copy your whereabouts from your record" was
  impossible to satisfy and the guess produced a strong flag against an innocent.
- Meeting 1 (t12): p-7* lies again ("ADMIN from tick 8 through tick 12"), p-8's honest
  sighting "p-7 in EAST_HALL at tick 9" breaks it → `alibi_vs_sighting/strong` on p-7 →
  5–0 ejection. This is the deduction loop working as designed: impostor over-claims an
  alibi, one honest sighting breaks it, flag, eject.
- Glitches: three husks; p-1's opening accuses p-2 for being "alone in Engineering"; p-9's
  turn is four questions and zero observations.

---------------------------------------------------------------------------------------------
## GAME 5 — seed 3 (CREWMATES win, 27 ticks, 2 meetings)
Impostors p-2*, p-6*.
- t8 p-2* kills p-3 in ENGINEERING; partner p-6* is also there and at t9 BOTH impostors vent
  out of ENGINEERING_VENT (the COVER branch fires on any visible body in the room, including
  the partner's kill). p-2* exits into LABS in front of p-9 (t10), p-6* into STORAGE in front
  of p-5 (t10). Both impostors burned by one kill.
- Meeting 0 (t12): TWO verified vent flags (p-6 by p-5, p-2 by p-9). The crew ejects p-6 6–1
  and dismisses p-9's equally verified flag: p-1 "I'll trust that plain sight over p-9's
  later claim", p-7 "p-9's claim against p-2 lacks corroboration and contradicts my own alibi
  for p-2" (his "alibi" is a sighting of p-2 five ticks earlier). Singular-impostor framing
  ("a hidden impostor") in the prompt + no rule for two simultaneous flags.
- t13–t21: nobody presses the button on the known second impostor (p-9's suspicion of p-2 was
  already 1.0 → no fresh crossing; everyone else's stayed under 0.6). Five crew idle in
  CAFETERIA t19–t26. p-2* kills p-1 in LABS at t22 (on the tick p-1's analyze_specimen
  completes), vents, sabotages at t25, p-4 (task inheritor again) finds p-1 at t26.
- Meeting 1: p-4's opening accuses p-9 for having been in LABS with p-1 "way back at tick 3"
  (23 ticks earlier). p-2*: "Liar. You're fabricating that vent... Vote p-9." p-9's held
  vent (15 ticks old) is put on the record again, flag, 5–0. One avoidable death and 14
  ticks lost to not acting on a verified flag.

---------------------------------------------------------------------------------------------
## CROSS-GAME: recurring patterns

1. 11 ejections in 5 games: 8 on a first-hand vent flag, 1 on an alibi-vs-sighting break
   (s1 p-7), 1 on a movement hunch in a 3-player endgame (s17 p-2), 1 WRONG on a lie plus a
   misread (s17 p-1). No ejection came from co-presence/elimination reasoning. Every meeting
   without a flag ended in a SKIP plurality (s2 m0/m2, s17 m2/m3, s0 m1).
2. Impostor detection is almost entirely the impostor's own vent use in front of a tasker:
   8 of the 11 vent uses were witnessed (7 at the exit room, 1 at entry), 5 of the 7
   witnessed exits were into ENGINEERING. The FSM's vent-exit chooses by body-absence and
   alphabet, not by player-absence.
3. Redistribution of dead crew's tasks (a) mints false "You completed" memories, (b) forces
   mid-task abandonment, (c) routes the inheritor to the corpse: of the 14 body reports in
   these games at least 9 were made by the crewmate who had just inherited the victim's task
   (verified by tp drop / pending change: s2 all four, s17 p-1 and p-8, s0 both, s3 p-4).
4. Idle-in-hub: finished crew stand in CAFETERIA for 10–30 ticks; the impostor cannot kill a
   group; games stall until a task-doer is alone or a sabotage splits the group.
5. Re-litigating an ejected impostor's vent (prompt-mandated "ALWAYS put it on the record")
   produces the `[invalid accusation target 'p-N' dropped]` husk 9 times in 5 games and
   whole meetings with no content (s0 m1, s2 m2, s17 m2).
6. Reporter-blaming by crew in 4 of 5 games despite the exculpation paragraph.
7. Impostor rationales state their role; impostors bus partners in speech under the
   vent-first rule; the persona says "a hidden impostor" (singular).
8. Kills: first kill at t4–t8 in every game (cooldown 4 from spawn); hub kills in seed 2;
   kills only on stationary targets (1-tick decision lag); 42/225 rejected on same-room.

## Ranked findings (severity ↓)

1. [VERIFIED, glitch] Unverified counter-sightings are presented to voters as "VERIFIED
   evidence" on par with an engine-verified vent; a lying impostor plus one crew misread
   ejected the only truthful witness 7–1 (seed 17 m0). Prompt/contradiction-engine design.
2. [VERIFIED, bug] Memory mints false "You completed <task>" lines whenever a dead player's
   task is redistributed (`agents/memory/store.py:1156-1163` vs `dead_task_rule: redistribute`);
   seen in seeds 2 (p-1, p-3 twice), 17 (p-1), 1 (p-1 with tasks 0/5). Fabricated alibi source.
3. [VERIFIED, bug] Impostor FSM stalks ejected players (bodies-only dead set,
   `impostor_policy.py:813-838`); seed 17 p-2* wasted ~25 ticks and passed on 10+ ticks of
   a lone target 1 room away. Explains part of the ping-pong/idle disclosures.
4. [VERIFIED, design] "You saw X move from A to B" / "(moved from A ...)" is misread by the
   model as "X in A" → false sightings → false strong flags (seed 17 p-7, p-9).
5. [VERIFIED, design] Post-meeting positions are not reset: kill 1 tick after a meeting on
   the person you were beside (s2 t8), meeting attended from inside a vent (s2 t19, s17 t6),
   vent-exit onto the reporter (s2 t20).
6. [VERIFIED, design] Emergency button needs a "fresh crossing": a first-hand vent (belief
   1.0) never triggers a call if suspicion was already ≥0.6 (s2 p-3 15 ticks, s3 p-9 14
   ticks); a known impostor walks free until it kills again.
7. [VERIFIED, prompt] Impostor prompt contains the crew's "ALWAYS report a witnessed vent"
   rule → partner bussing (s17 m1); the same rule for crew → 9 husks + 3 empty meetings.
8. [VERIFIED, design] Crew have no rendered record of their own location when alone → the
   roll-call "whereabouts" is guessed → strong flags against innocents (s1 p-1).
9. [VERIFIED, quality] Hallucinated corroboration: p-9 (s2 m3) invents an eyewitness sighting
   from another player's testimony; p-8 (s17 m4) invents "alone in ADMIN eight ticks".
10. [JUDGMENT] Two verified flags in one meeting (s3 m0): no protocol → the second impostor
   is ignored, then idles a known killer for 14 ticks and loses a crewmate.

## Ideas (concrete)

1. Rank flags: render engine-verified observations ("matches the witness's own record") in
   a separate "CONFIRMED" bucket and claim-vs-claim tensions as "DISPUTED"; tell voters a
   confirmed vent beats any number of disputed sightings; verify sightings against the
   speaker's memory too (p-4*'s `saw_player p-1 EAST_HALL tick 6` was not in its record —
   flag it as unsupported).
2. Fix the completed-task inference: derive completions from the engine's TaskCompleted
   event / owned-set shrink, not from pending-id change; render redistribution explicitly
   ("[tick 5] You picked up p-2's fix_wiring_cafeteria") so the crew can even reason "the
   task inheritor found the body".
3. Impostor FSM: build `confirmed_dead` from meeting-end dead rosters (ejections + announced
   deaths) not just seen bodies; choose vent exits by "no visible player in the destination
   room" (the impostor can see adjacent rooms from the vent room); do not COVER-vent when the
   body is a partner's kill; kill the co-located lone target immediately rather than the
   alphabetical best.
4. Meeting protocol: teleport everyone to CAFETERIA on resolution (or at least forbid a kill
   on the first tick after a meeting and eject in-vent impostors from the vent); include an
   engine-provided roll-call of "who was in which room when the meeting was called" — this
   is what humans see when everyone runs to the table, and it would have solved s17 m3 by
   elimination.
5. Memory rendering: phrase transitions as "X left A for B (now in B)"; render own path
   ("You: t7 MEDBAY → t8 WEST_HALL"); collapse repeated idle co-presence lines into spans
   ("t30–t47 with p-9 in CAFETERIA"); render joint sabotage repairs; keep spoken vent
   testimony as "p-8 says he saw p-4 vent" not "accused p-4".
6. Emergency trigger: fire on any new first-hand vent/kill observation regardless of prior
   level; allow calling on an outstanding verified flag against a living player.
7. Pacing: give finished crew something to do (patrol/escort/wander toward the last body
   room, follow the most-suspicious player) instead of idling in the hub; do task routing
   by distance, not alphabet; let a moving target be killable if it was co-located last tick.
8. Prompt hygiene: "hidden impostor(s)" per roster; strip the vent-first rule from the
   impostor template (or scope it to non-teammates); suppress re-accusation of ejected
   players before rendering instead of leaking `[invalid ... dropped]`; strip role words
   from recorded rationales if they are ever surfaced.

Files: dumps in /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/w1-9p2i-featured-a/ (s2_verbose.txt, s17_verbose.txt, s0/s1/s3.txt, s2_state.txt, s17_state.txt, *_mem.txt, *_prompts.txt, mem.py, state.py).
