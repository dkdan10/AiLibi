# Agent Prompt — 18.18 The Goodhart re-probe: conviction path + the carried 4p1i exploit

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.18 — The Goodhart re-probe: conviction path + the carried 4p1i exploit, anchored to training/bakeoff/goodhart.py (the probe machinery); audits/audit-phase-17-close.md §6 (the carried `d4-contest-farming` finding: +61.8% on the 4p1i reference roster — re-probe before any 4p1i-scored selection); training/reports/report-goodhart-probe.md (the standing report this extends); the standing rule: the probe re-runs when the training-signal role grows. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-goodhart-reprobe`
**Depends on:** 18.16
**Section refs:** training/bakeoff/goodhart.py (the probe machinery); audits/audit-phase-17-close.md §6 (the carried `d4-contest-farming` finding: +61.8% on the 4p1i reference roster — re-probe before any 4p1i-scored selection); training/reports/report-goodhart-probe.md (the standing report this extends); the standing rule: the probe re-runs when the training-signal role grows
**Complexity:** Medium

The training-signal role grew (the conviction term + pre-screen), so the probe re-runs
BEFORE any campaign selection leans on the new signal: the forced-lever sweep with the
conviction term live (can a lever family launder predicted-supply into fitness without
supplying real evidence?), the composed-gate laundering check, and the carried
`d4-contest-farming` 4p1i exploit re-probed at the current substrate. Findings recorded
with the materiality bar; any exploitable seam becomes a named blocker for 18.24's
protocol, never a silent caveat.

**Files in scope:**
- training/bakeoff/goodhart.py (the conviction-path probe arms)
- training/reports/report-goodhart-probe.md (the re-probe reading)
- tests/training/test_goodhart_probe.py; (re-pins + the new arms' fixtures)

**Files NOT in scope:**
- training/conviction/ + training/bakeoff/harness.py (probed, never edited)

**Definition of done:**
- [ ] The probe reports the conviction-term delta per forced lever beside the standing bars, the composed-gate verdict, and the 4p1i `d4-contest-farming` re-read, each with its materiality arithmetic; any above-bar finding is named in the report's blocker section.
- [ ] Conviction-model use during the probe is metered and quoted (the consumption discipline).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The probe's delta convention is unchanged; the new question is narrow — does the conviction
TERM (a prediction) diverge from the recorded REALITY (flags in bytes) under adversarial
levers, and by how much. Report predicted-vs-actual side by side per lever.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
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
Open a PR from branch `phase-18-goodhart-reprobe` with a title like `task 18.18: the goodhart re-probe: conviction path + the carried 4p1i exploit`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/bakeoff/goodhart.py (the probe machinery); audits/audit-phase-17-close.md §6 (the carried `d4-contest-farming` finding: +61.8% on the 4p1i reference roster — re-probe before any 4p1i-scored selection); training/reports/report-goodhart-probe.md (the standing report this extends); the standing rule: the probe re-runs when the training-signal role grows), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
