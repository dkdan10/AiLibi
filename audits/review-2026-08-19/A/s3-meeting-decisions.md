# s3 — Meeting decision quality: a mechanical sweep of all 300 replays

**Scope.** Every meeting in `replays/samples/9p2i` (50 games), `replays/ml_corpus/9p2i` (150),
`replays/samples/4p1i` (50), `replays/ml_corpus/4p1i` (50) — **300 games, 707 meetings, 3 934 turns,
3 934 ballots, 830 contradiction flags**. Everything below is re-derived from
`api/replay_loader.py::ReplayLoader` (turns / claims / observations / contradictions / ballots /
gate / `llm_calls`) cross-joined against omniscient truth (`ticks[].agent_states[].room_id`,
`ticks[].events`, `ticks[].bodies`, and the recorded per-tick `visibility` field). No eval module
was reused; every number here comes from my own walk.

Scripts: `…/scratchpad/work/s3-meeting-decisions/{extract,an_a,an_b,an_c,an_d,an_e,an_f,an_g}.py`,
raw outputs `out_{a..g}.txt`.

**Parser sanity-check.** Verified by hand against `watch.py` on two games before trusting anything:
`replays/samples/9p2i` seed 2 (4 meetings, outcomes SKIPPED/EJECTED p-4/SKIPPED/EJECTED p-7, all
gate rows, all 22 ballots) and `replays/samples/4p1i` seed 7 (1 meeting, 3 turns, 3 SKIP ballots) —
byte-for-byte agreement.

---

## 0. One calibration note that changes every timestamp claim

**[VERIFIED] F0 — Agent ticks and replay ticks are off by exactly one, corpus-wide.**
Every agent-facing observation stamped "tick N" describes the world the replay timeline shows at
**tick N−1**. Measured over **111 283** memory sighting lines in all 300 games: the subject's true
room matches at Δ=−1 in **111 283/111 283 (100.0 %)** cases, and only 57 637/111 283 (51.8 %) at
Δ=0. Same for the recorded visibility field (111 283/111 283 at Δ=−1).

Worked example (`samples/9p2i` seed 2): the engine emits
`{'type': 'vent', 'tick': 20, 'actor_id': 'p-7', 'phase': 'exit', 'to_room_id': 'STORAGE'}`, and at
tick 20 p-3's visibility is `[('p-7','STORAGE','vent')]`. p-3's memory says
`- [obs p-3:21:1] [tick 21] You witnessed p-7 vent in STORAGE.` and p-3 says it out loud at
meeting-3: *"I saw p-7 vent in STORAGE at tick 21 — that is the kill."* All 164 `saw_vent`
observations in `samples/9p2i` are stamped engine-event **+1** (164/164).

Cause (opened only to explain the observation): `orchestrator/game.py:1778` builds every agent's
packet *before* `advance_tick` at `:1786`, so a packet stamped `state.tick == N` carries the world
as of the end of tick N−1; `:1793` then records that same `input_tick=N` alongside the **post**-advance
state, which is what `ReplayLoader` serves as `ticks[N]`.

**Judgement:** a spectator-consistency bug. Agents argue in tick coordinates; the map/timeline the
viewer scrubs is one tick ahead of every sentence spoken. It also means the "you were in two places"
arithmetic a viewer would do by hand never lines up. All of my ground-truth checks below are done in
**agent-tick coordinates** (truth table shifted +1), so they measure the agent, not this offset.
Additionally the memory render is internally inconsistent: `You completed X (you were in R)` stamped
tick N matches the agent's own room at world N−2 (3 406/3 406 = 100 %), i.e. one tick *further* back
than the sighting lines stamped the same way — so an agent copying its own task line into a
`whereabouts` answer is off by one inside its own frame.

---

## 1. Corpus shape and headline outcomes

| set | games | meetings | mtgs/game | winner split | reasons |
|---|---|---|---|---|---|
| samples/9p2i | 50 | 165 | 3.30 | CREW 35 / IMP 15 | EJECT 31, PARITY 15, TASKS 4 |
| ml/9p2i | 150 | 463 | 3.09 | CREW 112 / IMP 38 | EJECT 106, PARITY 38, TASKS 6 |
| samples/4p1i | 50 | 39 | 0.78 | CREW 33 / IMP 17 | TASKS 23, PARITY 17, EJECT 10 |
| ml/4p1i | 50 | 40 | 0.80 | CREW 39 / IMP 11 | EJECT 20, TASKS 19, PARITY 11 |

**Ejection accuracy (per meeting):**

| set | meetings | SKIPPED | EJECT impostor | EJECT innocent | eject precision |
|---|---|---|---|---|---|
| samples/9p2i | 165 | 64 (38.8 %) | 78 (47.3 %) | 23 (13.9 %) | **78/101 = 77.2 %** |
| ml/9p2i | 463 | 161 (34.8 %) | 248 (53.6 %) | 54 (11.7 %) | **248/302 = 82.1 %** |
| samples/4p1i | 39 | 27 (69.2 %) | 10 (25.6 %) | 2 (5.1 %) | 10/12 = 83.3 % |
| ml/4p1i | 40 | 20 (50.0 %) | 20 (50.0 %) | 0 | 20/20 = 100 % |

By **meeting index** the crew gets *worse*, not better, as a game goes on (9p2i combined):
m0 64.0 % impostor-eject (128/200) → m1 45.0 % (90/200) → m2 56.5 % → m3 33.8 % → m4 31.8 %. Late meetings are the
ones with fewest living witnesses and the most carried-over noise.

By **trigger kind** the split is total:

| set | body meetings | skip | imp | inn | emergency meetings | skip | imp | inn |
|---|---|---|---|---|---|---|---|---|
| samples/9p2i | 151 | 42.4 % | 43.0 % | 14.6 % | 14 | **0 %** | 92.9 % | 7.1 % |
| ml/9p2i | 411 | 39.2 % | 48.2 % | 12.7 % | 52 | **0 %** | 96.2 % | 3.8 % |
| samples/4p1i | 35 | 77.1 % | 17.1 % | 5.7 % | 4 | **0 %** | 100 % | 0 |
| ml/4p1i | 29 | 69.0 % | 31.0 % | 0 | 11 | **0 %** | 100 % | 0 |

**[VERIFIED] Not one of the 81 emergency meetings skipped, and 78/81 ejected an impostor.**
The reason is mechanical, not deliberative: **81/81 emergency meetings carry a `vent_sighting`
flag, and 81/81 emergency openings carry a `saw_vent` observation.** The emergency button fires
only when the caller's private max suspicion crosses the 0.6 gate
(`agents/tactical/crewmate_policy.py:130-166`, `EmergencyButtonView.is_eligible`), and in practice
only a witnessed vent moves belief that far before a meeting. So the "emergency meeting" is the
**vent alarm**, and the discussion that follows is a formality.

---

## 2. The meeting does not decide — the flag detector does

**[VERIFIED] F1 — "did a contradiction flag fire" predicts the meeting outcome 88–100 % of the time.**

| set | accuracy of `flag ⇒ EJECT / no flag ⇒ SKIP` | SKIPPED meetings with zero flags | EJECTED meetings with zero flags |
|---|---|---|---|
| samples/9p2i | 146/165 = **88.5 %** | 55/64 (85.9 %) | 10/101 (9.9 %) |
| ml/9p2i | 418/463 = **90.3 %** | 142/161 (88.2 %) | 26/302 (8.6 %) |
| samples/4p1i | 38/39 = 97.4 % | 26/27 (96.3 %) | 0/12 |
| ml/4p1i | 40/40 = **100 %** | 20/20 | 0/20 |

`vent_sighting` alone accounts for **310/435 (71 %) of all ejections** and is perfectly precise:
**440/440 flagged subjects across all four sets were real impostors** (samples/9p2i 96,
ml/9p2i 313, samples/4p1i 11, ml/4p1i 20). Everything else the meeting produces is noise around
that one signal.

Flag → outcome cross-tab, per flagged subject (deduped per meeting):

| set | kind | severity | n | subject is impostor | subject ejected |
|---|---|---|---|---|---|
| samples/9p2i | vent_sighting | strong | 76 | **76/76 (100 %)** | 68/76 (89.5 %) |
| samples/9p2i | alibi_vs_sighting | strong | 47 | **4/47 (8.5 %)** | 22/47 (46.8 %) |
| samples/9p2i | alibi_vs_sighting | weak | 16 | 2/16 (12.5 %) | 4/16 (25.0 %) |
| samples/9p2i | alibi_conflict | weak | 8 | 0/8 (0 %) | 3/8 (37.5 %) |
| samples/9p2i | alibi_vs_physical | strong | 5 | 5/5 (100 %) | 4/5 (80 %) |
| ml/9p2i | vent_sighting | strong | 242 | **242/242 (100 %)** | 213/242 (88.0 %) |
| ml/9p2i | alibi_vs_sighting | strong | 142 | **28/142 (19.7 %)** | 68/142 (47.9 %) |
| ml/9p2i | alibi_vs_sighting | weak | 50 | 6/50 (12.0 %) | 18/50 (36.0 %) |
| ml/9p2i | alibi_vs_physical | strong | 25 | 25/25 (100 %) | 21/25 (84 %) |
| ml/9p2i | alibi_conflict | weak | 25 | 0/25 (0 %) | 5/25 (20 %) |

`alibi_vs_sighting` is the crew-killer: a strong-severity flag with **8.5 %–19.7 % precision**
that still ejects its subject ~47 % of the time, and the vote prompt introduces it as
*"Each flag below is VERIFIED evidence, not a verdict"*.

---

## 3. The innocent-ejection machine: the crew mis-states its own position

**[VERIFIED] F2 — ~1 in 5 crew roll-call answers is factually wrong, and that is what ejects innocents.**

Roll-call (`whereabouts`) self-placement vs truth, in agent-tick coordinates:

| set | crew whereabouts | true | **false** | impostor whereabouts | true | false |
|---|---|---|---|---|---|---|
| samples/9p2i | 723 | 575 (79.5 %) | **148 (20.5 %)** | 120 | 40 | 62 (51.7 %) |
| ml/9p2i | 2 038 | 1 622 (79.6 %) | **416 (20.4 %)** | 342 | 155 | 187 (54.7 %) |
| samples/4p1i | 78 | 71 (91.0 %) | 7 (9.0 %) | 8 | 3 | 5 (62.5 %) |
| ml/4p1i | 79 | 68 (86.1 %) | 11 (13.9 %) | 5 | 5 | 0 |

(The impostor's ~55 % false rate is *expected* — that's the deception. The crew's 20 % is a defect.)

Resolving every `alibi_vs_sighting` / `alibi_vs_physical` flag back to its two source statements
(`event_a_id` / `event_b_id` decode to `turn:{meeting}:turn-{k}:{claim|obs}:{i}`) and checking
**both** sides against the world:

| set | which side was actually false | n | subject ejected |
|---|---|---|---|
| samples/9p2i | the **accused's own self-placement** is false (CREW) | 23 | 11/23 (47.8 %) |
| samples/9p2i | the accused's own self-placement is false (IMPOSTOR) | 6 | 6/6 (100 %) |
| samples/9p2i | the **witness sighting** is false — innocent framed | 1 | 1/1 |
| ml/9p2i | the **accused's own self-placement** is false (CREW) | 81 | 40/81 (49.4 %) |
| ml/9p2i | the witness sighting is false — innocent framed (CREW) | 11 | 7/11 (63.6 %) |
| ml/9p2i | the accused's own self-placement is false (IMPOSTOR) | 11 | 9/11 (81.8 %) |
| ml/9p2i | BOTH statements false | 11 | 8/11 |

Root cause of every innocent ejection in the corpus (79 total):

| set | innocent ejections | victim mis-stated its OWN position → flag | flag from someone else's false sighting | no flag at all (pure rhetoric) |
|---|---|---|---|---|
| samples/9p2i | 23 | **16** | 4 | 3 |
| ml/9p2i | 54 | **40** | 13 | 1 |
| samples/4p1i | 2 | **2** | 0 | 0 |
| **total** | **79** | **58 (73.4 %)** | 17 (21.5 %) | 4 (5.1 %) |

And **74/79 (93.7 %) of innocent ejections carry an `alibi_vs_sighting` flag on the ejectee**
(the task's specific question) — flags built entirely from two *spoken, unverified* statements,
where in 3 of 4 cases the false statement was the victim's own.

**Exemplar — `samples/9p2i` seed 7, meeting-2 @tick 35, ejected p-6 (CREWMATE), 4–1.**
p-6 truly was in CAFETERIA at agent-tick 35. Raw lines:

```
[turn 1] p-6 (reply, reply_to turn-0)
    obs: {'type':'whereabouts','tick':35,'room':'EAST_HALL'}     <-- FALSE, p-6 was in CAFETERIA
    claims: {'type':'alibi','subject':'p-6','from_tick':35,'to_tick':35,'room':'EAST_HALL', ...}
    says: [invalid accusation target 'p-7' dropped] I was in EAST_HALL at tick 35, not near ADMIN. ...
[turn 2] p-8 (opt_in)
    claims: {'type':'corroboration','supports':'p-6','on_tick':35,'reason':'p-6 was with me in CAFETERIA, not ADMIN.'}
CONTRADICTIONS:
  - [alibi_vs_sighting/strong] subjects=('p-6',) :: Alibi places p-6 in EAST_HALL (ticks 35-35); sighting reports p-6 in CAFETERIA at tick 35.
  - [alibi_vs_sighting/strong] subjects=('p-6',) :: Alibi places p-6 in EAST_HALL (ticks 35-35); sighting reports p-6 in CAFETERIA at tick 35.   <-- same sentence twice
BALLOTS:
  p-8 -> p-6  conf=0.85  rationale: p-6 claimed EAST_HALL at tick 35. I saw him in CAFETERIA. Liar.
  p-2* -> p-6 conf=0.85  rationale: Oh god, p-6 claimed EAST_HALL but the flags say CAFETERIA, so he's lying ...
```
p-8 vouches for p-6 in turn 2 and votes him out in the same meeting for the vouch. The living
impostor **p-2 votes with the mob** and survives. The innocent was ejected for misremembering his
own room, nothing else.

---

## 4. Ballots: how the vote is actually made

| set | ballots | SKIP | eject | target is impostor | of ejects: cites a turn | cites own memory obs | cites NEITHER |
|---|---|---|---|---|---|---|---|
| samples/9p2i ALL | 971 | 451 (46.4 %) | 520 | 375/520 (72.1 %) | 476 (91.5 %) | 156 (30.0 %) | 0 |
| — crew | 726 | 266 (36.6 %) | 460 | 375/460 (81.5 %) | 417 (90.7 %) | 144 (31.3 %) | 0 |
| — impostor | 245 | **185 (75.5 %)** | 60 | 0/60 (0 %) | 59 (98.3 %) | 12 (20.0 %) | 0 |
| ml/9p2i ALL | 2 726 | 1 148 (42.1 %) | 1 578 | 1 187/1 578 (75.2 %) | 1 438 (91.1 %) | 494 (31.3 %) | 4 |
| — crew | 2 042 | 636 (31.1 %) | 1 406 | 1 187/1 406 (84.4 %) | 1 273 (90.5 %) | 443 (31.5 %) | 4 |
| — impostor | 684 | **512 (74.9 %)** | 172 | 0/172 (0 %) | 165 (95.9 %) | 51 (29.7 %) | 0 |
| samples/4p1i crew | 78 | 53 (67.9 %) | 25 | 23/25 (92 %) | 20 (80 %) | 12 (48 %) | 0 |
| ml/4p1i crew | 80 | 39 (48.8 %) | 41 | 41/41 (100 %) | 31 (75.6 %) | 21 (51.2 %) | 0 |

Clean: **zero self-votes, zero dead targets, zero uncited ejects** in samples (4 in ml/9p2i) — the
citation gate and target guards hold. **98.9–100 % of cited turns actually mention the ballot's
target.** Ballots reference public rhetoric (a turn) 3× more often than the voter's own memory row.

**Herding:** the ejected player equals the **opening accusation's target** in
72/101 (71.3 %) samples/9p2i, 194/302 (64.2 %) ml/9p2i, 11/12 samples/4p1i, 18/20 ml/4p1i, and
equals the **last** accusation made in 83.2 % / 74.8 %. Herding on the *reporter* is essentially
absent (3.0 % / 2.6 % / 0 % / 0 %) — the `reporter_exculpation` prompt block works. The opening
accusation is itself only 70–82 % accurate, so the ~30 % of openings that pick the wrong player
drag the meeting with them two-thirds of the time.

**Unanimity:** **0 of 435 ejection meetings were unanimous** — because the impostor always votes
SKIP. Among living **crew** only, 73.3 % / 73.5 % / 83.3 % / 100 % were unanimous. Mean share of
ballots on the ejectee is 0.73–0.74.

**[VERIFIED] F3 — the impostor SKIP bloc is a free blocking vote.** Impostors cast SKIP on
185/245 (75.5 %), 512/684 (74.9 %), 37/39 (94.9 %), 36/40 (90 %) of their ballots. Because SKIP is
a first-class plurality target (documented anti-cascade rule, `DESIGN.md` §4.6 line 451,
`meetings/voting.py::tally_ballots`), of the **78 SKIPPED meetings that had at least one eject
ballot**, 75 were skip-bloc and 3 were ties — and in **39 of them the sole non-SKIP leader was a real
impostor**. That is 39 impostor escapes bought by the impostors' own abstentions.

**[VERIFIED] F4 — the 0.6 confidence floor never binds.** Across all 707 meetings, **not one**
SKIPPED meeting with a plurality leader was skipped for being under threshold; every one was a
skip-bloc or a tie. The anti-cascade floor is decorative in practice; the SKIP bloc is doing all
the work.

**Confidence calibration is bimodal, not graded** (crew eject ballots):

| bucket | samples/9p2i n / correct | ml/9p2i n / correct |
|---|---|---|
| 0.60–0.70 | 23 / 82.6 % | 50 / 70.0 % |
| 0.70–0.80 | 31 / **61.3 %** | 130 / **66.2 %** |
| 0.80–0.90 | 160 / **58.1 %** | 515 / **69.5 %** |
| 0.90–0.96 | 215 / **99.1 %** | 629 / **99.5 %** |
| 0.96–1.00 | 30 / 100 % | 80 / 100 % |
| overall | mean conf 0.883 vs acc 0.815 (+0.068) | 0.880 vs 0.844 (+0.036) |

Confidence is **non-monotonic**: 0.65 beats 0.85. There are really two populations — "0.85 = I am
following the room" (58–70 % right) and "0.95 = a vent flag is on the table" (99 % right). The
model is not expressing a probability; it is expressing which of two scripts it is in.

**`considered_alternatives` hygiene** (share of all ballots):

| issue | samples/9p2i | ml/9p2i | 4p1i |
|---|---|---|---|
| impostor lists its own **teammate** as an alternative | 72 (7.4 %) | 226 (8.3 %) | n/a |
| alternative is a dead/ejected player | 63 (6.5 %) | 141 (5.2 %) | 0 |
| voter lists **itself** as an alternative | 20 (2.1 %) | 49 (1.8 %) | 0 |
| target also listed as an "alternative" | 13 (1.3 %) | 47 (1.7 %) | 1 |

The teammate row is the interesting one: it is the only place a 9p2i impostor's private roster
knowledge visibly leaks into a recorded field (the target guard coerces the *vote*, not the
alternatives list).

---

## 5. Hallucination audit — spoken statements vs the speaker's own memory vs truth

Every spoken observation was checked against (a) the speaker's own rendered memory block for that
meeting, extracted from its own `llm_calls[].prompt_text` `<memory>` section, and (b) omniscient
truth + the recorded per-tick visibility field.

`saw_player` (the workhorse claim):

| set | n | grounded in own memory | true but not in memory | from heard testimony | echo of this meeting | **room wrong (fabricated)** | speaker could not have seen it | co-present names false |
|---|---|---|---|---|---|---|---|---|
| samples/9p2i CREW | 1 301 | 86.6 % | 2.7 % | 1.2 % | 1.3 % | **8.2 %** | 12.2 % | 10.1 % |
| ml/9p2i CREW | 3 456 | 85.9 % | 2.9 % | 1.0 % | 2.2 % | **7.9 %** | 12.0 % | 8.9 % |
| samples/4p1i CREW | 123 | 93.5 % | 1.6 % | 0 | 0.8 % | 4.1 % | 5.7 % | 4.1 % |
| ml/4p1i CREW | 107 | 86.9 % | 2.8 % | 0 | 0 | 10.3 % | 11.2 % | 1.9 % |
| samples/9p2i IMPO | 244 | 89.3 % | 1.6 % | 0 | 3.7 % | 5.3 % | 7.8 % | 3.7 % |
| ml/9p2i IMPO | 720 | 90.4 % | 0.6 % | 0 | 3.5 % | 5.6 % | 8.1 % | 3.5 % |

Two things stand out. First, **the impostor fabricates placements LESS often than the crew**
(5.3–5.6 % vs 7.9–8.2 %) — the crew is noisier than the liar. Second, `alibi` claims: crew
fully-true 65.4 % / 67.4 % / 71.4 % / 78.3 %, crew **fully false** 2.8 % / 3.5 % / 0 % / 0 %,
impostor fully false 22.7 % / 27.3 % / 28.6 % / 0 %. `found_body` is essentially perfect
(962/963 true; the single wrong-room case is `ml/9p2i` seed 1078 m1 turn 4, p-6 IMPOSTOR placing
p-3's body in REACTOR when it was in ADMIN).

**[VERIFIED] F5 — crew can fabricate the game's strongest evidence type, and it renders as proof.**
`saw_vent` is grounded in the speaker's own memory 164/164 (samples/9p2i), 544/552 (ml/9p2i),
11/11, 20/20. The 8 ungrounded ones are the story:

*Exemplar A — `ml/9p2i` seed 1115, meeting-1 @tick 30.* p-8's only real vents are engine ticks
10–11 (agent ticks 11–12). Four crewmates each speak a first-hand vent sighting at **tick 30**:

```
turn 0 p-2: saw_vent {tick 30, subject p-8, room ENGINEERING}
   "Actually, before we start guessing, I have the smoking gun. I found p-1's body in Engineering,
    and I personally witnessed p-8 kill them right there. There is no other explanation..."
turn 2 p-3: saw_vent {tick 30, p-8, ENGINEERING}  "I corroborate p-2's account. I was in Engineering
    at tick 30 and saw p-8 vent right next to p-1's body."
turn 3 p-4: saw_vent {tick 30, p-8, ENGINEERING}  "You want me to take your word for it? I don't
    need to. I saw p-8 vent right next to the body myself."
turn 4 p-6: saw_vent {tick 30, p-8, ENGINEERING}  "I saw p-8 vent in Engineering at tick 30."
```
I pulled all four agents' rendered memories: **p-2, p-3 and p-4 have no vent line at all**; p-6's
only vent memory is `[obs p-6:12:1] [tick 12] You witnessed p-9 vent in STORAGE.` The claim is
100 % confabulated and 100 % contagious. And the transcript block handed to every later speaker
renders it exactly like a real one, with no "unverified" qualifier:

```
- tick 30: witnessed p-8 VENT in ENGINEERING (only the impostor can vent).
```
No `vent_sighting` flag was minted (the grounding gate correctly refused — the ballot prompts for
this meeting contain **no `<flagged_contradictions>` block at all**), yet all five crew ballots
landed on p-8 at confidence **1.00**. Right answer, entirely invented evidence.

*Exemplar B — `ml/9p2i` seed 1033.* p-7 (IMPOSTOR) **never vents in the whole game** (the only
vents are p-3's at engine ticks 11/12 and 18/19). p-6 (CREWMATE) nonetheless speaks
`saw_vent {tick 7, subject p-7, room MEDBAY}` at meeting-1 *and repeats it at meeting-2*, with
free_text *"I was in Medbay at tick 7 because I watched p-7 turn p-2 into a rug"* — a witnessed kill
that also never happened. p-7 was ejected 5–2 on that fabrication.

*Exemplar C — self-incrimination.* `ml/9p2i` seed 1023 m1 turn 2: p-6 (IMPOSTOR) speaks
`saw_vent {tick 22, subject 'p-6', room ENGINEERING}` — naming **itself** as the venter. p-6 did
vent STORAGE→ENGINEERING at engine tick 22. The impostor persona forbids exactly this
("a vent you used [is an] impostor-only fact, and naming one instantly exposes you").

*Exemplar D — laundering hearsay into first-hand testimony.* `samples/9p2i` seed 2, meeting-3
turn 3: p-9 speaks `saw_player {tick 21, subject p-7, room STORAGE}` and a corroboration
*"I was in ADMIN at tick 21, confirming p-7 was in STORAGE to vent."* p-9's rendered memory for
that meeting contains no tick-21 line and its visibility that tick is empty — p-9 saw nothing. The
placement happens to be true (p-7 was in STORAGE) because p-9 is repeating p-3's spoken vent
testimony as its own eyes, then voting p-7 at confidence 0.95.

Corpus-wide, **12.0–12.2 % of crew `saw_player` claims in 9p2i are placements the speaker's own
recorded field of view could not have contained**, plus 1.0–1.2 % lifted verbatim from
`[meeting] CLAIM by … (unverified)` memory lines and 1.3–2.2 % copied from an earlier speaker in
the same meeting.

---

## 6. Turn structure: a round-robin wearing a debate costume

**[VERIFIED] F6 — in 707/707 meetings, `#turns == #ballots == #living players`, and nobody ever
speaks twice.** The "opt-in info-share" gate (`DESIGN.md` §5.2 PHASE 3: "Eligible = living players
who have NOT yet spoken **AND hold a relevant observation**") never excludes anybody: living crew
participation 100 % (726/726, 2042/2042, 78/78, 80/80) and living impostor participation 100 %
(245/245, 684/684, 39/39, 40/40).

The "reactive accusation chain" is essentially always length 1:

| set | meetings by # of `reply` turns |
|---|---|
| samples/9p2i | 1 reply: 126, 2 replies: 39 |
| ml/9p2i | 0: 2, 1: **341**, 2: 116, 3: 4 |
| samples/4p1i | 1: 37, 2: 2 |
| ml/4p1i | 1: 33, 2: 7 |

**Accusations are almost never answered:** a direct `reply` from the accused follows only
204/778 (26.2 %) of accusations in samples/9p2i, 585/2 188 (26.7 %) in ml/9p2i, 41/107 (38.3 %) and
47/108 (43.5 %) in 4p1i. **553 / 1 542 accusations are never answered at all.** The structural
reason is by design: 424/778 (55 %) and 1 196/2 188 (55 %) of accusations are made in `opt_in`
turns, which *"may accuse but do NOT extend the chain"* (`DESIGN.md` §5.2 PHASE 3). So the shape of
every meeting is: one accusation → one rebuttal → a queue of unanswerable monologues → vote.

---

## 7. Two mechanical role tells

**[VERIFIED] F7 — the roll-call is a role classifier.**

| set | crew turns carrying a `whereabouts` | impostor turns carrying one | impostor turns with **zero** observations | P(impostor \| turn has no whereabouts) |
|---|---|---|---|---|
| samples/9p2i | 723/726 (99.6 %) | 120/245 (49.0 %) | 124/245 (50.6 %) | **125/128 = 97.7 %** |
| ml/9p2i | 2 035/2 042 (99.7 %) | 342/684 (50.0 %) | 342/684 (50.0 %) | **342/349 = 98.0 %** |
| samples/4p1i | 78/78 (100 %) | 8/39 (20.5 %) | 31/39 (79.5 %) | **31/31 = 100 %** |
| ml/4p1i | 79/80 (98.8 %) | 5/40 (12.5 %) | 35/40 (87.5 %) | **35/36 = 97.2 %** |

This is created by the impostor prompt itself: *"a bystander who was elsewhere has nothing to
explain, so explain nothing about your own whereabouts — every location, room, and timing detail
you mention must be about OTHER players."* Half of all impostor turns therefore arrive with an
**empty `observations` array**, which no crewmate turn ever does (0/2 926 crew turns in 9p2i). A
trivial rule — "eject whoever didn't answer the roll call" — would be right 98 % of the time.
(`replays/ml_corpus/README.md` records `impostor_roll_call` as the sole live toggle, recorded OFF,
so this asymmetry is a deliberate, currently-unmitigated configuration.)

**[VERIFIED] F8 — an impostor has never once reported a body or called a meeting.**
626/626 body reports and 707/707 meeting triggers across all 300 games come from a CREWMATE.
Consequently `impostor_report.*.v3` is compiled, versioned and pinned but **never invoked** —
0 calls out of the 7 932 meeting LLM calls in the corpus. The vote prompt tells voters *"self-report is weakly
exculpatory: the impostor almost never reports its own kill"*; the truth is stronger than the
prompt admits, and "who called this meeting" is a perfect innocence certificate.

---

## 8. Scaffold text leaking into the fiction

**[VERIFIED] F9 — dev audit markers are spliced into `free_text` and then quoted verbatim into
every later agent's prompt.** 53/971 (5.5 %) of samples/9p2i turns and 139/2 726 (5.1 %) of ml/9p2i
turns begin with a bracketed marker. `api/replay_loader.py` parses ballot markers into structured
`rewrite_reasons` chips, but **turn `free_text` markers are not parsed** (only the emergency
body-strip becomes `fabricated_opening`), so they survive to the spectator surface *and* to the LLM.
Proof, from the `<transcript>` block of p-9's accusation prompt in `samples/9p2i` seed 2 meeting-2:

```
- [headless-seed-2:meeting-2:turn-2] turn 2 (opt_in) — p-8: [invalid accusation target 'p-4' dropped]
  I... well, I suppose I should mention that I saw p-4 vent in ENGINEERING at tick 11 ...
```

Counts per set (turn `free_text` / ballot `rationale_text`):

| marker | samples/9p2i | ml/9p2i | ml/4p1i |
|---|---|---|---|
| `[invalid accusation target …]` | 53 / 0 | 137 / 0 | 0 |
| `[invalid corroboration supports …]` | 0 | 2 / 0 | 0 |
| `[under-gate eject target … redirected]` | 0 / 13 | 0 / 48 | 0 / 1 |
| `[invalid target … normalized to SKIP]` | 0 / 3 | 0 | 0 |
| `[teammate target … coerced to SKIP]` | 0 | 0 / 4 | 0 |
| `[invalid primary_reason_id … nulled]` | 0 / 2 | 0 / 1 | 0 |
| `[invalid primary_reason_observation_id … nulled]` | 0 | 0 / 2 | 0 |
| `[uncited zero-flag eject target … coerced to SKIP]` | 0 / 1 | 0 / 1 | 0 |

No "As an AI" boilerplate, no code-fence residue, no template placeholders anywhere (0/3 934) —
the JSON discipline is solid; the leak is entirely the repo's own audit markers.

**Why the marker fires so often is itself the bug.** The pattern is: a vent-witnessed impostor gets
ejected, and at the *next* meeting the witnesses keep naming them, because the opening prompt
instructs *"speak it FIRST, at this meeting, even if you already said it at an earlier meeting"*
while the memory never learns that the vent case is closed. **68 (samples/9p2i) and 232 (ml/9p2i)
`saw_vent` observations name a player who is already dead or ejected.** In `samples/9p2i` seed 0
meeting-1 three consecutive turns all open with `[invalid accusation target 'p-6' dropped]`.
Two of those wasted ballots even reached the tally as coerced SKIPs at confidence 0.95:

```
samples/9p2i seed 9 m1  p-2(CREW) -> SKIP conf=0.95
  raw: [invalid target 'p-4' normalized to SKIP] I-I mean, p-5 and p-8 both saw p-4 vent in LABS,
       which is, well, it's the smoking gun, isn't it, so I have to vote them out.
```

**[VERIFIED] F10 — the target-redirect guard makes ballots whose stated reason names a different
player than the recorded target.** `BALLOT_TARGET_REDIRECT_MARKER` (`meetings/manager.py:279`;
documented intent: *"innocents are ejectable, never at RANDOM"*) rewrites the target and keeps the
model's rationale:

```
samples/9p2i seed 8 m3  p-9(CREW) -> p-5   conf=0.75
  raw: [under-gate eject target 'p-4' redirected] p-4 claims REACTOR but I saw them in EAST_HALL
       at tick 34. The lie is undeniable. Vote them out.
```
More broadly, **84/2 170 eject ballots corpus-wide name players in their rationale but not the target**
(22/520 samples/9p2i, 58/1 578 ml/9p2i, 1/27, 3/45), and **259/1 764 SKIP ballots argue explicitly
for an ejection** (59/451, 192/1 148, 3/90, 5/75) ("…so I have
to vote them out", "the smoking gun"). One extra leak worth noting: a coerced impostor ballot can
carry private knowledge onto the surface —
`samples/9p2i` seed 8 m0, p-3 (IMPOSTOR): *"[under-gate eject target 'p-1' redirected] P-1 lies
about the vent. **I didn't vent.** Vote him."*

---

## 9. Free-text vs structured, and persona

| mismatch | samples/9p2i (n=971) | ml/9p2i (n=2 726) | samples/4p1i (117) | ml/4p1i (120) |
|---|---|---|---|---|
| free_text says "vent" with **no** `saw_vent` observation | 313 (32.2 %) | 925 (33.9 %) | 9 (7.7 %) | 24 (20 %) |
| accusation target never named in free_text | 105 (10.8 %) | 268 (9.8 %) | 17 (14.5 %) | 17 (14.2 %) |
| free_text accuses but carries no accusation claim | 61 (6.3 %) | 183 (6.7 %) | 1 | 2 |
| IMPOSTOR used a forbidden discovery word ("I found …") | 10 (1.0 %) | 48 (1.8 %) | 1 | 1 |

The "vent with no `saw_vent`" row is mostly *legitimate* (agents discussing someone else's vent
claim), but it is also the channel by which an unbacked vent rumour circulates: the structured
observation is gated, the sentence is not.

**Persona:** voices are distinguishable but the *ballot* register collapses. Repeated 4-word
rationale openings: `"how do you know"` 54 (5.6 %) / 133 (4.9 %), `"i saw p vent"` 26 / 98,
`"the evidence is too"` 25 / 75. Verbatim-duplicate rationales across independent games:
`"The evidence is too thin to justify an ejection."` **22×** in ml/9p2i, `"The smoke is too thick
to see the fire, so I'll hold my hand…"` **16×**. The vote prompt explicitly warns against one
stock formula (*"Half the table opens with the stock formula 'p-N's alibi contradicts multiple
sightings…' — don't"*); it succeeded in killing that one and grew four replacements.

**Prompt wording [VERIFIED]:** the persona line is hardcoded singular in all six
`agents/strategic/prompts/qwen3_6_27b/*.j2` templates (`crewmate_report.j2:58`,
`accusation_round.j2:79`, `vote_ballot.j2:74`, `impostor_report.j2:59`, and the two
`*_roll_call` variants), never conditioned on the impostor count — so every 9p2i prompt describes a **single** impostor —
`"a hidden impostor is killing crewmates one at a time"` (crewmate_report),
`"a hidden impostor kills crewmates"` (accusation_round, vote_ballot). Present in the first prompt
of **165/165 samples/9p2i meetings and 463/463 ml/9p2i meetings (100 %)**, while both those sets
have two impostors — and the same prompt then tells the impostor *"Your fellow saboteurs: p-4"*.
The crew is being told, in the persona line, that ejecting one player ends the game.

---

## 10. Prompt / memory as an input

Per-call sizes (input tokens):

| set | crewmate_report | accusation_round | vote_ballot | input tokens per meeting |
|---|---|---|---|---|
| samples/9p2i | n=179, mean 3 802, p95 4 619 | n=806, mean 4 092, p95 5 157 | n=971, mean 4 534, p95 5 451 | mean **50 799**, max 74 606 |
| ml/9p2i | n=513, mean 3 768 | n=2 263, mean 4 108 | n=2 726, mean 4 559 | comparable |

Outputs are small (mean 330 tokens for a turn, 110 for a ballot; free_text mean 217 chars).
About **18 %** of a 9p2i meeting's prompt bytes is the *same agent's own memory block re-sent* on
its later call (7.5 % in 4p1i) — every agent gets its full memory twice, once to speak and once to
vote.

Reading the memory renders as a spectator, the quality problems are:
1. **Volume over salience.** A typical 9p2i memory opens with 8 lines of tick-0 lobby co-presence
   (`You saw p-1 in CAFETERIA (with p-2, p-4, p-5, p-6, p-7, p-8, p-9)` ×8) — 15 347 such lines in a
   400-meeting sample, the single most common memory line shape by a wide margin. The opening prompt then has to
   fight it: *"Curate, don't dump."*
2. **Hearsay sits beside first-hand.** `[meeting] CLAIM by p-8 (unverified): saw p-4 in ENGINEERING
   @ tick 5` is one bullet away from `[obs p-8:5:1] You saw p-4 …`. That adjacency is exactly what
   produces the 1.0–1.2 % of `saw_player` claims lifted from hearsay and the seed-2 p-9 laundering
   above.
3. **The dead never leave.** Beliefs and observations about ejected players stay in the render
   (`- p-1: suspicion 0.50 … OUT OF THE GAME`), which is what keeps 232 `saw_vent` claims aimed at
   corpses alive.
4. **The self-position line is off by one relative to the sighting lines** (§0), so an agent that
   dutifully copies its own record into `whereabouts` can be wrong through no fault of its own.

---

## 11. Small stuff worth logging

- **`samples/4p1i`: 11/50 games hold no meeting at all** (9 CREWMATE_TASKS, 2 IMPOSTOR_PARITY);
  in 7 of them a kill happened and the body was never reported. `ml/4p1i`: 10/50, 4 with unreported
  kills. Two whole games end in an impostor parity win with the crew never once convening
  (seeds 25, 30).
- **Duplicate flags.** The same contradiction sentence is rendered up to **3× (samples/9p2i)** and
  **4× (ml/9p2i)** in one meeting's flag block (10 and 30 duplicate copies over 186 / 607 flags,
  7 and 23 meetings affected) — see seed 7 m2 above. Voters see doubled evidence weight for one
  fact.
- **Corroboration claims are inert as evidence** — 340 + 990 + 17 + 20 of them, none of which
  produce a flag; they only nudge belief. In seed 7 m2 a correct corroboration was outweighed by
  the flag built from the same sighting.
- **`alibi` claims about *other* players**: 1 (samples/9p2i) + 5 (ml/9p2i) turns vouch for someone
  else using the `alibi` shape whose schema docstring says the subject is the speaker.
- **Impostor teamwork is essentially absent**: across 750 impostor accusations in 9p2i, **zero**
  aimed at a teammate (the firewall holds), but teammate corroboration fires only 14 / 31 times —
  the two impostors mostly ignore each other.

---

## 12. Ranked findings

### BUGS (something is broken)

1. **B1 — Agent tick stamps are +1 vs the replay timeline (111 283/111 283).** Every spoken tick
   reference is one ahead of what the viewer's map shows; the memory's own self-position lines are
   one further back still (3 406/3 406 at Δ=−2). Cause at `orchestrator/game.py:1778` vs `:1786-93`.
   Fixing the stamp (or the recorded tick) makes every alibi argument in the corpus checkable by a
   human for the first time.
2. **B2 — Dev audit markers leak into the fiction and into other agents' prompts** (5.5 % / 5.1 % of
   turns; §8). `[invalid accusation target 'p-4' dropped]` is read by the LLM as something a player
   said. `api/replay_loader.py` already has the machinery (`_parse_rewrite_reasons`) for ballots —
   turn `free_text` needs the same parse, and the transcript renderer (`meetings/transcript.py`, which already owns the
   weak-contradiction marker) should strip markers before emitting the `<transcript>` block —
   [JUDGMENT] on the exact seam, [VERIFIED] that the marker reaches the prompt.
3. **B3 — Crew can speak a `saw_vent` that exists in neither their memory nor the engine, and it
   renders as proof** (8 cases in ml/9p2i; seed 1115 m1 has four speakers doing it at once, seed
   1033 sustains the same fabrication across two meetings). The flag detector correctly refuses to
   mint a flag, but nothing tells the reader — the transcript line is
   `witnessed p-8 VENT in ENGINEERING (only the impostor can vent)` either way.
4. **B4 — Duplicate contradiction flags** (up to 4 copies of one sentence per meeting) inflate the
   apparent weight of a single fact.
5. **B5 — `impostor_report.qwen3_6_27b.v3` is dead code in practice** — 0/3 934 calls, because an
   impostor has never reported a body (0/626). Either the FSM cannot emit REPORT for an impostor or
   the situation never arises; either way a pinned, version-bumped template is never exercised.

### DESIGN HOLES (working as specified; the specification hurts the game)

6. **D1 — The meeting is a flag detector, not a deliberation.** "Did a flag fire" predicts the
   outcome 88.5 % / 90.3 % / 97.4 % / 100 %. `vent_sighting` (100 % precise, 440/440) drives 71 % of
   ejections; emergency meetings (81/81 vent-triggered) eject 100 % of the time. Everything spoken
   between the opening and the vote moves almost nothing.
7. **D2 — `alibi_vs_sighting` is presented as "VERIFIED evidence" but is two unverified sentences
   disagreeing**, at 8.5 % / 19.7 % precision, and it ejects its subject ~47 % of the time.
   **74/79 innocent ejections carry one.** The evidence taxonomy already separates `role_proof` from
   `cross_statement` (`api/schemas.py::classify_evidence`); the *prompt* does not — the flag block
   header treats every kind the same.
8. **D3 — The crew's 20 % roll-call error rate is the innocent-ejection engine.** 58/79 innocent
   ejections (73.4 %) trace to the victim mis-stating its own position; only 17 to a false witness.
   The system converts the crew's own memory noise into "hard evidence" against itself.
9. **D4 — SKIP as a first-class plurality target hands the impostors a free blocking vote.**
   Impostors SKIP 75 % / 75 % / 95 % / 90 % of the time; 39 meetings whose sole leader was a real
   impostor were skipped on the SKIP bloc. Documented as an anti-cascade rule (`DESIGN.md` §4.6),
   but its cost lands on the crew. The paired confidence floor it was designed with **never fires
   once** in 707 meetings.
10. **D5 — The meeting is a fixed round-robin.** 707/707 meetings: `#turns == #ballots == #living`,
    nobody speaks twice, the chain is one reply long in 76 % of meetings, and 55 % of accusations
    are made in `opt_in` turns that by design cannot be answered — so **73 % of all accusations are
    never answered at all**. PHASE 2/PHASE 3 are producing no structural variety.
11. **D6 — Two mechanical role tells.** No whereabouts ⇒ impostor with 97.7–100 % accuracy; empty
    observations array ⇒ impostor (0/2 926 crew turns ever have one); reporting a body ⇒ crewmate
    with 100 % accuracy. The first is manufactured by the impostor persona's own instruction.
12. **D7 — 9p2i prompts say "a hidden impostor" (singular) in 628/628 meetings** while two
    impostors are in play, then privately name the teammate to the impostor. The crew is primed to
    believe one ejection ends the game.
13. **D8 — Ejected players never leave the agents' heads.** 300 `saw_vent` observations aimed at
    dead/ejected players; 190 turns whose accusation was dropped for naming a corpse; ballots
    normalized to SKIP at confidence 0.95 for the same reason.

### QUALITY OF REASONING

14. **Q1 — Confidence is bimodal, not calibrated.** The 0.80–0.90 bucket is *less* accurate
    (58.1 % / 69.5 %) than 0.60–0.70 (82.6 % / 70.0 %), while 0.90–0.96 is 99 %. Overall
    overconfidence +0.068 / +0.036. The number encodes "vent flag / no vent flag", not a belief.
15. **Q2 — Herding on the opening.** The ejected equals the opening accusation 71 % / 64 % /
    92 % / 90 % of the time, while the opening is only 70–82 % accurate. Ballots cite a public turn
    3× more often than the voter's own memory (91 % vs 30 %).
16. **Q3 — 12 % of crew sightings are things the speaker could not have seen**, 8 % put the subject
    in the wrong room, 9–10 % of co-present name lists are wrong; 1–2 % are hearsay or same-meeting
    echo re-spoken as first-hand. The impostor fabricates *less* than the crew.
17. **Q4 — Ballot voice collapse.** `"The evidence is too thin to justify an ejection."` appears
    verbatim 22× across independent ml/9p2i games; four stock openings cover ~15 % of all ballots.
18. **Q5 — Rationale/target divergence.** 84 eject ballots argue for a player they don't vote for,
    and 259 SKIP ballots argue for an ejection they don't cast — partly the redirect guard (F10),
    partly the model.

---

## 13. Ideas (cheapest first)

1. **Strip markers before rendering** (B2): parse turn `free_text` markers the way ballots already
   are; render a neutral chip on the spectator surface and nothing at all into the LLM transcript.
2. **Re-stamp agent ticks** or re-label the recorded tick (B1) so the viewer and the dialogue agree.
   One number, and every alibi argument becomes independently checkable.
3. **Fix the singular-impostor wording** in the 9p2i prompt set (D7) and de-duplicate the flag block
   (B4). Both are one-line changes with a re-record.
4. **Split the flag header by category** (D2). The taxonomy exists in code
   (`role_proof` / `cross_statement` / `weak_signal`); say it in the prompt — "one of these two
   accounts is wrong, and nothing here says which" for cross-statement flags versus "this is proof"
   for `vent_sighting`. Expect the innocent-ejection rate to move more than any rhetoric change.
5. **Render an ungrounded `saw_vent` differently** (B3): the transcript already knows whether the
   claim matched the speaker's own record (that's the flag-grounding gate) — surface the distinction
   in the line, e.g. `claims to have witnessed … (unverified)`.
6. **Make the roll-call symmetric** (D6). Turn on `impostor_roll_call` — or require every turn to
   carry exactly one `whereabouts`, truthful or not. A liar who *must* place themselves is what
   makes `alibi_vs_sighting` interesting; today the impostor simply declines to be checkable and
   only the crew produces falsifiable statements.
7. **Give the accused a second turn** (D5). Let one `opt_in` accusation re-open the chain, capped —
   currently 73 % of accusations die unanswered and the reply chain is length 1 in three quarters of
   meetings.
8. **Prune the memory render** (§10): drop the tick-0 lobby block, drop belief rows for players
   OUT OF THE GAME, and mark hearsay lines with a visual gutter distinct from first-hand rows. Also
   worth testing: don't re-send the memory in the ballot call (18 % of meeting prompt bytes) and
   instead send the turn the agent itself just spoke.
9. **Reconsider SKIP-as-plurality-bloc** (D4), or at least exclude non-voting abstentions from the
   denominator, given the confidence floor it was paired with never fires. As it stands, two
   impostors abstaining is worth more than two crewmates agreeing.
