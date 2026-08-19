# w4-9p2i-random-b — spectator review of replays/samples/9p2i seeds 30, 31, 32, 33, 40, 45, 49

Method: `watch.py` (plain + `--verbose` on all seven; `--memory` on p-7/p-3 (s30), p-1/p-8/p-5 (s31), p-5 (s32), p-6/p-1 (s40), p-1 (s45)); raw JSONL `llm_calls` prompts read for s30 m1, s32 m0, s45 m0/m1, s33 m1; two helper scripts written on top of `ReplayLoader` (`work/w4-9p2i-random-b/analyze.py` = kill/body/idle/ping-pong/post-meeting scan; `repro_policy.py` = offline re-derivation of an impostor's tactical decisions, matches the recorded action stream tick-for-tick). Code was opened only to explain observed behaviour; file:line cited where it was.

Tick convention (VERIFIED, s30 t5-8 vs obs ticks): the `[t N]` line in watch.py is the world AFTER tick N's actions; an observation stamped `[tick N+1]` in an agent's memory describes that state. I quote both forms; "obs-tick" = memory stamp.

Legend: [V] = VERIFIED in the bytes; [J] = JUDGMENT/inference. Tags: GLITCH (looks broken), DESIGN (deliberate but hurts believability), REASONING (LLM quality).

Scoreboard of the 7 games (26 meetings): 10 SKIP, 11 correct ejections, 5 wrong ejections. Of the 11 correct ejections, 10 were vent sightings and 1 (s40 m2) was carried-over suspicion; NONE came from body-proximity / "walked in on the killer" testimony. All 5 wrong ejections were driven by roll-call/alibi flags on innocents' own self-location errors (s30 m3 p-7, s31 m1 p-1, s31 m4 p-9, s40 m1 p-7) or by the table herding against a truthful vent witness (s32 m0 p-1). Winners: IMPOSTORS s30, s31, s32, s40; CREW s33, s45, s49.

---------------------------------------------------------------------------------------------------

## SEED 30 — IMPOSTORS win by parity at t42 (p-3*, p-6*; 4 meetings)

### Narrative
Act 1 (t0-t8). Everyone leaves spawn except p-8 (CAFETERIA task) and p-6*, who "fakes" `empty_trash` in CAFETERIA for t0-t3 (raw actions `do_task empty_trash`; watch renders him IDLE, crew p-8 sees `p-6@CAFETERIA:task`). t4: `p-6*@CAFETERIA:KILL ... EVENT kill p-6->p-8` — a hub kill with nobody else present. Body lies 4 ticks; p-5 walks in at t7, reports t8. Meeting-0: p-5 correctly accuses p-6 (0.5, "lingering in East Hall at tick 7"); p-6 deflects onto p-5; p-3* corroborates p-6 AND publicly says "tick 5: body of p-8 in CAFETERIA" and "p-3 places THEMSELVES in CAFETERIA at tick 8" (both false; p-3 was in EAST_HALL/ADMIN). Nobody notices that p-3 claims to have seen the body 3 ticks before it was reported. Gate `leader None ... passed False` -> 8/8 SKIP.
Act 2 (t9-t10). One tick after the meeting, p-3* kills p-2 in ADMIN at t9 as p-4 walks in (`others_in_room_now=['p-4']`); p-4 reports at t10 while p-3 slips to EAST_HALL. Meeting-1: p-4 "p-3 was the only one I saw there with me"; five players accuse p-3 (0.6-0.75). Only flag: a WEAK one on p-5 (endpoint-tick). Gate `leader None` -> 7/7 SKIP. Rationales: "p-3 has no flag, p-5's flag is weak. Why vote blind?" (p-4), "No one else has a case that breaks the threshold" (p-3*).
Act 3 (t11-t30). 15 event-free ticks (t11-t25). p-4 and p-5 finish tasks and idle in CAFETERIA t14/19-t26; p-7 tasks alone in MEDBAY t15-t25 and no impostor ever comes; p-3* ping-pongs EAST_HALL<->ENGINEERING t19-t25 and p-6* ADMIN<->EAST_HALL t20-t24 (repro shows both stalking stale sightings — p-6 is stalking p-2, who died at t9 but whose body p-6 never saw). t26 reactor sabotage by p-3 while p-1 is repairing in REACTOR; t28 p-3 kills p-1 in REACTOR with partner p-6 watching; t29 both impostors vent out of REACTOR simultaneously; t30 p-4 walks in and "sees" p-6 vent (only p-6, not p-3 — see GLITCH below). Meeting-2: `vent_sighting/strong` -> p-6 ejected (correct). p-3*'s ballot rationale: "I see p-6 venting in my own logs, but I cannot vote my own partner."
Act 4 (t32-t42). Positions are not reset: p-4 stays in REACTOR (with the ejected p-6's kill room) and resumes a task that was REDISTRIBUTED to him when p-1 died (tp 1.00 -> 0.57 at t28); p-3* walks in and kills him at t35. p-5 finds the body at t39. Meeting-3: p-7 answers roll-call "MEDBAY at tick 39" (he was in CAFETERIA t32-t39, IDLE) -> p-9 sighting flags him -> p-7 ejected (WRONG). p-3* pounces: "p-7 is lying about Medbay to hide their tracks". p-3 then kills p-5 in REACTOR at t42 (p-5 also had a redistributed REACTOR task). Parity.

### (a) Information gathering
- [V] Impostors see ADJACENT rooms, crew see only their own room: t0 `p-6* sees players=[... 8 players in WEST_HALL/EAST_HALL/CAFETERIA]` while `p-8 sees players=['p-6@CAFETERIA:task']`. Code: `engine/visibility.py:98-128` (`_resolve_observer_visibility_mode`: crew downgraded to `same_room_only`). DESIGN — it makes impostors the best-informed witnesses at the table (their sightings are true and plentiful) and it also gives them the partner's kill as "You discovered p-8's body" (p-3's memory line `[obs p-3:5:6] [tick 5] You discovered p-8's body in CAFETERIA.` while p-3 stood in EAST_HALL).
- [V] The rendered memory has NO line stating the agent's own room per tick. p-7's memory at m3 (`--memory p-7`) contains dozens of "You saw p-9 in CAFETERIA (tick 37/38/39)" but the last explicit self-placement is `[obs p-7:26:0] [tick 26] You completed submit_scan (you were in MEDBAY).` — the LLM answered the roll-call "MEDBAY, tick 39". That hallucination is what got him ejected. Same failure class in s31, s40, s32 (below). GLITCH-grade information design: the roll-call demands a self-location the memory never states.
- [V] Testimony DOES enter memory, as `[tick 9] [meeting] CLAIM by p-2 (unverified): p-2 was in MEDBAY during ticks 6-6.` lines and it nudges beliefs ("this meeting +0.15" for p-3 in p-1's m1 vote prompt). But (i) `found_body` observations spoken by others are NOT recorded as claims (p-3's "body of p-8 at tick 5" left no trace), (ii) free_text never enters memory, (iii) meeting-2/3 memories of p-7 kept exactly ONE claim from meeting-1 ("[tick 11] CLAIM by p-1: accused p-3") — the salience budget drops most testimony.
- [V] Nobody's memory records who died where or who reported: p-7's memory at m3 has no line for p-2's death, p-1's death, or p-6's ejection. Voters know only the current body (from the meeting header "p-5 reported body body-p-4-39 at tick 39"). A human remembers "p-2 died in ADMIN and p-3 was standing there".
- [V] Belief block after 3 kills and 3 meetings: p-7's beliefs list `p-3: last seen in EAST_HALL at tick 8` with NO suspicion — the impostor who killed 3 people is invisible to the belief system.
- [V] Vote prompt supplies engine arithmetic ("Your maximum suspicion ... 0.60; skip threshold 0.60") and the transcript shown to VOTERS strips all spoken observations (only "p-4 accuses p-3 (0.60): <free_text>"). Voters never see the roll-call table.

### (b) Decisions
- Opening reports are decent (p-5 m0, p-4 m1 both name the right person with real observations). Replies by impostors are pure deflection but coherent ("You walked into ADMIN alone at tick 10. You killed p-2 and called the meeting to frame me.").
- [V] Ballots follow the gate, not the room: m1 has 5 accusers of p-3 and 7/7 SKIP; rationales cite "no flag"/"threshold". Machinery language in rationales: "The only hard flag is on p-5" (p-7), "under the threshold" (p-6*).
- [V] Impostor self-tells never punished: p-3 spoke a body sighting 3 ticks pre-report (m0 turn 4, m3 turn 3), placed himself in the wrong room (CAFETERIA t8; REACTOR t31 in m2 while he was in STORAGE/ENGINEERING). Nobody flags it because no crew "saw" him elsewhere.
- [V] Impostor coordination: p-3 corroborates p-6 at m0 (true fact used as cover); p-6 lightly buses p-3 at m2 ("p-3 has been acting weirdly isolated near the reactor"); both SKIP rather than vote each other; p-3's rationale names the partner. Private rationales reveal role ("my teammate p-3", "I cannot vote my own partner") — recorded, not spoken.
- Hallucination: p-6* m0 "I was just passing through East Hall because I was worried about the lights flickering" — no lights sabotage ever happened. p-5 m0 "close enough to strike and run" — fine. p-7's m3 whereabouts (MEDBAY) — the fatal one.
- Wording: every prompt persona says "a hidden impostor is killing crewmates one at a time" (singular) in this 2-impostor game (m1 prompt, `<persona>`; 51/51 prompts checked in s32).
- Wrong ejection m3 = REASONING+DESIGN: p-7 misread his own memory; the flag machinery treats it as proof of lying.

### (c) Sim holes
- [V] Bodies persist across meetings only if undiscovered; the reported one is cleared (t32 no `bodies:` line). No double reports observed anywhere.
- [V] Positions are NOT reset after meetings: `meeting@t31: p-4 REACTOR->REACTOR, p-5/p-7/p-9 EAST_HALL->CAFETERIA, p-3 ENGINEERING->ENGINEERING`. Consequence: the reporter resumes tasking next to the killer (p-4 killed by p-3 four ticks later at t35).
- [V] Task redistribution on death (`api/replay_loader.py:1491` shows per-owner instances; `orchestrator/game.py:1176-1180` "re-keyed to living crewmates under redistribute"): tp drops p-4 1.00->0.57 (t28), p-5 1.00->0.67 (t35), p-9 1.00->0.81 (t42). Each drop sends one crewmate alone into REACTOR where p-3 camps; three consecutive kills there (t28, t35, t42). DESIGN that makes the endgame a conveyor belt.
- [V] Vent-witness asymmetry by id order (GLITCH): t30 both impostors exit REACTOR; `p-4 sees players=['p-6@REACTOR:vent']` but not p-3. Cause: actions apply in submitted (id) order (`engine/tick.py:590-600`), and vent witnesses are computed at apply time (`engine/rules.py:137-147`); p-3's exit resolved before p-4's move into REACTOR, p-6's after. Also physically odd: p-4 "witnessed p-6 vent in REACTOR" for an EXIT whose destination was ADMIN — the source-room witness of an exit sees someone who was already invisible in the vent.
- [V] Rejected kill t16 (`p-3->p-1 resolved=False`, target left EAST_HALL the same tick, id order again).
- [V] Dead time: 15 event-free ticks t11-t25; crew idle in CAFETERIA (p-4 t19-26, p-5 t14-26, p-7 t33-39, p-9 t33-42); impostor ping-pong t19-t25.
- [V] Impostor loiters at spawn (p-6 IDLE CAFETERIA t-1..t3 faking a task) then hub-kills the one crewmate with a CAFETERIA task at t4 — a pattern (also s33 t4, s40 t4, s49's p-9 loiters t-1..t3).
- [V] Kill with partner present (t28) and both impostors venting on the same tick from the same room (t29) — a spectator sees two players vanish into one vent.

### (d) Watchability
Rewind moments: t9-10 (p-4 walks in on the killer — and then the room votes SKIP 7-0: infuriating in a good way), t29-31 (double vent, p-4 catches one), m3 (an innocent talking himself out of the airlock). Boring: t11-t26 (nothing), t32-t42 (predictable REACTOR conveyor). The all-SKIP first two meetings make the crew look asleep.

---------------------------------------------------------------------------------------------------

## SEED 31 — IMPOSTORS win at t49 (p-3*, p-5*; 5 meetings)

### Narrative
p-3* kills p-2 in REACTOR t5 (nobody near), vents to ADMIN t6-7, walks to MEDBAY, kills p-4 at t10 (alone), enters vent t11 and SITS IN THE VENT for t11-t12 while p-7 walks into MEDBAY at t11 with the body. t12 p-1 finds p-2 in REACTOR and reports; p-7's report of p-4 the same tick is pre-empted (id order). Meeting-0 at t12 (p-3 is inside a vent during the meeting): everyone accuses p-1 (the reporter: "no alibi") — 7/7 SKIP. During this meeting p-7 announces a SECOND body ("I found p-4 dead in Medbay at tick 12") which is about a different corpse. t13: p-3 exits the vent MEDBAY->ADMIN in front of p-7 (source) and p-8 (destination); p-7 reports p-4 -> meeting-1 on the very next tick. Meeting-1: a roll-call for tick 11 in which p-1, p-8 (crew) and p-5* all misplace themselves; p-1 collects 3 `alibi_vs_sighting/strong` flags and is ejected 6-1 (WRONG). p-7 and p-8 have just witnessed p-3 vent but the observation lands after the meeting. p-7 then finishes a task (t14-17), walks MEDBAY->WEST_HALL->ADMIN->EAST_HALL->CAFETERIA and presses the button at t22 — 8 ticks after seeing the vent; p-8 (who also saw it) never calls. Meanwhile p-3 kills p-6 (t18, REACTOR — p-6 had just inherited p-1's tasks: tp 1.00->0.56 at t14) and vents; p-5 vents twice too. Meeting-2 (emergency): 3 vent flags -> p-3 ejected. Meeting-3 (t26, p-6's 8-tick-old body): p-7 accuses p-9 for being "nowhere near where the kill happened"; p-8's turn is "[invalid accusation target 'p-3' dropped] You're arguing over cafeteria sightings while I have eyes on p-3 venting..." -> SKIP. t27-t45: sole impostor p-5 ping-pongs REACTOR<->ENGINEERING for 20 ticks while p-7 tasks ALONE in REACTOR t26-t30 and p-9 idles in CAFETERIA t9-t38 (30 ticks). p-5 sabotages at t38, kills p-7 in ADMIN at t46. Meeting-4: p-9's alibi ("ENGINEERING 43-48"; he was in CAFETERIA 45-49) is flagged by p-5's adjacent-vision sightings -> p-9 ejected (WRONG) -> parity.

### (a) Information gathering — the roll-call/self-location failure, dissected [V]
`--memory p-1` at m1: p-1's only tick-11 line is `[obs p-1:11:1] [tick 11] You saw p-8 move from ENGINEERING to EAST_HALL.` (p-1 stood in ENGINEERING and saw p-8 leave). p-1's turn: `whereabouts tick 11 EAST_HALL; saw_player tick 11 p-8 EAST_HALL co_present p-1`. p-8's memory: `[obs p-8:11:2] You saw p-1 move from EAST_HALL to ENGINEERING.` (p-8 in EAST_HALL saw p-1 leave) -> p-8's turn: `whereabouts tick 11 ENGINEERING; saw p-1 in ENGINEERING`. Each read "You saw X move from A to B" as "I was in B with X". p-5*'s memory (adjacent vision) genuinely saw p-1 in ENGINEERING at 11 (true) but placed ITSELF in REACTOR (it was in EAST_HALL). Result: 6 strong flags, 3 on p-1 -> the most-flagged innocent is ejected. The `movement_perception` line has no "(you stayed in A)" clause and there is no per-tick "You were in X" trace. This is the single most damaging information-design defect in the set.
- [V] `whereabouts` for the crew is a lottery: p-8 said "EAST_HALL 10-11" in m0 (correct) and "ENGINEERING 11" in m1 one tick later.
- [V] Nobody knows how old a body is: p-2 died t5, reported t12; p-6 died t18, reported t26 — the room reasons as if the kill was fresh (p-1 m0 "p-8 moving ... at tick 11 ... suspiciously close to the timeline"). A human sees a stale corpse.
- [V] Vent-witness observations are held: p-7 `saw_vent tick 14 p-3 MEDBAY` and p-8 `saw_vent tick 14 p-3 ADMIN` were not usable at m1 (t13) and were spoken only at t22. The crew FSM has no "witnessed vent -> go press the button" branch (`agents/tactical/crewmate_policy.py:30-38` — only SUSPICION_ACCUMULATED -> CALL_MEETING); p-7 finished `inspect_samples` first (t17) and took a 4-room route to the button.

### (b) Decisions
- m0: seven players pile on the reporter for "no alibi" — the reporter-exculpation text exists only in the vote prompt; speakers still herd. Then all SKIP.
- m1: wrong ejection with 0.85 confidences ("A man who claims he was in the barn when I saw him in the coop is just a fox in sheep's clothing" — p-5*, whose own whereabouts was also wrong and flagged).
- m2: correct; p-3's reply "I might be misunderstanding the mechanics, but I certainly didn't vent" — mild scaffolding voice ("mechanics"). p-5* corroborates the witness AND says his partner was elsewhere in the same breath, then SKIPs — incoherent partner play.
- m3: p-7 accuses someone for being far from the body; p-5* "you say you found the body, yet you claim to be miles away in the Cafeteria" (twists p-7's words); p-8's spoken husk. Herd/geometry reasoning: p-7 m1 "East Hall ... way too close to Medbay" — EAST_HALL and MEDBAY are not adjacent (`engine/maps/canonical_1.yaml:179-203`); no map is ever shown to the LLM (0 hits for adjacent/map/layout in prompts).
- m4: p-9's self-alibi wrong; p-8's opening re-litigates the tick-14 vent of the long-ejected p-3 (prompt rule "speak it FIRST ... even if you already said it at an earlier meeting").
- Duplicate stock rationales: p-5* "The smoke is too thick to see the culprit/fire, so I'll hold my horse and let the dust settle." (m0 and m3, near-verbatim); p-9 "Max suspicion 0.50. Below threshold. Skip." (pure machinery, m0).

### (c) Sim holes
- [V] Impostor inside a vent during a meeting (t12 `p-3*@MEDBAY:VENT(VENTING)` + `>>> MEETING meeting-0`), and it speaks as if in LABS.
- [V] Vent exit into a room with a crewmate present and out of a room with a crewmate present (t13 `crew_in_from(prev)=['p-7'] crew_in_to(now)=['p-8']`) — VENT_EXIT has no witness check (`impostor_policy.py:29-38`).
- [V] Two meetings on consecutive ticks (t12, t13) because a same-tick report was pre-empted; a body announced mid-meeting.
- [V] GHOST STALKING (repro_policy.py, matches recorded actions exactly): t24-t43 p-5's target list is `[('p-1','REACTOR',0,1.0), ('p-7','REACTOR',0,1.0), ...]` — p-1 was EJECTED at t13 but `_confirmed_dead_from_bodies` (`agents/tactical/impostor_policy.py:813-838`) only learns deaths from bodies it saw; the ejected p-1's last sighting (REACTOR, ~t13) scores 1.0 and wins the id tie-break for 30 ticks (`_STALENESS_THRESHOLD=30`, line 185). p-5 walks to REACTOR, `_target_colocated_now(p-1)` fails, falls to `_idle` -> pretend task in ENGINEERING -> next tick stalks REACTOR again. It stood in REACTOR alone with p-7 at t27, t29 (`p-5* sees players=['p-7@REACTOR:task']`) with cooldown 0 and walked out. p-1's sighting expired at ~t43-44; p-5 killed p-7 at t46. GLITCH; it explains the manifest's "ping-pong pathing 31 of 32 impostors" and most of the dead time.
- [V] p-9 idle in CAFETERIA t9-t38 (30 ticks) — the crew "return to hub and wait" rule (`crewmate_policy.py:41-49`).
- [V] Task redistribution: p-6 1.00->0.56 (t14) walks to REACTOR and dies there; p-7 1.00->0.63 (t18); p-8 1.00->0.62 (t46).

### (d) Watchability
Rewind: t11-13 (impostor sitting in a vent while a crewmate stands over the body he made; two meetings back-to-back), m1 (three people misplace themselves and the wrong one dies), t27-t30 (impostor and lone victim alone in REACTOR — and nothing happens). Boring: t27-t45 (19 ticks of a ping-ponging impostor and an idle cafeteria).

---------------------------------------------------------------------------------------------------

## SEED 32 — IMPOSTORS win at t57 (p-5*, p-6*; 5 meetings)

### Narrative
p-5* kills p-2 in REACTOR t5, vents to ADMIN t7 in front of p-1 (destination witness). p-6* kills p-3 in ENGINEERING t7 (alone with him after p-7 left), vents to STORAGE. p-1 walks to CAFETERIA and presses the emergency button at t10 with a true vent sighting. Meeting-0: p-1 "I caught p-5 taking a shortcut through the vents in ADMIN at tick 8" + `saw_vent` obs (flag `vent_sighting/strong` on p-5) — but p-1 also says "whereabouts WEST_HALL tick 8" and "completed_task tick 8 start_reactor in WEST_HALL" (a fabricated task; he was in ADMIN). p-5*: "you couldn't have seen me vent in ADMIN if you were starting the reactor in West Hall". p-6* amplifies ("look at the geometry"), then p-7, p-8, p-9 (crew) repeat "West Hall to Admin is impossible" (they are adjacent, `canonical_1.yaml:200`). p-1 is ejected 6-1 (WRONG) — p-4's own vote prompt showed `p-5: suspicion 0.80 (verified flag)` vs `p-1: 0.60 no flag`, and p-4 still voted p-1 ("A man can't be in two places at once"). The prompt's own rule "never side with an unverified counter-accusation over a verified flag" was overridden by rhetoric. p-6* also spoke "tick 6: body of p-2 in REACTOR" — a body nobody had reported (it stayed unreported until t25!) — unnoticed.
t12-13: p-4 walks into ENGINEERING as p-6 enters the vent -> `saw_vent` -> meeting-1 -> p-6 ejected (correct). t14-t40: 26 ticks in which p-7, p-8, p-9 idle in CAFETERIA (tp 1.00), p-4 does everything alone (STORAGE, REACTOR, MEDBAY), and p-5* ping-pongs ADMIN<->EAST_HALL/WEST_HALL stalking ghosts (repro: targets `[('p-1','ADMIN',0,1.0), ('p-3','ENGINEERING',0,1.0), ...]` — p-1 ejected t10, p-3 killed by the partner t7 and never seen as a body by p-5). Meeting-2 (t25): p-4 finds p-2's 20-tick-old body; the room spends the meeting on p-6's tick-13 vent (already ejected) and on whether p-4 was in MEDBAY or ENGINEERING at 13 (p-8/p-9 mis-cite tick 8 as 13) -> SKIP. t40-41: p-1's ghost sighting expires, p-5 goes to MEDBAY and kills p-4 (t41), vents. Meeting-3 (t44) SKIP; p-5 kills p-7 in MEDBAY t48 (p-7 inherited p-4's MEDBAY task, tp 1.00->0.46); Meeting-4 SKIP; p-5 kills p-8 t57 (p-8 inherited, tp 1.00->0.61). Parity.

### (a) Information
- [V] No map in the prompt -> "geometry" arguments are invented (m0). Combined with p-1's self-location error, the true vent witness looked like a liar.
- [V] Voters saw the flag on p-5 and the arithmetic (p-4's ballot prompt: p-5 0.80 vs p-1 0.60) and voted p-1 anyway: herd > machinery in this case (the reverse of s30 m1 where machinery > testimony).
- [V] The vent witness's own memory was correct (`obs p-1:8:1`); the fabricated `completed_task start_reactor` came from nowhere (p-1's tasks were MEDBAY/ADMIN/CAFETERIA).
- [V] p-8/p-9 at m2: `saw_player tick 13 p-4 MEDBAY` — true sighting, wrong tick (it was obs-tick 8). No flag fired (the sighting didn't match their record) — the detector correctly refuses hallucinated ticks; the humans at the table did not.

### (b) Decisions
- Impostor deception at m0 is the best in the set: p-5's counter is short, specific, and exploits the witness's slip; p-6 launders it as "geometry"; three crew repeat it; p-4 flips against his own turn-2 accusation. p-9's ballot rationale: "My records confirm p-1 departed Medbay at tick 7, rendering their claim ... geographically impossible" — false inference stated as record.
- m1: p-6*'s reply "let's look at p-7, who left Engineering at tick 7" and p-5*'s echo "I saw p-7 leave Engineering at tick 7 and disappear" — coordinated bus of a crew target; ignored because of the flag.
- m2-m4: pure SKIP fatigue; the accusations that exist are proximity guesses ("only living player with no alibi near body" — p-7 m3, correct target p-5, 0.5).
- Voice: p-9 "I must respectfully interject, for my records indicate..." reads like a clerk; fine but repetitive. p-6* m0 "Let's take a breath and look at the geometry here" — nice.

### (c) Sim holes
- [V] Undiscovered body persists 20 ticks (p-2, t5->t25) through two meetings; p-6* announced it at t10.
- [V] Ghost-stalk dead time t14-t40 (longest no-event stretch 15 ticks from t26); crew idle 26 ticks; the eventual three kills are the redistribution conveyor (MEDBAY x2, ADMIN).
- [V] p-6 vented as p-4 walked in (t12); the enter-guard uses last tick's co-presence.
- Emergency meeting called with two undiscovered bodies on the map (t10).

### (d) Watchability
Rewind: m0 (a truthful vent report is argued into an ejection of the witness — genuinely dramatic), t12-13 (instant justice on p-6). Boring: t14-t40 (a quarter of the game with three crew asleep in the cafeteria and an impostor pacing a hallway), meetings 2-4.

---------------------------------------------------------------------------------------------------

## SEED 33 — CREW win at t31 (p-1*, p-5*; 4 meetings)

### Narrative
p-5* loiters at spawn faking a task, kills p-7 in CAFETERIA at t4 (hub kill, alone). p-1* kills p-6 in STORAGE t5, vents to ENGINEERING at t7 INTO a room holding p-2 and p-9 (`crew_in_to(now)=['p-2','p-9']`... verbose t8: both see him). p-2 finds p-7's body in CAFETERIA t9-10 and opens with the vent -> two `vent_sighting/strong` flags -> p-1 ejected 5-0 (correct). p-8 also says "I was right there in Engineering at tick 8 with p-1 and p-9" — false (he was in ADMIN/WEST_HALL) — a testimony line absorbed as own memory. t16: p-5* kills p-3 in ADMIN as p-9 walks in; p-9 reports t17 and accuses p-5 (0.6). Meeting-1: p-4 and p-8 (crew) attack p-9 ("you're lying about venting p-1 ... I saw you in East Hall at tick 9"; "p-1 was standing plain as day next to p-2 and you, so that vent story is thinner than a pancake") — the crew turns on the truthful witness; p-2's turn opens with "[invalid accusation target 'p-1' dropped]"; SKIP 5-0. t25: p-2 finds p-6's 20-tick-old body in STORAGE; Meeting-2: p-4 and p-8 now accuse p-2 (the reporter) of "lying about the vent"; p-9's turn again starts with the husk; SKIP. t27 p-5 kills p-2 in STORAGE, vents STORAGE->ENGINEERING at t29 in front of p-4 -> Meeting-3 -> p-5 ejected. Crew win.

### (a)/(b)
- [V] Correct outcome, but every ejection was a vent exit/enter seen by an arriving crewmate; the two "walked in on the killer" reports (m1 by p-9) and p-2's genuinely sharp inference at m2 ("p-5 was doing tasks alone in Cafeteria around the time p-7 died" — TRUE, p-5 did exactly that) converted nothing.
- [V] Crew misreads the transcript: p-4 m1 believes p-9 claimed to have vented; p-8 m1 contradicts a vent he "confirmed" one meeting earlier. Testimony-as-content is being replayed as first-person memory ("I was right there in Engineering at tick 8").
- [V] Re-litigation: p-2 and p-9 speak the tick-8 vent of the ejected p-1 in m1, m2, m3 (prompt-mandated), each time producing the "[invalid accusation target 'p-1' dropped]" husk in free_text; the husk is rendered into other players' transcripts (`said: "[invalid accusation target 'p-1' dropped] Wait, hold on..."` appears in 7 of 10 prompts of m1).
- [V] p-5*'s ballot rationale at m0: "p-1 is my teammate. Skipping." (role in recorded text).
- Duplicate rationale: p-8 "The smoke is too thick to see the fire, so I'll hold my hand and let the chips fall where they may." verbatim in m1 and m2.

### (c)
- [V] Body p-6 undiscovered t5->t25 (20 ticks): STORAGE is a dead end nobody visits.
- [V] Vent exit into an occupied room (t7) — the policy blind spot that decides most games.
- [V] Kill as witness arrives (t16, p-9) — witness gets no `kill` sighting because his move applied after the kill.
- Shortest dead stretch of the impostor-win games (7 ticks) — because both impostors kept acting.

### (d)
Good pace (32 ticks, 4 meetings, both ejections earned). Rewind: t7-8 (impostor pops out of a vent into a room with two witnesses), m1 (crew mobbing the man who walked in on the murder). Boring: m2 (stale body, recycled vent talk).

---------------------------------------------------------------------------------------------------

## SEED 40 — IMPOSTORS win at t43 (p-6*, p-9*; 3 meetings)

### Narrative
p-9* loiters t-1..t3, hub-kills p-2 in CAFETERIA at t4. p-4 finds it t7-8, opens with "I saw p-9 in East Hall at tick 7, moving from the Cafeteria" (correct, 0.5); everyone else offers alibis; 4 WEAK flags on p-1/p-8 (self-stated alibi pairs); 8/8 SKIP. Nobody moves after the meeting: p-4 stays in CAFETERIA tasking; both impostors walk in at t9; p-6 kills p-4 at t10 with p-9 standing there ("others_in_room_now=['p-9']") — the reporter dies in the meeting room 2 ticks after reporting. p-1 finds him at t12-13 and opens "I saw p-9 and p-6 together in East Hall at tick 12" — accuses only p-9. Meeting-1: p-7 (crew) claims alibi "LABS ticks 4-13" (she moved at ~t10-12); p-3 truthfully saw her in MEDBAY at 12 -> strong flag; p-5's whereabouts also flagged (p-6*'s adjacent-vision sighting, correct); the vote splits 4 (p-7) / 3 (p-5); p-7 ejected (WRONG); the two impostors split their votes across the two flagged innocents. t16-19 p-9 kills p-3 in STORAGE (rejected first attempt t16 as p-3 left EAST_HALL), vents; p-1 finds the body t24-25. Meeting-2: no flags, but carried suspicion of p-9 (accused in every meeting) crosses 0.6 -> `gate leader p-9 0.75 passed True` -> p-9 ejected 3-0-2 (correct) — the only non-vent correct ejection in the set. p-5's ballot rationale: "[under-gate eject target 'p-1' redirected] Actually, the herd is wrong to vote p-9; p-1's instant report ... make them the real impostor" — the machinery rewrote p-5's ballot from p-1 to p-9 and left the husk. p-1 (reporter, still in STORAGE) is killed there by p-6 at t29 (never found: 14 ticks, nobody enters STORAGE); reactor sabotage; p-6 kills p-5 in MEDBAY at t43. Parity.

### (a)/(b)
- [V] Meeting-1 shows the crew's ejection is a coin flip between whichever innocents mis-answered roll-call; the accused impostor p-9 (correct suspect in the opening) is never in danger while flags exist on someone else.
- [V] Meeting-2 shows carried suspicion CAN convict without a flag — but only after three meetings of the same name and with the second impostor never touched.
- [V] p-6*'s m1 line "p-1, you claim Medbay but I saw you sprinting from East Hall to Cafeteria at tick 13" is TRUE (adjacent vision) — impostor testimony is the most accurate testimony at the table.
- [V] Cross-meeting inconsistency never flagged: p-6* claimed alibi "EAST_HALL ticks 1-8" at m0 (he was in ENGINEERING t1-6, seen there by p-5 who cited it in m1); flags are per-meeting only.
- [V] p-1's beliefs at m2 still carry `p-4: suspicion 0.54` (dead since t10) and `p-6: 0.40 (alibi: in EAST_HALL at tick 12 per p-6)` — a self-alibi by the impostor lowered a crewmate's suspicion of him.

### (c)
- [V] Reporter killed in the meeting room 2 ticks post-meeting because positions persist and impostors converge on the hub.
- [V] Body never found (p-1, STORAGE, t29->end); p-8 idle in CAFETERIA t15-t32.
- [V] Ballot rewrite husk in the recorded rationale.

### (d)
Rewind: t8-10 (the reporter is stalked and killed in the cafeteria by both impostors while the room he just addressed disperses), m1 vote split, m2 (deduction finally lands). Boring: t26-t42.

---------------------------------------------------------------------------------------------------

## SEED 45 — CREW win at t25 (p-8*, p-9*; 3 meetings)

### Narrative
p-8* kills p-2 in REACTOR t5, vents and EXITS into STORAGE (t7) where p-1 and p-7 are tasking -> both get `saw_vent`. p-9* kills p-3 in ENGINEERING at t8 the same tick p-1 and p-7 walk in: `p-1 sees players=['p-7@ENGINEERING:None','p-8@ENGINEERING:None','p-9@ENGINEERING:kill']` — TWO CREW EYEWITNESSES TO A KILL (id order: p-1/p-7 moved before p-9's kill resolved). p-1 reports at t9 with the killer still in the room. Meeting-0: p-1 opens with the p-8 vent (`saw_vent tick 8 p-8 STORAGE`) and says NOTHING about having watched p-9 kill p-3 one tick earlier, even though his memory's top lines are `[obs p-1:9:4] You discovered p-3's body in ENGINEERING.` / `[obs p-1:9:3] You witnessed p-9 kill in ENGINEERING.` — the crew output schema has no witnessed-kill observation type (allowed shapes: saw_player, completed_task, found_body, saw_vent, whereabouts) and the prompt says vent first. p-8 ejected (correct); p-9* walks. Ten ticks later p-1 finds p-2's old body (t19). Meeting-1: p-1 "I directly witnessed p-9 perform a kill in Engineering at tick 9" (0.95), p-7 "I saw p-9 kill in Engineering. p-1 is telling the truth." — no flag kind fires; instead a strong `alibi_vs_sighting` fires on crew p-5 (LABS vs WEST_HALL at 9). p-4's vote prompt: `p-5: suspicion 0.80 (flag)` vs `p-9: 0.65 no flag; carried/soft only`. Votes: p-9 x3, p-5 x3 -> SKIP. p-9* then kills p-1 (the eyewitness) in REACTOR t22, vents, and p-4 walks in as he exits -> Meeting-2 -> p-9 ejected. Crew win — despite, not because of, the protocol.

### (a)/(b)
- [V] Strongest evidence the game can produce (a witnessed kill by two crew) is (i) unspeakable as a structured observation, (ii) held a full meeting, (iii) outranked by a roll-call slip when finally spoken. Rendering also omits the victim: "You witnessed p-9 kill in ENGINEERING." (no "p-3").
- [V] p-9*'s reply at m1 is the standard "you were in Reactor reporting the body, so how did you witness a kill in Engineering?" — time-confused but it worked on p-4/p-6 who voted the flagged p-5 ("the verified flag proves p-5 lied about their location in turn 4, which is way worse than just following the herd against p-9").
- [V] Impostor private rationales: p-9 m0 "p-8 is my partner. Vote SKIP."; m2 "You claim I vented, but I killed p-1 myself; voting me is suicide, so I skip to survive." (role + kill confession in recorded text; spectator-visible).
- Voice: p-4's nervous ramble is characterful; p-5's "The story unfolds in the quiet hum of Medbay ... and then, and then" narrator-voice is odd at a table.

### (c)
- [V] Kill in front of two witnesses because the impostor's no-witness check is one tick stale and it acts last (highest id).
- [V] Vent exit into an occupied room (t7).
- [V] Reporter reports with the killer in the room (t9).
- p-6 idle CAFETERIA t14-t25; p-2's body undiscovered 14 ticks.

### (d)
Rewind: t7-t9 (a vent seen by two, a kill seen by two, in consecutive ticks — and the meeting mentions only the vent), m1 (two eyewitnesses lose 3-3 to a roll-call flag). Short and tense; the best crew game of the set even though the protocol nearly threw it.

---------------------------------------------------------------------------------------------------

## SEED 49 — CREW win at t13 (p-7*, p-9*; 2 meetings)

### Narrative
p-7* kills p-2 in ENGINEERING t4 (alone), enters the vent at t5 exactly as p-1 arrives (`crew_in_to(now)=['p-1','p-8']`; only p-1 is a witness by id order), and stays inside the vent t5-t6; p-1 reports at t6 with p-7 still in the vent under his feet. Meeting-0: `saw_vent` -> p-7 ejected 6-0 (while inside a vent). p-9* spoke "tick 5: body of p-2 in ENGINEERING" (adjacent vision self-tell) — unnoticed. t10 p-9 kills p-4 in MEDBAY, exits the vent into ADMIN at t12 in front of p-5 while p-6 walks into MEDBAY as the source-room witness -> two vent flags -> Meeting-1 -> p-9 ejected. 13 ticks. p-9's reply: "I might be misremembering the vent logs" (scaffolding-flavoured phrase).

### (a)-(d)
- The cleanest game: both ejections correct, no dead time, four crew never left their task rooms. Also the least "social": no deduction happened; both impostors were caught by the vent-exit/vent-enter blind spot. Watchable as a highlight reel, not as a mystery. Rewind: t5-6 (impostor hides in the vent while the body is reported over him).

---------------------------------------------------------------------------------------------------

## CROSS-GAME: recurring patterns

P1 [V] Ejections come from vents, not from deduction. 10/11 correct ejections were `vent_sighting/strong` flags: 5 were vent EXITS into an occupied destination room (s31 t13, s33 t7, s33 t29, s45 t7, s49 t12), 2 were vent ENTERS as a crewmate arrived (s32 t12, s49 t5), 3 were exits 'seen' from the source room by a crewmate arriving that tick (s30 t30, s45 t24, s31 t13 p-7). The impostor FSM's VENT_EXIT has no witness check (`impostor_policy.py:29-38`) and the enter-guard is one tick stale. Meanwhile "I walked in and the killer was alone with the fresh body" (s30 m1, s33 m1) and "I watched p-9 kill" (s45 m1) convert to nothing.

P2 [V] Roll-call is a hallucination lottery that decides who gets ejected. Rendered memory never states the agent's own room per tick; "You saw X move from A to B" is read as "I was in B"; impostors (adjacent vision) misplace themselves too. Every strong `alibi_vs_sighting` flag in the set was on an innocent (s30 m3 p-7; s31 m1 p-1, p-8; s31 m4 p-9; s40 m1 p-7, p-5; s45 m1 p-5; s32 m0 p-4) except s31 m1 p-5* (unpunished). All 4 flag-driven ejections were wrong.

P3 [V] Ballots track the machinery, not the room, except when rhetoric beats it the wrong way. All-SKIP meetings (10/26) are those with no strong flag; rationales quote "threshold"/"no flag". The one time the room overrode the arithmetic (s32 m0) it ejected the truthful vent witness at the impostors' urging.

P4 [V] The impostor tactical policy chases ghosts. `_confirmed_dead_from_bodies` learns deaths only from bodies the impostor itself saw; ejected players and the partner's unseen victims stay kill/stalk targets for 30 ticks and win the id tie-break; the policy never invalidates a stale sighting on arrival, so it ping-pongs (s31 p-5 t23-t43 with a lone victim in the room at t27/t29; s32 p-5 t14-t40; s30 p-6 t14-t24 stalking p-2 who died at t9). This is the source of the long dead stretches (15/11/15/10 event-free ticks in s30/31/32/40) and of most of the manifest's ping-pong count.

P5 [V] Post-meeting geography is unreset and lethal in a predictable way: reporters resume tasking at the body's room and die there (s30 p-4 t35, s40 p-1 t29, s40 p-4 t10 in the meeting room itself); redistributed tasks (tp drops after each death) send the last crew one at a time into REACTOR/MEDBAY/STORAGE where the impostor waits (s30 t28/t35/t42; s31 t18; s32 t41/t48/t57). Endgames read as a conveyor belt.

P6 [V] Bodies persist across meetings and are found 8-20 ticks stale (s31 t26, s32 t25, s33 t25, s45 t19); the crew argues about them as if fresh; no body-age is exposed. Some are never found (s40 p-1 14 ticks; final kills).

P7 [V] Impostor self-tells are free: adjacent-vision "found_body" observations spoken pre-report (s30 p-3 twice, s32 p-6, s49 p-9), wrong self-placements (s30 p-3 x2, s31 p-5), cross-meeting alibi drift (s40 p-6) — none flagged, none noticed. Conversely impostor SIGHTINGS of others are the most accurate at the table (adjacent vision) and are used to flag innocents (s31 m4, s40 m1).

P8 [V] Held evidence: witnessed vents wait for the walk to the button (s31 p-7 8 ticks, p-8 never); a witnessed kill has no observation type and is spoken a meeting late (s45).

P9 [V] Scaffolding leaks: "[invalid accusation target 'p-N' dropped]" in spoken free_text (s31 m3, s33 m1, s33 m2), rendered into others' transcripts; "[under-gate eject target 'p-1' redirected]" ballot rewrite (s40 m2); "vent logs" (s49); duplicate stock rationales ("The smoke is too thick to see the fire..." s31/s32/s33x2/s40; "Max suspicion 0.50. Below threshold. Skip."); private impostor rationales naming partners/kills. Persona says "a hidden impostor" (singular) in every prompt of a 2-impostor game (51/51 in s32).

P10 [V] Crew idle at the hub for 8-30 ticks once tasks are done (s31 p-9 30 ticks; s32 three crew 26 ticks) — `crewmate_policy.py:41-49` return-to-hub-and-wait; combined with P4 the middle of impostor-win games is empty.

## Ranked findings (severity)
1. GLITCH — Impostor policy stalks ejected/unseen-dead players for 30 ticks and never invalidates a stale sighting on arrival (`impostor_policy.py:813-838`, `_STALENESS_THRESHOLD` line 185): idle impostor with cooldown 0 alone with a victim (s31 t27-t30), 15-26-tick dead stretches, ping-pong. Fix: fold meeting outcomes/ejections and roll-call deaths into the tactical dead-set; drop a sighting when you stand in its room and the player is not there.
2. DESIGN/GLITCH — Roll-call self-location has no ground truth in memory ("You were in X at tick t" never rendered; movement lines ambiguous). Produces every wrong ejection in the set. Fix: render a per-tick own-room trace (or a "you were in ROOM" suffix on movement/sighting lines) and validate `whereabouts` against it before it can be flagged as a lie.
3. DESIGN — Witnessed kill is not a speakable observation type and outranked by roll-call flags (s45 m1: two eyewitnesses lose to a flag on an innocent). Add `saw_kill` to the schema/contradiction vocabulary and weight it above alibi flags.
4. DESIGN — Meeting outcome = flag machinery (10 all-SKIP meetings; "walked in on the killer" never converts). Give same-room-at-discovery and "only person present at kill tick" a real evidence weight; let carried suspicion accumulate faster (s40 m2 shows it can work).
5. GLITCH — Vent witness/kill witness sets depend on player-id action order (`engine/tick.py:590-600`, `engine/rules.py:93,137-147`): s30 t30 p-4 sees p-6's exit but not p-3's; s45 t8 two witnesses to a kill only because the killer is p-9. Also an exit's source-room witness "sees" someone who was already invisible in the vent.
6. DESIGN — No post-meeting reset + task redistribution funnels reporters and last crew into isolated rooms with the impostor (s30, s31, s32, s40 endgames). Teleport all to CAFETERIA after meetings and/or let dead crew's tasks vanish or be done in company.
7. DESIGN — Bodies persist across meetings with no age; stale-body meetings (20 ticks) with fresh-kill reasoning. Clear bodies at meetings (as Among Us does) or expose "found N ticks after death".
8. GLITCH — Impostor VENT_EXIT and stale enter-guard vent into/out of occupied rooms (all 10 vent-based ejections). Either intentional "tell" or a bug — currently it is the crew's only reliable win path, which makes the social layer decorative.
9. REASONING — Herd overrides evidence in the wrong direction (s32 m0 vent witness ejected; s33 m1/m2 crew mobs the reporter/witness) and invents geography (no map in prompt). Give the LLM the adjacency list; make the "verified flag" instruction bite in the ballot validator.
10. LEAKS/WORDING — husks in free_text and rationales, duplicated stock lines, singular "a hidden impostor", impostor "found_body" self-tells unflagged, private rationales confessing kills.

## Ideas that would make these games better
1. Own-room trace + `saw_kill` observation + map adjacency in every meeting prompt (information layer). Cheap, removes most wrong ejections.
2. Tactical dead-set from meetings: after each meeting, feed "ejected: X; body reported: Y" into both FSMs; invalidate stale sightings on arrival; add a "witnessed vent/kill -> go press the button now, drop the task" crew branch, and stop crew from parking at the hub (patrol high-traffic rooms or buddy up).
3. Post-meeting teleport to CAFETERIA + clear all bodies at a meeting + a short kill cooldown after meetings; make redistributed tasks land in rooms adjacent to other crew or let dead crew's tasks be removed from the pool.
4. Evidence weights: same-room-at-report and sole-present-at-kill-tick as hard evidence; cross-meeting alibi consistency flags (s40 p-6's ENGINEERING vs EAST_HALL); flag `found_body` claims that predate the report (s30 p-3, s32 p-6, s49 p-9) as an impostor tell.
5. Vent witnessing consistent with physics: an exit is visible only in the destination room; enter/exit witness sets computed after all moves resolve, not in id order.
6. Ballot hygiene: strip husks from free_text before rendering to others; keep the LLM's stated target or show the redirect openly; ban stock rationale strings; fix persona to "impostors" when num_impostors > 1.
7. Pacing: an impostor "pressure" rule when nothing has happened for N ticks (sabotage lights/reactor, or move toward the largest crew group), and an emergency-button prompt for crew who hold a vent sighting > 2 ticks.

Files: dumps and scripts under /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/w4-9p2i-random-b/ (sNN.txt, sNN.verbose.txt, anNN.txt, repro_policy.py, analyze.py, s30_m1_prompts.txt).
