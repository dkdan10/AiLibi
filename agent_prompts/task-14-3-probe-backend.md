# Agent Prompt — 14.3 Provider-neutral probe backend (Featherless behind the probe seam)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.3 — Provider-neutral probe backend (Featherless behind the probe seam), anchored to experiments/model_probe/probe.py; experiments/lab/deception_battery.py; experiments/lab/deflection_probe.py; experiments/lab/model_ceiling_probe.py (the `dump` / `grade-frontier` modes). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-probe-backend`
**Depends on:** none
**Section refs:** experiments/model_probe/probe.py; experiments/lab/deception_battery.py; experiments/lab/deflection_probe.py; experiments/lab/model_ceiling_probe.py (the `dump` / `grade-frontier` modes)
**Complexity:** Medium

The real-data probes reconstruct hard contexts from committed `replays/samples/9p2i` and call the model
through one tiny seam that today hits `llm.ollama_client._default_send` then `_extract_json_block` +
`model_validate_json` (`probe.py:_one_call`, `deception_battery.py:_call`, `model_ceiling_probe.py:_call_ollama`).
Add a provider-neutral `call_turn` behind that seam so the identical reconstructed contexts can flow to
Featherless, parameterized by a `--backend`/`--models` flag (default `ollama` preserves CI + the existing
`results-*.jsonl`). The Featherless path is selectable with `thinking_policy="strip"` so reasoning models do
not abort the sweep. No engine/agent/replay bytes change — the probes stay read-only over committed replays.

**Files in scope:**
- experiments/lab/probe_backends.py (new: `Backend` literal, `call_turn(prompt, schema, *, backend, model, ...)` dispatching to the ollama or featherless `_default_send`, both through `_extract_json_block` + validate, returning `(parsed_or_None, raw_text, latency)`)
- experiments/model_probe/probe.py (`--backend` / `--models` plumbed through `_one_call` via `call_turn`; default `ollama`)
- experiments/lab/deception_battery.py (`_call` gains `backend`/`model` via `call_turn`; default unchanged)
- experiments/lab/deflection_probe.py (routes through `deception_battery._call`'s new signature)
- experiments/lab/model_ceiling_probe.py (a `run-featherless` subcommand sharing the existing `grade-frontier`; the `run-ollama` path generalized to `call_turn`)
- tests/experiments/test_probe_backends.py (new: `call_turn` dispatches + parses for an injected send, no network)

**Files NOT in scope:**
- llm/ (the adapter is 14.1; this only consumes its `_default_send`)
- agents/ + meetings/ + orchestrator/ (probes reconstruct, never mutate, the engine)
- replays/samples/ (read-only context reconstruction; no re-record)
- experiments/lab/featherless_sweep.py (the sweep driver is 14.4)

**Definition of done:**
- [ ] `call_turn` routes the SAME reconstructed prompt to either backend through the production `_extract_json_block` + `model_validate_json` path and returns `(parsed_or_None, raw_text, latency)`.
- [ ] All four probes default to `ollama` (CI + existing reports unaffected) and accept `--backend featherless --models <list>`; the ollama branch stays byte-identical so existing `results-*.jsonl` reproduce.
- [ ] The Featherless path is selectable with `thinking_policy=strip` so reasoning models do not abort the sweep; bounded concurrency is opt-in (sequential when latency is the measured metric).
- [ ] No engine/agent/replay-byte mutation; probes stay read-only over committed replays.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The seam is tiny: `probe.py:_one_call`, `deception_battery._call`, and `model_ceiling_probe._call_ollama`
each already call `_default_send` then `_extract_json_block` + `model_validate_json`. Factor that into
`call_turn(prompt, schema, *, backend, model, temperature, max_tokens)` and have each probe pass a `backend`
read from a new CLI flag. Keep the ollama branch's `_default_send` call byte-identical (same
`format=schema.model_json_schema()`, same options) so the committed `results-*.jsonl` reproduce. For
Featherless, build the `response_format` json_schema from `schema` and call `llm.featherless_client._default_send`
with `thinking_policy` threaded. Featherless is a concurrent hosted API, so a bounded `asyncio.Semaphore`
(opt-in, 4–8) can cut sweep wall time — but run a sequential pass whenever per-call latency is the metric.

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
Open a PR from branch `phase-14-probe-backend` with a title like `task 14.3: provider-neutral probe backend (featherless behind the probe seam)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/model_probe/probe.py; experiments/lab/deception_battery.py; experiments/lab/deflection_probe.py; experiments/lab/model_ceiling_probe.py (the `dump` / `grade-frontier` modes)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
