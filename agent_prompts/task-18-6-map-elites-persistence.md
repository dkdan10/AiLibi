# Agent Prompt — 18.6 MAP-Elites cell persistence + referee-tension descriptors

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.6 — MAP-Elites cell persistence + referee-tension descriptors, anchored to audits/audit-phase-18-planning.md §4 (#10) + §6 (the GAME/QD transfer); training/bakeoff/map_elites.py:207-219 (in-memory cell genomes), :407-418 + :452-458 (the freeze that discards them); training/bakeoff/harness.py:843-868 (`write_candidate_artifact`, the layout to mirror). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-map-elites-persistence`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §4 (#10) + §6 (the GAME/QD transfer); training/bakeoff/map_elites.py:207-219 (in-memory cell genomes), :407-418 + :452-458 (the freeze that discards them); training/bakeoff/harness.py:843-868 (`write_candidate_artifact`, the layout to mirror)
**Complexity:** Medium

Two changes to the QD instrument. (1) **Persist every filled cell's genome** at freeze
(per-cell weights + sha sidecars under the archive artifact dir, mirroring the candidate
layout) so the archive becomes a reloadable behaviorally-diverse pool — the hall-of-fame
seed source 18.20 consumes. (2) **Add a second descriptor configuration** whose axes are the
referee's tension quantities computed from tactical facts (per-episode evidence-supply
proxies: witnessed-kill fraction and meeting cadence beside win) — watchability quantities
as DESCRIPTORS (diversity dimensions), never fitness; cell quality stays the standing inner
fitness. The existing 3-axis archive and its committed rows stay byte-stable; the new
configuration is additive and selected explicitly.

**Files in scope:**
- training/bakeoff/map_elites.py (cell persistence + the additive descriptor configuration)
- tests/training/test_bakeoff_methods.py (the map-elites regions: round-trip of persisted cells; the additive config; byte-stability of the default run)
- training/artifacts/impostor/map-elites/ (the persisted-cell layout, regenerated deterministically)

**Files NOT in scope:**
- training/bakeoff/harness.py; (its artifact writer is imported, never edited)
- eval/watchability.py; (descriptors are computed from rollout facts, never from the referee)

**Definition of done:**
- [ ] A full-budget run persists every filled cell's genome with sha sidecars and reloads them bit-exactly; the default-configuration run's champion, jsonl row, and existing artifact tree are byte-identical to the committed state (pinned); the persisted-cell index carries the substrate sha the cells were scored against (the 18.24 stale-seed refusal reads it — a Wave-1 substrate adoption makes these cells re-run-before-use, a cheap deterministic re-run).
- [ ] The referee-tension descriptor configuration is additive, documented, and its axes are computed from `DecisionTrace`/rollout facts only — grep-provably no `eval.watchability` import in the entrant module (the standing AST firewall extends to it).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The witnessed-kill fraction and meeting-cadence descriptors already exist as rollout
descriptor fields — the new configuration is a re-binning, not new plumbing. Persistence
must be deterministic in iteration order (sorted cell keys) so re-runs are byte-identical.

## Public types this task introduces
- `training.bakeoff.map_elites.write_archive_cell_artifacts`
- `training.bakeoff.map_elites.load_archive_cell_genomes`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-map-elites-persistence` with a title like `task 18.6: map-elites cell persistence + referee-tension descriptors`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#10) + §6 (the GAME/QD transfer); training/bakeoff/map_elites.py:207-219 (in-memory cell genomes), :407-418 + :452-458 (the freeze that discards them); training/bakeoff/harness.py:843-868 (`write_candidate_artifact`, the layout to mirror)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
