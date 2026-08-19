# w6-4p1i-random — spectator review of replays/samples/4p1i seeds 20, 21, 22, 33, 34, 35, 44, 45, 46, 47

Method: `watch.py` dumps for all 10 games (ticks + meetings + finale); `--verbose` on seeds 22, 33, 44, 20, 21;
`--memory <impostor>` on seeds 33 (p-4), 44 (p-2), 35 (p-4), 45 (p-1), 47 (p-4), 20 (p-3) plus crew memories on
22 (p-3), 21 (p-3), 33 (p-2), 46 (p-1), 47 (p-1). Full LLM prompts/responses were extracted from the JSONL
`llm_calls` for every meeting (scratch: `work/w6-4p1i-random/llm_s<seed>.txt`). Source was opened only to
explain observed behaviour; file:line cited where so.

**Tick convention.** `watch.py` prints "[t N]" = world state after raw tick N's actions were applied
(`[t -1]` = spawn). Agent memory / meeting observations are stamped one higher (perception happens on the
following tick), e.g. seed 22 kill event at [t 6] → memory line "[tick 7] You witnessed p-4 kill". Below,
"t N" = watch tick, "obs tick N" = agent-facing tick.

**Set summary.** 10 games, 8–16 ticks each, 0–1 meetings each (9 meetings total). Winners: CREWMATE_EJECT 3
(20, 33, 46 — all three from a witnessed vent), CREWMATE_TASKS 5 (22, 34, 35, 44, 45), IMPOSTOR_PARITY 2
(21, 47). No sabotage was ever used (0/10). Every impostor ballot in every meeting was SKIP (9/9). Every
crew opening in the 6 skipped meetings pointed at *someone*; in 4 of those 6 (21, 22, 44, 45) it pointed at
the actual impostor and the table still skipped.

---

## Per-game narratives

### Seed 20 — CREWMATES by ejection @t10 (impostor p-3)
**Acts.** t0–3: everyone but p-2 heads east; p-2 does `empty_trash` in CAFETERIA; p-1 walks through
ENGINEERING to STORAGE (`fuel_reserves`); p-4 tasks in ENGINEERING; p-3* stands in ENGINEERING t1–3
(fake `align_engine_output`, rendered as `MOVING`). t4 p-3* → STORAGE; t5 kills p-1 (nobody sees).
t6 vent-enter STORAGE, t7 vent-exit ENGINEERING — **into a room p-3 could see was occupied** (verbose t5/t6:
`p-3* sees players=['p-4@ENGINEERING:task']`), and p-2 walks in on the same tick. Both p-2 and p-4 get
`saw_vent`. t8 all three walk to EAST_HALL together, t9 p-2/p-4 → CAFETERIA, p-3* → ADMIN. t10 p-2 and p-4
BOTH submit `emergency` (raw actions tick 10, reason `suspicion_accumulation`); p-2's resolves.
**Meeting.** p-2 opens with `saw_vent tick 8 p-3 ENGINEERING`, conf 1.0; p-4 opt-in "Saw p-3 vent. Confirmed."
Two `vent_sighting/strong` flags; gate leader p-3 @1.0; p-2, p-4 → p-3; p-3* SKIP. Ejected. Body in
STORAGE never found.
**Notes.** [VERIFIED] p-2's opening is muddled: "You were with p-4, but only one of you can vent. Why were
you in Engineering alone with a vent use?" (p-3 was not alone). [VERIFIED] p-3*'s reply "I suggest we examine
your own erratic movements between East Hall and Engineering" is grounded (impostor adjacent-vision saw p-2
bounce EAST_HALL→ENGINEERING→EAST_HALL) but does not address the vent. [VERIFIED] p-3*'s ballot rationale
"The evidence against the living candidates remains insufficient" — prompt vocabulary ("living") leaking.

### Seed 21 — IMPOSTORS by parity @t12 (impostor p-1)
**Acts.** t1 p-1*, p-2, p-3 in ENGINEERING; p-4 → ADMIN. t2 p-2 → REACTOR (dead end, `start_reactor`),
p-3 stays in ENGINEERING (`align_engine_output`) t2–t9. p-1* fake-tasks in ENGINEERING t1–3, walks into
REACTOR at t4, kills p-2 at t5, vents REACTOR→STORAGE (t6/7), walks STORAGE→ENGINEERING (t8),
EAST_HALL (t9), ENGINEERING (t10) — an aimless oscillation. p-3 finishes at t9, and (because dead p-2's
`start_reactor` was redistributed to p-3) walks into REACTOR at t10, sees the body, reports at t11. p-1*
also moves into REACTOR at raw tick 11 (id-order: its move resolves *before* p-3's report), so **the
killer is standing in the room when the body is reported** and p-3 never learns it (no perception phase
between arrival and meeting). Meeting skips; positions are not reset; t12 p-1* kills p-3 in REACTOR →
parity.
**Meeting.** p-3 opens: found body REACTOR; "I recall seeing p-1 move into REACTOR back at tick 5 …
It's a bit of a stretch" (conf 0.5). p-1* reply: "you were the one who moved from ENGINEERING to REACTOR
at tick 11" (grounded — impostor saw p-3's transition; classic reporter-blame). p-4 opt-in is an 80-word
purple-prose run-on ("The narrative unfolds from the quiet hum of the ADMIN terminal…") that "corroborates"
p-1 with a tick-1 hallway sighting and concludes p-3 is suspicious. Gate leader None. All SKIP.
**What p-3 actually knew** (memory dump): p-2 left ENGINEERING for REACTOR at obs tick 3; p-1 left
ENGINEERING for REACTOR at obs tick 5; p-1 reappeared in ENGINEERING at obs tick 9; p-3 stood in
ENGINEERING (REACTOR's only door) the whole time. A human with that log says "p-1 was the last one into a
dead end with p-2 and p-2 never came out" at high confidence. p-3 said 0.5 and "a stretch". [JUDGMENT] the
information was sufficient; the reasoning and the ballot arithmetic (p-4's suspicion of p-1 = 0.55 <
0.60) were not. [VERIFIED] p-4's ballot rationale leaks scaffolding verbatim: "for the suspicion of 0.55
falls short of the 0.60 threshold required to eject." [VERIFIED] misleading memory provenance: p-3's line
"[tick 9] You saw p-1 in ENGINEERING (moved from EAST_HALL, last seen there at tick 1)" — p-3 had seen p-1
enter REACTOR at tick 5; p-1 actually arrived from STORAGE (vent). [VERIFIED] no map topology is given in
any prompt (grep for adjacen/dead-end/doorway across all 9 meetings' prompts: nothing), so agents cannot
know REACTOR is a dead end.

### Seed 22 — CREWMATES by tasks @t10 (impostor p-4)
**Acts.** p-1 wires in CAFETERIA t0–4, p-2 → LABS, p-3 → ADMIN. p-4* fake-tasks in ENGINEERING t1–3,
walks EAST_HALL (t4) → CAFETERIA (t5), **kills p-1 in the hub at t6 while p-3 walks in** (p-3's move
resolves first, id order) → p-3 is a kill witness (`p-3 sees players=['p-4@CAFETERIA:kill']`). p-3
reports at t7 with p-4 still standing there. Meeting SKIPS. p-4* then hunts p-2: WEST_HALL t8 → MEDBAY t9
→ LABS t10, arriving the same tick p-2 completes the last task. p-3 idles in CAFETERIA t8–10.
**Meeting — the most damning of the set.** p-3's memory contains `[obs p-3:7:1] [tick 7] You witnessed
p-4 kill in CAFETERIA.` p-3 opens "I witnessed p-4 commit the kill right there" (accusation conf 1.0).
p-4*: "Mr. p-3, your assertion is quite preposterous… examine your own hurried transition from Admin to
the Cafeteria." p-2 opt-in: uses the tick-0 spawn co-presence as "evidence" ("I saw p-4 with p-1 in the
Cafeteria at tick 0, which supports p-3's account"). **Contradictions: none. Gate leader: None.** p-3 → p-4
(0.95); p-2 SKIP ("evidence too thin"); p-4* SKIP. Outcome SKIPPED.
Why: [VERIFIED] the turn schema has no witnessed-kill observation type — the opening prompt lists only
`saw_player / completed_task / found_body / saw_vent / whereabouts` (and `meetings/schemas.py:454-456`
lists contradiction kinds `alibi_conflict, alibi_vs_sighting, alibi_vs_physical, vent_sighting` — no kill
kind). So the "single most conclusive act" (`agents/memory/beliefs.py:76-93`, delta 1.0) reaches only
the witness's own belief; p-2's ballot prompt shows `p-4: suspicion 0.58 … this meeting +0.08 … no flag;
carried/soft only` and "when the max sits below the threshold, SKIP is the sound call". A first-hand kill
report moved a peer's suspicion by +0.08. A human table ejects p-4 instantly.
[VERIFIED] p-3's `whereabouts` was tick 5 ADMIN (its completed-task tick), not tick 6/7 CAFETERIA — the
"tick that matters" instruction was not followed. [VERIFIED] the loader shows p-4* as `CAFETERIA:KILL`
at t7 (stale action label one tick after the kill).

### Seed 33 — CREWMATES by ejection @t7 (impostor p-4)
**Acts.** t1 p-1 and p-4* → ENGINEERING; p-2, p-3 → ADMIN. p-4* fake-tasks beside p-1 t1–3, kills p-1 at
t4 (first legal tick — cooldown starts at 4). t5 vent-enter ENGINEERING; t6 vent-exit STORAGE. p-2 (whose
pending task silently switched — see below) walks into ENGINEERING at t6 and, because its move resolves
before p-4's exit, is counted a *source-room witness* of the exit → memory "You witnessed p-4 vent in
ENGINEERING" + "You heard a vent use in ENGINEERING". t7 p-2 reports; p-4*'s raw-tick-7 action was `move
ENGINEERING` (walking back to the body — dropped because the meeting resolved first).
**Meeting.** p-2 (anxious voice): "I-I found p-1's body … I swear I saw p-4 vent right there". p-4*
reply: "That is a lie. You were hiding in ADMIN at tick 2 while p-1 was killed in Engineering. You are the
impostor." p-3 opt-in backs p-2 with a joke ("a talent for disappearing acts"). `vent_sighting/strong`,
gate p-4 @0.95, p-2/p-3 → p-4, p-4* SKIP ("the suspicion is low"). Ejected.
**Notes.** [VERIFIED] false crew memory: p-2's memory says `[obs p-2:5:0] [tick 5] You completed
upload_logs (you were in ADMIN)` although p-2's `upload_logs` sat at 3/7 (loader `task_progress=0.43`,
never completed, no `task_completed` event). Cause (`agents/memory/store.py:1153-1200`): completion is
*inferred* from any change of `pending_task_id`; the dead p-1's `align_engine_output` was redistributed
to p-2 (`engine/maps/canonical_1.yaml dead_task_rule: redistribute`, `engine/tick.py:329-353`), sorts
before `upload_logs`, so pending flipped and the renderer minted a completion. Same mechanism made p-2
abandon a half-done task and walk to the murder room. [VERIFIED] the impostor's memory carries seven
"Your kill cooldown is N ticks" lines (clutter). [JUDGMENT] "witnessed p-4 vent in ENGINEERING" is
generous: p-4 had disappeared into the vent at t5, before p-2 arrived; p-2 "witnessed" the *exit* from
the source room (`engine/rules.py:137-147` counts source-room occupants at exit time as witnesses).

### Seed 34 — CREWMATES by tasks @t10, no meeting (impostor p-2)
**Acts.** p-2* → ENGINEERING t1–3 (fake task, alone — nobody to kill), EAST_HALL t4, ADMIN t5 (p-1 had
just left at t5 — they cross), EAST_HALL t6, CAFETERIA t7, then `wait` t8–10 sitting with p-1 and p-3 who
had both finished and gone home to idle. p-4 grinds `analyze_specimen` alone in LABS t3–10. Zero kills,
zero attempts, zero sabotage. Six ticks (t5–t10) with nothing but a progress bar.
[VERIFIED] the impostor never left the hub after t7 while a lone crewmate sat in LABS for 8 ticks.
[JUDGMENT] the least watchable game possible; a human impostor sabotages or walks to LABS.

### Seed 35 — CREWMATES by tasks @t15 (impostor p-4)
**Acts.** p-1 → ADMIN (`upload_logs`), p-2 → LABS, p-3 wires CAFETERIA then idles there t5–t15 (11 ticks
of `wait`). p-4* ENGINEERING t1–3, EAST_HALL t4, ADMIN t5, kills p-1 at t6, vents ADMIN→MEDBAY (t7/8),
LABS t9 — **alone with p-2 in LABS at t9, t10, t11 and does not kill at t10** (raw tick 10 = `do_task
analyze_specimen`, cooldown had just hit 0: memory "[tick 10] Your kill cooldown is 1 ticks"); submits
`kill p-2` at raw tick 11 but p-2's `move MEDBAY` resolves first (id order) → **kill rejected**; then
chases one room behind (MEDBAY t12 while p-2 → WEST_HALL; WEST_HALL t13 while p-2 → ADMIN). p-2 finds
the 8-tick-old body in ADMIN at t13, reports t14. Meeting skips. t15 p-2 finishes `upload_logs`
(redistributed from dead p-1) → tasks win, p-4* arriving in ADMIN the same tick.
**Meeting.** p-2 opens by *clearing the impostor*: "I saw p-4 doing a task in LABS at tick 11, which clears
them, so I'm pointing at p-3 since they have no alibi" (crew see impostor fake-tasks as `task`; the crew
prompt never warns tasks can be faked). p-3 (cowboy voice) alibis tick 5 CAFETERIA and counter-blames the
reporter. p-4* opt-in: "I was just in ADMIN when the body was found, right alongside p-2" — [VERIFIED] a
lie (p-4 was in WEST_HALL at t13/t14; its memory shows it *saw* p-2 in ADMIN from the adjacent hall),
unfalsifiable because crew have same-room-only vision and p-2 never says "p-4 was NOT there". All SKIP.
[JUDGMENT] no "absence" contradiction exists (a reporter alone with a body cannot flag "X claims to have
been with me and wasn't").

### Seed 44 — CREWMATES by tasks @t12 (impostor p-2)
**Acts.** p-1 → STORAGE, p-3 wires CAFETERIA, p-4 → ADMIN. p-2* ENGINEERING t1–3, STORAGE t4, kills p-1
t5, vents STORAGE→ENGINEERING t6/7 — p-3 walks into ENGINEERING on the exit tick but **is not a witness**
because p-2's action resolves before p-3's move (id order); verbose t7: `p-3 sees
players=['p-2@ENGINEERING:None']`. Compare seed 20 (same geometry, impostor id higher than the walker →
witnessed). p-3, carrying dead p-1's redistributed `fuel_reserves`, walks to STORAGE (t8), reports (t9).
Skip. Post-meeting p-2* wanders WEST_HALL/ADMIN/EAST_HALL t10–12 while p-3 is alone in STORAGE and p-4
alone in CAFETERIA (p-2 even sees p-4 there from WEST_HALL at t10 and turns away). Tasks win.
**Meeting.** p-3 opens on p-2 (0.5, "alone in Engineering at tick 8, right next door"). p-2* reply:
"p-3 moved from Engineering directly to Storage at tick 9, which is the exact moment the body was
reported". p-4 opt-in *sides with the impostor*: "I witnessed p-2 in the East Hall at tick 9, which
renders their presence in Storage at the time of the report impossible" — [JUDGMENT] fallacy: the kill
was ~tick 6, not the report tick; presence at report time clears nobody. All SKIP; p-4's rationale: "both
suspects hold equal suspicion below the threshold" (scaffold leak).

### Seed 45 — CREWMATES by tasks @t13 (impostor p-1)
**Acts.** p-2 → STORAGE, p-3 CAFETERIA trash then idle, p-4 MEDBAY long scan (t2–t12). p-1* ENGINEERING
t1–3, STORAGE t4, kills p-2 t5, vents → ENGINEERING t7 (p-3 arrives same tick, not a witness — id order
again). p-3 (redistributed `fuel_reserves`) walks to STORAGE t8, reports t9. Skip. Post-meeting p-1*
random-walks WEST_HALL→ADMIN→EAST_HALL→ENGINEERING t10–13 while p-3 is alone in STORAGE t10–13 and p-4
alone in MEDBAY t10–12; cooldown was long since 0. Tasks win at t13.
**Meeting.** p-3 opens on p-1 (0.5) using a tick-1 hallway co-sighting. p-1* (numbered-list voice):
"1. p-3 was in Engineering at tick 8. 2. p-3 moved to Storage at tick 9, right before calling the
meeting." p-4 (nervous voice) buys it. All SKIP; p-1* SKIP with confidence 0.0.
[VERIFIED] impostor ballot prompt is the crew ballot prompt ("name the one player you believe is the
impostor, or SKIP") over an IMPOSTOR memory whose belief table is empty → max suspicion 0.00 → SKIP.
[JUDGMENT] with 3 voters, impostor + one crew voting the same crewmate would have ejected them and won
by parity; the impostor never uses its ballot as a weapon (0/9 meetings).

### Seed 46 — CREWMATES by ejection @t10 (impostor p-3)
**Acts.** p-1 → LABS, p-2 → ADMIN (`upload_logs`), p-4 → REACTOR (long task). p-3* ENGINEERING t1–3,
REACTOR t4, kills p-4 t5, vents REACTOR→ADMIN t6/7, exiting next to p-2 (REACTOR is not adjacent to
ADMIN so p-3 could not see it was occupied — excusable). p-2 finishes at t7, walks EAST_HALL→CAFETERIA and
presses emergency at t10 (arrives t9, presses t10). p-1 crosses the impostor in WEST_HALL at t8.
**Meeting.** p-2: "I saw p-3 vent in ADMIN at tick 8. I was right there doing upload_logs." p-3* reply:
"you were lingering in that exact room at tick 8, suspiciously close to where you claim I vanished" —
[JUDGMENT] self-defeating (accuses the witness of being in the room where the witness says it saw you).
p-1: "I was in LABS at tick 8. I back p-2's report." (minor: p-1 was in MEDBAY at obs tick 8). Vent flag,
gate p-3 @1.0, ejected. Body in REACTOR never found.

### Seed 47 — IMPOSTORS by parity @t13 (impostor p-4)
**Acts.** p-1 → MEDBAY (`submit_scan`), p-2 → ENGINEERING, p-3 → ADMIN. p-4* fake-tasks beside p-2 in
ENGINEERING t1–3, kills p-2 at t4, vents ENGINEERING→LABS t5/6, fake-tasks in LABS t7–8, then `move
MEDBAY` twice (t9, t10 — a no-op second move), WEST_HALL t11, CAFETERIA t12, kills p-3 at t13. p-3 had
finished at t4 and idled in CAFETERIA t7–t12 (a sitting duck). p-1 abandoned `submit_scan` at 0.33 at t5
(redistributed `align_engine_output` sorts first) and walked to ENGINEERING, finding the body t8, report
t9; then p-1 stayed in ENGINEERING doing the 8-tick task (0.56 by the end) — race lost.
**Meeting.** p-1 (janitor voice): "I was just finishing up in Medbay, so I'm clean as a whistle … p-3 and
p-4 were hanging with p-2 at the start … Don't make me come over there with a mop." p-3 reply: alibi
ADMIN tick 5, blames reporter. **p-4* opt-in: "I was in Engineering at tick 5, right where p-2 died"** with
`whereabouts tick 5 ENGINEERING` and `saw_player tick 5 p-2 ENGINEERING co_present [p-4]` — the impostor
volunteers being alone with the victim in the kill room at the kill tick (its memory: "[tick 4] You saw
p-2 task in ENGINEERING", "[tick 5] You (IMPOSTOR) killed p-2"). Nobody reacts: p-1's ballot prompt shows
"(no per-player beliefs yet)", max suspicion 0.00; all SKIP.
[VERIFIED] false memory spoken at the table: p-1's memory `[obs p-1:5:0] [tick 5] You completed
submit_scan (you were in MEDBAY)` — never completed (0.33); the redistribution-induced pending flip minted
it, and p-1 turned it into "I was just finishing up in Medbay". [VERIFIED] impostor self-tell ignored.
[VERIFIED] p-3's ballot rationale is byte-identical to p-3's in seed 44 ("Actually, the evidence is too
thin to eject anyone, so I'm skipping to avoid wasting a vote on weak accusations.").

---

## (a) Information gathering

1. [VERIFIED] **Crew see only their own room** (`engine/visibility.py` role split: crew `same_room_only`,
   impostor `same_room_and_adjacent`). Combined with "everyone leaves the hub at t0 to a different task
   room", the typical crew memory at the meeting is 3 spawn lines + 1 found-body line (seed 47 p-1, seed
   22 p-2, seed 21 p-4). Voters usually know *nothing* about the interval in which the kill happened.
2. [VERIFIED] The **impostor sees adjacent rooms, even from inside a vent** (seed 33 t5: p-4* VENTING in
   ENGINEERING `sees p-2@EAST_HALL, p-3@EAST_HALL`; seed 20 t5–6 p-3* in STORAGE sees p-4 tasking in
   ENGINEERING). Its memory is rich (movement transitions "You saw p-2 move from LABS to MEDBAY", seed
   35) — but it also carries seven cooldown lines and never uses the richness (see (c) hunting).
3. [VERIFIED] **Spoken testimony enters beliefs only as a scalar nudge**: ballot tables show "this
   meeting +0.05 / +0.08 / -0.05" for accusations/corroborations, +0.30/+0.50 for a verified vent flag.
   A first-hand "I witnessed p-4 kill" moved a peer by +0.08 (seed 22). In seed 47 an impostor's spoken
   admission of being at the scene moved p-1's table not at all ("no per-player beliefs yet").
4. [VERIFIED] **No structured channel for a witnessed kill** (schema in every opening prompt; contradiction
   kinds `meetings/schemas.py:454-456`). The strongest fact in the game cannot become "VERIFIED evidence".
5. [VERIFIED] **False memories minted by task redistribution** (seeds 33 p-2, 47 p-1: "You completed X"
   for a task at 3/7 and 1/3). Cause: `agents/memory/store.py:1153-1200` infers completion from
   `pending_task_id` change; the comment's invariant "owned set only ever shrinks" is broken by
   `dead_task_rule: redistribute` (`engine/tick.py:329-353`). In seed 47 the false line was spoken as an
   alibi.
6. [VERIFIED] **Misleading provenance suffixes**: "(moved from EAST_HALL, last seen there at tick 1)"
   attached to a tick-9 sighting when the subject was last seen entering REACTOR at tick 5 (seed 21 p-3),
   or "(moved from CAFETERIA, last seen there at tick 0)" for a player met 9 ticks later (seed 46 p-1).
   The suffix picks the last *different-room* sighting and ignores transition lines.
7. [VERIFIED] Rendering clutter/order: "most salient first" interleaves ticks 5,4,3,2,2,7,6,6,2 (seed 33
   p-4) — hostile to timeline reasoning; duplicate id-less lines "[tick 10] p-1 left ENGINEERING." next to
   the id'd transition line (seed 21 p-3, seed 35 p-4).
8. [VERIFIED] Things a human would know that agents don't: map topology (no `<map>` block; REACTOR/STORAGE/
   LABS are dead ends — decisive in seed 21); who was in the room at the report (seed 21: killer standing
   next to reporter, unperceived); the room of the report for non-reporters (header says only "p-3
   reported body body-p-2-5 at tick 11"); that "doing a task" can be faked (seed 35 p-2 "clears" p-4).
9. [JUDGMENT] Vent sightings are the only rich, decisive information the crew ever gets, and they arise
   from FSM carelessness (see (c)) rather than from crew play.

## (b) Decisions / accusations / votes

- **Openings.** Reporters do report the body and give a room. Accusation grounding is thin by necessity:
  tick-0/1 spawn co-presence used as evidence in 22, 44, 45, 47 ("p-3 and p-4 were hanging with p-2 at
  the start"). The good exceptions: 21 (p-3 had the dead-end deduction and under-sold it at 0.5), 22
  (witnessed kill, 1.0), 20/33/46 (vent). Seed 35's opening cleared the impostor on a faked task.
- **Replies.** [VERIFIED] The impostor reply prompt instructs "Dismiss the accusation in a few words… explain
  nothing about your own whereabouts… `observations` empty" (seed 21 call 1). So the accused impostor never
  answers the actual accusation and always pivots to ONE counter-accusation — a template a human would read
  as a tell. Formulaic near-duplicates across games: "Mr. p-2, your assertion is entirely baseless… examine
  your own erratic movements" (20) / "Mr. p-3, your assertion is quite preposterous… examine your own hurried
  transition" (22). Crew replies do answer (alibi + counter), e.g. 35 p-3, 47 p-3.
- **Reporter-blame is the dominant deflection and it works.** Impostor replies in 21, 22, 44, 45 (and crew
  in 35, 47) accuse the reporter for "moving to the scene right before the report". Crew opt-ins in 44 and
  45 sided with the impostor on exactly that logic. The ballot prompt has a "self-report is weakly
  exculpatory" paragraph, but the discussion prompts don't, so the argument lands unrebutted in speech.
- **Ballots.** 3 ejections, all vent-flag-driven, all correct. 6 skips, 4 of which had the impostor as the
  opening's target. Skip rationales are near-monotone ("the evidence is too thin to eject anyone" in
  21, 22, 35, 44, 45, 46, 47) because the persona says "or SKIP if the evidence is too thin". Scaffolding
  leaks: "the suspicion of 0.55 falls short of the 0.60 threshold" (21 p-4), "equal suspicion below the
  threshold" (44 p-4), "the suspicion is too low" (45 p-4, 33 p-4*), "living candidates/living player"
  (20, 22 impostors). Citations are correct when made (turn ids / obs ids in 20, 33, 46, 22).
- **Impostor ballots: SKIP 9/9, confidence 0.0–0.5.** [VERIFIED] the impostor is voting with the crew
  ballot prompt over an empty belief table. Never bussed, never piled on, never swung a 1-1-1.
- **Impostor deception quality.** Lies are rare and mostly harmless (35: "I was in ADMIN alongside p-2");
  one outright self-tell (47: places itself alone with the victim at the kill tick, plus a fabricated
  `saw_player` of the victim at the death tick) — unexploited. Seed 46's counter is self-defeating.
- **Hallucinations vs. omniscient truth.** 47 p-1 "just finishing up in Medbay" (substrate-minted); 35
  p-4* "in ADMIN when the body was found" (lie); 46 p-1 "LABS at tick 8" (was MEDBAY, harmless); 33 p-4*
  "hiding in ADMIN at tick 2 while p-1 was killed" (kill was tick 5; muddled). No id husks like
  "[obs p-1:5:1]" in free_text; ids appear only in structured `evidence` fields ('obs p-2:0:1', 'obs
  p-4:5:1'). Wording matches the 1-impostor game ("a hidden impostor").
- **Voices.** Colourful and mostly consistent (janitor, cowboy, nervous, contrarian "Actually…", numbered
  reasoner). Two failure modes: purple-prose narrator producing an 80-word single sentence of near-zero
  content (21 p-4), and identical rationale sentences reused across seeds (44/47 p-3).

## (c) World-sim holes / glitches / awkwardness

1. [VERIFIED] **Impostor opening is 10/10 identical**: EAST_HALL t0 → ENGINEERING t1–3 standing on a fake
   `align_engine_output` (rendered `MOVING` in the omniscient view) while the initial 4-tick cooldown runs
   out, then kill at the first legal tick (t4: 33, 47; t5: 20, 21, 44, 45, 46; t6: 22, 35). Any spectator
   learns "the one who goes to Engineering and stands still is the impostor" after two games; any crewmate
   who goes to ENGINEERING with it dies (33 p-1, 47 p-2).
2. [VERIFIED] **Kill → vent-enter → vent-exit next tick, 10/10 kills.** The vent is used as a reflex even
   with nobody around (44, 45), and produced all three losses-by-ejection (20, 33, 46). In 20 the impostor
   vented into a room it could *see* was occupied.
3. [VERIFIED] **Within-tick id-order artefacts** (`engine/tick.py:565-600` applies actions sequentially;
   witnesses computed on the working state, `engine/rules.py:29-40,137-147`): whether a crewmate walking
   into a room *witnesses* a vent/kill depends on whether its id sorts before the impostor's (20 vs 44/45,
   same geometry, opposite results; 22's kill witness). Same ordering makes a kill get rejected because the
   target's move resolved first (35 raw t11) and puts the killer in the room at report time (21).
4. [VERIFIED] **Impostor's fake task shows as `MOVING`** in the loader state for 3 ticks while it stands
   still (every game t1–3) — spectator glitch; crew correctly see `task`.
5. [VERIFIED] **Task redistribution acts as a beacon to the body**: dead crewmate's task goes to a living
   crewmate who walks straight to the kill room (33, 44, 45, 47, 35, 21). It also makes crew abandon
   partly-done tasks (33 p-2 at 3/7, 47 p-1 at 1/3) and mints the false "You completed" memory (see (a)5).
   And the map comment claiming redistribution makes "the only crew win path … ejection" does not hold in
   4p1i: 5/10 wins were CREWMATE_TASKS.
6. [VERIFIED] **Bodies persist until a meeting and are cleared by it** (35: body lies 8 ticks; no `bodies:`
   line after any meeting). No double report observed (impossible after clearing). Reporter lag is always
   exactly one tick (arrive t, report t+1: 21, 22, 33, 35, 44, 45, 47) — reads as "stands over the body for
   a beat".
7. [VERIFIED] **Positions are NOT reset after a meeting** (21: p-1*/p-3 remain in REACTOR → kill at t12;
   22, 35, 44, 45, 47 likewise). [JUDGMENT] this is unlike the genre and decided seed 21; combined with no
   cooldown reset it hands the impostor a free post-meeting kill on the reporter.
8. [VERIFIED] **Impostor hunting is poor**: post-skip 1v2 endgames were lost to tasks 4/6 (22, 35, 44, 45)
   with lone crewmates available for many ticks (45: p-3 alone in STORAGE t10–13, p-4 alone in MEDBAY;
   44: p-3 alone in STORAGE t10–12; 34: p-4 alone in LABS t3–10 with no attempt at all); "one room behind"
   chase (35 t11–13); no-op repeated move (47 raw t9–10); did not fake-then-kill in LABS at cooldown 0 (35
   t10). No sabotage in 10 games; no impostor emergency.
9. [VERIFIED] **Crew idle after tasks**: p-3 idles 11 ticks in CAFETERIA (35), 6 ticks (47, then killed
   there), p-1/p-3 t7–10 (34), p-3 t8–10 (22). Crew never group up, patrol, or go look for a missing
   player. Dead time: 34 t5–10, 35 t7–13, 47 t6–8/t10–12.
10. [VERIFIED] Both surviving crew pressed emergency on the same tick in 20 (only one resolves) — fine, but
    the second's button use is presumably consumed. Actions submitted after the report on the meeting
    tick are dropped (33 raw t7 p-4 move; `engine/tick.py` returns on phase MEETING) — nothing illegal
    happens on meeting ticks; the venting impostor case never arose (all exits completed before reports).
11. [VERIFIED] Vent-exit "witness" from the *source* room (33): p-2 arrives after p-4 vanished and still
    gets "You witnessed p-4 vent in ENGINEERING" — believability cost, crew benefit.
12. [VERIFIED] Emergency callers walk to CAFETERIA and press on the tick after arrival (20 t9→t10, 46
    t9→t10) — one wasted tick each.

## (d) Watchability

- Rewind moments: 22 t6 (kill in the hub as p-3 walks in) and the meeting that follows (a witnessed kill
  gets skipped — infuriating in a good way); 21 t10–12 (killer walks in behind the reporter, meeting
  skips, kill); 47 turn 2 (impostor talks itself onto the crime scene and nobody blinks); 20 t7 (vent
  exit in front of two people); 35 t9–13 (the failed chase, one room behind).
- Boring: 34 entirely; every t1–3 (four people standing still); all post-meeting task grinds; the
  monotone SKIP round; games are 8–16 ticks — at 2 Hz that is 4–8 s of world time around one 3-turn
  meeting, so the "game" is really one conversation with a 5-second prologue.
- The meetings themselves are the entertainment (voices are fun), but they resolve on arithmetic the
  viewer can't see (the 0.60 threshold) rather than on what was said.

---

## Cross-game patterns and ranked findings

Recurring: impostor script (Engineering → first-legal-tick kill → reflex vent); crew script (leave hub,
sit alone in task room, idle when done); meeting = reporter's guess vs. reporter-blame, resolved by the
suspicion table; the only crew wins by deduction are really wins by "impostor blundered into a vent
witness".

Ranked by severity (impact on whether the sim is a believable, decidable social-deduction game):

1. **A witnessed kill cannot become evidence for anyone but the witness** — no `saw_kill` observation type,
   no contradiction kind, +0.08 to peers; seed 22 skipped with a first-hand witness. [VERIFIED]
2. **The suspicion-threshold arithmetic decides meetings and pushes SKIP** — 6/9 skipped; 4 of them had the
   impostor named in the opening; scaffolding numbers leak into speech (21, 44). [VERIFIED]
3. **Impostor never plays its ballot** — crew ballot prompt over an empty belief table → SKIP 9/9; a
   1-1-1 swing was available (45). [VERIFIED]
4. **Impostor FSM: reflex vent after every kill (all 3 ejections), venting into a visibly occupied room
   (20), no hunting in 1v2 endgames (34, 44, 45), one-room-behind chase (35), fake-task-instead-of-kill at
   cooldown 0 (35), 0 sabotage.** [VERIFIED]
5. **Task redistribution side-effects**: false "You completed" memory spoken as alibi (47), abandoned tasks
   (33, 47), body-beacon walk (6 games). [VERIFIED]
6. **Within-tick id-order decides who witnesses what and whether kills land** (20 vs 44/45, 22, 35 t11, 21
   t11). [VERIFIED]
7. **Crew information starvation**: same-room vision + solo tasking + no map topology + no "who was at the
   scene" → voters reason from spawn co-presence; the one strong deduction available (21) was
   under-confident. [VERIFIED/JUDGMENT]
8. **Positions/cooldown not reset after meetings** → free post-meeting kill on the reporter (21). [VERIFIED]
9. **Impostor reply protocol forbids answering the accusation** and produces template deflections; crew
   opt-ins routinely side with reporter-blame (44, 45). [VERIFIED]
10. **Rendering defects**: misleading "(moved from …, last seen …)" provenance, non-chronological ordering,
    duplicate id-less transition lines, cooldown clutter, stale `KILL`/`VENT` action labels and fake-task
    `MOVING` in the omniscient view. [VERIFIED]

## Ideas (concrete)

1. Add a `saw_kill` observation shape + a `kill_sighting/strong` contradiction (mirror of `vent_sighting`)
   and let it seed the gate/leader; teach the ballot prompt that a spoken first-hand kill witness is at
   least a 0.7 case for peers, not +0.08.
2. Give the impostor its own ballot prompt: vote to survive (pile onto the crew's leading suspect, break
   ties toward a crewmate, never SKIP when one more crew vote on someone wins the game).
3. Impostor FSM: vent only when a witness is possible or the impostor is being followed; never vent-exit
   into a room currently visible-occupied; in a 1v2 endgame path to the nearest lone crewmate (it already
   perceives adjacent rooms and the report room); use lights/reactor sabotage at least once; kill on the
   first cooldown-0 tick when alone with a target.
4. Reset everyone to CAFETERIA (and the kill cooldown) after a meeting; or, if not, at least perceive the
   room at report time so the reporter can say "p-1 was standing right there".
5. Redistribution: only redistribute at task-boundary (never pre-empt a started task), and derive
   "completed" from the engine's `TaskCompleted` event rather than a pending-id flip; consider a memory
   line "You were assigned p-1's task at STORAGE" so the walk-to-the-body is at least explicable.
6. Put a compact `<map>` block in meeting prompts (adjacency + dead ends + which room the body was reported
   in) — the seed-21 deduction is trivial with it.
7. Make within-tick resolution simultaneous for perception (compute witnesses/visibility on the
   post-tick state, or resolve moves before kills/vents) so id order stops deciding evidence.
8. Crew FSM after tasks: rendezvous in the hub *together*, or shadow another crewmate; a "buddy" rule would
   both create witnesses and reduce 11-tick idles.
9. Meeting protocol: give the accused impostor a mandatory whereabouts answer (unfalsifiable lies are
   fine — that's the game), add an "absence" flag when a claimed co-presence is denied by the claimed
   partner, and de-weight "moved to the scene right before reporting" for the reporter in the discussion
   prompts as it already is in the ballot prompt.
10. Rendering: chronological order (or a two-block "timeline / highlights" layout), drop the id-less
    duplicate transition lines, fold cooldown into one line, fix the provenance suffix to use the latest
    transition, and render the impostor's fake task as `TASK(fake)` in the omniscient viewer.
