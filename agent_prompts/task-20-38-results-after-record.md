# Agent Prompt — 20.38 The results on corrected bytes: re-curated featured games, the before/after column, the ML page amended

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.38 — The results on corrected bytes: re-curated featured games, the before/after column, the ML page amended, anchored to audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 rows 3.1 and 3.2 ("the results table gains its before/after column … *pre-registered, measured, reported — including the part that did not move*") and §7 (the post-wave-2 pitch paragraph; endorsement edit (b): every volatile number carries its baseline stamp from day one "so wave 3 adds a column instead of rewriting the page"); audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once, plainly — the enabling move this task completes) and §B3 (the reading guide is 3,239 words / 378 lines against an advertised five minutes, with `file:line` anchors already drifting); byte-coupled front-door anchors re-verified at HEAD — README.md:84 (the status/ladder-tip paragraph), README.md:149 (the single sample-provenance paragraph: `regenerated 2026-07-20`, the recording model, the `qwen3_6_27b` `v3` prompt set, "34% (4p1i) and 30% (9p2i)"); docs/reading-guide.md:39-50 (the numbers table), :45 (the row that states in prose that only *the README's* copy of the win rates is re-derived), :101-105 and :109-117 (the featured table and its claim to mirror `FEATURED_GAMES` exactly), :175-184 (the vent cross-tab, 70/95 meetings); scripts/check_doc_facts.py:87 (`_README` — the only document the checker reads), :89 (`_LADDER_TIP_AUDIT` = `audits/audit-phase-18-close.md`), :99-101 (the `ladder tip stands at baseline N` parse), :160-169 (`check_facts`), :172 (`check_sample_provenance`), :360 (`check_ladder_tip`); the pins the record moves — tests/eval/test_deduction_metrics.py:163 and :237 (the proof / non-proof cells; pooled 310/310 = 1.000 and 46/125 = 0.368 at audits/audit-phase-19-close.md:233), tests/eval/test_vj_instruments.py:509 (520/520 citation compliance), tests/api/test_sets.py:431 and :376 (the featured-seed and spoiler-free pins), frontend/src/components/ReplayPicker.tsx:102 (`FEATURED_GAMES`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-results-after-record`
**Depends on:** 20.13, 20.20, 20.36 — the results table and the ML page must exist before a column can be added to them; the architecture and contract-exhibit sections settle the README shape this task edits around; and the record must be committed before any of its numbers can be quoted.
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 rows 3.1 and 3.2 ("the results table gains its before/after column … *pre-registered, measured, reported — including the part that did not move*") and §7 (the post-wave-2 pitch paragraph; endorsement edit (b): every volatile number carries its baseline stamp from day one "so wave 3 adds a column instead of rewriting the page"); audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once, plainly — the enabling move this task completes) and §B3 (the reading guide is 3,239 words / 378 lines against an advertised five minutes, with `file:line` anchors already drifting); byte-coupled front-door anchors re-verified at HEAD — README.md:84 (the status/ladder-tip paragraph), README.md:149 (the single sample-provenance paragraph: `regenerated 2026-07-20`, the recording model, the `qwen3_6_27b` `v3` prompt set, "34% (4p1i) and 30% (9p2i)"); docs/reading-guide.md:39-50 (the numbers table), :45 (the row that states in prose that only *the README's* copy of the win rates is re-derived), :101-105 and :109-117 (the featured table and its claim to mirror `FEATURED_GAMES` exactly), :175-184 (the vent cross-tab, 70/95 meetings); scripts/check_doc_facts.py:87 (`_README` — the only document the checker reads), :89 (`_LADDER_TIP_AUDIT` = `audits/audit-phase-18-close.md`), :99-101 (the `ladder tip stands at baseline N` parse), :160-169 (`check_facts`), :172 (`check_sample_provenance`), :360 (`check_ladder_tip`); the pins the record moves — tests/eval/test_deduction_metrics.py:163 and :237 (the proof / non-proof cells; pooled 310/310 = 1.000 and 46/125 = 0.368 at audits/audit-phase-19-close.md:233), tests/eval/test_vj_instruments.py:509 (520/520 citation compliance), tests/api/test_sets.py:431 and :376 (the featured-seed and spoiler-free pins), frontend/src/components/ReplayPicker.tsx:102 (`FEATURED_GAMES`).
**Complexity:** Small
**Record impact:** post-record (the record's bytes, MANIFESTs and re-pinned cells already exist; nothing recorded moves here)
**Measurement:** `uv run python scripts/check_doc_facts.py` green; `uv run pytest tests/scripts/test_check_doc_facts.py tests/api/test_sets.py -q` green, including the new perturbation cases — a stale reading-guide win rate, a featured row the picker no longer carries, and a moved figure quoted without its baseline stamp each fail the check.

This is the payoff task. The phase pre-registered its bars before any fix existed, measured them on a
23-hour record, and now has to report the answer — including the part that did not move. The front
door is still quoting the previous baseline: README.md:149 says the samples were `regenerated
2026-07-20` on the `qwen3_6_27b` `v3` prompt set with impostor win rates "34% (4p1i) and 30% (9p2i)",
README.md:84 names the ladder tip at baseline 6, and docs/reading-guide.md:39-50 repeats both win
rates at :45 while crediting the guard to "the README's copy", beside two further rows the record
touches: 520/520 citation compliance (tests/eval/test_vj_instruments.py:509) and the 87% vent
cross-tab at :175-184 (70 flagged meetings against 95 unflagged). The pooled deduction cells the
results table states — 310/310 = 1.000 with proof against 46/125 = 0.368 without
(audits/audit-phase-19-close.md:233, pinned by tests/eval/test_deduction_metrics.py:163 and :237) —
are re-derived on the new bytes by those same pins. Every one of those is a cell the record either
moved or deliberately left standing. The whole argument of this phase — that a measurement made
after a pre-registration is worth more than a measurement made after a result — is only visible if
both columns are on the page.

The mechanical work is small because the earlier tasks built for it: the results table already stamps
each volatile row with its baseline and record date, so the edit is one added column and a header,
not a rewrite. What makes the task worth a contract is the discipline around the numbers. Quote; do
not compute. Every figure in this diff comes from `audits/audit-phase-20-baseline-7.md` or from the
test pin that owns it, and a figure with no pin does not go in the front door. The review-measured
bars the phase registered — false crew `whereabouts` 20.5%, sole-`alibi_vs_sighting` precision 14.6%,
grounded sighting side 36.5%, adjacent-room STRONG share 63.2% (all review-measured over the
committed baseline-6 bytes, re-pinned as committed cells by the honesty instrument set) and the
solvability y-axis (killer inside the crew's own candidate set in 581/626 body meetings = 92.8%, a
correct singleton in 103 of 109, and 61 of 354 ejections landing on a player the crew's pooled
perception had already cleared — same provenance) — are read off their new pins here, never
re-derived by hand.

The verdict sentence is the other half. The record's decision rule produced one of two outcomes, and
this task publishes whichever one happened in one sentence titled by its result: ADOPTED, in which
case baseline 7 is the ladder tip and `scripts/check_doc_facts.py:89` must point at the audit that
records it; or FINDING, in which case the record is published in full, the tip stands where it stood,
and the front door says so. The FINDING sentence is the stronger of the two and must not be softened
or buried — a project whose thesis is that it does not publish numbers it knows are confounded
cannot flinch at publishing a bar it missed. The decision itself belongs to the record audit; this
task states it and links it, and re-argues nothing.

There is one guard gap to close while the numbers are being touched. `scripts/check_doc_facts.py`
reads exactly one document (`_README` at :87, the only path threaded through `check_facts` at
:160-169), so the same win rates, refresh date and ladder-tip claim repeated in
docs/reading-guide.md are unguarded — the guide's own row at :45 says as much in prose, crediting the
check to "the README's copy". That is precisely the drift class the checker exists to kill, and after
a record it is the class most likely to fire: the guide and the ML page now repeat figures whose
committed source just moved. Widening the checker to the front-door document set, with a perturbation
test per new check, is what stops this page rotting the next time a baseline lands.

Finally, docs/ml-program.md needs an honest amendment rather than an update. The impostor mover's
target-selection defects are repaired now, so the comparator the Phase-17 and Phase-18 win edges
(+0.12 to +0.30) were measured against no longer exists in that form — and nothing was retrained, so
those figures were not re-measured. The page states that plainly: the erratum stands, the numbers are
stale by construction, and re-grounding them is a future owner decision, not a quiet edit.

**Files in scope:**
- README.md; (the results table's before/after column from audits/audit-phase-20-baseline-7.md; the status line; the demo sentence)
- docs/ml-program.md; (the Phase-20 read: what moved, what did not, the comparator note now that the FSM is repaired)
- docs/reading-guide.md; (the numbers table and the cross-tab re-quoted from the new pins; the featured table mirrors FEATURED_GAMES)
- docs/history.md; (Phase 20 row)
- scripts/check_doc_facts.py; (the new numbers checked against the new pins)
- tests/scripts/test_check_doc_facts.py

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
- [ ] The README states the record's verdict in one sentence titled by its result — ADOPTED, naming the new ladder tip, or FINDING, naming the bar that did not clear — and links `audits/audit-phase-20-baseline-7.md`; the sentence names at least one pre-registered bar that did not move.
- [ ] README's sample-provenance paragraph agrees with the new MANIFESTs on the refresh date, recording model, prompt-set family and version and both per-set impostor win rates, and every "ladder tip" sentence names the baseline the owning audit records; `scripts/check_doc_facts.py:89` points at that audit, and `uv run python scripts/check_doc_facts.py` is green at HEAD.
- [ ] `scripts/check_doc_facts.py` checks the moved facts wherever the front door repeats them — the win rates, the refresh date and the ladder-tip claim in docs/reading-guide.md and docs/ml-program.md, not README alone — and each new check has a perturbation case in tests/scripts/test_check_doc_facts.py that fails when the fact is drifted in the newly-covered document; docs/reading-guide.md:45's prose about which copy is guarded is updated to match.
- [ ] The reading guide's featured table equals `FEATURED_GAMES` seed-for-seed and in curated order, pinned by a check that parses the picker source and fails on an added, removed or re-ordered row; the guide's blurbs stay spoiler-free under the existing rule.
- [ ] docs/ml-program.md carries the Phase-20 read — which pre-registered bars moved, which did not, and the win split as the observed-not-gated secondary — plus the amended comparator note: the FSM target-selection defects are repaired, the Phase-17/18 win edges were measured against the defective comparator, nothing was retrained, so the erratum stands and the figures are stale by construction.
- [ ] docs/history.md gains the Phase-20 row in the file's existing shape, linking the record audit.
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
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 rows 3.1 and 3.2 ("the results table gains its before/after column … *pre-registered, measured, reported — including the part that did not move*") and §7 (the post-wave-2 pitch paragraph; endorsement edit (b): every volatile number carries its baseline stamp from day one "so wave 3 adds a column instead of rewriting the page"); audits/review-2026-08-19/C/collated-portfolio.md §A6 (state the results once, plainly — the enabling move this task completes) and §B3 (the reading guide is 3,239 words / 378 lines against an advertised five minutes, with `file:line` anchors already drifting); byte-coupled front-door anchors re-verified at HEAD — README.md:84 (the status/ladder-tip paragraph), README.md:149 (the single sample-provenance paragraph: `regenerated 2026-07-20`, the recording model, the `qwen3_6_27b` `v3` prompt set, "34% (4p1i) and 30% (9p2i)"); docs/reading-guide.md:39-50 (the numbers table), :45 (the row that states in prose that only *the README's* copy of the win rates is re-derived), :101-105 and :109-117 (the featured table and its claim to mirror `FEATURED_GAMES` exactly), :175-184 (the vent cross-tab, 70/95 meetings); scripts/check_doc_facts.py:87 (`_README` — the only document the checker reads), :89 (`_LADDER_TIP_AUDIT` = `audits/audit-phase-18-close.md`), :99-101 (the `ladder tip stands at baseline N` parse), :160-169 (`check_facts`), :172 (`check_sample_provenance`), :360 (`check_ladder_tip`); the pins the record moves — tests/eval/test_deduction_metrics.py:163 and :237 (the proof / non-proof cells; pooled 310/310 = 1.000 and 46/125 = 0.368 at audits/audit-phase-19-close.md:233), tests/eval/test_vj_instruments.py:509 (520/520 citation compliance), tests/api/test_sets.py:431 and :376 (the featured-seed and spoiler-free pins), frontend/src/components/ReplayPicker.tsx:102 (`FEATURED_GAMES`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
