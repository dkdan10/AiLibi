# Agent Prompt — 15.13 The pause: mid-phase audit, the seven decisions, and authoring Wave 2

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.13 — The pause: mid-phase audit, the seven decisions, and authoring Wave 2, anchored to audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; owner decisions 2026-07-05 (deployment + torch deferred to this pause). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-pause-audit`
**Depends on:** 15.8, 15.10, 15.11, 15.12
**Section refs:** audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; owner decisions 2026-07-05 (deployment + torch deferred to this pause)
**Complexity:** Integration

The wave boundary the phase was designed around: measure, decide, then author Wave 2 from evidence instead
of forecasts. Inputs (all machine-readable, all reproducible by the committed CLIs):
`results-impostor-bakeoff.jsonl` + `results-crew-track.jsonl` + `report-torch-probe.md` (per-entrant
gate/referee/fitness/KL/determinism/cost), `report-ballot-surrogate.md` (fidelity vs honest ceiling +
verdict), `report-goodhart-probe.md` (+ the 15.10 surrogate-path re-run), the corpus MANIFESTs + gate
outputs. Plus ONE fresh measurement this task runs: the operator-run REAL-LLM finalist evaluation — the top
1–2 bake-off candidates re-recorded on the canonical 50-seed 9p2i set against `Qwen/Qwen3-32B` (Featherless
$0, ~2.5h per finalist), scored by `scripts/validity_gate.py` + `scripts/measure_baseline.py
--watchability`, so the method decision rests on at least one real-meeting-path measurement, not only
fake-provider/surrogate numbers (finalist recordings are working artifacts quoted in the audit — they do
NOT replace or join `replays/samples/`). The audit (`audits/audit-phase-15-pause.md`) tabulates every
entrant on the single protocol and records the SEVEN owner decisions with rationale: (1) winning method +
champion candidate; (2) deployment end-state — opt-in factory beside the FSM default vs new default +
baseline-3 re-record; (3) torch — promote / keep experiment-tier / retire, incl. the distillation route;
(4) Wave-2 co-evolution GO/NO-GO (scoped only if GO, with the full stabilizer stack); (5) the crew
observation-surface change (owned-task set) YES/NO; (6) inference weight representation — float-hex vs
int-quantized — plus an enumeration of every determinism loosening now live; (7) the surrogate re-grounding
cadence going forward. Then this task AUTHORS the Wave-2 contracts into this file (IDs 15.14+, every
validator rule honored: full contract fields, scope-overlap edges, the CI tail), regenerates prompts, and
replaces the end-of-phase merge-criteria placeholder with the real criteria for the chosen deployment
branch.

**Files in scope:**
- audits/audit-phase-15-pause.md (new)
- tasks/phase-15.md (Wave-2 contracts + STATUS banner update + end-of-phase merge criteria)
- agent_prompts/ (mechanically regenerated task-15-* prompts for the new Wave-2 contracts — generator output, never hand-edited)

**Files NOT in scope:**
- training/ + eval/ + agents/ + engine/ + orchestrator/ (measurement is read-only; any referee patch the Goodhart findings demand becomes a Wave-2 contract, never a pause edit)
- replays/samples/ + replays/ml_corpus/ (untouched; finalist recordings live outside both)
- DESIGN.md + AGENT_IMPLEMENTATION.md (owner-side; any design amendment the decisions imply is recorded as an ask in the audit)

**Definition of done:**
- [ ] The audit tabulates every entrant (bake-off, crew, torch, distilled student) on the single metric tuple, with every quoted number regenerated from the committed CLIs/jsonl — zero hand-computed figures (each table cites its source artifact).
- [ ] The real-LLM finalist evaluation is run, its gate + referee results quoted, and its divergence (if any) from the fake-provider/surrogate numbers analyzed — the method decision explicitly cites it.
- [ ] All seven decisions are recorded with owner sign-off and rationale, including the NO paths (what was rejected and why).
- [ ] The Wave-2 contracts are authored into this file per the chosen branch, `uv run python scripts/validate_task_docs.py` + `uv run python scripts/generate_prompts.py --check` pass with the new contracts, and the STATUS banner + end-of-phase merge criteria reflect the decisions.
- [ ] The pause explicitly re-verdicts the referee: the Goodhart probe's findings (both runs) either cleared or their floors are contracted into Wave 2 before any champion selection uses the referee.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Model the audit on `audits/post-phase-14-pause.md` (label discipline, verdict-in-one-line, punch list) and
the decision block on Task 14.6's LOCKED-DECISION shape. The Wave-2 sketch at the bottom of this file is
the authoring skeleton — each bullet becomes a contract or is explicitly dropped with a reason. When
authoring contracts, re-read `scripts/_task_parser.py`'s rules (header em-dash, ID grammar, contract field
order, scope-overlap semantics, globally-unique public types) — the validator is the gate, and the new
prompts must be generator output.

## Integration risk

Self-certification is the trap this task exists to prevent — every number must trace to a committed
artifact, and the referee cannot bless a champion until its own red-team verdict is resolved. The second
trap is validator-invalid Wave-2 contracts: a malformed `tasks/phase-15.md` breaks
`validate_task_docs.py` for the WHOLE repo (the parser aggregates all phases), so the authoring step must
run the full check locally before the PR. Third: the finalist recordings must stay out of
`replays/samples/` and `replays/ml_corpus/` — provenance separation between "the canonical baseline," "the
frozen training corpus," and "pause working artifacts" is what keeps every later claim attributable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.determinism"`
- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.crew.options"`
- `uv run python -c "import training.crew.scorer"`
- `uv run python -c "import training.bakeoff.es"`
- `uv run python -c "import training.bakeoff.goodhart"`
- `uv run python -c "import eval.watchability"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import training.surrogate.ballots"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import engine.rng"`

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
Open a PR from branch `phase-15-pause-audit` with a title like `task 15.13: the pause: mid-phase audit, the seven decisions, and authoring wave 2`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; owner decisions 2026-07-05 (deployment + torch deferred to this pause)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
