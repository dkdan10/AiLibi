# Agent Prompt — 20.43 The instrument reads what v4 speaks: the movement-sided sighting resolves, a duplicated flag counts once

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.43 — The instrument reads what v4 speaks: the movement-sided sighting resolves, a duplicated flag counts once, anchored to audits/audit-phase-20-smoke.md §11 (the defect write-up: seeds 13 and 40, meeting-0 flags whose sighting side is a spoken `saw_move`; the exact raise reproduced; the blast radius; this routing slot) and §12 (the ABANDON verdict this task exists to lift); audits/audit-phase-20-preregistration.md §11 (the amendment log this task extends with one dated erratum) and §5 (the render census and I-11 precedents for instrument errata that move no bar); anchors re-verified by the smoke agent at HEAD d1381d7e: eval/evidence_honesty.py:2083-2131 (`_resolve_flag`, which accepts only a `SawPlayerObservation` on the sighting side and returns None on the movement shape) and :2043 (`_fold_flags`, whose guard raises on an unresolved flag so it cannot vanish from I-4/I-6/I-7 while counting in I-3 — the guard is RIGHT and stays); meetings/transcript.py `_apply_movement_claim_shape` and `_resolve_movement_sighting` (the detector semantics the resolver must mirror: a spoken `a at t-1 -> b at t` reads as the DESTINATION placement b at t; the file is FROZEN — read it, never edit it); scripts/counterfactual_phase20.py (shares `_fold_flags`; re-run its committed-sets leg to prove it still reproduces); the preserved smoke bytes at the scratch path named in audits/audit-phase-20-smoke.md (read-only evidence; they are NOT committed and no test may depend on that path). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-movement-sided-resolver`
**Depends on:** 20.34 and 20.35 — the smoke record surfaced this defect and its report is the specification; the counterfactual landed the shared fold this task must not fork
**Section refs:** audits/audit-phase-20-smoke.md §11 (the defect write-up: seeds 13 and 40, meeting-0 flags whose sighting side is a spoken `saw_move`; the exact raise reproduced; the blast radius; this routing slot) and §12 (the ABANDON verdict this task exists to lift); audits/audit-phase-20-preregistration.md §11 (the amendment log this task extends with one dated erratum) and §5 (the render census and I-11 precedents for instrument errata that move no bar); anchors re-verified by the smoke agent at HEAD d1381d7e: eval/evidence_honesty.py:2083-2131 (`_resolve_flag`, which accepts only a `SawPlayerObservation` on the sighting side and returns None on the movement shape) and :2043 (`_fold_flags`, whose guard raises on an unresolved flag so it cannot vanish from I-4/I-6/I-7 while counting in I-3 — the guard is RIGHT and stays); meetings/transcript.py `_apply_movement_claim_shape` and `_resolve_movement_sighting` (the detector semantics the resolver must mirror: a spoken `a at t-1 -> b at t` reads as the DESTINATION placement b at t; the file is FROZEN — read it, never edit it); scripts/counterfactual_phase20.py (shares `_fold_flags`; re-run its committed-sets leg to prove it still reproduces); the preserved smoke bytes at the scratch path named in audits/audit-phase-20-smoke.md (read-only evidence; they are NOT committed and no test may depend on that path)

The smoke proved the recording half of the stack and broke the measuring half: two recorded `alibi_vs_sighting` flags carry a spoken `saw_move` on the sighting side — the exact shape lever 3 (20.25) is specified to mint and the v4 prompt set (20.31) is the first to elicit — and `_resolve_flag` returns None on them, so `_fold_flags` raises and every honesty cell dies with it. The fix is the resolver, not the guard: teach `_resolve_flag` the movement-sided sighting, resolving it exactly as the frozen detector does — the destination room at the destination tick — so I-4 tolerance, I-6 adjacency and I-7 origin classification read the flag as minted. Second, smaller: the smoke bytes show the movement-sided flag DUPLICATED (the same alibi/sighting pair recorded twice in one meeting, seeds 13 and 40). The production mint is frozen; this task dedups at the instrument read — a flag identity seen twice in one meeting folds ONCE into every cell — and records the production-side dedup as a routed post-record item in the erratum. No committed cell can move: zero of the 1,956 committed v3-era prompts carry the `saw_move` shape (the smoke report §11 measured it), and the DoD asserts that OFF-neutrality rather than assuming it.

**Files in scope:**
- eval/evidence_honesty.py; (`_resolve_flag` gains the movement-sided sighting arm mirroring the frozen detector's destination read; the per-meeting fold dedups flags by identity before any cell counts; nothing else — the raising guard at `_fold_flags` stays exactly as it is)
- tests/eval/test_evidence_honesty.py; (a SYNTHETIC minimal fixture — a constructed meeting entry carrying a movement-sided `alibi_vs_sighting` flag — proves the resolver folds it into I-4/I-6/I-7 with the destination read; its twin with the flag duplicated proves it counts once in every cell; a planted wrong-shape case proves the guard still raises on a genuinely unresolvable flag; every committed pin reproduces unchanged)
- audits/audit-phase-20-preregistration.md; (§11 amendment log ONLY — one dated entry: the resolver arm, the instrument-side dedup, the production-mint dedup routed post-record, and that no ratified bar moved)

**Files NOT in scope:**
- meetings/transcript.py, meetings/manager.py, agents/, observation/, orchestrator/ (FROZEN per §9 — the detector semantics are read and mirrored, never edited; the production duplicate mint is routed, not fixed here)
- scripts/measure_baseline.py and scripts/counterfactual_phase20.py (consumers of the fixed instrument; both are re-RUN by the Measurement, neither is edited)
- replays/ and the smoke scratch directory (no committed byte moves; no test depends on an uncommitted path)
- tasks/phase-20.md and agent_prompts/ (the orchestrator owns coordination)

**Definition of done:**
- [ ] `_resolve_flag` resolves a movement-sided sighting to the destination room at the destination tick, mirroring `_apply_movement_claim_shape`'s read, with the mirror stated in a comment that cites the frozen source line; a genuinely unresolvable flag still raises through `_fold_flags` (planted case).
- [ ] A flag identity recorded twice in one meeting folds once into every cell family (synthetic twin fixture), and the erratum names the production-side mint dedup as routed post-record.
- [ ] Every committed pin in tests/eval/test_evidence_honesty.py passes unchanged, and `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` prints the identical committed cells — OFF-neutrality asserted, not assumed.
- [ ] `uv run python scripts/counterfactual_phase20.py --sets all` reproduces its committed predictions byte-for-byte (the shared fold did not drift).
- [ ] The §11 erratum entry is one dated row and no bar, cell definition or §4 target moved anywhere in the memo.
- [ ] `bash scripts/check.sh` passes.

**Complexity:** Small
**Record impact:** none on committed cells (the v3 corpus carries zero movement-sided sightings — smoke report §11's measured 0/1,956); this task UNBLOCKS the smoke re-measure and therefore the record window.
**Measurement:** `uv run pytest tests/eval/test_evidence_honesty.py -q` green with the three new cases named in the PR; `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` prints the committed cells unchanged; `uv run python scripts/counterfactual_phase20.py --sets all` byte-identical to its committed output — all three pasted into the PR Summary.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
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
Open a PR from branch `phase-20-movement-sided-resolver` with a title like `task 20.43: the instrument reads what v4 speaks: the movement-sided sighting resolves, a duplicated flag counts once`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-20-smoke.md §11 (the defect write-up: seeds 13 and 40, meeting-0 flags whose sighting side is a spoken `saw_move`; the exact raise reproduced; the blast radius; this routing slot) and §12 (the ABANDON verdict this task exists to lift); audits/audit-phase-20-preregistration.md §11 (the amendment log this task extends with one dated erratum) and §5 (the render census and I-11 precedents for instrument errata that move no bar); anchors re-verified by the smoke agent at HEAD d1381d7e: eval/evidence_honesty.py:2083-2131 (`_resolve_flag`, which accepts only a `SawPlayerObservation` on the sighting side and returns None on the movement shape) and :2043 (`_fold_flags`, whose guard raises on an unresolved flag so it cannot vanish from I-4/I-6/I-7 while counting in I-3 — the guard is RIGHT and stays); meetings/transcript.py `_apply_movement_claim_shape` and `_resolve_movement_sighting` (the detector semantics the resolver must mirror: a spoken `a at t-1 -> b at t` reads as the DESTINATION placement b at t; the file is FROZEN — read it, never edit it); scripts/counterfactual_phase20.py (shares `_fold_flags`; re-run its committed-sets leg to prove it still reproduces); the preserved smoke bytes at the scratch path named in audits/audit-phase-20-smoke.md (read-only evidence; they are NOT committed and no test may depend on that path)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
