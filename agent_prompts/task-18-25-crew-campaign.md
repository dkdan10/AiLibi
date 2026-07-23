# Agent Prompt — 18.25 THE CREW CAMPAIGN (operator, multi-session, ~30–40h real-path legs)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.25 — THE CREW CAMPAIGN (operator, multi-session, ~30–40h real-path legs), anchored to the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-crew-campaign`
**Depends on:** 18.24
**Section refs:** the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)
**Complexity:** Integration

The counter-adaptation half: evolve the crew side (both bases: general + owned-task)
against the frozen impostor campaign champions + hall of fame, with the conviction-supply
term giving crew fitness the conviction-economy gradient the fake path denies it, the
interrupt-preserving constraint kept (the 15.22 guard — starvation stays unreachable), and
real-path re-ranks per generation. Reachability honesty (the merged driver, 316d4e5): the
frozen-champion half of that shape is direct, the hall half is NOT — there is no seam for
adopting 18.24's committed hall as this campaign's opponent pool; the impostor side enters
via `impostor.initial_genome` seeded from a committed 18.24 champion (re-frozen as a fresh
lineage in this campaign's own hall; founders are substrate-fenced MAP-Elites cells only),
so the counter-adaptation reading is against the champion lineage plus this campaign's own
accumulating hall, and if the report judges full-pool continuity load-bearing that is a
routed amendment, never a silent driver edit. Crew mechanics the driver pins:
`first_side="crew"`; the crew side config structurally REJECTS `anchor_policy` (crew
anchor-CE is FSM-fixed by construction); the crew builder must emit a `crew-`-prefixed
`encoder_version` (the 18.19 conflation guard, enforced both directions). Report mirrors 18.24 (rows, cycling detector, floor
sensitivity, emergence sweeps — crew-side instruments emphasized: roll-call coverage,
conversion, counter-adaptation evidence against the specific impostor champions). Crew
champion adoption is NOT this task's call: candidates route to 18.26/18.27 evidence.
Duration honesty: the crew slate is smaller than 18.24's but the per-generation real-path
re-rank arithmetic is the same — plan **~30–40 h** of unattended real-path legs across
sessions, checkpoint-push per generation.

**Files in scope:**
- training/reports/report-crew-campaign.md (new) + training/reports/results-crew-campaign.jsonl (new)
- training/artifacts/coevo/ (crew-side frozen artifacts, via the driver; disjoint gen dirs from 18.24's — the store layout separates sides)
- tests/training/test_coevo_driver.py; (crew-campaign row pins ONLY — additive to 18.24's region)

**Files NOT in scope:**
- training/coevo/*.py + training/crew/*.py (runs, not redesigns)
- agents/tactical/learned/; (adoption is 18.27's evidence question)

**Definition of done:**
- [ ] The campaign report carries the full row/benchmark/meter discipline, the counter-adaptation reading (does trained crew close the frozen champion's win edge, and through which instrument channels), and the real-path re-rank tables with stamp proofs.
- [ ] Every candidate emergence behavior this campaign surfaces carries its 18.4-named ablation run and provenance in the report (the 18.24 discipline, crew side).
- [ ] The gate-validity discipline holds throughout (no starvation-family candidate survives selection; validity-gate columns quoted per entrant), and crew finalists (if any clear the bars) are named for 18.26.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The interesting cell is pace-to-wins conversion on the REAL path (the 17.13 open question:
does the citation-era conviction channel move an owned-task crew's pace advantage?) —
answer it with the campaign's real re-rank data and say so explicitly either way. Stamp
obligation (routed by the 18.19 verification): the committed measurement-tier
`training/artifacts/crew/` dirs carry NO `stamp.json`, so the `--crew-artifact` arm fails
loud on them BY DESIGN — every crew artifact this campaign freezes carries the five-field
stamp, and the first dual-stamped crew recordings are this campaign's re-rank legs.

## Integration risk

Crew real-path evals are the phase's first learned-crew recordings — the 18.7/18.19 stamp
guards get their first live exercise; any conflation or leak finding stops the campaign leg
until routed.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.conviction.serving"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`
- `uv run python -c "import training.anchor_study"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-18-crew-campaign` with a title like `task 18.25: the crew campaign (operator, multi-session, ~30–40h real-path legs)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
