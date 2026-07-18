# Agent Prompt — 18.16 Fitness-term + referee pre-screen integration

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.16 — Fitness-term + referee pre-screen integration, anchored to training/bakeoff/harness.py:569-590 (`inner_episode_fitness` + the gate/reward boundary comment at :582-585); audits/audit-phase-18-planning.md §2.3 (the two consumption modes); the 18.15 verdict (which modes are live). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-conviction-integration`
**Depends on:** 18.14, 18.15
**Section refs:** training/bakeoff/harness.py:569-590 (`inner_episode_fitness` + the gate/reward boundary comment at :582-585); audits/audit-phase-18-planning.md §2.3 (the two consumption modes); the 18.15 verdict (which modes are live)
**Complexity:** Medium

Wire the conviction model into BOTH sides' fitness under the GO verdict: an additive
`conviction_weight × predicted-supply` term in the impostor inner fitness
(`training/bakeoff/harness.py::inner_episode_fitness`) AND in the crew fitness
(`training/crew/scorer.py::crew_inner_episode_fitness` — a separate function that does NOT
route through the harness; the crew campaign trains without the gradient unless this seam
is wired here), plus a pre-screen hook the campaign driver calls before spending real-path
evals. Under NO-GO the term is structurally absent from both sides (not zero-weighted) and
the pre-screen is advisory-labeled. This task also adds the **additive anchor-policy seam**:
`DecisionTrace`/`inner_episode_fitness` accept an optional anchor policy (default: the
scripted FSM, byte-identical behavior when unset) so a campaign entrant can anchor to the
18.5 filtered-BC artifact — the seam's second consumer is 18.24's refined-anchor entrant
configuration. The gate/reward boundary comment extends to name the new term's provenance;
use-counting flows through the model's own sha-keyed counter.

**Files in scope:**
- training/bakeoff/harness.py; (the impostor term + the pre-screen seam + the anchor-policy seam + the boundary comment)
- training/crew/scorer.py (the crew-side conviction term — the fitness composition only)
- tests/training/test_bakeoff_harness.py; (term-provenance fixtures; NO-GO structural absence; counter threading; anchor-policy default byte-identity; the AST firewall extended to training/conviction)
- tests/training/test_crew_scorer.py (the crew-side term fixtures)

**Files NOT in scope:**
- training/conviction/ (consumed via its public seam)
- training/rewards.py (the dense terms do not move — this is fitness composition on both sides)
- training/crew/options.py (the menu does not move)

**Definition of done:**
- [ ] With a GO artifact both sides' fitness carries the term (impostor via the harness, crew via `crew_inner_episode_fitness`) with its weight named in the row metadata; with NO-GO the term is absent from both and rows say so; both fixture-pinned.
- [ ] The anchor-policy seam defaults to the scripted FSM with provably byte-identical fitness when unset, and an alternative anchor policy threads through trace + fitness, fixture-pinned.
- [ ] The pre-screen returns a machine-readable predicted-floors verdict consumed by tests, metered against the conviction counter, and documented as advisory-only under NO-GO.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The anchor-CE penalty's integration is the template (a named, weighted, metadata-carried
term). Keep the default `conviction_weight` conservative (≤ the anchor weight) — the λ/
weight tuning belongs to the 18.24 campaign protocol, not this integration.

## Public types this task introduces
- `training.bakeoff.harness.conviction_prescreen`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-18-conviction-integration` with a title like `task 18.16: fitness-term + referee pre-screen integration`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/bakeoff/harness.py:569-590 (`inner_episode_fitness` + the gate/reward boundary comment at :582-585); audits/audit-phase-18-planning.md §2.3 (the two consumption modes); the 18.15 verdict (which modes are live)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
