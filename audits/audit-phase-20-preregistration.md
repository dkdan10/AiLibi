# Phase-20 pre-registration — the falsifiability contract for the evidence-honesty record: instruments, baseline cells, bars, the decision rule (Task 20.22)

**Date:** 2026-08-19 (drafted at the planning PR, `4a7bd9c0`); pinned and ratified at Task 20.22.
**Status:** RATIFIED — the owner's merge of Task 20.22's PR is the ratification (§10). Every
baseline cell below is quoted from a committed pin, and every bar and rule is stated as
[PROPOSED — ratified at merge]. Amendments after that merge are dated errata in §11.
**Depends on:** the two merged instrument tasks — 20.14 `eval/solvability.py` (`49d7b7e5`,
PR #358; Codex follow-up `efa4aa3b`, PR #364) and 20.15 `eval/evidence_honesty.py`
(`cee2319a`, PR #365) — plus the already-committed 19.14 deduction cells and the 19.11
injustice fixtures. Pinned at `205df1bd`; the measured bytes are the baseline-6 record,
unchanged since `b809b19c` (`git diff b809b19c..HEAD -- replays/` is empty).

**What is being pre-registered:** the instrument list (§2), the baseline cells (§3), the
primary bars (§4), the secondary observed-not-gated cells (§5), the decision rule (§6), the
co-intervention declaration (§7), the offline-counterfactual protocol (§8), and the record
order (§9). The memo is read VERBATIM by 20.34 (the counterfactual) and 20.36 (the record).

**Method:** zero hand-computed figures. Every cell names the committed file that computes it
and reproduces from `uv run pytest -q -k "evidence_honesty or solvability or deduction_metrics"`
plus the two committed readers `scripts/measure_baseline.py --honesty --json` and
`--solvability --json` (:26-55). Every interval is the Wilson 95% score interval produced by
`eval.deduction_metrics._wilson_interval` (`eval/deduction_metrics.py:852`) — the only
interval producer any cell in this memo may quote, the 18.4 §10 convention. §12 reproduces
every number with one command.

**Label key** (the 18.4 key, unchanged): **[VERIFIED]** quoted from a committed test pin or
committed source · **[INFERRED]** arithmetic over verified cells with the inputs shown ·
**[PROPOSED — ratified at merge]** a definition, bar or rule the owner ratifies by merging
this task's PR.

---

## 0. Verdict in one line

**Eight primary bars, every one computable from committed bytes by a committed instrument,
judge ONE adopting record: the non-direct conviction cell must become a real inference
channel (0.368 → ≥ 0.60) with the innocent-ejection count falling (79 → < 35), the three
honesty mechanisms must close (false crew self-placement < 5%; sole-flag precision ≥ 50%;
grounded sighting side 100%), the two bugs must be gone (fabricated completions 0;
adjacent-room STRONG ~0), and the four committed injustice fixtures must each flip —
measured on the new bytes against the baseline-6 cells, with the win split observed inside a
band and never gated, and the decision rule (§6) written before any lever exists.**

## 1. Why these cells, and why now — and what re-anchors without re-ratification

The Phase-19 close (`audits/audit-phase-19-close.md` §4.1) measured the deduction economy as
proof-lookup: conviction accuracy **1.000 where ejectee-specific proof exists (310/310
pooled)** and **0.368 where it does not (46/125)**, with **79/79 innocent ejections in the
non-direct cell** [VERIFIED: `tests/eval/test_deduction_metrics.py`]. The owner's Option-A
ruling (§4.4) chartered this phase off that finding. The 2026-08-19 review then located the
mechanisms that make the non-direct cell fail and measured each over the same bytes
(`audits/review-2026-08-19/A/verdicts.md`, `B/verdicts.md`). Phase 20 fixes those mechanisms
behind levers and records once. These cells are the before; the record produces the after;
this memo is the contract between them. The wave's day-1 rule is the review's own
(`audits/review-2026-08-19/D/FINAL-synthesis.md` :239-241): *pre-register before any code*.

**The standing rule (the 18.4 one, restated for this phase)** [PROPOSED — ratified at merge]:
the DEFINITIONS (§2), the statistical conventions (§12), the BARS (§4) and the decision rule
(§6) are the ratified content. The quoted baseline CELLS (§3, §5) are EVIDENCE and re-anchor
mechanically at the adopting record — 20.36 re-quotes them on the new bytes with provenance,
without re-ratification. One consequence is load-bearing:

> Where a pinned re-derivation differs from the review-measured figure, the PIN replaces the
> cell and the bar's TARGET does not move with it. A bar that follows its own baseline is not
> a bar.

Every target in §4 is ratified as written, not recomputed from whatever the pin turned out to
say. §3.2 lists the four cells where the pin and the review disagree, keeps both numbers, and
names the cause.

**Precedence over anything that still states a superseded cell OR an older rule.** This memo is
the only normative source for the cells, the bars and the decision rule. Where a contract, a
generated prompt or an audit disagrees with it, the memo governs and the contract is re-anchored
at its pre-dispatch review — the same coordination pass this phase already runs before every
dispatch. At ratification the known divergences, so the pass has a written list rather than a
search:

* **Cells** — `tasks/phase-20.md`'s Task-20.36 read paragraph still names `148/723 = 20.5%`,
  `36.5% grounded` and `53/529 = 10.0%`; the pins are `152/723 = 21.0%`, `124/234 = 53.0%` at
  tick and `19/458` (§3.2).
* **The partial-adoption rule** — Task 20.34's DoD (`tasks/phase-20.md:5533`) still asks which
  levers "may graduate on their own cell even under a FINDING verdict", and Task 20.36's
  (`:5800`) still says "a partial adoption graduates exactly the eligible subset". §6 rules
  otherwise, for the mechanical reason stated there: partial adoption yields a published
  per-lever verdict and graduates nothing, because a subset slate matches neither committed
  record's substrate stamp. Both contracts are re-anchored to "publish the eligible list; the
  gates stay" before their tasks dispatch.

A stale statement downstream is a re-anchor, never a second baseline and never a second rule.

## 2. The instruments

Eleven of the thirteen rows changed status at 20.14 (I-12) and 20.15 (I-2…I-11); I-1 and I-13
were already committed at 19.14 and 19.11. Nothing here is measured by an uncommitted script
any more.

| id | instrument | owner module | committed pin |
|---|---|---|---|
| I-1 | Proof-vs-inference conviction cells (direct / non-direct; innocent ejections by cell) | `eval/deduction_metrics.py` (19.14) | `tests/eval/test_deduction_metrics.py`:178, :224, :256, :295-296, :309-310 |
| I-2 | False crew self-placement rate (a spoken `whereabouts` whose room matches the speaker's true room at neither agent-tick N nor N−1) | `eval/evidence_honesty.py` (20.15) | `tests/eval/test_evidence_honesty.py::test_i2_false_crew_self_placement_pins` |
| I-3 | Sole-`alibi_vs_sighting` convicting precision — ejections whose ejectee's STRONG flags were ALL of kind `alibi_vs_sighting`, however many (`sole_flag_precision.per_victim_precision`): right / wrong — and the class impostor share vs the living-voter base rate | 20.15 | `tests/eval/test_evidence_honesty.py::test_i3_sole_flag_precision_pins` |
| I-4 | Grounded sighting side (share of resolvable spoken sighting sides the speaker's own record supports, at the tick and at ±1 / ±2) | 20.15 | `tests/eval/test_evidence_honesty.py::test_i4_grounded_sighting_side_pins` |
| I-5 | Fabricated completion lines (rendered "You completed X" with no completion event at any earlier tick) | 20.15 | `tests/eval/test_evidence_honesty.py::test_i5_fabricated_completion_pins` |
| I-6 | Adjacent-room STRONG share — STRONG `alibi_vs_sighting` whose two rooms are one doorway apart AND whose sighting sits within ≤ 1 tick of the alibi window (`adjacent_room_flags.adjacent`; the un-gated `adjacent_any_gap` is reported beside it) | 20.15 | `tests/eval/test_evidence_honesty.py::test_i6_adjacent_room_strong_share_pins` |
| I-7 | Movement-origin flags (`alibi_vs_sighting` whose sighting is the origin half of a `move A→B` line in the speaker's memory) | 20.15 | `tests/eval/test_evidence_honesty.py::test_i7_movement_origin_flag_pins` |
| I-8 | Dev-marker contamination (turn `free_text` beginning with a bracketed marker; prompts containing one) | 20.15 | `tests/eval/test_evidence_honesty.py::test_i8_marker_contamination_pins` |
| I-9 | Singular-persona prompts in a 2-impostor game | 20.15 | `tests/eval/test_evidence_honesty.py::test_i9_singular_persona_pins` |
| I-10 | Meetings with a participant inside a vent; reporters killed ≤ 3 ticks after their meeting (context cells) | 20.15 | `tests/eval/test_evidence_honesty.py::test_i10_meeting_physicality_pins` |
| I-11 | Free zero-witness kills declined; ghost-top impostor decisions (policy reconstruction, 0 mismatches vs recorded actions) — co-intervention cells | 20.15 | `tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` |
| I-12 | Solvability: killer-in-candidate-set containment; singleton rate and correctness; ejections landing on an already-cleared player | `eval/solvability.py` (20.14) | `tests/eval/test_solvability.py::test_pooled_denominators_and_headline_cells` and the four per-set tests |
| I-13 | The four 19.11 injustice fixtures (provenance-impossible sighting 9p2i s23 M1; content-vs-own-memory miss s12 M0; one-tick interval artifact 4p1i s41/s49; equal-weight conflict s41) | `tests/api/fixtures/evidence_mechanisms.py` (19.11) | `tests/api/test_evidence_mechanisms.py`:173, :194, :220, :249 |

**The definitions are the code's, verbatim — with two named exceptions.**
`eval/evidence_honesty.py:226` (`CELL_DEFINITIONS`) holds one sentence per row I-2…I-11 —
numerator, denominator, clock convention and an explicit non-coverage clause — and
`tests/eval/test_evidence_honesty.py:135` asserts each sentence is present verbatim in the
module docstring AND in its own cell family's docstring. The memo adopts those sentences by
reference, so the definition ratified here is by construction the one the code computes.
I-12's rule (which meetings enter, which kill anchors a meeting, who counts as an observer,
what clears a player, and what the cell does NOT measure) is stated the same way in
`eval/solvability.py`'s "The rule, stated before any cell is counted" block.

Two of those sentences are NARROWER than the cell the module actually registers, and the
table above states the registered semantics in words so a bar can never be judged on the
wrong population. **What this memo ratifies is the wording in the §2 table, and the cell it
names.**

* **I-3.** `CELL_DEFINITIONS["I-3"]` says "carried exactly one STRONG contradiction and it was
  alibi_vs_sighting" — that sentence describes the companion cell
  `sole_flag_precision.per_victim_single_flag_precision` (8/58 pooled). The registered cell,
  and bar 4's population, is `per_victim_precision`: every STRONG flag on the ejectee is of
  kind `alibi_vs_sighting`, however many there are (12/82 pooled — the population the review
  measured as 12 right / 70 wrong). On baseline 6 the two readings differ; after a lever that
  changes how many flags a victim carries they can differ more, which is why the bar names its
  cell rather than inheriting a sentence.
* **I-6.** `CELL_DEFINITIONS["I-6"]` says "one doorway apart" and adds "no clock conversion
  applies". The registered numerator `adjacent_room_flags.adjacent` additionally requires the
  sighting to sit within ≤ 1 tick of the alibi window; the un-gated count is the separate
  `adjacent_any_gap`. The two coincide on baseline 6 (148 each) and can separate once a lever
  moves the flags, so bar 7 is stated on `adjacent` with `adjacent_any_gap` reported beside it.

Both are wording defects in 20.15's definition strings, not in the numbers the tests pin;
correcting the two strings is a production-code edit and routes back as its own contract (this
memo quotes instruments and never redefines a cell).

## 3. Baseline cells (baseline 6 — the committed bytes, unchanged since `b809b19c`)

### 3.1 The table

Every cell is `numerator/denominator` over the committed bytes of that set; `n/a` marks a cell
that is NOT-APPLICABLE on that roster by definition, with the underlying counts in brackets.
Every numeric row is recomputed by the §12 reader; I-13 is a pass/fail exhibit set re-run by
its own pytest file.

| cell | samples/9p2i | ml_corpus/9p2i | samples/4p1i | ml_corpus/4p1i | committed source |
|---|---|---|---|---|---|
| I-1 direct-proof accuracy | 68/68 | 213/213 | 9/9 | 20/20 | [VERIFIED] `tests/eval/test_deduction_metrics.py`:178, :256, :295-296, :309-310 |
| I-1 non-direct accuracy | 10/33 | 35/89 | 1/3 | 0/0 | [VERIFIED] same file, :224, :256, :295-296, :309-310; pooled 46/125 = 0.368 |
| I-1 innocent ejections (all inside the non-direct cell) | 23 | 54 | 2 | 0 | [INFERRED] non-direct denominator − numerator, per set; pooled 79 |
| I-2 false crew self-placement | 152/723 | 409/2038 | 10/78 | 16/79 | [VERIFIED] `tests/eval/test_evidence_honesty.py::test_i2_…` |
| I-3 sole-flag convicting precision (per victim) | 2/21 | 9/59 | 1/2 | 0/0 | [VERIFIED] `…::test_i3_…`; pooled 12/82 = 14.6% |
| I-3 class impostor share (STRONG `alibi_vs_sighting`, dedup subjects) | 4/47 | 28/142 | 1/2 | 0/1 | [VERIFIED] `…::test_i3_…`; pooled 33/192 = 17.2% |
| I-3 living-voter base rate at those meetings | 65/260 | 187/748 | 2/6 | 1/3 | [VERIFIED] `…::test_i3_…` pins the samples/9p2i cell; pooled 255/1017 = 25.1% |
| I-4 grounded sighting side (at tick) | 31/58 | 92/173 | 1/2 | 0/1 | [VERIFIED] `…::test_i4_…`; pooled 124/234 = 53.0% |
| I-4 grounded sighting side (within ±1 tick) | 36/58 | 116/173 | 1/2 | 1/1 | [VERIFIED] `…::test_i4_…`; pooled 154/234 = 65.8% |
| I-5 fabricated completion lines (rows that reached a model) | 19/458 | 40/1311 | 15/61 | 14/58 | [VERIFIED] `…::test_i5_…` |
| I-6 adjacent-room STRONG share | 38/58 | 108/173 | 1/2 | 1/1 | [VERIFIED] `…::test_i6_…`; pooled 148/234 = 63.2% |
| I-7 movement-origin flags | 7/76 | 30/233 | 0/3 | 1/1 | [VERIFIED] `…::test_i7_…`; pooled 38/313 |
| I-8 marker contamination (turns) | 53/971 | 139/2726 | 0/117 | 0/120 | [VERIFIED] `…::test_i8_…` |
| I-8 marker contamination (prompts) | 246/1956 | 671/5502 | 0/234 | 0/240 | [VERIFIED] `…::test_i8_…` |
| I-9 singular-persona prompts | 1956/1956 | 5502/5502 | n/a (234/234) | n/a (240/240) | [VERIFIED] `…::test_i9_…` |
| I-10 venting-participant meetings | 16/165 | 50/463 | 1/39 | 2/40 | [VERIFIED] `…::test_i10_…`; pooled 69/707 |
| I-10 reporter killed ≤ 3 ticks after | 27/165 | 75/463 | 5/39 | 4/40 | [VERIFIED] `…::test_i10_…`; pooled 111/707 |
| I-11 free zero-witness kills declined | 190/415 | 413/1053 | 16/80 | 18/75 | [VERIFIED] `tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` pins samples/9p2i |
| I-11 ghost-top impostor decisions | 303/2461 | 555/6663 | 0/632 | 0/579 | [VERIFIED] same class, all four sets, 0 reconstruction mismatches |
| I-12 containment (killer in the candidate set) | 132/151 | 348/411 | 35/35 | 29/29 | [VERIFIED] `tests/eval/test_solvability.py`; pooled 544/626 = 86.9% |
| I-12 singleton candidate sets | 41/151 | 74/411 | 6/35 | 5/29 | [VERIFIED] same; pooled 126/626 = 20.1% |
| I-12 singleton correct | 37/41 | 66/74 | 6/6 | 5/5 | [VERIFIED] same; pooled 114/126 = 90.5% |
| I-12 ejections on an already-cleared player | 21/87 | 62/250 | 0/8 | 0/9 | [VERIFIED] same; pooled 83/354 = 23.4% |
| I-13 injustice fixtures | 4/4 exhibit the injustice (pooled over the named seeds) | | | | [VERIFIED] `tests/api/test_evidence_mechanisms.py`:173, :194, :220, :249 |

Cells the pin tests assert literally carry the test's name above; the remaining per-set cells
in the same rows are emitted by the same committed module through
`scripts/measure_baseline.py --honesty --json` / `--solvability --json`, and the §12 reader
recomputes every cell in the table, so no number here is quoted rather than computed.

**Intervals** (Wilson 95%, `eval.deduction_metrics._wilson_interval`, §12 reproduces them)
[VERIFIED]: I-1 non-direct pooled 46/125 = 0.3680 [0.2886, 0.4553]; I-2 samples/9p2i 152/723
= 0.2102 [0.1821, 0.2414]; I-3 per-victim pooled 12/82 = 0.1463 [0.0857, 0.2386] against the
pooled base rate 255/1017 = 0.2507 [0.2251, 0.2783] and a class impostor share of 33/192 =
0.1719 [0.1251, 0.2315] — the class is *below* the base rate, which is the whole finding;
I-4 at-tick pooled 124/234 = 0.5299 [0.4660, 0.5929]; I-5 samples/9p2i 19/458 = 0.0415
[0.0267, 0.0639]; I-6 pooled 148/234 = 0.6325 [0.5690, 0.6917]; I-12 cleared-player ejections
pooled 83/354 = 0.2345 [0.1933, 0.2813].

### 3.2 Where the pin and the review disagree — both numbers kept, the pin authoritative

Four cells moved when the review's session scripts (deliberately not committed —
`audits/audit-phase-20-planning.md` §4 item 4) were replaced by committed instruments. In
every case the PIN is the cell this memo registers and the §4 target is unchanged; the
review's figure is kept beside it, with the cause quoted from the instrument task's own test
comment. A silent replacement would make the "before" unauditable, which is the defect this
phase exists to remove.

| cell | review-measured | **committed pin (authoritative)** | cause, quoted from the pin's test comment |
|---|---|---|---|
| I-2 false crew self-placement | 148/723 = 20.5%, 402/2038 = 19.7%, 7/78, 11/79 (`A/verdicts.md` G-1) | **152/723 = 21.0%, 409/2038, 10/78, 16/79** | *"Every DENOMINATOR reproduces exactly; the numerators run 3-7 higher per set because this instrument admits a claim as truthful only when the spoken room matches the speaker's own engine room at tick N or N-1, while the review's unpublished script evidently admitted a third neighbouring tick — the residual is 0.6 points on the 9p2i sets and is carried, not smoothed."* |
| I-4 grounded sighting side | 36.5% grounded over **170** resolvable sides of 234 (`A/verdicts.md` G-2) | **124/234 = 53.0% at tick (all 234 sides resolvable), 154/234 = 65.8% within ±1** | *"this instrument resolves all 234 (a side is unresolvable only when its engine tick is outside the recording) and grounds a side whenever the speaker's own record holds that subject in that room within the tolerance, which is more permissive than the review's per-tick visibility replay — so the rate is higher and the denominator is the full class."* |
| I-5 fabricated completion lines | 53/529 = 10.0%, 140/1528, 15/65, 14/64 (`A/verdicts.md` G-3; `B/verdicts.md` C-2) | **19/458, 40/1311, 15/61, 14/58** | *"This instrument counts the rendered rows that actually REACHED a model — the recorded prompts — while the review re-rendered memory offline. On the 4p1i sets the salience budget never bites and the NUMERATORS reproduce exactly (15 and 14); on the 9p2i sets the budget drops the oldest rows from every prompt, so both halves run lower. The prompt population is the honesty-relevant one: a fabricated row no prompt carried poisoned nobody."* The review also disagrees with itself on the samples-pooled count (G-3's rows sum to 68; `D/FINAL-synthesis.md` §4 item 2.1 quotes 65); the instrument's own recount over the prompt population is 34. |
| I-12 ejections on an already-cleared player | 61/354 = 17.2% (`A/ideas-multi-agent-researcher.md` §D1) | **83/354 = 23.4%** (59/354 re-scored under the review's anchor) | *"Cause: the kill anchor. The review anchors on the last kill at or before the trigger tick; this module anchors on the REPORTED body's own kill… a tighter candidate set clears more players, so more ejections land outside it."* The same anchor moves containment (review 581/626; pin 544/626, and **581/626 exactly** when re-scored under the review's anchor — the `killer_in_set_last_kill_anchor` pin) and the singleton cells (review 109/626 and 103/109; pin 126/626 and 114/126). |

Two further re-anchors are recorded here so no later reader mistakes them for drift:

* **I-3 reproduces the review EXACTLY** under the kind-sole reading — 12 right / 70 wrong =
  12/82 per victim, and 82 sole-flag meetings driving 77 ejections, 65 of them crewmates.
  The stricter exactly-one-flag reading of the same population returns 8/58, which is *not*
  the review's split; **bar 4 is registered on the per-victim kind-sole cell** (12/82), the
  one the review measured.
* **I-6, I-7, I-8, I-9, I-10 reproduce the review EXACTLY**, including 148/234 = 63.2%
  adjacent with distance-2 = 71, distance ≥3 = 15 and single-tick window = 187
  (`audits/review-2026-08-19/A/ideas-multi-agent-researcher.md` §D2),
  38/313 movement-origin flags with 38/38 memory-truthful-and-spoken-false (G-9), the marker
  and persona censuses (G-25), and the physicality cells (G-5). I-11 reproduces `B/verdicts.md`
  C-3's 190/415 with the 168 / 15 / 7 decline-reason split and G-12's ghost-top cells over
  10,335 reconstructed decisions with zero mismatches against the recorded actions.

The two anchors the review cites for the G-2 mechanism are CORRECTED at HEAD and re-verified
by this task: `_iter_sightings` at `meetings/transcript.py:2170` yields every
`SawPlayerObservation` unfiltered, and `_detect_alibi_vs_sightings` at `:2380-2494` never
inspects the sighter's own record (the review wrote `:2379-2494`).

## 4. Primary bars [PROPOSED — ratified at merge]

Measured on the baseline-7 bytes by the same instruments, pooled over the four recorded sets
with the per-set cells shown beside the pooled figure. Targets are as written; none of them
moved with §3.2's re-anchors.

1. **I-1 non-direct conviction accuracy 0.368 → ≥ 0.60 pooled, and no ADEQUATELY POWERED set
   below 0.50.** Before, pooled 46/125 = 0.3680 [0.2886, 0.4553]; per set 10/33 = 0.3030
   [0.1738, 0.4734], 35/89 = 0.3933 [0.2982, 0.4971], 1/3 = 0.3333 [0.0615, 0.7923], and no
   cell at all on corpus/4p1i (an empty denominator is the None sentinel, never 0.0). The
   per-set floor binds on a set whose non-direct denominator is **n ≥ 30** at the record;
   a smaller cell is ADVISORY (§4.1) — reported with its interval, never able to decide the
   verdict on its own. The pooled figure is the gate.
2. **I-1 innocent ejections 79 → < 35 pooled.** Before, per set 23 / 54 / 2 / 0, all of them
   inside the non-direct cell (the direct-proof cell is 310/310 innocent-free).
3. **I-2 false crew self-placement 21.0% → < 5% on samples/9p2i, and every set < 8%.**
   Before: 152/723 = 21.0%, 409/2038 = 20.1%, 10/78 = 12.8%, 16/79 = 20.3%.
4. **I-3 sole-`alibi_vs_sighting` convicting precision 14.6% → ≥ 50% pooled, AND the class
   impostor share above the living-voter base rate at the same meetings.** The population is
   `sole_flag_precision.per_victim_precision` — every STRONG flag on the ejectee is of kind
   `alibi_vs_sighting`, however many (§2, I-3) — not the stricter exactly-one-flag companion.
   Before: 12/82 = 14.6% precision; class share 33/192 = 17.2% against a base rate of
   255/1017 = 25.1% — the channel is currently worse than chance.
5. **I-4 grounded sighting side → 100% of the surviving STRONG sighting sides, measured on
   the AT-TICK cell.** Before: 124/234 = 53.0% at tick (154/234 = 65.8% within ±1, reported
   beside it and never the bar). "Surviving" is the point: a lever that suppresses an
   ungrounded flag removes it from the denominator, and a lever that grounds it moves it into
   the numerator; both are passes.
6. **I-5 fabricated completion lines → 0 on every set.** Before: 19/458, 40/1311, 15/61,
   14/58.
7. **I-6 adjacent-room STRONG share 63.2% → ~0, operationalised as ≤ 5% pooled.** The
   numerator is `adjacent_room_flags.adjacent` — one doorway apart AND the sighting within
   ≤ 1 tick of the alibi window (§2, I-6) — with the un-gated `adjacent_any_gap` reported
   beside it, because a lever may move the two apart. Before: 148/234 = 0.6325
   [0.5690, 0.6917], with `adjacent_any_gap` also 148 on the same denominator today.
8. **I-13 the four 19.11 injustice fixtures: each stated pass/fail INDIVIDUALLY** — (a)
   provenance-impossible sighting, 9p2i seed 23 M1; (b) content-vs-own-memory miss, 9p2i seed
   12 M0; (c) one-tick interval artifact, 4p1i seeds 49 and 41; (d) equal-weight conflict,
   4p1i seed 41 M0. A fixture FLIPS when the meeting no longer exhibits its injustice under
   the adopted substrate. Four separate verdicts, never one aggregate.

### 4.1 Rare-event cells — advisory framing and the powering arithmetic [PROPOSED — ratified at merge]

**First, the reading convention, so the advisory test is not confused with it.** Every bar in
this memo is a POINT-ESTIMATE bar ("0.368 → ≥ 0.60", "→ 0", "→ 100%"), with the Wilson interval
reported beside it as context — the 18.4 convention. "The interval contains the threshold" is
therefore NOT the advisory test; applied as one it would make every bar in §4 advisory,
including the pooled ones, and the phase would gate on nothing.

**The advisory test is GRANULARITY.** The 18.4 §7 discipline carries over in the form that
actually bites here: **a cell is ADVISORY when one observation moves it by more than the
margin the bar asks for — `1/n > |target − baseline|`.** Such a cell is not measuring the
lever; it is reporting which way a single game fell. An advisory cell is published with its
rate, its Wilson interval and this arithmetic, and takes no part in the verdict: it cannot
turn ADOPTED into FINDING and it cannot rescue a pooled bar that was missed. §6 reads pooled
figures plus the per-set clauses this section calls powered, nothing else.

**The members at baseline 6.** The I-1 non-direct cell on samples/4p1i: `1/3 = 0.3333`, so one
ejection moves it by 0.333 against a margin of |0.60 − 0.368| = 0.232 — the step is larger than
the whole distance the bar asks the record to travel. The same cell on ml_corpus/4p1i has no
cell at all (denominator 0, the None sentinel). Also advisory by the same test: the I-3
per-victim cell on samples/4p1i (1/2) and ml_corpus/4p1i (0/0), and the I-4 and I-6
sighting-side cells on the two 4p1i sets (2 and 1 STRONG sides).

Corroboration for the n=3 cell — every outcome it can take, with the interval the production
helper returns. All four straddle 0.50, so no observation there can even locate the cell
relative to the floor:

| outcome | rate and Wilson 95% |
|---|---|
| 0 of 3 | 0/3 = 0.0000 [0.0000, 0.5615] |
| 1 of 3 (the baseline) | 1/3 = 0.3333 [0.0615, 0.7923] |
| 2 of 3 | 2/3 = 0.6667 [0.2077, 0.9385] |
| 3 of 3 | 3/3 = 1.0000 [0.4385, 1.0000] |

Hence bar 1's n ≥ 30 clause: at n = 30 one ejection moves the cell 0.033, an order of magnitude
inside the 0.232 margin. Satisfied today by samples/9p2i (n=33) and ml_corpus/9p2i (n=89).

**Applied to every per-set clause, at the RECORDED denominator — this is a rule, not a list.**
Bar 3's "every set < 8%": on samples/4p1i the margin is |0.08 − 0.128| = 0.048 against a step
of 1/78 = 0.013, and on ml_corpus/4p1i |0.08 − 0.203| = 0.123 against 1/79 = 0.013, so both are
powered by a factor of 4 to 10 — but if the recorded denominator falls far enough that
1/n exceeds the margin, that set's clause becomes advisory at the record and is reported that
way, exactly like the n=3 cell. Bars 4 and 7 are pooled and take no per-set clause. 20.36
applies the `1/n > |target − baseline|` test to each per-set RATE clause on the numbers it
recorded and labels the result before reading the verdict.

**Bars 5 and 6 are COUNT bars, and the granularity test does not reach them — but a shrunken
denominator is still reportable.** The granularity test compares a rate step against the
distance between a rate baseline and a rate target; bar 5 ("no ungrounded surviving STRONG
sighting side") and bar 6 ("no fabricated completion line") have a target of ZERO occurrences
and are decided on the numerator, where there is no threshold for a step to straddle: one
occurrence fails, none passes, at any denominator, and an empty denominator passes vacuously.
Registering them under the rate test would say a cell of 1/10 is "advisory" for a
zero-occurrence target, which is not a measurement statement. What IS a real risk is the one
you can see in bar 5's own wording — a lever may pass the bar by shrinking the population
rather than by grounding it — so both bars are reported WITH their denominators beside the
verdict, and a pass whose denominator fell below 10% of its baseline-6 value (bar 5: under 24
of 234 surviving sides; bar 6: under 46 of 458 rendered rows on samples/9p2i) is labelled
**SUPPRESSED-NOT-FIXED** in the record audit. The verdict does not change — suppressing an
ungrounded flag is the intended repair, not a dodge — but the mechanism is never left implicit.

## 5. Secondary cells (observed, reported, never gated)

Reported in the record audit beside the bars; none of them can decide the verdict.

* **The win split, inside a pre-registered band of ±15 points per set.** Baseline-6 impostor
  win rates re-derived from the committed MANIFEST `winner` column rather than quoted from
  prose [VERIFIED]: **samples/9p2i 15/50 = 30%, ml_corpus/9p2i 38/150 = 25%, samples/4p1i
  17/50 = 34%, ml_corpus/4p1i 11/50 = 22%**. Source: `scripts/check_doc_facts.py:226`
  (`check_sample_provenance`) re-derives the two samples rates from
  `replays/samples/<set>/MANIFEST.md` for the README claim, and the same
  `scripts/check_doc_facts.py::parse_manifest` reader gives the two corpus rates. A leg
  outside its band is reported, and §7 explains why it cannot attribute.
* **The solvability y-axis (I-12).** Containment, singleton rate and correctness, and
  ejections on an already-cleared player — the last expected to fall.
* **The context and co-intervention cells:** I-7 movement-origin flags, I-8 marker
  contamination, I-9 singular-persona prompts, I-10 meeting physicality, I-11 declined free
  kills and ghost-top decisions.
* **The render census (20.30's cells):** mean rendered lines per snapshot and
  reported-testimony retention. Baseline-6 [VERIFIED,
  `tests/eval/test_evidence_honesty.py::test_render_budget_pins`]: samples/9p2i 1,956
  snapshots, 99,959 rendered rows, mean 51.1038, 18,319 testimony rows (buckets ≤4: 2,794;
  5-6: 11,772; ≥7: 3,753); both 4p1i sets carry **zero** testimony rows, which is why the
  census is reported per candidate-count bucket and never as one blended number.
* **Token cost per meeting call** — the v4 map card and the meetings block add tokens;
  reported, not gated.

## 6. The decision rule [PROPOSED — ratified at merge]

**ADOPTED (the levers graduate; the ladder tip moves to baseline 7)** iff bars 1, 2, 3, 5, 6
and 7 are met AND at least three of the four fixtures flip AND bar 4 is met or **the pooled
denominator of `sole_flag_precision.per_victim_precision` has fallen below 20** (a class too
small to judge precision is a class that has closed). **FINDING (the levers stay toggles; the
tip stays at baseline 6; the bytes and the read are committed as the finding record)**
otherwise.

The waiver names that field and no other. `SoleFlagPrecisionCells` also exposes
`per_meeting_sole_flag_meetings`, which counts MEETINGS whose only STRONG flag kind is
`alibi_vs_sighting` rather than EJECTIONS whose ejectee carried only that kind; the two
increment under different predicates and merely both equal 82 on baseline 6. The waiver is
"the class bar 4 measures has closed", so it reads bar 4's own denominator — 82 pooled today.

**Partial adoption is a per-lever VERDICT, not a partial graduation.** A lever is ELIGIBLE
when, conjunctively: (i) its named bar is met on the recorded bytes, (ii) 20.34's published
OFF/ON table predicted that direction and magnitude for that lever's own cell before the record
was spent, and (iii) it is independently stampable, which 20.33 guarantees by binding one
resolver per lever into the substrate stamp. 20.34 fixes the final eligible list before the
record; 20.36 publishes it lever by lever in the record audit. The two bug-class levers
(`task_completion_from_events` → bar 6; `map_aware_arbitration` → bar 7) are the expected
members.

**An eligible lever keeps its default-OFF gate.** No lever graduates out of this record except
under the full ADOPTED verdict, where all eight graduate together. The reason is mechanical,
not stylistic: `api/replay_loader.py::_assert_substrate_matches` compares a recording's stamped
slate against `orchestrator.replay.substrate_flag_snapshot()` across every
`SUBSTRATE_FLAG_KEYS` entry and fails loud on any difference. Graduate a SUBSET and both
records break — the graduated keys become unconditionally True, so the baseline-6 recordings
that omit them (missing-key-reads-False) stop reconstructing, and a retired key's mismatch is
the non-remediable branch; meanwhile the ungraduated levers were ON in the baseline-7
recording, so those bytes would replay only with their `AILIBI_*` variables exported. A ladder
tip no bare environment can reconstruct is not a tip. Under ADOPTED all eight graduate and the
bare snapshot equals the baseline-7 stamp; under FINDING all eight stay toggles and the bare
snapshot equals the baseline-6 stamp; there is no third substrate. An eligible lever's ON-path
evidence is carried forward — published, counterfactual-predicted, fixture-pinned — and it
graduates at the next record made at its own slate.

**Advisory cells never enter this rule.** The verdict reads each bar's pooled figure plus the
per-set clauses §4 marks as powered (today: bar 1's n ≥ 30 sets and bar 3's four sets). A cell
§4.1 marks advisory is reported beside the bar and takes no part in the arithmetic, in either
direction — it cannot fail a bar and it cannot pass one.

**No bar may be re-priced after this merge, and a miss is reported as a miss.** The record
audit states each bar's before, after and verdict on one line; "adopt anyway" is the single
outcome 20.36 must not produce.

## 7. The co-intervention, declared

Task 20.32 repairs the scripted impostor mover — C-3's all-target re-validation with a
proximity term (190/415 = 45.8% of free zero-witness kill opportunities declined on an id
tie-break) and G-12's dead-set read of meeting history (303/2461 ghost-top decisions on
samples/9p2i) — BEFORE the freeze. It is a defect repair to the comparator every ML ruling was
measured against, not a balance lever (synthesis ruling R3); it is declared HERE because it
changes game dynamics inside the same record.

**The attribution consequence, stated so it cannot be renegotiated:** because the mover repair
and the eight honesty levers land in one record, no honesty bar may be attributed to a lever on
the strength of the win split. Attribution rests on (a) the offline counterfactual over FROZEN
baseline-6 bytes (§8), which holds the mover constant by construction, and (b) the recorded
per-cell before/after. The win split is secondary (§5) and is never a bar. The policy id stays
`fsm-default`; the MANIFEST `git_sha` is the provenance of the repaired mover.

## 8. The offline-counterfactual protocol (20.34)

Before 20.35 starts: `uv run python scripts/counterfactual_phase20.py --sets all` re-runs the
eight levers' ON-path over the reconstructed inputs of all 300 committed games and publishes,
in `audits/audit-phase-20-counterfactual.md`, an OFF/ON table.

**This is the ONE entry point for the OFF/ON computation.** The instruments themselves
(`eval/evidence_honesty.py`, `eval/solvability.py`) compute a single slate — the one the bytes
were recorded under — and deliberately expose no lever-slate parameter; 20.15 declined that
surface because the ON-path harness is this task's, and a second place that can toggle levers
is a second place the before and the after can diverge. 20.34 owns the toggling, through the
resolvers' own `env` parameters, and proves its OFF column IS the committed baseline before any
ON number is believed.

**Predictable offline** (the levers are render/detector rules over recorded inputs, so their
own cells are computable without a model call): I-3's class size and impostor share and the
sole-flag precision proxy; I-4 grounded sighting side; I-5 fabricated completion lines; I-6
adjacent-room STRONG share; I-7 movement-origin flags; I-8 marker contamination in turns and
in prompts; I-9 singular-persona prompts; the render census; I-12's solvability cells; and the
surviving-STRONG-flag census over the 79 innocent-ejection meetings.

**Explicitly NOT predictable offline, with the reason:**

* **I-1 non-direct conviction accuracy and innocent ejections** — a flag that stops being
  minted is not a vote that changes. These are bars about how agents vote once the substrate
  moves, and the recorded ballots were cast under the old one.
* **I-2 false crew self-placement after a self-location trail exists** — the cell measures what
  the model *says*; 20.24 changes what the model can *read*. There is no offline projection
  from the old prompts to the new answers.
* **The model-dependent halves of the four I-13 fixtures** — the flag census at each anchored
  meeting is computable, the ejection that followed it is not.
* **The win split** — downstream of every one of the above.

Asserting any of these offline would be the exact overreach this phase is built to demonstrate
against.

**Abandon criteria** (read as written STOP conditions by the smoke and the record): a
`scripts/validity_gate.py` FAIL on any leg; a seed whose opening defaults (the
`(deadline_default)` watch item); a guard trip; or a lever-stamp mismatch between the recorded
snapshot and the declared slate.

## 9. The record order and the freeze

**Freeze** `agents/`, `meetings/`, `observation/`, `orchestrator/` and the prompt set at the
20.33 merge — that merge is the freeze declaration, which is why the prompt-set bump (20.31)
must precede it.

**Smoke (20.35):** 5 seeds of 9p2i into a scratch directory; STOP-and-report; the go/no-go is
the owner's.

**Record (20.36), in this order:** `replays/samples/9p2i` → `replays/ml_corpus/9p2i` →
`replays/samples/4p1i` → `replays/ml_corpus/4p1i`, each checkpoint-pushed per completed seed
range. **The corpus 9p2i leg precedes either 4p1i leg** because that is where the power is: the
non-direct cell (bar 1) is n=89 in the corpus against n=33 in the samples
(`tests/eval/test_deduction_metrics.py`:256 and :224), and both 4p1i sets contribute n=3 and
n=0. A delta on n=33 will not separate — the samples cell 10/33 = 0.3030 [0.1738, 0.4734] is
nearly a third of the scale wide, against the corpus cell 35/89 = 0.3933 [0.2982, 0.4971]. If
the window forces a choice, the two 4p1i legs are the ones that yield.

**The slate:** model `Qwen/Qwen3.6-27B` non-thinking via Featherless, prompt set `qwen3_6_27b`
v4, lever slate all eight ON, `impostor_roll_call` OFF, `$0`. `impostor_roll_call` is the only
live toggle at HEAD (`orchestrator/replay.py:570-572`); the thirteen retired levers stamp
unconditionally True (`:531`).

## 10. THE RATIFIED DECISION (owner) — the pre-registration

**LOCKED DECISION (owner, ratified by the merge of Task 20.22's PR — the 15.18 convention):**

* **Instrument list = the thirteen §2 rows**, with the definitions adopted by reference from
  `eval/evidence_honesty.py::CELL_DEFINITIONS` and `eval/solvability.py`'s stated rule —
  **except for I-3 and I-6, where the §2 wording and the cell it names govern** and the
  `CELL_DEFINITIONS` sentence does not: I-3 is `sole_flag_precision.per_victim_precision`
  (every STRONG flag on the ejectee is `alibi_vs_sighting`, however many), NOT the
  exactly-one-flag `per_victim_single_flag_precision`; I-6 is `adjacent_room_flags.adjacent`
  (one doorway apart AND the sighting within ≤ 1 tick of the alibi window), NOT the un-gated
  `adjacent_any_gap`. Both exceptions bind 20.34 and 20.36 as written here. They are not the
  same case: I-3's two readings **already differ on baseline 6** (12/82 against 8/58), so the
  wrong one would misprice bar 4 today; I-6's coincide today (148 each) and separate once a
  lever moves the flags, so the wrong one would misprice bar 7 only at the record — which is
  worse, not better. A new instrument, or a changed definition, enters only through §11 and
  only before the record.
* **Baseline cells = §3 exactly**, with §3.2's four pin-over-review replacements and their
  stated causes.
* **Bars = §4 exactly**, eight of them, targets as written. Bar 4 is the per-victim kind-sole
  cell; bar 5 is the at-tick grounded cell; bar 7's "~0" is ≤ 5% pooled; bar 8 is four
  individual verdicts. **The §4.1 rare-event discipline is part of the bars**: a per-set
  clause binds only where §4.1 calls the cell powered, and an advisory cell is reported and
  never gated, in either direction.
* **Decision rule = §6 exactly**, including the partial-adoption eligibility test — which
  yields a published per-lever VERDICT and never a partial graduation, because a subset slate
  matches neither committed record's stamp — and the no-re-pricing clause.
* **Secondary = §5 exactly**: observed and reported, never gated; the win-split band is ±15
  points per set against the four re-derived MANIFEST rates.
* **Co-intervention = §7**: declared by name, with attribution resting on §8 plus the recorded
  per-cell before/after, never on the win split.
* **Protocol and order = §8 and §9**, including the abandon criteria and the corpus-9p2i-first
  power argument.
* **The standing rule = §1**: definitions, conventions, bars and the decision rule are the
  ratified content; the quoted cells re-anchor mechanically at 20.36 with provenance, without
  re-ratification.
* **Rejected — let the bars follow the pins.** Four cells moved when the review's scripts were
  replaced by committed instruments (§3.2). Re-pricing bar 3 to the pin, or bar 5 to the more
  permissive within-±1 tolerance, would have made every target a function of the baseline it is
  supposed to judge. Rejected: the pin replaces the cell, the target does not move.
* **Rejected — defer ratification to the record.** Bars written after the recordings exist are
  fitted to them; the review states the day-1 rule for this wave
  (`D/FINAL-synthesis.md` :239-241) and the repo has executed it once already at 18.4.
* **Rejected — attributing the honesty bars through the win split.** The declared
  co-intervention (§7) makes the split un-attributable by construction; a band that is observed
  and reported is the honest form of the same information.
* **Evidence:** §3 (the committed cells and their pins), §3.2 (the pin-vs-review reconciliation),
  §12 (the reproduction commands).

**Sign-off.** Ratification rides the merge of Task 20.22's PR: the owner ratifies the MERGED
text. The DAG enforces "pre-registration before the first fix" — every lever task and the
co-intervention (20.32) depend on 20.22, so no substrate change can merge before the bars are
ratified. 20.34 and 20.36 read this memo verbatim; anything after the merge is a dated erratum
in §11.

## 11. Amendment log

| date | what changed | why | ratification vehicle |
|---|---|---|---|
| 2026-08-20 | I-11 instrument mode. `eval/evidence_honesty.py`'s I-11 fold takes an explicit policy parameter (default: the policy in the tree) and applies its recorded-action fidelity guard only when the caller asserts it. The §3.1 I-11 baseline values are now FROZEN CONSTANTS at the pre-repair sha (`eval.evidence_honesty.RATIFIED_I11_CELLS`, quoted from this memo), and the live-policy fold over the same baseline-6 bytes is Task 20.32's own counterfactual "after" cell. **No ratified bar rides I-11** — it is a §5 secondary, observed-not-gated cell — so no bar, no decision-rule input and no I-1…I-10 cell moves. Read the §12 reader's two I-11 rows from the frozen constants, not from the live fold. | Task 20.32 repairs the impostor mover, so the policy the committed bytes were recorded with is no longer in the tree and the I-11 fold can no longer recompute its own "before" (orchestrator ruling, coordination commit `c24db41c`). | Task 20.32 PR (owner-merged) |
| 2026-08-24 | Render-census row patterns. `eval/evidence_honesty.py`'s `_RENDERED_ROW` and `_TESTIMONY_ROW` now match the reported-testimony frame with OR without its meeting index (`[meeting]` or `[meeting 1]`); nothing else in either pattern changed. **No committed cell moved:** the recorded baseline-6 bytes carry 18,319 bare frames and ZERO tagged ones (`tests/eval/test_evidence_honesty.py::test_no_committed_prompt_carries_a_tagged_meeting_frame`), and the pre-widening patterns are re-stated in `::test_the_widened_meeting_frame_is_off_neutral` and asserted to count an OFF-shaped block identically with planted near-misses still rejected. The render census is a **§5 secondary, observed-not-gated cell — no bar rides it** — so no bar, no decision-rule input and no I-1…I-10 cell moves. | `meeting_outcome_memory` ON stamps WHICH meeting a claim was spoken at, so the OFF-shaped patterns silently stopped counting the row and the eight-lever census could not be computed at all. §8 requires the offline counterfactual at the record's actual slate; a pre-record value for a different slate defeats its purpose (orchestrator ruling on PR #385, owner delegated). | Task 20.34 PR #385 |

Convention: an amendment is any change to the §10-ratified set (instrument list, definitions,
baseline cells, bars, decision rule, secondary list, co-intervention declaration, protocol,
record order). Each amendment is a row here plus the edited section, shipped in an
owner-merged PR — the merge is the re-ratification. Amendments land BEFORE the record or not
at all for this phase's claims. A cell re-quote at the adopting record is NOT an amendment and
takes no row (§1).

## 12. Method + reproduction (all $0 against committed bytes, offline)

Every cell in §3 and §5 is re-runnable. The pins:

```bash
uv run pytest -q -k "evidence_honesty or solvability or deduction_metrics"
uv run pytest -q tests/agents/test_impostor_policy.py -k TestCommittedCorpusTargetingPins
uv run pytest -q tests/api/test_evidence_mechanisms.py
```

The readers, which emit every I-2…I-12 cell as JSON:

```bash
uv run python scripts/measure_baseline.py --honesty --json replays/samples/9p2i
uv run python scripts/measure_baseline.py --solvability --json replays/ml_corpus/9p2i
```

**The pin-diff reader.** This is the whole memo checked against the instruments in one pass
(~11 s, offline): every §3.1 cell recomputed from `eval/evidence_honesty.py`,
`eval/solvability.py` and the committed `tournament-eval-report.json`; every quoted Wilson
interval re-run through the production helper; §5's win split re-derived from the MANIFESTs and
its render census re-derived from `render_budget`; the I-13 exhibit count and every anchor seed
checked against `tests/api/fixtures/evidence_mechanisms.py`; the §3.1 row inventory asserted so
a deleted row is a failure rather than a silent pass; and §3.2's four deliberate
pin-over-review differences asserted still to carry BOTH numbers.
It prints `0 mismatches` and **exits 0 only then** — a mismatch names the cell and exits 1, so
a CI job or an operator cannot read drift as a pass. The interval check closes the CLASS, not
the instance: every bracketed pair in the memo must belong to a claim the reader re-runs, so a
value in a spelling the parser skips is a failure rather than a silent omission — and every
check records a mismatch rather than asserting, so `python -O`, which strips asserts, cannot
disable a gate. Six perturbations, every one verified to bite (the last under `-O`): a changed cell digit (`7/76` → `8/76`) names the
cell and exits 1; a changed interval (`[0.2886, 0.4553]` → `[1.0000, 1.0000]`) prints
`interval 46/125: 0.3680 1.0000 1.0000 != (0.368, 0.2886, 0.4553)`; an interval re-spelled out
of the parsed shape trips "20 intervals quoted but only 19 are in a shape this reader can
re-run"; bumping a render-census figure by one prints `render census: the memo no longer states
18,319`; and deleting the I-13 row prints both `I-13: the memo does not state 4 exhibits` and
`table inventory changed`; and re-spelling an interval as `[0.2886,0.4553]` under
`uv run python -O` still exits 1 with both `20 intervals quoted but only 19 are in a shape this
reader can re-run` and `only 19 intervals parsed`. Task 20.22's PR pastes its output.

```bash
uv run python - <<'EOF'
import re
from operator import attrgetter
from pathlib import Path

from eval.deduction_metrics import _wilson_interval
from eval.evidence_honesty import compute_evidence_honesty
from eval.meeting_quality import TournamentEvalReport
from eval.solvability import compute_solvability_report
from scripts.check_doc_facts import parse_manifest

MEMO = Path("audits/audit-phase-20-preregistration.md")
SETS = ("samples/9p2i", "ml_corpus/9p2i", "samples/4p1i", "ml_corpus/4p1i")
CELLS = {  # table row label -> (report, attribute path of the cell)
    "I-1 direct-proof accuracy": ("d", "proof_present"),
    "I-1 non-direct accuracy": ("d", "non_direct_accuracy"),
    "I-1 innocent ejections (all inside the non-direct cell)": ("d", "innocent"),
    "I-2 false crew self-placement": ("h", "false_whereabouts.crew_false"),
    "I-3 sole-flag convicting precision (per victim)": (
        "h", "sole_flag_precision.per_victim_precision"),
    "I-3 class impostor share (STRONG `alibi_vs_sighting`, dedup subjects)": (
        "h", "sole_flag_precision.class_impostor_share"),
    "I-3 living-voter base rate at those meetings": (
        "h", "sole_flag_precision.living_voter_base_rate"),
    "I-4 grounded sighting side (at tick)": ("h", "grounded_sighting.grounded_at_tick"),
    "I-4 grounded sighting side (within ±1 tick)": (
        "h", "grounded_sighting.grounded_within_1"),
    "I-5 fabricated completion lines (rows that reached a model)": (
        "h", "fabricated_completions.fabricated"),
    "I-6 adjacent-room STRONG share": ("h", "adjacent_room_flags.adjacent"),
    "I-7 movement-origin flags": ("h", "movement_origin_flags.spoke_origin"),
    "I-8 marker contamination (turns)": ("h", "marker_contamination.turns_with_marker"),
    "I-8 marker contamination (prompts)": (
        "h", "marker_contamination.prompts_with_marker"),
    "I-9 singular-persona prompts": (
        "h", "singular_persona.prompts_with_singular_persona"),
    "I-10 venting-participant meetings": (
        "h", "meeting_physicality.venting_participants"),
    "I-10 reporter killed ≤ 3 ticks after": (
        "h", "meeting_physicality.reporter_killed_within_three"),
    "I-11 free zero-witness kills declined": (
        "h", "impostor_targeting.free_kills_declined"),
    "I-11 ghost-top impostor decisions": ("h", "impostor_targeting.ghost_top"),
    "I-12 containment (killer in the candidate set)": ("s", "killer_in_set"),
    "I-12 singleton candidate sets": ("s", "singleton_sets"),
    "I-12 singleton correct": ("s", "singleton_correct"),
    "I-12 ejections on an already-cleared player": ("s", "cleared_player_ejections"),
}
TEXT = MEMO.read_text(encoding="utf-8")
FLAT = re.sub(r"\s+", " ", TEXT)
# Scoped so this reader, quoted inside the memo, cannot satisfy its own checks.
PROSE = re.sub(r"\s+", " ", TEXT.split("### 3.2")[1].split("## 6.")[0])
NUM = re.compile(r"(\d+)/(\d+)|(?<![\d/])(\d+)(?![\d/])")
stated, mismatches = {}, []
for line in TEXT.split("### 3.1")[1].split("### 3.2")[0].splitlines():
    row = [part.strip() for part in line.strip().strip("|").split("|")]
    if line.startswith("| I-") and len(row) == 6:
        stated[row[0]] = [
            [(int(a), int(b)) if b else (int(c),) for a, b, c in NUM.findall(part)]
            for part in row[1:5]
        ]

REPORTS = {  # every instrument walks each committed set exactly once
    name: {
        "h": compute_evidence_honesty(Path("replays") / name),
        "s": compute_solvability_report(Path("replays") / name),
        "d": TournamentEvalReport.model_validate_json(
            (Path("replays") / name / "tournament-eval-report.json").read_text(
                encoding="utf-8"
            )
        ).deduction.ejectee_proof_cross_tab,
    }
    for name in SETS
}


def computed(label, replay_set):
    which, path = CELLS[label]
    report = REPORTS[replay_set][which]
    if which == "d":
        if path == "proof_present":
            return [(report.proof_present_impostor, report.proof_present_ejections)]
        cell = report.non_direct_accuracy
        if path == "innocent":
            return [(cell.denominator - cell.numerator,)]
    else:
        cell = attrgetter(path)(report)
    return [(cell.numerator, cell.denominator)]


for label in CELLS:
    if label not in stated:
        mismatches.append(f"{label}: row absent from the baseline table")
        continue
    for replay_set, memo_cell in zip(SETS, stated[label]):
        want = computed(label, replay_set)
        if memo_cell != want:
            mismatches.append(f"{label} [{replay_set}]: {memo_cell} != {want}")
    print(f"OK  {label}: " + "  ".join(str(c) for c in stated[label]))

CLAIM = re.compile(r"(\d+)/(\d+) = (\d\.\d{4}) \[(\d\.\d{4}), (\d\.\d{4})\]")
BRACKET = re.compile(r"\[\s*\d\.\d{4}\s*,\s*\d\.\d{4}\s*\]")
prose = FLAT.split("## 12.")[0]  # §12 quotes the helper's tuples, not intervals
intervals = CLAIM.findall(prose)
# Every bracketed pair in the memo must belong to a claim this reader re-runs:
# equality closes the CLASS, so no new spelling can slip a value past the gate.
# Recorded as mismatches, never as asserts — `python -O` strips asserts, and a
# gate that vanishes with an interpreter flag is not a gate.
quoted_pairs = len(BRACKET.findall(prose))
if quoted_pairs != len(intervals):
    mismatches.append(
        f"{quoted_pairs} intervals quoted but only {len(intervals)} are in a shape this "
        "reader can re-run"
    )
if len(intervals) < 20:
    mismatches.append(f"only {len(intervals)} intervals parsed — a claim went missing")
for num, den, rate, low, high in intervals:
    want = tuple(round(value, 4) for value in _wilson_interval(int(num), int(den)))
    if want != (float(rate), float(low), float(high)):
        mismatches.append(f"interval {num}/{den}: {rate} {low} {high} != {want}")
print(f"OK  {len(intervals)} intervals, all from _wilson_interval")

for replay_set in SETS:
    manifest = parse_manifest(
        (Path("replays") / replay_set / "MANIFEST.md").read_text(encoding="utf-8")
    ).values()
    wins = sum(1 for row in manifest if row.winner.strip().upper() == "IMPOSTORS")
    quoted = re.search(rf"{re.escape(replay_set)} (\d+)/(\d+) = \d+%", PROSE)
    got = None if quoted is None else (int(quoted[1]), int(quoted[2]))
    if got != (wins, len(list(manifest))):
        mismatches.append(f"win split {replay_set}: {got} != {wins}")
print(f"OK  win split, all {len(SETS)} sets re-derived from the MANIFESTs")

# The non-tabular ratified cells: the I-13 exhibit set and the render census.
from tests.api.fixtures.evidence_mechanisms import EVIDENCE_MECHANISMS as mechanisms

if f"| I-13 injustice fixtures | {len(mechanisms)}/{len(mechanisms)} exhibit" not in TEXT:
    mismatches.append(f"I-13: the memo does not state {len(mechanisms)} exhibits")
for mechanism in mechanisms:
    for anchor in mechanism.anchors:
        if f"seed {anchor.seed}" not in PROSE and f"s{anchor.seed}" not in TEXT:
            mismatches.append(f"I-13: anchor seed {anchor.seed} is unnamed in the memo")
print(f"OK  I-13 {len(mechanisms)} exhibits, every anchor seed named")

budget = REPORTS["samples/9p2i"]["h"].render_budget
census = [
    f"{budget.snapshots:,}",
    f"{budget.rendered_lines_total:,}",
    f"{budget.rendered_lines_mean:.4f}",
    f"{budget.testimony_rows_total:,}",
] + [f"{count:,}" for count in budget.testimony_rows_by_living_bucket.values()]
for value in census:
    if value not in PROSE:
        mismatches.append(f"render census: the memo no longer states {value}")
for name in ("samples/4p1i", "ml_corpus/4p1i"):
    if REPORTS[name]["h"].render_budget.testimony_rows_total != 0:
        mismatches.append(f"render census: {name} testimony rows are no longer zero")
print(f"OK  render census, {len(census)} figures re-derived from the instrument")

# Row inventory: a deleted table row is drift, not a silent pass.
labels = {label for label in stated if label.startswith("I-")}
if labels != set(CELLS) | {"I-13 injustice fixtures"}:
    mismatches.append(f"table inventory changed: {sorted(labels ^ (set(CELLS) | {'I-13 injustice fixtures'}))}")
print(f"OK  table inventory, {len(labels)} rows")

for cell, review, pin in (
    ("I-2", "148/723 = 20.5%", "152/723 = 21.0%"),
    ("I-4", "**170** resolvable sides", "124/234 = 53.0%"),
    ("I-5", "53/529 = 10.0%, 140/1528, 15/65, 14/64", "19/458, 40/1311, 15/61, 14/58"),
    ("I-12 cleared-player", "61/354 = 17.2%", "83/354 = 23.4%"),
):
    for side in (review, pin):
        if re.sub(r"\s+", " ", side) not in PROSE:
            mismatches.append(f"{cell}: the reconciliation no longer states {side!r}")
    print(f"DELIBERATE  {cell}: review {review} -> pin {pin}")

print(f"\n{len(mismatches)} mismatches")
for line in mismatches:
    print("  " + line)
raise SystemExit(1 if mismatches else 0)
EOF
```

The intervals — the production helper, never by hand (the 18.4 §10 convention); the reader
above re-runs each of these against the memo text:

```python
from eval.deduction_metrics import _wilson_interval
_wilson_interval(46, 125)    # I-1 non-direct pooled -> (0.3680, 0.2886, 0.4553)
_wilson_interval(152, 723)   # I-2 samples/9p2i      -> (0.2102, 0.1821, 0.2414)
_wilson_interval(12, 82)     # I-3 per-victim pooled -> (0.1463, 0.0857, 0.2386)
_wilson_interval(255, 1017)  # I-3 base rate pooled  -> (0.2507, 0.2251, 0.2783)
_wilson_interval(33, 192)    # I-3 class share       -> (0.1719, 0.1251, 0.2315)
_wilson_interval(124, 234)   # I-4 at-tick pooled    -> (0.5299, 0.4660, 0.5929)
_wilson_interval(19, 458)    # I-5 samples/9p2i      -> (0.0415, 0.0267, 0.0639)
_wilson_interval(148, 234)   # I-6 pooled            -> (0.6325, 0.5690, 0.6917)
_wilson_interval(83, 354)    # I-12 cleared-player   -> (0.2345, 0.1933, 0.2813)
_wilson_interval(10, 33)     # bar-1 power, samples  -> (0.3030, 0.1738, 0.4734)
_wilson_interval(35, 89)     # bar-1 power, corpus   -> (0.3933, 0.2982, 0.4971)
```

The §5 win split is re-derived from the committed MANIFEST `winner` column by the same reader
(`scripts.check_doc_facts.parse_manifest`, the parser `check_sample_provenance` uses for the
README claim) — 15/50, 38/150, 17/50, 11/50 — never quoted from prose.
