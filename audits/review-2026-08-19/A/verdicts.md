# Gameplay-track adversarial verification verdicts (12 claims)

**VERDICT: PARTIALLY-TRUE** — mechanism is a CONFIRMED-BUG; the 73.4% attribution is inflated.

**Reproduced exactly [VERIFIED]**
- Line-shape census over all 971 rendered memories in samples/9p2i: 41 distinct "You" shapes, and the *only* one placing the agent explicitly is `[tick N] You completed <task> (you were in ROOM).` (843 instances). No dated self-position line exists.
- Prompt does order it: `accusation_round.j2:184` — "naming the room you were in at the tick in question — one room, one tick, **copied from your own record**" (also `:209`, `crewmate_report.j2:96,:110`).
- Crew whereabouts false (room matches actual at neither tick N nor N-1): samples/9p2i **148/723 = 20.5%**, ml/9p2i **402/2038 = 19.7%**, samples/4p1i **7/78 = 9.0%**, ml/4p1i **11/79 = 13.9%**. Impostors 46–48%. Widening to ±2 ticks only drops 9p2i crew to 13.0% — not a tick-convention artifact.
- 79 CREWMATE ejections corpus-wide (claim's denominator, exact); **75/79 = 94.9%** carry an `alibi_vs_sighting` naming them (claim: 74/79).
- Exemplar s30 m3 p-7: memory holds only `[tick 26] You completed submit_scan (you were in MEDBAY)`; it answers `whereabouts MEDBAY@39` while it sat in CAFETERIA t32–t39; flag `alibi_vs_sighting/strong`, gate passes at 0.85, ejected 3-1, impostor p-3 votes with the crowd and wins by parity at t42. 4p1i s10 p-3 claimed `EAST_HALL@1` having never left CAFETERIA all game.

**Where the claim is wrong [refutes]** — I re-derived which side of each decisive contradiction was factually wrong:

| 79 crew ejections | n | % |
|---|---:|---:|
| victim's placement FALSE, sighting TRUE | **35** | 44.3% |
| both true — a one-tick transit | 23 | 29.1% |
| victim TRUTHFUL, the **sighting** was FALSE | **17** | 21.5% |
| no flag | 4 | 5.1% |

35+23 = 58 is exactly how the claim got 58/79, but the 23 are real corridor transits, not mis-statements. And 17/79 are the opposite bug — a truthful crewmate killed by a witness's mis-dated sighting. The claim's own exemplars **s12 m0 p-3 and s39 m0 p-1 fall in that bucket**, i.e. they contradict its causal story. Honest split: 44.3% victim-caused, 21.5% witness-caused.

**Mechanism confirmed.** For FALSE crew whereabouts the named room is the *most recent* completed-task room 47.1% of the time vs 22.0% for TRUE ones (2.1× enrichment); TRUE ones instead have a sighting line at that tick 58.0% of the time vs 22.7%. The model copies the one stale room it can see.

**Bonus defect [VERIFIED].** That one anchor is itself mis-dated: for all 843 lines the agent's real room matches at tick N only **16.0%**, at N-1 97.0%, at N-2 100%.

**Design/code.** Not intentional — `DESIGN.md:705` (§6.6 worked example) specifies *more* than shipped: `- [tick 380] You completed wiring_admin (you were in Admin tick 375-385)`, with a tick range. `agents/memory/store.py:1025-1028` already keeps `own_room_by_tick[event.tick]` per tick but only uses it to scope others' sightings; `store.py:1191-1197` emits the single line pairing `event.tick` with `last_pending_task_room` from the *previous* iteration (`:1205`) — hence the 16%/97% split, and no range. Task 16.7 (`tasks/phase-16.md:643`) assumes "a self-placement is almost an alibi claim"; only impostor self-placements are documented as lies (`audits/audit-phase-18-meeting-gate.md:68,:370`). The crew-side gap is unlogged.

**Impact.** Innocents are 79/435 = 18.2% of all ejections. Games with ≥1 innocent ejection end in an impostor win 39/68 = 57%, versus 14/132 = 11% without [counts VERIFIED; direction partly [JUDGMENT]]. Since the contradiction reaches voters as VERIFIED evidence, a crewmate that cannot read its own logbook is indistinguishable from an impostor caught lying, and the impostor wins by voting with the crowd. Cheapest fix: render the `own_room_by_tick` spans the store already holds, and re-label the completed-task line with the tick its room belongs to — no prompt change needed.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-1/report.md`

---

**VERDICT: CONFIRMED-DESIGN-CHOICE** (every number reproduces; the behaviour is a twice-ratified owner decision, already a P1 Phase-19 item — not an undiscovered bug). Scripts: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-2/{census,baseline,resolve,ground,impact,causal,both}.py`

**Census — 707 meetings, all 4 sets, 830 flag-subject rows** [VERIFIED]
| kind/sev | flags | dedup subjects | %impostor (dedup) | ejects subject |
|---|---|---|---|---|
| vent_sighting/strong | 440 | 348 | **100.0%** | 89.1% |
| alibi_vs_physical/strong | 37 | 30 | 100.0% | 83.3% |
| alibi_vs_sighting/strong | 234 | 192 | **17.2%** (samples/9p2i 4/47=8.5%; ml/9p2i 28/142=19.7%) | **47.9%** |
| alibi_vs_sighting/weak | 79 | 67 | 11.9% | 34.3% |
| alibi_conflict/weak | 35 | 35 | **0.0%** | 25.7% |

Random baseline (mean impostor share of living voters at those same meetings) = **25.3%**. 33/192 is *below* chance, binomial one-sided p=0.0048; alibi_conflict 0/35 p=2.9e-5. **s3 vs s4 reconciled**: s3 counted strong-only, deduped by subject; s4 counted strong+weak, per-flag (9/76=11.8%, 37/233=15.9%). Both arithmetic is right.

**Framing verbatim** [VERIFIED] — present in **2543/2543** recorded `vote_ballot` prompts (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:100`): "Each flag below is VERIFIED evidence… An unverified counter-accusation that merely mirrors a flagged claim carries no weight; never side with one over a verified flag." Turn-phase prompts use a milder "Evidence, not verdicts:".

**Grounding** [VERIFIED] — `meetings/transcript.py:2170-2179` `_iter_sightings` yields *every* `SawPlayerObservation` unfiltered; `_detect_alibi_vs_sightings` (`:2379-2494`) never inspects the sighter's record. Resolving 170 resolvable sighting-sides against the sighter's own per-tick visibility: **63.5% were never perceived by that speaker at that tick** (28.8% not even ±2 ticks). Resolving all 234 against omniscient truth: 46 have a TRUE alibi and FALSE sighting (honest subject framed; only 4 impostors; 25 ejected), 108 subject-lied (only 13 impostors), 80 both-wrong. The flag detects LLM tick-bookkeeping noise, not deception. The grounding machinery **exists** (Task 16.7 `SightingRecord`/`grounded_vouch_subjects`, `transcript.py:159-181`) but is wired only to the *exculpatory* −0.05 vouch, never to the prosecutorial flag — that asymmetry is the bug-shaped residue.

**Design citation** [VERIFIED] — deliberate, twice. `tasks/phase-13.md:700` "**Owner decision (2026-06-22): LONE-STRONG.** A single-witness `alibi_vs_sighting` contradiction MAY cross the gate — relaxing the 'no single signal ejects' principle", over `audits/audit-2026-06-22-2149-wave-e-review.md:59` which blocked it and asked for a MID delta. Task 18.9 lever 1 (`transcript.py:2394-2418`) then promoted single-tick roll-call whereabouts too; `audits/audit-phase-18-baseline-6.md:324` §9.2 adopts the *exact* seed-17-m0 p-1 false positive knowingly. Already re-verified as P1 in `audits/audit-phase-19-triage.md` row 9 and `docs/reading-guide.md:196`.

**Two corrections to the claim** [VERIFIED] — (1) The exemplar shape (alibi flag beating a co-present vent flag) is the *tail*: of 77 meetings carrying both, the vent flag wins 70, alibi wins 5 (seeds 17, 4p1i-41, ml 1099/1121/1140 — all 5 ejected crewmates). (2) The real damage is the **sole-flag** case: 82 meetings whose *only* strong flag is `alibi_vs_sighting` → **77 ejections (93.9%), 77/77 landing on a flag subject, 65 of them crewmates (84.4%)**, versus 306 no-strong-flag meetings → 42 ejections (13.7%). Corpus-wide, **70 of 79 wrong ejections (88.6%) carried a strong `alibi_vs_sighting`, and in all 70 it was the only strong flag on the victim**. As sole convicting evidence: 12 right / 70 wrong = **14.6% precision**, against `vent_sighting`'s 310/316.

**Impact (3 sentences).** The one high-precision evidence channel the game has (engine-certified vent sightings, 440/440) shares a prompt block, a severity stamp and a "VERIFIED evidence" label with a channel that is *anti*-informative — worse than guessing — and that channel single-handedly flips a meeting's ejection rate from 14% to 94% while steering it onto an innocent five times out of six. Concretely, in `replays/samples/9p2i` seed 17 m0 the truthful vent witness p-1 is ejected 7-1 (p-8: "This verified contradiction proves p-1 is lying") while the correct flag naming impostor p-2 sits two lines above it in the same prompt, and seed 23 m1 / seed 8 m4 both hand IMPOSTOR_PARITY wins to the impostors off a single such flag. Believability cost: the crew's deliberation reads as competent right up to the moment it convicts the one person who actually saw something, because the label promises verification the detector never performed.

---

**VERDICT: CONFIRMED-BUG** (unintended interaction; not a sanctioned design choice)

**Prevalence** [VERIFIED] — every `You completed X` line in every committed replay's rendered memory, matched against replayed `task_completed` events. Calibration: all 520 true lines sit at `memory_tick = event_tick + 1` exactly, so "false" = no completion event at any tick < T.

| set | games | lines | FALSE | % | games hit | spoken at table |
|---|---|---|---|---|---|---|
| samples/9p2i | 50 | 529 | 53 | 10.0% | 36/50 | 16 |
| samples/4p1i | 50 | 65 | 15 | 23.1% | 15/50 | 5 |
| ml_corpus/9p2i | 150 | 1528 | 140 | 9.2% | 94/150 | 39 |
| ml_corpus/4p1i | 50 | 64 | 14 | 21.9% | 14/50 | 7 |

**Redistribution correlation is 100%, not merely enriched.** Of the 65 false lines in `samples/`, 58 have a crewmate KILL at T−1/T−2 and the other 7 have a meeting EJECTION at T−1 (s11 t14, s12 t8, s17 t7, s18 t22, s32 t11, s39 t9, s46 t18) — both paths call `redistribute_dead_tasks`. True lines: only 154/479 (32%) have a nearby death.

**Exemplar (9p2i s2, p-1 CREWMATE).** `do_task submit_scan` t2–t4; t4 `kill p-7→p-2` (p-2 mid-`empty_trash`); t5 `task_completed` fires for p-3 and p-5 only, p-1 is `MOVING`. Memory still shows `- [obs p-1:5:0] [tick 5] You completed submit_scan (you were in MEDBAY).` and p-1 opens meeting-0 with obs `{'type':'completed_task','tick':5,'task_id':'submit_scan','room':'MEDBAY'}` + *"I was busy with my scans in Medbay with p-3 and p-9."* `empty_trash` < `submit_scan` — the inherited instance displaced the pending id.

**Three false lines manufactured STRONG flags against innocents:**
- s11 p-6: false `upload_logs@14 MEDBAY` → *"I was locked in Medbay completing tasks at ticks 13 and 14"* → `[alibi_vs_sighting/strong] Alibi places p-6 in MEDBAY (14-14); sighting reports p-6 in WEST_HALL at tick 14.`
- s46 p-1: false `fuel_reserves@10 ADMIN` → strong flag vs. EAST_HALL sighting.
- s13 p-5: false `fuel_reserves@14 LABS` → strong flag vs. MEDBAY sighting.
Plus verbatim alibis built on nothing: s14 p-2 *"I must place myself firmly in ADMIN…, having completed the upload logs task."*; s47 p-4 *"I was in ADMIN until tick 14, completing logs."*

**Design check — refutation failed.** `DESIGN.md §3.5` scopes the dead-crewmate rule to win conditions only; `engine/maps/canonical_1.yaml:45` sets `dead_task_rule: redistribute`; `audits/audit-2026-06-24-1840-gameplay-data.md` audits that flip for win paths + firewall only. `DESIGN.md:705` and `tests/fixtures/memory_rendering/crewmate_basic.expected.md:7` pin the line's format presupposing truth. No phase ruling permits fabricated self-memory — the opposite: `agents/memory/store.py:1170-1177` warns fictitious completions "could become a fabricated `completed_task` alibi and corrupt the meeting/eval evidence (PR #155)".

**Code.** `agents/memory/store.py:1161-1166` justifies the inference on "Its owned set only ever shrinks — a task completes; none is added mid-game — so the pending id changes if and only if the previous pending task completed." That premise is false: `engine/tick.py:365-366` `surviving_tasks[new_id] = replace(task, id=new_id, owner=recipient)` (also from `orchestrator/game.py:1234-1239` on ejection) adds an instance mid-game, and `observation/service.py:592-612` picks the *lexicographically-first* owned unfinished map id — so an inherited earlier-sorting task flips `pending_task_id`, and `store.py:1178-1197` mints a completion for the merely displaced task. No positive check on `task_completed`/`crew_tasks_done` exists.

**Secondary** [VERIFIED]: (a) a uniform +1-tick stamp on all 520 true lines, so cited alibi ticks are systematically late; (b) the `role == "CREWMATE"` gate means only crewmates are poisoned — the bug is strictly one-sided; (c) the room comes from `last_pending_task_room` (previous self_state), which is what makes false lines collide with truthful sightings.

**Impact.** 10% (9p2i) to 22% (4p1i) of a crewmate's remembered work is fabricated, in 159/300 committed games, minted precisely on the tick a teammate dies — the exact window the next meeting litigates. Crewmates swear these phantom tasks as alibis (21 spoken instances in `samples/`), and because the room is invented too, the crew's evidence channel manufactures STRONG "VERIFIED evidence" contradiction flags against its own innocents while impostors are gated out of the inference entirely.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-3/REPORT.md`

---

**VERDICT: PARTIALLY-TRUE** — the observations reproduce, but two of the three are documented design, and one number is wrong.

**1. "No gather" — [VERIFIED] but CONFIRMED-DESIGN-CHOICE.** All-living-in-CAFETERIA: 0/39, 0/165, 0/40, 3/463 — the claim's counts exactly. Mean CAF share @T 0.27, lower @T+1 in all four sets. Two extra controls I added: CAF share at meeting ticks 0.2695 (n=707) vs 0.2881 at non-meeting ticks (n=7011) — meetings are *less* cafeteria-heavy than baseline; and 87.6% of agents are in the same room at T as at T-1. `DESIGN.md:473` §5.1 step 1: "Freezes engine state (no movement, no kills, cooldowns paused)"; `DESIGN.md:275` "returns control to tick t+1". No doc anywhere promises a gather, and the meeting prompts carry no physical framing at all (no room field, no "you are gathered" — `agents/strategic/prompts/qwen3_6_27b/*.j2`). The meeting is deliberately an abstraction over the alive-set.

**2. "Cooldowns not reset" — [VERIFIED], and it is a documented PAUSE, not an oversight.** `kill_cooldown_ticks: 4` (`engine/maps/canonical_1.yaml:34`). Consecutive same-impostor kill gaps, bucketed by meetings strictly between: 0 meetings → n=43, min 5; 1 → n=188, min 6; 2 → n=78, min 7; 3 → n=13, min 9. Each interposed meeting shifts the floor by exactly +1, i.e. the meeting tick consumes a tick number but does not decrement. `engine/tick.py:57` `_decrement_cooldowns` is only reachable from `advance_tick` (line 607); `orchestrator/game.py:1186-1190` states it outright — "cooldown / sabotage / emergency-uses counters are unchanged during the meeting tick because DESIGN.md §5.1 freezes engine state ('kill cooldown paused')". A reset would produce a gap of 1; nothing near that exists.

**3. Venting participants — [VERIFIED] CONFIRMED-BUG (believability).** 16/165 (9.7%) samples 9p2i, 50/463 (10.8%) ml_corpus 9p2i, 1/39 and 2/40 in the 4p1i sets; corpus 69/707 = 9.8%. Seed 2 t19: `[t 19] ... p-3@STORAGE:REPORT  p-7*@REACTOR:VENT(VENTING)  p-8@LABS:TASK  p-9@ADMIN:TASK` — and in that same meeting p-7 takes turn 1 ("Stop chasing ghosts, p-3...") and votes `p-7* -> SKIP conf=0.4`. Nobody notes he is absent; the SKIP holds and the impostor survives. Cause: the roster is gated on liveness only — `orchestrator/game.py:1029-1031` (`if not player.alive: continue`), no room and no `in_vent` check, even though `in_vent` is surfaced to the spectator API at `api/replay_loader.py:1485`.

**4. "89 reporters killed within 3 ticks" — [VERIFIED] the phenomenon, [REFUTED] the number.** True value is **111/707 (15.7%)**, all from body-triggered meetings (within 1 tick: 11; within 2: 77; within 3: 111; within 4: 134). Per set: ml_corpus/9p2i 75/463, samples/9p2i 27/165, samples/4p1i 5/39, ml_corpus/4p1i 4/40. No slicing reproduces 89 (SKIPPED-only 69, EJECTED-only 42, 9p2i-only 102, samples-only 32, unique reporters 111). The claim understates by 25%.

Exemplars confirmed in the bytes: seed 2 meeting-0 @t7 — p-4* sits in STORAGE at t6 and t7 (through the meeting) beside p-6, then `[t 8] p-4*@STORAGE:KILL`, `EVENT kill: {'killer_id': 'p-4', 'victim_id': 'p-6', 'room_id': 'STORAGE'}`; neither moved. Seed 40 — reporter p-4 (meeting @t8) killed at t10 in CAFETERIA by p-6*, who had been standing there since t9.

**Impact.** The frozen-in-place meeting is internally coherent but plays as a teleconference, and it hands the impostor a free execution: whoever they were standing next to when the meeting fired is still there at t+1 with a fresh 4-tick window, which is why 15.7% of reporters die within 3 ticks of the meeting they themselves called. The venting participant is the sharper break — one meeting in ten has someone deliberating from inside the one place the design treats as physically hidden, and no crewmate can perceive it, so the game's strongest tell is silently neutralised at the moment it would matter.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-5/REPORT.md`

---

Verification complete. All scripts are in `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-6/`.

**VERDICT: CONFIRMED-DESIGN-CHOICE** — the mechanic is real and intentional; every defect inference drawn from it is REFUTED.

**What reproduces exactly** [VERIFIED]
- Only the trigger body is consumed: across 4 sets, **478/478** body-triggered meeting boundaries removed **exactly one** body (|vanished| histogram `{1: 478}`); **0/47** emergency meetings removed any. Other corpses persist.
- Denominator **798 bodies**, **172 never reported (21.6%)**, **22 CAFETERIA survival-events** — all three match the claim exactly.
- Seed 8 meeting-0: 7 turns, 7 ballots, `grep -c "p-8"` = **0**. p-8 is genuinely never named.

**What is wrong** [VERIFIED]
1. **"invisible to crew (discovered_by=None)" is backwards.** `engine/visibility.py:93` — `if body.discovered_by is None and body.room in visible_room_set`. `discovered_by=None` is precisely what makes a body **visible and reportable**. Surviving corpses are live evidence, not ghosts.
2. **Seed 8's silence is correct fog-of-war, not a glitch.** The only agents who ever saw `body-p-8-4` were `t4 p-3 (IMPOSTOR)` and `t4–t8 p-5 (IMPOSTOR)` — the killer and his partner. CAFETERIA occupancy t5–t8 was `[]`. **Zero living crewmates had anything to say.**
3. **The claim's own seed-11 exemplar disproves it.** `body-p-4-4` lies in CAFETERIA t4–t13 with `crew_seers=[]` through both meetings; at t14 crewmate p-5 walks in and sees it; at t15 `report_body ... 'body_of': 'p-4', 'room_id': 'CAFETERIA'` → meeting-2. The corpse persisted *so it could be found later*, and it was.
4. **"98% in a room no crewmate re-enters" → 96.5%** (166/172), and that statistic *supports* fog-of-war rather than indicting it.
5. **"230/798 (28.8%)" is unreproducible.** Measured: **189/798 = 23.7%** unique bodies (247 boundary-events, 181 at body-meetings, 189 unique — none is 230).
6. **Zero real misses corpus-wide.** Of 172 never-reported bodies, only **6** were ever seen by a living crewmate, and all 6 have **gap=0** — first sighting on the game's final tick (e.g. `samples/9p2i seed39 body-p-5-34 first_crew_sighting=t34 ... game ends t34`). No crewmate ever saw an unreported corpse with time to act and stayed silent.
7. **The "meeting held in the Cafeteria" imagery is misleading.** Meetings are non-spatial: in **3/628** meetings were all living players in CAFETERIA; at meeting ticks they are spread across all 9 rooms (`ENGINEERING 344, MEDBAY 335, ADMIN 331…`). Nobody is standing over the corpse ignoring it.

**Design/code citation**
`orchestrator/game.py:1249-1259`, with the rationale in-comment: *"Consume the corpse that triggered a body-report meeting… so the trigger surface is the same as the observation surface."* The single `del bodies[triggering_body_id]` is deliberate and guards against an adversarial intent re-reporting the same body to spam meetings. Leaving other corpses on the floor with `discovered_by=None` is standard Among Us behaviour. `api/replay_loader.py:1389-1405` even documents the matching fog rule for a just-reported body.

**Real gameplay impact**
Essentially none, and what exists is positive: unreported corpses stay on the floor as live, findable evidence, and crew stay silent about them only because they genuinely have not seen them. The measured worst case is six bodies spotted on the final tick — no opportunity to report. The one item worth logging separately is not G-6 at all: in seed 8, impostors p-3 and p-5 "see" `body-p-8-4` in CAFETERIA *from EAST_HALL*, so cross-room body visibility deserves its own check.

---

**VERDICT: PARTIALLY-TRUE** — the mechanism is a real CONFIRMED-DESIGN-CHOICE; the headline statistic is REFUTED as a two-clock artefact.

**What holds [VERIFIED].** `FoundBodyObservation` carries exactly `type/tick/body_of/room` — no `died_at` (`meetings/schemas.py:76-82`, docstring "Body-discovery report tied to the meeting's trigger event"). Deeper: `BodyState` has no death-tick field at all (`engine/entities.py:43-49`); the kill tick survives only as an opaque string suffix in `body_id` (`engine/rules.py:78`), and that string reaches only the opening prompt (675/6892 meeting prompts = 9.8%, via `orchestrator/game.py:2455-2459` `"{actor} reported body {body_id} at tick {report_tick}"`). The memory line is stamped at discovery, not death (`agents/memory/store.py:1250-1258`). I reproduced G-7's histogram byte-for-byte across all 4 sets: N=963, 1→171, 2→134, 3→165, 4→181 … 30→1, min 1, median 4, mean 4.619, zero at 0.

**Design, not bug [VERIFIED].** DESIGN.md:549 specs `found_body` with a discovery tick only; DESIGN.md:703 specs the render. The prompts explicitly work around the absence: `agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:96` anchors the roll-call on "the tick that matters (**the tick it was reported to have happened**, or the tick under discussion)". No doc anywhere posits a time of death. This is a deliberate, documented anchor choice.

**What is REFUTED [VERIFIED].** The agent memory clock runs exactly **+1** vs the engine/replay clock: on 18,936/18,936 discriminating sightings (subject changed room between T-1 and T), `[tick T] You saw p-X in ROOM` matches the loader's room at T-1 — zero exceptions. G-7 compared agent-clock stamps against engine-clock kill ticks. Corrected (`obs.tick-1` vs kill tick): **min 0, median 3, mean 3.619, max 29, and 171/963 = 17.8% land EXACTLY on the kill tick**; zero impossible negatives confirms the correction. So "zero exact matches under both conventions" is false, and every figure quoted is inflated by 1. Both exemplars misread too: seed 2 m0's roll-call whereabouts sit at agent-tick 5 = **engine tick 4 = the kill tick itself**, not "the window after the killer left"; seed 21 m1's window is 15-20 engine, still 10 ticks past the t5 kill (that exemplar survives).

**What G-7 missed, and it cuts against it [VERIFIED].** A live eyewitness *does* get a true time of death: `[tick N] You witnessed p-X kill in ROOM` (`agents/memory/store.py:1367-1373`), 92 witnessed kills across the 4 sets, **86 (93.5%) alive at the next meeting**. But no meeting observation kind exists for it — the schema offers only `saw_player`/`completed_task`/`found_body`/`saw_vent`. samples/9p2i seed 26 m0 (kill engine t5, meeting t6): p-1 witnessed the murder, could only file `found_body @t6` + `saw_player p-3 @t5`, and the eyewitness account escaped solely as unstructured ballot text — "I watched p-3 kill p-8 myself" — where no detector or contradiction flag can reach it. That is the sharper finding: the death tick exists in memory and is **unspeakable at the table**.

**Real gameplay impact.** 82.2% of body reports still open an interrogation later than the murder (median 3 engine ticks, max 29), and in **116/621 body-triggered meetings (18.7%)** the entire spoken tick span never touches the kill tick — the table alibis a window the killer had already left. 79/621 (12.7%) debate a body whose killer was already dead or ejected; seed 21 m1 is the clean case (p-3 killed t5 by p-2, ejected at m0/t10, body reported t21, table argues ticks 15-20, skips). The corrective is not a `died_at` field on `found_body` — it is a `saw_kill` observation kind so the 93.5% of surviving eyewitnesses can put the murder moment on the record as structured evidence.

Scripts: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-7/` (`g7.py` histogram, `g7i.py` clock proof, `g7j.py` corrected histogram, `g7g.py` witness survival, `g7d.py` window coverage).

---

**VERDICT: PARTIALLY-TRUE** — every mechanism fact checks out and the deferral is a documented, owner-locked design choice; but "cannot become evidence for anyone but the witness" overstates it, and the real defect is a *starved* propagation path, not a missing one.

**What reproduced exactly [VERIFIED]**
- Observation shapes in the live recorded opening prompt (4p1i seed 22, p-3): `saw_player / completed_task / found_body / saw_vent / whereabouts`. No kill shape. Same 5 in p-2's opt-in prompt.
- Contradiction enum is 4 kinds, no kill kind — `meetings/schemas.py:454-456`.
- `You witnessed pN kill in ROOM` = **40 / 157,387** rendered memory obs-lines = **0.025%** (vs vent 844 = 0.536%). Matches the claimed 0.02%.
- Seed 22 verbatim: memory `- [obs p-3:7:1] [tick 7] You witnessed p-4 kill in CAFETERIA.`; p-3 speaks it only as free text + `accusation.reason`, structured obs are found_body/saw_player/whereabouts; `contradictions: []`; p-2's ballot prompt reads ``- `p-4`: suspicion 0.58 … this meeting +0.08 … — no flag; carried/soft only``, max 0.58 < threshold 0.60 → **SKIPPED**.
- Seed 45 m1: p-1 and p-7 both hold the t9 kill of p-3 by p-9; only flag is `alibi_vs_sighting/strong` on **innocent p-5**; 3-3 tie → SKIPPED. p-4's ballot: *"the verified flag proves p-5 lied about their location, which is way worse than just following the herd against p-9."* Impostor p-9 votes p-5 and rides the flag.
- **The A/B is inside one game**: seed 45 m0, the *same* two witnesses (p-1, p-7) speak a **vent** → two `vent_sighting/strong` flags → 5-1 eject of impostor p-8. Same witnesses, same "I saw it", vent = flag+eject, kill = nothing+skip.

**Where the claim overstates [VERIFIED]**
Half (b) of the contract *did* ship: `meetings/transcript.py:626 WEAK_REASON_KILL_SCENE`, `:1613-1621` a second `reconstruct_stated_paths(include_kill_scene=True)` recovers a placement at the body's room to contradict a stated alibi as `alibi_vs_physical`. So a kill *can* propagate. It fires **once in ~830 contradictions across 707 meetings** (ml_corpus 9p2i seed 1103 m0, and WEAK: `"[weak signal: single-voice kill-scene placement]"`), because it needs (i) the meeting triggered by a body in *that* room, (ii) the accused to volunteer a falsifiable alibi, (iii) 2+ voices. In seed 22 the impostor p-4 simply gave no whereabouts — silence is immunity. Also 5 of the 10 successful kill-witness ejections had **no flag at all**; rhetoric alone carried them.

**Design + code citation**
`tasks/phase-13-5.md:159-201`, Task 13.5.3 "Witnessed kill becomes real evidence". Files NOT in scope: *"meetings/schemas.py, the LLM output schema, and agents/strategic/prompts/*.j2 — … NOT a new observation type or contradiction kind … Literally surfacing 'I witnessed the kill act' as a new public structured claim is the heavier alternative below; deferred."* (b)-strictness *"STRICT (owner-LOCKED 2026-06-26)"* to stop a fabricated kill-accusation railroading a crewmate. Witness half: `agents/memory/beliefs.py:76` `WITNESSED_KILL_SUSPICION_DELTA = 1.0`, applied at `:1311-1318` to the witness's own `BeliefState` only.

**Quantified impact (33 kill-witness vs 473 vent-witness meetings, of 707 across all 4 sets)**
| | killer/venter ejected | lone witness | 2+ witnesses |
|---|---|---|---|
| witnessed **kill** | 10/33 = **30%** | 9/28 = 32% | 1/5 = **20%** |
| witnessed **vent** | 310/473 = **66%** | 217/330 = 66% | 93/143 = 65% |

Contradictions attributable to the kill: **0/33** — the 5 kill-witness meetings where a flag names the killer are all `vent_sighting` from a *separate* vent sighting. 3/33 ejected an innocent crewmate (seeds 37 m1, 46 m1, 1017 m0).

**Gameplay impact.** The most conclusive act in the game is the least persuasive one: a crewmate who watches the murder becomes personally certain (1.00) but has no vocabulary to put it on the record, so it reaches peers only as testimony, and adding a second eyewitness makes it *worse* (20%) rather than better — the opposite of the vent, which the prompt devotes a whole paragraph to and which converts at 66%. Worse for believability, the meeting routinely ranks a bookkeeping `alibi_vs_sighting` on an innocent above two people saying "I watched him do it" (seed 45 m1), and impostors win those meetings by staying silent about their location, since the one propagation path that exists needs the accused to volunteer an alibi to break. This is a deliberate, owner-locked deferral protecting against fabricated kill-accusations — but the STRICT gate it chose is, in the recorded corpus, effectively an OFF switch.

Scripts and data: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-8/` (`scan.py`, `agg.py`, `dump_calls.py`, `rows.json`). Repo untouched (`git status` clean).

---

**VERDICT: CONFIRMED-DESIGN-CHOICE** (all four sub-claims reproduce; (a) is documented + audit-ratified; (c) is true but tautological)

Re-derived independently over all 4 committed sets, n=300 games, 0 load failures. My totals match the claim's exactly: 986 kill intents, 188 whiffs, 626 report events, 16,453 room changes.

**(a) Seat-number decides contested kills — VERIFIED.** Restricted to non-meeting ticks, the separation is total: 156/156 lower-id victims escaped, 90/90 higher-id victims died, 0 in either off-diagonal cell. Per-seat whiff rate (meeting freezes excluded): p-1 46/186 = 24.7%, p-2 18.7%, p-3 15.9%, p-4 18.7%, p-5 19.4%, p-6 4.1%, p-7 6.3%, p-8 1.8%, p-9 0/11 = 0.0%. The claim's "p-1 25% / p-9 0%" is exact; the one p-9 whiff in unfiltered data (ml_corpus/9p2i seed 1019 t10) is a meeting freeze. All four named exemplars re-read clean from the raw JSONL, e.g. samples/9p2i seed 0 t15 `('p-1','move',{'to_room':'ENGINEERING'})` + `('p-8','kill',{'target':'p-1'})` in one actions array, p-1 alive at t16.
Cause: `orchestrator/game.py:2062` `for player_id in sorted(packets)` → `engine/tick.py:593` `for action in actions:` applied sequentially against a mutating state; `_apply_move` (engine/tick.py:255-261) relocates before `_apply_kill` runs.
Design status: `DESIGN.md:334` states it verbatim — "Intra-tick simultaneity is canonically id-ordered … a lower-id target's same-tick move legitimately escapes a kill. This is the documented rule, not a race (2026-06-07 audit decision); revisit only if a future wave gates on per-seat fairness." Not a bug; the fairness caveat is the doc's own open item.

**(b) Zero residue — VERIFIED, and cooldown is not a co-cause.** 156 target_moved + 24 meeting_tick + 8 both = 188, unexplained 0. I additionally recomputed each killer's last landed kill against `kill_cooldown_ticks: 4` (canonical_1.yaml:35): 0/188 whiffs had the killer on cooldown and 0/798 landed kills happened on cooldown, so id-order is the exclusive cause. 0 friendly-fire intents ever issued.

**(c) 0 double reports — VERIFIED but VACUOUS.** `report_body` events carry `body_of`, not `body_id`; keying naively makes every report unique (my own first pass had that flaw). Re-keyed on `(game, body_of)`: 626 events / 626 distinct bodies / 0 dups. But `engine/rules.py:182-197` has no report-once check — `orchestrator/game.py:1247-1259` deletes the corpse at meeting close, with a comment saying exactly that. Confirmed live: samples/9p2i seed 0 shows `body-p-2-5 in STORAGE` every tick t5→t17, p-1 reports at t17, bodies list empty at t18. I measured the opportunity: **0 agent-ticks in 300 games** where a living non-vented agent stood with an already-reported body. Near-miss: **67 ticks had 2-3 agents report the same body simultaneously**; only the lowest id counted, discarded by the same `phase=="MEETING"` early return (engine/tick.py:597).

**(d) 0 teleports — VERIFIED, filter question answered.** 358/16,453 changes are non-doorway-adjacent; all 358 are vent-network-adjacent *and* carry a vent event for that agent. I did not exclude meeting ticks — 50 straddle one and all are plain vent traversals; there is also no post-meeting CAFETERIA relocation (seed 0 t10→t11: p-1 LABS→MEDBAY, p-7 stays ADMIN). The claim undercounts rejected moves: **1,003, not 911** = 911 meeting freezes (alive) + 90 agents killed earlier in the same tick + 2 both — the 92 extra are precisely the victims of (a), so the residue is still zero. The non-circular half: **0/16,905 move intents ever named a non-adjacent room**, so the guard at engine/tick.py:250-255 never fires.

**Gameplay impact.** 26% of kill attempts are contested and 15.8% of all attempts whiff for a reason no spectator can see — the victim's seat number — with nothing in the narrative, memory render, or meeting acknowledging the miss, so it reads as a dropped frame rather than a dodge. Because seat id is fixed for a whole game it is a persistent invisible survivability handicap (p-1 dodges a quarter of everything, p-8/p-9 nothing) that contaminates any per-seat metric unless controlled for. The other three negatives are genuinely clean, but (c) is guaranteed by corpse deletion, not by a report-once rule, and would break the moment a body persisted past its meeting.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-10/report-G-10.md`

---

VERDICT: **PARTIALLY-TRUE** — (a) **CONFIRMED-BUG**; (b) **CONFIRMED-DESIGN-CHOICE** (symptom real and reproduced, cited cause refuted, already owner-pinned in `main`).

**(a) CONFIRMED-BUG.** [VERIFIED] The speech schema handed to the LLM has five observation shapes and no transition shape — `agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:205-209`. Memory nonetheless renders transitions — `agents/memory/store.py:1449-1453` `"[tick {tick}] You saw {p} move from {from_room} to {to_room}."`. In the obs frame that line means X was in A at T-1 and B at T (obs tick = record tick + 1; packets are built at the top of tick N from post-advance state + tick N-1 events, `orchestrator/game.py:1778-1792`). The two truthful static encodings are `(T,B)` and `(T-1,A)`; the one models reach for, `(T,A)`, is never true — and is exactly what the referee compares to the roll-call answer.

Corpus (300 games; samples/9p2i 50, samples/4p1i 50, ml/9p2i 150, ml/4p1i 50): 313 `alibi_vs_sighting` flags, all resolved to a concrete `saw_player`. **124 (39.6%)** are backed by a `move from A to B` line in the speaker's own memory; 86 spoke the destination, **38 (12.1% of all flags) spoke the origin**, 32 of them STRONG. Ground truth: **38/38** — memory line truthful, spoken room false. Per set: 7/76, 0/3, 30/233, 1/1. 25 games, 27 meetings; subjects 31 CREWMATE / 7 IMPOSTOR (roster base rate — role-blind noise, but 78% of what it ejects is wrong). **10 meetings ejected the falsely-flagged crewmate.**

- seed 12 m0: p-9 holds `[obs p-9:3:2] [tick 3] You saw p-3 move from MEDBAY to LABS.`, speaks `saw_player p-3 MEDBAY @3`; p-3 truthfully answers `alibi … room 'LABS', from_tick 3, to_tick 3`. Flag `[alibi_vs_sighting/strong] :: Alibi places p-3 in LABS (ticks 3-3); sighting reports p-3 in MEDBAY at tick 3.` → 6–0–1 against an innocent, p-5: *"the flag proves they were in Medbay. That break is real."* p-9's ballot cites `reason_obs=p-9:3:2` — the citation gate is satisfied by the line that refutes the flag.
- seed 39 m0: p-3\* (IMPOSTOR) holds `[obs p-3:8:6] [tick 8] You saw p-1 move from EAST_HALL to CAFETERIA.`, speaks EAST_HALL@8; p-1 (crewmate, body reporter) answers CAFETERIA@8 → STRONG flag → **7–1** ejection, every voter 0.85, both impostors riding it (p-6\*: *"the verified flag proves p-1's alibi is a lie"*). Winner: IMPOSTORS. Also ml/9p2i 1061 m2, 1012 m1, 1013 m1, 1066 m0; samples 13/17 m0.

[JUDGMENT] Unsanctioned anywhere in the design record. Task 13.5.4 (`tasks/phase-13-5.md:256-319`) shipped the render and deferred "a movement-driven belief/contradiction rule", but the render feeds a schema that cannot carry a transition; the 13.14 LONE-STRONG ruling (`tasks/phase-13.md:684-745`, priced at "+3 worst-case wrong crew vs +20 correct") then promotes this band to gate-crossing STRONG, and these 10 wrong ejections sit inside that budget without having been in the probe.

**(b) CONFIRMED-DESIGN-CHOICE.** [VERIFIED] Symptom reproduces: seed 23, crewmate p-1 is ADMIN@rec8 → EAST_HALL@rec9, `visible_players` empty at rec7–rec10, yet holds `[obs p-1:10:1] … You saw p-5 move from EAST_HALL to CAFETERIA.` and `[obs p-1:10:2] … p-6 move from EAST_HALL to ADMIN.` [VERIFIED] The cited cause is wrong: `observation/service.py:463-505` gates on `if event.from_room not in visible_rooms` — the departure room — and its docstring names arrival-gating as the already-fixed Codex P2 bug. The residual is that `visible_rooms` is post-advance (`orchestrator/game.py:1778`), and `engine/visibility.py:100-127` downgrades CREWMATES to `same_room_only`, so a crewmate's visible set is literally the room it just arrived in. Scale: **3,003 / 16,518 (18.2%)** rendered move-lines are unwitnessable (crew 1,549/5,711 = 27.1%; impostor 1,454/10,807 = 13.5%), of which **1,585** are the arriver pattern; per set 759/4,129, 32/349, 2,173/11,675, 39/365. The mirror loss dwarfs it: **19,435** genuinely-witnessed departures dropped vs 7,569 kept. [VERIFIED] Commit `deef31ea` (merged in `1b4b1693`, task 19.24(b)) reproduces this exact case, argues both tick-interior slices are real, and test-pins both — exposing `departure_visible_rooms` in `eval/leak_scan.py` as the flip hook.

**Impact.** (a) is the live harm: in 25/300 games a truthful movement memory is re-spoken as a placement that is never true, the referee stamps it STRONG "VERIFIED evidence", and 10 meetings ejected the innocent it framed — including an impostor manufacturing a 7–1 ejection of the body reporter by quoting the origin half of a true line. Because the table votes off the flag at 0.85 confidence, one mis-encoded word converts straight into a lost game. (b) is cosmetic by comparison — an odd doorway-narration — and its evidentiary weight is small next to the 72% of genuine departures the same gate silently drops; it is already owned and one substrate flip (plus a re-record) from the strict rule.

/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-9/report.md

---

VERDICT: **PARTIALLY-TRUE** — the `saw_player` half reproduces; the `saw_vent` half (the claim's headline evidence) is REFUTED.

**saw_vent — REFUTED.** 748 spoken `saw_vent` corpus-wide, 739 (98.8%) grounded in the speaker's own recorded FOV (`action=="vent"`, ±2 ticks). Only 9 exceptions; every one names a real impostor, none names an innocent, none is "in neither memory nor engine". 7 of the 9 are witnessed **kills**: seed 1115 t29 engine `EVENT kill: {'killer_id': 'p-8', 'victim_id': 'p-1', 'room_id': 'ENGINEERING'}`, all four speakers' FOV shows `p-8@ENGINEERING:kill`, p-3's memory reads `[obs p-3:30:4] [tick 30] You witnessed p-8 kill in ENGINEERING`, and its ballot cites `p-3:30:4` with rationale "I witnessed p-8 **kill** p-1". Same in 1033 (`[obs p-6:7:1] You witnessed p-7 kill in MEDBAY`; p-7 is the impostor and did kill p-2 there). Root cause is a schema gap, not fabrication: `meetings/schemas.py:143-148` has no witnessed-kill kind, so the nearest impostor-proving slot gets used. The cited seed 8 example ("I personally witnessed p-3 vent") is fully grounded — that example is simply wrong. And the guard the claim says failed actually fired: no `vent_sighting` flag was minted in 1115 m1 or 1033 m1, exactly as `meetings/transcript.py:220-221` intends ("an UNGROUNDED spoken vent claim mints NOTHING").

**saw_player — CONFIRMED.** Crew claims the speaker's own visibility could not contain: samples/9p2i 151/1301 = 11.6%, ml/9p2i 458/3456 = 13.3% (claimed 12.0-12.2%); factually false 8.5%/8.7% (claimed 7.9-8.2%). Impostors 1.2%/3.6% — they fabricate far less, gap bigger than claimed. Two corrections to the mechanism: (a) memory *does* keep provenance — `[tick 15] [meeting] CLAIM by p-3 (unverified): saw p-9 in MEDBAY @ tick 12` (`agents/memory/store.py:1485`); the loss is at the speech layer, since `SawPlayerObservation` (`meetings/schemas.py:57`) has no provenance field and `accusation_round.j2:112-113` renders it bare. Seed 2 m3 laundering verified: p-9 emits first-hand `saw_player(p-7, STORAGE, 21)` while its FOV is `p-9 sees players=[]` and it was in ADMIN — its own free text admits the distance. (b) 71% of false placements name a hallway (EAST_HALL 49.0%, WEST_HALL 21.9% of 453) vs EAST_HALL being 17.7% of all sightings: the model narrates inferred transit as a sighting.

**The harm channel the claim missed.** Ungrounded vents mint nothing, but ungrounded *sightings* do. `meetings/transcript.py:198-213` (Task 18.9) exempts single-tick roll-call answers from the weak band, and the sighting side is never grounded against `SightingRecord` the way the vent side is. Of 313 `alibi_vs_sighting` flags, 25 (8.0%) are STRONG and built on a placement the speaker could not have seen and that was false. samples/9p2i seed 44 m0: p-9 (in STORAGE, seeing only p-1) speaks `saw_player(p-4, EAST_HALL, 7)` while p-4 was in CAFETERIA → `[alibi_vs_sighting/strong] subjects=('p-4',)` → crewmate p-4 ejected 7-0, both impostors piling on. Population: 22.8% (18/79) of innocent ejections carry such taint vs 13.8% (49/356) of correct ones.

**Incidental glitch:** `RoomId: TypeAlias = str` (`meetings/schemas.py:41`) — no map validation. samples/9p2i seed 31 m3 p-7 twice speaks room `CAFERIA`; accepted, stored, rendered into the next prompt.

**Gameplay impact (3 sentences).** The vent channel is honest and well-defended, so the claim's alarming "witnessed VENT" quotes are almost all real evidence in the wrong syntactic box — the fix is a `saw_kill` observation kind, not a fabrication clamp. The sighting channel is the actual leak: crew narrate inferred hallway transits and re-speak heard testimony as first-hand at ~12-13% of claims, and because that channel has no grounding chokepoint, ~8% of STRONG `alibi_vs_sighting` flags shown to voters as VERIFIED evidence are manufactured from testimony that was physically impossible. That asymmetry — vents grounded, sightings not — reads as an oversight rather than a design ruling, and it is measurably ejecting innocents.

/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-4/G-4-verification.md

---

VERDICT: **PARTIALLY-TRUE** — (a) turn-marker half CONFIRMED-BUG, (a) ballot half CONFIRMED-DESIGN-CHOICE, (b) CONFIRMED-BUG (minor).

**(a) Turn markers — CONFIRMED-BUG, numbers reproduce exactly.**
Turns whose `free_text` opens with a dev marker: samples/9p2i **53/971 = 5.5%** (all `[invalid accusation target 'p-N' dropped]`); ml_corpus/9p2i **139/2726 = 5.1%** (137 accusation + 2 `invalid corroboration supports`). Both 4p1i sets: 0/117 and 0/120 (1-impostor games rarely produce dead-target accusations).
They reach the model verbatim. Exact bytes from p-3's own prompt, samples/9p2i seed 0 meeting-1:
`  said: "[invalid accusation target 'p-6' dropped] Wait, wait, hold on, I was in EAST_HALL at tick 16 with p-7 and p-8, ... but more importantly, I SAW p-6 vent in ENGINEERING at tick 8"`
Contamination denominators: prompts containing a dev marker **246/1956 = 12.6%** (samples/9p2i) and **671/5502 = 12.2%** (ml/9p2i); **33/165** and **91/463** meetings; **25/50** and **68/150** games.
Code: marker built at `meetings/manager.py:3908-3912` (constant :381-383), rendered unfiltered by `agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:136` and `accusation_round_roll_call.j2:133` (`said: "{{ turn.free_text }}"`).
Unintended per its own contract — `meetings/manager.py:3884-3887` promises "a dropped claim never reaches the transcript, contradiction detection, the post-meeting belief fold, or any prompt surface"; the *claim* doesn't, the *marker* does. `audits/audit-2026-06-11-2218-gameplay-data.md:38` (H-H-4) already called a spliced marker "a Frankenstein turn record" but only fixed the 60-char length bound, never the prompt visibility. Spectator-side stripping exists for ballots only (`api/replay_loader.py:2696-2703` `_BALLOT_PREFIX_MARKERS`); no turn-`free_text` equivalent.

**(a) Ballot half — REFUTED as a leak, CONFIRMED as a count.** `[under-gate eject target 'p-N' redirected]` appears in exactly **61** rationales (13 samples/9p2i + 48 ml/9p2i), as claimed. But ballot markers reach **0/7458** prompts across both 9p2i sets (ballots are post-meeting; `DESIGN.md:587` "not visible to agents during the vote"), and `DESIGN.md:589` explicitly sanctions "an audit marker in `rationale_text`". The spectator strips them into labelled chips. So this half is a sanctioned design choice with no model-facing effect — not a text-hygiene defect.

**(b) Singular persona — CONFIRMED.** All six qwen3_6_27b templates hardcode a singular hidden impostor with no impostor-count conditional: `crewmate_report.j2:58`, `impostor_report.j2:59`, `accusation_round.j2:79`, `accusation_round_roll_call.j2:76`, `impostor_report_roll_call.j2:69`, `vote_ballot.j2:74`. Coverage is total, and larger than claimed: **1956/1956** prompts in samples/9p2i (165 meetings) and **5502/5502** in ml/9p2i (463 meetings) — 100%, not just "165/165 meetings". Self-contradicting inside one prompt: p-6 in seed 0 meeting-0 is told `a hidden impostor kills crewmates ... the impostor by surviving` in `<persona>`, then at `accusation_round.j2:169` `Your fellow saboteurs: p-8 — never accuse or incriminate them`. 490/1956 and 1368/5502 prompts carry both strings. No design ruling sanctions the singular; `DESIGN.md:768` states the roster is "9 agents per game; 2 impostors (the canonical eval roster). Configurable", so the template is simply not parameterised. Also mis-states the win condition to crewmates: "the impostor wins by surviving until they equal the crew" is arithmetically wrong with two impostors.

**Gameplay impact.** The turn-marker splice puts editor-console text inside quoted dialogue in one prompt in eight, immediately before the sentence that usually names a vent sighting — it corrupts the fiction for any spectator reading the transcript and injects an unexplained token into the deliberation context at exactly the high-leverage moment. The singular persona is worse for reasoning than for prose: every crewmate in a 2-impostor game is told to hunt one killer and is given a parity condition that cannot be satisfied, which plausibly under-motivates a second ejection after a correct first one; the impostors get told they are the lone impostor and then handed a teammate two lines later.

Repro script: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-25/scan.py`

---

VERDICT: **CONFIRMED-BUG** — mechanism exact and worst case reproduced; two magnitude figures overstated; one cited seed refuted.

**Harness / fidelity.** `repro.py` + `analyze.py` re-seed the world, re-run perception per agent per tick, apply recorded meeting results, and call the real `ImpostorPolicy.decide` offline. Across **300 games / 10,335 impostor decisions: 0 mismatches vs the recorded action stream** — every target list below is the one the recorded impostor held.

**[VERIFIED] Mechanism.** `_confirmed_dead_from_bodies` (agents/tactical/impostor_policy.py:813-839) builds the dead-set only from `saw_body`. Ejection mints no body; a partner's victim's body is never seen. `_scored_targets` (:981) keeps the sighting at score 1.0 until `_STALENESS_THRESHOLD = 30` (:185), and `(-score, player_id)` (:1008) hands the tie to the lowest id. seed 36, decision-tick 50:
```
t 50 p-2 @ADMIN cd=0 -> policy=MoveIntent(to_room='WEST_HALL') | recorded=('move', {'to_room': 'WEST_HALL'})
      dead_seen=['p-1','p-3','p-5'] alive=['p-2','p-7','p-9']
      targets=[('p-6','WEST_HALL',1.0,0), ('p-7','ADMIN',1.0,0), ('p-9','CAFETERIA',1.0,0)]
```
p-6 was ejected at t34 and is absent from `dead_seen`. p-7 — alive, isolated, in p-2's own room, cooldown 0 — is a legal kill and loses on the string `"p-6" < "p-7"`. p-7 completes `upload_logs` at t51 (14/14); crew wins by tasks. Killing at t50 = 1v1 parity. **One game demonstrably thrown.**

**[VERIFIED] The ejection IS in memory; the FSM never looks.** `agents/perception.py:62-84` has no ejection event, but `agents/memory/store.py:549 record_meeting_outcome` folds `MeetingOutcome(end_tick, ejected_id)` into `memory.meeting_history` (`agents/memory/working.py:176-185`) from the meeting's public payload. Sole consumer: `agents/tactical/features.py:678`, the **v3 learned** encoder, which reduces it to 3 counts and drops the id. The FSM reads `memory.episodic` only.

**Not a sanctioned design choice.** The `_scored_targets` docstring states the intent ("never re-scores a corpse"). `audits/audit-2026-05-15-0225-reconciled.md:208` is the R-3 finding this guard exists for — "chasing a corpse or stale sighting forever, preventing parity" — and its seed-0 `ENGINEERING ↔ REACTOR` pendulum still reproduces in seeds 10/31/1016. `tasks/phase-2.md:1103-1106` offered a belief-flag sourcing as the alternative; nothing excludes ejections. `DESIGN.md §4.4` is silent. `tests/.../TestImpostorStaleAndDeadTargetPruning` covers only the body case — **no test exercises an ejected target**.

| set | games | imp decisions | mismatch | ghost-top | % | ejected/unseen | games ≥1 | blocked kills | games |
|---|---|---|---|---|---|---|---|---|---|
| samples/9p2i | 50 | 2461 | 0 | 303 | 12.3% | 222/81 | 22/50 | 30 | 9/50 |
| ml_corpus/9p2i | 150 | 6663 | 0 | 555 | 8.3% | 363/192 | 55/150 | 27 | 10/150 |
| samples/4p1i | 50 | 632 | 0 | 0 | 0% | — | 0/50 | 0 | 0/50 |
| ml_corpus/4p1i | 50 | 579 | 0 | 0 | 0% | — | 0/50 | 0 | 0/50 |

"blocked kill" = cd 0, live non-teammate co-located this tick with `co_present==0`, no fellow to defer to — the policy would have emitted `KillIntent` but a dead player outranks it. 9 of the 19 blocked-kill games are crew wins. **4p1i is 0/100 — the defect exists only on the 9p2i eval roster.** Longest runs cap at exactly 30 ticks: seed 31 p-5→ejected p-1 t14-t43, seed 17 p-2→p-1 t7-t36, seed 32 p-5→p-1 t11-t38.

**Where the claim overstates.** "40-53% wasted hops" is unsupported: backtracks are 332/1335 (24.9%) and 812/3624 (22.4%) of hops, and only 31%/27% of those pivot on a ghost-top tick — ~6-8% of hops, not 40-53%. "Most of the corpus dead time" is unsupported (8-12% of decisions). The ABAB figure is corroborated: I count 160/377 windows containing a ghost-top in ml_corpus/9p2i vs the claimed 173/384 — but that means ghost-targeting causes **under half** the pendulum; the rest is the same fall-through with a *live* stale target (`best.room == own_room`, not visible now → neither kill nor move branch fires at :385-398 → `_idle` wanders → paths back). **seed 42 is REFUTED**: at t41-t45 the target list is `[('p-2','CAFETERIA',0.1111,2), ('p-3',…,2), ('p-8',…,2)]` — no ghost on top; p-7 waits because every visible target has 2 witnesses (the intended KILL_OPPORTUNITY hold), and p-1's ADMIN isolation was never observed. A smaller genuine ghost run does exist at seed 42 t38-t40 (p-7 → ejected p-9).

**Caveat.** The counterfactual assumes the engine accepts the kill; per DESIGN.md §3.4 a lower-id target's same-tick move can dodge, so a few of the 57 blocked kills might have been rejected anyway. Not applicable to seed 36 t50 (p-7 was mid-`do_task`).

**Impact (3 sentences).** On the 9p2i roster the impostor spends 8-12% of its decisions hunting someone the whole table watched get ejected, walking past isolated killable crewmates because a corpse's id sorts lower — spectator-visible stupidity that cost kills in 19/200 games and provably threw seed 36. Because 4p1i is clean, the defect silently biases the canonical 9p2i impostor-win baseline downward, so some measured impostor weakness is a target-selection bug rather than a strategy or model ceiling. Fixing the dead-set alone will not remove the pacing artifact: it accounts for only ~42-46% of the A↔B oscillation, the rest being the same stale-sighting fall-through against live targets.

Full report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/verify-G-12/REPORT.md` (harness: `repro.py`, `analyze.py`; per-set JSON alongside)