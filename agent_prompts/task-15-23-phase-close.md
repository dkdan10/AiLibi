# Agent Prompt — 15.23 Phase close: gates on the shipped end-state, the close audit, the banner flip (operator-run, $0)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.23 — Phase close: gates on the shipped end-state, the close audit, the banner flip (operator-run, $0), anchored to audits/audit-phase-15-pause.md (the decisions this close verifies + the finalist recipe §3.1 re-run here through the CLI); tasks/phase-14.md 14.12 + audits/audit-phase-14-close.md (the close-audit pattern); audits/review-phase-15-midwave.md Q3 (corpus canary denominators) + Q5 (the provenance-durability convention this record follows). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-close`
**Depends on:** 15.19, 15.20, 15.21, 15.22
**Section refs:** audits/audit-phase-15-pause.md (the decisions this close verifies + the finalist recipe §3.1 re-run here through the CLI); tasks/phase-14.md 14.12 + audits/audit-phase-14-close.md (the close-audit pattern); audits/review-phase-15-midwave.md Q3 (corpus canary denominators) + Q5 (the provenance-durability convention this record follows)
**Complexity:** Integration

Close the phase on the shipped branch-A end-state. Record ONE fresh champion evaluation on the
canonical 50-seed 9p2i set against the real provider — now through the committed CLI
(`scripts/run_tournament.py --agent-factory learned-champion`, the 15.21 surface; no Python driver
needed anymore) — as an uncommitted working artifact per the pause's provenance separation, with the
Q5 convention honored (annotated tag at the recording commit, or the sha back-filled into the committed
measurement rows). Score it with the committed CLIs — validity gate, R-gate, the HARDENED 15.19
referee, funnel — and commit the measurement as `training/reports/results-champion-close.jsonl` (the
same row shape as `results-finalist-eval.jsonl`: the five-field stamp read back from the recording
bytes + the committed sidecar sha it was verified against). Write
`audits/audit-phase-15-close.md`: the gates re-run green on HEAD, the champion recording PASSES the
validity gate + the hardened referee (this is the one PASS-bar of the close; a failure here pauses for
an owner call rather than shipping), the R-gate and funnel deltas vs baseline 3 reported as FINDINGS,
canaries judged on the corpus denominators with the 50-seed figures alongside (Q3), every committed
replay byte-verified bare, provenance verified end-to-end (stamp + MANIFEST + sha equality), the torch
disposition (decision 3) re-stated as permanent record, and the Phase-16 hand-off inputs (v5
vent-elicitation uptake, the residual zero-flag channel, the funnel deltas) restated for the
`tasks/phase-16.md` author. Flip the STATUS banner to CLOSED with the end-state, the champion identity
+ sha, and the close-audit pointer.

**Files in scope:**
- audits/audit-phase-15-close.md (new: the close finding)
- training/reports/results-champion-close.jsonl (new: the committed champion-close measurement rows — CLI output data, not code)
- tasks/phase-15.md (STATUS banner flip region only)

**Files NOT in scope:**
- replays/samples/ + replays/ml_corpus/ (byte-untouched — branch A ships no baseline 4; the close recording is an uncommitted working artifact)
- eval/ + agents/ + training/ code (the close measures; any defect it finds becomes a Phase-16/17 contract, never a close edit)
- README.md (the samples provenance paragraph still describes baseline 3, which is still the canonical truth under branch A)

**Definition of done:**
- [ ] The champion close recording exists per the documented recipe (seeds 0–49, 9p2i, `Qwen/Qwen3-32B`, `--agent-factory learned-champion`), its read-back stamps are uniform with `weights_sha256` equal to the committed sidecar digest, and the Q5 provenance convention is demonstrably followed (tag or back-filled sha named in the audit).
- [ ] `training/reports/results-champion-close.jsonl` carries the full gate/core/referee/funnel CLI outputs + the read-back stamp + the committed sha it was verified against; every number the audit quotes traces to it or to the other committed artifacts (zero hand-computed figures).
- [ ] The champion recording PASSES the validity gate and the hardened referee — the close's one pass-bar; the R-gate, funnel deltas vs baseline 3, and canaries (corpus denominators, samples alongside) are reported as findings.
- [ ] Every committed replay byte-verifies bare on the close HEAD (`bash scripts/verify_samples.sh` + the corpus verification), and provenance is verified end-to-end (stamps, MANIFESTs, sidecar shas).
- [ ] The torch disposition, the co-evolution NO-GO, and the surrogate re-grounding cadence (decisions 3, 4, 7) are re-stated as the permanent close record, and the Phase-16 scoping inputs are handed off explicitly.
- [ ] The STATUS banner reads CLOSED with the end-state, champion identity + sha, and the close-audit filename.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Model the audit on `audits/audit-phase-14-close.md` (verdict-first, per-gate table, findings vs pass
bars kept separate) and reuse the pause's scoring shape verbatim — the close row is the finalist row
re-recorded through the 15.21 CLI on the hardened referee. The one deliberate asymmetry vs 14.12: no
re-record of the canonical sets (branch A), so there are NO byte-coupled test re-pins in this task; if
the close measurement disagrees with the pause's finalist numbers beyond seed noise, that is a FINDING
for the audit, not a reason to re-run until it agrees.

## Integration risk

Two ways this close can lie. First, self-agreement laundering: the close recording uses the same seeds
as the pause's finalist eval, so silently swapping in the pause's cached numbers would be invisible —
the audit must name its own recording timestamp + tag and quote only `results-champion-close.jsonl`.
Second, the pass-bar inversion: the hardened referee landing in 15.19 means the close referee is
STRICTER than the one the finalists were measured under; a champion that passed at the pause may fail
at close, and that outcome pauses for an owner call — it is the exact scenario the referee-before-
selection ordering exists to catch, not a defect in the close.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.crew.options"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.bakeoff.es"`
- `uv run python -c "import training.bakeoff.goodhart"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.determinism"`
- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import eval.funnel"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import eval.watchability"`
- `uv run python -c "import training.surrogate.ballots"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import engine.rng"`
- `uv run python -c "import training.crew.scorer"`
- `uv run python -c "import agents.tactical.learned.forward"`
- `uv run python -c "import agents.tactical.learned.factory"`

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
Open a PR from branch `phase-15-close` with a title like `task 15.23: phase close: gates on the shipped end-state, the close audit, the banner flip (operator-run, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-15-pause.md (the decisions this close verifies + the finalist recipe §3.1 re-run here through the CLI); tasks/phase-14.md 14.12 + audits/audit-phase-14-close.md (the close-audit pattern); audits/review-phase-15-midwave.md Q3 (corpus canary denominators) + Q5 (the provenance-durability convention this record follows)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
