# Agent Prompt — 15.7 Baseline 3: atomic re-record + the Wave-0 close finding (operator-run, $0)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.7 — Baseline 3: atomic re-record + the Wave-0 close finding (operator-run, $0), anchored to tasks/post-phase-14-clean-up.md H7 + §3 (the target sheet); tasks/phase-14.md 14.12 (the atomic re-record + close pattern); audits/audit-phase-14-close.md §1 (the gate this record must pass); scripts/refresh_samples.sh (the recording harness). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-baseline-3`
**Depends on:** 15.1, 15.2, 15.3, 15.4, 15.4.1, 15.5, 15.6
**Section refs:** tasks/post-phase-14-clean-up.md H7 + §3 (the target sheet); tasks/phase-14.md 14.12 (the atomic re-record + close pattern); audits/audit-phase-14-close.md §1 (the gate this record must pass); scripts/refresh_samples.sh (the recording harness)
**Complexity:** Integration

Record **baseline 3** — both canonical sets (50 + 50 seeds) on the unchanged model/provider
(`Qwen/Qwen3-32B`, Featherless, $0) with the Wave-0 substrate: the `qwen3_32b` set at v5 with
`vote_ballot` at v6 (15.4's vent elicitation + 15.5's reporter line; provenance rows render
`*.qwen3_32b.v5` for the three 15.4-owned templates and `vote_ballot.qwen3_32b.v6` — 15.5's
per-template bump) and the
`reporter_exculpation` lever ON — one atomic PR replacing `replays/samples/`, exactly the 14.12
pattern. Graduate the lever at the record — BOTH halves of the 14.9/14.12 move: the resolver itself
(`agents/memory/beliefs.py::reporter_exculpation_enabled`, 15.5's home) returns constant `True`, and
the registry entry moves `_TOGGLEABLE_LEVER_RESOLVERS` → `_RETIRED_ALWAYS_ON_LEVERS` in
`orchestrator/replay.py` — so the belief damp and the vote-surface annotation are UNCONDITIONAL under a
bare environment and the committed sets reconstruct BARE with no env export (this also discharges the
C6 recording-preflight hazard: no lever env for an operator to forget, and no gap between the stamped
flags and the code's bare behavior). Close the wave with
`audits/audit-phase-15-wave0-close.md`: the full validity gate, the R-gate measurement, and — the
wave's own instrument — the 15.3 funnel table re-measured against the charter's baseline-2 column
(vent transmission 36/74 → ?, structured vent observations 0 → ?, innocent-reporter ejections 22 → ?,
votes-outside-the-set 37/68 → ?), with the Phase-14 canaries (genuine-class conversion, R1) reported
alongside. Directions are findings, not pass bars; a regression on a canary is the one result that
pauses the phase for an owner call. Finally, pin the baseline-3 evidence-supply floor values into the
15.2 per-baseline constants block.

**Files in scope:**
- replays/samples/9p2i/ (the baseline-3 set: replays + MANIFEST + tournament-eval-report + rubric artifacts)
- replays/samples/4p1i/ (the baseline-3 set)
- agents/memory/beliefs.py (reporter-exculpation resolver graduation region — constant True; behind the 15.5 dependency edge)
- orchestrator/replay.py (lever graduation region — registry entry to retired-always-on; disjoint from 15.9's stamp region)
- eval/watchability.py (baseline-3 floor values in the per-baseline constants block region)
- audits/audit-phase-15-wave0-close.md (new: the close finding)
- audits/baseline2-final-measure.json (new: the committed BEFORE column — `measure_baseline.py --json` incl. `--watchability --funnel` captured on the baseline-2 bytes immediately before replacement)
- README.md (sample-provenance paragraph region — refresh recorded date / prompt set / measured win rates to baseline 3)
- tests/orchestrator/test_replay.py (graduation re-pins)
- tests/meetings/test_manager.py (byte-coupled re-pins to the new recorded bytes, where tests pin recorded rows)
- tests/scripts/test_manifest_writer.py (byte-coupled v4-row re-pins to the new recorded bytes)
- tests/api/test_eval.py (byte-coupled committed-report re-pins)

**Files NOT in scope:**
- scripts/refresh_samples.sh (drives the record as-is; graduation-at-record makes a lever export unnecessary)
- meetings/ + agents/ outside the named resolver-graduation region (all behavioral substrate changes landed in 15.4–15.6; this task graduates, records, and measures — no new behavior)
- replays/ml_corpus/ (that is 15.12's artifact, recorded against THIS baseline)

**Definition of done:**
- [ ] Both sets recorded at the Wave-0 config and committed in one atomic PR; `scripts/validity_gate.py`
  PASSES both sets from committed bytes; `bash scripts/verify_samples.sh` reconstructs all 100 samples
  clean under a BARE environment (lever graduated, no `AILIBI_*` export).
- [ ] MANIFEST provenance exact per seed: model, the mixed Wave-0 prompt versions (three templates at
  `qwen3_32b.v5`, `vote_ballot` at `qwen3_32b.v6` — 15.5's per-template bump), all six flags (five
  retired + the graduated reporter lever), git_sha, $0 cost, winner.
- [ ] The wave0-close audit reports the funnel before/after table (15.3's instrument on baseline 2 vs
  baseline 3), the R-gate measurement, and the canaries — every number regenerated by the committed
  CLIs, zero hand-computed figures. The BEFORE column regenerates from the committed
  `audits/baseline2-final-measure.json` (captured pre-replacement and named in the audit with the tip
  commit it was measured at — the baseline-2 bytes themselves survive only in git history).
- [ ] README's sample-provenance paragraph reflects baseline 3 (recorded date, the v5 prompt set with
  `vote_ballot` at v6, the measured impostor win rates) — the public quickstart never describes replaced samples.
- [ ] Every byte-coupled test that pins recorded rows or committed-report aggregates is re-pinned in
  this PR (`tests/scripts/test_manifest_writer.py`, `tests/api/test_eval.py`,
  `tests/meetings/test_manager.py`, `tests/orchestrator/test_replay.py` — plus a sweep for any other
  pin the replacement breaks); `bash scripts/check.sh` green on the final tree is the proof.
- [ ] Genuine-class conversion and R1 are reported against their baseline-2 anchors; a canary regression
  is flagged as the phase's NO-GO for an owner decision, not absorbed silently.
- [ ] The baseline-3 evidence-supply floors are pinned in `eval/watchability.py`'s per-baseline block
  with measured values in comments; `measure_baseline.py --watchability` runs clean against the new sets.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Follow 14.12's runbook: 2 parallel Featherless seed workers saturate the plan (~4h for both sets),
per-seed crash-retry, atomic staging, MANIFEST + report + rubric regeneration via the existing
refresh/build tooling. Graduation-at-record keeps the recorded stamp and the resolver's constant True
byte-consistent (the 14.12 §6 precedent explains why the committed set then serves bare). The operator
may run 15.12's corpus recording in the same session immediately after — same config, same workers —
but the artifacts land in separate PRs (canonical baseline vs training corpus provenance).

## Integration risk

This is a substrate re-record: every byte-coupled test that pins recorded rows must be re-pinned to the
new bytes deliberately (the 14.12 experience), and the one real NO-GO is a validity failure or a canary
regression — pause, don't paper. Prompt uptake risk is real and acceptable: v5's vent elicitation may
land below hopes (the model may under-report); that outcome is a FINDING that scopes Phase 16, not a
reason to iterate prompts inside this task (record-only discipline).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import eval.funnel"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import eval.watchability"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

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
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-15-baseline-3` with a title like `task 15.7: baseline 3: atomic re-record + the wave-0 close finding (operator-run, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/post-phase-14-clean-up.md H7 + §3 (the target sheet); tasks/phase-14.md 14.12 (the atomic re-record + close pattern); audits/audit-phase-14-close.md §1 (the gate this record must pass); scripts/refresh_samples.sh (the recording harness)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
