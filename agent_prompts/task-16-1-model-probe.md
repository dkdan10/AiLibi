# Agent Prompt — 16.1 Qwen3.6-27b sweep probe: the new Qwen generation on the committed contexts

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.1 — Qwen3.6-27b sweep probe: the new Qwen generation on the committed contexts, anchored to experiments/lab/featherless_sweep.py (SLATE :247-275, ModelSpec :226-243, preflight :904-957, corpora/detectors :1-96); agent_prompts/task-14-4-model-sweep.md (the precedent probe); llm/featherless_client.py:18-32 (the response_format_mode posture the probe must re-verify); audits/audit-phase-16-model-lock.md (the 16.2 consumer). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-model-probe`
**Depends on:** none
**Section refs:** experiments/lab/featherless_sweep.py (SLATE :247-275, ModelSpec :226-243, preflight :904-957, corpora/detectors :1-96); agent_prompts/task-14-4-model-sweep.md (the precedent probe); llm/featherless_client.py:18-32 (the response_format_mode posture the probe must re-verify); audits/audit-phase-16-model-lock.md (the 16.2 consumer)
**Complexity:** Medium

Evaluate the newer Qwen generation before any production change: add Qwen3.6-27b to the committed
sweep harness's `SLATE` as a candidate `ModelSpec` (probing BOTH thinking-axis settings and the
transport `qwen_kwarg`, exactly how the Phase-14 slate rows are declared) and operator-run the
sweep over the SAME reconstructed 9p2i contexts as the incumbent — model is the only moving
variable. The probe must establish, with committed evidence: (a) the exact served model id on the
flat-rate plan (the generation preflight 404s an unserved id — an unserved model is a NO-GO
finding, not an error); (b) parse success on both call kinds under `json_object`, and whether the
newer generation supports strict `json_schema` (the incumbent deterministically 400s on it — a
newer model may not; re-verify, do not assume); (c) the thinking-kwarg behavior the 16.12
`_THINKING_KWARG_BY_MODEL` entry will encode; (d) grade rows on the four corpora (opening
fabrication, reply/cover 2×2, vote parse + conversion, latency) beside a re-run incumbent row so
the comparison is same-day, not archival. This task is EXPERIMENT-TIER only: no `llm/` production
edit, no constant change — the fail-loud registry entry is 16.12's, post-lock.

**Files in scope:**
- experiments/lab/featherless_sweep.py (SLATE + any new-generation transport handling the probe needs)
- experiments/lab/results-featherless-sweep-qwen3-6-27b.jsonl (new: the committed sweep rows)
- experiments/lab/report-featherless-sweep-qwen3-6-27b.md (new: the graded comparison + the served-id/response-format/thinking findings)
- tests/experiments/test_probe_backends.py (slate-entry pins region — the new ModelSpec is well-formed; no network)

**Files NOT in scope:**
- llm/ (production client untouched — the registry entry and default swap are 16.12's, behind the lock)
- agents/strategic/prompts/ (no set work before the lock; the probe runs the new model against the EXISTING qwen3_32b set, which is itself a finding — a bespoke set is 16.13's)
- scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (recording surfaces untouched)

**Definition of done:**
- [ ] The new `ModelSpec` rides the existing harness unmodified in shape: pinned corpus ids re-rendered per cell, model-outer loop, switch pacing, generation preflight — a served-id failure produces a documented NO-GO row, never a crash.
- [ ] The committed JSONL carries, for the new model AND a same-day incumbent re-run: parse_ok rates per call kind, thinking-axis behavior, response_format verdict (`json_object` and `json_schema` both probed), token counts, latency, and the four corpora's grade booleans.
- [ ] The report ends in a RECOMMENDATION-SHAPED summary (the ranked-not-self-declared discipline): the head-to-head table, the served id, and the open risks — it recommends; 16.2 decides.
- [ ] Every reported number regenerates from the committed JSONL; the report names the exact reproduce command.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone a candidate row's shape from the existing `SLATE` (:247-275) — `served_id`, `label`,
`thinking_axis`, `qwen_kwarg`, `role="candidate"` — and let the harness do the rest; the pinned
corpus-id mechanism (`_pin_ids` :969-992) guarantees the new model sees byte-identical contexts.
The served id for a new release is a guess until the preflight confirms it: try the obvious
Featherless namespace forms (`Qwen/Qwen3.6-27B` and variants) and record what the API actually
serves — the preflight probe (:904-957) is the arbiter, and "not served on the plan" is a
first-class NO-GO outcome for 16.2, not a task failure. Operator gate: `FEATHERLESS_API_KEY`,
hours-scale, $0 flat-rate.

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
Open a PR from branch `phase-16-model-probe` with a title like `task 16.1: qwen3.6-27b sweep probe: the new qwen generation on the committed contexts`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/featherless_sweep.py (SLATE :247-275, ModelSpec :226-243, preflight :904-957, corpora/detectors :1-96); agent_prompts/task-14-4-model-sweep.md (the precedent probe); llm/featherless_client.py:18-32 (the response_format_mode posture the probe must re-verify); audits/audit-phase-16-model-lock.md (the 16.2 consumer)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
