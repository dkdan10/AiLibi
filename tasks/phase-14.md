# Phase 14 — Integrate Featherless AI: provider + model/prompt migration

Goal: migrate the canonical agent-intelligence provider from local Ollama `qwen3.5:9b` to a hosted
**Featherless AI** model. The 9B's 50-seed tournament takes ~13h and Phase 13 closed concluding
"mechanism built, the 9B can't drive it" (R1 = 3/50 games decided by ejection, eject-rate 9%, 177/195
meetings SKIP — `audits/audit-2026-06-25-0859-phase-13-close.md`). This phase integrates Featherless as a
provider, EVALUATES several Featherless models + redesigned prompts against REAL reconstructed simulation
data before committing, then **records a new full-sim baseline on the chosen model** as the deliverable.

Why a new baseline is the success criterion (owner decision 2026-06-25): the Phase-13 audit found the
binding constraint is INFORMATION (single-room vision → ~45% detector precision), so a well-calibrated
stronger model may *correctly still SKIP*. The phase therefore does NOT gate on "R1 went up" — it gates on
a VALID new baseline existing. The Phase-13 R-gate (R1/R4/R7/impostor/geomean) is computed and recorded as
a measurement on that baseline (the headline finding that scopes Phase 15), never a pass/fail gate the
re-record must beat. Structural information levers (vents/sabotage/wider vision) are explicitly deferred to
Phase 15.

Locked decisions (2026-06-25):
- **Provider:** Featherless AI (flat-rate, OpenAI-compatible, $25/mo Premium, any model size, 32K context).
  Cost recorded as $0 keyed by provider (the Ollama doctrine); token caps (turn 2048 / vote 1024) stay the
  real backstop. Hosted models do not byte-reproduce FRESH generation; recordings still replay
  byte-identically (the loosened contract Ollama already carries).
- **Prompts:** the four existing templates are PINNED as the frozen `qwen3.5:9b` reference set; NEW,
  independent prompt sets are authored per new model (simple game instructions + role + memory → deduction +
  interesting sim). A small per-model prompt-folder restructure selects the right set for the right model.
  New-model prompts are compared against the 9B results but are not a single-variable ablation — model +
  prompt are co-designed, by choice.
- **Model slate:** sweep Qwen3-32B (instruct), Qwen3-30B-A3B (MoE), GLM-4-32B, and one RP/creative
  fine-tune. Thinking models are on the table now that inference is on the cloud (the local `think=False`
  structured-output breakage — `experiments/lab/report-model-ceiling-probe.md` Finding 2 — does not apply to
  a hosted endpoint that returns reasoning in a separate channel); thinking-mode is a sweep AXIS.
- **Two-set structure** (4p1i flat + 9p2i canonical with its roster sidecar) is unchanged.

Parallelism: 14.1, 14.2, 14.3 are independent roots and dispatch in parallel (disjoint file scopes):
`(14.1 ∥ 14.2 ∥ 14.3) → 14.4 → 14.5 → 14.6 → 14.7 → 14.8`. 14.4 needs 14.1 + 14.3; 14.5 needs 14.2 + 14.4.
Operator-run / spend gates: 14.4 (model sweep, $0 marginal) and 14.7 (re-record, the time gate).
Design-thread (no agent dispatch): 14.6 (lock decision) and 14.8 (close). Track with
`python3 scripts/compute_next_task.py --phase 14`.

Merge Criteria (end-of-phase): the phase's success criterion is a new full-sim baseline recorded on the new
model. Concretely Phase 14 merges when (1) `FeatherlessClient` is a Protocol-conformant provider selectable
via `AILIBI_LLM_PROVIDER=featherless` with $0 provider-keyed cost, the thinking policy, and the shared
parse/normalize/failed-call seam, green under `bash scripts/check.sh`; (2) the per-model prompt-set structure
is in place with the 9B set pinned byte-identically; (3) the 14.4/14.5 sweep has chosen a model + prompt set
on real reconstructed 9p2i contexts and reported per-model structured-output fidelity + the
cover-directive/information-ceiling read; (4) THE PRIMARY CRITERION — a new full-sim baseline (both 4p1i +
9p2i, all 50 seeds) is re-recorded on the locked model + new prompt set in one atomic PR, passes the HARD
validity gate, reconstructs byte-identically, and is committed as the canonical baseline replacing the
final-9B one; and (5) the Phase-13 R-gate is computed and recorded as a MEASUREMENT on that baseline — a flat
or down R1 (information ceiling held) closes the phase as a finding, not a failure. The only thing that
blocks the baseline is a VALIDITY failure at 14.6/14.7 (no candidate model drives a valid sim), a real NO-GO
that pauses the phase rather than papering over the gate.

### Task 14.1 — FeatherlessClient adapter (OpenAI-compatible, $0, thinking policy)
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
reasoning models.

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
- [ ] Thinking policy: `fail_loud` (default) raises a descriptive error on a populated reasoning channel; `strip` discards it explicitly. No silent strip. Inline reasoning that survives into content is caught by the parse seam as a `ValidationError` (test both paths).
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

**Public types introduced:**
- llm.featherless_client.FeatherlessClient
- llm.featherless_client.FeatherlessRawResponse
- llm.featherless_client.FeatherlessSendHook
- llm.provider.PROVIDER_FEATHERLESS

**Implementation hint:**

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
`_compute_cost_usd` (`provider.py:597`). `max_tokens` vs `max_completion_tokens` and any request-level
reasoning-suppression field are resolved against the endpoint docs at implementation time.

**Integration risk:**

This is the provider seam every downstream task rides. Structured-output fidelity (does `response_format`
actually constrain decoding per model, or does the model emit prose-wrapped JSON the `_extract_json_block`
seam must rescue?) is model-specific and is what 14.4 measures — but the adapter must be correct on a clean
OpenAI-shaped response first. The `fail_loud` thinking default must NOT abort the 14.4 sweep of reasoning
models — the harness selects `strip`; the recorded baseline (14.7) selects `fail_loud` unless the owner signs
off on `strip` at 14.6. Getting the `usage` / `choices` fail-loud mapping right protects the per-game token
budget that is now the only real backstop ($0 cost zeroes the `BudgetedLLMClient` USD dimension). Changes to
`provider.py` shared constants / `__all__` / `_compute_cost_usd` are additive-only; the existing
Anthropic/Ollama tests must stay green.

**Ready-to-paste prompt:** `agent_prompts/task-14-1-featherless-client.md`

### Task 14.2 — Per-model prompt-set restructure (pin the 9B set byte-identically)
**Branch:** `phase-14-prompt-set-restructure`
**Depends on:** none
**Section refs:** DESIGN.md §11.4 (replay provenance / prompt_versions); agents/strategic/prompts/loader.py; orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`, `:261`); owner decision 2026-06-25 (per-model prompt sets)
**Complexity:** Medium

Introduce a per-model prompt-set directory layer so the right templates load for the right model. Move the
four existing templates VERBATIM (no content edit) into `agents/strategic/prompts/qwen3_5_9b/`, pinning them
as the frozen 9B reference set. Parameterize the loader by a `prompt_set` selector (env `AILIBI_PROMPT_SET`,
default `qwen3_5_9b` for backward-compatible rendering), building the Jinja `Environment` /
`FileSystemLoader` against the selected subdir. Make `DEFAULT_PROMPT_VERSIONS` a per-set registry and
namespace the recorded `prompt_versions` with the set name so a 9B replay is distinguishable from a new-model
replay. Because the move is content-preserving, the `qwen3_5_9b` set renders byte-identically and the
committed 4p1i/9p2i samples reconstruct byte-identical with ZERO re-record.

**Files in scope:**
- agents/strategic/prompts/qwen3_5_9b/crewmate_report.j2 (moved verbatim from the flat path)
- agents/strategic/prompts/qwen3_5_9b/impostor_report.j2 (moved verbatim)
- agents/strategic/prompts/qwen3_5_9b/accusation_round.j2 (moved verbatim)
- agents/strategic/prompts/qwen3_5_9b/vote_ballot.j2 (moved verbatim)
- agents/strategic/prompts/loader.py (the `prompt_set` selector + per-set Environment resolution; the template-name constants stay, the directory varies)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` becomes a per-set registry; recorded `prompt_versions` namespaced by set)
- tests/agents/test_prompt_loader.py (new or extended: the default set resolves to `qwen3_5_9b` and renders byte-identically; a second set loads; an unknown set fails loud)

**Files NOT in scope:**
- the four template BODIES (content frozen — pure move, zero byte change; any rewording is 14.5's new set)
- replays/samples/ (no re-record; the move must not require one)
- meetings/manager.py + agents/strategic/reasoner.py (call sites consume the loader callables unchanged)
- llm/ (provider work is 14.1)

**Definition of done:**
- [ ] The four templates live under `agents/strategic/prompts/qwen3_5_9b/` with byte-identical content; the `qwen3_5_9b` set renders byte-identically to the pre-move templates (a rendered-output equality test pins this).
- [ ] The loader takes a `prompt_set` selector defaulting to `qwen3_5_9b` (via `AILIBI_PROMPT_SET`); an unknown set raises (no silent fallback); a second (empty-stub) set is loadable to prove the seam.
- [ ] `DEFAULT_PROMPT_VERSIONS` is a per-set registry; recorded `prompt_versions` carry the set namespace; committed 4p1i + 9p2i reconstruct byte-identical with NO re-record (`scripts/verify_samples.sh` + `eval/prompt_regression.py` exact-match hold).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Keep template bytes identical — this is a `git mv` plus a loader/registry change, nothing more. The loader's
`_TEMPLATE_DIR` (`loader.py:57`) becomes per-set: resolve `prompt_set` to a subdir and build the
`FileSystemLoader` against it; the `*_TEMPLATE` filename constants are unchanged. For `DEFAULT_PROMPT_VERSIONS`
(`orchestrator/game.py:261`), key the mapping by set name (e.g. `{"qwen3_5_9b": {...current...}}`) and have
the game/meeting runner select by the active set; the recorded `prompt_versions` should make the set explicit
so provenance never confuses a 9B replay with a new-model replay. Determinism is the acceptance bar:
reconstruction reads recorded prompt bytes, so a content-preserving move keeps the committed samples valid —
prove it with `verify_samples` rather than asserting it.

**Ready-to-paste prompt:** `agent_prompts/task-14-2-prompt-set-restructure.md`

### Task 14.3 — Provider-neutral probe backend (Featherless behind the probe seam)
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

**Implementation hint:**

The seam is tiny: `probe.py:_one_call`, `deception_battery._call`, and `model_ceiling_probe._call_ollama`
each already call `_default_send` then `_extract_json_block` + `model_validate_json`. Factor that into
`call_turn(prompt, schema, *, backend, model, temperature, max_tokens)` and have each probe pass a `backend`
read from a new CLI flag. Keep the ollama branch's `_default_send` call byte-identical (same
`format=schema.model_json_schema()`, same options) so the committed `results-*.jsonl` reproduce. For
Featherless, build the `response_format` json_schema from `schema` and call `llm.featherless_client._default_send`
with `thinking_policy` threaded. Featherless is a concurrent hosted API, so a bounded `asyncio.Semaphore`
(opt-in, 4–8) can cut sweep wall time — but run a sequential pass whenever per-call latency is the metric.

**Ready-to-paste prompt:** `agent_prompts/task-14-3-probe-backend.md`

### Task 14.4 — Featherless model × thinking-mode sweep over reconstructed 9p2i contexts
**Branch:** `phase-14-model-sweep`
**Depends on:** 14.1, 14.3
**Section refs:** audits/audit-2026-06-25-0859-phase-13-close.md (the information-ceiling hypothesis); experiments/lab/report-model-ceiling-probe.md (the model-ceiling-vs-information method); experiments/lab/deflection_probe.py (the cover-directive injection); replays/samples/9p2i
**Complexity:** Integration

Operator-run sweep ($0 marginal): run each candidate Featherless model over the SAME reconstructed
opening/reply/vote contexts from committed `replays/samples/9p2i`, on the PINNED 9B prompts, in both
non-thinking and thinking mode where available, and grade with the identical mechanical `_grade`
(`self_co_locates_body`, `new_self_flag`, `deflects_legal`) + per-model structured-output parse-success rate.
Also run the cover-directive 2×2 (model × {cover OFF, cover ON-reply}, via `deflection_probe._cover_directive`)
to settle whether the impostor self-incrimination tell is a capability ceiling, a prompt artifact, both, or
the information ceiling. Emit a comparison report proposing a recommended (meeting_model, trigger_model, mode)
tuple WITH its evidence — including an honest statement of whether the information-ceiling hypothesis holds.

**Files in scope:**
- experiments/lab/featherless_sweep.py (new: the matrix driver over vote/opening/reply corpora × models × {pinned-9B prompts, cover ON/OFF} × {non-thinking, thinking}, reusing `model_ceiling_probe.do_dump` to freeze contexts once and `grade-frontier` to grade)
- experiments/lab/results-featherless-sweep.jsonl (new: per-cell mechanical grades + parse-success + tokens + latency)
- experiments/lab/report-featherless-sweep.md (new: the comparison table, the model-ceiling-vs-information read, the cover-directive quadrant verdict, and the recommended tuple with evidence)

**Files NOT in scope:**
- llm/ (the adapter is 14.1) + experiments/model_probe/probe.py + experiments/lab/deception_battery.py + experiments/lab/deflection_probe.py + experiments/lab/model_ceiling_probe.py + experiments/lab/probe_backends.py (14.2/14.3 own those; this consumes them)
- agents/strategic/prompts/ (prompt VARIANTS are tested by injection/registry, NOT by editing templates here; authoring a new set is 14.5)
- replays/samples/ (read-only; no re-record)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` unchanged until a baseline locks)

**Definition of done:**
- [ ] Each candidate model (Qwen3-32B instruct, Qwen3-30B-A3B, GLM-4-32B, one RP fine-tune) runs over the SAME reconstructed contexts on the PINNED 9B prompts, in non-thinking and thinking mode where available; mechanical metrics + per-model parse-success rate are tabulated against the 9B baseline.
- [ ] The cover-directive 2×2 (model × {cover OFF, cover ON-reply}) is run and the report states the quadrant verdict: capability ceiling / prompt artifact / both / information ceiling.
- [ ] Per-model structured-output fidelity (parse-success under `response_format`) is reported; any model that cannot reliably emit schema-valid JSON is flagged unfit for the sim.
- [ ] A recommended (meeting_model, trigger_model, mode) tuple is proposed WITH evidence; the report states honestly whether the information-ceiling hypothesis is supported (tell persists across all models) — a valid finding either way.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Reuse `model_ceiling_probe.do_dump` to freeze the hard body-meeting contexts once (`contexts.pkl`), then run
each Featherless model/mode as a new `--tag` graded by the IDENTICAL `_grade` / `grade-frontier` so the only
moving variable is the model (and, in the 2×2, the cover injection from `deflection_probe._cover_directive`).
For votes, drive `experiments/model_probe/probe.py --backend featherless` with its existing variant registry.
This generalizes `model_ceiling_probe.py:11-14` ("if self-flagging does NOT fall as model strength rises, the
binding constraint is INFORMATION not the model") across Featherless models. Operator session: set
`FEATHERLESS_API_KEY`; bounded concurrency for behavior passes, a sequential pass for latency. $0 marginal,
but watch token usage against the 32K context and the frozen 2048/1024 caps.

**Integration risk:**

This is where the strategic risk lives. The mechanical isolated-turn metrics here are PROXIES, not the live
R-gate — a model can deflect better in isolation yet still CORRECTLY SKIP in a noisy full game (the Phase-13
information-ceiling hypothesis). The report must distinguish "emits better turns in isolation" from "raises R1
in a full game," and the lock (14.6) must read this report as evidence, not verdict. Do not let one strong
model's good single-corpus numbers stand in for "the model fixes R1." Operator spend is $0 marginal but the
sweep must not be silently truncated — log the model/mode/context matrix actually run.

**Ready-to-paste prompt:** `agent_prompts/task-14-4-model-sweep.md`

### Task 14.5 — Author redesigned per-model prompt set + A/B re-sweep
**Branch:** `phase-14-new-model-prompts`
**Depends on:** 14.2, 14.4
**Section refs:** tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-25 (simple instructions + role + memory)
**Complexity:** Integration

Author a NEW, independent prompt set for the chosen model under its own `agents/strategic/prompts/<set>/`
directory — simpler "game instructions + role + memory → deduction + interesting sim" prompts with lighter
guard-rails than the 9B needed (the v8/v9 templates were rebuilt to fight the 9B's attention drift; a stronger
model should need less). Register the new set's versions and re-run the 14.4 sweep over the SAME reconstructed
contexts to A/B the new prompts vs the pinned-9B prompts ON the new model, recording the delta. If 14.4 showed
the cover directive is the binding lever, wire it into the reply path of the new set (not gated off the
body-report opening as it is today).

**Files in scope:**
- agents/strategic/prompts/<chosen_set>/crewmate_report.j2 (new)
- agents/strategic/prompts/<chosen_set>/impostor_report.j2 (new)
- agents/strategic/prompts/<chosen_set>/accusation_round.j2 (new; cover directive wired into the reply path if 14.4 showed it binding)
- agents/strategic/prompts/<chosen_set>/vote_ballot.j2 (new)
- orchestrator/game.py (register the new set in the per-set `DEFAULT_PROMPT_VERSIONS` registry)
- experiments/lab/report-featherless-sweep.md (append the new-prompts-vs-pinned A/B delta on the chosen model)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_5_9b/ (the pinned 9B set is frozen — never edited)
- agents/strategic/prompts/loader.py (the selector seam landed in 14.2; this only adds a set directory)
- replays/samples/ (re-record is 14.7)
- llm/ (provider work is 14.1)

**Definition of done:**
- [ ] A new prompt set for the chosen model is authored under `agents/strategic/prompts/<set>/` with lighter guard-rails than the 9B set, registered in the per-set version registry and selectable via `AILIBI_PROMPT_SET`.
- [ ] A re-sweep over the SAME reconstructed contexts records the new prompts' delta vs the pinned-9B prompts ON the new model (mechanical metrics + parse-success); the pinned `qwen3_5_9b` set is unchanged.
- [ ] If 14.4 showed the cover directive is the binding lever, it is wired into the new set's reply path (not gated off the body-report opening); otherwise the report records why it was not.
- [ ] The new set renders under `StrictUndefined` with the existing loader kwargs (no template kwarg drift); a render smoke test over a reconstructed context passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

This is where the owner's "simple instructions, generate deduction + interesting sim" intent lands. Start from
the structural skeleton of the 9B templates (same MeetingTurn / VoteBallot output contract, same kwargs the
loader passes — `agent_id`, `rendered_memory`, `transcript`, `contradictions`, `prior_turn`, `turn_kind`,
`living_ids`, `dead_ids`, `is_impostor`, `is_body_report`) but strip the stacked-imperative guard-rails the 9B
needed. The output JSON contract is FROZEN (the schema is shared) — only the natural-language instruction body
changes. Re-use the 14.3/14.4 harness to A/B: render the new set over the same `contexts.pkl` and grade with
the identical `_grade`. Keep the new set self-contained so a future model gets its own sibling directory.

**Integration risk:**

The new prompts co-vary with the model by design (owner decision), so the 9B comparison is a REFERENCE point,
not a controlled ablation — say so in the report and do not over-claim causality. The output schema must not
drift: a reworded prompt that changes the emitted JSON shape breaks `model_validate_json` and the recording
seam. Validate every new template renders under `StrictUndefined` with the exact loader kwargs before the
re-sweep, or the sweep aborts on an `UndefinedError` rather than a behavior signal.

**Ready-to-paste prompt:** `agent_prompts/task-14-5-new-model-prompts.md`

### Task 14.6 — Lock the baseline tuple (model + prompt set + thinking policy)
**Branch:** `phase-14-lock-decision`
**Depends on:** 14.5
**Section refs:** tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md; audits/audit-2026-06-25-0859-phase-13-close.md; agent_prompts/task-9-5-model-migration-rerecord.md (the pause-and-decide shape)
**Complexity:** Small

Design-thread decision (no code): read the 14.4/14.5 sweep evidence and lock the baseline tuple before any
re-record exists — the chosen meeting_model + trigger_model Featherless ids, the chosen prompt set, the
recorded-baseline thinking policy (`fail_loud` unless the owner signs off on `strip`), and a go/no-go for the
re-record. Mirror the Phase-9 pause between 9.4 (client) and 9.5 (re-record): the decision is re-answered
against the sweep's data, and a NO-GO is an allowed outcome (no candidate clears the structured-output /
behavior bar → stay on 9B / escalate the information ceiling), since the merge criterion is a VALID baseline,
not an improved one.

**Files in scope:**
- tasks/phase-14.md (record the locked decision: chosen meeting_model, trigger_model, prompt set, thinking policy, and the re-record go/no-go with its evidence)

**Files NOT in scope:**
- llm/ + agents/ + replays/ (no implementation; this is a recorded decision)
- experiments/ (the sweep is done; this reads its report)
- agent_prompts/ (the 14.7 prompt is regenerated mechanically by `generate_prompts.py`, not hand-edited here)

**Definition of done:**
- [ ] The locked (meeting_model, trigger_model) Featherless ids are recorded in `tasks/phase-14.md` with their evidence from the sweep report.
- [ ] The chosen prompt set and the recorded-baseline thinking policy (`fail_loud` unless the owner signs off on `strip`) are recorded with rationale.
- [ ] A re-record go/no-go is recorded, explicitly allowing a NO-GO ("no candidate clears the structured-output / behavior bar; stay on 9B / escalate the information ceiling").
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-14-6-lock-decision.md`

### Task 14.7 — Smoke → re-record BOTH sets on the locked model + new prompts + validity gate
**Branch:** `phase-14-featherless-rerecord`
**Depends on:** 14.1, 14.6
**Section refs:** DESIGN.md §11.4, §3.5 (replay provenance, canonical set); agent_prompts/task-9-5-model-migration-rerecord.md (the migration shape); tasks/phase-14.md (the locked tuple from 14.6); scripts/refresh_samples.sh
**Complexity:** Integration

Operator-run spend/time gate. With the tuple locked at 14.6, smoke first (3–5 seeds at 9p2i) to confirm the
thinking policy holds and structured-output parse-success ≈ 100% under the FROZEN token caps, project the
full-run wall time, and STOP for operator go. Then re-record BOTH committed sets (4p1i + 9p2i, all 50 seeds)
on the locked Featherless model + new prompt set in ONE atomic PR, regenerate reports + MANIFESTs +
prompt-regression fixtures + baseline, verify byte-identical reconstruction from the new recordings, and pass
the HARD validity gate. This new baseline replaces the final-9B one as canonical. Win split moves in any
direction and is REPORTED, not gated (the R-gate is 14.8).

**Files in scope:**
- replays/samples/4p1i/ (50 replays + tournament-eval-report.json + MANIFEST.md re-recorded on the locked model; model + prompt_versions + git_sha rows updated)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster sidecar {9,2,2} unchanged)
- tests/fixtures/prompt_regression/ (v_a + v_b fixtures + baseline.json regenerated — provider changed)
- tests/api/test_replay_loader.py (committed-set pins re-verified on new bytes; zero-denominator skips re-scoped)
- tests/eval/test_win_condition_selfcheck.py (committed-set pins re-verified)
- tests/scripts/test_refresh_samples.py (model rows = locked Featherless id, cost 0, git_sha)
- tests/scripts/test_manifest_writer.py (MANIFEST row pins for the new model + prompt_versions)
- scripts/refresh_samples.sh (provider/model literals point at Featherless for the operator run)

**Files NOT in scope:**
- engine/ + meetings/ + agents/ + llm/ + eval/ source (behavior landed in 14.1 / 14.5; this records + regenerates only)
- meetings/manager.py (token caps FROZEN — turn 2048 / vote 1024; do NOT raise; the 9.5 ctx-overrun lesson)
- agents/strategic/prompts/ (no template authoring here; this records the chosen prompt set, it does not edit it)
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel; do not modify)

**Definition of done:**
- [ ] Smoke first (3–5 seeds at 9p2i): thinking policy holds (no un-audited reasoning under `fail_loud`, or the signed-off `strip` behaving), structured-output parse-success ≈ 100%, per-seed wall time + full-run projection reported BEFORE the full runs; STOP for operator go. ABANDON without recording if the guard trips or parse-success craters — re-open 14.1/14.4 or escalate; do NOT weaken the guard or raise the caps.
- [ ] Smoke confirms the floor: every smoke seed reaches game_over with zero ballot truncation / unterminated-JSON parse failures under the FROZEN caps.
- [ ] Both sets re-recorded in ONE PR on the locked model + new prompt set; both reports + MANIFESTs regenerated (model + prompt_versions + new git_sha); prompt-regression fixtures + baseline regenerated; byte-identical reconstruction holds from the new recordings.
- [ ] Validity gate (HARD): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0; leak suite green at 4p1i and 9p2i; meeting_rate ≥ 0.60 with ≥ 30 resolved meetings at 9p2i; byte-identical reconstruction; zero tick-1 kills; zero missed-deadline markers; zero dangling primary_reason_id; cost rows 0; model + prompt_versions rows correct.
- [ ] Funnel report ($0): `extract_gameplay_facts` over the new 9p2i set; the PR body reports win split, ejection count, accusation precision, accuser follow-through, persuasion rate, threshold-quoting-skip count.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

This is the Phase-9 9.5 shape transplanted to Featherless: `AILIBI_LLM_PROVIDER=featherless` +
`FEATHERLESS_API_KEY` + `AILIBI_PROMPT_SET=<chosen>` on every `scripts/refresh_samples.sh` invocation; the
model from 14.6's locked constant. ONE atomic PR — an intermediate commit is un-reconstructable. Featherless
is concurrent, so the full re-record can run far faster than the 9B's ~13h; still smoke-project first. The
report regeneration + MANIFEST update + fixture refresh all happen through `scripts/build_sample_report.py` +
`scripts/_manifest_writer.py` exactly as the 9.5 operator workflow documents. Hosted non-determinism means
FRESH generation won't byte-reproduce, but the recordings replay byte-identically — verify that property
explicitly with `scripts/verify_samples.sh`.

**Integration risk:**

The phase's spend/time gate. If structured-output parse-success is below the sim's tolerance, or the thinking
guard trips, STOP and fix upstream (14.1 adapter, 14.6 model choice) rather than papering the gate — in
particular do NOT raise the token caps (the 9.5 lesson: a raised ctx reintroduced overrun). The recorded
baseline must be auditable: no silent thinking, no silent cost, model/prompt rows exact. A VALIDITY failure
here (no candidate drives a valid sim) is the one real NO-GO that pauses the phase — surface it, do not force
a degraded baseline through.

**Ready-to-paste prompt:** `agent_prompts/task-14-7-rerecord.md`

### Task 14.8 — Characterize the new baseline (R-gate as measurement) + phase close
**Branch:** `phase-14-baseline-characterize-close`
**Depends on:** 14.7
**Section refs:** audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py
**Complexity:** Medium

Design-thread close: compute the Phase-13 R-gate as a MEASUREMENT over the committed 14.7 baseline — R1
(games decided by ejection), R4 floor, R7, impostor win rate, and the rubric geomean ranking (eject-decided >
stopwatch) — and compare to the final-9B baseline (R1 3/50, impostor 84%, eject 9%). Write the close audit
framing the result as an honest finding: state whether the stronger model raised R1 and, if not, whether the
evidence supports the information-ceiling hypothesis (single-room vision → ~45% detector precision → correct
SKIP), recommending Phase 15 (asymmetric visibility / information richness). This is characterization, not a
gate — the phase already merged on the valid new baseline (14.7); a flat or down R1 is a recorded finding.

**Files in scope:**
- audits/audit-2026-06-25-phase-14-close.md (new: the R-gate measurement + the hypothesis-test verdict + the Phase 15 recommendation)
- tasks/phase-14.md (a STATUS banner recording the R-gate outcome and the next step)
- experiments/lab/results-rubric-score.json (re-ranked offline over the new committed replays — data regen, no code change)
- experiments/lab/report-rubric-interestingness.md (re-ranked offline — data regen)

**Files NOT in scope:**
- llm/ + agents/ + meetings/ + engine/ (no behavior change at close)
- replays/samples/ (the 14.7 bytes are the baseline; close READS them)
- eval/ source (the analyzers are reused as-is; this folds, it does not change them)

**Definition of done:**
- [ ] The R-gate is computed offline over the 14.7 baseline (R1, R4 floor, R7, impostor win rate, rubric geomean ranking) and compared to the final-9B baseline (R1 3/50, impostor 84%, eject 9%).
- [ ] The close audit frames the verdict as an HONEST hypothesis test: it states whether the model raised R1, and if not, whether the evidence supports the information-ceiling hypothesis; a null result is recorded as a valid finding, never a blocker.
- [ ] The close audit recommends the next phase (asymmetric visibility / information richness if the ceiling is confirmed; prompt/tactical work if a gap remains).
- [ ] The rubric data is re-ranked offline over the new committed replays ($0, no code change); no number is retrofit to pass.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Pure offline folds over the new `TournamentReport`: `eval/vote_correctness.py` (`ejection_accuracy`,
`compute_genuine_class_conversion`), `eval/accusation_calibration.py` (ECE), `eval/alibi_fabrication.py`
(survival_rate), assembled by `eval/meeting_quality.py`, plus the rubric geomean from
`experiments/lab/rubric_score.py` — all $0, no provider. The framing is the deliverable: per the Phase-13
audit the bottleneck may be INFORMATION not the model, so "R1 did not rise even on a Qwen3-32B-class model" is
a genuine finding that redirects Phase 15, not a Phase-14 failure. Do not retrofit any number.

**Ready-to-paste prompt:** `agent_prompts/task-14-8-baseline-characterize-close.md`
