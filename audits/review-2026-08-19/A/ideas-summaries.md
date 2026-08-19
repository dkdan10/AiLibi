# Ideation summaries (3 lenses)

Report written. Repo untouched (one note below).

**Ranked proposals — full report at the path at the end.**

Grounding: watched `samples/9p2i` seeds 2 & 17 (ticks + all meetings + p-9's rendered memory) and `samples/4p1i` seed 29; ran my own census over all 300 games (`scratchpad/work/ideas-game-designer/pacing.py`).

**Three new numbers of my own [VERIFIED]**
- Kills with **no third party in the room**: 79.7% / 81.2% (9p2i), 98.4% / 98.2% (4p1i). With crew's same-room-only vision, the murder scene is evidentially empty by construction.
- Meetings with **zero contradiction flags**: 39.4% / 36.3% / 66.7% / 50.0%.
- Outcome ledger: 9p2i crew wins **137× by ejection vs 10× by tasks**; impostors **53/53 by parity, 0 by anything else**. The task race is decorative; there is no impostor clock.
- Diagnosis: **one working evidence channel (the vent, 440/440 precise, 71% of ejections) and it is a lottery on where the impostor surfaces.** Everything spoken is downstream noise.
- Mechanism seen in the bytes: seed 17 p-9 *had* the right row — `[obs p-9:5:1] [tick 5] You saw p-1 in EAST_HALL (with p-4) (moved from CAFETERIA…)` — at **line 22**, under twelve near-identical CAFETERIA co-presence rows and an 8-line tick-0 lobby block, and spoke the stale one. The model is reading the top of a badly sorted list, not hallucinating.

| # | proposal | addresses | size | main risk | key metric |
|---|---|---|---|---|---|
| 1 | Render a self-location trail; refuse roll-call answers contradicting it | G-1 | S–M | re-record; no prompt change needed | false crew `whereabouts` 20.5%→<3% |
| 2 | Split flag block PROOF vs DISPUTE; stop labelling alibi flags "VERIFIED evidence" | G-2 | **S** | prompt version cascade | sole-alibi-flag precision 14.6%→≥50% |
| 3 | Post-meeting reset: gather, flush vents, cooldown grace, sweep bodies | G-5/6/18 | M | balance | reporter death ≤3 ticks 15.7%→~0 |
| 4 | Time of death on the body (FRESH/COLD band first) | G-7 | S–M | comparability | meetings debating the true window ≈0→>80% |
| 5 | Memory render: coalesce, drop lobby block, sort by decision-relevance | G-34 | S–M | re-record | ungrounded crew sightings 12%→<4% |
| 6 | Ground the prosecution side like the vouch side already is | G-2 mech | M | must follow #1 | grounded sighting side 36.5%→100% |
| 7 | Finished crew escort / sweep / patrol | G-15 | M | big crew buff | solo kills 79.7%→<60%; idle-done 13%→<3% |
| 8 | Symmetric roll-call — every turn carries one `whereabouts` | G-22 | S | prompt cascade; re-check firewall | P(impostor \| no whereabouts) 97.7%→chance |
| 9 | Exempt dead subjects from "speak your vent FIRST"; persist meeting outcomes | G-23/35 | S | prompt cascade | struck accusations 5.0–5.5%→0 |
| 10 | Text hygiene: strip husks, plural impostor, no threshold talk, show redirects | G-25/27/28/29 | S | prompt cascade | husks in `free_text`→0 |
| 11 | `saw_kill` observation + `kill_sighting/strong` above alibi flags | G-8 | M | barely fires until #7 | kill flags/100 games ~2→~15 |
| 12 | Let converging independent testimony reach the gate | G-19/20 | M | **highest** — mid-band is below chance today | `flag⇒EJECT` accuracy 88.5%→<70% |
| 13 | Sabotage as a real clock + 4p1i second act | G-40/43 | M–L | new win condition = own baseline | dead-air runs ≥5 ticks 44→<15 |
| 14 | Persist vote-time conviction; give the accused one reply | G-21/24/30 | M | +30–50% LLM calls | belief retention 19.1%→≥50% |
| 15 | Impostor FSM: no ghost-stalking, peek before venting, dwell not pendulum | G-12/13/39 | M | largest balance risk — must ship last | vent exits witnessed 56.5%→~35% |

**Balance note.** Crew already wins 70–75% in 9p2i and items 1–7 all help the crew further. The impostor budget is **#8, #13, #15**; #3 nerfs the impostor and must be paid for. Do not ship the crew half alone.

**Shipping order.** A: 1,2,5,9,10 (one combined re-record) → B: 4,6,8,11 → C: 3,7, then 13 as its own baselined wave → D: 12,14,15.

**Three things I would NOT change**
1. **The vent as the one certain tell.** 440/440 precise, 96.7–97.1% conversion. Every good deduction game needs one certain channel. Once other channels work there will be pressure to add noise to it — don't; fix the others. Watch #15 for accidentally deleting it.
2. **Crew same-room-only vision (Task 13.8).** Absurd-looking (41% of kills adjacent to a blind crewmate, 327/327) but it is the forcing function that makes the meeting exist. Narrow repair only: adjacent-room **bodies**, never players. Also fix `canonical_1.yaml:52-58`, which still documents uniform adjacency.
3. **SKIP as a first-class outcome + the structured round-robin protocol.** 39% of meetings honestly have nothing. And the typed/cited layer is why hygiene is perfect (0 dangling ids in 3,814 ballots) and the firewall provably airtight (0/929). Add a reply round *inside* it (#14b); never replace it with free-form chat.

Repo note: `git status` shows one untracked `.coverage` file (mtime 03:09 today, likely a pytest-cov side effect of `uv run` in this or a sibling Track-A session). I did not delete it, per the read-only rule — flagging so you can remove it.

`/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/reports/A/ideas-game-designer.md`

---

**RANKED IDEAS — multi-agent / LLM-reasoning lens**

Watched: samples/9p2i s17, s2; samples/4p1i s29 (+ raw prompts, p-8 memory). Censused all 300 games / 707 meetings / 7,458 meeting LLM calls. All numbers [VERIFIED] from the bytes.

**Diagnosis (new numbers, not in the collated set)**
- **Deduction headroom.** Zero-LLM co-presence elimination at the last kill tick (uses only living crewmates' own perception): candidate set is a **singleton in 109/626 body meetings, correct 103/109 = 94.5%**; ≤2 candidates 208/626; killer inside 581/626 (92.8%). **61/354 actual ejections landed on someone the crew's own pooled perception had already cleared.** A running cross-meeting tally puts a real impostor top in 286/463 ml/9p2i (61.8%) vs ~25% chance; meetings agree with it 29.6%.
- **The flag detector is geometry-blind.** **148/234 (63.2%)** strong `alibi_vs_sighting` flags name **adjacent rooms** — one tick of walking reconciles both statements. 130/148 name innocents. Of the 126 ejections they drove, **78 were adjacent-room, 68 of those wrongful**. 187/234 have a single-tick window. **0/7,458 prompts contain a map, adjacency or travel times.**
- **The belief scalar caps the LLM's conclusion.** 3,697/3,697 ballot prompts: *"do not report a confidence at or above the skip threshold for a target whose suspicion is below it."* Of 2,351 crew turns naming a suspect, only **1,276 (54.3%) voted that suspect**; 712 retreated to SKIP (243 abandoning a real impostor), 363 switched (309 onto a flag subject, 120 of them innocent, 94 abandoning a real impostor). **≥337 crew ballots named an actual impostor out loud and voted elsewhere.** Kept targets get a *lower* ballot confidence than spoken 596× vs 300×.
- **36.6% of voters (1,438/3,934) enter the ballot with zero belief rows** about anyone living; the store covers 34.6% of living others.
- **Nothing survives a meeting: 0/7,458 prompts record any prior ejection or its revealed role.** Vent testimony compresses to `accused p-2` while the impostor's fabricated *sighting* keeps room+tick.
- **1,723 mutual-vouch pairs** each earn two independent alibi discounts (s17: p-5/p-6 vouch only for each other, both land at 0.45 — below the accused venter's 0.50 prior).
- **Budget:** 53.2 lines/snapshot; 51.7% co-presence, 12.5% tick-0 spawn block, vent 0.69% + body 0.82%. Span-coalescing + dropping spawn frees **~32% at zero information loss**.
- **Endgame blindness:** 157 meetings at crew ≤ imp+1; **84 (53.5%) skipped**. At 3-alive the 0.60 gate is unreachable (prior 0.50) — 4p1i s29 loses exactly this way.
- **Exemplar (s17 m0):** truthful vent witness p-1 ejected 7–1 on a duplicated adjacent-room flag; p-8 accused the right man in its own turn (*"p-2 has provided no alibi for tick 6"*, 0.6) then voted p-1 at 0.85: *"This verified contradiction proves p-1 is lying."*

**Ranked proposals** (size · risk · key metric)
1. **R1 Map-aware flag arbitration** — adjacent rooms + ≤1 tick ⇒ demote/suppress. S · eval HIGH · vetoes 78/126 flag ejections, 68 wrongful.
2. **R2 Corroborated whereabouts board** (roster×tick grid, cell filled only on two-sided agreement; also fixes crew self-placement). M · design+eval HIGH.
3. **R3 Drop the confidence cap; persist an explicit posterior.** S–M · eval HIGH · unblocks the 337.
4. **R4 Persist meeting verdicts** ("p-1 EJECTED, was a CREWMATE"). S · low risk · 0/7,458 today.
5. **R5 Testimony as citable content**, not `accused X`. S · low risk.
6. **R6 Adversarial roll-call + rendered absence** (ship both halves). S · balance risk.
7. **R7 Corroboration algebra** — dedupe flags, collapse mutual-only vouches, ≥2 independent sources for STRONG. M.
8. **R8 Coalesce spans, drop spawn block** — the enabler that pays for 2/4/5. S.
9. **R9 Mandatory `alternative` field on every accusation** — cheapest ToM step; in s17 it forces "or he walked EAST_HALL→ENGINEERING". S.
10. **R10 Rebuttal turn for the accused** (73% of accusations die unanswered). S–M.
11. **R11 Endgame line + gate scaled to table size.** S · balance HIGH.
12. **R12 Map card in the prompt** (agent-side half of R1). S.
13. **R13 `saw_kill` obs + `kill_sighting` flag above alibi flags.** M.
14. **R14 Budget LLM calls** — reallocate filler turns into rebuttals/second passes. M · eval HIGH.
15. **R15 Reasoning scoreboard eval** (candidate-set containment, turn→ballot hold, flag precision × source × adjacency, belief retention, "named-then-defected"). M · **zero risk — do it first**; none of the five is measured today.

Wave order [JUDGMENT]: R15 → substrate wave (R1+R7+R8+R4+R5, no balance levers) → balance wave (R6, R11, R2 as single-variable arms).

**Would NOT change:** (N1) crew same-room-only vision — it is the forcing function; fix corpse-blindness with adjacent-**bodies**-only. (N2) the vent channel, citation discipline and the deterministic tally — 440/440, 0 dangling ids in 3,814 ballots; make other channels look like it, don't touch it. (N3) don't reach for a bigger model or longer instructions — in s17 the model found the right answer and was overruled by a false "VERIFIED" label and a pre-discussion scalar; §4.6 arithmetic already leaks into the characters' mouths.

Note: a `.coverage` file appeared untracked in the repo root as a side effect of `uv run python`; I left it in place rather than deleting anything.

Report: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/reports/A/ideas-multi-agent-researcher.md`

---

**RANKED PROPOSALS — Among Us veteran lens** (full report at the path below)

Grounded in spectator walks of 9p2i seeds 2 & 17 and 4p1i seed 29, plus 7 measurement scripts over all 300 committed games.

| # | proposal | size | key evidence (all [VERIFIED] this pass unless noted) |
|---|---|---|---|
| 1 | **Announce the ejection result + impostor count** ("p-4 was an IMPOSTOR. 1 remains") | S | **0 / 3,934** rendered memories contain any ejection outcome — 1,799 of them rendered *after* an ejection. Seed 2 m2+m3 are spent re-prosecuting the already-ejected p-4 |
| 2 | **Tell the table when a skip loses the game** (parity-1 clause in ballot prompt) | S–M | CRITICAL meetings eject **46.5%** (73/157) vs **65.8%** elsewhere; 84 skipped criticals → **56 impostor wins**. No parity/endgame word in any of the 6 templates. 4p1i s29: 3 alive, all SKIP, impostor wins at t11 |
| 3 | **Post-meeting reset** (teleport to Cafeteria, eject from vents, cooldown grace) | M | 15.7% of reporters die ≤3 ticks after their own meeting; 9.8% of meetings have a participant inside a vent. s17 t6: `p-2*@ENGINEERING:VENT(VENTING)` says *"I didn't vent anywhere"* |
| 4 | **Move-before-kill (or seeded actor order) + emit `kill_attempt_evaded`** | M | 156/156 lower-id victims escape, 90/90 higher-id die. s2 t30 `p-7:kill p-3` annihilated, then a **6-tick one-room-behind chase** that can never close |
| 5 | **Give finished crew a job** (patrol / escort / sweep) | M | **7,939** done-crew ticks, **60.4% literal `wait`**, 5,617 in CAFETERIA; 684 runs, mean 7.0, **max 36**. s17 p-9 waits t12–t41 |
| 6 | **Impostor: peek before venting; no reflex kill→vent** | S–M | Exits seen 56.5%/59.2% vs enters 8.8%/6.4%. **Seed 2: both impostors lose to the identical mistake** (t10 into p-8, t20 into p-3) |
| 7 | **Split the flag block: proof vs. conflicting accounts** | S / M | `vent_sighting` 440/440; `alibi_vs_sighting` **14.6% precision as sole evidence** (12 right / 70 wrong), below chance. s17 m0 ejects the honest vent witness 7–1 |
| 8 | **Render the self-location trail** (store already keeps `own_room_by_tick`) | S | 843 self-position lines, room correct at the stated tick only **16.0%**; 20.5% of crew whereabouts false; 44.3% of innocent ejections |
| 9 | **Take the free 1-on-1 kill; replace the pendulum with a dwell** | M | **55.8%** of solo+off-cooldown decision points declined; **202** A↔B oscillation runs, max **25 ticks**. s17: 6 straight declines beside p-5 |
| 10 | **`saw_kill` observation + `kill_sighting/strong`** | M | Witnessed-kill line is 0.02% of memory, worth +0.08. All 46 kills with a 3rd party present had that party be the impostor's **partner** — crew have never witnessed a kill |
| 11 | **Crew see adjacent-room bodies only** (not players) | S | Crew cross-room body sightings: **0, ever**. 21.6% of bodies never reported, 96.5% in rooms nobody re-enters |
| 12 | **Time of death on the body** (`fresh`/`cold` band) | S | 963/963 `found_body` carry the *report* tick, median +4, zero exact. s2 m0: *"cold as a cucumber… just a tick ago"* — kill t4, report t7 |
| 13 | **Let the impostor self-report** | S–M | **0/626** reports, **0/707** meeting calls; `impostor_report.v3` has **0 calls of 7,932** |
| 14 | **Make lights sabotage worth pressing** | S | **110 sabotages, 100% reactor, 0 lights ever.** Crew are already `same_room_only`, so lights strips only the *impostor's* vision — a self-harm button |
| 15 | **Emergency button fires on hard evidence** | S | 112/112 `suspicion_accumulation`, 0 with a body in view, 71/112 at t10–11. s2 p-3 holds a vent at belief 1.00 for 15 ticks and never presses |
| 16 | **Show `PRETEND_TASK` on the spectator DTO** | S | 1,747 fake tasks → IDLE 800 / MOVING 844 / **TASK 0**, though co-located crew correctly see `task`. **Free: frontend-only, no re-record** |

**Would NOT change:** (N1) crew same-room-only *player* vision — it is the forcing function and it is how the real game feels; fix only the corpse case. (N2) the vent tell at 100% precision — 440/440; rarer-and-perfect beats common-and-noisy; the problem was everything else sharing its "VERIFIED" label. (N3) sabotage as stall/lure, not a win lever — s17 t41–44 already shows it doing exactly the right job (splits the crew, wins a kill, not the game); making it a win condition re-creates the Wave-D stopwatch failure.

**Sequencing:** V1/V2/V5/V8/V11/V15 push crew-ward, V6/V9/V14 impostor-ward, V3/V4 change the kill economy — ship as one wave with a single combined re-record per the standing cadence doctrine. First three to build: **V1, V3, V5** (what a viewer notices in game one). V16 can ship today alone.

Note: repo untouched except an untracked `.coverage` file emitted by `uv run` (I did not create or delete any repo file).

/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/reports/A/ideas-among-us-veteran.md