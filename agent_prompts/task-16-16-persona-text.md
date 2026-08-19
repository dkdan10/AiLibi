# Agent Prompt — 16.16 Persona text: the voice layer, evidence-gated (second bump)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.16 — Persona text: the voice layer, evidence-gated (second bump), anchored to audits/post-phase-14-Voice-and-Judgment-planning.md §4.1-4.2 (the persona-conditioning design + the distinctness toolkit + the design caution); orchestrator/personas.py (16.9's bank + assignment); the locked set directory (behind 16.15's bump). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-persona-text`
**Depends on:** 16.9, 16.15
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §4.1-4.2 (the persona-conditioning design + the distinctness toolkit + the design caution); orchestrator/personas.py (16.9's bank + assignment); the locked set directory (behind 16.15's bump)
**Complexity:** Medium

The Voice half, landing last by design (the edges enforce the planning doc's thesis: the citation
gate and the judgment surface are merged before any voice gets louder). Render each participant's
persona card into the instruction preamble of all four templates — disposition + diction notes
shaping HOW the agent talks (`free_text`/`rationale_text` style), never WHAT it may claim
(observations/claims/ballots stay schema-locked; the persona never enters `rendered_memory` — the
firewall-orthogonality the planning doc proves). Guarded byte-identical: an empty persona renders
the exact pre-16.16 bytes (golden-proven), so the layer is inert wherever assignment is off. One
version bump owned here (the second on the locked set: v2 → v3 GO path; the NO-GO arithmetic per
16.2's surgery). Distinctness discipline from the toolkit: contrasting dispositions in the bank,
per-turn re-anchoring line, and the anti-sycophancy contrast (the aggressive-accuser /
cautious-hedger / quiet-follower spread that resists premature consensus). The phase's named
pairing is enforced at close: 16.17 reads the voice metrics ALONGSIDE the zero-flag conviction
rate — a zero-flag rise attributable to personas is the phase NO-GO.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (persona preamble region in all four templates — behind 16.15's edits)
- orchestrator/game.py (the locked set's version entry — the second bump; behind 16.15's)
- data/personas.json (card-text refinement region — the bank 16.9 committed; structure unchanged)
- tests/meetings/test_persona_render.py (new: empty-persona byte-identity + per-card render fixtures + the re-anchor line presence)

**Files NOT in scope:**
- orchestrator/personas.py (assignment logic frozen from 16.9; only card TEXT refines)
- meetings/ + agents/memory/ (no mechanism — pure surface)
- replays/samples/ (the re-record is 16.17)

**Definition of done:**
- [ ] Empty persona = byte-identical render (golden green on committed sets); each bank card renders into the preamble on a fixture with the schema-locked sections untouched.
- [ ] The persona text shapes style only: fixtures assert the persona block appears in the instruction preamble and NOWHERE in the memory/observation sections; the leak-suite role-neutrality sweep re-runs green on the refined cards.
- [ ] The second version bump is exactly one registry entry; the per-turn re-anchor line is present in the turn template (drift discipline).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Persona cards read as stage directions, not biographies: one disposition sentence, two diction
notes, one thing this voice never does. The re-anchor line ("stay in the voice described above")
goes at the turn template's response instructions — the cheap fix for multi-turn drift the
literature and the toolkit both point at. Resist trait taxonomies; the bank is a spread of
argumentative dispositions, which is what breaks consensus cascades.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.watchability"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import orchestrator.personas"`

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-16-persona-text` with a title like `task 16.16: persona text: the voice layer, evidence-gated (second bump)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-Voice-and-Judgment-planning.md §4.1-4.2 (the persona-conditioning design + the distinctness toolkit + the design caution); orchestrator/personas.py (16.9's bank + assignment); the locked set directory (behind 16.15's bump)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
