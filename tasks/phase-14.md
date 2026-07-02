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
`(14.1 ∥ 14.2) → 14.3 → 14.4 → 14.4.1 → 14.5 → 14.6 → 14.7 → 14.8 → (14.9 ∥ 14.11) → 14.10 → 14.12`.
14.3 needs 14.1; 14.4 needs 14.1 + 14.3; 14.4.1 (adapter `enable_thinking` fix surfaced by the 14.4 sweep)
needs 14.1 + 14.4; 14.5 needs 14.2 + 14.4 + 14.4.1; 14.9 (flag-default cleanup) needs 14.8 (the ablation runs
on the toggles 14.9 deletes); 14.11 (qwen3_32b v4) needs only 14.8 and runs in PARALLEL with 14.9 (their one
shared file, orchestrator/game.py, is disjoint-region — registry line vs gate retirement); 14.10 (evidence-
quality lift fix) needs 14.8 + 14.9 and STAYS SEQUENTIAL behind 14.9 — both edit `substrate_flag_snapshot()`
and agents/memory/beliefs.py, and 14.10's byte-identity/offline-proof semantics differ pre- vs post-14.9;
14.12 (baseline 2, the phase close) needs 14.10 + 14.11.
Operator-run / spend gates: 14.4 (model sweep, $0 marginal), 14.7 (baseline 1 — DONE, measured ~5h with 2
parallel seed workers), and 14.12 (baseline 2, the final re-record).
Design-thread (no agent dispatch): 14.6 (lock decision). 14.8 is agent-dispatchable ($0 offline analysis + a
small loader override), with the audit's fix specs reviewed by the owner before 14.10/14.11 dispatch.
Track with `python3 scripts/compute_next_task.py --phase 14`.

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

AMENDED (owner decision 2026-07-01, after baseline 1 landed R1 27/50 / ejection accuracy 0.566): the phase
does NOT close on baseline 1. Its characterization (14.8) exposed an over-conviction defect class — the crew
railroad (the 10.1 lift cap defeated at 4× flag density; 3 innocents ejected) and measurable dialogue-craft
defects (greedy self-contradicting alibis, dead-target ballots, flat-1.0 confidences, template rationales) —
that the phase fixes IN-PHASE before the final record: (6) 14.10 closes the railroad-cap bypass behind a
default-OFF lever and 14.11 hardens the locked set to v4 against the measured defect counts; and (7) THE
FINAL CRITERION — baseline 2 (14.12) is re-recorded with the lever ON + v4, passes the same HARD validity
gate, RESTORES the railroad tripwire (zero railroaded crew rows), reports the per-defect deltas vs baseline 1,
and closes the phase. Baseline 1 remains the committed canonical set until 14.12 replaces it. Re-record cost
is measured, not estimated: ~5h for both 50-seed sets with 2 parallel seed workers (14.7 datapoint).

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
- experiments/lab/featherless_sweep.py (add a `--prompt-set` axis + a `prompt_set` result column so the set-vs-set A/B is self-describing; the driver renders through the loader bound to the selected set rather than the single import-time default — keep the existing default-set behavior unchanged when the flag is absent; non-Qwen sets now route through the real adapter, the 14.4.1 fix having retired the need for the harness `_bare_send`)
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
- [ ] A re-sweep over the SAME reconstructed contexts records each set's delta vs the pinned-9B prompts ON its own model (mechanical metrics + parse-success); the pinned `qwen3_5_9b` set is unchanged. The driver gains a `--prompt-set` axis and stamps a `prompt_set` column on every result row so the A/B is self-describing and reproducible (no manual run-tracking); the default-set behavior is byte-unchanged when the flag is absent so existing 14.4 rows still reproduce.
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
The 14.4 driver renders the prompts through the loader's module-level wrappers bound to the import-time
`AILIBI_PROMPT_SET` and writes one fixed results path with no set column — so a clean A/B needs a `--prompt-set`
axis that builds the renderers via `build_prompt_renderers(<set>)` (Task 14.2) and tags each row's
`prompt_set`; keep the no-flag path byte-identical so the committed 14.4 rows still reproduce. GLM / Cydonia
now route through the real adapter (`call_turn`) — the 14.4.1 fix retired the harness `_bare_send` for them, so
drop that branch for the non-Qwen sets rather than carrying the workaround into the re-sweep.

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

**LOCKED DECISION (owner, 2026-06-30) — GO:**
- **meeting_model = trigger_model = `Qwen/Qwen3-32B`** (homogeneous; qwen3_32b used for EVERYTHING — both call kinds).
- **prompt set = `qwen3_32b`** (the Task 14.5 bespoke set; registered `…​.qwen3_32b.v2`, selectable via `AILIBI_PROMPT_SET=qwen3_32b`).
- **mode = `non_thinking`** (the request-time thinking toggle OFF).
- **thinking policy = `fail_loud`** (non-thinking baseline expects NO reasoning channel; a populated one is an auditable error, not silently stripped).
- **response_format_mode = `json_object`** (the 14.1 live finding: strict `json_schema` 400s on the slate; `json_schema` stays selectable, no silent fallback).
- **substrate flags = all 4 13.5 levers ON** (`AILIBI_TESTIMONY_AS_CONTENT` / `AILIBI_WITNESSED_KILL_EVIDENCE` / `AILIBI_MOVEMENT_PERCEPTION` / `AILIBI_UNFREEZE_MEMORY`); 14.8's per-lever ablation is characterization (non-gating).
- **Evidence:** Qwen3-32B non-thinking on the qwen3_32b set is validity-clean — reply parse-success 16/16 (100%) on both substrates, vote conversion 8/8, ~27.1s/turn isolated (vs ~226.1s thinking, an ~8× time cost over a 50-seed × 2-format run). The mechanical self-co tell is mixed vs the pinned-9B prompts (an information-ceiling artifact, NOT a model gap — 14.4/14.8), so the recorded baseline is chosen on VALIDITY + latency, which non-thinking wins; the tell is scoped to Phase 15. The other four bespoke sets (incl. the strong-tell-reduction thinking set and GLM at 100% parse) stay available but unrecorded, for the Phase-15 heterogeneous-games task. NO validity NO-GO — proceed to the 14.7 smoke.

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

**STATUS (2026-07-01) — COMPLETE (PR #213).** The v3 re-smoke cleared the gate (parse 99.19%, ZERO
1024-truncations), both sets re-recorded on the locked tuple, HARD validity gate PASS, byte-identical
flag-aware reconstruction holds; the baseline is canonical. Headline: R1 eject-decided 27/50 (9B: 3/50),
impostor win 0.32 (9B: 0.84). Measured wall time: **~5h for both 50-seed sets with 2 parallel seed workers**
(each worker running the next available seed) — far under the 13–30h projection; use ~5h for future re-record
planning (14.12). Carried findings → 14.8: ejection accuracy 0.566, the 5-row crew railroad (10.1 cap defeated
at 4× flag density; tripwire downgraded to a regression pin), 23 missed-deadline markers. History below.

**STATUS (2026-06-30, historical) — infra landed; resumed at the re-smoke:**
- The 14.7 flag-stamping infrastructure is MERGED to main (PR #209): the MANIFEST `flags` column
  (`scripts/_manifest_writer.py`), the additive-optional substrate stamp on the replay `game_over` record
  (`orchestrator/replay.py`), the flag-aware loader guard (`api/replay_loader.py`,
  `ReplaySubstrateMismatchError`), and `scripts/refresh_samples.sh` Featherless support — which now FAILS LOUD
  before staging any seed unless the 14.6-locked substrate (`AILIBI_PROMPT_SET=qwen3_32b` + all 4 flags = `1`)
  is exported. So the re-record PR does NOT rebuild any of that; it produces the replay BYTES + regenerated
  reports/MANIFESTs/fixtures + re-pinned byte tests only.
- The FIRST smoke (2026-06-30, locked tuple) NO-GO'd: parse-success ~88.5% on a complete game (seed 0: 46/52),
  with 2 unterminated-JSON vote-cap truncations at the frozen 1024 cap + 4 schema-adherence failures. Root
  cause: the 14.4/14.5 sweep tested only reply+vote corpora (never the opening turns) and votes at a 4096-token
  budget, not the production 1024 cap — so it could not surface these. The `qwen3_32b` set was hardened to
  **v3** for full-game schema adherence + a compact-ballot fix (PR #209). The task now RESUMES at a re-smoke on
  v3; the bar to clear before the full re-record is parse-success ≈ 100% AND zero 1024-truncation.

**Files in scope:** (the atomic re-record PR only — the flag-stamping infra is already on main, PR #209)
- replays/samples/4p1i/ (50 replays + tournament-eval-report.json + MANIFEST.md re-recorded on the locked model, all 4 flags ON; model + prompt_versions + `flags` + git_sha rows updated)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded, all 4 flags ON; roster sidecar {9,2,2} unchanged)
- tests/fixtures/prompt_regression/ (v_a + v_b fixtures + baseline.json regenerated — provider + substrate + prompt set changed)
- tests/api/test_replay_loader.py (committed-set BYTE pins re-verified on the new recordings)
- tests/eval/test_win_condition_selfcheck.py (committed-set pins re-verified on the new bytes)
- tests/scripts/test_manifest_writer.py (MANIFEST row pins for the locked model + `qwen3_32b.v3` prompt_versions + the new `flags` cell)

**Files NOT in scope:**
- the 14.7 flag-stamping infra — `scripts/_manifest_writer.py` (flags column), `orchestrator/replay.py` (stamp), `api/replay_loader.py` (guard) — plus `scripts/refresh_samples.sh` Featherless support + the locked-substrate preflight guard + their behavior tests: ALL LANDED on main (PR #209); the re-record CONSUMES them, it does not re-edit them
- engine/ + meetings/ + agents/ + llm/ + eval/ source (behavior landed in 14.1 / 14.5; this records + regenerates only)
- meetings/manager.py (token caps FROZEN — turn 2048 / vote 1024; do NOT raise; the 9.5 ctx-overrun lesson)
- agents/strategic/prompts/ (no template authoring here; this records the chosen prompt set, it does not edit it)
- the 13.5 flag-source logic (the `*_enabled()` resolvers + flag gates) — 14.7 sets the flags ON via env + STAMPS the config; it does NOT change the flag logic (default-ON + retiring the OFF path is 14.9)
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel; do not modify)

**Definition of done:**
- [ ] RE-smoke first (3–5 seeds at 9p2i) on the `qwen3_32b` **v3** set — the FIRST smoke NO-GO'd at ~88.5% parse: thinking policy holds under `fail_loud`, structured-output parse-success ≈ 100%, per-seed wall time + full-run projection reported BEFORE the full runs; STOP for operator go. ABANDON without recording if parse-success craters or the guard trips — iterate the `qwen3_32b` prompts (as v3 already did) or re-open 14.6; do NOT weaken the guard or raise the caps.
- [ ] Re-smoke confirms the floor on v3: every smoke seed reaches game_over with ZERO ballot truncation / unterminated-JSON parse failures under the FROZEN caps (the exact failure the first smoke hit — 2 vote-cap truncations at 1024, now targeted by v3's compact-ballot fix).
- [ ] Both sets re-recorded in ONE PR on the locked model + `qwen3_32b.v3` prompt set with all 4 13.5 substrate flags ON; both reports + MANIFESTs regenerated (the LANDED infra stamps model + prompt_versions + the `flags` column + new git_sha, and the flag config into the replay `game_over` metadata); prompt-regression fixtures + baseline regenerated; byte-identical reconstruction holds from the new recordings.
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
`FEATHERLESS_API_KEY` + `AILIBI_PROMPT_SET=qwen3_32b` PLUS all 4 substrate flags
(`AILIBI_TESTIMONY_AS_CONTENT=1 AILIBI_WITNESSED_KILL_EVIDENCE=1 AILIBI_MOVEMENT_PERCEPTION=1
AILIBI_UNFREEZE_MEMORY=1`) on every `scripts/refresh_samples.sh` invocation; the locked model
`Qwen/Qwen3-32B` for both meeting and trigger call kinds (14.6), request-time thinking OFF, `fail_loud`.
`refresh_samples.sh` now ENFORCES exactly this tuple at preflight (PR #209): a real Featherless run aborts $0
before staging if `AILIBI_PROMPT_SET` ≠ `qwen3_32b` or any of the 4 flags ≠ `1`, so a mis-set env fails loud
instead of recording the wrong baseline.
ONE atomic PR — an intermediate commit is un-reconstructable. Time expectation (measured, 14.4/14.6): Qwen3-32B
non-thinking is ~27.1s/turn isolated — roughly 2× the local 9B's per-call latency, offset by the plan's 32B
concurrency cap of 2 (a 32B request = 2 of 4 units), so the full 50-seed × 2-format re-record lands in the
SAME ~13–30h ballpark as the 9B (the win is offloading the operator's machine, NOT wall-clock); do NOT assume
"far faster." The smoke (3–5 seeds) MUST project the real wall time before the full run. (MEASURED OUTCOME,
2026-07-01: the projection was over — the run took ~5h for both sets with 2 parallel seed workers each pulling
the next available seed; seed-level parallelism amortizes the per-turn latency. Plan future re-records at ~5h.) The report regeneration +
MANIFEST update + fixture refresh all happen through `scripts/build_sample_report.py` +
`scripts/_manifest_writer.py` (which already emits the `flags` column, PR #209) exactly as the 9.5 operator
workflow documents. Hosted non-determinism means FRESH generation won't byte-reproduce, but the recordings replay
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
a degraded baseline through. The FIRST smoke already exercised this gate as designed — it NO-GO'd at ~88.5%
parse (vote-cap truncations + opening-turn schema failures the narrow sweep never covered), which drove the
`qwen3_32b` → v3 hardening (PR #209). That is the gate working, not a phase failure; the re-smoke on v3 must
clear ≈ 100% parse + zero 1024-truncation before the full run, and a second NO-GO means iterate the prompts
again — never raise the caps.

**Ready-to-paste prompt:** `agent_prompts/task-14-7-rerecord.md`

### Task 14.8 — Characterize baseline 1 (R-gate as measurement) + fix recommendations
**Branch:** `phase-14-baseline-characterize-close`
**Depends on:** 14.7
**Section refs:** audits/audit-2026-06-25-0859-phase-13-close.md (the R-gate definition); tasks/phase-13.md (R1/R4/R7 + impostor win rate + rubric geomean); eval/meeting_quality.py; experiments/lab/rubric_score.py; PR #213 (baseline-1 findings)
**Complexity:** Medium

Design-thread characterization (the phase CLOSE moves to 14.12, after the evidence-quality fixes and the
baseline-2 re-record). The headline is already known: R1 eject-decided **27/50** vs the 9B's 3/50, impostor
win 0.32 vs 0.84 — the new model DRIVES the corrected substrate, so the Phase-13 information-ceiling
hypothesis is REVISED, not confirmed: the ceiling bound impostor CONCEALMENT (the 14.4 tell persists) but the
live binding constraint was crew CONVERSION, and that broke. The problem has INVERTED to OVER-conviction:
ejection accuracy 0.566 (~43% of ejections take out crew), a 5-row crew railroad (2–9 stacked same-meeting
contradiction flags defeat the Phase-10.1 lift cap at the new model's 4× flag density; 3 innocents ejected —
the downgraded tripwire in `tests/meetings/test_manager.py` pins the exact set), and dialogue-level
self-sabotage measured on the committed bytes: ~10% of self-alibis are contradicted by the speaker's OWN
same-turn task observation (greedy tick spans — the railroad's fuel), 47/891 ballots guard-normalized (invalid
dead targets / bad `primary_reason_id`), 64 accusations at confidence 1.0, 33% of ballots sharing one literal
rationale template, 23 missed-deadline turns. This task: (1) compute the full R-gate measurement (R1, R4
floor, R7, impostor win rate, rubric geomean) vs the final-9B baseline; (2) quantify how much of R1=27
survives DISCOUNTING the railroad rows (genuine deduction vs pile-on); (3) run the per-lever ablation of the
4 substrate flags (offline, $0; kill-scene fired 0× in the 9B smoke — UNMEASURED, not negative); (4) write
the characterization audit whose deliverable is the CONCRETE fix specs for 14.10 (the 10.1 cap defeat —
diagnose the exact bypass mechanism) and 14.11 (the v4 prompt fixes, with the per-defect counts above as the
baseline the re-record must beat).

**STATUS (2026-07-02) — MEASURED (audit: `audits/audit-2026-07-01-phase-14-baseline1-characterization.md`).**
R-gate on baseline 1 (9p2i): R1 **27/50** (9B 3/50), R4 wrong-ejection games **39** (9B 4 — the inversion
headline), impostor win **0.32** (floor ✓), R7 **43/152 (28%)** (9B 13/195), geomean eject-decided median
61.3 vs stopwatch max 43.5 with 25/27 above every stopwatch (the 2 exceptions are the rubric's own railroad
floor firing — seeds 12/21 at 0.0). **Railroad-discounted R1 = 25/50** (only seeds 13/16 of the 27 run
through a pinned railroad meeting). Hypothesis verdict: REVISED as charted — the ceiling bound concealment,
conversion OVERSHOT into over-conviction (ejection accuracy 0.566). Cap-bypass diagnosis (exact fold
reproduction, 2482/2482 recorded render rows matched): the 10.1/13.14 caps HOLD — one STRONG
`alibi_vs_sighting` lift-key group saturates the +0.30 budget and gate-crosses the WHOLE roster at 0.80,
and the pre-13.5 Rule-1 body-proximity prior (0.70) compounds to the 1.00 clamp for at-scene voters
(impostors, in all 5 pinned rows); fuel = factually-false testimony (97–100% of flagged ejectee alibis
false vs engine truth; 47–67% of refuting sightings false). Per-lever ablation committed
(`experiments/lab/results-substrate-ablation.jsonl`): no lever harmful, none causes the railroad (5 rows in
every cell) — **14.9 default-ON set confirmed**; kill-scene detector fired 1×/152 meetings (effectively
UNMEASURED, not negative); unfreeze verified 554/554 on recorded bytes. **Confirmed 14.10 targets:**
certain-guilt exclusion (transient flag lift never renders 1.0 absent first-hand conclusive evidence) +
sloppy-testimony downgrade (self-refuted alibi group → WEAK delta; 0/57 impostor vs 6/31 crew flagged
ejections — zero conversion cost); witness-count weighting and ≥2-strong-group gating are measured
ANTI-signals (do not implement). **Confirmed 14.11 targets (the counts v4 must beat):** 30/295 (10.2%)
self-contradicted self-alibis, 27 invalid-target + 20 invalid-reason-id ballots (= the 47 guard-normalized),
64/505 conf-1.0 accusations, 320/891 (35.9%) "p-N's alibi …" template-family rationales, 23 missed-deadline
turn markers (all 27 `deadline_default` rows validation-triggered — output discipline, caps stay FROZEN).

**Files in scope:**
- audits/audit-2026-07-01-phase-14-baseline1-characterization.md (new: the R-gate measurement + railroad-discounted R1 + the per-lever ablation + the REVISED hypothesis verdict + the 14.10/14.11 fix specs)
- api/replay_loader.py (a small ANALYSIS-ONLY override on the reconstruction entry — e.g. `allow_substrate_mismatch: bool = False` threaded to `_assert_substrate_matches` — because the per-lever ablation DELIBERATELY re-derives the stamped all-ON baseline under toggled levers, which the Task-14.7 guard otherwise correctly refuses; default False so the serving/verify paths keep failing loud, additive only)
- experiments/lab/results-substrate-ablation.jsonl (new: per-lever ablation — each of the 4 flags toggled offline over the baseline replays via the override, R-gate / conversion metrics per cell, each row recording that the mismatch was deliberate; $0)
- tasks/phase-14.md (a STATUS banner recording the measurement outcome and the confirmed 14.10/14.11 targets)
- experiments/lab/report-rubric-interestingness.md (re-ranked offline — data regen; the score json was already regenerated by the 14.7 refresh)
- tests/api/test_replay_loader.py (the override: default-off keeps the guard firing; True permits the mismatch; no other loader behavior change)

**Files NOT in scope:**
- llm/ + agents/ + meetings/ + engine/ (no behavior change here beyond the loader's opt-in analysis override; the fixes are 14.10/14.11)
- replays/samples/ (the 14.7 bytes are baseline 1; this READS them)
- eval/ source (the analyzers are reused as-is; this folds, it does not change them)

**Definition of done:**
- [ ] The R-gate is computed offline over the 14.7 flags-ON baseline (R1, R4 floor, R7, impostor win rate, rubric geomean ranking) and compared to the final-9B baseline (R1 3/50, impostor 84%, eject 9%).
- [ ] The railroad-discounted R1 is computed (R-gate with the 5 pinned railroad rows' meetings discounted) so 14.12 can tell genuine-deduction gains from pile-on gains.
- [ ] A per-lever ablation (each of the 4 13.5 flags toggled offline over the baseline replays) characterizes each lever's contribution and confirms the 14.9 default-ON set; the kill-scene flag's 0× firing is noted as UNMEASURED (needs a richer scenario), not a negative result. THIS TASK IS THE LAST CHANCE to run it: 14.9 deletes the very toggles the ablation flips — the ablation must be complete and committed before 14.9 dispatches.
- [ ] The analysis-only substrate-mismatch override is added to the loader (default OFF — the serving/verify paths still fail loud; the ablation harness passes it explicitly) with a test for both positions; no other reconstruction behavior changes.
- [ ] The audit states the REVISED hypothesis verdict honestly: the ceiling bound concealment, not conversion; the live problem is now over-conviction (ejection accuracy 0.566) — with the evidence for each claim.
- [ ] The audit specifies the 14.10 fix (the exact mechanism by which ≥2 same-meeting flags defeat the 10.1 cap, from the pinned rows) and the 14.11 targets (the measured per-defect counts: 10% self-contradicted alibis, 47 guard-normalized ballots, 64 conf-1.0 accusations, 33% template rationales, 23 missed-deadline turns).
- [ ] The rubric interestingness report is re-ranked offline over the committed replays ($0, no code change); no number is retrofit to pass.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Pure offline folds over the new `TournamentReport`: `eval/vote_correctness.py` (`ejection_accuracy`,
`compute_genuine_class_conversion`), `eval/accusation_calibration.py` (ECE), `eval/alibi_fabrication.py`
(survival_rate), assembled by `eval/meeting_quality.py`, plus the rubric geomean from
`experiments/lab/rubric_score.py` — all $0, no provider. The 5 railroad rows to discount are pinned in
`tests/meetings/test_manager.py` (`known_railroad`: seed-13 m0 p-7, seed-16 m0 p-6, seed-28 m0 p-3/p-6,
seed-44 m1 p-1); seed-44 m1 is the worked example of the fuel — crew p-1's greedy alibi (`CAFETERIA t5-14`
spanning their own recorded `STORAGE t14` task) minted the contradictions the pile-on ran on. The ablation
mechanics: the baseline replays are STAMPED all-ON, and `api/replay_loader.py:_assert_substrate_matches`
(correctly) refuses a mismatched re-derivation — so add the analysis-only override FIRST (a keyword threaded
from the reconstruction entry at `replay_loader.py:717`, default False), then toggle one lever at a time via
env for the ablation cells. Run the full-suite ablation BEFORE 14.9 lands (14.9 deletes the toggles). The
framing is the deliverable: the audit's job is a MEASUREMENT plus two actionable fix specs, so 14.10/14.11
dispatch against precise targets instead of vibes. Do not retrofit any number.

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
- api/replay_loader.py (reconstruction no longer reads the flags — the corrected derivation is unconditional; the substrate-mismatch guard stays coherent for legacy stamped replays)
- orchestrator/replay.py (`substrate_flag_snapshot()` lazy-imports the four `*_enabled()` resolvers this task deletes — rework it to report the retired levers as unconditionally ON, keeping the stamp machinery generic for future levers like 14.10's)
- tests/ (the flag-OFF byte-identity / flag-toggle tests across tests/agents/ + tests/meetings/ + tests/observation/ + tests/orchestrator/ retargeted onto the flags-ON baseline)
- scripts/refresh_samples.sh (the locked-substrate preflight guard drops the four retired flag requirements — after this task those env vars no longer exist, and a guard demanding them would fail every Featherless refresh; the `AILIBI_PROMPT_SET=qwen3_32b` requirement stays)
- .env.example (remove the now-defunct flag knobs)

**Files NOT in scope:**
- replays/samples/ (the 14.7 flags-ON bytes ARE the baseline; this changes no replay)
- agents/strategic/prompts/ (the prompt sets are 14.2/14.5)
- llm/ (the provider is 14.1)
- scripts/_manifest_writer.py (the `flags` column from 14.7 stays as provenance even though the flags are no longer toggleable)

**Definition of done:**
- [ ] The 4 adopted levers are DEFAULT behavior (the `*_enabled()` env gates default-ON or removed); the now-dead flag-OFF branches and env constants are deleted, not left vestigial.
- [ ] The committed flags-ON baseline (14.7) reconstructs byte-identically WITHOUT any env vars set (`scripts/verify_samples.sh` under a bare environment); the MANIFEST/replay `flags` stamp reads "all 4 ON" and is consistent with the now-unconditional behavior.
- [ ] `orchestrator/replay.py`'s `substrate_flag_snapshot()` no longer imports the retired resolvers (the four levers report unconditionally ON); the loader's substrate-mismatch guard still validates legacy stamped replays; the stamp machinery stays generic so 14.10 can register its new lever.
- [ ] The spectator serves the committed baseline under a BARE environment: `ReplayLoader(replay_dir=replays/samples/9p2i).load_replay(...)` succeeds with no `AILIBI_*` vars set (this closes the known `run_spectator.sh` 500 — the stamped all-ON baseline vs the launcher's bare env — reported 2026-07-01; a test pins it).
- [ ] The `refresh_samples.sh` Featherless preflight no longer demands the retired flag env vars (the prompt-set requirement stays); its guard test is updated accordingly.
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
generated on the corrected substrate. Note the tail of the phase: 14.12 re-records baseline 2 after the
14.10/14.11 fixes and re-pins the byte tests once more — keep this task's retargeting mechanical so that
second re-pin is cheap.

**Integration risk:**

Touches the exact files 13.5 just landed (`store.py`, `transcript.py`, `observation/service.py`, `game.py`,
`beliefs.py`, `replay_loader.py`) and the committed-baseline tests — a missed OFF-branch deletion or a test
still asserting flag-OFF behavior breaks the suite. Sequence AFTER 14.7 (the baseline must be flags-ON first)
and 14.8 (the ablation must confirm no lever is harmful; if one is, STOP and escalate rather than silently
dropping it — the owner adopted all 4). The reconstruction must be byte-identical under a BARE environment
once the gates are removed — that is the acceptance bar; verify it explicitly.

**Ready-to-paste prompt:** `agent_prompts/task-14-9-substrate-default-on.md`

### Task 14.10 — Evidence-quality lift fix: certain-guilt ceiling + self-refuted-alibi downgrade (default-OFF lever)
**Branch:** `phase-14-evidence-quality-lift`
**Depends on:** 14.8, 14.9
**Section refs:** audits/audit-2026-07-01-phase-14-baseline1-characterization.md §3/§3a (the MEASURED mechanism + the two-bound fix spec — read it first, it overturned the original framing); tests/meetings/test_manager.py (the pinned 5-row railroad set = the reproduction corpus); agents/memory/beliefs.py (the 13.14 joint cap this extends); tasks/phase-13-5.md (the default-OFF-lever + stamp pattern this task reuses)
**Complexity:** Integration

Fix the crew-railroad defect per the MEASURED 14.8 diagnosis (audit §3 — which OVERTURNED the original
flag-density framing: the 10.1/13.14 caps HOLD; even seed-44's 9 flags dedup to ONE `contradiction_lift_key`
group capped at +0.30, so flag COUNT is a signature, not the causal variable). The real mechanism compounds:
one saturated strong group lands +0.30 in EVERY voter's graph in lockstep (0.50 → 0.80 ≥ the 0.60 gate = a
roster-wide must-vote on the flagged subject), and the voters carrying the Phase-10 Rule-1 body-proximity
prior (0.70) clamp to certain-guilt 1.00 — in all 5 pinned rows the 1.00-renderers are the impostors.
Implement the audit's TWO measured bounds behind a NEW default-OFF env lever (the 13.5 pattern): (1)
CERTAIN-GUILT EXCLUSION — extend the 13.14 joint cap to `min(lifted, prior + 0.3, CONTRADICTION_RENDER_CEIL)`
(just below the clamp, e.g. 0.97) for flag/testimony-driven lift, EXEMPTING first-hand conclusive observation
(a witnessed kill legitimately reads ~1.0); zero conversion cost — every 0.97 stays a must-vote. (2)
SELF-REFUTED-ALIBI DOWNGRADE — a contradiction group whose refuted alibi is contradicted by the subject's OWN
same-turn `completed_task` observation contributes the WEAK delta (0.08), not STRONG (0.30); measured cost on
baseline 1: 0/57 flagged impostor ejections, while keeping seed-16/44's rosters sub-gate. The audit REJECTS
two tempting shapes BY MEASUREMENT — do NOT implement witness-count weighting (an anti-signal: honest greedy
alibis attract MORE independent refuting witnesses than impostor lies) or ≥2-group gating (over-damps: 54/57
flagged impostor ejections ride exactly ONE group). The change alters belief re-derivation, so gate it
default-OFF: OFF preserves baseline-1 byte-identity and every committed-bytes test; 14.12 records baseline 2
with the lever ON and stamps it. Register the lever in the `substrate_flag_snapshot()` stamp machinery (kept
generic by 14.9) so the recording self-describes.

**Files in scope:**
- agents/memory/beliefs.py (the render-ceiling extension of the 13.14 joint cap + the self-refuted-alibi WEAK downgrade, behind the new `*_enabled()` resolver; the existing caps are extended, not rewritten)
- orchestrator/replay.py (register the new lever key in `SUBSTRATE_FLAG_KEYS` / `substrate_flag_snapshot()` so 14.12's recording stamps it — additive)
- .env.example (document the new default-OFF lever)
- tests/agents/test_beliefs.py (unit tests: a synthetic 9-flag same-meeting stack renders BELOW certain-guilt with the lever ON; byte-identity of the fold with it OFF; evidence-class weighting cases if implemented)
- tests/orchestrator/test_replay.py (the stamp round-trips the new lever)

**Files NOT in scope:**
- replays/samples/ (baseline 1 is untouched; the lever defaults OFF so it still byte-verifies — the re-record is 14.12)
- tests/meetings/test_manager.py (the railroad regression pin walks baseline-1 bytes and stays green as-is; RESTORING it to a tripwire happens at 14.12 when the bytes change)
- agents/strategic/prompts/ (the prompt-side fuel fix is 14.11)
- meetings/transcript.py detector logic (flags are still DETECTED the same; this task changes how the belief fold WEIGHS them)

**Definition of done:**
- [ ] Bound 1 (certain-guilt exclusion): with the lever ON, NO flag/testimony-driven lift can render at the 1.0 clamp — unit tests cover BOTH 1.0 paths from the audit: the neutral-prior case (0.50 + saturated 0.30 → 0.80, unchanged) and the compounding case (body-proximity prior 0.70 + 0.30 → CEILS at ~0.97, not 1.00); a first-hand witnessed-kill pin still renders ~1.0 (the exemption).
- [ ] Bound 2 (self-refuted-alibi downgrade): a contradiction group whose refuted alibi is contradicted by the subject's OWN same-turn `completed_task` observation contributes WEAK (0.08) not STRONG (0.30), with tests for the self-refuted and not-self-refuted cases.
- [ ] The offline proof over baseline-1 bytes (via the 14.8 `allow_substrate_mismatch` override): all 5 pinned railroad rows render below 1.0 with the lever ON, AND the seed-44 m0 true-impostor catch still gate-crosses (the over-damping canary).
- [ ] With the lever OFF (the default), the belief fold is byte-identical to pre-task behavior: committed baseline-1 reconstructs byte-identically and every committed-bytes test stays green unmodified.
- [ ] The REJECTED shapes are absent: no witness-count weighting, no ≥2-group gating (audit §3a rejected both by measurement — a reviewer finding either is a contract violation, not an improvement).
- [ ] The new lever is registered in `substrate_flag_snapshot()` / `SUBSTRATE_FLAG_KEYS` and round-trips through the replay stamp + MANIFEST `flags` cell (so the 14.12 recording self-describes).
- [ ] `.env.example` documents the lever as default-OFF pending the 14.12 baseline-2 re-record.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.memory.beliefs.evidence_quality_lift_enabled

**Implementation hint:**

Read audit §3/§3a FIRST — it reproduced the production fold exactly (2482/2482 recorded vote-prompt rows) and
its spec is measured, not hypothesized. Both bounds are small extensions at the 13.14 joint-cap site in
`agents/memory/beliefs.py`: bound 1 adds a third term to the min (`CONTRADICTION_RENDER_CEIL`, ~0.97, applied
only to flag/testimony-driven lift — the first-hand witnessed-kill pin path stays exempt); bound 2 needs the
self-refutation signal at fold time, which is mechanically derivable from the transcript (the subject's own
same-turn `completed_task` room/tick inside the refuted alibi span — the same check the audit ran). The 13.5
lever pattern is the template for the gate: a module constant `ENV_EVIDENCE_QUALITY_LIFT` + an
`evidence_quality_lift_enabled()` resolver read ad-hoc from `os.environ`, OFF branch byte-identical. Prove the
fix offline before 14.12 spends: re-derive the 5 pinned railroad meetings from baseline-1 bytes with the lever
ON and confirm every pinned row renders below 1.0 AND the seed-44 m0 true-impostor catch still converts. Note
the stamp: baseline 1's stamp lacks the new lever key, so re-deriving with it ON is a substrate mismatch — use
the 14.8 analysis-only override (`allow_substrate_mismatch=True`) for exactly this comparison; that is what it
exists for.

**Integration risk:**

This is a belief-fold change on the exact code path 13.5/14.9 just reshaped — the OFF-branch byte-identity
bullet is the guard against regressing the committed baseline; run `scripts/verify_samples.sh` (bare env)
before and after. Do NOT weaken the §4.6 vote gate or the detectors to make the numbers move — the fix is in
the FOLD's weighting, so genuine multi-witness evidence must still convict (the seed-44 m0 TRUE-impostor
catch, driven by real cross-referencing, must still convert with the lever ON; add it as a fixture if cheap).
Over-damping is the failure mode to watch: if the lever ON drops genuine-class conversion materially in the
14.12 smoke, the bound is too tight — iterate the weighting, do not ship a crew that can't convict.

**Ready-to-paste prompt:** `agent_prompts/task-14-10-evidence-quality-lift.md`

### Task 14.11 — qwen3_32b v4: alibi discipline, ballot craft, and voice (the measured-defect batch)
**Branch:** `phase-14-qwen3-32b-v4`
**Depends on:** 14.8
**Section refs:** audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the per-defect counts + targets); agents/strategic/prompts/qwen3_32b/ (the v3 set); meetings/schemas.py (the frozen output contract); replays/samples/9p2i/replay-seed-44.jsonl (the worked railroad-fuel example)
**Complexity:** Medium

Harden the locked `qwen3_32b` set v3 → v4 against the six defects MEASURED on baseline 1, so baseline 2's
dialogue is both more correct and more watchable. The fixes, each tied to its measured count: (1) ALIBI
DISCIPLINE — the alibi must match the speaker's own memory rows exactly, never spanning rooms they moved
between (10% of self-alibis were contradicted by the speaker's OWN same-turn task observation — the greedy
spans that fuel the railroad; seed-44 m1 p-1 is the worked example); (2) DEAD-ROSTER SALIENCE — move the
do-not-accuse/vote list adjacent to target selection with an explicit "naming an ejected/dead player wastes
your vote" (27 invalid-target ballots); (3) a REAL `turn_id` worked example for `primary_reason_id` — copy a
turn id verbatim from the transcript lines (20 invalid-id nulls); (4) CONFIDENCE CALIBRATION — a rubric (1.0
only for a first-hand witnessed kill; ~0.7 corroborated; ~0.5 hunch; 64 accusations sat at 1.0); (5)
OBSERVATION CURATION — put the 3–5 most probative observations on the record, not the whole movement log
(30+-row dumps bloat turns and feed the 23 missed-deadline rambles); (6) VOICED RATIONALE — the ballot
rationale states the argument in the agent's own words, referencing the specific turn that convinced them (33%
of ballots shared one literal template sentence). The output JSON schema is FROZEN (the same-schema
invariant); only instruction prose and examples change. In-place template edits are SAFE for baseline-1
byte-identity — reconstruction replays RECORDED prompt bytes and never re-renders templates (the 14.2
determinism contract); recorded `prompt_versions` rows stay `…​.v3` while the registry moves to v4 for future
recordings.

**Files in scope:**
- agents/strategic/prompts/qwen3_32b/crewmate_report.j2 (fixes 1, 4, 5; header → v4)
- agents/strategic/prompts/qwen3_32b/impostor_report.j2 (fixes 1, 4, 5; header → v4)
- agents/strategic/prompts/qwen3_32b/accusation_round.j2 (fixes 1, 2, 4, 5; header → v4)
- agents/strategic/prompts/qwen3_32b/vote_ballot.j2 (fixes 2, 3, 6; header → v4)
- orchestrator/game.py (registry bump ONLY: `qwen3_32b` → `_bespoke_versions("qwen3_32b", version="v4")` — one line at the PROMPT_VERSION_SETS registry, disjoint from the gate-retirement region 14.9 edits at `:714-735`; this task may run in PARALLEL with 14.9, whichever merges second rebases this trivially)
- tests/agents/test_bespoke_prompt_sets.py (render + cross-set parse stay green; add pins for the new directives — alibi-discipline present, dead-roster adjacency, confidence rubric — mirroring the cover-directive gating pins)

**Files NOT in scope:**
- the other bespoke sets + `qwen3_5_9b/` (frozen; this iterates ONLY the locked set)
- replays/samples/ (recorded v3 bytes verify unchanged; baseline 2 is 14.12)
- meetings/schemas.py + the graders (the output contract is the invariant)
- llm/ + agents/memory/ (the belief-side fix is 14.10)

**Definition of done:**
- [ ] All six measured defects are addressed in the templates, each traceable to its 14.8 count (the audit's targets are quoted in the template header comments where the directive lands).
- [ ] The registry maps `qwen3_32b` → v4; template headers read v4; recorded baseline-1 rows (…​.v3) are untouched and `scripts/verify_samples.sh` stays green on the committed sets (reconstruction replays recorded bytes — prove it, don't assume it).
- [ ] Every template renders under `StrictUndefined` with the existing loader kwargs; the cross-set parse check holds; the cover directive stays gated on `is_impostor`; the anti-meta-leak directive is preserved.
- [ ] A cheap offline validation pass runs the v4 set over reconstructed contexts (the 14.5 `--prompt-set` harness) and reports parse-success + the mechanical grades vs the v3 rows — a regression in either is a stop-and-iterate, not a ship.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Iterate on the v3 bodies (this is a hardening pass, not a ground-up rewrite — v3's response-shape checklist
and worked examples fixed the smoke failures; keep them). Fix 1 is the highest-leverage line in the phase
tail: the alibi bullet should read like "your `alibi` must quote your own memory exactly — one room, the tick
range you were ACTUALLY there; if you moved during the window, alibi only the room you were in at the relevant
tick; a range that spans rooms you moved between contradicts your own record and gets you ejected." For fix 6,
give two contrasting example rationales (one evidence-citing, one gut-read) so the model stops converging on a
single template sentence. Watch fix 5 vs the graders: curation must not drop the found_body/saw observations
`eval/vote_correctness.py` reads off the opening turn — say "always include the body report and the sightings
naming your suspect." Validate with `AILIBI_PROMPT_SET=qwen3_32b` + the featherless_sweep `--prompt-set`
axis on the same pinned contexts (operator, $0, fast); the LIVE proof is 14.12's smoke.

**Ready-to-paste prompt:** `agent_prompts/task-14-11-qwen3-32b-v4.md`

### Task 14.12 — Baseline 2: atomic re-record on the evidence-quality lever + v4 prompts + phase close
**Branch:** `phase-14-baseline-2-rerecord`
**Depends on:** 14.10, 14.11
**Section refs:** tasks/phase-14.md §14.7 (the proven smoke → re-record → validity-gate shape + the landed stamp infra); audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the targets baseline 2 must beat); scripts/refresh_samples.sh; tests/meetings/test_manager.py (the railroad pin to RESTORE to a tripwire)
**Complexity:** Integration

Operator-run spend/time gate, and the PHASE CLOSE. Re-record BOTH committed sets (50 × 4p1i + 50 × 9p2i) on
the locked tuple + the v4 prompt set + the 14.10 evidence-quality lever ON (stamped; the four 13.5 levers are
unconditional after 14.9), in ONE atomic PR, exactly the 14.7 shape: smoke first (3–5 seeds at 9p2i; parse
≈ 100%, zero 1024-truncation, wall-time projection — measured 14.7 datapoint: ~5h for both sets with 2
parallel seed workers), STOP for operator go, then the full runs, the HARD validity gate, and byte-identical
flag-aware reconstruction. Baseline 2 replaces baseline 1 as canonical. BECAUSE the fixes were specified
against measured defects, this close also measures them: restore the railroad REGRESSION PIN to the original
TRIPWIRE (zero crew rows at 1.0 from same-meeting flag stacks), and report the per-defect deltas vs baseline 1
(ejection accuracy vs 0.566, self-contradicted alibis vs 10%, guard-normalized ballots vs 47, conf-1.0
accusations vs 64, template-rationale share vs 33%, missed-deadline vs 23) plus the re-measured R-gate. The
honest R1 anchor is the RAILROAD-DISCOUNTED baseline-1 figure (25/50, audit §2 — the pinned rows accounted
for only 2 of the 24-game lift), not raw 27/50; and per audit §2 the stacked-flag signature is role-blind
(46% of impostor ejections carry it too), so "fewer stacked-flag convictions" alone is NOT a success metric.
Better CONVICTIONS, not just more: R1 holding near 25 with ejection accuracy up from 0.566 is the win
condition; R1 collapsing means 14.10 over-damped (stop, iterate the weighting, re-smoke — never weaken the
gate). Also report whether the 22 zero-flag crew mis-ejects (audit §7, untouched by 14.10's lever) moved
under v4's calibration/curation fixes. Close the phase with the final audit + STATUS banner.

**Files in scope:**
- replays/samples/4p1i/ (50 replays + report + MANIFEST re-recorded; `flags` rows now stamp the 14.10 lever)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster sidecar unchanged)
- tests/meetings/test_manager.py (the railroad pin RESTORED to the zero-railroad tripwire on the new bytes)
- tests/ committed-bytes pins (the #213-style mechanical re-pin across the byte-coupled tests — value pins re-derived, coordinates re-anchored property-preservingly)
- scripts/refresh_samples.sh (the locked-substrate preflight guard updated to require the 14.10 lever ON alongside the existing tuple)
- audits/audit-phase-14-close.md (new: the phase-close audit — per-defect deltas, the re-measured R-gate, the honest verdict + Phase 15 recommendation)
- tasks/phase-14.md (final STATUS banner: phase CLOSED on baseline 2)

**Files NOT in scope:**
- engine/ + meetings/ + agents/ + llm/ + eval/ source (behavior landed in 14.10/14.11; this records + regenerates + re-pins only)
- meetings/manager.py token caps (FROZEN — turn 2048 / vote 1024, unchanged through the whole phase)
- agents/strategic/prompts/ (v4 landed in 14.11; recording only)
- tests/fixtures/prompt_regression/ (stays frozen — the self-contained two-version A/B harness, per the #213 decision)

**Definition of done:**
- [ ] Smoke first (3–5 seeds at 9p2i, lever ON + v4): thinking policy holds, parse-success ≈ 100%, zero ballot truncation, genuine-class conversion has NOT collapsed (the 14.10 over-damping check), wall-time projection reported; STOP for operator go.
- [ ] Both sets re-recorded in ONE atomic PR on the locked tuple + v4 + the 14.10 lever ON; MANIFESTs/reports regenerated; the `flags` stamp records the lever; byte-identical flag-aware reconstruction holds.
- [ ] HARD validity gate passes (the 14.7 criteria: friendly-fire 0, all game_over, betrayal 0, leak suite green, meeting_rate ≥ 0.60 with ≥ 30 resolved at 9p2i, zero tick-1 kills, zero dangling primary_reason_id, cost rows 0, provenance rows exact).
- [ ] The railroad TRIPWIRE is restored (zero crew rows at 1.0 from ≥2 same-meeting flags on the new bytes) — the regression-pin era ends with the defect, not around it.
- [ ] The close audit reports the per-defect deltas vs baseline 1 (ejection accuracy / self-contradicted alibis / guard-normalized ballots / conf-1.0 accusations / template-rationale share / missed-deadline count) and the re-measured R-gate vs baseline 1 AND the 9B — no number retrofit.
- [ ] The phase STATUS banner records the close; the audit recommends Phase 15 (persona/voice layer; tactical/ML between-meeting play) with the evidence for each.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The operator env is the 14.7 recipe plus the new lever: `AILIBI_LLM_PROVIDER=featherless` +
`FEATHERLESS_API_KEY` + `AILIBI_PROMPT_SET=qwen3_32b` + `AILIBI_EVIDENCE_QUALITY_LIFT=1` (the four 13.5 vars
are gone after 14.9 — the substrate is unconditional). Update the refresh-script preflight guard to require
the lever alongside the prompt set BEFORE any seed stages (the same fail-loud shape PR #209 added). Run the
two sets with 2 parallel seed workers — the measured 14.7 wall time was ~5h total; smoke-project anyway. The
per-defect delta measurements are cheap offline folds over the new bytes (the same greps/folds 14.8
documented); put them in the close audit next to their baseline-1 numbers. The #213 PR is the template for
the mechanical test re-pin — expect the same byte-coupled test files; re-anchor property-preservingly and say
so per test.

**Integration risk:**

The phase's final spend gate, with a two-sided failure mode: the railroad tripwire must be RESTORABLE (14.10
under-fixed if any new railroad row appears) AND genuine conviction must survive (14.10 over-damped if R1 or
genuine-class conversion collapses — the seed-44-m0-style true-impostor catches are the canary). Either
failure is a stop-and-iterate on 14.10's weighting (or 14.11's prompts), re-smoke, and only then the full
spend — never weaken the §4.6 gate, never raise the caps, never ship a baseline that papers a defect the
phase set out to fix.

**Ready-to-paste prompt:** `agent_prompts/task-14-12-baseline-2-rerecord.md`
