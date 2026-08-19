# Agent Prompt — 7.6 Parse-tolerance / normalization layer for model reports

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.6 — Parse-tolerance / normalization layer for model reports, anchored to tasks/phase-7-plan.md "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (real-model reports crash the strict discriminated-union schemas); DESIGN.md §5 (LLM client contract), §6 (meeting schemas). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-report-parse-tolerance`
**Depends on:** 7.5 merged
**Section refs:** tasks/phase-7-plan.md "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (real-model reports crash the strict discriminated-union schemas); DESIGN.md §5 (LLM client contract), §6 (meeting schemas)
**Complexity:** Medium

The strict meeting/report schemas use discriminated unions with `extra="forbid"`,
and real models — especially the local `qwen2.5:7b-instruct` from Task 7.5 — emit
JSON that is *almost* right but carries fields that do not belong to the matched
union variant (the diagnosed failure: a `co_present` key on a `found_body`
observation). Under `extra="forbid"` that is a hard validation error, which today
becomes a FailedCall and a lost meeting. This task adds a small, well-tested
normalization step that strips keys not valid for the matched discriminated-union
variant *before* `schema.model_validate_json`, so a near-miss model output is
salvaged into a valid report instead of being dropped.

The normalization is applied in the SHARED extract→validate path in
`llm/provider.py` (right after `_extract_json_block`, before
`schema.model_validate_json`), so it protects EVERY provider — Anthropic and the new
Ollama client (7.5) — and the determinism/replay path that runs through the same
code. Because 7.5 routes its parse through that same shared path, this single change
covers both providers without per-client duplication. Put the actual logic in a
small new `llm/` helper module (a pure function over a parsed dict + the target
schema) so it is independently unit-testable and carries no provider/transport
imports; `llm/provider.py` just calls it in the validate path.

The normalization must be CONSERVATIVE and discriminator-aware: it resolves which
union variant the payload matches (via the schema's discriminator / the present
required keys), then drops only keys that are not declared on that variant — it must
NOT invent or rename fields, must NOT touch a payload that already validates, and
must leave non-union schemas untouched. Optionally add a bounded re-ask-on-invalid
retry (one re-prompt when validation still fails after normalization) — keep it
strictly bounded and OFF by default if it complicates determinism; the field-stripping
normalizer is the required core, the retry is the optional extra.

Determinism is a hard constraint: normalization is a pure deterministic function of
the parsed JSON + schema (no RNG, no clock, no network), so a recorded game replays
byte-identically and the frozen 4p/1i baseline is unaffected (its recorded outputs
already validate, so the normalizer is a no-op on them — assert this).

Residual risk (NOT something to fix here): the normalizer TRUSTS the discriminator
value. A payload with a wrong/mismatched discriminator (e.g. `type: saw_player` but
a `found_body`-shaped body) is NOT repaired — stripping to the named variant's
fields would corrupt it — so it remains a FailedCall. The normalizer never infers
the correct variant from body shape.

**Files in scope:**
- llm/provider.py
- llm/report_normalize.py
- tests/llm/test_report_normalize.py
- tests/llm/test_provider.py

**Files NOT in scope:**
- llm/client.py (the `LLMClient` Protocol is unchanged)
- llm/ollama_client.py (7.5's client parses through the shared `llm/provider.py` path; this task does NOT edit the client — the normalization lands in the shared path so it covers Ollama automatically)
- llm/fake_provider.py (the fake provider emits already-valid payloads; untouched)
- meetings/ and the schema definitions themselves (the discriminated-union schemas are NOT relaxed — `extra="forbid"` stays; this task normalizes the payload, it does not loosen the contract)
- replays/samples/ (no re-recording; the normalizer is a no-op on already-valid recorded outputs)
- scripts/refresh_samples.sh, eval/balance_eval.py (provider-agnostic refresh + budget are Task 7.7)
- DESIGN.md (design-thread-owned)
- frontend/ (no frontend surface)

**Definition of done:**
- [ ] A new `llm/report_normalize.py` exposes a pure function that, given a parsed JSON payload and a target (possibly discriminated-union) schema, strips keys not declared on the matched variant — without inventing/renaming fields, without altering a payload that already validates, and leaving non-union schemas untouched.
- [ ] The normalizer is invoked in the SHARED extract→validate path in `llm/provider.py` (after `_extract_json_block`, before `schema.model_validate_json`), so it protects Anthropic, the Ollama client (7.5), and the replay path through one code site.
- [ ] The diagnosed failure is covered: a `found_body` observation carrying a stray `co_present` key validates after normalization (a regression test pins exactly this case); a payload that is already valid is returned byte-identical (no-op); a payload missing a *required* field still fails loud (normalization does not mask genuinely-invalid output).
- [ ] If the optional bounded re-ask-on-invalid retry is implemented, it is strictly bounded (a single re-prompt) and does not break determinism/replay (off by default or pure under replay); if omitted, that omission is noted in the PR `## Decisions`.
- [ ] Determinism holds: the normalizer is a pure function (no RNG/clock/network); the frozen 4p/1i recorded outputs already validate, so the normalizer is a no-op on them and byte-identical replay is preserved (asserted by the existing determinism suite staying green).
- [ ] A test in `tests/llm/` asserts the normalizer is a NO-OP on already-valid recorded outputs by loading + reconstructing the committed 4p/1i baseline set after the normalizer lands (byte-identical) — an explicit assertion, not just relying on `check.sh`.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Find the single place in `llm/provider.py` where extracted text is validated —
`_extract_json_block(...)` followed by `schema.model_validate_json(...)` — and insert
the normalizer between the parse and the validate (parse the extracted text to a
`dict` first, normalize, then `schema.model_validate(normalized)`), so all providers
share it. For the discriminator-aware stripping, use THIS technique (simpler than
Pydantic core-schema internals): the report/observation/claim unions use
`Field(discriminator="type")` and each variant is a model carrying
`type: Literal[...]`. So: read the payload's `type` value, map it to the variant
model whose `type` Literal equals it, and keep ONLY that variant's declared
`model_fields` (stripping extras/misplaced keys), then validate. Build the
`{discriminator value → variant model}` map from the union's members. Keep the helper transport-free and side-effect-free so `tests/llm/test_report_normalize.py`
can table-test it directly: the `co_present`-on-`found_body` case, an already-valid
payload (no-op), a missing-required-field payload (still raises), and a non-union
schema (untouched). The `lint-imports` contract forbids new cross-layer imports, so
keep `llm/report_normalize.py` importing only stdlib + pydantic + the schema types it
already may see — no `engine`/`agents` imports.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.ollama_client"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-7-report-parse-tolerance` with a title like `task 7.6: parse-tolerance / normalization layer for model reports`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-7-plan.md "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (real-model reports crash the strict discriminated-union schemas); DESIGN.md §5 (LLM client contract), §6 (meeting schemas)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
