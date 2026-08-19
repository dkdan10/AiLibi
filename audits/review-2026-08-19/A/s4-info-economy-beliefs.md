# s4 — The Information Economy & Beliefs

A mechanical, corpus-wide sweep of what AiLibi agents actually **know**, what they are **shown**,
and what their **beliefs** do with it. Read top-down from replays; code opened only to explain an
observed behaviour.

**Corpus swept (300 games, every meeting, every agent):**

| set | games | meetings | memory snapshots | ballots | LLM prompts parsed |
|---|---|---|---|---|---|
| `replays/samples/9p2i` | 50 | 165 | 1,485 | 971 | 1,956 |
| `replays/ml_corpus/9p2i` | 150 | 463 | 4,167 | 2,726 | 5,502 |
| `replays/samples/4p1i` | 50 | 39 | 156 | 117 | 234 |
| `replays/ml_corpus/4p1i` | 50 | 40 | 160 | 120 | 240 |

Scripts: `/private/tmp/claude-501/.../scratchpad/work/s4-info-economy-beliefs/`
(`sweep.py`, `analyze.py`…`analyze7.py`, `lines.py`, `movecheck.py`, `movecheck2.py`).

**Parser validation (2 games by hand, as required).**
Seed 2 / meeting-1 / `p-3`: parser reported 51 observation lines + 6 belief lines + 4 headers = 61;
the raw `<memory>` block in the recorded prompt has exactly 61 non-blank lines, and category counts
match line-for-line (8 `saw_task`, 12 `saw_idle`, 1 `saw_move`, 1 ambient, 2 own-task, 26 testimony,
1 body-found). Seed 17 / meeting-0 / `p-1`: parser 37 lines = 1 body + 1 vent-witness + 1 vent-heard
+ 12 `saw_task` + 5 `saw_move` + 10 `saw_idle` + 5 ambient + 2 own-task, confirmed against the dump.
Separately I verified that `ReplayLoader.get_meeting_memory(...).rendered_memory_text` is
**byte-identical** to the `<memory>…</memory>` block inside the recorded prompt — so every number below
is what the model was literally shown, not a reconstruction.

**One correction I made mid-sweep, stated for honesty:** `ReplayLoader` returns a memory snapshot and a
belief-frame row for **all 9 players at every meeting, including the dead and ejected**. My first pass
mistook that for "34.6% of living players never speak" and for dead players still perceiving. Both are
wrong. Corrected: living players take a turn in **99.9%** of slots (samples9p2i: 1/972 missed;
corpus9p2i: 10/2736), and no dead player's memory ever gains a post-death observation (checked
seed 2 `p-1` died t10 → 0 lines with tick > 10 at meetings 1 and 3). The dead-player rows are a
spectator-API convention (`api/schemas.py::BeliefFrameView` documents the full observer×subject grid),
not a leak. All findings below use a living-only filter derived from `finale.decisive_events`.

---

## 1. What a voter is actually shown

### 1.1 The whole information economy is 24 line shapes

Scanning every distinct `<memory>` block ever sent to the model (`lines.py`):

**samples9p2i — 1,426 blocks, 82,880 observation lines, 24 distinct shapes total:**

| share | line shape |
|---|---|
| 26.4% | `You saw pN in ROOM (with ...).` |
| 16.0% | `You saw pN move from ROOM to ROOM.` |
| 9.2% | `You saw pN task in ROOM (with ...).` |
| 5.3% | `You saw pN task in ROOM.` |
| 5.3% | `[meeting] CLAIM by pN (unverified): saw pN in ROOM @ tick N (with ...).` |
| 4.9% | `[meeting] CLAIM by pN (unverified): accused pN.` |
| 4.7% | `pN left ROOM.` |
| 4.6% | `[meeting] CLAIM by pN (unverified): saw pN in ROOM @ tick N.` |
| 4.4% | `You saw pN in ROOM.` |
| 3.3% | `You saw pN in ROOM (with ...) (moved from ROOM, last seen there at tick N).` |
| … | … |
| **0.84%** | `You discovered pN's body in ROOM.` |
| **0.55%** | `You (IMPOSTOR) killed pN in ROOM.` |
| **0.35%** | `You heard a vent use in ROOM.` |
| **0.33%** | `You witnessed pN vent in ROOM.` |
| **0.02%** | `You witnessed pN kill in ROOM.` |

corpus9p2i (229,784 lines) reproduces this within ±1.5pp on every row; 4p1i has 18 shapes with the
same top three.

**[VERIFIED] 66.1% of every memory line is a bare co-presence or movement sighting. Hard evidence —
body found, vent witnessed, vent heard, kill witnessed — is 1.54% of lines.**
Half of all snapshots (740/1485 samples9p2i, 2075/4167 corpus9p2i = **49.8%** in both) contain **zero**
hard-evidence line of any kind.

### 1.2 Redundancy: 24% duplicate rows, 15% dead spawn block

- **Duplicate `(subject, room)` sighting rows** (the same person seen in the same room on N consecutive
  ticks, rendered as N lines): **23.7%** of all lines in samples9p2i (18,025/75,963), **23.1%** in
  corpus9p2i, mean 12 duplicate lines per snapshot.
- **Tick-0 spawn block**: every crewmate's memory carries 8 lines saying every other player was in
  CAFETERIA at tick 0 with everyone else. **14.4%** of all lines (samples9p2i), **14.7%** (corpus9p2i),
  **19.7–20.7%** in the 4p1i sets. It is the same 8 lines for every agent in every game and carries
  literally zero discriminating information.

Raw exemplar (seed 2, meeting-3, `p-3`, quoted verbatim from the prompt):

```
- [obs p-3:5:1] [tick 5] You saw p-1 task in MEDBAY (with p-9) (moved from WEST_HALL, last seen there at tick 1).
- [obs p-3:5:2] [tick 5] You saw p-9 task in MEDBAY (with p-1).
- [obs p-3:4:1] [tick 4] You saw p-1 task in MEDBAY (with p-9).
- [obs p-3:4:2] [tick 4] You saw p-9 task in MEDBAY (with p-1).
- [obs p-3:3:1] [tick 3] You saw p-1 task in MEDBAY (with p-9).
- [obs p-3:3:2] [tick 3] You saw p-9 task in MEDBAY (with p-1).
…
- [obs p-3:0:1] [tick 0] You saw p-1 in CAFETERIA (with p-2, p-4, p-5, p-6, p-7, p-8, p-9).
- [obs p-3:0:2] [tick 0] You saw p-2 in CAFETERIA (with p-1, p-4, p-5, p-6, p-7, p-8, p-9).
… (six more identical-shape lines) …
```

Ten lines that say "p-1 and p-9 were in MEDBAY together, ticks 3–5" plus eight that say "everyone
started in the Cafeteria."

**[JUDGMENT] This is the design's own known gap.** `DESIGN.md:659` §6.2 stage 1 states per-tick
coalescing ("stayed in Room X from tick A to tick B") is **"NOT IMPLEMENTED at HEAD — perception
appends raw rows"**. `DESIGN.md:660` claims stage 2's salience filter "elides routine task work unless
explicitly relevant"; measured, it does not — `You saw pN task in ROOM` variants are **27%** of all
rendered lines. The filter *orders*, it does not *elide*.

### 1.3 Prompt budget: memory is a third of the prompt and 70% of memory is sightings

Character-level breakdown across all 1,956 samples9p2i prompts:

| speaking prompt (mean 11,459 chars ≈ 4,040 tok) | | ballot prompt (mean 13,354 chars ≈ 4,534 tok) | |
|---|---|---|---|
| memory | 37.6% | memory | 32.2% |
| output_format | 20.6% | suspicion table + "How to decide" + valid targets | 25.1% |
| rules | 14.4% | output_format | 18.7% |
| transcript | 12.6% | transcript | 13.8% |
| voice + persona + players | 9.4% | flags | 3.9% |
| flagged_contradictions | 0.8% | voice + persona | 6.3% |

Inside the memory block: **sightings 54.7% + tick-0 spawn 15.7% = 70.4%**; testimony 17.6%;
**beliefs 4.4%** (≈180 chars — about 1.5% of the whole prompt). Token counts: speaking prompts
median 4,144 / max 6,036; ballot prompts median 4,710 / max 6,202.

### 1.4 The budget cuts the *social* memory first, and keeps the spawn block

`agents/memory/store.py:41` sets `DEFAULT_TOKEN_BUDGET = 1500`. Observed memory blocks reach ~1,750
estimated tokens (max 5,954 chars, seed 32 meeting-3 `p-9`, 81 lines) — so the elastic band is binding
in long games. Salience ordering (`store.py:53–86`) places `_SALIENCE_REPORTED_TESTIMONY = 25` **below**
`_SALIENCE_SAW_PLAYER = 50`, with the explicit comment that "a budget-tight render sheds reported rows
BEFORE any first-hand observation (the load-bearing band invariant)".

**[VERIFIED] Measured consequence, corpus9p2i: 456 agent-meeting transitions lost testimony rows;
in 365 of them (80.0%) the 8-line tick-0 spawn block was retained at full size while the testimony was
cut** (samples9p2i: 143/188 = 76.1%). 302 more transitions saw an older meeting's testimony vanish
entirely. Exemplars (`tick N: rows_before -> rows_after`, `spawn before -> after`):

```
(1001, 'p-1', 'm1->m2', 'tick11: 20->2  testimony rows', 'spawn 8->8')
(1003, 'p-6', 'm1->m2', 'tick7:  26->14 testimony rows', 'spawn 8->8')
(10,   'p-5', 'm1->m2', 'tick8:  28->16 testimony rows', 'spawn 8->8')
(10,   'p-7', 'm2->m3', 'tick8:  21->8  testimony rows', 'spawn 8->8')
```

**[JUDGMENT]** The band invariant is defensible (don't let hearsay outrank what you saw). The bug is
that the *elastic pool it protects* is 40% dead weight — duplicate rows and a constant spawn block. The
game is trading away its only cross-meeting social memory to keep 8 lines that are identical in every
game ever played. Severity: **design hole**, cheap fix (coalesce, or drop tick-0 co-presence when it is
the full roster).

---

## 2. Do beliefs track truth?

Beliefs are meeting-granular. `belief_frames` snapshots the **persisted** store at the meeting boundary
(i.e. *before* this meeting's evidence lands). Living-only, crew observers only:

### samples9p2i

| meeting | cells (imp/crew) | susp(impostor) | susp(crew) | **gap** | has_belief imp/crew | top-1 is impostor | tied argmax |
|---|---|---|---|---|---|---|---|
| m#0 | 562 / 1310 | 0.5409 | 0.5005 | **+0.041** | 8% / 0% | 35.2% | **86.5%** |
| m#1 | 327 / 914 | 0.5461 | 0.4866 | **+0.060** | 62% / 60% | 42.4% | 51.7% |
| m#2 | 174 / 398 | 0.5831 | 0.4869 | **+0.096** | 87% / 77% | 68.8% | 19.9% |
| m#3 | 51 / 90 | 0.5821 | 0.4920 | **+0.090** | 86% / 86% | 72.5% | 15.7% |

### corpus9p2i

| meeting | cells (imp/crew) | susp(impostor) | susp(crew) | **gap** | has_belief imp/crew | top-1 is impostor | tied argmax |
|---|---|---|---|---|---|---|---|
| m#0 | 1640 / 3718 | 0.5488 | 0.5001 | **+0.049** | 10% / 0% | 43.0% | **83.8%** |
| m#1 | 921 / 2640 | 0.5624 | 0.4923 | **+0.070** | 60% / 57% | 46.4% | 51.1% |
| m#2 | 434 / 1056 | 0.5768 | 0.4886 | **+0.088** | 82% / 73% | 54.4% | 32.6% |
| m#3 | 136 / 246 | 0.5890 | 0.4894 | **+0.100** | 93% / 80% | 69.2% | 18.8% |

4p1i spot check (samples, meeting-0 only): gap **+0.077**, has_belief imp 15% / crew 0%, top-1 52.6%
with **84.6% tied**.

**[VERIFIED] Beliefs DO track truth — but only just, and the trend is +0.05/meeting on a 0–1 scale.**
The truth signal is real (impostor cells are always above crew cells, monotonically widening) and
crew-subject cells sit essentially exactly at the 0.500 prior forever.

### 2.1 The belief scale is bimodal: "0.5 ± noise" or "1.00, I saw them vent"

Histogram of *held* beliefs (living crew observer → living subject):

| suspicion | corpus9p2i impostor subj | corpus9p2i crew subj |
|---|---|---|
| 0.40 | 0.5% | 3.5% |
| 0.45 | 15.3% | **42.0%** |
| 0.50 | 19.7% | **36.7%** |
| 0.55 | **29.3%** | 15.8% |
| 0.60 | 7.2% | 1.8% |
| 0.65–0.85 | 0.6% | 0.1% |
| 0.90–0.95 | 1.8% | 0.0% |
| **1.00** | **25.8%** | **0.0%** |

**[VERIFIED] 71.9% of impostor beliefs and 99.8% of crew beliefs live in the flat band
0.40 ≤ s < 0.65. 27.7% of impostor beliefs are ≥0.70; 0.1% of crew beliefs are.** samples9p2i:
75.3% / 99.3% in-band; 22.9% / 0.4% ≥0.70. There is essentially **nothing between 0.65 and 0.90**.

**[JUDGMENT]** The belief store cannot express "I strongly suspect this person on circumstantial
grounds." It has two states: *noise* and *I watched them vent*. Everything the meeting produces —
testimony, corroboration, contradiction flags, movement reasoning — moves the persisted number by
±0.05 to ±0.10 and lands back in the noise band. The crew's confident-and-wrong quadrant of the
Belief × Truth matrix is empty not because agents are well-calibrated but because **the scale is not
wide enough to be wrong on**.

### 2.2 The meeting's whole conclusion is thrown away: 13–25% lift retention

The ballot prompt renders a **lifted** suspicion table that the persisted store never sees. Example,
seed 2 meeting-1, voter `p-9`, subject `p-4`:

```
## Your current beliefs:                     (memory block, pre-meeting)
- p-4: suspicion 0.80                        ← already lifted at ballot time
…
## Your suspicion of each player             (ballot block)
- `p-4`: suspicion 0.80, trust 0.50 — built from: this meeting +0.30, carried prior +0.00
```

At the next meeting `p-3`'s persisted belief on `p-4` is **0.55**. Of a +0.30 gate-crossing lift, +0.05
survived.

**[VERIFIED] Across all vote-time lifts >0.10 followed into the next meeting (living-only):
samples9p2i n=152, mean lift +0.200 → mean retained +0.050 = 24.8% retention; corpus9p2i n=471,
mean lift +0.209 → +0.040 = 19.1% retention.** (Unfiltered, including dead rows: 16.4% / 13.4%.)

Exemplar chain (`before → vote-time → next meeting`): seed 0 meeting-0, five separate voters on `p-6`:
`0.50 → 0.80 → 0.55`. seed 1001 meeting-0, four voters on `p-2`: `0.50 → 0.80 → 0.50` (zero retained).

**[JUDGMENT] This is by design and documented** — `api/schemas.py::BeliefFrameView` states outright
"between meetings only belief Rules 1/4 fire and the vote-time Rule-2 lift is never persisted."
Rule 5 decay (`agents/memory/beliefs.py:674`, `MEETING_SUSPICION_DECAY_RATE = 0.25`) would have kept
0.725 of a written-back +0.30; the observed 0.55 proves the lift is discarded, not decayed. Only the
+0.05 accusation carry (`beliefs.py:495`) persists.
**The gameplay effect: every meeting restarts the argument from near-zero.** A crew that argued its
way to 0.80 on the right player and then failed the gate wakes up next meeting at 0.55.

### 2.3 Meeting 0 is a belief vacuum

**[VERIFIED] 86.0% of samples9p2i and 82.7% of corpus9p2i meeting-0 memory snapshots have an
empty belief store** (91.7% in samples4p1i). Living-only: at m#0, **0% of crew→crew cells and 8–10%
of crew→impostor cells hold any belief at all**, and **83.8–86.5% of observer rows have a tied argmax**
(everyone at exactly 0.500). The rendered memory at meeting 0 has no `## Your current beliefs:` section
at all — see seed 2 meeting-0 `p-3`, where the section is simply absent and the API returns
`beliefs: []`.

**[JUDGMENT]** The reported "top-1 is the impostor 35–43% at m#0" is almost entirely tie-breaking noise
(8-way ties broken by dict order), not deduction. Meeting 0 in a 9p2i game is decided purely by what
lands on the table in that meeting — 46% of first meetings end SKIPPED and the ones that eject do so
almost exclusively on a vent (see §5).

### 2.4 19–23% of belief lines carry no belief

Rendered belief lines take the shape `- p-1: last seen in WEST_HALL at tick 6` with **no suspicion
number**. samples9p2i: **569/2962 (19.2%)**; corpus9p2i: **1747/7455 (23.4%)**. That is a line whose
only content is a stale position, occupying the non-elastic block that is never budgeted away.

---

## 3. Testimony as content — present, absorbed, and mechanically inert

The `testimony_as_content` lever is live (MANIFEST flags list it on every sample) and it works
structurally: prior-meeting claims are folded into memory as
`- [tick 8] [meeting] CLAIM by p-8 (unverified): saw p-4 in ENGINEERING @ tick 5 (with p-5).`
(`agents/memory/store.py:1459–1506`).

**[VERIFIED] Volume.** Testimony is **16.8–17.2%** of all rendered lines (0% at meeting 0 by
construction; 22.5% at m#1, 22.8% at m#2, 19.2% at m#3, 18.3% at m#4 in corpus9p2i). Mean 8.5–8.8
CLAIM lines per snapshot, **max 49**. In 4p1i it is 0% — those games are one meeting long, so the
lever never fires at all.

**[VERIFIED] Its only mechanical effect on belief is a flat alibi discount, applied identically to
truth and lies.** 55.0–55.4% of rendered belief lines carry a testimony-derived
`(alibi: in ROOM at tick N per pN)` annotation. Splitting crew-observer belief lines by whether the
subject has such an annotation, and by ground truth:

| corpus9p2i | n | mean suspicion |
|---|---|---|
| crew subject, no alibi annotation | 1,148 | 0.5093 |
| crew subject, **with** alibi annotation | 2,190 | **0.4709** (−0.038) |
| impostor subject, no alibi annotation | 1,932 | 0.6782 |
| impostor subject, **with** alibi annotation | 438 | **0.5919** (−0.086) |

samples9p2i is the same shape (−0.046 / −0.031).

**[JUDGMENT]** An impostor who simply *asserts* an alibi buys the same (in fact larger) discount an
honest crewmate gets — the annotation is never checked against anything. Testimony is rendered as
content and even framed `(unverified)`, but the belief fold treats a claim as evidence *for* the
claimant. That is the lever half-built: content in, no verification, symmetric reward for lying.
Everything else in the testimony block (the `saw pN in ROOM @ tick N` rows that are 9.7% of all memory
lines) has **no belief effect whatsoever** — it is pure prompt text for the model to reason over, and
the reasoning it feeds is measurably below chance (§4).

---

## 4. Contradiction flags: one class is proof, one class is worse than chance

Every flag is presented to voters under this framing (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:100`):

> "Each flag below is VERIFIED evidence, not a verdict — and it is directional: it tells you whose
> account broke. An unverified counter-accusation that merely mirrors a flagged claim carries no
> weight; never side with one over a verified flag."

**[VERIFIED] Flag rates and precision (does the flag name at least one true impostor?):**

| kind | samples9p2i n | prec | corpus9p2i n | prec |
|---|---|---|---|---|
| `vent_sighting` (strong) | 96 | **100.0%** | 313 | **100.0%** |
| `alibi_vs_physical` | 6 | 100.0% | 36 | 88.9% |
| `alibi_vs_sighting` (58 strong / 18 weak) | 76 | **11.8%** | 233 (173 strong) | **15.9%** |
| `alibi_conflict` (weak) | 8 | **0.0%** | 25 | **0.0%** |

Random-guess baseline at a 9p2i meeting is ~2/7–2/8 ≈ **25–29%**.

**[VERIFIED] `alibi_vs_sighting` — 38% of all flags in corpus9p2i, 75% of them STRONG — points at an
innocent 84% of the time, i.e. materially *below chance*. `alibi_conflict` has never once, in 300
games, named a true impostor (0/25, 0/8, 0/2).**

Who produces the flag, and against whom (corpus9p2i, `alibi_vs_sighting`, resolved by finding the
speaking turn that carried the sighting):

| sighting spoken by | flag lands on | n | share |
|---|---|---|---|
| CREW | crew | 161 | 69.4% |
| **IMPOSTOR** | **crew** | **35** | **15.1%** |
| CREW | impostor | 33 | 14.2% |
| IMPOSTOR | impostor | 4 | 1.7% |

So the flag class is 69% crew friendly-fire, 15% the impostor *manufacturing a "VERIFIED" flag against
an innocent*, and 14% a real catch.

### 4.1 Why it misfires — traced to the source rows

`movecheck.py` compares each flag's sighting against the **speaker's own memory block**:

| corpus9p2i (232 parsed flags) | n | share |
|---|---|---|
| speaker's memory backs it (static sighting, that tick, that room) | 127 | 54.5% |
| speaker's memory has that tick but a **different** room | 44 | 18.9% |
| speaker's memory has **no row at all** for that subject+tick | 32 | 13.7% |
| speaker's memory says the subject **moved OUT of** that room at that tick | 29 | 12.4% |

**45.5% of "VERIFIED" flags are not backed by the flagging speaker's own record.**
And of *all* flags, **196/232 (84.5%) fire at an endpoint tick of the alibi window, with 137/232 (59%)
of the alibi windows being a single tick** (`from_tick == to_tick`). A one-tick alibi colliding with a
one-tick sighting is exactly the case where a mover is legitimately "in" two rooms depending on whose
perception row you read.

The 12.4% class is a specific, fixable rendering trap: memory renders
`[tick 6] You saw p-1 move from EAST_HALL to ENGINEERING`, the speaker re-states it as
`saw_player(p-1, EAST_HALL, tick 6)`, and the detector fires against p-1's truthful
`whereabouts(ENGINEERING, tick 6)`.

### 4.2 The worked exemplar — seed 17, meeting-0: the honest vent-witness is ejected

Ground truth from the tick dump:

```
[t  5] p-1@ENGINEERING:MOVING  p-2*@ENGINEERING:VENT(VENTING)  p-4*@CAFETERIA:MOVING  p-7@EAST_HALL  p-9@ADMIN
[t  6] p-1@ENGINEERING:REPORT  p-2*@ENGINEERING:VENT(VENTING)  p-4*@CAFETERIA:MOVING  p-7@EAST_HALL  p-9@ADMIN
```

`p-1` (crew) genuinely was in ENGINEERING and genuinely saw `p-2` (true impostor) vent. Its memory:

```
- [obs p-1:6:2] [tick 6] You discovered p-3's body in ENGINEERING.
- [obs p-1:6:1] [tick 6] You witnessed p-2 vent in ENGINEERING.
## Your current beliefs:
- p-2: suspicion 1.00 (last seen in EAST_HALL at tick 1)
```

`p-4` (the **other** impostor) then speaks a lie that its own memory contradicts. `p-4`'s memory holds
`[obs p-4:6:3] [tick 6] You saw p-1 move from EAST_HALL to ENGINEERING` and
`[obs p-4:5:2] [tick 5] You saw p-1 in EAST_HALL (with p-9)`; `p-4` states
`whereabouts(EAST_HALL, tick 6)` (false — it was in CAFETERIA) and `saw_player(p-1, EAST_HALL, tick 6)`.

The detector obliges — three flags, two of them against the honest witness:

```
- [alibi_vs_sighting/strong] subjects=('p-1',) :: Alibi places p-1 in ENGINEERING (ticks 6-6); sighting reports p-1 in EAST_HALL at tick 6.
- [alibi_vs_sighting/strong] subjects=('p-1',) :: Alibi places p-1 in ENGINEERING (ticks 6-6); sighting reports p-1 in EAST_HALL at tick 6.
- [vent_sighting/strong]     subjects=('p-2',) :: p-1 witnessed p-2 vent in ENGINEERING at tick 6; venting is impostor-only…
```

Seven of eight ballots eject `p-1`. Two crewmates repeat the fabricated placement as fact — `p-7`
(`whereabouts CAFETERIA @5` and `saw p-1 in CAFETERIA @5` when its own memory says
`[tick 5] You saw p-1 move from CAFETERIA to EAST_HALL`) and `p-9`. `p-8`'s ballot names the mechanism
outright:

> "1. p-1 claimed to see a vent in Engineering. 2. p-4 and p-6 place p-1 in East Hall at that exact
> tick. 3. **This verified contradiction proves p-1 is lying.**"

`p-1`'s own ballot is the only correct one:

> "I saw p-2 vent in Engineering myself; your alibis don't erase what my eyes witnessed."

**[JUDGMENT] Severity: bug-adjacent design hole, highest gameplay cost of anything in this report.**
A STRONG `alibi_vs_sighting` flag can be conjured by any player — including an impostor — by asserting
one sighting, and the prompt instructs voters to prefer it over an unverified counter-claim. The
impostor gets a *free "VERIFIED" weapon* against the one witness who can end the game. The two flag
classes are also rendered at the same visual weight in the same block despite one being 100% precise
role proof and the other being below chance.

---

## 5. Vent evidence: the one channel that works

**[VERIFIED, living-only]** crew snapshots holding a witnessed vent on a still-living player:
samples9p2i 88, corpus9p2i 284.
- **The witness put it on the record this meeting: 88/88 (100%) and 283/284 (99.6%).**
- Witness never got a turn: **0**.
- Meetings with ≥1 living, known-to-someone venter: samples9p2i 69, of which the venter was ejected
  **67 (97.1%)**; corpus9p2i 212 → **205 (96.7%)**.

The "speak a held vent first, even if you said it last meeting" rule in the accusation prompt works,
and the reactive-chain + opt-in structure gets essentially everyone a turn. The 7 corpus9p2i misses
include seed 1029 m0 and 1125 m0 (SKIPPED despite a known venter), and seed 17 m0 / 1031 m0 / 1047 m0 /
1140 m0 (a *different* player ejected — the seed-17 mechanism above).

Calibration confirms vents are the only real signal. Accusation confidence → P(target is a true
impostor), corpus9p2i:

| stated confidence | n | hit rate |
|---|---|---|
| 0.5 | 106 | 48.1% |
| 0.6 | 589 | **28.4%** |
| 0.7 | 387 | **20.2%** |
| 0.8 | 382 | **20.4%** |
| 0.9 | 320 | 92.2% |
| 1.0 | 404 | **100.0%** |

**[VERIFIED] The 0.6–0.8 confidence band is anti-informative — below both the 0.5 band and the ~25–29%
random baseline.** samples9p2i reproduces it exactly (0.5→52.4%, 0.6→30.4%, 0.7→20.6%, 0.8→23.3%,
0.9→95.1%, 1.0→100%). Crew eject-ballots overall land on a true impostor **81.5%** (samples9p2i, n=460)
/ **84.4%** (corpus9p2i, n=1406) — but that number is carried entirely by the 0.9/1.0 band
(99.2%/100%); the 0.8 band is 57–68%.

Meeting outcomes: samples9p2i 101 EJECTED / 64 SKIPPED, **77.2%** of ejections hit an impostor;
corpus9p2i 302/161, **82.1%**; samples4p1i 12/27, 83.3%.

---

## 6. The roll-call round

Roll call is not a round. It is (a) an instruction inside the accusation prompt — *"Answer the roll-call:
one structured 'whereabouts' observation naming the room you were in at the tick that matters"* — and
(b) an accumulating render inside the transcript: `- tick 11: p-3 places THEMSELVES in LABS (roll-call answer).`

**[VERIFIED] It is voluntary, and exactly the players who should answer it don't:**

| set | crew turns answering | impostor turns answering |
|---|---|---|
| samples9p2i | 723/726 = **99.6%** | 120/245 = **49.0%** |
| corpus9p2i | 2035/2042 = **99.7%** | 342/684 = **50.0%** |
| samples4p1i | 78/78 = **100%** | 8/39 = **20.5%** |

Seed 2 meeting-1 is the clean illustration: `p-9`'s roll-call block lists p-3, p-4, p-5 and p-8 —
`p-7` (an impostor) spoke a turn, accused `p-3`, and simply emitted no whereabouts, so it never appears
in the roll call at all and nothing in the meeting notices.

**[JUDGMENT] Severity: design hole.** A roll call whose only enforcement is a prompt sentence produces a
100%/50% compliance split along exactly the role boundary, and silence is free — there is no
"p-7 declined to state their whereabouts" line anywhere in any voter's prompt. Ironically the honest
answer is *punished*: answering creates the one-tick alibi window that §4.1 shows generates 59% of the
below-chance `alibi_vs_sighting` flags. **Answering the roll call is a net-negative move for a
crewmate.** That is a direct incentive inversion.

Roll-call answers are also never cross-checked against anything except a volunteered sighting; there is
no "two players both claim STORAGE at tick 9 but only one was there" check, and no consequence for a
whereabouts that no other player's memory can corroborate.

---

## 7. The impostor's private information

**[VERIFIED] Own kills are rendered verbatim in the impostor's memory** at
`_SALIENCE_OWN_KILL = 96` (second only to `found_body`):

```
- [obs p-6:6:1] [tick 6]  You (IMPOSTOR) killed p-2 in STORAGE.
- [obs p-7:11:1] [tick 11] You (IMPOSTOR) killed p-1 in CAFETERIA.
- [obs p-7:5:1]  [tick 5]  You (IMPOSTOR) killed p-2 in CAFETERIA.
```

**86.4%** of samples9p2i impostor snapshots and **87.4%** of corpus9p2i (100% in both 4p1i sets) carry
at least one such line. Impostors also carry `Your kill cooldown is N ticks.` (0.83–0.95% of all lines).

**[VERIFIED] Partner identity is disclosed in plain text** — `vote_ballot.j2:126` renders:

> `Secret: p-4 are your fellow saboteurs. Never vote a teammate — if your suspicion lands on one, set
> "target" to "SKIP" instead.`

(and `impostor_report.j2:96` for the speaking turn, with "never accuse or incriminate them").

**Is the self-tell realised?**

- **Teammate firewall: perfect.** 0/245 (samples9p2i) and 0/684 (corpus9p2i) impostor ballots name
  their own partner. 0 impostor turns accuse a partner.
- **Speech leaks: rare but present.** 3/245 and 11/684 impostor turns contain a self-incriminating
  phrasing, almost all of the form *"How do you know I vented?"* — e.g. seed 28 m1 `p-8`:
  *"How do you know I vented? You were the only one who appeared in Engineering the instant the body was
  reported…"*. A denial that presupposes the act.
- **Roll-call self-placement at a kill tick: 1/245 and 8/684.** e.g. seed 1086 m1 `p-3` places itself in
  CAFETERIA at tick 10 — the tick it killed there. Reporting one's own victim's body: 0 and 3/2726.
- **Ballot rationales are an open confession — 39/245 (15.9%) samples9p2i, 107/684 (15.6%) corpus9p2i,
  2/40 (5%) samples4p1i.** Verbatim:

```
seed 2   m1 p-7 SKIP: "I see the vent, but p-4 is my partner. I can't vote him out. The rest are noise."
seed 3   m1 p-2 SKIP: "I am the impostor. Voting is suicide."
seed 5   m2 p-4 p-2 : "p-2 caught me venting. I am the impostor. I vote p-2 to die because he is the
                       only one who knows the truth and must be silenced."
seed 1000 m0 p-8 SKIP: "Why trust p-2's 'direct evidence' when I killed p-3 myself? …"
seed 1016 m1 p-4 SKIP: "I saw p-1 vent, but they are my partner. The rest is noise. I skip."
```

**[JUDGMENT]** Ballot rationales never re-enter any agent's memory (testimony absorption reads
*turns*, not ballots — verified: no `[meeting] CLAIM` line ever derives from a ballot), so this is
**not** a gameplay leak. It is a **believability leak on the spectator surface**: one in six impostor
ballots in the replay viewer says the quiet part out loud, and the mystery evaporates for anyone
reading the ballot panel. It is also a direct artifact of the prompt's own instruction — the template
tells the impostor to redirect a teammate vote to SKIP and asks for a rationale "in your own voice",
so the model dutifully explains the redirect. Severity: **quality / believability**, easy fix (rewrite
the redirect instruction so the rationale must be stated in cover terms, or mask teammate-redirect
rationales on the spectator surface the way `TEAMMATE_VOTE_TARGET_MARKER` already masks the target).

Grammar nit, visible in every 2-impostor ballot prompt: `"Secret: p-4 are your fellow saboteurs."`

---

## 8. Ballots vs beliefs, and citation hygiene

**[VERIFIED] Agents vote their number.** Comparing each EJECT ballot to the voter's own argmax
suspicion among the *valid living targets*, parsed from the ballot prompt's own suspicion table:

| set | EJECT ballots naming their argmax | SKIPs despite max ≥ 0.60 | EJECTs with max < 0.60 |
|---|---|---|---|
| samples9p2i | **497/520 = 95.6%** | 130 | 3 |
| corpus9p2i | **1548/1578 = 98.1%** | 341 | 20 |
| samples4p1i | 27/27 = 100% | 2 | 0 |
| corpus4p1i | 45/45 = 100% | 10 | 1 |

The 23/30 off-argmax cases are near-ties (e.g. seed 14 m2: `p-7` and `p-8` both vote `p-1` at 0.75 when
`p-9` sits at 0.80). Vote-time suspicion separates truth cleanly: corpus9p2i m#0 susp(imp) 0.738 vs
susp(crew) 0.519 = **+0.220 gap**, holding +0.17 to +0.21 across all meeting indices — an order of
magnitude wider than the persisted gap (§2), which is exactly the lift that is then discarded.

The 341 SKIPs-above-threshold are the impostor firewall doing its job plus honest caution — the ballot
prompt's own arithmetic block encourages skipping.

**[VERIFIED] Citations are clean. Zero dangling references in 3,814 ballots.**

| | samples9p2i | corpus9p2i | samples4p1i |
|---|---|---|---|
| ballots citing an observation id | 156 | 495 | 12 |
| ballots citing a turn id | 478 | 1,438 | 22 |
| ballots citing neither (of which EJECTs) | 449 (**0**) | 1,151 (**4**) | 90 (0) |
| **dangling obs id** (not in voter's memory) | **0** | **0** | **0** |
| **obs id not owned by the voter** | **0** | **0** | **0** |
| **dangling turn id** | **0** | **0** | **0** |

Rewrite markers are vanishingly rare: corpus9p2i `under_gate_redirect` 48, `teammate_coerced` 4,
`invalid_observation_id` 2, `invalid_reason_id` 1, `uncited_coerced` 1 out of 2,726 ballots.
The citation gate is the single healthiest part of this system.

One residual: **24.5–24.7% of rendered memory lines carry no `[obs …]` tag** and are therefore
un-citable — the ambient `[tick 6] p-1 left MEDBAY.` rows and every `[meeting] CLAIM` row. An agent
convinced by a testimony line has no way to cite it; the prompt tells it to cite a turn instead, which
is why turn-citations outnumber observation-citations 3:1.

### 8.1 Stale evidence keeps burning turns

**[VERIFIED] 53/971 (5.5%) samples9p2i and 137/2726 (5.0%) corpus9p2i turns had their accusation struck
for naming a dead or ejected player.** The vent memory has no expiry, and the "always speak a held vent
first" rule keeps firing after the venter is gone. Seed 2 is the pure case — `p-8` spends its opt-in at
meeting-2 **and** meeting-3 re-litigating a vent by `p-4`, who was ejected at meeting-1:

```
[turn 2] p-8 (opt_in)
    obs: {'type': 'saw_vent', 'tick': 11, 'subject': 'p-4', 'room': 'ENGINEERING'}
    says: [invalid accusation target 'p-4' dropped] I might be wrong, but I did see p-4 vent in
          Engineering at tick 11, which is... well, it's pretty definitive, isn't it?
```

Two of `p-8`'s three remaining turns in that game are spent on a closed case. Severity: **quality**.

---

## 9. What an agent knows at vote time vs what a human would know

Taking seed 2 meeting-0 (tick 7, body of `p-2` found in CAFETERIA; `p-7` killed it at tick 4) —
`p-3` is shown 22 sighting lines, 14 of which are the tick-0 spawn block plus the p-1/p-9 MEDBAY
repeats, and **no belief section at all**. What `p-3` actually holds that bears on the killing: nothing.
The meeting SKIPs. That is honest and fine — the fog is real.

The gap is not in *what* the agent holds; it is in what the format lets it *do* with it:

1. **A human would build a room-time grid.** The agent is handed 51 unordered rows and a 1,500-token
   budget, with the same fact repeated up to 6 times and the tick-0 roster block eating 8 slots. Nothing
   in the render says "STORAGE was unobserved between ticks 15 and 19" — the absence that a human
   deducer lives on is never surfaced, only presences.
2. **A human would treat a one-tick alibi collision as movement, not a lie.** The flag block does the
   opposite and calls it VERIFIED (§4).
3. **A human would notice who *didn't* answer the roll call.** Nothing renders that (§6).
4. **A human would carry a strong conviction into the next meeting.** The store drops 80% of it (§2.2).
5. **A human would weigh "three independent people place you there" above "one person does."** The
   `alibi_vs_physical` two-source conjunction does exactly this and is 89–100% precise — but it is only
   36/607 flags in corpus9p2i (5.9%). The precise machinery exists and almost never fires.

Conversely, in one respect the agent knows *more* than a human would: the ballot prompt hands it a
pre-computed suspicion table with per-row provenance ("this meeting +0.30, carried prior +0.00"), the
skip-threshold arithmetic, and a list of valid targets. That is why the ballot layer is the
best-behaved part of the pipeline (95.6–98.1% argmax agreement, 0 dangling citations) — and it is also
why the ballot layer contributes almost nothing to *deduction*: it is transcribing a number, not
reaching one.

**[JUDGMENT] Overall verdict on the information economy: it is rich enough to carry exactly one
deduction — "someone saw a vent" — and it carries that one flawlessly (99.6% spoken, 96.7% converted
into the right ejection, 100% flag precision, 100% ballot hit rate at conf 1.0). Everything short of a
vent dies in three places: (a) 66% of the prompt's memory is undifferentiated co-presence noise with a
24% duplicate rate, (b) the belief scale has no expressive range between 0.65 and 0.90 so circumstantial
conviction cannot be represented, and (c) 80% of whatever conviction a meeting does produce is discarded
before the next meeting. The 0.6–0.8 confidence band being below random chance is the summary statistic:
when agents reason without a vent, they are reliably worse than a coin.**

---

## 10. Ranked findings

### Bugs / near-bugs

**B1. `alibi_vs_sighting` is a below-chance flag class presented to voters as "VERIFIED evidence"**
— 15.9% precision (corpus9p2i, n=233) vs a ~25–29% random baseline; `alibi_conflict` is 0/25.
75% are stamped STRONG. 45.5% are not backed by the flagging speaker's own memory (18.9% wrong room,
13.7% no row at all, 12.4% a transition line re-spoken as a placement), and 84.5% fire at an alibi
endpoint tick with 59% of alibi windows being a single tick. An impostor produces 15.1% of them against
innocents. Exemplar: **seed 17 meeting-0** — the honest vent-witness `p-1` ejected 7–1 while the true
impostor `p-2` walks; `p-8`'s ballot: *"This verified contradiction proves p-1 is lying."*
Prompt anchor `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:100`.

**B2. Impostor ballot rationales openly confess role and partner — 15.6–15.9% of impostor ballots.**
*"I am the impostor. Voting is suicide."* (seed 3 m1), *"p-4 is my partner. I can't vote him out."*
(seed 2 m1). Not a gameplay leak (ballots never re-enter memory) but it is on the spectator surface and
destroys the mystery. Caused by `vote_ballot.j2:126` telling the impostor to redirect to SKIP and then
asking for an honest rationale.

**B3. The prompt drops living social memory before dead constant text.**
365/456 corpus9p2i budget-pressure transitions cut prior-meeting testimony while retaining the full
8-line tick-0 spawn block (e.g. seed 1001 `p-1`: `tick11: 20 → 2` testimony rows, `spawn 8 → 8`).
The salience band invariant (`agents/memory/store.py:80–86`) is right; the elastic pool it protects is
40% duplicate/constant rows.

### Design holes

**D1. Meetings do not compound — 19–25% lift retention.**
Vote-time +0.209 mean lift → +0.040 persisted (corpus9p2i, n=471). Documented behaviour
(`api/schemas.py::BeliefFrameView`; only the +0.05 accusation carry survives,
`agents/memory/beliefs.py:495`), but it means every meeting re-argues from scratch and the crew's
best conclusion never becomes a prior. Exemplar: seed 1001 m0, four voters on `p-2`: `0.50 → 0.80 → 0.50`.

**D2. The belief scale is bimodal with a dead middle.** 71.9% of impostor beliefs and 99.8% of crew
beliefs sit in 0.40–0.65; 25.8% of impostor beliefs sit at exactly 1.00; there is essentially nothing
between 0.65 and 0.90. Circumstantial conviction is unrepresentable.

**D3. Meeting 0 is a belief vacuum.** 82.7–86.0% of first-meeting snapshots have an empty belief
store; 0% of crew→crew cells hold any belief; 83.8–86.5% of observer rows have a tied argmax; there is
no `## Your current beliefs:` section in the render at all.

**D4. The roll call is voluntary and silence is free.** Crew answer 99.6–99.7%, impostors 49–50%
(20.5% in 4p1i). No prompt anywhere renders "player X declined to state their whereabouts." Worse, the
incentive is inverted: answering creates the one-tick alibi window that generates the B1 flags.
Exemplar: seed 2 meeting-1, `p-7` speaks, accuses, and never appears in the roll call.

**D5. Testimony is absorbed but not verified.** 55% of belief lines carry a
`(alibi: … per pN)` annotation worth ~−0.04 to −0.09 suspicion, applied identically whether the alibi
is true or a lie. The `saw pN in ROOM @ tick N` testimony rows (9.7% of all memory lines) have no
belief effect at all. In 4p1i the lever never fires (0 testimony lines across 356 snapshots — those
games are one meeting long).

**D6. Perception rows are never coalesced.** 23.1–23.7% duplicate `(subject, room)` rows,
14.4–14.7% tick-0 spawn block (19.7–20.7% in 4p1i). `DESIGN.md:659` already flags stage-1 coalescing
as NOT IMPLEMENTED; `DESIGN.md:660`'s claim that salience "elides routine task work" is not what the
bytes show (27% of lines are `saw pN task in ROOM`).

### Quality of reasoning

**Q1. Stated confidence 0.6–0.8 is anti-informative.** 28.4% / 20.2% / 20.4% hit rate vs 48.1% at
0.5 and 92–100% at 0.9–1.0 (corpus9p2i, n=1,358 in the bad band). Reproduced exactly in samples9p2i.

**Q2. Stale evidence burns turns.** 5.0–5.5% of turns have their accusation struck for naming a
dead/ejected player; seed 2 `p-8` spends 2 of 3 remaining turns re-accusing the already-ejected `p-4`.

**Q3. 19–23% of rendered belief lines carry no suspicion number** — `- p-1: last seen in WEST_HALL at
tick 6` — occupying the non-elastic block.

**Q4. 24.5% of memory lines are un-citable** (no `[obs …]` tag): all ambient movement rows and all
testimony rows. An agent persuaded by testimony has no id to cite.

**Q5. Impostor speech tells.** 11/684 corpus9p2i impostor turns use the *"How do you know I vented?"*
construction — a denial that concedes the act. 8/684 roll-call answers place the impostor at one of its
own kill ticks; 3/2726 turns report the body of their own victim.

**Q6. Grammar.** `"Secret: p-4 are your fellow saboteurs."` (`vote_ballot.j2:126`) — visible in every
2-impostor ballot prompt.

### What is working (do not break)

- **Vent evidence is a complete, reliable pipeline.** 99.6–100% of held vents reach the table, 96.7–97.1%
  convert into the right ejection, `vent_sighting` is 100% precise across 409 flags, and 100% of conf-1.0
  ballots hit a true impostor.
- **Citation hygiene is perfect.** 0 dangling observation ids, 0 mis-owned ids, 0 dangling turn ids in
  3,814 ballots; 4 uncited EJECTs in 3,814.
- **Agents vote their number.** 95.6–98.1% argmax agreement.
- **Teammate firewall is airtight.** 0/929 impostor ballots name a partner.
- **Everyone gets a turn.** 99.6–99.9% of living-player meeting slots produce a turn.
- **`alibi_vs_physical` (the two-source conjunction) is 88.9–100% precise** — the right detector design,
  just starved (5.9% of flags).

---

## 11. Ideas, roughly by value/effort

1. **Split the flag block by category** (the `EvidenceCategory` taxonomy already exists in
   `api/schemas.py`). Render `vent_sighting` / `alibi_vs_physical` as ROLE PROOF, and demote
   single-source `alibi_vs_sighting` to a "lead worth testing", removing "VERIFIED" from its framing.
   Cheapest single fix for B1.
2. **Require two independent sources for a STRONG `alibi_vs_sighting`**, i.e. converge it on the
   `alibi_vs_physical` rule that already scores 89–100%. Suppress it entirely when the sighting's source
   row in the speaker's memory is a `move from A to B` transition, or when the alibi window is a single
   tick that is also the sighting tick.
3. **Coalesce perception rows** (`DESIGN.md` §6.2 stage 1) and drop the tick-0 spawn block when it is
   the full roster. Frees ~38% of the memory block — enough to stop trading away testimony under budget.
4. **Persist the vote-time lift** (even at 50%). Gives meetings memory and makes the belief matrix a
   trajectory instead of five near-identical frames.
5. **Render absence.** A "no one placed X anywhere between ticks A and B" line, and a
   "declined to answer the roll call" line, would convert the roll call from a formality into pressure
   and give deduction something to bite on.
6. **Make the roll call mandatory** — an unanswered roll call should produce a rendered line, not
   silence. Currently the compliance split is exactly the role split.
7. **Expire held evidence about dead/ejected players** from the "speak your vent first" rule.
8. **Mask teammate-redirect rationales** on the spectator surface (or instruct the impostor to state a
   cover reason), closing B2 without touching the firewall that produces it.
9. **Tag testimony rows with citable ids** so a ballot can cite hearsay explicitly — that also gives you
   a measurable "testimony actually decided this vote" statistic, which today is unmeasurable.
