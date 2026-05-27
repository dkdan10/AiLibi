# Agent Prompt — 4.7 LLMCallRecord agent_id propagation (R-3 substrate)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.7 — LLMCallRecord agent_id propagation (R-3 substrate), anchored to DESIGN.md §5, DESIGN.md §11.4, mid-phase DTO audit R-3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-llmcall-agent-id`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §5, DESIGN.md §11.4, mid-phase DTO audit R-3
**Complexity:** Medium

Mid-phase DTO audit R-3 informational finding (Unique-but-verified):
`orchestrator.replay.LLMCallRecord` carries no `agent_id` field;
therefore neither does `api.schemas.LLMCallView`. ThoughtStream
(4.8) needs per-call attribution; today the only recovery path is
parsing rendered_memory text inside `prompt_text` — fragile and
template-dependent. This task threads `agent_id` from the meeting
manager through the LLM client protocol into the captured record
and out to the DTO layer + TS types. Reconciler explicitly flagged
this as a prerequisite for 4.8 dispatch.

**Scope is wider than the audit hinted.** The audit cited
`participant.agent_id` as "in scope at `meetings/manager.py:555-565`"
but the recording client in `orchestrator/game.py:223-231` is
stateless — it sees only the prompt + response from `LLMClient.
complete()`. To capture `agent_id` at record time, the `LLMClient`
protocol must take an `agent_id` parameter; every implementation
(claude provider, fake) passes through; every call site in
`meetings/manager.py` populates the parameter. The call chain
covered:

```
meetings/manager.py call site
   ↓ (passes agent_id=participant.agent_id)
LLMClient.complete(prompt, *, agent_id=...)
   ↓
_RecordingLLMClient.complete in orchestrator/game.py
   ↓ (stores agent_id on the constructed LLMCallRecord)
LLMCallRecord (gains optional agent_id field)
   ↓ (JSONL persistence; backward-compat for old replays)
api/replay_loader.py _llm_call_view
   ↓
api.schemas.LLMCallView (gains optional agent_id field)
   ↓
frontend/src/types/api.ts (mirror)
```

**Backward-compatibility decision.** `agent_id: str | None`, not
`str`. Reason: existing replay JSONLs (the Phase 3 eval's
`/tmp/eval-50/replay-seed-{22,24,26,49}.jsonl` and anything else on
disk) were written before this task. Deserializing those with a
required-string field would crash. With `str | None` defaulting to
`None`, old replays still load and ThoughtStream gracefully shows
`agent_id: unknown` for those calls. Pinning the field as required
later is a one-line tightening once we're confident no old replays
matter — that's a Phase 5 hygiene call, not this task's.

**Out of scope** (explicit decisions deferred):

- **Replay format versioning.** No `format_version` field on
  `ReplayLog`. Adding versioning is a Phase 5 concern; this task
  relies on Pydantic's default-on-missing behavior.
- **Retroactive backfill of old replays.** The audit asked us to
  "decide between patch existing replays and leave at None." We
  leave at None. No migration script is written; if a Phase 5 task
  decides to backfill, that's a separate effort.
- **`agent_id` for non-meeting triggered calls.** The
  `call_kind="trigger"` case (per-agent LLM triggers per
  DESIGN.md §4.4 #3) similarly knows the calling agent; the
  parameter propagates there too. If a future call kind is genuinely
  agentless (system-level), `None` remains a valid value.
- **Renaming `LLMCallRecord.prompt` → `prompt_text`.** Already
  named `prompt` on the source type and `prompt_text` on the DTO
  per 4.1's deliberate mapping. Don't rename.

**Files in scope:**
- llm/client.py
- llm/claude_provider.py
- llm/fake.py
- orchestrator/game.py
- orchestrator/replay.py
- meetings/manager.py
- api/schemas.py
- api/replay_loader.py
- frontend/src/types/api.ts
- tests/llm/test_client.py (or equivalent — match existing test naming)
- tests/orchestrator/test_game.py
- tests/orchestrator/test_replay.py
- tests/meetings/test_manager.py
- tests/api/test_schemas.py
- tests/api/test_replays.py
- tests/api/test_replay_loader.py
- tests/api/fixtures/sample_replay.py

**Files NOT in scope:**
- engine/
- agents/
- observation/
- frontend/src/components/
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/package.json
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- scripts/
- tests/engine/
- tests/agents/
- tests/observation/
- tests/test_firewall.py

**Definition of done:**
- [ ] **`LLMClient.complete()` protocol extended.** [llm/client.py](llm/client.py)'s `LLMClient.complete()` signature gains `agent_id: str | None = None` as a keyword-only parameter (use `*,` to enforce keyword). Existing positional parameters unchanged. Docstring updated to describe the field's purpose ("identifies which game-agent originated this call; None for system-level calls").
- [ ] **All implementations updated to accept the parameter.** [llm/claude_provider.py](llm/claude_provider.py)'s adapter, [llm/fake.py](llm/fake.py) (or whatever the fake / recording client is named), and the `_RecordingLLMClient` in [orchestrator/game.py:204-233](orchestrator/game.py#L204) accept `agent_id` as a kwarg. The Anthropic adapter does NOT pass it to the upstream SDK (it's metadata, not provider-relevant); the fake stores it on its captured-call history for assertions.
- [ ] **`_RecordingLLMClient` captures `agent_id` on `LLMCallRecord`.** [orchestrator/game.py:223-231](orchestrator/game.py#L223) populates `agent_id=agent_id` on the constructed record.
- [ ] **`LLMCallRecord` gains the field.** [orchestrator/replay.py:51-71](orchestrator/replay.py#L51) adds `agent_id: str | None = None` (default-None for backward-compat). Pydantic `model_config` remains `frozen=True, extra="forbid"`. Schema validates a JSONL line that omits `agent_id` as `agent_id=None`; verify with a test.
- [ ] **Every call site in `meetings/manager.py` passes `agent_id`.** Audit with `grep -n "complete(" meetings/manager.py`. Each surfaced call passes `agent_id=<the speaking agent's id>`. The participant context object already carries `agent_id` per the audit reference; this is a parameter pass-through, not new bookkeeping. If a call genuinely has no agent (e.g. a manager-level system call), pass `agent_id=None` explicitly and add a code comment explaining why.
- [ ] **DTO exposure.** [api/schemas.py](api/schemas.py)'s `LLMCallView` (lines 357-370) gains `agent_id: str | None` as a new field. Update the `EXPECTED_DTOS` and `FORBIDDEN_TYPES` fixtures in [tests/api/test_leak.py](tests/api/test_leak.py) IF they reference the field set — but only if they do; the leak test is field-agnostic by design.
- [ ] **Loader propagation.** [api/replay_loader.py:1069-1081](api/replay_loader.py#L1069)'s `_llm_call_view` passes `agent_id=call.agent_id` (mapping the `LLMCallRecord.agent_id` straight through).
- [ ] **Frontend types mirror.** [frontend/src/types/api.ts:240-249](frontend/src/types/api.ts#L240) adds `agent_id: string | null` to the `LLMCallView` interface.
- [ ] **Backward-compat test.** A test in [tests/api/test_replay_loader.py](tests/api/test_replay_loader.py) writes a fixture JSONL that omits the `agent_id` field on `LLMCallRecord` entries (use `model_dump(mode="json", exclude={"agent_id"})` or hand-write a minimal valid JSON line); loads it; asserts the resulting `LLMCallView.agent_id is None`.
- [ ] **Round-trip test.** A test asserts that constructing an `LLMCallRecord(agent_id="p-2", ...)`, JSONL-roundtripping it, and loading it through the DTO yields `LLMCallView.agent_id == "p-2"`.
- [ ] **Manager call-site test.** A test in [tests/meetings/test_manager.py](tests/meetings/test_manager.py) uses the fake LLM client to assert that for a meeting with N participants, the fake's captured calls each carry the correct `agent_id` matching the speaking participant.
- [ ] **Sample replay fixture updated.** [tests/api/fixtures/sample_replay.py](tests/api/fixtures/sample_replay.py)'s helper that constructs synthetic LLM calls populates `agent_id` so downstream loader tests use the new field naturally.
- [ ] **No firewall change.** `agents/` still does not import from `engine/`. The `LLMClient` protocol lives in `llm/`, which `agents/` may import. Firewall preserved.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Order the work to minimize broken intermediate states:

Step 1 — Add the field to `LLMCallRecord` with `default=None`. This is backward-compatible at the schema layer immediately. Existing replays continue to load.

Step 2 — Extend the `LLMClient` protocol. Add `agent_id: str | None = None` as a keyword-only parameter. Update all implementers to accept it (no-ops for the real provider; capture-and-store for fakes).

Step 3 — In `_RecordingLLMClient.complete`, pass `agent_id` through to the `LLMCallRecord` constructor.

Step 4 — Walk every call site in `meetings/manager.py` and add `agent_id=<...>` to each. Use the participant or speaker context object already in scope.

Step 5 — Add the field to `LLMCallView` and propagate in the loader. Add to TS types.

Step 6 — Write the backward-compat test (fixture JSONL without `agent_id`) and the round-trip test (with `agent_id`).

Step 7 — Run full check suite; fix any captured assertions in existing tests that need to be aware of the new field (likely few since field is None-defaulted).

Pydantic v2 default-None pattern for `LLMCallRecord`:

```python
class LLMCallRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    call_kind: Literal["meeting", "trigger"]
    model: str
    prompt: str
    response_text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    agent_id: str | None = None
```

`extra="forbid"` still allows missing optional fields (Pydantic distinguishes "extra unknown field" from "missing optional field with default"). Verify by loading a JSONL line that lacks `agent_id` — should validate cleanly.

The protocol extension:

```python
class LLMClient(Protocol):
    def complete(
        self,
        prompt: str,
        *,
        call_kind: Literal["meeting", "trigger"] = "meeting",
        agent_id: str | None = None,
    ) -> LLMResponse: ...
```

Keep keyword-only via the `*,` separator; positional `agent_id` would be too easy to miswire.

## Public types this task introduces
- `orchestrator.replay.LLMCallRecord` gains field `agent_id: str | None`
- `api.schemas.LLMCallView` gains field `agent_id: str | None`
- `LLMClient.complete()` protocol gains keyword parameter `agent_id`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-4-llmcall-agent-id` with a title like `task 4.7: llmcallrecord agent_id propagation (r-3 substrate)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5, DESIGN.md §11.4, mid-phase DTO audit R-3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
