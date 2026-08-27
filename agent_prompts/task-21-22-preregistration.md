# Agent Prompt — 21.22 THE PRE-REGISTRATION (owner): the successor bars, the reporter cells and the decision rule for the injustice record

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.22 — THE PRE-REGISTRATION (owner): the successor bars, the reporter cells and the decision rule for the injustice record, anchored to audits/review-2026-08-26/A/collated-findings.md — A-4 (:431, P1, ADJUSTED: 30 of the 42 pooled innocent ejections eject the meeting's own body reporter; per slot 30/618 = 4.85% against 12/1844 = 0.65% for an innocent non-reporter, RR 7.46x, two-proportion z = 6.98; 28 of the 30 carry no contradiction naming the reporter; 0 of 618 report meetings had an impostor reporter; pooled ejection accuracy 387/429 = 90.2% and 387/399 = 97.0% with the reporter class removed — and the verifier's three binding corrections: the reporter's ejectability is a recorded design decision (agents/memory/beliefs.py:175-197, tasks/phase-15.md:553-580), the channel is DOWN ~2.6x from baseline 2's 22/106 = 20.8% to 7.9% of report-meeting ejections, and the finding's strongest new content is that it falsifies the 2026-08-19 D-track disposition of G-31 — the ballot-time guard let 10 reporter ejections through 152 samples/9p2i meetings), A-5 (:614, ADJUSTED to design-hole: the exculpation renders at ballot time only — `grep -c reporter agents/strategic/prompts/qwen3_6_27b/accusation_round.j2` returns 0 against 5 in vote_ballot.j2, both re-verified at HEAD), A-10 (:1138, the 42-row ledger: reporter 30, boomerang 29, impossible-transit 17, impostor-rides-the-herd 33, weak-flag 5, guard-redirect 4, forced endgame 5, the citation mix 79 hearsay / 40 own-observation / 26 own-turn of 145 ejecting ballots, 37 of 42 ejectees carrying no contradiction flag — with the verifier's corrections that SIX rows carry no tag beyond herd and/or transit (only three are pure herd) and that two supporting cells drift by one under a different tie-break and must be quoted as approximate), A-11 (:1346, the boomerang, with the verifier's instruction to DROP the 0/387 contrast as a tautology and to quote 29/492 = 5.9% overall and 29/271 = 10.7% within the no-vent-flag half against 1/71 = 1.4%), A-12 (:1449, the transit charge, with the verifier's replacement wording and the corrected within-stratum enrichment 15/19 = 78.9% against a 42/103 = 40.8% base = 1.9x, and the ≥half figure 15/42 = 35.7%), A-19 (:2252, the calibration cells, whose pooled headline the verifier REFUTES by decomposition), A-24 (:2901), A-37 (:3950), A-38 (:4006); audits/review-2026-08-26/B/collated-findings.md B-6 (:477) — the gauges the record reads are repaired upstream, which is why no bar here rides an un-repaired instrument; audits/audit-phase-20-preregistration.md §1 (the standing rule: definitions, conventions, bars and the rule are ratified content, cells re-anchor mechanically), §2 (the instrument-table shape and the definitions-by-reference convention), §3.1 and §3.2 (the cell table and the pin-over-review reconciliation), §4 and §4.1 (the bars and the `1/n > |target − baseline|` advisory test), §5, §6 (the conjunctive rule and the no-partial-graduation ruling), §7, §8, §9, §10, §11, §12 (the pin-diff reader); audits/audit-phase-20-baseline-7.md §6 (the verdict table: bars 1 and 2 MISSED, verdict FINDING), §6.1 (the owner's adoption ruling and its "what no surface may say" constraint), §6.2; audits/audit-phase-20-close.md §3.1 (the bars read back) and §4 (the routed balance wave); audits/audit-phase-18-emergence-preregistration.md (the label key, the claim discipline, THE RATIFIED DECISION and the amendment log this memo copies); the committed pins and readers, re-verified at HEAD — tests/eval/test_deduction_metrics.py:158, :179, :181, :265, :271, :307, :313, :329-330 (the per-set non-direct cells 16/30, 42/68, 1/2 and the corpus-4p1i denominator 3), tests/eval/test_funnel.py:632-633 (`reporter_ejected == 10`, `reporter_ejected_innocent == 10` on samples/9p2i), eval/funnel.py:798-799, :850-851, :894-895, :952 (`compute_information_funnel`), eval/deduction_metrics.py:852 (`_wilson_interval`, the only interval producer a cell may quote), eval/evidence_honesty.py:226 (`CELL_DEFINITIONS`), eval/vj_instruments.py:297-311 (the zero-flag conviction cells), scripts/measure_baseline.py:26-55 (`--funnel` / `--solvability` / `--honesty` / `--vj`, the committed readers), scripts/validity_gate.py, orchestrator/replay.py:524 (`_RETIRED_ALWAYS_ON_LEVERS`, 21 keys) and :568 (`_TOGGLEABLE_LEVER_RESOLVERS`, `impostor_roll_call` alone), api/replay_loader.py:603 (`_assert_substrate_matches`, the mechanical reason a subset slate cannot graduate), orchestrator/game.py:391 (the prompt set pinned at v4 today), agents/memory/beliefs.py:175-197 and agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-174 and meetings/manager.py:1776, :1831 (the exculpation as built), AGENTS.md craft rules 5 and 7. Anchors re-verified at HEAD.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-preregistration`
**Depends on:** 21.21
**Section refs:** audits/review-2026-08-26/A/collated-findings.md — A-4 (:431, P1, ADJUSTED: 30 of the 42 pooled innocent ejections eject the meeting's own body reporter; per slot 30/618 = 4.85% against 12/1844 = 0.65% for an innocent non-reporter, RR 7.46x, two-proportion z = 6.98; 28 of the 30 carry no contradiction naming the reporter; 0 of 618 report meetings had an impostor reporter; pooled ejection accuracy 387/429 = 90.2% and 387/399 = 97.0% with the reporter class removed — and the verifier's three binding corrections: the reporter's ejectability is a recorded design decision (agents/memory/beliefs.py:175-197, tasks/phase-15.md:553-580), the channel is DOWN ~2.6x from baseline 2's 22/106 = 20.8% to 7.9% of report-meeting ejections, and the finding's strongest new content is that it falsifies the 2026-08-19 D-track disposition of G-31 — the ballot-time guard let 10 reporter ejections through 152 samples/9p2i meetings), A-5 (:614, ADJUSTED to design-hole: the exculpation renders at ballot time only — `grep -c reporter agents/strategic/prompts/qwen3_6_27b/accusation_round.j2` returns 0 against 5 in vote_ballot.j2, both re-verified at HEAD), A-10 (:1138, the 42-row ledger: reporter 30, boomerang 29, impossible-transit 17, impostor-rides-the-herd 33, weak-flag 5, guard-redirect 4, forced endgame 5, the citation mix 79 hearsay / 40 own-observation / 26 own-turn of 145 ejecting ballots, 37 of 42 ejectees carrying no contradiction flag — with the verifier's corrections that SIX rows carry no tag beyond herd and/or transit (only three are pure herd) and that two supporting cells drift by one under a different tie-break and must be quoted as approximate), A-11 (:1346, the boomerang, with the verifier's instruction to DROP the 0/387 contrast as a tautology and to quote 29/492 = 5.9% overall and 29/271 = 10.7% within the no-vent-flag half against 1/71 = 1.4%), A-12 (:1449, the transit charge, with the verifier's replacement wording and the corrected within-stratum enrichment 15/19 = 78.9% against a 42/103 = 40.8% base = 1.9x, and the ≥half figure 15/42 = 35.7%), A-19 (:2252, the calibration cells, whose pooled headline the verifier REFUTES by decomposition), A-24 (:2901), A-37 (:3950), A-38 (:4006); audits/review-2026-08-26/B/collated-findings.md B-6 (:477) — the gauges the record reads are repaired upstream, which is why no bar here rides an un-repaired instrument; audits/audit-phase-20-preregistration.md §1 (the standing rule: definitions, conventions, bars and the rule are ratified content, cells re-anchor mechanically), §2 (the instrument-table shape and the definitions-by-reference convention), §3.1 and §3.2 (the cell table and the pin-over-review reconciliation), §4 and §4.1 (the bars and the `1/n > |target − baseline|` advisory test), §5, §6 (the conjunctive rule and the no-partial-graduation ruling), §7, §8, §9, §10, §11, §12 (the pin-diff reader); audits/audit-phase-20-baseline-7.md §6 (the verdict table: bars 1 and 2 MISSED, verdict FINDING), §6.1 (the owner's adoption ruling and its "what no surface may say" constraint), §6.2; audits/audit-phase-20-close.md §3.1 (the bars read back) and §4 (the routed balance wave); audits/audit-phase-18-emergence-preregistration.md (the label key, the claim discipline, THE RATIFIED DECISION and the amendment log this memo copies); the committed pins and readers, re-verified at HEAD — tests/eval/test_deduction_metrics.py:158, :179, :181, :265, :271, :307, :313, :329-330 (the per-set non-direct cells 16/30, 42/68, 1/2 and the corpus-4p1i denominator 3), tests/eval/test_funnel.py:632-633 (`reporter_ejected == 10`, `reporter_ejected_innocent == 10` on samples/9p2i), eval/funnel.py:798-799, :850-851, :894-895, :952 (`compute_information_funnel`), eval/deduction_metrics.py:852 (`_wilson_interval`, the only interval producer a cell may quote), eval/evidence_honesty.py:226 (`CELL_DEFINITIONS`), eval/vj_instruments.py:297-311 (the zero-flag conviction cells), scripts/measure_baseline.py:26-55 (`--funnel` / `--solvability` / `--honesty` / `--vj`, the committed readers), scripts/validity_gate.py, orchestrator/replay.py:524 (`_RETIRED_ALWAYS_ON_LEVERS`, 21 keys) and :568 (`_TOGGLEABLE_LEVER_RESOLVERS`, `impostor_roll_call` alone), api/replay_loader.py:603 (`_assert_substrate_matches`, the mechanical reason a subset slate cannot graduate), orchestrator/game.py:391 (the prompt set pinned at v4 today), agents/memory/beliefs.py:175-197 and agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-174 and meetings/manager.py:1776, :1831 (the exculpation as built), AGENTS.md craft rules 5 and 7. Anchors re-verified at HEAD.
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run pytest -q -k "deduction_metrics or funnel or evidence_honesty or solvability"` green — every pin the memo quotes resolves at this HEAD; plus the pin-diff reader pasted into the PR Summary as a `uv run python - <<'EOF'` heredoc, which recomputes every registered cell from `eval/deduction_metrics.py`, `eval/funnel.py` and `eval/evidence_honesty.py` over the four committed sets, re-runs every quoted interval through `eval.deduction_metrics._wilson_interval`, prints one line per cell, and exits 0 only on `0 mismatches`.

Phase 20 spent one 23-hour record and got a verdict its own rule wrote in advance: **FINDING**. Bars 1
and 2 — non-direct conviction accuracy ≥ 0.60 pooled, innocent ejections < 35 pooled — were MISSED,
at 61/103 = 0.5922 and 42 (`audits/audit-phase-20-baseline-7.md` §6). Baseline 7 is canon by an
explicit owner override of that FINDING verdict (§6.1), recorded as an override on stated grounds and
never as an arithmetic pass. Those two bars are the only ones the phase left unmet with a live
population behind them, and they are this phase's inheritance: the injustice record exists to try
them again, on corrected bytes, with the Wave-2 levers ON. This task writes the contract that judges
it — before the record is spent, in the tree, where nobody can move it afterwards.

The bars carry over with their **targets unchanged**. That is the 20.22 standing rule
(`audits/audit-phase-20-preregistration.md` §1) applied to its own successor: the corrected-substrate
re-record re-anchors every baseline CELL, and a re-anchored baseline never drags a target with it. A
bar that follows its own baseline is not a bar — and a bar that softens because the phase before it
missed by 0.0078 is worse than none.

**The new content is the reporter class, and it is registrable today because a committed instrument
already emits it.** A-4's headline — 30 of the 42 pooled innocent ejections eject the meeting's own
body reporter — is not a review-only walk. `eval/funnel.py`, the Task-15.3 information funnel, carries
a reporter-ejection census (`reporter_ejected`, `reporter_ejected_innocent`, `report_meetings`,
`report_ejections`, `killer_self_reported`; :850-851, :894-895), it is reachable per set through
`scripts/measure_baseline.py --funnel --json`, and this contract re-ran it over all four committed
sets at HEAD: **10 / 18 / 1 / 1 reporter ejections, every one of them innocent, over 144 / 400 / 37 /
37 report meetings and 91 / 248 / 18 / 22 report ejections, with `killer_self_reported` 0 on every
set**. Pooled: **30 reporter convictions, 618 report meetings, 379 report ejections** — the register's
figures to the digit, from committed code. The 42 denominator is the per-set non-direct innocent
counts summed — 30−16, 68−42, 2−1 and 3−2 — of which the first three are literal assertions
(`tests/eval/test_deduction_metrics.py`:179/181, :271, :313-314) while the corpus-4p1i set pins only
its denominator and the not-None sentinel (:329-330), so that one cell comes from the same committed
report through the reader rather than from an assertion. Say which is which in the memo. Either way
the reporter bars need no new instrument, which is what makes them registrable at a gate that adds no
code.

**Two reporter bars, not one, because a share alone can be gamed by its own denominator.** The count
bar (pooled reporter convictions) and the share bar (reporter convictions as a fraction of bar 2's own
innocent-ejection cell) move for different reasons: the share falls if the reporter class shrinks, and
it also falls if some other injustice class grows. They are registered jointly, and a share pass whose
innocent total did not fall is labelled **SHARE-BY-DILUTION** in the record audit — the same device
the phase-20 memo used for SUPPRESSED-NOT-FIXED, for the same reason: the verdict is allowed to stand
while the mechanism behind it is never left implicit.

**The proposed reporter targets come from bar 2's own arithmetic, and the memo shows the working.**
Bar 2 asks the pooled innocent-ejection count to fall from 42 to below 35 — at least eight cases. On
the phase-20 record the reporter class supplied 30 of those 42, leaving twelve non-reporter innocent
ejections in total; a phase that closed bar 2 while leaving the reporter class intact would have to
erase eight of those twelve. So the proposal is **bar 3: pooled reporter convictions 30 → ≤ 12**,
which on its own puts the pooled count at 24 with no other class moving, and **bar 4: the reporter
share 30/42 = 71.4% → < 40%**. The two are not redundant: bars 2 and 3 together already imply a share
under 12/35 = 34.3%, so bar 4 bites in exactly one case — a record that meets bar 2 because other
classes fell while the reporter class stood — the outcome this phase would most want to mistake for
success.
Both numbers are [PROPOSED — ratified at merge] and live in one table cell each, so the owner can
re-price them before merging without touching a line of prose.

**The instrument list is short by design.** Two rows carry all four bars — the proof-vs-inference
conviction cells (`eval/deduction_metrics.py`, bars 1 and 2) and the reporter-ejection census
(`eval/funnel.py`, bars 3 and 4) — and three more carry secondaries only: the evidence-honesty cells
(`eval/evidence_honesty.py`), the solvability y-axis (`eval/solvability.py`) and the zero-flag
conviction cells (`eval/vj_instruments.py`:297-311, the committed reading of the register's "37 of 42
ejectees carried no contradiction flag"). Definitions are adopted by reference from the modules that
compute them, in the 20.22 §2 shape, with any place where a definition string is narrower than the
registered cell called out in the memo's own words — because the wording that governs a bar is the
wording beside the bar, not a docstring that can drift.

**Power, re-derived rather than assumed.** At the phase-20 record the non-direct cell was n=30 on
samples/9p2i, n=68 on ml_corpus/9p2i and n=2 and n=3 on the two 4p1i sets: the corpus leg carries two
thirds of the whole denominator, and the samples leg sat exactly on the n ≥ 30 clause that makes a
per-set floor binding. That is why the record order puts corpus 9p2i before either 4p1i leg, and why
the memo re-runs the `1/n > |target − baseline|` test against ITS OWN denominators rather than
inheriting the phase-20 advisory list. If the corrected-substrate re-record moved a denominator across
the threshold, the advisory list changes with it, and the memo says which cells crossed.

**The slate the memo registers is the slate that merged.** The Wave-2 levers arrive as separate
contracts, one of which is an owner decision point that may be struck before dispatch. The memo
therefore reads the lever registry in the tree — `orchestrator/replay.py`:568 for what is still
toggleable, :524 for what has retired — and names the levers it finds, with `impostor_roll_call` OFF
as it has been since the baseline-7 record. A memo that named a lever the tree does not have would put
the record's slate and its own protocol section out of agreement on day one.

**The reporter bars also carry their own premise, and it can void them.** They read as injustice cells
only because the reporter is innocent by construction: the impostor policy cannot file a report
(`killer_self_reported` 0 on all four sets today, and 0/618 in A-4's independent walk). If any recorded
leg shows an impostor reporter, the premise has moved and the bars are **VOID**, not passed — the memo
says so, and the record audit checks `killer_self_reported == 0` and `reporter_ejected ==
reporter_ejected_innocent` per leg before reading either bar.

**What this memo may not do is invent a cell.** The register measured a great deal the repository
cannot recompute: the boomerang class, the impossible-transit charge, the hearsay citation mix, the
per-turn calibration decomposition. Each is a session walk, and several carry verifier corrections
that change the number or retract the framing (A-11's 0/387 contrast is a tautology; A-12's "provably
false every time" overstates the test; A-19's pooled headline is refuted by its own decomposition;
A-10's "only 4 of the 42" is six, of which three). A bar anchored to a figure nobody in this repository
can re-run cannot judge a record — that is precisely the defect 20.22 existed to remove. So the memo
registers only what a committed reader emits at this HEAD, and every other class goes into a named
**measured but not registered** list with its reason and one routing rule: a class the owner wants
gated becomes an instrument contract that merges before the record, or it stays observed.

**What the owner's merge ratifies, and what re-anchors without it.** The ratified content is the
instrument list, the definitions, the statistical conventions, the bars with their targets, the
advisory discipline, the secondary list, the decision rule, the declared co-interventions, the
protocol and the record order. The quoted baseline CELLS are evidence: they re-anchor mechanically at
the record, which re-quotes them on the new bytes with provenance and no re-ratification. The memo is
the only normative source for those things while the phase runs — where a contract, a generated prompt
or a later audit disagrees with it, the memo governs and the other surface is re-anchored at its
pre-dispatch review, never treated as a second baseline or a second rule.

**One ordering fact, stated rather than finessed.** Phase 20's memo landed before the first lever;
this one lands after the levers and after the offline counterfactual, because the DAG puts it there.
That makes it bars-before-the-record, not bars-before-the-levers, and the memo says so in its own
first section. Two things keep it honest: the two primary targets are inherited verbatim from
`audits/audit-phase-20-preregistration.md` §4 and are not derived from any phase-21 number, and the
counterfactual's predictions were committed before this merge and are quoted by section, never
re-computed here. Any target chosen with a phase-21 figure in view — the reporter bars are the
candidates — names the figure it was chosen against, so a later reader can see exactly how much slack
was priced in. The owner's merge ratifies; anything after it is a dated erratum in the amendment log.

**Files in scope:**
- audits/audit-phase-21-preregistration.md; (new — the instruments, the cells, the bars, the decision rule, the protocol, the record order, the ratified-decision section and an empty amendment log; every bar and rule marked [PROPOSED — ratified at merge])
- tasks/phase-21.md; (the 'Pre-registration' preamble paragraph pointing at the ratified memo — one paragraph)

**Files NOT in scope:**
- eval/ (no instrument is added, changed or redefined here; a cell the memo wants but no committed reader emits is routed as its own contract, exactly as the 18.4 and 20.22 batches did)
- tests/ (a pin the memo needs but does not have is a finding for the instrument contract, never a number typed into the memo)
- replays/ (bytes never move at a pre-registration gate)
- audits/audit-phase-20-preregistration.md, audits/audit-phase-20-baseline-7.md, audits/audit-phase-20-close.md (the phase-20 record is immutable; a successor bar is declared here and never by editing the record that missed it)
- agents/, meetings/, orchestrator/, agents/strategic/prompts/ (substrate is frozen for the record; the lever contracts own it)
- the STATUS line of tasks/phase-21.md (the phase close owns it)
- audits/README.md and docs/artifacts.md (the `audits/README.md` index line and the `docs/artifacts.md` `audits/`-row bump ride this PR as the standing index amendment — the 20.34 precedent — not as scope entries; both counts are re-read at implementation time, never hard-pinned)

**Definition of done:**
- [ ] `audits/audit-phase-21-preregistration.md` exists with the 18.4 / 20.22 skeleton in this order: verdict in one line; why these cells and what re-anchors without re-ratification; the instrument table; the baseline cells; where a pin and the register disagree; the primary bars; the advisory discipline; the secondary observed-not-gated cells; the decision rule; the declared co-interventions; the offline-counterfactual protocol; the record order and the freeze; THE RATIFIED DECISION; the amendment log; method and reproduction. The label key is the 18.4 one — [VERIFIED] quoted from a committed pin or committed source, [INFERRED] arithmetic over verified cells with inputs shown, [PROPOSED — ratified at merge] for every definition, bar and rule.
- [ ] Every registered cell names the committed file that computes it, beside the number. A grep for `[REVIEW-DERIVED]` in the memo returns zero hits, and no cell is hand-computed: every interval quoted comes from `eval.deduction_metrics._wilson_interval` (eval/deduction_metrics.py:852).
- [ ] The baseline column is read from the pins AS THEY STAND AT THIS HEAD — the corrected-substrate re-record's cells, not this contract's figures and not the phase-20 record's. That record is **baseline 8** and the memo names it by id in the column header, because two baseline ids move in this phase and a before column labelled only "baseline" would be ambiguous the moment baseline 9 exists. The baseline-7 values (non-direct 61/103 = 0.5922; innocent ejections 42 = 14/26/1/1; reporter convictions 30) appear beside them, labelled as the phase-20 record's history, and no phase-20 cell is re-priced anywhere in the memo.
- [ ] Bar 1 (non-direct conviction accuracy ≥ 0.60 pooled, no adequately powered set below 0.50) and bar 2 (innocent ejections < 35 pooled) are stated verbatim with unchanged targets, each with the per-set cells beside the pooled figure and its Wilson interval, and each carrying one sentence recording that this bar was **MISSED** at the phase-20 record and that baseline 7 is canon by explicit owner override of a FINDING verdict. No sentence anywhere in the memo states or implies that a phase-20 bar passed.
- [ ] Bar 3 (pooled reporter-conviction count) and bar 4 (the reporter share of bar 2's own innocent-ejection cell) are registered on committed cells — `eval.funnel.InformationFunnelReport.reporter_ejected_innocent` summed over the four sets for the numerator, bar 2's denominator for the share — with the proposed targets stated as [PROPOSED — ratified at merge] and the arithmetic that produced each shown, so the owner can move a number in exactly one place. The memo prints the per-set reproduction command and the four-set sum.
- [ ] The reporter bars state their premise and its void condition: `killer_self_reported == 0` and `reporter_ejected == reporter_ejected_innocent` on every recorded leg, checked before either bar is read; a leg that breaks the premise makes both bars VOID rather than met, and the memo says which cell the record audit reads to decide that.
- [ ] Bars 3 and 4 are stated jointly with the **SHARE-BY-DILUTION** label: a bar-4 pass whose bar-2 count did not fall is labelled that way in the record audit, with both denominators printed beside the verdict.
- [ ] The bars are also stated ONCE as a machine-readable table — one row per bar: bar id, the cell's fully qualified field, the committed reader that emits it, the baseline value, the target, and whether the per-set clause is powered — so the record contract reads the bars mechanically instead of re-deriving them from prose. The prose statement and the table agree, and the pin-diff reader checks both.
- [ ] The instrument table registers exactly the rows the bars and the secondaries need, each with its owner module and its committed pin, and adopts each definition by reference from the module that computes it. Where a module's definition string is narrower or broader than the cell the memo registers, the memo states the registered semantics in its own words, says which reading governs, and records that correcting the string is a production edit that routes as its own contract.
- [ ] The advisory discipline carries over verbatim in its granularity form — a cell is ADVISORY when `1/n > |target − baseline|`, published with its rate, its interval and the arithmetic, and taking no part in the verdict in either direction — and the memo names its members at the memo's own baseline denominators, with the 4p1i cells expected to qualify.
- [ ] The secondary cells are listed as observed-and-reported-never-gated, each naming its committed reader: the win split inside a pre-registered ±15-point-per-set band re-derived from each set's `MANIFEST.md`; the solvability y-axis; the zero-flag conviction cells (eval/vj_instruments.py:297-311); the evidence-honesty cells; the render census; token cost per meeting call.
- [ ] A **measured but not registered** section lists every review class the memo declines to gate — the ledger classes, the boomerang, the impossible-transit charge, the citation mix, the per-turn calibration decomposition — each with the reason (no committed reader emits it), each quoted in the VERIFIER-CORRECTED form rather than as originally filed, and each with the routing rule stated: an instrument contract merged before the record, or the class stays observed.
- [ ] The decision rule is written in ADOPTED / FINDING form, conjunctive, naming the exact subset of bars each verdict requires; it states that a partially eligible lever yields a published per-lever verdict and never a partial graduation, with the mechanical reason quoted from `api/replay_loader.py::_assert_substrate_matches` (:603) and the registry at orchestrator/replay.py:524 and :568; it states that no bar may be re-priced after this merge, that a miss publishes as a miss, and — in one sentence — that the phase-20 owner override is not a precedent for re-pricing, because an override is recorded as an override of a FINDING verdict and leaves the arithmetic where it stands.
- [ ] The ordering paragraph states plainly that this memo lands after the lever contracts and after the offline counterfactual, names the two mitigations (targets inherited verbatim from `audits/audit-phase-20-preregistration.md` §4; the counterfactual's predictions committed before this merge and quoted by section), and names any target that was chosen with a phase-21 figure in view together with that figure.
- [ ] The declared co-interventions section names, by name, everything landing inside the same record that is not a Wave-2 lever — the corrected-substrate repairs the re-record already carries — and states the attribution consequence: no bar is attributed to a lever on the strength of the win split, and attribution rests on the offline counterfactual plus the recorded per-cell before/after.
- [ ] The protocol section fixes the record order (`replays/samples/9p2i` → `replays/ml_corpus/9p2i` → `replays/samples/4p1i` → `replays/ml_corpus/4p1i`) with the power argument for the corpus-9p2i leg preceding either 4p1i leg stated from the memo's own re-anchored denominators; the freeze list; the slate (the Wave-2 levers that actually merged, ON; `impostor_roll_call` OFF; the model and the prompt-set version read from the tree and from the recorded MANIFESTs rather than from any contract's prose); and the abandon criteria as written STOP conditions — a `scripts/validity_gate.py` FAIL on any leg, a seed whose opening defaults, a guard trip, or a lever-stamp mismatch between the recorded snapshot and the declared slate.
- [ ] The memo states its own precedence and the split between ratified content and re-anchoring evidence: definitions, conventions, bars, advisory discipline, decision rule, co-intervention declaration, protocol and record order are ratified; the quoted cells are evidence that re-anchors at the record with provenance and without re-ratification; and any surface that disagrees with the memo is re-anchored at its pre-dispatch review rather than read as a second rule. Known divergences at ratification are listed by name so the coordination pass has a list rather than a search.
- [ ] A sign-off section records that ratification is the owner's merge of this PR, and an amendment log section exists with its convention stated and no rows at merge; the memo's status line does not say PROVISIONAL.
- [ ] `tasks/phase-21.md` gains one preamble paragraph naming the ratified memo as the document the record and the post-record sweep read verbatim; the STATUS line is untouched.
- [ ] The PR Summary carries the pin-diff reader's `0 mismatches` output and the green `pytest -k` run from Measurement, and its Decisions section records every proposed target with the arithmetic behind it.
- [ ] `uv run pytest -q -k "deduction_metrics or funnel or evidence_honesty or solvability"` passes.
- [ ] `uv run python scripts/measure_baseline.py --funnel --json replays/samples/9p2i` and the same command for the other three sets reproduce the reporter cells the memo quotes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import counterfactual_phase21"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.corroboration"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import orchestrator.game.TacticalAgent"`
- `uv run python -c "import eval.reporter_justice"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-preregistration` with a title like `task 21.22: the pre-registration (owner): the successor bars, the reporter cells and the decision rule for the injustice record`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-26/A/collated-findings.md — A-4 (:431, P1, ADJUSTED: 30 of the 42 pooled innocent ejections eject the meeting's own body reporter; per slot 30/618 = 4.85% against 12/1844 = 0.65% for an innocent non-reporter, RR 7.46x, two-proportion z = 6.98; 28 of the 30 carry no contradiction naming the reporter; 0 of 618 report meetings had an impostor reporter; pooled ejection accuracy 387/429 = 90.2% and 387/399 = 97.0% with the reporter class removed — and the verifier's three binding corrections: the reporter's ejectability is a recorded design decision (agents/memory/beliefs.py:175-197, tasks/phase-15.md:553-580), the channel is DOWN ~2.6x from baseline 2's 22/106 = 20.8% to 7.9% of report-meeting ejections, and the finding's strongest new content is that it falsifies the 2026-08-19 D-track disposition of G-31 — the ballot-time guard let 10 reporter ejections through 152 samples/9p2i meetings), A-5 (:614, ADJUSTED to design-hole: the exculpation renders at ballot time only — `grep -c reporter agents/strategic/prompts/qwen3_6_27b/accusation_round.j2` returns 0 against 5 in vote_ballot.j2, both re-verified at HEAD), A-10 (:1138, the 42-row ledger: reporter 30, boomerang 29, impossible-transit 17, impostor-rides-the-herd 33, weak-flag 5, guard-redirect 4, forced endgame 5, the citation mix 79 hearsay / 40 own-observation / 26 own-turn of 145 ejecting ballots, 37 of 42 ejectees carrying no contradiction flag — with the verifier's corrections that SIX rows carry no tag beyond herd and/or transit (only three are pure herd) and that two supporting cells drift by one under a different tie-break and must be quoted as approximate), A-11 (:1346, the boomerang, with the verifier's instruction to DROP the 0/387 contrast as a tautology and to quote 29/492 = 5.9% overall and 29/271 = 10.7% within the no-vent-flag half against 1/71 = 1.4%), A-12 (:1449, the transit charge, with the verifier's replacement wording and the corrected within-stratum enrichment 15/19 = 78.9% against a 42/103 = 40.8% base = 1.9x, and the ≥half figure 15/42 = 35.7%), A-19 (:2252, the calibration cells, whose pooled headline the verifier REFUTES by decomposition), A-24 (:2901), A-37 (:3950), A-38 (:4006); audits/review-2026-08-26/B/collated-findings.md B-6 (:477) — the gauges the record reads are repaired upstream, which is why no bar here rides an un-repaired instrument; audits/audit-phase-20-preregistration.md §1 (the standing rule: definitions, conventions, bars and the rule are ratified content, cells re-anchor mechanically), §2 (the instrument-table shape and the definitions-by-reference convention), §3.1 and §3.2 (the cell table and the pin-over-review reconciliation), §4 and §4.1 (the bars and the `1/n > |target − baseline|` advisory test), §5, §6 (the conjunctive rule and the no-partial-graduation ruling), §7, §8, §9, §10, §11, §12 (the pin-diff reader); audits/audit-phase-20-baseline-7.md §6 (the verdict table: bars 1 and 2 MISSED, verdict FINDING), §6.1 (the owner's adoption ruling and its "what no surface may say" constraint), §6.2; audits/audit-phase-20-close.md §3.1 (the bars read back) and §4 (the routed balance wave); audits/audit-phase-18-emergence-preregistration.md (the label key, the claim discipline, THE RATIFIED DECISION and the amendment log this memo copies); the committed pins and readers, re-verified at HEAD — tests/eval/test_deduction_metrics.py:158, :179, :181, :265, :271, :307, :313, :329-330 (the per-set non-direct cells 16/30, 42/68, 1/2 and the corpus-4p1i denominator 3), tests/eval/test_funnel.py:632-633 (`reporter_ejected == 10`, `reporter_ejected_innocent == 10` on samples/9p2i), eval/funnel.py:798-799, :850-851, :894-895, :952 (`compute_information_funnel`), eval/deduction_metrics.py:852 (`_wilson_interval`, the only interval producer a cell may quote), eval/evidence_honesty.py:226 (`CELL_DEFINITIONS`), eval/vj_instruments.py:297-311 (the zero-flag conviction cells), scripts/measure_baseline.py:26-55 (`--funnel` / `--solvability` / `--honesty` / `--vj`, the committed readers), scripts/validity_gate.py, orchestrator/replay.py:524 (`_RETIRED_ALWAYS_ON_LEVERS`, 21 keys) and :568 (`_TOGGLEABLE_LEVER_RESOLVERS`, `impostor_roll_call` alone), api/replay_loader.py:603 (`_assert_substrate_matches`, the mechanical reason a subset slate cannot graduate), orchestrator/game.py:391 (the prompt set pinned at v4 today), agents/memory/beliefs.py:175-197 and agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:171-174 and meetings/manager.py:1776, :1831 (the exculpation as built), AGENTS.md craft rules 5 and 7. Anchors re-verified at HEAD.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
