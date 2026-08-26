# Agent Prompt — 20.38 The results on corrected bytes: re-curated featured games, the before/after column, the ML page amended

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.38 — The results on corrected bytes: re-curated featured games, the before/after column, the ML page amended, anchored to audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 rows 3.1 and 3.2 ("the results table gains its before/after column … *pre-registered, measured, reported — including the part that did not move*") and §7 (the post-wave-2 pitch paragraph; endorsement edit (b): every volatile number carries its baseline stamp from day one "so wave 3 adds a column instead of rewriting the page"); audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once, plainly — the enabling move this task completes) and §B3 (the reading guide measured at review time as 3,239 words / 378 lines against an advertised five minutes, with `file:line` anchors already drifting — B3 has since been EXECUTED: the guide is 112 lines / 988 words at HEAD, and `check_guide_line_citations` at scripts/check_doc_facts.py:2104 already fails on any `file:line` citation in it); byte-coupled front-door anchors re-verified at HEAD, post-20.36 — README.md:128-136 (the results table) and README.md:144 (the `<!-- ANCHOR: a later contract adds the results table's before/after column once the next reference recording lands. -->` comment this task consumes and deletes), README.md:140 (the unstamped "almost nine in ten" headline paragraph, which rests on the moved cross-tab), README.md:151 (the status/ladder-tip paragraph, ALREADY re-quoted by the record to "the seventh … baseline 7"), README.md:195 (the single sample-provenance paragraph, ALREADY re-quoted by the record: `regenerated 2026-08-25`, `Qwen/Qwen3.6-27B`, the `qwen3_6_27b` `v4` prompt set, "36% (4p1i) and 24% (9p2i)"; the baseline-6 values it replaced, and which the before-column now carries, were `2026-07-20`, `v3`, "34% (4p1i) and 30% (9p2i)"); docs/reading-guide.md:13-23 (the numbers table — :17 and :18 were already re-quoted at the record; the guide is 112 lines at HEAD, carries NO prose row crediting the guard to *the README's* copy, and carries NO featured table at all: see the open ruling on the featured mirror in the DoD), :60 (the STALE prose "all 520 eject ballots", left behind when the record moved the same figure to 538/538 in both tables), :48-56 (the §2 exhibit paragraph, falsified by the record: `9p2i` seed 23 now carries no flags and ejects nobody, and `4p1i` seed 41 now ejects the impostor on one grounded proof — audits/audit-phase-20-baseline-7.md §4(a) and §4(d)), :70-78 (the vent cross-tab, still baseline 6: "all 165 committed 9p2i meetings", 70 flagged against 95 unflagged, 68/2 and 10/21); scripts/check_doc_facts.py:161 (`_README`), :163 (`_LADDER_TIP_AUDIT`, ALREADY re-pointed by the record to `audits/audit-phase-20-baseline-7.md`), :166 (`_READING_GUIDE`), :174-179 (`_LINKED_DOCUMENTS`), :182-188 (`_LADDER_TIP_DOCUMENTS` — README, glossary, history and the reading guide are all already scanned for the tip), :226 (`_AUDIT_LADDER_TIP`, the `ladder tip stands at baseline N` parse), :238-240 (`_REGENERATED_DATE` and `_WIN_RATE_CLAIM` — the two claim-shaped scans, still README-only), :509-528 (`check_facts`), :532 and :688 (`check_sample_provenance` and its README-bound win-rate loop), :720 (`check_ladder_tip`, whose docstring still says the tip is parsed from *the phase-18 close audit* — a stale in-code claim to repair while here), :1384 (`check_results_agreement`, which already equates the README results table against the guide's row for row), :1636 (`check_ml_results_table`), :2068 (`check_volatile_stamps`), :2104 (`check_guide_line_citations`); the pins the record MOVED, re-verified at HEAD — tests/eval/test_deduction_metrics.py:152-154 (samples-9p2i meetings 152, flagged 69, unflagged 83; was 165/70/95), :176-185 and :213-239 (the ejectee-proof and meeting-flag cells: 99 ejections, flagged 69/0, unflagged 16/14; was 101, 68/2, 10/21), :259-270 (the corpus twins); the pooled 310/310 = 1.000 vs 46/125 = 0.368 keeps its own baseline-6 stamp at audits/audit-phase-19-close.md:233, and its baseline-7 counterparts are the record's pooled cells — direct proof 326/326 = 1.000, non-direct 61/103 = 0.5922, innocent ejections 42 — at audits/audit-phase-20-baseline-7.md §3 bars 1 and 2; tests/eval/test_vj_instruments.py:524-532 (citation compliance now 538/538, was 520/520); tests/api/test_sets.py:431 (`test_featured_seeds_exist_in_their_committed_sets`) and :376 (`test_featured_labels_are_spoiler_free`), both still at those lines and both re-anchored at the record; frontend/src/components/ReplayPicker.tsx:103 (`FEATURED_GAMES`, re-curated at the record to `9p2i` seeds 2, 23, 13, 46 and `4p1i` seeds 29, 2, 11).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-results-after-record`
**Depends on:** 20.13, 20.20, 20.36 — the results table and the ML page must exist before a column can be added to them; the architecture and contract-exhibit sections settle the README shape this task edits around; and the record must be committed before any of its numbers can be quoted.
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 rows 3.1 and 3.2 ("the results table gains its before/after column … *pre-registered, measured, reported — including the part that did not move*") and §7 (the post-wave-2 pitch paragraph; endorsement edit (b): every volatile number carries its baseline stamp from day one "so wave 3 adds a column instead of rewriting the page"); audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once, plainly — the enabling move this task completes) and §B3 (the reading guide measured at review time as 3,239 words / 378 lines against an advertised five minutes, with `file:line` anchors already drifting — B3 has since been EXECUTED: the guide is 112 lines / 988 words at HEAD, and `check_guide_line_citations` at scripts/check_doc_facts.py:2104 already fails on any `file:line` citation in it); byte-coupled front-door anchors re-verified at HEAD, post-20.36 — README.md:128-136 (the results table) and README.md:144 (the `<!-- ANCHOR: a later contract adds the results table's before/after column once the next reference recording lands. -->` comment this task consumes and deletes), README.md:140 (the unstamped "almost nine in ten" headline paragraph, which rests on the moved cross-tab), README.md:151 (the status/ladder-tip paragraph, ALREADY re-quoted by the record to "the seventh … baseline 7"), README.md:195 (the single sample-provenance paragraph, ALREADY re-quoted by the record: `regenerated 2026-08-25`, `Qwen/Qwen3.6-27B`, the `qwen3_6_27b` `v4` prompt set, "36% (4p1i) and 24% (9p2i)"; the baseline-6 values it replaced, and which the before-column now carries, were `2026-07-20`, `v3`, "34% (4p1i) and 30% (9p2i)"); docs/reading-guide.md:13-23 (the numbers table — :17 and :18 were already re-quoted at the record; the guide is 112 lines at HEAD, carries NO prose row crediting the guard to *the README's* copy, and carries NO featured table at all: see the open ruling on the featured mirror in the DoD), :60 (the STALE prose "all 520 eject ballots", left behind when the record moved the same figure to 538/538 in both tables), :48-56 (the §2 exhibit paragraph, falsified by the record: `9p2i` seed 23 now carries no flags and ejects nobody, and `4p1i` seed 41 now ejects the impostor on one grounded proof — audits/audit-phase-20-baseline-7.md §4(a) and §4(d)), :70-78 (the vent cross-tab, still baseline 6: "all 165 committed 9p2i meetings", 70 flagged against 95 unflagged, 68/2 and 10/21); scripts/check_doc_facts.py:161 (`_README`), :163 (`_LADDER_TIP_AUDIT`, ALREADY re-pointed by the record to `audits/audit-phase-20-baseline-7.md`), :166 (`_READING_GUIDE`), :174-179 (`_LINKED_DOCUMENTS`), :182-188 (`_LADDER_TIP_DOCUMENTS` — README, glossary, history and the reading guide are all already scanned for the tip), :226 (`_AUDIT_LADDER_TIP`, the `ladder tip stands at baseline N` parse), :238-240 (`_REGENERATED_DATE` and `_WIN_RATE_CLAIM` — the two claim-shaped scans, still README-only), :509-528 (`check_facts`), :532 and :688 (`check_sample_provenance` and its README-bound win-rate loop), :720 (`check_ladder_tip`, whose docstring still says the tip is parsed from *the phase-18 close audit* — a stale in-code claim to repair while here), :1384 (`check_results_agreement`, which already equates the README results table against the guide's row for row), :1636 (`check_ml_results_table`), :2068 (`check_volatile_stamps`), :2104 (`check_guide_line_citations`); the pins the record MOVED, re-verified at HEAD — tests/eval/test_deduction_metrics.py:152-154 (samples-9p2i meetings 152, flagged 69, unflagged 83; was 165/70/95), :176-185 and :213-239 (the ejectee-proof and meeting-flag cells: 99 ejections, flagged 69/0, unflagged 16/14; was 101, 68/2, 10/21), :259-270 (the corpus twins); the pooled 310/310 = 1.000 vs 46/125 = 0.368 keeps its own baseline-6 stamp at audits/audit-phase-19-close.md:233, and its baseline-7 counterparts are the record's pooled cells — direct proof 326/326 = 1.000, non-direct 61/103 = 0.5922, innocent ejections 42 — at audits/audit-phase-20-baseline-7.md §3 bars 1 and 2; tests/eval/test_vj_instruments.py:524-532 (citation compliance now 538/538, was 520/520); tests/api/test_sets.py:431 (`test_featured_seeds_exist_in_their_committed_sets`) and :376 (`test_featured_labels_are_spoiler_free`), both still at those lines and both re-anchored at the record; frontend/src/components/ReplayPicker.tsx:103 (`FEATURED_GAMES`, re-curated at the record to `9p2i` seeds 2, 23, 13, 46 and `4p1i` seeds 29, 2, 11).
**Complexity:** Small
**Record impact:** post-record (the record's bytes, MANIFESTs and re-pinned cells already exist; nothing recorded moves here)
**Measurement:** `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_check_doc_facts.py tests/api/test_sets.py -q` green, including the new perturbation cases — a stale reading-guide win rate, a featured row the picker no longer carries, and a moved figure quoted without its baseline stamp each fail the check.

This is the payoff task. The phase pre-registered its bars before any fix existed, measured them on a
23-hour record, and now has to report the answer — including the part that did not move. The record's own PR already
re-quoted every mechanical fact its gate reads — README.md:195's provenance paragraph (`regenerated
2026-08-25`, `Qwen/Qwen3.6-27B`, the `v4` set, 36% and 24%), README.md:151's ladder tip at baseline
7, the moved win-rate and citation rows in both the README table and the guide's, README.md:138's
"538 ballots" sentence, and the re-curated `FEATURED_GAMES` — so those are re-verified here and left
alone, and this diff is the reporting. What the record left behind is the prose no gate reads:
docs/reading-guide.md:60 still says "all 520 eject ballots" against a table row that now reads
538 / 538; the guide's §3 cross-tab at :70-78 still narrates "all 165 committed 9p2i meetings", 70
flagged against 95 unflagged, 68/2 and 10/21, whose baseline-7 pins are 152 meetings, 69/83, 69/0 and
16/14 (tests/eval/test_deduction_metrics.py:152-154, :230-233); README.md:140's unstamped "almost
nine in ten" headline rests on that same moved cross-tab; and the guide's §2 exhibit paragraph at
:48-56 still tells two stories the record deleted (§4(a): `9p2i` seed 23 now carries no flags and
ejects nobody; §4(d): `4p1i` seed 41 now ejects the impostor on one grounded proof). The pooled
deduction cells the results table states — 310/310 = 1.000 with proof against 46/125 = 0.368 without
(audits/audit-phase-19-close.md:233) — are a baseline-6 measurement that keeps its own stamp; their
baseline-7 counterparts are the record's pooled cells at audits/audit-phase-20-baseline-7.md §3 bars
1 and 2. Every one of those is a cell the record either moved or deliberately left standing. The whole argument of this phase — that a measurement made
after a pre-registration is worth more than a measurement made after a result — is only visible if
both columns are on the page.

The mechanical work is small because the earlier tasks built for it: the results table already stamps
each volatile row with its baseline and record date, so the edit is one added column and a header,
not a rewrite. What makes the task worth a contract is the discipline around the numbers. Quote; do
not compute. Every figure in this diff comes from `audits/audit-phase-20-baseline-7.md` or from the
test pin that owns it, and a figure with no pin does not go in the front door. The bars the phase
registered are quoted at their PINNED baseline-6 cells, never at the review figures the
pre-registration superseded (`audits/audit-phase-20-preregistration.md` §1 and §3.2 rule this
explicitly, and name this contract's own class of divergence: the pin replaces the cell, the bar's
target does not move with it, and a contract still naming a superseded cell is re-anchored at its
pre-dispatch review) — false crew `whereabouts` 152/723 = 21.0% on `samples/9p2i` (NOT the review's
20.5%), sole-`alibi_vs_sighting` precision 12/82 = 14.6%, grounded sighting side 124/234 = 53.0% at
tick (NOT the review's 36.5% over 170 resolvable sides), adjacent-room STRONG share 148/234 = 63.2%,
and the solvability y-axis (containment 544/626, a correct singleton in 114 of 126, and 83 of 354
ejections landing on a player the crew's pooled perception had already cleared; the review's
581/626, 103/109 and 61/354 are the last-kill-anchor re-scoring, quoted beside the pins with their
cause). Their baseline-7 values are read off the new pins, never re-derived by hand:
tests/eval/test_evidence_honesty.py:1261-1288 (I-2 now 3/659, 17/1892, 1/80, 0/91), :1292 (I-3 now
0/0), :1354-1375 (I-4 now 0/0 on every set), :1423-1450 (I-6 now 0/0), and
tests/eval/test_solvability.py:578-590 (618 body meetings, containment 555/618, singleton 80/618
with 72/80 correct, 68/379 cleared-player ejections, 586/618 under the review's anchor).

The verdict sentence is the other half, and the record produced NEITHER of the two branches this
contract was written against. The pre-registered rule returned **FINDING**: bars 1 and 2 missed —
non-direct conviction accuracy 61/103 = 0.5922 against a bar of ≥ 0.60, missed by 0.0078, less than
one ejection, and 42 innocent ejections against < 35. That verdict stands and is not re-priced
anywhere. Separately, by explicit owner prerogative recorded at
audits/audit-phase-20-baseline-7.md §6.1 (2026-08-26), the owner OVERRODE it and adopted the
baseline-7 substrate as canon — which is why the ladder tip already stands at baseline 7 and
`scripts/check_doc_facts.py:163` already points at the record audit. §6.1's standing constraint
binds every byte written here: no document, comment, docstring, README row or commit message may
state or imply that the pre-registered bars passed, that the verdict was ADOPTED under the rule, or
that baseline 7 was adopted on the arithmetic. So the front door says both things, in that order —
the FINDING with the bars it missed, then the override with its owner and its date. The FINDING half
must not be softened or buried; a project whose thesis is that it does not publish numbers it knows
are confounded cannot flinch at publishing a bar it missed. The decision itself belongs to the
record audit; this task states it and links it, and re-argues nothing.

There is still a guard gap to close while the numbers are being touched, but it is narrower and
differently placed than this contract first assumed. `scripts/check_doc_facts.py` has since grown a
front-door document set — `_LINKED_DOCUMENTS` (:174-179), `_LADDER_TIP_DOCUMENTS` (:182-188: README,
glossary, history and the reading guide all scanned for the tip), `check_results_agreement` (:1384),
which already equates the README results table against the guide's row for row,
`check_ml_results_table` (:1636) and `check_guide_line_citations` (:2104) — and it is green at HEAD.
What is still README-only is the claim-shaped scan: `_REGENERATED_DATE` and `_WIN_RATE_CLAIM`
(:238-240) are read over `readme` alone inside `check_sample_provenance` (:532, :688). And nothing
reads any document's PROSE, which is exactly where the record's drift survived — docs/reading-guide.md
:60, :48-56 and :70-78 are all wrong at HEAD while every table the checker compares is right. That is
precisely the drift class the checker exists to kill, and after a record it is the class most likely
to fire. Widening the claim-shaped scans to the front-door document tuple, adding the check nothing
yet does — binding a document's narrative figures to the pins that own them — and giving each new
check its perturbation test is what stops this page rotting the next time a baseline lands.

Finally, docs/ml-program.md needs an honest amendment rather than an update. The impostor mover's
target-selection defects are repaired now (Task 20.32, merged), so the comparator the Phase-17 and
Phase-18 win edges (+0.12 to +0.30, re-verified against the page's own table at HEAD) were measured
against no longer exists in that form — and nothing was retrained, so those figures were not
re-measured. The page currently promises the opposite: its comparator section closes with "The
repair is Task 20.32; the re-measurement, Task 20.38" (docs/ml-program.md:138) — a forward reference
this task falsifies rather than fulfils, and must therefore rewrite rather than leave standing. The page states that plainly: the erratum stands, the numbers are
stale by construction, and re-grounding them is a future owner decision, not a quiet edit.

**Files in scope:**
- README.md; (the results table's before/after column from audits/audit-phase-20-baseline-7.md; the `<!-- ANCHOR: … before/after column … -->` comment at :144 that this task consumes; the verdict/override sentence; the unstamped "almost nine in ten" headline at :140; the demo sentence — but NOT the two living project-status/roadmap sentences under `## Project status`, which Task 20.42's contract claims as "the status line only")
- docs/ml-program.md; (the Phase-20 read: what moved, what did not, the comparator note now that the FSM is repaired)
- docs/reading-guide.md; (the numbers table and the §3 cross-tab re-quoted from the new pins; the stale "all 520 eject ballots" prose at :60; the §2 exhibit paragraph at :48-56, whose named games the record's §4 falsified; the featured mirror only if the open ruling in the DoD re-introduces the table)
- docs/history.md; (Phase 20 row)
- scripts/check_doc_facts.py; (the new numbers checked against the new pins)
- tests/scripts/test_check_doc_facts.py

Orchestrator rulings (2026-08-26, pre-dispatch): (1) the featured-mirror bullet is RETIRED as written — docs/reading-guide.md deliberately carries no table since the 20.12 trim; instead the §2 exhibit prose is corrected against the baseline-7 bytes, every seed it names must be in ReplayPicker.tsx's FEATURED_GAMES, and a doc-fact check binds the named seeds to the picker source (the Measurement perturbation names a seed the picker no longer carries). (2) The two-part verdict shape is RATIFIED into the DoD: every results surface states verdict-per-rule FINDING (bars 1 and 2 missed, bar 1 by 0.0078) plus the dated §6.1 owner override that adopted baseline 7 — no surface may state or imply the bars passed or that adoption was on the arithmetic.

**Files NOT in scope:**
- replays/ (the record is done; no recorded byte moves in this PR)
- frontend/ (the featured list was re-curated at the record; the bundle redeploys via Pages)
- tests/api/test_sets.py (the featured-seed pin belongs to the record's re-pin sweep; this task reads it and mirrors it, never edits it)
- audits/ (the record audit and the pre-registration are quoted, never rewritten; records get dated errata from their owning tasks)
- agents/, meetings/, orchestrator/, eval/ (no behaviour and no instrument changes; every cell is read from an existing pin)
- agents/strategic/prompts/ (prompt templates are edited by the single prompt-set bump task and by nothing else)
- docs/media/ and docs/lessons.md (the hero media and the lessons page are later tasks in this wave)

**Definition of done:**
- [ ] Every figure in README.md, docs/reading-guide.md and docs/ml-program.md that the record moved is re-quoted from its new pin, carrying the baseline-7 stamp with its baseline-6 value beside it in the before/after column; the PR body lists each row with the pin or audit section it came from, and no figure in the diff was computed by this task.
- [ ] The README states the record's outcome the way the record states it, in that order: **FINDING** under the pre-registered rule, naming bars 1 and 2 and bar 1's 0.0078 margin, THEN the owner's explicit adoption override (audits/audit-phase-20-baseline-7.md §6.1, 2026-08-26) that moved the ladder tip to baseline 7; the passage links the record audit and names at least one pre-registered bar that did not move, and no sentence anywhere in the diff states or implies that the bars passed, that the verdict was ADOPTED under the rule, or that baseline 7 was adopted on the arithmetic (§6.1's standing constraint on every surface in this repository).
- [ ] README's sample-provenance paragraph agrees with the new MANIFESTs on the refresh date, recording model, prompt-set family and version and both per-set impostor win rates, and every "ladder tip" sentence names the baseline the owning audit records; `scripts/check_doc_facts.py:163` (`_LADDER_TIP_AUDIT`) points at that audit, and `uv run python scripts/check_doc_facts.py` is green at HEAD. Every clause in this bullet was already satisfied by the record's own PR and the checker is green at HEAD today: re-verify each and leave the correct ones untouched — the diff is the reporting, not churn.
- [ ] `scripts/check_doc_facts.py` checks the moved facts wherever the front door repeats them — the win rates and the refresh date in docs/reading-guide.md and docs/ml-program.md, not README alone (the ladder-tip claim is already scanned across `_LADDER_TIP_DOCUMENTS` at :182-188 and needs no new check), and the guide's PROSE figures as well as its table, since the record's drift survived exactly there (:60, :70-78) while `check_results_agreement` kept the tables right — and each new check has a perturbation case in tests/scripts/test_check_doc_facts.py that fails when the fact is drifted in the newly-covered document or paragraph; `check_ladder_tip`'s docstring at :720, which still credits the phase-18 close audit, is corrected to name the constant it actually reads.
- [ ] **[OPEN RULING — orchestrator/owner, before dispatch]** The reading guide's featured table equals `FEATURED_GAMES` seed-for-seed and in curated order, pinned by a check that parses the picker source and fails on an added, removed or re-ordered row; the guide's blurbs stay spoiler-free under the existing rule. At HEAD there is NO featured table in docs/reading-guide.md — 20.12/20.13 rewrote the guide to 112 lines and left only the §2 prose at :44-56, which names three AUDIT exhibits (`9p2i` seeds 17 and 23, `4p1i` seed 41), not the record's re-curated list (`9p2i` 2, 23, 13, 46 and `4p1i` 29, 2, 11 at frontend/src/components/ReplayPicker.tsx:103), and whose seed-23 and seed-41 stories the record's §4 falsified. The ruling to make: either the table is re-introduced in the guide and pinned exactly as written above, or this bullet retires and the §2 exhibit paragraph is corrected against the new bytes instead — with the mirror pin landing on whichever front-door surface ends up listing curated games.
- [ ] docs/ml-program.md carries the Phase-20 read — which pre-registered bars moved, which did not, and the win split as the observed-not-gated secondary — plus the amended comparator note: the FSM target-selection defects are repaired, the Phase-17/18 win edges were measured against the defective comparator, nothing was retrained, so the erratum stands and the figures are stale by construction.
- [ ] docs/history.md's phase-20 narrative is brought to the record's reality in the file's existing prose shape, linking the record audit: the section already exists at :160-164 ("## In progress: phase 20") and the record already re-wrote "## Where the sample sets came from" (:168 onward) for baseline 7, so this is an amendment, not an addition, and "in progress" stays true until Task 20.42 closes the phase.
- [ ] A grep for each baseline-6 figure the record moved returns only before-column cells explicitly stamped baseline 6; the PR quotes the grep.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import tests._helpers.committed"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-20-results-after-record` with a title like `task 20.38: the results on corrected bytes: re-curated featured games, the before/after column, the ml page amended`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 rows 3.1 and 3.2 ("the results table gains its before/after column … *pre-registered, measured, reported — including the part that did not move*") and §7 (the post-wave-2 pitch paragraph; endorsement edit (b): every volatile number carries its baseline stamp from day one "so wave 3 adds a column instead of rewriting the page"); audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once, plainly — the enabling move this task completes) and §B3 (the reading guide measured at review time as 3,239 words / 378 lines against an advertised five minutes, with `file:line` anchors already drifting — B3 has since been EXECUTED: the guide is 112 lines / 988 words at HEAD, and `check_guide_line_citations` at scripts/check_doc_facts.py:2104 already fails on any `file:line` citation in it); byte-coupled front-door anchors re-verified at HEAD, post-20.36 — README.md:128-136 (the results table) and README.md:144 (the `<!-- ANCHOR: a later contract adds the results table's before/after column once the next reference recording lands. -->` comment this task consumes and deletes), README.md:140 (the unstamped "almost nine in ten" headline paragraph, which rests on the moved cross-tab), README.md:151 (the status/ladder-tip paragraph, ALREADY re-quoted by the record to "the seventh … baseline 7"), README.md:195 (the single sample-provenance paragraph, ALREADY re-quoted by the record: `regenerated 2026-08-25`, `Qwen/Qwen3.6-27B`, the `qwen3_6_27b` `v4` prompt set, "36% (4p1i) and 24% (9p2i)"; the baseline-6 values it replaced, and which the before-column now carries, were `2026-07-20`, `v3`, "34% (4p1i) and 30% (9p2i)"); docs/reading-guide.md:13-23 (the numbers table — :17 and :18 were already re-quoted at the record; the guide is 112 lines at HEAD, carries NO prose row crediting the guard to *the README's* copy, and carries NO featured table at all: see the open ruling on the featured mirror in the DoD), :60 (the STALE prose "all 520 eject ballots", left behind when the record moved the same figure to 538/538 in both tables), :48-56 (the §2 exhibit paragraph, falsified by the record: `9p2i` seed 23 now carries no flags and ejects nobody, and `4p1i` seed 41 now ejects the impostor on one grounded proof — audits/audit-phase-20-baseline-7.md §4(a) and §4(d)), :70-78 (the vent cross-tab, still baseline 6: "all 165 committed 9p2i meetings", 70 flagged against 95 unflagged, 68/2 and 10/21); scripts/check_doc_facts.py:161 (`_README`), :163 (`_LADDER_TIP_AUDIT`, ALREADY re-pointed by the record to `audits/audit-phase-20-baseline-7.md`), :166 (`_READING_GUIDE`), :174-179 (`_LINKED_DOCUMENTS`), :182-188 (`_LADDER_TIP_DOCUMENTS` — README, glossary, history and the reading guide are all already scanned for the tip), :226 (`_AUDIT_LADDER_TIP`, the `ladder tip stands at baseline N` parse), :238-240 (`_REGENERATED_DATE` and `_WIN_RATE_CLAIM` — the two claim-shaped scans, still README-only), :509-528 (`check_facts`), :532 and :688 (`check_sample_provenance` and its README-bound win-rate loop), :720 (`check_ladder_tip`, whose docstring still says the tip is parsed from *the phase-18 close audit* — a stale in-code claim to repair while here), :1384 (`check_results_agreement`, which already equates the README results table against the guide's row for row), :1636 (`check_ml_results_table`), :2068 (`check_volatile_stamps`), :2104 (`check_guide_line_citations`); the pins the record MOVED, re-verified at HEAD — tests/eval/test_deduction_metrics.py:152-154 (samples-9p2i meetings 152, flagged 69, unflagged 83; was 165/70/95), :176-185 and :213-239 (the ejectee-proof and meeting-flag cells: 99 ejections, flagged 69/0, unflagged 16/14; was 101, 68/2, 10/21), :259-270 (the corpus twins); the pooled 310/310 = 1.000 vs 46/125 = 0.368 keeps its own baseline-6 stamp at audits/audit-phase-19-close.md:233, and its baseline-7 counterparts are the record's pooled cells — direct proof 326/326 = 1.000, non-direct 61/103 = 0.5922, innocent ejections 42 — at audits/audit-phase-20-baseline-7.md §3 bars 1 and 2; tests/eval/test_vj_instruments.py:524-532 (citation compliance now 538/538, was 520/520); tests/api/test_sets.py:431 (`test_featured_seeds_exist_in_their_committed_sets`) and :376 (`test_featured_labels_are_spoiler_free`), both still at those lines and both re-anchored at the record; frontend/src/components/ReplayPicker.tsx:103 (`FEATURED_GAMES`, re-curated at the record to `9p2i` seeds 2, 23, 13, 46 and `4p1i` seeds 29, 2, 11).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
