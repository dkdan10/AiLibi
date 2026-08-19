# w7-corpus-9p2i — spectator review of six `replays/ml_corpus/9p2i` games

Reviewer stance: omniscient spectator, top-down. Source of truth = `watch.py --verbose` dumps
(tick lines, per-agent visibility), the raw JSONL (`llm_calls` prompts/responses, actions), and
`ReplayLoader.get_meeting_memory` renders. Code was opened only to explain observed behaviour and
is cited `file:line`. Tick convention: `watch.py` tick `tN` = engine tick; an agent's memory /
claim tick is **`tN+1`** (e.g. kill at watch t13 → "[tick 14] You discovered p-6's body"). I quote
watch ticks unless I say "obs tick".

Games watched end-to-end (all 9p/2i, Qwen3.6-27B, prompt set v3): **1008, 1028, 1061, 1089, 1111,
1144** (5,5,4,5,5,5 meetings). `--verbose` visibility read for all six; `--memory` reads for
p-9 & p-2 (1008), p-5 (1028), p-3 (1061), p-2 (1089), p-5/p-6 (1144). Scratch outputs in
`scratchpad/work/w7-corpus-9p2i/` (`watch-<seed>-verbose.txt`, `simfacts-<seed>.txt`,
`calls-*.txt`, `simfacts.py`, `dumpcalls.py`, `corpus_stats.py`).

Corpus context (150 games, raw JSONL pass): winners 106 CREWMATE_EJECT / 6 CREWMATE_TASKS /
38 IMPOSTOR_PARITY; 463 meetings → 302 EJECTED (248 impostor, 54 crew) / 161 SKIPPED.

---

## Game 1008 — IMPOSTORS win by parity, t51 (impostors p-2, p-4)

### Narrative
- **Act 1 (t0–13).** Everyone disperses; p-4* sits IDLE in CAFETERIA t-1..6 while p-1/p-9 task next to it (at t0–3 observers see it as `p-4@CAFETERIA:task`, i.e. the idle impostor renders as "tasking"; `None` from t4). p-2* and p-4* then pace together EAST_HALL↔ADMIN↔ENGINEERING (oscillation at t7, t9). At **t13 p-2\* kills p-6 in ADMIN with p-4\* in the room and p-5 + p-7 walking in the same tick** ("others in room now=['p-4*','p-5','p-7']; saw KILL action=['p-4*']; can see body=['p-4*','p-5','p-7']"). Both crew arrivals see the fresh body and the two impostors, not the act.
- **Meeting-0 (t14, reporter p-5): 8/8 SKIP.** p-5's opening blames p-7 ("p-7 is the one who was alone in West Hall just one tick prior") — p-5 was WITH p-7 in WEST_HALL at t12; its memory line `[tick 13] You saw p-7 in WEST_HALL.` has no `(with …)` because the observer is never listed, and the LLM read that as "alone". p-3 and p-8 then brand p-5 a liar; p-8's "I also saw p-5 and p-7 together in West Hall at tick 13" is **fabricated** (p-8 was alone in REACTOR t12–14; its memory has no tick-13 sighting at all — it parroted p-3's turn). p-2*/p-4* both open with the self-tell "I was in Admin with p-4 when the body was found" / "I saw p-6 in ADMIN at tick 13" and nobody notices that the two players standing over the corpse are the obvious suspects. Ballots: every voter SKIPs, several literally citing arithmetic ("The maximum suspicion is 0.50, which falls below the 0.60 skip threshold" — p-9).
- **Act 2 (t15–18).** No cafeteria reset: at t15 p-7 is in EAST_HALL with p-4*, p-1/p-5 in ADMIN. **t16 p-4\* kills p-7 in EAST_HALL 2 ticks after the meeting.** p-1 walks in at t17, reports t18. Meeting-1: p-1 correctly fingers p-4 ("I saw p-4 moving out of EAST_HALL into ADMIN at tick 18"), p-2* even seconds it (bus), p-1 votes p-4, **6 others SKIP** ("The highest suspicion is 0.55, below the 0.60 threshold").
- **Act 3 — the STORAGE conveyor belt (t20–42).** Dead crew's tasks are re-dealt to living crew (`engine/tick.py:314 redistribute_dead_tasks`; visible as tp drops 1.00→0.67 for p-1 at t13, 1.00→0.60 for p-3 at t22, 1.00→0.72 for p-5 at t31, 1.00→0.81 for p-8 at t38). The inherited task is `fuel_reserves` in STORAGE, so one after another a lone crewmate walks to STORAGE and dies there: p-1 (killed t22), p-3 (reports p-1 at t26, comes back for the task, killed t31), p-5 (reports p-3 at t35, **stays in STORAGE doing the task at t36–37, killed t38**), p-8 (reports p-5 at t42, finishes fuel_reserves t43, inherits `upload_logs`, killed in ADMIN t51). After each kill p-2* vents STORAGE→ENGINEERING (t23/24, t32/33, t39/40) — three times a crewmate arrives in ENGINEERING on the very exit tick and never sees it. p-9 finished its tasks at t8 and sits IDLE in CAFETERIA t9–26 and t31–44 (≈36 ticks).
- **Meeting-2 (t26)** ejects p-4* — correct, but on a movement hunch ("shuttling between Engineering and East Hall"), i.e. the FSM's pacing itself is the tell. p-4*'s reply busses its partner in free text ("p-2 was busy playing hide-and-seek in the vents at Engineering") but files no `saw_vent`, so it has zero mechanical weight and nobody follows up. p-2* claims "I was in Storage when the alarm hit, right next to p-3" (false: EAST_HALL at t26) — the reporter p-3, who was alone, does not contest it.
- **Meetings 3–4 (t35, t42): 4 then 3 alive, all SKIP** ("The evidence is too thin"). p-2* is inconsistent across meetings (whereabouts tick 29 = ENGINEERING in m3, = STORAGE in m4; truth EAST_HALL) — never flagged. p-2* kills p-8 at t51 → parity.

### (a) Information gathering
- Voters' memory is a flat, salience-sorted list of `You saw X in ROOM` lines. p-9's render at meeting-2 is ~80 lines, 30+ of them "You saw p-1/p-3/p-5 in CAFETERIA" one per tick, plus eight tick-0 lines each listing all 8 players. Rich in bytes, poor in structure; a human would compress it to "p-1 with me t1–14".
- **No self-location track**: memory carries no "you were in ROOM at tick N" (only `You completed T (you were in ROOM)`); confirmed by grep over all dumps and `agents/memory/store.py:1195` (only the task line). The prompt nevertheless demands a roll-call `whereabouts` "copied from your own record". p-8, alone in REACTOR t12–14, answered `whereabouts tick 14 WEST_HALL` — invented.
- Impostors see their room + adjacent rooms; crew see only their own room (`engine/visibility.py:96-125`, Task 13.8). p-2* in EAST_HALL at t14 sees CAFETERIA, ADMIN (with the body) and ENGINEERING; p-5 in WEST_HALL at t12 cannot see ADMIN next door. Crew get "footprints" instead: `[tick 13] You saw p-5 move from MEDBAY to WEST_HALL` (movement_perception).
- Testimony does enter memory, as `[tick 19] [meeting] CLAIM by p-1 (unverified): saw p-4 in EAST_HALL @ tick 15 (with p-2).` and into beliefs as `alibi: in ADMIN at tick 14 per p-5`, but only a subset (p-9's meeting-2 render carries 6 CLAIM lines from meeting-1 and none from meeting-0). Prior ballots/rationales are never shown.
- The ballot prompt lists numeric `suspicion` per player, but for p-5 at meeting-0 only p-1, p-3, p-7, p-9 appear — the two impostors it found standing over the body are absent from the list.
- No map/adjacency information anywhere in any prompt (grep "adjacent|map|layout" over `calls-*.txt` → nothing but the vent-mechanic sentence).
- Things a human would obviously know that agents don't: who was in the room when you walked in on the body (it is in memory as separate lines, but not linked to the discovery); who reported which body earlier; how people voted last meeting; that ADMIN and EAST_HALL are one step apart; where *you* were.

### (b) Decisions
- Openings: p-5 (m0) accuses on a misread; p-1 (m1) is grounded and right; p-3 (m2) grounded ("p-4 shuttling") and right by luck; p-5 (m3) and p-8 (m4) accuse whoever was last co-present with the victim.
- Replies rarely answer the accusation; the standard move is to counter-accuse the accuser (p-7 → p-5 in m0, p-4* → p-1 in m1, p-8 → p-5 in m3).
- Ballots: herd in speech, threshold in vote. Meeting-0: five speakers accuse p-5, everyone SKIPs. Rationales leak scaffolding: "below the 0.60 threshold", "the §4.6 reference point" language.
- Impostor play: p-2*/p-4* coordinate on the reporter (both accuse p-5 in m0) — decent; but both self-tell "I was in Admin with p-6 at tick 13" (m0), p-4* busses p-2 (m2), p-2* changes its own tick-29 whereabouts between m3 and m4.
- Hallucinations [VERIFIED]: p-8 m0 tick-13 WEST_HALL sighting; p-8 m0 `whereabouts 14 WEST_HALL` (was REACTOR); p-2* m2 "in Storage next to p-3" (EAST_HALL); p-2* m3 "in Engineering at tick 29" (EAST_HALL).
- Wording: persona says "a hidden impostor kills crewmates" (singular) in every prompt of this 2-impostor game; the impostor's own persona too. p-4*: "when the lights went out on p-6" — no lights sabotage happened (figure of speech, but misleading to listeners).
- Endgame: meeting-4 has 3 alive (p-2*, p-8, p-9); both crew SKIP; the next kill ends the game. No agent reasons "skip = lose".

### (c) World-sim holes
- Kill in front of two arriving witnesses + partner at t13 (they see the body, not the act — arrivals never see the action of the tick they enter on; also true for vents at t24/t33/t40).
- No cafeteria reset after meetings; players resume from where they stood (t14→t15). Reporter left alone at the scene (p-5 in STORAGE t36–37) and killed there.
- Kill cooldown is 4 ticks (`engine/maps/canonical_1.yaml:34`) and not reset by a meeting: t16 kill two ticks after m0.
- Both p-5 and p-7 issue `report` on the same tick (raw t14) — first wins, harmless.
- Body cleared at report; not visible again. Bodies of unreported victims persist (see 1061/1144).
- Idle: p-9 idle in CAFETERIA 36 ticks; p-3 t16–22, p-5 t21–26, p-8 t31–38 idle in CAFETERIA. Task redistribution then sends them out alone. 25 of 53 ticks have no event.
- Impostor FSM oscillation (p-2*/p-4* at t7,9,22,26) is what crew read as "shuttling".
- Reactor sabotage at t25 during the report tick and at t44 with two crew left; repaired by walking to ENGINEERING; no gameplay effect except moving people.

### (d) Watchability
Rewind: t13 (two impostors + two crew converge on the ADMIN kill, then 8/8 skip), t22–42 (four deaths at the same STORAGE task), t26 (right ejection, wrong reason, partner bus). Boring: t43–50 (p-9 idle, p-2* wandering), the eight tick-0 memory lines in every prompt.

---

## Game 1028 — CREWMATES win by tasks, t52 (impostors p-1, p-5)

### Narrative
- t5 p-5* kills p-6 in EAST_HALL (p-1* watching from ADMIN). **The pair then paces EAST_HALL↔ADMIN past the corpse for six ticks** (p-1* oscillation starts 5,6,7,8,9; p-5* 5,6,7,8; body seen by both every tick t5–11). p-3 walks in at t10, reports t11.
- **Meeting-0 (t11): 8/8 SKIP.** p-3 reports "I saw p-1 and p-5 moving from East Hall to Admin right as I discovered the body". p-1* replies with an invented geometry claim ("p-3 was in Engineering at tick 10 and appeared in East Hall by tick 11, a movement too fast to be innocent" — adjacent rooms). p-5* seconds it ("a jump that defies the map's geometry"). **Five crewmates (p-2, p-4, p-7, p-8, p-9) all file `corroboration supports p-5` on the impossible-jump claim** — p-8: "Medbay with p-7. p-3's jump is fake. Vote p-3." Everyone SKIPs anyway. p-9 alone is sane: "You all claim p-3 teleported, but how do you know for sure?"
- **t12: p-1\* kills the reporter p-3 in EAST_HALL one tick after the meeting** — p-1* and p-3 both stood in EAST_HALL during the meeting; no reset, no cooldown reset (p-1* had never killed). Meeting-1 (t15) SKIPs 5–2 (p-2, p-4 vote p-1). p-5* files `found_body tick 13 p-3 EAST_HALL` — an impostor announces it saw the body two ticks before the reporter did and nobody asks why it did not report.
- t20 p-1* kills p-4 in ENGINEERING with p-5* watching; **t21 both impostors enter the ENGINEERING vent, t22 p-1\* pops out in STORAGE in front of p-2 and p-9** (saw vent action = p-2, p-9). p-2 finds p-4's body t24, reports t25.
- **Meeting-2 (t25): p-1\* ejected** on two `vent_sighting/strong` flags. p-1*: "your claim of witnessing a vent is factually impossible as I was in Engineering". p-5* muddles: files `corroboration supports p-9: p-9 witnessed p-1 vent` (bussing its partner) while accusing p-2 of "contradicting" the same sighting. Its ballot rationale: "I know the truth of our shared sabotage, so I cast my vote into the void."
- Act 3: p-5* alone; kills p-2 (t32, ADMIN) and p-7 (t44, ADMIN), venting to REACTOR each time. Meeting-3 (t35, 4 alive) and Meeting-4 (t47, 3 alive) both SKIP. In m3/m4 p-9 keeps re-filing `saw_vent p-1 tick 23` (p-1 ejected 10+ ticks ago) because the prompt orders "put a witnessed vent on record at every meeting"; its free text is prefixed **`[invalid accusation target 'p-1' dropped]`** — a diagnostic husk that is rendered verbatim into everyone's transcript ("How do you know p-1 is dead? They're the impostor"). p-5* exploits it ("p-9's claim about seeing a vent is a desperate fabrication… p-1 is dead"). Meeting-4: p-8→p-5 (correct), p-5*→p-9, p-9 SKIP ("The vent I saw was p-1, who is dead, so I have no proof for the living") → no ejection with 3 alive. Crew win on tasks at t52 while p-5*'s cooldown runs.

### (a) Information
- Impostor memory renders a partner's kill as `[tick 13] You discovered p-3's body in EAST_HALL` (p-5* saw it from ADMIN through adjacent-room sight) — the LLM then narrates it as a discovery.
- p-9's memory carries the p-1 vent forever; nothing marks it as "already used / subject ejected", and the rules force it to be spoken.
- The impostor prompt does name the partner ("Your fellow saboteurs: p-1 — never accuse or incriminate them"; "p-1 are your fellow saboteurs" — grammar), yet p-5* still corroborated the vent against p-1.

### (b) Decisions
- Meeting-0 is a case study in verbal herding on a fabricated "impossible move": five corroborations of a claim no crewmate could know, contradicted by no one because nobody has a map.
- Correct ejection (m2) came purely from a hard flag; both movement-based meetings (m0, m1) skipped although m1's speech had it right (p-1 named by p-2, p-4, p-9).
- Impostor deception: p-1*'s "impossible movement" line and p-5*'s "and then, and then" storyteller voice work as rhetoric; but self-tells: p-5* "found body at 13" (m1), p-5* seconding the vent on its own partner (m2). p-5*'s ballot rationales ("we impostors", "our shared sabotage", "p-1 is my teammate") are private, harmless in-game, funny to a spectator.
- Endgame: 3 alive at m4, crew split 1–1–SKIP; the impostor was one cooldown away from winning.

### (c) World-sim
- Two impostors idling/pacing next to a body for 6 ticks (t5–11) with no crew nearby — the FSM has no "leave the scene" drive.
- Reporter killed 1 tick after the meeting (t12) — corpus-wide 25 kills happen ≤1 tick after a meeting and **89 reporters are killed within 3 ticks of their own meeting** (`corpus_stats.py`).
- Two impostors vent from the same room on the same tick (t21) and one exits into a room with two crew (t22).
- Reactor sabotage at t26 (right after m2) and t37; crew fix by walking to ENGINEERING; no other effect.
- Idle: p-7 CAFETERIA t14–26, p-8/p-9 t31–37, p-9 t43–52. 25/54 dead ticks.

### (d) Watchability
Rewind: t5–11 (impostors pacing past the body), t11→12 (reporter dies one tick after speaking), t21–22 (double vent, witnessed exit), m4 (1–1–SKIP with 3 alive). Boring: t26–31, t38–43.

---

## Game 1061 — IMPOSTORS win by parity, t44 (impostors p-1, p-8)

### Narrative
- t5 p-1* kills p-7 in STORAGE, vents to ENGINEERING at t7 **in front of p-4** (saw vent action = p-4). p-4 walks to CAFETERIA and presses the button at t10 (`emergency reason=suspicion_accumulation`).
- **Meeting-0 (t10, emergency): p-1\* ejected 6–0–2** on p-4's `saw_vent` (strong flag). Everyone else "corroborates" p-4 with "I was in Admin/Labs, so I cannot contradict the vent sighting". p-8* (impostor) even says "p-1 is the impostor. p-4 saw the vent." and its rationale "p-1 is my teammate. Vote is wasted." p-8* files `found_body tick 9 p-7 STORAGE` (it saw the corpse from ENGINEERING) — an impostor announcing an unreported body; ignored.
- **The emergency meeting does not clear p-7's body** (`bodies at t+1: ['body-p-7-5']`). p-2, standing in STORAGE during the meeting, reports it at t11 → **back-to-back meetings t10/t11** (18 such pairs in the corpus).
- **Meeting-1 (t11): innocent p-6 ejected 6–0–1.** p-2's opening is a shrug ("p-4's path seems odd"). p-4 re-files the p-1 vent (dropped, `[invalid accusation target 'p-1' dropped]` prefix ×4 this meeting). p-6, who was in ADMIN with p-2/p-5 at obs tick 8 (and said so at m0), now files `whereabouts tick 8 ENGINEERING` + "saw p-1 in ENGINEERING with p-4" — parroting p-4's testimony as its own. p-5 (truthfully) places p-6 in ADMIN at 8 → `alibi_vs_sighting/strong` on p-6 → p-8* seizes it ("P-6 is lying… Vote P-6") → ejected.
- t14 p-8* kills p-2 in STORAGE, vents. p-3 finds the body t19, reports t20.
- **Meeting-2 (t20): innocent p-4 (the vent witness) ejected 4–0–1.** p-3's memory line `[tick 18] You saw p-4 move from EAST_HALL to CAFETERIA` (movement perception granted on *entering* EAST_HALL as p-4/p-5 left it; p-3 never had them in view — see visibility t16–17) becomes `saw_player p-4 EAST_HALL tick 18`; p-4 truthfully says `CAFETERIA 18-18` → **`alibi_vs_sighting/strong`** although both statements are true (a move A→B on tick 18). p-5 gets the same flag but the room herds on p-4 ("p-3's lie about p-4's location is the only hard evidence here" — p-8*). p-5's ballot carries `[under-gate eject target 'p-3' redirected]` — its p-3 vote was rewritten by the gate to p-4.
- Act 3 (t21–44): 3 crew + p-8*. p-5/p-9 idle in CAFETERIA t18–43; p-8* chases p-3 (kill attempts t28, t31 rejected because p-3 moved that tick), kills p-3 in LABS t38, vents. Meeting-3 (t42, 3 alive) SKIPs 3–0 ("Suspicions below threshold"). t44 p-8* kills p-9 → parity.

### (a)/(b) notes
- The right ejection (m0) needed one witnessed vent; both wrong ejections were "VERIFIED" alibi flags born from (i) a crewmate copying hearsay as first-hand + no self-location record, and (ii) the tick-boundary/footprint semantics of movement perception. The gate then treated the flag as decisive.
- p-8*'s deception is minimal but effective: pile onto whichever flag appears ("Vote P-6", "Vote p-4"), skip otherwise.
- Every meeting after m0 re-litigates the dead p-1's vent (p-4 ×3, p-9 ×2, p-6, p-3): "I must place on the record that I witnessed p-1 vent…" — prompt-driven.

### (c) World-sim
- Body persists through an emergency meeting → instant second meeting.
- 28/46 dead ticks; p-9 idle in CAFETERIA t16–43 (28 ticks), p-5 t18–38.
- p-8* oscillation start ticks 4,7,17,20,23,24,25.
- Sabotage: none by either impostor.

### (d) Watchability
Rewind: t7 (vent seen), t10–11 (two meetings in two ticks), t20 (the hero gets ejected on a bogus flag). Boring: t21–37.

---

## Game 1089 — IMPOSTORS win by parity, t64 (impostors p-1, p-3)

### Narrative
- t4 **p-3\* kills p-4 in CAFETERIA (the hub) four ticks in**; p-2 finds it t6, reports t7. Meeting-0 (t7): p-2 suspects p-1 ("p-1 was with p-4 at start"); p-1*/p-3* coordinate a nonsense counter ("You reported the body from Medbay, yet it was in Cafeteria") — p-3* self-tells "I was in the Cafeteria with p-4 until the lights went out" (no lights sabotage exists in this game). p-8 "must respectfully concur" with the nonsense; 8/8 SKIP.
- **t8 p-1\* kills p-5 in ENGINEERING one tick after the meeting** (they were together in ENGINEERING during it). t9–10 p-1* vents ENGINEERING→STORAGE **in front of p-8**. p-2 finds p-5, reports t11.
- **Meeting-1 (t11): p-1\* ejected 5–1–1**, but only via the machinery: p-8 files the vent; p-1*, p-3*, p-6 all say "p-1 was standing next to us in Engineering at tick 11, the vent is fabricated"; p-2 and p-6 vote **p-8** (the witness) and the hard-evidence gate rewrites their ballots to p-1 (`[under-gate eject target 'p-8' redirected]`); p-1*'s own redirected ballot lands on p-6. Without the gate the crew ejects the vent witness.
- t13 p-3* kills p-6 in ADMIN as p-8 walks in (p-8 sees p-3 + body); p-8 reports t14. **Meeting-2 (t14):** p-8 says exactly the right thing ("I saw p-3 enter ADMIN alone at tick 13"); p-2 answers "p-8 was in East Hall at 13, couldn't be in Admin at 14" (EAST_HALL–ADMIN are adjacent) and p-7/p-9 corroborate the "impossible travel"; 4/5 SKIP, p-2's p-8 vote redirected to p-3.
- **Dead middle (t15–43, 29 ticks):** p-3* paces EAST_HALL↔CAFETERIA t19–32 (14 oscillation starts) while p-7/p-8/p-9 idle in CAFETERIA t25–35 and p-2 tasks alone in LABS t19–27 (never approached). At t35 p-3* fires a reactor sabotage that pulls the three idle crew to ENGINEERING, follows p-2 to MEDBAY and kills at t44 — the sabotage used as a lure. p-7 (inherited MEDBAY task) reports t47, m3 SKIPs 4/4, p-7 keeps tasking alone in MEDBAY t48–52, second sabotage t53, p-7 goes to ADMIN, killed t61.
- **Meeting-4 (t64, 3 alive: p-3\*, p-8, p-9): innocent p-9 ejected 2–0–1 → parity.** p-8, who had been in CAFETERIA/EAST_HALL with p-9 for ~40 ticks, opens by accusing p-9. p-9's self-alibi `EAST_HALL 59–63` is wrong (CAFETERIA t59–63); p-3* truthfully saw p-9 in CAFETERIA at 60 → strong flag → p-8 votes p-9 ("their alibi is demonstrably false… I saw them in the Cafeteria" — p-8 was there with p-9!). p-3*: "let's eject the teleporter… Let's not get too hung up on the dead."

### (a)/(b) notes
- Absent map knowledge produced two "impossible travel" ejections-that-should-not-be (m2 speech, m4 flag).
- Testimony absorbed as CLAIM lines (p-2's m2 memory shows 14 CLAIM lines from m1) but not weighed against physical facts.
- p-8's m2 opening is the best single piece of crew reasoning in the set; it lost to a herd.

### (c) World-sim
- Hub kill at t4; kill 1 tick after m0; 40/66 dead ticks; impostor ignores a lone target 9 ticks running (p-2 in LABS) while pacing; sabotage-as-lure works.

### (d) Watchability
Rewind: t4 (hub kill), t8–11 (kill next to a witness, vent seen, gate rescues the vote), t35–44 (sabotage lure), t64 (p-8 turns on p-9). Boring: t15–34 (nothing), t48–60.

---

## Game 1111 — CREWMATES win by ejection, t57 (impostors p-1, p-8)

### Narrative
- t4 p-8*'s kill on p-7 rejected (cooldown/co-location), t5 p-1* kills p-7 in EAST_HALL with p-8* watching. p-2 & p-9 find the body t8, p-2 reports t9.
- **Meeting-0 (t9): p-1\* ejected 5–1–2.** p-2 opens on p-9 ("standing over the body"), p-9 counters p-2, six players pile on p-2 ("Vote p-2 out" — p-6). p-1*'s structured alibi is `EAST_HALL 6–9, evidence: ('killed p-7 at tick 6',)` — a written confession hidden by the transcript renderer (evidence lists aren't shown). What actually sinks p-1 is **its own partner**: p-8* files `saw_player p-1 WEST_HALL tick 8` under a `corroboration supports p-1` (!) → `alibi_vs_sighting/strong` ×2 → gate leader → 6 votes. p-8*'s rationale: "While p-1's timeline is broken, they are my partner, so I must hold back." Crew p-3 also self-places wrongly (WEST_HALL vs LABS at 9) and eats a strong flag and one vote.
- t11 p-8* kills p-3 in LABS, vents; p-2 reports t18; m1 SKIPs (p-8*'s reply is a fabricated timeline about p-2). t23 sabotage. **t30 p-8\* kills p-2 in REACTOR; p-4 reports t34, stays in REACTOR (inherited `start_reactor`), killed there t37**; p-5 reports p-4 at t41 (m3 SKIP), the same REACTOR loop. p-5 killed t54 in ADMIN.
- **Meeting-4 (t57): p-6 walks into ADMIN at t56 as p-8\* drops into the vent** (`p-6 sees ['p-8@ADMIN:vent']` + `vent_use_heard`), files `saw_vent`, 2–0–1 → p-8* ejected. Crew win.

### Notes
- Right outcome both times, both via hard flags; the two SKIP meetings (m1–m3) contained no usable physical evidence because every kill was 1-on-1 in a remote room.
- Impostor "bussing" here is not tactical, it is a semantic error: `corroboration` filled with a contradicting sighting.
- Idle: p-6/p-9 CAFETERIA t29–47; 34/59 dead ticks; p-8* oscillation t18–20.

---

## Game 1144 — CREWMATES win by ejection, t46 (impostors p-3, p-6)

### Narrative
- t5 p-3* kills p-2 in STORAGE, **t7 vents out into ENGINEERING in front of p-1 and p-4**; same tick t7 p-6* kills p-9 in ADMIN, vents to REACTOR at t9 (partner p-3* watches). p-8 walks in on p-9's body t9; its t10 `report` loses to p-1's emergency press.
- **Meeting-0 (t10, emergency): p-3\* ejected 5–0–2.** p-1 and p-4 file the vent. **p-6\* (impostor) says in free text: "p-3 didn't vent. I was in Admin killing p-9. p-1 is lying to save themselves."** — a full confession. p-8 notices ("p-6 just confessed to killing p-9 in Admin… I found the body myself") but files a 1.0 accusation that goes nowhere; the vent flag decides. p-5 (in CAFETERIA at t7–9) says "I was in Engineering at tick 8… I also witnessed p-3 vent" — fabricated, and repeated at m1, m2 and m3 ("I was in ENGINEERING at tick 8… I did not see p-1"; p-1 was there).
- Both bodies survive the emergency meeting; p-8 reports p-9's at t11 → **Meeting-1 (t11)**: nobody uses the confession (it never entered any structured claim, flag or suspicion number); p-8→p-6, five SKIP ("Max suspicion 0.65. Below threshold." — p-6* itself). p-4's persona rambles: "…even though p-3 is dead now, wait, no, p-3 is dead, so… oh, right, p-3 is dead".
- p-2's body (killed t5) is finally found by p-1 at t13 in STORAGE, reported t14 → **Meeting-2 (t14): innocent p-8 ejected 4–0–2** on `alibi_vs_sighting/strong` (p-8 said `LABS 8-8`, p-7 saw it arrive in MEDBAY at 8 — a one-tick self-placement slip). Meanwhile the table's speech was all about p-1 "standing silent next to a vent".
- **t16 p-6\* kills the reporter p-1 in STORAGE two ticks after the meeting** (p-1 stayed to do the inherited task). p-1's body lies in STORAGE **19 ticks** (t16–35) — nobody visits. p-6* paces t19–32; p-5/p-7 idle in CAFETERIA t21–43. p-4 finds p-1 at t34, reports t35 (m3: p-5 and p-7 turn on p-4 using p-5's fabricated tick-8 memory; 4/4 SKIP). p-4 stays in STORAGE, p-6* walks in t36, kill attempt t37 rejected (p-4 stepped out), kills p-4 in MEDBAY t43, **vents out into ADMIN at t45 next to p-7 while p-5 sees the action** → Meeting-4 (t46) p-6* ejected 2–0–1. p-6*'s rationale: "Vent claim is false. I killed p-4."

### Notes
- Two correct ejections, both vent flags. One wrong ejection, alibi flag. The one piece of decisive non-vent evidence in the whole set — a spoken confession — had zero effect.
- Corpus-wide: only 1 impostor free-text confession of a kill (this one), 11 "I vented"-style denials that echo the accusation, 18 "I killed" in private rationales.

---

## Cross-game patterns

1. **How ejections actually happen (corpus, 302 ejections):** impostor by witnessed vent 213; impostor with no flag 26; impostor via alibi flag 9; **crew via strong `alibi_vs_sighting` flag 50 of 54 crew ejections**. Movement/timeline deduction almost never ejects; a meeting either has a hard flag or SKIPs (161/463). In my six games: 29 meetings, 12 ejections (8 impostor: 6 vent, 2 movement; 4 crew: all alibi flags), 17 SKIPs.
2. **The self-location gap → fabricated roll-call → "VERIFIED" flag → innocent ejected.** Memory has no "you were in ROOM at tick N" line, the prompt demands one anyway, and single-tick `whereabouts` (`ticks 8-8`) dominate the 50 crew-flag ejections listed by `corpus_stats`. Seen first-hand: 1061 p-6, 1061 p-4 (footprint/tick-boundary variant), 1089 p-9, 1144 p-8, 1111 p-3.
3. **Hearsay recycled as first-hand.** p-8 (1008 m0), p-6 (1061 m1), p-5 (1144 m0–m3) each copied another speaker's sighting into their own `saw_player`, passing the citation gate because the ids "appear above" (in the transcript).
4. **No map knowledge → "impossible travel" rhetoric.** 1028 m0 (5 corroborations), 1089 m2 (3), 1089 m4 ("teleporter"), all between adjacent rooms.
5. **Threshold arithmetic overrides deliberation.** Rationales quote "0.60 threshold" 208 times corpus-wide; speech says "Vote p-3", ballots skip. In every 3-alive endgame I watched (1008 m4, 1028 m4, 1061 m3, 1089 m3/m4) crew skipped or split; no notion that a skip at 3 alive concedes.
6. **Reporter dies at the scene.** No cafeteria reset + no post-meeting cooldown + task redistribution sending lone crew back to the same remote room: 1028 t12 (1 tick), 1144 t16 (2), 1008 t38 (3), 1111 t37 (3); corpus 89 reporters killed ≤3 ticks after their meeting.
7. **Bodies persist across meetings** (1061, 1144): emergency meetings don't sweep the floor → back-to-back meetings (18 pairs corpus-wide) and 19-tick-old corpses.
8. **Impostor tells the FSM produces:** one impostor idles at spawn 4–7 ticks in all six games; pacing A↔B↔A for 6–14 ticks (1028 t5–11 past a corpse; 1089 t19–32; 1144 t19–32); crew explicitly read "shuttling/rapid movement" as guilt (1008 m2). Impostors also announce unreported bodies ("found_body" from adjacent-room sight: 1028 p-5*, 1061 p-8*).
9. **Scaffolding leaks into agent-visible text:** `[invalid accusation target 'p-N' dropped]` appears in free_text 137 times corpus-wide and is rendered into later transcripts; `[under-gate eject target … redirected]` in 48 rationales; "a hidden impostor" (singular) in every persona of a 2-impostor game; "p-1 are your fellow saboteurs".
10. **Dead time.** 25–40 dead ticks per game (no event), crew idle 20–36 ticks in CAFETERIA after finishing tasks; the mid-game of 1089/1144 has ~15–30 ticks where a spectator sees one impostor pacing and three crew standing still.

## Ranked findings (severity ↓)

1. **[VERIFIED, glitch/design] Crew self-placement is unsupported by memory, yet drives 93% of wrong ejections.** No self-location line; roll-call `whereabouts` is invented; the detector mints a *strong* flag on any single-tick mismatch; the gate + threshold make that flag decisive (1061 m1/m2, 1089 m4, 1144 m2 + 50/54 corpus).
2. **[VERIFIED, glitch] Movement-perception "footprints" become sightings in the wrong room.** `You saw p-4 move from EAST_HALL to CAFETERIA` (perceived on entering EAST_HALL, no line of sight) → `saw_player p-4 EAST_HALL tick 18` → strong flag against a truthful `CAFETERIA 18-18` (1061 m2 cost the crew the game).
3. **[VERIFIED, quality] Hearsay parroted as first-hand and accepted by the citation gate** (1008 p-8, 1061 p-6, 1144 p-5 ×4) — it both fabricates evidence and produces the flags in (1).
4. **[VERIFIED, design] Reporter/crew left standing at the crime scene after a meeting; kill cooldown not reset; redistributed tasks march lone crew back to the same room** → 19% of reporters die within 3 ticks (1028 t12, 1144 t16, 1008 t38, 1111 t37).
5. **[VERIFIED, quality/design] Free-text content has no mechanical weight.** A literal confession ("I was in Admin killing p-9", 1144 m0) and a partner bus ("p-2 … in the vents", 1008 m2) change no suspicion number; meanwhile "0.60 threshold" is quoted in ballots and 35% of meetings skip.
6. **[VERIFIED, design] No map/adjacency in prompts** → recurring "impossible travel" herds (1028 m0, 1089 m2/m4).
7. **[VERIFIED, glitch] Bodies not cleared by meetings** → back-to-back meetings (1061 t10/11, 1144 t10/11) and stale corpses (1144 p-1 19 ticks).
8. **[VERIFIED, believability] Impostor FSM tells: spawn idling, pacing past corpses, ignoring lone targets, venting into occupied rooms** (1028 t5–11, 1089 t19–32, 1144 t45).
9. **[VERIFIED, polish] Scaffolding/diagnostic text visible to agents and spectators** (`[invalid accusation target …]`, `[under-gate …]`, singular "hidden impostor", 8 tick-0 memory lines, per-tick "You saw X in CAFETERIA" spam).
10. **[JUDGMENT, quality] Endgame reasoning absent**: at 3 alive nobody reasons about parity; p-8 (1089 m4) accuses the crewmate who had been beside him for 40 ticks.

## Ideas

1. **Give every agent a self-track**: render "You: CAFETERIA t1–8 → EAST_HALL t9 → ADMIN t10–14 (alone t12–14)" and make `whereabouts` a menu over it; refuse/soften flags when the alibi tick is a move tick (treat `move A→B at t` as "in A and B at t").
2. **Make footprints honest**: render "as you entered EAST_HALL at t18, p-4 and p-5 were leaving toward CAFETERIA" and map it to a `saw_move` claim, never `saw_player … EAST_HALL`.
3. **Post-meeting reset + cooldown reset**: teleport everyone to CAFETERIA, reset kill cooldown to max, sweep all bodies (or at least all *known* bodies) at meeting end; forbid a kill for N ticks after a meeting.
4. **Ship a map card in the prompt** ("ADMIN ↔ EAST_HALL ↔ CAFETERIA…", travel = 1 tick per edge) and let the detector veto "impossible travel" claims mechanically.
5. **Let free text bite**: run a light extractor over free_text for confessions/vent claims/"I saw X kill", surface them as `unverified_claim` rows in beliefs, and show prior-meeting ballots ("last time p-5 voted you") in memory.
6. **Endgame prompt**: when alive ≤ 2×impostors+1, tell voters plainly that a SKIP hands the impostor the win on the next kill and lower the skip threshold.
7. **Rendering diet**: collapse per-tick sightings into spans ("p-1 with you in CAFETERIA t1–14"), drop the tick-0 roster dump, tag consumed vents ("p-1, ejected"), strip `[invalid…]`/`[under-gate…]` husks before they reach transcripts.
8. **Impostor FSM polish**: leave the room after a kill, avoid venting into a room where a crewmate is arriving, stop spawn idling (fake a task), pick lone targets; add a small chance to walk away from a corpse.
9. **Pacing**: shorten idle-after-tasks (send finished crew to "wander with someone" or to fix things), or end the game when all live tasks are done rather than redistributing into a solo death march.
