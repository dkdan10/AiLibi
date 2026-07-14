# Phase-17 absence gate — the graduation + vent-widening ruling (Task 17.7)

**Date:** 2026-07-14 (evidence sections and the §6 bar proposal assembled and quoted BEFORE the
ruling was requested — the 15.18 pause shape: evidence first, decision slots explicit).
**Task:** 17.7 — THE ABSENCE GATE: graduation + vent-widening ruling (owner) + phase-doc surgery.
**What is being ruled:** THREE couplings, together (`audits/audit-phase-16-close.md` §0.1.4 routes
them as one decision): (1) graduate the `absence_prior` lever at a Phase-17 adopting record, or
stay OFF; (2) ship or hold the PR #264 vent-placement widening (a widening that ships travels WITH
the graduation record — it is meeting-layer); (3) under stay-OFF, the Phase-18 routing note. The
close never defined a graduation bar — §6 proposes a numeric one so the ruling is a criterion,
never a vibe.
**Method:** every evidence row below is a committed, test-pinned cell quoted with its source file
and line — zero fresh measurement (the gate reads Wave-0's already-merged evidence: 17.4's uptake
breakdown, 17.5's widened counterfactual, and the 16.17-era counterfactual re-pins). The one
derived composition in §6 is arithmetic over quoted cells with the formula shown beside it.
**Label key:** **[VERIFIED]** read directly in a committed source/artifact · **[INFERRED]**
reasoned from verified cells (arithmetic quoted) · **[PROPOSED]** a recommendation the owner
ratifies or amends.

## 0. Verdict in one line

**STAY-OFF, widening HOLD, Phase-18 routing recorded** (owner, 2026-07-14, §7): the proposed bar
fails on both clauses (new-over-gate 53/179 = 0.296 > 0.20; crew roll-call coverage 0.4624 <
0.60), the widening moves neither decision cell (53 → 53, 114 → 114), and the corpus re-record
(17.9) is UNBLOCKED at the baseline-5 meeting layer — the surgery below removes 17.8 per the 16.2
discipline and the mover record at 17.17 stays **baseline 6**.

## 1. What this gate re-opens — the §0.1.4 stay-OFF ruling and its evidence bar [VERIFIED]

`audits/audit-phase-16-close.md` §0.1.4 recorded the lever's stay-OFF at baseline 5 on the
ADOPTING-ERA (baseline-4) set-size evidence, and named the calibration confound:

> re-measured on baseline 4 and pinned in
> `tests/agents/test_absence_prior.py::TestAbsencePriorOnCommittedBytes` (re-pinned at `1c70d35`),
> **154/160 meetings carry a non-empty absent set** (median 4, max 8; histogram
> `{0:6,1:15,2:24,3:27,4:37,5:31,6:12,7:1,8:7}`), lever-ON creates a NEW at-or-over-the-gate
> candidate in **39/160** meetings and churns a voter's top rendered candidate in **106/160**.
> The pinned suite's own comment names the cause: the absent set is large because the 16.15
> roll-call elicitation did not exist in the recorded substrate — the lever is calibrated to
> work WITH roll-call (answering roll-call removes a player from the absent set) […]

The routed action this gate now executes: *"Phase 17 re-runs the set-size counterfactual on THIS
record's bytes (roll-call live) and graduates at its own adopting record if the post-roll-call
absent set supports it."* The PR #264 substrate-widening question was *"Declined for now,
recorded here"* and routed WITH the absence lever — *"widening shrinks the absent set and
prevents double-counting a vent-sighted player as also 'absent'; it interacts with the same
calibration this ruling declines to guess at."* Both halves are ruled together below.

## 2. Evidence row 1 — the baseline-5 counterfactual — source: `tests/agents/test_absence_prior.py::TestAbsencePriorOnCommittedBytes` (re-pinned at the PR #272 merge `937ed08`) [VERIFIED]

| cell | baseline 4 (§0.1.4 — context, different bytes) | **baseline 5 (committed pin)** | source line |
|---|---|---|---|
| meetings walked | 160 | **179** | :1343 |
| non-empty absent sets | 154/160 = 0.963 | **163/179 = 0.911** | :1355 |
| absent-set histogram | `{0:6,1:15,2:24,3:27,4:37,5:31,6:12,7:1,8:7}` | **`{0:16,1:23,2:26,3:39,4:32,5:28,6:11,7:4}`** | :1373–1382 |
| median / max | 4 / 8 | **3.0 / 7** | :1383–1385 |
| new at-or-over-the-gate candidate minted | 39/160 = 0.244 | **53/179 = 0.296** | :1396 |
| top rendered-candidate churn | 106/160 = 0.663 | **114/179 = 0.637** | :1409 |

The baseline-4 column is quoted as ladder context only — different bytes, different substrate,
never same-substrate deltas. The suite's own comments carry the reads:

> 163 of the 179 meetings still have at least one publicly-unplaced living player, but the sets
> are SMALLER now the 16.15 roll-call elicitation is LIVE and populates whereabouts claims
> (mean |absent| ~3.09 / median 3.0, down from baseline-4's ~3.6 / 4.0). (:1350–1354)

> The new-must-vote channel: in 53 meetings the lever ON creates at least one NEW
> at-or-over-the-rendered-gate candidate (for some voter) that OFF had under it. Absence only
> lifts, so no recorded conviction is ever lost — this is a pure ADDITION of vote-worthy
> candidates. (:1392–1395)

> In 114 meetings some voter's §4.6 TOP candidate (argmax by rendered suspicion, ties by sorted
> id) CHANGES identity under the lever — high because a near-neutral graph is tie-broken by id,
> so a fresh 0.58 absence row readily becomes (or displaces) the rendered argmax. (:1401–1404)

**The read:** live roll-call shrank the SETS (median 4 → 3, max 8 → 7) but did NOT shrink the
gate-relevant channels — the new-must-vote proportion ROSE (0.244 → 0.296, context read) and
churn is ~flat (0.663 → 0.637). The close's theory (roll-call calibrates the lever by shrinking
the absent set) delivered the shrinkage but not the calibration.

## 3. Evidence row 2 — who is not answering (17.4's uptake breakdown) — source: `eval/funnel.py` pooling folds + `tests/eval/test_funnel_pooling.py` committed pins (PR #273 merge `901afc8`) [VERIFIED]

| cell (9p2i unless noted) | committed pin | source line |
|---|---|---|
| roll-call coverage mean (the close's aggregate, reproduced) | 0.3628558127161479 | test_funnel_pooling.py:642 |
| **crew** coverage mean | **0.46238361266294226** | :712–714 |
| **impostor** coverage mean | **0.0893854748603352** | :715–717 |
| placed totals (crew / impostor) | 331 / 29 | :704–705 |
| claims by surface (opening / reply / opt-in) | 179 / 100 / 81 | :718–720 |
| asked / answered / answer rate among speakers | 496 / 360 / 0.7258 | :728–730 |
| 4p1i crew / impostor coverage means | 0.7821 / 0.1538 | :746–749 |

The pinned suite's comment carries the finding:

> the role split shows the ~⅓ answer rate is STRUCTURED (crew 0.462 vs impostor 0.089 —
> impostors refuse by prompt design), not uniform silence. (test_funnel_pooling.py:701–703)

The fold's design comment names the mechanism: the impostor templates *"instruct impostors to
explain nothing about their own whereabouts"* (`eval/funnel.py:1491–1505`).

**The read:** the 0.363 the close could not rule on decomposes three ways: (a) impostors refuse
by prompt design (0.089); (b) crew answer just under half the time (0.462); (c) among players who
take a meeting turn at all, 72.6% answer (360/496) — a large share of the residual gap is players
who never speak in the meeting, not players who speak and withhold. So the non-answering set is
impostor-skewed per capita (~5.2× — §6) but the raw absent population is still crew-heavy,
because crew outnumber impostors and answer under half the time.

## 4. Evidence row 3 — the widened column (17.5's double-count counterfactual) — source: `tests/agents/test_absence_prior.py`, same class (PR #272 merge `937ed08`) [VERIFIED]

| cell | unwidened | **widened (`include_vent_sightings=True`)** | source line |
|---|---|---|---|
| recorded vent-flag supply | 75 flags across 66/179 meetings | (the widening's input) | :1428–1429 |
| vent-sighted ∩ absent population | — | **46/179 meetings, never >1 subject per meeting** | :1440–1441 |
| mechanism cross-check vs recorded flags | — | agrees on every meeting | :1452 |
| non-empty absent sets | 163/179 | **159/179** | :1470 |
| histogram | `{0:16,1:23,2:26,3:39,4:32,5:28,6:11,7:4}` | **`{0:20,1:22,2:32,3:39,4:34,5:23,6:9}`** | :1461–1469 |
| max / median | 7 / 3.0 | **6 / 3.0** | :1471–1473 |
| new-over-gate meetings | 53 | **53 — UNCHANGED** | :1484–1488 |
| top-churn meetings | 114 | **114 — UNCHANGED** | :1499–1503 |

The suite pins the structural reasons the decision cells cannot move:

> a vent-sighted subject carries the STRONG vent flag (+0.30, joint-capped at prior+0.30) in
> BOTH env legs, so they are already at/over the rendered gate OFF-side and can never be a NEW
> over-gate candidate (:1479–1483) […] The flag-carrying subject's ~0.80 joint-capped row
> dominates the §4.6 argmax with or without the stacked absence +0.08 (0.80 either way under the
> cap) […] the widening's whole measured effect is the absent-set shrinkage above, not the fold
> outcomes. (:1494–1499)

**The read:** the widening buys absent-set HYGIENE — a vent-SIGHTED subject stops being priced
"unaccounted for" in exactly 46 subject-meetings — and moves NEITHER decision cell. It cannot
substitute for roll-call coverage; its case is correctness of the absent-set definition, not
calibration relief.

## 5. The lever's mechanics — what bounds the cost of either ruling [VERIFIED]

The boundary pins (the same suite's 65-test fixed layer): the delta is 0.08; lone absence renders
**0.58 UNDER the §4.6 gate** — a quiet crewmate is never ejectable on absence alone (:255–260,
:349–360); the delta composes through the render ceiling, the joint cap, reporter exculpation,
and the §4.7 guards (:588–746); it is transient-only and never accumulates across meetings
(:454–475); and it **mints no `ContradictionRef`**, so an absence-lifted over-gate target still
coerces to SKIP when uncited under the graduated J2 gate (:768–796). The realized conviction
damage of a GO is therefore bounded by the citation gate; the unbounded quantity is ATTENTION —
on these bytes, 53 meetings mint a new vote-worthy candidate and 114 change some voter's rendered
argmax.

## 6. The proposed graduation bar [PROPOSED — ratified/amended at Ruling 1]

**The bar:** GRADUATE the absence prior at an adopting record ONLY when, measured on the
committed canonical 9p2i set at the evaluating substrate:

1. **new-over-gate ≤ 0.20** — lever-ON mints a NEW at-or-over-the-rendered-gate candidate in at
   most 20% of meetings; AND
2. **crew roll-call coverage mean ≥ 0.60** on the same committed set;

with **top-churn REPORTED beside the verdict** (tie-break-sensitive by construction — the
:1401–1404 comment — so informational, never gating), and both gating cells quoted from committed
test pins, never hand-computed.

**Where the thresholds come from, priced both directions:**

- **The 20% ceiling sits below the 24.4% the close already declined** (39/160, §0.1.4): a bar at
  or above an already-rejected reading would loosen the ratchet. At ≤1 meeting in 5 the lever's
  game-wide footprint is a bounded minority while §5's structural pins bound each intrusion's
  depth.
- **The 0.60 crew-coverage floor is the 16.8 calibration premise made numeric** — the lever is
  "calibrated to work WITH roll-call (answering roll-call removes a player from the absent
  set)". At ≥0.60 a majority of living crew self-place every meeting, so remaining absence is
  dominated by refusal — and refusal is the lever's designed target: per capita, impostors
  refuse ~5.2× more than crew (1−0.0894 = 0.911 vs 1−0.4624 = 0.538 unplaced; placement rates
  0.4624 vs 0.0894 [VERIFIED]; the ratio is arithmetic [INFERRED]).
- **The quiet-crewmate cost at the MEASURED uptake** [INFERRED — arithmetic over the §3 cells;
  start-of-game roster shape 7 crew : 2 impostors, an approximation since living rosters
  shrink]: expected absent-set composition ≈ 7×(1−0.4624) : 2×(1−0.0894) ≈ 3.76 : 1.82 ≈
  **2.1 : 1 crew-to-impostor**. At today's coverage the +0.08 lift lands on roughly two quiet
  crew for every refusing impostor.
- **What the widening buys toward the bar: nothing.** Cell 1 is unchanged widened (53 → 53) and
  churn is unchanged (114 → 114) — §4. The bar deliberately does not credit it.

**The bar against today's committed cells:** new-over-gate 53/179 = **0.296 > 0.20 — FAIL**;
crew coverage **0.4624 < 0.60 — FAIL**. Both clauses fail: the bar reads **STAY-OFF** on the
baseline-5 evidence.

**What a GO would still buy, priced honestly:** the refusal signal is real and directionally
crew-aligned (the refusers are the impostors, ~5.2× per capita), impostor win rose 0.24 → 0.36
at baseline 5, and this phase trains against exactly that price — an absence prior is a
counterweight. Against it: (a) impostor refusal is BY PROMPT DESIGN (§3) — graduating now
hard-wires a template artifact as a game-wide suspicion channel; (b) at measured uptake the lift
lands ~2:1 on quiet crew; (c) the gate-relevant counterfactual read WORSE, not better, than the
reading the close declined (0.296 vs 0.244, context read); (d) the ~14–15h corpus would be
recorded on this uncalibrated channel and every Phase-17 mover would train against it.

## 7. THE THREE RULINGS

Each block follows the Task-14.6 locked-decision shape (the 15.18 convention). The §1–§6 memo
was assembled FIRST and the three couplings were then put to the owner in-session on 2026-07-14,
with a plain-terms implication briefing per direction. The owner's one clarifying question was
answered on the record before the ruling — *does stay-OFF take away any of the newly added
gameplay features?* No: every graduated Phase-16 layer (roll-call, the citation gates,
observation ids, personas, whereabouts-lie detection) is unconditional and unaffected; the
absence prior has never been ON, so stay-OFF removes nothing live and defers one addition. The
owner's recorded ruling, verbatim: **"STAY-OFF package (Recommended)"** — the combined slot
covering all three rulings below, with the §6 bar and the Phase-18 routing ratified as proposed.
Sign-off additionally rides the merge of this PR (the 15.18 convention).

### Ruling 1 — graduation: **STAY-OFF**

**LOCKED DECISION (owner, 2026-07-14) — the absence prior STAYS OFF; the §6 bar is RATIFIED as
proposed:**

- The graduation component of the owner's recorded package ruling (§7 preamble, verbatim
  **"STAY-OFF package"**): stay-OFF, with the §6 criterion (new-over-gate ≤ 0.20 AND crew
  roll-call coverage ≥ 0.60, top-churn reported informationally) adopted as the standing
  graduation bar for any future absence-prior ruling.
- The lever stays the sole live default-OFF toggle (`absence_prior`, the §0.1.4 posture); no
  adopting record this phase; Task 17.8 is REMOVED by this PR's surgery (§8).
- **Rejected — GO (graduate at 17.8):** the bar fails on both clauses (0.296 > 0.20; 0.4624 <
  0.60); the lift would land ~2:1 on quiet crew at measured uptake; the refusal signal is partly
  a prompt artifact; and the corpus would be recorded against the uncalibrated channel.
- **Evidence:** §2 (53/179, 114/179), §3 (0.4624 / 0.0894), §6 (the bar arithmetic).

### Ruling 2 — the vent-placement widening: **HOLD**

**LOCKED DECISION (owner, 2026-07-14) — the widening does NOT ship this phase:**

- The widening component of the owner's recorded package ruling (§7 preamble): HOLD.
- `include_vent_sightings` stays default-OFF with no production call site (the 17.5 posture:
  grounded-only, scope-firewalled, byte-preserving); the mechanism and its counterfactual pins
  stay green in the tree and travel to Phase 18 WITH the graduation package — a widening that
  ships is meeting-layer and must ride an adopting record, and under STAY-OFF no meeting-layer
  record exists this phase to carry it.
- **Rejected — SHIP:** structurally incoherent under STAY-OFF (no adopting record to travel
  with), and the measured case for it is hygiene-only — zero movement on both decision cells
  (§4: 53 → 53, 114 → 114).
- **Evidence:** §4 (46/179 double-count population; unchanged decision cells).

### Ruling 3 — the Phase-18 routing note: **RATIFIED**

**LOCKED DECISION (owner, 2026-07-14) — the stay-OFF path routes to Phase 18 as follows:**

- The routing component of the owner's recorded package ruling (§7 preamble): RATIFIED as
  proposed.
- Phase 18 owns, as one package: (a) the pooling-prompt uptake work that raises the answer rate
  (aggregate 0.363; the target is the §6 bar's crew clause, ≥ 0.60 crew coverage — and §3 shows
  the residual gap is substantially players who never take a meeting turn, so the work is
  turn-taking surface as well as template asks); (b) re-running this counterfactual on the
  Phase-18 substrate and graduating at a Phase-18 adopting record IFF the ratified §6 bar
  passes; (c) the vent widening travels with that package and is re-ruled with it (Ruling 2);
  (d) the impostor-template refusal artifact (§3) is a named input to the Phase-18
  heterogeneous-lobby prompt work — if impostor templates change, the bar re-reads on the new
  bytes, never on these.
- **Rejected — silent deferral:** the §0.1.4 discipline — a stay-OFF is a recorded owner
  decision with a named re-measure path, never an omission.
- **Evidence:** §3 (who is not answering), §6 (the bar the re-measure must pass).

## 8. The surgery record (the STAY-OFF direction, executed in this PR)

Exactly what the phase doc's Baseline-numbering block enumerates for STAY-OFF, per the 16.2
discipline (removal, not labeling — `scripts/compute_next_task.py` has no dropped state):

- **Task 17.8's contract is REMOVED** from `tasks/phase-17.md` and replaced with one prose drop
  record naming this audit; its generated prompt
  (`agent_prompts/task-17-8-absence-adopting-record.md`) is deleted (the generator never deletes
  — removed by hand, then `generate_prompts.py --check` and the validator's extra-file check
  hold the line).
- **The GO-conditional 17.8 clauses are SCRUBBED** from 17.9's DoD ("or the 17.8 substrate under
  GO"), 17.10's body and 17.11's body ("or the 17.8 baseline under the gate's GO" — the
  baseline-5 literal is now pinned), 17.11's files-NOT-in-scope note, and 17.16's body; the DAG
  diagram, collision-discipline block, and operator/owner-gates block drop their 17.8 arms; the
  preamble's Baseline-numbering block records that the GO surgery was NOT performed (the 16.2
  GO-banner convention, inverted); the STATUS banner records the three rulings; the two
  preamble designer-ruling lines that pointed at the pending gate now carry the ruled outcome.
- **Dependencies and scopes are otherwise untouched:** 17.9 still depends on `17.2, 17.7`; no
  `Depends on:` line ever named 17.8 (it was a DAG leaf), so the parsed graph loses only the
  leaf. The mover record at 17.17 stays **baseline 6**; `baseline5-final-measure.json` stays its
  BEFORE column; no renumbering.
- Prompts regenerated mechanically for every touched contract; validator, `--check`, and
  `compute_next_task.py --phase 17` green on the surviving DAG.

## 9. The sequencing consequence (the merge criterion's named line)

**The corpus re-record (17.9) is UNBLOCKED at the baseline-5 meeting layer** once this PR and
17.2 are merged: nine always-on levers, `absence_prior` OFF, `include_vent_sightings` OFF — the
byte-identical substrate of the 16.17 close record. No meeting-layer record intervenes between
this gate and the corpus, so the corpus is recorded at the FINAL Phase-17 meeting layer by
construction (locked decision 3's sequencing requirement, discharged on the stay-OFF branch).
