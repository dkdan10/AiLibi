# Agent Prompt — 14.1 FeatherlessClient adapter (OpenAI-compatible, $0, thinking policy)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.1 — FeatherlessClient adapter (OpenAI-compatible, $0, thinking policy), anchored to DESIGN.md §7, §10.4 (provider adapters, structured output); llm/client.py (the OpenAI adapter sketch in the module docstring); llm/ollama_client.py (the structural template); owner decision 2026-06-25 (Featherless AI Premium). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-featherless-client`
**Depends on:** none
**Section refs:** DESIGN.md §7, §10.4 (provider adapters, structured output); llm/client.py (the OpenAI adapter sketch in the module docstring); llm/ollama_client.py (the structural template); owner decision 2026-06-25 (Featherless AI Premium)
**Complexity:** Integration

Add a `FeatherlessClient` provider adapter behind the `llm.client.LLMClient` Protocol, structurally cloned
from `llm/ollama_client.py` (the closer template: it already solved lazy-import, injectable `send`,
$0-by-provider cost, fail-loud thinking, and the `_raw_from_*` test split). `complete()` builds an
OpenAI-compatible chat-completions request with `response_format={"type":"json_schema","json_schema":
{"name": schema.__name__, "schema": schema.model_json_schema(), "strict": True}}` (the analogue of Ollama's
`format=schema.model_json_schema()`), then routes the response through the SAME shared
`llm.provider._extract_json_block` → `schema.model_validate_json` → `_attach_parse_failure(LLMCallFailure)`
seam so Task 7.6 normalization and failed-call recording are inherited unchanged. Transport is a thin lazy
`httpx` POST (do NOT add the `openai` SDK — Ollama deliberately avoided it). Cost is $0 keyed by provider so
an A/B model swap can never fall back to a frontier rate. A `thinking_policy` knob (`fail_loud` default /
`strip`) handles reasoning models: `fail_loud` raises on a populated reasoning channel (parity with the
Ollama doctrine), `strip` discards it explicitly (logged, never silent) so the 14.4 sweep can evaluate
reasoning models. Because the shared `_extract_json_block` deliberately strips a prose preamble and returns
the first valid JSON object, `fail_loud` runs a RAW-CONTENT reasoning guard BEFORE extraction (inspecting the
`reasoning_content` channel and the raw `content` for reasoning markers / leading prose) — otherwise a
`reasoning\n{JSON}` response would be silently accepted. Separately, a REQUEST-time thinking toggle (mirroring
Ollama's top-level `think=` field) tells the model whether to reason at all, so 14.4 can drive the
non-thinking/thinking sweep axis — distinct from the response-side `thinking_policy`.

**Live finding + ratification (implemented in PR #202, 2026-06-27):** the strict `json_schema`
`response_format` above is REJECTED with a deterministic HTTP 400 by every Phase-14 slate model (Featherless
does not implement guided `json_schema` decoding). The adapter therefore exposes a `response_format_mode`
knob defaulting to **`json_object`** (syntactic-JSON; structured-output correctness comes from the shared
extract→validate→FailedCall seam + prompt engineering, exactly as the Anthropic adapter — which sends no
`response_format` — has always worked), with `json_schema` kept SELECTABLE (for a future endpoint and for
14.4 to A/B) and NO silent fallback between modes (a rejected `json_schema` request fails loud). This
deviation from the contract's strict-`json_schema` shape is ratified here and carried into 14.6's locked
tuple. The contract's own Integration risk anticipated it ("structured-output fidelity … is model-specific
and is what 14.4 measures").

**Files in scope:**
- llm/featherless_client.py (new: `FeatherlessClient`, `FeatherlessRawResponse`, `FeatherlessSendHook`, `_default_send`, `_raw_from_response_body`, module defaults, the thinking policy)
- llm/provider.py (`PROVIDER_FEATHERLESS`, `ENV_FEATHERLESS_API_KEY`, `ENV_FEATHERLESS_BASE_URL`, the zero pricing table, the `_compute_cost_usd` provider branch, the `build_default_client` branch, the trailing error message, `__all__`)
- .env.example (a Featherless provider block paralleling the Ollama block; provider list + model-default comment)
- tests/llm/test_featherless_client.py (new: injected-send unit tests — request shape, response_format json_schema translation, $0 cost, thinking fail-loud + strip, parse-failure carrier, model-constant pins)
- tests/llm/test_real_provider.py (new `@real_provider`-gated Featherless round-trips, skipped in CI)

**Files NOT in scope:**
- llm/ollama_client.py + llm/fake_provider.py (untouched; the shared helpers they import are extended additively in provider.py)
- agents/ + meetings/ + orchestrator/ (no call-site change; provider selection is construction-time only)
- replays/samples/ (no re-record here)
- meetings/manager.py (token caps frozen elsewhere; not touched here)

**Definition of done:**
- [ ] `FeatherlessClient` implements the `LLMClient` Protocol; `complete()` builds the `response_format` json_schema request from `schema.model_json_schema()` and routes the response through the SHARED `_extract_json_block` + `model_validate_json` + `_attach_parse_failure` seam.
- [ ] Cost is $0 for every Featherless model (provider-keyed zero table; an A/B model swap cannot fall back to a frontier rate); `preflight_cost_per_input_token_usd == preflight_cost_per_output_token_usd == 0.0`.
- [ ] Response-side thinking policy: `fail_loud` (default) raises a descriptive error on a populated reasoning channel — INCLUDING inline reasoning in `content` — via a raw-content guard that runs BEFORE `_extract_json_block` (the shared extractor strips a prose preamble and would otherwise silently accept `reasoning\n{JSON}`); `strip` discards reasoning explicitly. No silent strip. Tests assert `reasoning\n{valid JSON}` under `fail_loud` RAISES and under `strip` returns the JSON.
- [ ] Request-time thinking toggle: a first-class knob (mirroring Ollama's top-level `think=`) requests thinking ON or OFF, distinct from the response-side `thinking_policy`, so 14.4's non-thinking/thinking sweep axis is real and not degenerate; the exact wire field (e.g. `chat_template_kwargs` / `reasoning_effort`) is resolved per model at implementation time.
- [ ] `build_default_client` selects Featherless on `AILIBI_LLM_PROVIDER=featherless`, fails loud without `FEATHERLESS_API_KEY`, and reuses `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL`; `.env.example` documents the provider.
- [ ] `httpx` is imported lazily inside `_default_send`; CI / fake-provider runs never import it; unit tests inject `send` and make no network call; `_raw_from_response_body` fails loud on missing `usage` / empty `choices`.
- [ ] `@real_provider` Featherless tests are skipped in CI (env-gated on `AILIBI_RUN_REAL_PROVIDER_TESTS=1`) and documented as operator-verified.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone `llm/ollama_client.py` as the structural template, not `provider.py`: it already imports the private
helpers from `llm.provider` (`ollama_client.py:52-60` — `_extract_json_block`, `_compute_cost_usd`,
`LLMCallFailure`, `_attach_parse_failure`, `_RAW_RESPONSE_CHARS`, `_ERROR_MESSAGE_CHARS`, `PROVIDER_*`) and
mirrors the up-front-cost / try-except-ValidationError / `_attach_parse_failure` block at
`ollama_client.py:236-258` — copy that block byte-for-byte. The `response_format` json_schema `name` is
`schema.__name__`. `_model_for(call_kind)` mirrors `OllamaClient._model_for` including the unreachable
`raise ValueError`. `_default_send` posts to `{base_url}/chat/completions` with
`Authorization: Bearer {api_key}`, maps `usage.prompt_tokens` / `completion_tokens`, `body["model"]`, and the
reasoning side-channel `choices[0].message.reasoning_content` (`"" `when absent) into a frozen
`FeatherlessRawResponse`; split the body→model mapping into `_raw_from_response_body` for testability (like
`ollama_client.py:324 _raw_from_generate_response`). Fail loud on empty content (mirror Anthropic's "no text
blocks" `RuntimeError`). Add `_FEATHERLESS_PRICING_USD_PER_MTOK = {}` +
`_FEATHERLESS_FALLBACK_PRICING_USD_PER_MTOK = (0.0, 0.0)` and a `provider == PROVIDER_FEATHERLESS` branch in
`_compute_cost_usd` (`provider.py:597`). The `fail_loud` raw-content guard must run BEFORE
`_extract_json_block` (`provider.py:474-526`), which strips a prose preamble and returns the first valid JSON
— so a post-extraction check cannot catch `reasoning\n{JSON}`. The request-time thinking toggle mirrors
`ollama_client.py:205`'s top-level `think=`; its wire field (`chat_template_kwargs` / `reasoning_effort` / a
`/no_think` token) and `max_tokens` vs `max_completion_tokens` are resolved against the endpoint docs per
model at implementation time.

## Public types this task introduces
- `llm.featherless_client.FeatherlessClient`
- `llm.featherless_client.FeatherlessRawResponse`
- `llm.featherless_client.FeatherlessSendHook`
- `llm.provider.PROVIDER_FEATHERLESS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is the provider seam every downstream task rides. Structured-output fidelity (does `response_format`
actually constrain decoding per model, or does the model emit prose-wrapped JSON the `_extract_json_block`
seam must rescue?) is model-specific and is what 14.4 measures — but the adapter must be correct on a clean
OpenAI-shaped response first. The `fail_loud` thinking default must NOT abort the 14.4 sweep of reasoning
models — the harness selects `strip`; the recorded baseline (14.7) selects `fail_loud` unless the owner signs
off on `strip` at 14.6. Getting the `usage` / `choices` fail-loud mapping right protects the per-game token
budget that is now the only real backstop ($0 cost zeroes the `BudgetedLLMClient` USD dimension). The
`fail_loud` reasoning guard MUST run before `_extract_json_block` (which strips prose preambles), or
`fail_loud` silently degrades to `strip` — a no-silent-fallbacks violation. Changes to
`provider.py` shared constants / `__all__` / `_compute_cost_usd` are additive-only; the existing
Anthropic/Ollama tests must stay green.

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
Open a PR from branch `phase-14-featherless-client` with a title like `task 14.1: featherlessclient adapter (openai-compatible, $0, thinking policy)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, §10.4 (provider adapters, structured output); llm/client.py (the OpenAI adapter sketch in the module docstring); llm/ollama_client.py (the structural template); owner decision 2026-06-25 (Featherless AI Premium)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
