# Agent Prompt — 14.4.1 Make the Featherless adapter's `enable_thinking` kwarg conditional (unblock non-Qwen models)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.4.1 — Make the Featherless adapter's `enable_thinking` kwarg conditional (unblock non-Qwen models), anchored to llm/featherless_client.py (the 14.1 adapter; the request-time `chat_template_kwargs.enable_thinking` field); experiments/lab/report-featherless-sweep.md (14.4 finding: the mandatory field collapses GLM to `{}` and 400/504s Cydonia); experiments/lab/featherless_sweep.py (`_bare_send`, the harness workaround this task makes unnecessary in production). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-adapter-thinking-conditional`
**Depends on:** 14.1, 14.4
**Section refs:** llm/featherless_client.py (the 14.1 adapter; the request-time `chat_template_kwargs.enable_thinking` field); experiments/lab/report-featherless-sweep.md (14.4 finding: the mandatory field collapses GLM to `{}` and 400/504s Cydonia); experiments/lab/featherless_sweep.py (`_bare_send`, the harness workaround this task makes unnecessary in production)
**Complexity:** Medium

The 14.1 adapter ALWAYS sends `chat_template_kwargs.enable_thinking` (the Qwen3 convention). The 14.4 sweep
found this field is honored by the Qwen3 models but BREAKS the non-Qwen slate — `zai-org/GLM-4-32B-0414`
collapses to an empty `{}` response and `TheDrummer/Cydonia-24B-v2` 400/504s — so the sweep had to route them
through a sweep-local BARE send (`featherless_sweep.py:_bare_send`) that omits the field. That workaround lives
ONLY in the probe harness; the PRODUCTION client still cannot call GLM or Cydonia, which blocks locking (14.6)
or recording (14.7) a baseline on any non-Qwen model and blocks authoring/validating their bespoke prompts
(14.5) against the real client. Make the field CONDITIONAL: send `chat_template_kwargs.enable_thinking` only
for models that support the Qwen chat-template kwarg, and omit the whole `chat_template_kwargs` object
otherwise (an empty `{}` is what broke GLM). Gate it on an EXPLICIT per-model capability signal, not by
swallowing the HTTP 400 (AGENTS.md §"No silent fallbacks"); a non-thinking-only model that is asked to think
omits the field and runs non-thinking explicitly, rather than catching an error after the fact.

**Files in scope:**
- llm/featherless_client.py (gate the `chat_template_kwargs.enable_thinking` field on an explicit per-model thinking-capability signal; omit `chat_template_kwargs` entirely when it would be empty; the request-time thinking toggle becomes an explicit no-op for non-supporting models rather than an error)
- tests/llm/test_featherless_client.py (assert a Qwen3-id request INCLUDES `chat_template_kwargs.enable_thinking`; a GLM / Cydonia-id request OMITS it and omits an empty `chat_template_kwargs`; `request_thinking=True` on a non-supporting model omits the field and does not raise; all still route through the shared extract→validate seam)

**Files NOT in scope:**
- llm/provider.py + llm/ollama_client.py + llm/fake_provider.py (`build_default_client` constructs the client unchanged; the conditional is internal to the adapter)
- experiments/lab/featherless_sweep.py + experiments/lab/probe_backends.py (the harness `_bare_send` stays as the sweep's record of the workaround; this task fixes the PRODUCTION path, it does not refactor the probes)
- agents/ + meetings/ + orchestrator/ + replays/ (no call-site or recording change)

**Definition of done:**
- [ ] A Qwen3 model request still INCLUDES `chat_template_kwargs.enable_thinking` (both True and False) — the Qwen3 thinking axis is byte-unchanged and the existing 14.1 tests stay green.
- [ ] A non-Qwen request (`zai-org/GLM-4-32B-0414`, `TheDrummer/Cydonia-24B-v2`) OMITS `chat_template_kwargs.enable_thinking`, and omits `chat_template_kwargs` entirely when it would be empty — verified against the wire payload, so the production client can call GLM / Cydonia where 14.4 needed the bare-send workaround.
- [ ] The thinking-capability signal is EXPLICIT (a per-model capability flag / detection), not a caught-and-swallowed HTTP 400 — no silent fallback; an unrecognized id still fails loud.
- [ ] `request_thinking=True` on a non-supporting model is an explicit documented no-op (the field is omitted; the request runs non-thinking), not an exception.
- [ ] Unit tests inject `send` and assert both wire shapes with no network call.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 14.4 harness already proved the fix shape: `featherless_sweep.py:_bare_send` posts the identical request
MINUS `chat_template_kwargs` and parses through the SAME `_extract_json_block` + `model_validate_json` seam, so
the production change is to make the adapter's payload builder (`_build_chat_payload` / wherever the 14.1
adapter assembles `chat_template_kwargs`) emit the field conditionally on a per-model capability signal. Prefer
an explicit signal over substring magic: a small `enable_thinking`-supported predicate keyed off the model id
family, or a constructor / per-call capability flag the caller can override — so the behavior is testable and
fails loud on an unknown id rather than swallowing the 400. When the model does not support it, drop the whole
`chat_template_kwargs` object. Keep the Qwen3 path byte-identical so the existing 14.1 adapter tests stay green.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Open a PR from branch `phase-14-adapter-thinking-conditional` with a title like `task 14.4.1: make the featherless adapter's `enable_thinking` kwarg conditional (unblock non-qwen models)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing llm/featherless_client.py (the 14.1 adapter; the request-time `chat_template_kwargs.enable_thinking` field); experiments/lab/report-featherless-sweep.md (14.4 finding: the mandatory field collapses GLM to `{}` and 400/504s Cydonia); experiments/lab/featherless_sweep.py (`_bare_send`, the harness workaround this task makes unnecessary in production)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
