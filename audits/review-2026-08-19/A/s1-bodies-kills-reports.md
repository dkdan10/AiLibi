# s1 — Body / Kill / Report lifecycle: corpus-wide mechanical sweep

**Scope**: all 300 committed replays — `replays/samples/9p2i` (seeds 0–49, n=50),
`replays/samples/4p1i` (0–49, n=50), `replays/ml_corpus/9p2i` (1000–1149, n=150),
`replays/ml_corpus/4p1i` (1000–1049, n=50). 7,718 tick frames, 798 kills, 626 body
reports, 707 meetings.

**Method**. `ReplayLoader(...).load_replay(gid)` for the reconstructed world
(`ticks[].bodies`, `ticks[].events`, `agent_states[].visibility`), plus the raw
JSONL `actions` array for *attempted* actions (the JSONL carries only
`actions` + `state_hash` per tick; every event is a re-simulation product).
Scripts: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/s1-bodies-kills-reports/{extract,analyze,analyze2,analyze3,analyze4,dig}.py`.

**Sanity check** (required before trusting numbers): the extractor's frame dump for
`samples/9p2i` seed 2 and `samples/4p1i` seed 0 was diffed by hand against
`watch.py` output — rooms, actions, task progress, bodies, events, meeting ticks and
meeting outcomes match line for line (`work/s1-bodies-kills-reports/seed2.txt` vs
`sanity.py`). Raw-action attribution was cross-checked on seed 2 t7/t14 where
`p-4` issues `kill` on a meeting tick and it produces no event.

---

## 1. The engine's body bookkeeping is clean — this is the good news

Every integrity check on 798 bodies over 7,718 frames came back **zero**:

| check | violations |
|---|---|
| body changes room after it is created | 0 / 798 |
| body present with no matching `kill` event | 0 / 798 |
| body vanishes for a tick and returns | 0 / 798 |
| body reported twice | 0 / 626 reports |
| `report_body` for a body not on the floor that tick | 0 / 626 |
| `report_body` issued from a room other than the body's room | 0 / 626 |
| dead player with a non-null `room_id` | 0 / 7,718 frames |
| an **ejected** player's body appears on the floor | 0 |
| kill action rejected for an unexplained reason | 0 / 986 |
| report action rejected for an unexplained reason | 0 / 716 |

[VERIFIED] There is no glitch class in the body/report *plumbing*. Every rejected
action is fully explained by a documented rule (§6, §7 below). Everything that follows
is a design hole or a quality-of-behaviour issue, not a bug — with one arguable
exception (§10).

---

## 2. Denominators per set

| metric | samples/9p2i | samples/4p1i | ml/9p2i | ml/4p1i | TOTAL |
|---|---|---|---|---|---|
| games | 50 | 50 | 150 | 50 | 300 |
| tick frames | 1,769 | 682 | 4,638 | 629 | 7,718 |
| median game length (ticks) | 34 | 12 | 27 | 11 | — |
| kill **events** | 177 | 61 | 505 | 55 | 798 |
| kill **actions attempted** | 225 | 64 | 640 | 57 | 986 |
| kill actions that produced nothing | 48 (21%) | 3 (5%) | 135 (21%) | 2 (4%) | 188 (19%) |
| `report_body` events | 151 | 35 | 411 | 29 | 626 |
| report actions attempted | 171 | 35 | 479 | 31 | 716 |
| report actions that produced nothing | 20 | 0 | 68 | 2 | 90 (13%) |
| meetings | 165 | 39 | 463 | 40 | 707 |
| — of which `body` trigger | 151 | 35 | 411 | 29 | 626 |
| — of which `emergency` trigger | 14 | 4 | 52 | 11 | 81 |
| emergency-button presses attempted | 19 | 5 | 75 | 13 | 112 |
| bodies never reported by game end | 26 (15%) | 26 (43%) | 94 (19%) | 26 (47%) | 172 (22%) |
| bodies that survive ≥1 meeting | 45 | 4 | 170 | 11 | 230 (29%) |

---

## 3. Kill → report latency

[VERIFIED] n = 626 reported bodies.

| set | n | min | p25 | median | p75 | p90 | max | mean |
|---|---|---|---|---|---|---|---|---|
| samples/9p2i | 151 | 1 | 3 | 4 | 6 | 12 | 29 | 5.25 |
| samples/4p1i | 35 | 1 | 3 | 4 | 6 | 8 | 12 | 4.77 |
| ml/9p2i | 411 | 1 | 3 | 4 | 6 | 11 | 30 | 5.29 |
| ml/4p1i | 29 | 1 | 2 | 4 | 6 | 6 | 7 | 3.83 |
| **ALL** | **626** | 1 | 3 | **4** | 6 | 11 | **30** | **5.18** |

Full histogram (ticks): 1→55, 2→78, 3→139, 4→135, 5→32, 6→52, 7→22, 8→20, 9→10,
10→13, 11→19, 12→14, 13→5, 14→1, 15→2, 16→3, 17→4, 18→5, 19→5, 20→4, 21→2,
23→1, 24→1, 27→1, 29→2, 30→1.

**Latency by kill room** [VERIFIED]:

| room | kills | never reported | never% | median latency |
|---|---|---|---|---|
| STORAGE | 154 | 40 | 26% | 6 |
| CAFETERIA | 145 | 20 | 14% | 4 |
| REACTOR | 140 | 50 | **36%** | 4 |
| ADMIN | 102 | 27 | 26% | 3 |
| ENGINEERING | 98 | 4 | **4%** | 3 |
| MEDBAY | 81 | 16 | 20% | 3 |
| EAST_HALL | 40 | 3 | 8% | 2 |
| LABS | 31 | 11 | 35% | 5 |
| WEST_HALL | 7 | 1 | 14% | 3 |

[JUDGMENT] The map is doing exactly what `engine/maps/canonical_1.yaml` says it should
("Reactor … Long task here invites kills"; "Storage is doubly isolated … canonical
'kill happened here' room"). REACTOR/LABS/STORAGE swallow a third of the corpses.
That is the design working — but see §5: the crew never goes looking, so the
"crime scene" rooms are one-way sinks rather than places a search finds.

---

## 4. Bodies that persist THROUGH a meeting

[VERIFIED] Only the **reported** body is consumed by a meeting. Every other corpse on
the floor survives untouched, with `discovered_by=None`, and stays invisible to the
crew (`engine/visibility.py:88-95` filters `discovered_by is None`; the consumption
is `orchestrator/game.py:1256-1259` `del bodies[triggering_body_id]`, whose comment
gives the rationale — stop an adversarial intent re-triggering meetings with the same
`body_id`).

- 230 / 798 bodies (28.8%) survive at least one meeting.
- 318 total body×meeting survivals.
- Distribution: 1 meeting → 161 bodies, 2 → 52, 3 → 15, **4 → 2**.
- 22 of these were a corpse lying in **CAFETERIA — the meeting room itself** — while a
  meeting was convened.

**Exemplar A — `samples/9p2i` seed 2, body-p-6-8 survives meeting-1** (from `watch.py`):

```
[t 14] ... p-3@CAFETERIA:REPORT ... | dead: p-1,p-2,p-6
       bodies: body-p-1-10 in CAFETERIA (victim p-1, killer p-7); body-p-6-8 in STORAGE (victim p-6, killer p-4)
       EVENT report_body: {'reporter_id': 'p-3', 'body_of': 'p-1', 'room_id': 'CAFETERIA'}
[t 15] ... | dead: p-1,p-2,p-4,p-6
       bodies: body-p-6-8 in STORAGE (victim p-6, killer p-4)
```
p-6 was murdered at t8. The whole crew convened at t14, ejected p-4, dispersed —
and p-6's corpse was still in Storage, unmentioned, until p-3 stumbled on it at t19.

**Exemplar B — `samples/9p2i` seed 8, an unreported corpse on the meeting-room floor**:

```
t  4 | ... p-5*@CAFETERIA:KILL ...   BODIES body-p-8-4@CAFETERIA
t  8 | p-1@ADMIN:REPORT ...          BODIES body-p-6-6@ADMIN, body-p-8-4@CAFETERIA
      EV report_body reporter_id=p-1 body_of=p-6 room_id=ADMIN
      >>> MEETING headless-seed-8:meeting-0 ... outcome EJECTED p-3
```
p-8 was killed in the Cafeteria at t4. The t8 meeting is held (nominally) in the
Cafeteria with p-8's body on the floor. I read the full transcript: **seven turns,
seven ballots, and not one syllable about p-8.** The only body discussed is p-6's, in
Admin. p-8 simply stops existing.

[JUDGMENT] This is the single biggest believability hole in the lifecycle. In the
genre, a meeting is where the survivors take stock of who is missing. Here the
meeting is strictly about *one* corpse; every other death is silently absorbed by the
roster shrinking. A player watching the replay sees the crew step over a body to argue
about a different body.

---

## 5. Bodies never found at all

[VERIFIED] 172 / 798 bodies (21.6%) are never reported.

- Of those, **168 / 172 (98%) are in a room no living crewmate ever enters again**
  after the kill. Only 4 had a crewmate walk back through.
- Split by set: samples/9p2i 26/177 (median 5.5 ticks of game left after the kill,
  max 41); samples/4p1i 26/61 (median 1 tick left — these are the parity/task
  end-of-game kills, not a discovery failure); ml/9p2i 94/505 (median 6 ticks left,
  max 45, 58 of them with ≥5 ticks left); ml/4p1i 26/55 (median 3.5 left).
- 82 of the 172 had at least one meeting occur while they lay there.

Longest-lying corpses [VERIFIED]:
```
ml/9p2i#1067   p-1 killed t14 in STORAGE — 45 ticks to game end, never found
samples/9p2i#23 p-1 killed t15 in STORAGE — 41 ticks, never found
ml/9p2i#1122   p-3 killed t5  in REACTOR — 33 ticks, never found  (survived 3 meetings)
samples/9p2i#4  p-4 killed t5  in REACTOR — 29 ticks, never found  (survived 4 meetings)
```

**Why nobody looks** [VERIFIED]: crewmates spend **4,745 of 34,206 living-crew
agent-ticks (13.9%) standing `IDLE` with `task_progress == 1.00`.** A crewmate who
finishes their tasks parks — usually in the Cafeteria — and never patrols.
`samples/9p2i` seed 16 t19–t25 shows three of them (`p-4`, `p-5`, `p-6`) frozen in
`CAFETERIA:IDLE[1.00]` for seven straight ticks while `p-7`'s corpse cools in Labs:
```
t 22 | p-1*@MEDBAY:VENT p-2@MEDBAY:TASK[0.58] p-4@CAFETERIA:IDLE[1.00] p-5@CAFETERIA:IDLE[1.00] p-6@CAFETERIA:IDLE[1.00] p-8@MEDBAY:TASK[0.70] p-9*@MEDBAY:VENT
      BODIES body-p-7-20@LABS
      ACT [... ('p-4','wait',{}), ('p-5','wait',{}), ('p-6','wait',{}) ...]
```
[JUDGMENT] "Task-complete crew emit `wait` forever" is the proximate cause of the 22%
never-found rate, and it is *also* what makes the dead-end kill rooms unbeatable. A
"patrol / escort / sweep" idle behaviour would convert a large share of the 172 lost
corpses into meetings — i.e. into deduction opportunities — at zero LLM cost.

---

## 6. Who reports, and how fast

[VERIFIED, and this is a striking number] **The reporter is a CREWMATE in 626 / 626
reports. An impostor has never once reported a body in the entire 300-game corpus.**
Zero self-reports by the killer, zero "I found it" cover plays by the other impostor.

[VERIFIED] Crew reporting is a hard reflex, not a decision:
- Report tick minus the first tick the reporter could see the corpse: **+1 in 614/626
  cases, +2 in 12/626.** Never 0, never ≥3.
- Refined lingering (agent has a body in `visible_bodies` for ≥2 consecutive ticks and
  never even *attempts* a `report` or `emergency` action): **CREW 0, IMPOSTOR 1,074.**
  ≥4 consecutive ticks: CREW 0, IMPOSTOR 201. ≥8 ticks: IMPOSTOR 2.
- Longest impostor stare-downs: `samples/9p2i#17` p-2 sits with `body-p-7-10` for
  t12–t23 (12 ticks); `samples/9p2i#47` p-9 with `body-p-5-18` t18–t29 (12 ticks).

The 90 rejected report actions are entirely **two crewmates reporting the same corpse
on the same tick** (87) plus 3 on a meeting tick. Example, `samples/9p2i` seed 8 t8:
```
ACT [('p-1','report',{'body_id':'body-p-6-6'}), ..., ('p-7','report',{'body_id':'body-p-6-6'}), ...]
EV  report_body reporter_id=p-1   # p-7's identical report is dropped
```

[JUDGMENT] Two design consequences worth naming:
1. **Reporting carries no strategic weight.** A crewmate cannot choose to keep quiet
   and set a trap; the +1-tick reflex means "who reported" is pure geography. The
   meeting's "reporter exculpation" substrate flag therefore rewards nothing but luck.
2. **The impostor never gets to use the strongest bluff in the genre** — self-report.
   With adjacency vision (§7) an impostor can see a teammate's kill from the next room
   and would be perfectly placed to "discover" it. The behaviour simply isn't in the
   policy. This is a missing impostor lever, not a bug.

---

## 7. Witnesses: crewmates are structurally blind to murder

[VERIFIED] This is the finding with the widest blast radius. At base visibility,
**impostors see their room + every adjacent room; crewmates see their own room only.**
Across the corpus, `visible_players` entries pointing at another room:

| observer role | same-room sightings | cross-room sightings |
|---|---|---|
| IMPOSTOR (samples/9p2i) | 2,979 | **3,418** |
| CREWMATE (samples/9p2i) | 11,617 | **3** |
| IMPOSTOR (ml/4p1i) | 471 | 279 |
| CREWMATE (ml/4p1i) | 1,145 | 1 |

The four crewmate cross-room rows are all `action='vent'` — the separate vent-witness
channel, e.g. `samples/9p2i#14 t20 p-6@EAST_HALL sees p-1@ENGINEERING vent`. Bodies
are the same: impostors registered 413 cross-room `visible_bodies` in samples/9p2i;
crewmates registered **0**, ever.

This is deliberate — `engine/visibility.py:98-126`
(`_resolve_observer_visibility_mode`, Task 13.8): *"a CREWMATE is downgraded to
`same_room_only` while an IMPOSTOR keeps the base `same_room_and_adjacent`… the crew
must INFER kills from testimony rather than witness them."* Note it contradicts the
map file, which declares `visibility_defaults: base: same_room_and_adjacent` with the
comment *"visibility is uniform across the map"* (`canonical_1.yaml:52-58`) — the
asymmetry is applied in code on top of the map, so the map's own documentation is now
misleading.

What it costs, measured on kills [VERIFIED]:

| at the kill tick | count / 798 kills |
|---|---|
| some other living agent was in the kill room | 133 |
| a **crewmate** was in the kill room | 59 (7.4%) |
| a **crewmate stood in a room adjacent to the murder** | **327 (41%)** |
| …of those, crewmates who perceived **nothing** (no killer, no body) | **327 / 327 (100%)** |
| someone could see the killer standing in the kill room | 231 |
| …only a fellow impostor could | 172 |
| …a crewmate could | 59 |

[JUDGMENT] 41% of all murders happen one doorway away from a crewmate who is
mechanically incapable of noticing, while the killer's partner watches comfortably
from the next room. As a *balance* lever this is coherent and clearly intentional.
As *spectacle* it is corrosive: the omniscient replay repeatedly shows a crewmate
standing in East Hall while a body drops in the Cafeteria next door, and the crewmate
walks on. It also means the map's own topology rationale ("Cafeteria … kills adjacent
to Cafeteria are easily witnessed", `canonical_1.yaml:73-77`) is now false for the crew
— the hub design and the visibility rule are pulling in opposite directions.

A cheaper middle ground [JUDGMENT/idea]: give crewmates adjacent-room **body**
visibility only (not player visibility). That keeps kills unwitnessed — the stated
forcing function — while cutting the "walked past the corpse" absurdity and the 22%
never-found rate, and it does not hand the crew any live-sighting evidence.

---

## 8. Kill misses: an invisible per-seat handicap

[VERIFIED] 188 of 986 kill actions (19%) produce no kill. Complete classification, no
residue:
- **32** issued on a meeting tick (the world is frozen; e.g. `samples/9p2i#2 t7`
  `('p-4','kill',{'target':'p-6'})` → nothing, re-issued and lands at t8).
- **156** the target was in another room at resolution time. In **156/156** the target
  was co-located with the killer the *previous* tick — the victim walked out during
  the same tick.
- **0** cooldown rejections, **0** friendly-fire rejections, **0** unexplained.

DESIGN.md §3.4 documents this: *"queued actions resolve in ascending actor-id order,
so a lower-id target's same-tick move legitimately escapes a kill. This is the
documented rule, not a race (2026-06-07 audit decision); revisit only if a future wave
gates on per-seat fairness."* The corpus lets me quantify the deferred fairness
question exactly:

[VERIFIED] **156/156 escapes had a target whose id sorts BELOW the killer's. Zero
escapes with a higher-id target (0 of 355 such attempts).** Escape rate by seat:

| target | kill attempts | escaped | escape % |
|---|---|---|---|
| p-1 | 185 | 46 | **25%** |
| p-2 | 184 | 35 | 19% |
| p-3 | 150 | 24 | 16% |
| p-4 | 121 | 23 | 19% |
| p-5 | 101 | 20 | 20% |
| p-6 | 72 | 3 | 4% |
| p-7 | 63 | 4 | 6% |
| p-8 | 56 | 1 | 2% |
| p-9 | 11 | 0 | **0%** |

Being `p-1` is worth a 25% dodge chance; being `p-9` is worth 0%, by construction.
Killers are near-uniform across seats (65–129 kills each), so this is a pure seat
lottery, not a behavioural artefact.

[JUDGMENT] Two problems, one mechanical and one dramatic.
(a) *Mechanical*: this is a silent, monotone survival bonus by seat index. Any ML /
eval work that aggregates per-seat outcomes inherits it. The fix is a coin flip on
simultaneity (or resolving kills before moves) rather than a lexicographic tiebreak;
the audit note explicitly reserves this.
(b) *Dramatic*: **a near-miss produces no event, no observation, and no memory for
anybody.** 156 times in this corpus a crewmate walked out of a room a half-second
before a knife landed, and nobody — not the escapee, not the spectator, not the
meeting — ever knows. That is 156 discarded set-pieces.

---

## 9. Kills in the meeting room, and kills on the meeting tick

[VERIFIED] **145 / 798 kills (18%) happen in CAFETERIA**, the spawn/meeting/emergency-
button room. 20 of those corpses are never reported.

[VERIFIED] **11 kills land on the exact tick a meeting is triggered.** The world tick
resolves fully (moves, tasks, kills) and *then* the meeting opens, so the victim dies
and is excluded from the meeting they were about to attend.

The worst of them — `ml/9p2i` seed 1120, t12 — a murder in the meeting room on the
meeting tick:
```
t 12 | p-1@WEST_HALL:MOVING p-4@REACTOR:TASK p-5*@CAFETERIA:KILL p-6*@CAFETERIA:IDLE p-7@WEST_HALL:MOVING p-8@MEDBAY:REPORT p-9@ADMIN:MOVING
      BODIES body-p-2-7@MEDBAY, body-p-3-12@CAFETERIA
      EV kill        killer_id=p-5 victim_id=p-3 room_id=CAFETERIA
      EV task_completed agent_id=p-3 task_id=fix_wiring_cafeteria room_id=CAFETERIA
      EV report_body  reporter_id=p-8 body_of=p-2 room_id=MEDBAY
      >>> MEETING headless-seed-1120:meeting-0 trigger=body by=p-8 outcome=SKIPPED
t 13 | ...  BODIES body-p-3-12@CAFETERIA
```
p-3 finishes a task and is murdered in the same instant p-8 calls the meeting from
MedBay; the meeting convenes (7 turns, 7 ballots) with p-3's fresh corpse in the room,
skips, and everyone walks out past it. p-3's body then lies unreported.

Also `samples/9p2i#41 t11` — p-1 kills p-5 in Admin, p-2 reports p-4's body in Reactor,
and p-7 presses the emergency button, all on the same tick:
```
ACT [('p-1','kill',{'target':'p-5'}), ('p-2','report',{'body_id':'body-p-4-5'}), ...,
     ('p-7','emergency',{'reason':'suspicion_accumulation'}), ...]
EV kill p-1→p-5 ADMIN ; EV report_body p-2 body_of=p-4 ; MEETING meeting-0 ejected=p-1
```

Additionally: 82 kills happen the tick *before* a meeting and 31 the tick *after*.

[JUDGMENT] Design choice (the tick resolves then the meeting opens) with a bad
side effect: a player can be killed in the room the meeting is held in, on the meeting
tick, and their death is neither reported nor narrated — the roster just shrinks by one
more than the transcript accounts for.

---

## 10. Time of death never reaches the meeting

[VERIFIED] 963 `found_body` observations appear in meeting transcripts across the
corpus. Their `tick` field minus the **true kill tick**:

```
diff: 1→171  2→134  3→165  4→181  5→48  6→75  7→36  8→32  9→17  10→23  11→23
      12→18  13→5  14→1  15→4  16→4  17→4  18→5  19→5  20→4  21→2  23→1  24→1  27→1  29→2  30→1
min = 1, zero-count = 0, median = 4, mean = 4.62, max = 30
```
**Not one observation in 963 carries the tick the victim actually died.** 830 carry the
*report* tick; the remaining 133 carry the tick the speaker first *saw* the corpse
(always kill+1, and almost always an impostor).

The knock-on is visible in the free text. `samples/9p2i` seed 2, meeting-0 opening
(kill at t4, report at t7):
> "I found poor p-2 cold as a cucumber in the Cafeteria **just a tick ago**."

— wrong by three ticks, and the whole subsequent alibi argument is anchored on t7
rather than t4. Everyone then supplies whereabouts for t5–t7, which is exactly the
window in which the killer, p-7, had already walked away.

[JUDGMENT] This is the highest-leverage cheap fix in the whole lifecycle. In the genre,
"the body was cold / the body was fresh" is the primary deduction handle. Here it is
structurally unavailable: `found_body` is a *discovery* record with no `died_at` field,
so the crew's alibi cross-check window is systematically off by a median of 4 ticks —
i.e. it interrogates the wrong slice of the timeline. Adding a coarse
`freshness: fresh | cold` (or a `died_at_tick` band) to the `found_body` observation
would make the median-4 gap actionable instead of invisible. Borderline **bug**: the
meeting machinery is being fed a timestamp that means something other than what every
downstream prompt reads it as.

---

## 11. The impostor's `found_body` leak that nobody hears

[VERIFIED] Impostors *do* emit `found_body` observations for corpses the crew has
never been told about: **27** spoken before the body's eventual report and **4** for a
body never reported at all (crew equivalents: 11 and 0 — those 11 are same-tick races).

`samples/9p2i` seed 32, meeting-0 @t10, turn 3, `p-6` (IMPOSTOR):
```
obs: {'whereabouts', t8, ENGINEERING}; {'found_body', tick 6, body_of p-2, room REACTOR}; ...
says: "Let's take a breath and look at the geometry here; p-1 claims to be in West Hall
       starting a reactor while simultaneously watching a vent in Admin…"
```
p-2's body is not reported until **t25**. p-6 has just placed itself at an
undisclosed murder scene at t6, in the record, in front of everyone — and the free
text never mentions it, no contradiction is raised, and no ballot cites it. The crew
ejects the honest witness p-1 instead.

`samples/9p2i` seed 16, meeting-1 @t25, turn 3, `p-9` (IMPOSTOR) does the same for
`p-7` in LABS at t21 — a corpse **never reported for the rest of the game**.

[JUDGMENT] A structured self-incrimination is being emitted and then discarded. Either
an impostor should not be able to attach a `found_body` for an undisclosed corpse (it
is a tell no human would give), or — much better — the meeting should treat
"you claim to have found a body nobody has reported" as a first-class contradiction.
It is free, hard, mechanical evidence of exactly the kind the crew is starved of.

---

## 12. The emergency button

[VERIFIED] 112 presses → 81 meetings. All 31 rejections are two agents pressing on the
same tick (deduped), not a rule violation.
- **Every single press carries `reason: 'suspicion_accumulation'`** — 112/112. There
  is no second reason in the corpus.
- **0 / 112 presses were made by an agent with a body in view.** The button is never a
  "found something but can't report" move.
- Tick histogram: `{10:53, 11:18, 12:3, 13:2, 15:8, 16:2, 19:2, 20:5, 21:1, 22:2,
  23:2, 24:1, 25:3, 26:3, 27:1, 28:2, 33:2, 34:1, 41:1}` — **71 of 112 presses fire at
  t10–t11.**

[JUDGMENT] The button is a timer, not a decision. It fires on a threshold at t10, with
one canned reason, and the resulting meeting has no triggering fact behind it. That
shows up in the transcripts as an opening turn that has to invent a topic (seed 32
above: p-1 opens an emergency meeting by re-litigating a vent sighting from t8). Genre-
wise the emergency button should be the crew's *"X hasn't been seen since t6"* move —
which is precisely the information the game currently throws away (§4, §10).

---

## 13. Meeting-tick world coherence

[VERIFIED]
- Agents **do** act on the meeting tick: 306 / 707 meeting ticks have at least one
  agent change room, 153 have task progress advance, and 53 complete a task. The tick
  resolves fully and the meeting opens at the end of it. Coherent, if you know the
  ordering; slightly odd to watch (seed 2 t7 shows three agents holding
  `current_action=MOVING` while nobody moves — a stale action label).
- **Nobody gathers.** Across all meetings, only 974 of 3,934 living attendees (24.8%)
  are physically in CAFETERIA at the meeting tick, and after the meeting 1,609 / 2,826
  are in the same room they were in before, 1,217 continue their normal move, and only
  149 walk into the Cafeteria. There is no teleport-to-meeting and no post-meeting
  reset.
- Dead players: `room_id` is `null` in every frame (0 violations). Ejected players
  never leave a body (0 violations).

[JUDGMENT] "No gather, no reset" is a defensible abstraction but it has a concrete
gameplay consequence: positional information survives the meeting intact, so an
impostor who was cornered in Reactor before a meeting is still in Reactor after it,
and a crewmate two rooms from a corpse is still two rooms away. In the genre the
post-meeting scatter from a common point is what re-randomises the board. Here nothing
re-randomises, which compounds §5 (the same crew keep walking the same loops and the
same rooms stay unvisited).

---

## 14. Ranked findings

**Severity ladder: bug > design hole > quality.**

1. **[design hole / borderline bug] `found_body` never carries time of death**
   (§10). 963/963 observations off by median 4 ticks, min 1, max 30, zero exact.
   Every alibi window the crew argues about is anchored on the wrong tick. Highest
   leverage, smallest change.
2. **[design hole] Only the reported corpse is consumed; every other body is invisible
   and unmentioned** (§4). 230/798 bodies survive a meeting, 22 of them lying in the
   meeting room. Deaths enter the fiction only as a shrinking roster.
3. **[design hole] 22% of corpses are never found, 98% of them in a room no crewmate
   re-enters** (§5), driven by 13.9% of crew agent-ticks spent `IDLE` at
   `task_progress==1.0` (§5, `seed 16 t19–25`). No patrol behaviour exists.
4. **[design hole, deliberate] Crewmates are blind one room away; impostors are not**
   (§7). 327/327 crewmates adjacent to a murder perceive nothing. Documented at
   `engine/visibility.py:98-126` (Task 13.8) but contradicted by
   `canonical_1.yaml:52-58` and by the map's own hub rationale.
5. **[design hole] Per-seat kill-escape lottery** (§8). 156/156 escapes go to a
   lower-id target; p-1 dodges 25% of attempts, p-9 dodges 0%. Documented as
   "not a race" in DESIGN.md §3.4 with the fairness question explicitly deferred —
   this is the measurement that closes it.
6. **[design hole] Impostors never report a body — 0 / 626** (§6). The genre's single
   best impostor bluff is absent from the policy, while the adjacency vision makes them
   ideally placed to use it.
7. **[quality] Impostor `found_body` self-incrimination is emitted and ignored** (§11).
   31 instances of an impostor announcing an undisclosed corpse; no contradiction, no
   ballot cites it.
8. **[quality] Crew reporting is a reflex, not a choice** (§6): +1 tick in 614/626,
   0 crew lingers ever. "Who reported" carries zero information.
9. **[quality] The emergency button is a t10 timer with one canned reason** (§12):
   112/112 `suspicion_accumulation`, 71/112 at t10–11, 0 with a body in view.
10. **[quality] Kills land on the meeting tick and in the meeting room** (§9): 11 on
    the tick, 145 in CAFETERIA. Deaths that the meeting cannot see or name.
11. **[quality] The 156 near-misses are silent** (§8b): no event, no memory, no line.
12. **[clean]** Body plumbing, report validation, dead-player state, ejected-player
    handling: **zero** anomalies in 798 bodies / 626 reports / 7,718 frames (§1).

### Ideas, cheapest first

- Add `died_at_tick` (or `fresh|cold`) to `FoundBodyObservation`; re-point the
  meeting's alibi window at it. Fixes #1 and gives #2/#9 something to chew on.
- Make "claims to have found a corpse nobody has reported" a contradiction kind.
  Fixes #7; turns an impostor tell into crew evidence for free.
- Render the *other* corpses at a meeting as a known fact ("p-8 has not been seen
  since t4") — even without their location. Fixes the "roster silently shrinks"
  half of #2 and gives the emergency button (#9) a real trigger.
- Give idle, task-complete crew a patrol/sweep behaviour instead of `wait`. Directly
  attacks #3 and adds bodies-found → meetings → deduction opportunities at zero LLM
  cost.
- Extend crewmate visibility to **adjacent-room bodies only** (not players). Keeps the
  Task-13.8 forcing function intact while removing the "walked past the corpse"
  absurdity of #4.
- Randomise same-tick action order (or resolve kills before moves) to close #5; and
  emit a `kill_attempt_evaded` event so the escapee — and the spectator — learns about
  it (#11).
