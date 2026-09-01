# Phase-21 pre-registration — the falsifiability contract for the injustice record: instruments, baseline-8 cells, the successor bars, the reporter bars, the decision rule (Task 21.22)

**Date:** 2026-09-01, drafted and pinned at Task 21.22 against HEAD `38b680f0`.
**Status:** RATIFIED — the owner's merge of Task 21.22's PR is the ratification (§10). Every
baseline cell below is quoted from a committed pin or a committed reader run at that HEAD, and
every definition, bar and rule is stated as [PROPOSED — ratified at merge]. Amendments after
that merge are dated errata in §11.
**Depends on:** the merged Wave-2 lever contracts — `reporter_reasoning` (#414),
`corroboration_discipline` (#415) and `testimony_shapes` (#416, amended at #417) — plus the
21.18 instrument `eval/reporter_justice.py`, the 21.15 corrected-substrate re-record
(`audits/audit-phase-21-rerecord.md`, which mints **baseline 8**) and the 21.21 offline
counterfactual (`audits/audit-phase-21-counterfactual.md`, #418). The measured bytes are the
baseline-8 record; no file under `replays/` moves at this gate.

**What is being pre-registered:** the instrument list (§2), the baseline-8 cells (§3), the four
primary bars (§4), the advisory discipline (§4.2), the secondary observed-not-gated cells (§5),
the measured-but-not-registered list (§5.1), the decision rule (§6), the co-intervention
declaration (§7), the offline-counterfactual protocol and the tripwire dispositions (§8), and
the record order, the freeze, the slate and the preconditions (§9). The memo is read VERBATIM
by 21.23 (the smoke) and 21.24 (the adopting record).

**Method:** zero hand-computed figures. Every cell names the committed file that computes it and
reproduces from `uv run pytest -q -k "deduction_metrics or funnel or evidence_honesty or
solvability or reporter_justice"` plus the committed readers `python -m eval.reporter_justice
… --pooled` (`eval/reporter_justice.py`:677-692) and `scripts/measure_baseline.py --funnel /
--honesty / --solvability / --vj --json` (`scripts/measure_baseline.py`:26-34). Every interval
is the Wilson 95% score interval produced by `eval.deduction_metrics._wilson_interval`
(`eval/deduction_metrics.py`:983) — the only interval producer any cell in this memo may quote,
the 18.4 §10 convention carried through 20.22. §12 reproduces every number with one command.

**Label key** (the 18.4 key, unchanged): **[VERIFIED]** quoted from a committed test pin or
committed source · **[INFERRED]** arithmetic over verified cells with the inputs shown ·
**[PROPOSED — ratified at merge]** a definition, bar or rule the owner ratifies by merging this
task's PR.

---

## 0. Verdict in one line

**Four primary bars, every one computable from committed bytes by a committed instrument, judge
ONE adopting record: the two bars Phase 20 MISSED carry over with their targets unchanged —
non-direct conviction accuracy 50/96 = 0.5208 → ≥ 0.60 pooled and innocent ejections 46 → < 35
pooled — joined by two new bars aimed at the class that supplies 34 of those 46 innocent
ejections, the meeting's own body reporter: pooled reporter convictions 34 → ≤ 12 and the
reporter share of the innocent-ejection cell 73.9% → < 40%; measured on the record's own bytes
with the Wave-2 slate ON, under a conjunctive rule and seven dispositioned tripwires written
before the record is spent.**

## 1. Why these cells, and why now — and what re-anchors without re-ratification

Phase 20 spent one 23-hour record and got the verdict its own rule wrote in advance: **FINDING**.
Bars 1 and 2 — non-direct conviction accuracy ≥ 0.60 pooled, innocent ejections < 35 pooled —
were MISSED, at 61/103 = 0.5922 and 42 [VERIFIED: `audits/audit-phase-20-baseline-7.md` §6].
Baseline 7 is canon by an **explicit owner override of that FINDING verdict** (§6.1), recorded as
an override on stated grounds and never as an arithmetic pass. Those two bars are the only ones
that phase left unmet with a live population behind them, and they are this phase's inheritance:
the injustice record exists to try them again, on corrected bytes, with the Wave-2 levers ON.

**§6.1's constraint binds every sentence of this memo.** No document, comment, docstring, README
row or commit message in this repository may state or imply that the pre-registered phase-20 bars
passed, that the verdict was ADOPTED under the rule, or that baseline 7 was adopted on the
arithmetic. Nothing below says otherwise, and §4's bars 1 and 2 each carry the miss on their own
row.

**The bars carry over with their targets unchanged.** That is the 20.22 standing rule
(`audits/audit-phase-20-preregistration.md` §1) applied to its own successor: the
corrected-substrate re-record re-anchors every baseline CELL, and a re-anchored baseline never
drags a target with it. A bar that follows its own baseline is not a bar — and a bar that softens
because the phase before it missed by 0.0078 is worse than none.

> Where a pinned re-derivation differs from a published figure, the PIN replaces the cell and the
> bar's TARGET does not move with it.

**The distance moved, and the memo states it here rather than letting a reader carry 0.0078
forward.** At the phase-20 record bar 1's gap was 0.0078 — one conviction at a constant
denominator (62/103 = 0.6019 passes; 61/103 = 0.5922 does not). On baseline 8 the same bar's gap
is **0.0792** (0.60 − 50/96 = 0.5208), which is **eight** convictions at a constant denominator
(58/96 = 0.6042 passes; 57/96 = 0.5938 does not) [INFERRED from the §3.1 cell]. Bar 2's ask is
**−12** cases (46 → ≤ 34) rather than −8 (42 → ≤ 34). The targets still do not move; what moved
is how far they are.

**The new content is the reporter class, and it is registrable today because a committed
instrument already emits it — and since 21.18 that instrument is dedicated.** A-4's headline —
30 of the 42 pooled innocent ejections eject the meeting's own body reporter — is BASELINE-7
PRIOR-RECORD CONTEXT and is labelled that way wherever it appears. `eval/reporter_justice.py`
(21.18) computes the class directly, and `tests/eval/test_reporter_justice.py` pins it POOLED
over all four committed sets as LITERAL assertions: `body_report_meetings == 620` (:66),
`reporter_impostor_meetings == 0` (:78), `ejections == 429` and `innocent_ejections == 46`
(:87-88), `reporter_ejections == reporter_innocent_ejections == 34` (:99/:103), the share
(:104-105), and 34/620 against 12/1,859 at RR 8.495 (:113-126). Re-run at this HEAD the pooled
reading is **34 reporter convictions of 46 innocent ejections = 73.9%, over 620 body-report
meetings, per slot 5.48% against an innocent non-reporter's 0.65%, relative risk 8.50x**.

Because both numerator and denominator are pooled literal pins, the phase-20 memo's "some cells
come through the reader rather than from an assertion" hedge does NOT apply to bars 3 and 4. It
still applies to ONE row and only that row: bar 1's `ml_corpus/4p1i` cell, where
`tests/eval/test_deduction_metrics.py`:334-335 pins the denominator 3 and a not-None sentinel and
**not the numerator** — that cell's 3/3 comes through the committed
`tournament-eval-report.json` and the §12 reader, and the memo says so on the row.

**The independent TWIN, registered beside the primary and never as a second definition.**
`eval/funnel.py`'s reporter census (`reporter_ejected`, `reporter_ejected_innocent`,
`report_meetings`, `report_ejections`, `killer_self_reported`; :910-912, :918, folded at
:1045-1048) reads **7 / 23 / 4 / 0 reporter ejections, every one of them innocent**, over
141 / 407 / 36 / 36 report meetings and 85 / 249 / 21 / 22 report ejections, with
`killer_self_reported` **0 on every set** — pooled 34 / 620 / 377. Two independently authored
readers landing on the same 34, per set as well as pooled, is this memo's strongest provenance
claim for bar 3, and §3.1 states the agreement as a cell rather than asserting it. The reporter
bars need no new instrument, which is what makes them registrable at a gate that adds no code.

**The standing rule (the 18.4 one, restated for this phase)** [PROPOSED — ratified at merge]: the
DEFINITIONS (§2), the statistical conventions (§12), the BARS (§4), the advisory discipline
(§4.2), the decision rule (§6), the co-intervention declaration (§7), the protocol (§8) and the
record order (§9) are the ratified content. The quoted baseline CELLS (§3, §5) are EVIDENCE and
re-anchor mechanically at the adopting record — 21.24 re-quotes them on the new bytes with
provenance, without re-ratification.

**Precedence.** This memo is the only normative source for the cells, the bars and the decision
rule while the phase runs. Where a contract, a generated prompt or a later audit disagrees with
it, the memo governs and the other surface is re-anchored at its pre-dispatch review — never
treated as a second baseline and never as a second rule. The known divergences at ratification,
so the coordination pass has a written list rather than a search:

* **The prompt-set version.** Task 21.22's own contract text states that the committed sample
  sets "STAMP v4 and resolve through `tests/fixtures/prompt_archive/qwen3_6_27b_v4/`". At this
  HEAD all four committed `MANIFEST.md` files stamp **v5**
  (`accusation_round.qwen3_6_27b.v5` and its three siblings), `tests/fixtures/prompt_archive/`
  does not exist, and `tests/meetings/test_prompt_byte_golden.py`:191 pins
  `ARCHIVED_PROMPT_VERSION_SETS = {}`. The registry
  (`orchestrator/game.py`:381, `PROMPT_VERSION_SETS["qwen3_6_27b"]`) is also v5, so registry and
  recorded MANIFESTs AGREE here. The contract's reading INSTRUCTION stands and §9 follows it —
  the version is read from the recorded MANIFESTs, never from the registry — and the contract's
  v4 figure is stale prose, re-anchored here.
* **The report emitter.** The contract names
  `agents/tactical/crewmate_policy.py`:737-740 as "the ONLY emitter of a `{"type": "report"}`
  intent in the tree". At this HEAD there are **two**: that one, and
  `agents/tactical/learned/crew_forward.py`:1086-1091, the opt-in LEARNED CREW surface (18.7),
  which is a gated surface beside the scripted default and is not what these bytes were recorded
  with. Both are crew-side, so the premise §4.3 states survives — but it survives through two
  emitters, and the memo names both rather than resting on a count that is wrong.
* **The pooled Wilson interval.** `audits/audit-phase-21-rerecord.md` §5.1 quotes a pooled
  non-direct interval whose two bounds differ from the production helper's in the fourth decimal.
  §3.2 is the single place both readings are written out; the helper governs, and this memo never
  copies an interval it did not run.

A stale statement downstream is a re-anchor, never a second baseline and never a second rule.

**One ordering fact, stated rather than finessed.** Phase 20's memo landed before the first
lever; this one lands AFTER the three Wave-2 levers merged and after the offline counterfactual,
because the DAG puts it there. That makes it **bars-before-the-record, not bars-before-the-levers**,
and this memo says so in its own first section. Two things keep it honest:

1. the two PRIMARY targets (bars 1 and 2) are inherited verbatim from
   `audits/audit-phase-20-preregistration.md` §4 and are not derived from any phase-21 number;
2. the counterfactual's predictions were committed before this merge (#418) and are quoted by
   section here, never re-computed.

Any target chosen with a phase-21 figure in view names the figure it was chosen against. The two
reporter targets are the candidates, and §4 names theirs: **bar 3's ≤ 12 was chosen against the
non-reporter residue 46 − 34 = 12, and bar 4's < 40% against the boundary case 12/34 = 35.3%.**
The owner's merge ratifies; anything after it is a dated erratum in §11.

## 2. The instruments

Six rows. Two carry all four bars; one is the twin registered beside the reporter primary; three
carry secondaries only. **No instrument is added, changed or redefined at this gate** — a cell
this memo would want but no committed reader emits is routed as its own contract (§5.1), exactly
as the 18.4 and 20.22 batches did.

| id | instrument | owner module | committed pin | what rides it |
|---|---|---|---|---|
| I-1 | Proof-vs-inference conviction cells (direct-proof / non-direct accuracy; innocent ejections; the ejection total) | `eval/deduction_metrics.py` (19.14), `EjecteeProofCrossTab` at :1251 | `tests/eval/test_deduction_metrics.py`:163, :165/:186, :184, :270, :276, :312, :318-319, :334-335 | **bars 1 and 2** |
| I-2 | Reporter-justice cells (body-report meetings; reporter role; reporter ejections and the innocent half; per-slot rates and the relative risk; the share) | `eval/reporter_justice.py` (21.18), `ReporterJusticeCells` at :144-158, `compute_reporter_justice` at :540, `pool_reporter_justice` at :604 | `tests/eval/test_reporter_justice.py`:66, :78-79, :87-88, :99, :103, :104-105, :113-126 — POOLED LITERAL over all four sets via the module-scope `pooled` fixture at :55-58 | **bars 3 and 4** |
| I-3 | Reporter census, independently authored (`reporter_ejected`, `reporter_ejected_innocent`, `report_meetings`, `report_ejections`, `killer_self_reported`) | `eval/funnel.py` (15.3) :910-912, :918; `compute_information_funnel` at :968; folds at :1045-1048 | `tests/eval/test_funnel.py`:631-633, :638 | **registered BESIDE I-2 as the agreeing twin** (§3.1); never a second definition of the bar |
| I-4 | Evidence-honesty cells (false self-placement, sole-flag precision, grounded sighting sides, the render census) | `eval/evidence_honesty.py` (20.15), `CELL_DEFINITIONS` at :303 | `tests/eval/test_evidence_honesty.py` | secondary only (§5) |
| I-5 | Solvability y-axis (containment; singleton rate and correctness; ejections landing on an already-cleared player) | `eval/solvability.py` (20.14) :395 | `tests/eval/test_solvability.py` | secondary only (§5) |
| I-6 | Zero-flag conviction cells — convictions carrying no contradiction flag, split by the convicted player's role | `eval/vj_instruments.py`:312-327 | `tests/eval/test_vj_instruments.py` | secondary only (§5) |

**Definitions are adopted BY REFERENCE from the module that computes them**, in the 20.22 §2
shape: `eval/evidence_honesty.py::CELL_DEFINITIONS` (:303) holds one sentence per I-4 row;
`eval/solvability.py`'s "The rule, stated before any cell is counted" block states I-5's;
`eval/reporter_justice.py`'s own field comments and property docstrings state I-2's.

**One definition string is narrower than the cell this memo registers, and the registered
semantics govern** [PROPOSED — ratified at merge]:

* **I-2, the share.** `ReporterJusticeCells.reporter_share_of_innocent_ejections`
  (`eval/reporter_justice.py`:219-229) states in its own docstring that the numerator is
  `reporter_innocent_ejections` — **not every reporter ejection** — because "a guilty reporter
  convicted is a correct verdict and belongs to neither side of this ratio". **That is the
  registered reading and bar 4's population.** On baseline 8 the two coincide exactly
  (`reporter_ejections == reporter_innocent_ejections == 34`, pinned at :99/:103), so nothing is
  mispriced today; they separate the moment a recorded leg ejects a guilty reporter, which is
  also the leg §4.3's VOID condition catches. The bar names its cell rather than inheriting a
  count.

There is no other narrowing to declare: I-1's, I-5's and I-6's definition strings and the cells
this memo registers are the same population. Correcting any definition string is a production
edit and routes as its own contract — this memo quotes instruments and never redefines a cell.

## 3. Baseline cells (**baseline 8** — the committed bytes of the 21.15 corrected-substrate re-record)

The column is named by baseline ID deliberately: two baseline ids move in this phase, and a
"before" column labelled only "baseline" would be ambiguous the moment baseline 9 exists. The
baseline-7 values appear beside these as the phase-20 record's HISTORY, and **no phase-20 cell is
re-priced anywhere in this memo.**

### 3.1 The table

Every cell is `numerator/denominator` over the committed bytes of that set. Every numeric row is
recomputed by the §12 reader.

| cell | samples/9p2i | ml_corpus/9p2i | samples/4p1i | ml_corpus/4p1i | committed source |
|---|---|---|---|---|---|
| I-1 direct-proof accuracy | 68/68 | 220/220 | 19/19 | 26/26 | [VERIFIED] `EjecteeProofCrossTab.proof_present_impostor / .proof_present_ejections`; pooled **333/333** |
| I-1 non-direct accuracy | 14/27 | 32/61 | 1/5 | 3/3 | [VERIFIED] `tests/eval/test_deduction_metrics.py`:165/:186, :276, :318-319; the `ml_corpus/4p1i` NUMERATOR is reader-derived (:334-335 pins denominator 3 + the not-None sentinel only); pooled **50/96 = 0.5208** |
| I-1 innocent ejections | 13/95 | 29/281 | 4/24 | 0/29 | [VERIFIED] `tests/eval/test_deduction_metrics.py`:163, :270, :312; pooled **46/429** |
| I-2 body-report meetings | 141/151 | 407/439 | 36/39 | 36/43 | [VERIFIED] `tests/eval/test_reporter_justice.py`:66; pooled **620/672** |
| I-2 reporter is a CREWMATE | 141/141 | 407/407 | 36/36 | 36/36 | [VERIFIED] same file :78-79; pooled **620/620**, `reporter_impostor_meetings` 0 |
| I-2 reporter innocent ejections | 7/13 | 23/29 | 4/4 | 0/0 | [VERIFIED] same file :103, :88; pooled **34/46 = 73.9%** — bar 4's cell |
| I-2 reporter ejected per slot | 7/141 | 23/407 | 4/36 | 0/36 | [VERIFIED] same file :113-126; pooled **34/620 = 5.48%** |
| I-2 innocent non-reporter per slot | 6/464 | 6/1323 | 0/36 | 0/36 | [VERIFIED] same file :113-126; pooled **12/1859 = 0.65%**, RR **8.50x** |
| I-3 reporter_ejected_innocent (twin) | 7/141 | 23/407 | 4/36 | 0/36 | [VERIFIED] `tests/eval/test_funnel.py`:631-632; **agrees with I-2 per set and pooled: 7+23+4+0 = 34** |
| I-3 report_ejections (twin) | 85/141 | 249/407 | 21/36 | 22/36 | [VERIFIED] `tests/eval/test_funnel.py`:633; pooled **377/620** |
| I-3 killer_self_reported (twin) | 0/141 | 0/407 | 0/36 | 0/36 | [VERIFIED] `tests/eval/test_funnel.py`:638; **0 on every set** — §4.3's premise cell |
| I-5 containment (killer in the candidate set) | 127/141 | 358/407 | 36/36 | 36/36 | [VERIFIED] `eval/solvability.py`:395; pooled **557/620** |
| I-5 ejections on an already-cleared player | 16/85 | 47/249 | 0/21 | 0/22 | [VERIFIED] same; pooled **63/377** |
| I-6 zero-flag convictions | 20/95 | 58/281 | 5/24 | 3/29 | [VERIFIED] `eval/vj_instruments.py`:312-327; pooled **86/429** |
| I-6 zero-flag CREW convictions | 7/20 | 26/58 | 4/5 | 0/3 | [VERIFIED] same; pooled **37/86** — and 37 of the 46 innocent ejections carry no contradiction flag |

**Intervals** (Wilson 95%, `eval.deduction_metrics._wilson_interval`; §12 re-runs each)
[VERIFIED]: I-1 non-direct pooled 50/96 = 0.5208 [0.4220, 0.6180]; per set 14/27 = 0.5185
[0.3399, 0.6926], 32/61 = 0.5246 [0.4016, 0.6447], 1/5 = 0.2000 [0.0362, 0.6245], 3/3 = 1.0000
[0.4385, 1.0000]. I-2's share 34/46 = 0.7391 [0.5974, 0.8440]; the per-slot pair 34/620 = 0.0548
[0.0395, 0.0757] against 12/1859 = 0.0065 [0.0037, 0.0112].

**The baseline-7 history, beside them and never re-priced** [VERIFIED,
`audits/audit-phase-20-baseline-7.md` §3 and §6; `audits/audit-phase-21-rerecord.md` §5.1]:
non-direct **61/103 = 0.5922** (per set 16/30, 42/68, 1/2, 2/3); innocent ejections **42** (per
set 14 / 26 / 1 / 1); direct-proof 326/326. The reporter class on those bytes was **30 of 42 =
71.4%** with RR 7.46x, as filed at `audits/review-2026-08-26/A/collated-findings.md` A-4 (:431)
— a REVIEW figure over a prior record, quoted as history and never as a cell this memo registers.

### 3.2 Where a pin and the register disagree — both numbers kept, the pin authoritative

| cell | the other reading | **the pin / helper (authoritative)** | cause |
|---|---|---|---|
| I-1 non-direct pooled INTERVAL | `audits/audit-phase-21-rerecord.md` §5.1 quotes **[0.4224, 0.6178]** | **[0.4220, 0.6180]** — `_wilson_interval(50, 96)` returns `(0.5208333333333334, 0.42203591721406514, 0.618027543307401)` at this HEAD | the memo never silently copies an interval it did not run; the point estimate 0.5208 and all four per-set intervals agree exactly, so the divergence is confined to the pooled bracket and is carried, not smoothed |
| the reporter class | A-4 (:431) filed **30 of 42 = 71.4%**, per slot 30/618 = 4.85% against 12/1844 = 0.65%, **RR 7.46x**, over 618 report meetings | **34 of 46 = 73.9%**, per slot 34/620 = 5.48% against 12/1859 = 0.65%, **RR 8.50x**, over 620 report meetings | different BYTES, not a different method: A-4 measured the baseline-7 record and this memo measures baseline 8. The register figure is history; the pin is the cell |
| the prompt-set version | the 21.22 contract's own prose says the committed sets stamp **v4** and resolve through `tests/fixtures/prompt_archive/qwen3_6_27b_v4/` | **v5** in all four committed `MANIFEST.md` files; `tests/fixtures/prompt_archive/` absent; `ARCHIVED_PROMPT_VERSION_SETS = {}` (`tests/meetings/test_prompt_byte_golden.py`:191) | the archive seam was retired at 20.36 and the set re-recorded at v5 by 21.15; §9 reads the version from the recorded MANIFESTs, which is the instruction the contract also gives |
| the report emitter | the 21.22 contract calls `agents/tactical/crewmate_policy.py`:737-740 the **ONLY** emitter of a `{"type": "report"}` intent | **two** emitters: that one and `agents/tactical/learned/crew_forward.py`:1086-1091 | 18.7 shipped an opt-in learned CREW surface beside the scripted default. Both are crew-side and neither is reachable from an impostor, so §4.3's premise holds — through two emitters, named |

Three further re-anchors are recorded so no later reader mistakes them for drift.

* **The two readers AGREE, per set and pooled.** `eval/reporter_justice.py` and `eval/funnel.py`
  were authored independently, six phases apart, and land on 7 / 23 / 4 / 0 = **34** by both
  routes. This is registered as a CELL in §3.1 (row I-3), not asserted in prose.
* **A-5's design hole stands on the bytes the bars are priced from, and its repair exists as the
  lever the record turns ON.** At baseline 7 the reporter exculpation rendered at ballot time
  only. At this HEAD `grep -c reporter agents/strategic/prompts/qwen3_6_27b/accusation_round.j2`
  returns **5**, not 0, against 5 in `vote_ballot.j2` and 7 in `crewmate_report.j2`.
  **Only the SPEECH side is lever-gated, and the distinction is load-bearing** — the 21.22
  contract's own text calls both halves lever-gated and is wrong on the ballot half:
  * **speech side, LEVER-GATED**: `render_reporter_id` at `meetings/manager.py`:1132-1136 is
    `trigger.triggered_by` only `if reporter_reasoning and not _trigger_is_emergency(trigger)`,
    and everything downstream — the `reporter_context` at :1823-1832, threaded at :1828, feeding
    the 21.18 block at `accusation_round.j2`:133-136 — is inert when the lever is OFF;
  * **ballot side, UNCONDITIONAL**: `reporter_id` at :1984-1987 is `trigger.triggered_by` for
    every body report, `None` only for an emergency call, and is passed at :2039 with no lever
    read anywhere in the chain. That is the **15.5 exculpation**, which has rendered on every
    body-report ballot since long before this wave; `vote_ballot.j2`:238-241 is that block, not a
    Wave-2 one.

  **This is exactly why T3 (§8.1) predicts ballots gain NOTHING** — the reporter lever has no
  ballot seam to reach, because the ballot already says it. Attributing the ballot thread to
  `reporter_reasoning` would both misdescribe the lever and make T3 look like a lucky zero rather
  than a structural one. **The baseline-8 bytes are all-levers-OFF**, so A-5's design hole — the
  exculpation reaching the ballot and nothing else — IS the record's state, and A-5's "grep -c
  reporter = 0 in all five non-ballot templates" is a PRIOR-RECORD fact about the pre-21.18 tree
  that may not be re-run as a HEAD claim.
* **The reporter's ejectability is a RECORDED DESIGN DECISION, not an oversight**
  (`agents/memory/beliefs.py`:174-201, chartered at `tasks/phase-15.md`:552-580): 15.5 zeroed the
  reporter's SOFT accusation-driven pre-vote lift and deliberately left every HARD channel intact,
  so a reporter caught by a real contradiction or a vent/kill flag still crosses the gate. Bars 3
  and 4 gate the OUTCOME of that decision on new bytes; they do not assert it was wrong.

## 4. Primary bars [PROPOSED — ratified at merge]

Measured on the 21.24 record's bytes by the same instruments, pooled over the four recorded sets
with the per-set cells shown beside the pooled figure. **Bars 1 and 2 are inherited VERBATIM from
`audits/audit-phase-20-preregistration.md` §4 and their targets did not move with the
re-anchored baseline.**

---

**Bar 1 — I-1 non-direct conviction accuracy ≥ 0.60 pooled, and no ADEQUATELY POWERED set below
0.50.** Before (baseline 8): pooled **50/96 = 0.5208** [0.4220, 0.6180]; per set 14/27 = 0.5185
[0.3399, 0.6926], 32/61 = 0.5246 [0.4016, 0.6447], 1/5 = 0.2000 [0.0362, 0.6245], 3/3 = 1.0000
[0.4385, 1.0000]. The pooled figure is the gate.

*This bar was **MISSED** at the phase-20 record (61/103 = 0.5922 against ≥ 0.60), and baseline 7
is canon by explicit owner override of a FINDING verdict.*

**The inherited per-set clause, read at baseline-8 denominators.** Phase-20 §4.1 attaches
"adequately powered" to a non-direct denominator of **n ≥ 30** at the record. The baseline-8
denominators are **27 / 61 / 5 / 3** against phase-20's 30 / 68 / 2 / 3, so `samples/9p2i` has
**fallen below the `n ≥ 30` clause** and on these denominators `ml_corpus/9p2i` (n = 61) is the
only set whose 0.50 floor binds. That is stated as a CONSEQUENCE of carrying the clause verbatim,
never as a reason to re-price it — re-deriving a power threshold from a moved baseline is a bar
following its own baseline.

**And the clause DISAGREES with §4.2's granularity test on that very set, printed here rather
than reconciled.** At the pooled margin |0.60 − 0.5208| = 0.0792, `samples/9p2i`'s step is
1/27 = 0.0370, comfortably inside the margin — the granularity test calls it POWERED while the
literal `n ≥ 30` clause calls it not. **The `n ≥ 30` clause is carried VERBATIM and it governs**
[PROPOSED — ratified at merge]; the granularity disagreement is published beside it so no later
reader thinks it went unnoticed. **These are the memo's baseline denominators, not the record's:
the clause is applied at the record, to the record's own numbers.**

---

**Bar 2 — I-1 innocent ejections < 35 pooled.** Before (baseline 8): **46**, per set 13 / 29 / 4
/ 0. Every one of them sits inside the non-direct cell; the direct-proof cell is innocent-free at
0 of 333.

*This bar was **MISSED** at the phase-20 record (42 against < 35), and baseline 7 is canon by
explicit owner override of a FINDING verdict.*

The ask is **−12 cases**: 46 down to 34 or fewer, which is what `< 35` means on an integer
count. At the phase-20 record the same target asked for −8.

---

**Bar 3 — I-2 pooled reporter convictions 34 → ≤ 12** [PROPOSED — ratified at merge].

Cell: `eval.reporter_justice.ReporterJusticeCells.reporter_innocent_ejections`, pooled by
`pool_reporter_justice` (`eval/reporter_justice.py`:604) and pinned literally at
`tests/eval/test_reporter_justice.py`:103. Before: **34** pooled, per set 7 / 23 / 4 / 0.

**The arithmetic, on the baseline-8 numbers — the RESIDUE RULE.** Bar 2 asks the pooled
innocent-ejection count to fall from 46 to ≤ 34. The reporter class supplies 34 of those 46,
leaving a non-reporter residue of **46 − 34 = 12**. A phase that closed bar 2 while leaving the
reporter class intact would have to erase twelve of those twelve. The same-method target is
therefore **≤ 12** — which on its own puts the pooled innocent count at 46 − 22 = 24 with no
other class moving. The number is unchanged from the target the planning PR priced on 30 of 42,
because the residue is 12 on BOTH records.

**The burden, written beside the target rather than only the target** [INFERRED]: bar 3 now asks
for **22 cases erased, 64.7% of the class** (34 − 12 = 22; 22/34 = 0.647), against the **18 cases
and 60.0%** the same number asked at baseline 7 (30 − 12 = 18; 18/30 = 0.600). *The phase-21
figure this target was chosen against is the non-reporter residue 46 − 34 = 12.*

---

**Bar 4 — I-2 the reporter share of bar 2's own innocent-ejection cell, 34/46 = 73.9% → < 40%**
[PROPOSED — ratified at merge].

Cell: `ReporterJusticeCells.reporter_share_of_innocent_ejections` — numerator
`reporter_innocent_ejections` (:103), denominator `innocent_ejections` (:88), the registered
reading per §2. Before: **34/46 = 0.7391** [0.5974, 0.8440].

**The arithmetic** [INFERRED]: the boundary case is bar-3's cap over bar-2's cap, **12/34 =
35.3%**; the target is the round number just above it. *The phase-21 figure this target was
chosen against is that boundary case, 12/34 = 35.3%.*

**Why bars 3 and 4 are not redundant — and the extremum stated the right way round.** Bars 2 and
3 together do **NOT** imply a low share: bar 2 caps the denominator and places no floor under it,
so a record with `I = 12` and `R = 12` meets both and reads **100%**. Bar 4 bites in the case
bars 2 and 3 cannot see — a record that fixes the reporter class in ABSOLUTE terms and fixes the
rest of the ledger too, leaving the reporter still dominant in what remains: **`R = 10`, `I = 20`
passes bars 2 and 3 and fails bar 4 at 50%.** That is the outcome this phase would most want to
mistake for success, and it is the only thing bar 4 is for.

**Two reporter bars, not one, because a share alone can be gamed by its own denominator.** The
count bar and the share bar move for different reasons: the share falls if the reporter class
shrinks, and it also falls if some other injustice class grows. They are registered **jointly**,
and a bar-4 pass whose bar-2 count did NOT fall is labelled **SHARE-BY-DILUTION** in the record
audit, with both denominators printed beside the verdict — the same device the phase-20 memo used
for SUPPRESSED-NOT-FIXED, and for the same reason: the verdict is allowed to stand while the
mechanism behind it is never left implicit.

### 4.1 The bars as a machine-readable table

One row per bar, so 21.24's record contract reads the bars mechanically instead of re-deriving
them from prose. The prose statements above and this table agree, and the §12 reader checks both.

| bar | cell (fully qualified) | committed reader | baseline 8 | target [PROPOSED] | per-set clause powered? |
|---|---|---|---|---|---|
| 1 | `eval.deduction_metrics.EjecteeProofCrossTab.non_direct_accuracy` (pooled over the four sets) | `eval/deduction_metrics.py`:1251 via each set's `tournament-eval-report.json` | 50/96 = 0.5208 | **≥ 0.60 pooled**, no adequately powered set below 0.50 | `ml_corpus/9p2i` only (n=61 ≥ 30); `samples/9p2i` n=27 fell below the clause |
| 2 | `eval.deduction_metrics.MeetingFlagCrossTab` innocent-ejection total (flagged + unflagged, pooled) | `eval/deduction_metrics.py` via the same reports | 46 | **< 35 pooled** | pooled only — no per-set clause |
| 3 | `eval.reporter_justice.ReporterJusticeCells.reporter_innocent_ejections` (pooled by `pool_reporter_justice`) | `eval/reporter_justice.py`:604, CLI at :677-692 | 34 | **≤ 12 pooled** | pooled only — no per-set clause |
| 4 | `eval.reporter_justice.ReporterJusticeCells.reporter_share_of_innocent_ejections` (pooled) | `eval/reporter_justice.py`:219-229 | 34/46 = 0.7391 | **< 0.40 pooled** | pooled only — no per-set clause |

**Reproduction, one command for bars 3 and 4:**

```bash
uv run python -m eval.reporter_justice \
  replays/samples/9p2i replays/ml_corpus/9p2i replays/samples/4p1i replays/ml_corpus/4p1i --pooled
```

The four-set sum of the twin, one command per set:
`uv run python scripts/measure_baseline.py --funnel --json replays/<set>` — `reporter_ejected_innocent`
reads 7 / 23 / 4 / 0 and sums to **34**.

### 4.2 The advisory discipline [PROPOSED — ratified at merge]

**First, the reading convention, so the advisory test is not confused with it.** Every bar in
this memo is a POINT-ESTIMATE bar, with the Wilson interval reported beside it as context — the
18.4 convention. "The interval contains the threshold" is therefore NOT the advisory test;
applied as one it would make every bar here advisory, including the pooled ones, and the phase
would gate on nothing.

**The advisory test is GRANULARITY, carried over verbatim from
`audits/audit-phase-20-preregistration.md` §4.1: a cell is ADVISORY when one observation moves it
by more than the margin the bar asks for — `1/n > |target − baseline|`.** Such a cell is not
measuring the lever; it is reporting which way a single game fell. An advisory cell is published
with its rate, its Wilson interval and this arithmetic, and takes **no part in the verdict in
either direction**: it cannot turn ADOPTED into FINDING and it cannot rescue a pooled bar that
was missed.

**The margin term uses the POOLED baseline**, as phase-20 §4.1 does when it computes
|0.60 − 0.368| = 0.232 for a per-set cell. Stated explicitly so the test cannot be re-read
per-set later. At this memo's own baseline denominators the margin is
**|0.60 − 0.5208| = 0.0792**:

| set | step `1/n` | vs margin 0.0792 | verdict |
|---|---|---|---|
| `samples/9p2i` | 1/27 = 0.0370 | 0.0370 < 0.0792 | not advisory |
| `ml_corpus/9p2i` | 1/61 = 0.0164 | 0.0164 < 0.0792 | not advisory |
| `samples/4p1i` | 1/5 = 0.2000 | 0.2000 > 0.0792 | **ADVISORY** |
| `ml_corpus/4p1i` | 1/3 = 0.3333 | 0.3333 > 0.0792 | **ADVISORY** |

**Bars 2, 3 and 4 are COUNT bars and the granularity test does not reach them**, for the reason
phase-20 §4.1 gives: the test compares a rate step against the distance between a rate baseline
and a rate target, and a count bar is decided on the numerator. Bar 4 is a rate bar but a POOLED
one with no per-set clause, so it takes no advisory member either. **These are the memo's
baseline denominators, not the record's: 21.24 re-applies `1/n > |target − baseline|` to each
per-set clause on the numbers it recorded and labels the result before reading the verdict.**

### 4.3 The reporter bars' premise, and its VOID condition [PROPOSED — ratified at merge]

Bars 3 and 4 read as INJUSTICE cells only because the reporter is innocent by construction, and
the construction has two halves.

**The structural half.** No impostor path files a report. `agents/tactical/impostor_policy.py`:53
states the rule outright — in the `KILL → COVER` edge "the impostor must not file a report" — and
the two `ReportBodyIntent` emitters in the tree are both crew-side:
`agents/tactical/crewmate_policy.py`:737-740 (the scripted default these bytes were recorded
with) and `agents/tactical/learned/crew_forward.py`:1086-1091 (18.7's opt-in learned CREW
surface, gated, not the default). This is a property of the scripted FSM policies these bytes
record, which is exactly why the void condition below guards the case a **15.9-class learned
mover** would create rather than a coincidence in the corpus.

**The measured half.** `killer_self_reported` reads **0 on all four sets** at this HEAD
(`tests/eval/test_funnel.py`:638 pins the samples/9p2i cell) and `reporter_impostor_meetings`
reads **0 of 620** (`tests/eval/test_reporter_justice.py`:78-79).

**VOID.** If any recorded leg shows an impostor reporter, the premise has MOVED and bars 3 and 4
are **VOID — not passed and not missed.** The record audit reads, per leg and **before** either
bar:

* `eval.funnel.InformationFunnelReport.killer_self_reported == 0`, and
* `reporter_ejected == reporter_ejected_innocent` (`eval/funnel.py`:910-912), and
* `eval.reporter_justice.ReporterJusticeCells.reporter_impostor_meetings == 0`, and
* **the TWIN AGREES** —
  `eval.funnel.InformationFunnelReport.reporter_ejected_innocent ==
  eval.reporter_justice.ReporterJusticeCells.reporter_innocent_ejections`, **per leg AND
  pooled.**

A leg that breaks any of the four voids both reporter bars for the whole record. A VOID is
published as a VOID and never absorbed into either verdict branch.

**The twin's agreement is a VOID condition, not a footnote.** I-3 is registered in §2 and §3.1
precisely because two independently authored readers arriving at the same 34 is bar 3's strongest
provenance. A record on which they DISAGREE has lost that provenance, and reading bars 3 and 4
anyway would let a graduation ride a number whose only corroboration had just failed. So the
disagreement voids the reporter bars rather than being reported beside them, and the record audit
prints both readings, per leg and pooled, whether they agree or not.

## 5. Secondary cells (observed, reported, never gated)

Reported in the record audit beside the bars; **none of them can decide the verdict.**

* **The win split, inside a pre-registered band of ±15 points per set.** Baseline-8 impostor win
  rates re-derived from each set's committed `MANIFEST.md` `winner` column via
  `scripts.check_doc_facts.parse_manifest` rather than quoted from prose [VERIFIED]:
  **`samples/9p2i` 15/50 = 30%, `ml_corpus/9p2i` 36/150 = 24%, `samples/4p1i` 18/50 = 36%,
  `ml_corpus/4p1i` 13/50 = 26%.** A leg outside its band is reported, and §7 explains why it
  cannot attribute.
* **The solvability y-axis (I-5)** — containment 557/620 pooled, singleton rate and correctness,
  and ejections landing on an already-cleared player 63/377 pooled. Reader:
  `eval/solvability.py`:395 / `scripts/measure_baseline.py --solvability --json`.
* **The zero-flag conviction cells (I-6)** — `eval/vj_instruments.py`:312-327, the committed
  reading of the register's "37 of 42 ejectees carried no contradiction flag". At baseline 8:
  **86 of 429 convictions carry no flag, 37 of them CREW and 49 IMPOSTOR** — so 37 of the 46
  innocent ejections are flagless. Reader: `scripts/measure_baseline.py --vj --json`.
* **The evidence-honesty cells (I-4)** — false crew self-placement, the sole-flag precision
  cells and the grounded sighting sides. Reader: `eval/evidence_honesty.py` /
  `scripts/measure_baseline.py --honesty --json`.
* **The render census** — `eval.evidence_honesty.RenderBudgetCells`. Baseline 8 on
  `samples/9p2i` [VERIFIED]: **1,740 snapshots, 63,624 rendered rows, mean 36.5655, 25,628
  testimony rows** (buckets ≤4: 6,882; 5-6: 17,340; ≥7: 1,406). Reported per bucket and never as
  one blended number.
* **Token cost per meeting call** — the Wave-2 blocks add tokens (§8's +61,750-byte ballot
  interaction is the priced example); reported, not gated.

### 5.1 Measured but not registered

**What this memo may not do is invent a cell.** The 2026-08-26 register measured a great deal
this repository cannot recompute; a bar anchored to a figure nobody here can re-run cannot judge
a record, which is precisely the defect 20.22 existed to remove. Each class below is quoted in
its **VERIFIER-CORRECTED** form, not as originally filed.

| class | verifier-corrected reading | why it is not registered |
|---|---|---|
| the 42-row innocent-ejection ledger (A-10) | class totals reporter 30 / boomerang 29 / impossible-transit 17 / impostor-rides-the-herd 33 / weak-flag 5 / guard-redirect 4 / forced endgame 5, over a baseline-7 population; the filing's "only 4 of the 42" is wrong on its own ledger — **SIX** rows carry nothing beyond herd and/or transit, of which only **THREE** are pure herd; and two supporting cells drift by one under a different tie-break and must be quoted as approximate | no committed reader emits a per-row class ledger. `audits/audit-phase-21-counterfactual.md` §2.1 re-derives the classes at baseline 8 (RC 34, BOOM 33, IMP-RIDES 36, ENDGAME 12, WEAKFLAG 8, REDIRECT 3, PIT 20 of 46) through `scripts/counterfactual_phase21.py`, and §2.4 rules the overlap a JOIN rather than three censuses (BOOM ⊂ RC, union 44 of 46) — an offline census, not an instrument |
| the counter-accusation boomerang (A-11) | the verifier **DROPS** the "0 of 387 impostor ejections" contrast as a tautology (the opener is the trigger actor in 668/668 and the trigger actor is a crewmate in 668/668) and re-prices the shape at **29/492 = 5.9% overall** and **29/271 = 10.7%** within the no-vent-flag half against **1/71 = 1.4%** without it | same — no committed reader; the class is a session walk |
| the impossible-transit charge (A-12) | the verifier **REPLACES** "provably false every time" (the test performed is true by construction for every crewmate) and re-prices the within-stratum enrichment at **15/19 = 78.9%** against a **42/103 = 40.8%** base = **1.9x**, with the ≥half figure **15/42 = 35.7%** | same |
| the citation mix of the ejecting ballots (A-10) | 79 hearsay / 40 own-observation / 26 own-turn of 145 ejecting ballots at baseline 7 | same; `audits/audit-phase-21-counterfactual.md` §4.3 publishes the baseline-8 re-derivation (C-5…C-7) offline |
| the per-turn calibration decomposition (A-19) | the verifier **REFUTES** the pooled "turn ≥ 2 is pure noise" headline by a decomposition the filing never ran — same-target turn ≥ 2 crew accusations hit 79.2% (n=48) and 88.5% (n=122) against different-target 4.7% (n=106) and 3.1% (n=287); the pooled lift is a mixture artifact and the ML advice is **WITHDRAWN** | same |

**The routing rule** [PROPOSED — ratified at merge]: **a class the owner wants gated becomes an
instrument contract that merges BEFORE the record, or it stays observed.** A number typed into
this memo from a session walk is not a bar; a pin this memo needs but does not have is a finding
for that instrument contract.

## 6. The decision rule [PROPOSED — ratified at merge]

**ADOPTED** (the three Wave-2 levers graduate; the ladder tip moves to baseline 9) **iff all four
of bars 1, 2, 3 and 4 are met on the recorded bytes.** **FINDING** (the levers stay toggles; the
tip stays at baseline 8; the bytes and the read are committed as the finding record) **otherwise.**

The rule is CONJUNCTIVE and names its subset exactly: bars 1 AND 2 AND 3 AND 4 — there is no
"and/or", no waiver and no substitute. If §4.3's premise breaks on any leg, bars 3 and 4 are
**VOID**, which is not "met", so the conjunction fails and the verdict is FINDING with the VOID
published as its own line.

**Partial adoption is a per-lever VERDICT, never a partial graduation — and the verdict is a
RENDER verdict, because no bar maps to a single lever.** §7 declares that no bar may be attributed
to a lever, and `audits/audit-phase-21-counterfactual.md` §7 puts all four bars' cells
(R-3 / R-4, P-1, P-2) on its NOT-PREDICTABLE-OFFLINE list. An eligibility test that asked whether
the counterfactual predicted a lever's own BAR cell would therefore be unsatisfiable by
construction, and an eligibility test that assigned one bar to one lever would assert an
attribution this memo forbids. The test is stated so it can actually be run:

A lever is ELIGIBLE when, conjunctively:

1. **its own RENDER predictions held on the recorded bytes** — `reporter_reasoning` against
   `audits/audit-phase-21-counterfactual.md` **§8.1**, `corroboration_discipline` against that
   memo's **§8.2**, `testimony_shapes` against its **§8.3**, each read as the per-lever
   prediction table states it and each falsifiable from the recording alone;
2. **none of the seven tripwires in THIS memo's §8.1 fired against it** — for `testimony_shapes`
   that includes T1 and T5, the two NEVER-WORSE BARS; and
3. **it is independently stampable**, which the one-resolver-per-lever registry
   (`orchestrator/replay.py`:675-682) guarantees.

(The two documents both number a section 8.1 and they are different things: the counterfactual's
is its `reporter_reasoning` prediction table, this memo's is the tripwire dispositions. Each
reference above says which.)

**Eligibility decides nothing about the bars and graduates nothing.** It is published as a
per-lever line in the record audit — "this lever rendered what it was predicted to render, and
nothing got worse where it touched" — so that a FINDING verdict still records which levers
behaved.

**An eligible lever keeps its default-OFF gate.** The
reason is mechanical, not stylistic: `api/replay_loader.py::_assert_substrate_matches` (:655)
compares a recording's stamped slate against `orchestrator.replay.substrate_flag_snapshot()`
across every `SUBSTRATE_FLAG_KEYS` entry and fails loud on any difference. Graduate a SUBSET and
both records break — the graduated keys become unconditionally True, so the baseline-8 recordings
that stamp them OFF stop reconstructing, while the ungraduated levers were ON in the baseline-9
recording and those bytes would replay only with their `AILIBI_*` variables exported. A ladder
tip no bare environment can reconstruct is not a tip. Under ADOPTED all three graduate together
(`orchestrator/replay.py`:613-635 grows from twenty-one retired keys to twenty-four and :675-682
falls from four live toggles to one); under FINDING all three stay toggles; there is no third
substrate. An eligible lever's ON-path evidence is carried forward — published,
counterfactual-predicted — and it graduates at the next record made at its own slate.

**Advisory cells never enter this rule, and the per-set clause has ONE authority.** The verdict
reads each bar's pooled figure plus bar 1's own per-set clause, and nothing else. **That clause is
the inherited literal `n ≥ 30` (§4, bar 1) — NOT §4.2's granularity test**, and the distinction
decides cases: on baseline-8 denominators the two disagree on `samples/9p2i` (n = 27), where the
granularity test says POWERED and the ratified clause says not. Reading §4.2 here would let a set
the ratified clause excludes turn an otherwise passing bar 1 into a miss. **§4.2 governs only
which cells are published as ADVISORY; §4's `n ≥ 30` governs which per-set floor BINDS**, and
21.24 applies it to the record's own denominators.

**A tripwire is never a graduating bar.** §8's seven tripwires are STOP conditions and, for two
of them, NEVER-WORSE BARS. **No tripwire can carry an ADOPTED verdict on its own**, and a
tripwire that holds contributes nothing to the conjunction above.

**No bar may be re-priced after this merge, and a miss is reported as a miss.** The record audit
states each bar's before, after and verdict on one line; "adopt anyway" is the single outcome
21.24 must not produce. **The phase-20 owner override is not a precedent for re-pricing:** an
override is recorded as an override of a FINDING verdict and leaves the arithmetic exactly where
it stands.

## 7. The declared co-interventions

**What lands inside this record that is not a Wave-2 lever.** The 21.24 record runs on the
CORRECTED substrate, which means every repair the 21.15 re-record already carries is inside the
same bytes as the three levers. They are named here so no bar can be attributed to a lever by
default.

**The attribution consequence, stated so it cannot be renegotiated:** because the corrected
substrate and the three Wave-2 levers land in one record, **no bar may be attributed to a lever
on the strength of the win split.** Attribution rests on (a) the offline counterfactual over
FROZEN baseline-8 bytes (`audits/audit-phase-21-counterfactual.md`), which holds the substrate
constant by construction, and (b) the recorded per-cell before/after. The win split is a §5
secondary and is never a bar.

**And the baseline-8 record's own UN-PRE-DECLARED movements, each cited to
`audits/audit-phase-21-rerecord.md`** — these are movements the maintenance record's §0 named in
neither its expected-to-move nor its expected-to-hold list, and they are co-interventions in
exactly the sense that matters here: they moved the "before" this memo prices against.

| movement | before → after | citation |
|---|---|---|
| the sole-flag wrongful-conviction class **RE-OPENED** | **0 → 4** victims, all four CREWMATES, **one still carrying a STRONG flag** under the full slate | §5.1.1 |
| the I-13 injustice fixtures | **4/4 FLIPPED → 3/4 flipped + 1 partial** — fixture (b), content-vs-own-memory miss, `9p2i` seed 12 M0, held its evidence half and regressed its outcome half, ejecting the crewmate p-5 | §5.1.1b |
| the STRONG `alibi_vs_sighting` prosecution class | 11 / 12 → **21 / 27** — grew | §5.1.2 (b) |
| the oracle-register leak class, all four sets | non-zero → **ZERO** — the one unambiguously good movement | §5.1.2 (c) |
| the impostor false-whereabouts arm | **INVERTED**: 0/106 impostor against 6/660 crew on `samples/9p2i` (the old comment had it at ~twice the crew rate and was backwards) | §5.1.2 (d) |
| `weak_flag_only_impostor` on `samples` | 0 → **1** | §5.1.2 (e) |
| the `_COALESCED_ROW_PIN` margin | 37.05 → **36.59** against a **36.0** floor — margin 1.05 → 0.59, **MARGIN WATCH** | §5.1.2 (f) |

**"No surface may keep asserting the extinction."** §5.1.1's constraint binds every sentence of
this memo the way §6.1's does: the sole-flag wrongful-conviction class is not extinct on baseline
8, and nothing here says or implies that it is.

**Plus the 21.17 ML re-ground**, which landed between the baseline-8 record and this memo and is
declared here for the same reason: it is inside the tree the record runs from and is not a
Wave-2 lever.

## 8. The offline-counterfactual protocol, and the tripwire dispositions

**The protocol.** `audits/audit-phase-21-counterfactual.md` (#418) was published BEFORE this
merge and is quoted by section, never recomputed here. It reproduces at `$0` with
`uv run python scripts/counterfactual_phase21.py --sets all` (28.7 s, no network, §11 there), and
its own §7 names what no offline instrument can reach: **the reporter-conviction count (R-3,
R-4), non-direct conviction accuracy (P-1) and the innocent-ejection count (P-2) are all on that
list** — which is exactly why its ON column can never pre-empt a bar. Its governing sentence
(§0) is the one this memo inherits: **a sentence added to a prompt is not a vote that changes.**

Its four reading rules (§1.3) carry over as read: exposure is an UPPER BOUND; PIT is a judgement
net in both readings; the `[ADV]` ≤ 20-case rule is keyed on the CELL's denominator; and every
ingest and render reading is a ONE-STEP-AHEAD reading at each recorded boundary.

### 8.1 The tripwires, dispositioned by name [PROPOSED — ratified at merge]

All seven of §9's CANDIDATES are dispositioned; none is left unmentioned. **A tripwire is a STOP
or a never-worse bar, and is NEVER a graduating bar** (§6). Every one of them is falsifiable at
**21.23's first ON seed**, and the reader for all seven is `scripts/counterfactual_phase21.py`
(the cell ids below are its own, at :1483, :1496, :1508, :1621, :1699, :1711, :1756, :1793).

**Each tripwire is registered as a SAMPLE-LOCAL PREDICATE, not as a frozen population count**
[PROPOSED — ratified at merge]. This is the one place the counterfactual's §9 wording cannot be
adopted verbatim, and the reason is arithmetic: 21.23 is a **five-seed** smoke, so it cannot
literally read 620 of 620 openings or 2,715 of 2,715 speech turns, and a STOP condition phrased on
the 300-game totals would make a CORRECT smoke read "off its predicted value" and ABANDON — or
force the operator to reinterpret a ratified criterion at the terminal. The predicate below is
what any run is judged against, at any n; the baseline-8 population figure is printed beside it as
a REFERENCE only, for both runs (see the note under the table).

**One tripwire needs a reader that does not exist yet, and it is named rather than assumed.** T5's
predicate has two halves — every observed CREW speech turn gains the block, and ZERO impostor
turns do — and `scripts/counterfactual_phase21.py`'s `T-9` row emits only the AGGREGATE
`changed[accusation_round] / rendered[accusation_round]` (:1756-1766) with **no speaker-role
split**. Two offsetting errors — a crew turn missing the block while an impostor turn gains one —
leave that aggregate unchanged, so T-9 alone cannot falsify the predicate it is registered
against. Per §5.1's routing rule the fix is a reader, not a number: **21.23's smoke report must
publish the accusation-round render census SPLIT BY SPEAKER ROLE**, joining each recorded
`accusation_round` prompt to its speaker's role from the recording, and T5 is evaluated on that
split. §9.1 carries it as a precondition. Until that split is published T5 is UNREAD, which is a
STOP in its own right — an unevaluable never-worse bar may not be recorded as satisfied.

| id | cell | **the predicate any run must satisfy** | the baseline-8 population, for reference | disposition |
|---|---|---|---|---|
| **T1** | `T-7` — spoken vent accounts naming a player who never vented | **the count is 0**, whatever the denominator | 0 of 512 OFF | **RATIFIED as a NEVER-WORSE BAR *and* a pre-record STOP.** A non-zero ON reading means an ON arm mints fabricated vent accounts — the record has made something worse, and it must not start (or must stop) |
| **T2** | `R-13` / `R-14` — reporter openings and non-reporter speech turns gaining the reporter block | **every observed body-report opening gains the block, and every observed non-reporter speech turn in a body-report meeting gains it — 100% of each observed denominator, and no emergency-meeting prompt gains either** | 620/620 openings and 2,715/2,715 speech turns | **RATIFIED as a pre-record STOP.** A share below 100% on an ON seed means the lever did not thread and the record must not start. Declined as a bar |
| **T3** | `R-15` — ballots gaining a reporter block | **the count is 0**, whatever the ballot denominator | 0 of 3,631, in both columns | **RATIFIED as a pre-record STOP.** A non-zero reading means the reporter lever reached a seam it does not own. Declined as a bar |
| **T4** | `T-6` — location accounts reaching the alibi map | **100% of observed location accounts reach the map under ON** (and the OFF reconstruction of the same run is strictly below it) | 1,016/4,173 = 24.35% OFF → 4,173/4,173 = 100% ON | **RATIFIED as a pre-record STOP.** A partial fill means the widened `("alibi","whereabouts")` gate did not land. Declined as a bar |
| **T5** | `T-9` **split by speaker role** — see the note above; the aggregate `T-9` cannot read this predicate | **every observed CREW speech turn gains the block and the IMPOSTOR count is 0**, whatever the denominators | 2,023 of 2,959, with 0 impostor turns | **RATIFIED as a NEVER-WORSE BAR *and* a pre-record STOP.** An impostor turn gaining the block is a FIREWALL question, not a render one, and the record must not start (or must stop). **UNREAD until 21.23 publishes the role split (§9.1) — and UNREAD is itself a STOP** |
| **T6** | `C-9` — ballots gaining the source-count block | **every observed ballot gains the block except those whose meeting ledger holds no row for any of that voter's candidate targets** — the residue is enumerated, never estimated | 3,614 of 3,631 = 99.5% ON | **RATIFIED as a pre-record STOP.** A shortfall the residue rule does not account for means the ledger is not being built where it should be. Declined as a bar |
| **T7** | `B-1` — rendered memory rows per prompt snapshot at meeting 1 | **the meeting-1 row count is byte-identical between the run's own OFF and ON columns** | 255,918/7,271, unchanged across all three columns | **RATIFIED as a pre-record STOP.** A first-meeting memory-row diff means prose is displacing memory, which this slate must not do. Declined as a bar |

**How the two runs read the same predicate — and why the population column binds NEITHER.**
21.23's smoke evaluates each predicate over the seeds it recorded, and a shortfall STOPs the
record before it starts. 21.24 evaluates the SAME predicates over its own bytes. **The population
column is informational for both runs and is never a criterion**, including at 300 games: a
lever-ON record changes what the model says, and what the model says changes how long games run,
how many meetings they hold, how many speech turns and ballots those meetings produce, and how
many location accounts exist to reach the map. Every one of those is an OPPORTUNITY count, so
620 openings, 2,959 speech turns, 3,631 ballots and 4,173 location accounts can all legitimately
differ on the adopting record while every predicate holds. **Stopping a correct record because
its own behaviour changed a denominator would be the opposite of what these tripwires are for.**
The predicate is the ratified criterion; the population figure is the baseline-8 reference,
published beside the reading and never compared against it.

**The two NEVER-WORSE BARS, stated as such.** T1 and T5 are the only guards this pre-registration
carries against the record making something worse while the four primary bars improve. Each is a
one-sided bar on a COUNT, which is why neither needs a denominator to be judged: T1's fabricated
vent-account count may not rise above 0, and T5's impostor-turn count may not rise above 0.
Neither can contribute to ADOPTED; each can only stop the record or fail it.

## 9. The record order, the freeze, the slate and the preconditions

**The record order** (21.24): `replays/samples/9p2i` → `replays/ml_corpus/9p2i` →
`replays/samples/4p1i` → `replays/ml_corpus/4p1i`, each checkpoint-pushed per completed seed
range.

**The corpus 9p2i leg precedes either 4p1i leg because that is where the power is**, argued from
this memo's own re-anchored denominators: bar 1's non-direct cell is **n = 61** in the corpus
against **n = 27** in the samples, and the two 4p1i sets contribute **n = 5** and **n = 3**. The
corpus leg alone carries **61/96 = 63.5%** of the whole. A delta on n = 27 will not separate —
14/27 = 0.5185 [0.3399, 0.6926] is more than a third of the scale wide, against the corpus cell's
32/61 = 0.5246 [0.4016, 0.6447]. **If the window forces a choice, the two 4p1i legs are the ones
that yield.**

**The freeze.** `agents/`, `meetings/`, `observation/`, `orchestrator/` and
`agents/strategic/prompts/` are frozen for the record. Bytes under `replays/` never move at a
pre-registration gate and no `eval/` module is added, changed or redefined here.

**The slate: the THREE Wave-2 keys ON, `impostor_roll_call` OFF.** Read from the lever registry
in the tree rather than from any contract's prose: `orchestrator/replay.py`:613-635
(`_RETIRED_ALWAYS_ON_LEVERS`, **twenty-one** keys) and :675-682
(`_TOGGLEABLE_LEVER_RESOLVERS`, **FOUR** live toggles in registration order —
`impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`, `testimony_shapes`), all
default-OFF. The registered slate is therefore **`reporter_reasoning` = True,
`corroboration_discipline` = True, `testimony_shapes` = True, `impostor_roll_call` = False** —
the slate 21.21's counterfactual measured (its R7 ruling refuses a fourth key) and the slate
21.24 records. Three surfaces must agree on this and **this memo is the one that governs.**

**Model and prompt-set version are read from the tree and from the RECORDED MANIFESTs, never
from the registry's prose:** model `Qwen/Qwen3.6-27B` non-thinking via Featherless, `$0` on the
flat-rate subscription; prompt set `qwen3_6_27b`, whose committed sets stamp **v5** in all four
`MANIFEST.md` files at this HEAD (§3.2 records that the 21.22 contract's own text says v4 and is
stale).

### 9.1 PRECONDITIONS the record cannot start or finalize without

* **21.23's recorder fix** — `scripts/record_ml_corpus.sh`'s hardcoded `REQUIRED_PROMPT_VERSIONS`
  at **:170** (the four v5 literals) would refuse ANY lever-ON record **at finalization**, i.e.
  after roughly 22 hours of 21.24's spend. The failure mode is terminal and lands at the end.
  Routed at the #414 merge to be **fixed AND smoke-validated at 21.23**, deriving through
  `prompt_versions_for_set` from `--expect-levers`. **This is a written PRECONDITION the 21.24
  operator CONFIRMS before the first seed** — not a known risk carried into the run.
* **21.23's accusation-round render census, SPLIT BY SPEAKER ROLE** — T5's predicate is "every
  observed CREW speech turn gains the testimony-shape block and ZERO impostor turns do", and no
  committed reader emits that split today: `scripts/counterfactual_phase21.py`'s `T-9` row is an
  aggregate over `accusation_round` prompts (:1756-1766) in which a missing crew block and a
  gained impostor block cancel. The smoke must publish the census joined to each speaker's
  recorded role. **Until it does, T5 is UNREAD and the record does not start** (§8.1).

Named as **21.24's own re-anchor business rather than this memo's**: the version/environment
generalisation (#415), the Q2 seam and the `testimony_shapes` stamp-vs-environment guard
asymmetry (#416/#417), and the roll_call sibling-block gap.

### 9.2 Abandon criteria — written STOP conditions

* a `scripts/validity_gate.py` FAIL on any leg;
* a seed whose opening defaults (the `(deadline_default)` watch item);
* a guard trip;
* a lever-stamp mismatch between the recorded snapshot and the declared slate, compared through
  `orchestrator.replay.substrate_slate_mismatches` and **never re-derived**;
* any of the seven §8.1 tripwires failing **its predicate** — the sample-local criterion in
  §8.1's third column, evaluated over whatever the run actually recorded. A denominator smaller
  than baseline 8's is expected at the smoke and is NOT a trip.

## 10. THE RATIFIED DECISION (owner) — the pre-registration

**LOCKED DECISION (owner, ratified by the merge of Task 21.22's PR — the 15.18 convention):**

* **Instrument list = the six §2 rows**, definitions adopted by reference from the modules that
  compute them, **except for I-2's share, where the §2 wording and the cell it names govern**:
  bar 4's numerator is `reporter_innocent_ejections`, not every reporter ejection. A new
  instrument, or a changed definition, enters only through §11 and only before the record.
* **Baseline cells = §3 exactly**, with §3.2's four pin-over-other-reading replacements and their
  stated causes.
* **Bars = §4 exactly**, four of them. Bars 1 and 2 are inherited VERBATIM with unchanged targets
  and each carries its phase-20 MISS on its own row. Bars 3 and 4 are the reporter pair, stated
  jointly with the SHARE-BY-DILUTION label, and §4.1's machine-readable table is the form 21.24
  reads. **The §4.2 advisory discipline is part of the bars**, and so is §4.3's premise and its
  VOID condition.
* **The `n ≥ 30` powered clause is carried VERBATIM** (§4), ratified explicitly, with the
  granularity test's disagreement on `samples/9p2i` printed beside it and the clause re-applied
  to the RECORD's own denominators at the record.
* **Decision rule = §6 exactly**: ADOPTED iff **bars 1, 2, 3 and 4** are all met on the recorded
  bytes, FINDING otherwise — conjunctive, with no waiver and no substitute; a per-lever
  eligibility VERDICT on the levers' own §8 RENDER predictions and never a partial graduation; no
  bar re-priced after this merge; a miss published as a miss; and the phase-20 override
  explicitly not a precedent for re-pricing.
* **Secondary = §5 exactly**: observed and reported, never gated; the win-split band is ±15
  points per set against the four re-derived MANIFEST rates.
* **Measured but not registered = §5.1 exactly**, with its routing rule: an instrument contract
  merged before the record, or the class stays observed.
* **Co-interventions = §7**: the corrected-substrate repairs, the seven un-pre-declared
  baseline-8 movements and the 21.17 ML re-ground, with attribution resting on the offline
  counterfactual plus the recorded per-cell before/after and never on the win split.
* **Protocol, tripwires, order, slate and preconditions = §8 and §9**, including the seven
  tripwire dispositions (T1 and T5 as NEVER-WORSE BARS and STOPs; T2, T3, T4, T6 and T7 as STOPs;
  none of the seven a graduating bar), the corpus-9p2i-first power argument, and 21.23's recorder
  fix as a confirmed precondition.
* **The standing rule = §1**: definitions, conventions, bars, advisory discipline, decision rule,
  co-intervention declaration, protocol and record order are the ratified content; the quoted
  cells re-anchor mechanically at 21.24 with provenance, without re-ratification.
* **Rejected — soften a target because a re-anchored baseline made it look harder.** Bar 1's gap
  went from 0.0078 to 0.0792 and bar 2's ask from −8 to −12 when the substrate was corrected.
  Re-pricing either would make the target a function of the baseline it is supposed to judge.
  Rejected: the pin replaces the cell, the target does not move.
* **Rejected — re-derive the `n ≥ 30` clause from the moved denominators.** `samples/9p2i` fell
  to n = 27 and the granularity test disagrees with the literal clause there. Re-deriving a power
  threshold from a moved baseline is the same defect in a different coat. Rejected: the clause is
  carried verbatim and the disagreement is published.
* **Rejected — register a review class no committed reader emits.** The ledger, the boomerang,
  the transit charge, the citation mix and the calibration decomposition are §5.1's members. A
  bar anchored to a figure nobody in this repository can re-run cannot judge a record.
* **Rejected — defer ratification to the record.** Bars written after the recordings exist are
  fitted to them.
* **Evidence:** §3 (the committed cells and their pins), §3.2 (the pin-over-other-reading
  reconciliation), §12 (the reproduction commands and the pin-diff reader).

**Sign-off.** Ratification rides the merge of Task 21.22's PR: **the owner ratifies the MERGED
text.** Nothing in this memo is normative before that merge. 21.23 and 21.24 read it verbatim;
anything after the merge is a dated erratum in §11.

## 11. Amendment log

| date | what changed | why | ratification vehicle |
|---|---|---|---|

*(No rows at merge.)*

Convention: an amendment is any change to the §10-ratified set — instrument list, definitions,
baseline cells, bars, advisory discipline, secondary list, measured-but-not-registered list,
decision rule, co-intervention declaration, protocol, tripwire dispositions, record order,
slate or preconditions. Each amendment is a row here plus the edited section, shipped in an
owner-merged PR — **the merge is the re-ratification.** Amendments land BEFORE the record or not
at all for this phase's claims. **A cell re-quote at the adopting record is NOT an amendment and
takes no row** (§1).

## 12. Method + reproduction (all `$0` against committed bytes, offline)

Every cell in §3 and §5 is re-runnable. The pins:

```bash
uv run pytest -q -k "deduction_metrics or funnel or evidence_honesty or solvability or reporter_justice"
```

The readers:

```bash
uv run python -m eval.reporter_justice \
  replays/samples/9p2i replays/ml_corpus/9p2i replays/samples/4p1i replays/ml_corpus/4p1i --pooled
uv run python scripts/measure_baseline.py --funnel --json replays/samples/9p2i
uv run python scripts/measure_baseline.py --solvability --json replays/ml_corpus/9p2i
uv run python scripts/measure_baseline.py --vj --json replays/samples/4p1i
uv run python scripts/measure_baseline.py --honesty --json replays/ml_corpus/4p1i
```

**The pin-diff reader.** The whole memo checked against the instruments in one pass, offline:
every §3.1 cell recomputed from `eval/deduction_metrics.py`, `eval/reporter_justice.py`,
`eval/funnel.py`, `eval/solvability.py`, `eval/vj_instruments.py` and
`eval/evidence_honesty.py`; every quoted Wilson interval re-run through the production helper;
§4.1's machine-readable bar table checked against the prose bars AND against the recomputed
baselines; §5's win split re-derived from the MANIFESTs; the render census re-derived from
`render_budget`; §3.1's row inventory asserted so a deleted row is a failure rather than a silent
pass; and §3.2's deliberate divergences asserted still to carry BOTH numbers. It prints one line
per cell — memo value, recomputed value, `OK` or `MISMATCH` — records mismatches rather than
asserting them (`python -O` strips asserts, and a gate that vanishes under an interpreter flag is
not a gate), prints `0 mismatches` and **exits 0 only then.** Task 21.22's PR pastes its output.

The interval check closes the CLASS, not the instance: every bracketed pair outside §3.2 must
belong to a claim the reader re-runs, so a value in a spelling the parser skips is a failure
rather than a silent omission — and §3.2, whose whole job is to write out an interval the helper
does NOT produce, is excluded from that count and pinned by name instead, so it cannot be used to
smuggle an unchecked value past the gate. Every text check is scoped to the memo BEFORE §12, so
this reader — quoted inside the memo — cannot satisfy its own checks.

**Fifteen perturbations, every one verified to bite, the last under `-O`:**

| perturbation | what the reader prints |
|---|---|
| a changed cell digit (`20/95` → `21/95`) | `I-6 zero-flag convictions [samples/9p2i]: (21, 95) != (20, 95)` |
| a changed interval | `interval 34/46: 0.7391 1.0000 1.0000 != (0.7391, 0.5974, 0.844)` |
| an interval re-spelled out of the parsed shape (`[0.0037, 0.0112]` → `[0.0037,0.0112]`) | `16 intervals quoted but only 15 are in a shape this reader can re-run` **and** `only 15 intervals parsed` |
| a deleted §3.1 row | `table inventory: 14 rows, expected 15` |
| a target moved in §4.1's TABLE | `bar 3: the table's target is not '**≤ 12 pooled**'` **and** `bar 3: §4's prose states ≤ 12.0 but §4.1's table says ≤ 16.0` |
| a target moved in §4's PROSE, table left alone | `bar 3: §4's prose states ≤ 13.0 but §4.1's table says ≤ 12.0` |
| **bar 3's and bar 4's prose targets SWAPPED** (the SET of targets is unchanged) | `bar 3: §4's prose states < 0.4 but §4.1's table says ≤ 12.0` |
| a target moved in §0's verdict line | `§0's verdict line states [… ('<', 38.0) …] but §4.1's table says [… ('<', 35.0) …] -- in bar order` |
| §6's conjunctive subset narrowed | `§6 no longer reads 'ADOPTED iff bars 1, 2, 3 and 4 are met ... FINDING otherwise'` |
| **§6's verdict branches INVERTED** (ADOPTED ↔ FINDING) | the same message — the regex binds each branch to its own condition |
| **§6 gains a waiver** ("at least three of them suffice") | `§6 has gained a disjunction or waiver: 'at least three'` |
| §10's ratified list narrowed | `§10's ratified list no longer states 'ADOPTED iff **bars 1, 2, 3 and 4**'` |
| §4.3's twin VOID condition dropped | `§4.3's VOID list no longer names 'the TWIN AGREES'` |
| §4.3's `killer_self_reported` condition dropped | `§4.3's VOID list no longer names 'killer_self_reported == 0'` |
| §3.2's two divergent bounds collapsed into one | `interval: §3.2 no longer states '[0.4224, 0.6178]'` |
| the same re-spelling under `uv run python -O` | both interval messages; still exits 1 |

**The target diff is BOUND TO BAR IDS, not to a set of values.** §4.1's table, §0's verdict line
and §4's prose bars are all ratified content the record reads verbatim, so the reader splits §4
into per-bar blocks, compares each block's own arrow with ITS table row, and requires §0's four
arrows to match the table **in bar order**. An unlabelled set would prove only that all four
values occur somewhere — swapping bar 3's and bar 4's targets leaves such a set identical while
the normative prose assigns both reporter targets to the wrong cells. **Likewise the decision
rule is checked for its DIRECTION, not its vocabulary**: the regex binds ADOPTED to the
all-four conjunction and FINDING to the fallback, so inverting the branches or adding a waiver
fails even though the phrase "bars 1, 2, 3 and 4" survives.

```bash
uv run python - <<'EOF'
import re
from pathlib import Path

from eval.deduction_metrics import _wilson_interval
from eval.evidence_honesty import compute_evidence_honesty
from eval.funnel import compute_information_funnel
from eval.meeting_quality import TournamentEvalReport
from eval.reporter_justice import compute_reporter_justice, pool_reporter_justice
from eval.solvability import compute_solvability_report
from eval.vj_instruments import compute_vj_instruments
from scripts.check_doc_facts import parse_manifest

MEMO = Path("audits/audit-phase-21-preregistration.md")
SETS = ("samples/9p2i", "ml_corpus/9p2i", "samples/4p1i", "ml_corpus/4p1i")
TEXT = MEMO.read_text(encoding="utf-8")
FLAT = re.sub(r"\s+", " ", TEXT)
mismatches: list[str] = []

REPORTS = {  # every instrument walks each committed set exactly once
    name: {
        "d": TournamentEvalReport.model_validate_json(
            (Path("replays") / name / "tournament-eval-report.json").read_text(
                encoding="utf-8"
            )
        ).deduction,
        "r": compute_reporter_justice(Path("replays") / name),
        "f": compute_information_funnel(Path("replays") / name),
        "s": compute_solvability_report(Path("replays") / name),
        "v": compute_vj_instruments(Path("replays") / name),
    }
    for name in SETS
}
POOLED = pool_reporter_justice(REPORTS[name]["r"] for name in SETS)


def computed(label: str, name: str) -> tuple[int, ...] | None:
    d, r, f = REPORTS[name]["d"], REPORTS[name]["r"], REPORTS[name]["f"]
    s, v = REPORTS[name]["s"], REPORTS[name]["v"]
    ct, mf = d.ejectee_proof_cross_tab, d.meeting_flag_cross_tab
    return {
        "I-1 direct-proof accuracy": (
            ct.proof_present_impostor, ct.proof_present_ejections),
        # The None sentinel is NOT zero: a set with no non-direct ejections has no
        # accuracy cell at all, and the memo must say so rather than state 0/0.
        "I-1 non-direct accuracy": (
            (ct.non_direct_accuracy.numerator, ct.non_direct_accuracy.denominator)
            if ct.non_direct_accuracy.denominator is not None
            else None),
        "I-1 innocent ejections": (
            mf.flagged_ejections_innocent + mf.unflagged_ejections_innocent,
            ct.ejections_total),
        "I-2 body-report meetings": (r.body_report_meetings, r.meetings),
        "I-2 reporter is a CREWMATE": (
            r.reporter_crewmate_meetings, r.body_report_meetings),
        "I-2 reporter innocent ejections": (
            r.reporter_innocent_ejections, r.innocent_ejections),
        "I-2 reporter ejected per slot": (r.reporter_ejections, r.reporter_slots),
        "I-2 innocent non-reporter per slot": (
            r.innocent_non_reporter_ejections, r.innocent_non_reporter_slots),
        "I-3 reporter_ejected_innocent (twin)": (
            f.reporter_ejected_innocent, f.report_meetings),
        "I-3 report_ejections (twin)": (f.report_ejections, f.report_meetings),
        "I-3 killer_self_reported (twin)": (f.killer_self_reported, f.report_meetings),
        "I-5 containment (killer in the candidate set)": (
            s.killer_in_set.numerator, s.killer_in_set.denominator),
        "I-5 ejections on an already-cleared player": (
            s.cleared_player_ejections.numerator,
            s.cleared_player_ejections.denominator),
        "I-6 zero-flag convictions": (v.zero_flag_convictions, v.convictions_total),
        "I-6 zero-flag CREW convictions": (
            v.zero_flag_crew_convictions, v.zero_flag_convictions),
    }[label]


NUM = re.compile(r"(\d+)/(\d+)")
# `n/a` in a cell means the instrument has NO cell there (the None sentinel), which
# is a different statement from `0/0` and is parsed as such.
stated: dict[str, list[tuple[int, ...] | None]] = {}
for line in TEXT.split("### 3.1")[1].split("### 3.2")[0].splitlines():
    row = [part.strip() for part in line.strip().strip("|").split("|")]
    if line.startswith("| I-") and len(row) == 6:
        stated[row[0]] = [
            None if part == "n/a" else tuple(int(v) for v in NUM.findall(part)[0])
            for part in row[1:5]
        ]

for label in stated:
    for name in SETS:
        want = computed(label, name)
        got = stated[label][SETS.index(name)]
        if got != want:
            mismatches.append(f"{label} [{name}]: {got} != {want}")
    print(f"OK  {label}: " + "  ".join(str(c) for c in stated[label]))

# Row inventory: a deleted table row is drift, not a silent pass.
EXPECTED_ROWS = 15
if len(stated) != EXPECTED_ROWS:
    mismatches.append(f"table inventory: {len(stated)} rows, expected {EXPECTED_ROWS}")
print(f"OK  table inventory, {len(stated)} rows")

# The four BARS. Each baseline is recomputed from the bar's OWN registered producer,
# never from a second instrument that merely agrees today: bar 2 is registered on
# `MeetingFlagCrossTab`, so it is pooled from the deduction reports even though
# `eval.reporter_justice` also reads 46 on baseline 8.
nd_n = sum(
    REPORTS[n]["d"].ejectee_proof_cross_tab.non_direct_accuracy.numerator or 0
    for n in SETS
)
nd_d = sum(
    REPORTS[n]["d"].ejectee_proof_cross_tab.non_direct_accuracy.denominator or 0
    for n in SETS
)
bar2 = sum(
    REPORTS[n]["d"].meeting_flag_cross_tab.flagged_ejections_innocent
    + REPORTS[n]["d"].meeting_flag_cross_tab.unflagged_ejections_innocent
    for n in SETS
)
if bar2 != POOLED.innocent_ejections:
    print(
        f"NOTE  bar 2's producers disagree: MeetingFlagCrossTab {bar2} vs "
        f"reporter_justice {POOLED.innocent_ejections} -- bar 2 reads its own"
    )
BARS = {
    1: (f"{nd_n}/{nd_d} = {nd_n / nd_d:.4f}", "**≥ 0.60 pooled**"),
    2: (f"{bar2}", "**< 35 pooled**"),
    3: (f"{POOLED.reporter_innocent_ejections}", "**≤ 12 pooled**"),
    4: (
        f"{POOLED.reporter_innocent_ejections}/{POOLED.innocent_ejections} = "
        f"{POOLED.reporter_share_of_innocent_ejections:.4f}",
        "**< 0.40 pooled**",
    ),
}
bar_table = TEXT.split("### 4.1")[1].split("### 4.2")[0]
for bar_id, (baseline, target) in BARS.items():
    row = [
        line for line in bar_table.splitlines() if line.startswith(f"| {bar_id} |")
    ]
    if not row:
        mismatches.append(f"bar {bar_id}: no row in the machine-readable table")
        continue
    if baseline not in row[0]:
        mismatches.append(f"bar {bar_id}: the table's baseline is not {baseline!r}")
    if target not in row[0]:
        mismatches.append(f"bar {bar_id}: the table's target is not {target!r}")
    print(f"OK  bar {bar_id}: baseline {baseline}, target {target}")

# §4.1's table is not the only normative statement of a target: §0's verdict line and
# §4's prose bars are read verbatim by the record too. So the table's targets and the
# prose's targets are diffed against each other, BOTH WAYS -- a target moved in one
# place and not the other is drift the record contract would read two ways.
TARGET = re.compile(r"(≥|≤|<|>)\s*(\d+(?:\.\d+)?)(%?)")
ARROW = re.compile(r"→\s*(≥|≤|<|>)\s*(\d+(?:\.\d+)?)(%?)")


def _norm(op: str, num: str, pct: str) -> tuple[str, float]:
    """A target as (operator, value); percentages and fractions compare equal."""
    return op, (float(num) / 100 if pct else float(num))


table_targets = {}
for line in bar_table.splitlines():
    head = re.match(r"\|\s*(\d)\s*\|", line)
    if head:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        found = TARGET.search(cells[4])
        if found is None:
            mismatches.append(f"bar {head[1]}: the table row states no target")
            continue
        table_targets[int(head[1])] = _norm(*found.groups())

# §4's prose is split into PER-BAR BLOCKS and each block's arrow is compared with ITS
# OWN table row. An unlabelled set of targets is not enough: swapping bar 3's and
# bar 4's arrows leaves the set identical while the normative prose assigns both
# reporter targets to the wrong cells.
bar_prose = TEXT.split("## 4. Primary bars")[1].split("### 4.1")[0]
blocks = dict(
    zip(
        (int(m) for m in re.findall(r"\*\*Bar (\d) —", bar_prose)),
        re.split(r"\*\*Bar \d —", bar_prose)[1:],
    )
)
for bar_id, want in sorted(table_targets.items()):
    block = blocks.get(bar_id)
    if block is None:
        mismatches.append(f"bar {bar_id}: §4 carries no prose bar with that id")
        continue
    found = [_norm(*m) for m in ARROW.findall(re.sub(r"\s+", " ", block))]
    stated = [_norm(*m) for m in TARGET.findall(re.sub(r"\s+", " ", block))]
    if found and found[0] != want:
        mismatches.append(
            f"bar {bar_id}: §4's prose states {found[0][0]} {found[0][1]} but §4.1's "
            f"table says {want[0]} {want[1]}"
        )
    elif not found and want not in stated:
        mismatches.append(
            f"bar {bar_id}: §4's prose block states no target matching §4.1's "
            f"{want[0]} {want[1]}"
        )
    print(f"OK  bar {bar_id} prose block states {want[0]} {want[1]:g}, as its table row does")

# §0's verdict line carries the same four, in bar order, and is checked the same way.
verdict = re.sub(r"\s+", " ", TEXT.split("## 0. Verdict in one line")[1].split("## 1.")[0])
headline = [_norm(*m) for m in ARROW.findall(verdict)]
if headline != [table_targets[b] for b in sorted(table_targets)]:
    mismatches.append(
        f"§0's verdict line states {headline} but §4.1's table says "
        f"{[table_targets[b] for b in sorted(table_targets)]} -- in bar order"
    )
print(f"OK  §0's verdict line states the same {len(headline)} targets, in bar order")

# §6's rule and §10's ratified list must name the same conjunctive subset AND the same
# verdict DIRECTION: phrase presence is not semantic agreement, so the ADOPTED branch
# must be the one requiring all four and FINDING must be the fallback.
RULE = re.compile(
    r"\*\*ADOPTED\*\*.{0,200}?\*\*iff (?:all four of )?bars 1, 2, 3 and 4 are met"
    r".{0,400}?\*\*FINDING\*\*.{0,300}?\*\*otherwise\.\*\*",
    re.S,
)
rule_text = re.sub(r"\s+", " ", TEXT.split("## 6.")[1].split("## 7.")[0])
if RULE.search(rule_text) is None:
    mismatches.append(
        "§6 no longer reads 'ADOPTED iff bars 1, 2, 3 and 4 are met ... FINDING "
        "otherwise' -- the branches or the conjunction have changed"
    )
for banned in ("or bar", "waiver is", "at least three", "at least two"):
    if banned in rule_text:
        mismatches.append(f"§6 has gained a disjunction or waiver: {banned!r}")
ratified = re.sub(r"\s+", " ", TEXT.split("## 10.")[1].split("## 11.")[0])
for phrase in ("ADOPTED iff **bars 1, 2, 3 and 4**", "FINDING otherwise", "inherited VERBATIM"):
    if phrase not in ratified:
        mismatches.append(f"§10's ratified list no longer states {phrase!r}")
print("OK  §6 and §10 agree on the conjunction AND on which branch each verdict is")

# The twin agrees with the primary, per set and pooled -- the §3.1 I-3 claim.
twin = sum(REPORTS[n]["f"].reporter_ejected_innocent for n in SETS)
if twin != POOLED.reporter_innocent_ejections:
    mismatches.append(f"twin {twin} != reporter_justice {POOLED.reporter_innocent_ejections}")
for name in SETS:
    if REPORTS[name]["f"].reporter_ejected_innocent != REPORTS[name]["r"].reporter_innocent_ejections:
        mismatches.append(f"twin disagrees per set on {name}")
print(f"OK  twin: eval.funnel and eval.reporter_justice both read {twin}, per set and pooled")

# §4.3's premise: the void condition's own cells.
for name in SETS:
    f, r = REPORTS[name]["f"], REPORTS[name]["r"]
    if (f.killer_self_reported, r.reporter_impostor_meetings) != (0, 0):
        mismatches.append(f"premise broken on {name}")
    if f.reporter_ejected != f.reporter_ejected_innocent:
        mismatches.append(f"premise: reporter_ejected != innocent on {name}")
print("OK  premise: killer_self_reported 0 and reporter_impostor_meetings 0 on all four sets")

# §4.3's VOID list is what the record audit reads before either reporter bar, so a
# condition dropped from it is a gate silently removed. All four must be named.
void = re.sub(r"\s+", " ", TEXT.split("### 4.3")[1].split("## 5.")[0])
for condition in (
    "killer_self_reported == 0",
    "reporter_ejected == reporter_ejected_innocent",
    "reporter_impostor_meetings == 0",
    "the TWIN AGREES",
):
    if condition not in void:
        mismatches.append(f"§4.3's VOID list no longer names {condition!r}")
if "four voids" not in void:
    mismatches.append("§4.3 no longer says how many conditions void the reporter bars")
print("OK  §4.3 names all four VOID conditions")

# Every bracketed pair in the memo must belong to a claim this reader re-runs --
# equality closes the CLASS, so no new spelling slips a value past the gate. The
# ONE exception is §3.2, whose whole job is to write out an interval the helper
# does NOT produce; it is excluded from the count here and pinned by name in the
# DELIBERATE block below, so it cannot be used to smuggle in an unchecked value.
CLAIM = re.compile(r"\*{0,2}(\d+)/(\d+) = (\d\.\d{4})\*{0,2} \[(\d\.\d{4}), (\d\.\d{4})\]")
BRACKET = re.compile(r"\[\s*\d\.\d{4}\s*,\s*\d\.\d{4}\s*\]")
prose = FLAT.split("## 12.")[0]
head, rest = prose.split("### 3.2", 1)
_reconciliation, tail = rest.split("## 4. Primary bars", 1)
scan = head + tail
intervals = CLAIM.findall(scan)
quoted_pairs = len(BRACKET.findall(scan))
if quoted_pairs != len(intervals):
    mismatches.append(
        f"{quoted_pairs} intervals quoted but only {len(intervals)} are in a shape "
        "this reader can re-run"
    )
if len(intervals) < 16:
    mismatches.append(f"only {len(intervals)} intervals parsed -- a claim went missing")
if len(BRACKET.findall(_reconciliation)) != 2:
    mismatches.append("§3.2 no longer carries exactly the two divergent bounds")
for num, den, rate, low, high in intervals:
    want = tuple(round(value, 4) for value in _wilson_interval(int(num), int(den)))
    if want != (float(rate), float(low), float(high)):
        mismatches.append(f"interval {num}/{den}: {rate} {low} {high} != {want}")
print(f"OK  {len(intervals)} intervals, all from _wilson_interval")

# §5's win split, re-derived from the committed MANIFESTs.
for name in SETS:
    rows = list(
        parse_manifest(
            (Path("replays") / name / "MANIFEST.md").read_text(encoding="utf-8")
        ).values()
    )
    wins = sum(1 for row in rows if row.winner.strip().upper() == "IMPOSTORS")
    if f"`{name}` {wins}/{len(rows)} = " not in prose:
        mismatches.append(f"win split {name}: the memo no longer states {wins}/{len(rows)}")
print(f"OK  win split, all {len(SETS)} sets re-derived from the MANIFESTs")

# §5's render census, re-derived from the instrument.
budget = compute_evidence_honesty(Path("replays/samples/9p2i")).render_budget
census = [
    f"{budget.snapshots:,}",
    f"{budget.rendered_lines_total:,}",
    f"{budget.rendered_lines_mean:.4f}",
    f"{budget.testimony_rows_total:,}",
] + [f"{count:,}" for count in budget.testimony_rows_by_living_bucket.values()]
for value in census:
    if value not in prose:
        mismatches.append(f"render census: the memo no longer states {value}")
print(f"OK  render census, {len(census)} figures re-derived from the instrument")

# §3.2's deliberate divergences must keep BOTH readings. Scoped to `prose` so this
# reader, quoted inside §12, cannot satisfy its own checks.
for cell, other, authoritative in (
    ("interval", "[0.4224, 0.6178]", "[0.4220, 0.6180]"),
    ("reporter class", "30 of 42 = 71.4%", "34 of 46 = 73.9%"),
    ("prompt version", "**v4**", "**v5**"),
    ("report emitter", "**ONLY**", "**two** emitters"),
):
    for side in (other, authoritative):
        if re.sub(r"\s+", " ", side) not in prose:
            mismatches.append(f"{cell}: §3.2 no longer states {side!r}")
    print(f"DELIBERATE  {cell}: {other} -> {authoritative}")

print(f"\n{len(mismatches)} mismatches")
for line in mismatches:
    print("  " + line)
raise SystemExit(1 if mismatches else 0)
EOF
```

The intervals — the production helper, never by hand (the 18.4 §10 convention); the reader above
re-runs each of these against the memo text:

```python
from eval.deduction_metrics import _wilson_interval
_wilson_interval(50, 96)    # bar 1, pooled          -> (0.5208, 0.4220, 0.6180)
_wilson_interval(14, 27)    # bar 1, samples/9p2i    -> (0.5185, 0.3399, 0.6926)
_wilson_interval(32, 61)    # bar 1, ml_corpus/9p2i  -> (0.5246, 0.4016, 0.6447)
_wilson_interval(1, 5)      # bar 1, samples/4p1i    -> (0.2000, 0.0362, 0.6245)
_wilson_interval(3, 3)      # bar 1, ml_corpus/4p1i  -> (1.0000, 0.4385, 1.0000)
_wilson_interval(34, 46)    # bar 4, the share       -> (0.7391, 0.5974, 0.8440)
_wilson_interval(34, 620)   # reporter per slot      -> (0.0548, 0.0395, 0.0757)
_wilson_interval(12, 1859)  # innocent non-reporter  -> (0.0065, 0.0037, 0.0112)
```
