# Phase 21 — the offline counterfactual: the Wave-2 levers over the re-recorded bytes

**Status: this memo writes NO bar, NO target and NO decision rule.** It precedes the
pre-registration in the DAG on purpose, and a memo that published predicted values and then
proposed bars would be setting a bar to a number it had already seen. What follows is
measurements and predictions, offered for `audits/audit-phase-21-preregistration.md` and its
owner to read, convert, decline or replace. Every number here is recomputed on the baseline-8
bytes by `scripts/counterfactual_phase21.py`; where a figure from the 2026-08-26 review register
is quoted, it is labelled prior-record CONTEXT and is never the published cell.

**Date:** 2026-09-01. **Instrument:** `uv run python scripts/counterfactual_phase21.py --sets all`
(28.7 s over 300 games, `$0`, no network, no model call, no replay written, no `os.environ`
assignment). **Substrate:** baseline 8, the four committed sets under `replays/`, with all four
live toggles OFF — the substrate every one of those recordings stamps.

---

## §0 The one sentence this memo leads with

**A sentence added to a prompt is not a vote that changes.**

Task 20.34 wrote "a flag that stops being minted is not a vote that changes". The Phase-21 form
is stronger, and it is the reason this memo's honest column is narrower than the Phase-20
counterfactual's. That slate was five render levers and three DETECTOR levers, so a large part of
its table was flags that stop being minted — a pure function of recorded testimony and each
speaker's own records, computable to the digit. **The Wave-2 slate mints no flag.** Threading the
reporter's identity into the accusation round changes what the model READS; whether an accuser
then withholds an accusation is a fact about the model, not about the bytes.

So the honest offline column for these levers is the RENDERED SURFACE and the EXPOSED POPULATION:
how many prompts gain a block, in how many meetings, at what cost against the render budget, over
how many recorded cases of the shape the lever re-renders. Everything downstream of new model
behaviour is named in §7 with its reason, and the reporter-conviction count is the first name on
that list.

That is not a weak instrument, because the render-side predictions are falsifiable EARLY. Every
ON-column render cell below is checkable on the Wave-2 smoke's first ON seed without spending the
record: if this memo says the reporter block renders in every non-reporter speech turn of a
body-report meeting and the smoke's ON seed renders it in none, the lever did not thread and the
record must not start. §9 offers the sharpest of those as tripwire candidates.

---

## §1 How to read every row

### 1.1 The three columns

| column | what it is |
|---|---|
| **RECORDED-OFF** | a committed instrument reading the committed bytes: `eval.reporter_justice`, `eval.evidence_honesty`, `eval.solvability`, and each set's `tournament-eval-report.json`. This IS the record's own substrate. |
| **RECONSTRUCTED-OFF** | the same cell folded from the re-derived inputs of ONE reconstruction walk with the whole slate OFF. |
| **ON** | a SECOND RENDER of the same rebuilt memory and the same recorded meeting inputs with the lever's own argument supplied. |

A cell whose two OFF readings disagree prints no ON value at all: the counterfactual would be
measuring the reconstruction, not the lever. The withdrawal is per CELL and reaches the pooled row
too — pooling the sets that did reproduce would publish a row over a silently reduced denominator,
which is the opposite of what the refusal is for. **No cell in this memo disagrees on any set, and
no pooled ON column is withdrawn.** Where a row shows only one OFF column, the other has no
producer — an instrument cell has no reconstruction twin, and a render cell has no committed
instrument. That is a property of the cell, not a gap.

### 1.2 The ON column is a RENDER DIFF and is never re-driven

The reconstruction drives the real `MeetingManager` against a recorded-response stub keyed on
EXACT prompt bytes. A lever-ON prompt therefore misses every recorded response and fail-softs the
whole meeting into a defaulted transcript, defaulted ballots, a diverged outcome and fictional
memory from meeting 1 onward. Every ON cell here is a second render of the OFF inputs, compared
line for line. Nothing is fed back.

### 1.3 The reading rules

1. **Exposure is an upper bound, never a predicted flip.** A case a lever touches is not a case
   the lever fixes. No row of this memo subtracts an exposure count from an injustice count, and
   none may be read as though it did.
2. **The ledger's tags split into two kinds and both are labelled.** The structural tags are exact
   joins over recorded fields and reproduce digit for digit. The impossible-transit tag (C-8, PIT)
   is a regex over ballot prose and is a JUDGMENT NET wherever it appears — the Wave-0 verifier's
   ruling, executed: two independently written classifiers agreed on the total while disagreeing
   on two rows that cancelled, and the net over-triggers on true statements about venting. The
   regex is committed in the script and every tagged row is listed in §2.3 so a reader can
   re-judge it.
3. **`[ADV]` marks a cell one case would dominate, and it is keyed on the CELL's own denominator**
   — any column measured over 20 or fewer cases — not on the size of the set it sits in. A cell
   read over three turns is fragile inside a 439-meeting set, and labelling by the set would hide
   exactly that. Every marked cell is printed at its recorded denominator and takes no part in any
   directional statement. The two 4p1i sets carry the most of them by far (`samples/4p1i` had 4
   innocent ejections and `ml_corpus/4p1i` had 0), but T-4 and T-8 are marked in every set.
4. **Every testimony-shapes ingest and render cell is a ONE-STEP-AHEAD reading.** Meeting 1's ON
   render is derivable from meeting 1's recorded inputs; meeting 2's ON transcript is a model
   output that does not exist. T-1 through T-7b, T-9 and T-10 are therefore read at each RECORDED
   meeting boundary against RECORDED speech and compound nowhere. §7 names the compounding effect
   as its own un-reachable cell.
5. **The register's figures are prior-record CONTEXT.** Every A-4 / A-5 / A-10 / A-24 / A-38
   figure was measured on baseline-7 bytes that no longer exist. Where a corrected form exists,
   only the corrected form is quoted.

### 1.4 What moved since the register, stated before anything is read

| register figure (baseline 7) | this memo (baseline 8) |
|---|---|
| 42 innocent ejections | **46** |
| 618 body-report meetings of 668 | **620 of 672** (52 emergency) |
| reporter class 30 of 42 = 71% | **34 of 46 = 73.9%** |
| relative risk 7.46x | **8.50x** |
| co-discoverer impostor share 51 of 140 = 36.4% | **71 of 145 = 49.0%** |
| weak-flag class 5 | **8** (the committed pins moved 3 → 5 and 2 → 3) |
| sole-flag wrongful-conviction class 0 | **4**, with one STRONG statement-pair conviction beside it |
| A-24's adverse ballot-side regression, 9.6% crew / 17.1% impostor | **6.5% crew / 12.0% impostor**, both DOWN |

The last row matters for how the reporter lever is argued. A-24's headline was that the
BALLOT-side aim at the reporter had regressed; on baseline 8 both halves are lower than the
figures the register flagged. The memo states the direction on its own bytes and does not repeat
the register's.

---

## §2 The population: the injustice ledger at baseline 8

A-10 is a per-case classification of every innocent ejection in the record, and its verifier said
what it is for: "an acceptance-test artifact ... it should be scheduled with the levers it
scores". This memo recomputes it on the re-recorded bytes and joins each lever's exposure onto it.

### 2.1 The class totals

46 innocent ejections, all of them inside the non-direct cell (the proof-present cell is
innocent-free, 0 of 333).

| class | tag | count of 46 | what it is |
|---|---|---|---|
| reporter-convicted | RC | **34** | the ejectee is the body-report meeting's own reporter |
| counter-accusation boomerang | BOOM | **33** | the turn-1 reply accuses the turn-0 speaker AND the ejectee IS that speaker |
| impostor rides the herd | IMP-RIDES | **36** | a living impostor voted for the ejectee |
| forced endgame | ENDGAME | **12** | three or fewer ballots were cast |
| weak-flag only | WEAKFLAG | **8** | every contradiction naming the ejectee is a detector-flagged WEAK signal |
| guard-redirected | REDIRECT | **3** | a convicting ballot carries the structured guard-rewrite provenance |
| impossible transit | PIT | **20** | **JUDGMENT NET** — a convicting ballot asserts a physical impossibility about a player who could not have performed one |

RC is cross-checked against `eval.reporter_justice`'s own `reporter_innocent_ejections` (34) and
WEAKFLAG against the committed weak-flag conviction cell (5 + 3 = 8); the script refuses to
publish if either disagrees. The REDIRECT tag reads the structured `guard_rewrite_reason`
provenance field, never a marker string.

### 2.2 What is left when the classes are stripped

Six of the 46 carry nothing beyond the generic herd, and none of the six carries even the judgment
tag:

`samples/9p2i` 21:m2 p-1 · `samples/9p2i` 41:m2 p-9 · `ml_corpus/9p2i` 1036:m3 p-9 ·
`ml_corpus/9p2i` 1066:m3 p-3 · `ml_corpus/9p2i` 1106:m3 p-1 — all IMP-RIDES only — and
**`ml_corpus/9p2i` 1091:m1 p-9, which carries no tag at all.** That single row is the whole
baseline-8 "no alibi, last suspect standing" set. It is the one case in the record this ledger
offers no account of, and it is named rather than absorbed.

### 2.3 Every tagged row, so PIT can be re-judged

The judgment tag is listed with the rest so a reader can disagree with the net rather than with a
summary of it. Set / seed / meeting / ejectee / tags / recorded tally.

| set | seed | meeting | ejectee | tags | tally |
|---|---|---|---|---|---|
| samples/9p2i | 1 | m1 | p-5 | WEAKFLAG+REDIRECT | p-5 3, SKIP 2, p-1 1 |
| samples/9p2i | 1 | m3 | p-8 | RC+BOOM+PIT+IMP-RIDES+ENDGAME | p-8 2, p-7 1 |
| samples/9p2i | 4 | m3 | p-7 | RC+BOOM+PIT+IMP-RIDES+WEAKFLAG+ENDGAME | p-7 2, SKIP 1 |
| samples/9p2i | 6 | m2 | p-1 | RC+BOOM | SKIP 2, p-1 3 |
| samples/9p2i | 12 | m0 | p-5 | PIT+IMP-RIDES+WEAKFLAG+REDIRECT | p-5 5, SKIP 1, p-2 1 |
| samples/9p2i | 19 | m3 | p-1 | RC+BOOM+PIT+IMP-RIDES | p-9 1, p-1 4 |
| samples/9p2i | 21 | m2 | p-1 | IMP-RIDES | SKIP 2, p-1 3 |
| samples/9p2i | 26 | m3 | p-7 | RC+BOOM+PIT+IMP-RIDES+ENDGAME | p-7 2, SKIP 1 |
| samples/9p2i | 27 | m2 | p-2 | RC+BOOM | SKIP 2, p-2 3 |
| samples/9p2i | 38 | m0 | p-8 | PIT+IMP-RIDES+WEAKFLAG | p-8 7, p-4 1 |
| samples/9p2i | 41 | m2 | p-9 | IMP-RIDES | p-9 4, SKIP 1 |
| samples/9p2i | 46 | m3 | p-1 | RC+BOOM+PIT+IMP-RIDES | SKIP 1, p-1 3 |
| samples/9p2i | 48 | m2 | p-2 | PIT+IMP-RIDES+WEAKFLAG | SKIP 1, p-2 3 |
| ml_corpus/9p2i | 1002 | m2 | p-2 | RC+BOOM+PIT+IMP-RIDES | SKIP 1, p-2 3 |
| ml_corpus/9p2i | 1022 | m4 | p-5 | RC+BOOM+PIT+IMP-RIDES+ENDGAME | p-5 2, SKIP 1 |
| ml_corpus/9p2i | 1032 | m2 | p-4 | RC+BOOM+PIT+IMP-RIDES+WEAKFLAG+ENDGAME | p-4 2, SKIP 1 |
| ml_corpus/9p2i | 1036 | m3 | p-9 | IMP-RIDES | p-9 3, SKIP 1 |
| ml_corpus/9p2i | 1038 | m1 | p-1 | RC+BOOM+PIT+IMP-RIDES | SKIP 2, p-1 3 |
| ml_corpus/9p2i | 1045 | m2 | p-1 | RC+BOOM+IMP-RIDES | p-3 1, p-1 4 |
| ml_corpus/9p2i | 1049 | m0 | p-1 | RC+BOOM+PIT+IMP-RIDES | p-7 1, p-1 5, SKIP 1 |
| ml_corpus/9p2i | 1050 | m1 | p-1 | RC+BOOM+PIT+IMP-RIDES | p-9 1, p-1 3, SKIP 1 |
| ml_corpus/9p2i | 1053 | m1 | p-6 | RC+BOOM+IMP-RIDES | p-6 3, SKIP 2 |
| ml_corpus/9p2i | 1054 | m4 | p-7 | RC+BOOM+PIT+IMP-RIDES+ENDGAME | p-7 2, SKIP 1 |
| ml_corpus/9p2i | 1062 | m2 | p-1 | RC+BOOM+PIT+IMP-RIDES | p-9 1, p-1 4 |
| ml_corpus/9p2i | 1063 | m1 | p-4 | RC+BOOM | p-4 3, p-2 1, SKIP 1 |
| ml_corpus/9p2i | 1065 | m2 | p-6 | RC+BOOM+IMP-RIDES+ENDGAME | p-6 2, SKIP 1 |
| ml_corpus/9p2i | 1066 | m3 | p-3 | IMP-RIDES | p-3 4, SKIP 1 |
| ml_corpus/9p2i | 1074 | m1 | p-7 | IMP-RIDES+WEAKFLAG+REDIRECT | SKIP 2, p-7 4 |
| ml_corpus/9p2i | 1074 | m2 | p-2 | RC+BOOM | SKIP 1, p-9 1, p-2 2 |
| ml_corpus/9p2i | 1082 | m1 | p-1 | RC+BOOM | SKIP 2, p-1 3 |
| ml_corpus/9p2i | 1091 | m1 | p-9 | (none) | p-9 3, SKIP 2, p-5 1 |
| ml_corpus/9p2i | 1095 | m0 | p-1 | RC+BOOM+PIT | SKIP 3, p-1 4 |
| ml_corpus/9p2i | 1097 | m1 | p-4 | IMP-RIDES+WEAKFLAG | p-4 6, SKIP 1 |
| ml_corpus/9p2i | 1105 | m2 | p-1 | RC+BOOM | SKIP 2, p-1 3 |
| ml_corpus/9p2i | 1106 | m3 | p-1 | IMP-RIDES | SKIP 1, p-1 3 |
| ml_corpus/9p2i | 1111 | m0 | p-2 | RC+BOOM+PIT+IMP-RIDES | p-2 6, SKIP 2 |
| ml_corpus/9p2i | 1114 | m4 | p-7 | RC+BOOM+IMP-RIDES+ENDGAME | p-7 2, SKIP 1 |
| ml_corpus/9p2i | 1116 | m2 | p-1 | RC+BOOM+IMP-RIDES | SKIP 1, p-1 3 |
| ml_corpus/9p2i | 1121 | m1 | p-2 | RC+BOOM+IMP-RIDES | p-2 4, SKIP 2 |
| ml_corpus/9p2i | 1126 | m2 | p-1 | RC+BOOM | SKIP 2, p-1 4 |
| ml_corpus/9p2i | 1132 | m2 | p-1 | RC+IMP-RIDES | SKIP 2, p-1 3 |
| ml_corpus/9p2i | 1144 | m2 | p-1 | RC+BOOM+IMP-RIDES | SKIP 1, p-1 5 |
| samples/4p1i | 16 | m0 | p-2 | RC+BOOM+IMP-RIDES+ENDGAME | p-2 2, SKIP 1 |
| samples/4p1i | 27 | m0 | p-3 | RC+BOOM+PIT+IMP-RIDES+ENDGAME | p-3 2, SKIP 1 |
| samples/4p1i | 29 | m0 | p-1 | RC+BOOM+IMP-RIDES+ENDGAME | SKIP 1, p-1 2 |
| samples/4p1i | 39 | m0 | p-2 | RC+BOOM+PIT+IMP-RIDES+ENDGAME | p-2 2, SKIP 1 |

`ml_corpus/4p1i` contributes no row: it ejected no innocent at baseline 8.

### 2.4 The overlap is a join, not three censuses

The three levers reach the same meetings by construction — the reporter class, the hearsay class
and the testimony class all sit inside this one ledger — so their exposures are NOT additive. On
the 46 rows: **BOOM is a strict subset of RC** (all 33 boomerangs eject the reporter), RC and
IMP-RIDES overlap in 26, all three overlap in 25, and their union is 44 of 46 — the two rows
outside it are `samples/9p2i` 1:m1 p-5 and `ml_corpus/9p2i` 1091:m1 p-9. PIT overlaps RC in 17.
§8 states each lever's exposure against the ledger and then states the join, never a sum.

---

## §3 The reporter lever (`reporter_reasoning`)

### 3.1 The headline

**The class the lever aims at is 34 of the record's 46 innocent ejections (73.9%), and the lever's
rendered surface reaches every one of the meetings that produced them: 620 of 620 reporter
openings and 2,715 of 2,715 non-reporter speech turns in a body-report meeting.** Exposure is
100% of the class; effect is unknown and is named in §7.

### 3.2 The baseline

The reporter is the only seat the meeting hands a structural disadvantage, and the numbers say how
much. 620 of 672 meetings were opened by a body report; the reporter was a CREWMATE in 620 of 620,
so the exculpation is not a laundering channel on these bytes. Per slot, a reporter was ejected
34 of 620 times (5.48%) against an innocent non-reporter's 12 of 1,859 (0.65%) — **a relative risk
of 8.50x**. Aim at the reporter is standing rather than new: 521 of 2,129 crew speech accusations
and 520 of 739 impostor ones name the reporter, while the ballot half reads 160 of 2,479 crew and
103 of 856 impostor.

The exculpation is rendered on every body-report ballot and is almost never ARGUED: 82 of 3,335
ballot rationales mention a report at all and 13 carry an exculpatory hinge (an upper bound — the
instrument's hinge list is stated, and a hand read of the Wave-0 hits found roughly two thirds to
three quarters genuine). One reporter invokes it in speech.

### 3.3 The render census, per prompt class

| prompt class | rendered | gains the block | lines added | bytes added |
|---|---|---|---|---|
| reporter opening (`crewmate_report`) | 672 | **620** | +620 | +171,222 |
| non-reporter speech turn (`accusation_round`) | 2,959 | **2,715** | +11,005 | +1,026,970 |
| ballot (`vote_ballot`) | 3,631 | **0** | 0 | 0 |

Per body-report meeting, for the smoke to join on: **exactly 1 reporter opening and 4.38 mean
non-reporter speech turns (2,715 over 620 meetings) gain a block; 0 ballots do.**

The zeros are as load-bearing as the totals. The 52 openings and 244 speech turns that do NOT gain
the block are the emergency meetings, which have no reporter; the 3,631 ballots gain nothing
because the 15.5 exculpation already renders there, unconditionally, on every body report. **R-15
is an exact-zero cell in both columns and is offered as a tripwire in §9.**

The per-speaker `at_body` line — one neutral self-addressed sentence for a speaker whose own
record places them at the body when the meeting opened — rides the same seam and never fires for
the reporter, whose discovery IS the report.

### 3.4 The over-damping exposure, printed beside every co-discoverer row

A-38's proposed widening (extend the exculpatory framing to non-reporter co-discoverers) was
rejected on measurement, and the measurement got WORSE at the re-record. 118 of 620 body-report
meetings carry a non-reporter holding the same discovery; those meetings hold 145 co-discoverer
slots, and **71 of them — 49.0% — are IMPOSTORS.** The register's "51 of 140 = 36.4%" was measured
before `MeetingTrigger.body_victim_id` corrected a tick-match that counted speakers who found a
DIFFERENT corpse; it is superseded and is not quoted here. Extending exculpatory framing beyond
the report action hands it to an impostor in half of cases, not a third.

---

## §4 The corroboration lever (`corroboration_discipline`)

### 4.1 The headline

**The block renders on 3,614 of 3,631 ballots — 99.5% — and what it would tell those voters is
that 475 of 1,525 accused subjects in the record have no first-hand source behind the charge
against them.** The 17 ballots that gain nothing are meetings whose ledger has no row for any of
that voter's candidate targets.

### 4.2 The four ledger cells

These four are FIRST asserted here. Task 21.19 shipped a walk that prints them and deliberately
asserts no figure; this script pins them against the values the #415 merge-reality and #417
amendment records published, and refuses to print an ON number if the walk disagrees.

| cell | reading | what it means |
|---|---|---|
| accused subjects with no first-hand source | **475 / 1,525** | 31.1% of every charge at every table is carried by voices that added nothing they saw |
| ejected subjects with no first-hand source | **11 / 425** | of the ejections that carry a ledger row at all |
| ejections whose charge ANSWERED the ejectee's own | **33 / 429** | an answer to a charge is not a second witness |
| ejected subjects with a map-satisfied placement pair | **48 / 429** | two spoken placements one tick of walking reconciles |

### 4.3 The ejecting-ballot census over the injustice ledger

150 ballots ejected those 46 innocents. Their citation channel:

| channel | count of 150 | definition |
|---|---|---|
| hearsay | **89** | `primary_reason_id` names another speaker's turn |
| own observation | **37** | `primary_reason_observation_id` names a row from the voter's own memory |
| own turn | **23** | `primary_reason_id` names the voter's own turn |
| another player's observation | **0** | expected empty; the manager's normalizer nulls it |
| nothing | **1** | expected near-empty; the citation gate coerces an uncited eject to SKIP |

The sole-source chain: in every one of the 46 cases some other speaker's turn is the modal
citation, and that speaker is a **CREWMATE in 36 and an IMPOSTOR in 10**. Follower counts on that
one source — CREWMATE `{1: 13, 2: 14, 3: 7, 4: 1, 6: 1}`, IMPOSTOR `{1: 6, 2: 1, 3: 2, 4: 1}`. Of
the 53 impostor ballots cast in these meetings, 40 named the ejected innocent: the impostors pile
on, but they are not the originators in 36 of 46 cases.

Stated confidence, split by flag status, is the cell an anchoring rule would be aimed at and it is
flat: mean 0.8009 across the 9 ejections where a contradiction named the ejectee, and 0.8047
across the 37 where none did. **A flagless conviction is stated at the same confidence as a
flagged one.** Whether the block moves that number is a fact about the model and is in §7.

The impossibility-charge population is 20 of the 46 (C-8) — **a judgment net**, listed row by row
in §2.3.

### 4.4 The render census

| prompt class | rendered | gains the block | lines added | bytes added |
|---|---|---|---|---|
| ballot (`vote_ballot`) | 3,631 | **3,614** | +28,432 | +3,970,615 |
| reporter opening | 672 | 0 | 0 | 0 |
| speech turn | 2,959 | 0 | 0 | 0 |

Per meeting, for the smoke to join on: **5.38 mean ballots per meeting gain the block (3,614 over
672 meetings), 0 openings and 0 speech turns do**, and the block itself is 7.87 mean lines per
ballot it reaches.

The lever writes to exactly one seam. Its 28,432 added lines are 63% of the whole slate's added
prose, and §6 prices what that costs.

---

## §5 The testimony lever (`testimony_shapes`)

### 5.1 The headline

**4,763 spoken statements per record — 3,157 whereabouts self-placements and 1,606 movement
sightings — are dropped whole by the meeting reduction and reach no listener's memory, and the
lever's widened ingest takes the alibi map from 1,016 of 4,173 location accounts (24.35%) to
4,173 of 4,173 (100%).** Both readings are ONE STEP AHEAD at each recorded boundary.

### 5.2 The reduction census, by kind

| kind | OFF | ON | lever-gated |
|---|---|---|---|
| `saw_player` | 3,880 | 3,880 | no |
| `saw_vent` | 512 | 512 | no |
| `alibi` | 1,016 | 1,016 | no |
| `accusation` | 3,114 | 3,114 | no |
| `corroboration` | 1,412 | 1,412 | no |
| `whereabouts` | **0** | **3,157** | yes |
| `saw_move` | **0** | **1,606** | yes |
| `saw_kill` | **0** | **0** | yes |
| total | 9,934 | 14,697 | |

`saw_kill` is zero in BOTH columns and the reason is the point: before #416 no such shape existed
anywhere in the repo, so nobody could speak one, and the recorded transcripts contain none to
reduce. **The strongest testimony the game produces has no structured form on the committed
bytes.** The ON column here is not a prediction that crew will speak kills; it is the observation
that the shape has no history to read.

The verifier's note that `completed_task` and `found_body` fall through the same reduction still
stands. Both stay OUT of the Wave-2 slate and are not priced here.

### 5.3 The ingest, at each recorded boundary

At the 672 recorded meeting boundaries the reduction's statements are folded into every living
listener's episodic store. OFF that is 49,667 rows; ON it is 73,218 — **+23,551 rows**, an UPPER
BOUND: the own-statement guard is applied and the per-listener roster gate is not, because that
gate needs each listener's episodic store and the reconstruction does not expose one. The gate
drops only ids a listener never witnessed, and every id here is a co-spawned roster player, so the
bound is expected tight; it is still printed as a bound.

The alibi-map cell is the exactly-computable one. The map is fed by `alibi` statements alone at
1,016 of 4,173 location accounts; the widened `("alibi", "whereabouts")` gate takes it to the full
population. On the two `ml_corpus` sets alone the same cells read 724 of 3,030 = 23.9% → 3,030 of
3,030, reproducing Task 21.20's re-derivation to the digit.

### 5.4 The laundering join, published as a zero

**0 of 512 spoken vent accounts name a player who never vented.** The displacement class the
2026-08-26 register raised measures exactly zero on the baseline-8 bytes. This memo therefore
carries no laundering-displacement cell and no "the lever removes N" row; T-7 is offered as a ZERO
TRIPWIRE in §9 — an ON arm must not raise it — and never as an injustice a lever removes. The
baseline-7 reading of that class is retired and is not quoted here.

Printed beside it, and a different question: **59 of 512 spoken vent accounts are ones the
SPEAKER's own typed record does not bear out** (T-7b). An account can name a real venter and still
be a source this speaker cannot supply; that is what the corroboration ledger reads as first-hand,
and it is not a fabrication count. The two are kept apart deliberately.

### 5.5 The confession net, read as shipped

The `model_self_disclosure_visible_turns` / `crew_self_disclosure_control_turns` pair #416 shipped
is A-16's required disambiguation, already built. On these bytes it fires 5 times on the
player-visible surface, **1 of them by an IMPOSTOR speaker**. This memo reads that pair and does
not re-condition it. The register's "10 fires, 20% precision" is a baseline-7 figure over a
pre-disambiguation net and is not the cell above.

### 5.6 The render census

| prompt class | rendered | gains a block | lines added | bytes added |
|---|---|---|---|---|
| reporter opening (`crewmate_report`) | 672 | **672** | +1,344 | +401,856 |
| speech turn (`accusation_round`) | 2,959 | **2,023** | +4,046 | +1,185,478 |
| ballot (`vote_ballot`) | 3,631 | **0** | 0 | 0 |

Per meeting, for the smoke to join on: **exactly 1 opening and 3.01 mean crew speech turns (2,023
over 672 meetings) gain a block; 0 ballots do under this lever alone.**

The 936 speech turns that gain nothing are the impostor speakers: all three elicitation blocks in
`accusation_round.j2` are gated `testimony_shapes and not is_impostor`, and the template's one
other lever branch renders a `saw_kill` row the corpus contains none of. The ballot gains nothing
ALONE — and that is the slate's one genuine render interaction, priced in §6.2.

---

## §6 The render budget, priced as a first-class risk

### 6.1 The budget itself does not move offline, and the reason is structural

| cell | RECORDED-OFF | RECONSTRUCTED-OFF | ON (all three) |
|---|---|---|---|
| rendered memory rows per prompt snapshot | 255,918 / 7,271 = 35.20 | 255,918 / 7,271 = 35.20 | 255,918 / 7,271 = 35.20 |
| reported-testimony rows retained | 99,710 / 255,918 = 38.96% | 99,710 / 255,918 | 99,710 / 255,918 |

Testimony rows by living bucket: `<=4` 30,026, `5-6` 63,564, `>=7` 6,120.

The memory snapshot is composed BEFORE a template renders, so added prose displaces no memory row
at the recorded boundary. The slate can move this cell only through the widened INGEST adding rows
that then compete for `DEFAULT_TOKEN_BUDGET` at the NEXT meeting — which is the compounding effect
no offline instrument can reach (§7). **The displacement risk is real and it is un-measurable
here; saying so is the honest reading, and §9 offers the budget as a smoke-checkable cell rather
than a predicted one.**

### 6.2 What the slate does cost, and where the levers interact

| leg | prose lines added, per rendered prompt | ballot bytes added |
|---|---|---|
| `reporter_reasoning` alone | 11,625 / 7,262 = 1.60 | 0 |
| `corroboration_discipline` alone | 28,432 / 7,262 = 3.92 | +3,970,615 |
| `testimony_shapes` alone | 5,390 / 7,262 = 0.74 | 0 |
| **all three** | **45,447 / 7,262 = 6.26** | **+4,032,365** |
| two, less `testimony_shapes` | 40,057 / 7,262 = 5.52 | +3,970,615 |

Bytes are UTF-8 encoded bytes, not code points: the lever blocks carry em dashes and arrows, so a
character count would understate what the prompt costs.

Added lines and added bytes are exactly additive on the two TURN seams — 620 + 1,344 = 1,964 lines
and 171,222 + 401,856 = 573,078 bytes on the opening; 11,005 + 4,046 = 15,051 lines and 1,026,970 +
1,185,478 = 2,212,448 bytes on the speech turn. The BALLOT is the exception: its lines are additive
(28,432 + 0) but it carries **+61,750 bytes under the joint slate that neither lever produces
alone**, because `testimony_shapes` re-words the corroboration block's adopted clause — "named them
without an account their own record bears out" in place of "named them without adding anything they
saw". It is the only cross-lever render interaction in the slate, it is confined to one clause, and
it exists only when both levers are ON.

The leave-one-out attribution the `--withhold testimony_shapes` leg computes is the last row: 88%
of the slate's added prose survives dropping the testimony lever, and the corroboration block is
63% of the total on its own. The prose cost is the ballot's.

---

## §7 What no offline instrument can reach

Each of these is a fact about what the model does with new bytes, not about the bytes. Naming them
here is what makes the rest of the memo readable.

| cell | why it cannot be predicted offline |
|---|---|
| **the reporter-conviction count** (R-3, R-4) | the lever changes what an accuser READS; whether they then withhold an accusation is a fact about the model |
| **non-direct conviction accuracy** (P-1) | a vote is a model output; no render diff produces one |
| **the innocent-ejection count** (P-2) | the same, and it is the number the whole slate exists for |
| **the stated-confidence response to any anchoring rule** | §4.3's 0.80 is what the model said reading the OFF ballot; what it says reading the ON one is unrecorded |
| **whether crew stop laundering witnessed kills into `saw_vent` rows** | the `saw_kill` shape has no history: T-4 is 0 in both columns because nothing could have spoken one |
| **the win split** | downstream of every vote |
| **the COMPOUNDING effect of the widened ingest across a game** | meeting 1's ON render is derivable from meeting 1's recorded inputs, but meeting 2's ON transcript is a model output that does not exist. Every ingest and render cell in §5 is therefore a ONE-STEP-AHEAD reading at each recorded boundary, and the render budget's response (§6.1) is the specific casualty |
| **whether the reporter block reduces or INCREASES aim at the reporter** | naming a seat is not the same as protecting it; the direction is a model fact |
| **the ballot-block's effect on SKIP rate** | the corroboration block states source counts and changes no threshold; how a voter prices a one-voice charge is theirs |

And once more, in one sentence: **a sentence added to a prompt is not a vote that changes.**

---

## §8 Per-lever predictions, with what falsifies each and when

Every prediction below is a RENDER prediction. Each names what falsifies it and the earliest run
that can.

### 8.1 `reporter_reasoning`

| prediction | falsified by | when |
|---|---|---|
| every body-report meeting's opening prompt carries the discovery-account block; every non-reporter speech turn in one carries the base-rate block | one ON seed rendering either at zero, or any emergency meeting rendering either at all | the smoke's first ON seed |
| no ballot's bytes move | any ballot byte diff under this lever alone | the smoke's first ON seed |
| exposure over the injustice ledger: 34 of 46 rows (the RC class) sit in meetings the lever re-renders, and the 33 BOOM rows are a subset of them rather than an addition | — (an exposure statement, not a prediction) | — |
| a case the lever touches is not a case the lever fixes | — | — |

### 8.2 `corroboration_discipline`

| prediction | falsified by | when |
|---|---|---|
| ~99.5% of ballots gain the source-count block; the residue is meetings whose ledger has no row for that voter's candidates | a materially lower share on the ON seed | the smoke's first ON seed |
| the block states 475/1,525 no-first-hand charges over the record's own population | a re-walk of the committed bytes disagreeing | already asserted by this script |
| no speech turn's and no opening's bytes move | any diff on those seams under this lever alone | the smoke's first ON seed |
| exposure over the ledger: all 46 rows sit in meetings the block renders in; 89 of the 150 ejecting ballots are the hearsay shape it counts | — | — |
| a case the lever touches is not a case the lever fixes | — | — |

### 8.3 `testimony_shapes`

| prediction | falsified by | when |
|---|---|---|
| every opening prompt and every CREW speech turn gains an elicitation block; no impostor speech turn does | an impostor turn's bytes moving, or a crew turn's not moving | the smoke's first ON seed |
| the ballot's bytes move ONLY when the corroboration lever is also ON | a ballot diff under this lever alone | the smoke's first ON seed |
| the reduction carries `whereabouts` and `saw_move` where it carried none | zero of either in the ON recording's derived testimony | the smoke's first ON seed |
| the alibi map fills to 100% of location accounts | any location account absent from an ON agent's map | the smoke's first ON seed |
| `saw_kill` statements: no offline prediction is made | — | the full record only |
| the ingest's +23,551 rows and their budget consequence are ONE-STEP-AHEAD | — | the full record only |

### 8.4 The slate

| prediction | falsified by | when |
|---|---|---|
| added prose is additive in LINES on every seam and the only cross-lever interaction is the ballot's adopted-clause re-wording (+61,750 bytes) | a byte delta on any other seam that neither lever produces alone | the smoke's first ON seed |
| the rendered-memory-row budget is unchanged at meeting 1 | a first-meeting budget diff | the smoke's first ON seed |
| the budget at meeting 2 and beyond: no prediction | — | the full record only |

---

## §9 Tripwire CANDIDATES

Offered to the pre-registration, which may ratify, decline or replace any of them. Each is a cell
whose predicted value is exactly zero or exactly the full population, so one smoke seed falsifies
it at n=1. **None of these is a bar.**

| candidate | cell | predicted | reading |
|---|---|---|---|
| **T1 — the zero tripwire** | T-7, spoken vent accounts naming a player who never vented | **0 of 512** OFF; ON must not raise it | the class measures zero at baseline 8; an ON arm that mints fabricated vent accounts has made something worse |
| **T2 — the reporter thread** | R-13 / R-14 | **620/620** and **2,715/2,715** | zero on an ON seed means the lever did not thread and the record must not start |
| **T3 — the ballot untouched** | R-15, ballots gaining a reporter block | **0 of 3,631** | a non-zero reading means the reporter lever reached a seam it does not own |
| **T4 — the full-population fill** | T-6, location accounts reaching the alibi map | **100%** ON | a partial fill means the widened gate did not land |
| **T5 — the crew-only elicitation** | T-9 | **2,023 of 2,959**, and 0 impostor turns | an impostor turn gaining the block is a firewall question, not a render one |
| **T6 — the ledger block's reach** | C-9 | **~99.5% of ballots** | a materially lower share means the ledger is not being built where it should be |
| **T7 — the budget at meeting 1** | B-1 | unchanged | a first-meeting memory-row diff means prose is displacing memory, which this slate must not do |

---

## §10 The full table

Every row here is re-derived by the instrument and compared against this document by
`tests/scripts/test_counterfactual_phase21.py`, so the memo cannot drift from the script. `—`
means the column has no producer for that cell, and `[ADV]` marks a column measured over 20 or
fewer cases (reading rule 3).

The three censuses that are not cell rows — the ejecting-ballot census of §4.3, the eight-kind
reduction census of §5.2, and the per-lever render census of §3.3 / §4.4 / §5.6 — are emitted
pooled by `--json` as `pooled_ballot_census`, `pooled_testimony_census` and
`pooled_render_census`, and the §4.3 and §5.2 tables are compared against them by the same test.
Nothing published here exists only as prose.

### 10.1 Pooled, over 300 games and 672 meetings

| cell | what it counts | RECORDED-OFF | RECONSTRUCTED-OFF | ON |
|---|---|---|---|---|
| P-1 | non-direct conviction accuracy (impostor / non-direct ejections) | 50/96 | — | — |
| P-2 | innocent ejections (of every ejection) | 46/429 | 46/429 | — |
| P-3 | direct-proof ejections that convicted an impostor | 333/333 | — | — |
| P-4 | body-meeting ejections landing on an already-cleared player | 63/377 | — | — |
| R-1 | body-report meetings (of every meeting) | 620/672 | 620/672 | — |
| R-2 | reporter is a CREWMATE (of body-report meetings) | 620/620 | — | — |
| R-3 | innocent ejections that ejected the meeting's own reporter | 34/46 | — | — |
| R-4 | reporter ejected (per reporter slot) | 34/620 | — | — |
| R-5 | innocent non-reporter ejected (per slot) | 12/1859 | — | — |
| R-6 | crew SPEECH accusations aimed at the reporter | 521/2129 | — | — |
| R-7 | impostor SPEECH accusations aimed at the reporter | 520/739 | — | — |
| R-8 | crew BALLOTS aimed at the reporter | 160/2479 | — | — |
| R-9 | impostor BALLOTS aimed at the reporter | 103/856 | — | — |
| R-10 | ballot rationales carrying an exculpatory hinge (upper bound) | 13/3335 | — | — |
| R-11 | body-report meetings carrying a non-reporter co-discoverer | 118/620 | — | — |
| R-12 | co-discoverer slots held by an IMPOSTOR | 71/145 | — | — |
| R-13 | reporter openings gaining the discovery-account block | — | 0/620 | 620/620 |
| R-14 | non-reporter speech turns gaining the base-rate block | — | 0/2715 | 2715/2715 |
| R-15 | ballots gaining a reporter block | — | 0/3631 | 0/3631 |
| C-1 | accused subjects with NO first-hand source | — | 475/1525 | 475/1525 |
| C-2 | ejected subjects with NO first-hand source | — | 11/425 | 11/425 |
| C-3 | ejections whose charge ANSWERED the ejectee's own | — | 33/429 | 33/429 |
| C-4 | ejected subjects with a map-satisfied placement pair | — | 48/429 | 48/429 |
| C-5 | ejecting ballots citing HEARSAY (another speaker's turn) | — | 89/150 | — |
| C-6 | ejecting ballots citing the voter's OWN observation | — | 37/150 | — |
| C-7 | ejecting ballots citing NOTHING | — | 1/150 | — |
| C-8 | innocent ejections carrying an impossible-transit charge | — | 20/46 | — |
| C-9 | ballots gaining the source-count block | — | 0/3631 | 3614/3631 |
| T-1 | spoken statements surviving the reduction | — | 9934/14697 | 14697/14697 |
| T-2 | whereabouts self-placements dropped whole | — | 0/3157 | 3157/3157 |
| T-3 | saw_move transitions dropped whole | — | 0/1606 | 1606/1606 |
| T-4 | saw_kill accounts carried as content | — | 0/0 [ADV] | 0/0 [ADV] |
| T-5 | episodic rows the ingest writes at recorded boundaries | — | 49667/73218 | 73218/73218 |
| T-6 | location accounts that reach the alibi map | — | 1016/4173 | 4173/4173 |
| T-7 | spoken vent accounts naming a player who never vented | — | 0/512 | 0/512 |
| T-7b | spoken vent accounts the SPEAKER's own record does not bear out | — | 59/512 | 59/512 |
| T-8 | player-visible self-disclosure turns by an IMPOSTOR speaker | 1/5 [ADV] | — | — |
| T-9 | speech turns gaining a testimony-shape block | — | 0/2959 | 2023/2959 |
| T-10 | opening prompts gaining a testimony-shape block | — | 0/672 | 672/672 |
| B-1 | rendered memory rows per prompt snapshot | 255918/7271 | 255918/7271 | 255918/7271 |
| B-2 | reported-testimony rows retained (of rendered rows) | 99710/255918 | 99710/255918 | 99710/255918 |
| B-3 | prose lines the slate ADDS, per rendered prompt | — | 0/7262 | 45447/7262 |
| B-4 | prose lines added, leave-one-out | — | 0/7262 | 40057/7262 |

### 10.2 `samples/9p2i`

50 games, 151 meetings, 141 body reports, 95 ejections, 13 of them innocent.

| set | cell | RECORDED-OFF | RECONSTRUCTED-OFF | ON |
|---|---|---|---|---|
| samples/9p2i | P-1 | 14/27 | — | — |
| samples/9p2i | P-2 | 13/95 | 13/95 | — |
| samples/9p2i | P-3 | 68/68 | — | — |
| samples/9p2i | P-4 | 16/85 | — | — |
| samples/9p2i | R-1 | 141/151 | 141/151 | — |
| samples/9p2i | R-2 | 141/141 | — | — |
| samples/9p2i | R-3 | 7/13 [ADV] | — | — |
| samples/9p2i | R-4 | 7/141 | — | — |
| samples/9p2i | R-5 | 6/464 | — | — |
| samples/9p2i | R-6 | 127/511 | — | — |
| samples/9p2i | R-7 | 121/179 | — | — |
| samples/9p2i | R-8 | 45/605 | — | — |
| samples/9p2i | R-9 | 33/202 | — | — |
| samples/9p2i | R-10 | 6/807 | — | — |
| samples/9p2i | R-11 | 30/141 | — | — |
| samples/9p2i | R-12 | 19/38 | — | — |
| samples/9p2i | R-13 | — | 0/141 | 141/141 |
| samples/9p2i | R-14 | — | 0/666 | 666/666 |
| samples/9p2i | R-15 | — | 0/869 | 0/869 |
| samples/9p2i | C-1 | — | 93/354 | 93/354 |
| samples/9p2i | C-2 | — | 3/92 | 3/92 |
| samples/9p2i | C-3 | — | 7/95 | 7/95 |
| samples/9p2i | C-4 | — | 17/95 | 17/95 |
| samples/9p2i | C-5 | — | 25/44 | — |
| samples/9p2i | C-6 | — | 12/44 | — |
| samples/9p2i | C-7 | — | 1/44 | — |
| samples/9p2i | C-8 | — | 8/13 [ADV] | — |
| samples/9p2i | C-9 | — | 0/869 | 868/869 |
| samples/9p2i | T-1 | — | 2370/3577 | 3577/3577 |
| samples/9p2i | T-2 | — | 0/766 | 766/766 |
| samples/9p2i | T-3 | — | 0/441 | 441/441 |
| samples/9p2i | T-4 | — | 0/0 [ADV] | 0/0 [ADV] |
| samples/9p2i | T-5 | — | 12188/18371 | 18371/18371 |
| samples/9p2i | T-6 | — | 263/1029 | 1029/1029 |
| samples/9p2i | T-7 | — | 0/98 | 0/98 |
| samples/9p2i | T-7b | — | 8/98 | 8/98 |
| samples/9p2i | T-8 | 0/1 [ADV] | — | — |
| samples/9p2i | T-9 | — | 0/718 | 500/718 |
| samples/9p2i | T-10 | — | 0/151 | 151/151 |
| samples/9p2i | B-1 | 63624/1740 | 63624/1740 | 63624/1740 |
| samples/9p2i | B-2 | 25628/63624 | 25628/63624 | 25628/63624 |
| samples/9p2i | B-3 | — | 0/1738 | 11161/1738 |
| samples/9p2i | B-4 | — | 0/1738 | 9859/1738 |

### 10.3 `ml_corpus/9p2i`

150 games, 439 meetings, 407 body reports, 281 ejections, 29 of them innocent.

| set | cell | RECORDED-OFF | RECONSTRUCTED-OFF | ON |
|---|---|---|---|---|
| ml_corpus/9p2i | P-1 | 32/61 | — | — |
| ml_corpus/9p2i | P-2 | 29/281 | 29/281 | — |
| ml_corpus/9p2i | P-3 | 220/220 | — | — |
| ml_corpus/9p2i | P-4 | 47/249 | — | — |
| ml_corpus/9p2i | R-1 | 407/439 | 407/439 | — |
| ml_corpus/9p2i | R-2 | 407/407 | — | — |
| ml_corpus/9p2i | R-3 | 23/29 | — | — |
| ml_corpus/9p2i | R-4 | 23/407 | — | — |
| ml_corpus/9p2i | R-5 | 6/1323 | — | — |
| ml_corpus/9p2i | R-6 | 371/1494 | — | — |
| ml_corpus/9p2i | R-7 | 336/489 | — | — |
| ml_corpus/9p2i | R-8 | 109/1730 | — | — |
| ml_corpus/9p2i | R-9 | 61/582 | — | — |
| ml_corpus/9p2i | R-10 | 3/2312 | — | — |
| ml_corpus/9p2i | R-11 | 88/407 | — | — |
| ml_corpus/9p2i | R-12 | 52/107 | — | — |
| ml_corpus/9p2i | R-13 | — | 0/407 | 407/407 |
| ml_corpus/9p2i | R-14 | — | 0/1905 | 1905/1905 |
| ml_corpus/9p2i | R-15 | — | 0/2516 | 0/2516 |
| ml_corpus/9p2i | C-1 | — | 313/1006 | 313/1006 |
| ml_corpus/9p2i | C-2 | — | 5/280 | 5/280 |
| ml_corpus/9p2i | C-3 | — | 22/281 | 22/281 |
| ml_corpus/9p2i | C-4 | — | 31/281 | 31/281 |
| ml_corpus/9p2i | C-5 | — | 58/98 | — |
| ml_corpus/9p2i | C-6 | — | 23/98 | — |
| ml_corpus/9p2i | C-7 | — | 0/98 | — |
| ml_corpus/9p2i | C-8 | — | 10/29 | — |
| ml_corpus/9p2i | C-9 | — | 0/2516 | 2500/2516 |
| ml_corpus/9p2i | T-1 | — | 7067/10390 | 10390/10390 |
| ml_corpus/9p2i | T-2 | — | 0/2214 | 2214/2214 |
| ml_corpus/9p2i | T-3 | — | 0/1109 | 1109/1109 |
| ml_corpus/9p2i | T-4 | — | 0/0 [ADV] | 0/0 [ADV] |
| ml_corpus/9p2i | T-5 | — | 36485/53387 | 53387/53387 |
| ml_corpus/9p2i | T-6 | — | 705/2919 | 2919/2919 |
| ml_corpus/9p2i | T-7 | — | 0/366 | 0/366 |
| ml_corpus/9p2i | T-7b | — | 51/366 | 51/366 |
| ml_corpus/9p2i | T-8 | 1/3 [ADV] | — | — |
| ml_corpus/9p2i | T-9 | — | 0/2077 | 1441/2077 |
| ml_corpus/9p2i | T-10 | — | 0/439 | 439/439 |
| ml_corpus/9p2i | B-1 | 186784/5039 | 186784/5039 | 186784/5039 |
| ml_corpus/9p2i | B-2 | 74082/186784 | 74082/186784 | 74082/186784 |
| ml_corpus/9p2i | B-3 | — | 0/5032 | 31594/5032 |
| ml_corpus/9p2i | B-4 | — | 0/5032 | 27834/5032 |

### 10.4 `samples/4p1i`

50 games, 39 meetings, 36 body reports, 24 ejections, 4 of them innocent. Every cell in this block sits in a set that carried 4 innocent ejections, so no row here takes part in a directional statement.

| set | cell | RECORDED-OFF | RECONSTRUCTED-OFF | ON |
|---|---|---|---|---|
| samples/4p1i | P-1 | 1/5 [ADV] | — | — |
| samples/4p1i | P-2 | 4/24 | 4/24 | — |
| samples/4p1i | P-3 | 19/19 [ADV] | — | — |
| samples/4p1i | P-4 | 0/21 | — | — |
| samples/4p1i | R-1 | 36/39 | 36/39 | — |
| samples/4p1i | R-2 | 36/36 | — | — |
| samples/4p1i | R-3 | 4/4 [ADV] | — | — |
| samples/4p1i | R-4 | 4/36 | — | — |
| samples/4p1i | R-5 | 0/36 | — | — |
| samples/4p1i | R-6 | 12/59 | — | — |
| samples/4p1i | R-7 | 32/35 | — | — |
| samples/4p1i | R-8 | 5/72 | — | — |
| samples/4p1i | R-9 | 4/36 | — | — |
| samples/4p1i | R-10 | 1/108 | — | — |
| samples/4p1i | R-11 | 0/36 | — | — |
| samples/4p1i | R-12 | 0/0 [ADV] | — | — |
| samples/4p1i | R-13 | — | 0/36 | 36/36 |
| samples/4p1i | R-14 | — | 0/72 | 72/72 |
| samples/4p1i | R-15 | — | 0/117 | 0/117 |
| samples/4p1i | C-1 | — | 32/78 | 32/78 |
| samples/4p1i | C-2 | — | 3/24 | 3/24 |
| samples/4p1i | C-3 | — | 4/24 | 4/24 |
| samples/4p1i | C-4 | — | 0/24 | 0/24 |
| samples/4p1i | C-5 | — | 6/8 [ADV] | — |
| samples/4p1i | C-6 | — | 2/8 [ADV] | — |
| samples/4p1i | C-7 | — | 0/8 [ADV] | — |
| samples/4p1i | C-8 | — | 2/4 [ADV] | — |
| samples/4p1i | C-9 | — | 0/117 | 117/117 |
| samples/4p1i | T-1 | — | 241/355 | 355/355 |
| samples/4p1i | T-2 | — | 0/85 | 85/85 |
| samples/4p1i | T-3 | — | 0/29 | 29/29 |
| samples/4p1i | T-4 | — | 0/0 [ADV] | 0/0 [ADV] |
| samples/4p1i | T-5 | — | 482/710 | 710/710 |
| samples/4p1i | T-6 | — | 29/114 | 114/114 |
| samples/4p1i | T-7 | — | 0/20 [ADV] | 0/20 [ADV] |
| samples/4p1i | T-7b | — | 0/20 [ADV] | 0/20 [ADV] |
| samples/4p1i | T-8 | 0/0 [ADV] | — | — |
| samples/4p1i | T-9 | — | 0/78 | 39/78 |
| samples/4p1i | T-10 | — | 0/39 | 39/39 |
| samples/4p1i | B-1 | 2552/234 | 2552/234 | 2552/234 |
| samples/4p1i | B-2 | 0/2552 | 0/2552 | 0/2552 |
| samples/4p1i | B-3 | — | 0/234 | 1299/234 |
| samples/4p1i | B-4 | — | 0/234 | 1143/234 |

### 10.5 `ml_corpus/4p1i`

50 games, 43 meetings, 36 body reports, 29 ejections, 0 of them innocent. Every cell in this block sits in a set that carried 0 innocent ejections, so no row here takes part in a directional statement.

| set | cell | RECORDED-OFF | RECONSTRUCTED-OFF | ON |
|---|---|---|---|---|
| ml_corpus/4p1i | P-1 | 3/3 [ADV] | — | — |
| ml_corpus/4p1i | P-2 | 0/29 | 0/29 | — |
| ml_corpus/4p1i | P-3 | 26/26 | — | — |
| ml_corpus/4p1i | P-4 | 0/22 | — | — |
| ml_corpus/4p1i | R-1 | 36/43 | 36/43 | — |
| ml_corpus/4p1i | R-2 | 36/36 | — | — |
| ml_corpus/4p1i | R-3 | 0/0 [ADV] | — | — |
| ml_corpus/4p1i | R-4 | 0/36 | — | — |
| ml_corpus/4p1i | R-5 | 0/36 | — | — |
| ml_corpus/4p1i | R-6 | 11/65 | — | — |
| ml_corpus/4p1i | R-7 | 31/36 | — | — |
| ml_corpus/4p1i | R-8 | 1/72 | — | — |
| ml_corpus/4p1i | R-9 | 5/36 | — | — |
| ml_corpus/4p1i | R-10 | 3/108 | — | — |
| ml_corpus/4p1i | R-11 | 0/36 | — | — |
| ml_corpus/4p1i | R-12 | 0/0 [ADV] | — | — |
| ml_corpus/4p1i | R-13 | — | 0/36 | 36/36 |
| ml_corpus/4p1i | R-14 | — | 0/72 | 72/72 |
| ml_corpus/4p1i | R-15 | — | 0/129 | 0/129 |
| ml_corpus/4p1i | C-1 | — | 37/87 | 37/87 |
| ml_corpus/4p1i | C-2 | — | 0/29 | 0/29 |
| ml_corpus/4p1i | C-3 | — | 0/29 | 0/29 |
| ml_corpus/4p1i | C-4 | — | 0/29 | 0/29 |
| ml_corpus/4p1i | C-5 | — | 0/0 [ADV] | — |
| ml_corpus/4p1i | C-6 | — | 0/0 [ADV] | — |
| ml_corpus/4p1i | C-7 | — | 0/0 [ADV] | — |
| ml_corpus/4p1i | C-8 | — | 0/0 [ADV] | — |
| ml_corpus/4p1i | C-9 | — | 0/129 | 129/129 |
| ml_corpus/4p1i | T-1 | — | 256/375 | 375/375 |
| ml_corpus/4p1i | T-2 | — | 0/92 | 92/92 |
| ml_corpus/4p1i | T-3 | — | 0/27 | 27/27 |
| ml_corpus/4p1i | T-4 | — | 0/0 [ADV] | 0/0 [ADV] |
| ml_corpus/4p1i | T-5 | — | 512/750 | 750/750 |
| ml_corpus/4p1i | T-6 | — | 19/111 | 111/111 |
| ml_corpus/4p1i | T-7 | — | 0/28 | 0/28 |
| ml_corpus/4p1i | T-7b | — | 0/28 | 0/28 |
| ml_corpus/4p1i | T-8 | 0/1 [ADV] | — | — |
| ml_corpus/4p1i | T-9 | — | 0/86 | 43/86 |
| ml_corpus/4p1i | T-10 | — | 0/43 | 43/43 |
| ml_corpus/4p1i | B-1 | 2958/258 | 2958/258 | 2958/258 |
| ml_corpus/4p1i | B-2 | 0/2958 | 0/2958 | 0/2958 |
| ml_corpus/4p1i | B-3 | — | 0/258 | 1393/258 |
| ml_corpus/4p1i | B-4 | — | 0/258 | 1221/258 |

---

## §11 Reproduction

```
uv run python scripts/counterfactual_phase21.py --sets all
uv run python scripts/counterfactual_phase21.py --sets all --json
uv run python scripts/counterfactual_phase21.py --sets all --withhold corroboration_discipline
uv run pytest tests/scripts/test_counterfactual_phase21.py -q
```

28.7 s over the four committed sets from a fresh clone, `$0`, no network, no model call, no `AILIBI_*` export from the operator (the script refuses to run under one). The Phase-20 instrument took 28 s over the same 300 games. `--json` emits this table machine-readably for the pre-registration and the record audit to consume, and `--withhold` re-points the leave-one-out leg at any of the three levers.

The reconstruction is `tests.meetings.test_prompt_byte_golden.walk_replay_meetings`, the only committed walk that drives the real `MeetingManager` and yields per-meeting participants carrying `sighting_records`, `move_witness_records` and `body_discovery_records` — all three of which the ON legs need and which the replay-walk and the API loader do not supply. Importing it from a test module is a deliberate, precedented inversion (`eval/determinism_test.py`, `eval/leak_test.py`), so the command runs under `uv run`, which resolves the dev group; promoting the walk to a production home is Task 21.25's. That the OFF re-render IS the record is not assumed either: every recorded LLM call is attributed back to the render that produced its base, and a call no render explains is a refusal — which is also why RECORDED-OFF and RECONSTRUCTED-OFF agree on the render-budget cells to the digit.

### 11.1 What the instrument refuses to do

Four refusals fire before any number is printed, and each ships with a case proving it bites (`tests/scripts/test_counterfactual_phase21.py`):

1. **A graduated lever.** Every priced lever must still be registered in `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` and must read OFF under an EMPTY environment. A graduated resolver ignores the argument this script toggles it with, so its OFF column would silently be its ON column — the failure `scripts/counterfactual_phase20.py` turned into a refusal, inherited here on day one rather than after the fact.
2. **A stale ambient export.** `substrate_flag_snapshot()` read from the AMBIENT process must report every LIVE TOGGLE OFF — not only the priced three — at start and at exit, because the recorded substrate stamps all of them OFF. Seven consumers re-derive the meeting reduction with no `env` argument, so an operator with a stale `AILIBI_TESTIMONY_SHAPES=1` export would make every imported instrument's OFF column an ON column while an empty-mapping check sailed through green; and the one lever this memo holds OFF would do its damage most quietly of all, since its arm swaps a template file for a body neither priced lever's block reaches. The refusal names the variable and says to unset it. Both renderer bundles are additionally built under an explicit environment rather than the ambient one, so the template BODIES cannot follow an export either.
3. **An OFF column that is not the record.** The innocent-ejection enumeration is checked against `audits/audit-phase-21-rerecord.md` §5.1 per set; the RC and WEAKFLAG ledger classes are checked against `eval.reporter_justice` and the committed weak-flag conviction cell; the four corroboration cells are checked against the records that published them. A disagreement is a DEFECT IN THIS SCRIPT, and the failure message says so and names both readings.
4. **A fourth lever.** The slate is three keys with `impostor_roll_call` OFF. That arm swaps `accusation_round.j2` for a variant carrying neither sibling's block, so an all-four slate would silently drop the reporter and testimony-shapes effects from every statement turn while a composite stamp claimed them.

The process environment is byte-identical before and after a whole run, and a test asserts it.

