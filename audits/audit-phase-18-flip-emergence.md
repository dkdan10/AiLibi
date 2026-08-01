# Phase-18 flip + emergence reading — the two-axis owner memo: NO-FLIP on the §1.3 bar, zero EMERGENT among the fourteen pre-registered rulings, NO crew adoption (Task 18.27)

**Date:** 2026-08-01.
**Task:** 18.27 — THE FLIP + EMERGENCE READING (owner) + conditional productization,
`tasks/phase-18.md`. Depends on 18.4 (the ratified pre-registration), 18.18, 18.26 (the
evidence, merged `384effc`, #317).
**What is being ruled:** axis 1 — the champion candidate against the standing §1.3 flip
bar (`audits/audit-phase-17-close.md` §1.3, quoted verbatim in §1.1), on the evidence-gated
17.16 shape with both branches pre-authored; axis 2 — every pre-registered instrument
ruling of `audits/audit-phase-18-emergence-preregistration.md` (the 14-ruling enumeration
of its §2.2), each ruled EMERGENT / NOT-DEMONSTRATED under the §6 four-part discipline;
the F13 ruling (inherited from the 18.24 merge — the 18.26 pre-registered cell measures
it, this memo rules); the two post-hoc-criterion questions 18.26 put to this memo; and
the crew-adoption slot, put and recorded explicitly.
**Method:** every quoted cell comes from the committed 18.26 evidence rows and persisted
instrument cells in `training/reports/results-finalist-eval.jsonl` (rows
`p18-imp-{ea4bc955,bfd145cb,6d327dcb,7f73929d}`, `p18-fsm-comparator`,
`p18-crew-{c1-gen9,c1-gen0,c2-gen9,c2-gen0}`; persisted cells `f13_intersection_gauges`,
`instruments.kill_craft_rider_intersection`, `instruments.conversion_paired_49_seed`,
`instruments.intersection_49_seed_for_7f73929d`, `instruments.registered_nested_cells`,
`instruments.seed_mod5_splits`, `instruments.kill_craft_co_present_departure`) — never
report prose; ablation provenance is quoted from the committed campaign reports
(`report-impostor-campaign.md` §6, `report-crew-campaign.md` §6) as the pre-registration's
§6.c directs ("the 18.27 reading consumes ablation evidence from there and never
regenerates it"). Derived statistics (pooled z, Fisher z, split signs, the F13 pooled
margins) are the §6.a registered formulas computed from the quoted cells with inputs
beside them (the 15.18 convention); §15 reproduces every one. The prose defects of the
campaign reports are named in their own §12 Errata blocks — this memo quotes committed
artifacts, never the prose those errata correct.
**Label key:** **[VERIFIED]** quoted from a committed row/cell/pin/source ·
**[INFERRED]** arithmetic over verified cells (inputs shown) · **[RULED (owner) —
ratified at merge]** a ruling this memo makes, ratified by the owner's merge of this
task's PR.
**Sign-off:** the 14.6/15.18 convention — §13 is the owner record, ratified by merge.
**Separability (the 18.27 integration-risk contract):** Part A (axis 1, §1–§5) and
Part B (axis 2 + the slots, §6–§10) are independently ratifiable; §13 lists their
decisions separately so the owner can rule one axis and hold the other with the PR open
(the 17.14 PENDING pattern). Nothing in Part B is an input to Part A's ruling, and
Part A feeds Part B only the champion designation (§4.1), restated there.

---

## 0. Verdict in one line

**Axis 1 reads FAIL — NO-FLIP:** every learned arm beats the same-seed FSM comparator on
wins (+0.12 to +0.30) and every learned arm fails the referee's supply conjunction at the
adopted baseline-6 floors (three arms on both live gauges, `bfd145cb…` on conversion
alone with its flags cell UNRESOLVABLE), so no candidate satisfies referee-PASS AND
win-edge; the scripted FSM stays the default mover, the champion stays opt-in, nothing
swaps, and 18.28 closes NO-FLIP. **Axis 2 rules zero EMERGENT:** all fourteen
pre-registered rulings read NOT-DEMONSTRATED — eleven fail clause (a) or admit no delta,
two (crew-witnessed-kill rate z = +3.37, co-present-kill departure z = +4.32) pass
clauses (a)/(b)/(d) and fail on clause (c) because no campaign lever enables them and no
ablation exists (unablated ⇒ NOT-DEMONSTRATED by construction — they are recorded as the
phase's two named behavioral findings), and the two entropy rulings are unjudgeable as
recorded. **F13:** hypothesis A is REJECTED as unsupported (all three pooled
runner-up-minus-champion margins negative and noise-barred; zero referee passes anywhere
at n=50); hypothesis B stands as the operative reading without being itself demonstrated;
no selection-rule fix contract routes. **The crew-adoption slot is put and closes
NO-ADOPTION.**

---

# PART A — AXIS 1: THE FLIP

## 1. The standing bar

### 1.1 The §1.3 flip bar, verbatim **[VERIFIED]**

`audits/audit-phase-17-close.md` §1.3 ("What Phase 18 would need (the honest scoping)"),
first bullet, verbatim:

> - **To flip the default:** a mover that closes `utility-es`'s two gaps **without
>   surrendering the edge** — lift flags/meeting by ≥ +0.0773 to the 0.50279 supply floor
>   AND lift conversion to its own (then-lower) derived floor (−0.2016 at today's
>   economy), while keeping the win rate at or above the same-substrate FSM's. The bar
>   itself STAYS (owner charter, the 17.12 selection-bar-honesty ruling): a co-adapted
>   impostor's objective is to make convictions harder, and the floor pricing that is the
>   instrument working — the FAIL is the finding, and any future re-pricing of the bar is
>   an owner decision, never an instrument edit.

The phase charter carries the same bar as locked decision 4 (`tasks/phase-18.md`):
*"the §1.3 flip bar is the TARGET … The recorded default-flip bar stands unchanged
(flags/meeting ≥ 0.50279 at the baseline-5 economy — re-pinned at whatever baseline the
phase adopts — AND the population-relative conversion floor cleared AND win ≥ the
same-substrate FSM's)."* The task contract states the same conjunction: *"referee PASS at
the adopted baseline's floors AND win ≥ the same-seed FSM comparator."*

### 1.2 The bar at the adopted baseline (baseline 6) **[VERIFIED]**

The phase adopted baseline 6 at the 18.12 record; every 18.26 row scores
`baseline_id: "baseline-6"`. The floors, from `eval/watchability.py` (the committed 9p2i
pins, quoted by `audits/audit-phase-18-baseline-6.md` §5):

- `witnessed_event_rate` ≥ 6/177 = 0.03389830508474576
- `flags_per_meeting` ≥ 180/165 = 1.0909090909090908
- `testimony_backed_conversion` ≥ the population-relative derived floor
  min(1.0, 0.5735294117647058 × (1.0909090909090908 / measured flags_per_meeting)) —
  the 78/136 baseline-6 conversion pin under the 16.11 derivation
  (`population_relative_conversion=True`)

Every per-arm conversion floor quoted in §3 re-derives from exactly this formula on the
arm's own measured flags cell **[INFERRED — §15 reproduces each]**.

### 1.3 The comparator and the pairing map **[VERIFIED]**

The win-edge comparator is the fresh same-seed scripted-FSM arm recorded at 18.26
(`p18-fsm-comparator`: seeds 0–49, `tactical_policy_stamp` = the five-field
`fsm-default` stamp read back from bytes, `opponent_absence_proven: true`,
`crew_stamp_games: 0`, `learned_stamp_games: 0`, validity PASS) — never the Phase-17
report's 18/50 = 0.36 (baseline-5, stale) and never the canonical
`replays/samples/9p2i` manifest (15/50 = 0.30, a different recording of the same seeds;
the §2.1 comparator discipline binds the claim to the arm recorded beside the
candidates). Its row: **13/50 = 0.26 impostor win**, referee **PASS** (the only
referee-PASS row on the slate), mean 54.96 / median 53.55.

The pairing map, exactly: the comparator's **full-50** cells pair the three full arms
(`ea4bc955…`, `bfd145cb…`, `6d327dcb…`); **`7f73929d…` pairs the 49-seed intersection**
(seed 35 excluded — §2.2), where the comparator's seed-35 game is an `IMPOSTOR_PARITY`
and the intersection comparator is **12/49 = 0.24490, never 0.26** [INFERRED from the
comparator row's `watchability.per_game` reasons — §15]; **no comparator row pairs the
four crew arms** (a crew claim's §2.1 comparator is scripted-FSM crew vs the same
opponent, and no such row exists in the slate — §10).

## 2. The evidence corpus and the axis-1 mechanics

### 2.1 Provenance and validity **[VERIFIED]**

All nine arms: recorded 2026-07-29..31 on the real Featherless path
(`Qwen/Qwen3.6-27B`, prompt set `qwen3_6_27b`, $0), 50 seeds (0–49), 9p2i, stamps read
back from bytes on every game ("never echoed from the launch config"). The four impostor
arms and the comparator: stamp-proven (`stamp_verified_games` = games,
`stamp_equals_committed_sha256: true` where a committed sidecar exists), validity gate
PASS. The four crew arms are the owner-directed diagnostic block (2026-07-29), each
vs the frozen impostor champion `ea4bc955…` (dual-stamped, opponent stamp verified);
three of the four crew rows FAIL the validity gate (`c1-gen0` seed-20 stalemate,
`c2-gen9` two stalemates + meeting rate at the floor, `c2-gen0` zero LLM calls /
empty model provenance) and read as diagnostics, never selection evidence.

The four candidates **[VERIFIED]**:

| arm | artifact | lineage | anchor |
|---|---|---|---|
| `p18-imp-ea4bc955` | `coevo/intermediates/run-02-utility-lambda4/gen-2` | run-02 intermediate gen-2 (slate 1) | `fsm-default` (λ=4 lineage) |
| `p18-imp-bfd145cb` | `coevo/runnerups/run-02-utility-lambda4/gen-9` | run-02 runner-up gen-9 (slate 2) | `fsm-default` |
| `p18-imp-6d327dcb` | `coevo/run-01-utility-champion/impostor/gen-3` | the incumbent control (byte-identical to the committed opt-in champion), re-recorded at baseline 6 (slate 3) | `fsm-default` |
| `p18-imp-7f73929d` | `coevo/runnerups/run-03-utility-bcanchor/gen-8` | run-03 runner-up gen-8, the F13 test arm (slate 4) | `filtered-bc-anchor` |

### 2.2 The three mechanics this ruling carries **[VERIFIED]**

**(i) `witnessed_event_rate` is UNRESOLVABLE on ALL NINE arms — structural.** The 18.26
pre-registered noise precondition (a gauge whose split-half noise exceeds 25% of its
threshold reads UNRESOLVABLE, and only gauges clearing the precondition feed this
ruling) fails on every arm's `split_half.witnessed_event_rate` cell: the floor is the
rare-event point estimate 6/177 = 0.03390, so its ceiling is 0.00847, while the measured
half-to-half noise runs 0.01479 (`c2-gen0`) to 0.08671 (`7f73929d…`) — 1.75× to 10.2×
the ceiling; the comparator's own reads 0.02299. At n=50 this gauge cannot resolve a
25%-of-a-rare-event-floor question. Consequence: the ratified three-gauge referee is
**effectively two gauges** for this ruling — `flags_per_meeting` +
`testimony_backed_conversion` (this compression is this memo's wording for the
consequence of the nine exclusions, not the report's). The floor still gates (each arm's
witnessed PASS stands as a PASS); it is excluded from discriminating between arms.

**(ii) `bfd145cb…`'s flags cell is also UNRESOLVABLE — its FAIL rests on conversion
alone.** Its `split_half.flags_per_meeting` noise is 0.29291 against the 0.27273 ceiling
(a 7% overshoot; the only impostor arm to fail this precondition). The cell is excluded
from the ruling, so `bfd145cb…` fails axis 1 on `testimony_backed_conversion` alone —
its numeric flags miss (0.90000 < 1.09091) is reported but not counted.
`testimony_backed_conversion` clears the precondition on all eight arms that have
meetings (noise 0.00380–0.09459) and is the gauge this ruling reads most safely.

**(iii) `7f73929d…` scores at n=49.** Seed 35 is excluded (owner-sanctioned: 14 logged
attempts all rc 99, a content-triggered validation pathology on the deterministic
opening prompt; forensics kept), annotated on every cell; its win edge reads against the
49-seed intersection comparator **12/49 = 0.24490**, and the cross-seed-set +0.16857
against the full-50 comparator is named only to be rejected.

## 3. The reading — every floor cell and win edge, arm by arm

All cells **[VERIFIED]** from the rows' `watchability.supply_gauges` and `core`; margins
and edges **[INFERRED]** (subtraction). Per-arm derived conversion floors re-derive from
the §1.2 formula on the arm's measured flags cell.

| arm | witnessed (floor 0.03390) | flags (floor 1.09091) | conversion (derived floor) | referee | mean/median | impostor win | comparator | win edge |
|---|---|---|---|---|---|---|---|---|
| `ea4bc955…` | 0.15228 PASS† | **0.93548 FAIL** (−0.15542) | **0.36667 FAIL** vs 0.66882 (−0.30215) | **FAIL** | 48.90 / 50.15 | 26/50 = 0.52 | 13/50 = 0.26 | **+0.26** |
| `bfd145cb…` | 0.14778 PASS† | 0.90000 — UNRESOLVABLE (excluded) | **0.35099 FAIL** vs 0.69519 (−0.34419) | **FAIL** (conversion alone) | 47.24 / 48.00 | 28/50 = 0.56 | 13/50 = 0.26 | **+0.30** |
| `6d327dcb…` | 0.22280 PASS† | **0.96914 FAIL** (−0.12177) | **0.44444 FAIL** vs 0.64559 (−0.20115) | **FAIL** | 51.15 / 63.95 | 19/50 = 0.38 | 13/50 = 0.26 | **+0.12** |
| `7f73929d…` (n=49) | 0.22000 PASS† | **0.82840 FAIL** (−0.26251) | **0.38926 FAIL** vs 0.75527 (−0.36601) | **FAIL** | 52.49 / 53.70 | 21/49 = 0.42857 | 12/49 = 0.24490 | **+0.18367** |
| `p18-fsm-comparator` | 0.04598 PASS† | 1.19745 PASS (+0.10654) | 0.55147 PASS vs 0.52250 (+0.02897) | **PASS** | 54.96 / 53.55 | 13/50 = 0.26 | — | — |

† PASS on the floor; the gauge is UNRESOLVABLE for between-arm discrimination on every
arm (§2.2.i) — the PASS stands, and nothing in this ruling rests on it.

**The AND, read [INFERRED over the verified cells]:** every candidate has the win edge
(all four `core.impostor_win_rate` values exceed their paired comparator, +0.12 to
+0.30) and every candidate fails the referee (`watchability.referee_passed: false` on
all four; the comparator is the only PASS). The Phase-17 shape reproduces at baseline 6:
the learned movers still buy wins by starving the flag/conversion economy — the two
supply gauges the §1.3 bar named are exactly the two that fail, on every arm. **No
candidate satisfies referee-PASS AND win-edge. The conjunction fails on the whole
slate.**

## 4. THE RULING (owner) — axis 1

### 4.1 The champion designation (the 18.4 memo §2.4) **[RULED (owner) — ratified at merge]**

The pre-registration defines the champion as *"the SINGLE candidate put to axis 1 of
18.27 (impostor side) … regardless of whether the flip or adoption passes; every other
18.26 finalist counts as archive for clause (d)."* Neither 18.24 (closed STOPPED, §8 a
screening shortlist) nor 18.26 (which computes and quotes, ruling nothing) named one, so
the designation is this memo's:

**The champion candidate put to axis 1 is `ea4bc955…`** (run-02-utility-lambda4
intermediate gen-2). Grounds: it is the arm the phase already operationally froze as
"the frozen impostor champion" (the owner-directed 2026-07-29 crew block records all
four crew diagnostics against it); it is a campaign-trained candidate (the incumbent
control `6d327dcb…` is byte-identical to the already-committed opt-in champion, so
putting the incumbent to the swap question would answer nothing); and among the
campaign-trained arms it is an F13-champion-side selection (promoting a runner-up —
`bfd145cb…` on raw win rate, or `7f73929d…` — would presuppose the hypothesis-A reading
§5 rejects). The designation cannot change the axis-1 outcome (§3: every arm fails the
conjunction), and §3 reads all four against the bar regardless — the designation binds
axis 2's clause-(d) surface (§6.2).

### 4.2 The ruling, verbatim **[RULED (owner) — ratified at merge]**

> **AXIS 1: FAIL — NO-FLIP.** The champion candidate `ea4bc955…` retains the win edge
> (0.52 vs the same-seed FSM comparator 0.26, Δ +0.26) and FAILS the baseline-6 referee
> on both live supply gauges (flags/meeting 0.93548 < 1.09091; testimony-backed
> conversion 0.36667 < its population-relative derived floor 0.66882) — and so does
> every other finalist on the slate (§3). The §1.3 conjunction is unsatisfied as
> measured. Therefore: the scripted FSM STAYS the default mover on every
> default-SELECTOR surface; the committed champion STAYS opt-in and unswapped
> (`utility-es`, sha `6d327dcb…` — no finalist referee-dominates it: none passes the
> referee at all, and the incumbent control carries the least-bad margin on BOTH live
> gauges — flags −0.12177 and conversion −0.20115 against every alternative's
> −0.15542/−0.30215 (`ea4bc955…`), −0.34419 (`bfd145cb…`, conversion alone), and
> −0.26251/−0.36601 (`7f73929d…`, whose higher referee mean rides floor margins
> farther below the bar));
> the ARTIFACT surface under `agents/tactical/learned/` does not move; **18.28 closes
> NO-FLIP** (no mover record, the battery re-run over existing bytes at HEAD — the
> 17.17 shape). The FAIL is the finding, recorded here.

The finding, stated the way §1.3 prices it: the campaign closed neither of the two
named gaps. At baseline 6 the flag economy floor rose with the graduated meeting layer
(0.50279 → 1.09091) and the learned movers' supply stayed below it on every arm
(0.828–0.969 vs the comparator's 1.197), which LIFTS every arm's population-relative
conversion floor (0.646–0.755) far above its measured conversion (0.351–0.444) — the
starved-supply mechanism of the Phase-17 FAIL, reproduced on a co-adapted slate at
n=50. The win edge, meanwhile, is real and larger than Phase 17's (+0.26 on the
champion vs +0.16 then).

### 4.3 The UNRESOLVABLE verdicts read exactly that (inherited (e)) **[RULED (owner) — ratified at merge]**

The nine `witnessed_event_rate` UNRESOLVABLE verdicts and `bfd145cb…`'s flags
UNRESOLVABLE are reported as exactly that — a structural instrument finding at n=50
(the rare-event floor's 25% ceiling is unclearable), not a PASS, not a FAIL, and not a
reason to move anything. **The bar stays as ratified.** Re-pricing the bar (including
any response to the witnessed gauge's structural unresolvability) remains an owner
decision outside this memo, per §1.3's own closing sentence. The unresolvability
finding routes to 18.28's ledger (§12).

### 4.4 The PASS branch, pre-authored and NOT executed **[VERIFIED against the tree]**

The 17.16 both-branches shape, recorded so the ruling is evidence-gated rather than
post-hoc. Had §4.2 read PASS, this PR would have: (a) swapped the ARTIFACT surface —
`agents/tactical/learned/weights.json` + `weights.json.sha256` to the ruled candidate's
committed artifact bytes, the stamp constants in `factory.py`
(`CHAMPION_POLICY_ID`/`CHAMPION_METHOD`/`CHAMPION_ANCHOR_POLICY`) and
`forward.py::ENCODER_VERSION` to the ruled candidate's stamp fields, with the
sha-coherence pins re-pinned; and (b) pre-authored the selector flip for 18.28 — the
DEFAULT-SELECTOR surfaces (`orchestrator/game.py::build_default_agent_factory`,
`scripts/run_tournament.py`'s `--agent-factory` default) flip at 18.28's adopting
record, NOT here (adoption-at-record: a default graduates at the baseline that adopts
it), with the 18.27 pins proving the default NOT yet moved. On the ruled FAIL branch
none of (a) happens and (b) is moot: `agents/tactical/learned/` is untouched by this PR
(`committed_weights_sha256()` still `6d327dcb…`, the crew artifact still `bd6fdd0a…`),
and the default-selector surfaces are provably unmoved —
`tests/scripts/test_champion_flip_ruling.py` re-pins both from committed bytes (§11).

## 5. THE F13 RULING (owner)

### 5.1 What is being ruled **[VERIFIED]**

Inherited from the 18.24 merge: F13 observed that every referee PASS in the campaign
came from a runner-up (0 passes across 14 evaluated champions, 3 across 18 runner-ups,
all at n≤6). The 18.26 pre-registered cell measures the two hypotheses, quoted verbatim
from the contract (`tasks/phase-18.md`, Task 18.26):

> **hypothesis A** (the ES trades evidence-supply for wins; runner-ups sit one step
> less far along the trade — predicts the runner-ups' gauge margins **PERSIST** at
> n=50) … **hypothesis B** (n≤6 referee reads are noise — predicts the
> champion/runner-up gauge gap **VANISHES** at n=50)

The cell: champions (`6d327dcb…`, `ea4bc955…`) vs runner-ups (`bfd145cb…`,
`7f73929d…`) on the referee gauges, on the composition-clean 49-seed intersection (seed
35 removed from all four arms), persisted at `f13_intersection_gauges` on the three
full rows (with `7f73929d…`'s own n=49 `watchability`/`split_half` blocks as its view).
The 18.26 report computes and reports under §11.2's registered noise rule — *"A margin
smaller than either side's split-half noise is reported as such and cannot be read as
support for A"* — and rules nothing. The ruling is this memo's.

### 5.2 The measured cell **[VERIFIED cells; INFERRED pooling — §15]**

Pooled margins (runner-up mean − champion mean) on the 49-seed intersection, with the
pooled-side split-half noises (mean of the two member arms' noise) beside them:

| gauge | champion mean | runner-up mean | margin | champion-side noise | runner-up-side noise | §11.2 |
|---|---|---|---|---|---|---|
| `witnessed_event_rate` | 0.19188 | 0.18538 | **−0.00650** | 0.07001 | 0.06026 | barred by **both** sides |
| `flags_per_meeting` | 0.95481 | 0.86292 | **−0.09189** | 0.17958 | 0.15652 | barred by **both** sides |
| `testimony_backed_conversion` | 0.40412 | 0.36929 | **−0.03483** | 0.06578 | 0.00942 | barred by the **champion** side |

All three margins are NEGATIVE — the runner-ups sit *below* the champions on every
pooled gauge, hypothesis A's opposite — and all three are noise-barred from supporting
A under the registered either-side rule. Corroborating shape: at n=50 there are **zero
referee passes anywhere on the slate** — the three n≤6 runner-up passes (including
`7f73929d…`'s own screening PASS) did not persist. One residual cell survives the
within-lineage read (`ea4bc955…` vs `bfd145cb…`, both run-02, the one
lineage-held-constant pair): `testimony_backed_conversion` difference **−0.02231**,
exceeding `bfd145cb…`'s own intersection noise (0.01504) while sitting inside
`ea4bc955…`'s (0.09459) — one gauge wide, on one pair.

### 5.3 The ruling **[RULED (owner) — ratified at merge]**

> **F13: hypothesis A is REJECTED as unsupported at n=50.** Every pooled
> runner-up-minus-champion margin is negative and noise-barred; every n≤6 runner-up
> referee PASS failed to reproduce at n=50. "A unsupported" ≠ "B demonstrated":
> hypothesis B stands as the OPERATIVE reading — the n≤6 referee reads were noise, the
> F12 lesson now measured at claim scale — without being ruled a demonstrated claim of
> its own (it is the null the evidence fails to reject, and the §10.3 UNRESOLVABLE
> census prices how much this instrument can say at any n this phase recorded).
> **Consequence: no selection-rule defect is demonstrated, so no next-campaign/Phase-19
> selection-rule FIX contract routes from F13.** The residual within-lineage conversion
> cell (−0.02231, one gauge wide, one pair) is recorded to 18.28's ledger as an
> observation — the only trace of the A-shape that survives, below any claim grade.

---

# PART B — AXIS 2: EMERGENCE

## 6. The discipline and the ruling surface

### 6.1 What is ruled, and how **[VERIFIED]**

This memo reads against `audits/audit-phase-18-emergence-preregistration.md` verbatim:
the §2.2 enumeration ("the 13 rows above, with `action-entropy` ruled once per side —
**14 rulings total**"), the §6 four-part conjunctive discipline ((a) pooled |z| ≥ 1.96
vs the same-seed FSM comparator arm on the registered denominator fields — Fisher for
the correlation cell, Welch for mean cells; (b) 2-of-3 `seed mod 5` sign reproduction;
(c) a named `ablation:<instrument-key>/<lever-id>` showing the two-condition recede;
(d) selected-for on the champion's own recordings; watchability never a claim), the §7
advisory rule (a four-part pass rules EMERGENT regardless of the advisory flag; a
baseline-anchored advisory read never rules), and §6.a's registered no-claim reads (a
pooled rate of 0 or 1 admits no z — "the honest no-claim read, not a pass"; an entropy
claim is "unjudgeable from committed outputs and reads NOT-DEMONSTRATED as recorded"
until the variance field lands — it never did).

### 6.2 The clause-(d) surface **[RULED (owner) — carried from §4.1]**

The champion is `ea4bc955…` (§4.1), so the candidate arm for every clause-(a)/(b) read
is `p18-imp-ea4bc955` against the full-50 comparator cells, and **every other 18.26
finalist arm is archive for clause (d)** — the `6d327dcb…`/`bfd145cb…`/`7f73929d…`
deltas are archive observations (§8.4), reportable and never EMERGENT. Crew side: the
candidate named in the crew-adoption slot is `0bf179b7…` (§10); every crew axis-2
column reads NOT-DEMONSTRABLE for want of a §2.1 opponent-matched comparator — labeled,
not recorded, per the owner's 2026-07-31 decision — so no crew cell reaches clause (a)
at all. Roll-call cells are CONTEXT, not a ratified instrument (the pre-registration's
§2.5; its §9 amendment log is empty), and nothing here rules on them.

### 6.3 The clause-(c) ablation ledger — complete on ZERO of the five campaign runs **[VERIFIED]**

Quoted from the committed campaign reports, per run:

| run | named ablation | state as recorded |
|---|---|---|
| run-01-utility-champion | `ablation:*/conviction-term` (fake path, `master_seed=182401`, `training/artifacts/coevo/ablation-run-01-conviction-term/`) | RUN, but **a recede read is impossible by construction** — the twin reproduces the impostor champion lineage sha-for-sha (F6) |
| run-02-utility-lambda4 | `ablation:*/anchor-lambda=4.0` (fake path, `master_seed=182402`, `…/ablation-run-02-anchor-lambda/`) | RUN on the fake path only; the real-path half was never run (the §5.3 deflection candidate resolved NOT-SUSTAINED at tranche 2) |
| run-03-utility-bcanchor | — | **no ablation recorded** |
| run-04-freepolicy-v3 | `ablation:off-menu/encoder-v3` (fake + real legs, `master_seed=182404`, `…/ablation-run-04-encoder-v3/` + `…/realpath-ablation/ablation-run-04-encoder-v3/`, seeds 4000–4002) | RUN; the recede verdict is a tranche-1 **n=3 screen** (no recession observed), tranche 2 (4003–4005) VALIDITY-FAILED and never re-recorded before the §4.0 stop; classification deferred to this memo — resolved in §8.2 |
| run-05-freepolicy-v2-founders | — | **no ablation recorded** |

Crew campaigns: two conviction-term twins (`ablation-run-c{1,2}-conviction-term/`,
`master_seed` 182501/182502) — limb (c) PARTIAL on both, the recede recording
deliberately withheld under the F12 stop (§8.1). **Clause (c) is complete on zero of
the five impostor campaign runs and zero of the two crew runs as recorded.** By the
registered rule, an unablated candidate reads NOT-DEMONSTRATED by construction.

## 7. The fourteen rulings **[RULED (owner) — ratified at merge; every cell VERIFIED, every statistic INFERRED with inputs shown — §15]**

Candidate arm = `p18-imp-ea4bc955` (champion, §6.2); comparator arm =
`p18-fsm-comparator` (full-50 pairing). Clause (b) reads the committed
`instruments.seed_mod5_splits` views on both arms (splits of 30/10/10 games); "n/3" is
sign-reproduction of the pooled delta's sign, per-split deltas in §15. Clause (c) reads
§6.3. Clause (d) is satisfied by construction wherever (a) is read on the champion's
arm.

| # | ruling (instrument · cell) | champion arm | comparator arm | clause (a) | clause (b) | clause (c) | **RULING** |
|---|---|---|---|---|---|---|---|
| 1 | `false-vouch` · saw_player rate | 26/206 = 0.12621 | 20/196 = 0.10204 | z = +0.761 — fails | 2/3 (moot) | none | **NOT-DEMONSTRATED** |
| 2 | `false-vouch` · corroboration rate | 12/54 = 0.22222 | 6/54 = 0.11111 | z = +1.549 — fails | 3/3 (moot) | none | **NOT-DEMONSTRATED** |
| 3 | `false-vouch` · fabricated share (advisory) | 5/21 = 0.23810 | 9/19 = 0.47368 | z = −1.560 — fails | 3/3 (moot) | none | **NOT-DEMONSTRATED** |
| 4 | `frame` · attempt meeting rate | 151/155 = 0.97419 | 148/157 = 0.94268 | z = +1.393 — fails | 2/3 (moot) | none | **NOT-DEMONSTRATED** |
| 5 | `frame` · conversion rate (advisory) | 10/151 = 0.06623 | 6/148 = 0.04054 | z = +0.987 — fails | 3/3 (moot) | none | **NOT-DEMONSTRATED** |
| 6 | `teammate-immunity` · teammate-accusation rate (advisory) | 0/214 | 0/190 | pooled rate 0 — **no z exists, no delta** (the §6.a honest no-claim read) | 0/3 (all zero) | none | **NOT-DEMONSTRATED** |
| 7 | `alibi-survival` · fabricated-alibi survival (advisory) | 26/33 = 0.78788 | 23/30 = 0.76667 | z = +0.202 — fails | 2/3 (moot) | none | **NOT-DEMONSTRATED** |
| 8 | `deflection` · deflection efficacy | 42/95 = 0.44211 | 23/59 = 0.38983 | z = +0.639 — fails | 2/3 (moot) | none | **NOT-DEMONSTRATED** |
| 9 | `kill-craft` · crew-witnessed-kill rate | 30/197 = 0.15228 | 8/174 = 0.04598 | **z = +3.370 — passes** | **3/3 — passes** | **UNABLATED** (no nameable lever — §8.3) | **NOT-DEMONSTRATED** (fails (c) by construction) — named finding N1, §8.3 |
| 10 | `kill-craft` · within-one-hop point-biserial | r = 0.21108 @ 197 | r = 0.27505 @ 174 | Fisher z = −0.648 — fails | 2/3 (moot) | none | **NOT-DEMONSTRATED** |
| 11 | `kill-craft` · co-present-kill departure rate | 20/197 = 0.10152 | 0/174 = 0.0 | **z = +4.321 — passes** | **3/3 — passes** | **UNABLATED** (no nameable lever — §8.3) | **NOT-DEMONSTRATED** (fails (c) by construction) — named finding N2, §8.3 |
| 12 | `off-menu` · off-menu rate | 0/2015 | 0/2299 | pooled rate 0 — no z exists; **vacuous by construction** for the menu-bounded champion | 0/3 (all zero) | §6.3 run-04 screen (archive material — §8.2) | **NOT-DEMONSTRATED** |
| 13 | `action-entropy` · impostor mean conditional entropy | 0.60780 (100 agents / 2015 decisions) | 0.66839 (100 / 2299) | **unjudgeable** — the §6.a per-agent variance field never landed; the registered rule forbids out-of-report recomputation | context only | none | **NOT-DEMONSTRATED as recorded** |
| 14 | `action-entropy` · crew mean conditional entropy | 0.74780 (350 / 6128) | 0.88099 (350 / 7767) | **unjudgeable** — same routed variance gap; additionally the registered crew claim surface (a learned crew) has no §2.1 comparator in the slate (✥ label, §6.2) | context only | none | **NOT-DEMONSTRATED as recorded** |

**Tally: 0 EMERGENT, 14 NOT-DEMONSTRATED.** Eleven rulings fail clause (a) outright or
admit no delta; rulings 9 and 11 pass (a), (b), and (d) and fail only on the missing
ablation — they are the phase's two named behavioral findings (§8.3), ruled honestly
under the registered discipline rather than crowned; rulings 13–14 are unjudgeable as
recorded per the pre-registration's own routed-gap rule. The advisory flags on rulings
3, 5, 6, 7 changed nothing: every read above is the arm-vs-arm §6 discipline, and no
baseline-anchored read rules anywhere in this memo.

## 8. Campaign-surfaced candidate behaviors and archive observations, ruled

### 8.1 The conviction-term claim (from the 18.25 merge) **[RULED (owner) — ratified at merge]**

The "conviction term produces meeting-seeking crew" claim arrives NOT-DEMONSTRATED with
its limb states recorded: limb (a) unsatisfiable at n=3; limb (c) PARTIAL — the twins
establish the lever's selection-relevance, and the recede recording was deliberately
withheld under the F12 stop. **Ruled: NOT-DEMONSTRATED at this phase's budget**, with
the attribution fences honored in full: per F6 (extended, not contradicted, by 18.25's
paired twins) the term's demonstrated selection locus is **crew-side on both bases**
with a base-dependent channel (direct selection reordering where meetings are scarce;
exploiter-novelty where meetings are rich), and **no ruling in this memo attributes any
impostor-side selection effect to the conviction term** — not on the run-01 lineage
(the sha-for-sha twin) and not on the `ea4bc955…`-seeded lineages (18.25's bound). The
recede recording, if the claim is ever pursued, belongs to a 50-seed venue as a routed
contract (§12), never a retrofit into this phase.

### 8.2 The off-menu free-policy departure (from the 18.24 merge) **[RULED (owner) — ratified at merge]**

The campaign's largest cell movement — off-menu rate 79/101 = 0.782 (`27f852fe…`, v3
gen-9 hall champion) and 114/120 = 0.950 (`348df066…`, gen-3) against a structural-0
baseline — with the run-04 `ablation:off-menu/encoder-v3` screen deferred to this memo
for clause-(c) classification. **Ruled: NOT-DEMONSTRATED**, on two independent limbs:
**(d) fails** — the behavior lives in archive arms only (`27f852fe…` is a named
non-finalist exhibit; no free-policy arm is the champion, and the champion is menu-bounded,
for which the instrument is vacuous by construction); **(c) is incomplete** — the
recorded ablation is a tranche-1 n=3 screen (no recession observed: the v2-reverted
champion still steps off-menu at 0.61, consistent with the action space rather than the
encoder being the enabler), tranche 2 VALIDITY-FAILED and never re-recorded, so the
registered recede criterion was never evaluated at claim grade. The classification the
18.24 report deferred is hereby resolved: **the ablation reads UNFINISHED-as-recorded,
and no causal attribution (encoder-v3 vs action space) is made.** The standing exhibit
offer (inherited (d)) is **declined**: no off-menu emergence claim is pursued this
phase, so the `27f852fe…` claim-grade denominators are not wanted by this reading; the
exhibit and the family gradient (utility 0.0 → v2 ≈ 0.36–0.39 → v3 ≈ 0.88–0.95) route
to 18.28's ledger as the free-policy family's context.

### 8.3 The two named findings (rulings 9 and 11), and the family-wide cells **[RULED (owner) — ratified at merge]**

**N1 — the learned mover kills into witnesses at ~3.3× the scripted rate.**
Crew-witnessed-kill rate 30/197 = 0.15228 vs the comparator's 8/174 = 0.04598
(z = +3.370, sign-reproduced 3/3). **N2 — the learned mover emits a kill class the
scripted FSM cannot: co-present kills.** 20/197 = 0.10152 vs 0/174 (z = +4.321, 3/3;
the committed FSM kills only when alone — 0 co-present kills on all 863 corpus-pinned
kills and 0/174 here). Both are selected-for (present on the champion's own arm — and,
as archive corroboration, on every learned arm of the slate: witnessed 0.147–0.220,
co-present departure 0.076–0.187). Both are **NOT-DEMONSTRATED under the registered
discipline** because clause (c) is unsatisfiable by construction: the behaviors appear
on the un-levered incumbent control (`6d327dcb…`: witnessed 43/193, co-present 36/193),
so no campaign lever enables them and no `ablation:kill-craft/<lever-id>` exists to
name — the live hypothesis is learned-vs-scripted mover class, not a lever effect. They
are recorded as the phase's two named behavioral findings, routed to 18.28
(findings-not-failures, locked decision 4's "missing both closes as a measured
finding"); a §6.c-satisfiable claim would need a lever-scoped training contract in a
future campaign (§12). The same construction disposes of the remaining 18.24-surfaced
cells on this memo's reading: the family-wide deflection depression (20/96 = 0.208
pooled vs corpus 0.4539) and the pooled alibi-survival 31/31 context cell — both
present on the un-levered control, both **NOT-DEMONSTRATED by construction** (neither
reaches claim shape on the champion's own 18.26 arm either: rulings 7–8 fail (a)); and
the `10c1f9f3…` deflection candidate, which resolved NOT-SUSTAINED at tranche 2 before
reaching this reading (**NOT-DEMONSTRATED**, no live candidacy).

### 8.4 Archive observations (clause (d) fails; recorded, never EMERGENT) **[INFERRED from verified cells]**

On non-champion finalist arms, three cells clear the clause-(a) bar with 3/3 sign
reproduction and would still fail clause (c): `6d327dcb…` saw_player false-vouch rate
40/213 = 0.18779 vs 20/196 (z = +2.449), corroboration false-vouch rate 30/71 = 0.42254
vs 6/54 (z = +3.809), and within-one-hop point-biserial r = 0.52142 @ 193 vs 0.27505 @
174 (Fisher z = +2.808); `7f73929d…` corroboration rate 20/60 = 0.33333 vs 6/53
(z = +2.774, 2/3). These are archive observations under §2.4 — the incumbent lineage
vouches false at a higher rate and places kills nearer witnesses than the comparator —
reportable to the close, never EMERGENT. The 18.26-flagged borderline corpus-anchored
reads (e.g. `6d327dcb…` frame attempts vs the corpus anchor at z = +1.9601) rule
nothing: corpus-anchored reads are the sweep-context frame, and this memo's claims are
arm-vs-arm only.

## 9. The two post-hoc-criterion questions, answered **[RULED (owner) — ratified at merge]**

18.26 put exactly two questions to this memo — the equivalence margin ("gen-9 ≈ gen-0"
was never operationalized) on the rider and conversion pairs — and nothing else; every
other cell reads through pre-registered semantics.

> **No post-hoc equivalence criterion is adopted.** Writing an equivalence margin after
> seeing the data is the fitted-bar move the pre-registration exists to prevent (the
> 18.4 §8 rejection of "defer the bars to campaign time", applied to its own gap). Both
> cells therefore read as measured, as NULLS, not equivalences: the rider pair
> (`kill_craft_rider_intersection`: gen-9 30/191 = 0.15707 vs gen-0 33/200 = 0.16500,
> margin −0.00793, 95% CI [−0.0808, +0.0649]) and the conversion pair
> (`conversion_paired_49_seed`: 20 both-win / 6 gen-9-only / 5 gen-0-only / 18
> neither-win; McNemar exact p = 1.0) are **INCONCLUSIVE as recorded** — at n=49 per
> side they cannot distinguish "no learning effect" from "an effect this study is too
> small to see", and they support neither adoption nor an equivalence claim. If a
> future phase wants an equivalence read on a generation pair, the margin is
> pre-registered there before recording (routed note, §12).

**The routed rider question resolves against crew learning.** The crew-witnessed-kill
elevation (6.5×–15× corpus across the 18.25 arms) appears at BOTH generations against
the same learned opponent (0.157 gen-9, 0.165 gen-0 — the untrained control) while the
scripted-vs-scripted comparator reads 8/174 = 0.046 and the corpus 0.0238–0.0334: the
elevation tracks the **opponent**, and the champion's own arm carries the mechanism
(findings N1/N2 — learned-impostor kill placement). It is an impostor-side behavioral
departure, not a learned-crew observation effect; the crew-side claim column stays
NOT-DEMONSTRABLE (✥) regardless (§6.2).

## 10. THE CREW-ADOPTION SLOT (owner) — put and recorded explicitly

The contract requires this slot put explicitly, never folded silently into either axis.

**The slot [RULED (owner) — ratified at merge]:** the crew candidate considered is
`0bf179b7…` (run-c1-crew-owned-tasks gen-9, `crew-option-features-v2` — the only crew
arm on the slate with a PASS validity gate). The evidence, in full: 18.25 named **no
crew finalist** ("no crew finalist clears the bars … a ranked list would launder §4.0
noise into a hand-off") and 18.25 supplies nothing that clears a bar (inherited (f) —
the crew-adoption slot rests on 18.26 evidence alone); the 18.26 crew block is
owner-directed DIAGNOSTIC (2026-07-29); on that diagnostic the c1 pair reads null at
n=49 (win conversion 26/50 = 0.52 vs its same-opponent gen-0 control — paired margin +1
game, McNemar p = 1.0; rider margin −0.00793, §9), the c2 lineage is gate-invalid at
both generations (gen-9 meeting rate at the 0.60 floor with two learned deterministic
stalemates; gen-0 total starvation, zero LLM calls), and no crew arm has a §2.1
comparator for any axis-2 claim.

> **RULING: NO-ADOPTION — no crew-adoption question survives the evidence to be put
> beyond this slot.** The crew surface stays opt-in (`learned-crew`) on the committed
> `crew-owned-tasks-es` artifact (`bd6fdd0a…`), unswapped. The routed
> scripted-crew-vs-`ea4bc955…` comparator arm (the owner-optional follow-up 18.26
> recorded for "if 18.27 wants crew claims") is **DECLINED for this phase** — this memo
> pursues no crew-side axis-2 claim, so recording the arm now would be evidence
> assembled after the ruling it would serve; the routed contract stays available to a
> future phase through 18.28's ledger (§12).

---

# SHARED — IMPLEMENTATION, LEDGER, DECISIONS

## 11. The ruled branch implemented (FAIL) — what moved in the tree

This PR moves **no artifact and no default**: `agents/tactical/learned/` is untouched
(the FAIL branch's swap clause is empty — §4.2: no finalist referee-dominates the
committed champion), `orchestrator/game.py::build_default_agent_factory` and the
`scripts/run_tournament.py` default path are untouched, and `tasks/phase-18.md` gains
only the ruling's banner note. The ruling is pinned from committed bytes in
`tests/scripts/test_champion_flip_ruling.py` (the 18.27 section appended beside the
standing 17.16 pins, which re-run green unchanged):

- **the axis-1 ruling re-derived** — for each of the four candidate rows: stamp
  preconditions (games stamp-verified, stamp == committed sidecar, validity PASS,
  baseline-6), `referee_passed` false with the §3 floor cells pinned, the win edge
  against the comparator row (13/50 = 0.26; the 49-seed intersection 12/49 = 0.24490
  re-derived from the comparator's own per-game reasons for `7f73929d…`), and the
  conjunction failing on every arm;
- **the mechanics pinned** — `witnessed_event_rate` split-half noise above its 25%
  ceiling on all nine arms; `bfd145cb…`'s flags noise 0.29291 > 0.27273 with its FAIL
  resting on conversion alone;
- **the F13 cell pinned** — the three pooled margins negative and below the either-side
  noise bar, re-derived from `f13_intersection_gauges` + `7f73929d…`'s n=49 blocks;
- **the axis-2 tally pinned** — the champion-arm clause-(a) statistics re-derived from
  the persisted cells (the two passing z values and every failing one), the split-sign
  counts for the two named findings, and the 0-EMERGENT / 14-NOT-DEMONSTRATED tally;
- **the FAIL branch pinned** — the default-selector surfaces still select the scripted
  FSM, the absent-stamp fallback is untouched, and the opt-in artifacts are unswapped
  (`committed_weights_sha256()` == `6d327dcb…`, `committed_crew_weights_sha256()` ==
  `bd6fdd0a…`).

## 12. Hand-off ledger to 18.28 (routed items — every deferral named)

1. **NO-FLIP close path** (§4.2): no mover record; the battery re-runs over existing
   bytes at HEAD; the 17.17 "resist recording anything" discipline holds.
2. **The witnessed-gauge structural unresolvability** (§4.3): the rare-event floor's
   25% ceiling is unclearable at n=50 on every arm — an instrument finding for the
   close; any bar re-pricing is an owner decision outside this memo.
3. **F13 residual** (§5.3): the within-lineage conversion cell (−0.02231, one gauge,
   one pair) — an observation, no contract.
4. **Findings N1/N2** (§8.3): learned-impostor kill placement (witnessed ×3.3,
   co-present departure from a structural 0) — selected-for, split-reproduced,
   unablatable this phase; a §6.c-satisfiable claim needs a lever-scoped contract in a
   future campaign.
5. **F11 disposition** (inherited (c)): encoder v3 trained 3.8× worse than its v2
   ablation twin at the 12-generation budget (champion fitness 3.06 vs 11.61) — the
   measurement is input here, no ruling; the keep/drop disposition routes to the
   close's hand-off ledger with the off-menu family context (§8.2).
6. **The conviction-term recede recording** (§8.1): withheld under F12; belongs to a
   50-seed venue as a routed contract if the claim is pursued.
7. **The scripted-crew-vs-`ea4bc955…` comparator arm** (§10): declined this phase;
   stays available as a routed contract for any future crew claim.
8. **Equivalence margins** (§9): pre-register before recording in any future phase that
   wants a generation-pair equivalence read.
9. **The entropy variance field** (§7, rulings 13–14): the 18.4-routed
   `ActionEntropyCells` per-agent variance contract remains unlanded; entropy claims
   stay unjudgeable until it lands with re-pins.
10. **Cycling-detector inputs** (inherited (f), context): Red-Queen signature PRESENT
    on the general-base impostor (flat anchor + oscillating co-matchup); the owned-task
    crew reads progress, its impostor plateaus — context for whatever Phase 19
    inherits.

## 13. THE RATIFIED DECISIONS (owner) — ratified by the merge of this task's PR

**Axis 1 (Part A — separable):**

- **A1 — the champion designation:** `ea4bc955…` is the single candidate put to axis 1
  (§4.1); every other finalist is archive for clause (d).
- **A2 — THE FLIP RULING: FAIL — NO-FLIP** (§4.2, verbatim there): the scripted FSM
  stays the default mover, the champion stays opt-in and unswapped, the artifact
  surface does not move, 18.28 closes NO-FLIP; UNRESOLVABLE verdicts read exactly that
  and the bar stays as ratified (§4.3).
- **A3 — THE F13 RULING** (§5.3, verbatim there): hypothesis A rejected as unsupported;
  hypothesis B operative, not demonstrated; no selection-rule fix contract routes.

**Axis 2 + slots (Part B — separable):**

- **B1 — THE EMERGENCE RULINGS:** the fourteen §7 rulings, 0 EMERGENT / 14
  NOT-DEMONSTRATED, with N1/N2 recorded as the phase's named behavioral findings
  (§8.3), the conviction-term and off-menu candidates ruled NOT-DEMONSTRATED with the
  attribution fences honored (§8.1–§8.2), and the archive observations recorded as
  archive (§8.4).
- **B2 — the post-hoc questions:** no post-hoc equivalence criterion; both paired cells
  INCONCLUSIVE as recorded; the rider resolves toward learned-impostor kill placement
  (§9).
- **B3 — THE CREW-ADOPTION SLOT: NO-ADOPTION** (§10, verbatim there); the routed
  comparator arm declined for this phase.

- **Rejected — naming the top win-rate arm (`bfd145cb…`) champion:** promoting a
  runner-up on raw wins would bypass the campaign's selection rule on the strength of
  the hypothesis-A reading A3 rejects, and its axis-1 read is the weakest on the slate
  (referee FAIL resting on the one gauge whose flags cell is UNRESOLVABLE).
- **Rejected — ruling N1/N2 EMERGENT on three of four clauses:** the discipline is
  conjunctive by ratification; "there is no 'partially emergent'". The findings route
  as findings.
- **Rejected — recording the missing crew comparator arm to enable crew claims:**
  evidence assembled after the ruling it would serve (the owner's own 2026-07-31
  labelling decision, extended to this memo's scope).
- **Evidence:** §3 (the floor cells and win edges), §5.2 (the F13 cell), §7 (the
  fourteen rulings' cells and statistics), §8–§10 (the surfaced candidates, questions,
  and slot), §15 (reproduction).

## 14. Amendment log and limits

| date | what changed | why | ratification vehicle |
|---|---|---|---|
| — | (none) | — | — |

Limits, stated honestly: every axis-2 clause-(a) statistic above is computed at the
18.26 arm scale (one 50-seed arm per side) — the §7 powering table of the
pre-registration prices what that can and cannot see, and nothing here reads beyond it;
the witnessed gauge cannot discriminate between arms at this n (§2.2.i); the crew
columns are unjudgeable for want of a comparator, by design of the ratified slate; and
no cell in this memo was recomputed outside its committed report fields.

## 15. Method + reproduction (all $0 against committed bytes, offline)

The evidence rows and persisted cells:

```bash
uv run pytest tests/training/test_finalist_eval_pins.py -q   # the 18.26 row pins
uv run pytest tests/scripts/test_champion_flip_ruling.py -q  # the 17.16 pins + THIS ruling's pins
```

Every derived statistic in this memo, from the quoted cells only (the §6.a registered
formulas; `pooled_z(k_c, n_c, k_f, n_f)` and `fisher_z` exactly as defined in
`audits/audit-phase-18-emergence-preregistration.md` §10):

```python
# §3 win edges (core.impostor_win_rate minus the paired comparator rate):
0.52 - 13/50        # ea4bc955   -> +0.26
0.56 - 13/50        # bfd145cb   -> +0.30
0.38 - 13/50        # 6d327dcb   -> +0.12
21/49 - 12/49       # 7f73929d   -> +0.18367  (12/49 = 0.24490, §1.3/§2.2.iii)

# §1.2 per-arm derived conversion floors (the 16.11 derivation, baseline-6 pins):
min(1.0, (78/136) * ((180/165) / 0.9354838709677419))   # ea4bc955 -> 0.6688179974
min(1.0, (78/136) * ((180/165) / 0.9))                  # bfd145cb -> 0.6951871658
min(1.0, (78/136) * ((180/165) / 0.9691358024691358))   # 6d327dcb -> 0.6455941960
min(1.0, (78/136) * ((180/165) / 0.8284023668639053))   # 7f73929d -> 0.7552711994
min(1.0, (78/136) * ((180/165) / 1.197452229299363))    # comparator -> 0.5224997156

# §2.2 noise ceilings (25% of threshold): witnessed 0.25*6/177 = 0.00847;
# flags 0.25*180/165 = 0.27273; bfd145cb flags noise 0.29291 > 0.27273 (7% over).

# §5.2 F13 pooled margins (means of the f13_intersection_gauges measured cells;
# 7f73929d's n=49 watchability/split_half blocks are its view):
(0.1507537688 + 0.22) / 2 - (0.2275132275 + 0.15625) / 2        # witnessed -> -0.00650
(0.8974358974 + 0.8284023669) / 2 - (0.9559748428 + 0.9536423841) / 2  # flags -> -0.09189
(0.3493150685 + 0.3892617450) / 2 - (0.4366197183 + 0.3716216216) / 2  # conversion -> -0.03483
# side noises = mean of member-arm split-half noises:
(0.0750329092 + 0.0649932766) / 2   # champion witnessed  -> 0.07001
(0.0338056680 + 0.0867121638) / 2   # runner-up witnessed -> 0.06026
(0.2213431786 + 0.1378164557) / 2   # champion flags      -> 0.17958
(0.2957583760 + 0.0172752809) / 2   # runner-up flags     -> 0.15652
(0.0945945946 + 0.0369634340) / 2   # champion conversion -> 0.06578
(0.0150375940 + 0.0038043478) / 2   # runner-up conversion-> 0.00942
0.3493150685 - 0.3716216216         # within-lineage conversion -> -0.02231

# §7 clause (a), champion arm vs full-50 comparator arm:
pooled_z(26, 206, 20, 196)   # 1  saw_player          -> +0.761
pooled_z(12, 54, 6, 54)      # 2  corroboration       -> +1.549
pooled_z(5, 21, 9, 19)       # 3  fabricated share    -> -1.560
pooled_z(151, 155, 148, 157) # 4  frame attempts      -> +1.393
pooled_z(10, 151, 6, 148)    # 5  frame conversions   -> +0.987
pooled_z(0, 214, 0, 190)     # 6  teammate            -> None (no delta exists)
pooled_z(26, 33, 23, 30)     # 7  alibi survival      -> +0.202
pooled_z(42, 95, 23, 59)     # 8  deflection          -> +0.639
pooled_z(30, 197, 8, 174)    # 9  witnessed kills     -> +3.370  (passes)
fisher_z(0.21108484573789452, 197, 0.2750500467059708, 174)  # 10 -> -0.648
pooled_z(20, 197, 0, 174)    # 11 co-present departure-> +4.321  (passes)
pooled_z(0, 2015, 0, 2299)   # 12 off-menu            -> None (vacuous)
# 13/14: unjudgeable — no committed per-agent variance field (18.4 §6.a).

# §7 clause (b) per-split deltas for the two passing cells (seed_mod5_splits,
# candidate minus comparator; splits 30/10/10 games):
# 9  witnessed kills:     16/121-6/102, 9/39-1/36, 5/37-1/36   -> +0.0734, +0.2030, +0.1074 (3/3 +)
# 11 co-present departure: 12/121-0/102, 4/39-0/36, 4/37-0/36  -> +0.0992, +0.1026, +0.1081 (3/3 +)

# §8.4 archive observations (non-champion arms; 7f73929d vs the 49-seed
# intersection comparator cells):
pooled_z(40, 213, 20, 196)   # 6d327dcb saw_player    -> +2.449
pooled_z(30, 71, 6, 54)      # 6d327dcb corroboration -> +3.809
fisher_z(0.5214210511506046, 193, 0.2750500467059708, 174)  # 6d327dcb one-hop -> +2.808
pooled_z(20, 60, 6, 53)      # 7f73929d corroboration -> +2.774
```

Provenance of the substrate: baseline 6 (the 18.12 adopting record), the 18.26 rows
merged at `384effc` (#317), recorded 2026-07-29..31 at recording git shas quoted per
row, `Qwen/Qwen3.6-27B` via Featherless, $0. This memo edits no code, no floors, no
eval modules; its companions in this PR are the ruling pins
(`tests/scripts/test_champion_flip_ruling.py`) and the phase-doc banner note
(`tasks/phase-18.md`).
