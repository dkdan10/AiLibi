# Track A — Collated master findings (de-duplicated)

Sources: 13 reports under `scratchpad/reports/A/` — watchers `w1`–`w8` (per-game spectator passes over
`replays/samples/9p2i`, `replays/samples/4p1i`, `replays/ml_corpus/9p2i`), specialists `s1` (body/kill/report
lifecycle, 300 games), `s2` (movement/positions/pacing, 300 games), `s3` (meeting decisions, 707 meetings),
`s4` (information economy & beliefs, 300 games), plus `ux-visual-pass-lead` (spectator UI).

Legend — **category**: `bug` (looks broken) · `design-hole` (works as specified; the spec hurts the game) ·
`reasoning-quality` (LLM output quality) · `watchability` (spectator experience) · `wording/prompt`.
**severity**: `P0` breaks believability or correctness of the core loop · `P1` materially degrades it ·
`P2` polish. **corrob** = number of independent reports that raised it.

---

## A. The innocent-ejection machine (the single biggest cluster)

### G-1 — Crew have no record of where *they* were, but the roll-call demands one
**Claim.** Rendered memory contains no "you were in ROOM at tick N" line (own room appears only inside the
`You completed X (you were in Y)` suffix), yet the accusation prompt orders every speaker to answer the
roll-call with a `whereabouts` "copied from your own record" — so ~20% of crew self-placements are invented,
and those inventions are the primary cause of innocent ejections.
**Category** design-hole (information rendering) · **Severity** P0 · **corrob 10**
(w1, w2, w3, w4, w5, w7, w8, s2 Q6, s3 F2/D3, s4 D4)
**Numbers.** Crew `whereabouts` false 148/723 = 20.5% (samples/9p2i), 416/2038 = 20.4% (ml/9p2i), 9.0% / 13.9%
in 4p1i (s3, s2 independently). 58/79 (73.4%) of all innocent ejections in the corpus trace to the victim
mis-stating its own position; 74/79 (93.7%) carry an `alibi_vs_sighting` flag (s3).
**Exemplars.** samples/9p2i s30 m3 p-7 ("MEDBAY at 39", was CAFETERIA t32–39 → ejected); s31 m1 p-1 (3 strong
flags, ejected 6–1, both p-1 and p-8 read "You saw X move from A to B" as "I was in B"); s12 m0 p-3; s39 m0 p-1;
s8 m4 p-9; s36 m2 p-6; s42 m1 p-9; s7 m2 p-6; s10 m0 p-1; s13 m0 (three innocents flagged at once);
4p1i s41 p-4 (the vent witness, ejected); 4p1i s10 p-3 (`whereabouts tick 1 EAST_HALL`, never left CAFETERIA);
ml/9p2i 1061 m1/m2, 1089 m4, 1144 m2, 1111 m3.

### G-2 — `alibi_vs_sighting` is speech-vs-speech, is labelled "VERIFIED evidence", and is below chance
**Claim.** A STRONG flag is minted from one spoken alibi vs one spoken sighting with no grounding of either
side against the speaker's own record, then the ballot prompt tells voters "each flag below is VERIFIED
evidence… never side with an unverified counter-accusation over a verified flag".
**Category** design-hole (borderline bug) · **Severity** P0 · **corrob 9** (w1, w2, w3, w4, w5, w7, w8, s3 D2/F1, s4 B1)
**Numbers.** Precision: `vent_sighting` 440/440 = 100%; `alibi_vs_sighting` strong 8.5% (samples/9p2i, 4/47) and
19.7% (ml/9p2i, 28/142) — s3; s4 measures the same class at 11.8% / 15.9% vs a ~25–29% random baseline, and
`alibi_conflict` at 0/25. It still ejects its subject ~47% of the time. 45.5% of these flags are not backed by
the flagging speaker's own memory (18.9% wrong room, 13.7% no row at all, 12.4% a `move A→B` line re-spoken as
a placement). 84.5% fire at an alibi *endpoint* tick; 59% of alibi windows are a single tick.
**Provenance of the sighting** (ml/9p2i): CREW→crew 69.4%, IMPOSTOR→crew 15.1% (the impostor manufacturing a
"VERIFIED" weapon), CREW→impostor 14.2%, IMPOSTOR→impostor 1.7% (s4).
**Exemplars.** samples/9p2i seed 17 m0: honest vent witness p-1 ejected 7–1 after impostor p-4 fabricates
`saw_player p-1 EAST_HALL @6`; p-8's ballot: *"This verified contradiction proves p-1 is lying."*
seed 23 m1 (innocent p-4 ejected on p-7*'s true adjacent-vision sighting vs p-4's invented MEDBAY);
seed 8 m4 (p-7 votes out p-9 who had stood beside it for 5 ticks); 4p1i seed 41 (one-tick slip weighted
0.80 = a witnessed vent's 0.80).

### G-3 — Task redistribution mints FALSE "You completed <task>" memory lines
**Claim.** When a dead crewmate's tasks are re-keyed to a living one (`dead_task_rule: redistribute`), the
memory store infers a completion from any change of `pending_task_id` — an inference whose stated invariant
("the owned set only ever shrinks") the redistribute rule breaks — so agents are shown, and then speak,
completions that never happened.
**Category** bug · **Severity** P0 · **corrob 5** (w1, w3, w5, w6, and w8's endgame-conveyor thread)
**Code cited by reporters.** `agents/memory/store.py:1153-1200` vs `engine/tick.py:329-353` /
`engine/maps/canonical_1.yaml dead_task_rule: redistribute`.
**Exemplars.** samples/9p2i s2 p-1 "[tick 5] You completed submit_scan" (was 3/10) and p-3 "completed
log_findings" twice; s11 p-6 "[tick 14] You completed upload_logs" (never did it; sworn as an alibi → STRONG
flag); s13 p-2 twice; s15 p-1; s17 p-1; s1 p-1 with `tasks 0/5`; 4p1i s33 p-2 (upload_logs at 3/7),
s47 p-1 (spoken at the table: "I was just finishing up in Medbay"), s29/s41/s1/s10 reporters.
**Second-order effects** (same mechanic, separate finding G-22): mid-task abandonment and the body-beacon walk.

### G-4 — Hallucinated crew testimony, including fabricated `saw_vent`, renders as fact
**Claim.** Crew speak placements they could not have perceived; some speak first-hand vent sightings that exist
in neither their memory nor the engine, and the transcript renders those identically to real ones
(`tick 30: witnessed p-8 VENT in ENGINEERING (only the impostor can vent).`).
**Category** bug (rendering) + reasoning-quality · **Severity** P1 · **corrob 6** (s3 B3/Q3, s4, w1, w2, w3, w7)
**Numbers.** 12.0–12.2% of crew `saw_player` claims in 9p2i are placements the speaker's own recorded field of
view could not contain; 7.9–8.2% put the subject in the wrong room; 1.0–1.2% are lifted verbatim from
`[meeting] CLAIM … (unverified)` memory rows; 1.3–2.2% are echoes of an earlier speaker in the same meeting.
Impostors fabricate *less* than crew (5.3–5.6%). 8 `saw_vent` claims corpus-wide are wholly ungrounded (s3).
**Exemplars.** ml/9p2i 1115 m1 — four crewmates each claim a first-hand vent at tick 30; three have no vent line
at all; all five ballots land at confidence 1.00. ml/9p2i 1033 — p-6 sustains an invented vent + invented kill
across two meetings; the innocent-of-that-act p-7 ejected 5–2. samples/9p2i s2 m3 p-9 launders p-3's testimony
into its own eyewitness `saw_player p-7 STORAGE @21`; s8 m1 p-7 "I personally witnessed p-3 vent" (no such line);
1008 m0 p-8; 1061 m1 p-6; 1144 p-5 (×4 meetings).

---

## B. World-sim holes that break believability

### G-5 — No position reset and no cooldown reset after a meeting
**Claim.** Meetings are disembodied: nobody gathers, nobody is moved, kill cooldowns keep running, so the
impostor resumes standing next to the person it just debated and kills them 1–3 ticks later.
**Category** design-hole · **Severity** P0 · **corrob 12** (all of w1–w8, s1 §13, s2 D1, s3, s4 context)
**Numbers.** 707 meetings: all living agents in CAFETERIA in 0/39, 0/165, 0/40, 3/463; mean fraction present
0.27, and *lower* the tick after (0.10–0.19) — no gather, no reset (s1, s2). 9.7–10.8% of meetings have at least
one participant speaking **from inside a vent** (s2; 69/707). Corpus-wide **89 reporters are killed within 3
ticks of their own meeting** (w7 `corpus_stats.py`); 31 kills land the tick after a meeting (s1).
**Exemplars.** s2 t8 (p-4* kills p-6 one tick after the meeting she spoke at, neither moved); s4 t10/t14 (both
reporters killed 1 tick after their meeting); s6 t10; s40 t10 (reporter killed *in the meeting room*);
1028 t12; 1144 t16; 4p1i s21 t12, s29 t11, s0 t18–19; impostors attending a meeting from inside a vent:
s2 t19, s8 t8, s10 t21, s11 t9, s31 t12, s49 t5.

### G-6 — Only the reported corpse exists; every other body is invisible and unmentioned
**Claim.** A meeting consumes exactly the triggering body; all other corpses stay on the floor with
`discovered_by=None`, invisible to crew, never named in the meeting — deaths enter the fiction only as a
silently shrinking roster.
**Category** design-hole · **Severity** P0 · **corrob 10** (s1 §4/§5, s2 D5, w1, w2, w3, w4, w5, w6, w7, w8)
**Numbers.** 230/798 bodies (28.8%) survive ≥1 meeting (161 survive one, 52 two, 15 three, 2 four);
**22 corpses lay in CAFETERIA — the meeting room — during a meeting**. 172/798 (21.6%) are never reported at all;
168 of those 172 (98%) are in a room no living crewmate ever re-enters. Per-set never-found: 14.7% / 18.6%
(9p2i) and 42.6% / 47.3% (4p1i) (s1, s2 agree).
**Exemplars.** samples/9p2i s8 t8 — a full meeting in the Cafeteria with p-8's corpse on the floor: seven turns,
seven ballots, "not one syllable about p-8". s2 body-p-6-8 survives m1. s11 body lies in CAFETERIA t4–t15
through two meetings and is then reported as a fresh discovery. Longest: ml/9p2i 1067 p-1 (45 ticks, never
found); samples/9p2i 23 p-1 (41); ml/9p2i 1122 (33, survived 3 meetings); samples/9p2i 4 (29, survived 4).

### G-7 — `found_body` never carries the time of death
**Claim.** The discovery observation is stamped with the *report* tick, so every alibi window the meeting
argues over is anchored a median of 4 ticks after the murder.
**Category** design-hole (borderline bug) · **Severity** P0 · **corrob 6** (s1 §10, w2, w4 P6, w6, w7, w8 finding 6)
**Numbers.** 963 `found_body` observations, `obs.tick − true kill tick`: min 1, median 4, mean 4.62, max 30,
**zero exact** (s1). Kill→report latency median 4, p90 11, max 30 over 626 reports.
**Exemplars.** s2 m0 opening: "I found poor p-2 cold as a cucumber… **just a tick ago**" — the kill was at t4,
the report at t7, and the whole subsequent roll-call interrogates t5–t7, the window in which the killer had
already left. s21 m1 debates a "kill window" of ticks 16–21 for a body killed at t5. s17, s8, s32 (20-tick-old
body), s33 (20), s45 (14) all argued as fresh.

### G-8 — A witnessed kill cannot become evidence for anyone but the witness
**Claim.** The turn schema has no witnessed-kill observation shape (`saw_player / completed_task / found_body /
saw_vent / whereabouts`) and the contradiction vocabulary has no kill kind, so "I watched them do it" reaches
peers only as a +0.08 belief nudge.
**Category** design-hole · **Severity** P0 · **corrob 5** (w6 finding 1, w4 finding 3, w2, w5, s4 §1.1)
**Numbers.** `You witnessed pN kill in ROOM.` is **0.02%** of all rendered memory lines (s4). Contradiction kinds
listed by reporters: `alibi_conflict, alibi_vs_sighting, alibi_vs_physical, vent_sighting` — no kill kind.
**Exemplars.** 4p1i seed 22 — p-3 has `[tick 7] You witnessed p-4 kill in CAFETERIA`, opens with it at
confidence 1.0, no flag fires, peer's ballot shows `p-4: 0.58 … this meeting +0.08 … no flag`, meeting SKIPS,
crew then loses the race. 9p2i s45 — two crew witness p-9 kill p-3 at t8; the schema cannot carry it, so p-1's
opening speaks only the vent; at m1 the two eyewitnesses lose 3–3 to an `alibi_vs_sighting` flag on an innocent.
Same shape: s8 t17 (walked in on the killer over a fresh body → SKIP), s30 m1, s33 m1, s12 m1.

### G-9 — Movement perception produces wrong-room sightings and impossible provenance
**Claim.** `You saw X move from A to B [tick T]` has no structured counterpart, so witnesses encode it as
`saw_player(X, A, T)` while X truthfully says B at T — and the departure-room gate is evaluated on post-advance
visibility, so a late arriver "sees" everyone who just left the room.
**Category** bug · **Severity** P0 · **corrob 8** (w1, w2, w3, w4, w7, w8 (2a), s3, s4 §4.1)
**Numbers.** 12.4% of parsed `alibi_vs_sighting` flags have the speaker's own memory saying the subject *moved
out of* the flagged room at that tick (s4). Reporters cite `observation/service.py:491-498` (moved-event gated
on `visibility.visible_rooms`) against `observation/service.py:226` (visibility computed post-advance).
**Exemplars.** seed 23 p-1 "saw" p-5 and p-6 leave EAST_HALL at t10 while never co-present with either →
built its m1 opening accusation on it. seed 12 m0: p-2 and p-9 both hold `[tick 3] You saw p-3 move from MEDBAY
to LABS`, both emit `saw p-3 MEDBAY @3`, p-3 truthfully says LABS → STRONG flag → innocent ejected 6/7.
ml/9p2i 1061 m2 (p-3's footprint line ejects the vent witness p-4 and costs the crew the game). seed 39 m0
(impostor p-3* uses its own movement row to flag the reporter p-1 → 7–0 wrong ejection).

### G-10 — Contested kills are decided 100% by player number
**Claim.** Same-tick "victim moves while killer swings" is resolved by ascending actor id, so a lower-id target
always escapes and a higher-id target never does — a silent per-seat immunity over a quarter of all kill attempts.
**Category** bug (fairness) / documented design · **Severity** P1 · **corrob 6** (s1 §8, s2 B1, w1, w4, w6, w8)
**Numbers.** 246 contested attempts corpus-wide: victim lower-id → escaped **156/156 (100%)**; victim higher-id →
died **90/90 (100%)**. Escape rate by seat: p-1 25%, p-2 19%, p-3 16%, p-4 19%, p-5 20%, p-6 4%, p-7 6%, p-8 2%,
p-9 **0%**. Killers are near-uniform across seats, so this is a pure seat lottery. 188/986 kill actions (19%)
produce nothing: 156 id-order escapes + 32 meeting-tick freezes + **0 cooldown, 0 friendly-fire, 0 unexplained**.
Second symptom: 26/26 vent sightings by an observer standing in neither endpoint room have `observer_id >
venter_id` (`engine/rules.py:29-44` reads pre-move state).
**Dramatic cost.** A near-miss emits no event, no observation, no memory — 156 discarded set-pieces.

### G-11 — Vent/kill witness sets depend on intra-tick id order
**Claim.** Whether a crewmate walking into a room witnesses a vent or a kill depends on whether its id sorts
before the actor's; and an exit's *source-room* witness is credited with seeing someone who was already inside
the vent.
**Category** bug (perception ordering) · **Severity** P1 · **corrob 6** (w2, w3, w4, w6, w8, s2)
**Exemplars.** 4p1i s20 vs s44/s45 — identical geometry, opposite results, decided by id order. s30 t30 — both
impostors exit REACTOR, p-4 "sees" only p-6. s14 t20 — a double vent whose two witnesses are split one each.
s15 t7 / 4p1i s33 t6 — a source-room "witness" who arrived after the venter vanished. s8 t7 — two crew arrive,
only one is a witness.

### G-12 — Impostor FSM stalks ghosts, and it is the engine of dead time
**Claim.** `_confirmed_dead` is derived only from bodies the impostor itself saw, so ejected players and the
partner's unseen victims stay top-ranked kill targets for the full 30-tick staleness window; the FSM walks to a
dead player's last known room, fails to find them, falls through to a pretend task, and repeats — the A↔B
pendulum.
**Category** bug · **Severity** P1 · **corrob 4** (w8 finding 2 with a policy re-run that reproduces recorded
actions byte-for-byte, w4 finding 1 with an independent re-run, w1 finding 3, w2/w3/w7 observed the symptom)
**Code cited.** `agents/tactical/impostor_policy.py:813-838` (`_confirmed_dead_from_bodies`),
`_STALENESS_THRESHOLD = 30` (line ~185), tie-break `sort key (-score, player_id)`.
**Exemplars.** samples/9p2i seed 36 — **the impostors lost a won game**: p-2* with cooldown 0 paced
ADMIN↔WEST_HALL past the lone crewmate finishing the last task, stalking p-6 who was ejected at t34.
seed 42 t41–45 — kill-ready impostor stands IDLE beside three crew while p-1 finishes the last task alone.
seed 31 p-5 t24–t43 stalking the ejected p-1 (alone in REACTOR with p-7 at t27 and t29, no kill).
seed 17 p-2* wastes ~25 ticks on the ejected p-1. seed 32 p-5 t14–t40. seed 10 p-3 oscillates
REACTOR↔ENGINEERING for 13 ticks.

### G-13 — Vent exits are blind and land in occupied rooms; kill→vent is a reflex
**Claim.** VENT_EXIT has no witness check and the enter-guard uses last tick's co-presence, so the impostor
walks out of a wall in front of a tasking crewmate — which is how the crew wins nearly every game it wins.
**Category** design-hole (FSM) · **Severity** P1 · **corrob 8** (w1, w2, w3, w4, w5, w6, w7, s2 D4)
**Numbers.** Vent EXIT seen by a crewmate 56.5% (samples/9p2i) / 59.2% (ml/9p2i); vent ENTER seen only 8.8% /
6.4% (s2) — evidence exists at the emerge, never at the dive. 310/435 ejections (71%) are `vent_sighting` (s3).
**Exemplars.** s23 t7 (p-6* could *see* p-5 in ENGINEERING from STORAGE and vented into it anyway), s5 t7 and
t17, s6 t7 (two witnesses), s33 t7 (two witnesses), s45 t7, s49 t12, 4p1i s20 t7 (visibly occupied destination),
4p1i s2 t8, 4p1i s41 t6.

### G-14 — Crew are blind one room away; impostors are not
**Claim.** Crew visibility is downgraded to same-room-only while impostors keep same-room-and-adjacent, so 41%
of murders happen one doorway from a crewmate who is mechanically incapable of noticing — while the killer's
partner watches comfortably from next door.
**Category** design-hole (deliberate, Task 13.8) · **Severity** P1 · **corrob 7** (s1 §7, w1, w2, w3, w4, w6, w7)
**Numbers.** At the kill tick: a crewmate stood in a room adjacent to the murder in **327/798 kills (41%)**, and
**327/327 perceived nothing**. Cross-room sightings: impostor 3,418 vs crewmate **3** (all vent-channel) in
samples/9p2i; cross-room body sightings: impostor 413, crewmate **0**, ever.
**Side effect** (raised by w2, w3, w4, w7, s4): impostor testimony is the most *accurate* testimony at the table,
and it is what mints "VERIFIED" flags against innocents (15.1% of `alibi_vs_sighting` flags).
**Documentation conflict.** `engine/visibility.py:98-126` applies the asymmetry in code on top of
`canonical_1.yaml:52-58`, which still declares `base: same_room_and_adjacent` "uniform across the map" and
justifies the hub topology by "kills adjacent to Cafeteria are easily witnessed".

### G-15 — Finished crewmates become statues; half of every game is empty
**Claim.** A crewmate with no pending task returns to the hub and emits `wait` forever — the single largest
source of dead time, of never-found bodies, and of the endgame conveyor.
**Category** design-hole · **Severity** P1 · **corrob 12** (all watchers, s1 §5, s2 D2/Q1, s3, s4)
**Numbers.** 48.6% / 45.9% of 9p2i ticks and 61.4% / 59.8% of 4p1i ticks contain no kill, report, vent,
task-completion, meeting or sabotage. 10.3% (samples/9p2i) and 8.0% (ml/9p2i) of ALL living agent-ticks are a
crewmate IDLE at `task_progress == 1.0`; s1 measures 13.9% of crew agent-ticks IDLE-with-tasks-done.
38.5% of 9p2i and 68.5% of 4p1i agent-ticks are spent completely alone; nobody ever escorts anybody.
**Exemplars.** samples/9p2i seed 32 p-9 stands still in CAFETERIA for **36 consecutive ticks** (t20–t55) while
its three remaining teammates are murdered one at a time and the crew loses at 12/14 tasks. seed 31 p-9 30 ticks;
seed 17 p-9 30 ticks; seed 21 p-8 t17–t46; ml/9p2i 1061 p-9 28 ticks; 4p1i s10 p-3 12 ticks, s35 p-3 11 ticks.

### G-16 — Task redistribution is a body-beacon, a progress-bar reversal and a death conveyor
**Claim.** A dead crewmate's tasks are re-keyed to a living one (in practice the lowest-id), who abandons a
half-done task, walks alone to the victim's task room — usually the murder room — and dies there next.
**Category** design-hole · **Severity** P1 · **corrob 7** (w1, w3, w4 P5, w5, w6, w7, w8 finding 7, s2 Q5)
**Numbers.** 485 `task_progress` decreases corpus-wide (s2). In w1's 5-game sample, 9 of 14 body reports were
made by the crewmate who had just inherited the victim's task; in w5's 4p1i sample, 5/5.
**Exemplars.** s2 (all four bodies found by the inheritor); s30 t28/t35/t42 (three consecutive REACTOR kills as
each inheritor walks in alone); s21 REACTOR ×2 then ADMIN ×2; s32 MEDBAY ×2 + ADMIN; 1008 (four crewmates die in
STORAGE on the same inherited `fuel_reserves`); 4p1i s0 t19 (`tp 1.00 → 0.70` on a teammate's death).

### G-17 — The emergency button is a t10 timer, not a decision
**Claim.** Every press in the corpus carries the same canned reason, none is made with a body in view, and the
eligibility rule requires a *fresh* below→above-0.6 crossing, so a crewmate who already suspects someone can
witness them vent and still be unable to call.
**Category** design-hole · **Severity** P1 · **corrob 5** (s1 §12, w1, w3, w4, w8)
**Numbers.** 112 presses → 81 meetings; **112/112 `reason: suspicion_accumulation`**; **0/112 with a body in
view**; 71/112 fire at t10–t11. All 81 emergency meetings carry a `vent_sighting` flag and 78/81 eject an
impostor — the "emergency meeting" is really the vent alarm (s3).
**Exemplars.** s2 — p-3 holds a first-hand vent (belief 1.00) for 15 ticks and never calls, because its
suspicion was already ≈0.6 before the sighting (`crewmate_policy.py:158-166, 224-260`). s3 p-9 the same for 14
ticks. s12 p-4 holds the answer, is blocked by a 6-tick meeting cooldown, and is murdered on the walk to the
button. s31 p-7 takes 8 ticks and a completed task to reach the button; p-8, who saw the same vent, never goes.

### G-18 — Kills land on the meeting tick and inside the meeting room
**Claim.** The tick resolves fully and *then* the meeting opens, so a player can be murdered in the meeting
room on the meeting tick and their death is neither reported nor narrated.
**Category** design-hole · **Severity** P2 · **corrob 4** (s1 §9, s2 D6, w5, w6)
**Numbers.** 145/798 kills (18%) happen in CAFETERIA; **11 kills land on the exact tick a meeting is triggered**;
82 the tick before, 31 the tick after. 32 kill attempts corpus-wide are annihilated by a meeting elsewhere on
the map, at no cooldown cost to the impostor.
**Exemplar.** ml/9p2i 1120 t12 — p-3 completes a task and is murdered in the Cafeteria in the same instant p-8
calls a meeting from MedBay; the meeting convenes with p-3's fresh corpse in the room, skips, and everyone walks
out past it. Also samples/9p2i 41 t11 (kill + report + emergency press in one tick).

---

## C. The meeting doesn't deliberate

### G-19 — Meeting outcome is a function of the flag detector, not of the discussion
**Claim.** "Did a contradiction flag fire" predicts the outcome 88.5–100% of the time; testimony,
corroboration, eyewitness proximity and correct deduction move essentially nothing.
**Category** design-hole · **Severity** P0 · **corrob 11** (s3 D1/F1, s4 §5, w1, w2, w3, w4, w5, w6, w7, w8)
**Numbers.** Prediction accuracy `flag ⇒ EJECT / no flag ⇒ SKIP`: 88.5% (samples/9p2i), 90.3% (ml/9p2i), 97.4%
and 100% (4p1i). `vent_sighting` drives 71% of all ejections. 64/165 and 161/463 meetings end with no ejection.
Spoken accusation confidence → P(target is impostor): 0.5→48%, **0.6→28%, 0.7→20%, 0.8→20%**, 0.9→92%, 1.0→100%
— the mid band is *below* the ~25–29% random baseline (s4, reproduced on both sets).
**Exemplars.** s6 m1 — three crew independently name the impostor at 0.6, gate leader `None`, five SKIP.
s8 m2 — the reporter walked in on the killer beside a fresh body, says so, all SKIP. s23 m2 — the impostor says
"I was alone in Medbay with p-5 just before the end", all SKIP. s30 m1 — five accusers of the right player,
7/7 SKIP. 1008 m1 — the correct accusation, 6 SKIP ("highest suspicion 0.55, below the 0.60 threshold").

### G-20 — The impostor's SKIP bloc is a free blocking vote
**Claim.** SKIP is a first-class plurality target and impostors SKIP ~75–95% of their ballots, so two
abstentions outweigh two crewmates agreeing.
**Category** design-hole · **Severity** P1 · **corrob 4** (s3 F3/D4, s4, w5, w6)
**Numbers.** Impostor SKIP rate 185/245, 512/684, 37/39, 36/40. Of the 78 SKIPPED meetings that had at least one
eject ballot, 75 were skip-bloc and 3 ties — and **in 39 of them the sole non-SKIP leader was a real impostor**.
The paired confidence floor never binds once in 707 meetings. In 4p1i the impostor never once used its ballot as
a weapon (0/9 in w6's sample) though a 1-1-1 swing was available (seed 45).

### G-21 — Meetings do not compound: the vote-time conviction is discarded
**Claim.** The ballot prompt's lifted suspicion table is never written back, so a crew that argues its way to
0.80 on the right player and fails the gate wakes up next meeting at 0.55.
**Category** design-hole · **Severity** P1 · **corrob 3** (s4 D1/D2/D3, w1, w3)
**Numbers.** Mean vote-time lift +0.209 → +0.040 persisted = **19.1% retention** (ml/9p2i, n=471); 24.8%
(samples/9p2i, n=152). The belief scale is bimodal: 71.9% of impostor beliefs and 99.8% of crew beliefs sit in
0.40–0.65, 25.8% of impostor beliefs sit at exactly 1.00, and there is essentially **nothing between 0.65 and
0.90** — circumstantial conviction is unrepresentable. 82.7–86.0% of meeting-0 snapshots have an empty belief
store and 83.8–86.5% of observer rows have a tied argmax.
**Exemplar.** ml/9p2i 1001 m0, four voters on p-2: `0.50 → 0.80 → 0.50` (zero retained).

### G-22 — Two mechanical role tells: the roll-call and the report
**Claim.** The impostor persona instructs "explain nothing about your own whereabouts", so half of all impostor
turns arrive with an empty `observations` array — which no crew turn ever does; and an impostor has never
reported a body or called a meeting in 300 games.
**Category** design-hole (prompt-manufactured) · **Severity** P1 · **corrob 6** (s3 F7/F8/D6, s4 D4, w2, w5, w6, s1 §6)
**Numbers.** Crew turns carrying a `whereabouts`: 99.6% / 99.7% / 100% / 98.8%. Impostor turns: 49.0% / 50.0% /
20.5% / 12.5%. P(impostor | turn has no whereabouts) = **97.7–100%**. Body reports by an impostor: **0/626**;
meeting triggers by an impostor: **0/707** — so `impostor_report.qwen3_6_27b.v3` is a pinned, version-bumped
template with **0 calls out of 7,932** meeting LLM calls.
**Incentive inversion** (s4): answering the roll-call is *net negative* for a crewmate — it creates the one-tick
alibi window that generates 59% of the below-chance `alibi_vs_sighting` flags — while silence is free and
renders nowhere ("no line says p-7 declined to state their whereabouts").

### G-23 — Prompt-mandated re-litigation of a vent whose subject is already out
**Claim.** "A witnessed vent outranks everything else — speak it FIRST… even if you already said it at an
earlier meeting" has no exemption for dead or ejected subjects, so witnesses burn their remaining turns on a
closed case and the validator husk leaks into their spoken text.
**Category** wording/prompt · **Severity** P1 · **corrob 9** (w1, w2, w3, w4, w5(n/a), w6, w7, w8, s3 D8, s4 Q2/8.1)
**Numbers.** 68 (samples/9p2i) and 232 (ml/9p2i) `saw_vent` observations name a player already dead or ejected;
5.0–5.5% of all turns have their accusation struck for naming a corpse.
**Exemplars.** s21 — p-9 re-speaks the same dead vent at m1, m2, m3 and m4. s6 m2 — crew brand their own two
vent witnesses liars ("You're fabricating a dead man's sin") and the surviving impostor amplifies it. s13 m2 and
s15 m1 — the last meeting with 3 crew alive is entirely spent on an ejected impostor. s0 m1, s2 m2, s17 m2 —
whole meetings with no content. 1028 m3/m4 — p-9's fabricated-looking repetition is used by the live impostor.

### G-24 — The meeting is a fixed round-robin wearing a debate costume
**Claim.** Every meeting is exactly `#turns == #ballots == #living`, nobody ever speaks twice, the reactive
chain is one reply long, and the majority of accusations are made in `opt_in` turns that by design cannot be
answered.
**Category** design-hole · **Severity** P2 · **corrob 3** (s3 D5/F6, w2, w6)
**Numbers.** 707/707 meetings; living participation 100%; 1 reply in 126/165 and 341/463 meetings;
**553/1,542 accusations are never answered at all** (73% across sets); 55% of accusations are made in `opt_in`
turns. The "opt-in eligibility" gate (holds a relevant observation) never excludes anybody.

---

## D. Text hygiene, wording, spectator surface

### G-25 — Dev audit markers leak into `free_text` and into other agents' prompts
**Claim.** `[invalid accusation target 'p-N' dropped]` and friends are spliced into spoken text, are rendered
verbatim into the `<transcript>` block of every later speaker's prompt, and reach the spectator surface.
**Category** bug · **Severity** P1 · **corrob 10** (w1, w2, w3, w4, w6, w7, w8, s3 B2/F9/F10, s4)
**Numbers.** 53/971 (5.5%) samples/9p2i turns and 137–139/2,726 (5.1%) ml/9p2i turns begin with a marker.
Ballot markers: `[under-gate eject target … redirected]` 13 + 48, `[invalid target … normalized to SKIP]` 3,
`[teammate target … coerced to SKIP]` 4, `[uncited zero-flag eject … coerced to SKIP]` 1+1. `ReplayLoader`
parses ballot markers into structured chips but **not** turn `free_text`.
**Proof quoted by s3** — p-9's own prompt in seed 2 m2:
`- [headless-seed-2:meeting-2:turn-2] turn 2 (opt_in) — p-8: [invalid accusation target 'p-4' dropped] I… saw p-4 vent…`
**Related** (G-26): the redirect guard rewrites the ballot target and keeps the model's rationale, so 84 eject
ballots argue for a player they do not vote for and 259 SKIP ballots argue explicitly for an ejection; one
coerced impostor ballot surfaces private knowledge: *"[under-gate …] P-1 lies about the vent. **I didn't vent.**"*

### G-26 — Ballot target-redirect makes the tally contradict its own rationale
**Claim.** `guard_ballot_target_graph` rewrites an under-gate eject target to the argmax candidate while keeping
the model's text, so a spectator reads "Vote p-4 out" beside a recorded vote for p-5.
**Category** design-hole (transparency) · **Severity** P2 · **corrob 5** (s3 F10, w2, w3, w4, w8)
**Numbers.** 48 redirects in ml/9p2i, 13 in samples/9p2i; 84/2,170 eject ballots name a different player in the
rationale than in the target. In samples/9p2i seed 8 m3 both crew eject votes were redirected *onto the true
impostor* and still fell one short.

### G-27 — Every 2-impostor prompt says "a hidden impostor" (singular)
**Claim.** The persona line is hardcoded singular in all six `qwen3_6_27b` templates and never conditioned on
the impostor count, so the crew is primed to believe one ejection ends the game — in the same prompt that
privately tells the impostor "Your fellow saboteurs: p-4".
**Category** wording/prompt · **Severity** P1 (cheap, and it shapes crew reasoning) · **corrob 10**
(w1, w2, w3, w4, w7, w8, s3 D7, s4 Q6, ux lead; w5/w6 confirm it is correct for 1-impostor games)
**Numbers.** Present in the first prompt of **165/165 samples/9p2i and 463/463 ml/9p2i meetings (100%)**;
w4 checked 51/51 prompts in one game. Templates cited: `crewmate_report.j2:58`, `accusation_round.j2:79`,
`vote_ballot.j2:74`, `impostor_report.j2:59` + the two `*_roll_call` variants.
**Observed effect.** "The real killer is already ejected" as a SKIP rationale (s8 m1); whole meetings
re-litigating an ejected impostor (G-23). **Grammar nit:** `"Secret: p-4 are your fellow saboteurs."`

### G-28 — Impostor ballot rationales confess the role outright
**Claim.** One in six impostor ballots states the secret in plain text; it never re-enters gameplay, but it is
on the spectator surface and destroys the mystery for anyone reading the ballot panel.
**Category** watchability · **Severity** P2 · **corrob 9** (s4 B2, w1, w2, w3, w4, w5, w6, w7, w8)
**Numbers.** 39/245 (15.9%) samples/9p2i and 107/684 (15.6%) ml/9p2i impostor ballots.
**Verbatim.** *"I am the impostor. Voting is suicide."* (s3 m1) · *"p-2 caught me venting. I am the impostor. I
vote p-2 to die because he is the only one who knows the truth and must be silenced."* (s5 m2) · *"Why trust
p-2's 'direct evidence' when I killed p-3 myself?"* (1000 m0). Same leak in structured `evidence` fields:
`alibi … evidence: ('killed p-8 at tick 5',)` (s12, s7-4p1i).
**Cause** (s4): `vote_ballot.j2:126` tells the impostor to redirect a teammate vote to SKIP and then asks for an
honest rationale "in your own voice".

### G-29 — Threshold arithmetic and stock rationales in the characters' mouths
**Claim.** Agents speak the scaffolding: "Max suspicion 0.55. Below threshold. Skip.", "the 0.60 threshold",
"living candidates", "so I skip to preserve the game state" — and the ballot register collapses into a handful
of verbatim-repeated sentences.
**Category** wording/prompt + reasoning-quality · **Severity** P2 · **corrob 11** (all watchers, s3 Q4)
**Numbers.** "0.60 threshold" quoted 208 times corpus-wide (w7). `"The evidence is too thin to justify an
ejection."` appears verbatim **22×** across independent ml/9p2i games; `"The smoke is too thick to see the
fire…"` **16×**; four stock openings cover ~15% of all ballots.

### G-30 — Confidence is bimodal, not calibrated
**Claim.** Stated confidence encodes which script the model is in ("following the room" vs "a vent flag is on
the table"), not a probability: the 0.80–0.90 bucket is *less* accurate than 0.60–0.70.
**Category** reasoning-quality · **Severity** P2 · **corrob 2** (s3 Q1, s4 Q1)
**Numbers.** Crew eject ballots: 0.60–0.70 → 82.6%/70.0% correct; 0.70–0.80 → 61.3%/66.2%; 0.80–0.90 →
58.1%/69.5%; 0.90–0.96 → 99.1%/99.5%; 0.96–1.00 → 100%. Overall overconfidence +0.068 / +0.036.

### G-31 — Reporter-blame is the default deflection, and it works
**Claim.** The standard reply — impostor or crew — is "you rushed to the scene / called the meeting the moment
you arrived", and crew opt-ins routinely side with it against their own reporter.
**Category** reasoning-quality · **Severity** P1 · **corrob 8** (w2, w3, w4, w5, w6, w7, w8, s3)
**Numbers.** 65/165 meetings have ≥2 formal accusations of the reporter, though only 3 reporters were ever
ejected (the `reporter_exculpation` block works at ballot time but not in speech). 10 of 11 impostor replies in
w3's six games use the identical template.
**Exemplars.** s30 m0/m1, s4 m0/m1 (five accusers of the reporter, then all SKIP), s31 m0 (seven pile on),
s7 m0, s33 m1/m2, 4p1i s44/s45 (crew opt-ins side with the impostor's reporter-blame).

### G-32 — Impostor `found_body` self-incrimination is emitted and ignored
**Claim.** With adjacent-room vision an impostor files structured `found_body` observations for corpses nobody
has reported — a free, hard tell that no contradiction kind consumes and no ballot ever cites.
**Category** design-hole (missed lever) · **Severity** P2 · **corrob 6** (s1 §11, w1, w3, w4 P7, w7, w2)
**Numbers.** 27 spoken before the body's eventual report and 4 for a body **never** reported (crew equivalents:
11 same-tick races and 0).
**Exemplars.** samples/9p2i s32 m0 turn 3 — p-6* files `found_body tick 6 p-2 REACTOR`; that body is not
reported until t25; nobody reacts, and the meeting ejects the honest witness instead. s16 m1 p-9* for a corpse
never reported. s30 p-3* twice; s49 p-9*; 1028 p-5*; 1061 p-8*.

### G-33 — The impostor never uses the genre's best bluff, and never plays its ballot
**Claim.** 0/626 self-reports, 0/707 meeting calls, and (in 4p1i) 9/9 SKIP ballots over an empty belief table
even when one vote would win the game.
**Category** design-hole (missing lever) · **Severity** P2 · **corrob 3** (s1 §6, s3 F8, w6)
**Exemplar.** 4p1i seed 45 — with 3 voters, the impostor plus one crewmate voting the same crewmate ejects them
and wins by parity; the impostor SKIPs at confidence 0.0.

### G-34 — Memory render: 66% co-presence noise, 24% duplicates, and the spawn block outranks social memory
**Claim.** Two thirds of every memory block is undifferentiated co-presence/movement; hard evidence is 1.5% of
lines; and under budget pressure the render sheds prior-meeting testimony while retaining 8 constant tick-0
lobby lines that are identical in every game ever played.
**Category** design-hole · **Severity** P1 · **corrob 6** (s4 §1/B3/D6, w1, w2, w3, w7, w8)
**Numbers.** 66.1% of lines are bare co-presence or movement; hard evidence (body/vent/kill/heard) is 1.54%;
**49.8% of all memory snapshots contain zero hard-evidence line**. Duplicate `(subject, room)` rows 23.1–23.7%;
tick-0 spawn block 14.4–14.7% (19.7–20.7% in 4p1i). 365/456 budget-pressure transitions cut testimony while
keeping the spawn block at full size. 19–23% of belief lines carry no suspicion number at all; 24.5% of memory
lines have no `[obs …]` tag and are therefore un-citable.
**Documentation conflict.** `DESIGN.md:659` already marks per-tick coalescing NOT IMPLEMENTED; `DESIGN.md:660`
claims salience "elides routine task work" — measured, `saw pN task in ROOM` variants are 27% of lines.

### G-35 — Testimony is absorbed as claim stubs, unverified, and meeting outcomes are never recorded
**Claim.** Spoken testimony enters memory only as `[meeting] CLAIM by X (unverified): accused Y` — the *content*
of a vent claim is dropped, no line records who was ejected or why, and an asserted alibi buys a suspicion
discount whether it is true or a lie.
**Category** design-hole · **Severity** P1 · **corrob 7** (s4 D5, w1, w2, w3, w4, w6, w7)
**Numbers.** Testimony is 16.8–17.2% of rendered lines; 55% of belief lines carry a `(alibi: in ROOM at tick N
per pN)` annotation worth −0.04 (crew subject) to **−0.086** (impostor subject) — the liar gets the larger
discount. The `saw pN in ROOM @ tick N` testimony rows (9.7% of lines) have no belief effect at all. In 4p1i the
lever never fires (one-meeting games).
**Exemplar.** s6 — after m0 ejects p-6 on two verified vents, p-7's memory holds only "CLAIM by p-1
(unverified): accused p-6"; by m2 three crew call their own vent witnesses liars.

### G-36 — Duplicate contradiction flags inflate one fact into two or four
**Category** bug · **Severity** P2 · **corrob 2** (s3 B4, s4 §4.2)
**Numbers.** Same sentence rendered up to 3× (samples/9p2i) and 4× (ml/9p2i); 10 and 30 duplicate copies across
186/607 flags, affecting 7 and 23 meetings.
**Exemplar.** seed 7 m2 — the identical `alibi_vs_sighting` sentence against p-6 printed twice; p-6 ejected 4–1.

### G-37 — Agent tick stamps are +1 vs the replay timeline (and own-task lines are −2)
**Claim.** Every agent-facing observation stamped "tick N" describes the world the replay shows at N−1, while
the meeting header's "It is tick N" uses the replay index — so a viewer scrubbing the map can never line up the
dialogue, and an agent copying its own `You completed X (you were in R)` line into a `whereabouts` answer is off
by one inside its own frame.
**Category** bug (spectator consistency; contaminates the flag detector's inputs) · **Severity** P1
**corrob 4 explicit** (s2 B2, s3 F0, and every watcher opened with a hand-derived "tick convention" paragraph —
w1, w2, w3, w4, w5, w6, w7, w8 — which is the same defect experienced as friction)
**Numbers.** 111,283/111,283 memory sighting lines match truth at Δ=−1 and only 51.8% at Δ=0 (s3);
740/748 `saw_vent` and 785/853 `completed_task` observations stamped `event_tick + 1` with **zero** exact
matches (s2); meeting header 771/771 exact. `completed_task` self-position lines match the agent's room at
world N−2, 3,406/3,406.
**Cause cited.** `orchestrator/game.py:1778` builds packets before `advance_tick` at `:1786`; `:1793` records
`input_tick=N` alongside the post-advance state.

### G-38 — Spectator DTO misrepresents four action classes (and the omniscient view never clears bodies)
**Claim.** `AgentTickStateView.current_action` keeps the last *resolved* label, so a fake `do_task` renders as
MOVING/IDLE (never TASK) at exactly the moments the impostor is successfully pretending to work — while
co-located crew correctly see `task`; the emergency press renders REPORT; repair renders TASK. Separately the
frontend map accumulates every kill event and ignores engine truth, so corpses never disappear.
**Category** bug (spectator surface) · **Severity** P1 · **corrob 4** (s2 B3, ux lead, w3, w5)
**Numbers.** 1,747 fake `do_task` intents → IDLE 800 / MOVING 844 / **TASK 0**; `emergency` → REPORT 81;
`repair_sabotage` → TASK 302; 1,964 MOVING-without-motion agent-ticks. Frontend:
`frontend/src/components/MapView.tsx::buildBodyStatesByTick` (lines 229–264) — at seed 2 t29 the map shows FOUR
corpses while engine state has one.

### G-39 — Impostor pairs travel together, and the opening is a memorisable script
**Claim.** One impostor idles at spawn t0–t3 and kills the Cafeteria tasker at t4/t5 in 43/50 games; the two
impostors are co-located ~18–20% of the ticks they are both alive; and nothing in the perception or belief layer
has any notion of repeated co-presence, so the tell costs them nothing and reads as mechanical.
**Category** watchability / design-hole · **Severity** P2 · **corrob 6** (s2 D7, w1, w4, w6, w7, w8)
**Numbers.** First kill at t4 or t5 in 43/50 games; exactly one impostor per game (50/100) sits IDLE in
CAFETERIA for t0–t3; two impostors in the same room 17.9% / 19.6% of both-alive ticks. In w6's 4p1i set the
impostor opening is **10/10 identical** (EAST_HALL → ENGINEERING fake task → first-legal-tick kill).

### G-40 — Sabotage is a walk simulator (and is absent entirely from 4p1i)
**Claim.** 32 sabotages set-wide, none ever times out; the effect is that idle crew shuffle to ENGINEERING and
back — valuable only when the impostor uses it as a lure.
**Category** design-hole · **Severity** P2 · **corrob 5** (w3, w5, w6, w7, w8)
**Numbers.** 0 sabotage actions in 50 4p1i games (w5) and 0/10 in w6's sample; 8 corpus kills within 4 ticks of
a sabotage. Good uses: s17 t41–44 and t51–58, s36 t40, s39 t34, 1089 t35–44.
**Related wording bug.** Agents reference "when the lights went out" in games with no lights sabotage (s36, 1089,
1008) — a figure of speech that reads as a hallucinated event.

### G-41 — Spectator UI: internal jargon and layout on the product surface
**Category** watchability · **Severity** P2 · **corrob 1** (ux lead)
**Details.** Tournament-tab card subtitles carry "(DESIGN.md §11.3)", "Task 9.6 / 10.x, typed on the wire by
12.2", "sentinel — not a KPI"; replay cards show "56/100 MED · INTERNAL HEURISTIC" and unlabelled R1/R2/R3/R7
bars; "4p1i/9p2i" is never expanded. The fixed bottom transport dock takes ~35% of a 900px viewport and clips
the Mind Inspector; at 800×450 the map is entirely hidden. The ballot "CORRECT" badge reveals a target's role
even in unspoiled mode. Positive: the guided tour, the as-agent fog view, and the one-click full-prompt panel
are the project's best demo asset.

---

## E. Verified-clean (do not re-litigate)

| claim | evidence | raised by |
|---|---|---|
| Body plumbing is sound: 0 bodies move room, 0 bodies without a kill event, 0 flicker, **0 double reports (0/626)**, 0 reports from the wrong room, 0 dead players with a room, 0 bodies from ejections | 798 bodies / 626 reports / 7,718 frames | s1 §1 |
| **No teleports**: 0 non-adjacent moves in 16,453 room changes; 911/911 rejected `move` intents are meeting-tick freezes, never illegal targets | 300 games | s2 §2.1 |
| Kill rejections are fully explained: 156 id-order escapes + 32 meeting-tick, **0 cooldown, 0 friendly-fire, 0 unexplained** (of 188/986) | 300 games | s1 §8 |
| Crew reporting is exceptionless: 0/700 crew agent-ticks in a body room ended without a report; report at first-sight+1 in 614/626 | 300 games | s1 §6, s2 |
| Citation hygiene is perfect: 0 dangling observation ids, 0 mis-owned ids, 0 dangling turn ids in 3,814 ballots; 0 self-votes; 0 dead targets | 300 games | s3 §4, s4 §8 |
| Teammate firewall is airtight: 0/929 impostor ballots name a partner; 0 impostor accusations aim at a teammate | 300 games | s3, s4 |
| Everyone gets a turn: living players speak in 99.6–99.9% of slots | 707 meetings | s3 F6, s4 |
| The vent pipeline is complete: 99.6–100% of held vents reach the table, 96.7–97.1% convert to the right ejection, `vent_sighting` 440/440 precise | 300 games | s4 §5, s3 |
| Crew pathing is near-optimal (1.3–1.8% wasted hops in 4p1i, 9–10% in 9p2i) | 300 games | s2 §2.2 |
| Impostor kill *opportunism* is near-perfect once the real cooldown rule is modelled: exactly ONE ≥2-tick missed window in 300 games | 300 games | s2 Q2 (self-corrected) |
| Games do not drag after the decision: 0.3–1.8 ticks of tail; 68–75% of 9p2i games end on the meeting tick | 300 games | s2 §1 |

**One inter-report contradiction to settle.** w2 states "No rejected actions are recorded in the JSONL (`actions`
carries accepted actions only), so kill-attempt rejections cannot be watched." s1, s2, w1, w4, w5 and w6 all read
*attempted* actions out of the same `kind=tick` `actions` array and classify rejections from them. The majority
reading is almost certainly right; w2's per-game conclusions that depend on it should be re-checked.

---

## F. Merged idea list (de-duplicated)

Ordered by (reported value ÷ effort). "Proposed by" lists every report that proposed the same idea.

### Information layer
1. **Render a self-location trail** — `[tick T] You were in ROOM (moved from X)` or a compact path string; ideally
   auto-fill the roll-call `whereabouts` from it and reject/soften any answer that contradicts the agent's own
   record before it reaches the detector. *(w1, w2, w3, w4, w5, w7, w8, s3, s4 — 9 reports; the most-proposed
   change in the track.)*
2. **Split the flag block by evidence category** — the taxonomy already exists in code
   (`api/schemas.py::classify_evidence`, `role_proof` / `cross_statement` / `weak_signal`); say it in the prompt:
   "this is proof" for `vent_sighting` / `alibi_vs_physical` vs "one of these two accounts is wrong and nothing
   here says which" for `alibi_vs_sighting`. *(w1, w2, w5, s3, s4)*
3. **Require two independent sources for a STRONG `alibi_vs_sighting`** (converge it on the `alibi_vs_physical`
   rule that already scores 89–100%); suppress it when the sighting's source row is a `move A→B` transition or
   when the alibi window is a single tick equal to the sighting tick. *(w1, w3, w4, w8, s4)*
4. **Add a `moved` / `saw_move` observation shape** and make the detector treat "A at T−1 → B at T" as consistent
   with "B at T". *(w3, w4, w7, w8)*
5. **Add `died_at_tick` or a `fresh|cold` band to `found_body`** and re-point the meeting's alibi window at it.
   *(s1 — "the highest-leverage cheap fix in the whole lifecycle" — w2, w4, w6, w7, w8)*
6. **Add a `saw_kill` observation + `kill_sighting/strong` contradiction** and weight it above alibi flags.
   *(w4, w5, w6, w2)*
7. **Ship a map card in every meeting prompt** (adjacency + travel ticks + dead ends) and let the detector veto
   "impossible travel" claims mechanically. *(w3, w4, w6, w7)*
8. **Coalesce perception rows and drop the tick-0 spawn block** when it is the full roster; collapse repeated idle
   co-presence into spans ("t30–t47 with p-9 in CAFETERIA"). Frees ~38% of the memory block so testimony stops
   being the first thing shed under budget. *(s4, w1, w2, w7)*
9. **Persist meeting outcomes and verified status in memory** — "p-3 EJECTED at meeting 1", "p-8's vent was
   VERIFIED" — and keep vent testimony as content ("p-8 says he saw p-4 vent") rather than "accused p-4".
   *(w1, w2, w3, w7)*
10. **Render absence**: "no one placed X anywhere between ticks A and B", "p-7 declined to state their
    whereabouts", "the body was found with X and Y present". *(s4, w2, w8)*
11. **Persist the vote-time lift** (even at 50%) so meetings compound and beliefs become a trajectory. *(s4)*
12. **Tag testimony rows with citable ids** so a ballot can cite hearsay — which also makes "testimony decided
    this vote" measurable for the first time. *(s4)*
13. **Ground a spoken `saw_player` against the speaker's own perception log** the way `vent_sighting` already is,
    and render an ungrounded `saw_vent` differently (`claims to have witnessed … (unverified)`). *(w1, w8, s3)*

### World / engine
14. **Resolve movement before kills/vents, or seed-randomise the intra-tick actor order and record it** — closes
    the per-seat immunity and the phantom "vent seen from the wrong room" frames. *(s1, s2 — top of both lists —
    w4, w6)*
15. **Post-meeting reset**: teleport everyone to CAFETERIA (forcing a vent exit), reset or grace the kill
    cooldown, and sweep known bodies. *(w1, w2, w3, w4, w5, w6, w7, w8, s1, s2 — 10 reports.)*
16. **Give finished crew something to do** — patrol unvisited rooms, escort/buddy the last tasker, sweep for
    bodies, or walk to the button. One change closes the statue problem, most of the never-found bodies, a large
    slice of dead time, and creates witnesses. *(w1, w2, w3, w4, w5, w6, w7, w8, s1, s2 — 10 reports.)*
17. **Impostor FSM: fold meeting outcomes into `confirmed_dead`**, break score ties toward the nearest/most-recent
    sighting, invalidate a stale sighting on arrival, and re-plan when holding while a lone crewmate is one room
    away. *(w1, w4, w8; w2, w3, w7 propose the symptom-level version)*
18. **Impostor FSM: peek before venting** — never exit into a room the impostor can already see is occupied (it
    has adjacent vision); don't reflex-vent after every kill; leave the corpse's room. *(w1, w2, w3, w4, w5, w6, w7)*
19. **Emit a `kill_attempt_evaded` event** so the escapee, the meeting and the spectator learn about the 156
    silent near-misses. *(s1, s2)*
20. **Extend crewmate visibility to adjacent-room *bodies only*** (not players) — keeps the Task-13.8 forcing
    function ("crew must infer kills") while removing the "walked past the corpse" absurdity and much of the 22%
    never-found rate. *(s1 — the one proposal that threads the visibility asymmetry)*
21. **Make the vent dive audible one room further** (the `AudibleEvent(kind='vent_use_heard')` channel already
    exists) or leave a short-lived "vent recently used here" trace. *(s2)*
22. **Redistribution hygiene**: derive completions from the engine's `TaskCompleted` event rather than a
    pending-id flip (this is the G-3 fix); never pre-empt a started task; spread inherited tasks round-robin or
    by distance instead of lowest-id; render "You picked up p-2's fix_wiring_cafeteria" so the walk is explicable.
    *(w1, w3, w5, w6)*
23. **Make sabotage matter**: require two players in two rooms to repair so it splits the crew, or give the
    impostor a pressure rule that fires when nothing has happened for N ticks. *(w4, w6, w8)*
24. **Replace the impostor's A↔B pendulum with a dwell** (loiter and fake a task, which crew *can* see as `task`),
    and/or add a `paced_room` perception row so pendulum behaviour becomes accusable. *(s2, w4)*

### Meeting protocol
25. **Symmetric roll-call**: turn on `impostor_roll_call` (recorded OFF) or require every turn to carry exactly one
    `whereabouts`, truthful or not — a liar who must place themselves is what makes `alibi_vs_sighting`
    interesting; today only the crew produces falsifiable statements. *(w2, w3, w5, w6, s3, s4)*
26. **Let evidence other than a flag reach the gate**: same-room-at-discovery, sole-present-at-kill-tick,
    converging independent accusations (three 0.6s on one target), and a self-placement with the victim as a soft
    flag. *(w2, w4, w5, w6, w8)*
27. **Make "you claim to have found a corpse nobody has reported" a contradiction kind** — free, hard, mechanical
    evidence of exactly the kind the crew is starved of. *(s1, w4)*
28. **Add an "absence" contradiction**: X claims to be in room R at tick t; the reporter was in R at t and saw
    nobody. *(w6, w8)*
29. **Exempt dead/ejected subjects from the "always speak your held vent first" rule.** *(w1, w2, w3, w6, w7, w8, s4)*
30. **Give the accused a second turn** — let one `opt_in` accusation re-open the chain (capped); today 73% of
    accusations die unanswered. *(s3)*
31. **Endgame prompt**: when alive ≤ 2×impostors+1, tell voters plainly that a SKIP hands the impostor the win on
    the next kill, and lower the skip threshold. *(w7, w8)*
32. **Reconsider SKIP-as-plurality-bloc** (or exclude abstentions from the denominator) given the confidence floor
    it was paired with never fires once in 707 meetings. *(s3)*
33. **Emergency button**: fire on any new first-hand vent/kill observation regardless of prior level, allow a
    hard-evidence holder to call through the cooldown, and render the vent to the witness before a same-tick
    meeting resolves. *(w1, w4, w8)*
34. **Give the impostor its own ballot prompt** — vote to survive, pile onto the crew's leading suspect, never
    SKIP when one more vote wins the game. *(w6)*

### Text hygiene / spectator
35. **Strip validator husks from `free_text`** before it reaches the transcript and the spectator; parse them into
    structured chips the way ballots already are; never rewrite a ballot target silently — show the redirect.
    *(w1, w2, w3, w4, w6, w7, w8, s3)*
36. **Parameterise the persona by impostor count** ("a hidden impostor" → "hidden impostors"), and fix
    `"p-4 are your fellow saboteurs"`. *(w1, w2, w3, w4, w7, w8, s3, s4)*
37. **Keep the suspicion arithmetic out of the characters' voices**; ban stock rationale strings. *(w2, w4, w6, s3)*
38. **Mask teammate-redirect rationales on the spectator surface** (or instruct a cover reason) the way
    `TEAMMATE_VOTE_TARGET_MARKER` already masks the target. *(s4)*
39. **Re-stamp agent ticks** (or re-label the recorded tick) so the viewer and the dialogue agree, and assert
    `obs.tick <= meeting.tick - 1` in a test. *(s2, s3)*
40. **De-duplicate the contradiction block.** *(s3, s4)*
41. **Fix the frontend body lifecycle** (consume `TickView.bodies` instead of accumulating kill events) and drop
    the internal jargon from product copy; give the bottom dock less of the viewport. *(ux lead)*
42. **Project the real action into the spectator DTO** (`PRETEND_TASK`, `EMERGENCY`, `REPAIR`, `BLOCKED`) instead
    of the last resolved engine label. *(s2, w3, w5, w6)*

### Format
43. **4p1i needs a second act** — 3 tasks means the crew wins in 4–9 ticks and one kill makes the single meeting
    all-or-nothing; either 2 tasks per crewmate or a sabotage that actually fires. *(w5, w6)*

---

## G. The 12 claims most in need of adversarial verification

Ranked by (stakes if true) × (chance the reports got it wrong). Full JSON returned separately.

| # | id | claim | why it needs a second pair of eyes |
|---|---|---|---|
| 1 | G-1 | No self-location in memory → ~20% false crew roll-calls → 73% of innocent ejections | Load-bearing for the whole track; two reports derived the 20% independently but from the same loader |
| 2 | G-2 | `alibi_vs_sighting` STRONG is 8.5–19.7% precise and is framed as "VERIFIED evidence" | s3 and s4 report different precisions for the same class; the prompt quote must be checked verbatim |
| 3 | G-3 | Redistribution mints false "You completed X" memory lines | A clean, falsifiable bug claim; check a case where no task completed and the line still rendered |
| 4 | G-5 | No position reset, no cooldown reset; 89 reporters killed ≤3 ticks after their own meeting | The "89" comes from one script; the per-game exemplars are strong and easy to re-walk |
| 5 | G-6 | 230/798 bodies survive a meeting; 22 lay in the meeting room; 172 never found | Check the "corpse in the meeting room, never mentioned" transcript claim end-to-end |
| 6 | G-7 | 963/963 `found_body` observations carry the report tick, never the death tick | Single-source (s1); high leverage if true |
| 7 | G-8 | A witnessed kill has no observation type and reaches peers as +0.08 | Verify the schema list and the ballot-table delta in a raw prompt |
| 8 | G-10 | 156/156 id-order kill escapes; 0 unexplained rejections; 0 double reports; 0 teleports | Four integrity claims, two positive and two negative — adversarial checks should try to falsify the negatives |
| 9 | G-9 | Movement lines become wrong-room sightings; departure-room provenance leak | Two distinct mechanisms filed together; check whether both are real |
| 10 | G-4 | Crew fabricate `saw_vent` and it renders as proof; 12% of crew sightings are unseeable | Verify at least one ml/9p2i exemplar's four memories directly |
| 11 | G-25 / G-27 | Husks in `free_text` reach other agents' prompts; "a hidden impostor" in 628/628 2-impostor meetings | Both are trivially checkable and both are cheap fixes — worth being certain |
| 12 | G-12 / G-15 | Impostor FSM stalks ejected players for 30 ticks; it lost a won game (seed 36) and drives the dead time | Two reports re-ran the policy offline and matched recorded actions; confirm the seed-36 reconstruction |
