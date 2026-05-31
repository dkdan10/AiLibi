# Agent Prompt — 7.5 Ollama provider client + wiring

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.5 — Ollama provider client + wiring, anchored to tasks/phase-7-plan.md "Provider / eval-infra track", Q2 (now superseded — provider = local Ollama); the Phase 7 Ollama-enablement plan (model = `qwen2.5:7b-instruct`); DESIGN.md §5, §7 (LLM client contract). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-ollama-provider-client`
**Depends on:** none
**Section refs:** tasks/phase-7-plan.md "Provider / eval-infra track", Q2 (now superseded — provider = local Ollama); the Phase 7 Ollama-enablement plan (model = `qwen2.5:7b-instruct`); DESIGN.md §5, §7 (LLM client contract)
**Complexity:** Integration

Phase 7's eval-set task (7.8) must run a high volume of 7-player meeting calls, and
the diagnosis showed that doing this on a hosted frontier model is both expensive
(~$150+ over the phase) and brittle (real-model meeting reports crash the strict
discriminated-union schemas). The decision is to make the canonical
agent-intelligence provider a **local Ollama** open model — `qwen2.5:7b-instruct`,
free, self-hosted on the owner's Mac — keeping the existing Anthropic path as a
still-supported alternative and the frozen 4p/1i baseline (replays are
model-agnostic) intact. This task adds the provider client and wires it into the
default-client selection so the rest of the substrate (7.6 parse-tolerance, 7.7
provider-agnostic refresh, 7.8 eval set) can target it.

Add a new `llm/ollama_client.py` implementing the `LLMClient` Protocol
(`llm/client.py:157`) — `async def complete(*, prompt, schema, max_tokens,
temperature, call_kind, model, agent_id) -> LLMResponse` — mirroring the shape of
`AnthropicClient` (`llm/provider.py:127`) and `FakeProvider` (`llm/fake_provider.py`).
The client POSTs to the local Ollama server at `AILIBI_OLLAMA_HOST` (default
`localhost:11434`), passing **`format` = `schema.model_json_schema()`** for
constrained (schema-shaped) decoding when a schema is supplied, and an `options`
block carrying `temperature` plus a `seed` for reproducible generation. The Ollama
`options.seed` is derived from the per-GAME seed (so different games don't collide
and a game is reproducible-ish), NOT a single constant or a per-call hash. Map
Ollama's `prompt_eval_count` / `eval_count` response counters onto `TokenUsage`, and
set **`cost_usd = 0.0`** (a local model is free). REUSE the shared helpers from
`llm/provider.py` rather than re-implementing them: `_extract_json_block`
(`llm/provider.py:335`) to pull the JSON out of the raw model text, the existing
`_compute_cost_usd` cost path (with a `$0` Ollama entry / a rate of 0), and the
`LLMCallFailure` / parse-failure-attachment behavior (`llm/provider.py:62,278`) so a
malformed local output becomes a recoverable FailedCall, never a hard crash. The `$0`
rate is keyed by PROVIDER (ollama → `cost_usd` 0 regardless of model), with an
optional per-model override — NOT keyed by model name, so swapping
`qwen2.5:7b`→`llama3.1:8b` for an A/B does not silently fall back to a non-zero rate.

Wire it into `build_default_client` (`llm/provider.py:214`): add a
`PROVIDER_OLLAMA = "ollama"` constant and an env branch that constructs the
`OllamaClient`, reusing the `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL`
model knobs (with an Ollama-appropriate default of `qwen2.5:7b-instruct` for both).
The existing Anthropic branch STAYS in `build_default_client` (it is not dead code):
it is retained for (a) re-recording the frozen 4p/1i baseline if it is ever
deliberately rotated, and (b) optional cross-provider validation — so a future
reader does not delete it.
**Budget nuance (critical, do not skip):** `BudgetedLLMClient` pre-flight estimates
cost from `_DEFAULT_COST_PER_INPUT_TOKEN_USD` / `_DEFAULT_COST_PER_OUTPUT_TOKEN_USD`
(`llm/budgeted_client.py:69`), and `GameBudget` caps USD **and** tokens
(`llm/budget.py:96`). For Ollama the USD dimension must never block a free run: set
the pre-flight estimation rates to **0** for the Ollama client (and/or treat
`max_cost_usd` as effectively infinite for this provider), while KEEPING the token
caps intact (a local model can ramble — the token ceiling is the real backstop,
parametrized in 7.7). Do this in a way that leaves the Anthropic budget behavior
exactly as-is.

Add the `ollama` package (the official Python client) to `pyproject.toml` and refresh
`uv.lock` (only `anthropic==0.104.1` is present today). Add the operator config and
docs: `.env.example` gains `AILIBI_LLM_PROVIDER=ollama`, `AILIBI_OLLAMA_HOST`, and
the model knobs defaulting to `qwen2.5:7b-instruct`; `README.md` gains the local-setup
steps (install Ollama → `ollama pull qwen2.5:7b-instruct` → `ollama serve`); and
`AGENTS.md` gets a short note that Ollama is a supported provider and CI never hits
it. (The DESIGN.md §7 provider note is design-thread-owned and is NOT in this
contract's scope.)

Tests: `tests/llm/test_ollama_client.py` unit-tests the client by MOCKING the HTTP
call (assert the request carries `format = schema.model_json_schema()` and the
seed/temperature options; assert token mapping and `cost_usd == 0.0`; assert a
malformed body surfaces as a FailedCall, not an exception). Add an **opt-in,
server-gated** integration marker mirroring the existing `real_provider` gate
(`tests/llm/test_client.py:790`) — e.g. skip unless `AILIBI_RUN_OLLAMA_TESTS=1` and a
reachable server — so CI (which has no Ollama server) always skips it and never hits
the network.

Determinism note: the recording/replay layer captures the client's outputs, so a
recorded Ollama game replays byte-identically without the server; the `seed`
only matters for fresh generation, not replay. Fresh generation may drift across
Ollama/runtime versions; byte-identical determinism is guaranteed only via the
replay-record path (recorded outputs replay exactly), NOT via re-running a seed
fresh. This task does NOT generate or commit any sample data (that is 7.8) and does
NOT change the `LLMClient` Protocol itself — it implements it.

**Files in scope:**
- llm/ollama_client.py
- llm/provider.py
- llm/budgeted_client.py
- llm/budget.py
- pyproject.toml
- uv.lock
- .env.example
- README.md
- AGENTS.md
- tests/llm/test_ollama_client.py

**Files NOT in scope:**
- llm/client.py (the `LLMClient` Protocol is implemented, not changed)
- llm/fake_provider.py (the fake provider is the CI default and is untouched; mirror its shape, do not edit it)
- llm/cache.py (the response cache is provider-agnostic; no change needed)
- scripts/refresh_samples.sh, eval/balance_eval.py (provider-agnostic refresh + per-game budget knob are Task 7.7)
- replays/samples/ (no sample generation here; that is Task 7.8)
- DESIGN.md (the §7 provider note is design-thread-owned)
- frontend/ (no frontend surface for the provider choice)

**Definition of done:**
- [ ] `llm/ollama_client.py` defines `OllamaClient` implementing the `LLMClient` Protocol's `async def complete(...) -> LLMResponse`; it POSTs to `AILIBI_OLLAMA_HOST` (default `localhost:11434`), passes `format = schema.model_json_schema()` for constrained decoding when a schema is given, and sets `options` with `temperature` + a `seed` derived from the per-game seed (not a constant or per-call hash).
- [ ] Token usage is mapped from Ollama's `prompt_eval_count` / `eval_count` onto `TokenUsage`, and `cost_usd == 0.0` for every Ollama response (a `$0` entry on the cost path / a rate of 0).
- [ ] The client REUSES `_extract_json_block`, the `_compute_cost_usd` path, and the `LLMCallFailure` / parse-failure-attachment behavior from `llm/provider.py` so a malformed local output is a recoverable FailedCall, not a crash (covered by a test).
- [ ] `build_default_client` (`llm/provider.py:214`) gains `PROVIDER_OLLAMA = "ollama"` and an env branch that constructs `OllamaClient`, reusing `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL` with an Ollama default of `qwen2.5:7b-instruct`; the existing `fake` and `anthropic` branches are unchanged.
- [ ] The USD budget dimension is disabled for Ollama (pre-flight estimation rates → 0 and/or `max_cost_usd` effectively infinite for this provider) while the **token** caps stay intact; the Anthropic budget behavior is unchanged. Covered by a test asserting an Ollama pre-flight does not trip the USD ceiling.
- [ ] `ollama` is added to `pyproject.toml` and `uv.lock` is refreshed; `.env.example`, `README.md`, and `AGENTS.md` document the Ollama provider, host, and model knobs defaulting to `qwen2.5:7b-instruct`.
- [ ] `tests/llm/test_ollama_client.py` unit-tests the client with the HTTP call mocked (request shape incl. `format`/seed/temperature, token mapping, `cost_usd == 0.0`, malformed-body → FailedCall), plus an opt-in server-gated marker (e.g. `AILIBI_RUN_OLLAMA_TESTS=1` + reachable server) that CI skips — mirroring the `real_provider` gate.
- [ ] The `LLMClient` Protocol (`llm/client.py`) and `llm/fake_provider.py` are unchanged; CI never hits the network (the server-gated test is skipped without the env flag).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `llm/provider.py` end to end first — `AnthropicClient.complete` (line 127), the
shared `_extract_json_block` (line 335), the `_compute_cost_usd` path, the
`_attach_parse_failure` / `LLMCallFailure` behavior (lines 62, 278), and
`build_default_client` (line 214) — and model `OllamaClient.complete` on the
Anthropic one, swapping the transport for an Ollama `/api/generate` (or `/api/chat`)
POST with `format=schema.model_json_schema()`, `stream=False`, and
`options={"temperature": temperature, "seed": <derived-from-per-game-seed>}`. The official `ollama`
Python client returns a dict carrying `response` (the text), `prompt_eval_count`,
and `eval_count`; pull the JSON out of `response` with the SAME `_extract_json_block`
+ `schema.model_validate_json` path the Anthropic client uses, so 7.6's normalization
(applied in that shared path) automatically covers Ollama too. For the budget knob,
look at how `BudgetedLLMClient` is constructed around the provider client and pass
zeroed cost-estimation rates for the Ollama branch (the constructor already accepts
explicit rates — see the `_DEFAULT_COST_PER_*` comment at `llm/budgeted_client.py:69`),
leaving `GameBudget`'s token caps untouched. For the server-gated test, copy the
`real_provider` skip idiom at `tests/llm/test_client.py:790` (an env-flag +
reachability guard) so the integration case is opt-in. Add `ollama` with
`uv add ollama` so `pyproject.toml` + `uv.lock` move together; pin `ollama` to an
exact version in `pyproject.toml` (matching the repo's exact-pin convention, e.g.
`anthropic==0.104.1`), since `ollama` is pre-1.0 and its API can shift across minor
versions. Keep the Anthropic path byte-identical — only ADD the Ollama branch and
the zeroed-rate wiring.

## Public types this task introduces
- `llm.ollama_client.OllamaClient`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This task adds a second real provider behind the audited `LLMClient` boundary and
touches the budget pre-flight, so the risks are (a) the network: CI must never reach
Ollama, mitigated by the opt-in `AILIBI_RUN_OLLAMA_TESTS` server gate and the unit
tests using a mocked transport; (b) the budget pre-flight: zeroing the USD dimension
must NOT also disable the token caps (a local model can ramble unbounded), so the
token ceiling stays and only the dollar estimate goes to 0, and the Anthropic budget
path must be provably unchanged; (c) determinism: the client must not perturb the
record/replay contract — outputs are captured and replayed model-agnostically, and
the fixed `seed` only affects fresh generation; (d) malformed local output: a weak
local model can emit schema-invalid JSON, so the FailedCall path (not an exception)
must be exercised by a unit test here, with the deeper normalization landing in 7.6.

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
Open a PR from branch `phase-7-ollama-provider-client` with a title like `task 7.5: ollama provider client + wiring`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-7-plan.md "Provider / eval-infra track", Q2 (now superseded — provider = local Ollama); the Phase 7 Ollama-enablement plan (model = `qwen2.5:7b-instruct`); DESIGN.md §5, §7 (LLM client contract)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
