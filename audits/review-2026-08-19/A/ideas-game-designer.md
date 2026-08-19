# Track A — Ideation from a social-deduction game designer's chair

Lens: Among Us / Werewolf / Blood on the Clocktower. What I care about is **information design**
(who can learn what, and how certain is it), **pacing** (does the tension curve rise), **agency**
(can a player change their fate), **legibility** (can a spectator follow the logic), and
**decisiveness** (does the meeting resolve into a choice that felt earned).

Grounding: I watched `replays/samples/9p2i` seeds **2** and **17** end-to-end (ticks + all meetings +
p-9's rendered memory) and `replays/samples/4p1i` seed **29**, then ran my own pacing census over all
300 committed games (`scratchpad/work/ideas-game-designer/pacing.py`). Everything else is cited to the
Track-A reports and their verification verdicts.

---

## 0. The diagnosis, in designer's terms

### 0.1 The game has exactly one working evidence channel, and it is a lottery [VERIFIED]

- `vent_sighting` is **440/440 precise** (s4/s3, re-verified in verify-G-2 at 310/316 as sole convicting
  evidence) and drives **310/435 = 71% of all ejections** (s3).
- The vent **exit** is seen by a crewmate 56.5% / 59.2% of the time; the **enter** only 8.8% / 6.4% (s2).
  So the crew's one certain tell fires when the impostor happens to surface in an occupied room.
- Outcome ledger I measured over all four sets:
  | set | CREW_EJECT | CREW_TASKS | IMPOSTOR_PARITY |
  |---|---:|---:|---:|
  | samples/9p2i | 31 | 4 | 15 |
  | ml_corpus/9p2i | 106 | 6 | 38 |
  | samples/4p1i | 10 | 23 | 17 |
  | ml_corpus/4p1i | 20 | 19 | 11 |
  In 9p2i the crew wins **137 times by ejection and 10 times by tasks**; the impostor wins **53/53 by
  parity and 0 by anything else**. The task race is decorative and there is no impostor clock at all.

**So: the 9p2i game is "did the RNG put a crewmate in the room where the vent surfaced". Everything the
LLMs say is downstream of that.** That is the sentence a designer has to answer.

### 0.2 The murder scene produces no witnesses [VERIFIED — new number]

My census (`pacing.py`): kills with **no third party in the room** —
`samples/9p2i` **141/177 = 79.7%**, `ml_corpus/9p2i` **410/505 = 81.2%**,
`samples/4p1i` **60/61 = 98.4%**, `ml_corpus/4p1i` **54/55 = 98.2%**.
Layer on G-14 (crew vision is same-room-only; a crewmate stood one doorway from **327/798 = 41%** of
murders and **327/327 perceived nothing**), and the crime scene is evidentially empty by construction.
`You witnessed pN kill in ROOM.` is **0.02% of all rendered memory lines** (s4).

### 0.3 39% of meetings have nothing in them [VERIFIED — new number]

Meetings carrying **zero** contradiction flags: `samples/9p2i` **65/165 (39.4%)**,
`ml_corpus/9p2i` **168/463 (36.3%)**, `samples/4p1i` **26/39 (66.7%)**, `ml_corpus/4p1i` **20/40 (50%)**.
verify-G-2 measured that no-strong-flag meetings eject **13.7%** of the time while sole-`alibi_vs_sighting`
meetings eject **93.9%**. So a meeting is a switch thrown by the detector, not a deliberation
(prediction accuracy of `flag ⇒ EJECT` is 88.5–100%, G-19).

Watched live, seed 2 is exactly this: **m0 and m2 have zero flags and produce eight and four turns of
nothing**; m1 and m3 each open, a vent flag lands, and the vote is unanimous inside one turn.

### 0.4 The "lie" the crew catches is usually a clerical error, not a lie [VERIFIED]

Seed 17 m0 is the corpus's best scene and its worst bug. p-1 truthfully reports
`saw_vent p-2 ENGINEERING @6` — at world t5 p-1 **is** in ENGINEERING (dump `[t 5] p-1@ENGINEERING:MOVING`,
`p-2*@ENGINEERING:VENT(VENTING)`). Then:

> `- [alibi_vs_sighting/strong] :: Alibi places p-1 in ENGINEERING (ticks 6-6); sighting reports p-1 in EAST_HALL at tick 6.`
> `- [alibi_vs_sighting/strong] :: (identical line, printed twice)`
> `- [vent_sighting/strong] :: p-1 witnessed p-2 vent in ENGINEERING at tick 6 …`
> `gate: {'leader': 'p-1', … 'passed': True}` → p-1 ejected **7–1**
> p-8's ballot: *"3. This verified contradiction proves p-1 is lying."*

The correct vent flag naming the real impostor sits **two lines below** the flag that convicts the witness.
verify-G-2 confirms this shape recurs and that the sole-alibi-flag channel runs at **14.6% precision**.

And I watched the *mechanism* in p-9's own memory at that meeting. p-9 spoke
`saw_player p-1 CAFETERIA @5` — but p-9's rendered memory **contains the right row**:

> `- [obs p-9:5:1] [tick 5] You saw p-1 in EAST_HALL (with p-4) (moved from CAFETERIA, last seen there at tick 4).`

It sits at **line 22**, underneath twelve near-identical rows
(`[tick 1..4] You saw p-1 task in CAFETERIA (with p-4, p-7).` ×4, plus the same for p-4 and p-7) and above
an 8-line tick-0 lobby block. The model is not hallucinating. It is reading the top of a badly sorted list.
[JUDGMENT, from a [VERIFIED] render.]

### 0.5 The meeting is a teleconference, and the impostor gets a free execution [VERIFIED]

verify-G-5 confirmed: no gather (all-living-in-CAFETERIA 0/39, 0/165, 0/40, 3/463), cooldowns paused not
reset, **9.8% of meetings have a participant deliberating from inside a vent**, and **111/707 = 15.7% of
reporters are killed within 3 ticks of the meeting they called**.
4p1i seed 29 in one screen: p-4* sits in a vent at `[t 6..8] p-4*@LABS:VENT`, walks to MEDBAY, the meeting
convenes at t10, all three SKIP — and `[t 11] p-4*@MEDBAY:KILL` kills p-2, who never moved. Game over, 12 ticks.

### 0.6 Half the crew are statues [VERIFIED]

Idle-with-all-tasks-done agent-ticks: **13.0%** (samples/9p2i), 10.8% (ml/9p2i), 9.2% / 7.6% (4p1i).
Seed 17 t28–t47 is the picture: `p-6@CAFETERIA:IDLE tp=1.00  p-8@CAFETERIA:IDLE tp=1.00
p-9@CAFETERIA:IDLE tp=1.00` for twenty consecutive ticks while p-5 walks the map alone finishing every
remaining task, and is murdered in ADMIN at t44. Three finished crewmates could have escorted her. Nothing
in the FSM lets them.

### 0.7 The balance ledger (why these ship as a bundle) [JUDGMENT]

Crew already wins **70–75% in 9p2i**. Items 1–5, 7 and 14 all *help the crew* (verify-G-1: games with ≥1
innocent ejection end in an impostor win 57% of the time vs 11% without). So a repair wave that only fixes
the crew's information will push 9p2i past 85% crew. **The impostor budget is items 8, 9 and 10** (a real
sabotage clock, an FSM that stops surfacing into occupied rooms, and a roll-call the impostor must answer
so bluffing becomes a skill). Item 6 *nerfs* the impostor and must be paid for. Do not ship the crew half
alone.

---

## 1. Ranked proposals

Ordering is (effect on the game as a game) ÷ (cost + risk). Sizes: S ≤ ~1 task, M ≈ a wave item, L ≈ a wave.
"Comparability" below always means: any change to what an agent *sees* invalidates the pinned baseline-6
recordings and needs a combined re-record under the substrate-cadence doctrine.

---

### #1 — Render a self-location trail, and refuse a roll-call answer that contradicts it
**Addresses** G-1 (verify: CONFIRMED-BUG). Crew `whereabouts` answers are false **20.5% / 19.7%** of the
time; **44.3% of the 79 innocent ejections** are victim-caused self-misplacement; the *only* line in 971
rendered memories that places the agent is `You completed X (you were in Y)` (843 instances), and that
line's room is right at tick N only **16.0%** of the time (right at N−1 97.0%).

**What.** Render the spans the store already holds — `agents/memory/store.py:1025-1028` keeps
`own_room_by_tick` per tick and currently uses it only to scope *others'* sightings. Emit
`[tick 12–17] You were in MEDBAY (arrived from WEST_HALL).` and re-stamp the completed-task line with the
tick its room actually belongs to (`DESIGN.md:705` already specifies the range form — the shipped line is
*less* than the design). Then: a spoken `whereabouts` that contradicts the speaker's own trail is either
auto-corrected or rendered `(unsupported by your own record)` **before** the detector sees it.

**Effect.** Gameplay: removes the largest single source of innocent ejections and, more importantly, makes
the impostor's self-placement the **only** false self-placement at the table — which is the entire premise
of the genre. Watchability: the meeting stops convicting people for arithmetic.
**Size** S–M. **Risk** no firewall, no determinism risk; prompt text needs no change (it already says
"copied from your own record"); comparability broken → re-record.
**Measure** crew false-`whereabouts` rate 20.5% → target <3%; innocent-ejection share 79/435 = 18.2% →
target <8%; `alibi_vs_sighting` subject-is-impostor rate vs the 25.3% chance baseline.

---

### #2 — Split the flag block into PROOF vs DISPUTE and stop labelling both "VERIFIED evidence"
**Addresses** G-2 (verify: CONFIRMED-DESIGN-CHOICE, twice-ratified — `tasks/phase-13.md:700` LONE-STRONG —
so this is a *reversal*, not a bug fix). `vote_ballot.j2:100` says, in **2543/2543** recorded ballot
prompts: *"Each flag below is VERIFIED evidence… never side with one over a verified flag."*
`vent_sighting` deserves it. `alibi_vs_sighting` runs at **14.6% precision as sole convicting evidence**
and its subjects are impostors **17.2%** of the time against a **25.3%** chance baseline — *worse than
guessing*, p=0.0048.

**What.** Two labelled blocks in every meeting prompt.
`PROVEN (engine-certified)` — `vent_sighting`, `alibi_vs_physical` (100% / 100% impostor-subject).
`DISPUTED (two accounts conflict; nothing here says which is wrong)` — `alibi_vs_sighting`,
`alibi_conflict`. Drop the "never side against a flag" sentence for the DISPUTED class. The taxonomy
already exists in code (`api/schemas.py::classify_evidence`: `role_proof` / `cross_statement` /
`weak_signal`) — it just never reaches the model.

**Effect.** Sole-alibi-flag meetings should fall from a 93.9% ejection rate toward the ~40% a genuine
"one of you is wrong" signal deserves, and the resulting SKIPs are *correct* skips. Watchability: the crew
stops sounding like a jury reading a forged lab report.
**Size** S (prompt-only) — the cheapest P0 in the track.
**Risk** prompt version-bump cascade (`.j2` marker + `game.py DEFAULT_PROMPT_VERSIONS` + the live-recorded
prompt-version test pin); comparability broken; no firewall/determinism risk.
**Measure** precision of ejections whose only strong flag is `alibi_vs_sighting` (14.6% → ≥50%);
`flag ⇒ EJECT` prediction accuracy (88.5–100% → lower is better); innocent-ejection share.

---

### #3 — Post-meeting reset: gather, flush the vents, grace the cooldown, sweep known bodies
**Addresses** G-5 / G-6 / G-18 (verify-G-5: CONFIRMED). No gather in 707 meetings; **9.8%** have a
participant inside a vent; **15.7%** of reporters die within 3 ticks; 22 corpses lay in CAFETERIA *during*
a meeting; 11 kills land on the exact meeting tick.

**What.** On meeting close: teleport every living player to CAFETERIA (forcing a vent exit — and *that
exit is witnessed by everyone*, which is a great beat), give a 2-tick kill grace, and mark every body that
any living crewmate has already perceived as discovered so the map does not carry silent corpses forward.

**Effect.** The meeting becomes a *place*, which is the single biggest believability win available. It
also creates the Among-Us beat the sim entirely lacks: the scatter. A spectator can watch who follows
whom out of the cafeteria. And it removes the free execution of the person who just called the meeting.
Note the vent-flush is a *crew buff* (a forced public vent exit) and the gather is an *impostor buff*
(everyone is adjacent again) — they roughly cancel.
**Size** M. **Risk** substrate + real balance shift; determinism fine (deterministic teleport);
no firewall impact; comparability broken.
**Measure** reporter-death-within-3 (15.7% → ~0); venting participants (9.8% → 0); corpses surviving a
meeting (verified 478/478 single-body consumption today); impostor win rate delta; ticks between meetings.

---

### #4 — Put a time of death on the body
**Addresses** G-7 (single-source in s1, listed for verification, mechanism unambiguous in the dumps).
**963/963** `found_body` observations carry the *report* tick; `obs.tick − true kill tick` has median 4,
mean 4.62, max 30, and **zero exact matches**.

**What.** Add `died_at_tick` (or, if precision feels too generous, a `FRESH (≤2 ticks)` / `COLD (older)`
band) to the `found_body` observation and to the meeting's opening frame, and point the roll-call at *that*
window rather than at the report tick.

**Effect.** This is the highest-leverage cheap information fix in the whole corpus. Today the meeting
interrogates the window in which the killer had already left — seed 2 m0 opens
*"I found poor p-2 cold as a cucumber… just a tick ago"* for a body killed at t4 and reported at t7, and
the whole roll-call then litigates t5–t7. Fix this and every alibi in the room becomes meaningful at once,
which is what makes items #1 and #10 pay off. Watchability: the crew starts asking the right question.
**Size** S–M. **Risk** substrate; big shift in what alibis are worth → comparability definitely broken;
no determinism/firewall risk. Design call: exact tick is arguably *too* much information for a corpse —
I'd ship the FRESH/COLD band first and measure.
**Measure** fraction of meetings whose debated window contains the true kill tick (≈0 today → target >80%);
ejection precision; `alibi_vs_sighting` flag count (should fall as windows stop being arbitrary).

---

### #5 — Rebuild the memory render: coalesce, drop the lobby block, sort by decision-relevance
**Addresses** G-34 and §0.4 above. 66.1% of every memory block is bare co-presence/movement; hard evidence
is **1.54%** of lines; **49.8% of snapshots contain zero hard-evidence line**; duplicate `(subject, room)`
rows are 23.1–23.7%; the constant tick-0 lobby block is 14.4–14.7% (19.7–20.7% in 4p1i); and under budget
pressure **365/456** transitions shed prior-meeting testimony while keeping the lobby block intact.

**What.** (a) Collapse repeated co-presence into spans: `[t 30–47] with p-9 in CAFETERIA (idle)`.
(b) Drop the tick-0 block whenever it is the full roster — it is identical in every game ever played.
(c) Sort by decision-relevance *for this meeting*: everything inside the kill window first, then hard
evidence, then the rest — not "most salient first" as currently ordered, which buried p-9's decisive
EAST_HALL row 22 lines down while surfacing twelve copies of the same cafeteria row.
(d) Give every row an `[obs …]` id (24.5% have none today and are therefore un-citable).

**Effect.** The cheapest reasoning-quality win available: the models mostly aren't fabricating, they're
reading the top of a bad list. Frees ~38% of the block so testimony stops being the first thing shed.
**Size** S–M. **Risk** substrate (changes prompts as-seen) → re-record; no firewall/determinism risk.
**Measure** crew `saw_player` claims contradicted by the speaker's own record (12.0–12.2% → <4%);
lines per snapshot; % of snapshots with ≥1 hard-evidence line (50.2% → >80%); un-citable line share.

---

### #6 — Ground the prosecution the way the vouch side is already grounded
**Addresses** G-2's mechanism (verify-G-2). `grounded_vouch_subjects` (`meetings/transcript.py:2749`)
checks the speaker's **own typed record** before an exculpatory vouch counts. `_detect_alibi_vs_sightings`
(`transcript.py:2379-2494`) never inspects the sighter's record at all — `_iter_sightings`
(`:2170-2179`) yields *every* `SawPlayerObservation` unfiltered. Result: **63.5%** of resolvable
sighting-sides were never perceived by that speaker at that tick. The asymmetry is exactly backwards:
the exonerating channel is audited, the convicting channel is not.

**What.** For a STRONG `alibi_vs_sighting`, require (a) the sighting is in the sighter's own record within
±1 tick, **and** (b) two independent sighters, **or** a physical-layer corroborant — i.e. converge it onto
the `alibi_vs_physical` rule that already scores 100%. Suppress when the sighting's source row is a
`move A→B` transition (12.4% of these flags) or when the alibi window is a single tick equal to the
sighting tick (59% of windows are one tick; 84.5% of flags fire at an endpoint).

**Effect.** Turns an anti-informative channel into an informative one, and closes the path where an
**impostor manufactures a "VERIFIED" weapon** (15.1% of these flags are IMPOSTOR→crew sightings — exactly
what happened to p-1 in seed 17 m0, where p-4* invented `saw_player p-1 EAST_HALL @6`).
**Size** M. **Risk** substrate; deterministic pure function of transcript+records; no firewall risk;
comparability broken. Sequence *after* #1, or you will be grounding against a record that is itself wrong.
**Measure** flag count and precision; % of flags whose sighting side is grounded (36.5% → 100%);
impostor-authored flag share (15.1% → ~0).

---

### #7 — Give finished crewmates a job: escort, sweep, patrol
**Addresses** G-15 (13.0% idle-with-tasks-done agent-ticks; 10 of 13 reports raised it), plus G-6
(21.6% of bodies never reported; 96.5% of those in a room no crewmate re-enters) and §0.2.

**What.** Replace the `wait` terminal state with a priority list: (a) escort the nearest living crewmate
who still has pending tasks; (b) sweep the least-recently-visited rooms for bodies; (c) fall back to the
cafeteria/button. No new mechanics, no new perception — just a non-degenerate terminal policy.

**Effect.** One change hits four findings: the dead time, the never-found bodies, the **79.7% of kills with
no third party in the room**, and the endgame conveyor where the last tasker walks the map alone (seed 17
t28–t47 literally shows three idle crewmates watching p-5 die). It is the only proposal that raises
**witness density**, which every other evidence channel depends on. Watchability: the map stops being three
statues and a lone walker, and the impostor acquires a real problem — crowds.
**Size** M (tactical FSM). **Risk** substrate; a large crew buff (must be paid for — see §0.7); determinism
fine if the escort target is chosen by a deterministic key; no firewall risk.
**Measure** kills with no third party (79.7% → <60%); never-reported bodies (21.6% → <10%);
idle-with-tasks-done (13.0% → <3%); impostor win rate (expect a fall — budget for it).

---

### #8 — Symmetric roll-call: every turn carries exactly one `whereabouts`
**Addresses** G-22. Crew turns carry a `whereabouts` **99.6–100%** of the time; impostor turns
**49.0% / 50.0% / 20.5% / 12.5%**. `P(impostor | turn has no whereabouts)` = **97.7–100%**. The impostor
persona instructs "explain nothing about your own whereabouts" — a prompt-manufactured tell that also
*removes the impostor's only chance to lie in a falsifiable way*. Today only the crew produces falsifiable
statements, and s4 shows answering is net-negative for a crewmate.

**What.** Require exactly one `whereabouts` per turn from everyone (turn on the recorded-OFF
`impostor_roll_call`), and render a refusal explicitly (`p-7 declined to state their whereabouts`) so
silence stops being free and invisible.

**Effect.** This is what makes `alibi_vs_sighting` *interesting* rather than noisy: a liar who must commit
to a room can be caught by a real witness. It also converts the impostor from "says nothing structured"
into an actual bluffing agent, which is the single biggest watchability upgrade available in the dialogue.
**Size** S (prompt + validator). **Risk** prompt version cascade; balance shift toward crew; firewall must
be re-checked (an impostor's forced self-placement must never leak the partner's position).
**Measure** `P(impostor | no whereabouts)` → ~chance; impostor `whereabouts` truth rate (currently 46–48%
false, i.e. they already lie when they speak); alibi-flag impostor-subject share; ejection precision.

---

### #9 — Exempt dead/ejected subjects from "speak your vent FIRST", and persist meeting outcomes in memory
**Addresses** G-23 and G-35. **68 (samples) / 232 (ml)** `saw_vent` observations name a player already dead
or ejected; **5.0–5.5%** of all turns have their accusation struck for naming a corpse; no memory line
anywhere records who was ejected or why.

**What.** (a) Add "unless the subject is already dead or ejected" to the always-speak-your-vent rule.
(b) Write outcomes into memory: `[meeting 1] p-4 was EJECTED (7–1). p-4 was an IMPOSTOR.` and
`p-8's vent sighting of p-4 was VERIFIED.` (c) Keep testimony as *content* — `p-8 says he saw p-4 vent in
ENGINEERING at tick 11` — not the current stub `CLAIM by p-8 (unverified): accused p-4`.

**Effect.** I watched the cost of not having this in seed 2: at m2 **and** m3, long after p-4 was ejected
and confirmed, p-8 still opens with *"[invalid accusation target 'p-4' dropped] I… saw p-4 vent in
ENGINEERING at tick 11"* and p-9 still corroborates it — two of four remaining turns, in the last two
meetings of the game, spent on a closed case. Elsewhere the crew ends up branding its own vent witnesses
liars (s6 m2: *"You're fabricating a dead man's sin"*). Fixing this recovers ~5% of all turns and stops the
crew destroying its own credibility.
**Size** S. **Risk** prompt cascade for (a); substrate for (b)/(c); no firewall/determinism risk.
**Measure** `saw_vent` naming a corpse → 0; struck-accusation rate 5.0–5.5% → 0; zero-content meeting count.

---

### #10 — Text hygiene and spectator honesty
**Addresses** G-25 / G-26 / G-27 / G-28 / G-29.

**What.** (a) Strip `[invalid accusation target 'p-4' dropped]` and friends from `free_text` before it
reaches the transcript — 5.1–5.5% of turns start with one, and they are rendered verbatim into every later
speaker's prompt (`ReplayLoader` already parses the *ballot* markers into chips; do the same for turns).
(b) Parameterise the persona by impostor count — "a hidden impostor" appears in **628/628** two-impostor
meetings' prompts, and the crew visibly reasons "the real killer is already ejected" from it; also fix
`"p-4 are your fellow saboteurs."` (c) Ban the scaffolding from the characters' mouths — *"Max suspicion is
0.55, below the 0.60 threshold"* is spoken 208 times corpus-wide. (d) Show ballot redirects rather than
silently rewriting the target while keeping the model's rationale (84 ballots argue for a player they do
not vote for). (e) Mask impostor role-confessions on the spectator surface (15.6–15.9% of impostor ballots
say it outright: *"I am the impostor. Voting is suicide."*).

**Effect.** Pure watchability, and (b) demonstrably shapes crew reasoning, so it is not cosmetic.
**Size** S. **Risk** prompt cascade for (b)/(c); (a)/(d)/(e) are rendering-only but still change
prompts-as-seen → re-record; no firewall/determinism risk.
**Measure** husk occurrences in `free_text` → 0; "0.60 threshold" mentions → 0; a qualitative read of ten
meetings by someone who has not seen the corpus.

---

### #11 — A `saw_kill` observation and a `kill_sighting/strong` flag ranked above every alibi flag
**Addresses** G-8. The turn schema has no witnessed-kill shape (`saw_player / completed_task / found_body /
saw_vent / whereabouts`) and the contradiction vocabulary has no kill kind, so *"I watched them do it"*
reaches peers as a **+0.08** belief nudge. 4p1i seed 22: p-3 holds `[tick 7] You witnessed p-4 kill in
CAFETERIA`, opens with it at confidence 1.0, no flag fires, the meeting SKIPs, the crew loses.

**What.** Add the observation type, ground it against the witness's own record exactly as `vent_sighting`
is, and rank it at or above `vent_sighting` in the PROOF block.

**Effect.** Closes the most absurd hole in the information design. **But** note §0.2: with 79.7–98.4% of
kills unwitnessed, this channel will barely fire until #7 raises witness density — so its real value is
as the *payoff* for #7 rather than standalone.
**Size** M. **Risk** substrate; changes the eject distribution; no firewall risk.
**Measure** `kill_sighting` flags per 100 games (expect ~2 today, ~15 after #7); precision (should be 100%);
share of ejections.

---

### #12 — Let converging independent testimony reach the gate
**Addresses** G-19 / G-20. Spoken accusation confidence → P(target is impostor): 0.5→48%, **0.6→28%,
0.7→20%, 0.8→20%**, 0.9→92%, 1.0→100% — the mid band is *below* the ~25% baseline. So today the gate is
right to ignore speech. But that also means **s6 m1's three independent crew each naming the true impostor
at 0.6 produced `leader: None` and five SKIPs**, and 1008 m1's correct accusation lost to
*"highest suspicion 0.55, below the 0.60 threshold"*.

**What.** Admit a soft signal to the gate: ≥3 *independent* accusers of one target whose cited evidence ids
are disjoint, or 2 accusers plus a physical corroborant. Also revisit SKIP-as-plurality-target: impostors
SKIP 75–95% of ballots, and of the 78 SKIPPED meetings with ≥1 eject ballot, **39 had a real impostor as
the sole non-SKIP leader** — two abstentions currently outvote two crewmates who agree.

**Effect.** The first mechanism by which *discussion* changes an outcome. High upside for watchability
(the meeting can finally build to something) and high risk of amplifying noise.
**Size** M. **Risk** substrate; **this is the riskiest item in the list** — the mid-confidence band is
below chance *today*, so it must ship strictly after #1/#5/#6 have fixed the reason why. Determinism fine.
**Measure** `flag ⇒ EJECT` prediction accuracy (88.5–100% → target <70%); count and precision of ejections
carrying no strong flag (must be ≥ the vent channel's neighbourhood, not the alibi channel's).

---

### #13 — Make sabotage a real clock (and give 4p1i a second act)
**Addresses** G-40 / G-43. **32 sabotages set-wide, none ever times out**; **0 sabotages in 100 4p1i games**;
and per §0.1 **no impostor has ever won by anything but parity**. Agents even reference *"when the lights
went out"* in games with no lights sabotage.

**What.** Give reactor a hard countdown that ends the game for the impostors if it expires; require two
crew in two different rooms to repair it (the classic split); let the impostor policy fire it on a pressure
rule when nothing has happened for N ticks. For 4p1i specifically: 3 total tasks means the crew often wins
in 4–9 ticks off one meeting — either raise tasks-per-crewmate or make sabotage the second act.

**Effect.** The only proposal that changes the **tension curve** rather than the evidence economy. Today
the between-meeting stretch is flat: my census finds 44 dead-air runs of ≥5 consecutive event-free ticks in
samples/9p2i (max 11) and 103 in ml/9p2i (max 13). A countdown is a spectator's clock and a forced regroup
is a spectator's map moment. It also hands the impostor a second win condition, which is the fairest way to
pay for items #1–#7.
**Size** M–L. **Risk** a **new win condition** breaks eval comparability outright and needs its own
baseline; determinism fine; no firewall risk. Treat as its own wave.
**Measure** sabotages per game; impostor wins by SABOTAGE; dead-air runs ≥5 ticks (44 → target <15);
4p1i median game length (12 ticks → target ~20).

---

### #14 — Persist the vote-time conviction and give the accused one reply
**Addresses** G-21 / G-24 / G-30. Vote-time lift **+0.209 → +0.040 persisted = 19.1% retention**; the belief
scale is bimodal with **essentially nothing between 0.65 and 0.90**, so circumstantial conviction is
literally unrepresentable; **553/1,542 accusations (73%) are never answered**; the reactive chain is one
reply long in 126/165 and 341/463 meetings.

**What.** (a) Write back ≥50% of the vote-time lift so meetings compound. (b) Allow one `opt_in` accusation
to re-open the reply chain, capped at two extra turns, so the accused can answer. (c) Fix the confidence
ladder so the 0.65–0.90 band is reachable.

**Effect.** Turns four independent one-act meetings into a rising story. Watching seed 2, the crew *does*
converge on p-7 at m0 (two eject ballots at 0.62, four SKIPs listing p-7 as the alt) and then arrives at m2
with an empty slate. Retention would have ended that game two meetings early. And letting the accused speak
back is the thing that makes real social deduction watchable at all.
**Size** M. **Risk** substrate; **+30–50% LLM calls per meeting** (real cost); determinism fine; belief
write-back must not carry role information across the firewall.
**Measure** belief retention (19.1% → ≥50%); ejection precision by meeting index; % of accusations answered
(27% → >60%); the 0.65–0.90 belief-band population.

---

### #15 — Impostor FSM: stop stalking ghosts, peek before venting, dwell instead of pendulum
**Addresses** G-12 / G-13 / G-39. `_confirmed_dead` is derived only from bodies the impostor itself saw
(`agents/tactical/impostor_policy.py:813-838`), so ejected players stay top-ranked kill targets for the full
30-tick staleness window — in seed 36 the impostors **lost a won game** pacing ADMIN↔WEST_HALL after an
ejected player. Vent exits have no witness check, so the impostor walks out of a wall in front of a tasking
crewmate 56.5–59.2% of the time. The opening is a memorised script (first kill at t4/t5 in 43/50 games;
10/10 identical in one 4p1i sample).

**What.** Fold meeting outcomes into `confirmed_dead`; invalidate a stale sighting on arrival; never exit a
vent into a room the impostor can already *see* is occupied (it has adjacent vision — in seed 23 t7, p-6*
could see p-5 in ENGINEERING from STORAGE and vented into it anyway); don't reflex-vent after every kill;
replace the A↔B pendulum with a dwell that fakes a task, which co-located crew *can* perceive as `task`.

**Effect.** Removes the largest source of dead time and makes the impostor read as a player rather than a
subroutine. **Sequencing is critical**: this directly suppresses the channel carrying 71% of all ejections,
so it must land only after #4/#6/#7/#11 have given the crew a replacement. Ship it first and the crew
win rate falls off a cliff.
**Size** M. **Risk** the largest *balance* risk in the list; determinism fine; no firewall risk.
**Measure** vent exits witnessed (56.5% → ~35%); ticks spent targeting a dead player (→ 0); ejection channel
mix; crew win rate (the gate).

---

## 2. Suggested shipping order

1. **Wave A (information repair, mostly cheap):** #1, #2, #5, #9, #10 — one combined re-record.
2. **Wave B (evidence economy):** #4, #6, #8, #11.
3. **Wave C (world + pacing):** #3, #7, then #13 as its own baselined wave.
4. **Wave D (only after A–C measure clean):** #12, #14, #15.

Items #12 and #15 are the two that will look wrong if run early; both depend on repairs above them.

---

## 3. Three things I would NOT change

### N-1 — The vent as the one certain tell. Leave it alone.
`vent_sighting` is **440/440 precise**, drives **71% of ejections**, and **96.7–97.1% of held vents convert
to the correct ejection**. Every good social-deduction game needs exactly one channel that is *certain* —
Among Us's visual task, Blood on the Clocktower's Slayer, Werewolf's seer. It is the anchor the whole
information economy hangs on, and it is the one thing in this simulator that works perfectly.
There will be a temptation, once #6 and #11 land, to "balance" it by adding noise (a chance the witness is
wrong, a weak vent flag, a vent that fires from an adjacent room). **Don't.** The problem was never that
the vent is too strong; it is that everything *else* is random, so the vent looks like the whole game.
Fix the other channels. And be careful with #15: an impostor policy that gets *too* good at never being
seen venting would silently delete the crew's only reliable win.

### N-2 — The crew's same-room-only vision (the Task-13.8 asymmetry).
It looks unfair and it produces genuine absurdity — a crewmate stood one doorway from **41% of all murders**
and perceived nothing, **327/327**, while the killer's partner watches from next door. Reports repeatedly
flag it as a bug-shaped design choice, and `canonical_1.yaml:52-58` still *documents* uniform adjacency,
which should be corrected. But the asymmetry is the forcing function that makes the meeting exist at all:
give crew adjacent vision and most kills become directly witnessed, deliberation collapses into reporting,
and the LLM layer has nothing left to do. The right repair is s1's narrow one — extend crew perception to
adjacent-room **bodies only, never players**. That kills the "walked past the corpse" absurdity and much of
the 21.6% never-found rate while preserving the epistemic gap the whole game is built on.

### N-3 — SKIP as a first-class outcome, and the structured round-robin protocol.
39% of meetings carry zero flags and correctly skip; a design that forces an ejection every meeting is a
design where the crew wins by attrition and the impostor's only skill is surviving arithmetic. SKIP is the
honest answer to "we have nothing", and it should stay cheap. (Item #12's narrow fix — abstentions should
not out-vote agreement — is a *tally* change, not an argument for removing SKIP.)
Likewise the protocol: one turn each, typed claims, cited observation ids, ballots with citations. It reads
as mechanical, and there will be a pull toward free-form chat for "believability". That would be a
catastrophe for this project specifically — the typed layer is why citation hygiene is currently perfect
(**0 dangling observation ids, 0 mis-owned ids, 0 dangling turn ids across 3,814 ballots; 0 self-votes;
0 dead targets**), why the teammate firewall is provably airtight (**0/929 impostor ballots name a
partner**), and why any of this is measurable at all. Add a reply round *inside* the structure (#14b);
never replace the structure.

---

## 4. Scripts

`/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/ideas-game-designer/pacing.py`
— dead-air runs, idle-with-tasks-done, zero-flag meetings, solo-kill rate, over all 300 committed games.
