# Code-up review — `llm/` + `agents/strategic/prompts/` + `tests/llm/` (label: llm-and-prompts)

Reviewer scope: `llm/{client,provider,featherless_client,ollama_client,budget,budgeted_client,fake_provider,report_normalize}.py` (3,281 lines), `agents/strategic/prompts/loader.py` (733 lines) + 7 template sets (30 `.j2` files, 272 KB), `tests/llm/` (8 files, 6,040 lines, 301 tests) plus the prompt tests under `tests/agents/`. Read-only; nothing in the repo was touched. Machine load at timing: `uptime` load avg 5.95 / 6.73 / 9.87 (other reviewers running).

---

## 1. Executive read (10 lines)

1. The provider abstraction is sound and genuinely provider-neutral: one 7-kwarg `LLMClient` Protocol, three real adapters + a fake, one shared extract→normalize→validate→FailedCall seam, cost keyed by provider. It works and `mypy --strict` / ruff are clean [VERIFIED].
2. The three real adapters (`AnthropicClient`, `OllamaClient`, `FeatherlessClient`) each re-implement the same ~60-line `complete()` body (model pick → send → cost → extract → validate → attach `LLMCallFailure` → build `LLMResponse`) — a textbook copy-paste triplication that a 25-line shared helper would erase.
3. Comment/docstring load is extreme: 42% of all lines in the area are comments+docstrings vs 45% code (radon) [VERIFIED]; `featherless_client.py` is 874 lines for ~380 SLOC and its docstrings re-narrate Tasks 14.1/14.4/16.1/16.2/17.9 rather than describe behaviour. `loader.py` is 733 lines for ~300 SLOC.
4. Real defect found: `BudgetedLLMClient` never charges a schema-invalid response's cost to the `GameBudget` — three $1.35 Anthropic failures against a $1.00 cap leave the budget at $0.00 [VERIFIED by repro]. Harmless today only because production runs the $0-priced Featherless provider.
5. JSON extraction is robust to fences/preamble/truncation but takes the FIRST balanced object that parses, so an example object echoed before the answer hijacks the call [VERIFIED]; and Featherless `fail_loud` turns any benign prose preamble into a run-aborting `RuntimeError` (documented, but a harsh design).
6. Retry/timeout policy is uneven: Featherless has 6 attempts × up-to-600 s hard-coded (worst case ~61 min per call, no jitter, no Retry-After); Anthropic relies on SDK defaults; Ollama has neither. Every adapter opens a fresh HTTP client (new TLS handshake) per call by an explicit "no module state" rationale that does not actually require it.
7. The prompt registry is a hand-synced pair (template header comment ↔ `orchestrator/game.py` dict) with no test that the two agree; provenance is otherwise well-designed (per-set namespaced stamps, byte-golden replay test).
8. Five of seven prompt sets (20 files, ~137 KB) are the Phase-14 sweep slate: no committed replay uses them; the *default* set (`qwen3_5_9b`) is used by no committed replay either, so every bare-env import prints a stderr warning (2× per runner build) [VERIFIED].
9. The live `qwen3_6_27b` templates are competent prompt engineering (tagged sections, worked examples, hard caps) but heavy: instructions are ~55–70% of a 4–6k-token prompt; the vent/roll-call/confidence paragraphs are repeated 2–3× within one template and up to 11× across the set; the persona says "a hidden impostor" (singular) while the canonical roster is 9p/2i and the impostor prompt in the same breath lists "your fellow saboteurs".
10. Tests are fast (306 in 0.6 s), well-organised and mostly behavioural, with a superb byte-golden replay test; weaknesses are the many constant/version pins and prompt-substring greps, plus the missing budget-on-failure and extractor-hijack cases.

---

## 2. Findings, ranked by severity

### P1

**F1 — Failed-call spend never reaches the budget.** `llm/budgeted_client.py:296-306`. When the inner adapter raises `ValidationError` (schema-invalid body), the wrapper releases the in-flight reservation and re-raises without charging; the real cost is only carried on the exception (`LLMCallFailure`) to the replay log (`meetings/manager.py:1419`, `orchestrator/game.py:1885`) — never to `GameBudget`. Repro [VERIFIED]:
```
attempt 0: provider billed cost_usd=1.35; budget.cost_usd after = 0.00
attempt 1: provider billed cost_usd=1.35; budget.cost_usd after = 0.00
attempt 2: provider billed cost_usd=1.35; budget.cost_usd after = 0.00   (cap was $1.00)
```
Why it matters: the module docstring promises "no partial spend on a doomed call" and DESIGN §10.4 "cost overruns" fail-loud; a metered provider that emits invalid JSON on every opening (2 attempts) burns unbounded uncounted dollars. Bounded in practice by the manager's retry counts and by production being $0 Featherless, so **impact today is low; contract violation is real**. Confidence high.

**F2 — Three-way copy of the `complete()` pipeline.** `llm/provider.py:167-241`, `llm/ollama_client.py:161-262`, `llm/featherless_client.py:284-410`. Same sequence, same `LLMCallFailure(...)` construction (8 identical fields), same `_model_for` (3 identical copies incl. the "unreachable under mypy" branch), same `agent_id` `del`. The Featherless module even says it was "structurally cloned from ollama_client". Any fix to the seam (e.g. F1, F5) must be applied three times. [VERIFIED] Confidence high. Refactor: `_finalize(raw_text, model, in_tok, out_tok, cost, schema, prompt) -> LLMResponse` in `provider.py` (or a small `_BaseStructuredClient`).

**F3 — Comment/docstring sprawl restating task history.** radon raw over the 10 files [VERIFIED]: 4,014 LOC = 1,807 SLOC (45%) + 1,693 comment/docstring lines (42%). Worst: `client.py` 19% code (a 104-line docstring including a 40-line hypothetical OpenAI adapter sketch), `report_normalize.py` 38%, `budgeted_client.py` 39%, `loader.py` 41%, `featherless_client.py` 44%. Typical content: "Task 14.4 sweep found…", "PR #202 review…", "owner-ratified 2026-06-27…", "(the PR #203 binding discipline)". Every constant carries a paragraph. `_THINKING_KWARG_BY_MODEL` has 20 comment lines for 8 tuples. Why it matters: reading cost, and the docstrings drift (see F10). Confidence high.

### P2

**F4 — Extractor picks the FIRST balanced JSON object, not the answer.** `llm/provider.py:536-588`. Probes [VERIFIED]:
```
example-first  'Sure. An observation looks like {"type": "saw_vent", "tick": 3} and here is my turn: {...}'  -> '{"type": "saw_vent", "tick": 3}'
think-with-json '<think>maybe {"a":1}</think>{"turn_id":"t"}'                                             -> '{"a":1}'
empty-object    'Result: {} then {"turn_id":"t"}'                                                          -> '{}'
```
On the Anthropic/Ollama paths (no think-strip, no preamble guard) each of these becomes a FailedCall even though a valid answer is present. `schema` is already passed to `_extract_json_block`; trying each candidate against `schema.model_validate_json` (or preferring the last/largest candidate) would fix it. Perf note: the scan is O(n²) in the number of `{` — 8,000 unmatched opens = 1.25 s, but real outputs are capped (2048 tokens) and a realistic 800-stray-brace + truncated case took 1 ms, so not a live problem. Confidence high.

**F5 — Featherless `fail_loud` aborts the whole run on a benign preamble.** `llm/featherless_client.py:323-347`, `_detect_reasoning` 450-494. A structured call whose content starts with any prose ("Here is the JSON: {…}") raises `RuntimeError`, which the manager's fail-soft nets (TimeoutError/ValidationError only) do not catch → game aborts. The Anthropic adapter accepts the same output. The code comment acknowledges the trade-off; under `json_object` mode the preamble check is essentially dead (server forces JSON-first), under `none` mode it is a foot-gun. Also `<think>` is matched as a plain substring of the lower-cased content, so an agent quoting the literal token in `free_text` would trip it. [VERIFIED code; JUDGMENT on severity]

**F6 — Retry/timeout policy inconsistent and hard-coded.** `featherless_client.py:529-541, 684-747, 785`: 6 attempts, backoff 1·2ⁿ s (31 s total sleep), no jitter, no `Retry-After` on 429, per-attempt `httpx.Timeout(600.0)` hard-coded → worst case ≈61 min for ONE call with no overall deadline in headless mode (`MeetingDeadlines` are `None` when recording). 500 is always retried (a permanent 500 burns 31 s). `provider.py:697-731` (Anthropic): no timeout/max_retries passed (SDK defaults 600 s / 2 retries), not configurable. `ollama_client.py:265-297`: no retry, no timeout. None of the three exposes a knob. `_isolate_provider_timeout` in `meetings/manager.py:581` only re-tags builtin `TimeoutError`; httpx/anthropic timeouts are different exception classes, so it is inert for the real transports [JUDGMENT, cross-area]. Confidence medium-high.

**F7 — Fresh HTTP client per call.** `provider.py:725`, `ollama_client.py:281`, `featherless_client.py:781`. Each call constructs and tears down `AsyncAnthropic` / `ollama.AsyncClient` / `httpx.AsyncClient` — a new connection pool and TLS handshake per completion (~25 calls/game, ~2k per 50-game re-record). The stated reason ("no module-level state") is a non-sequitur: the adapter *instances* already hold state (`_api_key`, `_send`); a pooled client could live on the instance behind an `aclose()`/context manager. [JUDGMENT] Cannot time without network. Confidence medium.

**F8 — Fake provider is only accidentally compatible with the production schemas.** `llm/fake_provider.py:127-135`: unions are recognised only via `origin is typing.Union`; PEP 604 unions of two builtins produce `types.UnionType` and fall through to `_fallback_zero` → `None`. `class M(BaseModel): x: str | int` → fake raises `ValidationError` [VERIFIED]. `VoteBallot.target: PlayerId | Literal["SKIP"]` works only because `Literal.__or__` yields `typing.Union`. Realism: the fake's ballot `target` is `"fake-target-<hash>"` (not a player) → every fake vote is "invalid target normalized to SKIP"; `claims=[]`, `free_text="… (unsure)"` → fake meetings never accuse, never eject, never exercise the extractor/normalizer, so CI's end-to-end runs cover none of the interesting meeting paths. `_fallback_zero` is `json.loads("null")` inside a try/except — dead defensive code. Confidence high.

**F9 — Prompt-version registry is hand-synchronised in two places, untested for agreement.** Template headers (`qwen3_6_27b/*.j2:3` "version crewmate_report.qwen3_6_27b.v3") vs `orchestrator/game.py:340-357` `PROMPT_VERSION_SETS` (+ `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`) + `DEFAULT_PROMPT_VERSIONS` with three different formats (`crewmate_report.v8`, `impostor_report_v6`, `vote_ballot/v7`) and the 9B `accusation_round.j2:3` header says just "version 9". No test reads the header and compares to the registry (tests pin the registry values themselves: `test_registry_stamps_all_four_templates_v3`). Memory notes already record this as a known "version-bump cascade" gotcha — that is a symptom of the design. Fix: derive versions from the template header (or a hash) at load time. Confidence high.

**F10 — Doc/code drift.** `llm/client.py:80-83`: "`AILIBI_LLM_PROVIDER` — selects the adapter (`"anthropic"` | `"fake"`)" — omits `ollama` and `featherless` [VERIFIED]. `agents/strategic/prompts/__init__.py:3`: "The four Jinja2 templates next to this module" — there are 30 files in 7 sub-dirs. `report_normalize.py:3` still names `qwen2.5:7b-instruct`. `provider.py` is titled "Anthropic provider adapter" but hosts the shared extractor, three pricing tables and the 4-way factory. `ollama_client.py:88` "largest 7p/2i meeting prompts (~4040 tokens, measured)" — recorded 27B prompts reach 5,876 input tokens (measured, §3). `provider.py:713-718`: `extended_thinking` / `prompt_caching_beta` are plumbed and then discarded (`_ = extended_thinking`) — dead knobs pinned by `tests/llm/test_client.py::test_extended_thinking_and_caching_beta_flow_through_send_hook`. Confidence high.

**F11 — Import-time side effects in the loader.** `loader.py:242` builds `_ENV` at import (`build_environment()` → `resolve_prompt_set()` → stderr print). Importing `orchestrator.game` in a bare shell prints the "AILIBI_PROMPT_SET is unset" notice; `build_default_meeting_runner()` prints it twice [VERIFIED: count=2]. The module-level wrappers + `_ENV` are only used by `experiments/lab/*`; production uses `build_prompt_renderers`. Two parallel APIs for one job. Confidence high.

**F12 — Dead / retained prompt weight.** Committed replays (`replays/samples/{9p2i,4p1i}`, 100 files, 1,956+234 calls) are 100% `Qwen/Qwen3.6-27B` with `prompt_versions=*.qwen3_6_27b.v3` [VERIFIED]. `cydonia_24b`, `glm_4_32b`, `qwen3_30b_a3b`, `qwen3_32b`, `qwen3_32b_thinking` (20 files, ~137 KB) appear in no replay and only in registry entries/tests. The default set `qwen3_5_9b` is likewise used by no committed replay, so the "keep the default for byte-identity" rationale protects nothing except unit-test fixtures, while costing the import-time warning. The `*_roll_call.j2` variants duplicate 90% of their base template (142 body lines, 15 differ) behind a lever ruled default-OFF ("CREW-ONLY ruling"). Confidence high on facts; [JUDGMENT] on what to delete.

**F13 — Prompt content issues (27B set).**
- Singular impostor: `crewmate_report.j2` "a hidden impostor is killing crewmates one at a time"; `accusation_round.j2`/`vote_ballot.j2` "a hidden impostor"; `impostor_report.j2` "a hidden impostor kills crewmates" followed by "Your fellow saboteurs: p-4 …". Canonical roster is 9p/2i (`orchestrator/game.py:179`). The render contract carries no impostor count, so the templates cannot say it right. [VERIFIED wording]
- "VERIFIED evidence": `vote_ballot.j2` "Each flag below is VERIFIED evidence … never side with one over a verified flag", while `meetings/schemas.py:426` says "Flags are information, not verdicts". `alibi_conflict`/`alibi_vs_sighting` compare two pieces of *testimony*; an impostor's fabricated sighting yields a "verified" flag against an innocent. Overclaim. [JUDGMENT]
- Redundancy: within `accusation_round.j2` the vent-first paragraph appears 2×, "Answer the roll-call" 2×, "one room, one tick" 3×, confidence rubric 2×; across the set "Calibrate confidence honestly" 7×, "one room, one tick" 11× [VERIFIED counts]. Template bodies are 1.1k–3.3k tokens of instructions; recorded prompts are median 3.9k/4.2k/4.7k input tokens (opening/chain/vote), max 5,876 — instructions are roughly 55–70% of context.
- Free-text feedback with no cap or escaping: `said: "{{ turn.free_text }}"`, `{{ prior_turn.free_text }}`, `{{ claim.reason }}` are rendered raw (`autoescape=False`) inside `<transcript>`/`<accusation_against_you>`; `free_text: str` and `reason: str` have no `max_length` (`meetings/schemas.py:323,263`); the only cap is the 1000-char *unsure* check. A single verbose or tag-emitting agent turn is replayed verbatim into every subsequent prompt of the meeting (up to 8 turns + 9 ballots). Low security risk (all agents are the same model, no human input) but zero robustness margin. [VERIFIED code; JUDGMENT on risk]

**F14 — Featherless thinking-kwarg registry fails at wire time, not construction.** `featherless_client.py:604-627`: an env override to any unlisted model id raises inside `_build_chat_payload` on the first real send (and only there — injected-send tests never reach it). Fail-loud is right; the placement means the error surfaces mid-game rather than at `build_default_client`. Confidence high.

**F15 — Small unused API surface.** `BudgetSnapshot.remaining_*` (budget.py:83-93) and `BudgetedLLMClient.estimate()` are unused outside tests (vulture + grep) [VERIFIED]; `_default_send`'s two dead knobs (F10). Minor.

### P3 / notes
- `_send_with_retry` retries `json.JSONDecodeError` from `response.json()` — good — but a 2xx with `finish_reason=="length"` (truncated JSON) is not detected; it becomes a FailedCall via validation, which is acceptable.
- `_estimate_input_tokens` 4-chars/token + frontier defaults (6e-6/30e-6) means a $0.30 default cap admits only ~4 concurrent reservations at 2048 max_tokens on a metered provider — fine for the fake, but the default `GameBudget(max_cost_usd=0.30)` and the wire-up `budget=None → no budget layer at all` (`orchestrator/game.py:919`) are two different "defaults".

---

## 3. Architecture / design assessment

**Well designed**
- `LLMClient` Protocol + `LLMResponse`/`TokenUsage` are minimal and truly provider-free; `agent_id` as attribution-only metadata is a clean choice.
- One shared extract → `normalize_report_payload` → validate → `LLMCallFailure`-on-exception seam. `report_normalize.py` is a genuinely nice pure function: discriminator-aware, conservative (never infers a variant, never fabricates), byte-identical no-op verified against every committed recording (`test_normalizer_is_byte_identical_on_every_recorded_output`).
- Provider-keyed $0 pricing with an *explicit* raise for unpriced Anthropic models (Task 19.6) — the right fail-loud posture.
- `BudgetedLLMClient`'s in-flight reservation pool with the lock held only around the synchronous mutations is a correct, tested answer to the concurrent-preflight race.
- Injectable `send`/`sleep`/`retryable_exc` hooks make every transport path unit-testable without the SDKs; SDKs are lazily imported.
- Prompt-set binding (`build_prompt_renderers` → one `Environment` + one version mapping per runner) and the byte-golden replay test are excellent provenance engineering.
- Templates: tag-sectioned, positive phrasing, worked JSON examples, hard sentence caps, dead-roster and living-roster lists, deterministic skip-threshold arithmetic surfaced to the model — good practice for small open models.

**Accidental complexity**
- Three hand-copied adapters (F2). The "structurally cloned" comment is candid; the cure is a shared finalizer.
- Two parallel loader APIs (module wrappers on `_ENV` vs `build_prompt_renderers`), each wrapper carrying an `environment` and `template_name` escape hatch, plus a lever that swaps file *names* — for what is a `{% if impostor_roll_call %}` inside one template.
- The registry split (template header ↔ Python dict ↔ per-lever dict) with three version-string formats.
- Doc mass. Docstrings function as a change-log; the actual contracts (e.g. "raises `RuntimeError` on preamble", "does not charge failed calls") are buried or absent.
- Featherless: `ResponseFormatMode` ×3, `ThinkingPolicy` ×2, `request_thinking`, per-model kwarg registry, transport retry, parse retry — every sweep-era knob is retained in the production adapter although production is pinned to one model with one mode.
- Fake provider: reflection over annotations to build a "minimal valid instance" that is minimal to the point of being degenerate (F8); a table-driven fake keyed by schema class would be shorter and more useful.

**What I would refactor (in order)**
1. `provider.py`: add `_finalize_structured(raw_text, *, model, prompt, in_tok, out_tok, cost_usd, schema) -> LLMResponse`; make the three adapters ~15 lines each. Move `build_default_client` + pricing into `llm/factory.py`, leaving `provider.py` = Anthropic only (matching its docstring) or rename it.
2. `budgeted_client.py`: in the `except` branch, `extract_parse_failure(exc)` → charge `TokenUsage(in,out)`/`cost_usd` before re-raising (F1). One test.
3. `_extract_json_block`: iterate candidates and return the first that validates against `schema` (fallback to today's behaviour when none does) (F4).
4. Loader: delete `_ENV` and the module-level default path; keep `build_prompt_renderers` only; have `resolve_prompt_set` return `(name, was_fallback)` and print once at the CLI layer, or simply flip the default to `qwen3_6_27b` and delete the notice (F11/F12).
5. Registry: read `prompt_id/version` from the `.j2` header (already present) — one source of truth; keep the dict only as a pin test (F9).
6. Prompt sets: archive the 5 sweep sets under `experiments/` (they are experiment artefacts, not runtime code); fold `*_roll_call.j2` into a Jinja branch or delete if the ruling is final (F12).
7. Templates: add `num_impostors`/`impostor_word` to the render contract; de-duplicate the repeated paragraphs (a Jinja macro or a single `<rules>` block); soften "VERIFIED" to "detected" (F13).

---

## 4. Test assessment

- `tests/llm`: 306 passed / 17 skipped in **0.60 s** [VERIFIED]; skips are the opt-in real-provider (`AILIBI_RUN_REAL_PROVIDER_TESTS`) and live-Ollama tests — correctly gated. Prompt tests (`tests/agents/test_prompt_loader.py`, `test_bespoke_prompt_sets.py`, `test_impostor_answer_arm.py`): 127 passed in 1.15 s.
- Strengths: transport hooks let every branch of retry/backoff be tested with an injected `sleep`; `test_report_normalize.py` covers the discriminated-union edge cases (unhashable discriminator, reversed range as str/float, no-op guarantee) and re-checks byte-identity over every committed output; `test_budgeted_client.py` has real concurrency tests (stale-preflight race, overlap, release-on-failure); `tests/meetings/test_prompt_byte_golden.py` re-renders every recorded prompt through the production `MeetingManager` and asserts byte equality — the strongest instrument in the area.
- Weaknesses:
  - Constant/implementation pins: `test_default_attempt_budget_is_six`, `test_default_model_is_the_locked_qwen3_6_27b`, `test_registry_stamps_all_four_templates_v3`, `test_qwen_set_is_default_prompt_versions_byte_identical`, `test_notice_is_exactly_one_line`, `test_extended_thinking_and_caching_beta_flow_through_send_hook` (pins two dead knobs). These lock numbers, not behaviour, and are what makes every version bump a 3-file cascade.
  - Prompt tests are largely substring greps of template text (`test_ballot_rationale_carries_two_contrasting_voice_examples`, `test_confidence_rubric_present_in_every_turn_template`, `test_frozen_sets_do_not_carry_the_v5_markers`) — tautological with the file they read and brittle to rewording.
  - Missing: (a) failed-call cost charged to budget (F1 — no test, and the current behaviour would fail one); (b) extractor with an example object before the answer (F4); (c) fake provider against a PEP-604 builtin union (F8); (d) template-header version == registry version (F9); (e) `_supports_thinking_kwarg` reached via `build_default_client` with an env override (F14); (f) any check that `free_text` length is bounded before re-render (F13).
  - `test_real_provider.py` (776 lines, 32 tests) is Anthropic-only; there is no opt-in live smoke for the production Featherless path other than the sweep harness.

---

## 5. Recommendations (prioritised)

1. **Charge failed calls to the budget** (`budgeted_client.py` except-branch: read `extract_parse_failure(exc)` and `charge()` before re-raise; add a test). Small, closes a stated contract gap (F1).
2. **Collapse the three adapters onto one finalizer** in `llm/provider.py` (or `llm/_seam.py`); delete the three `_model_for` copies via a tiny mixin/dataclass. Then fix F4 (schema-aware candidate selection) once, in one place.
3. **Halve the doc mass**: move task-history narration to `audits/` (where it already lives) and keep contracts only. Target ≤25% comment lines; the loader and `featherless_client.py` first. Fix the four stale docstrings in F10 while there.
4. **One source of truth for prompt versions**: parse the `.j2` header at `build_prompt_renderers` time; keep a single golden test that pins recorded stamps. Delete `DEFAULT_PROMPT_VERSIONS`' three ad-hoc formats.
5. **Retire the import-time `_ENV`** and the stderr notice: either flip `DEFAULT_PROMPT_SET` to `qwen3_6_27b` (no committed replay depends on the 9B default) or make the fallback an error for operational entry points. Archive the 5 sweep sets under `experiments/lab/prompt_sets/` and fold the roll-call variants into a Jinja branch.
6. **Make retry/timeout explicit and shared**: a `TransportPolicy(max_attempts, base_backoff, jitter, per_attempt_timeout, honor_retry_after)` on all three adapters, pooled client per adapter instance, and a total-wall-clock cap so a headless recording cannot sit 60 min in one call.
7. **Prompt content**: pass `num_impostors` into the render contract and fix the singular wording; replace "VERIFIED evidence" with "detected contradiction (testimony vs testimony)"; de-duplicate the repeated vent/roll-call/confidence paragraphs (target −20–30% instruction tokens); cap `free_text`/`reason` (`max_length`) at the schema so one verbose turn cannot balloon every later prompt.
8. **Make the fake useful**: build fake ballots/turns from the prompt's living-roster block (or a table keyed by schema) so CI meetings can accuse and eject; handle `types.UnionType`; delete `_fallback_zero`.

---

## Appendix — evidence log

- radon raw (per file loc/sloc/comments/docstr/code%): budget 214/129/6/40/60%; budgeted_client 359/139/38/130/39%; client 175/33/0/104/19%; fake_provider 204/132/13/26/65%; featherless_client 874/381/173/238/44%; ollama_client 374/194/80/74/52%; provider 773/382/92/197/49%; report_normalize 308/118/27/111/38%; loader 733/299/27/317/41%. Max cyclomatic complexity: `fake_provider._zero_value_from_annotation` 24, `report_normalize._normalize` 21, otherwise ≤11.
- Recorded prompt sizes (replays/samples/9p2i, 1,956 calls): opening n=179 median 11,220 chars / 3,891 input tokens (max 4,784); chain n=806 median 11,607 / 4,175 (max 5,712); vote n=971 median 13,710 / 4,710 (max 5,876). Output tokens: turn median ~331–342 (max 601, cap 2048); vote median 107 (max 156, cap 1024).
- Template body sizes (27B set, after header comment): accusation_round 12.5 KB (~3.1k tok), roll-call variant 13.3 KB, crewmate_report 6.8 KB, impostor_report 4.6 KB, vote_ballot 9.4 KB.
- Extractor perf: 2,000 unmatched `{` = 80 ms; 8,000 = 1,247 ms; clean 7 KB object 0.3 ms; 800 stray `{x}` + truncated tail (7.2 KB) 1 ms.
- Bare-env notice count for `build_default_meeting_runner()`: 2.
- `mypy --strict llm agents/strategic/prompts`: Success (11 files). `ruff check`: All checks passed.
- Repro scripts kept under `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/llm-and-prompts/` (inline heredocs; nothing written into the repo).
