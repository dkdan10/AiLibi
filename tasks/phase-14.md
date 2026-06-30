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
re-record must beat. Structural information levers (vents/sabotage/wider vision) — and heterogeneous-model
games (per-agent model routing) — are explicitly deferred to Phase 15.

Locked decisions (2026-06-25):
- **Provider:** Featherless AI (flat-rate, OpenAI-compatible, $25/mo Premium, any model size, 32K context).
  Cost recorded as $0 keyed by provider (the Ollama doctrine); token caps (turn 2048 / vote 1024) stay the
  real backstop. Hosted models do not byte-reproduce FRESH generation; recordings still replay
  byte-identically (the loosened contract Ollama already carries).
- **Prompts:** the four existing templates are PINNED as the frozen `qwen3.5:9b` reference set; NEW,
  independent BESPOKE prompt sets are authored per CANDIDATE (model, mode) — built from the ground up (simple
  game instructions + role + memory → deduction + interesting sim), NOT derived from the 9B set, so each model
  is prompted to its own strengths rather than catering to the 9B's quirks (owner decision 2026-06-30; bespoke
  now, to learn each model's ceiling before sharing structure later). The single hard invariant across every
  set is that its turns emit the SAME output JSON schema (`MeetingTurn` / `VoteBallot`) so all sets parse
  identically and the downstream graders / recording seam are unchanged. The candidate sets are `qwen3-32b`
  (non-thinking + a thinking variant), `qwen3-30b-a3b`, `glm-4-32b`, and `cydonia-24b`. A per-model
  prompt-folder restructure selects the right set for the right model. New-model prompts are compared against
  the 9B results but are not a single-variable ablation — model + prompt are co-designed, by choice; the one
  clean control kept is new-set-vs-pinned-9B-set ON THE SAME model. The same-schema invariant is also what
  makes heterogeneous-model games possible (different models as different players in one seed) — that
  capability is structural (per-agent model + set routing + per-player provenance stamping) and is deferred to
  Phase 15; the Phase-14 recorded baseline stays HOMOGENEOUS (one locked model + one set).
- **Model slate:** sweep Qwen3-32B (instruct), Qwen3-30B-A3B (MoE), GLM-4-32B, and one RP/creative
  fine-tune. Thinking models are on the table now that inference is on the cloud (the local `think=False`
  structured-output breakage — `experiments/lab/report-model-ceiling-probe.md` Finding 2 — does not apply to
  a hosted endpoint that returns reasoning in a separate channel); thinking-mode is a sweep AXIS.
- **Two-set structure** (4p1i flat + 9p2i canonical with its roster sidecar) is unchanged.
- **Corrected substrate (Phase 13.5, now merged):** Phase 14 builds on the 13.5 substrate — four
  behavior-changing levers behind default-OFF env flags (`AILIBI_TESTIMONY_AS_CONTENT`,
  `AILIBI_WITNESSED_KILL_EVIDENCE`, `AILIBI_MOVEMENT_PERCEPTION`, `AILIBI_UNFREEZE_MEMORY`;
  `tasks/phase-13-5.md`), read ad-hoc from `os.environ` via the `*_enabled()` resolvers. The levers are pure
  replay-deterministic reductions of recorded events, so flag-ON ("corrected") contexts re-derive OFFLINE
  from the committed (flags-OFF) replays — no re-record needed for the sweep. Phase 14 SWEEPS each model on
  BOTH substrates (flag-OFF legacy + flag-ON corrected; owner decision 2026-06-26) and RE-RECORDS the new
  baseline with ALL 4 flags ON (the full corrected substrate); a per-lever ablation in 14.8 characterizes
  each. The 9B's own 3-game smoke showed the levers FIRE (54 reported-testimony prompts, 5 witnessed kills,
  202 movement packets, ballot lines == graph 36/36) but the 9B cannot DRIVE them (a voter at suspicion 1.00
  over the 0.60 gate, meeting STILL SKIPPED; kill-scene flag fired 0×). So the central Phase-14 hypothesis
  sharpens: can the NEW model DRIVE the corrected substrate where the 9B couldn't?

Parallelism: 14.1 and 14.2 are independent roots and dispatch in parallel (disjoint file scopes); 14.3
follows 14.1 because its probe backend imports the Featherless `_default_send` introduced by 14.1:
`(14.1 ∥ 14.2) → 14.3 → 14.4 → 14.4.1 → 14.5 → 14.6 → 14.7 → 14.8 → 14.9`. 14.3 needs 14.1; 14.4 needs 14.1 + 14.3; 14.4.1 (adapter `enable_thinking` fix surfaced by the 14.4 sweep) needs 14.1 + 14.4; 14.5 needs 14.2 + 14.4 + 14.4.1; 14.9 (flag-default cleanup) needs 14.8.
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
9p2i, all 50 seeds) is re-recorded on the locked model + new prompt set with ALL 4 substrate flags ON (the
flag config STAMPED into the MANIFEST + replay metadata; verify run flag-aware with roster.json) in one
atomic PR, passes the HARD validity gate, reconstructs byte-identically, and is committed as the canonical
baseline replacing the final-9B one; and (5) the Phase-13 R-gate is computed and recorded as a MEASUREMENT on
that baseline — a flat or down R1 (information ceiling held) closes the phase as a finding, not a failure. The
only thing that blocks the baseline is a VALIDITY failure at 14.6/14.7 (no candidate model drives a valid
sim), a real NO-GO that pauses the phase rather than papering over the gate. After the R-gate measurement,
Task 14.9 makes the adopted levers default-ON and retires the vestigial flag-OFF path.

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
`_compute_cost_usd` (`provider.py:597`). The `fail_loud` raw-content guard must run BEFORE
`_extract_json_block` (`provider.py:474-526`), which strips a prose preamble and returns the first valid JSON
— so a post-extraction check cannot catch `reasoning\n{JSON}`. The request-time thinking toggle mirrors
`ollama_client.py:205`'s top-level `think=`; its wire field (`chat_template_kwargs` / `reasoning_effort` / a
`/no_think` token) and `max_tokens` vs `max_completion_tokens` are resolved against the endpoint docs per
model at implementation time.

**Integration risk:**

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

**Ready-to-paste prompt:** `agent_prompts/task-14-1-featherless-client.md`

### Task 14.2 — Per-model prompt-set restructure (pin the 9B set byte-identically)
**Branch:** `phase-14-prompt-set-restructure`
**Depends on:** none
**Section refs:** DESIGN.md §11.4 (replay provenance / prompt_versions); agents/strategic/prompts/loader.py; orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`, `:266-271`); owner decision 2026-06-25 (per-model prompt sets)
**Complexity:** Medium

Introduce a per-model prompt-set directory layer so the right templates load for the right model. Move the
four existing templates VERBATIM (no content edit) into `agents/strategic/prompts/qwen3_5_9b/`, pinning them
as the frozen 9B reference set. Parameterize the loader by a `prompt_set` selector (env `AILIBI_PROMPT_SET`,
default `qwen3_5_9b` for backward-compatible rendering), building the Jinja `Environment` /
`FileSystemLoader` against the selected subdir. Add a per-set version registry ALONGSIDE the existing
`DEFAULT_PROMPT_VERSIONS`, keeping that symbol and the 9B set's recorded values (`crewmate_report.v8`,
`accusation_round.v9`, `impostor_report_v6`, `vote_ballot/v7`) byte-identically unchanged — so the committed
replays AND the existing `prompt_versions` assertions in `tests/orchestrator/` + `tests/scripts/` stay green
without edits. A new-model replay is distinguished by its OWN version strings plus the recorded model id, not
by prefixing the 9B set's keys/values. Because the move is content-preserving and the 9B recorded metadata is
unchanged, the committed 4p1i/9p2i samples reconstruct byte-identical with ZERO re-record. The prompt SET
(templates) is orthogonal to the 13.5 substrate-flag config: 13.5 changed no `.j2` and bumped no version, so
the byte-identical pin is independent of which substrate flags are ON (the corrected substrate is a
render-INPUT dimension, handled in 14.4/14.7, not a template change).

**Files in scope:**
- agents/strategic/prompts/qwen3_5_9b/crewmate_report.j2 (moved verbatim from the flat path)
- agents/strategic/prompts/qwen3_5_9b/impostor_report.j2 (moved verbatim)
- agents/strategic/prompts/qwen3_5_9b/accusation_round.j2 (moved verbatim)
- agents/strategic/prompts/qwen3_5_9b/vote_ballot.j2 (moved verbatim)
- agents/strategic/prompts/loader.py (the `prompt_set` selector + per-set Environment resolution; the template-name constants stay, the directory varies)
- orchestrator/game.py (add a per-set version registry alongside `DEFAULT_PROMPT_VERSIONS`; the 9B set's recorded `prompt_versions` keys/values are unchanged; additive only — preserve the merged 13.5 flag wiring, e.g. `unfreeze_memory_enabled()` / `ENV_UNFREEZE_MEMORY` at `:714-735` and the testimony read at `:1656`)
- tests/agents/test_prompt_loader.py (new or extended: the default set resolves to `qwen3_5_9b` and renders byte-identically; a second set loads; an unknown set fails loud)

**Files NOT in scope:**
- the four template BODIES (content frozen — pure move, zero byte change; any rewording is 14.5's new set)
- replays/samples/ (no re-record; the move must not require one)
- meetings/manager.py + agents/strategic/reasoner.py (call sites consume the loader callables unchanged)
- llm/ (provider work is 14.1)

**Definition of done:**
- [ ] The four templates live under `agents/strategic/prompts/qwen3_5_9b/` with byte-identical content; the `qwen3_5_9b` set renders byte-identically to the pre-move templates (a rendered-output equality test pins this).
- [ ] The loader takes a `prompt_set` selector defaulting to `qwen3_5_9b` (via `AILIBI_PROMPT_SET`); an unknown set raises (no silent fallback); a second (empty-stub) set is loadable to prove the seam.
- [ ] A per-set version registry is added alongside `DEFAULT_PROMPT_VERSIONS`; the 9B set's recorded `prompt_versions` keys/values are byte-identically unchanged, so the existing assertions in `tests/orchestrator/test_replay_meetings.py`, `tests/orchestrator/test_meeting_integration.py`, and `tests/scripts/test_manifest_writer.py` stay green WITHOUT edits; committed 4p1i + 9p2i reconstruct byte-identical with NO re-record (`scripts/verify_samples.sh` + `eval/prompt_regression.py` exact-match hold).
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
`FileSystemLoader` against it; the `*_TEMPLATE` filename constants are unchanged. Keep `DEFAULT_PROMPT_VERSIONS`
(`orchestrator/game.py:266-271`) as the 9B default mapping with its EXACT current values and add a registry
alongside (e.g. `PROMPT_VERSION_SETS = {"qwen3_5_9b": DEFAULT_PROMPT_VERSIONS, ...}`) that the runner selects
by active set. Do NOT prefix or reformat the 9B set's keys/values — `tests/orchestrator/test_replay_meetings.py:390-415`,
`tests/orchestrator/test_meeting_integration.py:2320`, and `tests/scripts/test_manifest_writer.py` pin them and
the committed replays store them verbatim; provenance for a new set comes from its own version strings + the
recorded model id. Determinism is the acceptance bar:
reconstruction reads recorded prompt bytes, so a content-preserving move keeps the committed samples valid —
prove it with `verify_samples` rather than asserting it.

**Ready-to-paste prompt:** `agent_prompts/task-14-2-prompt-set-restructure.md`

### Task 14.3 — Provider-neutral probe backend (Featherless behind the probe seam)
**Branch:** `phase-14-probe-backend`
**Depends on:** 14.1
**Section refs:** experiments/model_probe/probe.py; experiments/lab/deception_battery.py; experiments/lab/deflection_probe.py; experiments/lab/model_ceiling_probe.py (the `dump` / `grade-frontier` modes)
**Complexity:** Medium

The real-data probes reconstruct hard contexts from committed `replays/samples/9p2i` and call the model
through one tiny seam that today hits `llm.ollama_client._default_send` then `_extract_json_block` +
`model_validate_json` (`probe.py:_one_call`, `deception_battery.py:_call`, `model_ceiling_probe.py:_call_ollama`).
Add a provider-neutral `call_turn` behind that seam so the identical reconstructed contexts can flow to
Featherless via 14.1's `llm.featherless_client._default_send` (hence the dependency on 14.1), parameterized by
a `--backend`/`--models` flag (default `ollama` preserves CI + the existing `results-*.jsonl`). `call_turn`
threads BOTH the request-time thinking toggle (so 14.4 can drive its non-thinking/thinking axis) and the
response-side `thinking_policy="strip"` (so reasoning models do not abort the sweep). No engine/agent/replay
bytes change — the probes stay read-only over committed replays. The reconstructed-context path honors the
merged 13.5 substrate flags (`*_enabled()` read from `os.environ`), so the sweep can build flag-OFF and
flag-ON contexts by toggling the env vars; `call_turn` records the active `substrate_flags` config on each
result row for provenance. The 13.5 flag logic is not modified.

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
- [ ] `call_turn` threads BOTH the request-time thinking toggle (to drive 14.4's non-thinking/thinking axis) and the response-side `thinking_policy=strip` (so reasoning models do not abort the sweep); bounded concurrency is opt-in (sequential when latency is the measured metric).
- [ ] The reconstructed-context path honors the 13.5 `*_enabled()` flags (set via env) so the sweep can build BOTH flag-OFF and flag-ON contexts; each result row tags its `substrate_flags` config; the 13.5 flag gates are not modified.
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
(introduced by 14.1) with BOTH the request-time thinking flag and the response-side `thinking_policy` threaded
through `call_turn`'s signature. Featherless is a concurrent hosted API, so a bounded `asyncio.Semaphore`
(opt-in, 4–8) can cut sweep wall time — but run a sequential pass whenever per-call latency is the metric.
The substrate-flag config is controlled by the sweep via the 4 `AILIBI_*` env vars (read during context
reconstruction at `replay_loader.py:850` / `observation/service.py:461` / `beliefs.py:629` / the unfreeze
ballot re-render); `call_turn` accepts and records the active `substrate_flags` so 14.4's two-column
(flag-OFF / flag-ON) rows are self-describing.

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
- experiments/lab/featherless_sweep.py (new: the matrix driver over vote/opening/reply corpora × models × {pinned-9B prompts, cover ON/OFF} × {non-thinking, thinking} × {flag-OFF, flag-ON substrate}, reusing `model_ceiling_probe.do_dump` to freeze contexts once per substrate and `grade-frontier` to grade)
- experiments/lab/results-featherless-sweep.jsonl (new: per-cell mechanical grades + parse-success + tokens + latency + the `substrate_flags` config)
- experiments/lab/report-featherless-sweep.md (new: the comparison table, the model-ceiling-vs-information read, the cover-directive quadrant verdict, the per-model flag-OFF vs flag-ON substrate delta, and the recommended tuple with evidence)

**Files NOT in scope:**
- llm/ (the adapter is 14.1) + experiments/model_probe/probe.py + experiments/lab/deception_battery.py + experiments/lab/deflection_probe.py + experiments/lab/model_ceiling_probe.py + experiments/lab/probe_backends.py (14.2/14.3 own those; this consumes them)
- agents/strategic/prompts/ (prompt VARIANTS are tested by injection/registry, NOT by editing templates here; authoring a new set is 14.5)
- replays/samples/ (read-only; no re-record)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` unchanged until a baseline locks)

**Definition of done:**
- [ ] Each candidate model (`Qwen/Qwen3-32B`, `Qwen/Qwen3-30B-A3B`, `zai-org/GLM-4-32B`, `TheDrummer/Cydonia-24B-v2` [RP/creative]) — AND the 9B reference — runs over the SAME reconstructed contexts on the PINNED 9B prompts, in non-thinking and thinking mode where available (driven by the request-time thinking toggle from 14.1, threaded via 14.3 — not the response-side policy), on BOTH the flag-OFF (legacy) and flag-ON (corrected 13.5) substrate (two columns; flag-ON contexts re-derived offline by setting the 4 `AILIBI_*` env vars); each result row carries its `substrate_flags`; mechanical metrics + per-model parse-success rate are tabulated per substrate against the 9B.
- [ ] The cover-directive 2×2 (model × {cover OFF, cover ON-reply}) is run and the report states the quadrant verdict: capability ceiling / prompt artifact / both / information ceiling.
- [ ] The report states the per-model SUBSTRATE delta (flag-ON vs flag-OFF): does the corrected 13.5 substrate help THIS model decide where the 9B degraded (a voter at suspicion 1.00 over the 0.60 gate, meeting STILL SKIPPED)? — separating "corrected memory helps the model" from "the model is just stronger."
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
but watch token usage against the 32K context and the frozen 2048/1024 caps. Build the flag-ON (corrected
13.5) contexts by setting the 4 env vars (`AILIBI_TESTIMONY_AS_CONTENT` / `AILIBI_WITNESSED_KILL_EVIDENCE` /
`AILIBI_MOVEMENT_PERCEPTION` / `AILIBI_UNFREEZE_MEMORY`) before the context reconstruction (`ReplayLoader` /
`build_*_contexts` re-derive memory through the `*_enabled()` reads), and the flag-OFF column with them unset;
the levers are replay-deterministic over the committed (flags-OFF) replays, so no re-record is needed. Tag
every row's `substrate_flags`. Slate ids (HuggingFace repo form, owner-confirmed 2026-06-28):
`Qwen/Qwen3-32B` (quality baseline; the adapter default), `Qwen/Qwen3-30B-A3B` (MoE / speed), and
`zai-org/GLM-4-32B` (agentic) — these three are live-verified on Featherless (PR #202) — plus the RP/creative
wildcard `TheDrummer/Cydonia-24B-v2` (confirm it is served via `GET {base_url}/v1/models` before the run; an
unrecognized id is a hard HTTP 400). The thinking axis (`request_thinking` True/False) applies ONLY to the
two Qwen3 models (native `enable_thinking`); `zai-org/GLM-4-32B` and the RP tune run non-thinking only.

**Integration risk:**

This is where the strategic risk lives. The mechanical isolated-turn metrics here are PROXIES, not the live
R-gate — a model can deflect better in isolation yet still CORRECTLY SKIP in a noisy full game (the Phase-13
information-ceiling hypothesis). The report must distinguish "emits better turns in isolation" from "raises R1
in a full game," and the lock (14.6) must read this report as evidence, not verdict. Do not let one strong
model's good single-corpus numbers stand in for "the model fixes R1." Operator spend is $0 marginal but the
sweep must not be silently truncated — log the model/mode/context matrix actually run.

**Ready-to-paste prompt:** `agent_prompts/task-14-4-model-sweep.md`

### Task 14.4.1 — Make the Featherless adapter's `enable_thinking` kwarg conditional (unblock non-Qwen models)
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

**Implementation hint:**

The 14.4 harness already proved the fix shape: `featherless_sweep.py:_bare_send` posts the identical request
MINUS `chat_template_kwargs` and parses through the SAME `_extract_json_block` + `model_validate_json` seam, so
the production change is to make the adapter's payload builder (`_build_chat_payload` / wherever the 14.1
adapter assembles `chat_template_kwargs`) emit the field conditionally on a per-model capability signal. Prefer
an explicit signal over substring magic: a small `enable_thinking`-supported predicate keyed off the model id
family, or a constructor / per-call capability flag the caller can override — so the behavior is testable and
fails loud on an unknown id rather than swallowing the 400. When the model does not support it, drop the whole
`chat_template_kwargs` object. Keep the Qwen3 path byte-identical so the existing 14.1 adapter tests stay green.

**Ready-to-paste prompt:** `agent_prompts/task-14-4-1-adapter-thinking-conditional.md`

### Task 14.5 — Author bespoke per-candidate prompt sets + A/B re-sweep
**Branch:** `phase-14-new-model-prompts`
**Depends on:** 14.2, 14.4, 14.4.1
**Section refs:** tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md (14.4 evidence); agents/strategic/prompts/qwen3_5_9b/accusation_round.j2 (the cover-directive gating `is_impostor` + `is_body_report`); owner decision 2026-06-30 (bespoke per-candidate sets, same-schema invariant)
**Complexity:** Integration

Author a NEW, independent BESPOKE prompt set for EACH candidate (model, mode) under its own
`agents/strategic/prompts/<set>/` directory — built from the ground up (simpler "game instructions + role +
memory → deduction + interesting sim"), NOT derived from the 9B templates, so each model is prompted to its
own strengths rather than inheriting the v8/v9 scaffolding rebuilt to fight the 9B's attention drift. The
candidate sets are `qwen3_32b` (non-thinking), `qwen3_32b_thinking`, `qwen3_30b_a3b`, `glm_4_32b`, and
`cydonia_24b` (owner decision 2026-06-30; bespoke now, to learn each model's ceiling before sharing structure
later). The ONE hard invariant is the output JSON schema: every set's turns must emit the SAME
`MeetingTurn` / `VoteBallot` shape so all sets parse identically and the graders / recording seam are
unchanged. Register each set's versions and re-run the 14.4 sweep over the SAME reconstructed contexts to A/B
each new set vs the pinned-9B prompts ON its own model (the one clean control in a co-designed change),
recording the delta. Where 14.4 showed the cover directive is a binding lever, wire it into the reply path of
the new set(s) (not gated off the body-report opening as it is today). The non-Qwen sets require the 14.4.1
adapter fix so they iterate against the real client, not the harness bare-send.

**Files in scope:**
- agents/strategic/prompts/qwen3_32b/ (new bespoke set: the 4 templates — crewmate_report, impostor_report, accusation_round [cover directive wired into the reply path if 14.4 showed it binding], vote_ballot — same output schema)
- agents/strategic/prompts/qwen3_32b_thinking/ (new bespoke set for the thinking variant; may share most templates with `qwen3_32b`, author only what genuinely differs)
- agents/strategic/prompts/qwen3_30b_a3b/ (new bespoke set)
- agents/strategic/prompts/glm_4_32b/ (new bespoke set; requires the 14.4.1 adapter fix to run on the real client)
- agents/strategic/prompts/cydonia_24b/ (new bespoke set; requires the 14.4.1 adapter fix)
- orchestrator/game.py (register each new set in the per-set prompt-version registry; preserve the merged 13.5 flag wiring)
- experiments/lab/report-featherless-sweep.md (append the per-set new-vs-pinned-9B A/B delta on each set's own model)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_5_9b/ (the pinned 9B set is frozen — never edited)
- agents/strategic/prompts/loader.py (the selector seam landed in 14.2; this only adds set directories)
- replays/samples/ (re-record is 14.7)
- llm/ (the provider adapter is 14.1; the `enable_thinking` conditional is 14.4.1)
- per-agent model/set routing for heterogeneous-model games (structural; deferred to Phase 15 — these sets are the enabler, but 14.5 authors + validates them HOMOGENEOUSLY)

**Definition of done:**
- [ ] A bespoke prompt set is authored for EACH candidate (`qwen3_32b`, `qwen3_32b_thinking`, `qwen3_30b_a3b`, `glm_4_32b`, `cydonia_24b`) under its own `agents/strategic/prompts/<set>/`, built from the ground up (not copied from the 9B set), registered in the per-set version registry and selectable via `AILIBI_PROMPT_SET`.
- [ ] Every set's turns emit the SAME output JSON schema (`MeetingTurn` / `VoteBallot`) so all sets parse identically — a cross-set parse check over a reconstructed context confirms it; the output contract is the one hard invariant.
- [ ] A re-sweep over the SAME reconstructed contexts records each set's delta vs the pinned-9B prompts ON its own model (mechanical metrics + parse-success); the pinned `qwen3_5_9b` set is unchanged.
- [ ] Where 14.4 showed the cover directive is a binding lever, it is wired into the new set's reply path (not gated off the body-report opening); otherwise the report records why it was not.
- [ ] Every new set renders under `StrictUndefined` with the existing loader kwargs (no template kwarg drift); a render smoke test over a reconstructed context passes for each.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

This is where the owner's "simple instructions, generate deduction + interesting sim" intent lands, per
candidate. For each set, start from the OUTPUT contract (the shared `MeetingTurn` / `VoteBallot` schema and the
loader kwargs the templates may reference — `agent_id`, `rendered_memory`, `transcript`, `contradictions`,
`prior_turn`, `turn_kind`, `living_ids`, `dead_ids`, `is_impostor`, `is_body_report`) and write the
natural-language instruction body FRESH for that model — do NOT port the 9B's stacked-imperative guard-rails.
The JSON contract is FROZEN (only the instruction prose changes), which is what keeps `model_validate_json` and
the recording seam working across every set and is the precondition for later heterogeneous play. The
`qwen3_32b_thinking` set will usually differ from `qwen3_32b` in only a template or two (a thinking model needs
less step-by-step coaxing) — author only what differs, but keep it a self-contained directory. Re-use the
14.3/14.4 harness to A/B: render each set over the same `contexts.pkl` and grade with the identical `_grade`.
GLM / Cydonia need the 14.4.1 adapter fix to iterate against the real client rather than the sweep's
bare-send.

**Integration risk:**

The new prompts co-vary with the model by design (owner decision), so the 9B comparison is a REFERENCE point,
not a controlled ablation — say so in the report and do not over-claim causality. Authoring 5 bespoke sets
multiplies the schema-drift surface: each set is an independent output surface, and a single set drifting the
emitted JSON shape breaks `model_validate_json`, its own recording, AND the same-schema invariant that later
heterogeneous play depends on. Validate every new template renders under `StrictUndefined` with the exact
loader kwargs AND parses to the shared schema before the re-sweep, or the sweep aborts on an `UndefinedError` /
`ValidationError` rather than a behavior signal.

**Ready-to-paste prompt:** `agent_prompts/task-14-5-new-model-prompts.md`

### Task 14.6 — Lock the baseline tuple (model + prompt set + thinking policy)
**Branch:** `phase-14-lock-decision`
**Depends on:** 14.5
**Section refs:** tasks/phase-14.md (this phase); experiments/lab/report-featherless-sweep.md; audits/audit-2026-06-25-0859-phase-13-close.md; agent_prompts/task-9-5-model-migration-rerecord.md (the pause-and-decide shape)
**Complexity:** Small

Design-thread decision (no code): read the 14.4/14.5 sweep evidence and lock the baseline tuple before any
re-record exists — the chosen meeting_model + trigger_model Featherless ids, the chosen prompt set (ONE of the
14.5 bespoke sets; the baseline stays HOMOGENEOUS — the other bespoke sets remain available but unrecorded,
for the Phase-15 heterogeneous-games task they enable), the recorded-baseline thinking policy (`fail_loud` unless the owner signs off on `strip`), the
`response_format_mode` (`json_object` default per the 14.1 live finding 2026-06-27 — strict `json_schema` is
rejected by the slate; `json_schema` stays selectable), the substrate-flag
config for the re-record (all 4 13.5 flags ON per owner decision 2026-06-26; 14.8's per-lever ablation
characterizes each, non-gating), and a go/no-go for the re-record. Mirror the Phase-9 pause between 9.4
(client) and 9.5 (re-record): the decision is re-answered
against the sweep's data, and a NO-GO is an allowed outcome (no candidate clears the structured-output /
behavior bar → stay on 9B / escalate the information ceiling), since the merge criterion is a VALID baseline,
not an improved one.

**Files in scope:**
- tasks/phase-14.md (record the locked decision: chosen meeting_model, trigger_model, prompt set, thinking policy, response_format_mode (json_object), substrate-flag config (all 4 ON), and the re-record go/no-go with its evidence)

**Files NOT in scope:**
- llm/ + agents/ + replays/ (no implementation; this is a recorded decision)
- experiments/ (the sweep is done; this reads its report)
- agent_prompts/ (the 14.7 prompt is regenerated mechanically by `generate_prompts.py`, not hand-edited here)

**Definition of done:**
- [ ] The locked (meeting_model, trigger_model) Featherless ids are recorded in `tasks/phase-14.md` with their evidence from the sweep report.
- [ ] The chosen prompt set and the recorded-baseline thinking policy (`fail_loud` unless the owner signs off on `strip`) are recorded with rationale.
- [ ] The locked baseline is HOMOGENEOUS — ONE (meeting_model, trigger_model, prompt set, mode); the other 14.5 bespoke sets remain available but are NOT recorded (heterogeneous-model play is a Phase-15 task enabled by them).
- [ ] The `response_format_mode` is recorded = `json_object` (the 14.1 live finding 2026-06-27: strict `json_schema` 400s on the slate), with `json_schema` noted as selectable for a future endpoint and no silent fallback between modes.
- [ ] The re-record substrate-flag config is recorded = all 4 13.5 flags ON (owner decision 2026-06-26), with 14.8's per-lever ablation noted as characterization (non-gating).
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
on the locked Featherless model + new prompt set with ALL 4 13.5 substrate flags ON, in ONE atomic PR,
STAMPING the flag config into the MANIFEST (a new `flags` column) + the replay metadata so a replay
self-describes which substrate generated it, regenerate reports + MANIFESTs + prompt-regression fixtures +
baseline, verify byte-identical reconstruction from the new recordings WITH the same 4 flags set and
roster.json present, and pass the HARD validity gate. This new baseline replaces the final-9B one as
canonical. Win split moves in any direction and is REPORTED, not gated (the R-gate is 14.8).

**Files in scope:**
- replays/samples/4p1i/ (50 replays + tournament-eval-report.json + MANIFEST.md re-recorded on the locked model, all 4 flags ON; model + prompt_versions + `flags` + git_sha rows updated)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded, all 4 flags ON; roster sidecar {9,2,2} unchanged)
- scripts/_manifest_writer.py (NEW `flags` MANIFEST column stamping the substrate-flag config per seed; the `seed | model | prompt_versions | ...` header gains `flags`)
- orchestrator/replay.py (a substrate-flag-config field on the replay metadata so a replay self-describes which substrate generated it — additive; preserve the merged 13.5 reads)
- api/replay_loader.py (verify/reconstruct honors the stamped flag config; preserve the merged 13.5 `*_enabled()` reads)
- tests/fixtures/prompt_regression/ (v_a + v_b fixtures + baseline.json regenerated — provider + substrate changed)
- tests/api/test_replay_loader.py (committed-set pins re-verified on new bytes; zero-denominator skips re-scoped)
- tests/eval/test_win_condition_selfcheck.py (committed-set pins re-verified)
- tests/scripts/test_refresh_samples.py (model rows = locked Featherless id, cost 0, git_sha)
- tests/scripts/test_manifest_writer.py (MANIFEST row pins for the new model + prompt_versions)
- scripts/refresh_samples.sh (provider/model literals point at Featherless for the operator run)

**Files NOT in scope:**
- engine/ + meetings/ + agents/ + llm/ + eval/ source (behavior landed in 14.1 / 14.5; this records + regenerates only)
- meetings/manager.py (token caps FROZEN — turn 2048 / vote 1024; do NOT raise; the 9.5 ctx-overrun lesson)
- agents/strategic/prompts/ (no template authoring here; this records the chosen prompt set, it does not edit it)
- the 13.5 flag-source logic (the `*_enabled()` resolvers + flag gates) — 14.7 sets the flags ON via env + STAMPS the config; it does NOT change the flag logic (default-ON + retiring the OFF path is 14.9)
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel; do not modify)

**Definition of done:**
- [ ] Smoke first (3–5 seeds at 9p2i): thinking policy holds (no un-audited reasoning under `fail_loud`, or the signed-off `strip` behaving), structured-output parse-success ≈ 100%, per-seed wall time + full-run projection reported BEFORE the full runs; STOP for operator go. ABANDON without recording if the guard trips or parse-success craters — re-open 14.1/14.4 or escalate; do NOT weaken the guard or raise the caps.
- [ ] Smoke confirms the floor: every smoke seed reaches game_over with zero ballot truncation / unterminated-JSON parse failures under the FROZEN caps.
- [ ] Both sets re-recorded in ONE PR on the locked model + new prompt set with all 4 13.5 substrate flags ON; both reports + MANIFESTs regenerated (model + prompt_versions + new `flags` column + new git_sha); the flag config is also stamped into the replay metadata; prompt-regression fixtures + baseline regenerated; byte-identical reconstruction holds from the new recordings.
- [ ] Validity gate (HARD): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0; leak suite green at 4p1i and 9p2i; meeting_rate ≥ 0.60 with ≥ 30 resolved meetings at 9p2i; byte-identical reconstruction (verified FLAG-AWARE — the same 4 flags set AND roster.json present, else the loader defaults to 4p1i and fails spuriously); zero tick-1 kills; zero missed-deadline markers; zero dangling primary_reason_id; cost rows 0; model + prompt_versions + flags rows correct.
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
`FEATHERLESS_API_KEY` + `AILIBI_PROMPT_SET=<chosen>` PLUS all 4 substrate flags
(`AILIBI_TESTIMONY_AS_CONTENT=1 AILIBI_WITNESSED_KILL_EVIDENCE=1 AILIBI_MOVEMENT_PERCEPTION=1
AILIBI_UNFREEZE_MEMORY=1`) on every `scripts/refresh_samples.sh` invocation; the model from 14.6's locked
constant. ONE atomic PR — an intermediate commit is un-reconstructable. Featherless is concurrent, so the
full re-record can run far faster than the 9B's ~13h; still smoke-project first. The report regeneration +
MANIFEST update + fixture refresh all happen through `scripts/build_sample_report.py` +
`scripts/_manifest_writer.py` (the latter gains the `flags` column) exactly as the 9.5 operator workflow
documents. Hosted non-determinism means FRESH generation won't byte-reproduce, but the recordings replay
byte-identically — verify that property explicitly with `scripts/verify_samples.sh` RUN WITH THE SAME 4 FLAGS
SET and a present `roster.json` (a flag-ON recording reconstructs byte-identically only when verify sets the
same flags AND finds roster.json; a temp dir without it defaults to 4p1i and fails spuriously — not a
determinism bug). Do NOT touch the 13.5 `*_enabled()` logic here (set via env + stamp only; default-ON is
14.9).

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

Design-thread close: compute the Phase-13 R-gate as a MEASUREMENT over the committed 14.7 flags-ON baseline —
R1 (games decided by ejection), R4 floor, R7, impostor win rate, and the rubric geomean ranking (eject-decided
> stopwatch) — and compare to the final-9B baseline (R1 3/50, impostor 84%, eject 9%). Also run a per-lever
ABLATION (offline, $0): toggle each of the 4 substrate flags during re-derivation over the baseline replays to
characterize each lever's contribution, and recommend the default set for 14.9 (note the kill-scene flag fired
0× in the 9B smoke — flag it as UNMEASURED / needing a richer scenario, not a negative result). Write the
close audit framing the result as an honest finding: state whether the stronger model raised R1 — the sharper
hypothesis is can the NEW model DRIVE the corrected substrate where the 9B couldn't (the 9B's voter sat at
suspicion 1.00 over the 0.60 gate yet the meeting SKIPPED) — and, if not, whether the evidence supports the
information-ceiling hypothesis (single-room vision → ~45% detector precision → correct SKIP) even with the
corrected substrate ON, recommending Phase 15 (asymmetric visibility / information richness; and
heterogeneous-model games — per-agent model routing — enabled by the 14.5 bespoke same-schema sets). This is
characterization, not a gate — the phase already merged on the valid new baseline (14.7); a flat or down R1 is
a recorded finding.

**Files in scope:**
- audits/audit-2026-06-25-phase-14-close.md (new: the R-gate measurement + the per-lever ablation + the hypothesis-test verdict + the Phase 15 recommendation)
- experiments/lab/results-substrate-ablation.jsonl (new: per-lever ablation — each of the 4 flags toggled offline over the baseline replays, R-gate / conversion metrics per cell; $0)
- tasks/phase-14.md (a STATUS banner recording the R-gate outcome, the recommended default flag set, and the next step)
- experiments/lab/results-rubric-score.json (re-ranked offline over the new committed replays — data regen, no code change)
- experiments/lab/report-rubric-interestingness.md (re-ranked offline — data regen)

**Files NOT in scope:**
- llm/ + agents/ + meetings/ + engine/ (no behavior change at close)
- replays/samples/ (the 14.7 bytes are the baseline; close READS them)
- eval/ source (the analyzers are reused as-is; this folds, it does not change them)

**Definition of done:**
- [ ] The R-gate is computed offline over the 14.7 flags-ON baseline (R1, R4 floor, R7, impostor win rate, rubric geomean ranking) and compared to the final-9B baseline (R1 3/50, impostor 84%, eject 9%).
- [ ] A per-lever ablation (each of the 4 13.5 flags toggled offline over the baseline replays) characterizes each lever's contribution and recommends the default set for 14.9; the kill-scene flag's 0× firing is noted as UNMEASURED (needs a richer scenario), not a negative result.
- [ ] The close audit frames the verdict as an HONEST hypothesis test: it states whether the model raised R1, and if not, whether the evidence supports the information-ceiling hypothesis (even with the corrected substrate ON); a null result is recorded as a valid finding, never a blocker.
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

### Task 14.9 — Make the adopted 13.5 levers default-ON + retire the flag-OFF path
**Branch:** `phase-14-substrate-default-on`
**Depends on:** 14.8
**Section refs:** tasks/phase-13-5.md (the 4 levers); tasks/phase-14.md (the 14.7 flags-ON baseline + 14.8 ablation); agents/memory/store.py + meetings/transcript.py + observation/service.py + orchestrator/game.py (the `*_enabled()` resolvers)
**Complexity:** Integration

With the new baseline recorded flags-ON (14.7) and the per-lever ablation in hand (14.8), finish the
integration: make the adopted 13.5 levers the DEFAULT behavior and retire the now-vestigial flag-OFF path. Per
owner decision 2026-06-26 all 4 flags are adopted (the ablation is characterization, not a veto): flip the 4
`*_enabled()` resolvers to default-ON (or remove the env gate entirely), delete the now-dead OFF branches, and
retarget the flag-OFF byte-identity tests onto the flags-ON baseline. The committed replays are already
flags-ON (14.7), so reconstruction no longer needs the env vars set and the determinism story simplifies.

**Files in scope:**
- agents/memory/store.py (testimony + movement-sighting derivation becomes unconditional; the OFF branch + `ENV_TESTIMONY_AS_CONTENT` / `testimony_as_content_enabled` gate retired)
- meetings/transcript.py (`witnessed_kill_evidence_enabled` gate retired; kill-scene + witness-belief derivation unconditional)
- observation/service.py (`movement_perception_enabled` gate retired; the empty-tuple OFF branch removed)
- orchestrator/game.py (`unfreeze_memory_enabled` gate retired; the `rerender_memory is None` OFF branch removed)
- agents/memory/beliefs.py (the witnessed-kill suspicion read becomes unconditional)
- api/replay_loader.py (reconstruction no longer reads the flags — the corrected derivation is unconditional)
- tests/ (the flag-OFF byte-identity / flag-toggle tests across tests/agents/ + tests/meetings/ + tests/observation/ + tests/orchestrator/ retargeted onto the flags-ON baseline)
- .env.example (remove the now-defunct flag knobs)

**Files NOT in scope:**
- replays/samples/ (the 14.7 flags-ON bytes ARE the baseline; this changes no replay)
- agents/strategic/prompts/ (the prompt sets are 14.2/14.5)
- llm/ (the provider is 14.1)
- scripts/_manifest_writer.py (the `flags` column from 14.7 stays as provenance even though the flags are no longer toggleable)

**Definition of done:**
- [ ] The 4 adopted levers are DEFAULT behavior (the `*_enabled()` env gates default-ON or removed); the now-dead flag-OFF branches and env constants are deleted, not left vestigial.
- [ ] The committed flags-ON baseline (14.7) reconstructs byte-identically WITHOUT any env vars set (`scripts/verify_samples.sh` under a bare environment); the MANIFEST/replay `flags` stamp reads "all 4 ON" and is consistent with the now-unconditional behavior.
- [ ] The former flag-OFF byte-identity tests are retargeted onto the flags-ON baseline (or deleted with rationale); no test asserts the retired OFF behavior; the leak suite stays green at 4p1i and 9p2i.
- [ ] `.env.example` no longer advertises the retired flag knobs.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

A pure simplification gated on the 14.7 baseline existing flags-ON: the corrected derivation becomes
unconditional, so the `*_enabled()` resolvers + their OFF branches + the env constants
(`ENV_TESTIMONY_AS_CONTENT` / `ENV_WITNESSED_KILL_EVIDENCE` / `ENV_MOVEMENT_PERCEPTION` /
`ENV_UNFREEZE_MEMORY`) can be deleted. Do it lever-by-lever, re-running `scripts/verify_samples.sh` under a
BARE environment after each so any residual flag-read is caught immediately. The `flags` MANIFEST column
(14.7) stays as provenance even though the flags are no longer toggleable — it records that this baseline was
generated on the corrected substrate.

**Integration risk:**

Touches the exact files 13.5 just landed (`store.py`, `transcript.py`, `observation/service.py`, `game.py`,
`beliefs.py`, `replay_loader.py`) and the committed-baseline tests — a missed OFF-branch deletion or a test
still asserting flag-OFF behavior breaks the suite. Sequence AFTER 14.7 (the baseline must be flags-ON first)
and 14.8 (the ablation must confirm no lever is harmful; if one is, STOP and escalate rather than silently
dropping it — the owner adopted all 4). The reconstruction must be byte-identical under a BARE environment
once the gates are removed — that is the acceptance bar; verify it explicitly.

**Ready-to-paste prompt:** `agent_prompts/task-14-9-substrate-default-on.md`
