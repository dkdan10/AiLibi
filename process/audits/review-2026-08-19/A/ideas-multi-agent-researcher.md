# Ideas from a multi-agent / LLM-reasoning research lens

**Scope.** Top-down spectator pass. I watched `replays/samples/9p2i` seeds 17 and 2, `replays/samples/4p1i`
seed 29 end-to-end with `watch.py`, read the raw `llm_calls` prompts and responses for those meetings, read
rendered memory for `p-8` and `p-1`, then ran five census scripts over all 300 committed games
(707 meetings, 7,458 meeting LLM calls) to size what I saw. Scripts:
`scratchpad/work/ideas-mar/{probe,probe2,probe3,probe4}.py`. Nothing in the repo was modified.

Every number below is `[VERIFIED]` unless tagged `[JUDGMENT]`.

---

## Part 0 — The one game that contains the whole thesis

`replays/samples/9p2i` seed 17, meeting-0 @ tick 6. `p-2*` kills `p-3` in ENGINEERING at t4 and vents at t5.
`p-1` walks in, sees the vent AND the body, and reports.

```
[turn 0] p-1 (opening)
    obs: {'type':'saw_vent','tick':6,'subject':'p-2','room':'ENGINEERING'};
         {'type':'found_body','tick':6,'body_of':'p-3','room':'ENGINEERING'};
         {'type':'whereabouts','tick':6,'room':'ENGINEERING'}
    says: I found p-3 dead in Engineering, but more importantly, I saw p-2 vent right there at tick 6.
```

Everything `p-1` said is true. The engine agrees: the flag block carries

```
- [vent_sighting/strong] subjects=('p-2',) :: p-1 witnessed p-2 vent in ENGINEERING at tick 6; venting is
  impostor-only, and the spoken observation matches the witness's own record.
```

Sitting two lines above it, printed **twice**, is the flag that actually decides the meeting:

```
- [alibi_vs_sighting/strong] subjects=('p-1',) :: Alibi places p-1 in ENGINEERING (ticks 6-6);
  sighting reports p-1 in EAST_HALL at tick 6.
- [alibi_vs_sighting/strong] subjects=('p-1',) :: Alibi places p-1 in ENGINEERING (ticks 6-6);
  sighting reports p-1 in EAST_HALL at tick 6.
```

`p-1` really was in EAST_HALL at t4 and ENGINEERING at t5–t6. **EAST_HALL and ENGINEERING are adjacent**
(`ADMIN/CAFETERIA/ENGINEERING` are EAST_HALL's neighbours — dumped from `v.map.edges`). The impostor `p-4*`
re-dated a true t4 sighting by one tick and manufactured a STRONG "VERIFIED" contradiction out of a corridor.
`p-1` is ejected 7–1. Both impostors survive; the crew wins 40 ticks later only because a *second* vent gets
caught.

The tell that this is a reasoning-substrate failure and not a bad model: **`p-8` accused the right player in its
own turn and then voted against itself.**

```
[turn 6] p-8: claims: {'type':'accusation','against':'p-2','confidence':0.6,
   'reason':'p-1 witnessed p-2 venting at the body location; ... p-2 has provided no alibi for tick 6.'}
ballot   p-8 -> p-1  conf=0.85
   rationale: 1. p-1 claimed to see a vent in Engineering. 2. p-4 and p-6 place p-1 in East Hall at that
              exact tick. 3. This verified contradiction proves p-1 is lying.
```

`p-8` noticed the strongest real signal in the game — *the accused venter gave no account of himself at all* —
and then discarded it because a label said VERIFIED. Six things had to be missing for that to happen. They are
the six diagnoses below.

---

## Part 1 — Diagnosis

### D1. The crew has perception but no shared world model, and the headroom is large
The prompt asks for exactly the right object — `accusation_round.j2`: *"The crew catches the impostor by
establishing who was WHERE and WHEN ... that single checkable placement is what lets the crew clear you and
**corner whoever cannot be placed**"* — and then gives no one any way to build it. Each agent holds a private,
unindexed event log; the only cross-agent aggregation in the system is a plurality vote.

I measured the headroom with a zero-LLM oracle. At each of the **626 body-triggered meetings**, take the last
kill before the meeting `(tick tk, room R)` and clear every living player whom a *surviving crewmate* was
co-present with, in a room other than `R`, at `tk`. That uses nothing but same-room co-presence — precisely
what crew perception already records, and exactly what a crewmate would say out loud.

| computable candidate set | meetings | of 626 |
|---|---:|---:|
| contains the actual killer | 581 | **92.8%** |
| exactly 1 candidate | 109 | 17.4% |
| … and that candidate *is* the killer | **103 / 109** | **94.5%** |
| ≤ 2 candidates | 208 | 33.2% |
| … containing the killer | 183 / 208 | 88.0% |

Against that: of the 354 ejections at those meetings, **61 (17.2%) landed on someone the crew's own pooled
perception had already cleared**.

A cheap running version compounds: score each living player by how many kill windows they could not be cleared
for. That tally's top-ranked player is a real impostor in **286/463 (61.8%)** of `ml_corpus/9p2i` meetings and
**100/165 (60.6%)** of `samples/9p2i`, against a ~25% chance baseline — and the meeting's actual ejection agrees
with it only 137/463 (29.6%). No LLM call is involved in any of that.

*Caveat [JUDGMENT]:* this is an upper bound that assumes honest pooling. An impostor who lies about co-presence
can falsely clear a teammate — which is why the proposal below (R2) fills a cell only on two-sided agreement.

### D2. The one aggregation that does exist is geometry-blind
`alibi_vs_sighting/strong` compares a room at a tick to a room at a tick, and nothing anywhere knows the map.
Parsing all 234 strong instances against `canonical_1` adjacency:

| | count | share |
|---|---:|---:|
| the two rooms are **adjacent** (one tick of walking reconciles both statements) | **148** | **63.2%** |
| distance 2 | 71 | 30.3% |
| distance ≥3 | 15 | 6.4% |
| alibi window is a **single tick** | 187 | 79.9% |
| adjacent **and** the subject is innocent | 130 | 55.6% |

Those 234 flags drove 126 ejections. **78 of the 126 were adjacent-room flags, and 68 of those 78 (87.2%)
ejected an innocent.** Seed 17 m0 is one of the 68. The weak tier behaves identically (50/78 adjacent).

Confirmed absent from the prompts too: across 7,458 meeting LLM calls, **zero** carry a room list, an adjacency
table or travel times. In `4p1i` seed 29 the impostor wins the meeting on a pure geometry bluff no one can check
— *"p-1 was in Labs at tick 5 and suddenly appeared at the scene by tick 10, which is a very tight window to
cross the station"* — for a walk that actually took 5 ticks over 5 hops (LABS→MEDBAY→WEST_HALL→ADMIN→EAST_HALL→
ENGINEERING). The crew skips; the impostor kills `p-2` on t11 and wins by parity.

### D3. The belief scalar is a hard ceiling on the LLM's conclusion — and it never learns from the discussion
Verbatim, in **3,697/3,697** recorded ballot prompts:

> Your maximum suspicion among the living ejection targets is **0.50**; the skip threshold is **0.60**
> (the §4.6 reference point). … **do not report a confidence at or above the skip threshold for a target whose
> suspicion is below it.**

The scalar it caps against is produced by a non-LLM heuristic that never reads the transcript, and it lives in
0.40–0.65 for crew subjects. So the model is instructed to cap its post-discussion conviction at its
pre-discussion prior. The consequence, measured over every crew turn that named a suspect (n = **2,351**):

| what the crewmate did between its own turn and its ballot | n | share |
|---|---:|---:|
| voted the player it accused | 1,276 | 54.3% |
| **retreated to SKIP** | 712 | 30.3% |
| … having named a **real impostor** | **243** | 10.3% |
| switched to a different player | 363 | 15.4% |
| … onto a contradiction-flag subject | 309 | 13.1% |
| … onto a flag subject who was **innocent** | 120 | 5.1% |
| … abandoning a **real impostor** to do it | **94** | 4.0% |

**At least 337 crew ballots named an actual impostor out loud and then voted somewhere else.** And when a
crewmate *does* keep its target, the ballot confidence is *lower* than its own spoken confidence 596 times
against 300 higher — the ballot stage systematically deflates conviction.

### D4. A third of the table votes with an empty head
Across 3,934 agent-meeting snapshots: the belief store carries a row for only **6,889 / 19,934 = 34.6%** of the
other living players, and **1,438 / 3,934 (36.6%) of voters enter the ballot with zero belief rows about anyone
alive**. In `4p1i` seed 29 the ballot prompt lists `p-2` and `p-4` as the only valid targets and then shows a
suspicion table with exactly one row in it (`p-4: 0.50`). Combined with D3's cap, more than a third of every
table is structurally forced to SKIP before it reads a word of the transcript.

### D5. Nothing survives a meeting — not the verdict, not the evidence, not the content of testimony
Grepped all 7,458 meeting prompts for any record of a prior ejection (`was ejected`, `EJECTED at meeting`,
`voted out at meeting`): **0 hits.** No agent in this project has ever been told who the crew ejected last
meeting, let alone that it was wrong.

Testimony survives only as a stub. `p-8`'s memory at meeting-1 of seed 17, the meeting *after* the vent
witness was ejected:

```
- [tick 7] [meeting] CLAIM by p-1 (unverified): accused p-2.
- [tick 7] [meeting] CLAIM by p-4 (unverified): saw p-1 in EAST_HALL @ tick 5 (with p-9).
- [tick 7] [meeting] CLAIM by p-4 (unverified): saw p-1 in EAST_HALL @ tick 6.
## Your current beliefs:
- p-4: suspicion 0.45
- p-5: suspicion 0.45 (last seen in LABS at tick 3; alibi: in LABS at tick 4 per p-5)
- p-6: suspicion 0.45 (last seen in LABS at tick 3; alibi: in LABS at tick 4 per p-6)
```

Three things at once. (a) The *content* of the game's strongest fact — a first-hand vent — is compressed to
`accused p-2`, while the impostor's fabricated sighting keeps its room and tick. (b) `p-2`, the accused venter,
is not in the belief table at all; its entry is the flat 0.50 prior. (c) `p-5` and `p-6`, who vouched **only for
each other**, both sit at 0.45 — *less suspicious than the man an eyewitness watched vent.*

### D6. Corroboration is repetition, not independence
Point (c) generalises. **1,723 mutual-sighting pairs** are spoken corpus-wide (1,457 crew–crew) and each side
earns its own independent alibi discount; nothing distinguishes "two people vouch for each other" from "two
people independently saw it". The same blindness at the other end produces the duplicate STRONG flag printed
twice in seed 17 m0 — one fact, rendered as two pieces of verified evidence, in the meeting that ejects the
witness.

### D7. The information budget is spent on noise
Over 1,088 rendered memory snapshots in `replays/samples/`: mean **53.2 lines**, of which

| | share of all lines |
|---|---:|
| bare co-presence / sightings | 51.7% |
| tick-0 spawn block (identical in every game ever played) | 12.5% |
| `[meeting] CLAIM` stubs | 15.6% |
| movement | 20.3% |
| **vent lines** | **0.69%** |
| **body lines** | **0.82%** |

Run-length-coalescing the co-presence rows alone (`p-4 in CAFETERIA` at ticks 1,2,3,4 → one span) removes
**37.4%** of them — about 19% of the whole block — and dropping the spawn block adds another 12.5%. **~32% of
the context is recoverable with zero information loss**, which is roughly the room every proposal below needs.

### D8. The endgame is invisible to the voter
**157 meetings** were held at `crew_alive ≤ impostors + 1`, where a SKIP hands the game away on the next kill.
**84 of them (53.5%) skipped.** The ballot prompt contains no alive-count, no parity statement, and a fixed 0.60
gate. At 3 alive / 1 impostor the correct prior on each of the two candidates is exactly 0.50, so *the gate is
unreachable by construction* — which is exactly how `4p1i` seed 29 ends:

```
p-1 -> SKIP conf=0.4  "...my suspicion of p-4 remains below the threshold."
p-2 -> SKIP conf=0.4  p-4* -> SKIP conf=0.4
[t 11] p-4*@MEDBAY:KILL  → IMPOSTOR_PARITY
```

`p-1`'s own turn had it right by elimination — *"p-4 is my primary suspect by elimination"* — and the threshold
overruled it.

---

## Part 2 — Fifteen proposals, ranked

Ranked by (measured leverage) ÷ (size × risk). "Eval risk" means: does this move the committed baselines and
force a re-record. Almost all of them do; that is a scheduling fact, not an argument against.

---

### R1 · Map-aware flag arbitration — kill the corridor artifact — **rank 1**
**What.** Before stamping `alibi_vs_sighting` STRONG, run a reachability check on the map: if
`|tick(alibi) − tick(sighting)| ≤ 1` **and** the two rooms are adjacent, the two statements are compatible with
one tick of walking — demote to `weak`, or suppress and emit `reconcilable_transit` for the spectator instead.
Same check the other way: rooms ≥2 apart at the same tick are *physically* impossible and deserve to be
promoted, not merely equal-weighted.
**Why.** D2. 148/234 (63.2%) of strong flags are adjacent-room; 130 of those name innocents; 78 of the 126
flag-driven ejections would be vetoed, 68 of them wrongful. This is the single largest measured defect in the
track and the fix is a BFS over 10 rooms.
**Expected.** Innocent-ejection rate falls hard; `alibi_vs_sighting` moves from anti-informative (17.2%
impostor subjects vs a 25.3% chance baseline) toward the `alibi_vs_physical` band. Watchability: meetings stop
convicting the one person who saw something, which is the single most alienating thing a spectator watches.
**Size** S (detector-local; the map is already loaded). **Risk** determinism none (pure function of a static
map); firewall none; **eval comparability HIGH** — changes the ejection in a large fraction of games, needs a
full re-record and a new baseline.
**Measure.** Flag precision by kind split by adjacency bucket; innocent-ejection count (79/435 today); ejections
inside the computable candidate set (293/354); crew/impostor win split; R1/R7 gauges.

### R2 · A corroborated whereabouts board, computed rather than spoken — **rank 2**
**What.** Before turn 0, build a roster × tick occupancy grid over the kill window from living players' own
recorded perception, and fill a cell **only when two living players' records agree** (A's log says it was in
MEDBAY with B; B's log says it was in MEDBAY with A). Render it as a small table plus the derived line
`unaccounted at tick 4: p-2, p-5`. Every agent can read its **own row** — which is also the root fix for the
crew self-placement bug (G-1), since today the only self-anchor in memory is a stale
`You completed X (you were in Y)` line.
**Why.** D1: the prompt already demands this object; the headroom is a unique, 94.5%-correct candidate in 17.4%
of body meetings and ≤2 candidates in 33.2%.
**Expected.** Turns stop being 8 people reciting their own logs at each other and start being about the two
names in the gap. Watchability: a spectator can see the deduction narrowing, which today is invisible.
**Size** M. **Risk** — this is the proposal with real design risk. Two-sided agreement is what keeps it honest:
a lone liar cannot fill a cell, and an impostor pair filling a cell for each other is *itself* the tell
(see R7). It must be built from recorded perception only — never from engine truth — or it becomes omniscience
and the firewall argument collapses. **Eval HIGH.**
**Measure.** Candidate-set size at eject time; fraction of ejections inside it; the 61/354 out-of-set ejections;
impostor win rate (this is a crew buff — expect it to bite).

### R3 · Let the discussion write back: replace the confidence cap with a posterior — **rank 3**
**What.** Delete *"do not report a confidence at or above the skip threshold for a target whose suspicion is
below it"*. Ask each voter for a short explicit posterior over living players and **persist it** into the belief
store as the new prior. The pre-meeting scalar becomes an input to reasoning, not a ceiling on its output.
**Why.** D3. The system currently forbids an agent from concluding more than it believed before anyone spoke.
At least 337 crew ballots named a real impostor in speech and voted elsewhere; retention of vote-time lift is
19.1%.
**Expected.** Meetings compound into a trajectory instead of resetting; the 0.65–0.90 dead band in the belief
distribution — where all circumstantial conviction lives — becomes representable.
**Size** S–M (prompt + a write-back path the store already has shape for). **Risk** determinism fine;
**eval HIGH** — ejection rate will rise and the 0.60 gate must be re-tuned in the same wave, not after.
**Measure.** Turn→ballot hold rate (54.3% today); belief retention (19.1%); the P(impostor | stated confidence)
curve, whose 0.6–0.8 band is currently *below* chance.

### R4 · Persist the meeting's own verdict — **rank 4**
**What.** Write into every survivor's memory after each meeting: `meeting 1: p-1 EJECTED 7–1; p-1 was a
CREWMATE`, `p-8's vent claim was flagged VERIFIED and stands`, `p-2 gave no whereabouts`.
**Why.** D5 — **0 of 7,458** prompts contain any such line today. A crew that cannot learn it was wrong cannot
be a crew.
**Expected.** Ends the re-litigation of closed cases (G-23: whole meetings spent on an ejected player, 68 and
232 `saw_vent` observations naming a dead subject). Gives a successful frame a real cost. Watchability: the
narrative acquires a memory — "we got it wrong last time" is the sentence this game has never once produced.
**Size** S (pure rendering). **Risk** none to determinism or firewall; **eval MED** (re-record).
**Measure.** Rate of accusations naming dead/ejected players; accuracy at meeting *k*>0 vs meeting 0.

### R5 · Testimony as citable content, not a stub — **rank 5**
**What.** `CLAIM by p-1 (unverified): accused p-2` → `[tst m0:p-1:2] p-1 testified: witnessed p-2 VENT in
ENGINEERING @6 — unverified, corroborated by 0 others`, with an id a later ballot may cite the way it cites
`[obs …]` today.
**Why.** D5. The content of the game's only 100%-precise signal is destroyed on the way into memory while the
impostor's fabricated *sighting* keeps room and tick. 24.5% of memory lines carry no citable id at all.
**Expected.** Second-hand evidence becomes usable — and, for the first time, *measurable*: "testimony decided
this vote" is currently unfalsifiable.
**Size** S. **Risk** low; **eval MED**.
**Measure.** Share of ballots citing a testimony id; survival of a vent claim across meetings.

### R6 · Make the roll-call adversarial and render absence — **rank 6**
**What.** Two halves that must ship together. (a) Require *every* turn, impostor included, to carry exactly one
`whereabouts` (today crew 99.6% vs impostor 49.0%; `P(impostor | no whereabouts) = 97.7–100%`). (b) Render the
negative space: `no living player has placed p-2 anywhere between ticks 4 and 6`, `p-2 gave no account of
itself`.
**Why.** D3's exemplar — `p-8` spotted "p-2 has provided no alibi for tick 6" unaided and it was worth nothing,
because absence renders nowhere. And today answering the roll-call is *net negative* for a crewmate: it is what
creates the one-tick window that mints 80% of the below-chance flags, while silence is free.
**Expected.** The alibi channel becomes a contest between a liar and a checker instead of a crew self-harm
device. Watchability: an impostor forced to place itself is the genre's central drama, and it is missing.
**Size** S (prompt + render). **Risk** balance — (a) alone nerfs the impostor, (b) alone nerfs it further; ship
as a pair and expect to re-tune. **Eval HIGH.**
**Measure.** Impostor share of `alibi_vs_sighting` subjects (17.2% today, 25.3% chance); impostor win rate;
turns carrying a whereabouts by role.

### R7 · Corroboration algebra: count sources, not sentences — **rank 7**
**What.** (a) De-duplicate the flag block (seed 17 m0 prints the same sentence twice into the meeting that
ejects the witness). (b) Collapse mutual-only vouches into one line — `p-5 and p-6 vouch only for each other` —
and give the pair one discount, not two. (c) Require ≥2 *independent* sources (not co-located, not each other)
before a cross-statement flag is stamped STRONG.
**Why.** D6; 1,723 mutual pairs; and (c) is what converges `alibi_vs_sighting` on the rule
`alibi_vs_physical` already uses at ~100% precision.
**Expected.** The single loudest voice stops outweighing the table. Watchability: "who else saw it" becomes a
question worth asking, which is what a real deduction table sounds like.
**Size** M. **Risk** low determinism; **eval HIGH** (interacts with R1 — measure them in one wave, not two).
**Measure.** Precision by (flag kind × source count); the sole-flag conviction rate (12 right / 70 wrong today).

### R8 · Coalesce perception into spans; drop the spawn block — **rank 8**
**What.** `You saw p-4 task in CAFETERIA (with p-7, p-9)` × ticks 1,2,3,4 → `t1–t4 with p-4, p-7, p-9 in
CAFETERIA`. Drop the tick-0 lobby block when it is the full roster. Drop the duplicate
`[tick 1] p-2 left CAFETERIA` rows that restate an adjacent `You saw p-2 move from CAFETERIA to EAST_HALL`.
**Why.** D7: 32% of the block is recoverable at zero information loss, and today 365/456 budget-pressure
transitions shed *testimony* while keeping 8 constant lobby lines.
**Expected.** No direct gameplay effect; it is the enabler that pays for R2's grid and R4/R5's persistent lines.
Watchability: the "as-agent" fog view in the viewer becomes readable.
**Size** S. **Risk** determinism none; **eval MED** (memory text is pinned in fixtures).
**Measure.** Lines per snapshot (53.2 today); share of hard-evidence lines (1.5%); testimony-shed rate.

### R9 · A mandatory alternative-hypothesis field on every accusation — **rank 9**
**What.** Add one required key to the `accusation` claim: `alternative` — the most plausible *innocent*
explanation for the same evidence, and one clause on why it is rejected. Reject the accusation if the field is
empty or restates the accusation.
**Why.** The cheapest reasoning intervention available. In seed 17 it forces `p-8` to write "or p-1 walked
EAST_HALL→ENGINEERING between the two ticks" — the true answer — before it can convict. It is the theory-of-mind
step the pipeline never asks for, at the cost of one sentence and zero extra LLM calls.
**Expected.** Directly attacks the 0.6–0.8 confidence band that is currently below chance. Watchability: the
transcript stops sounding like eight people each reciting one fact.
**Size** S. **Risk** output-cap pressure (turns already truncate); **eval MED**.
**Measure.** P(impostor | stated confidence) by band; overconfidence (+0.068 today); the flag-switch rate
(309/2,351).

### R10 · Give the accused a rebuttal turn — **rank 10**
**What.** After the opt-in round, whoever the plurality of accusations names gets one final turn **with the
contradiction flags visible**, and may cite a specific flag as reconcilable.
**Why.** 553/1,542 accusations (73%) are never answered; 55% are made in opt-in turns that by design cannot be
answered; the reactive chain is one reply long in 126/165 and 341/463 meetings. In seed 17 `p-1` never gets to
say "those rooms are adjacent, I walked".
**Expected.** Directly converts R1's mechanical veto into a *spoken* one, which is far better television.
**Size** S–M (protocol + one extra LLM call per meeting). **Risk** cost pins and the recorded-call counts;
**eval HIGH**.
**Measure.** Reversal rate (leader at rebuttal vs ejected); innocent-ejection rate; accusations answered.

### R11 · Endgame awareness and a gate that scales with the table — **rank 11**
**What.** Render in the ballot prompt: `4 alive, at least 1 impostor still here — if this meeting skips, one
more kill ends the game`, and scale the skip threshold with the candidate count (e.g.
`1/(n_living − 1) + margin`) instead of a fixed 0.60.
**Why.** D8: 84/157 parity−1 meetings skipped; at 3-alive the 0.60 gate is mathematically unreachable.
**Expected.** Turns a large block of free impostor wins into genuine coin-flips. Watchability: last meetings
become tense instead of pro-forma.
**Size** S. **Risk** **balance HIGH** — this is a deliberate crew buff and will move the win split on its own;
run it as a single-variable arm. **Eval HIGH.**
**Measure.** Skip rate at parity−1 (53.5%); win split by reason; ejection accuracy at ≤4 alive.

### R12 · Publish a map card in every meeting prompt — **rank 12**
**What.** Room list, adjacency, travel ticks, and which rooms are dead ends, in the meeting prompts. The
agent-side half of R1.
**Why.** 0/7,458 prompts carry it; `4p1i` seed 29's meeting is decided by an unfalsifiable geometry bluff.
**Expected.** Agents can compute reconcilability themselves and can call out an impossible claim; the impostor's
"you crossed the station too fast" deflection stops working for free.
**Size** S. **Risk** context budget (pay for it with R8); **eval MED**.
**Measure.** Geometric-impossibility claims spoken and their accuracy; reconciled-transit mentions.

### R13 · `saw_kill` observation + a `kill_sighting` flag ranked above every alibi flag — **rank 13**
**What.** Add the missing observation shape and the missing contradiction kind. `You witnessed pN kill in ROOM`
is 0.02% of rendered lines and reaches peers as a +0.08 nudge.
**Why.** G-8. `4p1i` seed 22: `p-3` watched `p-4` kill, opened at confidence 1.0, no flag fired, the meeting
skipped, the crew lost.
**Expected.** The genre's other hard proof becomes as usable as the vent. Watchability: the eyewitness stops
being ignored.
**Size** M (schema + detector + prompt). **Risk** low determinism; **eval MED** (rare event — expect a small
absolute effect and a large believability one).
**Measure.** Conversion of witnessed kills to a correct ejection (near 0% today via the flag path).

### R14 · Spend LLM calls where they change the answer — **rank 14**
**What.** All 707/707 meetings are exactly `#turns == #ballots == #living` regardless of who holds anything, and
36.6% of voters have an empty belief table. Budget calls per meeting instead: an agent holding hard evidence
gets a turn *and* a rebuttal; an agent with nothing gets a templated "nothing to add" and a deterministic
abstain. Reinvest the savings in R10's rebuttal and a second pass over the two leading candidates.
**Why.** Same cost, denser deliberation. The "opt-in eligibility" gate exists and never excludes anybody.
**Expected.** Removes the filler turns that make the transcript feel like a round-robin in a debate costume.
**Size** M. **Risk** call counts, cost pins and recorded-prompt tests all move; **eval HIGH**. Do NOT let this
silence agents wholesale — 99.6–99.9% living participation is what makes the transcript readable; this is
reallocation, not censorship.
**Measure.** Cost per meeting; accusations answered; decision accuracy per dollar; filler-turn share.

### R15 · A reasoning scoreboard as a first-class eval — **rank 15 by leverage, but do it FIRST**
**What.** Five per-meeting metrics on the dashboard, all computable offline from existing replays (I computed
all five in one session): (a) computable-candidate-set size and whether the ejection landed inside it;
(b) turn→ballot hold rate; (c) flag precision by kind × source-count × adjacency bucket; (d) belief retention
across meetings; (e) count of "named an impostor in speech, voted elsewhere".
**Why.** Every finding in Part 1 moved one of these five, and **none of them is currently measured**. The
existing gauges measure outcomes, so a change that improves reasoning but not yet the win split reads as noise.
**Expected.** No gameplay effect at all. It is what makes R1–R14 falsifiable instead of a matter of taste.
**Size** M. **Risk** zero — read-only, no replay change, no re-record.
**Measure.** Itself.

**Suggested wave order [JUDGMENT].** R15 first (free, and it is the instrument). Then one substrate wave —
R1 + R7 + R8 + R4 + R5 — which is all rendering/detector and no balance lever, measured against the new
scoreboard. Then one balance wave — R6 + R11 + R2 — each as a single-variable arm, because each is a deliberate
crew buff and shipping them together makes the result uninterpretable. R9/R10/R12/R13/R14 fold into either wave
as capacity allows.

---

## Part 3 — Three things I would NOT change

### N1. Crew same-room-only visibility (Task 13.8)
It is the forcing function that makes deduction necessary at all; restoring adjacent-room *player* vision would
hand the crew the answer and collapse everything above into bookkeeping. The genuinely absurd symptom — crew
walking past corpses they cannot see, 41% of kills one doorway from a blind crewmate — is fixed by the narrow
carve-out already proposed elsewhere in the track (adjacent-room **bodies** only, never players). And the
side-effect people flag as a bug — impostors having the most accurate testimony at the table — is good fiction:
the killer *does* know where everyone was. The defect is not that the impostor knows; it is that R1 and R6 do
not yet make it costly to say so.

### N2. The `vent_sighting` channel, the citation discipline, and the deterministic tally
440/440 precision, 96.7–97.1% of held vents convert to the right ejection, 0 dangling observation or turn ids
across 3,814 ballots, 0 self-votes, 0 dead targets, and the teammate firewall is 0/929. This is the part of the
system that works, and every proposal above is an argument for making *other* channels look more like it — not
for touching it. Specifically: do not "improve" the vent flag by softening it, and do not replace the
deterministic tally with an LLM adjudicator. Determinism is why any of this is measurable.

### N3. Do not reach for a bigger model
Every defect I measured is in the substrate, not the reasoner. In seed 17 the model spotted the right suspect
(`p-8`, "p-2 has provided no alibi for tick 6"), constructed the correct case, and was then overruled by
(a) a label that promised a verification the detector never performed, and (b) an instruction not to exceed a
scalar computed before anyone spoke. A stronger model reading the same prompt convicts `p-1` too — more
fluently. The corollary: do not answer this with more free-text scaffolding either. The prompts already carry
`§4.6` and a threshold arithmetic block into the characters' mouths ("the 0.60 threshold" is spoken 208 times
corpus-wide); the fix is to give the agents better *objects* to reason over — a map, a grid, a verdict history,
an honest label — not longer instructions about how to reason.

---

## Appendix — method and reproduction

All scripts read-only, run as `AILIBI_PROMPT_SET=qwen3_6_27b uv run
python <script>`, under `scratchpad/work/ideas-mar/`:

| script | produces |
|---|---|
| `probe.py` | deduction oracle (626 body meetings), turn→ballot defection (2,351 crew turns), fatal-skip census (157 meetings), belief sparsity (3,934 snapshots), mutual-alibi pairs, ballot-vs-turn confidence |
| `probe2.py` | map adjacency from `v.map.edges`; all 234 strong + 78 weak `alibi_vs_sighting` flags bucketed by BFS distance, window width, subject role, ejection outcome |
| `probe3.py` | rendered-memory composition and span-coalescing savings over 1,088 snapshots |
| `probe4.py` | in-room / unplaced split; running cross-meeting candidate tally |
| inline `json`/`re` pass over `llm_calls` | prompt-text census over 7,458 meeting calls (singular-impostor line, confidence-cap clause, `§4.6`, adjacency, prior-ejection records) |

Game dumps: `s17.txt`, `s2.txt`, `4p29.txt`, `s17-mem-p8.txt` in the same directory.
