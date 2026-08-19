# Agent Prompt — 19.16 The outsider reading guide + the audit-idiom glossary

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.16 — The outsider reading guide + the audit-idiom glossary, anchored to audits/audit-phase-19-triage.md §7 item 17 [S-Claude] + rows 23 (N1/N2 and the clean negatives), the legibility-cliff finding (audit-phase-19-input-claude.md §3.2 item 5: the corpus is case law with no glossary); the named good-tail seeds (19.9's featured list). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-reading-guide`
**Depends on:** 19.1, 19.9 (the guide's demo path quotes 19.9's featured curation — it cannot publish before the curation exists)
**Section refs:** audits/audit-phase-19-triage.md §7 item 17 [S-Claude] + rows 23 (N1/N2 and the clean negatives), the legibility-cliff finding (audit-phase-19-input-claude.md §3.2 item 5: the corpus is case law with no glossary); the named good-tail seeds (19.9's featured list)
**Complexity:** Medium

The project's institutional memory is unreadable to outsiders — the strongest single
asset (the honesty machinery) is invisible behind the idiom. Write `docs/reading-guide.md`
(~200 lines): the meta-story (the workflow experiment, the honesty culture, the key
verified numbers each with its committed source path); a glossary of the audit idiom
(baseline N, the ladder tip, the §1.3 bar, canary denominator, NO-FLIP,
findings-not-failures, the 15.18 convention, graduated levers, adopting records, the
two-owner gate, errata discipline); a "where the bodies are buried" tour (the three
audits worth reading first and what each proves); the demo path (the featured seeds and
why each is worth watching); the capability distinctions an outsider needs
(evidence-processing vs deception vs general social deduction — with the vent-proof
qualification stated plainly); and the honest ML story (N1/N2, the clean negatives, the
frozen program, where the reopening checklist lives). README links it.

**Files in scope:**
- docs/reading-guide.md (new)
- README.md; (the link line only)

**Files NOT in scope:**
- audits/ (the corpus is described, never rewritten)
- docs/architecture.md (19.1's file)

**Definition of done:**
- [ ] Every number quoted carries its committed source path; every glossary entry is verifiable against a cited audit usage; the guide's demo path matches 19.9's featured list.
- [ ] An outsider path exists: README → guide → demo → the three named audits, with no undefined idiom on the path.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Write for a senior engineer with zero context and five minutes: short declarative
sentences, the numbers doing the arguing. The vent-proof qualification (87% of correct 9p
ejections ride an ejectee-specific vent sighting; ~30–39% otherwise) belongs in the
capability section stated exactly — the guide's credibility rests on volunteering it.

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
Open a PR from branch `phase-19-reading-guide` with a title like `task 19.16: the outsider reading guide + the audit-idiom glossary`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 17 [S-Claude] + rows 23 (N1/N2 and the clean negatives), the legibility-cliff finding (audit-phase-19-input-claude.md §3.2 item 5: the corpus is case law with no glossary); the named good-tail seeds (19.9's featured list)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
